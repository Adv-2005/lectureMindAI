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
    results = collection.query(query_embeddings=[query_embedding.tolist()], n_results=3)
    retrieved_chunks = results['documents'][0]
    context = "\n".join(retrieved_chunks)
    answer = generate_answer(context, request.query)
    return {"answer": answer, "context": retrieved_chunks}