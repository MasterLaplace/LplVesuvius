"""Sur PHerc0358, à seize sauts : côté par côté, les surfaces validées, contredites et portées par les chaînes de 389, et par les chaînes qui rognent leur plage retombée.

⚠⚠ **Ce que cette figure doit rendre évident.** Trois panneaux, les validées, les contredites et toutes les surfaces des trois chaînes ; une
rangée par côté qui porte des surfaces jugées ; dans chaque rangée, la barre bleue pour les chaînes de `389` et la barre orange pour les
chaînes rognées. Le troisième panneau dit si les contredites baissent parce que les chaînes se contredisent moins ou parce qu'elles sont plus
courtes.

  uv run python src/figures/figure_une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.py \\
      --sortie docs/images/397_une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.png

⚠ Tout vient de la mesure de `397`, et du nombre de surfaces des chaînes que `389` publie.
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
LA_MESURE = RACINE / "docs" / "mesures" / "une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.json"
CE_QUE_389_A_PUBLIE = RACINE / "docs" / "mesures" / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1200, 640
LA_BANDE = 520
LES_PANNEAUX = (("validée", "surfaces validées", 220, 440), ("contredite", "surfaces contredites", 520, 760),
                ("surfaces", "surfaces des trois chaînes", 840, 1080))
HAUT = 120
RANGEE = 36
EPAISSEUR = 12
LES_CHAINES = ("suivie", "compagne", "tierce")


def lire(chemin: Path = LA_MESURE, chemin389: Path = CE_QUE_389_A_PUBLIE) -> dict:
    return {"d": json.loads(chemin.read_text()), "d389": json.loads(chemin389.read_text())}


def les_lignes(m: dict) -> list[dict]:
    """Par côté qui porte une surface validée ou contredite dans l'une des deux mesures : les deux jeux de chaînes."""
    d, d389 = m["d"], m["d389"]
    out = []
    for c, c389 in zip(d["les_cotes"], d389["les_cotes"]):
        cle = f"{c['le_rang']} {c['le_cote']}"
        ref = {**d["la_reference_par_cote"][cle], "surfaces": sum(len(c389["les_nombres"][x]) for x in LES_CHAINES)}
        rog = {**c["les_statuts"], "surfaces": sum(len(c["les_sauts"][x]) for x in LES_CHAINES)}
        if any(ref[k] or rog[k] for k in ("validée", "contredite")):
            out.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "389": ref, "rognees": rog})
    return out


def le_titre(m: dict) -> str:
    v, b, a = m["d"]["le_verdict"], m["d"]["le_bilan"], m["d"]["la_reference"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return (f"rognées, les contredites passent de {a['contredite']} à {b['contredite']}, les validées de {a['validee']} à {b['validee']} : "
            f"{v['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(m: dict) -> tuple[str, ...]:
    d = m["d"]
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    ref = sum(len(c["les_nombres"][x]) for c in m["d389"]["les_cotes"] for x in LES_CHAINES)
    rog = sum(len(c["les_sauts"][x]) for c in d["les_cotes"] for x in LES_CHAINES)
    b = d["le_bilan"]
    deux = (f"rapporté à côté, qui ne décide rien : les chaînes rognées portent {rog} surfaces contre {ref} ; {b['les_surfaces_rognees']} "
            f"des {b['les_surfaces_vues']} surfaces gardées ont perdu {b['les_mailles_retirees']:,} mailles".replace(",", " "))
    trois = "⚠ ce qui n'est PAS établi : si une surface validée est sur la bonne feuille ; PHerc0358 n'a pas de tours publiés."
    return un, deux, trois


def dessiner(m: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1150, 500)]
    traces = {"barres": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(m), gros, ENCRE)
    ecrire(50, 46, "côté par côté : les chaînes de 389 en bleu, les chaînes qui rognent leur plage retombée en orange", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    lignes = les_lignes(m)
    plus = max((r[a][k] for r in lignes for a in ("389", "rognees") for k, _, _, _ in LES_PANNEAUX), default=1) or 1
    for _, nom, g, _ in LES_PANNEAUX:
        ecrire(g, HAUT - 34, nom, moyen, ENCRE)
        art.line([g, HAUT - 10, g, HAUT + len(lignes) * RANGEE], fill=GRIS)
    for i, r in enumerate(lignes):
        y = HAUT + i * RANGEE
        ecrire(70, y + 6, f"graine {r['le_rang']}, {r['le_cote']}", petit, ENCRE)
        for cle, _, g, dr in LES_PANNEAUX:
            for j, (jeu, couleur) in enumerate((("389", BLEU), ("rognees", ORANGE))):
                n = r[jeu][cle]
                yy = y + 2 + j * (EPAISSEUR + 2)
                fin = g + round(n / plus * (dr - g))
                if n:
                    art.rectangle([g + 1, yy, fin, yy + EPAISSEUR], fill=couleur)
                    traces["rectangles"].append((g + 1, fin, yy, yy + EPAISSEUR))
                traces["barres"].append((r["le_rang"], r["le_cote"], cle, jeu, n, fin, couleur))
                ecrire(fin + 6, yy - 1, str(n), petit, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(m)
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

    m = lire(mesure)
    d = m["d"]
    tmp = sortie.parent / ".sonde_397.png"
    try:
        _, poses, cadres, traces = dessiner(m, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(m))
    autre["d"]["le_bilan"]["contredite"] = 7
    autre["d"]["le_verdict"] = {"decidable": True, "lissue": "x ; oui"}
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith(f"ROGNÉES, LES CONTREDITES PASSENT DE {d['la_reference']['contredite']} À 7,")
      and le_titre(autre).endswith(": OUI"), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ les barres validées et contredites des chaînes rognées somment au bilan",
      sum(b[4] for b in traces["barres"] if b[2] == "validée" and b[3] == "rognees") == d["le_bilan"]["validee"]
      and sum(b[4] for b in traces["barres"] if b[2] == "contredite" and b[3] == "rognees") == d["le_bilan"]["contredite"])
    v("★★★★ celles des chaînes de 389 somment à la référence",
      sum(b[4] for b in traces["barres"] if b[2] == "validée" and b[3] == "389") == d["la_reference"]["validee"]
      and sum(b[4] for b in traces["barres"] if b[2] == "contredite" and b[3] == "389") == d["la_reference"]["contredite"])
    v("★★★★ les surfaces de 389 sont recomptées sur ses chaînes", all(
        b[4] == sum(len(c["les_nombres"][x]) for x in LES_CHAINES) for b in traces["barres"] if b[2] == "surfaces" and b[3] == "389"
        for c in m["d389"]["les_cotes"] if (c["le_rang"], c["le_cote"]) == (b[0], b[1])))
    v("★★★★ les surfaces rognées sont recomptées sur leurs chaînes", all(
        b[4] == sum(len(c["les_sauts"][x]) for x in LES_CHAINES) for b in traces["barres"] if b[2] == "surfaces" and b[3] == "rognees"
        for c in d["les_cotes"] if (c["le_rang"], c["le_cote"]) == (b[0], b[1])))
    v("★★★★ 389 en bleu, rognées en orange", all(b[6] == (BLEU if b[3] == "389" else ORANGE) for b in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande porte le verdict entier", la_bande(m)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
    octets = tmp.read_bytes()
    dessiner(m, tmp)
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
                   / "397_une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.png")
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
