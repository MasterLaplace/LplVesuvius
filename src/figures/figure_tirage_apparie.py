#!/usr/bin/env python3
"""L'effet mesuré, une fois le bruit d'échantillonnage retiré au lieu d'être borné.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. `07` §10 établit une **borne** — si la réparation déplace la
proximité, c'est de moins que la dispersion d'un tirage. Une borne se raconte mal : « moins de
5 % » se lit comme un résultat mou alors que c'est un aveu d'instrument. Le §12 retire la cause
au lieu de la borner, et ce que ça donne se voit d'un coup : deux barres par trace, et celle de
droite s'effondre.

⭐⭐ LE TRAIT DE BRUIT EST PAR TRACE, PAS GLOBAL. Chaque trace a sa propre dispersion de graine
(`le_bruit_de_lechantillon`), et la comparer à un plafond commun serait généreux pour les traces
calmes et sévère pour les agitées. Le trait dit, trace par trace, ce qu'il fallait dépasser pour
que l'effet soit lisible.

⚠ CE QUE LA FIGURE NE DIT PAS : que la réparation ne fait rien. Elle dit que ce qu'elle fait à
cette grandeur est plus petit que ce qu'on pouvait mesurer avant, et **combien** plus petit.

⚠ Les nombres sont LUS dans les trois mesures, jamais retapés.

Usage :
    uv run python src/figures/figure_tirage_apparie.py --verifier
    uv run python src/figures/figure_tirage_apparie.py \
        --sortie docs/images/07_tirage_apparie.png
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import (etiquette_de_trace as etiquette,  # noqa: E402
                            etiquettes_de_traces as etiquettes,
                            police, prose_tracable,
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)

RACINE = Path(__file__).resolve().parents[2]
MESURES = RACINE / "docs" / "mesures"

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)


def lire(index_p: Path, position_p: Path, bruit_p: Path) -> tuple[dict, dict, dict]:
    """Charge les trois mesures nécessaires à l'appariement.

    Refuse si un fichier manque ou ne porte pas la structure minimale attendue.
    """
    for nom, c in (("index", index_p), ("position", position_p), ("bruit", bruit_p)):
        if not c.is_file():
            raise FileNotFoundError(f"mesure {nom} absente : {c}")
    idx = json.loads(index_p.read_text(encoding="utf-8"))
    pos = json.loads(position_p.read_text(encoding="utf-8"))
    br = json.loads(bruit_p.read_text(encoding="utf-8"))
    if not idx.get("paires"):
        raise ValueError(f"{index_p} ne porte aucune paire")
    if not pos.get("paires"):
        raise ValueError(f"{position_p} ne porte aucune paire")
    return idx, pos, br


def rangees(index: dict, position: dict, bruit: dict) -> list[dict]:
    """
    @brief Une ligne par trace mesurée des DEUX façons, avec son bruit de graine propre.

    ⚠⚠ Appariement par NOM, jamais par ordre : trois fichiers produits par deux outils, et rien
    ne garantit qu'ils rangent leurs lignes pareil. Un appariement positionnel donnerait une
    figure parfaitement lisible dans laquelle chaque barre serait posée sur la mauvaise trace.
    """
    par_pos = {x["trace"]: x for x in position.get("paires", [])}
    par_bruit = {x["trace"]: x for x in bruit.get("lignes", [])}
    out = []
    for x in index.get("paires", []):
        p = par_pos.get(x["trace"])
        b = par_bruit.get(x["trace"])
        if not p or x.get("variation_shortfall_pct") is None \
                or p.get("variation_shortfall_pct") is None:
            continue
        out.append(dict(
            trace=x["trace"],
            index=abs(x["variation_shortfall_pct"]),
            position=abs(p["variation_shortfall_pct"]),
            # ⚠ La DEMI-etendue : l'effet se compte depuis une valeur mediane tandis que
            # l'etendue couvre les deux cotes.
            bruit=(b["shortfall_etendue_pct"] / 2.0) if b else None,
        ))
    return out


def prose(lignes: list[dict]) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    mi = statistics.median(x["index"] for x in lignes)
    mp = statistics.median(x["position"] for x in lignes)
    sous = sum(1 for x in lignes if x["bruit"] and x["position"] < x["bruit"])
    return [
        "en tirant des index de cellules valides, avant et apres ne portent pas",
        f"sur les memes cellules : effet median {mi:.2f} %.",
        f"en tirant des POSITIONS de grille, l'echantillon est le meme : {mp:.2f} %.",
        f"{sous} traces sur {len(lignes)} tombent alors sous leur propre bruit de graine.",
    ]


def dessiner(index: dict, position: dict, bruit: dict, sortie: Path) -> tuple[Path, list, list]:
    from PIL import ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lignes = rangees(index, position, bruit)
    if not lignes:
        raise ValueError("aucune trace mesurée des deux façons")

    # ⚠⚠ L'AXE EST COMMUN AUX DEUX BARRES, evidemment, mais aussi FIXE au maximum observe :
    # l'ajuster par trace ferait paraitre chaque effondrement identique, quelle que soit son
    # ampleur reelle.
    haut = max(max(x["index"], x["position"]) for x in lignes) * 1.12
    larg_barre, pas_ligne = 420, 34
    L, H = 900, 150 + pas_ligne * len(lignes) + 130
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        d.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(44, 26, "l'effet de la reparation, bruit retire au lieu d'etre borne",
           gros, TEXTE)
    ecrire(44, 52, "variation de shortfall en valeur absolue, par trace",
           moyen, DISCRET)

    x0, y0 = 300, 112
    for v in (1, 2, 5, 10, 20):
        if v > haut:
            break
        xx = x0 + int(v / haut * larg_barre)
        d.line([xx, y0 - 8, xx, y0 + pas_ligne * len(lignes)], fill=(36, 36, 36))
        ecrire(xx - 6, y0 - 24, f"{v} %", petit, DISCRET)

    noms = etiquettes([x["trace"] for x in lignes])
    for i, x in enumerate(lignes):
        yy = y0 + pas_ligne * i
        ecrire(44, yy + 6, noms[i], petit, TEXTE)
        for k, (cle, couleur) in enumerate((("index", ROUGE), ("position", AMBRE))):
            l_barre = max(2, int(x[cle] / haut * larg_barre))
            yb = yy + 2 + k * 11
            d.rectangle([x0, yb, x0 + l_barre, yb + 9], fill=couleur)
            ecrire(x0 + l_barre + 6, yb - 2, f"{x[cle]:.2f}", petit, couleur)
        # ⚠ Le bruit PROPRE a la trace, en trait vertical : c'est le seuil qu'il fallait
        # depasser pour que l'effet soit lisible, et il n'est pas le meme partout.
        if x["bruit"]:
            xb = x0 + int(x["bruit"] / haut * larg_barre)
            d.line([xb, yy, xb, yy + 24], fill=GRIS, width=1)

    bas = y0 + pas_ligne * len(lignes) + 22
    d.rectangle([44, bas + 3, 68, bas + 12], fill=ROUGE)
    ecrire(76, bas, "tirage par index (avant/apres sur des cellules differentes)",
           petit, DISCRET)
    d.rectangle([44, bas + 20, 68, bas + 29], fill=AMBRE)
    ecrire(76, bas + 17, "tirage par POSITION de grille (meme echantillon)",
           petit, DISCRET)
    d.line([500, bas + 3, 500, bas + 27], fill=GRIS, width=1)
    ecrire(510, bas + 12, "bruit de graine propre a la trace", petit, DISCRET)

    for k, ligne in enumerate(prose(lignes)):
        ecrire(44, bas + 46 + k * 19, ligne, moyen, TEXTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return sortie, poses, [(0, 0, L, H)]


def verifier() -> int:
    """Auto-test HORS LIGNE : l'appariement, l'étiquette, la prose et la figure avec sondes."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    idx = {"paires": [{"trace": "A-w010-027", "variation_shortfall_pct": -4.6},
                      {"trace": "B-w028-037", "variation_shortfall_pct": 1.7},
                      {"trace": "C-w038-045", "variation_shortfall_pct": 2.7}]}
    # ⚠⚠ RANGES DIFFEREMMENT, expres : c'est le seul cas ou un appariement positionnel
    # produit une figure lisible et fausse.
    pos = {"paires": [{"trace": "C-w038-045", "variation_shortfall_pct": 0.3},
                      {"trace": "A-w010-027", "variation_shortfall_pct": -0.09},
                      {"trace": "B-w028-037", "variation_shortfall_pct": 0.2}]}
    br = {"lignes": [{"trace": "A-w010-027", "shortfall_etendue_pct": 4.0},
                      {"trace": "B-w028-037", "shortfall_etendue_pct": 3.2}]}
    r = rangees(idx, pos, br)
    v("l'appariement suit le nom et non l'ordre",
      [x["trace"] for x in r] == ["A-w010-027", "B-w028-037", "C-w038-045"],
      str([x["trace"] for x in r]))
    v("... et chaque barre porte la valeur de SA trace",
      abs(r[0]["position"] - 0.09) < 1e-9 and abs(r[2]["position"] - 0.3) < 1e-9,
      str([x["position"] for x in r]))
    # ⚠ La VALEUR ABSOLUE : un effet de -4,6 % est aussi grand qu'un de +4,6, et tracer le
    # signe ferait paraitre nul ce qui est fort.
    v("les effets sont tracés en valeur absolue", r[0]["index"] == 4.6, str(r[0]["index"]))
    # ⚠ Le bruit est la DEMI-etendue, et une trace sans bruit connu ne recoit pas de trait
    # plutot qu'un trait a zero -- un trait a zero se lirait « rien a depasser ».
    v("le bruit est la demi-étendue", abs(r[0]["bruit"] - 2.0) < 1e-9, str(r[0]["bruit"]))
    v("... et une trace sans bruit connu n'en reçoit pas", r[2]["bruit"] is None)
    # ⚠ Une trace mesuree d'un seul cote est SAUTEE : une barre manquante se lirait comme
    # un effet nul.
    v("une trace mesurée d'un seul côté est sautée",
      len(rangees(idx, {"paires": []}, br)) == 0)
    v("l'etiquette garde les indices de spire",
      etiquette("20260623141924-w010-027") == "w010-027")

    lignes = prose(r)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle dit le compte sous le bruit",
      any("sur 3" in l for l in lignes), str(lignes))

    with tempfile.TemporaryDirectory() as d:
        rac = Path(d)
        f_idx = rac / "idx.json"
        f_pos = rac / "pos.json"
        f_br = rac / "bruit.json"
        f_idx.write_text(json.dumps(idx), encoding="utf-8")
        f_pos.write_text(json.dumps(pos), encoding="utf-8")
        f_br.write_text(json.dumps(br), encoding="utf-8")

        lu_idx, lu_pos, lu_br = lire(f_idx, f_pos, f_br)
        v("les trois JSON sont lus",
          len(lu_idx["paires"]) == 3 and len(lu_pos["paires"]) == 3 and len(lu_br["lignes"]) == 2)

        out_img, poses, cadres = dessiner(lu_idx, lu_pos, lu_br, rac / "f.png")
        v("l'image est écrite", out_img.is_file())
        v("... et elle n'est pas vide", out_img.stat().st_size > 1000)

        im = Image.open(out_img).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0] == 900)
        v("... et sa hauteur correspond au nombre de traces", im.size[1] == 150 + 34 * 3 + 130)

        pixels = list(im.getdata())
        v("... et elle porte les couleurs des deux tirages",
          ROUGE in pixels and AMBRE in pixels)

        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]) == [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres) == [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses) == [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]] == [])

        # ⚠ Sonde : une mesure manquante est refusée
        try:
            lire(rac / "inexistant.json", f_pos, f_br)
            v("sonde : un fichier manquant est refusé", False)
        except FileNotFoundError:
            v("sonde : un fichier manquant est refusé", True)

        # ⚠ Sonde : un JSON sans paires est refusé
        f_invalide = rac / "invalide.json"
        f_invalide.write_text(json.dumps({"corpus": "PHercParis4"}), encoding="utf-8")
        try:
            lire(f_invalide, f_pos, f_br)
            v("sonde : un JSON sans paires est refusé", False)
        except ValueError:
            v("sonde : un JSON sans paires est refusé", True)

        # ⚠ Sonde : aucun appariement possible est refusé par dessiner
        f_disjoint = rac / "disjoint.json"
        f_disjoint.write_text(
            json.dumps({"paires": [{"trace": "Z-w999-999", "variation_shortfall_pct": 1.0}]}),
            encoding="utf-8"
        )
        lu_disjoint = json.loads(f_disjoint.read_text(encoding="utf-8"))
        try:
            dessiner(lu_idx, lu_disjoint, lu_br, rac / "vide.png")
            v("sonde : aucun appariement possible est refusé", False)
        except ValueError:
            v("sonde : aucun appariement possible est refusé", True)

        # ⚠ Sonde : la garde attrape un débordement simulé
        texte_trop_long = [(850, 10, "Texte qui depasse de la toile de neuf cents pixels", police(17))]
        v("sonde : textes_debordants détecte le dépassement",
          len(textes_debordants(texte_trop_long, 900)) > 0)

    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--index", type=Path,
                   default=MESURES / "reparation_et_proximite_scroll1.json")
    p.add_argument("--position", type=Path,
                   default=MESURES / "reparation_et_proximite_scroll1_apparie.json")
    p.add_argument("--bruit", type=Path, default=MESURES / "le_bruit_de_lechantillon.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "07_tirage_apparie.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    idx, pos, br = lire(a.index, a.position, a.bruit)
    out, _, _ = dessiner(idx, pos, br, a.sortie)
    try:
        cible = out.relative_to(RACINE)
    except ValueError:
        cible = out
    print(f"écrit : {cible}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
