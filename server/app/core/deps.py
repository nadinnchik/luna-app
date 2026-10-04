from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.core.telegram_auth import decode_access_token


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует заголовок авторизации Bearer",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "").replace("bearer ", "").strip()
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истекший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    telegram_id = payload.get("sub")
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректная полезная нагрузка токена",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.telegram_id == int(telegram_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return user


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not authorization:
        return None
    try:
        token = authorization.replace("Bearer ", "").replace("bearer ", "").strip()
        payload = decode_access_token(token)
        if not payload or not payload.get("sub"):
            return None
        telegram_id = payload.get("sub")
        return db.query(User).filter(User.telegram_id == int(telegram_id)).first()
    except Exception:
        return None
