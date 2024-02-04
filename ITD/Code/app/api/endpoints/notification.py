from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.Notification,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    notification: schemas.NotificationCreate,
    db: Annotated[deps.Database, Depends(deps.get_db)],
):
    created_notification = crud.create_notification(db, notification)
    if created_notification is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while creating notification",
        )
    return created_notification
