---
class: projet
type: main
domains:
  - "[[Intelligence Artificielle]]"
  - "[[Maths-Info]]"
  - "[[STS]]"
status: planning
---

>[!abstract] Overview
> Chatbot pour dialoguer avec les informations administratives de l'ENS.

## Tasks
```dataview
TASK
FROM "01 PROJETS/ClemENS"
WHERE !completed
```

## Capstone
```dataview
LIST
FROM "01 PROJETS/ClemENS"
WHERE type = "deliverable"
```

## Meetings
```dataview
LIST
FROM "01 PROJETS/ClemENS"
WHERE type = "meeting"
SORT date DESC
```

## Ideas
```dataview
LIST
FROM "01 PROJETS/ClemENS"
WHERE class = "seedling" OR type = "fleeting"
SORT file.mtime DESC
```
