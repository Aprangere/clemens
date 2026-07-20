---
class: projet
type: log
projet: "[[ClemENS]]"
domains:
  - "[[Intelligence Artificielle]]"
date: 2026-04-30
---
← [[ClemENS]]

# Debug — Couverture des sources et cours

Objectif : ClemENS doit pouvoir répondre à « quels cours propose le département X ? » pour tous les départements.

---

## État actuel de la base (2026-04-30)

- **19 686 chunks** dans ChromaDB
- **684 PDFs** ingérés (11 234 pages lisibles, 26 ignorés — PDFs scannés sans couche texte)
- **100 pages HTML** ingérées (DG, ENS principal, bibliothèque, 12 départements)

---

## Problème identifié : département de Biologie

### Symptôme
La question « liste des cours du département de biologie » retourne seulement une mention d'un cours ("Introduction aux sciences du vivant") trouvé dans une brochure DMA, pas dans les sources bio directes.

### Cause
Le site principal `www.bio.ens.psl.eu/depbio/` est une vitrine quasi vide (1 539 chars scrappés).  
Les cours de biologie sont publiés sur un sous-domaine séparé **non seedé** :  
→ `www.edu.bio.ens.psl.eu` — site dédié à l'enseignement du département (découvert dans le crawl mais non ingéré)  
→ `www.ibens.bio.ens.psl.eu` — IBENS (recherche, potentiellement cours de master)

Aucun PDF propre au département de biologie n'est présent dans `app/data/`.

### Diagnostic
`www.edu.bio.ens.psl.eu` renvoie un vieux Drupal avec meta-redirect cassé ("Vous allez être redirigé") — contenu irrécupérable par scraping. Même pattern sur plusieurs autres départements.

### Correctif recommandé
Télécharger manuellement la brochure de formation bio (PDF) depuis le site du département et déposer dans `app/data/`, puis relancer `python app/ingest.py`.

---

## Pattern général : départements à couverture faible

**Cause commune** : vieux CMS (Drupal/Joomla), redirects cassés, contenu JS-rendu — BeautifulSoup ne récupère que la coquille.

| Département | Chars récupérés | Cause probable |
|---|---|---|
| Biologie | 1 539 + redirect mort | Vieux Drupal, edu.bio.ens.psl.eu inutilisable |
| Géographie | 681 | Site très léger |
| Littératures & langage | 1 032 | Site léger |
| Arts | 4 603 | Correct mais peu de détail cours |
| Cognitives | 1 834 | Site léger |
| ECLA / CIENS | ~2 400 | Contenu généraliste, pas de liste de cours |
| FAQs DG | ~250 chacune | JS — texte presque vide |

**Départements bien couverts** (scraping riche) : Mathématiques, Physique, Géosciences, Antiquité, Histoire, Chimie, Informatique

### Recommandation pour la démo
→ **Ajout manuel** : déposer les brochures PDF des départements faibles dans `app/data/` et relancer `python app/ingest.py`  
→ Les brochures DMA Math (`brochure-2024-2025.pdf`) et Physique (livrets ICFP) couvrent déjà bien leurs formations — téléchargées et ingérées ✓

---

## PDFs scannés (non lisibles, 26 fichiers)

Ces 26 fichiers sont des images scannées sans couche OCR — hors scope POC.  
Exemples : arrêtés officiels anciens (2007–2021), sujets de concours scannés.  
Solution post-POC : intégrer Tesseract OCR ou Adobe PDF Services.

---

## Sources CAS (non accessibles sans authentification)

- `intranet.ens.psl.eu` — règlement intérieur, PAJ, documents RH
- `moodle.ens.psl.eu` — ressources pédagogiques complètes
- `dg.ens.fr/degetteweb` — gestion internat

Ces sources nécessitent une intégration CAS post-POC ou une ingestion manuelle périodique.
