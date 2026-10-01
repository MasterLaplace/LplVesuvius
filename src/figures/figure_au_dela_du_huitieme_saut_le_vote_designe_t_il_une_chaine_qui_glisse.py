"""Sur les graines 4 et 6, côté moins, de PHerc0358, à seize sauts : les paires de la chaîne que le vote désigne avec chacune des deux autres, par saut de la chaîne désignée, et si elles s'accordent ou se contredisent.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux panneaux, un par côté ; dans chacun, deux rangées, une par chaîne voisine ; un point
par paire, au saut de la chaîne désignée : bleu si la paire tient les comptes, orange si elle les contredit ; un trait au début du glissement
et un trait pointillé au huitième saut.

  uv run python src/figures/figure_au_dela_du_huitieme_saut_le_vote_designe_t_il_une_chaine_qui_glisse.py \\
      --sortie docs/images/390_au_dela_du_huitieme_saut_le_vote_designe_t_il_une_chaine_qui_glisse.png

⚠ Tout vient des mesures de `389` et `390`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "au_dela_du_huitieme_saut_le_vote_designe_t_il_une_chaine_qui_glisse.json"
LES_CHAINES_389 = RACINE / "docs" / "mesures" / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1300, 580
LA_BANDE = 450
RAYON = 5
LES_COTES = ((4, "moins"), (6, "moins"))


def lire(chemin: Path = LA_MESURE, chaines: Path = LES_CHAINES_389) -> tuple[dict, dict]:
    return json.loads(chemin.read_text()), json.loads(chaines.read_text())


def les_points(c389: dict, x: str) -> list[tuple[str, int, bool]]:
    """Pour chaque paire de la chaîne `x` avec une autre : l'autre chaîne, le saut de `x`, et si la paire contredit les comptes."""
    out = []
    for k, ps in c389["les_paires"].items():
        a, b = k.split("|")
        if x not in (a, b):
            continue
        y = b if a == x else a
        for h, kk, m in ps:
            hx, hy = (h, kk) if a == x else (kk, h)
            out.append((y, hx, bool(m != (c389["les_comptes"][x][hx - 1] == c389["les_comptes"][y][hy - 1]))))
    return sorted(out)


def le_cadre(i: int) -> tuple[int, int, int, int]:
    return 50 + i * 610, 80, 50 + i * 610 + 590, 420


def en_x(cadre: tuple, h: int) -> int:
    x0, _, x1, _ = cadre
    return round(x0 + 90 + (h - 1) / 15 * (x1 - x0 - 120))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def la_bande(d: dict) -> tuple[str, ...]:
    import textwrap

    un = textwrap.wrap(f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", 175)
    vus = [c for c in d["les_cotes"] if (c["le_rang"], c["le_cote"]) in LES_COTES and c["le_vote"]]
    deux = ("rapporté à côté, qui ne décide rien : le glissement commence " + ", ".join(
        f"au saut {c['le_debut']['le_saut']} sur la graine {c['le_rang']}" for c in vus) + ", avant le huitième saut"
        if vus and all(not c["au_dela_du_huitieme"] for c in vus) else "rapporté à côté : un glissement commence au-delà du huitième saut")
    trois = "⚠ ce qui n'est PAS établi : si la chaîne désignée a glissé plutôt que les deux autres ensemble."
    return (*un, deux, trois)


def dessiner(d: dict, d389: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [le_cadre(i) for i in range(len(LES_COTES))]
    traces = {"points": [], "debuts": [], "huit": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, f"à seize sauts : {le_titre(d)}", gros, ENCRE)
    ecrire(50, 46, "les paires de la chaîne désignée, par son saut : bleu si elles tiennent les comptes, orange si elles les contredisent",
           petit, GRIS)
    c389 = {(c["le_rang"], c["le_cote"]): c for c in d389["les_cotes"]}
    c390 = {(c["le_rang"], c["le_cote"]): c for c in d["les_cotes"]}
    for i, cle in enumerate(LES_COTES):
        cadre = cadres[i]
        x0, y0, x1, y1 = cadre
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        c = c390[cle]
        x = c["le_vote"]
        ecrire(x0 + 10, y0 + 8, f"graine {cle[0]}, côté {cle[1]} : la {x} désignée", moyen, ENCRE)
        autres = sorted({y for y, _, _ in les_points(c389[cle], x)})
        lignes = {y: y0 + 90 + j * 110 for j, y in enumerate(autres)}
        for y, yy in lignes.items():
            ecrire(x0 + 10, yy - 8, f"la {y}", petit, ENCRE)
            art.line([x0 + 85, yy, x1 - 20, yy], fill=TRAIT)
        xh = en_x(cadre, 8)
        art.line([xh, y0 + 40, xh, y1 - 40], fill=GRIS, width=1)
        traces["huit"].append(xh)
        ecrire(xh + 4, y1 - 36, "8e saut", petit, GRIS)
        xd = en_x(cadre, c["le_debut"]["le_saut"])
        art.line([xd, y0 + 40, xd, y1 - 40], fill=ALERTE, width=2)
        traces["debuts"].append((cle, c["le_debut"]["le_saut"], xd))
        ecrire(xd + 4, y0 + 40, f"début : saut {c['le_debut']['le_saut']}", petit, ALERTE)
        decalage = {}
        for y, hx, contre in les_points(c389[cle], x):
            n = decalage.get((y, hx), 0)
            decalage[(y, hx)] = n + 1
            px, py = en_x(cadre, hx), lignes[y] - 24 + 12 * (n % 5)
            couleur = ORANGE if contre else BLEU
            art.ellipse([px - RAYON, py - RAYON, px + RAYON, py + RAYON], fill=couleur)
            traces["points"].append((cle, y, hx, contre, px, py, couleur))
        for h in (1, 4, 8, 12, 16):
            ecrire(en_x(cadre, h) - 4, y1 - 20, str(h), petit, GRIS)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    *lignes_, trois = la_bande(d)
    for j, t in enumerate(lignes_):
        ecrire(50, LA_BANDE + 10 + 18 * j, t, petit, ENCRE)
    ecrire(50, LA_BANDE + 18 * len(lignes_) + 20, trois, moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, traces


def verifier(sortie: Path, mesure: Path = LA_MESURE) -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    d, d389 = lire(mesure)
    tmp = sortie.parent / ".sonde_390.png"
    try:
        _, poses, cadres, traces = dessiner(d, d389, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; en partie"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "EN PARTIE", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    c389 = {(c["le_rang"], c["le_cote"]): c for c in d389["les_cotes"]}
    c390 = {(c["le_rang"], c["le_cote"]): c for c in d["les_cotes"]}
    attendu = []
    for cle in ((4, "moins"), (6, "moins")):
        x = c390[cle]["le_vote"]
        for k, ps in c389[cle]["les_paires"].items():
            a, b = k.split("|")
            if x in (a, b):
                for h, kk, m in ps:
                    hx, hy = (h, kk) if a == x else (kk, h)
                    y = b if a == x else a
                    attendu.append((cle, y, hx, m != (c389[cle]["les_comptes"][x][hx - 1] == c389[cle]["les_comptes"][y][hy - 1])))
    v("★★★★ un point par paire de la chaîne désignée, recompté sur les paires de 389",
      sorted(t[:4] for t in traces["points"]) == sorted(attendu), f"{len(traces['points'])} contre {len(attendu)}")
    v("★★★★ orange si la paire contredit, bleu sinon", all(f == (ORANGE if contre else BLEU) for *_, contre, _, _, f in traces["points"]))
    v("★★★★ chaque point est au saut de la chaîne désignée", all(px == en_x(cadres[[(4, "moins"), (6, "moins")].index(cle)], hx)
                                                               for cle, _, hx, _, px, _, _ in traces["points"]))
    v("★★★★ le début est celui de la mesure", [(cle, s) for cle, s, _ in traces["debuts"]]
      == [(cle, c390[cle]["le_debut"]["le_saut"]) for cle in ((4, "moins"), (6, "moins"))])
    v("★★★★ le huitième saut est marqué dans chaque panneau", traces["huit"] == [en_x(c, 8) for c in cadres])
    v("★★★★ chaque point est dans son panneau", all(cadres[[(4, "moins"), (6, "moins")].index(cle)][0] < px
                                                   < cadres[[(4, "moins"), (6, "moins")].index(cle)][2] for cle, _, _, _, px, _, _ in traces["points"]))
    v("★★★★ la bande porte le verdict entier",
      " ".join(la_bande(d)[:-2]) == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
    octets = tmp.read_bytes()
    dessiner(d, d389, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "390_au_dela_du_huitieme_saut_le_vote_designe_t_il_une_chaine_qui_glisse.png")
    p.add_argument("--mesure", type=Path, default=LA_MESURE)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie, a.mesure)
    d, d389 = lire(a.mesure)
    chemin, *_ = dessiner(d, d389, a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
