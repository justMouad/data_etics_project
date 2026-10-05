"""Point d'entrée principal du projet."""

from __future__ import annotations

from pathlib import Path

from src.utils import load_settings, print_project_banner


def run_pipeline() -> None:
    """Lance le pipeline dans une version de base du projet.

    Le pipeline complet LLM n'est pas encore implémenté. Cette fonction sert
    de point d'entrée de démonstration pour valider que le projet se lance
    correctement depuis sa racine.
    """
    settings = load_settings()
    root = Path(__file__).resolve().parent.parent
    print_project_banner(root)
    print(f"Projet initialisé avec succès. Configuration chargée depuis {settings['paths']['database']}")
    print("TODO: brancher l'ingestion, le nettoyage, l'extraction LLM et l'évaluation finale.")


def main() -> None:
    run_pipeline()


if __name__ == "__main__":
    main()
