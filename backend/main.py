import bcrypt
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import select, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:pg-auth@10.211.55.5:5432/postgres"
primary_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
Base = declarative_base()


class User(Base):
    """
    User model, mapping to the 'users' table in the database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # User ID
    username = Column(String(16), unique=True, index=True, nullable=False)  # Username
    password = Column(String(128), nullable=False)  # Password (hashed)


class UserInDB(BaseModel):
    """
    User database model for interaction.
    """
    id: int  # User ID
    username: str  # Username


class UserCreate(BaseModel):
    """
    Model for new user registration requests.
    """
    username: str  # Username
    password: str  # Password


class UserLogin(BaseModel):
    """
    Model for user login requests.
    """
    username: str  # Username
    password: str  # Password


async def setup_db():
    """
    Create database tables. Called upon application startup.
    """
    async with primary_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """
    Dependency function to generate a database session for dependency injection.
    """
    async_session = sessionmaker(bind=primary_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


app = FastAPI(debug=True)

# CORS middleware settings
origins = ["http://localhost:8080", "http://192.168.3.6:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    Initialize the database when the application starts.
    """
    await setup_db()


@app.post("/users/", response_model=UserInDB)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    :param user: UserCreate, contains username and password.
    :param db: AsyncSession, a database session.
    :return: UserInDB, returns registered user information.
    """
    query = select(User).where(text("username = :username")).params(username=user.username)
    db_user = await db.execute(query)
    db_user = db_user.fetchone()

    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    db_user = User(username=user.username, password=hashed_password.decode())

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except Exception as ex:
        await db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Error interacting with the database during registration: {str(ex)}")

    return UserInDB(id=db_user.id, username=db_user.username)


@app.post("/login/")
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Validate user login.
    :param request: UserLogin, contains username and password.
    :param db: AsyncSession, a database session.
    :return: Dictionary, contains login message.
    """
    query = select(User.password).where(text("username = :username")).params(username=request.username)
    db_user = await db.execute(query)
    db_user = db_user.fetchone()

    if not db_user:
        raise HTTPException(status_code=404, detail="该用户不存在,请注册后重新登录")

    if db_user and bcrypt.checkpw(request.password.encode(), db_user[0].encode()):
        return {"msg": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
