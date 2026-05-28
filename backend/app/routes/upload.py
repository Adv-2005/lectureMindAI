from fastapi import APIRouter, UploadFile, File
import os
from app.services.pdf_service import extract_text_from_pdf
from app.utils.chunker import chunk_text
from app.services.embedding_service import generate_embedding
from app.db.chroma import collection

router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    extracted_text = extract_text_from_pdf(file_path)
    chunks = chunk_text(extracted_text)
    embeddings = generate_embedding(chunks)
    ids = [f"{file.filename}_{i}" for i in range(len(chunks))]
    collection.add(documents = chunks, embeddings = embeddings.tolist(), ids = ids)
    return {"filename": file.filename, "chunks": len(chunks), "message": "File uploaded successfully!"}
