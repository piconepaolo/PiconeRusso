from typing import Optional

from fastapi.encoders import jsonable_encoder

from app import schemas, utils
from app.api import deps
from app.core.config.settings import DatabaseSettings
from app.github.GitHub import GitHubClient


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


def get_battle(
    db: deps.Database, tournament_id: schemas.PyObjectId, battle_id: schemas.PyObjectId
) -> Optional[schemas.Battle]:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.find_one(
        {"_id": tournament_id, "battles._id": battle_id}, {"battles.$": 1}
    )
    if not result:
        return None
    return schemas.Battle(**result["battles"][0])


def create_battle(
    db: deps.Database,
    tournament_id: schemas.PyObjectId,
    battle_create: schemas.BattleCreate,
) -> Optional[schemas.Tournament]:
    owner = GitHubClient.owner
    github_repository = f"https://www.github.com/{owner}/{battle_create.name}"
    battle = schemas.Battle(
        **battle_create.model_dump(), github_repository=github_repository
    )
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
    if not (
        result_battle := tournament_collection.find_one(
            {"_id": tournament_id, "battles._id": battle_id},
            {"battles.$": 1},
        )
    ):
        return None
    battle = schemas.Battle(**result_battle["battles"][0])
    print(battle.maximum_team_size)
    team_members = get_team_members(db, tournament_id, battle_id, team_id)
    if len(team_members) + 1 > battle.maximum_team_size:
        return None
    result = tournament_collection.update_one(
        {"_id": tournament_id, "battles.teams._id": team_id},
        {"$addToSet": {"battles.$[b].teams.$[t].members": member_id}},
        array_filters=[{"b._id": battle_id}, {"t._id": team_id}],
    )
    if result.modified_count == 0:
        return None
    return get_tournament(db, tournament_id)


def update_team_score(
    db: deps.Database,
    submission: schemas.Submission,
    score: int,
) -> Optional[int]:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.update_one(
        {
            "_id": submission.tournament_id,
            "battles._id": submission.battle_id,
            "battles.teams._id": submission.team_id,
        },
        {"$set": {"battles.$[b].teams.$[t].score": score}},
        array_filters=[{"b._id": submission.battle_id}, {"t._id": submission.team_id}],
    )
    if result.modified_count == 0:
        return None
    return score


def get_team_members(
    db: deps.Database,
    tournament_id: schemas.PyObjectId,
    battle_id: schemas.PyObjectId,
    team_id: schemas.PyObjectId,
) -> list[schemas.PyObjectId]:
    tournament_collection = db[DatabaseSettings.TOURNAMENT_COLLECTION]
    result = tournament_collection.find_one(
        {
            "_id": tournament_id,
            "battles._id": battle_id,
            "battles.teams._id": team_id,
        },
        {"battles.$": 1},
    )
    if not result:
        return []
    team = schemas.Team(**result["battles"][0]["teams"][0])
    return team.members if team.members else []
