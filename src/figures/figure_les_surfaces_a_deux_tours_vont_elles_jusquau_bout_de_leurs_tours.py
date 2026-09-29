"""Pour chaque surface que la descente de la chaîne bornée compte juste, graine par graine et saut par saut, combien de ses sommets posés sont au bout de chacun des tours qu'elle retrouve, et si elle va jusqu'au bout de tous.

⚠⚠ **Ce que cette figure doit rendre évident.** Une case par surface comptée, le nombre de sommets posés au bout de chaque tour qu'elle
retrouve écrit dedans. Orange : une surface à deux tours ; gris : une surface à un tour ; foncé si elle va jusqu'au bout de tous ses tours.
Si les cases orange étaient foncées et les grises claires, les surfaces à deux tours traverseraient la couture ; si c'est l'inverse, elles
ne la traversent pas.

  uv run python src/figures/figure_les_surfaces_a_deux_tours_vont_elles_jusquau_bout_de_leurs_tours.py \\
      --sortie docs/images/339_les_surfaces_a_deux_tours_vont_elles_jusquau_bout_de_leurs_tours.png

⚠ Tout vient de la mesure de `339`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_surfaces_a_deux_tours_vont_elles_jusquau_bout_de_leurs_tours.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
LES_COULEURS = {("deux", True): (176, 92, 42), ("deux", False): (236, 204, 180), ("un", True): (120, 124, 130),
                ("un", False): (222, 222, 220)}
L_, H_ = 1360, 580
LA_BANDE = 490


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return (f"{v['k2']} des {v['n2']} surfaces à deux tours touchent le bout de leurs deux tours, contre {v['k1']} des {v['n1']} "
            f"surfaces à un tour").upper()


def le_texte(s: dict) -> str:
    return " · ".join(str(s["au_bout"][str(t)]) for t in s["les_tours_retrouves"])


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cases": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "orange : deux tours ; gris : un tour ; foncé : au bout de tous ses tours (au moins 10 sommets posés à 60 voxels du bout "
                   "de chacun) ; dans la case, ces sommets, tour par tour", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 1310, 470
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    for h in range(1, 9):
        ecrire(x0 + 85 + (h - 1) * 145 + 45, y0 + 10, f"saut {h}", 0, GRIS)
    rangs = sorted({s["le_rang"] for s in d["les_surfaces_a_deux_tours"] + d["les_surfaces_a_un_tour"]})
    for m, r in enumerate(rangs):
        ya = y0 + 32 + m * 44
        ecrire(x0 + 14, ya + 11, f"graine {r}", 0, ENCRE)
        for genre, surfaces in (("un", d["les_surfaces_a_un_tour"]), ("deux", d["les_surfaces_a_deux_tours"])):
            for s in surfaces:
                if s["le_rang"] != r:
                    continue
                xa = x0 + 85 + (s["le_saut"] - 1) * 145
                art.rectangle([xa, ya, xa + 135, ya + 36], fill=LES_COULEURS[(genre, s["jusquau_bout"])])
                ecrire(xa + 8, ya + 11, le_texte(s), 0, (250, 249, 246) if s["jusquau_bout"] else ENCRE)
                traces["cases"].append((genre, r, s["le_saut"], s["jusquau_bout"], le_texte(s), xa + 135 < x1 and ya + 36 < y1))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    tete, _, suite = d["le_verdict"]["lissue"].rpartition(" ; ")
    ecrire(50, LA_BANDE + 10, f"LE VERDICT DÉCLARÉ : {tete} ;", petit, ENCRE)
    ecrire(50, LA_BANDE + 26, suite, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, "⚠ ce qui n'est PAS établi : pourquoi ces surfaces retrouvent deux tours, puisque ce n'est ni l'écart ni la "
                              "couture.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_339.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"].update(k2=7, n2=9, k1=1, n1=3)
    v("★★★ le titre LIT la mesure", le_titre(autre) == "7 DES 9 SURFACES À DEUX TOURS TOUCHENT LE BOUT DE LEURS DEUX TOURS, CONTRE 1 DES 3 "
      "SURFACES À UN TOUR", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = sorted((g, s["le_rang"], s["le_saut"], s["jusquau_bout"], " · ".join(str(s["au_bout"][str(t)]) for t in s["les_tours_retrouves"]))
                     for g, ss in (("un", d["les_surfaces_a_un_tour"]), ("deux", d["les_surfaces_a_deux_tours"])) for s in ss)
    v("★★★ une case par surface comptée, au genre et aux comptes mesurés", sorted(c[:5] for c in traces["cases"]) == attendu)
    v("★★★★ aucune case ne sort du cadre", all(c[5] for c in traces["cases"]))
    v("★★★ deux surfaces n'occupent jamais la même case", len({(c[1], c[2]) for c in traces["cases"]}) == len(traces["cases"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
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
                   / "339_les_surfaces_a_deux_tours_vont_elles_jusquau_bout_de_leurs_tours.png")
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
