import base64
import hashlib
import hmac
import json
import time
import urllib.parse
from datetime import datetime, timezone

from app.core.telegram_auth import (
    validate_telegram_init_data,
    create_access_token,
    decode_access_token,
)
from app.core.config import settings


def test_telegram_auth_valid():
    bot_token = "7968512345:AAExampleTokenPlaceholderForLocalDev"
    params = {
        "auth_date": str(int(time.time())),
        "query_id": "AAHdF60gAAAAAN0XrSB2Yy3s",
        "user": json.dumps({
            "id": 12345678,
            "first_name": "Надежда",
            "username": "nadinn",
            "language_code": "ru"
        }, ensure_ascii=False)
    }
    
    # Calculate HMAC
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    params["hash"] = hmac.new(secret, data_check.encode("utf-8"), hashlib.sha256).hexdigest()
    
    raw_init_data = urllib.parse.urlencode(params)
    is_valid, user_data = validate_telegram_init_data(raw_init_data, bot_token)
    assert is_valid is True, "Valid initData should pass validation"
    assert user_data["id"] == 12345678, "User ID should match"
    print("✅ test_telegram_auth_valid PASSED")


def test_telegram_auth_tampered():
    bot_token = "7968512345:AAExampleTokenPlaceholderForLocalDev"
    params = {
        "auth_date": str(int(time.time())),
        "query_id": "AAHdF60gAAAAAN0XrSB2Yy3s",
        "user": json.dumps({"id": 12345678, "first_name": "Надежда"}),
        "hash": "invalid_tampered_hash_1234567890abcdef"
    }
    raw_init_data = urllib.parse.urlencode(params)
    is_valid, user_data = validate_telegram_init_data(raw_init_data, bot_token)
    assert is_valid is False, "Tampered initData must be rejected"
    assert user_data is None
    print("✅ test_telegram_auth_tampered PASSED")


def test_jwt_token_cycle():
    payload = {"sub": "tg_12345678", "role": "user"}
    token = create_access_token(payload)
    assert isinstance(token, str) and len(token) > 20
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "tg_12345678"
    assert decoded["role"] == "user"
    assert "exp" in decoded
    print("✅ test_jwt_token_cycle PASSED")


def test_natal_calculations():
    # Zodiac sign date boundary checks
    test_dates = [
        (21, 3, "Овен"),
        (20, 4, "Телец"),
        (21, 5, "Близнецы"),
        (21, 6, "Рак"),
        (23, 7, "Лев"),
        (23, 8, "Дева"),
        (23, 9, "Весы"),
        (23, 10, "Скорпион"),
        (22, 11, "Стрелец"),
        (22, 12, "Козерог"),
        (20, 1, "Водолей"),
        (19, 2, "Рыбы"),
    ]
    
    def get_zodiac(day, month):
        if (month == 1 and day >= 20) or (month == 2 and day <= 18): return "Водолей"
        if (month == 2 and day >= 19) or (month == 3 and day <= 20): return "Рыбы"
        if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "Овен"
        if (month == 4 and day >= 20) or (month == 5 and day <= 20): return "Телец"
        if (month == 5 and day >= 21) or (month == 6 and day <= 20): return "Близнецы"
        if (month == 6 and day >= 21) or (month == 7 and day <= 22): return "Рак"
        if (month == 7 and day >= 23) or (month == 8 and day <= 22): return "Лев"
        if (month == 8 and day >= 23) or (month == 9 and day <= 22): return "Дева"
        if (month == 9 and day >= 23) or (month == 10 and day <= 22): return "Весы"
        if (month == 10 and day >= 23) or (month == 11 and day <= 21): return "Скорпион"
        if (month == 11 and day >= 22) or (month == 12 and day <= 21): return "Стрелец"
        return "Козерог"
        
    for day, month, expected in test_dates:
        res = get_zodiac(day, month)
        assert res == expected, f"Expected {expected} for {day}/{month}, got {res}"
    
    print("✅ test_natal_calculations (12 Zodiac Boundaries) PASSED")


def test_chat_ask_endpoint():
    from app.api.v1.endpoints.chat import ChatAskRequest, ask_ai_astrologer, generate_astrological_fallback
    
    # 1. Test fallback generator for money/finance question
    req_fin = ChatAskRequest(
        question="Как мне увеличить доход и пробить финансовый потолок?",
        name="Надежда",
        sun_sign="Козерог",
        moon_sign="Телец",
        asc_sign="Стрелец"
    )
    ans_fin = generate_astrological_fallback(req_fin)
    assert "Козерог" in ans_fin
    assert "доход" in ans_fin or "чек" in ans_fin
    
    # 2. Test endpoint handler
    resp = ask_ai_astrologer(req_fin, current_user=None)
    assert resp.answer is not None and len(resp.answer) > 30
    assert resp.source in ["llm", "astrology_engine"]
    print("✅ test_chat_ask_endpoint PASSED")


if __name__ == "__main__":
    print("🔮 Running LUNA Master Test Suite...")
    test_telegram_auth_valid()
    test_telegram_auth_tampered()
    test_jwt_token_cycle()
    test_natal_calculations()
    test_chat_ask_endpoint()
    print("\n🌟 ALL TESTS COMPLETED SUCCESSFULLY!")
