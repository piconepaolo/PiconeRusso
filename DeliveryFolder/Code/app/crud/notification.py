from typing import Optional

from fastapi.encoders import jsonable_encoder

from app import schemas
from app.api import deps
from app.core.config.settings import DatabaseSettings


def create_notification(
    db: deps.Database,
    notification: schemas.NotificationCreate,
) -> Optional[schemas.Notification]:
    notification_collection = db[DatabaseSettings.NOTIFICATION_COLLECTION]
    result = notification_collection.insert_one(jsonable_encoder(notification))
    if not (
        found_notification := notification_collection.find_one(
            {"_id": result.inserted_id}
        )
    ):
        return None
    created_notification = schemas.Notification(**found_notification)
    return created_notification
