from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    value: str


class TokenInDb(BaseModel):
    """This model is used to store the token in the database."""

    access_token: str
    email: Optional[str] = None
    valid: bool = True
