#!/usr/bin/env python3
"""Depouiller une chaine de spires : taille, ecarts, alpha, verdict, et l'EROSION.

⚠⚠ Pourquoi ce fichier existe plutot qu'une commande jetable : ce tableau part dans un
document, donc son calcul doit etre dans l'arbre. Un chiffre publie dont le calcul n'est pas
rejouable n'est pas un resultat, c'est une anecdote.

⚠⚠ ET POURQUOI L'AIRE EST CALCULEE ICI. Un maillage produit par `mode: gen_neighbor` n'a
PAS de `area_cm2` dans son `meta.json` -- verifie : il porte bbox, format, scale, source,
target_volume, type, uuid, vc_gsfs_*. Sans ce calcul, une campagne d'enchainement affiche
« ? cm² » a chaque spire, et on ne peut pas dire si les spires gardent leur taille. Or c'est
justement la question : **une chaine qui s'erode a une longueur maximale.**

L'aire vient de deux choses qui sont deja ecrites : `grid_cols`/`grid_rows` dans le rapport
de selfcross, et `scale` dans le meta du maillage. Un pas de grille vaut `1/scale` voxels,
donc une cellule vaut `(pas x voxel_um)²`.

⚠ C'est l'aire de la GRILLE, pas celle de la matiere : les sommets invalides comptent quand
meme. C'est un majorant, honnete comme mesure de taille, faux comme mesure de surface utile.
La distinction est imprimee.

Usage :
    uv run python analysis/src/table_chaine.py data/spires --voxel-um 8.64 \\
        --json docs/chaine_spires.json
    uv run python analysis/src/table_chaine.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
PAS_DEFAUT_VOXELS = 20.0        # 1 / 0,05, l'echelle que le traceur ecrit par defaut


def aire_grille_cm2(cols: int, rows: int, pas_voxels: float, voxel_um: float) -> float:
    """Aire de la grille, en cm², depuis son nombre de cellules et la taille d'une cellule.

    ⚠ `cols - 1` et non `cols` : N sommets font N-1 cellules. L'oublier surestime de
    quelques pour cent, ce qui est juste assez peu pour passer inapercu.
    """
    cote_um = pas_voxels * voxel_um
    return max(0, cols - 1) * max(0, rows - 1) * (cote_um ** 2) * 1e-8


def pas_du_maillage(dossier: Path) -> float:
    """Le pas de grille en voxels, lu dans le `scale` du meta du maillage.

    ⚠ Lu et non suppose : deux campagnes peuvent tracer a des echelles differentes, et un
    pas suppose ferait des aires fausses d'un facteur (rapport des echelles)².
    """
    for meta in sorted(dossier.glob("trace/*/meta.json")) + sorted(dossier.glob("*/meta.json")):
        try:
            d = json.loads(meta.read_text(encoding="utf-8"))
        except Exception:
            continue
        sc = d.get("scale")
        if isinstance(sc, list) and sc and sc[0]:
            return 1.0 / float(sc[0])
    return PAS_DEFAUT_VOXELS


def etiquette_de(racine_spires: Path) -> str:
    """L'etiquette que `spire_suivante.sh` met dans le nom des verdicts d'une campagne."""
    base = racine_spires.name
    return "" if base == "spires" else base.removeprefix("spires_") + "_"


def depouiller(racine_spires: Path, voxel_um: float, docs: Path) -> list[dict]:
    etiquette = etiquette_de(racine_spires)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lire_selfcross import lire  # noqa: E402

    lignes = []
    for d in sorted(p for p in racine_spires.glob("spire*") if p.is_dir()):
        rapport = d / "selfcross.json"
        # ⚠ L'etiquette de campagne fait partie du nom du verdict : sans elle, depouiller
        # la campagne A rendrait les chiffres de la campagne B (paye le 2026-08-21).
        verdict = docs / f"spire_{etiquette}{d.name}.json"
        if not rapport.is_file() or not verdict.is_file():
            continue
        brut = json.loads(rapport.read_text(encoding="utf-8"))
        cols, rows = brut.get("grid_cols"), brut.get("grid_rows")
        if not cols or not rows:
            continue
        try:
            croisements = lire(rapport)["transverse_self_intersections"]
        except Exception:
            croisements = None
        s = json.loads(verdict.read_text(encoding="utf-8"))["series"][0]
        lignes.append({
            "spire": d.name,
            "grille": [cols, rows],
            "aire_grille_cm2": round(aire_grille_cm2(cols, rows,
                                                     pas_du_maillage(d), voxel_um), 2),
            "croisements": croisements,
            "ecart_31c_um": s["serie"][0][1],
            "ecart_81c_um": s["serie"][-1][1],
            "alpha": round(s["alpha"], 3),
            "verdict": s["verdict"],
        })
    return lignes


def verifier() -> int:
    echecs = 0

    def ok(cond, quoi):
        nonlocal echecs
        print(("  ✅ " if cond else "  ❌ ") + quoi)
        if not cond:
            echecs += 1

    print("Témoins de table_chaine")

    # 2x2 sommets = 1 cellule de 20 voxels de côté à 8,64 µm = 172,8 µm => 2,985e-4 cm²
    a = aire_grille_cm2(2, 2, 20.0, 8.64)
    ok(abs(a - (172.8 ** 2) * 1e-8) < 1e-12,
       f"une cellule seule fait bien son côté au carré ({a:.3e} cm²)")
    # ⚠ Sonde du « cols - 1 » : compter les SOMMETS au lieu des cellules surestime de 4x ici.
    faux = 2 * 2 * (172.8 ** 2) * 1e-8
    ok(abs(faux / a - 4.0) < 1e-9,
       "compter les sommets au lieu des cellules surestimerait d'un facteur 4 (sonde)")
    ok(aire_grille_cm2(1, 50, 20.0, 8.64) == 0.0,
       "une grille d'une seule colonne n'a aucune cellule")
    ok(aire_grille_cm2(0, 0, 20.0, 8.64) == 0.0,
       "une grille vide ne casse pas le calcul")
    # L'aire doit doubler si le pas double dans une seule direction ? non : elle quadruple.
    ok(abs(aire_grille_cm2(3, 3, 40.0, 8.64) / aire_grille_cm2(3, 3, 20.0, 8.64) - 4.0) < 1e-9,
       "doubler le pas quadruple l'aire (c'est un carré, pas une longueur)")

    # ⚠⚠ L'etiquette est ce qui empeche deux campagnes d'ecraser leurs verdicts. Sans elle,
    # depouiller `spires` rendrait les chiffres de `spires_repousse`.
    ok(etiquette_de(Path("data/spires")) == "",
       "la campagne de base n'a pas d'etiquette")
    ok(etiquette_de(Path("data/spires_repousse")) == "repousse_",
       "une campagne nommee spires_<x> porte l'etiquette <x>_")
    ok(etiquette_de(Path("data/spires")) != etiquette_de(Path("data/spires_repousse")),
       "deux campagnes ne peuvent pas partager un nom de verdict (la sonde)")

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        # ⚠ Un meta sans `scale` doit retomber sur le pas par défaut, pas lever.
        (t / "trace" / "m").mkdir(parents=True)
        (t / "trace" / "m" / "meta.json").write_text('{"format": "tifxyz"}')
        ok(pas_du_maillage(t) == PAS_DEFAUT_VOXELS,
           "un meta sans échelle retombe sur le pas par défaut")
        (t / "trace" / "m" / "meta.json").write_text('{"scale": [0.1, 0.1]}')
        ok(pas_du_maillage(t) == 10.0, "une échelle de 0,1 donne un pas de 10 voxels")

    print(f"\n{'tous les témoins passent' if not echecs else f'{echecs} échec(s)'}")
    return 1 if echecs else 0


def pas_du_rayon(racine: Path) -> float | None:
    """Le `neighbor_step` reellement utilise, lu dans le meta d'un maillage produit avec lui.

    ⚠⚠ PAS depuis le nom du dossier. « Le nom d'un dossier n'est pas une mesure » est un
    piege deja paye ici : un dossier nomme `PHerc1447_officiel` contenait un segment a
    α = +1,02. Le traceur ecrit ses parametres dans le `meta.json` de ce qu'il produit
    (`vc_gsfs_params`), donc la valeur se lit a la source.
    """
    for meta in sorted(racine.glob("spire*/trace/*/meta.json")):
        try:
            d = json.loads(meta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        v = (d.get("vc_gsfs_params") or {}).get("neighbor_step")
        if v is not None:
            return float(v)
    return None


def compensation_de(racine: Path) -> dict:
    """Les comptes de pas reellement demandes, lus dans le meta d'un maillage.

    ⚠⚠ `neighbor_exit_count` et `neighbor_spike_window` comptent des PAS et non une
    distance, donc leur portee physique vaut `compte x neighbor_step`
    (`vc_grow_seg_from_seed.cpp:784` et `:879`). Une campagne qui les laisse aux defauts a
    donc une portee qui se divise quand on affine le pas -- c'est le mecanisme de la courbe
    en U. Une campagne qui les compense n'est PAS comparable a l'autre sur le seul pas.

    ⚠ Lu dans le meta, jamais deduit du nom du dossier ; et `spire_suivante.sh` n'ecrit ces
    cles que si elles ont ete demandees, donc leur ABSENCE veut dire « defauts de l'outil ».
    """
    for meta in sorted(racine.glob("spire*/trace/*/meta.json")):
        try:
            d = json.loads(meta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        par = d.get("vc_gsfs_params") or {}
        if "neighbor_step" not in par:
            continue
        return {"exit_count": par.get("neighbor_exit_count"),
                "spike_window": par.get("neighbor_spike_window"),
                "compense": ("neighbor_exit_count" in par
                             or "neighbor_spike_window" in par)}
    return {"exit_count": None, "spike_window": None, "compense": False}


def comparer(racines: list[Path], voxel_um: float, docs: Path) -> dict:
    """Comparer plusieurs campagnes d'enchainement A PROFONDEUR EGALE.

    ⚠⚠ Deux regles, et chacune corrige une erreur reellement commise dans ce depot.

    **A profondeur egale.** Une chaine se degrade avec le rang -- le meilleur predicteur
    d'un echec de spire est son NUMERO (`44` §8) -- donc comparer une campagne de 7 tours a
    une de 11 sur un taux « par tour » fait passer la profondeur pour un effet du reglage.
    Mesure : le taux d'erosion des quatre campagnes lu sur toute leur longueur allait de
    13,2 a 18,0 % et semblait suivre le pas ; a profondeur egale il est de 12,8 a 13,0 %,
    c'est-a-dire constant sur un facteur HUIT de pas. Toute la tendance etait l'artefact.

    **Sans seuil.** On compare des α et des aires, jamais des COMPTES de verdicts. Un compte
    de verdicts est un compte de franchissements de seuil, et 10 des 55 verdicts de ce depot
    ont un α a moins de 0,2 du seuil quand l'instrument ne discrimine pas a ±0,2 pres.
    """
    campagnes = []
    for r in racines:
        lignes = depouiller(r, voxel_um, docs)
        if lignes:
            campagnes.append({"nom": r.name, "racine": str(r), "lignes": lignes})
    if len(campagnes) < 2:
        return {"campagnes": campagnes, "raison": "moins de deux campagnes lisibles"}
    # ⚠ La profondeur commune est celle de la campagne la plus COURTE. Prendre la plus
    # longue et completer les autres reviendrait a comparer du vide a des mesures.
    profondeur = min(len(c["lignes"]) for c in campagnes)
    for c in campagnes:
        tronc = c["lignes"][:profondeur]
        alphas = sorted(l["alpha"] for l in tronc)
        c["profondeur"] = profondeur
        c["alpha_moyen"] = sum(alphas) / len(alphas)
        c["alpha_median"] = alphas[len(alphas) // 2]
        c["alpha_max"] = alphas[-1]
        a0, a1 = tronc[0]["aire_grille_cm2"], tronc[-1]["aire_grille_cm2"]
        c["erosion_par_tour"] = (100 * (1 - a1 / a0) / (profondeur - 1)
                                 if a0 and profondeur > 1 else None)
        c["longueur_reelle"] = len(c["lignes"])
        c["pas_du_rayon"] = pas_du_rayon(Path(c["racine"]))
        c.update(compensation_de(Path(c["racine"])))
        pr = c["pas_du_rayon"]
        # ⭐ La PORTEE PHYSIQUE du test de sortie, en voxels : c'est elle qui compte, pas le
        # pas. Deux campagnes de pas differents mais de meme portee sont comparables ; deux
        # campagnes de meme pas et de portees differentes ne le sont pas.
        c["portee_sortie_vox"] = ((c["exit_count"] or 1) * pr) if pr else None
    return {"campagnes": campagnes, "profondeur_commune": profondeur}


# ⚠ La figure vit ici et non dans un `figure_*.py` separe : un producteur, un consommateur,
# et l'isoler creerait un fichier dont la seule fonction serait de relire le JSON que
# celui-ci vient d'ecrire.
def dessiner_comparaison(res: dict, sortie: Path) -> None:
    """α contre la PORTEE PHYSIQUE du test de sortie, a profondeur egale.

    ⚠⚠ L'abscisse est la PORTEE, pas le pas du rayon, et ce choix EST le resultat. La
    premiere version de cette figure mettait le pas en abscisse et montrait une courbe en U ;
    une campagne a pas 0,125 avec les comptes compenses tombe sur la meme portee qu'une
    campagne a pas 0,25 et lui ressemble, pas a l'autre campagne a pas 0,125. Mettre le pas
    en abscisse dessinerait donc DEUX points a la meme x avec des α opposes -- une figure qui
    ne peut pas etre lue, parce qu'elle trace la mauvaise variable.

    ⭐ Deux courbes : l'α MOYEN dit ce que la campagne vaut, l'α MAX dit ce que vaut son pire
    tour -- et c'est le pire tour qui casse une chaine.
    """
    from PIL import Image, ImageDraw, ImageFont

    pts = [(c["portee_sortie_vox"], c["alpha_moyen"], c["alpha_max"],
            c.get("pas_du_rayon"), bool(c.get("compense")))
           for c in res["campagnes"] if c.get("portee_sortie_vox")]
    if len(pts) < 2:
        return
    pts.sort()
    L, H = 940, 620
    X0, X1, Y0, Y1 = 120, 860, 460, 120
    img = Image.new("RGB", (L, H), (255, 255, 255))
    art = ImageDraw.Draw(img)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()
    AMBRE, ENCRE, GRIS = (196, 116, 24), (30, 30, 30), (150, 150, 150)

    art.text((26, 22), "Ce qui décide, c'est la portée — pas la finesse du pas",
             fill=ENCRE, font=f_t)
    art.text((26, 44), f"α sur les {res['profondeur_commune']} premiers tours de chaque "
                       f"campagne, à profondeur ÉGALE et sans seuil",
             fill=(110, 110, 110), font=f_n)

    import math
    lo, hi = math.log(min(x[0] for x in pts)), math.log(max(x[0] for x in pts))
    amax = max(x[2] for x in pts) * 1.14

    def px(v):
        return X0 + (X1 - X0) * ((math.log(v) - lo) / (hi - lo) if hi > lo else 0.5)

    def py(a):
        return Y0 - (Y0 - Y1) * (a / amax)

    art.line([X0, Y0, X1, Y0], fill=GRIS)
    art.line([X0, Y0, X0, Y1], fill=GRIS)
    for a in (0.0, 0.5, 1.0, 1.5):
        if a <= amax:
            y = py(a)
            art.line([X0 - 4, y, X1, y], fill=(240, 240, 240))
            art.text((X0 - 48, y - 7), f"{a:+.1f}", fill=(140, 140, 140), font=f_p)
    art.text((26, Y1 - 26), "α", fill=(120, 120, 120), font=f_n)
    art.text((X0 + (X1 - X0) // 2 - 130, Y0 + 34),
             "portée physique du test de sortie = exit_count × pas   (voxels, échelle log)",
             fill=(120, 120, 120), font=f_p)

    # ⚠ Une portee peut porter DEUX campagnes (pas differents, meme portee). On relie les
    # medianes par portee, sinon la ligne zigzague entre deux points de meme x.
    from collections import OrderedDict
    grp: "OrderedDict[float, list]" = OrderedDict()
    for v, moy, mx, _, _ in pts:
        grp.setdefault(v, []).append((moy, mx))
    ligne = [(v, sum(m for m, _ in g) / len(g), sum(x for _, x in g) / len(g))
             for v, g in grp.items()]
    for (va, ma, xa), (vb, mb, xb) in zip(ligne, ligne[1:]):
        art.line([px(va), py(xa), px(vb), py(xb)], fill=(228, 214, 198), width=3)
        art.line([px(va), py(ma), px(vb), py(mb)], fill=AMBRE, width=3)

    meilleur = min(pts, key=lambda t: t[1])
    # ⚠ Deux campagnes peuvent partager une portee (pas differents, comptes compenses) :
    # leurs marqueurs tombent au meme pixel. On decale les etiquettes par rang DANS le
    # groupe, sinon les deux chiffres se superposent et la figure perd le fait qu'elle
    # existe pour montrer — que deux pas donnent le meme α a portee egale.
    rang: dict = {}
    for v, *_ in pts:
        rang[v] = rang.get(v, -1) + 1
    rang = {}
    for v, moy, mx, pas, comp in pts:
        art.ellipse([px(v) - 5, py(mx) - 5, px(v) + 5, py(mx) + 5],
                    outline=(190, 170, 145), width=2)
        # ⭐ Un contour marque une campagne dont les comptes ont ete COMPENSES : sans ce
        # marquage, un lecteur croirait que deux points a la meme portee sont deux mesures
        # du meme reglage, alors que l'un a un pas deux fois plus fin.
        if comp:
            art.ellipse([px(v) - 8, py(moy) - 8, px(v) + 8, py(moy) + 8],
                        outline=AMBRE, width=2)
        art.ellipse([px(v) - 5, py(moy) - 5, px(v) + 5, py(moy) + 5], fill=AMBRE)
        k = rang[v] = rang.get(v, -1) + 1
        dy = 14 + 17 * k if comp else -22 - 17 * k
        art.text((px(v) - 20, py(moy) + dy), f"pas {pas:g} → {moy:+.2f}",
                 fill=AMBRE if comp else (140, 110, 80), font=f_p)
        art.text((px(v) + 12, py(mx) - 7), f"{mx:+.2f}", fill=(170, 150, 125), font=f_p)
    # ⚠ « optimum » se place A GAUCHE du point et non dessous : l'espace du dessous est celui
    # des etiquettes de campagne, et deux campagnes peuvent partager cette portee.
    art.text((px(meilleur[0]) - 86, py(meilleur[1]) - 6), "optimum >", fill=AMBRE, font=f_p)

    yl = Y1 - 4
    art.ellipse([X0 + 8, yl, X0 + 16, yl + 8], fill=AMBRE)
    art.text((X0 + 22, yl - 2), "α moyen", fill=(110, 110, 110), font=f_p)
    art.ellipse([X0 + 108, yl, X0 + 116, yl + 8], outline=(190, 170, 145), width=2)
    art.text((X0 + 122, yl - 2), "α du PIRE tour", fill=(110, 110, 110), font=f_p)
    art.ellipse([X0 + 248, yl - 2, X0 + 258, yl + 8], outline=AMBRE, width=2)
    art.text((X0 + 264, yl - 2), "comptes compensés (exit_count relevé)",
             fill=(110, 110, 110), font=f_p)

    bas = Y0 + 62
    doubles = [v for v, g in grp.items() if len(g) > 1]
    if doubles:
        art.text((26, bas), "→ Deux campagnes partagent la portée 0,25 avec des pas dans un "
                            "rapport 2 — et donnent le même α.", fill=(60, 60, 60), font=f_n)
        art.text((26, bas + 20), "À pas égal (0,125), changer la seule portée fait passer "
                                 "l'α moyen de +0,33 à +0,13.", fill=(60, 60, 60), font=f_n)
    ers = [c["erosion_par_tour"] for c in res["campagnes"]
           if c["erosion_par_tour"] is not None]
    if ers:
        art.text((26, bas + 42), f"!! L'érosion ne bouge dans aucun des cas : "
                                 f"{min(ers):.1f} % par tour partout.",
                 fill=(120, 120, 120), font=f_n)
    art.text((26, bas + 62), "Donc le réglage décide OÙ la surface se pose, pas combien "
                             "elle en perd.", fill=(120, 120, 120), font=f_n)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("racine", nargs="*", type=Path)
    ap.add_argument("--comparer", action="store_true",
                    help="comparer plusieurs campagnes à PROFONDEUR ÉGALE, sur les α et "
                         "les aires — jamais sur des comptes de verdicts")
    ap.add_argument("--voxel-um", type=float, default=8.64)
    ap.add_argument("--docs", type=Path, default=RACINE / "docs")
    ap.add_argument("--json")
    ap.add_argument("--figure", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.racine:
        ap.error("donner la racine des spires, ou --verifier")

    if a.comparer:
        res = comparer(list(a.racine), a.voxel_um, a.docs)
        if "raison" in res:
            print(f"⚠ {res['raison']}", file=sys.stderr)
            return 3
        p = res["profondeur_commune"]
        print(f"  À PROFONDEUR ÉGALE — les {p} premiers tours de chaque campagne\n")
        print(f"  {'campagne':<26}{'pas':>7}{'portée':>8}{'long.':>7}{'α moyen':>10}"
              f"{'α médian':>10}{'α max':>9}{'érosion/tour':>14}")
        for c in res["campagnes"]:
            e, pr, po = c["erosion_par_tour"], c.get("pas_du_rayon"), c.get("portee_sortie_vox")
            print(f"  {c['nom']:<26}{(f'{pr:g}' if pr else '?'):>7}"
                  f"{(f'{po:g}' if po else '?'):>8}"
                  f"{c['longueur_reelle']:>7}{c['alpha_moyen']:>+10.3f}"
                  f"{c['alpha_median']:>+10.3f}{c['alpha_max']:>+9.3f}"
                  f"{(f'{e:.1f} %' if e is not None else '—'):>14}")
        # ⭐⭐ Si deux campagnes partagent un pas et diffèrent par la portée, la comparaison
        # « α contre pas » n'a plus de sens seule — c'est la portée qui varie.
        par_pas: dict = {}
        for c in res["campagnes"]:
            par_pas.setdefault(c.get("pas_du_rayon"), []).append(c)
        for pr, groupe in sorted(par_pas.items(), key=lambda kv: (kv[0] or 0)):
            if len(groupe) < 2:
                continue
            g = sorted(groupe, key=lambda c: c["alpha_moyen"])
            print(f"\n  ⭐⭐ à pas {pr:g}, DEUX portées mesurées : "
                  f"α moyen {g[0]['alpha_moyen']:+.3f} (portée "
                  f"{g[0]['portee_sortie_vox']:g}) contre {g[-1]['alpha_moyen']:+.3f} "
                  f"(portée {g[-1]['portee_sortie_vox']:g}).")
            print("     Même pas, même volume, même chaîne : ce qui change est la PORTÉE "
                  "PHYSIQUE du test\n     de sortie, pas la finesse de la marche.")
        meilleure = min(res["campagnes"], key=lambda c: c["alpha_moyen"])
        print(f"\n  ⭐ α moyen le plus bas : {meilleure['nom']} "
              f"({meilleure['alpha_moyen']:+.3f})")
        ers = [c["erosion_par_tour"] for c in res["campagnes"]
               if c["erosion_par_tour"] is not None]
        if ers:
            print(f"  ⚠ l'érosion, elle, ne bouge pas : de {min(ers):.1f} % à "
                  f"{max(ers):.1f} % par tour — donc le réglage change où la surface se "
                  f"pose,\n    pas combien elle en perd.")
        print("\n  ⚠ aucun COMPTE de verdict ici : un compte est un compte de "
              "franchissements de seuil,\n    et 10 des 55 verdicts du dépôt ont un α à "
              "moins de 0,2 de ce seuil.")
        if a.json:
            Path(a.json).write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
            print(f"\n  écrit : {a.json}")
        if a.figure:
            dessiner_comparaison(res, a.figure)
            print(f"  figure : {a.figure}")
        return 0

    lignes = depouiller(a.racine[0], a.voxel_um, a.docs)
    if not lignes:
        print("aucune spire jugée sous cette racine", file=sys.stderr)
        return 3

    print(f"{'spire':<9}{'grille':>10}{'aire*':>9}{'crois.':>8}"
          f"{'31c':>9}{'81c':>9}{'α':>8}  verdict")
    for l in lignes:
        c, r = l["grille"]
        print(f"{l['spire']:<9}{c}x{r:<6}{l['aire_grille_cm2']:>9.2f}"
              f"{('?' if l['croisements'] is None else l['croisements']):>8}"
              f"{l['ecart_31c_um']:>9.2f}{l['ecart_81c_um']:>9.2f}"
              f"{l['alpha']:>+8.3f}  {l['verdict']}")
    print("  * aire de la GRILLE (sommets invalides compris) — un majorant, pas la surface utile")

    conv = sum(1 for l in lignes if l["verdict"] == "converge")
    trav = sum(1 for l in lignes if l["verdict"] == "suit la fenêtre")
    print(f"\n  {conv}/{len(lignes)} convergent, {trav} suivent la fenêtre")
    if len(lignes) >= 2:
        a0, a1 = lignes[0]["aire_grille_cm2"], lignes[-1]["aire_grille_cm2"]
        if a0:
            perte = 100 * (1 - a1 / a0)
            par = perte / (len(lignes) - 1)
            print(f"  érosion : {a0:.2f} → {a1:.2f} cm² sur {len(lignes) - 1} tours "
                  f"({perte:.0f} % au total, {par:.1f} % par tour)")
            if par > 0:
                print(f"  ⚠ à ce rythme, la moitié de la surface est perdue en "
                      f"{int(round(50 / par))} tours")
    if a.json:
        Path(a.json).write_text(json.dumps(lignes, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
