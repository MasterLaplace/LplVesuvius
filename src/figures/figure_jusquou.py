#!/usr/bin/env python3
"""Le plafond est encore la mesure — et pourtant le taux ne baisse pas.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** La tranche `113` a
été lancée pour une raison précise : `107` mesurait une portée avec un plafond de six pas, et
**56 marches sur 56** le touchaient. Un plafond que tout le monde atteint n'est pas une borne
observée, c'est un réglage — donc « la portée vaut 1 250 µm » ne disait rien de la portée. Le
plafond est passé à vingt.

  ⭐ Le panneau de GAUCHE montre ce que la relance a rendu : **28 marches sur 28 touchent le
  nouveau plafond**, zéro sortie de volume, zéro marche arrêtée par quoi que ce soit. La portée
  est censurée une crantée plus haut. Ce qui a bougé est la **borne inférieure** — de 1,25 à
  3,97 mm — et c'est tout ce qu'on peut en dire.

  ⭐⭐ Le panneau de DROITE est le résultat, et il est positif dans sa forme négative : sur vingt
  pas, le taux de confirmation **ne décroît pas**. Si le marcheur accumulait de l'erreur, ce
  nuage descendrait ; il est plat autour de 0,52 du premier pas au vingtième.

⚠ Les deux panneaux répondent à deux questions différentes et il faut les garder séparés : « la
mesure a-t-elle mesuré quelque chose » (non) et « ce qu'elle a quand même vu dégrade-t-il »
(non). Les mettre sur un seul axe ferait lire le second comme une consolation du premier.

  uv run python src/figures/figure_jusquou.py \\
      --json docs/mesures/jusquou_va_t_il_si_on_le_laisse.json \\
      --sortie docs/images/113_le_plafond_est_encore_la_mesure.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (police, textes_debordants, textes_hors_cadre,  # noqa: E402
                            textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
PLAFOND = (176, 62, 62)
MARCHE = (86, 104, 132)
TAUX = (60, 110, 90)
ANCIEN = (196, 140, 60)

PLAFOND_DE_107 = 6
LONGUEUR_DE_107_UM = 1250.0
"""⚠ Les deux chiffres de `107` sont **relus dans le même JSON** (bloc
`ce_qui_a_arrete_les_marches_de_107`) et pas recopiés ici : une constante écrite dans une figure
est une seconde source, et c'est précisément la classe de défaut que ce dépôt traque. Ces deux
noms ne servent que de repli si le bloc manque, et la batterie vérifie qu'ils s'accordent."""


def lire(chemin: Path) -> dict:
    """Le JSON de `jusquou_va_t_il_si_on_le_laisse.py`.

    ⚠ Refuse une course **incomplète** plutôt que de dessiner les bandes déjà faites : une
    figure tirée d'un run à moitié rendu a exactement l'air d'une figure d'un run entier, et
    c'est ce qui ferait publier une part-au-plafond calculée sur la moitié des marches.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if d.get("course_incomplete"):
        raise ValueError(f"{chemin} : course incomplète, rien à dessiner")
    if not d.get("lignes"):
        raise ValueError(f"{chemin} ne porte aucune bande")
    if "resume" not in d or "profondeur_de_la_confirmation" not in d:
        raise ValueError(f"{chemin} : agrégats absents — relancer avec --reagreger")
    return d


def marches(d: dict) -> list[dict]:
    """Une marche par entrée, dans l'ordre des bandes."""
    return [x for l in d["lignes"] for x in l["detail"]]


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list]:
    """Dessine, et rend AUSSI les poses de texte et les cadres.

    ⚠⚠ Les rendre n'est pas un confort : les trois gardes de `figure_commune`
    (`textes_debordants`, `textes_hors_cadre`, `textes_qui_se_recouvrent`) ne peuvent juger que
    ce qu'on leur donne, et une figure qui garde ses poses pour elle est une figure qu'aucune
    batterie ne peut relire. La première version de ce fichier écrivait ses deux annotations
    **par-dessus les barres** et coupait sa dernière ligne hors de la toile ; c'est l'œil qui
    l'a vu, ce qui est l'ordre à inverser.
    """
    r = d["resume"]
    ms_ = marches(d)
    # ⚠⚠ La hauteur de la toile est DÉRIVÉE du nombre de marches, jamais posée : la grille a une
    # ligne par marche, donc une constante ferait déborder le jour où une campagne en rend
    # trente. Et le panneau de droite garde une hauteur FIXE — la sienne ne dépend pas des
    # marches, et la lui faire suivre a écrasé ses cinq graduations les unes sur les autres dès
    # que la fixture n'a eu que deux marches.
    HAUT_CASE, JEU, PH_DROITE = 10, 3, 330
    ph_gauche = max(len(ms_) * (HAUT_CASE + JEU), 40)
    L = 1180
    H = 112 + max(ph_gauche, PH_DROITE) + 148
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    a107 = d.get("ce_qui_a_arrete_les_marches_de_107", {})
    plaf107 = a107.get("plafond", PLAFOND_DE_107)
    long107 = a107.get("longueur_mediane_um", LONGUEUR_DE_107_UM)
    ms = marches(d)

    ecrire(28, 20, "Jusqu'où va-t-il si on le laisse ?", gros, ENCRE)
    ecrire(28, 46, f"{r['marches']} marches · plafond {plaf107} → {r['plafond']} pas · "
                   f"{d['fragment']} · sélecteur « {d['selecteur']} »", petit, GRIS)

    # ── Panneau gauche : chaque marche, pas par pas ──────────────────────────
    # ⚠⚠ La première version dessinait une BARRE par marche, hauteur = pas parcourus. Comme
    # les 28 marches font toutes exactement 20 pas, ça rendait un rectangle plein : une image
    # qui ne porte aucune information, alors que la mesure en porte trois. La grille les montre
    # toutes les trois à la fois — le mur à droite (le plafond que tout le monde touche), le
    # damier (les confirmations ne sont pas groupées), et l'absence de dégradé gauche-droite
    # (le taux ne baisse pas avec la profondeur).
    x0, y0 = 96, 112
    case, jeu, haut = 20, JEU, HAUT_CASE
    pmax = r["plafond"]
    pw, ph = pmax * case, ph_gauche
    ecrire(x0, y0 - 26, "chaque marche, pas par pas  (plein = pas confirmé)", moyen, ENCRE)
    # ⚠⚠ Les lignes sont ordonnées par RAYON, et le dire change ce que la figure montre : sans
    # cette étiquette, le vidage progressif vers le bas se lit comme un artefact d'ordre.
    ray = [l.get("rayon_mm") for l in d["lignes"] for _ in l["detail"]]

    for i, m in enumerate(ms):
        y = y0 + i * (haut + jeu)
        etapes = m.get("etapes") or []
        for k in range(pmax):
            x = x0 + k * case
            confirme = k < len(etapes) and etapes[k].get("confirme")
            if k < m["pas_parcourus"]:
                art.rectangle([x, y, x + case - 4, y + haut - 2],
                              fill=MARCHE if confirme else None,
                              outline=MARCHE if confirme else TRAIT)
    for k in (1, 5, 10, 15, 20):
        ecrire(x0 + (k - 1) * case + 2, y0 + ph + 6, str(k), petit, GRIS)

    # ⚠ Le plafond de `107` est un TRAIT VERTICAL, et c'est ce qui rend la censure visible :
    # tout ce qui est à sa droite est ce que la mesure précédente ne pouvait pas voir.
    x107 = x0 + plaf107 * case - 2
    art.line([x107, y0 - 6, x107, y0 + ph + 2], fill=ANCIEN, width=2)
    xfin = x0 + pmax * case - 4
    art.line([xfin, y0 - 6, xfin, y0 + ph + 2], fill=PLAFOND, width=3)
    if ray and ray[0] is not None:
        ecrire(x0 - 86, y0 - 4, f"rayon {ray[0]:.1f} mm", petit, GRIS)
        ecrire(x0 - 86, y0 + ph - 12, f"rayon {ray[-1]:.1f} mm", petit, GRIS)
    # ⚠ La légende du milieu n'est écrite que si la grille est assez haute pour l'accueillir.
    # Sans la condition elle touche les étiquettes de rayon dès que la course est courte, et
    # « elle ne se cogne que d'un pixel » est exactement le réglage qu'on ne fait pas.
    if ph > 90:
        ecrire(x0 - 86, y0 + ph // 2 - 6, "une ligne", petit, GRIS)
        ecrire(x0 - 86, y0 + ph // 2 + 8, "= une bande", petit, GRIS)

    ly = y0 + max(ph, PH_DROITE) + 30
    art.line([x0, ly + 6, x0 + 22, ly + 6], fill=PLAFOND, width=3)
    ecrire(x0 + 28, ly, f"plafond d'ici ({pmax} pas) — {r['marches_au_plafond']}/{r['marches']} "
                        f"marches le touchent, {r['sorties_du_volume']} sortie de volume",
           petit, PLAFOND)
    art.line([x107 - 130, ly + 24, x107 - 108, ly + 24], fill=ANCIEN, width=2)
    ecrire(x107 - 102, ly + 18, f"plafond de 107 ({plaf107}) — 56/56 le touchaient ; "
                                f"tout ce qui est à droite était invisible", petit, ANCIEN)
    ecrire(x0, ly + 38, f"longueur médiane {r['longueur_mediane_um']:.0f} µm "
                        f"(max {r['longueur_max_um']:.0f}), contre {long107:.0f} à 107 : "
                        f"une borne inférieure, pas une portée", petit, ENCRE)
    q = d.get("le_taux_suit_il_le_rayon", {})
    disp = d.get("le_taux_depend_il_de_la_marche", {})
    if q.get("decidable") and disp.get("decidable"):
        ecrire(x0, ly + 54,
               f"le taux va de {disp['taux_min']:.2f} à {disp['taux_max']:.2f} selon la marche "
               f"(dispersion ×{disp['indice_de_dispersion']:.1f}) et SUIT LE RAYON : "
               f"rho {q['rho_de_spearman']:+.3f}, p = {q['p']:.1e}", petit, PLAFOND)

    # ── Panneau droit : le taux, par profondeur ──────────────────────────────
    x1, pw2, ph2 = 672, 440, PH_DROITE
    art.rectangle([x1, y0, x1 + pw2, y0 + ph2], outline=TRAIT)
    ecrire(x1, y0 - 26, "le taux de confirmation, par profondeur  (pas depuis le départ)",
           moyen, ENCRE)

    prof = d["profondeur_de_la_confirmation"]
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = y0 + ph2 - int(ph2 * t)
        art.line([x1, y, x1 + pw2, y], fill=TRAIT)
        ecrire(x1 - 32, y - 7, f"{t:.2f}", petit, GRIS)

    global_ = r["taux_de_confirmation_global"]
    yg = y0 + ph2 - int(ph2 * global_)
    art.line([x1, yg, x1 + pw2, yg], fill=TAUX, width=2)

    pas_x2 = pw2 / max(len(prof), 1)
    precedent = None
    for i, e in enumerate(prof):
        x = x1 + int((i + 0.5) * pas_x2)
        y = y0 + ph2 - int(ph2 * e["taux"])
        if precedent:
            art.line([precedent[0], precedent[1], x, y], fill=MARCHE, width=2)
        art.ellipse([x - 4, y - 4, x + 4, y + 4], fill=MARCHE)
        precedent = (x, y)
        if e["pas"] in (1, 5, 10, 15, 20):
            ecrire(x - 5, y0 + ph2 + 6, str(e["pas"]), petit, GRIS)

    b = d["le_taux_baisse_avec_la_profondeur"]
    art.line([x1, ly + 6, x1 + 22, ly + 6], fill=TAUX, width=2)
    ecrire(x1 + 28, ly, f"taux global {global_:.3f} — plat du premier pas au vingtième",
           petit, TAUX)
    ecrire(x1, ly + 38, f"précoce {b['taux_precoce']:.2f} sur {b['pas_precoces']} pas · "
                        f"tardif {b['taux_tardif']:.2f} · écart {b['ecart']:+.3f}", petit, ENCRE)
    ecrire(x1, ly + 54, f"p = {b['p_sous_un_taux_constant']:.4f} sous un taux constant : "
                        f"la marche ne se dégrade pas en avançant", petit, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, [(x0, y0, x0 + pw, y0 + ph), (x1, y0, x1 + pw2, y0 + ph2)]


def verifier() -> int:
    """Des contrôles hors ligne, sur un JSON fabriqué — et deux sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    faux = {
        "fragment": "X", "selecteur": "s",
        "lignes": [{"de": 1, "a": 2, "rayon_mm": 4.0,
                    "detail": [{"pas_parcourus": 20, "pas_confirmes": 3, "sortie": False,
                                "au_plafond": True, "longueur_um": 3000.0,
                                "etapes": [{"pas": k, "confirme": k % 2 == 0}
                                           for k in range(1, 21)]},
                               {"pas_parcourus": 20, "pas_confirmes": 1, "sortie": False,
                                "au_plafond": True, "longueur_um": 4000.0,
                                "etapes": [{"pas": k, "confirme": k % 3 == 0}
                                           for k in range(1, 21)]}]}],
        "resume": {"marches": 2, "plafond": 20, "marches_au_plafond": 2, "part_au_plafond": 1.0,
                   "sorties_du_volume": 0, "longueur_mediane_um": 3500.0,
                   "longueur_max_um": 4000.0, "pas_confirmes_max": 3,
                   "taux_de_confirmation_global": 0.5,
                   "quelque_chose_a_arrete_des_marches": False},
        "profondeur_de_la_confirmation": [{"pas": i, "marches": 2, "confirmes": 1, "taux": 0.5}
                                          for i in range(1, 21)],
        "le_taux_baisse_avec_la_profondeur": {"taux_precoce": 0.5, "taux_tardif": 0.5,
                                              "pas_precoces": 6, "pas_tardifs": 6, "ecart": 0.0,
                                              "p_sous_un_taux_constant": 1.0},
        "ce_qui_a_arrete_les_marches_de_107": {"plafond": 6, "longueur_mediane_um": 1250.0},
        "le_taux_depend_il_de_la_marche": {"decidable": True, "taux_min": 0.1, "taux_max": 0.9,
                                           "indice_de_dispersion": 9.9},
        "le_taux_suit_il_le_rayon": {"decidable": True, "rho_de_spearman": -0.72, "p": 1.6e-05},
    }
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        j = r / "m.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON complet est lu", lu["resume"]["marches"], 2)
        v("les marches sont aplaties depuis les bandes", len(marches(lu)), 2)
        p, poses, cadres = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.getdata())
        v("... et elle porte les deux plafonds",
          PLAFOND in pixels and ANCIEN in pixels)
        # ⚠ Une grille de marches doit montrer des cases PLEINES et des cases VIDES : si la
        # figure ne dessinait que le contour, « confirmé » et « pas confirmé » seraient le
        # même dessin, et le damier — qui est le fait — disparaîtrait.
        v("... des cases pleines et des cases vides",
          pixels.count(MARCHE) > 200 and pixels.count(TRAIT) > 200)
        # ⚠⚠ Les trois gardes de `figure_commune`, et elles ont chacune attrapé un défaut réel
        # de la première version : deux annotations posées SUR les barres, et une dernière
        # ligne écrite sous le bord de la toile.
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])

        # ⚠⚠ LA sonde qui compte : une course incomplète doit être REFUSÉE. Sans elle, une
        # figure tirée d'un run à moitié rendu a exactement l'air d'une figure d'un run entier,
        # et la part-au-plafond publiée serait celle de la moitié des marches.
        j.write_text(json.dumps(faux | {"course_incomplete": True}), encoding="utf-8")
        try:
            lire(j)
            v("sonde : une course incomplète est refusée", False)
        except ValueError:
            v("sonde : une course incomplète est refusée", True)

        # ⚠ Et un JSON sans agrégats : ce n'est pas une panne de la mesure, c'est un run qu'il
        # faut réagréger — donc le refus doit NOMMER la commande plutôt que de dessiner vide.
        j.write_text(json.dumps({k: v_ for k, v_ in faux.items() if k != "resume"}),
                     encoding="utf-8")
        try:
            lire(j)
            v("sonde : un JSON sans agrégats est refusé", False)
        except ValueError as e:
            v("sonde : un JSON sans agrégats est refusé", "reagreger" in str(e))

        # ⚠ Les deux constantes de repli doivent s'accorder avec ce que le JSON déclare, sinon
        # la figure dessinerait un plafond de 107 que la mesure ne connaît pas.
        v("le plafond de repli s'accorde au JSON",
          faux["ce_qui_a_arrete_les_marches_de_107"]["plafond"], PLAFOND_DE_107)
        v("la longueur de repli aussi",
          faux["ce_qui_a_arrete_les_marches_de_107"]["longueur_mediane_um"], LONGUEUR_DE_107_UM)

    print(f"{'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/jusquou_va_t_il_si_on_le_laisse.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/113_le_plafond_est_encore_la_mesure.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    out, _, _ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {out.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
