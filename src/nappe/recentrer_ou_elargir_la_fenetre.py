#!/usr/bin/env python3
"""Recentrer la fenêtre de pas est GRATUIT ; l'élargir ne l'est pas.

⚠⚠⚠ POURQUOI CE FICHIER, ET IL DÉCIDE DU DESSIN DE LA RE-COURSE. `117` a mesuré que **63 pas
voyants sur 382** sont refusés parce que l'optimum de longueur tombe au bord de la fenêtre
[0,5 ; 2,0] × 173,0 µm, et `118` que les deux bouts sont de **vrais pas** — l'espacement local y
vaut 80,7 µm et 380,2 µm. Le remède évident est « élargir la fenêtre ». Avant de le faire, il faut
savoir ce que ça coûte.

⭐⭐⭐⭐ **RECENTRER NE COÛTE RIEN : le modèle nul est INVARIANT par changement d'échelle.** Il ne
dépend que des **rapports** `longueur / plus longue`, parce que chaque candidat est rééchantillonné
sur le même nombre de points. Mesuré : le nul d'une fenêtre centrée sur 250 µm ou sur 80 µm est
celui de la fenêtre publiée à **1,5·10⁻¹⁶** près, c'est-à-dire au bruit du flottant.

⭐⭐⭐⭐ **ÉLARGIR, SI : le nul se déplace de plus d'un écart-type de sa propre dispersion.**
[0,3 ; 3,0] le déplace de **1,2 σ**, [0,25 ; 4,0] de **2,0 σ**. Réutiliser la barre publiée sur une
fenêtre élargie remettrait donc exactement le biais que `nul_par_candidat` existe pour tuer — la
recherche biaisée vers les courts, qui rendait sur du bruit pur ce qu'elle rendait sur le volume.

⚠⚠ **Conséquence pour `R4-P24`** : la fenêtre peut suivre l'espacement local **sans rien
recalibrer**, ce qui rend le remède bon marché ; mais toute largeur nouvelle exige **son** nul, et
l'oublier serait une mesure fausse qui ressemble à une mesure.

⚠ Aucune lecture distante : le nul est un tirage de bruit, il ne touche aucun volume.

  uv run python src/nappe/recentrer_ou_elargir_la_fenetre.py --verifier
  uv run python src/nappe/recentrer_ou_elargir_la_fenetre.py \
      --json docs/mesures/recentrer_ou_elargir_la_fenetre.json
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

import le_pas_que_la_matiere_montre as M  # noqa: E402

NUL_TIRAGES = 800
"""Le nombre de tirages du nul, celui de `nul_par_candidat`. Il est relu ici parce que l'erreur-type
de la moyenne en dépend, et qu'une erreur-type calculée sur un autre compte serait fausse."""

NOMINAUX_UM = (80.0, 120.0, 173.0, 250.0, 400.0)
"""Les centres de fenêtre comparés, et ils ne sont pas choisis au hasard.

⚠ 80 et 400 encadrent l'espacement que `118` déduit aux deux bouts (80,7 et 380,2 µm) : ce sont
les recentrages que la re-course demanderait réellement, pas une plage décorative. 173,0 est le pas
nominal publié, donc la référence."""

FENETRES = ((0.5, 2.0), (0.4, 2.5), (0.3, 3.0), (0.25, 4.0))
"""Les largeurs comparées. La première est celle qui est publiée, donc l'écart y vaut zéro par
construction — c'est la ligne qui rend le tableau lisible, pas un résultat."""


def nul(nominal_um: float, bas: float, haut: float) -> tuple[np.ndarray, np.ndarray]:
    """Le nul par candidat d'une fenêtre, **importé** et jamais réécrit.

    ⚠ Un second nul serait deux modèles d'un même bruit, libres de ne pas s'accorder — et c'est
    précisément l'accord entre deux nuls que ce fichier mesure.
    """
    return M.nul_par_candidat(M.candidats_de_pas(nominal_um, bas=bas, haut=haut))


def le_nul_a_t_il_quelque_chose_a_dire(bas: float = 0.5, haut: float = 2.0) -> dict:
    """Le nul varie-t-il d'un candidat à l'autre — sinon, « pas d'écart » ne voudrait rien dire.

    ⭐⭐⭐ C'EST LE CONTRÔLE POSITIF, et sans lui tout ce fichier est vide. Si le nul était le même
    pour tous les candidats, deux fenêtres auraient forcément le même nul et l'invariance mesurée
    plus bas serait une propriété de la constante, pas du rééchantillonnage.

    Le nul existe justement parce qu'il n'est pas plat : un segment court rééchantillonné sur le
    même nombre de points est SUR-échantillonné, donc plus lisse, donc il corrèle mieux avec un
    gabarit lisse.
    """
    mu, sd = nul(173.0, bas, haut)
    amp = float(mu[0] - mu[-1])
    sigma = float(np.median(sd))
    # ⚠⚠ LA BONNE ÉCHELLE ICI EST L'ERREUR-TYPE DE LA MOYENNE, PAS LA DISPERSION. La question est
    # « la forme du nul est-elle mesurée ou tirée au sort », et une moyenne sur `tirages` tirages
    # a une erreur-type de σ/√n. Comparer l'amplitude à σ répondrait à une autre question — « un
    # score individuel varie-t-il autant » — et ma première version le faisait : elle déclarait
    # plat un nul qui varie de vingt-quatre erreurs-types.
    erreur_type = sigma / float(np.sqrt(NUL_TIRAGES))
    return {"decidable": True,
            "tirages": NUL_TIRAGES,
            "mu_du_plus_court": round(float(mu[0]), 4),
            "mu_du_plus_long": round(float(mu[-1]), 4),
            "amplitude": round(amp, 4),
            "sd_median": round(sigma, 5),
            "erreur_type_de_la_moyenne": round(erreur_type, 6),
            "amplitude_en_erreurs_types": round(amp / erreur_type, 1),
            "amplitude_en_sigma": round(amp / sigma, 2),
            "le_nul_est_plat": bool(abs(amp) < 3.0 * erreur_type)}


def le_nul_survit_il_au_recentrage(nominaux=NOMINAUX_UM, bas: float = 0.5,
                                   haut: float = 2.0) -> dict:
    """Changer le CENTRE de la fenêtre déplace-t-il le nul ?

    ⭐⭐⭐⭐ La réponse décide si `R4-P24` est bon marché. Le nul ne dépend que des **rapports**
    des longueurs à la plus longue, parce que `profils_emboites` rééchantillonne chaque candidat
    sur le même nombre de points. Une fenêtre mise à l'échelle garde ses rapports, donc son nul.

    ⚠ L'écart est rendu en absolu **et** en écarts-types du nul : un écart absolu ne dit pas s'il
    compte, et c'est la dispersion du nul lui-même qui donne l'échelle de ce qui compte.
    """
    ref_mu, ref_sd = nul(173.0, bas, haut)
    sigma = float(np.median(ref_sd))
    lignes = []
    for n in nominaux:
        mu, _ = nul(float(n), bas, haut)
        e = float(np.max(np.abs(mu - ref_mu)))
        lignes.append({"nominal_um": float(n), "ecart_max": e,
                       "ecart_en_sigma": round(e / sigma, 3)})
    pire = max(x["ecart_max"] for x in lignes)
    return {"decidable": True, "reference_um": 173.0, "sigma_du_nul": round(sigma, 5),
            "par_nominal": lignes, "ecart_max": pire,
            # ⚠ Le seuil n'est pas réglé : 1e-12 est le bruit du flottant sur des scores de
            # l'ordre de 0,1 en double précision, pas une tolérance choisie pour que ça passe.
            "le_nul_est_invariant": bool(pire < 1e-12)}


def le_nul_survit_il_a_lelargissement(fenetres=FENETRES, nominal_um: float = 173.0) -> dict:
    """Changer la LARGEUR de la fenêtre déplace-t-il le nul ?

    ⭐⭐⭐⭐ C'EST LA SONDE SYMÉTRIQUE, et elle est indispensable : un nul qui ne dépendrait de
    rien passerait le test du recentrage sans rien prouver. Si l'élargissement le déplace, alors
    l'invariance mesurée au recentrage est une propriété du rééchantillonnage et pas une
    indifférence de l'estimateur.

    ⚠ Élargir change les rapports — la plus courte devient plus courte RELATIVEMENT à la plus
    longue — donc le sur-échantillonnage de chaque candidat change, donc le nul aussi.
    """
    ref_mu, ref_sd = nul(nominal_um, *fenetres[0])
    sigma = float(np.median(ref_sd))
    lignes = []
    for bas, haut in fenetres:
        mu, _ = nul(nominal_um, bas, haut)
        e = float(np.max(np.abs(mu - ref_mu)))
        lignes.append({"bas": bas, "haut": haut, "ecart_max": round(e, 5),
                       "ecart_en_sigma": round(e / sigma, 2)})
    pire = max(x["ecart_max"] for x in lignes)
    return {"decidable": True, "reference": list(fenetres[0]),
            "sigma_du_nul": round(sigma, 5), "par_fenetre": lignes,
            "ecart_max": round(pire, 5), "ecart_max_en_sigma": round(pire / sigma, 2),
            "le_nul_bouge_a_lelargissement": bool(pire > sigma)}


def mesurer() -> dict:
    """Tout, sur du bruit tiré — aucune lecture distante, aucun volume touché."""
    return {"echantillons": M.ECHANTILLONS, "candidats": M.CANDIDATS,
            "fenetre_publiee": [M.FACTEUR_BAS, M.FACTEUR_HAUT],
            "pas_nominal_publie_um": 173.0,
            "le_nul_a_t_il_quelque_chose_a_dire": le_nul_a_t_il_quelque_chose_a_dire(),
            "le_nul_survit_il_au_recentrage": le_nul_survit_il_au_recentrage(),
            "le_nul_survit_il_a_lelargissement": le_nul_survit_il_a_lelargissement()}


def afficher(r: dict) -> None:
    c = r["le_nul_a_t_il_quelque_chose_a_dire"]
    print(f"nul par candidat · {r['candidats']} candidats · fenêtre publiée "
          f"{r['fenetre_publiee']} × {r['pas_nominal_publie_um']} µm")
    print(f"\n  contrôle positif : le nul va de {c['mu_du_plus_court']} (plus court) à "
          f"{c['mu_du_plus_long']} (plus long), soit {c['amplitude_en_erreurs_types']} "
          f"erreurs-types sur {c['tirages']} tirages ({c['amplitude_en_sigma']} σ)")
    print(f"  ⭐ le nul est plat : {c['le_nul_est_plat']}")
    d = r["le_nul_survit_il_au_recentrage"]
    print(f"\n  RECENTRER (σ du nul {d['sigma_du_nul']}) :")
    for x in d["par_nominal"]:
        print(f"    {x['nominal_um']:>6.1f} µm  écart max {x['ecart_max']:.2e}  "
              f"{x['ecart_en_sigma']:.3f} σ")
    print(f"  ⭐ le nul est invariant : {d['le_nul_est_invariant']}")
    e = r["le_nul_survit_il_a_lelargissement"]
    print("\n  ÉLARGIR :")
    for x in e["par_fenetre"]:
        print(f"    [{x['bas']:.2f} ; {x['haut']:.1f}]  écart max {x['ecart_max']:.5f}  "
              f"{x['ecart_en_sigma']:.1f} σ")
    print(f"  ⭐ le nul bouge à l'élargissement : {e['le_nul_bouge_a_lelargissement']}")


def verifier() -> int:
    """La batterie, hors ligne — et quatre sondes."""
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    # ⭐⭐⭐ LE CONTRÔLE POSITIF D'ABORD : sans lui, « pas d'écart » ne veut rien dire.
    c = le_nul_a_t_il_quelque_chose_a_dire()
    v("le nul n'est PAS plat d'un candidat à l'autre", not c["le_nul_est_plat"],
      f"{c['mu_du_plus_court']} → {c['mu_du_plus_long']}, "
      f"{c['amplitude_en_erreurs_types']} erreurs-types")
    v("... et le court score PLUS HAUT que le long, comme le biais le veut",
      c["mu_du_plus_court"] > c["mu_du_plus_long"])

    # ⭐⭐⭐⭐ LE RECENTRAGE EST EXACT.
    d = le_nul_survit_il_au_recentrage()
    v("le nul est invariant par recentrage", d["le_nul_est_invariant"],
      f"écart max {d['ecart_max']:.2e}")
    v("... sur toute la plage que la re-course demanderait",
      len(d["par_nominal"]) == len(NOMINAUX_UM))
    v("... et l'écart reste sous le bruit du flottant",
      all(x["ecart_max"] < 1e-12 for x in d["par_nominal"]))

    # ⭐⭐⭐⭐ LA SONDE SYMÉTRIQUE : un nul indifférent à tout passerait le test ci-dessus.
    e = le_nul_survit_il_a_lelargissement()
    v("sonde : élargir DÉPLACE le nul", e["le_nul_bouge_a_lelargissement"],
      f"{e['ecart_max_en_sigma']} σ")
    v("... et la fenêtre publiée est à zéro par construction",
      e["par_fenetre"][0]["ecart_max"] == 0.0)
    v("... et l'écart croît avec la largeur",
      [x["ecart_max"] for x in e["par_fenetre"]]
      == sorted(x["ecart_max"] for x in e["par_fenetre"]),
      f"{[x['ecart_max'] for x in e['par_fenetre']]}")

    # ⚠⚠ LA SONDE QUI TIENT TOUT : l'invariance vient des RAPPORTS. Une fenêtre mise à l'échelle
    # doit rendre le MÊME nul, une fenêtre dont un seul bout bouge doit en rendre un autre —
    # sinon le test ne mesure pas ce qu'on croit.
    a_mu, _ = nul(173.0, 0.5, 2.0)
    b_mu, _ = nul(346.0, 0.5, 2.0)
    v("sonde : doubler le centre rend le même nul",
      float(np.max(np.abs(a_mu - b_mu))) < 1e-12)
    c_mu, _ = nul(173.0, 0.5, 2.2)
    v("sonde : bouger un SEUL bout en rend un autre",
      float(np.max(np.abs(a_mu - c_mu))) > 1e-6,
      f"{float(np.max(np.abs(a_mu - c_mu))):.2e}")

    # ⚠ La graine est celle du nul publié : un tirage qui changerait à chaque lancement rendrait
    # un écart différent à chaque relecture, donc ne serait pas une mesure.
    v("le nul est reproductible",
      float(np.max(np.abs(nul(173.0, 0.5, 2.0)[0] - a_mu))) == 0.0)

    r = mesurer()
    v("la mesure rend ses trois sections",
      all(k in r for k in ("le_nul_a_t_il_quelque_chose_a_dire",
                           "le_nul_survit_il_au_recentrage",
                           "le_nul_survit_il_a_lelargissement")))
    afficher(r)

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
