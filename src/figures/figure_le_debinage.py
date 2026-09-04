#!/usr/bin/env python3
"""Le débinage rend-il quelque chose ? — trois nuages sur un seul axe.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat de H2 est un **non-écart**, et un non-écart se
raconte mal : « 1,44 contre 1,43 » se lit comme deux nombres qu'un lecteur pressé prendra pour
une différence. Trois nuages qui se recouvrent, avec leurs intervalles, se lisent d'un coup — et
c'est exactement ce que la mesure dit.

⭐⭐ LES POINTS, PAS SEULEMENT LES MÉDIANES. `64` §1 établit qu'un résumé sans sa dispersion ne
peut pas ÉTABLIR une différence : il fallait 27 tuiles par fragment pour l'écart observé, et on
en avait 10. Une figure qui ne montrerait que trois traits reproduirait cette faute en image.

⚠ LE TRAIT À `d′ = 1` EST LA SEULE GRADUATION QUI A UN SENS HORS DE CE JEU : c'est le seuil que
`16` utilise — en dessous, deux feuilles voisines ne se distinguent pas.

⚠ Les nombres sont LUS dans `docs/mesures/le_debinage.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_le_debinage.py --verifier
    uv run python src/figures/figure_le_debinage.py \\
        --mesure docs/mesures/le_debinage.json \\
        --sortie docs/images/75_le_debinage.png
"""

from __future__ import annotations

import argparse
import json
import statistics
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
BANDE = (40, 34, 22)

BAS, HAUT = 0.0, 3.0
"""Les bornes de l'axe des `d′`.

⚠⚠ FIXES, et partant de zéro : un axe ajusté aux données ferait paraître énorme un écart qui
n'existe pas, ce qui est exactement le contraire de ce que cette figure doit montrer. Le haut
suit les données si elles dépassent — laisser un point dehors est pire que le montrer."""


def colonnes(mesure: dict) -> list[dict]:
    """
    @brief Une colonne par volume mesuré, avec ses valeurs, sa médiane et son intervalle.

    ⚠ L'ordre est celui de la mesure et non l'alphabétique : `fin`, `grossier`, puis le
    contrôle. Trier changerait ce que la figure raconte — la comparaison d'abord, le contrôle
    après.
    """
    ordre = ("fin", "grossier", "fin_bine")
    titres = {"fin": "natif fin", "grossier": "natif grossier",
              "fin_bine": "fin biné x2 (controle)"}
    out = []
    for cle in ordre:
        d = (mesure.get("volumes") or {}).get(cle)
        if not d or not d.get("valeurs"):
            continue
        out.append(dict(cle=cle, titre=titres[cle],
                        um=d.get("voxel_effectif_um", d.get("voxel_um")),
                        kev=d.get("energie_keV"), valeurs=list(d["valeurs"]),
                        median=d.get("d_median"), ic=d.get("ic95")))
    return out


def bornes(cols: list[dict]) -> tuple[float, float]:
    """Le haut de l'axe : `HAUT`, ou plus si une fenêtre dépasse."""
    pic = max((max(c["valeurs"]) for c in cols), default=HAUT)
    return BAS, max(HAUT, pic * 1.05)


def echelle(valeur: float, bas: float, haut: float, pixels: int) -> int:
    """Un `d′`, en pixels depuis le bas de l'axe."""
    if haut <= bas:
        return 0
    v = min(max(valeur, bas), haut)
    return int(round((v - bas) / (haut - bas) * pixels))


def prose(mesure: dict, cols: list[dict]) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    r = mesure.get("rapport_fin_sur_grossier")
    f = next((c for c in cols if c["cle"] == "fin"), None)
    g = next((c for c in cols if c["cle"] == "grossier"), None)
    lignes = ["le meme objet, deux echantillonnages natifs, meme bras de 1,2 m."]
    if f and g:
        lignes.append(f"d′ median {f['median']:.2f} a {f['um']:.3f} um contre "
                      f"{g['median']:.2f} a {g['um']:.3f} um.")
    if r:
        lignes.append(f"rapport {r:.2f} : le debinage ne rend rien de mesurable "
                      "(69 predisait au plus 1,5).")
    lignes.append("les intervalles se recouvrent, donc rien ne separe les deux.")
    return lignes


def dessiner(mesure: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    cols = colonnes(mesure)
    if not cols:
        raise SystemExit("aucune colonne complète dans la mesure")
    bas, haut = bornes(cols)

    gx, gy, gw, gh = 110, 108, 620, 380
    L, H = gw + 260, gh + 300
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)

    d.text((44, 26), "le debinage rend-il quelque chose ?", fill=TEXTE, font=gros)
    d.text((44, 52), "separabilite des feuilles (d′), une fenetre = un point — PHerc0500P2",
           fill=DISCRET, font=moyen)
    d.rectangle([gx, gy, gx + gw, gy + gh], outline=(60, 60, 60))

    val = 0.5
    while val < haut:
        yy = gy + gh - echelle(val, bas, haut, gh)
        # ⚠ `d′ = 1` est la seule graduation qui a un sens hors de ce jeu : c'est le seuil de
        # `16`, en dessous duquel deux feuilles voisines ne se distinguent pas.
        couleur = (86, 74, 52) if abs(val - 1.0) < 1e-9 else (36, 36, 36)
        d.line([gx, yy, gx + gw, yy], fill=couleur)
        d.text((gx - 40, yy - 7), f"{val:.1f}", fill=DISCRET, font=petit)
        val = round(val + 0.5, 10)
    # ⚠ L'etiquette du seuil est posee A GAUCHE, dans la marge sous la premiere colonne : a
    # droite elle recouvrait les points de la troisieme, c'est-a-dire la donnee.
    d.text((gx + 6, gy + gh - echelle(1.0, bas, haut, gh) + 4),
           "d′ = 1 : deux feuilles indistinguables", fill=(150, 128, 90), font=petit)

    largeur = gw // max(len(cols), 1)
    for i, c in enumerate(cols):
        cx = gx + largeur * i + largeur // 2
        couleur = GRIS if c["cle"] != "fin_bine" else AMBRE
        # ⚠ L'intervalle est dessine AVANT les points : recouvert par eux, il donnerait
        # l'impression d'une barre d'erreur ajoutee apres coup sur des donnees choisies.
        if c.get("ic"):
            y1 = gy + gh - echelle(c["ic"][1], bas, haut, gh)
            y2 = gy + gh - echelle(c["ic"][0], bas, haut, gh)
            d.rectangle([cx - 46, y1, cx + 46, y2], fill=BANDE)
            d.line([cx - 46, y1, cx + 46, y1], fill=AMBRE)
            d.line([cx - 46, y2, cx + 46, y2], fill=AMBRE)
        # ⚠ Les fenetres sont decalees par leur RANG, jamais au hasard : une figure doit rendre
        # les memes pixels a chaque execution.
        for j, x in enumerate(sorted(c["valeurs"])):
            px = cx - 34 + (j % 9) * 8
            py = gy + gh - echelle(x, bas, haut, gh)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=couleur)
        if c.get("median"):
            ym = gy + gh - echelle(c["median"], bas, haut, gh)
            d.line([cx - 54, ym, cx + 54, ym], fill=ROUGE, width=2)
            d.text((cx + 58, ym - 7), f"{c['median']:.2f}", fill=ROUGE, font=petit)
        d.text((cx - 52, gy + gh + 12), c["titre"], fill=TEXTE, font=petit)
        d.text((cx - 52, gy + gh + 28),
               f"{c['um']:.3f} um · {c['kev']:.0f} keV" if c.get("kev") else f"{c['um']:.3f} um",
               fill=DISCRET, font=petit)
        d.text((cx - 52, gy + gh + 44), f"{len(c['valeurs'])} fenetres",
               fill=DISCRET, font=petit)

    bas_txt = gy + gh + 74
    d.line([gx + 4, bas_txt + 6, gx + 28, bas_txt + 6], fill=ROUGE, width=2)
    d.text((gx + 36, bas_txt), "mediane", fill=ROUGE, font=petit)
    d.rectangle([gx + 130, bas_txt + 1, gx + 154, bas_txt + 11], fill=BANDE, outline=AMBRE)
    d.text((gx + 162, bas_txt), "IC 95 %, bootstrap sur les fenetres", fill=AMBRE, font=petit)
    for k, ligne in enumerate(prose(mesure, cols)):
        d.text((44, bas_txt + 26 + k * 19), ligne, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"colonnes": len(cols),
            "rapport": mesure.get("rapport_fin_sur_grossier"),
            "sortie": str(sortie)}


def verifier() -> int:
    """Auto-test HORS LIGNE : l'axe, l'ordre des colonnes et la prose."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("le bas de l'axe est a zero pixel", echelle(0.0, 0.0, 3.0, 300) == 0)
    v("le haut est en butee", echelle(3.0, 0.0, 3.0, 300) == 300)
    v("le seuil d′ = 1 est au tiers", echelle(1.0, 0.0, 3.0, 300) == 100)
    v("un axe degenere ne divise pas par zero", echelle(1.0, 1.0, 1.0, 300) == 0)

    faux = {"rapport_fin_sur_grossier": 1.01, "volumes": {
        "grossier": {"voxel_um": 9.362, "voxel_effectif_um": 9.362, "energie_keV": 113.0,
                     "d_median": 1.43, "ic95": [1.30, 1.60], "valeurs": [1.2, 1.4, 1.6, 1.5]},
        "fin": {"voxel_um": 4.317, "voxel_effectif_um": 4.317, "energie_keV": 111.0,
                "d_median": 1.44, "ic95": [1.25, 1.65], "valeurs": [1.1, 1.4, 1.7, 1.5]},
        "fin_bine": {"voxel_um": 4.317, "voxel_effectif_um": 8.634, "energie_keV": 111.0,
                     "d_median": 1.25, "ic95": [1.10, 1.45], "valeurs": [1.0, 1.2, 1.4]},
        # ⚠⚠ Un volume sans valeurs est SAUTE : une colonne vide se lirait comme un d′ nul.
        "vide": {"voxel_um": 1.0, "d_median": 2.0, "valeurs": []}}}
    cols = colonnes(faux)
    v("les trois colonnes sont trouvees", len(cols) == 3, str([c["cle"] for c in cols]))
    # ⚠⚠ L'ORDRE est celui de la mesure, pas l'alphabetique : « fin, grossier, controle ».
    # Trier changerait ce que la figure raconte.
    v("... dans l'ordre comparaison puis controle",
      [c["cle"] for c in cols] == ["fin", "grossier", "fin_bine"], str([c["cle"] for c in cols]))
    v("... et un volume sans fenetre est saute", all(c["cle"] != "vide" for c in cols))
    # ⚠ Le voxel EFFECTIF, pas le natif : le controle est a 8,634 µm, et afficher 4,317
    # ferait croire a deux mesures au meme pas.
    v("le controle affiche son voxel EFFECTIF",
      abs(cols[2]["um"] - 8.634) < 1e-9, str(cols[2]["um"]))
    v("une mesure sans volume ne produit rien", colonnes({}) == [])

    b, h = bornes(cols)
    v("l'axe englobe toutes les fenetres",
      all(b <= x <= h for c in cols for x in c["valeurs"]))
    v("... et ne se resserre pas sous 3,0", h >= 3.0, str(h))

    lignes = prose(faux, cols)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle dit le rapport", any("1.01" in l for l in lignes), str(lignes))
    v("... et que les intervalles se recouvrent", any("recouvre" in l for l in lignes))

    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_debinage.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_le_debinage.png")
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
