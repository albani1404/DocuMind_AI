# API (prefix `/api`, dokumentasi interaktif di `/docs`)

Semua endpoint selain `/auth/register` dan `/auth/login` memerlukan header `Authorization: Bearer <token>`.

| Method | Path | Keterangan |
|---|---|---|
| POST | /auth/register, /auth/login | Mengembalikan `access_token` dan `user` |
| GET | /auth/me | Profil pengguna |
| POST | /documents | Upload (multipart `file`); proses berjalan di background |
| GET | /documents, /documents/{id} | Daftar / detail + status |
| GET | /documents/{id}/pages | Teks per halaman |
| GET | /documents/{id}/file | Unduh file asli |
| POST | /documents/{id}/reprocess | Ulangi pemrosesan |
| DELETE | /documents/{id} | Hapus file, halaman, dan vektor |
| POST | /chat | `{question, conversation_id?, document_ids?}` → `{answer, sources[]}` |
| GET | /chat/conversations, /chat/conversations/{id} | Riwayat |
| POST | /search | Pencarian semantik tanpa LLM |
| POST | /ai/documents/{id}/summary | Ringkasan |
| POST | /ai/documents/{id}/extract | Ekstraksi terstruktur (JSON) |
| POST | /ai/compare | `{document_a, document_b, focus?}` |
| GET | /ai/analytics | Statistik akun |

Kode error: 400 isi file tidak cocok, 401 token, 409 dokumen belum terindeks, 413 terlalu besar, 415 tipe tidak didukung, 503 `GEMINI_API_KEY` belum diatur.
