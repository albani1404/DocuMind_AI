import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.services.chunking.chunker import chunk_pages
from app.services.preprocessing.cleaner import clean_text
from app.main import app


def test_clean_text_joins_hyphenation():
    assert "keamanan" in clean_text("kea-\nmanan cloud")


def test_chunker_keeps_page_numbers():
    pages = [(1, "Kalimat satu. " * 80), (2, "Halaman dua isi. " * 80)]
    chunks = chunk_pages(pages, size=300, overlap=50)
    assert {c.page for c in chunks} == {1, 2}
    assert all(len(c.text) <= 400 for c in chunks)


def test_auth_and_upload_validation():
    with TestClient(app) as c:
        assert c.get("/health").json()["status"] == "ok"
        r = c.post("/api/auth/register", json={"email": "t@x.id", "name": "Tester", "password": "rahasia123"})
        assert r.status_code in (201, 409)
        tok = c.post("/api/auth/login", json={"email": "t@x.id", "password": "rahasia123"}).json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        bad = c.post("/api/documents", files={"file": ("a.exe", b"MZ", "application/octet-stream")}, headers=h)
        assert bad.status_code == 415
        fake = c.post("/api/documents", files={"file": ("a.pdf", b"bukan pdf", "application/pdf")}, headers=h)
        assert fake.status_code == 400
        assert c.get("/api/documents").status_code == 401
