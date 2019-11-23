import base64
import hashlib
import json
import socket

from webtrawl.http.exceptions import InvalidVerbException, HttpException, InvalidUrlException, HttpVersionNotSupported, \
    HttpBadRequest, InvalidHeaderException, InvalidHostException, HttpNotImplemented, HttpBadGateway, HttpGatewayTimeout
from webtrawl.http.headers import Headers
from webtrawl.http.response import Response
from webtrawl.http.url import URL


class Request:
    _CHUNK_SIZE = 1024 * 1024 * 1  # 1 MB chunks
    _UPSTREAM_CHUNK_SIZE = 1024 * 1  # 1 kB chunks
    VERBS = {
        b"GET": False,
        b"POST": True,
    }
    VERSIONS = [
        b"HTTP/1.0",
        b"HTTP/1.1",
        b"HTTP/2",
    ]
    HOSTS = [
        b"localhost:8081",
        b"webtrawl-test.fshbwl.ru",
    ]
    TIMEOUT = 30

    def __init__(self, sin, *, strict=True, upstream=("localhost", 80)):
        self.sin = sin
        self.strict = strict
        self.verb = None
        self.url = None
        self.version = None
        self.headers = Headers(include_default=False)
        self.body = None
        self.close_connection = True
        self.UPSTREAM = upstream

    def parse(self):
        finished_head = False
        line = b""
        while 1:
            try:
                if not finished_head:
                    buffer = self.sin.readline(65537)
                    if not buffer:
                        break
                    line += buffer
                    if len(line) > 65536:
                        raise HttpBadRequest()
                    if self.strict and line[-2:] != b"\r\n":
                        continue
                    if line in ([b"\r\n"] if self.strict else [b"\r\n", b"\n"]):
                        finished_head = True
                        conntype = self.headers[b"Connection"].lower()
                        if conntype == b"close":
                            self.close_connection = True
                        elif conntype.lower() == b"keep-alive":
                            self.close_connection = False
                        if self.headers[b"Expect"].lower() == "100-continue":
                            raise HttpNotImplemented()
                        self.body = b""
                        continue
                    if self.strict:
                        line = line[:-2]
                    elif line[-1:] == b"\n":
                        line = line[:-2] if line[-2:-1] == b"\r" else line[:-1]
                    if self.verb is None:
                        self._parse_first_line(line)
                        self._validate_verb()
                        self._validate_url()
                        self._validate_version()
                    else:
                        self._parse_header(line)
                else:
                    if self.VERBS[self.verb] is False or not self.headers.has(b"Content-Length"):
                        break
                    length = 0
                    content_length = int(self.headers[b"Content-Length"])
                    while length < content_length:
                        chunk = self.sin.read(min(self._CHUNK_SIZE, content_length - length))
                        length += len(chunk)
                        self.body += chunk
                    break
            except socket.timeout:
                raise
            except HttpException:
                raise
            except Exception as e:
                print(e)
                return False
            line = b""
        if not self.verb:
            raise InvalidVerbException()
        if not self.url:
            raise InvalidUrlException()
        if not self.version:
            raise HttpVersionNotSupported()
        self._validate_headers()
        return True

    def _parse_first_line(self, line: bytes):
        if not self.strict:
            while b"  " in line:
                line = line.replace(b"  ", b" ")
        args = line.split(b" ")
        self.verb = args[0]
        if len(args) < 2:
            return
        self.url = URL(args[1])
        if len(args) < 3:
            return
        self.version = args[2]

    def _parse_header(self, line: bytes):
        line = line.replace(b"\r", b"").replace(b"\n", b"")
        name, value = line.split(b": ", 2)
        if len(name) is 0:
            raise InvalidHeaderException
        if name[:10] == b"X-Magikarp" or name[:10] == b"x-magikarp":
            raise InvalidHeaderException
        self.headers[name] = value

    def _validate_verb(self):
        if self.verb not in self.VERBS.keys():
            raise InvalidVerbException()

    def _validate_url(self):
        pass

    def _validate_version(self):
        if self.version not in self.VERSIONS:
            raise HttpVersionNotSupported()

    def _validate_headers(self):
        if not self.headers[b"Host"] in self.HOSTS:
            raise InvalidHostException

    def forward(self):
        response = Response()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(float(self.TIMEOUT))
        try:
            s.connect(self.UPSTREAM)
            s.sendall(bytes(self))
            buffer = b""
            header_done = False
            while 1:
                chunk = s.recv(self._UPSTREAM_CHUNK_SIZE)
                if not chunk:
                    if not header_done:
                        raise HttpBadGateway()
                    try:
                        response.parse(buffer, True)
                    except ValueError as e:
                        raise HttpBadGateway()
                    break
                buffer += chunk
                lines = buffer.split(b"\r\n" if self.strict else b"\n")
                if len(lines) is 1:
                    continue
                for i in range(len(lines) - 1):
                    line = lines[i]
                    if not header_done and line == (b"" if self.strict else b"\r"):
                        header_done = True
                        continue
                    if header_done:
                        line += b"\r\n" if self.strict else b"\n"
                    try:
                        response.parse(line, header_done)
                    except ValueError as e:
                        raise HttpBadGateway()
                buffer = lines[-1]
        except socket.timeout:
            raise HttpGatewayTimeout()
        except socket.error as e:
            print(e)
            raise HttpBadGateway()
        finally:
            s.close()
        return response

    def __str__(self):
        return bytes(self).decode("ascii")

    def __json__(self, include_body=False):
        return {
            "verb": self.verb.decode("ascii"),
            "url": self.url.__json__(),
            "version": self.version.decode("ascii"),
            "headers": self.headers.__json__(),
            "body": self.body.decode("utf8", "backslashreplace") if include_body and self.body else None,
        }

    def __bytes__(self):
        return b"\r\n".join([
            b" ".join([self.verb, bytes(self.url), self.version]),
            bytes(self.headers),
            b"",
            self.body if self.body is not None else b"",
        ])

    def cache(self):
        h = hashlib.sha1()
        h.update(self.verb)
        h.update(bytes(self.url))
        h.update(self.version)
        h.update(self.headers[b"Host"])
        h.update(self.headers[b"Authorization"])
        h.update(self.body)
        return h.hexdigest().encode("ascii")
