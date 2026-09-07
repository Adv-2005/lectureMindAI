from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """Create the embedding implementation used by the existing Chroma collection."""
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


def get_vector_store() -> Chroma:
    """Return the LangChain view of the persistent LectureMindAI collection."""
    settings.prepare_directories()
    return Chroma(
        collection_name=settings.chroma_collection,
        persist_directory=str(settings.chroma_path),
        embedding_function=get_embeddings(),
    )


def save_upload(original_filename: str, content: bytes) -> tuple[str, Path]:
    """Store an upload under a collision-resistant internal filename."""
    document_id = str(uuid4())
    safe_filename = Path(original_filename or "lecture.pdf").name
    stored_filename = f"{document_id}_{safe_filename}"
    file_path = settings.uploads_dir / stored_filename
    file_path.write_bytes(content)
    return document_id, file_path


def load_and_split_pdf(
    file_path: Path,
    document_id: str,
    original_filename: str,
) -> list[Document]:
    """Load a PDF page-by-page, split it, and retain retrieval/citation metadata."""
    loader = PyMuPDFLoader(str(file_path))
    pages = loader.load()
    uploaded_at = datetime.now(UTC).isoformat()

    for page in pages:
        # PyPDFLoader uses a zero-based page index; citations remain one-based.
        page.metadata.update(
            {
                "document_id": document_id,
                "filename": original_filename,
                "stored_filename": file_path.name,
                "source_type": "pdf",
                "uploaded_at": uploaded_at,
                "page": int(page.metadata.get("page", 0)) + 1,
            }
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(pages)
    for chunk_index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = chunk_index
    return [chunk for chunk in chunks if chunk.page_content.strip()]


def index_documents(documents: Iterable[Document], document_id: str) -> int:
    """Embed and persist chunks through LangChain's Chroma integration."""
    chunks = list(documents)
    if not chunks:
        return 0

    ids = [f"{document_id}_{index}" for index in range(len(chunks))]
    get_vector_store().add_documents(chunks, ids=ids)
    return len(chunks)
