import sys
from pathlib import Path
import pdfplumber

if len(sys.argv) < 2:
    sys.exit("Usage : python scripts/pdf_vers_txt.py chemin/vers/fichier.pdf")

pdf_path = Path(sys.argv[1])
if not pdf_path.exists():
    sys.exit(f"Fichier introuvable : {pdf_path}")

with pdfplumber.open(pdf_path) as pdf:
    texte = "\n".join(page.extract_text() or "" for page in pdf.pages)

sortie = pdf_path.with_suffix(".txt")
sortie.write_text(texte, encoding="utf-8")
print(f"{len(texte)} caractères écrits dans {sortie}")