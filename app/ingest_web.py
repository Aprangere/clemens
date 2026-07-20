"""
Ingest HTML pages (DG règlements, FAQs, departement sites) into ChromaDB.

Usage:
    python ingest_web.py                   # ingest all URLs in WEB_SOURCES
    python ingest_web.py --url <url>       # ingest a single URL
    python ingest_web.py --dry-run         # show what would be ingested, no write
"""

import argparse
import json
import sys
import time
from urllib.parse import urlparse

import chromadb
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import CHROMA_COLLECTION, CHROMA_PATH, EMBED_MODEL, MISTRAL_API_KEY

sys.stdout.reconfigure(encoding="utf-8")

# ── Sources HTML à ingérer ─────────────────────────────────────────────────────

POC_WEB_SOURCES = [
    "https://www.dg.ens.fr/fr/reglement/interieur/",
    "https://www.dg.ens.fr/fr/faqs/delegation-generale/",
    "https://www.dg.ens.fr/fr/faqs/info-pratiques/",
    "https://www.dg.ens.fr/fr/faqs/internat/",
    "https://www.dg.ens.fr/fr/faqs/la-rentr%C3%A9e/",
    "https://www.ens.psl.eu/contact",
    "https://www.ens.psl.eu/des-campus-au-coeur-de-paris/vie-de-campus",
]

WEB_SOURCES = [
    # ── DG — Règlements ───────────────────────────────────────────────────────
    "https://www.dg.ens.fr/fr/reglement/interieur/",
    "https://www.dg.ens.fr/fr/reglement/thurnage/",
    "https://www.dg.ens.fr/fr/reglement/parking/",
    "https://www.dg.ens.fr/fr/reglement/casiers/",
    "https://www.dg.ens.fr/fr/reglement/panneaux/",
    "https://www.dg.ens.fr/fr/reglement/malles/",
    "https://www.dg.ens.fr/fr/reglement/delegations/",
    "https://www.dg.ens.fr/fr/reglement/moderation/",
    "https://www.dg.ens.fr/fr/reglement/sysadmins/",
    "https://www.dg.ens.fr/fr/reglement/annexe-pour-les-exthurnes/",
    "https://www.dg.ens.fr/fr/reglement/annexe-pour-les-couloirs-dits-calmes/",
    # ── DG — Règlements EN ────────────────────────────────────────────────────
    "https://www.dg.ens.fr/en/reglement/",
    "https://www.dg.ens.fr/en/reglement/interieur/",
    "https://www.dg.ens.fr/en/reglement/thurnage/",
    # appendix-for-exthurnes/ et appendix-for-quiet-corridors/ retirées (404, pages disparues)
    # FAQs DG : JS-rendues, contenu vide — à ingérer manuellement en .txt si besoin
    # ── ENS principal ─────────────────────────────────────────────────────────
    "https://www.ens.psl.eu/une-formation-d-exception/admission-concours",
    "https://www.ens.psl.eu/une-formation-d-exception/admission-concours/textes-officiels",
    "https://www.ens.psl.eu/une-formation-d-exception/formations",
    "https://www.ens.psl.eu/une-formation-d-exception/departements",
    "https://www.ens.psl.eu/departement/departement-d-informatique",
    "https://www.ens.psl.eu/une-formation-d-exception/carrieres",
    "https://www.ens.psl.eu/une-formation-d-exception/un-concours-et-apres",
    "https://www.ens.psl.eu/etudiant-bac2-et-cpge",
    "https://www.ens.psl.eu/etudiant-bac3",
    "https://www.ens.psl.eu/etudiant-bac-5",
    "https://www.ens.psl.eu/etudiant-international",
    "https://www.ens.psl.eu/normalien",
    "https://www.ens.psl.eu/des-campus-au-coeur-de-paris/sante-et-handicap-l-ens-mobilisee",
    "https://www.ens.psl.eu/des-campus-au-coeur-de-paris/lutte-contre-les-discriminations-le-harcelement-et-les-violences",
    "https://www.ens.psl.eu/des-campus-au-coeur-de-paris/vie-de-campus",
    "https://www.ens.psl.eu/des-campus-au-coeur-de-paris/vie-associative-culturelle-et-sportive",
    "https://www.ens.psl.eu/contact",
    "https://www.ens.psl.eu/recrutement/recrutement-par-concours",
    # ── Bibliothèque ──────────────────────────────────────────────────────────
    "https://bib.ens.psl.eu/accueil",
    "https://bib.ens.psl.eu/informations-pratiques",
    "https://bib.ens.psl.eu/formations",
    "https://bib.ens.psl.eu/contacts",
    "https://bib.ens.psl.eu/ulm-lsh-jourdan-shs/collections/ressources-electroniques",
    "https://bib.ens.psl.eu/centre-documentaire-du-caphes",
    "https://bib.ens.psl.eu/mathematiques-et-informatique",
    # ── Antiquité ─────────────────────────────────────────────────────────────
    "https://antiquite.ens.psl.eu/",
    "https://antiquite.ens.psl.eu/category/master/",
    "https://antiquite.ens.psl.eu/presentation-du-master-humanites/",
    "https://antiquite.ens.psl.eu/cours-agregations-de-lettres-classiques-et-de-grammaire/",
    "https://antiquite.ens.psl.eu/cours-agregation-de-lettres-modernes/",
    "https://antiquite.ens.psl.eu/stages/",
    "https://antiquite.ens.psl.eu/bibliotheque-ressources-electroniques-antiquite-grec-latin/",
    "https://antiquite.ens.psl.eu/agregation-de-grammaire-cours-de-linguistique/",
    "https://antiquite.ens.psl.eu/cours-initiation-et-approfondissement-antiquites-numeriques/",
    "https://antiquite.ens.psl.eu/cours-initiation-et-approfondissement-en-epigraphie/",
    "https://antiquite.ens.psl.eu/cours-initiation-et-approfondissement-en-grec/",
    "https://antiquite.ens.psl.eu/cours-initiation-et-approfondissement-en-histoire-et-archeologie-antiquite/",
    "https://antiquite.ens.psl.eu/cours-initiation-et-approfondissement-en-latin/",
    "https://antiquite.ens.psl.eu/cours-initiation-et-approfondissement-en-linguistique/",
    "https://antiquite.ens.psl.eu/programmes-stages-de-recherche/",
    # ── Histoire ──────────────────────────────────────────────────────────────
    "https://histoire.ens.psl.eu/-accueil-2-.html",
    "https://histoire.ens.psl.eu/-cours-et-seminaires-3-.html",
    "https://histoire.ens.psl.eu/-master-.html",
    "https://histoire.ens.psl.eu/-international-.html",
    "https://histoire.ens.psl.eu/-informations-pratiques-258-.html",
    "https://histoire.ens.psl.eu/contact-140.html",
    # ── Mathématiques (DMA) ───────────────────────────────────────────────────
    "https://www.math.ens.psl.eu/lenseignement/",
    "https://www.math.ens.psl.eu/lenseignement/formations/",
    "https://www.math.ens.psl.eu/lenseignement/formations/1ere-annee/",
    "https://www.math.ens.psl.eu/lenseignement/formations/deuxieme-annee/",
    "https://www.math.ens.psl.eu/lenseignement/formations/3eme-et-4eme-annees/",
    "https://www.math.ens.psl.eu/lenseignement/etudier-au-dma/",
    "https://www.math.ens.psl.eu/lenseignement/etudier-au-dma/concours-entree-ens/",
    "https://www.math.ens.psl.eu/lenseignement/etudier-au-dma/concours-normalien-etudiant/",
    "https://www.math.ens.psl.eu/lenseignement/etudier-au-dma/selection-internationale/",
    "https://www.math.ens.psl.eu/lenseignement/etudier-au-dma/relations-internationales/",
    "https://www.math.ens.psl.eu/lenseignement/etudier-au-dma/bourse-olympique/",
    "https://www.math.ens.psl.eu/lenseignement/annales-dexamen/",
    "https://www.math.ens.psl.eu/lenseignement/edt/",
    "https://www.math.ens.psl.eu/lenseignement/feuilles-de-td-et-tp/",
    "https://www.math.ens.psl.eu/lenseignement/polycopies-de-cours/",
    "https://www.math.ens.psl.eu/lenseignement/presentation-de-la-formation/",
    "https://www.math.ens.psl.eu/lenseignement/responsabilites-pedagogiques/",
    "https://www.math.ens.psl.eu/lenseignement/stages-exposes/",
    "https://www.math.ens.psl.eu/lenseignement/liste-de-m2-en-region-parisienne-accueillant-des-normaliens/",
    "https://www.math.ens.psl.eu/lenseignement/formations/mathematiques-pour-toutes/",
    "https://www.math.ens.psl.eu/lenseignement/formations/3eme-et-4eme-annees/cours-de-m2/",
    "https://www.math.ens.psl.eu/brochure-enseignement/",
    "https://www.math.ens.psl.eu/le-departement/administration-et-responsabilites/",
    "https://www.math.ens.psl.eu/bibliotheque/conditions-d-inscription/",
    "https://www.math.ens.psl.eu/contact/",
    "https://www.math.ens.psl.eu/contact/venir-au-secretariat-pedagogique/",
    "https://www.math.ens.psl.eu/bibliotheque/",
    "https://www.math.ens.psl.eu/bibliotheque/services/",
    "https://www.math.ens.psl.eu/concours-normalien-etudiant/",
    # ── Physique ──────────────────────────────────────────────────────────────
    "http://www.phys.ens.fr/fr/cours",
    "http://www.phys.ens.fr/fr/formations/licence-3",
    "http://www.phys.ens.fr/fr/formations/m1-icfp",
    "http://www.phys.ens.fr/fr/formations/m2-icfp",
    "http://www.phys.ens.fr/fr/formations/master-icfp",
    "http://www.phys.ens.fr/fr/formations/agregation-de-physique",
    "http://www.phys.ens.fr/fr/formations/diplome-ens",
    "http://www.phys.ens.fr/fr/article/lenseignement-de-la-physique-lens",
    "http://www.phys.ens.fr/fr/article/etre-candidat-en-master",
    "http://www.phys.ens.fr/fr/article/livrets-daccueil-des-etudiants",
    "http://www.phys.ens.fr/fr/article/contacts-administratifsenseignement",
    "http://www.phys.ens.fr/fr/programme",
    "http://www.phys.ens.fr/fr/article/le-stage-experimental-un-mois-en-fin-de-l3",
    "http://www.phys.ens.fr/fr/article/selection-par-linternational-physics-olympiad",
    "http://www.phys.ens.fr/fr/form/contact",
    "http://www.phys.ens.fr/fr/formations/master-astronomie-astrophysique-et-ingenierie-spatiale",
    # Portail stages.phys.ens.psl.eu retiré — SPA JS, contenu vide en scraping statique
    # ── Géosciences ───────────────────────────────────────────────────────────
    "https://www.geosciences.ens.fr/enseignement",
    "https://www.geosciences.ens.fr/enseignement/diplome-de-lens",
    "https://www.geosciences.ens.fr/enseignement/offres-de-stages",
    "https://www.geosciences.ens.fr/master",
    "https://www.geosciences.ens.fr/admissions-et-bourses",
    "https://www.geosciences.ens.fr/departement/acces-contact",
    "https://www.geosciences.ens.fr/departement/services",
    "https://www.geosciences.ens.fr/recherche/seminaires",
    # ── Informatique (DI) ─────────────────────────────────────────────────────
    "https://www.di.ens.fr/",
    "https://www.di.ens.fr/information",
    "https://www.di.ens.fr/contact_web",
    # ── Chimie ────────────────────────────────────────────────────────────────
    "https://www.chimie.ens.fr/formation/",
    "https://www.chimie.ens.fr/recherche/",
    # ── Arts ──────────────────────────────────────────────────────────────────
    "https://arts.ens.psl.eu/",
    # ── Économie ──────────────────────────────────────────────────────────────
    "http://www.economie.ens.fr/",
    # ── Études cognitives ─────────────────────────────────────────────────────
    "http://www.cognition.ens.fr",
    "http://www.cognition.ens.fr/en/about-dec/presentation-636",
    "http://www.cognition.ens.fr/en/about-dec/administration-and-governance-638",
    "http://www.cognition.ens.fr/en/about-dec/contact-map-637",
    "http://www.cognition.ens.fr/en/about-dec/cellules-de-mediation-17222",
    "http://www.cognition.ens.fr/en/admissions-scholarships-14195",
    "http://www.cognition.ens.fr/en/teaching/courses-640",
    "http://www.cognition.ens.fr/en/teaching/common-facts-and-tips-your-dens-dec-15618",
    "http://www.cognition.ens.fr/en/teaching/ens-psl-international-graduate-program-655",
    # ── Biologie ──────────────────────────────────────────────────────────────
    "https://www.bio.ens.psl.eu/depbio/",
    "https://www.edu.bio.ens.psl.eu/",
    # ── Philosophie ───────────────────────────────────────────────────────────
    "https://philosophie.ens.psl.eu/",
    # ── Sciences sociales ─────────────────────────────────────────────────────
    "https://sciences-sociales.ens.psl.eu/",
    # ── Géographie ────────────────────────────────────────────────────────────
    "https://geographie.ens.psl.eu/",
    # ── Littératures et langage ───────────────────────────────────────────────
    "https://litteratures.ens.psl.eu/",
    # ── CERES ─────────────────────────────────────────────────────────────────
    "https://ceres.ens.psl.eu/",
    # ── ECLA (langues) ────────────────────────────────────────────────────────
    "https://ecla.ens.psl.eu/",
    # ── CIENS ─────────────────────────────────────────────────────────────────
    "https://ciens.ens.psl.eu/",
    "https://ciens.ens.psl.eu/brochure-cours-cette-annee/",
    "https://ciens.ens.psl.eu/enseignements-fr/",
    "https://ciens.ens.psl.eu/la-mineure/",
    "https://ciens.ens.psl.eu/semestre-1-2025-2026/",
    "https://ciens.ens.psl.eu/semestre-2-2025-2026/",
    "https://ciens.ens.psl.eu/notre-reglement-interieur-reglement-interieur-du-centre-interdisciplinaire-sur-les-enjeux-strategiques-ciensnotre-reglement-interieur/",
    "https://ciens.ens.psl.eu/charte-dutilisation-de-lintelligence-artificielle-generative/",
]

DELAY = 0.4


# ── Scraping ───────────────────────────────────────────────────────────────────

def fetch_page(url: str, session: requests.Session) -> str | None:
    try:
        r = session.get(url, timeout=12, verify=False)
        r.raise_for_status()
        if "text/html" not in r.headers.get("Content-Type", ""):
            return None
    except Exception as e:
        print(f"  ERR  {url} — {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Remove nav, footer, scripts, styles
    for tag in soup(["nav", "footer", "script", "style", "header"]):
        tag.decompose()

    # Try main content area first
    main = soup.find("main") or soup.find(id="content") or soup.find(class_="content") or soup.body
    if main is None:
        return None

    text = main.get_text(separator="\n", strip=True)
    # Collapse excessive blank lines
    lines = [l for l in text.splitlines() if l.strip()]
    return "\n".join(lines)


def url_to_title(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    slug = path.split("/")[-1].replace("-", " ").replace("%C3%A9", "e").replace("%C3%A8", "e")
    host = urlparse(url).netloc.replace("www.", "")
    return f"{host} — {slug}" if slug else host


# ── LLM filter ────────────────────────────────────────────────────────────────

def filter_with_llm(text: str, url: str) -> dict:
    prompt = (
        "Tu évalues une page web pour un chatbot administratif de l'ENS (École Normale Supérieure, Paris). "
        "Le chatbot répond aux questions des étudiants sur : vie à l'internat, thurnage, "
        "règlements, cours et formations, contacts administratifs, services étudiants.\n\n"
        f"URL : {url}\n\n"
        f"Contenu (premiers 2000 chars) :\n{text[:2000]}\n\n"
        "Réponds uniquement en JSON (pas de markdown) :\n"
        '{"score": <0-10>, "keep": <true/false>, "reason": "<une phrase>"}\n'
        "score >= 6 = garder. Rejette : pages vitrine vides, navigation pure, résultats de recherche, "
        "pages sans contenu actionnable pour un étudiant."
    )
    max_retries = 4
    for attempt in range(max_retries):
        r = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
            verify=False,
        )
        if r.status_code in (429, 503) and attempt < max_retries - 1:
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"  ...  {r.status_code}, retry dans {wait}s")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return json.loads(r.json()["choices"][0]["message"]["content"])


# ── Indexing ───────────────────────────────────────────────────────────────────

def build_documents(urls: list[str], filter_llm: bool = False) -> list[Document]:
    session = requests.Session()
    session.headers["User-Agent"] = "ClemENS-bot/1.0 (student project, ENS Ulm)"

    docs = []
    for url in urls:
        print(f"  Fetch  {url}")
        text = fetch_page(url, session)
        if not text or len(text) < 100:
            print(f"  SKIP   {url} (vide ou trop court)")
            time.sleep(DELAY)
            continue

        if filter_llm:
            try:
                verdict = filter_with_llm(text, url)
                score  = verdict.get("score", 0)
                keep   = verdict.get("keep", False)
                reason = verdict.get("reason", "")
                tag    = "KEEP" if keep else "SKIP"
                print(f"  {tag} [{score}/10] {url_to_title(url)}")
                print(f"         {reason}")
                if not keep:
                    time.sleep(DELAY)
                    continue
            except Exception as e:
                print(f"  WARN   filtre LLM échoué pour {url} — {e} (page conservée par défaut)")

        doc = Document(
            text=text,
            metadata={
                "source": url,
                "title": url_to_title(url),
                "type": "web",
            },
            id_=url,
        )
        docs.append(doc)
        print(f"  OK     {url_to_title(url)} ({len(text)} chars)")
        time.sleep(DELAY)

    return docs


def ingest(docs: list[Document]):
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    chroma_collection = chroma_client.get_or_create_collection(CHROMA_COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

    print(f"\nIndexation de {len(docs)} pages...")
    VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )
    print("Ingestion web terminée.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Ingérer une seule URL")
    parser.add_argument("--poc", action="store_true", help="Ingérer uniquement la sélection POC")
    parser.add_argument("--dry-run", action="store_true", help="Scrape + filtre LLM + affiche le résultat, sans ingérer")
    parser.add_argument("--filter", action="store_true", help="Activer le filtre LLM Mistral avant ingestion")
    args = parser.parse_args()

    if args.url:
        urls = [args.url]
    elif args.poc:
        urls = POC_WEB_SOURCES
    else:
        urls = WEB_SOURCES

    use_filter = args.filter or args.dry_run

    print(f"Récupération de {len(urls)} page(s){' + filtre LLM' if use_filter else ''}...\n")
    docs = build_documents(urls, filter_llm=use_filter)

    kept   = len(docs)
    total  = len(urls)

    if use_filter:
        print(f"\n{'─' * 45}")
        print(f"  {kept} / {total} pages retenues  |  {total - kept} filtrées")
        print(f"{'─' * 45}")

    if not docs:
        print("Aucun document récupéré.")
        return

    if args.dry_run:
        print("[dry-run] Aucune ingestion effectuée.")
        return

    ingest(docs)


if __name__ == "__main__":
    main()
