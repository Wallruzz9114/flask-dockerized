import json

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from src import bcrypt
from src.api.users.crud import get_user_by_id
from src.api.users.models import User


def test_create_user(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps(
            {
                "username": "jose",
                "email": "jpinto@flask.com",
                "password": "mypassword123",
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 201
    assert "jpinto@flask.com" in data["message"]


def test_create_user_invalid_json(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.post(
        "/users", data=json.dumps({}), content_type="application/json"
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_create_user_invalid_json_keys(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"email": "jpinto@flask.com", "password": "mypassword123"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_create_user_duplicate_email(test_app: Flask, test_database):
    client = test_app.test_client()

    client.post(
        "/users",
        data=json.dumps(
            {
                "username": "jpinto",
                "email": "jpinto@flask.com",
                "password": "mypassword123",
            }
        ),
        content_type="application/json",
    )

    response = client.post(
        "/users",
        data=json.dumps(
            {
                "username": "jpinto",
                "email": "jpinto@flask.com",
                "password": "mypassword123",
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Sorry. That email already exists." in data["message"]


def test_single_user(test_app: Flask, test_database, create_user):
    user = create_user("jpinto", "jpinto@flask.com", "mypassword123")

    client = test_app.test_client()
    response = client.get(f"/users/{user.id}")
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert "jpinto" in data["username"]
    assert "jpinto@flask.com" in data["email"]
    assert "password" not in data


def test_single_user_incorrect_id(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.get("/users/999")
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_all_users(test_app: Flask, test_database: SQLAlchemy, create_user):
    test_database.session.query(User).delete()

    create_user("jpinto", "jpinto@flask.com", "mypassword123")
    create_user("hpinto", "hpinto@flask.com", "mypassword123")

    client = test_app.test_client()
    response = client.get("/users")
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert len(data) == 2
    assert "jpinto" in data[0]["username"]
    assert "jpinto@flask.com" in data[0]["email"]
    assert "hpinto" in data[1]["username"]
    assert "hpinto@flask.com" in data[1]["email"]
    assert "password" not in data[0]
    assert "password" not in data[1]


def test_remove_user(test_app: Flask, test_database: SQLAlchemy, create_user):
    test_database.session.query(User).delete()
    user = create_user("user-to-be-removed", "remove-me@flask.com", "mypassword123")
    client = test_app.test_client()
    response_one = client.get("/users")
    data = json.loads(response_one.data.decode())
    assert response_one.status_code == 200
    assert len(data) == 1

    response_two = client.delete(f"/users/{user.id}")
    data = json.loads(response_two.data.decode())
    assert response_two.status_code == 200
    assert "remove-me@flask.com was removed!" in data["message"]

    resp_three = client.get("/users")
    data = json.loads(resp_three.data.decode())
    assert resp_three.status_code == 200
    assert len(data) == 0


def test_remove_user_incorrect_id(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.delete("/users/999")
    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_update_user(test_app: Flask, test_database, create_user):
    user = create_user("user-to-be-updated", "update-me@flask.com", "mypassword123")
    client = test_app.test_client()
    response_one = client.put(
        f"/users/{user.id}",
        data=json.dumps(
            {"username": "me", "email": "me@flask.com", "password": "mypassword123"}
        ),
        content_type="application/json",
    )
    data = json.loads(response_one.data.decode())
    assert response_one.status_code == 200
    assert f"{user.id} was updated!" in data["message"]

    response_two = client.get(f"/users/{user.id}")
    data = json.loads(response_two.data.decode())
    assert response_two.status_code == 200
    assert "me" in data["username"]
    assert "me@flask.com" in data["email"]


@pytest.mark.parametrize(
    "user_id, payload, status_code, message",
    [
        [1, {}, 400, "Input payload validation failed"],
        [1, {"email": "me@flask.com"}, 400, "Input payload validation failed"],
        [
            999,
            {"username": "me", "email": "me@flask.com"},
            404,
            "User 999 does not exist",
        ],
    ],
)
def test_update_user_invalid(
    test_app: Flask,
    test_database,
    user_id: int,
    payload: object,
    status_code: int,
    message: str,
):
    client = test_app.test_client()
    response = client.put(
        f"/users/{user_id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())
    assert response.status_code == status_code
    assert message in data["message"]


def test_update_user_duplicate_email(test_app: Flask, test_database, create_user):
    create_user("hajek", "rob@hajek.org", "mypassword123")
    user = create_user("rob", "rob@notreal.com", "mypassword123")

    client = test_app.test_client()
    response = client.put(
        f"/users/{user.id}",
        data=json.dumps(
            {"username": "rob", "email": "rob@notreal.com", "password": "mypassword123"}
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "Sorry. That email already exists." in data["message"]


def test_update_user_with_password(test_app: Flask, test_database, create_user):
    old_password = "greaterthaneight"
    new_password = "somethingdifferent"

    user = create_user("user-to-be-updated", "update-me@flask.com", old_password)
    assert bcrypt.check_password_hash(user.password, old_password)

    client = test_app.test_client()
    response = client.put(
        f"/users/{user.id}",
        data=json.dumps(
            {"username": "me", "email": "foo@flask.com", "password": new_password}
        ),
        content_type="application/json",
    )
    assert response.status_code == 200

    user = get_user_by_id(user.id)
    assert bcrypt.check_password_hash(user.password, old_password)
    assert not bcrypt.check_password_hash(user.password, new_password)
