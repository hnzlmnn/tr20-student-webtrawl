import urllib.parse

from webtrawl.http.query import Query


class URL:
    def __init__(self, href: bytes):
        if b"?" in href:
            path, query = href.split(b"?", 1)
        else:
            path = href
            query = None
        self.path = path
        self.query = Query(query)

    def __str__(self):
        return bytes(self).decode("ascii")

    def __json__(self):
        return {
            "path": self.path.decode("ascii"),
            "query": self.query.__json__(),
        }

    def __bytes__(self):
        return self.path + bytes(self.query)
