from datetime import datetime

from sqlalchemy.sql import func
from src import db


class User(db.Model):

    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username: str = db.Column(db.String(128), nullable=False)
    email: str = db.Column(db.String(128), nullable=False)
    active: bool = db.Column(db.Boolean(), default=True, nullable=False)
    created_date: datetime = db.Column(db.DateTime, default=func.now(), nullable=False)

    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
