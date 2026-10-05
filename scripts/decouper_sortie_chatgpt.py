"""Découpe une sortie ChatGPT (contrat + annotation) en deux fichiers.

Usage (depuis la racine etics-contrats) :
    python scripts/decouper_sortie_chatgpt.py data/brut/corpus_initial.txt CT-001 CT-002 CT-003

Les IDs doivent être donnés dans l'ordre d'apparition des contrats dans le fichier.
Le fichier source doit contenir les balises <CONTRAT>...</CONTRAT>
et <ANNOTATION>...</ANNOTATION>.
"""
import json
import re
import sys
from pathlib import Path

CONTRATS = Path("data/contrats")
VERITE = Path("data/verite_terrain")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)

    source = Path(sys.argv[1])
    ids = sys.argv[2:]

    if not source.exists():
        sys.exit(f"Fichier introuvable : {source}")

    texte = source.read_text(encoding="utf-8")

    contrats = re.findall(r"<CONTRAT>(.*?)</CONTRAT>", texte, flags=re.S)
    annotations = re.findall(r"<ANNOTATION>(.*?)</ANNOTATION>", texte, flags=re.S)

    print(f"{len(contrats)} contrat(s) et {len(annotations)} annotation(s) trouvé(s).")

    if len(contrats) != len(ids):
        sys.exit(
            f"Erreur : {len(contrats)} contrat(s) trouvé(s) mais {len(ids)} ID donné(s). "
            "Vérifiez les balises <CONTRAT> dans le fichier source."
        )

    CONTRATS.mkdir(parents=True, exist_ok=True)
    VERITE.mkdir(parents=True, exist_ok=True)

    for i, cid in enumerate(ids):
        (CONTRATS / f"{cid}.txt").write_text(contrats[i].strip() + "\n", encoding="utf-8")
        print(f"[ok] {cid}.txt écrit")

        if i >= len(annotations):
            print(f"[!!] {cid} : pas d'annotation trouvée")
            continue

        brut = annotations[i].strip()
        try:
            json.loads(brut)
            (VERITE / f"{cid}.json").write_text(brut + "\n", encoding="utf-8")
            print(f"[ok] {cid}.json valide")
        except json.JSONDecodeError as e:
            (VERITE / f"{cid}.INVALIDE.json").write_text(brut + "\n", encoding="utf-8")
            print(f"[!!] {cid} : JSON invalide ({e}). Sauvé en {cid}.INVALIDE.json, à corriger.")


if __name__ == "__main__":
    main()