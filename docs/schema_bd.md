# Schéma de base de données locale

La base SQLite locale est stockée dans `data/db/etics.sqlite`.

## Tables prévues

- `contracts` : informations sur les contrats ingérés.
- `clauses` : clauses détectées ou annotées.

## Utilisation

Le module `src/database.py` établit la structure minimale, qui peut ensuite être enrichie selon les besoins du projet.
