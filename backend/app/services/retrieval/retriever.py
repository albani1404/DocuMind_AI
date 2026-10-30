from app.core.config import get_settings
from app.services.embeddings.bge_m3 import embed_query
from app.services.vector_store import chroma_store


def retrieve(query: str, owner_id: int, document_ids: list[int] | None = None, k: int | None = None) -> list[dict]:
    """Semantic retrieval top-K dari ChromaDB."""
    return chroma_store.query(embed_query(query), owner_id, document_ids, k or get_settings().top_k)
