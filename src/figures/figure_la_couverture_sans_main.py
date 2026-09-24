"""La couverture sans main : les boucles que la procédure trouve et leur état, et ce qu'il lui reste à lire.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LA PROCÉDURE sur l'empreinte : le rectangle et chaque aile
qu'elle trouve, dans son état — dessous, franchit, à lire —, et les chunks qu'entourent celles qui tiennent. À droite,
CE QU'IL RESTE À LIRE : ce que chaque boucle à lire coûte en chunks, la plus chère en haut — c'est le panneau qui dit
combien la main a épargné de lecture, et ce qu'il en coûte de s'en passer.

  uv run python src/figures/figure_la_couverture_sans_main.py \\
      --json docs/mesures/la_couverture_sans_main.json \\
      --sortie docs/images/246_la_couverture_sans_main.png
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
L_, H_ = 1360, 1000
LES_COULEURS = {"dessous": BON, "franchit": ALERTE, "à lire": CONTRE}


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def _milliers(n: int) -> str:
    return f"{int(n):,}".replace(",", " ")


def lire(chemin: Path) -> dict:
    """Le JSON de `la_couverture_sans_main.py`, et la présence de `233`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("le_verdict", "le_journal", "la_couverture", "la_couverture_a_la_main", "les_boucles_qui_tiennent"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["la_presence"] = json.loads(CE_QUE_233_A_RENDU.read_text())["la_presence"]
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if not v["il_y_a_un_rectangle"]:
        return "SANS MAIN, AUCUN RECTANGLE NE TIENT : RIEN N'EST RELIÉ"
    if v["il_reste_a_lire"]:
        return (f"SANS MAIN, LA PROCÉDURE REFAIT CE QUE LA MAIN A FAIT, ET DEMANDE {v['combien_de_bandes_a_lire']} "
                f"BANDES DE PLUS")
    c = d.get("la_couverture") or {}
    if c.get("la_part") is not None:
        return (f"SANS MAIN, LA PROCÉDURE VA AU BOUT : ELLE COUVRE {_fr(c['la_part'], 4)} DE L'EMPREINTE ET NE DEMANDE "
                f"PLUS RIEN")
    return "SANS MAIN, LA PROCÉDURE VA AU BOUT ET NE DEMANDE PLUS RIEN"


def les_boucles(d: dict) -> list[dict]:
    """Les boucles que la procédure trouve, dans l'ordre du journal."""
    return [e for e in d["le_journal"] if e.get("les_coins")]


def la_carte(d: dict, s: float) -> tuple[Image.Image, int]:
    """L'empreinte, un pixel par chunk, agrandie sans lissage : les chunks qu'entoure une boucle dessous teintés."""
    rangees = d["la_presence"]["les_rangees"]
    gy, gx = [int(x) for x in d["la_presence"]["la_grille"]]
    M = [[False] * gx for _ in range(gy)]
    for b in d["les_boucles_qui_tiennent"]:
        r0, r1, c0, c1 = [int(x) for x in b["les_coins"]]
        h = int(b["la_largeur"]) // 2
        for r in range(max(0, r0 - h), min(gy, r1 + h + 1)):
            for c in range(max(0, c0 - h), min(gx, c1 + h + 1)):
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

    v = d["le_verdict"]
    bs = les_boucles(d)
    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"le rectangle de 233, puis sur chaque côté la plus large aile de 234, coupée tous les {d['la_portee']} "
                   f"rangs au plus (245), départagée par 236 quand elle franchit ; rien n'est choisi", petit, GRIS)

    # ── PANNEAU 1 · LA PROCÉDURE ────────────────────────────────────────────────────────────
    panneau(50, 84, 560, 800, "LA PROCÉDURE · chaque boucle qu'elle trouve, et son état")
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
    n_b = 0
    for e in bs:
        a0, a1, b0, b1 = [int(x) for x in e["les_coins"]]
        coul = LES_COULEURS.get(e["letat"], GRIS)
        if e["letat"] == "à lire":
            for (p, q) in (((X(b0), Y(a0)), (X(b1 + 1), Y(a0))), ((X(b1 + 1), Y(a0)), (X(b1 + 1), Y(a1 + 1))),
                           ((X(b1 + 1), Y(a1 + 1)), (X(b0), Y(a1 + 1))), ((X(b0), Y(a1 + 1)), (X(b0), Y(a0)))):
                ln = max(abs(q[0] - p[0]), abs(q[1] - p[1]))
                m_ = max(2, int(ln // 6))
                for j in range(0, m_, 2):
                    art.line([p[0] + (q[0] - p[0]) * j / m_, p[1] + (q[1] - p[1]) * j / m_,
                              p[0] + (q[0] - p[0]) * (j + 1) / m_, p[1] + (q[1] - p[1]) * (j + 1) / m_], fill=coul,
                             width=1)
        else:
            art.rectangle([X(b0), Y(a0), X(b1 + 1), Y(a1 + 1)], outline=coul, width=2)
        points.append((X(b1 + 1), Y(a1 + 1)))
        n_b += 1
    traces["boucles"] = n_b
    ly = round(Y(gy)) + 12
    art.rectangle([70, ly + 3, 84, ly + 13], fill=ENTOURE, outline=TRAIT)
    ecrire(92, ly, "un chunk qu'entoure une boucle qui tient", 0, GRIS)
    art.rectangle([70, ly + 23, 84, ly + 33], outline=BON, width=2)
    ecrire(92, ly + 20, "dessous", 0, BON)
    art.rectangle([170, ly + 23, 184, ly + 33], outline=ALERTE, width=2)
    ecrire(192, ly + 20, "franchit", 0, ALERTE)
    art.rectangle([280, ly + 23, 294, ly + 33], outline=CONTRE, width=1)
    ecrire(302, ly + 20, "en tirets : à lire", 0, CONTRE)
    etats = {}
    for e in d["le_journal"]:
        etats[e["letat"]] = etats.get(e["letat"], 0) + 1
    ecrire(70, ly + 44, " · ".join(f"{n} {k}" for k, n in sorted(etats.items())), 0, GRIS)

    # ── PANNEAU 2 · CE QU'IL RESTE À LIRE ───────────────────────────────────────────────────
    panneau(580, 84, 1310, 800, "CE QU'IL RESTE À LIRE · ce que chaque boucle coûte en chunks")
    alire = sorted((e for e in d["le_journal"] if e["letat"] == "à lire"), key=lambda e: -int(e["ce_quelle_coute"]))
    montre = alire[:18]
    CM = max([int(e["ce_quelle_coute"]) for e in montre] + [1])
    BX0, BX1 = 895, 1210
    y0, pas_ = 136, 32
    for i, e in enumerate(montre):
        y = y0 + i * pas_
        nom = "le rectangle" if e["la_boucle"] == "le rectangle" else f"l'aile {e['le_cote']}"
        a0, a1, b0, b1 = e["les_coins"]
        ecrire(596, y + 2, f"{nom} · {e['la_largeur']} lignes · {a0}-{a1} × {b0}-{b1}", 0, ENCRE)
        art.rectangle([BX0, y, BX0 + (BX1 - BX0) * int(e["ce_quelle_coute"]) / CM, y + 16], fill=CONTRE)
        ecrire(BX0 + (BX1 - BX0) * int(e["ce_quelle_coute"]) / CM + 8, y + 2, _milliers(e["ce_quelle_coute"]), 0,
               CONTRE)
        points.append((BX0 + (BX1 - BX0) * int(e["ce_quelle_coute"]) / CM, y + 16))
    traces["a_lire"] = len(montre)
    reste = alire[len(montre):]
    if reste:
        ecrire(596, y0 + len(montre) * pas_ + 4, f"et {len(reste)} boucles de plus, "
                                                 f"{_milliers(sum(int(e['ce_quelle_coute']) for e in reste))} chunks", 0,
               GRIS)
    ecrire(596, 772, f"en tout : {d['le_verdict']['combien_de_bandes_a_lire']} bandes, "
                     f"{_milliers(d['ce_qui_reste_a_lire'])} chunks, que plusieurs boucles se partagent", 0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    cp = d["la_comparaison"]
    ecrire(50, 856, f"★ sans aucun choix, elle retrouve {len(cp['retrouvees'])} des boucles que la main tenait, et la "
                    f"colonne qui dérive ; les {len(cp['tenues_a_la_main_seulement'])} autres sont à lire, au pas qui "
                    f"voit.", moyen, ENCRE)
    ecrire(50, 882, f"★ jugé depuis ce qui est lu : {_fr(d['la_couverture']['la_part'])} de l'empreinte ; à la main, "
                    f"243 : {_fr(d['la_couverture_a_la_main']['la_part'])}.", moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : ce que la procédure couvre une fois tout lu, ni ce qu'elle vaut sur un "
                    "autre segment.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_246.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    t3 = {le_titre({"le_verdict": {"il_y_a_un_rectangle": a, "il_reste_a_lire": b, "combien_de_bandes_a_lire": 3}})
          for a, b in ((False, False), (True, True), (True, False))}
    v("★★★★ les trois titres possibles sont distincts", len(t3) == 3)
    # ⚠ « DEMANDE » seul ne départage rien : le titre de la procédure finie dit « ne demande plus rien ».
    v("★★★ le titre LIT le verdict", ("BANDES DE PLUS" in le_titre(d)) == bool(d["le_verdict"]["il_reste_a_lire"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ la carte teinte exactement les chunks que la couverture publiée compte",
      traces.get("carte") == d["la_couverture"]["combien"], f"{traces.get('carte')} contre {d['la_couverture']['combien']}")
    v("★★★★ chaque boucle trouvée a son cadre, et chaque boucle à lire montrée sa barre",
      traces.get("boucles") == len(les_boucles(d))
      and traces.get("a_lire") == min(18, sum(1 for e in d["le_journal"] if e["letat"] == "à lire")))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte le verdict, les deux couvertures, ce qu'il reste à lire, et ce qui n'est PAS établi",
      d["le_verdict"]["ce_qui_reste_a_mesurer"] in txt and _fr(d["la_couverture"]["la_part"]) in txt
      and _fr(d["la_couverture_a_la_main"]["la_part"]) in txt and _milliers(d["ce_qui_reste_a_lire"]) in txt
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
    p.add_argument("--json", type=Path, default=MESURES / "la_couverture_sans_main.json")
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "246_la_couverture_sans_main.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
