from json import JSONEncoder

from application import app_sqlite_db


class DailyBannerItemEncoder(JSONEncoder):
    def default(self, obj):
        return {"banner_id": obj.banner_id, "date": obj.date}


class DailyBannerItem(app_sqlite_db.Model):
    record_id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    banner_id = app_sqlite_db.Column(app_sqlite_db.String(100), unique=True)
    date = app_sqlite_db.Column(app_sqlite_db.BigInteger)
