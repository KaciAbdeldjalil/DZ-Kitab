import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal, engine
from app.models.book import Book, Announcement, BookCategoryEnum, BookConditionEnum, AnnouncementStatusEnum
from app.models.user import User
from sqlalchemy import text

def seed():
    session = SessionLocal()
    try:
        # 1. CLEANUP
        print("Cleaning up database (handling FK constraints)...")
        session.execute(text("DELETE FROM wishlist"))
        session.execute(text("DELETE FROM favorites"))
        session.execute(text("DELETE FROM ratings"))
        session.execute(text("DELETE FROM book_condition_scores"))
        session.execute(text("DELETE FROM notifications"))
        session.execute(text("DELETE FROM messages"))
        session.execute(text("DELETE FROM announcements"))
        session.execute(text("DELETE FROM books"))
        session.commit()

        # 2. GET A VALID USER
        user = session.query(User).filter(User.username == 'jalil').first()
        if not user:
            user = session.query(User).first()
        
        if not user:
            print("ERROR: No user found. Please create a user first.")
            return

        print(f"Using User ID: {user.id} ({user.username})")

        # 3. DATA DEFINITION
        data = {
            BookCategoryEnum.INFORMATIQUE: [
                {"title": "Clean Code", "isbn": "9780132350884", "authors": "Robert C. Martin", "description": "A Handbook of Agile Software Craftsmanship", "price": 4500},
                {"title": "Introduction to Algorithms", "isbn": "9780262033848", "authors": "Thomas H. Cormen", "description": "The standard reference for algorithms.", "price": 8500},
                {"title": "The Pragmatic Programmer", "isbn": "9780135957059", "authors": "Andrew Hunt, David Thomas", "description": "Your journey to mastery.", "price": 5000}
            ],
            BookCategoryEnum.PHYSIQUE: [
                {"title": "The Feynman Lectures on Physics", "isbn": "9780465024147", "authors": "Richard Feynman", "description": "The most famous textbook in physics.", "price": 12000},
                {"title": "University Physics", "isbn": "9780321973610", "authors": "Young and Freedman", "description": "Comprehensive physics textbook.", "price": 9500}
            ],
            BookCategoryEnum.MATHEMATIQUES: [
                {"title": "Calculus", "isbn": "9781285740621", "authors": "James Stewart", "description": "Standard calculus text.", "price": 7500},
                {"title": "Linear Algebra Done Right", "isbn": "9783319110790", "authors": "Sheldon Axler", "description": "Deep dive into linear algebra.", "price": 4000}
            ],
            BookCategoryEnum.MEDECINE: [
                {"title": "Gray's Anatomy", "isbn": "9780702052309", "authors": "Susan Standring", "description": "The anatomical basis of clinical practice.", "price": 15000},
                {"title": "Harrison's Principles of Internal Medicine", "isbn": "9781259644030", "authors": "Dennis Kasper", "description": "Leading internal medicine guide.", "price": 18000}
            ],
            BookCategoryEnum.ECONOMIE: [
                {"title": "Capital in the Twenty-First Century", "isbn": "9780674430006", "authors": "Thomas Piketty", "description": "Analysis of wealth and income inequality.", "price": 3500},
                {"title": "Economics", "isbn": "9781260225587", "authors": "Paul Samuelson", "description": "Foundation of modern economics.", "price": 6000}
            ]
        }

        # 4. INSERTION
        for category, books_list in data.items():
            print(f"Seeding category: {category}")
            for item in books_list:
                # Create Book
                book = Book(
                    isbn=item["isbn"],
                    title=item["title"],
                    authors=item["authors"],
                    description=item["description"],
                    cover_image_url=f"https://covers.openlibrary.org/b/isbn/{item['isbn']}-L.jpg",
                    language="fr",
                    categories=category.value
                )
                session.add(book)
                session.flush() # Get ID

                # Create Announcement
                announcement = Announcement(
                    book_id=book.id,
                    user_id=user.id,
                    price=item["price"],
                    market_price=item["price"] + 1000,
                    condition=BookConditionEnum.BON_ETAT,
                    category=category,
                    status=AnnouncementStatusEnum.ACTIVE,
                    description=f"Excellent book for {category.value} students.",
                    location="Alger, Algerie"
                )
                session.add(announcement)
        
        session.commit()
        print("Database seeded successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed()
