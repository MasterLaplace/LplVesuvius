"""L'ajustement de toutes les boucles garde-t-il la spire : le treillis, la moitié, le quart.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LE TREILLIS : chaque demi-côté porte sa somme
mesurée et l'erreur avec laquelle l'ajustement des autres le prédit quand il est retiré ; on y voit où
l'incohérence se loge. À droite en haut, LA MOITIÉ : chaque ligne entière retirée, son erreur ajustée
contre ses détours et contre le bruit seul — c'est le panneau qui conclut. À droite en bas, LE QUART.

  uv run python src/figures/figure_lajustement_de_toutes_les_boucles_garde_t_il_la_spire.py \\
      --json docs/mesures/lajustement_de_toutes_les_boucles_garde_t_il_la_spire.json \\
      --sortie docs/images/226_lajustement_de_toutes_les_boucles_garde_t_il_la_spire.png
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

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
MOYEN = (196, 150, 70)
CONTRE = (92, 108, 150)
BRUIT = (222, 220, 214)
L_, H_ = 1360, 1060


def _fr(x, n: int = 3) -> str:
    """Un nombre en français. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def _signe(x) -> str:
    return ("+" if float(x) > 0 else "") + _fr(x, 4)


def lire(chemin: Path) -> dict:
    """Le JSON de `lajustement_de_toutes_les_boucles_garde_t_il_la_spire.py`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("la_validation_croisee", "les_demi_cotes", "le_verdict", "la_reproduction_de_225"):
        if not d.get(cle):
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if v["un_cote_ajuste_depasse"]:
        return "MÊME AJUSTÉES TOUTES ENSEMBLE, LES BOUCLES LAISSENT UN CÔTÉ AU-DELÀ DU DEMI-FEUILLET"
    if v["un_detour_depasse"]:
        return "L'AJUSTEMENT DE TOUTES LES BOUCLES GARDE LA SPIRE LÀ OÙ UN SEUL DÉTOUR LA PERD"
    return "L'AJUSTEMENT DE TOUTES LES BOUCLES GARDE LA SPIRE, COMME UN SEUL DÉTOUR"


def le_nom(cle: str) -> str:
    """`colonnes_71` → « la colonne 71 », `rangees_99_71_142` → « la rangée 99, de 71 à 142 »."""
    p_ = cle.split("_")
    tete = ("la rangée " if p_[0] == "rangees" else "la colonne ") + p_[1]
    return tete if len(p_) == 2 else f"{tete}, de {p_[2]} à {p_[3]}"


def le_cas_qui_se_repand(d: dict):
    """Le demi-côté à une seule boucle que l'ajustement prédit le plus mal par rapport à cette boucle."""
    q = [(n, x) for n, x in d["la_validation_croisee"]["le_quart"].items() if len(x["les_detours_en_voxels"]) == 1]
    if not q:
        return None
    return max(q, key=lambda t: abs(t[1]["lerreur_ajustee_en_voxels"])
               - abs(next(iter(t[1]["les_detours_en_voxels"].values()))))


def _couleur(e: float, demi: float):
    a = abs(float(e))
    return ALERTE if a >= demi else (MOYEN if a >= demi / 2 else BON)


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

    ve, vc, dc = d["le_verdict"], d["la_validation_croisee"], d["les_demi_cotes"]
    demi = float(d["le_demi_pli_en_voxels"])

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, "aucune lecture neuve · les douze demi-côtés de 224, le trou franchi par la règle de 225, "
                   f"rejoués sur ses {d['la_reproduction_de_225']['les_boucles']} fermetures · chaque côté retiré "
                   "puis prédit par l'ajustement pondéré de tous les autres", petit, GRIS)

    # ── PANNEAU 1 · LE TREILLIS ─────────────────────────────────────────────────────────────
    panneau(50, 84, 560, 820, "LE TREILLIS · chaque demi-côté retiré et prédit")
    nx = {0: 120, 1: 275, 2: 420}
    ny = {0: 170, 1: 430, 2: 690}
    R, C = [], []
    for k in dc:
        sens, centre, de, a = k.split("_")
        (R if sens == "rangees" else C).append(int(centre))
    R, C = sorted(set(R)), sorted(set(C))
    quart = vc["le_quart"]
    for k, x in sorted(dc.items()):
        (i0, j0), (i1, j1) = x["de"], x["a"]
        e = quart[k]["lerreur_ajustee_en_voxels"]
        coul = _couleur(e, demi)
        art.line([nx[j0], ny[i0], nx[j1], ny[i1]], fill=coul, width=5)
        points += [(nx[j0], ny[i0]), (nx[j1], ny[i1])]
        mx, my = (nx[j0] + nx[j1]) / 2, (ny[i0] + ny[i1]) / 2
        if i0 == i1:
            ecrire(mx - 44, my - 30, f"mesuré {_signe(x['la_somme_en_voxels'])}", 0, GRIS)
            ecrire(mx - 44, my + 8, f"ajusté {_signe(e)}", 0, coul)
        else:
            ecrire(mx + 8, my - 14, f"mesuré {_signe(x['la_somme_en_voxels'])}", 0, GRIS)
            ecrire(mx + 8, my + 2, f"ajusté {_signe(e)}", 0, coul)
        traces[k] = 1
    for i in range(3):
        for j in range(3):
            art.ellipse([nx[j] - 6, ny[i] - 6, nx[j] + 6, ny[i] + 6], fill=ENCRE)
    for i, r in enumerate(R):
        ecrire(62, ny[i] - 7, f"r. {r}", 0, ENCRE)
    for j, c in enumerate(C):
        ecrire(nx[j] - 18, 136, f"col. {c}", 0, ENCRE)
    ecrire(66, 740, "vert : moins d'un quart de feuillet · ocre : moins d'un demi", 0, GRIS)
    ecrire(66, 758, "rouge : au-delà du demi-feuillet", 0, GRIS)
    ecrire(66, 782, "« ajusté » : l'erreur avec laquelle les autres le prédisent", 0, GRIS)

    # ── PANNEAUX 2 et 3 · LA MOITIE, LE QUART ───────────────────────────────────────────────
    def rangs(x0, y0, x1, y1, titre, cas, pas):
        panneau(x0, y0, x1, y1, titre)
        ax0, ax1 = x0 + 150, x0 + 400
        haut = 75.0

        def ax(v):
            return ax0 + (ax1 - ax0) * min(abs(float(v)), haut) / haut
        yb = y0 + 44 + pas * len(cas)
        for v_, lab, coul in ((demi, f"demi-feuillet {int(demi)}", ALERTE), (2 * demi, f"un feuillet {int(2 * demi)}", GRIS)):
            art.line([ax(v_), y0 + 38, ax(v_), yb], fill=coul, width=1)
            ecrire(ax(v_) - 30, yb + 4, lab, 0, coul)
        ecrire(ax0 - 4, yb + 4, "0", 0, GRIS)
        yy = y0 + 44
        for nom, x in cas.items():
            lab = nom.replace("rangees_", "rangée ").replace("colonnes_", "colonne ")
            if lab.count("_"):
                parts = lab.split("_")
                lab = f"{parts[0]} {parts[1]}–{parts[2]}"
            ecrire(x0 + 14, yy - 6, lab, 0, ENCRE)
            art.line([ax0, yy, ax1, yy], fill=TRAIT, width=1)
            art.rectangle([ax0, yy - 3, ax(x["le_nul"]["lerreur_mediane_en_valeur_absolue"]), yy + 3], fill=BRUIT)
            for v_ in x["les_detours_en_voxels"].values():
                art.ellipse([ax(v_) - 4, yy - 4, ax(v_) + 4, yy + 4], outline=CONTRE)
                points.append((ax(v_) + 4, yy + 4))
            e = x["lerreur_ajustee_en_voxels"]
            coul = BON if x["sous_le_demi_pli"] else ALERTE
            art.ellipse([ax(e) - 5, yy - 5, ax(e) + 5, yy + 5], fill=coul)
            points.append((ax(e) + 5, yy + 5))
            ecrire(ax1 + 12, yy - 6, f"ajusté {_signe(e)}", 0, coul)
            ecrire(ax1 + 110, yy - 6, "détours " + ", ".join(_signe(v_) for v_ in x["les_detours_en_voxels"].values()),
                   0, CONTRE)
            traces[f"{titre[:6]}:{nom}"] = 1
            yy += pas

    rangs(580, 84, 1310, 400, "LA MOITIÉ · chaque ligne entière retirée, |erreur| en voxels", vc["la_moitie"], 34)
    rangs(580, 420, 1310, 820, "LE QUART · chaque demi-côté retiré", vc["le_quart"], 25)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 838, L_, H_], fill=BANDE)
    ecrire(50, 852, f"LE VERDICT : {ve['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    pire = max(((n, x) for e_ in vc.values() for n, x in e_.items()),
               key=lambda t: abs(t[1]["lerreur_ajustee_en_voxels"]))
    ecrire(50, 876, f"⚠ la pire prédiction ajustée : {le_nom(pire[0])}, {pire[1]['les_coutures']} coutures, "
                    f"à {_signe(pire[1]['lerreur_ajustee_en_voxels'])} vx — là où le bruit seul resterait dessous "
                    f"{_fr(pire[1]['le_nul']['la_part_sous_le_demi_pli'], 4)} des tirages.", moyen, ALERTE)
    rp = le_cas_qui_se_repand(d)
    if rp:
        (nb, x_), = [(next(iter(rp[1]["les_detours_en_voxels"])), rp[1])]
        ecrire(50, 902, f"⚠⚠ l'ajustement ne dilue pas l'incohérence, il la répand : {le_nom(rp[0])}, que sa seule "
                        f"boucle prédit à {_signe(x_['les_detours_en_voxels'][nb])} vx,", moyen, ALERTE)
        ecrire(50, 922, f"   l'ajustement de tous les chemins le prédit à {_signe(x_['lerreur_ajustee_en_voxels'])} vx.",
               moyen, ALERTE)
    ecrire(50, 952, "⚠ ce qui n'est PAS établi : lequel des côtés de la boucle en haut à gauche porte l'erreur — "
                    "le treillis ne le dit pas.", moyen, ALERTE)
    ecrire(50, 982, "★ la suite : où est l'erreur que porte la boucle en haut à gauche, et une boucle plus fine "
                    "la désigne-t-elle ?", moyen, ENCRE)

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
    tmp = sortie.parent / ".sonde_226.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(a, b):
        return {"le_verdict": {"un_cote_ajuste_depasse": a, "un_detour_depasse": b}}
    v("★★★★ les trois titres possibles sont distincts, et dépasser après l'ajustement prime",
      len({le_titre(_v(a, b)) for a in (True, False) for b in (True, False)}) == 3
      and le_titre(_v(True, False)) == le_titre(_v(True, True)))
    v("★★★ le titre LIT le verdict",
      ("AU-DELÀ" in le_titre(d)) == d["le_verdict"]["un_cote_ajuste_depasse"])
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile",
      all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    vc = d["la_validation_croisee"]
    v("★★★★ chaque demi-côté du treillis et chaque cas retiré sont tracés",
      all(traces.get(k) for k in d["les_demi_cotes"])
      and sum(1 for k in traces if ":" in k) == len(vc["le_quart"]) + len(vc["la_moitie"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte l'erreur ajustée et les détours de chaque ligne entière",
      all(f"ajusté {_signe(x['lerreur_ajustee_en_voxels'])}" in txt
          and all(_signe(v_) in txt for v_ in x["les_detours_en_voxels"].values())
          for x in vc["la_moitie"].values()))
    v("★★★★ elle porte la somme mesurée de chaque demi-côté",
      all(f"mesuré {_signe(x['la_somme_en_voxels'])}" in txt for x in d["les_demi_cotes"].values()))
    v("★★★★ elle dit ce qui n'est PAS établi", "n'est PAS établi" in txt)
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
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "lajustement_de_toutes_les_boucles_garde_t_il_la_spire.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "226_lajustement_de_toutes_les_boucles_garde_t_il_la_spire.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
