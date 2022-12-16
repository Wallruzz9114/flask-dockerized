import json

from flask import Flask


def test_ping(test_app: Flask):
    # Givem
    client = test_app.test_client()

    # When
    response = client.get("/ping")
    data = json.loads(response.data.decode())

    # Then
    assert response.status_code == 200
    assert "pong" in data["message"]
    assert "success" in data["status"]
