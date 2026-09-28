"""La spire produite et le texte du segment là où il repasse : l'étalon, la bande vue, et les blocs choisis sans l'encre.

⚠⚠ **Ce que cette figure doit rendre évident.** Que notre lecture retrouve la carte publiée sur la référence ; que, sur la spire
produite, elle dessine les lettres que la carte publiée porte au vis-à-vis là où le segment repasse ; et que ses deux témoins, le
texte de la spire de départ et le vis-à-vis décalé, restent en dessous.

  uv run python src/figures/figure_le_tour_produit_porte_t_il_le_texte_du_segment.py \\
      --sortie docs/images/296_le_tour_produit_porte_t_il_le_texte_du_segment.png

⚠ Les images viennent de `data/encre_du_tour_voisin/`, que `--encre` et `--json` écrivent ; les barres, de la mesure.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "le_tour_produit_porte_t_il_le_texte_du_segment.json"
LES_DONNEES = RACINE / "data" / "encre_du_tour_voisin"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
BLEU = (58, 92, 150)
AMBRE = (206, 160, 60)
L_, H_ = 1360, 900
LES_BARRES = (("au_vis_a_vis", "au vis-à-vis", BON), ("temoin_sous_le_bloc", "texte de la spire de départ", GRIS),
              ("temoin_decale", "vis-à-vis décalé de 1,2 mm", BLEU))


def _fr(x, n: int = 2) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    b = d["la_partie_b"]["reunie"]["a_moins_dun_demi_feuillet"]
    oui = d["le_verdict"]["lissue"].startswith("la spire produite porte")
    return (f"{'OUI' if oui else 'NON'} : LÀ OÙ LE SEGMENT REPASSE, LA SPIRE PRODUITE PORTE SON TEXTE À {_fr(b['au_vis_a_vis'])}, "
            f"CONTRE {_fr(b['temoin_sous_le_bloc'])} ET {_fr(b['temoin_decale'])} POUR SES TÉMOINS")


def _en_gris(a: np.ndarray, echelle: float | None = None) -> Image.Image:
    a = np.nan_to_num(np.asarray(a, dtype=float), nan=0.0)
    haut = echelle if echelle is not None else (float(np.percentile(a, 99.5)) or 1.0)
    return Image.fromarray((np.clip(a / haut, 0, 1) * 255).astype(np.uint8))


def les_images(donnees: Path = LES_DONNEES) -> dict:
    a = np.load(donnees / "partie_a_pour_la_figure.npz")
    e = np.load(donnees / "etalon_pour_la_figure.npz")
    return {"etalon_lu": e["lue"], "etalon_publie": e["publiee"], "a_lue": a["lue"], "a_vis": a["au_vis_a_vis"],
            "a_proche": a["proche"]}


def dessiner(d: dict, sortie: Path, images: dict):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"barres": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    def coller(im: Image.Image, x, y, w, h):
        img.paste(im.convert("RGB").resize((w, h), Image.LANCZOS), (x, y))
        points.extend([(x, y), (x + w, y + h)])

    et, a = d["letalonnage"], d["la_partie_a"]
    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"PHercParis4 · 20230702185753 · modèle {d['le_modele']['nom']} · couches "
                   f"{d['le_modele']['les_couches'][0]} à {d['le_modele']['les_couches'][1] - 1} · carte publiée réduite "
                   f"{d['les_constantes']['la_reduction']} fois · demi-feuillet {_fr(d['les_constantes']['le_demi_feuillet_voxels'], 0)}"
                   " voxels", petit, GRIS)

    panneau(50, 80, 420, 400, "L'ÉTALON : LA RÉFÉRENCE, LUE PAR NOUS")
    coller(_en_gris(images["etalon_publie"], 255.0), 70, 120, 160, 160)
    coller(_en_gris(images["etalon_lu"], 1.0), 245, 120, 160, 160)
    ecrire(70, 290, "carte publiée", 0, GRIS)
    ecrire(245, 290, "notre lecture", 0, GRIS)
    ecrire(70, 316, f"bloc {et['le_bloc'][0]}_{et['le_bloc'][1]} · corrélation {_fr(et['la_correlation'])}", 0, ENCRE)
    ecrire(70, 336, f"{et['les_pixels']} pixels de carte", 0, GRIS)

    panneau(440, 80, 1310, 400, "PARTIE A, VUE AVANT D'ÉCRIRE : LA BANDE DE LA RANGÉE 176, COLONNES 64 À 144")
    w_, h_ = 840, 70
    coller(_en_gris(images["a_lue"], 1.0), 455, 118, w_, h_)
    coller(_en_gris(images["a_vis"], 255.0), 455, 212, w_, h_)
    masque = np.asarray(images["a_proche"], dtype=float)
    teinte = np.zeros(masque.shape + (3,), dtype=np.uint8)
    teinte[masque > 0] = AMBRE
    coller(Image.fromarray(teinte), 455, 306, w_, 14)
    ecrire(455, 192, "notre lecture de la spire produite", 0, GRIS)
    ecrire(455, 286, "la carte publiée au vis-à-vis, sur le segment", 0, GRIS)
    ecrire(455, 326, f"■ là où le segment repasse à moins d'un demi-feuillet : {_fr(100 * a['la_part_proche'], 0)} % des points",
           0, AMBRE)
    pa = a["a_moins_dun_demi_feuillet"]
    ecrire(455, 350, f"là : {_fr(pa['au_vis_a_vis'])} au vis-à-vis, {_fr(pa['temoin_sous_le_bloc'])} contre la spire de départ,"
                     f" {_fr(pa['temoin_decale'])} décalé · ailleurs : {_fr(a['au_dela']['au_vis_a_vis'])}", 0, ENCRE)

    panneau(50, 420, 1310, 770, "PARTIE B, DÉCLARÉE AVANT DE LIRE : LES SIX BLOCS CHOISIS SUR LES SEULS MAILLAGES")
    groupes = (("partie A, à moins d'un demi-feuillet", a["a_moins_dun_demi_feuillet"]),
               ("partie B, à moins d'un demi-feuillet", d["la_partie_b"]["reunie"]["a_moins_dun_demi_feuillet"]),
               ("partie B, au-delà", d["la_partie_b"]["reunie"]["au_dela"]))
    base, haut = 700, 200
    for g, (nom, m) in enumerate(groupes):
        x0 = 130 + g * 390
        for k, (cle, _, coul) in enumerate(LES_BARRES):
            val = m.get(cle)
            h = max(0.0, (val or 0.0)) * haut
            x = x0 + k * 80
            art.rectangle([x, base - h, x + 60, base], fill=coul)
            traces["barres"].append((nom, cle, val))
            points.append((x + 60, base - h))
            ecrire(x + 10, int(base - h) - 18, _fr(val), 0, ENCRE)
        art.line([x0 - 10, base, x0 + 250, base], fill=GRIS)
        ecrire(x0, base + 10, nom, 0, ENCRE)
        ecrire(x0, base + 28, f"{m['les_pixels']} pixels de carte", 0, GRIS)
    for k, (_, nom, coul) in enumerate(LES_BARRES):
        ecrire(130 + k * 290, 458, f"■ {nom}", 0, coul)
    blocs = " · ".join(f"{b[0]}_{b[1]}" for b in d["la_partie_b"]["le_plan"]["les_blocs_de_la_partie_b"])
    ecrire(130, 480, f"blocs {blocs}", 0, GRIS)

    art.rectangle([0, 786, L_, H_], fill=BANDE)
    ecrire(50, 798, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 820, "le juge est le segment lui-même, un tour plus loin sur sa surface ; il ne sait rien du transfert, et il "
                    "ne vaut que là où il repasse", moyen, ENCRE)
    ecrire(50, 846, "⚠ ce qui n'est PAS établi : la spire produite là où le segment ne repasse pas ; les autres spires ; un "
                    "autre rouleau ; la lecture du texte.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


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

    d, images = lire(mesure), les_images()
    tmp = sortie.parent / ".sonde_296.png"
    _, poses, cadres, points, traces = dessiner(d, tmp, images)
    autre = json.loads(json.dumps(d))
    autre["la_partie_b"]["reunie"]["a_moins_dun_demi_feuillet"].update(au_vis_a_vis=0.31, temoin_sous_le_bloc=0.12,
                                                                        temoin_decale=0.27)
    v("★★★ le titre LIT la mesure", "À 0,31, CONTRE 0,12 ET 0,27" in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    groupes = [d["la_partie_a"]["a_moins_dun_demi_feuillet"], d["la_partie_b"]["reunie"]["a_moins_dun_demi_feuillet"],
               d["la_partie_b"]["reunie"]["au_dela"]]
    v("★★★★ une barre par corrélation, chacune à la valeur mesurée",
      [x[2] for x in traces["barres"]] == [g.get(c) for g in groupes for c, _, _ in LES_BARRES])
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    v("★★★ elle dit que la partie A a été vue avant d'écrire", "VUE AVANT D'ÉCRIRE" in txt)
    octets = tmp.read_bytes()
    dessiner(d, tmp, images)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "296_le_tour_produit_porte_t_il_le_texte_du_segment.png")
    p.add_argument("--mesure", type=Path, default=LA_MESURE)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie, a.mesure)
    chemin, *_ = dessiner(lire(a.mesure), a.sortie, les_images())
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
