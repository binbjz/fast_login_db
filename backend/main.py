import os
import secrets
import heapq
import bcrypt
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db, setup_db
from backend.models import User
from backend.schemas import (
    LoginSuccess,
    LogoutResult,
    SessionInfo,
    UserCreate,
    UserInDB,
    UserLogin,
)


@asynccontextmanager
async def app_lifespan(app_instance: FastAPI):
    print("Application starting up...")
    await setup_db()
    try:
        yield
    finally:
        print("Application shutting down...")


def _session_ttl_seconds() -> int:
    raw = os.getenv("SESSION_TTL_SECONDS", "1800")
    try:
        ttl = int(raw)
    except ValueError:
        ttl = 1800
    return max(ttl, 60)


APP_DEBUG = os.getenv("APP_DEBUG", "false").lower() in {"1", "true", "yes"}
SESSION_TTL_SECONDS = _session_ttl_seconds()
app = FastAPI(lifespan=app_lifespan, debug=APP_DEBUG)

CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "").lower() in {"1", "true", "yes"}
raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
if raw_origins.strip():
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
else:
    origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://0.0.0.0:8080",
        "http://192.168.65.1:8080",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if CORS_ALLOW_ALL else origins,
    allow_credentials=False if CORS_ALLOW_ALL else True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass
class AuthSession:
    user_id: int
    username: str
    expires_at: datetime


SESSIONS: dict[str, AuthSession] = {}
SESSION_EXPIRY_HEAP: list[tuple[float, str]] = []


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _cleanup_expired_sessions(now: datetime | None = None) -> None:
    current = now or _utc_now()
    now_ts = current.timestamp()
    while SESSION_EXPIRY_HEAP and SESSION_EXPIRY_HEAP[0][0] <= now_ts:
        _, token = heapq.heappop(SESSION_EXPIRY_HEAP)
        session = SESSIONS.get(token)
        if not session:
            continue
        if session.expires_at.timestamp() <= now_ts:
            SESSIONS.pop(token, None)


def _create_session(user_id: int, username: str) -> tuple[str, AuthSession]:
    now = _utc_now()
    _cleanup_expired_sessions(now)
    token = secrets.token_urlsafe(32)
    session = AuthSession(
        user_id=user_id,
        username=username,
        expires_at=now + timedelta(seconds=SESSION_TTL_SECONDS),
    )
    SESSIONS[token] = session
    heapq.heappush(SESSION_EXPIRY_HEAP, (session.expires_at.timestamp(), token))
    return token, session


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录或会话已过期")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="认证信息格式错误")
    return token.strip()


def _require_session(authorization: str | None) -> tuple[str, AuthSession]:
    token = _extract_bearer_token(authorization)
    now = _utc_now()
    _cleanup_expired_sessions(now)
    session = SESSIONS.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="未登录或会话已过期")
    if session.expires_at <= now:
        SESSIONS.pop(token, None)
        raise HTTPException(status_code=401, detail="未登录或会话已过期")
    return token, session


@app.post("/users/", response_model=UserInDB)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == user.username)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user:
        raise HTTPException(status_code=400, detail="该用户已存在")

    hashed_password = await run_in_threadpool(
        lambda: bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    )
    db_user = User(username=user.username, password=hashed_password)

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="该用户已存在")
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="注册失败，请稍后重试")

    return UserInDB(id=db_user.id, username=db_user.username)


@app.post("/login/", response_model=LoginSuccess)
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == request.username)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=401, detail="用户名或密码不正确")

    is_valid = await run_in_threadpool(
        lambda: bcrypt.checkpw(request.password.encode(), db_user.password.encode())
    )
    if is_valid:
        token, session = _create_session(db_user.id, db_user.username)
        return LoginSuccess(
            msg="登录成功",
            user_id=session.user_id,
            username=db_user.username,
            access_token=token,
            expires_in=SESSION_TTL_SECONDS,
            expires_at=session.expires_at,
        )
    else:
        raise HTTPException(status_code=401, detail="用户名或密码不正确")


@app.get("/me", response_model=SessionInfo)
async def get_current_user_info(authorization: str | None = Header(default=None)):
    _, session = _require_session(authorization)
    expires_in = max(int((session.expires_at - _utc_now()).total_seconds()), 0)
    return SessionInfo(
        user_id=session.user_id,
        username=session.username,
        expires_in=expires_in,
        expires_at=session.expires_at,
    )


@app.post("/logout/", response_model=LogoutResult)
async def logout(authorization: str | None = Header(default=None)):
    token, _ = _require_session(authorization)
    SESSIONS.pop(token, None)
    return LogoutResult(msg="已退出登录")
