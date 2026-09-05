#!/usr/bin/env python3
"""Quelle translation a le DROIT d'être appliquée, et ce qu'elle laisse derrière elle.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET CE N'EST PAS « CHOISIR LE MEILLEUR NOMBRE ».
`le_residu_est_une_translation` a mesuré que le désaccord entre les deux aplatissements est une
translation, et que sur l'encre son optimum est **(−24, 0)** cases. Appliquer ce nombre-là au
recalage et republier ensuite l'AUC de l'encre serait **circulaire** : l'accord serait élevé par
construction, et le chiffre ne mesurerait plus rien.

⭐⭐⭐ **La règle est donc de provenance, pas de valeur.** Une translation tirée de la
**géométrie** — silhouettes, carreaux de bord, repères — n'a jamais vu d'encre, donc l'encre
reste un arbitre extérieur après qu'on l'a appliquée. Une translation tirée de l'**encre** est
un plafond : elle dit ce qu'on pourrait gagner, jamais ce qu'on a le droit de retrancher.
`applicables()` implémente cette règle, et une candidate d'encre en est **exclue par
construction** plutôt que par vigilance.

⚠⚠ ET LA MESURE QUI COMPTE EST L'ÉCART ENTRE LES DEUX. Si la meilleure candidate géométrique
tombe sur l'optimum de l'encre, la géométrie suffit à recaler. Si elle en est loin, alors une
part du désaccord est **invisible aux silhouettes**, et c'est une borne sur ce qu'un recalage
purement géométrique pourra jamais rendre — ce qui est exactement ce que `75` a besoin de savoir
avant de densifier quoi que ce soit.

⚠ Deux façons d'appliquer la même translation doivent donner le même résultat : corriger
l'**affine** ou décaler la **lecture**. Elles sont mesurées toutes les deux et comparées, parce
qu'une erreur de signe dans la correction ne ressemble pas à une panne — elle dégrade doucement.

Usage :
    uv run python src/encre/la_translation_applicable.py --verifier
    uv run python src/encre/la_translation_applicable.py \\
        --json docs/mesures/la_translation_applicable.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "encre"))

RECALAGE = RACINE / "docs" / "mesures" / "le_recalage_des_etiquettes.json"
RESIDU = RACINE / "docs" / "mesures" / "le_residu_est_une_translation.json"

GEOMETRIE = "géométrie"
ENCRE = "encre"


def corriger(transformation: dict, di: float, dj: float) -> dict:
    """
    @brief La même affine, dont les décalages absorbent la translation `(di, dj)`.

    ⚠⚠⚠ LE SIGNE EST DÉRIVÉ DE `appliquer`, PAS CHOISI. Cette fonction rend `out[l] =
    source[(l − d)/e]`, et la translation mesurée dit que les étiquettes justes en `l` sont
    celles que l'ancienne transformation mettait en `l + di`. Donc
    $(l - d')/e = (l + d_i - d)/e$, d'où $d' = d - d_i$ : les décalages **retranchent** la
    translation. L'écrire dans l'autre sens double l'erreur au lieu de la corriger, et une
    affine doublement fausse ne lève rien — elle rend juste un accord plus bas.

    ⚠ Les **échelles** ne bougent pas : une translation est une translation. Si le résidu avait
    une composante d'échelle, elle apparaîtrait comme une dispersion des optima par fenêtre
    corrélée à la position, ce que `le_residu_est_une_translation` mesure séparément.
    """
    out = dict(transformation)
    out["decalage_lignes"] = transformation["decalage_lignes"] - di
    out["decalage_colonnes"] = transformation["decalage_colonnes"] - dj
    return out


def candidats(recalage: dict, residu: dict) -> list[dict]:
    """Les translations en jeu, chacune avec la PROVENANCE qui décide de son usage.

    ⚠ La provenance est portée par la donnée et non déduite d'un nom : un jour quelqu'un
    ajoutera une candidate, et « celles dont le nom contient encre » serait une règle qui
    s'use.
    """
    out = []
    sil = residu.get("accord_des_silhouettes", {}).get("meilleur")
    if sil:
        out.append(dict(nom="optimum des silhouettes", provenance=GEOMETRIE,
                        decalage=[float(sil["di"]), float(sil["dj"])],
                        critere="Dice du masque recalé contre le support publié"))
    cb = residu.get("constante_des_bords")
    if cb:
        out.append(dict(nom="médiane des carreaux de bord", provenance=GEOMETRIE,
                        decalage=[float(cb[0]), float(cb[1])],
                        critere="médiane des 34 décalages de recouvrement"))
    cr = residu.get("constante_des_reperes")
    if cr:
        out.append(dict(nom="médiane des repères intérieurs", provenance=GEOMETRIE,
                        decalage=[float(cr[0]), float(cr[1])],
                        critere="médiane des 55 appariements de trous"))
    bal = residu.get("balayage", {}).get("meilleur")
    if bal:
        out.append(dict(nom="optimum sur l'encre", provenance=ENCRE,
                        decalage=[float(bal["di"]), float(bal["dj"])],
                        critere="AUC médiane de la carte publiée sur 127 fenêtres"))
    out.insert(0, dict(nom="aucune correction", provenance=GEOMETRIE, decalage=[0.0, 0.0],
                       critere="l'affine publiée, telle quelle"))
    return out


def applicables(liste: list[dict]) -> list[dict]:
    """Celles qu'on a le droit d'appliquer : uniquement les géométriques.

    ⚠⚠ C'est la règle entière du fichier, et elle est ici plutôt que dans une consigne : une
    candidate ajustée sur l'encre rendrait l'encre juge et partie, donc tout chiffre d'encre
    mesuré à travers elle cesserait d'être une mesure. Le refus est **par construction** — la
    fonction ne la rend pas — et non par une note qu'un appelant pressé sauterait.
    """
    return [c for c in liste if c["provenance"] != ENCRE]


def ecart(a: dict, b: dict) -> float:
    """La distance entre deux candidates, en cases."""
    return float(np.hypot(a["decalage"][0] - b["decalage"][0],
                          a["decalage"][1] - b["decalage"][1]))


def _accord(carte: np.ndarray, etiquettes: np.ndarray) -> tuple[float | None, int, int]:
    """L'AUC de la carte publiée contre des étiquettes DÉJÀ dans son repère, et ses deux comptes."""
    from le_nul_verso import aire_sous_la_courbe  # noqa: PLC0415

    dans = (carte > 0) & np.isfinite(carte)
    encre = etiquettes > 0.5
    a = carte[dans & encre].ravel()
    b = carte[dans & ~encre].ravel()
    if a.size < 100 or b.size < 100:
        return None, int(a.size), int(b.size)
    return float(aire_sous_la_courbe(a, b)), int(a.size), int(b.size)


def juger(candidate: dict, masque: np.ndarray, etiquettes: np.ndarray, carte: np.ndarray,
          base: dict, empreinte_reduite: np.ndarray) -> dict:
    """Ce que vaut une candidate une fois **appliquée à l'affine** : silhouettes, puis encre.

    ⚠⚠ Les silhouettes d'abord et l'encre ensuite, dans cet ordre et pas l'inverse : le Dice est
    le critère que les candidates géométriques optimisent, donc c'est là qu'elles doivent
    montrer qu'elles font ce qu'elles prétendent. L'AUC vient après, en **arbitre extérieur**,
    et n'est une mesure que pour celles qui n'ont jamais vu l'encre.
    """
    import le_recalage_des_etiquettes as rec  # noqa: PLC0415

    di, dj = candidate["decalage"]
    t = corriger(base, di, dj)
    m = rec.appliquer(masque, t, carte.shape)
    e = rec.appliquer(etiquettes, t, carte.shape)
    dice = rec.dice(rec._reduire(m, rec.COTE_VALIDATION), empreinte_reduite)
    auc, pe, pf = _accord(carte, e)
    return dict(nom=candidate["nom"], provenance=candidate["provenance"],
                decalage=[round(di, 2), round(dj, 2)],
                transformation_corrigee={k: v for k, v in t.items()
                                         if k.startswith(("echelle", "decalage"))},
                dice=round(dice, 6), auc=None if auc is None else round(auc, 5),
                pixels_encre=pe, pixels_fond=pf)


def equivalence(candidate: dict, masque_etiquettes: np.ndarray, carte: np.ndarray,
                base: dict) -> dict:
    """Corriger l'AFFINE et décaler la LECTURE donnent-ils le même accord ?

    ⚠⚠⚠ C'EST LE CONTRÔLE DU SIGNE, et il ne peut pas être remplacé par une relecture. Une
    correction appliquée à l'envers ne lève rien : elle rend un accord plus bas, ce qui ressemble
    à une mauvaise candidate et non à un bug. Les deux chemins doivent tomber sur le même
    nombre — au bord près, parce que décaler la lecture **ampute** la fenêtre commune alors que
    corriger l'affine rend une image entière.
    """
    import le_recalage_des_etiquettes as rec  # noqa: PLC0415

    di, dj = int(round(candidate["decalage"][0])), int(round(candidate["decalage"][1]))
    par_laffine = rec.appliquer(masque_etiquettes, corriger(base, di, dj), carte.shape)
    ancien = rec.appliquer(masque_etiquettes, base, carte.shape)
    h, w = carte.shape
    i0, i1 = max(0, di), min(h, h + di)
    j0, j1 = max(0, dj), min(w, w + dj)
    # ⚠ La même fenêtre des deux côtés : comparer une image entière à une image amputée ferait
    # porter l'écart par la bordure et non par la correction.
    a1, _, _ = _accord(carte[i0 - di:i1 - di, j0 - dj:j1 - dj],
                       ancien[i0:i1, j0:j1])
    a2, _, _ = _accord(carte[i0 - di:i1 - di, j0 - dj:j1 - dj],
                       par_laffine[i0 - di:i1 - di, j0 - dj:j1 - dj])
    return dict(decalage=[di, dj],
                auc_par_lecture=None if a1 is None else round(a1, 5),
                auc_par_laffine=None if a2 is None else round(a2, 5),
                ecart=None if a1 is None or a2 is None else round(abs(a1 - a2), 5))


def mesurer() -> dict:
    """Le dossier : chaque candidate jugée, et l'écart entre géométrie et encre."""
    import le_recalage_des_etiquettes as rec  # noqa: PLC0415

    if not RECALAGE.is_file() or not RESIDU.is_file():
        raise SystemExit("mesures antérieures absentes")
    recalage = json.loads(RECALAGE.read_text())
    residu = json.loads(RESIDU.read_text())
    masque, etiquettes = rec._image("500P2_mask.png"), rec._image("500P2_inklabels.png")
    publiee = rec.carte_publiee_reduite()
    if masque is None or etiquettes is None or publiee is None:
        raise SystemExit("carte publiée ou masque absents")
    carte, nom = publiee
    empreinte = (carte > 0).astype(float)
    base = rec.affine_par_boites(masque, empreinte)
    # ⚠ L'empreinte réduite est calculée UNE fois : elle ne dépend d'aucune candidate, et la
    # réduire par candidate ferait payer une minute pour le même tableau.
    emp_red = rec._reduire(empreinte, rec.COTE_VALIDATION)

    liste = candidats(recalage, residu)
    jugees = [juger(c, masque, etiquettes, carte, base, emp_red) for c in liste]
    permis = {c["nom"] for c in applicables(liste)}
    for j in jugees:
        j["applicable"] = j["nom"] in permis

    geo = [j for j in jugees if j["applicable"] and j["decalage"] != [0.0, 0.0]]
    # ⚠⚠ La retenue est celle qui maximise le DICE, pas l'AUC : le critère est déclaré avant de
    # regarder l'encre, sinon « la meilleure candidate géométrique » serait choisie sur l'encre
    # et la règle de provenance ne servirait à rien.
    retenue = max(geo, key=lambda j: j["dice"]) if geo else None
    plafond = next((j for j in jugees if not j["applicable"]), None)
    sans = next((j for j in jugees if j["decalage"] == [0.0, 0.0]), None)

    # ⚠⚠⚠ LA PART DU PLAFOND EST RENDUE PAR CANDIDATE, ET C'EST ELLE QUI DIT LE RÉSULTAT. Une
    # seule « retenue » laisserait croire que la géométrie donne UNE réponse ; quatre critères
    # sans encre en donnent quatre, et l'étalement de leurs parts est la mesure de ce que la
    # géométrie ne sait pas trancher.
    if sans and plafond and sans["auc"] and plafond["auc"]:
        total = plafond["auc"] - sans["auc"]
        for j in jugees:
            j["part_du_plafond"] = (round((j["auc"] - sans["auc"]) / total, 4)
                                    if j["auc"] is not None and total > 0 else None)
    # ⚠⚠ Et le fait le plus dur à voir autrement : une candidate peut faire BAISSER le Dice tout
    # en faisant monter l'AUC. Le critère des silhouettes n'est alors pas seulement faible, il
    # est en partie contraire à celui qui compte — donc le compter est obligatoire.
    if sans:
        for j in jugees:
            j["degrade_le_dice"] = bool(j["dice"] < sans["dice"])
    geos = [j for j in jugees if j["applicable"] and j["decalage"] != [0.0, 0.0]]
    etalement = max((float(np.hypot(a["decalage"][0] - b["decalage"][0],
                                    a["decalage"][1] - b["decalage"][1]))
                     for a in geos for b in geos), default=0.0)
    parts = [j["part_du_plafond"] for j in geos if j.get("part_du_plafond") is not None]

    out = dict(carte_publiee=nom, cote_de_validation=rec.COTE_VALIDATION,
               etalement_des_candidates_geometriques=round(etalement, 2),
               part_du_plafond_min=round(min(parts), 4) if parts else None,
               part_du_plafond_max=round(max(parts), 4) if parts else None,
               candidates_qui_degradent_le_dice=[j["nom"] for j in jugees
                                                 if j.get("degrade_le_dice")],
               transformation_publiee={k: v for k, v in base.items()
                                       if k.startswith(("echelle", "decalage"))},
               candidates=jugees, retenue=retenue, plafond=plafond, sans_correction=sans)
    if retenue and plafond:
        cr = next(c for c in liste if c["nom"] == retenue["nom"])
        cp = next(c for c in liste if c["nom"] == plafond["nom"])
        out["ecart_geometrie_encre_cases"] = round(ecart(cr, cp), 2)
        out["ecart_geometrie_encre_um"] = round(ecart(cr, cp) * residu["cellule_um"], 1)
        if sans and retenue["auc"] and plafond["auc"] and sans["auc"]:
            gagne, total = retenue["auc"] - sans["auc"], plafond["auc"] - sans["auc"]
            out["part_du_plafond_atteinte"] = (round(gagne / total, 4) if total > 0 else None)
    if retenue:
        out["equivalence"] = equivalence(
            next(c for c in liste if c["nom"] == retenue["nom"]), etiquettes, carte, base)
    return out


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    t = dict(echelle_lignes=0.5, echelle_colonnes=0.25,
             decalage_lignes=10.0, decalage_colonnes=-5.0)
    c = corriger(t, -24.0, 3.0)
    v("la correction RETRANCHE la translation des décalages",
      c["decalage_lignes"] == 34.0 and c["decalage_colonnes"] == -8.0, str(c))
    v("... et ne touche pas les échelles",
      c["echelle_lignes"] == 0.5 and c["echelle_colonnes"] == 0.25)
    v("une translation nulle laisse l'affine intacte", corriger(t, 0.0, 0.0) == t)
    v("... et l'original n'est pas modifié", t["decalage_lignes"] == 10.0)

    # ⚠⚠⚠ LE SIGNE, VÉRIFIÉ CONTRE `appliquer` ET NON CONTRE MA PROSE. Une source dont la ligne
    # porte son propre numéro rend le test lisible : après correction de `di`, la cible doit
    # porter en `l` ce qu'elle portait en `l + di`.
    import le_recalage_des_etiquettes as rec  # noqa: PLC0415

    src = np.tile(np.arange(200, dtype=float).reshape(-1, 1), (1, 8))
    ident = dict(echelle_lignes=1.0, echelle_colonnes=1.0,
                 decalage_lignes=0.0, decalage_colonnes=0.0)
    avant = rec.appliquer(src, ident, (200, 8))
    apres = rec.appliquer(src, corriger(ident, -5.0, 0.0), (200, 8))
    v("après correction, la cible porte en l ce qu'elle portait en l + di",
      bool(np.array_equal(apres[10:100, 0], avant[5:95, 0])),
      f"{apres[10, 0]} contre {avant[5, 0]}")
    # ⚠ Le contrôle inverse : corriger dans l'autre sens NE DOIT PAS coïncider, sinon le premier
    # passerait pour une identité.
    autre = rec.appliquer(src, corriger(ident, 5.0, 0.0), (200, 8))
    v("... et corriger à l'envers ne donne pas la même chose",
      not np.array_equal(autre[10:100, 0], avant[5:95, 0]))

    # --- la règle de provenance ---
    faux_recalage = {}
    faux_residu = {"accord_des_silhouettes": {"meilleur": {"di": -8, "dj": -8}},
                   "constante_des_bords": [-13.0, 2.0],
                   "constante_des_reperes": [-3.2, 8.2],
                   "balayage": {"meilleur": {"di": -24, "dj": 0}}}
    liste = candidats(faux_recalage, faux_residu)
    v("les cinq candidates sont là, l'affine publiée comprise", len(liste) == 5, str(len(liste)))
    v("... et la première est l'absence de correction", liste[0]["decalage"] == [0.0, 0.0])
    permis = applicables(liste)
    v("l'optimum sur l'encre est EXCLU des applicables",
      all(c["nom"] != "optimum sur l'encre" for c in permis)
      and any(c["nom"] == "optimum sur l'encre" for c in liste), str(len(permis)))
    v("... et les quatre géométriques restent", len(permis) == 4, str(len(permis)))
    # ⚠⚠ Sans ce contrôle, `applicables` pourrait rendre la liste vide et « aucune candidate
    # d'encre n'est passée » serait satisfait par le refus de tout.
    v("... donc le filtre n'est pas un refus général",
      any(c["provenance"] == GEOMETRIE for c in permis))
    v("l'écart entre deux candidates est une distance",
      abs(ecart(liste[1], liste[-1]) - float(np.hypot(-8 + 24, -8 - 0))) < 1e-9,
      str(ecart(liste[1], liste[-1])))

    # --- l'accord, sur une fixture dont la réponse est connue ---
    carte = np.zeros((60, 60))
    carte[10:50, 10:50] = 60.0
    carte[20:30, 20:30] = 220.0
    eti = np.zeros((60, 60))
    eti[20:30, 20:30] = 1.0
    a, pe, pf = _accord(carte, eti)
    v("l'accord est parfait quand les étiquettes tombent sur l'encre", a == 1.0, str(a))
    v("... et les deux comptes sont rendus", pe == 100 and pf == 1500, f"{pe}/{pf}")
    b, _, _ = _accord(carte, np.zeros((60, 60)))
    v("... et il refuse quand une population manque", b is None)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
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
    print(f"{'candidate':<32} {'provenance':<11} {'décalage':>12} {'Dice':>9} {'AUC':>8}  appl.")
    print("-" * 82)
    for c in r["candidates"]:
        print(f"{c['nom']:<32} {c['provenance']:<11} "
              f"{str(tuple(c['decalage'])):>12} {c['dice']:>9.6f} "
              f"{(c['auc'] if c['auc'] is not None else float('nan')):>8.4f}"
              f"  {'oui' if c['applicable'] else 'NON'}")
    if r.get("retenue"):
        print(f"\nretenue (meilleur Dice parmi les applicables) : {r['retenue']['nom']} "
              f"{tuple(r['retenue']['decalage'])}")
    if r.get("ecart_geometrie_encre_cases") is not None:
        print(f"écart géométrie / encre : {r['ecart_geometrie_encre_cases']} cases "
              f"= {r['ecart_geometrie_encre_um']} µm")
    if r.get("part_du_plafond_atteinte") is not None:
        print(f"part du plafond atteinte par la retenue : "
              f"{r['part_du_plafond_atteinte'] * 100:.1f} %")
    if r.get("part_du_plafond_max") is not None:
        print(f"les quatre critères géométriques s'étalent sur "
              f"{r['etalement_des_candidates_geometriques']} cases et atteignent de "
              f"{r['part_du_plafond_min'] * 100:.1f} % à {r['part_du_plafond_max'] * 100:.1f} % "
              f"du plafond")
    if r.get("candidates_qui_degradent_le_dice"):
        print(f"⚠ font BAISSER le Dice : "
              f"{', '.join(r['candidates_qui_degradent_le_dice'])}")
    if r.get("equivalence"):
        e = r["equivalence"]
        print(f"équivalence affine / lecture : {e['auc_par_laffine']} contre "
              f"{e['auc_par_lecture']}, écart {e['ecart']}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
