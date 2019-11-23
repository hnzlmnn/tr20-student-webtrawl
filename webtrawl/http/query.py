from urllib.parse import quote_from_bytes


class Query:
    parameters = None

    def __init__(self, query: bytes):
        if query is None:
            return
        self.parameters = {}
        if b"#" in query:
            query = query[:query.index(b"#")]
        pairs = query.split(b"&")
        for pair in pairs:
            if b"=" in pair:
                name, value = pair.split(b"=", 1)
            else:
                name, value = pair, b""
            if name == b"":
                continue
            self[name] = value

    def values(self):
        if not self.parameters:
            return iter([])
        return self.parameters.values()

    def keys(self):
        if not self.parameters:
            return iter([])
        return self.parameters.keys()

    def items(self):
        if not self.parameters:
            return iter([])
        return self.parameters.items()

    def __getitem__(self, item):
        if type(item) is not bytes:
            return None
        return self.parameters.get(item, None)

    def __setitem__(self, key, value):
        if type(key) is not bytes:
            raise ValueError("Query parameter names must be bytes")
        if type(value) is not bytes:
            raise ValueError("Query parameter values must be bytes")
        self.parameters[key] = value

    def __str__(self):
        return bytes(self).decode("ascii")

    def __bytes__(self):
        if not self.parameters:
            return b""
        return b"?" + b"&".join(b"=".join([name, value]) for name, value in self.parameters.items())

    def __json__(self):
        if not self.parameters:
            return None
        return {
            key.decode("ascii"): value.decode("ascii") for key, value in self.parameters.items()
        }
