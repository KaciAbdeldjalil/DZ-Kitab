from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType
from app.models.rating import Rating
from app.models.user import User
from typing import Optional

def notify_new_rating(db: Session, rating: Rating):
    """
    Crer une notification quand un vendeur reoit une nouvelle note
    """
    try:
        seller = db.query(User).filter(User.id == rating.seller_id).first()
        buyer = db.query(User).filter(User.id == rating.buyer_id).first()
        
        if not seller or not buyer:
            print(f" Utilisateur non trouv pour la notification")
            return
        
        # Crer la notification
        notification = Notification(
            user_id=rating.seller_id,
            type=NotificationType.NEW_RATING,
            title=f"Nouvelle note de {buyer.username}",
            message=f"{buyer.username} vous a donn {rating.rating} toiles" + (f": {rating.comment[:50]}..." if rating.comment else ""),
            related_user_id=rating.buyer_id,
            related_announcement_id=rating.announcement_id,
            related_rating_id=rating.id,
            action_url=f"/announcements/{rating.announcement_id}/ratings"
        )
        
        db.add(notification)
        db.commit()
        
        print(f" Notification cre pour le vendeur {seller.username}")
        
    except Exception as e:
        print(f" Erreur cration notification: {e}")
        db.rollback()


def notify_low_rating_alert(db: Session, seller_id: int, low_rating_count: int, average_rating: float):
    """
    Alerter le vendeur qu'il a trop de notes basses
    """
    try:
        seller = db.query(User).filter(User.id == seller_id).first()
        if not seller:
            return
        
        notification = Notification(
            user_id=seller_id,
            type=NotificationType.LOW_RATING_ALERT,
            title=" Alerte: Notes basses",
            message=f"Vous avez {low_rating_count} notes de 1 toile. Votre moyenne est de {average_rating:.1f}/5.0",
            action_url="/profile/ratings"
        )
        
        db.add(notification)
        db.commit()
        
        print(f" Alerte notes basses envoye  {seller.username}")
        
    except Exception as e:
        print(f" Erreur alerte notes basses: {e}")
        db.rollback()


def notify_account_suspended(db: Session, seller_id: int, suspension_end_date: str):
    """
    Notifier le vendeur que son compte est suspendu
    """
    try:
        seller = db.query(User).filter(User.id == seller_id).first()
        if not seller:
            return
        
        notification = Notification(
            user_id=seller_id,
            type=NotificationType.ACCOUNT_SUSPENDED,
            title=" Compte Suspendu",
            message=f"Votre compte est suspendu jusqu'au {suspension_end_date}",
            action_url="/profile/suspension"
        )
        
        db.add(notification)
        db.commit()
        
        print(f" Notification suspension envoye  {seller.username}")
        
    except Exception as e:
        print(f" Erreur notification suspension: {e}")
        db.rollback()


def notify_account_reactivated(db: Session, seller_id: int):
    """
    Notifier le vendeur que son compte est ractiv
    """
    try:
        seller = db.query(User).filter(User.id == seller_id).first()
        if not seller:
            return
        
        notification = Notification(
            user_id=seller_id,
            type=NotificationType.ACCOUNT_REACTIVATED,
            title=" Compte Ractiv",
            message="Votre compte a t ractiv avec succs. Vous pouvez  nouveau publier des annonces.",
            action_url="/dashboard"
        )
        
        db.add(notification)
        db.commit()
        
        print(f" Notification ractivation envoye  {seller.username}")
        
    except Exception as e:
        print(f" Erreur notification ractivation: {e}")
        db.rollback()
