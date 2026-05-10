"""Веб-MVP расписания: FastAPI + SQLite + простые страницы."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, get_db
from app.models import Base, Event, User
from app.security import create_token, decode_token, hash_password, verify_password

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def parse_datetime_local(value: str) -> datetime:
    """Строка из <input type='datetime-local'> (часто YYYY-MM-DDTHH:MM или с секундами)."""
    s = value.strip()
    if not s:
        raise ValueError(
            "Выбери дату и время. Если во времени стоит «--:--», укажи часы и минуты (например 15:00)."
        )
    if "T" not in s:
        raise ValueError("Нужны и дата, и время: сначала день в календаре, потом время.")
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            "Неверная дата или время. Не оставляй время пустым — именно из-за этого часто ругается браузер."
        ) from exc


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Расписание (danila-n)", lifespan=lifespan)
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    token = request.cookies.get(settings.cookie_name)
    if not token:
        return None
    try:
        payload = decode_token(token)
        uid = int(payload["sub"])
    except Exception:
        return None
    return db.get(User, uid)


def login_redirect() -> RedirectResponse:
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)


@app.get("/")
def root(user: User | None = Depends(get_current_user)):
    if user is None:
        return login_redirect()
    return RedirectResponse("/day", status_code=status.HTTP_302_FOUND)


@app.get("/login")
def login_page(
    request: Request,
    user: User | None = Depends(get_current_user),
    info: str | None = Query(None),
):
    if user is not None:
        return RedirectResponse("/day", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request, "login.html", {"error": None, "info": info})


@app.post("/login")
def login_post(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    name = username.strip()
    stmt = select(User).where(User.username == name)
    u = db.execute(stmt).scalar_one_or_none()
    if u is None or not verify_password(password, u.password_hash):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Неверный логин или пароль", "info": None},
            status_code=401,
        )
    resp = RedirectResponse("/day", status_code=status.HTTP_302_FOUND)
    ttl = max(1, int(settings.jwt_days * 86400))
    resp.set_cookie(
        settings.cookie_name,
        create_token(u.id),
        httponly=True,
        max_age=ttl,
        samesite="lax",
    )
    return resp


@app.get("/register")
def register_page(request: Request, user: User | None = Depends(get_current_user)):
    if user is not None:
        return RedirectResponse("/day", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request, "register.html", {"error": None})


@app.post("/register")
def register_post(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    password_confirm: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    name = username.strip()
    err: str | None = None
    if len(name) < 2:
        err = "Логин слишком короткий (минимум 2 символа)."
    elif len(name) > 64:
        err = "Логин слишком длинный (максимум 64 символа)."

    min_pw = 4
    if err is None and len(password) < min_pw:
        err = f"Пароль слишком короткий (минимум {min_pw} символа)."
    if err is None and password != password_confirm:
        err = "Пароли не совпали — введи одинаково в оба поля."

    if err is not None:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"error": err},
            status_code=400,
        )

    exists = db.execute(select(User).where(User.username == name)).scalar_one_or_none()
    if exists is not None:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"error": "Такой логин уже занят — придумай другой."},
            status_code=400,
        )

    db.add(User(username=name, password_hash=hash_password(password)))
    db.commit()
    return RedirectResponse("/login?info=registered", status_code=status.HTTP_302_FOUND)


@app.get("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    resp.delete_cookie(settings.cookie_name)
    return resp


def _day_bounds(chosen: date) -> tuple[datetime, datetime]:
    start = datetime(chosen.year, chosen.month, chosen.day)
    return start, start + timedelta(days=1)


def _week_bounds(day_in_week: date) -> tuple[date, date, datetime, datetime]:
    monday = day_in_week - timedelta(days=day_in_week.weekday())
    sunday = monday + timedelta(days=6)
    start = datetime(monday.year, monday.month, monday.day)
    end_exclusive = datetime(sunday.year, sunday.month, sunday.day) + timedelta(days=1)
    return monday, sunday, start, end_exclusive


def _month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    first = date(year, month, 1)
    if month == 12:
        next_first = date(year + 1, 1, 1)
    else:
        next_first = date(year, month + 1, 1)
    start = datetime(first.year, first.month, first.day)
    end_exclusive = datetime(next_first.year, next_first.month, next_first.day)
    return start, end_exclusive


def _events_overlap(
    db: Session,
    user_id: int,
    window_start: datetime,
    window_end_exclusive: datetime,
) -> list[Event]:
    stmt = (
        select(Event)
        .where(
            Event.user_id == user_id,
            Event.starts_at < window_end_exclusive,
            Event.ends_at > window_start,
        )
        .order_by(Event.starts_at)
    )
    return list(db.execute(stmt).scalars().all())


@app.get("/day")
def page_day(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
    d: Optional[str] = Query(None, description="YYYY-MM-DD"),
):
    if user is None:
        return login_redirect()
    chosen = date.fromisoformat(d) if d else date.today()
    start, end_ex = _day_bounds(chosen)
    events = _events_overlap(db, user.id, start, end_ex)
    return templates.TemplateResponse(
        request,
        "day.html",
        {
            "user": user,
            "chosen": chosen,
            "prev": chosen - timedelta(days=1),
            "next": chosen + timedelta(days=1),
            "events": events,
        },
    )


@app.get("/week")
def page_week(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
    w: Optional[str] = Query(None, description="любая дата недели YYYY-MM-DD"),
):
    if user is None:
        return login_redirect()
    base = date.fromisoformat(w) if w else date.today()
    mon, sun, ws, we = _week_bounds(base)
    events = _events_overlap(db, user.id, ws, we)
    return templates.TemplateResponse(
        request,
        "week.html",
        {
            "user": user,
            "monday": mon,
            "sunday": sun,
            "prev_week_anchor": mon - timedelta(days=7),
            "next_week_anchor": mon + timedelta(days=7),
            "events": events,
        },
    )


@app.get("/month")
def page_month(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
    y: Optional[int] = Query(None),
    m: Optional[int] = Query(None),
):
    if user is None:
        return login_redirect()
    today = date.today()
    year = y or today.year
    month = m or today.month
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="месяц должен быть от 1 до 12")

    ms, me = _month_bounds(year, month)
    events = _events_overlap(db, user.id, ms, me)

    first_this = date(year, month, 1)
    prev_last = first_this - timedelta(days=1)
    if month == 12:
        nxt_first = date(year + 1, 1, 1)
    else:
        nxt_first = date(year, month + 1, 1)

    return templates.TemplateResponse(
        request,
        "month.html",
        {
            "user": user,
            "year": year,
            "month": month,
            "prev_y": prev_last.year,
            "prev_m": prev_last.month,
            "next_y": nxt_first.year,
            "next_m": nxt_first.month,
            "events": events,
        },
    )


@app.get("/events/new")
def events_new_form(request: Request, user: User | None = Depends(get_current_user)):
    if user is None:
        return login_redirect()
    return templates.TemplateResponse(
        request,
        "event_new.html",
        {"user": user, "error": None},
    )


@app.post("/events/new")
def events_new_save(
    request: Request,
    title: Annotated[str, Form()],
    starts_at: Annotated[str, Form()],
    ends_at: Annotated[str, Form()],
    note: Annotated[str, Form()] = "",
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user is None:
        return login_redirect()
    try:
        start_dt = parse_datetime_local(starts_at)
        end_dt = parse_datetime_local(ends_at)
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "event_new.html",
            {"user": user, "error": str(exc)},
            status_code=400,
        )
    if end_dt <= start_dt:
        return templates.TemplateResponse(
            request,
            "event_new.html",
            {
                "user": user,
                "error": "Время окончания должно быть позже начала.",
            },
            status_code=400,
        )

    ev = Event(
        user_id=user.id,
        title=title.strip()[:256],
        starts_at=start_dt,
        ends_at=end_dt,
        note=(note.strip() or None),
    )
    db.add(ev)
    db.commit()
    return RedirectResponse("/day", status_code=status.HTTP_302_FOUND)


@app.post("/events/{event_id}/delete")
def events_delete(event_id: int, user: User | None = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        return login_redirect()
    ev = db.get(Event, event_id)
    if ev is None or ev.user_id != user.id:
        raise HTTPException(status_code=404)
    db.delete(ev)
    db.commit()
    return RedirectResponse("/day", status_code=status.HTTP_302_FOUND)
