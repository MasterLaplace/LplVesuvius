"""Le vote ramène-t-il les rangées sur le feuillet : ce qu'il retire, le tronçon, la rangée, les nuls refusés.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, CE QUE LE VOTE RETIRE : le
désaccord par couture baisse sur les quatre paires voisines. En haut à droite, LE TRONÇON : les
séparations ne passent pas pour autant sous le demi-feuillet, et une paire s'aggrave. En bas à gauche,
LA RANGÉE ENTIÈRE, et c'est le panneau qui conclut : la marche typique reste au-dessus du demi-feuillet
sur les quatre paires. En bas à droite, LES DEUX NULS REFUSÉS, parce qu'un négatif mesuré avec un
instrument faux ne dirait rien.

  uv run python src/figures/figure_le_vote_ramene_t_il_les_rangees_sur_le_feuillet.py \\
      --json docs/mesures/le_vote_ramene_t_il_les_rangees_sur_le_feuillet.json \\
      --sortie docs/images/220_le_vote_ramene_t_il_les_rangees_sur_le_feuillet.png
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


def lire(chemin: Path) -> dict:
    """Le JSON de `le_vote_ramene_t_il_les_rangees_sur_le_feuillet.py`.

    ⚠⚠⚠ SANS L'ÉTALON DU NUL DE LA PORTE, un vote qui « perd » contre lui se lirait comme un vote qui
    se trompe ; sans la marche refusée, la marche retenue n'aurait pas de raison d'être centrée.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    if not (d.get("letalon") or {}).get("decidable"):
        raise SystemExit("l'étalon du nul de la porte manque")
    paires = d.get("les_paires_voisines") or {}
    if not paires or not all(x.get("decidable") for x in paires.values()):
        raise SystemExit("une paire voisine est indécidable")
    for cle in ("le_nul_de_la_porte", "le_verdict"):
        if not d.get(cle):
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    t, n = v["combien_tiennent_a_lechelle_de_la_rangee"], v["combien_de_paires"]
    if t == 0:
        return "LE VOTE AUX EXTRÊMES NE GARDE PAS LES RANGÉES SUR LE MÊME FEUILLET"
    if t < n:
        return f"LE VOTE GARDE {t} PAIRE(S) VOISINE(S) SUR {n} SUR LE MÊME FEUILLET"
    return "LE VOTE GARDE LES RANGÉES SUR LE MÊME FEUILLET"


def dessiner(d: dict, sortie: Path):
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

    ps, ve, po, et = d["les_paires_voisines"], d["le_verdict"], d["le_nul_de_la_porte"], d["letalon"]
    demi = float(d["le_demi_pli_en_voxels"])
    noms = sorted(ps)

    ecrire(50, 28, le_titre(d), gros, ENCRE)
    ecrire(50, 56,
           f"{len(d['les_colonnes_fortes_de_219'])} colonnes fortes de `219` corrigées par la médiane "
           f"des quatre autres rangées · {len(noms)} paires voisines · demi-feuillet {int(demi)} vx · "
           f"une rangée = {d['les_coutures_dune_rangee']} coutures · aucune lecture neuve", petit, GRIS)

    def deux_barres(x0, y0, titre_bas, cle_av, cle_ap, unite, echelle, ligne=None):
        bx, bw = x0 + 150, 300
        y = y0
        for n in noms:
            x = ps[n]
            ecrire(x0 + 16, y + 1, n, 0, ENCRE)
            barre(bx, y, bw, x[cle_av] / echelle, 9, TRAIT)
            ecrire(bx + bw + 10, y - 1, f"{_fr(x[cle_av], 2)} {unite}", 0, GRIS)
            y += 14
            barre(bx, y, bw, x[cle_ap] / echelle, 9, CONTRE)
            ecrire(bx + bw + 10, y - 1, f"{_fr(x[cle_ap], 2)} {unite}", 0, CONTRE)
            y += 26
        if ligne is not None:
            xl = bx + bw * ligne / echelle
            art.line([xl, y0 - 6, xl, y - 18], fill=ALERTE, width=2)
            ecrire(xl - 50, y - 14, f"demi-feuillet {int(ligne)} vx", 0, ALERTE)
        ecrire(x0 + 16, y + 8, titre_bas, 0, GRIS)
        return y

    # ── PANNEAU 1 · CE QUE LE VOTE RETIRE ───────────────────────────────────────────────────
    panneau(50, 88, 660, 404, "CE QUE LE VOTE RETIRE · le désaccord par couture")
    e1 = max(max(ps[n]["lecart_type_des_desaccords_avant_en_voxels"] for n in noms), 1.0) * 1.15
    deux_barres(50, 130, "gris : avant le vote · bleu : après", "lecart_type_des_desaccords_avant_en_voxels",
                "lecart_type_des_desaccords_apres_en_voxels", "vx", e1)
    ecrire(66, 360, "le vote retire bien quelque chose, sur les quatre paires : ses extrêmes", 0, ENCRE)
    ecrire(66, 378, "⚠ mais ce qui sépare deux rangées est la marche, pas la couture", 0, ALERTE)

    # ── PANNEAU 2 · LE TRONCON ──────────────────────────────────────────────────────────────
    panneau(700, 88, 1310, 404, "LE TRONÇON · la séparation, avant et après le vote")
    e2 = max(max(max(ps[n]["la_separation_avant_en_voxels"], ps[n]["la_separation_apres_en_voxels"])
                 for n in noms), demi) * 1.15
    deux_barres(700, 130, "sur le plus long tronçon commun de chaque paire",
                "la_separation_avant_en_voxels", "la_separation_apres_en_voxels", "vx", e2, demi)
    av_, ap_ = (ve["combien_sous_le_demi_pli_avant_sur_le_troncon"],
                ve["combien_sous_le_demi_pli_apres_sur_le_troncon"])
    ecrire(716, 360,
           f"sous le demi-feuillet : {av_} paires avant, {ap_} après"
           + (" — le vote n'en change aucune" if av_ == ap_ else ""), 0, ENCRE)
    pire = max(noms, key=lambda n: ps[n]["la_separation_apres_en_voxels"]
               - ps[n]["la_separation_avant_en_voxels"])
    if ps[pire]["la_separation_apres_en_voxels"] > ps[pire]["la_separation_avant_en_voxels"]:
        ecrire(716, 378, f"⚠ et {pire} s'aggrave : le vote aligne une rangée sur les "
                         f"quatre autres, à tort ou à raison", 0, ALERTE)

    # ── PANNEAU 3 · LA RANGEE ───────────────────────────────────────────────────────────────
    panneau(50, 428, 660, 762, "LA RANGÉE ENTIÈRE · la marche médiane de pas centrés")
    e3 = max(max(ps[n]["la_rangee_mediane_avant_en_voxels"] for n in noms), demi) * 1.15
    y = deux_barres(50, 470, f"marches de {d['les_coutures_dune_rangee']} coutures tirées dans les "
                    f"désaccords du tronçon", "la_rangee_mediane_avant_en_voxels",
                    "la_rangee_mediane_apres_en_voxels", "vx", e3, demi)
    ecrire(66, 690, "rangées qui restent sous le demi-feuillet, avant → après :", 0, ENCRE)
    ecrire(66, 708, " · ".join(f"{n} {ps[n]['les_rangees_sous_le_demi_pli_avant']}→"
                               f"{ps[n]['les_rangees_sous_le_demi_pli_apres']}/{ps[n]['tirages']}"
                               for n in noms), 0, GRIS)
    ecrire(66, 732, f"★ {ve['combien_tiennent_a_lechelle_de_la_rangee']} paire sur "
                    f"{ve['combien_de_paires']} : la marche typique quitte le feuillet partout", 0,
           ALERTE if ve["combien_tiennent_a_lechelle_de_la_rangee"] == 0 else BON)

    # ── PANNEAU 4 · LES DEUX NULS REFUSES ───────────────────────────────────────────────────
    panneau(700, 428, 1310, 762, "LES DEUX INSTRUMENTS REFUSÉS")
    ecrire(716, 462, "1 · la marche qui garde la moyenne du tronçon", 0, ENCRE)
    x = ps[noms[0]]
    r_ = x["la_marche_refusee"]
    ecrire(730, 482, f"{noms[0]} : moyenne {_fr(x['la_moyenne_des_desaccords_apres_en_voxels'], 4)} ± "
                     f"{_fr(x['son_erreur_en_voxels'], 4)} vx par couture", 0, GRIS)
    ecrire(730, 500, f"sur une rangée elle fabrique {_fr(r_['la_derive_quelle_fabrique_apres_en_voxels'], 2)}"
                     f" ± {_fr(r_['lerreur_sur_cette_derive_en_voxels'], 2)} vx de dérive,", 0, GRIS)
    ecrire(730, 518, f"quand la marche ne s'étale que de {_fr(r_['ce_que_la_marche_setale_en_voxels'], 2)}"
                     f" vx : elle mesure l'erreur d'une moyenne", 0, GRIS)
    ecrire(730, 536, f"refusée : sa marche médiane vaudrait {_fr(r_['la_rangee_mediane_apres_en_voxels'], 2)}"
                     f" vx au lieu de {_fr(x['la_rangee_mediane_apres_en_voxels'], 2)}", 0, ALERTE)
    ecrire(716, 574, "2 · le nul de la porte : corriger une AUTRE rangée", 0, ENCRE)
    ecrire(730, 594, f"sur du bruit pur il « gagne » {et['les_victoires_sur_du_bruit']}/"
                     f"{et['le_compte_decisif']} = {_fr(et['le_taux'], 4)}, plus de deux fois la "
                     f"garantie", 0, GRIS)
    ecrire(730, 612, f"sur la matière le vote fait {_fr(po['la_somme_des_separations_apres_le_vote'], 2)}"
                     f" vx contre {_fr(po['la_somme_mediane_par_une_autre_rangee'], 2)}", 0, GRIS)
    ecrire(730, 630, f"({po['les_tirages_au_moins_aussi_bons']}/{po['tirages']} autres rangées font au "
                     f"moins aussi bien) : une séparation est un seul maximum", 0, GRIS)
    ecrire(730, 648, "refusé : il ne tient pas sa garantie, et le verdict ne s'appuie pas sur lui",
           0, ALERTE)
    ecrire(716, 700, "★ la question « le vote désigne-t-il la bonne rangée » a sa réponse : `219`", 0,
           ENCRE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 790, L, H], fill=BANDE)
    ecrire(50, 812, f"CE QUI RESTE À MESURER : {ve['ce_qui_reste_a_mesurer']}", moyen, ENCRE)
    ecrire(50, 842,
           "★ le vote retire les extrêmes, et il ne suffit pas : ce qui sépare deux rangées voisines est "
           "la marche de leurs coutures ordinaires.", moyen, ENCRE)
    ecrire(50, 876,
           "★ la suite : le consensus des cinq voisines, pris à CHAQUE couture, traverse-t-il la rangée "
           "sans quitter le feuillet ?", moyen, ENCRE)
    ecrire(50, 910,
           "⚠ ce qui n'est PAS établi : que la moyenne d'un tronçon ne soit que du hasard — elle est "
           "publiée avec son erreur, et le centrage le suppose.", moyen, ALERTE)
    ecrire(50, 934,
           "⚠ et une rangée entière n'est lue ici que par extrapolation : les tronçons communs sont "
           "plus courts qu'elle.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_220.png"
    _, poses, cadres, barres, points = dessiner(d, tmp)

    def _v(t, n):
        return {"le_verdict": {"combien_tiennent_a_lechelle_de_la_rangee": t, "combien_de_paires": n}}

    v("★★★★ les titres possibles sont distincts, et le compte des paires qui tiennent les sépare",
      len({le_titre(_v(0, 4)), le_titre(_v(2, 4)), le_titre(_v(4, 4))}) == 3)
    v("★★★ le titre LIT le verdict",
      ("NE GARDE PAS" in le_titre(d)) == (d["le_verdict"]["combien_tiennent_a_lechelle_de_la_rangee"]
                                          == 0))
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
    ps = d["les_paires_voisines"]
    v("★★★★ elle porte les quatre paires, avant ET après, sur les trois échelles",
      all(n in txt for n in ps)
      and all(f"{_fr(x[k], 2)} vx" in txt for x in ps.values()
              for k in ("lecart_type_des_desaccords_avant_en_voxels",
                        "lecart_type_des_desaccords_apres_en_voxels",
                        "la_separation_avant_en_voxels", "la_separation_apres_en_voxels",
                        "la_rangee_mediane_avant_en_voxels", "la_rangee_mediane_apres_en_voxels")))
    v("★★★★ elle porte le compte des rangées sous le demi-feuillet, avant et après",
      all(f"{x['les_rangees_sous_le_demi_pli_avant']}→{x['les_rangees_sous_le_demi_pli_apres']}/"
          f"{x['tirages']}" in txt for x in ps.values()))
    v("★★★★ elle porte la marche refusée avec la dérive qu'elle fabrique et son erreur",
      _fr(next(iter(ps.values()))["la_marche_refusee"]["la_derive_quelle_fabrique_apres_en_voxels"], 2)
      in txt and "refusée" in txt)
    et, po = d["letalon"], d["le_nul_de_la_porte"]
    v("★★★★ elle porte le taux du nul de la porte sur du bruit et son score sur la matière",
      f"{et['les_victoires_sur_du_bruit']}/{et['le_compte_decisif']}" in txt
      and f"{po['les_tirages_au_moins_aussi_bons']}/{po['tirages']}" in txt)
    v("★★★★ elle dit ce qui n'est PAS établi — la moyenne du tronçon et l'extrapolation",
      "n'est PAS établi" in txt and "extrapolation" in txt)
    v("★★★ elle dit qu'aucune lecture neuve n'a eu lieu", "aucune lecture neuve" in txt)
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
                   / "le_vote_ramene_t_il_les_rangees_sur_le_feuillet.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "220_le_vote_ramene_t_il_les_rangees_sur_le_feuillet.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
