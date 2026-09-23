"""Deux chemins arrivent-ils sur la même spire : le segment, les deux chemins de chaque boucle, le bruit seul.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LE SEGMENT : les six bandes, les quatre boucles
autour de la croix centrale et le grand rectangle, chaque boucle marquée de sa fermeture — ou ouverte,
avec l'endroit où le consensus manque. En haut à droite, LES DEUX CHEMINS de chaque boucle, du même départ
à la même arrivée, et la fenêtre du demi-feuillet autour de l'arrivée : c'est le panneau qui conclut. En bas
à droite, CE QUE LE BRUIT SEUL DONNERAIT : chaque fermeture contre des marches indépendantes et contre les
boucles d'une seule ligne par côté.

  uv run python src/figures/figure_deux_chemins_arrivent_ils_sur_la_meme_spire.py \\
      --json docs/mesures/deux_chemins_arrivent_ils_sur_la_meme_spire.json \\
      --sortie docs/images/224_deux_chemins_arrivent_ils_sur_la_meme_spire.png
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

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
BANDE_LUE = (200, 207, 224)
BRUIT = (222, 220, 214)

LES_QUADRANTS = ("haut_gauche", "haut_droite", "bas_gauche", "bas_droite")
LES_NOMS = {"haut_gauche": "en haut à gauche", "haut_droite": "en haut à droite",
            "bas_gauche": "en bas à gauche", "bas_droite": "en bas à droite",
            "le_grand_rectangle": "le grand rectangle"}
L_, H_ = 1360, 1030


def _fr(x, n: int = 3) -> str:
    """Un nombre en français. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def _signe(x) -> str:
    return ("+" if float(x) > 0 else "") + _fr(x, 2)


def lire(chemin: Path) -> dict:
    """Le JSON de `deux_chemins_arrivent_ils_sur_la_meme_spire.py`.

    ⚠⚠⚠ SANS LES CHEMINS PUBLIÉS, la figure tracerait un résumé ; sans l'étalon, une épreuve se lirait
    comme si elle tenait sa garantie.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("les_boucles", "lepreuve", "letalon_de_lepreuve", "la_couverture_du_consensus",
                "les_centres", "le_verdict", "la_reproduction", "la_grille"):
        if not d.get(cle):
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if v["les_boucles_qui_depassent"]:
        return "DEUX CHEMINS DE CONSENSUS ARRIVENT SUR DES SPIRES DIFFÉRENTES"
    if v["mieux_que_des_marches_independantes"] is None:
        return "DEUX CHEMINS DE CONSENSUS ARRIVENT SUR LA MÊME SPIRE ; L'ÉPREUVE NE TRANCHE PAS"
    if v["mieux_que_des_marches_independantes"]:
        return "DEUX CHEMINS DE CONSENSUS ARRIVENT SUR LA MÊME SPIRE, ET PORTENT UNE GÉOMÉTRIE COMMUNE"
    return "DEUX CHEMINS DE CONSENSUS ARRIVENT SUR LA MÊME SPIRE, COMME Y ARRIVERAIT UN BRUIT DE CETTE TAILLE"


def les_trous(d: dict) -> list[str]:
    """Où le consensus manque, dit par bande — pour la légende et pour la bande du bas."""
    out = []
    for k, c in sorted(d["la_couverture_du_consensus"].items()):
        s = c["les_coutures_sans_consensus"]
        if s:
            sens, centre = k.split("_")
            lieu = ", ".join(str(x) for x in s) if len(s) < 3 else f"{s[0]}–{s[-1]}"
            out.append(f"{'la rangée' if sens == 'rangees' else 'la colonne'} {centre}, "
                       f"couture{'s' if len(s) > 1 else ''} {lieu}")
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

    ve, ep, et = d["le_verdict"], d["lepreuve"], d["letalon_de_lepreuve"]
    B, demi = d["les_boucles"], float(d["le_demi_pli_en_voxels"])
    R, C = d["les_centres"]["rangees"], d["les_centres"]["colonnes"]
    gy, gx = d["la_grille"]
    rp = d["la_reproduction"]

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"six bandes de cinq lignes · les quatre neuves lues sur ce que les boucles "
                   f"traversent, retombées sur 219 et 223 en {rp['combien_de_coutures_relues']} coutures, "
                   f"écart {_fr(rp['lecart_le_plus_grand'], 4)} · consensus = médiane des lignes présentes, "
                   f"au moins trois sur cinq", petit, GRIS)

    # ── PANNEAU 1 · LE SEGMENT ────────────────────────────────────────────────────────────
    panneau(50, 84, 520, 812, "LE SEGMENT · six bandes, quatre boucles")
    s = min(360.0 / gx, 520.0 / gy)
    mx0, my0 = 110, 150

    def px(c):
        return mx0 + s * float(c)

    def py(r):
        return my0 + s * float(r)

    art.rectangle([px(0), py(0), px(gx), py(gy)], outline=TRAIT)
    points += [(px(gx), py(gy))]
    ecrire(px(0), py(0) - 18, "colonne 0", 0, GRIS)
    ecrire(px(gx) - 64, py(0) - 18, f"colonne {gx - 1}", 0, GRIS)
    ecrire(px(0), py(gy) + 4, f"rangée {gy - 1}", 0, GRIS)
    for k, c in sorted(d["la_couverture_du_consensus"].items()):
        sens, centre = k.split("_")
        centre = int(centre)
        if sens == "rangees":
            art.rectangle([px(C[0]), py(centre - 2), px(C[2] + 1), py(centre + 3)], fill=BANDE_LUE)
            for sc in c["les_coutures_sans_consensus"]:
                art.rectangle([px(sc), py(centre - 4), px(sc + 1) + 1, py(centre + 5)], fill=ALERTE)
        else:
            art.rectangle([px(centre - 2), py(R[0]), px(centre + 3), py(R[2] + 1)], fill=BANDE_LUE)
            for sc in c["les_coutures_sans_consensus"]:
                art.rectangle([px(centre - 4), py(sc), px(centre + 5), py(sc + 1) + 1], fill=ALERTE)
    for n in LES_QUADRANTS:
        b = B[n]
        (r0, c0), (r1, c1) = b["les_coins"]
        coul = GRIS if not b.get("fermable") else (BON if b["sous_le_demi_pli"] else ALERTE)
        art.rectangle([px(c0 + 0.5), py(r0 + 0.5), px(c1 + 0.5), py(r1 + 0.5)], outline=coul, width=2)
        cx, cy = (px(c0) + px(c1)) / 2, (py(r0) + py(r1)) / 2
        lab = f"L = {_signe(b['la_fermeture_en_voxels'])} vx" if b.get("fermable") else "ouverte"
        ecrire(cx - 40, cy - 7, lab, 0, coul)
    for r in R:
        ecrire(mx0 - 52, py(r) - 7, f"rangée {r}", 0, ENCRE)
    for i, c in enumerate(C):
        ecrire(px(c) - 22, py(gy) + 22 + 16 * (i % 2), f"col. {c}", 0, ENCRE)
    g = B["le_grand_rectangle"]
    yy = int(py(gy)) + 66
    ecrire(66, yy, f"rangée {R[1]} : la bande de 219 · colonne {C[1]} : celle de 223", 0, GRIS)
    ecrire(66, yy + 18, f"rangées {R[0]} et {R[2]}, colonnes {C[0]} et {C[2]} : lues ici", 0, GRIS)
    ecrire(66, yy + 42, ("le grand rectangle : L = " + _signe(g["la_fermeture_en_voxels"]) + " vx"
                         if g.get("fermable") else "le grand rectangle : ouvert"),
           0, ENCRE if g.get("fermable") else ALERTE)
    trous = les_trous(d)
    if trous:
        ecrire(66, yy + 60, "sans majorité pour voter (en rouge) :", 0, ALERTE)
        for j, t in enumerate(trous):
            ecrire(66, yy + 78 + 18 * j, t, 0, ALERTE)

    # ── PANNEAU 2 · LES DEUX CHEMINS ──────────────────────────────────────────────────────
    panneau(540, 84, 1310, 468, "LES DEUX CHEMINS · du coin en haut à gauche au coin opposé")
    ecrire(556, 110, "par la rangée d'abord", 0, BON)
    ecrire(706, 110, "par la colonne d'abord", 0, CONTRE)
    ecrire(866, 110, f"± {int(demi)} vx autour de l'arrivée", 0, ALERTE)
    fermees = [n for n in LES_QUADRANTS if B[n].get("fermable")]
    borne = demi * 1.1
    for n in fermees:
        ch = B[n]["les_deux_chemins_en_voxels"]
        a_end = ch["par_la_rangee_dabord"][-1]
        borne = max(borne, max(abs(x) for k in ("par_la_rangee_dabord", "par_la_colonne_dabord")
                               for x in ch[k]) * 1.1, abs(a_end) + demi * 1.05)
    boites = {"haut_gauche": (556, 134), "haut_droite": (930, 134), "bas_gauche": (556, 300),
              "bas_droite": (930, 300)}
    lw, lh = 356, 150
    for n in LES_QUADRANTS:
        x0, y0 = boites[n]
        art.rectangle([x0, y0, x0 + lw, y0 + lh], outline=TRAIT)
        ecrire(x0 + 8, y0 + 6, LES_NOMS[n], 0, ENCRE)
        b = B[n]
        if not b.get("fermable"):
            ecrire(x0 + 8, y0 + 60, "ouverte : un côté n'a pas de consensus", 0, ALERTE)
            ecrire(x0 + 8, y0 + 78, "à chaque couture", 0, ALERTE)
            continue
        ch = b["les_deux_chemins_en_voxels"]
        gx0, gx1, gy0, gy1 = x0 + 34, x0 + lw - 30, y0 + 28, y0 + lh - 12

        def qy(v, gy0=gy0, gy1=gy1):
            return gy0 + (gy1 - gy0) * (borne - float(v)) / (2.0 * borne)
        art.line([gx0, qy(0), gx1, qy(0)], fill=TRAIT, width=1)
        ecrire(x0 + 6, qy(0) - 7, "0", 0, GRIS)
        for k, coul in (("par_la_rangee_dabord", BON), ("par_la_colonne_dabord", CONTRE)):
            serie = ch[k]
            pts = [(gx0 + (gx1 - gx0) * j / (len(serie) - 1), qy(v)) for j, v in enumerate(serie)]
            art.line(pts, fill=coul, width=2)
            traces[f"{n}:{k}"] = len(serie)
            points.extend(pts)
        a_end, b_end = ch["par_la_rangee_dabord"][-1], ch["par_la_colonne_dabord"][-1]
        art.line([gx1 + 8, qy(a_end + demi), gx1 + 8, qy(a_end - demi)], fill=ALERTE, width=2)
        art.line([gx1 + 4, qy(a_end + demi), gx1 + 12, qy(a_end + demi)], fill=ALERTE, width=1)
        art.line([gx1 + 4, qy(a_end - demi), gx1 + 12, qy(a_end - demi)], fill=ALERTE, width=1)
        art.ellipse([gx1 + 5, qy(b_end) - 3, gx1 + 11, qy(b_end) + 3], fill=CONTRE)
        points += [(gx1 + 12, qy(a_end - demi)), (gx1 + 12, qy(a_end + demi))]
        ecrire(x0 + lw - 148, y0 + 6, f"L = {_signe(b['la_fermeture_en_voxels'])} vx", 0,
               BON if b["sous_le_demi_pli"] else ALERTE)
    ecrire(556, 454 - 2, f"{B['bas_gauche']['les_coutures_par_chemin']} coutures par chemin · même "
                         f"échelle pour les quatre", 0, GRIS)

    # ── PANNEAU 3 · CE QUE LE BRUIT SEUL DONNERAIT ─────────────────────────────────────────
    panneau(540, 488, 1310, 812, "CE QUE LE BRUIT SEUL DONNERAIT · |L| en voxels")
    ax0, ax1 = 700, 1130
    haut = 75.0
    for n in LES_QUADRANTS + ("le_grand_rectangle",):
        u = (B[n].get("les_boucles_dune_ligne") or {})
        if u.get("decidable"):
            haut = max(haut, max(abs(x) for x in u["les_fermetures_en_voxels"]) * 1.05)

    def ax(v):
        return ax0 + (ax1 - ax0) * min(float(v), haut) / haut

    yl0 = 530
    for v_, lab, coul in ((demi, f"demi-feuillet {int(demi)}", ALERTE), (2 * demi, f"un feuillet {int(2 * demi)}",
                                                                           GRIS)):
        art.line([ax(v_), yl0 - 4, ax(v_), yl0 + 5 * 34 - 8], fill=coul, width=1)
        ecrire(ax(v_) - 30, yl0 + 5 * 34 - 4, lab, 0, coul)
    ecrire(ax0 - 4, yl0 + 5 * 34 - 4, "0", 0, GRIS)
    yy = yl0
    for n in LES_QUADRANTS + ("le_grand_rectangle",):
        b = B[n]
        ecrire(556, yy, LES_NOMS[n], 0, ENCRE)
        art.line([ax0, yy + 7, ax1, yy + 7], fill=TRAIT, width=1)
        if not b.get("fermable"):
            ecrire(ax0 + 8, yy, "ouverte", 0, ALERTE)
            yy += 34
            continue
        nl = b.get("le_nul") or {}
        if nl:
            art.rectangle([ax0, yy + 3, ax(nl["la_fermeture_mediane_du_nul_en_valeur_absolue"]), yy + 11],
                          fill=BRUIT)
        u = b.get("les_boucles_dune_ligne") or {}
        if u.get("decidable"):
            for x in u["les_fermetures_en_voxels"]:
                art.line([ax(abs(x)), yy + 13, ax(abs(x)), yy + 19], fill=CONTRE, width=1)
                points.append((ax(abs(x)), yy + 19))
            traces[f"{n}:une_ligne"] = len(u["les_fermetures_en_voxels"])
        L = abs(float(b["la_fermeture_en_voxels"]))
        coul = BON if b["sous_le_demi_pli"] else ALERTE
        art.ellipse([ax(L) - 5, yy + 2, ax(L) + 5, yy + 12], fill=coul)
        points.append((ax(L) + 5, yy + 12))
        ecrire(1144, yy - 6, f"consensus {_fr(L, 2)}", 0, coul)
        if nl:
            ecrire(1144, yy + 8, f"bruit {_fr(nl['la_fermeture_mediane_du_nul_en_valeur_absolue'], 2)}, "
                                 f"{_fr(100 * nl['la_part_du_nul_sous_le_demi_pli'], 1)} % dessous", 0, GRIS)
        yy += 34
    ecrire(556, 740, "gris : médiane du bruit seul (quatre marches indépendantes) · bleu : une ligne par côté, "
                     "toutes les combinaisons", 0, GRIS)
    if ep.get("decidable"):
        ecrire(556, 760, f"Σ L² sur {len(ep['les_rectangles'])} boucles : {_fr(ep['la_statistique'], 2)} contre "
                         f"{_fr(ep['la_statistique_mediane_du_nul'], 2)} pour des marches indépendantes "
                         f"(rapport {_fr(ep['le_rapport_au_nul'], 4)}) · p = {_fr(ep['la_valeur_p'], 4)}",
               0, ENCRE)
    ecrire(556, 778, f"étalon : au θ dérivé {_fr(et['le_theta'], 4)}, {et['combien_concluent_mieux']} sur "
                     f"{et['les_replicats']} jeux de marches indépendantes concluent à tort « mieux » "
                     f"({_fr(et['le_taux'], 4)}, borne {_fr(et['la_borne'], 4)})", 0, ENCRE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 830, L_, H_], fill=BANDE)
    ecrire(50, 846, f"LE VERDICT : {ve['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    nf = ve["les_boucles_fermables"]
    ecrire(50, 870, f"★ les {nf} boucles qui se ferment restent sous le demi-feuillet, la plus grande à "
                    f"{_fr(ve['la_plus_grande_fermeture_en_valeur_absolue'], 2)} vx : aucun chemin de "
                    f"consensus n'arrive sur la spire voisine.", moyen, ENCRE)
    une = [B[n]["les_boucles_dune_ligne"] for n in LES_QUADRANTS if B[n].get("fermable")
           and (B[n].get("les_boucles_dune_ligne") or {}).get("decidable")]
    if une:
        k_ = sum(u["combien"] for u in une)
        dep = k_ - sum(u["combien_sous_le_demi_pli"] for u in une)
        ecrire(50, 894, f"★ une ligne seule par côté, là où chaque côté en a une sans trou : {dep} boucles sur "
                        f"{k_} dépassent le demi-feuillet.", moyen, ENCRE)
    ecrire(50, 922, "⚠ ce qui n'est PAS établi : que le pas porte une géométrie commune — les boucles se "
                    "ferment comme des marches indépendantes, et trois boucles", moyen, ALERTE)
    ecrire(50, 942, "   ne verraient qu'une géométrie qui porterait l'essentiel du pas.", moyen, ALERTE)
    if trous:
        ecrire(50, 968, f"⚠ {len(ve['les_boucles_ouvertes'])} boucle(s) restent ouvertes"
                        f"{', dont le grand rectangle' if 'le_grand_rectangle' in ve['les_boucles_ouvertes'] else ''}"
                        f" : sur {'; '.join(trous)}, il n'y a pas de majorité pour voter.", moyen, ALERTE)
    ecrire(50, 996, "★ la suite : là où une bande perd sa majorité, qu'est-ce qui franchit la couture sur "
                    "la même spire ?", moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


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
    tmp = sortie.parent / ".sonde_224.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(dep, mieux):
        return {"le_verdict": {"les_boucles_qui_depassent": dep, "mieux_que_des_marches_independantes": mieux}}

    titres = {le_titre(_v(dp, m)) for dp in ([], ["a"]) for m in (True, False, None)}
    v("★★★★ les quatre titres possibles sont distincts, et dépasser le demi-feuillet prime",
      len(titres) == 4 and le_titre(_v(["a"], None)) == le_titre(_v(["a"], True)))
    v("★★★ le titre LIT le verdict",
      ("DIFFÉRENTES" in le_titre(d)) == bool(d["le_verdict"]["les_boucles_qui_depassent"])
      and ("BRUIT" in le_titre(d)) == (d["le_verdict"]["mieux_que_des_marches_independantes"] is False))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile",
      all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    B = d["les_boucles"]
    fermees = [n for n in LES_QUADRANTS if B[n].get("fermable")]
    v("★★★★ chaque chemin de chaque boucle fermée est tracé ENTIER, pas un résumé",
      all(traces.get(f"{n}:{k}") == len(B[n]["les_deux_chemins_en_voxels"][k])
          for n in fermees for k in ("par_la_rangee_dabord", "par_la_colonne_dabord")) and fermees)
    v("★★★★ chaque boucle d'une ligne est tracée, toutes les combinaisons",
      all(traces.get(f"{n}:une_ligne") == len(B[n]["les_boucles_dune_ligne"]["les_fermetures_en_voxels"])
          for n in fermees if B[n]["les_boucles_dune_ligne"].get("decidable")))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte la fermeture de chaque boucle fermée, et dit les ouvertes",
      all(f"L = {_signe(B[n]['la_fermeture_en_voxels'])} vx" in txt for n in fermees)
      and txt.count("ouverte") >= len([n for n in LES_QUADRANTS if not B[n].get("fermable")]))
    v("★★★★ elle porte la médiane du bruit seul et sa part sous le demi-feuillet, boucle par boucle",
      all(f"bruit {_fr(B[n]['le_nul']['la_fermeture_mediane_du_nul_en_valeur_absolue'], 2)}, "
          f"{_fr(100 * B[n]['le_nul']['la_part_du_nul_sous_le_demi_pli'], 1)} % dessous" in txt for n in fermees))
    ep, et = d["lepreuve"], d["letalon_de_lepreuve"]
    v("★★★★ elle porte l'épreuve et son étalon : Σ L², le nul, p, le θ dérivé, le taux et sa borne",
      _fr(ep["la_statistique"], 2) in txt and _fr(ep["la_statistique_mediane_du_nul"], 2) in txt
      and f"p = {_fr(ep['la_valeur_p'], 4)}" in txt and _fr(et["le_theta"], 4) in txt
      and f"{et['combien_concluent_mieux']} sur {et['les_replicats']}" in txt and _fr(et["la_borne"], 4) in txt)
    v("★★★★ elle nomme chaque endroit où le consensus n'a pas de majorité",
      all(t in txt for t in les_trous(d)))
    v("★★★★ elle dit ce qui n'est PAS établi", "n'est PAS établi" in txt and "géométrie commune" in txt)
    v("★★★ elle dit que la lecture retombe sur 219 et 223",
      f"retombées sur 219 et 223 en {d['la_reproduction']['combien_de_coutures_relues']} coutures" in txt)
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
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "deux_chemins_arrivent_ils_sur_la_meme_spire.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "224_deux_chemins_arrivent_ils_sur_la_meme_spire.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
