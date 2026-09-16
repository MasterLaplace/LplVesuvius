"""Le cap agit-il sur les deux axes ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les deux populations du rouleau
et le fait que la plus courte est incluse dans l'autre. En haut à droite, ce que l'appariement
change, axe par axe. En bas à gauche, la fixture matière par matière — appariée par construction.
En bas à droite, le lien entre cohérence et effet du cap, et là où il ne tient pas.

  uv run python src/figures/figure_le_cap_agit_il_sur_les_deux_axes.py \\
      --json docs/mesures/le_cap_agit_il_sur_les_deux_axes.json \\
      --sortie docs/images/171_le_cap_agit_il_sur_les_deux_axes.png
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
    """Le JSON de `le_cap_agit_il_sur_les_deux_axes.py`.

    ⚠⚠ Refuse une mesure dont le rouleau n'a qu'UNE des deux lectures : le résultat de cette
    tranche est l'écart entre elles, et une figure qui n'en montrerait qu'une reconduirait
    exactement le défaut qu'elle est faite pour montrer.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    ro = d.get("le_rouleau") or {}
    if not ro.get("decidable"):
        raise ValueError(f"{chemin} : {ro.get('raison', 'le rouleau est indécidable')}")
    for cle in ("toutes_les_bandes", "bandes_appariees", "lappariement_change_la_reponse"):
        if not ro.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not (d.get("la_fixture") or {}).get("par_matiere"):
        raise ValueError(f"{chemin} : la fixture est absente")
    if not d["la_fixture"].get("la_matiere_du_rouleau"):
        raise ValueError(f"{chemin} : la matière du rouleau n'est pas nommée")
    if not (d.get("le_verdict") or {}).get("cas_examines"):
        raise ValueError(f"{chemin} : le verdict est absent")
    if not (d.get("lecart_a_la_fixture") or {}).get("decidable"):
        raise ValueError(f"{chemin} : l'écart à la fixture est absent")
    return d


def court(nom: str) -> str:
    """Le nom d'un cas, assez court pour tenir dans la liste du verdict.

    ⚠ Le raccourci est DECLARE UNE FOIS et employé par le dessin comme par le contrôle : deux
    raccourcis seraient deux orthographes du même cas, et le contrôle chercherait alors un nom
    que la figure n'écrit pas.
    """
    return (nom.replace("le rouleau, bandes appariées", "le rouleau (appariées)")
               .replace("spirale ", "").replace("écrasée et froissée", "écrasée+froissée"))


def envelopper(noms: list[str], largeur: int) -> list[str]:
    """Des noms répartis sur plusieurs lignes, sans jamais couper un nom en deux.

    ⚠⚠ UNE LISTE TRONQUEE EST PIRE QU'UNE LISTE ABSENTE : elle a l'air complète. La première
    version de cette figure coupait la liste des cas à soixante-quatorze caractères et perdait
    sa troisième matière en laissant une virgule pendante — aucun contrôle de texte ne voit ça,
    parce que la ligne coupée tient parfaitement dans son cadre. C'est l'œil qui l'a trouvée.
    """
    lignes: list[str] = []
    for nom in noms:
        if lignes and len(lignes[-1]) + 2 + len(nom) <= largeur:
            lignes[-1] = f"{lignes[-1]}, {nom}"
        else:
            lignes.append(nom)
    return lignes


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

    ro, fx, ve = d["le_rouleau"], d["la_fixture"], d["le_verdict"]
    ec = d["lecart_a_la_fixture"]
    # ⚠⚠ LA MATIERE DU ROULEAU EST LUE PAR SON NOM, jamais prise par son rang dans la liste.
    rou = next(m for m in fx["par_matiere"] if m["nom"] == fx["la_matiere_du_rouleau"])
    tout, app = ro["toutes_les_bandes"], ro["bandes_appariees"]
    chg = ro["lappariement_change_la_reponse"]

    ecrire(28, 20, "Le cap agit-il sur les deux axes ? — et la comparaison publiée porte sur "
                   "deux populations inégales", gros, ENCRE)
    ecrire(28, 46, "`R4-P27` demandait pourquoi la fixture marche deux fois trop azimutalement ; "
                   "sans cap elle est EN DESSOUS du rouleau, et l'écart est un effet du cap",
           petit, GRIS)

    # ---- panneau 1 : les deux populations
    x0, y0, pw, ph = 56, 122, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux courses du rouleau — et l'appariement qui existe", moyen, ENCRE)
    bpc = ro["bandes_par_cap"]
    for k, (cap, n) in enumerate(sorted(bpc.items(), key=lambda kv: float(kv[0]))):
        yy = y0 + 24 + k * 30
        w = (n / max(bpc.values())) * (pw - 300)
        ecrire(x0 + 14, yy - 1, f"cap {_fr(float(cap), 2)}", 0, GRIS)
        art.rectangle([x0 + 110, yy, x0 + 110 + max(w, 1), yy + 15], fill=CONTRE)
        points.append((x0 + 110 + w, yy + 7))
        barres.append((x0 + 110 + w, x0 + 110 + (pw - 300)))
        ecrire(x0 + 110 + (pw - 300) + 8, yy - 1, f"{n} bandes", 0, CONTRE)
    marq = "★" if ro["la_plus_courte_est_incluse"] else "✗"
    ecrire(x0 + 14, y0 + 96,
           f"{marq}  la plus courte est INCLUSE dans l'autre : "
           f"{ro['bandes_communes']} bandes communes", moyen,
           BON if ro["la_plus_courte_est_incluse"] else ALERTE)
    ecrire(x0 + 14, y0 + 126, "⚠⚠⚠ COMPARER DES TOTAUX SUR DES POPULATIONS INÉGALES", petit,
           ALERTE)
    ecrire(x0 + 14, y0 + 144, "est le péché capital de ce dépôt. Ici il est RÉPARABLE : les",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 160, "deux lectures sont rendues côte à côte, et c'est l'écart",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 176, "entre elles qui est le résultat.", petit, GRIS)
    ecrire(x0 + 14, y0 + 202,
           f"⚠ la fixture, elle, est appariée PAR CONSTRUCTION : {fx['departs']} départs",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 218, "marchés aux DEUX caps, donc rien à réparer de ce côté.",
           petit, GRIS)

    # ---- panneau 2 : ce que l'appariement change
    x0, y0, pw, ph = 712, 122, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que l'appariement change — le rouleau, axe par axe", moyen, ENCRE)
    ecrire(x0 + 200, y0 + 12, "sans appariement", petit, GRIS)
    ecrire(x0 + 330, y0 + 12, "apparié", petit, ENCRE)
    ecrire(x0 + 430, y0 + 12, "change de sens", petit, ALERTE)
    for k, axe in enumerate(("axial", "azimutal")):
        yy = y0 + 38 + k * 30
        ecrire(x0 + 14, yy, f"le cap multiplie l'{axe}", 0, GRIS)
        ecrire(x0 + 200, yy, "×" + _fr(chg[axe]["sans_appariement"]), 0, CONTRE)
        ecrire(x0 + 330, yy, "×" + _fr(chg[axe]["apparie"]), 0, ENCRE)
        ecrire(x0 + 430, yy, "oui" if chg[axe]["le_cap_change_de_sens"] else "non", 0,
               ALERTE if chg[axe]["le_cap_change_de_sens"] else GRIS)
    x_barre, barre_max = x0 + 168, pw - 280
    e_a = app["effet"]
    vm = max(e_a[f"part_{a}e_{c}_cap"] for a in ("axial", "azimutal")
             for c in ("sans", "avec")) or 1.0
    ecrire(x0 + 14, y0 + 108, "les parts sur les bandes APPARIÉES", moyen, ENCRE)
    for k, (lib, cle) in enumerate((("axiale sans cap", "part_axiale_sans_cap"),
                                    ("axiale avec cap", "part_axiale_avec_cap"),
                                    ("azimutale sans cap", "part_azimutale_sans_cap"),
                                    ("azimutale avec cap", "part_azimutale_avec_cap"))):
        yy = y0 + 134 + k * 24
        val = float(e_a[cle])
        w = (val / vm) * barre_max
        coul = ALERTE if lib.startswith("axiale") else CONTRE
        ecrire(x0 + 14, yy - 1, lib, 0, GRIS)
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 15], fill=coul)
        points.append((x_barre + w, yy + 7))
        barres.append((x_barre + w, x_barre + barre_max))
        ecrire(x_barre + barre_max + 8, yy - 1, _fr(val), 0, coul)

    # ---- panneau 3 : la fixture, matiere par matiere
    x0, y0, pw, ph = 56, 450, 620, 292
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la fixture — ce que le cap multiplie, matière par matière", moyen, ENCRE)
    ecrire(x0 + 300, y0 + 10, "axial", petit, ALERTE)
    ecrire(x0 + 400, y0 + 10, "azimutal", petit, CONTRE)
    ecrire(x0 + 500, y0 + 10, "lien", petit, ENCRE)
    for k, m in enumerate(fx["par_matiere"]):
        yy = y0 + 34 + k * 26
        e = m["effet"]
        ecrire(x0 + 14, yy, m["nom"][:36], 0, ENCRE)
        for dx, cle, coul in ((300, "le_cap_multiplie_l_axial_par", ALERTE),
                              (400, "le_cap_multiplie_l_azimutal_par", CONTRE)):
            ecrire(x0 + dx, yy, "×" + _fr(e.get(cle)) if e.get(cle) is not None else "—", 0, coul)
        li = m["lien"]
        if li.get("decidable"):
            ecrire(x0 + 500, yy, "★ tient" if li["le_cap_retire_ce_qui_alterne"] else "✗ non",
                   0, BON if li["le_cap_retire_ce_qui_alterne"] else ALERTE)
        else:
            ecrire(x0 + 500, yy, "non posable", 0, GRIS)
    ecrire(x0 + 14, y0 + 178, "⚠ le contrôle VIDE est la spirale nue : son axe axial ne porte",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 194, "rien, donc le lien n'y est PAS posable — le dire vaut mieux",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 210, "que trancher à pile ou face.", petit, GRIS)
    ecrire(x0 + 14, y0 + 236,
           f"⚠ un rapport sous un est une réduction ; au-dessus, le cap AJOUTE.", petit, GRIS)
    ecrire(x0 + 14, y0 + 254,
           f"{fx['departs']} départs, {fx['pas_max']} pas, rayon {_fr(fx['rayon_mm'], 1)} mm",
           petit, GRIS)

    # ---- panneau 4 : le lien
    x0, y0, pw, ph = 712, 450, 592, 292
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le lien — le cap mord-il l'axe qui ALTERNE ?", moyen, ENCRE)
    li = app["lien"]
    if li.get("decidable"):
        ecrire(x0 + 14, y0 + 16, "sur le rouleau, bandes appariées :", moyen, ENCRE)
        for k, (lib, cle, coul) in enumerate((
                ("cohérence axiale sans cap", "axial", ALERTE),
                ("cohérence azimutale sans cap", "azimutal", CONTRE))):
            yy = y0 + 44 + k * 20
            ecrire(x0 + 14, yy, lib, 0, GRIS)
            ecrire(x0 + 250, yy, _fr(li["coherences_sans_cap"][cle]), 0, coul)
            ecrire(x0 + 320, yy, "le cap ×" + _fr(li["rapports"][cle]), 0, coul)
        ecrire(x0 + 14, y0 + 92,
               f"l'axe le moins cohérent  : {li['laxe_le_moins_coherent_sans_cap']}", moyen,
               ENCRE)
        ecrire(x0 + 14, y0 + 114,
               f"l'axe le plus réduit     : {li['laxe_que_le_cap_reduit_le_plus']}", moyen, ENCRE)
        tient = li["le_cap_retire_ce_qui_alterne"]
        ecrire(x0 + 14, y0 + 142,
               ("★  ce sont le même — le cap retire ce qui alterne" if tient
                else "✗  ce ne sont PAS le même — le cap mord l'axe le plus COHÉRENT"),
               moyen, BON if tient else ALERTE)
    else:
        ecrire(x0 + 14, y0 + 16, f"le lien n'est pas posable sur le rouleau — {li.get('raison')}",
               moyen, GRIS)
    ecrire(x0 + 14, y0 + 166, "⚠⚠ LE VERDICT EST JOINT : un cap qui retirerait ce qui alterne "
                              "une fois sur deux", petit, GRIS)
    ecrire(x0 + 14, y0 + 182, "ne retire pas ce qui alterne.", petit, GRIS)
    yy = y0 + 204
    ecrire(x0 + 14, yy, f"cas posables : {ve['cas_posables']} sur {ve['cas_examines']}",
           petit, ENCRE)
    for lib, noms, coul in (("★ le lien tient", ve["ou_le_lien_tient"], BON),
                            ("✗ il ne tient pas", ve["ou_le_lien_ne_tient_pas"], ALERTE)):
        yy += 17
        ecrire(x0 + 14, yy, f"{lib} ({len(noms)})", petit, coul if noms else GRIS)
        for ligne in envelopper([court(x) for x in noms], 72):
            yy += 15
            ecrire(x0 + 28, yy, ligne, petit, coul)

    # ---- bande
    y = 770
    art.rectangle([56, y, L - 56, y + 132], fill=BANDE)
    cadres.append((56, y, L - 56, y + 132))
    ecrire(74, y + 12,
           f"✗  `R4-P27` posait une fausse prémisse : SANS cap la fixture rend "
           f"{_fr(rou['effet']['part_azimutale_sans_cap'])} d'azimutal là où le "
           f"rouleau en rend {_fr(tout['effet']['part_azimutale_sans_cap'])} — elle est EN "
           f"DESSOUS.", moyen, ALERTE)
    ecrire(74, y + 38,
           f"★★★★  Et la comparaison des deux caps du rouleau porte sur "
           f"{'/'.join(str(v) for _k, v in sorted(ro['bandes_par_cap'].items()))} bandes : "
           f"appariée, le cap MULTIPLIE la part axiale par "
           f"{_fr(chg['axial']['apparie'])} au lieu de la diviser.", moyen, ENCRE)
    ecrire(74, y + 64,
           f"★★★★  Et l'azimutal du rouleau ne tombe pas à "
           f"{_fr(tout['effet']['part_azimutale_avec_cap'])} mais à "
           f"{_fr(app['effet']['part_azimutale_avec_cap'])} : le « deux fois trop » vaut "
           f"×{_fr(ec['toutes_les_bandes_avec_cap']['la_fixture_vaut_le_rouleau_fois'])} publié "
           f"et ×{_fr(ec['bandes_appariees_avec_cap']['la_fixture_vaut_le_rouleau_fois'])} "
           f"apparié.", moyen, ENCRE)
    ecrire(74, y + 90,
           f"✗  Le mécanisme attendu est REFUSÉ : sur le rouleau l'axe le moins cohérent est "
           f"« {li.get('laxe_le_moins_coherent_sans_cap', '—')} » et l'axe que le cap réduit est "
           f"« {li.get('laxe_que_le_cap_reduit_le_plus', '—')} ».", moyen, ALERTE)
    ecrire(74, y + 112,
           f"★  Le contrôle tient : sur la spirale nue l'axe axial ne porte rien, donc le lien "
           f"n'y est pas posable et aucun verdict n'y est rendu.", moyen, ENCRE)

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
    ve = d["le_verdict"]

    # ⭐⭐⭐⭐ LES DEUX LECTURES DU ROULEAU SONT DESSINEES, ET C'EST TOUT LE SUJET. Une figure qui
    # n'en porterait qu'une reconduirait le defaut qu'elle existe pour montrer.
    faux = copy.deepcopy(d)
    faux["le_rouleau"]["lappariement_change_la_reponse"]["axial"]["sans_appariement"] = 0.717
    _c, p2, _cd, _pt, _b = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ le rapport SANS appariement est lu, pas supposé",
      any("0,717" in t for _x, _y, t, _f in p2) and not any("0,717" in t for t in tous))
    faux2 = copy.deepcopy(d)
    faux2["le_rouleau"]["lappariement_change_la_reponse"]["axial"]["apparie"] = 0.515
    _c, p3, _cd, _pt, _b = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ ... et celui APPARIÉ aussi, sinon il n'y aurait rien à comparer",
      any("0,515" in t for _x, _y, t, _f in p3))
    faux3 = copy.deepcopy(d)
    faux3["le_rouleau"]["bandes_appariees"]["effet"]["part_azimutale_avec_cap"] = 0.313
    _c, p4, _cd, _pt, _b = dessiner(faux3, sortie)
    v("⭐⭐⭐ la part azimutale APPARIÉE avec cap est lue",
      any("0,313" in t for _x, _y, t, _f in p4))
    # ⚠⚠ LA MATIERE DU ROULEAU EST LUE PAR SON NOM : si la figure la prenait par son rang, changer
    # le nom ne changerait rien et le chiffre de la bande resterait celui d'une autre matiere.
    faux4 = copy.deepcopy(d)
    for m in faux4["la_fixture"]["par_matiere"]:
        if m["nom"] == faux4["la_fixture"]["la_matiere_du_rouleau"]:
            m["effet"]["part_azimutale_sans_cap"] = 0.919
    _c, p5, _cd, _pt, _b = dessiner(faux4, sortie)
    v("⭐⭐⭐ la matière du rouleau est trouvée par son NOM, pas par son rang",
      any("0,919" in t for _x, _y, t, _f in p5))
    # ⚠⚠ LE VERDICT DU LIEN EST LU, ET IL PEUT VALOIR L'AUTRE CHOSE : une figure qui ecrirait
    # « refuse » en dur passerait le jour ou la mesure dirait le contraire.
    faux5 = copy.deepcopy(d)
    faux5["le_rouleau"]["bandes_appariees"]["lien"]["le_cap_retire_ce_qui_alterne"] = True
    _c, p6, _cd, _pt, _b = dessiner(faux5, sortie)
    v("⭐⭐⭐⭐ le verdict du lien est LU, pas écrit en dur",
      any("ce sont le même" in t for _x, _y, t, _f in p6)
      and not any("ce sont le même" in t for t in tous))
    # ⚠ Une mesure incomplete est REFUSEE, jamais dessinee a moitie.
    creux = copy.deepcopy(d)
    creux["le_rouleau"]["bandes_appariees"] = {}
    try:
        lire_ok = False
        chemin_tmp = sortie.with_name(sortie.stem + "_creux.png")
        json_tmp = json_path.with_name(json_path.stem + "_creux.json")
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
        chemin_tmp.unlink(missing_ok=True)
    v("une mesure sans la lecture appariée est REFUSÉE, jamais dessinée à moitié", lire_ok)
    # ⭐⭐⭐⭐ LE CONTROLE QUE L'OEIL A DICTE : une liste tronquee tient parfaitement dans son
    # cadre, donc aucun controle de texte ne la voit. Celui-ci exige que CHAQUE nom cite par le
    # verdict apparaisse quelque part dans la figure.
    attendus = [court(x) for x in ve["ou_le_lien_tient"] + ve["ou_le_lien_ne_tient_pas"]]
    absents = [x for x in attendus if not any(x in t for t in tous)]
    v("⭐⭐⭐⭐ chaque cas nommé par le verdict est écrit en entier, aucun n'est tronqué",
      not absents and attendus, f"{len(attendus)} cas, absents : {absents}"[:180])
    v("... et le nombre de cas posables est celui que le verdict compte",
      any(f"cas posables : {ve['cas_posables']} sur {ve['cas_examines']}" in t for t in tous))
    # ⭐⭐⭐⭐ LE NOMBRE QUE `R4-P27` APPELLE « DEUX FOIS TROP » EST LU SOUS SES DEUX VALEURS.
    faux6 = copy.deepcopy(d)
    faux6["lecart_a_la_fixture"]["bandes_appariees_avec_cap"][
        "la_fixture_vaut_le_rouleau_fois"] = 0.717
    _c, p7, _cd, _pt, _b = dessiner(faux6, sortie)
    v("⭐⭐⭐⭐ l'écart apparié à la fixture est lu, pas supposé",
      any("0,717" in t for _x, _y, t, _f in p7) and not any("0,717" in t for t in tous))

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
                   default=RACINE / "docs" / "mesures" / "le_cap_agit_il_sur_les_deux_axes.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "171_le_cap_agit_il_sur_les_deux_axes.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
