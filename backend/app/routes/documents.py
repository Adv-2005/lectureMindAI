from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.core.config import settings
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

@router.delete("/documents/{document_id}")
def delete_document(document_id: str):
    results = collection.get(
    where={
        "document_id": document_id
    },
    include=["metadatas"]
)
    ids = results["ids"]
    if not ids:
        raise HTTPException(status_code=404, detail="Document not found")

    metadata = results.get("metadatas") or []
    first_metadata = next(
        (meta for meta in metadata if isinstance(meta, dict)),
        {},
    )
    filename = first_metadata.get("filename")
    stored_filename = first_metadata.get("stored_filename") or filename

    if stored_filename:
        # Older indexed uploads do not include stored_filename. Their vector
        # records are still removed even if no matching file can be found.
        file_path = settings.uploads_dir / Path(stored_filename).name
        file_path.unlink(missing_ok=True)

    collection.delete(ids=ids)

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "filename": filename,
        "deleted_chunks": len(ids)
    }
