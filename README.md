<div align="center">

# 🧠 DocMind AI
### Domain-Specific Chatbot · Powered by Local LLMs

<br/>

> 🔒 **Zero cloud. Zero hallucinations. Zero privacy risk.**
>
> *An intelligent offline AI chatbot that answers questions directly from your organizational documents — running entirely on your machine.*

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5%2B-FF6B35?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Offline](https://img.shields.io/badge/100%25-OFFLINE-success?style=for-the-badge)

</div>

---

## 📖 Table of Contents

- [About The Project](#-about-the-project)
- [Key Features](#-key-features)
- [Screenshots](#-screenshots)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Running the Project](#-running-the-project)
- [API Reference](#-api-reference)
- [How It Works](#-how-it-works)
- [Configuration](#-configuration)
- [Roadmap](#-roadmap)
- [Author](#-author)
- [License](#-license)

---

## 🚀 About The Project

**DocMind AI** is a fully local, privacy-first RAG (Retrieval-Augmented Generation) pipeline that lets you chat with your own **PDF documents**. No API keys. No data sent to the cloud. No subscriptions. Your documents stay on your machine, and so does the AI.

> ⚠️ **PDF files only.** DocMind AI exclusively supports `.pdf` uploads. Other formats (`.docx`, `.txt`, etc.) are not accepted and will be rejected by the backend.

Built for developers, researchers, and teams who need to query internal knowledge bases, handbooks, resumes, technical docs, or any PDF — without compromising confidentiality.

**Tech Stack:**

| Layer | Technology |
|---|---|
| 🖥️ Frontend | Streamlit |
| ⚙️ Backend | FastAPI |
| 🔗 LLM Framework | LangChain |
| 🗄️ Vector Store | ChromaDB (persistent on disk) |
| 🤖 LLM | Ollama — `llama3.2:latest` |
| 📐 Embeddings | Ollama — `nomic-embed-text:latest` |
| 📄 PDF Parsing | PyPDF via LangChain |

---

## ✨ Key Features

- **📤 PDF-Only Upload & Background Ingestion** — Only `.pdf` files are accepted; any other format is rejected with a `400` error. Ingestion (chunking + embedding) runs in a background thread so the API responds instantly.
- **🔁 Smart Deduplication** — Already-ingested files are tracked in `ingested_files.json`; re-uploading the same file is detected and skipped automatically.
- **🔍 Semantic Search (RAG)** — Queries are embedded and matched to the top-5 most relevant document chunks using cosine similarity in ChromaDB.
- **🗑️ Document Management** — Delete any ingested document; its chunks are removed from the vector store, the tracking log, and disk simultaneously.
- **📋 Source Citations** — Every answer includes source cards showing which file and page the context came from.
- **💬 Persistent Chat History** — Conversation state is preserved in Streamlit's session for the duration of the session.
- **🌐 100% Offline** — Runs entirely on your local machine via Ollama. No internet connection required after setup.
- **🔒 Privacy First** — Your documents are never uploaded to any external service.

---

## 📸 Screenshots

### Upload & Document Management
> Upload PDFs and see all ingested documents with one-click deletion.

https://raw.githubusercontent.com/Abhinxvsharma/docmind-ai/main/screenshots/upload.png

### Chat Interface
> Ask anything about your documents and get grounded, cited answers.

https://raw.githubusercontent.com/Abhinxvsharma/docmind-ai/main/screenshots/chat.png

### Rich Answers with Source Cards
> Responses include page-level citations so you always know where the answer came from.

https://raw.githubusercontent.com/Abhinxvsharma/docmind-ai/main/screenshots/sources.png

> 📌 *Replace the screenshot URLs above with actual paths after adding your images to the repo.*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Upload PDF  │  │  Chat Input  │  │  Document Manager │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬──────────┘  │
└─────────┼────────────────┼───────────────────┼─────────────┘
          │  POST /upload  │  POST /query       │ GET/DELETE
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Background Task Queue                  │    │
│  │  load_single_pdf → chunk_documents → create_vector  │    │
│  └──────────────────────────┬──────────────────────────┘    │
└─────────────────────────────┼───────────────────────────────┘
                              │
          ┌───────────────────┼────────────────────┐
          ▼                   ▼                    ▼
  ┌───────────────┐  ┌─────────────────┐  ┌──────────────┐
  │  ChromaDB     │  │  Ollama LLM     │  │ ingested_    │
  │  (vector_     │  │  llama3.2       │  │ files.json   │
  │   store/)     │  │  (inference)    │  │ (dedup log)  │
  └───────────────┘  └─────────────────┘  └──────────────┘
          ▲                   ▲
          │  nomic-embed-text │  ChatOllama
          └───────────────────┘
              Ollama Embeddings
```

**RAG Flow:**
```
User Query
    │
    ▼
Embed query  ──►  ChromaDB similarity_search (k=5)
                         │
                         ▼
                  Top-5 relevant chunks
                         │
                         ▼
              Build prompt (system: context + human: query)
                         │
                         ▼
                   llama3.2 via Ollama
                         │
                         ▼
               Answer + Source citations
```

---

## 📂 Project Structure

```
docmind-ai/
│
├── main.py                  # FastAPI app — all API endpoints
│
├── services/
│   ├── __init__.py          # Makes services/ a Python package
│   ├── ingestion.py         # PDF loading, chunking, ChromaDB write
│   └── retrieval.py         # Embedding, similarity search, LLM call
│
├── frontend.py              # Streamlit UI
│
├── requirements.txt         # All Python dependencies
├── ingested_files.json      # Auto-generated — tracks ingested filenames
│
├── temp/                    # Auto-created — stores uploaded PDF files
└── vector_store/            # Auto-created — persistent ChromaDB data
```

---

## 🛠️ Prerequisites

Before running DocMind AI, make sure you have the following installed:

### 1. Python 3.10+
```bash
python --version   # should be 3.10 or higher
```

### 2. Ollama
Download and install from **[https://ollama.com/download](https://ollama.com/download)**

Then pull the required models:
```bash
# Embedding model (for vectorizing documents and queries)
ollama pull nomic-embed-text

# LLM (for generating answers)
ollama pull llama3.2
```

Verify Ollama is running:
```bash
ollama list   # should show both models
```

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/docmind-ai.git
cd docmind-ai

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Running the Project

You need **two terminals** running simultaneously.

### Terminal 1 — Start the FastAPI Backend
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`

Interactive API docs: `http://127.0.0.1:8000/docs`

### Terminal 2 — Start the Streamlit Frontend
```bash
streamlit run frontend.py
```
The UI will open automatically at `http://localhost:8501`

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a PDF file for ingestion |
| `POST` | `/query` | Query the ingested documents |
| `GET` | `/documents` | List all ingested document filenames |
| `DELETE` | `/document/{filename}` | Delete a document and its vector chunks |

### `POST /upload`
> ⚠️ **PDF files only.** Non-PDF uploads return `400 Bad Request`.
```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@your_document.pdf"
```
```json
{
  "message": "'your_document.pdf' uploaded successfully. Ingestion running in background.",
  "status": "processing"
}
```

### `POST /query`
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main topics covered?"}'
```
```json
{
  "answer": "Based on the documents, the main topics covered are..."
}
```

### `GET /documents`
```bash
curl http://127.0.0.1:8000/documents
```
```json
{
  "documents": ["handbook.pdf", "resume.pdf"]
}
```

### `DELETE /document/{filename}`
```bash
curl -X DELETE http://127.0.0.1:8000/document/handbook.pdf
```
```json
{
  "message": "'handbook.pdf' deleted successfully.",
  "status": "deleted"
}
```

---

## ⚙️ How It Works

### Ingestion Pipeline
1. **Upload** — Only `.pdf` files are accepted (validated server-side); the file is saved to `temp/` in 1MB streaming chunks (memory-efficient).
2. **Deduplication** — Filename is checked against `ingested_files.json`; duplicates are rejected.
3. **Background Task** — FastAPI's `BackgroundTasks` runs ingestion *after* the HTTP response is sent, keeping the API non-blocking.
4. **Loading** — `PyPDFLoader` loads only the newly uploaded file (not the entire `temp/` folder).
5. **Chunking** — `RecursiveCharacterTextSplitter` splits pages into 1000-character chunks with 200-character overlap to preserve sentence context.
6. **Embedding** — Each chunk is embedded via `nomic-embed-text` through Ollama.
7. **Storage** — Chunks are appended to the persistent ChromaDB store on disk (`vector_store/`).

### Query Pipeline
1. **Embed Query** — The user's question is embedded using the same `nomic-embed-text` model.
2. **Similarity Search** — ChromaDB returns the top 5 most semantically similar chunks.
3. **Prompt Construction** — A structured `ChatPromptTemplate` builds a grounded system prompt with the retrieved context.
4. **LLM Inference** — `llama3.2` via Ollama generates an answer strictly from the provided context.
5. **Return** — The answer is returned to the frontend along with source metadata.

---

## 🔧 Configuration

| Parameter | Location | Default | Description |
|-----------|----------|---------|-------------|
| `chunk_size` | `ingestion.py` | `1000` | Max characters per chunk |
| `chunk_overlap` | `ingestion.py` | `200` | Overlap between adjacent chunks |
| `k` (top results) | `retrieval.py` | `5` | Number of chunks retrieved per query |
| `embedding model` | `ingestion.py` / `retrieval.py` | `nomic-embed-text:latest` | Must match in both files |
| `llm model` | `retrieval.py` | `llama3.2:latest` | LLM used for answer generation |
| `vector_store dir` | `ingestion.py` / `retrieval.py` | `vector_store` | ChromaDB persistence directory |
| `temp dir` | `main.py` | `temp` | Uploaded PDFs storage folder |
| `BACKEND_URL` | `frontend.py` | `http://127.0.0.1:8000` | FastAPI base URL |

---

## 🗺️ Roadmap

- [x] PDF upload with background ingestion
- [x] File deduplication
- [x] Semantic search with ChromaDB
- [x] Full document deletion (vector store + disk)
- [x] Source citations with page numbers
- [x] Persistent chat history within session
- [ ] Multi-file upload in a single request
- [ ] Streaming LLM responses (token-by-token)
- [ ] Conversation memory (multi-turn context)
- [ ] Support for `.docx`, `.txt`, and `.md` files
- [ ] Re-rank retrieved chunks before prompting
- [ ] User authentication & multi-user support
- [ ] Docker / Docker Compose setup
- [ ] SharePoint / Confluence / HRMS integration
- [ ] Mobile application

---

## 👨‍💻 Author

<div align="center">

**Abhinav Sharma**

*Passionate about building AI/ML solutions that make a real-world impact 🚀*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/your-linkedin)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/your-github)

B.Tech CSE — Rayat Bahra Institute of Engineering & Nano-Technology, Hoshiarpur

</div>

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.

See [LICENSE](LICENSE) for full details.

---

<div align="center">

Made with ❤️ by Abhinav Sharma

⭐ Star this repo if you found it useful!

</div>
