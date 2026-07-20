---
class: projet
type: log
projet: "[[ClemENS]]"
domains:
  - "[[Intelligence Artificielle]]"
  - "[[Maths-Info]]"
date: 2026-04-30
---
← [[ClemENS]]

# Stratégie sources — Purge et récupération

## Problème identifié

La base ChromaDB contient 19 686 chunks dont une majorité de bruit : rapports de jury de concours, communiqués de presse, offres de stage, newsletters. Ce bruit dilue les bons documents et dégrade les réponses RAG.

**Règle générale** : mieux vaut 500 chunks pertinents que 20 000 chunks bruités.

---

## Purge immédiate

### Fichiers à supprimer de `app/data/` (339 / 686 PDFs)

| Catégorie | Volume | Exemples |
|---|---|---|
| Rapports de jury (AELM, AEGr, AELC) | ~277 | `AEGr_2008_rapport_jury.pdf` |
| Communiqués de presse + lettres d'info | ~41 | `LettreInfo_ENS_*.pdf`, `communique_*.pdf` |
| Sujets et offres de stage | ~21 | `Offre-XXXXX.pdf`, `sujetMaster*.pdf` |

**Procédure** :
1. Supprimer les fichiers identifiés de `app/data/`
2. Supprimer `app/chroma_db/` entièrement
3. Relancer `python app/ingest.py` (PDFs propres uniquement)
4. Relancer `python app/ingest_web.py` (pages DG seulement)

### Pages web à ne pas ré-ingérer

Supprimer de `WEB_SOURCES` dans `ingest_web.py` :
- Pages très courtes (< 500 chars) : bib infos pratiques, ENS normalien, étudiant-bac2...
- Pages génériques sans contenu actionnable

---

## Sources à ajouter manuellement

Pour les départements à couverture faible (bio, géo, littératures...), copier le contenu des pages de cours dans des fichiers `.txt` dans `app/data/`. `ingest.py` les ingère automatiquement.

Format recommandé : `[departement]_cours_[annee].txt`

---

## Stratégie long terme : meilleures sources

### 1. PDFs en priorité ✅
Le format le plus dense pour le RAG. À chercher sur chaque site de département :
- Brochure de formation / livret d'accueil
- Programme des cours annuel
- Guide du normalien / conscrit

### 2. Playwright (JS-rendered)
Pour les sites dont le contenu est chargé en JavaScript (FAQs DG, certains sites départements), BeautifulSoup ne récupère que la coquille HTML.

```python
# Installation
pip install playwright
playwright install chromium

# Usage minimal
from playwright.async_api import async_playwright

async def fetch_js_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        content = await page.inner_text("body")
        await browser.close()
        return content
```

**Candidats prioritaires** :
- `dg.ens.fr/fr/faqs/` — FAQs actuellement vides (JS)
- `dg.ens.fr/fr/reglement/` — vérifier si le contenu est complet

### 3. Sitemap crawl
Partir du `sitemap.xml` de chaque site donne une couverture exhaustive et structurée, contrairement au crawl par liens qui peut rater des sections.

```python
import requests
from bs4 import BeautifulSoup

def urls_from_sitemap(base_url):
    r = requests.get(f"{base_url}/sitemap.xml", timeout=10, verify=False)
    soup = BeautifulSoup(r.content, "xml")
    return [loc.text for loc in soup.find_all("loc")]
```

**Sites ENS avec sitemap probable** :
- `www.math.ens.psl.eu/sitemap.xml`
- `www.di.ens.fr/sitemap.xml`
- `www.geosciences.ens.fr/sitemap.xml`

### 4. Export Moodle / Intranet (post-CAS)
Une fois l'authentification CAS intégrée, exporter les ressources pédagogiques de Moodle et les documents de l'intranet. C'est là que se trouvent les vraies infos pour les étudiants.

### 5. Ingestion périodique
Mettre en place un cron pour ré-ingérer les sources web toutes les semaines ou tous les mois afin de garder la base à jour (nouvelles dates, nouveaux règlements).

---

## Critères de sélection des sources

**Garder** :
- Concerne directement la vie étudiante à l'ENS (internat, scolarité, services)
- Contient des procédures, règles, délais, contacts
- Brochures de formation avec liste de cours, conditions d'admission
- Documents officiels (règlements, chartes, guides)

**Virer** :
- Rapports de jury de concours (utiles aux futurs candidats, pas aux étudiants ENS)
- Communiqués de presse et actualités
- Publications de recherche, thèses
- Offres de stage et d'emploi (trop volatiles, nécessitent une MAJ fréquente)
- Pages vitrine sans contenu actionnable (< 300 chars)
