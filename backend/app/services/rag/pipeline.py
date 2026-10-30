"""RAG: retrieve -> rerank -> context assembly -> Gemini -> jawaban + sumber halaman."""
from app.core.config import get_settings
from app.services.retrieval.retriever import retrieve
from app.services.reranking.reranker import rerank
from app.services.llm.gemini import generate

SYSTEM = (
    "Kamu adalah asisten analisis dokumen. Jawab HANYA berdasarkan konteks yang diberikan. "
    "Jika jawabannya tidak ada di konteks, katakan dengan jelas bahwa dokumen tidak memuatnya. "
    "Setiap klaim harus diberi sitasi dengan format [S1], [S2] sesuai nomor sumber. "
    "Jawab dalam bahasa yang sama dengan pertanyaan pengguna, ringkas dan terstruktur."
)


def assemble_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[S{i}] ({c['filename']}, halaman {c['page']})\n{c['text']}" for i, c in enumerate(chunks, 1))


def to_sources(chunks: list[dict]) -> list[dict]:
    return [{
        "document_id": c["document_id"], "filename": c["filename"], "page": c["page"],
        "score": round(c.get("rerank_score", c["score"]), 4), "snippet": c["text"][:280],
    } for c in chunks]


def answer_question(question: str, owner_id: int, document_ids: list[int] | None,
                    history: list[dict] | None = None) -> tuple[str, list[dict]]:
    s = get_settings()
    candidates = retrieve(question, owner_id, document_ids, s.top_k)
    top = rerank(question, candidates, s.top_n)
    if not top:
        return "Saya tidak menemukan informasi yang relevan di dokumen Anda.", []
    hist = ""
    if history:
        hist = "Riwayat percakapan:\n" + "\n".join(f"{m['role']}: {m['content'][:500]}" for m in history[-6:]) + "\n\n"
    prompt = f"{hist}Konteks:\n{assemble_context(top)}\n\nPertanyaan: {question}\n\nJawaban:"
    return generate(prompt, system=SYSTEM), to_sources(top)
