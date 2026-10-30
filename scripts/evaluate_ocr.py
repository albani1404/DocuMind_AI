"""Evaluasi OCR: Character Error Rate (CER).
Folder berisi pasangan gambar + file .txt ground truth bernama sama.
Jalankan: python scripts/evaluate_ocr.py data/ocr_eval   (dari root repo)"""
import sys
from pathlib import Path
sys.path.insert(0, "backend")
from app.services.ocr.paddle_ocr import ocr_image_bytes


def edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


total_err = total_len = 0
for img in sorted(Path(sys.argv[1]).glob("*.[jp][pn]g")):
    gt = img.with_suffix(".txt")
    if not gt.exists():
        continue
    pred, _ = ocr_image_bytes(img.read_bytes())
    ref = " ".join(gt.read_text(encoding="utf-8").split()); pred = " ".join(pred.split())
    e = edit_distance(pred, ref); total_err += e; total_len += len(ref)
    print(f"{img.name}: CER {e / max(len(ref), 1):.3f}")
print(f"CER total: {total_err / max(total_len, 1):.3f}")
