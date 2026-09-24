"""Le transport : un GET HTTPS avec connexion persistante par fil, et la RAISON d'un échec.

⚠⚠ Deux échecs ne se confondent jamais : « absent du dépôt » (403 ou 404, un fait sur la donnée) et
« le réseau a échoué » (tout le reste, un fait sur le fil). Le producteur a payé leur confusion : une
coupure avait fait passer des chunks pour absents sans que rien ne le dise
(`src/nappe/ou_le_maillage_quitte_t_il_son_feuillet.py:99`).

⭐ La connexion est gardée ouverte par fil. Le lecteur du producteur ouvrait une connexion TLS par
chunk, en série : 1,03 s par chunk de 1,78 Mo. Ici chaque fil réutilise la sienne, et le lecteur de
bandes en fait travailler plusieurs à la fois.
"""
from __future__ import annotations

import http.client
import threading
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

ABSENT = "absent du dépôt"
RESEAU = "le réseau a échoué"


@dataclass(frozen=True)
class Reponse:
    corps: bytes | None
    raison: str | None  # None quand le corps est là
    reprises: int = 0


class Transport:
    """GET avec reprises bornées : 4 essais, attentes 0,5 s, 1 s, 2 s, comme le producteur."""

    def __init__(self, delai: float = 120.0, reprises: int = 3, pause: float = 0.5, journal=None):
        self.delai, self.reprises, self.pause, self.journal = delai, reprises, pause, journal
        self._local = threading.local()
        self.octets = 0
        self._verrou = threading.Lock()

    def _connexion(self, hote: str) -> http.client.HTTPSConnection:
        pool = getattr(self._local, "pool", None)
        if pool is None:
            pool = self._local.pool = {}
        c = pool.get(hote)
        if c is None:
            c = pool[hote] = http.client.HTTPSConnection(hote, timeout=self.delai)
        return c

    def _oublier(self, hote: str) -> None:
        c = getattr(self._local, "pool", {}).pop(hote, None)
        if c is not None:
            c.close()

    def get(self, url: str) -> Reponse:
        morceaux = urlsplit(url)
        chemin = morceaux.path + (f"?{morceaux.query}" if morceaux.query else "")
        derniere = "?"
        for essai in range(self.reprises + 1):
            try:
                c = self._connexion(morceaux.netloc)
                c.request("GET", chemin, headers={"Connection": "keep-alive"})
                r = c.getresponse()
                corps = r.read()
                if r.status in (403, 404):
                    return Reponse(None, ABSENT, essai)
                if r.status == 200:
                    with self._verrou:
                        self.octets += len(corps)
                    return Reponse(corps, None, essai)
                derniere = f"HTTP {r.status}"
            except (OSError, http.client.HTTPException) as e:
                derniere = type(e).__name__
                self._oublier(morceaux.netloc)
            if essai < self.reprises:
                time.sleep(self.pause * (2.0 ** essai))
        if self.journal is not None:
            self.journal.warn("TRANSPORT_ECHEC", url=url, raison=derniere, essais=self.reprises + 1)
        return Reponse(None, f"{RESEAU} : {derniere}", self.reprises)


class TransportEnMemoire:
    """Un transport de test : un dictionnaire d'URL vers des corps. Une URL absente est « absente »,
    une URL qui vaut `None` simule un fil tombé."""

    def __init__(self, corps: dict[str, bytes | None]):
        self.corps = corps
        self.demandes: list[str] = []
        self.octets = 0

    def get(self, url: str) -> Reponse:
        self.demandes.append(url)
        if url not in self.corps:
            return Reponse(None, ABSENT)
        x = self.corps[url]
        if x is None:
            return Reponse(None, f"{RESEAU} : simulé")
        self.octets += len(x)
        return Reponse(x, None)
