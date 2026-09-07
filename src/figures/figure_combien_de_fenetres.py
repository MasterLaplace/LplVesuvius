#!/usr/bin/env python3
"""Combien de fenetres faut-il pour que la carte des treize DECIDE quelque chose ?

⚠⚠⚠ CETTE FIGURE PORTE UNE QUESTION DE BUDGET, PAS UN RESULTAT SUR LES ROULEAUX. `33` a montre
que la carte des treize ne separe RIEN — 0 rouleau sur 13 du temoin, 0 paire sur 78 — et `31`
inscrit « 50 fenetres minimum » au calendrier. Mais 50 est le chiffre pour separer un rouleau du
TEMOIN, et ce n'est pas la decision dont le prix a besoin : il faut choisir SUR LEQUEL des treize
depenser six mois, donc separer les rouleaux ENTRE EUX.

⚠⚠ Le panneau A dit ce qu'un budget ACHETE, et le panneau B dit que la paire qui decide est la
plus chere de toutes — parce que les deux mieux classes sont ceux dont les parts sont les plus
proches. Une campagne lancee sans ces deux chiffres est une campagne dont on ne sait pas si elle
peut conclure.

Usage :
    uv run python src/figures/figure_combien_de_fenetres.py --verifier
    uv run python src/figures/figure_combien_de_fenetres.py \\
        --sortie docs/images/75_combien_de_fenetres.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "combien_de_fenetres.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
PALE = (243, 231, 227)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    d = m["paire_decisive"]
    aujourdhui = m["fenetres_actuelles_total"]
    n50 = m["paires_separees_par_budget"].get("50", {})
    return [
        f"la carte des treize rouleaux repose aujourd'hui sur {aujourdhui} fenetres au total, "
        f"soit {min(m['fenetres_actuelles'].values())} a "
        f"{max(m['fenetres_actuelles'].values())} par rouleau. ⚠⚠ et elle ne separe RIEN : "
        "aucun rouleau du temoin apres correction, aucune des 78 paires. ce fichier ne mesure "
        "donc rien sur les rouleaux — il repond a la question qui PRECEDE la campagne : a quel "
        "effectif la question deviendrait decidable.",
        f"⚠⚠⚠ PANNEAU A : ce qu'un budget achete. a {50} fenetres par rouleau — le chiffre "
        f"inscrit au calendrier — on separe {n50.get('nominal', 0)} paire(s) sur "
        f"{m['paires']} au seuil nominal, et {n50.get('holm', 0)} apres correction de Holm. la "
        "correction n'est pas un raffinement optionnel : 78 comparaisons au seuil de cinq pour "
        "cent produisent des « significatifs » par pur hasard, et ce depot a deja eu a retirer "
        "un classement pour cette raison exacte.",
        f"⚠⚠⚠ PANNEAU B : LA PAIRE QUI DECIDE est la plus CHERE de toutes, et c'est structurel. "
        f"choisir ou depenser six mois demande de separer les DEUX MIEUX CLASSES — "
        f"{d['a']} a {d['part_a']:.1%} et {d['b']} a {d['part_b']:.1%} — donc les deux dont les "
        f"parts sont les plus PROCHES ({d['ecart']:.1%} d'ecart). a 50 fenetres sa puissance est "
        f"de {d['puissance_a_50']:.1%}.",
        (f"⚠⚠⚠ et elle n'est PAS atteignable dans l'echelle balayee : au seuil corrige sa "
         f"puissance plafonne a {d['holm']['puissance']:.1%} meme a "
         f"{m['echelle'][-1]} fenetres par rouleau. il en faudrait AU MOINS "
         f"{m['borne_basse_decisive']} par rouleau — {m['borne_basse_totale']} au total, soit "
         f"{m['facteur_sur_lexistant']} FOIS le budget actuel — et ce chiffre est une borne "
         "BASSE, parce que l'approximation qui le donne surestime la puissance donc sous-estime "
         "l'effectif. CHOISIR LE ROULEAU PAR SA PART COMPRIMEE N'EST PAS UNE PROCEDURE DE "
         "DECISION DISPONIBLE A CE PRIX."
         if not m["la_paire_decisive_est_atteignable"]
         else f"⚠ elle est atteignable : {d['holm']['fenetres']} fenetres par rouleau, soit "
         f"{m['cout_total_fenetres']} au total, contre {aujourdhui} aujourd'hui — un facteur "
         f"{m['cout_total_fenetres'] / max(aujourdhui, 1):.0f}."),
        f"⚠⚠ ET LE CHIFFRE DU CALENDRIER NE SUFFIT MEME PAS A LA QUESTION FACILE : separer un "
        f"rouleau du TEMOIN demande {m['au_temoin'][0]['holm']['fenetres'] or '> ' + str(m['echelle'][-1])} "
        f"fenetres apres correction pour le mieux classe, la ou le calendrier en inscrit 50. "
        "les deux questions sont donc sous-financees, et celle qui decide l'est de deux ordres "
        "de grandeur.",
        "⚠⚠ et la comparaison au TEMOIN est beaucoup moins chere, ce qui est exactement le "
        "piege : repondre a la question facile — « ce rouleau a-t-il plus de zones comprimees "
        "que le temoin » — ne repond PAS a celle qui decide du rouleau. le calendrier inscrit le "
        "chiffre de la question facile ; le panneau B chiffre l'autre.",
        "⚠ ce que ca ne dit pas : que le prix soit hors de portee. ca dit que le CRITERE DE "
        "CHOIX propose n'est pas mesurable a ce prix, donc qu'il faut soit un autre critere, "
        "soit accepter de choisir le rouleau autrement — et le dire est moins couteux que six "
        "mois passes sur le mauvais.",
    ]


def panneau_budget(art, x0, y0, pw, ph, m, petit) -> None:
    """Ce qu'un budget par rouleau achete, en paires separees."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "paires separees sur "
             f"{m['paires']} · plein : seuil nominal · creux : apres Holm",
             fill=DISCRET, font=petit)
    budgets = sorted(int(k) for k in m["paires_separees_par_budget"])
    gauche, droite = x0 + 46, x0 + pw - 26
    base, sommet = y0 + ph - 40, y0 + 36
    haut = max(m["paires"], 1)

    def px(i: int) -> float:
        return gauche + (droite - gauche) * i / max(1, len(budgets) - 1)

    def py(v: float) -> float:
        return base - (base - sommet) * v / haut

    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (0, 20, 40, 60, 78):
        if g <= haut:
            art.text((gauche - 40, py(g) - 6), f"{g:>4}", fill=DISCRET, font=petit)
    for cle, coul, plein in (("nominal", BLEU, True), ("holm", ROUGE, False)):
        pts = [(px(i), py(m["paires_separees_par_budget"][str(n)][cle]))
               for i, n in enumerate(budgets)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            art.line([ax, ay, bx, by], fill=coul, width=2)
        for cx, cy in pts:
            if plein:
                art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=coul)
            else:
                art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=coul, width=2)
        art.text((droite + 4, pts[-1][1] - 6), cle, fill=coul, font=petit)
    for i, n in enumerate(budgets):
        art.text((px(i) - 12, base + 8), str(n), fill=DISCRET, font=petit)
    # ⚠ Le chiffre du calendrier est marqué SUR l'axe : c'est lui que la figure conteste, donc
    # il doit être visible sans le chercher dans la prose.
    if 50 in budgets:
        j = budgets.index(50)
        art.line([px(j), sommet, px(j), base], fill=(220, 200, 200))
        art.text((px(j) - 30, sommet - 14), "le calendrier", fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 18), "abscisse : fenetres par rouleau",
             fill=DISCRET, font=petit)


def panneau_paires(art, x0, y0, pw, ph, m, petit) -> None:
    """Chaque paire par son ecart, et si elle est atteignable."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "chaque paire par l'ECART de leurs parts",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 19), "vert : separable apres Holm dans l'echelle · gris : non",
             fill=DISCRET, font=petit)
    paires = sorted(m["paires_detail"], key=lambda p: p["ecart"])
    gauche, droite = x0 + 46, x0 + pw - 30
    base, sommet = y0 + ph - 40, y0 + 42
    haut = max(p["ecart"] for p in paires) * 1.1

    def py(v: float) -> float:
        return base - (base - sommet) * v / haut

    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (0.05, 0.10, 0.15, 0.20):
        if g < haut:
            art.text((gauche - 42, py(g) - 6), f"{g:>4.0%}", fill=DISCRET, font=petit)
    lg = (droite - gauche) / max(1, len(paires))
    d = m["paire_decisive"]
    for i, p in enumerate(paires):
        x = gauche + i * lg
        ok = p["holm"]["fenetres"] is not None
        coul = VERT if ok else (190, 190, 190)
        art.rectangle([x, py(p["ecart"]), x + max(1.0, lg - 1), base], fill=coul)
        if p["a"] == d["a"] and p["b"] == d["b"]:
            art.rectangle([x - 2, py(p["ecart"]) - 4, x + lg + 1, base], outline=ROUGE, width=2)
            art.text((x + 6, py(p["ecart"]) - 20), "la paire qui DECIDE", fill=ROUGE,
                     font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             f"{sum(1 for p in paires if p['holm']['fenetres'] is not None)} paires sur "
             f"{len(paires)} separables · abscisse : les paires, triees par ecart croissant",
             fill=DISCRET, font=petit)


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 268
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "Combien de fenetres pour que la carte des treize DECIDE ?",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['rouleaux']} rouleaux · {m['paires']} paires · cible {m['cible']:.0%} de "
             f"puissance · seuil corrige {m['alpha_holm']:.1e}",
             fill=DISCRET, font=moyen)
    titres = ("A · ce qu'un budget par rouleau achete",
              "B · les 78 paires, et celle qui decide")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    panneau_budget(art, marge, 104, pw, ph, m, petit)
    panneau_paires(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"paires": len(m["paires_detail"]), "titres": titres, "panneau": pw,
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LA PAIRE QUI DÉCIDE EST CELLE DES DEUX MIEUX CLASSÉS, jamais la plus facile : c'est
    # elle qui dit où dépenser six mois, et prendre une autre répondrait à une question que
    # personne ne pose.
    v("la paire décisive est celle des deux parts les plus BASSES",
      all(m["paire_decisive"]["part_a"] <= p["part_a"] for p in m["paires_detail"])
      and m["paire_decisive"]["part_a"] <= m["paire_decisive"]["part_b"],
      f"{m['paire_decisive']['a']} contre {m['paire_decisive']['b']}")
    # ⚠⚠ ET ELLE EST PARMI LES PLUS CHÈRES, ce que la figure affirme : son écart doit être parmi
    # les plus petits. Si ce n'était pas vrai, la prose serait fausse.
    ecarts = sorted(p["ecart"] for p in m["paires_detail"])
    v("... et son écart est parmi le quart le plus petit des 78",
      m["paire_decisive"]["ecart"] <= ecarts[len(ecarts) // 4],
      f"{m['paire_decisive']['ecart']} contre un quartile à {ecarts[len(ecarts) // 4]}")
    # ⚠⚠ LE SEUIL CORRIGÉ N'ACHÈTE JAMAIS PLUS QUE LE NOMINAL, et un budget plus grand jamais
    # moins de paires : deux monotonies qui, si elles cassaient, diraient que le compte ne
    # compte pas ce qu'il annonce.
    b = sorted(int(k) for k in m["paires_separees_par_budget"])
    v("un budget plus grand n'achète jamais moins de paires",
      all(m["paires_separees_par_budget"][str(x)]["nominal"]
          <= m["paires_separees_par_budget"][str(y)]["nominal"] for x, y in zip(b, b[1:])))
    v("... et le seuil corrigé n'achète jamais plus que le nominal",
      all(x["holm"] <= x["nominal"] for x in m["paires_separees_par_budget"].values()),
      str({k: (x["nominal"], x["holm"])
           for k, x in m["paires_separees_par_budget"].items()}))
    # ⚠ LE CHIFFRE DU CALENDRIER EST DANS L'ÉCHELLE : la figure le conteste, donc il doit y être.
    v("le chiffre du calendrier (50 fenêtres) est dans l'échelle balayée",
      "50" in m["paires_separees_par_budget"])

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("les 78 paires sont dessinées", r["paires"] == m["paires"], str(r["paires"]))
        debord = [(t[:36], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        _, _, pt_ = police(17, 13, 11)
        trop = [(t, pt_.getbbox(t)[2]) for t in r["titres"] if pt_.getbbox(t)[2] >= r["panneau"]]
        v("chaque titre de panneau tient dans son panneau", not trop, str(trop))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_combien_de_fenetres.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
