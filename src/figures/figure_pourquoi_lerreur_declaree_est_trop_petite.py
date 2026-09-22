"""Pourquoi l'erreur déclarée est trop petite : les décalages, les queues, l'étalon, le remède.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, LES DÉCALAGES : pour chaque paire,
l'autocorrélation la plus forte des carrés contre ce que le rebrassage de sa PROPRE série donne —
aucune ne dépasse. En haut à droite, LES QUEUES, et c'est le panneau qui conclut : le facteur
`(κ+2)/2` avec son intervalle par blocs, et le rapport que `216` a mesuré par un chemin entièrement
différent, qui tombe dedans sur les trois paires. En bas à gauche, L'ÉTALON, qui dit que l'épreuve
des décalages ne borne RIEN sur une série de cette longueur — un négatif sans borne est un silence,
et le dire est la moitié du résultat. En bas à droite, LE REMÈDE : l'erreur déclarée à côté de
l'erreur corrigée.

  uv run python src/figures/figure_pourquoi_lerreur_declaree_est_trop_petite.py \\
      --json docs/mesures/pourquoi_lerreur_declaree_est_trop_petite.json \\
      --sortie docs/images/217_pourquoi_lerreur_declaree_est_trop_petite.png
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


def _fr(x, n: int = 3) -> str:
    """Un nombre en français. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def _decimales_fr(texte: str) -> str:
    return re.sub(r"(?<=\d)\.(?=\d)", ",", texte)


def lire(chemin: Path) -> dict:
    """Le JSON de `pourquoi_lerreur_declaree_est_trop_petite.py`.

    ⚠⚠⚠ LES REFUS SONT CEUX QUI FERAIENT LIRE UNE AUTRE TRANCHE SOUS CE NOM. Sans l'étalon, la
    figure montrerait un négatif sans dire qu'il n'est pas borné ; sans le rapport de `216`, le
    facteur des queues n'aurait rien à prédire ; sans la famille longue, la limite de portée
    resterait invisible.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    if not (d.get("letalon") or {}).get("decidable"):
        raise SystemExit("l'étalon manque — un négatif sans étalon est un silence")
    if not (d.get("ce_que_216_a_rendu") or {}).get("decidable"):
        raise SystemExit("le rapport de `216` manque — le facteur des queues n'a rien à prédire")
    if len(d.get("ce_que_211_a_rendu") or {}) < 2:
        raise SystemExit("moins de deux paires — rien à comparer")
    for cle in ("lepreuve_des_decalages", "la_famille_longue", "lepreuve_des_queues",
                "le_tau_implique", "lerreur_corrigee"):
        if not d.get(cle):
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if v.get("une_dependance_depasse_le_hasard"):
        return "LES DEUX HYPOTHÈSES SONT FAUSSES"
    if not v.get("les_queues_rendent_compte_du_depassement"):
        return "LES QUEUES SEULES NE RENDENT PAS COMPTE DU DÉPASSEMENT"
    if not v.get("lepreuve_des_decalages_borne_quelque_chose"):
        return "CE SONT LES QUEUES, ET LE BUDGET NE LAISSE PAS DE PLACE POUR AUTRE CHOSE"
    return "CE SONT LES QUEUES, ET SEULEMENT ELLES"


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []
    points: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def replier(texte, fonte, largeur_max):
        mots, lignes, courante = texte.split(" "), [], ""
        for mot in mots:
            essai = (courante + " " + mot).strip()
            if courante and art.textlength(essai, font=fonte) > largeur_max:
                lignes.append(courante)
                courante = mot
            else:
                courante = essai
        if courante:
            lignes.append(courante)
        return lignes

    def barre(x, y, largeur_max, part, hauteur, coul):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    noms = sorted(d["ce_que_211_a_rendu"])
    par216, et, ve = d["ce_que_216_a_rendu"], d["letalon"], d["le_verdict"]
    lam = float(par216["le_rapport"])

    ecrire(50, 28, le_titre(d), gros, ENCRE)
    ecrire(50, 56,
           f"{len(noms)} paires · séries par couture CONTIGUËS publiées par `211` · "
           f"`216` a mesuré un dépassement de {_fr(lam, 4)} par un chemin entièrement différent · "
           f"aucune lecture neuve du volume", petit, GRIS)

    # ── PANNEAU 1 · LES DECALAGES ─────────────────────────────────────────────────────────────
    panneau(50, 88, 660, 404, "LES DÉCALAGES · l'autocorrélation des carrés contre son rebrassage")
    ech = max(max(d["lepreuve_des_decalages"][n]["la_famille_du_nul_la_plus_forte"] for n in noms),
              max(d["lepreuve_des_decalages"][n]["la_famille_observee"] for n in noms)) * 1.2
    bx, bw = 260, 290
    y = 126
    for n in noms:
        f = d["lepreuve_des_decalages"][n]
        lg = d["la_famille_longue"][n]
        ecrire(66, y + 1, f"{n}  courte ({f['combien_de_decalages']} décalages)", 0, ENCRE)
        barre(bx, y, bw, f["la_famille_observee"] / ech, 11, CONTRE)
        ecrire(bx + bw + 10, y, _fr(f["la_famille_observee"], 4), 0, GRIS)
        ecrire(bx + bw + 62, y,
               f"{f['les_tirages_au_moins_aussi_forts']}/{f['tirages']} ✗", 0, BON)
        y += 24
        ecrire(66, y + 1, f"       longue ({lg['combien_de_decalages']} décalages)", 0, GRIS)
        barre(bx, y, bw, lg["la_famille_observee"] / ech, 11, TRAIT)
        ecrire(bx + bw + 10, y, _fr(lg["la_famille_observee"], 4), 0, GRIS)
        ecrire(bx + bw + 62, y,
               f"{lg['les_tirages_au_moins_aussi_forts']}/{lg['tirages']} ✗", 0, BON)
        y += 34
    pire_nul = max(d["lepreuve_des_decalages"][n]["la_famille_du_nul_la_plus_forte"] for n in noms)
    xn = bx + bw * min(1.0, pire_nul / ech)
    art.line([xn, 118, xn, y - 16], fill=ENCRE, width=2)
    ecrire(xn - 108, y - 12, f"le pire rebrassage {_fr(pire_nul, 4)}", 0, ENCRE)
    ecrire(66, 346,
           "aucune paire, ni en portée courte ni en portée longue, ne rend une autocorrélation",
           0, ENCRE)
    ecrire(66, 364, "que le rebrassage de sa propre série n'égale", 0, ENCRE)
    ecrire(66, 382,
           f"⚠ la statistique d'abord déclarée, τ, est au plancher sur les trois : "
           f"{ve['la_statistique_refusee_est_au_plancher']}", 0, ALERTE)

    # ── PANNEAU 2 · LES QUEUES ────────────────────────────────────────────────────────────────
    panneau(700, 88, 1310, 404, "LES QUEUES · le facteur (κ+2)/2 et ce que `216` a mesuré")
    fmax = max(d["lepreuve_des_queues"][n]["lintervalle_par_blocs"][1] for n in noms) * 1.08
    gx0, gw = 830, 400
    for i, n in enumerate(noms):
        f = d["lepreuve_des_queues"][n]
        yy = 142 + i * 62
        bas, haut = f["lintervalle_par_blocs"]
        x1, x2 = gx0 + gw * bas / fmax, gx0 + gw * haut / fmax
        xp = gx0 + gw * f["le_facteur_des_queues"] / fmax
        ecrire(716, yy - 4, n, 0, ENCRE)
        ecrire(716, yy + 12, f"κ = {_fr(f['lexces_daplatissement'], 4)}", 0, GRIS)
        art.rectangle([x1, yy + 2, x2, yy + 12], fill=TRAIT)
        art.rectangle([xp - 2, yy - 2, xp + 2, yy + 16], fill=ALERTE)
        points.append((x2, yy + 12))
        ecrire(x2 + 8, yy + 1, _fr(f["le_facteur_des_queues"], 4), 0, ALERTE)
    xl = gx0 + gw * lam / fmax
    art.line([xl, 130, xl, 330], fill=BON, width=2)
    ecrire(xl - 4, 336, f"le dépassement mesuré par `216` : {_fr(lam, 4)}", 0, BON)
    ecrire(716, 356,
           f"le trait vert tombe DANS les trois intervalles : "
           f"{ve['combien_de_paires_couvrent_le_rapport_de_216']}/"
           f"{ve['combien_de_paires_mesurees']} paires", 0, BON)
    ecrire(716, 376,
           f"★ donc τ impliqué vaut au plus {_fr(ve['le_tau_implique_le_plus_grand'], 4)} : "
           f"le budget ne laisse pas de place pour une grosse dépendance", 0, ENCRE)

    # ── PANNEAU 3 · L'ETALON ──────────────────────────────────────────────────────────────────
    panneau(50, 428, 660, 762, "L'ÉTALON · et il dit que l'épreuve des décalages NE BORNE RIEN")
    ecrire(66, 462,
           f"séries de {et['les_coutures_par_serie']} points, comme celles que `211` publie", 0,
           GRIS)
    ex, ew = 330, 200
    yy = 486
    for e in et["lechelle_par_volatilite"]:
        ecrire(66, yy, f"volatilité stochastique φ = {_fr(e['la_force'], 2)}", 0, ENCRE)
        barre(ex, yy, ew, e["les_vus"] / float(e["sur"]), 10, CONTRE)
        ecrire(ex + ew + 10, yy - 1, f"{e['les_vus']}/{e['sur']}", 0, GRIS)
        yy += 22
    yy += 6
    for e in et["lechelle_par_echelle_lente"]:
        ecrire(66, yy, f"échelle lente a = {_fr(e['la_force'], 2)}", 0, ENCRE)
        barre(ex, yy, ew, e["les_vus"] / float(e["sur"]), 10, TRAIT)
        ecrire(ex + ew + 10, yy - 1, f"{e['les_vus']}/{e['sur']}", 0, GRIS)
        yy += 22
    ecrire(66, 730,
           f"faux {et['les_faux']}/{et['le_compte_decisif']} = "
           f"{_fr(et['le_taux_de_faux'], 4)} · piège (queues κ="
           f"{_fr(et['laplatissement_du_piege'], 0)} sans dépendance) "
           f"{et['les_tirs_sur_le_piege']}/{et['le_compte_decisif']} = "
           f"{_fr(et['le_taux_sur_le_piege'], 4)}", 0, BON)
    ecrire(66, 746,
           "⚠ aucune force n'est vue par TOUS les réplicats : plus la dépendance monte, plus les "
           "queues montent avec", 0, ALERTE)

    # ── PANNEAU 4 · LE REMEDE ─────────────────────────────────────────────────────────────────
    panneau(700, 428, 1310, 762, "LE REMÈDE · se(V) = V·√((κ+2)/n), et il tient en une ligne")
    rmax = max(d["lerreur_corrigee"][n]["lerreur_corrigee_en_voxels2"] for n in noms) * 1.15
    rx, rw = 960, 250
    yy = 476
    for n in noms:
        co = d["lerreur_corrigee"][n]
        ecrire(716, yy + 1, f"{n}  déclarée", 0, ENCRE)
        barre(rx, yy, rw, co["lerreur_declaree_en_voxels2"] / rmax, 11, CONTRE)
        ecrire(rx + rw + 10, yy, f"{_fr(co['lerreur_declaree_en_voxels2'], 4)} vx²", 0, GRIS)
        yy += 22
        ecrire(716, yy + 1, "       corrigée", 0, ALERTE)
        barre(rx, yy, rw, co["lerreur_corrigee_en_voxels2"] / rmax, 11, ALERTE)
        ecrire(rx + rw + 10, yy, f"{_fr(co['lerreur_corrigee_en_voxels2'], 4)} vx²", 0, GRIS)
        yy += 20
        ecrire(716, yy, f"       rapport {_fr(co['le_rapport'], 4)}", 0, ENCRE)
        yy += 30
    ecrire(716, 706,
           "l'aplatissement se mesure sur ce qui est DÉJÀ lu : aucune lecture neuve, aucun réglage",
           0, ENCRE)
    ecrire(716, 728,
           "⚠ et il n'a aucune raison d'être le même d'une paire à l'autre, ni d'un rouleau à "
           "l'autre", 0, GRIS)

    # ── BANDE ─────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 790, L, H], fill=BANDE)
    ecrire(50, 812, f"CE QUI RESTE À MESURER : {ve['ce_qui_reste_a_mesurer']}", moyen, ENCRE)
    for i, ligne in enumerate(replier(_decimales_fr(f"     {ve['pourquoi']}."), moyen, L - 112)):
        ecrire(50, 840 + i * 22, ligne, moyen, ENCRE)
    ecrire(50, 930,
           "★ la formule d'erreur de toute la chaîne 208 à 215 est fausse parce qu'elle suppose une "
           "gaussienne, et la matière n'en est pas une.", moyen, ENCRE)
    ecrire(50, 954,
           "⚠ ce qui n'est PAS établi : que les coutures soient indépendantes. Elles le paraissent, "
           "et l'instrument est trop faible pour l'affirmer.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, barres, points


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
    tmp = sortie.parent / ".sonde_217.png"
    _, poses, cadres, barres, points = dessiner(d, tmp)

    v("★★★★ les quatre titres possibles sont DISTINCTS",
      len({le_titre({"le_verdict": {"une_dependance_depasse_le_hasard": a,
                                    "les_queues_rendent_compte_du_depassement": b,
                                    "lepreuve_des_decalages_borne_quelque_chose": c}})
           for a in (True, False) for b in (True, False) for c in (True, False)}) == 4)
    v("★★★ le titre LIT le verdict au lieu de le recalculer",
      ("PAS DE PLACE" in le_titre(d))
      == (not d["le_verdict"]["une_dependance_depasse_le_hasard"]
          and d["le_verdict"]["les_queues_rendent_compte_du_depassement"]
          and not d["le_verdict"]["lepreuve_des_decalages_borne_quelque_chose"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, 1360),
      str(textes_debordants(poses, 1360))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ aucune barre ne déborde de sa piste", all(b <= p + 1e-6 for b, p in barres),
      str([x for x in barres if x[0] > x[1] + 1e-6])[:160])
    v("★★★ tout ce qui est tracé reste dans la toile",
      all(0 <= x <= 1360 and 0 <= y <= 980 for x, y in points))

    txt = " ".join(t for _, _, t, _ in poses)
    noms = sorted(d["ce_que_211_a_rendu"])
    v("★★★★ elle porte les TROIS paires, en portée courte ET en portée longue — montrer la seule "
      "courte cacherait que la limite de portée a été regardée",
      all(n in txt for n in noms)
      and all(f"{d['la_famille_longue'][n]['combien_de_decalages']} décalages" in txt
              for n in noms))
    v("★★★★ elle porte chaque compte de rebrassages, sans quoi une autocorrélation nue ne dirait "
      "pas si elle est remarquable",
      all(f"{d['lepreuve_des_decalages'][n]['les_tirages_au_moins_aussi_forts']}/"
          f"{d['lepreuve_des_decalages'][n]['tirages']}" in txt for n in noms))
    v("★★★★ elle porte le rapport de `216` ET les trois facteurs de queues — c'est leur "
      "RENCONTRE qui est le résultat",
      _fr(d["ce_que_216_a_rendu"]["le_rapport"], 4) in txt
      and all(_fr(d["lepreuve_des_queues"][n]["le_facteur_des_queues"], 4) in txt for n in noms))
    v("★★★★ elle porte le τ impliqué le plus grand, qui est la borne que l'étalon n'a pas pu donner",
      _fr(d["le_verdict"]["le_tau_implique_le_plus_grand"], 4) in txt)
    v("★★★★ elle porte les DEUX échelles de l'étalon et dit qu'aucune force n'est vue partout",
      all(_fr(e["la_force"], 2) in txt for e in d["letalon"]["lechelle_par_volatilite"])
      and "aucune force n'est vue par TOUS" in txt)
    v("★★★★ elle porte le taux du PIÈGE, sans lequel le négatif pourrait venir d'une règle qui ne "
      "tire jamais",
      _fr(d["letalon"]["le_taux_sur_le_piege"], 4) in txt)
    v("★★★★ elle porte l'erreur déclarée À CÔTÉ de la corrigée pour chaque paire",
      all(_fr(d["lerreur_corrigee"][n]["lerreur_declaree_en_voxels2"], 4) in txt
          and _fr(d["lerreur_corrigee"][n]["lerreur_corrigee_en_voxels2"], 4) in txt
          for n in noms))
    v("★★★★ elle dit ce qui n'est PAS établi — que les coutures soient indépendantes",
      "n'est PAS établi" in txt and "trop faible" in txt)
    v("★★★ elle dit qu'aucune lecture neuve du volume n'a eu lieu",
      "aucune lecture neuve du volume" in txt)
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
                   default=RACINE / "docs" / "mesures"
                   / "pourquoi_lerreur_declaree_est_trop_petite.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "217_pourquoi_lerreur_declaree_est_trop_petite.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
