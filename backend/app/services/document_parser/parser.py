"""Ekstraksi teks per halaman dari PDF, DOCX, dan gambar (via OCR)."""
from dataclasses import dataclass
from pathlib import Path
import logging

log = logging.getLogger(__name__)
MIN_CHARS_PER_PAGE = 30  # di bawah ini halaman PDF dianggap hasil scan -> OCR


@dataclass
class PageText:
    page_number: int
    text: str
    ocr_confidence: float | None = None
    used_ocr: bool = False


def parse_pdf(path: Path) -> list[PageText]:
    import fitz  # PyMuPDF
    from app.services.ocr.paddle_ocr import ocr_image_bytes

    pages: list[PageText] = []
    with fitz.open(path) as pdf:
        for i, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if len(text) >= MIN_CHARS_PER_PAGE:
                pages.append(PageText(i, text))
                continue
            # halaman scan: render lalu OCR
            pix = page.get_pixmap(dpi=200)
            ocr_text, conf = ocr_image_bytes(pix.tobytes("png"))
            pages.append(PageText(i, ocr_text, conf, used_ocr=True))
    return pages


def parse_docx(path: Path) -> list[PageText]:
    """DOCX tidak punya konsep halaman tetap; kita kelompokkan per ~3000 karakter
    sebagai 'halaman virtual' agar sitasi tetap bermakna."""
    from docx import Document

    doc = Document(str(path))
    blocks = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                blocks.append(" | ".join(cells))
    pages, buf, n = [], [], 0
    for b in blocks:
        buf.append(b); n += len(b)
        if n >= 3000:
            pages.append("\n".join(buf)); buf, n = [], 0
    if buf:
        pages.append("\n".join(buf))
    return [PageText(i, t) for i, t in enumerate(pages, start=1)]


def parse_image(path: Path) -> list[PageText]:
    from app.services.ocr.paddle_ocr import ocr_image_bytes

    text, conf = ocr_image_bytes(path.read_bytes())
    return [PageText(1, text, conf, used_ocr=True)]


def parse_document(path: Path, ext: str) -> list[PageText]:
    ext = ext.lower().lstrip(".")
    if ext == "pdf":
        return parse_pdf(path)
    if ext == "docx":
        return parse_docx(path)
    if ext in {"jpg", "jpeg", "png"}:
        return parse_image(path)
    raise ValueError(f"Tipe file tidak didukung: {ext}")
