class BannersEditorSettings:
    map_update_time: str = ""
    last_mapping_time: int = 0
    daily_banner_id: str = ""
    admins = ["test"]

    def to_json(self):
        return self.__dict__
