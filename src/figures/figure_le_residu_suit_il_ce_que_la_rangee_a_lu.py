"""Le résidu suit-il ce que la rangée a lu ? La famille, ce que l'ajustement laisse passer, la
rangée, la sensibilité.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, L'ÉPREUVE DÉCLARÉE : les six
membres de la famille, chacun sa corrélation de rangs au résidu signé, et le trait du rebrassage le
plus fort. Un membre qui dépasserait ce trait serait la réponse à `R4-P60` ; aucun ne l'approche.
En haut à droite, LA LIMITE STRUCTURELLE, et c'est elle qui donne son sens au négatif : la part
qu'un ajustement additif LAISSE PASSER de chaque covariable. Ce qui est absorbé ne peut pas rompre
l'additivité, par construction. En bas à gauche, la règle que la porte prescrivait — l'énergie par
rangée — avec la rangée que `214` nommait en post hoc et le trait qui dit qu'elle n'est pas payée.
En bas à droite, l'échelle de l'étalon : ce que la règle AURAIT vu, donc la borne.

  uv run python src/figures/figure_le_residu_suit_il_ce_que_la_rangee_a_lu.py \\
      --json docs/mesures/le_residu_suit_il_ce_que_la_rangee_a_lu.json \\
      --sortie docs/images/215_le_residu_suit_il_ce_que_la_rangee_a_lu.png
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
    """Un nombre en français, sans zéros inutiles.

    ⚠⚠ LE `rstrip` NE S'APPLIQUE QU'EN PRÉSENCE D'UNE VIRGULE : sans ce garde, `_fr(90, 0)` rend
    « 9 ». Défaut payé par `177` et repris tel quel.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def _decimales_fr(texte: str) -> str:
    """Les décimales d'une phrase, en français.

    ⚠⚠ LA RAISON DU VERDICT EST DE LA PROSE CONSTRUITE PAR LE MODULE, donc ses nombres sortent au
    format de Python. Les convertir ICI et non dans le JSON garde une seule vérité : le JSON porte
    des nombres, la figure porte du texte. Le motif exige un chiffre DES DEUX CÔTÉS du point, donc
    il ne peut pas toucher une fin de phrase ni un nom de fichier.
    """
    return re.sub(r"(?<=\d)\.(?=\d)", ",", texte)


def lire(chemin: Path) -> dict:
    """Le JSON de `le_residu_suit_il_ce_que_la_rangee_a_lu.py`.

    ⚠⚠⚠ LES REFUS SONT CEUX QUI FERAIENT LIRE UNE AUTRE TRANCHE SOUS CE NOM. Une famille qui ne
    porterait qu'un membre ne peut pas payer un choix ; une mesure sans part non additive ferait
    lire un négatif comme « cette covariable n'agit pas » au lieu de « pas NON ADDITIVEMENT » ; un
    étalon absent rendrait le négatif muet au lieu de le rendre borné.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    ep = d.get("lepreuve_declaree") or {}
    if not ep.get("decidable") or int(ep.get("combien_de_membres") or 0) < 2:
        raise SystemExit("l'épreuve déclarée ne porte pas de famille")
    if not (d.get("la_part_non_additive") or {}).get("decidable"):
        raise SystemExit("la part non additive manque — le négatif ne serait pas lisible")
    if not (d.get("letalon") or {}).get("decidable"):
        raise SystemExit("l'étalon manque — un négatif sans étalon n'est pas une borne")
    if not (d.get("la_regle_portee_par_la_porte") or {}).get("decidable"):
        raise SystemExit("la règle que la porte prescrivait n'est pas portée")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer.

    ⚠⚠⚠ `214` A PAYÉ L'INVERSE : son titre dérivait « la hauteur reste gratuite » d'un seul
    booléen alors que le JSON publie le champ, et sur ce tirage les deux divergeaient — la figure
    contredisait sa propre bande.
    """
    v = d["le_verdict"]
    if v.get("le_residu_suit_une_covariable_de_lecture"):
        return "CE QUE LES RANGÉES ONT LU EXPLIQUE LE RÉSIDU"
    if v.get("une_rangee_porte_le_residu"):
        return "UNE RANGÉE PORTE LE RÉSIDU, AUCUNE LECTURE NE LA NOMME"
    return "CE QUI ROMPT L'ADDITIVITÉ N'EST PAS DANS CE QUI A ÉTÉ LU"


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
        """Coupe un texte aux espaces — la raison du verdict change de longueur avec sa branche."""
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

    ep = d["lepreuve_declaree"]
    pa = d["la_part_non_additive"]
    ra = d["la_regle_portee_par_la_porte"]
    et = d["letalon"]
    ag = d["lagregat_refuse"]
    pg = d["le_piege_nomme"]
    pc = d["le_piege_des_covariables"]
    q214 = d["ce_que_214_a_rendu"]
    ve = d["le_verdict"]

    ecrire(50, 28, le_titre(d), gros, ENCRE)
    ecrire(50, 56,
           f"{q214['combien_de_rangees']} rangées · {q214['combien_de_paires']} paires · "
           f"pire résidu {_fr(q214['le_pire_residu_en_erreurs'], 4)} erreurs sur "
           f"{q214['la_paire_du_pire_residu_en_erreurs']} · médian "
           f"{_fr(q214['le_residu_median_en_erreurs'], 4)} · aucune lecture neuve du volume",
           petit, GRIS)

    # ── PANNEAU 1 · L'EPREUVE DECLAREE ────────────────────────────────────────────────────────
    panneau(50, 88, 660, 404, "L'ÉPREUVE DÉCLARÉE · la famille de six, déclarée avant d'être vue")
    membres = sorted(ep["les_correlations_observees"], key=lambda k: -abs(
        ep["les_correlations_observees"][k]))
    echelle = max(0.5, float(ep["la_famille_du_nul_la_plus_forte"]) * 1.15)
    bx, bw = 300, 300
    for i, m in enumerate(membres):
        y = 126 + i * 34
        c = float(ep["les_correlations_observees"][m])
        ecrire(66, y + 2, m.replace("·", " · "), 0, ENCRE)
        coul = ALERTE if m == ep["le_membre_le_plus_fort"] else CONTRE
        barre(bx, y, bw, abs(c) / echelle, 12, coul)
        ecrire(bx + bw + 12, y + 1, f"{_fr(abs(c), 4)}", 0, GRIS)
    xn = bx + bw * min(1.0, float(ep["la_famille_du_nul_la_plus_forte"]) / echelle)
    art.line([xn, 118, xn, 344], fill=ENCRE, width=2)
    ecrire(bx - 6, 352, "0", 0, GRIS)
    ecrire(xn - 62, 352, f"rebrassage le plus fort {_fr(ep['la_famille_du_nul_la_plus_forte'])}",
           0, ENCRE)
    ecrire(66, 374,
           f"le plus fort observé : {ep['le_membre_le_plus_fort']} · "
           f"{ep['les_tirages_au_moins_aussi_forts']}/{ep['tirages']} rebrassages au moins aussi "
           f"forts ✗", 0, ALERTE)

    # ── PANNEAU 2 · CE QUE L'AJUSTEMENT LAISSE PASSER ─────────────────────────────────────────
    panneau(700, 88, 1310, 404,
            "LA LIMITE STRUCTURELLE · ce qu'un ajustement additif LAISSE PASSER")
    parts = pa["les_parts_non_additives"]
    px, pw = 960, 260
    for i, m in enumerate(sorted(parts, key=lambda k: -(parts[k] or 0.0))):
        y = 126 + i * 34
        val = parts[m]
        ecrire(716, y + 2, m.replace("·", " · "), 0, ENCRE)
        coul = BON if m == pa["le_membre_le_plus_visible"] else CONTRE
        barre(px, y, pw, (val or 0.0), 12, coul)
        ecrire(px + pw + 12, y + 1, _fr(val, 4), 0, GRIS)
    ecrire(px - 6, 352, "0", 0, GRIS)
    ecrire(px + pw - 22, 352, "1", 0, GRIS)
    ecrire(716, 374,
           "une covariable ABSORBÉE n'est pas une covariable inactive : elle n'agit pas NON "
           "additivement", 0, ENCRE)

    # ── PANNEAU 3 · LA REGLE QUE LA PORTE PRESCRIVAIT ─────────────────────────────────────────
    panneau(50, 428, 660, 762,
            "LA RÈGLE QUE LA PORTE PRESCRIVAIT · l'énergie de résidu par rangée")
    en = ra["les_energies"]
    rangs = sorted(en, key=lambda k: int(k))
    emax = max(max(float(x) for x in en.values()),
               float(ra["lenergie_du_nul_la_plus_forte"])) * 1.1
    gx0, gy1, gw, gh = 100, 700, 520, 210
    art.line([gx0, gy1, gx0 + gw, gy1], fill=TRAIT)
    art.line([gx0, gy1 - gh, gx0, gy1], fill=TRAIT)
    pas = gw / float(len(rangs))
    for i, k in enumerate(rangs):
        val = float(en[k])
        hh = gh * val / emax
        x = gx0 + i * pas + pas * 0.22
        w = pas * 0.56
        coul = ALERTE if int(k) == int(ra["la_rangee_la_plus_chargee"]) else CONTRE
        art.rectangle([x, gy1 - hh, x + w, gy1], fill=coul)
        points.append((x + w, gy1 - hh))
        ecrire(x - 2, gy1 + 6, k, 0, GRIS)
    yn = gy1 - gh * float(ra["lenergie_du_nul_la_plus_forte"]) / emax
    art.line([gx0, yn, gx0 + gw, yn], fill=ENCRE, width=2)
    ecrire(gx0 + gw - 232, yn - 16,
           f"rebrassage le plus fort {_fr(ra['lenergie_du_nul_la_plus_forte'], 4)}", 0, ENCRE)
    ecrire(66, 462,
           f"la plus chargée : {ra['la_rangee_la_plus_chargee']} à "
           f"{_fr(ra['lenergie_la_plus_grande'], 4)} contre un médian de "
           f"{_fr(ra['lenergie_mediane'], 4)}", 0, ENCRE)
    ecrire(66, 480,
           f"{ra['les_tirages_au_moins_aussi_forts']}/{ra['tirages']} rebrassages au moins aussi "
           f"forts ✗ — la lecture post hoc de `214` n'est PAS payée", 0, ALERTE)
    ecrire(66, 726,
           f"agrégat refusé : la somme SIGNÉE par rangée vaut "
           f"{_fr(ag['la_plus_grande_somme_en_valeur_absolue'], 6)} vx² au pire, nulle par les "
           f"équations normales", 0, GRIS)

    # ── PANNEAU 4 · L'ETALON ──────────────────────────────────────────────────────────────────
    panneau(700, 428, 1310, 762, "L'ÉTALON · ce que la règle AURAIT vu, donc la borne")
    ecrire(716, 462, f"lien injecté sur {et['le_membre_injecte']} · "
                     f"part non additive {_fr(pa['la_part_la_plus_grande'], 4)}", 0, GRIS)
    ex, ew = 900, 280
    for i, e in enumerate(et["lechelle"]):
        y = 492 + i * 34
        part = e["les_vus"] / float(e["sur"])
        ecrire(730, y + 2, f"facteur {e['le_facteur']}", 0, ENCRE)
        coul = BON if e["les_vus"] == e["sur"] else CONTRE
        barre(ex, y, ew, part, 12, coul)
        ecrire(ex + ew + 12, y + 1, f"{e['les_vus']}/{e['sur']}", 0, GRIS)
    ecrire(716, 668,
           f"plus petit facteur vu partout : {et['le_plus_petit_facteur_vu']} erreurs "
           f"d'échantillonnage · monotone", 0, ENCRE)
    ecrire(716, 686,
           f"faux {et['les_faux']}/{et['le_compte_decisif']} = {_fr(et['le_taux_de_faux'], 4)} "
           f"contre une garantie de {_fr(d['la_garantie_par_epreuve'], 4)}", 0, BON)
    ecrire(716, 704,
           f"aveugle {et['les_aveugles']}/{et['le_compte_decisif']} = "
           f"{_fr(et['le_taux_aveugle'], 4)} · ceux qui tirent ressemblent à l'identité à "
           f"{_fr(et['la_ressemblance_mediane_des_aveugles_qui_tirent'], 4)},", 0, GRIS)
    ecrire(716, 722,
           f"ceux qui se taisent à "
           f"{_fr(et['la_ressemblance_mediane_des_aveugles_qui_se_taisent'], 4)} — un aveugle sur "
           f"neuf rangées ne peut pas être propre", 0, GRIS)

    # ── BANDE ─────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 790, L, H], fill=BANDE)
    ecrire(50, 812, f"CE QUI RESTE À MESURER : {ve['ce_qui_reste_a_mesurer']}", moyen, ENCRE)
    for i, ligne in enumerate(replier(_decimales_fr(f"     {ve['pourquoi']}."),
                                      moyen, L - 112)):
        ecrire(50, 840 + i * 22, ligne, moyen, ENCRE)
    ecrire(50, 906,
           f"piège nommé · l'énergie contre la variance propre : {_fr(pg['la_correlation_energie_variance'], 4)} "
           f"— le sens ATTENDU était négatif, le rendu est "
           f"{'négatif' if pg['le_sens_rendu_est_negatif'] else 'POSITIF'}, "
           f"{pg['les_tirages_au_moins_aussi_forts']}/{pg['tirages']} au moins aussi forts",
           0, ALERTE)
    ecrire(50, 924,
           f"piège des covariables · aucune des trois ne suit la variance propre : la plus forte "
           f"{_fr(pc['la_plus_forte_en_valeur_absolue'], 4)}, "
           f"{pc['les_tirages_au_moins_aussi_forts']}/{pc['tirages']} au moins aussi forts — "
           f"l'artefact ne peut donc rien porter", 0, BON)
    ecrire(50, 946,
           f"★ la borne : un lien de {et['le_plus_petit_facteur_vu']} erreurs sur la covariable la "
           f"MIEUX vue aurait été trouvé douze fois sur douze. Rien de tel n'est là.", moyen,
           ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, barres, points


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            resultat = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not resultat:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    d = lire(json_path)
    tmp = sortie.parent / ".sonde_215.png"
    _, poses, cadres, barres, points = dessiner(d, tmp)

    v("★★★ le titre LIT le verdict au lieu de le recalculer",
      (le_titre(d) == "CE QUI ROMPT L'ADDITIVITÉ N'EST PAS DANS CE QUI A ÉTÉ LU")
      == (not d["le_verdict"]["le_residu_suit_une_covariable_de_lecture"]
          and not d["le_verdict"]["une_rangee_porte_le_residu"]))
    v("★★★★ les trois titres possibles sont DISTINCTS, sinon la figure dirait la même chose de "
      "trois mesures différentes",
      len({le_titre({"le_verdict": {"le_residu_suit_une_covariable_de_lecture": a,
                                    "une_rangee_porte_le_residu": b}})
           for a in (True, False) for b in (True, False)}) == 3)
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, 1360),
      str(textes_debordants(poses, 1360))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ aucune barre ne déborde de sa piste",
      all(b <= p + 1e-6 for b, p in barres), str([x for x in barres if x[0] > x[1] + 1e-6])[:160])
    v("★★★ tout ce qui est tracé reste dans la toile",
      all(0 <= x <= 1360 and 0 <= y <= 980 for x, y in points))

    txt = " ".join(t for _, _, t, _ in poses)
    ep, ra, et, pa = (d["lepreuve_declaree"], d["la_regle_portee_par_la_porte"],
                      d["letalon"], d["la_part_non_additive"])
    v("★★★★ la figure porte les SIX membres de la famille — en montrer moins ferait croire que le "
      "choix a été payé sur moins de candidats qu'il ne l'a été",
      all(m.replace("·", " · ") in txt for m in ep["les_correlations_observees"]))
    v("★★★★ elle nomme le membre le plus fort et son compte de rebrassages",
      ep["le_membre_le_plus_fort"] in txt
      and f"{ep['les_tirages_au_moins_aussi_forts']}/{ep['tirages']}" in txt)
    v("★★★★ elle porte la part non additive, sans quoi le négatif se lirait « cette covariable "
      "n'agit pas »",
      _fr(pa["la_part_la_plus_grande"], 4) in txt and _fr(pa["la_part_la_plus_petite"], 4) in txt)
    v("★★★★ elle nomme la rangée que `214` lisait en post hoc ET le compte qui dit qu'elle n'est "
      "pas payée",
      str(ra["la_rangee_la_plus_chargee"]) in txt
      and f"{ra['les_tirages_au_moins_aussi_forts']}/{ra['tirages']}" in txt)
    v("★★★★ elle porte l'agrégat REFUSÉ et la raison de son refus",
      "équations normales" in txt
      and _fr(d["lagregat_refuse"]["la_plus_grande_somme_en_valeur_absolue"], 6) in txt)
    v("★★★★ elle porte la borne de l'étalon et son taux de faux",
      str(et["le_plus_petit_facteur_vu"]) in txt and _fr(et["le_taux_de_faux"], 4) in txt)
    v("★★★★ elle porte le diagnostic de l'aveugle — sans lui un taux d'aveugle non nul se lirait "
      "comme un défaut de la règle",
      _fr(et["la_ressemblance_mediane_des_aveugles_qui_tirent"], 4) in txt
      and _fr(et["la_ressemblance_mediane_des_aveugles_qui_se_taisent"], 4) in txt)
    v("★★★★ elle porte le piège nommé AVEC son sens attendu et son sens rendu",
      "ATTENDU" in txt and _fr(d["le_piege_nomme"]["la_correlation_energie_variance"], 4) in txt)
    v("★★★ elle porte le piège des covariables, qui dit que l'artefact ne porte rien",
      _fr(d["le_piege_des_covariables"]["la_plus_forte_en_valeur_absolue"], 4) in txt)
    v("★★★ elle dit qu'aucune lecture neuve du volume n'a eu lieu",
      "aucune lecture neuve du volume" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal — la prose du verdict vient du module "
      "au format de Python et doit être francisée AVANT d'être tracée",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    v("★★★ et la francisation ne touche QUE des décimales, jamais une fin de phrase",
      _decimales_fr("il plafonne à 0.0972. suite") == "il plafonne à 0,0972. suite")

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
                   / "le_residu_suit_il_ce_que_la_rangee_a_lu.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "215_le_residu_suit_il_ce_que_la_rangee_a_lu.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
