# Roadmap

Fase 1–5 sudah ada kerangka fungsionalnya di kode. Pekerjaan lanjutan yang disarankan:

**Fase 7 (Testing)**: tambah integration test dengan dokumen sampel; dataset evaluasi retrieval (`scripts/evaluate_retrieval.py`) dan OCR (`scripts/evaluate_ocr.py`); evaluasi RAG (faithfulness, answer relevance); load test dengan Locust; uji keamanan (upload berbahaya, IDOR antar user).

**Fase 8 (Produksi)**: Alembic migration; rate limiting; antrian Celery/Redis; streaming jawaban (SSE); logging terstruktur + Prometheus/Grafana; HTTPS di reverse proxy; CI GitHub Actions; deploy (VPS + Docker Compose atau Cloud Run + Cloud SQL).

**Peningkatan kualitas**: hybrid search (BM25 + dense), pemilihan kolom/tabel pada PDF, highlight kotak sitasi di PDF asli, OCR bahasa Indonesia yang lebih baik (model Latin PaddleOCR), cache jawaban.
