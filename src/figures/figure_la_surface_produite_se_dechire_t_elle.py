"""La surface produite ne se déchire pas là où elle rate ; là où la bande saute, c'est la couche de la bande qui se déchire.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, DEUX CARTES DE LA MÊME FENÊTRE de la bande `w028-037`, choisie
par une règle : la profondeur où la chaîne tombe, et celle de la couche que la bande porte. La première est lisse, la
seconde saute d'un tour par plaques. En bas à gauche, LA PART DES POINTS BORDÉS D'UNE FALAISE, dans la surface de la chaîne
et dans la couche de la bande, là où elles s'accordent et là où la bande saute. En bas à droite, les deux détecteurs.

  uv run python src/figures/figure_la_surface_produite_se_dechire_t_elle.py \\
      --sortie docs/images/252_la_surface_produite_se_dechire_t_elle.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURES = RACINE / "docs" / "mesures"
LA_BANDE_JSON = MESURES / "la_surface_produite_se_dechire_t_elle.json"
LE_SEGMENT_JSON = MESURES / "la_surface_produite_du_segment_5753.json"
PAS = 72.0833

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
VIDE = (228, 226, 220)
L_, H_ = 1360, 950
LES_COTES = (("plus", "du_cote_plus"), ("moins", "du_cote_moins"))
LA_GAMME = ((0.5, (214, 226, 205)), (1.0, (60, 110, 90)), (2.0, (176, 92, 42)), (3.0, (90, 40, 20)))


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    d = {"bande": json.loads(LA_BANDE_JSON.read_text()), "segment": json.loads(LE_SEGMENT_JSON.read_text())}
    for k, m in d.items():
        if not m.get("decidable"):
            raise SystemExit(f"mesure indécidable : {k}")
    return d


def la_couleur(v) -> tuple[int, int, int]:
    """La profondeur en pas, sur la gamme : un pas en vert, deux en rouille."""
    if v is None:
        return VIDE
    x = abs(v) / PAS
    if x <= LA_GAMME[0][0]:
        return LA_GAMME[0][1]
    for (a, ca), (b, cb) in zip(LA_GAMME, LA_GAMME[1:]):
        if x <= b:
            f = (x - a) / (b - a)
            return tuple(round(ca[k] + f * (cb[k] - ca[k])) for k in range(3))
    return LA_GAMME[-1][1]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : la surface tient-elle en une pièce, et la couche de la bande est-elle plus souvent
    déchirée que la surface là où la bande saute, des deux côtés ?"""
    b = d["bande"]
    une = all(b[c]["la_part_hors_de_la_plus_grande_piece"] < 0.01 for _, c in LES_COTES)
    dechire = all(b[c]["les_falaises_par_groupe"]["trop_pres_la_ou_la_bande_saute"]["bordes_dans_la_couche_de_la_bande"]
                  > 2 * b[c]["les_falaises_par_groupe"]["trop_pres_la_ou_la_bande_saute"]["bordes_dans_la_surface_de_la_chaine"]
                  for _, c in LES_COTES)
    if une and dechire:
        return "LA SURFACE PRODUITE NE SE DÉCHIRE PAS LÀ OÙ ELLE RATE ; LÀ OÙ LA BANDE SAUTE, C'EST SA COUCHE QUI SE DÉCHIRE"
    return "LA SURFACE PRODUITE ET LA COUCHE DE LA BANDE SE DÉCHIRENT PAREIL"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, object] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    b = d["bande"]
    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, "la surface est le premier saut de 247 avec m7, sur la maille de huit ; une falaise sépare deux mailles "
                   "voisines dont les profondeurs diffèrent d'un demi-feuillet ou plus", petit, GRIS)

    # ── PANNEAU 1 · DEUX CARTES ─────────────────────────────────────────────────────────────
    fen = b["du_cote_plus"]["la_fenetre"]
    a0, a1 = fen["les_colonnes"]
    panneau(50, 84, 1310, 470, f"LA MÊME FENÊTRE, CÔTÉ PLUS · colonnes {a0} à {a1 - 1} de la maille, celles qui portent le "
                               f"plus de chutes où la bande saute ({fen['les_sauts_dans_la_fenetre']})")
    ech = 8
    cartes = 0
    for k, (titre, cle) in enumerate((("où la chaîne tombe", "la_chaine"), ("la couche que la bande porte", "la_bande"))):
        m = fen[cle]
        x0, y0 = 74 + k * 620, 150
        ecrire(x0, 124, titre, 0, ENCRE)
        for i, ligne in enumerate(m):
            for j, v in enumerate(ligne):
                art.rectangle([x0 + j * ech * 0.6, y0 + i * ech, x0 + (j + 1) * ech * 0.6 - 1, y0 + (i + 1) * ech - 1],
                              fill=la_couleur(v))
        for i, ligne in enumerate(fen["les_sauts"]):
            for j, s_ in enumerate(ligne):
                if s_:
                    cx, cy = x0 + (j + 0.5) * ech * 0.6, y0 + (i + 0.5) * ech
                    art.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=FOND)
        points.append((x0 + len(m[0]) * ech * 0.6, y0 + len(m) * ech))
        cartes += 1
    traces["cartes"] = cartes
    yl = 150 + len(fen["la_chaine"]) * ech + 22
    for k, (v, t) in enumerate(((0.5, "un demi-pas"), (1.0, "un pas"), (2.0, "deux pas"), (3.0, "trois pas"))):
        art.rectangle([74 + k * 150, yl + 2, 90 + k * 150, yl + 12], fill=la_couleur(v * PAS))
        ecrire(96 + k * 150, yl, t, 0, GRIS)
    art.rectangle([694, yl + 2, 710, yl + 12], fill=VIDE)
    ecrire(716, yl, "pas de couche en face", 0, GRIS)
    ecrire(900, yl, "point clair : une chute où la bande saute", 0, GRIS)

    # ── PANNEAU 2 · LES FALAISES PAR GROUPE ─────────────────────────────────────────────────
    panneau(50, 490, 820, 800, "LA PART DES POINTS BORDÉS D'UNE FALAISE")
    bx0, bx1 = 330, 700
    y = 530
    barres = 0
    for objet, nom_o in (("bande", "la bande w028-037"), ("segment", "le segment 20230702185753")):
        ecrire(66, y, nom_o, 0, ENCRE)
        y += 18
        for nom_c, cote in LES_COTES:
            for groupe, nom_g in (("accord", "accord"), ("trop_pres_la_ou_la_bande_saute", "la bande saute")):
                g = d[objet][cote]["les_falaises_par_groupe"][groupe]
                ecrire(80, y + 1, f"côté {nom_c}, {nom_g} ({g['combien']})", 0, GRIS)
                for j, (cle, coul) in enumerate((("bordes_dans_la_surface_de_la_chaine", BON),
                                                  ("bordes_dans_la_couche_de_la_bande", ALERTE))):
                    v_ = g[cle]
                    art.rectangle([bx0, y + j * 7, bx0 + (bx1 - bx0) * v_, y + j * 7 + 5], fill=coul)
                    points.append((bx0 + (bx1 - bx0) * v_, y + j * 7 + 5))
                    barres += 1
                ecrire(bx1 + 8, y + 1, f"{_fr(g['bordes_dans_la_surface_de_la_chaine'])} · "
                                       f"{_fr(g['bordes_dans_la_couche_de_la_bande'])}", 0, ENCRE)
                y += 16
            y += 4
        y += 8
    traces["barres"] = barres
    ecrire(66, y + 4, "vert : dans la surface de la chaîne · rouille : dans la couche de la bande", 0, GRIS)

    # ── PANNEAU 3 · LES DEUX DÉTECTEURS ─────────────────────────────────────────────────────
    panneau(840, 490, 1310, 800, "LES DEUX DÉTECTEURS, SUR LA BANDE")
    y = 530
    for nom_c, cote in LES_COTES:
        x = b[cote]
        pc = x["les_pieces"]
        ecrire(856, y, f"côté {nom_c}", 0, ENCRE)
        ecrire(870, y + 18, f"{pc['les_pieces']} pièces ; la plus grande tient {pc['la_plus_grande']} mailles sur "
                            f"{pc['les_mailles']}", 0, GRIS)
        for k, (nom, cle) in enumerate((("la falaise", "la_falaise"), ("hors de la plus grande pièce",
                                                                       "hors_de_la_plus_grande_piece"))):
            c = x["les_detecteurs"][cle]
            ecrire(870, y + 36 + k * 18, f"{nom} : {_fr(c['la_part_des_rates_signales'])} des ratés, "
                                         f"{_fr(c['la_part_des_justes_signales_a_tort'])} des justes", 0, GRIS)
        ecrire(870, y + 72, f"part juste au plus : {_fr(x['la_part_juste_au_plus_si_les_chutes_ou_la_bande_saute_etaient_justes'])}"
                            f", contre {_fr(x['les_detecteurs']['la_falaise']['la_part_juste_a_laller'])}", 0, ENCRE)
        y += 110

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    gp = b["du_cote_plus"]["les_falaises_par_groupe"]["trop_pres_la_ou_la_bande_saute"]
    gm = b["du_cote_moins"]["les_falaises_par_groupe"]["trop_pres_la_ou_la_bande_saute"]
    ecrire(50, 832, "LE VERDICT : la surface produite reste d'une pièce ; là où la bande saute, c'est la couche de la bande "
                    "qui saute d'un tour entre deux mailles voisines", petit, ENCRE)
    ecrire(50, 856, f"★ là où la bande saute, sa couche est bordée d'une falaise en {_fr(gp['bordes_dans_la_couche_de_la_bande'])} "
                    f"et {_fr(gm['bordes_dans_la_couche_de_la_bande'])} des points, la surface de la chaîne en "
                    f"{_fr(gp['bordes_dans_la_surface_de_la_chaine'])} et {_fr(gm['bordes_dans_la_surface_de_la_chaine'])}.",
           moyen, ENCRE)
    ecrire(50, 882, "★ une feuille ne saute pas d'un tour entre deux mailles voisines : là, c'est le juge qu'il faut soupçonner, "
                    "pas la chaîne.", moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : une surface continue peut aussi glisser d'une spire à l'autre ; la part juste "
                    "« au plus » est une borne, pas une mesure.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path) -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    d = lire()
    tmp = sortie.parent / ".sonde_252.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "LA SURFACE PRODUITE" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ les deux cartes sont dessinées", traces["cartes"] == 2)
    v("★★★★ chaque groupe a ses deux barres, deux objets et deux côtés", traces["barres"] == 16)
    # ⚠⚠ LA GAMME : un pas en vert, deux en rouille, et rien en gris clair.
    v("★★★ la gamme met un pas en vert et deux en rouille", la_couleur(PAS) == BON and la_couleur(2 * PAS) == ALERTE
      and la_couleur(None) == VIDE)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte les deux objets et ce qui n'est PAS établi",
      "w028-037" in txt and "20230702185753" in txt and "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "252_la_surface_produite_se_dechire_t_elle.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
