from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime settings for the local LectureMindAI stack."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_prefix="LECTUREMIND_",
        extra="ignore",
    )

    ollama_base_url: str = "http://localhost:11434"
    chat_model: str = "qwen2.5:1.5b"
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_collection: str = "lecture_notes"
    chroma_path: Path = BACKEND_DIR / "chroma_db"
    uploads_dir: Path = BACKEND_DIR / "uploads"
    checkpoint_db_path: Path = BACKEND_DIR / "langgraph_checkpoints.sqlite"
    retrieval_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200

    def model_post_init(self, __context: object) -> None:
        """Resolve user-supplied relative paths from the backend directory."""
        for field_name in ("chroma_path", "uploads_dir", "checkpoint_db_path"):
            path = getattr(self, field_name)
            if not path.is_absolute():
                setattr(self, field_name, BACKEND_DIR / path)

    def prepare_directories(self) -> None:
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_db_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
