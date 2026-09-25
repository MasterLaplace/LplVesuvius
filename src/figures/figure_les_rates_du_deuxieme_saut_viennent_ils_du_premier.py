"""Les ratés du deuxième saut, rangés : hérités du premier saut, ou propres au deuxième.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour le témoin et pour la chaîne partie de la spire corrigée, les
ratés du deuxième saut coupés en deux : ceux dont le premier saut avait raté, et ceux dont le premier saut était juste. À
droite, où tombent les ratés propres, et ce que la spire corrigée change au deuxième saut selon que le premier a changé.

  uv run python src/figures/figure_les_rates_du_deuxieme_saut_viennent_ils_du_premier.py \\
      --sortie docs/images/277_les_rates_du_deuxieme_saut_viennent_ils_du_premier.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_rates_du_deuxieme_saut_viennent_ils_du_premier.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
HERITE = (214, 170, 140)
L_, H_ = 1360, 760
LES_CHAINES = (("le_temoin", "témoin, parti du segment"), ("partie_de_la_spire_corrigee", "partie de la spire corrigée"))


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def le_titre(d: dict) -> str:
    o = d["partie_de_la_spire_corrigee"]
    return (f"AU DEUXIÈME SAUT DE LA CHAÎNE PARTIE DE LA SPIRE CORRIGÉE, {o['les_propres']} RATÉS PROPRES ET "
            f"{o['les_herites']} RATÉS HÉRITÉS DU PREMIER")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"barres": [], "lignes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    o = d["partie_de_la_spire_corrigee"]
    ecrire(50, 52, f"20230702185753 · m7, côté plus · les deux chaînes de 276 · {o['les_points_notes_aux_deux_sauts']} points "
                   f"notés aux deux premiers sauts · le juge ne sert qu'à noter", petit, GRIS)

    # ── PANNEAU 1 · HÉRITÉS OU PROPRES ─────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 640, 640, "LES RATÉS DU DEUXIÈME SAUT, HÉRITÉS OU PROPRES")
    bx0, bx1 = 90, 600
    total = max(d[k]["les_rates_du_deuxieme_saut"] for k, _ in LES_CHAINES) or 1
    for i, (k, nom) in enumerate(LES_CHAINES):
        y = 170 + 190 * i
        r = d[k]
        ecrire(bx0, y - 30, f"{nom} : {r['les_rates_du_deuxieme_saut']} ratés", moyen, ENCRE)
        x = bx0
        for cle, coul, lib in (("les_herites", HERITE, "hérités"), ("les_propres", ALERTE, "propres")):
            w = r[cle] / total * (bx1 - bx0)
            art.rectangle([x, y, x + w, y + 44], fill=coul)
            points.append((x + w, y + 44))
            traces["barres"].append((k, cle, r[cle]))
            x += w
        ecrire(bx0, y + 54, f"hérités du premier saut : {r['les_herites']}", 0, ENCRE)
        ecrire(bx0, y + 72, f"propres au deuxième, le premier était juste : {r['les_propres']}", 0, ENCRE)
    ecrire(bx0, 560, f"notés au deuxième saut seulement, rangés nulle part : "
                     f"{o['les_points_notes_au_deuxieme_saut_seulement']}", 0, GRIS)
    for k, (coul, texte) in enumerate(((HERITE, "hérité : le premier saut avait raté"),
                                       (ALERTE, "propre : le premier saut était juste"))):
        art.rectangle([bx0, 590 + 20 * k, bx0 + 12, 602 + 20 * k], fill=coul)
        ecrire(bx0 + 18, 589 + 20 * k, texte, 0, ENCRE)

    # ── PANNEAU 2 · LES RATÉS PROPRES, ET CE QUE LA SPIRE CORRIGÉE CHANGE ─────────────────────────────────────────────
    panneau(660, 80, 1310, 640, "OÙ TOMBENT LES RATÉS PROPRES")
    colonnes = [(690, "chaîne"), (900, "trop près"), (990, "trop loin"), (1080, "sur la 1re couche"), (1210, "n'avance pas")]
    for x, t in colonnes:
        ecrire(x, 140, t, 0, GRIS)
    for i, (k, nom) in enumerate(LES_CHAINES):
        p_ = d[k]["parmi_les_propres"]
        y = 168 + 30 * i
        for (x, _), t in zip(colonnes, (nom, str(p_["trop_pres"]), str(p_["trop_loin"]),
                                        str(p_["retombes_sur_la_premiere_couche"]), str(p_["dun_saut_qui_navance_pas"]))):
            ecrire(x, y, t, 0, ENCRE)
        traces["lignes"] += 1
    ecrire(674, 290, "CE QUE LA SPIRE CORRIGÉE CHANGE AU DEUXIÈME SAUT", moyen, ENCRE)
    colonnes2 = [(690, ""), (960, "le premier saut a changé"), (1150, "il est le même")]
    for x, t in colonnes2:
        ecrire(x, 322, t, 0, GRIS)
    ch = d["les_changements_du_deuxieme_saut"]
    for i, (cle, lib) in enumerate((("les_rates_rendus_justes", "ratés rendus justes"),
                                    ("les_justes_rendus_rates", "justes rendus ratés"))):
        y = 350 + 30 * i
        for (x, _), t in zip(colonnes2, (lib, str(ch[cle]["le_premier_saut_a_change"]),
                                         str(ch[cle]["le_premier_saut_est_le_meme"]))):
            ecrire(x, y, t, 0, ENCRE)
        traces["lignes"] += 1

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 656, L_, H_], fill=BANDE)
    ecrire(50, 668, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 690, "les deux chaînes redonnent le deuxième saut de 276 compte pour compte, et le premier saut du témoin est "
                    "la spire produite", moyen, ENCRE)
    ecrire(50, 714, "⚠ ce qui n'est PAS établi : pourquoi un saut parti d'un point juste rate ; une correction du deuxième "
                    "saut.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path, mesure: Path = LA_MESURE) -> int:
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

    d = lire(mesure)
    tmp = sortie.parent / ".sonde_277.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    o = d["partie_de_la_spire_corrigee"]
    v("★★★ le titre LIT la mesure", f"{o['les_propres']} RATÉS PROPRES" in le_titre(d)
      and f"{o['les_herites']} RATÉS HÉRITÉS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [(k, c, d[k][c]) for k, _ in LES_CHAINES for c in ("les_herites", "les_propres")]
    v("★★★★ deux segments par chaîne, hérités puis propres, et leurs longueurs sont les comptes mesurés",
      traces["barres"] == attendu, str(traces["barres"]))
    v("★★★★ hérités et propres font tous les ratés du deuxième saut, pour chaque chaîne",
      all(d[k]["les_herites"] + d[k]["les_propres"] == d[k]["les_rates_du_deuxieme_saut"] for k, _ in LES_CHAINES))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "277_les_rates_du_deuxieme_saut_viennent_ils_du_premier.png")
    p.add_argument("--mesure", type=Path, default=LA_MESURE)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie, a.mesure)
    chemin, *_ = dessiner(lire(a.mesure), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
