#!/usr/bin/env python3
"""Deux facons de suivre une nappe, sur la MEME coupe : le plus proche, et la crete.

⚠⚠ Ce que la figure doit rendre visible : le piege n'est pas que la methode naive
s'egare visiblement, c'est qu'elle reste un chemin CONNEXE ET PLAUSIBLE tout en changeant
de feuille. Rien dans sa forme ne dit qu'elle a change ; seul son RAYON le dit. Les deux
chemins sont donc dessines sur le meme fond et a la meme echelle, et l'ecart au rayon de
depart est imprime a cote.

⚠ L'escalier du chemin naif est un artefact de son pas entier (il saute de voxel en
voxel), pas le symptome recherche : un lisseur le ferait disparaitre sans rien corriger
du changement de feuille.

Les donnees viennent de `suivre_nappe` lui-meme : meme bloc, memes fonctions, memes
reglages que les temoins. Une figure qui re-implementerait la marche illustrerait un
autre programme que celui qui tourne.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from suivre_nappe import _nappe_cylindrique, marcher, marcher_plus_proche  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
ECHELLE = 7          # pixels par voxel
N, RAYON, ECART = 96, 28.0, 4.0
FOND = (14, 14, 16)
NAPPE = (150, 150, 156)
NAIF = (232, 96, 72)
NOTRE = (250, 176, 60)


def figure_reelle(bloc_npy: Path, depart, sortie: Path, n_pas: int = 800) -> dict | None:
    """La meme marche, sur la VRAIE prediction publiee, avant et apres la distance.

    ⚠⚠ Les deux moities sont le meme bloc, le meme depart et le meme code : seul le CHAMP
    change. Si l'une avait un autre reglage, on ne saurait pas ce qui explique la difference.

    ⚠⚠ ET LE PLAN DE COUPE EST CHOISI PAR LA MARCHE, PAS PAR MOI. Premiere version : je
    coupais en z, au z du depart. Le chemin y traversait visiblement cinq nappes -- une
    image accablante, et FAUSSE : la marche avait parcouru 125 voxels en z pour 57 en y,
    donc elle s'enfoncait dans l'ecran et sa projection sur une tranche de z ne pouvait
    que croiser des bandes. Mesure qui tranche : la valeur de la distance le long du
    chemin ne descend jamais sous 1,22 et ne traverse AUCUN vide. Le plan est donc celui
    des deux axes de plus grande etendue, et la tranche est prise a la mediane du chemin
    sur le troisieme -- la ou le chemin est reellement.
    """
    from PIL import Image, ImageDraw
    from suivre_nappe import champ_de_distance, echantillon

    if not bloc_npy.exists():
        return None
    brut = np.load(bloc_npy).astype(np.float32)
    if brut.max() > 1.5:
        brut = brut / 255.0
    dist = champ_de_distance(brut)

    n = brut.shape[0]
    ech = max(1, 760 // n)
    panneaux = []
    # ⚠⚠ LES DEUX CHEMINS SONT JUGES SUR LE MEME CHAMP, celui de la distance. Compter
    # « les vides traverses » sur le champ de chacun ne separait rien : sur un masque, la
    # matiere est un plateau, donc y rester est facile et ne dit rien de la position dans
    # l'epaisseur. Ce qui separe, c'est la distance au bord LE LONG du chemin -- une
    # marche sur l'axe median est loin des bords, une marche collee au bord ne l'est pas.
    for champ, titre in ((brut, "masque publie (th0.2) - deux valeurs, aucune crete"),
                         (dist, "transformee de distance - la crete est l'axe median")):
        res = marcher(champ, depart, [0.0, 1.0, 0.0], n_pas=n_pas)
        pts = np.array(res["points"])
        if pts.ndim != 2 or len(pts) < 2:
            pts = np.array([depart, depart], dtype=float)
        etendue = pts.max(0) - pts.min(0)
        a1, a2 = sorted(int(k) for k in np.argsort(etendue)[-2:])
        perp = ({0, 1, 2} - {a1, a2}).pop()
        tranche = int(round(float(np.median(pts[:, perp]))))
        coupe = np.take(champ, min(max(tranche, 0), champ.shape[perp] - 1), axis=perp)

        m = float(coupe.max()) or 1.0
        h, w = coupe.shape
        im = Image.new("RGB", (w * ech, h * ech + 60), FOND)
        d = ImageDraw.Draw(im)
        for y in range(h):
            for x in range(w):
                v = float(coupe[y, x]) / m
                if v > 0.03:
                    g = tuple(int(FOND[i] + (NAPPE[i] - FOND[i]) * min(v, 1.0)) for i in range(3))
                    d.rectangle([x * ech, y * ech + 60, (x + 1) * ech - 1,
                                 (y + 1) * ech + 59], fill=g)
        d.line([(q[a2] * ech + ech / 2, q[a1] * ech + ech / 2 + 60) for q in pts],
               fill=NOTRE, width=2, joint="curve")
        dx, dy = depart[a2] * ech + ech / 2, depart[a1] * ech + ech / 2 + 60
        d.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], outline=(255, 255, 255), width=2)

        # ⚠ Un vide est une valeur de distance quasi nulle, en VOXELS -- pas une fraction
        # du maximum de la tranche. Une premiere version prenait 0,6 x max : sur la
        # tranche la plus epaisse, ca mettait le seuil a 2,4 voxels et comptait 25
        # « vides » sur un chemin qui n'en traverse aucun.
        edt_chemin = np.array([echantillon(dist, q) for q in pts])
        vides = int(np.sum(np.diff((edt_chemin < 0.5).astype(int)) == 1))
        mediane = float(np.median(edt_chemin))
        noms = "zyx"
        d.text((8, 6), titre, fill=(226, 226, 230))
        d.text((8, 24), f"{res['pas_faits']} pas - {res['arret']}", fill=NOTRE)
        d.text((8, 42), f"plan {noms[a1]}{noms[a2]} (tranche {noms[perp]}={tranche}) - "
                        f"distance au bord le long du chemin : mediane {mediane:.2f} vx, "
                        f"{vides} vide(s) traverse(s)", fill=(150, 150, 156))
        panneaux.append((im, res, (vides, mediane)))

    largeur = sum(im.width for im, _, _ in panneaux) + 8
    hauteur = max(im.height for im, _, _ in panneaux)
    toile = Image.new("RGB", (largeur, hauteur), FOND)
    x = 0
    for im, _, _ in panneaux:
        toile.paste(im, (x, 0))
        x += im.width + 8
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"sortie": str(sortie),
            "pas_masque": panneaux[0][1]["pas_faits"],
            "pas_distance": panneaux[1][1]["pas_faits"],
            "vides_masque": panneaux[0][2][0],
            "vides_distance": panneaux[1][2][0],
            "edt_median_masque": panneaux[0][2][1],
            "edt_median_distance": panneaux[1][2][1],
            "arret_masque": panneaux[0][1]["arret"],
            "arret_distance": panneaux[1][1]["arret"]}


def figure_nappe(bloc_npy: Path, depart, sortie: Path) -> dict | None:
    """L'echine et ses cotes, sur la vraie prediction — un morceau de nappe, pas un fil.

    ⚠⚠ Le plan de coupe est choisi par LA COUVERTURE, pas par moi : les deux axes de plus
    grande etendue de l'ENSEMBLE des chemins. Sur un fil unique c'etait deja le remede a une
    figure trompeuse (`41` §6bis) ; ici c'est encore plus necessaire, parce que les cotes
    explorent justement l'axe que l'echine ne parcourt pas -- donc la tranche du fil serait
    la mauvaise.

    ⚠ L'echine est dessinee dans une couleur distincte : sans ca, une figure ou toutes les
    cotes sont paralleles et aucune echine visible ressemblerait a un peigne pose a plat,
    c'est-a-dire exactement au defaut que le mode `--nappe` existe pour eviter.
    """
    from PIL import Image, ImageDraw
    from suivre_nappe import champ_de_distance, marcher_nappe

    if not bloc_npy.exists():
        return None
    brut = np.load(bloc_npy).astype(np.float32)
    if brut.max() > 1.5:
        brut = brut / 255.0
    dist = champ_de_distance(brut)

    r = marcher_nappe(dist, depart, [0.0, 1.0, 0.0], n_pas=800,
                      ecart_cotes=6.0, n_cotes=24)
    if not r["chemins"]:
        return None

    tous = np.array([q for ch in r["chemins"] for q in ch])
    etendue = tous.max(0) - tous.min(0)
    a1, a2 = sorted(int(k) for k in np.argsort(etendue)[-2:])
    perp = ({0, 1, 2} - {a1, a2}).pop()
    tranche = int(round(float(np.median(tous[:, perp]))))
    coupe = np.take(dist, min(max(tranche, 0), dist.shape[perp] - 1), axis=perp)

    n = dist.shape[0]
    ech = max(1, 900 // n)
    m = float(coupe.max()) or 1.0
    h, w = coupe.shape
    im = Image.new("RGB", (w * ech, h * ech + 62), FOND)
    d = ImageDraw.Draw(im)
    for y in range(h):
        for x in range(w):
            v = float(coupe[y, x]) / m
            if v > 0.03:
                g = tuple(int(FOND[i] + (NAPPE[i] - FOND[i]) * min(v, 1.0)) for i in range(3))
                d.rectangle([x * ech, y * ech + 62, (x + 1) * ech - 1,
                             (y + 1) * ech + 61], fill=g)
    for k, ch in enumerate(r["chemins"]):
        pts = np.array(ch)
        if len(pts) < 2:
            continue
        couleur = NOTRE if k == 0 else (110, 170, 235)
        d.line([(q[a2] * ech + ech / 2, q[a1] * ech + ech / 2 + 62) for q in pts],
               fill=couleur, width=3 if k == 0 else 1, joint="curve")
    dx, dy = depart[a2] * ech + ech / 2, depart[a1] * ech + ech / 2 + 62
    d.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], outline=(255, 255, 255), width=2)

    noms = "zyx"
    d.text((8, 6), f"un morceau de nappe : 1 echine (ambre) + {r['cotes']} cotes (bleu)",
           fill=(226, 226, 230))
    d.text((8, 24), f"{r['points']} points de passage, contre {len(r['chemins'][0])} "
                    f"pour l'echine seule", fill=NOTRE)
    d.text((8, 42), f"plan {noms[a1]}{noms[a2]} (tranche {noms[perp]}={tranche}) "
                    f"- etendue {etendue[a1]:.0f} x {etendue[a2]:.0f} voxels",
           fill=(150, 150, 156))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return {"sortie": str(sortie), "points": r["points"], "cotes": r["cotes"],
            "echine": len(r["chemins"][0])}


def main() -> int:
    from PIL import Image, ImageDraw

    c = N / 2.0
    bloc = _nappe_cylindrique(N, RAYON, epaisseur=1.0, entre=ECART)
    zz, yy, xx = np.mgrid[0:N, 0:N, 0:N]
    ang = np.arctan2(yy - c, xx - c)
    interne = np.hypot(yy - c, xx - c) < RAYON + ECART / 2
    bloc[(np.abs(ang - 0.6) < 0.30) & interne] = 0.0

    depart = [48.0, c + RAYON * np.sin(-0.8), c + RAYON * np.cos(-0.8)]
    naif = marcher_plus_proche(bloc, depart, n_pas=200)
    notre = marcher(bloc, depart, [0.0, 1.0, 0.0], n_pas=200)

    coupe = bloc[48]
    largeur = hauteur = N * ECHELLE
    im = Image.new("RGB", (largeur, hauteur + 96), FOND)
    d = ImageDraw.Draw(im)

    # Le fond : la coupe, en niveaux de gris, un carré par voxel.
    for y in range(N):
        for x in range(N):
            v = float(coupe[y, x])
            if v > 0.05:
                g = tuple(int(FOND[i] + (NAPPE[i] - FOND[i]) * min(v, 1.0)) for i in range(3))
                d.rectangle([x * ECHELLE, y * ECHELLE + 72,
                             (x + 1) * ECHELLE - 1, (y + 1) * ECHELLE + 71], fill=g)

    def tracer(res, couleur, epaisseur=3):
        pts = np.array(res["points"])
        if pts.ndim != 2 or len(pts) < 2:
            return 0.0
        xy = [(p[2] * ECHELLE + ECHELLE / 2, p[1] * ECHELLE + ECHELLE / 2 + 72) for p in pts]
        d.line(xy, fill=couleur, width=epaisseur, joint="curve")
        r = np.hypot(pts[:, 1] - c, pts[:, 2] - c)
        return float(np.max(np.abs(r - RAYON)))

    e_naif = tracer(naif, NAIF)
    e_notre = tracer(notre, NOTRE)

    # Le départ, commun aux deux.
    dx, dy = depart[2] * ECHELLE + ECHELLE / 2, depart[1] * ECHELLE + ECHELLE / 2 + 72
    d.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], outline=(255, 255, 255), width=2)

    d.text((10, 8), "Deux facons de suivre une nappe - meme coupe, meme depart, "
                    f"deux spires a {ECART:.0f} voxels (30 um)", fill=(226, 226, 230))
    d.text((10, 30), f"au plus proche : quitte sa nappe de {e_naif:.1f} voxels "
                     f"- soit au-dela de la spire voisine", fill=NAIF)
    d.text((10, 48), f"sur la crete : reste a {e_notre:.2f} voxel, et s'ARRETE au trou "
                     f"({notre['pas_faits']} pas)", fill=NOTRE)

    sortie = RACINE / "docs" / "images" / "41_deux_marches.png"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    print(f"ecrit : {sortie}  ({im.width}x{im.height})")
    print(f"  naif  : ecart max {e_naif:.2f} voxels, {naif['pas_faits']} pas — {naif['arret']}")
    print(f"  notre : ecart max {e_notre:.2f} voxel, {notre['pas_faits']} pas — {notre['arret']}")

    # ⚠ La figure reelle n'est produite QUE si le bloc a ete telecharge : une figure
    # fabriquee a partir de rien serait indistinguable d'une figure de donnees.
    r = figure_reelle(RACINE / "data" / "nappe" / "bloc_1447_r128.npy",
                      [128.0, 128.0, 128.0],
                      RACINE / "docs" / "images" / "41_marche_reelle.png")
    if r is None:
        print("  (pas de bloc réel sous data/nappe/ — figure réelle non produite)")
    else:
        print(f"ecrit : {r['sortie']}")
        print(f"  masque    : {r['pas_masque']} pas, distance au bord médiane "
              f"{r['edt_median_masque']:.2f} vx, {r['vides_masque']} vide(s) — {r['arret_masque']}")
        print(f"  distance  : {r['pas_distance']} pas, distance au bord médiane "
              f"{r['edt_median_distance']:.2f} vx, {r['vides_distance']} vide(s) — {r['arret_distance']}")

    # ⚠ Le bloc de PHerc0358 est celui de la campagne `42` ; s'il n'a pas été téléchargé,
    # la figure n'est pas produite — une figure fabriquée à partir de rien serait
    # indistinguable d'une figure de données.
    rn = figure_nappe(RACINE / "data" / "nappe" / "bloc_0358_r128.npy",
                      [128.0, 128.0, 128.0],
                      RACINE / "docs" / "images" / "42_morceau_de_nappe.png")
    if rn is None:
        print("  (pas de bloc PHerc0358 sous data/nappe/ — figure nappe non produite)")
    else:
        print(f"ecrit : {rn['sortie']}")
        print(f"  {rn['cotes']} côtes, {rn['points']} points "
              f"(échine seule : {rn['echine']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
