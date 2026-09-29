"""La chaîne partie des nappes de m7 d'une seule feuille, chaque saut croissant sans changer de feuille, sur quatre sauts.

⚠⚠ **Ce que cette figure doit rendre évident.** Côté par côté, la carte du pas de chaque saut là où il est posé, comparé au pas du
rouleau (20 voxels) : ce qui reste de la grille à chaque saut, et si le pas y est celui d'une spire. Sous chaque carte, ce que le
juge en dit.

  uv run python src/figures/figure_la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.py \\
      --sortie docs/images/306_la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
VIDE = (228, 226, 220)
L_, H_ = 1360, 800
LA_BANDE = 716
LE_PAS = 20.0


def _fr(x, n: int = 1) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def la_couleur(pas_: float) -> tuple[int, int, int]:
    """L'écart du pas au pas du rouleau, de −20 (bleu, trop court) à +20 voxels (brun, trop long)."""
    t = max(-1.0, min(1.0, (abs(pas_) - LE_PAS) / LE_PAS))
    if t < 0:
        a = -t
        return (int(245 - a * 190), int(242 - a * 150), int(236 - a * 60))
    return (int(245 - t * 70), int(242 - t * 150), int(236 - t * 196))


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cartes": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "pas de chaque saut là où il est posé, comparé au pas du rouleau : clair au pas de 20 voxels, bleu plus court, "
                   "brun plus long ; gris : rien de posé", petit, GRIS)
    for r, c in enumerate(d["les_cotes"]):
        y0, y1 = 72 + r * 160, 72 + r * 160 + 152
        art.rectangle([50, y0, 1310, y1], outline=TRAIT)
        cadres.append((50, y0, 1310, y1))
        ecrire(60, y0 + 8, f"graine {c['le_rang']}, côté {c['le_cote']}", moyen, ENCRE)
        ecrire(60, y0 + 30, f"dernier saut qui tient : {c['le_dernier_saut_qui_tient']}", 0,
               BON if c["le_dernier_saut_qui_tient"] else GRIS)
        for k, s in enumerate(c["les_sauts"]):
            x0 = 260 + k * 262
            n = 0
            for i, ligne in enumerate(s["la_carte"]):
                for j, v in enumerate(ligne):
                    art.rectangle([x0 + j * 2, y0 + 10 + i * 2, x0 + j * 2 + 1, y0 + 11 + i * 2],
                                  fill=VIDE if v is None else la_couleur(v))
                    n += v is not None
            traces["cartes"].append((c["le_rang"], c["le_cote"], s["le_saut"], n))
            tx = x0 + 138
            lignes = [(f"saut {s['le_saut']}", ENCRE), (s["la_piece"], BON if s["la_piece"] == "suit sa feuille" else GRIS),
                      (f"Z {_fr(s['le_z'], 2)}", ENCRE), (f"plan {_fr(100 * s['la_part_du_plan'], 1)} %", ENCRE),
                      (f"pas {_fr(s['le_pas_median_voxels'])}", ENCRE),
                      (f"au pas {_fr(None if s['la_part_au_pas'] is None else 100 * s['la_part_au_pas'], 0)} %", ENCRE),
                      (f"boucles {s['les_boucles']['ceux_qui_ne_ferment_pas']}", ENCRE)]
            for m, (t, col) in enumerate(lignes):
                ecrire(tx, y0 + 10 + 18 * m, t, 0, col)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : que les spires soient consécutives là où m7 manque une feuille ; ce que vaut une "
                    "chaîne de 6 mm sur un rouleau entier.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_306.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "une chaîne tient"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "UNE CHAÎNE TIENT", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(c["le_rang"], c["le_cote"], s["le_saut"], sum(x is not None for ligne in s["la_carte"] for x in ligne))
               for c in d["les_cotes"] for s in c["les_sauts"]]
    v("★★★ chaque carte dessine exactement les points posés", traces["cartes"] == attendu)
    v("★★★ au pas du rouleau la couleur est claire, plus court bleu, plus long brun",
      min(la_couleur(20.0)) > 230 and la_couleur(0.0)[2] > la_couleur(0.0)[0] and la_couleur(-40.0)[0] > la_couleur(-40.0)[2])
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
                   / "306_la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires.png")
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
