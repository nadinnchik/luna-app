from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User, Child
from app.schemas.schemas import ChildCreate, ChildOut
from app.core.deps import get_current_user

router = APIRouter()


@router.get("", response_model=List[ChildOut])
def get_children(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all children associated with the current user."""
    return current_user.children


@router.post("", response_model=ChildOut, status_code=status.HTTP_201_CREATED)
def add_child(
    data: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new child to the user profile."""
    child = Child(
        user_id=current_user.id,
        name=data.name.strip(),
        birth_date=data.birth_date.strip(),
        birth_time=data.birth_time.strip() if data.birth_time else "12:00",
        birth_city=data.birth_city.strip() if data.birth_city else "Не указан",
        sun_sign=data.sun_sign
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a child by ID."""
    child = db.query(Child).filter(Child.id == child_id, Child.user_id == current_user.id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль ребёнка не найден",
        )
    db.delete(child)
    db.commit()
    return None
