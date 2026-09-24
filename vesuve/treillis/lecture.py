"""E4 : les pas d'une bande, au format même que le producteur publie.

Une bande est une définition (`le_sens`, `le_centre`, `les_lignes`, `de`, `a`) ; sa lecture rend
`le_long` (les pas le long de chaque ligne), `en_travers` (les pas entre deux lignes voisines, qui
contrôlent la lecture contre les bandes publiées) et `les_lectures` (ce que chaque ligne a refusé, et
pourquoi). Les clés, les indexations et l'arrondi à quatre décimales sont ceux de
`deux_chemins_arrivent_ils_sur_la_meme_spire.py:200-263`, parce que la procédure sans main sert une
demande avec des bandes publiées ou lues : un format à deux orthographes serait deux procédures.

⚠⚠ Une bande est lue ENTIÈRE ou refusée : un chunk perdu par le réseau rend toute la bande
indécidable, et elle n'est jamais publiée à moitié.
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

from vesuve import noyau
from vesuve.noyau import Indecidable
from vesuve.transport import RESEAU
from vesuve.treillis.digest import LA_LARGEUR_DU_BORD, LE_COTE, LES_COUPES, CacheDeDigests, Digest, digerer

LE_DEMI_FEUILLET = 36  # round(173 / 2,4 / 2) : la plage du pas ET le seuil du certificat


def _triple(pas: float, desaccord: float, coupes: int) -> list:
    return [round(pas, 4), round(desaccord, 4), int(coupes)]


def la_couture(a: Digest, cote_a: str, b: Digest, cote_b: str, plage: int = LE_DEMI_FEUILLET) -> list | None:
    """Le pas entre le bord `cote_a` de a et le bord `cote_b` de b, ou None s'il n'est pas lisible."""
    if not (a.retenu and b.retenu):
        return None
    try:
        return _triple(*noyau.pas_dune_couture(a.profil(cote_a), b.profil(cote_b),
                                               [1] * len(LES_COUPES), plage))
    except Indecidable:
        return None


class LecteurDeBandes:
    """Lit les chunks d'une bande en parallèle, les réduit en digests, et rend ses pas."""

    def __init__(self, tableau, cache: CacheDeDigests | None, fils: int = 16, journal=None, segment: str = ""):
        self.tableau, self.cache, self.fils, self.journal, self.segment = tableau, cache, fils, journal, segment
        self._memoire: dict[tuple[int, int], Digest] = {}
        self.chunks_lus = 0

    def digest(self, cy: int, cx: int) -> Digest:
        cle = (int(cy), int(cx))
        d = self._memoire.get(cle)
        if d is None and self.cache is not None:
            d = self.cache.lire(*cle)
        if d is None:
            c = self.tableau.chunk(0, *cle)
            d = digerer(*cle, c.bloc, c.raison, c.reprises)
            self.chunks_lus += 1
            if self.cache is not None:
                self.cache.ecrire(d)
        self._memoire[cle] = d
        return d

    def precharger(self, positions) -> None:
        manquants = [p for p in dict.fromkeys(positions) if p not in self._memoire]
        if not manquants:
            return
        debut, octets = time.monotonic(), getattr(self.tableau.transport, "octets", 0)
        with ThreadPoolExecutor(max_workers=self.fils) as pool:
            list(pool.map(lambda p: self.digest(*p), manquants))
        if self.journal is not None:
            duree = time.monotonic() - debut
            lus = getattr(self.tableau.transport, "octets", 0) - octets
            self.journal.info("CHUNKS_LUS", combien=len(manquants), secondes=round(duree, 2),
                              mo_par_s=round(lus / 1e6 / max(duree, 1e-9), 1), fils=self.fils)

    def _la_ligne(self, sens: str, ligne: int, voulues: list[int]) -> tuple[dict[int, Digest], dict]:
        digests = {v: self.digest(*((ligne, v) if sens == "rangees" else (v, ligne))) for v in voulues}
        refus: dict[str, int] = {}
        for d in digests.values():
            if not d.retenu:
                refus[d.raison] = refus.get(d.raison, 0) + 1
        pannes = sum(n for r, n in refus.items() if r.startswith(RESEAU))
        nom = "rangée" if sens == "rangees" else "colonne"
        if pannes:
            raise Indecidable(f"{pannes} chunks perdus par le réseau sur la {nom} {ligne} : une ligne dont le fil "
                              f"est tombé n'est pas comparable")
        lus = sum(1 for d in digests.values() if d.retenu)
        if lus == 0:
            raise Indecidable(f"la {nom} {ligne} est vide : {refus}")
        cle, compte = (("la_rangee", "colonnes") if sens == "rangees" else ("la_colonne", "rangees"))
        lecture = {"segment": self.segment, "grille_de_chunks": list(self.tableau.grille[1:]), cle: int(ligne),
                   "le_cote_du_chunk": LE_COTE, "la_largeur_du_bord": LA_LARGEUR_DU_BORD,
                   "les_rangees_lues": list(LES_COUPES), "les_colonnes_de_coupe": list(LES_COUPES),
                   f"{compte}_demandees": len(voulues), f"{compte}_lues": lus,
                   "les_reprises_du_reseau": sum(d.reprises for d in digests.values()), "refuses": refus}
        return digests, lecture

    def lire(self, bande: dict) -> dict:
        """La bande publiée : {définition, le_long, en_travers, les_lectures}, clés en chaînes."""
        sens, lignes = bande["le_sens"], [int(x) for x in bande["les_lignes"]]
        voulues = list(range(int(bande["de"]), int(bande["a"]) + 1))
        self.precharger([(l, v) if sens == "rangees" else (v, l) for l in lignes for v in voulues])
        le_long, en_travers, lectures, precedente = {}, {}, {}, None
        for l in lignes:
            digests, lectures[str(l)] = self._la_ligne(sens, l, voulues)
            if sens == "rangees":  # le long : horizontal, clé = colonne de gauche ; en travers : vertical
                long_ = {v: la_couture(digests[v], "droit", digests[v + 1], "gauche")
                         for v in voulues if v + 1 in digests}
                if precedente is not None:
                    for v in voulues:
                        x = la_couture(precedente[1][v], "bas", digests[v], "haut")
                        if x is not None:
                            en_travers.setdefault(str(precedente[0]), {})[str(v)] = x
            else:  # le long : vertical, clé = rangée du dessus ; en travers : horizontal, clé = colonne de gauche
                long_ = {v: la_couture(digests[v], "bas", digests[v + 1], "haut")
                         for v in voulues if v + 1 in digests}
                if precedente is not None:
                    for v in voulues:
                        x = la_couture(precedente[1][v], "droit", digests[v], "gauche")
                        if x is not None:
                            en_travers.setdefault(str(v), {})[str(precedente[0])] = x
            le_long[str(l)] = {str(v): x for v, x in sorted(long_.items()) if x is not None}
            precedente = (l, digests)
        en_travers = {r: dict(sorted(s.items(), key=lambda kv: int(kv[0])))
                      for r, s in sorted(en_travers.items(), key=lambda kv: int(kv[0]))}
        return {"le_sens": sens, "le_centre": int(bande["le_centre"]), "les_lignes": lignes,
                "de": int(bande["de"]), "a": int(bande["a"]), "le_long": le_long, "en_travers": en_travers,
                "les_lectures": lectures}
