from webtrawl.http.response import Response


class HttpException(Exception):
    status_code = 500
    detail = None

    def to_response(self):
        return Response(self.status_code)

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.to_response().status)


class HttpBadRequest(HttpException):
    status_code = 400


class HttpBadGateway(HttpException):
    status_code = 502


class HttpGatewayTimeout(HttpException):
    status_code = 504


class HttpNotImplemented(HttpException):
    status_code = 501


class HttpVersionNotSupported(HttpException):
    status_code = 505


class InvalidVerbException(HttpBadRequest):
    pass


class InvalidUrlException(HttpBadRequest):
    pass


class InvalidHeaderException(HttpBadRequest):
    pass


class InvalidHostException(HttpBadRequest):
    pass
