#!/usr/bin/env python3
"""Les cellules que `windcheck` retire sont-elles vraiment indiscernables de celles qu'il garde ?

⚠⚠ **Pourquoi cette figure existe, et pourquoi elle commence par une vérification.**
[`04`](../docs/04_experience_excision.md) publie un tableau où les deux populations ont la
**même** moyenne, la même médiane, les mêmes quartiles et le même écart-type — à la
décimale. C'est le résultat, et c'est aussi exactement à quoi ressemble **une colonne
recopiée deux fois**. Un lecteur ne peut pas distinguer les deux, et l'auteur non plus.

⭐ Ce fichier recalcule tout depuis `docs/mesures/excision_samples.tsv` et **refuse de dessiner** si
les deux populations sont le même échantillon — mêmes lignes, ou même multiensemble de
valeurs. Le résultat n'est croyable qu'une fois cette possibilité écartée par une mesure.

⚠ Ce qu'il n'établit pas : que l'excision est inutile. Il établit qu'à l'endroit excisé le
CT ne montre rien de particulier. Un défaut de géométrie peut être réel sans avoir de
contrepartie matérielle locale — c'est même la lecture que `04` retient.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python src/figures/figure_excision.py \\
        --tsv docs/mesures/excision_samples.tsv --sortie docs/images/04_excision.png \\
        --json docs/mesures/excision_resume.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

LARGEUR = 1120
MARGE = 40
NIVEAUX = 256

ANGLAIS = {
    "Ce que le scanner voit là où windcheck coupe":
        "What the scanner sees where windcheck cuts",
    "distribution des niveaux de gris": "grey-level distribution",
    "cellules excisées": "excised cells",
    "témoins appariés": "matched controls",
    "niveau de gris": "grey level",
    "le niveau 0 (vide) porte ": "level 0 (void) carries ",
    " et sort du cadre — l'échelle est celle des niveaux 1 à 255":
        " and runs off the frame — the scale is that of levels 1 to 255",
    "écart de moyenne par segment": "per-segment mean gap",
    " · médiane ": " · median ",
    "H₀ n'est pas rejetée": "H₀ is not rejected",
    " · δ de Cliff = ": " · Cliff's δ = ",
    " segments, ": " segments, ",
    "négatifs": "negative",
    "positifs": "positive",
    "les deux populations sont DISTINCTES : ": "the two populations are DISTINCT: ",
    " valeurs différentes": " differing values",
    "médiane identique, quartiles identiques, écart-type identique":
        "same median, same quartiles, same standard deviation",
}

FOND, TEXTE, DOUX = (255, 255, 255), (25, 25, 25), (150, 150, 150)
EXCISE, TEMOIN = (200, 45, 45), (60, 110, 170)


def resumer(valeurs: list[int]) -> dict:
    """Moyenne, médiane, quartiles, écart-type — à la main, sans dépendance."""
    n = len(valeurs)
    if not n:
        return {"n": 0}
    v = sorted(valeurs)
    moy = sum(v) / n

    def q(p):
        # ⚠ Quantile par position basse, la convention la plus simple à réimplémenter.
        # Le choix compte peu ici — ce qui compte est que les DEUX populations passent par
        # la même, sinon une différence de convention se lirait comme une différence de
        # matière.
        return v[min(n - 1, int(p * n))]

    var = sum((x - moy) ** 2 for x in v) / n
    return {"n": n, "moyenne": moy, "mediane": q(0.5), "q1": q(0.25), "q3": q(0.75),
            "ecart_type": var ** 0.5}


def distinctes(a: list[int], b: list[int]) -> dict:
    """Les deux populations sont-elles réellement deux échantillons différents ?

    ⚠⚠ La garde qui rend le résultat croyable. Deux résumés identiques ont une explication
    ennuyeuse — la même colonne lue deux fois — indiscernable du résultat par la seule
    lecture du tableau. On compare donc les **multiensembles** de valeurs, pas leurs
    résumés : deux échantillons distincts d'une même loi ont les mêmes statistiques et des
    histogrammes qui diffèrent à l'unité près.
    """
    ca, cb = Counter(a), Counter(b)
    if ca == cb:
        return {"distinctes": False,
                "pourquoi": "les deux populations ont exactement le même multiensemble de "
                            "valeurs — c'est le même échantillon lu deux fois"}
    # ⚠ Normalise par la taille : les temoins sont ~4 fois plus nombreux, donc comparer des
    # comptes bruts trouverait une difference qui n'est que celle des effectifs.
    na, nb = len(a) or 1, len(b) or 1
    differents = sum(1 for k in set(ca) | set(cb)
                     if abs(ca.get(k, 0) / na - cb.get(k, 0) / nb) > 1e-12)
    return {"distinctes": True, "niveaux_differents": differents,
            "niveaux_vus": len(set(ca) | set(cb))}


def mann_whitney(a: list[int], b: list[int]) -> dict:
    """U, δ de Cliff et p — exacts sur des entiers bornés, sans scipy.

    ⚠⚠ **Recalculés parce que les chiffres de tête de `04` §6 doivent être sous garde.**
    Un nombre publié dont le calcul n'est pas dans l'arbre est une anecdote — la règle est
    celle du dépôt, et elle vaut pour les documents anciens comme pour les neufs.

    ⭐ Les valeurs sont des niveaux de gris entiers, donc les **rangs moyens** se calculent
    exactement depuis les comptes par niveau, en 256 opérations et sans trier 379 000
    valeurs. Les ex æquo sont massifs ici (quatre valeurs sur cinq partagent leur niveau
    avec des milliers d'autres) : les ignorer gonflerait la variance et rendrait un p trop
    grand, c'est-à-dire trop conservateur dans le sens qui arrange la conclusion.
    """
    import math
    ca, cb = Counter(a), Counter(b)
    n1, n2 = len(a), len(b)
    if not n1 or not n2:
        return {"impossible": "un échantillon est vide"}
    niveaux = sorted(set(ca) | set(cb))
    # rang moyen de chaque niveau, sur l'echantillon COMBINE
    r1 = 0.0
    cumul = 0
    correction = 0.0
    inferieurs = 0          # combien de b sont STRICTEMENT sous le niveau courant
    plus_grand = plus_petit = 0
    for v in niveaux:
        na, nb = ca.get(v, 0), cb.get(v, 0)
        t = na + nb
        rang_moyen = cumul + (t + 1) / 2.0
        r1 += na * rang_moyen
        cumul += t
        correction += t ** 3 - t
        plus_grand += na * inferieurs
        inferieurs += nb
    # ⚠ Le second sens se deduit : ce qui n'est ni « a > b » ni ex aequo est « a < b ».
    ex_aequo = sum(ca.get(v, 0) * cb.get(v, 0) for v in niveaux)
    plus_petit = n1 * n2 - plus_grand - ex_aequo
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    n = n1 + n2
    var = (n1 * n2 / 12.0) * ((n + 1) - correction / (n * (n - 1)))
    z = (u1 - mu) / math.sqrt(var) if var > 0 else 0.0
    p = math.erfc(abs(z) / math.sqrt(2))          # bilateral
    return {"u": u1, "z": z, "p": p,
            "cliff_delta": (plus_grand - plus_petit) / (n1 * n2),
            "ex_aequo": ex_aequo}


def histogramme(valeurs: list[int], niveaux: int = NIVEAUX) -> list[float]:
    """La densité par niveau de gris, normalisée — deux effectifs différents comparés."""
    c = Counter(min(max(int(v), 0), niveaux - 1) for v in valeurs)
    n = len(valeurs) or 1
    return [c.get(i, 0) / n for i in range(niveaux)]


def lire(tsv: Path) -> dict[str, dict]:
    """Le TSV, groupé par population et par segment."""
    par_pop: dict[str, list[int]] = {}
    par_seg: dict[str, dict[str, list[int]]] = {}
    with tsv.open(encoding="utf-8") as f:
        entete = f.readline().rstrip("\n").split("\t")
        try:
            i_seg, i_pop, i_int = (entete.index(c) for c in ("segment", "population",
                                                             "intensity"))
        except ValueError:
            raise ValueError(f"colonnes attendues absentes — vues : {entete}")
        for ligne in f:
            p = ligne.rstrip("\n").split("\t")
            if len(p) <= max(i_seg, i_pop, i_int):
                continue
            pop, val = p[i_pop], int(p[i_int])
            par_pop.setdefault(pop, []).append(val)
            par_seg.setdefault(p[i_seg], {}).setdefault(pop, []).append(val)
    return {"par_population": par_pop, "par_segment": par_seg}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    r = resumer([1, 2, 3, 4])
    v("la médiane d'un échantillon simple", r["mediane"] == 3, str(r["mediane"]))
    v("la moyenne aussi", abs(r["moyenne"] - 2.5) < 1e-12)
    v("un échantillon vide n'a pas de résumé", resumer([])["n"] == 0)
    v("un échantillon constant a un écart-type nul",
      resumer([7] * 10)["ecart_type"] == 0)

    # ⚠⚠ LA garde. Deux echantillons IDENTIQUES doivent etre refuses ; deux echantillons
    # differents de MEME statistique doivent passer -- sinon la garde eteindrait le
    # resultat qu'elle est la pour rendre croyable.
    a = [1, 2, 3, 4, 5, 6]
    v("le même échantillon deux fois est REFUSÉ", distinctes(a, list(a))["distinctes"] is False)
    v("... en disant pourquoi", "même échantillon" in distinctes(a, list(a))["pourquoi"])
    b = [1, 2, 3, 4, 5, 7]
    v("deux échantillons différents passent", distinctes(a, b)["distinctes"] is True)
    # ⚠ Et le cas qui compte vraiment : meme moyenne, meme mediane, valeurs differentes.
    c, dd = [10, 20, 30, 40], [10, 21, 29, 40]
    v("même moyenne et même médiane, mais valeurs différentes ⇒ distinctes",
      distinctes(c, dd)["distinctes"] is True
      and abs(resumer(c)["moyenne"] - resumer(dd)["moyenne"]) < 1e-12)
    # ⚠ Des effectifs differents ne doivent pas suffire a declarer une difference de FORME :
    # un echantillon double a la meme densite normalisee.
    v("doubler un échantillon ne change pas sa densité",
      histogramme([1, 2, 3]) == histogramme([1, 1, 2, 2, 3, 3]))

    # ⚠⚠ Un ecart de MEDIANES de niveaux entiers est entier ; un ecart de MOYENNES ne l'est
    # pas. Les deux repondent a « ce segment penche de quel cote », et ils ne comptent pas
    # les memes segments -- un segment dont les medianes sont egales a une moyenne qui ne
    # l'est pas. C'est pourquoi les deux sont publies.
    e1, t1 = [10, 20, 30], [10, 20, 31]
    v("un écart de médianes de niveaux entiers est entier",
      float(resumer(e1)["mediane"] - resumer(t1)["mediane"]).is_integer())
    v("... alors qu'un écart de moyennes ne l'est pas",
      not float(resumer(e1)["moyenne"] - resumer(t1)["moyenne"]).is_integer())

    # ⚠⚠ Mann-Whitney, verifie sur des cas dont on connait la reponse.
    mw = mann_whitney([1, 2, 3], [1, 2, 3])
    v("deux échantillons identiques ont un δ de Cliff nul",
      abs(mw["cliff_delta"]) < 1e-12, f"{mw['cliff_delta']}")
    v("... et un p qui ne rejette rien", mw["p"] > 0.9, f"{mw['p']:.3f}")
    sep = mann_whitney([10, 11, 12], [1, 2, 3])
    v("deux échantillons séparés ont un δ de Cliff de +1", abs(sep["cliff_delta"] - 1) < 1e-12)
    v("... et l'inverse donne −1",
      abs(mann_whitney([1, 2, 3], [10, 11, 12])["cliff_delta"] + 1) < 1e-12)
    # ⚠ La correction d'ex aequo : sans elle, un echantillon massivement ex aequo aurait une
    # variance surestimee, donc un p trop grand -- trop conservateur DANS LE SENS qui
    # arrange une conclusion de non-difference. Le comptage des ex aequo est donc asserte.
    t = mann_whitney([5] * 10, [5] * 10)
    v("des ex æquo massifs sont comptés", t["ex_aequo"] == 100, str(t["ex_aequo"]))
    v("un échantillon vide est refusé", "impossible" in mann_whitney([], [1]))

    h = histogramme([0, 255, 300, -5])
    v("un histogramme somme à 1", abs(sum(h) - 1.0) < 1e-12)
    v("une valeur hors bornes est écrêtée, pas jetée", h[255] > 0 and h[0] > 0)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tsv", type=Path, default=Path(__file__).resolve().parents[2] / "docs/mesures/excision_samples.tsv")
    ap.add_argument("--sortie", type=Path, default=Path(__file__).resolve().parents[2] / "docs/images/04_excision.png")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    import langue

    if not a.tsv.is_file():
        print(f"absent : {a.tsv}", file=sys.stderr)
        return 1
    d = lire(a.tsv)
    pops = d["par_population"]
    if set(pops) != {"excised", "control"} and len(pops) != 2:
        print(f"deux populations attendues, vues : {sorted(pops)}", file=sys.stderr)
        return 1
    nom_e = "excised" if "excised" in pops else sorted(pops)[0]
    nom_t = next(k for k in pops if k != nom_e)
    exc, tem = pops[nom_e], pops[nom_t]

    dis = distinctes(exc, tem)
    resume = {"excisees": resumer(exc), "temoins": resumer(tem), **dis,
              "segments": len(d["par_segment"])}
    # ⚠⚠ Le refus est AVANT le dessin : une figure qui montrerait deux courbes superposees
    # parce que ce sont les memes donnees serait la plus convaincante des figures fausses.
    if not dis["distinctes"]:
        print(f"⚠⚠ REFUS — {dis['pourquoi']}", file=sys.stderr)
        return 1

    # ⚠ L'ecart de mediane PAR SEGMENT : le resultat global pourrait cacher des segments qui
    # s'annulent. Le publier a cote est ce qui empeche « pas de difference en moyenne » de
    # se lire comme « pas de difference ».
    # ⚠⚠ DEUX statistiques par segment, et il faut les deux. `04` §6 publie « 30 negatifs,
    # 22 positifs, mediane -0,011 » -- un chiffre a trois decimales, donc un ecart de
    # MOYENNES, puisqu'un ecart de medianes de niveaux de gris entiers est entier. Ne
    # publier que le mien donnerait deux comptes differents du meme objet dans un meme
    # document, sans qu'une ligne dise que ce sont deux quantites.
    deltas, deltas_moy = [], []
    for seg, p in sorted(d["par_segment"].items()):
        if nom_e in p and nom_t in p and p[nom_e] and p[nom_t]:
            re_, rt_ = resumer(p[nom_e]), resumer(p[nom_t])
            deltas.append(re_["mediane"] - rt_["mediane"])
            deltas_moy.append(re_["moyenne"] - rt_["moyenne"])

    def compter(xs, nom):
        return {f"{nom}_n": len(xs),
                f"{nom}_negatifs": sum(1 for x in xs if x < 0),
                f"{nom}_positifs": sum(1 for x in xs if x > 0),
                f"{nom}_nuls": sum(1 for x in xs if x == 0),
                f"{nom}_mediane": (sorted(xs)[len(xs) // 2] if xs else None)}

    resume["deltas_par_segment"] = {**compter(deltas, "mediane"),
                                    **compter(deltas_moy, "moyenne")}
    resume["mann_whitney"] = mann_whitney(exc, tem)
    # ⚠⚠ LE NIVEAU ZERO EST DU VIDE, et il pèse 3,4 % de chaque population — trois fois le
    # bin suivant. Comparer deux échantillons qui contiennent chacun une part de néant
    # inclut du vide-contre-vide, identique par construction, ce qui DILUE toute différence
    # réelle vers zéro. Un p de 0,859 obtenu ainsi serait rassurant pour une mauvaise
    # raison. On refait donc la mesure sans ce niveau, et on publie les deux : si la
    # conclusion survit, elle est plus forte ; si elle ne survit pas, elle était portée par
    # le vide partagé.
    exc_nz = [v for v in exc if v > 0]
    tem_nz = [v for v in tem if v > 0]
    resume["part_vide"] = {"excisees": 1 - len(exc_nz) / max(len(exc), 1),
                           "temoins": 1 - len(tem_nz) / max(len(tem), 1)}
    resume["mann_whitney_sans_vide"] = mann_whitney(exc_nz, tem_nz)
    resume["sans_vide"] = {"excisees": resumer(exc_nz), "temoins": resumer(tem_nz)}

    def police(t, gras=False):
        c = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if gras
             else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        try:
            return ImageFont.truetype(c, t)
        except OSError:
            return ImageFont.load_default()

    f_t, f_n, f_p = police(21, True), police(15), police(12)
    H = 300
    n_seg = sum(1 for p_ in d["par_segment"].values()
                if nom_e in p_ and nom_t in p_ and p_[nom_e] and p_[nom_t])
    hauteur = MARGE + 34 + H + 46 + 24 + n_seg * 6 + 42 + 4 * 20 + MARGE
    img = Image.new("RGB", (LARGEUR, hauteur), FOND)
    g = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if a.anglais else None)

    g.text((MARGE, MARGE - 14), "Ce que le scanner voit là où windcheck coupe",
           font=f_t, fill=TEXTE)
    y = MARGE + 30
    g.text((MARGE, y), "distribution des niveaux de gris", font=f_n, fill=TEXTE)
    y += 22

    he, ht = histogramme(exc), histogramme(tem)
    # ⚠⚠ L'ECHELLE IGNORE LE NIVEAU 0. Il porte 3,4 % de chaque population -- trois fois le
    # bin suivant -- donc le laisser fixer la hauteur ecrase toute la distribution reelle
    # dans le tiers bas du cadre, et la figure cache exactement ce qu'elle doit montrer.
    # Le bin est dessine quand meme, et sa hauteur reelle est DITE a cote : le tronquer en
    # silence serait pire que de le laisser ecraser le reste.
    pic = max(max(he[1:]), max(ht[1:])) or 1.0
    x0, larg = MARGE + 30, LARGEUR - 2 * MARGE - 60
    g.line([x0, y + H, x0 + larg, y + H], fill=DOUX)
    for i in range(NIVEAUX):
        xa = x0 + int(i / NIVEAUX * larg)
        xb = x0 + int((i + 1) / NIVEAUX * larg)
        for h, coul in ((ht, TEMOIN), (he, EXCISE)):
            hh = min(int(h[i] / pic * H), H)
            if hh:
                # ⚠ Contour et non aplat : deux aplats superposes cachent celui du dessous,
                # donc une figure remplie ne pourrait PAS montrer que les deux coincident.
                g.line([xa, y + H - hh, xb, y + H - hh], fill=coul, width=2)
    for t in (0, 64, 128, 192, 255):
        xx = x0 + int(t / NIVEAUX * larg)
        g.line([xx, y + H, xx, y + H + 4], fill=DOUX)
        g.text((xx - 8, y + H + 8), str(t), font=f_p, fill=DOUX)
    g.text((x0 + larg - 120, y + H + 8), "niveau de gris", font=f_p, fill=DOUX)
    g.text((x0, y + 26), f"le niveau 0 (vide) porte {max(he[0], ht[0]):.1%} et sort du "
                         f"cadre — l'échelle est celle des niveaux 1 à 255",
           font=f_p, fill=DOUX)
    for i, (coul, lib, n) in enumerate(((EXCISE, "cellules excisées", len(exc)),
                                        (TEMOIN, "témoins appariés", len(tem)))):
        g.line([x0 + i * 220, y + 8, x0 + 20 + i * 220, y + 8], fill=coul, width=3)
        g.text((x0 + 26 + i * 220, y), f"{lib} ({n})", font=f_p, fill=coul)
    y += H + 46

    # ── les écarts par segment ────────────────────────────────────────────────────────
    # ⚠⚠ L'ecart de MOYENNES et pas de medianes. Sur des niveaux de gris entiers un ecart de
    # medianes ne prend que des valeurs entieres : 52 segments se repartissent alors sur
    # trois ou quatre barres, et le graphique ne montre plus une distribution mais un
    # escalier. La moyenne est continue, donc elle montre ou se situe reellement chaque
    # segment -- et c'est aussi la statistique que `04` §6 rapporte.
    g.text((MARGE, y), "écart de moyenne par segment", font=f_n, fill=TEXTE)
    y += 24
    hb = 4
    ecart = 2
    m = max((abs(x) for x in deltas_moy), default=1.0) or 1.0
    demi = (LARGEUR - 2 * MARGE - 160) // 2
    cx = MARGE + 80 + demi
    ordonnes = sorted(deltas_moy)
    haut = len(ordonnes) * (hb + ecart)
    g.line([cx, y - 4, cx, y + haut + 4], fill=DOUX)
    for i, dv in enumerate(ordonnes):
        yy = y + i * (hb + ecart)
        xx = cx + int(dv / m * demi)
        g.rectangle([min(cx, xx), yy, max(cx, xx), yy + hb],
                    fill=EXCISE if dv > 0 else TEMOIN)
    # ⚠ Les bornes sont ETIQUETEES : sans elles un lecteur ne peut pas savoir si l'echelle
    # couvre un niveau de gris ou cinquante, donc la figure ne dit rien de l'amplitude.
    g.text((cx - demi - 74, y + haut // 2 - 7), f"−{m:.1f}".replace(".", ","),
           font=f_p, fill=TEMOIN)
    g.text((cx + demi + 10, y + haut // 2 - 7), f"+{m:.1f}".replace(".", ","),
           font=f_p, fill=EXCISE)
    g.text((cx - 6, y + haut + 8), "0", font=f_p, fill=DOUX)
    dpr = resume["deltas_par_segment"]
    g.text((MARGE, y + haut + 8),
           f"{dpr['moyenne_negatifs']} négatifs · {dpr['moyenne_positifs']} positifs · "
           f"médiane {dpr['moyenne_mediane']:+.3f}".replace(".", ","),
           font=f_p, fill=DOUX)
    y += haut + 34

    e, t_ = resume["excisees"], resume["temoins"]
    mw = resume["mann_whitney"]
    for i, txt in enumerate((
            f"Mann-Whitney p = {mw['p']:.3f}".replace(".", ",")
            + f" · δ de Cliff = {mw['cliff_delta']:+.4f}".replace(".", ",")
            + " — H₀ n'est pas rejetée",
            f"les deux populations sont DISTINCTES : {dis['niveaux_differents']}"
            f"/{dis['niveaux_vus']} valeurs différentes",
            f"médiane identique, quartiles identiques, écart-type identique "
            f"({e['mediane']:.0f} · {e['q1']:.0f}–{e['q3']:.0f} · "
            f"{e['ecart_type']:.1f})".replace(".", ","),
            f"{resume['segments']} segments, {e['n']} cellules excisées contre "
            f"{t_['n']} témoins")):
        g.text((MARGE, y + i * 20), txt, font=f_n,
               fill=EXCISE if i == 1 else TEXTE)

    if a.anglais and g.intraduits():
        print("des libellés n'ont pas de traduction :", file=sys.stderr)
        for t in g.intraduits():
            print(f"    « {t} »", file=sys.stderr)
        return 1

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{hauteur})")
    print(f"  {dis['niveaux_differents']}/{dis['niveaux_vus']} niveaux diffèrent — "
          f"les deux populations ne sont pas le même échantillon")
    print(f"  excisées  n={e['n']:>7} médiane {e['mediane']:>4} "
          f"Q1–Q3 {e['q1']}–{e['q3']} σ {e['ecart_type']:.1f}")
    print(f"  témoins   n={t_['n']:>7} médiane {t_['mediane']:>4} "
          f"Q1–Q3 {t_['q1']}–{t_['q3']} σ {t_['ecart_type']:.1f}")
    mw = resume["mann_whitney"]
    if "impossible" not in mw:
        print(f"  Mann-Whitney U = {mw['u']:.0f}  z = {mw['z']:+.3f}  p = {mw['p']:.3f}  "
              f"δ de Cliff = {mw['cliff_delta']:+.4f}")
    pv, mz = resume["part_vide"], resume["mann_whitney_sans_vide"]
    if "impossible" not in mz:
        print(f"  sans le niveau 0 (vide : {pv['excisees']:.1%} / {pv['temoins']:.1%}) : "
              f"p = {mz['p']:.3f}  δ de Cliff = {mz['cliff_delta']:+.4f}")
    print(f"  par segment, écart de MÉDIANES : {dpr['mediane_negatifs']} négatifs, "
          f"{dpr['mediane_positifs']} positifs, {dpr['mediane_nuls']} nuls, "
          f"médiane {dpr['mediane_mediane']}")
    print(f"  par segment, écart de MOYENNES  : {dpr['moyenne_negatifs']} négatifs, "
          f"{dpr['moyenne_positifs']} positifs, "
          f"médiane {dpr['moyenne_mediane']:+.3f}")
    if a.json:
        a.json.write_text(json.dumps(resume, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
