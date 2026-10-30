from fastapi import APIRouter, Depends
from app.api.dependencies import current_user
from app.core.config import get_settings
from app.schemas import SearchIn
from app.services.rag.pipeline import to_sources
from app.services.reranking.reranker import rerank
from app.services.retrieval.retriever import retrieve

router = APIRouter(prefix="/search", tags=["search"])


@router.post("")
def semantic_search(body: SearchIn, user=Depends(current_user)):
    """Pencarian semantik multi-dokumen (tanpa LLM)."""
    cands = retrieve(body.query, user.id, body.document_ids, max(get_settings().top_k, body.limit))
    return {"query": body.query, "results": to_sources(rerank(body.query, cands, body.limit))}
