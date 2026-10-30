# Arsitektur

```
React (Vite) ──/api──> FastAPI ──> PostgreSQL   (user, dokumen, halaman, percakapan, metadata)
                          │──────> ChromaDB      (embedding + metadata: document_id, owner_id, page)
                          │──────> storage/      (uploads = file asli, processed = JSON hasil ekstraksi)
                          └──────> Gemini API    (jawaban, ringkasan, ekstraksi, perbandingan)
```

**Offline (ingestion)**: `workers/processing.py` dijalankan lewat `BackgroundTasks` → parser/OCR → cleaner → chunker → BGE-M3 → Chroma.
Status dokumen: `uploaded → processing → indexed | failed`.

**Online (query)**: `rag/pipeline.py` → `retrieval` (top-K=20) → `reranking` (top-N=5) → prompt berbasis konteks → `llm/gemini.py`.

**Keputusan desain**
- Isolasi data: setiap query Chroma difilter `owner_id`.
- Halaman OCR: halaman PDF dengan < 30 karakter teks otomatis di-OCR (PDF campuran didukung).
- DOCX tidak punya halaman tetap → dibagi "halaman virtual" ±3000 karakter agar sitasi tetap berguna.
- `BackgroundTasks` cukup untuk skala kecil; untuk beban tinggi ganti dengan Celery/RQ (antarmuka `process_document(doc_id)` tetap sama).
- Model berat (BGE-M3, reranker, PaddleOCR) dimuat lazy dan di-cache per proses.
