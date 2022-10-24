from flask import Response, json

from application import app


class BaseResponse:
    success = False
    reason = ""

    def __init__(self, success: bool, reason: str = "", request_data: dict = []):
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
