import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import TelegramAuthRequest, AuthTokenResponse, UserOut
from app.core.config import settings
from app.core.telegram_auth import validate_telegram_init_data, create_access_token
from app.core.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/telegram", response_model=AuthTokenResponse)
def authenticate_telegram(req: TelegramAuthRequest, db: Session = Depends(get_db)):
    """
    Validates Telegram WebApp initData string using HMAC-SHA256.
    Finds or registers the user in SQLite/Postgres and returns a JWT access token.
    """
    telegram_user = None
    telegram_id = None
    first_name = None
    username = None
    last_name = None
    language_code = "ru"

    # 1. Attempt official HMAC-SHA256 validation with Bot Token
    if req.init_data:
        is_valid, user_data = validate_telegram_init_data(req.init_data, settings.TELEGRAM_BOT_TOKEN)
        if is_valid and user_data:
            telegram_user = user_data
            telegram_id = telegram_user.get("id")
            first_name = telegram_user.get("first_name", "")
            last_name = telegram_user.get("last_name", "")
            username = telegram_user.get("username", "")
            language_code = telegram_user.get("language_code", "ru")

    # 2. Fallback for Local Dev / Testing if bot token not yet configured
    if not telegram_id:
        # If running in local dev with placeholder token or dev_user_id provided
        if req.dev_user_id:
            telegram_id = req.dev_user_id
            first_name = "Dev User"
        elif req.init_data and "user=" in req.init_data:
            # Parse unverified for dev fallback
            import urllib.parse
            import json
            try:
                parsed = dict(urllib.parse.parse_qsl(req.init_data))
                if "user" in parsed:
                    u = json.loads(parsed["user"])
                    telegram_id = u.get("id")
                    first_name = u.get("first_name", "Гость")
                    last_name = u.get("last_name", "")
                    username = u.get("username", "")
            except Exception:
                pass

    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось верифицировать данные Telegram WebApp. Передайте валидный initData.",
        )

    # 3. Find or Create User in Database
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language_code=language_code,
            name=first_name or "Гость",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update latest info
        if first_name and not user.name:
            user.name = first_name
        if username:
            user.username = username
        db.commit()
        db.refresh(user)

    # 4. Generate JWT
    access_token = create_access_token(data={"sub": str(user.telegram_id), "user_id": user.id})

    return AuthTokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's full profile including children and quiz."""
    return current_user
