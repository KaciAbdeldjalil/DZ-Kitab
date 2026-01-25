# app/scripts/match_books.py

"""
Script pour matcher automatiquement les livres de la plateforme
avec les livres recommands des cursus.

Usage:
    python -m app.scripts.match_books
"""

import sys
import os
from pathlib import Path

# Ajouter le rpertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.curriculum_service import auto_match_all_books

def run_matching():
    """
    Fonction principale : matcher tous les livres
    """
    print("\n" + "="*60)
    print(" MATCHING AUTOMATIQUE DES LIVRES")
    print("="*60 + "\n")
    
    db: Session = SessionLocal()
    
    try:
        # Lancer le matching
        auto_match_all_books(db)
        
        print("\n" + "="*60)
        print(" MATCHING TERMIN AVEC SUCCS")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f" Erreur lors du matching: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    run_matching()
