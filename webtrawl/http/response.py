from webtrawl.http.headers import Headers
from webtrawl.http.status import Status


class Response:
    def __init__(self, status=None, *, headers=None, body: bytes = None):
        if type(status) is int:
            status = Status(status)
        self.status = status
        if headers is None:
            headers = Headers()
        elif type(headers) is dict:
            headers = Headers(headers)
        self.headers = headers
        if body is None:
            body = b""
        if type(body) is not bytes:
            raise ValueError("Response body must be bytes got type {}".format(type(body)))
        self.body = body

    def parse(self, line, header_done=False):
        if self.status is None:
            self._parse_status_line(line)
        elif not header_done:
            self._parse_header_line(line)
        else:
            self.body += line

    def __str__(self):
        return bytes(self).decode("ascii")

    def __json__(self, include_body=False):
        return {
            "status": self.status.__json__(),
            "headers": self.headers.__json__(),
            "body": self.body.decode("utf8", "backslashreplace") if include_body and self.body else None,
        }

    def __bytes__(self):
        return b"\r\n".join([
            bytes(self.status),
            bytes(self.headers),
            b"",
            bytes(self.body),
        ])

    def send_bytes(self):
        self.headers[b"Content-Length"] = str(len(self.body)).encode("ascii")
        return bytes(self)

    def _parse_status_line(self, line):
        parts = line.split(b" ", 2)
        if len(parts) < 3:
            raise ValueError(b"Invalis status line: " + line)
        self.status = Status(parts[1], version=parts[0], description=parts[2])

    def _parse_header_line(self, line):
        if b": " not in line:
            raise ValueError(b"Invlaid header: " + line)
        name, value = line.split(b": ", 1)
        self.headers[name] = value
