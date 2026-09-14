#!/usr/bin/env python3
"""Deux marches jumelles, parties de la même feuille, y sont-elles encore à l'arrivée ?

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** À gauche, la dérive
entre deux jumelles en fonction de leur écart latéral, sur trois matières : une pile **périodique**
(qui ne porte aucune identité de feuille, donc la réponse connue est « elles ne se séparent pas »),
une pile dont **chaque feuille** a son propre froissement (qui en porte une), et le **rouleau**. La
barre pleine est la dérive VRAIE, lue dans la phase analytique ; la barre creuse est ce que le
compteur du marcheur en voit. Le rouleau n'a pas de vérité, donc il n'a qu'une barre creuse — et
c'est l'écart entre les deux piles qui lui donne une échelle. À droite, la dérive lue contre la
dérive vraie, paire par paire : la diagonale est le compteur parfait.

  uv run python src/figures/figure_deux_marches_jumelles.py \\
      --json docs/mesures/deux_marches_jumelles.json \\
      --sortie docs/images/138_deux_jumelles_sur_la_meme_feuille.png
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
BANDE = (236, 234, 228)
PERIODIQUE = (86, 104, 132)
PAR_FEUILLE = (60, 110, 90)
ROULEAU = (176, 92, 42)
CUBE = (196, 140, 60)

MATIERES = (("la_pile_periodique", "pile périodique", PERIODIQUE),
            ("la_pile_par_feuille", "pile par feuille", PAR_FEUILLE),
            ("le_rouleau", "le rouleau", ROULEAU))


def lire(chemin: Path) -> dict:
    """Le JSON de `deux_marches_jumelles_lisent_elles_la_meme_feuille.py`.

    ⚠⚠ Refuse un JSON dont les DEUX piles ne sont pas décidables : elles sont l'échelle sur
    laquelle le rouleau se lit, et une échelle à un seul bout n'en est pas une.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    for cle in ("la_pile_periodique", "la_pile_par_feuille"):
        bloc = d.get(cle) or {}
        if not bloc.get("resume", {}).get("decidable"):
            raise ValueError(f"{chemin} : la pile {cle} n'a rendu aucune paire")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1180, 740
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    j = d.get("juger", {})
    total = sum((d.get(c) or {}).get("resume", {}).get("paires", 0) for c, _, _ in MATIERES)
    ecrire(28, 20, "Deux jumelles parties de la même feuille, et ce qui les sépare", gros, ENCRE)
    ecrire(28, 46, f"{total} paires · écart latéral pris DANS le plan de la feuille · "
                   f"cube de lecture {d['largeur_du_cube_vx']} voxels "
                   f"({d['largeur_du_cube_vx'] * 2.4:.1f} µm) · {d['pas_max']} pas par marche",
           petit, GRIS)

    # ── Gauche : la dérive par écart latéral, sur les trois matières ──────────
    x0, y0, pw, ph = 60, 150, 540, 380
    ecrire(x0, y0 - 26, "dérive médiane, en feuilles, par écart latéral", moyen, ENCRE)
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    ecarts = [float(e) for e in d["ecarts_vx"]]
    # ⚠ L'echelle est celle des barres REELLEMENT dessinees — les medianes. La premiere version la
    # prenait sur les p90, qui ne sont pas traces : les barres tenaient alors dans le tiers bas du
    # panneau et l'ecart entre les trois matieres, qui est tout l'argument, devenait illisible.
    hauts = [0.0]
    for cle, _, _ in MATIERES:
        s = (d.get(cle) or {}).get("resume", {})
        for b in s.get("par_ecart", []):
            hauts.append(b.get("derive_lue_mediane", 0.0))
            hauts.append(b.get("derive_vraie_mediane", 0.0) or 0.0)
    haut = max(hauts) * 1.12 or 1.0

    def by(v):
        return y0 + ph - 30 - (v / haut) * (ph - 60)

    for k in range(0, int(haut) + 1):
        art.line([x0 + 4, by(k), x0 + pw - 4, by(k)], fill=TRAIT, width=1)
        ecrire(x0 - 20, int(by(k)) - 6, f"{k}", petit, GRIS)
    groupe = (pw - 30) / max(1, len(ecarts))
    for i, ec in enumerate(ecarts):
        gx = x0 + 15 + i * groupe
        dedans = ec < d["largeur_du_cube_vx"]
        ecrire(int(gx + groupe / 2) - 26, y0 + ph - 22,
               f"{ec:.0f} vx", petit, ENCRE if dedans else CUBE)
        # ⚠ Un trait AMBRE sous les ecarts qui depassent le cube de lecture : c'est la seule
        # frontiere que la mesure ait, et elle vient de l'instrument, pas de la matiere. Une
        # etiquette coloree seule ne se voit pas — et ne se compte pas non plus.
        if not dedans:
            art.rectangle([gx + 6, y0 + ph - 8, gx + groupe - 10, y0 + ph - 5], fill=CUBE)
        larg = groupe / 8.0
        for m, (cle, _, coul) in enumerate(MATIERES):
            s = (d.get(cle) or {}).get("resume", {})
            b = next((z for z in s.get("par_ecart", []) if float(z["ecart_vx"]) == ec), None)
            if b is None:
                continue
            bx = gx + 6 + m * 2.3 * larg
            # ⚠ La barre PLEINE est la vérité, la CREUSE ce que le compteur en voit. Une matière
            # sans vérité — le rouleau — n'a donc pas de barre pleine, et son absence est le fait.
            if b.get("derive_vraie_mediane") is not None:
                art.rectangle([bx, by(b["derive_vraie_mediane"]), bx + larg, by(0.0)], fill=coul)
                points.append((bx + larg, by(b["derive_vraie_mediane"])))
            art.rectangle([bx + larg + 2, by(b["derive_lue_mediane"]), bx + 2 * larg + 2, by(0.0)],
                          outline=coul, width=2)
            points.append((bx + 2 * larg + 2, by(b["derive_lue_mediane"])))
    yl = y0 + 6
    for cle, nom, coul in MATIERES:
        s = (d.get(cle) or {}).get("resume", {})
        if not s.get("decidable"):
            continue
        art.rectangle([x0 + 12, yl + 3, x0 + 22, yl + 12], fill=coul)
        ecrire(x0 + 28, yl, f"{nom} · {s['paires']} paires", petit, coul)
        yl += 16
    # ⚠ La legende passe SOUS la derniere ligne de grille : posee au-dessus, elle croisait le
    # trait du haut et se lisait mal sur les vraies donnees.
    ecrire(x0 + 12, yl + 4, "plein : dérive VRAIE (phase analytique) · creux : dérive LUE (compteur)",
           petit, GRIS)
    ecrire(x0, y0 + ph + 6, f"écart latéral en voxels · ambre : au-delà du cube de lecture "
                            f"({d['largeur_du_cube_vx']} vx), aucun voxel partagé", petit, GRIS)

    # ── Droite : la dérive lue contre la dérive vraie ─────────────────────────
    x1 = x0 + pw + 70
    pw2 = L - x1 - 40
    ecrire(x1, y0 - 26, "ce que le compteur voit contre ce que la matière impose", moyen, ENCRE)
    art.rectangle([x1, y0, x1 + pw2, y0 + ph], outline=TRAIT, width=1)
    paires = [(coul, x) for cle, _, coul in MATIERES
              for x in (d.get(cle) or {}).get("paires", []) if "derive_vraie" in x]
    m_ = max([abs(x["derive_vraie"]) for _, x in paires]
             + [abs(x["derive_lue"]) for _, x in paires] + [1.0]) * 1.08

    def sx(v):
        return x1 + 34 + (v / m_) * (pw2 - 52)

    def sy(v):
        return y0 + ph - 34 - (v / m_) * (ph - 58)

    art.line([sx(0.0), sy(0.0), sx(m_), sy(m_)], fill=GRIS, width=1)
    for k in range(0, int(m_) + 1):
        ecrire(int(sx(k)) - 4, y0 + ph - 26, f"{k}", petit, GRIS)
        ecrire(x1 + 12, int(sy(k)) - 6, f"{k}", petit, GRIS)
    for coul, x in paires:
        a, b = sx(abs(x["derive_vraie"])), sy(abs(x["derive_lue"]))
        points.append((a, b))
        art.ellipse([a - 4, b - 4, a + 4, b + 4], fill=coul)
    ecrire(x1 + 34, y0 + 8, "la diagonale : un compteur qui voit tout", petit, GRIS)
    ecrire(x1, y0 + ph + 6, "dérive VRAIE (feuilles) en abscisse, dérive LUE en ordonnée",
           petit, GRIS)
    yc = y0 + 26
    for cle, nom in (("sur_la_pile_periodique", "périodique"),
                     ("sur_la_pile_par_feuille", "par feuille")):
        c = (d.get("le_compteur_voit_il_la_separation") or {}).get(cle, {})
        if c.get("decidable") and not c.get("aucune_variation"):
            ecrire(x1 + 34, yc, f"{nom} : rho {c['rho_de_spearman']:+}, p {c['p_du_rang']}",
                   petit, PERIODIQUE if "pério" in nom else PAR_FEUILLE)
            yc += 16

    # ── La bande de conclusion ────────────────────────────────────────────────
    yb = y0 + ph + 42
    art.rectangle([x0, yb, L - 40, H - 20], fill=BANDE, outline=TRAIT, width=1)
    lignes = []
    if j.get("decidable"):
        lignes.append((f"★ Une pile PÉRIODIQUE ne sépare pas ses jumelles : dérive vraie "
                       f"{j.get('derive_vraie_periodique')} feuille. Une pile dont chaque feuille "
                       f"a son froissement les sépare de {j.get('derive_vraie_par_feuille')}, "
                       f"soit {j.get('combien_de_fois_plus')} fois plus.", ENCRE))
        if j.get("derive_lue_du_rouleau") is not None:
            parts = []
            for cle, nom, _ in MATIERES:
                r_ = (d.get(cle) or {}).get("resume", {})
                if r_.get("part_des_paires_au_dela_dune_feuille") is not None:
                    parts.append(f"{nom} {r_['part_des_paires_au_dela_dune_feuille']:.0%}")
            rangs = [c for c in (d.get("les_trois_matieres_sont_elles_distinctes") or {})
                     .get("comparaisons", []) if c["plus_grand"] == "rouleau"]
            dits = " et ".join(f"p {c['p_de_rang']}" for c in rangs)
            lignes.append((f"★ Le rouleau lit {j['derive_lue_du_rouleau']} feuille de dérive. "
                           f"Part des paires qui dépassent UNE feuille : {' · '.join(parts)}"
                           + (f" — son lot se sépare des deux fixtures ({dits})." if dits
                              else "."), ENCRE))
        o = (d.get("dou_vient_la_derive") or {}).get("sur_le_rouleau", {})
        if o.get("decidable") and "derive_a_lecart_le_plus_petit" in o:
            lignes.append((f"★ Sur le rouleau la dérive ne croît pas avec l'écart "
                           f"(rho {o['rho_ecart_lateral']:+}, p {o['p_ecart_lateral']}) : à "
                           f"{o['ecart_le_plus_petit_vx']:.0f} voxel"
                           f"{'s' if o['ecart_le_plus_petit_vx'] > 1 else ''} d'écart, là où les "
                           f"deux cubes partagent presque tous leurs voxels, elle vaut déjà "
                           f"{o['derive_a_lecart_le_plus_petit']} feuille.", ENCRE))
        if j.get("plancher_du_bruit_p90_periodique") is not None:
            lignes.append((f"✗ Le plancher n'est pas zéro : sur la pile périodique, une paire sur "
                           f"dix se sépare quand même de {j['plancher_du_bruit_p90_periodique']} "
                           f"feuille, par le seul bruit. Une paire isolée ne décide de rien.",
                           ROULEAU))
    for i, (texte, coul) in enumerate(lignes):
        ecrire(x0 + 14, yb + 12 + i * 22, texte, petit, coul)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    # ⚠ Trois cadres : un par panneau, plus un pour la bande de conclusion — `textes_hors_cadre`
    # range un texte sous le cadre qui contient son origine.
    cadres = [(x0 - 30, y0 - 30, x0 + pw + 10, yb - 2),
              (x1 - 30, y0 - 30, L - 20, yb - 2),
              (x0, yb, L - 40, H)]
    return sortie, poses, cadres, points


def verifier() -> int:
    """Des contrôles hors ligne, sur un JSON fabriqué — et des sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    ecarts = [4, 16, 41, 82]

    def paire(ec, lu, vrai=None):
        p = {"ecart_vx": float(ec), "ecart_um": round(ec * 2.4, 1), "derive_lue": lu,
             "derive_lue_max": abs(lu), "pas_communs": 25, "feuilles_a": 24.0,
             "feuilles_b": 24.0 - lu, "pas_a": 25, "pas_b": 25}
        if vrai is not None:
            p.update({"derive_vraie": vrai, "traversee_vraie_a": 24.0, "traversee_vraie_b": 24.0,
                      "decalage_de_phase_au_depart": 0.01, "erreur_de_comptage_a": 0.3,
                      "erreur_de_comptage_b": -0.2})
        return p

    def bloc(paires, avec_vrai):
        par = []
        for ec in ecarts:
            lot = [x for x in paires if x["ecart_vx"] == ec]
            b = {"ecart_vx": float(ec), "ecart_um": round(ec * 2.4, 1), "paires": len(lot),
                 "dans_le_cube_de_lecture": ec < 41,
                 "derive_lue_mediane": round(sum(abs(x["derive_lue"]) for x in lot) / len(lot), 3),
                 "derive_lue_p90": 1.8}
            if avec_vrai:
                b.update({"derive_vraie_mediane": round(
                    sum(abs(x["derive_vraie"]) for x in lot) / len(lot), 3),
                    "derive_vraie_p90": 2.1, "decalage_au_depart_median": 0.01})
            par.append(b)
        r = {"decidable": True, "paires": len(paires), "par_ecart": par,
             "derive_lue_mediane": 0.3, "derive_lue_p90": 1.9}
        if avec_vrai:
            r.update({"derive_vraie_mediane": 0.5, "derive_vraie_p90": 2.2,
                      "erreur_de_comptage_mediane": 0.4, "traversee_mediane": 24.0})
        return {"paires": paires, "resume": r}

    per = bloc([paire(e, 0.1 + 0.05 * i, 0.03 + 0.02 * i)
                for e in ecarts for i in range(5)], True)
    pf = bloc([paire(e, 0.5 + 0.2 * i, 0.9 + 0.3 * i) for e in ecarts for i in range(5)], True)
    rou = bloc([paire(e, 0.4 + 0.1 * i) for e in ecarts for i in range(5)], False)
    compteur = {"decidable": True, "paires": 20, "aucune_variation": False,
                "rho_de_spearman": 0.6378, "p_du_rang": 9e-05, "derive_vraie_mediane": 0.03,
                "derive_lue_mediane": 0.11, "ecart_median": 0.08, "p_apparie": 0.001,
                "le_compteur_voit_le_rang": True, "le_compteur_voit_le_niveau": False}
    faux = {"ecarts_vx": ecarts, "largeur_du_cube_vx": 41, "pas_max": 25, "bruit": 8.0,
            "la_pile_periodique": per, "la_pile_par_feuille": pf, "le_rouleau": rou,
            "le_compteur_voit_il_la_separation": {"sur_la_pile_periodique": compteur,
                                                  "sur_la_pile_par_feuille": compteur},
            "dou_vient_la_derive": {"sur_le_rouleau": {
                "decidable": True, "paires": 40, "rho_ecart_lateral": -0.1375,
                "p_ecart_lateral": 0.3974, "la_derive_croit_avec_lecart": False,
                "ecart_le_plus_petit_vx": 1.0, "derive_a_lecart_le_plus_petit": 2.61}},
            "juger": {"decidable": True, "derive_vraie_periodique": 0.027,
                      "derive_vraie_par_feuille": 0.977, "derive_lue_periodique": 0.11,
                      "derive_lue_par_feuille": 0.615, "plancher_du_bruit_p90_periodique": 1.873,
                      "traversee_mediane_periodique": 24.0, "traversee_mediane_par_feuille": 24.0,
                      "la_pile_periodique_ne_separe_pas": True, "la_pile_par_feuille_separe": True,
                      "combien_de_fois_plus": 36.2, "derive_lue_du_rouleau": 0.4,
                      "derive_lue_du_rouleau_p90": 1.5, "ou_tombe_le_rouleau_sur_lechelle": 0.574}}

    with tempfile.TemporaryDirectory() as dtmp:
        r = Path(dtmp)
        j = r / "c.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", lu["largeur_du_cube_vx"], 41)
        p, poses, cadres, points = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
            else list(im.getdata())
        v("les trois matières ont trois couleurs",
          pixels.count(PERIODIQUE) > 200 and pixels.count(PAR_FEUILLE) > 200
          and pixels.count(ROULEAU) > 200)
        v("les écarts hors du cube sont marqués", pixels.count(CUBE) > 40)
        v("la bande de conclusion est peinte", pixels.count(BANDE) > 3000)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])
        gx0, gy0, gx1, gy1 = cadres[0]
        v("tous les points tiennent dans un cadre",
          [1 for x, y in points if not (gx0 <= x <= cadres[1][2] and gy0 <= y <= gy1)], [])
        v("les quatre lignes de conclusion sont écrites",
          sum(1 for _, _, t, _ in poses if t.startswith("★") or t.startswith("✗")), 4)
        # sondes
        for nom_, bris in (
                ("porteur d'un message", lambda x: x.update(message="volume injoignable")),
                ("sans pile périodique décidable",
                 lambda x: x["la_pile_periodique"]["resume"].update(decidable=False)),
                ("sans pile par feuille décidable",
                 lambda x: x["la_pile_par_feuille"]["resume"].update(decidable=False))):
            c = json.loads(json.dumps(faux))
            bris(c)
            j.write_text(json.dumps(c), encoding="utf-8")
            try:
                lire(j)
                v(f"sonde : un JSON {nom_} est refusé", False)
            except ValueError:
                v(f"sonde : un JSON {nom_} est refusé", True)
        # ⚠ Le rouleau ABSENT est legitime : les deux piles suffisent a dessiner l'echelle.
        c = json.loads(json.dumps(faux))
        c.pop("le_rouleau")
        c["juger"].pop("derive_lue_du_rouleau")
        # ⚠ Sans rouleau, le diagnostic « d'ou vient la derive sur le rouleau » n'a plus de sujet :
        # le laisser ferait ecrire une conclusion sur une matiere absente de l'image.
        c["dou_vient_la_derive"].pop("sur_le_rouleau")
        j.write_text(json.dumps(c), encoding="utf-8")
        p2, poses2, _, _ = dessiner(lire(j), r / "h.png")
        v("un JSON sans rouleau se dessine quand même", p2.is_file())
        v("... et sa conclusion perd les DEUX lignes du rouleau",
          sum(1 for _, _, t, _ in poses2 if t.startswith("★") or t.startswith("✗")), 2)
        j.write_text(json.dumps(faux), encoding="utf-8")
        dessiner(lire(j), r / "g.png")
        v("deux rendus du même JSON sont identiques au bit",
          (r / "f.png").read_bytes() == (r / "g.png").read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "deux_marches_jumelles.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "138_deux_jumelles_sur_la_meme_feuille.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
