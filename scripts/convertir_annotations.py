"""Convertit les anciennes annotations vers le schéma ETICS.

Usage (depuis la racine etics-contrats) :
    python scripts/convertir_annotations.py
"""
import json
from pathlib import Path

VERITE = Path("data/verite_terrain")
GRAVITE_VERS_NIVEAU = {1: "faible", 2: "moyen", 3: "eleve"}


def convertir(chemin: Path) -> None:
    data = json.loads(chemin.read_text(encoding="utf-8"))

    if "clauses_toxiques" not in data:
        print(f"[skip] {chemin.name} : déjà au nouveau format")
        return

    nouvelles = []
    for c in data["clauses_toxiques"]:
        nouvelles.append({
            "article": c.get("article", ""),
            "categorie": c.get("categorie"),
            "texte_exact": c.get("texte_exact", ""),
            "niveau_toxicite": GRAVITE_VERS_NIVEAU.get(c.get("gravite"), "moyen"),
            "justification": c.get("justification", ""),
            "confiance": 1.0,
        })

    converti = {
        "contrat_id": chemin.stem,
        "metadata": {
            "titre": None,
            "date_signature": None,
            "type_contrat": data.get("type_contrat"),
            "statut": data.get("statut"),
            "secteur": data.get("secteur"),
        },
        "parties": [],
        "clauses": nouvelles,
    }
    chemin.write_text(json.dumps(converti, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[ok] {chemin.name} converti ({len(nouvelles)} clause(s))")


for f in sorted(VERITE.glob("CT-*.json")):
    if "INVALIDE" not in f.name:
        convertir(f)