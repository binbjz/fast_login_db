from pydantic import BaseModel, field_validator, model_validator

from backend.validation import (
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


class UserInDB(BaseModel):
    id: int
    username: str
