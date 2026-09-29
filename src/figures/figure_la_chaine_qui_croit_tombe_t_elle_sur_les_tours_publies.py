"""Surface par surface, sur quel tour publié la chaîne qui croît de PHercParis4 tombe-t-elle : 5753_0, 5753_-1, 5753_-2, 5753_-3, de chaque côté de chaque graine.

⚠⚠ **Ce que cette figure doit rendre évident.** Chaque ligne est une graine, chaque colonne une surface de la chaîne, la nappe puis ses
trois spires. La case porte le tour publié que la surface retrouve (« — » si aucun) ; elle est verte si la surface retrouve le tour
suivant de celui que la surface d'avant retrouvait seul, orange si ce passage échoue. Si, côté moins, les cases descendent 0, −1, −2 en
vert dès que la chaîne a touché un tour publié, la chaîne suit les tours que l'équipe a tracés.

  uv run python src/figures/figure_la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies.py \\
      --sortie docs/images/329_la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies.png

⚠ Tout vient de la mesure.
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE_BON = (214, 232, 222)
PALE_ALERTE = (240, 218, 204)
L_, H_ = 1360, 560
LA_BANDE = 470
LES_COLONNES = ("la nappe", "saut 1", "saut 2", "saut 3")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    p = d["les_passages"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    cs = les_cases(d)
    n_ = lambda c, e: sum(1 for x in cs if x[1] == c and x[4] == e)  # noqa: E731
    return (f"côté moins, la chaîne qui croît passe d'un tour publié au suivant {n_('moins', 'réussi')} fois sur "
            f"{n_('moins', 'réussi') + n_('moins', 'échoué')} ; côté plus, {n_('plus', 'réussi')} fois sur "
            f"{n_('plus', 'réussi') + n_('plus', 'échoué')}").upper()


def _retrouves(lect: dict) -> list[int]:
    return sorted((int(t) for t, x in lect.items() if x["la_lecture"] == "retrouve"), reverse=True)


def les_cases(d: dict) -> list:
    """Pour chaque graine, chaque côté et chaque surface : les tours retrouvés, et l'état du passage depuis la surface d'avant."""
    out = []
    for g in d["les_graines"]:
        for c in ("moins", "plus"):
            surfaces = [g["la_nappe"]] + [sp["les_tours"] for sp in g["les_cotes"][c]["les_spires"]]
            avant = None
            for j, lect in enumerate(surfaces):
                r = _retrouves(lect)
                etat = ""
                if avant is not None and len(avant) == 1 and str(avant[0] - 1) in lect:
                    x = lect[str(avant[0] - 1)]["la_lecture"]
                    etat = "réussi" if x == "retrouve" else ("" if x == "non lue" else "échoué")
                out.append((g["le_rang"], c, j, tuple(r), etat))
                avant = r
    return out


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cases": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "le tour publié que chaque surface retrouve (« — » : aucun) ; vert : la surface retrouve le tour suivant de celui que "
                   "la surface d'avant retrouvait seule ; orange : ce passage échoue", petit, GRIS)
    cases = les_cases(d)
    par = {(g, c, j): (r, e) for g, c, j, r, e in cases}
    for k, c in enumerate(("moins", "plus")):
        x0, y0 = 50 + k * 640, 76
        x1, y1 = x0 + 620, 452
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 12, y0 + 8, f"côté {c}", moyen, ENCRE)
        cx0, cw, rh = x0 + 90, 125, 38
        for j, nom in enumerate(LES_COLONNES):
            ecrire(int(cx0 + j * cw + 8), y0 + 36, nom, 0, GRIS)
        for n, g in enumerate(d["les_graines"]):
            yy = y0 + 58 + n * rh
            ecrire(x0 + 16, yy + 10, f"g{g['le_rang']}", 0, ENCRE)
            for j in range(len(LES_COLONNES)):
                if (g["le_rang"], c, j) not in par:
                    continue
                r, e = par[(g["le_rang"], c, j)]
                fond = PALE_BON if e == "réussi" else (PALE_ALERTE if e == "échoué" else FOND)
                art.rectangle([cx0 + j * cw, yy, cx0 + (j + 1) * cw - 8, yy + rh - 6], fill=fond, outline=TRAIT)
                texte = "/".join(f"{t}".replace("-", "−") for t in r) if r else "—"
                ecrire(int(cx0 + j * cw + 10), yy + 9, texte, 0, BON if e == "réussi" else (ALERTE if e == "échoué" else ENCRE))
                traces["cases"].append((g["le_rang"], c, j, r, e))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : ce que valent ces tours publiés comme vérité ; ni la chaîne au-delà du "
                              "troisième saut.", moyen, ALERTE)

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

    d = lire(mesure)
    tmp = sortie.parent / ".sonde_329.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    for g in autre["les_graines"]:
        for x in g["la_nappe"].values():
            x["la_lecture"] = "ne retrouve pas"
        for c in g["les_cotes"].values():
            for sp in c["les_spires"]:
                for x in sp["les_tours"].values():
                    x["la_lecture"] = "ne retrouve pas"
    v("★★★ le titre LIT la mesure", "0 FOIS SUR 0 ; CÔTÉ PLUS, 0 FOIS SUR 0" in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ une case par surface lue", sorted(traces["cases"]) == sorted(x for x in les_cases(d) if x[2] < len(LES_COLONNES)))
    v("★★★★ les passages de la figure sont ceux de la mesure", (sum(1 for x in traces["cases"] if x[4] == "réussi"),
      sum(1 for x in traces["cases"] if x[4] == "échoué")) == (d["les_passages"]["reussis"], d["les_passages"]["echoues"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    octets = tmp.read_bytes()
    dessiner(d, tmp)
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
                   / "329_la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies.png")
    p.add_argument("--mesure", type=Path, default=LA_MESURE)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie, a.mesure)
    chemin, *_ = dessiner(lire(a.mesure), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
