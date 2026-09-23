"""Une bande plus large ferme-t-elle le grand rectangle : la fermeture, le bruit, et les côtés, largeur par largeur.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, LA FERMETURE DU GRAND RECTANGLE à chaque
largeur de l'échelle de `218`, contre le demi-feuillet et contre le bruit seul — c'est le panneau qui
conclut, et il montre aussi que la fermeture ne décroît pas avec la largeur. En haut à droite, LE BRUIT : la
dispersion du pas et la part des tirages sous le demi-feuillet. En bas, LES QUATRE CÔTÉS à chaque largeur :
celui qui porte la fermeture.

  uv run python src/figures/figure_une_bande_plus_large_ferme_t_elle_le_grand_rectangle.py \\
      --json docs/mesures/une_bande_plus_large_ferme_t_elle_le_grand_rectangle.json \\
      --sortie docs/images/228_une_bande_plus_large_ferme_t_elle_le_grand_rectangle.png
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

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
BRUIT = (222, 220, 214)
LES_COTES = (("haut", "rangée du haut", CONTRE), ("droite", "colonne de droite", GRIS),
             ("bas", "rangée du bas", BON), ("gauche", "colonne de gauche", ALERTE))
L_, H_ = 1360, 1000


def _fr(x, n: int = 3) -> str:
    """Un nombre en français. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def _signe(x) -> str:
    return ("+" if float(x) > 0 else "") + _fr(x, 4)


def lire(chemin: Path) -> dict:
    """Le JSON de `une_bande_plus_large_ferme_t_elle_le_grand_rectangle.py`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("par_largeur", "les_largeurs", "le_verdict", "la_reproduction", "la_fermeture_de_225"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if not v["le_bruit_diminue_de_cinq_a_neuf"]:
        return "À NEUF LIGNES, LE BRUIT NE DIMINUE PAS : LA LARGEUR NE RÉDUIT PAS L'ERREUR DU CONSENSUS"
    if not v["le_grand_rectangle_se_ferme_a_neuf"]:
        return "LA LARGEUR RÉDUIT LE BRUIT, MAIS LE GRAND RECTANGLE RESTE AU-DELÀ DU DEMI-FEUILLET"
    return "À NEUF LIGNES, LE BRUIT DIMINUE ET LE GRAND RECTANGLE SE FERME SOUS LE DEMI-FEUILLET"


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

    ks = [int(k) for k in d["les_largeurs"]]
    P = d["par_largeur"]
    demi = 36.0
    ve = d["le_verdict"]

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"les quatre bandes du grand rectangle élargies de cinq à neuf lignes, lues pour cette tranche et "
                   f"retombées sur 219, 223 et 224 en {d['la_reproduction']['combien_de_coutures_relues']} coutures · "
                   f"à cinq lignes, la fermeture retombe sur celle de 225 : {_signe(d['la_fermeture_de_225'])} vx",
           petit, GRIS)

    # ── PANNEAU 1 · LA FERMETURE, LARGEUR PAR LARGEUR ───────────────────────────────────────
    panneau(50, 84, 670, 470, "LA FERMETURE DU GRAND RECTANGLE · à chaque largeur de 218")
    gx0, gx1, gy0, gy1 = 130, 600, 130, 420
    borne = 48.0

    def px(i):
        return gx0 + (gx1 - gx0) * i / (len(ks) - 1)

    def py(v):
        return gy0 + (gy1 - gy0) * (borne - float(v)) / (2 * borne)
    for yv, lab, coul in ((demi, f"+{int(demi)}", ALERTE), (0.0, "0", GRIS), (-demi, f"-{int(demi)}", ALERTE)):
        art.line([gx0 - 20, py(yv), gx1 + 20, py(yv)], fill=coul, width=1)
        ecrire(gx0 - 60, py(yv) - 7, f"{lab} vx", 0, coul)
    for i, k in enumerate(ks):
        m = float(P[str(k)]["le_nul"]["la_fermeture_mediane_en_valeur_absolue"])
        art.rectangle([px(i) - 14, py(m), px(i) + 14, py(-m)], fill=BRUIT)
    pts = [(px(i), py(P[str(k)]["la_fermeture_en_voxels"])) for i, k in enumerate(ks)]
    art.line(pts, fill=CONTRE, width=1)
    for i, k in enumerate(ks):
        x = P[str(k)]
        coul = BON if x["sous_le_demi_pli"] else ALERTE
        X, Y = pts[i]
        art.ellipse([X - 6, Y - 6, X + 6, Y + 6], fill=coul)
        ecrire(X - 30, Y + 10 if x["la_fermeture_en_voxels"] < 0 else Y - 24, _signe(x["la_fermeture_en_voxels"]), 0, coul)
        ecrire(X - 20, gy1 + 10, f"{k} lignes", 0, ENCRE)
        points.append((X, Y))
    traces["fermetures"] = len(pts)
    ecrire(66, 452, "gris : ± la fermeture médiane du bruit seul, les quatre côtés tirés indépendamment par blocs", 0, GRIS)

    # ── PANNEAU 2 · LE BRUIT ────────────────────────────────────────────────────────────────
    panneau(690, 84, 1310, 470, "LE BRUIT · il diminue avec la largeur")
    yy = 140
    ecrire(706, yy, "lignes", 0, GRIS)
    ecrire(790, yy, "dispersion du pas", 0, GRIS)
    ecrire(940, yy, "bruit seul : médiane", 0, GRIS)
    ecrire(1100, yy, "sous le demi-feuillet", 0, GRIS)
    yy += 28
    smax = max(float(P[str(k)]["la_dispersion_du_pas_en_voxels"]) for k in ks)
    for k in ks:
        x = P[str(k)]
        ecrire(716, yy, str(k), 0, ENCRE)
        s_ = float(x["la_dispersion_du_pas_en_voxels"])
        art.rectangle([790, yy + 14, 790 + 120 * s_ / smax, yy + 20], fill=CONTRE)
        ecrire(790, yy - 2, f"{_fr(s_, 4)} vx", 0, CONTRE)
        ecrire(940, yy - 2, f"{_fr(x['le_nul']['la_fermeture_mediane_en_valeur_absolue'], 4)} vx", 0, ENCRE)
        part = float(x["le_nul"]["la_part_sous_le_demi_pli"])
        art.rectangle([1100, yy + 14, 1100 + 150 * part, yy + 20], fill=BON)
        ecrire(1100, yy - 2, _fr(part, 4), 0, BON)
        points.append((1100 + 150 * part, yy + 20))
        yy += 52
    ecrire(706, 400, "la dispersion du pas baisse avec la largeur, et le bruit seul avec elle", 0, ENCRE)
    ecrire(706, 418, "⚠ une part que les lignes voisines partageraient ne baisserait pas (208)", 0, ALERTE)

    # ── PANNEAU 3 · LES QUATRE CÔTÉS ────────────────────────────────────────────────────────
    panneau(50, 490, 1310, 800, "LES QUATRE CÔTÉS · la somme des pas du consensus le long de chacun, en voxels")
    bx0, by0, by1 = 150, 540, 740
    vmax = max(abs(float(c["la_somme_en_voxels"])) for k in ks for c in P[str(k)]["les_cotes"]) * 1.1
    yz = (by0 + by1) / 2

    def qy(v):
        return yz - (by1 - by0) / 2 * float(v) / vmax
    art.line([bx0 - 20, yz, 1200, yz], fill=TRAIT, width=1)
    ecrire(bx0 - 60, yz - 7, "0", 0, GRIS)
    largeur_groupe = 250
    for i, k in enumerate(ks):
        cotes = {c["le_cote"]: float(c["la_somme_en_voxels"]) for c in P[str(k)]["les_cotes"]}
        gx = bx0 + i * largeur_groupe
        for j, (nom, lab, coul) in enumerate(LES_COTES):
            x_ = gx + j * 44
            v = cotes[nom]
            art.rectangle([x_, min(qy(v), yz), x_ + 34, max(qy(v), yz)], fill=coul)
            ecrire(x_ - 6, (qy(v) - 16) if v >= 0 else (qy(v) + 4), _fr(v, 2), 0, coul)
            points.append((x_ + 34, qy(v)))
            traces[f"{k}:{nom}"] = 1
        ecrire(gx + 50, by1 + 16, f"{k} lignes", 0, ENCRE)
    for j, (nom, lab, coul) in enumerate(LES_COTES):
        ecrire(1170 - 0, 560 + 22 * j, lab, 0, coul)
    ecrire(66, 776, "la fermeture est haut + droite − bas − gauche : la colonne de gauche en porte l'essentiel à toutes "
                    "les largeurs", 0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {d['le_verdict']['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    p9, p5 = P[str(ks[-1])], P["5"]
    ecrire(50, 856, f"★ de cinq à neuf lignes, le bruit seul passe de {_fr(p5['le_nul']['la_fermeture_mediane_en_valeur_absolue'], 4)} "
                    f"à {_fr(p9['le_nul']['la_fermeture_mediane_en_valeur_absolue'], 4)} vx, et le grand rectangle ferme à "
                    f"{_signe(p9['la_fermeture_en_voxels'])} vx.", moyen, ENCRE)
    ecrire(50, 882, f"⚠⚠ mais la fermeture ne décroît pas avec la largeur : à trois lignes déjà elle est à "
                    f"{_signe(P[str(ks[0])]['la_fermeture_en_voxels'])} vx — celle de cinq lignes était un tirage juste "
                    f"au-delà du demi-feuillet.", moyen, ALERTE)
    ecrire(50, 908, f"⚠ et à neuf lignes, le bruit seul ne reste sous le demi-feuillet que dans "
                    f"{_fr(p9['le_nul']['la_part_sous_le_demi_pli'], 4)} des tirages : la largeur rend l'issue plus "
                    f"probable, pas certaine.", moyen, ALERTE)
    ecrire(50, 936, "⚠ ce qui n'est PAS établi : pourquoi la colonne de gauche porte la fermeture à toutes les largeurs.",
           moyen, ALERTE)
    ecrire(50, 962, "★ la suite : la colonne 71 porte-t-elle, dans sa moitié haute, une erreur que ses lignes partagent ?",
           moyen, ENCRE)

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
    tmp = sortie.parent / ".sonde_228.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(a, b):
        return {"le_verdict": {"le_bruit_diminue_de_cinq_a_neuf": a, "le_grand_rectangle_se_ferme_a_neuf": b}}
    v("★★★★ les trois titres possibles sont distincts, et ne pas réduire le bruit prime",
      len({le_titre(_v(a, b)) for a in (True, False) for b in (True, False)}) == 3
      and le_titre(_v(False, True)) == le_titre(_v(False, False)))
    v("★★★ le titre LIT le verdict", ("SE FERME SOUS" in le_titre(d)) == (
        d["le_verdict"]["le_bruit_diminue_de_cinq_a_neuf"] and d["le_verdict"]["le_grand_rectangle_se_ferme_a_neuf"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    ks = d["les_largeurs"]
    v("★★★★ chaque largeur et chacun de ses quatre côtés sont tracés",
      traces.get("fermetures") == len(ks) and all(traces.get(f"{k}:{n}") for k in ks for n in ("haut", "droite", "bas", "gauche")))
    txt = " ".join(t for _, _, t, _ in poses)
    P = d["par_largeur"]
    v("★★★★ elle porte la fermeture, la dispersion et le bruit seul de chaque largeur",
      all(_signe(P[str(k)]["la_fermeture_en_voxels"]) in txt and _fr(P[str(k)]["la_dispersion_du_pas_en_voxels"], 4) in txt
          and _fr(P[str(k)]["le_nul"]["la_fermeture_mediane_en_valeur_absolue"], 4) in txt for k in ks))
    v("★★★★ elle dit que la fermeture ne décroît pas avec la largeur, et ce qui n'est PAS établi",
      "ne décroît pas" in txt and "n'est PAS établi" in txt)
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
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "une_bande_plus_large_ferme_t_elle_le_grand_rectangle.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "228_une_bande_plus_large_ferme_t_elle_le_grand_rectangle.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
