from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List
import os

# FIX: Keep embeddings and llm as globals (lightweight connection objects, not inference)
# NOTE: model name MUST match ingestion.py — different models = incompatible vector spaces
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
llm = ChatOllama(model="llama3.2:latest")

# FIX: REMOVED the global `vector_store = Chroma(...)` that was here before.
# It crashed at startup if vector_store/ didn't exist yet (before any PDF was uploaded).
# The load_vector_store() function below handles this safely with an existence check.


def create_prompt(context: str, query: str) -> list:
    """
    FIX: create_prompt() was defined but NEVER used before.
    Now it's properly integrated into retrieve_and_answer().

    Builds a structured chat prompt using:
    - system message: role + context (retrieved chunks)
    - human message: the user's question

    Returns a list of BaseMessages ready for llm.invoke().
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a helpful assistant.
Answer the question ONLY using the context provided below.
If the context does not contain enough information to answer, clearly say so — do not make up an answer.

Context:
{context}"""
        ),
        (
            "human",
            "{query}"
        )
    ])

    # format_messages() fills in {context} and {query} and returns List[BaseMessage]
    return prompt.format_messages(context=context, query=query)


def load_vector_store(persist_directory: str = "vector_store") -> Chroma:
    """
    Reconnect to an existing ChromaDB on disk.
    Raises a clear error if no PDFs have been ingested yet.
    """
    if not os.path.exists(persist_directory):
        raise ValueError(
            f"Vector store not found at '{persist_directory}'. "
            "Please upload at least one PDF first via POST /upload."
        )

    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    return vector_store


def retrieve_and_answer(query: str, vector_store: Chroma) -> dict:
    """
    Core RAG function:
    1. Embed the query and find the top-k most similar chunks in ChromaDB
    2. Build a grounded prompt with the retrieved context
    3. Send to LLM and return the answer + source citations
    """
    if not query:
        raise ValueError("Query cannot be empty.")
    if vector_store is None:
        raise ValueError("Vector store is not initialized.")

    # STEP 1: Similarity search — query is embedded and compared to all stored vectors
    # k=5 means return the top 5 most semantically similar chunks
    relevant_chunks: List[Document] = vector_store.similarity_search(query, k=5)

    if not relevant_chunks:
        return {"answer": "No relevant information found in the uploaded documents."}

    # STEP 2: Build context string from retrieved chunks
    # Double newline between chunks keeps them visually separated in the prompt
    context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])

    # STEP 3: Build the structured prompt using ChatPromptTemplate (now actually used)
    messages = create_prompt(context, query)

    # STEP 4: Send to LLM — response is an AIMessage object
    response = llm.invoke(messages)

    # STEP 5: Return answer + source metadata so the client can cite where info came from
    return {
        "answer": response.content,
       
    }
