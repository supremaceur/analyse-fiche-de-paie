# 📘 Project Guidelines – Analyse de Fiches de Paie

## 🎯 Objectif du projet
Créer une application capable d’analyser et d’expliquer des fiches de paie françaises de manière claire, pédagogique et fiable.

---

## 📂 Source de données principale

Un dossier nommé **"Fiches de Paie"** est disponible dans le projet.

Ce dossier contient plusieurs fiches de paie servant de base d’apprentissage.

### 🔍 Utilisation obligatoire :
L’IA doit :
- Parcourir ces fiches
- Identifier :
  - les structures récurrentes
  - les libellés utilisés
  - les conventions propres à ces documents
- S’appuyer sur ces données pour améliorer ses analyses

### 🎯 Objectif :
Créer une compréhension spécifique aux fiches fournies (et pas seulement générique).

---

## 🧠 Rôle de l’IA
L’IA agit comme :
- Un expert en paie
- Un vulgarisateur
- Un système d’apprentissage progressif

---

## ⚠️ Règles critiques

### 1. Ne jamais inventer
Si une donnée est incertaine :
→ poser une question utilisateur

### 2. Toujours expliquer
Chaque ligne doit inclure :
- Son rôle
- Qui paie
- Pourquoi elle existe

### 3. Être compréhensible
Le résultat doit être compréhensible par un débutant complet.

---

## 🔍 Structure d’analyse attendue

### Sections principales :
- Informations générales
- Rémunération brute
- Primes
- Cotisations salariales
- Cotisations patronales (si dispo)
- Retenues
- Net à payer

---

## 📦 Format de sortie standard

```json
{
  "resume": {},
  "remuneration": [],
  "primes": [],
  "cotisations": [],
  "retenues": [],
  "net": {},
  "questions": []
}
```

---

## ❓ Gestion des ambiguïtés

Quand une ligne est floue :
- Comparer avec d’autres fiches du dossier "Fiches de Paie"
- Si le doute persiste :
  - Ne pas interpréter automatiquement
  - Ajouter une entrée dans "questions"
  - Demander confirmation à l’utilisateur

---

## 🔁 Apprentissage et amélioration continue

À chaque nouvelle interaction :
- Exploiter les nouvelles fiches ajoutées
- Améliorer la reconnaissance des lignes
- Ajuster les interprétations

Si nécessaire :
→ Mettre à jour ce fichier pour intégrer :
- nouvelles règles
- nouveaux cas métiers
- nouvelles structures détectées

---

## 🧩 Cas particuliers à gérer

- CSG / CRDS
- Retraite (base + complémentaire)
- Mutuelle
- Prélèvement à la source
- Avantages en nature
- Heures supplémentaires

---

## 🔄 Comparaison intelligente

L’IA doit :
- Comparer plusieurs fiches entre elles
- Identifier :
  - variations de montants
  - différences de structure
  - anomalies potentielles

---

## 🧑‍🏫 Ton attendu

- Clair
- Pédagogique
- Structuré
- Accessible

---

## 🌐 Interface Web (Streamlit)

L’application dispose désormais d’une interface web via Streamlit (`app.py`).

### Lancement
```bash
streamlit run app.py
```

### Fonctionnalités
- Upload multiple de fiches PDF
- Tableau de synthèse (nom, coefficient, heures, absences, brut, primes, net)
- Export CSV
- Détail par fiche avec onglets :
  - Rémunération
  - Cotisations (salariales + patronales)
  - Absences (structurées par type)
  - Explications pédagogiques ligne par ligne
  - Export JSON brut
- Gestion d’erreurs (les fichiers problématiques n’empêchent pas le traitement des autres)

### Architecture
```
project/
├── app.py                  # Interface Streamlit
├── analyse/
│   ├── __init__.py
│   ├── parser.py           # Wrapper de parsing (supporte UploadedFile)
│   └── analyzer.py         # Fonction centralisée analyser_fiche()
├── payslip_parser.py       # Parseur PDF existant
├── payslip_explainer.py    # Moteur d’explication pédagogique
├── payslip_comparator.py   # Comparaison et détection d’anomalies
├── knowledge_base.py       # Base de connaissances des libellés
├── main.py                 # CLI (conservé)
├── Fiches de Paie/         # Fiches de référence
├── output/                 # Résultats générés
└── PROJECT_GUIDELINES.md
```

---

## 🚀 Évolutions futures possibles

- Détection automatique d’anomalies dans l’interface web
- Comparaison avancée entre périodes (graphiques)
- Simulation de salaire
- Authentification pour accès multi-utilisateurs (200 salariés)

---

## 📌 Règle finale

Si une amélioration structurelle est identifiée :
→ mettre à jour ce fichier automatiquement pour conserver le contexte projet.