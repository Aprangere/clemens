"""
Crawl ENS Ulm (ens.psl.eu) and its subsites to discover PDFs and admin pages.
Outputs a structured markdown block ready to paste into Data.md.

Usage:
    python scrape_sources.py
    python scrape_sources.py --update   # writes result directly into Data.md
"""

import argparse
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ── Config ────────────────────────────────────────────────────────────────────

DATA_MD = Path(__file__).parent.parent / "Data.md"

# Domaines déjà crawlés — exclus du crawl département (exact match, pas les sous-domaines)
DONE_DOMAINS = re.compile(
    r"^(www\.)?dg\.ens\.fr$|^www\.ens\.psl\.eu$"
)

def _seeds_from_data_md(skip_done: bool = False) -> list[str]:
    """Extract non-CAS http(s) URLs from Data.md as crawl seeds."""
    urls = []
    url_re = re.compile(r'https?://[^\s\)\]|<>"]+')
    for line in DATA_MD.read_text(encoding="utf-8").splitlines():
        if "CAS" in line:
            continue
        for url in url_re.findall(line):
            url = url.rstrip(".,;)")
            if skip_done and DONE_DOMAINS.search(urlparse(url).netloc.lower()):
                continue
            if url not in urls:
                urls.append(url)
    return urls

SEEDS = _seeds_from_data_md()

DG_SEEDS = [
    "https://www.dg.ens.fr/fr/",
    "https://www.dg.ens.fr/fr/reglement/",
    "https://www.dg.ens.fr/fr/faqs/delegation-generale/",
]

DG_DOMAIN = re.compile(r"(^|\.)dg\.ens\.fr$")

ALLOWED_DOMAINS = re.compile(
    r"(^|\.)ens\.psl\.eu$|(^|\.)ens\.fr$"
)

MAX_PAGES = 500
MAX_DEPTH = 4
DELAY = 0.3  # seconds between requests

ADMIN_KEYWORDS = re.compile(
    r"scolar|administrat|règlement|inscription|bourse|logement|"
    r"biblioth|service|diplôme|stage|visa|séjour|international|contact|"
    r"faq|guide|form|procédure|vie.étudiant|formation|accueil|mobilit|"
    r"ressource|document|cours|enseignement|master|licence|programme|"
    r"recherche|seminaire|séminaire|agenda|annonce|actualit",
    re.IGNORECASE,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def is_allowed(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return bool(ALLOWED_DOMAINS.search(host))


def is_pdf(url: str) -> bool:
    return urlparse(url).path.lower().endswith(".pdf")



# ── Crawler ───────────────────────────────────────────────────────────────────

def crawl(seeds=None, domain_filter=None, max_pages=None, max_depth=None):
    seeds = seeds or SEEDS
    domain_filter = domain_filter or ALLOWED_DOMAINS
    max_pages = max_pages or MAX_PAGES
    max_depth = max_depth or MAX_DEPTH

    session = requests.Session()
    session.headers["User-Agent"] = "ClemENS-bot/1.0 (student project, ENS Ulm)"

    visited = set()
    queue = [(url, 0) for url in seeds]

    pdfs: set[str] = set()
    admin_pages: dict[str, list[str]] = defaultdict(list)
    subsites: set[str] = set()

    print(f"Crawl — max {max_pages} pages, profondeur {max_depth}\n")

    while queue and len(visited) < max_pages:
        url, depth = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        host = urlparse(url).netloc
        subsites.add(host)

        print(f"  [{len(visited):>3}] {url}")

        try:
            r = session.get(url, timeout=10)
            r.raise_for_status()
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue
        except Exception:
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup.find_all("a", href=True):
            href = urljoin(url, tag["href"]).split("#")[0].split("?")[0]
            if not href.startswith("http"):
                continue
            link_host = urlparse(href).netloc.lower()
            if not domain_filter.search(link_host):
                continue
            if is_pdf(href):
                pdfs.add(href)
            elif depth < max_depth and href not in visited:
                queue.append((href, depth + 1))

        if ADMIN_KEYWORDS.search(url):
            admin_pages[host].append(url)

        time.sleep(DELAY)

    return sorted(pdfs), dict(admin_pages), sorted(subsites)


def download_pdfs(pdfs: list[str], dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "ClemENS-bot/1.0 (student project, ENS Ulm)"
    downloaded, skipped = 0, 0
    for url in pdfs:
        filename = Path(urlparse(url).path).name
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        out = dest / filename
        if out.exists():
            skipped += 1
            continue
        try:
            r = session.get(url, timeout=15)
            r.raise_for_status()
            out.write_bytes(r.content)
            print(f"  OK  {filename}")
            downloaded += 1
        except Exception as e:
            print(f"  ERR {url} — {e}")
        time.sleep(DELAY)
    print(f"\n{downloaded} téléchargés, {skipped} déjà présents.")


# ── Output ────────────────────────────────────────────────────────────────────

def render_markdown(pdfs, admin_pages, subsites) -> str:
    lines = ["## Sources découvertes — ENS Ulm", ""]

    lines.append("### PDFs")
    if pdfs:
        for p in pdfs:
            lines.append(f"- {p}")
    else:
        lines.append("_aucun trouvé_")
    lines.append("")

    lines.append("### Pages administratives")
    for host, urls in sorted(admin_pages.items()):
        lines.append(f"\n#### {host}")
        for u in sorted(set(urls)):
            lines.append(f"- {u}")
    if not admin_pages:
        lines.append("_aucune trouvée_")
    lines.append("")

    lines.append("### Sites et sous-domaines")
    for s in subsites:
        lines.append(f"- {s}")
    lines.append("")

    return "\n".join(lines)


def update_data_md(block: str):
    marker_start = "<!-- scrape:start -->"
    marker_end = "<!-- scrape:end -->"
    content = DATA_MD.read_text(encoding="utf-8")

    replacement = f"{marker_start}\n{block}\n{marker_end}"

    if marker_start in content:
        content = re.sub(
            f"{re.escape(marker_start)}.*?{re.escape(marker_end)}",
            replacement,
            content,
            flags=re.DOTALL,
        )
    else:
        content += f"\n\n{replacement}\n"

    DATA_MD.write_text(content, encoding="utf-8")
    print(f"\nData.md mis à jour : {DATA_MD}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true", help="Écrire dans Data.md")
    parser.add_argument("--dg-only", action="store_true", help="Crawl dédié dg.ens.fr uniquement")
    parser.add_argument("--dept-only", action="store_true", help="Crawl départements uniquement (skip DG + ENS main déjà faits)")
    parser.add_argument("--download", action="store_true", help="Télécharger les PDFs dans app/data/")
    args = parser.parse_args()

    if args.dg_only:
        pdfs, admin_pages, subsites = crawl(
            seeds=DG_SEEDS,
            domain_filter=DG_DOMAIN,
            max_pages=500,
            max_depth=4,
        )
    elif args.dept_only:
        dept_seeds = _seeds_from_data_md(skip_done=True)
        print(f"Seeds départements ({len(dept_seeds)}) :")
        for s in dept_seeds:
            print(f"  {s}")
        pdfs, admin_pages, subsites = crawl(
            seeds=dept_seeds,
            max_pages=MAX_PAGES,
            max_depth=MAX_DEPTH,
        )
    else:
        pdfs, admin_pages, subsites = crawl()

    block = render_markdown(pdfs, admin_pages, subsites)

    if args.update:
        update_data_md(block)

    if args.download:
        dest = Path(__file__).parent / "data"
        print(f"\nTéléchargement de {len(pdfs)} PDFs vers {dest}...")
        download_pdfs(pdfs, dest)

    print("\n" + "-" * 60)
    print(block)

    if not args.update:
        print("(Passe --update pour écrire dans Data.md)")


if __name__ == "__main__":
    main()
