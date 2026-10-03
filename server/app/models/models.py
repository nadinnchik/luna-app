from datetime import datetime, timezone
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="ru")

    # Natal / Birth profile
    name = Column(String(255), nullable=True)
    birth_date = Column(String(50), nullable=True)
    birth_time = Column(String(50), nullable=True)
    birth_city = Column(String(255), nullable=True)
    sun_sign = Column(String(50), nullable=True)
    moon_sign = Column(String(50), nullable=True)
    asc_sign = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")
    quiz = relationship("QuizProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    purchases = relationship("PurchasedProduct", back_populates="user", cascade="all, delete-orphan")


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    birth_date = Column(String(50), nullable=False)
    birth_time = Column(String(50), nullable=True)
    birth_city = Column(String(255), nullable=True)
    sun_sign = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    parent = relationship("User", back_populates="children")


class QuizProfile(Base):
    __tablename__ = "quiz_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    q_rel = Column(String(255), nullable=True)
    q_job = Column(String(255), nullable=True)
    q_focus = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="quiz")


class PurchasedProduct(Base):
    __tablename__ = "purchased_products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(50), nullable=False)  # e.g., 'natal', 'synastry', 'finance', 'kids'
    target_child_id = Column(Integer, nullable=True)
    status = Column(String(50), default="active")
    analysis_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="purchases")
