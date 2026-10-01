"""Sur les côtés où l'écart majoritaire décale une chaîne, sur PHercParis4 et sur PHerc0358 : les surfaces validées sans alignement et alignées, et l'écart retenu.

⚠⚠ **Ce que cette figure doit rendre évident.** Par côté où l'écart majoritaire décale une chaîne, deux barres : les surfaces validées sans
alignement (gris) et alignées (bleu) ; dessous, la chaîne décalée, l'écart, et sur combien de paires même feuille il est porté ; et si les
tours publiés jugent ce côté.

  uv run python src/figures/figure_un_ecart_pris_sur_cinq_paires_qui_saccordent_aligne_t_il_sans_deplacer_une_surface_lue.py \\
      --sortie docs/images/388_un_ecart_pris_sur_cinq_paires_qui_saccordent_aligne_t_il_sans_deplacer_une_surface_lue.png

⚠ Tout vient de la mesure de `388`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "un_ecart_pris_sur_cinq_paires_qui_saccordent_aligne_t_il_sans_deplacer_une_surface_lue.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (205, 203, 197)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
L_, H_ = 1400, 580
LA_BANDE = 460
HAUT, BAS = 140, 330
LARGEUR = 50
LES_ROULEAUX = (("les_cotes_de_paris4", "PHercParis4"), ("les_cotes_de_0358", "PHerc0358"))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_decales(d: dict) -> list[tuple[str, dict]]:
    """Les côtés où l'écart majoritaire décale une chaîne, PHercParis4 d'abord, dans l'ordre de la mesure."""
    return [(nom, c) for cle, nom in LES_ROULEAUX for c in d[cle] if any(e["lecart"] for e in c["les_ecarts"].values())]


def les_ecarts_dits(c: dict) -> str:
    return " ; ".join(f"la {x} {e['lecart']:+d} ({e['porte_par']} paires sur {e['les_paires_meme_feuille']})"
                      for x, e in c["les_ecarts"].items() if e["lecart"])


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    n = d["les_deplacees"]
    pl = "s" if n > 1 else ""
    return (f"écart majoritaire : {n} surface{pl} lue{pl} déplacée{pl} sur PHercParis4 : "
            f"{v['lissue'].rpartition(' ; ')[2].partition(',')[0]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    p4 = [c for n, c in les_decales(d) if n == "PHercParis4"]
    juges = [c for c in p4 if c["le_cote"] == "moins"]
    deux = (f"rapporté à côté, qui ne décide rien : sur PHercParis4, l'écart majoritaire décale une chaîne sur {len(p4)} côté"
            f"{'s' if len(p4) > 1 else ''}, dont {len(juges)} que les tours publiés jugent")
    trois = "⚠ ce qui n'est PAS établi : si cinq paires qui s'accordent ne peuvent pas être toutes fausses."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1350, 440)]
    traces = {"barres": [], "rectangles": [], "dessous": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "par côté où l'écart majoritaire décale une chaîne : surfaces validées sans alignement (gris) et alignées (bleu)", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 20, BAS, x1 - 20, BAS], fill=GRIS)
    ds = les_decales(d)
    plus = max((n for _, c in ds for n in c["validees"]), default=0) or 1
    pas = (x1 - x0 - 60) // max(1, len(ds))
    for i, (rouleau, c) in enumerate(ds):
        gauche = x0 + 50 + i * pas
        for j, (n, couleur) in enumerate(zip(c["validees"], (CLAIR, BLEU))):
            g = gauche + j * (LARGEUR + 8)
            sommet = BAS - round(n / plus * (BAS - HAUT))
            if n:
                art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
                traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            traces["barres"].append((rouleau, c["le_rang"], c["le_cote"], j, n, sommet, couleur))
            ecrire(g + 16, sommet - 18, str(n), petit, ENCRE)
        ecrire(gauche, BAS + 10, f"{rouleau}, graine {c['le_rang']}, {c['le_cote']}", moyen, ENCRE)
        dit = les_ecarts_dits(c)
        ecrire(gauche, BAS + 32, dit, petit, GRIS)
        juge = "jugé par les tours publiés" if rouleau == "PHercParis4" and c["le_cote"] == "moins" else "sans vérité"
        ecrire(gauche, BAS + 50, juge, petit, ALERTE if juge == "sans vérité" else ENCRE)
        traces["dessous"].append((rouleau, c["le_rang"], c["le_cote"], dit, juge))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
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

    d = lire(mesure)
    tmp = sortie.parent / ".sonde_388.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["les_deplacees"] = 3
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; non"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "ÉCART MAJORITAIRE : 3 SURFACES LUES DÉPLACÉES SUR PHERCPARIS4 : NON", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    ds = [(n, c) for k, n in (("les_cotes_de_paris4", "PHercParis4"), ("les_cotes_de_0358", "PHerc0358")) for c in d[k]
          if any(e["lecart"] for e in c["les_ecarts"].values())]
    attendu = [(n, c["le_rang"], c["le_cote"], j, c["validees"][j]) for n, c in ds for j in (0, 1)]
    v("★★★★ deux barres par côté décalé, sans alignement puis alignées, PHercParis4 d'abord", [b[:5] for b in traces["barres"]] == attendu,
      str(traces["barres"][:2]))
    v("★★★★ sans alignement en gris, alignées en bleu", all(f == (CLAIR, BLEU)[j] for _, _, _, j, _, _, f in traces["barres"]))
    plus = max(n for *_, n, _, _ in traces["barres"])
    v("★★★★ la hauteur de chaque barre est son nombre, rapporté à la plus haute",
      all(BAS - s == round(n / plus * (BAS - HAUT)) for *_, n, s, _ in traces["barres"]))
    v("★★★★ sous chaque côté, l'écart retenu et ses paires",
      [t[3] for t in traces["dessous"]] == [" ; ".join(f"la {x} {e['lecart']:+d} ({e['porte_par']} paires sur {e['les_paires_meme_feuille']})"
                                                       for x, e in c["les_ecarts"].items() if e["lecart"]) for _, c in ds])
    v("★★★★ seuls les côtés moins de PHercParis4 sont jugés par les tours publiés",
      all((t[4] == "jugé par les tours publiés") == (t[0] == "PHercParis4" and t[2] == "moins") for t in traces["dessous"]))
    p4 = [c for n, c in ds if n == "PHercParis4"]
    v("★★★★ la bande compte les côtés décalés de PHercParis4 et ceux qui sont jugés",
      f"décale une chaîne sur {len(p4)} côté" in la_bande(d)[1]
      and f"dont {sum(c['le_cote'] == 'moins' for c in p4)} que les tours publiés jugent" in la_bande(d)[1])
    dx = json.loads(json.dumps(d))
    for c in dx["les_cotes_de_paris4"]:
        if any(e["lecart"] for e in c["les_ecarts"].values()):
            c["le_cote"] = "moins"
    v("★★★★ un côté moins décalé serait compté jugé", "dont 1 que les tours publiés jugent" in la_bande(dx)[1] if len(p4) == 1 else True)
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
                   / "388_un_ecart_pris_sur_cinq_paires_qui_saccordent_aligne_t_il_sans_deplacer_une_surface_lue.png")
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
