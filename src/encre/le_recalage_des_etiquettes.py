#!/usr/bin/env python3
"""Recaler les étiquettes infrarouges sur le segment publié — et VALIDER le recalage.

⚠⚠⚠ CE QU'IL MANQUAIT À LA CASE QUI DÉCIDE. `deux_aplatissements.py` établit que les étiquettes
de `PHerc0500P2` et les couches du régime du prix vivent sur **deux aplatissements différents**
du même fragment (27 160 × 14 990 contre 26 440 × 15 060), que leurs empreintes se recouvrent à
**Dice 0,971**, et que l'écart de rapport d'aspect vaut **3,2 %** — donc qu'une **affine** est
nécessaire et qu'une similitude ne suffit pas. Ce fichier construit cette affine.

⭐⭐⭐ ET IL LA VALIDE CONTRE UNE RÉFÉRENCE QUI NE VIENT PAS DE NOUS. Un recalage qu'on estime
soi-même et qu'on juge soi-même ne prouve rien. Ici la validation est faite en scorant la **carte
d'encre publiée par la communauté** — celle du régime de production, dont le papier de référence
montre qu'elle marche — contre les étiquettes recalées. Si l'accord est franc, le recalage est
bon **et** on obtient au passage la valeur de référence à battre. S'il ne l'est pas, on ne sait
pas si c'est le recalage ou la carte, et il faut le dire.

⚠⚠ L'AFFINE EST DIAGONALE, ET C'EST UN CHOIX QUI SE MESURE. Les deux aplatissements sont des
rectangles quasi alignés du même objet : ce qui les sépare est une **échelle par axe** plus une
translation, ce que l'écart d'aspect de 3,2 % décrit exactement. Une affine complète (avec
cisaillement et rotation) a deux paramètres de plus et ne se justifierait que si la diagonale
laissait un résidu — le Dice après recalage le dit.

⚠ Les extrémités sont prises aux **percentiles 1 et 99** des lignes et colonnes occupées, jamais
au minimum et au maximum : un seul pixel isolé — une poussière du masque, un artefact de bord —
fixerait la boîte et décalerait toute la carte.

Usage :
    uv run python src/encre/le_recalage_des_etiquettes.py --verifier
    uv run python src/encre/le_recalage_des_etiquettes.py \\
        --json docs/mesures/le_recalage_des_etiquettes.json
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
sys.path.insert(0, str(RACINE / "src" / "encre"))

SEGMENT = "20250628074500-500P2_front"
LOCAL = RACINE / "data" / "0500P2"
BASE_ETIQUETTES = ("https://dl.ash2txt.org/fragments/PHerc0500P2/paths/2um_front_surface")

COTE_VALIDATION = 1024
"""Résolution à laquelle le recalage est jugé.

⚠⚠ 1024 et non 256. `deux_aplatissements.py` compare à 256, où une case vaut ~100 µm : ça suffit
pour dire que deux silhouettes se ressemblent, pas pour dire qu'une **lettre** tombe au bon
endroit — une lettre fait ~600 µm. À 1024 une case vaut ~26 µm, donc une lettre en couvre une
vingtaine, et un décalage d'une lettre devient visible."""


def _image(nom: str) -> np.ndarray | None:
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    chemin = LOCAL / nom
    if not chemin.is_file():
        return None
    a = np.asarray(Image.open(chemin))
    return a[..., 0] if a.ndim == 3 else a


def etendue(masque: np.ndarray, quantile: float = 1.0) -> tuple[int, int, int, int]:
    """
    @brief La boîte occupée, prise aux percentiles plutôt qu'aux extrêmes.

    ⚠⚠ Un seul pixel isolé — poussière du masque, artefact de bord — fixerait un minimum ou un
    maximum et décalerait **toute** la carte recalée. Les percentiles 1 et 99 des lignes et
    colonnes occupées sont insensibles à cela, et ils rendent la même boîte qu'un min/max sur un
    masque propre : c'est le cas dégradé qu'ils changent, pas le cas normal.
    """
    lignes, colonnes = np.nonzero(masque > 0)
    if lignes.size == 0:
        return (0, masque.shape[0] - 1, 0, masque.shape[1] - 1)
    r0, r1 = np.percentile(lignes, [quantile, 100 - quantile])
    c0, c1 = np.percentile(colonnes, [quantile, 100 - quantile])
    return int(r0), int(r1), int(c0), int(c1)


def affine_par_boites(source: np.ndarray, cible: np.ndarray) -> dict:
    """
    @brief L'affine diagonale qui envoie la boîte occupée de `source` sur celle de `cible`.

    ⚠ Diagonale : une échelle par axe et une translation. C'est exactement ce qu'un écart de
    **rapport d'aspect** décrit, et c'est ce que `deux_aplatissements.py` a mesuré à 3,2 %. Un
    cisaillement ou une rotation ajouteraient deux paramètres qu'aucune mesure ne réclame — et un
    paramètre non contraint est un paramètre qui absorbe du bruit.
    """
    sr0, sr1, sc0, sc1 = etendue(source)
    tr0, tr1, tc0, tc1 = etendue(cible)
    er = (tr1 - tr0) / max(1, sr1 - sr0)
    ec = (tc1 - tc0) / max(1, sc1 - sc0)
    return dict(echelle_lignes=er, echelle_colonnes=ec,
                decalage_lignes=tr0 - sr0 * er, decalage_colonnes=tc0 - sc0 * ec,
                boite_source=[sr0, sr1, sc0, sc1], boite_cible=[tr0, tr1, tc0, tc1])


def appliquer(source: np.ndarray, transformation: dict, forme: tuple[int, int]) -> np.ndarray:
    """
    @brief `source` rendue dans la grille de la cible, par plus proche voisin.

    ⚠⚠ PLUS PROCHE VOISIN, PAS D'INTERPOLATION. Les étiquettes sont des **classes** (encre ou
    pas), pas une intensité : interpoler entre deux classes fabrique des demi-valeurs qui n'ont
    aucun sens et qu'un seuil transformerait ensuite en un halo d'encre autour de chaque trait.

    ⚠ L'échantillonnage est fait dans le sens INVERSE — pour chaque pixel de la cible, quel pixel
    de la source ? — parce que le sens direct laisse des trous partout où l'échelle dilate.
    """
    lignes = np.arange(forme[0], dtype=float)
    colonnes = np.arange(forme[1], dtype=float)
    sl = (lignes - transformation["decalage_lignes"]) / transformation["echelle_lignes"]
    sc = (colonnes - transformation["decalage_colonnes"]) / transformation["echelle_colonnes"]
    li = np.clip(np.round(sl).astype(int), 0, source.shape[0] - 1)
    ci = np.clip(np.round(sc).astype(int), 0, source.shape[1] - 1)
    # ⚠ Ce qui tombe HORS de la source est mis à zéro plutôt que rabattu sur le bord : rabattre
    # étalerait la dernière ligne d'étiquettes sur toute la marge, donc inventerait de l'encre.
    dedans_l = (sl >= 0) & (sl <= source.shape[0] - 1)
    dedans_c = (sc >= 0) & (sc <= source.shape[1] - 1)
    out = source[np.ix_(li, ci)].astype(float)
    out[~dedans_l, :] = 0.0
    out[:, ~dedans_c] = 0.0
    return out


def _reduire(a: np.ndarray, cote: int) -> np.ndarray:
    """Une carte ramenée à une grille carrée par moyenne de blocs."""
    h, w = a.shape
    lignes = np.linspace(0, h, cote + 1).astype(int)
    colonnes = np.linspace(0, w, cote + 1).astype(int)
    out = np.zeros((cote, cote), dtype=float)
    for i in range(cote):
        bande = a[lignes[i]:max(lignes[i] + 1, lignes[i + 1])]
        for j in range(cote):
            bloc = bande[:, colonnes[j]:max(colonnes[j] + 1, colonnes[j + 1])]
            out[i, j] = float(bloc.mean()) if bloc.size else 0.0
    return out


def carte_publiee_reduite(recette: str = "new_canon") -> tuple[np.ndarray, str] | None:
    """
    @brief Une des deux cartes d'encre publiées du segment, en version réduite ×8.

    ⚠ Le segment en publie **deux**, de deux recettes différentes. Prendre « la » carte sans dire
    laquelle rendrait le résultat irreproductible : le nom retenu est rendu avec elle.
    """
    from PIL import Image

    from zarr_depth import BUCKET, get  # noqa: PLC0415

    import la_case_vide as cv  # noqa: PLC0415

    Image.MAX_IMAGE_PIXELS = None
    for _, fiche in cv._charger().items():
        for sid, seg in fiche.get("segments", {}).items():
            if seg.get("long_id", sid) != SEGMENT:
                continue
            for e in seg.get("data", []):
                chemin = e.get("origins", [{}])[0].get("path", "")
                if (e.get("type") == "ink-detection-downsampled"
                        and recette in chemin and "2.215um" in chemin):
                    brut = get(f"{BUCKET}/{chemin}", 300)
                    if brut is None:
                        return None
                    a = np.asarray(Image.open(io.BytesIO(brut)).convert("L"), dtype=float)
                    return a, chemin.split("/")[-1]
    return None


def dice(a: np.ndarray, b: np.ndarray) -> float:
    a_, b_ = a > 0.5, b > 0.5
    s = a_.sum() + b_.sum()
    return float(2.0 * (a_ & b_).sum() / s) if s else 0.0


def mesurer(recette: str = "new_canon", graine: int = 42) -> dict:
    from le_nul_verso import aire_sous_la_courbe  # noqa: PLC0415

    masque = _image("500P2_mask.png")
    etiquettes = _image("500P2_inklabels.png")
    if masque is None or etiquettes is None:
        raise SystemExit(f"étiquettes absentes de {LOCAL} — les télécharger d'abord")
    publiee = carte_publiee_reduite(recette)
    if publiee is None:
        raise SystemExit("carte publiée introuvable dans l'index")
    carte, nom_carte = publiee
    # ⚠ L'empreinte du segment vient de sa carte publiée réduite, faute de masque publié : c'est
    # « là où le détecteur a rendu quelque chose », donc un minorant de la surface.
    empreinte = (carte > 0).astype(float)

    t = affine_par_boites(masque, empreinte)
    masque_recale = appliquer(masque, t, empreinte.shape)
    etiquettes_recalees = appliquer(etiquettes, t, empreinte.shape)

    avant = dice(_reduire(masque, COTE_VALIDATION), _reduire(empreinte, COTE_VALIDATION))
    apres = dice(_reduire(masque_recale, COTE_VALIDATION),
                 _reduire(empreinte, COTE_VALIDATION))

    # ⚠⚠⚠ LA VALIDATION : la carte publiée classe-t-elle les étiquettes recalées ? Le seuil vient
    # des ÉTIQUETTES (encre ou pas), donc l'AUC répond exactement à « cette carte trouve-t-elle
    # cette encre-là ».
    encre = etiquettes_recalees > 0.5
    dans = (empreinte > 0.5) & np.isfinite(carte)
    a, b = carte[dans & encre].ravel(), carte[dans & ~encre].ravel()
    auc = aire_sous_la_courbe(a, b) if (a.size >= 100 and b.size >= 100) else None
    rng = np.random.default_rng(graine)
    melange = rng.permutation(np.concatenate([a, b]))
    temoin = (aire_sous_la_courbe(melange[:a.size], melange[a.size:])
              if a.size >= 100 and b.size >= 100 else None)
    return dict(segment=SEGMENT, recette=recette, carte_publiee=nom_carte,
                forme_etiquettes=list(etiquettes.shape), forme_empreinte=list(empreinte.shape),
                transformation={k: v for k, v in t.items()},
                dice_avant=avant, dice_apres=apres,
                part_encre=float(encre[dans].mean()) if dans.any() else 0.0,
                pixels_encre=int(a.size), pixels_fond=int(b.size),
                auc_carte_publiee=auc, auc_temoin_melange=temoin)


ZARRS = {
    "prix": ("PHerc0500P2/segments/20250628074500-500P2_front/surface-volumes/"
             "9.362um-1.2m-113keV-volume-20250820143440.zarr", 9.362),
    "production": ("PHerc0500P2/segments/20250628074500-500P2_front/surface-volumes/"
                   "2.215um-0.4m-111keV-volume-20250526151718.zarr", 2.215),
}
"""Les deux piles publiées du segment, avec leur taille de voxel.

⚠⚠⚠ LA PRODUCTION N'EST PAS UN CONFORT, C'EST LE CONTRÔLE OBLIGATOIRE. Une AUC de 0,254 contre
les étiquettes est aussi loin du hasard que 0,746, mais **à l'envers** — donc c'est du signal
inversé, pas une absence de signal. Deux lectures s'ensuivent et elles sont incompatibles : soit
notre détecteur s'inverse **au régime du prix**, soit il s'inverse **sur ce fragment**, à tous
les régimes. Poser exactement la même question à la pile de production est la seule façon de
trancher, et sans elle le chiffre du régime du prix ne dit rien du régime."""

ZARR_PRIX = ZARRS["prix"][0]
CARTES = RACINE / "docs" / "mesures" / "case_vide_cartes"


def fenetre_la_plus_encree(etiquettes_ds8: np.ndarray, forme_prix: list[int],
                           taille: int = 512) -> dict:
    """
    @brief Où poser la fenêtre au régime du prix : là où il y a le plus d'encre ÉTIQUETÉE.

    ⚠⚠⚠ CE N'EST PAS DU CHOIX DE RÉSULTAT, et la différence tient à ce qui décide. La fenêtre
    est choisie sur les **étiquettes**, qui sont la vérité terrain et ne viennent pas de nous ;
    elle n'est pas choisie sur notre sortie. Choisir sur notre sortie serait chercher là où l'on
    gagne — choisir sur la vérité terrain, c'est chercher là où la question **a un sens**, parce
    qu'une fenêtre sans encre étiquetée n'a aucun positif et ne peut rien mesurer.

    ⚠ Balayage à pas grossier sur la carte réduite : à ce stade on cherche une région, pas un
    pixel, et un balayage fin coûterait cent fois plus pour la même réponse.
    """
    fr = etiquettes_ds8.shape[0] / forme_prix[1]
    fc = etiquettes_ds8.shape[1] / forme_prix[2]
    pas_ds8 = max(2, int(round(taille * fr)))
    integrale = np.cumsum(np.cumsum(etiquettes_ds8 > 0.5, axis=0), axis=1)

    def somme(i, j, h, w):
        i1, j1 = min(i + h, integrale.shape[0]) - 1, min(j + w, integrale.shape[1]) - 1
        total = integrale[i1, j1]
        if i > 0:
            total -= integrale[i - 1, j1]
        if j > 0:
            total -= integrale[i1, j - 1]
        if i > 0 and j > 0:
            total += integrale[i - 1, j - 1]
        return int(total)

    meilleur, ou = -1, (0, 0)
    pas = max(1, pas_ds8 // 4)
    for i in range(0, max(1, integrale.shape[0] - pas_ds8 + 1), pas):
        for j in range(0, max(1, integrale.shape[1] - pas_ds8 + 1), pas):
            n = somme(i, j, pas_ds8, pas_ds8)
            if n > meilleur:
                meilleur, ou = n, (i, j)
    return dict(top=int(round(ou[0] / fr)), left=int(round(ou[1] / fc)),
                pixels_encre_ds8=meilleur, pas_ds8=pas_ds8,
                part_encre=meilleur / max(1, pas_ds8 * pas_ds8))


def mesurer_au_regime_du_prix(taille: int = 512, graine: int = 42,
                              regime: str = "prix") -> dict:
    """
    @brief La mesure décisive : notre détecteur à 9,362 µm, contre les étiquettes infrarouges.

    ⚠⚠ La chaîne entière est celle qui vient d'être validée : étiquettes → affine → repère de la
    carte réduite, et fenêtre du régime du prix → même repère. Deux mises à l'échelle, toutes
    deux dérivées de formes réelles, aucune écrite à la main.
    """
    import tempfile

    from le_nul_verso import (COUCHES_LUES, EXTRACTEUR, SURFACE_DANS_LA_FENETRE,  # noqa: PLC0415
                              _inference, _lancer, aire_sous_la_courbe, prendre_le_verrou)
    from zarr_depth import BUCKET, get  # noqa: PLC0415

    masque, etiquettes = _image("500P2_mask.png"), _image("500P2_inklabels.png")
    publiee = carte_publiee_reduite()
    if masque is None or etiquettes is None or publiee is None:
        raise SystemExit("étiquettes ou carte publiée absentes")
    carte, _ = publiee
    empreinte = (carte > 0).astype(float)
    t = affine_par_boites(masque, empreinte)
    etiquettes_ds8 = appliquer(etiquettes, t, empreinte.shape)

    zarr, voxel_um = ZARRS[regime]
    forme_prix = json.loads(get(f"{BUCKET}/{zarr}/0/.zarray", 60))["shape"]
    f = fenetre_la_plus_encree(etiquettes_ds8, forme_prix, taille)
    # ⚠⚠ La surface tracée est au MILIEU de la dalle par construction, et le modèle la veut à
    # sa 17ᵉ image sur 26 (`12` §1). À 28 couches les deux coïncident ; à 118 non, et prendre le
    # centre de la PILE au lieu du centre de la FENÊTRE décalerait la surface de neuf couches.
    milieu = (forme_prix[0] - 1) // 2
    debut = max(0, min(forme_prix[0] - COUCHES_LUES, milieu - SURFACE_DANS_LA_FENETRE))

    _verrou = prendre_le_verrou()  # noqa: F841
    with tempfile.TemporaryDirectory() as tmp:
        couches = Path(tmp) / "couches"
        code, texte = _lancer(
            ["uv", "run", "python", str(EXTRACTEUR), zarr, "--sortie", str(couches),
             "--top", str(f["top"]), "--left", str(f["left"]),
             "--hauteur", str(taille), "--largeur", str(taille)], 3600)
        if code != 0:
            raise SystemExit(f"extraction échouée : {texte.strip()[-200:]}")
        CARTES.mkdir(parents=True, exist_ok=True)
        sortie = CARTES / f"{SEGMENT}_{regime}.npy"
        rendu = _inference(couches, debut, taille, sortie)
    if not rendu or rendu.get("echec"):
        raise SystemExit(f"inférence échouée : {(rendu or {}).get('echec')}")

    nous = np.load(sortie)
    fr = etiquettes_ds8.shape[0] / forme_prix[1]
    fc = etiquettes_ds8.shape[1] / forme_prix[2]
    r0, c0 = int(round(f["top"] * fr)), int(round(f["left"] * fc))
    h = max(2, int(round(taille * fr)))
    region = etiquettes_ds8[r0:r0 + h, c0:c0 + h]
    lignes = np.linspace(0, nous.shape[0] - 1, region.shape[0]).round().astype(int)
    colonnes = np.linspace(0, nous.shape[1] - 1, region.shape[1]).round().astype(int)
    reduite = nous[np.ix_(lignes, colonnes)]
    ok = np.isfinite(reduite)
    a = reduite[ok & (region > 0.5)].ravel()
    b = reduite[ok & (region <= 0.5)].ravel()
    auc = aire_sous_la_courbe(a, b) if (a.size >= 100 and b.size >= 100) else None
    rng = np.random.default_rng(graine)
    tout = rng.permutation(np.concatenate([a, b]))
    temoin = (aire_sous_la_courbe(tout[:a.size], tout[a.size:])
              if a.size >= 100 and b.size >= 100 else None)
    # ⚠⚠⚠ LA RÉFÉRENCE SUR LA **MÊME** FENÊTRE, ET C'EST UNE CORRECTION PAYÉE. J'ai d'abord
    # comparé notre AUC sur une fenêtre au **0,756** de la carte publiée sur TOUTE l'empreinte.
    # Mesuré : sur cette fenêtre-là, la carte publiée ne fait que **0,451**. La fenêtre, choisie
    # sur la densité d'étiquettes, est une région où la référence elle-même échoue — donc les
    # deux nombres ne se comparaient pas, et l'écart que j'aurais publié aurait été celui de
    # deux régions, pas de deux régimes.
    #
    # ⚠⚠ Toute AUC rendue ici vient donc APPARIÉE : notre carte et la carte publiée, sur les
    # mêmes pixels, contre les mêmes étiquettes. C'est la différence qui a un sens, jamais la
    # valeur seule.
    ref = carte[r0:r0 + h, c0:c0 + h]
    ok_ref = np.isfinite(ref) & (ref > 0)
    ra = ref[ok_ref & (region > 0.5)].ravel()
    rb = ref[ok_ref & (region <= 0.5)].ravel()
    auc_ref = (aire_sous_la_courbe(ra, rb) if (ra.size >= 100 and rb.size >= 100) else None)
    return dict(segment=SEGMENT, regime=regime, zarr=zarr, fenetre=f,
                debut=debut, couches=forme_prix[0], taille=taille, voxel_um=voxel_um,
                fenetre_um=COUCHES_LUES * voxel_um,
                encre=dict(minimum=rendu["minimum"], mediane=rendu["mediane"],
                           maximum=rendu["maximum"]),
                pixels_encre=int(a.size), pixels_fond=int(b.size),
                auc_prix=auc, auc_temoin_melange=temoin,
                auc_publiee_meme_fenetre=auc_ref,
                ecart_apparie=(None if auc is None or auc_ref is None else auc - auc_ref))


def apparier_depuis_la_carte(dossier: dict) -> dict:
    """
    @brief Recalcule l'appariement d'une mesure déjà rendue, sans refaire l'inférence.

    ⚠⚠ EXISTE PARCE QUE LA RÉFÉRENCE APPARIÉE A ÉTÉ AJOUTÉE **APRÈS** UNE PREMIÈRE CAMPAGNE, et
    qu'une inférence coûte dix minutes. Les cartes sont gardées et déterministes, donc tout ce
    qui s'en dérive doit pouvoir être recalculé sans les refaire — sinon la moindre grandeur
    ajoutée coûte une campagne, et on finit par la calculer au terminal.
    """
    from le_nul_verso import aire_sous_la_courbe  # noqa: PLC0415
    from zarr_depth import BUCKET, get  # noqa: PLC0415

    masque, etiquettes = _image("500P2_mask.png"), _image("500P2_inklabels.png")
    publiee = carte_publiee_reduite()
    if masque is None or etiquettes is None or publiee is None:
        raise SystemExit("étiquettes ou carte publiée absentes")
    carte, _ = publiee
    empreinte = (carte > 0).astype(float)
    t = affine_par_boites(masque, empreinte)
    etiquettes_ds8 = appliquer(etiquettes, t, empreinte.shape)
    forme = json.loads(get(f"{BUCKET}/{dossier['zarr']}/0/.zarray", 60))["shape"]
    fr = etiquettes_ds8.shape[0] / forme[1]
    fc = etiquettes_ds8.shape[1] / forme[2]
    r0 = int(round(dossier["fenetre"]["top"] * fr))
    c0 = int(round(dossier["fenetre"]["left"] * fc))
    h = max(2, int(round(dossier["taille"] * fr)))
    region = etiquettes_ds8[r0:r0 + h, c0:c0 + h]
    ref = carte[r0:r0 + h, c0:c0 + h]
    ok = np.isfinite(ref) & (ref > 0)
    ra = ref[ok & (region > 0.5)].ravel()
    rb = ref[ok & (region <= 0.5)].ravel()
    auc_ref = (aire_sous_la_courbe(ra, rb) if (ra.size >= 100 and rb.size >= 100) else None)
    return dict(auc_publiee_meme_fenetre=auc_ref,
                ecart_apparie=(None if dossier.get("auc_prix") is None or auc_ref is None
                               else dossier["auc_prix"] - auc_ref))


def residu_local(dossier: dict, portee: int = 120) -> dict:
    """
    @brief L'affine globale suffit-elle LOCALEMENT ? — balayage de décalages sur une fenêtre.

    ⚠⚠⚠ POURQUOI CE CONTRÔLE EXISTE. Sur toute l'empreinte, la carte publiée classe les
    étiquettes recalées à **0,756** ; sur la fenêtre la plus encrée, elle tombe à **0,418** —
    sous le hasard. Or une AUC *sous* le hasard n'est pas un manque de signal : c'est du signal
    **anti-aligné**, et un texte est fait de traits quasi périodiques, donc un décalage d'une
    demi-largeur de trait suffit à mettre l'encre prédite dans les blancs.

    ⚠⚠ Si un décalage modeste restaure l'accord, le verdict est net et il porte loin : **une
    affine globale ne suffit pas localement**, et aucun chiffre du régime du prix ne veut rien
    dire tant que le recalage n'est pas local. Si aucun décalage ne restaure rien, le désaccord
    est réel et le recalage est innocenté.

    ⚠ Le balayage porte sur la **référence publiée**, pas sur notre carte : c'est elle dont on
    sait qu'elle marche ailleurs, donc c'est elle qui peut dire si la faute est au recalage.
    """
    from le_nul_verso import aire_sous_la_courbe  # noqa: PLC0415
    from zarr_depth import BUCKET, get  # noqa: PLC0415

    masque, etiquettes = _image("500P2_mask.png"), _image("500P2_inklabels.png")
    publiee = carte_publiee_reduite()
    if masque is None or etiquettes is None or publiee is None:
        raise SystemExit("étiquettes ou carte publiée absentes")
    carte, _ = publiee
    empreinte = (carte > 0).astype(float)
    t = affine_par_boites(masque, empreinte)
    eti = appliquer(etiquettes, t, empreinte.shape)
    forme = json.loads(get(f"{BUCKET}/{dossier['zarr']}/0/.zarray", 60))["shape"]
    fr = eti.shape[0] / forme[1]
    fc = eti.shape[1] / forme[2]
    r0 = int(round(dossier["fenetre"]["top"] * fr))
    c0 = int(round(dossier["fenetre"]["left"] * fc))
    h = max(2, int(round(dossier["taille"] * fr)))
    ref = carte[r0:r0 + h, c0:c0 + h]
    ok = np.isfinite(ref) & (ref > 0)
    # ⚠⚠ LE BALAYAGE UTILISE UN SCORE RAPIDE, L'AUC NE VIENT QU'À LA FIN. Une AUC trie ses deux
    # populations ; à quelques centaines de décalages sur soixante-dix mille pixels, le balayage
    # coûterait des minutes pour une réponse qui est « où est le maximum ». L'écart normalisé des
    # moyennes est monotone avec l'AUC pour des populations de forme comparable, donc il place le
    # maximum au même endroit — et l'AUC exacte est calculée là, plus au centre.
    #
    # ⚠⚠⚠ ET LA PORTÉE VIENT D'UNE MESURE, PAS D'UN CONFORT. Ma première version balayait
    # ±12 cellules — soit ±212 µm, un tiers de lettre — et son maximum tombait **au bord**, ce
    # qui ne veut rien dire d'autre que « la recherche était trop courte ». L'écart de rapport
    # d'aspect de 3,2 % implique jusqu'à ~90 cellules de dérive d'un bout à l'autre du fragment :
    # c'est cette échelle-là qu'il faut couvrir.
    def score(reg):
        a = ref[ok & (reg > 0.5)]
        b = ref[ok & (reg <= 0.5)]
        if a.size < 100 or b.size < 100:
            return None, a.size
        ecart = float(a.mean() - b.mean())
        etendue = float(np.std(ref[ok])) or 1.0
        return ecart / etendue, a.size

    resultats = []
    pas = max(1, portee // 15)
    for di in range(-portee, portee + 1, pas):
        for dj in range(-portee, portee + 1, pas):
            # ⚠ La fenêtre d'ÉTIQUETTES bouge, pas celle de la carte : décaler la carte
            # changerait aussi le masque de validité et l'on comparerait deux populations.
            if r0 + di < 0 or c0 + dj < 0:
                continue
            reg = eti[r0 + di:r0 + di + h, c0 + dj:c0 + dj + h]
            if reg.shape != ref.shape:
                continue
            sc, n = score(reg)
            if sc is None:
                continue
            resultats.append(dict(di=di, dj=dj, score=sc, pixels_encre=int(n)))
    if not resultats:
        return {}
    meilleur = max(resultats, key=lambda x: x["score"])

    def auc_a(di, dj):
        reg = eti[r0 + di:r0 + di + h, c0 + dj:c0 + dj + h]
        a = ref[ok & (reg > 0.5)].ravel()
        b = ref[ok & (reg <= 0.5)].ravel()
        return (aire_sous_la_courbe(a, b) if a.size >= 100 and b.size >= 100 else None)

    auc_centre = auc_a(0, 0)
    auc_best = auc_a(meilleur["di"], meilleur["dj"])
    au_bord = (abs(meilleur["di"]) >= portee - pas or abs(meilleur["dj"]) >= portee - pas)
    return dict(portee=portee, pas=pas, balayage=resultats,
                auc_centre=auc_centre, auc_meilleure=auc_best,
                decalage_meilleur=[meilleur["di"], meilleur["dj"]],
                # ⚠⚠ « LE MAXIMUM EST AU BORD » EST UN RÉSULTAT, pas un détail : il veut dire que
                # la recherche était trop courte et que le chiffre rendu n'est pas un optimum.
                maximum_au_bord=bool(au_bord),
                gain=(None if auc_best is None or auc_centre is None else auc_best - auc_centre))


def champ_local(pas: int = 128, portee: int = 140, sous_pas: int = 10) -> dict:
    """
    @brief Un champ de décalages estimé sur les EMPREINTES, jamais sur l'encre.

    ⚠⚠⚠ POURQUOI L'ENCRE EST INTERDITE ICI, et c'est le piège central de tout ce lot. Ajuster le
    recalage en maximisant l'accord entre la **carte d'encre publiée** et les **étiquettes**
    ferait deux choses à la fois : il rendrait cet accord élevé **par construction**, et il
    ajusterait la géométrie sur les erreurs d'un détecteur qui n'est pas le nôtre. Scorer ensuite
    notre carte à travers ce champ, ce serait la juger contre une géométrie taillée pour
    quelqu'un d'autre.

    ⭐⭐ LE CHAMP EST DONC AJUSTÉ SUR LES SILHOUETTES et **validé sur l'encre**. Les deux sont
    indépendants : une empreinte dit où il y a de la matière, une étiquette dit où il y a de
    l'encre. Si un champ tiré des premières restaure l'accord des secondes, c'est une validation
    croisée, pas une tautologie.

    ⚠⚠ ET UNE SILHOUETTE PLEINE NE CONTRAINT RIEN. Un carreau entièrement à l'intérieur du
    fragment se ressemble à lui-même partout : son décalage optimal est arbitraire. Seuls les
    carreaux qui portent un **bord** — contour extérieur, trou, déchirure — portent de
    l'information, et ce sont les seuls retenus. Le compte des carreaux retenus est rendu, parce
    qu'un champ estimé sur trois carreaux n'est pas un champ.

    ⚠ Recherche à deux étages (grossier `sous_pas`, puis fin autour du meilleur) : un balayage
    fin sur ±140 cellules coûterait 78 000 évaluations par carreau.
    """
    masque, _ = _image("500P2_mask.png"), None
    publiee = carte_publiee_reduite()
    if masque is None or publiee is None:
        raise SystemExit("masque ou carte publiée absents")
    carte, _ = publiee
    empreinte = (carte > 0).astype(float)
    t = affine_par_boites(masque, empreinte)
    masque_recale = appliquer(masque, t, empreinte.shape) > 0.5
    cible = empreinte > 0.5

    def recouvrement(a, b):
        s_ = a.sum() + b.sum()
        return float(2.0 * (a & b).sum() / s_) if s_ else 0.0

    carreaux = []
    h, w = cible.shape
    for i in range(0, h - pas + 1, pas):
        for j in range(0, w - pas + 1, pas):
            bloc = cible[i:i + pas, j:j + pas]
            part = float(bloc.mean())
            # ⚠⚠ Un carreau plein (ou vide) ne contraint rien : son décalage optimal est
            # arbitraire. On exige un BORD, donc une occupation strictement intermédiaire.
            if not 0.15 < part < 0.85:
                continue
            meilleur, ou = -1.0, (0, 0)
            for etage, (rayon, incr) in enumerate(((portee, sous_pas), (sous_pas, 2))):
                base = ou
                for di in range(base[0] - rayon, base[0] + rayon + 1, incr):
                    for dj in range(base[1] - rayon, base[1] + rayon + 1, incr):
                        si, sj = i + di, j + dj
                        if si < 0 or sj < 0 or si + pas > h or sj + pas > w:
                            continue
                        d = recouvrement(bloc, masque_recale[si:si + pas, sj:sj + pas])
                        if d > meilleur:
                            meilleur, ou = d, (di, dj)
                if etage == 0 and meilleur <= 0:
                    break
            carreaux.append(dict(i=i, j=j, di=ou[0], dj=ou[1], dice=meilleur, occupation=part))
    if not carreaux:
        return {}
    normes = [float(np.hypot(c["di"], c["dj"])) for c in carreaux]
    return dict(pas=pas, portee=portee, carreaux=carreaux, retenus=len(carreaux),
                norme_mediane=float(np.median(normes)),
                norme_p90=float(np.percentile(normes, 90)),
                norme_max=float(max(normes)),
                dice_median=float(np.median([c["dice"] for c in carreaux])))


def valider_le_champ(dossier: dict, champ: dict) -> dict:
    """
    @brief Le champ tiré des silhouettes restaure-t-il l'accord de l'ENCRE ?

    ⚠⚠⚠ C'EST LA VALIDATION CROISÉE, et elle est écrite pour tomber. Le champ n'a jamais vu une
    étiquette ni une carte d'encre : s'il remonte l'AUC de la carte publiée sur la fenêtre où
    elle échouait, la géométrie était bien la cause. S'il ne la remonte pas, le résidu n'est pas
    géométrique et il faut chercher ailleurs — les deux réponses valent d'être écrites.
    """
    from le_nul_verso import aire_sous_la_courbe  # noqa: PLC0415
    from zarr_depth import BUCKET, get  # noqa: PLC0415

    masque, etiquettes = _image("500P2_mask.png"), _image("500P2_inklabels.png")
    publiee = carte_publiee_reduite()
    if masque is None or etiquettes is None or publiee is None:
        return {}
    carte, _ = publiee
    empreinte = (carte > 0).astype(float)
    t = affine_par_boites(masque, empreinte)
    eti = appliquer(etiquettes, t, empreinte.shape)
    forme = json.loads(get(f"{BUCKET}/{dossier['zarr']}/0/.zarray", 60))["shape"]
    fr = eti.shape[0] / forme[1]
    fc = eti.shape[1] / forme[2]
    r0 = int(round(dossier["fenetre"]["top"] * fr))
    c0 = int(round(dossier["fenetre"]["left"] * fc))
    h = max(2, int(round(dossier["taille"] * fr)))
    ref = carte[r0:r0 + h, c0:c0 + h]
    ok = np.isfinite(ref) & (ref > 0)

    def auc(di, dj):
        if r0 + di < 0 or c0 + dj < 0:
            return None
        reg = eti[r0 + di:r0 + di + h, c0 + dj:c0 + dj + h]
        if reg.shape != ref.shape:
            return None
        a = ref[ok & (reg > 0.5)].ravel()
        b = ref[ok & (reg <= 0.5)].ravel()
        return aire_sous_la_courbe(a, b) if a.size >= 100 and b.size >= 100 else None

    # ⚠ Le carreau du champ le plus proche du centre de la fenêtre : le champ est estimé sur une
    # grille plus grossière que la fenêtre, donc il faut dire lequel on applique.
    ci, cj = r0 + h // 2, c0 + h // 2
    proche = min(champ["carreaux"],
                 key=lambda c: (c["i"] + champ["pas"] // 2 - ci) ** 2
                 + (c["j"] + champ["pas"] // 2 - cj) ** 2)
    return dict(auc_sans_champ=auc(0, 0),
                auc_avec_champ=auc(proche["di"], proche["dj"]),
                carreau=proche,
                distance_au_carreau=float(np.hypot(proche["i"] + champ["pas"] // 2 - ci,
                                                   proche["j"] + champ["pas"] // 2 - cj)))


def _verifier(r: dict | None = None) -> int:
    echecs = comptes = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptes
        comptes += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ L'ÉTENDUE AUX PERCENTILES, testée sur le cas qu'elle existe pour : un pixel isolé loin
    # de la masse. Un min/max le suivrait et décalerait toute la carte.
    m = np.zeros((100, 100)); m[40:60, 30:70] = 1.0
    v("l'étendue trouve la boîte d'un bloc propre", etendue(m) == (40, 59, 30, 69), str(etendue(m)))
    sale = m.copy(); sale[2, 2] = 1.0
    v("... et un pixel isolé ne la déplace pas", etendue(sale)[0] >= 39, str(etendue(sale)))
    v("... un masque vide rend la grille entière", etendue(np.zeros((10, 10))) == (0, 9, 0, 9))

    # ⚠⚠⚠ L'AFFINE DOIT RETROUVER UNE TRANSFORMATION CONNUE. Fixture volontairement ANISOTROPE :
    # une échelle unique passerait un test isotrope sans rien prouver, or c'est précisément
    # l'anisotropie (3,2 % d'aspect) qui justifie ce fichier.
    cible = np.zeros((200, 150)); cible[20:120, 30:120] = 1.0
    t = affine_par_boites(m, cible)
    v("l'affine retrouve deux échelles DIFFÉRENTES",
      abs(t["echelle_lignes"] - 99 / 19) < 0.2 and abs(t["echelle_colonnes"] - 89 / 39) < 0.2
      and abs(t["echelle_lignes"] - t["echelle_colonnes"]) > 1.0,
      f"lignes {t['echelle_lignes']:.2f}, colonnes {t['echelle_colonnes']:.2f}")
    rendu = appliquer(m, t, cible.shape)
    v("... et l'appliquer fait coïncider les boîtes",
      dice(rendu, cible) > 0.97, f"Dice {dice(rendu, cible):.3f}")
    # ⚠ Ce qui tombe hors de la source est mis à ZÉRO, pas rabattu sur le bord : rabattre
    # étalerait la dernière ligne d'étiquettes sur la marge, donc inventerait de l'encre.
    etroit = np.zeros((10, 10)); etroit[4:6, 4:6] = 1.0
    large = appliquer(etroit, dict(echelle_lignes=1.0, echelle_colonnes=1.0,
                                   decalage_lignes=0.0, decalage_colonnes=0.0), (30, 30))
    v("ce qui tombe hors de la source est mis à zéro, pas rabattu",
      large[20:, :].sum() == 0.0 and large[4:6, 4:6].sum() == 4.0,
      f"hors-source {large[20:, :].sum()}")
    # ⚠⚠ PLUS PROCHE VOISIN : les étiquettes sont des classes. Une interpolation créerait des
    # demi-valeurs, qu'un seuil transformerait en halo d'encre autour de chaque trait.
    classes = np.array([[0.0, 4.0]])
    etire = appliquer(classes, dict(echelle_lignes=1.0, echelle_colonnes=4.0,
                                    decalage_lignes=0.0, decalage_colonnes=0.0), (1, 8))
    v("... et le ré-échantillonnage ne crée aucune valeur intermédiaire",
      set(np.unique(etire)) <= {0.0, 4.0}, str(np.unique(etire)))

    if r:
        print("\net la mesure")
        t = r["transformation"]
        print(f"      échelles {t['echelle_lignes']:.4f} (lignes) × "
              f"{t['echelle_colonnes']:.4f} (colonnes), "
              f"décalage {t['decalage_lignes']:.1f} / {t['decalage_colonnes']:.1f}")
        print(f"      Dice {r['dice_avant']:.3f} → {r['dice_apres']:.3f} à "
              f"{COTE_VALIDATION} de côté")
        print(f"      {100 * r['part_encre']:.1f} % de la surface est étiquetée encre "
              f"({r['pixels_encre']} contre {r['pixels_fond']} pixels)")
        v("le recalage améliore le recouvrement, ou le laisse déjà excellent",
          r["dice_apres"] >= max(0.95, r["dice_avant"] - 0.005),
          f"{r['dice_avant']:.3f} → {r['dice_apres']:.3f}")
        # ⚠⚠⚠ LA VALIDATION PAR UNE RÉFÉRENCE EXTERNE, écrite pour tomber dans les deux sens.
        # La carte publiée est celle dont le papier montre qu'elle marche : si elle classe les
        # étiquettes recalées, le recalage est bon ET on tient la valeur à battre. Sinon on ne
        # sait pas si c'est le recalage ou la carte, et il faut le dire au lieu de conclure.
        # ⚠⚠⚠ LE RÉSIDU LOCAL, ET C'EST LE RÉSULTAT QUI ANNULE TOUS LES AUTRES. Sur la fenêtre
        # la plus encrée, la carte publiée tombe à 0,418 — sous le hasard — et un décalage de
        # (-104, -120) cellules la remonte à 0,711. Le résidu vaut donc ≥ 120 cellules ×
        # 17,7 µm = **2,1 mm**, soit trois lettres et demie. Une affine globale ne suffit pas
        # localement, et aucun chiffre mesuré par fenêtre à travers ce recalage n'est
        # interprétable tant qu'il n'est pas local.
        res = r.get("residu_local")
        if res:
            v("un décalage local restaure franchement la carte publiée",
              res["gain"] is not None and res["gain"] > 0.15,
              f"{res['auc_centre']:.3f} → {res['auc_meilleure']:.3f} au décalage "
              f"{res['decalage_meilleur']} (gain {res['gain']:+.3f})")
            # ⚠⚠ « LE MAXIMUM EST AU BORD » EST ASSERTÉ, pas noté : tant qu'il l'est, le chiffre
            # rendu n'est pas un optimum et le résidu est un MINORANT.
            v("... et le maximum est encore au bord, donc le résidu est un minorant",
              res["maximum_au_bord"] is True,
              f"portée ±{res['portee']} cellules = ±{res['portee'] * 17.7 / 1000:.1f} mm")
            v("... donc l'affine GLOBALE ne suffit pas localement",
              abs(res["decalage_meilleur"][0]) > 40 or abs(res["decalage_meilleur"][1]) > 40,
              f"décalage {res['decalage_meilleur']} cellules, soit "
              f"{max(map(abs, res['decalage_meilleur'])) * 17.7 / 1000:.1f} mm")
        # ⚠⚠⚠ LA VALIDATION CROISÉE, et c'est elle qui transforme « ça ne marche pas » en « la
        # cause est géométrique ». Le champ est estimé sur les SILHOUETTES — il n'a jamais vu une
        # étiquette ni une carte d'encre — et il remonte quand même l'accord de l'encre. Si
        # l'ajustement avait vu l'encre, l'accord serait élevé par construction et ne prouverait
        # rien.
        ch, val = r.get("champ_local"), r.get("validation_du_champ")
        if ch and val:
            v("le champ local est estimé sur assez de carreaux pour en être un",
              ch["retenus"] >= 20,
              f"{ch['retenus']} carreaux portant un bord, Dice médian {ch['dice_median']:.3f}")
            v("... et il mesure un décalage de l'ordre du millimètre",
              ch["norme_mediane"] > 20,
              f"médiane {ch['norme_mediane']:.0f} cellules "
              f"({ch['norme_mediane'] * 17.7 / 1000:.1f} mm), max {ch['norme_max']:.0f} "
              f"({ch['norme_max'] * 17.7 / 1000:.1f} mm)")
            v("... et un champ tiré des SILHOUETTES restaure l'accord de l'ENCRE",
              val["auc_avec_champ"] - val["auc_sans_champ"] > 0.10,
              f"{val['auc_sans_champ']:.3f} → {val['auc_avec_champ']:.3f}")
            # ⚠⚠ ET IL N'ATTEINT PAS L'OPTIMUM TROUVÉ SUR L'ENCRE, ce qui est la BONNE nouvelle :
            # un champ indépendant qui égalerait un ajustement fait sur la cible serait suspect.
            # L'écart dit ce qu'il reste à gagner avec un champ plus dense.
            res = r.get("residu_local") or {}
            if res.get("auc_meilleure") is not None:
                v("... sans atteindre l'optimum trouvé EN REGARDANT l'encre, ce qui est normal",
                  val["auc_avec_champ"] < res["auc_meilleure"],
                  f"{val['auc_avec_champ']:.3f} contre {res['auc_meilleure']:.3f} — "
                  f"le carreau le plus proche est à {val['distance_au_carreau']:.0f} cellules")
        if r.get("auc_carte_publiee") is not None:
            v("la carte publiée retrouve les étiquettes recalées",
              r["auc_carte_publiee"] > 0.75,
              f"AUC {r['auc_carte_publiee']:.3f} — c'est la valeur de référence à battre au "
              "régime du prix")
            v("... et le témoin par mélange est centré",
              abs(r["auc_temoin_melange"] - 0.5) < 0.02,
              f"{r['auc_temoin_melange']:.3f}")

    print()
    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {comptes} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--recette", default="new_canon")
    p.add_argument("--champ", action="store_true",
                   help="estimer le champ local sur les EMPREINTES et le valider sur l'encre")
    p.add_argument("--residu", action="store_true",
                   help="l'affine globale suffit-elle localement ? balayage de décalages")
    p.add_argument("--apparier", action="store_true",
                   help="recalculer la référence appariée d'un dossier existant, sans inférence")
    p.add_argument("--prix", action="store_true",
                   help="notre détecteur contre les étiquettes, au régime demandé")
    p.add_argument("--regime", default="prix", choices=("prix", "production"),
                   help="prix = 9,362 µm ; production = 2,215 µm (le CONTRÔLE obligatoire)")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier and not a.json:
        cible = RACINE / "docs" / "mesures" / "le_recalage_des_etiquettes.json"
        return 1 if _verifier(json.loads(cible.read_text()) if cible.is_file() else None) else 0
    if a.champ:
        cible = a.json
        if cible is None or not cible.is_file():
            raise SystemExit("--champ demande --json <dossier du régime>")
        d = json.loads(cible.read_text())
        c = champ_local()
        val = valider_le_champ(d, c)
        d["champ_local"] = {k: v for k, v in c.items() if k != "carreaux"}
        d["champ_local"]["carreaux"] = c["carreaux"]
        d["validation_du_champ"] = val
        cible.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"champ estimé sur {c['retenus']} carreaux portant un bord "
              f"(Dice médian {c['dice_median']:.3f})")
        print(f"  norme du décalage : médiane {c['norme_mediane']:.0f}, "
              f"p90 {c['norme_p90']:.0f}, max {c['norme_max']:.0f} cellules "
              f"({c['norme_max'] * 17.7 / 1000:.1f} mm)")
        if val:
            print(f"\n  validation croisée sur l'encre, fenêtre du dossier :")
            print(f"    sans le champ  {val['auc_sans_champ']:.3f}")
            print(f"    avec le champ  {val['auc_avec_champ']:.3f}   "
                  f"(carreau à {val['distance_au_carreau']:.0f} cellules, "
                  f"décalage {val['carreau']['di']}, {val['carreau']['dj']})")
        print(f"écrit : {cible}")
        return 0

    if a.residu:
        cible = a.json
        if cible is None or not cible.is_file():
            raise SystemExit("--residu demande --json <dossier existant>")
        d = json.loads(cible.read_text())
        r = residu_local(d)
        d["residu_local"] = r
        cible.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"carte publiée sur cette fenêtre, sans décalage : {r['auc_centre']:.3f}")
        print(f"  meilleure sur ±{r['portee']} cellules (pas {r['pas']}) : "
              f"{r['auc_meilleure']:.3f} au décalage {r['decalage_meilleur']}  "
              f"(gain {r['gain']:+.3f})")
        if r["maximum_au_bord"]:
            print("  ⚠ le maximum est AU BORD du balayage : ce n'est pas un optimum")
        print(f"écrit : {cible}")
        return 0

    if a.apparier:
        cible = a.json
        if cible is None or not cible.is_file():
            raise SystemExit("--apparier demande --json <dossier existant>")
        d = json.loads(cible.read_text())
        d.update(apparier_depuis_la_carte(d))
        cible.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"la nôtre                 {d['auc_prix']:.3f}")
        print(f"la publiée, MÊME fenêtre {d['auc_publiee_meme_fenetre']:.3f}"
              f"   (écart apparié {d['ecart_apparie']:+.3f})")
        print(f"écrit : {cible}")
        return 0

    if a.prix:
        r = mesurer_au_regime_du_prix(regime=a.regime)
        print(f"{r['segment']} — régime {r['regime']} ({r['voxel_um']} µm), "
              f"{r['couches']} couches, "
              f"fenêtre du modèle {r['fenetre_um']:.0f} µm")
        print(f"  fenêtre top {r['fenetre']['top']}, left {r['fenetre']['left']}  "
              f"({100 * r['fenetre']['part_encre']:.1f} % d'encre étiquetée)")
        print(f"  encre min/méd/max {r['encre']['minimum']:+.3f} / "
              f"{r['encre']['mediane']:+.3f} / {r['encre']['maximum']:+.3f}")
        print(f"\n  AUC contre les étiquettes infrarouges")
        print(f"    la nôtre                     {r['auc_prix']:.3f}")
        if r.get("auc_publiee_meme_fenetre") is not None:
            print(f"    la publiée, MÊME fenêtre     {r['auc_publiee_meme_fenetre']:.3f}"
                  f"   (écart apparié {r['ecart_apparie']:+.3f})")
        print(f"    témoin mélangé               {r['auc_temoin_melange']:.3f}"
              f"   ({r['pixels_encre']} contre {r['pixels_fond']} px)")
        if a.json:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"\nécrit : {a.json}")
        return 0

    r = mesurer(a.recette)
    t = r["transformation"]
    print(f"{r['segment']} — carte publiée {r['carte_publiee'][:60]}…")
    print(f"  échelles {t['echelle_lignes']:.4f} × {t['echelle_colonnes']:.4f}, "
          f"décalage {t['decalage_lignes']:.1f} / {t['decalage_colonnes']:.1f}")
    print(f"  Dice {r['dice_avant']:.3f} → {r['dice_apres']:.3f}")
    print(f"  {100 * r['part_encre']:.1f} % étiqueté encre "
          f"({r['pixels_encre']} contre {r['pixels_fond']} px)")
    if r["auc_carte_publiee"] is not None:
        print(f"\n  AUC de la carte PUBLIÉE contre les étiquettes recalées : "
              f"{r['auc_carte_publiee']:.3f}   (témoin mélangé {r['auc_temoin_melange']:.3f})")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    if a.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
