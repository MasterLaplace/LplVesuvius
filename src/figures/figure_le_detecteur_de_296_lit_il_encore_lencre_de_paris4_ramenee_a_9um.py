"""Sur PHercParis4 : la carte d'encre publiée sous le bloc étalon, et ce que le détecteur de 296 y lit à 2,4, 4,8 et 9,6 µm.

⚠⚠ **Ce que cette figure doit rendre évident.** Quatre images du même bloc, réduites 8 fois : la carte publiée, puis la lecture du
détecteur sur le bloc à sa résolution, ramené à 4,8 µm, ramené à 9,6 µm. Si le détecteur lit encore, les lettres de la carte restent dans
la dernière image. Sous chacune, sa corrélation avec la carte et celle du témoin, la carte décalée de 64 pixels.

  uv run python src/figures/figure_le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um.py \
      --sortie docs/images/408_le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um.png

⚠ Les corrélations viennent de la mesure de `408` ; les images, des lectures gardées sous `data/` par `296` et `408`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um.json"

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
    return "—" if v is None else f"{v:g}".replace(".", ",")


def les_images() -> list[tuple[str, np.ndarray | None]]:
    """La carte publiée sous le bloc, puis les lectures à 2,4, 4,8 et 9,6 µm, réduites 8 fois ; None si une lecture manque."""
    import le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um as m408
    import le_tour_produit_porte_t_il_le_texte_du_segment as m296

    carte = m296.la_carte_sous(m296.la_carte_publiee(), *m296.LE_BLOC_ETALON, 1)
    out = [("carte publiée", carte)]
    for nom, chemin in (("2,4 µm", m296.LE_DOSSIER_ENCRE / "etalon_reference.npy"), ("4,8 µm", m408.LE_DOSSIER / "etalon_ramene_2.npy"),
                        ("9,6 µm", m408.LE_DOSSIER / "etalon_ramene_4.npy")):
        out.append((nom, m296.reduire(np.load(chemin)) if chemin.exists() else None))
    return out


def les_legendes(d: dict) -> list[str]:
    """Sous chaque image : rien pour la carte, la corrélation et le témoin pour chaque lecture."""
    lec = [d["le_controle"], d["les_lectures"].get("2"), d["les_lectures"].get("4")]
    return [""] + [("non lue" if x is None else f"corrélation {le_nombre(x['la_correlation'])}, témoin {le_nombre(x['le_temoin'])}")
                   for x in lec]


def le_titre(d: dict) -> str:
    x = d["les_lectures"].get("4")
    c = "non lue" if x is None else le_nombre(x["la_correlation"])
    return ("le détecteur de 296 sur l'étalon ramené à".upper() + " 9,6 µm "
            + f": corrélation {c} ; {d['le_verdict']['lissue'].rpartition(' ; ')[2]}".upper())


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    inv = d.get("la_lecture_inverse")
    deux = ("rapporté à côté, qui ne décide rien : la lecture à 4,8 µm ; à 9,6 µm, les couches dans l'ordre inverse, corrélation "
            f"{'non lue' if inv is None else le_nombre(inv['la_correlation'])} ; le bloc est ramené par moyenne de bloc, puis "
            "rééchantillonné sur 2,4 µm")
    trois = "⚠ ce qui n'est PAS établi : la réponse d'un vrai scanner à 9,362 µm et à 113 keV ; l'encre de PHerc0358."
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
    ecrire(50, 44, "le bloc 176_144 du segment 20230702185753, réduit 8 fois ; chaque image étalée du 1er au 99e centile", petit, GRIS)
    for (x0, y0, x1, y1), x, (nom, a), legende in zip(cadres, LES_X, images, les_legendes(d)):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        ecrire(x, Y0 - 22, nom, moyen, ENCRE)
        if a is None:
            ecrire(x + 90, Y0 + 120, "non lue", moyen, ALERTE)
            traces["images"].append((nom, None))
        else:
            vue = Image.fromarray(en_gris(a)[:COTE, :COTE]).resize((COTE, COTE), Image.NEAREST)
            img.paste(vue.convert("RGB"), (x, Y0))
            traces["images"].append((nom, a.shape))
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
    tmp = sortie.parent / ".sonde_408.png"
    try:
        images = les_images()
        _, poses, cadres, traces = dessiner(d, tmp, images)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = {"le_verdict": {"lissue": "x ; oui"}, "les_lectures": {"4": {"la_correlation": 0.81, "le_temoin": 0.1}}}
    v("★★★ le titre LIT la mesure",
      le_titre(autre) == "LE DÉTECTEUR DE 296 SUR L'ÉTALON RAMENÉ À 9,6 µm : CORRÉLATION 0,81 ; OUI", le_titre(autre))
    v("★★★★ la légende de chaque lecture porte sa corrélation de la mesure",
      les_legendes(d)[1].startswith(f"corrélation {le_nombre(d['le_controle']['la_correlation'])}")
      and all(("4" not in d["les_lectures"] and lg == "non lue") or lg.startswith(f"corrélation {le_nombre(d['les_lectures'][k]['la_correlation'])}")
              for k, lg in (("2", les_legendes(d)[2]), ("4", les_legendes(d)[3])) if k in d["les_lectures"]))
    v("★★★★ quatre images, dans l'ordre carte, 2,4, 4,8, 9,6 µm", [t[0] for t in traces["images"]]
      == ["carte publiée", "2,4 µm", "4,8 µm", "9,6 µm"])
    v("★★★★ chaque lecture dessinée a la taille de la carte réduite",
      all(s is None or s[0] >= COTE for _, s in traces["images"]), str(traces["images"]))
    v("★★★★ une lecture qui manque est dite non lue, pas dessinée", any(t[1] is None for t in traces["images"]) is
      any(a is None for _, a in images))
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
                   / "408_le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um.png")
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
