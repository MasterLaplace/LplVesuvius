"""Le transfert de spire à spire : où il retombe, et quelle règle retrouve la spire voisine.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, OÙ LE TRANSFERT RETOMBE sur `20230702185753` : chaque maille
du segment, verte quand le transfert arrive sur la couche que le segment porte lui-même au tour voisin, rouille quand il
arrive ailleurs. Un pas fixe d'un côté, la feuille suivante puis le vote de l'autre : les taches rouilles du premier
sont ce que le second rattrape. À droite, LA PART SUR LA BONNE SPIRE pour chaque règle, des deux côtés de la normale,
sur le segment et sur la bande `w028-037`, tracée par d'autres : c'est le panneau qui dit que compter les feuilles bat
le pas fixe, et que viser un pas ne le bat pas.

  uv run python src/figures/figure_le_transfert_retrouve_t_il_la_spire_voisine.py \\
      --sortie docs/images/247_le_transfert_retrouve_t_il_la_spire_voisine.png
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
MESURES = RACINE / "docs" / "mesures"
LE_SEGMENT_JSON = MESURES / "le_transfert_retrouve_t_il_la_spire_voisine.json"
LA_BANDE_JSON = MESURES / "le_transfert_sur_la_bande_w028_037.json"
LA_SPIRE_JSON = MESURES / "la_spire_voisine_est_elle_a_un_pas.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
PRESENT = (222, 219, 211)
L_, H_ = 1360, 1000
LES_ISSUES = {"v": BON, "x": ALERTE, ".": PRESENT, "o": CONTRE}
LA_PREDICTION = "m7"
LES_REGLES = (("un pas fixe, sans lire", None),
              ("recaler vers un pas", "le_recalage"),
              ("recaler, voter, sinon le pas", "le_consensus_sinon_le_pas"),
              ("la feuille suivante", "la_feuille_suivante"),
              ("la feuille suivante, puis le vote", "la_feuille_suivante_sinon_le_pas_puis_le_vote"))


def _fr(x, n: int = 3) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    """Les deux mesures du transfert, et celle de la spire voisine que le segment porte."""
    d = {"segment": json.loads(LE_SEGMENT_JSON.read_text()), "bande": json.loads(LA_BANDE_JSON.read_text()),
         "spire": json.loads(LA_SPIRE_JSON.read_text())}
    for k in ("segment", "bande"):
        if not d[k].get("decidable"):
            raise SystemExit(f"mesure {k} indécidable")
    return d


def la_part(mesure: dict, cote: str, verite: str, regle: str | None, prediction: str = LA_PREDICTION) -> float:
    """La part sur la bonne spire d'une règle, lue dans la mesure et jamais recalculée."""
    j = mesure["les_predictions"][prediction][cote][verite]
    if regle is None:
        return j["le_temoin_sans_lecture"]["la_part_sur_la_bonne_spire"]
    if regle == "le_recalage":
        return j["le_recalage"]["la_part_sur_la_bonne_spire"]
    return j["les_etages_posterieurs"][regle]["la_part_sur_la_bonne_spire"]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : la meilleure règle contre le pas fixe, des deux côtés."""
    s = d["segment"]
    a = [la_part(s, c, "le_segment_seul", LES_REGLES[-1][1]) for c in ("du_cote_plus", "du_cote_moins")]
    b = [la_part(s, c, "le_segment_seul", None) for c in ("du_cote_plus", "du_cote_moins")]
    if min(a) > max(b):
        return (f"COMPTER LES FEUILLES RETROUVE LA SPIRE VOISINE SUR {_fr(a[0])} ET {_fr(a[1])} DES POINTS, "
                f"UN PAS FIXE SUR {_fr(b[0])} ET {_fr(b[1])}")
    return "COMPTER LES FEUILLES NE BAT PAS UN PAS FIXE"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, object] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    s = d["segment"]
    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"{s['le_segment']} · juge : la couche que le segment porte lui-même au tour voisin, tracée à la "
                   f"main · prédiction {LA_PREDICTION} à 9,6 µm · {s['les_points']} points", petit, GRIS)

    # ── PANNEAU 1 · OÙ LE TRANSFERT RETOMBE ─────────────────────────────────────────────────
    panneau(50, 84, 690, 800, "OÙ LE TRANSFERT RETOMBE · côté moins, chaque maille du segment")
    cartes = s["les_predictions"][LA_PREDICTION]["du_cote_moins"]["le_segment_seul"]["les_cartes"]
    ech = 1.25
    comptes = {}
    for k, (nom, cle) in enumerate((("un pas fixe, sans lire", "sans_lecture"),
                                    ("la feuille suivante, puis le vote", "la_feuille_suivante_puis_le_vote"))):
        x0, y0 = 74 + k * 310, 150
        ecrire(x0, 124, nom, 0, ENCRE)
        lignes = cartes[cle]
        larg = max(len(l_) for l_ in lignes)
        petite = Image.new("RGB", (larg, len(lignes)), FOND)
        px = petite.load()
        n = {"v": 0, "x": 0}
        for i, l_ in enumerate(lignes):
            for j, ch in enumerate(l_):
                if ch in LES_ISSUES:
                    px[j, i] = LES_ISSUES[ch]
                if ch in n:
                    n[ch] += 1
        grande = petite.resize((round(larg * ech), round(len(lignes) * ech)), Image.NEAREST)
        img.paste(grande, (x0, y0))
        points.append((x0 + grande.width, y0 + grande.height))
        comptes[cle] = n
        ecrire(x0, y0 + grande.height + 8, f"bonne spire {n['v']} · ailleurs {n['x']}", 0, GRIS)
    traces["comptes"] = comptes
    ly = 150 + round(len(cartes["sans_lecture"]) * ech) + 36
    for k, (ch, nom) in enumerate((("v", "la bonne spire"), ("x", "une autre spire"), (".", "rien en face pour juger"))):
        art.rectangle([74 + k * 190, ly + 3, 88 + k * 190, ly + 13], fill=LES_ISSUES[ch], outline=TRAIT)
        ecrire(96 + k * 190, ly, nom, 0, GRIS)

    # ── PANNEAU 2 · LA PART SUR LA BONNE SPIRE ──────────────────────────────────────────────
    panneau(710, 84, 1310, 800, "LA PART SUR LA BONNE SPIRE · côté plus, puis côté moins")
    groupes = (("20230702185753, jugé par lui-même", s, "le_segment_seul"),
               ("20230702185753, jugé par lui-même et ses témoins", s, "le_segment_et_ses_temoins"),
               ("w028-037, tranche centrale, jugée par elle-même", d["bande"], "le_segment_seul"))
    BX0, BX1 = 950, 1200
    y = 128
    barres = 0
    for titre, mesure, verite in groupes:
        ecrire(726, y, titre, 0, ENCRE)
        y += 22
        for nom, cle in LES_REGLES:
            ecrire(740, y + 2, nom, 0, GRIS)
            for c, cote in enumerate(("du_cote_plus", "du_cote_moins")):
                v = la_part(mesure, cote, verite, cle)
                yy = y + c * 9
                coul = CONTRE if cle is None else (BON if cle.startswith("la_feuille") else ALERTE)
                art.rectangle([BX0, yy, BX0 + (BX1 - BX0) * v, yy + 7], fill=coul)
                points.append((BX0 + (BX1 - BX0) * v, yy + 7))
                barres += 1
            ecrire(BX1 + 8, y + 2, f"{_fr(la_part(mesure, 'du_cote_plus', verite, cle))} · "
                                   f"{_fr(la_part(mesure, 'du_cote_moins', verite, cle))}", 0, ENCRE)
            y += 24
        y += 14
    for f_ in (0.5, 0.75, 1.0):
        xg = BX0 + (BX1 - BX0) * f_
        art.line([xg, 146, xg, y - 12], fill=TRAIT, width=1)
        ecrire(xg - 10, y - 8, _fr(f_, 2), 0, GRIS)
    traces["barres"] = barres
    ecrire(726, y + 16, "bleu : le témoin qui ne lit rien · rouille : viser un pas · vert : compter les feuilles", 0,
           GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    sp = d["spire"]["le_segment_lui_meme"]
    ecrire(50, 832, f"LE VERDICT : compter les feuilles le long de la normale bat le pas fixe sur le segment et sur la "
                    f"bande ; viser un pas ne le bat pas", petit, ENCRE)
    ecrire(50, 856, f"★ le segment porte sa propre spire voisine en face de {_fr(sp['la_part_avec_une_couche'])} de ses "
                    f"points, à {_fr(sp['du_cote_plus']['lecart_median_en_pas'])} et "
                    f"{_fr(sp['du_cote_moins']['lecart_median_en_pas'])} pas : c'est le juge.", moyen, ENCRE)
    b = d["bande"]
    ecrire(50, 882, f"★ sur la bande w028-037, tracée par d'autres : "
                    f"{_fr(la_part(b, 'du_cote_plus', 'le_segment_seul', LES_REGLES[-1][1]))} et "
                    f"{_fr(la_part(b, 'du_cote_moins', 'le_segment_seul', LES_REGLES[-1][1]))} contre "
                    f"{_fr(la_part(b, 'du_cote_plus', 'le_segment_seul', None))} et "
                    f"{_fr(la_part(b, 'du_cote_moins', 'le_segment_seul', None))} ; "
                    f"avec ps256 sur le segment : {_fr(la_part(s, 'du_cote_plus', 'le_segment_seul', LES_REGLES[-1][1], 'ps256'))}"
                    f" et {_fr(la_part(s, 'du_cote_moins', 'le_segment_seul', LES_REGLES[-1][1], 'ps256'))}.",
           moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : les règles après la première ont été écrites après sa mesure, et la "
                    "bande est leur seule validation ; aucune spire entière n'est encore produite.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path) -> int:
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

    d = lire()
    tmp = sortie.parent / ".sonde_247.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "COMPTER LES FEUILLES" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    # ⚠⚠⚠ LA CARTE DOIT DIRE CE QUE LA MESURE DIT : ses mailles vertes, rapportées aux mailles jugées, rendent la part
    # que la mesure publie pour ce côté, cette vérité et cette règle.
    j = d["segment"]["les_predictions"][LA_PREDICTION]["du_cote_moins"]["le_segment_seul"]
    for cle, part in (("sans_lecture", j["le_temoin_sans_lecture"]["la_part_sur_la_bonne_spire"]),
                      ("la_feuille_suivante_puis_le_vote",
                       j["les_etages_posterieurs"]["la_feuille_suivante_sinon_le_pas_puis_le_vote"]
                       ["la_part_sur_la_bonne_spire"])):
        n = traces["comptes"][cle]
        v(f"★★★★ la carte « {cle} » rend la part publiée", round(n["v"] / (n["v"] + n["x"]), 4) == part,
          f"{n} contre {part}")
    v("★★★★ chaque règle a ses deux barres, sur les trois objets", traces["barres"] == 3 * len(LES_REGLES) * 2)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte le juge, la validation et ce qui n'est PAS établi",
      "c'est le juge" in txt and "w028-037" in txt and "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "247_le_transfert_retrouve_t_il_la_spire_voisine.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
