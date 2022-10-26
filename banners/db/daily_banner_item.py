from json import JSONEncoder

from application import db


class DailyBannerItemEncoder(JSONEncoder):
    def default(self, obj):
        return {"banner_id": obj.banner_id, "date": obj.date}


class DailyBannerItem(db.Model):
    record_id = db.Column(db.Integer, primary_key=True)
    banner_id = db.Column(db.String(100), unique=True)
    date = db.Column(db.BigInteger)
