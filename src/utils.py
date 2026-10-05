"""Utilitaires divers et chargement des paramètres de configuration."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_settings(settings_path: str | Path | None = None) -> dict:
    """Charge la configuration YAML principale."""
    if settings_path is None:
        settings_path = Path(__file__).resolve().parent.parent / "config" / "settings.yaml"
    with Path(settings_path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def print_project_banner(project_root: str | Path) -> None:
    """Affiche un petit message de bienvenue pour le projet."""
    root = Path(project_root)
    print("==== etics-contrats ====")
    print(f"Racine du projet : {root}")
    print("Projet académique de détection de clauses toxiques dans des contrats fictifs.")
