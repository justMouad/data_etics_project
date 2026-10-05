"""Utilitaires de conversion de documents pour l'analyse de contrats."""

from __future__ import annotations

from pathlib import Path


def convert_documents(source_dir: str | Path, output_dir: str | Path) -> None:
    """Prépare la structure de sortie des documents convertis."""
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for file_path in sorted(source_path.glob("*")):
        if file_path.is_file():
            destination = output_path / file_path.name
            destination.write_bytes(file_path.read_bytes())


if __name__ == "__main__":
    raise SystemExit("Ce script est un scaffold. Ajouter les conversions PDF/DOCX dans une version de production.")
