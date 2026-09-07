# LectureMindAI

LectureMindAI is a local PDF study assistant built with FastAPI, Next.js,
LangChain, and LangGraph. Upload lecture notes and ask grounded questions about
them through a persistent conversational RAG workflow.

## Features

- PDF ingestion with LangChain's `PyMuPDFLoader`
- Page-aware recursive chunking with `RecursiveCharacterTextSplitter`
- Local `all-MiniLM-L6-v2` embeddings and persistent Chroma vector search
- Local Qwen chat generation through Ollama and LangChain
- LangGraph workflow for follow-up rewriting, retrieval, and grounded answers
- SQLite-backed LangGraph checkpoints, so sessions survive backend restarts
- Per-document filtering, source metadata, document listing, and deletion
- FastAPI JSON endpoints and a Next.js chat interface

## Architecture

```text
PDF upload
  -> PyMuPDFLoader
  -> RecursiveCharacterTextSplitter
  -> HuggingFace embeddings
  -> Chroma

Chat request (session_id)
  -> LangGraph SQLite checkpoint
  -> Rewrite follow-up question
  -> Retrieve Chroma documents
  -> Generate cited answer with Ollama/Qwen
  -> Persist updated conversation state
```

## Stack

- Frontend: Next.js, TypeScript, Tailwind CSS, Axios
- API: FastAPI and Uvicorn
- RAG: LangChain, LangGraph, Chroma, SentenceTransformers, PyMuPDF
- Local model: Ollama with `qwen2.5:1.5b`
- Conversation persistence: SQLite via `langgraph-checkpoint-sqlite`

## Run locally

### Backend

From `backend/`, create and activate a virtual environment, then install the
dependencies:

```bash
pip install -r requirements.txt
```

Optional: copy `.env.example` to `.env` to override the Ollama model, paths,
chunking, or retrieval settings. The embedding model is downloaded by
SentenceTransformers on its first use if it is not already cached.

Start the API:

```bash
uvicorn app.main:app --reload
```

### Ollama

Install Ollama, then download and run the local chat model:

```bash
ollama pull qwen2.5:1.5b
ollama run qwen2.5:1.5b
```

### Frontend

From `frontend/`:

```bash
npm install
npm run dev
```

## API

### `POST /upload`

Accepts a PDF in a multipart `file` field, indexes its chunks in Chroma, and
returns its `document_id`.

### `POST /query`

```json
{
  "query": "What is gradient descent?",
  "session_id": "browser-session-id",
  "selected_documents": ["optional-document-id"]
}
```

The response preserves the UI's existing JSON contract:

```json
{
  "answer": "...",
  "context": ["retrieved chunk"],
  "sources": [{ "filename": "lecture.pdf", "page": 4, "document_id": "..." }],
  "used_documents": ["lecture.pdf"]
}
```

`session_id` is the LangGraph thread ID. Reusing it restores conversation state
from `backend/langgraph_checkpoints.sqlite` after a backend restart.

### Document management

- `GET /documents` lists indexed documents.
- `DELETE /documents/{document_id}` removes its Chroma chunks and uploaded file.

## Notes on existing data

The refactor keeps the `lecture_notes` collection, the existing Chroma path,
and the original `all-MiniLM-L6-v2` embedding model. Existing vector records
therefore remain queryable. New uploads also record an internal stored filename
so deleting them removes the correct UUID-prefixed file.

## Next steps

Possible extensions include relevance grading, streaming responses, flashcard
and quiz graph branches, audio/video ingestion, authentication, and production
observability.

## License

MIT License
