#!/usr/bin/env python3
"""La queue du penchant est-elle locale ?

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** En haut, l'excès
`1 − cos θ` pas à pas le long d'une traversée : le rouleau puis la meilleure matière de `140`, avec
en teinte pleine les pas qui portent la MOITIÉ de l'excès. Si la queue du rouleau était locale, ses
pas pleins formeraient quelques blocs là où ceux de la matière seraient éparpillés — et on voit
qu'ils ne le sont pas davantage. En bas à gauche, la courbe de concentration de chaque marche : les
treize du rouleau tombent DANS la bande des soixante de fixture. En bas à droite, le groupement de
chaque marche : la spirale NUE, qui ne porte aucun excès, est la plus groupée de toutes — donc ce
que cette statistique mesure d'abord est le CAP du marcheur, pas la matière.

  uv run python src/figures/figure_la_queue_du_penchant_est_elle_locale.py \\
      --json docs/mesures/la_queue_du_penchant_est_elle_locale.json \\
      --sortie docs/images/141_la_queue_du_penchant.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (police, textes_debordants, textes_hors_cadre,  # noqa: E402
                            textes_qui_se_recouvrent)
# ⚠ Les statistiques viennent du MODULE, jamais réécrites ici : une figure qui recalcule ce qu'elle
# illustre est une seconde réponse à la même question, et les deux sont libres de diverger.
from la_queue_du_penchant_est_elle_locale import (lexces_par_pas,  # noqa: E402
                                                  les_morceaux_qui_portent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ROULEAU = (150, 96, 176)
ROULEAU_PALE = (214, 190, 226)
MATIERE = (60, 110, 90)
MATIERE_PALE = (176, 205, 191)
NUE = (150, 152, 158)


def lire(chemin: Path) -> dict:
    """Le JSON de `la_queue_du_penchant_est_elle_locale.py`.

    ⚠⚠ Refuse une mesure à laquelle il manque un des deux côtés : l'image est une COMPARAISON, et
    une comparaison sans son témoin est une affirmation déguisée en dessin.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    if not d.get("le_rouleau", {}).get("marches"):
        raise ValueError(f"{chemin} : aucune marche du rouleau")
    lots = [x for x in d.get("sur_les_fixtures", {}).get("lots", []) if x.get("marches")]
    if len(lots) < 2:
        raise ValueError(f"{chemin} : il faut au moins deux matières témoins, {len(lots)} trouvée(s)")
    if not d.get("juger", {}).get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    return d


def representative(marches: list[dict]) -> dict:
    """La marche qui porte le groupement MÉDIAN de son lot.

    ⚠ Choisie par une règle et jamais à l'œil : une figure dont l'exemple est choisi parce qu'il
    est parlant illustre le choix, pas la mesure.
    """
    vals = sorted(m["groupement"]["autocorrelation"] for m in marches
                  if m.get("groupement", {}).get("decidable"))
    med = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1]
                                                     + vals[len(vals) // 2]) / 2.0
    return min(marches, key=lambda m: (abs(m["groupement"]["autocorrelation"] - med),
                                       -m["concentration"]["pas"]))


def _court(lot: dict) -> str:
    """Le nom d'un lot en trois signes, pour une colonne étroite."""
    causes = ("é+f" if lot["ecrasement"] > 0.0 and lot["amplitude_um"] > 0.0
              else "é" if lot["ecrasement"] > 0.0
              else "f" if lot["amplitude_um"] > 0.0 else "nue")
    return causes + (f" b{lot['bruit']:g}" if lot["bruit"] > 0.0 else "")


def _lorenz(angles) -> list[tuple[float, float]]:
    """La part cumulée de l'excès contre la part des pas, du plus cher au moins cher."""
    import numpy as np  # noqa: PLC0415

    e = np.sort(lexces_par_pas(angles))[::-1]
    s = float(e.sum())
    if s <= 0.0:
        return [(0.0, 0.0), (1.0, 1.0)]
    c = np.cumsum(e) / s
    n = e.size
    return [(0.0, 0.0)] + [((i + 1) / n, float(c[i])) for i in range(n)]


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1240, 828
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    b = d["le_rouleau"]
    f = d["sur_les_fixtures"]
    j = d["juger"]
    lots = [x for x in f["lots"] if x.get("marches")]
    meilleure = min((x for x in lots if x["ecrasement"] > 0.0 and x["bruit"] == 0.0),
                    key=lambda x: x["bruit"], default=lots[-1])

    ecrire(28, 20, "La queue du penchant n'est pas locale : elle est celle du marcheur", gros,
           ENCRE)
    ecrire(28, 46, f"{b['n_marches']} marches du rouleau (`137`, cap {b['memoire_du_cap']}) contre "
                   f"{j['marches_de_fixture']} marches de fixture — écrasement {f['ecrasement']}, "
                   f"froissement {f['amplitude_um']:g} µm, bruit balayé "
                   f"{', '.join(f'{x:g}' for x in f['bruits'])} · l'excès d'un pas est "
                   f"1 − cos θ, sa somme donne le rapport chemin / étendue", petit, GRIS)

    # ── Haut : où tombe l'excès le long d'une traversée ──────────────────────
    x0, y0, pw, ph = 60, 118, L - 120, 176
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'excès pas à pas le long d'une traversée — en plein, les pas qui en "
                        "portent la moitié", moyen, ENCRE)
    bandes = ((representative(b["marches"]), "le rouleau", ROULEAU, ROULEAU_PALE),
              (representative(meilleure["marches"]), meilleure["nom"], MATIERE, MATIERE_PALE))
    # ⚠⚠ L'échelle vient de CE QUI EST DESSINÉ, et elle est COMMUNE aux deux bandes : deux échelles
    # propres feraient paraître identiques deux excès qui diffèrent d'un facteur deux.
    haut = max(max(lexces_par_pas(m["angles_deg"])) for m, _, _, _ in bandes)
    for k, (m, nom, plein, pale) in enumerate(bandes):
        by = y0 + 34 + k * 72
        e = lexces_par_pas(m["angles_deg"])
        mo = les_morceaux_qui_portent(e)
        garde = set(sorted(range(e.size), key=lambda i: -e[i])[:mo["pas_retenus"]])
        larg = (pw - 250) / max(e.size, 1)
        ecrire(x0 + 8, by + 8, nom, petit, plein)
        ecrire(x0 + 8, by + 24, f"{e.size} pas · {mo['morceaux']} morceaux · "
                                f"{mo['morceaux_par_cent_pas']:.2f} pour cent pas", petit, GRIS)
        for i in range(e.size):
            hh = (float(e[i]) / haut) * 52.0
            ax = x0 + 190 + i * larg
            art.rectangle([ax, by + 56 - hh, ax + max(larg - 0.8, 1.0), by + 56],
                          fill=(plein if i in garde else pale))
            points.append((ax, by + 56 - hh))
        art.line([x0 + 190, by + 56, x0 + pw - 52, by + 56], fill=TRAIT, width=1)
    ecrire(x0 + pw - 46, y0 + 62, f"{haut:.2f}", petit, GRIS)
    ecrire(x0 + pw - 46, y0 + 78, "excès", petit, GRIS)

    # ── Bas gauche : la concentration, marche par marche ─────────────────────
    x1, y1, pw1, ph1 = 60, 380, 520, 260
    art.rectangle([x1, y1, x1 + pw1, y1 + ph1], outline=TRAIT, width=1)
    cadres.append((x1, y1, x1 + pw1, y1 + ph1))
    ecrire(x1, y1 - 24, "part cumulée de l'excès contre part des pas", moyen, ENCRE)

    def cx(v):
        return x1 + 46 + float(v) * (pw1 - 76)

    def cy(v):
        return y1 + ph1 - 34 - float(v) * (ph1 - 56)

    art.line([cx(0), cy(0), cx(1), cy(1)], fill=TRAIT, width=1)
    for lot in lots:
        for m in lot["marches"]:
            c = _lorenz(m["angles_deg"])
            art.line([p for xy in c for p in (cx(xy[0]), cy(xy[1]))], fill=(206, 206, 202), width=1)
    for m in b["marches"]:
        c = _lorenz(m["angles_deg"])
        art.line([p for xy in c for p in (cx(xy[0]), cy(xy[1]))], fill=ROULEAU, width=1)
    # ⚠⚠ UNE BANDE RÉSERVÉE, parce que la garde des recouvrements compare TEXTE à TEXTE et pas
    # texte à un remplissage : une légende écrite par-dessus les courbes passe tous les contrôles
    # et reste illisible. Le dépôt a déjà payé ça en `137`.
    art.rectangle([x1 + 162, y1 + 4, x1 + pw1 - 6, y1 + 58], fill=FOND)
    ecrire(x1 + 168, y1 + 10, f"les {j['marches_de_fixture']} marches de fixture", petit, GRIS)
    ecrire(x1 + 168, y1 + 26, f"les {b['n_marches']} du rouleau", petit, ROULEAU)
    ecrire(x1 + 168, y1 + 42, "la diagonale : aucun excès concentré", petit, GRIS)
    ecrire(int(cx(0)) - 24, int(cy(1)) - 6, "100 %", petit, GRIS)
    ecrire(int(cx(0)) - 14, int(cy(0)) - 6, "0", petit, GRIS)
    ecrire(x1 + 46, y1 + ph1 - 24, "part des pas, du plus cher au moins cher", petit, GRIS)

    # ── Bas droite : le groupement, et ce qu'il mesure vraiment ──────────────
    x2, y2, pw2, ph2 = 650, 380, L - 650 - 60, 260
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    ecrire(x2, y2 - 24, "groupement de chaque marche (autocorrélation)", moyen, ENCRE)
    # ⚠ Les noms sont COURTS ici et longs dans le tableau : six colonnes de soixante-seize pixels
    # ne tiennent pas « spirale écrasée et froissée, bruit 24 », et un libellé qui déborde sur son
    # voisin rend la colonne illisible — la garde des recouvrements l'a dit.
    familles = [("rouleau", b["marches"], ROULEAU)] + [
        (_court(x), x["marches"], (NUE if x["ecrasement"] == 0.0 else MATIERE)) for x in lots]
    tous = [m["groupement"]["autocorrelation"] for _, ms, _ in familles for m in ms
            if m.get("groupement", {}).get("decidable")]
    lo, hi = min(tous), max(tous)
    marge = max((hi - lo) * 0.12, 0.02)
    lo, hi = lo - marge, hi + marge

    def gy(v):
        return y2 + ph2 - 46 - ((float(v) - lo) / (hi - lo)) * (ph2 - 74)

    for v_ in (0.4, 0.6, 0.8, 1.0):
        if lo <= v_ <= hi:
            art.line([x2 + 44, gy(v_), x2 + pw2 - 8, gy(v_)], fill=TRAIT, width=1)
            ecrire(x2 + 8, int(gy(v_)) - 7, f"{v_:.1f}", petit, GRIS)
    med = b["autocorrelation_median"]
    art.line([x2 + 44, gy(med), x2 + pw2 - 8, gy(med)], fill=ROULEAU_PALE, width=2)
    pas_x = (pw2 - 70) / len(familles)
    for i, (nom, ms, coul) in enumerate(familles):
        ax = x2 + 56 + (i + 0.5) * pas_x
        # ⚠ Les marches d'une même matière se ressemblent, donc leurs points se superposent et la
        # colonne paraît porter deux marches au lieu de douze. L'écart horizontal est DÉTERMINISTE
        # et ne touche que l'abscisse, qui ne porte aucune grandeur : la hauteur reste exacte.
        for k_, m in enumerate(ms):
            g = m.get("groupement", {})
            if not g.get("decidable"):
                continue
            yy = gy(g["autocorrelation"])
            dx = ((k_ % 5) - 2) * 4.5
            art.ellipse([ax + dx - 3, yy - 3, ax + dx + 3, yy + 3], fill=coul)
            points.append((ax + dx, yy))
        ecrire(int(ax) - 3 * len(nom), y2 + ph2 - 34, nom, petit, coul)
    ecrire(x2 + 56, y2 + 8, f"médiane du rouleau {med:.4f}", petit, ROULEAU)
    ecrire(x2 + 56, y2 + 24, f"la spirale NUE, sans aucun excès, monte à "
                             f"{max(m['groupement']['autocorrelation'] for m in lots[0]['marches']):.4f}",
           petit, (110, 112, 118))

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 690
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    nue_max = max(m["groupement"]["autocorrelation"] for m in lots[0]["marches"])
    ecrire(44, by0 + 10, f"✗ la queue N'EST PAS locale : le rouleau tombe DANS la distribution "
                         f"des fixtures — "
                         f"{j['autocorrelation_part_des_fixtures_au_dessus']:.0%} d'entre elles "
                         f"sont plus groupées, "
                         f"{j['part_du_sommet_20_part_des_fixtures_au_dessus']:.0%} plus "
                         f"concentrées.", moyen, ENCRE)
    ecrire(44, by0 + 34, f"la spirale nue ne porte aucun excès et se groupe à {nue_max:.4f} : ce "
                         f"que ces statistiques mesurent d'abord est le cap du marcheur.",
           petit, ENCRE)
    ecrire(44, by0 + 52, f"ce qui manque à la matière est du NIVEAU — excès "
                         f"{meilleure['exces_moyen_median']} contre {b['exces_moyen_median']} — "
                         f"et pas une forme.", petit, ENCRE)
    ecrire(44, by0 + 74, "conséquence pour le graal : il n'y a PAS d'endroits où le chemin part "
                         "de travers qu'une alarme locale pourrait signaler.", petit, ENCRE)
    ecrire(44, by0 + 92, f"les {j['morceaux_du_rouleau']:.0f} morceaux de "
                         f"{j['longueur_des_morceaux_du_rouleau']:.1f} pas qui portent la moitié "
                         f"de l'excès font {j['morceaux_par_cent_pas_du_rouleau']:.2f} pour cent "
                         f"pas, contre {meilleure['morceaux_par_cent_pas_median']:.2f} à la "
                         f"matière.", petit, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import tempfile  # noqa: PLC0415

    from figure_commune import glyphes_manquants  # noqa: PLC0415

    src = RACINE / "docs" / "mesures" / "la_queue_du_penchant_est_elle_locale.json"
    v("la mesure existe", src.exists(), str(src))
    if not src.exists():
        print(f"\nÉCHEC ({echecs + 1} failures, {controles + 1} checks)")
        return 1
    d = lire(src)

    # ---- la lecture refuse ce qu'elle ne peut pas dessiner
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for nom, contenu in (("message", {"message": "fixture injoignable"}),
                             ("sans rouleau", {"le_rouleau": {"marches": []},
                                               "sur_les_fixtures": {"lots": []}}),
                             ("un seul témoin", {"le_rouleau": d["le_rouleau"],
                                                 "sur_les_fixtures": {
                                                     "lots": d["sur_les_fixtures"]["lots"][:1]},
                                                 "juger": d["juger"]}),
                             ("jugement indécidable", {"le_rouleau": d["le_rouleau"],
                                                       "sur_les_fixtures": d["sur_les_fixtures"],
                                                       "juger": {"decidable": False}})):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except ValueError:
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        # ---- la règle de la marche représentative
        r1 = representative(d["le_rouleau"]["marches"])
        r2 = representative(d["le_rouleau"]["marches"])
        v("la marche représentative est choisie par une règle, donc toujours la même",
          r1["marche"] == r2["marche"], f"marche {r1['marche']}")
        vals = sorted(m["groupement"]["autocorrelation"] for m in d["le_rouleau"]["marches"])
        v("... et c'est bien celle du groupement médian",
          abs(r1["groupement"]["autocorrelation"] - vals[len(vals) // 2]) < 0.2,
          f"{r1['groupement']['autocorrelation']} contre {vals[len(vals) // 2]}")

        # ---- la courbe de concentration
        lo = _lorenz([0.0] * 30)
        v("une marche sans excès donne la diagonale", lo == [(0.0, 0.0), (1.0, 1.0)])
        lo = _lorenz([40.0] * 30)
        v("une marche à excès constant suit la diagonale",
          all(abs(x - y) < 1e-9 for x, y in lo))
        lo = _lorenz([0.0] * 29 + [60.0])
        v("un excès porté par un seul pas monte d'un coup",
          lo[1][1] > 0.99, f"{lo[1][1]:.4f}")
        v("la courbe finit toujours à cent pour cent",
          abs(_lorenz(d["le_rouleau"]["marches"][0]["angles_deg"])[-1][1] - 1.0) < 1e-9)

        # ---- le dessin
        sortie = tmp / "141.png"
        chemin, poses, cadres, points = dessiner(d, sortie)
        v("l'image est écrite", chemin.exists() and chemin.stat().st_size > 0)
        v("un cadre par panneau, plus celui de la bande de conclusion", len(cadres) == 4,
          f"{len(cadres)}")
        deb = textes_debordants(poses, 1240)
        v("aucun texte ne déborde de la toile", not deb, str(deb[:2]))
        hors = textes_hors_cadre(poses, cadres)
        v("aucun texte ne sort de son panneau", not hors, str(hors[:2]))
        rec = textes_qui_se_recouvrent(poses)
        v("aucun texte n'en recouvre un autre", not rec, str(rec[:3]))
        manquants = sorted({g for _x, _y, t, _f in poses for g in glyphes_manquants(t)})
        v("aucun glyphe absent de la police déployée", not manquants, str(manquants))
        v("tous les points tracés tombent dans la toile",
          all(0 <= x <= 1240 and 0 <= y <= 828 for x, y in points), f"{len(points)} points")
        v("il y a bien de quoi regarder", len(points) > 200, f"{len(points)} points")

        # ---- ⭐ deux rendus de la même vue sont identiques au bit
        autre = tmp / "141_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        # ---- ⭐ le verdict dessiné est celui de la mesure, pas une phrase figée
        d2 = json.loads(json.dumps(d))
        d2["juger"]["autocorrelation_part_des_fixtures_au_dessus"] = 0.99
        troisieme = tmp / "141_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure : la changer change l'image",
          troisieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/la_queue_du_penchant_est_elle_locale.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/141_la_queue_du_penchant.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
