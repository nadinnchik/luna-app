import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    class BaseSettings:
        pass


class Settings(BaseSettings):
    PROJECT_NAME: str = "LUNA Astrologer API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Telegram Bot Token (used to validate initData HMAC)
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "7968512345:AAExampleTokenPlaceholderForLocalDev")

    # JWT secret for session tokens
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "luna_celestial_secret_change_in_production_2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30

    # Database URL: default is local SQLite; in Railway/production use Postgres
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./luna.db")

    # CORS configuration (allow Telegram WebApp origins & GitHub Pages)
    CORS_ORIGINS: list = [
        "https://nadinnchik.github.io",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000",
        "*"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
