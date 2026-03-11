from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int = 10) -> None:
        self._capacity = capacity
        self._cache = OrderedDict()

    def get(self, key: str) -> str:
        if key not in self._cache:
            return ''
        self._cache.move_to_end(key)
        return self._cache[key]

    def set(self, key: str, value: str) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._capacity:
            self._cache.popitem(last=False)

    def rem(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
