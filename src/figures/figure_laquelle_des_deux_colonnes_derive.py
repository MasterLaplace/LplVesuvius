"""Laquelle des deux colonnes dérive : trois lignes parallèles, les trois boucles qu'elles ferment deux à deux.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LES TROIS LIGNES : la troisième ligne dérivée hors de
l'aile, les deux colonnes de l'aile, et la somme des pas le long de chacune. En haut à droite, LES TROIS BOUCLES à
neuf lignes, contre le bruit seul de chacune et le demi-feuillet — c'est le panneau qui conclut : la boucle la plus
serrée désigne la ligne qu'elle exclut. En bas à droite, LARGEUR PAR LARGEUR, et l'emboîtement.

  uv run python src/figures/figure_laquelle_des_deux_colonnes_derive.py \\
      --json docs/mesures/laquelle_des_deux_colonnes_derive.json \\
      --sortie docs/images/236_laquelle_des_deux_colonnes_derive.png
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
CE_QUE_224_A_RENDU = RACINE / "docs" / "mesures" / "deux_chemins_arrivent_ils_sur_la_meme_spire.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
L_, H_ = 1360, 1000
NOMS = {"laile": "l'aile", "letroite": "l'étroite", "la_large": "la large"}


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path) -> dict:
    """Le JSON de `laquelle_des_deux_colonnes_derive.py`, et le demi-feuillet de `224`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("laile", "le_verdict"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["le_demi_pli"] = float(json.loads(CE_QUE_224_A_RENDU.read_text())["le_demi_pli_en_voxels"])
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer, dans l'ordre de priorité des issues."""
    v = d["le_verdict"]
    if d.get("la_troisieme_ligne") is None:
        return "AUCUNE TROISIÈME LIGNE NE TIENT PRÈS DE L'AILE"
    if v["les_boucles_ouvertes"]:
        return "À NEUF LIGNES, UN TROU TROP LONG LAISSE UNE BOUCLE OUVERTE"
    if not v["tranche"]:
        return "À NEUF LIGNES, LES TROIS BOUCLES NE DÉPARTAGENT PAS LES DEUX COLONNES"
    if not v["cest_une_colonne_de_laile"]:
        return "À NEUF LIGNES, C'EST LA TROISIÈME LIGNE QUI DÉRIVE"
    return f"À NEUF LIGNES, C'EST LA COLONNE {v['la_ligne_qui_derive']} QUI DÉRIVE"


def les_sommes_par_ligne(d: dict) -> dict:
    """La somme des pas le long de chaque ligne parallèle, à la largeur jugée, lue dans les côtés des boucles."""
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    out = {}
    for nom, b in (d.get("par_boucle") or {}).items():
        x = b["par_largeur"][k1]
        if not x["fermable"]:
            continue
        a0, a1, b0, b1 = b["les_coins"]
        cotes = {c["le_cote"]: c["la_somme_en_voxels"] for c in x["les_cotes"]}
        if d["la_troisieme_ligne"]["le_sens"] == "colonnes":
            out.setdefault(int(b0), cotes["gauche"])
            out.setdefault(int(b1), cotes["droite"])
        else:
            out.setdefault(int(a0), cotes["haut"])
            out.setdefault(int(a1), cotes["bas"])
    return out


def la_plus_serree_par_largeur(d: dict) -> dict:
    """À chaque largeur où les trois boucles ferment, celle qui ferme le plus serré."""
    par = d.get("par_boucle") or {}
    out = {}
    for k in sorted((par.get("laile") or {}).get("par_largeur") or {}, key=int):
        xs = {n: par[n]["par_largeur"][k] for n in ("laile", "letroite", "la_large")}
        if all(x["fermable"] for x in xs.values()):
            out[k] = min(xs, key=lambda n: abs(float(xs[n]["la_fermeture_en_voxels"])))
    return out


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    demi = d["le_demi_pli"]
    aile = d["laile"]
    tl = d["la_troisieme_ligne"]
    v = d["le_verdict"]
    k1 = str(v["la_largeur_jugee"])
    par = d.get("par_boucle") or {}
    rp = d.get("la_reproduction") or {}
    a0, a1, b0, b1 = [int(x) for x in aile["les_coins"]]

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"l'aile de droite de 234, rangées {a0} à {a1}, entre les colonnes {b0} et {b1} · la troisième "
                   f"ligne, dérivée de la présence, et ses deux bouts, lus pour cette tranche, retombent sur les bandes "
                   f"publiées en {rp.get('combien_de_coutures_relues', 0)} coutures à l'écart "
                   f"{_fr(rp.get('lecart_le_plus_grand'))}", petit, GRIS)

    # ── PANNEAU 1 · LES TROIS LIGNES ─────────────────────────────────────────────────────────
    panneau(50, 84, 560, 800, "LES TROIS LIGNES · et la somme des pas le long de chacune")
    lignes = sorted({int(tl["la_ligne"]), int(tl["la_plus_proche"]), int(tl["la_plus_loin"])})
    sommes = les_sommes_par_ligne(d)
    X0, X1, Y0, Y1 = 170, 480, 170, 600

    def X(c):
        return X0 + (X1 - X0) * (float(c) - lignes[0]) / max(1.0, float(lignes[-1] - lignes[0]))
    derive = v.get("la_ligne_qui_derive")
    for c in lignes:
        coul = ALERTE if c == derive else (CONTRE if c == int(tl["la_ligne"]) else BON)
        art.rectangle([X(c) - 5, Y0, X(c) + 5, Y1], fill=coul)
        lib = "troisième ligne" if c == int(tl["la_ligne"]) else "colonne de l'aile"
        ecrire(X(c) - 30, Y0 - 34, f"colonne {c}", 0, ENCRE)
        ecrire(X(c) - 40, Y0 - 20, lib, 0, GRIS)
        points.append((X(c), Y1))
    for r, t in ((a0, f"rangée {a0}"), (a1, f"rangée {a1}")):
        y = Y0 if r == a0 else Y1
        art.line([X(lignes[0]), y, X(lignes[-1]), y], fill=GRIS, width=2)
        ecrire(66, y - 7, t, 0, GRIS)
    yy = 640
    ecrire(66, yy, "somme des pas le long de la ligne, à neuf lignes, en voxels :", 0, ENCRE)
    yy += 22
    n_s = 0
    for c in lignes:
        if c in sommes:
            ecrire(80, yy, f"colonne {c} : {_fr(sommes[c])}", 0, ALERTE if c == derive else ENCRE)
            yy += 20
            n_s += 1
    traces["sommes"] = n_s
    ecrire(66, yy + 8, "⚠ une somme seule suit aussi la forme vraie de la feuille :", 0, GRIS)
    ecrire(66, yy + 24, "seules les boucles la retranchent", 0, GRIS)

    # ── PANNEAU 2 · LES TROIS BOUCLES ────────────────────────────────────────────────────────
    panneau(580, 84, 1310, 470, "LES TROIS BOUCLES · à neuf lignes, contre le bruit seul")
    BX0, BW, VMAX = 800, 300, 60.0

    def BX(x):
        return BX0 + BW * min(abs(float(x)), VMAX) / VMAX
    yy = 140
    n_b = 0
    for nom in ("laile", "letroite", "la_large"):
        if nom not in par:
            continue
        co = par[nom]["les_coins"]
        c0_, c1_ = (co[2], co[3]) if tl["le_sens"] == "colonnes" else (co[0], co[1])
        x = par[nom]["par_largeur"][k1]
        ecrire(596, yy, f"{NOMS[nom]} · colonnes {c0_} à {c1_}", 0, ENCRE)
        if not x["fermable"]:
            art.rectangle([BX0, yy + 3, BX0 + BW, yy + 12], outline=ALERTE)
            ecrire(BX0 + BW + 12, yy, "ouverte", 0, ALERTE)
        else:
            L = x["la_fermeture_en_voxels"]
            coul = BON if nom == v.get("la_plus_serree") else (ALERTE if abs(L) >= demi else CONTRE)
            art.rectangle([BX0, yy + 3, BX(L), yy + 12], fill=coul)
            med = x["le_nul"]["la_fermeture_mediane_en_valeur_absolue"]
            art.line([BX(med), yy + 1, BX(med), yy + 14], fill=ENCRE, width=2)
            points.append((BX(L), yy + 12))
            ecrire(BX0 + BW + 12, yy, f"{_fr(L)} · {_fr(x['le_nul']['la_part_sous_la_fermeture'])}", 0, ENCRE)
        yy += 22
        ecrire(612, yy, f"exclut la colonne {lexclue_(nom, tl)}", 0, GRIS)
        yy += 40
        n_b += 1
    traces["boucles"] = n_b
    art.line([BX(demi), 136, BX(demi), yy - 30], fill=ALERTE, width=1)
    ecrire(BX(demi) - 60, yy - 26, f"demi-feuillet · {_fr(demi)}", 0, ALERTE)
    ecrire(596, 410, "barre : la fermeture en valeur absolue · trait : la médiane du bruit seul", 0, GRIS)
    ecrire(596, 428, "chiffres : la fermeture · la part du bruit seul qui ferme plus serré", 0, GRIS)
    if v.get("les_marges"):
        ecrire(596, 446, "marges sur le bruit seul : " + " · ".join(f"{NOMS[n]} {_fr(m_)}"
                                                                   for n, m_ in sorted(v["les_marges"].items())),
               0, BON if v["tranche"] else ALERTE)

    # ── PANNEAU 3 · LARGEUR PAR LARGEUR ──────────────────────────────────────────────────────
    panneau(580, 490, 1310, 800, "LARGEUR PAR LARGEUR · et l'emboîtement")
    emb = (d.get("lemboitement") or {}).get("par_largeur") or {}
    yy = 530
    ecrire(596, yy, "lignes", 0, GRIS)
    for i, nom in enumerate(("laile", "letroite", "la_large")):
        ecrire(680 + 130 * i, yy, NOMS[nom], 0, GRIS)
    ecrire(1080, yy, "emboîtement", 0, GRIS)
    yy += 24
    n_l = 0
    for k in sorted((par.get("laile") or {}).get("par_largeur") or {}, key=int):
        ecrire(596, yy, f"{k}", 0, ENCRE)
        for i, nom in enumerate(("laile", "letroite", "la_large")):
            x = par[nom]["par_largeur"][k]
            ecrire(680 + 130 * i, yy, _fr(x["la_fermeture_en_voxels"]) if x["fermable"] else "ouverte", 0, ENCRE)
        e = emb.get(k) or {}
        ecrire(1080, yy, f"écart {_fr(e['lecart'], 6)}" if e.get("jugeable") else "non jugé", 0,
               ENCRE if e.get("jugeable") else GRIS)
        yy += 24
        n_l += 1
    traces["largeurs"] = n_l
    ecrire(596, 760, "la large est la somme de l'aile et de l'étroite : la colonne commune s'y parcourt deux fois,", 0,
           GRIS)
    ecrire(596, 776, "une fois dans chaque sens", 0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    if v.get("la_plus_serree"):
        ecrire(50, 856, f"★ la boucle la plus serrée est {NOMS[v['la_plus_serree']]}, qui exclut la colonne "
                        f"{lexclue_(v['la_plus_serree'], tl)} ; la boucle de l'aile retombe sur ce que 234 publie.",
               moyen, ENCRE)
    ps = la_plus_serree_par_largeur(d)
    if ps and len(set(ps.values())) == 1:
        ecrire(50, 882, f"★ à chacune des {len(ps)} largeurs, la plus serrée est {NOMS[next(iter(ps.values()))]}.",
               moyen, ENCRE)
        traces["par_largeur"] = len(ps)
    if v.get("les_marges"):
        n_m, m_m = min(v["les_marges"].items(), key=lambda t: t[1])
        ecrire(50, 908, f"⚠ la plus petite marge sur le bruit seul est celle de {NOMS[n_m]} : {_fr(m_m)} voxels.", moyen,
               ALERTE)
    ecrire(50, 934, "⚠ ce qui n'est PAS établi : où, le long de l'aile, la ligne désignée dérive, ni si la troisième "
                    "ligne est juste : elle départage, elle n'est pas une vérité de terrain.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def lexclue_(nom: str, tl: dict) -> int:
    """La ligne qu'une boucle exclut — lue comme la mesure la définit."""
    return {"laile": int(tl["la_ligne"]), "letroite": int(tl["la_plus_loin"]),
            "la_large": int(tl["la_plus_proche"])}[nom]


def verifier(json_path: Path, sortie: Path) -> int:
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

    d = lire(json_path)
    tmp = sortie.parent / ".sonde_236.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(tl, ouv, tr, col):
        return {"la_troisieme_ligne": tl, "le_verdict": {"les_boucles_ouvertes": ouv, "tranche": tr,
                                                          "cest_une_colonne_de_laile": col,
                                                          "la_ligne_qui_derive": 243 if col else None}}
    t_ = {"la_ligne": 234}
    tous = [_v(None, [], False, False), _v(t_, ["laile"], True, True), _v(t_, [], False, False),
            _v(t_, [], True, False), _v(t_, [], True, True)]
    v("★★★★ les cinq titres possibles sont distincts, et l'ordre des issues prime",
      len({le_titre(x) for x in tous}) == 5 and le_titre(_v(None, ["laile"], True, True)) == le_titre(tous[0]))
    v("★★★ le titre LIT le verdict", ("QUI DÉRIVE" in le_titre(d)) == bool(d["le_verdict"]["tranche"]
                                                                      and d["le_verdict"]["cest_une_colonne_de_laile"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ les trois boucles ont leur barre, les trois lignes leur somme, les quatre largeurs leur ligne",
      traces.get("boucles") == 3 and traces.get("sommes") == 3 and traces.get("largeurs") == 4)
    txt = " ".join(t for _, _, t, _ in poses)
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    v("★★★★ elle porte la fermeture de chaque boucle à chaque largeur, et ce qui n'est PAS établi",
      all(_fr(x["la_fermeture_en_voxels"]) in txt for b in d["par_boucle"].values() for x in b["par_largeur"].values()
          if x["fermable"]) and "n'est PAS établi" in txt and k1 == "9")
    v("★★★★ la somme de chaque ligne est lue deux fois pareille dans les boucles qui la partagent",
      all(abs(les_sommes_par_ligne(d)[c] - s_) < 1e-9 for c, s_ in _les_sommes_en_double(d)))
    v("★★★★ la plus petite marge est nommée", not d["le_verdict"].get("les_marges") or
      _fr(min(d["le_verdict"]["les_marges"].values())) in txt)
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


def _les_sommes_en_double(d: dict) -> list[tuple[int, float]]:
    """Chaque ligne parallèle, telle que la lit chacune des boucles qui la contient."""
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    out = []
    for b in (d.get("par_boucle") or {}).values():
        x = b["par_largeur"][k1]
        if not x["fermable"]:
            continue
        a0, a1, b0, b1 = b["les_coins"]
        cotes = {c["le_cote"]: c["la_somme_en_voxels"] for c in x["les_cotes"]}
        if d["la_troisieme_ligne"]["le_sens"] == "colonnes":
            out += [(int(b0), cotes["gauche"]), (int(b1), cotes["droite"])]
        else:
            out += [(int(a0), cotes["haut"]), (int(a1), cotes["bas"])]
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path, default=RACINE / "docs" / "mesures" / "laquelle_des_deux_colonnes_derive.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "236_laquelle_des_deux_colonnes_derive.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
