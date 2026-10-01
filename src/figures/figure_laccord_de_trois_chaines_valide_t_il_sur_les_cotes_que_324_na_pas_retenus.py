"""Sur PHerc0358 : côté par côté, sur les seize côtés des huit graines, combien des surfaces des trois chaînes l'accord valide, confirme une fois, contredit ou laisse sans témoin.

⚠⚠ **Ce que cette figure doit rendre évident.** Une barre empilée par côté : en bas les surfaces validées en bleu, puis confirmées par une
seule autre chaîne en bleu clair, contredites en orange, sans témoin en gris clair. À gauche les onze côtés que `324` n'a pas retenus, à
droite les cinq qu'il a suivis ; au-dessus de chaque barre, les validées sur les surfaces, et dessous, le plus grand compte validé.

  uv run python src/figures/figure_laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.py \\
      --sortie docs/images/380_laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.png

⚠ Tout vient de la mesure de `380`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (205, 203, 197)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
PALE = (150, 172, 196)
ORANGE = (214, 150, 76)
L_, H_ = 1300, 600
LA_BANDE = 480
HAUT, BAS = 140, 380
LARGEUR, LE_PAS, LE_TROU = 44, 66, 50
LES_STATUTS = (("validée", BLEU), ("confirmée une fois", PALE), ("contredite", ORANGE), ("sans témoin", CLAIR))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_comptes(c: dict) -> dict:
    """Les surfaces d'un côté par statut, leur total, et le plus grand compte d'une surface validée."""
    n = {k: sum(s["le_statut"] == k for s in c["les_surfaces"]) for k, _ in LES_STATUTS}
    n["total"] = len(c["les_surfaces"])
    n["le_plus_loin"] = max((s["le_compte"] for s in c["les_surfaces"] if s["le_statut"] == "validée"), default=None)
    return n


def les_groupes(d: dict) -> tuple[list[dict], list[dict]]:
    """Les côtés neufs puis les côtés suivis, chacun dans l'ordre de la mesure."""
    return ([c for c in d["les_cotes"] if not c["suivi_par_324"]], [c for c in d["les_cotes"] if c["suivi_par_324"]])


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["le_bilan"]
    return (f"hors des côtés de 324 : {b['validees']} surfaces validées sur {b['les_surfaces']}, sur {b['les_cotes_valides']} côtés, "
            f"jusqu'à {b['le_plus_loin']} tours : {v['lissue'].rpartition(' ; ')[2].split(',')[0]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    b = d["le_bilan"]
    vides = sum(1 for c in d["les_cotes"] if not c["suivi_par_324"] and not any(sum(x) for x in c["les_points_par_surface"].values()))
    deux = (f"rapporté à côté, qui ne décide rien : sur {vides} des {b['les_cotes_neufs']} côtés neufs, aucune chaîne ne pose de point ; "
            f"contrôle : les 5 côtés suivis redonnent 374 ({'oui' if d['redonne_374'] else 'non'})")
    trois = "⚠ ce qui n'est PAS établi : si une surface validée hors des côtés de 324 est sur la bonne feuille."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(40, 70, 1260, 460)]
    traces = {"barres": [], "segments": [], "rectangles": [], "dessous": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(40, 20, le_titre(d), gros, ENCRE)
    ecrire(40, 46, "par côté, les surfaces des trois chaînes, empilées : validées (bleu), confirmées une fois (bleu clair), contredites "
                   "(orange), sans témoin (gris)", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 20, BAS, x1 - 20, BAS], fill=GRIS, width=1)
    neufs, suivis = les_groupes(d)
    plus = max((les_comptes(c)["total"] for c in d["les_cotes"]), default=0) or 1
    gauche = x0 + 30
    for g, (nom, cotes) in enumerate((("les côtés que 324 n'a pas retenus", neufs), ("les côtés suivis par 374", suivis))):
        if g:
            gauche += LE_TROU
        ecrire(gauche, y0 + 12, f"{nom} ({len(cotes)})", moyen, ENCRE)
        for c in cotes:
            n = les_comptes(c)
            bas = BAS
            for cle, couleur in LES_STATUTS:
                h = round(n[cle] / plus * (BAS - HAUT))
                if h:
                    art.rectangle([gauche, bas - h, gauche + LARGEUR, bas], fill=couleur)
                    traces["rectangles"].append((gauche, gauche + LARGEUR, bas - h, bas))
                traces["segments"].append((c["le_rang"], c["le_cote"], cle, n[cle], h, couleur))
                bas -= h
            traces["barres"].append((c["le_rang"], c["le_cote"], bool(c["suivi_par_324"]), n["validée"], n["total"], bas))
            ecrire(gauche + 4, bas - 18, f"{n['validée']}/{n['total']}", petit, ENCRE)
            ecrire(gauche, BAS + 8, f"{c['le_rang']} {c['le_cote']}", moyen, ENCRE)
            loin = ("aucune" if n["le_plus_loin"] is None
                    else f"→ {n['le_plus_loin']} tour{'s' if n['le_plus_loin'] > 1 else ''}")
            ecrire(gauche, BAS + 30, loin, petit, GRIS)
            traces["dessous"].append((c["le_rang"], c["le_cote"], n["le_plus_loin"]))
            gauche += LE_PAS

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(40, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(40, LA_BANDE + 28, deux, petit, ENCRE)
    ecrire(40, LA_BANDE + 56, trois, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_380.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"validees": 9, "les_surfaces": 10, "les_cotes_valides": 1, "le_plus_loin": 3})
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; en partie"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "HORS DES CÔTÉS DE 324 : 9 SURFACES VALIDÉES SUR 10, SUR 1 CÔTÉS, JUSQU'À 3 TOURS : "
      "EN PARTIE", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    neufs, suivis = les_groupes(d)
    v("★★★★ les côtés neufs d'abord, puis les suivis, chacun dans l'ordre de la mesure",
      [(r, c, s) for r, c, s, *_ in traces["barres"]] == [(c["le_rang"], c["le_cote"], bool(c["suivi_par_324"])) for c in neufs + suivis]
      and len(traces["barres"]) == len(d["les_cotes"]))
    statuts = ["validée", "confirmée une fois", "contredite", "sans témoin"]
    attendu = [(c["le_rang"], c["le_cote"], k, sum(s["le_statut"] == k for s in c["les_surfaces"])) for c in neufs + suivis for k in statuts]
    v("★★★★ quatre segments par côté, dans l'ordre des statuts, recomptés sur les surfaces",
      [s_[:4] for s_ in traces["segments"]] == attendu, str(traces["segments"][:4]))
    b = d["le_bilan"]
    somme = {k: sum(n for r, c, k_, n, _, _ in traces["segments"] if k_ == k and (r, c) in {(x["le_rang"], x["le_cote"]) for x in neufs})
             for k in statuts}
    v("★★★★ les segments des côtés neufs somment au bilan par statut", somme == b["par_statut"]
      and sum(somme.values()) == b["les_surfaces"], str(somme))
    v("★★★★ validées en bleu, confirmées une fois en bleu clair, contredites en orange, sans témoin en gris clair",
      all(f == {"validée": BLEU, "confirmée une fois": PALE, "contredite": ORANGE, "sans témoin": CLAIR}[k]
          for _, _, k, _, _, f in traces["segments"]))
    plus = max(len(c["les_surfaces"]) for c in d["les_cotes"])
    v("★★★★ la hauteur de chaque segment est son nombre, rapportée au côté le plus fourni",
      all(h == round(n / plus * (BAS - HAUT)) for _, _, _, n, h, _ in traces["segments"]))
    v("★★★★ chaque barre s'élève de la somme de ses segments",
      all(BAS - haut == sum(h for r_, c_, _, _, h, _ in traces["segments"] if (r_, c_) == (r, c))
          for r, c, _, _, _, haut in traces["barres"]))
    loin = [(c["le_rang"], c["le_cote"], max((s["le_compte"] for s in c["les_surfaces"] if s["le_statut"] == "validée"), default=None))
            for c in neufs + suivis]
    v("★★★★ sous chaque côté, le plus grand compte d'une surface validée", traces["dessous"] == loin, str(traces["dessous"]))
    v("★★★ le plus loin des côtés neufs est celui du bilan",
      max((x for (r, c, x) in loin if x is not None and (r, c) in {(y["le_rang"], y["le_cote"]) for y in neufs}), default=None)
      == b["le_plus_loin"])
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    vides = sum(1 for c in neufs if not any(sum(x) for x in c["les_points_par_surface"].values()))
    v("★★★★ la bande compte les côtés neufs sans point et rapporte le contrôle",
      f"sur {vides} des {b['les_cotes_neufs']} côtés neufs" in la_bande(d)[1]
      and f"redonnent 374 ({'oui' if d['redonne_374'] else 'non'})" in la_bande(d)[1])
    vide_suivi = json.loads(json.dumps(d))
    for c in vide_suivi["les_cotes"]:
        if c["suivi_par_324"]:
            c["les_points_par_surface"] = {x: [0] * len(p_) for x, p_ in c["les_points_par_surface"].items()}
    v("★★★★ un côté suivi sans point n'entre pas dans le compte des côtés neufs sans point",
      f"sur {vides} des {b['les_cotes_neufs']} côtés neufs" in la_bande(vide_suivi)[1])
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
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
                   / "380_laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.png")
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
