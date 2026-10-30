from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.database.session import get_db
from app.models import User
from app.repositories import UserRepo

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login-form")


def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    uid = decode_token(token)
    user = UserRepo(db).get(uid) if uid else None
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token tidak valid atau kedaluwarsa",
                            headers={"WWW-Authenticate": "Bearer"})
    return user
