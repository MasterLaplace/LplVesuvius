"""Le titre de PHerc. Paris 4 : chercher là où le texte finit, c'est-à-dire au cœur du rouleau.

Le prix : « The expected title region has shown no detectable ink so far — possibly a different ink, and the
top rows are physically missing ». Le dépôt n'a jamais visé le titre ; il a en revanche l'objet le plus
instrumenté de tous (120 spires publiées, l'axe courbe mesuré). Ce pipeline ne lit pas : il dit OÙ regarder,
avec une règle écrite avant de regarder.

La règle, RAPPORTÉE et non mesurée ici (`docs/archive/06_mesures_a_faire.md:10-15`, citant la Bodleian) : le
début du texte est à l'extérieur, la fin et le titre (le colophon) au cœur.

    T0 la règle           où un titre se trouve sur un rouleau d'Herculanum
    T1 la bande           la plus intérieure des bandes publiées, et ses révisions
    T2 le sens            quelle extrémité de la bande déroulée est au cœur : le rayon à l'axe courbe
    T3 le recalage        l'orientation de la carte d'encre contre le maillage, par leurs silhouettes
    T4 la fin du texte    le profil d'encre le long de la spire : où la dernière colonne s'arrête
    T5 le témoin          deux révisions de la même bande s'accordent-elles sur cette fin ?
    T6 les candidats      les vues de la dernière colonne et de ce qui la suit, à lire par un œil
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

from vesuve import images
from vesuve.rapport import Rapport

LE_PIXEL_UM = 2.4 * 8  # la carte réduite 8× d'un volume de surface à 2,4 µm
LAXE = Path(__file__).resolve().parents[1] / "donnees" / "paris4" / "laxe.json"
UNE_BANDE = re.compile(r"(\d{14})-w(\d{3})-(\d{3})\.jpg$")


def les_bandes(cartes: Path) -> list[dict]:
    """Les cartes des bandes numérotées `wNNN-MMM` (NNN, MMM : les rangs de spire, croissants vers l'extérieur)."""
    out = []
    for p in sorted(Path(cartes).glob("*.jpg")):
        m = UNE_BANDE.search(p.name)
        if m:
            out.append({"le_segment": m.group(1), "de": int(m.group(2)), "a": int(m.group(3)), "la_carte": p})
    return out


def le_rayon_par_colonne(maillage: Path, laxe: dict) -> np.ndarray:
    """La distance médiane de chaque colonne du maillage à l'axe courbe, en mm."""
    x, y, z = (tifffile.imread(Path(maillage) / f"{c}.tif").astype(np.float64) for c in "xyz")
    ok = (x > 0) & (y > 0) & (z > 0)
    v = float(laxe["le_voxel_um"]) / 1000.0
    t = laxe["la_trace"]
    cx = np.interp(z * v, t["z_mm"], t["cx_mm"])
    cy = np.interp(z * v, t["z_mm"], t["cy_mm"])
    r = np.hypot(x * v - cx, y * v - cy)
    r[~ok] = np.nan
    return np.nanmedian(r, axis=0)


def lorientation(carte: np.ndarray, maillage: Path) -> tuple[str, float]:
    """Laquelle des quatre orientations (identité, miroirs) superpose le mieux la silhouette de la carte à
    celle du maillage : une orientation mesurée, jamais supposée."""
    x = tifffile.imread(Path(maillage) / "x.tif")
    s = (x > 0).astype(np.float32)
    c = np.asarray(Image.fromarray((carte > 0).astype(np.uint8) * 255).resize((s.shape[1], s.shape[0]),
                                                                               Image.BILINEAR), dtype=np.float32) / 255
    formes = {"identite": c, "miroir_horizontal": c[:, ::-1], "miroir_vertical": c[::-1, :], "demi_tour": c[::-1, ::-1]}
    if float(s.std()) == 0.0 or float(c.std()) == 0.0:
        return "identite", float("nan")  # une silhouette pleine ne dit rien de l'orientation
    notes = {k: float(np.corrcoef(s.ravel(), v.ravel())[0, 1]) for k, v in formes.items()}
    k = max(notes, key=notes.get)
    return k, notes[k]


def les_cellules_decrites(carte: np.ndarray, colonnes: int = 449, tranches: int = 16) -> np.ndarray:
    """(tranches, colonnes) : la part d'encre de chaque cellule, NaN là où il n'y a presque pas de papyrus."""
    from vesuve.rendu.rangees import binariser_encre
    papyrus = carte > 0
    encre = binariser_encre(carte, papyrus)
    bc = np.linspace(0, carte.shape[1], colonnes + 1).astype(int)
    br = np.linspace(0, carte.shape[0], tranches + 1).astype(int)
    out = np.full((tranches, colonnes), np.nan)
    for i in range(tranches):
        for j in range(colonnes):
            p = papyrus[br[i]:br[i + 1], bc[j]:bc[j + 1]].sum()
            if p > 0.5 * (br[i + 1] - br[i]) * (bc[j + 1] - bc[j]):
                out[i, j] = encre[br[i]:br[i + 1], bc[j]:bc[j + 1]].sum() / p
    return out


def le_seuil_des_cellules(cellules: np.ndarray) -> float:
    """Écrite ou vide : le seuil d'Otsu sur les parts d'encre de toutes les cellules, sans paramètre.

    ⚠ La première version prenait le milieu entre deux centiles d'un profil moyenné sur la hauteur : la
    dernière colonne d'un livre est COURTE (cinq lignes en haut sur `w010-027`), sa moyenne restait sous le
    seuil, et l'avant-dernière colonne passait pour la dernière. C'est l'image qui l'a montré.
    """
    from vesuve.rendu.rangees import binariser_encre
    v = cellules[np.isfinite(cellules)]
    octets = np.clip(np.round(v / max(v.max(), 1e-9) * 254) + 1, 1, 255).astype(np.uint8)
    b = binariser_encre(octets, np.ones_like(octets, dtype=bool))
    return float(v[~b].max() if (~b).any() else v.max())


def la_fin_du_texte(cellules: np.ndarray, du_coeur: str) -> dict:
    """Depuis le cœur, la première suite d'au moins 2 % de la bande dont chaque tranche porte une cellule écrite :
    la dernière colonne. Sa dernière ligne est la plus basse de ses cellules écrites."""
    seuil = le_seuil_des_cellules(cellules)
    ecrite = np.nan_to_num(cellules, nan=0.0) > seuil
    n = cellules.shape[1]
    ordre = np.arange(n) if du_coeur == "debut" else np.arange(n)[::-1]
    long_min = max(3, int(0.02 * n))
    run, bout = 0, None
    for rang, j in enumerate(ordre):
        run = run + 1 if ecrite[:, j].any() else 0
        if run >= long_min:
            bout = rang - run + 1
            break
    if bout is None:
        return {"le_seuil": round(seuil, 4), "la_derniere_colonne": None, "la_part_de_la_bande_apres_le_texte": None}
    # La colonne se prolonge vers l'extérieur SUR LES SEULES TRANCHES DE SES LIGNES, à travers les trous plus
    # courts que la suite minimale : une espace entre deux mots vide une tranche, un entre-colonnes davantage.
    # ⚠ Sur toutes les tranches, les lignes du bas qui débordent d'une colonne à l'autre soudaient la bande entière.
    siennes = np.flatnonzero(ecrite[:, ordre[bout:bout + long_min]].any(axis=1))
    k, trou = bout, 0
    while k + trou + 1 < n:
        if ecrite[siennes, ordre[k + trou + 1]].any():
            k, trou = k + trou + 1, 0
        elif trou + 1 < long_min:
            trou += 1
        else:
            break
    j0, j1 = sorted((int(ordre[bout]), int(ordre[k])))
    # Ses lignes sont celles de son bord côté cœur : la hauteur écrite de la DERNIÈRE colonne, pas celle d'un
    # débordement voisin ou d'un grain au bord du papyrus.
    return {"le_seuil": round(seuil, 4), "la_derniere_colonne": [j0, j1],
            "ses_tranches_ecrites": [int(siennes.min()), int(siennes.max())] if siennes.size else None,
            "la_part_de_la_bande_apres_le_texte": round(bout / n, 4)}


def lancer(cartes: Path, sortie: Path = Path("sorties/paris4-title"), cache: Path = Path("cache"),
           maillages: Path | None = None, journal=None) -> Rapport:
    sortie = Path(sortie)
    r = Rapport("paris4-title", {"les_cartes": str(cartes), "les_maillages": str(maillages) if maillages else None}, journal)
    laxe = json.loads(LAXE.read_text())

    with r.etage("T0", "la règle") as e:
        e.noter(la_regle=("le début du texte est à l'extérieur du rouleau, la fin et le titre (le colophon) au cœur : "
                          "« the end of the papyrus (the innermost part of the carbonised scroll) where the colophon "
                          "with the title of the work may be preserved »"),
                son_statut="rapporté (`docs/archive/06_mesures_a_faire.md:10-15`, Bodleian), pas mesuré ici",
                ce_que_dit_le_prix="aucune encre détectée jusqu'ici dans la région attendue ; encre peut-être différente ; "
                                   "rangées du haut physiquement manquantes")

    with r.etage("T1", "la bande la plus intérieure") as e:
        bandes = les_bandes(cartes)
        if not bandes:
            e.arreter(f"aucune carte de bande `wNNN-MMM` sous {cartes}")
        else:
            d0 = min(b["de"] for b in bandes)
            revisions = [b for b in bandes if b["de"] == d0]
            e.noter(les_bandes_vues=len(bandes), la_plus_interieure=f"w{d0:03d}-{revisions[0]['a']:03d}",
                    ses_revisions=[b["le_segment"] for b in revisions],
                    ce_qui_manque=f"les spires w000 à w{d0 - 1:03d} ne sont dans aucune bande publiée : le cœur même n'est pas tracé")
    if r.arrete:
        r.ecrire(sortie)
        return r

    fins = []
    for rev in revisions:
        seg = rev["le_segment"]
        maillage = Path(maillages) / seg if maillages else None
        carte = images.lire_une_image(Path(rev["la_carte"]).read_bytes())
        with r.etage(f"T2·{seg}", "le sens de l'enroulement") as e:
            if maillage is None or not (maillage / "x.tif").exists():
                e.sauter(f"le maillage de {seg} n'est pas donné (--maillages) : l'extrémité du cœur reste inconnue")
                du_coeur = None
            else:
                rayons = le_rayon_par_colonne(maillage, laxe)
                n = len(rayons)
                debut, fin = float(np.nanmedian(rayons[: n // 10])), float(np.nanmedian(rayons[-n // 10:]))
                orient, note = lorientation(carte, maillage)
                du_coeur_maillage = "debut" if debut < fin else "fin"
                miroir = orient in ("miroir_horizontal", "demi_tour")
                du_coeur = ({"debut": "fin", "fin": "debut"}[du_coeur_maillage] if miroir else du_coeur_maillage)
                if not note == note:  # NaN : la silhouette ne mesure rien
                    e.partiel("la silhouette du maillage est pleine : l'orientation n'est pas mesurable, l'identité est supposée")
                elif note < 0.5:
                    e.partiel(f"la silhouette de la carte ne corrèle qu'à {note:.2f} avec celle du maillage : "
                              f"l'orientation retenue n'est pas établie")
                e.noter(le_rayon_au_debut_mm=round(debut, 2), le_rayon_a_la_fin_mm=round(fin, 2),
                        lorientation_de_la_carte=orient, sa_correlation=round(note, 3),
                        le_coeur_est_du_cote=("gauche" if du_coeur == "debut" else "droite") + " de la carte")
        with r.etage(f"T4·{seg}", "la fin du texte") as e:
            if du_coeur is None:
                e.sauter("sans le sens de l'enroulement, « la fin » n'a pas de côté")
                continue
            cellules = les_cellules_decrites(carte)
            f = la_fin_du_texte(cellules, du_coeur)
            fins.append({"le_segment": seg, **f, "du_coeur": du_coeur, "la_largeur": carte.shape[1],
                         "la_hauteur": carte.shape[0], "carte": carte, "cellules": cellules.shape})
            e.noter(**f, la_regle=("16 tranches × 449 cellules le long de la spire, écrite ou vide par le seuil d'Otsu "
                                   "sur toutes les cellules : aucun paramètre choisi"))

    with r.etage("T5", "le témoin : deux révisions de la même bande", "B3") as e:
        parts = [f["la_part_de_la_bande_apres_le_texte"] for f in fins if f["la_part_de_la_bande_apres_le_texte"] is not None]
        if len(parts) < 2:
            e.sauter("il faut deux révisions jugées pour les confronter")
        else:
            e.noter(les_parts_apres_le_texte=parts, leur_ecart=round(abs(parts[0] - parts[1]), 4),
                    la_lecture=("deux maillages indépendants de la même bande : s'ils placent la fin du texte au même "
                                "endroit de la spire, la fin n'est pas un artefact d'un seul maillage"))

    with r.etage("T6", "les candidats") as e:
        sortie.mkdir(parents=True, exist_ok=True)
        produits, lieux = [], []
        from PIL import ImageDraw
        for f in fins:
            if f["la_derniere_colonne"] is None:
                continue
            c, w, h = f["carte"], f["la_largeur"], f["la_hauteur"]
            nt, nc = f["cellules"]
            c0, c1 = int(f["la_derniere_colonne"][0] * w / nc), int((f["la_derniere_colonne"][1] + 1) * w / nc)
            derniere = min(h - 1, int((f["ses_tranches_ecrites"][1] + 1) * h / nt))
            marge = (c1 - c0) // 2
            vers_le_coeur = f["du_coeur"] != "debut"
            z0, z1 = (max(0, c0 - marge // 2), min(w, c1 + 2 * marge)) if vers_le_coeur else \
                (max(0, c0 - 2 * marge), min(w, c1 + marge // 2))
            seg = f["le_segment"]
            images.barre_dechelle(images.niveaux(c[:, z0:z1]), LE_PIXEL_UM, 5.0).save(sortie / f"{seg}_derniere_colonne.png")
            images.barre_dechelle(images.niveaux(c[max(0, derniere - h // 16):, z0:z1]), LE_PIXEL_UM, 5.0).save(
                sortie / f"{seg}_sous_la_derniere_ligne.png")
            apercu = images.niveaux(c)
            apercu.thumbnail((2400, 2400))
            k = apercu.width / w
            a2 = apercu.convert("RGB")
            d = ImageDraw.Draw(a2)
            d.rectangle([c0 * k, 0, c1 * k, a2.height - 1], outline=(230, 120, 60), width=4)
            d.rectangle([z0 * k, min(derniere * k, a2.height - 2), z1 * k, a2.height - 1], outline=(80, 200, 255), width=4)
            a2.save(sortie / f"{seg}_bande_entiere.jpg", quality=85)
            produits += [f"{seg}_derniere_colonne.png", f"{seg}_sous_la_derniere_ligne.png", f"{seg}_bande_entiere.jpg"]
            lieux.append({"le_segment": seg, "la_derniere_colonne_px": [c0, c1], "sa_derniere_ligne_px": derniere,
                          "sa_hauteur_ecrite": round(derniere / h, 3),
                          "la_region_candidate_px": {"colonnes": [z0, z1], "rangees": [derniere, h]}})
        (sortie / "candidats.json").write_text(json.dumps(lieux, indent=1))
        e.noter(les_lieux=lieux, les_produits=produits + ["candidats.json"],
                la_lecture=("quand la dernière colonne est COURTE et que rien ne la suit vers le cœur, c'est la forme de "
                            "la fin d'un livre : le titre final se cherche sous sa dernière ligne et dans l'espace qui la "
                            "suit. En orange la colonne, en bleu la région"),
                ce_quil_reste=("lire, et chercher une AUTRE encre : le prix dit que la région attendue n'a montré aucune "
                               "encre détectable ; ces vues sont celles du modèle publié, et le produit ink-3d ou la carte "
                               "à 1,129 µm sont les suivantes à regarder"))

    r.exigence("une image que les papyrologues puissent lire", "non mesurée",
               "des vues de la fin du texte sur la bande la plus intérieure, à 19,2 µm par pixel ; personne ne les a lues")
    r.exigence("tout volume de Scroll 1, 2,4 µm compris", "atteinte", "les cartes d'encre publiées sur le volume à 2,4 µm")
    r.exigence("validation sur une région tenue à l'écart", "partiel",
               "deux révisions indépendantes de la même bande confrontées (T5) ; pas de vérité de terrain")
    r.exigence("le cœur du rouleau", "non atteinte", "les spires w000 à w009 ne sont dans aucune bande publiée")
    r.ecrire(sortie)
    return r
