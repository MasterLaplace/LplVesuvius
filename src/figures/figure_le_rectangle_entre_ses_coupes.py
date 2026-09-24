"""Le rectangle entre ses coupes : les tranches fines, et la fermeture qu'elles cumulent, coupe après coupe.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LES TRANCHES FINES : le rectangle de `233` coupé aux rangées
de `224` et aux coupes de plus, chaque tranche contre son bruit seul, à neuf lignes. À droite, LE PROFIL : la fermeture
cumulée depuis la rangée 26, les coupes de `238` en gros points, contre le demi-feuillet — c'est le panneau qui
conclut. En bas, le verdict.

  uv run python src/figures/figure_le_rectangle_entre_ses_coupes.py \\
      --json docs/mesures/le_rectangle_entre_ses_coupes.json \\
      --sortie docs/images/239_le_rectangle_entre_ses_coupes.png
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
CE_QUE_224_A_RENDU = RACINE / "docs" / "mesures" / "deux_chemins_arrivent_ils_sur_la_meme_spire.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
L_, H_ = 1360, 1000


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path) -> dict:
    """Le JSON de `le_rectangle_entre_ses_coupes.py`, et le demi-feuillet de `224`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("le_rectangle", "le_verdict", "les_coupes"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["le_demi_pli"] = float(json.loads(CE_QUE_224_A_RENDU.read_text())["le_demi_pli_en_voxels"])
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer, dans l'ordre de priorité des issues."""
    v = d["le_verdict"]
    if v["combien_de_tranches"] < 2:
        return "AUCUNE COUPE DE PLUS NE TIENT DANS LE RECTANGLE"
    if v["les_tranches_ouvertes"]:
        return "À NEUF LIGNES, UN TROU TROP LONG LAISSE UNE TRANCHE FINE OUVERTE"
    if v["franchit"]:
        return "À NEUF LIGNES, ENTRE SES COUPES, LE PROFIL DU RECTANGLE ATTEINT LE DEMI-FEUILLET"
    return "À NEUF LIGNES, ENTRE SES COUPES AUSSI, LE PROFIL DU RECTANGLE RESTE SOUS LE DEMI-FEUILLET"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    demi = d["le_demi_pli"]
    v = d["le_verdict"]
    k1 = str(v["la_largeur_jugee"])
    r0, r1, c0, c1 = [int(x) for x in d["le_rectangle"]]
    coupes = [int(x) for x in d["les_coupes"]]
    prof = d.get("le_profil") or []
    pt = d.get("par_tranche") or []
    rp = d.get("la_reproduction") or {}

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    c238 = [int(x) for x in d.get("les_coupes_de_238") or []]
    ecrire(50, 54, f"le rectangle de 233 coupé tous les {d['la_portee']} rangs au plus, la plus longue traversée de 235 · "
                   f"les {len(d.get('les_coupes_de_plus') or [])} coupes de plus retombent sur les bandes publiées en "
                   f"{rp.get('combien_de_coutures_relues', 0)} coutures à l'écart {_fr(rp.get('lecart_le_plus_grand'))}",
           petit, GRIS)
    Y0, Y1 = 150, 700

    def Y(r):
        return Y0 + (Y1 - Y0) * (float(r) - r0) / max(1.0, float(r1 - r0))

    # ── PANNEAU 1 · LES TRANCHES ─────────────────────────────────────────────────────────────
    panneau(50, 84, 560, 800, "LES TRANCHES FINES · chacune contre son bruit seul, à neuf lignes")
    TX0, TW, TMAX = 300, 150, 40.0

    def TX(x):
        return TX0 + TW * max(-TMAX, min(TMAX, float(x))) / TMAX
    for x_ in (-demi, demi):
        art.line([TX(x_), Y0 - 6, TX(x_), Y1 + 6], fill=ALERTE, width=1)
    art.line([TX0, Y0 - 6, TX0, Y1 + 6], fill=GRIS, width=1)
    ecrire(TX(-demi) - 14, Y1 + 10, f"−{_fr(demi)}", 0, ALERTE)
    ecrire(TX0 - 3, Y1 + 10, "0", 0, GRIS)
    ecrire(TX(demi) - 8, Y1 + 10, f"{_fr(demi)}", 0, ALERTE)
    for c in coupes:
        art.line([140, Y(c), 500, Y(c)], fill=GRIS if c in c238 else TRAIT, width=1)
        ecrire(66, Y(c) - 7, f"rangée {c}", 0, ENCRE if c in c238 else GRIS)
    n_t = 0
    for sb in pt:
        a_, b_ = sb["entre"]
        x = sb["par_largeur"][k1]
        ym = (Y(a_) + Y(b_)) / 2
        if x["fermable"]:
            L = float(x["la_fermeture_en_voxels"])
            med = float(x["le_nul"]["la_fermeture_mediane_en_valeur_absolue"])
            art.rectangle([TX(-med), ym - 9, TX(med), ym + 9], fill=BANDE, outline=TRAIT)
            art.rectangle([min(TX0, TX(L)), ym - 4, max(TX0, TX(L)), ym + 4], fill=BON if abs(L) < demi else ALERTE)
            points.append((TX(L), ym))
            ecrire(TX(TMAX) + 14, ym - 7, f"{_fr(L)}", 0, ENCRE)
        else:
            art.rectangle([TX(-TMAX), ym - 6, TX(TMAX), ym + 6], outline=ALERTE)
            ecrire(TX(TMAX) + 14, ym - 7, "ouverte", 0, ALERTE)
        n_t += 1
    traces["tranches"] = n_t
    ecrire(66, 740, "barre : la fermeture de la tranche, en voxels ; fond : ± la médiane du bruit seul", 0, GRIS)
    ecrire(66, 756, "rangées en noir : les coupes de 238 ; en gris : les coupes de plus", 0, GRIS)

    # ── PANNEAU 2 · LE PROFIL ────────────────────────────────────────────────────────────────
    panneau(580, 84, 1310, 800, "LE PROFIL · la fermeture cumulée depuis la rangée 26")
    PM = max([abs(float(p["le_cumul_en_voxels"])) for p in prof] + [demi]) + 6.0
    PX0, PW = 945, 300

    def PX(x):
        return PX0 + PW * float(x) / PM
    for x_ in (-demi, demi):
        art.line([PX(x_), Y0 - 6, PX(x_), Y1 + 6], fill=ALERTE, width=1)
    art.line([PX0, Y0 - 6, PX0, Y1 + 6], fill=GRIS, width=1)
    ecrire(PX(-demi) - 14, Y1 + 10, f"−{_fr(demi)}", 0, ALERTE)
    ecrire(PX0 - 3, Y1 + 10, "0", 0, GRIS)
    ecrire(PX(demi) - 8, Y1 + 10, f"{_fr(demi)}", 0, ALERTE)
    pts = [(PX(0.0), Y(r0))] + [(PX(p["le_cumul_en_voxels"]), Y(p["la_coupe"])) for p in prof]
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):  # en tirets : entre deux coupes, le profil n'est pas vu
        for i in range(0, 20, 2):
            art.line([xa + (xb - xa) * i / 20, ya + (yb - ya) * i / 20,
                      xa + (xb - xa) * (i + 1) / 20, ya + (yb - ya) * (i + 1) / 20], fill=CONTRE, width=2)
    for (x_, y_), p in zip(pts[1:], prof):
        loin = abs(float(p["le_cumul_en_voxels"])) >= demi
        r_ = 5 if int(p["la_coupe"]) in c238 else 3
        art.ellipse([x_ - r_, y_ - r_, x_ + r_, y_ + r_], fill=ALERTE if loin else CONTRE)
        ecrire(596, y_ - 7, f"coupe {p['la_coupe']} : {_fr(p['le_cumul_en_voxels'])}", 0, ALERTE if loin else ENCRE)
        points.append((x_, y_))
    traces["profil"] = len(pts)
    ecrire(596, 740, f"traits bruns : le demi-feuillet, à ±{_fr(demi)} voxels ; en brun, une coupe où le cumul l'atteint",
           0, GRIS)
    ecrire(596, 756, f"gros points : les coupes de 238 ; ⚠ en tirets, entre deux coupes : non vu, sur au plus "
                     f"{d['la_portee']} rangs", 0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    if v.get("le_pic"):
        ecrire(50, 856, f"★ le cumul va au plus à {_fr(v['le_pic']['le_cumul_en_voxels'])} voxels, à la coupe "
                        f"{v['le_pic']['la_coupe']} ; au bout, {_fr(prof[-1]['le_cumul_en_voxels'])}.", moyen, ENCRE)
    ecrire(50, 882, "★ les tranches fines somment au rectangle de 233 et, entre deux coupes de 238, à la tranche de 238.",
           moyen, ENCRE)
    ecrire(50, 908, f"⚠ ce qui n'est PAS établi : une traversée plus courte que {d['la_portee']} rangs, entre deux coupes.",
           moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(json_path: Path, sortie: Path) -> int:
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

    d = lire(json_path)
    tmp = sortie.parent / ".sonde_239.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(m, ouv, fr):
        return {"le_verdict": {"combien_de_tranches": m, "les_tranches_ouvertes": ouv, "franchit": fr}}
    tous = [_v(m, o, f) for m in (1, 4) for o in ([], [[0, 9]]) for f in (False, True)]
    v("★★★★ les quatre titres possibles sont distincts, et l'ordre des issues prime",
      len({le_titre(x) for x in tous}) == 4 and le_titre(_v(1, [[0, 9]], True)) == le_titre(_v(1, [], False))
      and le_titre(_v(4, [[0, 9]], True)) == le_titre(_v(4, [[0, 9]], False)))
    v("★★★ le titre LIT le verdict", ("ATTEINT" in le_titre(d)) == bool(d["le_verdict"].get("franchit")))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque tranche a sa case, et le profil un point par coupe",
      traces.get("tranches") == len(d["les_coupes"]) - 1 and traces.get("profil") == len(d.get("le_profil") or []) + 1)
    txt = " ".join(t for _, _, t, _ in poses)
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    v("★★★★ elle porte la fermeture de chaque tranche, le cumul à chaque coupe, et ce qui n'est PAS établi",
      all(_fr(sb["par_largeur"][k1]["la_fermeture_en_voxels"]) in txt for sb in d["par_tranche"]
          if sb["par_largeur"][k1]["fermable"])
      and all(_fr(p["le_cumul_en_voxels"]) in txt for p in d["le_profil"]) and "n'est PAS établi" in txt)
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
    p.add_argument("--json", type=Path, default=RACINE / "docs" / "mesures" / "le_rectangle_entre_ses_coupes.json")
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "239_le_rectangle_entre_ses_coupes.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
