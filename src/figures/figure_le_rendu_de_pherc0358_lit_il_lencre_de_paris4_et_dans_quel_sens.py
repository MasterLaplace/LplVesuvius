"""Sur PHercParis4 : la carte d'encre publiée sous le bloc étalon, la couche de la surface du rendu de 409, et ce que le détecteur lit dans chaque sens.

⚠⚠ **Ce que cette figure doit rendre évident.** Quatre images du même bloc : la carte publiée, réduite 8 fois ; la couche de la surface
telle que le rendu de `409` la lit au niveau de 9,6 µm ; la lecture du détecteur quand les couches croissent vers le creux de la feuille ;
et quand elles croissent vers sa bosse. Un seul des deux sens doit redonner les lettres de la carte.

  uv run python src/figures/figure_le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.py \
      --sortie docs/images/409_le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.png

⚠ Les corrélations viennent de la mesure de `409` ; les images, des piles et des lectures gardées sous `data/` par `409`.
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
sys.path.insert(0, str(RACINE / "src" / "nappe"))
LA_MESURE = RACINE / "docs" / "mesures" / "le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
L_, H_ = 1200, 640
LA_BANDE = 520
COTE = 256
LES_X = (50, 330, 610, 890)
Y0 = 96


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_nombre(v) -> str:
    return "non lue" if v is None else f"{v:g}".replace(".", ",")


def les_images() -> list[tuple[str, np.ndarray | None]]:
    import le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens as m409
    import le_tour_produit_porte_t_il_le_texte_du_segment as m296

    carte = m296.la_carte_sous(m296.la_carte_publiee(), *m296.LE_BLOC_ETALON, 1)
    pile = m409.LE_DOSSIER / "pile_creux.npy"
    surface = (m296.reduire(np.load(pile, mmap_mode="r")[..., m409.LA_COUCHE_DE_LA_SURFACE - m296.LES_COUCHES[0]].astype(np.float32))
               if pile.exists() else None)
    out = [("carte publiée", carte), ("couche de la surface", surface)]
    for s in m409.LES_SENS:
        f = m409.LE_DOSSIER / f"encre_{s}.npy"
        out.append((f"vers {'le creux' if s == 'creux' else 'la bosse'}", m296.reduire(np.load(f)) if f.exists() else None))
    return out


def les_legendes(d: dict) -> list[str]:
    lec = d["les_lectures"]
    sous = ["", f"corrélation avec la pile de 408 : {le_nombre(d.get('la_surface_contre_408'))}"]
    for s in ("creux", "bosse"):
        x = lec.get(s)
        sous.append("non lue" if x is None else f"corrélation {le_nombre(x['la_correlation'])}, témoin {le_nombre(x['le_temoin'])}")
    return sous


def le_titre(d: dict) -> str:
    lec = d["les_lectures"]
    c = lambda s: le_nombre(lec[s]["la_correlation"]) if s in lec else "non lue"  # noqa: E731
    return (f"le rendu de 409 sur l'étalon : vers le creux {c('creux')}, vers la bosse {c('bosse')} ; "
            f"{d['le_verdict']['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    p = d["le_plan"]
    deux = (f"rapporté à côté, qui ne décide rien : morceaux du niveau 2, {p['les_morceaux'].get('tire', 0)} tirés et "
            f"{p['les_morceaux'].get('deja', 0)} déjà là ; couverture du bloc, {le_nombre(p['la_couverture'])}")
    trois = "⚠ ce qui n'est PAS établi : que la courbure d'une surface de 6 mm de PHerc0358 se lise aussi sûrement ; l'encre de PHerc0358."
    return un, deux, trois


def en_gris(a: np.ndarray) -> np.ndarray:
    a = np.where(np.isfinite(a), a, np.nan)
    lo, hi = np.nanpercentile(a, 1), np.nanpercentile(a, 99)
    return np.nan_to_num(np.clip((a - lo) / max(hi - lo, 1e-9), 0, 1) * 255, nan=0).astype(np.uint8)


def dessiner(d: dict, sortie: Path, images: list | None = None):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(x - 10, Y0 - 30, x + COTE + 10, Y0 + COTE + 60) for x in LES_X]
    images = les_images() if images is None else images
    traces = {"images": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 44, "le bloc 176_144 du segment 20230702185753, rendu depuis le niveau 2 de PHercParis4 (9,6 µm), réduit 8 fois", petit, GRIS)
    for (x0, y0, x1, y1), x, (nom, a), legende in zip(cadres, LES_X, images, les_legendes(d)):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        ecrire(x, Y0 - 22, nom, moyen, ENCRE)
        if a is None:
            ecrire(x + 90, Y0 + 120, "non lue", moyen, ALERTE)
            traces["images"].append((nom, None))
        else:
            img.paste(Image.fromarray(en_gris(np.asarray(a))[:COTE, :COTE]).convert("RGB"), (x, Y0))
            traces["images"].append((nom, np.asarray(a).shape))
        if legende:
            ecrire(x, Y0 + COTE + 12, legende, petit, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un_, deux_, trois_ = la_bande(d)
    ecrire(50, LA_BANDE + 10, un_, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux_, petit, ENCRE)
    ecrire(50, LA_BANDE + 56, trois_, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_409.png"
    try:
        images = les_images()
        _, poses, cadres, traces = dessiner(d, tmp, images)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = {"le_verdict": {"lissue": "x ; le sens est fixé : vers le creux"},
             "les_lectures": {"creux": {"la_correlation": 0.85}, "bosse": {"la_correlation": 0.01}}}
    v("★★★ le titre LIT la mesure",
      le_titre(autre) == "LE RENDU DE 409 SUR L'ÉTALON : VERS LE CREUX 0,85, VERS LA BOSSE 0,01 ; LE SENS EST FIXÉ : VERS LE CREUX", le_titre(autre))
    v("★★★★ la légende de chaque lecture porte sa corrélation de la mesure",
      all(les_legendes(d)[2 + i].startswith(f"corrélation {le_nombre(d['les_lectures'][s]['la_correlation'])}")
          for i, s in enumerate(("creux", "bosse")) if s in d["les_lectures"]))
    v("★★★★ quatre images, dans l'ordre carte, surface, creux, bosse",
      [t[0] for t in traces["images"]] == ["carte publiée", "couche de la surface", "vers le creux", "vers la bosse"])
    v("★★★★ une lecture qui manque est dite non lue, pas dessinée",
      any(t[1] is None for t in traces["images"]) is any(a is None for _, a in images))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t_, _ in poses for x in glyphes_manquants(t_)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
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
                   / "409_le_rendu_de_pherc0358_lit_il_lencre_de_paris4_et_dans_quel_sens.png")
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
