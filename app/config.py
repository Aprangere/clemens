import os

from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

if not MISTRAL_API_KEY:
    # Sur Streamlit Cloud, les secrets ne sont pas toujours exposés comme
    # variables d'environnement — repli sur st.secrets. Le try/except couvre
    # les scripts CLI (ingest.py, scrape_sources.py...) qui tournent hors
    # contexte Streamlit et où st.secrets n'est pas disponible.
    try:
        import streamlit as st
        MISTRAL_API_KEY = st.secrets.get("MISTRAL_API_KEY", "")
    except Exception:
        pass
MISTRAL_MODEL = "mistral-small-latest"

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMA_PATH = os.path.join(_BASE_DIR, "chroma_db")
CHROMA_COLLECTION = "clemens"

DATA_PATH = os.path.join(_BASE_DIR, "data")

TOP_K = 12
