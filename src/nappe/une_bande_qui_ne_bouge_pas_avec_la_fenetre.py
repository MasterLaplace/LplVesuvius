#!/usr/bin/env python3
"""Le plancher de frequence doit etre PHYSIQUE, pas relatif a la fenetre — et ce que ca change.

⚠⚠⚠ POURQUOI CE FICHIER, ET `110` L'A NOMME. L'estimateur de `98` cherche sa frequence entre
`F_MIN = 0,35` et `k + 4` PERIODES PAR FENETRE. Le plancher est donc relatif : sur deux pas il
admet une longueur d'onde de 1314 µm, sur six de 3943 — alors qu'aucune de ces deux valeurs n'est
un espacement de feuille. Consequence mesuree par `110` : une composante de basse frequence devient
EXPRIMABLE des que la fenetre est assez longue, et si elle est plus forte que la periodicite elle
gagne l'argmax. La falaise du mode bas — correct a deux pas, effondre a trois — est exactement
cette signature, et une derive SEULE la reproduit sur une periodicite intacte.

⭐⭐⭐ LE REMEDE N'EST PAS UN NOUVEL ESTIMATEUR MAIS UNE BANDE DERIVEE DE LA MATIERE. Une feuille a
un espacement, et la campagne en a deja fixe la plage : les candidats du balayage vont de 86,5 a
346 µm. Une longueur d'onde hors de cette plage n'est pas un espacement de feuille, c'est autre
chose. En frequence, `f = L / lambda`, donc la bande suit la longueur de la fenetre et le PLANCHER
reste physique. Aucune ligne de l'estimateur n'est reecrite : c'est `98` qu'on appelle, avec une
bande calculee.

⚠⚠⚠ ET LE PRIX A PAYER EST NOMME AVANT D'ETRE MESURE : une bande etroite ne peut plus dire « pas
de periodicite » PAR SON COMPTE. Sur une derive seule, sans aucune feuille, elle rend quand meme un
nombre. C'est le SCORE qui doit le dire, donc la bande bornee a besoin de SA propre barre — et
comme la bande change avec la longueur de la fenetre, la barre en change aussi. *Chaque famille
porte la barre de sa propre forme*, et ici chaque LONGUEUR porte la sienne.

Usage :
    uv run python src/nappe/une_bande_qui_ne_bouge_pas_avec_la_fenetre.py --verifier
    uv run python src/nappe/une_bande_qui_ne_bouge_pas_avec_la_fenetre.py \\
        --json docs/mesures/une_bande_qui_ne_bouge_pas_avec_la_fenetre.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

CHEMIN_DE_107 = RACINE / "docs" / "mesures" / "le_marcheur_avec_le_bon_pas.json"
SELECTEURS = ("calibre", "deux_roles")
PREFIXE_MIN = 2
GRAINE = 111
TIRAGES_DU_NUL = 600


def bornes_de_longueur_donde() -> tuple[float, float]:
    """La plage d'espacements que la campagne considere comme une feuille, en micrometres.

    ⚠⚠ ELLE N'EST PAS UN REGLAGE DE CETTE TRANCHE : ce sont les candidats du balayage de `105`,
    deja fixes par `FACTEUR_BAS` et `FACTEUR_HAUT` autour du pas nominal. Les reprendre est ce qui
    empeche cette tranche d'inventer une plage qui lui convient — et si un jour la plage bouge, les
    deux bougent ensemble.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415

    c = M.candidats_de_pas(C.PAS_UM)
    return float(np.min(c)), float(np.max(c))


def bande_de_frequences(longueur_um: float, lambda_min_um: float,
                        lambda_max_um: float) -> tuple[float, float]:
    """La bande de frequences qu'une fenetre de `longueur_um` doit balayer, et rien de plus.

    ⭐⭐⭐ C'EST TOUTE LA TRANCHE EN UNE LIGNE : `f = L / lambda`. Le nombre de periodes admissibles
    grandit avec la fenetre — ce qui est correct, une fenetre deux fois plus longue contient deux
    fois plus de feuilles — mais la LONGUEUR D'ONDE admissible, elle, ne bouge pas. C'est
    exactement la propriete qui manquait : le plancher de `98` est relatif a la fenetre, donc il
    laisse entrer une derive de plus en plus longue a mesure que la marche s'allonge.

    ⚠ L'ordre est inverse entre les deux : la plus GRANDE longueur d'onde donne la plus PETITE
    frequence. Confondre les deux mettrait le plancher au plafond, et l'estimateur chercherait une
    feuille tous les quatre-vingts micrometres sur une fenetre qui en fait mille.
    """
    if not (lambda_min_um > 0.0 and lambda_max_um >= lambda_min_um):
        raise ValueError("les bornes de longueur d'onde doivent etre positives et ordonnees")
    if longueur_um <= 0.0:
        raise ValueError("une fenetre a une longueur strictement positive")
    return longueur_um / lambda_max_um, longueur_um / lambda_min_um


def feuilles_franchies_bornees(v: np.ndarray, longueur_um: float,
                               lambda_min_um: float, lambda_max_um: float):
    """L'estimateur de `98`, appele avec une bande derivee de la matiere.

    ⚠⚠ AUCUNE LIGNE DE L'ESTIMATEUR N'EST REECRITE ICI, et c'est delibere : une seconde
    implementation du meme ajustement serait deux reponses a « combien de feuilles », libres de
    diverger. Ce qui change est la BANDE, pas la machine.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    f_min, f_max = bande_de_frequences(longueur_um, lambda_min_um, lambda_max_um)
    return C.feuilles_franchies(v, f_min=f_min, f_max=f_max)


def nul_de_la_bande(longueurs_um, lambda_min_um: float, lambda_max_um: float,
                    echantillons_par_pas: int = 73, pas_par_fenetre=None,
                    tirages: int = TIRAGES_DU_NUL, graine: int = GRAINE) -> dict:
    """Ce que la bande BORNEE rend sur du bruit pur, longueur par longueur.

    ⭐⭐⭐ ELLE EXISTE PARCE QU'UNE BANDE ETROITE NE PEUT PLUS DIRE « PAS DE PERIODICITE » PAR SON
    COMPTE. Sur une derive seule, sans aucune feuille, elle rend quand meme un nombre — c'est le
    prix de l'avoir bornee. Le score doit donc porter le verdict, et un score n'est lisible
    qu'avec la barre de SA PROPRE FORME.

    ⚠⚠ ET LA BARRE CHANGE AVEC LA LONGUEUR, ce qui n'etait pas vrai de `98`. Deux effets
    s'opposent : la bande contient `L (1/lambda_min - 1/lambda_max)` frequences, donc elle
    s'elargit avec la fenetre et devrait rendre l'accord fortuit plus facile ; mais le nombre
    d'ECHANTILLONS grandit lui aussi, et la correlation d'un gabarit avec du bruit blanc decroit
    en `1/racine(n)`.

    ⚠⚠⚠ MESURE : C'EST LE SECOND QUI GAGNE, ET J'AVAIS ECRIT L'INVERSE. La barre BAISSE — 0,287 a
    deux pas, 0,172 a six — donc la bande bornee devient PLUS discriminante quand la marche
    s'allonge, pas moins. Une barre unique prise au plus court serait donc trop severe aux
    fenetres longues, et non trop permissive comme je l'avais affirme. C'est la raison d'etre de
    la barre par longueur, et le sens de sa pente est un resultat, pas une hypothese.
    """
    r = np.random.default_rng(graine)
    lignes = []
    for i, L in enumerate(longueurs_um):
        n = (pas_par_fenetre[i] if pas_par_fenetre else 1) * echantillons_par_pas + 1
        v = r.normal(100.0, 20.0, size=(tirages, n))
        _f, sc, _b = feuilles_franchies_bornees(v, L, lambda_min_um, lambda_max_um)
        f_min, f_max = bande_de_frequences(L, lambda_min_um, lambda_max_um)
        lignes.append({"longueur_um": round(float(L), 1),
                       "echantillons": int(n),
                       "f_min": round(f_min, 3), "f_max": round(f_max, 3),
                       "p99_du_score": round(float(np.percentile(sc, 99)), 4),
                       "p95_du_score": round(float(np.percentile(sc, 95)), 4),
                       "score_median": round(float(np.median(sc)), 4)})
    return {"tirages": int(tirages), "graine": int(graine),
            "lambda_min_um": lambda_min_um, "lambda_max_um": lambda_max_um,
            "par_longueur": lignes,
            "barre": round(max(x["p99_du_score"] for x in lignes), 4) if lignes else None,
            # ⚠⚠ LE SENS DE LA PENTE EST RENDU, PAS SUPPOSE. Je l'avais annonce montant ; il
            # descend, parce que le nombre d'echantillons grandit plus vite que la bande. Publier
            # le sens est ce qui empeche de reprendre une barre au mauvais bout.
            "la_barre_baisse_avec_la_longueur": bool(
                len(lignes) > 1
                and lignes[-1]["p99_du_score"] < lignes[0]["p99_du_score"]),
            "pente_de_la_barre": round(
                lignes[-1]["p99_du_score"] - lignes[0]["p99_du_score"], 4)
            if len(lignes) > 1 else None}


def deux_lectures_dun_meme_profil(v: np.ndarray, pas: int, avance_um: float,
                                  lambda_min_um: float, lambda_max_um: float,
                                  echantillons: int) -> list[dict]:
    """Le meme profil lu par les DEUX bandes, prefixe par prefixe.

    ⭐⭐⭐ LA COMPARAISON EST APPARIEE SUR LES MEMES ECHANTILLONS, ce qui est la seule forme honnete
    pour opposer deux instruments : ils ne lisent pas deux volumes, ils lisent le meme profil. Tout
    ecart entre eux vient donc de la BANDE et de rien d'autre.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    out = []
    for k in range(PREFIXE_MIN, pas + 1):
        n = k * echantillons + 1
        if n > v.size:
            break
        L = float(k) * avance_um
        fa, sa, ba = C.feuilles_franchies(v[:n].reshape(1, -1), f_min=0.35,
                                          f_max=float(k) + 4.0)
        fb, sb, bb = feuilles_franchies_bornees(v[:n].reshape(1, -1), L,
                                                lambda_min_um, lambda_max_um)
        if not np.isfinite(fa[0]) or not np.isfinite(fb[0]):
            out.append({"pas": k, "decidable": False, "pourquoi": "profil plat"})
            continue
        out.append({"pas": k, "decidable": True, "longueur_um": round(L, 1),
                    "ancien": {"feuilles": round(float(fa[0]), 3),
                               "feuilles_par_pas": round(float(fa[0]) / k, 3),
                               "score": round(float(sa[0]), 3),
                               "en_butee": bool(ba[0])},
                    "borne": {"feuilles": round(float(fb[0]), 3),
                              "feuilles_par_pas": round(float(fb[0]) / k, 3),
                              "score": round(float(sb[0]), 3),
                              "en_butee": bool(bb[0])}})
    return out


def controle_fabrique(pas_max: int = 6, avance_um: float = 230.0,
                      graine: int = GRAINE + 1) -> dict:
    """Les quatre cas dont on connait la reponse, lus par les DEUX bandes.

    ⚠⚠⚠ LES DEUX CONTROLES NEGATIFS SONT CE QUI REND LA TRANCHE LISIBLE. Une bande bornee qui
    rendrait « une feuille par pas » sur une derive SEULE, ou sur du bruit, serait un instrument
    qui trouve des feuilles partout — donc pire que celui qu'elle remplace. Ce qui doit les
    ecarter n'est plus le compte mais le SCORE, et c'est mesure ici plutot qu'espere.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    lmin, lmax = bornes_de_longueur_donde()
    rng = np.random.default_rng(graine)
    cas = []
    for nom, periodique, derive, ampl in (
            ("periodicite pure", True, None, 0.0),
            ("periodicite plus derive x1,5", True, 8.0, 1.5),
            ("periodicite plus derive x2,0", True, 8.0, 2.0),
            ("derive SEULE, aucune feuille", False, 8.0, 1.0),
            ("bruit pur", False, None, 0.0)):
        lignes = []
        for k in range(PREFIXE_MIN, pas_max + 1):
            n = k * C.ECHANTILLONS + 1
            t = np.linspace(0.0, float(k), n)
            v = 100.0 + rng.normal(0.0, 5.0, n)
            if periodique:
                v = v + 40.0 * np.cos(2.0 * np.pi * t)
            if derive is not None:
                v = v + 40.0 * max(ampl, 1.0) * np.cos(2.0 * np.pi * t / derive)
            lignes.extend(deux_lectures_dun_meme_profil(v, k, avance_um, lmin, lmax,
                                                        C.ECHANTILLONS)[-1:])
        cas.append({"cas": nom, "attendu_une_feuille_par_pas": periodique,
                    "par_longueur": lignes})
    # ⭐⭐⭐ LES TROIS VERDICTS, ET CHACUN PEUT DIRE NON.
    def _bornes(nom, cle):
        c = next(x for x in cas if x["cas"] == nom)
        return [y["borne"][cle] for y in c["par_longueur"] if y.get("decidable")]

    def _anciens(nom, cle):
        c = next(x for x in cas if x["cas"] == nom)
        return [y["ancien"][cle] for y in c["par_longueur"] if y.get("decidable")]

    avec = _bornes("periodicite plus derive x2,0", "feuilles_par_pas")
    avec_a = _anciens("periodicite plus derive x2,0", "feuilles_par_pas")
    seule = _bornes("derive SEULE, aucune feuille", "score")
    pure = _bornes("periodicite pure", "score")
    return {
        "lambda_min_um": lmin, "lambda_max_um": lmax, "avance_um": avance_um,
        "cas": cas,
        "la_bande_bornee_garde_le_compte_sous_une_derive": bool(
            avec and min(avec) >= 0.9),
        "lancienne_bande_le_perd": bool(avec_a and min(avec_a) <= 0.3),
        # ⚠⚠ LE PRIX : sur une derive SEULE la bande bornee rend quand meme un compte, donc c'est
        # le SCORE qui doit l'ecarter. Le verdict compare les deux scores plutot que les comptes.
        "sur_une_derive_seule_le_score_seffondre": bool(
            seule and pure and max(seule) < min(pure)),
        "score_max_sur_une_derive_seule": round(max(seule), 3) if seule else None,
        "score_min_sur_une_periodicite_pure": round(min(pure), 3) if pure else None}


def comparer(courbes: list[list[dict]], barre_par_longueur: dict | None = None) -> dict:
    """Les deux bandes, longueur par longueur, sur les memes profils."""
    par: dict[int, dict[str, list]] = {}
    for c in courbes:
        for x in c:
            if not x.get("decidable"):
                continue
            d = par.setdefault(x["pas"], {"ancien": [], "borne": [],
                                          "score_ancien": [], "score_borne": []})
            d["ancien"].append(x["ancien"]["feuilles_par_pas"])
            d["borne"].append(x["borne"]["feuilles_par_pas"])
            d["score_ancien"].append(x["ancien"]["score"])
            d["score_borne"].append(x["borne"]["score"])
    if not par:
        return {"decidable": False, "pourquoi": "aucun profil lisible"}
    lignes = []
    for k in sorted(par):
        d = par[k]
        ligne = {"pas": k, "marches": len(d["ancien"]),
                 "ancien_median": round(float(np.median(d["ancien"])), 3),
                 "borne_median": round(float(np.median(d["borne"])), 3),
                 "score_ancien_median": round(float(np.median(d["score_ancien"])), 3),
                 "score_borne_median": round(float(np.median(d["score_borne"])), 3)}
        if barre_par_longueur and k in barre_par_longueur:
            b = barre_par_longueur[k]
            ligne["barre_du_score_borne"] = b
            ligne["part_au_dessus_de_la_barre"] = round(
                float(np.mean(np.asarray(d["score_borne"]) > b)), 3)
        lignes.append(ligne)
    return {"decidable": True, "par_longueur": lignes,
            "ancien_au_plus_court": lignes[0]["ancien_median"],
            "ancien_au_plus_long": lignes[-1]["ancien_median"],
            "borne_au_plus_court": lignes[0]["borne_median"],
            "borne_au_plus_long": lignes[-1]["borne_median"],
            "derive_de_lancien": round(lignes[-1]["ancien_median"]
                                       - lignes[0]["ancien_median"], 3),
            "derive_du_borne": round(lignes[-1]["borne_median"]
                                     - lignes[0]["borne_median"], 3),
            # ⭐⭐⭐ LE VERDICT DE LA TRANCHE : la falaise etait-elle celle de l'instrument ?
            "la_bande_bornee_supprime_la_falaise": bool(
                abs(lignes[-1]["borne_median"] - lignes[0]["borne_median"])
                < 0.5 * abs(lignes[-1]["ancien_median"] - lignes[0]["ancien_median"]))}


def mesurer(chemin: Path = CHEMIN_DE_107, bandes_max: int | None = None,
            fils: int = 32, brouillon: Path | None = None) -> dict:
    """Une lecture de polyligne par marche, et cette fois LE PROFIL BRUT EST GARDE.

    ⭐⭐⭐ GARDER LE PROFIL EST LA LECON DE `102`, DE `107` ET DE `110` PRISE UNE BONNE FOIS. `107` a
    garde ses etapes mais pas son depart ; `110` a garde ses prefixes mais pas ses echantillons,
    donc cette tranche a du repayer trente-quatre minutes de reseau pour relire les MEMES voxels.
    Le profil fait quatre cent trente-neuf nombres par marche : le garder coute deux cent
    cinquante kilooctets et rend toute relecture future gratuite.

    ⚠⚠ `brouillon` ecrit les lectures AVANT que le verdict ne soit calcule — la garde que `110` a
    payee vingt minutes pour apprendre.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement, maintenant  # noqa: PLC0415
    from le_compte_suit_il_le_pas import departs_de_107  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    brut = json.loads(Path(chemin).read_text())
    dep = departs_de_107(bandes_max)
    if "message" in dep:
        return dep
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    lmin, lmax = bornes_de_longueur_donde()
    t0 = maintenant()
    lignes, lectures = [], 0
    bandes = [x for x in brut.get("lignes", [])
              if (int(x["de"]), int(x["a"])) in dep["par_bande"]]
    for i, ligne in enumerate(bandes):
        d = dep["par_bande"][(int(ligne["de"]), int(ligne["a"]))]
        detail = []
        for j, cellule in enumerate(ligne.get("detail", [])):
            if j >= len(d["departs"]):
                break
            cel = {"depart_zyx": [round(float(t), 3) for t in d["departs"][j]]}
            for sel in SELECTEURS:
                m = cellule.get(sel)
                if not m or not m.get("etapes"):
                    continue
                etapes = [x for x in m["etapes"] if "avance_um" in x]
                if len(etapes) < PREFIXE_MIN:
                    continue
                pts, p = [], np.asarray(d["departs"][j], dtype=np.float64).copy()
                for x in etapes:
                    dd = np.asarray(x["direction"], dtype=np.float64)
                    av = float(x["avance_um"]) / C.VOXEL_FIN_UM
                    tt = np.linspace(0.0, 1.0, C.ECHANTILLONS, endpoint=False)
                    pts.append(p[None, :] + dd[None, :] * (av * tt)[:, None])
                    p = p + dd * av
                pts.append(p[None, :])
                zyx = np.rint(np.concatenate(pts)).astype(np.int64)
                if not vol.dans_le_volume(zyx).all():
                    cel[sel] = {"decidable": False, "pourquoi": "le trajet sort du volume"}
                    continue
                v = vol.lire(zyx, fils=fils)
                lectures += 1
                if not np.isfinite(v).all():
                    cel[sel] = {"decidable": False, "pourquoi": "le trajet traverse un trou"}
                    continue
                avance = float(np.mean([float(x["avance_um"]) for x in etapes]))
                cel[sel] = {
                    "decidable": True, "pas": len(etapes),
                    "avance_moyenne_um": round(avance, 2),
                    # ⭐⭐⭐ LE PROFIL BRUT, GARDE. C'est ce que `110` n'a pas fait.
                    "profil": [round(float(t), 2) for t in v],
                    "prefixes": deux_lectures_dun_meme_profil(
                        v, len(etapes), avance, lmin, lmax, C.ECHANTILLONS)}
            detail.append(cel)
        lignes.append({"de": ligne["de"], "a": ligne["a"],
                       "rayon_mm": ligne.get("rayon_mm"), "detail": detail})
        avancement(i + 1, len(bandes), "bandes", t0)

    lu = {"fragment": C.OBJET, "volume_fin": C.VOLUME_FIN,
          "source": str(Path(chemin).relative_to(RACINE)),
          "lambda_min_um": lmin, "lambda_max_um": lmax,
          "lectures": lectures, "secondes": round(maintenant() - t0, 1),
          "bandes": len(lignes), "lignes": lignes}
    if brouillon is not None:
        brouillon.parent.mkdir(parents=True, exist_ok=True)
        brouillon.write_text(json.dumps(lu, indent=2, ensure_ascii=False))
        print(f"lectures écrites avant le verdict : {brouillon}")
    return agreger(lu)


def agreger(r: dict) -> dict:
    """Le verdict, DERIVE des profils gardes — le partage que `107` et `110` imposent."""
    lmin = float(r.get("lambda_min_um") or bornes_de_longueur_donde()[0])
    lmax = float(r.get("lambda_max_um") or bornes_de_longueur_donde()[1])
    courbes, avances, pas_max = [], [], 0
    for ligne in r.get("lignes", []):
        for cel in ligne.get("detail", []):
            for sel in SELECTEURS:
                m = cel.get(sel)
                if not isinstance(m, dict) or not m.get("decidable"):
                    continue
                courbes.append(m.get("prefixes") or [])
                avances.append(float(m.get("avance_moyenne_um") or 0.0))
                pas_max = max(pas_max, int(m.get("pas") or 0))
    r = dict(r)
    # ⚠⚠ LE NUL EST CALCULE AUX LONGUEURS REELLEMENT LUES, pas a des longueurs rondes : la bande
    # depend de la longueur, donc sa barre aussi, et une barre calculee ailleurs ne garde rien.
    if avances and pas_max >= PREFIXE_MIN:
        import combien_dinterstices_traverses as C  # noqa: PLC0415

        av = float(np.median(avances))
        ks = list(range(PREFIXE_MIN, pas_max + 1))
        nul = nul_de_la_bande([k * av for k in ks], lmin, lmax,
                              echantillons_par_pas=C.ECHANTILLONS, pas_par_fenetre=ks)
        r["nul_de_la_bande"] = nul
        barres = {k: x["p99_du_score"] for k, x in zip(ks, nul["par_longueur"])}
    else:
        barres = None
    r["marches_lues"] = len(courbes)
    r["controle_fabrique"] = controle_fabrique()
    r["comparaison"] = comparer(courbes, barres)
    src = RACINE / (r.get("source") or "")
    if src.is_file():
        r["par_mode"] = comparer_par_mode(r.get("lignes", []),
                                          json.loads(src.read_text()), barres)
    return r


def comparer_par_mode(lignes: list[dict], brut_de_107: dict,
                      barres: dict | None = None, part: float = 0.5) -> dict:
    """La comparaison, separee par le mode que `107` a trouve — `110` a montre que le melange ment.

    ⭐⭐⭐ C'EST LA OU LA TRANCHE SE JOUE. Le mode qui ne compte rien est celui dont `110` a mesure
    la falaise ; s'il la perd sous la bande bornee, c'est que la falaise etait celle de
    l'instrument. S'il la garde, c'est la matiere, et la question se referme dans l'autre sens.
    """
    mode = {}
    for ln in brut_de_107.get("lignes", []):
        for cel in ln.get("detail", []):
            for sel in SELECTEURS:
                t = ((cel.get(sel) or {}).get("trajet_entier") or {})
                if t.get("decidable"):
                    mode[(int(ln["de"]), sel)] = bool(
                        float(t["feuilles_franchies"]) >= part * int(t["pas_parcourus"]))
    jeux: dict[str, list] = {"mode_haut": [], "mode_bas": []}
    for ln in lignes:
        for cel in ln.get("detail", []):
            for sel in SELECTEURS:
                m = cel.get(sel)
                if not isinstance(m, dict) or not m.get("decidable"):
                    continue
                cle = (int(ln["de"]), sel)
                if cle not in mode:
                    continue
                jeux["mode_haut" if mode[cle] else "mode_bas"].append(m.get("prefixes") or [])
    out = {nom: (comparer(jeu, barres) if jeu else {"decidable": False, "marches": 0})
           for nom, jeu in jeux.items()}
    a, b = out.get("mode_haut", {}), out.get("mode_bas", {})
    if a.get("decidable") and b.get("decidable"):
        out["falaise_de_lancien_dans_le_mode_bas"] = b["derive_de_lancien"]
        out["falaise_du_borne_dans_le_mode_bas"] = b["derive_du_borne"]
        # ⭐⭐⭐ LE VERDICT : la bande bornee retire-t-elle la falaise du mode qui ne compte rien ?
        out["la_bande_bornee_retire_la_falaise_du_mode_bas"] = bool(
            b.get("la_bande_bornee_supprime_la_falaise"))
        out["ecart_entre_modes_au_plus_long_ancien"] = round(
            a["ancien_au_plus_long"] - b["ancien_au_plus_long"], 3)
        out["ecart_entre_modes_au_plus_long_borne"] = round(
            a["borne_au_plus_long"] - b["borne_au_plus_long"], 3)
        # ⚠⚠ ET LE FAIT QUI DECIDE DE `107` : si la bande bornee rapproche les deux modes, la
        # bimodalite que `107` a publiee etait au moins en partie celle de l'instrument.
        out["la_bande_bornee_rapproche_les_deux_modes"] = bool(
            abs(out["ecart_entre_modes_au_plus_long_borne"])
            < abs(out["ecart_entre_modes_au_plus_long_ancien"]))
    return out


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    print(f"\n{r.get('fragment')} · {r.get('marches_lues')} marches · bande physique "
          f"{r.get('lambda_min_um')} à {r.get('lambda_max_um')} µm "
          f"({r.get('lectures')} lectures, {r.get('secondes')} s)\n")
    cf = r.get("controle_fabrique", {})
    print("CONTRÔLE FABRIQUÉ — feuilles par pas (score), ancien puis BORNÉ")
    for c in cf.get("cas", []):
        a = "  ".join(f"{x['pas']}→{x['ancien']['feuilles_par_pas']:.2f}"
                      f"({x['ancien']['score']:.2f})"
                      for x in c["par_longueur"] if x.get("decidable"))
        b = "  ".join(f"{x['pas']}→{x['borne']['feuilles_par_pas']:.2f}"
                      f"({x['borne']['score']:.2f})"
                      for x in c["par_longueur"] if x.get("decidable"))
        print(f"   {c['cas']:<32} ancien {a}")
        print(f"   {'':<32} BORNÉ  {b}")
    print(f"   ★ la bande bornée garde le compte sous une dérive : "
          f"{cf.get('la_bande_bornee_garde_le_compte_sous_une_derive')} "
          f"(l'ancienne le perd : {cf.get('lancienne_bande_le_perd')})")
    print(f"   ★ sur une dérive SEULE le score s'effondre : "
          f"{cf.get('sur_une_derive_seule_le_score_seffondre')} — "
          f"{cf.get('score_max_sur_une_derive_seule')} contre "
          f"{cf.get('score_min_sur_une_periodicite_pure')} sur une périodicité pure")
    n = r.get("nul_de_la_bande", {})
    if n.get("par_longueur"):
        print(f"\nLA BARRE DE LA BANDE BORNÉE, LONGUEUR PAR LONGUEUR ({n['tirages']} tirages)")
        for x in n["par_longueur"]:
            print(f"   {x['longueur_um']:>7.0f} µm · f de {x['f_min']:.2f} à {x['f_max']:.2f} · "
                  f"p99 {x['p99_du_score']:.4f}")
        print(f"   ★ la barre BAISSE avec la longueur : "
              f"{n['la_barre_baisse_avec_la_longueur']} (pente {n['pente_de_la_barre']:+.4f}) — "
              f"la bande bornée devient PLUS discriminante quand la marche s'allonge")
    c = r.get("comparaison", {})
    if c.get("decidable"):
        print(f"\nLES DEUX BANDES SUR LES MÊMES PROFILS")
        print(f"   {'pas':>4} {'marches':>8} {'ancien':>8} {'BORNÉ':>8} "
              f"{'sc.anc':>8} {'sc.bor':>8} {'>barre':>8}")
        for x in c["par_longueur"]:
            print(f"   {x['pas']:>4} {x['marches']:>8} {x['ancien_median']:>8.3f} "
                  f"{x['borne_median']:>8.3f} {x['score_ancien_median']:>8.3f} "
                  f"{x['score_borne_median']:>8.3f} "
                  f"{x.get('part_au_dessus_de_la_barre', float('nan')):>8.3f}")
        print(f"   ★ dérive de l'ancien {c['derive_de_lancien']:+.3f} · "
              f"du BORNÉ {c['derive_du_borne']:+.3f}")
    pm = r.get("par_mode", {})
    if pm.get("mode_haut", {}).get("decidable") and pm.get("mode_bas", {}).get("decidable"):
        print(f"\n★★★ PAR MODE — la falaise est-elle celle de l'instrument ?")
        for nom in ("mode_haut", "mode_bas"):
            b = pm[nom]
            print(f"   {nom:<11} ancien "
                  + "  ".join(f"{x['pas']}→{x['ancien_median']:.3f}"
                              for x in b["par_longueur"])
                  + f"  · dérive {b['derive_de_lancien']:+.3f}")
            print(f"   {'':<11} BORNÉ  "
                  + "  ".join(f"{x['pas']}→{x['borne_median']:.3f}"
                              for x in b["par_longueur"])
                  + f"  · dérive {b['derive_du_borne']:+.3f}")
        print(f"   ★★★ LA BANDE BORNÉE RETIRE-T-ELLE LA FALAISE DU MODE BAS ? "
              f"{'OUI' if pm.get('la_bande_bornee_retire_la_falaise_du_mode_bas') else 'NON'}")
        print(f"   ★ écart entre les modes au plus long : "
              f"{pm['ecart_entre_modes_au_plus_long_ancien']:+.3f} avec l'ancien, "
              f"{pm['ecart_entre_modes_au_plus_long_borne']:+.3f} avec le BORNÉ")
        print(f"   ★ la bande bornée RAPPROCHE les deux modes : "
              f"{pm.get('la_bande_bornee_rapproche_les_deux_modes')}")


def _courbe(paires, pas_debut: int = PREFIXE_MIN) -> list[dict]:
    """Une courbe de prefixes fabriquee : `(ancien, borne)` par longueur."""
    return [{"pas": pas_debut + i, "decidable": True, "longueur_um": 230.0 * (pas_debut + i),
             "ancien": {"feuilles": a * (pas_debut + i), "feuilles_par_pas": a, "score": 0.5,
                        "en_butee": False},
             "borne": {"feuilles": b * (pas_debut + i), "feuilles_par_pas": b, "score": 0.6,
                       "en_butee": False}}
            for i, (a, b) in enumerate(paires)]


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === LA BANDE =============================================================================
    # ⭐⭐⭐ LA PROPRIETE QUI EST TOUTE LA TRANCHE : la longueur d'onde admissible NE BOUGE PAS avec
    # la fenetre, alors que le nombre de periodes, lui, grandit. C'est exactement l'inverse de ce
    # que `98` fait, et c'est ce qui ferme la porte a la derive.
    a2, b2 = bande_de_frequences(460.0, 86.5, 346.0)
    a6, b6 = bande_de_frequences(1380.0, 86.5, 346.0)
    v("la bande grandit avec la fenêtre, en PÉRIODES",
      a6 > a2 and b6 > b2, f"{a2:.3f}–{b2:.3f} puis {a6:.3f}–{b6:.3f}")
    v("... mais la LONGUEUR D'ONDE admissible ne bouge pas",
      abs(460.0 / b2 - 1380.0 / b6) < 1e-9 and abs(460.0 / a2 - 1380.0 / a6) < 1e-9,
      f"λ de {460.0 / b2:.1f} à {460.0 / a2:.1f} µm dans les deux cas")
    # ⚠ La plus GRANDE longueur d'onde donne la plus PETITE frequence : les inverser mettrait le
    # plancher au plafond, et l'estimateur chercherait une feuille tous les quatre-vingts microns.
    v("... et la plus grande longueur d'onde donne la plus petite fréquence",
      a2 < b2 and abs(a2 - 460.0 / 346.0) < 1e-9)
    for mauvais in ((460.0, 0.0, 346.0), (460.0, 346.0, 86.5), (0.0, 86.5, 346.0)):
        try:
            bande_de_frequences(*mauvais)
            ok = False
        except ValueError:
            ok = True
        v(f"une bande absurde est refusée plutôt que calculée {mauvais}", ok)
    # ⚠⚠ ET LES BORNES VIENNENT DU BALAYAGE DE `105`, PAS DE CETTE TRANCHE : si un jour la plage
    # des candidats bouge, les deux bougent ensemble.
    lmin, lmax = bornes_de_longueur_donde()
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    cands = M.candidats_de_pas(C.PAS_UM)
    v("les bornes de longueur d'onde SONT les candidats du balayage",
      abs(lmin - float(np.min(cands))) < 1e-9 and abs(lmax - float(np.max(cands))) < 1e-9,
      f"{lmin} à {lmax} µm")

    # === CE QUE LA BANDE BORNEE REPARE ========================================================
    # ⭐⭐⭐ LE CONTROLE CENTRAL, ET IL DOIT TRANCHER DANS LES DEUX SENS : la bande bornee garde le
    # compte sous une derive que l'ancienne PERD. Si l'ancienne ne le perdait pas, il n'y aurait
    # rien a reparer et cette tranche n'aurait pas lieu d'etre.
    cf = controle_fabrique()
    v("la bande bornée garde le compte sous une dérive",
      cf["la_bande_bornee_garde_le_compte_sous_une_derive"] is True)
    v("... là où l'ancienne bande le PERD",
      cf["lancienne_bande_le_perd"] is True)
    # ⚠⚠⚠ LE PRIX DE LA BANDE ETROITE : elle ne peut plus dire « pas de periodicite » PAR SON
    # COMPTE. C'est le SCORE qui doit l'ecarter, et la garde le verifie sur une derive SEULE.
    v("sur une dérive SEULE, le score de la bande bornée s'effondre",
      cf["sur_une_derive_seule_le_score_seffondre"] is True,
      f"{cf['score_max_sur_une_derive_seule']} contre "
      f"{cf['score_min_sur_une_periodicite_pure']} sur une périodicité pure")
    pure = next(x for x in cf["cas"] if x["cas"] == "periodicite pure")
    v("... et sur une périodicité pure les deux bandes s'accordent",
      all(abs(x["ancien"]["feuilles_par_pas"] - x["borne"]["feuilles_par_pas"]) < 0.05
          for x in pure["par_longueur"] if x.get("decidable")),
      str([(x["pas"], x["ancien"]["feuilles_par_pas"], x["borne"]["feuilles_par_pas"])
           for x in pure["par_longueur"] if x.get("decidable")][:3]))
    # ⚠ Le bruit pur est le second controle negatif : un instrument qui y trouverait une feuille
    # par pas au score haut serait pire que celui qu'il remplace.
    bruit = next(x for x in cf["cas"] if x["cas"] == "bruit pur")
    v("sur du bruit pur, le score de la bande bornée reste bas",
      max(x["borne"]["score"] for x in bruit["par_longueur"] if x.get("decidable")) < 0.5,
      str(max(x["borne"]["score"] for x in bruit["par_longueur"] if x.get("decidable"))))

    # === LE NUL DE LA BANDE, LONGUEUR PAR LONGUEUR ============================================
    # ⭐⭐ LA BARRE CHANGE AVEC LA LONGUEUR, ce qui n'etait pas vrai de `98` : une bande plus large
    # trouve plus facilement un accord sur du bruit. Publier une barre unique ferait passer pour
    # significatif a six pas ce qui ne l'est pas.
    ks = [2, 4, 6]
    nul = nul_de_la_bande([k * 230.0 for k in ks], lmin, lmax,
                          echantillons_par_pas=C.ECHANTILLONS, pas_par_fenetre=ks,
                          tirages=200)
    v("le nul rend une barre par longueur", len(nul["par_longueur"]) == 3)
    # ⚠⚠⚠ ET LE SENS DE LA PENTE EST UNE MESURE, PAS UNE HYPOTHESE : j'avais asserte qu'elle
    # MONTE, et le nul a dit l'inverse. Deux effets s'opposent — la bande s'elargit, mais le
    # nombre d'echantillons grandit et la correlation fortuite decroit en `1/racine(n)` — et
    # c'est le second qui gagne. La bande bornee devient donc PLUS discriminante quand la marche
    # s'allonge.
    v("... et la barre BAISSE avec la longueur, parce que les échantillons grandissent",
      nul["la_barre_baisse_avec_la_longueur"] is True,
      str([x["p99_du_score"] for x in nul["par_longueur"]]))
    # ⚠⚠ ET LA BARRE DE LA BANDE BORNEE DOIT DIFFERER DE CELLE DE `98` : reprendre la barre de
    # l'ancienne famille serait donner a une forme la barre d'une autre, ce que ce depot a deja
    # paye en `98`.
    p99_ancien = C.nul_de_lestimateur_continu(
        tirages=200).get("barre_de_la_famille_continue")
    v("... et elle diffère de la barre de la famille de `98`",
      p99_ancien is not None and abs(nul["barre"] - p99_ancien) > 0.02,
      f"{nul['barre']} contre {p99_ancien}")

    # === LA COMPARAISON =======================================================================
    # ⭐⭐⭐ LE VERDICT DOIT POUVOIR DIRE NON : si la bande bornee tombait de la meme falaise, elle
    # ne reparerait rien et la tranche devrait le publier.
    falaise = comparer([_courbe([(1.0, 1.0), (0.2, 1.0), (0.15, 1.0), (0.12, 1.0),
                                 (0.1, 1.0)])] * 6)
    v("une falaise que la bande bornée supprime est annoncée comme telle",
      falaise["la_bande_bornee_supprime_la_falaise"] is True,
      f"ancien {falaise['derive_de_lancien']:+.3f}, borné {falaise['derive_du_borne']:+.3f}")
    deux = comparer([_courbe([(1.0, 1.0), (0.2, 0.2), (0.15, 0.15), (0.12, 0.12),
                              (0.1, 0.1)])] * 6)
    v("... et une falaise que les DEUX subissent ne l'est PAS",
      deux["la_bande_bornee_supprime_la_falaise"] is False,
      f"ancien {deux['derive_de_lancien']:+.3f}, borné {deux['derive_du_borne']:+.3f}")
    v("la comparaison se refuse sans profil lisible",
      comparer([])["decidable"] is False)
    # ⚠ La part au-dessus de la barre est rendue quand la barre est fournie, et seulement alors :
    # une part calculee contre une barre absente serait un nombre sans reference.
    avec = comparer([_courbe([(1.0, 1.0)] * 5)] * 4, {2: 0.4, 3: 0.4, 4: 0.4, 5: 0.4, 6: 0.4})
    v("la part au-dessus de la barre est rendue quand une barre est donnée",
      all("part_au_dessus_de_la_barre" in x for x in avec["par_longueur"]))
    sans = comparer([_courbe([(1.0, 1.0)] * 5)] * 4)
    v("... et absente quand il n'y en a pas",
      all("part_au_dessus_de_la_barre" not in x for x in sans["par_longueur"]))

    # === LES DEUX LECTURES D'UN MEME PROFIL ===================================================
    n = 4 * C.ECHANTILLONS + 1
    t = np.linspace(0.0, 4.0, n)
    pref = deux_lectures_dun_meme_profil(100.0 + 40.0 * np.cos(2.0 * np.pi * t), 4, 230.0,
                                         lmin, lmax, C.ECHANTILLONS)
    v("les deux lectures portent une ligne par longueur",
      [x["pas"] for x in pref] == [2, 3, 4])
    v("... et chacune porte les DEUX bandes sur les MÊMES échantillons",
      all("ancien" in x and "borne" in x for x in pref if x["decidable"]))
    v("... et sur une périodicité parfaite les deux rendent le compte juste",
      all(abs(x["borne"]["feuilles_par_pas"] - 1.0) < 0.05 for x in pref if x["decidable"]),
      str([(x["pas"], x["borne"]["feuilles_par_pas"]) for x in pref if x["decidable"]]))
    plat = deux_lectures_dun_meme_profil(np.full(n, 100.0), 4, 230.0, lmin, lmax,
                                         C.ECHANTILLONS)
    v("un profil plat est déclaré non décidable par les deux",
      all(not x["decidable"] for x in plat))

    # === L'AGREGATION SURVIT AU BROUILLON SEUL ================================================
    # ⚠⚠ `agreger` doit tourner sur un brouillon, sinon `--reagreger` ne servirait a rien — la
    # garde que `110` a payee vingt minutes pour apprendre.
    brouillon = {"lambda_min_um": lmin, "lambda_max_um": lmax, "source": "",
                 "lignes": [{"de": 1, "a": 2, "detail": [{"calibre": {
                     "decidable": True, "pas": 6, "avance_moyenne_um": 230.0,
                     "prefixes": _courbe([(1.0, 1.0)] * 5)}}]}]}
    ag = agreger(brouillon)
    v("l'agrégation tourne sur un brouillon seul", ag.get("marches_lues") == 1)
    v("... et calcule la barre aux longueurs RÉELLEMENT lues",
      bool(ag.get("nul_de_la_bande", {}).get("par_longueur")),
      str([x["longueur_um"] for x in ag.get("nul_de_la_bande", {}).get("par_longueur", [])]))

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 0 if echecs == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--source", type=Path, default=CHEMIN_DE_107)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--fils", type=int, default=32)
    p.add_argument("--reagreger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = agreger(json.loads(a.json.read_text()))
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    r = mesurer(chemin=a.source, bandes_max=a.bandes, fils=a.fils, brouillon=a.json)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
