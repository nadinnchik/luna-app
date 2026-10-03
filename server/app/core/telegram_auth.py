import hashlib
import hmac
import json
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any

from jose import jwt, JWTError
from fastapi import HTTPException, status, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

security = HTTPBearer(auto_error=False)


def validate_telegram_init_data(init_data_raw: str, bot_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validates Telegram WebApp initData string using HMAC-SHA256.
    Returns (is_valid, parsed_user_dict).
    """
    if not init_data_raw:
        return False, None

    try:
        # Parse query params
        parsed_params = dict(urllib.parse.parse_qsl(init_data_raw, keep_blank_values=True))
        received_hash = parsed_params.pop("hash", None)

        if not received_hash:
            return False, None

        # Build data_check_string: sorted key=value separated by \n
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_params.items()))

        # Secret key = HMAC_SHA256("WebAppData", bot_token)
        secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()

        # Calculated hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

        if calculated_hash != received_hash:
            return False, None

        # Parse user JSON payload
        user_json = parsed_params.get("user")
        user_data = json.loads(user_json) if user_json else {}

        return True, user_data
    except Exception:
        return False, None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
