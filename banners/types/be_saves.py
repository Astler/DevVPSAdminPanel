class BannersEditorSaves:
    last_mapping_time: int = 0

    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_json(json_dct: dict):
        info = BannersEditorSaves()

        info.last_mapping_time = int(json_dct.get("last_mapping_time", info.last_mapping_time))

        return info
