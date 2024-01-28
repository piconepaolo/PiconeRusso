from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: schemas.UserCreate,
    db: deps.Database = Depends(deps.get_db),
):
    if crud.get_user_by_email(email=user.email, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # check if the user is an educator account
    if user.email.endswith("mail.polimi.it"):
        is_educator = False
    else:
        is_educator = True
    new_user = schemas.UserNoId(**user.model_dump(), is_educator=is_educator)
    created_user = crud.create_user(db, new_user, user.password)
    if created_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while creating user",
        )
    return created_user


@router.get("/me", response_model=schemas.UserInDB, response_model_exclude={"password"})
def get_current_user(
    current_user: Annotated[schemas.User, Depends(deps.get_current_user)],
):
    return current_user


@router.post("/logout")
async def logout(
    current_user: Annotated[schemas.User, Depends(deps.get_current_user)],
    db: deps.Database = Depends(deps.get_db),
):
    result = crud.invalidate_tokens(db=db, user=current_user)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )
    return {"detail": "Logout successful"}
