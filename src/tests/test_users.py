import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from src.api.models import User


def test_add_user(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"username": "jose", "email": "jpinto@flask.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 201
    assert "jpinto@flask.com" in data["message"]


def test_add_user_invalid_json(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.post(
        "/users", data=json.dumps({}), content_type="application/json"
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_invalid_json_keys(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"email": "jpinto@flask.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_duplicate_email(test_app: Flask, test_database):
    client = test_app.test_client()

    client.post(
        "/users",
        data=json.dumps({"username": "jpinto", "email": "jpinto@flask.com"}),
        content_type="application/json",
    )

    response = client.post(
        "/users",
        data=json.dumps({"username": "jpinto", "email": "jpinto@flask.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Sorry. That email already exists." in data["message"]


def test_single_user(test_app: Flask, test_database, create_user):
    user = create_user("jpinto", "jpinto@flask.com")

    client = test_app.test_client()
    response = client.get(f"/users/{user.id}")
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert "jpinto" in data["username"]
    assert "jpinto@flask.com" in data["email"]


def test_single_user_incorrect_id(test_app: Flask, test_database):
    client = test_app.test_client()
    response = client.get("/users/999")
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_all_users(test_app: Flask, test_database: SQLAlchemy, create_user):
    test_database.session.query(User).delete()

    create_user("jpinto", "jpinto@flask.com")
    create_user("hpinto", "hpinto@flask.com")

    client = test_app.test_client()
    response = client.get("/users")
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert len(data) == 2
    assert "jpinto" in data[0]["username"]
    assert "jpinto@flask.com" in data[0]["email"]
    assert "hpinto" in data[1]["username"]
    assert "hpinto@flask.com" in data[1]["email"]
