from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from app import schemas
import pytest


@pytest.mark.usefixtures("authorized_client", "current_user_id")
def test_create_team(
    team_create: schemas.TeamCreate,
    authorized_client: TestClient,
    current_user_id: schemas.User,
):
    print(jsonable_encoder(team_create))
    response = authorized_client.post("/api/teams/", json=jsonable_encoder(team_create))
    assert response.status_code == 201
    assert response.json()["name"] == team_create.name
    assert current_user_id in schemas.Team(**response.json()).members
