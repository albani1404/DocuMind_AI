import difflib
from app.services.llm.gemini import generate

SYSTEM = "Kamu membandingkan dua dokumen secara objektif dalam Bahasa Indonesia. Sebut halaman bila relevan."


def _flat(pages, limit=25_000) -> str:
    return "\n".join(f"[H{n}] {t}" for n, t in pages)[:limit]


def lexical_similarity(a: str, b: str) -> float:
    return round(difflib.SequenceMatcher(None, a[:20000], b[:20000]).ratio(), 4)


def compare_documents(name_a: str, pages_a, name_b: str, pages_b, focus: str | None = None) -> dict:
    ta, tb = _flat(pages_a), _flat(pages_b)
    prompt = (
        f"Bandingkan Dokumen A ({name_a}) dan Dokumen B ({name_b})."
        + (f" Fokus: {focus}." if focus else "")
        + "\nFormat: ## Kesamaan, ## Perbedaan utama, ## Hal yang hanya ada di A, "
          "## Hal yang hanya ada di B, ## Kesimpulan.\n\n"
        f"=== DOKUMEN A ===\n{ta}\n\n=== DOKUMEN B ===\n{tb}")
    return {"similarity": lexical_similarity(ta, tb), "analysis": generate(prompt, system=SYSTEM)}
