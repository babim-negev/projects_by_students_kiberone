"""Настройки из .env (рядом с папкой app)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


class Settings:
    secret_key: str = os.getenv("SECRET_KEY", "DEV_ONLY_CHANGE_ME_SECRET_KEY_PLEASE_ENV")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./danila_schedule.db")
    jwt_days: float = float(os.getenv("JWT_DAYS", "14"))
    cookie_name: str = os.getenv("COOKIE_NAME", "danila_schedule")


settings = Settings()
