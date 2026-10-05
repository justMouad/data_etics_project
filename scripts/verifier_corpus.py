"""Vérifie le corpus et complète les champs dérivés des annotations.

Usage (depuis la racine etics-contrats) :
    python scripts/verifier_corpus.py            # vérifie seulement
    python scripts/verifier_corpus.py --ecrire   # vérifie ET complète les JSON
"""
import json
import re
import sys
from pathlib import Path

CONTRATS = Path("data/contrats")
VERITE = Path("data/verite_terrain")

CATEGORIES = {"DESEQUILIBRE", "OPACITE", "DISCRIMINATION", "VIE_PRIVEE",
              "VULNERABILITE", "RENONCIATION_DROITS", "HARCELEMENT_MENACE", "ILLEGAL"}
NIVEAUX = ["faible", "moyen", "eleve", "critique"]  # du moins au plus grave


def normaliser(texte: str) -> str:
    """Neutralise les différences sans importance (apostrophes, espaces, sauts de ligne)."""
    texte = texte.replace("\u2019", "'").replace("\u2018", "'")
    texte = texte.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", texte).strip()


def verifier(cid: str, ecrire: bool) -> bool:
    chemin_contrat = next(CONTRATS.glob(f"{cid}.*"), None)
    chemin_json = VERITE / f"{cid}.json"
    erreurs, alertes = [], []

    if chemin_contrat is None:
        print(f"[!!] {cid} : contrat introuvable")
        return False

    contrat = normaliser(chemin_contrat.read_text(encoding="utf-8"))
    try:
        data = json.loads(chemin_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[!!] {cid} : JSON invalide ({e})")
        return False

    clauses = data.get("clauses", [])

    for i, c in enumerate(clauses, start=1):
        extrait = normaliser(c.get("texte_exact", ""))
        if not extrait:
            erreurs.append(f"clause {i} : texte_exact vide")
        elif extrait not in contrat:
            erreurs.append(f"clause {i} ({c.get('article')}) : texte_exact INTROUVABLE dans le contrat")
        else:
            c["position"] = contrat.index(extrait) + 1
        if c.get("categorie") not in CATEGORIES:
            erreurs.append(f"clause {i} : catégorie invalide '{c.get('categorie')}'")
        if c.get("niveau_toxicite") not in NIVEAUX:
            erreurs.append(f"clause {i} : niveau invalide '{c.get('niveau_toxicite')}'")
        if len(c.get("justification", "")) < 10:
            alertes.append(f"clause {i} : justification très courte")
        c["clause_id"] = f"{cid}-C{i}"

    # Champs dérivés
    niveaux = [c["niveau_toxicite"] for c in clauses if c.get("niveau_toxicite") in NIVEAUX]
    data["contrat_id"] = cid
    data["presence_toxicite"] = len(clauses) > 0
    data["niveau_toxicite"] = max(niveaux, key=NIVEAUX.index) if niveaux else "aucune"
    data["categorie_toxicite"] = sorted({c["categorie"] for c in clauses if c.get("categorie") in CATEGORIES})
    data.setdefault("source", "hybride")
    data.setdefault("version_schema", "1.0")

    if ecrire and not erreurs:
        chemin_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    statut = "OK" if not erreurs else "ERREUR"
    print(f"[{statut}] {cid} : {len(clauses)} clause(s), niveau doc = {data['niveau_toxicite']}")
    for e in erreurs:
        print(f"      - {e}")
    for a in alertes:
        print(f"      ~ {a}")
    return not erreurs


def main():
    ecrire = "--ecrire" in sys.argv
    ids = sorted(p.stem for p in VERITE.glob("CT-*.json") if "INVALIDE" not in p.name)
    if not ids:
        sys.exit("Aucune annotation dans data/verite_terrain/")
    resultats = [verifier(cid, ecrire) for cid in ids]
    print(f"\n{sum(resultats)}/{len(resultats)} contrat(s) valide(s)"
          + ("  (JSON complétés)" if ecrire else "  (rien n'a été modifié, utilisez --ecrire)"))


if __name__ == "__main__":
    main()