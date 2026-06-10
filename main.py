from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
import json

from services.ingestion import load_single_pdf, chunk_documents, create_vector_store
from services.retrieval import retrieve_and_answer, load_vector_store

app = FastAPI(
    title="RAG Pipeline API",
    description="Upload PDFs and query them using local LLMs via Ollama"
)

# --------------------------------------------------------------------------
# FILE DEDUPLICATION — tracks which filenames have already been ingested
# Stored as a JSON list on disk so it survives server restarts
# --------------------------------------------------------------------------
INGESTED_FILES_LOG = "ingested_files.json"


def load_ingested_files() -> set:
    """Load the set of already-ingested filenames from disk."""
    if os.path.exists(INGESTED_FILES_LOG):
        with open(INGESTED_FILES_LOG, "r") as f:
            return set(json.load(f))
    return set()


def save_ingested_files(files: set):
    """Persist the updated set of ingested filenames to disk."""
    with open(INGESTED_FILES_LOG, "w") as f:
        json.dump(list(files), f, indent=2)


# --------------------------------------------------------------------------
# BACKGROUND TASK — runs AFTER the HTTP response is returned
# FIX: Ingestion (load → chunk → embed) is CPU/IO heavy.
#      Running it inside the request handler blocked the async event loop.
#      Now it runs in a background thread via FastAPI's BackgroundTasks.
# --------------------------------------------------------------------------
def process_pdf_background(file_path: str, filename: str):
    """
    Background task: run the full ingestion pipeline for ONE specific PDF.

    FIX: Previously called load_pdf("temp") which reloaded ALL PDFs in the
    temp/ folder every time a new file was uploaded. This caused:
      - Duplicate chunks in the vector store (old files re-embedded)
      - Wasted processing time on already-ingested documents

    Now uses load_single_pdf(file_path) to process ONLY the new file.
    """
    print(f"[Background] Starting ingestion for: {filename}")

    # Load ONLY this specific file — not the whole temp/ folder
    loaded_documents = load_single_pdf(file_path)
    if not loaded_documents:
        print(f"[Background] No pages loaded from: {filename}")
        return

    chunks = chunk_documents(loaded_documents)
    if not chunks:
        print(f"[Background] No chunks created for: {filename}")
        return

    create_vector_store(chunks)

    # Mark this file as ingested so we skip it on future uploads
    ingested = load_ingested_files()
    ingested.add(filename)
    save_ingested_files(ingested)

    print(f"[Background] Ingestion complete for: {filename}")


# --------------------------------------------------------------------------
# FIX: Pydantic model for /query request body
# Before: query was a URL query parameter → ?query=text (poor REST practice,
#         breaks for long/complex questions, not JSON-native)
# After:  query is a JSON body field → {"query": "your question"}
# --------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str


# --------------------------------------------------------------------------
# ENDPOINT 1: POST /upload
# --------------------------------------------------------------------------
@app.post("/upload", summary="Upload a PDF for ingestion")
async def upload_file(
    background_tasks: BackgroundTasks,   # FastAPI injects this automatically
    file: UploadFile = File(...)
):
    """
    Upload a PDF file. The file is saved to disk immediately and then
    ingested (chunked + embedded) in the background.

    Returns instantly — ingestion continues after the response is sent.
    """

    # VALIDATION: Only accept PDFs
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # DEDUPLICATION: Skip if this filename was already ingested
    ingested = load_ingested_files()
    if file.filename in ingested:
        return {
            "message": f"'{file.filename}' has already been ingested. Skipping.",
            "status": "duplicate"
        }

    # SAVE FILE: Stream in 1 MB chunks instead of loading entire file into RAM
    # FIX: The original `file.read()` loaded the whole file at once — bad for large PDFs
    os.makedirs("temp", exist_ok=True)
    file_location = os.path.join("temp", file.filename)

    with open(file_location, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)  # Read 1 MB at a time
            if not chunk:
                break
            f.write(chunk)

    # BACKGROUND TASK: Pass the exact file path — not just filename
    background_tasks.add_task(process_pdf_background, file_location, file.filename)

    return {
        "message": f"'{file.filename}' uploaded successfully. Ingestion running in background.",
        "status": "processing"
    }


# --------------------------------------------------------------------------
# ENDPOINT 3: GET /documents — list all ingested files
# --------------------------------------------------------------------------
@app.get("/documents", summary="List all ingested documents")
async def list_documents():
    """Returns the list of all filenames that have been successfully ingested."""
    ingested = load_ingested_files()
    return {"documents": sorted(list(ingested))}


# --------------------------------------------------------------------------
# ENDPOINT 4: DELETE /document/{filename} — remove a document
# --------------------------------------------------------------------------
@app.delete("/document/{filename}", summary="Delete an ingested document")
async def delete_document(filename: str):
    """
    Removes all chunks for the given filename from ChromaDB,
    deletes it from the ingestion log, and removes the file from temp/.
    """
    ingested = load_ingested_files()
    if filename not in ingested:
        raise HTTPException(status_code=404, detail=f"'{filename}' not found in ingested files.")

    # ── Remove chunks from ChromaDB ──────────────────────────────
    try:
        from langchain_chroma import Chroma
        from langchain_ollama import OllamaEmbeddings

        embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
        vector_store = Chroma(
            persist_directory="vector_store",
            embedding_function=embeddings
        )

        # Get ALL stored entries, then filter by source matching filename
        collection = vector_store._collection
        all_docs   = collection.get()

        ids_to_delete = [
            doc_id
            for doc_id, meta in zip(all_docs["ids"], all_docs["metadatas"])
            if filename in meta.get("source", "")
        ]

        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            print(f"[Delete] Removed {len(ids_to_delete)} chunks for '{filename}'")
        else:
            print(f"[Delete] No chunks found for '{filename}' in vector store")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete from vector store: {str(e)}")

    # ── Remove from ingestion log ────────────────────────────────
    ingested.discard(filename)
    save_ingested_files(ingested)

    # ── Delete file from temp/ ───────────────────────────────────
    file_path = os.path.join("temp", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"[Delete] Removed file: {file_path}")

    return {"message": f"'{filename}' deleted successfully.", "status": "deleted"}

@app.post("/query", summary="Query the ingested documents")
async def query_vector_store(request: QueryRequest):
    """
    Ask a question against the ingested PDF documents.

    Request body: {"query": "What is this document about?"}

    Returns: {"answer": "...", "sources": [{"file": "...", "page": ...}]}
    """

    # FIX: Wrap load_vector_store() in try/except and return a proper 404
    # Before: a ValueError from load_vector_store() would crash with a 500 error
    try:
        vector_store = load_vector_store()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        result = retrieve_and_answer(request.query, vector_store)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result