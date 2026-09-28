"""The transport: an HTTPS GET with one persistent connection per thread, and the REASON of a failure.

⚠⚠ Two failures are never confused: "absent from the bucket" (403 or 404, a fact about the data) and "the
network failed" (anything else, a fact about the wire). The research paid for confusing them: a cut had made
chunks look absent without anything saying so (`src/nappe/ou_le_maillage_quitte_t_il_son_feuillet.py:99` on
the `experimental` branch).

⭐ The connection is kept open per thread. The research reader opened one TLS connection per chunk, in series:
1.03 s per chunk of 1.78 MB. Here each thread reuses its own, and the band reader runs several at once.
"""
from __future__ import annotations

import http.client
import threading
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

ABSENT = "absent from the bucket"
NETWORK = "the network failed"


@dataclass(frozen=True)
class Response:
    body: bytes | None
    reason: str | None  # None when the body is there
    retries: int = 0


class Transport:
    """GET with bounded retries: 4 attempts, waiting 0.5 s, 1 s, 2 s, as the research did."""

    def __init__(self, timeout: float = 120.0, retries: int = 3, pause: float = 0.5, journal=None):
        self.timeout, self.retries, self.pause, self.journal = timeout, retries, pause, journal
        self._local = threading.local()
        self.bytes_read = 0
        self._lock = threading.Lock()
        self._all: list[http.client.HTTPSConnection] = []  # to close them, thread dead or alive

    def _connection(self, host: str) -> http.client.HTTPSConnection:
        pool = getattr(self._local, "pool", None)
        if pool is None:
            pool = self._local.pool = {}
        c = pool.get(host)
        if c is None:
            c = pool[host] = http.client.HTTPSConnection(host, timeout=self.timeout)
            with self._lock:
                self._all.append(c)
        return c

    def close(self) -> None:
        """Closes every open connection, including those of threads that already finished.

        ⚠ A thread of a pool that dies does not close the connection stored in its `threading.local`: its TLS
        socket is collected open. Over a reading of thousands of chunks, that is a descriptor leak; the tests,
        which treat warnings as errors, caught it (`ResourceWarning`).
        """
        with self._lock:
            connections, self._all = self._all, []
        for c in connections:
            c.close()
        self._local = threading.local()

    def _forget(self, host: str) -> None:
        c = getattr(self._local, "pool", {}).pop(host, None)
        if c is not None:
            c.close()

    def get(self, url: str) -> Response:
        parts = urlsplit(url)
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        last = "?"
        for attempt in range(self.retries + 1):
            try:
                c = self._connection(parts.netloc)
                c.request("GET", path, headers={"Connection": "keep-alive"})
                r = c.getresponse()
                body = r.read()
                if r.status in (403, 404):
                    return Response(None, ABSENT, attempt)
                if r.status == 200:
                    with self._lock:
                        self.bytes_read += len(body)
                    return Response(body, None, attempt)
                last = f"HTTP {r.status}"
            except (OSError, http.client.HTTPException) as e:
                last = type(e).__name__
                self._forget(parts.netloc)
            if attempt < self.retries:
                time.sleep(self.pause * (2.0 ** attempt))
        if self.journal is not None:
            self.journal.warn("TRANSPORT_FAILED", url=url, reason=last, attempts=self.retries + 1)
        return Response(None, f"{NETWORK}: {last}", self.retries)


class InMemoryTransport:
    """A test transport: a dictionary from URLs to bodies. A missing URL is "absent", a URL mapped to
    `None` simulates a dropped wire."""

    def __init__(self, bodies: dict[str, bytes | None]):
        self.bodies = bodies
        self.requests: list[str] = []
        self.bytes_read = 0

    def close(self) -> None:
        pass

    def get(self, url: str) -> Response:
        self.requests.append(url)
        if url not in self.bodies:
            return Response(None, ABSENT)
        x = self.bodies[url]
        if x is None:
            return Response(None, f"{NETWORK}: simulated")
        self.bytes_read += len(x)
        return Response(x, None)
