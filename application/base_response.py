from flask import Response, json

from application import app


class BaseResponse:
    success = False
    reason = ""
    request_data = ""

    def __init__(self, success: bool, reason: str = "", request_data: str = ""):
        self.success = success
        self.reason = reason
        self.request = request_data

    def to_response(self) -> Response:
        if self.success:
            status_code = 200
        else:
            status_code = 400

        return app.response_class(response=json.dumps(self.__dict__),
                                  status=status_code,
                                  mimetype='application/json')
