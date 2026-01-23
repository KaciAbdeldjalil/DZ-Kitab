from django.core.management.base import BaseCommand
from app.models.user import User, UniversityEnum
from app.models.book import Book, Announcement, BookConditionEnum, BookCategoryEnum, AnnouncementStatusEnum
from app.models.book_condition import BookConditionScore
from app.models.rating import Rating, SellerStats
from app.models.notification import Notification, NotificationPreference, NotificationType
from app.models.user_suspension import UserSuspension, RatingAlert
from app.models.wishlist import Wishlist
from app.models.message import Message
from datetime import timedelta, datetime
import random

class Command(BaseCommand):
    help = 'Seed complet de la base de données'

    def handle(self, *args, **kwargs):

        self.stdout.write("🚀 Début du seed...")

        # --- USERS ---
        User.objects.all().delete()
        user1 = User.objects.create(username='alice', email='alice@test.com', hashed_password='pass', university=UniversityEnum.ESTIN)
        user2 = User.objects.create(username='bob', email='bob@test.com', hashed_password='pass', university=UniversityEnum.ESI)

        # --- BOOKS ---
        Book.objects.all().delete()
        book1 = Book.objects.create(
            isbn='9781234567890',
            title='Apprendre Python',
            authors='Auteur A',
            publisher='Editeur X',
            published_date='2020',
            categories='Informatique'
        )
        book2 = Book.objects.create(
            isbn='9780987654321',
            title='Mathématiques avancées',
            authors='Auteur B',
            publisher='Editeur Y',
            published_date='2019',
            categories='Mathématiques'
        )

        # --- ANNOUNCEMENTS ---
        Announcement.objects.all().delete()
        ann1 = Announcement.objects.create(
            book=book1,
            user=user1,
            price=30,
            condition=BookConditionEnum.NEUF,
            category=BookCategoryEnum.INFORMATIQUE,
            status=AnnouncementStatusEnum.ACTIVE
        )
        ann2 = Announcement.objects.create(
            book=book2,
            user=user2,
            price=40,
            condition=BookConditionEnum.BON_ETAT,
            category=BookCategoryEnum.MATHEMATIQUES,
            status=AnnouncementStatusEnum.RESERVE
        )

        # --- BOOK CONDITION SCORES ---
        BookConditionScore.objects.all().delete()
        score1 = BookConditionScore.objects.create(
            announcement=ann1,
            page_no_missing=True,
            page_no_torn=True,
            page_clean=True
        )
        score1.calculate_scores()
        score1.suggest_price(base_price=30)

        score2 = BookConditionScore.objects.create(
            announcement=ann2,
            page_no_missing=True,
            page_no_torn=False,
            page_clean=True
        )
        score2.calculate_scores()
        score2.suggest_price(base_price=40)

        # --- RATINGS ---
        Rating.objects.all().delete()
        rating1 = Rating.objects.create(
            buyer=user2,
            seller=user1,
            announcement=ann1,
            rating=5,
            comment='Excellent livre!',
            communication_rating=5,
            condition_accuracy_rating=5,
            delivery_speed_rating=5
        )

        # --- SELLER STATS ---
        SellerStats.objects.all().delete()
        stats1 = SellerStats.objects.create(user=user1)
        stats1.calculate_stats(db=None)  # tu peux ajouter db session si besoin

        # --- NOTIFICATIONS ---
        Notification.objects.all().delete()
        NotificationPreference.objects.all().delete()
        notif1 = Notification.objects.create(
            user=user1,
            type=NotificationType.NEW_RATING,
            title="Nouvelle note reçue",
            message="Vous avez reçu une nouvelle note sur votre annonce.",
            related_user_id=user2.id,
            related_announcement_id=ann1.id
        )
        pref1 = NotificationPreference.objects.create(
            user=user1
        )

        # --- SUSPENSIONS & RATING ALERTS ---
        UserSuspension.objects.all().delete()
        RatingAlert.objects.all().delete()
        suspension1 = UserSuspension.create_manual_suspension(
            user_id=user2.id,
            duration_days=7,
            reason="Test suspension"
        )
        suspension1.save()
        alert1 = RatingAlert.objects.create(
            user=user2,
            alert_type='low_rating',
            low_rating_count=1
        )

        # --- WISHLIST ---
        Wishlist.objects.all().delete()
        wishlist1 = Wishlist.objects.create(
            user=user1,
            announcement=ann2
        )

        # --- MESSAGES ---
        Message.objects.all().delete()
        msg1 = Message.objects.create(
            sender=user1,
            receiver=user2,
            annonce=ann1,
            contenu="Bonjour, est-ce que ce livre est dispo?",
            etat=False
        )
        msg2 = Message.objects.create(
            sender=user2,
            receiver=user1,
            annonce=ann1,
            contenu="Oui, encore disponible.",
            etat=False
        )
        # Relation N↔N réponses
        msg1.reponses.add(msg2)

        self.stdout.write(self.style.SUCCESS("✅ Seed complet terminé !"))

