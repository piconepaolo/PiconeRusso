from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.Team,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    team: schemas.TeamCreate,
    db: Annotated[deps.Database, Depends(deps.get_db)],
    current_user: schemas.User = Depends(deps.get_current_user),
):
    created_team = crud.create_team(db, team, current_user)
    if created_team is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while creating team",
        )
    # Add the creator of the team as a member of the team
    if not crud.add_team_members(db, [current_user.id], created_team.id, current_user):
        if not crud.delete_team(db, created_team):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while deleting team",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while adding team members",
        )
    new_team = crud.get_team(db, created_team.id)
    return new_team


@router.post(
    "/set_repository", response_model=schemas.Team, status_code=status.HTTP_200_OK
)
def set_repository_link(
    team_id: schemas.PyObjectId,
    repository_link: schemas.url,
    db: Annotated[deps.Database, Depends(deps.get_db)],
    current_user: schemas.User = Depends(deps.get_current_user),
):
    if not (team := crud.get_team(db, team_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    if not (
        new_team := crud.set_team_repository(db, team, repository_link, current_user)
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while setting repository link",
        )
    return new_team


@router.put("/add_members", response_model=schemas.Team, status_code=status.HTTP_200_OK)
def add_team_members(
    team_id: schemas.PyObjectId,
    members_id: list[schemas.PyObjectId],
    db: Annotated[deps.Database, Depends(deps.get_db)],
    current_user: schemas.User = Depends(deps.get_current_user),
) -> schemas.Team:
    if not (new_team := crud.add_team_members(db, members_id, team_id, current_user)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while adding members",
        )
    if not (new_team := crud.get_team(db, team_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error while getting team",
        )
    return new_team
