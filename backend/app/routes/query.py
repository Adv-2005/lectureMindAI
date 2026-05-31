from itertools import zip_longest

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.chroma import collection
from app.services.embedding_service import model
from app.services.llm_service import generate_answer

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def query_rag(request: QueryRequest):
    query_embedding = model.encode(request.query)
    results = collection.query(query_embeddings=[query_embedding.tolist()], n_results=3, include=["documents", "metadatas"])
    retrieved_chunks = results['documents'][0]
    metadata = results['metadatas'][0] or []
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
    answer = generate_answer(context, request.query)
    return {"answer": answer, "context": retrieved_chunks, "sources": metadata}