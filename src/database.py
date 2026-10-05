import json
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

JSON_DIR = Path("resultats/json")
SCHEMA_SQL = Path("sql/schema.sql")


def connecter():
    """Ouvre la connexion à PostgreSQL à partir des variables PG* du fichier .env."""
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "etics"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD"),
    )


def creer_tables(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL.read_text(encoding="utf-8"))
    conn.commit()


def inserer(conn, r: dict) -> None:
    """Insère (ou remplace) un résultat d'analyse et ses clauses."""
    meta = r.get("metadata") or {}
    ext = r.get("extraction") or {}
    parties = {p.get("role"): p.get("nom") for p in (r.get("parties") or [])}
    cid = r["contrat_id"]

    with conn.cursor() as cur:
        # Rejouable sans doublons : la suppression du document supprime ses clauses (CASCADE)
        cur.execute("DELETE FROM documents WHERE contrat_id = %s", (cid,))

        cur.execute(
            """
            INSERT INTO documents (
                contrat_id, titre, date_signature, type_contrat, statut, secteur,
                employeur, salarie, fonction, date_debut, date_fin, periode_essai_mois,
                lieu_travail, clause_mobilite, duree_travail, remuneration_brute_annuelle,
                remuneration_variable_presente, convention_collective, clause_non_concurrence,
                non_concurrence_duree_mois, non_concurrence_contrepartie, clause_exclusivite,
                preavis, presence_toxicite, niveau_toxicite, categories_toxicite,
                source, version_schema
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                cid, meta.get("titre"), meta.get("date_signature"), meta.get("type_contrat"),
                meta.get("statut"), meta.get("secteur"),
                parties.get("employeur"), parties.get("salarie"),
                ext.get("fonction"), ext.get("date_debut"), ext.get("date_fin"),
                ext.get("periode_essai_mois"), ext.get("lieu_travail"), ext.get("clause_mobilite"),
                ext.get("duree_travail"), ext.get("remuneration_brute_annuelle"),
                ext.get("remuneration_variable_presente"), ext.get("convention_collective"),
                ext.get("clause_non_concurrence"), ext.get("non_concurrence_duree_mois"),
                ext.get("non_concurrence_contrepartie"), ext.get("clause_exclusivite"),
                ext.get("preavis"),
                r["presence_toxicite"], r["niveau_toxicite"], r.get("categorie_toxicite", []),
                r.get("source"), r.get("version_schema"),
            ),
        )

        for c in r.get("clauses", []):
            cur.execute(
                """
                INSERT INTO clauses_toxiques
                    (clause_id, contrat_id, article, position, categorie,
                     texte_exact, niveau_toxicite, justification, confiance)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (c["clause_id"], cid, c.get("article"), c.get("position"), c["categorie"],
                 c["texte_exact"], c["niveau_toxicite"], c.get("justification"), c.get("confiance")),
            )


def charger_tout() -> None:
    fichiers = sorted(JSON_DIR.glob("CT-*.json"))
    if not fichiers:
        sys.exit("Aucun résultat dans resultats/json/. Lancez d'abord src.extraction.")

    conn = connecter()
    try:
        creer_tables(conn)
        for f in fichiers:
            r = json.loads(f.read_text(encoding="utf-8"))
            try:
                inserer(conn, r)
                conn.commit()
                print(f"[ok] {f.stem} : {len(r.get('clauses', []))} clause(s) chargée(s)")
            except Exception as e:
                conn.rollback()
                print(f"[!!] {f.stem} : {e}")
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM documents")
            nb_doc = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM clauses_toxiques")
            nb_cl = cur.fetchone()[0]
        print(f"\nBase PostgreSQL : {nb_doc} document(s), {nb_cl} clause(s)")
    finally:
        conn.close()


if __name__ == "__main__":
    charger_tout()