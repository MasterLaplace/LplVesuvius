"""La coupe cherchée trouve-t-elle la frontière ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, la marche DESSINÉE couche par couche, avec
sa frontière et les trois coupes : celle de `173` tombe à huit alors que la frontière est à
trente-sept, et elle rend quand même un quart de tour. En bas à gauche, ce que le mélange laisse. En
bas à droite, la relecture de `173` — ses six longueurs « fiables » ne mettent la coupe au bon
endroit à aucun décalage.

  uv run python src/figures/figure_la_coupe_cherchee_trouve_t_elle_la_frontiere.py \\
      --json docs/mesures/la_coupe_cherchee_trouve_t_elle_la_frontiere.json \\
      --sortie docs/images/174_la_coupe_cherchee_trouve_t_elle_la_frontiere.png
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
RECETTES = ("aveugle", "meilleure", "ajustee")
LIBELLES = {"aveugle": "aveugle (la campagne)", "meilleure": "meilleure (`173`)",
            "ajustee": "ajustée (réparée)"}


def _fr(x, n: int = 2) -> str:
    if x is None:
        return "—"
    return f"{float(x):.{n}f}".rstrip("0").rstrip(".").replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `la_coupe_cherchee_trouve_t_elle_la_frontiere.py`.

    ⚠⚠ Refuse une mesure sans les TROIS recettes : le résultat est que deux d'entre elles manquent
    la frontière et qu'une la trouve, et une figure qui n'en montrerait qu'une ferait lire soit que
    l'instrument est bon, soit qu'il est perdu.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("ou_tombe_la_coupe", "le_melange", "les_trois_matieres",
                "la_relecture_de_173", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if set(d["ou_tombe_la_coupe"].get("par_recette") or {}) != set(RECETTES):
        raise ValueError(f"{chemin} : les trois recettes ne sont pas toutes là")
    if not d["la_relecture_de_173"].get("lignes"):
        raise ValueError(f"{chemin} : la relecture de `173` est vide")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []
    traits: list[tuple[float, float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    c, m, t = d["ou_tombe_la_coupe"], d["le_melange"], d["les_trois_matieres"]
    rl, v = d["la_relecture_de_173"], d["le_verdict"]

    ecrire(28, 20, "La coupe cherchée trouve-t-elle la frontière ? — non, elle trouve le "
                   "déséquilibre", gros, ENCRE)
    ecrire(28, 46, "Maximiser l'écart récompense une coupe dont un côté n'a pas de direction : "
                   "l'écart à une direction arbitraire est arbitrairement grand", petit, GRIS)

    # ---- panneau 1 : la marche DESSINEE, et les trois coupes
    x0, y0, pw, ph = 56, 122, 1248, 238
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           f"la marche de référence — {c['couches']} couches, frontière CONSTRUITE à la couche "
           f"{c['frontiere']}", moyen, ENCRE)
    gx, gy, gw, gh = x0 + 120, y0 + 24, pw - 300, 34
    n = int(c["couches"])
    pas = gw / float(n)
    for i in range(n):
        coul = CONTRE if i < int(c["frontiere"]) else ALERTE
        art.rectangle([gx + i * pas, gy, gx + (i + 1) * pas, gy + gh], fill=coul)
    ecrire(x0 + 14, gy + 8, "l'orientation", 0, GRIS)
    ecrire(gx, gy + gh + 6, "couche 0", 0, GRIS)
    ecrire(gx + gw - 30, gy + gh + 6, str(n), 0, GRIS)
    fx = gx + int(c["frontiere"]) * pas
    art.line([fx, gy - 10, fx, gy + gh + 4], fill=ENCRE, width=3)
    points.append((fx, gy + gh))
    ecrire(fx - 30, gy - 26, f"frontière {c['frontiere']}", 0, ENCRE)
    for k, rec in enumerate(RECETTES):
        x = c["par_recette"][rec]
        yy = y0 + 96 + k * 44
        ok = x["elle_tombe_sur_la_frontiere"]
        ecrire(x0 + 14, yy + 2, f"{'★' if ok else '✗'} {LIBELLES[rec]}", moyen,
               BON if ok else ALERTE)
        cx = gx + int(x["coupe"]) * pas
        art.line([cx, yy, cx, yy + 22], fill=BON if ok else ALERTE, width=3)
        points.append((cx, yy + 22))
        for xx in range(int(min(cx, fx)), int(max(cx, fx)), 8):
            art.line([xx, yy + 11, xx + 4, yy + 11], fill=GRIS, width=1)
        # ⚠⚠ LE TRAIT EST ENREGISTRE AVEC SON ETENDUE : `textes_qui_se_recouvrent` ne voit que du
        # texte contre du texte, et une premiere version faisait passer le pointille EN TRAVERS du
        # libelle « bascule … témoin … ». C'est la lecon de la barre qui debordait dans `167`, sous
        # une autre forme : ce qui est dessine doit etre enregistre pour pouvoir etre verifie.
        traits.append((min(cx, fx), yy + 11, max(cx, fx)))
        ecrire(gx + gw + 10, yy - 4,
               f"coupe {x['coupe']} · écart {x['ecart_a_la_frontiere']}", 0,
               BON if ok else ALERTE)
        ecrire(gx + gw + 10, yy + 12,
               f"bascule {_fr(x['bascule_deg'], 1)}° · témoin {_fr(x['temoin_deg'], 1)}°", 0,
               GRIS)

    # ---- panneau 2 : ce que le melange laisse
    x0, y0, pw, ph = 56, 412, 620, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           f"ce que le mélange laisse — {m['permutations']} permutations des couches", moyen,
           ENCRE)
    a, b = m["la_meilleure_coupe"], m["la_coupe_ajustee"]
    ecrire(x0 + 300, y0 + 12, "réel", petit, ENCRE)
    ecrire(x0 + 390, y0 + 12, "mélanges (max)", petit, GRIS)
    for k, (lib, reel, mx, ok) in enumerate((
            ("l'écart maximisé (`173`)", a["bascule_reelle_deg"],
             a["bascule_maximale_des_permutations_deg"],
             a["elle_depasse_toutes_les_permutations"]),
            ("l'ajustement (réparé)", b["part_atteinte"],
             b["part_maximale_des_permutations"], b["elle_depasse_toutes_les_permutations"]))):
        yy = y0 + 42 + k * 34
        ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} {lib}", moyen, BON if ok else ALERTE)
        ecrire(x0 + 300, yy, _fr(reel, 3), 0, ENCRE)
        ecrire(x0 + 390, yy, _fr(mx, 3), 0, GRIS)
    ecrire(x0 + 14, y0 + 120, "⚠⚠ MÉLANGER CONSERVE LE MULTIENSEMBLE DES ANGLES, donc une", petit,
           ALERTE)
    ecrire(x0 + 14, y0 + 136, "part pure et un mélange restent trouvables : l'écart maximisé", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 152, "survit au mélange, et ne mesure donc pas l'ordre en profondeur.",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 176, "★ L'ajustement, lui, n'y survit pas : sans ordre, aucune coupe", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 192,
           f"ne laisse deux parts dirigées ({b['permutations_refusees']} mélanges refusés).",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 216, "⚠ la borne se DÉRIVE : n directions au hasard rendent 1/√n.", petit,
           GRIS)

    # ---- panneau 3 : les matieres
    x0, y0, pw, ph = 712, 412, 592, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les matières, par la recette réparée", moyen, ENCRE)
    ecrire(x0 + 230, y0 + 12, "bascule", petit, ALERTE)
    ecrire(x0 + 330, y0 + 12, "témoin", petit, CONTRE)
    ecrire(x0 + 430, y0 + 12, "part atteinte", petit, ENCRE)
    for k, (nom, x) in enumerate(t["par_matiere"].items()):
        yy = y0 + 42 + k * 30
        if not x["decidable"]:
            ecrire(x0 + 14, yy, f"✗ {nom}", moyen, ALERTE)
            ecrire(x0 + 230, yy, "refusée", 0, ALERTE)
            continue
        propre = (x["temoin_deg"] == 0.0)
        ecrire(x0 + 14, yy, f"{'★' if propre else '⚠'} {nom[:22]}", moyen,
               BON if propre else CONTRE)
        ecrire(x0 + 230, yy, _fr(x["bascule_deg"], 1), 0, ALERTE)
        ecrire(x0 + 330, yy, _fr(x["temoin_deg"], 1), 0, CONTRE)
        ecrire(x0 + 430, yy, _fr(x["part_atteinte"], 3), 0, ENCRE)
    ecrire(x0 + 14, y0 + 176, "⚠⚠ LA LIMITE EST DITE PLUTÔT QUE TUE : une dérive n'est pas",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 192, "séparée d'une marche par un VERDICT. Ce qui les distingue est",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 208, "le témoin, un nombre à lire — zéro sur une marche — et le", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 224, "prétendre un verdict serait choisir un seuil.", petit, GRIS)

    # ---- panneau 4 : la relecture de 173
    x0, y0, pw, ph = 56, 714, 1248, 168
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           f"la relecture de `173` — {rl['decalages']} décalages par longueur", moyen, ENCRE)
    colonnes = ((120, "aveugle", "aveugle"), (260, "meilleure", "meilleure (`173`)"),
                (430, "ajustee", "ajustée"), (580, "sur_la_frontiere", "SUR LA FRONTIÈRE"))
    for dx, _cle, lib in colonnes:
        ecrire(x0 + dx, y0 + 10, lib, petit, ALERTE if "FRONT" in lib else GRIS)
    for k, x in enumerate(rl["lignes"]):
        yy = y0 + 32 + k * 16
        ecrire(x0 + 14, yy, f"{_fr(x['demande_en_feuilles'])} f", 0, ENCRE)
        for dx, cle, _lib in colonnes:
            plein = x[cle] == x["lus"]
            ecrire(x0 + dx, yy, f"{x[cle]}/{x['lus']}", 0,
                   (BON if plein else GRIS) if cle != "sur_la_frontiere"
                   else (BON if plein else ALERTE))
    ecrire(x0 + 700, y0 + 40,
           f"★ `173` publie {len(v['longueurs_fiables_de_173'])} longueurs « fiables » : "
           f"{', '.join(_fr(f) for f in v['longueurs_fiables_de_173'])}", moyen, ENCRE)
    ecrire(x0 + 700, y0 + 68,
           "✗ et AUCUNE ne met la coupe sur la frontière à tous les décalages :", moyen, ALERTE)
    ecrire(x0 + 700, y0 + 92,
           f"   {v['longueurs_fiables_sur_la_frontiere'] or 'aucune'}", moyen, ALERTE)
    ecrire(x0 + 700, y0 + 122,
           "⚠⚠ « lit la bascule » gagne ici une TROISIÈME condition : la coupe", petit, GRIS)
    ecrire(x0 + 700, y0 + 138,
           "doit tomber sur la frontière, que la fixture connaît.", petit, GRIS)

    # ---- bande
    y = 890
    art.rectangle([56, y, L - 56, y + 66], fill=BANDE)
    cadres.append((56, y, L - 56, y + 66))
    ecrire(74, y + 6,
           f"✗  `173` était juste au mauvais endroit : sa coupe tombe à "
           f"{c['par_recette']['meilleure']['coupe']} quand la frontière est à {c['frontiere']} "
           f"(écart {v['ecart_a_la_frontiere_de_la_meilleure']}), et elle rend pourtant "
           f"{_fr(c['par_recette']['meilleure']['bascule_deg'], 1)}°.", moyen, ALERTE)
    ecrire(74, y + 26,
           "★★★★  La réparation a deux pièces et aucune n'est un seuil : une moyenne sans "
           "résultante n'est pas une direction, et la coupe s'obtient", moyen, ENCRE)
    ecrire(74, y + 46,
           f"         en AJUSTANT deux segments. Elle tombe sur "
           f"{c['par_recette']['ajustee']['coupe']}, et elle ne survit pas au mélange.",
           moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres, traits


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
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
    v("aucune barre ne déborde de son graphe", not debordantes, f"{len(barres)} barres")
    v("les traits tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} repères")

    def _boite(x, y, texte, f):
        b = f.getbbox(texte)
        return (x + b[0], y + b[1], x + b[2], y + b[3])

    # ⭐⭐⭐⭐ LE CONTROLE QUE L'OEIL A DICTE : un trait qui traverse un texte le rend illisible, et
    # aucun controle de texte ne le voit puisqu'il ne regarde que du texte contre du texte.
    traverses = [(t, round(x1), round(x2)) for x1, ty, x2 in traits
                 for (px, py, t, f) in poses
                 if (lambda b: b[0] < x2 and b[2] > x1 and b[1] <= ty <= b[3])(
                     _boite(px, py, t, f))]
    v("⭐⭐⭐⭐ aucun trait ne traverse un texte", not traverses,
      f"{len(traits)} traits, {traverses}"[:180])

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    # ⭐⭐⭐⭐ LES TROIS COUPES SONT DESSINEES DEPUIS LA MESURE : c'est leur ECART a la frontiere qui
    # porte l'argument, et une coupe ecrite en dur le supprimerait de l'image.
    for rec in RECETTES:
        faux = copy.deepcopy(d)
        faux["ou_tombe_la_coupe"]["par_recette"][rec]["coupe"] = 71
        faux["ou_tombe_la_coupe"]["par_recette"][rec]["ecart_a_la_frontiere"] = 34
        _c, p2, _cd, pt2, _b, _t = dessiner(faux, sortie)
        v(f"⭐⭐⭐ la coupe « {rec} » est lue et son trait se déplace",
          any("coupe 71" in t for _x, _y, t, _f in p2) and pt2 != points)
    faux2 = copy.deepcopy(d)
    faux2["ou_tombe_la_coupe"]["frontiere"] = 71
    _c, p3, _cd, _pt, _b, _t = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ la frontière est lue, pas écrite en dur",
      any("frontière 71" in t for _x, _y, t, _f in p3)
      and not any("frontière 71" in t for t in tous))
    faux3 = copy.deepcopy(d)
    faux3["le_melange"]["la_coupe_ajustee"]["part_maximale_des_permutations"] = 0.717
    _c, p4, _cd, _pt, _b, _t = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ le maximum des permutations est lu, et c'est LUI qui fait le contrôle",
      any("0,717" in t for _x, _y, t, _f in p4) and not any("0,717" in t for t in tous))
    faux4 = copy.deepcopy(d)
    faux4["la_relecture_de_173"]["lignes"][2]["sur_la_frontiere"] = 5
    _c, p5, _cd, _pt, _b, _t = dessiner(faux4, sortie)
    v("⭐⭐⭐⭐ la colonne « sur la frontière » est lue ligne par ligne",
      any("5/12" in t for _x, _y, t, _f in p5))
    faux5 = copy.deepcopy(d)
    faux5["le_verdict"]["longueurs_fiables_sur_la_frontiere"] = [1.25]
    _c, p6, _cd, _pt, _b, _t = dessiner(faux5, sortie)
    v("⭐⭐⭐ ... et « aucune » n'est pas écrit en dur",
      any("1,25" in t for _x, _y, t, _f in p6) and any("aucune" in t for t in tous))
    # ⚠ Une mesure a qui il manque une recette est REFUSEE.
    creux = copy.deepcopy(d)
    creux["ou_tombe_la_coupe"]["par_recette"].pop("ajustee", None)
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("une mesure à qui il manque une recette est REFUSÉE", lire_ok)

    dessiner(d, sortie)
    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {faits} checks)")
    else:
        print(f"ALL PASS (0 failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "la_coupe_cherchee_trouve_t_elle_la_frontiere.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "174_la_coupe_cherchee_trouve_t_elle_la_frontiere.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
