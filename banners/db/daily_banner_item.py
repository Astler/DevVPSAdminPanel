from application import db


class DailyBannerItem(db.Model):
    record_id = db.Column(db.Integer, primary_key=True)
    banner_id = db.Column(db.String(100), unique=True)
    date = db.Column(db.BigInteger)