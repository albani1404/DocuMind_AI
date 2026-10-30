from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.core.config import get_settings
from app.database.session import get_db
from app.models import Document
from app.repositories import DocumentRepo
from app.schemas import DocumentOut, PageOut
from app.utils.files import safe_name, unique_path, magic_ok
from app.workers.processing import process_document

router = APIRouter(prefix="/documents", tags=["documents"])


def _own(db, doc_id, user) -> Document:
    doc = DocumentRepo(db).get(doc_id, user.id)
    if not doc:
        raise HTTPException(404, "Dokumen tidak ditemukan")
    return doc


@router.post("", response_model=DocumentOut, status_code=201)
async def upload(bg: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db),
                 user=Depends(current_user)):
    s = get_settings()
    ext = Path(file.filename or "").suffix.lower().lstrip(".")
    if ext not in s.allowed_ext.split(","):
        raise HTTPException(415, f"Tipe file tidak didukung. Gunakan: {s.allowed_ext}")
    data = await file.read()
    if len(data) > s.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Ukuran file melebihi {s.max_upload_mb} MB")
    if not data or not magic_ok(ext, data[:8]):
        raise HTTPException(400, "Isi file tidak cocok dengan ekstensinya")
    Path(s.upload_dir).mkdir(parents=True, exist_ok=True)
    path = unique_path(s.upload_dir, ext)
    path.write_bytes(data)
    doc = Document(owner_id=user.id, filename=safe_name(file.filename or "dokumen"), stored_path=str(path),
                   file_type=ext, size_bytes=len(data), status="uploaded")
    db.add(doc); db.commit(); db.refresh(doc)
    bg.add_task(process_document, doc.id)
    return doc


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), user=Depends(current_user)):
    return DocumentRepo(db).list_for(user.id)


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    return _own(db, doc_id, user)


@router.get("/{doc_id}/pages", response_model=list[PageOut])
def get_pages(doc_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    return _own(db, doc_id, user).pages


@router.get("/{doc_id}/file")
def download(doc_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    doc = _own(db, doc_id, user)
    return FileResponse(doc.stored_path, filename=doc.filename)


@router.post("/{doc_id}/reprocess", response_model=DocumentOut)
def reprocess(doc_id: int, bg: BackgroundTasks, db: Session = Depends(get_db), user=Depends(current_user)):
    doc = _own(db, doc_id, user)
    doc.status = "uploaded"; db.commit()
    bg.add_task(process_document, doc.id)
    return doc


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    from app.services.vector_store import chroma_store
    doc = _own(db, doc_id, user)
    chroma_store.delete_document(doc.id)
    Path(doc.stored_path).unlink(missing_ok=True)
    (Path(get_settings().processed_dir) / f"{doc.id}.json").unlink(missing_ok=True)
    db.delete(doc); db.commit()
