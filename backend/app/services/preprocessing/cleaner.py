import re
import unicodedata

_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w)")
_MULTI_NL = re.compile(r"\n{3,}")
_MULTI_SP = re.compile(r"[ \t\u00a0]{2,}")
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _CTRL.sub("", text)
    text = _HYPHEN_BREAK.sub(r"\1\2", text)      # kata terpotong di akhir baris
    text = re.sub(r"(?<![\.\:\!\?\n])\n(?!\n|[-•\d])", " ", text)  # gabung baris dalam paragraf
    text = _MULTI_SP.sub(" ", text)
    text = _MULTI_NL.sub("\n\n", text)
    return text.strip()
