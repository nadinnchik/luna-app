from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# Auth Schemas
class TelegramAuthRequest(BaseModel):
    init_data: str
    dev_user_id: Optional[int] = None  # only allowed in local dev / testing


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


# Natal Data
class NatalDataUpdate(BaseModel):
    name: str
    birth_date: str
    birth_time: Optional[str] = "12:00"
    birth_city: Optional[str] = "Не указан"
    sun_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    asc_sign: Optional[str] = None


# Child Schemas
class ChildCreate(BaseModel):
    name: str
    birth_date: str
    birth_time: Optional[str] = "12:00"
    birth_city: Optional[str] = "Не указан"
    sun_sign: Optional[str] = None


class ChildOut(BaseModel):
    id: int
    name: str
    birth_date: str
    birth_time: Optional[str] = None
    birth_city: Optional[str] = None
    sun_sign: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Quiz Schemas
class QuizUpdate(BaseModel):
    q_rel: Optional[str] = None
    q_job: Optional[str] = None
    q_focus: Optional[str] = None


class QuizOut(BaseModel):
    q_rel: Optional[str] = None
    q_job: Optional[str] = None
    q_focus: Optional[str] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Purchase Schemas
class PurchaseCreate(BaseModel):
    product_id: str
    price: Optional[int] = None
    target_child_id: Optional[int] = None
    analysis_data: Optional[dict] = None


class PurchaseOut(BaseModel):
    id: int
    product_id: str
    status: str
    target_child_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# User Profile Schemas
class UserOut(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_city: Optional[str] = None
    sun_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    asc_sign: Optional[str] = None
    children: List[ChildOut] = []
    quiz: Optional[QuizOut] = None
    purchases: List[PurchaseOut] = []

    class Config:
        from_attributes = True


# Analytics Event Schema
class AnalyticsEventSchema(BaseModel):
    event: str
    userId: Optional[str] = None
    timestamp: Optional[str] = None
    payload: Optional[dict] = None
