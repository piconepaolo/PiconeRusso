import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from pydantic.functional_validators import AfterValidator

from app.core.security import MINIMUM_PASSWORD_LENGTH
from app.schemas.py_object_id import PyObjectId


def check_password(v: str):
    if len(v) < MINIMUM_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MINIMUM_PASSWORD_LENGTH} characters long"
        )
    return v


def is_polimi_account(v: str):
    if v.endswith("@polimi.it") or v.endswith("@mail.polimi.it"):
        return v
    raise ValueError("Email must be a polimi account")


def lower_case(v: str):
    return v.lower()


SecurePassword = Annotated[str, AfterValidator(check_password)]
PolimiEmail = Annotated[
    EmailStr, AfterValidator(is_polimi_account), AfterValidator(lower_case)
]


class UserBase(BaseModel):
    email: PolimiEmail
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=20)


class UserCreate(UserBase):
    @field_validator("first_name", "last_name")
    @classmethod
    def check_name(cls, v: str):
        pattern = r"^[a-zA-Z\s']+$"
        if not re.match(pattern, v):
            raise ValueError("Name must only contain letters")
        return v.title()

    password: SecurePassword


class UserNoId(UserBase):
    is_educator: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserInDB(UserNoId, UserCreate):
    ...


class User(UserNoId):
    id: PyObjectId = Field(alias="_id")


class UserResetPassword(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    password: SecurePassword
    password_confirmation: SecurePassword

    @model_validator(mode="before")
    @classmethod
    def passwords_match(cls, values):
        if values.get("password") != values.get("password_confirmation"):
            raise ValueError("Passwords don't match")
        return values
