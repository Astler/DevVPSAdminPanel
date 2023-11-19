from enum import Enum
from json import JSONEncoder

from application import app_sqlite_db


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
        return {"admin_id": obj.admin_id, "action_info": obj.action_info, "date": obj.date,
                "action": obj.admin_action}


class AdminActionItem(app_sqlite_db.Model):
    record_id = app_sqlite_db.Column(app_sqlite_db.Integer, primary_key=True)
    admin_id = app_sqlite_db.Column(app_sqlite_db.String(200))
    action_info = app_sqlite_db.Column(app_sqlite_db.String(200))
    action = app_sqlite_db.Column(app_sqlite_db.Integer)
    date = app_sqlite_db.Column(app_sqlite_db.BigInteger)
