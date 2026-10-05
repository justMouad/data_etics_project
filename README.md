# etics-contrats

## Présentation du projet

`etics-contrats` est un projet universitaire de recherche et de prototypage sur la détection automatique de clauses toxiques dans des contrats de travail français. L'objectif est d'évaluer si un modèle de langage peut repérer, classifier et expliquer les clauses problématiques dans des documents contractuels synthétiques, fictifs et contrôlés.

Le projet est conçu comme une base solide pour des expérimentations reproductibles en NLP, avec une séparation claire entre ingestion, nettoyage, schémas de données, extraction, base SQLite locale et évaluation.

## Objectif scientifique

L'objectif est d'étudier la capacité d'un système de traitement automatique à :

- détecter des clauses potentiellement toxiques dans des contrats synthétiques ;
- classer les clauses selon des catégories de toxicité définies par le projet ;
- évaluer la robustesse des détections sur un corpus fictif ;
- produire des traces explicatives et des métriques de qualité ;
- préparer une extension future vers un pipeline complet avec un LLM via une API externe.

Le projet ne vise pas à fournir un avis juridique et ne doit pas être utilisé comme base décisionnelle réelle.

## Architecture générale

Le projet est structuré en modules de responsabilités distinctes :

- `src/ingestion.py` : chargement des contrats et préparation du corpus ;
- `src/nettoyage.py` : normalisation du texte et nettoyage des documents ;
- `src/schemas.py` : schémas Pydantic pour la validation des données ;
- `src/llm_client.py` : interface LLM centralisée en préparation d'une intégration API ;
- `src/extraction.py` : extraction des clauses et génération de résultats ;
- `src/database.py` : accès local à SQLite ;
- `src/evaluation.py` : métriques et agrégation des résultats ;
- `src/utils.py` : utilitaires, configuration et chemins de fichiers ;
- `config/` : schémas, catégories de toxicité et paramètres ;
- `prompts/` : instructions LLM et exemples few-shot ;
- `resultats/` : sorties JSON/CSV et logs ;
- `tests/` : tests unitaires de validation.

## Installation

### Création de l'environnement virtuel

```bash
python -m venv .venv
```

#### Windows

```powershell
.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Configuration du .env

Créez un fichier `.env` à la racine du projet et ajoutez les variables nécessaires :

```env
LLM_API_KEY=
LLM_MODEL=gpt-4o-mini
```

Le fichier `.env` est ignoré par Git et la clé API ne doit jamais être ajoutée dans le dépôt.

## Structure des dossiers

```text
etics-contrats/
├── README.md
├── requirements.txt
├── .env
├── .gitignore
├── config/
│   ├── schema.json
│   ├── categories.json
│   └── settings.yaml
├── prompts/
│   ├── generation_contrats.txt
│   ├── extraction.txt
│   └── exemples_fewshot.json
├── data/
│   ├── contrats/
│   ├── verite_terrain/
│   ├── reels/
│   ├── brut/
│   └── db/
│       └── etics.sqlite
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── ingestion.py
│   ├── nettoyage.py
│   ├── schemas.py
│   ├── llm_client.py
│   ├── extraction.py
│   ├── database.py
│   ├── evaluation.py
│   └── utils.py
├── scripts/
│   ├── decouper_sortie_chatgpt.py
│   ├── convertir_en_pdf_docx.py
│   └── verifier_corpus.py
├── resultats/
│   ├── json/
│   ├── logs/
│   ├── metriques.csv
│   └── erreurs.csv
├── notebooks/
│   ├── 01_exploration_corpus.ipynb
│   ├── 02_test_prompt.ipynb
│   └── 03_analyse_resultats.ipynb
├── docs/
│   ├── definition_toxicite.md
│   ├── guide_annotation.md
│   ├── schema_bd.md
│   ├── limites_ethique.md
│   └── rapport/
└── tests/
    ├── test_schemas.py
    └── test_evaluation.py
```

## Format des données d'entrée

Les contrats utilisés dans ce projet sont synthétiques et fictifs. Les fichiers peuvent être déposés dans `data/contrats/` sous différents formats (TXT, PDF, DOCX, JSON) selon les besoins de la campagne. Le corpus est conçu pour supporter à la fois :

- des contrats complets ;
- des morceaux de contrat ciblés ;
- des documents de référence de terrain ;
- des sorties d'annotation ou de validation.

Chaque document doit être annoté ou structuré de manière cohérente, avec un identifiant unique (ex. `contrat_001`) et un objet de métadonnées associé.

## Fonctionnement prévu du pipeline

1. Ingestion des fichiers de contrat depuis `data/contrats/` et `data/brut/`.
2. Nettoyage et normalisation du texte.
3. Extraction des clauses sur la base de règles ou d'un modèle LLM.
4. Validation des clauses avec des schémas Pydantic.
5. Enregistrement des résultats dans SQLite local (`data/db/etics.sqlite`).
6. Évaluation sur un corpus de référence synthétique ou manuel.
7. Export des résultats dans `resultats/json/` et `resultats/metrics.csv`.

## Comment lancer le projet

Depuis la racine du projet :

```bash
python -m src.main
```

## Comment lancer les tests

```bash
pytest
```

## Comment générer les contrats synthétiques

La génération de contrats synthétiques est prévue via des scripts internes ou des notebooks. Les documents générés doivent rester fictifs et ne pas contenir de données personnelles réelles.

Les scripts d'aide sont présents dans `scripts/` et peuvent être étendus pour produire un corpus contrôlé selon des profils de contrat, secteurs ou catégories.

## Comment évaluer le système

Le module `src/evaluation.py` prépare les métriques de base pour le projet. L'évaluation peut intégrer :

- précision et rappel par catégorie ;
- taux de détection des clauses toxiques ;
- taux de faux positifs ;
- scores de similarité sur les textes extraits ;
- analyse des écarts entre annotations humaines et sorties du modèle.

## Avertissement important

Les contrats et données utilisés dans ce projet sont entièrement synthétiques, fictifs et créés à des fins académiques. Aucun document réel, aucun contrat d'une personne réelle, ni aucune donnée personnelle n'est utilisé dans ce dépôt.

## Limites du système

- Le pipeline LLM n'est pas encore implémenté totalement ; il est prévu comme extension future.
- La détection de toxicité repose sur un cadre de travail académique et non sur un avis juridique.
- Les catégories de toxicité doivent être enrichies et validées par des experts métier ou juridiques.
- Les résultats doivent toujours être interprétés dans un contexte de recherche, pas comme une décision de conformité.

## Remarques de conception

- Le projet est pensé pour être maintenable, modulaire et extensible.
- Les schémas Pydantic servent de garde-fou pour les sorties structurées.
- L'accès à l'API LLM se fait via des variables d'environnement, jamais directement codées.
- Les dépendances sont volontairement limitées à ce qui est nécessaire au lancement du projet.
