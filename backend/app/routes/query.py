from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.services.rag_graph import ask_question


router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    session_id: str
    selected_documents: List[str] = []

@router.post("/query")
def query_rag(request: QueryRequest):
    return ask_question(
        query=request.query,
        session_id=request.session_id,
        selected_documents=request.selected_documents,
    )
