---
class: projet
type: fleeting
projet: "[[ClemENS]]"
---
← [[ClemENS]]
# RGPD & IA — Conformité ClemENS

## Options de conformité

### Option 1 — LLM local (Ollama + Mistral)
Aucune donnée ne sort du serveur ENS. Solution la plus propre juridiquement, recommandée pour une institution publique française. Aucun DPA nécessaire.

### Option 2 — Mistral API avec DPA
Mistral AI est une entreprise française, hébergement EU, DPA disponible. Le DPA (effectif nov. 2025) stipule que les données ne sont pas utilisées pour entraîner les modèles. Standard Contractual Clauses (SCCs) pour les transferts internationaux.
- DPA : [legal.mistral.ai/terms/data-processing-addendum](https://legal.mistral.ai/terms/data-processing-addendum)
- Conformité & certifications : [help.mistral.ai — Regulatory Compliance](https://help.mistral.ai/en/collections/789670-regulatory-compliance-and-certification)
- Stockage des données : [help.mistral.ai — Where is data stored](https://help.mistral.ai/en/articles/347629-where-do-you-store-my-data-or-my-organization-s-data)

## Recommandations CNIL (2025)

La CNIL a publié ses recommandations IA/RGPD en 2025. Points clés pour ClemENS :
- Les prompts utilisateurs contenant des données personnelles sont concernés par le RGPD
- Principe de minimisation : ne pas ingérer plus que nécessaire
- Information des personnes si données personnelles traitées

- Recommandations CNIL IA : [cnil.fr — IA et RGPD recommandations](https://www.cnil.fr/fr/ia-et-rgpd-la-cnil-publie-ses-nouvelles-recommandations-pour-accompagner-une-innovation-responsable)
- Fiches pratiques IA : [cnil.fr — fiches pratiques](https://www.cnil.fr/fr/les-fiches-pratiques-ia)

## À noter pour le pitch

- CAS ≠ RGPD : l'authentification contrôle l'accès, pas le traitement des données
- Solution locale = argument fort face à la direction d'une institution publique
- Les requêtes des utilisateurs (questions administratives) contiennent rarement des données sensibles — risque RGPD faible côté usage
