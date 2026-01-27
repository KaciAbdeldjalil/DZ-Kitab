FROM python:3.11-slim

WORKDIR /app

# Copier uniquement requirements pour profiter du cache Docker
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Commande par daut
# Railway use dynamic port, so we use shell format or a script
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
