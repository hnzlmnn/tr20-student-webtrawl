http_status = {
    100: b"Continue",
    101: b"Switching Protocols",
    102: b"Processing",
    200: b"OK",
    201: b"Created",
    202: b"Accepted",
    203: b"Non-authoritative Information",
    204: b"No Content",
    205: b"Reset Content",
    206: b"Partial Content",
    207: b"Multi-Status",
    208: b"Already Reported",
    226: b"IM Used",
    300: b"Multiple Choices",
    301: b"Moved Permanently",
    302: b"Found",
    303: b"See Other",
    304: b"Not Modified",
    305: b"Use Proxy",
    307: b"Temporary Redirect",
    308: b"Permanent Redirect",
    400: b"Bad Request",
    401: b"Unauthorized",
    402: b"Payment Required",
    403: b"Forbidden",
    404: b"Not Found",
    405: b"Method Not Allowed",
    406: b"Not Acceptable",
    407: b"Proxy Authentication Required",
    408: b"Request Timeout",
    409: b"Conflict",
    410: b"Gone",
    411: b"Length Required",
    412: b"Precondition Failed",
    413: b"Payload Too Large",
    414: b"Request-URI Too Long",
    415: b"Unsupported Media Type",
    416: b"Requested Range Not Satisfiable",
    417: b"Expectation Failed",
    418: b"I'm a teapot",
    421: b"Misdirected Request",
    422: b"Unprocessable Entity",
    423: b"Locked",
    424: b"Failed Dependency",
    426: b"Upgrade Required",
    428: b"Precondition Required",
    429: b"Too Many Requests",
    431: b"Request Header Fields Too Large",
    444: b"Connection Closed Without Response",
    451: b"Unavailable For Legal Reasons",
    499: b"Client Closed Request",
    500: b"Internal Server Error",
    501: b"Not Implemented",
    502: b"Bad Gateway",
    503: b"Service Unavailable",
    504: b"Gateway Timeout",
    505: b"HTTP Version Not Supported",
    506: b"Variant Also Negotiates",
    507: b"Insufficient Storage",
    508: b"Loop Detected",
    510: b"Not Extended",
    511: b"Network Authentication Required",
    599: b"Network Connect Timeout Error",
}


class Status:
    def __init__(self, code: int = 200, *, version: str = None, description: str = None):
        if type(code) is not int:
            code = int(code)
        self.code = code
        if version is None:
            version = b"HTTP/1.0"
        if type(version) is str:
            try:
                version = version.encode("ascii")
            except UnicodeEncodeError:
                version = b"HTTP/1.0"
        self.version = version
        if description is None:
            description = http_status.get(self.code, b"Unknown")
        elif type(description) is str:
            try:
                description = description.encode("ascii")
            except UnicodeEncodeError:
                description = b"Invalid"
        self.description = description

    def __str__(self):
        return bytes(self).decode("ascii")

    def __json__(self):
        return {
            "version": self.version.decode("ascii"),
            "code": self.code,
            "description": self.description.decode("utf8", "backslashreplace"),
        }

    def __bytes__(self):
        return b" ".join([
            self.version,
            str(self.code).encode("ascii"),
            self.description,
        ])
