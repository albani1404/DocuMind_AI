from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import Document, User, Conversation


class UserRepo:
    def __init__(self, db: Session): self.db = db

    def by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email.lower()))

    def get(self, uid: int) -> User | None:
        return self.db.get(User, uid)

    def create(self, email: str, name: str, password_hash: str) -> User:
        u = User(email=email.lower(), name=name, password_hash=password_hash)
        self.db.add(u); self.db.commit(); self.db.refresh(u)
        return u


class DocumentRepo:
    def __init__(self, db: Session): self.db = db

    def list_for(self, owner_id: int) -> list[Document]:
        return list(self.db.scalars(
            select(Document).where(Document.owner_id == owner_id).order_by(Document.created_at.desc())))

    def get(self, doc_id: int, owner_id: int) -> Document | None:
        d = self.db.get(Document, doc_id)
        return d if d and d.owner_id == owner_id else None

    def get_many(self, ids: list[int], owner_id: int) -> list[Document]:
        return list(self.db.scalars(
            select(Document).where(Document.id.in_(ids), Document.owner_id == owner_id)))

    def stats(self, owner_id: int) -> dict:
        q = lambda *c: self.db.execute(select(*c).where(Document.owner_id == owner_id)).one()
        total, pages, chunks, size = q(func.count(Document.id), func.coalesce(func.sum(Document.page_count), 0),
                                       func.coalesce(func.sum(Document.chunk_count), 0),
                                       func.coalesce(func.sum(Document.size_bytes), 0))
        by_status = dict(self.db.execute(
            select(Document.status, func.count()).where(Document.owner_id == owner_id).group_by(Document.status)).all())
        ocr = self.db.scalar(select(func.count()).where(Document.owner_id == owner_id, Document.used_ocr.is_(True))) or 0
        convs = self.db.scalar(select(func.count()).where(Conversation.owner_id == owner_id)) or 0
        return {"documents": total, "pages": int(pages), "chunks": int(chunks), "bytes": int(size),
                "by_status": by_status, "ocr_documents": ocr, "conversations": convs}
