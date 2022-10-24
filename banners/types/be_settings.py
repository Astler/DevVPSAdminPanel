class BannersEditorSettings:
    map_update_time: str = ""
    daily_banner_id: str = ""
    admins = ["test"]

    def to_json(self):
        return self.__dict__
