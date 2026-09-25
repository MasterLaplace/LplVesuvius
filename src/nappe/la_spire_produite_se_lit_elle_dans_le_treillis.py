"""La spire voisine que la chaîne produit, rendue comme le segment l'est, se lit-elle dans le treillis ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL PAS NE SOIT LU SUR UNE PILE PRODUITE. Ce qui était vu avant d'écrire, et qui
est dit : un rendu d'essai de 256 × 256 pixels de `20230702185753` par `vc_render_tifxyz` égalait la pile publiée au même
endroit en 0,99 des voxels, **à l'ordre des couches près** (sans `--flip-normals`, la pile rendue est la publiée
retournée) ; et le compte des ratés du transfert par bloc, qui a fixé la règle du bloc ci-dessous.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P92`. La couverture par boucles juge un segment sans humain (`256`), mais elle
lit le volume de surface que le segment PUBLIE. La spire voisine que produit la chaîne (`247`, `248`) n'a pas de volume
publié : tant qu'elle n'en a pas, rien de ce que le treillis sait faire ne peut la juger. Cette tranche lui en donne un,
avec l'outil qui a rendu le volume publié, et demande si la marche du treillis voit, sur cette pile, là où le transfert a
raté.

## Ce qui est rendu, et le contrôle qui en fait un instrument

1. LE CONTRÔLE : un carré de 2 × 2 chunks de `20230702185753`, rendu depuis le scan brut par `vc_render_tifxyz`, avec
   `--flip-normals`, 109 couches au pas d'un voxel, comparé à la pile publiée au même endroit. Il doit l'égaler.
2. LE BLOC, sans choix : parmi les blocs de 16 × 16 chunks alignés sur 16, entièrement dans l'empreinte et où la surface
   produite existe à chaque point de la maille, celui qui porte le plus de ratés du transfert, comptés là où les deux
   juges de `247` (le segment seul, et le segment avec ses témoins) s'accordent à moins d'un demi-feuillet.
3. TROIS PILES SUR CE BLOC : la publiée ; le segment réduit à la maille de la chaîne (un point sur huit), rendu de même,
   pour mesurer ce que la maille coûte à elle seule ; et la spire produite (`m7`, côté plus, la feuille suivante puis le
   vote de `247`), sur la même maille.

## Ce qui se lit

Sur chaque pile, les pas de toutes les coutures du bloc, par le lecteur de `224`, sans retouche. Puis LA MARCHE DU BLOC :
la profondeur de la feuille en chaque chunk, par moindres carrés sur les pas (chaque pas dit la différence entre deux
chunks voisins), à une constante près.

## Ce qui se mesure

⭐⭐⭐ L'ACCORD DES PAIRES, qui n'a besoin d'aucune ancre. Deux chunks où le juge note le transfert sont SUR LA MÊME SPIRE
pour le juge si leurs erreurs diffèrent de moins d'un demi-feuillet, et pour la marche si leurs profondeurs diffèrent de
moins d'un demi-feuillet. Sur les paires que le juge sépare, la part que la marche sépare ; sur celles qu'il réunit, la
part qu'elle réunit. Une marche plate réunit tout, et c'est le témoin : elle ne sépare rien.

## Les issues, exclusives

- le rendu n'égale pas la pile publiée : rien de ce qui suit n'est un instrument ;
- la pile produite ne se lit pas (ses coutures sont refusées) : le treillis ne voit pas la spire produite ;
- la marche ne sépare pas mieux que le témoin : le treillis lit la spire produite sans y voir les ratés ;
- elle sépare : le treillis peut juger une spire que la chaîne a produite.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut la marche sur un autre bloc, ni une boucle de la couverture, ni l'autre
côté, ni `ps256`. ⚠ Le juge a ses propres fautes : là où il se trompe, un désaccord ne dit pas qui a tort.

Usage :
    uv run python src/nappe/la_spire_produite_se_lit_elle_dans_le_treillis.py --verifier
    uv run python src/nappe/la_spire_produite_se_lit_elle_dans_le_treillis.py \\
        --json docs/mesures/la_spire_produite_se_lit_elle_dans_le_treillis.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from deux_chemins_arrivent_ils_sur_la_meme_spire import lire_une_bande  # noqa: E402
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT, PAS_EN_VOXELS,  # noqa: E402
                                                lire_tifxyz, les_normales, telecharger)
from ou_le_maillage_quitte_t_il_son_feuillet import le_segment_declare, un_chunk  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

LE_VOLUME_BRUT = f"{BUCKET}/PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr"
LE_DOSSIER = RACINE / "data" / "rendu_spire_voisine"
LA_MAILLE = 8
LE_COTE_DU_CHUNK = 128
LES_COUCHES = 109
LE_BLOC = 16
LE_CONTROLE = (196, 144, 2)   # rangée et colonne du premier chunk, côté en chunks
LA_PREDICTION, LE_COTE = "m7", "du_cote_plus"
LES_JUGES = ("le_segment_seul", "le_segment_et_ses_temoins")
LA_PATIENCE = 900
LE_TEMOIN_DE_FIN = ".rendu_complet"
LE_PAS_DE_COUPE = 8
LA_RAMPE_EN_CHUNKS = 4   # la largeur de la transition posée par le contrôle positif
LE_DOSSIER_DE_LA_RAMPE = "la_rampe_des_rangees"
DELAI = 120.0


# ── LES MAILLAGES ──────────────────────────────────────────────────────────────────────────────────────────────

def le_maillage_reduit(ref: np.ndarray, valide: np.ndarray, maille: int = LA_MAILLE) -> tuple[np.ndarray, np.ndarray]:
    """Le segment, un point sur `maille` : ce que la chaîne voit de lui, et `-1` hors de lui."""
    r, v = ref[::maille, ::maille], valide[::maille, ::maille]
    return np.where(v[..., None], r, -1.0), v


def le_maillage_produit(ref: np.ndarray, valide: np.ndarray, tau: np.ndarray,
                        maille: int = LA_MAILLE) -> tuple[np.ndarray, np.ndarray]:
    """La spire produite : chaque point de la maille poussé de `tau` voxels le long de la normale du segment.

    ⚠ C'est exactement le premier saut de `248`, qui égale `247` : la normale est celle du segment, pas recalculée.
    Là où la normale ou `tau` manque, le point est `-1`, comme le format le veut.
    """
    n, ok = les_normales(ref, valide)
    r, n8, ok8 = ref[::maille, ::maille], n[::maille, ::maille], ok[::maille, ::maille]
    if tau.shape != ok8.shape:
        raise ValueError(f"la carte du transfert fait {tau.shape}, la maille {ok8.shape}")
    bon = ok8 & np.isfinite(tau)
    q = r + np.where(bon, tau, 0.0)[..., None] * n8
    return np.where(bon[..., None], q, -1.0), bon


def ecrire_tifxyz(dossier: Path, points: np.ndarray, valide: np.ndarray, scale: float, nom: str) -> Path:
    """Un dossier tifxyz : trois grilles float32 et le meta que `vc_render_tifxyz` lit."""
    import tifffile

    dossier.mkdir(parents=True, exist_ok=True)
    for a, c in enumerate("xyz"):
        tifffile.imwrite(dossier / f"{c}.tif", points[..., a].astype(np.float32))
    p = points[valide]
    meta = {"bbox": [p.min(axis=0).tolist(), p.max(axis=0).tolist()], "format": "tifxyz",
            "scale": [float(scale), float(scale)], "type": "seg", "uuid": nom}
    (dossier / "meta.json").write_text(json.dumps(meta, indent=2))
    return dossier


# ── LE RENDU ───────────────────────────────────────────────────────────────────────────────────────────────────

def le_cadre(cy: int, cx: int, cote: int, chunk: int = LE_COTE_DU_CHUNK) -> dict:
    """Le cadre en pixels du volume de surface qui couvre `cote` × `cote` chunks à partir du chunk (cy, cx)."""
    return {"x": int(cx) * chunk, "y": int(cy) * chunk, "largeur": int(cote) * chunk, "hauteur": int(cote) * chunk}


def la_commande_de_rendu(tifxyz: Path, sortie: Path, cadre: dict, couches: int = LES_COUCHES,
                         miroir: Path | None = None) -> list[str]:
    """La commande qui rend une pile comme la publiée : 109 couches au pas d'un voxel, normales retournées.

    ⚠ Avec `miroir`, le volume est lu dans ce dossier local et nulle part ailleurs (`le_miroir_du_volume`) : sans l'adresse
    distante, un chunk que le miroir n'a pas se lit comme du vide, jamais comme un téléchargement caché.
    """
    source = ["-v", str(miroir)] if miroir is not None else ["-v", str(LE_DOSSIER / "cache"), "--remote-url", LE_VOLUME_BRUT]
    return [*source, "--scale", "1", "-g", "0",
            "-s", str(tifxyz), "--tif-output", str(sortie), "-n", str(int(couches)), "--slice-step", "1",
            "--flip-normals", "--crop-x", str(cadre["x"]), "--crop-y", str(cadre["y"]),
            "--crop-width", str(cadre["largeur"]), "--crop-height", str(cadre["hauteur"])]


def la_pile_est_complete(sortie: Path) -> bool:
    """Une pile se reprend quand le rendu qui l'a écrite est allé au bout : ses 109 couches ET le témoin de fin.

    ⚠⚠ Compter les couches ne suffit pas. `vc_render_tifxyz` crée ses 109 fichiers dès le début puis les remplit bande par
    bande : le 2026-09-25, une pile avait ses 109 fichiers à 18 % de son rendu. Une pile coupée en route, machine éteinte ou
    réseau perdu, passait donc pour complète, et la mesure suivante aurait lu une pile en partie vide sans rien en dire.
    """
    return (sortie / LE_TEMOIN_DE_FIN).is_file() and len(list(sortie.glob("*.tif"))) == LES_COUCHES


def rendre(tifxyz: Path, sortie: Path, cadre: dict, patience: int = LA_PATIENCE, lancer=subprocess.run,
           miroir: Path | None = None) -> dict:
    """La pile, par le chien de garde du dépôt ; une pile complète n'est pas refaite.

    ⚠ Le témoin de fin n'est écrit qu'après un rendu qui a rendu zéro ET ses 109 couches, et il est retiré AVANT de relancer :
    un témoin resté d'un rendu précédent ferait passer pour complète la pile qu'un nouveau rendu interrompu laisse derrière lui.
    `lancer` n'est remplacé que par la batterie, pour exercer ce chemin sans télécharger une pile.
    """
    if la_pile_est_complete(sortie):
        return {"rendue": True, "reprise": True}
    (sortie / LE_TEMOIN_DE_FIN).unlink(missing_ok=True)
    ecartee = mettre_de_cote(sortie)
    debut = time.monotonic()
    cmd = [str(RACINE / "src" / "outils" / "rendre_surveille.sh"), str(sortie), str(int(patience)), "--",
           *la_commande_de_rendu(tifxyz, sortie, cadre, miroir=miroir)]
    sortie.parent.mkdir(parents=True, exist_ok=True)
    journal = sortie.with_suffix(".log")
    with journal.open("w") as fh:
        rc = lancer(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=RACINE).returncode
    n = len(list(sortie.glob("*.tif"))) if sortie.is_dir() else 0
    ok = rc == 0 and n == LES_COUCHES
    if ok:
        (sortie / LE_TEMOIN_DE_FIN).write_text(f"code {rc}, {n} couches\n")
    return {"rendue": ok, "reprise": False, "le_code": rc, "les_couches": n,
            "les_secondes": round(time.monotonic() - debut, 1), **({"mise_de_cote": str(ecartee)} if ecartee else {})}


def mettre_de_cote(sortie: Path) -> Path | None:
    """Une pile inachevée, déplacée avant qu'un rendu ne la refasse ; rien n'est effacé.

    ⚠⚠ `vc_render_tifxyz` ne refait pas une pile dont les 109 fichiers existent : il écrit « all slices exist, skipping » et
    rend zéro. Or il crée ses 109 fichiers dès le début. Une pile coupée en route, relancée en place, était donc déclarée
    rendue sans qu'un pixel ne change, et recevait le témoin de fin : le 2026-09-25, quatre piles du segment l'ont reçu ainsi.
    """
    if not (sortie.is_dir() and any(sortie.glob("*.tif"))):
        return None
    base, k = sortie.parent / "_partielles" / f"{sortie.name}_{time.strftime('%Y%m%dT%H%M%S')}", 0
    dest = base
    while dest.exists():
        k += 1
        dest = base.with_name(f"{base.name}_{k}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    sortie.rename(dest)
    return dest


def le_journal_prouve_la_fin(journal: Path) -> bool:
    """Un journal de rendu écrit avant le témoin de fin prouve que le rendu est allé au bout : la dernière bande à 100 %, la
    ligne de débit du chien de garde, et aucun abandon."""
    if not journal.is_file():
        return False
    t = journal.read_text(errors="replace")
    return bool(re.search(r"band (\d+)/\1 \(100%\)", t)) and "   rendu :" in t and "ABANDONNE" not in t


def marquer_les_piles_anciennes(dossier: Path = LE_DOSSIER) -> dict:
    """Le témoin de fin, posé une fois sur les piles rendues avant qu'il existe, quand leur journal prouve la fin.

    ⚠ Une pile dont le journal ne prouve rien n'est pas marquée : elle sera refaite à son prochain usage, ce qui coûte un
    rendu, là où la marquer à tort coûterait une mesure fausse.
    """
    out = {"deja_marquees": [], "marquees": [], "laissees": []}
    for d in sorted(x for x in dossier.rglob("*") if x.is_dir() and len(list(x.glob("*.tif"))) == LES_COUCHES):
        nom = str(d.relative_to(dossier))
        if (d / LE_TEMOIN_DE_FIN).is_file():
            out["deja_marquees"].append(nom)
        elif le_journal_prouve_la_fin(d.with_suffix(".log")):
            (d / LE_TEMOIN_DE_FIN).write_text("posé après coup : le journal prouve la fin\n")
            out["marquees"].append(nom)
        else:
            out["laissees"].append(nom)
    return out


def lire_la_pile(dossier: Path) -> np.ndarray:
    import tifffile

    fs = sorted(dossier.glob("*.tif"))
    return np.stack([tifffile.imread(f) for f in fs])


def servir(pile: np.ndarray, cy0: int, cx0: int, chunk: int = LE_COTE_DU_CHUNK):
    """Un lecteur de chunks sur une pile rendue, à la forme de celui du dépôt : `(bloc, raison)`."""
    ny, nx = pile.shape[1] // chunk, pile.shape[2] // chunk

    def ouvrir(cy: int, cx: int):
        y, x = int(cy) - cy0, int(cx) - cx0
        if not (0 <= y < ny and 0 <= x < nx):
            return None, "hors du rendu"
        return pile[:, y * chunk:(y + 1) * chunk, x * chunk:(x + 1) * chunk], None
    return ouvrir


def le_meta(forme_publiee) -> dict:
    """Le meta du volume publié, que le lecteur prend pour la géométrie du treillis."""
    return {"shape": [int(x) for x in forme_publiee], "chunks": [LES_COUCHES, LE_COTE_DU_CHUNK, LE_COTE_DU_CHUNK],
            "dtype": "|u1", "compressor": None, "fill_value": 0, "dimension_separator": "/"}


# ── LE BLOC ────────────────────────────────────────────────────────────────────────────────────────────────────

def lerreur_jugee(tau: np.ndarray, juges: list[np.ndarray]) -> np.ndarray:
    """L'erreur du transfert là où tous les juges existent et s'accordent à moins d'un demi-feuillet, NaN ailleurs."""
    ok = np.isfinite(tau)
    for j in juges:
        ok &= np.isfinite(j)
    for j in juges[1:]:
        with np.errstate(invalid="ignore"):
            ok &= np.abs(j - juges[0]) < DEMI_PAS_EN_VOXELS
    return np.where(ok, tau - juges[0], np.nan)


def la_fenetre_de_maille(cy: int, cx: int, cote: int, maille: int = LA_MAILLE, chunk: int = LE_COTE_DU_CHUNK,
                         pas_de_grille: int = 20) -> tuple[slice, slice]:
    """Les points de la maille qui encadrent un bloc de chunks, bornes comprises."""
    px = pas_de_grille * maille
    r0, r1 = int(np.floor(cy * chunk / px)), int(np.ceil((cy + cote) * chunk / px))
    c0, c1 = int(np.floor(cx * chunk / px)), int(np.ceil((cx + cote) * chunk / px))
    return slice(r0, r1 + 1), slice(c0, c1 + 1)


def les_blocs_candidats(tau: np.ndarray, empreinte: np.ndarray, gy: int, gx: int, cote: int = LE_BLOC,
                        pas_de_grille: int = 20) -> list[tuple[int, int]]:
    """Les blocs que la règle admet, au pas du bloc : dans l'empreinte, la surface produite partout définie.

    `empreinte` est la validité de la grille pleine du segment ; l'ordre est celui de la rangée puis de la colonne.
    """
    out = []
    for by in range(0, gy - cote + 1, cote):
        for bx in range(0, gx - cote + 1, cote):
            e0 = empreinte[by * LE_COTE_DU_CHUNK // pas_de_grille:(by + cote) * LE_COTE_DU_CHUNK // pas_de_grille,
                           bx * LE_COTE_DU_CHUNK // pas_de_grille:(bx + cote) * LE_COTE_DU_CHUNK // pas_de_grille]
            sr, sc = la_fenetre_de_maille(by, bx, cote, pas_de_grille=pas_de_grille)
            if e0.size == 0 or not e0.all() or sr.stop > tau.shape[0] or sc.stop > tau.shape[1] \
                    or not np.isfinite(tau[sr, sc]).all():
                continue
            out.append((by, bx))
    return out


def le_bloc(tau: np.ndarray, erreur: np.ndarray, empreinte: np.ndarray, gy: int, gx: int, cote: int = LE_BLOC,
            pas_de_grille: int = 20) -> dict:
    """Le bloc de la règle : parmi les candidats, le plus de ratés jugés ; égalités départagées par la rangée puis la
    colonne."""
    cands = []
    for by, bx in les_blocs_candidats(tau, empreinte, gy, gx, cote, pas_de_grille):
        sr, sc = la_fenetre_de_maille(by, bx, cote, pas_de_grille=pas_de_grille)
        e = erreur[sr, sc]
        note = np.isfinite(e)
        cands.append((-int((np.abs(e[note]) >= DEMI_PAS_EN_VOXELS).sum()), by, bx, int(note.sum())))
    if not cands:
        return {"decidable": False, "la_raison": "aucun bloc ne tient la règle"}
    cands.sort()
    m, by, bx, n = cands[0]
    return {"decidable": True, "la_rangee": by, "la_colonne": bx, "le_cote": cote, "les_rates": -m,
            "les_points_notes": n, "les_blocs_candidats": len(cands)}


# ── LA MARCHE ──────────────────────────────────────────────────────────────────────────────────────────────────

def les_pas_du_bloc(by: int, bx: int, cote: int, ouvrir, meta: dict, volume: dict, delai: float = DELAI) -> dict:
    """Les pas de toutes les coutures du bloc : le long des rangées, et entre rangées voisines."""
    bande = {"le_sens": "rangees", "le_centre": by + cote // 2, "les_lignes": list(range(by, by + cote)),
             "de": bx, "a": bx + cote - 1}
    return lire_une_bande(bande, volume, delai, ouvrir, meta)


def la_marche_du_bloc(h: dict, v: dict, by: int, bx: int, cote: int) -> dict:
    """La profondeur de la feuille en chaque chunk du bloc, par moindres carrés sur les pas, de moyenne nulle.

    `h[r][c]` est la profondeur de (r, c+1) moins celle de (r, c) ; `v[r][c]`, celle de (r+1, c) moins celle de (r, c).
    Seules comptent les coutures dont les deux chunks sont dans le bloc. Un chunk qu'aucune couture ne relie au reste
    n'a pas de profondeur : NaN.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse.linalg import lsqr

    idx = lambda r, c: (r - by) * cote + (c - bx)  # noqa: E731
    dedans = lambda r, c: by <= r < by + cote and bx <= c < bx + cote  # noqa: E731
    lignes, cols, vals, b = [], [], [], []
    aretes = []
    for sens, d in (("h", h), ("v", v)):
        for r, s in d.items():
            for c, x in s.items():
                r, c = int(r), int(c)
                r2, c2 = (r, c + 1) if sens == "h" else (r + 1, c)
                if not (dedans(r, c) and dedans(r2, c2)):
                    continue
                k = len(b)
                lignes += [k, k]
                cols += [idx(r2, c2), idx(r, c)]
                vals += [1.0, -1.0]
                b.append(float(x[0]))
                aretes.append((idx(r, c), idx(r2, c2)))
    n = cote * cote
    D = np.full((cote, cote), np.nan)
    if not b:
        return {"la_profondeur": D, "les_coutures": 0, "le_residu_rms": None, "les_chunks_relies": 0}
    g = coo_matrix((np.ones(len(aretes)), ([a for a, _ in aretes], [z for _, z in aretes])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    touche = np.zeros(n, dtype=bool)
    for a, z in aretes:
        touche[a] = touche[z] = True
    comptes = np.bincount(lab[touche], minlength=lab.max() + 1)
    grande = int(np.argmax(comptes))
    garde = touche & (lab == grande)
    A = coo_matrix((vals, (lignes, cols)), shape=(len(b), n)).tocsr()
    sel = np.array([garde[a] and garde[z] for a, z in aretes])
    A2, b2 = A[sel][:, garde], np.array(b)[sel]
    x = lsqr(A2, b2, atol=1e-10, btol=1e-10)[0]
    x = x - x.mean()
    D.ravel()[np.nonzero(garde)[0]] = x
    res = A2 @ x - b2
    return {"la_profondeur": D, "les_coutures": int(sel.sum()), "le_residu_rms": round(float(np.sqrt(np.mean(res ** 2))), 4),
            "les_chunks_relies": int(garde.sum())}


def lerreur_aux_chunks(erreur: np.ndarray, by: int, bx: int, cote: int, maille: int = LA_MAILLE,
                       chunk: int = LE_COTE_DU_CHUNK, pas_de_grille: int = 20) -> np.ndarray:
    """L'erreur du transfert au centre de chaque chunk du bloc, bilinéaire entre les quatre points de maille qui
    l'encadrent ; NaN si l'un des quatre n'est pas noté."""
    px = pas_de_grille * maille
    out = np.full((cote, cote), np.nan)
    for i in range(cote):
        for j in range(cote):
            y, x = ((by + i) * chunk + chunk / 2.0) / px, ((bx + j) * chunk + chunk / 2.0) / px
            y0, x0 = int(np.floor(y)), int(np.floor(x))
            if y0 + 1 >= erreur.shape[0] or x0 + 1 >= erreur.shape[1]:
                continue
            q = erreur[y0:y0 + 2, x0:x0 + 2]
            if not np.isfinite(q).all():
                continue
            fy, fx = y - y0, x - x0
            out[i, j] = ((1 - fy) * ((1 - fx) * q[0, 0] + fx * q[0, 1]) + fy * ((1 - fx) * q[1, 0] + fx * q[1, 1]))
    return out


def laccord_des_paires(profondeur: np.ndarray, erreur: np.ndarray, seuil: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Sur les paires de chunks où les deux existent : le juge les sépare-t-il, la marche aussi ?"""
    ok = np.isfinite(profondeur) & np.isfinite(erreur)
    d, e = profondeur[ok], erreur[ok]
    iu = np.triu_indices(len(d), k=1)
    sep_j = np.abs(e[:, None] - e[None, :])[iu] >= seuil
    sep_m = np.abs(d[:, None] - d[None, :])[iu] >= seuil
    out = {"les_chunks": int(ok.sum()), "les_paires": int(len(sep_j)),
           "les_paires_que_le_juge_separe": int(sep_j.sum()), "les_paires_quil_reunit": int((~sep_j).sum())}
    if sep_j.any():
        out["la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe"] = round(float(sep_m[sep_j].mean()), 4)
    if (~sep_j).any():
        out["la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit"] = round(float((~sep_m)[~sep_j].mean()), 4)
    if len(d) > 2 and np.std(d) > 0 and np.std(e) > 0:
        out["la_correlation"] = round(float(np.corrcoef(d, e)[0, 1]), 4)
    return out


def la_rampe(forme: tuple, by: int, cote: int, hauteur: float = PAS_EN_VOXELS, largeur: int = LA_RAMPE_EN_CHUNKS,
             maille: int = LA_MAILLE, chunk: int = LE_COTE_DU_CHUNK, pas_de_grille: int = 20) -> np.ndarray:
    """Le contrôle positif : un écart POSÉ le long des RANGÉES, nul au-dessus de la rampe, d'un pas plein au-dessous, la
    rampe de `largeur` chunks centrée sur le milieu du bloc.

    ⚠ La transition est progressive exprès : une marche ne lit qu'un écart qui avance de moins d'un demi-feuillet d'une
    couture à la suivante, et la rampe en pose un quart de pas par couture. ⚠⚠ Elle court le long des rangées et non
    des colonnes, et c'est une correction : posée d'abord le long des colonnes, elle tombait pour sa moitié droite dans
    l'air qui borde le bloc, où il n'y a rien à décaler.
    """
    y = np.arange(forme[0]) * pas_de_grille * maille
    y0 = (by + cote // 2 - largeur // 2) * chunk
    t = np.clip((y - y0) / float(largeur * chunk), 0.0, 1.0) * float(hauteur)
    return np.broadcast_to(t[:, None], forme).copy()


def la_feuille_dans_la_pile(pile: np.ndarray, chunk: int = LE_COTE_DU_CHUNK, lissage: int = 9) -> np.ndarray:
    """Chunk par chunk, l'écart au milieu de la pile de la couche la plus claire du profil moyen, lissé par un triangle
    de `lissage` couches : zéro quand la surface est sur la feuille. ⚠ Un triangle et non une boîte : une boîte étale
    une couche claire en plateau, et le plateau se lit à son bord."""
    ny, nx = pile.shape[1] // chunk, pile.shape[2] // chunk
    milieu = pile.shape[0] // 2
    demi = lissage // 2
    noyau = np.concatenate([np.arange(1, demi + 2), np.arange(demi, 0, -1)]).astype(float)
    noyau /= noyau.sum()
    out = np.full((ny, nx), np.nan)
    for i in range(ny):
        for j in range(nx):
            b = pile[:, i * chunk:(i + 1) * chunk, j * chunk:(j + 1) * chunk]
            vus = b.reshape(b.shape[0], -1)
            if not (vus > 0).any(axis=0).mean() > 0.5:
                continue
            prof = np.convolve(vus.mean(axis=1), noyau, mode="same")
            bord = lissage // 2
            k = bord + int(np.argmax(prof[bord:len(prof) - bord]))
            out[i, j] = k - milieu
    return out


def la_part_retrouvee(marche: np.ndarray, temoin: np.ndarray, pose: np.ndarray) -> dict:
    """Ce que la marche retrouve d'un écart posé : la pente de (marche − marche du témoin) contre l'écart posé.

    Une marche qui voit tout l'écart a une pente de un ; une marche qui n'en voit rien, de zéro. Le témoin est la même
    surface sans l'écart, lue de même : sa soustraction retire ce que la surface fait d'elle-même.
    """
    ok = np.isfinite(marche) & np.isfinite(temoin) & np.isfinite(pose)
    if ok.sum() < 3 or np.std(pose[ok]) == 0:
        return {"decidable": False}
    x, y = pose[ok], (marche - temoin)[ok]
    pente = float(np.polyfit(x, y, 1)[0])
    return {"decidable": True, "les_chunks": int(ok.sum()), "la_pente": round(pente, 4),
            "lecart_pose_voxels": round(float(x.max() - x.min()), 4),
            "lecart_retrouve_voxels": round(pente * float(x.max() - x.min()), 4)}


def la_rangee_de_coupe(erreur: np.ndarray) -> int:
    """La rangée de chunks du bloc qui porte le plus de ratés jugés ; la première en cas d'égalité."""
    with np.errstate(invalid="ignore"):
        rates = (np.abs(erreur) >= DEMI_PAS_EN_VOXELS).sum(axis=1)
    return int(np.argmax(rates))


def la_coupe(pile: np.ndarray, y: int, pas: int | None = None) -> list:
    """La coupe de la pile à la rangée de pixels `y` : couche contre colonne, moyennée par `pas` colonnes."""
    pas = LE_PAS_DE_COUPE if pas is None else pas
    ligne = pile[:, int(y), :].astype(np.float64)
    n = ligne.shape[1] // pas
    return np.round(ligne[:, :n * pas].reshape(ligne.shape[0], n, pas).mean(axis=2)).astype(int).tolist()


# ── LA MESURE ──────────────────────────────────────────────────────────────────────────────────────────────────

def le_controle(pile_publiee_de) -> dict:
    """Le rendu du segment lui-même contre la pile publiée, sur le carré de contrôle."""
    cy, cx, cote = LE_CONTROLE
    d = LE_DOSSIER / "le_segment_plein"
    r = rendre(RACINE / "data" / "spire_voisine" / LE_SEGMENT, d / f"controle_{cy}_{cx}", le_cadre(cy, cx, cote))
    if not r["rendue"]:
        return {"decidable": False, "le_rendu": r}
    ren = lire_la_pile(d / f"controle_{cy}_{cx}")
    pub = pile_publiee_de(cy, cx, cote)
    if pub is None:
        return {"decidable": False, "la_raison": "la pile publiée ne répond pas"}
    diff = np.abs(ren.astype(np.int16) - pub.astype(np.int16))
    return {"decidable": True, "le_rendu": r, "les_voxels": int(diff.size),
            "la_part_des_voxels_egaux": round(float((diff == 0).mean()), 4),
            "la_part_a_un_niveau_pres": round(float((diff <= 1).mean()), 4),
            "lecart_max": int(diff.max()),
            "la_part_egale_si_lordre_des_couches_est_retourne": round(float((ren[::-1] == pub).mean()), 4)}


def mesurer(cache: Path = LE_CACHE, delai: float = DELAI) -> dict:
    debut = time.monotonic()
    d = telecharger(LE_SEGMENT, cache, delai)
    if isinstance(d, str):
        return {"decidable": False, "la_raison": d}
    ref, valide, esp = lire_tifxyz(d)
    volume = le_segment_declare()
    meta = array_meta(f"{BUCKET}/{volume['cle']}", 0, delai)
    gy, gx = -(-meta["shape"][1] // LE_COTE_DU_CHUNK), -(-meta["shape"][2] // LE_COTE_DU_CHUNK)

    def pile_publiee_de(cy, cx, cote, large=None):
        large = cote if large is None else large
        out = np.zeros((LES_COUCHES, cote * LE_COTE_DU_CHUNK, large * LE_COTE_DU_CHUNK), dtype=np.uint8)
        for i in range(cote):
            for j in range(large):
                b, _ = un_chunk(f"{BUCKET}/{volume['cle']}", meta, cy + i, cx + j, delai, None)
                if b is None:
                    return None
                out[:, i * LE_COTE_DU_CHUNK:(i + 1) * LE_COTE_DU_CHUNK,
                    j * LE_COTE_DU_CHUNK:(j + 1) * LE_COTE_DU_CHUNK] = b
        return out

    out = {"le_segment": LE_SEGMENT, "la_prediction": LA_PREDICTION, "le_cote": LE_COTE, "la_maille": LA_MAILLE,
           "le_treillis": [int(gy), int(gx)], "le_controle": le_controle(pile_publiee_de)}
    if not out["le_controle"].get("decidable"):
        out["decidable"] = False
        return out
    tau = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    juges = [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES]
    err = lerreur_jugee(tau, juges)
    bloc = le_bloc(tau, err, valide, gy, gx)
    out["le_bloc"] = bloc
    if not bloc["decidable"]:
        out["decidable"] = False
        return out
    by, bx = bloc["la_rangee"], bloc["la_colonne"]
    cadre = le_cadre(by, bx, LE_BLOC)
    scale = 1.0 / (esp * LA_MAILLE)
    pr, vr = le_maillage_reduit(ref, valide)
    pp, vp = le_maillage_produit(ref, valide, tau)
    t_reduit = ecrire_tifxyz(LE_DOSSIER / "le_segment_reduit" / "maillage", pr, vr, scale, "le_segment_reduit")
    t_produit = ecrire_tifxyz(LE_DOSSIER / "la_spire_produite" / "maillage", pp, vp, scale, "la_spire_produite")
    e_chunks = lerreur_aux_chunks(err, by, bx, LE_BLOC)
    out["lerreur_aux_chunks"] = {"les_chunks_notes": int(np.isfinite(e_chunks).sum()),
                                 "les_chunks_rates": int((np.abs(e_chunks[np.isfinite(e_chunks)]) >= DEMI_PAS_EN_VOXELS).sum())}
    out["les_piles"] = {}
    cartes = {"lerreur": e_chunks}
    ic = la_rangee_de_coupe(e_chunks)
    y_coupe = ic * LE_COTE_DU_CHUNK + LE_COTE_DU_CHUNK // 2
    rang = pile_publiee_de(by + ic, bx, 1, LE_BLOC)
    coupes = {"la_rangee_du_bloc": ic, "le_pas_en_pixels": LE_PAS_DE_COUPE,
              "la_publiee": None if rang is None else la_coupe(rang, LE_COTE_DU_CHUNK // 2)}
    rampe = la_rampe(tau.shape, by, LE_BLOC)
    pz, vz = le_maillage_produit(ref, valide, rampe)
    t_rampe = ecrire_tifxyz(LE_DOSSIER / LE_DOSSIER_DE_LA_RAMPE / "maillage", pz, vz, scale, "la_rampe_posee")
    e_rampe = lerreur_aux_chunks(rampe, by, bx, LE_BLOC)
    cartes["la_rampe"] = e_rampe
    out["la_feuille_dans_la_pile"] = {}
    for nom, tifxyz in (("la_publiee", None), ("le_segment_reduit", t_reduit), ("la_spire_produite", t_produit),
                        ("la_rampe_posee", t_rampe)):
        if tifxyz is None:
            ouvrir, r = None, {"rendue": True, "publiee": True}
        else:
            sortie = LE_DOSSIER / (LE_DOSSIER_DE_LA_RAMPE if nom == "la_rampe_posee" else nom) / f"bloc_{by}_{bx}"
            r = rendre(tifxyz, sortie, cadre)
            if not r["rendue"]:
                out["les_piles"][nom] = {"le_rendu": r}
                out["decidable"] = False
                return out
            pile = lire_la_pile(sortie)
            coupes[nom] = la_coupe(pile, y_coupe)
            f = la_feuille_dans_la_pile(pile)
            fv = f[np.isfinite(f)]
            out["la_feuille_dans_la_pile"][nom] = {
                "les_chunks": int(fv.size), "lecart_median_voxels": round(float(np.median(np.abs(fv))), 4) if fv.size else None,
                "la_part_a_moins_dun_quart_de_pas": round(float((np.abs(fv) <= PAS_EN_VOXELS / 4).mean()), 4) if fv.size else None}
            ouvrir = servir(pile, by, bx)
        lu = les_pas_du_bloc(by, bx, LE_BLOC, ouvrir, meta, volume, delai)
        if not lu.get("decidable"):
            out["les_piles"][nom] = {"le_rendu": r, "la_lecture": lu.get("raison")}
            out["decidable"] = False
            return out
        m = la_marche_du_bloc(lu["le_long"], lu["en_travers"], by, bx, LE_BLOC)
        prof = m.pop("la_profondeur")
        cartes[nom] = prof
        out["les_piles"][nom] = {"le_rendu": r, "la_marche": m,
                                 "letendue_de_la_marche_voxels": (round(float(np.nanmax(prof) - np.nanmin(prof)), 4)
                                                                  if np.isfinite(prof).any() else None),
                                 "laccord_des_paires": laccord_des_paires(prof, e_rampe if nom == "la_rampe_posee"
                                                                          else e_chunks)}
    np.save(LE_DOSSIER / f"cartes_{by}_{bx}.npy", np.stack([cartes[k] for k in
                                                            ("lerreur", "la_publiee", "le_segment_reduit",
                                                             "la_spire_produite", "la_rampe", "la_rampe_posee")]))
    out["le_temoin_plat"] = laccord_des_paires(np.zeros((LE_BLOC, LE_BLOC)), e_chunks)
    out["ce_que_la_marche_retrouve_de_la_rampe"] = la_part_retrouvee(cartes["la_rampe_posee"],
                                                                      cartes["le_segment_reduit"], e_rampe)
    out["les_cartes"] = {k: [[None if not np.isfinite(x) else round(float(x), 2) for x in r] for r in c]
                         for k, c in cartes.items()}
    out["les_coupes"] = coupes
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = True
    return out


def le_verdict(r: dict) -> dict:
    c = r.get("le_controle") or {}
    if not c.get("decidable") or c.get("la_part_a_un_niveau_pres", 0.0) < 0.99:
        return {"lissue": "le rendu n'égale pas la pile publiée : rien de ce qui suit n'est un instrument"}
    z = ((r.get("les_piles") or {}).get("la_rampe_posee") or {}).get("laccord_des_paires") or {}
    if r.get("decidable") and z and (z.get("la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe") or 0.0) <= 0.5:
        return {"lissue": "la marche ne voit pas l'écart posé : sur ces piles, le treillis est aveugle"}
    p = (r.get("les_piles") or {}).get("la_spire_produite") or {}
    m = p.get("la_marche") or {}
    if not r.get("decidable") or not m.get("les_coutures"):
        return {"lissue": "la pile produite ne se lit pas : le treillis ne voit pas la spire produite"}
    a = p["laccord_des_paires"]
    sep = a.get("la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe") or 0.0
    reu = a.get("la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit") or 0.0
    if sep <= 0.5 or sep + reu <= 1.0:
        return {"lissue": "la marche ne sépare pas mieux que le témoin : le treillis lit la spire produite sans y "
                          "voir les ratés", "separe": sep, "reunit": reu}
    return {"lissue": "la marche sépare : le treillis peut juger une spire que la chaîne a produite",
            "separe": sep, "reunit": reu}


# ── LA BATTERIE ────────────────────────────────────────────────────────────────────────────────────────────────

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

    # Un plan incliné, la grille pleine au pas de 20 voxels : sa normale est connue.
    h, w = 33, 41
    ii, jj = np.mgrid[0:h, 0:w].astype(float)
    ref = np.stack([20.0 * jj, 20.0 * ii, 5.0 * jj + 1000.0], axis=-1)
    val = np.ones((h, w), dtype=bool)
    n, ok = les_normales(ref, val)
    tau = np.full(ref[::8, ::8].shape[:2], 72.0)
    tau[1, 1] = np.nan
    pp, vp = le_maillage_produit(ref, val, tau)
    dep = pp - ref[::8, ::8]
    v("★★★★ la spire produite est poussée de tau le long de la normale du segment",
      lambda: np.allclose(dep[2, 2], 72.0 * n[16, 16]) and abs(np.linalg.norm(dep[2, 2]) - 72.0) < 1e-9)
    v("★★★★ là où tau manque, le point est -1, et là où la normale manque aussi",
      lambda: (pp[1, 1] == -1).all() and not vp[1, 1] and (pp[0, 0] == -1).all() and not vp[0, 0])
    pr, vr = le_maillage_reduit(ref, val)
    v("★★★ le segment réduit est un point sur huit du segment", lambda: np.array_equal(pr, ref[::8, ::8]) and vr.all())
    with tempfile.TemporaryDirectory() as t:
        dd = ecrire_tifxyz(Path(t) / "m", pp, vp, 1.0 / 160.0, "essai")
        rp, rv, resp = lire_tifxyz(dd)
        v("★★★★ un tifxyz écrit se relit tel quel, espacement compris",
          lambda: np.allclose(rp[rv], pp[vp], atol=1e-3) and np.array_equal(rv, vp) and abs(resp - 160.0) < 1e-6)
    c = la_commande_de_rendu(Path("m"), Path("s"), le_cadre(3, 5, 2))
    v("★★★★ le rendu retourne les normales, 109 couches au pas d'un voxel, au cadre des chunks",
      lambda: "--flip-normals" in c and c[c.index("-n") + 1] == "109" and c[c.index("--slice-step") + 1] == "1"
      and c[c.index("--crop-x") + 1] == "640" and c[c.index("--crop-y") + 1] == "384"
      and c[c.index("--crop-width") + 1] == "256")
    cm = la_commande_de_rendu(Path("m"), Path("s"), le_cadre(3, 5, 2), miroir=Path("miroir"))
    v("★★★★ depuis un miroir, le volume est le miroir et rien n'est lu à distance",
      lambda: cm[cm.index("-v") + 1] == "miroir" and "--remote-url" not in cm and cm[2:] == c[4:])
    pile = np.arange(LES_COUCHES * 256 * 384, dtype=np.int64).reshape(LES_COUCHES, 256, 384) % 251
    ouv = servir(pile, 10, 20)
    b, why = ouv(11, 22)
    v("★★★★ le lecteur de pile rend le bon chunk, et refuse hors du rendu",
      lambda: why is None and np.array_equal(b, pile[:, 128:256, 256:384]) and ouv(12, 20)[0] is None
      and ouv(10, 19)[1] == "hors du rendu")
    # Le bloc : deux candidats, le plus raté gagne ; un bloc où la surface produite manque est écarté.
    g_tau = np.zeros((40, 40))
    g_err = np.full((40, 40), 0.0)
    emp = np.ones((400, 400), dtype=bool)
    g_err[12:22, 0:10] = 72.0
    b1 = le_bloc(g_tau, g_err, emp, 50, 50, cote=16, pas_de_grille=20)
    v("★★★★ le bloc est celui qui porte le plus de ratés jugés",
      lambda: b1["decidable"] and (b1["la_rangee"], b1["la_colonne"]) == (16, 0), str(b1))
    g_tau2 = g_tau.copy()
    g_tau2[15, 5] = np.nan
    b2 = le_bloc(g_tau2, g_err, emp, 50, 50, cote=16, pas_de_grille=20)
    v("★★★ un bloc où la surface produite manque en un point est écarté",
      lambda: b2["decidable"] and (b2["la_rangee"], b2["la_colonne"]) != (16, 0), str(b2))
    j1, j2 = np.array([[80.0, 80.0, np.nan]]), np.array([[90.0, 150.0, 80.0]])
    e = lerreur_jugee(np.array([[100.0, 100.0, 100.0]]), [j1, j2])
    v("★★★★ l'erreur n'est jugée que là où les deux juges existent et s'accordent",
      lambda: e[0, 0] == 20.0 and np.isnan(e[0, 1]) and np.isnan(e[0, 2]))
    # La marche retrouve une profondeur connue depuis ses seules différences, à une constante près.
    by, bx, cote = 3, 7, 6
    D = np.add.outer(np.linspace(0, 50, cote), np.linspace(0, -30, cote))
    D[3:, 3:] += 72.0
    hh = {r: {c: (D[r - by, c - bx + 1] - D[r - by, c - bx], 0.0, 16) for c in range(bx, bx + cote - 1)}
          for r in range(by, by + cote)}
    vv = {r: {c: (D[r - by + 1, c - bx] - D[r - by, c - bx], 0.0, 16) for c in range(bx, bx + cote)}
          for r in range(by, by + cote - 1)}
    hh[by][bx + cote - 1] = (999.0, 0.0, 16)   # une couture qui sort du bloc ne compte pas
    m = la_marche_du_bloc(hh, vv, by, bx, cote)
    v("★★★★ la marche retrouve la profondeur depuis les pas, de moyenne nulle",
      lambda: np.allclose(m["la_profondeur"], D - D.mean(), atol=1e-6) and m["le_residu_rms"] < 1e-6, str(m.get("le_residu_rms")))
    hh2 = {r: {c: x for c, x in s.items() if c != bx} for r, s in hh.items()}
    vv2 = {r: {c: x for c, x in s.items() if c != bx} for r, s in vv.items()}
    m2 = la_marche_du_bloc(hh2, vv2, by, bx, cote)
    v("★★★ un chunk qu'aucune couture ne relie au reste n'a pas de profondeur",
      lambda: np.isnan(m2["la_profondeur"][:, 0]).all() and np.isfinite(m2["la_profondeur"][:, 1:]).all())
    # L'erreur aux chunks : le centre du chunk (by, bx) tombe au point de maille qu'on sait calculer.
    eg = np.add.outer(np.arange(40.0), 100.0 * np.arange(40.0))
    ec = lerreur_aux_chunks(eg, 5, 10, 2)
    yy, xx = (5 * 128 + 64) / 160.0, (10 * 128 + 64) / 160.0
    v("★★★★ l'erreur au centre d'un chunk est l'interpolée de la maille",
      lambda: abs(ec[0, 0] - (yy + 100.0 * xx)) < 1e-9, f"{ec[0, 0]} contre {yy + 100 * xx}")
    eg2 = eg.copy()
    eg2[4, 8] = np.nan
    v("★★★ un coin non noté rend le chunk non noté", lambda: np.isnan(lerreur_aux_chunks(eg2, 5, 10, 2)[0, 0]))
    # L'accord des paires : une marche qui voit le saut sépare ce que le juge sépare ; une marche plate, rien.
    err = np.zeros((4, 4))
    err[:, 2:] = 72.0
    a_vrai = laccord_des_paires(err + 3.0, err)
    a_plat = laccord_des_paires(np.zeros((4, 4)), err)
    v("★★★★ une marche qui suit l'erreur sépare et réunit tout ce que le juge sépare et réunit",
      lambda: a_vrai["la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe"] == 1.0
      and a_vrai["la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit"] == 1.0)
    v("★★★★ la marche plate, le témoin, ne sépare rien",
      lambda: a_plat["la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe"] == 0.0
      and a_plat["les_paires_que_le_juge_separe"] == 64)
    v("★★★ le verdict retient le témoin : une marche plate ne sépare pas",
      lambda: "ne sépare pas" in le_verdict({"le_controle": {"decidable": True, "la_part_a_un_niveau_pres": 1.0},
                                             "decidable": True, "les_piles": {"la_spire_produite": {
                                                 "la_marche": {"les_coutures": 10}, "laccord_des_paires": a_plat}}})["lissue"])
    v("★★★ le verdict refuse un rendu qui n'égale pas la publiée",
      lambda: "n'égale pas" in le_verdict({"le_controle": {"decidable": True, "la_part_a_un_niveau_pres": 0.5}})["lissue"])

    ee = np.full((4, 3), np.nan)
    ee[1, :2] = 72.0
    ee[2, 0] = -40.0
    v("★★★ la coupe passe par la rangée de chunks la plus ratée", lambda: la_rangee_de_coupe(ee) == 1)
    pc = np.zeros((3, 4, 16), dtype=np.uint8)
    pc[:, 2, 8:] = 80
    v("★★★ la coupe moyenne la rangée demandée par paquets de colonnes",
      lambda: la_coupe(pc, 2, 8) == [[0, 80]] * 3 and la_coupe(pc, 1, 8) == [[0, 0]] * 3)

    rz = la_rampe((40, 3), 10, 16)
    y0 = (10 + 8 - 2) * 128
    v("★★★★ la rampe posée est nulle au-dessus d'elle, d'un pas plein au-dessous, et la même sur chaque colonne",
      lambda: rz[y0 // 160, 0] == 0.0 and rz[-(-(y0 + 512) // 160), 1] == PAS_EN_VOXELS
      and 0.0 < rz[y0 // 160 + 2, 2] < PAS_EN_VOXELS and (rz[:, 0] == rz[:, 2]).all())
    pf = np.full((LES_COUCHES, 128, 256), 20, dtype=np.uint8)
    pf[54, :, :128] = 200
    pf[80, :, 128:] = 200
    ff = la_feuille_dans_la_pile(pf)
    v("★★★★ la feuille dans la pile est à zéro au milieu, et à son écart ailleurs",
      lambda: ff[0, 0] == 0 and ff[0, 1] == 26, str(ff))
    v("★★★ le verdict refuse une marche qui ne voit pas la rampe posée",
      lambda: "aveugle" in le_verdict({"le_controle": {"decidable": True, "la_part_a_un_niveau_pres": 1.0},
                                       "decidable": True, "les_piles": {"la_rampe_posee": {
                                           "laccord_des_paires": a_plat}}})["lissue"])

    pose = np.tile(np.linspace(0.0, 72.0, 8), (8, 1))
    tem = np.random.default_rng(0).normal(0.0, 3.0, (8, 8))
    v("★★★★ une marche qui voit tout l'écart posé a une pente de un, une marche aveugle une pente de zéro",
      lambda: abs(la_part_retrouvee(tem + pose, tem, pose)["la_pente"] - 1.0) < 1e-9
      and abs(la_part_retrouvee(tem, tem, pose)["la_pente"]) < 1e-9)

    # La reprise : une pile coupée en route a ses 109 fichiers, et ne doit pas passer pour complète.
    class _Fin:
        def __init__(self, code):
            self.returncode = code

    def faux_rendu(code: int):
        """Comme `vc_render_tifxyz` : les 109 fichiers d'abord, vides, puis remplis si le rendu va au bout ; et rien du
        tout si les 109 existent déjà."""
        def lancer(cmd, **_):
            sortie = Path(cmd[cmd.index("--tif-output") + 1])
            if sortie.is_dir() and all((sortie / f"{k:03d}.tif").exists() for k in range(LES_COUCHES)):
                return _Fin(0)
            sortie.mkdir(parents=True, exist_ok=True)
            for k in range(LES_COUCHES):
                (sortie / f"{k:03d}.tif").write_bytes(b"" if code else b"rendu")
            return _Fin(code)
        return lancer

    with tempfile.TemporaryDirectory() as t:
        s_ = Path(t) / "bloc"
        s_.mkdir()
        for k in range(LES_COUCHES - 1):
            (s_ / f"{k:03d}.tif").write_bytes(b"")
        (s_ / LE_TEMOIN_DE_FIN).write_text("un témoin resté d'avant")
        r1 = rendre(Path("m"), s_, le_cadre(0, 0, 1), lancer=faux_rendu(4))
        v("★★★★ un rendu interrompu laisse ses 109 fichiers, et la pile n'est pas complète",
          lambda: not r1["rendue"] and r1["les_couches"] == LES_COUCHES and not la_pile_est_complete(s_), str(r1))
        v("★★★★ le témoin resté d'un rendu précédent est retiré avant de relancer",
          lambda: not (s_ / LE_TEMOIN_DE_FIN).exists())
        r2 = rendre(Path("m"), s_, le_cadre(0, 0, 1), lancer=faux_rendu(0))
        v("★★★★ la pile interrompue est refaite, et le rendu qui va au bout pose le témoin",
          lambda: r2["rendue"] and not r2["reprise"] and la_pile_est_complete(s_), str(r2))
        v("★★★★ refaite pour de vrai : ses couches sont celles du nouveau rendu, et l'inachevée est mise de côté, pas effacée",
          lambda: all((s_ / f"{k:03d}.tif").read_bytes() == b"rendu" for k in range(LES_COUCHES))
          and Path(r2.get("mise_de_cote", "/nulle/part")).is_dir(), str(r2))
        r3 = rendre(Path("m"), s_, le_cadre(0, 0, 1), lancer=faux_rendu(1))
        v("★★★ une pile complète est reprise sans être relancée", lambda: r3 == {"rendue": True, "reprise": True}, str(r3))
        a_ = Path(t) / "anciennes"
        fin = "  band 15/16 (93%)\r  band 16/16 (100%)  eta 0m00s\nRendering: x\n   rendu : 9 octets en 3 s (3 Kio/s)\n"
        for nom, j in (("finie", fin), ("coupee", "  band 3/16 (18%)  eta 7m06s"),
                       ("abandonnee", fin + "⚠⚠ RENDU ABANDONNE — ni activité\n"), ("sans_journal", None)):
            (a_ / nom).mkdir(parents=True)
            for k in range(LES_COUCHES):
                (a_ / nom / f"{k:03d}.tif").write_bytes(b"")
            if j is not None:
                (a_ / f"{nom}.log").write_text(j)
        ma = marquer_les_piles_anciennes(a_)
        v("★★★★ le témoin n'est posé après coup que sur une pile dont le journal prouve la fin",
          lambda: ma["marquees"] == ["finie"] and ma["laissees"] == ["abandonnee", "coupee", "sans_journal"], str(ma))
        mb = marquer_les_piles_anciennes(a_)
        v("★★★ une seconde passe ne marque rien de plus", lambda: mb["deja_marquees"] == ["finie"] and not mb["marquees"])

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--marquer-les-anciennes", action="store_true",
                   help="pose le témoin de fin sur les piles rendues avant lui, quand leur journal prouve la fin")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.marquer_les_anciennes:
        m = marquer_les_piles_anciennes()
        print(json.dumps({k: len(x) for k, x in m.items()} | {"laissees": m["laissees"]}, indent=1, ensure_ascii=False))
        return 0
    r = mesurer()
    r["le_verdict"] = le_verdict(r)
    texte = json.dumps(r, indent=2, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(texte[:4000])
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
