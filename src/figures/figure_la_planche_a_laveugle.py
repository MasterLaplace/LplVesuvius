"""La planche à l'aveugle — trente cubes ouverts, et rien qui dise lesquels retiennent.

⚠⚠ **Ce que cette image doit rendre évident.** Trente tuiles, numérotées de 1 à 30, chacune la
couche du MILIEU d'un chunk du rouleau. Quinze viennent de chunks où la marche de `190` tient sa
feuille, quinze de chunks appariés DANS LE MÊME SEGMENT où elle ne la tient pas. L'ordre est une
permutation semée, et **l'image ne dit pas lequel est lequel**.

⚠⚠⚠ ET C'EST LA PROPRIÉTÉ QUE SA BATTERIE VÉRIFIE : la planche est dessinée **exactement la même**
que la mesure porte sa clef ou non. Une figure qui changerait d'un octet à la levée serait une figure
qui lisait la clef, donc une planche qui n'a jamais été aveugle.

  uv run python src/figures/figure_la_planche_a_laveugle.py \\
      --json docs/mesures/ouvrir_les_quinze.json \\
      --sortie docs/images/195_la_planche_a_laveugle.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)

AGRANDISSEMENT = 2
ECART = 14
BANDEAU = 20


def lire(chemin: Path) -> dict:
    """Le JSON d'`ouvrir_les_quinze.py` — et SEULEMENT sa planche.

    ⚠⚠⚠ LA CLEF N'EST JAMAIS LUE ICI, et ce n'est pas une politesse : c'est la seule chose qui rende
    l'image aveugle une fois la levée faite. Le champ existe dans le fichier final ; cette fonction
    ne le renvoie pas, donc `dessiner` ne peut pas le poser.
    """
    return lire_dict(json.loads(chemin.read_text(encoding="utf-8")), str(chemin))


def _forme(p: dict) -> tuple[int, int]:
    """La forme d'une tuile — carrée par `cote`, ou rectangulaire par `hauteur` et `largeur`.

    ⚠⚠ UN SEUL DESSINATEUR POUR LES DEUX PLANCHES, ET C'EST DELIBERE : deux modules qui dessinent
    « une planche aveugle » seraient deux definitions de ce qu'est une planche aveugle, libres de ne
    plus s'accorder sur ce qui fuit et ce qui ne fuit pas.
    """
    if p.get("hauteur") is not None and p.get("largeur") is not None:
        return int(p["hauteur"]), int(p["largeur"])
    return int(p["cote"]), int(p["cote"])


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list]:
    p = d["la_planche"]
    hau, lar = _forme(p)
    cols, rangs = int(p["colonnes"]), int(p["rangs"])
    tw, th = lar * AGRANDISSEMENT, hau * AGRANDISSEMENT
    L = ECART + cols * (tw + ECART)
    entete, pied = 104, 72
    H = entete + rangs * (th + BANDEAU + ECART) + pied
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(21, 14, 12)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(ECART, 20, "Trente cubes du rouleau, ouverts — lesquels tiennent une feuille ?",
           gros, ENCRE)
    vue = d.get("la_vue_declaree") or "La couche du MILIEU de chaque cube"
    ecrire(ECART, 52,
           f"{vue[0].upper()}{vue[1:]} · {hau}×{lar} voxels à 2,4 µm · niveau de gris "
           f"COMMUN aux trente, tiré du mélange "
           f"[{d['le_niveau_commun'].get('bas')} ; {d['le_niveau_commun'].get('haut')}]",
           petit, GRIS)
    ecrire(ECART, 72,
           "Quinze retiennent, quinze sont leurs contrôles appariés DANS LE MÊME SEGMENT. "
           "L'ordre est une permutation semée. Rien ici ne dit lequel est lequel.",
           petit, GRIS)

    for place in range(len(p["ordre"])):
        c, r = place % cols, place // cols
        x = ECART + c * (tw + ECART)
        y = entete + r * (th + BANDEAU + ECART)
        tuile = Image.frombytes("L", (lar, hau), bytes.fromhex(p["octets"][place]))
        img.paste(tuile.resize((tw, th), Image.NEAREST).convert("RGB"), (x, y))
        art.rectangle([x, y, x + tw - 1, y + th + BANDEAU - 1], outline=TRAIT, width=1)
        cadres.append((x, y, x + tw, y + th + BANDEAU))
        ecrire(x + 6, y + th + 3, f"{place + 1}", moyen, ENCRE)

    yb = entete + rangs * (th + BANDEAU + ECART) + 6
    ecrire(ECART, yb,
           f"{d['lappariement'].get('segments_apparies')} segments · "
           f"{d['lappariement'].get('sans_paire')} retenants sans paire disponible · "
           "aucune tuile ne porte son camp, aucune n'est retouchée.", petit, GRIS)
    ecrire(ECART, yb + 20,
           "⚠ Ce qui sera noté n'est pas un trait mais une ASSIGNATION : quinze numéros, déposés "
           "une fois, dont le nul est exactement hypergéométrique.", petit, ENCRE)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    import copy  # noqa: PLC0415

    d = lire(json_path)
    chemin, poses, cadres = dessiner(d, sortie)
    img = Image.open(chemin)
    p = d["la_planche"]
    hau, lar = _forme(p)
    attendue = (ECART + int(p["colonnes"]) * (lar * AGRANDISSEMENT + ECART),
                104 + int(p["rangs"]) * (hau * AGRANDISSEMENT + BANDEAU + ECART) + 72)
    v("l'image est écrite et a la taille que la planche impose", img.size == attendue,
      f"{img.size} contre {attendue}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:200])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:200])
    v("il y a un cadre par tuile", len(cadres) == len(p["ordre"]), f"{len(cadres)} cadres")
    numeros = sorted(int(t) for _x, _y, t, _f in poses if t.isdigit())
    v("★★★ chaque place porte son numéro, une fois et une seule",
      numeros == list(range(1, len(p["ordre"]) + 1)), f"{len(numeros)} numéros")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    # ⚠⚠⚠ LA GARDE QUI FAIT TOUT LE TRAVAIL : LA PLANCHE EST LA MEME AVEC ET SANS CLEF.
    brut = json.loads(json_path.read_text(encoding="utf-8"))
    avec = copy.deepcopy(brut)
    avec["la_cle"] = list(range(1, len(p["ordre"]) // 2 + 1))
    avec["la_note"] = {"les_justes": 15}
    tmp = sortie.with_name(sortie.stem + "_avec_clef.png")
    dessiner(lire_dict(avec), tmp)
    v("★★★★ la planche est bit-identique que la mesure porte sa clef ou non",
      tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    # ★★★★ CHAQUE TUILE EST BIEN CELLE DE LA MESURE, ET PAS UN MOTIF DESSINE.
    for place in (0, 7, 29 if len(p["ordre"]) > 29 else len(p["ordre"]) - 1):
        faux = copy.deepcopy(brut)
        faux["la_planche"]["octets"][place] = "ff" * (hau * lar)
        tmp2 = sortie.with_name(sortie.stem + "_sonde.png")
        dessiner(lire_dict(faux), tmp2)
        v(f"★★★★ la tuile {place + 1} vient bien de la mesure",
          tmp2.read_bytes() != octets)
        tmp2.unlink(missing_ok=True)

    # ★★★ L'ORDRE EST CELUI DE LA MESURE : LE CHANGER CHANGE L'IMAGE.
    faux = copy.deepcopy(brut)
    faux["la_planche"]["octets"] = list(reversed(faux["la_planche"]["octets"]))
    tmp3 = sortie.with_name(sortie.stem + "_ordre.png")
    dessiner(lire_dict(faux), tmp3)
    v("★★★ l'ordre posé est celui que la mesure a tiré", tmp3.read_bytes() != octets)
    tmp3.unlink(missing_ok=True)

    # ⚠⚠ UNE MESURE MAL FORMEE EST REFUSEE, JAMAIS COMPLETEE.
    for casse, quoi in ((lambda x: x["la_planche"].pop("ordre"), "sans ordre"),
                        (lambda x: x["la_planche"]["octets"].pop(), "à court de tuiles"),
                        (lambda x: x["la_planche"].__setitem__("octets",
                                                               ["00"] * len(p["ordre"])),
                         "aux tuiles tronquées"),
                        (lambda x: [x["la_planche"].pop(k2, None)
                                    for k2 in ("cote", "hauteur", "largeur")],
                         "sans forme de tuile")):
        faux = copy.deepcopy(brut)
        casse(faux)
        refuse = False
        try:
            lire_dict(faux)
        except ValueError:
            refuse = True
        v(f"une mesure {quoi} est refusée", refuse)

    print(f"figure_la_planche_a_laveugle.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def lire_dict(brut: dict, ou: str = "la mesure") -> dict:
    """La lecture d'une planche aveugle, carrée ou non — et SEULEMENT sa planche."""
    p = brut.get("la_planche") or {}
    for cle in ("ordre", "octets", "colonnes", "rangs"):
        if p.get(cle) is None:
            raise ValueError(f"{ou} : la planche n'a pas de {cle}")
    if p.get("cote") is None and (p.get("hauteur") is None or p.get("largeur") is None):
        raise ValueError(f"{ou} : la planche ne dit pas la forme de ses tuiles")
    if len(p["octets"]) != len(p["ordre"]):
        raise ValueError(f"{ou} : {len(p['octets'])} tuiles pour {len(p['ordre'])} places")
    h, w = _forme(p)
    attendu = 2 * h * w
    mauvaises = [i for i, x in enumerate(p["octets"]) if len(x) != attendu]
    if mauvaises:
        raise ValueError(f"{ou} : tuiles de mauvaise taille {mauvaises[:4]}")
    return {"la_planche": p, "la_couche_montree": brut.get("la_couche_montree"),
            "la_vue_declaree": brut.get("la_vue_declaree"),
            "le_niveau_commun": brut.get("le_niveau_commun") or {},
            "lappariement": brut.get("lappariement") or {}}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "ouvrir_les_quinze.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "195_la_planche_a_laveugle.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
