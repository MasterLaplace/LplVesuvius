#!/usr/bin/env python3
"""Un pool de connexions HTTPS persistantes, une par fil.

⚠⚠ **Pourquoi ce fichier existe plutôt qu'un `curl` par objet.** Récupérer 41 538 objets
avec un processus `curl` chacun coûte une poignée de main TLS par objet : **mesuré à
7 objets/s**. Avec une connexion **gardée ouverte** sur des milliers de requêtes :
**195 à 209 objets/s**, soit **×28**. Ce qui coûte ici est la **latence**, pas le débit —
c'est la même leçon que `libcurl` face au binaire `curl`.

⚠ **Extrait ici parce qu'un second appelant est apparu.** Deux copies d'un pool de
connexions finiraient par ne pas s'accorder sur la reprise après fermeture, et c'est
exactement le genre de désaccord qui ne se voit qu'à la millième requête.
"""

from __future__ import annotations

import http.client
import threading
import time

_local = threading.local()


def connexion(hote: str, timeout: float = 120.0) -> http.client.HTTPSConnection:
    """Une connexion par fil, gardée ouverte. C'est tout l'intérêt."""
    c = getattr(_local, "conn", None)
    if c is None or getattr(_local, "hote", None) != hote:
        if c is not None:
            try:
                c.close()
            except Exception:
                pass
        c = http.client.HTTPSConnection(hote, timeout=timeout)
        _local.conn = c
        _local.hote = hote
    return c


def obtenir(hote: str, chemin: str, timeout: float = 120.0,
            essais: int = 3) -> bytes | None:
    """Rend le corps, ou None sur 404.

    ⚠ **Un 404 est NORMAL** ici : il veut dire « hors du volume », pas « panne ». Les
    confondre ferait passer un rouleau bordé de vide pour un téléchargement en échec.

    ⚠ Une connexion persistante FINIT par être fermée par le serveur ; la rouvrir est le
    cas normal, pas une erreur. Mais on ne réessaie pas indéfiniment, sinon une panne
    réelle ressemble à de la lenteur.
    """
    for essai in range(essais):
        try:
            c = connexion(hote, timeout)
            c.request("GET", chemin)
            r = c.getresponse()
            corps = r.read()
            if r.status == 200:
                return corps
            if r.status == 404:
                return None
            raise OSError(f"HTTP {r.status}")
        except Exception:
            try:
                _local.conn.close()
            except Exception:
                pass
            _local.conn = None
            if essai == essais - 1:
                raise
            time.sleep(0.2 * (essai + 1))
    return None
