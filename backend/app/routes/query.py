from itertools import zip_longest

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.chroma import collection
from app.services.embedding_service import model
from app.services.llm_service import (generate_answer,rewrite_query)
from app.services.chat_memory import chat_sessions
from typing import List


router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    session_id: str
    selected_documents: List[str] = []

@router.post("/query")
def query_rag(request: QueryRequest):
    
    chat_history = chat_sessions.get(request.session_id, [])
    rewritten_query = rewrite_query(chat_history, request.query)
    query_embedding = model.encode(rewritten_query)
    query_params = {
        "query_embeddings": [query_embedding.tolist()],
        "n_results": 5,
        "include": ["documents", "metadatas"]
    }
    if request.selected_documents:
        query_params["where"] = {"document_id": {"$in": request.selected_documents}}
    results = collection.query(**query_params)
    retrieved_chunks = results['documents'][0]
    metadata = results['metadatas'][0] or []
    used_documents = list(
    {
        meta["filename"]
        for meta in metadata
        if meta
    }
)
    #retrieval gaurd
    if not retrieved_chunks:
        return {
            "answer": "I could not find that information in the uploaded material.",
            "context": [],
            "sources": [],
            "used_documents": used_documents
        }
    context_parts = []
    for chunk, meta in zip_longest(retrieved_chunks, metadata, fillvalue=None):
        if not chunk:
            continue
        if not meta:
            source_info = "Unknown source"
        else:
            source_info = f"{meta['filename']} (Page {meta['page']})" if 'page' in meta else meta['filename']
        context_parts.append(f"Source: {source_info}\nContent: {chunk}")
    context = "\n".join(context_parts)
    answer = generate_answer(context, rewritten_query)
    if request.session_id not in chat_sessions:
        chat_sessions[request.session_id] = []

    chat_sessions[request.session_id].append(
    {
        "role": "user",
        "content": request.query
    }
)

    chat_sessions[request.session_id].append(
    {
        "role": "assistant",
        "content": answer
    }
)
    MAX_MESSAGES = 10

    if len(chat_sessions[request.session_id]) > MAX_MESSAGES:
        chat_sessions[request.session_id] = chat_sessions[request.session_id][-MAX_MESSAGES:]
    return {"answer": answer, "context": retrieved_chunks, "sources": metadata, "used_documents": used_documents}