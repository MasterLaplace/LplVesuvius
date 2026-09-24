"""Les ailes tiennent-elles sur leur profil : la couverture sur l'empreinte, et le profil de chaque aile jugée.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LA COUVERTURE : l'empreinte, les chunks qu'entourent les
boucles jugées sur leur profil et qui restent dessous, et l'aile de droite qui franchit en chemin (`235`, `237`). À
droite, UN PANNEAU PAR AILE JUGÉE : ses sous-boucles contre leur bruit seul, et la fermeture cumulée coupe après coupe
contre le demi-feuillet — ce sont les panneaux qui concluent. En bas, le verdict.

  uv run python src/figures/figure_les_ailes_tiennent_elles_sur_leur_profil.py \\
      --json docs/mesures/les_ailes_tiennent_elles_sur_leur_profil.json \\
      --sortie docs/images/240_les_ailes_tiennent_elles_sur_leur_profil.png
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
CE_QUE_234_A_RENDU = MESURES / "le_segment_au_dela_du_rectangle_se_relie_t_il.json"
CE_QUE_235_A_RENDU = MESURES / "ou_laile_de_droite_se_separe.json"

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
L_, H_ = 1360, 1000
LIB = {"haut": "l'aile du haut", "droite": "l'aile de droite", "bas": "l'aile du bas", "gauche": "l'aile de gauche"}
DE = {"haut": "DU HAUT", "droite": "DE DROITE", "bas": "DU BAS", "gauche": "DE GAUCHE"}


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path) -> dict:
    """Le JSON de `les_ailes_tiennent_elles_sur_leur_profil.py`, la présence de `233`, l'aile de droite de `234` et
    son profil dans `235`, et le demi-feuillet de `224`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("le_verdict", "les_decoupages", "le_rectangle_de_239"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["la_presence"] = json.loads(CE_QUE_233_A_RENDU.read_text())["la_presence"]
    d234 = json.loads(CE_QUE_234_A_RENDU.read_text())
    d["les_ailes_de_234"] = d234["les_ailes"]
    d["la_couverture_de_234"] = d234["la_couverture"]["par_le_rectangle_et_les_ailes_qui_ferment"]
    d["le_profil_de_235"] = json.loads(CE_QUE_235_A_RENDU.read_text()).get("le_profil") or []
    d["le_demi_pli"] = float(json.loads(CE_QUE_224_A_RENDU.read_text())["le_demi_pli_en_voxels"])
    return d


def les_noms(cotes) -> str:
    """« LES AILES DU HAUT ET DE GAUCHE »."""
    n = [DE[c] for c in cotes]
    if len(n) == 1:
        return f"L'AILE {n[0]}"
    return "LES AILES " + ", ".join(n[:-1]) + " ET " + n[-1]


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer, dans l'ordre de priorité des issues."""
    v = d["le_verdict"]
    if not v["les_ailes_jugees"]:
        return "AUCUNE AUTRE AILE NE FERME DANS 234 : IL N'Y A RIEN À JUGER"
    if v["les_ailes_ouvertes"]:
        return "À NEUF LIGNES, UN TROU TROP LONG LAISSE UNE SOUS-BOUCLE OUVERTE"
    if v["les_ailes_qui_franchissent"]:
        return f"À NEUF LIGNES, LE PROFIL DE {les_noms(v['les_ailes_qui_franchissent'])} ATTEINT LE DEMI-FEUILLET EN CHEMIN"
    if v["les_ailes_sans_coupe"]:
        return "UNE AILE NE SE DÉCOUPE PAS : SON PROFIL N'EST PAS VU"
    return f"À NEUF LIGNES, {les_noms(v['les_ailes_jugees'])} RESTENT SOUS LE DEMI-FEUILLET SUR TOUT LEUR PROFIL"


def lentoure(forme, coins, h: int):
    gy, gx = forme
    r0, r1, c0, c1 = coins
    return max(0, r0 - h), min(gy, r1 + h + 1), max(0, c0 - h), min(gx, c1 + h + 1)


def les_boucles_qui_tiennent(d: dict) -> list:
    """Le rectangle si `239` le dit dessous, et les ailes jugées qui restent dessous."""
    r = d["le_rectangle_de_239"]
    return ([r["les_coins"]] if r["reste_dessous"] else []) + \
        [d["par_aile"][c]["les_coins"] for c in d["le_verdict"]["les_ailes_qui_restent_dessous"]]


def la_carte(d: dict, s: float) -> tuple[Image.Image, int]:
    """L'empreinte, un pixel par chunk puis agrandie sans lissage : les chunks qu'entoure une boucle qui tient sur son
    profil teintés ; et combien de chunks teintés la carte porte."""
    rangees = d["la_presence"]["les_rangees"]
    gy, gx = [int(x) for x in d["la_presence"]["la_grille"]]
    h = int(d["le_verdict"]["la_largeur_jugee"]) // 2
    M = [[False] * gx for _ in range(gy)]
    for co in les_boucles_qui_tiennent(d):
        a, b, e, f = lentoure((gy, gx), [int(x) for x in co], h)
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
    k1 = str(v["la_largeur_jugee"])
    jugees = v["les_ailes_jugees"]
    par = d.get("par_aile") or {}
    decs = d["les_decoupages"]
    rp = d.get("la_reproduction") or {}
    cov = d.get("la_couverture") or {}

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    n_c = sum(max(0, len(decs[c]["les_coupes"]) - 2) for c in jugees)
    ecrire(50, 54, f"chaque aile coupée par la règle de 235, deux coupes voisines à "
                   f"{max(decs[c]['le_plus_grand_ecart'] for c in jugees)} coutures au plus · les {n_c} coupes retombent "
                   f"sur les bandes publiées en {rp.get('combien_de_coutures_relues', 0)} coutures à l'écart "
                   f"{_fr(rp.get('lecart_le_plus_grand'))}" if jugees else "aucune aile n'est jugée", petit, GRIS)

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

    def le_cadre(co, coul, w=2):  # noqa: E306
        a0, a1, b0, b1 = [int(x) for x in co]
        art.rectangle([X(b0), Y(a0), X(b1 + 1), Y(a1 + 1)], outline=coul, width=w)
        points.append((X(b1 + 1), Y(a1 + 1)))
    le_cadre(d["le_rectangle_de_239"]["les_coins"], BON if d["le_rectangle_de_239"]["reste_dessous"] else ALERTE)
    dr = d["les_ailes_de_234"].get(d.get("laile_de_235") or "", {}).get("les_coins")
    if dr:
        le_cadre(dr, ALERTE)
    for c in jugees:
        co = par.get(c, {}).get("les_coins") or d["les_ailes_de_234"][c]["les_coins"]
        le_cadre(co, BON if par.get(c, {}).get("le_verdict", {}).get("reste_dessous") else ALERTE)
        a0, a1, b0, b1 = [int(x) for x in co]
        for y in decs[c]["les_coupes"][1:-1]:
            if decs[c]["le_sens"] == "rangees":
                art.line([X(b0), Y(y + 0.5), X(b1 + 1), Y(y + 0.5)], fill=GRIS, width=1)
            else:
                art.line([X(y + 0.5), Y(a0), X(y + 0.5), Y(a1 + 1)], fill=GRIS, width=1)
    ly = round(Y(gy)) + 12
    art.rectangle([70, ly + 3, 84, ly + 13], fill=ENTOURE, outline=TRAIT)
    ecrire(92, ly, "un chunk qu'entoure une boucle qui tient sur son profil", 0, GRIS)
    art.rectangle([70, ly + 23, 84, ly + 33], fill=PRESENT, outline=TRAIT)
    ecrire(92, ly + 20, "un chunk que le dépôt porte et qu'aucune n'entoure", 0, GRIS)
    art.rectangle([70, ly + 43, 84, ly + 53], outline=BON, width=2)
    ecrire(92, ly + 40, "une boucle qui reste dessous, ses coupes en gris", 0, BON)
    art.rectangle([70, ly + 63, 84, ly + 73], outline=ALERTE, width=2)
    ecrire(92, ly + 60, "une boucle qui franchit le demi-feuillet en chemin", 0, ALERTE)

    # ── UN PANNEAU PAR AILE JUGÉE ───────────────────────────────────────────────────────────
    n_j = max(1, len(jugees))
    hp = (800 - 84 - 12 * (n_j - 1)) / n_j
    n_sb, n_pr = 0, 0
    for i, c in enumerate(jugees):
        py0 = round(84 + i * (hp + 12))
        py1 = round(py0 + hp)
        dec = decs[c]
        co = [int(x) for x in (par.get(c, {}).get("les_coins") or d["les_ailes_de_234"][c]["les_coins"])]
        lng = "colonnes" if dec["le_sens"] == "colonnes" else "rangées"
        trv = "rangées" if dec["le_sens"] == "colonnes" else "colonnes"
        de_, a_ = dec["les_coupes"][0], dec["les_coupes"][-1]
        b0, b1 = (co[0], co[1]) if dec["le_sens"] == "colonnes" else (co[2], co[3])
        panneau(580, py0, 1310, py1, f"{LIB[c].upper()} · {lng} {de_} à {a_}, {trv} {b0} à {b1}")
        pa = par.get(c) or {}
        sbs = pa.get("par_sous_boucle") or []
        prof = pa.get("le_profil") or []
        VM = max([abs(float(p["le_cumul_en_voxels"])) for p in prof]
                 + [abs(float(sb["par_largeur"][k1]["la_fermeture_en_voxels"])) for sb in sbs
                    if sb["par_largeur"][k1]["fermable"]] + [demi]) + 6.0
        AX0, AX1 = 650, 1280
        YM = (py0 + 58 + py1 - 64) / 2
        YH = (py1 - 64 - py0 - 58) / 2

        def AX(y, de_=de_, a_=a_, AX0=AX0, AX1=AX1):  # noqa: E306
            return AX0 + (AX1 - AX0) * (float(y) - de_) / max(1.0, float(a_ - de_))

        def AY(x, YM=YM, YH=YH, VM=VM):  # noqa: E306
            return YM - YH * float(x) / VM
        for x_ in (-demi, demi):
            art.line([AX0 - 6, AY(x_), AX1 + 6, AY(x_)], fill=ALERTE, width=1)
        art.line([AX0 - 6, AY(0), AX1 + 6, AY(0)], fill=GRIS, width=1)
        ecrire(596, AY(demi) - 7, f"{_fr(demi)}", 0, ALERTE)
        ecrire(596, AY(0) - 7, "0", 0, GRIS)
        ecrire(596, AY(-demi) - 7, f"−{_fr(demi)}", 0, ALERTE)
        for y in dec["les_coupes"]:
            art.line([AX(y), AY(-demi) + 4, AX(y), AY(-demi) + 10], fill=GRIS, width=1)
            ecrire(AX(y) - 9, py1 - 44, f"{y}", 0, GRIS)
        for sb in sbs:
            a, b = sb["entre"]
            x = sb["par_largeur"][k1]
            xm = (AX(a) + AX(b)) / 2
            if x["fermable"]:
                L = float(x["la_fermeture_en_voxels"])
                med = float(x["le_nul"]["la_fermeture_mediane_en_valeur_absolue"])
                art.rectangle([AX(a) + 3, AY(med), AX(b) - 3, AY(-med)], fill=BANDE, outline=TRAIT)
                art.rectangle([xm - 4, min(AY(0), AY(L)), xm + 4, max(AY(0), AY(L))],
                              fill=BON if abs(L) < demi else ALERTE)
                points.append((xm, AY(L)))
                ecrire(xm - 22, py0 + 36, f"{_fr(L)}", 0, ENCRE)
            else:
                art.rectangle([AX(a) + 3, AY(VM), AX(b) - 3, AY(-VM)], outline=ALERTE)
                ecrire(xm - 20, py0 + 36, "ouverte", 0, ALERTE)
            n_sb += 1
        pts = [(AX(de_), AY(0.0))] + [(AX(p["la_coupe"]), AY(p["le_cumul_en_voxels"])) for p in prof]
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):  # en tirets : entre deux coupes, le profil n'est pas vu
            for j in range(0, 20, 2):
                art.line([xa + (xb - xa) * j / 20, ya + (yb - ya) * j / 20,
                          xa + (xb - xa) * (j + 1) / 20, ya + (yb - ya) * (j + 1) / 20], fill=CONTRE, width=2)
        for (x_, y_), p in zip(pts[1:], prof):
            loin = abs(float(p["le_cumul_en_voxels"])) >= demi
            art.ellipse([x_ - 4, y_ - 4, x_ + 4, y_ + 4], fill=ALERTE if loin else CONTRE)
            points.append((x_, y_))
        n_pr += len(pts)
        vv = pa.get("le_verdict") or {}
        if vv.get("le_pic"):
            ecrire(596, py1 - 24, f"points : le cumul depuis la coupe {de_}, qui va au plus à "
                                  f"{_fr(vv['le_pic']['le_cumul_en_voxels'])} à la coupe {vv['le_pic']['la_coupe']} ; "
                                  f"au bout, {_fr(prof[-1]['le_cumul_en_voxels'])}", 0, ENCRE)
        elif vv.get("sans_coupe"):
            ecrire(596, py1 - 24, "aucune coupe ne tient : le profil n'est pas vu", 0, ALERTE)
    traces["sous_boucles"] = n_sb
    traces["profil"] = n_pr

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    ecrire(50, 856, "barres : la fermeture de chaque sous-boucle, contre ± la médiane de son bruit seul ; traits bruns : "
                    f"le demi-feuillet, à ±{_fr(demi)} voxels ; ⚠ en tirets, entre deux coupes : non vu.", petit, GRIS)
    cv = cov.get("par_les_boucles_qui_restent_dessous_sur_leur_profil") or {}
    if cv:
        ecrire(50, 878, f"★ les boucles qui tiennent sur leur profil entourent {_fr(cv['la_part'])} de l'empreinte, contre "
                        f"{_fr(cov['par_le_rectangle']['la_part'])} pour le rectangle seul ; jugées à leur bout, 234 en "
                        f"comptait {_fr(d['la_couverture_de_234']['la_part'])}.", moyen, ENCRE)
    fr235 = [p for p in d["le_profil_de_235"] if abs(float(p["le_cumul_en_voxels"])) >= demi]
    if fr235:
        ecrire(50, 904, f"★ l'aile de droite, découpée par 235, reste hors du compte : son cumul atteint le demi-feuillet "
                        f"de la coupe {fr235[0]['la_coupe']} à la coupe {fr235[-1]['la_coupe']}.", moyen, ENCRE)
    if jugees:
        ecrire(50, 930, f"⚠ ce qui n'est PAS établi : une traversée plus courte que "
                        f"{max(decs[c]['le_plus_grand_ecart'] for c in jugees)} coutures, entre deux coupes.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_240.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(j, ouv, fr, sc):
        return {"le_verdict": {"les_ailes_jugees": j, "les_ailes_ouvertes": ouv, "les_ailes_qui_franchissent": fr,
                               "les_ailes_sans_coupe": sc}}
    tous = [_v(["haut"] if j else [], ["haut"] if o else [], ["haut"] if f else [], ["haut"] if s_ else [])
            for j in (True, False) for o in (True, False) for f in (True, False) for s_ in (True, False)]
    v("★★★★ les cinq titres possibles sont distincts, et l'ordre des issues prime",
      len({le_titre(x) for x in tous}) == 5
      and le_titre(_v(["haut"], ["haut"], ["haut"], [])) == le_titre(_v(["haut"], ["haut"], [], []))
      and le_titre(_v(["haut"], [], ["haut"], ["haut"])) == le_titre(_v(["haut"], [], ["haut"], [])))
    v("★★★ le titre nomme les ailes : une, ou plusieurs",
      les_noms(["gauche"]) == "L'AILE DE GAUCHE" and les_noms(["haut", "gauche"]) == "LES AILES DU HAUT ET DE GAUCHE")
    v("★★★ le titre LIT le verdict",
      ("ATTEINT" in le_titre(d)) == bool(d["le_verdict"]["les_ailes_qui_franchissent"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    par = d.get("par_aile") or {}
    jug = d["le_verdict"]["les_ailes_jugees"]
    v("★★★★ chaque sous-boucle a sa case, et chaque profil un point par coupe",
      traces.get("sous_boucles") == sum(len(par[c].get("par_sous_boucle") or []) for c in jug)
      and traces.get("profil") == sum(len(par[c].get("le_profil") or []) + 1 for c in jug))
    v("★★★★ la carte teinte exactement les chunks que la couverture publiée compte",
      traces.get("carte") == d["la_couverture"]["par_les_boucles_qui_restent_dessous_sur_leur_profil"]["combien"])
    txt = " ".join(t for _, _, t, _ in poses)
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    v("★★★★ elle porte la fermeture de chaque sous-boucle, le pic et le bout de chaque profil, la couverture, et ce qui "
      "n'est PAS établi",
      all(_fr(sb["par_largeur"][k1]["la_fermeture_en_voxels"]) in txt for c in jug
          for sb in par[c].get("par_sous_boucle") or [] if sb["par_largeur"][k1]["fermable"])
      and all(_fr(par[c]["le_verdict"]["le_pic"]["le_cumul_en_voxels"]) in txt
              and _fr(par[c]["le_profil"][-1]["le_cumul_en_voxels"]) in txt
              for c in jug if par[c]["le_verdict"].get("le_pic"))
      and _fr(d["la_couverture"]["par_les_boucles_qui_restent_dessous_sur_leur_profil"]["la_part"]) in txt
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
    p.add_argument("--json", type=Path, default=MESURES / "les_ailes_tiennent_elles_sur_leur_profil.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "240_les_ailes_tiennent_elles_sur_leur_profil.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
