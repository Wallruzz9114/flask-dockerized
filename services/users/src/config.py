import os


class BaseConfig:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "asfbHOjkbLBSksbfpsba!"
    BCRYPT_LOG_ROUNDS = 13


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    BCRYPT_LOG_ROUNDS = 4


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")
    BCRYPT_LOG_ROUNDS = 4


class ProductionConfig(BaseConfig):
    url = os.environ.get("DATABASE_URL")

    if url is not None and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = url
    SECRET_KEY = os.getenv("SECRET_KEY", "asfbHOjkbLBSksbfpsba!")
