"""Sur PHercParis4 : par statut que l'accord de trois chaînes donne à une surface, aux comptes de 369 et aux comptes de m7, la part des surfaces lues qui sont sur le bon tour publié, et combien de surfaces portent ce statut.

⚠⚠ **Ce que cette figure doit rendre évident.** Par statut, deux barres à la part des surfaces lues sur le bon tour : aux comptes de `369`
en gris, aux comptes de `m7` en bleu ; au-dessus, les surfaces sur le bon tour sur les surfaces lues ; dessous, combien de surfaces portent
ce statut aux deux comptes ; en trait plein, les 90 % de la règle.

  uv run python src/figures/figure_laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.py \\
      --sortie docs/images/385_laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.png

⚠ Tout vient de la mesure de `385`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (205, 203, 197)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
L_, H_ = 1200, 580
LA_BANDE = 460
HAUT, BAS = 130, 350
LARGEUR = 56
X0, PAS_X = 180, 240
LES_STATUTS = ("validée", "contredite", "confirmée une fois", "sans témoin")
LES_COMPTES = (("avec_369", CLAIR), ("avec_m7", BLEU))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def en_y(p: float) -> int:
    return BAS - round(p * (BAS - HAUT))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    a, b = d["avec_m7"]["validée"], d["avec_369"]["validée"]
    return (f"aux comptes de m7, {a['sur_le_bon_tour']} sur {a['lues']} validées lues au bon tour, contre {b['sur_le_bon_tour']} sur "
            f"{b['lues']} : {v['lissue'].rpartition(' ; ')[2].partition(',')[0]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    g = d["les_genres"]
    deux = (f"rapporté à côté, qui ne décide rien : des {g['double']['dits']} sauts que 369 compte doubles, {g['double']['une']} ne "
            f"franchissent qu'une feuille de m7 ; {g['simple']['une']} des {g['simple']['dits']} sauts simples dits en franchissent une")
    trois = "⚠ ce qui n'est PAS établi : ce que vaut l'accord aux comptes de m7 sur PHerc0358, dont les feuilles s'écartent autrement."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1150, 440)]
    traces = {"barres": [], "dessous": [], "seuils": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "part des surfaces lues sur le bon tour publié, par statut : aux comptes de 369 (gris) et de m7 (bleu)", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([140, BAS, 1110, BAS], fill=GRIS)
    for k in range(0, 11, 2):
        y = en_y(k / 10.0)
        art.line([136, y, 140, y], fill=GRIS)
        ecrire(90, y - 7, f"{10 * k} %", petit, GRIS)
    for i, st in enumerate(LES_STATUTS):
        xa = X0 + i * PAS_X
        for j, (k, couleur) in enumerate(LES_COMPTES):
            b = d[k][st]
            p = b["sur_le_bon_tour"] / b["lues"] if b["lues"] else 0.0
            y = en_y(p)
            g = xa + j * (LARGEUR + 8)
            art.rectangle([g, y, g + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((st, k, b["sur_le_bon_tour"], b["lues"], y, couleur))
            ecrire(g + 8, y - 18, f"{b['sur_le_bon_tour']}/{b['lues']}", petit, ENCRE)
        ecrire(xa, BAS + 10, st, moyen, ENCRE)
        sous = f"{d['avec_369'][st]['les_surfaces']} puis {d['avec_m7'][st]['les_surfaces']} surfaces"
        ecrire(xa, BAS + 32, sous, petit, GRIS)
        traces["dessous"].append((st, sous))
    yp = en_y(d["les_constantes"]["la_part"])
    art.line([140, yp, 1110, yp], fill=ENCRE, width=2)
    traces["seuils"].append(("la part", d["les_constantes"]["la_part"], yp))
    ecrire(1025, yp - 34, "90 % : la règle", petit, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 56, trois, moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, traces


def verifier(sortie: Path, mesure: Path = LA_MESURE) -> int:
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

    d = lire(mesure)
    tmp = sortie.parent / ".sonde_385.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["avec_m7"]["validée"].update({"sur_le_bon_tour": 9, "lues": 12})
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; en partie"}
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("AUX COMPTES DE M7, 9 SUR 12 VALIDÉES LUES AU BON TOUR, CONTRE ")
      and le_titre(autre).endswith(" : EN PARTIE"), le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(st, k, d[k][st]["sur_le_bon_tour"], d[k][st]["lues"]) for st in ("validée", "contredite", "confirmée une fois", "sans témoin")
               for k in ("avec_369", "avec_m7")]
    v("★★★★ deux barres par statut, aux comptes de 369 puis de m7, lues dans la mesure", [b[:4] for b in traces["barres"]] == attendu,
      str(traces["barres"][:2]))
    v("★★★★ la hauteur d'une barre est sa part de surfaces lues sur le bon tour",
      all(y == BAS - round((bons / lues if lues else 0.0) * (BAS - HAUT)) for _, _, bons, lues, y, _ in traces["barres"]))
    v("★★★★ aux comptes de 369 en gris, de m7 en bleu", all(f == {"avec_369": CLAIR, "avec_m7": BLEU}[k] for _, k, _, _, _, f in traces["barres"]))
    v("★★★★ sous chaque statut, ses surfaces aux deux comptes",
      traces["dessous"] == [(st, f"{d['avec_369'][st]['les_surfaces']} puis {d['avec_m7'][st]['les_surfaces']} surfaces")
                            for st in ("validée", "contredite", "confirmée une fois", "sans témoin")])
    v("★★★★ les surfaces des deux comptes sont les mêmes en tout",
      sum(d["avec_369"][st]["les_surfaces"] for st in d["avec_369"]) == sum(d["avec_m7"][st]["les_surfaces"] for st in d["avec_m7"]))
    v("★★★★ le seuil est celui de la règle, à 90 %",
      traces["seuils"] == [("la part", d["les_constantes"]["la_part"], en_y(d["les_constantes"]["la_part"]))] and d["les_constantes"]["la_part"] == 0.9)
    g = d["les_genres"]
    v("★★★★ la bande rapporte les doubles qui ne franchissent qu'une feuille et les simples",
      f"des {g['double']['dits']} sauts que 369 compte doubles, {g['double']['une']} ne" in la_bande(d)[1]
      and f"{g['simple']['une']} des {g['simple']['dits']} sauts simples dits" in la_bande(d)[1])
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "385_laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.png")
    p.add_argument("--mesure", type=Path, default=LA_MESURE)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie, a.mesure)
    chemin, *_ = dessiner(lire(a.mesure), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
