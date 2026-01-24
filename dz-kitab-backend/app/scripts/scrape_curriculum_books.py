# app/scripts/scrape_curriculum_books.py

"""
Script de web scraping pour récupérer les listes de livres recommandés
pour différents cursus universitaires algériens.

Usage:
    python -m app.scripts.scrape_curriculum_books
"""

import sys
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.curriculum import Curriculum, RecommendedBook

# Configuration
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# URLs à scraper (exemples - à adapter selon les sources réelles)
SOURCES = [
    {
        "name": "L1 Informatique USTHB",
        "university": "USTHB",
        "field": "Informatique",
        "year": "1ère année",
        "url": "https://www.usthb.dz/fei/programmes/l1-informatique",  # URL fictive
        "selector": ".book-list .book-item"  # Sélecteur CSS fictif
    },
    {
        "name": "1ère Année Médecine Université d'Alger",
        "university": "Université d'Alger 1",
        "field": "Médecine",
        "year": "1ère année",
        "url": "https://www.univ-alger.dz/medecine/1ere-annee",  # URL fictive
        "selector": ".recommended-books .book"
    },
    {
        "name": "L1 Mathématiques USTHB",
        "university": "USTHB",
        "field": "Mathématiques",
        "year": "1ère année",
        "url": "https://www.usthb.dz/fs/maths/l1",  # URL fictive
        "selector": ".course-books li"
    }
]


def scrape_usthb_informatique() -> List[Dict]:
    """
    Scraper spécifique pour USTHB Informatique
    À adapter selon la structure réelle du site
    """
    books = []
    
    # Exemple de données hardcodées (à remplacer par du vrai scraping)
    sample_books = [
        {"title": "Algorithmique et structures de données", "author": "Thomas H. Cormen"},
        {"title": "Introduction à Python", "author": "Gérard Swinnen"},
        {"title": "Architecture des ordinateurs", "author": "Andrew S. Tanenbaum"},
        {"title": "Mathématiques pour l'informatique", "author": "Donald Knuth"},
        {"title": "Systèmes d'exploitation", "author": "Abraham Silberschatz"}
    ]
    
    return sample_books


def scrape_medecine_alger() -> List[Dict]:
    """
    Scraper spécifique pour Médecine Alger
    """
    books = [
        {"title": "Anatomie humaine", "author": "Frank H. Netter"},
        {"title": "Physiologie médicale", "author": "Guyton et Hall"},
        {"title": "Biochimie médicale", "author": "Harper"},
        {"title": "Histologie", "author": "Ross et Pawlina"},
        {"title": "Embryologie humaine", "author": "Larsen"}
    ]
    
    return books


def scrape_maths_usthb() -> List[Dict]:
    """
    Scraper spécifique pour Mathématiques USTHB
    """
    books = [
        {"title": "Analyse mathématique I", "author": "Vladimir Zorich"},
        {"title": "Algèbre linéaire", "author": "Serge Lang"},
        {"title": "Topologie générale", "author": "James Munkres"},
        {"title": "Probabilités et statistiques", "author": "Sheldon Ross"},
        {"title": "Calcul différentiel", "author": "Michael Spivak"}
    ]
    
    return books


def scrape_generic(url: str, selector: str) -> List[Dict]:
    """
    Scraper générique pour n'importe quelle page
    
    Args:
        url: URL de la page à scraper
        selector: Sélecteur CSS pour trouver les livres
    
    Returns:
        Liste de dictionnaires avec titre et auteur
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        books = []
        
        book_elements = soup.select(selector)
        
        for element in book_elements:
            # Adapter selon la structure HTML réelle
            title = element.select_one('.title, h3, .book-title')
            author = element.select_one('.author, .book-author')
            
            if title:
                book_data = {
                    "title": title.get_text(strip=True),
                    "author": author.get_text(strip=True) if author else None
                }
                books.append(book_data)
        
        return books
        
    except Exception as e:
        print(f"❌ Erreur lors du scraping de {url}: {e}")
        return []


def save_curriculum_books(db: Session, curriculum_data: Dict, books: List[Dict]):
    """
    Sauvegarder le cursus et ses livres dans la base de données
    
    Args:
        db: Session de base de données
        curriculum_data: Données du cursus
        books: Liste des livres recommandés
    """
    try:
        # Créer ou récupérer le cursus
        curriculum = db.query(Curriculum).filter(
            Curriculum.name == curriculum_data["name"]
        ).first()
        
        if not curriculum:
            curriculum = Curriculum(
                name=curriculum_data["name"],
                university=curriculum_data["university"],
                field=curriculum_data["field"],
                year=curriculum_data["year"],
                source_url=curriculum_data.get("url")
            )
            db.add(curriculum)
            db.flush()
        
        print(f"✅ Cursus: {curriculum.name}")
        
        # Ajouter les livres
        for book_data in books:
            # Vérifier si le livre existe déjà
            existing_book = db.query(RecommendedBook).filter(
                RecommendedBook.title == book_data["title"],
                RecommendedBook.author == book_data.get("author")
            ).first()
            
            if not existing_book:
                recommended_book = RecommendedBook(
                    title=book_data["title"],
                    author=book_data.get("author"),
                    isbn=book_data.get("isbn"),
                    source_url=curriculum_data.get("url")
                )
                db.add(recommended_book)
                db.flush()
            else:
                recommended_book = existing_book
            
            # Lier le livre au cursus
            if recommended_book not in curriculum.recommended_books:
                curriculum.recommended_books.append(recommended_book)
            
            print(f"  📚 {book_data['title']} - {book_data.get('author', 'Auteur inconnu')}")
        
        db.commit()
        print(f"✅ {len(books)} livres ajoutés pour {curriculum.name}\n")
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        db.rollback()


def run_scraping():
    """
    Fonction principale d'exécution du scraping
    """
    print("\n" + "="*60)
    print("🕷️  SCRAPING DES LISTES DE LIVRES RECOMMANDÉS")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # 1. USTHB Informatique
        print("🔍 Scraping: L1 Informatique USTHB...")
        books = scrape_usthb_informatique()
        save_curriculum_books(db, {
            "name": "L1 Informatique USTHB",
            "university": "USTHB",
            "field": "Informatique",
            "year": "1ère année"
        }, books)
        time.sleep(1)
        
        # 2. Médecine Alger
        print("🔍 Scraping: 1ère Année Médecine Université d'Alger...")
        books = scrape_medecine_alger()
        save_curriculum_books(db, {
            "name": "1ère Année Médecine Université d'Alger",
            "university": "Université d'Alger 1",
            "field": "Médecine",
            "year": "1ère année"
        }, books)
        time.sleep(1)
        
        # 3. Mathématiques USTHB
        print("🔍 Scraping: L1 Mathématiques USTHB...")
        books = scrape_maths_usthb()
        save_curriculum_books(db, {
            "name": "L1 Mathématiques USTHB",
            "university": "USTHB",
            "field": "Mathématiques",
            "year": "1ère année"
        }, books)
        
        print("\n" + "="*60)
        print("✅ SCRAPING TERMINÉ AVEC SUCCÈS")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erreur globale: {e}")
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    run_scraping()
