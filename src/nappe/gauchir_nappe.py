#!/usr/bin/env python3
"""Déplacer une nappe LE LONG DE SA NORMALE — la moitié « appliquer » du champ.

⚠⚠ **Ce fichier existe parce que `20` §4 écrivait que corriger était hors de portée**,
*« parce que la chaîne maillage → rendu n'est pas ici »*. Elle y est depuis le
2026-08-19 (`24`), et rien n'avait été écrit pour s'en servir. `champ_correction.py`
mesure **de combien** une trace est décalée ; ce fichier **le fait**.

⚠ Et il ne prétend pas gauchir. Un gauchissement déplace chaque point de sa propre
quantité, et le champ que le dépôt sait produire aujourd'hui est un **résumé par
segment** (`depth_profile --grid` rend une médiane, pas une carte). Ce qui est
implémenté ici est donc la translation **le long de la normale locale**, qui n'est déjà
pas une translation rigide : chaque point suit SA normale. Le champ par fenêtre de
`20` §8 se branchera ici quand un producteur le rendra en coordonnées de maillage.

## Ce que le déplacement ne peut pas faire, et qu'il faut dire

⚠⚠ **Le signe n'est pas connu a priori.** L'ordre des couches d'un rendu est celui du
rendeur, et une normale n'a pas de sens (`valider_champ_normal.py`). Le protocole
honnête est donc empirique : déplacer, re-rendre, mesurer. Si le pic s'éloigne, c'est
l'autre signe. Deux rendus, aucune convention inventée.

⚠ **Un point sans normale n'est pas déplacé — il est INVALIDÉ, et compté.** Le laisser
en place pendant que ses voisins bougent cisaillerait la nappe, et un cisaillement se
lit comme du relief. Un point qu'on ne sait pas orienter est un point qu'on ne sait pas
corriger, et c'est ce qu'il faut dire plutôt que de le laisser mentir.

⚠ **La bbox du `meta.json` est RECALCULÉE.** Elle décrit où la nappe se trouve ; la
recopier après un déplacement livrerait un maillage dont les métadonnées décrivent la
place qu'il occupait avant.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

INVALIDE = -1.0


def lire(dossier: Path) -> tuple[dict, dict]:
    """Les trois plans et la métadonnée d'un `.tifxyz`."""
    import tifffile

    plans = {n: tifffile.imread(str(dossier / f"{n}.tif")) for n in ("x", "y", "z")}
    meta_p = dossier / "meta.json"
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
    return plans, meta


def deplacer(plans: dict, voxels: float) -> tuple[dict, dict]:
    """Chaque point valide avance de `voxels` le long de sa propre normale.

    ⚠ La normale vient de `recaler_sur_la_matiere.normales`, qui la tire des DEUX
    tangentes du maillage et refuse de la calculer à travers un trou. On ne la
    recalcule pas ici : deux définitions de « la normale de cette nappe » finiraient
    par ne pas s'accorder, et c'est le genre d'écart qu'aucun rendu ne montre.
    """
    import numpy as np
    import projeter_tangentiel as pt
    import recaler_sur_la_matiere as rsm

    normale, orientable = rsm.normales(plans)
    bon = pt.valide(plans)

    sortie = {c: plans[c].astype(np.float32).copy() for c in ("x", "y", "z")}
    a_deplacer = bon & orientable
    for i, c in enumerate(("x", "y", "z")):
        sortie[c][a_deplacer] = (plans[c][a_deplacer].astype(np.float64)
                                 + voxels * normale[..., i][a_deplacer]).astype(np.float32)

    # ⚠⚠ Valide mais NON orientable : on ne peut pas le corriger, donc on ne le garde pas.
    perdus = bon & ~orientable
    for c in ("x", "y", "z"):
        sortie[c][perdus] = INVALIDE

    return sortie, {
        **_distorsion(plans, sortie),
        "points": int(bon.size),
        "valides": int(bon.sum()),
        "deplaces": int(a_deplacer.sum()),
        "invalides_faute_de_normale": int(perdus.sum()),
        "voxels": float(voxels),
    }


def _aires(plans):
    """L'aire de chaque maille du quadrillage, ou `nan` si un de ses coins manque."""
    import numpy as np
    import projeter_tangentiel as pt

    P = np.stack([plans[n] for n in ("x", "y", "z")], axis=-1).astype(np.float64)
    bon = pt.valide(plans)
    du = P[1:, :-1] - P[:-1, :-1]
    dv = P[:-1, 1:] - P[:-1, :-1]
    aire = np.linalg.norm(np.cross(du, dv), axis=2)
    entier = bon[:-1, :-1] & bon[1:, :-1] & bon[:-1, 1:]
    return np.where(entier, aire, np.nan)


def _distorsion(avant, apres) -> dict:
    """De combien la surface s'est ÉTIRÉE — la déformation qu'un déplacement normal cause.

    ⚠⚠ **Un déplacement le long de la normale n'est pas une isométrie.** Sur une surface
    courbe, l'aire d'une maille décalée de `d` vaut `(1 − 2Hd + Kd²)` fois la sienne, où
    `H` et `K` sont les courbures moyenne et de Gauss. Donc la nappe s'ÉTIRE là où elle
    est convexe et se COMPRIME là où elle est concave — et les deux signes de `d`
    déforment en sens **opposés**. C'est visible à l'œil sur un rendu, et c'est ce qui
    fait qu'une correction ne peut pas être arbitrairement grande.

    ⚠ Ce n'est PAS un repli : un repli se mesure par `vc_tifxyz_selfcross`, et sur le cas
    livré (±26 voxels) il rend **zéro** auto-intersection transversale sur les trois
    versions. L'étirement existe sans que la nappe se croise.
    """
    import numpy as np

    a0, a1 = _aires(avant), _aires(apres)
    bon = np.isfinite(a0) & np.isfinite(a1) & (a0 > 1e-12)
    if not bon.any():
        return {}

    # ⚠⚠ LA COUVERTURE, et c'est un aveuglement de ce fichier qu'un lecteur a trouve a
    # l'oeil avant que la mesure ne le dise. Tout ce qui suit ne porte que sur les mailles
    # valides DES DEUX COTES : une maille que la transformation fait disparaitre est
    # exclue **par construction**, donc aucune de ces statistiques ne peut signaler une
    # perte. Une mesure restreinte aux donnees existantes ne rapporte jamais les donnees
    # absentes. Paye le 2026-08-27 : un re-aplatissement rendait des chiffres de
    # distorsion meilleurs que la base tout en perdant 2 % de la surface et en trouant
    # 6 % de son quadrillage -- ce qui se voit sur l'image et se lisait dans aucun nombre.
    avant_ok = np.isfinite(a0) & (a0 > 1e-12)
    apres_ok = np.isfinite(a1) & (a1 > 1e-12)
    couverture = {
        "mailles_avant": int(avant_ok.sum()),
        "mailles_apres": int(apres_ok.sum()),
        "mailles_perdues": int((avant_ok & ~apres_ok).sum()),
        "aire_totale_avant": float(a0[avant_ok].sum()),
        "aire_totale_apres": float(a1[apres_ok].sum()),
    }
    couverture["aire_conservee"] = (couverture["aire_totale_apres"]
                                    / max(couverture["aire_totale_avant"], 1e-12))
    ratio = a1[bon] / a0[bon]

    # ⚠⚠ COURBURE ou BRUIT DE NORMALE ? Les deux etirent, et on ne peut pas les
    # distinguer sur une amplitude. Ce qui les separe est la FORME du champ : une
    # courbure est lisse, donc correlee entre mailles voisines ; un bruit de normale est
    # du sel-et-poivre. Le temoin est le MELANGE des memes valeurs -- sans lui, une
    # correlation elevee pourrait n'etre qu'un artefact du calcul.
    champ = np.where(bon, a1 / np.where(a0 > 1e-12, a0, np.nan), np.nan)
    haut, bas = champ[:-1, :], champ[1:, :]
    paire = np.isfinite(haut) & np.isfinite(bas)
    coherence = temoin = float("nan")
    if paire.sum() >= 8 and haut[paire].std() > 0 and bas[paire].std() > 0:
        coherence = float(np.corrcoef(haut[paire], bas[paire])[0, 1])
        melange = champ.copy()
        valeurs = melange[bon].copy()
        np.random.default_rng(0).shuffle(valeurs)
        melange[bon] = valeurs
        h2, b2 = melange[:-1, :], melange[1:, :]
        p2 = np.isfinite(h2) & np.isfinite(b2)
        if p2.sum() >= 8 and h2[p2].std() > 0 and b2[p2].std() > 0:
            temoin = float(np.corrcoef(h2[p2], b2[p2])[0, 1])

    return {
        **couverture,
        "mailles": int(bon.sum()),
        "etirement_coherence_voisins": coherence,
        "etirement_temoin_melange": temoin,
        "aire_ratio_median": float(np.median(ratio)),
        "aire_ratio_p01": float(np.percentile(ratio, 1)),
        "aire_ratio_p99": float(np.percentile(ratio, 99)),
        "aire_totale_ratio": float(a1[bon].sum() / a0[bon].sum()),
    }


def ecrire(dossier: Path, plans: dict, meta: dict, comptes: dict) -> None:
    """Écrit le `.tifxyz`, **bbox recalculée** sur les points réellement valides."""
    import numpy as np
    import tifffile

    dossier.mkdir(parents=True, exist_ok=True)
    for c in ("x", "y", "z"):
        tifffile.imwrite(str(dossier / f"{c}.tif"), plans[c].astype(np.float32))

    bon = ((plans["x"] > INVALIDE) & (plans["y"] > INVALIDE) & (plans["z"] > INVALIDE))
    neuf = dict(meta)
    if bon.any():
        bas = [float(plans[c][bon].min()) for c in ("x", "y", "z")]
        haut = [float(plans[c][bon].max()) for c in ("x", "y", "z")]
        neuf["bbox"] = [bas, haut]
    neuf["deplacement_voxels"] = comptes["voxels"]
    (dossier / "meta.json").write_text(json.dumps(neuf, indent=4) + "\n")


def verifier() -> int:
    """Les contrôles hors ligne, chacun avec son cas négatif."""
    import tempfile

    import numpy as np
    import projeter_tangentiel as pt
    import recaler_sur_la_matiere as rsm

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # Un plan z = 5 dans le plan xy : sa normale est ±z, donc un deplacement de d
    # doit changer z de exactement d et laisser x et y intacts.
    h, w = 6, 7
    gy, gx = np.mgrid[0:h, 0:w]
    plans = {"x": gx.astype(np.float32) + 10.0,
             "y": gy.astype(np.float32) + 20.0,
             "z": np.full((h, w), 5.0, np.float32)}
    out, c = deplacer(plans, 3.0)
    v("tous les points sont deplaces", c["deplaces"] == h * w, str(c))
    v("le plan bouge de exactement d, sur z seul",
      np.allclose(np.abs(out["z"] - plans["z"]), 3.0) and np.allclose(out["x"], plans["x"]),
      f"z {float(out['z'][2, 2])}")
    # ⚠⚠ LE controle qui compte : le signe doit s'INVERSER avec le signe demande.
    # Sans lui, un deplacement qui ignorerait son argument passerait.
    inv, _ = deplacer(plans, -3.0)
    v("le signe inverse le sens", np.allclose(out["z"] + inv["z"], 2 * plans["z"]),
      f"{float(out['z'][2, 2])} / {float(inv['z'][2, 2])}")
    # ... et un deplacement NUL est l'identite.
    zero, _ = deplacer(plans, 0.0)
    v("un deplacement nul ne bouge rien",
      all(np.array_equal(zero[c2], plans[c2]) for c2 in ("x", "y", "z")))

    # Un point invalide le reste, et ne devient jamais un point valide deplace.
    troue = {c2: a.copy() for c2, a in plans.items()}
    for c2 in ("x", "y", "z"):
        troue[c2][3, 3] = INVALIDE
    out2, c2n = deplacer(troue, 3.0)
    v("un point invalide le reste", out2["z"][3, 3] == INVALIDE, str(out2["z"][3, 3]))
    v("... et il n'est pas compte comme deplace", c2n["deplaces"] < h * w, str(c2n))
    # ⚠ Ma premiere version assertait `>= 0`, une TAUTOLOGIE. Et sa fixture ne pouvait de
    # toute facon pas produire un point valide sans normale : mesure, un trou d'un point
    # laisse `orientable` exactement egal a `valide`. Il faut un point ISOLE.
    isole = {c2: np.full((5, 5), INVALIDE, np.float32) for c2 in ("x", "y", "z")}
    isole["x"][2, 2], isole["y"][2, 2], isole["z"][2, 2] = 1.0, 2.0, 3.0
    out3, c3n = deplacer(isole, 3.0)
    v("un point valide SANS voisins n'a pas de normale",
      c3n["invalides_faute_de_normale"] == 1 and c3n["deplaces"] == 0, str(c3n))
    v("... et il est invalide en sortie, pas laisse en place",
      out3["z"][2, 2] == INVALIDE, str(out3["z"][2, 2]))

    # ⚠⚠ LE CONTRAT avec `normales`, plutot que la redondance qu'il rend invisible :
    # aucun point ne doit etre orientable sans etre valide. Tant qu'il tient, le `bon &`
    # de `a_deplacer` est une ceinture ; s'il cede un jour, ce controle le dira au lieu
    # de laisser un point invalide se faire deplacer et devenir un point valide invente.
    n_t, orient_t = rsm.normales(troue)
    v("aucun point orientable n'est invalide",
      not bool((~pt.valide(troue) & orient_t).any()))
    v("le compte de valides est celui du masque", c2n["valides"] == h * w - 1, str(c2n))

    # ⚠⚠ LA COUVERTURE : une transformation qui PERD des mailles doit le dire, et c'est
    # le controle qui manquait. Toutes les statistiques d'etirement ne portent que sur ce
    # qui existe des deux cotes, donc elles peuvent s'ameliorer pendant que la surface
    # disparait -- exactement ce qu'un re-aplatissement a fait le 2026-08-27, avec des
    # chiffres meilleurs que la base et 2 % de surface en moins.
    v("une transformation sans perte conserve tout",
      c["mailles_perdues"] == 0 and abs(c["aire_conservee"] - 1.0) < 1e-9, str(c))
    perce = {c4: a4.copy() for c4, a4 in out.items()}
    for c4 in ("x", "y", "z"):
        perce[c4][2:4, 2:4] = INVALIDE
    cperte = _distorsion(plans, perce)
    v("... et une perte de mailles est SIGNALEE", cperte["mailles_perdues"] > 0,
      str(cperte))
    v("... avec l'aire qu'elle coute", cperte["aire_conservee"] < 0.99,
      str(cperte["aire_conservee"]))

    # ⚠⚠ L'ETIREMENT, contre une reponse ANALYTIQUE. Un plan deplace est congruent a
    # lui-meme : ratio exactement 1. Un cylindre de rayon R deplace de d devient un
    # cylindre de rayon R±d, donc ses aires sont multipliees par (R±d)/R -- un nombre
    # qu'on connait sans passer par le code teste. Sans ce cas courbe, un calcul de
    # distorsion qui rendrait toujours 1 passerait.
    v("un plan deplace ne s'etire pas", abs(c["aire_ratio_median"] - 1.0) < 1e-9,
      str(c.get("aire_ratio_median")))
    # ⚠⚠ Une maille dont un coin manque n'a pas d'aire. L'inclure calculerait une surface
    # a partir de la valeur SENTINELLE (-1), c'est-a-dire un nombre invente -- et il
    # polluerait justement les percentiles, la ou la distorsion se lit. Un trou d'un point
    # retire les TROIS mailles qui le touchent (celle qui l'a pour coin, et les deux dont
    # il est le voisin en ligne ou en colonne).
    _, ct = deplacer(troue, 3.0)
    v("une maille qui touche un trou n'a pas d'aire",
      ct["mailles"] == (h - 1) * (w - 1) - 3,
      f"{ct['mailles']} au lieu de {(h - 1) * (w - 1) - 3}")

    R, d = 100.0, 10.0
    theta = np.linspace(0.0, 0.8, 40)
    vlong = np.linspace(0.0, 30.0, 24)
    TH, VV = np.meshgrid(theta, vlong, indexing="ij")
    cyl = {"x": (R * np.cos(TH)).astype(np.float32) + 500.0,
           "y": (R * np.sin(TH)).astype(np.float32) + 500.0,
           "z": VV.astype(np.float32) + 500.0}
    _, cp = deplacer(cyl, d)
    _, cm = deplacer(cyl, -d)
    attendus = sorted(((R + d) / R, (R - d) / R))
    obtenus = sorted((cp["aire_ratio_median"], cm["aire_ratio_median"]))
    v("un cylindre s'etire de (R±d)/R, la valeur analytique",
      all(abs(o - a2) < 2e-3 for o, a2 in zip(obtenus, attendus)),
      f"{obtenus} contre {attendus}")
    # ⚠ Les deux signes deforment en sens OPPOSES : c'est la signature de la courbure
    # moyenne, et c'est pourquoi les deux rendus de `20` §9 sont distordus differemment.
    v("... et les deux signes en sens opposes",
      (cp["aire_ratio_median"] - 1.0) * (cm["aire_ratio_median"] - 1.0) < 0,
      f"{cp['aire_ratio_median']} / {cm['aire_ratio_median']}")
    # ⚠⚠ Un cylindre PARFAIT a une courbure CONSTANTE, donc un etirement constant : il n'y
    # a rien a correler et la coherence sort a zero. Ma premiere fixture etait celle-la, et
    # le controle a eu raison d'echouer. Ce que la coherence separe, c'est une courbure qui
    # VARIE d'un bruit de normale -- il faut donc une surface ondulee.
    v("un cylindre parfait n'a pas de structure d'etirement a lire",
      abs(cp["etirement_coherence_voisins"]) < 0.3,
      str(cp["etirement_coherence_voisins"]))
    U, W = np.meshgrid(np.linspace(0, 60, 44), np.linspace(0, 60, 44), indexing="ij")
    onde = {"x": (U + 500.0).astype(np.float32),
            "y": (W + 500.0).astype(np.float32),
            "z": (500.0 + 6.0 * np.sin(U / 7.0) * np.cos(W / 9.0)).astype(np.float32)}
    _, co = deplacer(onde, 4.0)
    v("une courbure qui VARIE donne un etirement structure",
      co["etirement_coherence_voisins"] > 0.5, str(co["etirement_coherence_voisins"]))
    v("... et son melange l'effondre",
      abs(co["etirement_temoin_melange"]) < 0.3, str(co["etirement_temoin_melange"]))

    # L'ecriture : la bbox suit les points, elle ne recopie pas l'ancienne.
    with tempfile.TemporaryDirectory() as d:
        cible = Path(d) / "sortie.tifxyz"
        ecrire(cible, out, {"bbox": [[0, 0, 0], [1, 1, 1]], "uuid": "x"}, c)
        relu = json.loads((cible / "meta.json").read_text())
        # ⚠ Une PROPRIETE, pas une valeur attendue. Ma premiere version asserait z = 8,0
        # -- la normale pointe en fait vers -z, donc z vaut 2,0 -- et c'etait l'assertion
        # qui avait tort, pas le code. Une bbox se juge sur ce qu'elle doit etre : serree
        # et contenante. Le SIGNE de la normale, lui, ne s'assere pas : il se mesure.
        bon_r = ((replans_ok := True) and
                 (out["x"] > INVALIDE) & (out["y"] > INVALIDE) & (out["z"] > INVALIDE))
        v("la bbox contient tous les points valides",
          all(relu["bbox"][0][i] <= float(out[c3][bon_r].min()) + 1e-6 and
              relu["bbox"][1][i] >= float(out[c3][bon_r].max()) - 1e-6
              for i, c3 in enumerate(("x", "y", "z"))), str(relu["bbox"]))
        v("... et elle est SERREE, donc ce n'est plus l'ancienne",
          relu["bbox"][0] != [0, 0, 0] and relu["bbox"][1] != [1, 1, 1], str(relu["bbox"]))
        v("... et le reste de la metadonnee survit", relu["uuid"] == "x")
        v("le deplacement voyage avec le maillage", relu["deplacement_voxels"] == 3.0)
        replans, _ = lire(cible)
        v("ce qui est ecrit se relit a l'identique",
          np.array_equal(replans["z"], out["z"]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deplacer une nappe le long de sa normale, de N voxels.",
        epilog="⚠ Le SIGNE se determine en mesurant : deplacer, re-rendre, comparer.")
    parser.add_argument("--verifier", action="store_true")
    parser.add_argument("entree", type=Path, nargs="?", help="dossier .tifxyz")
    parser.add_argument("sortie", type=Path, nargs="?", help="dossier .tifxyz a ecrire")
    parser.add_argument("--voxels", type=float, default=None,
                        help="deplacement le long de la normale, en voxels du volume")
    a = parser.parse_args()

    if a.verifier:
        return verifier()
    if a.entree is None or a.sortie is None or a.voxels is None:
        parser.error("entree, sortie et --voxels sont requis")

    plans, meta = lire(a.entree)
    out, comptes = deplacer(plans, a.voxels)
    ecrire(a.sortie, out, meta, comptes)
    print(f"{comptes['deplaces']} / {comptes['valides']} points deplaces de "
          f"{a.voxels:+.2f} voxels ; {comptes['invalides_faute_de_normale']} invalides "
          f"faute de normale")
    if comptes.get("mailles_perdues"):
        print(f"  ⚠⚠ COUVERTURE : {comptes['mailles_perdues']} mailles perdues, "
              f"aire conservee {100 * comptes['aire_conservee']:.1f} % — les chiffres de "
              f"distorsion ci-dessous NE LES VOIENT PAS")
    if "aire_ratio_median" in comptes:
        print(f"  etirement : aire mediane x{comptes['aire_ratio_median']:.4f} "
              f"(p01 {comptes['aire_ratio_p01']:.4f}, p99 {comptes['aire_ratio_p99']:.4f}), "
              f"aire totale x{comptes['aire_totale_ratio']:.4f}")
        print(f"  etirement structure : coherence voisins "
              f"{comptes['etirement_coherence_voisins']:+.3f} "
              f"(temoin melange {comptes['etirement_temoin_melange']:+.3f})")
        print("  ⚠ un deplacement normal n'est pas une isometrie : la nappe s'etire ou se "
              "comprime selon sa COURBURE -- une coherence elevee le prouve, un champ "
              "mouchete accuserait le bruit de normale")
    print(f"ecrit : {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
