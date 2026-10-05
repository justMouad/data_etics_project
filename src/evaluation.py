"""Évaluation et métriques de qualité du système."""

from __future__ import annotations

from src.schemas import ContractAnalysis


def classify_contract_toxicity(analysis: ContractAnalysis) -> str:
    """Retourne le niveau global de toxicité d'un contrat."""
    toxic_clauses = [clause for clause in analysis.clauses if clause.conclusion == "toxique"]
    if not toxic_clauses:
        return "aucune"
    levels = ["faible", "moyen", "eleve", "critique"]
    max_level = max((clause.niveau_toxicite for clause in toxic_clauses), key=lambda item: levels.index(item))
    return max_level


def score_contract(analysis: ContractAnalysis) -> float:
    """Calcule un score simple basé sur la présence de clauses toxiques."""
    return round(len(analysis.toxic_clauses) / max(len(analysis.clauses), 1), 2)
