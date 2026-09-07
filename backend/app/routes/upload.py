import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.ingestion_service import index_documents, load_and_split_pdf, save_upload

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")

    document_id, file_path = save_upload(file.filename, content)
    try:
        documents = load_and_split_pdf(file_path, document_id, file.filename)
        chunk_count = index_documents(documents, document_id)
    except Exception as exc:
        logger.exception("Unable to process uploaded PDF (document_id=%s)", document_id)
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Unable to process PDF.") from exc

    if not chunk_count:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="No readable text was found in this PDF.")

    return {
        "filename": file.filename,
        "chunks": chunk_count,
        "message": "File uploaded successfully!",
        "document_id": document_id,
    }
