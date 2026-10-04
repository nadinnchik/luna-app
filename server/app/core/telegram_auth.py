import base64
import hashlib
import hmac
import json
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any

try:
    from jose import jwt, JWTError
    HAS_JOSE = True
except ImportError:
    HAS_JOSE = False
    class JWTError(Exception):
        pass

from app.core.config import settings


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _pure_jwt_encode(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    
    # Convert datetime objects to timestamps if needed
    cleaned_payload = {}
    for k, v in payload.items():
        if isinstance(v, datetime):
            cleaned_payload[k] = int(v.timestamp())
        else:
            cleaned_payload[k] = v
            
    p_b64 = _b64url_encode(json.dumps(cleaned_payload, separators=(",", ":")).encode("utf-8"))
    msg = f"{h_b64}.{p_b64}".encode("utf-8")
    sig = _b64url_encode(hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).digest())
    return f"{h_b64}.{p_b64}.{sig}"


def _pure_jwt_decode(token: str, secret: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise JWTError("Invalid token format")
    h_b64, p_b64, sig_b64 = parts
    msg = f"{h_b64}.{p_b64}".encode("utf-8")
    expected_sig = _b64url_encode(hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).digest())
    if not hmac.compare_digest(sig_b64, expected_sig):
        raise JWTError("Signature verification failed")
    payload = json.loads(_b64url_decode(p_b64).decode("utf-8"))
    if "exp" in payload and payload["exp"] < time.time():
        raise JWTError("Token expired")
    return payload


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
    if HAS_JOSE:
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return _pure_jwt_encode(to_encode, settings.JWT_SECRET_KEY)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        if HAS_JOSE:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return _pure_jwt_decode(token, settings.JWT_SECRET_KEY)
    except Exception:
        return None
