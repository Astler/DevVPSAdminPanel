from json import JSONEncoder

from application import app_sqlite_db


class DeletedBannerModelEncoder(JSONEncoder):
    def default(self, obj):
        return {"id": obj.id, "date": obj.date, "content": obj.content}


class DeletedBannerModel(app_sqlite_db.Model):
    record_id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    id = app_sqlite_db.Column(app_sqlite_db.String(100))
    admin_id = app_sqlite_db.Column(app_sqlite_db.String(100))
    layers = app_sqlite_db.Column(app_sqlite_db.String())
    content = app_sqlite_db.Column(app_sqlite_db.String())
    date = app_sqlite_db.Column(app_sqlite_db.BigInteger)
