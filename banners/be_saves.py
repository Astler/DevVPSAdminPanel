class BannersEditorSaves:
    last_banners_map_update_time = 0

    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_json(json_dct: dict):
        info = BannersEditorSaves()

        info.last_banners_map_update_time = json_dct.get("last_banners_map_update_time",
                                                         info.last_banners_map_update_time)

        return info
