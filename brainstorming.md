---
class: projet
type: fleeting
domains:
  - "[[Intelligence Artificielle]]"
  - "[[STS]]"
---

← [[ClemENS]]

# Brainstorming — ClemENS

## Contexte et objectif

Chatbot RAG pour aider étudiants et personnel ENS à naviguer les informations administratives. Objectif immédiat : **proof of concept fonctionnel** à présenter à la direction et à des profils techniques. Projet aussi à visée pédagogique — apprendre RAG, vector stores, scraping, auth en pratique.

## Architecture retenue

```
Sources (PDFs, pages web ENS)
        ↓
  Ingestion + Chunking
        ↓
  Embeddings (sentence-transformers)
        ↓
  ChromaDB (vector store local)
        ↓
  Retrieval → Claude API (Sonnet) → Réponse sourcée
        ↓
  Interface Streamlit
```

## Sources de données

- PDFs publics ENS (règlements, guides, circulaires)
- Pages web ENS scrapées (BeautifulSoup)
- Docs derrière auth → **ingestion manuelle** par un admin (pas de scraping authentifié)

## Auth

- Sources privées : ingestion manuelle, contenu vit dans ChromaDB
- Accès à ClemENS : simple auth pour le POC, CAS ENS possible ensuite

## Stack MVP

| Couche | Choix | Note |
|---|---|---|
| UI | Streamlit | |
| LLM | Ollama + Mistral (local) | RGPD : rien ne sort du serveur |
| Embedding | `sentence-transformers` | local, pas d'API externe |
| Vector DB | ChromaDB | local |
| Ingestion | LangChain / LlamaIndex | |
| Scraping | BeautifulSoup | |

Alternative LLM si serveur limité : Mistral API (entreprise FR, hébergement EU, DPA RGPD).

## Chemin d'apprentissage

1. RAG de base — PDFs → ChromaDB → Claude → Streamlit
2. Web scraping — pages ENS publiques dans le pipeline
3. Auth chatbot — login simple, puis CAS ENS
4. Sources privées — ingestion manuelle de docs authentifiés

## POC — ce qu'il faut pour convaincre

- 5–10 vrais docs ENS ingérés
- Réponses **sourcées** (le chatbot cite le document source)
- UI propre et simple
- Quelques questions-types qui marchent bien pour la démo (scénarios préparés)
- Réponse claire quand il ne sait pas (pas d'hallucination)

## Décisions arrêtées

- **Hébergement** : local (serveur ENS) — données sensibles, pas de cloud
- **Mise à jour** : à définir plus tard
- **Auth CAS** : à définir plus tard, hors scope POC

## Questions ouvertes

- Bilingue FR/EN ou 100% français ?
- Qui gère l'ingestion des docs privés côté ENS ?

