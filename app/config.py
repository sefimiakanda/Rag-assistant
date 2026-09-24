"""
Configuration centrale du projet.
Toutes les valeurs "en dur" (noms de modèles, chemins, tailles de chunks)
sont regroupées ici pour être faciles à modifier sans toucher au reste du code.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # charge les variables depuis un fichier .env si présent

# --- Chemins ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

# --- Modèles Ollama (100 % gratuits, tournent en local ou sur votre serveur) ---
# Modèle de génération : choisi pour tourner confortablement sur 16 Go de RAM (CPU).
# Alternatives si votre machine/serveur le permet : "qwen2.5:7b-instruct", "phi3.5:3.8b"
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
# Modèle d'embeddings : léger, dédié à la recherche sémantique
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# Adresse du service Ollama. En local : http://localhost:11434 (valeur par défaut).
# En déploiement Docker (voir docker-compose.yml) : http://ollama:11434
# (le nom "ollama" est celui du service dans docker-compose.yml, résolu automatiquement).
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# --- Paramètres RAG ---
CHUNK_SIZE = 1000        # taille d'un morceau de texte (en caractères)
CHUNK_OVERLAP = 150      # chevauchement entre deux morceaux consécutifs
TOP_K = 4                # nombre de morceaux renvoyés par la recherche
