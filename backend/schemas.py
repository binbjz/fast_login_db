from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator

from backend.validation import (
    validate_login_username,
    validate_password,
    validate_password_not_equal,
    validate_username,
)


class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str) -> str:
        return validate_username(value)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        return validate_password(value)

    @model_validator(mode="after")
    def _validate_username_password_pair(self):
        validate_password_not_equal(self.username, self.password)
        return self


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def _validate_login_username(cls, value: str) -> str:
        return validate_login_username(value)


class UserInDB(BaseModel):
    id: int
    username: str


class LoginSuccess(BaseModel):
    msg: str
    user_id: int
    username: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: datetime


class SessionInfo(BaseModel):
    user_id: int
    username: str
    expires_in: int
    expires_at: datetime


class LogoutResult(BaseModel):
    msg: str
