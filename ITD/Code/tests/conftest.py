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
def team_create() -> schemas.TeamCreate:
    return schemas.TeamCreate(
        name="Team",
    )


@fixture(scope="session")
def add_team_member() -> list[schemas.PyObjectId]:
    return [schemas.PyObjectId()]


@fixture(scope="session")
def db() -> deps.Database:
    return deps.get_db()


@fixture(scope="session", autouse=True)
def test_client(db: deps.Database):
    import app.main

    with TestClient(app.main.app) as client:
        client.headers["Content-Type"] = "application/json"
        yield client

    db.drop_collection("users")
    db.drop_collection("authentication_tokens")


@fixture(scope="class")
def authorized_client(db: deps.Database, student_user_create: schemas.UserCreate):
    import app.main

    with TestClient(app.main.app) as client:
        token = create_and_login_user(student_user_create, client)
        client.headers["Content-Type"] = "application/json"
        client.headers["Authorization"] = f"Bearer {token}"
        yield client

    db.drop_collection("users")
    db.drop_collection("authentication_tokens")


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
def current_user_id(
    db: deps.Database, student_user_create: schemas.UserCreate
) -> schemas.PyObjectId:
    user = crud.get_user_by_email(db, student_user_create.email)
    assert user is not None
    return user.id
