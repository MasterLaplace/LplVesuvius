"""Le bruit propre croît-il avec l'écartement ? Le nuage, l'épreuve, le triangle, la sensibilité.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LE NUAGE QUI PORTE TOUTE LA QUESTION :
un point par paire de rangées, l'écartement en abscisse et le désaccord par couture en ordonnée,
avec le niveau que `211` a mesuré à l'écartement un tracé en travers. Si le nuage est PLAT, le bruit
est propre et la hauteur de la nappe est gratuite ; s'il MONTE, la nappe a une hauteur tenable et le
recto se découpe en dalles. En bas à gauche, l'épreuve : la tendance observée contre les rebrassages
des étiquettes de rangée. Au centre, le triangle enfin sur-déterminé et ses résidus. À droite,
l'échelle de sensibilité de l'étalon — ce qui transforme un résultat négatif en BORNE.

  uv run python src/figures/figure_le_bruit_propre_croit_il_avec_lecartement.py \\
      --json docs/mesures/le_bruit_propre_croit_il_avec_lecartement.json \\
      --sortie docs/images/214_le_bruit_propre_croit_il_avec_lecartement.png
"""
from __future__ import annotations

import argparse
import json
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


def _fr(x, n: int = 3) -> str:
    """Un nombre en français, sans zéros inutiles.

    ⚠⚠ LE `rstrip` NE S'APPLIQUE QU'EN PRÉSENCE D'UNE VIRGULE : sans ce garde, `_fr(90, 0)` rend
    « 9 ». Défaut payé par `177`.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `le_bruit_propre_croit_il_avec_lecartement.py`.

    ⚠⚠⚠ LES TROIS REFUS SONT CEUX QUI FERAIENT LIRE UNE AUTRE TRANCHE SOUS CE NOM. Une échelle qui
    ne porterait qu'un seul écartement ne peut pas montrer une tendance ; un triangle qui ne serait
    pas sur-déterminé ne peut rien réfuter, ce qui est exactement la limite que cette tranche existe
    pour lever ; et une épreuve sans son compte de rebrassages écartés cache le mécanisme que la
    sonde a dû ajouter. Dans les trois cas la figure ne se dessine pas.
    """
    d = json.loads(Path(chemin).read_text())
    if not d.get("les_desaccords_par_paire", {}).get("decidable"):
        raise SystemExit("la mesure ne porte aucun désaccord décidable")
    if len(d["les_desaccords_par_paire"].get("les_ecartements_couverts") or []) < 3:
        raise SystemExit("moins de trois écartements — aucune tendance n'est lisible")
    tri = d.get("le_triangle_surdetermine") or {}
    if not tri.get("decidable") or tri.get("combien_dequations", 0) <= tri.get(
            "combien_dinconnues", 99):
        raise SystemExit("le triangle n'est pas sur-déterminé — la tranche perdrait sa réfutation")
    if "les_rebrassages_qui_refont_lobserve" not in (d.get("lepreuve") or {}):
        raise SystemExit("l'épreuve ne publie pas son compte de rebrassages écartés")
    return d


def le_titre(d: dict) -> str:
    """
    @brief Le titre RELIT le verdict publié, il ne le recalcule jamais.

    ⚠⚠⚠ Première version : le titre déduisait « la hauteur reste gratuite » du seul
    `le_bruit_croit_avec_lecartement`, alors que le JSON publie `la_hauteur_reste_gratuite`,
    qui exige EN PLUS que le modèle additif tienne. Sur le vrai rouleau les deux lectures
    divergent, et la figure se contredisait entre son titre et sa bande. Un nombre juste sous
    un mauvais nom est pire qu'un nombre absent : le titre lit le champ, point.
    """
    v = d.get("le_verdict") or {}
    croit = v.get("le_bruit_croit_avec_lecartement")
    gratuite = v.get("la_hauteur_reste_gratuite")
    if croit is None:
        return "Le bruit propre croît-il avec l'écartement ? — indécidable"
    if croit:
        return "Le bruit propre CROÎT avec l'écartement — la nappe a une hauteur tenable"
    if gratuite:
        return "Le bruit propre NE CROÎT PAS avec l'écartement — la hauteur reste gratuite"
    return "Le bruit propre NE CROÎT PAS — mais le modèle additif casse, la hauteur n'est pas gratuite"


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []
    traits: list[tuple[float, float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def replier(texte, fonte, largeur_max):
        """
        @brief Coupe un texte aux espaces pour qu'aucune ligne ne dépasse `largeur_max` pixels.

        ⚠ La longueur de la raison du verdict dépend de la branche que la mesure prend : la
        branche « le modèle additif casse » est deux fois plus longue que « rien de cette porte ».
        Une figure qui tiendrait par la brièveté d'une seule branche déborderait le jour où la
        mesure en prend une autre — et c'est le jour qui compte.
        """
        mots, lignes, courante = texte.split(" "), [], ""
        for mot in mots:
            essai = (courante + " " + mot).strip()
            if courante and art.textlength(essai, font=fonte) > largeur_max:
                lignes.append(courante)
                courante = mot
            else:
                courante = essai
        if courante:
            lignes.append(courante)
        return lignes

    def barre(x, y, largeur_max, part, hauteur, coul):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    ech = d["les_rangees_ecartees"]
    mes = d["les_desaccords_par_paire"]
    ep = d["lepreuve"]
    tri = d["le_triangle_surdetermine"]
    lon = d.get("ce_que_la_longueur_fait") or {}
    ve = d["le_verdict"]
    et = d.get("letalon") or {}
    p211 = d.get("ce_que_211_a_rendu") or {}
    niveau = p211.get("le_desaccord_par_couture_en_voxels")

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"médiane {ech['la_mediane']} · {ech['combien_de_rangees']} rangées à "
           f"±{', ±'.join(str(x) for x in ech['les_ecartements_declares'])} · "
           f"{mes['combien_de_paires']} paires · écartements de "
           f"{min(mes['les_ecartements_couverts'])} à {mes['lecartement_le_plus_grand']} · "
           f"une seule épreuve déclarée, garantie "
           f"{_fr(d['la_garantie_par_epreuve'], 4)}", petit, GRIS)

    # ---- panneau 1 : le nuage, et c'est lui qui porte la question
    x0, y0, pw, ph = 56, 122, 1248, 306
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "un point par paire — si le nuage est PLAT le bruit est propre, s'il MONTE la nappe a "
           "une hauteur", moyen, ENCRE)
    gx0, gy0, gw, gh = x0 + 62, y0 + 20, pw - 392, 228
    paires = sorted(mes["les_paires"], key=lambda q: (q["lecartement"], q["la_paire"]))
    e_max = float(mes["lecartement_le_plus_grand"])
    s_vals = [float(q["le_desaccord_par_couture_en_voxels"]) for q in paires]
    err = [float(q.get("lerreur_dechantillonnage_en_voxels") or 0.0) for q in paires]
    bas = min(min(s_vals) - max(err) * 2.0, float(niveau or min(s_vals))) * 0.94
    haut = max(max(s_vals) + max(err) * 2.0, float(niveau or max(s_vals))) * 1.06
    if haut <= bas:
        haut = bas + 1.0

    def _px(e):
        return gx0 + gw * (float(e) / e_max if e_max > 0 else 0.0)

    def _py(s):
        return gy0 + gh * (1.0 - (float(s) - bas) / (haut - bas))

    art.line([gx0, gy0, gx0, gy0 + gh], fill=TRAIT, width=1)
    art.line([gx0, gy0 + gh, gx0 + gw, gy0 + gh], fill=TRAIT, width=1)
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = gy0 + gh * (1.0 - frac)
        art.line([gx0 - 4, yy, gx0, yy], fill=TRAIT, width=1)
        ecrire(gx0 - 52, yy - 7, _fr(bas + frac * (haut - bas), 2), petit, GRIS)
    for e in sorted({int(q["lecartement"]) for q in paires}):
        art.line([_px(e), gy0 + gh, _px(e), gy0 + gh + 4], fill=TRAIT, width=1)
    for e in (min(mes["les_ecartements_couverts"]), int(e_max)):
        ecrire(_px(e) - 6, gy0 + gh + 9, str(e), petit, GRIS)
    # ⚠⚠⚠ LE NIVEAU DE `211` EST TRACE, ET C'EST LA PREDICTION POSEE D'AVANCE : sous le modele le
    # nuage doit rester dessus. Le dessiner APRES les points le ferait passer par-dessus eux.
    if niveau is not None:
        yn = _py(float(niveau))
        art.line([gx0, yn, gx0 + gw, yn], fill=CONTRE, width=2)
        traits.append((gx0, yn, gx0 + gw))
        ecrire(gx0 + 64, gy0 + gh + 9,
               f"`211` à l'écartement 1 : {_fr(niveau, 4)}", petit, CONTRE)
    for q, sv, ev in zip(paires, s_vals, err):
        px, py = _px(q["lecartement"]), _py(sv)
        if ev > 0:
            art.line([px, _py(sv - ev), px, _py(sv + ev)], fill=TRAIT, width=1)
        art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=ENCRE)
        points.append((px, py))
    ecrire(gx0 - 44, gy0 - 16, "voxels", petit, GRIS)
    ecrire(gx0 + gw - 226, gy0 + gh + 9, "écartement (rangées)", petit, GRIS)

    bx = x0 + pw - 318
    ecrire(bx, gy0 + 4, "CE QUE LE NUAGE DIT", petit, ENCRE)
    for i, (lab, val, coul) in enumerate((
            ("au plus petit écartement",
             f"{_fr((ve.get('au_plus_petit_ecartement') or {}).get('le_desaccord_par_couture_en_voxels'), 4)} "
             f"vx sur {(ve.get('au_plus_petit_ecartement') or {}).get('les_coutures_communes')} coutures",
             ENCRE),
            ("au plus grand écartement",
             f"{_fr((ve.get('au_plus_grand_ecartement') or {}).get('le_desaccord_par_couture_en_voxels'), 4)} "
             f"vx sur {(ve.get('au_plus_grand_ecartement') or {}).get('les_coutures_communes')} coutures",
             ENCRE),
            ("le plus petit / le plus grand",
             f"{_fr(ve.get('le_desaccord_le_plus_petit_en_voxels'), 4)} — "
             f"{_fr(ve.get('le_desaccord_le_plus_grand_en_voxels'), 4)} vx", GRIS),
            ("contrôle : la longueur suit-elle ?",
             f"tendance {_fr(lon.get('la_tendance_de_la_longueur'), 4)}", GRIS))):
        ecrire(bx, gy0 + 30 + i * 40, lab, petit, GRIS)
        ecrire(bx, gy0 + 46 + i * 40, val, moyen, coul)

    # ---- panneau 2 : l'épreuve
    y1 = y0 + ph + 44
    p2x, p2w, p2h = 56, 404, 268
    art.rectangle([p2x, y1, p2x + p2w, y1 + p2h], outline=TRAIT, width=1)
    cadres.append((p2x, y1, p2x + p2w, y1 + p2h))
    ecrire(p2x, y1 - 24, "l'épreuve : les étiquettes rebrassées", moyen, ENCRE)
    obs = float(ep.get("la_tendance_observee") or 0.0)
    nul_max = float(ep.get("la_tendance_du_nul_la_plus_forte") or 0.0)
    nul_med = float(ep.get("la_tendance_du_nul_median") or 0.0)
    ax0, ay0, aw = p2x + 26, y1 + 44, p2w - 58
    art.line([ax0, ay0 + 44, ax0 + aw, ay0 + 44], fill=TRAIT, width=1)
    for val, coul, lab, dy in ((nul_med, GRIS, "nul médian", 52),
                               (nul_max, CONTRE, "nul le plus fort", 72),
                               (obs, BON if ep.get("ca_croit_avec_lecartement") else ALERTE,
                                "observé", 20)):
        xx = ax0 + aw * (float(val) + 1.0) / 2.0
        art.line([xx, ay0 + 34, xx, ay0 + 54], fill=coul, width=3)
        traits.append((xx, ay0 + 34, xx))
        ecrire(min(xx + 6, ax0 + aw - 96), ay0 + dy, f"{lab} {_fr(val, 4)}", petit, coul)
    ecrire(ax0 - 8, ay0 + 62, "−1", petit, GRIS)
    ecrire(ax0 + aw - 8, ay0 + 62, "+1", petit, GRIS)
    ecrire(p2x + 18, y1 + 138,
           f"{ep.get('les_tirages_au_moins_aussi_forts')} rebrassage(s) sur "
           f"{ep.get('tirages')} au moins aussi forts", moyen,
           BON if ep.get("ca_croit_avec_lecartement") else ENCRE)
    ecrire(p2x + 18, y1 + 160,
           f"{ep.get('les_rebrassages_qui_refont_lobserve')} écarté(s) : ils REFONT les mêmes "
           f"écartements", petit, GRIS)
    ecrire(p2x + 18, y1 + 178,
           f"la suite des positions porte une symétrie : "
           f"{'oui' if ep.get('la_suite_des_positions_a_une_symetrie') else 'non'}", petit, GRIS)
    ecrire(p2x + 18, y1 + 204,
           f"{'★' if ep.get('ca_croit_avec_lecartement') else '✗'}  "
           f"{'LE DÉSACCORD CROÎT' if ep.get('ca_croit_avec_lecartement') else 'AUCUNE TENDANCE'}",
           moyen, ALERTE if ep.get("ca_croit_avec_lecartement") else BON)
    ecrire(p2x + 18, y1 + 228,
           "épreuve à UN sens, déclarée d'avance", petit, GRIS)

    # ---- panneau 3 : le triangle enfin sur-déterminé
    p3x, p3w = 484, 404
    art.rectangle([p3x, y1, p3x + p3w, y1 + p2h], outline=TRAIT, width=1)
    cadres.append((p3x, y1, p3x + p3w, y1 + p2h))
    ecrire(p3x, y1 - 24, "le triangle : enfin sur-déterminé", moyen, ENCRE)
    ecrire(p3x + 18, y1 + 16,
           f"{tri['combien_dequations']} équations pour {tri['combien_dinconnues']} inconnues",
           moyen, ENCRE)
    ecrire(p3x + 18, y1 + 36,
           "`212` en avait 3 pour 3 : exactement déterminé, donc irréfutable", petit, GRIS)
    bruits = tri.get("les_bruits_propres_en_voxels2") or {}
    bmax = max([abs(float(x)) for x in bruits.values()] + [1e-9])
    for i, (nom, val) in enumerate(sorted(bruits.items(), key=lambda kv: int(kv[0]))):
        yy = y1 + 56 + i * 14
        ecrire(p3x + 18, yy - 3, str(nom), petit, GRIS)
        barre(p3x + 66, yy, 150, abs(float(val)) / bmax, 9,
              ALERTE if float(val) < 0 else CONTRE)
        ecrire(p3x + 226, yy - 3, f"{_fr(val, 4)} vx²", petit, ENCRE)
    yr = y1 + 56 + max(1, len(bruits)) * 14 + 12
    ecrire(p3x + 18, yr,
           f"pire résidu {_fr(tri.get('le_pire_residu_en_erreurs'), 4)} erreurs "
           f"({tri.get('la_paire_du_pire_residu_en_erreurs')})", moyen, ENCRE)
    ecrire(p3x + 18, yr + 20,
           f"résidu médian {_fr(tri.get('le_residu_median_en_erreurs'), 4)} erreurs · "
           f"l'erreur est dérivée des coutures", petit, GRIS)
    ecrire(p3x + 18, yr + 38,
           f"{'★' if tri.get('le_modele_tient_aux_erreurs') else '✗'}  "
           f"{'LE MODÈLE ADDITIF TIENT' if tri.get('le_modele_tient_aux_erreurs') else 'LE MODÈLE ADDITIF CASSE'}",
           moyen, BON if tri.get("le_modele_tient_aux_erreurs") else ALERTE)
    ecrire(p3x + 18, yr + 56,
           f"variance négative : "
           f"{'OUI — réfuté' if tri.get('le_modele_est_refute_par_une_variance_negative') else 'aucune'}",
           petit, ALERTE if tri.get("le_modele_est_refute_par_une_variance_negative") else GRIS)

    # ---- panneau 4 : l'échelle de sensibilité
    p4x, p4w = 912, 392
    art.rectangle([p4x, y1, p4x + p4w, y1 + p2h], outline=TRAIT, width=1)
    cadres.append((p4x, y1, p4x + p4w, y1 + p2h))
    ecrire(p4x, y1 - 24, "l'étalon : jusqu'où l'épreuve voit-elle ?", moyen, ENCRE)
    ecrire(p4x + 18, y1 + 18,
           "facteur : par combien le CARRÉ du désaccord croît sur l'échelle", petit, GRIS)
    plus_petit = et.get("le_plus_petit_facteur_vu")
    for i, b in enumerate(et.get("lechelle_de_sensibilite") or []):
        yy = y1 + 40 + i * 22
        vu = int(b["les_vus"]) >= int(b["replicats"])
        ecrire(p4x + 18, yy - 2, f"×{b['le_facteur']}", petit,
               BON if vu else GRIS)
        barre(p4x + 54, yy + 1, 168, float(b["les_vus"]) / float(b["replicats"]), 9,
              BON if vu else GRIS)
        ecrire(p4x + 232, yy - 2,
               f"{b['les_vus']}/{b['replicats']} · croissance "
               f"{_fr(b['la_croissance_en_voxels'], 3)}", petit, ENCRE if vu else GRIS)
    ys = y1 + 40 + len(et.get("lechelle_de_sensibilite") or []) * 22 + 12
    ecrire(p4x + 18, ys,
           f"plus petit facteur vu partout : "
           f"{('×' + str(plus_petit)) if plus_petit else 'aucun'} · monotone "
           f"{'oui' if et.get('la_sensibilite_est_monotone') else 'NON'}", moyen, ENCRE)
    ecrire(p4x + 18, ys + 22,
           f"faux {et.get('les_faux')}/{et.get('les_replicats_du_refus')} = "
           f"{_fr(et.get('le_taux_de_faux'), 4)} · garantie {_fr(et.get('la_garantie'), 4)}",
           petit, GRIS)
    ecrire(p4x + 18, ys + 40,
           f"contrôle aveugle (dérive partagée ×10) : {_fr(et.get('le_taux_du_controle_aveugle'), 4)}",
           petit, GRIS)
    pu = et.get("la_regle_plus_puissante") or {}
    if pu.get("le_taux_de_faux") is not None:
        vus_pu = sum(int(b["les_vus"]) for b in (pu.get("les_vus_par_facteur") or []))
        tot = sum(int(b["replicats"]) for b in (pu.get("les_vus_par_facteur") or []))
        vus_g = sum(int(b["les_vus"]) for b in (et.get("lechelle_de_sensibilite") or []))
        ecrire(p4x + 18, ys + 58,
               f"la plus puissante voit {vus_pu}/{tot} contre {vus_g}/{tot} · faux "
               f"{pu.get('les_faux')}/{pu.get('les_replicats_du_refus')} = "
               f"{_fr(pu.get('le_taux_de_faux'), 4)}", petit, CONTRE)
    ecrire(p4x + 18, ys + 80,
           f"{'★' if et.get('letalon_separe') else '✗'}  "
           f"{"L'ÉTALON SÉPARE" if et.get('letalon_separe') else "L'ÉTALON NE SÉPARE PAS"}",
           moyen, BON if et.get("letalon_separe") else ALERTE)

    # ---- la bande : le verdict
    yb = y1 + p2h + 34
    art.rectangle([0, yb, L, H], fill=BANDE)
    croit = ve.get("le_bruit_croit_avec_lecartement")
    gratuite = ve.get("la_hauteur_reste_gratuite")
    ecrire(56, yb + 20,
           f"{'✗' if croit else '★'}  "
           f"{'LE DÉSACCORD CROÎT AVEC L’ÉCARTEMENT' if croit else 'LE DÉSACCORD NE DÉPEND PAS DE L’ÉCARTEMENT'}"
           f" — sur {ve.get('combien_de_paires')} paires et "
           f"{ve.get('combien_decartements')} écartements, de "
           f"{(ve.get('lechelle_des_ecartements') or ['—', '—'])[0]} à "
           f"{(ve.get('lechelle_des_ecartements') or ['—', '—'])[1]} rangées.",
           moyen, ALERTE if croit else BON)
    ecrire(56, yb + 44,
           f"{'★' if gratuite else '✗'}  LA HAUTEUR DE LA NAPPE "
           f"{'RESTE GRATUITE' if gratuite else 'N’EST PLUS GRATUITE'} : "
           f"{ve.get('ce_qui_reste_a_mesurer')}.", moyen,
           BON if gratuite else ALERTE)
    lignes = replier(f"     {ve.get('pourquoi_il_reste_a_mesurer')}.", moyen, L - 112)
    for i, ligne in enumerate(lignes):
        ecrire(56, yb + 68 + i * 22, ligne, moyen, ENCRE)
    yq = yb + 68 + len(lignes) * 22 + 2
    if plus_petit:
        ecrire(56, yq,
               f"⚠ ET LA BORNE EST CE QUE L’ÉTALON REND : l'épreuve voit une croissance qui "
               f"multiplie le carré du désaccord par {plus_petit} d'un bout à l'autre de "
               f"l'échelle — donc « pas de croissance » veut dire « moins que ça ».", petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres, traits


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
            print(f"  ÉCHEC {nom}{(' — ' + detail) if detail else ''}")

    import tempfile  # noqa: PLC0415

    d = lire(json_path)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        chemin, poses, cadres, points, barres, traits = dessiner(d, t / "a.png")
        v("★★ la figure est écrite", chemin.exists() and chemin.stat().st_size > 20000,
          str(chemin.stat().st_size if chemin.exists() else 0))
        # ⚠⚠ LE RENDU EST BIT POUR BIT REPRODUCTIBLE : sans ça, comparer deux versions d'une figure
        # ne dirait rien, et la garde de fraîcheur du dépôt serait un tirage au sort.
        dessiner(d, t / "b.png")
        v("★★★ le rendu est bit pour bit identique d'une passe à l'autre",
          (t / "a.png").read_bytes() == (t / "b.png").read_bytes())

        from PIL import Image as _I  # noqa: PLC0415
        im = _I.open(t / "a.png")
        v("★★ la toile fait 1360×980", im.size == (1360, 980), str(im.size))
        v("★★★ la figure porte cinq cadres — quatre panneaux et la bande",
          len(cadres) == 4, str(len(cadres)))

        v("★★★ aucun texte ne déborde de l'image",
          not textes_debordants(poses, im.size[0]),
          str(textes_debordants(poses, im.size[0]))[:200])
        v("★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
          str(textes_hors_cadre(poses, cadres))[:200])
        v("★★★ aucun texte n'en recouvre un autre",
          not textes_qui_se_recouvrent(poses),
          str(textes_qui_se_recouvrent(poses))[:200])
        # ⚠⚠⚠ `⭐` ET `⛔` NE SONT PAS DANS LA POLICE DÉPLOYÉE, et un glyphe manquant se dessine en
        # carré vide sans que rien ne le signale. La garde lit la police, pas une liste tenue à la
        # main.
        manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
        v("★★★★ aucun glyphe ne manque à la police déployée", not manquants, str(manquants[:5]))

        # ⚠⚠ LE TROU ENTRE LE BAS D'UN PANNEAU ET LA BANDE : un texte qui y tombe flotte sans
        # rattachement, et aucune des gardes précédentes ne le voit.
        bas_panneaux = max(c[3] for c in cadres)
        bande = None
        for (x, y, texte, f) in poses:
            if texte.startswith("✗  ") or texte.startswith("★  "):
                if y > bas_panneaux:
                    bande = min(bande, y) if bande else y
        flottants = [(x, y, t_) for (x, y, t_, _f) in poses
                     if bas_panneaux < y < (bande or 10 ** 9) - 2]
        v("★★★★ aucun texte ne tombe entre le bas d'un panneau et la bande",
          not flottants, str(flottants[:2]))

    # ⭐⭐⭐⭐ LA GARDE QUI COMPTE : L'ÉCHELLE SUIT LES DONNÉES. `212` a payé une garde qui ne pouvait
    # pas échouer — une hauteur posée en multiple d'une constante faisait retomber la bande au même
    # pixel quelle que soit la valeur publiée. Ici l'échelle verticale est dérivée des désaccords,
    # donc DÉPLACER un désaccord DOIT déplacer le trait de `211`, et la sonde le mesure.
    def _trait_211(dd):
        import tempfile as _t  # noqa: PLC0415
        with _t.TemporaryDirectory() as td:
            _c, _p, _ca, _pt, _b, tr = dessiner(dd, Path(td) / "x.png")
        return round(tr[0][1], 3) if tr else None

    y_ref = _trait_211(d)
    bouge = json.loads(json.dumps(d))
    for q in bouge["les_desaccords_par_paire"]["les_paires"]:
        q["le_desaccord_par_couture_en_voxels"] = float(
            q["le_desaccord_par_couture_en_voxels"]) * 2.0
    y_bouge = _trait_211(bouge)
    v("★★★★ l'échelle verticale est DÉRIVÉE des désaccords : les doubler déplace le trait de `211`",
      y_ref is not None and y_bouge is not None and abs(y_ref - y_bouge) > 8.0,
      f"{y_ref} contre {y_bouge}")

    # ⚠⚠⚠ ET LES NOMBRES DESSINÉS SONT CEUX DU JSON, avec les décimales du PRODUCTEUR — ni
    # complétées ni rognées. Un nombre juste sous un mauvais arrondi est un nombre faux.
    with tempfile.TemporaryDirectory() as tmp:
        _c, poses2, _ca, _pt, _b, _tr = dessiner(d, Path(tmp) / "c.png")
    tout = " ".join(t for (_x, _y, t, _f) in poses2)
    ve = d["le_verdict"]
    ep = d["lepreuve"]
    tri = d["le_triangle_surdetermine"]
    for nom, val, n in (
            ("le désaccord le plus petit", ve.get("le_desaccord_le_plus_petit_en_voxels"), 4),
            ("le désaccord le plus grand", ve.get("le_desaccord_le_plus_grand_en_voxels"), 4),
            ("la tendance observée", ep.get("la_tendance_observee"), 4),
            ("le nul le plus fort", ep.get("la_tendance_du_nul_la_plus_forte"), 4),
            ("le pire résidu", tri.get("le_pire_residu_en_erreurs"), 4)):
        v(f"★★★ {nom} est dessiné tel que le producteur le publie",
          val is None or _fr(val, n) in tout, f"{nom} = {_fr(val, n)}")
    v("★★★ le compte d'équations et d'inconnues du triangle est dessiné",
      f"{tri['combien_dequations']} équations pour {tri['combien_dinconnues']} inconnues" in tout)
    v("★★★ le niveau que `211` a mesuré est dessiné, jamais recalculé",
      (d.get("ce_que_211_a_rendu") or {}).get("le_desaccord_par_couture_en_voxels") is None
      or _fr((d["ce_que_211_a_rendu"])["le_desaccord_par_couture_en_voxels"], 4) in tout)
    v("★★★ le compte de rebrassages écartés est dessiné",
      str(ep.get("les_rebrassages_qui_refont_lobserve")) in tout)
    v("★★★★ le verdict dessiné est celui du JSON, et il emploie ★ ou ✗ et jamais ⭐ ni ⛔",
      ("★" in tout or "✗" in tout) and "⭐" not in tout and "⛔" not in tout)
    v("★★★ ce qui reste à mesurer et POURQUOI sont dessinés séparément",
      str(ve.get("ce_qui_reste_a_mesurer")) in tout
      and str(ve.get("pourquoi_il_reste_a_mesurer")) in tout)

    # ⚠⚠⚠ LES TROIS REFUS DE `lire` SONT EXERCÉS : une garde qu'on n'essaie pas de franchir est
    # une garde dont on ne sait pas si elle est là.
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        for nom, mutation in (
                ("une échelle d'un seul écartement",
                 lambda x: x["les_desaccords_par_paire"].__setitem__(
                     "les_ecartements_couverts", [1])),
                ("un triangle exactement déterminé",
                 lambda x: x["le_triangle_surdetermine"].__setitem__("combien_dequations", 3)),
                ("une épreuve sans compte de rebrassages",
                 lambda x: x["lepreuve"].pop("les_rebrassages_qui_refont_lobserve", None)),
                ("des désaccords indécidables",
                 lambda x: x["les_desaccords_par_paire"].__setitem__("decidable", False))):
            casse = json.loads(json.dumps(d))
            mutation(casse)
            p_ = t / "casse.json"
            p_.write_text(json.dumps(casse, ensure_ascii=False))
            try:
                lire(p_)
                ok = False
            except SystemExit:
                ok = True
            v(f"★★★★ la figure REFUSE {nom}", ok)

    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "le_bruit_propre_croit_il_avec_lecartement.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "214_le_bruit_propre_croit_il_avec_lecartement.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
