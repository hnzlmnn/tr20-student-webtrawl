import datetime


class Headers:
    def __init__(self, headers: dict = None, *, include_default=True):
        if headers is None or type(headers) is not dict:
            headers = {}
        self.headers = {}
        if include_default:
            self[b"Content-Type"] = b"text/plain"
            self[b"Date"] = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT').encode("ascii")
            self[b"Server"] = b"WebTrawl"
        self.headers.update(headers)

    def __getitem__(self, item: bytes):
        if type(item) is not bytes:
            return b""
        return self.headers.get(item.lower(), b"")

    def __setitem__(self, key: bytes, value: bytes):
        if type(key) is not bytes:
            raise ValueError("Header names must be bytes")
        if type(value) is not bytes:
            raise ValueError("Header values must be bytes")
        self.headers[key.lower()] = value

    def has(self, item: bytes):
        return item.lower() in self.headers

    def __str__(self):
        return bytes(self).decode("ascii")

    def __bytes__(self):
        return b"\r\n".join(name + b": " + value for name, value in self.headers.items())

    def __json__(self):
        return {
            key.decode("ascii"): value.decode("ascii") for key, value in self.headers.items()
        }

    def pop(self, item, default=None):
        return self.headers.pop(item.lower(), default)
