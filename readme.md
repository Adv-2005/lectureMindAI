# Real-Time Multimodal RAG Study Assistant

An end-to-end Retrieval-Augmented Generation (RAG) system built from scratch to understand the internals of modern AI retrieval systems without relying on frameworks such as LangChain or LlamaIndex.

The project enables users to upload lecture PDFs and ask natural-language questions about the content. It performs semantic retrieval using vector embeddings and generates grounded responses using a locally hosted Large Language Model (LLM).

## Features

### Implemented (V1)

* PDF upload and ingestion
* Text extraction using PyMuPDF
* Configurable text chunking with overlap
* Semantic embeddings using BAAI/bge-small-en-v1.5
* Vector storage and similarity search using ChromaDB
* Context-aware question answering using Qwen 2.5 via Ollama
* Source metadata tracking
* Document identifiers for scalable multi-document support
* Conversational query rewriting for follow-up questions
* FastAPI backend APIs
* Next.js frontend interface

### Example Queries

* What is gradient descent?
* Explain backpropagation in simple terms.
* Summarize the key concepts discussed in this document.
* How does it differ from stochastic gradient descent?

## Architecture

```text
PDF Upload
    ↓
Text Extraction (PyMuPDF)
    ↓
Chunking
    ↓
Embeddings (BGE)
    ↓
ChromaDB
    ↓
Query Rewriting
    ↓
Semantic Retrieval
    ↓
Context Assembly
    ↓
Qwen 2.5 (Ollama)
    ↓
Grounded Answer
```

## Tech Stack

### Frontend

* Next.js 15
* TypeScript
* Tailwind CSS
* Axios

### Backend

* FastAPI
* Uvicorn

### AI / ML

* BAAI/bge-small-en-v1.5
* SentenceTransformers
* Qwen 2.5 1.5B
* Ollama

### Database

* ChromaDB

### Document Processing

* PyMuPDF (fitz)

## Project Structure

```text
backend/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── db/
│   ├── utils/
│   └── main.py
│
├── uploads/
└── chroma_db/

frontend/
│
└── src/
    ├── app/
    ├── components/
    └── lib/
```

## How It Works

### 1. Document Ingestion

When a PDF is uploaded:

* Text is extracted using PyMuPDF
* Text is split into chunks
* Embeddings are generated using BGE
* Chunks and metadata are stored in ChromaDB

### 2. Query Processing

When a user asks a question:

* Conversation history is used to rewrite follow-up questions into standalone queries
* The query is converted into an embedding
* ChromaDB retrieves the most relevant chunks
* Retrieved context is passed to Qwen through Ollama
* A grounded answer is generated

### 3. Metadata Storage

Each chunk stores metadata such as:

```json
{
  "document_id": "...",
  "filename": "...",
  "page": 1,
  "chunk_id": 0
}
```

This enables future support for:

* Multi-document retrieval
* Source citations
* Page-level references
* Document filtering

## Running Locally

### Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

### Ollama

Install Ollama and pull the model:

```bash
ollama pull qwen2.5:1.5b
```

Run the model:

```bash
ollama run qwen2.5:1.5b
```

### Frontend

Install dependencies:

```bash
npm install
```

Run the application:

```bash
npm run dev
```

## API Endpoints

### Upload PDF

```http
POST /upload
```

Uploads and indexes a PDF document.

### Ask Question

```http
POST /query
```

Request:

```json
{
  "query": "What is gradient descent?"
}
```

Response:

```json
{
  "answer": "...",
  "sources": [...]
}
```

## Roadmap

### V2 — Multi-Document Knowledge Base

* Multiple PDF support
* Document filtering
* Cross-document retrieval
* Source citations

### V3 — Audio RAG

* Whisper transcription
* Timestamp-aware retrieval
* Lecture audio support

### V4 — Video Processing

* Video ingestion
* Frame extraction
* Timestamp retrieval

### V5 — Multimodal RAG

* Unified retrieval across PDFs, audio, and video
* Cross-modal search
* Context fusion

### V6 — Advanced Retrieval

* Hybrid Search (BM25 + Vector Search)
* Reranking
* Query Expansion
* Context Compression

### V7 — Real-Time Processing

* Streaming ingestion
* WebSockets
* Live querying

### V8 — AI Study Assistant

* Summaries
* Flashcards
* Quiz generation
* Topic extraction

### V9 — Production Deployment

* Authentication
* User accounts
* Background jobs
* Monitoring and analytics

## Why No LangChain or LlamaIndex?

This project intentionally avoids abstraction frameworks in order to:

* Understand RAG internals deeply
* Learn retrieval engineering concepts
* Gain debugging experience
* Build AI systems from first principles

The goal is to master the underlying architecture before introducing higher-level frameworks.

## License

MIT License
