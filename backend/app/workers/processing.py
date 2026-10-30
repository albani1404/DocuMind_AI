"""Pemrosesan dokumen di background: parse -> clean -> chunk -> embed -> simpan ke Chroma."""
import json
import logging
from pathlib import Path
from app.core.config import get_settings
from app.database.session import SessionLocal
from app.models import Document, DocumentPage

log = logging.getLogger(__name__)


def process_document(doc_id: int) -> None:
    from app.services.document_parser.parser import parse_document
    from app.services.preprocessing.cleaner import clean_text
    from app.services.chunking.chunker import chunk_pages
    from app.services.embeddings.bge_m3 import embed_texts
    from app.services.vector_store import chroma_store

    s = get_settings()
    db = SessionLocal()
    try:
        doc = db.get(Document, doc_id)
        if not doc:
            return
        doc.status, doc.error = "processing", None
        db.commit()

        parsed = parse_document(Path(doc.stored_path), doc.file_type)
        cleaned = [(p.page_number, clean_text(p.text)) for p in parsed]
        if not any(t for _, t in cleaned):
            raise ValueError("Tidak ada teks yang dapat diekstrak dari dokumen ini.")

        db.query(DocumentPage).filter_by(document_id=doc.id).delete()
        for p, (_, text) in zip(parsed, cleaned):
            db.add(DocumentPage(document_id=doc.id, page_number=p.page_number, text=text,
                                ocr_confidence=p.ocr_confidence))
        doc.page_count = len(parsed)
        doc.used_ocr = any(p.used_ocr for p in parsed)

        Path(s.processed_dir).mkdir(parents=True, exist_ok=True)
        (Path(s.processed_dir) / f"{doc.id}.json").write_text(
            json.dumps([{"page": n, "text": t} for n, t in cleaned], ensure_ascii=False), encoding="utf-8")

        chunks = chunk_pages([(n, t) for n, t in cleaned if t], s.chunk_size, s.chunk_overlap)
        chroma_store.delete_document(doc.id)
        chroma_store.add_chunks(doc.id, doc.owner_id, doc.filename, chunks,
                                embed_texts([c.text for c in chunks]))
        doc.chunk_count, doc.status = len(chunks), "indexed"
        db.commit()
        log.info("Dokumen %s terindeks: %s halaman, %s chunk", doc.id, doc.page_count, len(chunks))
    except Exception as e:  # noqa: BLE001
        log.exception("Gagal memproses dokumen %s", doc_id)
        db.rollback()
        doc = db.get(Document, doc_id)
        if doc:
            doc.status, doc.error = "failed", str(e)[:500]
            db.commit()
    finally:
        db.close()
