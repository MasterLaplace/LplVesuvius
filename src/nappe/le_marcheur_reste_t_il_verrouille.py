#!/usr/bin/env python3
"""Le marcheur reste-t-il verrouillé sur les feuilles, ou sa phase dérive-t-elle ?

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST LA QUESTION DU GRAAL POSÉE SUR LE BON AXE. `119` a mesuré que la
trajectoire ne dérive pas : la rectitude tient et les virages se compensent. Ça dit **où** le
marcheur va, pas **sur quelle feuille il tombe**. Un marcheur peut aller parfaitement droit en
atterrissant chaque fois un tiers de feuille trop loin, et c'est exactement ce que l'humain corrige
d'une spire à l'autre.

⚠⚠ **ET LA QUESTION N'EST PAS MESURABLE SUR LE VRAI VOLUME**, parce qu'on n'y connaît pas où sont
les feuilles. Sur une pile **fabriquée**, la phase est connue à chaque point : on peut donc dire, au
centième de feuille près, où le marcheur a atterri. C'est pour ça que ce document est analytique.

⭐⭐⭐⭐ **LE MARCHEUR PREND UN DÉCALAGE ET LE GARDE.** Il atterrit systématiquement **après** la
feuille, et l'écart ne grandit pas avec la profondeur sur une pile propre : il l'acquiert au premier
pas et le tient. Un décalage constant ne fait pas rater de feuille ; un décalage qui grandit, si.

⚠⚠ **Ce que ça ne dit pas** : le vrai rouleau n'est pas une pile plane à pas constant. Ce qui est
établi ici est une propriété du **mécanisme**, pas du rouleau — au même titre que `controle_fabrique`
établit que le témoin naïf échoue dès qu'il y a de l'obliquité.

⚠ Aucune lecture distante : tout est analytique.

  uv run python src/nappe/le_marcheur_reste_t_il_verrouille.py --verifier
  uv run python src/nappe/le_marcheur_reste_t_il_verrouille.py \
      --json docs/mesures/le_marcheur_reste_t_il_verrouille.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

MARCHES = 12
PAS = 20
CONDITIONS = ((0.0, 0.0), (0.0, 8.0), (35.0, 0.0), (35.0, 8.0))
"""Les quatre conditions : deux obliquités × deux niveaux de bruit.

⚠ 35° est l'obliquité que `controle_fabrique` utilise déjà, et 8 le niveau de bruit pour lequel
`accord_des_moities` publie sa calibration. Les reprendre plutôt que d'en choisir d'autres évite
qu'un résultat dépende d'un réglage propre à ce fichier."""


def _outils(demi: int):
    """Les barres et le nul, montés une fois — ils ne dépendent pas de la pile."""
    import combien_dinterstices_traverses as C
    import le_pas_que_la_matiere_montre as M
    from la_direction_que_la_matiere_montre import nul_du_tenseur

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs, tirages=300)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd,
                                                            tirages=150).values())
    return {"C": C, "M": M, "longueurs": longueurs, "mu": mu, "sd": sd, "barre": barre,
            "barre_moities": nul_du_tenseur(tirages=40, demi=demi)["accord_des_moities_p1_deg"],
            "barre_interstice": max(x["p99"]
                                    for x in C.accord_du_bruit_pur(tirages=200).values())}


def phases(pile, depart, etapes, voxel_um: float,
           origine_proj_um: float | None = None) -> list[float]:
    """La phase — en feuilles — de chaque atterrissage, comptée depuis le départ.

    ⭐⭐⭐ C'EST CE QUE LE VRAI VOLUME NE PEUT PAS RENDRE. La pile est analytique, donc la position
    d'une feuille est connue partout : la phase d'un point est sa projection sur la normale divisée
    par le pas. Une phase entière veut dire « sur une feuille ».

    ⚠ La projection est reprise du point REELLEMENT atteint, pas de la distance parcourue : la
    marche s'écarte de la normale, donc `parcouru / pas` surestimerait l'avance d'autant.
    """
    p = np.asarray(depart, dtype=np.float64).copy()
    # ⚠⚠ L'ORIGINE PAR DÉFAUT EST LE DÉPART DE LA MARCHE, et c'est juste tant que toutes les
    # marches d'un lot partent de la même projection — ce qui est le cas de `124`, dont l'écart
    # latéral est orthogonal à la normale. Dès qu'un lot porte des départs DÉCALÉS le long de la
    # normale, il faut une origine COMMUNE : sinon un décrochement injecté au départ devient
    # invisible, chaque marche le comptant depuis son propre zéro. La sonde de `126` a trouvé
    # exactement ça.
    depart_proj = (float(p @ pile.normale) * voxel_um if origine_proj_um is None
                   else float(origine_proj_um))
    out = []
    for e in etapes:
        p = p + np.asarray(e["direction"], dtype=np.float64) * (e["avance_um"] / voxel_um)
        out.append((float(p @ pile.normale) * voxel_um - depart_proj) / pile.pas_um)
    return out


def une_marche(o, pile, depart, x_hat, pas: int, demi: int, impose_um: float | None = None):
    """Une marche sur la pile, et les phases de ses atterrissages."""
    from combien_de_pas_la_matiere_porte import marcher

    etapes = [e for e in marcher(
        pile, depart, x_hat, o["longueurs"], o["mu"], o["sd"], o["barre"], o["barre_moities"],
        o["barre_interstice"], o["C"].VOXEL_FIN_UM, pas_max=pas, demi=demi,
        interroge_la_matiere=impose_um is None,
        pas_impose_um=impose_um, direction_imposee=None if impose_um is None else x_hat)
        if "confirme" in e]
    return etapes, phases(pile, depart, etapes, o["C"].VOXEL_FIN_UM)


def _ecarts(ph: list[float]) -> list[float]:
    """L'écart à la feuille la plus proche, en feuilles, dans [-0,5 ; 0,5]."""
    return [float(x - round(x)) for x in ph]


def le_marcheur_reste_t_il_verrouille(obliquite_deg: float, bruit: float, marches: int = MARCHES,
                                      pas: int = PAS, demi: int = 20) -> dict:
    """Le décalage à la feuille grandit-il avec la profondeur ?

    ⭐⭐⭐⭐ C'EST LE TEST DE L'ACCUMULATION, SUR L'AXE QUI COMPTE. `119` a montré que la direction
    ne dérive pas ; ici on demande si l'ATTERRISSAGE dérive. Un décalage constant est sans
    conséquence — le marcheur franchit la même feuille à chaque fois — alors qu'un décalage qui
    grandit finit par faire manquer une feuille, et c'est la panne que l'humain répare.

    ⚠⚠ Les marches partent de phases DIFFÉRENTES, tirées régulièrement sur une feuille : partir
    toujours d'une feuille mesurerait la réponse du marcheur à une seule mise en place, et un
    décalage acquis au premier pas ressemblerait à une propriété du mécanisme.

    ⚠ L'unité du test est la MARCHE : les pas d'une marche partagent son départ.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique

    o = _outils(demi)
    C = o["C"]
    x_hat = np.array([0.0, 0.0, 1.0])
    pile = VolumeFabrique(C.PAS_UM, obliquite_deg=obliquite_deg, bruit=bruit)
    debut, fin, toutes = [], [], []
    for i in range(marches):
        base = np.array([2000.0, 2000.0, 2000.0])
        proj = float(base @ pile.normale) * C.VOXEL_FIN_UM
        # ⚠ Le départ est glissé sur la feuille puis décalé d'une fraction connue : les marches
        # balaient donc la feuille au lieu de répéter la même mise en place.
        cible = round(proj / C.PAS_UM) * C.PAS_UM + (i / marches) * C.PAS_UM
        dep = base + pile.normale * ((cible - proj) / C.VOXEL_FIN_UM)
        etapes, ph = une_marche(o, pile, dep, x_hat, pas, demi)
        if len(ph) < 6:
            continue
        ec = _ecarts(ph)
        t = max(1, len(ec) // 3)
        debut.append(float(np.median(np.abs(ec[:t]))))
        fin.append(float(np.median(np.abs(ec[-t:]))))
        toutes.append({"depart_dans_la_feuille": round(i / marches, 3),
                       "pas": len(ph), "ecart_median": round(float(np.median(ec)), 4),
                       "phase_finale": round(ph[-1], 3),
                       "avance_par_pas": round(ph[-1] / len(ph), 4)})
    if len(debut) < 6:
        return {"decidable": False, "pourquoi": f"{len(debut)} marches exploitables"}
    p = float(stats.wilcoxon(debut, fin).pvalue) if any(
        a != b for a, b in zip(debut, fin)) else None
    return {
        "decidable": True, "obliquite_deg": obliquite_deg, "bruit": bruit,
        "marches": len(debut), "pas": pas,
        "ecart_median_premier_tiers": round(float(np.median(debut)), 4),
        "ecart_median_dernier_tiers": round(float(np.median(fin)), 4),
        "p_appariee": round(p, 4) if p is not None else None,
        "avance_par_pas_mediane": round(
            float(np.median([m["avance_par_pas"] for m in toutes])), 4),
        "par_marche": toutes,
        "le_decalage_grandit": bool(p is not None
                                    and float(np.median(fin)) > float(np.median(debut))
                                    and p < 0.05)}


def temoin_le_pas_impose_derive(obliquite_deg: float = 35.0, marches: int = MARCHES,
                                pas: int = PAS, demi: int = 20) -> dict:
    """Le contrôle positif : un pas NOMINAL imposé sur une pile oblique DOIT dériver.

    ⭐⭐⭐⭐ SANS LUI, « le décalage ne grandit pas » ne dit rien. Un test qui ne verrait jamais
    grandir un décalage serait satisfait par un marcheur parfait comme par un instrument aveugle.
    Le naïf avance du pas nominal le long du rayon ; sur une pile inclinée de 35° il franchit
    `cos(35°)` de feuille par pas, donc son décalage grandit d'environ 0,18 feuille par pas — une
    dérive connue d'avance, et c'est ce qui en fait un étalon.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique

    o = _outils(demi)
    C = o["C"]
    x_hat = np.array([0.0, 0.0, 1.0])
    pile = VolumeFabrique(C.PAS_UM, obliquite_deg=obliquite_deg)
    debut, fin = [], []
    for i in range(marches):
        base = np.array([2000.0, 2000.0, 2000.0])
        proj = float(base @ pile.normale) * C.VOXEL_FIN_UM
        cible = round(proj / C.PAS_UM) * C.PAS_UM + (i / marches) * C.PAS_UM
        dep = base + pile.normale * ((cible - proj) / C.VOXEL_FIN_UM)
        _, ph = une_marche(o, pile, dep, x_hat, pas, demi, impose_um=C.PAS_UM)
        if len(ph) < 6:
            continue
        ec = _ecarts(ph)
        t = max(1, len(ec) // 3)
        debut.append(float(np.median(np.abs(ec[:t]))))
        fin.append(float(np.median(np.abs(ec[-t:]))))
    if len(debut) < 6:
        return {"decidable": False, "pourquoi": f"{len(debut)} marches exploitables"}
    p = float(stats.wilcoxon(debut, fin).pvalue) if any(
        a != b for a, b in zip(debut, fin)) else None
    return {"decidable": True, "obliquite_deg": obliquite_deg, "marches": len(debut),
            "ecart_median_premier_tiers": round(float(np.median(debut)), 4),
            "ecart_median_dernier_tiers": round(float(np.median(fin)), 4),
            "p_appariee": round(p, 4) if p is not None else None,
            "avance_attendue_par_pas": round(float(np.cos(np.deg2rad(obliquite_deg))), 4),
            "le_decalage_grandit": bool(p is not None
                                        and float(np.median(fin)) > float(np.median(debut))
                                        and p < 0.05)}


def mesurer(conditions=CONDITIONS, demi: int = 20) -> dict:
    """Les quatre conditions, plus le témoin — tout analytique."""
    out = {"marches_par_condition": MARCHES, "pas": PAS, "conditions": []}
    for obl, bruit in conditions:
        out["conditions"].append(le_marcheur_reste_t_il_verrouille(obl, bruit, demi=demi))
    out["temoin_le_pas_impose_derive"] = temoin_le_pas_impose_derive(demi=demi)
    return out


def afficher(r: dict) -> None:
    print(f"{r['marches_par_condition']} marches par condition · {r['pas']} pas")
    print("\n  obliquité  bruit   écart 1er tiers   dernier tiers      p   grandit")
    for c in r["conditions"]:
        if not c.get("decidable"):
            continue
        print(f"    {c['obliquite_deg']:>5.1f}°  {c['bruit']:>5.1f}   "
              f"{c['ecart_median_premier_tiers']:>13.4f}   {c['ecart_median_dernier_tiers']:>13.4f}"
              f"   {c['p_appariee']!s:>6}   {c['le_decalage_grandit']}")
        print(f"            avance médiane par pas : {c['avance_par_pas_mediane']} feuille")
    t = r["temoin_le_pas_impose_derive"]
    if t.get("decidable"):
        print(f"\n  témoin, pas nominal imposé à {t['obliquite_deg']}° : "
              f"{t['ecart_median_premier_tiers']} → {t['ecart_median_dernier_tiers']} "
              f"(p {t['p_appariee']}) · grandit : {t['le_decalage_grandit']}")
        print(f"  avance attendue par pas : {t['avance_attendue_par_pas']} feuille")


def verifier() -> int:
    """La batterie, hors ligne — et les contrôles qui rendent le résultat lisible."""
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    # ⭐⭐ La phase est calculee juste : sur une pile plane, un deplacement d'un pas le long de la
    # normale avance d'exactement une feuille.
    from combien_de_pas_la_matiere_porte import VolumeFabrique
    import combien_dinterstices_traverses as C

    pile = VolumeFabrique(C.PAS_UM)
    dep = np.array([2000.0, 2000.0, 2000.0])
    faux = [{"direction": [0.0, 0.0, 1.0], "avance_um": C.PAS_UM} for _ in range(4)]
    ph = phases(pile, dep, faux, C.VOXEL_FIN_UM)
    v("un pas le long de la normale avance d'une feuille",
      all(abs(x - (i + 1)) < 1e-9 for i, x in enumerate(ph)), f"{ph}")
    # ⚠ Et un pas OBLIQUE avance de moins : c'est ce que le temoin naif subit.
    obl = VolumeFabrique(C.PAS_UM, obliquite_deg=60.0)
    ph2 = phases(obl, dep, faux, C.VOXEL_FIN_UM)
    # ⚠⚠ Une ORIGINE COMMUNE rend visible un départ décalé, ce que l'origine par défaut cache.
    dec = np.asarray(dep, dtype=np.float64) + pile.normale * (C.PAS_UM / C.VOXEL_FIN_UM)
    o0 = float(np.asarray(dep) @ pile.normale) * C.VOXEL_FIN_UM
    v("un depart decale d'une feuille est INVISIBLE sans origine commune",
      abs(phases(pile, dec, faux, C.VOXEL_FIN_UM)[0] - 1.0) < 1e-9)
    v("... et visible avec", abs(phases(pile, dec, faux, C.VOXEL_FIN_UM, o0)[0] - 2.0) < 1e-9,
      f"{phases(pile, dec, faux, C.VOXEL_FIN_UM, o0)[0]}")
    v("un pas oblique avance de cos(theta) feuille",
      abs(ph2[0] - np.cos(np.deg2rad(60.0))) < 1e-9, f"{ph2[0]:.4f}")
    v("les ecarts sont ramenes dans [-0,5 ; 0,5]",
      all(-0.5 <= x <= 0.5 for x in _ecarts([0.2, 0.8, 1.5, -0.3, 12.49])))

    r = mesurer(conditions=((0.0, 0.0), (35.0, 0.0)), demi=20)
    propre = r["conditions"][0]
    v("la condition propre est decidable", propre["decidable"])
    # ⭐⭐⭐⭐ LE RESULTAT : sur une pile propre, le decalage ne grandit pas.
    v("sur une pile propre, le decalage ne grandit pas", not propre["le_decalage_grandit"],
      f"{propre['ecart_median_premier_tiers']} → {propre['ecart_median_dernier_tiers']}, "
      f"p {propre['p_appariee']}")
    v("... et l'avance par pas reste proche d'une feuille",
      abs(propre["avance_par_pas_mediane"] - 1.0) < 0.1,
      f"{propre['avance_par_pas_mediane']}")
    # ⭐⭐⭐⭐ LE TEMOIN POSITIF : sans lui, « ne grandit pas » serait sans puissance.
    t = r["temoin_le_pas_impose_derive"]
    v("temoin : un pas nominal impose sur une pile oblique DERIVE", t["le_decalage_grandit"],
      f"{t['ecart_median_premier_tiers']} → {t['ecart_median_dernier_tiers']}, "
      f"p {t['p_appariee']}")
    v("... et son avance attendue est cos(35°)",
      abs(t["avance_attendue_par_pas"] - float(np.cos(np.deg2rad(35.0)))) < 1e-4)
    v("les marches partent de phases differentes",
      len({m["depart_dans_la_feuille"] for m in propre["par_marche"]}) >= 6,
      f"{len({m['depart_dans_la_feuille'] for m in propre['par_marche']})}")
    v("moins de six marches rend indecidable",
      not le_marcheur_reste_t_il_verrouille(0.0, 0.0, marches=3, pas=20)["decidable"])
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
