import json
from datetime import datetime

import pytest
import src.api.users
from flask import Flask


def test_add_user(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    def mock_get_user_by_email(email: str):
        return None

    def mock_create_user(username: str, email: str):
        return True

    monkeypatch.setattr(src.api.users, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(src.api.users, "create_user", mock_create_user)

    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"username": "jpinto", "email": "jpinto@flask.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert json.loads(response.data.decode())
    assert "jpinto@flask.com was added!" in data["message"]


def test_add_user_invalid_json(test_app: Flask):
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_invalid_json_keys(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"email": "jpinto@flask.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_duplicate_email(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    def mock_get_user_by_email(email: str):
        return True

    def mock_create_user(username: str, email: str):
        return True

    monkeypatch.setattr(src.api.users, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(src.api.users, "create_user", mock_create_user)

    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"username": "jpinto", "email": "jpinto@flask.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Sorry. That email already exists." in data["message"]


def test_single_user(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    def mock_get_user_by_id(user_id: int):
        return {
            "id": 1,
            "username": "jeffrey",
            "email": "jeffrey@testdriven.io",
            "created_date": datetime.now(),
        }

    monkeypatch.setattr(src.api.users, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    response = client.get("/users/1")
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert "jeffrey" in data["username"]
    assert "jeffrey@testdriven.io" in data["email"]


def test_single_user_incorrect_id(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    def mock_get_user_by_id(user_id: int):
        return None

    monkeypatch.setattr(src.api.users, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    response = client.get("/users/999")
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_all_users(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    def mock_get_all_users():
        return [
            {
                "id": 1,
                "username": "jpinto",
                "email": "jpinto@flask.com",
                "created_date": datetime.now(),
            },
            {
                "id": 1,
                "username": "hpinto",
                "email": "hpinto@flask.com",
                "created_date": datetime.now(),
            },
        ]

    monkeypatch.setattr(src.api.users, "get_all_users", mock_get_all_users)
    client = test_app.test_client()
    response = client.get("/users")
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert len(data) == 2
    assert "jpinto" in data[0]["username"]
    assert "jpinto@flask.com" in data[0]["email"]
    assert "hpinto" in data[1]["username"]
    assert "hpinto@flask.com" in data[1]["email"]


def test_remove_user(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    def mock_get_user_by_id(user_id: int):
        d = AttrDict()
        d.update(
            {
                "id": 1,
                "username": "user-to-be-removed",
                "email": "remove-me@testdriven.io",
            }
        )
        return d

    def mock_delete_user(user):
        return True

    monkeypatch.setattr(src.api.users, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(src.api.users, "delete_user", mock_delete_user)
    client = test_app.test_client()
    response_two = client.delete("/users/1")
    data = json.loads(response_two.data.decode())

    assert response_two.status_code == 200
    assert "remove-me@testdriven.io was removed!" in data["message"]


def test_remove_user_incorrect_id(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    def mock_get_user_by_id(user_id: int):
        return None

    monkeypatch.setattr(src.api.users, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    resp = client.delete("/users/999")
    data = json.loads(resp.data.decode())

    assert resp.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_update_user(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    def mock_get_user_by_id(user_id: int):
        d = AttrDict()
        d.update({"id": 1, "username": "me", "email": "me@testdriven.io"})
        return d

    def mock_update_user(user, username, email):
        return True

    def mock_get_user_by_email(email):
        return None

    monkeypatch.setattr(src.api.users, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(src.api.users, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(src.api.users, "update_user", mock_update_user)
    client = test_app.test_client()
    response_one = client.put(
        "/users/1",
        data=json.dumps({"username": "me", "email": "me@testdriven.io"}),
        content_type="application/json",
    )
    data = json.loads(response_one.data.decode())

    assert response_one.status_code == 200
    assert "1 was updated!" in data["message"]

    resp_two = client.get("/users/1")
    data = json.loads(resp_two.data.decode())

    assert resp_two.status_code == 200
    assert "me" in data["username"]
    assert "me@testdriven.io" in data["email"]


@pytest.mark.parametrize(
    "user_id, payload, status_code, message",
    [
        [1, {}, 400, "Input payload validation failed"],
        [1, {"email": "me@testdriven.io"}, 400, "Input payload validation failed"],
        [
            999,
            {"username": "me", "email": "me@testdriven.io"},
            404,
            "User 999 does not exist",
        ],
    ],
)
def test_update_user_invalid(
    test_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
    user_id: int,
    payload,
    status_code: int,
    message: str,
):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(src.api.users, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    response = client.put(
        f"/users/{user_id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == status_code
    assert message in data["message"]


def test_update_user_duplicate_email(test_app: Flask, monkeypatch: pytest.MonkeyPatch):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    def mock_get_user_by_id(user_id: int):
        d = AttrDict()
        d.update({"id": 1, "username": "me", "email": "me@testdriven.io"})
        return d

    def mock_update_user(user, username, email):
        return True

    def mock_get_user_by_email(email):
        return True

    monkeypatch.setattr(src.api.users, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(src.api.users, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(src.api.users, "update_user", mock_update_user)
    client = test_app.test_client()
    response = client.put(
        "/users/1",
        data=json.dumps({"username": "me", "email": "me@testdriven.io"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Sorry. That email already exists." in data["message"]
