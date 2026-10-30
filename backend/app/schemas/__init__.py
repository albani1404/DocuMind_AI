from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    file_type: str
    size_bytes: int
    page_count: int
    chunk_count: int
    status: str
    error: str | None = None
    used_ocr: bool
    summary: str | None = None
    extracted: dict | None = None
    created_at: datetime


class PageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    page_number: int
    text: str
    ocr_confidence: float | None = None


class Source(BaseModel):
    document_id: int
    filename: str
    page: int
    score: float
    snippet: str


class ChatIn(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    conversation_id: int | None = None
    document_ids: list[int] | None = None


class ChatOut(BaseModel):
    conversation_id: int
    answer: str
    sources: list[Source]


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    content: str
    sources: list | None = None
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    document_ids: list | None = None
    created_at: datetime


class SearchIn(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    document_ids: list[int] | None = None
    limit: int = Field(default=10, ge=1, le=30)


class CompareIn(BaseModel):
    document_a: int
    document_b: int
    focus: str | None = None
