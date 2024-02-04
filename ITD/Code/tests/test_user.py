from fastapi.encoders import jsonable_encoder
from starlette.testclient import TestClient

from app import schemas


def test_create_user(test_client: TestClient, educator_user_create: schemas.UserCreate):
    response = test_client.post(
        "/api/users/", json=jsonable_encoder(educator_user_create)
    )
    assert response.status_code == 201
    assert response.json()["email"] == educator_user_create.email
    assert response.json()["first_name"] == educator_user_create.first_name
    assert response.json()["last_name"] == educator_user_create.last_name
    assert response.json()["is_educator"] is True
    assert "password" not in response.json()


def test_create_user_existing(
    test_client: TestClient, educator_user_create: schemas.UserCreate
):
    response = test_client.post(
        "/api/users/", json=jsonable_encoder(educator_user_create)
    )
    assert response.status_code == 400


def test_create_user_student(
    test_client: TestClient, student_user_create: schemas.UserCreate
):
    response = test_client.post(
        "/api/users/", json=jsonable_encoder(student_user_create)
    )
    assert response.status_code == 201
    assert response.json()["email"] == student_user_create.email
    assert response.json()["first_name"] == student_user_create.first_name
    assert response.json()["last_name"] == student_user_create.last_name
    assert response.json()["is_educator"] is False
    assert "password" not in response.json()


def test_user_login(test_client: TestClient, educator_user_create: schemas.UserCreate):
    response = test_client.post(
        "/api/auth/token",
        data=f"username={educator_user_create.email}&password={educator_user_create.password}",  # type: ignore
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"

    access_token = response.json()["access_token"]
    response = test_client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == educator_user_create.email
    assert response.json()["first_name"] == educator_user_create.first_name
    assert response.json()["last_name"] == educator_user_create.last_name
    assert response.json()["is_educator"] is True
