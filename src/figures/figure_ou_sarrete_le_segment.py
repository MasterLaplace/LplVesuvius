"""Où s'arrête le segment : l'empreinte que le dépôt porte, le plus grand rectangle qui y tient, et ses deux chemins.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, L'EMPREINTE : les chunks que le dépôt liste, et
le rectangle dérivé d'elle, avec ceux de `224` et de `232` pour l'échelle. En haut à droite, LES DEUX
CHEMINS À NEUF LIGNES, couture par couture, d'un coin à l'autre, et l'écart où ils arrivent contre le
demi-feuillet — c'est le panneau qui conclut. En bas à droite, LA FERMETURE PAR LARGEUR, le segment entier
contre sa moitié (`228`).

  uv run python src/figures/figure_ou_sarrete_le_segment.py \\
      --json docs/mesures/ou_sarrete_le_segment.json \\
      --sortie docs/images/233_ou_sarrete_le_segment.png
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
CE_QUE_224_A_RENDU = RACINE / "docs" / "mesures" / "deux_chemins_arrivent_ils_sur_la_meme_spire.json"
CE_QUE_232_A_RENDU = RACINE / "docs" / "mesures" / "deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
FRANCHI = (214, 170, 80)
PRESENT = (218, 215, 206)
L_, H_ = 1360, 1000


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une
    virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path) -> dict:
    """Le JSON de `ou_sarrete_le_segment.py`, le grand rectangle de `224` et le rectangle de `232`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("par_largeur", "le_rectangle", "le_verdict", "la_reproduction", "la_presence", "lempreinte",
                "les_bandes_declarees", "les_deux_chemins", "la_moitie_du_segment",
                "le_plus_long_trou_franchi_par_225"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d224 = json.loads(CE_QUE_224_A_RENDU.read_text())
    (a, b), (c, e) = d224["les_boucles"]["le_grand_rectangle"]["les_coins"]
    d["le_rectangle_de_224"] = [int(a), int(c), int(b), int(e)]
    d["le_demi_pli"] = float(d224["le_demi_pli_en_voxels"])
    d["le_rectangle_de_232"] = [int(x) for x in json.loads(CE_QUE_232_A_RENDU.read_text())["le_rectangle"]["les_coins"]]
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer, dans l'ordre de priorité des issues."""
    v = d["le_verdict"]
    if not v["le_rectangle_depasse_la_moitie"]:
        return "LE DÉPÔT NE PORTE PAS DE RECTANGLE PLUS GRAND QUE LA MOITIÉ DU SEGMENT"
    if v["le_segment_entier_reste_ouvert"]:
        return "À NEUF LIGNES, UN TROU TROP LONG LAISSE LE PLUS GRAND RECTANGLE OUVERT"
    if not v["le_segment_entier_se_ferme"]:
        return "À NEUF LIGNES, LES DEUX CHEMINS DU PLUS GRAND RECTANGLE ARRIVENT À UN DEMI-FEUILLET L'UN DE L'AUTRE"
    return "À NEUF LIGNES, LES DEUX CHEMINS DU PLUS GRAND RECTANGLE ARRIVENT SUR LA MÊME SPIRE"


def la_carte(d: dict, s: float) -> tuple[Image.Image, int]:
    """L'empreinte listée, un pixel par chunk puis agrandie sans lissage ; et combien de chunks y sont."""
    rangees = d["la_presence"]["les_rangees"]
    gy, gx = [int(x) for x in d["la_presence"]["la_grille"]]
    img = Image.new("RGB", (gx, gy), FOND)
    img.putdata([PRESENT if ch == "1" else FOND for r in rangees for ch in r])
    n = sum(r.count("1") for r in rangees)
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

    gy, gx = [int(x) for x in d["la_presence"]["la_grille"]]
    r0, r1, c0, c1 = [int(x) for x in d["le_rectangle"]["les_coins"]]
    emp = d["lempreinte"]
    plus_long = int(d["le_plus_long_trou_franchi_par_225"])
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    trous = d["par_largeur"][k1]["les_trous"]
    rp = d["la_reproduction"]
    demi = d["le_demi_pli"]

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"le dépôt listé en {d['la_presence']['les_pages']} pages porte {emp['combien']} chunks sur "
                   f"{emp['sur']} · le rectangle en est dérivé, rien d'autre · ses quatre bandes de neuf lignes, lues "
                   f"pour cette tranche, retombent sur les bandes publiées en {rp['combien_de_coutures_relues']} coutures "
                   f"à l'écart {_fr(rp['lecart_le_plus_grand'])}", petit, GRIS)

    # ── PANNEAU 1 · L'EMPREINTE ─────────────────────────────────────────────────────────────
    panneau(50, 84, 560, 800, "OÙ S'ARRÊTE LE SEGMENT · les chunks que le dépôt porte")
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
    a0, a1, b0, b1 = d["le_rectangle_de_224"]
    art.rectangle([X(b0), Y(a0), X(b1), Y(a1)], outline=GRIS)
    ecrire(X(b0) + 4, Y(a0) + 4, "224 · la moitié du segment", 0, GRIS)
    e0, e1, f0, f1 = d["le_rectangle_de_232"]
    art.rectangle([X(f0), Y(e0), X(f1), Y(e1)], outline=CONTRE)
    ecrire(X(f1) + 4, Y(e0) - 6, "232", 0, CONTRE)

    def la_couleur(cote, seam):
        for t in trous:
            if t["le_cote"] == cote and t["le_debut"] <= seam < t["le_debut"] + t["la_longueur"]:
                return ALERTE if t["la_longueur"] > plus_long else FRANCHI
        return BON
    for cote, sens, centre, de, a in (("haut", "r", r0, c0, c1), ("bas", "r", r1, c0, c1),
                                      ("gauche", "c", c0, r0, r1), ("droite", "c", c1, r0, r1)):
        for seam in range(de, a):
            coul = la_couleur(cote, seam)
            if sens == "r":
                art.rectangle([X(seam), Y(centre - 4), X(seam + 1), Y(centre + 5)], fill=coul)
                points.append((X(seam + 1), Y(centre + 5)))
            else:
                art.rectangle([X(centre - 4), Y(seam), X(centre + 5), Y(seam + 1)], fill=coul)
                points.append((X(centre + 5), Y(seam + 1)))
        traces[cote] = a - de
    ecrire(X(c0) + 14, Y(r0) + 12, f"rangée {r0}", 0, ENCRE)
    ecrire(X(c0) + 14, Y(r1) - 22, f"rangée {r1}", 0, ENCRE)
    ecrire(X(c0) + 14, Y((r0 + r1) / 2) + 60, f"colonne {c0}", 0, ENCRE)
    ecrire(X(c1) - 76, Y((r0 + r1) / 2) + 60, f"colonne {c1}", 0, ENCRE)
    ly = round(Y(gy)) + 12
    art.rectangle([70, ly + 3, 84, ly + 13], fill=PRESENT, outline=TRAIT)
    ecrire(92, ly, f"un chunk que le dépôt porte · rangées {emp['les_rangees'][0]} à {emp['les_rangees'][1]}, "
                   f"colonnes {emp['les_colonnes'][0]} à {emp['les_colonnes'][1]}", 0, GRIS)
    art.rectangle([70, ly + 23, 84, ly + 33], fill=BON)
    ecrire(92, ly + 20, "les bandes du plus grand rectangle : neuf lignes votent à chaque couture", 0, BON)
    art.rectangle([70, ly + 43, 84, ly + 53], outline=CONTRE)
    ecrire(92, ly + 40, "232 · le rectangle dérivé de la croix, resté ouvert", 0, CONTRE)
    art.rectangle([70, ly + 63, 84, ly + 73], outline=GRIS)
    ecrire(92, ly + 60, "224 · le grand rectangle, la moitié du segment", 0, GRIS)

    # ── PANNEAU 2 · LES DEUX CHEMINS ────────────────────────────────────────────────────────
    panneau(580, 84, 1310, 470, "LES DEUX CHEMINS À NEUF LIGNES · d'un coin du rectangle à l'autre")
    ch = d["les_deux_chemins"]
    pr, pc = ch["par_la_rangee_dabord"], ch["par_la_colonne_dabord"]
    n = len(pr) - 1
    ys = pr + pc
    lo, hi = min(min(ys), -demi / 2), max(max(ys), demi)
    lo, hi = lo - 6, hi + 6
    PX0, PX1, PY0, PY1 = 650, 1150, 136, 420

    def PX(i):
        return PX0 + (PX1 - PX0) * i / n

    def PY(v):
        return PY1 - (PY1 - PY0) * (v - lo) / (hi - lo)
    art.line([PX0, PY(0), PX1, PY(0)], fill=TRAIT)
    art.line([PX0, PY0, PX0, PY1], fill=TRAIT)
    for v_ in (-20, 0, 20, 40, 60):
        if lo <= v_ <= hi:
            ecrire(PX0 - 34, PY(v_) - 7, _fr(v_), 0, GRIS)
    for nom, serie, coude, coul in (("par la rangée d'abord", pr, ch["le_coude"], BON),
                                    ("par la colonne d'abord", pc, ch["lautre_coude"], CONTRE)):
        pts = [(PX(i), PY(v)) for i, v in enumerate(serie)]
        art.line(pts, fill=coul, width=2)
        points.extend(pts)
        art.line([PX(coude), PY(serie[coude]) - 8, PX(coude), PY(serie[coude]) + 8], fill=coul, width=2)
        traces[f"chemin:{nom}"] = len(serie)
    ecrire(PX0 + 6, PY0 - 2, f"vert : la rangée {r0} puis la colonne {c1} · bleu : la colonne {c0} puis la rangée {r1}",
           0, GRIS)
    ecrire(PX(ch["le_coude"]) - 30, PY(min(pr[ch["le_coude"] - 20:ch["le_coude"] + 20])) + 12,
           f"coude {ch['le_coude']}", 0, BON)
    ecrire(PX(ch["lautre_coude"]) - 72, PY(pc[ch["lautre_coude"]]) - 24, f"coude {ch['lautre_coude']}", 0, CONTRE)
    ecrire(PX0, PY1 + 8, f"coutures, de 0 à {n}", 0, GRIS)
    fin_r, fin_c = pr[-1], pc[-1]
    xb = PX1 + 16
    art.line([xb, PY(fin_r), xb, PY(fin_c)], fill=ENCRE, width=2)
    for v_ in (fin_r, fin_c):
        art.line([PX1 + 2, PY(v_), xb, PY(v_)], fill=ENCRE)
    xd = PX1 + 30
    art.rectangle([xd, PY(fin_r), xd + 8, PY(fin_r - demi)], fill=TRAIT)
    points.append((xd + 8, PY(fin_r - demi)))
    L9 = d["par_largeur"][k1]["la_fermeture_en_voxels"]
    ecrire(xd + 16, PY((fin_r + fin_c) / 2) - 32, f"écart {_fr(L9)}", 0, ENCRE)
    ecrire(xd + 16, PY((fin_r + fin_c) / 2) - 16, "voxels", 0, ENCRE)
    ecrire(xd + 16, PY(fin_r - demi) - 32, f"demi-feuillet", 0, GRIS)
    ecrire(xd + 16, PY(fin_r - demi) - 16, f"{_fr(demi)} voxels", 0, GRIS)
    ecrire(596, 446, "⚠ un chemin dérive de plusieurs dizaines de voxels ; ce qui compte est l'écart où les deux arrivent",
           0, GRIS)

    # ── PANNEAU 3 · LA FERMETURE PAR LARGEUR ────────────────────────────────────────────────
    panneau(580, 490, 1310, 800, "LA FERMETURE PAR LARGEUR · le segment entier contre sa moitié (228)")
    BX0, BW, VMAX = 690, 360, 70.0

    def BX(v):
        return BX0 + BW * min(abs(float(v)), VMAX) / VMAX
    art.line([BX(demi), 530, BX(demi), 764], fill=ALERTE, width=1)
    ecrire(BX(demi) - 60, 766, f"demi-feuillet · {_fr(demi)}", 0, ALERTE)
    yy = 538
    for k in d["les_largeurs"]:
        e = d["par_largeur"][str(k)]
        m = d["la_moitie_du_segment"][str(k)]
        Le, Lm = e["la_fermeture_en_voxels"], m["la_fermeture_en_voxels"]
        ecrire(596, yy + 8, f"{k} lignes", 0, ENCRE)
        art.rectangle([BX0, yy + 2, BX(Le), yy + 14], fill=BON if abs(Le) < demi else ALERTE)
        art.rectangle([BX0, yy + 18, BX(Lm), yy + 26], fill=TRAIT)
        med = e["le_nul"]["la_fermeture_mediane_en_valeur_absolue"]
        art.line([BX(med), yy, BX(med), yy + 16], fill=ENCRE, width=2)
        points.extend([(BX(Le), yy + 14), (BX(Lm), yy + 26)])
        ecrire(BX0 + BW + 16, yy - 2, f"entier {_fr(Le)} · moitié {_fr(Lm)}", 0, ENCRE)
        ecrire(BX0 + BW + 16, yy + 14, f"bruit seul sous le demi-feuillet {_fr(e['le_nul']['la_part_sous_le_demi_pli'])}",
               0, GRIS)
        traces[f"largeur:{k}"] = 1
        yy += 56
    ecrire(596, 780, "barre pleine : le segment entier · barre claire : la moitié · trait : médiane du bruit seul",
           0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    nul = d["par_largeur"][k1]["le_nul"]
    L5 = d["par_largeur"]["5"]["la_fermeture_en_voxels"]
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {d['le_verdict']['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    ecrire(50, 856, f"★ le plus grand rectangle que le dépôt porte va des rangées {r0} à {r1} et des colonnes {c0} à "
                    f"{c1} : {d['le_rectangle']['le_chemin']} coutures d'un coin à l'autre, contre "
                    f"{d['le_rectangle']['le_chemin_de_224']} pour la moitié du segment.", moyen, ENCRE)
    ecrire(50, 882, f"★ à neuf lignes, ses deux chemins arrivent à {_fr(L9)} voxels l'un de l'autre, sous le "
                    f"demi-feuillet ; à cinq lignes, à {_fr(L5)}, au-delà.", moyen, ENCRE)
    ecrire(50, 908, f"⚠ la fermeture est un tirage : le bruit seul ferme plus serré dans {_fr(nul['la_part_sous_la_fermeture'])} "
                    f"des tirages, et reste sous le demi-feuillet dans {_fr(nul['la_part_sous_le_demi_pli'])}.",
           moyen, ALERTE)
    ecrire(50, 936, "⚠ ce qui n'est PAS établi : le segment entre les bords du rectangle et ceux de l'empreinte, ni lequel "
                    "des deux chemins est sur la bonne spire.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_233.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(dep, ouv, fer):
        return {"le_verdict": {"le_rectangle_depasse_la_moitie": dep, "le_segment_entier_reste_ouvert": ouv,
                               "le_segment_entier_se_ferme": fer}}
    tous = [(a, b, c) for a in (True, False) for b in (True, False) for c in (True, False)]
    v("★★★★ les quatre titres possibles sont distincts, et l'ordre des issues prime",
      len({le_titre(_v(*t)) for t in tous}) == 4
      and len({le_titre(_v(False, b, c)) for _, b, c in tous}) == 1
      and le_titre(_v(True, True, True)) == le_titre(_v(True, True, False)))
    v("★★★ le titre LIT le verdict",
      ("MÊME SPIRE" in le_titre(d)) == bool(d["le_verdict"]["le_segment_entier_se_ferme"]
                                           and not d["le_verdict"]["le_segment_entier_reste_ouvert"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ la carte porte exactement les chunks de l'empreinte publiée",
      traces.get("carte") == int(d["lempreinte"]["combien"]), f"{traces.get('carte')} contre {d['lempreinte']['combien']}")
    r0, r1, c0, c1 = d["le_rectangle"]["les_coins"]
    v("★★★★ chaque couture des quatre côtés est tracée",
      traces.get("haut") == c1 - c0 and traces.get("bas") == c1 - c0 and traces.get("gauche") == r1 - r0
      and traces.get("droite") == r1 - r0)
    ch = d["les_deux_chemins"]
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    v("★★★★ les deux chemins sont tracés en entier, et leur écart final est la fermeture jugée",
      traces.get("chemin:par la rangée d'abord") == d["le_rectangle"]["le_chemin"] + 1
      and traces.get("chemin:par la colonne d'abord") == d["le_rectangle"]["le_chemin"] + 1
      and abs(ch["par_la_rangee_dabord"][-1] - ch["par_la_colonne_dabord"][-1]
              - d["par_largeur"][k1]["la_fermeture_en_voxels"]) < 1e-3)
    v("★★★★ chaque largeur a sa barre", all(traces.get(f"largeur:{k}") for k in d["les_largeurs"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte la fermeture de chaque largeur, entière et moitié, et ce qui n'est PAS établi",
      all(f"entier {_fr(d['par_largeur'][str(k)]['la_fermeture_en_voxels'])} · moitié "
          f"{_fr(d['la_moitie_du_segment'][str(k)]['la_fermeture_en_voxels'])}" in txt for k in d["les_largeurs"])
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
    p.add_argument("--json", type=Path, default=RACINE / "docs" / "mesures" / "ou_sarrete_le_segment.json")
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "233_ou_sarrete_le_segment.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
