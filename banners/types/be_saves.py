class BannersEditorSaves:
    map_update_time: str = ""

    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_json(json_dct: dict):
        info = BannersEditorSaves()

        info.map_update_time = json_dct.get("map_update_time", info.map_update_time)

        return info
