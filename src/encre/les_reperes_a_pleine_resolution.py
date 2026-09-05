#!/usr/bin/env python3
"""Le goulot de C1 était-il le fragment, ou le sous-échantillonnage ? — et ce que ça change à la COUVERTURE.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `75` C1 a trouvé **314** trous intérieurs utilisables dans le
masque des étiquettes et n'en a transporté que **55** vers la carte publiée, parce que celle-ci
est **réduite ×8** : un trou de 64 pixels y devient un pixel. Et les 55 survivants sont
**groupés d'un côté**, ce qui est la limite que tout le reste de C1 bute dessus.

⭐⭐⭐ **Or le segment publie AUSSI la carte à pleine résolution**, 20,5 Mo, et son échelle est
presque celle du masque. Le goulot n'était donc peut-être pas le fragment mais le fichier qu'on
avait choisi de lire — ce qui est une hypothèse mesurable, pas une opinion.

⚠⚠ **ET LA QUESTION QUI DÉCIDE N'EST PAS LE COMPTE, C'EST LA COUVERTURE.** Mille repères
entassés dans le même quartier ne valent pas mieux que cinquante-cinq : ce que le recalage
réclame, c'est de la matière **là où il n'y en a pas**. La part de l'empreinte à portée d'un
repère est donc mesurée, à plusieurs rayons, et comparée à celle des 55.

⚠ La couverture est comptée **dans l'empreinte** et jamais dans le rectangle : les coins vides
d'une image la diluent, et une couverture diluée se lit comme un manque de repères alors qu'elle
mesure la forme du fragment.

Usage :
    uv run python src/encre/les_reperes_a_pleine_resolution.py --verifier
    uv run python src/encre/les_reperes_a_pleine_resolution.py \\
        --json docs/mesures/les_reperes_a_pleine_resolution.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "encre"))

SEGMENT = "20250628074500-500P2_front"
APPARIES = RACINE / "docs" / "mesures" / "les_reperes_apparies.json"

RAYONS = (500, 1000, 2000, 4000)
"""Les rayons de couverture, en pixels de la carte à pleine résolution.

⚠ Balayés et non choisis : un rayon dit implicitement « jusqu'où un repère contraint le champ »,
et personne ne l'a mesuré. Le résultat est donc la COURBE, et c'est elle qui dit si la
couverture manque de repères ou de portée."""


def carte_publiee_pleine(recette: str = "new_canon") -> tuple[np.ndarray, str] | None:
    """La carte d'encre publiée du segment, à sa résolution NATIVE.

    ⚠⚠ `carte_publiee_reduite` prend délibérément la version `ink-detection-downsampled` ; celle
    d'ici prend `ink-detection`, huit fois plus fine. Les deux existent dans l'index, et lire la
    première par habitude est exactement ce qui a coûté 259 repères sur 314.

    ⚠ Le nom du fichier est rendu avec la carte : le segment en publie **deux**, de deux
    recettes, et « la » carte sans dire laquelle rendrait le résultat irreproductible.
    """
    from PIL import Image  # noqa: PLC0415

    import la_case_vide as cv  # noqa: PLC0415
    from zarr_depth import BUCKET, get  # noqa: PLC0415

    Image.MAX_IMAGE_PIXELS = None
    for _, fiche in cv._charger().items():
        for sid, seg in fiche.get("segments", {}).items():
            if seg.get("long_id", sid) != SEGMENT:
                continue
            for e in seg.get("data", []):
                chemin = e.get("origins", [{}])[0].get("path", "")
                if (e.get("type") == "ink-detection"
                        and recette in chemin and "2.215um" in chemin):
                    brut = get(f"{BUCKET}/{chemin}", 900)
                    if brut is None:
                        return None
                    a = np.asarray(Image.open(io.BytesIO(brut)).convert("L"), dtype=np.uint8)
                    return a, chemin.split("/")[-1]
    return None


def couverture(positions: np.ndarray, empreinte: np.ndarray, rayon: float,
               pas: int = 16) -> float:
    """La part de l'EMPREINTE à moins de `rayon` d'un repère.

    ⚠⚠⚠ C'est la grandeur que C1 réclame et que personne n'avait mesurée. « Groupés d'un côté »
    est une impression ; « 31 % de l'empreinte à portée » est une contrainte qu'on peut suivre
    d'une tranche à l'autre.

    ⚠ Comptée dans l'empreinte, jamais dans le rectangle : les coins vides d'une image la
    diluent, et une couverture diluée se lit comme un manque de repères alors qu'elle mesure la
    forme du fragment.

    ⚠ Échantillonnée au `pas` plutôt que pixel par pixel — 400 millions de cellules contre
    quelques centaines de repères — et le pas est rendu, parce qu'un échantillonnage trop
    grossier ne mesure plus une couverture mais un tirage.
    """
    if positions.size == 0:
        return 0.0
    ii, jj = np.nonzero(empreinte[::pas, ::pas])
    if ii.size == 0:
        return 0.0
    ii = ii.astype(float) * pas
    jj = jj.astype(float) * pas
    proche = np.zeros(ii.size, dtype=bool)
    # ⚠ Par blocs : la matrice complète ferait des centaines de millions de distances.
    for k in range(0, positions.shape[0], 64):
        bloc = positions[k:k + 64]
        d = np.hypot(ii[:, None] - bloc[None, :, 0], jj[:, None] - bloc[None, :, 1])
        proche |= (d <= rayon).any(axis=1)
    return float(proche.mean())


def profil_de_couverture(positions: np.ndarray, empreinte: np.ndarray,
                         rayons=RAYONS, pas: int = 16) -> list[dict]:
    """La couverture à chaque rayon — la courbe, pas un point."""
    return [dict(rayon=int(r), part=round(couverture(positions, empreinte, r, pas), 4))
            for r in rayons]


def composantes_du_fond(support: np.ndarray, aires=(4, 16, 64, 256, 1024)) -> dict:
    """Les trous du support, comptés SANS filtre de forme, par palier d'aire.

    ⚠⚠⚠ POURQUOI CE COMPTE BRUT EXISTE. `trous()` écarte ce qui touche le bord et `utilisables()`
    ce qui n'est pas assez rond ; les deux sont justes, et ensemble ils cachent d'où vient un
    écart. Un support qui passe de 71 trous à 14 en gagnant huit fois en résolution pose une
    question de **matière**, pas de filtre, et seul le compte brut peut y répondre.

    ⚠ Le compte des composantes qui touchent le bord est rendu à part : une baie ouverte sur
    l'extérieur n'est pas un trou, et c'est exactement ce qu'un sous-échantillonnage referme.
    """
    from scipy import ndimage  # noqa: PLC0415

    marques, n = ndimage.label(support == 0)
    if n == 0:
        return dict(composantes=0, interieures=0, par_aire={})
    bord = set(np.unique(np.concatenate([marques[0], marques[-1],
                                         marques[:, 0], marques[:, -1]]).tolist()))
    bord.discard(0)
    tailles = np.bincount(marques.ravel())
    interieurs = [k for k in range(1, n + 1) if k not in bord]
    return dict(composantes=int(n), interieures=len(interieurs),
                touchant_le_bord=int(n - len(interieurs)),
                par_aire={str(a): sum(1 for k in interieurs if tailles[k] >= a)
                          for a in aires})


def reduire_le_support(support: np.ndarray, facteur: int = 8) -> np.ndarray:
    """Le même support, réduit par blocs — un bloc est plein dès qu'il contient de la matière.

    ⚠⚠⚠ C'EST LE TÉMOIN QUI TRANCHE. Si les trous du support réduit publié étaient ceux du
    fragment, réduire le support à **pleine résolution** par la même règle devrait les rendre.
    S'il n'en rend qu'une poignée, alors les autres ne sont pas dans la matière : ils sont dans
    le fichier — et un fichier `.jpg` est **compressé avec perte**, donc il crénelle les bords à
    fort contraste, c'est-à-dire précisément le pourtour des vrais trous.

    ⚠ La règle est « dès qu'il y a de la matière » et non « en majorité » : c'est la plus
    généreuse, donc celle qui donne le plus de chances aux trous d'exister. Un témoin doit être
    monté en faveur de ce qu'il conteste.
    """
    h, w = support.shape
    hh, ww = h // facteur, w // facteur
    bloc = (support[:hh * facteur, :ww * facteur] > 0).reshape(
        hh, facteur, ww, facteur).mean(axis=(1, 3))
    return (bloc > 0).astype(np.uint8) * 255


def etendue_interdecile(positions: np.ndarray, forme: tuple[int, int]) -> dict:
    """L'ÉTENDUE du semis, en part de la carte — à distinguer de son compte.

    ⚠⚠⚠ POURQUOI CETTE MESURE EXISTE, ET C'EST LA FIGURE QUI L'A RÉCLAMÉE. Le compte de repères
    est passé de 55 à 314 et la couverture a monté, ce qui se lit comme « le problème recule ».
    Le dessin montre autre chose : les nouveaux repères suivent **la même bande** que les
    anciens. Multiplier la densité là où on avait déjà de la matière ne donne rien à un recalage
    qui manque de matière **ailleurs**, donc l'étendue doit être comptée à part du compte.

    ⚠ Interdécile et non min-max : deux repères égarés aux extrémités feraient croire à un semis
    étalé alors qu'ils sont deux. Le 80 % central est ce qui décrit où le semis **est**.
    """
    if positions.size == 0:
        return dict(repères=0)
    p10 = np.percentile(positions, 10, axis=0)
    p90 = np.percentile(positions, 90, axis=0)
    return dict(repères=int(positions.shape[0]),
                lignes=[round(float(p10[0]), 1), round(float(p90[0]), 1)],
                colonnes=[round(float(p10[1]), 1), round(float(p90[1]), 1)],
                part_de_la_hauteur=round(float(p90[0] - p10[0]) / forme[0], 4),
                part_de_la_largeur=round(float(p90[1] - p10[1]) / forme[1], 4))


def mesurer(recette: str = "new_canon", graine: int = 42, pas: int = 16) -> dict:
    """Le compte, l'appariement et la COUVERTURE, à pleine résolution contre le réduit."""
    import le_recalage_des_etiquettes as rec  # noqa: PLC0415
    import les_reperes_apparies as ap  # noqa: PLC0415
    from les_reperes_interieurs import trous, utilisables  # noqa: PLC0415

    masque = rec._image("500P2_mask.png")
    pleine = carte_publiee_pleine(recette)
    if masque is None or pleine is None:
        raise SystemExit("masque ou carte pleine résolution absents")
    carte, nom = pleine
    empreinte = (carte > 0).astype(float)
    t = rec.affine_par_boites(masque, empreinte)
    # ⚠⚠ L'aire minimale de la cible est DÉRIVÉE de l'échelle et non reprise du cas réduit : à
    # ×8 un trou de 64 px en valait 1, ici il en vaut 60. Garder 4 laisserait entrer des
    # poussières que le masque n'a jamais eues, et gonfler le compte de cibles rendrait
    # l'appariement facile pour la mauvaise raison.
    facteur = t["echelle_lignes"] * t["echelle_colonnes"]
    from les_reperes_interieurs import AIRE_MINIMALE  # noqa: PLC0415

    aire_cible = max(4, int(round(AIRE_MINIMALE * facteur)))
    r = ap.mesurer(carte.astype(float), masque, t, aire_min_cible=aire_cible, graine=graine)

    sources = np.array([p["source"] for p in r["paires"]], dtype=float)
    prof = profil_de_couverture(sources, empreinte > 0.5, pas=pas)

    # ⚠⚠⚠ LE POINT DE COMPARAISON EST LE CAS RÉDUIT, RAMENÉ À CETTE GRILLE. Sans lui « 31 % de
    # couverture » ne dit pas si c'est mieux qu'avant : les 55 repères d'origine vivent dans une
    # image huit fois plus petite, donc leurs positions ET leurs rayons doivent être remis à
    # l'échelle avant toute comparaison.
    avant = {}
    if APPARIES.is_file():
        d = json.loads(APPARIES.read_text())
        forme = d.get("forme_carte") or [1, 1]
        fr = carte.shape[0] / forme[0]
        fc = carte.shape[1] / forme[1]
        anciennes = np.array([[p["source"][0] * fr, p["source"][1] * fc]
                              for p in d.get("paires", [])], dtype=float)
        avant = dict(repères=len(anciennes), facteur_de_remise_a_l_echelle=[round(fr, 4),
                                                                           round(fc, 4)],
                     etendue=etendue_interdecile(anciennes, carte.shape),
                     couverture=profil_de_couverture(anciennes, empreinte > 0.5, pas=pas))

    tous = utilisables(trous(masque))
    # ⚠⚠⚠ LE COMPTE BRUT DES DEUX CÔTÉS, ET LE TÉMOIN DE RÉDUCTION. Sans eux, « 14 trous contre
    # 71 » se lit comme un filtre trop sévère ; avec eux, il se lit comme ce qu'il est.
    support_plein = (carte > 0).astype(np.uint8) * 255
    reduite = rec.carte_publiee_reduite(recette)
    fond = dict(pleine_resolution=composantes_du_fond(support_plein),
                pleine_reduite_x8=composantes_du_fond(reduire_le_support(support_plein)))
    if reduite is not None:
        fond["reduite_publiee"] = composantes_du_fond(
            (reduite[0] > 0).astype(np.uint8) * 255)
    return dict(carte_publiee=nom, recette=recette, forme_carte=list(carte.shape),
                forme_masque=list(masque.shape), pas_de_couverture=pas,
                echelle=[round(t["echelle_lignes"], 5), round(t["echelle_colonnes"], 5)],
                aire_minimale_cible=aire_cible,
                trous_du_masque_utilisables=len(tous),
                reperes_transportables=r["reperes_transportables"],
                trous_du_support=r["trous_du_support"],
                distance_mediane=r["distance_mediane"],
                distance_p10=r["distance_p10"],
                distance_temoin_mediane=r["distance_temoin_mediane"],
                bat_le_temoin=r["bat_le_temoin"],
                composantes_du_fond=fond,
                etendue=etendue_interdecile(sources, carte.shape),
                couverture=prof, cas_reduit=avant, paires=r["paires"])


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    emp = np.zeros((200, 200), dtype=bool)
    emp[50:150, 50:150] = True
    un = np.array([[100.0, 100.0]])
    v("un repère au centre couvre tout quand le rayon dépasse l'empreinte",
      couverture(un, emp, 500.0, pas=2) == 1.0)
    v("... et rien quand le rayon est nul",
      couverture(un, emp, 0.0, pas=2) < 0.01, str(couverture(un, emp, 0.0, pas=2)))
    v("aucun repère ne couvre rien", couverture(np.zeros((0, 2)), emp, 500.0) == 0.0)
    c1 = couverture(un, emp, 20.0, pas=2)
    c2 = couverture(un, emp, 40.0, pas=2)
    v("la couverture croît avec le rayon", c2 > c1, f"{c1:.3f} puis {c2:.3f}")

    # ⚠⚠⚠ LE CONTRÔLE QUI DISCRIMINE : à COMPTE ÉGAL, des repères étalés couvrent plus que des
    # repères groupés. Sans lui, `couverture` pourrait ne compter que les repères et la mesure
    # dirait la même chose d'un tas et d'un semis, ce qui est exactement l'erreur que ce fichier
    # existe pour ne pas commettre.
    groupes = np.array([[60.0, 60.0], [62.0, 60.0], [60.0, 62.0], [62.0, 62.0]])
    etales = np.array([[60.0, 60.0], [140.0, 60.0], [60.0, 140.0], [140.0, 140.0]])
    cg = couverture(groupes, emp, 30.0, pas=2)
    ce = couverture(etales, emp, 30.0, pas=2)
    v("à compte égal, des repères étalés couvrent PLUS que des repères groupés",
      ce > 2.0 * cg, f"{cg:.3f} groupés contre {ce:.3f} étalés")

    # ⚠⚠ Et la couverture ne compte QUE l'empreinte : un rectangle aux trois quarts vide ne doit
    # pas diluer le résultat, sinon la mesure porterait sur la forme de l'image.
    creuse = np.zeros((200, 200), dtype=bool)
    creuse[90:110, 90:110] = True
    v("les cellules hors empreinte ne diluent pas la couverture",
      couverture(un, creuse, 30.0, pas=2) == 1.0,
      str(couverture(un, creuse, 30.0, pas=2)))
    v("une empreinte vide rend zéro sans lever",
      couverture(un, np.zeros((200, 200), dtype=bool), 30.0) == 0.0)

    # --- le compte brut et son témoin de réduction ---
    sup = np.full((240, 240), 255, dtype=np.uint8)
    sup[100:120, 100:120] = 0          # un vrai trou intérieur
    sup[0:10, 0:10] = 0                # une baie ouverte sur le bord
    f = composantes_du_fond(sup, aires=(4, 64))
    v("le compte brut sépare l'intérieur du bord",
      f["interieures"] == 1 and f["touchant_le_bord"] == 1, str(f))
    v("... et le classe par aire", f["par_aire"]["4"] == 1 and f["par_aire"]["64"] == 1, str(f))
    vide = composantes_du_fond(np.full((20, 20), 255, dtype=np.uint8))
    v("un support sans trou rend zéro sans lever", vide["composantes"] == 0, str(vide))

    r8 = reduire_le_support(sup, 8)
    v("la réduction divise bien la forme par le facteur", r8.shape == (30, 30), str(r8.shape))
    fr8 = composantes_du_fond(r8, aires=(1,))
    v("... et un trou de 20 px sur 8 survit à la réduction",
      fr8["interieures"] == 1, str(fr8))
    # ⚠⚠ LE CONTRÔLE QUI REND LE TÉMOIN CAPABLE D'ÉCHOUER : la règle « dès qu'il y a de la
    # matière » REFERME les trous plus petits que le bloc. Un témoin qui les garderait ne
    # pourrait pas montrer qu'une réduction en fabrique ou en efface.
    fin = np.full((240, 240), 255, dtype=np.uint8)
    fin[100:104, 100:104] = 0
    v("... alors qu'un trou plus petit que le bloc disparaît",
      composantes_du_fond(reduire_le_support(fin, 8), aires=(1,))["interieures"] == 0)
    v("... et il existait bien avant la réduction",
      composantes_du_fond(fin, aires=(1,))["interieures"] == 1)

    # --- l'étendue, qui doit distinguer densité et extension ---
    dense = np.array([[100.0 + k * 0.1, 100.0 + k * 0.1] for k in range(200)])
    large = np.array([[60.0, 60.0], [140.0, 60.0], [60.0, 140.0], [140.0, 140.0]])
    ed = etendue_interdecile(dense, (200, 200))
    el = etendue_interdecile(large, (200, 200))
    # ⚠⚠⚠ LE CONTRÔLE QUI FAIT TOUT LE TRAVAIL : deux cents repères entassés doivent avoir une
    # étendue PLUS PETITE que quatre repères aux coins. Sans lui, une mesure qui rendrait le
    # compte déguisé passerait, et c'est exactement l'erreur que ce champ existe pour empêcher.
    v("un semis dense mais étroit a une étendue plus petite qu'un semis clairsemé et large",
      ed["part_de_la_hauteur"] < el["part_de_la_hauteur"],
      f"{ed['part_de_la_hauteur']} contre {el['part_de_la_hauteur']} "
      f"pour {ed['repères']} contre {el['repères']} repères")
    v("... et le compte est rendu à côté, pas confondu avec elle",
      ed["repères"] == 200 and el["repères"] == 4)
    # ⚠ Interdécile et non min-max : deux égarés ne doivent pas gonfler l'étendue.
    egares = np.vstack([dense, [[0.0, 0.0], [199.0, 199.0]]])
    v("deux repères égarés ne gonflent pas l'étendue",
      etendue_interdecile(egares, (200, 200))["part_de_la_hauteur"]
      < 2.0 * ed["part_de_la_hauteur"],
      str(etendue_interdecile(egares, (200, 200))["part_de_la_hauteur"]))
    v("un semis vide rend un compte nul sans lever",
      etendue_interdecile(np.zeros((0, 2)), (200, 200))["repères"] == 0)

    prof = profil_de_couverture(un, emp, rayons=(10, 20, 40), pas=2)
    v("le profil rend un point par rayon, dans l'ordre",
      [p["rayon"] for p in prof] == [10, 20, 40], str(prof))
    v("... et il est croissant",
      prof[0]["part"] <= prof[1]["part"] <= prof[2]["part"], str([p["part"] for p in prof]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--recette", default="new_canon")
    p.add_argument("--pas", type=int, default=16, help="pas d'échantillonnage de la couverture")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.recette, pas=a.pas)
    print(f"carte {r['forme_carte'][0]} × {r['forme_carte'][1]}, échelle {r['echelle']}")
    print(f"trous du masque utilisables        {r['trous_du_masque_utilisables']:>8}")
    print(f"dont transportables ici            {r['reperes_transportables']:>8}")
    print(f"trous du support publié            {r['trous_du_support']:>8}")
    print(f"distance d'appariement, médiane    {r['distance_mediane']:>8}")
    print(f"témoin, même compte au hasard      {r['distance_temoin_mediane']:>8}")
    print(f"bat le témoin : {'OUI' if r['bat_le_temoin'] else 'NON'}\n")
    f = r["composantes_du_fond"]
    print(f"{'support':<22} {'composantes':>12} {'intérieures':>12} {'aire >= 4':>10}")
    print("-" * 60)
    for cle, nom in (("reduite_publiee", "réduit publié (.jpg)"),
                     ("pleine_reduite_x8", "pleine réduite ×8"),
                     ("pleine_resolution", "pleine (.tif)")):
        if cle in f:
            e = f[cle]
            print(f"{nom:<22} {e['composantes']:>12} {e['interieures']:>12} "
                  f"{e['par_aire'].get('4', 0):>10}")
    print()
    e, ea = r["etendue"], r["cas_reduit"].get("etendue", {})
    print(f"étendue interdécile du semis : {e['part_de_la_hauteur'] * 100:.1f} % de la hauteur "
          f"× {e['part_de_la_largeur'] * 100:.1f} % de la largeur")
    if ea:
        print(f"                 au cas réduit : {ea['part_de_la_hauteur'] * 100:.1f} % "
              f"× {ea['part_de_la_largeur'] * 100:.1f} %\n")
    print(f"{'rayon':>8} {'couverture':>12} {'cas réduit':>12}")
    print("-" * 34)
    anciennes = {c["rayon"]: c["part"] for c in r["cas_reduit"].get("couverture", [])}
    for c in r["couverture"]:
        av = anciennes.get(c["rayon"])
        print(f"{c['rayon']:>8} {c['part'] * 100:>11.1f}% "
              f"{'—' if av is None else f'{av * 100:>10.1f}%'}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
