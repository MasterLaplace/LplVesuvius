#!/usr/bin/env python3
"""Le pas inter-feuilles, lu sur les transferts que l'HUMAIN a reussis.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST LA SEULE VERITE DE TERRAIN DU GOULOT. `84` etablit que
`PHercParis4` publie **92 franchissements de spire contenus dans une seule maille**, et zero
partout ailleurs. Une bande `wNNN-MMM` est donc un transfert de spire a spire **deja fait a la
main**, et sa geometrie est lisible sans toucher au volume.

⭐⭐⭐ PREMIER RESULTAT : L'ETENDUE DECLAREE **EST** LE NOMBRE DE TOURS. En deroulant l'angle le
long d'une ligne de grille, `w028-037` rend **9,97** tours pour 10 declares et `w116-117` rend
**1,99** pour 2 — ecart median **-0,01 tour sur 27 des 28 bandes**. Les noms ne sont pas des
etiquettes, c'est la geometrie. ⚠ Une exception nommee : `w010-027` rend **12,75** tours pour 18.

⭐⭐ SECOND RESULTAT : le pas mesure sur ces transferts vaut **202 µm**, ce qui confirme l'atlas
`winding-ruler` (182,4 µm, p25 134,4, p75 259,2) par un chemin **entierement independant** —
maillages publies par des humains contre predictions de surface le long de rayons.

⚠⚠⚠ ET UN GRADIENT QUE J'AI FAILLI PUBLIER, RETRACTE AVANT DE L'ETRE. La pente brute donne 205 µm
au coeur, ~145 au milieu, ~380 puis **~1000 µm au bord** — un facteur huit qu'on lirait comme une
delamination. C'est **l'estimateur**, et le controle ne depend d'aucune hypothese sur POURQUOI :
sur UNE SEULE bande de dix tours, donc a pas constant par construction, ajuster la pente sur une
fenetre de plus en plus courte donne 202, 208, 224, 287, **523**, **1817** µm pour 10, 6, 4, 3, 2
et 1 tour. Le pas ne change pas ; seule la fenetre change.

⚠⚠⚠ ET LA CAUSE N'EST PAS ETABLIE — c'est ecrit ici plutot que devine. Deux mecanismes ont ete
testes sur fixture, et aucun ne rend la magnitude :

  - une **section ovale** ne gonfle PAS la pente, elle la DEGONFLE (200,3 sur huit tours contre
    183,2 sur un). C'etait ma premiere explication et elle est fausse : un `cos(2t)` fait deux
    periodes par tour, donc il s'annule meme sur un tour ;
  - un **centre decale** gonfle bien, et dans le bon sens — 200,0 / 216,2 / 233,3 / 269,5 pour
    un decalage de 0, 0,5, 1 et 2 mm sur une fenetre d'un tour. Mais l'ampleur n'y est pas : il
    faudrait des dizaines de millimetres de decalage pour atteindre 1817 µm, ce qui est absurde.

⭐⭐ CE QUI TIENT SANS LA CAUSE, ET C'EST LA REGLE QUI COMPTE POUR TOUT MARCHEUR : **on ne mesure
pas le pas d'un enroulement sur un arc court.** Les bandes du bord n'en couvrent que deux, donc
elles ne peuvent pas le mesurer — et les croire ferait croire a une delamination qui n'est pas
mesuree ici. Un controle qui reproduit un biais sur des donnees dont on connait la reponse
n'a pas besoin d'expliquer le biais pour le refuter.

⚠ Une ligne de grille est ISO-Z (ecart-type 1,1 a 1,8 mm) et une colonne court sur tout le rouleau
(42 mm). C'est verifie, pas suppose : la pente est donc bien lue a hauteur constante.

Usage :
    uv run python src/nappe/le_pas_lu_sur_les_transferts.py --verifier
    uv run python src/nappe/le_pas_lu_sur_les_transferts.py \\
        --json docs/mesures/le_pas_lu_sur_les_transferts.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "depot"))

# ⚠⚠ LE NOMBRE DE TOURS MINIMAL POUR QU'UNE PENTE VEUILLE DIRE QUELQUE CHOSE. Il est DERIVE du
# controle et non choisi : la pente ajustee vaut 202 µm sur dix tours, 208 sur six, 224 sur
# quatre — puis 287 sur trois et 523 sur deux. Le coude est entre quatre et trois, donc on exige
# quatre. Descendre plus bas ne mesure plus le pas, ca mesure la forme de la section.
TOURS_MINIMUM = 4
# ⚠ Une ligne de grille doit etre presque entiere pour que l'angle deroule couvre la bande.
PART_VALIDE_MINIMUM = 0.8
FENETRES = (10, 6, 4, 3, 2, 1)


def grille(rev: dict) -> tuple[np.ndarray, np.ndarray] | None:
    """Les points 3D d'une bande EN GARDANT sa topologie de grille, et le masque des valides.

    ⚠⚠ `le_sens_du_rang.points` aplatit en nuage, ce qui perd exactement ce dont ce fichier a
    besoin : l'ordre des cellules. Un nuage ne dit pas ou est le franchissement ; la grille si.
    """
    from PIL import Image  # noqa: PLC0415

    import le_sens_du_rang as R  # noqa: PLC0415

    Image.MAX_IMAGE_PIXELS = None
    canaux = []
    for f in R.fichiers(rev):
        if not f.is_file():
            return None
        canaux.append(np.asarray(Image.open(io.BytesIO(f.read_bytes())), dtype=np.float64))
    a = np.stack(canaux, axis=-1)
    return a, np.all(np.isfinite(a), axis=-1) & np.all(a > 0, axis=-1)


def orientation(a: np.ndarray, ok: np.ndarray, voxel_um: float) -> dict:
    """Une LIGNE de la grille est-elle a hauteur constante, ou une colonne ?

    ⭐ C'est la condition qui rend la pente lisible : une pente lue le long d'une ligne qui monte
    le long du rouleau melangerait l'enroulement avec la forme de la section a d'autres hauteurs.
    Verifie plutot que suppose.
    """
    z = np.where(ok, a[..., 2], np.nan)
    with np.errstate(invalid="ignore"):
        par_ligne = float(np.nanmedian(np.nanstd(z, axis=1))) * voxel_um / 1000.0
        par_colonne = float(np.nanmedian(np.nanstd(z, axis=0))) * voxel_um / 1000.0
    return {"ecart_type_z_le_long_dune_ligne_mm": round(par_ligne, 2),
            "ecart_type_z_le_long_dune_colonne_mm": round(par_colonne, 2),
            "les_lignes_sont_iso_z": par_ligne * 5.0 < par_colonne}


def tours_et_pente(a: np.ndarray, ok: np.ndarray, bords: np.ndarray, cx: np.ndarray,
                   cy: np.ndarray, voxel_um: float,
                   fenetre_tours: float | None = None) -> dict:
    """Combien de tours une ligne de grille fait-elle, et de combien le rayon y monte-t-il ?

    ⚠⚠⚠ LA PENTE N'EST RENDUE QUE SI LA FENETRE COUVRE ASSEZ DE TOURS. Sur un arc court, le
    rayon oscille avec l'angle parce que la section n'est pas un cercle, et l'ajustement lit
    cette oscillation comme une montee. Mesure : la meme bande de dix tours rend 202 µm sur dix
    et **1817 µm sur un**. Une pente sur deux tours n'est pas une mesure du pas.
    """
    H, W = ok.shape
    i = np.clip(np.searchsorted(bords, a[..., 2], side="right") - 1, 0, cx.size - 1)
    rad = np.hypot(a[..., 0] - cx[i], a[..., 1] - cy[i]) * voxel_um / 1000.0
    ang = np.arctan2(a[..., 1] - cy[i], a[..., 0] - cx[i])
    tours: list[float] = []
    pentes: list[float] = []
    for r in range(H):
        m = ok[r]
        if int(m.sum()) < PART_VALIDE_MINIMUM * W:
            continue
        aa = np.unwrap(ang[r][m])
        rr = rad[r][m]
        etendue = float(aa.max() - aa.min())
        if etendue < 0.5 * 2 * np.pi:
            continue
        tours.append(etendue / (2 * np.pi))
        s = slice(None)
        if fenetre_tours is not None:
            if etendue < fenetre_tours * 2 * np.pi * 0.95:
                continue
            s = aa <= aa.min() + fenetre_tours * 2 * np.pi
            if int(np.sum(s)) < 10:
                continue
        pentes.append(abs(float(np.polyfit(aa[s], rr[s], 1)[0])) * 2 * np.pi * 1000.0)
    if not tours:
        return {}
    return {"lignes": len(tours), "tours_median": round(float(np.median(tours)), 2),
            "pente_um_par_tour": round(float(np.median(pentes)), 1) if pentes else None,
            "pente_p25": round(float(np.percentile(pentes, 25)), 1) if pentes else None,
            "pente_p75": round(float(np.percentile(pentes, 75)), 1) if pentes else None}


def mesurer() -> dict:
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415

    bandes = R.bandes_du_fragment()
    nuages = []
    for x in bandes:
        n = R.points(x["recente"])
        if n is not None and len(n):
            nuages.append(n)
    if len(nuages) < 3:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    tout = np.concatenate(nuages)
    bords, cx, cy, _, _ = A.axe_par_tranche(tout)

    lignes = []
    orient = None
    for x in bandes:
        g = grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        if orient is None:
            orient = orientation(a, ok, R.VOXEL_UM)
        t = tours_et_pente(a, ok, bords, cx, cy, R.VOXEL_UM)
        if not t:
            continue
        lignes.append({"de": x["de"], "a": x["a"], "etendue": x["etendue"], **t,
                       "ecart_tours": round(t["tours_median"] - x["etendue"], 2)})

    # ⚠⚠⚠ LE CONTROLE QUI RETRACTE LE GRADIENT : sur UNE bande de dix tours, donc a pas constant
    # par construction, la pente enfle quand la fenetre retrecit. Sans lui, les ~1000 µm des
    # bandes de deux tours se liraient comme une delamination du bord.
    dix = next((x for x in bandes if x["etendue"] == 10), None)
    balayage = []
    if dix is not None:
        g = grille(dix["recente"])
        if g is not None:
            for f in FENETRES:
                t = tours_et_pente(g[0], g[1], bords, cx, cy, R.VOXEL_UM, fenetre_tours=f)
                if t.get("pente_um_par_tour") is not None:
                    balayage.append({"fenetre_tours": f, "pente_um_par_tour":
                                     t["pente_um_par_tour"], "lignes": t["lignes"]})

    longues = [x for x in lignes if x["etendue"] >= TOURS_MINIMUM
               and x["pente_um_par_tour"] is not None]
    courtes = [x for x in lignes if x["etendue"] < TOURS_MINIMUM
               and x["pente_um_par_tour"] is not None]
    ecarts = [abs(x["ecart_tours"]) for x in lignes]
    return {
        "fragment": R.FRAGMENT, "voxel_um": R.VOXEL_UM,
        "tours_minimum": TOURS_MINIMUM,
        "orientation_de_la_grille": orient,
        "bandes": len(lignes),
        "lignes": lignes,
        # ⭐⭐⭐ L'ETENDUE DECLAREE EST LE NOMBRE DE TOURS.
        "letendue_est_le_nombre_de_tours": {
            "ecart_median_tours": round(float(np.median([x["ecart_tours"] for x in lignes])), 2),
            "bandes_a_moins_dun_dixieme_de_tour": sum(1 for e in ecarts if e < 0.1),
            "pire_ecart": round(float(max(ecarts)), 2),
            "la_pire": next(f"w{x['de']:03d}-{x['a']:03d}" for x in lignes
                            if abs(x["ecart_tours"]) == max(ecarts)),
        },
        # ⭐⭐ LE PAS, lu sur les bandes assez longues pour le porter.
        "pas_sur_les_bandes_longues_um": {
            "bandes": len(longues),
            "median": round(float(np.median([x["pente_um_par_tour"] for x in longues])), 1),
            "min": round(float(min(x["pente_um_par_tour"] for x in longues)), 1),
            "max": round(float(max(x["pente_um_par_tour"] for x in longues)), 1),
        } if longues else {},
        # ⚠⚠⚠ CE QUE LES BANDES COURTES RENDENT, publie a cote pour que la retractation soit
        # LISIBLE plutot qu'affirmee.
        "pas_sur_les_bandes_courtes_um": {
            "bandes": len(courtes),
            "median": round(float(np.median([x["pente_um_par_tour"] for x in courtes])), 1),
        } if courtes else {},
        "balayage_de_fenetre_sur_une_seule_bande": balayage,
        "le_gradient_est_un_artefact": bool(
            len(balayage) >= 3
            and balayage[-1]["pente_um_par_tour"] > 4 * balayage[0]["pente_um_par_tour"]),
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- la mecanique, sur une spirale fabriquee dont on connait le pas -----------------------
    # ⚠⚠ UNE SPIRALE A PAS CONNU, dans une grille : lignes iso-z, colonnes le long de l'axe.
    PAS = 0.2   # mm par tour
    H, W = 40, 900
    th = np.linspace(0.0, 8 * 2 * np.pi, W)
    a = np.zeros((H, W, 3))
    for r in range(H):
        rr = 5.0 + PAS * th / (2 * np.pi)
        a[r, :, 0] = 1000.0 + rr * np.cos(th) / 0.045532
        a[r, :, 1] = 2000.0 + rr * np.sin(th) / 0.045532
        a[r, :, 2] = 100.0 + r * 50.0
    ok = np.ones((H, W), dtype=bool)
    o = orientation(a, ok, 45.532)
    v("les lignes de la grille fabriquée sont iso-z", o["les_lignes_sont_iso_z"], str(o))
    bords = np.linspace(0.0, 100.0 + H * 50.0 + 1.0, 9)
    cx = np.full(8, 1000.0)
    cy = np.full(8, 2000.0)
    t = tours_et_pente(a, ok, bords, cx, cy, 45.532)
    v("le nombre de tours est retrouvé", abs(t["tours_median"] - 8.0) < 0.05,
      str(t["tours_median"]))
    v("... et le pas fabriqué est retrouvé",
      abs(t["pente_um_par_tour"] - PAS * 1000) < 0.05 * PAS * 1000,
      f"{t['pente_um_par_tour']} pour {PAS * 1000} attendu")
    # ⚠ Un cercle parfait ne gonfle RIEN, quelle que soit la fenetre : c'est le plancher, et
    # sans lui on ne saurait pas si l'ajustement lui-meme est biaise.
    rond = tours_et_pente(a, ok, bords, cx, cy, 45.532, fenetre_tours=1)
    v("une section circulaire ne gonfle pas la pente, même sur un tour",
      abs(rond["pente_um_par_tour"] - PAS * 1000) < 0.02 * PAS * 1000,
      f"{rond['pente_um_par_tour']} pour {PAS * 1000}")
    # ⚠⚠⚠ MA PREMIERE EXPLICATION ETAIT FAUSSE, ET LA FIXTURE LE GARDE. Une section OVALE ne
    # gonfle pas la pente, elle la DEGONFLE : un `cos(2t)` fait deux periodes par tour, donc il
    # s'annule meme sur une fenetre d'un tour. Garder ce controle empeche de re-proposer cette
    # explication.
    ovale = a.copy()
    for r in range(H):
        rr = (5.0 + PAS * th / (2 * np.pi)) * (1.0 + 0.25 * np.cos(2 * th))
        ovale[r, :, 0] = 1000.0 + rr * np.cos(th) / 0.045532
        ovale[r, :, 1] = 2000.0 + rr * np.sin(th) / 0.045532
    o8 = tours_et_pente(ovale, ok, bords, cx, cy, 45.532, fenetre_tours=8)
    o1 = tours_et_pente(ovale, ok, bords, cx, cy, 45.532, fenetre_tours=1)
    v("une section ovale ne gonfle PAS la pente sur un tour",
      o1["pente_um_par_tour"] < o8["pente_um_par_tour"],
      f"{o1['pente_um_par_tour']} contre {o8['pente_um_par_tour']} — "
      "ma première explication, réfutée")
    # ⚠⚠ UN CENTRE DECALE, LUI, GONFLE — dans le bon sens, mais pas de la bonne ampleur. Les
    # deux moities sont assertees : le sens, et l'insuffisance.
    decale = np.full(8, 1000.0 + 2.0 / 0.045532)
    d8 = tours_et_pente(a, ok, bords, decale, cy, 45.532, fenetre_tours=8)
    d1 = tours_et_pente(a, ok, bords, decale, cy, 45.532, fenetre_tours=1)
    v("un centre décalé gonfle la pente sur un tour",
      d1["pente_um_par_tour"] > 1.2 * d8["pente_um_par_tour"],
      f"{d1['pente_um_par_tour']} contre {d8['pente_um_par_tour']}")
    # ⚠⚠⚠ MAIS PAS ASSEZ : deux millimetres de decalage rendent ~270 µm quand la donnee reelle
    # en rend 1817. La cause reste donc NON ETABLIE, et le controle tient sans elle.
    v("... mais pas de l'ampleur observée sur les données réelles",
      d1["pente_um_par_tour"] < 400.0,
      f"{d1['pente_um_par_tour']} — il faudrait des dizaines de mm pour atteindre 1817")

    r = mesurer()
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    # --- les donnees reelles ------------------------------------------------------------------
    o = r["orientation_de_la_grille"]
    v("les lignes de grille du fragment sont iso-z", o["les_lignes_sont_iso_z"], str(o))
    e = r["letendue_est_le_nombre_de_tours"]
    # ⭐⭐⭐ LE FAIT : le nom d'une bande est sa geometrie.
    v("l'étendue déclarée EST le nombre de tours mesuré",
      abs(e["ecart_median_tours"]) < 0.05, str(e))
    v("... sur la quasi-totalité des bandes",
      e["bandes_a_moins_dun_dixieme_de_tour"] >= r["bandes"] - 2, str(e))
    # ⚠ L'exception est NOMMEE plutot que lissee.
    v("... et l'exception est nommée", e["pire_ecart"] > 1.0 and e["la_pire"], str(e))
    # ⭐⭐ LE PAS, et son accord avec l'atlas par un chemin independant.
    p = r["pas_sur_les_bandes_longues_um"]
    v("le pas lu sur les bandes longues est de l'ordre de l'atlas",
      150.0 < p["median"] < 260.0, f"{p} contre l'atlas 182,4 (p25 134,4 · p75 259,2)")
    # ⚠⚠⚠ LA RETRACTATION, MESUREE : le gradient est l'estimateur.
    bal = r["balayage_de_fenetre_sur_une_seule_bande"]
    v("le balayage de fenêtre tourne sur une seule bande", len(bal) >= 4, str(len(bal)))
    v("... et la pente y gonfle quand la fenêtre rétrécit",
      r["le_gradient_est_un_artefact"],
      str([(x["fenetre_tours"], x["pente_um_par_tour"]) for x in bal]))
    # ⚠⚠ ET LES BANDES COURTES RENDENT BIEN LE CHIFFRE ABERRANT, ce qui est la moitie qui rend
    # la retractation lisible : sans lui, on ne verrait pas ce qui a failli etre publie.
    c = r["pas_sur_les_bandes_courtes_um"]
    v("les bandes courtes rendent un pas nettement plus grand",
      c["median"] > 2 * p["median"], f"{c['median']} contre {p['median']}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    r = mesurer()
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 1
    o = r["orientation_de_la_grille"]
    print(f"{r['fragment']} · {r['bandes']} bandes · une ligne de grille varie de "
          f"{o['ecart_type_z_le_long_dune_ligne_mm']} mm en z, une colonne de "
          f"{o['ecart_type_z_le_long_dune_colonne_mm']} mm")
    print(f"  → les lignes sont "
          f"{'ISO-Z, la pente est lue à hauteur constante' if o['les_lignes_sont_iso_z'] else '⛔ PAS iso-z'}\n")
    print(f"{'bande':>10} {'ét.':>4} {'tours':>7} {'écart':>7} {'pente µm/tour':>15}")
    for x in r["lignes"]:
        marque = "" if x["etendue"] >= r["tours_minimum"] else "   ⚠ trop court pour mesurer"
        print(f"  w{x['de']:03d}-{x['a']:03d} {x['etendue']:>4} {x['tours_median']:>7.2f} "
              f"{x['ecart_tours']:>+7.2f} {x['pente_um_par_tour']:>15.1f}{marque}")
    e = r["letendue_est_le_nombre_de_tours"]
    print(f"\n⭐⭐⭐ L'ÉTENDUE DÉCLARÉE EST LE NOMBRE DE TOURS — écart médian "
          f"{e['ecart_median_tours']:+.2f} tour, {e['bandes_a_moins_dun_dixieme_de_tour']}/"
          f"{r['bandes']} bandes à moins d'un dixième de tour")
    print(f"   ⚠ une exception : {e['la_pire']}, {e['pire_ecart']:.2f} tour d'écart")
    p_ = r["pas_sur_les_bandes_longues_um"]
    c_ = r["pas_sur_les_bandes_courtes_um"]
    print(f"\n⭐⭐ LE PAS, sur les {p_['bandes']} bandes d'au moins {r['tours_minimum']} tours : "
          f"{p_['median']:.0f} µm ({p_['min']:.0f} à {p_['max']:.0f})")
    print(f"   l'atlas winding-ruler publie 182,4 µm — deux chemins indépendants s'accordent")
    print(f"\n⚠⚠⚠ RÉTRACTÉ AVANT PUBLICATION — les {c_['bandes']} bandes courtes rendent "
          f"{c_['median']:.0f} µm, ce qui se lirait comme une délamination du bord.")
    print("   contrôle sur UNE SEULE bande de dix tours, donc à pas constant par construction :")
    for x in r["balayage_de_fenetre_sur_une_seule_bande"]:
        print(f"     fenêtre de {x['fenetre_tours']:>2} tour(s) → "
              f"{x['pente_um_par_tour']:>7.1f} µm")
    print("   ⭐ RÈGLE : on ne mesure pas le pas d'un enroulement sur un arc court.")
    print("   ⚠⚠ la CAUSE n'est pas établie : une section ovale DÉGONFLE la pente, un centre")
    print("      décalé la gonfle mais d'un dixième de ce qu'il faudrait. Le contrôle tient")
    print("      sans elle — reproduire un biais sur des données dont on connaît la réponse")
    print("      n'exige pas de l'expliquer pour le réfuter.")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
