import json
from datetime import datetime
from enum import Enum
from json import JSONEncoder

from banners.data.firebase.banner_firebase_item import BannerFirebaseItem
from banners.data_old.banner_image_generator import get_image_data_url
from core.dependencies import app_sqlite_db


class AdminAction(Enum):
    AddedDaily = 1
    Deleted = 2
    Renamed = 3

    def __int__(self):
        return self.value

    @classmethod
    def get_action_by_value(cls, value):
        for action in cls:
            if action.value == value:
                return action
        return None


class AdminActionItemEncoder(JSONEncoder):
    def default(self, obj):
        return {"admin": obj.admin, "action_data": obj.action_data, "date": obj.date,
                "action": obj.admin_action}


class AdminActionModel(app_sqlite_db.Model):
    record_id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    admin = app_sqlite_db.Column(app_sqlite_db.String(200))
    action_data = app_sqlite_db.Column(app_sqlite_db.String(200))
    action = app_sqlite_db.Column(app_sqlite_db.Integer)
    date = app_sqlite_db.Column(app_sqlite_db.BigInteger)

    @classmethod
    def build(cls, admin_id: str, action: AdminAction, action_info: dict) -> 'AdminActionModel':
        return cls(
            admin=admin_id,
            action_data=json.dumps(action_info),
            action=int(action),
            date=int(datetime.now().timestamp())
        )


    def to_ui_info(self):
        banner = BannerFirebaseItem.from_json(self.action_data)

        return {
            'admin': self.admin,
            'info': self.action_data,
            'translated_action': str(AdminAction.get_action_by_value(self.action).name),
            'date': datetime.fromtimestamp(self.date / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': get_image_data_url(banner.layers) if banner.layers else None
        }