import json
import re
from app.services.llm.gemini import generate

SYSTEM = "Kamu mengekstrak informasi terstruktur dari dokumen. Keluarkan JSON valid saja, tanpa penjelasan."
SCHEMA = """{
  "title": string|null, "document_type": string|null, "language": string|null,
  "authors": [string], "organizations": [string], "dates": [{"label": string, "value": string}],
  "people": [string], "locations": [string], "monetary_values": [{"label": string, "value": string}],
  "keywords": [string], "key_facts": [string], "action_items": [string]
}"""


def extract_information(pages: list[tuple[int, str]]) -> dict:
    text = "\n\n".join(f"[Halaman {n}]\n{t}" for n, t in pages)[:50_000]
    prompt = f"Ekstrak informasi dari dokumen berikut sesuai skema JSON ini (isi null/[] bila tidak ada):\n{SCHEMA}\n\nDokumen:\n{text}"
    raw = generate(prompt, system=SYSTEM, json_mode=True)
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw, "error": "Output LLM bukan JSON valid"}
