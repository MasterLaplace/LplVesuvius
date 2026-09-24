"""L'audit d'un segment publié, pour les Progress Prizes : où une trace existante a-t-elle changé de spire ?

Le jury dit ce qu'il paie : « detecting failure-cases of existing methods on real scroll data ». Le même
certificat que le Grand Prize, lu à l'envers : une boucle de consensus dont le profil FRANCHIT le demi-feuillet
dit que ses deux chemins n'arrivent plus sur la même spire, et la troisième ligne de `236` désigne la
ligne qui dérive. Sur le segment `20230702185753`, tracé et publié, c'est la colonne 260 (`R4-F401`).

⚠ Ce que l'audit ne dit pas, et il le dit : il ne départage pas une colonne mal lue d'une matière qui
s'écarte (`R4-F406`, `R4-F407`). Il désigne une région à regarder, il ne la condamne pas.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import tifffile

from vesuve import images
from vesuve.distant import Distant, Indisponible
from vesuve.rapport import Rapport
from vesuve.transport import Transport
from vesuve.treillis import certificat as cert, geometrie as geo
from vesuve.treillis.segment import certifier_le_segment, la_carte_dencre_publiee, les_lectures_en_plus

SUSPECT = 3


def les_cas_dechec(res: dict, demi: float) -> list[dict]:
    """Chaque boucle qui franchit : où son cumul passe le demi-feuillet, et quelle ligne dérive."""
    cas = []
    for e in res["le_journal"]:
        if e["letat"] != "franchit":
            continue
        prof = e.get("le_profil") or []
        au_dela = [p["la_coupe"] for p in prof if abs(p["le_cumul_en_voxels"]) >= demi]
        dp = e.get("le_departage") or {}
        v = dp.get("le_verdict") or {}
        cas.append({"la_boucle": e["les_coins"], "le_cote": e.get("le_cote"), "la_largeur": e["la_largeur"],
                    "la_fermeture_en_voxels": e.get("la_fermeture"), "le_pic": e.get("le_pic"),
                    "les_coupes_au_dela_du_demi_feuillet": au_dela, "le_departage": dp.get("letat"),
                    "la_troisieme_ligne": (dp.get("la_troisieme_ligne") or {}).get("la_ligne"),
                    "la_ligne_qui_derive": v.get("la_ligne_qui_derive"), "les_marges": v.get("les_marges")})
    return cas


def le_masque_daudit(res: dict, cas: list[dict]) -> np.ndarray:
    """Le masque du certificat, et en plus les chunks de la bande qui dérive, le long de sa boucle."""
    m = res["le_masque"].copy()
    for c in cas:
        x, k = c["la_ligne_qui_derive"], c["la_largeur"]
        if x is None:
            continue
        r0, r1, c0, c1 = c["la_boucle"]
        h = k // 2
        if c["le_cote"] in ("droite", "gauche"):
            zone = (slice(r0, r1 + 1), slice(max(0, x - h), x + h + 1))
        else:
            zone = (slice(max(0, x - h), x + h + 1), slice(c0, c1 + 1))
        sous = m[zone]
        sous[sous == cert.PRESENT] = SUSPECT
    return m


def lancer(segment: str = "20230702185753", sortie: Path = Path("sorties/progress"), cache: Path = Path("cache"),
           lectures=(), juger: int = 0, journal=None) -> Rapport:
    sortie = Path(sortie)
    r = Rapport("progress", {"segment": segment, "lectures_en_plus": [str(x) for x in lectures]}, journal)
    neuves = les_lectures_en_plus(lectures)
    with r.etage("P0", "le segment audité") as e:
        s, res = certifier_le_segment(segment, neuves)
        ctx = s["contexte"]
        e.noter(lobjet=ctx["lobjet"], le_segment=segment, le_volume=ctx["le_volume"],
                sa_nature="un segment publié, tracé par d'autres : l'audit juge une méthode existante")
    demi = float(ctx["la_procedure"]["demi"])

    with r.etage("P1", "le certificat, lu à l'envers", "B4") as e:
        cas = les_cas_dechec(res, demi)
        for c in cas:
            e.constater("P", (c["le_pic"] or {}).get("le_cumul_en_voxels"), boucle=c["la_boucle"],
                        a_la_coupe=(c["le_pic"] or {}).get("la_coupe"), demi=demi)
            if c["les_marges"]:
                e.constater("M", c["les_marges"], la_ligne_qui_derive=c["la_ligne_qui_derive"])
        e.noter(les_boucles_jugees=sum(1 for x in res["le_journal"] if x.get("la_fermeture") is not None),
                les_boucles_qui_franchissent=len(cas))

    with r.etage("P2", "les cas d'échec") as e:
        m = le_masque_daudit(res, cas)
        sortie.mkdir(parents=True, exist_ok=True)
        (sortie / "cas_dechec.json").write_text(json.dumps(cas, ensure_ascii=False, indent=1))
        tifffile.imwrite(sortie / "masque_daudit.tif", m)
        images.dessiner_les_boucles(images.masque_en_couleurs(m), [x for x in res["le_journal"]
                                                                   if x["letat"] in ("franchit", "dessous")], 2, 1
                                    ).save(sortie / "masque_daudit.png")
        phrases = []
        for c in cas:
            if c["la_ligne_qui_derive"] is not None:
                sens = "colonne" if c["le_cote"] in ("droite", "gauche") else "rangée"
                bornes = c["la_boucle"][:2] if sens == "colonne" else c["la_boucle"][2:]
                phrases.append(f"la {sens} {c['la_ligne_qui_derive']}, des lignes {bornes[0]} à {bornes[1]} : le cumul "
                               f"franchit le demi-feuillet aux coupes {c['les_coupes_au_dela_du_demi_feuillet']} "
                               f"(pic {c['le_pic']['le_cumul_en_voxels']} voxels à la coupe {c['le_pic']['la_coupe']})")
        e.noter(les_chunks_suspects=int((m == SUSPECT).sum()), les_cas=phrases,
                la_limite=("l'audit ne départage pas une colonne mal lue d'une matière qui s'écarte (`R4-F406`) : "
                           "il désigne où regarder"))
        if not cas:
            e.partiel("aucune boucle jugée ne franchit : rien n'est désigné sur ce qui est lu")

    with r.etage("P3", "la région suspecte, sur l'encre publiée", "B3") as e:
        try:
            carte = images.lire_une_image(Distant(cache, Transport(journal=journal)).octets(la_carte_dencre_publiee(ctx)))
            vue = images.superposer(carte, m, alpha=0.5)
            vue = images.dessiner_les_boucles(vue, [x for x in res["le_journal"] if x["letat"] == "franchit"],
                                              carte.shape[0] / m.shape[0], 6)
            vue.thumbnail((1600, 1600))
            vue.save(sortie / "encre_et_region_suspecte.jpg", quality=88)
            e.noter(limage="encre_et_region_suspecte.jpg")
        except Indisponible as x:
            e.sauter(f"la carte d'encre n'a pas pu être obtenue : {x}")

    r.exigence("détecter un cas d'échec d'une méthode existante sur de vraies données",
               "atteinte" if cas else "non atteinte",
               "; ".join(e for e in r.donnees["les_etages"][2]["sorties"].get("les_cas", [])) or "aucun cas désigné")
    r.exigence("reproductible et documenté", "atteinte", "rejeu depuis les données embarquées, sans réseau ni graine libre")
    r.exigence("borner ce qu'on affirme", "atteinte", "une région à regarder, pas une condamnation (`R4-F406`)")
    r.ecrire(sortie)
    return r
