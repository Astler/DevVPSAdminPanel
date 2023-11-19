import json
from datetime import datetime, timezone


class MessedBannersInfo:
    def __init__(self, banners=None, date=0):
        if banners is None:
            banners = []

        self.banners = banners
        self.date = date

    def to_dict(self):
        return {"banners": self.banners, "date": self.date}

    def to_json(self):
        return json.JSONEncoder(sort_keys=True, indent=4, ensure_ascii=False).encode(self.to_dict())

    def formatted_time(self):
        dt_object = datetime.fromtimestamp(self.date, tz=timezone.utc)
        formatted_time = dt_object.strftime('%d/%m/%y %H-%M-%S')
        return formatted_time

    @staticmethod
    def from_json(json_dct: dict):
        info = MessedBannersInfo()

        info.banners = json_dct.get("banners", info.banners)
        info.date = json_dct.get("date", info.date)

        return info
