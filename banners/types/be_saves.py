class BannersEditorSaves:
    map_update_time: str = ""
    admins = ["test"]

    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_json(json_dct: dict):
        info = BannersEditorSaves()

        info.map_update_time = json_dct.get("map_update_time", info.map_update_time)
        info.admins = json_dct.get("admins", info.admins)

        return info

    def try_add_admin(self, admin_data):
        if admin_data.id not in self.admins:
            self.admins.append(admin_data.id)

        return self

