class Filter:

    def validate_request(self, request):
        return NotImplementedError()

    def validate_response(self, response):
        return NotImplementedError()


class BlacklistFilter(Filter):

    def __init__(self, blacklist):
        self.blacklist = blacklist

    def validate_request(self, request):
        for item in self.blacklist:
            for value in request.url.query.values():
                if item in value:
                    return False
            if item in request.body:
                return False
        return True

    def validate_response(self, response):
        return True
