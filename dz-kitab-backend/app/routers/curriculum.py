# app/routers/curriculum.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.curriculum import Curriculum, RecommendedBook
from app.models.book import Book, Announcement
from app.models.user import User
from app.services.curriculum_service import (
    get_book_curriculum_badges,
    search_books_by_curriculum,
    get_all_curriculums,
    get_curriculum_stats,
    auto_match_all_books
)
from app.middleware.auth import security
from app.services.jwt import verify_token

router = APIRouter()

@router.get("/test")
def test_curriculum():
    """Test endpoint"""
    return {
        "message": " Curriculum router is working!",
        "endpoints": [
            "GET /curriculum/ - Liste des cursus",
            "GET /curriculum/{id} - Dtails d'un cursus",
            "GET /curriculum/badges/book/{book_id} - Badges d'un livre",
            "GET /curriculum/{id}/books - Livres d'un cursus",
            "GET /curriculum/stats/overview - Statistiques",
            "POST /curriculum/admin/match-books - Matching (Admin)"
        ]
    }
def get_current_user_id(token: str = Depends(security), db: Session = Depends(get_db)) -> int:
    """Get the current authenticated user ID from token"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouv"
        )
    
    return user.id


# ============================================
# GET ALL CURRICULUMS
# ============================================

@router.get("/")
def get_curriculums(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    university: Optional[str] = None,
    field: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
     Obtenir la liste de tous les cursus disponibles
    
    Filtres optionnels:
    - university: Filtrer par universit (ex: "USTHB")
    - field: Filtrer par filire (ex: "Informatique")
    """
    try:
        query = db.query(Curriculum)
        
        if university:
            query = query.filter(Curriculum.university.ilike(f"%{university}%"))
        
        if field:
            query = query.filter(Curriculum.field.ilike(f"%{field}%"))
        
        total = query.count()
        curriculums = query.offset(skip).limit(limit).all()
        
        result = []
        for curriculum in curriculums:
            result.append({
                "id": curriculum.id,
                "name": curriculum.name,
                "university": curriculum.university,
                "field": curriculum.field,
                "year": curriculum.year,
                "description": curriculum.description,
                "books_count": len(curriculum.recommended_books),
                "created_at": curriculum.created_at.isoformat()
            })
        
        return {
            "total": total,
            "curriculums": result
        }
        
    except Exception as e:
        print(f" Erreur rcupration cursus: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la rcupration des cursus"
        )


# ============================================
# GET CURRICULUM DETAILS
# ============================================

@router.get("/{curriculum_id}")
def get_curriculum_details(
    curriculum_id: int,
    db: Session = Depends(get_db)
):
    """
     Obtenir les dtails d'un cursus et ses livres recommands
    """
    try:
        curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
        
        if not curriculum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cursus non trouv"
            )
        
        # Formater les livres recommands
        recommended_books = []
        for book in curriculum.recommended_books:
            recommended_books.append({
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "publisher": book.publisher,
                "edition": book.edition
            })
        
        return {
            "id": curriculum.id,
            "name": curriculum.name,
            "university": curriculum.university,
            "field": curriculum.field,
            "year": curriculum.year,
            "description": curriculum.description,
            "source_url": curriculum.source_url,
            "books_count": len(recommended_books),
            "recommended_books": recommended_books,
            "created_at": curriculum.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Erreur dtails cursus: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la rcupration des dtails"
        )


# ============================================
# GET BOOK BADGES
# ============================================

@router.get("/badges/book/{book_id}")
def get_book_badges(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
     Obtenir les badges de cursus pour un livre
    
    Retourne les badges "Recommand en [Cursus]" si le livre correspond
    """
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livre non trouv"
            )
        
        badges = get_book_curriculum_badges(db, book_id)
        
        return {
            "book_id": book_id,
            "book_title": book.title,
            "badges_count": len(badges),
            "badges": badges
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Erreur badges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la rcupration des badges"
        )


# ============================================
# SEARCH BOOKS BY CURRICULUM
# ============================================

@router.get("/{curriculum_id}/books")
def search_books_by_curriculum_endpoint(
    curriculum_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
     Rechercher tous les livres disponibles pour un cursus
    
    Retourne toutes les annonces de livres qui correspondent aux livres
    recommands pour ce cursus
    """
    try:
        curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
        
        if not curriculum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cursus non trouv"
            )
        
        # Trouver les livres correspondants
        books = search_books_by_curriculum(db, curriculum_id)
        book_ids = [b.id for b in books]
        
        # Rcuprer les annonces pour ces livres
        query = db.query(Announcement).filter(
            Announcement.book_id.in_(book_ids),
            Announcement.status == "Active"
        )
        
        total = query.count()
        announcements = query.offset(skip).limit(limit).all()
        
        # Formater les rsultats
        result = []
        for ann in announcements:
            book = db.query(Book).filter(Book.id == ann.book_id).first()
            user = db.query(User).filter(User.id == ann.user_id).first()
            badges = get_book_curriculum_badges(db, book.id)
            
            result.append({
                "id": ann.id,
                "book": {
                    "id": book.id,
                    "title": book.title,
                    "authors": book.authors,
                    "cover_image_url": book.cover_image_url
                },
                "price": ann.price,
                "condition": ann.condition,
                "seller": {
                    "id": user.id,
                    "username": user.username
                },
                "badges": badges,
                "created_at": ann.created_at.isoformat()
            })
        
        return {
            "curriculum": {
                "id": curriculum.id,
                "name": curriculum.name
            },
            "total": total,
            "announcements": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Erreur recherche livres: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche"
        )


# ============================================
# STATISTICS
# ============================================

@router.get("/stats/overview")
def get_curriculum_statistics(db: Session = Depends(get_db)):
    """
     Obtenir des statistiques sur les cursus
    """
    try:
        stats = get_curriculum_stats(db)
        
        # Cursus par universit
        curriculums_by_university = db.query(
            Curriculum.university,
            db.func.count(Curriculum.id).label('count')
        ).group_by(Curriculum.university).all()
        
        # Cursus par filire
        curriculums_by_field = db.query(
            Curriculum.field,
            db.func.count(Curriculum.id).label('count')
        ).group_by(Curriculum.field).all()
        
        return {
            "overview": stats,
            "by_university": [
                {"university": u, "count": c}
                for u, c in curriculums_by_university
            ],
            "by_field": [
                {"field": f, "count": c}
                for f, c in curriculums_by_field
            ]
        }
        
    except Exception as e:
        print(f" Erreur statistiques: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la rcupration des statistiques"
        )


# ============================================
# ADMIN: TRIGGER MATCHING
# ============================================

@router.post("/admin/match-books")
def trigger_book_matching(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
     Matcher tous les livres avec les recommandations (ADMIN)
    
     excuter aprs un scraping ou priodiquement
    """
    try:
        # Vrifier que l'utilisateur est admin
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accs rserv aux administrateurs"
            )
        
        # Lancer le matching
        auto_match_all_books(db)
        
        return {
            "message": "Matching termin avec succs",
            "stats": get_curriculum_stats(db)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Erreur matching: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du matching"
        )


