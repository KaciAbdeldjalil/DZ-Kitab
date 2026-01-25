# app/scripts/scrape_curriculum_books.py

"""
Script de web scraping pour rcuprer les listes de livres recommands
pour diffrents cursus universitaires algriens.

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

# Ajouter le rpertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.curriculum import Curriculum, RecommendedBook

# Configuration
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# URLs  scraper (exemples -  adapter selon les sources relles)
SOURCES = [
    {
        "name": "L1 Informatique USTHB",
        "university": "USTHB",
        "field": "Informatique",
        "year": "1re anne",
        "url": "https://www.usthb.dz/fei/programmes/l1-informatique",  # URL fictive
        "selector": ".book-list .book-item"  # Slecteur CSS fictif
    },
    {
        "name": "1re Anne Mdecine Universit d'Alger",
        "university": "Universit d'Alger 1",
        "field": "Mdecine",
        "year": "1re anne",
        "url": "https://www.univ-alger.dz/medecine/1ere-annee",  # URL fictive
        "selector": ".recommended-books .book"
    },
    {
        "name": "L1 Mathmatiques USTHB",
        "university": "USTHB",
        "field": "Mathmatiques",
        "year": "1re anne",
        "url": "https://www.usthb.dz/fs/maths/l1",  # URL fictive
        "selector": ".course-books li"
    }
]


def scrape_usthb_informatique() -> List[Dict]:
    """
    Scraper spcifique pour USTHB Informatique
     adapter selon la structure relle du site
    """
    books = []
    
    # Exemple de donnes hardcodes ( remplacer par du vrai scraping)
    sample_books = [
        {"title": "Algorithmique et structures de donnes", "author": "Thomas H. Cormen"},
        {"title": "Introduction  Python", "author": "Grard Swinnen"},
        {"title": "Architecture des ordinateurs", "author": "Andrew S. Tanenbaum"},
        {"title": "Mathmatiques pour l'informatique", "author": "Donald Knuth"},
        {"title": "Systmes d'exploitation", "author": "Abraham Silberschatz"}
    ]
    
    return sample_books


def scrape_medecine_alger() -> List[Dict]:
    """
    Scraper spcifique pour Mdecine Alger
    """
    books = [
        {"title": "Anatomie humaine", "author": "Frank H. Netter"},
        {"title": "Physiologie mdicale", "author": "Guyton et Hall"},
        {"title": "Biochimie mdicale", "author": "Harper"},
        {"title": "Histologie", "author": "Ross et Pawlina"},
        {"title": "Embryologie humaine", "author": "Larsen"}
    ]
    
    return books


def scrape_maths_usthb() -> List[Dict]:
    """
    Scraper spcifique pour Mathmatiques USTHB
    """
    books = [
        {"title": "Analyse mathmatique I", "author": "Vladimir Zorich"},
        {"title": "Algbre linaire", "author": "Serge Lang"},
        {"title": "Topologie gnrale", "author": "James Munkres"},
        {"title": "Probabilits et statistiques", "author": "Sheldon Ross"},
        {"title": "Calcul diffrentiel", "author": "Michael Spivak"}
    ]
    
    return books


def scrape_generic(url: str, selector: str) -> List[Dict]:
    """
    Scraper gnrique pour n'importe quelle page
    
    Args:
        url: URL de la page  scraper
        selector: Slecteur CSS pour trouver les livres
    
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
            # Adapter selon la structure HTML relle
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
        print(f" Erreur lors du scraping de {url}: {e}")
        return []


def save_curriculum_books(db: Session, curriculum_data: Dict, books: List[Dict]):
    """
    Sauvegarder le cursus et ses livres dans la base de donnes
    
    Args:
        db: Session de base de donnes
        curriculum_data: Donnes du cursus
        books: Liste des livres recommands
    """
    try:
        # Crer ou rcuprer le cursus
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
        
        print(f" Cursus: {curriculum.name}")
        
        # Ajouter les livres
        for book_data in books:
            # Vrifier si le livre existe dj
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
            
            print(f"   {book_data['title']} - {book_data.get('author', 'Auteur inconnu')}")
        
        db.commit()
        print(f" {len(books)} livres ajouts pour {curriculum.name}\n")
        
    except Exception as e:
        print(f" Erreur lors de la sauvegarde: {e}")
        db.rollback()


def run_scraping():
    """
    Fonction principale d'excution du scraping
    """
    print("\n" + "="*60)
    print("  SCRAPING DES LISTES DE LIVRES RECOMMANDS")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # 1. USTHB Informatique
        print(" Scraping: L1 Informatique USTHB...")
        books = scrape_usthb_informatique()
        save_curriculum_books(db, {
            "name": "L1 Informatique USTHB",
            "university": "USTHB",
            "field": "Informatique",
            "year": "1re anne"
        }, books)
        time.sleep(1)
        
        # 2. Mdecine Alger
        print(" Scraping: 1re Anne Mdecine Universit d'Alger...")
        books = scrape_medecine_alger()
        save_curriculum_books(db, {
            "name": "1re Anne Mdecine Universit d'Alger",
            "university": "Universit d'Alger 1",
            "field": "Mdecine",
            "year": "1re anne"
        }, books)
        time.sleep(1)
        
        # 3. Mathmatiques USTHB
        print(" Scraping: L1 Mathmatiques USTHB...")
        books = scrape_maths_usthb()
        save_curriculum_books(db, {
            "name": "L1 Mathmatiques USTHB",
            "university": "USTHB",
            "field": "Mathmatiques",
            "year": "1re anne"
        }, books)
        
        print("\n" + "="*60)
        print(" SCRAPING TERMIN AVEC SUCCS")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n Erreur globale: {e}")
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    run_scraping()
