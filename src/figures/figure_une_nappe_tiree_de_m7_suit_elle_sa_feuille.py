"""L'alignement contre huit traversées : l'étalonnage sur six blocs neufs, et les nappes tirées de m7 sur PHerc0358.

⚠⚠ **Ce que cette figure doit rendre évident.** Bloc par bloc, Z du tracé humain, du premier saut et des deux rampes, contre le
seuil 3 ; sur PHerc0358, Z de chaque nappe tirée de `m7` et de ses deux spires suivantes, à côté de celui des pièces du traceur.

  uv run python src/figures/figure_une_nappe_tiree_de_m7_suit_elle_sa_feuille.py \\
      --sortie docs/images/300_une_nappe_tiree_de_m7_suit_elle_sa_feuille.png

⚠ Tout vient de la mesure.
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
LA_MESURE = RACINE / "docs" / "mesures" / "une_nappe_tiree_de_m7_suit_elle_sa_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
BLEU = (58, 92, 150)
AMBRE = (206, 160, 60)
VIOLET = (120, 84, 150)
L_, H_ = 1360, 920
LES_SERIES = (("le_segment", "tracé humain", BON), ("saut_1", "saut 1", BLEU), ("rampe_douce", "rampe 14°", VIOLET),
              ("rampe_raide", "rampe 45°", AMBRE))
LES_NAPPES = (("nappe", "la nappe", BON), ("plus", "spire suivante +", BLEU), ("moins", "spire suivante −", VIOLET))
Z_BAS, Z_HAUT = -4.0, 32.0


def _fr(x, n: int = 1) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if v.get("separe") is False:
        r = d["letalonnage"]["le_verdict"]["les_raisons"]
        return (f"NON, PAR LA RÈGLE : L'ALIGNEMENT CONTRE HUIT TRAVERSÉES NE SÉPARE PAS AU PAS DU PRIX "
                f"({len(r)} COMPARAISON{'S' if len(r) > 1 else ''} SUR 24 DU MAUVAIS CÔTÉ)")
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def _y(z: float, base: float, haut: float) -> float:
    z = min(max(z, Z_BAS), Z_HAUT)
    return base - (z - Z_BAS) / (Z_HAUT - Z_BAS) * haut


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"blocs": [], "nappes": [], "pieces": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    e = d["letalonnage"]
    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "Z = (alignement − moyenne de huit rampes plantées) / leur écart · une pièce suit sa feuille si Z ≥ 3 · "
                   "échelle écrêtée de −4 à 32", petit, GRIS)

    panneau(50, 74, 1310, 400, "L'ÉTALONNAGE, PHercParis4 AU NIVEAU 2, SIX BLOCS NEUFS")
    base, haut = 360, 240

    def lignes_de_seuil(x0, x1):
        for z, nom, coul in ((0.0, "Z = 0", GRIS), (3.0, "Z = 3", ENCRE)):
            y = _y(z, base, haut)
            art.line([x0, y, x1, y], fill=coul)
            ecrire(x0 - 50, int(y) - 7, nom, 0, coul)

    lignes_de_seuil(130, 1290)
    for i, b in enumerate(e["les_blocs"]):
        x0 = 160 + i * 190
        for k, (cle, _, coul) in enumerate(LES_SERIES):
            z = b.get(cle)
            x = x0 + k * 32
            if z is not None:
                y0_, y1_ = sorted((_y(0.0, base, haut), _y(z, base, haut)))
                art.rectangle([x, y0_, x + 24, y1_], fill=coul)
                points.append((x + 24, y0_))
            traces["blocs"].append((tuple(b["le_bloc"]), cle, z))
        ecrire(x0, base + 8, f"bloc {b['le_bloc'][0]}_{b['le_bloc'][1]}", 0, ENCRE)
    for k, (_, nom, coul) in enumerate(LES_SERIES):
        ecrire(160 + k * 220, 100, f"■ {nom}", 0, coul)
    ecrire(160, 384, " ; ".join(e["le_verdict"]["les_raisons"]) or "le juge sépare", 0,
           ALERTE if e["le_verdict"]["les_raisons"] else BON)

    r = d["le_rouleau"]
    panneau(50, 416, 900, 770, "PHerc0358 : LES NAPPES TIRÉES DE m7 ET LEURS SPIRES SUIVANTES (rapporté)")
    base, haut = 700, 230
    lignes_de_seuil(130, 880)
    for i, g in enumerate(r["les_graines"]):
        x0 = 160 + i * 180
        for k, (cle, _, coul) in enumerate(LES_NAPPES):
            z = g["le_detail"][cle]["le_z"]
            x = x0 + k * 40
            if z is not None:
                y0_, y1_ = sorted((_y(0.0, base, haut), _y(z, base, haut)))
                art.rectangle([x, y0_, x + 30, y1_], fill=coul)
                points.append((x + 30, y0_))
                ecrire(x, int(min(y0_, y1_)) - 15, _fr(z), 0, ENCRE)
            traces["nappes"].append((g["le_rang"], cle, z))
        ecrire(x0, base + 8, f"graine {g['le_rang']}", 0, ENCRE)
        ecrire(x0, base + 24, f"appui {_fr(g['la_part_appuyee'], 2)}", 0, GRIS)
    for k, (_, nom, coul) in enumerate(LES_NAPPES):
        ecrire(160 + k * 200, 442, f"■ {nom}", 0, coul)

    panneau(920, 416, 1310, 770, "LES PIÈCES DU TRACEUR (rapporté)")
    base2 = 700
    xs = {1: 990, 2: 1070, 3: 1150, 4: 1230}
    art.line([950, _y(3.0, base2, 230), 1290, _y(3.0, base2, 230)], fill=ENCRE)
    art.line([950, _y(0.0, base2, 230), 1290, _y(0.0, base2, 230)], fill=GRIS)
    for p in r["les_pieces_du_traceur"]:
        rang = int(p["la_piece"][5])
        z = p["le_z"]
        if z is None:
            continue
        x, y = xs[rang], _y(z, base2, 230)
        art.ellipse([x - 3, y - 3, x + 3, y + 3], fill=ENCRE)
        points.append((x + 3, y + 3))
        traces["pieces"].append((p["la_piece"], z))
    for rang, x in xs.items():
        ecrire(x - 24, base2 + 8, f"trace {rang}", 0, ENCRE)
    ecrire(940, 442, "dix pièces jugées par surface de 299", 0, GRIS)

    art.rectangle([0, 786, L_, H_], fill=BANDE)
    ecrire(50, 798, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 820, "les nappes, leurs spires et les pièces du traceur sont rapportées : par la règle, le rouleau n'est pas jugé",
           moyen, ENCRE)
    ecrire(50, 846, "⚠ ce qui n'est PAS établi : sur quelle feuille une nappe est posée ; qu'elle ne passe pas d'une feuille à "
                    "la voisine ; que la spire suivante soit la voisine ;", moyen, ALERTE)
    ecrire(50, 868, "ce que vaut une nappe de 6 mm pour un rouleau entier.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


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
    tmp = sortie.parent / ".sonde_300.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "separe": False, "lissue": "x"}
    autre["letalonnage"]["le_verdict"]["les_raisons"] = ["a", "b"]
    v("★★★ le titre LIT la mesure", "(2 COMPARAISONS SUR 24" in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ une barre par bloc et par série, chacune au Z mesuré",
      traces["blocs"] == [(tuple(b["le_bloc"]), c, b.get(c)) for b in d["letalonnage"]["les_blocs"] for c, _, _ in LES_SERIES])
    v("★★★★ une barre par graine et par surface, chacune au Z mesuré",
      traces["nappes"] == [(g["le_rang"], c, g["le_detail"][c]["le_z"]) for g in d["le_rouleau"]["les_graines"]
                           for c, _, _ in LES_NAPPES])
    v("★★★ un point par pièce du traceur, à son Z",
      traces["pieces"] == [(p["la_piece"], p["le_z"]) for p in d["le_rouleau"]["les_pieces_du_traceur"]
                           if p["le_z"] is not None])
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
                   / "300_une_nappe_tiree_de_m7_suit_elle_sa_feuille.png")
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
