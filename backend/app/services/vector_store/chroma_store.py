from functools import lru_cache
from app.core.config import get_settings

COLLECTION = "documind_chunks"


@lru_cache(maxsize=1)
def _collection():
    import chromadb
    client = chromadb.PersistentClient(path=get_settings().chroma_dir)
    return client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})


def add_chunks(doc_id: int, owner_id: int, filename: str, chunks, embeddings: list[list[float]]) -> None:
    col = _collection()
    col.upsert(
        ids=[f"{doc_id}:{c.index}" for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[{"document_id": doc_id, "owner_id": owner_id, "filename": filename,
                    "page": c.page, "chunk_index": c.index} for c in chunks],
    )


def delete_document(doc_id: int) -> None:
    _collection().delete(where={"document_id": doc_id})


def query(embedding: list[float], owner_id: int, document_ids: list[int] | None, k: int) -> list[dict]:
    where: dict = {"owner_id": owner_id}
    if document_ids:
        where = {"$and": [{"owner_id": owner_id}, {"document_id": {"$in": document_ids}}]}
    res = _collection().query(query_embeddings=[embedding], n_results=k, where=where,
                              include=["documents", "metadatas", "distances"])
    out = []
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        out.append({"text": text, "score": 1.0 - float(dist), **meta})
    return out
