from sqlalchemy import Column, Integer, String

from backend.validation import get_validation_config


USERNAME_MAX_LEN = get_validation_config().username_max_len
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(USERNAME_MAX_LEN), unique=True, index=True, nullable=False)
    password = Column(String(128), nullable=False)
