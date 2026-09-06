#!/usr/bin/env python3
"""Deux ancres valent bien mieux qu'une : l'encadrement annule un biais.

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
        f"une spire est reconstruite depuis m-j ET depuis m+j : {m['triplets']} triplets "
        f"symetriques, sauts {m['sauts']}, deux bits de supervision au lieu d'un.",
        f"branches seules {m['erreur_montante_mediane_um']} et "
        f"{m['erreur_descendante_mediane_um']} um ; ENCADREE "
        f"{m['erreur_encadree_mediane_um']} um, sous la demi-epaisseur de "
        f"{m['demi_epaisseur_um']}. elle bat les DEUX branches sur "
        f"{m['triplets_ou_lencadrement_bat_les_deux']} triplets sur {m['triplets']}.",
        f"et elle bat aussi « la meilleure des deux » ({m['erreur_de_la_meilleure_mediane_um']} "
        "um), qui demande de savoir laquelle — donc ce n'est pas une regle de selection.",
        f"le mecanisme est un BIAIS annule : les ecarts signes valent "
        f"{m['ecart_signe_montant_median_um']:+.1f} et "
        f"{m['ecart_signe_descendant_median_um']:+.1f} um, de signes opposes sur "
        f"{m['triplets_aux_signes_opposes']} triplets sur {m['triplets']}. moyenner du bruit "
        "gagne racine de deux au mieux ; annuler un biais gagne tout le biais.",
        f"⚠ ce n'est pas une methode mais une BORNE : encadrer suppose de connaitre les deux "
        f"bouts. ce qu'elle dit est ou porter l'effort — cinq soupcons sur la mecanique du pas "
        f"n'ont rien rendu, une seconde ancre divise l'erreur par "
        f"{m['erreur_montante_mediane_um'] / m['erreur_encadree_mediane_um']:.1f}.",
        f"⚠ et le desaccord entre branches ({m['desaccord_median_um']} um) ne PREDIT pas "
        f"l'erreur (rho {m['desaccord_contre_erreur']['rho']}, p "
        f"{m['desaccord_contre_erreur']['p']}) : le seul signal de confiance sans cible du "
        "chantier ne sert pas.",
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
    art.text((marge, 18), "Deux ancres valent bien mieux qu'une : l'encadrement annule un biais",
             fill=TEXTE, font=gros)
    art.text((marge, 42), f"{m['triplets']} triplets symetriques, ecart inter-feuilles "
             f"{m['ecart_lu_um']} um", fill=DISCRET, font=moyen)

    lg = m["lignes"]
    # ---------- A : les trois erreurs, triplet par triplet ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · erreur de chaque branche, et de leur encadrement",
             fill=TEXTE, font=moyen)
    art.rectangle([ax, ay, ax + pw, ay + ph], outline=CADRE)
    top = max(max(e["erreur_montante_um"], e["erreur_descendante_um"]) for e in lg) * 1.1
    larg = pw / (len(lg) + 1)
    yd = ay + ph - m["demi_epaisseur_um"] / top * (ph - 26)
    art.line([ax, yd, ax + pw, yd], fill=TEXTE)
    art.text((ax + 4, yd - 14), f"demi-feuille {m['demi_epaisseur_um']:.0f}µ",
             fill=TEXTE, font=petit)
    for k, e in enumerate(lg):
        x0 = ax + larg * (k + 0.5)
        for dec, cle, coul in ((-0.30, "erreur_montante_um", BLEU),
                               (0.0, "erreur_descendante_um", DISCRET),
                               (0.30, "erreur_encadree_um", AMBRE)):
            h = e[cle] / top * (ph - 26)
            art.rectangle([x0 + dec * larg - larg * 0.13, ay + ph - h,
                           x0 + dec * larg + larg * 0.13, ay + ph], fill=coul)
        # ⚠ L'abscisse ne porte que la spire ENCADRÉE, comme le panneau B : le triplet complet
        # tenait sur douze étiquettes qui se chevauchaient, donc ne se lisait pas du tout.
        art.text((x0 - 8, ay + ph + 3), str(e["cible"]), fill=DISCRET, font=petit)
        if k == 0 or e["saut"] != lg[k - 1]["saut"]:
            art.line([x0 - larg * 0.5, ay + ph, x0 - larg * 0.5, ay + ph + 14], fill=DISCRET)
            art.text((x0 - larg * 0.45, ay + ph + 17), f"saut {e['saut']}", fill=AMBRE,
                     font=petit)
    art.text((ax + 6, ay + 6), "bleu : montante   gris : descendante   ambre : ENCADREE",
             fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 22), "spire encadree en abscisse", fill=DISCRET, font=petit)

    # ---------- B : les ecarts SIGNES ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · elles se trompent en sens CONTRAIRES",
             fill=TEXTE, font=moyen)
    art.rectangle([bx, by, bx + pw, by + ph], outline=CADRE)
    plus = max(max(abs(e["ecart_signe_montante_um"]), abs(e["ecart_signe_descendante_um"]))
               for e in lg) * 1.2
    zero = by + ph / 2
    art.line([bx, zero, bx + pw, zero], fill=TEXTE)
    art.text((bx + 6, by + ph - 16), "la ligne du milieu : 0, pile sur la cible", fill=TEXTE,
             font=petit)
    for k, e in enumerate(lg):
        x0 = bx + larg * (k + 0.5)
        for dec, cle, coul in ((-0.18, "ecart_signe_montante_um", BLEU),
                               (0.18, "ecart_signe_descendante_um", DISCRET)):
            h = e[cle] / plus * (ph / 2 - 18)
            art.rectangle(sorted([zero, zero - h]) and
                          [x0 + dec * larg - larg * 0.15, min(zero, zero - h),
                           x0 + dec * larg + larg * 0.15, max(zero, zero - h)], fill=coul)
        art.text((x0 - 8, by + ph + 3), str(e["cible"]), fill=DISCRET, font=petit)
    art.text((bx + 6, by + 6), "au-dessus : la branche a DEPASSE la cible", fill=DISCRET,
             font=petit)
    art.text((bx + 6, by + ph + 19),
             f"signes opposes sur {m['triplets_aux_signes_opposes']} triplets sur "
             f"{m['triplets']} — spire encadree en abscisse", fill=AMBRE, font=petit)

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
    v("le désaccord entre branches ne prédit PAS l'erreur",
      not m["le_desaccord_predit_lerreur"], str(m["desaccord_contre_erreur"]))
    # ⚠ L'écart doit se creuser avec le saut, sinon « ça aide » serait une constante.
    par_saut = {}
    for e in m["lignes"]:
        par_saut.setdefault(e["saut"], []).append(
            min(e["erreur_montante_um"], e["erreur_descendante_um"]) / e["erreur_encadree_um"])
    gains = [sum(x) / len(x) for _, x in sorted(par_saut.items())]
    v("le gain se creuse quand le saut grandit", gains[-1] > gains[0],
      str([round(g, 2) for g in gains]))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les triplets sont dessinés", r["triplets"] == m["triplets"])
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
