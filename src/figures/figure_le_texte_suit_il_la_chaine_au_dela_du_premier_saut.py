"""Le texte du segment le long de la chaîne : ce que le juge voit saut par saut, et ce qu'il y lit, contre ses trois témoins.

⚠⚠ **Ce que cette figure doit rendre évident.** Que le juge d'encre voit de moins en moins de la chaîne à chaque saut ; que, là
où il la voit, la surface produite porte les lettres que la carte publiée porte au vis-à-vis ; et que ses trois témoins, dont le
texte un tour en arrière, restent en dessous.

  uv run python src/figures/figure_le_texte_suit_il_la_chaine_au_dela_du_premier_saut.py \\
      --sortie docs/images/297_le_texte_suit_il_la_chaine_au_dela_du_premier_saut.png

⚠ Les images viennent de `data/encre_du_tour_voisin/`, que `--json` écrit ; les barres, de la mesure.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_texte_suit_il_la_chaine_au_dela_du_premier_saut.json"
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
VIOLET = (120, 84, 150)
L_, H_ = 1360, 920
LES_BARRES = (("au_vis_a_vis", "au vis-à-vis", BON), ("temoin_sous_le_bloc", "texte de la spire de départ", GRIS),
              ("temoin_decale", "vis-à-vis décalé de 1,2 mm", BLEU),
              ("temoin_du_saut_precedent", "texte un tour en arrière", VIOLET))


def _fr(x, n: int = 2) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def _milliers(n: int) -> str:
    return f"{int(n):,}".replace(",", " ")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_sauts_lus(d: dict) -> list[str]:
    return [h for h in sorted(d["les_sauts"], key=int) if d["les_sauts"][h].get("reunie")]


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    h = str(v["le_saut"])
    m = d["les_sauts"][h]["reunie"]["a_moins_dun_demi_feuillet"]
    if v["lissue"].startswith("la chaîne perd"):
        return (f"NON : LA CHAÎNE PERD LE TEXTE AU SAUT {h}, À {_fr(m['au_vis_a_vis'])} CONTRE "
                f"{_fr(max(m[c] for c, _, _ in LES_BARRES[1:]))} POUR LE MEILLEUR TÉMOIN")
    return (f"OUI : LE TEXTE SUIT LA CHAÎNE JUSQU'AU SAUT {h}, LE DERNIER QUE LE JUGE VOIT : {_fr(m['au_vis_a_vis'])} CONTRE "
            f"{_fr(max(m[c] for c, _, _ in LES_BARRES[1:]))} AU PLUS POUR SES TÉMOINS")


def _en_gris(a: np.ndarray, echelle: float | None = None, juges: np.ndarray | None = None) -> Image.Image:
    """Une carte en gris ; hors des pixels jugés, un fond neutre, parce que la mesure ne les lit pas."""
    a = np.nan_to_num(np.asarray(a, dtype=float), nan=0.0)
    haut = echelle if echelle is not None else (float(np.percentile(a, 99.5)) or 1.0)
    g = np.clip(a / haut, 0, 1) * 255
    if juges is not None:
        g = np.where(np.asarray(juges, dtype=bool), g, 150.0)
    return Image.fromarray(g.astype(np.uint8))


def les_images(donnees: Path = LES_DONNEES, saut: int = 2) -> dict:
    a = np.load(donnees / f"la_chaine_saut_{saut}_pour_la_figure.npz")
    return {"lue": a["lue"], "vis": a["au_vis_a_vis"], "precedent": a["precedent"], "proche": a["proche"]}


def dessiner(d: dict, sortie: Path, images: dict):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"barres": [], "vues": [], "memes": []}

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

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"PHercParis4 · 20230702185753 · la chaîne de 248, m7, côté plus, sans correction · modèle "
                   f"{d['le_modele']['nom']} · demi-feuillet {_fr(d['les_constantes']['le_demi_feuillet_voxels'], 0)} voxels "
                   f"· étalon {_fr(d['letalonnage']['la_correlation'])}", petit, GRIS)

    panneau(50, 80, 560, 420, "CE QUE LE JUGE VOIT, SAUT PAR SAUT")
    ecrire(70, 108, "pixels de carte à moins d'un demi-feuillet du segment, sur les 340 blocs", 0, GRIS)
    sauts = sorted(d["les_sauts"], key=int)
    plus = max(d["les_sauts"][h]["les_pixels_proches_du_segment"] for h in sauts) or 1
    base, haut = 360, 180
    for k, h in enumerate(sauts):
        s = d["les_sauts"][h]
        n = s["les_pixels_proches_du_segment"]
        x = 100 + k * 110
        hh = n / plus * haut
        coul = AMBRE if s["se_lit"] else TRAIT
        art.rectangle([x, base - hh, x + 70, base], fill=coul)
        traces["vues"].append((h, n))
        points.append((x + 70, base - hh))
        ecrire(x, int(base - hh) - 18, _milliers(n), 0, ENCRE)
        ecrire(x + 8, base + 8, f"saut {h}", 0, ENCRE)
        ecrire(x + 8, base + 26, "lu" if s["se_lit"] else "non lu", 0, ENCRE if s["se_lit"] else ALERTE)
    art.line([90, base, 540, base], fill=GRIS)
    ecrire(70, 132, "■ saut lu : ses six blocs ont au moins 10 000 pixels proches", 0, AMBRE)

    deux = d["les_sauts"].get("2", {})
    titre_b = (f"LE DEUXIÈME SAUT, BLOC {deux['les_blocs'][0][0]}_{deux['les_blocs'][0][1]}" if deux.get("les_blocs")
               else "LE DEUXIÈME SAUT")
    panneau(580, 80, 1310, 420, titre_b)
    w_, h_ = 200, 200
    for k, (cle, nom) in enumerate((("lue", "notre lecture du saut"), ("vis", "carte publiée au vis-à-vis"),
                                    ("precedent", "carte, un tour en arrière"))):
        x = 600 + k * 235
        coller(_en_gris(images[cle], 1.0 if cle == "lue" else 255.0, images["proche"]), x, 118, w_, h_)
        ecrire(x, 324, nom, 0, GRIS)
    masque = np.asarray(images["proche"], dtype=float)
    teinte = np.zeros(masque.shape + (3,), dtype=np.uint8)
    teinte[masque > 0] = AMBRE
    coller(Image.fromarray(teinte), 600, 346, 670, 12)
    ecrire(600, 366, "■ colonnes où le segment repasse à moins d'un demi-feuillet ; gris : pixels que la mesure ne lit pas", 0,
           AMBRE)
    if deux.get("les_mesures"):
        m0 = deux["les_mesures"][0]["a_moins_dun_demi_feuillet"]
        ecrire(600, 388, f"là : {_fr(m0['au_vis_a_vis'])} au vis-à-vis, {_fr(m0['temoin_du_saut_precedent'])} un tour en "
                         f"arrière, {_fr(m0['temoin_sous_le_bloc'])} spire de départ, {_fr(m0['temoin_decale'])} décalé",
               0, ENCRE)

    panneau(50, 440, 1310, 770, "LÀ OÙ LE SEGMENT REPASSE À MOINS D'UN DEMI-FEUILLET, SUR LES SIX BLOCS DE CHAQUE SAUT")
    lus = les_sauts_lus(d)
    base, haut = 700, 180
    for g, h in enumerate(lus):
        m = d["les_sauts"][h]["reunie"]["a_moins_dun_demi_feuillet"]
        x0 = 130 + g * 400
        for k, (cle, _, coul) in enumerate(LES_BARRES):
            val = m.get(cle)
            hh = max(0.0, (val or 0.0)) * haut
            x = x0 + k * 72
            art.rectangle([x, base - hh, x + 56, base], fill=coul)
            traces["barres"].append((h, cle, val))
            points.append((x + 56, base - hh))
            ecrire(x + 8, int(base - hh) - 18, _fr(val), 0, ENCRE)
        art.line([x0 - 10, base, x0 + 290, base], fill=GRIS)
        ecrire(x0, base + 10, f"saut {h} · {d['les_sauts'][h]['le_verdict']['lissue'].split(' le texte')[0]}", 0, ENCRE)
        ecrire(x0, base + 28, f"{_milliers(m['les_pixels'])} pixels de carte", 0, GRIS)
        meme = m.get("la_part_sur_la_meme_feuille_que_le_saut_precedent")
        if h != "1" and meme is not None:
            ecrire(x0, base + 44, f"vis-à-vis sur la feuille du saut précédent : {_fr(meme)}", 0,
                   ALERTE if meme > 0.9 else GRIS)
            traces["memes"].append((h, meme))
    for k, (_, nom, coul) in enumerate(LES_BARRES):
        ecrire(130 + k * 290, 478, f"■ {nom}", 0, coul)
    ecrire(130, 500, "au saut 1, le saut précédent est le segment lui-même : son témoin est le texte de la spire de départ",
           0, GRIS)

    art.rectangle([0, 786, L_, H_], fill=BANDE)
    ecrire(50, 798, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 820, "le juge est le segment lui-même, là où il repasse sur la chaîne ; il ne sait rien du transfert, et il ne "
                    "voit de la chaîne que ce que le segment couvre", moyen, ENCRE)
    ecrire(50, 846, "⚠ ce qui n'est PAS établi : la chaîne là où le segment ne repasse pas ; la chaîne corrigée ; un autre "
                    "segment ; un autre rouleau ; la lecture du texte.", moyen, ALERTE)
    trois = d["les_sauts"].get("3", {}).get("reunie", {}).get("a_moins_dun_demi_feuillet", {})
    if trois.get("la_part_sur_la_meme_feuille_que_le_saut_precedent") is not None:
        ecrire(50, 870, f"⚠ au saut 3, {_fr(trois['la_part_sur_la_meme_feuille_que_le_saut_precedent'])} des pixels jugés font "
                        "face à la feuille du saut précédent, et le témoin « un tour en arrière » y vaut presque la mesure :",
               moyen, ALERTE)
        ecrire(50, 890, "il ne départage plus un saut resté sur place d'un saut qui a avancé.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_297.png"
    _, poses, cadres, points, traces = dessiner(d, tmp, images)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"lissue": "la chaîne perd le texte au saut 2", "decidable": True, "le_saut": 2}
    autre["les_sauts"]["2"]["reunie"]["a_moins_dun_demi_feuillet"].update(
        au_vis_a_vis=0.31, temoin_sous_le_bloc=0.12, temoin_decale=0.27, temoin_du_saut_precedent=0.44)
    v("★★★ le titre LIT la mesure", "AU SAUT 2, À 0,31 CONTRE 0,44" in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [(h, c, d["les_sauts"][h]["reunie"]["a_moins_dun_demi_feuillet"].get(c))
               for h in les_sauts_lus(d) for c, _, _ in LES_BARRES]
    v("★★★★ une barre par corrélation et par saut lu, chacune à la valeur mesurée", traces["barres"] == attendu)
    v("★★★★ une barre de vue par saut, à la valeur mesurée",
      traces["vues"] == [(h, d["les_sauts"][h]["les_pixels_proches_du_segment"]) for h in sorted(d["les_sauts"], key=int)])
    v("★★★ la part sur la feuille du saut précédent est celle de la mesure, saut par saut",
      traces["memes"] == [(h, d["les_sauts"][h]["reunie"]["a_moins_dun_demi_feuillet"]
                           ["la_part_sur_la_meme_feuille_que_le_saut_precedent"]) for h in les_sauts_lus(d) if h != "1"])
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    v("★★★ elle dit quels sauts ne sont pas lus",
      all(("non lu" in txt) or s["se_lit"] for s in d["les_sauts"].values()))
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
                   / "297_le_texte_suit_il_la_chaine_au_dela_du_premier_saut.png")
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
