# app/routers/recommendations.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.book import Announcement, Book
from app.models.user import User
from app.schemas.book import AnnouncementResponse

router = APIRouter()

def format_announcement_response(announcement: Announcement, db: Session) -> AnnouncementResponse:
    """Helper pour formater une annonce en rponse"""
    book = db.query(Book).filter(Book.id == announcement.book_id).first()
    user = db.query(User).filter(User.id == announcement.user_id).first()
    
    return AnnouncementResponse(
        id=announcement.id,
        book_id=announcement.book_id,
        user_id=announcement.user_id,
        category=announcement.category.value if hasattr(announcement.category, 'value') else announcement.category,
        price=announcement.price,
        market_price=announcement.market_price,
        final_calculated_price=announcement.final_calculated_price,
        condition=announcement.condition.value if hasattr(announcement.condition, 'value') else announcement.condition,
        status=announcement.status.value if hasattr(announcement.status, 'value') else announcement.status,
        description=announcement.description,
        custom_images=announcement.custom_images,
        location=announcement.location,
        page_count=announcement.page_count,
        publication_date=announcement.publication_date,
        views_count=announcement.views_count or 0,
        created_at=announcement.created_at,
        updated_at=announcement.updated_at,
        book=book,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    )

@router.get("/announcements/{announcement_id}")
def get_same_domain_recommendations(
    announcement_id: int,
    limit: int = Query(4, ge=1, le=12, description="Nombre de recommandations"),
    db: Session = Depends(get_db)
):
    """
     Obtenir les recommandations pour une annonce
    
    **Condition**: Recommande uniquement les livres du MME DOMAINE (catgorie)
    
    **Paramtres**:
    - **announcement_id**: ID de l'annonce actuelle
    - **limit**: Nombre de recommandations (par dfaut: 4)
    
    **Retourne**: Liste de livres de la mme catgorie
    """
    try:
        # 1. Rcuprer l'annonce actuelle
        current_announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not current_announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Annonce non trouve"
            )
        
        # 2. Extraire la catgorie
        category = current_announcement.category.value if hasattr(
            current_announcement.category, 'value'
        ) else current_announcement.category
        
        # 3. Chercher les annonces de la MME catgorie
        recommendations = db.query(Announcement).filter(
            Announcement.category == category,           #  MME DOMAINE
            Announcement.id != announcement_id,          #  Exclure l'annonce actuelle
            Announcement.status == "Active"              #  Seulement les actives
        ).order_by(
            Announcement.created_at.desc()               #  Les plus rcentes en premier
        ).limit(limit).all()
        
        # 4. Formater les rponses
        formatted_recommendations = [
            format_announcement_response(ann, db)
            for ann in recommendations
        ]
        
        # 5. Retourner les recommandations
        return {
            "success": True,
            "announcement_id": announcement_id,
            "category": category,
            "total": len(formatted_recommendations),
            "recommendations": formatted_recommendations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Erreur recommandations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la rcupration des recommandations"
        )

@router.get("/test")
def test_recommendations():
    """Test endpoint pour vrifier que le router fonctionne"""
    return {
        "message": " Recommendations router is working!",
        "description": "Ce module recommande des livres du mme domaine",
        "endpoint": "GET /api/recommendations/announcements/{announcement_id}",
        "example": "GET /api/recommendations/announcements/1?limit=4"
    }
