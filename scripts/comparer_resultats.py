"""Compare les résultats du système avec la vérité terrain.

Usage (depuis la racine etics-contrats) :
    python scripts/comparer_resultats.py
Produit resultats/erreurs.csv et resultats/metriques.csv.
"""
import csv
import json
import re
from pathlib import Path

RESULTATS = Path("resultats/json")
VERITE = Path("data/verite_terrain")
SORTIE = Path("resultats")


def norm(t) -> str:
    t = str(t or "").lower().replace("\u2019", "'").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", t).strip()


def similaire(a: str, b: str) -> bool:
    """Deux extraits désignent la même clause s'ils se contiennent ou se recouvrent fortement."""
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    ta, tb = set(a.split()), set(b.split())
    return len(ta & tb) / len(ta | tb) >= 0.6


def comparer(cid: str, pred: dict, ref: dict, erreurs: list) -> dict:
    p_clauses = list(pred.get("clauses", []))
    r_clauses = list(ref.get("clauses", []))
    non_appariees = p_clauses.copy()
    tp = cat_ok = niv_ok = 0

    for r in r_clauses:
        trouve = next((p for p in non_appariees if similaire(p["texte_exact"], r["texte_exact"])), None)
        if trouve is None:
            erreurs.append([cid, "FAUX_NEGATIF", r.get("article"), r.get("categorie"),
                            "clause attendue non détectée : " + r["texte_exact"][:80]])
            continue
        non_appariees.remove(trouve)
        tp += 1
        if trouve["categorie"] == r["categorie"]:
            cat_ok += 1
        else:
            erreurs.append([cid, "CATEGORIE", r.get("article"), r.get("categorie"),
                            f"attendu {r['categorie']}, obtenu {trouve['categorie']}"])
        if trouve["niveau_toxicite"] == r["niveau_toxicite"]:
            niv_ok += 1
        else:
            erreurs.append([cid, "NIVEAU", r.get("article"), r.get("categorie"),
                            f"attendu {r['niveau_toxicite']}, obtenu {trouve['niveau_toxicite']}"])

    for p in non_appariees:
        erreurs.append([cid, "FAUX_POSITIF", p.get("article"), p.get("categorie"),
                        "clause en plus : " + p["texte_exact"][:80]])

    ref_present = len(r_clauses) > 0
    pred_present = len(p_clauses) > 0
    ref_niveau = ref.get("niveau_toxicite", "aucune")
    return {
        "cid": cid, "tp": tp, "fp": len(non_appariees), "fn": len(r_clauses) - tp,
        "cat_ok": cat_ok, "niv_ok": niv_ok,
        "doc_present_ok": ref_present == pred_present,
        "doc_niveau_ok": ref_niveau == pred.get("niveau_toxicite"),
    }


def main():
    erreurs, lignes = [], []
    for f in sorted(RESULTATS.glob("CT-*.json")):
        cid = f.stem
        ref_path = VERITE / f"{cid}.json"
        if not ref_path.exists():
            print(f"[skip] {cid} : pas de vérité terrain")
            continue
        pred = json.loads(f.read_text(encoding="utf-8"))
        ref = json.loads(ref_path.read_text(encoding="utf-8"))
        lignes.append(comparer(cid, pred, ref, erreurs))

    if not lignes:
        raise SystemExit("Aucun résultat à comparer dans resultats/json/")

    print(f"{'contrat':8} {'TP':>3} {'FP':>3} {'FN':>3} {'cat':>5} {'niv':>5}  doc_toxique  doc_niveau")
    for l in lignes:
        print(f"{l['cid']:8} {l['tp']:>3} {l['fp']:>3} {l['fn']:>3} "
              f"{l['cat_ok']:>2}/{l['tp']:<2} {l['niv_ok']:>2}/{l['tp']:<2}  "
              f"{'ok' if l['doc_present_ok'] else 'ERREUR':>11}  {'ok' if l['doc_niveau_ok'] else 'ERREUR':>10}")

    tp = sum(l["tp"] for l in lignes)
    fp = sum(l["fp"] for l in lignes)
    fn = sum(l["fn"] for l in lignes)
    precision = tp / (tp + fp) if tp + fp else 0.0
    rappel = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * rappel / (precision + rappel) if precision + rappel else 0.0
    n = len(lignes)
    acc_doc = sum(l["doc_present_ok"] for l in lignes) / n
    acc_niv = sum(l["doc_niveau_ok"] for l in lignes) / n
    print(f"\nClauses : précision {precision:.2f} | rappel {rappel:.2f} | F1 {f1:.2f}  ({n} contrat(s))")
    print(f"Document toxique oui/non : {acc_doc:.0%} | niveau du document : {acc_niv:.0%}")

    SORTIE.mkdir(exist_ok=True)
    with open(SORTIE / "erreurs.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["contrat", "type_erreur", "article", "categorie", "detail"])
        w.writerows(erreurs)
    with open(SORTIE / "metriques.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["contrats", "tp", "fp", "fn", "precision", "rappel", "f1", "acc_doc", "acc_niveau_doc"])
        w.writerow([n, tp, fp, fn, round(precision, 3), round(rappel, 3), round(f1, 3),
                    round(acc_doc, 3), round(acc_niv, 3)])
    print(f"{len(erreurs)} désaccord(s) écrit(s) dans resultats/erreurs.csv")


if __name__ == "__main__":
    main()