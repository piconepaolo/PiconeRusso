from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from app import schemas
import pytest
from bson import ObjectId


@pytest.mark.usefixtures("authorized_client", "current_user_id")
def test_create_team(
    team_create: schemas.TeamCreate,
    authorized_client: TestClient,
    current_user_id: schemas.PyObjectId,
) -> schemas.Team:
    response = authorized_client.post("/api/teams/", json=jsonable_encoder(team_create))
    team = schemas.Team(**response.json())
    assert response.status_code == 201
    assert response.json()["name"] == team_create.name
    assert current_user_id in team.members
    return team


@pytest.mark.usefixtures("authorized_client", "current_user_id", "team_members")
def test_add_team_member(
    authorized_client: TestClient,
    current_user_id: schemas.PyObjectId,
    team_members: list[ObjectId],
):
    team = test_create_team(
        schemas.TeamCreate(name="Team2"),
        authorized_client,
        current_user_id,
    )
    params = {"team_id": team.id}
    response = authorized_client.put(
        "/api/teams/add_members",
        params=params,
        json=[str(current_user_id)],
    )
    # assertion to check if the user is already in the team
    assert response.status_code == 400

    response = authorized_client.put(
        "/api/teams/add_members",
        params=params,
        json=list(map(str, team_members)),
    )
    assert response.status_code == 200
    # assertion to check if the team members are the same as the ones added
    assert all(
        [member in schemas.Team(**response.json()).members for member in team_members]
    )
