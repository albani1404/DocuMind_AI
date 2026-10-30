"""Evaluasi retrieval: Hit@K dan MRR.
Format file JSON: [{"question": "...", "document_id": 1, "page": 4}, ...]
Jalankan: python scripts/evaluate_retrieval.py eval.json --owner 1 -k 5   (dari root repo)"""
import argparse, json, sys
sys.path.insert(0, "backend")
from app.services.retrieval.retriever import retrieve
from app.services.reranking.reranker import rerank

ap = argparse.ArgumentParser()
ap.add_argument("file"); ap.add_argument("--owner", type=int, required=True); ap.add_argument("-k", type=int, default=5)
a = ap.parse_args()
cases = json.load(open(a.file, encoding="utf-8"))
hits, rr = 0, 0.0
for c in cases:
    top = rerank(c["question"], retrieve(c["question"], a.owner, [c["document_id"]], 20), a.k)
    rank = next((i for i, t in enumerate(top, 1) if t["document_id"] == c["document_id"] and t["page"] == c["page"]), None)
    hits += rank is not None; rr += 1 / rank if rank else 0
n = len(cases) or 1
print(f"Kasus: {n} | Hit@{a.k}: {hits / n:.3f} | MRR: {rr / n:.3f}")
