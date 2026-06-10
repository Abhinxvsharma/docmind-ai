from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from typing import List
import os

# FIX: Single shared embedding instance — same model MUST be used in retrieval.py
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")


def load_single_pdf(file_path: str) -> List[Document]:
    """
    Load ONE specific PDF file by its exact path.
    Used by the background task so each uploaded file is processed
    independently — prevents re-processing old files already in temp/.

    Each page becomes one Document with .page_content and .metadata.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"[Ingestion] Loaded {len(documents)} pages from '{file_path}'")
    return documents


def load_pdf(file_path: str) -> List[Document]:
    """
    Scan a directory for all .pdf files (recursively) and load them.
    Each page of every PDF becomes one Document with .page_content and .metadata.
    """
    loader = DirectoryLoader(
        file_path,
        glob="**/*.pdf",      # ** = recurse into subdirectories
        show_progress=True,   # tqdm progress bar in terminal
        silent_errors=True,   # skip broken/password-protected PDFs silently
        loader_cls=PyPDFLoader
    )

    documents = loader.load()
    print(f"[Ingestion] Loaded {len(documents)} pages from PDFs in '{file_path}'")
    return documents


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Split documents into smaller chunks for better embedding precision.

    chunk_size    : max characters per chunk
    chunk_overlap : characters repeated between adjacent chunks
                    (prevents sentences from being cut at boundaries)
    """
    if not documents:
        raise ValueError("No documents found to chunk.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
        # Splits on: \n\n → \n → space → char (in that priority order)
    )

    chunks = text_splitter.split_documents(documents)
    print(f"[Ingestion] Created {len(chunks)} chunks from {len(documents)} pages")
    return chunks


def create_vector_store(
    chunks: List[Document],
    persist_directory: str = "vector_store"
) -> Chroma:
    """
    Store embedded chunks in ChromaDB on disk.
    - If the store already exists → append new chunks (incremental ingestion).
    - If it doesn't exist yet  → create it from scratch.
    """
    if not chunks:
        raise ValueError("No chunks found to store.")

    if os.path.exists(persist_directory):
        # APPEND to existing store — supports uploading new PDFs without wiping old data
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        vector_store.add_documents(chunks)
        print(f"[Ingestion] Added {len(chunks)} chunks to existing vector store")
    else:
        # CREATE new store — embeds all chunks and persists to disk
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        print(f"[Ingestion] Created new vector store with {len(chunks)} chunks")

    return vector_store
