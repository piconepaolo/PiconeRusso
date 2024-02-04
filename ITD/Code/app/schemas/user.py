import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, model_validator
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


def validate_name(v: str):
    if len(v) > 20:
        raise ValueError("Name must be at most 20 characters long")
    pattern = r"^[a-zA-Z\s']+$"
    if not re.match(pattern, v):
        raise ValueError("Name must only contain letters")
    return v.title()


SecurePassword = Annotated[str, AfterValidator(check_password)]
PolimiEmail = Annotated[
    EmailStr, AfterValidator(is_polimi_account), AfterValidator(lower_case)
]
Name = Annotated[str, AfterValidator(validate_name)]


class UserInfo(BaseModel):
    email: PolimiEmail
    first_name: Name
    last_name: Name
    github_username: str


class UserBase(UserInfo):
    is_educator: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserInfo):
    password: SecurePassword


class UserCreateDB(UserBase, UserCreate):
    pass


class User(UserBase, UserCreate):
    id: PyObjectId = Field(alias="_id")


class UserResponse(UserBase):
    pass


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
