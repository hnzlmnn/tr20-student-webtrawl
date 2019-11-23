#!/usr/bin/env python3
import sys
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from webtrawl import application, create_logger
from webtrawl.cache import Cache
from webtrawl.filter import BlacklistFilter

HOST = socket.gethostname()

logger = create_logger("./logs/webtrawl.log")

cache = Cache("./cache.pickle")


class WafRequestHandler(BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            application(os.environ, self.rfile, self.wfile, logger=logger, cache=cache, filter=BlacklistFilter([
                b"'",
                b"%27",
                b"\"",
                b"%22",
            ]))
        except socket.timeout as e:
            self.close_connection = True
            return


PORT = int(sys.argv[1]) if sys.argv[1:] else 8000

if sys.argv[2:]:
    os.chdir(sys.argv[2])
    CWD = sys.argv[2]
else:
    CWD = os.getcwd()

server = ThreadingHTTPServer(('0.0.0.0', PORT), WafRequestHandler)
print("Serving HTTP traffic from", CWD, "on", HOST, "using port", PORT)

while 1:
    try:
        sys.stdout.flush()
        server.handle_request()
    except KeyboardInterrupt:
        print("\nShutting down server per users request.")
        break
