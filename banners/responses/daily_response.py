from flask import Response, json

from application import app
from application.base_response import BaseResponse


class DailyResponse(BaseResponse):
    daily_banner_id = ""
    previous_daily_banners = []

    def __init__(self, daily_banner_id: str, previous_daily_banners=[], success: bool = False, reason: str = "",
                 request_data=None):
        super().__init__(success, reason, request_data)

        if request_data is None:
            request_data = []

        self.daily_banner_id = daily_banner_id
        self.previous_daily_banners = previous_daily_banners
        self.success = success
        self.reason = reason
        self.init_request_fields(request_data)

    def init_request_fields(self, request_data: dict):
        for field in request_data:
            self.__dict__[field] = request_data[field]

    def to_response(self) -> Response:
        if self.success:
            status_code = 200
        else:
            status_code = 400

        return app.response_class(response=json.dumps(self.__dict__),
                                  status=status_code,
                                  mimetype='application/json')
