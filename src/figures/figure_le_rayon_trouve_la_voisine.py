#!/usr/bin/env python3
"""Ce qu'un rayon de recherche trouve, selon sa taille — en coupe, à l'échelle mesurée.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat de
[`07`](../../docs/07_reparee_nest_pas_propre.md) §11 est une CAUSE, pas un nombre : trois familles
de paramètres cessent de compter ensemble parce que le rayon trouvait la spire **voisine**, qui
est de la géométrie parfaitement normale. Cette phrase demande une image — un lecteur qui voit un
cercle engloutir trois feuilles comprend en une seconde ce qu'aucune table de rho ne lui dira.

⭐⭐ LA COUPE EST À L'ÉCHELLE, ET SES TROIS NOMBRES SONT MESURÉS. Le pas inter-feuilles vient de
`11` §3 (**142,8 µm**, cv 1,8 %), mesuré ailleurs et avant — c'est ce qui rend le rayon corrigé
non ajustable. Les deux rayons sont les **minorants** que chaque fichier de mesure impose à
lui-même : une distance rendue par `proximity.py` est plafonnée par le rayon, donc la plus grande
médiane du fichier en est une borne inférieure. Aucune date, aucun journal.

⚠ LE CERCLE DE GAUCHE EST UN MINORANT, et la figure le dit au lieu de le taire : le rayon
employé était **au moins** celui-là. Le dessiner comme une valeur exacte affirmerait ce que la
donnée ne peut pas établir.

⚠ Les nombres sont LUS dans `docs/mesures/le_rayon_des_mesures.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_le_rayon_trouve_la_voisine.py --verifier
    uv run python src/figures/figure_le_rayon_trouve_la_voisine.py \\
        --mesure docs/mesures/le_rayon_des_mesures.json \\
        --sortie docs/images/07_le_rayon_trouve_la_voisine.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)
FEUILLE = (92, 96, 104)

ANOMALIE_UM = 50.0
"""L'écart que la métrique cherche : deux parties NON adjacentes qui se frôlent.

⚠ C'est un ordre de grandeur d'illustration, **pas une mesure** — la queue basse du rapport n'a
pas de valeur unique. Il est choisi bien sous le pas de feuille pour montrer ce que le cercle
doit isoler, et la légende le dit plutôt que de le laisser passer pour un chiffre."""


def nombres(mesure: dict) -> dict:
    """
    @brief Le pas de feuille et les deux minorants de rayon, lus dans la mesure.
    """
    bornes = mesure.get("borne_du_rayon") or {}
    pas = mesure.get("pas_entre_feuilles_um")
    ancien = bornes.get("proximity_scroll1.jsonl")
    corrige = bornes.get("proximity_scroll1_rayon_corrige.jsonl")
    if not pas or not ancien or not corrige:
        raise SystemExit("mesure incomplète : il faut le pas et les deux bornes de rayon")
    return dict(pas=float(pas), ancien=float(ancien), corrige=float(corrige))


def prose(n: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    return [
        f"le pas entre deux feuilles vaut {n['pas']:.1f} um, mesure ailleurs et avant.",
        f"l'ancien rayon portait a AU MOINS {n['ancien']:.0f} um, soit "
        f"{n['ancien'] / n['pas']:.1f} pas : il trouvait la spire VOISINE,",
        "qui est de la geometrie normale, et noyait l'anomalie dedans.",
        f"le rayon tire de la physique porte a {n['corrige']:.0f} um, soit "
        f"{n['corrige'] / n['pas']:.2f} pas : il ne peut trouver QUE l'anomalie.",
    ]


def dessiner(mesure: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    n = nombres(mesure)

    # ⚠ L'ECHELLE est commune aux deux panneaux, sinon les deux cercles paraitraient de meme
    # taille et la figure dirait exactement l'inverse de la mesure.
    px_par_um = 0.42
    larg_p, haut_p = 470, 400
    L, H = 2 * larg_p + 90, haut_p + 240
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)

    d.text((44, 26), "ce qu'un rayon de recherche trouve, selon sa taille",
           fill=TEXTE, font=gros)
    d.text((44, 52), "coupe a l'echelle -- les feuilles du rouleau, vues de cote",
           fill=DISCRET, font=moyen)

    for j, (cle, couleur, titre) in enumerate(
            (("ancien", ROUGE, "ancien rayon : AU MOINS %.0f um" % n["ancien"]),
             ("corrige", AMBRE, "rayon de la physique : %.0f um" % n["corrige"]))):
        x0 = 44 + j * (larg_p + 2)
        y0 = 96
        cx, cy = x0 + larg_p // 2, y0 + haut_p // 2
        d.text((x0, y0 - 24), titre, fill=couleur, font=moyen)
        d.rectangle([x0, y0, x0 + larg_p, y0 + haut_p], outline=(60, 60, 60))

        # ⚠ Les feuilles sont tracees AVANT les cercles : par-dessus, un cercle ne montrerait
        # plus lesquelles il englobe, ce qui est tout le sujet.
        k = 1
        while True:
            dy = int(k * n["pas"] * px_par_um)
            if dy > haut_p // 2:
                break
            for signe in (-1, 1):
                yy = cy + signe * dy
                d.line([x0 + 4, yy, x0 + larg_p - 4, yy], fill=FEUILLE, width=2)
            k += 1
        d.line([x0 + 4, cy, x0 + larg_p - 4, cy], fill=(150, 152, 158), width=3)

        # L'anomalie : une partie non adjacente qui frole la feuille centrale.
        ya = cy - int(ANOMALIE_UM * px_par_um)
        d.line([cx - 60, ya, cx + 60, ya], fill=AMBRE, width=3)

        rayon = int(n[cle] * px_par_um)
        d.ellipse([cx - rayon, cy - rayon, cx + rayon, cy + rayon], outline=couleur, width=2)
        if cle == "ancien":
            # ⚠ Le minorant se DIT : une fleche vers l'exterieur plutot qu'un cercle net, sinon
            # la figure affirme un rayon exact que la donnee ne peut pas etablir.
            d.line([cx + rayon, cy, cx + rayon + 26, cy], fill=couleur, width=2)
            d.polygon([(cx + rayon + 32, cy), (cx + rayon + 22, cy - 5),
                       (cx + rayon + 22, cy + 5)], fill=couleur)
            d.text((cx + rayon - 30, cy + 8), "au moins", fill=couleur, font=petit)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=TEXTE)

        pas_couverts = n[cle] / n["pas"]
        # ⚠ Un fond opaque sous le verdict : pose a nu, il tombait SUR une feuille, et une
        # ligne de texte barree par un trait de la meme figure se lit mal deux fois -- le
        # texte et la feuille.
        d.rectangle([x0 + 2, y0 + haut_p - 50, x0 + larg_p - 2, y0 + haut_p - 6], fill=FOND)
        d.text((x0 + 8, y0 + haut_p - 46),
               f"porte a {pas_couverts:.1f} pas de feuille", fill=couleur, font=moyen)
        d.text((x0 + 8, y0 + haut_p - 26),
               ("il trouve la spire VOISINE, geometrie normale"
                if pas_couverts >= 1.0 else
                "il ne peut trouver QUE l'anomalie"), fill=DISCRET, font=petit)

    bas = 96 + haut_p + 16
    d.line([44, bas + 6, 68, bas + 6], fill=FEUILLE, width=2)
    d.text((78, bas), "une feuille du rouleau", fill=DISCRET, font=petit)
    d.line([300, bas + 6, 324, bas + 6], fill=AMBRE, width=3)
    d.text((334, bas), f"l'anomalie cherchee (~{ANOMALIE_UM:.0f} um, illustration)",
           fill=DISCRET, font=petit)
    d.ellipse([640, bas + 2, 648, bas + 10], fill=TEXTE)
    d.text((658, bas), "la cellule mesuree", fill=DISCRET, font=petit)

    for k, ligne in enumerate(prose(n)):
        d.text((44, bas + 30 + k * 20), ligne, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"pas_um": n["pas"], "ancien_um": n["ancien"], "corrige_um": n["corrige"],
            "pas_couverts_ancien": n["ancien"] / n["pas"],
            "pas_couverts_corrige": n["corrige"] / n["pas"], "sortie": str(sortie)}


def verifier() -> int:
    """Auto-test HORS LIGNE : la lecture des nombres et la prose."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    faux = {"pas_entre_feuilles_um": 142.8,
            "borne_du_rayon": {"proximity_scroll1.jsonl": 382.6,
                               "proximity_scroll1_rayon_corrige.jsonl": 125.8}}
    n = nombres(faux)
    v("le pas et les deux bornes sont lus", (n["pas"], n["ancien"], n["corrige"])
      == (142.8, 382.6, 125.8), str(n))
    # ⚠⚠ LE FAIT QUE LA FIGURE EXISTE POUR MONTRER, asserte : l'ancien depasse un pas de
    # feuille, le corrige non. Si ce rapport s'inversait un jour, la figure dirait le
    # contraire de la mesure et il faudrait la refaire.
    v("l'ancien rayon depasse un pas de feuille", n["ancien"] / n["pas"] > 1.0)
    v("... et le corrige ne le depasse pas", n["corrige"] / n["pas"] <= 1.0)
    # ⚠ Une mesure incomplete doit REFUSER plutot que dessiner un cercle par defaut.
    for manque in ({"pas_entre_feuilles_um": 142.8, "borne_du_rayon": {}},
                   {"borne_du_rayon": {"proximity_scroll1.jsonl": 382.6,
                                       "proximity_scroll1_rayon_corrige.jsonl": 125.8}}):
        try:
            nombres(manque)
            v("une mesure incomplete est refusee", False, str(manque))
        except SystemExit:
            v("une mesure incomplete est refusee", True)

    lignes = prose(n)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle nomme la spire voisine", any("VOISINE" in l for l in lignes), str(lignes))
    # ⚠ Le rapport est recalcule ici a la main : 382,6 / 142,8 = 2,7.
    v("... et elle dit les 2,7 pas", any("2.7 pas" in l for l in lignes), str(lignes))

    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_rayon_des_mesures.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "07_le_rayon_trouve_la_voisine.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
