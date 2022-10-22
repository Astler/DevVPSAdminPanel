class BannersEditorAdminData:
    id = ""

    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_json(json_dct: dict):
        info = BannersEditorAdminData()

        info.id = json_dct.get("id", info.id)

        return info
