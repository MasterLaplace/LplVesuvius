"""L'étroite reste-t-elle sans écart : les profils des trois familles de sous-boucles, coupe après coupe.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LES PROFILS : la fermeture cumulée depuis la rangée 26 de
l'aile, de l'étroite et de la large, sur le même axe des rangées, contre le demi-feuillet — c'est le panneau qui
conclut. À droite, LES SOUS-BOUCLES, intervalle par intervalle, les trois familles côte à côte. En bas, le verdict.

  uv run python src/figures/figure_letroite_reste_t_elle_sans_ecart.py \\
      --json docs/mesures/letroite_reste_t_elle_sans_ecart.json \\
      --sortie docs/images/237_letroite_reste_t_elle_sans_ecart.png
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
OCRE = (190, 150, 60)
L_, H_ = 1360, 1000
FAMILLES = ("laile", "letroite", "la_large")
NOMS = {"laile": "l'aile", "letroite": "l'étroite", "la_large": "la large"}
COUL = {"laile": CONTRE, "letroite": BON, "la_large": OCRE}


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path) -> dict:
    """Le JSON de `letroite_reste_t_elle_sans_ecart.py`, et le demi-feuillet de `224`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("laile", "le_verdict", "les_coupes_de_letroite"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["le_demi_pli"] = float(json.loads(CE_QUE_224_A_RENDU.read_text())["le_demi_pli_en_voxels"])
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer, dans l'ordre de priorité des issues."""
    v = d["le_verdict"]
    if v["combien_de_sous_boucles"] < 2:
        return "AUCUNE COUPE NE TIENT DANS L'ÉTROITE"
    if v["les_sous_boucles_ouvertes"]:
        return "À NEUF LIGNES, UN TROU TROP LONG LAISSE UNE SOUS-BOUCLE OUVERTE"
    if v["letroite_franchit"]:
        return "À NEUF LIGNES, L'ÉTROITE ATTEINT LE DEMI-FEUILLET EN CHEMIN"
    return "À NEUF LIGNES, L'ÉTROITE RESTE SOUS LE DEMI-FEUILLET TOUT DU LONG, L'AILE LE FRANCHIT" \
        if (v.get("les_franchissements") or {}).get("laile") else \
        "À NEUF LIGNES, L'ÉTROITE RESTE SOUS LE DEMI-FEUILLET TOUT DU LONG"


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
    coupes = [int(x) for x in d["les_coupes_de_letroite"]]
    lo, hi = coupes[0], coupes[-1]
    prof = d.get("les_profils") or {}
    pf = d.get("par_famille") or {}
    rp = d.get("la_reproduction") or {}
    tl = d["la_troisieme_ligne"]

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"l'étroite, colonnes {tl['la_ligne']} à {tl['la_plus_proche']}, découpée aux {len(coupes) - 2} coupes "
                   f"intérieures de 235 · lues pour cette tranche, elles retombent sur les bandes publiées en "
                   f"{rp.get('combien_de_coutures_relues', 0)} coutures à l'écart {_fr(rp.get('lecart_le_plus_grand'))}",
           petit, GRIS)

    # ── PANNEAU 1 · LES PROFILS ──────────────────────────────────────────────────────────────
    panneau(50, 84, 660, 800, "LES PROFILS · la fermeture cumulée depuis la rangée 26")
    Y0, Y1 = 150, 700
    tous = [abs(float(p["le_cumul_en_voxels"])) for n in FAMILLES for p in prof.get(n, [])]
    PM = max(tous + [demi]) + 6.0
    PX0, PW = 355, 250

    def PX(x):
        return PX0 + PW * float(x) / PM

    def Y(r):
        return Y0 + (Y1 - Y0) * (float(r) - lo) / max(1.0, float(hi - lo))
    for x_ in (-demi, demi):
        art.line([PX(x_), Y0 - 6, PX(x_), Y1 + 6], fill=ALERTE, width=1)
    art.line([PX0, Y0 - 6, PX0, Y1 + 6], fill=GRIS, width=1)
    ecrire(PX(-demi) - 14, Y1 + 10, f"−{_fr(demi)}", 0, ALERTE)
    ecrire(PX0 - 3, Y1 + 10, "0", 0, GRIS)
    ecrire(PX(demi) - 8, Y1 + 10, f"{_fr(demi)}", 0, ALERTE)
    ecrire(66, Y0 - 8, f"rangée {lo}", 0, GRIS)
    ecrire(66, Y1 - 8, f"rangée {hi}", 0, GRIS)
    n_p = 0
    for n in FAMILLES:
        pts = [(PX(0.0), Y(lo))] + [(PX(p["le_cumul_en_voxels"]), Y(p["la_coupe"])) for p in prof.get(n, [])]
        if len(pts) > 1:
            art.line(pts, fill=COUL[n], width=2 if n == "letroite" else 1)
        for (x_, y_), p in zip(pts[1:], prof.get(n, [])):
            loin = abs(float(p["le_cumul_en_voxels"])) >= demi
            art.ellipse([x_ - 3, y_ - 3, x_ + 3, y_ + 3], fill=ALERTE if loin else COUL[n])
            points.append((x_, y_))
        n_p += 1
    traces["profils"] = n_p
    yy = 740
    for i, n in enumerate(FAMILLES):
        x0 = 66 + 190 * i
        art.rectangle([x0, yy + 4, x0 + 14, yy + 10], fill=COUL[n])
        bout = prof.get(n, [{}])[-1].get("le_cumul_en_voxels")
        ecrire(x0 + 20, yy, f"{NOMS[n]} · au bout {_fr(bout)}", 0, ENCRE)
    ecrire(66, 764, f"traits bruns : le demi-feuillet, à ±{_fr(demi)} voxels · en brun, un point où le cumul l'atteint",
           0, GRIS)

    # ── PANNEAU 2 · LES SOUS-BOUCLES ─────────────────────────────────────────────────────────
    panneau(680, 84, 1310, 800, "LES SOUS-BOUCLES · intervalle par intervalle, à neuf lignes")
    BX0, BW, VMAX = 990, 150, 20.0

    def BX(x):
        return BX0 + BW * max(-VMAX, min(VMAX, float(x))) / VMAX
    art.line([BX0, Y0 - 6, BX0, Y1 + 6], fill=GRIS, width=1)
    n_s = 0
    for j, sb in enumerate(pf.get("letroite") or []):
        r_, s_ = sb["entre"]
        ym = (Y(r_) + Y(s_)) / 2
        ecrire(696, ym - 7, f"rangées {r_} à {s_}", 0, ENCRE)
        for i, n in enumerate(FAMILLES):
            x = pf[n][j]["par_largeur"][k1]
            yb = ym - 7 + 5 * i
            if not x["fermable"]:
                art.rectangle([BX(-VMAX), yb, BX(VMAX), yb + 3], outline=ALERTE)
                continue
            L = float(x["la_fermeture_en_voxels"])
            art.rectangle([min(BX0, BX(L)), yb, max(BX0, BX(L)), yb + 3], fill=COUL[n])
            points.append((BX(L), yb))
        xe = sb["par_largeur"][k1]
        if xe["fermable"]:
            ecrire(BX(VMAX) + 12, ym - 7, f"{_fr(xe['la_fermeture_en_voxels'])}", 0, BON)
        n_s += 1
    traces["sous_boucles"] = n_s
    ecrire(BX(-VMAX) - 16, Y1 + 10, f"−{_fr(VMAX)}", 0, GRIS)
    ecrire(BX(VMAX) - 8, Y1 + 10, f"{_fr(VMAX)}", 0, GRIS)
    ecrire(696, 740, "barres, de haut en bas : l'aile, l'étroite, la large ; chiffre : l'étroite", 0, GRIS)
    ecrire(696, 758, f"coupées à ±{_fr(VMAX)} voxels", 0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    pic = v.get("le_pic_de_letroite")
    fr = v.get("les_franchissements") or {}
    if pic:
        ecrire(50, 856, f"★ le cumul de l'étroite va au plus à {_fr(pic['le_cumul_en_voxels'])} voxels, à la coupe "
                        f"{pic['la_coupe']} ; celui de l'aile atteint le demi-feuillet à {len(fr.get('laile') or [])} "
                        f"coupes, celui de la large à {len(fr.get('la_large') or [])}.", moyen, ENCRE)
    ecrire(50, 882, "★ les sous-boucles de l'aile retombent sur 235, celles de l'étroite sur 236, et dans chaque "
                    "intervalle la large est la somme des deux autres.", moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : pourquoi la colonne 260 dérive, ni si les deux colonnes qui "
                    "s'accordent sont justes.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_237.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(m, ouv, fr, fa):
        return {"le_verdict": {"combien_de_sous_boucles": m, "les_sous_boucles_ouvertes": ouv, "letroite_franchit": fr,
                               "les_franchissements": {"laile": [1] if fa else []}}}
    tous = [_v(1, [], False, False), _v(3, [[0, 9]], False, False), _v(3, [], True, False), _v(3, [], False, True),
            _v(3, [], False, False)]
    v("★★★★ les cinq titres possibles sont distincts, et l'ordre des issues prime",
      len({le_titre(x) for x in tous}) == 5 and le_titre(_v(1, [[0, 9]], True, True)) == le_titre(tous[0])
      and le_titre(_v(3, [[0, 9]], True, True)) == le_titre(tous[1]))
    v("★★★ le titre LIT le verdict", ("RESTE SOUS" in le_titre(d)) == bool(d["le_verdict"].get("letroite_reste_dessous")))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    n_sb = len(d["les_coupes_de_letroite"]) - 1
    v("★★★★ trois profils, et chaque intervalle a ses trois barres",
      traces.get("profils") == 3 and traces.get("sous_boucles") == n_sb)
    txt = " ".join(t for _, _, t, _ in poses)
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    v("★★★★ elle porte la fermeture de chaque sous-boucle de l'étroite, le bout de chaque profil, et ce qui n'est PAS "
      "établi",
      all(_fr(sb["par_largeur"][k1]["la_fermeture_en_voxels"]) in txt for sb in d["par_famille"]["letroite"]
          if sb["par_largeur"][k1]["fermable"])
      and all(_fr(d["les_profils"][n][-1]["le_cumul_en_voxels"]) in txt for n in FAMILLES)
      and "n'est PAS établi" in txt)
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
    p.add_argument("--json", type=Path, default=RACINE / "docs" / "mesures" / "letroite_reste_t_elle_sans_ecart.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "237_letroite_reste_t_elle_sans_ecart.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
