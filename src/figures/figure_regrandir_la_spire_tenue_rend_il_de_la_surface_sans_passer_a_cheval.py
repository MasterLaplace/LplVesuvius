"""Sur PHercParis4, graines 4 à 8 : la surface gardée, la part des sauts jugés qui sont justes, et la part des sauts justes à cheval, pour la chaîne mixte et pour la chaîne qui regrandit sa spire tenue.

⚠⚠ **Ce que cette figure doit rendre évident.** Trois groupes de barres : la surface, en mailles, la part juste, la part à cheval ; dans
chaque groupe, la chaîne mixte en bleu et la chaîne qui regrandit en orange. Sous chaque barre, le compte qui la fait.

  uv run python src/figures/figure_regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval.py \\
      --sortie docs/images/358_regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval.png

⚠ Tout vient de la mesure de `358`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 590
LA_BANDE = 470
HAUT, BAS = 150, 390
LARGEUR = 80
LES_CHAINES = (("la_chaine_mixte", "chaîne mixte", BLEU), ("la_chaine_qui_regrandit", "chaîne qui regrandit sa spire tenue", ORANGE))
LES_GROUPES = (("s", "la_surface", None, "mailles gardées, en médiane", 230),
               ("j", "les_justes", "les_juges", "sauts jugés qui sont justes", 550),
               ("c", "les_justes_a_cheval", "les_justes", "sauts justes à cheval", 870))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def les_juges(d: dict, cle: str, graines=(4, 5, 6, 7, 8)) -> list[dict]:
    return [s for c in d["les_cotes"][cle] if c["le_rang"] in graines for s in c["les_sauts"] if s["la_justesse"] != "non jugé"]


def la_bande(d: dict) -> tuple[str, ...]:
    un, deux, trois = (d["le_verdict"]["lissue"].split(" ; ") + ["", ""])[:3]
    juges = les_juges(d, "la_chaine_qui_regrandit")
    regrandis = [s for s in juges if s["depuis"] == "la croissance"]
    m13 = les_juges(d, "la_chaine_mixte", (1, 2, 3))
    r13 = les_juges(d, "la_chaine_qui_regrandit", (1, 2, 3))
    quatre = (f"rapporté à côté, qui ne décide rien : des {len(juges)} sauts jugés, {len(regrandis)} gardent la surface regrandie, dont "
              f"{sum(s['a_cheval'] for s in regrandis)} à cheval ; graines 1 à 3 : {sum(s['la_justesse'] == 'juste' for s in r13)} juste "
              f"sur {len(r13)}, contre {sum(s['la_justesse'] == 'juste' for s in m13)} sur {len(m13)}")
    cinq = "⚠ ce qui n'est PAS établi : si une autre marge, ou un critère qui juge la seule partie regrandie, garderait la surface sans le cheval."
    return f"LE VERDICT DÉCLARÉ : {un} ;", f"{deux} ;" if trois else deux, trois, quatre, cinq


def la_part(d: dict, cle: str, haut: str, bas: str | None) -> tuple[float, str]:
    b = d["les_bilans"][cle]
    if bas is None:
        plus = max(d["les_bilans"][k]["la_surface"] for k, _, _ in LES_CHAINES)
        return b[haut] / plus, f"{b[haut]:g} mailles".replace(".", ",")
    return (b[haut] / b[bas] if b[bas] else 0.0), f"{b[haut]} sur {b[bas]}"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"barres": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "sur PHercParis4, graines 4 à 8 ; la surface est rapportée à la plus grande des deux, les autres barres sont des parts",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    ecrire(x0 + 12, y0 + 8, "les sauts jugés par les tours publiés", moyen, ENCRE)
    lx = x0 + 560
    for i, (_, nom, couleur) in enumerate(LES_CHAINES):
        ly = y0 + 10 + i * 20
        art.rectangle([lx, ly + 2, lx + 12, ly + 14], fill=couleur)
        traces["rectangles"].append((lx, lx + 12, ly + 2, ly + 14))
        ecrire(lx + 20, ly, nom, petit, ENCRE)
    art.line([x0 + 40, BAS, x1 - 40, BAS], fill=GRIS, width=1)
    for groupe, haut, bas, titre, centre in LES_GROUPES:
        for i, (cle, _, couleur) in enumerate(LES_CHAINES):
            part, compte = la_part(d, cle, haut, bas)
            gauche = centre - LARGEUR - 8 if i == 0 else centre + 8
            sommet = BAS - round(part * (BAS - HAUT))
            art.rectangle([gauche, sommet, gauche + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((groupe, cle, part, compte, sommet, couleur))
            traces["rectangles"].append((gauche, gauche + LARGEUR, sommet, BAS))
            if bas is not None:
                ecrire(gauche + 18, sommet - 18, f"{round(100 * part)} %", petit, ENCRE)
            ecrire(gauche + 6, BAS + 6, compte, petit, ENCRE)
        ecrire(centre - 95, BAS + 26, titre, moyen, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    for k, ligne in enumerate(la_bande(d)):
        if k < 4:
            ecrire(50, LA_BANDE + 8 + 16 * k, ligne, petit, ENCRE)
        else:
            ecrire(50, LA_BANDE + 8 + 16 * k + 6, ligne, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_358.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"]["lissue"] = "x ; y ; non, elle ne rend pas de surface"
    v("★★★ le titre LIT la mesure", le_titre(autre) == "NON, ELLE NE REND PAS DE SURFACE", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    v("★★★★ la bande tient dans la toile", LA_BANDE + 8 + 16 * 4 + 6 + 18 < H_)
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    for cle in ("la_chaine_mixte", "la_chaine_qui_regrandit"):
        juges = les_juges(d, cle)
        justes = [s for s in juges if s["la_justesse"] == "juste"]
        b = d["les_bilans"][cle]
        v(f"★★★★ le bilan de {cle} se recompte sur ses sauts",
          (b["les_juges"], b["les_justes"], b["les_justes_a_cheval"]) == (len(juges), len(justes), sum(s["a_cheval"] for s in justes)))
    v("★★★★ la chaîne mixte est en bleu, la chaîne qui regrandit en orange",
      all(f == {"la_chaine_mixte": BLEU, "la_chaine_qui_regrandit": ORANGE}[k] for _, k, _, _, _, f in traces["barres"]))
    comptes = {k: [c for g, k2, _, c, _, _ in traces["barres"] if k2 == k] for k, _, _ in LES_CHAINES}
    attendu = {k: [f"{d['les_bilans'][k]['la_surface']:g} mailles".replace(".", ","),
                   f"{d['les_bilans'][k]['les_justes']} sur {d['les_bilans'][k]['les_juges']}",
                   f"{d['les_bilans'][k]['les_justes_a_cheval']} sur {d['les_bilans'][k]['les_justes']}"] for k in comptes}
    v("★★★★ la surface, puis les justes sur les jugés, puis les justes à cheval sur les justes, au compte de chaque chaîne",
      comptes == attendu, str(comptes))
    autre = json.loads(json.dumps(d))
    b = autre["les_bilans"]["la_chaine_qui_regrandit"]
    b["les_juges"] = b["les_justes"] + 11
    tmp2 = tmp.with_name(".sonde_358_autre.png")
    _, _, _, t2 = dessiner(autre, tmp2)
    tmp2.unlink(missing_ok=True)
    c2 =[c for _, k2, _, c, _, _ in t2["barres"] if k2 == "la_chaine_qui_regrandit"]
    v("★★★★ la part à cheval se rapporte aux justes, pas aux jugés, même quand les deux diffèrent",
      c2[1:] == [f"{b['les_justes']} sur {b['les_juges']}", f"{b['les_justes_a_cheval']} sur {b['les_justes']}"], str(c2))
    plus = max(d["les_bilans"][k]["la_surface"] for k in comptes)
    v("★★★★ la plus grande surface fait une barre pleine, l'autre sa part",
      all(BAS - s == round(d["les_bilans"][k]["la_surface"] / plus * (BAS - HAUT)) for g, k, _, _, s, _ in traces["barres"] if g == "s"))
    v("★★★★ la hauteur de chaque part est sa part",
      all(BAS - s == round(p * (BAS - HAUT)) for g, _, p, _, s, _ in traces["barres"] if g != "s"))
    textes = {t for _, _, t, _ in poses}
    v("★★★★ sous chaque barre, le compte qui la fait", all(c in textes for _, _, _, c, _, _ in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    juges = les_juges(d, "la_chaine_qui_regrandit")
    reg = [s for s in juges if s["depuis"] == "la croissance"]
    v("★★★★ la bande rapporte à côté les surfaces regrandies gardées et leurs sauts à cheval, recomptés",
      f"{len(reg)} gardent la surface regrandie, dont {sum(s['a_cheval'] for s in reg)} à cheval" in " ".join(la_bande(d)))
    v("★★★★ la bande porte le verdict entier",
      " ".join(la_bande(d)[:3]).replace(" ;", "").strip() == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}".replace(" ;", ""))
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t for t in textes))
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
                   / "358_regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval.png")
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
