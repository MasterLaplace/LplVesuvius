"""Le segment au-delà du rectangle : les ailes dérivées de l'empreinte, leur fermeture, et la part qu'elles entourent.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LES AILES SUR L'EMPREINTE : le rectangle de `233`
et, de chaque côté, l'aile dérivée de la présence, ses bandes colorées par ce que la lecture en dit. En haut à
droite, LA FERMETURE DE CHAQUE AILE, largeur par largeur, contre le demi-feuillet — c'est le panneau qui
conclut. En bas à droite, LA PART DE L'EMPREINTE ENTOURÉE, par le rectangle seul puis avec les ailes.

  uv run python src/figures/figure_le_segment_au_dela_du_rectangle_se_relie_t_il.py \\
      --json docs/mesures/le_segment_au_dela_du_rectangle_se_relie_t_il.json \\
      --sortie docs/images/234_le_segment_au_dela_du_rectangle_se_relie_t_il.png
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
CE_QUE_233_A_RENDU = RACINE / "docs" / "mesures" / "ou_sarrete_le_segment.json"
CE_QUE_224_A_RENDU = RACINE / "docs" / "mesures" / "deux_chemins_arrivent_ils_sur_la_meme_spire.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
FRANCHI = (214, 170, 80)
PRESENT = (218, 215, 206)
ENTOURE = (196, 214, 204)
L_, H_ = 1360, 1000
LES_COTES = ("haut", "droite", "bas", "gauche")
LIB = {"haut": "l'aile du haut", "droite": "l'aile de droite", "bas": "l'aile du bas", "gauche": "l'aile de gauche"}


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une
    virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path) -> dict:
    """Le JSON de `le_segment_au_dela_du_rectangle_se_relie_t_il.py`, la présence de `233` et le demi-feuillet."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("les_ailes", "le_verdict", "la_couverture_declaree", "le_rectangle_de_233", "lempreinte"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["la_presence"] = json.loads(CE_QUE_233_A_RENDU.read_text())["la_presence"]
    d["le_demi_pli"] = float(json.loads(CE_QUE_224_A_RENDU.read_text())["le_demi_pli_en_voxels"])
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer, dans l'ordre de priorité des issues."""
    v = d["le_verdict"]
    if not v["les_ailes_qui_tiennent"]:
        return "AUCUNE AILE NE TIENT AUTOUR DU PLUS GRAND RECTANGLE"
    if v["les_ailes_ouvertes"]:
        return "À NEUF LIGNES, UN TROU TROP LONG LAISSE UNE AILE OUVERTE"
    if v["les_ailes_a_un_demi_feuillet"]:
        return "À NEUF LIGNES, UNE AILE ARRIVE À UN DEMI-FEUILLET DU PLUS GRAND RECTANGLE"
    return "À NEUF LIGNES, CHAQUE AILE ARRIVE SUR LA MÊME SPIRE QUE LE PLUS GRAND RECTANGLE"


def lissue(d: dict, cote: str) -> str:
    """L'issue d'une aile, lue dans le verdict."""
    v = d["le_verdict"]
    for cle, lib in (("les_ailes_ouvertes", "ouverte"), ("les_ailes_a_un_demi_feuillet", "à un demi-feuillet"),
                     ("les_ailes_qui_ferment", "ferme")):
        if cote in v[cle]:
            return lib
    return "aucune aile"


def lentoure(forme, coins, h: int):
    gy, gx = forme
    r0, r1, c0, c1 = coins
    return max(0, r0 - h), min(gy, r1 + h + 1), max(0, c0 - h), min(gx, c1 + h + 1)


def la_carte(d: dict, s: float) -> tuple[Image.Image, int]:
    """L'empreinte, un pixel par chunk puis agrandie sans lissage : les chunks entourés par une boucle qui ferme
    teintés ; et combien de chunks présents la carte porte."""
    rangees = d["la_presence"]["les_rangees"]
    gy, gx = [int(x) for x in d["la_presence"]["la_grille"]]
    h = int(d["le_verdict"]["la_largeur_jugee"]) // 2
    boucles = [d["le_rectangle_de_233"]["les_coins"]] + [d["les_ailes"][c]["les_coins"]
                                                          for c in d["le_verdict"]["les_ailes_qui_ferment"]]
    M = [[False] * gx for _ in range(gy)]
    for co in boucles:
        a, b, e, f = lentoure((gy, gx), co, h)
        for r in range(a, b):
            for c in range(e, f):
                M[r][c] = True
    img = Image.new("RGB", (gx, gy), FOND)
    img.putdata([(ENTOURE if M[r][c] else PRESENT) if ch == "1" else FOND
                 for r, ligne in enumerate(rangees) for c, ch in enumerate(ligne)])
    n = sum(ligne.count("1") for ligne in rangees)
    return img.resize((round(gx * s), round(gy * s)), Image.NEAREST), n


def la_plus_lache(d: dict):
    """L'aile qui ferme avec la plus grande fermeture, à la largeur jugée : (côté, fermeture, part du bruit plus serré)."""
    k = str(d["le_verdict"].get("la_largeur_jugee"))
    pire = None
    for cote in d["le_verdict"].get("les_ailes_qui_ferment", []):
        x = (d.get("par_aile") or {}).get(cote, {}).get("par_largeur", {}).get(k)
        if x and x["fermable"] and (pire is None or abs(x["la_fermeture_en_voxels"]) > abs(pire[1])):
            pire = (cote, x["la_fermeture_en_voxels"], x["le_nul"]["la_part_sous_la_fermeture"])
    return pire


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

    gy, gx = [int(x) for x in d["la_presence"]["la_grille"]]
    r0, r1, c0, c1 = [int(x) for x in d["le_rectangle_de_233"]["les_coins"]]
    demi = d["le_demi_pli"]
    plus_long = d.get("le_plus_long_trou_franchi_par_225")
    par = d.get("par_aile") or {}
    rp = d.get("la_reproduction") or {}

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"les ailes sont dérivées de la présence que 233 publie, rien d'autre · leurs bandes neuves, lues pour "
                   f"cette tranche, retombent sur les bandes publiées en {rp.get('combien_de_coutures_relues', 0)} coutures "
                   f"à l'écart {_fr(rp.get('lecart_le_plus_grand'))}", petit, GRIS)

    # ── PANNEAU 1 · LES AILES SUR L'EMPREINTE ───────────────────────────────────────────────
    panneau(50, 84, 560, 800, "LES AILES SUR L'EMPREINTE · le rectangle de 233 et ce qui l'entoure")
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

    def une_bande(sens, centre, de, a, coul):  # noqa: E306
        if sens == "r":
            art.rectangle([X(de), Y(centre - 4), X(a + 1), Y(centre + 5)], fill=coul)
            points.append((X(a + 1), Y(centre + 5)))
        else:
            art.rectangle([X(centre - 4), Y(de), X(centre + 5), Y(a + 1)], fill=coul)
            points.append((X(centre + 5), Y(a + 1)))
    for sens, centre, de, a in (("r", r0, c0, c1), ("r", r1, c0, c1), ("c", c0, r0, r1), ("c", c1, r0, r1)):
        une_bande(sens, centre, de, a, GRIS)
    for cote in LES_COTES:
        co = d["les_ailes"][cote]["les_coins"]
        if not co:
            continue
        issue = lissue(d, cote)
        coul = {"ferme": BON, "ouverte": ALERTE, "à un demi-feuillet": ALERTE}.get(issue, CONTRE)
        a0, a1, b0, b1 = [int(x) for x in co]
        for sens, centre, de, a in (("r", a0, b0, b1), ("r", a1, b0, b1), ("c", b0, a0, a1), ("c", b1, a0, a1)):
            une_bande(sens, centre, de, a, coul)
        traces[f"aile:{cote}"] = 1
    ly = round(Y(gy)) + 12
    art.rectangle([70, ly + 3, 84, ly + 13], fill=ENTOURE, outline=TRAIT)
    ecrire(92, ly, "un chunk entouré par une boucle qui ferme, bandes comprises", 0, GRIS)
    art.rectangle([70, ly + 23, 84, ly + 33], fill=PRESENT, outline=TRAIT)
    ecrire(92, ly + 20, "un chunk que le dépôt porte, qu'aucune boucle qui ferme n'entoure", 0, GRIS)
    art.rectangle([70, ly + 43, 84, ly + 53], fill=GRIS)
    ecrire(92, ly + 40, "les bandes du rectangle de 233", 0, GRIS)
    art.rectangle([70, ly + 63, 84, ly + 73], fill=BON)
    ecrire(92, ly + 60, "les bandes d'une aile qui ferme ; en brun, d'une aile qui ne ferme pas", 0, BON)

    # ── PANNEAU 2 · LA FERMETURE DE CHAQUE AILE ─────────────────────────────────────────────
    panneau(580, 84, 1310, 520, "LA FERMETURE DE CHAQUE AILE · largeur par largeur, contre le demi-feuillet")
    BX0, BW, VMAX = 700, 260, 70.0

    def BX(v):
        return BX0 + BW * min(abs(float(v)), VMAX) / VMAX
    yy = 130
    tenues = [c for c in LES_COTES if d["les_ailes"][c]["les_coins"]]
    y_haut = yy
    for cote in LES_COTES:
        co = d["les_ailes"][cote]["les_coins"]
        if not co:
            ecrire(596, yy, f"{LIB[cote]} · aucune aile ne tient", 0, GRIS)
            traces[f"largeurs:{cote}"] = 0
            yy += 26
            continue
        a0, a1, b0, b1 = co
        ecrire(596, yy, f"{LIB[cote]} · rangées {a0} à {a1}, colonnes {b0} à {b1} · {lissue(d, cote)}", 0, ENCRE)
        yy += 20
        y_barres = yy
        n_ = 0
        for k, x in sorted((par.get(cote) or {}).get("par_largeur", {}).items(), key=lambda t: int(t[0])):
            ecrire(612, yy, f"{k} lignes", 0, ENCRE)
            if not x["fermable"]:
                art.rectangle([BX0, yy + 3, BX0 + BW, yy + 12], fill=ALERTE)
                ecrire(BX0 + BW + 12, yy, f"ouverte : un trou de plus de {plus_long} coutures", 0, ALERTE)
            else:
                L = x["la_fermeture_en_voxels"]
                art.rectangle([BX0, yy + 3, BX(L), yy + 12], fill=BON if abs(L) < demi else ALERTE)
                med = x["le_nul"]["la_fermeture_mediane_en_valeur_absolue"]
                art.line([BX(med), yy + 1, BX(med), yy + 14], fill=ENCRE, width=2)
                points.append((BX(L), yy + 12))
                ecrire(BX0 + BW + 12, yy, f"{_fr(L)} · {_fr(x['le_nul']['la_part_sous_le_demi_pli'])} · "
                                          f"{_fr(x['le_nul']['la_part_sous_la_fermeture'])}", 0, ENCRE)
            n_ += 1
            yy += 18
        traces[f"largeurs:{cote}"] = n_
        art.line([BX(demi), y_barres, BX(demi), yy - 2], fill=ALERTE, width=1)  # jamais à travers un titre
        yy += 10
    ecrire(BX(demi) - 60, yy - 4, f"demi-feuillet · {_fr(demi)}", 0, ALERTE)
    ecrire(596, 478, "barre : la fermeture, en voxels · trait : médiane du bruit seul", 0, GRIS)
    ecrire(596, 496, "chiffres : la fermeture · la part du bruit seul sous le demi-feuillet · celle qui ferme plus serré",
           0, GRIS)

    # ── PANNEAU 3 · LA PART DE L'EMPREINTE ENTOURÉE ─────────────────────────────────────────
    panneau(580, 540, 1310, 800, "LA PART DE L'EMPREINTE ENTOURÉE · bandes comprises")
    cd = d["la_couverture_declaree"]
    cf = (d.get("la_couverture") or {}).get("par_le_rectangle_et_les_ailes_qui_ferment")
    lignes = [("le rectangle de 233 seul", cd["par_le_rectangle"], GRIS),
              ("avec toutes les ailes, déclarée avant la lecture", cd["par_le_rectangle_et_toutes_les_ailes"], CONTRE)]
    if cf is not None:
        lignes.append(("avec les ailes qui ferment", cf, BON))
    yy = 590
    for lib, x, coul in lignes:
        ecrire(596, yy, f"{lib} · {x['combien']} chunks sur {x['sur']}, soit {_fr(x['la_part'])}", 0, ENCRE)
        art.rectangle([596, yy + 20, 596 + 600, yy + 34], outline=TRAIT)
        art.rectangle([596, yy + 20, 596 + 600 * float(x["la_part"]), yy + 34], fill=coul)
        points.append((596 + 600 * float(x["la_part"]), yy + 34))
        traces[f"couverture:{lib}"] = 1
        yy += 56
    ecrire(596, 776, "⚠ entouré ne veut pas dire vérifié : une boucle dit que ses deux chemins s'accordent, pas son intérieur",
           0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    v = d["le_verdict"]
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    ecrire(50, 856, "★ " + " · ".join(f"{LIB[c]} : {lissue(d, c)}" for c in LES_COTES), moyen, ENCRE)
    if cf is not None:
        ecrire(50, 882, f"★ les boucles qui ferment entourent {_fr(cf['la_part'])} de l'empreinte, contre "
                        f"{_fr(cd['par_le_rectangle']['la_part'])} pour le rectangle seul.", moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : ce qui reste au-delà des bandes extérieures et dans les coins, ni "
                    "ce que porte l'intérieur d'une boucle.", moyen, ALERTE)
    lache = la_plus_lache(d)
    if lache is not None:
        cote, L, serre = lache
        ecrire(50, 934, f"⚠ la plus lâche, {LIB[cote]}, ferme à {_fr(L)}, à {_fr(demi - abs(L))} du demi-feuillet ; "
                        f"le bruit seul ferme plus serré dans {_fr(serre)} des tirages.", moyen, ALERTE)
        traces["la_plus_lache"] = 1

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
    tmp = sortie.parent / ".sonde_234.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(tenues, ouv, loin):
        return {"le_verdict": {"les_ailes_qui_tiennent": tenues, "les_ailes_ouvertes": ouv,
                               "les_ailes_a_un_demi_feuillet": loin}}
    tous = [_v(t, o, l_) for t in ([], ["haut"]) for o in ([], ["haut"]) for l_ in ([], ["haut"])]
    v("★★★★ les quatre titres possibles sont distincts, et l'ordre des issues prime",
      len({le_titre(x) for x in tous}) == 4 and le_titre(_v([], ["haut"], ["haut"])) == le_titre(_v([], [], []))
      and le_titre(_v(["haut"], ["haut"], ["haut"])) == le_titre(_v(["haut"], ["haut"], [])))
    v("★★★ le titre LIT le verdict", ("MÊME SPIRE" in le_titre(d)) == bool(d["le_verdict"]["chaque_aile_se_ferme"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ la carte porte exactement les chunks de l'empreinte publiée",
      traces.get("carte") == int(d["lempreinte"]["combien"]))
    tenues = [c for c in LES_COTES if d["les_ailes"][c]["les_coins"]]
    v("★★★★ chaque aile qui tient est tracée, et a ses quatre largeurs",
      all(traces.get(f"aile:{c}") == 1 and traces.get(f"largeurs:{c}") == 4 for c in tenues)
      and all(traces.get(f"largeurs:{c}") == 0 for c in LES_COTES if c not in tenues))
    v("★★★★ chaque couverture a sa barre", sum(1 for k in traces if k.startswith("couverture:"))
      == 2 + (1 if d.get("la_couverture") else 0))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte la fermeture de chaque aile et largeur, la couverture, et ce qui n'est PAS établi",
      all(_fr(x["la_fermeture_en_voxels"]) in txt for c in tenues
          for x in (d.get("par_aile") or {}).get(c, {}).get("par_largeur", {}).values() if x["fermable"])
      and _fr(d["la_couverture_declaree"]["par_le_rectangle"]["la_part"]) in txt and "n'est PAS établi" in txt)
    lache = la_plus_lache(d)
    v("★★★★ la plus lâche des ailes qui ferment est nommée, avec la part du bruit seul qui ferme plus serré",
      lache is None or (traces.get("la_plus_lache") == 1 and _fr(lache[2]) in txt and _fr(lache[1]) in txt))
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
                   default=RACINE / "docs" / "mesures" / "le_segment_au_dela_du_rectangle_se_relie_t_il.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "234_le_segment_au_dela_du_rectangle_se_relie_t_il.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
