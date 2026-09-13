#!/usr/bin/env python3
"""La course, vue en trois dimensions pendant qu'elle dure.

⭐⭐⭐⭐ **Pourquoi cette figure existe, et ce qu'elle ne remplace pas.** Une course de seize bandes
n'écrivait son brouillon qu'à la fin de chaque bande, et ne rendait ses positions qu'à la fin :
pendant quarante minutes il n'y avait rien à regarder qu'une barre de progression. La trace de
`jusquou_va_t_il_si_on_le_laisse.py --trace` dit désormais chaque pas ; cette figure la relit et
dessine les trajectoires **dans un même repère**, celui du volume, sous une caméra qu'on tourne.

  ⚠⚠ Ce N'EST PAS la projection de `figure_le_marcheur_derive_t_il.py`, et c'est délibéré. Celle-là
  aplatit CHAQUE marche dans SON plan le plus défavorable pour juger sa rectitude ; seize marches y
  perdent toute géométrie relative. Ici la question est l'inverse — OÙ les marches sont les unes par
  rapport aux autres dans le rouleau — donc la projection est une caméra orthographique commune,
  et rien d'autre. Deux questions, deux projections ; une seule d'entre elles serait fausse pour
  l'autre.

  ⭐⭐⭐ Le trait porte les états que `115` et `129` ont nommés : un pas **confirmé** est plein, un
  pas non confirmé est gris, un pas pris **contre la garde** (`oriente` faux) est ambre, un pas
  **aveugle** (`rien_lu`) est en alerte. La profondeur est rendue par l'ordre de peinture (le
  lointain d'abord) et par un léger fondu vers le fond.

  ⚠⚠ RENDU PUR D'UN INSTANTANÉ. La figure ouvre la trace en lecture, ne l'écrit jamais, et une
  ligne coupée en cours d'écriture est ignorée plutôt que refusée : c'est ce qui autorise à relire
  une course PENDANT qu'elle tourne sans pouvoir la perturber. `--suivre N` re-rend toutes les N
  secondes ; `--tourner D` ajoute D degrés d'azimut à chaque rendu, ce qui est ce qui fait voir le
  relief à l'œil.

  uv run python src/figures/figure_la_course_en_3d.py \\
      --trace docs/mesures/la_course_a_cap.jsonl \\
      --sortie docs/images/133_la_course_en_3d.png
  uv run python src/figures/figure_la_course_en_3d.py --trace /tmp/course.jsonl \\
      --sortie /tmp/course.png --suivre 10 --tourner 3
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (police, textes_debordants, textes_hors_cadre,  # noqa: E402
                            textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
CONFIRME = (60, 110, 90)
REFUSE = (150, 152, 156)
AVEUGLE = (176, 62, 62)
GARDE = (196, 140, 60)
DEPART = (86, 104, 132)
AZIMUT = 35.0
ELEVATION = 25.0


def lire(chemin: Path) -> dict:
    """La trace, ligne par ligne, telle qu'elle est à cet instant.

    ⚠⚠ Une ligne qui ne se parse pas est IGNORÉE et comptée, jamais refusée : la course écrit
    pendant qu'on lit, donc la dernière ligne peut être coupée. Refuser ferait échouer exactement
    le rendu qu'on veut, celui d'une course en train de tourner. Mais un fichier sans en-tête
    `course` est refusé — ce n'est pas une trace, ou pas encore.
    """
    marches: dict[int, dict] = {}
    entete, coupees = None, 0
    for brute in chemin.read_text(encoding="utf-8").splitlines():
        try:
            l = json.loads(brute)
        except json.JSONDecodeError:
            coupees += 1
            continue
        q = l.get("quoi")
        if q == "course":
            entete = l
        elif q == "depart":
            marches[int(l["marche"])] = {"bande": l.get("bande"), "rayon_mm": l.get("rayon_mm"),
                                         "points": [l["position_zyx"]], "confirme": [],
                                         "oriente": [], "rien_lu": [], "fin": None}
        elif q == "pas":
            m = marches.get(int(l["marche"]))
            if m is None:
                coupees += 1
                continue
            m["points"].append(l["position_zyx"])
            m["confirme"].append(bool(l.get("confirme")))
            m["oriente"].append(bool(l.get("oriente")))
            m["rien_lu"].append(bool(l.get("rien_lu")))
        elif q == "fin":
            m = marches.get(int(l["marche"]))
            if m is not None:
                m["fin"] = l.get("fin")
    if entete is None:
        raise ValueError(f"{chemin} : aucune ligne `course` — ce n'est pas une trace")
    return {"source": chemin.name, "entete": entete, "coupees": coupees,
            "marches": [marches[k] for k in sorted(marches)]}


def camera(azimut_deg: float, elevation_deg: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Les trois axes d'une caméra orthographique : droite, haut, et la profondeur.

    ⚠ Les positions sont en (z, y, x) et l'axe du rouleau est z, donc le « haut » du monde est z.
    De face (azimut 0, élévation 0) la caméra regarde le long de +y, +x va à droite et +z en
    haut ; l'azimut tourne autour de z, une élévation positive regarde D'EN HAUT. Orthographique
    et non perspective : une perspective rendrait deux longueurs égales inégales selon leur
    profondeur, ce qui est le mensonge qu'une figure de trajectoires ne peut pas se permettre.

    ⚠ Ma première version regardait le long de +x et vers le HAUT pour une élévation positive :
    les deux sont des conventions, mais la seconde met le point le plus haut le plus LOIN, donc
    le relief se lisait à l'envers. C'est la batterie qui l'a dit, pas la relecture.
    """
    az, el = np.radians(azimut_deg), np.radians(elevation_deg)
    # ⚠ En (z, y, x) : la profondeur regarde VERS la scène, et d'en haut quand `el` > 0.
    vue = np.array([-np.sin(el), np.cos(el) * np.cos(az), np.cos(el) * np.sin(az)])
    haut_monde = np.array([1.0, 0.0, 0.0])
    droite = np.cross(haut_monde, vue)
    n = float(np.linalg.norm(droite))
    if n < 1e-9:
        droite = np.array([0.0, 1.0, 0.0])
    else:
        droite = droite / n
    haut = np.cross(vue, droite)
    return droite, haut, vue


def projeter(points: np.ndarray, azimut_deg: float, elevation_deg: float) -> np.ndarray:
    """(N, 3) en (z, y, x) → (N, 3) en (écran x, écran y, profondeur).

    ⚠ La profondeur CROÎT en s'éloignant de la caméra : le plus grand est le plus lointain, et
    c'est lui qu'on peint d'abord.
    """
    droite, haut, vue = camera(azimut_deg, elevation_deg)
    return np.stack([points @ droite, points @ haut, points @ vue], axis=1)


def dessiner(d: dict, sortie: Path, azimut: float = AZIMUT,
             elevation: float = ELEVATION) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés.

    ⚠ La taille du voxel vient de l'EN-TÊTE de la trace, jamais d'une option : un nombre tapé à
    la main est un nombre faux un jour sur deux, et le premier rendu en a reçu 7,91 pour 2,4.
    Une trace qui ne la porte pas écrit l'emprise en voxels, ce qui est vrai.
    """
    marches = d["marches"]
    e = d["entete"]
    voxel_um = e.get("voxel_um")
    L, H = 1180, 720
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    pas_total = sum(len(m["confirme"]) for m in marches)
    conf = sum(sum(m["confirme"]) for m in marches)
    aveugles = sum(sum(m["rien_lu"]) for m in marches)
    contre = sum(sum(1 for o, a in zip(m["oriente"], m["rien_lu"]) if not o and not a)
                 for m in marches)
    finies = sum(1 for m in marches if m["fin"] is not None)
    bandes = e.get("bandes")
    en_cours = "course finie" if bandes and finies >= bandes else "course en cours"
    ecrire(28, 20, "La course, vue en trois dimensions", gros, ENCRE)
    ecrire(28, 46, f"{e.get('fragment', '?')} · plafond {e.get('pas_max')} pas · mémoire du cap "
                   f"{e.get('memoire_du_cap', 0)} · {en_cours}", petit, GRIS)

    # ── Le panneau 3D ────────────────────────────────────────────────────────
    x0, y0, pw, ph = 40, 100, 800, 560
    cadre = (x0, y0, x0 + pw, y0 + ph)
    tous = [np.asarray(m["points"], dtype=float) for m in marches if len(m["points"]) >= 1]
    points_ecran: list[tuple[float, float]] = []
    if tous:
        nuage = np.concatenate(tous)
        centre = nuage.mean(axis=0)
        # ⚠⚠ L'emprise est celle de la BOÎTE ENGLOBANTE PROJETÉE, pas du nuage : la boîte est
        # dessinée, et une boîte vue de biais déborde de la projection de ce qu'elle contient.
        # Le premier rendu réel cadrait sur les points et la boîte sortait du panneau pour aller
        # rayer le texte de droite — le piège que `figure_le_marcheur_derive_t_il` a payé en 2D.
        lo, hi = nuage.min(axis=0) - centre, nuage.max(axis=0) - centre
        coins = np.array([[a, b, c] for a in (lo[0], hi[0]) for b in (lo[1], hi[1])
                          for c in (lo[2], hi[2])])
        pc = projeter(coins, azimut, elevation)
        pr = projeter(nuage - centre, azimut, elevation)
        xmin, xmax = float(pc[:, 0].min()), float(pc[:, 0].max())
        ymin, ymax = float(pc[:, 1].min()), float(pc[:, 1].max())
        zmin, zmax = float(pr[:, 2].min()), float(pr[:, 2].max())
        # ⚠ Même échelle sur les deux axes, pour la raison de toujours : étirer un axe rend une
        # ondulation aussi visible qu'un demi-tour.
        ech = min((pw - 40) / max(1e-9, xmax - xmin), (ph - 40) / max(1e-9, ymax - ymin))
        ox = x0 + pw / 2 - (xmin + xmax) / 2 * ech
        oy = y0 + ph / 2 + (ymin + ymax) / 2 * ech

        def ecran(p):
            return ox + p[0] * ech, oy - p[1] * ech

        # La boîte englobante en 3D, fine, pour que l'œil ait un repère de profondeur.
        points_ecran.extend(ecran(q) for q in pc)
        for i in range(8):
            for j in range(i + 1, 8):
                if sum(1 for k in range(3) if coins[i][k] != coins[j][k]) == 1:
                    art.line([ecran(pc[i]), ecran(pc[j])], fill=TRAIT, width=1)
        # Le tripode des axes, en bas à gauche du panneau, projeté par la même caméra.
        tri_o = (x0 + 46, y0 + ph - 46)
        for vec, nom in (((1.0, 0.0, 0.0), "z (axe)"), ((0.0, 1.0, 0.0), "y"),
                         ((0.0, 0.0, 1.0), "x")):
            v = projeter(np.asarray([vec]), azimut, elevation)[0]
            bout = (tri_o[0] + v[0] * 30, tri_o[1] - v[1] * 30)
            # ⚠ Un axe vu par le bout se projette en un point : son trait n'a rien à montrer et
            # son étiquette tomberait sur celle d'un voisin (vu de dessus, « z » sur « x »).
            if float(np.hypot(v[0], v[1])) < 0.2:
                continue
            art.line([tri_o, bout], fill=GRIS, width=1)
            ecrire(int(bout[0]) + 3, int(bout[1]) - 6, nom, petit, GRIS)

        # ⚠⚠ Le lointain d'abord : les segments sont triés par profondeur avant d'être peints,
        # sinon un trait derrière un autre passe devant lui et le relief se lit à l'envers.
        segments = []
        for m in marches:
            p = projeter(np.asarray(m["points"], dtype=float) - centre, azimut, elevation)
            for k in range(1, len(p)):
                coul = (AVEUGLE if m["rien_lu"][k - 1]
                        else GARDE if not m["oriente"][k - 1]
                        else CONFIRME if m["confirme"][k - 1] else REFUSE)
                segments.append((float((p[k - 1, 2] + p[k, 2]) / 2), p[k - 1], p[k], coul))
            points_ecran.extend(ecran(q) for q in p)
            # Le départ, marqué, parce qu'une marche d'un seul point n'aurait sinon rien à voir.
            a = ecran(p[0])
            art.ellipse([a[0] - 3, a[1] - 3, a[0] + 3, a[1] + 3], outline=DEPART, width=1)
        segments.sort(key=lambda s: -s[0])
        prof = max(1e-9, zmax - zmin)
        for z, a, b, coul in segments:
            # Le fondu vers le fond : jusqu'à 45 % vers la couleur du papier pour le plus
            # LOINTAIN. ⚠ Ma première version fondait le plus proche — le contrôle « le point le
            # plus haut est le plus proche » l'a dit, parce qu'il fixe le sens de la profondeur.
            t = 0.45 * (z - zmin) / prof
            c = tuple(int(coul[i] * (1 - t) + FOND[i] * t) for i in range(3))
            art.line([ecran(a), ecran(b)], fill=c, width=2)
        etendue_vx = hi - lo
        if voxel_um:
            ecrire(x0, y0 + ph + 8, f"emprise {etendue_vx[2] * voxel_um / 1000:.1f} × "
                                    f"{etendue_vx[1] * voxel_um / 1000:.1f} × "
                                    f"{etendue_vx[0] * voxel_um / 1000:.1f} mm (x, y, z)",
                   petit, GRIS)
        else:
            ecrire(x0, y0 + ph + 8, f"emprise {etendue_vx[2]:.0f} × {etendue_vx[1]:.0f} × "
                                    f"{etendue_vx[0]:.0f} voxels (x, y, z)", petit, GRIS)
    else:
        ecrire(x0 + 20, y0 + 20, "aucune marche n'a encore posé de point", moyen, GRIS)
    ecrire(x0, y0 - 22, f"azimut {azimut:.0f}° · élévation {elevation:.0f}° · orthographique",
           petit, GRIS)

    # ── Le panneau de droite : où en est la course ───────────────────────────
    x1, y1 = x0 + pw + 40, y0
    pw2 = L - x1 - 28
    ecrire(x1, y1 - 22, "où en est la course", moyen, ENCRE)
    yl = y1 + 6
    lignes = [(f"{len(marches)} marche(s) parties" + (f" sur {bandes}" if bandes else ""), ENCRE),
              (f"{finies} finie(s)", ENCRE),
              (f"{pas_total} pas posés", ENCRE),
              (f"{conf} confirmés" + (f" ({conf / pas_total:.1%})" if pas_total else ""),
               CONFIRME),
              (f"{contre} contre la garde", GARDE if contre else GRIS),
              (f"{aveugles} aveugle(s)", AVEUGLE if aveugles else GRIS)]
    if d["coupees"]:
        lignes.append((f"{d['coupees']} ligne(s) coupée(s), ignorée(s)", GRIS))
    for texte, coul in lignes:
        ecrire(x1, yl, texte, petit, coul)
        yl += 18
    yl += 10
    ecrire(x1, yl, "légende du trait", petit, GRIS)
    yl += 18
    for coul, nom in ((CONFIRME, "pas confirmé"), (REFUSE, "pas non confirmé"),
                      (GARDE, "pas contre la garde"), (AVEUGLE, "pas aveugle"),
                      (DEPART, "départ")):
        art.line([x1, yl + 6, x1 + 22, yl + 6], fill=coul, width=2)
        ecrire(x1 + 30, yl, nom, petit, ENCRE)
        yl += 18
    yl += 10
    # Les marches, une ligne chacune, avec leur état — ce qui fait que la figure se lit comme un
    # tableau de bord et pas seulement comme une image.
    ecrire(x1, yl, "les marches", petit, GRIS)
    yl += 18
    for i, m in enumerate(marches[:22]):
        n = len(m["confirme"])
        etat = m["fin"] or ("en cours" if n else "au départ")
        r = f" · r {m['rayon_mm']:.2f} mm" if isinstance(m.get("rayon_mm"), (int, float)) else ""
        ecrire(x1, yl, f"{i:>2} · {n:>3} pas · {sum(m['confirme']):>3} conf{r} · {etat}",
               petit, ENCRE if m["fin"] else CONFIRME)
        yl += 15
    if len(marches) > 22:
        ecrire(x1, yl, f"… et {len(marches) - 22} de plus", petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]}) · {len(marches)} marche(s), "
          f"{pas_total} pas")
    return sortie, poses, [cadre, (x1, y1, x1 + pw2, H - 20)], points_ecran


def suivre(trace: Path, sortie: Path, azimut: float, elevation: float, toutes_les: float,
           tourner: float, tours: int | None = None) -> int:
    """Re-rend la trace toutes les `toutes_les` secondes, tant qu'on ne l'interrompt pas.

    ⚠ La boucle ne s'arrête pas d'elle-même sur une course finie : la trace ne dit pas combien de
    bandes restent à venir avec certitude (une reprise en écrit moins), et s'arrêter trop tôt
    est pire que tourner à vide. Ctrl-C est la sortie prévue ; `tours` borne le nombre de rendus,
    et n'existe que pour que la batterie puisse exercer cette boucle — une boucle qu'on ne peut
    pas tester est une boucle qu'on découvre cassée le soir d'une course.

    Rend le nombre de rendus effectués.
    """
    az, rendus = azimut, 0
    try:
        while tours is None or rendus < tours:
            if trace.is_file():
                try:
                    dessiner(lire(trace), sortie, az, elevation)
                    rendus += 1
                except ValueError as e:
                    print(f"⚠ {e}")
            else:
                print(f"… {trace} n'existe pas encore")
            az = (az + tourner) % 360.0
            time.sleep(toutes_les)
    except KeyboardInterrupt:
        print("\narrêt demandé")
    return rendus


def verifier() -> int:
    """Des contrôles hors ligne, sur une trace fabriquée — et des sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    def trace_fabriquee(n_marches=4, n_pas=12, fins=True):
        lignes = [{"quoi": "course", "fragment": "F", "pas_max": n_pas, "memoire_du_cap": 0.5,
                   "bandes": n_marches, "voxel_um": 2.4}]
        rng = np.random.default_rng(3)
        for i in range(n_marches):
            p = np.array([1000.0 + 300.0 * i, 2000.0, 2000.0 + 200.0 * i])
            lignes.append({"quoi": "depart", "bande": [i, i + 1], "rayon_mm": 4.0 + i,
                           "marche": i, "position_zyx": p.tolist()})
            for k in range(1, n_pas + 1):
                p = p + np.array([0.3, 2.0, 1.0]) + rng.normal(0, 0.2, 3)
                lignes.append({"quoi": "pas", "marche": i, "pas": k,
                               "position_zyx": [round(float(x), 2) for x in p],
                               "confirme": bool(k % 3), "oriente": bool(k != 7 or i != 1),
                               "rien_lu": bool(k == 9 and i == 2),
                               "avance_um": 173.0, "parcouru_um": 173.0 * k})
            if fins:
                lignes.append({"quoi": "fin", "marche": i, "pas_parcourus": n_pas,
                               "pas_confirmes": 2, "fin": "plafond"})
        return lignes

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        j = r / "t.jsonl"
        j.write_text("\n".join(json.dumps(x) for x in trace_fabriquee()) + "\n",
                     encoding="utf-8")
        lu = lire(j)
        v("la trace est lue", len(lu["marches"]), 4)
        v("... et chaque marche porte départ + pas", len(lu["marches"][0]["points"]), 13)
        v("... et sa fin", lu["marches"][3]["fin"], "plafond")
        p, poses, cadres, points = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
            else list(im.getdata())

        def fondus(coul, marge=3):
            # ⚠ Un trait est FONDU vers le fond selon sa profondeur, donc la couleur exacte
            # n'apparaît que sur le segment le plus proche. Un pixel « de cette couleur » est un
            # pixel sur le segment coul → FOND, à `marge` près par canal.
            n = 0
            for px in pixels:
                d0 = FOND[0] - coul[0]
                if abs(d0) < 1e-9:
                    continue
                tt = (px[0] - coul[0]) / d0
                if not (-0.02 <= tt <= 0.5):
                    continue
                if all(abs(px[i] - (coul[i] + tt * (FOND[i] - coul[i]))) <= marge
                       for i in range(3)):
                    n += 1
            return n
        v("les pas confirmés sont tracés", fondus(CONFIRME) > 50)
        v("... et les refusés dans une autre couleur", fondus(REFUSE) > 50)
        v("... et le pas contre la garde en ambre", fondus(GARDE) > 5)
        v("... et le pas aveugle en alerte", fondus(AVEUGLE) > 5)
        v("l'emprise est écrite en millimètres quand la trace porte le voxel",
          any("mm (x, y, z)" in tx for _, _, tx, _ in poses))
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        gx0, gy0, gx1, gy1 = cadres[0]
        # ⚠ `points` porte AUSSI les huit coins de la boîte : c'est elle qui sortait du panneau.
        v("toutes les trajectoires ET la boîte tiennent dans leur cadre",
          [1 for x, y in points if not (gx0 - 1 <= x <= gx1 + 1 and gy0 - 1 <= y <= gy1 + 1)], [])

        # ⭐⭐⭐ LA CAMÉRA : deux axes orthonormés, et une profondeur qui trie vraiment.
        dr, ha, vu = camera(35.0, 25.0)
        v("les axes de la caméra sont orthonormés",
          all(abs(float(a @ b)) < 1e-9 for a, b in ((dr, ha), (dr, vu), (ha, vu)))
          and all(abs(float(np.linalg.norm(a)) - 1.0) < 1e-9 for a in (dr, ha, vu)))
        # ⚠ Vue de face (az 0, el 0) : x va à droite et z va en haut, sans miroir.
        pr = projeter(np.asarray([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0]]), 0.0, 0.0)
        v("de face, +x va vers la droite de l'écran", pr[0, 0] > 0.9 and abs(pr[0, 1]) < 1e-9)
        v("... et +z va vers le haut", pr[1, 1] > 0.9 and abs(pr[1, 0]) < 1e-9)
        # ⚠ Une élévation positive regarde d'en haut : un point plus haut en z se RAPPROCHE.
        pr2 = projeter(np.asarray([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]), 0.0, 30.0)
        v("vu d'en haut, le point le plus haut est le plus proche", bool(pr2[0, 2] < pr2[1, 2]))
        # ⚠ Tourner la caméra d'un demi-tour inverse la droite de l'écran.
        pr3 = projeter(np.asarray([[0.0, 0.0, 1.0]]), 180.0, 0.0)
        v("un demi-tour d'azimut inverse l'écran", pr3[0, 0] < -0.9)

        # ⭐⭐⭐⭐ LES SONDES QUI FONT DE CETTE FIGURE UN VISUALISEUR TEMPS RÉEL.
        # 1. une ligne coupée (course en train d'écrire) est ignorée, jamais refusée.
        j.write_text(j.read_text(encoding="utf-8") + '{"quoi": "pas", "marche": 0, "pa',
                     encoding="utf-8")
        lu2 = lire(j)
        v("sonde : une ligne coupée est ignorée et comptée", lu2["coupees"], 1)
        v("... et le reste est intact", len(lu2["marches"][0]["points"]), 13)
        # 2. une course sans ligne de fin est « en cours », pas cassée.
        j.write_text("\n".join(json.dumps(x) for x in trace_fabriquee(fins=False)) + "\n",
                     encoding="utf-8")
        lu3 = lire(j)
        v("sonde : une course sans `fin` est lisible", all(m["fin"] is None for m in lu3["marches"]))
        dessiner(lu3, r / "g.png")
        v("... et se dessine", (r / "g.png").is_file())
        # 3. un fichier sans en-tête est refusé : ce n'est pas une trace.
        j.write_text('{"quoi": "pas", "marche": 0}\n', encoding="utf-8")
        try:
            lire(j)
            v("sonde : un fichier sans en-tête `course` est refusé", False)
        except ValueError:
            v("sonde : un fichier sans en-tête `course` est refusé", True)
        # 4. une trace réduite à son en-tête se dessine (la course vient de partir).
        j.write_text(json.dumps({"quoi": "course", "pas_max": 3, "bandes": 2}) + "\n",
                     encoding="utf-8")
        p4, poses4, _, pts4 = dessiner(lire(j), r / "h.png")
        v("une trace sans marche se dessine quand même", p4.is_file() and pts4 == [])
        j.write_text("\n".join(json.dumps({k: v_ for k, v_ in x.items() if k != "voxel_um"})
                               for x in trace_fabriquee()) + "\n", encoding="utf-8")
        _, poses5, _, _ = dessiner(lire(j), r / "i.png")
        v("... et sans voxel dans l'en-tête, l'emprise est dite en voxels",
          any("voxels (x, y, z)" in tx for _, _, tx, _ in poses5))
        # 5. les deux caméras rendent deux images : la 3D n'est pas une constante.
        j.write_text("\n".join(json.dumps(x) for x in trace_fabriquee()) + "\n",
                     encoding="utf-8")
        dessiner(lire(j), r / "a.png", 35.0, 25.0)
        dessiner(lire(j), r / "b.png", 125.0, 25.0)
        v("sonde : tourner la caméra change l'image",
          (r / "a.png").read_bytes() != (r / "b.png").read_bytes())
        # 8. vu de dessus, l'axe z se projette en un point et son étiquette ne recouvre rien.
        _, poses_haut, _, _ = dessiner(lire(j), r / "u.png", 0.0, 85.0)
        v("vu de dessus, aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses_haut), [])
        v("... et l'axe vu par le bout n'est pas étiqueté",
          not any(tx.startswith("z (axe)") for _, _, tx, _ in poses_haut))
        # 7. le mode qui suit une course rend, tourne, et s'arrête au nombre de tours demandé.
        n = suivre(j, r / "s.png", 35.0, 25.0, 0.0, 90.0, tours=2)
        v("le suivi rend le nombre de tours demandé", n, 2)
        v("... et son dernier rendu est celui d'une caméra tournée",
          (r / "s.png").read_bytes() != (r / "a.png").read_bytes()
          and (r / "s.png").read_bytes() == dessiner(lire(j), r / "t.png", 125.0, 25.0)[0].read_bytes())
        # 6. et deux rendus de la même vue sont identiques au bit : le rendu est pur.
        dessiner(lire(j), r / "c.png", 35.0, 25.0)
        v("deux rendus d'une même vue sont identiques au bit",
          (r / "a.png").read_bytes() == (r / "c.png").read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", type=Path,
                   default=RACINE / "docs" / "mesures" / "la_course_a_cap.jsonl")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "133_la_course_en_3d.png")
    p.add_argument("--azimut", type=float, default=AZIMUT)
    p.add_argument("--elevation", type=float, default=ELEVATION)
    p.add_argument("--suivre", type=float, default=None, metavar="SECONDES",
                   help="re-rend toutes les N secondes, tant que la course tourne")
    p.add_argument("--tourner", type=float, default=0.0, metavar="DEGRES",
                   help="avec --suivre : degrés d'azimut ajoutés à chaque rendu")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.suivre is not None:
        suivre(a.trace, a.sortie, a.azimut, a.elevation, a.suivre, a.tourner)
        return 0
    dessiner(lire(a.trace), a.sortie, a.azimut, a.elevation)
    return 0


if __name__ == "__main__":
    sys.exit(main())
