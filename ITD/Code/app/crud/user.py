from typing import Optional

from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from app import schemas
from app.api import deps
from app.core.config.settings import DatabaseSettings
from app.core.security import get_password_hash


def create_user(
    db: deps.Database, user: schemas.UserCreateDB
) -> Optional[schemas.User]:
    user.password = get_password_hash(user.password)
    users_collection = db[DatabaseSettings.USER_COLLECTION]
    result = users_collection.insert_one(jsonable_encoder(user))
    if not (found_user := users_collection.find_one({"_id": result.inserted_id})):
        return None
    created_user = schemas.User(**found_user)
    return created_user


def get_users(
    db: deps.Database,
    skip: int = 0,
    limit: int = 100,
) -> list[schemas.User]:
    user_colletion = db[DatabaseSettings.USER_COLLECTION]
    users_cursor = user_colletion.find().limit(limit).skip(skip)
    users = [schemas.User(**user) for user in users_cursor]
    return users


def get_user_by_id(db: deps.Database, user_id: str) -> Optional[schemas.User]:
    user = db[DatabaseSettings.USER_COLLECTION].find_one({"_id": ObjectId(user_id)})
    if user is None:
        return None
    user = schemas.User(**user)
    return user


def get_user_by_email(db: deps.Database, email: str) -> Optional[schemas.User]:
    user = db[DatabaseSettings.USER_COLLECTION].find_one({"email": email})
    if user is None:
        return None
    user = schemas.User(**user)
    return user


def update_password(db: deps.Database, email: str, password: str) -> bool:
    new_hashed_password = get_password_hash(password)
    result = db[DatabaseSettings.USER_COLLECTION].update_one(
        {"email": email}, {"$set": {"password": new_hashed_password}}
    )
    return result.modified_count > 0


def update_user(db: deps.Database, user_uuid: str, **kwargs) -> Optional[int]:
    if not db[DatabaseSettings.USER_COLLECTION].find_one({"Uuid": user_uuid}):
        return None
    result = db[DatabaseSettings.USER_COLLECTION].update_one(
        {"Uuid": user_uuid}, {"$set": kwargs}
    )
    return result.modified_count > 0
