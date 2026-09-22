"""La piste de `191` tient-elle sur des chunks qu'elle n'a jamais vus ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P40` QUI LE NOMME. `191` a cherché ce qui distingue les
chunks où une surface tient sa feuille, parmi **19** observables déclarés, et n'a rien établi : son
meilleur atteint **0,3889** quand le plancher de détection vaut **0,4286**. Mais elle a NOMMÉ une
piste — le plafond lu dans la matière, aire **0,8889** — et l'a écrite dans le registre.

⭐⭐⭐⭐ ET C'EST LA DIFFÉRENCE ENTRE CHERCHER ET CONFIRMER, QUE CETTE CHAÎNE N'AVAIT JAMAIS FAITE.
`191` CHERCHAIT : elle avait le droit de regarder dix-neuf colonnes, donc elle a payé dix-neuf. `192`
ne cherche plus : **un seul observable, fixé et publié avant de voir la donnée**, donc il paie UN.
Confondre les deux coûte des deux côtés — payer dix-neuf pour une hypothèse unique interdit de jamais
conclure, et n'en payer qu'un après avoir regardé dix-neuf confirme n'importe quoi.

⚠⚠⚠ ET LA CONFIRMATION SE FAIT SUR DES CHUNKS NEUFS, JAMAIS SUR CEUX QUI ONT SERVI À CHOISIR. La
piste a été choisie sur les trois premiers segments ; ce fichier étiquette les trois SUIVANTS, que
ni `190` ni `191` n'ont lus. Rejouer le test sur la même matière ne mesurerait que le choix qu'on y
a fait.

⚠⚠ ET LE SENS EST DÉCLARÉ, DONC LE TEST EST UNILATÉRAL. C'est légitime ici et nulle part ailleurs :
`191` a **publié** la direction — aire **au-dessus** d'une demie, donc un plafond PLUS GRAND là où la
marche tient — et cette direction est dans le registre, commitée, avant que ces chunks-ci n'existent
pour nous. Un test unilatéral dans une direction choisie après coup serait une tricherie ; dans une
direction publiée, c'est l'information qu'on a déjà.

⚠ Rien de `190` n'est modifié : l'étiquetage des segments neufs passe par son `un_segment`, inchangé,
et les mesures publiées ne sont pas touchées.

Usage :
    uv run python src/nappe/la_piste_tient_elle_sur_des_chunks_neufs.py --verifier
    uv run python src/nappe/la_piste_tient_elle_sur_des_chunks_neufs.py \\
        --json docs/mesures/la_piste_tient_elle_sur_des_chunks_neufs.json
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

from jusquou_suit_on_une_fibre import DEPARTS_PAR_COUCHE  # noqa: E402
from la_ou_le_rouleau_se_laisse_suivre import (LETIQUETTE, _colonne,  # noqa: E402
                                               laire_sous_la_courbe)
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, PERMUTATIONS,  # noqa: E402
                                             SEGMENTS, les_volumes)
from suit_on_plus_loin_quand_le_voxel_est_plus_fin import le_plafond  # noqa: E402
from une_surface_qui_choisit_sa_couche import un_segment  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_RECHERCHE_A_RENDU = MESURES / "la_ou_le_rouleau_se_laisse_suivre.json"
GRAINE = 20261002

# ⚠⚠⚠ L'OBSERVABLE EST DECLARE ICI, SEUL, ET IL EST RELU DE `191` — jamais retape et jamais choisi.
# C'est la clef que `191` a nommee comme sa meilleure piste, et le fichier REFUSE de tourner si la
# mesure de `191` en nomme une autre : une confirmation qui ne confirmerait pas l'hypothese publiee
# n'en serait pas une.
LA_CLEF_DECLAREE = "plafond_du_ruban"
# ⚠⚠ LE SENS EST DECLARE : `191` publie une aire AU-DESSUS d'une demie, donc un plafond PLUS GRAND
# la ou la marche tient. Le test est donc unilateral dans ce sens-la, et dans aucun autre.
LE_SENS_DECLARE = 1
# ⚠⚠⚠ LES SEGMENTS DEJA VUS SONT CEUX DE `190`, ET LES NEUFS VIENNENT APRES EUX DANS L'ORDRE DU
# DEPOT. Aucun choix : on saute ce qui a servi a choisir la piste et on prend la suite.
SEGMENTS_DEJA_VUS = SEGMENTS
# ⚠⚠⚠ LE NOMBRE DE SEGMENTS NEUFS N'EST PAS CHOISI : il est celui qu'il faut pour que l'ETALON VOIE.
# Un premier essai a pris trois segments, rendu vingt-trois chunks dont TROIS seulement retiennent,
# et son etalon est passe au ROUGE — une colonne portant litteralement l'etiquette n'y survivait pas
# a la permutation. La campagne se dimensionne donc sur l'etalon, qui ne depend QUE des etiquettes
# et jamais de l'observable teste : arreter sur lui ne peut pas favoriser l'hypothese.
REPLICATS_DE_LETALON = 25
PLAFOND_DE_SEGMENTS = 24


def la_piste_publiee(chemin: Path = CE_QUE_LA_RECHERCHE_A_RENDU) -> dict:
    """La piste que `191` a nommée — sa clef, son aire, sa séparation et le plancher qu'elle avait.

    ⭐ C'EST L'HYPOTHÈSE, ET ELLE EST RELUE PLUTÔT QUE RETAPÉE. Si `191` avait nommé une autre clef,
    ce fichier n'aurait rien à confirmer : la confirmation porte sur ce qui a été publié, pas sur ce
    qu'on aurait aimé publier.
    """
    if not chemin.is_file():
        return {}
    d = json.loads(chemin.read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    m = v.get("le_meilleur") or {}
    return {"clef": m.get("cle"), "nom": m.get("nom"), "aire": m.get("aire"),
            "separation": m.get("separation"),
            "le_plancher_de_la_recherche": v.get("le_plancher_de_detection"),
            "observables_de_la_recherche": v.get("observables_declares"),
            "chunks_de_la_recherche": v.get("chunks_etiquetes")}


def les_volumes_neufs(deja: int = SEGMENTS_DEJA_VUS,
                      plafond: int = PLAFOND_DE_SEGMENTS) -> list[dict]:
    """Les segments que `190` n'a PAS lus — les suivants dans l'ordre que le dépôt recense.

    ⚠⚠ AUCUN CHOIX : on saute exactement ce qui a servi à nommer la piste et on prend la suite. Un
    choix parmi les segments neufs — les plus texturés, les plus grands — ferait confirmer le choix.
    """
    tous = les_volumes(combien=int(deja) + int(plafond))
    return tous[int(deja):]


def letalon_voit_il(n: int, k: int, replicats: int = REPLICATS_DE_LETALON,
                    tirages: int = PERMUTATIONS, graine: int = GRAINE) -> float:
    """À quelle fréquence l'instrument retrouve une colonne qui PORTE l'étiquette, à ce compte-là.

    ⭐⭐⭐⭐ C'EST L'INSTRUMENT QUI DIT SI L'INSTRUMENT PEUT VOIR, ET IL NE DÉPEND QUE DES ÉTIQUETTES.
    Avec trois chunks qui retiennent sur vingt-trois, une colonne portant littéralement l'étiquette
    ne survit à la permutation que **56 %** du temps : le test est alors aveugle par construction, et
    un silence ne voudrait rien dire. Cette fonction rend cette fréquence-là, et c'est elle qui
    dimensionne la campagne.

    ⚠⚠ Elle ne regarde JAMAIS l'observable testé — seulement `n` et `k`. C'est ce qui rend légitime
    d'arrêter la collecte sur elle : une règle d'arrêt qui ne peut pas connaître l'hypothèse ne peut
    pas la favoriser.

    ⚠ La colonne porteuse est BRUITÉE, comme dans `191` : une colonne qui SERAIT l'étiquette rendrait
    un écart parfait que nul observable réel n'atteint, donc l'étalon serait plus facile qu'il ne
    doit l'être.
    """
    if int(k) <= 0 or int(k) >= int(n):
        return 0.0
    vus = 0
    for t in range(int(replicats)):
        r = np.random.default_rng(int(graine) + 977 * (t + 1))
        e = [True] * int(k) + [False] * (int(n) - int(k))
        porteuse = [(1.0 if x else 0.0) + float(val)
                    for x, val in zip(e, r.normal(0.0, 0.6, int(n)))]
        j = juger_un_observable(porteuse, e, tirages, LE_SENS_DECLARE,
                                int(graine) + 977 * (t + 1))
        vus += int(bool(j.get("la_piste_tient")))
    return round(vus / float(replicats), 4)


def assez_de_chunks(n: int, k: int, replicats: int = REPLICATS_DE_LETALON,
                    tirages: int = PERMUTATIONS, graine: int = GRAINE) -> bool:
    """La règle d'arrêt : l'étalon doit voir sa colonne porteuse à TOUS les réplicats.

    ⚠⚠⚠ À TOUS, ET NON « LA PLUPART DU TEMPS ». Un instrument qui voit neuf fois sur dix rend un
    silence dont un dixième est du bruit, et c'est précisément le silence qu'on s'apprête à publier.
    """
    return letalon_voit_il(n, k, replicats, tirages, graine) >= 1.0


def etiqueter(volumes, combien: int = DEPARTS_PAR_COUCHE, cote: int = COTE_DU_TREILLIS,
              replicats: int = REPLICATS_DE_LETALON, tirages: int = PERMUTATIONS) -> dict:
    """L'étiquetage de `190`, rejoué tel quel sur des segments neufs.

    ⚠⚠⚠ RIEN DE `190` N'EST MODIFIÉ NI REJOUÉ DIFFÉREMMENT : c'est son `un_segment`, avec ses
    départs, son pas forcé, son plancher par couche, ses dix-neuf tirages et sa graine. Une seconde
    écriture de la marche serait une seconde définition de l'étiquette, libre de diverger — et c'est
    l'étiquette qui est comparée d'un jeu de chunks à l'autre.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    plafond = le_plafond(float(C.VOXEL_FIN_UM), float(C.PAS_UM))
    segs, lignes, montee = [], [], []
    # ⚠⚠⚠ ON COLLECTE JUSQU'A CE QUE L'ETALON VOIE, SEGMENT PAR SEGMENT, et on s'arrete la. La
    # regle ne regarde que les etiquettes, donc elle ne peut pas favoriser l'hypothese ; et sans
    # elle, le compte serait choisi, ce qui reviendrait a choisir ce que l'instrument peut voir.
    for v in volumes:
        s_ = un_segment(v, combien, plafond, cote)
        segs.append(s_)
        for c in (s_.get("chunks") or []):
            if c.get(LETIQUETTE) is None or c.get(LA_CLEF_DECLAREE) is None:
                continue
            lignes.append({"segment": s_["segment"], "chunk": c["chunk"],
                           "etiquette": bool(c[LETIQUETTE]),
                           "valeur": float(c[LA_CLEF_DECLAREE])})
        n, k = len(lignes), int(sum(1 for x in lignes if x["etiquette"]))
        # ⭐⭐⭐⭐ LA MONTEE DU COMPTE EST ENREGISTREE, SEGMENT PAR SEGMENT, et c'est elle qui rend
        # la regle d'arret VERIFIABLE au lieu d'affirmee : on y lit a quel compte l'instrument etait
        # encore aveugle et a partir de quel compte il voit.
        montee.append({"segments": len(segs), "chunks": n, "qui_retiennent": k,
                       "part_vue_par_letalon": letalon_voit_il(n, k, replicats, tirages)})
        if assez_de_chunks(n, k, replicats, tirages):
            break
    n, k = len(lignes), int(sum(1 for x in lignes if x["etiquette"]))
    return {"decidable": bool(lignes), "segments": [s_.get("segment") for s_ in segs],
            "la_montee_du_compte": montee,
            "segments_lus": len(segs),
            "refuses": [s_.get("refuses") for s_ in segs],
            "chunks_etiquetes": n, "chunks_qui_retiennent": k,
            "letalon_voit_a_ce_compte": letalon_voit_il(n, k, replicats, tirages),
            "le_compte_suffit": bool(assez_de_chunks(n, k, replicats, tirages)),
            "lignes": lignes}


def lecart_signe(valeurs, etiquettes, sens: int = LE_SENS_DECLARE) -> float | None:
    """L'écart à l'indifférence, DANS LE SENS DÉCLARÉ — jamais en valeur absolue.

    ⚠⚠⚠ C'EST CE QUI DISTINGUE UNE CONFIRMATION D'UNE RECHERCHE. `191` prenait la valeur absolue
    parce qu'elle ne savait pas dans quel sens un observable devait séparer ; ici le sens est publié,
    donc une séparation dans l'AUTRE sens est une réfutation et non un succès. Prendre la valeur
    absolue ferait compter un renversement complet comme une confirmation.
    """
    a = laire_sous_la_courbe(valeurs, etiquettes)
    return None if a is None else round(float(sens) * (float(a) - 0.5), 4)


def contre_le_melange(valeurs, etiquettes, tirages: int = PERMUTATIONS,
                      sens: int = LE_SENS_DECLARE, graine: int = GRAINE) -> dict:
    """Le nul d'UN SEUL observable : la même étiquette, mélangée sur les mêmes chunks.

    ⭐⭐⭐⭐ ET C'EST ICI QUE LE PRIX CHANGE. `191` reprenait le maximum sur DIX-NEUF colonnes à chaque
    tirage, parce qu'elle avait le droit d'en regarder dix-neuf. Ce fichier n'en regarde qu'UNE,
    fixée avant de voir la donnée, donc son plancher est la permutation de cette colonne-là — et il
    est bien plus bas. C'est toute la différence entre chercher et confirmer.
    """
    r = np.random.default_rng(int(graine))
    e = np.asarray(etiquettes, dtype=bool)
    ecarts = []
    for _ in range(int(tirages)):
        x = lecart_signe(valeurs, list(r.permutation(e)), sens)
        if x is not None:
            ecarts.append(float(x))
    if not ecarts:
        return {"decidable": False, "raison": "aucun mélange lisible"}
    return {"decidable": True, "tirages": int(tirages),
            "le_plus_grand_ecart": round(max(ecarts), 4),
            "les_ecarts": [round(x, 4) for x in ecarts]}


def juger_un_observable(valeurs, etiquettes, tirages: int = PERMUTATIONS,
                        sens: int = LE_SENS_DECLARE, graine: int = GRAINE) -> dict:
    """L'écart observé contre celui des mélanges — la règle, écrite une seule fois."""
    ecart = lecart_signe(valeurs, etiquettes, sens)
    if ecart is None:
        return {"decidable": False, "raison": "un des deux camps est vide"}
    nul = contre_le_melange(valeurs, etiquettes, tirages, sens, graine)
    if not nul.get("decidable"):
        return {"decidable": False, "raison": nul.get("raison")}
    return {"decidable": True,
            "laire": laire_sous_la_courbe(valeurs, etiquettes),
            "lecart_dans_le_sens_declare": ecart,
            "le_nul": nul, "le_plancher_de_detection": nul["le_plus_grand_ecart"],
            "laire_a_depasser": round(0.5 + float(nul["le_plus_grand_ecart"]), 4),
            # ⭐⭐⭐⭐ LA REGLE : l'ecart observe, DANS LE SENS DECLARE, doit depasser celui de TOUS
            # les melanges de l'etiquette sur les memes chunks.
            "la_piste_tient": bool(float(ecart) > float(nul["le_plus_grand_ecart"]))}


def sur_letalon(etiquettes, tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Deux colonnes dont la réponse est CONNUE, sur les MÊMES chunks et la MÊME étiquette.

    ⭐⭐⭐⭐ LA FACE POSITIVE PORTE L'ÉTIQUETTE, BRUITÉE, DANS LE SENS DÉCLARÉ : l'instrument DOIT la
    tenir, sinon son silence sur le rouleau ne voudrait rien dire. ⭐⭐⭐⭐ LA FACE NÉGATIVE est du
    bruit pur : il ne DOIT rien y tenir.

    ⚠⚠ ET UNE TROISIÈME FACE, QUE `191` N'AVAIT PAS : une colonne qui porte l'étiquette À L'ENVERS.
    Le test étant unilatéral, elle DOIT échouer — un test qui la tiendrait ne serait pas unilatéral,
    il prendrait la valeur absolue sans le dire, et la direction publiée ne servirait à rien.
    """
    n = len(etiquettes)
    r = np.random.default_rng(int(graine) + 7)
    porteuse = [(1.0 if x else 0.0) + float(v) for x, v in zip(etiquettes, r.normal(0.0, 0.6, n))]
    envers = [-x for x in porteuse]
    bruit = list(r.normal(0.0, 1.0, n))
    faces = {
        "elle_porte_letiquette": (porteuse, True),
        "elle_la_porte_a_lenvers": (envers, False),
        "elle_nest_que_du_bruit": (bruit, False),
    }
    lu = {nom: {**juger_un_observable(v, etiquettes, tirages, LE_SENS_DECLARE, graine),
                "attendu": att}
          for nom, (v, att) in faces.items()}
    return {**lu,
            "letalon_separe_les_trois": bool(
                all(bool(x.get("la_piste_tient")) == bool(x["attendu"]) for x in lu.values()))}


def mesurer(deja: int = SEGMENTS_DEJA_VUS, combien: int = DEPARTS_PAR_COUCHE,
            cote: int = COTE_DU_TREILLIS, tirages: int = PERMUTATIONS,
            replicats: int = REPLICATS_DE_LETALON) -> dict:
    piste = la_piste_publiee()
    if not piste.get("clef"):
        return {"message": "la piste de `191` n'est pas lisible ; relancer `191` d'abord"}
    # ⚠⚠⚠ LA CONFIRMATION PORTE SUR CE QUI A ETE PUBLIE, ET SUR RIEN D'AUTRE. Si `191` nommait une
    # autre clef, ce fichier n'aurait rien a confirmer et le dire est plus utile que de tourner.
    if str(piste["clef"]) != LA_CLEF_DECLAREE:
        return {"message": f"`191` nomme « {piste['clef']} » et non « {LA_CLEF_DECLAREE} » : "
                           "l'hypothèse déclarée ici ne serait pas celle qui a été publiée"}
    if float(piste.get("aire") or 0.0) <= 0.5 and LE_SENS_DECLARE > 0:
        return {"message": "`191` publie une aire sous une demie : le sens déclaré ici serait faux"}
    volumes = les_volumes_neufs(deja)
    if not volumes:
        return {"message": "le dépôt ne recense pas assez de segments pour en offrir des neufs"}
    marque = etiqueter(volumes, combien, cote, replicats, tirages)
    if not marque.get("decidable"):
        return {"message": "aucun chunk neuf n'a pu être étiqueté"}
    valeurs = [x["valeur"] for x in marque["lignes"]]
    etiquettes = [x["etiquette"] for x in marque["lignes"]]
    verdict = juger_un_observable(valeurs, etiquettes, tirages, LE_SENS_DECLARE, GRAINE)
    etalon = sur_letalon(etiquettes, tirages, GRAINE)
    return {"graine": int(GRAINE), "tirages": int(tirages),
            "replicats_de_letalon": int(replicats),
            "la_clef_declaree": LA_CLEF_DECLAREE, "le_sens_declare": int(LE_SENS_DECLARE),
            "segments_deja_vus": int(deja),
            "segments_neufs": int(marque.get("segments_lus") or 0),
            "la_piste_de_191": piste, "letiquetage": {k: v for k, v in marque.items()
                                                      if k != "lignes"},
            "les_chunks": marque["lignes"], "letalon": etalon,
            "la_montee_du_compte": marque.get("la_montee_du_compte") or [],
            "le_verdict": {**verdict,
                           "chunks_neufs": marque["chunks_etiquetes"],
                           "chunks_neufs_qui_retiennent": marque["chunks_qui_retiennent"],
                           "letalon_voit_a_ce_compte": marque.get("letalon_voit_a_ce_compte"),
                           "le_premier_compte": ((marque.get("la_montee_du_compte") or [{}])[0]),
                           "le_compte_suffit": bool(marque.get("le_compte_suffit")),
                           "laire_de_la_recherche": piste.get("aire"),
                           "le_plancher_de_la_recherche": piste.get("le_plancher_de_la_recherche"),
                           "observables_de_la_recherche": piste.get("observables_de_la_recherche"),
                           "chunks_de_la_recherche": piste.get("chunks_de_la_recherche"),
                           "letalon_separe_les_trois": bool(
                               etalon.get("letalon_separe_les_trois"))}}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, e, p = r["le_verdict"], r["letalon"], r["la_piste_de_191"]
    print("LA PISTE DE `191` TIENT-ELLE SUR DES CHUNKS QU'ELLE N'A JAMAIS VUS ?")
    print(f"  l'hypothèse, relue de `191` : « {p['nom']} », aire {p['aire']}, sens "
          f"{'+' if r['le_sens_declare'] > 0 else '-'}")
    print(f"  {r['segments_neufs']} segments neufs après les {r['segments_deja_vus']} déjà vus · "
          f"{v['chunks_neufs']} chunks dont {v['chunks_neufs_qui_retiennent']} retiennent · "
          f"UN seul observable, donc {r['tirages']} mélanges le paient")
    print()
    print("  L'ÉTALON — mêmes chunks, même étiquette, trois colonnes connues")
    for nom in ("elle_porte_letiquette", "elle_la_porte_a_lenvers", "elle_nest_que_du_bruit"):
        x = e.get(nom) or {}
        if not x.get("decidable"):
            print(f"     {nom:<26} — {x.get('raison')}")
            continue
        ok = bool(x.get("la_piste_tient")) == bool(x.get("attendu"))
        print(f"     {nom:<26} attendu {str(x['attendu']):<5} · tient "
              f"{str(x['la_piste_tient']):<5} · écart {x['lecart_dans_le_sens_declare']} contre "
              f"{x['le_plancher_de_detection']} · {'★' if ok else '✗'}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("chunks_neufs", "chunks_neufs_qui_retiennent", "laire",
                "lecart_dans_le_sens_declare", "le_plancher_de_detection", "laire_a_depasser",
                "laire_de_la_recherche", "le_plancher_de_la_recherche",
                "observables_de_la_recherche", "chunks_de_la_recherche",
                "letalon_separe_les_trois", "la_piste_tient"):
        print(f"     {cle:<36} {v.get(cle)}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⚠⚠⚠ L'HYPOTHESE EST RELUE DE `191`, JAMAIS RETAPEE.
    p = la_piste_publiee()
    v("la piste de `191` est relue", bool(p.get("clef")), str(p))
    v("★★★ et c'est bien la clef DÉCLARÉE ici", p.get("clef") == LA_CLEF_DECLAREE,
      f"{p.get('clef')} contre {LA_CLEF_DECLAREE}")
    v("★★ et son aire est au-dessus d'une demie, comme le sens déclaré le suppose",
      p.get("aire") is not None and float(p["aire"]) > 0.5 and LE_SENS_DECLARE > 0,
      str(p.get("aire")))
    v("elle est absente quand la mesure l'est",
      la_piste_publiee(Path("/n/existe/pas.json")) == {})

    # ⚠⚠ LES SEGMENTS NEUFS VIENNENT APRES LES DEJA VUS, SANS AUCUN RECOUVREMENT.
    deja = [x["segment"] for x in les_volumes(combien=SEGMENTS_DEJA_VUS)]
    neufs = [x["segment"] for x in les_volumes_neufs()]
    v("★★★ les segments neufs ne recouvrent PAS ceux qui ont servi à choisir la piste",
      not (set(deja) & set(neufs)), f"{deja} contre {neufs}")
    v("le dépôt en offre plus qu'assez", len(neufs) >= 6, str(len(neufs)))
    v("aucun segment neuf n'est vide", all(bool(s) for s in neufs), str(neufs))

    # ⭐⭐⭐⭐ L'ETALON DIT SI L'INSTRUMENT PEUT VOIR, ET C'EST CE QUI DIMENSIONNE LA CAMPAGNE. Un
    # premier essai a rendu vingt-trois chunks dont TROIS retiennent, et une colonne portant
    # litteralement l'etiquette n'y survivait pas — le test etait aveugle par construction.
    petit_ = letalon_voit_il(23, 3, 8)
    grand_ = letalon_voit_il(69, 20, 8)
    v("★★★★ à trois chunks qui retiennent sur vingt-trois, l'étalon est AVEUGLE",
      float(petit_) < 1.0, f"il voit {petit_} du temps")
    v("★★★★ et il voit à tous les réplicats quand le compte monte", float(grand_) >= 1.0,
      f"il voit {grand_} du temps")
    v("★★★ la règle d'arrêt exige TOUS les réplicats, pas la plupart",
      not assez_de_chunks(23, 3, 8) and assez_de_chunks(69, 20, 8),
      f"{petit_} contre {grand_}")
    v("★★ et elle ne regarde QUE les étiquettes",
      "valeurs" not in assez_de_chunks.__code__.co_varnames
      and set(assez_de_chunks.__code__.co_varnames[:2]) == {"n", "k"},
      str(assez_de_chunks.__code__.co_varnames[:4]))
    # ⭐⭐⭐ LA MONTEE DU COMPTE EST RELUE DE LA MESURE PUBLIEE, et c'est ce qui rend la regle
    # d'arret VERIFIABLE : on doit y lire que l'instrument etait aveugle avant, et qu'il ne s'est
    # arrete qu'une fois qu'il voit a TOUS les replicats.
    mo = []
    f_ = MESURES / "la_piste_tient_elle_sur_des_chunks_neufs.json"
    if f_.is_file():
        mo = (json.loads(f_.read_text(encoding="utf-8")).get("la_montee_du_compte") or [])
    v("★★ la montée du compte est publiée", bool(mo), str(len(mo)))
    v("★★ et le compte y monte", all(a_["chunks"] < b_["chunks"] for a_, b_ in zip(mo, mo[1:])),
      str([x.get("chunks") for x in mo]))
    v("★★★ la collecte ne s'arrête QU'UNE FOIS que l'étalon voit à tous les réplicats",
      bool(mo) and float(mo[-1]["part_vue_par_letalon"]) >= 1.0
      and all(float(x["part_vue_par_letalon"]) < 1.0 for x in mo[:-1]),
      str([x.get("part_vue_par_letalon") for x in mo]))
    v("un camp vide rend un étalon qui ne voit rien",
      letalon_voit_il(10, 0, 4) == 0.0 and letalon_voit_il(10, 10, 4) == 0.0)

    # ⭐⭐⭐⭐ LE TEST EST UNILATERAL, ET C'EST CE QU'IL FAUT CASSER POUR LE VERIFIER : une colonne qui
    # porte l'etiquette A L'ENVERS ne doit PAS tenir. Un test qui la tiendrait prendrait la valeur
    # absolue sans le dire, et la direction publiee par `191` ne servirait a rien.
    e = [True] * 6 + [False] * 15
    r = np.random.default_rng(31337)
    porteuse = [(1.0 if x else 0.0) + float(t) for x, t in zip(e, r.normal(0.0, 0.5, len(e)))]
    j_p = juger_un_observable(porteuse, e, 19, LE_SENS_DECLARE, 4242)
    j_e = juger_un_observable([-x for x in porteuse], e, 19, LE_SENS_DECLARE, 4242)
    j_b = juger_un_observable(list(r.normal(0.0, 1.0, len(e))), e, 19, LE_SENS_DECLARE, 4242)
    v("★★★★ une colonne qui porte l'étiquette tient", j_p["la_piste_tient"],
      f"{j_p['lecart_dans_le_sens_declare']} contre {j_p['le_plancher_de_detection']}")
    v("★★★★ la MÊME colonne à l'envers ne tient PAS", not j_e["la_piste_tient"],
      f"{j_e['lecart_dans_le_sens_declare']} contre {j_e['le_plancher_de_detection']}")
    v("★★★ et du bruit pur ne tient pas", not j_b["la_piste_tient"],
      f"{j_b['lecart_dans_le_sens_declare']} contre {j_b['le_plancher_de_detection']}")
    v("l'écart dans le sens déclaré est l'aire moins une demie",
      abs(float(j_p["lecart_dans_le_sens_declare"]) - (float(j_p["laire"]) - 0.5)) < 1e-9,
      f"{j_p['lecart_dans_le_sens_declare']} pour une aire de {j_p['laire']}")
    v("l'aire à dépasser est une demie plus le plancher",
      abs(float(j_p["laire_a_depasser"]) - 0.5 - float(j_p["le_plancher_de_detection"])) < 1e-9)

    # ⭐⭐⭐⭐ ET LE PRIX D'UN SEUL OBSERVABLE EST PLUS BAS QUE CELUI DE DIX-NEUF : c'est toute la
    # difference entre chercher et confirmer, et elle se MESURE au lieu de s'affirmer.
    from la_ou_le_rouleau_se_laisse_suivre import (contre_le_melange_des_etiquettes,  # noqa: PLC0415
                                                   le_maximum_de_la_famille)
    colonnes = [_colonne(f"b{i}", list(np.random.default_rng(900 + i).normal(0, 1, len(e))))
                for i in range(19)]
    famille = contre_le_melange_des_etiquettes(colonnes, e, 19, 4242)
    seul = contre_le_melange(colonnes[0]["valeurs"], e, 19, LE_SENS_DECLARE, 4242)
    v("★★★★ le plancher d'UN observable déclaré est plus bas que celui de DIX-NEUF cherchés",
      float(seul["le_plus_grand_ecart"]) < float(famille["le_plus_grand_maximum"]),
      f"{seul['le_plus_grand_ecart']} contre {famille['le_plus_grand_maximum']}")
    v("et la famille de `191` se relit telle quelle",
      le_maximum_de_la_famille(colonnes, e).get("decidable"))

    # ⚠ UN CAMP VIDE EST REFUSE, jamais compte comme « la piste ne tient pas ».
    v("un camp vide est refusé",
      juger_un_observable([1.0, 2.0], [True, True], 19).get("decidable") is False)
    v("et un mélange sans lecture aussi",
      contre_le_melange([1.0, 2.0], [True, True], 19).get("decidable") is False)

    et = sur_letalon(e, 19, 4242)
    v("★★★★ l'étalon sépare ses TROIS faces", bool(et.get("letalon_separe_les_trois")),
      str({k: (x.get("la_piste_tient"), x.get("attendu")) for k, x in et.items()
           if isinstance(x, dict)}))

    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "la_piste_tient_elle_sur_des_chunks_neufs.py"
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
