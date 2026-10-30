from functools import lru_cache
from app.core.config import get_settings


class LLMNotConfigured(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _client():
    key = get_settings().gemini_api_key
    if not key:
        raise LLMNotConfigured("GEMINI_API_KEY belum diisi di file .env")
    from google import genai
    return genai.Client(api_key=key)


def generate(prompt: str, system: str | None = None, temperature: float = 0.2, json_mode: bool = False) -> str:
    from google.genai import types
    cfg = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        response_mime_type="application/json" if json_mode else None,
    )
    resp = _client().models.generate_content(model=get_settings().gemini_model, contents=prompt, config=cfg)
    return (resp.text or "").strip()
