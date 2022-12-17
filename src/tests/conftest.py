import pytest

from src import create_app, db
from src.api.models import User

# Fixtures are reusable objects for tests. They have a scope associated with them,
# which indicates how often the fixture is invoked:

#    1. function - once per test function (default)
#    2. class - once per test class
#    3. module - once per test module
#    4. session - once per test session


@pytest.fixture(scope="module")
def test_app():
    app = create_app()
    app.config.from_object("src.config.TestingConfig")
    with app.app_context():
        yield app  # Testing happens here


@pytest.fixture(scope="module")
def test_database():
    db.create_all()
    yield db  # Testing happens here
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope="function")
def create_user():
    def _add_user(username: str, email: str):
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    return _add_user
