"""Fonctions de nettoyage et normalisation des textes contractuels."""

from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    """Remplace les espaces multiples par un seul espace et supprime les retours à la ligne excessifs."""
    return re.sub(r"\s+", " ", text).strip()


def clean_contract_text(text: str) -> str:
    """Nettoie le texte d'un contrat avant extraction."""
    cleaned = text.replace("\r", "\n")
    cleaned = normalize_whitespace(cleaned)
    return cleaned


def split_sentences(text: str) -> list[str]:
    """Sépare le texte en phrases simples reconstruites à partir de points et de retours à la ligne."""
    return [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]
