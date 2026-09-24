"""
Coeur de la logique RAG : lecture du PDF, découpage, indexation,
recherche et génération de réponse.

Ce module est le même que celui exploré dans notebook_rag.py, mais
organisé en fonctions réutilisables, appelées par l'API FastAPI (main.py)
et par le script d'indexation (ingest.py).
"""
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.config import (
    CHROMA_DIR, EMBEDDING_MODEL, LLM_MODEL, OLLAMA_BASE_URL,
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K,
)

# ---------------------------------------------------------------------------
# 1. Chargement + découpage du PDF
# ---------------------------------------------------------------------------
def load_and_split_pdf(pdf_path: str) -> List[Document]:
    """Lit un PDF et le découpe en petits morceaux ("chunks")."""
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()  # une Document par page, avec metadata (source, page)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(pages)


# ---------------------------------------------------------------------------
# 2. Construction / chargement de la base vectorielle (Chroma)
# ---------------------------------------------------------------------------
def get_embeddings() -> OllamaEmbeddings:
    # base_url permet de pointer vers Ollama en local OU vers un conteneur/serveur distant
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)


def build_vectorstore(chunks: List[Document]) -> Chroma:
    """Crée une nouvelle base vectorielle à partir des chunks et la sauvegarde sur disque."""
    return Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )


def load_vectorstore() -> Chroma:
    """Recharge une base vectorielle déjà construite (utilisé par l'API en production)."""
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
    )


# ---------------------------------------------------------------------------
# 3. Chaîne RAG : retrieval + prompt + LLM
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """Tu es l'assistant interne d'une entreprise technologique.
Réponds à la question UNIQUEMENT à partir du contexte fourni ci-dessous.
Si l'information ne figure pas dans le contexte, dis clairement que tu ne sais pas.
Réponds en français, de façon claire et concise.

Contexte :
{context}

Question : {question}

Réponse :"""


def format_docs(docs: List[Document]) -> str:
    """Concatène les chunks récupérés en un seul bloc de texte pour le prompt."""
    return "\n\n".join(doc.page_content for doc in docs)


def build_chain(vectorstore: Chroma):
    """Assemble le pipeline complet : retriever -> prompt -> LLM -> texte."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatOllama(model=LLM_MODEL, temperature=0.2, base_url=OLLAMA_BASE_URL)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def ask(question: str, vectorstore: Chroma) -> Tuple[str, List[dict]]:
    """Pose une question au RAG et renvoie la réponse + les sources utilisées."""
    chain, retriever = build_chain(vectorstore)
    answer = chain.invoke(question)
    sources_docs = retriever.invoke(question)
    sources = [
        {
            "page": doc.metadata.get("page", "?"),
            "extrait": doc.page_content[:150] + "...",
        }
        for doc in sources_docs
    ]
    return answer, sources
