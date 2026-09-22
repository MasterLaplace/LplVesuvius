"""Les erreurs déclarées rendent-elles compte des résidus ? Le budget, la forme, les queues, l'étalon.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, LE BUDGET : l'énergie que les
résidus portent contre celle que les erreurs déclarées autorisent, avec les tirages du modèle
déclaré. En haut à droite, LA FORME, et c'est le panneau qui retourne `214` : les résidus
standardisés bruts, puis les mêmes une fois le budget remis à l'échelle, avec la bande que le modèle
déclaré produit. Le pire résidu rentre dans la bande. En bas à gauche, LES QUEUES : le pire désaccord
de chaque paire en écarts-types, contre ce qu'une gaussienne fait de pire — c'est la preuve, déjà
publiée par `214` et jamais lue ainsi, que la formule d'erreur suppose une loi que la matière n'a
pas. En bas à droite, l'étalon, qui montre ce que chaque épreuve peut et NE PEUT PAS distinguer.

  uv run python src/figures/figure_les_erreurs_declarees_rendent_elles_compte_des_residus.py \\
      --json docs/mesures/les_erreurs_declarees_rendent_elles_compte_des_residus.json \\
      --sortie docs/images/216_les_erreurs_declarees_rendent_elles_compte_des_residus.png
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
    """Les décimales d'une phrase construite par le module, en français."""
    return re.sub(r"(?<=\d)\.(?=\d)", ",", texte)


def lire(chemin: Path) -> dict:
    """Le JSON de `les_erreurs_declarees_rendent_elles_compte_des_residus.py`.

    ⚠⚠⚠ LES REFUS SONT CEUX QUI FERAIENT LIRE UNE AUTRE TRANCHE SOUS CE NOM. Sans le contrôle des
    queues, la figure laisserait croire que la seule explication du dépassement est la dépendance
    des coutures ; sans l'étalon, elle montrerait deux épreuves sans dire laquelle sépare quoi.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle, quoi in (("lepreuve_du_budget", "l'épreuve du budget"),
                      ("lepreuve_de_la_forme", "l'épreuve de la forme"),
                      ("le_controle_des_queues", "le contrôle des queues"),
                      ("letalon", "l'étalon"),
                      ("le_refus_du_khi_deux_naif", "le refus du khi-deux naïf")):
        if not (d.get(cle) or {}).get("decidable"):
            raise SystemExit(f"{quoi} manque")
    if (d.get("lepreuve_du_budget") or {}).get("lempreinte_du_nul") \
            != (d.get("lepreuve_de_la_forme") or {}).get("lempreinte_du_nul"):
        raise SystemExit("les deux épreuves ne lisent pas le même nul")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer — défaut payé par la figure de `214`."""
    v = d["le_verdict"]
    if not v.get("les_residus_depassent_le_budget"):
        return "LES ERREURS DÉCLARÉES RENDENT COMPTE DES RÉSIDUS"
    if v.get("lexces_est_concentre"):
        return "UNE RUPTURE SUR QUELQUES PAIRES, QUE LE BUDGET N'EXPLIQUE PAS"
    return "LES ERREURS DÉCLARÉES SONT SOUS-ESTIMÉES D'UN FACTEUR " + _fr(
        v.get("le_facteur_sur_lerreur"), 4)


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

    lu = d["ce_que_214_a_rendu"]
    bg, b, f = d["le_budget_attendu"], d["lepreuve_du_budget"], d["lepreuve_de_la_forme"]
    q, e, n, et = (d["le_controle_des_queues"], d["les_coutures_effectives"],
                   d["le_refus_du_khi_deux_naif"], d["letalon"])
    std = d["lajustement"]["les_residus_standardises"]
    ve = d["le_verdict"]

    ecrire(50, 28, le_titre(d), gros, ENCRE)
    ecrire(50, 56,
           f"{lu['combien_de_rangees']} rangées · {lu['combien_de_paires']} paires · coutures de "
           f"{lu['les_coutures_les_moins_nombreuses']} à "
           f"{lu['les_coutures_les_plus_nombreuses']} · le pire résidu de `214` valait "
           f"{_fr(lu['le_pire_residu_de_214_en_erreurs'], 4)} erreurs sur "
           f"{lu['la_paire_du_pire_residu_de_214']} · aucune lecture neuve du volume",
           petit, GRIS)

    # ── PANNEAU 1 · LE BUDGET ─────────────────────────────────────────────────────────────────
    panneau(50, 88, 660, 404, "LE BUDGET · ce que les erreurs déclarées autorisent")
    ech = max(b["le_rapport"], b["le_rapport_du_nul_le_plus_fort"]) * 1.12
    bx, bw = 250, 330
    for i, (nom, val, coul) in enumerate((
            ("observé", b["le_rapport"], ALERTE),
            ("nul le plus fort", b["le_rapport_du_nul_le_plus_fort"], CONTRE),
            ("nul médian", b["le_rapport_du_nul_median"], CONTRE),
            ("budget déclaré", 1.0, BON))):
        y = 132 + i * 38
        ecrire(66, y + 2, nom, 0, ENCRE)
        barre(bx, y, bw, val / ech, 14, coul)
        ecrire(bx + bw + 12, y + 1, _fr(val, 4), 0, GRIS)
    ecrire(66, 298,
           f"énergie observée {_fr(b['lenergie_observee'], 4)} pour un budget de "
           f"{_fr(b['lenergie_attendue'], 4)} · {b['les_tirages_au_moins_aussi_forts']}/"
           f"{b['tirages']} tirages au moins aussi forts", 0, ALERTE)
    ecrire(66, 318,
           f"l'erreur déclarée est donc sous-estimée d'un facteur "
           f"{_fr(b['le_facteur_sur_lerreur'], 4)}", 0, ENCRE)
    ecrire(66, 344,
           f"⚠ refus nommé : avec `n - p` = {_fr(bg['la_trace_du_projecteur'], 0)} le rapport "
           f"vaudrait {_fr(n['le_rapport_naif'], 4)} au lieu de {_fr(n['le_rapport_exact'], 4)},",
           0, GRIS)
    ecrire(66, 362,
           f"soit {_fr(n['lecart_relatif'], 4)} d'écart — `n - p` répond pour un ajustement "
           f"PONDÉRÉ, et celui de `214` ne l'est pas", 0, GRIS)
    ecrire(66, 382,
           f"coutures effectives au plus {_fr(e['les_coutures_effectives_impliquees'], 1)} pour "
           f"{e['les_coutures_medianes_declarees']} déclarées — un PLANCHER", 0, GRIS)

    # ── PANNEAU 2 · LA FORME ──────────────────────────────────────────────────────────────────
    panneau(700, 88, 1310, 404, "LA FORME · une fois le budget remis à l'échelle")
    vals = sorted((abs(v) for v in std.values()), reverse=True)
    rac = float(b["le_rapport"]) ** 0.5
    gx0, gy1, gw, gh = 740, 330, 540, 190
    hmax = max(vals[0], f["la_forme_du_nul_la_plus_forte"]) * 1.1
    art.line([gx0, gy1, gx0 + gw, gy1], fill=TRAIT)
    pas = gw / float(len(vals))
    for i, v_ in enumerate(vals):
        x = gx0 + i * pas
        art.rectangle([x, gy1 - gh * v_ / hmax, x + pas * 0.42, gy1], fill=ALERTE)
        art.rectangle([x + pas * 0.46, gy1 - gh * (v_ / rac) / hmax, x + pas * 0.88, gy1],
                      fill=CONTRE)
        points.append((x + pas * 0.88, gy1 - gh * v_ / hmax))
    yb = gy1 - gh * float(f["la_forme_du_nul_la_plus_forte"]) / hmax
    art.line([gx0, yb, gx0 + gw, yb], fill=ENCRE, width=2)
    ecrire(gx0 + gw - 254, yb - 16,
           f"le pire du modèle déclaré {_fr(f['la_forme_du_nul_la_plus_forte'], 4)}", 0, ENCRE)
    ecrire(716, 128, "en ambre le résidu BRUT, en bleu le même une fois le budget remis à l'échelle",
           0, GRIS)
    ecrire(716, 146,
           f"le pire passe de {_fr(max(vals), 4)} à "
           f"{_fr(f['le_plus_grand_residu_remis_a_lechelle'], 4)} sur "
           f"{f['la_paire_du_plus_grand']}, et rentre sous le trait", 0, ENCRE)
    ecrire(716, 348,
           f"{f['les_tirages_au_moins_aussi_forts']}/{f['tirages']} tirages du modèle déclaré font "
           f"au moins aussi fort · médian remis à l'échelle "
           f"{_fr(f['le_residu_median_remis_a_lechelle'], 4)}", 0, BON)
    ecrire(716, 372,
           "⚠ l'excès est donc ÉTALÉ et non CONCENTRÉ : le dénominateur ment, pas le modèle",
           0, ENCRE)

    # ── PANNEAU 3 · LES QUEUES ────────────────────────────────────────────────────────────────
    panneau(50, 428, 660, 762,
            "LES QUEUES · la formule suppose aussi une gaussienne, et `214` l'avait déjà réfutée")
    qx, qw = 240, 340
    for i, (nom, val, coul) in enumerate((
            ("le pire, toutes paires", q["le_rapport_le_plus_grand"], ALERTE),
            ("la paire médiane", q["le_rapport_median"], ALERTE),
            ("la paire la plus sage", q["le_rapport_le_plus_petit"], CONTRE),
            ("la pire gaussienne", q["la_reference_gaussienne_la_plus_forte"], BON),
            ("la gaussienne médiane", q["la_reference_gaussienne_mediane"], BON))):
        y = 470 + i * 36
        ecrire(66, y + 2, nom, 0, ENCRE)
        barre(qx, y, qw, val / (q["le_rapport_le_plus_grand"] * 1.1), 13, coul)
        ecrire(qx + qw + 12, y + 1, _fr(val, 4), 0, GRIS)
    ecrire(66, 664,
           f"le pire désaccord d'une paire, en écarts-types, contre une gaussienne de "
           f"{q['les_coutures_de_reference']} tirages", 0, GRIS)
    ecrire(66, 690,
           f"la normalité est REFUSÉE : la moitié des paires dépasse ce qu'une gaussienne fait de "
           f"pire ✗", 0, ALERTE)
    ecrire(66, 714,
           f"★ un excès d'aplatissement de {_fr(q['lexces_daplatissement_qui_suffirait'], 4)} "
           f"suffirait à expliquer tout le dépassement", 0, ENCRE)
    ecrire(66, 732,
           "sans qu'aucune couture ne soit corrélée — les deux défauts ne sont PAS séparés ici",
           0, ENCRE)

    # ── PANNEAU 4 · L'ETALON ──────────────────────────────────────────────────────────────────
    panneau(700, 428, 1310, 762, "L'ÉTALON · ce que chaque épreuve peut, et ne peut PAS, distinguer")
    ecrire(716, 462,
           f"décalage sur {et['les_paires_decalees']} paires · à budget ÉGAL, étalée contre "
           f"concentrée", 0, GRIS)
    ecrire(716, 486, "facteur", 0, GRIS)
    ecrire(800, 486, "le budget voit", 0, GRIS)
    ecrire(1010, 486, "la forme dit CONCENTRÉE", 0, GRIS)
    for i, x in enumerate(et["lechelle"]):
        y = 506 + i * 28
        ecrire(722, y, _fr(x["le_facteur"], 2), 0, ENCRE)
        ecrire(800, y, f"étalée {x['le_budget_voit_letalee']}/{x['sur']}", 0, CONTRE)
        ecrire(892, y, f"concentrée {x['le_budget_voit_la_concentree']}/{x['sur']}", 0, CONTRE)
        ecrire(1010, y, f"étalée {x['la_forme_dit_concentree_sur_letalee']}/{x['sur']}", 0, BON)
        ecrire(1112, y, f"concentrée {x['la_forme_dit_concentree_sur_la_concentree']}/{x['sur']}",
               0, ALERTE)
    ecrire(716, 662,
           f"le budget voit dès {_fr(et['le_plus_petit_facteur_vu_par_le_budget'], 2)} et ne "
           f"distingue JAMAIS les deux matières · la forme sépare dès "
           f"{_fr(et['le_plus_petit_facteur_ou_la_forme_separe'], 2)}", 0, ENCRE)
    ecrire(716, 684,
           f"faux du budget {et['les_faux_du_budget']}/{et['le_compte_decisif']} = "
           f"{_fr(et['le_taux_de_faux_du_budget'], 4)} · faux de la forme "
           f"{et['les_faux_de_la_forme']}/{et['le_compte_decisif']} = "
           f"{_fr(et['le_taux_de_faux_de_la_forme'], 4)}", 0, BON)
    ecrire(716, 706,
           f"contre une garantie de {_fr(d['la_garantie_du_nul'], 4)} · "
           f"{et['les_variances_negatives_rencontrees']} variance négative rencontrée", 0, GRIS)
    ecrire(716, 726,
           f"⚠ l'échelle du budget n'est pas monotone : il plafonne dès "
           f"{_fr(et['le_plus_petit_facteur_vu_par_le_budget'], 2)},", 0, GRIS)
    ecrire(716, 742, "donc un réplicat manquant plus haut est du tirage et non une régression",
           0, GRIS)

    # ── BANDE ─────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 790, L, H], fill=BANDE)
    ecrire(50, 812, f"CE QUI RESTE À MESURER : {ve['ce_qui_reste_a_mesurer']}", moyen, ENCRE)
    for i, ligne in enumerate(replier(_decimales_fr(f"     {ve['pourquoi']}."), moyen, L - 112)):
        ecrire(50, 840 + i * 22, ligne, moyen, ENCRE)
    ecrire(50, 928,
           f"★ donc le résidu de {lu['la_paire_du_pire_residu_de_214']}, que `214` publiait à "
           f"{_fr(lu['le_pire_residu_de_214_en_erreurs'], 4)} erreurs, vaut "
           f"{_fr(f['le_plus_grand_residu_remis_a_lechelle'], 4)} une fois le budget corrigé : un "
           f"maximum parfaitement ordinaire parmi {lu['combien_de_paires']}.", moyen, ENCRE)
    ecrire(50, 952,
           "⚠ cette tranche ne sépare PAS la dépendance des coutures de leurs queues : elle "
           "établit que la formule d'erreur est fausse, pas laquelle de ses deux hypothèses l'est.",
           moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_216.png"
    _, poses, cadres, barres, points = dessiner(d, tmp)

    v("★★★ le titre LIT le verdict au lieu de le recalculer",
      ("SOUS-ESTIMÉES" in le_titre(d))
      == (d["le_verdict"]["les_residus_depassent_le_budget"]
          and not d["le_verdict"]["lexces_est_concentre"]))
    v("★★★★ les trois titres possibles sont DISTINCTS",
      len({le_titre({"le_verdict": {"les_residus_depassent_le_budget": a,
                                    "lexces_est_concentre": b,
                                    "le_facteur_sur_lerreur": 1.5}})
           for a in (True, False) for b in (True, False)}) == 3)
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
    b, f, q, et = (d["lepreuve_du_budget"], d["lepreuve_de_la_forme"],
                   d["le_controle_des_queues"], d["letalon"])
    v("★★★★ elle porte le rapport ET le compte de tirages — un rapport seul ne dit pas s'il est "
      "remarquable",
      _fr(b["le_rapport"], 4) in txt
      and f"{b['les_tirages_au_moins_aussi_forts']}/{b['tirages']}" in txt)
    v("★★★★ elle porte le pire résidu de `214` ET le même une fois le budget remis à l'échelle — "
      "montrer l'un sans l'autre serait montrer la moitié du résultat",
      _fr(d["ce_que_214_a_rendu"]["le_pire_residu_de_214_en_erreurs"], 4) in txt
      and _fr(f["le_plus_grand_residu_remis_a_lechelle"], 4) in txt)
    v("★★★★ elle porte le refus du khi-deux naïf avec les DEUX rapports",
      _fr(d["le_refus_du_khi_deux_naif"]["le_rapport_naif"], 4) in txt
      and _fr(d["le_refus_du_khi_deux_naif"]["lecart_relatif"], 4) in txt)
    v("★★★★ elle porte le contrôle des queues AVEC sa référence gaussienne — les queues seules ne "
      "voudraient rien dire sans ce à quoi elles sont comparées",
      _fr(q["le_rapport_median"], 4) in txt
      and _fr(q["la_reference_gaussienne_la_plus_forte"], 4) in txt)
    v("★★★★ elle porte l'excès d'aplatissement qui suffirait, sans lequel la seconde hypothèse de "
      "la formule resterait invisible",
      _fr(q["lexces_daplatissement_qui_suffirait"], 4) in txt)
    v("★★★★ elle porte les DEUX taux de faux de l'étalon",
      _fr(et["le_taux_de_faux_du_budget"], 4) in txt
      and _fr(et["le_taux_de_faux_de_la_forme"], 4) in txt)
    v("★★★★ elle dit que le budget ne distingue JAMAIS les deux matières — c'est la limite de la "
      "première épreuve et la raison d'être de la seconde",
      "ne distingue JAMAIS" in txt)
    v("★★★★ elle dit que la tranche ne sépare PAS la dépendance des queues",
      "ne sépare PAS la dépendance" in txt)
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
                   / "les_erreurs_declarees_rendent_elles_compte_des_residus.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "216_les_erreurs_declarees_rendent_elles_compte_des_residus.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
