"""Le cap agit-il sur les deux axes ? — et `R4-P27` comparait deux populations inégales.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL COMMENCE PAR REFUSER LA PREMISSE DE SA PROPRE PORTE. `R4-P27`
demande pourquoi une fixture calibrée sur le vrai rapport des axes marche DEUX FOIS TROP
azimutalement. Deux nombres déjà publiés par `169` disent qu'elle ne le fait pas : SANS cap la
fixture rend **0,308** de part azimutale là où le rouleau en rend **0,405**, donc elle est EN
DESSOUS. L'écart n'apparaît qu'AVEC le cap, et il ne dit alors rien de l'écrasement : il dit que le
cap ne fait pas la même chose aux deux matières.

⚠⚠⚠ ET LA COMPARAISON DES DEUX CAPS DU ROULEAU EST FAITE SUR DEUX POPULATIONS INEGALES. Les deux
courses stockées ne portent pas le même nombre de bandes — neuf sans cap, treize avec — et les
médianes publiées les comparent telles quelles. C'est le péché capital de ce dépôt, et il est ici
RÉPARABLE plutôt que fatal : les neuf bandes de la course sans cap sont toutes présentes dans les
treize de l'autre, donc l'appariement existe. Ce module rend les DEUX lectures côte à côte, et
c'est l'écart entre elles qui se mesure.

⭐⭐⭐⭐ ET LA COHERENCE SE DECOMPOSE PAR AXE, PARCE QU'ELLE MOYENNE SUR L'AXE OU LA DIFFERENCE VIT.
`coherence_tangentielle` est la norme d'une somme de vecteurs : une marche dont la part axiale tient
son signe et dont l'azimutale alterne rend le même nombre que son miroir. Or c'est exactement l'axe
sur lequel le rouleau et la fixture peuvent différer. `coherence_dun_axe` pose la même idée sur UN
axe, et les deux nombres sont rendus À CÔTÉ de la cohérence tangentielle, jamais à sa place.

⚠⚠ LE MEME LECTEUR DES DEUX COTES. Une marche du rouleau et une marche de la fixture passent toutes
deux par `le_cote_dune_marche` de `169` — le seul endroit du dépôt qui nomme les quatre grandeurs
d'une marche. Deux lecteurs seraient deux réponses à « qu'est-ce qu'une marche rend », libres de
diverger sur le nom d'un axe.

⚠⚠ L'APPARIEMENT DE LA FIXTURE EST EXACT PAR CONSTRUCTION : chaque départ est marché aux DEUX caps.
Le défaut de population n'existe donc que du côté du rouleau, et c'est pour cela qu'il n'avait aucune
raison d'être vu depuis la fixture.

⚠ CONTROLE OBLIGATOIRE ET VIDE : sur la spirale nue les deux axes ne portent rien — les cohérences
par axe y valent `None` — donc le lien entre cohérence et effet du cap n'y est PAS posable. À dire,
jamais à chiffrer.

Usage :
    uv run python src/nappe/le_cap_agit_il_sur_les_deux_axes.py --verifier
    uv run python src/nappe/le_cap_agit_il_sur_les_deux_axes.py \\
        --json docs/mesures/le_cap_agit_il_sur_les_deux_axes.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_fixture_penche_t_elle_du_meme_cote import (CAPS, DEPARTS,  # noqa: E402
                                                   PAS_MAX, RAYON_MM,
                                                   le_cote_dune_marche, lenquete)
from la_pince_tient_elle_la_feuille import MATIERES, _nom  # noqa: E402
from le_chemin_penche_t_il_ou_serpente_t_il import mesurer as mesurer_le_rouleau  # noqa: E402

# ⚠ Les quatre grandeurs d'une marche, sous les noms que `le_cote_dune_marche` leur donne. Les
# ecrire ici une fois evite qu'un axe soit lu sous le nom de l'autre dans un seul des deux camps.
LES_AXES = ("axial", "azimutal")
LA_COHERENCE_DUN_AXE = {"axial": "coherence_axiale", "azimutal": "coherence_azimutale"}


def le_rouleau_par_cap() -> dict | None:
    """Les marches du VRAI rouleau aux deux caps, et les bandes que les deux courses partagent.

    ⚠⚠⚠ RIEN N'EST RECALCULE SUR LE VOLUME. `penchant` travaille sur des pas DEJA STOCKES — la
    direction et l'avance de chaque pas sont dans les courses — donc cette lecture coûte une
    seconde là où produire les courses a coûté des heures. Ce qui serait interdit, et ne l'est pas
    ici, serait de refaire la course.

    ⚠⚠ L'APPARIEMENT SE FAIT SUR LA BANDE, parce que c'est ce qu'une marche traverse. Deux marches
    de bandes différentes ne sont pas deux essais de la même chose : elles lisent deux endroits du
    rouleau, et le penchant y dépend de l'endroit.
    """
    r = mesurer_le_rouleau(avec_fixture=False)
    par_cap: dict[float, dict[tuple, dict]] = {}
    sources: dict[float, str] = {}
    for c in r.get("par_course") or []:
        cap = c.get("memoire_du_cap")
        if cap is None:
            continue
        sources[float(cap)] = str(c.get("source"))
        par_cap[float(cap)] = {tuple(m["bande"]): m for m in c.get("marches") or []
                               if m.get("bande") is not None}
    if len(par_cap) < 2:
        return None
    caps = sorted(par_cap)
    communes = sorted(set(par_cap[caps[0]]) & set(par_cap[caps[1]]))
    return {"caps": caps, "sources": sources, "par_cap": par_cap,
            "bandes_communes": [list(b) for b in communes],
            "bandes_par_cap": {str(c): len(par_cap[c]) for c in caps},
            # ⚠ La reparabilite est un FAIT, pas une hypothese : elle tient si et seulement si la
            # course la plus courte est incluse dans l'autre. Si elle ne l'etait pas, l'appariement
            # jetterait des bandes des DEUX cotes et ce module devrait le dire.
            "la_plus_courte_est_incluse": bool(
                set(par_cap[caps[0]]) <= set(par_cap[caps[1]])
                or set(par_cap[caps[1]]) <= set(par_cap[caps[0]]))}


def resumer(marches: list[dict | None]) -> dict:
    """Les cinq médianes d'un lot de marches, et ce que chaque axe a dû taire.

    ⚠⚠ UNE COHERENCE ABSENTE SE COMPTE, ELLE NE SE REMPLACE PAS. Une marche dont un axe ne porte
    rien rend `None` sur cet axe ; la traiter comme un zéro ferait lire du silence comme un
    serpentement parfait, et la traiter comme un un ferait lire du silence comme une dérive.
    """
    dec = [m for m in marches if m is not None]
    if not dec:
        return {"decidable": False, "raison": "aucune marche décidable", "marches": len(marches)}
    out = {"decidable": True, "marches": len(marches), "decidables": len(dec),
           "axial_median": round(float(statistics.median([m["axial"] for m in dec])), 3),
           "azimutal_median": round(float(statistics.median([m["azimutal"] for m in dec])), 3),
           "coherence_median": round(float(statistics.median([m["coherence"] for m in dec])), 3)}
    for axe in LES_AXES:
        cle = LA_COHERENCE_DUN_AXE[axe]
        lus = [float(m[cle]) for m in dec if m.get(cle) is not None]
        out[f"coherence_{axe}e_mediane"] = (round(float(statistics.median(lus)), 3) if lus
                                            else None)
        out[f"marches_ou_l_{axe}_ne_porte_rien"] = int(len(dec) - len(lus))
    return out


def _rapport(sans: float, avec: float) -> float | None:
    """`avec / sans`, ou `None` quand il n'y a rien à diviser.

    ⚠⚠ UN RAPPORT SUR ZERO N'EST PAS UN GRAND RAPPORT, c'est une absence de question. La spirale
    nue rend une part axiale exactement nulle, et rendre l'infini y ferait passer le contrôle vide
    pour la matière la plus sensible au cap du lot.
    """
    if sans == 0.0:
        return None
    return round(avec / sans, 3)


def leffet_du_cap(sans: dict, avec: dict) -> dict:
    """Ce que le cap fait à chaque axe : le rapport de la part avec cap à la part sans cap.

    ⭐ UN RAPPORT PAR AXE, JAMAIS UN SEUL CHIFFRE. Un cap qui prendrait autant à l'un qu'à l'autre
    et un cap qui prendrait tout à l'un rendent la même moyenne, et c'est précisément la question.
    """
    if not (sans.get("decidable") and avec.get("decidable")):
        return {"decidable": False, "raison": "un des deux caps n'a aucune marche décidable"}
    out = {"decidable": True}
    for axe in LES_AXES:
        out[f"part_{axe}e_sans_cap"] = sans[f"{axe}_median"]
        out[f"part_{axe}e_avec_cap"] = avec[f"{axe}_median"]
        out[f"le_cap_multiplie_l_{axe}_par"] = _rapport(sans[f"{axe}_median"],
                                                        avec[f"{axe}_median"])
        out[f"coherence_{axe}e_sans_cap"] = sans[f"coherence_{axe}e_mediane"]
        out[f"coherence_{axe}e_avec_cap"] = avec[f"coherence_{axe}e_mediane"]
    out["coherence_tangentielle_sans_cap"] = sans["coherence_median"]
    out["coherence_tangentielle_avec_cap"] = avec["coherence_median"]
    # ⚠⚠ DE COMBIEN LA MATIERE PENCHE PLUS D'UN COTE QUE DE L'AUTRE. C'est la MARGE du verdict de
    # `169` — « le rouleau penche axialement » — et elle est distincte du verdict : une marge qui
    # fond de moitie laisse le verdict debout et ne le laisse plus reposer sur grand-chose.
    for cap, lot in (("sans", sans), ("avec", avec)):
        out[f"lecart_entre_les_parts_{cap}_cap"] = round(
            abs(lot["axial_median"] - lot["azimutal_median"]), 3)
    return out


def le_lien(effet: dict) -> dict:
    """L'axe le moins cohérent SANS cap est-il celui que le cap réduit le plus ?

    ⭐⭐⭐⭐ C'EST L'ENONCE QUI TESTE LE MECANISME, ET IL EST ORDINAL : aucun seuil n'y entre, on
    compare deux nombres mesurés à deux autres nombres mesurés. Le mécanisme qu'on attendrait d'une
    mémoire de cap est qu'elle ne puisse retirer que ce qui ALTERNE — donc qu'elle morde l'axe le
    moins cohérent. Si l'axe mordu est l'autre, le mécanisme est faux.

    ⚠⚠ UNE EGALITE N'EST NI L'UN NI L'AUTRE, et un axe muet non plus : le lien n'est alors PAS
    posable, et le dire vaut mieux que trancher à pile ou face.
    """
    if not effet.get("decidable"):
        return {"decidable": False, "raison": "l'effet du cap n'est pas mesurable"}
    coh = {a: effet[f"coherence_{a}e_sans_cap"] for a in LES_AXES}
    rap = {a: effet[f"le_cap_multiplie_l_{a}_par"] for a in LES_AXES}
    if any(coh[a] is None for a in LES_AXES) or any(rap[a] is None for a in LES_AXES):
        return {"decidable": False, "raison": "un axe ne porte rien",
                "coherences_sans_cap": coh, "rapports": rap}
    if coh[LES_AXES[0]] == coh[LES_AXES[1]] or rap[LES_AXES[0]] == rap[LES_AXES[1]]:
        return {"decidable": False, "raison": "une égalité ne désigne aucun axe",
                "coherences_sans_cap": coh, "rapports": rap}
    moins_coherent = min(LES_AXES, key=lambda a: coh[a])
    le_plus_reduit = min(LES_AXES, key=lambda a: rap[a])
    return {"decidable": True, "coherences_sans_cap": coh, "rapports": rap,
            "laxe_le_moins_coherent_sans_cap": moins_coherent,
            "laxe_que_le_cap_reduit_le_plus": le_plus_reduit,
            "le_cap_retire_ce_qui_alterne": bool(moins_coherent == le_plus_reduit)}


def le_rouleau(lecture: dict) -> dict:
    """Le rouleau, lu DEUX FOIS : sur toutes ses bandes, puis sur les bandes appariées.

    ⚠⚠⚠ LES DEUX LECTURES SONT RENDUES, JAMAIS UNE SEULE. Publier la seule appariée effacerait le
    défaut au lieu de le montrer ; publier la seule non appariée le reconduirait. C'est l'écart
    entre les deux qui est le résultat.
    """
    caps = lecture["caps"]
    sans, avec = caps[0], caps[1]
    communes = [tuple(b) for b in lecture["bandes_communes"]]
    out = {"decidable": True, "sources": lecture["sources"],
           "bandes_par_cap": lecture["bandes_par_cap"],
           "bandes_communes": len(communes),
           "la_plus_courte_est_incluse": lecture["la_plus_courte_est_incluse"]}
    for etiquette, choix in (("toutes_les_bandes", None), ("bandes_appariees", communes)):
        lots = {}
        for cap in (sans, avec):
            marches = lecture["par_cap"][cap]
            cles = sorted(marches) if choix is None else choix
            lots[cap] = resumer([le_cote_dune_marche(marches[k]) for k in cles if k in marches])
        eff = leffet_du_cap(lots[sans], lots[avec])
        out[etiquette] = {"sans_cap": lots[sans], "avec_cap": lots[avec],
                          "effet": eff, "lien": le_lien(eff)}
    a, b = out["toutes_les_bandes"]["effet"], out["bandes_appariees"]["effet"]
    # ⭐⭐⭐⭐ LE FAIT QUE CE MODULE EXISTE POUR MESURER : l'appariement change-t-il la reponse ?
    # Il ne s'agit pas de savoir laquelle est vraie — l'appariee l'est — mais de combien la lecture
    # publiee s'ecarte d'elle, axe par axe.
    out["lappariement_change_la_reponse"] = {
        axe: {"sans_appariement": a.get(f"le_cap_multiplie_l_{axe}_par"),
              "apparie": b.get(f"le_cap_multiplie_l_{axe}_par"),
              "le_cap_change_de_sens": bool(
                  a.get(f"le_cap_multiplie_l_{axe}_par") is not None
                  and b.get(f"le_cap_multiplie_l_{axe}_par") is not None
                  and (a[f"le_cap_multiplie_l_{axe}_par"] < 1.0)
                  != (b[f"le_cap_multiplie_l_{axe}_par"] < 1.0))}
        for axe in LES_AXES}
    return out


def la_fixture(matieres=MATIERES, departs: int = DEPARTS, caps=CAPS,
               pas_max: int = PAS_MAX, rayon_mm: float = RAYON_MM) -> dict:
    """La grille de `169`, matière par matière, appariée par départ.

    ⚠⚠ L'APPARIEMENT EST EXACT PAR CONSTRUCTION et n'a donc pas à être réparé : `lenquete` marche
    CHAQUE départ aux deux caps. La population est la même des deux côtés, et c'est ce qui rend la
    fixture comparable à la lecture appariée du rouleau plutôt qu'à l'autre.
    """
    grille = lenquete(matieres=matieres, departs=departs, caps=caps,
                      pas_max=pas_max, rayon_mm=rayon_mm)
    lus = sorted(float(c) for c in grille["caps"])
    sans, avec = lus[0], lus[-1]
    out = []
    for nom in dict.fromkeys(c["nom"] for c in grille["cases"]):
        cs = [c for c in grille["cases"] if c["nom"] == nom]
        angles_sans = {c["angle_du_depart_deg"] for c in cs
                       if c["memoire_du_cap"] == sans}
        angles_avec = {c["angle_du_depart_deg"] for c in cs
                       if c["memoire_du_cap"] == avec}
        communs = sorted(angles_sans & angles_avec)
        lots = {cap: resumer([c["marche"] for c in cs if c["memoire_du_cap"] == cap
                              and c["angle_du_depart_deg"] in communs])
                for cap in (sans, avec)}
        eff = leffet_du_cap(lots[sans], lots[avec])
        out.append({"nom": nom, "departs_apparies": len(communs),
                    "departs_sans_cap": len(angles_sans), "departs_avec_cap": len(angles_avec),
                    "lappariement_est_exact": bool(angles_sans == angles_avec),
                    "sans_cap": lots[sans], "avec_cap": lots[avec],
                    "effet": eff, "lien": le_lien(eff)})
    return {"decidable": bool(out), "caps": [sans, avec], "par_matiere": out,
            # ⚠⚠ LA MATIERE DU ROULEAU EST NOMMEE ICI, PAS DEDUITE D'UNE POSITION. C'est la
            # derniere de `MATIERES` — l'ecrasement calibre par `90` et le froissement de `134` —
            # et un lecteur qui la prendrait par son rang changerait de matiere le jour ou une
            # ligne est inseree, sans que rien n'ait l'air faux.
            "la_matiere_du_rouleau": _nom(*matieres[-1]),
            "departs": int(departs), "pas_max": int(pas_max), "rayon_mm": float(rayon_mm)}


def lecart_a_la_fixture(rouleau: dict, fixture: dict) -> dict:
    """Combien de fois la fixture marche plus azimutalement que le rouleau, aux deux caps.

    ⭐⭐⭐⭐ C'EST LE NOMBRE QUE `R4-P27` APPELLE « DEUX FOIS TROP », ET IL A DEUX VALEURS. Il est
    calculé sous les DEUX lectures du rouleau, parce que c'est précisément là que l'appariement
    change la réponse — le publier sous une seule ferait passer un artefact de population pour une
    propriété de l'écrasement.

    ⚠⚠ ET IL EST RENDU AUX DEUX CAPS. Sans cap le rapport tombe SOUS un, donc la fixture marche
    MOINS azimutalement que le rouleau ; ne montrer que le cap 0,75 laisserait croire que
    l'écrasement pousse toujours trop loin.
    """
    m = next((x for x in fixture.get("par_matiere", [])
              if x["nom"] == fixture.get("la_matiere_du_rouleau")), None)
    if m is None or not m["effet"].get("decidable"):
        return {"decidable": False, "raison": "la matière du rouleau n'est pas mesurable"}
    out = {"decidable": True, "la_matiere": m["nom"]}
    for etiquette in ("toutes_les_bandes", "bandes_appariees"):
        e = rouleau[etiquette]["effet"]
        for cap in ("sans", "avec"):
            cle = f"part_azimutale_{cap}_cap"
            out[f"{etiquette}_{cap}_cap"] = {
                "la_fixture": m["effet"][cle], "le_rouleau": e[cle],
                "la_fixture_vaut_le_rouleau_fois": _rapport(e[cle], m["effet"][cle])}
    return out


def juger(rouleau: dict | None, fixture: dict) -> dict:
    """Ce que les deux camps répondent à la même question, sans jamais les fondre en un chiffre."""
    liens = []
    if rouleau and rouleau.get("decidable"):
        liens.append(("le rouleau, bandes appariées", rouleau["bandes_appariees"]["lien"]))
    for m in fixture.get("par_matiere", []):
        liens.append((m["nom"], m["lien"]))
    posables = [(n, x) for n, x in liens if x.get("decidable")]
    tiennent = [n for n, x in posables if x["le_cap_retire_ce_qui_alterne"]]
    return {"decidable": bool(posables),
            "cas_posables": len(posables), "cas_examines": len(liens),
            "ou_le_lien_tient": tiennent,
            "ou_le_lien_ne_tient_pas": [n for n, x in posables
                                        if not x["le_cap_retire_ce_qui_alterne"]],
            # ⚠⚠ L'ENONCE JOINT DU DEPOT : un mecanisme tient quand AUCUN cas posable ne le
            # dement. Une majorite ne suffit pas — un cap qui retirerait ce qui alterne une fois
            # sur deux ne retire pas ce qui alterne.
            "le_cap_retire_ce_qui_alterne": bool(posables and len(tiennent) == len(posables)),
            "pourquoi_les_autres_ne_sont_pas_posables": [
                {"nom": n, "raison": x.get("raison")} for n, x in liens
                if not x.get("decidable")]}


def mesurer() -> dict:
    lecture = le_rouleau_par_cap()
    r = le_rouleau(lecture) if lecture else {"decidable": False,
                                             "raison": "les deux courses du rouleau sont absentes"}
    f = la_fixture()
    ecart = (lecart_a_la_fixture(r, f) if lecture
             else {"decidable": False, "raison": "le rouleau est absent"})
    return {"le_rouleau": r, "la_fixture": f, "lecart_a_la_fixture": ecart,
            "le_verdict": juger(r if lecture else None, f)}


def _ligne_deffet(nom: str, e: dict, lien: dict) -> list[str]:
    if not e.get("decidable"):
        return [f"   {nom:<34} — {e.get('raison')}"]
    out = [f"   {nom:<34} "
           f"axial {e['part_axiale_sans_cap']:.3f} → {e['part_axiale_avec_cap']:.3f} "
           f"(×{e['le_cap_multiplie_l_axial_par']}) · "
           f"azimutal {e['part_azimutale_sans_cap']:.3f} → {e['part_azimutale_avec_cap']:.3f} "
           f"(×{e['le_cap_multiplie_l_azimutal_par']})"]
    out.append(f"   {'':<34} cohérence axiale "
               f"{e['coherence_axiale_sans_cap']} → {e['coherence_axiale_avec_cap']} · "
               f"azimutale {e['coherence_azimutale_sans_cap']} → "
               f"{e['coherence_azimutale_avec_cap']} · tangentielle "
               f"{e['coherence_tangentielle_sans_cap']} → {e['coherence_tangentielle_avec_cap']}")
    if lien.get("decidable"):
        out.append(f"   {'':<34} ★ moins cohérent : {lien['laxe_le_moins_coherent_sans_cap']} · "
                   f"le plus réduit : {lien['laxe_que_le_cap_reduit_le_plus']} → "
                   f"le cap retire ce qui alterne : {lien['le_cap_retire_ce_qui_alterne']}")
    else:
        out.append(f"   {'':<34} ✗ lien non posable — {lien.get('raison')}")
    return out


def afficher(r: dict) -> None:
    ro = r.get("le_rouleau") or {}
    print("LE CAP AGIT-IL SUR LES DEUX AXES ?")
    print()
    if not ro.get("decidable"):
        print(f"  le rouleau — {ro.get('raison')}")
    else:
        print(f"  LE ROULEAU · bandes par cap {ro['bandes_par_cap']} · "
              f"communes {ro['bandes_communes']} · la plus courte est incluse : "
              f"{ro['la_plus_courte_est_incluse']}")
        for etiquette in ("toutes_les_bandes", "bandes_appariees"):
            bloc = ro[etiquette]
            for ligne in _ligne_deffet(etiquette.replace("_", " "), bloc["effet"], bloc["lien"]):
                print(ligne)
        print("   ⚠⚠⚠ l'appariement change la réponse :")
        for axe, d in ro["lappariement_change_la_reponse"].items():
            print(f"      {axe:<10} ×{d['sans_appariement']} sans appariement → "
                  f"×{d['apparie']} apparié · le cap change de sens : "
                  f"{d['le_cap_change_de_sens']}")
    print()
    fx = r.get("la_fixture") or {}
    print(f"  LA FIXTURE · {fx.get('departs')} départs, {fx.get('pas_max')} pas, "
          f"rayon {fx.get('rayon_mm')} mm")
    for m in fx.get("par_matiere", []):
        print(f"   {'':<2}appariement exact : {m['lappariement_est_exact']} "
              f"({m['departs_apparies']} départs)")
        for ligne in _ligne_deffet(m["nom"], m["effet"], m["lien"]):
            print(ligne)
    print()
    ec = r.get("lecart_a_la_fixture") or {}
    if ec.get("decidable"):
        print(f"  L'ECART A LA FIXTURE · part azimutale · {ec['la_matiere']}")
        for cle, d in ((k, ec[k]) for k in ec if isinstance(ec.get(k), dict)):
            print(f"   {cle:<34} fixture {d['la_fixture']:.3f} · rouleau "
                  f"{d['le_rouleau']:.3f} · la fixture vaut le rouleau "
                  f"×{d['la_fixture_vaut_le_rouleau_fois']}")
        print()
    v = r.get("le_verdict") or {}
    print(f"  ★ LE VERDICT · {v.get('cas_posables')} cas posables sur {v.get('cas_examines')}")
    print(f"     le lien tient    : {v.get('ou_le_lien_tient')}")
    print(f"     le lien ne tient pas : {v.get('ou_le_lien_ne_tient_pas')}")
    print(f"     → le cap retire ce qui alterne : {v.get('le_cap_retire_ce_qui_alterne')}")
    for x in v.get("pourquoi_les_autres_ne_sont_pas_posables", []):
        print(f"     ✗ {x['nom']} — {x['raison']}")


def _marche(axial: float, azimutal: float, coh: float,
            coh_ax: float | None, coh_az: float | None) -> dict:
    """Une marche dont les cinq grandeurs sont CHOISIES — pour que l'attendu se dérive d'elles."""
    return le_cote_dune_marche({"decidable": True, "pas": 9,
                                "axial_absolu_median": axial,
                                "azimutal_absolu_median": azimutal,
                                "glissement_axial_median_um": 0.0,
                                "coherence_tangentielle": coh,
                                "coherence_axiale": coh_ax,
                                "coherence_azimutale": coh_az})


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ---- le résumé, et ce qu'il refuse de remplacer
    v("un lot vide n'est pas décidable", resumer([]).get("decidable") is False)
    v("... et un lot de `None` non plus", resumer([None, None]).get("decidable") is False)
    muet = resumer([_marche(0.4, 0.2, 0.9, None, 0.8), _marche(0.6, 0.2, 0.9, 0.5, 0.6)])
    # ⚠⚠ L'ATTENDU SE DERIVE DE LA FIXTURE : une seule marche porte l'axial, donc la mediane
    # axiale EST sa valeur. Si `None` devenait zero, la mediane vaudrait 0,25 ; si elle devenait
    # un, 0,75. Les trois sont distinguables, donc la sonde mord.
    v("⚠⚠ un axe muet est COMPTE, jamais remplacé par zéro ni par un",
      muet["coherence_axiale_mediane"] == 0.5 and muet["marches_ou_l_axial_ne_porte_rien"] == 1
      and muet["marches_ou_l_azimutal_ne_porte_rien"] == 0,
      f"cohérence axiale {muet['coherence_axiale_mediane']} sur "
      f"{muet['decidables'] - muet['marches_ou_l_axial_ne_porte_rien']} marches")
    v("... et l'axe qui porte, lui, est résumé sur toutes ses marches",
      muet["coherence_azimutale_mediane"] == 0.7,
      f"{muet['coherence_azimutale_mediane']}")
    v("un rapport sur zéro n'est pas un grand rapport, c'est `None`",
      _rapport(0.0, 0.3) is None and _rapport(0.4, 0.2) == 0.5)

    # ---- le lien, sur des cas dont la réponse se dérive de leurs propres nombres
    fabrique = leffet_du_cap(
        resumer([_marche(0.4, 0.4, 0.9, 0.2, 0.9)]),
        resumer([_marche(0.2, 0.4, 0.9, 0.2, 0.9)]))
    li = le_lien(fabrique)
    v("⭐ le lien TIENT quand l'axe le moins cohérent est celui que le cap réduit",
      li["decidable"] and li["laxe_le_moins_coherent_sans_cap"] == "axial"
      and li["laxe_que_le_cap_reduit_le_plus"] == "axial"
      and li["le_cap_retire_ce_qui_alterne"] is True,
      f"{li.get('laxe_le_moins_coherent_sans_cap')} / "
      f"{li.get('laxe_que_le_cap_reduit_le_plus')}")
    miroir = leffet_du_cap(
        resumer([_marche(0.4, 0.4, 0.9, 0.2, 0.9)]),
        resumer([_marche(0.4, 0.2, 0.9, 0.2, 0.9)]))
    lm = le_lien(miroir)
    v("... et il NE TIENT PAS sur le cas miroir, où le cap mord l'axe le plus cohérent",
      lm["decidable"] and lm["laxe_le_moins_coherent_sans_cap"] == "axial"
      and lm["laxe_que_le_cap_reduit_le_plus"] == "azimutal"
      and lm["le_cap_retire_ce_qui_alterne"] is False,
      f"{lm.get('laxe_le_moins_coherent_sans_cap')} / "
      f"{lm.get('laxe_que_le_cap_reduit_le_plus')}")
    egal = le_lien(leffet_du_cap(resumer([_marche(0.4, 0.4, 0.9, 0.5, 0.5)]),
                                 resumer([_marche(0.2, 0.2, 0.9, 0.5, 0.5)])))
    v("⚠⚠ une égalité ne désigne aucun axe, donc le lien n'est pas posable",
      egal.get("decidable") is False, egal.get("raison"))
    sourd = le_lien(leffet_du_cap(resumer([_marche(0.0, 0.4, 0.9, None, 0.9)]),
                                  resumer([_marche(0.0, 0.2, 0.9, None, 0.9)])))
    v("... et un axe muet non plus", sourd.get("decidable") is False, sourd.get("raison"))

    # ---- le verdict est JOINT : une majorité ne suffit pas
    jf = {"par_matiere": [{"nom": "a", "lien": le_lien(fabrique)},
                          {"nom": "b", "lien": le_lien(miroir)}]}
    j = juger(None, jf)
    v("⚠⚠ le verdict est JOINT : un seul cas qui dément suffit à ne pas conclure",
      j["cas_posables"] == 2 and j["le_cap_retire_ce_qui_alterne"] is False
      and j["ou_le_lien_tient"] == ["a"] and j["ou_le_lien_ne_tient_pas"] == ["b"])
    v("... et un lot où tous les cas posables tiennent conclut, lui",
      juger(None, {"par_matiere": [{"nom": "a", "lien": le_lien(fabrique)}]})[
          "le_cap_retire_ce_qui_alterne"] is True)

    # ---- le rouleau : l'appariement existe, et il CHANGE la réponse
    lecture = le_rouleau_par_cap()
    v("les deux courses du rouleau sont là", lecture is not None,
      "" if lecture else "une course manque, la comparaison est refusée")
    if lecture is not None:
        tailles = sorted(lecture["bandes_par_cap"].values())
        v("⚠⚠⚠ les deux courses ne portent PAS le même nombre de bandes",
          tailles[0] != tailles[-1], f"{lecture['bandes_par_cap']}")
        v("... mais la plus courte est INCLUSE dans l'autre, donc l'appariement existe",
          lecture["la_plus_courte_est_incluse"]
          and len(lecture["bandes_communes"]) == tailles[0],
          f"{len(lecture['bandes_communes'])} bandes communes pour {tailles[0]}")
        ro = le_rouleau(lecture)
        # ⚠⚠ Une marche du ROULEAU passe par le MEME lecteur qu'une marche de la fixture. Si les
        # cles ne s'y trouvaient pas, le lecteur rendrait `None` et le lot serait vide.
        v("⚠⚠ une marche du rouleau est lue par le lecteur de la fixture",
          ro["toutes_les_bandes"]["sans_cap"]["decidables"] == tailles[0],
          f"{ro['toutes_les_bandes']['sans_cap']['decidables']} marches décidables")
        chg = ro["lappariement_change_la_reponse"]
        # ⭐⭐⭐⭐ LA RAISON D'ETRE DE CE MODULE, ET ELLE PEUT ECHOUER : si les deux lectures
        # rendaient les memes rapports, l'appariement ne serait qu'une precaution d'ecriture.
        v("⭐⭐⭐⭐ l'appariement CHANGE la réponse sur au moins un axe",
          any(chg[a]["sans_appariement"] != chg[a]["apparie"] for a in LES_AXES),
          " · ".join(f"{a} ×{chg[a]['sans_appariement']}→×{chg[a]['apparie']}"
                     for a in LES_AXES))
        v("... et les deux lectures sont rendues côte à côte, jamais une seule",
          ro["toutes_les_bandes"]["effet"]["decidable"]
          and ro["bandes_appariees"]["effet"]["decidable"])

    # ---- la fixture : l'appariement y est exact PAR CONSTRUCTION
    petite = la_fixture(matieres=(MATIERES[0], MATIERES[1]), departs=2, pas_max=5)
    v("l'appariement de la fixture est exact sur chaque matière",
      petite["decidable"] and all(m["lappariement_est_exact"] for m in petite["par_matiere"]),
      f"{[m['departs_apparies'] for m in petite['par_matiere']]} départs appariés")
    nue = next((m for m in petite["par_matiere"] if m["nom"] == "spirale nue"), None)
    # ⚠ CONTROLE VIDE : sur la spirale nue l'axe axial ne porte rien, donc le lien n'y est pas
    # posable. Un module qui y rendrait un verdict mesurerait son propre arrondi.
    v("⚠ contrôle vide : sur la spirale nue le lien n'est PAS posable",
      nue is not None and nue["lien"].get("decidable") is False,
      (nue or {}).get("lien", {}).get("raison"))
    v("... et c'est parce qu'un de ses axes ne porte rien, pas parce qu'elle a échoué",
      nue is not None and nue["sans_cap"]["decidable"]
      and nue["sans_cap"]["marches_ou_l_axial_ne_porte_rien"] > 0,
      f"{(nue or {}).get('sans_cap', {}).get('marches_ou_l_axial_ne_porte_rien')} marches muettes")

    # ---- l'écart à la fixture, et il a DEUX valeurs
    ec = lecart_a_la_fixture(
        {"toutes_les_bandes": {"effet": {"decidable": True, "part_azimutale_sans_cap": 0.4,
                                         "part_azimutale_avec_cap": 0.2}},
         "bandes_appariees": {"effet": {"decidable": True, "part_azimutale_sans_cap": 0.4,
                                        "part_azimutale_avec_cap": 0.3}}},
        {"la_matiere_du_rouleau": "m",
         "par_matiere": [{"nom": "m", "effet": {"decidable": True,
                                                "part_azimutale_sans_cap": 0.3,
                                                "part_azimutale_avec_cap": 0.3}}]})
    # ⚠⚠ L'ATTENDU SE DERIVE DE LA FIXTURE : 0,3/0,2 vaut 1,5 et 0,3/0,3 vaut 1,0. Si le module
    # ne publiait qu'une lecture, l'un des deux serait absent et le doublement serait invisible.
    v("⭐⭐⭐⭐ l'écart à la fixture est rendu sous les DEUX lectures du rouleau",
      ec["decidable"]
      and ec["toutes_les_bandes_avec_cap"]["la_fixture_vaut_le_rouleau_fois"] == 1.5
      and ec["bandes_appariees_avec_cap"]["la_fixture_vaut_le_rouleau_fois"] == 1.0,
      f"{ec.get('toutes_les_bandes_avec_cap', {}).get('la_fixture_vaut_le_rouleau_fois')} contre "
      f"{ec.get('bandes_appariees_avec_cap', {}).get('la_fixture_vaut_le_rouleau_fois')}")
    v("... et SANS cap aussi, où la fixture passe sous le rouleau",
      ec["toutes_les_bandes_sans_cap"]["la_fixture_vaut_le_rouleau_fois"] == 0.75,
      f"×{ec['toutes_les_bandes_sans_cap']['la_fixture_vaut_le_rouleau_fois']}")

    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {controles} checks)")
    else:
        print(f"ALL PASS (0 failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
