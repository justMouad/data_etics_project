from src.schemas import ClauseExtraction, ContractAnalysis, ContractMetadata, ContractParty


def test_contract_analysis_accepts_multiple_clauses():
    metadata = ContractMetadata(
        titre="Contrat fictif",
        date_signature="2025-01-01",
        type_contrat="CDD",
        pays="France",
        secteur="Technologie",
        source="manual",
    )

    analysis = ContractAnalysis(
        contrat_id="contrat_001",
        metadata=metadata,
        parties=[
            ContractParty(role="employeur", nom="Alpha SAS", type_partie="entreprise"),
            ContractParty(role="salarié", nom="Jean Test", type_partie="personne"),
        ],
        clauses=[
            ClauseExtraction(
                clause_id="c1",
                categorie="Sanctions abusives",
                texte_exact="Tout salarié qui conteste la décision de l'employeur est sanctionné sans procédure.",
                conclusion="toxique",
                niveau_toxicite="eleve",
                justification="Clause potentiellement intimidante et non cadrée.",
                article="Article 7",
                position=1,
                confiance=0.9,
            ),
            ClauseExtraction(
                clause_id="c2",
                categorie="Confidentialite",
                texte_exact="Le salarié accepte la surveillance des communications personnelles dans le cadre de son activité.",
                conclusion="non_toxique",
                niveau_toxicite="non_applicable",
                justification="Clause encadrée et conforme au cadre de recherche du projet.",
                article="Article 11",
                position=2,
                confiance=0.8,
            ),
        ],
    )

    assert analysis.contrat_id == "contrat_001"
    assert len(analysis.clauses) == 2
    assert analysis.toxic_clauses[0].clause_id == "c1"
