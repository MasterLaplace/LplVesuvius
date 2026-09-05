#!/usr/bin/env python3
"""Ce n'est pas la matière la plus proche qui raccroche, c'est la FORME d'une feuille.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. La mesure tient en deux nombres qui se ressemblent —
46,1 µm pour le maximum brut, 33,3 pour le gabarit — et rien dans ces deux nombres ne dit
POURQUOI l'un marche et l'autre pas. Le profil dessiné le dit d'un coup d'œil : la crête est
large de trente voxels et son creux est à trente-trois micromètres derrière ; un maximum
d'intensité se pose n'importe où sur ce plateau, une forme entière n'a qu'un endroit où tenir.

⭐ Le panneau des sept profils de départ porte la revendication qui rend le gabarit
légitime : il est lu **sur la spire d'où l'on part**, pas sur celle qu'on cherche, et il est
le même partout. Un gabarit qui changerait de forme d'une spire à l'autre ne serait pas la
signature d'une feuille, il serait celle d'un endroit.

⚠ Les deux paires qui ÉCHOUENT sont dessinées comme les autres, en rouge. Une figure qui ne
montrerait que les cinq gagnantes serait un argument, pas une mesure.

Usage :
    uv run python src/figures/figure_le_raccrochage_a_la_matiere.py --verifier
    uv run python src/figures/figure_le_raccrochage_a_la_matiere.py \\
        --sortie docs/images/75_le_raccrochage_a_la_matiere.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_raccrochage_a_la_matiere.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
BLEU = (54, 88, 132)
VERT = (60, 128, 84)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    c = m["convention"]
    return [
        f"le volume brut, {m['voxel_um']} um le voxel, verifie accorde aux spires par le nom "
        f"du zarr : {c['lignes']} lignes cumulees sur {c['spires']} spires publiees.",
        f"une spire publiee est posee a {c['crete_um']:+.1f} um de la crete de matiere, et le "
        f"creux d'air est a {c['creux_um']:+.1f} um ; contraste {c['contraste']:.1f}.",
        f"le pas normal seul laisse {m['pas_seul_median_um']:.1f} um ; le maximum brut "
        f"{m['contendant_maximum_brut_median_um']:.1f} um, soit RIEN ; le gabarit "
        f"{m['raccroche_median_um']:.1f} um.",
        f"trois temoins, chacun ne cassant qu'une chose : gabarit melange "
        f"{m['temoin_gabarit_melange_median_um']:.1f} um, fenetre d'une feuille entiere "
        f"{m['temoin_fenetre_large_median_um']:.1f} um, et raccrocher sans avoir bouge ne "
        f"deplace que de {m['deplacement_sur_place_median_um']:.1f} um.",
        f"l'etalon est l'erreur que laisse la MEILLEURE longueur de pas constante sur des "
        f"paires reservees, {m['etalon_um']} um : le raccrochage passe dessous.",
    ]


def _cadre(art, x0, y0, w, h):
    art.rectangle([x0, y0, x0 + w, y0 + h], outline=CADRE)


def _courbe(art, xs, ys, couleur, largeur=2):
    for a, b in zip(list(zip(xs, ys)), list(zip(xs, ys))[1:]):
        art.line([a[0], a[1], b[0], b[1]], fill=couleur, width=largeur)


def contendants(m: dict) -> list[tuple[str, float, tuple[int, int, int]]]:
    """Les barres du panneau C, dans l'ordre où elles se lisent.

    ⚠ Les témoins sont dans la MÊME liste que les contendants et de la même longueur : les
    mettre à part laisserait croire qu'on compare les gagnants entre eux.
    """
    return [
        ("ne pas bouger", m["sur_place_median_um"], DISCRET),
        ("fenêtre d'une feuille entière (témoin)", m["temoin_fenetre_large_median_um"], ROUGE),
        ("gabarit mélangé (témoin)", m["temoin_gabarit_melange_median_um"], ROUGE),
        ("le pas normal seul", m["pas_seul_median_um"], BLEU),
        ("le maximum brut d'intensité", m["contendant_maximum_brut_median_um"], BLEU),
        ("accordé aux voisins (n'ajoute rien)", m["accorde_median_um"], DISCRET),
        ("LE GABARIT", m["raccroche_median_um"], AMBRE),
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    c = m["convention"]
    lignes = couper(prose(m), 128)
    marge = 40
    pw, ph = 400, 210
    ecart = 56
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 74 + ph + 52 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18),
             "Ce n'est pas la matiere la plus proche qui raccroche, c'est la FORME d'une feuille",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"volume brut {m['zarr']} — {c['lignes']} lignes, {m['paires']} paires de spires",
             fill=DISCRET, font=moyen)

    # ---------- A : le profil de la matiere ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · la matiere autour d'une spire publiee", fill=TEXTE, font=moyen)
    _cadre(art, ax, ay, pw, ph)
    dec = c["decalages_voxels"]
    prof, lisse = c["profil"], c["profil_lisse"]
    lo, hi = min(min(prof), min(lisse)), max(max(prof), max(lisse))
    xs = [ax + k / (len(dec) - 1) * pw for k in range(len(dec))]

    def yv(v):
        return ay + ph - (v - lo) / max(1e-9, hi - lo) * ph

    _courbe(art, xs, [yv(v) for v in prof], (205, 205, 205), 1)
    _courbe(art, xs, [yv(v) for v in lisse], AMBRE, 3)
    x0v = ax + (0.0 - dec[0]) / (dec[-1] - dec[0]) * pw
    art.line([x0v, ay, x0v, ay + ph], fill=BLEU, width=2)
    art.text((x0v + 4, ay + 6), "la spire publiee", fill=BLEU, font=petit)
    for cle, coul, txt in (("crete_um", VERT, "crete"), ("creux_um", ROUGE, "creux")):
        t = c[cle] / m["voxel_um"]
        x = ax + (t - dec[0]) / (dec[-1] - dec[0]) * pw
        art.line([x, ay, x, ay + ph], fill=coul)
        art.text((x + 3, ay + ph - 34), f"{txt} {c[cle]:+.1f}µ", fill=coul, font=petit)
    for t in (dec[0], 0.0, dec[-1]):
        x = ax + (t - dec[0]) / (dec[-1] - dec[0]) * pw
        art.text((min(max(x - 16, ax), ax + pw - 34), ay + ph + 3),
                 f"{t * m['voxel_um']:+.0f}µ", fill=DISCRET, font=petit)

    # ---------- B : les sept profils de depart ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · le gabarit, lu sur la spire de DEPART, est le meme partout",
             fill=TEXTE, font=moyen)
    _cadre(art, bx, by, pw, ph)
    tous = [e["profil_de_depart"] for e in m["lignes"]]
    plo = min(min(p) for p in tous)
    phi = max(max(p) for p in tous)
    xsb = [bx + k / (len(tous[0]) - 1) * pw for k in range(len(tous[0]))]
    for p in tous:
        _courbe(art, xsb, [by + ph - (v - plo) / max(1e-9, phi - plo) * ph for v in p],
                (170, 190, 210), 1)
    _courbe(art, xsb, [by + ph - (v - plo) / max(1e-9, phi - plo) * ph for v in lisse],
            AMBRE, 3)
    x0b = bx + (0.0 - dec[0]) / (dec[-1] - dec[0]) * pw
    art.line([x0b, by, x0b, by + ph], fill=BLEU, width=2)
    art.text((bx + 6, by + 6), f"{len(tous)} spires, une courbe chacune", fill=DISCRET,
             font=petit)
    art.text((bx + 6, by + 22), "en ambre : leur mediane, le gabarit", fill=AMBRE, font=petit)

    # ---------- C : les contendants et leurs temoins ----------
    cx, cy = marge, 96 + ph + 74
    art.text((cx, cy - 20), "C · ce que chacun laisse, en micrometres (mediane des paires)",
             fill=TEXTE, font=moyen)
    barres = contendants(m)
    plus = max(v for _, v, _ in barres) * 1.12
    haut = 20
    lab = 232
    for k, (nom, val, coul) in enumerate(barres):
        y = cy + k * (haut + 6)
        art.text((cx, y + 3), nom, fill=coul, font=petit)
        w = (val / plus) * (pw - lab)
        art.rectangle([cx + lab, y, cx + lab + w, y + haut - 4], fill=coul)
        art.text((cx + lab + w + 5, y + 3), f"{val:.1f}", fill=TEXTE, font=petit)
    ye = cy + len(barres) * (haut + 6)
    xe = cx + lab + (m["etalon_um"] / plus) * (pw - lab)
    art.line([xe, cy - 6, xe, ye], fill=TEXTE, width=2)
    # ⚠ La légende de l'étalon est ancrée à GAUCHE : posée sous sa barre, elle débordait dans
    # le panneau voisin — un panneau qui écrit par-dessus son voisin fait lire un chiffre sous
    # le mauvais titre.
    art.text((cx, ye + 4),
             f"trait vertical : l'etalon, {m['etalon_um']}µ, la meilleure longueur constante",
             fill=TEXTE, font=petit)

    # ---------- D : par paire ----------
    dx, dy = marge + pw + ecart, 96 + ph + 74
    art.text((dx, dy - 20), "D · paire par paire : le pas seul, puis raccroche",
             fill=TEXTE, font=moyen)
    _cadre(art, dx, dy, pw, ph)
    lg = m["lignes"]
    top = max(max(e["pas_seul_um"], e["raccroche_um"]) for e in lg) * 1.15
    larg = pw / (len(lg) * 2 + 1)
    for k, e in enumerate(lg):
        gagne = e["raccroche_um"] < e["pas_seul_um"]
        x = dx + larg * (2 * k + 1)
        h1 = e["pas_seul_um"] / top * (ph - 30)
        h2 = e["raccroche_um"] / top * (ph - 30)
        art.rectangle([x - larg * 0.44, dy + ph - h1, x - 2, dy + ph], fill=BLEU)
        art.rectangle([x + 2, dy + ph - h2, x + larg * 0.44, dy + ph],
                      fill=AMBRE if gagne else ROUGE)
        art.text((x - 16, dy + ph + 3), f"{e['de']}→{e['vers']}", fill=DISCRET, font=petit)
        if not gagne:
            art.text((x - 8, dy + ph - h2 - 15), "✗", fill=ROUGE, font=petit)
    ye2 = dy + ph - m["etalon_um"] / top * (ph - 30)
    art.line([dx, ye2, dx + pw, ye2], fill=TEXTE)
    art.text((dx + 4, ye2 - 14), f"etalon {m['etalon_um']}µ", fill=TEXTE, font=petit)
    art.text((dx + 4, dy + 6), "bleu : le pas seul   ambre : raccroche   rouge : raccroche pire",
             fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"barres": len(barres), "paires": len(lg), "profils": len(tous),
            "echecs_dessines": sum(1 for e in lg if e["raccroche_um"] >= e["pas_seul_um"]),
            "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LES TROIS FAITS QUE LA FIGURE PORTE. Le gabarit passe sous l'étalon qu'aucune
    # longueur constante n'atteint ; il bat ses témoins ; et le maximum brut, lui, ne fait
    # rien — sans ce dernier la figure ne dirait pas ce qui, dans le raccrochage, travaille.
    v("le gabarit passe sous l'étalon", m["passe_sous_letalon"],
      f"{m['raccroche_median_um']} contre {m['etalon_um']}")
    v("... et bat le gabarit mélangé", m["bat_le_gabarit_melange"])
    v("... et la fenêtre d'une feuille entière", m["bat_la_fenetre_large"])
    v("le maximum brut ne fait rien de plus que le pas seul",
      abs(m["contendant_maximum_brut_median_um"] - m["pas_seul_median_um"]) < 5.0,
      f"{m['contendant_maximum_brut_median_um']} contre {m['pas_seul_median_um']}")
    v("... et le gabarit, lui, fait mieux que les deux", m["bat_le_maximum_brut"])
    # ⚠ Le raccrochage sur place est le contrôle qui dit que le gabarit trouve SA feuille.
    v("raccrocher sans avoir bougé déplace peu",
      m["deplacement_sur_place_median_um"] < m["demi_fenetre_um"] / 2,
      f"{m['deplacement_sur_place_median_um']} contre {m['demi_fenetre_um'] / 2}")
    v("le profil est cumulé sur des centaines de lignes", m["convention"]["lignes"] > 500,
      str(m["convention"]["lignes"]))
    # ⚠⚠ CE QUE LE PANNEAU C DOIT MONTRER, et la première version l'avait écrit trop fort :
    # le gabarit bat tout ce qui n'est PAS un raccrochage. « Accordé aux voisins » n'est pas
    # un rival, c'est le même raccrochage passé à la médiane de son voisinage — l'exiger
    # plus long aurait fait échouer la figure sur un fait qu'elle rapporte volontiers.
    b = contendants(m)
    rivaux = [v_ for nom, v_, _ in b if "voisins" not in nom]
    v("dans le panneau C, le gabarit bat tout ce qui n'est pas lui",
      min(rivaux) == m["raccroche_median_um"], str([round(x, 1) for x in rivaux]))
    # ⚠⚠ ET L'ACCORD DES VOISINS N'AJOUTE RIEN, ce qui est un résultat et pas un aveu : il
    # reprend moins d'un micromètre là où son propre témoin — la médiane de neuf décalages
    # SANS RAPPORT — en reprend déjà presque autant. Une figure qui l'aurait vendu comme un
    # gain aurait vendu l'effet de la médiane, pas celui du voisinage.
    v("l'accord des voisins ne reprend presque rien",
      abs(m["accorde_median_um"] - m["raccroche_median_um"]) < 2.0,
      f"{m['accorde_median_um']} contre {m['raccroche_median_um']}")
    v("... et sa queue ne bat pas son propre témoin",
      not m["laccord_bat_son_temoin_sur_la_queue"],
      f"p90 {m['accorde_p90_median_um']} contre {m['temoin_accord_melange_p90_median_um']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("toutes les paires sont dessinées", r["paires"] == m["paires"])
        v("... y compris celles qui échouent",
          r["echecs_dessines"] == m["paires"] - m["paires_ameliorees"],
          f"{r['echecs_dessines']} dessinées")
        v("un profil de départ par paire", r["profils"] == m["paires"])
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png").convert("L")
        gris = img.getextrema()
        v("l'image a du relief", gris[0] < 90 and gris[1] > 240, str(gris))
        # ⚠ Une figure dont un panneau déborde du cadre est une figure fausse : la largeur
        # est vérifiée, pas espérée.
        c_ = Image.open(Path(d) / "t.png")
        v("l'image est plus large que haute", c_.width > c_.height * 0.9,
          f"{c_.width}x{c_.height}")
        # ⚠⚠ Le panneau C écrivait sa légende d'étalon SOUS la barre, donc dans le panneau D.
        # Le contrôle est géométrique : la légende commence à gauche du panneau C et tient
        # dans sa largeur.
        marge_ = 40
        pw_ = 400
        _, _, petit_ = police(17, 13, 11)
        long_legende = petit_.getbbox(
            f"trait vertical : l'etalon, {m['etalon_um']}µ, la meilleure longueur constante")[2]
        v("la légende de l'étalon tient dans son panneau", marge_ + long_legende < marge_ + pw_,
          f"{long_legende} px pour {pw_}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_le_raccrochage_a_la_matiere.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    r = dessiner(json.loads(a.mesure.read_text()), a.sortie)
    print(json.dumps(r, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
