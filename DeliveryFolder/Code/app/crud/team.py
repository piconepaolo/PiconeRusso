from typing import Optional

from fastapi.encoders import jsonable_encoder

from app import schemas
from app.api import deps
from app.core.config.settings import DatabaseSettings


def create_team(
    db: deps.Database, team: schemas.TeamCreate, user: schemas.User
) -> Optional[schemas.Team]:
    team_collection = db[DatabaseSettings.TEAM_COLLECTION]
    result = team_collection.insert_one(jsonable_encoder(team))
    if not (found_team := team_collection.find_one({"_id": result.inserted_id})):
        return None
    created_team = schemas.Team(**found_team)
    return created_team


def add_team_members(
    db: deps.Database,
    users_id: list[schemas.PyObjectId],
    team_id: schemas.PyObjectId,
    inviter: schemas.User,
) -> bool:
    team_collection = db[DatabaseSettings.TEAM_COLLECTION]
    if team := get_team(db, team_id):
        if inviter.id not in team.members and len(team.members) > 0:
            return False
        already_members = team.members
        users = [user_id for user_id in users_id if user_id not in already_members]
        users.extend(already_members)
        result = team_collection.update_one(
            {"_id": team_id},
            {"$set": {"members": users}},
        )
        if result.modified_count != 0:
            return True
    return False


def get_team(db: deps.Database, team_id: schemas.PyObjectId) -> Optional[schemas.Team]:
    team_collection = db[DatabaseSettings.TEAM_COLLECTION]
    if not (found_team := team_collection.find_one({"_id": team_id})):
        return None
    team = schemas.Team(**found_team)
    return team


def set_team_repository(
    db: deps.Database,
    team: schemas.Team,
    repository_link: schemas.url,
    user: schemas.User,
) -> Optional[schemas.Team]:
    if user.id not in team.members:
        return None
    team_collection = db[DatabaseSettings.TEAM_COLLECTION]
    result = team_collection.update_one(
        {"_id": team.id},
        {"$set": {"repository": repository_link}},
    )
    if result.modified_count == 0:
        return None
    return get_team(db, team.id)


def delete_team(db: deps.Database, team: schemas.Team):
    team_collection = db[DatabaseSettings.TEAM_COLLECTION]
    result = team_collection.delete_one({"_id": team.id})
    if result.deleted_count == 0:
        return False
    return True
