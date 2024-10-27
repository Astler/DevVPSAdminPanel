import json
from datetime import datetime
from json import JSONEncoder

from core.dependencies import app_sqlite_db
from banners.data_old.banner_image_generator import get_image_data_url


class ProjectItemEncoder(JSONEncoder):
    def default(self, obj):
        return {
            "api_key": obj.api_key,
            "name": obj.name,
            "date": obj.date
        }


class ProjectItem(app_sqlite_db.Model):
    record_id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    name = app_sqlite_db.Column(app_sqlite_db.String(100))
    api_key = app_sqlite_db.Column(app_sqlite_db.String(100), unique=True)
    date = app_sqlite_db.Column(app_sqlite_db.BigInteger)
