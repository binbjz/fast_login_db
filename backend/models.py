from sqlalchemy import Column, Integer, String

from backend.database import Base
from backend.limits import USERNAME_DB_MAX_LEN


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(USERNAME_DB_MAX_LEN), unique=True, index=True, nullable=False)
    password = Column(String(128), nullable=False)
