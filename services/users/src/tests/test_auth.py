import json

import pytest
from flask import Flask, current_app

from src.api.users.models import User


def test_passwords_are_random(test_app, test_database, create_user):
    user_one = create_user("justatest", "test@test.com", "greaterthaneight")
    user_two = create_user("justatest2", "test@test2.com", "greaterthaneight")
    assert user_one.password != user_two.password


def test_encode_token(test_app, test_database, create_user):
    user = create_user("justatest", "test@test.com", "test")
    token = user.encode_token(user.id, "access")
    assert isinstance(token, str)


def test_decode_token(test_app, test_database, create_user):
    user = create_user("justatest", "test@test.com", "test")
    token = user.encode_token(user.id, "access")
    assert isinstance(token, str)
    assert User.decode_token(token) == user.id


def test_user_registration(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.post(
        "/auth/register",
        data=json.dumps(
            {
                "username": "lol",
                "email": "lol@test.com",
                "password": "123456",
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 201
    assert response.content_type == "application/json"
    assert "lol" in data["username"]
    assert "lol@test.com" in data["email"]
    assert "password" not in data


def test_user_registration_duplicate_email(test_app: Flask, test_database, create_user):
    create_user("test", "test@test.com", "test")
    client = test_app.test_client()
    response = client.post(
        "/auth/register",
        data=json.dumps(
            {"username": "jpinto", "email": "test@test.com", "password": "test"}
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert "Sorry. That email already exists." in data["message"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"email": "me@flask.com", "password": "greaterthanten"},
        {"username": "jpinto", "password": "greaterthanten"},
        {"email": "me@flask.com", "username": "jpinto"},
    ],
)
def test_user_registration_invalid_json(test_app, test_database, payload):
    client = test_app.test_client()
    response = client.post(
        f"/auth/register",
        data=json.dumps(payload),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert "Input payload validation failed" in data["message"]


def test_login_user_success(test_app: Flask, test_database, create_user):
    create_user("jpinto", "jpinto@flask.com", "testpassword")
    client = test_app.test_client()
    response = client.post(
        "/auth/login",
        data=json.dumps({"email": "jpinto@flask.com", "password": "testpassword"}),
        content_type="application/json",
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert data["access_token"]
    assert data["refresh_token"]


def test_login_user_failure(test_app: Flask, test_database):
    client = test_app.test_client()
    resp = client.post(
        "/auth/login",
        data=json.dumps({"email": "testnotreal@test.com", "password": "test"}),
        content_type="application/json",
    )

    data = json.loads(resp.data.decode())

    assert resp.status_code == 404
    assert resp.content_type == "application/json"
    assert "User does not exist." in data["message"]


def test_valid_tokens(test_app: Flask, test_database, create_user):
    create_user("test4", "test4@test.com", "test")
    client = test_app.test_client()
    # user login
    login_response = client.post(
        "/auth/login",
        data=json.dumps({"email": "test4@test.com", "password": "test"}),
        content_type="application/json",
    )
    # valid refresh
    refresh_token = json.loads(login_response.data.decode())["refresh_token"]

    response = client.post(
        "/auth/refresh",
        data=json.dumps({"refresh_token": refresh_token}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert data["access_token"]
    assert data["refresh_token"]
    assert response.content_type == "application/json"


def test_expired_tokens(test_app: Flask, test_database, create_user):
    create_user("test5", "test5@test.com", "test")
    current_app.config["REFRESH_TOKEN_EXPIRATION"] = -1
    client = test_app.test_client()
    # user login
    login_response = client.post(
        "/auth/login",
        data=json.dumps({"email": "test5@test.com", "password": "test"}),
        content_type="application/json",
    )
    # invalid token refresh
    refresh_token = json.loads(login_response.data.decode())["refresh_token"]
    response = client.post(
        "/auth/refresh",
        data=json.dumps({"refresh_token": refresh_token}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 401
    assert response.content_type == "application/json"
    assert "Signature expired. Please log in again." in data["message"]


def test_invalid_tokens(test_app, test_database):
    client = test_app.test_client()
    response = client.post(
        "/auth/refresh",
        data=json.dumps({"refresh_token": "Invalid"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 401
    assert response.content_type == "application/json"
    assert "Invalid token. Please log in again." in data["message"]


def test_user_status(test_app: Flask, test_database, create_user):
    create_user("test6", "test6@test.com", "test")
    client = test_app.test_client()
    login_response = client.post(
        "/auth/login",
        data=json.dumps({"email": "test6@test.com", "password": "test"}),
        content_type="application/json",
    )
    token = json.loads(login_response.data.decode())["access_token"]
    response = client.get(
        "/auth/status",
        headers={"Authorization": f"Bearer {token}"},
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert "test6" in data["username"]
    assert "test6@test.com" in data["email"]
    assert "password" not in data


def test_invalid_status(test_app: Flask, test_database):
    client = test_app.test_client()
    resp = client.get(
        "/auth/status",
        headers={"Authorization": "Bearer invalid"},
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())

    assert resp.status_code == 401
    assert resp.content_type == "application/json"
    assert "Invalid token. Please log in again." in data["message"]
