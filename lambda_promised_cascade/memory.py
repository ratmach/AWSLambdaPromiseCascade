import redis
from uuid import uuid4


class SharedMemory:
    def __init__(self, uid=None):
        self.uid = uid or str(uuid4()).replace("-", "")
        self.client = redis.Redis()

    def __setattr__(self, key, value):
        if key not in ('uid', 'client'):
            self.client.set(key, value)
        else:
            super().__setattr__(key, value)

    def __getattr__(self, item):
        return self.client.get(item)

    def __setitem__(self, key, value):
        self.client.set(self.transform_key(key), value)

    def __getitem__(self, item):
        return self.client.get(self.transform_key(item))

    def transform_key(self, key):
        return f"{self.uid}__{key}"
