import json
from datetime import datetime
from json import JSONEncoder

from admin.data.project_fields import ProjectsFields
from application import app_sqlite_db
from banners.data_old.banner_image_generator import get_image_data_url


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

    def to_ui_info(self):
        return {
            'banner_id': self.id,
            'date': datetime.fromtimestamp(self.date).strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': get_image_data_url(json.loads(self.layers)) if self.layers else None
        }

    @classmethod
    def build(cls, banner_id: str, admin_id: str, banner_data: dict) -> 'DeletedBannerModel':
        return cls(
            id=banner_id,
            admin_id=admin_id,
            layers=json.dumps(banner_data[ProjectsFields.LAYERS.value], ensure_ascii=False,
                              cls=DeletedBannerModelEncoder),
            content=json.dumps(banner_data),
            date=int(datetime.now().timestamp())
        )
