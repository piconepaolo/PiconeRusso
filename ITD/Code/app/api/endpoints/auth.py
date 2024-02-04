from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, schemas
from app.api import deps
from app.core import security

router = APIRouter()


async def authenticate_user(username: str, password: str, db: deps.Database):
    user = crud.get_user_by_email(db, username)
    if not user:
        return False
    if not security.verify_password(password, user.password):
        return False
    return user


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: deps.Database = Depends(deps.get_db),
):
    user = await authenticate_user(form_data.username.lower(), form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    token_storage = schemas.TokenInDb(
        email=user.email, access_token=access_token, valid=True
    )
    crud.save_authentication_token(db, token_storage)
    return {"access_token": access_token, "token_type": "bearer"}
