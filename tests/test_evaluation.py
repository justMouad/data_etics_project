from src.evaluation import classify_contract_toxicity, score_contract
from src.schemas import ClauseExtraction, ContractAnalysis, ContractMetadata


def test_classify_contract_toxicity_and_score():
    metadata = ContractMetadata(
        titre="Contrat de test",
        date_signature="2025-01-02",
        type_contrat="CDI",
        pays="France",
        secteur="Marketing",
        source="manual",
    )

    analysis = ContractAnalysis(
        contrat_id="contrat_002",
        metadata=metadata,
        clauses=[
            ClauseExtraction(
                clause_id="c1",
                categorie="Discrimination",
                texte_exact="Nous ne recrutons que des candidats de moins de 30 ans.",
                conclusion="toxique",
                niveau_toxicite="eleve",
                justification="Clause discriminatoire potentiellement problématique.",
                article="Article 3",
                position=1,
                confiance=0.95,
            ),
            ClauseExtraction(
                clause_id="c2",
                categorie="Confidentialite",
                texte_exact="Les données professionnelles sont conservées selon le cadre interne.",
                conclusion="non_toxique",
                niveau_toxicite="non_applicable",
                justification="Clause non toxique selon le projet.",
                article="Article 9",
                position=2,
                confiance=0.7,
            ),
        ],
    )

    assert classify_contract_toxicity(analysis) == "eleve"
    assert score_contract(analysis) == 0.5
