#!/usr/bin/env python3
"""Recoller une nappe projetée sur la MATIÈRE, point par point.

⚠⚠ POURQUOI. [`44`](../docs/44_ou_la_chaine_se_trouve.md) §7 mesure qu'une chaîne tangentielle
**purement géométrique** a un horizon : six maillons, ~580 µm, puis son pas s'emballe et le
maillage se détruit. 580 µm est le centième d'un tour de nappe, donc la géométrie seule ne fera
jamais le tour d'une feuille. Ce qui manque n'est pas un meilleur pas — c'est de **redemander à
la donnée où la feuille se trouve** entre deux projections.

⭐ Et ce geste est déjà mesuré ailleurs, sur un autre objet :
[`41`](../docs/41_marcher_le_long_dune_nappe.md) §6 marche une nappe par transformée de distance
et recentrage sur la crête, et va jusqu'à ce que le **bloc se termine**. Ce fichier applique ce
même geste, non plus à une ligne de 283 points, mais à **chaque point** d'une nappe.

⚠⚠ Les deux moitiés viennent d'endroits différents **exprès** :

  - la **normale** vient du MAILLAGE (produit vectoriel de ses deux tangentes), pas du tenseur
    de structure. Demander à la donnée dans quelle direction la feuille fait face, puis lui
    demander où est sa crête *le long de cette direction*, serait circulaire — et sur un masque
    binaire le tenseur de structure ne voit rien à l'intérieur de la matière, ce que `41` §6
    a payé ;
  - la **crête** vient de la DONNÉE (`champ_de_distance` + `recentrer` de `suivre_nappe`), et
    d'elle seule.

⚠⚠ LE NIVEAU DE PYRAMIDE EST UN ARGUMENT SANS DÉFAUT. Le maillage est en coordonnées de scan
(niveau 0) et la prédiction téléchargée ici est au niveau 2 : lire l'un dans l'autre sans
diviser désigne un point quatre fois plus proche de l'origine, dans le vide. C'est exactement
ce qui a produit treize rendus noirs (`54`), et le remède est que le niveau soit nommé.

⚠ Ce fichier **ne garantit pas** que le recalage tombe sur la BONNE feuille. Il tombe sur la
crête la plus proche le long de la normale, dans une portée bornée ; c'est tout ce qu'une
mesure locale peut promettre. La portée est donc bornée **sous la demi-spire**, sinon un point
peut se recaler sur la feuille voisine — la panne exacte que `41` §2 mesure pour « au plus
proche » (5,9 voxels d'écart contre 0,67 pour la marche).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

INVALIDE = 0.0


def normales(plans):
    """La normale unitaire en chaque point : le produit vectoriel des deux tangentes.

    ⚠ Les tangentes viennent de `projeter_tangentiel.tangentes`, donc elles portent déjà sa
    règle : différence centrée là où les deux voisins existent, décentrée au bord, et **rien**
    là où aucun voisin n'est valide. Une normale calculée à travers un trou serait la normale
    de la corde entre deux morceaux de nappe séparés.
    """
    import numpy as np
    import projeter_tangentiel as pt

    tu, ok_u = pt.tangentes(plans, 0)
    tv, ok_v = pt.tangentes(plans, 1)
    n = np.cross(tu, tv)
    norme = np.linalg.norm(n, axis=2)
    ok = ok_u & ok_v & (norme > 1e-9)
    n = np.divide(n, norme[..., None], out=np.zeros_like(n), where=(norme > 1e-9)[..., None])
    return n, ok


def bornes(plans, valide_masque, niveau: int, marge: float):
    """La boîte du maillage dans le repère du NIVEAU demandé, marge comprise."""
    import numpy as np

    ech = 1 << niveau
    bas, haut = [], []
    for nom in ("z", "y", "x"):
        v = plans[nom][valide_masque].astype(np.float64) / ech
        bas.append(int(np.floor(v.min() - marge)))
        haut.append(int(np.ceil(v.max() + marge)) + 1)
    return bas, haut


def recaler(plans, racine_zarr: Path, niveau: int, portee: float = 4.0,
            pas: float = 0.25, spire_um: float | None = None,
            voxel_um: float = 2.4) -> tuple[dict, dict]:
    """Chaque point valide, ramené sur la crête locale le long de sa propre normale.

    ⚠⚠ Un point est **laissé où il est** — jamais déplacé au hasard — dans trois cas, et les
    trois sont comptés séparément parce qu'ils veulent dire trois choses différentes : il est
    hors de la boîte téléchargée, il n'y a pas de matière autour de lui, ou la crête trouvée
    est **au bord de la portée** (auquel cas le vrai maximum est peut-être plus loin, donc
    celui-là n'est pas un maximum mais une borne).
    """
    import numpy as np
    import region_locale as rl
    import suivre_nappe as sn

    ech = float(1 << niveau)
    # ⚠ La portée est exprimée en voxels DU NIVEAU, comme tout ce qui touche le bloc.
    if spire_um:
        # ⚠⚠ Le garde-fou qui empêche de changer de feuille : une portée d'une demi-spire ou
        # plus permet à un point d'atteindre la nappe voisine, et rien en aval ne le verrait.
        demi = 0.5 * spire_um / voxel_um / ech
        if portee >= demi:
            raise ValueError(
                f"portée {portee:g} ≥ demi-spire {demi:.2f} voxels de niveau {niveau} — "
                f"un point pourrait se recaler sur la feuille voisine")

    bon = ((plans["x"] > INVALIDE) & (plans["y"] > INVALIDE) & (plans["z"] > INVALIDE))
    n, ok_n = normales(plans)
    bas, haut = bornes(plans, bon, niveau, portee + 2.0)
    bloc, info = rl.lire_region(racine_zarr, niveau, bas, haut)
    champ = sn.champ_de_distance(bloc)
    plancher = sn.plancher_pour(champ)

    sortie = {c: plans[c].copy() for c in ("x", "y", "z")}
    comptes = {"recales": 0, "hors_boite": 0, "sans_matiere": 0, "borne_atteinte": 0,
               "sans_normale": 0, "points": int(bon.sum())}
    deplacements = []
    cretes = []
    signes = []
    o = info["origine"]
    forme = champ.shape
    rs, cs = np.nonzero(bon)
    for r, c in zip(rs.tolist(), cs.tolist()):
        if not ok_n[r, c]:
            comptes["sans_normale"] += 1
            continue
        p = np.array([float(plans["z"][r, c]) / ech - o[0],
                      float(plans["y"][r, c]) / ech - o[1],
                      float(plans["x"][r, c]) / ech - o[2]])
        if not all(portee + 1.0 <= p[i] < forme[i] - portee - 1.0 for i in range(3)):
            comptes["hors_boite"] += 1
            continue
        # La normale du maillage est en (x, y, z) ; le bloc est indexé (z, y, x). Une
        # homothétie uniforme ne change pas une direction, donc seul l'ORDRE des axes bouge.
        nb = np.array([float(n[r, c, 2]), float(n[r, c, 1]), float(n[r, c, 0])])
        q, t, val = sn.recentrer(champ, p, nb, portee=portee, pas=pas)
        if val < plancher:
            comptes["sans_matiere"] += 1
            continue
        if abs(abs(t) - portee) < pas / 2.0:
            comptes["borne_atteinte"] += 1
            continue
        comptes["recales"] += 1
        # ⚠⚠ LE DIAGNOSTIC QUI DIT SI ON PEUT CROIRE LE RESTE : la HAUTEUR de la crête sur
        # laquelle on vient de se poser. Le champ de distance rend à chaque voxel de matière
        # sa distance au vide, donc la valeur au sommet **est** la demi-épaisseur locale de la
        # nappe. Une crête à 1,0 veut dire une nappe d'un voxel : il n'y a pas de sommet à
        # localiser, et `argmax` rend le premier indice d'un plateau — la panne que `41` §6
        # décrit pour un masque binaire, et qui revient dès qu'on lit trop grossièrement.
        #
        # ⚠ Mon PREMIER indicateur était faux et la batterie l'a dit : je comptais les `t`
        # tombant sur un multiple du pas, en croyant y voir un plateau. C'est aussi, et
        # surtout, ce que rend un pic parfaitement SYMÉTRIQUE — donc l'indicateur accusait le
        # cas le plus sain. La hauteur, elle, ne se trompe pas de cas.
        cretes.append(float(val))
        deplacements.append(abs(t) * ech)
        # ⚠⚠ LE SIGNE, et il sépare deux mondes. Des déplacements SYMÉTRIQUES autour de zéro
        # disent « chaque point se recale un peu, dans un sens ou l'autre » — un affinage. Des
        # déplacements tous du MÊME côté disent que la prédiction est **décalée** par rapport
        # au maillage, et recaler dessus déplacerait alors la nappe entière d'un biais
        # systématique en croyant l'affiner. Ne garder que la valeur absolue rendrait les deux
        # cas identiques à la lecture.
        signes.append(float(t) * ech)
        # ⚠ Le déplacement `t` est en voxels DU NIVEAU : le remonter en coordonnées de scan
        # demande de le remultiplier. L'oublier recalerait de quatre fois trop peu.
        sortie["x"][r, c] = plans["x"][r, c] + t * ech * float(n[r, c, 0])
        sortie["y"][r, c] = plans["y"][r, c] + t * ech * float(n[r, c, 1])
        sortie["z"][r, c] = plans["z"][r, c] + t * ech * float(n[r, c, 2])

    if deplacements:
        d = np.array(deplacements)
        comptes["deplacement_median_vox"] = float(np.median(d))
        comptes["deplacement_p90_vox"] = float(np.percentile(d, 90))
        comptes["deplacement_max_vox"] = float(d.max())
    if signes:
        sg = np.array(signes)
        comptes["deplacement_signe_median_vox"] = float(np.median(sg))
        comptes["part_vers_le_plus"] = float((sg > 0).mean())
    if cretes:
        cr = np.array(cretes)
        comptes["crete_mediane"] = float(np.median(cr))
        comptes["crete_p10"] = float(np.percentile(cr, 10))
    comptes["champ_max"] = float(champ.max())
    comptes.update({"niveau": niveau, "portee_niveau": portee,
                    "bloc": info["forme_lue"], "chunks_absents": info["chunks_absents"]})
    return sortie, comptes


def decaler(plans, dz: float, dy: float, dx: float):
    """La même nappe, translatée en bloc. Sa forme est intacte, sa place ne l'est plus."""
    out = {c: a.copy() for c, a in plans.items()}
    bon = ((plans["x"] > INVALIDE) & (plans["y"] > INVALIDE) & (plans["z"] > INVALIDE))
    for c, d in (("x", dx), ("y", dy), ("z", dz)):
        out[c][bon] = plans[c][bon] + d
    return out


def plancher_de_hasard(plans, racine_zarr: Path, niveau: int, portee: float,
                       rayon_vox: float, tirages: int = 3, graine: int = 20260825,
                       spire_um: float | None = None, voxel_um: float = 2.4) -> dict:
    """⚠⚠ LE TÉMOIN NÉGATIF, et sans lui aucun « % posé » n'est interprétable.

    Une nappe **posée n'importe où** dans un volume dont un quart des voxels est de la matière
    trouve forcément quelque chose sous une partie de ses points. Tant qu'on ne sait pas
    combien, « 35 % posé » peut vouloir dire « à moitié perdue » comme « complètement
    perdue » — et c'est exactement la différence qui décide si une chaîne a encore un sens à
    cette distance.

    ⭐ La mesure : la MÊME nappe, translatée en bloc de `rayon_vox` dans une direction tirée
    au sort, plusieurs fois. Sa forme, sa densité de points et son échantillonnage sont
    identiques ; seule sa place est fausse. Ce qu'elle lit alors est le plancher.

    ⚠ Plusieurs tirages, pas un : une translation unique peut atterrir sur une feuille par
    chance, et un plancher mesuré une fois serait un plancher tiré au sort. La graine est
    fixée pour que le nombre publié se rejoue.
    """
    import numpy as np

    rng = np.random.default_rng(graine)
    parts, details = [], []
    for i in range(tirages):
        v = rng.normal(size=3)
        v = v / (np.linalg.norm(v) or 1.0) * rayon_vox
        try:
            _, c = recaler(decaler(plans, float(v[0]), float(v[1]), float(v[2])),
                           racine_zarr, niveau, portee, spire_um=spire_um, voxel_um=voxel_um)
        except ValueError:
            # ⚠ Une translation qui sort du tableau n'est pas un plancher : elle est sautée
            # et comptée, sinon le plancher serait tiré vers zéro par des tirages hors volume.
            details.append({"tirage": i, "hors_volume": True})
            continue
        interroges = c["points"] - c["hors_boite"]
        part = (c["recales"] + c["borne_atteinte"]) / interroges if interroges > 0 else 0.0
        parts.append(part)
        details.append({"tirage": i, "decalage_vox": [round(float(x), 1) for x in v],
                        "part_posee": round(part, 4), "hors_boite": c["hors_boite"]})
    return {"tirages": tirages, "retenus": len(parts), "rayon_vox": rayon_vox,
            "plancher_median": float(np.median(parts)) if parts else None,
            "plancher_max": float(max(parts)) if parts else None, "details": details}


def verifier() -> int:
    """Les témoins, sur une dalle fabriquée dont on connaît l'axe médian au voxel près."""
    import shutil
    import tempfile

    import numpy as np

    import region_locale as rl

    echecs = controles = 0

    def v(nom, cond, det=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))

    # Une DALLE horizontale : matière pour z dans [28, 36], donc axe médian à z = 32.
    racine = Path(tempfile.mkdtemp(prefix="recaler_temoins_"))
    n, c = 64, 64
    d = racine / "0"
    d.mkdir(parents=True)
    (d / ".zarray").write_text(json.dumps(
        {"shape": [n, n, n], "chunks": [c, c, c], "dtype": "|u1", "compressor": None,
         "fill_value": 0, "dimension_separator": "/"}), encoding="utf-8")
    vol = np.zeros((n, n, n), dtype=np.uint8)
    vol[28:37, :, :] = 255
    (d / "0/0").mkdir(parents=True)
    (d / "0/0/0").write_bytes(vol.tobytes())

    # Un maillage PLAT posé à z = 29, soit trois voxels sous l'axe médian de la dalle.
    lignes, colonnes = 5, 7
    gx = np.zeros((lignes, colonnes), dtype=np.float32)
    gy = np.zeros_like(gx)
    gz = np.full_like(gx, 29.0)
    for r in range(lignes):
        for cc in range(colonnes):
            gx[r, cc] = 20.0 + 2.0 * cc
            gy[r, cc] = 20.0 + 2.0 * r
    plans = {"x": gx, "y": gy, "z": gz}

    nrm, okn = normales(plans)
    # ⚠ Une nappe plate dans le plan (x, y) a une normale purement en z. La vérifier ici est ce
    # qui rend le recalage interprétable : un recalage le long d'une mauvaise normale bougerait
    # les points DANS la feuille au lieu de les traverser.
    v("la normale d'une nappe plate est portée par z",
      abs(abs(float(nrm[2, 3, 2])) - 1.0) < 1e-6, str(nrm[2, 3]))
    v("... et les deux autres composantes sont nulles",
      abs(float(nrm[2, 3, 0])) < 1e-6 and abs(float(nrm[2, 3, 1])) < 1e-6)
    v("tous les points ont une normale", bool(okn.all()))

    sortie, cpt = recaler(plans, racine, 0, portee=6.0, pas=0.25)
    # ⚠⚠ LE CONTRÔLE QUI PORTE LE FICHIER : le maillage est parti de z = 29 et l'axe médian
    # de la dalle est à z = 32. Un recalage qui ne bouge rien, ou qui bouge dans le mauvais
    # sens, échoue ici — et une simple assertion « ça a bougé » ne l'aurait pas vu.
    v("tous les points sont recalés", cpt["recales"] == lignes * colonnes,
      str(cpt))
    zz = sortie["z"]
    v("... sur l'axe médian de la dalle", abs(float(np.median(zz)) - 32.0) < 0.3,
      str(float(np.median(zz))))
    v("... et le déplacement médian vaut les trois voxels attendus",
      abs(cpt["deplacement_median_vox"] - 3.0) < 0.3,
      str(cpt.get("deplacement_median_vox")))
    v("x et y ne bougent pas", bool(np.allclose(sortie["x"], gx))
      and bool(np.allclose(sortie["y"], gy)))
    # ⚠⚠ Le SIGNE : la dalle est au-dessus du maillage, donc TOUS les points montent. C'est
    # le cas « biais », et il doit se lire comme tel — sinon un décalage systématique de la
    # prédiction passerait pour un affinage point par point.
    v("un décalage systématique est vu comme un biais",
      cpt["part_vers_le_plus"] > 0.99 or cpt["part_vers_le_plus"] < 0.01,
      str(cpt["part_vers_le_plus"]))
    v("... et la médiane signée porte les trois voxels",
      abs(abs(cpt["deplacement_signe_median_vox"]) - 3.0) < 0.3,
      str(cpt["deplacement_signe_median_vox"]))

    # ⚠ Un point posé DANS LE VIDE n'est pas déplacé au hasard : il est compté.
    vide = {c2: a.copy() for c2, a in plans.items()}
    vide["z"][:] = 10.0
    _, cv = recaler(vide, racine, 0, portee=3.0, pas=0.25)
    v("un maillage dans le vide n'est pas recalé", cv["recales"] == 0, str(cv))
    v("... et c'est compté comme absence de matière",
      cv["sans_matiere"] == lignes * colonnes, str(cv["sans_matiere"]))

    # ⚠⚠ La BORNE : une dalle hors de portée ne doit pas être atteinte de justesse. À portée
    # 1, l'axe est à trois voxels, donc chaque point bute sur la borne et est REFUSÉ plutôt
    # que déplacé d'un voxel dans la bonne direction — un point qui bute n'a pas trouvé un
    # maximum, il a trouvé le bord de sa fenêtre.
    _, cb = recaler(plans, racine, 0, portee=1.0, pas=0.25)
    v("un maximum au bord de la portée est refusé", cb["recales"] == 0, str(cb))
    v("... et compté comme borne atteinte", cb["borne_atteinte"] == lignes * colonnes,
      str(cb["borne_atteinte"]))

    # ⚠⚠ Hors de la boîte : compté, pas déplacé. Et le cas ne se fabrique PAS en éloignant le
    # maillage — la boîte est dérivée de son propre englobant, donc il est toujours dedans. Il
    # faut le poser au bord du VOLUME, là où l'écrêtage mord. Ma première version aplatissait
    # x à une constante : ça détruit la tangente le long des colonnes, donc le compte tombait
    # dans `sans_normale` et le contrôle mesurait autre chose que son nom.
    loin = {c2: a.copy() for c2, a in plans.items()}
    loin["z"][:] = 2.0
    _, cl = recaler(loin, racine, 0, portee=6.0, pas=0.25)
    v("un point trop près du bord du VOLUME est hors boîte",
      cl["hors_boite"] == lignes * colonnes, str(cl))
    v("... et pas rangé dans un autre compte", cl["sans_normale"] == 0)

    # ⚠⚠ LE GARDE-FOU DE LA DEMI-SPIRE, sondé dans les deux sens.
    try:
        recaler(plans, racine, 0, portee=40.0, spire_um=173.0, voxel_um=2.4)
        v("une portée d'une demi-spire est refusée", False)
    except ValueError:
        v("une portée d'une demi-spire est refusée", True)
    _, cs2 = recaler(plans, racine, 0, portee=6.0, spire_um=173.0, voxel_um=2.4)
    v("... et une portée sûre passe", cs2["recales"] == lignes * colonnes)

    # ⚠ Le NIVEAU : la même dalle décrite au niveau 1 doit recaler un maillage dont les
    # coordonnées sont DEUX FOIS plus grandes, et le déplacement remonte en scan.
    d1 = racine / "1"
    d1.mkdir()
    (d1 / ".zarray").write_text(json.dumps(
        {"shape": [n, n, n], "chunks": [c, c, c], "dtype": "|u1", "compressor": None,
         "fill_value": 0, "dimension_separator": "/"}), encoding="utf-8")
    (d1 / "0/0").mkdir(parents=True)
    (d1 / "0/0/0").write_bytes(vol.tobytes())
    gros = {"x": gx * 2.0, "y": gy * 2.0, "z": gz * 2.0}
    s1, c1 = recaler(gros, racine, 1, portee=6.0, pas=0.25)
    v("au niveau 1, tous les points sont recalés", c1["recales"] == lignes * colonnes,
      str(c1))
    # L'axe est à 32 au niveau 1, donc à 64 en scan ; le maillage part de 58.
    v("... sur l'axe médian remonté en coordonnées de scan",
      abs(float(np.median(s1["z"])) - 64.0) < 0.6, str(float(np.median(s1["z"]))))
    v("... et le déplacement est DOUBLÉ, pas laissé au niveau",
      abs(c1["deplacement_median_vox"] - 6.0) < 0.6,
      str(c1.get("deplacement_median_vox")))

    # ⚠⚠ LE DIAGNOSTIC DE PLATEAU, sondé dans les deux sens. Une dalle ÉPAISSE a une crête
    # nette : la parabole corrige, donc peu de points retombent sur un multiple du pas. Une
    # dalle de DEUX voxels n'a pas de crête : son champ de distance est un plateau, et le
    # recalage se pose sur le premier indice — ce qui ressemble exactement à un recalage
    # réussi si personne ne compte.
    # Une dalle de neuf voxels a une demi-épaisseur de ~4,5 : sa crête est haute.
    v("une dalle épaisse a une crête haute", cpt["crete_mediane"] >= 3.0,
      str(cpt.get("crete_mediane")))
    mince = np.zeros((n, n, n), dtype=np.uint8)
    mince[31:33, :, :] = 255
    (d / "0/0/0").write_bytes(mince.tobytes())
    _, cm = recaler(plans, racine, 0, portee=6.0, pas=0.25)
    v("une dalle de deux voxels n'a PAS de crête",
      cm["recales"] > 0 and cm["crete_mediane"] <= 1.5,
      f"{cm.get('crete_mediane')} sur {cm['recales']}")
    v("... et le bloc entier le dit aussi", cm["champ_max"] <= 1.5,
      str(cm["champ_max"]))
    (d / "0/0/0").write_bytes(vol.tobytes())

    # ⚠⚠ LE CUMUL SURVIT AU RECALAGE. Un recalage déplace le long de la NORMALE, donc il ne
    # fait pas avancer : la distance parcourue est inchangée. Sans ce report, une nappe recalée
    # oublie d'où elle vient et la chaîne suivante recompte depuis zéro — ce qui poserait tous
    # ses points de mesure au mauvais endroit de tout axe.
    import projeter_tangentiel as _pt
    d_out = racine / "sortie"
    m_src = {"scale": [0.05, 0.05], "uuid": "src", "parcouru_vox": 123.0}
    porte = {"recale_de": "src", **cpt}
    porte["parcouru_vox"] = float(m_src["parcouru_vox"])
    m_out = _pt.ecrire(sortie, m_src, d_out, porte)
    v("le cumul survit au recalage", m_out.get("parcouru_vox") == 123.0,
      str(m_out.get("parcouru_vox")))
    v("... et la provenance est écrite", m_out.get("recale_de") == "src")
    # ⚠ Le contrôle négatif : sans le report, le champ disparaît. C'est ce qui rend la ligne
    # ci-dessus une mesure et pas une tautologie.
    m_sans = _pt.ecrire(sortie, m_src, racine / "sortie2", {"recale_de": "src"})
    v("... et sans report il DISPARAÎT", "parcouru_vox" not in m_sans)

    # ⚠⚠ LE TÉMOIN NÉGATIF. Sur une dalle qui traverse tout le volume, une nappe translatée
    # LATÉRALEMENT reste dessus : le plancher est alors haut, et c'est correct — un plancher
    # dit ce qu'on lit par hasard DANS CE VOLUME, pas dans un volume idéal.
    dec = decaler(plans, 0.0, 3.0, 0.0)
    v("une translation déplace la nappe", abs(float(dec["y"][2, 3] - plans["y"][2, 3]) - 3.0)
      < 1e-6)
    v("... sans toucher les autres axes", bool(np.allclose(dec["x"], plans["x"])))
    pl = plancher_de_hasard(plans, racine, 0, 6.0, rayon_vox=4.0, tirages=3)
    v("le plancher est mesuré sur plusieurs tirages", pl["tirages"] == 3)
    v("... et il en retient au moins un", pl["retenus"] >= 1, str(pl["retenus"]))
    v("... sur une dalle traversante, il est HAUT", pl["plancher_median"] > 0.5,
      str(pl["plancher_median"]))
    # ⚠ Sur un volume VIDE le plancher tombe à zéro : c'est le contrôle qui rend le nombre
    # ci-dessus une mesure et pas une constante.
    vide_vol = np.zeros((n, n, n), dtype=np.uint8)
    (d / "0/0/0").write_bytes(vide_vol.tobytes())
    pv = plancher_de_hasard(plans, racine, 0, 6.0, rayon_vox=4.0, tirages=2)
    v("dans un volume vide, le plancher est nul", pv["plancher_median"] == 0.0,
      str(pv["plancher_median"]))
    (d / "0/0/0").write_bytes(vol.tobytes())
    # ⚠ La graine est fixée : deux appels rendent le même plancher, donc le nombre publié
    # se rejoue.
    pl2 = plancher_de_hasard(plans, racine, 0, 6.0, rayon_vox=4.0, tirages=3)
    v("le plancher est reproductible", pl2["plancher_median"] == pl["plancher_median"])

    r, _ = rl.lire_region(racine, 0, (0, 0, 0), (n, n, n))
    v("la dalle du témoin est bien là", int(r.max()) == 255)

    shutil.rmtree(racine, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("source", nargs="?", type=Path, help="le tifxyz à recaler")
    p.add_argument("--zarr", type=Path, help="la boîte de prédiction locale")
    p.add_argument("--niveau", type=int, help="OBLIGATOIRE — sans défaut, exprès")
    p.add_argument("--dest", type=Path)
    p.add_argument("--portee", type=float, default=4.0,
                   help="portée de recherche, en voxels DU NIVEAU")
    p.add_argument("--pas", type=float, default=0.25)
    p.add_argument("--spire-um", type=float,
                   help="l'écart inter-spires du rouleau — la portée est refusée si elle "
                        "atteint la demi-spire")
    p.add_argument("--voxel-um", type=float, default=2.4)
    p.add_argument("--plancher", type=float, metavar="RAYON_VOX",
                   help="mesurer le TÉMOIN NÉGATIF : la même nappe translatée au hasard de "
                        "RAYON voxels, plusieurs fois — sans lui, aucun « % posé » n'est "
                        "interprétable")
    p.add_argument("--tirages", type=int, default=3)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.source or not a.zarr or a.niveau is None:
        p.error("source, --zarr et --niveau sont requis")

    import projeter_tangentiel as pt

    plans, meta = pt.lire(a.source)
    sortie, cpt = recaler(plans, a.zarr, a.niveau, a.portee, a.pas, a.spire_um, a.voxel_um)
    print(f"{a.source.name}  ·  niveau {a.niveau}  ·  bloc {cpt['bloc']}")
    print(f"  recalés         {cpt['recales']} / {cpt['points']}")
    print(f"  hors boîte      {cpt['hors_boite']}")
    print(f"  sans matière    {cpt['sans_matiere']}")
    print(f"  borne atteinte  {cpt['borne_atteinte']}")
    print(f"  sans normale    {cpt['sans_normale']}")
    if "deplacement_signe_median_vox" in cpt:
        sm = cpt["deplacement_signe_median_vox"]
        part = cpt["part_vers_le_plus"]
        biais = "⚠⚠ BIAIS" if part > 0.8 or part < 0.2 else "⭐ symétrique"
        print(f"  {biais}       médiane signée {sm:+.2f} vox   "
              f"{part * 100:.0f} % vont vers +normale")
    if "crete_mediane" in cpt:
        # ⚠⚠ Une crête à 1,0 n'est pas une crête : c'est un plateau d'un voxel, et le
        # recalage s'y pose sur le premier indice. Le marqueur le dit plutôt que de laisser
        # lire un déplacement médian comme s'il était localisé.
        m = cpt["crete_mediane"]
        marque = "⚠⚠" if m < 1.5 else "⭐" if m >= 2.5 else "⚠"
        print(f"  {marque} crête         médiane {m:.2f} voxels de niveau "
              f"(p10 {cpt['crete_p10']:.2f})  ·  la plus épaisse du bloc "
              f"{cpt['champ_max']:.1f}")
    if "deplacement_median_vox" in cpt:
        print(f"  ⭐ déplacement   médian {cpt['deplacement_median_vox']:.2f} vox "
              f"({cpt['deplacement_median_vox'] * a.voxel_um:.1f} µm)   "
              f"p90 {cpt['deplacement_p90_vox']:.2f}   max {cpt['deplacement_max_vox']:.2f}")
    if a.plancher:
        pl = plancher_de_hasard(plans, a.zarr, a.niveau, a.portee, a.plancher,
                                a.tirages, spire_um=a.spire_um, voxel_um=a.voxel_um)
        cpt["plancher"] = pl
        if pl["plancher_median"] is not None:
            interroges = cpt["points"] - cpt["hors_boite"]
            part = (cpt["recales"] + cpt["borne_atteinte"]) / max(1, interroges)
            print(f"  ⭐ PLANCHER      {pl['plancher_median'] * 100:.1f} % "
                  f"(max {pl['plancher_max'] * 100:.1f} %) sur {pl['retenus']} tirages "
                  f"à {a.plancher:g} voxels")
            print(f"     cette nappe   {part * 100:.1f} %  →  "
                  + ("⚠⚠ AU NIVEAU DU HASARD" if part <= pl["plancher_max"]
                     else f"⭐ {(part - pl['plancher_median']) * 100:.1f} points au-dessus"))

    if a.dest:
        # ⚠⚠ `parcouru_vox` DOIT survivre au recalage. `ecrire` reconstruit un meta neuf à
        # partir de `rendu` seul, donc sans cette ligne une nappe recalée **oublie d'où elle
        # vient** et la chaîne suivante recompte sa distance depuis zéro. Le recalage déplace
        # le long de la NORMALE : il ne fait pas avancer, donc la distance parcourue est
        # inchangée — pas remise à zéro, pas augmentée.
        porte = {"recale_de": a.source.name, **cpt}
        if "parcouru_vox" in meta:
            porte["parcouru_vox"] = float(meta["parcouru_vox"])
        pt.ecrire(sortie, meta, a.dest, porte)
        print(f"écrit : {a.dest}")
    if a.json:
        a.json.write_text(json.dumps(cpt, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
