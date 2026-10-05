from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User, PurchasedProduct
from app.schemas.schemas import NatalDataUpdate, UserOut, PurchaseCreate, PurchaseOut
from app.core.deps import get_current_user

router = APIRouter()


@router.put("/natal", response_model=UserOut)
def update_natal_profile(
    data: NatalDataUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Saves or updates the user's birth data (name, date, time, city, Sun, Moon, Ascendant).
    """
    current_user.name = data.name.strip()
    current_user.birth_date = data.birth_date.strip()
    current_user.birth_time = data.birth_time.strip() if data.birth_time else "12:00"
    current_user.birth_city = data.birth_city.strip() if data.birth_city else "Не указан"

    if data.sun_sign:
        current_user.sun_sign = data.sun_sign
    if data.moon_sign:
        current_user.moon_sign = data.moon_sign
    if data.asc_sign:
        current_user.asc_sign = data.asc_sign

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/purchase", response_model=PurchaseOut)
def record_purchase(
    data: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records or updates a one-time product purchase (e.g., 'natal' for LUNA PRO 17 chapters).
    """
    purchase = db.query(PurchasedProduct).filter(
        PurchasedProduct.user_id == current_user.id,
        PurchasedProduct.product_id == data.product_id
    ).first()

    if not purchase:
        purchase = PurchasedProduct(
            user_id=current_user.id,
            product_id=data.product_id,
            target_child_id=data.target_child_id,
            status="active",
            analysis_data=data.analysis_data
        )
        db.add(purchase)
    else:
        purchase.status = "active"
        if data.analysis_data:
            purchase.analysis_data = data.analysis_data

    db.commit()
    db.refresh(purchase)
    return purchase


@router.get("/purchases", response_model=List[PurchaseOut])
def get_user_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the list of active product purchases for the user.
    """
    return db.query(PurchasedProduct).filter(PurchasedProduct.user_id == current_user.id).all()

