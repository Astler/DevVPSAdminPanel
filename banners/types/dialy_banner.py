class DailyBanner:
    daily_banner_id: str = ""

    def to_json(self):
        return self.__dict__
