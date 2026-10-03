import hashlib
import hmac
import json
import urllib.parse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.telegram_auth import validate_telegram_init_data, create_access_token, decode_access_token


def test_telegram_auth_flow():
    bot_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

    # Simulated Telegram user payload
    user_data = {
        "id": 987654321,
        "first_name": "Надежда",
        "last_name": "Астро",
        "username": "nadinnchik",
        "language_code": "ru"
    }

    raw_params = {
        "auth_date": "1710000000",
        "query_id": "AAHdF60gAAAAAN0XrSB2Yy3s",
        "user": json.dumps(user_data, ensure_ascii=False)
    }

    # Generate valid Telegram HMAC hash
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(raw_params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    raw_params["hash"] = calc_hash
    init_data_string = urllib.parse.urlencode(raw_params)

    print("--- 1. Generated Telegram initData ---")
    print(init_data_string)

    # Validate
    is_valid, parsed_user = validate_telegram_init_data(init_data_string, bot_token)
    print("\n--- 2. Validation Result ---")
    print(f"Is Valid: {is_valid}")
    print(f"Parsed User: {parsed_user}")
    assert is_valid is True
    assert parsed_user["id"] == 987654321

    # Create JWT
    token = create_access_token({"sub": str(parsed_user["id"])})
    print("\n--- 3. Generated JWT Token ---")
    print(token)

    # Decode JWT
    decoded = decode_access_token(token)
    print("\n--- 4. Decoded Token Payload ---")
    print(decoded)
    assert decoded["sub"] == "987654321"

    print("\n✨ All Telegram Auth Verification Tests PASSED Successfully!")


if __name__ == "__main__":
    test_telegram_auth_flow()
