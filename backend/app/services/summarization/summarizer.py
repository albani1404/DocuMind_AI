from app.services.llm.gemini import generate

SYSTEM = "Kamu meringkas dokumen secara akurat dalam Bahasa Indonesia tanpa menambah fakta di luar teks."
MAX_CHARS = 60_000


def _window(pages: list[tuple[int, str]]) -> str:
    text = "\n\n".join(f"[Halaman {n}]\n{t}" for n, t in pages)
    if len(text) <= MAX_CHARS:
        return text
    half = MAX_CHARS // 2
    return text[:half] + "\n\n[... bagian tengah dipangkas ...]\n\n" + text[-half:]


def summarize(pages: list[tuple[int, str]]) -> str:
    prompt = (
        "Buat ringkasan dokumen berikut dengan format:\n"
        "1. Ringkasan eksekutif (3-5 kalimat)\n2. Poin-poin utama (maks 7 butir, sebut halaman)\n"
        "3. Kesimpulan atau rekomendasi (jika ada)\n\n" + _window(pages))
    return generate(prompt, system=SYSTEM)
