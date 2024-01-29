from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pymongo.database import Database

from app import crud, schemas
from app.api import deps
from app.core import config, security
from app.core.config import settings
from app.database import mongo_client
from starlette.config import environ

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


def get_db() -> Database:
    if environ.get("TESTING"):
        return mongo_client.ckb_test
    return mongo_client.ckb


def get_current_user(
    token: Annotated[str, Depends(deps.oauth2_scheme)], db=Depends(get_db)
) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    session_invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.security_settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    token_invalidated = crud.is_token_invalidated(db, token)
    if user is None:
        raise credentials_exception
    if token_invalidated:
        raise session_invalid
    return user


def get_current_educator(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if not current_user.is_educator:
        raise HTTPException(
            status_code=401, detail="The user doesn't have enough privileges"
        )
    return current_user
