#!/usr/bin/env python3
"""La case qui décide demande un RECALAGE, et ce fichier mesure s'il est traitable.

⚠⚠⚠ CE QUE `68` §4 ET `72` §3 AFFIRMENT, ET CE QUI MANQUE. Les deux disent que remplir la case
du régime du prix sur `PHerc0500P2` ne demande *« ni faisceau, ni annotation manuelle, ni
rescan »* — c'est vrai, et incomplet. **Scorer** le résultat contre la vérité terrain infrarouge
demande une chose de plus, que ni l'un ni l'autre ne nomme : les étiquettes et les couches du
régime du prix ne vivent pas sur le **même aplatissement**.

⭐⭐ CE QUI EST PUBLIÉ, ET OÙ — vérifié le 2026-09-05 sur les DEUX serveurs, parce que
n'interroger qu'une vue du corpus est l'angle mort que `78` §0 recense trois fois :

| | serveur | forme |
|---|---|---|
| `500P2_inklabels.png` + `_ir` + `_mask` | `dl.ash2txt.org/fragments/PHerc0500P2/paths/2um_front_surface/` | **27 160 × 14 990** |
| couches du chemin des étiquettes | même chemin, `layers/` | 65 couches, **2 µm seulement** |
| couches du **régime du prix** | bucket ouvert, `segments/20250628074500-500P2_front/` | 28 couches, 9,362 µm, grille **6 280 × 3 580** |
| couches de production | même segment | 118 couches, 2,215 µm, grille **26 440 × 15 060** |

⚠⚠ **26 440 × 15 060 contre 27 160 × 14 990** : les deux surfaces couvrent le même fragment mais
ne sont **pas la même paramétrisation**. Un aplatissement n'est pas unique, donc les étiquettes
ne se transportent pas pixel pour pixel.

⚠⚠⚠ ET LE RECALAGE NE PEUT PAS ÊTRE EXACT, faute de coordonnées. Le segment publie son
`tifxyz-transformed` — une position 3D par cellule — donc apparier deux surfaces **par leur
géométrie** serait une recherche de plus proche voisin, exacte et bon marché. Le chemin des
étiquettes, lui, ne publie **que des images** : pas de `tifxyz`, pas d'`obj`. L'appariement doit
donc se faire **par l'image**, ce qui est approximatif par nature.

⭐ CE QUE CE FICHIER MESURE, ET RIEN DE PLUS : à quel point les deux empreintes se superposent
sous une **similitude** (échelle, rotation, translation). C'est un test de **faisabilité**, pas
un recalage : s'il rend un recouvrement franc, la registration fine est un lot défini ; s'il
n'en rend aucun, les deux aplatissements diffèrent par plus qu'une similitude et il faudra un
champ de déformation, ce qui est un tout autre chantier.

⚠ Les deux empreintes viennent de sources différentes et il faut le dire : celle des étiquettes
est le `_mask` publié, celle du segment est la **région non nulle de sa carte d'encre réduite**.
La seconde n'est pas un masque de surface — c'est là où le détecteur a rendu quelque chose — donc
elle peut être plus petite que la surface réelle. Un recouvrement mesuré est donc un **minorant**.

Usage :
    uv run python src/encre/deux_aplatissements.py --verifier
    uv run python src/encre/deux_aplatissements.py --json docs/mesures/deux_aplatissements.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "encre"))

SEGMENT = "20250628074500-500P2_front"
ETIQUETTES = ("https://dl.ash2txt.org/fragments/PHerc0500P2/paths/2um_front_surface/"
              "500P2_mask.png")
LOCAL = RACINE / "data" / "0500P2"

COTE = 256
"""Côté de la grille sur laquelle les deux empreintes sont comparées.

⚠⚠ Les deux images font ~27 000 × 15 000 : une recherche de similitude à pleine résolution
coûterait des heures pour une réponse qui est un OUI ou un NON. À 256 de côté une cellule vaut
~100 µm, soit une lettre — assez fin pour qu'un recouvrement franc se distingue d'un
recouvrement de silhouettes quelconques, et assez grossier pour balayer.

⚠ Et les deux sont ramenées à la MÊME grille carrée, ce qui **détruit le rapport d'aspect** :
c'est voulu, puisque l'échelle fait partie de ce qu'on cherche. Le rapport d'aspect d'origine
est rendu à part, et c'est lui qui dit si une similitude peut suffire."""


def _reduire(a: np.ndarray, cote: int = COTE) -> np.ndarray:
    """
    @brief Une empreinte binaire ramenée à une grille carrée, par moyenne de blocs.

    ⚠ Moyenne et non échantillonnage : prendre un pixel sur N sur une silhouette perdrait les
    bords fins et rendrait deux empreintes plus dissemblables qu'elles ne sont — donc un verdict
    de faisabilité faussement négatif.
    """
    h, w = a.shape
    lignes = np.linspace(0, h, cote + 1).astype(int)
    colonnes = np.linspace(0, w, cote + 1).astype(int)
    out = np.zeros((cote, cote), dtype=float)
    for i in range(cote):
        bande = a[lignes[i]:max(lignes[i] + 1, lignes[i + 1])]
        for j in range(cote):
            bloc = bande[:, colonnes[j]:max(colonnes[j] + 1, colonnes[j + 1])]
            out[i, j] = float(bloc.mean()) if bloc.size else 0.0
    return out


def dice(a: np.ndarray, b: np.ndarray) -> float:
    """
    @brief Le recouvrement de deux empreintes binaires — 1 identiques, 0 disjointes.

    ⚠ Dice et non « part de pixels égaux » : deux empreintes qui couvriraient chacune 30 % de la
    grille s'accordent à 58 % **par le fond** sans se recouvrir du tout. Un accord de fond n'est
    pas un recouvrement.
    """
    a_, b_ = a > 0.5, b > 0.5
    s = a_.sum() + b_.sum()
    return float(2.0 * (a_ & b_).sum() / s) if s else 0.0


def balayer(a: np.ndarray, b: np.ndarray, decalages: range) -> dict:
    """
    @brief Le meilleur recouvrement sous translation entière, et celui de départ.

    ⚠⚠ LE POINT DE DÉPART EST RENDU AVEC LE MEILLEUR, et c'est la moitié qui informe : si
    translater ne gagne rien, les deux empreintes sont déjà alignées **ou** elles ne le seront
    par aucune translation. Le seul « meilleur » ne distingue pas les deux.
    """
    depart = dice(a, b)
    meilleur, ou = depart, (0, 0)
    for di in decalages:
        for dj in decalages:
            if di == 0 and dj == 0:
                continue
            deplace = np.roll(np.roll(b, di, axis=0), dj, axis=1)
            # ⚠ `roll` fait revenir le bord de l'autre côté : on annule la bande qui a bouclé,
            # sinon un décalage fabrique un recouvrement avec du contenu venu du bord opposé.
            if di > 0:
                deplace[:di] = 0
            elif di < 0:
                deplace[di:] = 0
            if dj > 0:
                deplace[:, :dj] = 0
            elif dj < 0:
                deplace[:, dj:] = 0
            d = dice(a, deplace)
            if d > meilleur:
                meilleur, ou = d, (di, dj)
    return dict(dice_depart=depart, dice_meilleur=meilleur, decalage=list(ou))


def empreinte_etiquettes() -> np.ndarray | None:
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    chemin = LOCAL / "500P2_mask.png"
    if not chemin.is_file():
        return None
    a = np.asarray(Image.open(chemin))
    if a.ndim == 3:
        a = a[..., 0]
    return (a > 0).astype(float)


def empreinte_segment() -> np.ndarray | None:
    """
    @brief L'empreinte du segment publié, tirée de sa carte d'encre réduite.

    ⚠⚠ CE N'EST PAS UN MASQUE DE SURFACE et le docstring de tête le dit : c'est là où le
    détecteur publié a rendu quelque chose. Le corpus ouvert ne publie pas de masque pour ce
    segment, donc c'est la meilleure empreinte disponible — et elle borne le recouvrement par
    en dessous plutôt que de le gonfler.
    """
    from PIL import Image

    from zarr_depth import BUCKET, get  # noqa: PLC0415

    import la_case_vide as cv  # noqa: PLC0415

    Image.MAX_IMAGE_PIXELS = None
    for _, fiche in cv._charger().items():
        for sid, seg in fiche.get("segments", {}).items():
            if seg.get("long_id", sid) != SEGMENT:
                continue
            for e in seg.get("data", []):
                chemin = e.get("origins", [{}])[0].get("path", "")
                if e.get("type") == "ink-detection-downsampled" and "2.215um" in chemin:
                    brut = get(f"{BUCKET}/{chemin}", 180)
                    if brut is None:
                        return None
                    a = np.asarray(Image.open(io.BytesIO(brut)).convert("L"))
                    return (a > 0).astype(float)
    return None


def mesurer() -> dict:
    eti, seg = empreinte_etiquettes(), empreinte_segment()
    if eti is None or seg is None:
        raise SystemExit("empreinte absente : lancer d'abord le téléchargement du masque")
    a, b = _reduire(eti), _reduire(seg)
    # ⚠ ±12 cellules à 256 de côté, soit ±5 % de l'étendue : au-delà, deux silhouettes de
    # fragment ne se recouvrent plus par translation mais par coïncidence de forme.
    res = balayer(a, b, range(-12, 13))
    return dict(segment=SEGMENT,
                forme_etiquettes=list(eti.shape), forme_segment_reduit=list(seg.shape),
                aspect_etiquettes=eti.shape[0] / eti.shape[1],
                aspect_segment=seg.shape[0] / seg.shape[1],
                part_etiquettes=float((a > 0.5).mean()),
                part_segment=float((b > 0.5).mean()),
                cote=COTE, **res)


def _verifier(r: dict | None = None) -> int:
    echecs = comptes = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptes
        comptes += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ DICE PLUTÔT QUE « PART DE PIXELS ÉGAUX », testé sur le cas qui les sépare : deux
    # empreintes disjointes couvrant chacune un tiers de la grille s'accordent à 33 % par le
    # fond, et se recouvrent à 0.
    g = np.zeros((30, 30)); g[:10] = 1.0
    h = np.zeros((30, 30)); h[20:] = 1.0
    v("deux empreintes disjointes ont un Dice nul", dice(g, h) == 0.0, f"{dice(g, h):.3f}")
    v("... et deux identiques un Dice de 1", dice(g, g.copy()) == 1.0)
    v("... et un demi-recouvrement rend 0,5",
      abs(dice(np.r_[np.ones(20), np.zeros(20)].reshape(40, 1),
               np.r_[np.zeros(10), np.ones(20), np.zeros(10)].reshape(40, 1)) - 0.5) < 1e-9)
    v("deux empreintes vides ne divisent pas par zéro",
      dice(np.zeros((4, 4)), np.zeros((4, 4))) == 0.0)

    # ⚠⚠⚠ LE BALAYAGE DOIT RETROUVER UN DÉCALAGE CONNU, et ne rien inventer quand il n'y en a
    # pas. Sans ce second cas, un balayage qui rendrait toujours le meilleur coin passerait.
    base = np.zeros((40, 40)); base[10:20, 12:24] = 1.0
    bouge = np.roll(np.roll(base, 5, axis=0), -3, axis=1)
    b1 = balayer(base, bouge, range(-8, 9))
    v("le balayage retrouve un décalage connu", b1["decalage"] == [-5, 3],
      f"{b1['decalage']}, Dice {b1['dice_depart']:.2f} → {b1['dice_meilleur']:.2f}")
    b2 = balayer(base, base.copy(), range(-8, 9))
    v("... et n'en invente pas quand les deux coïncident déjà",
      b2["decalage"] == [0, 0] and b2["dice_meilleur"] == 1.0, str(b2["decalage"]))
    # ⚠ La bande qui a bouclé est annulée : sans ça, un décalage fabrique un recouvrement avec
    # le contenu revenu du bord opposé, et le balayage préfère les grands décalages.
    bord = np.zeros((40, 40)); bord[:4] = 1.0
    b3 = balayer(bord, bord.copy(), range(-8, 9))
    v("... et un décalage ne fabrique pas de recouvrement par le bord",
      b3["dice_meilleur"] == 1.0 and b3["decalage"] == [0, 0], str(b3))

    v("la réduction garde une empreinte non vide",
      _reduire(np.pad(np.ones((100, 100)), 50), 32).sum() > 0)

    if r:
        print("\net la mesure")
        print(f"      étiquettes {r['forme_etiquettes']} (aspect {r['aspect_etiquettes']:.4f}, "
              f"{100 * r['part_etiquettes']:.0f} % de la grille)")
        print(f"      segment    {r['forme_segment_reduit']} (aspect {r['aspect_segment']:.4f}, "
              f"{100 * r['part_segment']:.0f} %)")
        print(f"      Dice sans décalage {r['dice_depart']:.3f} → meilleur "
              f"{r['dice_meilleur']:.3f} au décalage {r['decalage']}")
        # ⚠⚠⚠ LE VERDICT DE FAISABILITÉ, ÉCRIT POUR TOMBER DANS LES DEUX SENS. Un recouvrement
        # franc dit que les deux aplatissements se ressemblent assez pour qu'un recalage fin
        # soit un lot défini ; un recouvrement faible dit qu'ils diffèrent par plus qu'une
        # similitude, et alors la case décisive demande un champ de déformation.
        v("les deux aplatissements se recouvrent franchement",
          r["dice_meilleur"] > 0.80,
          f"Dice {r['dice_meilleur']:.3f} — au-dessus de 0,80 un recalage fin est un lot "
          "défini ; en dessous il faut un champ de déformation")
        # ⚠⚠ ET LES RAPPORTS D'ASPECT DISENT SI UNE SIMILITUDE PEUT SUFFIRE : deux
        # aplatissements du même fragment qui n'ont pas le même rapport d'aspect ne se
        # déduisent pas l'un de l'autre par une échelle isotrope.
        ecart = abs(r["aspect_etiquettes"] / r["aspect_segment"] - 1.0)
        v("... et leurs rapports d'aspect sont compatibles avec une similitude",
          ecart < 0.05, f"{100 * ecart:.1f} % d'écart")

    print()
    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {comptes} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier and not a.json:
        cible = RACINE / "docs" / "mesures" / "deux_aplatissements.json"
        return 1 if _verifier(json.loads(cible.read_text()) if cible.is_file() else None) else 0
    r = mesurer()
    print(f"{r['segment']}")
    print(f"  étiquettes {r['forme_etiquettes']}  aspect {r['aspect_etiquettes']:.4f}")
    print(f"  segment    {r['forme_segment_reduit']}  aspect {r['aspect_segment']:.4f}")
    print(f"  Dice {r['dice_depart']:.3f} → {r['dice_meilleur']:.3f} au décalage {r['decalage']}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    if a.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
