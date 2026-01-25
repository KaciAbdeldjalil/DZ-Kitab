# app/services/rating_monitor.py

from sqlalchemy.orm import Session
from app.models.rating import Rating, SellerStats
from app.models.user_suspension import UserSuspension, RatingAlert
from app.models.user import User
from app.services.notification_service import (
    notify_low_rating_alert,
    notify_account_suspended,
    notify_account_reactivated
)
from app.services.email import (
    send_low_rating_alert,
    send_account_suspension_notice,
    send_account_reactivation_notice
)
from datetime import datetime, timedelta

# Seuils de suspension
SUSPENSION_THRESHOLD = 10  # 10 notes  0 = suspension
LOW_RATING_WARNING_THRESHOLD = 3  # 3 notes  0 = alerte
SUSPENSION_DURATION_DAYS = 15

def check_and_handle_low_ratings(db: Session, seller_id: int):
    """
    Vrifier les notes d'un vendeur et prendre des mesures si ncessaire
    
    - Alerte  3 notes de 0 toile
    - Suspension automatique  10 notes de 0 toile
    """
    try:
        # Compter les notes  0 et 1 toile
        zero_rating_count = db.query(Rating).filter(
            Rating.seller_id == seller_id,
            Rating.rating == 0
        ).count()
        
        low_rating_count = db.query(Rating).filter(
            Rating.seller_id == seller_id,
            Rating.rating <= 1
        ).count()
        
        # Rcuprer les stats du vendeur
        stats = db.query(SellerStats).filter(SellerStats.user_id == seller_id).first()
        average_rating = stats.average_rating if stats else 0.0
        
        seller = db.query(User).filter(User.id == seller_id).first()
        if not seller:
            return
        
        print(f" Checking ratings for seller {seller.username}: {zero_rating_count} zero ratings, avg: {average_rating:.2f}")
        
        # Vrifier si dj suspendu
        active_suspension = db.query(UserSuspension).filter(
            UserSuspension.user_id == seller_id,
            UserSuspension.is_active == True
        ).first()
        
        if active_suspension:
            print(f" User {seller.username} already suspended")
            return
        
        # SUSPENSION AUTOMATIQUE: 10 notes  0
        if zero_rating_count >= SUSPENSION_THRESHOLD:
            print(f" Suspending user {seller.username} - {zero_rating_count} zero ratings")
            suspend_user(db, seller_id, zero_rating_count)
            return
        
        # ALERTE: 3 notes  0 ou plus
        if zero_rating_count >= LOW_RATING_WARNING_THRESHOLD or low_rating_count >= 5:
            # Vrifier si une alerte a dj t envoye rcemment
            recent_alert = db.query(RatingAlert).filter(
                RatingAlert.user_id == seller_id,
                RatingAlert.created_at >= datetime.utcnow() - timedelta(days=7)
            ).first()
            
            if not recent_alert:
                print(f" Sending low rating alert to {seller.username}")
                send_low_rating_warning(db, seller_id, low_rating_count, average_rating)
        
    except Exception as e:
        print(f" Error checking low ratings: {e}")
        db.rollback()

def suspend_user(db: Session, seller_id: int, zero_rating_count: int):
    """
    Suspendre un utilisateur pour notes basses
    """
    try:
        seller = db.query(User).filter(User.id == seller_id).first()
        if not seller:
            return
        
        # Crer la suspension
        suspension = UserSuspension.create_low_rating_suspension(
            user_id=seller_id,
            zero_rating_count=zero_rating_count,
            duration_days=SUSPENSION_DURATION_DAYS
        )
        
        db.add(suspension)
        
        # Dsactiver le compte
        seller.is_active = False
        
        db.commit()
        db.refresh(suspension)
        
        # Envoyer notifications
        suspension_end = suspension.suspension_end_date.strftime("%d/%m/%Y")
        
        # Notification in-app
        notify_account_suspended(db, seller_id, suspension_end)
        
        # Email
        try:
            send_account_suspension_notice(
                seller.email,
                seller.username,
                zero_rating_count,
                suspension_end
            )
        except Exception as e:
            print(f" Failed to send suspension email: {e}")
        
        print(f" User {seller.username} suspended until {suspension_end}")
        
    except Exception as e:
        print(f" Error suspending user: {e}")
        db.rollback()

def send_low_rating_warning(db: Session, seller_id: int, low_rating_count: int, average_rating: float):
    """
    Envoyer une alerte pour notes basses
    """
    try:
        seller = db.query(User).filter(User.id == seller_id).first()
        if not seller:
            return
        
        # Crer l'alerte
        alert = RatingAlert(
            user_id=seller_id,
            alert_type="low_rating_warning",
            low_rating_count=low_rating_count,
            average_rating=average_rating
        )
        
        db.add(alert)
        db.commit()
        
        # Notification in-app
        notify_low_rating_alert(db, seller_id, low_rating_count, average_rating)
        
        # Email
        try:
            email_sent = send_low_rating_alert(
                seller.email,
                seller.username,
                low_rating_count,
                average_rating
            )
            
            if email_sent:
                alert.email_sent = True
                alert.email_sent_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            print(f" Failed to send warning email: {e}")
        
        print(f" Low rating warning sent to {seller.username}")
        
    except Exception as e:
        print(f" Error sending low rating warning: {e}")
        db.rollback()

def check_expired_suspensions(db: Session):
    """
    Vrifier et ractiver les comptes dont la suspension a expir
     excuter rgulirement (cron job)
    """
    try:
        expired_suspensions = db.query(UserSuspension).filter(
            UserSuspension.is_active == True,
            UserSuspension.suspension_end_date <= datetime.utcnow()
        ).all()
        
        for suspension in expired_suspensions:
            reactivate_user(db, suspension.user_id, suspension.id)
        
        if expired_suspensions:
            print(f" Reactivated {len(expired_suspensions)} users")
        
    except Exception as e:
        print(f" Error checking expired suspensions: {e}")
        db.rollback()

def reactivate_user(db: Session, user_id: int, suspension_id: int):
    """
    Ractiver un utilisateur aprs la fin de la suspension
    """
    try:
        suspension = db.query(UserSuspension).filter(UserSuspension.id == suspension_id).first()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not suspension or not user:
            return
        
        # Ractiver la suspension
        suspension.reactivate()
        
        # Ractiver l'utilisateur
        user.is_active = True
        
        db.commit()
        
        # Notifications
        notify_account_reactivated(db, user_id)
        
        try:
            send_account_reactivation_notice(user.email, user.username)
        except Exception as e:
            print(f" Failed to send reactivation email: {e}")
        
        print(f" User {user.username} reactivated")
        
    except Exception as e:
        print(f" Error reactivating user: {e}")
        db.rollback()

def get_user_suspension_status(db: Session, user_id: int) -> dict:
    """
    Obtenir le statut de suspension d'un utilisateur
    """
    try:
        active_suspension = db.query(UserSuspension).filter(
            UserSuspension.user_id == user_id,
            UserSuspension.is_active == True
        ).first()
        
        if not active_suspension:
            return {
                "is_suspended": False,
                "suspension": None
            }
        
        # Vrifier si expire
        if active_suspension.is_expired():
            reactivate_user(db, user_id, active_suspension.id)
            return {
                "is_suspended": False,
                "suspension": None
            }
        
        return {
            "is_suspended": True,
            "suspension": {
                "id": active_suspension.id,
                "reason": active_suspension.reason,
                "description": active_suspension.description,
                "suspended_at": active_suspension.suspended_at.isoformat(),
                "suspension_end_date": active_suspension.suspension_end_date.isoformat(),
                "zero_rating_count": active_suspension.zero_rating_count,
                "days_remaining": (active_suspension.suspension_end_date - datetime.utcnow()).days
            }
        }
        
    except Exception as e:
        print(f" Error getting suspension status: {e}")
        return {
            "is_suspended": False,
            "suspension": None
        }
