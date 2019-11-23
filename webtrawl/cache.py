import pickle
from datetime import timedelta, datetime


class Cache:
    KEEP_DELAY_PER_HIT = timedelta(seconds=10)
    KEEP_DELAY_MAX = timedelta(minutes=10)

    def __init__(self, persistence_file):
        self.persistence_file = persistence_file
        try:
            with open(self.persistence_file, "rb") as file:
                self.cache = pickle.load(file)
        except (pickle.UnpicklingError, FileNotFoundError):
            self.cache = {
                "last-hit": {},
                "hits": {},
                "items": {},
                "permanent": set(),
            }
        self.free()

    def flush(self):
        self.cache = {}
        self.persist()

    def persist(self):
        try:
            with open(self.persistence_file, "wb") as file:
                pickle.dump(self.cache, file)
        except pickle.PickleError:
            pass

    def has(self, *, request=None, id=None):
        if request is None and id is None:
            raise ValueError("Either request or id is required")
        if id is None:
            id = self.calculate_id(request)
        return id in self.cache["items"]

    def get(self, *, request=None, id=None, default=None):
        if request is None and id is None:
            raise ValueError("Either request or id is required")
        if id is None:
            id = self.calculate_id(request)
        item = self.cache["items"].get(id, None)
        if item is None:
            return default
        self.hit(id)
        return item

    def all(self):
        return list(self.cache["items"].keys())

    def last_hit(self, id):
        return self.cache["last-hit"].get(id, None)

    def last_hit_bytes(self, id):
        hit = self.last_hit(id)
        if hit is None:
            return b""
        return hit.strftime("%c").encode("ascii")

    def hits(self, id):
        return self.cache["hits"].get(id, 0)

    def hit(self, id):
        self.cache["hits"].setdefault(id, 0)
        self.cache["hits"][id] += 1
        self.cache["last-hit"][id] = datetime.now()

    def is_permanent(self, id):
        return id in self.cache["permanent"]

    def mark_permanent(self, id, save=True):
        self.cache["permanent"].add(id)
        if save:
            self.persist()

    def unmark_permanent(self, id, save=True):
        self.cache["permanent"].discard(id)
        if save:
            self.persist()

    def delete(self, id):
        self.cache["items"].pop(id)
        self.cache["hits"].pop(id)
        self.cache["last-hit"].pop(id)

    def free(self):
        for id in list(self.cache["items"].keys()):
            if self.is_permanent(id):
                continue
            last_hit = self.last_hit(id)
            if last_hit is None:
                self.delete(id)
            diff =  datetime.now() - last_hit
            if diff > self.KEEP_DELAY_MAX or diff > self.KEEP_DELAY_PER_HIT * self.hits(id):
                self.delete(id)

    def calculate_id(self, request):
        return request.cache()

    def update(self, response, *, request=None, id=None, permanent=False):
        if request is None and id is None:
            raise ValueError("Either request or id is required")
        if id is None:
            id = self.calculate_id(request)
        if permanent:
            self.mark_permanent(id, False)
        else:
            self.unmark_permanent(id, False)
        self.cache["items"].setdefault(id, response)
        self.hit(id)
        self.free()
        self.persist()
