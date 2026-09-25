"""Les ratés du deuxième saut rejugés : hérités ou propres, sous le juge de 248 et sous les deux juges de 253.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chaque juge et chaque chaîne, les ratés du deuxième saut coupés
en hérités et en propres, rapportés à leur total. À droite, combien des ratés propres de 277 le juge intact écarte, et où
tombent ceux qu'il garde.

  uv run python src/figures/figure_sous_un_juge_intact_le_deuxieme_saut_rate_t_il_encore_de_lui_meme.py \\
      --sortie docs/images/278_sous_un_juge_intact_le_deuxieme_saut_rate_t_il_encore_de_lui_meme.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "sous_un_juge_intact_le_deuxieme_saut_rate_t_il_encore_de_lui_meme.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
HERITE = (214, 170, 140)
ECARTE = (206, 208, 211)
L_, H_ = 1360, 760
LES_JUGES = (("le_juge_de_248", "le juge de 248"), ("le_juge_intact", "le juge intact de 253"),
             ("le_juge_sans_falaise", "le juge sans falaise de 253"))
LES_CHAINES = (("le_temoin", "témoin"), ("partie_de_la_spire_corrigee", "spire corrigée"))


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def le_titre(d: dict) -> str:
    o = d["le_juge_intact"]["partie_de_la_spire_corrigee"]
    e = d["les_propres_de_277_que_le_juge_intact_ecarte"]["partie_de_la_spire_corrigee"]
    return (f"SOUS UN JUGE INTACT, {o['les_propres']} RATÉS PROPRES ET {o['les_herites']} HÉRITÉS AU DEUXIÈME SAUT : "
            f"IL ÉCARTE {e['ecartes']} DES {e['les_propres']} RATÉS PROPRES DE 277")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"barres": [], "lignes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · les deux chaînes de 276 · un raté est hérité si le premier saut avait "
                   "raté, propre s'il était juste", petit, GRIS)

    # ── PANNEAU 1 · HÉRITÉS OU PROPRES, SOUS CHAQUE JUGE ────────────────────────────────────────────────────────────
    panneau(50, 80, 640, 640, "LES RATÉS DU DEUXIÈME SAUT, SOUS CHAQUE JUGE")
    bx0, bx1 = 190, 600
    for i, (kj, nom_j) in enumerate(LES_JUGES):
        y0 = 130 + 165 * i
        ecrire(70, y0, f"{nom_j} : {d['les_points_notes'][kj]} points notés aux deux sauts", moyen, ENCRE)
        for k, (kc, nom_c) in enumerate(LES_CHAINES):
            r = d[kj][kc]
            y = y0 + 30 + 52 * k
            ecrire(70, y + 8, nom_c, 0, ENCRE)
            tot = max(r["les_rates_du_deuxieme_saut"], 1)
            x = bx0
            for cle, coul in (("les_herites", HERITE), ("les_propres", ALERTE)):
                w = r[cle] / tot * (bx1 - bx0)
                art.rectangle([x, y, x + w, y + 26], fill=coul)
                points.append((x + w, y + 26))
                traces["barres"].append((kj, kc, cle, r[cle]))
                x += w
            ecrire(bx0, y + 30, f"{r['les_rates_du_deuxieme_saut']} ratés : {r['les_herites']} hérités, "
                                f"{r['les_propres']} propres", 0, GRIS)
    for k, (coul, texte) in enumerate(((HERITE, "hérité"), (ALERTE, "propre"))):
        art.rectangle([70 + 120 * k, 614, 82 + 120 * k, 626], fill=coul)
        ecrire(88 + 120 * k, 613, texte, 0, ENCRE)

    # ── PANNEAU 2 · CE QUE LE JUGE INTACT ÉCARTE ─────────────────────────────────────────────────────────────────────
    panneau(660, 80, 1310, 640, "LES RATÉS PROPRES DE 277 QUE LE JUGE INTACT ÉCARTE")
    for k, (kc, nom_c) in enumerate(LES_CHAINES):
        e = d["les_propres_de_277_que_le_juge_intact_ecarte"][kc]
        y = 150 + 70 * k
        ecrire(690, y, f"{nom_c} : {e['les_propres']} ratés propres sous le juge de 248", 0, ENCRE)
        tot = max(e["les_propres"], 1)
        wg = e["gardes"] / tot * 560
        art.rectangle([690, y + 20, 690 + wg, y + 44], fill=ALERTE)
        art.rectangle([690 + wg, y + 20, 1250, y + 44], fill=ECARTE)
        points.append((1250, y + 44))
        traces["barres"].append(("ecartes", kc, e["gardes"], e["ecartes"]))
        ecrire(690, y + 48, f"gardés : {e['gardes']} · écartés, couche déchirée à l'un des deux sauts : {e['ecartes']}",
               0, GRIS)
    ecrire(674, 320, "OÙ TOMBENT LES RATÉS PROPRES QUE LE JUGE INTACT GARDE", moyen, ENCRE)
    colonnes = [(690, "chaîne"), (850, "trop près"), (950, "trop loin"), (1050, "sur la 1re couche"), (1190, "n'avance pas")]
    for x, t in colonnes:
        ecrire(x, 352, t, 0, GRIS)
    for k, (kc, nom_c) in enumerate(LES_CHAINES):
        p_ = d["le_juge_intact"][kc]["parmi_les_propres"]
        y = 380 + 30 * k
        for (x, _), t in zip(colonnes, (nom_c, str(p_["trop_pres"]), str(p_["trop_loin"]),
                                        str(p_["retombes_sur_la_premiere_couche"]), str(p_["dun_saut_qui_navance_pas"]))):
            ecrire(x, y, t, 0, ENCRE)
        traces["lignes"] += 1

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 656, L_, H_], fill=BANDE)
    ecrire(50, 668, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 690, "sous le juge de 248, les deux chaînes redonnent le rangement de 277 compte pour compte", moyen, ENCRE)
    ecrire(50, 714, "⚠ ce qui n'est PAS établi : une couche qui glisse par des pentes douces reste intacte ; une correction "
                    "du deuxième saut.", moyen, ALERTE)

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

    d = lire(mesure)
    tmp = sortie.parent / ".sonde_278.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    o = d["le_juge_intact"]["partie_de_la_spire_corrigee"]
    v("★★★ le titre LIT la mesure", f"{o['les_propres']} RATÉS PROPRES ET {o['les_herites']} HÉRITÉS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [(kj, kc, c, d[kj][kc][c]) for kj, _ in LES_JUGES for kc, _ in LES_CHAINES
               for c in ("les_herites", "les_propres")]
    v("★★★★ deux segments par juge et par chaîne, hérités puis propres, aux comptes mesurés",
      traces["barres"][:len(attendu)] == attendu, str(traces["barres"][:4]))
    v("★★★★ gardés et écartés font tous les ratés propres de 277",
      all(e["gardes"] + e["ecartes"] == e["les_propres"]
          for e in d["les_propres_de_277_que_le_juge_intact_ecarte"].values()))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" /
                   "278_sous_un_juge_intact_le_deuxieme_saut_rate_t_il_encore_de_lui_meme.png")
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
