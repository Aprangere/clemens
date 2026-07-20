---
class: projet
type: log
projet: "[[ClemENS]]"
domains:
  - "[[Intelligence Artificielle]]"
date: 2026-05-01
---
← [[ClemENS]]

# ClemENS vs NotebookLM

## Constat

NotebookLM (Google) fait 80% de ce que fait ClemENS en 10 minutes, sans infrastructure. La question est : qu'est-ce que ClemENS apporte que NotebookLM ne peut pas faire ?

---

## Avantages de ClemENS

**RGPD / souveraineté des données**
NotebookLM = Google. Une institution publique française qui envoie les questions de ses étudiants à Google pose un problème juridique réel. ClemENS utilise Mistral AI (entreprise française, DPA, hébergement EU, données non utilisées pour l'entraînement) — vendable à la DSI et au DPO de l'ENS.

**Base partagée et maintenue**
NotebookLM fonctionne par utilisateur : chacun uploade ses propres docs. ClemENS c'est une base centrale maintenue par l'ENS, identique pour tous, mise à jour de façon centralisée.

**Intégration CAS (potentiel)**
À terme, ClemENS peut s'authentifier via le CAS ENS et accéder à l'intranet, Moodle, aux ressources protégées. NotebookLM ne fera jamais ça.

**Contrôle institutionnel**
L'ENS choisit ce qui entre dans la base, comment le bot répond, peut auditer les questions posées, personnaliser le ton et les limites du système.

**Branding**
ClemENS est un produit ENS. NotebookLM est un produit Google.

---

## Avantages de NotebookLM

- Prêt en 10 minutes, zéro infrastructure
- Interface très soignée (audio overviews, podcast, etc.)
- Modèle IA constamment mis à jour par Google
- Gratuit

---

## Positionnement pour le pitch direction

NotebookLM est un **argument de vente**, pas un concurrent :
> *"NotebookLM fait la même chose mais avec les données chez Google. ClemENS garde tout en interne, est conforme RGPD, et peut s'intégrer au CAS ENS."*

**Risque** : la direction répond *"on utilise juste NotebookLM alors"*.
**Réponse** : RGPD + CAS + base institutionnelle partagée + contrôle.

---

## Question stratégique ouverte

ClemENS est-il un outil interne ENS à long terme, ou un POC pour démontrer la faisabilité ?

- Si **long terme** : l'investissement infra/maintenance se justifie, intégration CAS à planifier.
- Si **POC uniquement** : NotebookLM suffit pour la démo, ClemENS sert à montrer qu'on peut faire mieux si on le décide.
