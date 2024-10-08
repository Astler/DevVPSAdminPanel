from flask_login import UserMixin

from core.dependencies import app_sqlite_db


class User(UserMixin, app_sqlite_db.Model):
    id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    email = app_sqlite_db.Column(app_sqlite_db.String(100), unique=True)
    password = app_sqlite_db.Column(app_sqlite_db.String(100))
    name = app_sqlite_db.Column(app_sqlite_db.String(1000))
