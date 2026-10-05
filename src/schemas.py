"""Schémas Pydantic pour le projet etics-contrats."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ContractParty(BaseModel):
    """Représente une partie du contrat."""

    role: str = Field(..., description="Rôle de la partie dans le contrat, par exemple employeur ou salarié")
    nom: str = Field(..., min_length=1)
    type_partie: str | None = None


class ContractMetadata(BaseModel):
    """Métadonnées générales du contrat."""

    titre: str = Field(..., min_length=1)
    date_signature: str | None = None
    type_contrat: str = Field(..., min_length=1)
    pays: str | None = None
    secteur: str | None = None
    source: str | None = None


class ClauseExtraction(BaseModel):
    """Clause individuelle détectée dans un contrat."""

    clause_id: str = Field(..., min_length=1)
    categorie: str = Field(..., min_length=1)
    texte_exact: str = Field(..., min_length=1)
    conclusion: Literal["toxique", "non_toxique"]
    niveau_toxicite: Literal["faible", "moyen", "eleve", "critique", "non_applicable"]
    justification: str = Field(..., min_length=10)
    article: str = Field(..., min_length=1)
    position: int = Field(..., ge=1)
    confiance: float = Field(..., ge=0.0, le=1.0)


class ContractAnalysis(BaseModel):
    """Résultat cohérent d'analyse d'un contrat."""

    contrat_id: str = Field(..., min_length=1)
    metadata: ContractMetadata
    parties: list[ContractParty] = Field(default_factory=list)
    clauses: list[ClauseExtraction] = Field(default_factory=list)
    categorie_toxicite: list[str] = Field(default_factory=list)
    presence_toxicite: bool = False
    niveau_toxicite: Literal["aucune", "faible", "moyen", "eleve", "critique"] = "aucune"
    source: Literal["manual", "llm", "hybride"] = "manual"
    version_schema: str = Field(default="0.1.0")

    @property
    def toxic_clauses(self) -> list[ClauseExtraction]:
        return [clause for clause in self.clauses if clause.conclusion == "toxique"]
