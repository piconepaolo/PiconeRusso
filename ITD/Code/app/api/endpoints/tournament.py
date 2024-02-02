from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app import crud, schemas
from app.api import deps

router = APIRouter()


# TODO: Add backgroup tasks to send notifications to all students subscribed to the platform
@router.post(
    "/",
    response_model=schemas.Tournament,
    status_code=status.HTTP_201_CREATED,
)
def create_tournament(
    tournament: schemas.TournamentCreate,
    current_user: schemas.User = Depends(deps.get_current_educator),
    db: deps.Database = Depends(deps.get_db),
) -> Optional[schemas.Tournament]:
    tournament_db = crud.create_tournament(db, tournament)
    if not tournament_db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create tournament",
        )
    if not crud.add_educator_to_tournament(db, current_user.id, tournament_db.id):
        crud.delete_tournament(db, tournament_db.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not add educator to tournament",
        )

    return crud.get_tournament(db, tournament_db.id)


@router.get(
    "/{tournament_id}",
    response_model=schemas.Tournament,
    status_code=status.HTTP_200_OK,
)
def get_tournament(
    tournament_id: schemas.PyObjectId, db: deps.Database = Depends(deps.get_db)
) -> schemas.Tournament:
    if not (tournament := crud.get_tournament(db, tournament_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found",
        )
    return tournament


@router.put(
    "/{tournament_id}",
    response_model=schemas.Tournament,
    status_code=status.HTTP_200_OK,
)
def update_tournament(
    tournament_id: schemas.PyObjectId,
    tournament: schemas.TournamentUpdate,
    db: deps.Database = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_educator),
) -> schemas.Tournament:
    if not crud.get_tournament(db, tournament_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found",
        )
    if not (
        tournament_updated := crud.update_tournament(db, tournament, tournament_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update tournament",
        )
    return tournament_updated


@router.post(
    "/{tournament_id}/subscribe",
    response_model=schemas.Tournament,
    status_code=status.HTTP_200_OK,
)
def subscribe_student_to_tournament(
    tournament_id: schemas.PyObjectId,
    db: deps.Database = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_student),
) -> schemas.Tournament:
    if not crud.get_tournament(db, tournament_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found",
        )
    if not crud.subscribe_student_to_tournament(db, current_user.id, tournament_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not subscribe student to tournament",
        )
    if not (tournament := crud.get_tournament(db, tournament_id)):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve tournament",
        )
    return tournament


@router.post(
    "/{tournament_id}/battle",
    response_model=schemas.Tournament,
    status_code=status.HTTP_201_CREATED,
)
def create_battle(
    tournament_id: schemas.PyObjectId,
    battle: schemas.BattleCreate,
    db: deps.Database = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_educator),
) -> schemas.Tournament:
    if not crud.get_tournament(db, tournament_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found",
        )
    if not (updated_tournament := crud.create_battle(db, tournament_id, battle)):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create battle",
        )
    return updated_tournament


@router.post(
    "/{tournament_id}/{battle_id}/create_team",
    response_model=schemas.Tournament,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    tournament_id: schemas.PyObjectId,
    battle_id: schemas.PyObjectId,
    team: schemas.TeamCreate,
    db: deps.Database = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user),
) -> schemas.Tournament:
    if not crud.get_tournament(db, tournament_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found",
        )
    if not (
        updated_tournament := crud.create_team(
            db, tournament_id, battle_id, team, current_user
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create team",
        )
    return updated_tournament


@router.put(
    "/{tournament_id}/{battle_id}/{team_id}/add_member",
    response_model=Optional[schemas.Tournament],
    status_code=status.HTTP_200_OK,
)
def add_team_member(
    tournament_id: schemas.PyObjectId,
    team_id: schemas.PyObjectId,
    battle_id: schemas.PyObjectId,
    member_id: schemas.PyObjectId,
    db: deps.Database = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user),
) -> Optional[schemas.Tournament]:
    if not crud.get_tournament(db, tournament_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found",
        )
    # if not (
    #     updated_tournament := crud.add_team_member(
    #         db, tournament_id, battle_id, team_id, member_id
    #     )
    # ):
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Could not add team member",
    #     )
    return crud.add_team_member(db, tournament_id, team_id, battle_id, member_id)
