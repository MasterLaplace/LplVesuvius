#!/usr/bin/env python3
"""Les 217 greffons du dépôt, par famille et par ce qu'ils savent faire d'eux-mêmes.

⚠⚠ **Ce que cette figure établit**, et c'est l'argument entier du chantier C : une
architecture à greffons n'a pas été construite, elle a été **constatée**. Le skill dit de ne
pas en bâtir une avant le deuxième implémenteur réel ; il y en a deux cent dix-sept, de forme
uniforme, et il leur manquait seulement un registre.

⭐ Les deux colonnes disent la propriété des paliers : le **palier de release** ne porte ni
`experiments/src` ni `inference_xpu/src`, et `lplv` y rend **203 verbes au lieu de 217, sans
erreur ni configuration**. Un palier est ADDITIF, pas divergent — une famille absente
contribue zéro.

⚠ Les barres sont découpées par ce qu'un module DÉCLARE, pas par ce qu'on croit qu'il fait :
`--verifier` (il s'auto-teste) et `--json` (sa sortie est relisible par un autre outil). Les
deux sont lus dans le fichier, donc le compte suit le code sans que personne l'entretienne.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    ./lplv --verbes --json > docs/verbes.json
    uv run python analysis/src/figure_verbes.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LARGEUR, HAUTEUR = 1020, 470
X0, LARG_MAX = 300, 300
FOND, ENCRE, GRIS = (255, 255, 255), (25, 25, 28), (150, 150, 155)
BLEU, AMBRE, PALE = (44, 90, 160), (214, 141, 40), (205, 210, 218)

# ⚠ Ce que la release emporte, LU dans le script qui la fabrique plutôt que recopié ici :
# deux listes de « ce que porte la release » finiraient par ne pas s'accorder.
RELEASE = Path(__file__).resolve().parents[2] / "tools/faire_la_release.sh"


def familles_de_la_release(chemin: Path = RELEASE) -> set[str]:
    """Les dossiers que le palier de production emporte, lus dans `GARDES`."""
    if not chemin.is_file():
        return set()
    texte = chemin.read_text(encoding="utf-8", errors="replace")
    debut = texte.find("GARDES=(")
    if debut == -1:
        return set()
    bloc = texte[debut:texte.index(")", debut)]
    return {l.strip().strip('"') for l in bloc.splitlines()[1:] if l.strip().startswith('"')}


def porte(famille: str, gardes: set[str]) -> bool:
    """La release porte-t-elle cette famille ?"""
    return any(famille == g or famille.startswith(g + "/") for g in gardes)


def repartir(verbes: list[dict]) -> dict[str, dict[str, int]]:
    """Par famille : combien s'auto-testent, combien rendent du JSON, combien ni l'un ni l'autre."""
    out: dict[str, dict[str, int]] = {}
    for v in verbes:
        fam = str(Path(v["chemin"]).parent)
        d = out.setdefault(fam, {"les_deux": 0, "verifie": 0, "json": 0, "muet": 0, "total": 0})
        d["total"] += 1
        if v["verifie"] and v["json"]:
            d["les_deux"] += 1
        elif v["verifie"]:
            d["verifie"] += 1
        elif v["json"]:
            d["json"] += 1
        else:
            d["muet"] += 1
    return out


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    faux = [
        {"chemin": "a/x.py", "verifie": True, "json": True},
        {"chemin": "a/y.py", "verifie": True, "json": False},
        {"chemin": "a/z.py", "verifie": False, "json": True},
        {"chemin": "b/w.py", "verifie": False, "json": False},
    ]
    r = repartir(faux)
    v("chaque verbe tombe dans une seule case",
      r["a"]["les_deux"] == 1 and r["a"]["verifie"] == 1 and r["a"]["json"] == 1)
    v("... donc la somme des cases est le total",
      all(d["les_deux"] + d["verifie"] + d["json"] + d["muet"] == d["total"] for d in r.values()))
    v("un muet est compte comme muet", r["b"]["muet"] == 1 and r["b"]["total"] == 1)
    v("deux familles restent deux familles", set(r) == {"a", "b"})

    gardes = familles_de_la_release()
    v("les gardes de la release se lisent dans le script", "analysis/src" in gardes)
    v("... et la release porte bien analysis/src", porte("analysis/src", gardes))
    v("... et tools", porte("tools", gardes))
    # ⭐ Le contrôle qui donne son sens à la figure : sans famille absente, les deux colonnes
    # seraient identiques et la propriété des paliers ne se verrait pas.
    v("... et PAS experiments/src", not porte("experiments/src/excision", gardes))
    v("... ni inference_xpu/src", not porte("inference_xpu/src", gardes))
    v("un script de release absent ne fait pas planter", familles_de_la_release(Path("/nexiste/pas")) == set())

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    racine = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entree", type=Path, default=racine / "docs/verbes.json")
    ap.add_argument("--sortie", type=Path, default=racine / "docs/images/56_verbes.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer `./lplv --verbes --json > {a.entree}`", file=sys.stderr)
        return 1
    verbes = json.loads(a.entree.read_text(encoding="utf-8"))
    parts = repartir(verbes)
    gardes = familles_de_la_release()

    from PIL import Image, ImageDraw, ImageFont

    def police(taille):
        for n in ("DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
            try:
                return ImageFont.truetype(n, taille)
            except OSError:
                continue
        return ImageFont.load_default()

    im = Image.new("RGB", (LARGEUR, HAUTEUR), FOND)
    d = ImageDraw.Draw(im)
    f_titre, f_txt, f_pt = police(21), police(14), police(12)

    total = sum(p["total"] for p in parts.values())
    livres = sum(p["total"] for f, p in parts.items() if porte(f, gardes))
    d.text((40, 26), f"{total} greffons de forme uniforme, découverts et non déclarés",
           font=f_titre, fill=ENCRE)
    d.text((40, 56), f"`lplv` les nomme  ·  {sum(p['les_deux'] + p['verifie'] for p in parts.values())} "
                     f"s'auto-testent  ·  {sum(p['les_deux'] + p['json'] for p in parts.values())} "
                     f"rendent du JSON", font=f_txt, fill=GRIS)

    echelle = LARG_MAX / max(p["total"] for p in parts.values())
    y = 104
    d.text((X0, y - 22), "arbre complet", font=f_pt, fill=GRIS)
    d.text((X0 + LARG_MAX + 90, y - 22), "palier de release", font=f_pt, fill=GRIS)
    for fam in sorted(parts, key=lambda k: -parts[k]["total"]):
        p = parts[fam]
        d.text((40, y + 6), fam, font=f_txt, fill=ENCRE)
        x = X0
        for cle, couleur in (("les_deux", BLEU), ("verifie", AMBRE), ("json", PALE), ("muet", (235, 236, 240))):
            larg = p[cle] * echelle
            if larg >= 1:
                d.rectangle([x, y, x + larg, y + 26], fill=couleur)
                x += larg
        d.text((X0 + p["total"] * echelle + 8, y + 6), str(p["total"]), font=f_pt, fill=GRIS)

        # La colonne de droite : ce que la release porte, et ce qu'elle laisse.
        xr = X0 + LARG_MAX + 90
        if porte(fam, gardes):
            d.rectangle([xr, y, xr + p["total"] * echelle * 0.55, y + 26], fill=BLEU)
            d.text((xr + p["total"] * echelle * 0.55 + 8, y + 6), str(p["total"]), font=f_pt, fill=GRIS)
        else:
            d.rectangle([xr, y, xr + 46, y + 26], outline=PALE)
            d.text((xr + 54, y + 6), "absent, 0 verbe, sans erreur", font=f_pt, fill=GRIS)
        y += 46

    y += 14
    for i, (couleur, mot) in enumerate((
            (BLEU, "s'auto-teste ET rend du JSON"), (AMBRE, "s'auto-teste seulement"),
            (PALE, "rend du JSON seulement"), ((235, 236, 240), "ni l'un ni l'autre"))):
        d.rectangle([40 + i * 250, y, 40 + i * 250 + 16, y + 14], fill=couleur)
        d.text((40 + i * 250 + 24, y), mot, font=f_pt, fill=GRIS)

    d.text((40, y + 34),
           f"Le palier de release rend {livres} verbes au lieu de {total} : un palier est ADDITIF, "
           f"pas divergent.", font=f_txt, fill=ENCRE)
    d.text((40, y + 56),
           "Rien ici n'est déclaré à la main : la famille vient du chemin, `--verifier` et `--json` "
           "sont lus dans le fichier.", font=f_pt, fill=GRIS)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(a.sortie)
    print(f"{total} verbes, {livres} dans le palier de release  →  {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
