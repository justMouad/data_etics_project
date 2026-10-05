from pathlib import Path

import pdfplumber
from docx import Document


def lire_document(chemin) -> str:
    """Lit un contrat (.txt, .pdf, .docx) et renvoie son texte brut."""
    chemin = Path(chemin)
    suffixe = chemin.suffix.lower()

    if suffixe == ".txt":
        return chemin.read_text(encoding="utf-8")

    if suffixe == ".pdf":
        with pdfplumber.open(chemin) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    if suffixe == ".docx":
        doc = Document(chemin)
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError(f"Format non géré : {suffixe}")