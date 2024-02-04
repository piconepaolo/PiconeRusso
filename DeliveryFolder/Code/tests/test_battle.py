from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from app import schemas


def test_create_battle(
    tournament_db: schemas.Tournament,
    battle_create: schemas.BattleCreate,
    authorized_educator: TestClient,
):
    print(battle_create)
    endpoint = f"/api/tournaments/{tournament_db.id}/battle"
    response = authorized_educator.post(endpoint, json=jsonable_encoder(battle_create))
    tournament = schemas.Tournament(**response.json())
    assert response.status_code == 201
    assert tournament.battles[0].name == battle_create.name
