# app/routes/documents.py

from fastapi import APIRouter
from app.db.chroma import collection

router = APIRouter()


@router.get("/documents")
def get_documents():

    results = collection.get(
        include=["metadatas"]
    )

    metadatas = results.get("metadatas", [])

    documents = {}

    for meta in metadatas:

        # Skip empty/None metadata entries returned by the collection
        if not meta:
            continue

        document_id = meta.get("document_id")

        # Skip entries that don't have a document_id
        if not document_id:
            continue

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": meta.get("filename"),
                "source_type": meta.get("source_type", "pdf"),
                "chunk_count": 0,
                "uploaded_at": meta.get("uploaded_at")
            }

        documents[document_id]["chunk_count"] += 1

    return list(documents.values())