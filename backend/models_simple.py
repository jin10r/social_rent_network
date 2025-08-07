"""
Упрощенные модели для тестирования без PostGIS
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint, ARRAY, DECIMAL, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    photo_url = Column(Text, nullable=True)
    age = Column(Integer, CheckConstraint('age >= 18 AND age <= 100'), nullable=True)
    bio = Column(Text, nullable=True)
    price_min = Column(Integer, CheckConstraint('price_min >= 0'), nullable=True)
    price_max = Column(Integer, CheckConstraint('price_max >= price_min'), nullable=True)
    metro_station = Column(String(255), nullable=True)
    # Простые координаты вместо географии
    search_lat = Column(Float, nullable=True)
    search_lon = Column(Float, nullable=True)
    search_radius = Column(Integer, CheckConstraint('search_radius > 0'), nullable=True)  # in meters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    likes_given = relationship("UserLike", foreign_keys="UserLike.liker_id", back_populates="liker")
    likes_received = relationship("UserLike", foreign_keys="UserLike.liked_id", back_populates="liked")
    listing_likes = relationship("ListingLike", back_populates="user")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, CheckConstraint('price >= 0'), nullable=False)
    address = Column(String(500), nullable=True)
    # Простые координаты вместо географии
    lat = Column(Float, nullable=False, index=True)
    lon = Column(Float, nullable=False, index=True)
    rooms = Column(Integer, CheckConstraint('rooms > 0'), nullable=True)
    area = Column(DECIMAL(7, 2), CheckConstraint('area > 0'), nullable=True)
    floor = Column(Integer, nullable=True)
    total_floors = Column(Integer, nullable=True)
    metro_station = Column(String(255), nullable=True)
    metro_distance = Column(Integer, nullable=True)  # in meters
    photos = Column(Text, nullable=True)  # Строка вместо массива для SQLite
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    likes = relationship("ListingLike", back_populates="listing")


class UserLike(Base):
    __tablename__ = "user_likes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    liker_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    liked_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    liker = relationship("User", foreign_keys=[liker_id], back_populates="likes_given")
    liked = relationship("User", foreign_keys=[liked_id], back_populates="likes_received")

    __table_args__ = (
        CheckConstraint('liker_id != liked_id', name='check_no_self_like'),
    )


class UserMatch(Base):
    __tablename__ = "user_matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user1_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])

    __table_args__ = (
        CheckConstraint('user1_id != user2_id', name='check_no_self_match'),
    )


class ListingLike(Base):
    __tablename__ = "listing_likes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id = Column(String, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="listing_likes")
    listing = relationship("Listing", back_populates="likes")