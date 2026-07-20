---
class: ai
type: instructions
projet: "[[ClemENS]]"
---

# ClemENS — Instructions Claude Code

## Vue d'ensemble

ClemENS est un chatbot RAG (Retrieval-Augmented Generation) pour aider étudiants et personnel de l'ENS Ulm à naviguer les informations administratives. Objectif immédiat : **proof of concept** à présenter à la direction.

## Environnement

- **Python** : Python 3.11 global (`C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe`)
- **Ne pas utiliser le venv** — les dépendances RAG sont sur le Python global, le venv n'a que requests/bs4
- **Fichier principal** : `app/main.py` — lancer avec `streamlit run app/main.py` depuis la racine

## Structure

```
ClemENS/
  app/
    main.py            ← app Streamlit (fichier principal)
    config.py          ← chemins, modèles, clés API (TOP_K=12)
    rag.py             ← pipeline RAG (LlamaIndex + ChromaDB + Mistral)
    ingest.py          ← ingestion PDFs + TXTs → ChromaDB
    ingest_web.py      ← ingestion pages HTML → ChromaDB
    scrape_sources.py  ← crawl ENS, seeds depuis Data.md
    data/              ← PDFs et TXTs à ingérer (ne pas committer les scannés)
    chroma_db/         ← base vectorielle (ne pas committer)
    assets/            ← logos (clemens5upgrade.png, logo-ens-transparent.png...)
    .env               ← MISTRAL_API_KEY (ne pas committer)
    .streamlit/
      config.toml      ← thème ENS (primaryColor bordeaux)
  .streamlit/
    config.toml        ← même config à la racine (Streamlit cherche ici)
  Data.md              ← inventaire sources
  debug-sources.md     ← diagnostic couverture par département
  meilleures-sources.md ← stratégie sources (Playwright, sitemap, CAS...)
  clemens-vs-notebooklm.md ← comparaison avec NotebookLM
```

## Stack

| Couche | Choix |
|---|---|
| LLM | Mistral API (`mistral-small-latest`) via OpenAILike |
| Embeddings | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (local) |
| Vector store | ChromaDB (local, persistant) |
| RAG framework | LlamaIndex |
| UI | Streamlit |
| Scraping | BeautifulSoup + requests (verify=False pour SSL Windows) |

## Commandes clés

```bash
# Lancer l'app
streamlit run app/main.py

# Ingestion (PDFs + TXTs dans app/data/)
python app/ingest.py

# Ingestion pages web (WEB_SOURCES dans ingest_web.py)
python app/ingest_web.py

# Scraping DG uniquement + téléchargement PDFs
python app/scrape_sources.py --dg-only --download

# Scraping départements (seeds depuis Data.md, skip DG+ENS déjà faits)
python app/scrape_sources.py --dept-only --download --update

# Repartir de zéro
rm -rf app/chroma_db
```

## Sources actuelles dans app/data/

**PDFs DG (11 fichiers)** — vie internat, thurnage, logement, règles cuisines :
- `Manuel_conscrits_vie_internat_2022_FR/EN.pdf` ← clé
- `infos_rentree_conscrits_FR/EN.pdf` ← clé
- `livretTG-1.pdf`
- `Commission_logement.pdf`, `Rapport_acces_logement.pdf`
- `Tri_sélectif_cuisines_FR/EN.pdf`, `etiquette_malle_FR/EN.pdf`
- `PresentationAGTG2026.pdf` ← référence à jour sur la réforme thurnage/UDG

> Retirés le 2026-07-20 (contenu obsolète, réforme périmée) : `Thurnage_Blanc_recap.pdf`, `DS_réforme_sociale_du_thurnage.pdf`, `Synthèse_réforme_thurnage.pdf`, `Documents_réforme_UDG.pdf`

**Notice concours** :
- `notice_interens_2026.pdf`

**Contacts** (TXT ingéré) :
- `contacts_ressources_ENS.txt` ← URLs et contacts de tous les départements

**À ajouter manuellement** (guides doctorant, RGPD, brochures départements) :
- Déposer dans `app/data/` puis relancer `python app/ingest.py`
- Les `.txt` sont aussi supportés (pour contenu CAS ou copié-collé)

## Pages web ingérées (WEB_SOURCES)

- DG règlements FR : intérieur, thurnage, parking, casiers, panneaux, malles, délégations, modération, sysadmins, annexes
- DG règlements EN : intérieur, thurnage
- ENS principal : admissions, formations, départements, carrières, campus, contact, santé, VSS
- Bibliothèque : accueil, contacts, formations, ressources électroniques
- Départements : Antiquité, Histoire, Maths, Physique, Géosciences, DI, Chimie, Arts, Économie, Cognitives, Bio, Philo, Sciences sociales, Géo, Littératures, CERES, ECLA, CIENS

FAQs DG : JS-rendues → contenu vide. À ingérer manuellement en `.txt`.

## RGPD

Mistral API avec DPA (entreprise FR, hébergement EU, données non utilisées pour entraînement). Voir `RGPD-conformite.md`.

## Règles

- Ne jamais committer `chroma_db/` ni `.env`
- Les ingestions sont **cumulatives** — pour repartir de zéro : `rm -rf app/chroma_db`
- `ingest.py` lit les `.pdf` ET les `.txt` dans `app/data/`
- TOP_K = 12 (ajusté après problèmes de bruit avec TOP_K=5)
