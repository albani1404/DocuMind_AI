import os
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")

print("========== GEMINI CONFIGURATION ==========")
print("API Key ditemukan:", api_key is not None)
print("API Key kosong:", not bool(api_key and api_key.strip()))
print("Panjang API Key:", len(api_key.strip()) if api_key else 0)
print("Ada spasi di awal:", api_key.startswith(" ") if api_key else False)
print("Ada spasi di akhir:", api_key.endswith(" ") if api_key else False)
print("==========================================")