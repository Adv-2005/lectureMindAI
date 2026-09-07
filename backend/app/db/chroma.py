import chromadb
from app.core.config import settings

settings.prepare_directories()

client = chromadb.PersistentClient(path=str(settings.chroma_path))

collection = client.get_or_create_collection(name=settings.chroma_collection)
