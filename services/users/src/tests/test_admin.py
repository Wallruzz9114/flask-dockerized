import os

from src import create_app, db


def test_admin_view_dev():
    os.environ["FLASK_ENV"] = "development"
    assert os.getenv("FLASK_ENV") == "development"

    app = create_app()
    app.config.from_object("src.config.TestingConfig")

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        client = app.test_client()
        response = client.get("/admin/user/")
        assert response.status_code == 200

    assert os.getenv("FLASK_ENV") == "development"


def test_admin_view_prod():
    os.environ["FLASK_ENV"] = "production"
    assert os.getenv("FLASK_ENV") == "production"

    app = create_app()
    app.config.from_object("src.config.TestingConfig")

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        client = app.test_client()
        response = client.get("/admin/user/")
        assert response.status_code == 404

    assert os.getenv("FLASK_ENV") == "production"
