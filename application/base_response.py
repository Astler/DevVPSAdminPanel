from flask import Response, json

from application import app


class BaseResponse:
    def __init__(self, success: bool, reason: str = "", request_data=None):
        if request_data is None:
            request_data = []
        self.success = success
        self.reason = reason
        self.init_request_fields(request_data)

    def init_request_fields(self, request_data: dict):
        for field in request_data:
            self.__dict__[field] = request_data[field]

    def to_response(self) -> Response:
        return app.response_class(response=json.dumps(self.__dict__),
                                  status=200 if self.success else 400,
                                  mimetype='application/json')


class SuccessResponse(BaseResponse):
    def __init__(self, reason: str = "", request_data=None):
        super().__init__(True, reason, request_data)


class FailedResponse(BaseResponse):
    def __init__(self, reason: str = "", request_data=None):
        super().__init__(False, reason, request_data)
