"""
API FastAPI : sert l'interface web et répond aux questions via le pipeline RAG.

Lancement (depuis la racine du projet) :
    uv run uvicorn app.main:app --reload
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import BASE_DIR, CHROMA_DIR
from app.rag import load_vectorstore, ask

app = FastAPI(title="Assistant RAG Entreprise")

# Fichiers statiques (CSS) et templates (HTML)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# La base vectorielle est chargée UNE SEULE FOIS au démarrage du serveur
# (et non à chaque question) pour que l'API reste rapide.
vectorstore = None


@app.on_event("startup")
def startup_event():
    global vectorstore
    if not CHROMA_DIR.exists():
        raise RuntimeError(
            "Aucune base vectorielle trouvée. Lancez d'abord : uv run python -m app.ingest"
        )
    vectorstore = load_vectorstore()
    print("Base vectorielle chargée, API prête.")


class Question(BaseModel):
    question: str


@app.get("/")
def home(request: Request):
    """Affiche la page d'accueil (le chat)."""
    return templates.TemplateResponse(request, "index.html", {})


@app.post("/ask")
def ask_question(payload: Question):
    """Reçoit une question, interroge le RAG, renvoie la réponse + les sources."""
    answer, sources = ask(payload.question, vectorstore)
    return {"answer": answer, "sources": sources}
