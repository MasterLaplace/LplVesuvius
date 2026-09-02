#!/usr/bin/env python3
"""Deux maillages qui prétendent au même endroit y sont-ils ?

⚠⚠ POURQUOI. Une chaîne de projections et un bond direct de même longueur totale sont deux
manières d'atteindre le même point. Les comparer par leur **profil** demande deux rendus, et
[`44`](docs/44_ou_la_chaine_se_trouve.md) a mesuré que ce chemin échoue quand la distance
est assez grande pour que les deux soient déjà sorties de leur feuille : on oppose alors
« mauvais » à « irrendable ». La question « les deux atterrissent-elles au même endroit ? »
est plus élémentaire, et elle ne coûte **aucun rendu**.

⭐ Ce qui rend la comparaison possible : deux `tifxyz` issus d'une même source partagent leur
**paramétrisation**. Le point de grille (i, j) désigne le même point de la nappe de départ des
deux côtés, donc les apparier est légitime — et c'est la SEULE raison pour laquelle ça l'est.
Deux maillages de provenances différentes ne s'apparient pas par indice, et ce fichier
**refuse** de le faire (formes différentes ⇒ erreur).

⚠⚠ Un écart nu ne veut rien dire. « 4 voxels » est énorme si les deux maillages n'ont bougé
que de 4 voxels, et négligeable s'ils en ont parcouru 120. Le nombre qui porte le sens est donc
le **rapport à la longueur du déplacement** — d'où l'argument `--depuis`, qui nomme la source
commune. Sans elle, ce script imprime la distance et refuse d'en tirer un verdict.

⭐ Et l'écart se **décompose**, parce que deux échecs différents s'y cachent :

  - **le long** du déplacement : la chaîne avance un peu plus, ou un peu moins, loin que le
    bond. C'est un réglage de pas, pas une divergence — la feuille suivie est la même.
  - **en travers** : la chaîne a dérivé de côté. C'est le cisaillement, et c'est ce qui fait
    changer de feuille.

Les confondre ferait passer un décalage de calibration pour une perte de nappe, et l'inverse.

Usage :
    uv run python src/nappe/ecart_de_maillages.py A B --depuis SOURCE [--voxel-um 2.4]
    uv run python src/nappe/ecart_de_maillages.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sys
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from figure_commune import police  # noqa: E402

INVALIDE = 0.0


def lire(dossier: Path):
    """Les trois plans et la métadonnée d'un `tifxyz`."""
    import tifffile

    meta = json.loads((dossier / "meta.json").read_text(encoding="utf-8"))
    plans = {n: tifffile.imread(str(dossier / f"{n}.tif")) for n in ("x", "y", "z")}
    if len({a.shape for a in plans.values()}) != 1:
        raise ValueError(f"{dossier} : les trois images n'ont pas la même forme")
    return plans, meta




def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())


def valide(plans):
    return (plans["x"] > INVALIDE) & (plans["y"] > INVALIDE) & (plans["z"] > INVALIDE)


def ecart(a_plans, b_plans, source_plans=None) -> dict:
    """L'écart point à point entre deux maillages appariés par indice de grille.

    ⚠⚠ Seuls les points valides **des deux** côtés comptent. Un point absent d'un maillage
    n'est pas un accord à écart nul : c'est une absence, et la compter comme un zéro tirerait
    la médiane vers le bas d'autant plus fort que le maillage est troué — soit exactement la
    mauvaise direction.
    """
    import numpy as np

    formes = {a_plans["x"].shape, b_plans["x"].shape}
    if len(formes) != 1:
        raise ValueError(f"grilles de formes différentes : {formes} — non appariables")

    bon = valide(a_plans) & valide(b_plans)
    if source_plans is not None:
        if source_plans["x"].shape != a_plans["x"].shape:
            raise ValueError("la source n'a pas la forme des maillages comparés")
        bon = bon & valide(source_plans)
    n = int(bon.sum())
    if n == 0:
        raise ValueError("aucun point valide des deux côtés — rien à comparer")

    d = np.stack([b_plans[c][bon].astype(np.float64) - a_plans[c][bon].astype(np.float64)
                  for c in ("x", "y", "z")], axis=1)
    norme = np.linalg.norm(d, axis=1)
    r = {
        "points_compares": n,
        "points_grille": int(bon.size),
        "ecart_median_vox": float(np.median(norme)),
        "ecart_p90_vox": float(np.percentile(norme, 90)),
        "ecart_max_vox": float(norme.max()),
    }

    if source_plans is None:
        return r

    # ⭐ Le déplacement commun : de la source vers le premier maillage. C'est l'échelle à
    # laquelle l'écart doit être lu, et c'est ce qui transforme une distance en verdict.
    dep = np.stack([a_plans[c][bon].astype(np.float64) - source_plans[c][bon].astype(np.float64)
                    for c in ("x", "y", "z")], axis=1)
    longueur = np.linalg.norm(dep, axis=1)
    r["deplacement_median_vox"] = float(np.median(longueur))
    med_dep = r["deplacement_median_vox"]
    r["rapport_median"] = float(r["ecart_median_vox"] / med_dep) if med_dep > 0 else None

    # ⚠⚠ La décomposition. `axe` est la direction du déplacement en chaque point, donc la
    # projection de l'écart dessus est « la chaîne va-t-elle aussi loin » et le reste est
    # « la chaîne part-elle de côté ». Là où le déplacement est nul la direction n'existe
    # pas : ces points sont EXCLUS de la décomposition plutôt que projetés sur un axe
    # arbitraire, ce qui inventerait une dérive ou l'effacerait selon l'axe choisi.
    utile = longueur > 0
    if int(utile.sum()) == 0:
        return r
    axe = dep[utile] / longueur[utile][:, None]
    le_long = np.einsum("ij,ij->i", d[utile], axe)
    en_travers = np.linalg.norm(d[utile] - le_long[:, None] * axe, axis=1)
    r["points_decomposes"] = int(utile.sum())
    r["le_long_median_vox"] = float(np.median(le_long))
    r["en_travers_median_vox"] = float(np.median(en_travers))
    r["en_travers_p90_vox"] = float(np.percentile(en_travers, 90))
    return r


def en_micrometres(r: dict, voxel_um: float, spire_um: float | None = None) -> dict:
    """⚠ Un nombre appartient à sa géométrie de lecture. Les unités voyagent ensemble.

    ⚠⚠ D'OÙ `spire_um` DOIT VENIR, et c'est une correction du 2026-09-03. Un écart exprimé en
    spires est une DIVISION par ce nombre : un pas surestimé de 10 % fait lire 0,9 spire là où
    il y en a une. `espacement_spires.py` le mesurait par défaut au **niveau 2** de pyramide,
    qui fusionne des feuilles voisines et surestime donc le pas — le défaut est mesuré 36 fois
    sur 36 par `winding-ruler`. Son défaut est passé au niveau 1 ; un relevé antérieur se
    reconnaît à son champ `"level": 2` et **ne doit pas être passé ici tel quel**.

    ⭐ Et `spire_um` ajoute la seule unité qui rende un écart LISIBLE : la **spire**. « 8 µm »
    ne dit pas si deux maillages sont sur la même feuille ; « 0,05 spire » le dit. L'écart
    inter-spires est mesuré par `src/nappe/espacement_spires.py` et publié rouleau par
    rouleau dans [`16`](docs/16_carte_difficulte_rouleaux_du_prix.md).

    ⚠⚠ Il n'a AUCUN défaut, et c'est délibéré : une spire appartient à son rouleau — 150 µm
    pour `PHerc0125`, 225 pour `PHerc1667`. En défauter un attribuerait la géométrie d'un
    rouleau aux mesures d'un autre, silencieusement, et c'est exactement la classe d'erreur
    que ce dépôt paie le plus cher.
    """
    out = dict(r)
    out["voxel_um"] = voxel_um
    for cle in list(r):
        if cle.endswith("_vox"):
            out[cle[:-4] + "_um"] = r[cle] * voxel_um
    if spire_um:
        out["spire_um"] = spire_um
        for cle in list(r):
            if cle.endswith("_vox"):
                out[cle[:-4] + "_spires"] = r[cle] * voxel_um / spire_um
    return out


# ⚠⚠ La carte a besoin de l'écart PAR POINT, pas de ses quantiles. `ecart` rend des
# statistiques parce que c'est ce qu'un verdict demande ; `champ_ecart` rend la grille, parce
# qu'une moyenne ne dit pas OÙ deux maillages se séparent — et « partout un peu » et « beaucoup
# le long d'un pli » sont deux mécanismes différents qui donnent la même médiane.
def champ_ecart(a_plans, b_plans):
    """La grille des écarts point à point, et le masque des points comparables."""
    import numpy as np

    formes = {a_plans["x"].shape, b_plans["x"].shape}
    if len(formes) != 1:
        raise ValueError(f"grilles de formes différentes : {formes} — non appariables")
    bon = valide(a_plans) & valide(b_plans)
    champ = np.zeros(a_plans["x"].shape, dtype=np.float64)
    if bon.any():
        d = np.stack([b_plans[c][bon].astype(np.float64) - a_plans[c][bon].astype(np.float64)
                      for c in ("x", "y", "z")], axis=1)
        champ[bon] = np.linalg.norm(d, axis=1)
    return champ, bon


def concentration(champ, bon, part: float = 0.10) -> dict:
    """Le désaccord est-il RÉPARTI ou CONCENTRÉ, et sur quel axe de grille ?

    ⚠⚠ Deux mécanismes rendent la même médiane et demandent deux remèdes opposés. « Partout un
    peu » est une accumulation : elle se combat en raccourcissant le pas. « Beaucoup le long de
    quelques lignes » est une poignée de tangentes fausses : elle se combat en les **rejetant**,
    et raccourcir le pas n'y ferait rien.

    ⭐ Le nombre est directement lisible parce qu'il porte son propre témoin : sur un champ
    **uniforme**, le pire dixième des lignes porte exactement un dixième du total. Un 0,10 dit
    donc « réparti » et un 0,60 dit « six fois plus concentré qu'un hasard uniforme », sans
    qu'aucun seuil n'ait à être choisi.

    ⚠ Les deux axes sont rendus, jamais un seul : *lequel* concentre est le diagnostic. Une
    concentration le long de l'axe de projection et une concentration en travers de lui ne
    disent pas la même chose du champ de tangentes.
    """
    import numpy as np

    total = float(champ[bon].sum())
    out = {"total": total, "part_examinee": part}
    if total <= 0:
        out["lignes"] = out["colonnes"] = None
        return out
    for nom, axe in (("lignes", 1), ("colonnes", 0)):
        # Somme le long de `axe` : il reste un poids par ligne de l'AUTRE axe.
        poids = np.where(bon, champ, 0.0).sum(axis=axe)
        n = max(1, int(round(len(poids) * part)))
        pires = np.sort(poids)[::-1][:n]
        out[nom] = float(pires.sum() / total)
        out[nom + "_comptees"] = n
        out[nom + "_total"] = int(len(poids))
    return out


# ⚠ Le point où la question bascule : à une DEMI-spire, deux maillages sont plus près de deux
# feuilles différentes que de la même. C'est la seule graduation qui porte un sens physique,
# donc c'est celle que la carte trace.
DEMI_SPIRE = 0.5
ABSENT = (232, 228, 220)
FROID = (74, 132, 96)
CHAUD = (196, 72, 60)


def teinte(v: float, haut: float):
    """Du vert au rouge, saturé à `haut`. Le vert est « même feuille », le rouge « ailleurs »."""
    t = 0.0 if haut <= 0 else max(0.0, min(1.0, v / haut))
    return tuple(int(FROID[i] + (CHAUD[i] - FROID[i]) * t) for i in range(3))


def carte(a_plans, b_plans, sortie: Path, voxel_um: float,
          spire_um: float | None = None, zoom: int = 4, titre: str = "") -> dict:
    """Où, sur la nappe, les deux maillages se séparent.

    ⚠⚠ Un point ABSENT d'un des deux maillages est peint d'une teinte qui n'appartient pas au
    dégradé. Le peindre en vert le ferait lire comme un accord parfait — c'est-à-dire que les
    trous ressembleraient au meilleur résultat possible, ce qui est la pire confusion possible
    sur une carte de désaccord.
    """
    from PIL import Image, ImageDraw

    # ⚠ La police par défaut de PIL n'a ni flèche ni accent correctement espacé : la légende
    # sortait en « 0 ⊐ 0,686 » et « points au-delàd'une ». DejaVu est celle de toutes les
    # autres figures du dépôt, donc la carte se lit comme elles.
    g_titre, g_corps = police(13, 11)

    champ, bon = champ_ecart(a_plans, b_plans)
    unite = spire_um if spire_um else voxel_um
    # En spires si on en a une, sinon en voxels — et l'échelle le DIT dans sa légende.
    valeurs = champ * voxel_um / spire_um if spire_um else champ
    haut = max(1e-9, float(valeurs[bon].max()) if bon.any() else 1.0)

    h, w = champ.shape
    haut_titre = 26 if titre else 0
    lib = "spires" if spire_um else "voxels"
    au_dela = int((valeurs[bon] >= DEMI_SPIRE).sum()) if spire_um else 0
    legende = f"0 à {haut:.3f} {lib}".replace(".", ",")
    if spire_um:
        legende += f"   ·   {au_dela} points au-delà d'une demi-spire"
    # ⚠⚠ Le canevas est dimensionné pour CONTENIR sa légende, mesurée. Un libellé coupé est
    # invisible pour un contrôle qui ne regarde que des couleurs — et c'est exactement ce qui
    # est passé au premier tirage, où la carte annonçait « au-delà d'une demi- ».
    mes = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bar_x = 8 + 60 * 3 + 10
    besoin = bar_x + int(mes.textlength(legende, font=g_corps)) + 8
    if titre:
        besoin = max(besoin, 8 + int(mes.textlength(titre, font=g_titre)) + 8)
    im = Image.new("RGB", (max(w * zoom, besoin), h * zoom + haut_titre + 36),
                   (250, 249, 246))
    d = ImageDraw.Draw(im)
    if titre:
        d.text((8, 6), titre, font=g_titre, fill=(28, 30, 34))
    for r in range(h):
        for c in range(w):
            if not bon[r, c]:
                col = ABSENT
            else:
                col = teinte(float(valeurs[r, c]), haut)
            d.rectangle([c * zoom, r * zoom + haut_titre,
                         c * zoom + zoom - 1, r * zoom + haut_titre + zoom - 1], fill=col)
    y = h * zoom + haut_titre + 10
    for k in range(60):
        d.rectangle([8 + k * 3, y, 8 + k * 3 + 2, y + 10], fill=teinte(haut * k / 59, haut))
    d.text((bar_x, y - 2), legende, font=g_corps, fill=(90, 92, 96))
    depassement = max(0, bar_x + int(d.textlength(legende, font=g_corps)) - im.size[0])
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    # ⚠ La GRILLE est rapportée à part du canevas : le titre et la légende sont de la
    # décoration et peuvent bouger, « une case par point de grille » ne le peut pas. Un
    # contrôle écrit sur la taille du canevas se casse à chaque retouche de mise en page et
    # ne dit rien sur ce qui compte.
    return {"largeur": im.size[0], "hauteur": im.size[1],
            "grille_largeur": w * zoom, "grille_hauteur": h * zoom, "haut_echelle": haut,
            "depassement": int(depassement),
            "unite": lib, "points_absents": int((~bon).sum()),
            "points_au_dela_demi_spire": au_dela if spire_um else None}


def verifier() -> int:
    """Les témoins, sur des maillages fabriqués dont on connaît l'écart exact."""
    import shutil
    import tempfile

    import numpy as np
    import tifffile
    from PIL import Image

    echecs = controles = 0

    def v(nom, cond, det=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))

    lignes, colonnes = 7, 11
    gx = np.zeros((lignes, colonnes), dtype=np.float32)
    gy = np.zeros_like(gx)
    gz = np.full_like(gx, 500.0)
    for r_ in range(lignes):
        for c in range(colonnes):
            gx[r_, c] = 1000.0 + 10.0 * c
            gy[r_, c] = 2000.0 + 10.0 * r_
    src = {"x": gx, "y": gy, "z": gz}

    def decale(dx, dy, dz):
        return {"x": gx + dx, "y": gy + dy, "z": gz + dz}

    # Deux maillages IDENTIQUES : écart nul, partout.
    r = ecart(decale(30, 0, 0), decale(30, 0, 0), src)
    v("deux maillages identiques ont un écart nul", r["ecart_median_vox"] == 0.0)
    v("... et un écart maximal nul aussi", r["ecart_max_vox"] == 0.0)
    v("... et un rapport nul au déplacement", r["rapport_median"] == 0.0)
    v("tous les points sont comparés", r["points_compares"] == lignes * colonnes)

    # Un écart PUREMENT LE LONG : les deux ont avancé sur x, l'un de 30, l'autre de 34.
    r = ecart(decale(30, 0, 0), decale(34, 0, 0), src)
    v("un écart le long vaut sa différence", abs(r["ecart_median_vox"] - 4.0) < 1e-9)
    v("... et le déplacement vaut 30", abs(r["deplacement_median_vox"] - 30.0) < 1e-9)
    v("... et le rapport vaut 4/30", abs(r["rapport_median"] - 4.0 / 30.0) < 1e-9)
    v("... la composante le long porte tout", abs(r["le_long_median_vox"] - 4.0) < 1e-9)
    v("... et il n'y a AUCUNE dérive", abs(r["en_travers_median_vox"]) < 1e-9)
    # ⚠ Le signe compte : aller moins loin n'est pas aller plus loin.
    r2 = ecart(decale(30, 0, 0), decale(26, 0, 0), src)
    v("aller moins loin donne un le-long NÉGATIF", r2["le_long_median_vox"] < 0,
      str(r2["le_long_median_vox"]))

    # Un écart PUREMENT EN TRAVERS : même avance sur x, mais l'un a dérivé sur z.
    r = ecart(decale(30, 0, 0), decale(30, 0, 5), src)
    v("un écart en travers vaut sa dérive", abs(r["ecart_median_vox"] - 5.0) < 1e-9)
    v("... la composante le long est nulle", abs(r["le_long_median_vox"]) < 1e-9)
    v("... et la dérive porte tout", abs(r["en_travers_median_vox"] - 5.0) < 1e-9)

    # ⚠⚠ Le contrôle qui compte le plus : un point invalide n'est PAS un accord.
    a = decale(30, 0, 0)
    b = {k: arr.copy() for k, arr in decale(34, 0, 0).items()}
    for c in ("x", "y", "z"):
        b[c][0, 0] = INVALIDE
    r = ecart(a, b, src)
    v("un point invalide est EXCLU, pas compté à zéro",
      r["points_compares"] == lignes * colonnes - 1, str(r["points_compares"]))
    v("... et il ne tire pas la médiane vers zéro", abs(r["ecart_median_vox"] - 4.0) < 1e-9)
    v("la grille entière reste rapportée", r["points_grille"] == lignes * colonnes)

    # Des grilles de formes différentes ne s'apparient pas.
    autre = {c: np.zeros((3, 3), dtype=np.float32) + 1.0 for c in ("x", "y", "z")}
    try:
        ecart(a, autre)
        v("deux formes différentes sont refusées", False)
    except ValueError:
        v("deux formes différentes sont refusées", True)

    # Aucun point valide des deux côtés.
    vide = {c: np.zeros((lignes, colonnes), dtype=np.float32) for c in ("x", "y", "z")}
    try:
        ecart(a, vide)
        v("aucun point commun est refusé", False)
    except ValueError:
        v("aucun point commun est refusé", True)

    # Sans source, pas de verdict — la distance seule ne dit rien.
    r = ecart(a, decale(34, 0, 0))
    v("sans source, l'écart est mesuré", abs(r["ecart_median_vox"] - 4.0) < 1e-9)
    v("... mais AUCUN rapport n'est annoncé", "rapport_median" not in r)
    v("... et aucune décomposition non plus", "le_long_median_vox" not in r)

    # ⚠ Un déplacement nul n'a pas de direction : la décomposition doit s'abstenir.
    r = ecart(src, decale(0, 0, 3), src)
    v("un déplacement nul ne fabrique pas d'axe", "le_long_median_vox" not in r,
      str(r.get("le_long_median_vox")))

    # Les deux unités voyagent ensemble.
    u = en_micrometres({"ecart_median_vox": 4.0, "points_compares": 7}, 2.4)
    v("l'écart est converti en µm", abs(u["ecart_median_um"] - 9.6) < 1e-9)
    v("... la valeur en voxels reste", u["ecart_median_vox"] == 4.0)
    v("... la taille du voxel est écrite", u["voxel_um"] == 2.4)
    v("... et un compte n'est PAS converti", "points_compares_um" not in u)

    # ⭐ La lecture en SPIRES, la seule qui dise si deux maillages sont sur la même feuille.
    u = en_micrometres({"ecart_median_vox": 4.0, "points_compares": 7}, 2.4, spire_um=173.0)
    v("l'écart est aussi lu en spires",
      abs(u["ecart_median_spires"] - 9.6 / 173.0) < 1e-12, str(u.get("ecart_median_spires")))
    v("... et la spire employée est écrite", u["spire_um"] == 173.0)
    # ⚠⚠ Sans spire déclarée, AUCUNE lecture en spires. Un rouleau a la sienne — 150 µm pour
    # PHerc0125, 225 pour PHerc1667 — et en défauter une attribuerait la géométrie d'un
    # rouleau aux mesures d'un autre.
    u = en_micrometres({"ecart_median_vox": 4.0}, 2.4)
    v("sans spire déclarée, aucune lecture en spires", "ecart_median_spires" not in u)
    u = en_micrometres({"ecart_median_vox": 4.0}, 2.4, spire_um=0.0)
    v("une spire nulle n'invente pas de division", "ecart_median_spires" not in u)

    # ⚠⚠ LA CARTE. Elle existe parce qu'une médiane ne dit pas OÙ deux maillages se séparent,
    # et « partout un peu » et « beaucoup le long d'un pli » sont deux mécanismes différents
    # qui rendent la même médiane.
    import numpy as _np
    a2 = decale(30, 0, 0)
    b2 = {c: arr.copy() for c, arr in decale(30, 0, 0).items()}
    b2["z"][3, 5] += 100.0          # un seul point qui s'écarte
    ch, bo = champ_ecart(a2, b2)
    v("le champ isole le point qui s'écarte", abs(ch[3, 5] - 100.0) < 1e-9, str(ch[3, 5]))
    v("... et laisse les autres à zéro", float(ch.sum()) == float(ch[3, 5]))
    v("le masque couvre toute la grille", int(bo.sum()) == lignes * colonnes)
    for c in ("x", "y", "z"):
        b2[c][0, 0] = INVALIDE
    ch, bo = champ_ecart(a2, b2)
    v("un point invalide sort du masque", not bool(bo[0, 0]))
    v("... et son écart n'est pas inventé", ch[0, 0] == 0.0)
    # ⚠ Le dégradé est SATURÉ : au-delà du haut de l'échelle il ne devient pas plus rouge, et
    # en dessous de zéro pas plus vert. Sondé aux deux bouts.
    v("le bas du dégradé est le froid", teinte(0.0, 10.0) == FROID)
    v("le haut du dégradé est le chaud", teinte(10.0, 10.0) == CHAUD)
    v("au-delà, ça sature", teinte(1000.0, 10.0) == CHAUD)
    v("une échelle nulle ne divise pas par zéro", teinte(5.0, 0.0) == FROID)
    # ⚠⚠ La couleur des ABSENTS n'appartient PAS au dégradé. Sinon un trou se lirait comme
    # l'accord parfait — la pire confusion possible sur une carte de désaccord.
    degrade = {teinte(k / 40.0, 1.0) for k in range(41)}
    v("la teinte des absents n'est pas dans le dégradé", ABSENT not in degrade)

    # ⚠⚠ CONCENTRATION : le témoin est dans le nombre lui-même. Un champ uniforme met un
    # dixième du total dans le pire dixième des lignes, donc 0,10 signifie « réparti » sans
    # qu'aucun seuil n'ait été choisi. Sondé sur trois champs dont on connaît la réponse.
    uni = _np.ones((10, 10))
    tout = _np.ones((10, 10), dtype=bool)
    c = concentration(uni, tout)
    v("un champ uniforme concentre un dixième", abs(c["lignes"] - 0.10) < 1e-9,
      str(c["lignes"]))
    v("... sur les deux axes", abs(c["colonnes"] - 0.10) < 1e-9)
    v("... et une ligne est comptée par dixième", c["lignes_comptees"] == 1)
    raie = _np.zeros((10, 10))
    raie[:, 3] = 1.0                       # UNE colonne porte tout
    c = concentration(raie, tout)
    v("une raie verticale concentre sur les colonnes", abs(c["colonnes"] - 1.0) < 1e-9,
      str(c["colonnes"]))
    # ⚠ Et pas sur l'autre axe : chaque ligne en reçoit autant, donc le pire dixième des
    # lignes n'en porte qu'un dixième. C'est ce qui rend les deux nombres discriminants.
    v("... et pas sur les lignes", abs(c["lignes"] - 0.10) < 1e-9, str(c["lignes"]))
    c = concentration(raie.T, tout)
    v("une raie horizontale concentre sur les lignes", abs(c["lignes"] - 1.0) < 1e-9)
    # ⚠⚠ Les points hors masque ne comptent pas — sinon un maillage troué paraîtrait réparti.
    masque = tout.copy()
    masque[:, 3] = False
    c = concentration(raie, masque)
    v("un champ dont tout le poids est masqué a un total nul", c["total"] == 0.0)
    v("... et n'annonce aucune concentration", c["lignes"] is None)

    racine4 = Path(tempfile.mkdtemp(prefix="carte_temoins_"))
    f = racine4 / "carte.png"
    r = carte(a2, b2, f, voxel_um=2.4, spire_um=173.0, zoom=3)
    v("la carte est écrite", f.is_file() and f.stat().st_size > 0)
    # ⚠ L'invariant est « une case par point de grille », PAS la taille du canevas : le
    # titre et la légende sont de la décoration, et un contrôle écrit sur leur hauteur se
    # casse à chaque retouche sans rien dire de ce qui compte.
    v("la grille a une case par point de grille",
      r["grille_largeur"] == colonnes * 3 and r["grille_hauteur"] == lignes * 3,
      f"{r['grille_largeur']}x{r['grille_hauteur']}")
    v("... et le canevas la contient entièrement",
      r["largeur"] >= r["grille_largeur"] and r["hauteur"] > r["grille_hauteur"])
    v("le trou est compté comme absent", r["points_absents"] == 1)
    # 100 voxels × 2,4 = 240 µm, soit 1,387 spire : au-delà d'une demi-spire.
    v("l'unité est la spire quand elle est donnée", r["unite"] == "spires")
    v("le point qui s'écarte dépasse la demi-spire",
      r["points_au_dela_demi_spire"] == 1, str(r["points_au_dela_demi_spire"]))
    px = _pixels(Image.open(f).convert("RGB"))
    v("la teinte des absents est bien peinte", ABSENT in px)
    # ⚠⚠ La légende ne doit pas être COUPÉE. Un libellé tronqué est invisible pour un contrôle
    # qui ne regarde que des couleurs, et le premier tirage annonçait « au-delà d'une demi- ».
    v("la légende tient dans le canevas", r["depassement"] == 0, f"{r['depassement']} px")
    long_titre = carte(a2, b2, racine4 / "titre.png", voxel_um=2.4, spire_um=173.0, zoom=1,
                       titre="un titre volontairement très long pour déborder du canevas")
    v("... même avec un titre plus large que la grille", long_titre["depassement"] == 0)
    v("... et le canevas s'élargit alors", long_titre["largeur"] > colonnes)
    # ⚠ Sans spire, la carte se lit en voxels et n'annonce AUCUN franchissement : « une demi-
    # spire » n'a pas de sens sans spire, et l'annoncer quand même serait un nombre sans unité.
    r2 = carte(a2, b2, racine4 / "vox.png", voxel_um=2.4, zoom=2)
    v("sans spire, la carte se lit en voxels", r2["unite"] == "voxels")
    v("... et n'annonce aucun franchissement",
      r2["points_au_dela_demi_spire"] is None)
    shutil.rmtree(racine4, ignore_errors=True)

    # Le tour complet par le disque, sur de vrais fichiers.
    racine = Path(tempfile.mkdtemp(prefix="ecart_temoins_"))
    for nom, plans in (("src", src), ("a", decale(30, 0, 0)), ("b", decale(34, 0, 0))):
        d = racine / nom
        d.mkdir()
        for c in ("x", "y", "z"):
            tifffile.imwrite(str(d / f"{c}.tif"), plans[c].astype(np.float32))
        (d / "meta.json").write_text(json.dumps({"scale": [0.05, 0.05], "uuid": nom}),
                                     encoding="utf-8")
    pa, _ = lire(racine / "a")
    pb, _ = lire(racine / "b")
    ps, _ = lire(racine / "src")
    r = ecart(pa, pb, ps)
    v("le tour par le disque donne le même écart", abs(r["ecart_median_vox"] - 4.0) < 1e-9)
    shutil.rmtree(racine, ignore_errors=True)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("a", nargs="?", type=Path, help="premier maillage (tifxyz)")
    p.add_argument("b", nargs="?", type=Path, help="second maillage (tifxyz)")
    p.add_argument("--depuis", type=Path,
                   help="la source commune — sans elle, aucun rapport n'est annoncé")
    p.add_argument("--voxel-um", type=float, default=2.4,
                   help="taille du voxel du maillage (défaut : niveau 0 du scan)")
    p.add_argument("--spire-um", type=float,
                   help="l'écart inter-spires du rouleau (docs/16) — sans lui, aucune "
                        "lecture en spires n'est annoncée")
    p.add_argument("--carte", type=Path,
                   help="une carte du désaccord, un point de grille par case")
    p.add_argument("--zoom", type=int, default=4, help="cases par point de grille")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()

    if a.verifier:
        return verifier()
    if not a.a or not a.b:
        p.error("deux maillages sont requis")

    pa, _ = lire(a.a)
    pb, _ = lire(a.b)
    ps = lire(a.depuis)[0] if a.depuis else None
    r = en_micrometres(ecart(pa, pb, ps), a.voxel_um, a.spire_um)
    r["a"] = a.a.name
    r["b"] = a.b.name
    r["depuis"] = a.depuis.name if a.depuis else None

    print(f"{a.a.name}  contre  {a.b.name}"
          + (f"   (depuis {a.depuis.name})" if a.depuis else ""))
    print(f"  points comparés     {r['points_compares']} / {r['points_grille']}")
    print(f"  écart médian        {r['ecart_median_vox']:.3f} vox   "
          f"{r['ecart_median_um']:.1f} µm")
    print(f"  écart p90           {r['ecart_p90_vox']:.3f} vox   {r['ecart_p90_um']:.1f} µm")
    print(f"  écart max           {r['ecart_max_vox']:.3f} vox   {r['ecart_max_um']:.1f} µm")
    if "deplacement_median_vox" in r:
        print(f"  déplacement médian  {r['deplacement_median_vox']:.3f} vox   "
              f"{r['deplacement_median_um']:.1f} µm")
        print(f"  ⭐ rapport           {r['rapport_median'] * 100:.2f} % du déplacement")
    if "ecart_median_spires" in r:
        print(f"  ⭐ en spires         médian {r['ecart_median_spires']:.3f}   "
              f"p90 {r['ecart_p90_spires']:.3f}   max {r['ecart_max_spires']:.3f}"
              f"   (spire = {r['spire_um']:.0f} µm)")
    if "le_long_median_vox" in r:
        print(f"  le long             {r['le_long_median_vox']:+.3f} vox   "
              f"{r['le_long_median_um']:+.1f} µm")
        print(f"  en travers          {r['en_travers_median_vox']:.3f} vox   "
              f"{r['en_travers_median_um']:.1f} µm   "
              f"(p90 {r['en_travers_p90_um']:.1f} µm)")
    else:
        print("  ⚠ aucun rapport : la source commune n'a pas été donnée (--depuis)")

    if a.carte:
        c = carte(pa, pb, a.carte, a.voxel_um, a.spire_um, a.zoom,
                  titre=f"où {a.a.name} et {a.b.name} se séparent")
        r["carte"] = str(a.carte)
        r["points_absents"] = c["points_absents"]
        r["points_au_dela_demi_spire"] = c["points_au_dela_demi_spire"]
        ch, bo = champ_ecart(pa, pb)
        co = concentration(ch, bo)
        r["concentration"] = co
        if co.get("lignes") is not None:
            print(f"  ⭐ concentration     le pire dixième des colonnes porte "
                  f"{co['colonnes'] * 100:.0f} % du désaccord, "
                  f"des lignes {co['lignes'] * 100:.0f} %   (uniforme = 10 %)")
        print(f"  carte : {a.carte}  (échelle 0 → {c['haut_echelle']:.3f} {c['unite']}"
              + (f", {c['points_au_dela_demi_spire']} points au-delà d'une demi-spire"
                 if c["points_au_dela_demi_spire"] is not None else "") + ")")

    if a.json:
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
