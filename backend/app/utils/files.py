import re
import uuid
from pathlib import Path

MAGIC = {"pdf": [b"%PDF"], "docx": [b"PK\x03\x04"], "png": [b"\x89PNG"], "jpg": [b"\xff\xd8\xff"], "jpeg": [b"\xff\xd8\xff"]}


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._\- ]", "_", Path(name).name)[:200] or "dokumen"


def unique_path(dir_: str, ext: str) -> Path:
    return Path(dir_) / f"{uuid.uuid4().hex}.{ext}"


def magic_ok(ext: str, head: bytes) -> bool:
    return any(head.startswith(m) for m in MAGIC.get(ext, []))
