import sys
sys.path.insert(0, "app")
import chromadb
from config import CHROMA_PATH, CHROMA_COLLECTION

client = chromadb.PersistentClient(path=CHROMA_PATH)
col = client.get_collection(CHROMA_COLLECTION)
print(f"Total chunks : {col.count()}")

# Chunks biologie
results = col.query(
    query_texts=["cours biologie departement enseignement"],
    n_results=8,
    include=["documents", "metadatas"],
)
print("\n=== Chunks biologie ===")
for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
    src = meta.get("title") or meta.get("file_name") or meta.get("source") or "?"
    print(f"[{i+1}] {src}")
    print(f"     {doc[:250]}\n")

# Chunks avec source bio
all_bio = col.get(where={"source": {"$contains": "bio"}}, include=["metadatas"], limit=20)
print(f"\n=== Sources contenant 'bio' : {len(all_bio['ids'])} chunks ===")
seen = set()
for m in all_bio["metadatas"]:
    src = m.get("source") or m.get("file_name") or "?"
    if src not in seen:
        print(f"  {src}")
        seen.add(src)
