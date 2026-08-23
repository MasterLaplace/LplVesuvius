#!/usr/bin/env python3
"""Quel couple de fenêtres peut porter une pente, et lequel rendra l'identité.

⚠⚠ **La question que [`51`](../../docs/51_une_pente_a_deux_appuis.md) laisse ouverte.** Sur
`PHercParis4`, la fenêtre de 41 couches est sous le seuil de détection : tout couple qui
l'emploie rend l'identité du couple, quoi qu'il y ait dans le volume. Relancer la même
campagne avec le même couple redonnerait donc **le même nombre**, et il faut savoir *avant
de dépenser* si un autre couple existe.

Ce fichier répond en deux temps, et l'ordre compte :

1. ⭐ **Un fait, sans modèle** : parmi les profondeurs DÉJÀ mesurées, y en a-t-il deux qui
   dégagent le plancher de détection avec un rapport d'au moins deux ? Si oui, le couple
   utilisable existe aujourd'hui et aucun rendu n'est à payer.
2. ⚠ **Une prédiction, avec son étiquette** : sinon, à quelle profondeur l'amplitude
   croiserait-elle le plancher, en supposant amplitude ∝ n^β. C'est la construction de α et
   de β appliquée à l'amplitude.

⚠⚠ **Et la prédiction porte le nombre de points qui la soutiennent.** Avec exactement deux
profondeurs il n'y a **aucun résidu**, donc la loi de puissance n'est pas testable : la
prédiction est l'extrapolation d'un modèle qu'on n'a pas pu réfuter. Ce dépôt a déjà publié
une extrapolation faite sur un seul échantillon — le rendu à « 57 Kio/s », corrigé depuis
d'un facteur vingt à soixante-dix. L'étiquette n'est pas une politesse.

Reproduire :

    python3 analysis/src/fenetre_utilisable.py --racine . --json docs/fenetre_utilisable.json
    python3 analysis/src/fenetre_utilisable.py --verifier
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_profils_plats import lire_profil, juger              # noqa: E402

# ⚠ Le rapport minimal entre les deux fenetres vient de `test_convergence`, qui REFUSE une
# serie dont les fenetres sont trop proches. Le recopier ici ferait deux seuils pour une
# meme contrainte, et ils finiraient par se contredire.
try:
    from test_convergence import analyser as _analyser           # noqa: F401
    RAPPORT_MIN = 2.0
except ImportError:                                              # pragma: no cover
    RAPPORT_MIN = 2.0

# ⚠ La marge au-dessus du plancher. Une amplitude posee PILE au seuil est detectee par
# definition du seuil, mais elle n'a aucune reserve : un tirage un peu moins favorable la
# fait repasser dessous. On demande donc un tiers de plus pour RECOMMANDER une fenetre,
# tout en RAPPORTANT celles qui dégagent tout juste.
MARGE_RECOMMANDATION = 1.33


def profondeur(x: dict) -> int:
    """Le nombre de couches d'une fenêtre, depuis sa demi-fenêtre.

    ⚠ `couche_tracee` est la MOITIÉ de la fenêtre par construction du rendu, et la couche
    tracée elle-même est au centre — d'où le `2n + 1` et non `2n`.
    """
    return int(x["couche_tracee"]) * 2 + 1


def degage(x: dict, marge: float = 1.0) -> bool:
    """Cette fenêtre mesure-t-elle, avec la marge demandée ?"""
    a, seuil = x.get("amplitude"), x.get("seuil")
    if a is None or not seuil:
        return False
    return a >= seuil * marge


def couple_disponible(xs: list[dict], marge: float = 1.0,
                      rapport_min: float = RAPPORT_MIN) -> tuple[int, int] | None:
    """Deux profondeurs déjà mesurées qui dégagent le plancher, écartées d'un facteur deux.

    ⭐ On prend la paire la plus SERRÉE qui satisfait la contrainte, pas la plus large :
    une fenêtre profonde coûte le rendu de toutes ses couches, donc élargir sans raison est
    une dépense sans mesure en face.
    """
    ok = sorted({profondeur(x) for x in xs if degage(x, marge)})
    meilleur = None
    for i, n0 in enumerate(ok):
        for n1 in ok[i + 1:]:
            if n1 / n0 >= rapport_min:
                if meilleur is None or (n1 / n0) < (meilleur[1] / meilleur[0]):
                    meilleur = (n0, n1)
    return meilleur


def beta_amplitude(xs: list[dict]) -> float | None:
    """L'exposant de amplitude ∝ n^β, entre les deux profondeurs extrêmes.

    ⚠ Entre les EXTRÊMES et non par moindres carrés : c'est la même construction que α, qui
    lit lui aussi ses deux bouts. Deux définitions de la même pente dans un même dépôt
    finiraient par ne pas s'accorder.
    """
    pts = sorted({(profondeur(x), float(x["amplitude"]))
                  for x in xs if x.get("amplitude") is not None})
    if len(pts) < 2:
        return None
    (n0, a0), (n1, a1) = pts[0], pts[-1]
    if a0 <= 0 or a1 <= 0 or n0 <= 0 or n1 <= n0:
        return None
    return math.log(a1 / a0) / math.log(n1 / n0)


def profondeur_predite(xs: list[dict], marge: float = MARGE_RECOMMANDATION) -> dict | None:
    """À quelle profondeur l'amplitude croiserait le plancher, et ce que vaut la prédiction.

    ⚠⚠ Trois refus, chacun pour une raison différente :

    - moins de deux profondeurs : il n'y a pas de pente à lire ;
    - β ≤ 0 : l'amplitude ne croît pas avec la fenêtre, donc **aucune** profondeur ne fera
      passer le plancher — creuser serait payer un rendu pour le même refus ;
    - une amplitude ou un seuil manquant : une absence de donnée n'est pas une observation.
    """
    b = beta_amplitude(xs)
    if b is None:
        return None
    pts = sorted({(profondeur(x), float(x["amplitude"]), float(x.get("seuil") or 0.0))
                  for x in xs if x.get("amplitude") is not None and x.get("seuil")})
    if len(pts) < 2:
        return None
    if b <= 0:
        return {"beta": b, "atteignable": False,
                "raison": ("l'amplitude ne croît pas avec la fenêtre — aucune profondeur "
                           "ne fera passer le plancher")}
    n0, a0, seuil = pts[0]
    cible = seuil * marge
    if a0 >= cible:
        n_star = float(n0)
    else:
        n_star = n0 * (cible / a0) ** (1.0 / b)
    nmax = pts[-1][0]
    return {"beta": b, "atteignable": True,
            "profondeur_cible": n_star,
            "cible_amplitude": cible,
            "profondeurs_mesurees": [n for n, _, _ in pts],
            # ⚠⚠ Le facteur d'extrapolation : 1,0 veut dire « dans la plage mesuree ».
            "facteur_extrapolation": max(1.0, n_star / nmax),
            # ⚠⚠ Avec DEUX points il n'y a aucun residu, donc la loi de puissance n'est pas
            # testable. Ce n'est pas la meme chose qu'un ajustement sur cinq points qui colle.
            "loi_testable": len(pts) >= 3}


# ⚠ La tolerance d'appariement des profondeurs PHYSIQUES entre deux niveaux. Au niveau 1 une
# tranche vaut deux fois l'epaisseur, donc 41 tranches deviennent 21 (arrondi au superieur
# pour garder un compte impair, centre sur la couche tracee) : 41 x 2,4 = 98,4 µm contre
# 21 x 4,8 = 100,8. Les deux fenetres regardent la meme chose a 2,4 % pres, et exiger
# l'egalite exacte n'apparierait jamais rien.
TOLERANCE_PROFONDEUR = 0.10


def profondeur_physique(x: dict) -> float | None:
    """La profondeur d'une fenêtre en microns — la seule grandeur comparable entre niveaux."""
    ct, vx = x.get("couche_tracee"), x.get("voxel_um")
    if ct is None or not vx:
        return None
    return profondeur(x) * float(vx)


def amplitude_a_travers_les_niveaux(xs: list[dict],
                                    tol: float = TOLERANCE_PROFONDEUR) -> list[dict]:
    """L'amplitude survit-elle à un changement de niveau de pyramide ?

    ⚠⚠ **La question que [`50`](../../docs/50_le_rendu_attendait_la_memoire.md) ne pose
    pas.** Il mesure que α est préservé d'un niveau à l'autre, et c'est ce qui autorise à
    rendre moins cher. Mais α est un rapport d'écarts, pas une amplitude : un niveau plus
    grossier MOYENNE des voxels, donc il peut très bien lisser le relief que le plancher de
    détection cherche. Décider de rendre une nouvelle fenêtre au niveau 2 en se fondant sur
    une amplitude mesurée au niveau 0 mélangerait deux effets.

    ⭐ On apparie par profondeur **physique** (microns), jamais par compte de tranches : au
    niveau 1 une tranche vaut deux fois l'épaisseur, donc 21 tranches y couvrent ce que 41
    couvrent au niveau 0. Comparer les comptes ferait paraître un désaccord d'un facteur
    deux qui n'existe pas.

    ⚠⚠ **Et les profils donnés ici DOIVENT être la même surface** — c'est à l'appelant de le
    déclarer, jamais à ce fichier de le deviner. Ma première version balayait tout l'arbre et
    appariait par profondeur seule : elle a mis face à face deux traces sans rapport à 99,6 µm
    et rapporté « −53,8 % » comme si la pyramide avait mangé le relief. Un chiffre parfaitement
    plausible, et une comparaison entre étrangers.
    """
    ok = [x for x in xs if x.get("amplitude") is not None
          and profondeur_physique(x) is not None and x.get("voxel_um")]
    out = []
    vus: set[tuple[int, int]] = set()
    for i, a in enumerate(ok):
        for b in ok[i + 1:]:
            if abs(float(a["voxel_um"]) - float(b["voxel_um"])) < 1e-9:
                continue
            pa, pb = profondeur_physique(a), profondeur_physique(b)
            if abs(pa - pb) > tol * max(pa, pb):
                continue
            cle = (id(a), id(b))
            if cle in vus:
                continue
            vus.add(cle)
            fin, gros = (a, b) if a["voxel_um"] < b["voxel_um"] else (b, a)
            af, ag = float(fin["amplitude"]), float(gros["amplitude"])
            out.append({
                "profondeur_um": round((pa + pb) / 2.0, 1),
                "voxel_fin": float(fin["voxel_um"]), "voxel_gros": float(gros["voxel_um"]),
                "amplitude_fine": af, "amplitude_grossiere": ag,
                # ⚠ L'ecart RELATIF, rapporte au niveau fin : c'est lui la reference, le
                # grossier est ce qu'on envisage de payer a la place.
                "ecart_relatif": (ag - af) / af if af > 0 else None,
                "seuil": fin.get("seuil"),
                # ⚠⚠ Ce qui decide vraiment n'est pas l'ecart mais le CAMP : deux amplitudes
                # qui different de 22 % mais degagent toutes deux le plancher rendent le meme
                # verdict, et c'est le verdict qu'on achete.
                "meme_camp": (degage(fin) == degage(gros)),
                "degage_fin": degage(fin), "degage_gros": degage(gros)})
    return sorted(out, key=lambda d: d["profondeur_um"])


def juger_serie(xs: list[dict]) -> dict | None:
    """Le verdict d'une série : couple utilisable aujourd'hui, ou profondeur à atteindre."""
    xs = [juger(x) for x in xs if x.get("couche_tracee")]
    if len(xs) < 2:
        return None
    strict = couple_disponible(xs, 1.0)
    confort = couple_disponible(xs, MARGE_RECOMMANDATION)
    pred = profondeur_predite(xs)
    if confort:
        etat = "couple confortable disponible"
    elif strict:
        etat = "couple disponible, sans marge"
    elif pred and not pred.get("atteignable"):
        etat = "aucune profondeur ne dégagera le plancher"
    else:
        etat = "il faut rendre une fenêtre plus profonde"
    return {"etat": etat, "couple_strict": strict, "couple_confortable": confort,
            "prediction": pred,
            "profondeurs": sorted({profondeur(x) for x in xs}),
            "amplitudes": [round(float(x["amplitude"]), 4) for x in
                           sorted(xs, key=profondeur) if x.get("amplitude") is not None]}


def balayer(racine: Path) -> dict[str, list[dict]]:
    par: dict[str, list[dict]] = {}
    for p in sorted(racine.rglob("profil*.json")):
        x = lire_profil(p)
        if x:
            par.setdefault(str(p.parent), []).append(x)
    return par


def resumer(par: dict[str, list[dict]]) -> dict:
    juges = {}
    for k, xs in sorted(par.items()):
        j = juger_serie(xs)
        if j:
            juges[k] = j
    par_etat: dict[str, int] = {}
    for j in juges.values():
        par_etat[j["etat"]] = par_etat.get(j["etat"], 0) + 1
    a_rendre = sorted(k for k, j in juges.items()
                      if j["etat"] == "il faut rendre une fenêtre plus profonde"
                      and (j.get("prediction") or {}).get("atteignable"))
    return {"series": len(juges), "par_etat": par_etat, "a_rendre": a_rendre,
            "marge_recommandation": MARGE_RECOMMANDATION,
            "rapport_min": RAPPORT_MIN, "detail": juges}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    def prof(ct, ampl, seuil=0.02):
        return {"couche_tracee": ct, "amplitude": ampl, "seuil": seuil,
                "seuil_est_un_repli": False, "ecart_um": 1.0, "plafond_um": 99.0,
                "au_plafond": False}

    # --- la profondeur d'une fenetre ----------------------------------------------------
    # ⚠ 2n + 1 et non 2n : la couche tracee est au CENTRE de sa fenetre.
    v("une demi-fenêtre de 20 fait 41 couches", profondeur(prof(20, 0.1)) == 41)
    v("une demi-fenêtre de 80 fait 161 couches", profondeur(prof(80, 0.1)) == 161)

    # --- degager le plancher ------------------------------------------------------------
    v("pile au seuil, la fenêtre dégage", degage(prof(20, 0.02)))
    v("juste sous le seuil, non", not degage(prof(20, 0.0199)))
    v("pile au seuil, elle ne dégage PAS avec la marge",
      not degage(prof(20, 0.02), MARGE_RECOMMANDATION))
    v("une amplitude absente ne dégage pas", not degage(prof(20, None)))

    # --- le couple disponible -----------------------------------------------------------
    # ⚠⚠ **LE +1 COMPTE, et c'est ma propre attente qui etait fausse ici.** J'attendais
    # (41, 81) : doubler la demi-fenetre, c'est bien doubler la fenetre, non ? Non —
    # 81/41 = 1,976 < 2, donc `test_convergence` REFUSE ce couple. La couche tracee est au
    # centre, donc le +1 de 2n+1 empeche un doublement de demi-fenetre d'atteindre le
    # rapport. Il faut sauter un cran : 161/41 = 3,93.
    xs = [prof(20, 0.05), prof(40, 0.06), prof(80, 0.07)]
    v("le couple le plus serré qui atteint le rapport est choisi",
      couple_disponible(xs) == (41, 161), str(couple_disponible(xs)))
    v("doubler la demi-fenêtre ne suffit PAS à doubler la fenêtre",
      couple_disponible([prof(20, 0.05), prof(40, 0.06)]) is None,
      "81/41 = 1,976")
    v("un couple sous le rapport minimal est écarté",
      couple_disponible([prof(20, 0.05), prof(25, 0.06)]) is None)
    v("une seule fenêtre qui dégage ne fait pas de couple",
      couple_disponible([prof(20, 0.05), prof(80, 0.001)]) is None)

    # --- beta et la profondeur predite --------------------------------------------------
    # amplitude doublant pour une fenetre doublant : beta = 1.
    b = beta_amplitude([prof(20, 0.01), prof(41, 0.02)])
    v("β vaut 1 quand l'amplitude suit la fenêtre", abs(b - 1.0) < 0.05, f"{b:.4f}")
    v("β est nul quand l'amplitude ne bouge pas",
      abs(beta_amplitude([prof(20, 0.01), prof(80, 0.01)])) < 1e-9)
    # ⚠⚠ Le refus qui evite de payer un rendu pour rien.
    d = profondeur_predite([prof(20, 0.05), prof(80, 0.01)])
    v("une amplitude qui DÉCROÎT rend la fenêtre inatteignable", not d["atteignable"])
    v("... et le dit", "ne croît pas" in d["raison"])
    v("une seule profondeur ne prédit rien", profondeur_predite([prof(20, 0.01)]) is None)

    d2 = profondeur_predite([prof(20, 0.01), prof(80, 0.02)])
    v("la profondeur prédite dépasse celles mesurées",
      d2["profondeur_cible"] > max(d2["profondeurs_mesurees"]),
      f"{d2['profondeur_cible']:.1f}")
    v("... et le facteur d'extrapolation le chiffre",
      d2["facteur_extrapolation"] > 1.0, f"{d2['facteur_extrapolation']:.2f}")
    # ⚠⚠ Deux points : aucun residu, donc la loi n'est pas testable. C'est l'etiquette qui
    # separe une prediction d'un ajustement, et ce depot a deja paye une extrapolation faite
    # sur un seul echantillon.
    v("avec deux points la loi n'est PAS testable", not d2["loi_testable"])
    v("avec trois points elle l'est",
      profondeur_predite([prof(20, 0.01), prof(40, 0.014),
                          prof(80, 0.02)])["loi_testable"])
    # ⚠ Une amplitude qui degage DEJA la cible a la fenetre la plus etroite ne demande pas
    # de creuser : la profondeur cible est celle-la, et le facteur d'extrapolation vaut 1.
    d3 = profondeur_predite([prof(20, 0.09), prof(80, 0.12)])
    v("une fenêtre qui dégage déjà ne demande rien de plus",
      d3["profondeur_cible"] == 41 and d3["facteur_extrapolation"] == 1.0,
      f"{d3['profondeur_cible']} / {d3['facteur_extrapolation']}")

    # --- le verdict de serie ------------------------------------------------------------
    j = juger_serie([prof(20, 0.09), prof(80, 0.12)])
    v("deux fenêtres franches donnent un couple confortable",
      j["etat"] == "couple confortable disponible", j["etat"])
    j2 = juger_serie([prof(20, 0.0175), prof(80, 0.0462)])
    v("le cas ps256_c0 demande une fenêtre plus profonde",
      j2["etat"] == "il faut rendre une fenêtre plus profonde", j2["etat"])
    v("... et il est atteignable", j2["prediction"]["atteignable"])
    # ⚠ La valeur mesuree sur le vrai profil : 0,0175 a 41c et 0,0462 a 161c.
    v("... β y vaut environ 0,71", abs(j2["prediction"]["beta"] - 0.71) < 0.02,
      f"{j2['prediction']['beta']:.4f}")
    # ⚠⚠ Trouve sur les VRAIES donnees et pas par relecture : un profil qui ne rapporte
    # aucune amplitude rend `prediction` a None, et le resume plantait dessus. « Inconnu »
    # n'est pas « plat » -- c'est la regle de `audit_profils_plats` -- donc ce cas existe.
    sans = juger_serie([prof(20, None), prof(80, None)])
    v("une série sans amplitude ne prédit rien et ne plante pas",
      sans is not None and sans["prediction"] is None, str(sans))
    v("... et le résumé la traverse",
      resumer({"z": [prof(20, None), prof(80, None)]})["a_rendre"] == [])

    j3 = juger_serie([prof(20, 0.05), prof(80, 0.01)])
    v("une amplitude décroissante est déclarée sans issue",
      j3["etat"] == "aucune profondeur ne dégagera le plancher", j3["etat"])

    # --- l'amplitude a travers les niveaux ----------------------------------------------
    def pro(ct, ampl, vox, seuil=0.02):
        return {"couche_tracee": ct, "amplitude": ampl, "seuil": seuil,
                "voxel_um": vox, "seuil_est_un_repli": False}

    # ⚠ Les valeurs REELLES de `data/controle_resolution` : 41 tranches a 2,4 µm contre
    # 21 a 4,8, soit 98,4 et 100,8 µm -- la meme fenetre physique a 2,4 % pres.
    n = amplitude_a_travers_les_niveaux([pro(20, 0.0146, 2.4), pro(10, 0.0147, 4.8)])
    v("deux niveaux à la même profondeur physique s'apparient", len(n) == 1, str(n))
    v("... l'écart relatif est chiffré", n and abs(n[0]["ecart_relatif"] - 0.0035) < 0.01,
      f"{n[0]['ecart_relatif']:.4f}" if n else "")
    # ⚠⚠ Ce qui decide n'est pas l'ecart mais le CAMP : les deux sont sous le plancher, donc
    # le niveau grossier rend le meme verdict, et c'est le verdict qu'on achete.
    v("... et les deux sont du même côté du plancher", n and n[0]["meme_camp"])
    v("... tous deux sous le plancher",
      n and not n[0]["degage_fin"] and not n[0]["degage_gros"])
    # ⚠ Deux profondeurs PHYSIQUES differentes ne s'apparient pas : 41 tranches a 2,4 contre
    # 41 a 4,8 regardent deux fois plus loin, et les confondre comparerait deux fenetres.
    v("deux profondeurs physiques différentes ne s'apparient pas",
      amplitude_a_travers_les_niveaux([pro(20, 0.01, 2.4), pro(20, 0.01, 4.8)]) == [])
    # ⚠ Deux profils du MEME niveau ne sont pas une comparaison de niveaux.
    v("deux profils du même voxel ne s'apparient pas",
      amplitude_a_travers_les_niveaux([pro(20, 0.01, 2.4), pro(20, 0.02, 2.4)]) == [])
    # ⚠⚠ Le cas ou le niveau grossier fait CHANGER de camp est le seul qui interdise de
    # rendre moins cher. Il doit etre nomme, pas noye dans un pourcentage.
    chg = amplitude_a_travers_les_niveaux([pro(20, 0.05, 2.4), pro(10, 0.01, 4.8)])
    v("un changement de camp est signalé", chg and not chg[0]["meme_camp"],
      str(chg))
    v("une amplitude nulle au niveau fin ne divise pas par zéro",
      amplitude_a_travers_les_niveaux(
          [pro(20, 0.0, 2.4), pro(10, 0.01, 4.8)])[0]["ecart_relatif"] is None)

    r = resumer({"a": [prof(20, 0.09), prof(80, 0.12)],
                 "b": [prof(20, 0.0175), prof(80, 0.0462)]})
    v("le résumé compte les deux séries", r["series"] == 2)
    v("... et ne met à rendre que celle qui en a besoin", r["a_rendre"] == ["b"],
      str(r["a_rendre"]))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--racine", type=Path, default=Path("."))
    ap.add_argument("--json", type=Path)
    # ⚠⚠ Les dossiers d'une MEME surface rendue a plusieurs niveaux de pyramide, declares a
    # la main. Sans declaration, aucune comparaison inter-niveaux n'est tentee : rien dans
    # une arborescence ne dit que deux rendus portent sur la meme surface, et deviner revient
    # a comparer des etrangers.
    ap.add_argument("--niveaux", type=Path, nargs="+", default=[],
                    help="dossiers d'une même surface rendue à plusieurs niveaux")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    par = balayer(a.racine)
    if not par:
        print(f"aucun profil sous {a.racine}", file=sys.stderr)
        return 1
    r = resumer(par)
    if a.niveaux:
        decl = [juger(x) for d in a.niveaux
                for x in balayer(d).get(str(d), []) or
                [y for ys in balayer(d).values() for y in ys]]
        # ⚠ dedoublonnage : un dossier parent et son enfant donneraient deux fois le meme.
        vus, uniques = set(), []
        for x in decl:
            if x["fichier"] not in vus:
                vus.add(x["fichier"])
                uniques.append(x)
        n = amplitude_a_travers_les_niveaux(uniques)
        r["amplitude_entre_niveaux"] = n
        r["paires_de_niveaux"] = len(n)
        r["paires_meme_camp"] = sum(1 for x in n if x["meme_camp"])
        r["dossiers_declares"] = [str(d) for d in a.niveaux]
    print(f"\n  {r['series']} série(s), plancher dégagé avec une marge de "
          f"×{r['marge_recommandation']}, fenêtres écartées d'au moins ×{r['rapport_min']}")
    for etat, n in sorted(r["par_etat"].items(), key=lambda kv: -kv[1]):
        print(f"    {n:4d}  {etat}")

    if r["a_rendre"]:
        print(f"\n  ⚠ {len(r['a_rendre'])} série(s) demandent une fenêtre plus profonde :")
        for k in r["a_rendre"][:12]:
            j = r["detail"][k]
            p = j["prediction"]
            marque = "" if p["loi_testable"] else "  ⚠ loi NON testable (2 points)"
            print(f"      {k:44s} β {p['beta']:+.2f}  cible ≈ {p['profondeur_cible']:.0f}c"
                  f"  (×{p['facteur_extrapolation']:.2f}){marque}")
        if len(r["a_rendre"]) > 12:
            print(f"      … et {len(r['a_rendre']) - 12} autre(s)")

    if r.get("amplitude_entre_niveaux"):
        print(f"\n  l'amplitude à travers les niveaux de pyramide "
              f"({r['paires_meme_camp']}/{r['paires_de_niveaux']} paires du même côté du "
              f"plancher) :")
        for x in r["amplitude_entre_niveaux"]:
            camp = "même camp" if x["meme_camp"] else "⚠⚠ CAMPS OPPOSÉS"
            print(f"      {x['profondeur_um']:7.1f} µm   voxel {x['voxel_fin']:g} → "
                  f"{x['voxel_gros']:g}   amplitude {x['amplitude_fine']:.4f} → "
                  f"{x['amplitude_grossiere']:.4f}   "
                  f"({'—' if x['ecart_relatif'] is None else format(x['ecart_relatif'], '+.1%')})"
                  f"   {camp}")

    if a.json:
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
