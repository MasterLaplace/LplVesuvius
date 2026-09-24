"""Où l'aile de droite se sépare : ses sous-boucles d'une coupe à l'autre, et la fermeture qu'elles cumulent.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LES SOUS-BOUCLES : la fermeture de chacune à neuf
lignes, rangée après rangée, contre le demi-feuillet — c'est le panneau qui conclut. En haut à droite, LE PROFIL :
la fermeture cumulée coupe après coupe, sur le même axe des rangées, jusqu'à celle que `234` publie pour l'aile.
En bas à droite, L'EMBOÎTEMENT : la somme des sous-boucles contre l'aile, largeur par largeur.

  uv run python src/figures/figure_ou_laile_de_droite_se_separe.py \\
      --json docs/mesures/ou_laile_de_droite_se_separe.json \\
      --sortie docs/images/235_ou_laile_de_droite_se_separe.png
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
LIB = {"haut": "l'aile du haut", "droite": "l'aile de droite", "bas": "l'aile du bas", "gauche": "l'aile de gauche"}


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path) -> dict:
    """Le JSON de `ou_laile_de_droite_se_separe.py`, et le demi-feuillet de `224`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("laile", "le_decoupage", "le_verdict"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["le_demi_pli"] = float(json.loads(CE_QUE_224_A_RENDU.read_text())["le_demi_pli_en_voxels"])
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer, dans l'ordre de priorité des issues."""
    v = d["le_verdict"]
    aile = LIB[d["laile"]["le_cote"]].upper()
    if v["combien_de_sous_boucles"] < 2:
        return f"AUCUNE COUPE NE TIENT DANS {aile}"
    if v["les_sous_boucles_ouvertes"]:
        return "À NEUF LIGNES, UN TROU TROP LONG LAISSE UNE SOUS-BOUCLE OUVERTE"
    if v["les_sous_boucles_a_un_demi_feuillet"]:
        return f"À NEUF LIGNES, {aile} CHANGE DE SPIRE ENTRE DEUX COUPES"
    return f"À NEUF LIGNES, L'ÉCART DE {aile} SE CUMULE D'UNE COUPE À L'AUTRE"


def les_franchissements(d: dict) -> list[dict]:
    """Les coupes où la fermeture cumulée depuis le premier bout atteint le demi-feuillet."""
    return [p for p in d.get("le_profil") or [] if abs(float(p["le_cumul_en_voxels"])) >= d["le_demi_pli"]]


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
    aile = d["laile"]
    dec = d["le_decoupage"]
    coupes = [int(x) for x in dec["les_coupes"]]
    a0, a1, b0, b1 = [int(x) for x in aile["les_coins"]]
    v = d["le_verdict"]
    k1 = str(v["la_largeur_jugee"])
    sbs = d.get("par_sous_boucle") or []
    rp = d.get("la_reproduction") or {}

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"{LIB[aile['le_cote']]} de 234, rangées {a0} à {a1} et colonnes {b0} à {b1}, découpée en "
                   f"{dec['combien_de_sous_boucles']} sous-boucles par les coupes qui y tiennent · lues pour cette "
                   f"tranche, les coupes retombent sur les bandes publiées en {rp.get('combien_de_coutures_relues', 0)} "
                   f"coutures à l'écart {_fr(rp.get('lecart_le_plus_grand'))}", petit, GRIS)

    lo, hi = coupes[0], coupes[-1]
    Y0, Y1 = 150, 740

    def Y(r):
        return Y0 + (Y1 - Y0) * (float(r) - lo) / max(1.0, float(hi - lo))

    # ── PANNEAU 1 · LES SOUS-BOUCLES ─────────────────────────────────────────────────────────
    panneau(50, 84, 700, 800, "LES SOUS-BOUCLES · la fermeture de chacune, à neuf lignes")
    BX0, BW, VMAX = 385, 175, 40.0

    def BX(x):
        return BX0 + BW * max(-VMAX, min(VMAX, float(x))) / VMAX
    for x_ in (-demi, demi):
        art.line([BX(x_), Y0 - 6, BX(x_), Y1 + 6], fill=ALERTE, width=1)
    art.line([BX0, Y0 - 6, BX0, Y1 + 6], fill=GRIS, width=1)
    ecrire(BX(-demi) - 12, Y1 + 10, f"−{_fr(demi)}", 0, ALERTE)
    ecrire(BX0 - 32, Y1 + 10, "demi-feuillet", 0, ALERTE)
    ecrire(BX(demi) - 6, Y1 + 10, f"{_fr(demi)}", 0, ALERTE)
    n_ = 0
    for sb in sbs:
        r_, s_ = [int(x) for x in sb["entre"]]
        ya, yb = Y(r_), Y(s_)
        ym = (ya + yb) / 2
        ecrire(66, ym - 7, f"rangées {r_} à {s_}", 0, ENCRE)
        x = sb["par_largeur"][k1]
        if not x["fermable"]:
            art.rectangle([BX(-VMAX), ym - 5, BX(VMAX), ym + 5], outline=ALERTE)
            ecrire(BX(VMAX) + 12, ym - 7, "ouverte", 0, ALERTE)
        else:
            L = float(x["la_fermeture_en_voxels"])
            coul = BON if x["sous_le_demi_pli"] else ALERTE
            art.rectangle([min(BX0, BX(L)), ym - 5, max(BX0, BX(L)), ym + 5], fill=coul)
            med = float(x["le_nul"]["la_fermeture_mediane_en_valeur_absolue"])
            for m_ in (-med, med):
                art.line([BX(m_), ym - 7, BX(m_), ym + 7], fill=ENCRE, width=1)
            points.append((BX(L), ym))
            ecrire(BX(VMAX) + 12, ym - 7, f"{_fr(L)} · {_fr(x['le_nul']['la_part_sous_la_fermeture'])}", 0, ENCRE)
        art.line([60, yb, 690, yb], fill=TRAIT, width=1)
        n_ += 1
    traces["sous_boucles"] = n_
    ecrire(66, 762, "barre : la fermeture, en voxels · traits : la médiane du bruit seul, de part et d'autre", 0, GRIS)
    ecrire(66, 778, "chiffres : la fermeture · la part du bruit seul qui ferme plus serré", 0, GRIS)

    # ── PANNEAU 2 · LE PROFIL ────────────────────────────────────────────────────────────────
    panneau(720, 84, 1310, 800 - 170, "LE PROFIL · la fermeture cumulée, coupe après coupe")
    prof = d.get("le_profil") or []
    PX0, PW = 1015, 230
    PM = max([abs(float(p["le_cumul_en_voxels"])) for p in prof] + [demi]) + 4.0

    def PX(x):
        return PX0 + PW * float(x) / PM
    Yp0, Yp1 = 150, 560

    def YP(r):
        return Yp0 + (Yp1 - Yp0) * (float(r) - lo) / max(1.0, float(hi - lo))
    for x_ in (-demi, demi):
        art.line([PX(x_), Yp0 - 6, PX(x_), Yp1 + 6], fill=ALERTE, width=1)
    art.line([PX0, Yp0 - 6, PX0, Yp1 + 6], fill=GRIS, width=1)
    ecrire(PX(-demi) - 30, Yp1 + 10, f"−{_fr(demi)}", 0, ALERTE)
    ecrire(PX(demi) - 10, Yp1 + 10, f"{_fr(demi)}", 0, ALERTE)
    ecrire(736, Yp0 - 8, f"rangée {lo}", 0, GRIS)
    ecrire(736, Yp1 - 8, f"rangée {hi}", 0, GRIS)
    pts = [(PX(0.0), YP(lo))] + [(PX(p["le_cumul_en_voxels"]), YP(p["la_coupe"])) for p in prof]
    if len(pts) > 1:
        art.line(pts, fill=CONTRE, width=2)
    fr = les_franchissements(d)
    loin = {int(p_["la_coupe"]) for p_ in fr}
    for (x_, y_), c_ in zip(pts, [lo] + [int(p_["la_coupe"]) for p_ in prof]):
        art.ellipse([x_ - 3, y_ - 3, x_ + 3, y_ + 3], fill=ALERTE if c_ in loin else CONTRE)
        points.append((x_, y_))
    traces["profil"] = len(pts)
    if prof:
        ecrire(736, Yp1 + 30, f"au bout, {_fr(prof[-1]['le_cumul_en_voxels'])} voxels ; {LIB[aile['le_cote']]} de 234 "
                              f"ferme à {_fr(aile['la_fermeture_en_voxels'])}", 0, ENCRE)
        ecrire(736, Yp1 + 46, "en brun, une coupe où le cumul depuis la rangée "
                              f"{lo} atteint le demi-feuillet : {len(fr)}", 0, ALERTE if fr else GRIS)
    traces["franchissements"] = len(fr)

    # ── PANNEAU 3 · L'EMBOÎTEMENT ───────────────────────────────────────────────────────────
    panneau(720, 650, 1310, 800, "L'EMBOÎTEMENT · la somme des sous-boucles contre l'aile")
    emb = (d.get("lemboitement") or {}).get("par_largeur") or {}
    yy = 684
    n_e = 0
    for k in sorted(emb, key=int):
        x = emb[k]
        if x["jugeable"]:
            ecrire(736, yy, f"{k} lignes : somme {_fr(x['la_somme_des_sous_boucles'])}, aile "
                            f"{_fr(x['la_fermeture_de_laile'])}, écart {_fr(x['lecart'], 6)}", 0, ENCRE)
        else:
            ecrire(736, yy, f"{k} lignes : un trou sur un long côté, non jugé", 0, GRIS)
        yy += 22
        n_e += 1
    traces["emboitement"] = n_e

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    pg = v.get("la_plus_grande")
    if pg:
        ecrire(50, 856, f"★ la plus grande sous-boucle, rangées {pg['entre'][0]} à {pg['entre'][1]}, ferme à "
                        f"{_fr(pg['la_fermeture_en_voxels'])} voxels ; {len(v['les_sous_boucles_a_un_demi_feuillet'])} "
                        f"sur {v['combien_de_sous_boucles']} atteignent le demi-feuillet.", moyen, ENCRE)
    ecrire(50, 882, "★ la somme des sous-boucles retombe sur la fermeture que 234 publie pour l'aile, à l'arrondi près.",
           moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : lequel des deux longs côtés dérive, ni ce qui reste de l'empreinte "
                    "au-delà des ailes.", moyen, ALERTE)
    if fr:
        ecrire(50, 934, "⚠ en chemin, le cumul atteint le demi-feuillet : " + ", ".join(
            f"{_fr(p_['le_cumul_en_voxels'])} à la coupe {p_['la_coupe']}" for p_ in fr) + ".", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_235.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(m, ouv, loin):
        return {"laile": {"le_cote": "droite"},
                "le_verdict": {"combien_de_sous_boucles": m, "les_sous_boucles_ouvertes": ouv,
                               "les_sous_boucles_a_un_demi_feuillet": loin}}
    tous = [_v(m, o, l_) for m in (1, 3) for o in ([], [[0, 9]]) for l_ in ([], [[0, 9]])]
    v("★★★★ les quatre titres possibles sont distincts, et l'ordre des issues prime",
      len({le_titre(x) for x in tous}) == 4 and le_titre(_v(1, [[0, 9]], [[0, 9]])) == le_titre(_v(1, [], []))
      and le_titre(_v(3, [[0, 9]], [[0, 9]])) == le_titre(_v(3, [[0, 9]], [])))
    v("★★★ le titre LIT le verdict", ("SE CUMULE" in le_titre(d)) == bool(d["le_verdict"]["lecart_se_cumule"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    sbs = d.get("par_sous_boucle") or []
    v("★★★★ chaque sous-boucle a sa barre, et le profil un point par coupe",
      traces.get("sous_boucles") == len(sbs) == d["le_decoupage"]["combien_de_sous_boucles"]
      and traces.get("profil") == len(d.get("le_profil") or []) + 1)
    fr = les_franchissements(d)
    v("★★★★ chaque coupe où le cumul atteint le demi-feuillet est nommée, avec son cumul",
      traces.get("franchissements") == len(fr) and all(
          _fr(p_["le_cumul_en_voxels"]) in " ".join(t for _, _, t, _ in poses) for p_ in fr))
    v("★★★★ chaque largeur a sa ligne d'emboîtement",
      traces.get("emboitement") == len((d.get("lemboitement") or {}).get("par_largeur") or {}) == 4)
    txt = " ".join(t for _, _, t, _ in poses)
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    v("★★★★ elle porte la fermeture de chaque sous-boucle, celle de l'aile, et ce qui n'est PAS établi",
      all(_fr(sb["par_largeur"][k1]["la_fermeture_en_voxels"]) in txt for sb in sbs if sb["par_largeur"][k1]["fermable"])
      and _fr(d["laile"]["la_fermeture_en_voxels"]) in txt and "n'est PAS établi" in txt)
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
    p.add_argument("--json", type=Path, default=RACINE / "docs" / "mesures" / "ou_laile_de_droite_se_separe.json")
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "235_ou_laile_de_droite_se_separe.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
