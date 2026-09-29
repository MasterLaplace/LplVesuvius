"""Le texte du segment suit-il la chaîne de `248` au-delà du premier saut, là où le segment repasse sur elle ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE ENCRE NE SOIT LUE SUR UN SAUT AU-DELÀ DU PREMIER, ET AVANT QUE SES SURFACES
NE SOIENT PRODUITES. Ce qui était vu avant d'écrire : tout ce que `247`, `248`, `276` et `296` publient. `296` montre que, sur
six blocs choisis sans l'encre, la spire que le premier saut produit porte le texte du segment là où il repasse : 0,8331,
contre 0,1166 et 0,1037 pour ses deux témoins (`R4-F477`). `248` §6 montre que le segment ne porte presque pas de troisième
couche : il ne juge, par sa géométrie, que deux sauts (`R4-F416`).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P96`. Dérouler demande des dizaines de sauts, et un saut raté est définitif. Le juge
d'encre de `296` ne sait rien du transfert : c'est le segment lui-même, un tour plus loin sur sa surface, et sa carte d'encre
publiée. Porté sur les sauts suivants de la chaîne, il dit, par ce que la surface produite porte, si la chaîne tient la feuille.

## Ce qui est fait

- **La chaîne** est celle de `248`, le témoin de `276` : `m7`, du côté plus, quatre sauts, chacun parti de la surface que le
  précédent a produite, le long de sa normale recalculée, sans correction. Elle doit redonner les sauts publiés par `248`
  compte pour compte, et son premier saut doit être la spire produite de `275` et `296`, point pour point ; sinon la mesure est
  indécidable.
- **Les surfaces** des sauts 2, 3 et 4 sont écrites en maillage, comme `280` écrit son deuxième saut, et rendues en piles
  depuis le miroir, comme `275`.
- **Le juge** est celui de `296`, sans rien y changer : pour chaque point du maillage du saut, le point du segment le plus proche
  en 3D parmi ceux à plus de 30 mailles de lui sur la surface ; la carte publiée, réduite 8 fois, lue à ce vis-à-vis ; notre
  lecture de la pile, par le même modèle, réduite à la même échelle ; la corrélation de Pearson là où le vis-à-vis est à moins
  d'un demi-feuillet (36 voxels).
- **Trois témoins**, sur exactement les mêmes pixels que la mesure :
  1. la carte sous le bloc lui-même, le texte de la spire de départ, comme `296` ;
  2. la carte au vis-à-vis décalé de 64 pixels de carte, comme `296` ;
  3. ⭐ **la carte au vis-à-vis du saut précédent**, au même point de la chaîne : le texte un tour en arrière. Un saut qui
     n'a pas avancé est resté sur la feuille du saut d'avant, et son vis-à-vis est le même que le sien : ce témoin l'égale.
     Au premier saut, le saut précédent est le segment lui-même, et ce témoin est le premier.

## Les blocs, déclarés avant de lire

Pour chaque saut, les six blocs candidats de `257` où le plus de pixels de carte ont leur vis-à-vis à moins d'un
demi-feuillet ; à égalité, l'ordre des blocs. Ils sont choisis sur les seuls maillages (`--preparer`). ⚠ Ce n'est pas la
règle de `296`, qui prenait la plus grande part : sur un saut où peu de points ont un vis-à-vis, une part se prend sur une
poignée de points, et un bloc de trois points proches aurait la part 1. Le premier saut n'est pas rechoisi : c'est celui de
`296`, ses six blocs et ses lectures.

Un saut dont les six blocs, comptés sur la géométrie seule, ont moins de 10 000 pixels à moins d'un demi-feuillet n'est ni
rendu ni lu : le juge ne le voit pas, et il est indécidable.

## Les issues, saut par saut, exclusives

- la corrélation au vis-à-vis dépasse ses trois témoins : **le saut porte le texte du segment là où il repasse** ;
- sinon : il ne le porte pas ;
- indécidable si moins de 10 000 pixels de carte sont jugés.

## L'issue de la tranche, qui répond à `R4-P96`

- **la chaîne perd le texte au saut h** : le premier saut, à partir du deuxième, qui ne le porte pas ;
- sinon, **le texte suit la chaîne jusqu'au saut H**, le dernier saut décidable ;
- indécidable si l'étalon de `296` ne tient plus (sous 0,8), si `296` ne se redonne pas, si la chaîne ne redonne pas `248`, si
  son premier saut n'est pas la spire produite, si le contrôle du rendu n'est pas identique voxel pour voxel, ou si le
  deuxième saut est lui-même indécidable.

## Rapporté à côté, qui ne décide rien

- la part que le juge voit : pour chaque saut et chacun des 340 blocs, la part des points dont le vis-à-vis est à moins d'un
  demi-feuillet ;
- la part des pixels jugés dont le vis-à-vis est la même feuille que celui du saut précédent (à moins de 30 mailles de lui sur
  le segment) : la géométrie de ce que le troisième témoin attrape ;
- sur les pixels jugés, ce que dit le juge géométrique de `248` au même point : la corrélation là où il dit la chaîne sur la
  bonne spire, et là où il la dit ratée ;
- la corrélation au-delà du demi-feuillet, sur les mêmes blocs.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : la chaîne là où le segment ne repasse pas, c'est-à-dire presque partout ; la chaîne
corrigée (`275`, `280`) ; l'autre côté, l'autre prédiction ; un autre segment, un autre rouleau. Les blocs sont choisis là où le
saut passe près du segment : là, il est plus probable qu'il soit juste.

Usage :
    uv run python src/nappe/le_texte_suit_il_la_chaine_au_dela_du_premier_saut.py --verifier
    uv run python src/nappe/le_texte_suit_il_la_chaine_au_dela_du_premier_saut.py --preparer
    uv run python src/nappe/le_texte_suit_il_la_chaine_au_dela_du_premier_saut.py --rendre 3
    uv run --project src/xpu --with albumentations --with zarr --with tqdm --with numcodecs --with imagecodecs \\
        python src/nappe/le_texte_suit_il_la_chaine_au_dela_du_premier_saut.py --encre
    uv run python src/nappe/le_texte_suit_il_la_chaine_au_dela_du_premier_saut.py \\
        --json docs/mesures/le_texte_suit_il_la_chaine_au_dela_du_premier_saut.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))

import le_tour_produit_porte_t_il_le_texte_du_segment as j296  # noqa: E402

LE_DOSSIER = j296.LE_DOSSIER
LE_DOSSIER_ENCRE = j296.LE_DOSSIER_ENCRE
LE_PLAN = LE_DOSSIER_ENCRE / "la_chaine_plan.json"
LE_CONTROLE = LE_DOSSIER_ENCRE / "la_chaine_controle.json"
CE_QUE_296_A_PUBLIE = RACINE / "docs" / "mesures" / "le_tour_produit_porte_t_il_le_texte_du_segment.json"
LES_SAUTS = 4
LES_SAUTS_JUGES = (2, 3, 4)
LES_BLOCS_PAR_SAUT = 6
LE_BLOC_DU_CONTROLE = (144, 176)     # le bloc de 296 où le segment repasse le plus


def la_surface(h: int) -> str:
    """Le nom de la surface du saut h ; le premier saut est la spire produite de `275`."""
    return j296.LES_SURFACES[1] if h == 1 else f"la_chaine_saut_{h}"


def la_lecture(h: int, by: int, bx: int) -> Path:
    """Le fichier où `--encre` range notre lecture d'un bloc du saut h ; le premier saut est celui de `296`."""
    return LE_DOSSIER_ENCRE / (f"partie_b_produite_{by}_{bx}.npy" if h == 1 else f"la_chaine_saut_{h}_{by}_{bx}.npy")


# ── La géométrie ───────────────────────────────────────────────────────────────────────────────────────────────────

def le_vis_a_vis_au_pixel(fl, fc, lignes, colonnes, rangee, colonne, espacement, combien: int = 1):
    """L'indice de maillage du vis-à-vis de chaque pixel de carte d'un bloc, interpolé comme `296` le lit ; NaN s'il manque."""
    from scipy.ndimage import map_coordinates

    p = j296.LE_CHUNK * j296.LE_BLOC // j296.LA_REDUCTION
    py, px = np.mgrid[0:p, 0:p * combien].astype(float)
    mr = (rangee * j296.LE_CHUNK + (py + 0.5) * j296.LA_REDUCTION) / espacement - lignes[0]
    mc = (colonne * j296.LE_CHUNK + (px + 0.5) * j296.LA_REDUCTION) / espacement - colonnes[0]
    connu = np.isfinite(fl)
    r = map_coordinates(np.where(connu, fl, -1e6), [mr, mc], order=1)
    c = map_coordinates(np.where(connu, fc, -1e6), [mr, mc], order=1)
    ok = (r >= 0) & (c >= 0)
    return np.where(ok, r, np.nan), np.where(ok, c, np.nan)


def la_meme_feuille(r, c, rp, cp, loin: float = j296.LOIN_SUR_LA_SURFACE) -> np.ndarray:
    """Vrai où le vis-à-vis d'un saut est à moins de `loin` mailles, sur le segment, de celui du saut précédent."""
    with np.errstate(invalid="ignore"):
        return np.hypot(r - rp, c - cp) <= loin


def les_pixels_proches(ref, ref_ok, pro, pro_ok, by: int, bx: int, esp: float) -> tuple[float, int]:
    """La part des points du bloc dont le vis-à-vis est à moins d'un demi-feuillet, et le nombre de pixels de carte proches."""
    lignes, colonnes = j296.les_mailles_dune_bande(by, bx, 1, esp)
    _, _, ecart = j296.les_vis_a_vis(ref, ref_ok, pro, pro_ok, lignes, colonnes)
    pix = j296.lecart_au_pixel(ecart, lignes, colonnes, by, bx, 1, esp) < j296.LE_DEMI_FEUILLET
    return j296.la_part_proche(ecart), int(pix.sum())


def les_blocs_du_saut(pixels: dict, combien: int = LES_BLOCS_PAR_SAUT) -> list[tuple[int, int]]:
    """Les `combien` blocs aux plus de pixels proches ; à égalité, dans l'ordre des blocs ; aucun bloc sans pixel proche."""
    return [b for b, n in sorted(pixels.items(), key=lambda t: (-t[1], t[0])) if n > 0][:combien]


def le_saut_se_lit(pixels: dict, blocs: list) -> bool:
    """Un saut se rend et se lit si ses blocs, comptés sur la géométrie seule, ont au moins le minimum de pixels proches."""
    return sum(pixels[b] for b in blocs) >= j296.LE_MINIMUM_DE_PIXELS


# ── La mesure d'un bloc ────────────────────────────────────────────────────────────────────────────────────────────

def mesurer_un_bloc(encre, carte, ref, ref_ok, pro, pro_ok, prec, prec_ok, by: int, bx: int, esp: float,
                    juste: np.ndarray | None = None) -> tuple[dict, dict]:
    """Notre lecture d'un bloc du saut contre la carte au vis-à-vis, et ses trois témoins, sur exactement les mêmes pixels.

    `prec` est le maillage du saut précédent ; None au premier saut, dont le saut précédent est le segment lui-même.
    `juste` est, sur la grille du maillage, le juge de `248` au même point : 1 juste, 0 raté, NaN non noté."""
    from scipy.ndimage import map_coordinates

    lignes, colonnes = j296.les_mailles_dune_bande(by, bx, 1, esp)
    fl, fc, ecart = j296.les_vis_a_vis(ref, ref_ok, pro, pro_ok, lignes, colonnes)
    petite = j296.reduire(encre)
    vis = j296.la_carte_au_vis_a_vis(carte, fl, fc, lignes, colonnes, by, bx, 1, esp)
    decale = j296.la_carte_au_vis_a_vis(carte, fl, fc, lignes, colonnes, by, bx, 1, esp, j296.LE_DECALAGE)
    dessous = j296.la_carte_sous(carte, by, bx, 1)
    r, c = le_vis_a_vis_au_pixel(fl, fc, lignes, colonnes, by, bx, esp)
    if prec is None:
        precedent = dessous.copy()
        py, px = np.mgrid[0:r.shape[0], 0:r.shape[1]].astype(float)
        rp = (by * j296.LE_CHUNK + (py + 0.5) * j296.LA_REDUCTION) / esp
        cp = (bx * j296.LE_CHUNK + (px + 0.5) * j296.LA_REDUCTION) / esp
    else:
        flp, fcp, _ = j296.les_vis_a_vis(ref, ref_ok, prec, prec_ok, lignes, colonnes)
        precedent = j296.la_carte_au_vis_a_vis(carte, flp, fcp, lignes, colonnes, by, bx, 1, esp)
        rp, cp = le_vis_a_vis_au_pixel(flp, fcp, lignes, colonnes, by, bx, esp)
    proche = j296.lecart_au_pixel(ecart, lignes, colonnes, by, bx, 1, esp) < j296.LE_DEMI_FEUILLET
    meme = la_meme_feuille(r, c, rp, cp)
    if juste is not None:
        p = j296.LE_CHUNK * j296.LE_BLOC // j296.LA_REDUCTION
        py, px = np.mgrid[0:p, 0:p].astype(float)
        mr = (by * j296.LE_CHUNK + (py + 0.5) * j296.LA_REDUCTION) / esp
        mc = (bx * j296.LE_CHUNK + (px + 0.5) * j296.LA_REDUCTION) / esp
        jg = map_coordinates(np.where(np.isfinite(juste), juste, -1.0), [mr, mc], order=0, cval=-1.0)
    else:
        jg = np.full(dessous.shape, -1.0)
    h = min(petite.shape[0], vis.shape[0], dessous.shape[0])
    w = min(petite.shape[1], vis.shape[1], dessous.shape[1])
    x = {"petite": petite, "vis": vis, "decale": decale, "dessous": dessous, "precedent": precedent, "proche": proche,
         "meme": meme, "juge": jg}
    x = {k: a[:h, :w] for k, a in x.items()}
    return lire_les_pixels(x), x


def lire_les_pixels(x: dict) -> dict:
    """La mesure et ses trois témoins sur les pixels où tout est connu, séparés par le demi-feuillet."""
    connus = np.ones(x["petite"].shape, dtype=bool)
    for k in ("petite", "vis", "decale", "dessous", "precedent"):
        connus &= np.isfinite(x[k])
    out = {}
    for nom, masque in (("a_moins_dun_demi_feuillet", x["proche"]), ("au_dela", ~x["proche"])):
        m = masque & connus
        c, n = j296.correlation(x["petite"], x["vis"], m)
        out[nom] = {"les_pixels": n, "au_vis_a_vis": c,
                    "temoin_sous_le_bloc": j296.correlation(x["petite"], x["dessous"], m)[0],
                    "temoin_decale": j296.correlation(x["petite"], x["decale"], m)[0],
                    "temoin_du_saut_precedent": j296.correlation(x["petite"], x["precedent"], m)[0]}
        if nom == "a_moins_dun_demi_feuillet":
            out[nom]["la_part_sur_la_meme_feuille_que_le_saut_precedent"] = (
                round(float(x["meme"][m].mean()), 4) if m.any() else None)
            juge = {}
            for cle, val in (("juste", 1.0), ("rate", 0.0)):
                mj = m & (x["juge"] == val)
                cj, nj = j296.correlation(x["petite"], x["vis"], mj, minimum=1000)
                juge[cle] = {"les_pixels": nj, "au_vis_a_vis": cj}
            juge["non_note"] = int((m & (x["juge"] < 0)).sum())
            out[nom]["sous_le_juge_de_248"] = juge
    return out


def reunir(morceaux: list[dict]) -> dict:
    """Les pixels de plusieurs blocs mis ensemble, puis lus comme un seul."""
    return lire_les_pixels({k: np.concatenate([m[k].ravel() for m in morceaux]) for k in morceaux[0]})


# ── Les issues ─────────────────────────────────────────────────────────────────────────────────────────────────────

LES_TEMOINS = ("temoin_sous_le_bloc", "temoin_decale", "temoin_du_saut_precedent")


def le_verdict_du_saut(reunie: dict | None) -> dict:
    """L'issue déclarée pour un saut, sur ses blocs réunis ; None si le saut n'a pas été lu."""
    b = (reunie or {}).get("a_moins_dun_demi_feuillet", {})
    c = b.get("au_vis_a_vis")
    if reunie is None or c is None or b.get("les_pixels", 0) < j296.LE_MINIMUM_DE_PIXELS \
            or any(b.get(t) is None for t in LES_TEMOINS):
        return {"lissue": "indécidable : le juge ne voit pas ce saut", "decidable": False, "porte": None}
    porte = all(c > b[t] for t in LES_TEMOINS)
    return {"lissue": "le saut porte le texte du segment là où il repasse" if porte
            else "le saut ne porte pas le texte du segment là où il repasse", "decidable": True, "porte": porte}


def le_verdict(d: dict) -> dict:
    """L'issue de la tranche, qui répond à `R4-P96`."""
    e = d.get("letalonnage", {}).get("la_correlation")
    if e is None or e < j296.LE_SEUIL_DETALONNAGE:
        return {"lissue": "indécidable : la lecture ne retrouve plus la carte publiée sur la référence", "decidable": False}
    for cle, raison in (("296_se_redonne", "296 ne se redonne pas"), ("la_chaine_redonne_248", "la chaîne ne redonne pas 248"),
                        ("le_premier_saut_est_la_spire_produite", "le premier saut n'est pas la spire produite"),
                        ("le_rendu_est_identique", "le contrôle du rendu n'est pas identique")):
        if not d.get("les_controles", {}).get(cle):
            return {"lissue": f"indécidable : {raison}", "decidable": False}
    sauts = d.get("les_sauts", {})
    if not sauts.get("2", {}).get("le_verdict", {}).get("decidable"):
        return {"lissue": "indécidable : le juge ne voit pas le deuxième saut", "decidable": False}
    dernier = 1
    for h in LES_SAUTS_JUGES:
        v = sauts.get(str(h), {}).get("le_verdict", {})
        if not v.get("decidable"):
            continue
        if not v["porte"]:
            return {"lissue": f"la chaîne perd le texte au saut {h}", "decidable": True, "le_saut": h}
        dernier = h
    return {"lissue": f"le texte suit la chaîne jusqu'au saut {dernier}, le dernier que le juge voit", "decidable": True,
            "le_saut": dernier}


# ── Les étapes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def la_chaine():
    """La chaîne de `248` (le témoin de `276`), ce qui la juge, et les contrôles qui l'autorisent."""
    from le_transfert_enchaine_tient_il_les_spires import juger_le_saut
    from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import (CE_QUE_248_A_PUBLIE, LA_PREDICTION,
                                                                                    LE_COTE, LE_SIGNE, la_reproduction,
                                                                                    les_deux_chaines)

    c = les_deux_chaines(sauts=LES_SAUTS)
    if isinstance(c, str):
        raise RuntimeError(c)
    publie = json.loads(CE_QUE_248_A_PUBLIE.read_text())["les_predictions"][LA_PREDICTION][LE_COTE]["les_sauts"]
    juges = [juger_le_saut(c["pt"][h], c["verite"][h], LE_SIGNE, h + 1) for h in range(LES_SAUTS)]
    with np.errstate(invalid="ignore"):
        ecart = float(np.nanmax(np.abs(c["temoin"][0]["le_pas"] - c["tau0"])))
    return c, la_reproduction(juges, publie), ecart


def preparer() -> dict:
    """Les surfaces des sauts, écrites en maillage ; la part que le juge voit ; les blocs de chaque saut, sur la géométrie."""
    from la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut import le_maillage_des_points
    from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import le_segment
    from la_spire_produite_se_lit_elle_dans_le_treillis import LA_MAILLE, ecrire_tifxyz
    from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, LE_SEGMENT, lire_tifxyz, telecharger
    from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import DEMI_PAS_EN_VOXELS

    t0 = time.monotonic()
    c, reproduction, ecart_premier = la_chaine()
    grille = c["sur_la_grille"]
    _, _, esp_plein = lire_tifxyz(telecharger(LE_SEGMENT, LE_CACHE))
    scale = 1.0 / (esp_plein * LA_MAILLE)
    ref, ref_ok, pro1, pro1_ok, esp = j296.les_maillages()
    maillages, identique = {1: (pro1, pro1_ok)}, None
    for h in range(1, LES_SAUTS + 1):
        q = np.stack([grille(c["temoin"][h - 1]["q"][:, a]) for a in range(3)], axis=-1)
        pts, ok = le_maillage_des_points(q)
        if h == 1:
            identique = bool(np.array_equal(ok, pro1_ok)
                             and np.array_equal(pts[ok].astype(np.float32).astype(np.float64), pro1[pro1_ok]))
            continue
        dossier = LE_DOSSIER / la_surface(h) / "maillage"
        ecrire_tifxyz(dossier, pts, ok, scale, la_surface(h))
        lu, lu_ok, _ = lire_tifxyz(dossier)
        maillages[h] = (lu, lu_ok)
    _, _, _, candidats = le_segment(LE_CACHE)
    sauts = {}
    for h in range(1, LES_SAUTS + 1):
        pro, pro_ok = maillages[h]
        parts, pixels = {}, {}
        for b in sorted(candidats):
            parts[b], pixels[b] = les_pixels_proches(ref, ref_ok, pro, pro_ok, *b, esp)
        plan_296 = json.loads(j296.LE_PLAN.read_text())
        blocs = ([tuple(b) for b in plan_296["les_blocs_de_la_partie_b"]] if h == 1 else les_blocs_du_saut(pixels))
        with np.errstate(invalid="ignore"):
            juste = np.abs(c["pt"][h - 1] - c["verite"][h - 1]) < DEMI_PAS_EN_VOXELS
        juste = np.where(np.isfinite(c["verite"][h - 1]), juste.astype(float), np.nan)
        np.save(LE_DOSSIER_ENCRE / f"la_chaine_juge_de_248_saut_{h}.npy", grille(juste))
        sauts[str(h)] = {"la_surface": la_surface(h), "les_blocs": [list(b) for b in blocs],
                         "leurs_pixels_proches": [pixels[b] for b in blocs],
                         "leurs_parts_proches": [round(parts[b], 4) for b in blocs],
                         "les_pixels_proches_des_blocs": int(sum(pixels[b] for b in blocs)),
                         "se_lit": h == 1 or le_saut_se_lit(pixels, blocs),
                         "la_part_proche_mediane": round(float(np.median(list(parts.values()))), 4),
                         "les_blocs_a_plus_de_la_moitie_proche": int(sum(p > 0.5 for p in parts.values())),
                         "les_pixels_proches_du_segment": int(sum(pixels.values())),
                         "les_points_du_maillage": int(pro_ok.sum())}
    plan = {"la_chaine_redonne_248": reproduction, "le_premier_saut_ecart_max_voxels": ecart_premier,
            "le_premier_saut_est_la_spire_produite": bool(identique and ecart_premier == 0.0),
            "les_blocs_candidats": len(candidats), "les_sauts": sauts,
            "la_regle": f"les {LES_BLOCS_PAR_SAUT} blocs aux plus de pixels de carte à moins de {j296.LE_DEMI_FEUILLET:g} "
                        "voxels de leur vis-à-vis, sur les seuls maillages ; le premier saut est celui de 296",
            "les_secondes": round(time.monotonic() - t0, 1)}
    LE_DOSSIER_ENCRE.mkdir(parents=True, exist_ok=True)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def rendre(ouvriers: int = 3) -> dict:
    """Les piles des sauts qui se lisent, depuis le miroir ; puis le contrôle du rendu, qui doit être identique."""
    from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import le_controle_du_miroir, tout_rendre
    from la_spire_produite_se_lit_elle_dans_le_treillis import LE_BLOC, le_cadre
    from la_spire_produite_se_lit_elle_dans_le_treillis import rendre as rendre_une_pile

    plan = json.loads(LE_PLAN.read_text())
    out = {}
    for h in LES_SAUTS_JUGES:
        s = plan["les_sauts"][str(h)]
        if s["se_lit"]:
            out[str(h)] = tout_rendre({tuple(b) for b in s["les_blocs"]}, ouvriers, (s["la_surface"],))
            print(f"saut {h} : {out[str(h)]}", flush=True)
    # Le contrôle : le premier saut sur le bloc de 296 où le segment repasse le plus, rendu à nouveau depuis le miroir, contre
    # la pile de 275 ; et, pour chaque saut lu, son premier bloc rendu à distance puis depuis le miroir.
    taches = [(la_surface(1), *LE_BLOC_DU_CONTROLE)]
    distance = {}
    for h in LES_SAUTS_JUGES:
        s = plan["les_sauts"][str(h)]
        if s["se_lit"]:
            by, bx = s["les_blocs"][0]
            pile = LE_DOSSIER / "la_chaine_a_distance" / f"{s['la_surface']}_{by}_{bx}"
            distance[f"{s['la_surface']}_{by}_{bx}"] = rendre_une_pile(LE_DOSSIER / s["la_surface"] / "maillage", pile,
                                                                        le_cadre(by, bx, LE_BLOC))
    miroir = le_controle_du_miroir(min(int(ouvriers), 3), tuple(taches))
    from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import les_voxels_differents

    comparees = {}
    for h in LES_SAUTS_JUGES:
        s = plan["les_sauts"][str(h)]
        if s["se_lit"]:
            by, bx = s["les_blocs"][0]
            cle = f"{s['la_surface']}_{by}_{bx}"
            pile = LE_DOSSIER / "la_chaine_a_distance" / cle
            comparees[cle] = (les_voxels_differents(LE_DOSSIER / s["la_surface"] / f"bloc_{by}_{bx}", pile)
                              if distance[cle].get("rendue") else None)
    controle = {"le_miroir_contre_275": miroir, "a_distance": distance, "a_distance_contre_le_miroir": comparees,
                "identiques": bool(miroir["identiques"]) and all(v == 0 for v in comparees.values())}
    LE_CONTROLE.write_text(json.dumps(controle, ensure_ascii=False, indent=1))
    out["le_controle"] = controle
    return out


def les_lectures(plan: dict) -> list[tuple[str, tuple[int, int, int], Path]]:
    """Ce que `--encre` lit : chaque bloc de chaque saut qui se lit, à partir du deuxième."""
    out = []
    for h in LES_SAUTS_JUGES:
        s = plan["les_sauts"][str(h)]
        if s["se_lit"]:
            out += [(s["la_surface"], (by, bx, 1), la_lecture(h, by, bx)) for by, bx in s["les_blocs"]]
    return out


def les_maillages_des_sauts(plan: dict) -> dict:
    """Les maillages des sauts, relus depuis le disque."""
    from la_spire_voisine_est_elle_a_un_pas import lire_tifxyz

    ref, ref_ok, pro1, pro1_ok, esp = j296.les_maillages()
    out = {0: (ref, ref_ok), 1: (pro1, pro1_ok)}
    for h in LES_SAUTS_JUGES:
        pts, ok, _ = lire_tifxyz(LE_DOSSIER / la_surface(h) / "maillage")
        out[h] = (pts, ok)
    return out, esp


def la_reproduction_de_296(carte, maillages296) -> dict:
    """Les six blocs de `296`, remesurés par sa propre fonction sur ses lectures, contre ce qu'elle publie, bloc pour bloc."""
    publie = json.loads(CE_QUE_296_A_PUBLIE.read_text())
    refait = []
    for bl in publie["la_partie_b"]["les_blocs"]:
        by, bx = bl["le_bloc"]
        m, _ = j296.mesurer_une_bande(np.load(la_lecture(1, by, bx)), carte, maillages296, by, bx, 1)
        refait.append(m["a_moins_dun_demi_feuillet"] == bl["a_moins_dun_demi_feuillet"])
    return {"les_blocs": len(refait), "redonnes": int(sum(refait)), "reproduit": bool(refait) and all(refait)}


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(LE_PLAN.read_text())
    controle = json.loads(LE_CONTROLE.read_text()) if LE_CONTROLE.exists() else {}
    carte = j296.la_carte_publiee()
    maillages, esp = les_maillages_des_sauts(plan)
    ref, ref_ok = maillages[0]
    etalon = j296.reduire(np.load(LE_DOSSIER_ENCRE / "etalon_reference.npy"))
    publiee = j296.la_carte_sous(carte, *j296.LE_BLOC_ETALON, 1)[:etalon.shape[0], :etalon.shape[1]]
    c, n = j296.correlation(etalon, publiee)
    d = {"letalonnage": {"le_bloc": list(j296.LE_BLOC_ETALON), "la_correlation": c, "les_pixels": n}}
    r296 = la_reproduction_de_296(carte, (ref, ref_ok, *maillages[1], esp))
    d["les_controles"] = {"296_se_redonne": r296["reproduit"],
                          "la_chaine_redonne_248": all(s["reproduit"] for s in plan["la_chaine_redonne_248"]["les_sauts"]),
                          "le_premier_saut_est_la_spire_produite": plan["le_premier_saut_est_la_spire_produite"],
                          "le_rendu_est_identique": bool(controle.get("identiques")),
                          "la_reproduction_de_296": r296}
    sauts = {}
    for h in range(1, LES_SAUTS + 1):
        s = plan["les_sauts"][str(h)]
        entree = {k: s[k] for k in ("la_surface", "les_blocs", "leurs_pixels_proches", "leurs_parts_proches",
                                    "les_pixels_proches_des_blocs", "se_lit", "la_part_proche_mediane",
                                    "les_blocs_a_plus_de_la_moitie_proche", "les_pixels_proches_du_segment",
                                    "les_points_du_maillage")}
        if s["se_lit"]:
            juste = np.load(LE_DOSSIER_ENCRE / f"la_chaine_juge_de_248_saut_{h}.npy")
            prec = None if h == 1 else maillages[h - 1]
            blocs, morceaux = [], []
            for by, bx in s["les_blocs"]:
                m, x = mesurer_un_bloc(np.load(la_lecture(h, by, bx)), carte, ref, ref_ok, *maillages[h],
                                       *(prec if prec is not None else (None, None)), by, bx, esp, juste)
                blocs.append({"le_bloc": [by, bx], **m})
                morceaux.append(x)
                if h > 1 and [by, bx] == s["les_blocs"][0]:
                    np.savez_compressed(LE_DOSSIER_ENCRE / f"la_chaine_saut_{h}_pour_la_figure.npz", lue=x["petite"],
                                        au_vis_a_vis=x["vis"], precedent=x["precedent"], proche=x["proche"])
            entree["les_mesures"] = blocs
            entree["reunie"] = reunir(morceaux)
        entree["le_verdict"] = le_verdict_du_saut(entree.get("reunie")) if h > 1 else {
            "lissue": "le premier saut, celui de 296", "decidable": True, "porte": True}
        sauts[str(h)] = entree
    d["les_sauts"] = sauts
    d["le_verdict"] = le_verdict(d)
    d["decidable"] = d["le_verdict"]["decidable"]
    d["le_modele"] = {"nom": "scrollprize/ink_canonical_2um",
                      "sha256": hashlib.sha256(j296.LE_MODELE.read_bytes()).hexdigest(),
                      "les_couches": list(j296.LES_COUCHES), "la_tuile": j296.LA_TUILE, "le_pas": j296.LE_PAS_DE_TUILE}
    d["les_constantes"] = {"loin_sur_la_surface_mailles": j296.LOIN_SUR_LA_SURFACE,
                           "le_demi_feuillet_voxels": j296.LE_DEMI_FEUILLET,
                           "le_decalage_pixels_de_carte": j296.LE_DECALAGE, "la_reduction": j296.LA_REDUCTION,
                           "les_blocs_par_saut": LES_BLOCS_PAR_SAUT, "le_minimum_de_pixels": j296.LE_MINIMUM_DE_PIXELS}
    d["le_plan"] = {k: plan[k] for k in ("la_regle", "les_blocs_candidats", "le_premier_saut_ecart_max_voxels",
                                         "la_chaine_redonne_248")}
    d["le_controle_du_rendu"] = controle
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


# ── La batterie ────────────────────────────────────────────────────────────────────────────────────────────────────

def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # Un segment qui fait trois tours : trois nappes planes, à 73 voxels l'une de l'autre, portées par des colonnes éloignées.
    h, w = 10, 110
    ref = np.zeros((h, w, 3))
    ref_ok = np.zeros((h, w), dtype=bool)
    for i in range(h):
        for j in range(20):
            for t, j0 in enumerate((0, 45, 90)):
                ref[i, j + j0] = (j * 20.0, i * 20.0, 73.0 * t)
    for j0 in (0, 45, 90):
        ref_ok[:, j0:j0 + 20] = True
    un = ref.copy()
    un[..., 2] += 73.0
    un_ok = ref_ok.copy()
    un_ok[:, 20:] = False
    deux = ref.copy()
    deux[..., 2] += 146.0
    deux_ok = un_ok.copy()
    colle = un.copy()                                          # un deuxième saut resté sur la feuille du premier
    lignes, colonnes = np.arange(h), np.arange(20)
    fl1, fc1, e1 = j296.les_vis_a_vis(ref, ref_ok, un, un_ok, lignes, colonnes)
    fl2, fc2, e2 = j296.les_vis_a_vis(ref, ref_ok, deux, deux_ok, lignes, colonnes)
    flc, fcc, ec = j296.les_vis_a_vis(ref, ref_ok, colle, deux_ok, lignes, colonnes)
    v("★★★★ le vis-à-vis du deuxième saut est le troisième tour du segment, à écart nul",
      np.nanmax(e2) < 1e-9 and np.all(fc2 == np.arange(20)[None, :] + 90), f"{np.nanmax(e2)} {fc2[0, :3]}")
    v("★★★★ un deuxième saut resté sur la feuille du premier a le même vis-à-vis que lui",
      np.array_equal(fcc, fc1) and np.array_equal(flc, fl1) and np.nanmax(ec) < 1e-9)
    v("★★★ la même feuille : deux vis-à-vis à moins de 30 mailles, sur le segment",
      la_meme_feuille(fl1, fc1, flc, fcc).all() and not la_meme_feuille(fl1, fc1, fl2, fc2).any())
    esp = 160.0
    lg, cl = j296.les_mailles_dune_bande(176, 64, 1, esp)
    gl, gc = np.meshgrid(lg.astype(float), cl.astype(float), indexing="ij")
    r, c = le_vis_a_vis_au_pixel(gl + 3.0, gc - 2.0, lg, cl, 176, 64, esp)
    carte = np.add.outer(np.arange(6400.0), np.arange(4600.0) * 0.001)
    lu = j296.la_carte_au_vis_a_vis(carte, gl + 3.0, gc - 2.0, lg, cl, 176, 64, 1, esp)
    par = esp / j296.LA_REDUCTION
    from scipy.ndimage import map_coordinates
    relu = map_coordinates(carte, [r * par, c * par], order=1, cval=np.nan)
    v("★★★★ le vis-à-vis au pixel est celui où 296 lit la carte", np.nanmax(np.abs(relu - lu)) < 1e-6,
      str(np.nanmax(np.abs(relu - lu))))
    v("★★★ un vis-à-vis inconnu reste inconnu au pixel",
      np.isnan(le_vis_a_vis_au_pixel(np.full_like(gl, np.nan), gc, lg, cl, 176, 64, esp)[0]).all())
    grand = np.zeros((20, 110, 3))
    grand_ok = np.zeros((20, 110), dtype=bool)
    for i in range(20):
        for j in range(20):
            for t, j0 in enumerate((0, 45, 90)):
                grand[i, j + j0] = (j * 20.0, i * 20.0, 73.0 * t)
    for j0 in (0, 45, 90):
        grand_ok[:, j0:j0 + 20] = True
    g1, g1_ok = grand.copy(), grand_ok.copy()
    g1[..., 2] += 73.0
    g1_ok[:, 20:] = False
    g2 = grand.copy()
    g2[..., 2] += 146.0
    carte_ = np.random.default_rng(3).random((600, 3000))
    encre_ = np.random.default_rng(4).random((2048, 2048))
    m1, _ = mesurer_un_bloc(encre_, carte_, grand, grand_ok, g1, g1_ok, None, None, 0, 0, esp)
    p1 = m1["a_moins_dun_demi_feuillet"]
    v("★★★★ au premier saut, le saut précédent est le segment : son témoin est le texte sous le bloc, jamais la même feuille",
      p1["les_pixels"] > 20000 and p1["temoin_du_saut_precedent"] == p1["temoin_sous_le_bloc"]
      and p1["la_part_sur_la_meme_feuille_que_le_saut_precedent"] == 0.0, str(p1))
    m2, x2 = mesurer_un_bloc(encre_, carte_, grand, grand_ok, g2, g1_ok, g1, g1_ok, 0, 0, esp)
    p2 = m2["a_moins_dun_demi_feuillet"]
    m3, _ = mesurer_un_bloc(encre_, carte_, grand, grand_ok, g1, g1_ok, g1, g1_ok, 0, 0, esp)
    p3 = m3["a_moins_dun_demi_feuillet"]
    v("★★★★ au deuxième saut, le témoin du saut précédent lit le vis-à-vis du premier, une autre feuille",
      p2["les_pixels"] > 20000 and p2["la_part_sur_la_meme_feuille_que_le_saut_precedent"] == 0.0
      and p2["temoin_du_saut_precedent"] != p2["au_vis_a_vis"], str(p2))
    v("★★★★ un deuxième saut resté sur la feuille du premier : même feuille partout, et son témoin l'égale",
      p3["la_part_sur_la_meme_feuille_que_le_saut_precedent"] == 1.0
      and p3["temoin_du_saut_precedent"] == p3["au_vis_a_vis"], str(p3))
    pixels = {(16, 0): 500, (16, 16): 9000, (32, 0): 9000, (32, 16): 0, (48, 0): 20}
    v("★★★★ les blocs d'un saut : les plus de pixels proches, à égalité dans l'ordre, jamais un bloc sans pixel",
      les_blocs_du_saut(pixels, 4) == [(16, 16), (32, 0), (16, 0), (48, 0)])
    v("★★★★ un saut se lit s'il a assez de pixels proches, comptés sur la géométrie seule",
      le_saut_se_lit(pixels, [(16, 16), (32, 0)]) and not le_saut_se_lit(pixels, [(16, 0), (48, 0)]))
    rng = np.random.default_rng(1)
    texte = rng.random((256, 256))
    autre = rng.random((256, 256))
    proche = np.ones((256, 256), dtype=bool)
    x = {"petite": texte + 0.1 * rng.random((256, 256)), "vis": texte, "decale": np.roll(texte, 64, axis=1),
         "dessous": autre, "precedent": rng.random((256, 256)), "proche": proche, "meme": ~proche,
         "juge": np.where(np.arange(256)[None, :] < 128, 1.0, 0.0) * np.ones((256, 1))}
    m = lire_les_pixels(x)["a_moins_dun_demi_feuillet"]
    v("★★★★ un saut qui porte le texte : au-dessus de ses trois témoins",
      le_verdict_du_saut({"a_moins_dun_demi_feuillet": m})["porte"] is True, str(m))
    y = dict(x, precedent=texte)
    my = lire_les_pixels(y)["a_moins_dun_demi_feuillet"]
    v("★★★★ un saut qui n'a pas avancé égale le témoin du saut précédent : il ne porte pas",
      le_verdict_du_saut({"a_moins_dun_demi_feuillet": my})["porte"] is False, str(my))
    v("★★★ le juge de 248 sépare les pixels justes et ratés", m["sous_le_juge_de_248"]["juste"]["les_pixels"] == 128 * 256
      and m["sous_le_juge_de_248"]["rate"]["les_pixels"] == 128 * 256 and m["sous_le_juge_de_248"]["non_note"] == 0)
    z = dict(x)
    z["decale"] = x["decale"].copy()
    z["decale"][:, :10] = np.nan
    mz = lire_les_pixels(z)["a_moins_dun_demi_feuillet"]
    v("★★★★ la mesure et ses témoins sont pris sur exactement les mêmes pixels", mz["les_pixels"] == 256 * 246)
    v("★★★ trop peu de pixels : indécidable",
      le_verdict_du_saut({"a_moins_dun_demi_feuillet": dict(m, les_pixels=100)})["decidable"] is False
      and le_verdict_du_saut(None)["decidable"] is False)
    base = {"letalonnage": {"la_correlation": 0.95},
            "les_controles": {"296_se_redonne": True, "la_chaine_redonne_248": True,
                              "le_premier_saut_est_la_spire_produite": True, "le_rendu_est_identique": True}}
    oui = {"decidable": True, "porte": True}
    non = {"decidable": True, "porte": False}
    rien = {"decidable": False, "porte": None}
    tous = dict(base, les_sauts={"2": {"le_verdict": oui}, "3": {"le_verdict": oui}, "4": {"le_verdict": rien}})
    perd = dict(base, les_sauts={"2": {"le_verdict": oui}, "3": {"le_verdict": non}, "4": {"le_verdict": oui}})
    deux_ = dict(base, les_sauts={"2": {"le_verdict": rien}, "3": {"le_verdict": oui}, "4": {"le_verdict": oui}})
    v("★★★★ l'issue : le texte suit la chaîne jusqu'au dernier saut que le juge voit",
      le_verdict(tous)["lissue"].startswith("le texte suit la chaîne jusqu'au saut 3"), le_verdict(tous)["lissue"])
    v("★★★★ l'issue : la chaîne perd le texte au premier saut qui ne le porte pas",
      le_verdict(perd)["lissue"] == "la chaîne perd le texte au saut 3")
    v("★★★ l'issue : indécidable si le deuxième saut l'est", "indécidable" in le_verdict(deux_)["lissue"])
    for cle in base["les_controles"]:
        casse = json.loads(json.dumps(tous))
        casse["les_controles"][cle] = False
        v(f"★★★ l'issue : indécidable sans le contrôle « {cle} »", "indécidable" in le_verdict(casse)["lissue"])
    mal = json.loads(json.dumps(tous))
    mal["letalonnage"]["la_correlation"] = 0.5
    v("★★★ l'issue : indécidable sans étalon", "indécidable" in le_verdict(mal)["lissue"])
    lec = les_lectures({"les_sauts": {"2": {"se_lit": True, "la_surface": "la_chaine_saut_2", "les_blocs": [[16, 32]]},
                                      "3": {"se_lit": False, "la_surface": "la_chaine_saut_3", "les_blocs": [[48, 64]]},
                                      "4": {"se_lit": True, "la_surface": "la_chaine_saut_4", "les_blocs": [[80, 96]]}}})
    v("★★★ --encre ne lit que les sauts qui se lisent, sur leur propre surface",
      [(s, b) for s, b, _ in lec] == [("la_chaine_saut_2", (16, 32, 1)), ("la_chaine_saut_4", (80, 96, 1))]
      and lec[0][2].name == "la_chaine_saut_2_16_32.npy")
    v("★★ le premier saut est la spire produite de 296, ses lectures celles de 296",
      la_surface(1) == j296.LES_SURFACES[1] and la_lecture(1, 144, 176).name == "partie_b_produite_144_176.npy")

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--preparer", action="store_true", help="les surfaces des sauts et leurs blocs, sur les seuls maillages")
    p.add_argument("--rendre", type=int, default=None, metavar="OUVRIERS", help="les piles des sauts qui se lisent")
    p.add_argument("--encre", action="store_true", help="le modèle de l'équipe sur les blocs de chaque saut")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.preparer:
        print(json.dumps(preparer(), ensure_ascii=False, indent=1))
        return 0
    if a.rendre is not None:
        print(json.dumps(rendre(a.rendre), ensure_ascii=False, indent=1))
        return 0
    if a.encre:
        os.environ.setdefault("PYTORCH_ENABLE_XPU_FALLBACK", "0")
        for surface, (r, c, n), sortie in les_lectures(json.loads(LE_PLAN.read_text())):
            if sortie.exists():
                print(f"déjà lu : {sortie.name}", flush=True)
                continue
            print(json.dumps(j296.lencre(surface, r, c, n, sortie), ensure_ascii=False), flush=True)
        return 0
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(texte)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
