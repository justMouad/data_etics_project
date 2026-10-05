CREATE TABLE IF NOT EXISTS documents (
    contrat_id                     TEXT PRIMARY KEY,
    titre                          TEXT,
    date_signature                 DATE,
    type_contrat                   TEXT CHECK (type_contrat IN ('CDI','CDD','INTERIM','STAGE','ALTERNANCE')),
    statut                         TEXT CHECK (statut IN ('cadre','non_cadre')),
    secteur                        TEXT,
    employeur                      TEXT,
    salarie                        TEXT,
    fonction                       TEXT,
    date_debut                     DATE,
    date_fin                       DATE,
    periode_essai_mois             NUMERIC,
    lieu_travail                   TEXT,
    clause_mobilite                BOOLEAN,
    duree_travail                  TEXT,
    remuneration_brute_annuelle    NUMERIC,
    remuneration_variable_presente BOOLEAN,
    convention_collective          TEXT,
    clause_non_concurrence         BOOLEAN,
    non_concurrence_duree_mois     NUMERIC,
    non_concurrence_contrepartie   BOOLEAN,
    clause_exclusivite             BOOLEAN,
    preavis                        TEXT,
    presence_toxicite              BOOLEAN NOT NULL,
    niveau_toxicite                TEXT NOT NULL
        CHECK (niveau_toxicite IN ('aucune','faible','moyen','eleve','critique')),
    categories_toxicite            TEXT[] NOT NULL DEFAULT '{}',
    source                         TEXT CHECK (source IN ('manual','llm','hybride')),
    version_schema                 TEXT,
    date_extraction                TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS clauses_toxiques (
    clause_id        TEXT PRIMARY KEY,
    contrat_id       TEXT NOT NULL REFERENCES documents(contrat_id) ON DELETE CASCADE,
    article          TEXT,
    position         INTEGER,
    categorie        TEXT NOT NULL CHECK (categorie IN (
        'DESEQUILIBRE','OPACITE','DISCRIMINATION','VIE_PRIVEE',
        'VULNERABILITE','RENONCIATION_DROITS','HARCELEMENT_MENACE','ILLEGAL')),
    texte_exact      TEXT NOT NULL,
    niveau_toxicite  TEXT NOT NULL CHECK (niveau_toxicite IN ('faible','moyen','eleve','critique')),
    justification    TEXT,
    confiance        NUMERIC CHECK (confiance BETWEEN 0 AND 1)
);

CREATE INDEX IF NOT EXISTS idx_clauses_contrat   ON clauses_toxiques(contrat_id);
CREATE INDEX IF NOT EXISTS idx_clauses_categorie ON clauses_toxiques(categorie);