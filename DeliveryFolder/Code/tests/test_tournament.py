from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from app import schemas


def test_create_tournament(
    tournament_create: schemas.TournamentCreate,
    authorized_educator: TestClient,
    current_educator: schemas.User,
):
    response = authorized_educator.post(
        "/api/tournaments/", json=jsonable_encoder(tournament_create)
    )
    tournament = schemas.Tournament(**response.json())
    assert response.status_code == 201
    assert response.json()["name"] == tournament_create.name
    assert current_educator.id in tournament.educators
