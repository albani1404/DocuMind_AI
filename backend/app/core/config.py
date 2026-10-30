from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]  # documind-ai/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DocuMind AI"
    debug: bool = False
    cors_origins: str = "http://localhost:5173"

    database_url: str = "postgresql+psycopg2://documind:documind@localhost:5432/documind"
    secret_key: str = "ganti-dengan-secret-acak"
    access_token_minutes: int = 60 * 12

    upload_dir: str = str(ROOT / "storage" / "uploads")
    processed_dir: str = str(ROOT / "storage" / "processed")
    chroma_dir: str = str(ROOT / "storage" / "chroma")
    max_upload_mb: int = 25
    allowed_ext: str = "pdf,docx,jpg,jpeg,png"

    embedding_model: str = "BAAI/bge-m3"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    use_reranker: bool = True
    chunk_size: int = 900       # karakter
    chunk_overlap: int = 150
    top_k: int = 20             # kandidat retrieval
    top_n: int = 5              # setelah rerank

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    ocr_lang: str = "en"        # PaddleOCR: 'en', 'id' tidak tersedia -> gunakan 'latin' bila perlu


@lru_cache
def get_settings() -> Settings:
    return Settings()
