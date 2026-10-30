"""Buat akun demo: python scripts/seed_database.py  (jalankan dari folder backend/)"""
import sys
sys.path.insert(0, "backend")
from app.core.security import hash_password
from app.database.session import SessionLocal, init_db
from app.repositories import UserRepo

init_db()
with SessionLocal() as db:
    repo = UserRepo(db)
    if not repo.by_email("demo@documind.ai"):
        repo.create("demo@documind.ai", "Demo User", hash_password("demo12345"))
        print("Akun dibuat: demo@documind.ai / demo12345")
    else:
        print("Akun demo sudah ada")
