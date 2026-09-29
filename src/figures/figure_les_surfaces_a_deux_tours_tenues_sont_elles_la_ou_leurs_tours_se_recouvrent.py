"""Sous chaque surface à deux tours des quatre chaînes, la part des sommets du tour de trop posés sur elle qui ont le tour attendu à un quart de pas : autour des graines 1 à 3, où le référent pose deux tours sur une feuille, et sur les graines 4 à 8, où le compte des feuilles de 345 tient ou refuse la surface.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, une rangée par groupe de surfaces, chacune à sa part, et le seuil de la moitié :
à droite du seuil, la surface est posée où ses deux tours publiés se recouvrent ; à gauche, elle est à cheval sur deux feuilles. La rangée
du haut est le contrôle. À droite, les surfaces des graines 4 à 8, une par ligne, avec leurs tours et ce que dit la mesure.

  uv run python src/figures/figure_les_surfaces_a_deux_tours_tenues_sont_elles_la_ou_leurs_tours_se_recouvrent.py \\
      --sortie docs/images/346_les_surfaces_a_deux_tours_tenues_sont_elles_la_ou_leurs_tours_se_recouvrent.png

⚠ Tout vient de la mesure de `346`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_surfaces_a_deux_tours_tenues_sont_elles_la_ou_leurs_tours_se_recouvrent.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
GRIS_POINT = (150, 153, 158)
L_, H_ = 1360, 600
LA_BANDE = 510
LE_SEUIL = 0.5
LES_RANGEES = (("le contrôle : graines 1 à 3", lambda s: s["le_rang"] < 4),
               ("graines 4 à 8, tenues par 345", lambda s: s["le_rang"] >= 4 and s["tient_par_345"]),
               ("graines 4 à 8, refusées par 345", lambda s: s["le_rang"] >= 4 and not s["tient_par_345"]))
LES_NOMS = {"sans relance": "sans relance", "relancée depuis un point": "depuis un point", "relancée depuis la spire": "depuis la spire",
            "bornée": "bornée"}


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return (f"{v['k']} des {v['n']} surfaces à deux tours que le compte tient sur les graines 4 à 8 sont posées où leurs tours se "
            f"recouvrent").upper()


def f2(x) -> str:
    return "non lue" if x is None else f"{x:.2f}".replace(".", ",")


LA_POSEE = "posée où ses tours se recouvrent"


def les_comptes(d: dict) -> dict:
    """Recomptés sur les surfaces, sans passer par le verdict : les lues et les posées du contrôle et des tenues des graines 4 à 8,
    et les tenues que la règle ne lit pas."""
    ctl = [s["la_surface"]["la_lecture"] for s in d["les_surfaces"] if s["le_rang"] < 4]
    ten = [s for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["tient_par_345"]]
    lues = [s["la_surface"]["la_lecture"] for s in ten if s["la_surface"]["la_lecture"] != "non lue"]
    return {"controle_lues": sum(x != "non lue" for x in ctl), "controle_posees": sum(x == LA_POSEE for x in ctl),
            "tenues": len(ten), "tenues_lues": len(lues), "tenues_posees": sum(x == LA_POSEE for x in lues),
            "tenues_non_lues": [s for s in ten if s["la_surface"]["la_lecture"] == "non lue"]}


def la_bande(d: dict) -> tuple[str, str, str]:
    """Les trois lignes de la bande : le verdict déclaré, sa suite ou ce qui est rapporté à côté, et ce qui n'est pas établi."""
    v, c = d["le_verdict"], les_comptes(d)
    if v.get("decidable"):
        tete, _, suite = v["lissue"].rpartition(" ; ")
        return (f"LE VERDICT DÉCLARÉ : {tete} ;", suite,
                "⚠ ce qui n'est PAS établi : lequel des deux tours publiés est à la mauvaise place là où ils se recouvrent.")
    aside = (f"rapporté à côté, qui ne décide rien : {c['tenues_posees']} des {c['tenues_lues']} tenues lues sont posées où leurs tours "
             f"se recouvrent, contre {c['controle_posees']} des {c['controle_lues']} lues autour des graines 1 à 3")
    if c["tenues_non_lues"]:
        s = c["tenues_non_lues"][0]
        pas_etabli = (f"⚠ ce qui n'est PAS établi : où est posée la surface {LES_NOMS[s['la_chaine']]}, graine {s['le_rang']}, "
                      f"saut {s['le_saut']}, que la règle ne lit pas.")
    else:
        pas_etabli = "⚠ ce qui n'est PAS établi : où sont posées les surfaces tenues par 345."
    return f"LE VERDICT DÉCLARÉ : {v['lissue']}", aside, pas_etabli


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"points": [], "lignes": [], "ecretes": 0, "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "la part des sommets du tour de trop posés sur la surface qui ont le tour attendu à un quart de pas", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 690, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "chaque surface à deux tours, à sa part", moyen, ENCRE)
    gx0, gx1 = x0 + 240, x1 - 30
    X = lambda p: gx0 + p * (gx1 - gx0)  # noqa: E731
    xn = x0 + 205
    ys = [y0 + 110, y0 + 220, y0 + 310]
    for (nom, _), yr in zip(LES_RANGEES, ys):
        ecrire(x0 + 12, yr - 7, nom, 0, ENCRE)
        art.line([gx0, yr, gx1, yr], fill=TRAIT)
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        art.line([X(p), y0 + 60, X(p), y1 - 60], fill=TRAIT)
        ecrire(int(X(p)) - 10, y1 - 54, f"{int(p * 100)} %", 0, GRIS)
    art.line([X(LE_SEUIL), y0 + 60, X(LE_SEUIL), y1 - 60], fill=ALERTE, width=2)
    gauche = "à cheval sur deux feuilles ←"
    ecrire(int(X(LE_SEUIL) - 6 - art.textlength(gauche, font=petit)), y0 + 40, gauche, 0, ALERTE)
    ecrire(int(X(LE_SEUIL)) + 6, y0 + 40, "→ posée où ses tours se recouvrent", 0, ALERTE)
    ecrire(xn - 20, y1 - 54, "non lue", 0, GRIS)
    ecrire(gx0 + 30, y1 - 30, "la part du tour de trop qui a le tour attendu à un quart de pas", 0, ENCRE)
    for (nom, garde), yr in zip(LES_RANGEES, ys):
        k = 0
        for s in d["les_surfaces"]:
            if not garde(s):
                continue
            p = s["la_surface"]["la_part"]
            if p is not None and not 0.0 <= p <= 1.0:
                traces["ecretes"] += 1
            cx = xn if p is None else X(min(max(p, 0.0), 1.0))
            cy = yr + ((k * 37) % 31 - 15)
            k += 1
            tenue = s["le_rang"] >= 4 and s["tient_par_345"]
            rr = 6 if tenue else 4
            art.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=ALERTE if tenue else GRIS_POINT, outline=ENCRE if tenue else None)
            traces["points"].append((nom, s["la_chaine"], s["le_rang"], s["le_saut"], p))
            traces["rectangles"].append((0, cx - rr, cx + rr, cy - rr, cy + rr))

    x0, y0, x1, y1 = 720, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les surfaces à deux tours des graines 4 à 8", moyen, ENCRE)
    cols = (x0 + 12, x0 + 120, x0 + 200, x0 + 270, x0 + 335, x0 + 400, x0 + 490)
    for x, t in zip(cols, ("chaîne", "graine", "tours", "attendu", "part", "l'autre sens", "345")):
        ecrire(x, y0 + 44, t, 0, GRIS)
    y = y0 + 66
    for s in d["les_surfaces"]:
        if s["le_rang"] < 4:
            continue
        a = s["la_surface"]
        tours = ", ".join(str(t) for t in sorted([a["le_tour_attendu"], *a["les_tours_de_trop"]], reverse=True))
        cellules = (LES_NOMS[s["la_chaine"]], f"{s['le_rang']}, saut {s['le_saut']}", tours, str(a["le_tour_attendu"]), f2(a["la_part"]),
                    f2(a["la_part_dans_lautre_sens"]), "tenue" if s["tient_par_345"] else "refusée")
        for x, t in zip(cols, cellules):
            ecrire(x, y, t, 0, ALERTE if s["tient_par_345"] else ENCRE)
        traces["lignes"].append(cellules)
        y += 22
    ecrire(x0 + 12, y + 16, "tours : ceux que la surface retrouve ; part : celle du tour de trop", 0, GRIS)
    ecrire(x0 + 12, y + 32, "sur le tour attendu ; l'autre sens : celle du tour attendu sur le tour de trop", 0, GRIS)

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
    tmp = sortie.parent / ".sonde_346.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"].update({"decidable": True, "k": 1, "n": 3})
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("1 DES 3 SURFACES"), le_titre(autre))
    indec = json.loads(json.dumps(d))
    indec["le_verdict"] = {"decidable": False, "lissue": "indécidable : une lecture a échoué (x)"}
    v("★★★ un titre indécidable LIT son issue", le_titre(indec) == "INDÉCIDABLE : UNE LECTURE A ÉCHOUÉ (X)", le_titre(indec))
    c = les_comptes(d)
    ctl = [s for s in d["les_surfaces"] if s["le_rang"] < 4]
    v("★★★★ le contrôle est recompté", (c["controle_lues"], c["controle_posees"])
      == (sum(s["la_surface"]["la_part"] is not None for s in ctl), sum((s["la_surface"]["la_part"] or 0) >= LE_SEUIL for s in ctl)),
      str(c))
    txt_bande = " ".join(la_bande(d))
    if not d["le_verdict"].get("decidable"):
        v("★★★★ la bande rapporte à côté les comptes recomptés",
          f"{c['tenues_posees']} des {c['tenues_lues']} tenues lues" in txt_bande
          and f"contre {c['controle_posees']} des {c['controle_lues']} lues" in txt_bande, txt_bande[:200])
        v("★★★★ la bande nomme chaque tenue que la règle ne lit pas",
          all(f"graine {s['le_rang']}, saut {s['le_saut']}" in txt_bande for s in c["tenues_non_lues"][:1])
          and (not c["tenues_non_lues"]) == ("que la règle ne lit pas" not in txt_bande))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ un point par surface à deux tours, et aucun autre",
      sorted(p[1:4] for p in traces["points"]) == sorted((s["la_chaine"], s["le_rang"], s["le_saut"]) for s in d["les_surfaces"]))
    rang = {nom: [p for p in traces["points"] if p[0] == nom] for nom, _ in LES_RANGEES}
    v("★★★★ la rangée du contrôle porte les surfaces des graines 1 à 3, et elles seules",
      len(rang[LES_RANGEES[0][0]]) == sum(1 for s in d["les_surfaces"] if s["le_rang"] < 4)
      and all(p[2] < 4 for p in rang[LES_RANGEES[0][0]]))
    tenues = sum(1 for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["tient_par_345"])
    v("★★★★ la rangée des tenues porte les surfaces tenues des graines 4 à 8, et elles seules",
      len(rang[LES_RANGEES[1][0]]) == tenues == c["tenues"] and all(p[2] >= 4 for p in rang[LES_RANGEES[1][0]])
      and (not d["le_verdict"].get("decidable") or tenues == d["le_verdict"]["n"]))
    a_droite = sum(1 for p in rang[LES_RANGEES[1][0]] if p[4] is not None and p[4] >= LE_SEUIL)
    v("★★★★ les tenues à droite du seuil sont celles que la mesure dit posées où leurs tours se recouvrent",
      a_droite == c["tenues_posees"] and (not d["le_verdict"].get("decidable") or a_droite == d["le_verdict"]["k"]), str(a_droite))
    v("★★★ une ligne du tableau par surface des graines 4 à 8, à sa part",
      [(x[1], x[4], x[5]) for x in traces["lignes"]]
      == [(f"{s['le_rang']}, saut {s['le_saut']}", f2(s["la_surface"]["la_part"]), f2(s["la_surface"]["la_part_dans_lautre_sens"]))
          for s in d["les_surfaces"] if s["le_rang"] >= 4])
    v("★★★ rien n'est écrêté", traces["ecretes"] == 0, str(traces["ecretes"]))
    mesureur = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    boites = [mesureur.textbbox((x, y), t, font=f) for x, y, t, f in poses]
    sous_texte = [r for r in traces["rectangles"]
                  if any(b[0] < r[2] and r[1] < b[2] and b[1] < r[4] and r[3] < b[3] for b in boites)]
    v("★★★★ aucun point ne passe sous un texte", not sous_texte, str(sous_texte[:3]))
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
                   / "346_les_surfaces_a_deux_tours_tenues_sont_elles_la_ou_leurs_tours_se_recouvrent.png")
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
