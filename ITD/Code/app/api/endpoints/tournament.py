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
