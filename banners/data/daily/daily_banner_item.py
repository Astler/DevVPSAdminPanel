import json
from datetime import datetime
from json import JSONEncoder

from application import app_sqlite_db
from banners.data_old.banner_image_generator import get_image_data_url


class DailyBannerItemEncoder(JSONEncoder):
    def default(self, obj):
        return {"banner_id": obj.banner_id, "date": obj.date, "layers": obj.layers}


class DailyBannerItem(app_sqlite_db.Model):
    record_id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    banner_id = app_sqlite_db.Column(app_sqlite_db.String(100), unique=True)
    date = app_sqlite_db.Column(app_sqlite_db.BigInteger)
    layers = app_sqlite_db.Column(app_sqlite_db.String())

    def to_ui_info(self):
        return {
            'banner_id': self.banner_id,
            'date': datetime.fromtimestamp(self.date / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': get_image_data_url(json.loads(self.layers)) if self.layers else None
        }
