"""L'alignement des profils au pas du prix : l'étalonnage sur six blocs neufs de PHercParis4, et quatre surfaces neuves de PHerc0358.

⚠⚠ **Ce que cette figure doit rendre évident.** Bloc par bloc, le rapport R de l'alignement d'une surface à celui de ses deux
rampes : au-dessus de 2 pour le tracé humain et le premier saut, sous 2 pour les rampes ; et, sur PHerc0358, pièce par pièce, où
chacune des quatre surfaces neuves suit sa feuille.

  uv run python src/figures/figure_lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.py \\
      --sortie docs/images/299_lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.png

⚠ Tout vient de la mesure.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.json"

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
L_, H_ = 1360, 900
LES_SERIES = (("le_segment", "tracé humain", BON), ("saut_1", "saut 1", BLEU), ("rampe_douce", "rampe 14°", VIOLET),
              ("rampe_raide", "rampe 45°", AMBRE), ("decale_dun_demi_pas", "décalé ½ pas (rapporté)", ALERTE))
LES_PIECES = {"suit sa feuille": BON, "ne la suit pas": ALERTE, "non jugée": TRAIT}
R_MAX = 12.0


def _fr(x, n: int = 2) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def _milliers(n: int) -> str:
    return f"{int(n):,}".replace(",", " ")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if v.get("separe") is False:
        return "NON : AU PAS DU PRIX, L'ALIGNEMENT DES PROFILS NE SÉPARE PAS UNE FEUILLE D'UNE TRAVERSÉE"
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    parts = [s["la_part_qui_suit"] for s in d["le_rouleau"]["les_surfaces"]]
    txt = " · ".join(_fr(p) for p in parts)
    if v["lissue"].startswith("aucune"):
        return f"LE JUGE SÉPARE AU PAS DU PRIX, ET AUCUNE DES QUATRE SURFACES NEUVES NE SUIT SA FEUILLE ({txt})"
    return f"LE JUGE SÉPARE AU PAS DU PRIX, ET {v['lissue'].upper()} ({txt})"


def _y_du_rapport(r: float, base: float, haut: float) -> float:
    """Une échelle logarithmique de 1/4 à R_MAX : R = 1 et R = 2 doivent être lisibles tous les deux."""
    r = min(max(r, 0.25), R_MAX)
    return base - (math.log(r) - math.log(0.25)) / (math.log(R_MAX) - math.log(0.25)) * haut


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"points": [], "pieces": [], "releves": None}

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
    ecrire(50, 46, "R = l'alignement du profil moyen d'une pièce / le plus grand de ceux de ses deux rampes plantées · une pièce "
                   f"suit sa feuille si R ≥ {_fr(d['les_constantes']['le_rapport_minimum'], 0)} · ±200 µm le long de la normale",
           petit, GRIS)

    panneau(50, 74, 1310, 400, "L'ÉTALONNAGE, PHercParis4 AU NIVEAU 2 (9,6 µm), SIX BLOCS NEUFS")
    base, haut = 360, 240
    for r, nom in ((1.0, "R = 1"), (2.0, "R = 2")):
        y = _y_du_rapport(r, base, haut)
        art.line([130, y, 1290, y], fill=ENCRE if r == 2.0 else GRIS)
        ecrire(66, int(y) - 7, nom, 0, ENCRE if r == 2.0 else GRIS)
    for i, b in enumerate(e["les_blocs"]):
        x0 = 160 + i * 190
        for k, (cle, _, coul) in enumerate(LES_SERIES):
            r = b.get(cle)
            x = x0 + k * 26
            if r is not None:
                y = _y_du_rapport(r, base, haut)
                art.rectangle([x, y, x + 18, base], fill=coul)
                points.append((x + 18, y))
            traces["points"].append((tuple(b["le_bloc"]), cle, r))
        ecrire(x0, base + 8, f"bloc {b['le_bloc'][0]}_{b['le_bloc'][1]}", 0, ENCRE)
    for k, (_, nom, coul) in enumerate(LES_SERIES):
        ecrire(160 + k * 220, 100, f"■ {nom}", 0, coul)
    ecrire(160, 118, f"le juge {'SÉPARE' if e['le_verdict']['separe'] else 'NE SÉPARE PAS'} au pas du prix · échelle "
                     "logarithmique, écrêtée à 12", 0, BON if e["le_verdict"]["separe"] else ALERTE)

    surfaces = d["le_rouleau"]["les_surfaces"]
    panneau(50, 416, 1310, 760, "PHerc0358 AU NIVEAU 0 (9,362 µm) : QUATRE SURFACES NEUVES, PIÈCE PAR PIÈCE (16 × 16 MAILLES)")
    for k, s in enumerate(surfaces):
        ox, oy = 80 + k * 305, 470
        pieces = s["le_detail"]
        n_i = 1 + max((p["le_groupe"][0] for p in pieces), default=0) // 16
        n_j = 1 + max((p["le_groupe"][1] for p in pieces), default=0) // 16
        case = max(1, min(200 // max(n_i, 1), 200 // max(n_j, 1)))
        art.rectangle([ox, oy, ox + n_j * case, oy + n_i * case], fill=FOND, outline=TRAIT)
        for p in pieces:
            i, j = p["le_groupe"][0] // 16, p["le_groupe"][1] // 16
            art.rectangle([ox + j * case, oy + i * case, ox + (j + 1) * case - 1, oy + (i + 1) * case - 1],
                          fill=LES_PIECES[p["la_piece"]])
            traces["pieces"].append((s["le_rang"], tuple(p["le_groupe"]), p["la_piece"]))
        points.append((ox + n_j * case, oy + n_i * case))
        g = s["la_graine"]
        ecrire(ox, 448, f"graine {s['le_rang']} · {g[0]} {g[1]} {g[2]}", 0, ENCRE)
        ecrire(ox, oy + n_i * case + 8, f"suit sa feuille : {_fr(s['la_part_qui_suit'])}", 0, ENCRE)
        ecrire(ox, oy + n_i * case + 24, f"{_milliers(s['les_points_juges_en_pieces'])} points jugés, "
                                         f"{_milliers(s['sans_matiere'])} sans matière", 0, GRIS)
        ecrire(ox, oy + n_i * case + 40, f"{_fr(s['laire_cm2'], 1)} cm² · {s['les_contacts_transverses']} contacts", 0, GRIS)
    for k, (nom, coul) in enumerate(LES_PIECES.items()):
        ecrire(80 + k * 200, 736, f"■ {nom}", 0, coul)
    if not e["le_verdict"]["separe"]:
        ecrire(700, 736, "rapporté : l'étalonnage ne sépare pas, ces cases ne sont pas un verdict", 0, ALERTE)

    art.rectangle([0, 776, L_, H_], fill=BANDE)
    ecrire(50, 788, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 810, "l'alignement est rapporté aux rampes plantées dans les propres points de la pièce : même matière, même "
                    "nombre de points, mais qui traversent l'empilement", moyen, ENCRE)
    ecrire(50, 836, "⚠ ce qui n'est PAS établi : sur quelle feuille la surface est posée ; qu'elle ne passe pas d'une feuille à "
                    "la voisine en gardant la phase ;", moyen, ALERTE)
    ecrire(50, 858, "qu'elle soit le recto ; qu'elle se déroule ; ce que vaut un autre tirage du traceur sur la même graine.",
           moyen, ALERTE)
    rl = d.get("les_releves")
    if rl:
        seg = rl["letalonnage"]["le_segment"]
        pieces = " · ".join(_fr(x["lalignement_median"]) for x in rl["le_rouleau"])
        rampes = " · ".join(_fr(max(x["celui_de_la_rampe_douce"], x["celui_de_la_rampe_raide"])) for x in rl["le_rouleau"])
        ecrire(50, 880, f"rapporté : l'alignement du tracé humain va de {_fr(seg['lalignement_min'])} à "
                        f"{_fr(seg['lalignement_max'])} par bloc ; celui des pièces des surfaces neuves vaut en médiane "
                        f"{pieces}, celui de leurs rampes {rampes}", petit, ENCRE)
        traces["releves"] = (seg["lalignement_min"], seg["lalignement_max"],
                             [x["lalignement_median"] for x in rl["le_rouleau"]])

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
    tmp = sortie.parent / ".sonde_299.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "separe": True, "lissue": "aucune des surfaces neuves ne suit"}
    for s, p in zip(autre["le_rouleau"]["les_surfaces"], (0.11, 0.22, 0.33, 0.44)):
        s["la_part_qui_suit"] = p
    v("★★★ le titre LIT la mesure", "(0,11 · 0,22 · 0,33 · 0,44)" in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ une barre par bloc et par série, chacune au rapport mesuré",
      traces["points"] == [(tuple(b["le_bloc"]), c, b.get(c)) for b in d["letalonnage"]["les_blocs"] for c, _, _ in
                           LES_SERIES])
    v("★★★★ une case par pièce, à son verdict mesuré",
      traces["pieces"] == [(s["le_rang"], tuple(p["le_groupe"]), p["la_piece"]) for s in d["le_rouleau"]["les_surfaces"]
                           for p in s["le_detail"]])
    v("★★★ l'échelle place R = 2 au-dessus de R = 1", _y_du_rapport(2.0, 360, 240) < _y_du_rapport(1.0, 360, 240))
    rl = d["les_releves"]
    v("★★★ les relevés écrits sont ceux de la mesure",
      traces["releves"] == (rl["letalonnage"]["le_segment"]["lalignement_min"],
                            rl["letalonnage"]["le_segment"]["lalignement_max"],
                            [x["lalignement_median"] for x in rl["le_rouleau"]]))
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
                   / "299_lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.png")
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
