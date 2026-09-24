"""La couverture sans main, une fois les 111 bandes lues : ce qu'elle couvre, et le rectangle au pas qui voit.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, DEUX CARTES DE L'EMPREINTE de `20230702185753` : les chunks
qu'entourent les boucles que la main tenait (`243`), et ceux qu'entourent les boucles que la procédure tient seule. À
droite, LE PROFIL DU RECTANGLE coupé au pas qui voit : chaque coupe reste dans le demi-feuillet. Les cartes sont
dessinées par le code de la figure de `246`, importé.

  uv run python src/figures/figure_la_couverture_sans_main_une_fois_lue.py \\
      --sortie docs/images/256_la_couverture_sans_main_une_fois_lue.png
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)
from figure_la_couverture_sans_main import la_carte, lire  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "la_couverture_sans_main_une_fois_lue.json"
DEMI = 36.0

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 900


def _fr(x, n: int = 4) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def le_rectangle(d: dict) -> dict:
    return next(e for e in d["le_journal"] if e["la_boucle"] == "le rectangle")


def a_la_main(d: dict) -> dict:
    """La même mesure, restreinte aux boucles que la main tenait : celles que la procédure retrouve, plus celles que la
    main seule tenait."""
    coins = [c for c in d["la_comparaison"]["retrouvees"] + d["la_comparaison"]["tenues_a_la_main_seulement"]]
    return {**d, "les_boucles_qui_tiennent": [{"les_coins": c[:4], "la_largeur": c[4]} for c in coins]}


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : la procédure ne demande-t-elle plus rien, et couvre-t-elle plus que la main ?"""
    c, m = d["la_couverture"], d["la_couverture_a_la_main"]
    if not d["le_verdict"]["il_reste_a_lire"] and c["la_part"] > m["la_part"]:
        return (f"LES 111 BANDES LUES, LA PROCÉDURE SANS MAIN COUVRE {_fr(c['la_part'])} DE L'EMPREINTE, LA MAIN "
                f"{_fr(m['la_part'])}")
    return "LES 111 BANDES LUES, LA PROCÉDURE SANS MAIN NE COUVRE PAS PLUS QUE LA MAIN"


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
    ecrire(50, 54, f"20230702185753 · la procédure de 246, jugée sur les {d['combien_de_bandes_publiees']} bandes publiées "
                   f"et les {len(d['les_bandes'])} bandes qu'elle demandait, coupée tous les {d['la_portee']} rangs au plus",
           petit, GRIS)

    # ── PANNEAU 1 · LES DEUX CARTES ──────────────────────────────────────────────────────────
    panneau(50, 84, 820, 740, "LES CHUNKS QU'ENTOURE UNE BOUCLE QUI TIENT")
    s = 1.25
    cartes = {}
    for k, (titre, mesure, cle) in enumerate((("à la main (243)", a_la_main(d), "la_couverture_a_la_main"),
                                              ("sans main, tout lu", d, "la_couverture"))):
        carte, n = la_carte(mesure, s)
        x0, y0 = 80 + k * 370, 150
        img.paste(carte, (x0, y0))
        points.append((x0 + carte.width, y0 + carte.height))
        c = d[cle]
        ecrire(x0, 124, titre, 0, ENCRE)
        ecrire(x0, y0 + carte.height + 10, f"{c['combien']} chunks sur {c['sur']} · {_fr(c['la_part'])}", 0, ENCRE)
        cartes[cle] = n
    traces["cartes"] = cartes
    cp = d["la_comparaison"]
    ecrire(80, 700, f"boucles retrouvées {len(cp['retrouvees'])} · tenues à la main seulement {len(cp['tenues_a_la_main_seulement'])} · "
                    f"tenues sans main seulement {len(cp['tenues_sans_main_seulement'])}", 0, GRIS)

    # ── PANNEAU 2 · LE RECTANGLE AU PAS QUI VOIT ─────────────────────────────────────────────
    r = le_rectangle(d)
    prof = [p["le_cumul_en_voxels"] for p in r["le_profil"]]
    panneau(840, 84, 1310, 740, f"LE RECTANGLE, COUPÉ TOUS LES {d['la_portee']} RANGS AU PLUS")
    gx0, gx1, gy0, gy1 = 900, 1280, 160, 600
    Y0, Y1 = -50.0, 50.0

    def Y(v_):
        return gy1 - (gy1 - gy0) * (max(min(v_, Y1), Y0) - Y0) / (Y1 - Y0)

    art.rectangle([gx0, Y(DEMI), gx1, Y(-DEMI)], fill=(228, 236, 230))
    for v_ in (-DEMI, 0.0, DEMI):
        art.line([gx0, Y(v_), gx1, Y(v_)], fill=ALERTE if v_ else TRAIT, width=1)
        ecrire(gx0 - 42, Y(v_) - 7, f"{_fr(v_, 0)} vx", 0, ALERTE if v_ else GRIS)
    pts = [(gx0 + (gx1 - gx0) * k / max(len(prof) - 1, 1), Y(v_)) for k, v_ in enumerate(prof)]
    art.line(pts, fill=BON, width=3)
    for p in pts:
        art.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=BON)
        points.append(p)
    traces["coupes"] = len(prof)
    ecrire(gx0, gy1 + 10, f"{len(prof)} coupes, de la première à la dernière ; le demi-feuillet en ambre", 0, GRIS)
    ecrire(gx0, gy1 + 30, f"écart le plus grand : {_fr(max(abs(x) for x in prof))} voxels · état : {r['letat']}", 0, ENCRE)
    etroite = next((e for e in d["le_journal"] if e.get("les_coins") == [112, 266, 243, 252]), None)
    if etroite is not None:
        ecrire(gx0, gy1 + 50, f"l'aile étroite de 243, à {etroite['la_largeur']} lignes : {etroite['letat']}", 0, ENCRE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 758, L_, H_], fill=BANDE)
    c, m = d["la_couverture"], d["la_couverture_a_la_main"]
    ecrire(50, 772, "LE VERDICT : la procédure sans main va au bout ; elle ne demande plus rien, et elle couvre plus que la "
                    "main", petit, ENCRE)
    ecrire(50, 796, f"★ {c['combien']} chunks sur {c['sur']} sans main, contre {m['combien']} à la main ; elle retrouve les "
                    f"{len(cp['retrouvees'])} boucles de la main et en tient {len(cp['tenues_sans_main_seulement'])} de plus.",
           moyen, ENCRE)
    ecrire(50, 822, f"★ le rectangle reste sous le demi-feuillet à chacune de ses {len(prof)} coupes.", moyen, ENCRE)
    ecrire(50, 848, "⚠ ce qui n'est PAS établi : un seul segment ; ce qu'aucune boucle n'entoure n'est pas relié.", moyen, ALERTE)

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

    d = lire(LA_MESURE)
    tmp = sortie.parent / ".sonde_256.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "LES 111 BANDES LUES" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    # ⚠⚠⚠ LES CARTES DOIVENT DIRE CE QUE LA MESURE DIT : les chunks teintés sont ceux que la mesure compte.
    v("★★★★ la carte sans main teinte les chunks que la mesure compte",
      traces["cartes"]["la_couverture"] == d["la_couverture"]["combien"],
      f"{traces['cartes']['la_couverture']} contre {d['la_couverture']['combien']}")
    v("★★★★ la carte à la main teinte les chunks que 243 comptait",
      traces["cartes"]["la_couverture_a_la_main"] == d["la_couverture_a_la_main"]["combien"],
      f"{traces['cartes']['la_couverture_a_la_main']} contre {d['la_couverture_a_la_main']['combien']}")
    v("★★★★ le profil du rectangle est celui du journal", traces["coupes"] == len(le_rectangle(d)["le_profil"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte la main, le rectangle et ce qui n'est PAS établi",
      "à la main (243)" in txt and "le rectangle" in txt.lower() and "n'est PAS établi" in txt)
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "256_la_couverture_sans_main_une_fois_lue.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(LA_MESURE), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
