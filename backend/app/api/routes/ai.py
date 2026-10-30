from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.repositories import DocumentRepo
from app.schemas import CompareIn, DocumentOut
from app.services.llm.gemini import LLMNotConfigured
from app.services.summarization.summarizer import summarize
from app.services.information_extraction.extractor import extract_information
from app.services.document_comparison.comparer import compare_documents

router = APIRouter(prefix="/ai", tags=["ai"])


def _ready(db, doc_id, user):
    doc = DocumentRepo(db).get(doc_id, user.id)
    if not doc:
        raise HTTPException(404, "Dokumen tidak ditemukan")
    if doc.status != "indexed":
        raise HTTPException(409, f"Dokumen belum siap (status: {doc.status})")
    return doc, [(p.page_number, p.text) for p in doc.pages]


def _llm(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except LLMNotConfigured as e:
        raise HTTPException(503, str(e))


@router.post("/documents/{doc_id}/summary", response_model=DocumentOut)
def make_summary(doc_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    doc, pages = _ready(db, doc_id, user)
    doc.summary = _llm(summarize, pages); db.commit()
    return doc


@router.post("/documents/{doc_id}/extract", response_model=DocumentOut)
def make_extraction(doc_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    doc, pages = _ready(db, doc_id, user)
    doc.extracted = _llm(extract_information, pages); db.commit()
    return doc


@router.post("/compare")
def compare(body: CompareIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if body.document_a == body.document_b:
        raise HTTPException(400, "Pilih dua dokumen yang berbeda")
    a, pa = _ready(db, body.document_a, user)
    b, pb = _ready(db, body.document_b, user)
    return _llm(compare_documents, a.filename, pa, b.filename, pb, body.focus)


@router.get("/analytics")
def analytics(db: Session = Depends(get_db), user=Depends(current_user)):
    return DocumentRepo(db).stats(user.id)
