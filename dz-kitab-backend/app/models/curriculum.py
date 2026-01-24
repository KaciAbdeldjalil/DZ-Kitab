# app/models/curriculum.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Table d'association many-to-many entre Curriculum et RecommendedBook
curriculum_books = Table(
    'curriculum_books',
    Base.metadata,
    Column('curriculum_id', Integer, ForeignKey('curriculums.id', ondelete='CASCADE')),
    Column('recommended_book_id', Integer, ForeignKey('recommended_books.id', ondelete='CASCADE'))
)

class Curriculum(Base):
    """
    Table pour stocker les cursus universitaires
    Ex: "L1 Informatique USTHB", "1ère Année Médecine Université d'Alger"
    """
    __tablename__ = "curriculums"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # "L1 Informatique USTHB"
    university = Column(String, nullable=False)  # "USTHB"
    field = Column(String, nullable=False)  # "Informatique"
    year = Column(String, nullable=False)  # "1ère année" ou "L1"
    description = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)  # URL de la source du scraping
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    recommended_books = relationship(
        "RecommendedBook",
        secondary=curriculum_books,
        back_populates="curriculums",
        lazy="select"
    )

    def __repr__(self):
        return f"<Curriculum(name={self.name}, university={self.university})>"


class RecommendedBook(Base):
    """
    Table pour stocker les livres recommandés (issus du scraping)
    """
    __tablename__ = "recommended_books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=True)
    isbn = Column(String, nullable=True, index=True)  # Si disponible
    publisher = Column(String, nullable=True)
    edition = Column(String, nullable=True)
    source_url = Column(String, nullable=True)  # URL d'où vient l'info
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    curriculums = relationship(
        "Curriculum",
        secondary=curriculum_books,
        back_populates="recommended_books",
        lazy="select"
    )

    def __repr__(self):
        return f"<RecommendedBook(title={self.title}, author={self.author})>"


class BookCurriculumMatch(Base):
    """
    Table pour lier les livres de la plateforme aux livres recommandés
    Permet de savoir si un Book est recommandé pour un cursus
    """
    __tablename__ = "book_curriculum_matches"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    recommended_book_id = Column(Integer, ForeignKey("recommended_books.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Integer, default=100)  # Score de correspondance (0-100)
    match_method = Column(String, nullable=True)  # "isbn", "title_exact", "title_fuzzy"
    verified = Column(Integer, default=False)  # Vérifié manuellement
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    book = relationship("Book", backref="curriculum_matches", lazy="select")
    recommended_book = relationship("RecommendedBook", backref="book_matches", lazy="select")

    def __repr__(self):
        return f"<BookCurriculumMatch(book_id={self.book_id}, recommended_book_id={self.recommended_book_id})>"
