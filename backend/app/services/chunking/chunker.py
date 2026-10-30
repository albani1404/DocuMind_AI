"""Chunking sadar-halaman: setiap chunk mempertahankan nomor halaman asalnya."""
from dataclasses import dataclass
import re

_SENT = re.compile(r"(?<=[\.\!\?])\s+|\n{2,}")


@dataclass
class Chunk:
    page: int
    index: int
    text: str


def _split_units(text: str, size: int) -> list[str]:
    units: list[str] = []
    for part in _SENT.split(text):
        part = part.strip()
        if not part:
            continue
        while len(part) > size:       # kalimat sangat panjang
            units.append(part[:size]); part = part[size:]
        units.append(part)
    return units


def chunk_pages(pages: list[tuple[int, str]], size: int = 900, overlap: int = 150) -> list[Chunk]:
    chunks: list[Chunk] = []
    idx = 0
    for page_no, text in pages:
        buf = ""
        for u in _split_units(text, size):
            if buf and len(buf) + len(u) + 1 > size:
                chunks.append(Chunk(page_no, idx, buf)); idx += 1
                tail = buf[-overlap:] if overlap else ""
                buf = (tail.split(" ", 1)[-1] + " " + u).strip() if tail else u
            else:
                buf = f"{buf} {u}".strip()
        if len(buf) >= 20:
            chunks.append(Chunk(page_no, idx, buf)); idx += 1
    return chunks
