#!/usr/bin/env python3
"""L'écart apparié : comparer deux méthodes quand les cas varient plus qu'elles.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL VIENT D'UNE MESURE. La famille du déroulage compare des
méthodes sur cinq à sept pas de spire, en publiant la **différence de leurs médianes**. Or sur
les pas de la boîte publiée, ne rien faire coûte de **32,2 à 73,9 µm** selon le pas : la
variabilité d'un pas à l'autre vaut **quatre fois** l'écart entre deux méthodes. Une différence
de médianes mêle donc les deux, et le résultat se fait décider par le tirage des pas plutôt que
par la méthode.

⭐⭐ Mesuré : sur `le_raccrochage_choisit_il_bien`, la différence des médianes donnait un gain de
**5,6 µm** ; l'écart pris **sur le même pas** donne **−1,2 µm**, avec un intervalle à un pas de
moins de **[−5,2 ; +2,5]** qui enjambe zéro. Le gain publié n'était pas faux comme nombre — il
était le mauvais nombre pour la question.

⚠⚠ ET L'INTERVALLE FAIT PARTIE DU VERDICT. Ce dépôt a écrit qu'« un verdict qui change avec la
population n'est pas un verdict » ; à six pas, la règle ne se respecte qu'en la mesurant. Un
écart dont le signe ne survit pas au retrait d'un pas quelconque n'est pas une amélioration,
c'est un pas qui portait la conclusion.

Usage :
    uv run python src/commun/lecart_apparie.py --verifier
"""

from __future__ import annotations

import argparse
import sys

import numpy as np


def ecart_apparie(valeurs: list[float], reference: list[float]) -> dict:
    """L'écart cas par cas entre deux méthodes, et ce qu'il devient si un cas quelconque sort.

    ⚠ Un écart NÉGATIF veut dire que la méthode fait MIEUX que sa référence : c'est une erreur
    qu'on retranche, et l'inverser serait la façon la plus discrète de publier une perte comme
    un gain.

    ⚠⚠ Les deux listes sont appariées par POSITION : elles doivent décrire les mêmes cas dans
    le même ordre, sans quoi la soustraction compare deux cas différents et rend un nombre
    parfaitement stable et dénué de sens. La longueur est donc exigée égale plutôt que
    tronquée — tronquer laisserait passer exactement ce désalignement.

    Rend l'écart médian, l'intervalle de cet écart à un cas de moins, le nombre de cas
    améliorés et le nombre de cas.
    """
    if len(valeurs) != len(reference):
        raise ValueError(f"{len(valeurs)} valeurs contre {len(reference)} références : "
                         "un écart apparié compare les mêmes cas, dans le même ordre")
    ecarts = [float(a) - float(b) for a, b in zip(valeurs, reference)]
    if not ecarts:
        return dict(ecart_median_um=None, intervalle_um=None, pas_ameliores=0, pas=0)
    loo = ([float(np.median(np.delete(np.array(ecarts), i))) for i in range(len(ecarts))]
           if len(ecarts) > 1 else [float(np.median(ecarts))])
    return dict(ecart_median_um=round(float(np.median(ecarts)), 1),
                intervalle_um=[round(min(loo), 1), round(max(loo), 1)],
                pas_ameliores=sum(1 for e in ecarts if e < 0), pas=len(ecarts))


def tranche(ecart: dict) -> bool:
    """Le verdict que cet écart autorise : mieux, et de façon qui survit au retrait d'un cas.

    ⚠⚠⚠ TROIS CONDITIONS, ET AUCUNE N'EST UN SEUIL. L'écart médian doit être négatif ; la
    majorité des cas doit s'améliorer — sans quoi une médiane serait portée par une minorité —
    et l'intervalle à un cas de moins doit rester entièrement négatif. La troisième est celle
    que ce dépôt s'était donnée en prose sans jamais la calculer.
    """
    if ecart["ecart_median_um"] is None or ecart["pas"] < 2:
        return False
    return bool(ecart["ecart_median_um"] < 0
                and ecart["pas_ameliores"] > ecart["pas"] / 2
                and ecart["intervalle_um"][1] < 0)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    v("l'écart d'une méthode à elle-même vaut exactement zéro",
      ecart_apparie([3.0, 9.0, 1.0], [3.0, 9.0, 1.0])["ecart_median_um"] == 0.0)
    e = ecart_apparie([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
    v("... un écart NÉGATIF veut dire mieux que la référence",
      e["ecart_median_um"] == -2.0 and e["pas_ameliores"] == 3, str(e))
    # ⚠⚠⚠ LA RAISON D'ÊTRE DU FICHIER : deux méthodes séparées d'un écart constant gardent cet
    # écart quelle que soit la dispersion des cas. Une différence de médianes, elle, se ferait
    # décider par cette dispersion — c'est ce qui a fait publier 5,6 µm là où il y avait −1,2.
    disperse = ecart_apparie([40.0, 90.0, 33.0], [42.0, 92.0, 35.0])
    v("... et il annule la dispersion entre cas, si grande soit-elle",
      disperse["ecart_median_um"] == -2.0 and disperse["intervalle_um"] == [-2.0, -2.0],
      str(disperse))
    # ⚠⚠ LE CONTRÔLE QUI DISCRIMINE : un écart dont un seul cas porte le signe est refusé.
    porte = ecart_apparie([10.0, 10.0, 10.0], [11.0, 9.0, 9.0])
    v("un écart dont la majorité des cas ne profite pas est REFUSÉ",
      not tranche(porte), str(porte))
    v("... un écart franc et partagé est ACCEPTÉ",
      tranche(ecart_apparie([8.0, 7.0, 9.0], [10.0, 10.0, 10.0])),
      str(ecart_apparie([8.0, 7.0, 9.0], [10.0, 10.0, 10.0])))
    # ⚠⚠⚠ ET CELUI QUI EMPÊCHE UN CAS DE DÉCIDER SEUL : deux cas sur trois s'améliorent et la
    # médiane est négative, mais elle ne tient qu'à un cheveu — retirer le cas franchement bon
    # la fait remonter au-dessus de zéro. C'est la troisième condition de `tranche`, et sans
    # elle ce dépôt aurait publié « une autre forme marche mieux » sur un seul pas de spire.
    fragile = ecart_apparie([5.0, 9.9, 12.0], [10.0, 10.0, 10.0])
    v("... un écart que le retrait d'un seul cas annule est REFUSÉ",
      not tranche(fragile) and fragile["ecart_median_um"] < 0,
      str(fragile))
    # ⚠ Un désalignement des listes rend un nombre parfaitement stable et dénué de sens : il
    # est refusé plutôt que tronqué, parce que tronquer EST le désalignement.
    mal = None
    try:
        ecart_apparie([1.0, 2.0], [1.0])
    except ValueError as exc:
        mal = str(exc)
    v("deux listes de longueurs différentes sont REFUSÉES, pas tronquées",
      mal is not None, str(mal))
    v("... et un cas unique ne tranche rien", not tranche(ecart_apparie([1.0], [9.0])),
      str(ecart_apparie([1.0], [9.0])))
    v("aucune donnée ne rend aucun écart, plutôt qu'un zéro",
      ecart_apparie([], [])["ecart_median_um"] is None)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    if not p.parse_args().verifier:
        p.error("ce module est un instrument : il s'exerce par --verifier")
    return verifier()


if __name__ == "__main__":
    sys.exit(main())
