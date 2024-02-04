from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from app import schemas


def test_create_team(
    battle_db: schemas.Tournament,
    team_create: schemas.TeamCreate,
    authorized_student: TestClient,
    current_student: schemas.User,
):
    battle_id = battle_db.battles[0].id
    endpoint = f"/api/tournaments/{battle_db.id}/{battle_id}/create_team"
    response = authorized_student.post(endpoint, json=jsonable_encoder(team_create))
    tournament = schemas.Tournament(**response.json())
    assert response.status_code == 201
    assert tournament.battles[0].teams[0].name == team_create.name
    assert current_student.id in tournament.battles[0].teams[0].members


def test_add_team_member(
    authorized_student: TestClient,
    team_db: schemas.Tournament,
    team_members: list[ObjectId],
):
    battle_id = team_db.battles[0].id
    team_id = team_db.battles[0].teams[0].id
    endpoint = f"/api/tournaments/{team_db.id}/{battle_id}/{team_id}/add_member"
    response = authorized_student.put(
        endpoint, params={"member_id": str(team_members[0])}
    )
    print(response.json())
    team_db = schemas.Tournament(**response.json())
    assert response.status_code == 200
    assert team_members[0] in team_db.battles[0].teams[0].members
