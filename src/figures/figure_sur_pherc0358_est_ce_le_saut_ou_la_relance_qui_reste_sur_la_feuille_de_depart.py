"""Sur PHerc0358, saut par saut, la spire que trouve le saut et la surface relancée depuis elle : leurs points à zéro, et si le critère de 352 tiendrait chacune ; et, sous les sauts dont la relance garde 50 points sur la feuille de départ, si la spire est partie ou restée.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, deux rangées par côté, la spire au-dessus, la surface relancée en dessous, une
case par saut : foncée si le critère la tiendrait, claire sinon, avec ses points à zéro. Un liseré ambre marque les sauts jugés dont la
spire est partie, un liseré gris ceux dont elle est restée. À droite, les comptes.

  uv run python src/figures/figure_sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart.py \\
      --sortie docs/images/355_sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart.png

⚠ Tout vient de la mesure de `355`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
CLAIR = (226, 224, 219)
L_, H_ = 1360, 600
LA_BANDE = 510
CG, CL, CH = 250, 58, 22
LES_SAUTS = 8


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_sauts(d: dict) -> list[dict]:
    return [s for c in d["les_cotes"] for s in c["les_sauts"] if s["a_une_surface"]]


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return f"sous {v['n']} sauts retombés, la spire est partie sous {v['p']} et restée sous {v['r']}".upper()


def la_bande(d: dict) -> tuple[str, str, str]:
    s = les_sauts(d)
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = (f"rapporté à côté, lu après coup, qui ne décide rien : le critère de 352 tiendrait {sum(x['la_spire_tenue'] for x in s)} des "
            f"{len(s)} spires, et {sum(x['la_relance_tenue'] for x in s)} des surfaces relancées")
    trois = "⚠ ce qui n'est PAS établi : si une spire partie est sur la bonne feuille, ni ce qu'une autre relance ferait."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cases": [], "liseres": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "une case par saut : la spire au-dessus, la surface relancée en dessous ; z : les points à zéro feuille", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 840, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la spire et la surface relancée, saut par saut", moyen, ENCRE)
    for h in range(LES_SAUTS):
        ecrire(CG + h * (CL + 6) + 12, y0 + 36, f"saut {h + 1}", 0, GRIS)
    y = y0 + 56
    for c in d["les_cotes"]:
        ecrire(x0 + 12, y + 3, f"graine {c['le_rang']}, {c['le_cote']} : spire", 0, ENCRE)
        ecrire(x0 + 12, y + CH + 5, "surface relancée", 0, GRIS)
        for h, s in enumerate(c["les_sauts"]):
            cx = CG + h * (CL + 6)
            for rang, (cle, tenu) in enumerate((("la_spire", s["la_spire_tenue"]), ("la_relance", s["la_relance_tenue"]))):
                cy = y + rang * (CH + 2)
                art.rectangle([cx, cy, cx + CL, cy + CH], fill=BLEU if tenu else CLAIR)
                traces["rectangles"].append((0, cx, cx + CL, cy, cy + CH))
                ecrire(cx + 5, cy + 4, f"z = {s[cle]['les_comptes'].get('0', 0)}", 0, FOND if tenu else ENCRE)
                traces["cases"].append((c["le_rang"], c["le_cote"], h + 1, cle, tenu))
            if s["la_lecture"] in ("partie", "restée"):
                couleur = ALERTE if s["la_lecture"] == "partie" else GRIS
                art.rectangle([cx - 2, y - 2, cx + CL + 2, y + 2 * CH + 4], outline=couleur, width=2)
                traces["liseres"].append((c["le_rang"], c["le_cote"], h + 1, s["la_lecture"], couleur))
        y += 2 * CH + 20
    art.rectangle([x0 + 12, y1 - 24, x0 + 24, y1 - 12], fill=BLEU)
    ecrire(x0 + 30, y1 - 26, "le critère de 352 la tiendrait", 0, ENCRE)
    art.rectangle([x0 + 230, y1 - 24, x0 + 242, y1 - 12], outline=ALERTE, width=2)
    ecrire(x0 + 248, y1 - 26, "spire partie", 0, ENCRE)
    art.rectangle([x0 + 350, y1 - 24, x0 + 362, y1 - 12], outline=GRIS, width=2)
    ecrire(x0 + 368, y1 - 26, "spire restée", 0, ENCRE)
    traces["rectangles"] += [(0, x0 + 12, x0 + 24, y1 - 24, y1 - 12), (0, x0 + 230, x0 + 242, y1 - 24, y1 - 12),
                             (0, x0 + 350, x0 + 362, y1 - 24, y1 - 12)]

    x0, y0, x1, y1 = 870, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les comptes", moyen, ENCRE)
    s = les_sauts(d)
    lectures = [x["la_lecture"] for x in s]
    lignes = (("sauts qui ont une surface", len(s)),
              ("relance à 50 points à zéro ou plus", sum(1 for x in lectures if x is not None)),
              ("  dont la spire est partie", lectures.count("partie")),
              ("  dont la spire est restée", lectures.count("restée")),
              ("  dont la spire n'est pas lue", lectures.count("non lue")),
              ("spires que 352 tiendrait", sum(x["la_spire_tenue"] for x in s)),
              ("surfaces relancées que 352 tiendrait", sum(x["la_relance_tenue"] for x in s)))
    y = y0 + 44
    for nom, n in lignes:
        ecrire(x0 + 12, y, nom, 0, ENCRE)
        ecrire(x0 + 360, y, str(n), 0, ENCRE)
        traces.setdefault("lignes", []).append((nom, n))
        y += 22

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 26, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, trois, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_355.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"].update({"n": 9, "p": 4, "r": 5})
    v("★★★ le titre LIT la mesure", le_titre(autre) == "SOUS 9 SAUTS RETOMBÉS, LA SPIRE EST PARTIE SOUS 4 ET RESTÉE SOUS 5", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(c["le_rang"], c["le_cote"], h, k, s[f"{k}_tenue"]) for c in d["les_cotes"] for h, s in enumerate(c["les_sauts"], 1)
               for k in ("la_spire", "la_relance")]
    v("★★★★ deux cases par saut, la spire et la surface relancée, à ce que le critère en dirait", traces["cases"] == attendu)
    liseres = [(c["le_rang"], c["le_cote"], h, s["la_lecture"]) for c in d["les_cotes"] for h, s in enumerate(c["les_sauts"], 1)
               if s["la_lecture"] in ("partie", "restée")]
    v("★★★★ un liseré par saut jugé lu, de la couleur de sa lecture", [x[:4] for x in traces["liseres"]] == liseres
      and all(x[4] == (ALERTE if x[3] == "partie" else GRIS) for x in traces["liseres"]))
    v("★★★★ les liserés sont autant que les sauts jugés du verdict", not d["le_verdict"].get("decidable")
      or (sum(x[3] == "partie" for x in traces["liseres"]), sum(x[3] == "restée" for x in traces["liseres"]))
      == (d["le_verdict"]["p"], d["le_verdict"]["r"]))
    v("★★★★ aucun côté n'a plus de sauts que la grille n'a de colonnes", all(len(c["les_sauts"]) <= LES_SAUTS for c in d["les_cotes"]))
    s = [x for c in d["les_cotes"] for x in c["les_sauts"] if x["a_une_surface"]]
    v("★★★★ la bande rapporte à côté les spires et les relances que 352 tiendrait, recomptées",
      f"tiendrait {sum(x['la_spire_tenue'] for x in s)} des {len(s)} spires, et {sum(x['la_relance_tenue'] for x in s)} des surfaces"
      in " ".join(la_bande(d)))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
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
                   / "355_sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart.png")
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
