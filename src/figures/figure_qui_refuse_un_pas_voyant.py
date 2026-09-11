#!/usr/bin/env python3
"""Ce qui refuse un pas voyant : deux tiers du temps, c'est la fenêtre et pas la matière.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** `115` a mesuré que
là où le volume répond, le marcheur tient 0,7618 de ses pas. Le chiffre se lit comme « un pas sur
quatre échoue sur la matière ». Il ne le fait pas.

  ⭐⭐⭐ Le panneau de GAUCHE décompose les 91 refus par le terme du prédicat qui était faux.
  Le bloc de la **butée** est à part et il est le plus gros : ces pas-là n'ont rien contre eux
  sinon que l'optimum de longueur est tombé au bord de la fenêtre de candidats. C'est l'instrument
  qui ne sait pas répondre, pas la matière qui dit non.

  ⭐⭐⭐ Le panneau de DROITE montre pourquoi ce n'est pas une figure de style : les 31 longueurs
  candidates sont énumérées, et les pas en butée sont **exactement aux deux bouts**, jamais entre.
  La fenêtre va de 0,5 à 2 fois le pas nominal ; quarante-trois pas veulent en sortir par le bas,
  vingt par le haut.

⚠ Ce que la figure ne dit pas et que le texte doit dire : un pas en butée aurait pu échouer AUSSI
sur la matière avec une fenêtre plus large. Le taux que la matière seule autoriserait est une
borne supérieure.

  uv run python src/figures/figure_qui_refuse_un_pas_voyant.py \\
      --json docs/mesures/qui_refuse_un_pas_voyant.json \\
      --sortie docs/images/117_qui_refuse_un_pas_voyant.png
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
CONFIRME = (86, 104, 132)
BUTEE = (196, 140, 60)
MATIERE = (176, 62, 62)


def lire(chemin: Path) -> dict:
    """Le JSON de `qui_refuse_un_pas_voyant.py`.

    ⚠⚠ Refuse un JSON dont le prédicat ne s'est pas reconstruit. La décomposition porterait alors
    sur une conjonction qui n'est pas celle du marcheur, et le dessin serait juste au pixel près
    au sujet de la mauvaise chose.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    g = d.get("le_predicat_est_il_bien_reconstruit", {})
    if not g.get("le_predicat_est_celui_quon_croit"):
        raise ValueError(f"{chemin} : le prédicat ne s'est pas reconstruit, rien à décomposer")
    if not d.get("qui_refuse", {}).get("decidable"):
        raise ValueError(f"{chemin} ne porte aucune décomposition")
    if not d.get("les_bouts_de_la_fenetre", {}).get("par_candidat"):
        raise ValueError(f"{chemin} ne porte pas la distribution par candidat")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list]:
    """Dessine, et rend AUSSI les poses de texte et les cadres."""
    q = d["qui_refuse"]
    f = d["les_bouts_de_la_fenetre"]
    L, H = 1180, 470
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(28, 20, "Ce qui refuse un pas voyant", gros, ENCRE)
    ecrire(28, 46, f"{q['voyants']} pas voyants · {q['voyants_confirmes']} confirmés · "
                   f"{q['voyants_refuses']} refusés · source {d['source']}", petit, GRIS)

    # ── Panneau gauche : la décomposition des refus ──────────────────────────
    x0, y0 = 40, 112
    pw, ph = 470, 260
    ecrire(x0, y0 - 26, "les refus, par terme du prédicat qui était faux", moyen, ENCRE)
    # ⚠⚠ Les barres sont à l'ÉCHELLE du plus grand refus, jamais du nombre de pas voyants : à
    # l'échelle des 382, les quatre petites causes seraient des traits d'un pixel et la figure
    # dirait « il n'y a que la butée », ce qui est une conclusion et pas un dessin.
    lignes = list(q["combinaisons"].items())
    pic = max(n for _, n in lignes) if lignes else 1
    haut, jeu = 26, 12
    for i, (cle, n) in enumerate(lignes):
        y = y0 + i * (haut + jeu)
        larg = int((n / pic) * (pw - 210))
        # ⚠ Seule la butée SEULE est ambre. Une combinaison qui contient la butée porte aussi
        # un refus de la matière, donc élargir la fenêtre ne la récupérerait pas : la peindre en
        # ambre gonflerait le bloc « réparable » d'un pas qui ne l'est pas.
        couleur = BUTEE if cle == "butee" else MATIERE
        art.rectangle([x0 + 190, y, x0 + 190 + max(3, larg), y + haut - 6], fill=couleur)
        ecrire(x0, y + 3, f"{cle:<22}", petit, ENCRE)
        ecrire(x0 + 196 + max(3, larg), y + 3, str(n), petit, ENCRE)
    bas_g = y0 + len(lignes) * (haut + jeu) + 10
    ecrire(x0, bas_g, f"{q['butee_seule']} refusés par la SEULE butée, soit "
                      f"{q['part_des_refus_qui_sont_une_butee']:.0%} des refus", petit, BUTEE)
    ecrire(x0, bas_g + 20, f"la matière seule en refuse {q['refuses_par_la_matiere_seule']} "
                           f"sur {q['voyants']}", petit, MATIERE)
    ecrire(x0, bas_g + 40, f"donc le taux vaudrait AU PLUS "
                           f"{q['taux_au_plus_si_la_fenetre_ne_bornait_pas']}, jamais mesuré",
           petit, ENCRE)

    # ── Panneau droit : les 31 longueurs candidates ──────────────────────────
    x1, y1 = x0 + pw + 110, y0
    pw2, ph2 = L - x1 - 40, 260
    ecrire(x1, y1 - 26, "les 31 longueurs candidates, et qui les occupe", moyen, ENCRE)
    cand = f["par_candidat"]
    larg = max(4, int(pw2 / max(1, len(cand))) - 3)
    pic2 = max(c["libres"] + c["en_butee"] for c in cand)
    base = y1 + ph2 - 46
    for i, c in enumerate(cand):
        x = x1 + i * (larg + 3)
        n = c["libres"] + c["en_butee"]
        h = int((n / pic2) * (ph2 - 70))
        art.rectangle([x, base - h, x + larg, base],
                      fill=BUTEE if c["en_butee"] else CONFIRME)
    art.line([x1, base, x1 + pw2, base], fill=TRAIT, width=1)
    ecrire(x1, base + 8, f"{f['bout_court_um']:.1f}", petit, BUTEE)
    ecrire(x1 + pw2 - 42, base + 8, f"{f['bout_long_um']:.1f}", petit, BUTEE)
    ecrire(x1 + pw2 // 2 - 30, base + 8, "µm par pas", petit, GRIS)
    ecrire(x1, base + 34, f"fenêtre [{f['facteur_bas']} ; {f['facteur_haut']}] × "
                          f"{f['pas_nominal_um']:.0f} µm nominal", petit, ENCRE)
    ecrire(x1, base + 54, f"{f['au_bout_court']} au bout court · {f['au_bout_long']} au bout "
                          f"long · {f['entre_les_deux']} entre les deux", petit, BUTEE)

    prof = d["le_taux_baisse_t_il_chez_les_voyants"]
    t_, v_ = prof["sur_tous_les_pas"], prof["sur_les_voyants"]
    ecrire(28, H - 58, f"et la profondeur ne dégrade rien : chez les voyants le taux va de "
                       f"{t_['taux_precoce']} → {t_['taux_tardif']} sur tous les pas à "
                       f"{v_['taux_precoce']} → {v_['taux_tardif']} (p "
                       f"{v_['p_sous_un_taux_constant']})", moyen, ENCRE)
    ecrire(28, H - 32, "les deux taux montent parce qu'on retire des pas qui ne confirment "
                       "jamais ; le tardif monte le plus parce qu'ils sont en queue de marche",
           petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    return sortie, poses, [(x0, y0, x0 + pw, y0 + ph), (x1, y1, x1 + pw2, y1 + ph2)]


def verifier() -> int:
    """Des contrôles hors ligne, sur un JSON fabriqué — et trois sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    faux = {
        "source": "m.json",
        "le_predicat_est_il_bien_reconstruit": {
            "decidable": True, "pas": 560, "desaccords": 0,
            "le_predicat_est_celui_quon_croit": True},
        "qui_refuse": {
            "decidable": True, "voyants": 382, "voyants_confirmes": 291, "voyants_refuses": 91,
            "combinaisons": {"butee": 62, "accord": 17, "interstices": 8,
                             "interstices+accord": 3, "interstices+butee": 1},
            "marginales": {"interstices": 12, "accord": 20, "butee": 63},
            "butee_seule": 62, "refuses_par_la_matiere_seule": 28,
            "taux_au_plus_si_la_fenetre_ne_bornait_pas": 0.9122,
            "part_des_refus_qui_sont_une_butee": 0.6923},
        "les_bouts_de_la_fenetre": {
            "decidable": True, "pas_en_butee": 63, "bout_court_um": 86.5, "bout_long_um": 346.0,
            "au_bout_court": 43, "au_bout_long": 20, "entre_les_deux": 0,
            "pas_nominal_um": 173.0, "facteur_bas": 0.5, "facteur_haut": 2.0,
            "tous_aux_bouts": True,
            "par_candidat": ([{"um": 86.5, "libres": 0, "en_butee": 43}]
                             + [{"um": 95.2 + 8.7 * i, "libres": 10 + i % 7, "en_butee": 0}
                                for i in range(29)]
                             + [{"um": 346.0, "libres": 0, "en_butee": 20}])},
        "le_taux_baisse_t_il_chez_les_voyants": {
            "sur_tous_les_pas": {"decidable": True, "taux_precoce": 0.56, "taux_tardif": 0.5,
                                 "p_sous_un_taux_constant": 0.3253},
            "sur_les_voyants": {"decidable": True, "taux_precoce": 0.74, "taux_tardif": 0.8,
                                "p_sous_un_taux_constant": 0.3493},
            "le_lecteur_retrouve_113": True},
    }
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        j = r / "m.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", lu["qui_refuse"]["voyants"], 382)
        p, poses, cadres = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.getdata())
        # ⚠⚠ La butée et la matière doivent être DISTINCTES à l'écran : c'est toute la thèse de
        # la figure, et deux blocs de la même couleur la rendraient invisible.
        v("le bloc de la butée est dessiné", pixels.count(BUTEE) > 300)
        v("ceux de la matière aussi", pixels.count(MATIERE) > 300)
        v("les candidats libres ont leur propre couleur", pixels.count(CONFIRME) > 300)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f_ in poses if f_ is not None and y + f_.getbbox(t)[3] > im.size[1]], [])

        # ⚠⚠ LA sonde qui compte : un prédicat qui ne s'est pas reconstruit est REFUSÉ. Sans
        # elle, la figure décomposerait une conjonction qui n'est pas celle du marcheur.
        casse = json.loads(json.dumps(faux))
        casse["le_predicat_est_il_bien_reconstruit"]["le_predicat_est_celui_quon_croit"] = False
        j.write_text(json.dumps(casse), encoding="utf-8")
        try:
            lire(j)
            v("sonde : un prédicat irréconciliable est refusé", False)
        except ValueError:
            v("sonde : un prédicat irréconciliable est refusé", True)

        sans = json.loads(json.dumps(faux))
        sans["les_bouts_de_la_fenetre"]["par_candidat"] = []
        j.write_text(json.dumps(sans), encoding="utf-8")
        try:
            lire(j)
            v("sonde : un JSON sans distribution est refusé", False)
        except ValueError:
            v("sonde : un JSON sans distribution est refusé", True)

        muet = json.loads(json.dumps(faux))
        muet["qui_refuse"] = {"decidable": False, "pourquoi": "rien"}
        j.write_text(json.dumps(muet), encoding="utf-8")
        try:
            lire(j)
            v("sonde : un JSON sans décomposition est refusé", False)
        except ValueError:
            v("sonde : un JSON sans décomposition est refusé", True)

        # ⚠ Une décomposition à une seule cause ne doit pas écraser la mise en page.
        seule = json.loads(json.dumps(faux))
        seule["qui_refuse"]["combinaisons"] = {"butee": 91}
        j.write_text(json.dumps(seule), encoding="utf-8")
        _, poses2, _ = dessiner(lire(j), r / "g.png")
        im2 = Image.open(r / "g.png").convert("RGB")
        v("une cause unique ne fait rien déborder", textes_debordants(poses2, im2.size[0]), [])
        v("... ni se recouvrir", textes_qui_se_recouvrent(poses2), [])

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "qui_refuse_un_pas_voyant.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "117_qui_refuse_un_pas_voyant.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
