FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances (via uv, plus rapide que pip)
COPY pyproject.toml .
RUN pip install --no-cache-dir uv \
    && uv pip install --system --no-cache -r pyproject.toml

# Copie du code de l'application
COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
