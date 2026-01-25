from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.rating import Rating, SellerStats
from app.models.user import User
from app.models.book import Announcement
from app.schemas.rating import (
    RatingCreate,
    RatingUpdate,
    RatingResponse,
    SellerStatsResponse,
    RatingListResponse
)
from app.middleware.auth import security
from app.services.jwt import verify_token
from app.services.notification_service import notify_new_rating

router = APIRouter()

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

@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating(
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    buyer_id: int = Depends(get_current_user_id)
):
    """Create a new rating for a seller"""
    try:
        announcement = db.query(Announcement).filter(
            Announcement.id == rating_data.announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Annonce non trouve"
            )
        
        seller_id = announcement.user_id
        
        if buyer_id == seller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez pas noter votre propre annonce"
            )
        
        existing_rating = db.query(Rating).filter(
            Rating.buyer_id == buyer_id,
            Rating.announcement_id == rating_data.announcement_id
        ).first()
        
        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous avez dj not cette annonce"
            )
        
        rating = Rating(
            buyer_id=buyer_id,
            seller_id=seller_id,
            announcement_id=rating_data.announcement_id,
            rating=rating_data.rating,
            comment=rating_data.comment,
            communication_rating=rating_data.communication_rating,
            condition_accuracy_rating=rating_data.condition_accuracy_rating,
            delivery_speed_rating=rating_data.delivery_speed_rating
        )
        
        db.add(rating)
        db.commit()
        db.refresh(rating)
        
        #  NOTIFICATION: Notifier le vendeur de la nouvelle note
        try:
            notify_new_rating(db, rating)
        except Exception as e:
            print(f" Erreur notification: {e}")
            # Continue mme si la notification choue
        
        update_seller_stats(db, seller_id)
        
        buyer = db.query(User).filter(User.id == buyer_id).first()
        seller = db.query(User).filter(User.id == seller_id).first()
        
        return RatingResponse(
            id=rating.id,
            buyer_id=rating.buyer_id,
            seller_id=rating.seller_id,
            announcement_id=rating.announcement_id,
            rating=rating.rating,
            comment=rating.comment,
            communication_rating=rating.communication_rating,
            condition_accuracy_rating=rating.condition_accuracy_rating,
            delivery_speed_rating=rating.delivery_speed_rating,
            created_at=rating.created_at,
            buyer_username=buyer.username,
            seller_username=seller.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Error creating rating: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la cration de la note: {str(e)}"
        )

@router.get("/seller/{seller_id}", response_model=RatingListResponse)
def get_seller_ratings(
    seller_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all ratings for a specific seller"""
    seller = db.query(User).filter(User.id == seller_id).first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendeur non trouv"
        )
    
    total = db.query(Rating).filter(Rating.seller_id == seller_id).count()
    ratings = db.query(Rating).filter(
        Rating.seller_id == seller_id
    ).order_by(Rating.created_at.desc()).offset(skip).limit(limit).all()
    
    formatted_ratings = []
    for rating in ratings:
        buyer = db.query(User).filter(User.id == rating.buyer_id).first()
        
        formatted_ratings.append(
            RatingResponse(
                id=rating.id,
                buyer_id=rating.buyer_id,
                seller_id=rating.seller_id,
                announcement_id=rating.announcement_id,
                rating=rating.rating,
                comment=rating.comment,
                communication_rating=rating.communication_rating,
                condition_accuracy_rating=rating.condition_accuracy_rating,
                delivery_speed_rating=rating.delivery_speed_rating,
                created_at=rating.created_at,
                buyer_username=buyer.username,
                seller_username=seller.username
            )
        )
    
    return RatingListResponse(
        total=total,
        ratings=formatted_ratings
    )

@router.get("/seller/{seller_id}/stats", response_model=SellerStatsResponse)
def get_seller_stats(seller_id: int, db: Session = Depends(get_db)):
    """Get aggregated statistics for a seller"""
    seller = db.query(User).filter(User.id == seller_id).first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendeur non trouv"
        )
    
    stats = db.query(SellerStats).filter(SellerStats.user_id == seller_id).first()
    
    if not stats:
        stats = SellerStats(user_id=seller_id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    stats.calculate_stats(db)
    db.commit()
    db.refresh(stats)
    
    return SellerStatsResponse(
        user_id=stats.user_id,
        total_ratings=stats.total_ratings,
        average_rating=stats.average_rating,
        avg_communication=stats.avg_communication,
        avg_condition_accuracy=stats.avg_condition_accuracy,
        avg_delivery_speed=stats.avg_delivery_speed,
        rating_5_count=stats.rating_5_count,
        rating_4_count=stats.rating_4_count,
        rating_3_count=stats.rating_3_count,
        rating_2_count=stats.rating_2_count,
        rating_1_count=stats.rating_1_count,
        is_top_seller=stats.is_top_seller,
        total_sales=stats.total_sales
    )

@router.put("/{rating_id}", response_model=RatingResponse)
def update_rating(
    rating_id: int,
    rating_data: RatingUpdate,
    db: Session = Depends(get_db),
    buyer_id: int = Depends(get_current_user_id)
):
    """Update a rating (only by the buyer who created it)"""
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note non trouve"
        )
    
    if rating.buyer_id != buyer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'tes pas autoris  modifier cette note"
        )
    
    if rating_data.rating is not None:
        rating.rating = rating_data.rating
    if rating_data.comment is not None:
        rating.comment = rating_data.comment
    if rating_data.communication_rating is not None:
        rating.communication_rating = rating_data.communication_rating
    if rating_data.condition_accuracy_rating is not None:
        rating.condition_accuracy_rating = rating_data.condition_accuracy_rating
    if rating_data.delivery_speed_rating is not None:
        rating.delivery_speed_rating = rating_data.delivery_speed_rating
    
    db.commit()
    db.refresh(rating)
    
    update_seller_stats(db, rating.seller_id)
    
    buyer = db.query(User).filter(User.id == rating.buyer_id).first()
    seller = db.query(User).filter(User.id == rating.seller_id).first()
    
    return RatingResponse(
        id=rating.id,
        buyer_id=rating.buyer_id,
        seller_id=rating.seller_id,
        announcement_id=rating.announcement_id,
        rating=rating.rating,
        comment=rating.comment,
        communication_rating=rating.communication_rating,
        condition_accuracy_rating=rating.condition_accuracy_rating,
        delivery_speed_rating=rating.delivery_speed_rating,
        created_at=rating.created_at,
        buyer_username=buyer.username,
        seller_username=seller.username
    )

@router.delete("/{rating_id}")
def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    buyer_id: int = Depends(get_current_user_id)
):
    """Delete a rating (only by the buyer who created it)"""
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note non trouve"
        )
    
    if rating.buyer_id != buyer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'tes pas autoris  supprimer cette note"
        )
    
    seller_id = rating.seller_id
    
    db.delete(rating)
    db.commit()
    
    update_seller_stats(db, seller_id)
    
    return {
        "message": "Note supprime avec succs",
        "rating_id": rating_id
    }

def update_seller_stats(db: Session, seller_id: int):
    """Update seller statistics after a rating change"""
    try:
        stats = db.query(SellerStats).filter(SellerStats.user_id == seller_id).first()
        
        if not stats:
            stats = SellerStats(user_id=seller_id)
            db.add(stats)
        
        stats.calculate_stats(db)
        db.commit()
        
    except Exception as e:
        print(f" Error updating seller stats: {e}")
        db.rollback()
