"""La feuille a-t-elle trois plis ? — d'où viennent les frontières en trop.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `181` a mesuré que les creux du rouleau sont espacés comme des PLIS et
non comme des interstices — vingt chunks sur vingt-sept — mais que leur espacement médian vaut
**23,5** couches pour un pli de **36**. Le rouleau porte donc plus de frontières qu'un empilement
régulier de deux plis par feuille n'en prédit, et `R4-P33` demande d'où elles viennent.

⭐⭐⭐⭐ ET LE CHIFFRE NOMME LUI-MÊME UNE HYPOTHÈSE CONCRÈTE. Une feuille de `P` plis porte une
frontière tous les `pas / P` micromètres, soit `pas / P / voxel` couches : **36** à deux plis,
**24** à trois, **18** à quatre. Vingt-trois et demi tombe entre trois et quatre, beaucoup plus près
de trois. `14` §1 décrit une feuille de DEUX plis ; si le rouleau en portait trois, l'écart mesuré
par `181` cesserait d'être un excès inexpliqué et deviendrait une propriété de la matière.

⚠⚠⚠ MAIS UNE MÉDIANE NE SUFFIT PAS, ET C'EST TOUTE LA DIFFICULTÉ. Un empilement RÉGULIER à trois
plis et un MÉLANGE de vraies frontières et de fissures peuvent rendre la même médiane : ce qui les
sépare est la FORME de la distribution — groupée autour d'une valeur, ou étalée. On mesure donc les
deux, et on les compare à deux matières construites dont la réponse est connue.

⚠⚠ LE MÉLANGE EST CONSTRUIT ET IL EST DIT : la fixture ne sait pas fabriquer une fissure, donc les
creux surnuméraires y sont CREUSÉS à des profondeurs tirées au hasard. Leur profondeur et leur
largeur ne sont pas choisies — elles sont relues de ce que `180` a mesuré sur le rouleau — et leur
NOMBRE est dérivé de l'écart entre ce qu'un empilement à deux plis prédit et ce que `181` a compté.

⚠ Tout le reste est appelé et non recopié : le lecteur séquentiel de `181`, le chemin du rouleau de
`176`, le recouvrement de `179`, le bruit de `180`.

Usage :
    uv run python src/nappe/la_feuille_a_t_elle_trois_plis.py --verifier
    uv run python src/nappe/la_feuille_a_t_elle_trois_plis.py \\
        --json docs/mesures/la_feuille_a_t_elle_trois_plis.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from de_quoi_une_frontiere_est_elle_faite import (CE_QUE_LA_FIXTURE_A_RENDU,  # noqa: E402
                                                  CE_QUE_LE_ROULEAU_A_RENDU, COUCHES,
                                                  DECALAGES, _relire, plusieurs_creux)
from la_coherence_creuse_t_elle_a_la_frontiere import CONTRASTE_DE_LA_FIXTURE  # noqa: E402
from la_profondeur_tourne_t_elle_ou_bascule_t_elle import PERMUTATIONS  # noqa: E402
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             SEGMENTS, la_courbe_dun_chunk, les_chunks,
                                             les_volumes)
from quelle_fenetre_lit_une_bascule import courbe_de_la_fixture  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LESPACEMENT_A_RENDU = MESURES / "de_quoi_une_frontiere_est_elle_faite.json"
GRAINE = 20260922


def lechelle_des_plis(voxel_um: float, pas_um: float, espacement: float) -> list[int]:
    """Les nombres de plis dont l'espacement ENCADRE celui qu'on a mesuré.

    ⚠⚠ DÉRIVÉE, PAS CHOISIE. Une feuille de `P` plis porte une frontière tous les `pas/P/voxel`
    couches, et cette suite décroît ; on garde les deux `P` qui encadrent l'espacement mesuré, plus
    le `P` de `14` §1 — DEUX — parce que c'est celui dont on se demande s'il est faux. Une échelle
    plus large ferait balayer des matières que la question ne pose pas.
    """
    def ecart(p: int) -> float:
        return float(pas_um) / float(p) / float(voxel_um)

    p = 2
    while ecart(p) > float(espacement) and p < 40:
        p += 1
    return sorted({2, max(2, p - 1), p})


def lespacement_dun_pli(p: int, voxel_um: float, pas_um: float) -> float:
    """L'espacement, en couches, d'une feuille de `p` plis."""
    return float(pas_um) / float(p) / float(voxel_um)


def les_creux_a_chercher(plis, couches: int, voxel_um: float, pas_um: float) -> int:
    """Combien de creux une fenêtre peut porter au pas le PLUS FIN de l'échelle — dérivé.

    ⚠⚠⚠ UN PLAFOND TROP BAS NE REND PAS MOINS DE CREUX, IL REND DE FAUX ESPACEMENTS, et la mesure
    l'a montré nu : à quatre plis la matière porte une frontière toutes les **18** couches, et un
    lecteur plafonné à trois creux en rendait un espacement de **53** — il ne voit que les trois plus
    profondes, qui ne sont pas voisines, donc il mesure des MULTIPLES du vrai pas. Le plafond se
    dérive donc du pas le plus fin que l'échelle contient, et non d'un nombre écrit à la main.

    ⚠ Un de plus que le compte exact, parce qu'une fenêtre décalée peut en attraper un de plus
    qu'une fenêtre alignée.
    """
    fin = min(lespacement_dun_pli(int(p), voxel_um, pas_um) for p in plis)
    return int(couches // fin) + 1


def les_surnumeraires(espacement_mesure: float, couches: int, voxel_um: float,
                      pas_um: float) -> int:
    """Combien de creux en trop un mélange doit porter — DÉRIVÉ DES ESPACEMENTS, pas des comptes.

    ⚠⚠⚠ UNE PREMIÈRE VERSION LE TIRAIT DE L'ÉCART ENTRE LE NOMBRE DE CREUX DU ROULEAU ET CELUI D'UN
    EMPILEMENT À DEUX PLIS. Or ces deux comptes sont PLAFONNÉS par le lecteur, donc leur différence
    l'est aussi : elle rendait UN seul creux en trop, ce qui ne fabrique pas un mélange — l'étalon
    censé représenter un mélange étalait alors moins qu'un empilement régulier, et le contrôle ne
    contrôlait rien.

    ⭐ L'écart entre deux ESPACEMENTS n'est pas plafonné : une fenêtre de `couches` couches porte
    `couches / espacement` frontières, et la différence entre ce que le rouleau montre et ce qu'un
    empilement à deux plis prédit est le nombre à ajouter.
    """
    a = float(couches) / max(1e-9, float(espacement_mesure))
    b = float(couches) / lespacement_dun_pli(2, voxel_um, pas_um)
    return max(1, int(round(a - b)))


def letalement(espacements) -> dict:
    """La forme de la distribution : sa médiane et son étalement RAPPORTÉ à elle.

    ⭐⭐⭐⭐ L'ÉTALEMENT EST RAPPORTÉ À LA MÉDIANE, DONC IL EST SANS UNITÉ ET SE COMPARE ENTRE
    MATIÈRES QUI N'ONT PAS LE MÊME ESPACEMENT. Un empilement régulier rend un étalement faible quel
    que soit son pas ; un mélange de vraies frontières et de fissures en rend un grand. C'est cette
    quantité-là qui sépare les deux, et aucun seuil n'y entre : elle est lue sur le rouleau et sur
    deux matières construites dont la réponse est connue.

    ⚠ L'écart absolu MÉDIAN et non l'écart-type : une seule fissure très éloignée ferait exploser un
    écart-type, et ce qu'on veut savoir est si la MASSE de la distribution est groupée.
    """
    v = [float(x) for x in espacements]
    if len(v) < 2:
        return {"mesures": len(v), "mediane": (round(v[0], 3) if v else None),
                "etalement": None, "etalement_relatif": None}
    med = float(statistics.median(v))
    eam = float(statistics.median([abs(x - med) for x in v]))
    return {"mesures": len(v), "mediane": round(med, 3), "etalement": round(eam, 3),
            "etalement_relatif": (round(eam / med, 4) if med > 0 else None)}


def _creux_dune_courbe(courbe, combien: int, permutations: int, graine: int) -> dict:
    lu = plusieurs_creux([x[1] for x in courbe], int(combien), permutations, graine)
    return lu if lu.get("decidable") else {"decidable": False, "espacements": [],
                                           "creux_retenus": 0}


def un_etalon_a_p_plis(p: int, fraction: float, bruit: float, voxel_um: float, pas_um: float,
                       combien: int, decalages: int = DECALAGES,
                       permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """La MÊME lecture sur une feuille de `p` plis.

    ⚠⚠ LE RECOUVREMENT EST LA MÊME FRACTION D'UN PLI À TOUS LES `p`, jamais la même longueur : deux
    matières dont les plis n'ont pas la même épaisseur ne se comparent qu'à interpénétration
    relative égale, et la fixture refuse de toute façon un recouvrement plus épais qu'un pli.
    """
    transition = float(fraction) * (float(pas_um) / float(p))
    espaces, creux = [], 0
    for k in range(int(decalages)):
        dec = float(pas_um) * k / float(decalages)
        courbe = courbe_de_la_fixture(COUCHES, dec, CONTRASTE_DE_LA_FIXTURE, int(p),
                                      voxel_um, pas_um, transition_um=transition,
                                      bruit=float(bruit))
        lu = _creux_dune_courbe(courbe, combien, permutations, graine)
        espaces += [int(x) for x in lu["espacements"]]
        creux += int(lu.get("creux_retenus", 0))
    return {"plis": int(p), "creux_cherches": int(combien), "espacement_construit": round(
        lespacement_dun_pli(p, voxel_um, pas_um), 3),
        "recouvrement_um": round(transition, 3), "bruit": float(bruit),
        "cellules": int(decalages), "creux_retenus": int(creux),
        "espacements": sorted(espaces), **letalement(espaces)}


def un_melange(fraction: float, bruit: float, voxel_um: float, pas_um: float,
               profondeur: float, largeur: int, surnumeraires: int, combien: int,
               decalages: int = DECALAGES, permutations: int = PERMUTATIONS,
               graine: int = GRAINE) -> dict:
    """Une feuille de DEUX plis, plus des creux surnuméraires posés au hasard — le mélange.

    ⚠⚠⚠ C'EST LA SEULE MATIÈRE CONSTRUITE DE CETTE TRANCHE, et elle est dite : la fixture ne sait
    pas fabriquer une fissure. Ce qui n'est PAS choisi est ce qui compte — la profondeur et la
    largeur des creux ajoutés sont relues de ce que `180` a mesuré sur le rouleau, et leur NOMBRE
    est dérivé de l'écart entre ce qu'un empilement à deux plis rend et ce que `181` a compté.

    ⚠ Les positions sont tirées uniformément parce que c'est exactement l'hypothèse qu'on met à
    l'épreuve : une fissure n'a pas de raison de tomber à un pas régulier.
    """
    transition = float(fraction) * (float(pas_um) / 2.0)
    espaces, creux = [], 0
    for k in range(int(decalages)):
        dec = float(pas_um) * k / float(decalages)
        courbe = courbe_de_la_fixture(COUCHES, dec, CONTRASTE_DE_LA_FIXTURE, 2,
                                      voxel_um, pas_um, transition_um=transition,
                                      bruit=float(bruit))
        c = [list(x) for x in courbe]
        r = np.random.default_rng(int(graine) + 7919 * k)
        socle = float(statistics.median([x[1] for x in c]))
        h = int(largeur) // 2
        for pos in r.integers(h + 1, COUCHES - h - 1, int(surnumeraires)):
            for j in range(int(pos) - h, int(pos) + h + 1):
                c[j][1] = socle * (1.0 - float(profondeur))
        lu = _creux_dune_courbe(c, combien, permutations, graine)
        espaces += [int(x) for x in lu["espacements"]]
        creux += int(lu.get("creux_retenus", 0))
    return {"quoi": "un mélange", "surnumeraires": int(surnumeraires),
            "recouvrement_um": round(transition, 3), "bruit": float(bruit),
            "cellules": int(decalages), "creux_retenus": int(creux),
            "espacements": sorted(espaces), **letalement(espaces)}


def un_segment(volume: dict, combien: int, cote: int = COTE_DU_TREILLIS,
               permutations: int = PERMUTATIONS, delai: float = DELAI,
               graine: int = GRAINE) -> dict:
    url = f"{BUCKET}/{volume['cle']}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": volume["segment"],
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    espaces, lus, creux, refus = [], 0, 0, {}
    for cy, cx in les_chunks(-(-rows // hy), -(-cols // hx), cote):
        courbe, pourquoi = la_courbe_dun_chunk(url, meta, cy, cx, delai)
        if courbe is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        lus += 1
        lu = _creux_dune_courbe(courbe, combien, permutations, graine)
        espaces += [int(x) for x in lu["espacements"]]
        creux += int(lu.get("creux_retenus", 0))
    return {"decidable": bool(lus), "segment": volume["segment"], "chunks_lus": int(lus),
            "refuses": refus, "creux_retenus": int(creux), "espacements": sorted(espaces),
            **letalement(espaces)}


def le_pli_qui_correspond(etalons: list[dict], mediane: float) -> int | None:
    """Le nombre de plis dont l'espacement CONSTRUIT est le plus proche de celui du rouleau.

    ⚠ Égalités tranchées par le plus petit nombre de plis, pour que deux exécutions rendent la même
    réponse. La comparaison porte sur l'espacement que la matière porte PAR CONSTRUCTION, pas sur
    celui que le lecteur en rend : le second est déjà une mesure, et comparer deux mesures ferait
    entrer deux fois le bruit du lecteur.
    """
    if mediane is None or not etalons:
        return None
    return int(min(etalons, key=lambda e: (abs(float(e["espacement_construit"])
                                               - float(mediane)), e["plis"]))["plis"])


def juger(segments: list[dict], etalons: list[dict], melange: dict, de_181: dict,
          voxel_um: float, pas_um: float) -> dict:
    """Trois plis, ou un mélange ? Et l'étalement tranche là où la médiane ne peut pas."""
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible"}
    espaces = [e for s in lus for e in s["espacements"]]
    forme = letalement(espaces)
    p = le_pli_qui_correspond(etalons, forme["mediane"])
    retenu = next((e for e in etalons if e["plis"] == p), None)
    deux = next((e for e in etalons if e["plis"] == 2), None)
    return {"decidable": True, "segments": len(lus),
            "chunks_lus": int(sum(s["chunks_lus"] for s in lus)),
            "creux_retenus": int(sum(s["creux_retenus"] for s in lus)),
            "espacements_mesures": forme["mesures"],
            "espacement_median_du_rouleau": forme["mediane"],
            "espacement_median_de_181": de_181.get("espacement_median_du_rouleau"),
            "etalement_du_rouleau": forme["etalement"],
            "etalement_relatif_du_rouleau": forme["etalement_relatif"],
            "les_plis_qui_correspondent": p,
            "espacement_construit_a_ce_pli": (retenu["espacement_construit"]
                                              if retenu else None),
            "espacement_lu_a_ce_pli": (retenu["mediane"] if retenu else None),
            "etalement_relatif_a_ce_pli": (retenu["etalement_relatif"] if retenu else None),
            "espacement_construit_a_deux_plis": (deux["espacement_construit"] if deux else None),
            "etalement_relatif_a_deux_plis": (deux["etalement_relatif"] if deux else None),
            "surnumeraires_du_melange": melange["surnumeraires"],
            "espacement_median_du_melange": melange["mediane"],
            "etalement_relatif_du_melange": melange["etalement_relatif"],
            # ⚠⚠ TROIS ENONCES. Le premier dit que le rouleau ne tient PAS a deux plis, sinon la
            # question ne se pose pas. Le second dit quel nombre de plis son espacement designe. Le
            # troisieme est celui qui tranche : un empilement REGULIER est groupe, un melange est
            # etale, et le rouleau se range du cote de l'un des deux.
            "il_ne_tient_pas_a_deux_plis": bool(
                p is not None and int(p) != 2),
            "son_etalement_est_celui_dun_empilement_regulier": bool(
                forme["etalement_relatif"] is not None and retenu is not None
                and melange["etalement_relatif"] is not None
                and retenu["etalement_relatif"] is not None
                and abs(forme["etalement_relatif"] - retenu["etalement_relatif"])
                < abs(forme["etalement_relatif"] - melange["etalement_relatif"])),
            "les_deux_formes_se_separent": bool(
                retenu is not None and melange["etalement_relatif"] is not None
                and retenu["etalement_relatif"] is not None
                and melange["etalement_relatif"] > retenu["etalement_relatif"])}


def mesurer(segments_n: int = SEGMENTS, cote: int = COTE_DU_TREILLIS,
            permutations: int = PERMUTATIONS, decalages: int = DECALAGES) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    de_179 = _relire(CE_QUE_LA_FIXTURE_A_RENDU, ("le_recouvrement_juste_suffisant_um",))
    de_180 = _relire(CE_QUE_LE_ROULEAU_A_RENDU,
                     ("le_bruit_apparie", "profondeur_mediane_du_rouleau",
                      "largeur_mediane_du_rouleau", "chunks_lus"))
    de_181 = _relire(CE_QUE_LESPACEMENT_A_RENDU,
                     ("espacement_median_du_rouleau", "creux_retenus", "chunks_lus"))
    if de_179 is None or de_180 is None or de_181 is None:
        return {"message": "les mesures de `179`, `180` et `181` donnent les réglages et l'échelle"}
    fraction = float(de_179["le_recouvrement_juste_suffisant_um"]) / (pas / 2.0)
    bruit = float(de_180["le_bruit_apparie"])
    plis = lechelle_des_plis(vx, pas, float(de_181["espacement_median_du_rouleau"]))
    cherches = les_creux_a_chercher(plis, COUCHES, vx, pas)
    volumes = les_volumes(combien=segments_n)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    segs = [un_segment(v, cherches, cote, permutations) for v in volumes]
    etalons = [un_etalon_a_p_plis(p, fraction, bruit, vx, pas, cherches, decalages, permutations)
               for p in plis]
    # ⚠⚠ LE NOMBRE DE CREUX SURNUMERAIRES EST DERIVE : c'est l'ecart entre ce que `181` a compte sur
    # le rouleau et ce qu'un empilement a DEUX plis rend, ramene a un chunk. Le choisir ferait du
    # melange une matiere reglee pour perdre ou pour gagner.
    # ⚠⚠ LE NOMBRE DE CREUX SURNUMERAIRES SE DERIVE DES ESPACEMENTS, PAS DES COMPTES. Une premiere
    # version le tirait de l'ecart entre le nombre de creux du rouleau et celui d'un empilement a
    # deux plis — or ces deux comptes sont PLAFONNES par le lecteur, donc leur difference l'est
    # aussi et elle rendait UN seul creux en trop, ce qui ne fabrique pas un melange. L'ecart entre
    # deux espacements, lui, n'est pas plafonne : une fenetre porte `couches / espacement`
    # frontieres.
    surnumeraires = les_surnumeraires(float(de_181["espacement_median_du_rouleau"]),
                                      COUCHES, vx, pas)
    melange = un_melange(fraction, bruit, vx, pas,
                         float(de_180["profondeur_mediane_du_rouleau"]),
                         int(de_180["largeur_mediane_du_rouleau"]), surnumeraires, cherches,
                         decalages, permutations)
    return {"cote_du_treillis": int(cote), "permutations": int(permutations),
            "decalages": int(decalages), "couches": int(COUCHES), "graine": int(GRAINE),
            "creux_cherches_par_chunk": int(cherches),
            "plis_balayes": plis, "fraction_de_recouvrement": round(fraction, 4),
            "bruit_apparie_de_180": bruit,
            "espacement_median_de_181": float(de_181["espacement_median_du_rouleau"]),
            "profondeur_de_180": float(de_180["profondeur_mediane_du_rouleau"]),
            "largeur_de_180": int(de_180["largeur_mediane_du_rouleau"]),
            "les_segments": segs, "les_etalons": etalons, "le_melange": melange,
            "le_verdict": juger(segs, etalons, melange, de_181, vx, pas)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v = r["le_verdict"]
    print("LA FEUILLE A-T-ELLE TROIS PLIS ?")
    print(f"  {r['creux_cherches_par_chunk']} creux cherchés par chunk · treillis {r['cote_du_treillis']}×"
          f"{r['cote_du_treillis']} · {r['permutations']} permutations · plis balayés "
          f"{r['plis_balayes']} · bruit {r['bruit_apparie_de_180']}")
    print()
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"  {s['segment']} — {s.get('raison')}")
            continue
        print(f"  {s['segment']} · {s['chunks_lus']} chunks · creux {s['creux_retenus']} · "
              f"espacement {s['mediane']} · étalement {s['etalement']} "
              f"({s['etalement_relatif']})")
    print()
    print("  LES ÉTALONS · une feuille de P plis, même fraction de recouvrement, même bruit")
    print(f"   {'plis':>5} {'construit':>10} {'lu':>8} {'mesures':>8} {'étalement':>10} "
          f"{'relatif':>9}")
    for e in r["les_etalons"]:
        marque = "★" if e["plis"] == v.get("les_plis_qui_correspondent") else " "
        print(f"   {e['plis']:>5} {e['espacement_construit']:>10} {str(e['mediane']):>8} "
              f"{e['mesures']:>8} {str(e['etalement']):>10} {str(e['etalement_relatif']):>9} "
              f"{marque}")
    m = r["le_melange"]
    print(f"   {'mélange':>5} {'—':>10} {str(m['mediane']):>8} {m['mesures']:>8} "
          f"{str(m['etalement']):>10} {str(m['etalement_relatif']):>9}   "
          f"({m['surnumeraires']} creux en trop)")
    print()
    print("  ★ LE VERDICT")
    for cle in ("chunks_lus", "creux_retenus", "espacements_mesures",
                "espacement_median_du_rouleau", "espacement_median_de_181",
                "etalement_du_rouleau", "etalement_relatif_du_rouleau",
                "les_plis_qui_correspondent", "espacement_construit_a_ce_pli",
                "espacement_lu_a_ce_pli", "etalement_relatif_a_ce_pli",
                "espacement_construit_a_deux_plis", "etalement_relatif_a_deux_plis",
                "surnumeraires_du_melange", "espacement_median_du_melange",
                "etalement_relatif_du_melange", "il_ne_tient_pas_a_deux_plis",
                "les_deux_formes_se_separent",
                "son_etalement_est_celui_dun_empilement_regulier"):
        print(f"     {cle:<48} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)

    # ⚠⚠ L'ECHELLE DES PLIS ENCADRE L'ESPACEMENT MESURE, et elle contient toujours DEUX — celui
    # dont `14` §1 parle et dont on se demande s'il est faux.
    for mesure in (23.5, 20.0, 30.0):
        ech = lechelle_des_plis(vx, pas, mesure)
        v(f"l'échelle contient deux plis (mesure {mesure})", 2 in ech, str(ech))
        v(f"et elle encadre l'espacement mesuré ({mesure})",
          min(lespacement_dun_pli(p, vx, pas) for p in ech) <= mesure
          <= max(lespacement_dun_pli(p, vx, pas) for p in ech), str(ech))
    v("un pli de plus resserre l'espacement",
      lespacement_dun_pli(3, vx, pas) < lespacement_dun_pli(2, vx, pas))

    # ⚠⚠⚠ LE PLAFOND SE DERIVE DU PAS LE PLUS FIN, et une premiere version l'ecrivait a trois : la
    # matiere a QUATRE plis porte une frontiere toutes les 18 couches et le lecteur en rendait 53,
    # parce qu'il ne voyait que les trois plus profondes, qui ne sont pas voisines.
    ech = [2, 3, 4]
    cherches = les_creux_a_chercher(ech, COUCHES, vx, pas)
    v("le plafond couvre le pas le plus fin de l'échelle",
      cherches > COUCHES / min(lespacement_dun_pli(p, vx, pas) for p in ech),
      f"{cherches} pour {COUCHES} couches et un pas de "
      f"{round(min(lespacement_dun_pli(p, vx, pas) for p in ech), 2)}")
    v("et il dépasse ce qu'un empilement à deux plis demande",
      cherches > COUCHES / lespacement_dun_pli(2, vx, pas), str(cherches))

    # ⭐⭐⭐⭐ L'ETALEMENT SEPARE UN EMPILEMENT REGULIER D'UN MELANGE, et la reponse est connue AVANT
    # la mesure : une suite d'espacements egaux etale zero, une suite tiree au hasard etale.
    regulier = letalement([36, 36, 36, 35, 37, 36])
    melange = letalement([5, 12, 36, 60, 8, 44])
    v("un empilement régulier étale peu", regulier["etalement_relatif"] < 0.1,
      str(regulier))
    v("un mélange étale beaucoup", melange["etalement_relatif"] > 0.5, str(melange))
    v("et l'étalement est rapporté à la médiane, donc sans unité",
      letalement([72, 72, 70, 74])["etalement_relatif"]
      == letalement([36, 36, 35, 37])["etalement_relatif"],
      f"{letalement([72, 72, 70, 74])} contre {letalement([36, 36, 35, 37])}")
    v("une seule mesure ne rend aucun étalement",
      letalement([36])["etalement_relatif"] is None, str(letalement([36])))

    # ⚠ L'ECART ABSOLU MEDIAN ET NON L'ECART-TYPE : une seule valeur tres eloignee ne doit pas
    # faire exploser la mesure, parce que ce qu'on veut savoir est si la MASSE est groupee.
    v("une seule valeur très éloignée ne fait pas exploser l'étalement",
      letalement([36, 36, 36, 36, 400])["etalement_relatif"] < 0.1,
      str(letalement([36, 36, 36, 36, 400])))

    # ⚠⚠⚠ ET LE NOMBRE DE CREUX SURNUMERAIRES EST EXERCE PAR SA MONOTONIE, parce qu'une sonde qui
    # le remplacait par UNE CONSTANTE passait au VERT : la batterie fabriquait son propre melange et
    # ne touchait jamais la derivation. Ce qu'une constante ne peut pas faire est CROITRE quand
    # l'espacement mesure se resserre.
    suites = [les_surnumeraires(x, COUCHES, vx, pas) for x in (30.0, 23.5, 18.0, 12.0)]
    v("les creux surnuméraires croissent quand l'espacement se resserre",
      all(a <= b for a, b in zip(suites, suites[1:])) and suites[0] < suites[-1], str(suites))
    v("et un espacement de deux plis n'en demande aucun en trop",
      les_surnumeraires(lespacement_dun_pli(2, vx, pas), COUCHES, vx, pas) == 1,
      str(les_surnumeraires(lespacement_dun_pli(2, vx, pas), COUCHES, vx, pas)))

    # ⚠ LE PLI RETENU EST LE PLUS PROCHE, ET UNE EGALITE VA AU PLUS PETIT.
    faux = [{"plis": 2, "espacement_construit": 36.0},
            {"plis": 3, "espacement_construit": 24.0},
            {"plis": 4, "espacement_construit": 18.0}]
    v("le pli retenu est le plus proche", le_pli_qui_correspond(faux, 23.5) == 3,
      str(le_pli_qui_correspond(faux, 23.5)))
    v("et une égalité va au plus petit nombre de plis",
      le_pli_qui_correspond([{"plis": 2, "espacement_construit": 30.0},
                             {"plis": 5, "espacement_construit": 10.0}], 20.0) == 2)

    # ⭐⭐⭐⭐ LE CHEMIN PHYSIQUE : chaque etalon doit RELIRE le pas qu'il porte. C'est ce controle
    # qui a montre que le plafond etait faux.
    de_179 = _relire(CE_QUE_LA_FIXTURE_A_RENDU, ("le_recouvrement_juste_suffisant_um",))
    de_180 = _relire(CE_QUE_LE_ROULEAU_A_RENDU, ("le_bruit_apparie",))
    v("les mesures de `179` et `180` donnent les réglages", de_179 and de_180)
    if de_179 and de_180:
        fraction = float(de_179["le_recouvrement_juste_suffisant_um"]) / (pas / 2.0)
        bruit = float(de_180["le_bruit_apparie"])
        for p in (2, 4):
            e = un_etalon_a_p_plis(p, fraction, bruit, vx, pas, cherches, 4, PERMUTATIONS)
            v(f"l'étalon à {p} plis relit le pas qu'il porte",
              e["mediane"] is not None
              and abs(float(e["mediane"]) - float(e["espacement_construit"])) <= 2.0,
              f"lu {e['mediane']} pour {e['espacement_construit']}")
            v(f"et il étale peu ({p} plis)",
              e["etalement_relatif"] is not None and e["etalement_relatif"] < 0.2,
              str(e["etalement_relatif"]))

    # ⭐⭐⭐⭐ LES ENONCES DU VERDICT TOMBENT CHACUN SUR L'ENTREE QUI LE VISE.
    def _seg(espaces):
        return {"decidable": True, "segment": "x", "chunks_lus": 9, "creux_retenus": 20,
                "espacements": list(espaces), **letalement(espaces)}

    def _et(p, construit, rel):
        return {"plis": p, "espacement_construit": construit, "mediane": construit,
                "mesures": 20, "etalement": rel * construit, "etalement_relatif": rel,
                "cellules": 12, "creux_retenus": 20}

    ets = [_et(2, 36.0, 0.05), _et(3, 24.0, 0.05), _et(4, 18.0, 0.05)]
    mel = {"quoi": "un mélange", "surnumeraires": 2, "mediane": 34.0, "mesures": 20,
           "etalement": 7.0, "etalement_relatif": 0.21, "cellules": 12, "creux_retenus": 20}
    d181 = {"espacement_median_du_rouleau": 23.5}
    regul = juger([_seg([24, 24, 25, 23, 24, 25])], ets, mel, d181, vx, pas)
    v("un rouleau régulier à trois plis ne tient pas à deux",
      regul["il_ne_tient_pas_a_deux_plis"], str(regul["les_plis_qui_correspondent"]))
    v("et son étalement est celui d'un empilement régulier",
      regul["son_etalement_est_celui_dun_empilement_regulier"],
      str(regul["etalement_relatif_du_rouleau"]))
    v("les deux formes construites se séparent", regul["les_deux_formes_se_separent"])
    etale = juger([_seg([5, 12, 36, 60, 8, 44])], ets, mel, d181, vx, pas)
    v("un rouleau étalé n'est pas un empilement régulier",
      not etale["son_etalement_est_celui_dun_empilement_regulier"],
      str(etale["etalement_relatif_du_rouleau"]))
    deux = juger([_seg([36, 36, 35, 37, 36, 36])], ets, mel, d181, vx, pas)
    v("un rouleau à deux plis tient à deux plis", not deux["il_ne_tient_pas_a_deux_plis"],
      str(deux["les_plis_qui_correspondent"]))
    plat = juger([_seg([24, 24, 25])], [_et(2, 36.0, 0.25), _et(3, 24.0, 0.25)],
                 {**mel, "etalement_relatif": 0.05}, d181, vx, pas)
    v("un mélange moins étalé qu'un empilement retire le contrôle",
      not plat["les_deux_formes_se_separent"])
    vide = juger([{"decidable": False, "segment": "x"}], ets, mel, d181, vx, pas)
    v("aucun segment lisible rend un verdict indécidable", not vide["decidable"])

    nom = "la_feuille_a_t_elle_trois_plis.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e in echecs:
            print(f"   ✗ {e}")
        return 1
    print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--cote", type=int, default=COTE_DU_TREILLIS)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(SEGMENTS, a.cote)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
