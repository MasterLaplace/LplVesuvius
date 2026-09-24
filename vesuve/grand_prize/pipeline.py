"""Le pipeline du Grand Prize : dérouler automatiquement, et dire exactement jusqu'où.

La question du prix tient en une ligne : qu'est-ce qui remplace l'humain qui corrige le transfert de spire
à spire ? La réponse que ce pipeline exécute est celle de `244` et `246` : le treillis donne le pas de
chaque couture, le consensus de cinq voisines retire le bruit propre de chaque ligne, et une boucle qui se
referme sous le demi-feuillet coupe après coupe certifie que ses deux chemins n'ont pas changé de spire.

Les étages, dans l'ordre de `213` §2 et `244` §5 :

    E0 l'objet        est-il éligible, et sinon ce que ça coûte
    E1 le volume      la présence des chunks du volume de surface
    E2 l'échelle      le demi-feuillet
    B  le budget      jusqu'où une nappe tient : pourquoi on ferme des boucles au lieu de marcher
    E4 le treillis    les pas des bandes, publiées ou lues ici
    E6 le certificat  la procédure sans main, et le masque par chunk
    E7 le juge        (option) le pic de matière des chunks certifiés, sans vérité terrain
    E8 l'encre        la carte d'encre publiée, sous le masque
    E9 l'emballage    le masque, la surface certifiée et son `approval.tif`, et ce qui n'est pas produit
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import tifffile

from vesuve import catalogue, donnees, images, noyau, tifxyz
from vesuve.distant import Distant, Indisponible
from vesuve.noyau import Indecidable
from vesuve.rapport import Rapport
from vesuve.transport import Transport
from vesuve.treillis import certificat as cert
from vesuve.treillis.digest import CacheDeDigests
from vesuve.treillis.lecture import LecteurDeBandes
from vesuve.treillis.segment import certifier_le_segment, la_carte_dencre_publiee, les_lectures_en_plus
from vesuve.zarr_distant import LE_BUCKET, TableauDistant

LA_COUCHE_TRACEE = 54  # un volume de surface a 109 couches centrées sur la surface tracée
LE_DEBIT_MESURE = 19.0  # chunks par seconde à 16 fils, mesuré sur la plus petite bande publiée


def _certifier(A, s, neuves):
    return certifier_le_segment(s["contexte"]["le_segment"], neuves)[1]


def lancer(segment: str = "20230702185753", sortie: Path = Path("sorties/grand-prize"), cache: Path = Path("cache"),
           lire: bool = False, tours: int = 6, fils: int = 16, lectures=(), juger: int = 0, encre: bool = True,
           surface: bool = True, journal=None) -> Rapport:
    s = donnees.le_segment(segment)
    ctx = s["contexte"]
    r = Rapport("grand-prize", {"segment": segment, "lobjet": ctx["lobjet"], "lire": lire, "tours": tours,
                                "fils": fils, "lectures_en_plus": [str(x) for x in lectures], "juger": juger},
                journal)
    sortie = Path(sortie)
    transport = Transport(journal=journal)
    distant = Distant(cache, transport)

    with r.etage("E0", "l'objet") as e:
        ok = catalogue.est_eligible("grand-prize", ctx["lobjet"])
        e.noter(lobjet=ctx["lobjet"], le_segment=segment, eligible=ok,
                les_eligibles=[v.objet for v in catalogue.LE_GRAND_PRIX])
        if not ok:
            e.partiel(f"{ctx['lobjet']} n'est pas un des treize rouleaux du prix : la méthode est construite là où "
                      f"le référent existe, et il faudra la transporter sur un rouleau sans vérité de terrain (`151` E0)")

    A = s["presence"]
    with r.etage("E1", "le volume") as e:
        e.noter(le_volume=ctx["le_volume"], la_grille=list(A.shape), les_chunks_presents=int(A.sum()),
                la_provenance="la liste des clés du dépôt, relue par `ou_sarrete_le_segment.py` (98 pages)")

    with r.etage("E2", "l'échelle") as e:
        demi = e.appliquer("E2", ctx["le_pas_um"], ctx["le_voxel_um"], s_um=ctx["le_pas_um"], v_um=ctx["le_voxel_um"])
        if demi != ctx["la_procedure"]["demi"]:
            e.arreter(f"le demi-feuillet recalculé ({demi}) n'est pas celui de la procédure ({ctx['la_procedure']['demi']})")

    with r.etage("B", "le budget de la nappe") as e:
        b = ctx["le_budget"]
        tenables = {}
        for famille in ("traverser", "saccorder"):
            for nom, sigma in b[famille].items():
                tenables[f"{famille} {nom}"] = e.appliquer("N5", float(demi), float(sigma), budget=f"{famille} {nom}",
                                                           delta=demi, sigma=sigma)
        s_ = b["saccorder"]
        e.appliquer("N7", s_["198-197"] ** 2, s_["198-199"] ** 2, s_["197-199"] ** 2,
                    rangee=198, var_198_197=s_["198-197"] ** 2, var_198_199=s_["198-199"] ** 2,
                    var_197_199=s_["197-199"] ** 2)
        liant = min(v for k, v in tenables.items() if k.startswith("saccorder"))
        e.noter(la_longueur_tenable_qui_lie=round(liant, 2), les_coutures_dune_rangee=b["les_coutures_dune_rangee"],
                la_conclusion=(f"une rangée de {b['les_coutures_dune_rangee']} coutures dépasse les {liant:.2f} que "
                               f"l'accord permet : deux rangées marchées chacune pour soi finissent sur deux "
                               f"feuillets (`R4-F341`). D'où le certificat : fermer des boucles plutôt que marcher."))

    neuves = les_lectures_en_plus(lectures)
    with r.etage("E4", "le treillis : les bandes publiées", "B4") as e:
        e.noter(les_bandes_publiees=len(s["bandes"]), les_bandes_donnees=len(neuves))
        try:
            res = _certifier(A, s, neuves)
        except cert.LectureRefusee as x:
            e.arreter(f"une bande lue en plus ne retombe pas sur ce qui est publié : {x}")
    if r.arrete:
        r.ecrire(sortie)
        return r
    with r.etage("E4L", "le treillis : lire ce que la procédure demande", "B4") as e:
        lus, tour = 0, 0
        if lire and res["les_demandes"]:
            t = TableauDistant(f"{LE_BUCKET}/{ctx['le_volume']}", transport)
            lecteur = LecteurDeBandes(t, CacheDeDigests(Path(cache) / "digests", t.url), fils, journal, segment)
            for tour in range(1, tours + 1):
                for d in res["les_demandes"]:
                    try:
                        neuves[d["cle"]] = lecteur.lire(d)
                    except Indecidable as x:
                        e.partiel(f"la bande {d['cle']} n'a pas pu être lue : {x}")
                        break
                (sortie / "lectures").mkdir(parents=True, exist_ok=True)
                (sortie / "lectures" / "bandes_lues.json").write_text(
                    json.dumps({"les_bandes": neuves}, ensure_ascii=False))
                try:
                    res = _certifier(A, s, neuves)
                except cert.LectureRefusee as x:
                    e.arreter(f"une bande lue ici ne retombe pas sur ce qui est publié : {x}")
                    break
                if not res["les_demandes"] or e.donnees["etat"] != "fait":
                    break
            lus = lecteur.chunks_lus
        e.noter(les_bandes_publiees=len(s["bandes"]), les_bandes_neuves=len(neuves), les_chunks_lus_ici=lus,
                les_tours_de_lecture=tour)
        if not lire:
            e.sauter("rejeu : les bandes publiées et celles données par --lectures ; --lire lit ce que la procédure demande")
    if r.arrete:
        r.ecrire(sortie)
        return r

    with r.etage("E6", "le certificat", "B4") as e:
        etats = {}
        for x in res["le_journal"]:
            etats[x["letat"]] = etats.get(x["letat"], 0) + 1
        e.constater("S", ctx["la_procedure"]["portee"], ecart_qui_evite=30)
        for x in res["le_journal"]:
            if x.get("la_fermeture") is not None:
                e.constater("L", x["la_fermeture"], boucle=x["les_coins"], largeur=x["la_largeur"], etat=x["letat"])
                if x.get("le_pic"):
                    e.constater("P", x["le_pic"]["le_cumul_en_voxels"], boucle=x["les_coins"],
                                a_la_coupe=x["le_pic"]["la_coupe"], demi=demi)
            v = (x.get("le_departage") or {}).get("le_verdict")
            if v and v.get("les_marges"):
                e.constater("M", v["les_marges"], la_ligne_qui_derive=v["la_ligne_qui_derive"],
                            la_plus_serree=v["la_plus_serree"])
        e.constater("K", res["la_couverture"]["la_part"], chunks=res["la_couverture"]["combien"],
                    sur=res["la_couverture"]["sur"])
        e.noter(le_rectangle=res["le_rectangle"], les_etats=etats, les_boucles_qui_tiennent=res["les_boucles_qui_tiennent"],
                les_bandes_a_lire=len(res["les_demandes"]), les_chunks_a_lire=res["ce_qui_reste_a_lire"],
                le_temps_de_lecture_estime_min=round(res["ce_qui_reste_a_lire"] / LE_DEBIT_MESURE / 60, 1),
                les_ailes_autour_dun_rectangle_non_juge=res["les_ailes_autour_dun_rectangle_non_juge"])
        if res["les_demandes"]:
            e.partiel(f"{len(res['les_demandes'])} bandes ({res['ce_qui_reste_a_lire']} chunks) restent à lire pour juger "
                      f"ce que la procédure trouve ; la couverture est celle de ce qui est jugé. "
                      f"`vesuve grand-prize --lire` les lit, environ "
                      f"{res['ce_qui_reste_a_lire'] / LE_DEBIT_MESURE / 60:.0f} min à 16 fils")
        if res["les_ailes_autour_dun_rectangle_non_juge"]:
            e.noter(lavertissement=("des ailes sont certifiées autour d'un rectangle qui n'est pas lui-même jugé : "
                                    "elles tiennent sur leur profil, mais le rectangle qui les relie n'est pas prouvé"))
    masque = res["le_masque"]

    with r.etage("E7", "le juge sans vérité terrain", "B3") as e:
        if juger <= 0:
            e.sauter("demandé avec --juger N : il lit N chunks certifiés sur le bucket")
        else:
            t = TableauDistant(f"{LE_BUCKET}/{ctx['le_volume']}", transport)
            lecteur = LecteurDeBandes(t, CacheDeDigests(Path(cache) / "digests", t.url), fils, journal, segment)
            ys, xs = np.nonzero(masque == cert.CERTIFIE)
            if not len(ys):
                e.sauter("aucun chunk n'est certifié")
            else:
                pris = np.random.default_rng(20260924).choice(len(ys), size=min(juger, len(ys)), replace=False)
                lecteur.precharger([(int(ys[i]), int(xs[i])) for i in pris])
                ecarts, reliefs = [], []
                for i in pris:
                    d = lecteur.digest(int(ys[i]), int(xs[i]))
                    if d.retenu:
                        p = d.profondeur
                        ecarts.append(abs(int(np.argmax(p)) - LA_COUCHE_TRACEE) * ctx["le_voxel_um"])
                        reliefs.append(float((p.max() - p.min()) / p.mean()))
                e.noter(les_chunks_juges=len(ecarts), lecart_median_du_pic_um=round(float(np.median(ecarts)), 2),
                        la_part_a_moins_dun_demi_feuillet=round(float(np.mean(np.array(ecarts) < demi * ctx["le_voxel_um"])), 4),
                        le_relief_median=round(float(np.median(reliefs)), 4),
                        la_regle=("`src/tracecheck/tracecheck.py:204` : le pic de matière de chaque chunk doit tomber sur "
                                  "la couche tracée ; un écart au-delà du demi-feuillet (36 voxels, 86,4 µm) dit que la "
                                  "surface a quitté sa feuille"))

    with r.etage("E8", "l'encre, la règle graduée", "B3") as e:
        if not encre:
            e.sauter("désactivé par --sans-encre")
        else:
            chemin = la_carte_dencre_publiee(ctx)
            try:
                carte = images.lire_une_image(distant.octets(chemin))
                sortie.mkdir(parents=True, exist_ok=True)
                vue = images.superposer(carte, masque)
                vue = images.dessiner_les_boucles(vue, res["le_journal"], carte.shape[0] / masque.shape[0], 6)
                vue.thumbnail((1600, 1600))  # la carte pleine est le produit publié ; la vue sert à lire
                vue.save(sortie / "encre_sous_le_masque.jpg", quality=88)
                e.noter(la_carte=chemin, sa_forme=list(carte.shape), limage="encre_sous_le_masque.jpg",
                        la_lecture=("la carte d'encre PUBLIÉE (modèle de l'équipe, 2,4 µm), sous le masque : l'encre "
                                    "est la règle graduée qui dit si le déroulé fait du sens, pas l'ouvrage"))
            except Indisponible as x:
                e.sauter(f"la carte d'encre n'a pas pu être obtenue : {x}")

    with r.etage("E9", "l'emballage") as e:
        sortie.mkdir(parents=True, exist_ok=True)
        tifffile.imwrite(sortie / "masque_par_chunk.tif", masque)
        images.dessiner_les_boucles(images.masque_en_couleurs(masque), res["le_journal"], 2, 1).save(
            sortie / "masque_par_chunk.png")
        (sortie / "certificat.json").write_text(json.dumps(
            {k: res[k] for k in ("le_rectangle", "le_journal", "les_boucles_qui_tiennent", "la_couverture",
                                 "ce_qui_reste_a_lire")}, ensure_ascii=False, indent=1))
        (sortie / "bandes_a_lire.json").write_text(json.dumps(res["les_demandes"], ensure_ascii=False, indent=1))
        produits = ["masque_par_chunk.tif", "masque_par_chunk.png", "certificat.json", "bandes_a_lire.json"]
        if surface:
            chemin = f"{ctx['lobjet']}/segments/{segment}/mesh/{segment}-on-20260411134726-2.4um.tifxyz"
            try:
                sf = tifxyz.lire(distant.dossier_tifxyz(chemin))
                echelle = float(sf.meta["scale"][0])
                grille = tifxyz.masque_de_chunks_vers_grille(masque, sf.forme, 128, echelle)
                certifie = (grille == cert.CERTIFIE) & sf.valide()
                tifxyz.ecrire(tifxyz.restreindre(sf, certifie), sortie / f"{segment}_certifie.tifxyz",
                              approbation=certifie.astype(np.uint8))
                produits.append(f"{segment}_certifie.tifxyz/ (x, y, z, meta.json, approval.tif)")
                e.noter(la_surface=chemin, sa_grille=list(sf.forme), les_sommets_certifies=int(certifie.sum()),
                        les_sommets_valides=int(sf.valide().sum()))
            except Indisponible as x:
                e.partiel(f"la surface n'a pas pu être obtenue : {x}")
        e.noter(les_produits=produits,
                ce_qui_nest_pas_produit=("`column_NN.tifxyz` : découper la surface en colonnes de texte demande que "
                                         "l'encre soit lisible colonne par colonne, et au régime des treize rouleaux "
                                         "le détecteur publié ne sépare pas la feuille du vide (`R1-F20`). Le livrable "
                                         "est la surface certifiée, entière, et son masque."))

    part = res["la_couverture"]["la_part"]
    r.exigence("un des treize rouleaux éligibles", "non atteinte" if not catalogue.est_eligible("grand-prize", ctx["lobjet"])
               else "atteinte", f"{ctx['lobjet']} : le référent de la méthode, hors de la liste")
    r.exigence("100 % du recto déroulé", "non atteinte",
               f"un segment publié : {res['la_couverture']['combien']} chunks certifiés sur {res['la_couverture']['sur']} "
               f"({part:.2%} de SON empreinte), un segment n'est pas un rouleau")
    r.exigence("pipeline automatique, au plus 8 h d'humain", "atteinte",
               "0 h : la procédure prend chaque décision sans main (`R4-F410`) ; la seule entrée est la présence")
    r.exigence("70 % des caractères lisibles par colonne", "non mesurée",
               "aucune lecture ; au régime du prix l'encre publiée est plate (`R1-F20`)")
    r.exigence("un maillage par colonne, `column_NN.tifxyz`", "non atteinte",
               "la surface certifiée est rendue entière, avec `approval.tif` ; pas de découpage en colonnes")
    r.exigence("image Docker", "atteinte", "`vesuve/Dockerfile`, qui lance ce pipeline depuis les données embarquées")
    r.exigence("graines fixées et rapportées", "atteinte",
               f"nul par blocs : graine {ctx['la_procedure']['graine']}, {ctx['la_procedure']['tirages']} tirages ; "
               f"juge : graine 20260924")
    r.exigence("intégré à VC3D", "non mesurée", "la surface et `approval.tif` suivent le contrat tifxyz que villa lit")
    r.ecrire(sortie)
    return r
