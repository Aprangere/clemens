import os

from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = "mistral-small-latest"

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMA_PATH = os.path.join(_BASE_DIR, "chroma_db")
CHROMA_COLLECTION = "clemens"

DATA_PATH = os.path.join(_BASE_DIR, "data")

TOP_K = 12
