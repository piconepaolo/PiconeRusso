from app import schemas
from app.api import deps
from app.core.config.settings import DatabaseSettings


async def save_authentication_token(
    db: deps.Database, token: schemas.TokenInDb
) -> bool:
    token_collection = db[DatabaseSettings.AUTHENTICATION_TOKEN_COLLECTION]
    result = token_collection.insert_one(token.model_dump())
    if result.inserted_id:
        return True
    return False


async def is_token_invalidated(db: deps.Database, token: str) -> bool:
    token_collection = db[DatabaseSettings.AUTHENTICATION_TOKEN_COLLECTION]
    token_verify = schemas.TokenInDb(access_token=token, valid=False)
    token_dump = token_verify.model_dump(exclude_unset=True)
    result = token_collection.find(token_dump).to_list(None)  # type: ignore
    if result:
        return True
    return False


async def invalidate_tokens(
    db: deps.Database,
    user: schemas.User,
) -> bool:
    result = None
    token_collection = db[DatabaseSettings.AUTHENTICATION_TOKEN_COLLECTION]
    result = token_collection.update_many(
        {"email": user.email}, {"$set": {"valid": False}}
    )
    if result and result.modified_count > 0:
        return True
    return False
