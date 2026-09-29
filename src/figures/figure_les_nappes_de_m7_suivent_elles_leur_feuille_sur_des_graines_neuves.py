"""Le juge déclaré par taux sur vingt-quatre blocs, et les nappes de m7 tirées de huit graines neuves de PHerc0358.

⚠⚠ **Ce que cette figure doit rendre évident.** Bloc par bloc, le Z du tracé humain et celui des deux rampes contre le seuil 3,
avec les deux taux que la règle demande ; puis, graine par graine, le Z de chaque nappe tirée de `m7` et de ses deux spires
suivantes.

  uv run python src/figures/figure_les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.py \\
      --sortie docs/images/301_les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.json"

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
L_, H_ = 1360, 940
LES_SERIES = (("le_segment", "tracé humain", BON), ("saut_1", "saut 1 (rapporté)", BLEU),
              ("rampe_douce", "rampe 14°", VIOLET), ("rampe_raide", "rampe 45°", AMBRE))
LES_NAPPES = (("nappe", "la nappe", BON), ("plus", "spire suivante +", BLEU), ("moins", "spire suivante −", VIOLET))
Z_BAS, Z_HAUT = -4.0, 32.0


def _fr(x, n: int = 1) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    e = d["letalonnage"]["le_verdict"]
    if v.get("separe") is False:
        return (f"NON : MÊME PAR TAUX, LE JUGE NE SÉPARE PAS AU PAS DU PRIX (TRACÉ {_fr(e['le_taux_du_trace'], 3)}, "
                f"RAMPES {_fr(e['le_taux_des_rampes'], 3)})")
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return (f"OUI : {v['k']} DES {v['n']} NAPPES TIRÉES DE m7 SUIVENT LEUR FEUILLE, {v['j']} AVEC UNE SPIRE SUIVANTE "
            f"(JUGE PAR TAUX : {_fr(e['le_taux_du_trace'], 3)} ET {_fr(e['le_taux_des_rampes'], 3)})")


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
    traces = {"blocs": [], "nappes": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    def seuils(x0, x1, base, haut):
        for z, nom, coul in ((0.0, "Z = 0", GRIS), (3.0, "Z = 3", ENCRE)):
            y = _y(z, base, haut)
            art.line([x0, y, x1, y], fill=coul)
            ecrire(x0 - 50, int(y) - 7, nom, 0, coul)

    e = d["letalonnage"]
    ev = e["le_verdict"]
    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, f"la règle : le tracé humain à Z ≥ 3 sur au moins {_fr(d['les_constantes']['le_taux_du_trace'] * 100, 0)} % "
                   f"des blocs, les rampes sur au plus {_fr(d['les_constantes']['le_taux_des_rampes'] * 100, 0)} % · "
                   "échelle écrêtée de −4 à 32", petit, GRIS)

    panneau(50, 74, 1310, 400, "L'ÉTALONNAGE, PHercParis4 AU NIVEAU 2, VINGT-QUATRE BLOCS NEUFS")
    base, haut = 360, 240
    seuils(130, 1290, base, haut)
    for i, b in enumerate(e["les_blocs"]):
        x = 150 + i * 47
        for k, (cle, _, coul) in enumerate(LES_SERIES):
            z = b.get(cle)
            if z is not None:
                y = _y(z, base, haut)
                art.ellipse([x + k * 8 - 3, y - 3, x + k * 8 + 3, y + 3], fill=coul)
                points.append((x + k * 8 + 3, y + 3))
            traces["blocs"].append((tuple(b["le_bloc"]), cle, z))
    for k, (_, nom, coul) in enumerate(LES_SERIES):
        ecrire(160 + k * 240, 100, f"● {nom}", 0, coul)
    ecrire(160, 376, f"tracé humain à Z ≥ 3 : {_fr(ev['le_taux_du_trace'], 3)} des blocs · rampes à Z ≥ 3 : "
                     f"{_fr(ev['le_taux_des_rampes'], 3)} des comparaisons · premier saut, rapporté : "
                     f"{e['le_premier_saut_rapporte']['au_moins_3']} sur {e['le_premier_saut_rapporte']['sur']}", 0,
           BON if ev["separe"] else ALERTE)

    graines = d["le_rouleau"]["les_graines"]
    panneau(50, 416, 1310, 790, "PHerc0358 : LES NAPPES TIRÉES DE m7 DEPUIS HUIT GRAINES NEUVES")
    base, haut = 700, 220
    seuils(130, 1290, base, haut)
    for i, g in enumerate(graines):
        x0 = 150 + i * 142
        for k, (cle, _, coul) in enumerate(LES_NAPPES):
            z = g["le_detail"][cle]["le_z"]
            x = x0 + k * 34
            if z is not None:
                y0_, y1_ = sorted((_y(0.0, base, haut), _y(z, base, haut)))
                art.rectangle([x, y0_, x + 26, y1_], fill=coul)
                points.append((x + 26, y0_))
                ecrire(x, int(min(y0_, y1_)) - 15, _fr(z), 0, ENCRE)
            traces["nappes"].append((g["le_rang"], cle, z))
        ecrire(x0, base + 8, f"graine {g['le_rang']} · {_fr(g['la_hauteur'], 2)}", 0, ENCRE)
        ecrire(x0, base + 24, f"appui {_fr(g['la_part_appuyee'], 2)}", 0, GRIS)
        ecrire(x0, base + 40, g["la_nappe"], 0, BON if g["la_nappe"] == "suit sa feuille" else ALERTE)
    for k, (_, nom, coul) in enumerate(LES_NAPPES):
        ecrire(160 + k * 220, 442, f"■ {nom}", 0, coul)
    if not ev["separe"]:
        ecrire(820, 442, "rapporté : l'étalonnage ne sépare pas, rien n'est jugé", 0, ALERTE)

    art.rectangle([0, 806, L_, H_], fill=BANDE)
    ecrire(50, 818, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 840, "une nappe est un plan de 6 mm posé sur une graine, que chaque point déplace vers la feuille de m7 la plus "
                    "proche avec le vote de 247 ; la spire suivante, la feuille d'après", moyen, ENCRE)
    ecrire(50, 866, "⚠ ce qui n'est PAS établi : sur quelle feuille une nappe est posée ; qu'elle ne passe pas d'une feuille à "
                    "la voisine ; que la spire suivante soit la voisine ;", moyen, ALERTE)
    ecrire(50, 888, "ce que vaut une nappe de 6 mm pour un rouleau entier.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_301.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "separe": False, "lissue": "x"}
    autre["letalonnage"]["le_verdict"].update(le_taux_du_trace=0.875, le_taux_des_rampes=0.0625)
    v("★★★ le titre LIT la mesure", "(TRACÉ 0,875, RAMPES 0,062)" in le_titre(autre) or "(TRACÉ 0,875, RAMPES 0,063)"
      in le_titre(autre), le_titre(autre))
    oui = json.loads(json.dumps(d))
    oui["le_verdict"] = {"decidable": True, "separe": True, "k": 3, "j": 2, "n": 7, "lissue": "x"}
    v("★★★ le titre LIT k, j et n", le_titre(oui).startswith("OUI : 3 DES 7 NAPPES") and "2 AVEC" in le_titre(oui),
      le_titre(oui))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ un point par bloc et par série, chacun au Z mesuré",
      traces["blocs"] == [(tuple(b["le_bloc"]), c, b.get(c)) for b in d["letalonnage"]["les_blocs"] for c, _, _ in LES_SERIES])
    v("★★★★ une barre par graine et par surface, chacune au Z mesuré",
      traces["nappes"] == [(g["le_rang"], c, g["le_detail"][c]["le_z"]) for g in d["le_rouleau"]["les_graines"]
                           for c, _, _ in LES_NAPPES])
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
                   / "301_les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.png")
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
