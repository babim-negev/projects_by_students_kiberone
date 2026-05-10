#!/usr/bin/env python3
"""Создать пользователя в SQLite (один раз перед первым входом).

Запуск из папки danila-n:

  python scripts/create_user.py <логин> <пароль>
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.database import SessionLocal, engine
from app.models import Base, User
from app.security import hash_password


def main(argv: list[str]) -> None:
    if len(argv) != 3:
        print("Использование: python scripts/create_user.py <логин> <пароль>")
        sys.exit(1)
    username, raw_password = argv[1].strip(), argv[2]
    if not username:
        print("Логин не может быть пустым")
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        exists = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if exists:
            print("Такой пользователь уже есть — выбери другой логин.")
            sys.exit(1)
        db.add(User(username=username, password_hash=hash_password(raw_password)))
        db.commit()
        print("Пользователь создан. Можно открыть сайт и войти.")
    finally:
        db.close()


if __name__ == "__main__":
    main(sys.argv)
