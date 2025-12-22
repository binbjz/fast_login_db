import os
import bcrypt
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from backend.database import get_db, setup_db
from backend.models import User
from backend.schemas import UserInDB, UserCreate, UserLogin


@asynccontextmanager
async def app_lifespan(app_instance: FastAPI):
    print("Application starting up...")
    await setup_db()
    try:
        yield
    finally:
        print("Application shutting down...")


app = FastAPI(lifespan=app_lifespan, debug=True)

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


@app.post("/users/", response_model=UserInDB)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(text("username = :username")).params(username=user.username)
    result = await db.execute(query)
    db_user_tuple = result.first()

    if db_user_tuple:
        raise HTTPException(status_code=400, detail="该用户已存在")

    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    # db_user: <backend.main_async.User object at 0x1210515d0>
    db_user = User(username=user.username, password=hashed_password.decode())

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except Exception as ex:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"注册-操作数据库错误: {str(ex)}")

    return UserInDB(id=db_user.id, username=db_user.username)


@app.post("/login/")
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(User).where(text("username = :username")).params(username=request.username)
    result = await db.execute(query)
    db_user_tuple = result.first()

    if not db_user_tuple:
        raise HTTPException(status_code=404, detail="该用户不存在,请注册后重新登录")

    db_user = db_user_tuple[0]

    if bcrypt.checkpw(request.password.encode(), db_user.password.encode()):
        return {"msg": "登录成功", "username": db_user.username}
    else:
        raise HTTPException(status_code=401, detail="用户名或密码不正确")
