from fastapi import APIRouter, UploadFile, File
import os
from app.services.pdf_service import extract_text_from_pdf
from app.utils.chunker import chunk_text
from app.services.embedding_service import generate_embedding
from app.db.chroma import collection
from uuid import uuid4
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    document_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    extracted_pages = extract_text_from_pdf(pdf_path=file_path, document_id=document_id, filename=file.filename)
    all_chunks = []
    all_metadata = []

    for page in extracted_pages:
        chunks = chunk_text(page["text"])
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append({
                "filename": file.filename,
                "page": page["page"],
                "source_type": "pdf",
                "document_id": document_id,
                "uploaded_at": datetime.utcnow().isoformat()
            })
    embeddings = generate_embedding(all_chunks)
    ids = [f"{document_id}_{i}" for i in range(len(all_chunks))]
    collection.add(documents = all_chunks, embeddings = embeddings.tolist(), ids = ids, metadatas = all_metadata)
    return {"filename": file.filename, "chunks": len(all_chunks), "message": "File uploaded successfully!", "document_id": document_id}
