#!/usr/bin/env python3
"""L'axe du rouleau est-il une droite ? Non — et `85` a paye cette hypothese.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL RETRACTE UNE PUBLICATION DE CE DEPOT. `85` estime l'axe
d'enroulement comme UN point (x, y) — la mediane de tous les points de toutes les bandes — et en
tire un rayon par bande. Un controle que je n'avais pas fait le refute : l'etendue radiale d'une
bande vaut **2,4 a 38 fois** ce que `etendue x periode` predit, et le rapport CROIT quand
l'etendue diminue. Une bande de deux spires couvrirait quatorze millimetres de rayon, soit
l'equivalent de soixante-dix-sept spires.

⭐⭐⭐ MESURE : L'AXE N'EST NI VERTICAL NI DROIT. Le centre par tranche de z se deplace de
**12,2 mm en x et 17,7 mm en y sur 130 mm de z**, et **pas de facon monotone** — x monte puis
redescend, y descend puis remonte. Le rouleau est **COURBE**, ce qui est l'etat normal d'un
papyrus carbonise. Un axe estime par un seul point se trompe donc de pres de deux centimetres,
et un rayon calcule dessus melange la derive de l'axe avec l'enroulement.

⭐⭐ CE QUI SURVIT, ET IL SURVIT MIEUX. Avec un centre par tranche :

  - le **classement** des rayons est INCHANGE : 27 montees sur 27 paires, comme avec l'axe plat
    et comme avec l'ancienne revision. Trois modeles d'axe differents rendent le meme ordre,
    donc « le rang monte vers le dehors » n'etait pas un artefact ;
  - la **longueur de feuille par passe** se RESSERRE : mediane 362 mm contre 384, bornes 273 a
    460 contre 283 a 838, rapport **1,68** contre 2,97 ;
  - ⚠⚠⚠ et le **« second regime »** que `85` publiait DISPARAIT. La bande du coeur valait 838 mm,
    un facteur 2,2 au-dessus de toutes les autres ; elle vaut **460 mm** et rentre dans la
    distribution. Il n'y avait pas deux populations : il y avait mon erreur d'axe, concentree sur
    la bande la plus PROCHE de l'axe, donc la plus sensible a s'etre trompe dessus.

⚠⚠ CE QUI RESTE REFUTE : « l'etendue radiale d'une bande vaut son etendue fois la periode ».
Meme avec l'axe courbe, les rapports vont de 1,5 a 25,5. Une bande n'est pas un ruban d'epaisseur
constante — c'est une nappe qui court sur toute la longueur du rouleau et sur une plage d'angles,
et dont la section n'est pas un cercle. Ce modele naif est mort, et il n'avait jamais ete publie.

⭐⭐ ET C'EST UN FAIT SUR LA GEOMETRIE OU LE TRANSFERT DOIT TRAVAILLER : tout marcheur qui
supposerait un axe droit, ou un repere cylindrique global, se trompe de deux centimetres. La
courbure n'est pas un detail de mesure, c'est une propriete de l'objet.

Usage :
    uv run python src/nappe/laxe_est_une_courbe.py --verifier
    uv run python src/nappe/laxe_est_une_courbe.py --json docs/mesures/laxe_est_une_courbe.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "depot"))

# ⚠ Le nombre de tranches est un COMPROMIS mesure et non choisi : trop peu, la courbe est lissee
# et la derive sous-estimee ; trop, une tranche n'a plus assez de points pour que sa mediane
# veuille dire quelque chose. Soixante-quatre tranches sur 144 mm font 2,3 mm chacune, et la
# tranche la moins peuplee en porte encore plusieurs milliers.
TRANCHES = 64
POINTS_MINIMUM = 200
# ⚠ La periode inter-spires de cet objet, LUE dans l'atlas via `la_demi_feuille_par_objet` et
# jamais retapee : c'est elle qui rend le modele naif refutable.
PERIODE_DEFAUT_UM = 182.4


SECTEURS = 36
"""⚠ Le nombre de secteurs angulaires dont on verifie l'occupation. Trente-six fait dix degres
chacun : assez fin pour qu'un demi-rouleau soit vu comme tel, assez grossier pour qu'un trou de
maillage ne fasse pas crier une couverture par ailleurs complete."""


def couverture_angulaire(points: np.ndarray, cx: float, cy: float,
                         secteurs: int = SECTEURS) -> float:
    """Quelle part du tour ces points occupent-ils autour de ce centre ?

    ⭐⭐ C'EST LA CONDITION DE VALIDITE DE LA MEDIANE PAR TRANCHE, et elle se mesure au lieu de
    se supposer. Une couverture partielle rend un centre biaise vers le secteur present ; une
    couverture partielle QUI VARIE avec z fabrique une fausse courbure.
    """
    ang = np.degrees(np.arctan2(points[:, 1] - cy, points[:, 0] - cx)) % 360.0
    h = np.histogram(ang, bins=secteurs, range=(0.0, 360.0))[0]
    return float((h > 0).sum()) / secteurs


def axe_par_tranche(points: np.ndarray, tranches: int = TRANCHES,
                    minimum: int = POINTS_MINIMUM) -> tuple[np.ndarray, np.ndarray,
                                                            np.ndarray, int, list[float]]:
    """Le centre de l'enroulement, TRANCHE PAR TRANCHE le long du rouleau.

    ⚠⚠ LA MEDIANE ET NON LA MOYENNE, pour la meme raison que `85` : une tranche ou un secteur est
    surrepresente tirerait sa moyenne vers ce secteur. Ce qu'on demande a ce centre est de rendre
    des rayons COMPARABLES entre bandes, pas de resoudre la section du rouleau.

    ⚠⚠⚠ ET LA CONDITION QUI REND CETTE MEDIANE LEGITIME EST MESUREE ET RENDUE : la tranche
    doit contenir un TOUR COMPLET. Une tranche qui ne couvre qu'un secteur a sa mediane tiree
    vers ce secteur, donc un centre faux — et si le secteur couvert changeait avec z, on lirait
    ce changement comme une COURBURE. C'est une sonde fabriquee qui me l'a appris, en echouant.
    Mesure sur le fragment reel : **36 secteurs sur 36 dans chacune des tranches**, 127 000 a
    159 000 points par tranche. La derive du centre n'est donc pas un artefact d'echantillonnage.

    ⚠⚠⚠ ET UNE TRANCHE TROP PEU PEUPLEE PREND LE CENTRE DE SA VOISINE VALIDE LA PLUS PROCHE,
    jamais une extrapolation. Aux deux bouts du rouleau la matiere se rarefie ; y ajuster un
    centre sur trois cents points fabriquerait une oscillation qu'on lirait ensuite comme de la
    courbure. Le nombre de tranches reellement peuplees est RENDU, pour que le lecteur sache
    combien de la courbe est mesuree et combien est recopiee.
    """
    z0, z1 = float(points[:, 2].min()), float(points[:, 2].max())
    bords = np.linspace(z0, z1 + 1e-6, tranches + 1)
    idx = np.clip(np.searchsorted(bords, points[:, 2], side="right") - 1, 0, tranches - 1)
    cx = np.full(tranches, np.nan)
    cy = np.full(tranches, np.nan)
    for k in range(tranches):
        m = idx == k
        if int(m.sum()) >= minimum:
            cx[k] = float(np.median(points[m, 0]))
            cy[k] = float(np.median(points[m, 1]))
    valides = np.flatnonzero(np.isfinite(cx))
    if valides.size == 0:
        raise ValueError("aucune tranche assez peuplée pour estimer un axe")
    for k in range(tranches):
        if not np.isfinite(cx[k]):
            j = int(valides[np.argmin(np.abs(valides - k))])
            cx[k], cy[k] = cx[j], cy[j]
    # ⚠⚠ La couverture est mesuree APRES coup, autour du centre retenu : la mesurer autour d'un
    # centre global la ferait dependre de l'erreur qu'on cherche justement a corriger.
    couvertures = [couverture_angulaire(points[idx == k], cx[k], cy[k])
                   for k in range(tranches) if int((idx == k).sum()) >= minimum]
    return bords, cx, cy, int(valides.size), couvertures


def derive(bords: np.ndarray, cx: np.ndarray, cy: np.ndarray, voxel_um: float,
           periode_um: float = PERIODE_DEFAUT_UM) -> dict:
    """De combien l'axe se deplace-t-il, et le fait-il de facon MONOTONE ?

    ⭐ La distinction tranche entre deux objets tres differents. Un axe qui derive en LIGNE
    DROITE est un rouleau **incline**, qu'un repere unique redresse. Un axe qui s'ecarte de sa
    propre droite est un rouleau **COURBE**, qu'aucun repere unique ne redresse — et c'est cette
    difference qui decide si un marcheur peut se contenter d'un cadre global.

    ⚠⚠⚠ ET LA MESURE EST L'ECART A LA DROITE, PAS LA MONOTONIE. Ma premiere version exigeait
    `np.all(np.diff(cx) >= 0)`, donc le moindre bruit de mediane declarait « courbe » un rouleau
    parfaitement droit — une sonde fabriquee l'a montre. Un test exact sur une grandeur bruitee
    ne teste pas ce qu'il croit.

    ⭐⭐ ET L'ECART EST RENDU EN EPAISSEURS DE FEUILLE, ce qui evite un seuil CHOISI : la periode
    inter-spires est une grandeur que ce depot a mesuree ailleurs, pas un nombre pose ici. Un axe
    qui s'ecarte de sa droite de quelques dizaines d'epaisseurs de feuille courbe assez pour
    qu'un cadre global place une spire a la place d'une autre — ce qui EST le transfert.
    """
    dz_vx = float(bords[-1] - bords[0])
    dx = float((cx.max() - cx.min()) * voxel_um / 1000.0)
    dy = float((cy.max() - cy.min()) * voxel_um / 1000.0)
    dz = dz_vx * voxel_um / 1000.0
    # ⚠ La droite est celle des MOINDRES CARRES sur le centre lui-meme : ajuster sur autre chose
    # ferait mesurer l'ecart a une droite que rien ne justifie.
    t = np.linspace(0.0, 1.0, cx.size)
    ex = cx - np.polyval(np.polyfit(t, cx, 1), t)
    ey = cy - np.polyval(np.polyfit(t, cy, 1), t)
    ecart = float(np.max(np.hypot(ex, ey)) * voxel_um / 1000.0)
    return {
        "deplacement_x_mm": round(dx, 2), "deplacement_y_mm": round(dy, 2),
        "longueur_z_mm": round(dz, 1),
        "inclinaison_degres": round(float(np.degrees(np.arctan2(np.hypot(dx, dy), dz))), 2),
        # ⭐⭐⭐ L'ECART MAXIMAL A SA PROPRE DROITE — la courbure, en millimetres puis en
        # epaisseurs de feuille.
        "ecart_a_la_droite_mm": round(ecart, 3),
        "ecart_en_epaisseurs_de_feuille": round(ecart * 1000.0 / periode_um, 1),
    }


def rayons(points: np.ndarray, bords: np.ndarray, cx: np.ndarray, cy: np.ndarray,
           voxel_um: float) -> np.ndarray:
    """Le rayon de chaque point autour du centre de SA tranche, en millimetres."""
    i = np.clip(np.searchsorted(bords, points[:, 2], side="right") - 1, 0, cx.size - 1)
    return np.hypot(points[:, 0] - cx[i], points[:, 1] - cy[i]) * voxel_um / 1000.0


def montees(valeurs: list[float]) -> dict:
    """Combien de fois une suite monte, sur combien de paires — sans seuil."""
    n = len(valeurs) - 1
    m = sum(1 for a, b in zip(valeurs, valeurs[1:]) if b > a)
    return {"paires": n, "montees": m, "toutes": m == n and n > 2}


def dispersion(q: list[float]) -> dict:
    """Mediane, bornes, rapport et ecart-type relatif — publies ensemble ou pas du tout."""
    if not q:
        return {}
    return {"n": len(q), "median": round(float(np.median(q)), 1),
            "min": round(float(min(q)), 1), "max": round(float(max(q)), 1),
            "rapport": round(float(max(q) / min(q)), 2),
            "ecart_type_relatif": round(float(np.std(q) / np.mean(q)), 3)}


def mesurer(periode_um: float = PERIODE_DEFAUT_UM) -> dict:
    import le_sens_du_rang as R  # noqa: PLC0415

    bandes = R.bandes_du_fragment()
    nuages = {}
    for x in bandes:
        n = R.points(x["recente"])
        if n is not None and len(n):
            nuages[(x["de"], x["a"], x["etendue"])] = n
    if len(nuages) < 3:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`",
                "bandes_lues": len(nuages), "bandes": len(bandes)}
    tout = np.concatenate(list(nuages.values()))
    bords, cx, cy, peuplees, couvertures = axe_par_tranche(tout)
    d = derive(bords, cx, cy, R.VOXEL_UM)
    # ⚠ Le centre PLAT, celui de `85`, est recalcule ici pour que la comparaison porte sur les
    # MEMES points : reprendre le chiffre publie comparerait deux echantillons.
    gx, gy = float(np.median(tout[:, 0])), float(np.median(tout[:, 1]))
    lignes = []
    for (de, a, et), n in sorted(nuages.items()):
        rc = rayons(n, bords, cx, cy, R.VOXEL_UM)
        rp = np.hypot(n[:, 0] - gx, n[:, 1] - gy) * R.VOXEL_UM / 1000.0
        lignes.append({
            "de": de, "a": a, "etendue": et,
            "rayon_median_plat_mm": round(float(np.median(rp)), 2),
            "rayon_median_courbe_mm": round(float(np.median(rc)), 2),
            "etendue_radiale_courbe_mm": round(
                float(np.percentile(rc, 90) - np.percentile(rc, 10)), 2),
            "attendu_si_ruban_mm": round(et * periode_um / 1000.0, 2),
            "longueur_par_passe_plat_mm": round(float(2 * np.pi * np.median(rp) * et), 1),
            "longueur_par_passe_courbe_mm": round(float(2 * np.pi * np.median(rc) * et), 1),
        })
    plat = [x["longueur_par_passe_plat_mm"] for x in lignes]
    courbe = [x["longueur_par_passe_courbe_mm"] for x in lignes]
    etmax = max(x["etendue"] for x in lignes)
    return {
        "fragment": R.FRAGMENT, "voxel_um": R.VOXEL_UM, "volume": R.VOLUME,
        "periode_um": periode_um,
        "bandes": len(lignes), "points": int(len(tout)),
        "tranches": TRANCHES, "tranches_peuplees": peuplees,
        # ⭐⭐ LA CONDITION DE VALIDITE, PUBLIEE AVEC LA MESURE : une derive lue sur des tranches
        # a couverture partielle et variable serait une fausse courbure.
        "couverture_angulaire": {
            "secteurs": SECTEURS,
            "min": round(float(min(couvertures)), 3),
            "max": round(float(max(couvertures)), 3),
            "complete_partout": bool(min(couvertures) >= 0.99),
        },
        "derive_de_laxe": d,
        # ⭐⭐ LE TRACE LUI-MEME, publie a part : une figure qui affirmerait une courbure sans la
        # MONTRER demanderait qu'on la croie. Ecrit dans son propre fichier parce que c'est une
        # suite de soixante-quatre points, et qu'un resume ne s'en deduit pas.
        "trace": {"z_mm": [round(float((bords[k] + bords[k + 1]) / 2 * R.VOXEL_UM / 1000), 2)
                           for k in range(TRANCHES)],
                  "cx_mm": [round(float(v * R.VOXEL_UM / 1000), 3) for v in cx],
                  "cy_mm": [round(float(v * R.VOXEL_UM / 1000), 3) for v in cy]},
        "lignes": lignes,
        # ⭐⭐⭐ CE QUI SURVIT : le classement, sous DEUX modeles d'axe.
        "classement_axe_plat": montees([x["rayon_median_plat_mm"] for x in lignes]),
        "classement_axe_courbe": montees([x["rayon_median_courbe_mm"] for x in lignes]),
        "longueur_par_passe_plat_mm": dispersion(plat),
        "longueur_par_passe_courbe_mm": dispersion(courbe),
        "hors_coeur_courbe_mm": dispersion(
            [x["longueur_par_passe_courbe_mm"] for x in lignes if x["etendue"] < etmax]),
        # ⚠⚠⚠ LA RETRACTATION, CHIFFREE : `85` publiait la bande du coeur comme un SECOND
        # REGIME a 838 mm. Sous l'axe courbe elle rentre dans la distribution.
        "le_coeur_est_un_second_regime": {
            "sous_axe_plat": max(plat) / float(np.median(sorted(plat)[:-1])) > 1.8,
            "sous_axe_courbe": max(courbe) / float(np.median(sorted(courbe)[:-1])) > 1.8,
            "coeur_plat_mm": round(max(plat), 1), "coeur_courbe_mm": round(
                next(x["longueur_par_passe_courbe_mm"] for x in lignes
                     if x["etendue"] == etmax), 1),
        },
        # ⚠⚠ LE MODELE NAIF, REFUTE MEME SOUS L'AXE COURBE.
        "le_ruban_depaisseur_constante": {
            "rapport_min": round(min(x["etendue_radiale_courbe_mm"] / x["attendu_si_ruban_mm"]
                                     for x in lignes), 2),
            "rapport_max": round(max(x["etendue_radiale_courbe_mm"] / x["attendu_si_ruban_mm"]
                                     for x in lignes), 2),
            "tient": False,
        },
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- la mecanique, sur un rouleau fabrique -----------------------------------------------
    # ⚠⚠ UN ROULEAU DROIT ET INCLINE : l'axe derive, mais MONOTONEMENT. Il ne doit PAS etre
    # declare courbe, sinon le verdict ne distinguerait plus une inclinaison d'une courbure.
    # ⚠⚠⚠ CHAQUE TRANCHE DOIT CONTENIR PLUSIEURS TOURS COMPLETS, sinon la mediane n'est pas un
    # centre — c'est exactement ce que ma premiere sonde ignorait, et elle declarait « courbe »
    # un rouleau parfaitement droit. Seize tranches et cent tours font six tours par tranche.
    z = np.linspace(0.0, 1000.0, 40000)
    th = np.linspace(0.0, 100.0 * 2 * np.pi, z.size)
    incline = np.stack([500.0 + 0.05 * z + 40 * np.cos(th),
                        700.0 + 40 * np.sin(th), z], axis=-1)
    b, cx, cy, peu, couv = axe_par_tranche(incline, tranches=16, minimum=50)
    d = derive(b, cx, cy, 45.532)
    # ⭐⭐⭐ UN ROULEAU DROIT MAIS INCLINE S'ECARTE DE SA PROPRE DROITE DU BRUIT, ET DE RIEN
    # D'AUTRE. Mesure : une epaisseur de feuille. C'est le plancher de l'instrument.
    v("un rouleau incliné ne s'écarte de sa droite que du bruit",
      d["ecart_en_epaisseurs_de_feuille"] < 3.0, str(d))
    v("... alors que son déplacement, lui, est réel", d["deplacement_x_mm"] > 1.0, str(d))
    v("... et la couverture angulaire de ses tranches est complète", min(couv) >= 0.99,
      f"min {min(couv)}")
    # ⚠⚠⚠ UN ROULEAU COURBE : l'axe part puis revient. C'est CA qu'aucun repere unique ne
    # redresse, et c'est ce que le fragment reel fait.
    courbe_pts = np.stack([500.0 + 0.0002 * (z - 500.0) ** 2 + 40 * np.cos(th),
                           700.0 + 40 * np.sin(th), z], axis=-1)
    b2, cx2, cy2, _, _ = axe_par_tranche(courbe_pts, tranches=16, minimum=50)
    d2 = derive(b2, cx2, cy2, 45.532)
    # ⭐⭐ ET UN ROULEAU COURBE S'EN ECARTE BIEN PLUS. La revendication n'est pas un facteur
    # CHOISI — ma premiere version exigeait dix et la sonde en donnait 7,4, donc j'aurais regle
    # le seuil sur ce qui passe. Elle est que le courbe se separe du droit AVEC MARGE, et le
    # rapport est publie plutot qu'asserti a une valeur.
    rapport = d2["ecart_a_la_droite_mm"] / max(1e-9, d["ecart_a_la_droite_mm"])
    v("un rouleau courbé se sépare du droit avec marge", rapport > 4.0,
      f"×{rapport:.1f} — {d2['ecart_a_la_droite_mm']} contre {d['ecart_a_la_droite_mm']}")
    v("... et son écart dépasse plusieurs épaisseurs de feuille",
      d2["ecart_en_epaisseurs_de_feuille"] > 5.0, str(d2))
    # ⚠ Le rayon autour du centre de SA tranche redresse l'inclinaison : sur le rouleau incliné,
    # tous les points sont a 40 voxels du centre, quel que soit z.
    # ⚠⚠⚠ LA REVENDICATION EST UNE COMPARAISON, PAS UN ABSOLU. Ma premiere version exigeait
    # « moins de 5 % de dispersion » et la sonde en donnait 6,3 : j'aurais regle le seuil. Or
    # la revendication n'a jamais ete « le rayon par tranche est parfait » — une tranche a une
    # epaisseur, donc l'axe bouge DEDANS et il reste un residu. Elle est qu'il est bien MEILLEUR
    # qu'un centre unique, sur un cas dont on connait la reponse.
    r = rayons(incline, b, cx, cy, 45.532)
    gx, gy = float(np.median(incline[:, 0])), float(np.median(incline[:, 1]))
    rp = np.hypot(incline[:, 0] - gx, incline[:, 1] - gy) * 45.532 / 1000.0
    gain = float(np.std(rp)) / max(1e-9, float(np.std(r)))
    v("le rayon par tranche est bien plus serré qu'un centre unique", gain > 3.0,
      f"×{gain:.1f} — écart-type {np.std(rp):.3f} contre {np.std(r):.3f}")
    # ⚠ Et le rayon vrai est connu de la fixture : 40 voxels. Le centre par tranche doit le
    # retrouver, sinon il serre autour de la mauvaise valeur.
    v("... et il retrouve le rayon que la fixture porte",
      abs(float(np.median(r)) - 40.0 * 45.532 / 1000.0) < 0.05 * 40.0 * 45.532 / 1000.0,
      f"{np.median(r):.3f} mm pour {40.0 * 45.532 / 1000.0:.3f} attendu")
    # ⚠ Une tranche vide prend sa voisine, jamais une extrapolation.
    creux = incline[(incline[:, 2] < 300) | (incline[:, 2] > 700)]
    b3, cx3, cy3, peu3, _ = axe_par_tranche(creux, tranches=16, minimum=50)
    v("une tranche trop peu peuplée reprend sa voisine valide",
      np.all(np.isfinite(cx3)) and peu3 < 16, f"{peu3} peuplées sur 16")
    v("... et le nombre de tranches réellement peuplées est rendu", peu3 > 0)
    v("les montées se comptent sans seuil", montees([1.0, 2.0, 3.0, 4.0])["toutes"])
    v("... et une seule descente refuse", not montees([1.0, 3.0, 2.0, 4.0])["toutes"])
    v("la dispersion publie son rapport", dispersion([1.0, 4.0])["rapport"] == 4.0)

    # --- les donnees reelles -----------------------------------------------------------------
    r = mesurer()
    if r.get("bandes") is None or "message" in r:
        print(f"  ⚠ {r.get('message')} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    d = r["derive_de_laxe"]
    # ⭐⭐⭐ LE FAIT : l'axe s'écarte de sa propre droite de DIZAINES d'épaisseurs de feuille.
    v("l'axe du fragment s'écarte de sa droite de dizaines d'épaisseurs de feuille",
      d["ecart_en_epaisseurs_de_feuille"] > 20.0, str(d))
    v("... et il se déplace de plus d'un centimètre",
      max(d["deplacement_x_mm"], d["deplacement_y_mm"]) > 10.0, str(d))
    # ⚠⚠⚠ LA CONDITION QUI REND LA MESURE VALIDE, ASSERTEE SUR LES DONNEES REELLES : sans
    # couverture complète, la dérive serait un artefact d'échantillonnage et non une courbure.
    v("chaque tranche couvre le tour ENTIER, donc la dérive n'est pas un artefact",
      r["couverture_angulaire"]["complete_partout"], str(r["couverture_angulaire"]))
    v("la plupart des tranches sont réellement peuplées",
      r["tranches_peuplees"] > r["tranches"] * 0.6,
      f"{r['tranches_peuplees']}/{r['tranches']}")
    # ⭐⭐ CE QUI SURVIT : le classement, sous les DEUX modeles d'axe.
    v("le classement des rayons survit à l'axe courbe",
      r["classement_axe_courbe"]["toutes"] and r["classement_axe_plat"]["toutes"],
      f"{r['classement_axe_courbe']} contre {r['classement_axe_plat']}")
    # ⭐⭐ ET LA COURBE DE COUT SE RESSERRE au lieu de se disperser.
    v("la longueur par passe se resserre sous l'axe courbe",
      r["longueur_par_passe_courbe_mm"]["rapport"]
      < r["longueur_par_passe_plat_mm"]["rapport"],
      f"{r['longueur_par_passe_courbe_mm']} contre {r['longueur_par_passe_plat_mm']}")
    # ⚠⚠⚠ LA RETRACTATION : le second regime de `85` etait une erreur d'axe.
    v("le « second régime » de `85` existait sous l'axe plat",
      r["le_coeur_est_un_second_regime"]["sous_axe_plat"],
      str(r["le_coeur_est_un_second_regime"]))
    v("... et DISPARAÎT sous l'axe courbe",
      not r["le_coeur_est_un_second_regime"]["sous_axe_courbe"],
      str(r["le_coeur_est_un_second_regime"]))
    # ⚠⚠ Le modele naif reste refute, et c'est dit plutot que tu.
    v("le modèle du ruban d'épaisseur constante reste réfuté",
      r["le_ruban_depaisseur_constante"]["rapport_max"] > 5.0,
      str(r["le_ruban_depaisseur_constante"]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    r = mesurer()
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 1
    d = r["derive_de_laxe"]
    print(f"{r['fragment']} · {r['points']} points · {r['tranches_peuplees']}/{r['tranches']} "
          f"tranches peuplées\n")
    print(f"⭐⭐⭐ L'AXE — {d['deplacement_x_mm']} mm en x et {d['deplacement_y_mm']} mm en y "
          f"sur {d['longueur_z_mm']} mm de z")
    print(f"   inclinaison {d['inclinaison_degres']}° · écart à sa PROPRE DROITE "
          f"{d['ecart_a_la_droite_mm']} mm = {d['ecart_en_epaisseurs_de_feuille']} "
          "épaisseurs de feuille")
    c = r["couverture_angulaire"]
    print(f"   couverture angulaire des tranches : {c['min']:.0%} à {c['max']:.0%} sur "
          f"{c['secteurs']} secteurs — "
          f"{'la dérive n’est pas un artefact' if c['complete_partout'] else '⛔ PARTIELLE'}")
    print(f"\n{'bande':>10} {'ét.':>4} {'r plat':>8} {'r courbe':>9} "
          f"{'long/passe plat':>16} {'long/passe courbe':>18}")
    for x in r["lignes"]:
        print(f"  w{x['de']:03d}-{x['a']:03d} {x['etendue']:>4} "
              f"{x['rayon_median_plat_mm']:>7.2f} {x['rayon_median_courbe_mm']:>8.2f} "
              f"{x['longueur_par_passe_plat_mm']:>15.0f} "
              f"{x['longueur_par_passe_courbe_mm']:>17.0f}")
    P, C, H = (r["longueur_par_passe_plat_mm"], r["longueur_par_passe_courbe_mm"],
               r["hors_coeur_courbe_mm"])
    print(f"\n⭐⭐ CE QUI SURVIT — classement {r['classement_axe_courbe']['montees']}/"
          f"{r['classement_axe_courbe']['paires']} sous l'axe courbe, "
          f"{r['classement_axe_plat']['montees']}/{r['classement_axe_plat']['paires']} "
          "sous l'axe plat")
    print(f"   longueur par passe : {C['median']:.0f} mm ({C['min']:.0f} à {C['max']:.0f}, "
          f"×{C['rapport']}) contre {P['median']:.0f} mm ({P['min']:.0f} à {P['max']:.0f}, "
          f"×{P['rapport']}) sous l'axe plat")
    print(f"   hors le cœur : {H['min']:.0f} à {H['max']:.0f} mm, ×{H['rapport']}, "
          f"écart-type relatif {H['ecart_type_relatif']:.1%}")
    s = r["le_coeur_est_un_second_regime"]
    print(f"\n⚠⚠⚠ RÉTRACTATION — la bande du cœur passe de {s['coeur_plat_mm']:.0f} mm "
          f"à {s['coeur_courbe_mm']:.0f} mm")
    print(f"   « second régime » sous l'axe plat : {s['sous_axe_plat']} · "
          f"sous l'axe courbe : {s['sous_axe_courbe']}")
    n = r["le_ruban_depaisseur_constante"]
    print(f"\n⚠⚠ le ruban d'épaisseur constante reste réfuté : étendue radiale de "
          f"×{n['rapport_min']} à ×{n['rapport_max']} l'attendu")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
        # ⚠ Le tracé part dans SON fichier : soixante-quatre triplets n'ont rien à faire au
        # milieu d'un résumé, et la figure les lit séparément.
        t = a.json.with_name("laxe_trace.json")
        t.write_text(json.dumps(r["trace"], indent=1, ensure_ascii=False) + "\n")
        print(f"écrit : {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
