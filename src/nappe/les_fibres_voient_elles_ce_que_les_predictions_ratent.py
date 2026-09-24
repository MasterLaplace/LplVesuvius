"""Les fibres voient-elles la feuille que les deux prédictions de surface ratent ensemble ?

⭐⭐⭐⭐ LA SUITE DE `251` ET `254`. Là où `m7` et `ps256` s'accordent, elles ratent ensemble environ un point sur vingt, et
ni le retour, ni le désaccord, ni la surface voisine ne le voient. Il faut une source que ces deux prédictions n'ont pas
lue. PHercParis4 en publie une autre, entraînée pour une autre cible : deux prédictions de FIBRES, dont un canal
`presence` dit où le modèle voit des fibres de papyrus, donc de la feuille. Là où la chaîne est tombée sur rien, les
fibres devraient ne rien voir ; là où la bande a sa couche, elles devraient voir quelque chose.

⚠⚠⚠ CE QUI EST DÉCLARÉ AVANT LA MESURE, et c'est le protocole de `249`, appliqué à la présence de fibres au lieu du scan :
  - la présence est lue au niveau 3 (19,2 µm, le plus fin publié), le long de la normale du segment, sur 3 × 3 rayons
    voisins espacés d'un voxel de ce niveau, rapportée à la présence sur la feuille du segment, dans une fenêtre de huit
    voxels du maillage de part et d'autre de la profondeur ;
  - deux témoins sur les points où `m7` et `ps256` s'accordent et sont justes : la profondeur de la chute (une feuille) et
    la mi-chemin (un interstice) ; le seuil de Youden entre eux, sa sensibilité, ses fausses alertes ;
  - les RATÉS COMMUNS de `251` (les deux prédictions d'accord, les deux ratées), trop près et trop loin : la part où les
    fibres voient une feuille là où la chaîne est tombée, et là où la bande a sa couche ;
  - le juge en moyenne de `249` : les profils médians alignés, et leur contraste ;
  - les deux prédictions de fibres publiées, notées côte à côte.

⚠⚠ Le niveau 3 est deux fois plus grossier que les prédictions de surface : à 19,2 µm un pas fait neuf voxels et une
feuille deux ou trois. `17` a déjà vu la phase `lasagna` de ce niveau se diffuser sur plusieurs pas.

Usage :
    uv run python src/nappe/les_fibres_voient_elles_ce_que_les_predictions_ratent.py --verifier
    uv run python src/nappe/les_fibres_voient_elles_ce_que_les_predictions_ratent.py \\
        --json docs/mesures/les_fibres_voient_elles_ce_que_les_predictions_ratent.json
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
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

from deux_predictions_trahissent_elles_le_saut_rate import le_desaccord  # noqa: E402
from la_bande_a_t_elle_manque_un_tour import (LE_DERRIERE, LES_TEMOINS_PAR_COTE, la_moyenne_autour,  # noqa: E402
                                              la_part_de_vraies_feuilles, le_contraste_et_son_intervalle,
                                              le_profil_aligne, le_profil_brut, le_seuil, un_sur_k)
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, PAS_EN_VOXELS,  # noqa: E402
                                                les_normales, lire_tifxyz, telecharger)
from le_transfert_enchaine_tient_il_les_spires import (LA_BANDE, LA_TRANCHE, LES_SAUTS,  # noqa: E402
                                                       les_couches_ordonnees)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LA_MAILLE, le_facteur,  # noqa: E402
                                                         lecteur_du_depot)

LES_FIBRES = {
    "fibres_0801": ("PHercParis4/representations/predictions/fibers/20260411134726-fibers-20260801084232-L1/"
                    "PHercParis4-20260411134726-las-sd1-d74cca79_presence.ome.zarr", 3),
    "fibres_0915": ("PHercParis4/representations/predictions/fibers/20260411134726-fibers-20260915212757-L1/"
                    "PHercParis4-20260411134726-las-sd1-7ff0ce6c_presence.ome.zarr", 3),
}


def les_groupes_communs(t_m7: np.ndarray, t_ps: np.ndarray, t_b: np.ndarray, cote: float) -> dict:
    """Les points où les deux prédictions s'accordent et sont justes, et ceux où elles s'accordent et ratent toutes les
    deux, trop près ou trop loin (le côté est celui de `m7`)."""
    note = np.isfinite(t_b)
    accord = note & ~le_desaccord(t_m7, t_ps)
    with np.errstate(invalid="ignore"):
        err = cote * (t_m7 - t_b)
        juste_m7 = np.abs(err) < DEMI_PAS_EN_VOXELS
        juste_ps = np.abs(t_ps - t_b) < DEMI_PAS_EN_VOXELS
    communs = accord & ~juste_m7 & ~juste_ps
    return {"accord_et_juste": accord & juste_m7 & juste_ps,
            "rates_communs_trop_pres": communs & (err <= -DEMI_PAS_EN_VOXELS),
            "rates_communs_trop_loin": communs & (err >= DEMI_PAS_EN_VOXELS)}


def juger_avec_les_fibres(profil: np.ndarray, t: np.ndarray, tau: np.ndarray, t_b: np.ndarray, groupes: dict,
                          temoins: np.ndarray) -> dict:
    """Le seuil étalonné sur les témoins, ce que les fibres voient là où la chaîne est tombée et là où la bande a sa
    couche, et le juge en moyenne."""
    soi = la_moyenne_autour(profil, t, np.zeros(len(tau)))

    def s(centre):
        with np.errstate(invalid="ignore", divide="ignore"):
            return la_moyenne_autour(profil, t, centre) / soi

    seuil = le_seuil(s(tau)[temoins], s(tau / 2.0)[temoins])
    # ⚠⚠⚠ AJOUTÉ APRÈS LA MESURE, ET DIT COMME TEL : la présence de fibres est souvent nulle, y compris sur la feuille du
    # segment, et le rapport du protocole de `249` y devient instable. La part des témoins sans fibre sur le segment dit
    # pourquoi, et le même seuil est pris sur la présence brute, sans rapport.
    brute = {c: la_moyenne_autour(profil, t, centre) for c, centre in (("feuille", tau), ("interstice", tau / 2.0))}
    seuil_brut = le_seuil(brute["feuille"][temoins], brute["interstice"][temoins])
    out_brut = {"la_part_des_temoins_sans_fibre_sur_le_segment": round(float((soi[temoins] == 0).mean()), 4),
                "la_part_des_temoins_sans_fibre_a_la_chute": round(float((brute["feuille"][temoins] == 0).mean()), 4),
                "le_seuil_sur_la_presence_brute": {k: round(v, 4) for k, v in seuil_brut.items()}}
    out = {"les_temoins": int(temoins.sum()), "le_seuil": {k: round(v, 4) for k, v in seuil.items()},
           "sans_rapport": out_brut,
           "en_moyenne": {"le_temoin_feuille": le_contraste_et_son_intervalle(le_profil_aligne(profil, t, tau, soi)[temoins]),
                          "le_temoin_interstice": le_contraste_et_son_intervalle(
                              le_profil_aligne(profil, t, tau / 2.0, soi)[temoins])},
           "les_rates_communs": {}}
    for nom in ("rates_communs_trop_pres", "rates_communs_trop_loin"):
        g = groupes[nom]
        if not g.any():
            out["les_rates_communs"][nom] = {"combien": 0}
            continue
        r = {"combien": int(g.sum())}
        for ou, centre in (("la_ou_la_chaine_est_tombee", tau), ("la_ou_la_bande_a_sa_couche", t_b)):
            v = s(centre)[g]
            part = float((v[np.isfinite(v)] >= seuil["le_seuil"]).mean()) if np.isfinite(v).any() else None
            vraies = None if part is None else la_part_de_vraies_feuilles(part, seuil["la_sensibilite"],
                                                                           seuil["les_fausses_alertes"])
            r[ou] = {"la_part_au_dessus_du_seuil": None if part is None else round(part, 4),
                     "la_part_de_vraies_feuilles": None if vraies is None else round(vraies, 4),
                     "en_moyenne": le_contraste_et_son_intervalle(le_profil_aligne(profil, t, centre, soi)[g])}
        out["les_rates_communs"][nom] = r
    return out


def mesurer(cache: Path = LE_CACHE, maille: int = LA_MAILLE, delai: float = DELAI) -> dict:
    debut = time.monotonic()
    d = telecharger(LA_BANDE, cache, delai)
    if isinstance(d, str):
        return {"decidable": False, "la_raison": d}
    ref, valide, esp = lire_tifxyz(d)
    h = ref.shape[0]
    a, b = int(h * LA_TRANCHE[0]), int(h * LA_TRANCHE[1])
    ref, valide = ref[a:b], valide[a:b]
    couches = les_couches_ordonnees(ref, valide, esp, maille, LES_SAUTS)["les_cartes"]
    normales, ok = les_normales(ref, valide)
    grille = np.zeros_like(ok)
    grille[::maille, ::maille] = True
    ii, jj = np.nonzero(ok & grille)
    p, n = ref[ii, jj], normales[ii, jj]
    gi, gj = ii // maille, jj // maille
    out = {"la_bande": LA_BANDE, "les_rangees": list(LA_TRANCHE), "les_points": int(len(p)), "les_fibres": {}}
    t_max = float(np.ceil(LES_SAUTS * PAS_EN_VOXELS))
    lectures = {}
    for cote_, nom, cote in (("plus", "du_cote_plus", 1.0), ("moins", "du_cote_moins", -1.0)):
        t_b = couches[cote_][gi, gj, 0]
        sauts = {}
        for nom_p in ("m7", "ps256"):
            f = cache / f"transfert_suivante_{LA_BANDE}_{nom_p}_{nom}.npy"
            if not f.exists():
                return {"decidable": False, "la_raison": f"le premier saut de 247 manque : {f.name}"}
            sauts[nom_p] = np.load(f)[gi, gj]
        groupes = les_groupes_communs(sauts["m7"], sauts["ps256"], t_b, cote)
        temoins = un_sur_k(groupes["accord_et_juste"], LES_TEMOINS_PAR_COTE)
        a_lire = temoins | groupes["rates_communs_trop_pres"] | groupes["rates_communs_trop_loin"]
        out.setdefault("les_groupes", {})[nom] = {k: int(g.sum()) for k, g in groupes.items()}
        t = cote * np.arange(-LE_DERRIERE, t_max + 1.0)
        for nom_f, (chemin, niveau) in LES_FIBRES.items():
            facteur, meta = le_facteur(chemin, niveau, delai)
            lire, stats = lecteur_du_depot(meta, cache, nom_f, chemin, niveau, delai)
            lectures[nom_f] = stats
            profil = np.full((len(p), len(t)), np.nan)
            profil[a_lire] = le_profil_brut(p[a_lire], n[a_lire], t, facteur, meta, lire)
            r = out["les_fibres"].setdefault(nom_f, {"le_facteur": facteur})
            r[nom] = juger_avec_les_fibres(profil, t, sauts["m7"], t_b, groupes, temoins)
    out["la_lecture"] = {k: {"chunks_lus": s["lus"], "combien_de_pannes": len(s["pannes"]), "les_pannes": s["pannes"][:10]}
                         for k, s in lectures.items()}
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = all(not s["pannes"] for s in lectures.values())
    return out


def afficher(r: dict) -> None:
    if "les_points" not in r:
        print(f"indécidable : {r.get('la_raison')}")
        return
    print(f"{r['la_bande']} : {r['les_points']} points, groupes {r['les_groupes']}, {r['les_secondes']} s, lecture {r['la_lecture']}")
    for nom_f, rf in r["les_fibres"].items():
        for nom in ("du_cote_plus", "du_cote_moins"):
            j = rf[nom]
            m = j["en_moyenne"]
            print(f"    sans rapport {j['sans_rapport']}")
            print(f"— {nom_f} {nom} : seuil {j['le_seuil']} ; en moyenne feuille {m['le_temoin_feuille']['le_contraste']} "
                  f"[{m['le_temoin_feuille']['q05']}, {m['le_temoin_feuille']['q95']}] interstice "
                  f"{m['le_temoin_interstice']['le_contraste']} [{m['le_temoin_interstice']['q05']}, {m['le_temoin_interstice']['q95']}]")
            for g, c in j["les_rates_communs"].items():
                if not c.get("combien"):
                    continue
                for ou in ("la_ou_la_chaine_est_tombee", "la_ou_la_bande_a_sa_couche"):
                    x = c[ou]
                    print(f"    {g} ({c['combien']}) {ou:28s} au-dessus {x['la_part_au_dessus_du_seuil']} vraies "
                          f"{x['la_part_de_vraies_feuilles']} contraste {x['en_moyenne']['le_contraste']} "
                          f"[{x['en_moyenne']['q05']}, {x['en_moyenne']['q95']}] amplitude {x['en_moyenne']['lamplitude']}")


# ---------------------------------------------------------------------------------------------------
def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ LES GROUPES : accord et juste, raté commun trop près, raté commun trop loin, un désaccord, un raté seul.
    t_b = np.array([72.0, 150.0, 72.0, 72.0, 72.0, np.nan])
    m7 = np.array([74.0, 72.0, 150.0, 72.0, 150.0, 72.0])
    ps = np.array([70.0, 75.0, 148.0, 150.0, 72.0, 72.0])
    g = les_groupes_communs(m7, ps, t_b, 1.0)
    v("★★★★ accord et juste, raté commun trop près, raté commun trop loin ; un désaccord et un raté seul n'y sont pas",
      g["accord_et_juste"].tolist() == [True, False, False, False, False, False]
      and g["rates_communs_trop_pres"].tolist() == [False, True, False, False, False, False]
      and g["rates_communs_trop_loin"].tolist() == [False, False, True, False, False, False], str(g))
    gm = les_groupes_communs(-m7, -ps, -t_b, -1.0)
    v("★★★ de l'autre côté, les mêmes groupes", all(np.array_equal(g[k], gm[k]) for k in g))

    # ⭐⭐⭐⭐ LE JUGE, sur des profils fabriqués : des témoins qui séparent ; un raté commun tombé sur rien alors que la bande a
    # une feuille, et un autre tombé sur une vraie feuille que la bande n'a pas prise.
    tt = np.arange(-12.0, 301.0)
    N = 403
    prof = np.full((N, len(tt)), 20.0)
    prof[:, np.abs(tt) <= 10] = 200.0
    prof[:400, np.abs(tt - 72) <= 10] = 200.0
    prof[400, np.abs(tt - 144) <= 10] = 200.0          # la bande à 144, la chaîne à 72 sur rien
    prof[401, np.abs(tt - 72) <= 10] = 200.0           # la chaîne à 72 sur une feuille, la bande à 144 sur rien
    prof[402, np.abs(tt - 144) <= 10] = 200.0
    tau = np.r_[np.full(400, 72.0), 72.0, 72.0, 72.0]
    tb = np.r_[np.full(400, 72.0), 144.0, 144.0, 144.0]
    groupes = {"accord_et_juste": np.r_[np.ones(400, bool), False, False, False],
               "rates_communs_trop_pres": np.r_[np.zeros(400, bool), True, True, True],
               "rates_communs_trop_loin": np.zeros(N, bool)}
    j = juger_avec_les_fibres(prof, tt, tau, tb, groupes, groupes["accord_et_juste"])
    c = j["les_rates_communs"]["rates_communs_trop_pres"]
    v("★★★★ les témoins séparent la feuille de l'interstice", j["le_seuil"]["laire_sous_la_courbe"] == 1.0, str(j["le_seuil"]))
    v("★★★★ un raté commun sur trois est tombé sur une feuille", c["la_ou_la_chaine_est_tombee"]["la_part_au_dessus_du_seuil"]
      == round(1 / 3, 4), str(c["la_ou_la_chaine_est_tombee"]))
    v("★★★★ et deux sur trois ont une feuille là où la bande a sa couche",
      c["la_ou_la_bande_a_sa_couche"]["la_part_au_dessus_du_seuil"] == round(2 / 3, 4), str(c["la_ou_la_bande_a_sa_couche"]))
    v("★★★ un groupe vide ne rend rien", j["les_rates_communs"]["rates_communs_trop_loin"] == {"combien": 0})
    v("★★ les deux prédictions de fibres sont lues au niveau 3", all(nv == 3 for _, nv in LES_FIBRES.values()))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} ({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--delai", type=float, default=DELAI)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(LE_CACHE, LA_MAILLE, a.delai)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
