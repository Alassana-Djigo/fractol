"""Cache em memória (LRU, limitada em bytes) para respostas já calculadas."""

import os
import threading
from collections import OrderedDict


class ByteLRU:
    """Guarda `bytes` por chave; ao passar o limite, sai o menos usado."""

    def __init__(self, max_bytes: int):
        self.max_bytes = max_bytes
        self._items: OrderedDict = OrderedDict()
        self._size = 0
        self._lock = threading.Lock()

    @property
    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return len(self._items)

    def get(self, key):
        with self._lock:
            value = self._items.get(key)
            if value is not None:
                self._items.move_to_end(key)
            return value

    def put(self, key, value: bytes) -> None:
        if len(value) > self.max_bytes:
            return
        with self._lock:
            old = self._items.pop(key, None)
            if old is not None:
                self._size -= len(old)
            self._items[key] = value
            self._size += len(value)
            while self._size > self.max_bytes:
                _, evicted = self._items.popitem(last=False)
                self._size -= len(evicted)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._size = 0


# Limite configurável pela variável de ambiente FRACTOL_CACHE_MB (por processo).
DATA_CACHE = ByteLRU(int(os.environ.get("FRACTOL_CACHE_MB", "64")) * 1024 * 1024)
