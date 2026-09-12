#!/usr/bin/env python3
"""La garde refuse deux pas voyants sur cinq, et le taux ne le voit pas.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** « 42 % des pas
voyants sont refusés » est un nombre ; ce qui décide du remède est **où** ces refus tombent. Une
grille le montre d'un coup d'œil : les cases aveugles de `116` sont toujours en queue de marche —
c'est ce que « absorbant » veut dire — alors que les cases refusées sont **partout**, mêlées aux
orientées, ce qui est exactement pourquoi s'arrêter dessus coûterait quatre cinquièmes de la course.

  ⭐⭐⭐⭐ Le panneau de GAUCHE : une ligne par marche, une case par pas. Gris pour un pas
  aveugle, bleu pour un pas orienté, ambre pour un pas que la garde refuse. Le point noir marque
  un pas **confirmé** — et il tombe aussi souvent sur l'ambre que sur le bleu.

  ⭐⭐⭐ Le panneau de DROITE : pour chacune des marches qui portent les deux états, le taux de
  confirmation de ses pas orientés relié à celui de ses pas refusés. Les traits **se croisent
  dans les deux sens**. Aucun seuil ne sépare les deux populations, et c'est ce que p 0,5861 dit
  sans le montrer.

⚠ `oriente` est RECALCULÉ depuis le désaccord et la barre : le drapeau enregistré dans cette
course date d'avant la réparation de `120` et déclarait orientés les 178 pas qui ne lisent rien.

  uv run python src/figures/figure_ce_que_la_garde_refuse.py \\
      --json docs/mesures/ce_que_la_garde_refuse.json \\
      --sortie docs/images/129_ce_que_la_garde_refuse.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
AVEUGLE = (206, 204, 199)
ORIENTE = (86, 104, 132)
REFUSE = (196, 140, 60)
CONFIRME = (252, 252, 250)
ALERTE = (176, 62, 62)


def lire(chemin: Path) -> dict:
    """Le JSON de `129`, et le refus de dessiner ce qui n'a pas été mesuré."""
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    if not d.get("par_marche"):
        raise ValueError(f"{chemin} ne porte aucune marche")
    t = d.get("le_taux_distingue_t_il", {})
    if not t.get("detail_par_marche"):
        raise ValueError(f"{chemin} ne porte pas le détail par marche : rien à apparier")
    c = d.get("combien_la_garde_refuse", {})
    if not c.get("voyants"):
        raise ValueError(f"{chemin} ne porte aucun pas voyant")
    # ⚠⚠ Les états et les confirmations doivent décrire les MÊMES pas. Une figure qui les
    # apparierait de travers peindrait des points de confirmation sur les mauvaises cases, et
    # rien à l'écran ne le dirait.
    # ⚠⚠⚠ LES CONFIRMATIONS SONT EXIGEES, PAS OPTIONNELLES. Ma première version les prenait si
    # elles étaient là : le producteur ne les émettait pas, donc la figure dessinait sa légende
    # « • confirmé » sans un seul point, et la batterie ne pouvait pas le voir parce que SA
    # fixture, elle, en portait. Un JSON sans confirmations est désormais refusé.
    for m in d["par_marche"]:
        if "confirmes" not in m:
            raise ValueError("une marche ne porte pas ses confirmations : la légende du point "
                             "confirmé ne serait honorée par rien")
        if len(m["confirmes"]) != len(m["etats"]):
            raise ValueError("les états et les confirmations n'ont pas la même longueur")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list]:
    """Dessine, et rend AUSSI les poses de texte et les cadres."""
    marches = d["par_marche"]
    c = d["combien_la_garde_refuse"]
    t = d["le_taux_distingue_t_il"]
    a = d["le_desaccord_est_il_absorbant"]
    L, H = 1180, 560
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(28, 20, "La garde refuse deux pas voyants sur cinq, et le taux ne le voit pas",
           gros, ENCRE)
    ecrire(28, 46, f"{c['marches']} marches · {c['pas']} pas · barre du nul {c['barre_deg']}° · "
                   f"source {d['source']}", petit, GRIS)

    # ── Panneau gauche : la grille des états ─────────────────────────────────
    x0, y0 = 40, 116
    larg = max(4, min(20, int(560 / max(1, max(len(m["etats"]) for m in marches)))))
    haut = max(4, min(16, int(300 / max(1, len(marches)))))
    pw = larg * max(len(m["etats"]) for m in marches)
    ph = haut * len(marches)
    ecrire(x0, y0 - 26, "chaque marche, pas par pas", moyen, ENCRE)
    for i, m in enumerate(marches):
        conf = m.get("confirmes") or []
        for k, s in enumerate(m["etats"]):
            cx, cy = x0 + k * larg, y0 + i * haut
            fill = {"A": AVEUGLE, "O": ORIENTE, "D": REFUSE}.get(s, AVEUGLE)
            art.rectangle([cx, cy, cx + larg - 1, cy + haut - 1], fill=fill)
            # ⚠⚠ LE POINT EST CLAIR, PAS SOMBRE, et ce n'est pas une preference : un point
            # presque noir sur un bleu fonce est invisible, donc la moitie gauche annoncait
            # « il tombe aussi souvent sur l'ambre que sur le bleu » sans le montrer. Un point
            # clair contraste sur les DEUX fonds, ce qu'aucune couleur sombre ne fait.
            if k < len(conf) and conf[k]:
                mx, my = cx + larg / 2, cy + haut / 2
                art.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=CONFIRME)
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    ecrire(x0, y0 + ph + 10, "■ orienté   ■ refusé par la garde   ■ aveugle   • confirmé",
           petit, GRIS)
    ecrire(x0, y0 + ph + 32, f"{c['voyants_desorientes']} pas voyants refusés sur "
                             f"{c['voyants']} ({c['part_des_voyants_refusee']}), sur "
                             f"{c['marches_concernees']} marches", petit, ENCRE)
    ecrire(x0, y0 + ph + 52, "les refus sont MÊLÉS aux orientés, là où les aveugles font la "
                             "queue de la marche", petit, REFUSE)

    # ── Panneau droit : les taux appariés ────────────────────────────────────
    x1, y1 = x0 + pw + 96, y0
    pw2, ph2 = L - x1 - 40, 300
    ecrire(x1, y1 - 26, "par marche : orienté relié à refusé", moyen, ENCRE)
    paires = sorted(((x["taux_oriente"], x["taux_refuse"]) for x in t["detail_par_marche"]),
                    key=lambda p: p[0])
    bas = min(min(p) for p in paires)
    hautv = max(max(p) for p in paires)
    span = max(1e-9, hautv - bas)
    base = y1 + ph2 - 40
    pas_x = max(6, int(pw2 / max(1, len(paires))) - 3)
    monte = descend = 0
    for i, (to, td) in enumerate(paires):
        x = x1 + i * (pas_x + 3) + pas_x // 2
        yo = base - (to - bas) / span * (ph2 - 70)
        yd = base - (td - bas) / span * (ph2 - 70)
        # ⭐⭐⭐ Le trait est peint selon le SENS de l'écart, et c'est ce qui montre que les deux
        # populations se croisent : un lot où le refusé perdrait toujours serait d'une seule
        # couleur, et ce serait un résultat. Ici il y a des deux.
        art.line([x, yo, x, yd], fill=ALERTE if td < to else ORIENTE, width=2)
        art.ellipse([x - 3, yo - 3, x + 3, yo + 3], fill=ORIENTE)
        art.ellipse([x - 3, yd - 3, x + 3, yd + 3], fill=REFUSE)
        monte += int(td > to)
        descend += int(td < to)
    art.line([x1, base, x1 + pw2, base], fill=TRAIT, width=1)
    ecrire(x1, base + 8, f"taux de confirmation, {bas:.2f} → {hautv:.2f}", petit, GRIS)
    ecrire(x1, base + 30, f"{t['taux_des_orientes']} sur les orientés contre "
                          f"{t['taux_des_refuses']} sur les refusés", petit, ENCRE)
    ecrire(x1, base + 50, f"{descend} marches où le refusé perd, {monte} où il gagne · "
                          f"p {t['p_appariee']} sur {t['marches_avec_les_deux_etats']}",
           petit, REFUSE)

    ecrire(28, H - 52, f"et le désaccord n'est PAS absorbant : l'orientation revient "
                       f"{a['part_de_retour_apres_un_refus']} du temps, là où un pas aveugle "
                       f"n'est jamais suivi d'autre chose", moyen, ENCRE)
    ecrire(28, H - 26, f"donc s'arrêter au premier refus jetterait "
                       f"{d['ce_que_couterait_larret']['pas_jetes']} pas sur {c['pas']}, dont "
                       f"{d['ce_que_couterait_larret']['pas_confirmes_jetes']} confirmés",
           petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    return sortie, poses, [(x0, y0, x0 + pw, y0 + ph), (x1, y1, x1 + pw2, y1 + ph2)]


def verifier() -> int:
    """Des contrôles hors ligne, sur un JSON fabriqué — et cinq sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    def faire(etats, confirmes=None):
        return {"rayon_mm": 4.0, "etats": etats,
                "confirmes": confirmes if confirmes is not None else [True] * len(etats)}

    faux = {
        "source": "c.json", "fragment": "PHercParis4",
        "par_marche": [faire("OODDOODDOOAA") for _ in range(12)],
        "combien_la_garde_refuse": {
            "marches": 12, "pas": 144, "aveugles": 24, "voyants": 120,
            "voyants_desorientes": 48, "part_des_voyants_refusee": 0.4,
            "marches_concernees": 12, "barre_deg": 8.88,
            "desaccord_median_des_refuses": 14.56, "desaccord_maximal": 90.0},
        "le_taux_distingue_t_il": {
            "marches_avec_les_deux_etats": 12, "taux_des_orientes": 0.7511,
            "taux_des_refuses": 0.7764, "p_appariee": 0.5861, "le_taux_distingue": False,
            "detail_par_marche": [
                {"rayon_mm": 4.0 + i, "taux_oriente": 0.70 + 0.01 * i,
                 "taux_refuse": 0.72 + 0.01 * ((i * 5) % 7) - 0.02 * (i % 2)}
                for i in range(12)]},
        "le_desaccord_est_il_absorbant": {
            "decidable": True, "part_de_retour_apres_un_refus": 0.5033,
            "le_desaccord_est_absorbant": False},
        "ce_que_couterait_larret": {"pas_jetes": 443, "pas_confirmes_jetes": 276},
    }

    with tempfile.TemporaryDirectory() as dtmp:
        r = Path(dtmp)
        j = r / "c.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", len(lu["par_marche"]), 12)
        p, poses, cadres = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        px = list(im.getdata())
        v("les trois états ont trois couleurs", px.count(ORIENTE) > 200
          and px.count(REFUSE) > 200 and px.count(AVEUGLE) > 200)
        # ⭐⭐ Le point de confirmation doit SE VOIR : un marqueur invisible est un marqueur
        # absent, et la legende promettrait ce que le dessin ne montre pas.
        gx0_, gy0_, gx1_, gy1_ = cadres[0]
        gauche = list(im.crop((int(gx0_), int(gy0_), int(gx1_), int(gy1_))).getdata())
        v("les pas confirmés sont visibles sur la grille", gauche.count(CONFIRME) > 200,
          )
        sans_c = json.loads(json.dumps(faux))
        for m in sans_c["par_marche"]:
            m["confirmes"] = [False] * len(m["etats"])
        j.write_text(json.dumps(sans_c), encoding="utf-8")
        dessiner(lire(j), r / "h.png")
        g2 = list(Image.open(r / "h.png").convert("RGB").crop(
            (int(gx0_), int(gy0_), int(gx1_), int(gy1_))).getdata())
        v("... et une grille sans confirmation n'en porte aucun", g2.count(CONFIRME), 0)
        # ⭐⭐⭐⭐ LA SONDE QUI COMPTE : un lot où le refusé perd TOUJOURS doit être d'une seule
        # couleur à droite. Sans elle, « les deux populations se croisent » serait vrai de
        # n'importe quel dessin.
        # ⚠⚠ LA COMPARAISON EST RELATIVE, PAS UN SEUIL. Ma première version demandait « moins de
        # 400 pixels orientés », un nombre choisi — et faux, parce que les POINTS des taux
        # orientés sont de cette couleur eux aussi et sont dessinés quel que soit le sens. Les
        # deux jeux sont donc comparés l'un à l'autre, ce qui ne demande aucun nombre.
        gx1, gy1, gx2, gy2 = cadres[1]

        def panneau(image):
            return list(image.convert("RGB").crop(
                (int(gx1), int(gy1), int(gx2), int(gy2))).getdata())

        normal = panneau(im)
        perd = json.loads(json.dumps(faux))
        for x in perd["le_taux_distingue_t_il"]["detail_par_marche"]:
            x["taux_oriente"], x["taux_refuse"] = 0.90, 0.40
        j.write_text(json.dumps(perd), encoding="utf-8")
        dessiner(lire(j), r / "g.png")
        droite = panneau(Image.open(r / "g.png"))
        v("un lot où le refusé perd toujours porte PLUS d'alerte",
          droite.count(ALERTE) > normal.count(ALERTE))
        v("... et MOINS de traits de l'autre sens",
          droite.count(ORIENTE) < normal.count(ORIENTE))
        # ⭐ Et le jeu ordinaire doit porter les DEUX sens, sinon « elles se croisent » serait une
        # affirmation sur un dessin qui n'en montre qu'un.
        v("le jeu ordinaire porte les deux sens",
          normal.count(ALERTE) > 0 and normal.count(ORIENTE) > 0)

        # ⚠⚠ LA LEGENDE EST FAITE DE GLYPHES, et tous ne sont pas dans la police deployee : le
        # depot a deja paye des carres vides a la place de `⭐` et `⛔`. Chaque texte pose est
        # verifie, pas seulement ceux qu'on soupconne.
        v("aucun glyphe ne manque a la police",
          sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)}), [])
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])

        for nom, bris in (
                ("sans marche", lambda x: x.update(par_marche=[])),
                ("sans détail apparié",
                 lambda x: x["le_taux_distingue_t_il"].update(detail_par_marche=[])),
                ("sans pas voyant",
                 lambda x: x["combien_la_garde_refuse"].update(voyants=0)),
                ("dont les confirmations n'ont pas la bonne longueur",
                 lambda x: x["par_marche"][0].update(confirmes=[True])),
                ("sans confirmations du tout",
                 lambda x: [m.pop("confirmes") for m in x["par_marche"]])):
            casse = json.loads(json.dumps(faux))
            bris(casse)
            j.write_text(json.dumps(casse), encoding="utf-8")
            try:
                lire(j)
                v(f"sonde : un JSON {nom} est refusé", False)
            except ValueError:
                v(f"sonde : un JSON {nom} est refusé", True)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "ce_que_la_garde_refuse.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "129_ce_que_la_garde_refuse.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
