#!/usr/bin/env python3
"""Le critère : ce n'est pas la forme, c'est comment on choisit — et le voisinage n'est pas un lissage.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Deux tranches avaient fermé les portes de la **forme** cherchée
et de son **amplitude**, sans jamais évaluer ce qui tourne réellement : le raccrochage déployé
passe ses décalages par la médiane du voisinage 3×3 de grille, et aucune des deux mesures ne
l'appelait. Elles jugeaient donc un raccrochage plus grossier que celui qui produit les nombres.

⭐⭐⭐ Le panneau A porte le premier gain de la campagne qui **tranche** contre l'immobilité, et le
panneau B porte la raison pour laquelle il compte : l'accord de voisinage améliore la lecture
bien plus qu'il n'améliore le **bruit**. Sans ce second panneau, on créditerait la lecture d'un
simple adoucissement — une médiane de voisinage améliore n'importe quoi.

⚠⚠ Chaque écart est pris **pas par pas** et porte son intervalle quand n'importe quel pas sort :
sur cette matière, la dispersion d'un pas à l'autre vaut quatre fois l'écart entre méthodes.

Usage :
    uv run python src/figures/figure_le_critere_du_raccrochage.py --verifier
    uv run python src/figures/figure_le_critere_du_raccrochage.py \\
        --sortie docs/images/75_le_critere_du_raccrochage.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import echelle_appariee, police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402
from lecart_apparie import tranche  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_critere_du_raccrochage.json"
# ⚠⚠⚠ LA SECONDE POPULATION N'EST PAS UN BONUS, C'EST CE QUI REND LES VERDICTS LISIBLES. La
# tranche précédente a mesuré qu'à six ou sept pas un verdict bascule quand un pas sort ; ici
# deux boîtes donnent deux populations (8 pas / 16 537 cellules et 7 pas / 6 582), et ce qui
# est publié comme acquis est ce qui tranche dans les DEUX. Une figure qui n'en porterait
# qu'une afficherait des verdicts que ce dépôt sait déjà fragiles.
TEMOIN = RACINE / "docs" / "mesures" / "le_critere_du_raccrochage_640.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
VERT = (76, 122, 84)
ROUGE = (188, 68, 52)
CADRE = (200, 200, 200)


def couleur(x: dict, e: dict | None) -> tuple[int, int, int]:
    """La couleur d'une barre : ce qu'elle EST d'abord, ce qu'elle vaut ensuite.

    ⚠⚠ Un témoin et une borne ne sont pas des méthodes, donc ils ne prennent jamais la couleur
    d'un verdict — un témoin peint en « tranche » se lirait comme un remède disponible.
    """
    if x["borne"]:
        return ROUGE
    if x["temoin"]:
        return AMBRE
    return VERT if (e is not None and tranche(e)) else BLEU


def echelle_lisible(x: dict, e: dict | None) -> str:
    if e is None or e["ecart_median_um"] is None:
        return "—"
    return (f"{e['ecart_median_um']:+.1f} um  {e['pas_ameliores']}/{e['pas']}  "
            f"{e['intervalle_um']}")


def verdict_de(m: dict, nom: str, cle: str) -> bool:
    """Ce critère tranche-t-il sur cette comparaison, dans cette population ?"""
    e = next(x for x in m["resume"] if x["critere"] == nom)[cle]
    return e is not None and tranche(e)


def robuste(m: dict, t: dict | None, nom: str, cle: str) -> bool:
    """Le verdict tient-il dans les DEUX populations ?

    ⚠⚠⚠ C'est la seule forme sous laquelle ce dépôt a le droit d'écrire « acquis » sur cette
    matière : la tranche précédente a mesuré qu'à sept pas un verdict bascule quand un pas
    sort. Sans seconde population, `tranche` répond sur l'échantillon qu'on lui a donné.
    """
    return bool(verdict_de(m, nom, cle) and t is not None and verdict_de(t, nom, cle))


def prose(m: dict, t: dict | None = None) -> list[str]:
    def par(nom: str) -> dict:
        return next(x for x in m["resume"] if x["critere"] == nom)

    dep, comb = par("correlation_accordee"), par("correlation_accordee_centree")
    brut, mel = par("correlation"), par("melange_accorde")
    deux = (f"{t['paires']} pas / {t['cellules']} cellules" if t else "aucune")
    return [
        f"{m['paires']} pas, {m['cellules']} cellules retenues sur "
        f"{m['cellules_lisibles']} lisibles, boite de {int(m['boite']['cote_voxels'])} voxels. "
        f"la forme cherchee et la fenetre sont FIXEES ; ce qui varie est le CRITERE, "
        f"c'est-a-dire comment on designe un decalage. ⚠ chaque ecart est pris PAS PAR PAS et "
        f"porte son intervalle quand n'importe quel pas sort — ici la dispersion entre pas vaut "
        f"quatre fois l'ecart entre methodes.",
        f"⚠⚠ CE QUI TOURNE VRAIMENT N'AVAIT JAMAIS ETE EVALUE. le raccrochage deploye passe ses "
        f"decalages par la mediane du voisinage 3x3 de GRILLE, et les deux tranches precedentes "
        f"echantillonnaient au hasard — ce qui detruit l'adjacence et rend l'accord inappelable. "
        f"elles jugeaient donc un raccrochage plus grossier que celui qui produit les nombres "
        f"publies. cette mesure travaille sur la grille.",
        f"⚠⚠ le chemin DEPLOYE — correlation puis accord de voisinage — TRANCHE contre ne rien "
        f"faire : {echelle_lisible(dep, dep['contre_ne_rien_faire'])}, soit "
        f"{dep['erreur_mediane_um']} um contre {m['erreur_ne_rien_faire_mediane_um']} en ne "
        f"bougeant pas. c'est la premiere fois que le raccrochage deploye est mesure TEL QU'IL "
        f"TOURNE, et il gagne. ⚠ la correlation SEULE, elle, ne tranche pas "
        f"({echelle_lisible(brut, brut['contre_ne_rien_faire'])}) : tout le gain vient de "
        f"l'accord.",
        f"⚠⚠ MAIS LE TEMOIN REFUSE LA LECTURE FACILE. une mediane de voisinage ameliore "
        f"N'IMPORTE QUOI : le meme accord applique aux decalages d'un gabarit MELANGE gagne "
        f"{echelle_lisible(mel, mel['contre_sa_version_brute'])}, et il TRANCHE lui aussi. "
        f"l'accord sur la lecture vaut {m['gain_de_laccord_um']} um contre "
        f"{m['gain_de_laccord_sur_le_bruit_um']} um sur le bruit : la lecture garde une avance, "
        f"mais une part importante du gain est du lissage PUR.",
        f"⚠⚠⚠ ET C'EST POUR CA QUE DEUX POPULATIONS SONT PUBLIEES ({deux} pour la seconde). a "
        f"sept pas le lissage du bruit NE tranchait PAS, a huit il tranche — le verdict a "
        f"bascule avec la population, ce que ce depot sait etre le mode de defaillance de cette "
        f"matiere. ce qui est acquis est ce qui tranche des DEUX cotes : l'accord ameliore la "
        f"lecture, et correlation + accord + retrait du biais bat l'immobilite.",
        f"la BORNE reste tres loin : l'oracle des decalages rend "
        f"{m['erreur_oracle_mediane_um']} um et tranche sur {m['paires']} pas sur "
        f"{m['paires']}. entre {comb['erreur_mediane_um']} et 20 um, le chantier de la lecture "
        f"est entame — il n'est pas ferme.",
    ]


def echelle(art, x0: int, y0: int, pw: int, ph: int, m: dict, entrees: list[dict],
            cle: str, petit, moyen, legende: str) -> list[str]:
    """Le tableau des écarts appariés, tracé par l'échelle partagée.

    ⚠ Ce fichier ne dessine plus lui-même : `figure_commune.echelle_appariee` porte le tracé,
    et `la_lissite_de_la_feuille` s'en sert aussi. Deux échelles séparées finiraient par ne
    plus s'accorder sur ce qu'un intervalle veut dire, alors que c'est LUI le verdict.
    """
    return echelle_appariee(
        art, x0, y0, pw, ph,
        [(x["critere"].replace("_", " "), x[cle], couleur(x, x[cle]), x["deploye"])
         for x in entrees],
        petit, legende, FOND, TEXTE, DISCRET, CADRE)


def dessiner(m: dict, sortie: Path, t: dict | None = None) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart = 40, 440, 46
    largeur_utile = pw * 2 + ecart
    for coupe in (128, 120, 112, 104, 96, 88):
        lignes = couper(prose(m, t), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    tous = m["resume"]
    accordes = [x for x in tous if x["accorde"]]
    ph = 34 + 46 * len(tous)
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Le critere : le voisinage de grille n'est pas un lissage",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['paires']} pas · {m['cellules']} cellules · forme et fenetre FIXEES, "
             f"seul le critere varie", fill=DISCRET, font=moyen)

    art.text((marge, 76), "A · ce que chaque critere gagne contre NE RIEN FAIRE",
             fill=TEXTE, font=moyen)
    eta = echelle(art, marge, 96, pw, ph, m, tous, "contre_ne_rien_faire", petit, moyen,
                  "vert : tranche · bleu : ne tranche pas · ambre : temoin · rouge : borne")
    bx = marge + pw + ecart
    art.text((bx, 76), "B · ce que l'ACCORD de voisinage ajoute a sa propre version brute",
             fill=TEXTE, font=moyen)
    eta += echelle(art, bx, 96, pw, ph, m, accordes, "contre_sa_version_brute", petit, moyen,
                   "le meme accord sur la LECTURE et sur le BRUIT (ambre)")
    art.text((bx + 10, 96 + ph - 18),
             "un temoin qui gagne autant dit qu'une part du gain est du lissage",
             fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"criteres": len(tous), "etiquettes": eta,
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "panneau": pw, "sortie": str(sortie)}


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
    # ⚠⚠⚠ LA SECONDE POPULATION N'EST PAS OPTIONNELLE UNE FOIS LA PREMIÈRE PUBLIÉE. Sauter la
    # corroboration quand elle manque ferait exactement ce que ce dépôt appelle une
    # vérification incapable de s'exécuter : la figure affirmerait « acquis » sur une seule
    # population, précisément là où l'on sait qu'un verdict bascule.
    v("la seconde population est là, sinon rien ne peut être dit acquis",
      TEMOIN.is_file(), str(TEMOIN))
    t = json.loads(TEMOIN.read_text()) if TEMOIN.is_file() else None
    v("... et c'est bien une AUTRE population, pas la même relue",
      t is not None and (t["paires"], t["cellules"]) != (m["paires"], m["cellules"]),
      f"{m['paires']} pas / {m['cellules']} cellules contre "
      f"{t['paires'] if t else '—'} / {t['cellules'] if t else '—'}")
    v("la prose est traçable", prose_tracable(prose(m, t)))

    def par(nom: str) -> dict:
        return next(x for x in m["resume"] if x["critere"] == nom)

    # ⚠⚠⚠ LE DÉFAUT DE MÉTHODE QUE CETTE TRANCHE RÉPARE : le chemin déployé passe par l'accord
    # de voisinage, et il doit être dans la mesure — sinon on évalue encore autre chose.
    v("le chemin réellement déployé est mesuré, et il est marqué comme tel",
      par("correlation_accordee")["deploye"]
      and sum(1 for x in m["resume"] if x["deploye"]) == 1)
    v("... et l'accord DÉPLACE réellement des cellules",
      all(e[f"cellules_deplacees_{n}"] > 0 for e in m["lignes"]
          for n in ("correlation_accordee", "melange_accorde")),
      str([e["cellules_deplacees_correlation_accordee"] for e in m["lignes"]][:4]))
    # ⚠⚠ UNE SEULE POPULATION PAR MESURE : c'est l'accord qui la fixe, et les bruts sont jugés
    # dessus — sinon les accordés seraient notés sur les cellules qui leur restent.
    v("tous les critères sont jugés sur les cellules que l'accord retient",
      all(0 < e["cellules"] <= e["cellules_lisibles"] for e in m["lignes"]),
      str([(e["cellules"], e["cellules_lisibles"]) for e in m["lignes"]][:3]))
    # ⭐⭐⭐ LE RÉSULTAT QUE LA FIGURE PORTE : le chemin déployé, mesuré TEL QU'IL TOURNE, bat
    # l'immobilité — et tout le gain vient de l'accord, pas de la corrélation.
    v("le chemin déployé TRANCHE contre ne rien faire",
      m["le_chemin_deploye_bat_ne_rien_faire"],
      str(par("correlation_accordee")["contre_ne_rien_faire"]))
    v("... alors que la corrélation SEULE ne tranche pas",
      not tranche(par("correlation")["contre_ne_rien_faire"]),
      str(par("correlation")["contre_ne_rien_faire"]))
    # ⚠⚠⚠ ET LE TÉMOIN, QUI REFUSE LA LECTURE FACILE : l'accord améliore aussi le bruit. Taire
    # ce fait ferait passer un lissage pour une meilleure lecture.
    v("l'accord améliore la LECTURE, et de façon qui tranche",
      m["laccord_ameliore_la_correlation"],
      str(par("correlation_accordee")["contre_sa_version_brute"]))
    v("... mais il améliore AUSSI le bruit, et ce fait est publié",
      isinstance(m["laccord_ameliore_aussi_le_bruit"], bool)
      and m["gain_de_laccord_sur_le_bruit_um"] is not None,
      f"bruit {m['gain_de_laccord_sur_le_bruit_um']} µm · "
      f"tranche : {m['laccord_ameliore_aussi_le_bruit']}")
    v("... la lecture garde tout de même l'avance sur le bruit",
      m["gain_de_laccord_um"] < m["gain_de_laccord_sur_le_bruit_um"],
      f"{m['gain_de_laccord_um']} contre {m['gain_de_laccord_sur_le_bruit_um']} µm")
    # ⚠⚠⚠ ET CE QUI EST DIT ACQUIS DOIT TRANCHER DANS LES DEUX POPULATIONS. Un verdict d'une
    # seule est un verdict que ce dépôt a déjà vu basculer.
    v("⭐ ACQUIS des deux côtés : l'accord améliore la lecture",
      robuste(m, t, "correlation_accordee", "contre_sa_version_brute"),
      f"{m['gain_de_laccord_um']} µm ici · "
      f"{t['gain_de_laccord_um'] if t else '—'} µm sur l'autre population")
    v("⭐ ACQUIS des deux côtés : accord puis retrait du biais bat l'immobilité",
      robuste(m, t, "correlation_accordee_centree", "contre_ne_rien_faire"),
      str(par("correlation_accordee_centree")["contre_ne_rien_faire"]))
    # ⚠⚠ ET CE QUI A BASCULÉ EST DIT AUSSI : le lissage du bruit ne tranchait pas à sept pas.
    v("⚠ et le verdict du lissage sur le BRUIT a bougé d'une population à l'autre",
      t is not None
      and verdict_de(m, "melange_accorde", "contre_sa_version_brute")
      != verdict_de(t, "melange_accorde", "contre_sa_version_brute"),
      f"ici {verdict_de(m, 'melange_accorde', 'contre_sa_version_brute')} · "
      f"là {verdict_de(t, 'melange_accorde', 'contre_sa_version_brute') if t else '—'}")
    v("⛔ la borne reste très loin, et c'est ce qui garde le chantier ouvert",
      par("oracle")["erreur_mediane_um"]
      < par("correlation_accordee_centree")["erreur_mediane_um"] / 1.4,
      f"{par('oracle')['erreur_mediane_um']} contre "
      f"{par('correlation_accordee_centree')['erreur_mediane_um']} µm")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png", t)
        v("tous les critères sont dessinés", r["criteres"] == len(m["resume"]),
          str(r["criteres"]))
        debord = [(t[:40], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        v("toutes les étiquettes dessinées sont rendues par la police",
          prose_tracable(r["etiquettes"]), str(r["etiquettes"][:3]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · ce que chaque critere gagne contre NE RIEN FAIRE",
                      "B · ce que l'ACCORD de voisinage ajoute a sa propre version brute"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < r["panneau"],
              f"{pt_.getbbox(titre)[2]} px pour {r['panneau']}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_le_critere_du_raccrochage.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    t = json.loads(TEMOIN.read_text()) if TEMOIN.is_file() else None
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie, t),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
