import argparse
import sys
from pathlib import Path

import chromadb
import fitz  # pymupdf
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import CHROMA_COLLECTION, CHROMA_PATH, DATA_PATH, EMBED_MODEL

sys.stdout.reconfigure(encoding="utf-8")

POC_PDFS = [
    "Manuel_conscrits_vie_internat_2022_FR.pdf",
    "infos_rentree_conscrits.pdf",
    "notice_interens_2026_mise_en_ligne_vf260212-1.pdf",
    "ens_guide_doctorant_2025_2026.pdf",
    "guide_du_doctorant_contractuel_2024-25.pdf",
    "notice_rgpd_etudiants_ens-psl.pdf",
    "constitution-1958-vingt-cinquieme-revision.pdf",
]

MIN_TEXT_RATIO = 0.5  # minimum ratio of printable chars to keep a page


def is_readable(text: str) -> bool:
    if not text or len(text) < 50:
        return False
    printable = sum(1 for c in text if c.isprintable() or c in "\n\t")
    return (printable / len(text)) >= MIN_TEXT_RATIO


def extract_pdf(path: Path) -> list[Document]:
    docs = []
    try:
        pdf = fitz.open(str(path))
        for i, page in enumerate(pdf):
            text = page.get_text("text").strip()
            if not is_readable(text):
                continue
            docs.append(Document(
                text=text,
                metadata={
                    "file_name": path.name,
                    "title": path.stem.replace("_", " ").replace("%C3%A9", "e"),
                    "page": i + 1,
                    "source": path.name,
                },
            ))
        pdf.close()
    except Exception as e:
        print(f"  ERR  {path.name} — {e}")
    return docs


def ingest(poc: bool = False):
    data_path = Path(DATA_PATH)

    if poc:
        files = [data_path / f for f in POC_PDFS if (data_path / f).exists()]
        missing = [f for f in POC_PDFS if not (data_path / f).exists()]
        if missing:
            print(f"Avertissement — introuvables : {missing}")
        print(f"Mode POC — {len(files)} PDF(s) sélectionnés.")
    else:
        files = sorted(data_path.glob("*.pdf")) + sorted(data_path.glob("*.txt"))
        print(f"Mode complet — {len(files)} fichiers trouvés.")

    documents = []
    skipped = 0
    for f in files:
        if f.suffix == ".txt":
            text = f.read_text(encoding="utf-8", errors="ignore").strip()
            if text:
                documents.append(Document(
                    text=text,
                    metadata={"file_name": f.name, "title": f.stem.replace("_", " "), "source": f.name},
                ))
                print(f"  TXT  {f.name} ({len(text)} chars)")
            continue
        pages = extract_pdf(f)
        if pages:
            documents.extend(pages)
        else:
            skipped += 1
            print(f"  SKIP {f.name} (contenu illisible)")

    print(f"\n{len(documents)} pages lisibles extraites ({skipped} fichiers ignorés).")

    if not documents:
        print("Aucun document à ingérer.")
        return

    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    chroma_collection = chroma_client.get_or_create_collection(CHROMA_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

    print("Génération des embeddings...")
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )
    print("Ingestion terminée.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--poc", action="store_true", help="Sélection POC uniquement")
    args = parser.parse_args()
    ingest(poc=args.poc)
