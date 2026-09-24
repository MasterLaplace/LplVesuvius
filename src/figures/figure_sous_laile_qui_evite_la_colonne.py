"""Sous l'aile qui évite la colonne qui dérive : où une colonne de neuf lignes tient, au bord droit de l'empreinte.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LA COUVERTURE : l'empreinte, les chunks qu'entourent les
boucles qui tiennent sur leur profil selon `241`, l'aile de `241`, les rangées où l'aile est cherchée et, s'il y en a
une, l'aile. À droite, LE BORD DROIT : rangée par rangée, les colonnes au-delà de la bande intérieure dont les neuf lignes
ont leurs chunks, séparées en celles qu'une colonne extérieure peut prendre et celles qui partagent une ligne avec la
bande intérieure ou avec la ligne évitée — c'est le panneau qui conclut.

  uv run python src/figures/figure_sous_laile_qui_evite_la_colonne.py \\
      --json docs/mesures/sous_laile_qui_evite_la_colonne.json \\
      --sortie docs/images/242_sous_laile_qui_evite_la_colonne.png
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
CE_QUE_233_A_RENDU = MESURES / "ou_sarrete_le_segment.json"

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
INTERDIT = (232, 206, 188)
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
    """Le JSON de `sous_laile_qui_evite_la_colonne.py`, et la présence de `233`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("le_verdict", "laile", "laile_de_241", "les_rangees_cherchees", "les_boucles_de_241",
                "la_couverture_de_241"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["la_presence"] = json.loads(CE_QUE_233_A_RENDU.read_text())["la_presence"]
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer, dans l'ordre de priorité des issues."""
    v = d["le_verdict"]
    ligne, rangee = v["la_ligne_evitee"], v["sous_la_rangee"]
    if not d["laile"].get("les_coins"):
        return f"SOUS LA RANGÉE {rangee}, AUCUNE AILE NE TIENT SANS PARTAGER DE LIGNE AVEC LA COLONNE {ligne}"
    if v.get("ouverte"):
        return "À NEUF LIGNES, UN TROU TROP LONG LAISSE L'AILE OU UNE TRANCHE OUVERTE"
    if v.get("franchit"):
        return f"SOUS LA RANGÉE {rangee}, L'AILE QUI ÉVITE LA COLONNE {ligne} ATTEINT LE DEMI-FEUILLET"
    if v.get("non_vu"):
        return "UN ÉCART ENTRE DEUX COUPES DÉPASSE LA PORTÉE : LE PROFIL N'Y EST PAS VU"
    return f"SOUS LA RANGÉE {rangee}, L'AILE QUI ÉVITE LA COLONNE {ligne} RESTE SOUS LE DEMI-FEUILLET"


def lentoure(forme, coins, h: int):
    gy, gx = forme
    r0, r1, c0, c1 = coins
    return max(0, r0 - h), min(gy, r1 + h + 1), max(0, c0 - h), min(gx, c1 + h + 1)


def les_boucles_qui_tiennent(d: dict) -> list:
    """Celles de `241`, et l'aile si elle reste dessous."""
    return [list(co) for co in d["les_boucles_de_241"]] + \
        ([d["laile"]["les_coins"]] if d["le_verdict"].get("reste_dessous") else [])


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


def le_bord(d: dict) -> dict:
    """Au-delà de la bande intérieure, pour chaque rangée et chaque colonne centrale, si les neuf lignes de la colonne
    ont leurs chunks à cette rangée et à la suivante ; et quelles colonnes une colonne extérieure peut prendre."""
    rangees = d["la_presence"]["les_rangees"]
    gy, gx = [int(x) for x in d["la_presence"]["la_grille"]]
    k = int(d["le_verdict"]["la_largeur_jugee"])
    h = k // 2
    dedans, ligne = int(d["les_rangees_cherchees"][3]), int(d["la_ligne_evitee"])
    cs = list(range(dedans + 1, gx - h))
    rs = [r for r in range(gy - 1) if any(rangees[r][c] == "1" for c in range(dedans + 1, gx))]
    r0, r1 = (rs[0], rs[-1]) if rs else (0, 0)

    def tient(r, c):  # noqa: E306
        return all(rangees[r][x] == "1" and rangees[r + 1][x] == "1" for x in range(c - h, c + h + 1))
    permise = {c: c >= dedans + k and abs(c - ligne) >= k for c in cs}
    T = {(r, c): tient(r, c) for r in range(r0, r1 + 1) for c in cs}
    return {"les_colonnes": cs, "de": r0, "a": r1, "permise": permise, "tient": T,
            "combien_de_coutures_permises_qui_tiennent": sum(1 for (r, c), t in T.items() if t and permise[c])}


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

    v = d["le_verdict"]
    ligne, rangee = v["la_ligne_evitee"], v["sous_la_rangee"]
    co = d["laile"].get("les_coins")
    a241 = [int(x) for x in d["laile_de_241"]]
    ch = [int(x) for x in d["les_rangees_cherchees"]]
    k = int(v["la_largeur_jugee"])

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"la règle de 234, sur les rangées {ch[0]} à {ch[1]} du rectangle de 233, parmi les colonnes "
                   f"extérieures à {k} colonnes au moins de la {ch[3]} et de la {ligne}", petit, GRIS)

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
    # les rangées où l'aile est cherchée, au-delà de la bande intérieure : en tirets
    xa, xb, ya, yb = X(ch[3] + 1), X(gx), Y(ch[0]), Y(ch[1] + 1)
    for (p, q) in (((xa, ya), (xb, ya)), ((xb, ya), (xb, yb)), ((xb, yb), (xa, yb)), ((xa, yb), (xa, ya))):
        for j in range(0, 40, 2):
            art.line([p[0] + (q[0] - p[0]) * j / 40, p[1] + (q[1] - p[1]) * j / 40,
                      p[0] + (q[0] - p[0]) * (j + 1) / 40, p[1] + (q[1] - p[1]) * (j + 1) / 40], fill=ALERTE, width=2)
    points.append((xb, yb))
    if co:
        le_cadre(co, BON if v.get("reste_dessous") else ALERTE)
    ly = round(Y(gy)) + 12
    art.rectangle([70, ly + 3, 84, ly + 13], fill=ENTOURE, outline=TRAIT)
    ecrire(92, ly, "un chunk qu'entoure une boucle qui tient sur son profil", 0, GRIS)
    art.rectangle([70, ly + 23, 84, ly + 33], fill=PRESENT, outline=TRAIT)
    ecrire(92, ly + 20, "un chunk que le dépôt porte et qu'aucune n'entoure", 0, GRIS)
    art.rectangle([70, ly + 43, 84, ly + 53], outline=BON, width=2)
    ecrire(92, ly + 40, f"l'aile de 241 qui évite la colonne {ligne}, rangées {a241[0]} à {a241[1]}", 0, BON)
    art.rectangle([70, ly + 63, 84, ly + 73], outline=ALERTE, width=2)
    ecrire(92, ly + 60, f"en tirets : là où l'aile est cherchée, sous la rangée {rangee}", 0, ALERTE)

    # ── PANNEAU 2 · LE BORD DROIT ───────────────────────────────────────────────────────────
    panneau(580, 84, 1310, 800, f"LE BORD DROIT · où une colonne de {k} lignes a tous ses chunks, rangée par rangée")
    b = le_bord(d)
    cs, r0, r1 = b["les_colonnes"], b["de"], b["a"]
    BX0, BX1, BY0, BY1 = 680, 1290, 150, 726
    sx = (BX1 - BX0) / max(1, len(cs))
    sy = (BY1 - BY0) / max(1, r1 - r0 + 1)

    def BX(c):
        return BX0 + sx * (c - cs[0])

    def BY(r):
        return BY0 + sy * (r - r0)
    n_b = 0
    for (r, c), t in b["tient"].items():
        if not t:
            continue
        coul = CONTRE if b["permise"][c] else INTERDIT
        art.rectangle([BX(c), BY(r), BX(c + 1) - 1, BY(r + 1)], fill=coul)
        n_b += 1
    art.rectangle([BX0, BY0, BX1, BY1], outline=TRAIT)
    traces["bord"] = n_b
    # la rangée où l'aile de 241 s'arrête, et sa colonne extérieure
    art.line([BX0 - 8, BY(rangee + 0.5), BX1 + 8, BY(rangee + 0.5)], fill=ALERTE, width=2)
    ecrire(BX0 - 64, BY(rangee + 0.5) - 7, f"rang {rangee}", 0, ALERTE)
    if a241[3] in cs:
        art.rectangle([BX(a241[3]), BY(a241[0]), BX(a241[3] + 1), BY(a241[1] + 1)], outline=BON, width=2)
        points.append((BX(a241[3] + 1), BY(a241[1] + 1)))
    for c in (cs[0], ligne, a241[3], cs[-1]):
        if c in cs:
            ecrire(BX(c) - 8, BY1 + 6, f"{c}", 0, ALERTE if c == ligne else GRIS)
    for r in (r0, r1):
        ecrire(BX0 - 64, BY(r) - 7 + (0 if r == r0 else -4), f"rang {r}", 0, GRIS)
    art.rectangle([600, 758, 614, 768], fill=CONTRE)
    ecrire(622, 755, "une colonne extérieure permise", 0, GRIS)
    art.rectangle([840, 758, 854, 768], fill=INTERDIT)
    ecrire(862, 755, f"une colonne qui partage une ligne avec la {ch[3]} ou la {ligne}", 0, GRIS)
    art.rectangle([600, 776, 614, 786], outline=BON, width=2)
    ecrire(622, 773, f"la colonne {a241[3]}, extérieure de l'aile de 241", 0, GRIS)
    ecrire(884, 773, f"trait brun : la rangée {rangee}, où elle s'arrête", 0, ALERTE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    if not co:
        ecrire(50, 856, f"★ sous la rangée {rangee}, aucune colonne extérieure permise ne tient avec deux rangées qui "
                        f"la relient à la {ch[3]} : rien n'est lu.", moyen, ENCRE)
    cv = d.get("la_couverture") or d["la_couverture_de_241"]
    ecrire(50, 882, f"★ les boucles qui tiennent sur leur profil entourent {_fr(cv['la_part'])} de l'empreinte, "
                    f"{cv['combien']} chunks sur {cv['sur']}.", moyen, ENCRE)
    ecrire(50, 908, f"⚠ ce qui n'est PAS établi : si la colonne {ligne} est mal lue sous la rangée {rangee}, ni ce "
                    f"qu'une bande plus étroite y relierait.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_242.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(co, o, f, n_):
        return {"laile": {"les_coins": co}, "le_verdict": {"la_ligne_evitee": 260, "sous_la_rangee": 112,
                                                           "ouverte": o, "franchit": f, "non_vu": n_}}
    tous = [_v([0, 9, 0, 9] if c else None, o, f, n_) for c in (True, False) for o in (True, False)
            for f in (True, False) for n_ in (True, False)]
    v("★★★★ les cinq titres possibles sont distincts, et l'ordre des issues prime",
      len({le_titre(x) for x in tous}) == 5
      and le_titre(_v([0, 9, 0, 9], True, True, False)) == le_titre(_v([0, 9, 0, 9], True, False, False))
      and le_titre(_v([0, 9, 0, 9], False, True, True)) == le_titre(_v([0, 9, 0, 9], False, True, False)))
    v("★★★ le titre LIT le verdict",
      ("AUCUNE AILE" in le_titre(d)) == (not d["laile"].get("les_coins")))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    cv = d.get("la_couverture") or d["la_couverture_de_241"]
    v("★★★★ la carte teinte exactement les chunks que la couverture publiée compte",
      traces.get("carte") == cv["combien"], f"{traces.get('carte')} contre {cv['combien']}")
    b = le_bord(d)
    k = int(d["le_verdict"]["la_largeur_jugee"])
    v("★★★★ le bord ne permet que les colonnes à neuf colonnes au moins de la bande intérieure et de la ligne évitée",
      all(p == (c >= d["les_rangees_cherchees"][3] + k and abs(c - d["la_ligne_evitee"]) >= k)
          for c, p in b["permise"].items())
      and not b["permise"].get(d["la_ligne_evitee"], True) and b["permise"].get(d["laile_de_241"][3], False))
    v("★★★★ le bord montre la colonne extérieure de l'aile de 241 tenant tout du long de l'aile",
      all(b["tient"].get((r, d["laile_de_241"][3]), False) for r in range(d["laile_de_241"][0], d["laile_de_241"][1])))
    v("★★★ le bord trace une case par couture qui tient", traces.get("bord") == sum(b["tient"].values()))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte le verdict, la couverture, et ce qui n'est PAS établi",
      d["le_verdict"]["ce_qui_reste_a_mesurer"] in txt and _fr(cv["la_part"]) in txt and "n'est PAS établi" in txt)
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
    p.add_argument("--json", type=Path, default=MESURES / "sous_laile_qui_evite_la_colonne.json")
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "242_sous_laile_qui_evite_la_colonne.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
