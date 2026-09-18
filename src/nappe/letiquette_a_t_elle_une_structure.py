"""L'étiquette a-t-elle une structure — ou la chaîne poursuit-elle du bruit ?

⭐⭐⭐⭐ POURQUOI CE FICHIER. `191` a cherché parmi **19** observables intrinsèques, `193` parmi
**12** extrinsèques, et aucun des trente et un ne sépare les chunks où une surface tient sa feuille
de ceux où elle ne la tient pas. Avant d'en déclarer une trente-deuxième, il faut demander ce que la
chaîne n'a jamais demandé : **cette étiquette porte-t-elle seulement une structure ?**

⭐⭐⭐⭐ ET TROIS QUESTIONS SUFFISENT, TOUTES TROIS DÉCLARÉES ICI ET RÉPONDUES SANS UN SEUL
TÉLÉCHARGEMENT :
1. **Le compte global** — la marche retient-elle plus souvent que la règle ne se déclenche toute
   seule ? Le taux de faux de `190` est MESURÉ, donc la comparaison est exacte, pas permutée.
2. **Entre les segments** — les segments diffèrent-ils, ou l'étiquette est-elle répartie comme le
   hasard la répartirait ?
3. **Dans l'espace** — les chunks qui retiennent se tiennent-ils près les uns des autres à
   l'intérieur d'un segment ?

⚠⚠⚠ TROIS QUESTIONS DÉCLARÉES SONT TROIS CHANCES, ET ELLES SE PAIENT. Le nombre de mélanges est
DÉRIVÉ de ce compte : la chaîne se donne un sur vingt par famille depuis `176`, donc trois questions
exigent de résoudre un sur soixante, et il faut cinquante-neuf tirages pour cela. Ce n'est pas une
famille au sens de `191` — il n'y a aucun choix parmi des observables — mais trois tests déclarés,
et les compter est la seule façon de ne pas les compter pour un.

⚠⚠ ET CE QUE CE FICHIER NE FAIT PAS : il ne cherche rien. Aucune liste, aucun maximum, aucun
observable. Trois questions écrites avant de regarder, trois réponses.

Usage :
    uv run python src/nappe/letiquette_a_t_elle_une_structure.py --verifier
    uv run python src/nappe/letiquette_a_t_elle_une_structure.py \\
        --json docs/mesures/letiquette_a_t_elle_une_structure.json
"""
from __future__ import annotations

import argparse
import json
import sys
from math import comb
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_recette_posee_sur_le_rouleau import PERMUTATIONS  # noqa: E402
from ou_le_chunk_se_trouve_t_il import les_etiquettes  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_MARCHE_A_RENDU = MESURES / "une_surface_qui_choisit_sa_couche.json"
CE_QUE_LA_RECHERCHE_A_RENDU = MESURES / "la_ou_le_rouleau_se_laisse_suivre.json"
CE_QUE_LEXTRINSEQUE_A_RENDU = MESURES / "ou_le_chunk_se_trouve_t_il.json"
GRAINE = 20261004

# ⚠⚠⚠ LES TROIS QUESTIONS SONT DECLAREES ICI, ET LEUR NOMBRE FIXE LE PRIX. La chaine se donne un
# sur vingt par famille depuis `176` ; trois questions declarees exigent donc de resoudre un sur
# soixante, et cinquante-neuf tirages sont le plus petit nombre qui le permette.
LES_TROIS_QUESTIONS = ("le compte global", "entre les segments", "dans l espace")
TIRAGES = len(LES_TROIS_QUESTIONS) * (PERMUTATIONS + 1) - 1


def le_taux_de_faux_publie(chemin: Path = CE_QUE_LA_MARCHE_A_RENDU) -> float | None:
    """Le taux auquel la règle de `190` se déclenche quand il n'y a RIEN à tenir — relu, jamais tapé.

    ⭐ C'EST LE SEUL NUL DONT CETTE TRANCHE A BESOIN POUR SA PREMIÈRE QUESTION, et il est MESURÉ :
    `190` l'a lu sur quarante réplicats d'une matière à écart de direction nul. La comparaison est
    donc exacte — une loi binomiale — et non permutée.
    """
    if not chemin.is_file():
        return None
    d = json.loads(chemin.read_text(encoding="utf-8"))
    return (d.get("le_verdict") or {}).get("le_taux_de_faux_mesure")


def le_compte_global(n: int, k: int, taux: float) -> dict:
    """La marche retient-elle plus souvent que la règle ne se déclenche toute seule ?

    ⭐⭐⭐⭐ C'EST LA QUESTION QUI DÉCIDE SI TOUT LE RESTE A UN SENS. Si le compte observé tient dans
    ce que la règle rend sur une matière où il n'y a rien à tenir, alors l'étiquette est du bruit et
    trente et un observables n'avaient rien à expliquer.

    ⚠ La probabilité est calculée EXACTEMENT, par la loi binomiale, parce que le taux est mesuré et
    que chaque chunk est jugé par sa propre famille de dix-neuf tirages. Une permutation ici ne
    ferait qu'ajouter du bruit à un calcul qui n'en a pas besoin.
    """
    p = float(taux)
    attendus = round(float(n) * p, 4)
    au_moins = sum(comb(int(n), i) * p ** i * (1.0 - p) ** (int(n) - i)
                   for i in range(int(k), int(n) + 1))
    return {"chunks": int(n), "qui_retiennent": int(k), "le_taux_de_faux": p,
            "attendus_par_hasard": attendus,
            "la_probabilite_den_avoir_autant_ou_plus": float(f"{au_moins:.6g}"),
            "le_seuil_des_trois_questions": round(1.0 / float(TIRAGES + 1), 6),
            # ⭐ L'ENONCE : le compte observe est-il plus rare que le seuil que trois questions
            # declarees imposent ?
            "letiquette_porte_plus_que_le_hasard": bool(
                au_moins < 1.0 / float(TIRAGES + 1))}


def _khi2(compte, p: float) -> float:
    s = 0.0
    for c, t in compte:
        att = float(t) * p
        if att > 0.0:
            s += (float(c) - att) ** 2 / att
        if float(t) - att > 0.0:
            s += ((float(t) - float(c)) - (float(t) - att)) ** 2 / (float(t) - att)
    return s


def entre_les_segments(par_segment, tirages: int = TIRAGES,
                       graine: int = GRAINE) -> dict:
    """Les segments diffèrent-ils, ou l'étiquette y est-elle répartie comme le hasard le ferait ?

    ⭐ LE NUL EST UNE PERMUTATION LIBRE DE L'ÉTIQUETTE SUR TOUS LES CHUNKS, à taille de segment
    conservée : c'est exactement « la même étiquette, distribuée au hasard », et le khi-deux mesure
    l'écart à cette distribution-là.

    ⚠⚠ ET LA RÉPONSE PEUT ALLER DANS LES DEUX SENS. Un khi-deux SOUS le nul veut dire que
    l'étiquette est plus UNIFORME que le hasard, ce qui est une information et non un échec — donc
    le verdict dit « les segments diffèrent » et jamais « le test a échoué ».
    """
    segs = sorted(par_segment)
    tailles = [len(par_segment[s]) for s in segs]
    n = sum(tailles)
    k = sum(sum(1 for x in par_segment[s] if x) for s in segs)
    if n == 0 or k == 0 or k == n:
        return {"decidable": False, "raison": "un des deux camps est vide"}
    p = float(k) / float(n)
    obs = _khi2([(sum(1 for x in par_segment[s] if x), len(par_segment[s])) for s in segs], p)
    r = np.random.default_rng(int(graine))
    e = np.array([True] * k + [False] * (n - k))
    nuls = []
    for _ in range(int(tirages)):
        m = r.permutation(e)
        i, c = 0, []
        for t in tailles:
            c.append((int(m[i:i + t].sum()), t))
            i += t
        nuls.append(_khi2(c, p))
    plus_grands = int(sum(1 for x in nuls if x >= obs))
    return {"decidable": True, "segments": len(segs), "chunks": int(n),
            "qui_retiennent": int(k), "tirages": int(tirages),
            "le_khi_deux": round(float(obs), 4),
            "le_khi_deux_median_du_nul": round(float(np.median(nuls)), 4),
            "les_nuls_au_moins_aussi_grands": plus_grands,
            "la_part_des_nuls_au_moins_aussi_grands": round(
                plus_grands / float(tirages), 4),
            "les_taux_par_segment": {s: round(sum(1 for x in par_segment[s] if x)
                                              / float(len(par_segment[s])), 4) for s in segs},
            # ⭐ L'ENONCE : les segments different-ils ? Il faut depasser TOUS les nuls, comme
            # partout ailleurs dans la chaine.
            "les_segments_different": bool(plus_grands == 0)}


def _distance_moyenne(points) -> float | None:
    if len(points) < 2:
        return None
    d = [((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2) ** 0.5
         for i in range(len(points)) for j in range(i + 1, len(points))]
    return float(np.mean(d))


def _paires_voisines(points) -> int:
    return int(sum(1 for i in range(len(points)) for j in range(i + 1, len(points))
                   if max(abs(points[i][0] - points[j][0]),
                          abs(points[i][1] - points[j][1])) <= 1))


def dans_lespace(par_segment_positions, tirages: int = TIRAGES,
                 graine: int = GRAINE) -> dict:
    """Les chunks qui retiennent se tiennent-ils PRÈS les uns des autres dans leur segment ?

    ⭐ LE NUL MÉLANGE L'ÉTIQUETTE À L'INTÉRIEUR DE CHAQUE SEGMENT : chaque segment garde exactement
    son compte, et seule la place change. C'est le seul nul qui isole le groupement spatial de
    l'effet de segment que la deuxième question mesure déjà.

    ⚠⚠⚠ ET LE COMPTE DE PAIRES VOISINES EST PORTÉ COMME CONTRÔLE NOMMÉ, INCAPABLE DE DISCRIMINER :
    le treillis est si lâche que deux positions n'y sont presque jamais adjacentes, donc cette
    statistique vaut zéro pour l'observé comme pour presque tous les mélanges. La dire est plus utile
    que de la taire — et c'est la distance moyenne qui répond.
    """
    segs = sorted(par_segment_positions)
    obs_d, obs_v, poids = [], 0, 0
    for s in segs:
        pts = [(a, b) for a, b, e in par_segment_positions[s] if e]
        x = _distance_moyenne(pts)
        if x is not None:
            obs_d.append(x)
            poids += 1
        obs_v += _paires_voisines(pts)
    if not obs_d:
        return {"decidable": False, "raison": "aucun segment n'a deux chunks qui retiennent"}
    obs = float(np.mean(obs_d))
    r = np.random.default_rng(int(graine) + 3)
    nuls, nuls_v = [], []
    for _ in range(int(tirages)):
        ds, vv = [], 0
        for s in segs:
            lg = par_segment_positions[s]
            et = r.permutation(np.array([e for _a, _b, e in lg]))
            pts = [(a, b) for (a, b, _e), ee in zip(lg, et) if ee]
            y = _distance_moyenne(pts)
            if y is not None:
                ds.append(y)
            vv += _paires_voisines(pts)
        if ds:
            nuls.append(float(np.mean(ds)))
        nuls_v.append(vv)
    if not nuls:
        return {"decidable": False, "raison": "aucun mélange lisible"}
    plus_serres = int(sum(1 for x in nuls if x <= obs))
    return {"decidable": True, "segments_qui_comptent": poids, "tirages": int(tirages),
            "la_distance_moyenne": round(obs, 4),
            "la_distance_moyenne_du_nul": round(float(np.median(nuls)), 4),
            "les_nuls_au_moins_aussi_serres": plus_serres,
            "la_part_des_nuls_au_moins_aussi_serres": round(plus_serres / float(len(nuls)), 4),
            # ⚠⚠⚠ LE CONTROLE NOMME, INCAPABLE DE DISCRIMINER : le treillis est trop lache pour que
            # deux positions soient adjacentes.
            "les_paires_voisines": int(obs_v),
            "les_paires_voisines_du_nul": int(round(float(np.median(nuls_v)))),
            "le_compte_de_voisines_ne_discrimine_pas": bool(
                int(obs_v) == 0 and int(max(nuls_v)) == 0),
            "les_chunks_qui_retiennent_se_groupent": bool(plus_serres == 0)}


def la_sensibilite_entre_segments(chauds: int, segments: int = 12, par_segment: int = 7,
                                  replicats: int = 5, tirages: int = TIRAGES,
                                  graine: int = GRAINE) -> float:
    """À quelle fréquence l'instrument voit un écart POSÉ entre segments, à cette force-là.

    ⭐⭐⭐⭐ ELLE EXISTE PARCE QU'UNE FACE POSITIVE MARGINALE N'EST PAS UNE FACE POSITIVE. Un étalon
    dont l'effet posé n'est vu qu'une fois sur cinq ne dit pas que l'instrument voit : il dit qu'il
    voit parfois, et le silence qu'il autorise ensuite n'est pas lisible. La force de la face est
    donc DÉRIVÉE de cette courbe — la plus petite qui soit vue à TOUS les réplicats — et jamais
    choisie.

    ⚠ La moitié des segments est « chaude » et l'autre vide : c'est l'écart le plus simple qu'on
    puisse poser, et ce qui varie d'un barreau à l'autre est sa FORCE et rien d'autre.
    """
    vus = 0
    for t in range(int(replicats)):
        lu = {f"S{i}": ([True] * int(chauds) + [False] * (int(par_segment) - int(chauds))
                        if i < int(segments) // 2 else [False] * int(par_segment))
              for i in range(int(segments))}
        r = entre_les_segments(lu, tirages, int(graine) + 977 * (t + 1))
        vus += int(bool(r.get("les_segments_different")))
    return round(vus / float(replicats), 4)


def la_force_quil_faut(segments: int = 12, par_segment: int = 7, replicats: int = 5,
                       tirages: int = TIRAGES, graine: int = GRAINE) -> int:
    """La plus petite force d'écart que l'instrument voit à TOUS les réplicats — dérivée, pas choisie."""
    for chauds in range(1, int(par_segment) + 1):
        if la_sensibilite_entre_segments(chauds, segments, par_segment, replicats, tirages,
                                         graine) >= 1.0:
            return int(chauds)
    return int(par_segment)


def sur_letalon(tirages: int = TIRAGES, graine: int = GRAINE, replicats: int = 5) -> dict:
    """Trois matières d'étiquettes dont la réponse est CONNUE, une par question.

    ⭐⭐⭐⭐ CHAQUE QUESTION A SA FACE POSITIVE ET SA FACE NÉGATIVE, et sans elles un silence ne
    voudrait rien dire. Une étiquette concentrée dans la moitié des segments DOIT faire dire « les
    segments diffèrent » ; la même étiquette répartie uniformément ne le doit PAS. Une étiquette
    posée sur des positions voisines DOIT faire dire « ça se groupe » ; la même étalée ne le doit
    pas.

    ⚠⚠ Les deux faces d'une question portent le MÊME nombre d'étiquettes et les MÊMES segments : ce
    qui change est leur PLACE, et rien d'autre.
    """
    segs = [f"S{i}" for i in range(12)]
    # ⚠⚠⚠ LA FORCE DE LA FACE POSITIVE EST DERIVEE DE LA COURBE DE SENSIBILITE, jamais choisie :
    # c'est la plus petite que l'instrument voie a TOUS les replicats.
    force = la_force_quil_faut(12, 7, replicats, tirages, graine)
    courbe = {str(c): la_sensibilite_entre_segments(c, 12, 7, replicats, tirages, graine)
              for c in range(1, 8)}
    # ⚠ Une etiquette CONCENTREE : tout dans les six premiers segments, a la force derivee.
    concentree = {s: [True] * force + [False] * (7 - force) if i < 6 else [False] * 7
                  for i, s in enumerate(segs)}
    etalee = {s: ([True] if i % 8 == 0 else []) + [False] * (7 - (1 if i % 8 == 0 else 0))
              for i, s in enumerate(segs)}
    # ⚠ Un groupement POSE : les retenants collés dans un coin de chaque segment.
    grille = [(a, b) for a in range(5) for b in range(5)]
    groupee = {s: [(a, b, (a <= 1 and b <= 1)) for a, b in grille] for s in segs[:4]}
    dispersee = {s: [(a, b, ((a * 5 + b) % 6 == 0)) for a, b in grille] for s in segs[:4]}
    return {
        "la_force_derivee": int(force), "la_courbe_de_sensibilite": courbe,
        "les_segments_different_quand_ils_different":
            entre_les_segments(concentree, tirages, graine),
        "les_segments_ne_different_pas_quand_ils_ne_different_pas":
            entre_les_segments(etalee, tirages, graine),
        "ca_se_groupe_quand_c_est_groupe": dans_lespace(groupee, tirages, graine),
        "ca_ne_se_groupe_pas_quand_c_est_disperse": dans_lespace(dispersee, tirages, graine),
        # ⚠ LA PREMIERE QUESTION EST DE L'ARITHMETIQUE EXACTE : son etalon est un compte dont la
        # probabilite se calcule a la main.
        "le_compte_dit_oui_quand_il_le_faut": le_compte_global(81, 15, 0.075),
        "le_compte_dit_non_quand_il_le_faut": le_compte_global(81, 6, 0.075),
    }


def letalon_separe(e: dict) -> bool:
    """Les trois questions séparent-elles TOUTES leurs deux faces ?

    ⚠⚠⚠ LES SIX ENSEMBLE, ET PAS CINQ : un instrument qui dirait « oui » partout, ou « non »
    partout, passerait la moitié du contrôle en ne discriminant rien.
    """
    return bool(
        (e.get("les_segments_different_quand_ils_different") or {}).get("les_segments_different")
        and not (e.get("les_segments_ne_different_pas_quand_ils_ne_different_pas")
                 or {}).get("les_segments_different")
        and (e.get("ca_se_groupe_quand_c_est_groupe")
             or {}).get("les_chunks_qui_retiennent_se_groupent")
        and not (e.get("ca_ne_se_groupe_pas_quand_c_est_disperse")
                 or {}).get("les_chunks_qui_retiennent_se_groupent")
        and (e.get("le_compte_dit_oui_quand_il_le_faut")
             or {}).get("letiquette_porte_plus_que_le_hasard")
        and not (e.get("le_compte_dit_non_quand_il_le_faut")
                 or {}).get("letiquette_porte_plus_que_le_hasard"))


def ce_que_les_recherches_ont_rendu() -> dict:
    """Ce que `191` et `193` ont cherché — relu pour que le total des observables soit un fait."""
    out = {}
    for nom, chemin in (("intrinseques", CE_QUE_LA_RECHERCHE_A_RENDU),
                        ("extrinseques", CE_QUE_LEXTRINSEQUE_A_RENDU)):
        if chemin.is_file():
            v = (json.loads(chemin.read_text(encoding="utf-8")).get("le_verdict") or {})
            out[nom] = v.get("observables_declares")
    a, b = out.get("intrinseques"), out.get("extrinseques")
    out["en_tout"] = (int(a) + int(b)) if a and b else None
    return out


def mesurer(tirages: int = TIRAGES, graine: int = GRAINE) -> dict:
    taux = le_taux_de_faux_publie()
    if taux is None:
        return {"message": "le taux de faux de `190` n'est pas lisible ; relancer `190` d'abord"}
    marques = les_etiquettes()["chunks"]
    if not marques:
        return {"message": "aucun chunk étiqueté ; relancer `190` et `192` d'abord"}
    segs = sorted({k[0] for k in marques})
    par_segment = {s: [bool(v["etiquette"]) for k, v in sorted(marques.items()) if k[0] == s]
                   for s in segs}
    positions = {s: sorted((k[1], k[2], bool(v["etiquette"]))
                           for k, v in marques.items() if k[0] == s) for s in segs}
    n = len(marques)
    k = int(sum(1 for v in marques.values() if v["etiquette"]))
    compte = le_compte_global(n, k, float(taux))
    segments = entre_les_segments(par_segment, tirages, graine)
    espace = dans_lespace(positions, tirages, graine)
    etalon = sur_letalon(tirages, graine)
    cherches = ce_que_les_recherches_ont_rendu()
    return {"graine": int(graine), "tirages": int(tirages),
            "les_trois_questions": list(LES_TROIS_QUESTIONS),
            "le_seuil_des_trois_questions": round(1.0 / float(tirages + 1), 6),
            "le_taux_de_faux_relu_de_190": float(taux),
            "les_observables_deja_cherches": cherches,
            "letalon": etalon, "letalon_separe": letalon_separe(etalon),
            "la_force_derivee_de_letalon": etalon.get("la_force_derivee"),
            "la_courbe_de_sensibilite": etalon.get("la_courbe_de_sensibilite"),
            "le_compte_global": compte,
            "entre_les_segments": segments,
            "dans_lespace": espace,
            "le_verdict": {
                "decidable": True,
                "chunks": n, "qui_retiennent": k, "segments": len(segs),
                "letiquette_porte_plus_que_le_hasard": bool(
                    compte["letiquette_porte_plus_que_le_hasard"]),
                "la_probabilite_du_compte": compte["la_probabilite_den_avoir_autant_ou_plus"],
                "les_attendus_par_hasard": compte["attendus_par_hasard"],
                "les_segments_different": bool(segments.get("les_segments_different")),
                "le_khi_deux": segments.get("le_khi_deux"),
                "le_khi_deux_median_du_nul": segments.get("le_khi_deux_median_du_nul"),
                "la_part_des_nuls_au_moins_aussi_grands": segments.get(
                    "la_part_des_nuls_au_moins_aussi_grands"),
                "les_chunks_qui_retiennent_se_groupent": bool(
                    espace.get("les_chunks_qui_retiennent_se_groupent")),
                "la_distance_moyenne": espace.get("la_distance_moyenne"),
                "la_distance_moyenne_du_nul": espace.get("la_distance_moyenne_du_nul"),
                "la_part_des_nuls_au_moins_aussi_serres": espace.get(
                    "la_part_des_nuls_au_moins_aussi_serres"),
                "le_compte_de_voisines_ne_discrimine_pas": bool(
                    espace.get("le_compte_de_voisines_ne_discrimine_pas")),
                "les_observables_deja_cherches": cherches.get("en_tout"),
                "le_seuil_des_trois_questions": round(1.0 / float(tirages + 1), 6),
                "letalon_separe": letalon_separe(etalon),
                "la_force_derivee_de_letalon": etalon.get("la_force_derivee"),
                # ⭐⭐⭐⭐ L'ENONCE DE LA TRANCHE : l'etiquette est REELLE en gros et SANS STRUCTURE
                # en detail — ni entre les segments, ni dans l'espace.
                "reelle_et_sans_structure": bool(
                    compte["letiquette_porte_plus_que_le_hasard"]
                    and not segments.get("les_segments_different")
                    and not espace.get("les_chunks_qui_retiennent_se_groupent"))}}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, e = r["le_verdict"], r["letalon"]
    print("L'ÉTIQUETTE A-T-ELLE UNE STRUCTURE ?")
    print(f"  {v['qui_retiennent']} chunks qui retiennent sur {v['chunks']}, "
          f"{v['segments']} segments · {len(r['les_trois_questions'])} questions DÉCLARÉES · "
          f"{r['tirages']} mélanges, donc un seuil de {r['le_seuil_des_trois_questions']}")
    print()
    print("  L'ÉTALON — chaque question a ses deux faces")
    for nom, cle, lu in (
            ("des segments qui DIFFÈRENT", "les_segments_different_quand_ils_different",
             "les_segments_different"),
            ("des segments qui ne diffèrent pas",
             "les_segments_ne_different_pas_quand_ils_ne_different_pas", "les_segments_different"),
            ("une étiquette GROUPÉE", "ca_se_groupe_quand_c_est_groupe",
             "les_chunks_qui_retiennent_se_groupent"),
            ("une étiquette dispersée", "ca_ne_se_groupe_pas_quand_c_est_disperse",
             "les_chunks_qui_retiennent_se_groupent"),
            ("un compte au-dessus du hasard", "le_compte_dit_oui_quand_il_le_faut",
             "letiquette_porte_plus_que_le_hasard"),
            ("un compte dans le hasard", "le_compte_dit_non_quand_il_le_faut",
             "letiquette_porte_plus_que_le_hasard")):
        print(f"     {nom:<34} {(e.get(cle) or {}).get(lu)}")
    print(f"     {'l étalon sépare les six':<34} {r['letalon_separe']}")
    print(f"     {'la force DÉRIVÉE de la face positive':<34} "
          f"{r.get('la_force_derivee_de_letalon')} chunks chauds sur 7")
    print(f"     {'la courbe de sensibilité':<34} {r.get('la_courbe_de_sensibilite')}")
    print()
    print("  LES TAUX PAR SEGMENT")
    for s, t in (r["entre_les_segments"].get("les_taux_par_segment") or {}).items():
        print(f"     {s:<26} {t}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("chunks", "qui_retiennent", "segments", "les_attendus_par_hasard",
                "la_probabilite_du_compte", "le_seuil_des_trois_questions",
                "letiquette_porte_plus_que_le_hasard", "le_khi_deux",
                "le_khi_deux_median_du_nul", "la_part_des_nuls_au_moins_aussi_grands",
                "les_segments_different", "la_distance_moyenne", "la_distance_moyenne_du_nul",
                "la_part_des_nuls_au_moins_aussi_serres",
                "les_chunks_qui_retiennent_se_groupent",
                "le_compte_de_voisines_ne_discrimine_pas", "les_observables_deja_cherches",
                "letalon_separe", "reelle_et_sans_structure"):
        print(f"     {cle:<48} {v.get(cle)}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⚠⚠⚠ LES TROIS QUESTIONS SONT DECLAREES, ET LEUR NOMBRE FIXE LE PRIX.
    v("★ les trois questions sont déclarées", len(LES_TROIS_QUESTIONS) == 3,
      str(LES_TROIS_QUESTIONS))
    v("★★★ le nombre de tirages est DÉRIVÉ de ce nombre",
      TIRAGES == len(LES_TROIS_QUESTIONS) * (PERMUTATIONS + 1) - 1,
      f"{TIRAGES} pour {len(LES_TROIS_QUESTIONS)} questions et {PERMUTATIONS} permutations")
    v("★★ et il résout bien un sur soixante",
      abs(1.0 / (TIRAGES + 1) - 1.0 / (3 * (PERMUTATIONS + 1))) < 1e-12,
      str(1.0 / (TIRAGES + 1)))

    # ⚠⚠ LE TAUX DE FAUX EST RELU DE `190`, JAMAIS TAPE.
    t = le_taux_de_faux_publie()
    v("le taux de faux de `190` est relu", t is not None and 0.0 < float(t) < 1.0, str(t))
    v("et il est absent quand la mesure l'est",
      le_taux_de_faux_publie(Path("/n/existe/pas.json")) is None)

    # ⭐⭐⭐⭐ LA PREMIERE QUESTION EST DE L'ARITHMETIQUE EXACTE, ET ELLE SE VERIFIE A LA MAIN.
    c = le_compte_global(10, 10, 0.5)
    v("★★ la probabilité d'un compte plein vaut celle de la loi binomiale",
      abs(float(c["la_probabilite_den_avoir_autant_ou_plus"]) - 0.5 ** 10) < 1e-9,
      str(c["la_probabilite_den_avoir_autant_ou_plus"]))
    v("la probabilité d'en avoir au moins zéro vaut un",
      abs(float(le_compte_global(10, 0, 0.3)["la_probabilite_den_avoir_autant_ou_plus"]) - 1.0)
      < 1e-9)
    v("★★ les attendus sont le compte fois le taux",
      abs(float(le_compte_global(80, 3, 0.25)["attendus_par_hasard"]) - 20.0) < 1e-9,
      str(le_compte_global(80, 3, 0.25)["attendus_par_hasard"]))
    v("★★★ un compte au niveau du hasard ne porte RIEN",
      not le_compte_global(81, 6, 0.075)["letiquette_porte_plus_que_le_hasard"])
    v("★★★ et un compte très au-dessus porte quelque chose",
      le_compte_global(81, 15, 0.075)["letiquette_porte_plus_que_le_hasard"])

    # ⭐⭐⭐⭐ LES DEUX AUTRES QUESTIONS ONT CHACUNE LEURS DEUX FACES, ET L'ETALON LES EXERCE.
    v("★★★★ la force de la face positive est DÉRIVÉE de la sensibilité, pas choisie",
      la_sensibilite_entre_segments(la_force_quil_faut(12, 7, 3, TIRAGES, 4242), 12, 7, 3,
                                    TIRAGES, 4242) >= 1.0,
      str(la_force_quil_faut(12, 7, 3, TIRAGES, 4242)))
    v("★★★ et une force plus faible n'est PAS vue à tous les coups",
      la_sensibilite_entre_segments(1, 12, 7, 3, TIRAGES, 4242) < 1.0,
      str(la_sensibilite_entre_segments(1, 12, 7, 3, TIRAGES, 4242)))
    e = sur_letalon(TIRAGES, 4242, 3)
    v("★★★★ des segments qui diffèrent sont vus comme tels",
      (e["les_segments_different_quand_ils_different"] or {}).get("les_segments_different"),
      str((e["les_segments_different_quand_ils_different"] or {}).get("le_khi_deux")))
    v("★★★★ et des segments qui ne diffèrent pas ne le sont PAS",
      not (e["les_segments_ne_different_pas_quand_ils_ne_different_pas"]
           or {}).get("les_segments_different"))
    v("★★★★ une étiquette groupée est vue groupée",
      (e["ca_se_groupe_quand_c_est_groupe"] or {}).get(
          "les_chunks_qui_retiennent_se_groupent"),
      str((e["ca_se_groupe_quand_c_est_groupe"] or {}).get("la_distance_moyenne")))
    v("★★★★ et une étiquette dispersée ne l'est PAS",
      not (e["ca_ne_se_groupe_pas_quand_c_est_disperse"] or {}).get(
          "les_chunks_qui_retiennent_se_groupent"))
    v("★★★★ l'étalon sépare les SIX faces", letalon_separe(e),
      str({k_: (x.get("les_segments_different") if "segments" in k_ else
                x.get("les_chunks_qui_retiennent_se_groupent")
                if "groupe" in k_ else x.get("letiquette_porte_plus_que_le_hasard"))
           for k_, x in e.items() if isinstance(x, dict) and "decidable" in x
           or isinstance(x, dict) and "chunks" in x}))

    # ⚠⚠ LE MELANGE DE LA DEUXIEME QUESTION GARDE LA TAILLE DES SEGMENTS, celui de la troisieme
    # garde le COMPTE de chaque segment : sans cela, les deux mesureraient la meme chose.
    petit = {"A": [True, False, False], "B": [True, True, False, False]}
    s1 = entre_les_segments(petit, 9, 5)
    v("le khi-deux se calcule sur les tailles réelles", s1["chunks"] == 7 and s1["segments"] == 2,
      str((s1["chunks"], s1["segments"])))
    v("un camp vide est refusé",
      entre_les_segments({"A": [False, False]}, 9, 5).get("decidable") is False)
    pos = {"A": [(0, 0, True), (0, 1, True), (4, 4, False)]}
    d1 = dans_lespace(pos, 9, 5)
    v("la distance moyenne est celle des seuls retenants",
      abs(float(d1["la_distance_moyenne"]) - 1.0) < 1e-9, str(d1["la_distance_moyenne"]))
    v("un segment sans deux retenants ne compte pas",
      dans_lespace({"A": [(0, 0, True), (1, 1, False)]}, 9, 5).get("decidable") is False)

    # ⚠⚠⚠ LE CONTROLE NOMME, INCAPABLE DE DISCRIMINER, EST DIT PLUTOT QUE TU.
    loin = {s: [(a * 40, b * 40, (a + b) % 3 == 0) for a in range(3) for b in range(3)]
            for s in ("A", "B")}
    d2 = dans_lespace(loin, 9, 5)
    v("★★★ sur un treillis lâche, le compte de paires voisines ne discrimine pas",
      d2["le_compte_de_voisines_ne_discrimine_pas"],
      f"{d2['les_paires_voisines']} observées, {d2['les_paires_voisines_du_nul']} au nul")

    v("ce que `191` et `193` ont cherché est relu",
      bool(ce_que_les_recherches_ont_rendu().get("en_tout")),
      str(ce_que_les_recherches_ont_rendu()))

    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "letiquette_a_t_elle_une_structure.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e_ in echecs:
            print(f"   ✗ {e_}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return len(echecs)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
