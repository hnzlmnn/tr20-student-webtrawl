import base64
import json
import os
import socket
import logging

from webtrawl.http.exceptions import HttpBadRequest, HttpException, HttpBadGateway, HttpGatewayTimeout
from webtrawl.http.request import Request
from webtrawl.http.response import Response
from webtrawl.loghandler import TimestampedRotatingFileHandler

__author__ = "@hnzlmnn"
__description__ = "This page is part of the TROOPERS20 student program, developed by @hnzlmnn"
__url__ = "https://troopers.de/students/"


def create_logger(path):
    path = os.path.abspath(path)
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    logger = logging.getLogger("WebTrawl")
    logger.setLevel(logging.INFO)

    handler = TimestampedRotatingFileHandler("{}/{}".format(dir, os.path.basename(path)), maxBytes=1024 * 1024 * 10)  # 10 MB per file
    logger.addHandler(handler)

    return logger


def log_request(logger, request, response):
    if not logger:
        return
    logger.log(logging.INFO, json.dumps({
        "request": request.__json__(),
        "response": response.__json__() if response else None,
    }))


def generate_response(request, cache):
    response = None
    cache_id = None
    if cache:
        cache_id = request.headers[b"X-Magikarp-Id"]
        if cache_id == b"":
            cache_id = cache.calculate_id(request)
        if request.headers[b"X-Magikarp-List"] == b"true":
            return Response(200, body=b"\n".join([
                b";".join([id, str(cache.hits(id)).encode("ascii"), cache.last_hit_bytes(id)]) for id in cache.all()
            ])+b"\n")
        response = cache.get(id=cache_id)
    if response is None:
        response = request.forward()
        response.headers[b"X-Frame-Options"] = b"SAMEORIGIN"
        response.headers[b"X-XSS-Protection"] = b"1; mode=block"
        response.headers[b"X-Protected-By"] = b"WebTrawl"
        if cache:
            response.headers[b"X-Magikarp-Id"] = cache_id
            cache.update(response, id=cache_id, permanent=(response.headers.pop(b"X-Magikarp-Forever", None) is not None))
    return response


def application(env, sin, sout, *, logger, cache=None, filter=None, strict=True):
    request = Request(sin, strict=strict, upstream=(env.get("UPSTREAM", "localhost"), int(env.get("UPSTREAM_PORT", 3003))))
    try:
        if not request.parse():
            raise HttpBadRequest()
        if filter:
            if not filter.validate_request(request):
                raise HttpBadRequest()
        try:
            response = generate_response(request, cache)
            if filter:
                if not filter.validate_response(response):
                    raise HttpBadRequest()
            # print(bytes(response))
            log_request(logger, request, response)
            sout.write(response.send_bytes())
            sout.flush()
        except socket.timeout:
            raise HttpGatewayTimeout()
        except Exception as e:
            print(e)
            raise HttpBadGateway()
    except HttpException as e:
        print(e)
        response = e.to_response()
        log_request(logger, request, response)
        sout.write(response.send_bytes())
        sout.flush()
