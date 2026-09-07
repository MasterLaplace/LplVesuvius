#!/usr/bin/env python3
"""Le verdict de la marche tient-il depuis une AUTRE ancre ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, et il vient d'une faute déjà payée. `la_portee_du_raccrochage`
publie que lisser la nappe entre deux bras achète un bras — mesuré sur **une seule** marche,
depuis **une seule** ancre. Or ce dépôt a déjà vu trois verdicts s'inverser en changeant la
population : passer de 7 à 6 pas déplaçait l'erreur du chemin déployé de 36,0 à 48,5 µm, et c'est
cette découverte qui a produit `lecart_apparie`. Un verdict tiré d'une population est une
hypothèse sur les autres tant que les autres n'ont pas été regardées.

⭐⭐ CE QUE CE FICHIER DEMANDE, et rien de plus : le SIGNE tient-il ? Pas « la portée est-elle la
même » — elle ne peut pas l'être, une ancre plus haute a moins de bras devant elle et rencontre
d'autres spires. Ce qui doit tenir est l'ORDRE : le marcheur lissé va-t-il au moins aussi loin
que le pas normal seul, et son écart apparié reste-t-il négatif, depuis chaque ancre ?

⚠⚠ LES ANCRES NE SONT PAS COMPARABLES ENTRE ELLES, et c'est pourquoi rien n'est moyenné ici.
Chaque ancre est une marche à part, avec sa longueur, ses spires et son trou de corpus ; agréger
leurs portées ferait une moyenne de choses différentes. Ce qui s'agrège est le COMPTE des ancres
où le signe tient, ce qui est un fait sur la robustesse et non sur la matière.

⚠ Et l'ancre la plus haute est écartée : il lui faut au moins une spire devant elle pour marcher.

Usage :
    uv run python src/nappe/la_portee_tient_elle_ailleurs.py --verifier
    uv run python src/nappe/la_portee_tient_elle_ailleurs.py --cote 960 --ancres 4 \\
        --json docs/mesures/la_portee_tient_elle_ailleurs.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from la_portee_du_raccrochage import mesurer as marche_depuis  # noqa: E402
from le_corpus_des_spires import corpus_fabrique, volume_fabrique  # noqa: E402

# ⚠⚠⚠ LES DEUX COLONNES QUE CE FICHIER CONFRONTE, et elles sont nommées ici plutôt que
# choisies à l'exécution : le marcheur que la tranche précédente propose, et celui qu'il
# prétend battre. Les laisser en argument permettrait de chercher la paire qui gagne.
CANDIDAT = "rien_lisse"
REFERENCE = "rien"
# ⚠ Ce qu'on relit de chaque marche : la portée de chaque marcheur, l'écart apparié du candidat
# à sa référence, et de quoi dire si l'ancre avait seulement de quoi marcher.
CLE_ECART = "ecart_du_pas_normal_lisse"


def signe_tient(ligne: dict) -> bool:
    """Le signe tient à cette ancre : au moins aussi loin, ET un écart apparié négatif.

    ⚠⚠ LES DEUX CONDITIONS, PAS UNE. Une portée est un entier, donc elle est grossière : deux
    marcheurs peuvent la partager en étant séparés de trente micromètres. Un écart apparié est
    fin mais ne dit rien du seuil qui décide qu'une marche est perdue. Exiger les deux, c'est
    demander que le candidat ne soit pire sur aucun des deux plans.

    ⚠ La condition sur l'écart est « médiane négative », pas `tranche` : trancher demande une
    majorité de bras améliorés ET un intervalle entièrement négatif, ce qui devient très exigeant
    sur une marche courte. Ce fichier demande si le SIGNE tient, ce qui est la question posée.
    """
    e = ligne.get("ecart")
    return bool(ligne["portee_candidat"] >= ligne["portee_reference"]
                and e is not None and e["ecart_median_um"] < 0)


def mesurer(ancres: int = 4, graine: int = 42, minimum: int = 30, cache_actif: bool = True,
            cote: float | None = None, bras_max: int = 8,
            corpus: dict | None = None, volume=None) -> dict:
    """La même marche depuis les `ancres` premières spires de la boîte."""
    lignes, soucis = [], []
    for k in range(max(1, int(ancres))):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                r = marche_depuis(graine=graine, minimum=minimum, cache_actif=cache_actif,
                                  cote=cote, bras_max=bras_max, corpus=corpus, volume=volume,
                                  decalage_ancre=k)
        except RuntimeError as exc:
            # ⚠ Une ancre trop haute n'a plus de spire devant elle. C'est une fin normale du
            # balayage, pas une panne : elle est comptée et nommée, jamais avalée.
            soucis.append(dict(decalage=k, raison=str(exc)))
            break

        def par(nom: str) -> dict:
            return next(x for x in r["lignes"] if x["marcheur"] == nom)

        lignes.append(dict(
            decalage=k, ancre=r["ancre"], spires_visees=r["spires_visees"],
            bras_au_pas_nominal=r["bras_au_pas_nominal"],
            portees={x["marcheur"]: x["portee"] for x in r["lignes"]},
            portee_candidat=par(CANDIDAT)["portee"], portee_reference=par(REFERENCE)["portee"],
            ecart=r[CLE_ECART],
            rugosite_nappe_candidat=par(CANDIDAT)["rugosites_nappe_um"],
            rugosite_nappe_reference=par(REFERENCE)["rugosites_nappe_um"]))
    if not lignes:
        raise RuntimeError("aucune ancre n'a pu marcher : " + str(soucis))
    for x in lignes:
        x["signe_tient"] = signe_tient(x)
    return dict(
        candidat=CANDIDAT, reference=REFERENCE, ancres=len(lignes), lignes=lignes,
        ancres_refusees=soucis,
        # ⭐⭐⭐ LE COMPTE, ET RIEN QUI RESSEMBLE À UNE MOYENNE. Chaque ancre est une marche à part,
        # avec sa longueur et son trou de corpus ; moyenner leurs portées ferait la moyenne de
        # choses différentes. Ce qui s'agrège est le nombre d'ancres où le signe tient.
        ancres_ou_le_signe_tient=sum(x["signe_tient"] for x in lignes),
        le_signe_tient_partout=all(x["signe_tient"] for x in lignes),
        # ⚠ ET LE CONTRAIRE EST PUBLIÉ AUSSI : une ancre où le candidat fait PIRE est le fait qui
        # renverserait le verdict, donc elle est nommée et pas seulement soustraite d'un total.
        ancres_ou_le_candidat_perd=[x["decalage"] for x in lignes
                                    if x["portee_candidat"] < x["portee_reference"]],
        # ⚠⚠⚠ DEUX VERDICTS, ET IL FAUT LES SÉPARER. « L'écart est négatif » et « la portée
        # gagne un bras » ne sont pas la même affirmation : un gain de six micromètres est
        # constant et fin, un bras gagné demande que l'erreur passe SOUS un seuil, ce qui
        # n'arrive que là où elle en était proche. Publier le second à la place du premier
        # ferait passer la chance d'une ancre pour une propriété de la méthode.
        ancres_ou_la_portee_gagne=[x["decalage"] for x in lignes
                                   if x["portee_candidat"] > x["portee_reference"]],
        ancres_ou_lecart_est_negatif=[x["decalage"] for x in lignes
                                      if x["ecart"] and x["ecart"]["ecart_median_um"] < 0])


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ LES DEUX CONDITIONS DU SIGNE, exercées séparément : une seule des deux suffirait à
    # laisser passer un candidat qui va moins loin mais lit un peu mieux, ou l'inverse.
    v("le signe tient quand la portée est au moins égale ET l'écart négatif",
      signe_tient(dict(portee_candidat=5, portee_reference=4,
                       ecart=dict(ecart_median_um=-6.7))))
    v("... il ne tient pas si la portée baisse, même avec un écart négatif",
      not signe_tient(dict(portee_candidat=3, portee_reference=4,
                           ecart=dict(ecart_median_um=-6.7))))
    v("... ni si l'écart est positif, même à portée égale",
      not signe_tient(dict(portee_candidat=4, portee_reference=4,
                           ecart=dict(ecart_median_um=+0.4))))
    v("... et un écart absent ne tient PAS pour un signe",
      not signe_tient(dict(portee_candidat=5, portee_reference=4, ecart=None)))

    # ⚠⚠⚠ LE CHEMIN QUI PRODUIT LE NOMBRE PUBLIÉ, HORS LIGNE.
    from le_corpus_des_spires import geometrie_fabriquee  # noqa: PLC0415

    c = corpus_fabrique()
    fab = mesurer(ancres=3, minimum=20, corpus=c, volume=volume_fabrique(geometrie_fabriquee()))
    v("la mesure tourne de bout en bout sur des matières fabriquées",
      fab["ancres"] >= 2, f"{fab['ancres']} ancres · "
      + str([x["ancre"] for x in fab["lignes"]]))
    # ⚠⚠ CHAQUE ANCRE EST UNE MARCHE À PART : elles ne partent pas de la même spire et n'ont pas
    # le même nombre de bras devant elles. Un contrôle qui verrait deux ancres identiques
    # signalerait que le décalage n'a rien décalé.
    v("... chaque ancre part d'une spire différente et voit moins de bras que la précédente",
      len({x["ancre"] for x in fab["lignes"]}) == fab["ancres"]
      and all(len(a["spires_visees"]) >= len(b["spires_visees"])
              for a, b in zip(fab["lignes"], fab["lignes"][1:])),
      str([(x["ancre"], len(x["spires_visees"])) for x in fab["lignes"]]))
    v("... le signe est jugé à chaque ancre, et le compte n'est pas une moyenne",
      isinstance(fab["ancres_ou_le_signe_tient"], int)
      and 0 <= fab["ancres_ou_le_signe_tient"] <= fab["ancres"],
      f"{fab['ancres_ou_le_signe_tient']}/{fab['ancres']} · "
      + str([x["signe_tient"] for x in fab["lignes"]]))
    # ⚠ CE QUI RENVERSERAIT LE VERDICT EST NOMMÉ, pas seulement soustrait d'un total : une ancre
    # où le candidat va moins loin est le fait qu'un lecteur doit pouvoir aller regarder.
    # ⚠⚠⚠ LES DEUX VERDICTS SONT SÉPARÉS, et le contrôle exige qu'ils ne se confondent pas :
    # une ancre où la portée gagne est nécessairement une ancre où le signe tient, mais
    # l'inverse est faux, et c'est exactement la nuance qu'il ne faut pas perdre.
    v("... « l'écart est négatif » et « la portée gagne » sont publiés SÉPARÉMENT",
      set(fab["ancres_ou_la_portee_gagne"]) <= set(fab["ancres_ou_lecart_est_negatif"])
      or not fab["ancres_ou_la_portee_gagne"],
      f"portée {fab['ancres_ou_la_portee_gagne']} ⊆ écart "
      f"{fab['ancres_ou_lecart_est_negatif']}")
    v("... et les ancres où le candidat va MOINS loin sont nommées",
      all(fab["lignes"][k]["portee_candidat"] < fab["lignes"][k]["portee_reference"]
          for k in fab["ancres_ou_le_candidat_perd"]),
      str(fab["ancres_ou_le_candidat_perd"]))
    v("... le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    souci = None
    try:
        json.dumps(fab)
        afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("... et l'affichage tourne sur ce résultat", souci is None, str(souci))
    # ⚠⚠ UNE DEMANDE D'ANCRES AU-DELÀ DE CE QUE LA BOÎTE PORTE S'ARRÊTE ET LE DIT. Rendre
    # silencieusement moins d'ancres que demandé ferait lire « le signe tient partout » sur un
    # balayage qui s'est arrêté tôt.
    trop = mesurer(ancres=99, minimum=20, corpus=c,
                   volume=volume_fabrique(geometrie_fabriquee()))
    v("une demande d'ancres au-delà de la boîte s'arrête et NOMME la raison",
      trop["ancres_refusees"] and trop["ancres"] < 99,
      f"{trop['ancres']} ancres · " + str(trop["ancres_refusees"][:1]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible : une ligne par ancre, et le signe au bout."""
    print(f"candidat « {r['candidat']} » contre référence « {r['reference']} » · "
          f"{r['ancres']} ancre(s)")
    print()
    print(f"{'ancre':>6} {'bras':>5} {'candidat':>9} {'référence':>10} {'corpus':>7} "
          f"{'écart apparié (µm)':>26}  signe")
    print("-" * 78)
    for x in r["lignes"]:
        e = x["ecart"]
        txt = (f"{e['ecart_median_um']:+7.1f} · {e['pas_ameliores']}/{e['pas']} · "
               f"{e['intervalle_um']}" if e else "—")
        print(f"{x['ancre']:>6} {len(x['spires_visees']):>5} {x['portee_candidat']:>9} "
              f"{x['portee_reference']:>10} {x['bras_au_pas_nominal']:>7} {txt:>26}  "
              f"{'oui' if x['signe_tient'] else 'NON'}")
    print()
    print(f"→ le signe tient sur {r['ancres_ou_le_signe_tient']}/{r['ancres']} ancres · "
          f"partout : {'OUI' if r['le_signe_tient_partout'] else 'NON'}")
    print(f"→ ⭐ l'écart est négatif aux ancres {r['ancres_ou_lecart_est_negatif']} "
          f"({len(r['ancres_ou_lecart_est_negatif'])}/{r['ancres']})")
    print(f"→ ⚠ mais la PORTÉE ne gagne un bras qu'aux ancres "
          f"{r['ancres_ou_la_portee_gagne']} "
          f"({len(r['ancres_ou_la_portee_gagne'])}/{r['ancres']}) : un gain apparié constant et "
          "un bras gagné ne sont PAS la même affirmation")
    if r["ancres_ou_le_candidat_perd"]:
        print(f"→ ⚠ le candidat va MOINS loin aux ancres {r['ancres_ou_le_candidat_perd']}")
    for x in r["ancres_refusees"]:
        print(f"→ ancre {x['decalage']} refusée : {x['raison']}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ancres", type=int, default=4)
    p.add_argument("--cote", type=float, default=None)
    p.add_argument("--bras-max", type=int, default=8)
    p.add_argument("--minimum", type=int, default=30)
    p.add_argument("--sans-cache", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(ancres=a.ancres, minimum=a.minimum, cache_actif=not a.sans_cache,
                cote=a.cote, bras_max=a.bras_max)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
