#!/usr/bin/env python3
"""Le rang d'une spire monte-t-il vers le DEHORS ou vers le DEDANS ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `84` mesure que les 28 bandes de `PHercParis4` decroissent sans
une seule inversion — 18, 10, 8, 7, 6, 5, 5, puis des 4, des 3 et des 2 — et nomme explicitement
ce qu'il ne sait pas : **dans quel sens va le rang**. La circonference croit vers l'exterieur,
donc une passe d'effort constant y couvrirait moins de spires ; si le rang monte vers le dehors,
la decroissance est la courbe de cout du deroulage manuel. S'il monte vers le dedans, elle dit
tout autre chose, et la lecture de `84` s'effondre.

⭐⭐ CE QUI TRANCHE EST UN RAYON, et il se lit sur le maillage le moins cher publie : le
`tifxyz-transformed` sur le volume a 45,532 µm, **330 Kio par canal**, un mebioctet par bande.
Vingt-huit bandes tiennent dans vingt-huit mebioctets.

⚠⚠⚠ ET CE MAILLAGE NE PEUT PAS DONNER LE PAS INTER-FEUILLES, il faut le dire avant de s'en
servir. Mesure : ses cellules voisines sont a **~19,9 voxels** l'une de l'autre dans les deux
directions de la grille, soit **~905 µm** — trois a six fois l'ecart entre feuilles qu'on
cherche. Une distance de feuille a feuille lue dessus serait dominee par l'ecart d'echantillonnage
et non par la matiere. C'est une limite de GRILLE, publiee comme telle.

⚠⚠ L'AXE EST UNE ESTIMATION, ET LE VERDICT DOIT SURVIVRE A DEUX ESTIMATIONS. Un centre pris sur
une bande partielle est biaise vers son arc ; on prend donc la mediane de TOUS les points de
TOUTES les bandes, et on refait le classement avec un second centre pour verifier qu'il ne
change pas. Un ordre qui dependrait du centre choisi ne serait pas un ordre.

⚠ Une bande publie plusieurs REVISIONS. La regle est ecrite : on garde la plus recente, et la
sonde verifie que le classement des rayons survit au choix de la plus ancienne.

Usage :
    uv run python src/nappe/le_sens_du_rang.py --verifier
    uv run python src/nappe/le_sens_du_rang.py --telecharger
    uv run python src/nappe/le_sens_du_rang.py --json docs/mesures/le_sens_du_rang.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "depot"))

FRAGMENT = "PHercParis4"
# ⚠ Le volume et la resolution sont NOMMES, pas devines : c'est le seul maillage publie pour les
# vingt-huit bandes, et sa taille est ce qui rend la mesure faisable.
VOLUME = "20260310170716"
VOXEL_UM = 45.532
CACHE = RACINE / "data" / "paris4_bandes"


def bandes_du_fragment(chemin: Path | None = None) -> list[dict]:
    """Les bandes de `PHercParis4`, une revision par bande, dans l'ordre des rangs.

    ⚠⚠ LA REGLE DE CHOIX EST ECRITE : la revision la plus RECENTE. Une bande en publie deux ou
    trois, et prendre « la premiere rencontree » ferait dependre le chiffre publie de l'ordre
    d'un dictionnaire. La sonde verifie que le classement survit au choix inverse.
    """
    from les_spires_consecutives_publiees import charger_index, rangs_du_suffixe  # noqa: PLC0415

    ech = charger_index(chemin) if chemin else charger_index()
    par: dict[tuple[int, int], list[dict]] = {}
    for sid, seg in ech[FRAGMENT].get("segments", {}).items():
        r = rangs_du_suffixe(seg.get("suffix", ""))
        if not r:
            continue
        chemins = [o["path"] for x in seg.get("data", [])
                   if x["type"] == "tifxyz-transformed"
                   for o in x.get("origins", []) if f"{VOXEL_UM}um" in o["path"]]
        if not chemins:
            continue
        par.setdefault((min(r), max(r)), []).append(
            dict(sid=sid, suffixe=seg.get("suffix", ""), chemin=chemins[0]))
    out = []
    for (lo, hi), revs in sorted(par.items()):
        revs.sort(key=lambda e: e["sid"])
        out.append(dict(de=lo, a=hi, etendue=hi - lo + 1,
                        revisions=[e["sid"] for e in revs],
                        recente=revs[-1], ancienne=revs[0]))
    return out


def fichiers(rev: dict) -> list[Path]:
    """Les trois canaux d'une revision, dans le cache."""
    return [CACHE / rev["sid"] / f"{c}.tif" for c in "xyz"]


def telecharger(bandes: list[dict], toutes_revisions: bool = False) -> dict:
    """Rapatrie les canaux manquants. Rend ce qui a ete pris et ce qui manque encore."""
    from zarr_depth import BUCKET, get  # noqa: PLC0415

    pris = manquants = deja = 0
    for b in bandes:
        revs = ([b["recente"], b["ancienne"]] if toutes_revisions else [b["recente"]])
        for rev in {r["sid"]: r for r in revs}.values():
            for c, dest in zip("xyz", fichiers(rev)):
                if dest.is_file() and dest.stat().st_size > 0:
                    deja += 1
                    continue
                brut = get(f"{BUCKET}/{rev['chemin'].rstrip('/')}/{c}.tif", 300)
                if brut is None:
                    manquants += 1
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(brut)
                pris += 1
    return {"pris": pris, "deja_la": deja, "manquants": manquants}


def points(rev: dict) -> np.ndarray | None:
    """Les points 3D valides d'une bande, en voxels du volume nomme.

    ⚠ Les cellules invalides portent des coordonnees nulles ou negatives — c'est ce que le format
    ecrit hors de la decoupe — et les garder placerait une feuille entiere a l'origine du volume.
    """
    from PIL import Image  # noqa: PLC0415

    Image.MAX_IMAGE_PIXELS = None
    canaux = []
    for f in fichiers(rev):
        if not f.is_file():
            return None
        canaux.append(np.asarray(Image.open(io.BytesIO(f.read_bytes())), dtype=np.float64))
    a = np.stack(canaux, axis=-1)
    ok = np.all(np.isfinite(a), axis=-1) & np.all(a > 0, axis=-1)
    return a[ok]


def echantillonnage(rev: dict) -> dict | None:
    """L'ecart entre deux cellules VOISINES de la grille, en micrometres.

    ⭐ C'EST CE CHIFFRE QUI INTERDIT DE LIRE UN PAS INTER-FEUILLES ICI. Il est mesure sur la
    grille elle-meme — la mediane des distances entre cellules adjacentes — donc il ne suppose
    rien du maillage. Une limite de grille se publie, elle ne se devine pas.
    """
    from PIL import Image  # noqa: PLC0415

    Image.MAX_IMAGE_PIXELS = None
    canaux = []
    for f in fichiers(rev):
        if not f.is_file():
            return None
        canaux.append(np.asarray(Image.open(io.BytesIO(f.read_bytes())), dtype=np.float64))
    a = np.stack(canaux, axis=-1)
    ok = np.all(np.isfinite(a), axis=-1) & np.all(a > 0, axis=-1)
    ds = []
    for axe in (0, 1):
        va = np.take(ok, range(0, ok.shape[axe] - 1), axis=axe)
        vb = np.take(ok, range(1, ok.shape[axe]), axis=axe)
        pa = np.take(a, range(0, a.shape[axe] - 1), axis=axe)
        pb = np.take(a, range(1, a.shape[axe]), axis=axe)
        m = va & vb
        if m.any():
            ds.append(np.linalg.norm(pb[m] - pa[m], axis=-1))
    if not ds:
        return None
    d = np.concatenate(ds)
    return {"grille": list(ok.shape), "valides": int(ok.sum()),
            "pas_median_vx": round(float(np.median(d)), 2),
            "pas_median_um": round(float(np.median(d)) * VOXEL_UM, 1)}


def axe(nuages: list[np.ndarray]) -> tuple[float, float]:
    """Le centre de l'enroulement dans le plan (x, y), estime sur TOUS les points.

    ⚠⚠ LA MEDIANE ET NON LA MOYENNE. Une bande partielle est un arc, donc sa moyenne tire le
    centre vers cet arc ; la mediane de l'union de toutes les bandes resiste a un secteur
    surrepresente. Ce n'est pas un ajustement de cercle et ne pretend pas l'etre : ce qu'on
    demande a ce centre est de CLASSER des rayons, pas de les mesurer dans l'absolu.

    ⚠ Le troisieme axe est celui du rouleau et n'entre pas dans le rayon : un rayon mesure en
    trois dimensions melangerait la position le long du rouleau avec la distance a son axe.
    """
    tout = np.concatenate([n for n in nuages if n is not None and len(n)])
    return float(np.median(tout[:, 0])), float(np.median(tout[:, 1]))


def rayon(nuage: np.ndarray, cx: float, cy: float) -> dict:
    """Le rayon de cette bande autour du centre donne, en micrometres."""
    r = np.hypot(nuage[:, 0] - cx, nuage[:, 1] - cy) * VOXEL_UM
    return {"rayon_median_um": round(float(np.median(r)), 1),
             "rayon_p10_um": round(float(np.percentile(r, 10)), 1),
             "rayon_p90_um": round(float(np.percentile(r, 90)), 1),
             "points": int(len(r))}


def longueur_par_passe(etendue: int, rayon_um: float) -> float:
    """La longueur de feuille qu'une passe humaine a couverte, en millimetres.

    ⭐⭐⭐ C'EST LA PREDICTION QUI REND L'EXPLICATION FALSIFIABLE. Dire « la circonference croit
    vers l'exterieur, donc une passe y couvre moins de spires » n'est une histoire que tant qu'on
    ne la mesure pas. Si une passe couvre une LONGUEUR de feuille a peu pres constante, alors
    `etendue x 2piR` doit etre a peu pres constant sur les vingt-huit bandes — et l'ecart-type
    relatif de ce produit tranche, sans qu'aucun seuil ne soit choisi.

    ⚠ La longueur et non l'aire : la hauteur balayee le long du rouleau n'est pas mesuree ici, et
    la supposer constante ajouterait une hypothese a celle qu'on teste.
    """
    return 2.0 * np.pi * rayon_um * etendue / 1000.0


def paliers(lignes: list[dict]) -> dict:
    """Les suites de bandes de MEME etendue, et ce que la longueur y fait.

    ⚠⚠⚠ POURQUOI CE DECOUPAGE EXISTE, ET CE QU'IL EMPECHE DE CONCLURE. L'etendue d'une bande est
    un ENTIER : on ne coupe pas deux spires et demie. A l'interieur d'un palier — une suite de
    bandes de meme etendue — la longueur de feuille croit donc mecaniquement avec le rayon, et
    l'etendue ne redescend qu'au palier suivant. Le residu de la prediction « une passe couvre une
    longueur constante » est donc en partie cette QUANTIFICATION et non du bruit.

    ⚠⚠ Et c'est ce qui interdit une conclusion tentante : le maximum atteint juste avant chaque
    descente d'etendue decline lui aussi (838, 535, 498, 490, 459, 436, 433, 415), ce qui
    RESSEMBLE a un budget par passe qui se reduit vers l'exterieur. Mais un pas de quantification
    vaut une circonference entiere — 156 mm au rang 128 — donc a cette precision le declin du
    maximum n'est pas separable de la quantification. La mesure rend les deux et ne tranche pas.
    """
    out, courant = [], []
    for x in lignes:
        if courant and x["etendue"] != courant[-1]["etendue"]:
            out.append(courant)
            courant = []
        courant.append(x)
    if courant:
        out.append(courant)
    return {
        "paliers": [{"etendue": g[0]["etendue"], "bandes": len(g),
                     "longueur_min_mm": min(y["longueur_par_passe_mm"] for y in g),
                     "longueur_max_mm": max(y["longueur_par_passe_mm"] for y in g),
                     "croit_avec_le_rayon": all(
                         b["longueur_par_passe_mm"] > a["longueur_par_passe_mm"]
                         for a, b in zip(g, g[1:]))} for g in out],
        # ⭐ Le maximum atteint juste avant chaque descente d'etendue : ce qui ressemblerait a un
        # budget par passe, et que la quantification empeche de lire comme tel.
        "maximums_avant_descente_mm": [max(y["longueur_par_passe_mm"] for y in g)
                                       for g in out[:-1]],
        "tous_les_paliers_croissent": all(
            all(b["longueur_par_passe_mm"] > a["longueur_par_passe_mm"]
                for a, b in zip(g, g[1:])) for g in out if len(g) > 1),
    }


def sens(rangs: list[int], rayons: list[float]) -> dict:
    """Le rayon monte-t-il avec le rang, descend-il, ou ni l'un ni l'autre ?

    ⭐ La reponse est un COMPTE d'inversions et non une correlation : une correlation de 0,9
    laisse la question ouverte pour les paires qui la contredisent, alors qu'une monotonie se
    refute d'une seule inversion et se constate sans seuil.
    """
    montees = sum(1 for a, b in zip(rayons, rayons[1:]) if b > a)
    descentes = sum(1 for a, b in zip(rayons, rayons[1:]) if b < a)
    n = len(rayons) - 1
    return {"paires": n, "montees": montees, "descentes": descentes,
            "vers_le_dehors": montees == n and n > 2,
            "vers_le_dedans": descentes == n and n > 2,
            "du_premier_au_dernier": [rayons[0], rayons[-1]] if rayons else [],
            "rangs": [rangs[0], rangs[-1]] if rangs else []}


def _dispersion(q: list[float]) -> dict:
    """Mediane, bornes, rapport et ecart-type relatif d'une liste — publie ensemble ou rien.

    ⚠ Un ecart-type relatif seul ne dit pas si la population a deux regimes ; le RAPPORT
    max/min le dit, et les deux ensemble se lisent sans se contredire.
    """
    if not q:
        return {}
    return {"bandes": len(q), "median": round(float(np.median(q)), 1),
            "min": round(float(min(q)), 1), "max": round(float(max(q)), 1),
            "rapport": round(float(max(q) / min(q)), 2),
            "ecart_type_relatif": round(float(np.std(q) / np.mean(q)), 3)}


def mesurer(toutes_revisions: bool = False) -> dict:
    """Le rayon de chaque bande, et le sens que ça donne au rang."""
    bandes = bandes_du_fragment()
    clef = "ancienne" if toutes_revisions else "recente"
    nuages, absentes = {}, []
    for b in bandes:
        n = points(b[clef])
        if n is None or not len(n):
            absentes.append([b["de"], b["a"]])
            continue
        nuages[(b["de"], b["a"])] = n
    if len(nuages) < 3:
        return {"fragment": FRAGMENT, "voxel_um": VOXEL_UM, "volume": VOLUME,
                "bandes": len(bandes), "bandes_lues": len(nuages),
                "bandes_absentes": absentes,
                "revision": clef, "sens": None,
                "message": "cache incomplet : lancer --telecharger"}
    cx, cy = axe(list(nuages.values()))
    # ⚠⚠ LE SECOND CENTRE EST CELUI DE LA BANDE LA PLUS INTERIEURE PAR SON RANG, et il sert
    # uniquement a verifier que le classement ne depend pas du centre. Deux centres qui rendent
    # deux ordres diraient que l'ordre est une propriete de l'estimation, pas de la matiere.
    premiere = min(nuages)
    cx2, cy2 = (float(np.median(nuages[premiere][:, 0])),
                float(np.median(nuages[premiere][:, 1])))
    lignes = []
    for (lo, hi), n in sorted(nuages.items()):
        r1 = rayon(n, cx, cy)
        r2 = rayon(n, cx2, cy2)
        lignes.append({"de": lo, "a": hi, "etendue": hi - lo + 1,
                       **r1, "rayon_median_second_centre_um": r2["rayon_median_um"]})
    for x in lignes:
        x["longueur_par_passe_mm"] = round(longueur_par_passe(x["etendue"],
                                                              x["rayon_median_um"]), 1)
    rangs = [x["de"] for x in lignes]
    s1 = sens(rangs, [x["rayon_median_um"] for x in lignes])
    s2 = sens(rangs, [x["rayon_median_second_centre_um"] for x in lignes])
    ech = echantillonnage(bandes[0][clef])
    return {
        "fragment": FRAGMENT, "volume": VOLUME, "voxel_um": VOXEL_UM,
        "revision": clef,
        "bandes": len(bandes), "bandes_lues": len(lignes), "bandes_absentes": absentes,
        "centre_vx": [round(cx, 1), round(cy, 1)],
        "centre_de_controle_vx": [round(cx2, 1), round(cy2, 1)],
        "lignes": lignes,
        "sens": s1,
        "sens_second_centre": s2,
        "le_sens_survit_au_centre": (s1["vers_le_dehors"] == s2["vers_le_dehors"]
                                     and s1["vers_le_dedans"] == s2["vers_le_dedans"]),
        # ⚠⚠⚠ LA LIMITE DE GRILLE, PUBLIEE AVEC LA MESURE : ce maillage ne peut pas donner le pas
        # inter-feuilles, et un lecteur qui l'ignorerait tirerait un pas de trois a six fois trop
        # grand sans qu'aucune ligne ne le previenne.
        # ⭐⭐⭐ LA PREDICTION, MESUREE : si une passe humaine couvre une longueur de feuille a
        # peu pres constante, ce produit l'est aussi, et « la circonference explique la
        # decroissance » cesse d'etre une histoire. L'ecart-type relatif tranche sans seuil.
        # ⚠ LE MEME RESUME QUE HORS-COEUR, par la MEME fonction : deux definitions d'une meme
        # dispersion finiraient par ne pas s'accorder, et c'est celle-la qu'on compare a l'autre.
        "longueur_par_passe_mm": _dispersion([x["longueur_par_passe_mm"] for x in lignes]),
        "paliers_dune_meme_etendue": paliers(lignes),
        # ⚠⚠ LA DISPERSION SANS LA BANDE DU COEUR, publiee a cote de celle avec : la bande de 18
        # spires est un facteur deux au-dessus de toutes les autres, et une dispersion qui la
        # melange decrit une population de deux regimes comme si elle en decrivait un.
        "longueur_par_passe_hors_coeur_mm": _dispersion(
            [x["longueur_par_passe_mm"] for x in lignes
             if x["etendue"] < max(y["etendue"] for y in lignes)]),
        "echantillonnage_du_maillage": ech,
        "ce_maillage_donne_le_pas_inter_feuilles": False,
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- la géométrie, sur un enroulement fabriqué de toutes pièces --------------------------
    # ⚠⚠ UNE SPIRALE FABRIQUEE, et son centre n'est PAS a l'origine : un centre a l'origine
    # laisserait passer un estimateur qui rendrait zero.
    c0 = (1000.0, 2000.0)
    faux = {}
    for k, r0 in enumerate([100.0, 200.0, 300.0, 400.0], start=1):
        th = np.linspace(0.0, 2 * np.pi, 400)
        faux[k] = np.stack([c0[0] + r0 * np.cos(th), c0[1] + r0 * np.sin(th),
                            np.linspace(0, 50, th.size)], axis=-1)
    cx, cy = axe(list(faux.values()))
    v("le centre estimé retrouve celui de la spirale fabriquée",
      abs(cx - c0[0]) < 12 and abs(cy - c0[1]) < 12, f"({cx:.1f}, {cy:.1f}) pour {c0}")
    ry = [rayon(faux[k], cx, cy)["rayon_median_um"] for k in sorted(faux)]
    v("les rayons sortent dans l'ordre des coquilles",
      ry == sorted(ry), str(ry))
    v("... et à l'échelle du voxel nommé",
      abs(ry[0] - 100.0 * VOXEL_UM) < 0.05 * 100.0 * VOXEL_UM, str(ry[0]))

    s = sens([1, 2, 3, 4], ry)
    v("un rayon qui monte avec le rang dit « vers le dehors »",
      s["vers_le_dehors"] and not s["vers_le_dedans"], str(s))
    v("... et l'inverse dit « vers le dedans »",
      sens([1, 2, 3, 4], ry[::-1])["vers_le_dedans"])
    # ⚠⚠ UNE SEULE INVERSION SUFFIT A REFUSER, c'est tout l'interet d'un compte plutot que d'une
    # correlation : une correlation de 0,9 laisserait passer la paire qui contredit.
    casse = [ry[0], ry[2], ry[1], ry[3]]
    v("une seule inversion refuse la monotonie",
      not sens([1, 2, 3, 4], casse)["vers_le_dehors"]
      and sens([1, 2, 3, 4], casse)["montees"] == 2, str(sens([1, 2, 3, 4], casse)))
    # ⚠ Trois points ne suffisent pas a l'affirmer : deux paires sont une coincidence courante.
    v("deux paires ne suffisent pas à affirmer un sens",
      not sens([1, 2, 3], [1.0, 2.0, 3.0])["vers_le_dehors"],
      str(sens([1, 2, 3], [1.0, 2.0, 3.0])))
    # ⚠ Le rayon ignore le troisieme axe : deux coquilles de meme rayon a deux hauteurs
    # differentes doivent rendre le MEME rayon, sinon on melange la position le long du rouleau.
    haut = faux[1].copy()
    haut[:, 2] += 5000.0
    v("le rayon ne dépend pas de la position le long du rouleau",
      rayon(haut, cx, cy)["rayon_median_um"] == rayon(faux[1], cx, cy)["rayon_median_um"])

    # ⭐⭐ LA PREDICTION FALSIFIABLE : une passe qui couvre une longueur constante donne un
    # produit constant. La fonction est exercee sur des nombres dont on connait la reponse.
    v("une passe deux fois plus courte à rayon double couvre la même longueur",
      abs(longueur_par_passe(4, 100.0) - longueur_par_passe(2, 200.0)) < 1e-9,
      f"{longueur_par_passe(4, 100.0)} contre {longueur_par_passe(2, 200.0)}")
    v("... et la longueur est bien 2piR fois l'étendue, en millimètres",
      abs(longueur_par_passe(1, 1000.0) - 2 * np.pi) < 1e-9,
      str(longueur_par_passe(1, 1000.0)))

    # ⚠⚠ LA QUANTIFICATION DE L'ETENDUE, exercee sur des paliers fabriques : a l'interieur d'un
    # palier la longueur doit croitre, et le decoupage doit rendre un palier par valeur d'etendue.
    faux_lignes = [{"etendue": 4, "longueur_par_passe_mm": 300.0},
                   {"etendue": 4, "longueur_par_passe_mm": 320.0},
                   {"etendue": 3, "longueur_par_passe_mm": 260.0},
                   {"etendue": 3, "longueur_par_passe_mm": 280.0}]
    pal = paliers(faux_lignes)
    v("un palier par valeur d'étendue", [g["etendue"] for g in pal["paliers"]] == [4, 3],
      str(pal["paliers"]))
    v("... et la longueur croît dans chaque palier", pal["tous_les_paliers_croissent"])
    v("... et le maximum avant descente est publié",
      pal["maximums_avant_descente_mm"] == [320.0], str(pal["maximums_avant_descente_mm"]))
    # ⚠ Un palier qui DECROIT doit être vu comme tel, sinon le contrôle ne peut pas échouer.
    v("un palier décroissant est refusé",
      not paliers([{"etendue": 4, "longueur_par_passe_mm": 320.0},
                   {"etendue": 4, "longueur_par_passe_mm": 300.0}])[
          "tous_les_paliers_croissent"])
    # ⚠⚠ LE RAPPORT ET L'ECART-TYPE ENSEMBLE : un ecart-type seul ne voit pas deux regimes.
    d = _dispersion([100.0, 100.0, 100.0, 400.0])
    v("la dispersion publie son rapport max/min", d["rapport"] == 4.0, str(d))
    v("... et une liste vide ne rend rien plutôt qu'un zéro", _dispersion([]) == {})

    # --- l'index ------------------------------------------------------------------------------
    b = bandes_du_fragment()
    v("les 28 bandes sont lues, chacune avec un maillage", len(b) == 28, str(len(b)))
    v("... et chacune garde ses révisions", all(x["revisions"] for x in b))
    # ⚠⚠ LA REGLE DE CHOIX EST DETERMINISTE : la plus recente, donc le plus grand identifiant.
    v("la révision retenue est la plus récente",
      all(x["recente"]["sid"] == max(x["revisions"]) for x in b))
    v("... et la plus ancienne est gardée pour la sonde",
      all(x["ancienne"]["sid"] == min(x["revisions"]) for x in b))
    v("l'étendue des bandes décroît, comme `84` l'a mesuré",
      [x["etendue"] for x in b][:3] == [18, 10, 8], str([x["etendue"] for x in b][:5]))

    # --- les données réelles, si le cache est là ---------------------------------------------
    r = mesurer()
    if r.get("sens") is None:
        print(f"  ⚠ cache incomplet ({r['bandes_lues']}/{r['bandes']} bandes) : contrôles sur "
              "données réelles sautés — lancer --telecharger")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    v("toutes les bandes sont lues", r["bandes_lues"] == r["bandes"],
      f"{r['bandes_lues']}/{r['bandes']} — absentes {r['bandes_absentes']}")
    # ⚠⚠⚠ LE VERDICT DOIT SURVIVRE AU CENTRE : un ordre qui dependrait de l'estimation ne
    # serait pas un ordre.
    v("le sens du rang ne dépend pas du centre estimé", r["le_sens_survit_au_centre"],
      f"{r['sens']} contre {r['sens_second_centre']}")
    v("le rang a un sens, et il est nommé",
      r["sens"]["vers_le_dehors"] != r["sens"]["vers_le_dedans"], str(r["sens"]))
    # ⚠⚠⚠ LA LIMITE DE GRILLE EST PUBLIEE, et elle est mesuree et non supposee.
    v("le maillage publie son échantillonnage",
      r["echantillonnage_du_maillage"] is not None
      and r["echantillonnage_du_maillage"]["pas_median_um"] > 300,
      str(r["echantillonnage_du_maillage"]))
    v("... et déclare qu'il ne donne PAS le pas inter-feuilles",
      r["ce_maillage_donne_le_pas_inter_feuilles"] is False)
    # ⭐⭐ LA PREDICTION, SUR LES VRAIES BANDES : une passe couvre-t-elle une longueur de feuille
    # a peu pres constante ? Le RAPPORT hors coeur tranche, et la bande du coeur est publiee a
    # part parce qu'elle est un second regime et non un point de la meme population.
    H = r["longueur_par_passe_hors_coeur_mm"]
    v("hors la bande du cœur, la longueur par passe tient dans un facteur deux",
      H and H["rapport"] < 2.0, str(H))
    v("... et la bande du cœur est bien au-delà",
      r["longueur_par_passe_mm"]["rapport"] > 2.5,
      str(r["longueur_par_passe_mm"]))
    # ⚠⚠ ET LE RESIDU EST DE LA QUANTIFICATION : dans chaque palier d'etendue constante la
    # longueur croit avec le rayon, ce qui est mecanique et non du bruit.
    pal = r["paliers_dune_meme_etendue"]
    v("dans chaque palier d'étendue constante, la longueur croît avec le rayon",
      pal["tous_les_paliers_croissent"], str(pal["paliers"]))
    v("... et les maximums avant descente sont publiés, sans être lus comme un budget",
      len(pal["maximums_avant_descente_mm"]) == len(pal["paliers"]) - 1,
      str(pal["maximums_avant_descente_mm"]))

    # ⚠⚠⚠ LA SONDE DE LA REGLE DE CHOIX, devenue un controle permanent : le sens du rang doit
    # etre le meme avec la revision la plus ANCIENNE. Un verdict qui dependrait de la revision
    # retenue serait une propriete du choix et non de la matiere. Le controle se saute si le
    # cache des anciennes revisions n'est pas la, et le DIT.
    vieux = mesurer(toutes_revisions=True)
    if vieux.get("sens") is None:
        print("  ⚠ cache des révisions anciennes absent : sonde du choix de révision sautée "
              "— lancer --telecharger --toutes-revisions")
    else:
        v("le sens du rang survit au choix de la révision la plus ancienne",
          vieux["sens"]["vers_le_dehors"] == r["sens"]["vers_le_dehors"]
          and vieux["sens"]["vers_le_dedans"] == r["sens"]["vers_le_dedans"],
          f"{vieux['sens']} contre {r['sens']}")
        # ⚠⚠⚠ LES BANDES SE COMPARENT PAR LEUR CLEF, JAMAIS PAR LEUR POSITION. Ma premiere
        # version zippait les deux listes : quand le cache des anciennes revisions est partiel,
        # une bande manquante decale tout et la comparaison apparie la bande i de l'une avec la
        # bande i de l'autre — deux bandes differentes. Elle rendait alors 16 % d'ecart, qui
        # n'etait pas un desaccord de revisions mais un desaccord de MES DEUX LISTES.
        ra = {(x["de"], x["a"]): x["rayon_median_um"] for x in vieux["lignes"]}
        rb = {(x["de"], x["a"]): x["rayon_median_um"] for x in r["lignes"]}
        communes = sorted(set(ra) & set(rb))
        ecarts = [abs(ra[k] - rb[k]) / rb[k] for k in communes]
        v("les deux révisions sont comparées sur les bandes COMMUNES, pas par position",
          len(communes) >= 3, f"{len(communes)} bandes communes")
        # ⚠⚠⚠ ET CE QU'IL NE FAUT PAS ASSERTER. Ma premiere version exigeait que les rayons ne
        # bougent pas de plus d'un pour cent entre revisions : ils bougent de **15,9 %**, et ce
        # n'est pas un defaut. Les deux revisions ne couvrent pas la meme etendue de surface —
        # grille 184x448 et 78453 cellules valides pour la recente, 119x449 et 50877 pour
        # l'ancienne — donc leurs medianes portent sur deux echantillons de la meme bande. Un
        # controle qui exigerait l'egalite serait un controle qui ne peut pas passer pour une
        # raison qui n'est pas un defaut.
        # ⭐ CE QUI DOIT TENIR, ET QUI TIENT : le CLASSEMENT. Le rayon est un resume d'un
        # echantillon, l'ordre est une propriete de l'enroulement.
        v("le classement complet des rayons survit à la révision, sans une inversion",
          vieux["sens"]["montees"] == vieux["sens"]["paires"],
          f"{vieux['sens']['montees']}/{vieux['sens']['paires']} montées")
        v("... et le désaccord de rayon entre révisions est RAPPORTÉ, pas asserti",
          bool(ecarts), f"max {max(ecarts):.1%} sur {len(communes)} bandes — "
          f"les deux révisions couvrent {vieux['echantillonnage_du_maillage']['valides']} et "
          f"{r['echantillonnage_du_maillage']['valides']} cellules")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--telecharger", action="store_true")
    p.add_argument("--toutes-revisions", action="store_true",
                   help="prend aussi la révision la plus ancienne (pour la sonde)")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    bandes = bandes_du_fragment()
    if a.telecharger:
        rap = telecharger(bandes, a.toutes_revisions)
        print(f"{rap['pris']} canaux pris · {rap['deja_la']} déjà là · "
              f"{rap['manquants']} manquants")

    r = mesurer(toutes_revisions=a.toutes_revisions)
    if r.get("sens") is None:
        print(f"⚠ {r['message']} ({r['bandes_lues']}/{r['bandes']} bandes)")
        return 1
    e = r["echantillonnage_du_maillage"]
    print(f"{r['fragment']} · maillage sur {r['volume']} à {r['voxel_um']} µm · "
          f"révision {r['revision']}")
    print(f"grille {e['grille']} · {e['valides']} cellules valides · cellules voisines à "
          f"{e['pas_median_vx']} vx = {e['pas_median_um']} µm\n")
    print(f"{'bande':>12} {'étendue':>8} {'rayon médian':>14} {'p10..p90':>18} "
          f"{'2e centre':>11}")
    for x in r["lignes"]:
        print(f"  w{x['de']:03d}-{x['a']:03d} {x['etendue']:>8} "
              f"{x['rayon_median_um'] / 1000:>11.2f} mm "
              f"{x['rayon_p10_um'] / 1000:>8.2f}..{x['rayon_p90_um'] / 1000:<7.2f} "
              f"{x['rayon_median_second_centre_um'] / 1000:>8.2f} mm")
    s = r["sens"]
    mot = ("VERS LE DEHORS" if s["vers_le_dehors"]
           else ("VERS LE DEDANS" if s["vers_le_dedans"] else "NI L'UN NI L'AUTRE"))
    print(f"\n⭐ le rang monte {mot} — {s['montees']} montée(s) et "
          f"{s['descentes']} descente(s) sur {s['paires']} paires")
    print(f"   du rang {s['rangs'][0]} au rang {s['rangs'][1]} : "
          f"{s['du_premier_au_dernier'][0] / 1000:.2f} mm → "
          f"{s['du_premier_au_dernier'][1] / 1000:.2f} mm")
    print(f"   {'✅' if r['le_sens_survit_au_centre'] else '⛔'} le sens "
          f"{'survit' if r['le_sens_survit_au_centre'] else 'NE SURVIT PAS'} au second centre")
    L = r["longueur_par_passe_mm"]
    H = r["longueur_par_passe_hors_coeur_mm"]
    print(f"\n⭐⭐ une passe humaine couvre {L['median']:.0f} mm de feuille en médiane "
          f"({L['min']:.0f} à {L['max']:.0f}, rapport ×{L['rapport']})")
    print(f"   hors la bande du cœur : {H['min']:.0f} à {H['max']:.0f} mm sur {H['bandes']} "
          f"bandes, rapport ×{H['rapport']}, écart-type relatif {H['ecart_type_relatif']:.0%}")
    pal = r["paliers_dune_meme_etendue"]
    print(f"   {len(pal['paliers'])} paliers d'étendue constante · "
          f"{'tous croissent' if pal['tous_les_paliers_croissent'] else 'un palier décroît'} "
          "avec le rayon")
    print(f"   maximums avant chaque descente d'étendue : "
          f"{' '.join(f'{x:.0f}' for x in pal['maximums_avant_descente_mm'])} mm")
    print("   ⚠ ce déclin n'est PAS séparable de la quantification : un pas d'étendue vaut une")
    print("     circonférence entière, donc la mesure rend les deux et ne tranche pas.")
    print(f"\n⚠⚠ ce maillage ne donne PAS le pas inter-feuilles : ses cellules voisines sont à "
          f"{e['pas_median_um']} µm,")
    print("   soit trois à six fois l'écart cherché. C'est une limite de GRILLE.")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
