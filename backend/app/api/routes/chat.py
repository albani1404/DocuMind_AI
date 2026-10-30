import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models import Conversation, Message
from app.schemas import ChatIn, ChatOut, ConversationOut, MessageOut
from app.services.llm.gemini import LLMNotConfigured
from app.services.rag.pipeline import answer_question

log = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatOut)
def ask(body: ChatIn, db: Session = Depends(get_db), user=Depends(current_user)):
    conv = db.get(Conversation, body.conversation_id) if body.conversation_id else None
    if conv and conv.owner_id != user.id:
        raise HTTPException(404, "Percakapan tidak ditemukan")
    if not conv:
        conv = Conversation(owner_id=user.id, title=body.question[:80], document_ids=body.document_ids)
        db.add(conv); db.commit(); db.refresh(conv)
    history = [{"role": m.role, "content": m.content} for m in conv.messages]
    doc_ids = body.document_ids or conv.document_ids
    try:
        answer, sources = answer_question(body.question, user.id, doc_ids, history)
    except LLMNotConfigured as e:
        raise HTTPException(503, str(e))
    except Exception as e:  # noqa: BLE001
        log.exception("Gagal menjawab pertanyaan")
        raise HTTPException(502, f"Gagal menjawab ({type(e).__name__}): {str(e)[:300]}")
    db.add(Message(conversation_id=conv.id, role="user", content=body.question))
    db.add(Message(conversation_id=conv.id, role="assistant", content=answer, sources=sources))
    db.commit()
    return ChatOut(conversation_id=conv.id, answer=answer, sources=sources)


@router.get("/conversations", response_model=list[ConversationOut])
def conversations(db: Session = Depends(get_db), user=Depends(current_user)):
    return db.query(Conversation).filter_by(owner_id=user.id).order_by(Conversation.id.desc()).all()


@router.get("/conversations/{cid}", response_model=list[MessageOut])
def messages(cid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    conv = db.get(Conversation, cid)
    if not conv or conv.owner_id != user.id:
        raise HTTPException(404, "Percakapan tidak ditemukan")
    return conv.messages


@router.delete("/conversations/{cid}", status_code=204)
def delete_conversation(cid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    conv = db.get(Conversation, cid)
    if not conv or conv.owner_id != user.id:
        raise HTTPException(404, "Percakapan tidak ditemukan")
    db.delete(conv); db.commit()