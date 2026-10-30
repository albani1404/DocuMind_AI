# 📄 DocuMind AI — Intelligent Document Understanding System

> **Tanya jawab dokumen dengan AI — jawaban selalu disertai halaman sumber.**

Unggah PDF, DOCX, atau gambar hasil scan, lalu tanyakan isinya. DocuMind AI memahami konteks dokumen Anda dan menjawab dengan sitasi halaman `[S1]` yang bisa diverifikasi.

![Stack](https://img.shields.io/badge/React%2BTypeScript-Vite-61DAFB) ![Backend](https://img.shields.io/badge/FastAPI-Python-009688) ![DB](https://img.shields.io/badge/PostgreSQL-SQLite-336791) ![Vector](https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6F00) ![AI](https://img.shields.io/badge/Gemini%20API-LLM-4285F4)

---

## ✨ Fitur Utama

- 📤 **Upload dokumen** (PDF, DOCX, JPG/PNG scan) dengan validasi ekstensi, ukuran, & magic bytes.
- 🔍 **OCR otomatis** untuk dokumen scan (PaddleOCR).
- 🧠 **RAG (Retrieval-Augmented Generation)** — jawaban berbasis konteks dokumen, bukan halusinasi.
- 📑 **Sitasi halaman** `[S1]`, `[S2]` — setiap jawaban bisa ditelusuri ke sumbernya.
- 📝 **Ringkasan**, ekstraksi informasi terstruktur, dan **perbandingan dua dokumen**.
- 💬 **Riwayat chat** per percakapan, multi-dokumen dalam satu sesi.
- 📊 **Analitik dasar** & dashboard pengguna.
- 🔐 **Autentikasi JWT** + isolasi data per pengguna.

## 🛠️ Tech Stack

| Layer | Teknologi |
|---|---|
| Frontend | React + TypeScript (Vite) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL (SQLite untuk dev cepat) |
| Vector Store | ChromaDB |
| Embedding | BGE-M3 |
| Reranker | BGE Reranker v2-m3 |
| OCR | PaddleOCR |
| LLM | Gemini API (Google) |

---

## 🚀 Menjalankan (Lokal)

```bash
cp .env.example backend/.env        # isi GEMINI_API_KEY dan SECRET_KEY
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload       # http://localhost:8000/docs
# Frontend (terminal lain)
cd frontend && npm install && npm run dev   # http://localhost:5173
```

> Tanpa PostgreSQL, untuk uji cepat: `DATABASE_URL=sqlite:///./documind.db`.
> Model BGE-M3 (~2 GB) diunduh otomatis saat dokumen pertama diproses.

## 🐳 Menjalankan (Docker)

```bash
cp .env.example .env && docker compose up --build   # web: http://localhost:5173
```

---

## 🗺️ Roadmap & Cara Kerja Sistem

### Alur Upload & Indeksing Dokumen

```
┌──────────┐   ┌────────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Upload  │ → │  Validasi   │ → │ Parse /  │ → │ Cleaning │ → │ Chunking │ → │ Embedding│
│  PDF/    │   │ (ekstensi, │   │  OCR per │   │  teks    │   │ sadar    │   │ BGE-M3   │
│ DOCX/Img │   │  ukuran,   │   │ halaman  │   │          │   │ halaman  │   │          │
└──────────┘   │ magic bytes│   └──────────┘   └──────────┘   └──────────┘   └────┬─────┘
               └────────────┘                                                      │
                                                                                   ▼
                                                                            ┌────────────┐
                                                                            │  ChromaDB  │
                                                                            │ (vector +  │
                                                                            │  metadata) │
                                                                            └────────────┘
```

1. **Upload** — file diterima, disimpan ke `storage/uploads`.
2. **Validasi** — ekstensi, ukuran (max upload), dan magic bytes dicek.
3. **Parse / OCR per halaman** — PDF & DOCX diparse; gambar/scan diproses PaddleOCR; output berupa teks per halaman.
4. **Cleaning** — normalisasi whitespace, hapus artefak, perbaikan teks.
5. **Chunking sadar-halaman** — teks dipecah menjadi chunk dengan metadata `document_id` & `page`.
6. **Embedding BGE-M3** — setiap chunk di-embed menjadi vektor.
7. **Simpan ke ChromaDB** — vektor + metadata disimpan untuk pencarian semantik.

### Alur Tanya Jawab (RAG)

```
┌────────┐   ┌────────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────┐
│ Query  │ → │ Embed      │ → │ Top-K    │ → │ Rerank   │ → │ Context      │ → │  Gemini  │
│ user   │   │ query      │   │ retrieval│   │ top-N    │   │ assembly     │   │  LLM     │
└────────┘   └────────────┘   └──────────┘   └──────────┘   └──────────────┘   └────┬─────┘
                                                                                      │
                                                                                      ▼
                                                                               ┌────────────┐
                                                                               │ Jawaban +  │
                                                                               │ sitasi [S1]│
                                                                               └────────────┘
```

1. **Query user** — pertanyaan masuk via `/api/chat`.
2. **Embed query** — pertanyaan di-embed dengan BGE-M3.
3. **Top-K retrieval** — chunk paling relevan (top-20) diambil dari ChromaDB.
4. **Rerank** — BGE Reranker menyaring ke top-5 paling relevan.
5. **Context assembly** — chunk terpilih dirakit jadi konteks bernomor `[S1]`, `[S2]`, …
6. **Gemini LLM** — menghasilkan jawaban berbasis konteks.
7. **Jawaban + sitasi** — dikembalikan ke user beserta referensi halaman sumber.

### Status Implementasi

| Fase | Status |
|---|---|
| 1 Inisialisasi | ✅ Selesai |
| 2 Document processing (PDF/DOCX/OCR) | ✅ Selesai |
| 3 Embedding engine | ✅ Selesai |
| 4 RAG engine | ✅ Selesai |
| 5 Fitur lanjutan (ringkasan, ekstraksi, perbandingan, multi-dokumen, riwayat chat) | ✅ Selesai |
| 6 Frontend | Dashboard, dokumen, viewer, chat, ringkasan, ekstraksi, pencarian, perbandingan, analitik dasar |
| 7 Testing | Unit test dasar + skrip evaluasi OCR/retrieval; RAG eval & load test belum |
| 8 Produksi | Auth JWT + Docker selesai; monitoring & deploy belum |

### Roadmap ke Depan

- [ ] RAG evaluation & load testing
- [ ] Monitoring (metrics, tracing) & deploy pipeline
- [ ] Dukungan format dokumen tambahan (XLSX, PPTX)
- [ ] Multi-bahasa & model embedding alternatif
- [ ] Plugin/ekstensi browser untuk ingest cepat

---

## 📚 Dokumentasi Lainnya

Lihat folder `docs/` untuk arsitektur, skema database, referensi API, dan roadmap detail.

## 🤝 Kontribusi

Pull request & issue sangat diterima. Pastikan menjalankan test sebelum submit.

## 📜 Lisensi

MIT — lihat `LICENSE`.
