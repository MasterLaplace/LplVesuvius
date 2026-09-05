#!/usr/bin/env python3
"""Le peigne d'échantillonnage contre le réseau de feuilles — pourquoi 64 ne peut pas marcher.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat d'`A2 ter` tient en deux nombres — 3,89 écarts par
cellule contre une borne de 0,5 — et un lecteur qui les voit en tableau doit croire sur parole
que le second est une limite et non un réglage. Le **repliement se regarde** : dessiner les
feuilles à leur pas mesuré, puis les points où le champ est échantillonné, montre d'un coup
qu'une cellule saute presque quatre feuilles.

⭐⭐ La bande du bas est le contrôle, et sans elle la figure ne prouverait rien : le **même**
réseau échantillonné à la demi-période (Nyquist) est traversé par deux points par feuille. Ce
n'est donc pas « le réseau est trop fin pour être échantillonné », c'est **« ce produit-là
l'échantillonne trop grossièrement »** — deux énoncés que la figure du haut seule confond.

⚠ Les deux bandes couvrent **exactement la même longueur physique**, sinon on comparerait deux
zooms. Et les feuilles sont tracées au pas **mesuré** du rouleau (`76`), pas à un pas rond.

⚠ Les nombres sont LUS dans `docs/mesures/le_pas_de_la_grille.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_le_pas_de_la_grille.py --verifier
    uv run python src/figures/figure_le_pas_de_la_grille.py \\
        --sortie docs/images/75_le_pas_de_la_grille.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
VERT = (52, 122, 72)
FEUILLE = (168, 168, 172)


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    return [
        f"une cellule de la grille publiee couvre {m['cellules_par_pas']:.2f} ecarts "
        f"inter-feuilles ({m['pas_grille_vox']} voxels = {m['pas_grille_um']:.0f} um).",
        f"un residu s'integre feuille a feuille, donc il faut deux echantillons par ecart : "
        f"{m['pas_maximal_utile_vox']:.2f} voxels au plus.",
        f"le produit publie est {m['trop_grossier_de']:.1f} fois trop grossier — ce n'est pas "
        "un seuil choisi, c'est Nyquist.",
        "le champ n'est donc pas bruite a cette echelle : il est REPLIE, et un gradient replie "
        "rend un residu sans rapport avec la feuille.",
    ]


def bande(art, x0: int, y: int, largeur: int, hauteur: int, pas_um: float,
          echantillon_um: float, etendue_um: float, couleur, petit, titre: str) -> int:
    """Une bande : les feuilles au pas mesuré, et les points d'échantillonnage par-dessus.

    Rend le nombre d'échantillons dessinés — ⚠ il est **compté**, pas annoncé : une bande qui
    en dessinerait zéro se lirait comme une bande sans échantillonnage plutôt que comme un bug.
    """
    art.text((x0, y - 17), titre, fill=DISCRET, font=petit)
    art.rectangle([x0, y, x0 + largeur, y + hauteur], outline=(215, 215, 215))
    par_um = largeur / etendue_um
    d = pas_um
    while d < etendue_um:
        x = x0 + d * par_um
        art.line([x, y + 1, x, y + hauteur - 1], fill=FEUILLE, width=1)
        d += pas_um
    n = 0
    e = 0.0
    while e <= etendue_um:
        x = x0 + e * par_um
        art.line([x, y - 6, x, y + hauteur + 6], fill=couleur, width=2)
        art.ellipse([x - 3, y + hauteur + 5, x + 3, y + hauteur + 11], fill=couleur)
        n += 1
        e += echantillon_um
    return n


def dessiner(mesures: list[dict], sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    reels = [m for m in mesures if "refus" not in m]
    if not reels:
        raise SystemExit("aucune mesure exploitable")
    m = reels[0]
    gros, moyen, petit = police(17, 13, 11)

    # ⚠ L'étendue couvre CINQ cellules publiées : moins ne montrerait pas la périodicité du
    # peigne, plus tasserait les feuilles jusqu'à les rendre indiscernables.
    etendue = 5.0 * m["pas_grille_um"]
    nyquist_um = m["pas_maximal_utile_vox"] * m["voxel_um"]

    marge, largeur_bande, hauteur_bande = 30, 940, 62
    lignes = prose(m)
    L = marge * 2 + largeur_bande
    H = 96 + 2 * (hauteur_bande + 62) + len(lignes) * 19 + 26
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Le peigne d'echantillonnage contre le reseau de feuilles",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['rouleau']}, voxel {m['voxel_um']:g} um, ecart inter-feuilles "
             f"{m['pas_inter_feuilles_um']:g} um (mesure) — {etendue / 1000:.1f} mm de large",
             fill=DISCRET, font=moyen)

    y = 92
    n_publie = bande(art, marge, y, largeur_bande, hauteur_bande,
                     m["pas_inter_feuilles_um"], m["pas_grille_um"], etendue, AMBRE, petit,
                     f"publie — un echantillon tous les {m['pas_grille_vox']} voxels "
                     f"({m['pas_grille_um']:.0f} um)")
    art.text((marge, y + hauteur_bande + 18),
             f"{n_publie} echantillons sur {etendue / m['pas_inter_feuilles_um']:.0f} feuilles",
             fill=AMBRE, font=petit)

    y2 = y + hauteur_bande + 62
    n_nyq = bande(art, marge, y2, largeur_bande, hauteur_bande,
                  m["pas_inter_feuilles_um"], nyquist_um, etendue, VERT, petit,
                  f"ce qu'il faudrait — un echantillon tous les "
                  f"{m['pas_maximal_utile_vox']:.2f} voxels ({nyquist_um:.0f} um)")
    art.text((marge, y2 + hauteur_bande + 18),
             f"{n_nyq} echantillons sur les MEMES "
             f"{etendue / m['pas_inter_feuilles_um']:.0f} feuilles — deux par ecart",
             fill=VERT, font=petit)

    bas = H - len(lignes) * 19 - 14
    for j, l in enumerate(lignes):
        art.text((marge, bas + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"rouleau": m["rouleau"], "echantillons_publie": n_publie,
            "echantillons_nyquist": n_nyq, "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    faux = [{"rouleau": "PHerc0139", "voxel_um": 9.362, "pas_inter_feuilles_um": 154.1,
             "pas_grille_vox": 64, "pas_grille_um": 599.2, "cellules_par_pas": 3.888,
             "pas_maximal_utile_vox": 8.23, "trop_grossier_de": 7.78, "resout_le_pas": False}]
    lignes = prose(faux[0])
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle donne les DEUX nombres, le mesure et la borne",
      any("3.89" in x for x in lignes) and any("8.23" in x for x in lignes), str(lignes[:2]))
    # ⚠⚠ La borne DOIT être présentée comme Nyquist et non comme un réglage, sinon tout le
    # résultat se lit comme un seuil qu'on pourrait desserrer.
    v("... et elle dit que la borne est Nyquist, pas un seuil choisi",
      any("Nyquist" in x for x in lignes), str(lignes[2]))
    v("... et que le champ est REPLIE, pas bruite",
      any("REPLIE" in x for x in lignes), str(lignes[-1]))

    import shutil
    import tempfile
    d = Path(tempfile.mkdtemp())
    r = dessiner(faux, d / "x.png")
    # ⭐⭐ LE CONTRÔLE QUI COMPTE : le peigne publié doit sauter des feuilles et le peigne de
    # Nyquist doit en couvrir deux par écart. Sans ces deux comptes, une bande vide ou une
    # bande saturée passerait pour un dessin.
    v("le peigne publie saute des feuilles",
      r["echantillons_publie"] == 6, f"{r['echantillons_publie']} sur 5 cellules")
    v("... et le peigne de Nyquist en couvre deux par ecart",
      r["echantillons_nyquist"] >= 2 * 5 * faux[0]["cellules_par_pas"],
      f"{r['echantillons_nyquist']} echantillons")
    v("une mesure entierement en refus est REFUSEE, pas dessinee vide",
      _leve(lambda: dessiner([{"rouleau": "x", "refus": "injoignable"}], d / "y.png")))
    shutil.rmtree(d, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_pas_de_la_grille.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_le_pas_de_la_grille.png")
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
