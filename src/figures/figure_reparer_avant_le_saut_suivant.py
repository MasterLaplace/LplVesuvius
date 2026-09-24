"""Réparer avant le saut suivant : la règle, ce qu'elle fait aux points qu'elle touche, et ce qu'elle rend à la chaîne.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LA RÈGLE DESSINÉE sur une tache signalée de cinq sur cinq : tour
après tour, elle se comble depuis son bord ; c'est le code du module qui la comble, pas un dessin. Au milieu, CE QUE LA
RÉPARATION FAIT AUX POINTS QU'ELLE TOUCHE au premier saut : presque autant de justes rendus faux que de ratés rendus
justes. À droite, LA TENUE DES QUATRE SAUTS avec et sans réparation : elle ne bouge presque pas.

  uv run python src/figures/figure_reparer_avant_le_saut_suivant.py --sortie docs/images/254_reparer_avant_le_saut_suivant.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)
from reparer_avant_le_saut_suivant import reparer  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "reparer_avant_le_saut_suivant.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (150, 185, 170)
CONTRE = (92, 108, 150)
SAIN = (222, 219, 211)
L_, H_ = 1360, 950
LES_COTES = (("plus", "du_cote_plus"), ("moins", "du_cote_moins"))
LES_ISSUES = (("raté devenu juste", "rate_devenu_juste", BON), ("juste devenu raté", "juste_devenu_rate", ALERTE),
              ("resté juste", "reste_juste", PALE), ("resté raté", "reste_rate", (196, 160, 90)))


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    d = json.loads(LA_MESURE.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def le_comblement(tours: int) -> np.ndarray:
    """La tache de cinq sur cinq de la batterie, après `tours` tours de réparation : vrai là où un point a été réparé."""
    H, W = 9, 9
    gi_, gj_ = np.nonzero(np.ones((H, W), bool))

    def grille_(val):
        c = np.full((H, W), np.nan)
        c[gi_, gj_] = val
        return c

    tache = (gi_ >= 2) & (gi_ <= 6) & (gj_ >= 2) & (gj_ <= 6)
    centres = [np.array([75.0, 150.0]) for _ in range(H * W)]
    _, rep = reparer(np.where(tache, 150.0, 72.0), tache, centres, grille_, gi_, gj_, tours=tours)
    return rep.reshape(H, W), tache.reshape(H, W)


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : de combien la réparation fait-elle bouger la tenue des quatre sauts ?"""
    g = [d[c]["en_reparant"]["le_juge_de_248"]["qui_tient"]["la_chaine"]["la_part_qui_tient_tous_les_sauts"]
         - d[c]["sans_reparation"]["le_juge_de_248"]["qui_tient"]["la_chaine"]["la_part_qui_tient_tous_les_sauts"]
         for _, c in LES_COTES]
    if max(abs(x) for x in g) < 0.01:
        return "RÉPARER PAR LES VOISINS AVANT LE SAUT SUIVANT NE FAIT PRESQUE RIEN GAGNER À LA CHAÎNE"
    return "RÉPARER PAR LES VOISINS AVANT LE SAUT SUIVANT CHANGE LA TENUE DE LA CHAÎNE"


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

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, "signalé : le retour ou le désaccord des deux prédictions ; réparé : la médiane de trois voisins sains au "
                   "moins, sur la feuille la plus proche", petit, GRIS)

    # ── PANNEAU 1 · LA RÈGLE ─────────────────────────────────────────────────────────────────
    panneau(50, 84, 470, 800, "LA RÈGLE, TOUR APRÈS TOUR")
    ech = 18
    grilles = 0
    for k, tours in enumerate((0, 1, 2, 3)):
        rep, tache = le_comblement(tours)
        x0 = 80 + (k % 2) * 190
        y0 = 150 + (k // 2) * 230
        ecrire(x0, y0 - 24, "avant" if tours == 0 else f"après {tours} tour{'s' if tours > 1 else ''}", 0, ENCRE)
        for i in range(rep.shape[0]):
            for j in range(rep.shape[1]):
                coul = SAIN if not tache[i, j] else (BON if rep[i, j] else ALERTE)
                art.rectangle([x0 + j * ech, y0 + i * ech, x0 + (j + 1) * ech - 2, y0 + (i + 1) * ech - 2], fill=coul)
        points.append((x0 + rep.shape[1] * ech, y0 + rep.shape[0] * ech))
        grilles += 1
    traces["grilles"] = grilles
    for k, (coul, t) in enumerate(((SAIN, "sain"), (ALERTE, "signalé"), (BON, "réparé"))):
        art.rectangle([80 + k * 120, 634, 94 + k * 120, 646], fill=coul)
        ecrire(100 + k * 120, 632, t, 0, GRIS)
    ecrire(80, 670, "trois voisins sains, c'est un côté entier du carré :", 0, GRIS)
    ecrire(80, 688, "le moins qui laisse la réparation longer un bord droit", 0, GRIS)

    # ── PANNEAU 2 · CE QU'ELLE FAIT ──────────────────────────────────────────────────────────
    panneau(490, 84, 900, 800, "CE QU'ELLE FAIT AU PREMIER SAUT")
    bx0, bx1 = 510, 880
    y = 134
    piles = 0
    for nom_c, cote in LES_COTES:
        c = d[cote]["ce_que_la_reparation_a_fait_au_premier_saut"]
        ecrire(510, y, f"côté {nom_c} · {c['les_points_repares_notes']} points réparés, jugés", 0, ENCRE)
        y += 22
        x = bx0
        for _, cle, coul in LES_ISSUES:
            w = (bx1 - bx0) * c[cle]
            art.rectangle([x, y, x + w, y + 22], fill=coul)
            x += w
        points.append((x, y + 22))
        piles += 1
        y += 32
        for k, (nom, cle, coul) in enumerate(LES_ISSUES):
            art.rectangle([510, y + k * 20 + 3, 522, y + k * 20 + 13], fill=coul)
            ecrire(530, y + k * 20, f"{nom} : {_fr(c[cle])}", 0, ENCRE)
        y += 4 * 20 + 30
    traces["piles"] = piles
    ecrire(510, y, "presque autant de justes rendus ratés", 0, GRIS)
    ecrire(510, y + 18, "que de ratés rendus justes", 0, GRIS)

    # ── PANNEAU 3 · LA TENUE ─────────────────────────────────────────────────────────────────
    panneau(920, 84, 1310, 800, "LA TENUE DES QUATRE SAUTS")
    cx0, cx1 = 940, 1200
    C0, C1 = 0.6, 1.0
    y = 134
    barres = 0
    for juge, nom_j in (("le_juge_de_248", "jugée comme 248"), ("le_juge_sans_falaise", "jugée sans falaise")):
        ecrire(940, y, nom_j, 0, ENCRE)
        y += 22
        for nom_c, cote in LES_COTES:
            for nom_r, cle_r, coul in (("sans réparation", "sans_reparation", PALE), ("en réparant", "en_reparant", BON)):
                v_ = d[cote][cle_r][juge]["qui_tient"]["la_chaine"]["la_part_qui_tient_tous_les_sauts"]
                w = (cx1 - cx0) * (v_ - C0) / (C1 - C0)
                art.rectangle([cx0, y + 14, cx0 + w, y + 24], fill=coul)
                points.append((cx0 + w, y + 24))
                ecrire(940, y, f"côté {nom_c}, {nom_r}", 0, GRIS)
                ecrire(cx1 + 8, y + 12, _fr(v_), 0, ENCRE)
                barres += 1
                y += 34
        y += 20
    traces["barres"] = barres
    ecrire(940, y, "l'échelle commence à 0,6", 0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    cp = d["du_cote_plus"]["ce_que_la_reparation_a_fait_au_premier_saut"]
    tp = [d["du_cote_plus"][k]["le_juge_de_248"]["qui_tient"]["la_chaine"]["la_part_qui_tient_tous_les_sauts"]
          for k in ("sans_reparation", "en_reparant")]
    ecrire(50, 832, "LE VERDICT : la réparation par les voisins ne remplace pas l'humain ; elle défait presque autant qu'elle "
                    "répare", petit, ENCRE)
    ecrire(50, 856, f"★ côté plus, elle rend justes {_fr(cp['rate_devenu_juste'])} des points qu'elle touche et en rend ratés "
                    f"{_fr(cp['juste_devenu_rate'])} ; {_fr(cp['reste_rate'])} restent ratés.", moyen, ENCRE)
    ecrire(50, 882, f"★ la tenue des quatre sauts passe de {_fr(tp[0])} à {_fr(tp[1])} côté plus, jugée comme 248.", moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : une seule règle de réparation, et le diagnostic du premier saut a été ajouté "
                    "après la mesure.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_254.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "RÉPARER PAR LES VOISINS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    # ⚠⚠ LA RÈGLE DESSINÉE EST CELLE DU MODULE : avant, rien ; après trois tours, toute la tache est comblée.
    r0, t0 = le_comblement(0)
    r3, t3 = le_comblement(3)
    v("★★★★ la tache dessinée se comble en trois tours, et rien avant", not r0.any() and r3[t3].all())
    v("★★★★ les quatre issues de chaque côté font un, à l'arrondi près",
      all(abs(sum(d[c]["ce_que_la_reparation_a_fait_au_premier_saut"][k] for _, k, _ in LES_ISSUES) - 1) < 0.002
          for _, c in LES_COTES))
    v("★★★ les quatre grilles, les deux piles et les huit barres sont dessinées",
      traces["grilles"] == 4 and traces["piles"] == 2 and traces["barres"] == 8)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte les deux juges et ce qui n'est PAS établi",
      "jugée comme 248" in txt and "sans falaise" in txt and "n'est PAS établi" in txt)
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "254_reparer_avant_le_saut_suivant.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
