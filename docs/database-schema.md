# Skema database (PostgreSQL)

| Tabel | Kolom penting |
|---|---|
| users | id, email (unik), name, password_hash, created_at |
| documents | id, owner_id→users, filename, stored_path, file_type, size_bytes, page_count, chunk_count, status, error, used_ocr, summary, extracted (JSON), created_at |
| document_pages | id, document_id→documents (cascade), page_number, text, ocr_confidence |
| conversations | id, owner_id→users, title, document_ids (JSON, null = semua), created_at |
| messages | id, conversation_id→conversations (cascade), role, content, sources (JSON), created_at |

ChromaDB collection `documind_chunks` (cosine): id `"{document_id}:{chunk_index}"`, metadata `document_id, owner_id, filename, page, chunk_index`.

Skema dibuat otomatis oleh `init_db()` saat startup. Untuk produksi gunakan Alembic (`app/database/migrations`).
