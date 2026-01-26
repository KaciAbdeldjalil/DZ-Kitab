# # app/database.py

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# import os
# from dotenv import load_dotenv

# # Charger les variables d'environnement
# load_dotenv()

# # URL de connexion - Support SQLite par dfaut pour le dveloppement local facile
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dzkitab.db")

# # Crer le moteur SQLAlchemy
# if DATABASE_URL.startswith("sqlite"):
#     engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# else:
#     engine = create_engine(DATABASE_URL)


# # Crer une session locale
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base pour les modles
# Base = declarative_base()

# # Dpendance pour obtenir la session DB
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import re
from dotenv import load_dotenv

# Detect Vercel environment
IS_VERCEL = os.getenv("VERCEL") == "1"
ENVIRONMENT = os.getenv("ENVIRONMENT", "production" if IS_VERCEL else "development")

# Only load .env if not on Vercel
if not IS_VERCEL:
    load_dotenv()

# Priorité absolue à la variable d'environnement DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Normalisation pour SQLAlchemy (postgres:// -> postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Nettoyage des caractères invisibles
if DATABASE_URL:
    DATABASE_URL = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', DATABASE_URL).strip()

# Fallback ULTIME pour la production (Neon DB)
if not DATABASE_URL and (ENVIRONMENT == "production" or IS_VERCEL):
    DATABASE_URL = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Fallback pour le développement local (SQLite)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./dzkitab.db"

# Créer le moteur SQLAlchemy
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Créer une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

