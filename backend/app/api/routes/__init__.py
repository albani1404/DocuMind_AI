from fastapi import APIRouter
from app.api.routes import auth, documents, chat, search, ai

api_router = APIRouter(prefix="/api")
for r in (auth.router, documents.router, chat.router, search.router, ai.router):
    api_router.include_router(r)
