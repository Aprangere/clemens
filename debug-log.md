---
class: projet
type: fleeting
projet: "[[ClemENS]]"
---
← [[ClemENS]]

# Debug Log — ClemENS

---

## [2026-04-30] PDFs ingérés en binaire brut — chatbot illisible

### Symptôme
Réponses du chatbot incohérentes. Les sources affichées dans l'UI montrent du garbage : `OA��aA�,OA��aA�,...` au lieu de texte. Le chatbot dit "je ne trouve pas" même pour des sujets couverts (thurnage, départements ENS).

### Diagnostic initial (incorrect)
Hypothèse : `pypdf` ne sait pas extraire le texte de certains PDFs (scannés ou encodage custom).

### Diagnostic réel
`SimpleDirectoryReader` de LlamaIndex lisait les PDFs comme des **fichiers texte bruts** au lieu d'utiliser le reader PDF. Chaque PDF était ingéré comme un seul chunk de ~300k chars contenant le binaire brut du fichier (`%PDF-1.5\n%\n1797 0 obj...`). `pypdf` n'était pas utilisé du tout.

Confirmation :
```python
docs = SimpleDirectoryReader(input_files=['AG_TG.pdf']).load_data()
# → 1 chunk, 320 521 chars, extrait: '%PDF-1.5\n%\n1797 0 obj...'
```

Cause probable : `llama-index-readers-file` (reader PDF de LlamaIndex) non installé ou non enregistré, provoquant un fallback en lecture texte brut.

### Fix appliqué
Remplacement de `SimpleDirectoryReader` par une extraction directe avec **`pymupdf` (`fitz`)** page par page :
- Extraction texte propre par page
- Filtre qualité : pages avec < 50% de caractères imprimables ignorées
- Métadonnées enrichies : `file_name`, `title`, `page`, `source`

```python
# ingest.py — nouvelle approche
import fitz
pdf = fitz.open(path)
for page in pdf:
    text = page.get_text("text").strip()
    if is_readable(text):
        documents.append(Document(text=text, metadata={...}))
```

### Résolution
ChromaDB vidé, réingestion complète avec le nouveau `ingest.py`.

**Résultat :** 2477 pages lisibles extraites sur 148 PDFs. 14 fichiers ignorés — ce sont les arrêtés officiels (PDFs scannés/images sans texte extractible). Ces 14 fichiers nécessitent OCR pour être ingérés (hors scope POC).

---

## [2026-04-30] Encodage Windows (cp1252) — crash scraper

### Symptôme
`scrape_sources.py` crashait à la fin avec `UnicodeEncodeError: 'charmap' codec can't encode character` au moment d'afficher les résultats.

### Cause
`sys.stdout` sur Windows utilise cp1252 par défaut, qui ne supporte pas les caractères accentués français ni les caractères Unicode de box-drawing (`─`).

### Fix appliqué
1. `sys.stdout.reconfigure(encoding="utf-8")` en tête de script
2. Remplacement du séparateur `"─" * 60` par `"-" * 60`
3. Écriture dans `Data.md` placée **avant** les `print()` pour garantir l'écriture même si l'affichage crash

---

## [2026-04-30] Mauvais environnement Python — ModuleNotFoundError

### Symptôme
`ingest.py` échoue avec `ModuleNotFoundError: No module named 'chromadb'` même après avoir utilisé `venv/Scripts/python.exe`.

### Cause
Les dépendances RAG (chromadb, llama-index, sentence-transformers...) sont installées sur le **Python 3.11 global** (`C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe`), pas dans le venv du projet (qui n'avait que `requests` et `beautifulsoup4`).

### Fix appliqué
Utiliser explicitement le Python global pour toutes les commandes RAG :
```bash
"C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe" ingest.py
```
Documenté dans `CLAUDE.md`.

---

## [2026-04-30] FAQs DG vides à l'ingestion web

### Symptôme
Les pages `dg.ens.fr/fr/faqs/` récupèrent très peu de contenu (225–430 chars) ou sont skippées entièrement.

### Cause
Le contenu des FAQs est probablement chargé dynamiquement en JavaScript. `requests` + `BeautifulSoup` ne rend pas le JS — seule la structure HTML statique est récupérée.

### Statut
Non résolu. Options futures :
- Utiliser `playwright` ou `selenium` pour rendre le JS
- Copier-coller manuellement le contenu des FAQs dans des fichiers `.txt` dans `app/data/`
- Ingestion manuelle depuis le navigateur

---

## [2026-04-30] ChromaDB verrouillé — impossible à supprimer

### Symptôme
`rm -rf chroma_db` échoue avec "Device or resource busy".

### Cause
L'app Streamlit (ou un processus Python) avait ChromaDB ouvert en écriture.

### Fix appliqué
Identifier et tuer les processus Python via PowerShell, puis supprimer :
```powershell
Get-Process | Where-Object { $_.Name -match "python" }
Stop-Process -Id <ids> -Force
Remove-Item -Recurse -Force chroma_db
```
