from pytest import fixture
from starlette.config import environ
from starlette.testclient import TestClient
from app import schemas
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
def db() -> deps.Database:
    return deps.get_db()


@fixture(scope="session", autouse=True)
def test_client(db: deps.Database):
    import app.main

    with TestClient(app.main.app) as client:
        yield client

    db.drop_collection("users")
    db.drop_collection("authentication_tokens")
