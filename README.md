# Assistant RAG Entreprise — 100% local et gratuit

Assistant question/réponse basé sur un document PDF interne, utilisant
uniquement des modèles open source servis en local via Ollama (aucun crédit API à dépenser).

## Stack
- **LLM** : `llama3.2:3b` (via Ollama)
- **Embeddings** : `nomic-embed-text` (via Ollama)
- **Base vectorielle** : Chroma (locale, persistée sur disque)
- **Backend** : FastAPI
- **Frontend** : HTML/CSS + JS vanilla (`templates/index.html`, `static/style.css`)
- **Env. virtuel** : uv

## 1. Installer Ollama et les modèles
Téléchargez Ollama sur https://ollama.com, puis :
```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

## 2. Installer les dépendances Python avec uv
Depuis la racine du projet :
```bash
uv sync
```
(ou `uv add <package>` si vous ajoutez des dépendances au fur et à mesure)

## 3. Explorer le pipeline 
Ouvrez `notebook_rag.ipynb` dans VS Code pour comprendre chaque étape du RAG.

## 4. Ajouter votre document
Placez le PDF de l'entreprise dans `data/`.

## 5. Indexer le document
```bash
uv run python -m app.ingest
```

## 6. Lancer l'API
```bash
uv run uvicorn app.main:app --reload
```
Ouvrez http://127.0.0.1:8000 dans votre navigateur.

## Structure du projet
```
rag-assistant/
├── app/
│   ├── config.py      # paramètres centraux (modèles, chunking, chemins)
│   ├── rag.py          # logique RAG (chargement, index, recherche, génération)
│   ├── ingest.py        # script d'indexation du PDF (à lancer une fois)
│   └── main.py           # API FastAPI
├── templates/
│   └── index.html         # interface chat
├── static/
│   └── style.css           # style de l'interface
├── data/                    # placez votre PDF ici
├── notebook_rag.py            # notebook d'exploration commenté
├── pyproject.toml
└── README.md
```

## Déployer pour toute l'entreprise (accès web)

Le fait que le LLM tourne "en local" ne veut pas dire qu'il doit rester sur
le PC : la même stack peut tourner sur un serveur (interne ou cloud) et
être accessible depuis un navigateur, par plusieurs employés.

1. **Installez Docker** sur le serveur (interne ou VPS cloud : OVH, Hetzner,
   Scaleway, AWS...).
2. **Copiez le projet** sur le serveur (git clone, scp, etc.), avec votre
   PDF dans `data/`.
3. **Lancez tout** :
   ```bash
   docker compose up -d --build
   ```
   Cela démarre 3 conteneurs : `ollama` (le LLM), `app` (l'API RAG),
   `nginx` (le reverse proxy exposé sur le port 80).
4. **Téléchargez les modèles dans le conteneur Ollama** (une seule fois) :
   ```bash
   docker compose exec ollama ollama pull llama3.2:3b
   docker compose exec ollama ollama pull nomic-embed-text
   ```
5. **Indexez le PDF** :
   ```bash
   docker compose exec app python -m app.ingest
   ```
6. **Accédez à l'assistant** via `http://<ip-du-serveur>` (ou votre nom de
   domaine une fois configuré dans `nginx/nginx.conf`).

### Sécurité (important pour un usage entreprise)
- Activez HTTPS via Certbot (instructions dans `nginx/nginx.conf`).
- Ajoutez une authentification devant l'app (ex. `python-jose` + login, ou
  une authentification basique au niveau nginx avec `auth_basic`) pour
  éviter que n'importe qui sur Internet interroge vos documents internes.
- Si l'assistant n'a besoin d'être accessible que par les employés,
  préférez un déploiement sur le réseau interne ou derrière un VPN plutôt
  que de l'exposer publiquement.

## Pour aller plus loin
- Modèle plus puissant si votre machine le permet : `qwen2.5:7b-instruct`
  (changez `LLM_MODEL` dans `app/config.py` ou via une variable d'env)
- Plusieurs PDF : adaptez `app/ingest.py` pour boucler sur tous les fichiers
  de `data/` au lieu du premier trouvé
- Déploiement : conteneuriser avec Docker (Ollama + FastAPI dans des
  services séparés) pour mettre en production sur un serveur interne
