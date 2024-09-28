from json import JSONEncoder

from application import app_sqlite_db


class DeletedBannerItemEncoder(JSONEncoder):
    def default(self, obj):
        return {"id": obj.id, "date": obj.date, "content": obj.content}


class DeletedBannerItem(app_sqlite_db.Model):
    record_id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    id = app_sqlite_db.Column(app_sqlite_db.String(100))
    content = app_sqlite_db.Column(app_sqlite_db.String())
    date = app_sqlite_db.Column(app_sqlite_db.BigInteger)
