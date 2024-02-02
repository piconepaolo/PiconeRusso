from typing import Optional

from fastapi.encoders import jsonable_encoder

from app import schemas, utils
from app.api import deps
from app.core.config.settings import DatabaseSettings


def create_tournament(
    db: deps.Database, tournament: schemas.TournamentCreate
) -> Optional[schemas.Tournament]:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.insert_one(jsonable_encoder(tournament))
    if not result.inserted_id:
        return None
    return schemas.Tournament(**tournament.model_dump(), _id=result.inserted_id)


def get_tournament(
    db: deps.Database, tournament_id: schemas.PyObjectId
) -> Optional[schemas.Tournament]:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.find_one({"_id": tournament_id})
    if not result:
        return None
    return schemas.Tournament(**result)


def update_tournament(
    db: deps.Database,
    tournament: schemas.TournamentUpdate,
    tournament_id: schemas.PyObjectId,
) -> Optional[schemas.Tournament]:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.update_one(
        {"_id": tournament_id}, {"$set": jsonable_encoder(tournament)}
    )
    if result.modified_count == 0:
        return None
    return get_tournament(db, tournament_id)


def subscribe_student_to_tournament(
    db: deps.Database, student: schemas.PyObjectId, tournament_id: schemas.PyObjectId
) -> bool:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    if not (tournament := get_tournament(db, tournament_id)):
        return False
    if student in tournament.registered_students:
        return False
    result = tournament_collection.update_one(
        {"_id": tournament_id}, {"$push": {"registered_students": student}}
    )
    return result.modified_count != 0


def add_educator_to_tournament(
    db: deps.Database, educator: schemas.PyObjectId, tournament_id: schemas.PyObjectId
) -> bool:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.update_one(
        {"_id": tournament_id}, {"$push": {"educators": educator}}
    )
    return result.modified_count != 0


def delete_tournament(db: deps.Database, tournament_id: schemas.PyObjectId) -> bool:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.delete_one({"_id": tournament_id})
    return result.deleted_count != 0


def create_battle(
    db: deps.Database,
    tournament_id: schemas.PyObjectId,
    battle_create: schemas.BattleCreate,
) -> Optional[schemas.Tournament]:
    battle = schemas.Battle(**battle_create.model_dump())
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.update_one(
        {"_id": tournament_id},
        {"$push": {"battles": utils.embed_document_id(battle)}},
    )
    if result.modified_count == 0:
        return None
    return get_tournament(db, tournament_id)


def create_team(
    db: deps.Database,
    tournament_id: schemas.PyObjectId,
    battle_id: schemas.PyObjectId,
    team_create: schemas.TeamCreate,
    current_user: schemas.User,
) -> Optional[schemas.Tournament]:
    team = schemas.Team(**team_create.model_dump())
    team.members.append(current_user.id)
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.update_one(
        {"_id": tournament_id, "battles._id": battle_id},
        {"$push": {"battles.$.teams": utils.embed_document_id(team)}},
    )
    if result.modified_count == 0:
        return None
    return get_tournament(db, tournament_id)


def add_team_member(
    db: deps.Database,
    tournament_id: schemas.PyObjectId,
    team_id: schemas.PyObjectId,
    battle_id: schemas.PyObjectId,
    member_id: schemas.PyObjectId,
) -> Optional[schemas.Tournament]:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.update_one(
        {"_id": tournament_id, "battles.teams._id": team_id},
        {"$addToSet": {"battles.$[b].teams.$[t].members": member_id}},
        array_filters=[{"b._id": battle_id}, {"t._id": team_id}],
    )
    if result.modified_count == 0:
        return None
    return get_tournament(db, tournament_id)
