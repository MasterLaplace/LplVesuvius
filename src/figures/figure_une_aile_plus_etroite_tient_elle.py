"""Une aile plus étroite, sous l'aile qui évite la colonne qui dérive : sur l'empreinte, ses tranches, son profil.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LA COUVERTURE : l'empreinte, les chunks qu'entourent les
boucles qui tiennent sur leur profil, chacune à sa largeur, l'aile de `241` et l'aile étroite. À droite, en haut, LES
TRANCHES de l'aile étroite contre leur bruit seul ; en bas, LE PROFIL : son cumul coupe après coupe contre le
demi-feuillet, avec les rangées où la colonne évitée le franchit selon `235` — c'est le panneau qui conclut.

  uv run python src/figures/figure_une_aile_plus_etroite_tient_elle.py \\
      --json docs/mesures/une_aile_plus_etroite_tient_elle.json \\
      --sortie docs/images/243_une_aile_plus_etroite_tient_elle.png
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
CE_QUE_224_A_RENDU = MESURES / "deux_chemins_arrivent_ils_sur_la_meme_spire.json"
CE_QUE_233_A_RENDU = MESURES / "ou_sarrete_le_segment.json"
CE_QUE_235_A_RENDU = MESURES / "ou_laile_de_droite_se_separe.json"
CE_QUE_241_A_RENDU = MESURES / "au_dela_de_la_colonne_qui_derive.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
PRESENT = (218, 215, 206)
ENTOURE = (196, 214, 204)
TEINTE = (240, 222, 208)
L_, H_ = 1360, 1000
LES_MOTS = {1: "une", 3: "trois", 5: "cinq", 7: "sept", 9: "neuf"}


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path) -> dict:
    """Le JSON de `une_aile_plus_etroite_tient_elle.py`, la présence de `233`, l'aile de `241`, les franchissements de
    `235` et le demi-feuillet de `224`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("le_verdict", "les_essais", "les_boucles_de_241", "la_couverture_de_242", "les_rangees_cherchees"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["la_presence"] = json.loads(CE_QUE_233_A_RENDU.read_text())["la_presence"]
    d["laile_de_241"] = json.loads(CE_QUE_241_A_RENDU.read_text())["laile"]["les_coins"]
    d["le_demi_pli"] = float(json.loads(CE_QUE_224_A_RENDU.read_text())["le_demi_pli_en_voxels"])
    p235 = json.loads(CE_QUE_235_A_RENDU.read_text()).get("le_profil") or []
    fr = [int(p["la_coupe"]) for p in p235 if abs(float(p["le_cumul_en_voxels"])) >= d["le_demi_pli"]]
    d["la_traversee_de_235"] = [fr[0], fr[-1]] if fr else None
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer, dans l'ordre de priorité des issues."""
    v = d["le_verdict"]
    ligne, rangee, k = v["la_ligne_evitee"], v["sous_la_rangee"], v.get("la_largeur_jugee")
    mot = LES_MOTS.get(k, str(k)).upper() if k else ""
    if not (d.get("laile") or {}).get("les_coins"):
        return f"SOUS LA RANGÉE {rangee}, AUCUNE AILE PLUS ÉTROITE N'ÉVITE LA COLONNE {ligne}"
    if v.get("ouverte"):
        return f"À {mot} LIGNES, UN TROU TROP LONG LAISSE L'AILE OU UNE TRANCHE OUVERTE"
    if v.get("franchit"):
        return f"À {mot} LIGNES, L'AILE ÉTROITE QUI ÉVITE LA COLONNE {ligne} ATTEINT LE DEMI-FEUILLET"
    if v.get("non_vu"):
        return "UN ÉCART ENTRE DEUX COUPES DÉPASSE LA PORTÉE : LE PROFIL N'Y EST PAS VU"
    return f"À {mot} LIGNES, L'AILE ÉTROITE QUI ÉVITE LA COLONNE {ligne} RESTE SOUS LE DEMI-FEUILLET"


def lentoure(forme, coins, h: int):
    gy, gx = forme
    r0, r1, c0, c1 = coins
    return max(0, r0 - h), min(gy, r1 + h + 1), max(0, c0 - h), min(gx, c1 + h + 1)


def les_boucles_qui_tiennent(d: dict) -> list:
    """Chacune à sa largeur : celles que la mesure publie, ou à défaut celles de `241`, à la largeur de la ligne."""
    if d.get("les_boucles_qui_tiennent") is not None:
        return [([int(x) for x in b["les_coins"]], int(b["la_largeur"])) for b in d["les_boucles_qui_tiennent"]]
    return [([int(x) for x in co], int(d["la_largeur_de_la_ligne"])) for co in d["les_boucles_de_241"]]


def la_carte(d: dict, s: float) -> tuple[Image.Image, int]:
    """L'empreinte, un pixel par chunk puis agrandie sans lissage : les chunks qu'entoure une boucle qui tient sur son
    profil teintés ; et combien de chunks teintés la carte porte."""
    rangees = d["la_presence"]["les_rangees"]
    gy, gx = [int(x) for x in d["la_presence"]["la_grille"]]
    M = [[False] * gx for _ in range(gy)]
    for co, k in les_boucles_qui_tiennent(d):
        a, b, e, f = lentoure((gy, gx), co, k // 2)
        for r in range(a, b):
            for c in range(e, f):
                M[r][c] = True
    img = Image.new("RGB", (gx, gy), FOND)
    img.putdata([(ENTOURE if M[r][c] else PRESENT) if ch == "1" else FOND
                 for r, ligne in enumerate(rangees) for c, ch in enumerate(ligne)])
    n = sum(1 for r, ligne in enumerate(rangees) for c, ch in enumerate(ligne) if ch == "1" and M[r][c])
    return img.resize((round(gx * s), round(gy * s)), Image.NEAREST), n


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
    ligne, rangee = v["la_ligne_evitee"], v["sous_la_rangee"]
    k = d.get("la_largeur")
    mot = LES_MOTS.get(k, str(k)) if k else "—"
    co = (d.get("laile") or {}).get("les_coins")
    rp = d.get("la_reproduction") or {}
    pt = d.get("par_tranche") or []
    prof = d.get("le_profil") or []
    a241 = [int(x) for x in d["laile_de_241"]]

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    if co:
        ecrire(50, 54, f"la plus grande aile à {mot} lignes sous la rangée {rangee}, dont la colonne extérieure évite les "
                       f"{d['la_largeur_de_la_ligne']} lignes de la {ligne} : rangées {co[0]} à {co[1]}, colonnes {co[2]} "
                       f"à {co[3]} · ses {len(d.get('les_bandes_declarees') or [])} bandes retombent en "
                       f"{rp.get('combien_de_coutures_relues', 0)} coutures à l'écart "
                       f"{_fr(rp.get('lecart_le_plus_grand'))}", petit, GRIS)

    # ── PANNEAU 1 · LA COUVERTURE ───────────────────────────────────────────────────────────
    panneau(50, 84, 560, 800, "LA COUVERTURE · ce qui tient sur son profil")
    gy, gx = [int(x) for x in d["la_presence"]["la_grille"]]
    s = 1.42
    X0, Y0 = 90, 130

    def X(c):
        return X0 + s * float(c)

    def Y(r):
        return Y0 + s * float(r)
    carte, n_carte = la_carte(d, s)
    img.paste(carte, (X0, Y0))
    art.rectangle([X(0), Y(0), X(gx), Y(gy)], outline=TRAIT)
    traces["carte"] = n_carte

    def le_cadre(c_, coul, w=2):  # noqa: E306
        a0, a1, b0, b1 = [int(x) for x in c_]
        art.rectangle([X(b0), Y(a0), X(b1 + 1), Y(a1 + 1)], outline=coul, width=w)
        points.append((X(b1 + 1), Y(a1 + 1)))
    for c_ in d["les_boucles_de_241"]:
        le_cadre(c_, BON, 1)
    le_cadre(a241, BON)
    # la colonne évitée, sous la rangée où l'aile de 241 s'arrête
    art.line([X(ligne + 0.5), Y(rangee), X(ligne + 0.5), Y(d["les_rangees_cherchees"][1])], fill=ALERTE, width=2)
    if co:
        le_cadre(co, BON if v.get("reste_dessous") else ALERTE)
        for y in (d.get("le_decoupage") or {}).get("les_coupes", [])[1:-1]:
            art.line([X(co[2]), Y(y + 0.5), X(co[3] + 1), Y(y + 0.5)], fill=GRIS, width=1)
    ly = round(Y(gy)) + 12
    art.rectangle([70, ly + 3, 84, ly + 13], fill=ENTOURE, outline=TRAIT)
    ecrire(92, ly, "un chunk qu'entoure une boucle qui tient sur son profil", 0, GRIS)
    art.rectangle([70, ly + 23, 84, ly + 33], fill=PRESENT, outline=TRAIT)
    ecrire(92, ly + 20, "un chunk que le dépôt porte et qu'aucune n'entoure", 0, GRIS)
    art.rectangle([70, ly + 43, 84, ly + 53], outline=BON if v.get("reste_dessous") else ALERTE, width=2)
    ecrire(92, ly + 40, f"l'aile étroite, à {mot} lignes, ses coupes en gris", 0,
           BON if v.get("reste_dessous") else ALERTE)
    art.line([70, ly + 68, 84, ly + 68], fill=ALERTE, width=2)
    ecrire(92, ly + 60, f"la colonne {ligne}, sous la rangée {rangee}", 0, ALERTE)

    # ── PANNEAU 2 · LES TRANCHES ────────────────────────────────────────────────────────────
    panneau(580, 84, 1310, 420, f"LES TRANCHES · chacune contre son bruit seul, à {mot} lignes")
    n_t = 0
    kk = str(k)
    if co and pt:
        a_lo, a_hi = co[0], co[1]
        AX0, AX1 = 650, 1280

        def AX(r):
            return AX0 + (AX1 - AX0) * (float(r) - a_lo) / max(1.0, float(a_hi - a_lo))
        VM = max([abs(float(sb["par_largeur"][kk]["la_fermeture_en_voxels"])) for sb in pt
                  if sb["par_largeur"][kk]["fermable"]]
                 + [float(sb["par_largeur"][kk]["le_nul"]["la_fermeture_mediane_en_valeur_absolue"]) for sb in pt
                    if sb["par_largeur"][kk]["fermable"]] + [demi]) + 6.0
        YM, YH = 252, 110

        def AY(x):
            return YM - YH * float(x) / VM
        for x_ in (-demi, demi):
            art.line([AX0 - 6, AY(x_), AX1 + 6, AY(x_)], fill=ALERTE, width=1)
        art.line([AX0 - 6, AY(0), AX1 + 6, AY(0)], fill=GRIS, width=1)
        ecrire(596, AY(demi) - 7, f"{_fr(demi)}", 0, ALERTE)
        ecrire(596, AY(0) - 7, "0", 0, GRIS)
        ecrire(596, AY(-demi) - 7, f"−{_fr(demi)}", 0, ALERTE)
        for sb in pt:
            a, b = sb["entre"]
            x = sb["par_largeur"][kk]
            xm = (AX(a) + AX(b)) / 2
            if x["fermable"]:
                L = float(x["la_fermeture_en_voxels"])
                med = float(x["le_nul"]["la_fermeture_mediane_en_valeur_absolue"])
                art.rectangle([AX(a) + 3, AY(med), AX(b) - 3, AY(-med)], fill=BANDE, outline=TRAIT)
                art.rectangle([xm - 5, min(AY(0), AY(L)), xm + 5, max(AY(0), AY(L))],
                              fill=BON if abs(L) < demi else ALERTE)
                points.append((xm, AY(L)))
                ecrire(xm - 22, 118, f"{_fr(L)}", 0, ENCRE)
            else:
                art.rectangle([AX(a) + 3, AY(VM), AX(b) - 3, AY(-VM)], outline=ALERTE)
                ecrire(xm - 20, 118, "ouverte", 0, ALERTE)
            ecrire(AX(a) - 9, 380, f"{a}", 0, GRIS)
            n_t += 1
        ecrire(AX(a_hi) - 9, 380, f"{a_hi}", 0, GRIS)
        ecrire(596, 398, "gris clair : la médiane de la fermeture du bruit seul, de part et d'autre de zéro", 0, GRIS)
    traces["tranches"] = n_t

    # ── PANNEAU 3 · LE PROFIL ───────────────────────────────────────────────────────────────
    panneau(580, 436, 1310, 800, f"LE PROFIL · le cumul depuis la rangée {co[0] if co else rangee}, à {mot} lignes")
    n_p = 0
    tr = d.get("la_traversee_de_235")
    if co and prof:
        a_lo, a_hi = co[0], co[1]
        AX0, AX1 = 650, 1280

        def AX(r):  # noqa: F811
            return AX0 + (AX1 - AX0) * (float(r) - a_lo) / max(1.0, float(a_hi - a_lo))
        VM = max([abs(float(p["le_cumul_en_voxels"])) for p in prof] + [demi]) + 6.0
        YM, YH = 616, 120

        def AY(x):  # noqa: F811
            return YM - YH * float(x) / VM
        if tr:
            art.rectangle([max(AX0, AX(tr[0])), AY(VM), min(AX1, AX(tr[1])), AY(-VM)], fill=TEINTE)
            ecrire(max(AX0, AX(tr[0])) + 4, AY(VM) - 16,
                   f"235 : la colonne {ligne} au demi-feuillet, coupes {tr[0]} à {tr[1]}", 0, ALERTE)
        for x_ in (-demi, demi):
            art.line([AX0 - 6, AY(x_), AX1 + 6, AY(x_)], fill=ALERTE, width=1)
        art.line([AX0 - 6, AY(0), AX1 + 6, AY(0)], fill=GRIS, width=1)
        ecrire(596, AY(demi) - 7, f"{_fr(demi)}", 0, ALERTE)
        ecrire(596, AY(0) - 7, "0", 0, GRIS)
        ecrire(596, AY(-demi) - 7, f"−{_fr(demi)}", 0, ALERTE)
        pts = [(AX(a_lo), AY(0.0))] + [(AX(p["la_coupe"]), AY(p["le_cumul_en_voxels"])) for p in prof]
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):  # en tirets : entre deux coupes, rien n'est vu
            for j in range(0, 20, 2):
                art.line([xa + (xb - xa) * j / 20, ya + (yb - ya) * j / 20,
                          xa + (xb - xa) * (j + 1) / 20, ya + (yb - ya) * (j + 1) / 20], fill=CONTRE, width=2)
        for x_, y_ in pts[1:]:
            art.ellipse([x_ - 5, y_ - 5, x_ + 5, y_ + 5], fill=CONTRE)
            points.append((x_, y_))
        n_p = len(pts)
        for y in [a_lo] + [p["la_coupe"] for p in prof]:
            ecrire(AX(y) - 9, 752, f"{y}", 0, CONTRE)
        ecrire(596, 772, f"points bleus : l'aile étroite, par la colonne {co[3]} ; en tirets, entre deux coupes, rien "
                         f"n'est vu", 0, GRIS)
    traces["profil"] = n_p

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    vt = d.get("le_verdict_des_tranches") or {}
    if co and vt.get("le_pic"):
        ecrire(50, 856, f"★ par la colonne {co[3]}, le cumul va au plus à {_fr(vt['le_pic']['le_cumul_en_voxels'])} "
                        f"voxels, à la coupe {vt['le_pic']['la_coupe']} ; au bout, rangée {co[1]}, "
                        f"{_fr(prof[-1]['le_cumul_en_voxels'])}.", moyen, ENCRE)
    cv = d.get("la_couverture") or d["la_couverture_de_242"]
    ecrire(50, 882, f"★ les boucles qui tiennent sur leur profil entourent {_fr(cv['la_part'])} de l'empreinte, "
                    f"contre {_fr(d['la_couverture_de_242']['la_part'])} selon 242.", moyen, ENCRE)
    if co:
        ecrire(50, 908, f"⚠ ce qui n'est PAS établi : ce qui relie la matière entre la colonne {co[3]} et la colonne "
                        f"{ligne}, ni une traversée plus courte que "
                        f"{(d.get('le_decoupage') or {}).get('le_plus_grand_ecart')} rangs.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_243.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(co, o, f, n_):
        return {"laile": {"les_coins": co}, "le_verdict": {"la_ligne_evitee": 260, "sous_la_rangee": 112,
                                                           "la_largeur_jugee": 7, "ouverte": o, "franchit": f,
                                                           "non_vu": n_}}
    tous = [_v([0, 9, 0, 9] if c else None, o, f, n_) for c in (True, False) for o in (True, False)
            for f in (True, False) for n_ in (True, False)]
    v("★★★★ les cinq titres possibles sont distincts, et l'ordre des issues prime",
      len({le_titre(x) for x in tous}) == 5
      and le_titre(_v([0, 9, 0, 9], True, True, False)) == le_titre(_v([0, 9, 0, 9], True, False, False))
      and le_titre(_v([0, 9, 0, 9], False, True, True)) == le_titre(_v([0, 9, 0, 9], False, True, False)))
    v("★★★ le titre LIT le verdict",
      ("ATTEINT" in le_titre(d)) == bool(d["le_verdict"].get("franchit"))
      and ("RESTE SOUS" in le_titre(d)) == bool(d["le_verdict"].get("reste_dessous")))
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
      traces.get("tranches") == len(d.get("par_tranche") or [])
      and traces.get("profil") == (len(d.get("le_profil") or []) + 1 if d.get("le_profil") else 0))
    cv = d.get("la_couverture") or d["la_couverture_de_242"]
    v("★★★★ la carte teinte exactement les chunks que la couverture publiée compte, chaque boucle à sa largeur",
      traces.get("carte") == cv["combien"], f"{traces.get('carte')} contre {cv['combien']}")
    txt = " ".join(t for _, _, t, _ in poses)
    kk = str(d.get("la_largeur"))
    v("★★★★ elle porte la fermeture de chaque tranche, le cumul au bout, la couverture, et ce qui n'est PAS établi",
      all(_fr(sb["par_largeur"][kk]["la_fermeture_en_voxels"]) in txt for sb in d.get("par_tranche") or []
          if sb["par_largeur"][kk]["fermable"])
      and (not d.get("le_profil") or _fr(d["le_profil"][-1]["le_cumul_en_voxels"]) in txt)
      and _fr(cv["la_part"]) in txt
      and (not (d.get("laile") or {}).get("les_coins") or "n'est PAS établi" in txt))
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
    p.add_argument("--json", type=Path, default=MESURES / "une_aile_plus_etroite_tient_elle.json")
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "243_une_aile_plus_etroite_tient_elle.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
