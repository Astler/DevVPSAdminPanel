class BannerServerItem:
    def __init__(self, name: str = "", mid: str = "", mdate: str = ""):
        self.name = name
        self.id = mid
        self.date = mdate

    def to_dict(self):
        return {"id": self.id, "name": self.name, "date": self.date}
