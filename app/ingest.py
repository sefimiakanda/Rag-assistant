"""
Script d'indexation : à exécuter UNE FOIS (ou à chaque nouveau PDF)
pour construire la base vectorielle à partir du document de l'entreprise.

Usage (depuis la racine du projet) :
    uv run python -m app.ingest
"""
from app.config import DATA_DIR
from app.rag import load_and_split_pdf, build_vectorstore


def main():
    pdf_files = list(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(
            f"Aucun PDF trouvé dans {DATA_DIR}. Placez-y votre document d'entreprise."
        )

    pdf_path = pdf_files[0]
    print(f"Indexation de : {pdf_path.name}")

    chunks = load_and_split_pdf(str(pdf_path))
    print(f"{len(chunks)} morceaux ('chunks') créés.")

    build_vectorstore(chunks)
    print("Base vectorielle sauvegardée dans chroma_db/. Vous pouvez lancer l'API.")


if __name__ == "__main__":
    main()
