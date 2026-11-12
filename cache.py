from collections import OrderedDict
import threading


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)

            self.cache[key] = value

            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    def get_stats(self):
        with self.lock:
            return {
                "hits": self.hits,
                "misses": self.misses,
                "items": len(self.cache),
                "capacity": self.capacity
            }