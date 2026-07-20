---
class: projet
type: task
domains:
  - "[[Intelligence Artificielle]]"
  - "[[Maths-Info]]"
projet: "[[ClemENS]]"
---
← [[ClemENS]]

# POC — Next Steps

Étapes priorisées pour un POC convaincant. CAS et déploiement à l'échelle sont hors scope pour cette phase.

---

## ✅ Fait

- [x] Architecture RAG fonctionnelle (LlamaIndex + ChromaDB + Mistral API)
- [x] Scraper ENS (`scrape_sources.py`) — crawl de tous les sous-sites ENS
- [x] 148 PDFs téléchargés dans `app/data/` (DG, textes officiels, manuels internat...)
- [x] Ingestion PDF corrigée — `fitz`/pymupdf page par page (fix du bug `SimpleDirectoryReader` qui lisait les PDFs en binaire brut)
- [x] 2477 pages PDF propres dans ChromaDB
- [x] 27 pages HTML ingérées (règlements DG, FAQs, pages admin ENS)
- [x] `ingest.py --poc` et `ingest_web.py --poc` — mode sélection réduite pour dev rapide
- [x] `main.py` — interface Streamlit avec historique et citations sources
- [x] `CLAUDE.md` — documentation complète du projet
- [x] `debug-log.md` — log des problèmes et solutions
- [x] `Data.md` — inventaire complet : 17 départements, PDFs, ressources CAS flaggées
- [x] App fonctionnelle ✅

---

## 🔄 En cours

- [x] Crawler les 17 sites départements (scrape_sources.py en cours de mise à jour)
- [ ] Ingérer les pages HTML des départements (cours, formations, secrétariats)

---

## À faire — Sources

- [ ] Relancer `scrape_sources.py --download --update` avec tous les seeds départements
- [ ] Relancer `ingest.py` pour les nouveaux PDFs départements
- [ ] Relancer `ingest_web.py` avec les pages départements découvertes
- [ ] 14 arrêtés officiels scannés (PDFs images) — nécessitent OCR, hors scope POC
- [ ] FAQs DG (contenu JS non récupérable par BeautifulSoup) — copie manuelle ou Playwright

## Idée — Collecteur de documents (phase beta)

- [ ] Formulaire / point de dépôt pour que les étudiants et le personnel partagent eux-mêmes des documents (brochures départements, guides, comptes-rendus à jour...)
- Rationale (2026-07-20) : le vrai goulot d'étranglement de ClemENS c'est les **sources**, pas le pipeline RAG — scraping automatisé plafonne vite (9 départements avec sites morts, docs qui se périment sans qu'on le sache). Un collecteur crowdsourcé auprès des utilisateurs de la beta comblerait les trous plus vite qu'un scraping/curation manuelle supplémentaire.
- À trancher : formulaire simple (Google Form/Typeform → dépôt manuel dans `app/data/`) vs. upload direct intégré à l'app Streamlit avec ingestion automatique
- Le risque n'est pas la pertinence (un dépôt volontaire est par nature déjà jugé pertinent par la personne qui le partage, contrairement au bruit structurel du crawl) mais la **péremption silencieuse** : `Documents_réforme_UDG.pdf` était un doc légitime à l'origine, personne ne l'a retiré quand la réforme a changé. Prévoir une date de dépôt visible + rappel périodique ("ce doc a 1 an, toujours valide ?") plutôt qu'une modération de contenu lourde.

## À faire — Ressources CAS (ingestion manuelle)

- [ ] Télécharger manuellement depuis `intranet.ens.psl.eu` et déposer dans `app/data/`
- [ ] Idem pour `moodle.ens.psl.eu` si pertinent

## À faire — Interface

- [x] Personnaliser avatars et logo ENS (`st.chat_message(avatar=...)`)
- [x] Message d'accueil / instructions minimales

## À faire — Validation

- [ ] Rédiger 6–8 questions-types que posent vraiment les étudiants ENS
- [ ] Tester chaque question, noter succès et échecs
- [ ] Préparer les scénarios de démo à partir des cas qui marchent

## À faire — Pitch direction

- [ ] Préparer slide RGPD (DPA Mistral + option locale)
- [ ] Démonstration live avec scénarios validés
- [ ] Formuler les prochaines étapes post-POC

---

## Hors scope POC

- Auth CAS ENS — après validation direction
- Déploiement à l'échelle — idem
- OCR des arrêtés scannés
- Playwright pour FAQs JS
