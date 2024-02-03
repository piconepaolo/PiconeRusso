from datetime import datetime, timedelta

from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pytest import fixture
from starlette.config import environ
from starlette.testclient import TestClient

from app import crud, schemas
from app.api import deps

environ["TESTING"] = "True"


@fixture(scope="session")
def educator_user_create() -> schemas.UserCreate:
    return schemas.UserCreate(
        email="educator@polimi.it",
        first_name="Educator",
        last_name="Educator",
        password="educator",
    )


@fixture(scope="session")
def student_user_create() -> schemas.UserCreate:
    return schemas.UserCreate(
        email="student@mail.polimi.it",
        first_name="Student",
        last_name="Student",
        password="student",
    )


@fixture(scope="session")
def tournament_create() -> schemas.TournamentCreate:
    return schemas.TournamentCreate(
        name="Tournament",
        description="Tournament description",
        start_date=datetime.utcnow(),
        registration_deadline=datetime.utcnow() + timedelta(days=20),
    )


@fixture(scope="session")
def battle_create() -> schemas.BattleCreate:
    return schemas.BattleCreate(
        name="Battle",
        maximum_team_size=5,
        minimum_team_size=3,
        registration_deadline=datetime.utcnow() + timedelta(days=10),
        submission_deadline=datetime.utcnow() + timedelta(days=30),
    )


@fixture(scope="session")
def tournament_db(
    db: deps.Database, tournament_create: schemas.TournamentCreate
) -> schemas.Tournament:
    tournament = crud.create_tournament(db, tournament_create)
    return schemas.Tournament(**jsonable_encoder(tournament))


@fixture(scope="session")
def battle_db(
    db: deps.Database,
    tournament_db: schemas.Tournament,
    battle_create: schemas.BattleCreate,
) -> schemas.Tournament:
    tournament = crud.create_battle(db, tournament_db.id, battle_create)
    return schemas.Tournament(**jsonable_encoder(tournament))


@fixture(scope="class")
def team_db(
    db: deps.Database,
    battle_db: schemas.Tournament,
    team_create: schemas.TeamCreate,
    current_student: schemas.User,
) -> schemas.Tournament:
    tournament = crud.create_team(
        db, battle_db.id, battle_db.battles[0].id, team_create, current_student
    )
    return schemas.Tournament(**jsonable_encoder(tournament))


@fixture(scope="session")
def team_create() -> schemas.TeamCreate:
    return schemas.TeamCreate(
        name="Team",
    )


@fixture(scope="session")
def team_members() -> list[ObjectId]:
    return [ObjectId()]


@fixture(scope="session")
def db() -> deps.Database:
    return deps.get_db()


@fixture(scope="session", autouse=True)
def test_client(db: deps.Database):
    import app.main

    with TestClient(app.main.app) as client:
        client.headers["Content-Type"] = "application/json"
        yield client

    drop_collections(db)


@fixture(scope="class")
def authorized_student(db: deps.Database, student_user_create: schemas.UserCreate):
    import app.main

    with TestClient(app.main.app) as client:
        token = create_and_login_user(student_user_create, client)
        client.headers["Content-Type"] = "application/json"
        client.headers["Authorization"] = f"Bearer {token}"
        yield client

    drop_collections(db)


@fixture(scope="class")
def authorized_educator(db: deps.Database, educator_user_create: schemas.UserCreate):
    import app.main

    with TestClient(app.main.app) as client:
        token = create_and_login_user(educator_user_create, client)
        client.headers["Content-Type"] = "application/json"
        client.headers["Authorization"] = f"Bearer {token}"
        yield client

    drop_collections(db)


def drop_collections(db: deps.Database):
    db.drop_collection("users")
    db.drop_collection("authentication_tokens")
    db.drop_collection("teams")


def create_user(student_user_create: schemas.UserCreate, client: TestClient):
    user = client.post("/api/users/", json=jsonable_encoder(student_user_create))
    assert user.status_code == 201


def login_user(student_user_create: schemas.UserCreate, client: TestClient) -> str:
    """
    Returns the access token
    """
    client.headers["Content-Type"] = "application/x-www-form-urlencoded"
    token = client.post(
        "/api/auth/token",
        data={
            "username": student_user_create.email,
            "password": student_user_create.password,
        },
    )
    assert token.status_code == 200
    return token.json()["access_token"]


def create_and_login_user(
    student_user_create: schemas.UserCreate, client: TestClient
) -> str:
    """
    Generates a user and returns the access token
    """
    create_user(student_user_create, client)
    return login_user(student_user_create, client)


@fixture(scope="class")
def current_educator(
    db: deps.Database, educator_user_create: schemas.UserCreate
) -> schemas.User:
    user = crud.get_user_by_email(db, educator_user_create.email)
    assert user is not None
    return user


@fixture(scope="class")
def current_student(
    db: deps.Database, student_user_create: schemas.UserCreate
) -> schemas.User:
    user = crud.get_user_by_email(db, student_user_create.email)
    assert user is not None
    return user
