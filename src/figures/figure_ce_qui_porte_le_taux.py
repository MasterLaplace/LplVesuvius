#!/usr/bin/env python3
"""Le rayon ne portait pas le taux : il portait la probabilité que le volume réponde.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** `113` a publié un
rho de −0,7188 entre le rayon et le taux de confirmation, et il se lit naturellement comme « la
matière devient plus dure vers l'extérieur ». Elle ne l'est pas. Un tiers des pas ne lit **rien**,
ces pas-là sont concentrés au grand rayon, et **aucun** ne confirme. Une fois les marches aveugles
écartées, le nuage est **plat**.

  ⭐ Le panneau de GAUCHE met les deux nuages l'un sur l'autre : les marches qui ont lu quelque
  chose, et celles qui n'ont rien lu. La pente n'existe que parce que les secondes sont à droite.

  ⭐⭐ Le panneau de DROITE est le défaut, et c'est une barre contre une barre : les 178 pas
  aveugles portent tous le drapeau `oriente`. Le marcheur croit savoir où il va exactement là où
  il ne lit rien.

⚠ Les deux panneaux ne se moyennent pas l'un dans l'autre, et c'est voulu : « le rayon n'est pas
la cause » est un résultat sur le rouleau, « le vide passe pour orienté » est un défaut de
l'instrument. Les mettre sur un seul axe ferait lire le second comme une explication du premier,
alors qu'il en est la condition.

  uv run python src/figures/figure_ce_qui_porte_le_taux.py \\
      --json docs/mesures/ce_qui_porte_le_taux.json \\
      --sortie docs/images/115_le_rayon_ne_portait_pas_le_taux.png
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
VOYANTE = (86, 104, 132)
AVEUGLE = (176, 62, 62)
ACCENT = (196, 140, 60)


def lire(chemin: Path) -> dict:
    """Le JSON de `ce_qui_porte_le_taux.py`.

    ⚠ Refuse un fichier sans marches ou sans les deux verdicts plutôt que de dessiner un cadre
    vide : une figure tirée d'une mesure incomplète a exactement l'air d'une figure complète.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("par_marche", "le_vide_est_il_declare_oriente",
                "le_rayon_survit_il_aux_marches_voyantes"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : « {cle} » absent — relancer la mesure")
    if not d["le_vide_est_il_declare_oriente"].get("decidable"):
        raise ValueError(f"{chemin} : le verdict du vide est indécidable")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list]:
    """Dessine, et rend AUSSI les poses de texte et les cadres, pour que les gardes relisent."""
    L, H = 1180, 560
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    pm = d["par_marche"]
    o = d["le_vide_est_il_declare_oriente"]
    v = d["le_rayon_survit_il_aux_marches_voyantes"]

    ecrire(28, 20, "Le rayon ne portait pas le taux", gros, ENCRE)
    ecrire(28, 46, f"{d['marches']} marches · {d['pas']} pas · source {d['source']}", petit, GRIS)

    # ── Gauche : le taux contre le rayon, voyantes et aveugles séparées ───────
    x0, y0, pw, ph = 76, 112, 480, 330
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT)
    ecrire(x0, y0 - 26, "le taux contre le rayon en mm  (rouge = la marche n'a rien lu)",
           moyen, ENCRE)

    rmin = min(m["rayon_mm"] for m in pm)
    rmax = max(m["rayon_mm"] for m in pm)
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = y0 + ph - int(ph * t)
        art.line([x0, y, x0 + pw, y], fill=TRAIT)
        ecrire(x0 - 34, y - 7, f"{t:.2f}", petit, GRIS)
    for r in (5, 10, 15, 20):
        x = x0 + int(pw * (r - rmin) / max(1e-9, rmax - rmin))
        ecrire(x - 6, y0 + ph + 6, f"{r}", petit, GRIS)

    # ⚠ La coupure de 17 mm est LUE dans la mesure, jamais posée ici : c'est le rayon de la
    # première marche qui porte un pas aveugle. Une verticale choisie dans la figure serait un
    # seuil que personne n'aurait mesuré.
    xc = x0 + int(pw * (v["coupure_mm"] - rmin) / max(1e-9, rmax - rmin))
    art.line([xc, y0, xc, y0 + ph], fill=ACCENT, width=2)

    for m in pm:
        x = x0 + int(pw * (m["rayon_mm"] - rmin) / max(1e-9, rmax - rmin))
        y = y0 + ph - int(ph * m["taux"])
        aveugle = m["pas_aveugles"] > 0
        c = AVEUGLE if aveugle else VOYANTE
        art.ellipse([x - 5, y - 5, x + 5, y + 5], fill=c if not aveugle else None, outline=c,
                    width=2)

    ly = y0 + ph + 30
    art.ellipse([x0, ly + 2, x0 + 10, ly + 12], fill=VOYANTE)
    ecrire(x0 + 18, ly, f"{v['marches_voyantes']} marches qui ont lu — rho "
                        f"{v['rho_sur_les_voyantes']:+.4f}, p {v['p_sur_les_voyantes']:.3f}",
           petit, VOYANTE)
    art.ellipse([x0, ly + 22, x0 + 10, ly + 32], outline=AVEUGLE, width=2)
    ecrire(x0 + 18, ly + 20, f"{v['marches'] - v['marches_voyantes']} marches avec au moins un pas "
                             f"aveugle · rho sur toutes {v['rho_sur_toutes']:+.4f}", petit, AVEUGLE)
    ecrire(x0, ly + 40, f"médiane des voyantes : {v['taux_median_voyantes_interieur']:.3f} sous "
                        f"{v['coupure_mm']:.0f} mm contre "
                        f"{v['taux_median_voyantes_exterieur']:.3f} au-dessus "
                        f"(p {v['p_interieur_contre_exterieur']:.4f})", petit, ENCRE)

    # ── Droite : le défaut du drapeau ────────────────────────────────────────
    x1, pw2 = 700, 420
    art.rectangle([x1, y0, x1 + pw2, y0 + ph], outline=TRAIT)
    ecrire(x1, y0 - 26, "ce que le marcheur croit savoir", moyen, ENCRE)

    total = o["pas"]
    aveu, voyants = o["pas_aveugles"], total - o["pas_aveugles"]
    hb, ecart = 54, 26
    yb = y0 + 40
    for titre, n, conf, couleur in (
            (f"{voyants} pas qui ont lu", voyants, o["voyants_confirmes"], VOYANTE),
            (f"{aveu} pas AVEUGLES", aveu, o["aveugles_confirmes"], AVEUGLE)):
        larg = int(pw2 * 0.86 * n / max(1, total))
        art.rectangle([x1 + 20, yb, x1 + 20 + larg, yb + hb], outline=couleur, width=2)
        lc = int(larg * conf / max(1, n))
        art.rectangle([x1 + 20, yb, x1 + 20 + lc, yb + hb], fill=couleur)
        ecrire(x1 + 20, yb - 18, titre, petit, couleur)
        ecrire(x1 + 26, yb + hb + 6, f"{conf} confirmés sur {n}", petit, ENCRE)
        yb += hb + ecart + 22

    yb += 10
    art.rectangle([x1 + 20, yb, x1 + 20 + int(pw2 * 0.86 * aveu / max(1, total)), yb + hb],
                  fill=ACCENT)
    ecrire(x1 + 20, yb - 18, "et pourtant déclarés « orientés »", petit, ACCENT)
    ecrire(x1 + 26, yb + hb + 6,
           f"{o['aveugles_declares_orientes']} sur {aveu} — le désaccord de deux moitiés de rien "
           f"vaut 0,00°", petit, ENCRE)

    ecrire(x1, ly, f"taux sur les pas qui ont lu : {o['taux_voyant']:.4f}", petit, VOYANTE)
    ecrire(x1, ly + 20, f"{d['marches_aveugles_des_le_depart']} marches sont aveugles dès leur "
                        f"PREMIER pas", petit, AVEUGLE)
    ecrire(x1, ly + 40, "un vide et un accord parfait rendent le même nombre", petit, ACCENT)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, [(x0, y0, x0 + pw, y0 + ph), (x1, y0, x1 + pw2, y0 + ph)]


def verifier() -> int:
    """Contrôles hors ligne sur un JSON fabriqué, et les sondes qui les rendent capables d'échouer."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    faux = {
        "source": "x.json", "marches": 4, "pas": 80, "marches_aveugles_des_le_depart": 1,
        "par_marche": [{"rayon_mm": 5.0, "taux": 0.8, "pas_aveugles": 0},
                       {"rayon_mm": 12.0, "taux": 0.75, "pas_aveugles": 0},
                       {"rayon_mm": 20.0, "taux": 0.7, "pas_aveugles": 0},
                       {"rayon_mm": 23.0, "taux": 0.0, "pas_aveugles": 20}],
        "le_vide_est_il_declare_oriente": {
            "decidable": True, "pas": 80, "pas_aveugles": 20, "part_aveugle": 0.25,
            "aveugles_confirmes": 0, "voyants_confirmes": 45, "taux_voyant": 0.75,
            "aveugles_declares_orientes": 20, "le_vide_passe_pour_oriente": True},
        "le_rayon_survit_il_aux_marches_voyantes": {
            "decidable": True, "marches": 4, "marches_voyantes": 3,
            "rho_sur_toutes": -0.9, "p_sur_toutes": 0.01,
            "rho_sur_les_voyantes": -0.2, "p_sur_les_voyantes": 0.6,
            "taux_median_voyantes_interieur": 0.8, "taux_median_voyantes_exterieur": 0.7,
            "p_interieur_contre_exterieur": 0.4, "coupure_mm": 17.0,
            "le_rayon_survit_aux_voyantes": False},
    }
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        j = r / "m.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON complet est lu", lu["marches"], 4)
        p, poses, cadres = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... à la taille annoncée", im.size, (1180, 560))
        pixels = list(im.getdata())
        v("... et elle porte les trois couleurs qui portent le sens",
          VOYANTE in pixels and AVEUGLE in pixels and ACCENT in pixels)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])

        # ⚠⚠ Les deux sondes : une mesure incomplète doit être REFUSÉE, sinon la figure a l'air
        # complète en ne montrant qu'une partie des marches.
        for cle in ("par_marche", "le_rayon_survit_il_aux_marches_voyantes"):
            j.write_text(json.dumps({k: x for k, x in faux.items() if k != cle}), encoding="utf-8")
            try:
                lire(j)
                v(f"sonde : un JSON sans « {cle} » est refusé", False)
            except ValueError:
                v(f"sonde : un JSON sans « {cle} » est refusé", True)
        j.write_text(json.dumps(faux | {"le_vide_est_il_declare_oriente": {"decidable": False}}),
                     encoding="utf-8")
        try:
            lire(j)
            v("sonde : un verdict indécidable est refusé", False)
        except ValueError:
            v("sonde : un verdict indécidable est refusé", True)

        # ⚠⚠ Et le module doit pouvoir écrire HORS du dépôt : `fraicheur_des_figures.py` régénère
        # dans un dossier temporaire, et un module qui lève là devient « impossible » à vérifier
        # sans que rien ne rougisse.
        import subprocess
        j.write_text(json.dumps(faux), encoding="utf-8")
        rc = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                             "--json", str(j), "--sortie", str(r / "dehors.png")],
                            capture_output=True, text=True)
        v("écrire hors du dépôt ne lève pas", rc.returncode, 0)
        v("... et l'image y est bien écrite", (r / "dehors.png").is_file(), True)

    print(f"{'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/ce_qui_porte_le_taux.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/115_le_rayon_ne_portait_pas_le_taux.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    out, _, _ = dessiner(lire(a.json), a.sortie)
    try:
        dit = out.relative_to(RACINE)
    except ValueError:
        dit = out
    print(f"écrit : {dit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
