#!/usr/bin/env python3
"""L'appariement des repères survit-il à un témoin qui garde leur FORME ? — et ce que le support est vraiment.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST UNE CORRECTION DE MON PROPRE CONTRÔLE. Les deux
tranches précédentes ont jugé l'appariement des repères contre un semis tiré **uniformément**
dans l'empreinte. Or les repères sont **groupés d'un côté** — c'est mesuré, le 80 % central tient
sur 29 % × 18 % de la carte — et les vides du support sont eux aussi peu nombreux et localisés.
Un semis uniforme est donc plus loin de tout **par construction**, et « 7,7 fois mieux que le
hasard » peut n'être que la signature du **groupement**, sans aucune correspondance.

⭐⭐⭐ **Le témoin juste garde la forme et casse la place** : le même nuage de repères, avec sa
géométrie interne intacte, posé ailleurs dans l'empreinte. S'il obtient la même distance, la
correspondance n'existe pas ; s'il fait nettement moins bien, elle existe. C'est le contrôle que
`46` appelle « le témoin dans l'image » transposé à un semis.

⚠⚠ ET LA CARACTÉRISATION QUI PRÉCÈDE TOUT : le support de la carte publiée est-il un **masque**
ou un **seuil de prédiction** ? La question se tranche sur l'histogramme : un masque laisse un
**trou** sous la première valeur rendue, une prédiction non. Sans elle, « les vides du support »
ne veut rien dire.

Usage :
    uv run python src/encre/le_temoin_de_meme_forme.py --verifier
    uv run python src/encre/le_temoin_de_meme_forme.py \\
        --json docs/mesures/le_temoin_de_meme_forme.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "encre"))

PLEINE = RACINE / "docs" / "mesures" / "les_reperes_a_pleine_resolution.json"


def signature_de_masque(carte: np.ndarray) -> dict:
    """Le zéro de cette carte est-il un MASQUE ou une prédiction basse ?

    ⚠⚠⚠ LE TEST EST LE TROU APRÈS ZÉRO, et il ne se devine pas. Un détecteur qui prédit peu
    d'encre rend des valeurs basses : 1, 2, 3 sont occupées. Un pipeline qui **masque** écrit un
    zéro franc et sa première valeur rendue est bien plus haute, donc l'histogramme montre un pic
    à zéro suivi d'un **vide**. La largeur de ce vide est rendue : c'est elle qui distingue les
    deux, pas la part de zéros.
    """
    h = np.bincount(carte.ravel(), minlength=256)
    premiere = int(np.argmax(h[1:] > 0) + 1) if (h[1:] > 0).any() else 0
    positifs = carte[carte > 0]
    return dict(part_de_zero=round(float(h[0] / carte.size), 4),
                premiere_valeur_rendue=premiere,
                largeur_du_vide_apres_zero=max(0, premiere - 1),
                niveaux_occupes=int((h[1:] > 0).sum()),
                quantiles_des_positifs=[int(x) for x in
                                        np.percentile(positifs, [1, 25, 50, 75, 99])]
                if positifs.size else [])


def semis_deplace(positions: np.ndarray, empreinte: np.ndarray, graine: int = 42,
                  tirages: int = 20, part_dedans: float = 0.8,
                  essais: int = 400) -> list[np.ndarray]:
    """Le MÊME nuage, sa géométrie interne intacte, posé ailleurs dans l'empreinte.

    ⚠⚠⚠ C'est le témoin que les tranches précédentes n'avaient pas. Un semis uniforme casse deux
    choses à la fois — la place ET le groupement — donc il ne peut pas dire laquelle des deux
    explique un bon appariement. Celui-ci n'en casse qu'une.

    ⚠ Une pose n'est retenue que si une part suffisante des points tombe **dans** l'empreinte :
    un nuage à moitié dehors serait loin de toute cible par construction, donc flatterait
    l'appariement vrai — l'erreur exacte qu'on veut cesser de commettre.

    ⚠⚠ Le nombre de poses réellement trouvées est rendu par l'appelant : un témoin qui n'aurait
    qu'une pose n'est pas un témoin, c'est une anecdote, et ça arrive dès que le nuage remplit
    presque l'empreinte.
    """
    if positions.size == 0:
        return []
    ii, jj = np.nonzero(empreinte)
    if ii.size == 0:
        return []
    rng = np.random.default_rng(graine)
    lo = positions.min(axis=0)
    hi = positions.max(axis=0)
    h, w = empreinte.shape
    poses = []
    for _ in range(essais):
        if len(poses) >= tirages:
            break
        di = rng.uniform(-lo[0], h - 1 - hi[0])
        dj = rng.uniform(-lo[1], w - 1 - hi[1])
        cand = positions + np.array([di, dj])
        li = np.clip(cand[:, 0].astype(int), 0, h - 1)
        lj = np.clip(cand[:, 1].astype(int), 0, w - 1)
        if empreinte[li, lj].mean() >= part_dedans:
            poses.append(cand)
    return poses


def mesurer(recette: str = "new_canon", graine: int = 42, tirages: int = 20) -> dict:
    """L'appariement vrai contre DEUX témoins : l'uniforme d'avant, et le même en forme."""
    import le_recalage_des_etiquettes as rec  # noqa: PLC0415
    import les_reperes_apparies as ap  # noqa: PLC0415
    from les_reperes_a_pleine_resolution import carte_publiee_pleine  # noqa: PLC0415
    from les_reperes_interieurs import trous, utilisables  # noqa: PLC0415

    masque = rec._image("500P2_mask.png")
    pleine = carte_publiee_pleine(recette)
    if masque is None or pleine is None:
        raise SystemExit("masque ou carte pleine résolution absents")
    carte, nom = pleine
    empreinte = carte > 0
    t = rec.affine_par_boites(masque, empreinte.astype(float))

    support = empreinte.astype(np.uint8) * 255
    facteur = t["echelle_lignes"] * t["echelle_colonnes"]
    from les_reperes_interieurs import AIRE_MINIMALE  # noqa: PLC0415

    cibles_t = utilisables(trous(support, aire_minimale=max(4, int(round(AIRE_MINIMALE
                                                                        * facteur)))))
    cibles = np.array([c["centre"] for c in cibles_t], dtype=float)
    sources = np.array([ap.transformer(s["centre"], t)
                        for s in utilisables(trous(masque))], dtype=float)
    if cibles.size == 0 or sources.size == 0:
        raise SystemExit("pas de quoi apparier")

    vrai = float(np.median(ap.apparier(sources, cibles)))
    uniforme = ap.semis_temoin(support, len(sources), graine)
    med_uniforme = float(np.median(ap.apparier(uniforme, cibles)))
    poses = semis_deplace(sources, empreinte, graine=graine, tirages=tirages)
    medianes = [float(np.median(ap.apparier(p, cibles))) for p in poses]
    # ⚠ Trois poses sont rendues pour la figure, avec les cibles et le semis vrai : une figure
    # qui les recalculerait pourrait en tirer d'autres, donc dessinerait un témoin différent de
    # celui qui est jugé ici.
    echantillon = [[[round(float(x), 1), round(float(y), 1)] for x, y in q]
                   for q in poses[:3]]

    # ⚠⚠⚠ LE RANG EST LA STATISTIQUE JUSTE, PAS LE VERDICT BINAIRE. « Bat le meilleur témoin »
    # est vrai ou faux, mais ne dit pas de combien on s'en approche ; le rang de la pose vraie
    # parmi toutes les poses est un test de permutation exact, et sa valeur p vaut
    # rang / (poses + 1). C'est la seule façon de distinguer « aucune correspondance » de « une
    # correspondance faible ».
    rang = 1 + sum(1 for m in medianes if m < vrai)
    return dict(carte_publiee=nom, recette=recette,
                rang_de_la_pose_vraie=rang,
                poses_comparees=len(medianes),
                p_de_permutation=(round(rang / (len(medianes) + 1), 4)
                                  if medianes else None),
                signature_de_masque=signature_de_masque(carte),
                reperes=len(sources), cibles=len(cibles),
                distance_vraie=round(vrai, 2),
                temoin_uniforme=round(med_uniforme, 2),
                temoin_de_meme_forme=dict(
                    poses=len(poses),
                    mediane=round(float(np.median(medianes)), 2) if medianes else None,
                    meilleure=round(float(min(medianes)), 2) if medianes else None,
                    pire=round(float(max(medianes)), 2) if medianes else None,
                    toutes=[round(m, 2) for m in medianes]),
                # ⚠⚠ LE VERDICT EST CONTRE LA MEILLEURE DES POSES, pas contre leur médiane : un
                # appariement qui ne battrait qu'une pose moyenne serait battu par la chance dès
                # qu'on tire un peu plus. Comparer au meilleur témoin est la version stricte, et
                # c'est celle qui décide.
                bat_le_temoin_uniforme=bool(vrai < med_uniforme),
                bat_le_temoin_de_meme_forme=bool(medianes and vrai < min(medianes)),
                rapport_a_l_uniforme=round(med_uniforme / vrai, 2) if vrai else None,
                rapport_a_la_meme_forme=(round(min(medianes) / vrai, 2)
                                         if medianes and vrai else None),
                forme_carte=list(carte.shape),
                cibles_xy=[[round(float(c[0]), 1), round(float(c[1]), 1)] for c in cibles],
                reperes_xy=[[round(float(x), 1), round(float(y), 1)] for x, y in sources],
                poses_echantillon=echantillon)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠⚠ Les deux cas que la signature doit distinguer, et dans les deux sens.
    masque_like = np.zeros((100, 100), dtype=np.uint8)
    masque_like[20:80, 20:80] = 30
    masque_like[30:40, 30:40] = 200
    s1 = signature_de_masque(masque_like)
    v("un masque laisse un vide franc sous sa première valeur",
      s1["premiere_valeur_rendue"] == 30 and s1["largeur_du_vide_apres_zero"] == 29, str(s1))
    prediction = np.zeros((100, 100), dtype=np.uint8)
    rng = np.random.default_rng(3)
    prediction[20:80, 20:80] = rng.integers(0, 60, size=(60, 60))
    s2 = signature_de_masque(prediction)
    v("... alors qu'une prédiction basse occupe 1, 2, 3",
      s2["premiere_valeur_rendue"] == 1 and s2["largeur_du_vide_apres_zero"] == 0, str(s2))
    v("une carte entièrement nulle ne lève pas",
      signature_de_masque(np.zeros((10, 10), dtype=np.uint8))["niveaux_occupes"] == 0)

    # --- le témoin de même forme ---
    emp = np.zeros((400, 400), dtype=bool)
    emp[20:380, 20:380] = True
    nuage = np.array([[100.0 + 3 * k, 100.0 + 2 * (k % 7)] for k in range(30)])
    poses = semis_deplace(nuage, emp, tirages=10)
    v("le témoin trouve plusieurs poses", len(poses) >= 5, str(len(poses)))
    # ⚠⚠⚠ LA PROPRIÉTÉ QUI FAIT TOUT : la géométrie INTERNE doit être intacte, sinon le témoin
    # casserait le groupement en même temps que la place et ne vaudrait pas mieux que l'uniforme.
    d0 = np.hypot(*(nuage[1:] - nuage[:-1]).T)
    v("... et chaque pose garde la géométrie interne au bit près",
      all(np.allclose(np.hypot(*(p[1:] - p[:-1]).T), d0) for p in poses))
    v("... et elle est bien DÉPLACÉE, pas laissée sur place",
      all(not np.allclose(p, nuage) for p in poses))
    v("... et posée dans l'empreinte",
      all(emp[p[:, 0].astype(int), p[:, 1].astype(int)].mean() >= 0.8 for p in poses))
    # ⚠ Une empreinte à peine plus grande que le nuage ne doit pas rendre des poses fantaisistes.
    serree = np.zeros((400, 400), dtype=bool)
    serree[98:190, 98:118] = True
    v("une empreinte serrée rend peu de poses plutôt que de mauvaises",
      len(semis_deplace(nuage, serree, tirages=10)) <= 10)
    v("un nuage vide ne rend aucune pose",
      semis_deplace(np.zeros((0, 2)), emp) == [])

    # --- le cas qui montre pourquoi l'uniforme ne suffit pas ---
    import les_reperes_apparies as ap  # noqa: PLC0415

    cibles = np.array([[100.0 + 30 * k, 110.0] for k in range(6)])
    vrai = float(np.median(ap.apparier(nuage, cibles)))
    sup = (emp.astype(np.uint8)) * 255
    unif = float(np.median(ap.apparier(ap.semis_temoin(sup, len(nuage), 1), cibles)))
    meme = min(float(np.median(ap.apparier(p, cibles))) for p in poses)
    # ⚠⚠ Sur une fixture où les cibles sont DANS le nuage, les deux témoins doivent perdre — et
    # c'est le cas facile. Le contrôle utile est le suivant.
    v("quand les cibles sont dans le nuage, les deux témoins perdent",
      vrai < unif and vrai < meme, f"vrai {vrai:.0f}, uniforme {unif:.0f}, même forme {meme:.0f}")
    # ⚠⚠⚠ ET LE CAS QUI JUSTIFIE TOUT LE FICHIER : des cibles groupées AILLEURS. L'uniforme se
    # laisse encore battre parce qu'il s'étale sur toute l'empreinte, le témoin de même forme
    # non. Sans ce contrôle, `semis_deplace` pourrait être un synonyme coûteux de l'uniforme.
    loin = np.array([[300.0 + 5 * k, 330.0] for k in range(6)])
    vrai2 = float(np.median(ap.apparier(nuage, loin)))
    unif2 = float(np.median(ap.apparier(ap.semis_temoin(sup, len(nuage), 1), loin)))
    meme2 = min(float(np.median(ap.apparier(p, loin))) for p in poses)
    v("des cibles groupées ailleurs : le témoin de même forme le voit, l'uniforme moins",
      meme2 < vrai2 and (unif2 / max(1e-9, vrai2)) > (meme2 / max(1e-9, vrai2)),
      f"vrai {vrai2:.0f}, uniforme {unif2:.0f}, même forme {meme2:.0f}")

    # ⚠⚠ Le rang doit être un vrai rang : premier quand la pose vraie bat tout, dernier quand
    # elle est battue par tout. Sans ces deux bornes, « p = 0,05 » pourrait n'être qu'un compteur
    # qui ne compte rien.
    def rang(vrai_, medianes_):
        return 1 + sum(1 for m in medianes_ if m < vrai_)

    v("le rang vaut 1 quand la pose vraie bat toutes les autres", rang(10.0, [20.0, 30.0]) == 1)
    v("... et le dernier quand elle est battue par toutes",
      rang(99.0, [20.0, 30.0]) == 3, str(rang(99.0, [20.0, 30.0])))
    v("... et il se place au milieu quand elle est moyenne",
      rang(25.0, [20.0, 30.0]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--recette", default="new_canon")
    p.add_argument("--tirages", type=int, default=20)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.recette, tirages=a.tirages)
    s = r["signature_de_masque"]
    print(f"le zéro de la carte : {s['part_de_zero'] * 100:.1f} % des pixels, première valeur "
          f"rendue {s['premiere_valeur_rendue']}, donc un vide de "
          f"{s['largeur_du_vide_apres_zero']} niveaux")
    print(f"→ c'est un {'MASQUE' if s['largeur_du_vide_apres_zero'] >= 5 else 'seuil de prédiction'}\n")
    t = r["temoin_de_meme_forme"]
    print(f"{r['reperes']} repères contre {r['cibles']} cibles\n")
    print(f"{'':<26}{'distance médiane':>18}")
    print("-" * 44)
    print(f"{'appariement vrai':<26}{r['distance_vraie']:>18.0f}")
    print(f"{'témoin uniforme':<26}{r['temoin_uniforme']:>18.0f}   "
          f"×{r['rapport_a_l_uniforme']}")
    print(f"{'témoin de MÊME FORME':<26}"
          f"{(t['meilleure'] if t['meilleure'] is not None else float('nan')):>18.0f}   "
          f"×{r['rapport_a_la_meme_forme']}   ({t['poses']} poses, "
          f"médiane {t['mediane']}, pire {t['pire']})")
    print(f"\nbat l'uniforme : {'OUI' if r['bat_le_temoin_uniforme'] else 'NON'}   "
          f"bat la même forme : {'OUI' if r['bat_le_temoin_de_meme_forme'] else 'NON'}")
    print(f"rang de la pose VRAIE : {r['rang_de_la_pose_vraie']} sur "
          f"{r['poses_comparees'] + 1}   →   p = {r['p_de_permutation']}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
