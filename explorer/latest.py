"""Pedido mais recente de cada cliente, para largar cálculos já desactualizados."""

import threading
from collections import OrderedDict


class LatestRequests:
    """Guarda o número do pedido mais recente de cada cliente (por processo)."""

    def __init__(self, max_clients: int = 1000):
        self.max_clients = max_clients
        self._latest: OrderedDict[str, int] = OrderedDict()
        self._lock = threading.Lock()

    def note(self, client: str, rid: int) -> None:
        with self._lock:
            if rid > self._latest.get(client, -1):
                self._latest[client] = rid
            self._latest.move_to_end(client)
            while len(self._latest) > self.max_clients:
                self._latest.popitem(last=False)

    def is_stale(self, client: str, rid: int) -> bool:
        """Verdade se já chegou um pedido mais recente deste cliente."""
        with self._lock:
            return self._latest.get(client, -1) > rid


LATEST = LatestRequests()
