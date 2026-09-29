"""Au pas du prix, la matière dit-elle si une surface est posée sur sa feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL VOXEL NE SOIT LU POUR CETTE TRANCHE, SUR PHercParis4 COMME SUR PHerc0358. Ce qui
était vu avant d'écrire : ce que `24`, `38`, `49`, `54`, `81` et `248` à `297` publient, et les métadonnées des deux volumes,
de la prédiction `m7` et du produit `lasagna` de PHerc0358. ⚠ La surface automatique de PHerc0358 jugée ici est celle de `24` :
ses auto-intersections sont connues, et `38` a dit des tirages de R3 qu'ils ne convergent pas (α ≈ 1, avec la réserve de `49`).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST #5 (`R4-P16`, `R4-P17`, `R4-P11`). Tout ce que la chaîne fait part d'une surface
qu'une personne a tracée. Les treize rouleaux du prix n'en ont aucune et ne publient aucun rang de spire (`81`). Avant de
produire une première surface sur l'un d'eux, il faut un juge qui dise, sans référent, si elle est posée sur une feuille ; et
un juge sans référent n'est croyable que s'il a d'abord été vu séparer, là où la réponse est connue et au pas où il servira,
une surface juste de surfaces fausses fabriquées pour lui.

## Le juge : la place de la surface dans le profil de la matière

Pour chaque point de la surface, le profil du scan brut le long de sa normale, de −T à +T pas du volume jugé, avec
T = 200 µm (21 pas à 9,6 µm comme à 9,362 µm : plus d'un pas entre feuilles de part et d'autre). La note du point est le rang
de la valeur au point parmi les 2T autres du profil, ex æquo comptés pour moitié : 1 si la surface est au plus dense du
profil, 0 au plus creux. ⭐ Sa valeur au hasard est connue exactement : pour une surface dont la place par rapport aux feuilles
est uniforme, ce qui est le cas d'une surface qui traverse l'empilement, l'espérance de la note est 1/2, quel que soit le
rouleau, l'épaisseur des feuilles ou leur pas. La note d'une surface est la moyenne de ses points.

Le juge ne lit que le scan brut, jamais la prédiction `m7` sur laquelle le traceur a poussé la surface : un juge qui lirait ce
que le générateur lit se jugerait lui-même. Un profil constant ne porte rien : il est écarté et compté. Un point dont le
profil sort du volume est écarté et compté.

## L'étalonnage, au pas du prix, sur PHercParis4 au niveau 2 (9,6 µm)

Toutes les surfaces sont sur la même grille réduite (160 voxels par maille), sur les six blocs de `296`, suréchantillonnées
quatre fois (un point tous les 40 voxels, 96 µm) ; les normales sont recalculées sur la géométrie de chaque surface.

- le segment réduit : le tracé humain ;
- les quatre sauts de la chaîne de `248` (le premier est la spire produite de `275`), avec, maille par maille, le juge
  géométrique de `248` : juste, raté, ou non noté ;
- trois défauts plantés dans le segment, sur ses propres points :
  1. décalé d'un demi-pas le long de sa normale (36 voxels, le demi-pas de `248`) : entre deux feuilles ;
  2. une rampe douce : le long des colonnes, un décalage en dents de scie d'amplitude deux pas, de pente 1/4 (14°) ;
  3. une rampe raide : la même, de pente 1 (45°). Les rampes traversent l'empilement sans jamais s'éloigner de plus de deux
     pas du segment.

## Le rouleau, par une règle déclarée

Parmi les treize du prix, celui où une première surface automatique existe déjà dans l'arbre, poussée sur les seuls produits
publiés et reproductible depuis sa graine : PHerc0358 (`data/artefacts/PHerc0358`, `24`). ⚠ C'est une règle de coût, et ce
rouleau a été vu : `24` y a compté les auto-intersections de cette surface. Elle est jugée au niveau 0 (9,362 µm), par pièces
de 16 × 16 mailles, suréchantillonnées deux fois (un point tous les 10 voxels, 94 µm), avec les mêmes trois défauts plantés
sur elle-même, au pas de ce rouleau (187,24 µm, `espacement_PHerc0358_L1.json`).

## Les issues, exclusives

L'ÉTALONNAGE : le juge sépare au pas du prix si, sur chacun des six blocs, la note du segment dépasse 1/2 et celles de ses
deux rampes, et celle de son décalé est sous 1/2 ; et si, sur les six blocs réunis, les notes des deux rampes sont sous le
seuil τ = (note du segment + 1/2) / 2. Sinon : au pas du prix, la place dans le profil ne sépare pas une feuille d'une
traversée, et le rouleau n'est pas jugé. Indécidable si la chaîne de `297` ne se redonnait pas.

LE ROULEAU : indécidable si l'étalonnage ne sépare pas, ou si, sur la surface de PHerc0358, l'une de ses deux rampes plantées
atteint τ : le seuil ne se transporte pas d'un rouleau à l'autre. Sinon chaque pièce d'au moins 100 points jugés est posée
sur une feuille (note ≥ τ, et celle de son propre décalé sous 1/2), entre les feuilles (note ≤ 1 − τ), ou en travers ; et
l'issue est la part des points jugés de la surface qui sont dans des pièces posées sur une feuille.

## Rapporté à côté, qui ne décide rien

- sur les sauts de la chaîne, la note là où le juge de `248` dit juste et là où il dit raté : ce que la place dans le profil
  voit d'une spire ratée ;
- le profil moyen de chaque surface, chaque profil ramené à moyenne nulle et écart un, et le pas qu'il montre ;
- les profils écartés, sans matière ou hors du volume ;
- sur PHerc0358, la carte des pièces, et où tombent les auto-intersections de `24`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle feuille la surface est posée. Une surface qui passe d'une feuille à la voisine
sans se croiser est posée sur une feuille partout, et ce juge la passe ; c'est ce que le relevé sur les sauts ratés mesure. Ni
que la surface soit le recto, ni qu'elle se déroule, ni ce que vaut ce juge sur un autre rouleau que celui où son seuil se
vérifie par ses propres défauts.

Usage :
    uv run python src/nappe/la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille.py --verifier
    uv run python src/nappe/la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille.py --preparer
    uv run python src/nappe/la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille.py --lire 8
    uv run python src/nappe/la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille.py \\
        --json docs/mesures/la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
LE_DOSSIER = RACINE / "data" / "matiere_au_pas_du_prix"
LES_MORCEAUX = LE_DOSSIER / "morceaux"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
CE_QUE_297_A_PREPARE = RACINE / "data" / "encre_du_tour_voisin" / "la_chaine_plan.json"
LA_SURFACE_DE_24 = RACINE / "data" / "artefacts" / "PHerc0358" / "mesh.tifxyz"
LES_CROISEMENTS_DE_24 = RACINE / "data" / "artefacts" / "PHerc0358" / "selfcross_a.json"
LE_PAS_DE_0358 = RACINE / "docs" / "mesures" / "espacement_PHerc0358_L1.json"

LA_FENETRE_UM = 200.0
LES_VOLUMES = {
    "PHercParis4": {"url": f"{BUCKET}/PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr",
                    "niveau": 2, "facteur": 4, "le_voxel_um": 9.6, "le_voxel_plein_um": 2.4},
    "PHerc0358": {"url": f"{BUCKET}/PHerc0358/volumes/20250821151737-9.362um-1.2m-113keV-masked.zarr",
                  "niveau": 0, "facteur": 1, "le_voxel_um": 9.362, "le_voxel_plein_um": 9.362},
}
LE_SURECHANTILLONNAGE = {"PHercParis4": 4, "PHerc0358": 2}
LA_PIECE_EN_MAILLES = 16
LE_MINIMUM_DE_POINTS_PAR_PIECE = 100
LES_PENTES = {"rampe_douce": 0.25, "rampe_raide": 1.0}
LAMPLITUDE_EN_PAS = 2.0
LES_DEFAUTS = ("decale_dun_demi_pas", "rampe_douce", "rampe_raide")
LE_HASARD = 0.5


def la_demi_fenetre(volume: str) -> int:
    """T, en pas du volume jugé : 200 µm, arrondis."""
    return int(round(LA_FENETRE_UM / LES_VOLUMES[volume]["le_voxel_um"]))


# ── La géométrie des surfaces ──────────────────────────────────────────────────────────────────────────────────────

def surechantillonner(points: np.ndarray, valide: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """La grille (h, w, 3) interpolée k fois par maille, en bilinéaire ; un point est valide si les quatre coins de sa maille
    le sont."""
    h, w = valide.shape
    if h < 2 or w < 2:
        return np.zeros((0, 0, 3)), np.zeros((0, 0), dtype=bool)
    p = np.where(valide[..., None], points, 0.0)
    r = np.arange((h - 1) * k + 1) / k
    c = np.arange((w - 1) * k + 1) / k
    r0 = np.minimum(np.floor(r).astype(int), h - 2)
    c0 = np.minimum(np.floor(c).astype(int), w - 2)
    fr, fc = (r - r0)[:, None, None], (c - c0)[None, :, None]
    a, b = p[r0][:, c0], p[r0][:, c0 + 1]
    d, e = p[r0 + 1][:, c0], p[r0 + 1][:, c0 + 1]
    out = (1 - fr) * ((1 - fc) * a + fc * b) + fr * ((1 - fc) * d + fc * e)
    ok = valide[r0][:, c0] & valide[r0][:, c0 + 1] & valide[r0 + 1][:, c0] & valide[r0 + 1][:, c0 + 1]
    return out, ok


def la_dent_de_scie(x: np.ndarray, pente: float, amplitude: float) -> np.ndarray:
    """Un décalage continu, de 0 à `amplitude` et retour, de pente ±`pente` : une surface qui traverse l'empilement sans
    s'éloigner de plus d'`amplitude` de son origine."""
    u = (np.asarray(x, dtype=float) * pente / amplitude) % 2.0
    return amplitude * (1.0 - np.abs(u - 1.0))


def les_defauts(points: np.ndarray, valide: np.ndarray, normales: np.ndarray, n_ok: np.ndarray, demi_pas: float,
                pas: float, pas_de_grille: float) -> dict:
    """Les trois défauts plantés, sur les propres points d'une surface : décalée d'un demi-pas, et deux rampes."""
    ok = valide & n_ok
    out = {"decale_dun_demi_pas": (points + demi_pas * normales, ok.copy())}
    x = np.arange(points.shape[1]) * pas_de_grille
    for nom, pente in LES_PENTES.items():
        dec = la_dent_de_scie(x, pente, LAMPLITUDE_EN_PAS * pas)
        out[nom] = (points + dec[None, :, None] * normales, ok.copy())
    return out


def les_points_juges(points: np.ndarray, valide: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Les points qui ont une normale sur leur propre géométrie : (n, 3) positions, (n, 3) normales, (n, 2) indices."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    n, n_ok = les_normales(points, valide)
    ok = valide & n_ok
    ii = np.argwhere(ok)
    return points[ok], n[ok], ii


# ── Le volume, par morceaux ────────────────────────────────────────────────────────────────────────────────────────

class LesMorceaux:
    """Les morceaux d'un volume zarr, rangés sur disque une fois tirés, relus par un cache borné.

    Un morceau absent de la source vaut la valeur de remplissage, comme zarr le veut ; un échec de transport lève : « rien
    ici » et « je n'ai pas pu regarder » sont deux réponses différentes.
    """

    def __init__(self, nom: str, url: str | None, niveau: int, meta: dict | None = None, source=None,
                 dossier: Path | None = None, garder: int = 256):
        self.nom, self.url, self.niveau = nom, url, niveau
        self.source = source
        self.dossier = (dossier or LES_MORCEAUX) / nom / str(niveau)
        if meta is None:
            import tracecheck as tc
            meta = tc.array_meta(url, niveau, 60.0)
        self.meta = meta
        self.forme = tuple(int(v) for v in meta["shape"])
        self.taille = tuple(int(v) for v in meta["chunks"])
        self.remplissage = int(meta.get("fill_value") or 0)
        self._cache: OrderedDict = OrderedDict()
        self._garder = garder
        self.lus_sur_disque = 0

    def chemin(self, cz: int, cy: int, cx: int, genre: str = "raw") -> Path:
        """Le fichier d'un morceau. ⚠ Le genre est ajouté au nom, jamais substitué à son dernier point : remplacer le suffixe
        ferait de `94.28.34` un `94.28.absent`, que `94.28.35` lirait aussi comme le sien."""
        return self.dossier / f"{cz}.{cy}.{cx}.{genre}"

    def connu(self, cz: int, cy: int, cx: int) -> bool:
        return self.chemin(cz, cy, cx).exists() or self.chemin(cz, cy, cx, "absent").exists()

    def tirer(self, cz: int, cy: int, cx: int) -> str:
        """Range un morceau sur disque s'il n'y est pas ; rend 'deja', 'tire' ou 'absent'."""
        c = self.chemin(cz, cy, cx)
        if self.connu(cz, cy, cx):
            return "deja"
        if self.source is not None:
            brut, raison = self.source(cz, cy, cx)
        else:
            import tracecheck as tc
            cle = tc.chunk_key(self.meta, self.niveau, cy, cx, cz)
            brut, raison = tc.get_with_reason(f"{self.url}/{cle}", 60.0)
        self.dossier.mkdir(parents=True, exist_ok=True)
        if brut is None:
            if raison != "absent":
                raise RuntimeError(f"{self.nom} niveau {self.niveau} morceau {cz}.{cy}.{cx} : {raison}")
            self.chemin(cz, cy, cx, "absent").write_bytes(b"")
            return "absent"
        attendu = int(np.prod(self.taille))
        if (self.meta.get("compressor") or None) is not None:
            import tracecheck as tc
            brut = tc.decode(brut, self.meta, attendu)
            if brut is None:
                raise RuntimeError(f"{self.nom} morceau {cz}.{cy}.{cx} : décodage impossible")
        if len(brut) != attendu:
            raise RuntimeError(f"{self.nom} morceau {cz}.{cy}.{cx} : {len(brut)} octets pour {attendu}")
        tmp = self.chemin(cz, cy, cx, "part")
        tmp.write_bytes(brut)
        tmp.rename(c)
        return "tire"

    def morceau(self, cz: int, cy: int, cx: int) -> np.ndarray:
        cle = (cz, cy, cx)
        if cle in self._cache:
            self._cache.move_to_end(cle)
            return self._cache[cle]
        c = self.chemin(cz, cy, cx)
        if c.exists():
            a = np.fromfile(c, dtype=np.uint8).reshape(self.taille)
        elif self.chemin(cz, cy, cx, "absent").exists():
            a = np.full(self.taille, self.remplissage, dtype=np.uint8)
        else:
            raise RuntimeError(f"{self.nom} morceau {cz}.{cy}.{cx} pas tiré : --lire d'abord")
        self.lus_sur_disque += 1
        self._cache[cle] = a
        if len(self._cache) > self._garder:
            self._cache.popitem(last=False)
        return a

    def la_boite(self, bas: np.ndarray, haut: np.ndarray, besoin: set | None = None) -> np.ndarray:
        """Le volume dense de `bas` à `haut` inclus, en (z, y, x), assemblé des morceaux.

        Un morceau de la boîte que rien ne lit peut ne pas avoir été tiré : il reste à zéro. Un morceau de `besoin` qui n'a
        pas été tiré lève, pour qu'un morceau manquant ne se lise jamais comme du vide."""
        tz, ty, tx = self.taille
        out = np.zeros(tuple(int(h - b + 1) for b, h in zip(bas, haut)), dtype=np.uint8)
        for cz in range(bas[0] // tz, haut[0] // tz + 1):
            for cy in range(bas[1] // ty, haut[1] // ty + 1):
                for cx in range(bas[2] // tx, haut[2] // tx + 1):
                    if (besoin is not None and (cz, cy, cx) not in besoin and (cz, cy, cx) not in self._cache
                            and not self.connu(cz, cy, cx)):
                        continue
                    m = self.morceau(cz, cy, cx)
                    z0, y0, x0 = max(bas[0], cz * tz), max(bas[1], cy * ty), max(bas[2], cx * tx)
                    z1, y1, x1 = (min(haut[0], (cz + 1) * tz - 1), min(haut[1], (cy + 1) * ty - 1),
                                  min(haut[2], (cx + 1) * tx - 1))
                    out[z0 - bas[0]:z1 - bas[0] + 1, y0 - bas[1]:y1 - bas[1] + 1, x0 - bas[2]:x1 - bas[2] + 1] = \
                        m[z0 - cz * tz:z1 - cz * tz + 1, y0 - cy * ty:y1 - cy * ty + 1, x0 - cx * tx:x1 - cx * tx + 1]
        return out


def les_coordonnees(points: np.ndarray, normales: np.ndarray, facteur: float, T: int) -> np.ndarray:
    """(n, 2T+1, 3) : les positions du profil de chaque point, en voxels du niveau jugé, dans l'ordre (z, y, x) du tableau.
    Les points et les normales sont en (x, y, z), au niveau 0."""
    t = np.arange(-T, T + 1, dtype=float)
    c = points[:, None, :] / facteur + t[None, :, None] * normales[:, None, :]
    return c[..., ::-1]


def dans_le_volume(coords: np.ndarray, forme: tuple) -> np.ndarray:
    """Vrai pour les points dont tout le profil, voisins de l'interpolation compris, est dans le volume."""
    f = np.asarray(forme, dtype=float)
    return ((coords >= 0.0) & (coords <= f - 1.0)).all(axis=(1, 2))


def les_morceaux_complets(coords: np.ndarray, taille: tuple) -> set:
    """Tous les morceaux que l'interpolation touche : pour chaque échantillon, le cube de ses huit voisins."""
    out = set()
    t = np.asarray(taille)
    for pas in range(0, len(coords), 4096):
        c = coords[pas:pas + 4096].reshape(-1, 3)
        b = np.floor(c).astype(np.int64)
        lo, hi = b // t, (b + 1) // t
        for dz in (0, 1):
            for dy in (0, 1):
                for dx in (0, 1):
                    m = np.stack([(lo, hi)[dz][:, 0], (lo, hi)[dy][:, 1], (lo, hi)[dx][:, 2]], axis=1)
                    out.update(map(tuple, np.unique(m, axis=0).tolist()))
    return out


def les_profils(vol: LesMorceaux, coords: np.ndarray) -> np.ndarray:
    """Le scan, en trilinéaire, le long de chaque profil ; (n, 2T+1). Les points sont traités par morceau de leur centre,
    pour qu'une boîte n'assemble jamais plus que les morceaux voisins."""
    from scipy.ndimage import map_coordinates

    n, L, _ = coords.shape
    out = np.empty((n, L), dtype=np.float32)
    T = L // 2
    t = np.asarray(vol.taille)
    centre = np.floor(coords[:, T, :]).astype(np.int64) // t
    ordre = np.lexsort((centre[:, 2], centre[:, 1], centre[:, 0]))
    cles, debuts = np.unique(centre[ordre], axis=0, return_index=True)
    fins = list(debuts[1:]) + [len(ordre)]
    for d, f in zip(debuts, fins):
        idx = ordre[d:f]
        c = coords[idx]
        bas = np.floor(c.reshape(-1, 3).min(axis=0)).astype(np.int64)
        haut = np.minimum(np.floor(c.reshape(-1, 3).max(axis=0)).astype(np.int64) + 1, np.asarray(vol.forme) - 1)
        boite = vol.la_boite(bas, haut, les_morceaux_complets(c, vol.taille))
        loc = (c.reshape(-1, 3) - bas).T
        out[idx] = map_coordinates(boite, loc, order=1, mode="nearest").reshape(len(idx), L)
    return out


# ── La note ────────────────────────────────────────────────────────────────────────────────────────────────────────

def le_rang_au_centre(profils: np.ndarray) -> np.ndarray:
    """Le rang de la valeur au centre parmi les 2T autres du profil, ex æquo pour moitié : 1 au plus dense, 0 au plus creux."""
    T = profils.shape[1] // 2
    c = profils[:, T:T + 1]
    autres = np.delete(profils, T, axis=1)
    return ((autres < c).sum(axis=1) + 0.5 * (autres == c).sum(axis=1)) / autres.shape[1]


def sans_matiere(profils: np.ndarray) -> np.ndarray:
    """Un profil constant ne porte rien."""
    return profils.max(axis=1) == profils.min(axis=1)


def le_profil_moyen(profils: np.ndarray) -> list:
    """La moyenne des profils, chacun ramené à moyenne nulle et écart un."""
    if len(profils) == 0:
        return []
    m = profils.mean(axis=1, keepdims=True)
    s = profils.std(axis=1, keepdims=True)
    z = (profils - m) / np.where(s > 0, s, 1.0)
    return [round(float(v), 4) for v in z.mean(axis=0)]


def le_pas_montre(profil: list, voxel_um: float) -> float | None:
    """Le décalage, à partir de 5 pas, où le profil moyen, symétrisé, est le plus haut : le pas que la matière montre, en µm ;
    None si ce plus haut n'est pas au-dessus du creux qui le précède."""
    if not profil:
        return None
    p = np.asarray(profil)
    T = len(p) // 2
    sym = (p[T:] + p[T::-1]) / 2.0
    if T < 6:
        return None
    k = 5 + int(np.argmax(sym[5:]))
    if sym[k] <= sym[1:k].min():
        return None
    return round(k * voxel_um, 2)


def le_relief(profil: list) -> dict:
    """Ce qui se lit du profil moyen, sans rien décider : son amplitude, où il est le plus dense et le plus creux, en pas le
    long de la normale, et sa valeur au point."""
    if not profil:
        return {"lamplitude": None, "le_plus_dense": None, "le_plus_creux": None, "au_point": None}
    p = np.asarray(profil)
    T = len(p) // 2
    return {"lamplitude": round(float(p.max() - p.min()), 2), "le_plus_dense": int(np.argmax(p)) - T,
            "le_plus_creux": int(np.argmin(p)) - T, "au_point": round(float(p[T]), 4)}


def les_morceaux_absents(volume: str, cles: list) -> dict:
    """Parmi les morceaux que le plan demande, ceux que la source n'a pas : le vide que le scan masque."""
    v = LES_VOLUMES[volume]
    dossier = LES_MORCEAUX / volume / str(v["niveau"])
    absents = sum((dossier / f"{c[0]}.{c[1]}.{c[2]}.absent").exists() for c in cles)
    tires = sum((dossier / f"{c[0]}.{c[1]}.{c[2]}.raw").exists() for c in cles)
    return {"demandes": len(cles), "tires": int(tires), "absents": int(absents)}


def noter(profils: np.ndarray, dedans: np.ndarray) -> dict:
    """Ce qui se note d'un ensemble de profils : la note, les points jugés et écartés."""
    vide = sans_matiere(profils) & dedans
    juge = dedans & ~vide
    q = le_rang_au_centre(profils[juge]) if juge.any() else np.zeros(0)
    moyen = le_profil_moyen(profils[juge])
    return {"la_note": round(float(q.mean()), 4) if len(q) else None, "les_points_juges": int(juge.sum()),
            "sans_matiere": int(vide.sum()), "hors_du_volume": int((~dedans).sum()),
            "le_profil_moyen": moyen, "le_relief_du_profil": le_relief(moyen), "_q": q, "_juge": juge}


def public(d: dict) -> dict:
    return {k: v for k, v in d.items() if not k.startswith("_")}


# ── Les issues ─────────────────────────────────────────────────────────────────────────────────────────────────────

def le_seuil(note_du_segment: float) -> float:
    """Le milieu entre la note du tracé humain et le hasard."""
    return round((note_du_segment + LE_HASARD) / 2.0, 4)


def letalonnage_separe(blocs: list[dict], reunis: dict) -> dict:
    """Le juge sépare si, bloc par bloc, le segment dépasse 1/2 et ses deux rampes, son décalé est sous 1/2 ; et si, réunies,
    les deux rampes sont sous le seuil."""
    raisons = []
    for b in blocs:
        s = b["le_segment"]
        if s is None or any(b[d] is None for d in LES_DEFAUTS):
            raisons.append(f"bloc {b['le_bloc']} : une note manque")
            continue
        if not s > LE_HASARD:
            raisons.append(f"bloc {b['le_bloc']} : le segment n'est pas au-dessus du hasard ({s})")
        for r in LES_PENTES:
            if not s > b[r]:
                raisons.append(f"bloc {b['le_bloc']} : le segment ne dépasse pas sa {r} ({s} contre {b[r]})")
        if not b["decale_dun_demi_pas"] < LE_HASARD:
            raisons.append(f"bloc {b['le_bloc']} : le décalé n'est pas sous le hasard ({b['decale_dun_demi_pas']})")
    tau = le_seuil(reunis["le_segment"]) if reunis.get("le_segment") is not None else None
    if tau is None:
        raisons.append("pas de note pour le segment")
    else:
        for r in LES_PENTES:
            if reunis.get(r) is None or not reunis[r] < tau:
                raisons.append(f"réunies, la {r} atteint le seuil ({reunis.get(r)} contre τ = {tau})")
    return {"separe": not raisons and len(blocs) > 0, "le_seuil": tau, "les_raisons": raisons}


def la_piece(note: float | None, note_decalee: float | None, n: int, tau: float) -> str:
    if note is None or n < LE_MINIMUM_DE_POINTS_PAR_PIECE:
        return "non jugée"
    if note >= tau:
        return "posée sur une feuille" if (note_decalee is not None and note_decalee < LE_HASARD) else "en travers"
    if note <= 1.0 - tau:
        return "entre les feuilles"
    return "en travers"


def le_verdict(d: dict) -> dict:
    """L'issue de la tranche, depuis l'étalonnage et le rouleau."""
    if not d.get("la_chaine_de_297_se_redonne"):
        return {"decidable": False, "lissue": "indécidable : la chaîne de 297 ne se redonne pas"}
    e = d["letalonnage"]["le_verdict"]
    if not e["separe"]:
        return {"decidable": True, "separe": False,
                "lissue": "au pas du prix, la place dans le profil ne sépare pas une feuille d'une traversée"}
    tau = e["le_seuil"]
    r = d["le_rouleau"]
    for nom in LES_PENTES:
        if r["reunis"][nom] is None or r["reunis"][nom] >= tau:
            return {"decidable": False, "separe": True,
                    "lissue": f"indécidable : sur PHerc0358, sa {nom} plantée atteint τ = {tau} ({r['reunis'][nom]}) ; "
                              "le seuil ne se transporte pas"}
    pieces = r["les_pieces"]
    total = sum(p["les_points_juges"] for p in pieces if p["la_piece"] != "non jugée")
    posee = sum(p["les_points_juges"] for p in pieces if p["la_piece"] == "posée sur une feuille")
    part = round(posee / total, 4) if total else None
    return {"decidable": total > 0, "separe": True, "la_part_posee": part,
            "lissue": (f"la première surface de PHerc0358 est posée sur une feuille sur {part} de ses points jugés"
                       if total else "indécidable : aucune pièce de PHerc0358 n'a assez de points jugés")}


# ── Préparer, lire, mesurer ────────────────────────────────────────────────────────────────────────────────────────

def les_surfaces_de_paris4() -> dict:
    """Les surfaces de l'étalonnage, bloc par bloc : (points, normales, indices, bloc, juge de 248)."""
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz
    from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS, PAS_EN_VOXELS

    k = LE_SURECHANTILLONNAGE["PHercParis4"]
    blocs = [tuple(b) for b in json.loads(j296.LE_PLAN.read_text())["les_blocs_de_la_partie_b"]]
    noms = {"le_segment": j296.LES_SURFACES[0], "saut_1": j296.LES_SURFACES[1],
            **{f"saut_{h}": f"la_chaine_saut_{h}" for h in (2, 3, 4)}}
    grilles = {n: lire_tifxyz(j296.LE_DOSSIER / d / "maillage") for n, d in noms.items()}
    juges = {n: np.load(RACINE / "data" / "encre_du_tour_voisin" / f"la_chaine_juge_de_248_saut_{n[-1]}.npy")
             for n in noms if n.startswith("saut_")}
    esp = grilles["le_segment"][2]
    out = {n: [] for n in list(noms) + list(LES_DEFAUTS)}
    for b in blocs:
        lignes, colonnes = j296.les_mailles_dune_bande(*b, 1, esp)
        for n, (pts, ok, _) in grilles.items():
            L = lignes[lignes < ok.shape[0]]
            C = colonnes[colonnes < ok.shape[1]]
            sp, sok = surechantillonner(pts[np.ix_(L, C)], ok[np.ix_(L, C)], k)
            nn, nok = les_normales(sp, sok)
            ii = np.argwhere(sok & nok)
            juge = None
            if n in juges:
                J = juges[n]
                if J.shape != ok.shape:
                    raise RuntimeError(f"le juge de 248 du {n} a la forme {J.shape}, le maillage {ok.shape}")
                gi = np.clip(np.rint(ii[:, 0] / k).astype(int) + L[0], 0, J.shape[0] - 1)
                gj = np.clip(np.rint(ii[:, 1] / k).astype(int) + C[0], 0, J.shape[1] - 1)
                juge = J[gi, gj]
            out[n].append({"le_bloc": list(b), "points": sp[sok & nok], "normales": nn[sok & nok], "juge": juge})
            if n == "le_segment":
                for dn, (dp, dok) in les_defauts(sp, sok, nn, nok, float(DEMI_PAS_EN_VOXELS), float(PAS_EN_VOXELS),
                                                 esp / k).items():
                    dn_, dnok = les_normales(dp, dok)
                    m = dok & dnok
                    out[dn].append({"le_bloc": list(b), "points": dp[m], "normales": dn_[m], "juge": None})
    return out


def la_surface_de_0358() -> dict:
    """La surface de `24` et ses défauts, pièce par pièce."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    k = LE_SURECHANTILLONNAGE["PHerc0358"]
    pts, ok, esp = lire_tifxyz(LA_SURFACE_DE_24)
    pas = float(json.loads(LE_PAS_DE_0358.read_text())["seuils"]["0.5"]["median_um"]) / LES_VOLUMES["PHerc0358"]["le_voxel_um"]
    sp, sok = surechantillonner(pts, ok, k)
    nn, nok = les_normales(sp, sok)
    surfaces = {"la_surface_de_24": (sp, sok & nok, nn)}
    for dn, (dp, dok) in les_defauts(sp, sok, nn, nok, pas / 2.0, pas, esp / k).items():
        dn_, dnok = les_normales(dp, dok)
        surfaces[dn] = (dp, dok & dnok, dn_)
    P = LA_PIECE_EN_MAILLES * k
    out = {n: [] for n in surfaces}
    for n, (p, m, nr) in surfaces.items():
        for i0 in range(0, m.shape[0], P):
            for j0 in range(0, m.shape[1], P):
                mm = m[i0:i0 + P, j0:j0 + P]
                if not mm.any():
                    continue
                out[n].append({"la_piece": [i0 // k, j0 // k], "points": p[i0:i0 + P, j0:j0 + P][mm],
                               "normales": nr[i0:i0 + P, j0:j0 + P][mm], "juge": None})
    return out, {"le_pas_en_voxels": round(pas, 3), "le_demi_pas_en_voxels": round(pas / 2.0, 3),
                 "la_grille": list(ok.shape), "les_points_valides": int(ok.sum())}


def ranger(nom: str, morceaux: list[dict], cle: str) -> Path:
    LES_SURFACES_PREPAREES.mkdir(parents=True, exist_ok=True)
    f = LES_SURFACES_PREPAREES / f"{nom}.npz"
    np.savez_compressed(f, points=np.concatenate([m["points"] for m in morceaux]) if morceaux else np.zeros((0, 3)),
                        normales=np.concatenate([m["normales"] for m in morceaux]) if morceaux else np.zeros((0, 3)),
                        groupe=np.concatenate([np.full(len(m["points"]), i) for i, m in enumerate(morceaux)])
                        if morceaux else np.zeros(0, dtype=int),
                        juge=np.concatenate([m["juge"] if m["juge"] is not None else np.full(len(m["points"]), np.nan)
                                             for m in morceaux]) if morceaux else np.zeros(0),
                        groupes=np.array([json.dumps(m[cle]) for m in morceaux]))
    return f


def preparer() -> dict:
    """Les surfaces, leurs points et leurs normales, et les morceaux qu'elles liront ; rien n'est lu du scan."""
    t0 = time.monotonic()
    plan297 = json.loads(CE_QUE_297_A_PREPARE.read_text())
    se_redonne = bool((plan297.get("la_chaine_redonne_248") or {}).get("tous")
                      and plan297.get("le_premier_saut_est_la_spire_produite"))
    paris = les_surfaces_de_paris4()
    prix, sur_0358 = la_surface_de_0358()
    plan = {"la_chaine_de_297_se_redonne": se_redonne, "PHerc0358": sur_0358, "les_surfaces": {}, "les_morceaux": {}}
    for volume, surfaces, cle in (("PHercParis4", paris, "le_bloc"), ("PHerc0358", prix, "la_piece")):
        v = LES_VOLUMES[volume]
        vol = LesMorceaux(volume, v["url"], v["niveau"])
        T = la_demi_fenetre(volume)
        tous = set()
        for nom, morceaux in surfaces.items():
            f = ranger(f"{volume}__{nom}", morceaux, cle)
            n = sum(len(m["points"]) for m in morceaux)
            if n:
                pts = np.concatenate([m["points"] for m in morceaux])
                nrm = np.concatenate([m["normales"] for m in morceaux])
                coords = les_coordonnees(pts, nrm, v["facteur"], T)
                dedans = dans_le_volume(coords, vol.forme)
                tous |= les_morceaux_complets(coords[dedans], vol.taille)
            plan["les_surfaces"][f"{volume}__{nom}"] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": n,
                                                          "les_groupes": len(morceaux)}
        cles = sorted(tous)
        (LE_DOSSIER / f"morceaux_{volume}.json").write_text(json.dumps(cles))
        plan["les_morceaux"][volume] = {"le_niveau": v["niveau"], "combien": len(cles),
                                        "les_octets": int(len(cles) * np.prod(vol.taille)), "la_demi_fenetre": T}
    plan["les_secondes"] = round(time.monotonic() - t0, 1)
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire(ouvriers: int = 8) -> dict:
    """Range sur disque les morceaux que le plan demande ; ce qui est déjà là n'est pas retiré."""
    out = {}
    for volume, v in LES_VOLUMES.items():
        t0 = time.monotonic()
        cles = [tuple(c) for c in json.loads((LE_DOSSIER / f"morceaux_{volume}.json").read_text())]
        vol = LesMorceaux(volume, v["url"], v["niveau"])
        comptes = {"deja": 0, "tire": 0, "absent": 0}
        with ThreadPoolExecutor(ouvriers) as ex:
            for i, r in enumerate(ex.map(lambda c: vol.tirer(*c), cles)):
                comptes[r] += 1
                if (i + 1) % 500 == 0:
                    print(f"{volume} : {i + 1}/{len(cles)} {comptes}", flush=True)
        dt = time.monotonic() - t0
        out[volume] = dict(comptes, combien=len(cles), les_secondes=round(dt, 1),
                           le_debit_mo_s=round(comptes["tire"] * np.prod(vol.taille) / 1e6 / max(dt, 1e-9), 1))
        print(json.dumps({volume: out[volume]}), flush=True)
    return out


def juger_une_surface(vol: LesMorceaux, fichier: Path, facteur: float, T: int) -> dict:
    z = np.load(fichier)
    pts, nrm, groupe, juge = z["points"], z["normales"], z["groupe"], z["juge"]
    groupes = [json.loads(g) for g in z["groupes"]]
    if len(pts) == 0:
        return {"reunis": noter(np.zeros((0, 2 * T + 1)), np.zeros(0, dtype=bool)), "groupes": [], "juge": juge,
                "q": np.zeros(0), "profils": np.zeros((0, 2 * T + 1))}
    coords = les_coordonnees(pts, nrm, facteur, T)
    dedans = dans_le_volume(coords, vol.forme)
    profils = np.zeros((len(pts), 2 * T + 1), dtype=np.float32)
    if dedans.any():
        profils[dedans] = les_profils(vol, coords[dedans])
    reunis = noter(profils, dedans)
    par_groupe = []
    for i, g in enumerate(groupes):
        m = groupe == i
        par_groupe.append(dict(public(noter(profils[m], dedans[m])), le_groupe=g))
    q_plein = np.full(len(pts), np.nan)
    q_plein[reunis["_juge"]] = reunis["_q"]
    return {"reunis": reunis, "groupes": par_groupe, "juge": juge, "q": q_plein, "profils": profils}


def la_note_par_juge(q: np.ndarray, juge: np.ndarray) -> dict:
    """La note là où le juge de 248 dit juste, raté, ou ne dit rien."""
    out = {}
    for nom, m in (("juste", juge == 1.0), ("rate", juge == 0.0), ("non_note", ~np.isfinite(juge))):
        m = m & np.isfinite(q)
        out[nom] = {"la_note": round(float(q[m].mean()), 4) if m.any() else None, "les_points": int(m.sum())}
    return out


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(LE_PLAN.read_text())
    d = {"la_question": __doc__.splitlines()[0], "la_chaine_de_297_se_redonne": plan["la_chaine_de_297_se_redonne"],
         "les_constantes": {"la_fenetre_um": LA_FENETRE_UM, "les_volumes": LES_VOLUMES,
                            "le_surechantillonnage": LE_SURECHANTILLONNAGE, "la_piece_en_mailles": LA_PIECE_EN_MAILLES,
                            "le_minimum_de_points_par_piece": LE_MINIMUM_DE_POINTS_PAR_PIECE,
                            "les_pentes": LES_PENTES, "lamplitude_en_pas": LAMPLITUDE_EN_PAS},
         "le_plan": {k: plan[k] for k in ("les_morceaux", "PHerc0358")},
         "les_morceaux_sur_disque": {v: les_morceaux_absents(v, json.loads((LE_DOSSIER / f"morceaux_{v}.json").read_text()))
                                     for v in LES_VOLUMES}}
    resultats = {}
    for volume in LES_VOLUMES:
        v = LES_VOLUMES[volume]
        vol = LesMorceaux(volume, v["url"], v["niveau"])
        T = la_demi_fenetre(volume)
        for cle, info in plan["les_surfaces"].items():
            if not cle.startswith(volume + "__"):
                continue
            resultats[cle] = juger_une_surface(vol, RACINE / info["le_fichier"], v["facteur"], T)
            print(f"{cle} : {resultats[cle]['reunis']['la_note']} sur {resultats[cle]['reunis']['les_points_juges']} "
                  f"points ({time.monotonic() - t0:.0f} s)", flush=True)
    P = "PHercParis4__"
    noms_p = ["le_segment", "saut_1", "saut_2", "saut_3", "saut_4", *LES_DEFAUTS]
    reunis = {n: resultats[P + n]["reunis"]["la_note"] for n in noms_p}
    blocs = []
    for i, g in enumerate(resultats[P + "le_segment"]["groupes"]):
        blocs.append({"le_bloc": g["le_groupe"],
                      **{n: resultats[P + n]["groupes"][i]["la_note"] for n in noms_p},
                      "les_points_juges": {n: resultats[P + n]["groupes"][i]["les_points_juges"] for n in noms_p}})
    e = {"les_blocs": blocs, "reunis": reunis,
         "les_details": {n: public(resultats[P + n]["reunis"]) for n in noms_p},
         "sous_le_juge_de_248": {n: la_note_par_juge(resultats[P + n]["q"], resultats[P + n]["juge"])
                                 for n in ("saut_1", "saut_2", "saut_3", "saut_4")},
         "le_pas_montre_um": {n: le_pas_montre(resultats[P + n]["reunis"]["le_profil_moyen"],
                                               LES_VOLUMES["PHercParis4"]["le_voxel_um"]) for n in noms_p}}
    e["le_verdict"] = letalonnage_separe(blocs, reunis)
    d["letalonnage"] = e
    Q = "PHerc0358__"
    noms_q = ["la_surface_de_24", *LES_DEFAUTS]
    tau = e["le_verdict"]["le_seuil"]
    pieces = []
    for i, g in enumerate(resultats[Q + "la_surface_de_24"]["groupes"]):
        dec = resultats[Q + "decale_dun_demi_pas"]["groupes"]
        dec_i = next((x for x in dec if x["le_groupe"] == g["le_groupe"]), None)
        note_dec = dec_i["la_note"] if dec_i else None
        pieces.append({"la_piece_en_mailles": g["le_groupe"], "la_note": g["la_note"],
                       "les_points_juges": g["les_points_juges"], "la_note_decalee": note_dec,
                       "la_piece": la_piece(g["la_note"], note_dec, g["les_points_juges"], tau) if tau else "non jugée"})
    r = {"reunis": {n: resultats[Q + n]["reunis"]["la_note"] for n in noms_q},
         "les_details": {n: public(resultats[Q + n]["reunis"]) for n in noms_q},
         "les_pieces": pieces,
         "le_pas_montre_um": {n: le_pas_montre(resultats[Q + n]["reunis"]["le_profil_moyen"],
                                               LES_VOLUMES["PHerc0358"]["le_voxel_um"]) for n in noms_q},
         "les_croisements_de_24": les_croisements_par_piece(pieces)}
    d["le_rouleau"] = r
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    figure_path = LE_DOSSIER / "pour_la_figure.npz"
    q24 = resultats[Q + "la_surface_de_24"]
    np.savez_compressed(figure_path, q_0358=q24["q"], groupe_0358=np.load(RACINE / plan["les_surfaces"][
        Q + "la_surface_de_24"]["le_fichier"])["groupe"])
    d["pour_la_figure"] = str(figure_path.relative_to(RACINE))
    return d


def les_croisements_par_piece(pieces: list[dict]) -> dict:
    """Où tombent les contacts transverses de `24`, par pièce, et la note des pièces qui en portent."""
    try:
        s = json.loads(LES_CROISEMENTS_DE_24.read_text())
    except (OSError, ValueError) as exc:
        return {"lisible": False, "raison": str(exc)}
    compte = {}
    total = 0
    for c in s.get("census", []):
        for t in c.get("transverse_contacts", []):
            for q in (t["quad1"], t["quad2"]):
                cle = (q[0] // LA_PIECE_EN_MAILLES * LA_PIECE_EN_MAILLES, q[1] // LA_PIECE_EN_MAILLES * LA_PIECE_EN_MAILLES)
                compte[cle] = compte.get(cle, 0) + 1
                total += 1
    avec = [p for p in pieces if tuple(p["la_piece_en_mailles"]) in compte]
    return {"lisible": True, "les_extremites_de_contacts": total, "les_pieces_touchees": len(compte),
            "leurs_verdicts": {v: sum(1 for p in avec if p["la_piece"] == v) for v in
                               ("posée sur une feuille", "en travers", "entre les feuilles", "non jugée")},
            "par_piece": {f"{a}_{b}": n for (a, b), n in sorted(compte.items())}}


# ── La batterie ────────────────────────────────────────────────────────────────────────────────────────────────────

def _feuillets(forme, pas: float, axe: int, epaisseur: float, bruit: float = 0.0, graine: int = 0) -> np.ndarray:
    """Un empilement synthétique : des feuilles denses, de pas `pas`, perpendiculaires à l'axe `axe` du tableau."""
    idx = np.arange(forme[axe], dtype=float)
    phase = (idx % pas) / pas
    prof = 60.0 + 150.0 * np.exp(-0.5 * ((np.minimum(phase, 1 - phase) * pas) / epaisseur) ** 2)
    sh = [1, 1, 1]
    sh[axe] = forme[axe]
    v = np.broadcast_to(prof.reshape(sh), forme).astype(float)
    if bruit:
        v = v + np.random.default_rng(graine).normal(0, bruit, forme)
    return np.clip(v, 0, 255).astype(np.uint8)


def _source_de(volume: np.ndarray, taille: int):
    """Un volume en mémoire servi par morceaux, comme S3 ; les morceaux hors du volume sont absents."""
    forme = volume.shape

    def source(cz, cy, cx):
        z0, y0, x0 = cz * taille, cy * taille, cx * taille
        if z0 >= forme[0] or y0 >= forme[1] or x0 >= forme[2] or min(cz, cy, cx) < 0:
            return None, "absent"
        m = np.zeros((taille,) * 3, dtype=np.uint8)
        b = volume[z0:z0 + taille, y0:y0 + taille, x0:x0 + taille]
        m[:b.shape[0], :b.shape[1], :b.shape[2]] = b
        return m.tobytes(), None
    return source


def verifier() -> int:
    import tempfile

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    from la_spire_voisine_est_elle_a_un_pas import les_normales

    tmp = Path(tempfile.mkdtemp())
    pas, taille = 18.0, 16

    def juger(volume, pts, nrm, facteur=1.0, T=21, nom=None):
        """Un volume en mémoire, rangé sous son propre nom : deux volumes d'essai ne partagent jamais leurs morceaux."""
        meta = {"shape": list(volume.shape), "chunks": [taille] * 3, "fill_value": 0, "compressor": None}
        vol = LesMorceaux(nom, None, 0, meta=meta, source=_source_de(volume, taille), dossier=tmp)
        coords = les_coordonnees(pts, nrm, facteur, T)
        dedans = dans_le_volume(coords, vol.forme)
        for c in les_morceaux_complets(coords[dedans], vol.taille):
            vol.tirer(*c)
        profils = np.zeros((len(pts), 2 * T + 1), dtype=np.float32)
        if dedans.any():
            profils[dedans] = les_profils(vol, coords[dedans])
        return noter(profils, dedans), profils, vol

    def plan_z(z, n=12, x0=40.0, y0=40.0, espace=6.0):
        """Une grille plane à hauteur z : points (n, n, 3) en (x, y, z)."""
        g = np.zeros((n, n, 3))
        for i in range(n):
            for j in range(n):
                g[i, j] = (x0 + j * espace, y0 + i * espace, z)
        return g

    # Un empilement de feuilles perpendiculaires à z (l'axe 0 du tableau), de pas 18.
    V = _feuillets((160, 140, 140), pas, 0, 3.0, bruit=4.0)
    pic, creux = 4 * pas, 4 * pas + pas / 2
    g = plan_z(pic)
    ok = np.ones(g.shape[:2], dtype=bool)
    n, nok = les_normales(g, ok)
    m = ok & nok
    sur, _, _ = juger(V, g[m], n[m], nom="z")
    v("★★★★ une surface posée sur ses feuilles a une note proche de 1",
      lambda: sur["la_note"] > 0.9, str(sur["la_note"]))
    ent, _, _ = juger(V, plan_z(creux)[m], n[m], nom="z")
    v("★★★★ une surface entre deux feuilles a une note bien sous le hasard",
      lambda: ent["la_note"] < 0.25, str(ent["la_note"]))

    # Une rampe : la même surface, décalée en dents de scie le long des colonnes, normales recalculées.
    G = plan_z(pic, n=48, espace=2.0)
    OK = np.ones(G.shape[:2], dtype=bool)
    N, NOK = les_normales(G, OK)
    defauts = les_defauts(G, OK, N, NOK, pas / 2.0, pas, 2.0)
    for nom in LES_PENTES:
        dp, dok = defauts[nom]
        dn, dnok = les_normales(dp, dok)
        mm = dok & dnok
        r, _, _ = juger(V, dp[mm], dn[mm], nom="z")
        v(f"★★★★ la {nom} a une note proche du hasard", abs(r["la_note"] - 0.5) < 0.12, str(r["la_note"]))
    dp, dok = defauts["decale_dun_demi_pas"]
    mm = dok & NOK
    r, _, _ = juger(V, dp[mm], N[mm], nom="z")
    v("★★★★ le décalé d'un demi-pas tombe entre les feuilles, bien sous le hasard",
      lambda: r["la_note"] < 0.25, str(r["la_note"]))
    x = np.linspace(0, 400, 4001)
    d = la_dent_de_scie(x, 0.25, 36.0)
    v("★★★ la dent de scie va de 0 à son amplitude, à la pente déclarée",
      abs(d.min()) < 1e-9 and abs(d.max() - 36.0) < 0.1 and abs(np.abs(np.diff(d) / np.diff(x)).max() - 0.25) < 1e-6)

    # L'ordre des axes : des feuilles perpendiculaires à x (l'axe 2 du tableau) ; une surface plane x = pic.
    Vx = _feuillets((140, 140, 160), pas, 2, 3.0, bruit=4.0)
    gx = np.zeros((12, 12, 3))
    for i in range(12):
        for j in range(12):
            gx[i, j] = (pic, 40.0 + j * 6, 40.0 + i * 6)
    nx, nxok = les_normales(gx, ok)
    rx, _, _ = juger(Vx, gx[m], nx[m], nom="x")
    v("★★★★ l'ordre (z, y, x) du tableau : une feuille perpendiculaire à x se lit sur x", lambda: rx["la_note"] > 0.9,
      str(rx["la_note"]))
    rz, _, _ = juger(V, gx[m], nx[m], nom="z")
    v("★★★ la même surface dans un empilement perpendiculaire à z n'a pas de feuille à sa place",
      abs(rz["la_note"] - 0.5) < 0.2 or rz["les_points_juges"] == 0, str(rz["la_note"]))

    # Le niveau : des points au niveau 0, un volume au niveau 2 (facteur 4).
    r4, _, _ = juger(V, g[m] * 4.0, n[m], facteur=4.0, nom="z")
    v("★★★★ des points du niveau 0 se lisent au niveau 2, divisés par 4",
      lambda: r4["la_note"] > 0.9, str(r4["la_note"]))
    r1, _, _ = juger(V, g[m] * 4.0, n[m], facteur=1.0, nom="z")
    v("★★★ lus sans le facteur, ils sortent du volume", r1["les_points_juges"] == 0, str(r1["les_points_juges"]))

    # La note : rang au centre, ex æquo pour moitié.
    prof = np.array([[1, 2, 3, 9, 3, 2, 1], [9, 8, 7, 0, 7, 8, 9], [5, 5, 5, 5, 5, 5, 5], [1, 5, 1, 5, 1, 5, 1]],
                    dtype=float)
    q = le_rang_au_centre(prof)
    v("★★★★ le rang au centre : 1 au plus dense, 0 au plus creux, 1/2 pour un profil plat, ex æquo pour moitié",
      np.allclose(q, [1.0, 0.0, 0.5, 5.0 / 6.0]), str(q))
    rng = np.random.default_rng(3)
    phases = rng.uniform(0, 1, 20000)
    t = np.arange(-21, 22)
    aleat = np.cos(2 * np.pi * (t[None, :] / 18.0 + phases[:, None])) + 0.3 * np.cos(4 * np.pi * (t[None, :] / 18.0
                                                                                                + phases[:, None]))
    v("★★★★ au hasard de la phase, la note vaut 1/2", abs(le_rang_au_centre(aleat).mean() - 0.5) < 0.01,
      str(le_rang_au_centre(aleat).mean()))
    vide = noter(np.full((5, 43), 7.0, dtype=np.float32), np.ones(5, dtype=bool))
    v("★★★ un profil sans matière est écarté et compté", vide["sans_matiere"] == 5 and vide["la_note"] is None)
    hors = noter(np.zeros((3, 43), dtype=np.float32), np.array([True, False, False]))
    v("★★★ un point hors du volume est écarté et compté", hors["hors_du_volume"] == 2)

    # Le profil moyen montre le pas.
    _, profs, _ = juger(V, g[m], n[m], nom="z")
    pm = le_profil_moyen(profs)
    v("★★★ le profil moyen d'une surface sur ses feuilles montre le pas", le_pas_montre(pm, 1.0) == pas,
      str(le_pas_montre(pm, 1.0)))
    v("★★ un profil moyen plat ne montre aucun pas", le_pas_montre([0.0] * 43, 1.0) is None)
    rl = le_relief([0.0, -1.0, 0.5, 2.0, 0.0])
    v("★★★ le relief du profil moyen : amplitude, plus dense et plus creux comptés depuis le point",
      rl == {"lamplitude": 3.0, "le_plus_dense": 1, "le_plus_creux": -1, "au_point": 0.5}, str(rl))

    # Le suréchantillonnage.
    pl = plan_z(10.0, n=5, espace=10.0)
    okp = np.ones((5, 5), dtype=bool)
    okp[0, 0] = False
    s, sok = surechantillonner(pl, okp, 4)
    v("★★★ le suréchantillonnage d'un plan reste sur le plan, au pas divisé",
      s.shape == (17, 17, 3) and np.allclose(s[sok][:, 2], 10.0) and np.allclose(s[4, 4, :2], [50.0, 50.0]))
    v("★★★ un point dont une maille a un coin invalide n'est pas valide", not sok[0:4, 0:4].any() and sok[5, 5])

    # Les morceaux : l'interpolation lit le voisin du dessus ; un morceau absent vaut le remplissage ; un transport qui
    # échoue lève.
    c = np.array([[[15.5, 3.0, 3.0]]])
    mc = les_morceaux_complets(c, (16, 16, 16))
    v("★★★ un échantillon à la frontière d'un morceau lit aussi le suivant", (0, 0, 0) in mc and (1, 0, 0) in mc)
    meta = {"shape": [20, 20, 20], "chunks": [16] * 3, "fill_value": 0, "compressor": None}
    vv = LesMorceaux("abs", None, 0, meta=meta, source=lambda *a: (None, "absent"), dossier=tmp)
    v("★★★ un morceau absent de la source vaut le remplissage", vv.tirer(0, 0, 0) == "absent"
      and int(vv.morceau(0, 0, 0).max()) == 0)
    vd = LesMorceaux("voisin", None, 0, meta=meta, source=lambda cz, cy, cx: ((None, "absent") if cx == 0 else
                                                                            (bytes([7]) * 16 ** 3, None)), dossier=tmp)
    v("★★★★ un morceau absent ne rend pas absents ses voisins de même préfixe",
      vd.tirer(0, 0, 0) == "absent" and vd.tirer(0, 0, 1) == "tire" and int(vd.morceau(0, 0, 1).min()) == 7)
    ve = LesMorceaux("err", None, 0, meta=meta, source=lambda *a: (None, "delai depasse"), dossier=tmp)
    try:
        ve.tirer(0, 0, 0)
        leve = False
    except RuntimeError:
        leve = True
    v("★★★★ un transport qui échoue lève, il ne se lit pas comme du vide", leve)
    vp = LesMorceaux("pastire", None, 0, meta=meta, source=lambda *a: (None, "absent"), dossier=tmp)
    try:
        vp.morceau(1, 1, 1)
        leve = False
    except RuntimeError:
        leve = True
    v("★★★ un morceau jamais tiré lève au lieu de se lire comme du vide", leve)
    V2 = (np.arange(40 ** 3) % 251).astype(np.uint8).reshape(40, 40, 40)
    vb = LesMorceaux("boite", None, 0, meta={"shape": [40] * 3, "chunks": [16] * 3, "fill_value": 0,
                                              "compressor": None}, source=_source_de(V2, 16), dossier=tmp)
    for cz in range(3):
        for cy in range(3):
            for cx in range(3):
                vb.tirer(cz, cy, cx)
    v("★★★★ une boîte assemblée de morceaux est le volume, voxel pour voxel",
      np.array_equal(vb.la_boite(np.array([5, 13, 30]), np.array([35, 33, 39])), V2[5:36, 13:34, 30:40]))

    vm = LesMorceaux("manque", None, 0, meta={"shape": [40] * 3, "chunks": [16] * 3, "fill_value": 0,
                                               "compressor": None}, source=_source_de(V2, 16), dossier=tmp)
    vm.tirer(0, 0, 0)
    cm = les_coordonnees(np.array([[8.0, 8.0, 8.0]]), np.array([[0.0, 0.0, 1.0]]), 1.0, 12)
    try:
        les_profils(vm, cm)
        leve = False
    except RuntimeError:
        leve = True
    v("★★★★ un profil qui lit un morceau jamais tiré lève, il ne se lit pas comme du vide", leve)

    # Les issues.
    bl = {"le_bloc": [1, 2], "le_segment": 0.8, "rampe_douce": 0.5, "rampe_raide": 0.52, "decale_dun_demi_pas": 0.2}
    re = {"le_segment": 0.8, "rampe_douce": 0.5, "rampe_raide": 0.52}
    v("★★★★ l'étalonnage sépare quand chaque bloc ordonne et que les rampes réunies sont sous τ",
      letalonnage_separe([bl, dict(bl, le_bloc=[3, 4])], re)["separe"] and le_seuil(0.8) == 0.65)
    for casse, nom in ((dict(bl, rampe_douce=0.81), "une rampe dépasse le segment"),
                       (dict(bl, decale_dun_demi_pas=0.55), "le décalé est au-dessus du hasard"),
                       (dict(bl, le_segment=0.49, rampe_douce=0.4, rampe_raide=0.4), "le segment est sous le hasard")):
        v(f"★★★★ l'étalonnage ne sépare pas si, dans un seul bloc, {nom}",
          not letalonnage_separe([bl, casse], re)["separe"])
    v("★★★ l'étalonnage ne sépare pas si les rampes réunies atteignent τ",
      not letalonnage_separe([bl], dict(re, rampe_raide=0.66))["separe"])
    v("★★★ une pièce haute dont le décalé ne tombe pas sous 1/2 n'est pas posée sur une feuille",
      la_piece(0.8, 0.6, 500, 0.65) == "en travers" and la_piece(0.8, 0.3, 500, 0.65) == "posée sur une feuille")
    v("★★★ une pièce basse est entre les feuilles, une pièce moyenne en travers, une pièce maigre non jugée",
      la_piece(0.3, 0.7, 500, 0.65) == "entre les feuilles" and la_piece(0.55, 0.4, 500, 0.65) == "en travers"
      and la_piece(0.9, 0.1, 50, 0.65) == "non jugée")
    base = {"la_chaine_de_297_se_redonne": True,
            "letalonnage": {"le_verdict": {"separe": True, "le_seuil": 0.65}},
            "le_rouleau": {"reunis": {"rampe_douce": 0.5, "rampe_raide": 0.52},
                           "les_pieces": [{"la_piece": "posée sur une feuille", "les_points_juges": 300},
                                          {"la_piece": "en travers", "les_points_juges": 100},
                                          {"la_piece": "non jugée", "les_points_juges": 50}]}}
    vd = le_verdict(base)
    v("★★★★ l'issue : la part des points jugés dans des pièces posées sur une feuille, sans les pièces non jugées",
      vd["decidable"] and vd["la_part_posee"] == 0.75, str(vd))
    b2 = json.loads(json.dumps(base))
    b2["le_rouleau"]["reunis"]["rampe_raide"] = 0.7
    v("★★★★ l'issue : indécidable si une rampe plantée sur le rouleau atteint τ", not le_verdict(b2)["decidable"]
      and "ne se transporte pas" in le_verdict(b2)["lissue"])
    b3 = json.loads(json.dumps(base))
    b3["letalonnage"]["le_verdict"]["separe"] = False
    v("★★★★ l'issue : le juge qui ne sépare pas au pas du prix ne juge pas le rouleau",
      le_verdict(b3)["separe"] is False and "ne sépare pas" in le_verdict(b3)["lissue"])
    b4 = dict(base, la_chaine_de_297_se_redonne=False)
    v("★★★ l'issue : indécidable si la chaîne ne se redonne pas", not le_verdict(b4)["decidable"])

    # Le juge de 248, par juste et raté.
    qn = np.array([0.9, 0.8, 0.2, np.nan, 0.6])
    jn = np.array([1.0, 1.0, 0.0, 0.0, np.nan])
    pj = la_note_par_juge(qn, jn)
    v("★★★ la note sous le juge de 248 : juste, raté, non noté, sans les points non jugés",
      pj["juste"]["la_note"] == 0.85 and pj["rate"]["les_points"] == 1 and pj["non_note"]["la_note"] == 0.6)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--preparer", action="store_true", help="les surfaces et les morceaux qu'elles liront, sans rien lire")
    p.add_argument("--lire", type=int, default=None, metavar="OUVRIERS", help="range les morceaux sur disque")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.preparer:
        print(json.dumps(preparer(), ensure_ascii=False, indent=1))
        return 0
    if a.lire is not None:
        print(json.dumps(lire(a.lire), ensure_ascii=False, indent=1))
        return 0
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(texte)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
