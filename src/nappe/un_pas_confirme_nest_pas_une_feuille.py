#!/usr/bin/env python3
"""Un pas confirmé garantit-il qu'UNE feuille a été franchie ? — la bande d'acceptation.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST UN CONTROLE QUI L'A IMPOSE PLUTOT QU'UN PLAN. La suite annoncee
apres `103` etait de relever la borne de `102` en payant trente pas au prix plein. En construisant
l'instrument qui devait le rendre lisible — un REGISTRE des feuilles franchies, l'equivalent gratuit
de ce que l'humain dit quand il corrige un transfert : « tu es sur la spire n » — le controle de
calibration a refute l'instrument au premier lancement, et en le refutant il a montre un defaut
bien plus lourd dans le critere de `102` lui-meme.

⛔⛔⛔ LE COMPTEUR D'INTERSTICES DE `98` NE SAIT PAS DIRE « MOINS D'UNE FEUILLE ». Sa famille de
gabarits est {1, 2, 3}, donc sa reponse ne peut jamais valoir zero : un segment qui ne franchit que
0,82 feuille rend « 1 interstice » avec un score de 0,781, tres au-dessus de la barre du bruit pur
(0,331). Le compteur voit un SAUT et il est AVEUGLE A UN RETARD.

⭐⭐⭐ ET C'EST LA CONSEQUENCE ENCHAINEE QUI DECIDE, comme dans `103` — mais dans l'autre sens, et
c'est pire. `103` chiffrait la conquence d'un TAUX D'ECHEC : une chute se voit. Ici il s'agit d'un
BIAIS : si un pas confirme ne franchit que `f` feuille, alors cent vingt pas confirmes n'en
franchissent que `120 f`, et **chaque pas est confirme**. Un deroulage qui se croit a la spire 120
serait a la spire 84, sans qu'aucune verification n'ait rien signale. Une chute est visible ; un
retard s'accumule en silence.

⭐⭐ LA BANDE EST MESUREE SUR DES PROFILS FABRIQUES, donc la reponse est connue et il n'y a aucun
referent humain. On balaie la fraction de feuille reellement franchie, on applique les TROIS
conditions de `102`, et on publie l'intervalle ou un pas ressort CONFIRME.

⭐⭐⭐ ET LE REMPLACANT EXISTE, CALIBRE, DANS `98` : `feuilles_franchies` estime la fraction sur une
famille CONTINUE, donc elle peut valoir moins de un. Elle reproduit `cos(theta)` a trois decimales
pres sur quatre obliquites fabriquees — c'est-a-dire qu'elle mesure exactement le retard que le
compteur entier ne voyait pas.

⭐ CE QUE CE FICHIER CHANGE DANS L'ORDRE DES CHOSES : la portee de `102` n'est PAS la prochaine
depense. Mesurer la forme de la survie d'un critere juste a 30 % pres, c'est mesurer la mauvaise
chose. Le registre passe devant.

Usage :
    uv run python src/nappe/un_pas_confirme_nest_pas_une_feuille.py --verifier
    uv run python src/nappe/un_pas_confirme_nest_pas_une_feuille.py \\
        --json docs/mesures/un_pas_confirme_nest_pas_une_feuille.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

PORTEE = RACINE / "docs" / "mesures" / "combien_de_pas_la_matiere_porte.json"

# ⚠ La grille de fractions balayees est declaree ici, avant tout resultat : un balayage qu'on
# resserre jusqu'a ce que la bande plaise serait le seuil regle sur ce qui passe.
FRACTIONS = np.round(np.arange(0.40, 1.81, 0.02), 3)
BRUITS = (0.0, 5.0, 15.0, 30.0)
TIRAGES = 200
SPIRES = 120


def profil_dune_fraction(f: float, bruit: float, tirages: int, graine: int,
                         sur_la_feuille: bool = True) -> np.ndarray:
    """Des segments FABRIQUES qui franchissent exactement `f` feuille, avec du bruit.

    ⚠ La phase de depart est celle d'un segment qui part SUR une feuille, ce qui est l'hypothese
    du marcheur : il vient d'atterrir sur une. Le cas oppose est balaye a part, parce qu'un
    marcheur a moitie decale est une panne DIFFERENTE et les melanger rendrait la bande illisible.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    r = np.random.default_rng(graine)
    t = np.linspace(0.0, 1.0, C.ECHANTILLONS)
    base = np.cos(2 * np.pi * float(f) * t)
    if not sur_la_feuille:
        base = -base
    v = 100.0 + 40.0 * base
    out = np.repeat(v.reshape(1, -1), tirages, axis=0)
    if bruit:
        out = out + r.normal(0.0, float(bruit), out.shape)
    return out


def bande_dacceptation(fractions=FRACTIONS, bruits=BRUITS, tirages: int = TIRAGES,
                       graine: int = 404) -> dict:
    """Pour quelles fractions de feuille reellement franchies un pas ressort-il CONFIRME ?

    ⭐⭐⭐ C'EST LE FICHIER ENTIER, ET IL EST FABRIQUE DONC SANS REFERENT. Les trois conditions de
    `102` sont appliquees telles quelles — un interstice compte, un accord au-dessus de la barre du
    bruit pur, et pas de butee — sur des segments dont on SAIT combien de feuille ils franchissent.
    La bande rendue est l'intervalle de fractions qu'un pas confirme peut cacher.

    ⚠ La butee du balayage de `99` n'entre pas ici : elle porte sur le choix de la LONGUEUR du pas,
    en amont, et ce fichier interroge la VERIFICATION en aval. Les melanger attribuerait a l'une le
    mode d'echec de l'autre.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    barre = max(x["p99"] for x in C.accord_du_bruit_pur().values())
    lignes = []
    for bruit in bruits:
        for i, f in enumerate(fractions):
            v = profil_dune_fraction(f, bruit, tirages, graine + i * 17 + int(bruit))
            combien, _, score, _ = C.accord(v)
            confirme = (combien == 1) & (score > barre)
            frac, sc_c, butee = C.feuilles_franchies(v)
            lignes.append({
                "bruit": float(bruit), "fraction_vraie": float(f),
                "part_confirmee": round(float(np.mean(confirme)), 3),
                "compte_median": int(np.median(combien)),
                "score_median": round(float(np.median(score)), 3),
                # ⭐ La fraction que l'estimateur CONTINU rend sur les memes segments : c'est la
                # comparaison qui montre que le retard est mesurable, pas seulement reel.
                "fraction_estimee_mediane": round(float(np.nanmedian(frac)), 3),
                "estimee_en_butee": round(float(np.mean(butee)), 3),
                "score_continu_median": round(float(np.nanmedian(sc_c)), 3)})
    out = {"barre_de_linterstice": round(float(barre), 4), "tirages": tirages,
           "spires": SPIRES, "lignes": lignes}
    return {**out, **verdict_de_la_bande(out)}


def verdict_de_la_bande(r: dict, part: float = 0.5) -> dict:
    """Les bornes de la bande, par niveau de bruit, et l'erreur de spire qu'elles entrainent.

    ⚠⚠ « CONFIRME » EST PRIS A LA MAJORITE DES TIRAGES, et le seuil est declare : une fraction
    confirmee une fois sur deux est deja une fraction qu'un marcheur accepte la moitie du temps.
    Prendre « au moins un tirage » ferait une bande absurdement large, prendre « tous » la ferait
    absurdement etroite ; la mediane est le seul point qui ne demande pas d'etre justifie apres
    coup.
    """
    out = {"par_bruit": []}
    for bruit in sorted({x["bruit"] for x in r["lignes"]}):
        j = [x for x in r["lignes"] if x["bruit"] == bruit]
        passe = [x["fraction_vraie"] for x in j if x["part_confirmee"] >= part]
        if not passe:
            out["par_bruit"].append({"bruit": bruit, "aucune_fraction_confirmee": True})
            continue
        bas, haut = min(passe), max(passe)
        # ⭐⭐⭐ LA CONSEQUENCE ENCHAINEE, ET C'EST LE CHIFFRE QUI DECIDE. Un pas confirme peut ne
        # franchir que `bas` feuille ; cent vingt pas confirmes n'en franchissent alors que
        # 120 x bas, et rien ne le signale puisque chaque pas est confirme.
        out["par_bruit"].append({
            "bruit": bruit, "fraction_basse": bas, "fraction_haute": haut,
            "largeur": round(haut - bas, 3),
            "spires_apres_120_pas_au_plus_bas": round(SPIRES * bas, 1),
            "spires_apres_120_pas_au_plus_haut": round(SPIRES * haut, 1),
            "erreur_de_spires_au_plus_bas": round(SPIRES * (1.0 - bas), 1),
            # ⚠ Un pas de 199 µm qui ne franchit que `bas` feuille veut dire que la feuille
            # franchie mesurait 199 / bas µm : la bande se lit aussi en microns.
            "pas_de_feuille_implique_um_bas": round(199.0 / haut, 1),
            "pas_de_feuille_implique_um_haut": round(199.0 / bas, 1)})
    vrais = [x for x in out["par_bruit"] if not x.get("aucune_fraction_confirmee")]
    if vrais:
        pire = max(vrais, key=lambda x: x["largeur"])
        out["fraction_la_plus_basse_confirmee"] = min(x["fraction_basse"] for x in vrais)
        out["largeur_maximale"] = pire["largeur"]
        # ⭐⭐ LE VERDICT : un pas confirme garantit-il UNE feuille ? Non des que la bande basse
        # s'ecarte de un de plus de ce que cent vingt spires tolerent — et cent vingt spires ne
        # tolerent presque rien, une spire d'erreur etant deja un texte decale d'une ligne.
        out["un_pas_confirme_garantit_une_feuille"] = bool(
            out["fraction_la_plus_basse_confirmee"] >= 0.99)
        out["erreur_de_spires_maximale_sur_120"] = round(
            SPIRES * (1.0 - out["fraction_la_plus_basse_confirmee"]), 1)
    return out


def le_compteur_est_aveugle_au_retard(fractions=(0.5, 0.7, 0.82, 1.0, 1.3),
                                      graine: int = 12) -> dict:
    """La preuve directe : le compteur entier ne descend jamais sous un, l'estimateur continu si.

    ⭐⭐ ELLE EST PUBLIEE PLUTOT QU'ASSERTEE DANS LA BATTERIE, et la difference compte : un lecteur
    doit voir, sur la meme page que le verdict, la ligne « 0,82 feuille franchie, compte rendu 1,
    score 0,781 » — sinon « le compteur est aveugle » se lit comme une opinion.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    barre = max(x["p99"] for x in C.accord_du_bruit_pur().values())
    out = []
    for f in fractions:
        v = profil_dune_fraction(f, 0.0, 1, graine)
        combien, _, score, _ = C.accord(v)
        frac, sc, bu = C.feuilles_franchies(v)
        out.append({"fraction_vraie": float(f), "compte_entier": int(combien[0]),
                    "score_entier": round(float(score[0]), 3),
                    "passe_la_barre": bool(score[0] > barre),
                    "fraction_estimee": round(float(frac[0]), 3),
                    "score_continu": round(float(sc[0]), 3),
                    "en_butee": bool(bu[0])})
    return {"barre_de_linterstice": round(float(barre), 4), "lignes": out,
            # ⭐ Les deux verdicts sont CALCULES, et chacun echoue differemment : le premier dit
            # que le compteur ne sait pas exprimer un retard, le second qu'il le laisse PASSER.
            "le_compteur_ne_descend_jamais_sous_un": bool(
                min(x["compte_entier"] for x in out) >= 1),
            "un_retard_passe_la_barre": bool(
                any(x["fraction_vraie"] < 0.95 and x["passe_la_barre"] for x in out)),
            "lestimateur_continu_le_voit": bool(
                all(abs(x["fraction_estimee"] - x["fraction_vraie"]) < 0.05
                    for x in out if not x["en_butee"]))}
def bornes_depuis_les_lignes(lignes: list[dict], pas_max: int, quoi: str = "matiere") -> dict:
    """Ce que les lignes DEJA PAYEES de `102` peuvent, et ne peuvent pas, dire de la survie.

    ⚠⚠⚠ ELLE EXISTE POUR JUSTIFIER UNE DEPENSE, ET ELLE LA JUSTIFIE EN AVOUANT UNE LIMITE. Une
    mediane de quatre valeurs livre la 2e et la 3e statistique d'ordre melangees : de `m` on tire
    seulement `a2 <= m <= a3`. Donc si `m >= k` on sait que DEUX cellules au moins passent le pas
    `k`, si `m < k` on sait qu'au plus DEUX le passent, et le maximum tranche la derniere. La
    survie n'est bornee qu'a deux cellules sur quatre pres.

    ⭐ C'est la lecon a retenir : **un agregat ne se desagrege pas**. Publier une mediane par bande
    detruit la forme de la distribution, et aucune relecture ne la rend. `102` a paye sept heures
    pour des marches dont les etapes existaient et n'ont pas ete ecrites.
    """
    n = sum(x["cellules"] for x in lignes)
    courbe = []
    for k in range(1, pas_max + 1):
        bas = haut = 0
        for x in lignes:
            m = x.get(f"pas_confirmes_median_{quoi}")
            mx = x.get(f"pas_confirmes_max_{quoi}")
            if m is None or mx is None:
                continue
            c = x["cellules"]
            if m >= k:
                # a3 >= m >= k et a4 >= a3 : au moins deux cellules passent, au plus toutes.
                bas += 2
                haut += c
            elif mx >= k:
                # a2 <= m < k donc a1 et a2 tombent ; a3 est indecidable, a4 passe.
                haut += 2
            # k > max : aucune cellule ne passe, les deux bornes sont nulles.
        courbe.append({"pas": k, "survie_basse": round(bas / n, 3),
                       "survie_haute": round(haut / n, 3),
                       "largeur": round((haut - bas) / n, 3)})
    # ⭐⭐ LE VERDICT EST CALCULE : deux hypotheses opposees sont-elles TOUTES DEUX dans la bande ?
    # Si oui, ces lignes ne decident rien et la depense est justifiee. Si non, elle ne l'est pas.
    prem, dern = courbe[0], courbe[-1]
    risque_constant_max = (1.0 - (dern["survie_basse"] / prem["survie_haute"])
                           ** (1.0 / max(pas_max - 1, 1))
                           if prem["survie_haute"] > 0 and dern["survie_basse"] > 0 else 1.0)
    risque_constant_min = (1.0 - (dern["survie_haute"] / max(prem["survie_basse"], 1e-9))
                           ** (1.0 / max(pas_max - 1, 1))
                           if prem["survie_basse"] > 0 else 0.0)
    return {
        "cellules": n, "pas_max": pas_max, "courbe": courbe,
        "largeur_maximale": max(x["largeur"] for x in courbe),
        "risque_par_pas_compatible_de": round(max(min(risque_constant_min, 1.0), 0.0), 3),
        "risque_par_pas_compatible_a": round(max(min(risque_constant_max, 1.0), 0.0), 3),
        # ⚠ « Ne decide rien » veut dire : la bande contient a la fois un risque qui s'effondre
        # (proche de zero) et un risque fort. C'est un enonce sur la LARGEUR, pas sur une valeur.
        "ces_lignes_ne_decident_pas_la_forme": bool(
            max(x["largeur"] for x in courbe) > 0.2),
        "pourquoi": "une médiane par bande ne se désagrège pas : de m on ne tire que a2 <= m <= a3",
    }


def budget(bandes: int, cellules: int, pas: int, secondes_par_cube: float,
           plancher_s: float = 3.76) -> dict:
    """Le prix de la course, chiffre AVANT de la lancer, depuis le cout mesure par `103`.

    ⭐⭐ ELLE EXISTE PARCE QUE `102` A DECOUVERT SON PRIX APRES SEPT HEURES. `103` a mesure qu'un
    cube coute 15,4 s et qu'un plancher de 3,76 s ne descend jamais ; une course se chiffre donc
    d'avance, et le chiffre entre dans le document a cote du resultat.

    ⚠ Le marcheur lit un cube par pas ET deux segments (le balayage qui decide, le gabarit qui
    verifie). Les segments sont des lignes 1-D, donc domines par le plancher par requete et non
    par leur longueur — c'est pour ca qu'ils entrent comme un plancher et non comme un volume.
    """
    marches = bandes * cellules
    etapes = marches * pas
    s = etapes * (secondes_par_cube + 2.0 * plancher_s)
    return {"marches": marches, "etapes": etapes,
            "secondes_par_cube": round(secondes_par_cube, 2),
            "plancher_par_segment_s": plancher_s,
            "secondes_par_etape": round(secondes_par_cube + 2.0 * plancher_s, 2),
            "heures": round(s / 3600.0, 2)}


def _lignes_de_102() -> tuple[list[dict], int] | None:
    if not PORTEE.is_file():
        return None
    r = json.loads(PORTEE.read_text())
    lignes = [x for x in r["lignes"]
              if x.get("pas_confirmes_median_matiere") is not None]
    return (lignes, int(r["pas_max"])) if lignes else None


def ce_que_la_bande_ne_distingue_pas(bande: dict, bruit: float = 15.0) -> dict:
    """Quels pas DEJA PUBLIES par la campagne la bande d'acceptation confond-elle ?

    ⭐⭐⭐ ELLE RELIE CE FICHIER A LA QUESTION OUVERTE DE `99`, ET LE LIEN EST DERIVE. Depuis `99`
    la campagne traine un ecart de 21 % entre le pas que la matiere montre (198,9 µm) et celui des
    transferts humains (164,0) ; `100` a refute l'obliquite comme explication et `101` a confirme
    que l'obliquite est reelle sans expliquer l'ecart. Cette fonction ne l'explique pas davantage
    — mais elle dit ce qu'aucune des trois ne disait : le critere de verification ACCEPTE les deux,
    et une bonne partie de ce qui les entoure. On ne peut donc pas argumenter sur le pas a partir
    d'un pas confirme.

    ⚠ Les valeurs comparees sont LUES dans les mesures versionnees, jamais recopiees : un chiffre
    tape ici cesserait de suivre la mesure qui le produit.
    """
    src = {}
    p = RACINE / "docs" / "mesures" / "le_pas_que_la_matiere_montre.json"
    if p.is_file():
        r = json.loads(p.read_text())
        src["nominal"] = r["pas_nominal_um"]
        src["que_la_matiere_montre"] = r["la_longueur_differe_du_nul"]["mediane_reelle_um"]
        bord = r.get("par_tiers", {}).get("bord", {})
        if bord.get("pas_median_um"):
            src["que_la_matiere_montre_au_bord"] = bord["pas_median_um"]
    p = RACINE / "docs" / "mesures" / "deux_humains_sur_la_meme_matiere.json"
    if p.is_file():
        src["des_transferts_humains"] = json.loads(p.read_text())["pas_um"]
    ligne = next((x for x in bande.get("par_bruit", [])
                  if x.get("bruit") == bruit and not x.get("aucune_fraction_confirmee")), None)
    if ligne is None or not src:
        return {"message": "bande ou mesures antérieures absentes"}
    bas, haut = ligne["pas_de_feuille_implique_um_bas"], ligne["pas_de_feuille_implique_um_haut"]
    dedans = {k: bool(bas <= v <= haut) for k, v in src.items()}
    return {"bruit": bruit, "pas_impliques_um": [bas, haut], "pas_publies_um": src,
            "dans_la_bande": dedans,
            # ⭐⭐ LE VERDICT : la bande confond-elle les pas que la campagne oppose depuis `99` ?
            "la_bande_confond_les_pas_publies": bool(sum(dedans.values()) >= 2),
            "combien_de_pas_publies_confondus": int(sum(dedans.values())),
            "ecart_publie_par_99_en_pourcent": (
                round(100.0 * (src["que_la_matiere_montre"] / src["des_transferts_humains"] - 1.0), 1)
                if "que_la_matiere_montre" in src and "des_transferts_humains" in src else None),
            "largeur_de_la_bande_en_pourcent": round(100.0 * (haut / bas - 1.0), 1)}


def mesurer(fractions=FRACTIONS, bruits=BRUITS, tirages: int = TIRAGES) -> dict:
    """Tout est FABRIQUE : ce fichier ne lit pas une seule fois le volume distant.

    ⭐⭐ ET C'EST SA FORCE, PAS SA LIMITE. La question porte sur le CRITERE, pas sur le rouleau :
    elle se tranche sur des segments dont on connait la reponse. `103` a montre qu'un bord se
    compte sur le corpus entier ; ici il n'y a pas de bord a compter, il y a un instrument a
    calibrer, et un instrument se calibre sur du connu.
    """
    r = {"question": "un pas confirmé garantit-il qu'une feuille a été franchie ?",
         "aucune_lecture_distante": True,
         "bande": bande_dacceptation(fractions, bruits, tirages),
         "aveuglement": le_compteur_est_aveugle_au_retard()}
    r["ce_que_la_bande_ne_distingue_pas"] = ce_que_la_bande_ne_distingue_pas(r["bande"])
    b = _lignes_de_102()
    # ⚠ Les deux blocs ci-dessous ne repondent PAS a la question du fichier : ils disent pourquoi
    # la mesure de portee, qui etait la suite annoncee, passe DERRIERE. Les garder ici plutot que
    # de les jeter evite d'avoir a redecouvrir le chiffrage au prochain tour.
    r["ce_que_102_pouvait_dire_de_la_forme"] = (
        bornes_depuis_les_lignes(*b) if b else {"message": "mesure de `102` absente"})
    r["prix_de_la_mesure_de_portee"] = {
        "en_couverture_28x3x10": budget(28, 3, 10, 15.4),
        "en_profondeur_28x1x30": budget(28, 1, 30, 15.4)}
    return agreger(r)


def agreger(r: dict) -> dict:
    """Le verdict, DERIVE des trois blocs — meme partage que `100` a `103`."""
    b = r["bande"]
    a = r["aveuglement"]
    r["resume"] = {
        "un_pas_confirme_garantit_une_feuille": b.get("un_pas_confirme_garantit_une_feuille"),
        "fraction_la_plus_basse_confirmee": b.get("fraction_la_plus_basse_confirmee"),
        "erreur_de_spires_maximale_sur_120": b.get("erreur_de_spires_maximale_sur_120"),
        "largeur_maximale_de_la_bande": b.get("largeur_maximale"),
        "le_compteur_ne_descend_jamais_sous_un": a["le_compteur_ne_descend_jamais_sous_un"],
        "un_retard_passe_la_barre": a["un_retard_passe_la_barre"],
        "lestimateur_continu_le_voit": a["lestimateur_continu_le_voit"],
        "combien_de_pas_publies_confondus": r.get(
            "ce_que_la_bande_ne_distingue_pas", {}).get("combien_de_pas_publies_confondus"),
        # ⭐⭐⭐ LE VERDICT D'ORDONNANCEMENT, ET IL EST DERIVE : la portee ne passe devant que si
        # le critere garantit une feuille. Il ne la garantit pas, donc le registre passe devant.
        "la_portee_est_la_prochaine_depense": bool(
            b.get("un_pas_confirme_garantit_une_feuille") is True),
    }
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    a = r["aveuglement"]
    print(f"LE COMPTEUR ENTIER CONTRE L'ESTIMATEUR CONTINU "
          f"(barre du bruit pur {a['barre_de_linterstice']})")
    print(" feuille vraie   compte entier   score   passe ?   fraction estimée   butée")
    for x in a["lignes"]:
        print(f"     {x['fraction_vraie']:5.2f}            {x['compte_entier']:3d}       "
              f"{x['score_entier']:.3f}    {'OUI' if x['passe_la_barre'] else 'non':>3}"
              f"          {x['fraction_estimee']:6.3f}       "
              f"{'BUTÉE' if x['en_butee'] else '-'}")
    print(f"   ⛔ le compteur ne descend jamais sous un : "
          f"{a['le_compteur_ne_descend_jamais_sous_un']}")
    print(f"   ⛔⛔ et un retard PASSE la barre : {a['un_retard_passe_la_barre']}")
    print(f"   ★★★ l'estimateur continu le voit : {a['lestimateur_continu_le_voit']}")

    b = r["bande"]
    print("\nLA BANDE D'ACCEPTATION DU CRITÈRE DE `102`, par niveau de bruit")
    print(" bruit   fraction basse   haute   largeur   spires après 120 pas   "
          "pas de feuille impliqué")
    for x in b.get("par_bruit", []):
        if x.get("aucune_fraction_confirmee"):
            print(f" {x['bruit']:5.1f}   aucune fraction confirmée")
            continue
        print(f" {x['bruit']:5.1f}      {x['fraction_basse']:.3f}       "
              f"{x['fraction_haute']:.3f}    {x['largeur']:.3f}      "
              f"{x['spires_apres_120_pas_au_plus_bas']:5.1f} à "
              f"{x['spires_apres_120_pas_au_plus_haut']:5.1f}        "
              f"{x['pas_de_feuille_implique_um_bas']:5.1f} à "
              f"{x['pas_de_feuille_implique_um_haut']:5.1f} µm")
    s = r.get("resume", {})
    if s.get("fraction_la_plus_basse_confirmee") is not None:
        print(f"\n★★★ UN PAS CONFIRMÉ NE GARANTIT PAS UNE FEUILLE : la plus basse fraction "
              f"confirmée est {s['fraction_la_plus_basse_confirmee']:.2f},")
        print(f"    donc cent vingt pas tous confirmés peuvent n'avoir franchi que "
              f"{120 * s['fraction_la_plus_basse_confirmee']:.0f} spires —")
        print(f"    une erreur de {s['erreur_de_spires_maximale_sur_120']:.0f} spires que "
              f"RIEN ne signale, puisque chaque pas est confirmé.")
        print("\n⚠⚠ ET C'EST PIRE QU'UN TAUX D'ÉCHEC : `103` chiffrait la conséquence d'une "
              "CHUTE, qui se voit.\n    Un retard s'accumule en silence.")

    d = r.get("ce_que_la_bande_ne_distingue_pas", {})
    if d.get("pas_publies_um"):
        print(f"\nCE QUE LA BANDE NE DISTINGUE PAS — pas de feuille impliqué "
              f"{d['pas_impliques_um'][0]} à {d['pas_impliques_um'][1]} µm "
              f"(soit ±{d['largeur_de_la_bande_en_pourcent']:.0f} %)")
        for k, val in d["pas_publies_um"].items():
            print(f"   {k:32s} {val:7.1f} µm   "
                  f"{'DANS la bande' if d['dans_la_bande'][k] else 'hors'}")
        print(f"   ⛔ la bande confond {d['combien_de_pas_publies_confondus']} des pas publiés, "
              f"dont l'écart de {d['ecart_publie_par_99_en_pourcent']} % que `99` laisse ouvert")

    c = r.get("ce_que_102_pouvait_dire_de_la_forme", {})
    if c.get("courbe"):
        print(f"\nPOURQUOI LA PORTÉE PASSE DERRIÈRE — les lignes de `102` bornent la survie à "
              f"{c['largeur_maximale']} près,")
        print(f"   donc un risque par pas CONSTANT de {c['risque_par_pas_compatible_de']:.3f} à "
              f"{c['risque_par_pas_compatible_a']:.3f} y est compatible.")
        print(f"   ⚠ {c['pourquoi']}")
    p = r.get("prix_de_la_mesure_de_portee", {})
    for nom, x in p.items():
        print(f"   {nom} : {x['marches']} marches, {x['etapes']} étapes, {x['heures']} h")
    if s:
        print(f"\n★ LA PORTÉE EST-ELLE LA PROCHAINE DÉPENSE ? "
              f"{'oui' if s['la_portee_est_la_prochaine_depense'] else 'NON — le registre passe devant'}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === LA FIXTURE DOIT FABRIQUER CE QU'ELLE ANNONCE =======================================
    # ⚠⚠⚠ SANS CE CONTROLE TOUT LE RESTE EST NUL. Si le profil fabrique ne franchit pas la
    # fraction annoncee, la bande mesure ma propre erreur de mise en place — le defaut que la
    # fixture de `100` a paye, et qui avait rendu 242 µm pour 173 injectes.
    for f in (0.6, 0.82, 1.0, 1.4):
        frac, _, bu = C.feuilles_franchies(profil_dune_fraction(f, 0.0, 1, 7))
        v(f"le profil fabriqué franchit bien {f} feuille",
          abs(float(frac[0]) - f) < 0.01 and not bool(bu[0]), f"{float(frac[0]):.3f}")
    # ⚠ Et la polarite OPPOSEE doit etre fabricable aussi, sinon la moitie des cas du marcheur
    # — celui qui atterrit dans un interstice — ne serait jamais exercee.
    a = profil_dune_fraction(0.82, 0.0, 1, 7, sur_la_feuille=True)
    b = profil_dune_fraction(0.82, 0.0, 1, 7, sur_la_feuille=False)
    v("les deux polarités sont fabricables et distinctes",
      float(np.corrcoef(a[0], b[0])[0, 1]) < -0.99,
      f"corrélation {float(np.corrcoef(a[0], b[0])[0, 1]):.3f}")
    v("... et l'estimateur continu rend la même fraction sur les deux",
      abs(float(C.feuilles_franchies(a)[0][0]) - float(C.feuilles_franchies(b)[0][0])) < 0.01)
    # ⚠ Le bruit doit reellement bruiter, sinon les colonnes « bruit » de la bande seraient
    # quatre copies d'une meme mesure.
    v("le bruit demandé est réellement appliqué",
      float(np.std(profil_dune_fraction(1.0, 30.0, 200, 3)
                   - profil_dune_fraction(1.0, 0.0, 200, 3))) > 20.0)

    # === L'AVEUGLEMENT DU COMPTEUR ENTIER ====================================================
    a = le_compteur_est_aveugle_au_retard()
    v("le compteur entier ne descend jamais sous un interstice",
      a["le_compteur_ne_descend_jamais_sous_un"] is True,
      str([x["compte_entier"] for x in a["lignes"]]))
    # ⛔⛔ ET C'EST CELUI-LA QUI COMPTE : un retard ne se contente pas d'etre inexprimable, il
    # PASSE la barre du bruit pur, donc il ressort CONFIRME.
    v("... et un retard réel passe quand même la barre du bruit pur",
      a["un_retard_passe_la_barre"] is True,
      str([(x["fraction_vraie"], x["score_entier"]) for x in a["lignes"]
           if x["fraction_vraie"] < 0.95]))
    v("l'estimateur continu, lui, rend la fraction vraie",
      a["lestimateur_continu_le_voit"] is True)

    # === LA BANDE D'ACCEPTATION ==============================================================
    # ⚠ Balayage court pour la batterie : la forme du verdict est verifiee, pas sa valeur
    # publiee, qui demande la grille complete.
    r = bande_dacceptation(fractions=(0.5, 0.7, 0.9, 1.0, 1.1, 1.4),
                           bruits=(0.0, 15.0), tirages=40)
    v("la bande est rendue par niveau de bruit",
      len(r["par_bruit"]) == 2, str([x["bruit"] for x in r["par_bruit"]]))
    haut = next(x for x in r["par_bruit"] if x["bruit"] == 0.0)
    v("la fraction exacte de UNE feuille est confirmée",
      haut["fraction_basse"] <= 1.0 <= haut["fraction_haute"],
      f"[{haut['fraction_basse']}, {haut['fraction_haute']}]")
    # ⭐⭐⭐ LE CONTROLE QUI REND LE VERDICT HONNETE : la bande doit etre STRICTEMENT plus large
    # qu'un point. Si elle ne contenait que 1,0, le critere de `102` serait exact et ce fichier
    # n'aurait rien a dire — donc ce controle peut echouer, et c'est ce qui lui donne un sens.
    v("... et la bande est strictement plus large qu'un point",
      haut["largeur"] > 0.0, f"largeur {haut['largeur']}")
    # ⭐⭐ LA CONSEQUENCE ENCHAINEE EST PUBLIEE A COTE DE LA BANDE, jamais toute seule.
    v("la conséquence sur cent vingt spires est publiée à côté de la bande",
      haut["spires_apres_120_pas_au_plus_bas"] == round(SPIRES * haut["fraction_basse"], 1),
      f"{haut['spires_apres_120_pas_au_plus_bas']} spires pour "
      f"{haut['fraction_basse']} feuille par pas")
    # ⚠ Et la bande se lit aussi en microns : un pas de 199 µm qui ne franchit que `f` feuille
    # veut dire que la feuille franchie mesurait 199/f µm.
    v("... et la bande est traduite en pas de feuille impliqué",
      abs(haut["pas_de_feuille_implique_um_haut"]
          - round(199.0 / haut["fraction_basse"], 1)) < 1e-9)
    # ⚠⚠ LE VERDICT DOIT POUVOIR DIRE OUI. Un critere parfait — une bande reduite a 1,0 — doit
    # rendre « oui », sinon le verdict est un non deguise et il ne mesure rien.
    parfait = {"lignes": [{"bruit": 0.0, "fraction_vraie": f, "part_confirmee": (1.0 if f == 1.0 else 0.0),
                           "compte_median": 1, "score_median": 1.0,
                           "fraction_estimee_mediane": f, "estimee_en_butee": 0.0,
                           "score_continu_median": 1.0} for f in (0.7, 1.0, 1.3)]}
    vp = verdict_de_la_bande(parfait)
    v("un critère parfait ferait rendre OUI au verdict",
      vp["un_pas_confirme_garantit_une_feuille"] is True,
      f"fraction basse {vp['fraction_la_plus_basse_confirmee']}")
    v("... et son erreur de spires serait nulle",
      vp["erreur_de_spires_maximale_sur_120"] == 0.0)
    # ⚠ Un critere qui ne confirme RIEN doit etre dit tel quel, jamais rendu comme une bande vide
    # dont on lirait « parfait ».
    rien = {"lignes": [{"bruit": 0.0, "fraction_vraie": f, "part_confirmee": 0.0,
                        "compte_median": 1, "score_median": 0.0,
                        "fraction_estimee_mediane": f, "estimee_en_butee": 0.0,
                        "score_continu_median": 0.0} for f in (0.7, 1.0, 1.3)]}
    v("un critère qui ne confirme rien est dit tel quel, pas rendu comme parfait",
      verdict_de_la_bande(rien)["par_bruit"][0].get("aucune_fraction_confirmee") is True
      and "un_pas_confirme_garantit_une_feuille" not in verdict_de_la_bande(rien))

    # === CE QUE LA BANDE CONFOND ============================================================
    # ⭐⭐⭐ LE LIEN AVEC LA QUESTION OUVERTE DEPUIS `99`, et il doit etre DERIVE des mesures
    # versionnees et non tape. Un chiffre recopie ici cesserait de suivre la mesure qui le produit.
    large = {"par_bruit": [{"bruit": 15.0, "fraction_basse": 0.7, "fraction_haute": 1.36,
                            "largeur": 0.66, "pas_de_feuille_implique_um_bas": 146.3,
                            "pas_de_feuille_implique_um_haut": 284.3}]}
    d = ce_que_la_bande_ne_distingue_pas(large)
    if "message" in d:
        v("la bande est confrontée aux pas publiés", False, d["message"])
    else:
        v("la bande confond les pas que la campagne oppose depuis `99`",
          d["la_bande_confond_les_pas_publies"] is True,
          f"{d['combien_de_pas_publies_confondus']} pas dans "
          f"{d['pas_impliques_um']} µm : {d['pas_publies_um']}")
        # ⚠⚠ ET LA COMPARAISON QUI COMPTE : la bande est-elle plus large que l'ecart que `99`
        # laisse ouvert ? Si elle ne l'etait pas, le critere pourrait servir a trancher l'ecart.
        v("... et elle est plus large que l'écart de `99` lui-même",
          d["largeur_de_la_bande_en_pourcent"] > abs(d["ecart_publie_par_99_en_pourcent"]),
          f"±{d['largeur_de_la_bande_en_pourcent']} % contre "
          f"{d['ecart_publie_par_99_en_pourcent']} %")
        # ⭐ Et le verdict doit pouvoir dire NON : une bande etroite ne confondrait rien.
        etroite = {"par_bruit": [{"bruit": 15.0, "pas_de_feuille_implique_um_bas": 172.0,
                                  "pas_de_feuille_implique_um_haut": 174.0}]}
        v("... et une bande étroite ne confondrait qu'un seul pas",
          ce_que_la_bande_ne_distingue_pas(etroite)["combien_de_pas_publies_confondus"] == 1,
          str(ce_que_la_bande_ne_distingue_pas(etroite)["dans_la_bande"]))

    # === LA BORNE TIREE DES LIGNES DE `102` DOIT ETRE UNE BORNE ==============================
    # ⭐⭐⭐ On FABRIQUE des bandes dont on connait les comptes par cellule, on les agrege comme
    # `102` l'a fait (mediane + maximum), et la survie VRAIE doit tomber dans la bande rendue.
    # Une borne qui n'encadre pas est pire qu'une absence de borne.
    rng = np.random.default_rng(11)
    dedans = total = 0
    for _ in range(120):
        comptes = [sorted(int(x) for x in rng.integers(0, 7, 4)) for _ in range(28)]
        lignes = [{"cellules": 4,
                   "pas_confirmes_median_matiere": (c[1] + c[2]) / 2.0,
                   "pas_confirmes_max_matiere": c[3]} for c in comptes]
        bo = bornes_depuis_les_lignes(lignes, 6)
        n = 28 * 4
        for x in bo["courbe"]:
            vrai = sum(1 for c in comptes for q in c if q >= x["pas"]) / n
            total += 1
            dedans += 1 if x["survie_basse"] - 1e-9 <= vrai <= x["survie_haute"] + 1e-9 else 0
    v("la borne tirée des médianes de `102` encadre TOUJOURS la survie vraie",
      dedans == total, f"{dedans}/{total} points encadrés")
    b102 = _lignes_de_102()
    v("... et sur les vraies lignes elle est trop large pour décider de la forme",
      bool(b102) and bornes_depuis_les_lignes(*b102)["ces_lignes_ne_decident_pas_la_forme"],
      f"largeur maximale {bornes_depuis_les_lignes(*b102)['largeur_maximale']}"
      if b102 else "mesure de `102` absente")

    # === LE PRIX DE LA MESURE QUI PASSE DERRIERE =============================================
    bu = budget(28, 3, 10, 15.4)
    v("le prix de la mesure de portée est chiffré depuis le coût mesuré par `103`",
      bu["etapes"] == 840 and bu["heures"] == round(840 * (15.4 + 2 * 3.76) / 3600.0, 2),
      f"{bu['etapes']} étapes, {bu['heures']} h")
    v("... et les deux allocations coûtent le même prix pour trois fois moins de marches",
      budget(28, 1, 30, 15.4)["heures"] == bu["heures"]
      and budget(28, 1, 30, 15.4)["marches"] * 3 == bu["marches"],
      f"{budget(28, 1, 30, 15.4)['marches']} marches contre {bu['marches']}")

    # === L'ORDONNANCEMENT EST DERIVE, PAS DECRETE ============================================
    faux = {"bande": {**rien, **verdict_de_la_bande(parfait)},
            "aveuglement": a,
            "ce_que_102_pouvait_dire_de_la_forme": {},
            "prix_de_la_mesure_de_portee": {}}
    v("si le critère garantissait une feuille, la portée redeviendrait la prochaine dépense",
      agreger(faux)["resume"]["la_portee_est_la_prochaine_depense"] is True)
    faux["bande"] = {**rien, **verdict_de_la_bande(
        {"lignes": [{"bruit": 0.0, "fraction_vraie": f, "part_confirmee": 1.0,
                     "compte_median": 1, "score_median": 1.0,
                     "fraction_estimee_mediane": f, "estimee_en_butee": 0.0,
                     "score_continu_median": 1.0} for f in (0.7, 1.0, 1.3)]})}
    v("... et il ne l'est pas quand la bande est large",
      agreger(faux)["resume"]["la_portee_est_la_prochaine_depense"] is False,
      f"fraction basse {faux['bande']['fraction_la_plus_basse_confirmee']}")
    v("l'affichage tourne sur ce résultat", afficher(agreger(faux)) is None)

    print(("ALL PASS" if echecs == 0 else "FAILURES")
          + f" ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--tirages", type=int, default=TIRAGES)
    p.add_argument("--reagreger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = json.loads(a.json.read_text())
        # ⚠ Seul le verdict est refait : les lignes de balayage ne sont jamais retouchees.
        r["bande"] = {**r["bande"], **verdict_de_la_bande(r["bande"])}
        r = agreger(r)
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    r = mesurer(tirages=a.tirages)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
