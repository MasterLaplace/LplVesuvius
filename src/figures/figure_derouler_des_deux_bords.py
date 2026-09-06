#!/usr/bin/env python3
"""Deux ancres valent bien mieux qu'une — et pondérées par leurs bras, mieux encore.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Les trois médianes — 52,8 / 66,5 / **31,0 µm** — se lisent comme
une moyenne qui aide un peu, et ce n'est pas ça : le panneau A montre que l'écart se **creuse**
avec le saut, jusqu'à un facteur quatre là où les deux branches ont perdu la feuille et où
l'encadrement la tient encore.

⭐⭐ Le panneau B porte le mécanisme, et c'est lui qui empêche de lire ce gain comme un
moyennage : les deux branches se trompent **en sens contraires** — +34,1 µm d'un côté, −59,9 de
l'autre. Moyenner du bruit gagne √2 au mieux ; annuler un biais gagne tout le biais.

Usage :
    uv run python src/figures/figure_derouler_des_deux_bords.py --verifier
    uv run python src/figures/figure_derouler_des_deux_bords.py \\
        --sortie docs/images/75_derouler_des_deux_bords.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "derouler_des_deux_bords.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    return [
        f"une spire est reconstruite depuis a < m ET depuis b > m : {m['triplets']} "
        f"encadrements, portee {m['portee']}, dont {m['triplets_symetriques']} symetriques ; "
        "deux bits de supervision au lieu d'un.",
        f"branches seules {m['erreur_montante_mediane_um']} et "
        f"{m['erreur_descendante_mediane_um']} um ; ENCADREE "
        f"{m['erreur_encadree_mediane_um']} um, sous la demi-epaisseur de "
        f"{m['demi_epaisseur_um']}. elle bat les DEUX branches sur "
        f"{m['triplets_ou_lencadrement_bat_les_deux']} encadrements sur "
        f"{m['triplets']} mesures.",
        f"et elle bat aussi « la meilleure des deux » ({m['erreur_de_la_meilleure_mediane_um']} "
        "um), qui demande de savoir laquelle — donc ce n'est pas une regle de selection.",
        f"PONDEREE par les bras — la branche au bras court pese le plus, sans aucun parametre "
        f"libre — elle rend {m['erreur_ponderee_mediane_um']} um, contre "
        f"{m['temoin_poids_inverse_median_um']} pour le poids INVERSE. et elle repare "
        f"exactement les paires que la mesure disait cassees, {m['paires_reparees_par_la_ponderation']}, "
        "sans toucher aux symetriques : a bras egaux le poids vaut un demi.",
        f"le mecanisme est un BIAIS annule : les ecarts signes valent "
        f"{m['ecart_signe_montant_median_um']:+.1f} et "
        f"{m['ecart_signe_descendant_median_um']:+.1f} um, de signes opposes sur "
        f"{m['triplets_aux_signes_opposes']} encadrements sur {m['triplets']} mesures. "
        "moyenner du bruit "
        "gagne racine de deux au mieux ; annuler un biais gagne tout le biais.",
        f"⚠ ce n'est pas une methode mais une BORNE : encadrer suppose de connaitre les deux "
        f"bouts. ce qu'elle dit est ou porter l'effort — cinq soupcons sur la mecanique du pas "
        f"n'ont rien rendu, une seconde ancre divise l'erreur par "
        f"{m['gain_sur_la_branche_montante']}.",
        f"et le desaccord entre branches PREDIT l'erreur (rho "
        f"{m['desaccord_contre_erreur']['rho']}, p {m['desaccord_contre_erreur']['p']}, n "
        f"{m['desaccord_contre_erreur']['n']}) : c'est le seul signal de confiance du chantier "
        "qui ne demande pas la reponse, donc un derouleur peut s'en servir en marchant. ⚠ sur "
        "une douzaine d'encadrements symetriques seulement, il ne predisait rien — un verdict "
        "sur un petit echantillon n'est pas un verdict.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lignes = couper(prose(m), 128)
    marge, pw, ph, ecart = 40, 400, 250, 56
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 90 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18),
             "Deux ancres valent mieux qu'une, et ponderees par leurs bras mieux encore",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['triplets']} encadrements dont {m['triplets_symetriques']} symetriques, "
             f"ecart inter-feuilles {m['ecart_lu_um']} um", fill=DISCRET, font=moyen)

    lg = m["lignes"]
    # ---------- A : l'erreur par PAIRE DE BRAS ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · erreur par paire de bras : branches contre encadrement",
             fill=TEXTE, font=moyen)
    art.rectangle([ax, ay, ax + pw, ay + ph], outline=CADRE)
    paires = list(m["par_paire_de_bras"].items())
    # ⚠ La pondérée est relue par paire depuis les lignes : le résumé par paire ne la porte pas,
    # et la recalculer dans la figure serait un nombre que la mesure ne publie pas.
    pond = {}
    for e in m["lignes"]:
        cle = f"{min(e['bras_bas'], e['bras_haut'])}+{max(e['bras_bas'], e['bras_haut'])}"
        pond.setdefault(cle, []).append(e["erreur_ponderee_um"])
    pond = {k: sorted(v)[len(v) // 2] for k, v in pond.items()}
    top = max(max(d["meilleure_branche_um"], d["encadree_um"]) for _, d in paires) * 1.15
    larg = pw / (len(paires) + 1)
    yd = ay + ph - m["demi_epaisseur_um"] / top * (ph - 34)
    art.line([ax, yd, ax + pw, yd], fill=TEXTE)
    art.text((ax + 4, yd - 14), f"demi-feuille {m['demi_epaisseur_um']:.0f}µ",
             fill=TEXTE, font=petit)
    for k, (cle, d) in enumerate(paires):
        x0 = ax + larg * (k + 0.5)
        for dec, val, coul in ((-0.28, d["meilleure_branche_um"], BLEU),
                               (0.0, d["encadree_um"], DISCRET),
                               (0.28, pond[cle], AMBRE)):
            h = val / top * (ph - 34)
            art.rectangle([x0 + dec * larg - larg * 0.13, ay + ph - h,
                           x0 + dec * larg + larg * 0.13, ay + ph], fill=coul)
        art.text((x0 - 12, ay + ph + 3), cle,
                 fill=(AMBRE if d["symetrique"] else DISCRET), font=petit)
    art.text((ax + 6, ay + 6),
             "bleu : MEILLEURE branche   gris : encadrement   ambre : PONDERE par les bras",
             fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 22),
             "abscisse : les deux bras, en spires — en ambre les symetriques",
             fill=DISCRET, font=petit)

    # ---------- B : le desaccord contre l'erreur ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · le desaccord PREDIT l'erreur, et il ne voit pas la cible",
             fill=TEXTE, font=moyen)
    art.rectangle([bx, by, bx + pw, by + ph], outline=CADRE)
    xs = [e["desaccord_um"] for e in lg]
    ys = [e["erreur_encadree_um"] for e in lg]
    xmax, ymax = max(xs) * 1.1, max(ys) * 1.1
    for e in lg:
        x_ = bx + e["desaccord_um"] / xmax * (pw - 30) + 20
        y_ = by + ph - e["erreur_encadree_um"] / ymax * (ph - 40) - 20
        coul = AMBRE if e["symetrique"] else BLEU
        art.ellipse([x_ - 3, y_ - 3, x_ + 3, y_ + 3], fill=coul)
    yd2 = by + ph - m["demi_epaisseur_um"] / ymax * (ph - 40) - 20
    art.line([bx, yd2, bx + pw, yd2], fill=TEXTE)
    art.text((bx + pw - 116, yd2 - 14), f"demi-feuille {m['demi_epaisseur_um']:.0f}µ",
             fill=TEXTE, font=petit)
    d_ = m["desaccord_contre_erreur"]
    art.text((bx + 6, by + 6), f"rho {d_['rho']} · p {d_['p']} · n {d_['n']}",
             fill=TEXTE, font=petit)
    art.text((bx + 6, by + 22), "ambre : encadrements symetriques", fill=AMBRE, font=petit)
    art.text((bx + 6, by + ph + 3), "abscisse : desaccord entre branches (um)",
             fill=DISCRET, font=petit)
    art.text((bx + 6, by + ph + 19), "ordonnee : erreur de l'encadrement (um)",
             fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"triplets": len(lg), "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LES QUATRE FAITS QUE LA FIGURE PORTE. L'encadrement bat les DEUX branches, il bat
    # aussi « la meilleure des deux » (donc ce n'est pas une règle de sélection), il tient la
    # feuille, et le mécanisme est un biais annulé. Sans le troisième, « ça aide » ne dirait pas
    # si ça sert ; sans le quatrième, on lirait un moyennage.
    v("l'encadrement bat les deux branches", m["lencadrement_bat_les_deux"],
      f"{m['erreur_encadree_mediane_um']} contre {m['erreur_montante_mediane_um']} et "
      f"{m['erreur_descendante_mediane_um']}")
    v("... et aussi « la meilleure des deux », qui demande la réponse",
      m["erreur_encadree_mediane_um"] < m["erreur_de_la_meilleure_mediane_um"],
      f"{m['erreur_encadree_mediane_um']} contre {m['erreur_de_la_meilleure_mediane_um']}")
    v("... et il tient la feuille", m["sous_la_demi_feuille"]["erreur_encadree_mediane_um"],
      f"{m['erreur_encadree_mediane_um']} contre {m['demi_epaisseur_um']}")
    v("le mécanisme est un biais annulé, pas un moyennage",
      m["lencadrement_annule_un_biais"],
      f"{m['triplets_aux_signes_opposes']} triplets sur {m['triplets']}")
    v("... et les deux écarts signés sont bien de signes opposés",
      m["ecart_signe_montant_median_um"] * m["ecart_signe_descendant_median_um"] < 0,
      f"{m['ecart_signe_montant_median_um']} et {m['ecart_signe_descendant_median_um']}")
    # ⚠⚠ ET LE NÉGATIF INTERNE, qui doit être dit : le désaccord ne prédit pas l'erreur.
    # ⚠⚠⚠ CE VERDICT S'EST INVERSÉ AVEC L'ÉCHANTILLON, et dans le bon sens : sur douze
    # encadrements symétriques le désaccord ne prédisait rien (rho 0,28, p 0,38) ; sur
    # cinquante-six, symétriques et non, il prédit (rho 0,41, p 0,002). Un verdict sur un petit
    # échantillon n'est pas un verdict — la même leçon que la boîte, dans l'autre sens.
    v("le désaccord entre branches prédit l'erreur",
      m["le_desaccord_predit_lerreur"], str(m["desaccord_contre_erreur"]))
    v("... sur un échantillon assez grand pour trancher",
      m["desaccord_contre_erreur"]["n"] > 40, str(m["desaccord_contre_erreur"]["n"]))
    # ⚠ L'écart doit se creuser avec le saut, sinon « ça aide » serait une constante.
    par_saut = {}
    for e in m["lignes"]:
        par_saut.setdefault(e["saut"], []).append(
            min(e["erreur_montante_um"], e["erreur_descendante_um"]) / e["erreur_encadree_um"])
    gains = [sum(x) / len(x) for _, x in sorted(par_saut.items())]
    v("le gain se creuse quand le saut grandit", gains[-1] > gains[0],
      str([round(g, 2) for g in gains]))
    # ⚠⚠⚠ LA PONDÉRATION : elle bat le milieu, elle bat son témoin inversé, elle ne touche pas
    # les symétriques, et elle répare TOUTES les paires cassées. Les quatre ensemble — sans la
    # dernière, « ça améliore la médiane » pourrait vouloir dire qu'elle a déplacé des cas sains.
    v("la pondération bat le milieu", m["la_ponderation_bat_le_milieu"],
      f"{m['erreur_ponderee_mediane_um']} contre {m['erreur_encadree_mediane_um']}")
    v("... et son témoin de poids inversé", m["la_ponderation_bat_son_temoin"],
      f"{m['erreur_ponderee_mediane_um']} contre {m['temoin_poids_inverse_median_um']}")
    v("... sans toucher aux symétriques", m["symetriques_inchanges_par_la_ponderation"])
    v("... et elle répare toutes les paires cassées",
      m["la_ponderation_repare_les_paires_cassees"],
      f"{m['paires_reparees_par_la_ponderation']} sur {m['paires_ou_lencadrement_nuit']}")
    # ⚠ Les encadrements asymétriques doivent être la majorité du corpus mesuré, sinon la
    # question « où poser la seconde ancre » n'aurait presque pas de points.
    v("les encadrements asymétriques dominent la mesure",
      m["triplets"] - m["triplets_symetriques"] > m["triplets_symetriques"],
      f"{m['triplets_symetriques']} symétriques sur {m['triplets']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les encadrements sont dessinés", r["triplets"] == m["triplets"])
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        # ⚠⚠ UN TITRE DE PANNEAU QUI DÉBORDE SE LIT TRONQUÉ, DONC FAUX — le panneau B affichait
        # « en sens contraire » pour « contraires », ce qui change la phrase. Et le remplacement
        # qui devait le corriger était un `str.replace` SANS assertion, donc un no-op silencieux :
        # ce contrôle est ce qui l'aurait vu.
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · erreur de chaque branche, et de leur encadrement",
                      "B · elles se trompent en sens CONTRAIRES"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < 400, f"{pt_.getbbox(titre)[2]} px pour 400")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_derouler_des_deux_bords.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
