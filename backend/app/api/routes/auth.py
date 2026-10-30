from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.database.session import get_db
from app.repositories import UserRepo
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _token(user) -> TokenOut:
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/register", response_model=TokenOut, status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    repo = UserRepo(db)
    if repo.by_email(body.email):
        raise HTTPException(409, "Email sudah terdaftar")
    return _token(repo.create(body.email, body.name, hash_password(body.password)))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = UserRepo(db).by_email(body.email)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Email atau kata sandi salah")
    return _token(user)


@router.post("/login-form", response_model=TokenOut, include_in_schema=False)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return login(LoginIn(email=form.username, password=form.password), db)


@router.get("/me", response_model=UserOut)
def me(user=Depends(current_user)):
    return user
