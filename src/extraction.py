import json
import re
import sys
from pathlib import Path

from src.ingestion import lire_document
from src.llm_client import appeler_llm

PROMPT = Path("prompts/extraction.txt")
SORTIE = Path("resultats/json")

CATEGORIES = {"DESEQUILIBRE", "OPACITE", "DISCRIMINATION", "VIE_PRIVEE",
              "VULNERABILITE", "RENONCIATION_DROITS", "HARCELEMENT_MENACE", "ILLEGAL"}
NIVEAUX = ["faible", "moyen", "eleve", "critique"]
CHAMPS = ["metadata", "parties", "extraction", "clauses"]


def normaliser(texte: str) -> str:
    texte = texte.replace("\u2019", "'").replace("\u2018", "'").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", texte).strip()


def valider(data: dict, texte_contrat: str) -> list[str]:
    """Renvoie la liste des erreurs (vide si la sortie est correcte)."""
    erreurs = []
    for champ in CHAMPS:
        if champ not in data:
            erreurs.append(f"champ manquant : {champ}")
    if erreurs:
        return erreurs

    contrat = normaliser(texte_contrat)
    for i, c in enumerate(data["clauses"], start=1):
        if c.get("categorie") not in CATEGORIES:
            erreurs.append(f"clause {i} : catégorie invalide '{c.get('categorie')}'")
        if c.get("niveau_toxicite") not in NIVEAUX:
            erreurs.append(f"clause {i} : niveau invalide '{c.get('niveau_toxicite')}'")
        extrait = normaliser(c.get("texte_exact") or "")
        if not extrait or extrait not in contrat:
            erreurs.append(f"clause {i} : texte_exact absent du contrat (doit être copié mot pour mot)")
        if not isinstance(c.get("confiance"), (int, float)):
            erreurs.append(f"clause {i} : confiance doit être un nombre")
    return erreurs


def finaliser(data: dict, cid: str, texte_contrat: str) -> dict:
    """Ajoute les champs dérivés et administratifs (calculés par le code, pas par le LLM)."""
    contrat = normaliser(texte_contrat)
    clauses = data["clauses"]
    for i, c in enumerate(clauses, start=1):
        c["clause_id"] = f"{cid}-C{i}"
        c["position"] = contrat.index(normaliser(c["texte_exact"])) + 1
    niveaux = [c["niveau_toxicite"] for c in clauses]
    data["contrat_id"] = cid
    data["presence_toxicite"] = len(clauses) > 0
    data["niveau_toxicite"] = max(niveaux, key=NIVEAUX.index) if niveaux else "aucune"
    data["categorie_toxicite"] = sorted({c["categorie"] for c in clauses})
    data["source"] = "llm"
    data["version_schema"] = "1.0"
    return data


def analyser(chemin, essais: int = 3) -> dict:
    chemin = Path(chemin)
    cid = chemin.stem
    texte = lire_document(chemin)
    systeme = PROMPT.read_text(encoding="utf-8")
    message = f"Voici le contrat à analyser :\n\n{texte}"

    erreurs_prec: list[str] = []
    for n in range(1, essais + 1):
        utilisateur = message
        if erreurs_prec:
            utilisateur += ("\n\nTa réponse précédente contenait ces erreurs, corrige-les :\n- "
                            + "\n- ".join(erreurs_prec))
        brut = appeler_llm(systeme, utilisateur)
        try:
            data = json.loads(brut)
        except json.JSONDecodeError as e:
            erreurs_prec = [f"JSON invalide : {e}"]
            print(f"   essai {n} : {erreurs_prec[0]}")
            continue
        erreurs_prec = valider(data, texte)
        if not erreurs_prec:
            return finaliser(data, cid, texte)
        print(f"   essai {n} : {len(erreurs_prec)} erreur(s) -> nouvel essai")

    raise ValueError(f"{cid} : échec après {essais} essais. Dernières erreurs : {erreurs_prec}")


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage : python -m src.extraction data/contrats/CT-001.txt [autres fichiers]")
    SORTIE.mkdir(parents=True, exist_ok=True)
    for chemin in sys.argv[1:]:
        print(f"Analyse de {chemin}...")
        try:
            resultat = analyser(chemin)
        except Exception as e:
            print(f"[!!] {e}")
            continue
        sortie = SORTIE / f"{Path(chemin).stem}.json"
        sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[ok] {sortie} : {len(resultat['clauses'])} clause(s), niveau = {resultat['niveau_toxicite']}")


if __name__ == "__main__":
    main()