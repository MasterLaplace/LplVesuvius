"""La correction sans juge, répétée jusqu'à l'arrêt, sur huit blocs pris à pas réguliers : avant, après, et contre quoi.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, BLOC PAR BLOC, la part des points sur la bonne spire avant toute
correction et après la dernière passe : un trait qui monte ou qui descend, et à côté ce que la marche seule a lu, l'écart
type de la différence au départ et à la fin. À droite, LE GAIN CONTRE LA PART AVANT : l'ancre de la correction est la
médiane du bloc, donc un bloc où moins de la moitié des points est juste est celui où elle peut tirer dans le mauvais sens.

  uv run python src/figures/figure_la_correction_tient_elle_sur_des_blocs_reguliers.py \\
      --sortie docs/images/263_la_correction_tient_elle_sur_des_blocs_reguliers.png
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

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "la_correction_tient_elle_sur_des_blocs_reguliers.json"
DE_262 = RACINE / "docs" / "mesures" / "la_correction_repetee_converge_t_elle.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 650


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    d["_262"] = json.loads(DE_262.read_text())
    return d


def les_blocs_de_262(d: dict) -> list[tuple[str, float, float]]:
    """Les deux blocs choisis de `262`, en repère : la part avant toute correction, et après sa dernière passe."""
    out = []
    for nom, b in d["_262"]["les_blocs"].items():
        p = b["les_passes"]
        apres = [q["la_part_sur_la_bonne_spire_apres"] for q in p if q["la_part_sur_la_bonne_spire_apres"] is not None]
        out.append((nom[-3:], p[0]["la_part_avant"], apres[-1]))
    return out


def les_lignes(d: dict) -> list[tuple[str, dict]]:
    """Les blocs que le juge note, du plus bas au plus haut avant correction."""
    ok = [(n, b) for n, b in d["les_blocs"].items() if b["avant"]["la_part_sur_la_bonne_spire"] is not None]
    return sorted(ok, key=lambda nb: (nb[1]["avant"]["la_part_sur_la_bonne_spire"], nb[0]))


def la_couleur(b: dict):
    return BON if b["la_suite"] == "plus haute" else ALERTE if b["la_suite"] == "plus basse" else GRIS


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : sur combien de blocs la part monte, descend, et la part réunie."""
    c = d["le_verdict"]["les_comptes"]
    r = d["reunis"]
    return (f"PRISE À PAS RÉGULIERS, LA CORRECTION SANS JUGE MONTE SUR {c['plus haute']} BLOCS, DESCEND SUR "
            f"{c['plus basse']}, NE BOUGE PAS SUR {c['égale']} ; RÉUNIS, DE {_fr(r['avant'], 4)} À {_fr(r['apres'], 4)}")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(17, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {"avant": 0, "apres": 0, "gain": 0, "repere": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    def point(x, y, coul, plein=True):
        if plein:
            art.ellipse([x - 5, y - 5, x + 5, y + 5], fill=coul)
        else:
            art.ellipse([x - 5, y - 5, x + 5, y + 5], outline=coul, width=2)
        points.append((x, y))

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · les blocs candidats de 257 en ordre, les deux déjà étudiés retirés, huit "
                   "pris à pas réguliers · la procédure de 262 sans changement · le juge ne sert qu'à juger", petit, GRIS)
    lignes = les_lignes(d)

    # ── PANNEAU 1 · BLOC PAR BLOC ──────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 800, 510, "LA PART SUR LA BONNE SPIRE, AVANT ○ ET APRÈS ●, BLOC PAR BLOC")
    gx0, gx1, gy0 = 330, 570, 150
    pas = min(40, (470 - gy0) // max(1, len(lignes) + 1))
    parts = [b[k]["la_part_sur_la_bonne_spire"] for _, b in lignes for k in ("avant", "apres")]
    x_lo = min(0.5, float(np.floor(10 * min(parts))) / 10)
    xx = lambda v: gx0 + (gx1 - gx0) * (v - x_lo) / (1.0 - x_lo)  # noqa: E731
    for v in (x_lo, (x_lo + 1.0) / 2, 1.0):
        art.line([xx(v), gy0 - 18, xx(v), gy0 + pas * (len(lignes) + 1) - 16], fill=TRAIT)
        ecrire(xx(v) - 10, gy0 - 36, _fr(v, 2), 0, GRIS)
    ecrire(600, gy0 - 36, "l'écart type lu, au départ → à la fin", 0, GRIS)
    for k, (nom, b) in enumerate(lignes):
        y = gy0 + pas * k
        p = b["les_passes"]
        ecrire(66, y - 7, f"({b['la_rangee']}, {b['la_colonne']}) · {b['avant']['les_points_notes']} points · "
                          f"{len(p)} passe{'s' if len(p) > 1 else ''}", 0, ENCRE)
        a, z = b["avant"]["la_part_sur_la_bonne_spire"], b["apres"]["la_part_sur_la_bonne_spire"]
        coul = la_couleur(b)
        art.line([xx(a), y, xx(z), y], fill=coul, width=3)
        point(xx(a), y, GRIS, plein=False)
        traces["avant"] += 1
        point(xx(z), y, coul)
        traces["apres"] += 1
        ecrire(600, y - 7, f"{_fr(p[0]['lecart_type_de_la_difference_lue_voxels'], 1)} → "
                           f"{_fr(p[-1]['lecart_type_de_la_difference_lue_voxels'], 1)} voxels", 0, GRIS)
    r = d["reunis"]
    y = gy0 + pas * len(lignes) + 8
    ecrire(66, y - 7, f"réunis · {r['les_points_notes']} points", 0, ENCRE)
    art.line([xx(r["avant"]), y, xx(r["apres"]), y], fill=ENCRE, width=3)
    point(xx(r["avant"]), y, ENCRE, plein=False)
    point(xx(r["apres"]), y, ENCRE)
    ecrire(600, y - 7, f"{_fr(r['avant'], 4)} → {_fr(r['apres'], 4)}", 0, ENCRE)
    ecrire(66, y + 16, f"{r['les_rates_rendus_justes']} ratés rendus justes, {r['les_justes_rendus_rates']} justes rendus "
                       "ratés", 0, ENCRE)
    sans = [f"({b['la_rangee']}, {b['la_colonne']})" for b in d["les_blocs"].values()
            if b["avant"]["la_part_sur_la_bonne_spire"] is None]
    if sans:
        ecrire(66, y + 36, f"{', '.join(sans)} : aucun point que le juge note, hors de la réunion", 0, GRIS)

    # ── PANNEAU 2 · LE GAIN CONTRE LA PART AVANT ───────────────────────────────────────────────────────────────────
    panneau(820, 80, 1310, 510, "LE GAIN CONTRE LA PART AVANT")
    ref262 = les_blocs_de_262(d)
    gains = [b["apres"]["la_part_sur_la_bonne_spire"] - b["avant"]["la_part_sur_la_bonne_spire"] for _, b in lignes]
    hi = max(0.1, 0.1 * float(np.ceil(10 * max(abs(g) for g in gains + [z - a for _, a, z in ref262]))))
    hx0, hx1, hy0, hy1, lo = 880, 1280, 130, 440, -hi
    hxx = lambda v: hx0 + (hx1 - hx0) * v  # noqa: E731
    hyy = lambda g: hy1 - (hy1 - hy0) * (g - lo) / (hi - lo)  # noqa: E731
    for g in (lo, lo / 2, 0.0, hi / 2, hi):
        art.line([hx0, hyy(g), hx1, hyy(g)], fill=GRIS if g == 0.0 else TRAIT)
        ecrire(hx0 - 44, hyy(g) - 7, ("+" if g > 0 else "") + _fr(g, 2), 0, GRIS)
    art.line([hxx(0.5), hy0, hxx(0.5), hy1], fill=GRIS)
    for v in (0.0, 0.5, 1.0):
        ecrire(hxx(v) - 8, hy1 + 8, _fr(v, 1), 0, GRIS)
    ecrire(hxx(0.5) + 6, hy1 - 20, "la moitié juste", 0, GRIS)
    ecrire(hx0, hy1 + 26, "la part sur la bonne spire avant toute correction", 0, GRIS)
    for nom, b in lignes:
        a, z = b["avant"]["la_part_sur_la_bonne_spire"], b["apres"]["la_part_sur_la_bonne_spire"]
        point(hxx(a), hyy(z - a), la_couleur(b))
        traces["gain"] += 1
    for nom, a, z in ref262:
        point(hxx(a), hyy(z - a), ENCRE, plein=False)
        ecrire(hxx(a) + 9, hyy(z - a) - 7, f"le bloc de {nom}, choisi en 262", 0, ENCRE)
        traces["repere"] += 1
    ecrire(hx0, hy1 + 44, "● les blocs pris à pas réguliers   ○ les deux blocs choisis de 262", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 526, L_, H_], fill=BANDE)
    ecrire(50, 538, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    q = r["la_premiere_passe"]
    ecrire(50, 560, f"★ réunis, {r['les_rates_rendus_justes']} ratés rendus justes pour {r['les_justes_rendus_rates']} "
                    f"justes rendus ratés : la première passe signale {q['les_rates_signales']} des {q['les_rates']} ratés "
                    f"et {q['les_justes_signales']} des {q['les_justes']} justes.", moyen, ENCRE)
    ecrire(50, 586, f"la procédure s'arrête seule sur {r['les_blocs_qui_sarretent_seuls']} blocs sur "
                    f"{r['les_blocs_decidables']} ; aucun bloc n'a été choisi, le juge n'a rien décidé.", moyen, ENCRE)
    ecrire(50, 612, "⚠ ce qui n'est PAS établi : une règle qui saurait, sans le juge, où ne pas corriger ; une boucle ; un "
                    "autre côté.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_263.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    c = d["le_verdict"]["les_comptes"]
    v("★★★ le titre LIT la mesure", f"MONTE SUR {c['plus haute']} BLOCS, DESCEND SUR {c['plus basse']}" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    n = len(les_lignes(d))
    v("★★★★ chaque bloc noté a son avant, son après et son gain, et les deux blocs de 262 leur repère",
      traces == {"avant": n, "apres": n, "gain": n, "repere": len(les_blocs_de_262(d))}, str(traces))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ chaque bloc est écrit avec ses points notés",
      all(f"({b['la_rangee']}, {b['la_colonne']}) · {b['avant']['les_points_notes']} points" in txt for _, b in les_lignes(d)))
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
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
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "263_la_correction_tient_elle_sur_des_blocs_reguliers.png")
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
