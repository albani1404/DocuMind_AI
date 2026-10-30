"""OCR dengan PaddleOCR (dimuat lazy karena berat)."""
from functools import lru_cache
import io
import logging
import numpy as np
from PIL import Image
from app.core.config import get_settings

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _engine():
    from paddleocr import PaddleOCR
    return PaddleOCR(use_angle_cls=True, lang=get_settings().ocr_lang, show_log=False)


def ocr_image_bytes(data: bytes) -> tuple[str, float | None]:
    """Return (teks, rata-rata confidence 0..1)."""
    img = np.array(Image.open(io.BytesIO(data)).convert("RGB"))
    result = _engine().ocr(img, cls=True)
    lines, confs = [], []
    for page in result or []:
        for item in page or []:
            text, conf = item[1]
            lines.append(text); confs.append(float(conf))
    return "\n".join(lines), (sum(confs) / len(confs) if confs else None)
