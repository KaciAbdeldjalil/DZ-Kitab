# app/models/user.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UniversityEnum(enum.Enum):
    ESTIN = "ESTIN"
    ESI = "ESI"
    EPAU = "EPAU"
    USTHB = "USTHB"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    university = Column(Enum(UniversityEnum), nullable=True)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with announcements
    announcements = relationship("Announcement", back_populates="user", cascade="all, delete-orphan")

    # Relations pour les ratings
    ratings_given = relationship(
        "Rating",
        foreign_keys="Rating.buyer_id",
        back_populates="buyer",
        cascade="all, delete-orphan"
    )

    ratings_received = relationship(
        "Rating",
        foreign_keys="Rating.seller_id",
        back_populates="seller",
        cascade="all, delete-orphan"
    )

    seller_stats = relationship(
        "SellerStats",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Relations pour les suspensions (à implémenter plus tard)
    # suspensions = relationship(
    #     "UserSuspension",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

    # rating_alerts = relationship(
    #     "RatingAlert",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
