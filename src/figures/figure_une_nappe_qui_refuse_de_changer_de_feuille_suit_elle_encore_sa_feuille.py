"""Les nappes de m7 qui croissent depuis leur graine sans changer de feuille, à côté des nappes du vote de 301.

⚠⚠ **Ce que cette figure doit rendre évident.** Graine par graine, la carte du décalage de la nappe croissante le long de la
normale, et en dessous celle de la nappe du vote là où elle est appuyée sur `m7` : une nappe d'une seule feuille a une carte sans
marche de couleur ; la nappe du vote en montre, là où elle passe à la voisine. À côté, ce que le juge en dit.

  uv run python src/figures/figure_une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.py \\
      --sortie docs/images/305_une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
VIDE = (228, 226, 220)
L_, H_ = 1360, 640
LA_BORNE = 30.0     # voxels : la portée de la recherche de part et d'autre du plan


def _fr(x, n: int = 1) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def la_couleur(x: float) -> tuple[int, int, int]:
    """Un décalage de −30 à +30 voxels, du bleu au brun en passant par le clair."""
    t = max(-1.0, min(1.0, x / LA_BORNE))
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

    def carte(x0, y0, c, echelle=2):
        n = 0
        for i, ligne in enumerate(c):
            for j, v in enumerate(ligne):
                art.rectangle([x0 + j * echelle, y0 + i * echelle, x0 + j * echelle + echelle - 1,
                               y0 + i * echelle + echelle - 1], fill=VIDE if v is None else la_couleur(v))
                n += v is not None
        return n

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "décalage le long de la normale de la graine, de −30 (bleu) à +30 voxels (brun) ; en haut la nappe croissante, "
                   "en bas celle du vote de 301 là où elle est appuyée sur m7", petit, GRIS)
    for k, g in enumerate(d["les_graines"]):
        x0, y0, x1, y1 = 50 + k * 158, 72, 50 + k * 158 + 150, 548
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 8, y0 + 8, f"graine {g['le_rang']}", moyen, ENCRE)
        n = carte(x0 + 10, y0 + 32, g["la_carte"])
        traces["cartes"].append((g["le_rang"], "croissante", n))
        if g.get("la_carte_du_vote") is not None:
            n = carte(x0 + 10, y0 + 172, g["la_carte_du_vote"])
            traces["cartes"].append((g["le_rang"], "vote", n))
        else:
            ecrire(x0 + 12, y0 + 230, "vote non retiré", 0, GRIS)
        suit = g["la_nappe"] == "suit sa feuille"
        lignes = [(g["la_nappe"], BON if suit else GRIS),
                  (f"Z {_fr(g['le_z'], 2)} (vote {_fr(g['le_z_de_la_nappe_du_vote'], 2)})", ENCRE),
                  (f"plan posé {_fr(100 * g['la_part_du_plan'], 0)} %", ENCRE),
                  (f"déchirures {_fr(100 * (g['les_dechirures'] or 0), 2)} %", ENCRE),
                  (f"boucles ouvertes {g['les_boucles']['ceux_qui_ne_ferment_pas']}", ENCRE),
                  (f"vote gardé {_fr(None if g.get('la_part_du_vote_gardee') is None else 100 * g['la_part_du_vote_gardee'], 0)} %",
                   GRIS)]
        for m, (t, c) in enumerate(lignes):
            ecrire(x0 + 8, y0 + 316 + 18 * m, t, 0, c)
        if suit and not g["les_boucles"]["ceux_qui_ne_ferment_pas"] and not g["les_dechirures"]:
            ecrire(x0 + 8, y0 + 316 + 18 * len(lignes), "une seule feuille", 0, BON)

    art.rectangle([0, 560, L_, H_], fill=BANDE)
    ecrire(50, 572, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 594, "⚠ ce qui n'est PAS établi : qu'une nappe reste sur une seule feuille là où deux feuilles se touchent sans "
                    "écart ; ce que vaut une croissance point par point sur un rouleau entier.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_305.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "des nappes croissent"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "DES NAPPES CROISSENT", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = []
    for g in d["les_graines"]:
        attendu.append((g["le_rang"], "croissante", sum(x is not None for ligne in g["la_carte"] for x in ligne)))
        if g.get("la_carte_du_vote") is not None:
            attendu.append((g["le_rang"], "vote", sum(x is not None for ligne in g["la_carte_du_vote"] for x in ligne)))
    v("★★★ chaque carte dessine exactement les points mesurés", traces["cartes"] == attendu)
    v("★★★ la couleur va du bleu au brun, et le zéro est clair",
      la_couleur(-30.0)[2] > la_couleur(-30.0)[0] and la_couleur(30.0)[0] > la_couleur(30.0)[2]
      and min(la_couleur(0.0)) > 230)
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
                   / "305_une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.png")
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
