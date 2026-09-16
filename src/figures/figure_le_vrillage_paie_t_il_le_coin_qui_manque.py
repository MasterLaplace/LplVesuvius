"""Le vrillage paie-t-il le coin qui manque ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle et la cible. En haut
à droite, le balayage : la part axiale monte avec le vrillage, l'azimutale NE DESCEND PAS. En bas à
gauche, la pose — la calibration touche sa cible au millième et la matière penche toujours du
mauvais côté. En bas à droite, le prix : le pire écart aux trois grandeurs du rouleau AUGMENTE.

  uv run python src/figures/figure_le_vrillage_paie_t_il_le_coin_qui_manque.py \\
      --json docs/mesures/le_vrillage_paie_t_il_le_coin_qui_manque.json \\
      --sortie docs/images/170_le_vrillage_paie_t_il_le_coin_qui_manque.png
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
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    return f"{float(x):.{n}f}".rstrip("0").rstrip(".").replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `le_vrillage_paie_t_il_le_coin_qui_manque.py`.

    ⚠⚠ Refuse une mesure sans la POSE et sans les DEUX distances : le verdict de cette tranche est
    une comparaison de prix, et une figure qui n'en montrerait qu'un côté ne comparerait rien.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    for cle in ("sans_vrillage", "avec_vrillage", "distance_sans_vrillage",
                "distance_avec_vrillage", "le_rouleau"):
        if not j.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if j.get("il_paie_ce_quil_donne") is None:
        raise ValueError(f"{chemin} : le verdict joint est absent")
    if not (d.get("enquete") or {}).get("balayage"):
        raise ValueError(f"{chemin} : le balayage est absent")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    j, e = d["juger"], d["enquete"]
    ro, sans, avec = j["le_rouleau"], j["sans_vrillage"], j["avec_vrillage"]
    ds, da = j["distance_sans_vrillage"], j["distance_avec_vrillage"]
    c = j["le_controle_de_la_spirale_nue"]
    bal = [m for m in e["balayage"] if m.get("decidable")]

    ecrire(28, 20, "Le vrillage paie-t-il le coin qui manque ? — il AJOUTE de l'axial sans "
                   "RETIRER d'azimutal", gros, ENCRE)
    ecrire(28, 46, "`169` mesure que les deux causes du dépôt tirent en sens opposés ; le vrillage "
                   "donne le coin axial ET suivi qui manquait, et voici ce qu'il coûte", petit,
           GRIS)

    # ---- panneau 1 : le controle et la cible
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle, et ce qu'il faut atteindre", moyen, ENCRE)
    m1 = "★" if c["il_ne_penche_pas"] else "✗"
    ecrire(x0 + 14, y0 + 22, f"{m1}  la spirale nue ne penche pas du tout", moyen,
           BON if c["il_ne_penche_pas"] else ALERTE)
    ecrire(x0 + 14, y0 + 52,
           f"part axiale {_fr(c['axial_median'])}, glissement "
           f"{_fr(c['glissement_axial_median_um'], 1)} µm, sur {c['decidables']} marches",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 86, "la cible — le VRAI rouleau, avec cap", moyen, ENCRE)
    for i, (lib, val) in enumerate((("part axiale", ro["axial"]),
                                    ("part azimutale", ro["azimutal"]),
                                    ("rapport", ro["rapport"]),
                                    ("penchant", ro["penchant_deg"]),
                                    ("cohérence", ro["coherence"]))):
        ecrire(x0 + 14, y0 + 114 + i * 17, f"{lib:<16}", 0, GRIS)
        ecrire(x0 + 140, y0 + 114 + i * 17,
               _fr(val, 4) + ("°" if lib == "penchant" else ""), 0, ENCRE)
    ecrire(x0 + 300, y0 + 114,
           "⚠⚠ LA CALIBRATION SE FAIT SUR LA PART", petit, ALERTE)
    ecrire(x0 + 300, y0 + 130, "AXIALE, et sur elle SEULE. Les trois", petit, GRIS)
    ecrire(x0 + 300, y0 + 146, "autres sont LUES ensuite — rien n'a", petit, GRIS)
    ecrire(x0 + 300, y0 + 162, "été fait pour qu'elles tombent juste.", petit, GRIS)
    ecrire(x0 + 300, y0 + 186, "C'est la méthode de `134`.", petit, GRIS)

    # ---- panneau 2 : le balayage
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le balayage — l'axial monte, l'azimutal ne descend pas", moyen, ENCRE)
    gx, gy, gw, gh = x0 + 54, y0 + 26, pw - 110, ph - 96
    art.rectangle([gx, gy, gx + gw, gy + gh], outline=TRAIT, width=1)
    vmax = max(max(m["axial"], m["azimutal"]) for m in bal) or 1.0
    vmax = max(vmax, float(ro["axial"]), float(ro["azimutal"]))
    xmax = max(m["vrillage"] for m in bal) or 1.0
    for cle, coul in (("azimutal", CONTRE), ("axial", ALERTE)):
        prev = None
        for m in bal:
            px = gx + (m["vrillage"] / xmax) * gw
            py = gy + gh - (m[cle] / vmax) * gh
            if prev is not None:
                art.line([prev[0], prev[1], px, py], fill=coul, width=2)
            art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=coul)
            points.append((px, py))
            prev = (px, py)
        ecrire(gx + gw + 8, (gy + gh - (bal[-1][cle] / vmax) * gh) - 6, cle[:8], 0, coul)
    for lib, val, coul in (("cible axiale", ro["axial"], ALERTE),
                           ("cible azimutale", ro["azimutal"], CONTRE)):
        yy = gy + gh - (float(val) / vmax) * gh
        for xx in range(int(gx), int(gx + gw), 9):
            art.line([xx, yy, xx + 4, yy], fill=coul, width=1)
        ecrire(gx + 6, yy - 14, f"{lib} {_fr(val)}", 0, coul)
    ecrire(gx - 44, gy - 2, _fr(vmax, 2), 0, GRIS)
    ecrire(gx - 20, gy + gh + 4, "0", 0, GRIS)
    ecrire(gx + gw - 28, gy + gh + 4, f"vrillage {_fr(xmax, 2)}", 0, GRIS)
    ecrire(x0 + 12, y0 + ph - 38,
           "l'azimutal vient de l'ÉCRASEMENT, que le vrillage ne touche pas", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20,
           "il faut le vrillage 0,6 pour que le côté bascule — bien après la cible", petit,
           ALERTE)

    # ---- panneau 3 : la pose
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           f"la pose — vrillage {_fr(avec['vrillage'], 5)} posé sur la part axiale", moyen, ENCRE)
    x_barre = x0 + 150
    barre_max = pw - 262
    vm2 = max(sans["axial"], sans["azimutal"], avec["axial"], avec["azimutal"],
              ro["axial"], ro["azimutal"]) or 1.0
    for k, (qui, m, coul_fond) in enumerate((("sans vrillage", sans, GRIS),
                                             ("avec vrillage", avec, ENCRE),
                                             ("le rouleau", ro, ENCRE))):
        base = y0 + 26 + k * 82
        pen = ("AXIALEMENT" if float(m["axial"]) > float(m["azimutal"]) else "azimutalement")
        ecrire(x0 + 12, base, f"{qui} — penche {pen}", petit,
               ALERTE if pen == "AXIALEMENT" else CONTRE)
        for i, (lib, cle, coul) in enumerate((("axiale", "axial", ALERTE),
                                              ("azimutale", "azimutal", CONTRE))):
            yy = base + 20 + i * 20
            val = float(m[cle])
            w = (val / vm2) * barre_max
            ecrire(x0 + 12, yy - 1, f"part {lib}", 0, GRIS)
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
            points.append((x_barre + w, yy + 7))
            barres.append((x_barre + w, x_barre + barre_max))
            ecrire(x_barre + barre_max + 8, yy - 1, _fr(val), 0, coul)
    ecrire(x0 + 12, y0 + ph - 56,
           "★ la calibration touche sa cible au millième — et la matière", petit, BON)
    ecrire(x0 + 12, y0 + ph - 38,
           "penche TOUJOURS azimutalement, parce que l'azimutal n'a pas bougé", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 20,
           f"({_fr(sans['azimutal'])} sans vrillage, {_fr(avec['azimutal'])} avec)", petit, GRIS)

    # ---- panneau 4 : le prix
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le PRIX — la pire des trois, jamais la moyenne", moyen, ENCRE)
    x_barre = x0 + 150
    barre_max = pw - 262
    dmax = max(ds["distance"], da["distance"]) or 1.0
    for k, (qui, dd, coul) in enumerate((("sans vrillage", ds, CONTRE),
                                         ("avec vrillage", da, ALERTE))):
        yy = y0 + 32 + k * 30
        w = (dd["distance"] / dmax) * barre_max
        ecrire(x0 + 12, yy - 1, qui, 0, GRIS)
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 15], fill=coul)
        points.append((x_barre + w, yy + 7))
        barres.append((x_barre + w, x_barre + barre_max))
        ecrire(x_barre + barre_max + 8, yy - 1, _fr(dd["distance"], 4), 0, coul)
    ecrire(x0 + 12, y0 + 96,
           f"la pire des trois est « {ds['la_pire']} » sans vrillage et "
           f"« {da['la_pire']} » avec", 0, GRIS)
    ecrire(x0 + 12, y0 + 118, "les trois grandeurs, écart par écart", petit, ENCRE)
    for i, cle in enumerate(("rapport", "penchant_deg", "coherence")):
        yy = y0 + 142 + i * 18
        ecrire(x0 + 12, yy, cle, 0, GRIS)
        ecrire(x0 + 150, yy, _fr(ds["par_grandeur"][cle], 4), 0, CONTRE)
        ecrire(x0 + 240, yy, "→", 0, GRIS)
        ecrire(x0 + 270, yy, _fr(da["par_grandeur"][cle], 4), 0,
               ALERTE if da["par_grandeur"][cle] > ds["par_grandeur"][cle] else BON)
    ecrire(x0 + 12, y0 + ph - 74,
           "⚠⚠ LE VRILLAGE RAPPROCHE LE RAPPORT ET ÉLOIGNE LE PENCHANT :", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 56,
           f"{_fr(sans['penchant_deg'], 2)}° sans vrillage, {_fr(avec['penchant_deg'], 2)}° avec, "
           f"pour {_fr(ro['penchant_deg'], 2)}° sur le rouleau.", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 32,
           "La pire des trois est ce qui compte : une moyenne pardonnerait à", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 16,
           "une matière qui en reproduit deux et rate la troisième.", petit, GRIS)

    # ---- bande
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    ecrire(74, y + 12,
           f"✗  Il ne donne PAS le côté : posé sur la part axiale du rouleau il la touche au "
           f"millième ({_fr(avec['axial'])} pour {_fr(ro['axial'])}) et la matière penche "
           f"toujours azimutalement.", moyen, ALERTE)
    ecrire(74, y + 38,
           f"✗  Et il ÉLOIGNE des trois grandeurs : la pire des trois passe de "
           f"{_fr(ds['distance'], 4)} à {_fr(da['distance'], 4)}, sur le penchant.", moyen, ALERTE)
    ecrire(74, y + 64,
           f"★★★★  La raison est lisible : le vrillage AJOUTE de l'axial sans RETIRER d'azimutal "
           f"({_fr(sans['azimutal'])} → {_fr(avec['azimutal'])}).", moyen, ENCRE)
    ecrire(74, y + 86,
           f"         Or le rouleau a une part azimutale BASSE ({_fr(ro['azimutal'])}) quand la "
           f"matière calibrée en a presque le double. Ce qui manque n'est pas une cause, c'est un "
           f"EXCÈS.", moyen, ENCRE)
    ecrire(74, y + 110,
           f"★  Le contrôle tient : la spirale nue ne penche pas du tout "
           f"({_fr(c['axial_median'])} de part axiale), donc l'instrument ne mesure pas le "
           f"marcheur.", moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points, barres = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    debordantes = [(round(a, 1), round(b, 1)) for a, b in barres if a > b + 0.5]
    v("⭐⭐⭐⭐ aucune barre ne déborde de son graphe, donc aucune ne recouvre son nombre",
      not debordantes, f"{len(barres)} barres, {debordantes}"[:180])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    # ⚠⚠⚠ LA PART AZIMUTALE EST LA MOITIE QUI REFUTE : c'est parce qu'elle NE BOUGE PAS que la
    # calibration touche sa cible sans donner le cote. Une figure qui ne la montrerait pas ferait
    # lire une reussite.
    faux = copy.deepcopy(d)
    faux["juger"]["avec_vrillage"]["azimutal"] = 0.717
    _c, p2, _cd, _pt, _b = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ la part AZIMUTALE avec vrillage est LUE, pas supposée",
      any("0,717" in t for _x, _y, t, _f in p2) and not any("0,717" in t for t in tous),
      "c'est elle qui refuse le côté malgré une calibration juste")
    faux2 = copy.deepcopy(d)
    faux2["juger"]["distance_avec_vrillage"]["distance"] = 0.3131
    _c, p3, _cd, _pt, _b = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ le PRIX est lu, et c'est la pire des trois",
      any("0,3131" in t for _x, _y, t, _f in p3))
    faux3 = copy.deepcopy(d)
    faux3["juger"]["distance_sans_vrillage"]["distance"] = 0.5151
    _c, p4, _cd, _pt, _b = dessiner(faux3, sortie)
    v("⭐⭐⭐ ... et celui SANS vrillage aussi, sinon il n'y aurait rien à comparer",
      any("0,5151" in t for _x, _y, t, _f in p4))
    faux4 = copy.deepcopy(d)
    for m in faux4["enquete"]["balayage"]:
        m["azimutal"] = 0.04
    _c, _p5, _cd, pt5, _b = dessiner(faux4, sortie)
    v("⭐⭐⭐ le balayage entier est tracé, les deux courbes",
      len(pt5) == len(points), f"{len(pt5)} points contre {len(points)}")
    faux5 = copy.deepcopy(d)
    faux5["juger"]["le_controle_de_la_spirale_nue"]["il_ne_penche_pas"] = False
    _c, p6, _cd, _pt, _b = dessiner(faux5, sortie)
    v("⭐⭐⭐⭐ un contrôle qui cesse de tenir change la marque de la figure",
      any(t.startswith("✗  la spirale nue") for _x, _y, t, _f in p6)
      and not any(t.startswith("✗  la spirale nue") for t in tous))
    v("⚠ la cible du rouleau est écrite à côté de chaque grandeur",
      all(any(_fr(d["juger"]["le_rouleau"][k], 4) in t for t in tous)
          for k in ("axial", "azimutal", "rapport")),
      "sans elle, les nombres de la fixture ne veulent rien dire")

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_170.json"
        tmp.write_text(json.dumps(cassee, ensure_ascii=False))
        try:
            lire(tmp)
            return False
        except ValueError:
            return True
        finally:
            tmp.unlink(missing_ok=True)

    v("⚠ une mesure sans la POSE est REFUSÉE",
      refuse(lambda x: x["juger"].update(avec_vrillage=None)))
    v("⚠⚠ une mesure sans les DEUX distances est REFUSÉE",
      refuse(lambda x: x["juger"].update(distance_sans_vrillage=None)),
      "un prix qui n'est comparé à rien n'est pas un prix")
    v("⚠ une mesure sans le balayage est REFUSÉE",
      refuse(lambda x: x["enquete"].update(balayage=[])))

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "le_vrillage_paie_t_il_le_coin_qui_manque.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "170_le_vrillage_paie_t_il_le_coin_qui_manque.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt, _b = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
