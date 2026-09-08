#!/usr/bin/env python3
"""Existe-t-il une boite ou la portee cesse d'etre censuree par le corpus ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `le_mur_du_corpus` etablit que toutes les portees publiees sont
**censurees a droite** : l'oracle est colle au plafond du corpus sur les cinq ancres, et le
plafond vient d'un seul saut — les spires 10 et 11, voisines par leur numero, a 1000,6 µm l'une
de l'autre. La question suivante n'est pas « comment marcher mieux » mais **« ou peut-on
seulement MESURER »** : existe-t-il, sur ce meme fragment, un placement de boite ou la chaine des
spires publiees tient au pas nominal sur plus de six bras ?

⭐⭐ ET LA BOITE SE CHOISIT SUR LE CORPUS, JAMAIS SUR LE RESULTAT. Ce balayage ne fait tourner
aucun marcheur : il ne regarde que ce que les spires publiees demandent les unes aux autres.
Choisir la boite ou la marche est belle serait choisir l'endroit ou le verdict arrange, ce que ce
depot refuse partout ailleurs ; choisir celle ou le corpus est mesurable est le contraire — c'est
retirer une limite d'instrument, pas fabriquer un resultat.

⚠⚠ CE QUE CE FICHIER NE DIT PAS, ET QU'IL NE FAUT PAS LUI FAIRE DIRE : qu'une chaine plus longue
rende la marche meilleure. Elle rend la MESURE capable de juger plus loin. Un marcheur peut
parfaitement echouer au deuxieme bras d'une chaine qui en offre dix — c'est precisement ce qu'on
veut pouvoir observer, et qu'un plafond a six interdit.

⚠ La chaine est comptee comme `mesurer` la construit : l'ancre est la spire la plus BASSE de la
boite, les bras montent, et un bras existe si les deux spires ont assez de cellules dans la
boite. Compter autrement mesurerait une chaine que le marcheur ne parcourrait pas.

Usage :
    uv run python src/nappe/ou_poser_la_boite.py --verifier
    uv run python src/nappe/ou_poser_la_boite.py --cote 960 \\
        --json docs/mesures/ou_poser_la_boite.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

# ⚠ La boite courante est IMPORTEE et jamais retapee : un centre recopie ici cesserait d'etre
# celui de la mesure le jour ou l'un des deux bouge, et la comparaison « mieux que l'actuelle »
# porterait sur une boite qui n'existe pas.
from le_raccrochage_a_la_matiere import BOITE_CENTRE  # noqa: E402

MINIMUM = 30
COTE = 960.0


def distances_par_paire(corpus: dict) -> dict:
    """Pour chaque paire de spires (i < j) : la distance de chaque cellule de i au nuage de j.

    ⚠⚠ TOUTES LES PAIRES, PAS SEULEMENT LES RANGS VOISINS. Une spire trop pauvre dans une boite
    est ecartee, donc la chaine que le marcheur parcourt peut sauter un rang — et le bras devient
    alors i→j avec j > i+1. Ne precalculer que les rangs voisins rendrait ces bras invisibles.

    ⚠ La distance va des cellules de i vers le nuage ENTIER de j, exactement comme `mesurer` :
    restreindre la cible a la boite ferait grandir la distance parce que la cible manque, ce qui
    se lit comme un corpus mauvais.
    """
    from le_pas_normal_atteint_la_spire import distance_a  # noqa: PLC0415

    voxel_um = float(corpus["voxel_um"])
    rangs = sorted(corpus["grilles"])
    cellules = {r: corpus["grilles"][r][0][corpus["grilles"][r][1]] for r in rangs}
    out = {}
    for i in rangs:
        for j in rangs:
            if j <= i:
                continue
            out[(i, j)] = distance_a(cellules[i], cellules[j], voxel_um)
    return {"cellules": cellules, "distances": out, "voxel_um": voxel_um,
            "ecart_um": float(corpus["ecart_um"]), "rangs": rangs}


def chaine_dans_la_boite(pre: dict, centre, cote: float, minimum: int = MINIMUM) -> dict:
    """Les spires de la boite, et la plus longue chaine consecutive au pas nominal.

    ⭐ LE PLAFOND EST LA GRANDEUR RENDUE : c'est le nombre de bras qu'un marcheur parfait
    parcourrait avant que le corpus lui demande un saut qu'aucun membre de la famille ne sait
    faire. Au-dela, toute portee mesuree est censuree.
    """
    centre = np.asarray(centre, dtype=np.float64)
    lo, hi = centre - cote / 2, centre + cote / 2
    ecart = pre["ecart_um"]
    demi_feuille = ecart / 2.0
    dedans, comptes = [], {}
    for r in pre["rangs"]:
        p = pre["cellules"][r]
        m = ((p >= lo) & (p <= hi)).all(axis=-1)
        n = int(m.sum())
        comptes[r] = n
        if n >= minimum:
            dedans.append((r, m))
    if len(dedans) < 2:
        return {"centre": [float(x) for x in centre], "cote": cote, "spires": len(dedans),
                "chaine": [r for r, _ in dedans], "plafond": 0, "bras": []}
    chaine = [r for r, _ in dedans]
    masques = dict(dedans)
    bras = []
    plafond = 0
    encore = True
    for k, (de, vers) in enumerate(zip(chaine, chaine[1:]), start=1):
        d = pre["distances"][(de, vers)][masques[de]]
        g = float(np.median(d))
        au_pas = bool(abs(g - ecart) < demi_feuille)
        bras.append({"bras": k, "de": de, "vers": vers, "ecart_um": round(g, 1),
                     "ecart_au_pas_um": round(abs(g - ecart), 1), "au_pas_nominal": au_pas})
        # ⚠⚠ LE PLAFOND S'ARRETE AU PREMIER BRAS HORS DU PAS, comme une portee s'arrete au
        # premier echec. Compter les bras sains au-dela publierait un plafond qu'aucune marche
        # ne peut atteindre, puisqu'elle ne passe pas le saut.
        if encore and au_pas:
            plafond = k
        elif not au_pas:
            encore = False
    return {"centre": [float(x) for x in centre], "cote": cote, "spires": len(chaine),
            "chaine": chaine, "plafond": plafond, "bras": bras,
            "cellules_par_spire": comptes}


def balayer(pre: dict, cote: float = COTE, pas: float = 480.0,
            minimum: int = MINIMUM) -> list[dict]:
    """Toutes les boites d'un treillis couvrant le fragment, avec leur plafond.

    ⚠ Le treillis est REGULIER et couvre l'etendue des spires publiees. Un balayage centre sur
    la boite actuelle chercherait autour d'elle et raterait ce qui vaut ailleurs.
    """
    tout = np.concatenate([pre["cellules"][r] for r in pre["rangs"]])
    lo, hi = tout.min(axis=0), tout.max(axis=0)
    # ⚠⚠ UN AXE PLUS COURT QUE LA BOITE DONNE UN SEUL CENTRE, PAS ZERO. Un `arange` dont la borne
    # haute passe sous la borne basse rend un tableau vide, donc le produit cartesien est vide et
    # le balayage n'essaie AUCUNE boite — en rendant « aucune boite ne fait mieux », qui se lit
    # comme un verdict alors que c'est un balayage qui n'a pas eu lieu.
    axes = []
    for a in range(3):
        if hi[a] - lo[a] <= cote:
            axes.append(np.array([(lo[a] + hi[a]) / 2.0]))
        else:
            axes.append(np.arange(lo[a] + cote / 2, hi[a] - cote / 2 + 1e-9, pas))
    out = []
    for z in axes[0]:
        for y in axes[1]:
            for x in axes[2]:
                out.append(chaine_dans_la_boite(pre, (z, y, x), cote, minimum))
    return out


def mesurer(cote: float = COTE, pas: float = 480.0, minimum: int = MINIMUM,
            corpus: dict | None = None) -> dict:
    """Le plafond de la boite actuelle, et le meilleur plafond du fragment."""
    if corpus is None:
        from le_corpus_des_spires import corpus_publie  # noqa: PLC0415

        corpus = corpus_publie()
    pre = distances_par_paire(corpus)
    actuelle = chaine_dans_la_boite(pre, BOITE_CENTRE, cote, minimum)
    toutes = balayer(pre, cote, pas, minimum)
    # ⚠ Le tri departage a plafond egal par le nombre de spires, puis par le centre, pour que
    # deux executions rendent la MEME meilleure boite : un maximum choisi au hasard parmi des
    # ex aequo ferait bouger le chiffre publie sans qu'aucune donnee ait change.
    ordre = sorted(toutes, key=lambda b: (-b["plafond"], -b["spires"], b["centre"]))
    meilleure = ordre[0] if ordre else actuelle
    return {
        "cote": cote, "pas_du_treillis": pas, "minimum_cellules": minimum,
        "ecart_um": pre["ecart_um"], "demi_feuille_um": pre["ecart_um"] / 2.0,
        "boites_essayees": len(toutes),
        "boite_actuelle": actuelle,
        "meilleure_boite": meilleure,
        "gain_de_plafond": meilleure["plafond"] - actuelle["plafond"],
        "plafond_maximal": meilleure["plafond"],
        # ⭐ Combien de boites font au moins aussi bien que l'actuelle : un maximum isole est un
        # accident de treillis, plusieurs boites est une propriete du fragment.
        "boites_au_moins_aussi_bonnes": sum(1 for b in toutes
                                            if b["plafond"] >= actuelle["plafond"]),
        "boites_meilleures": sum(1 for b in toutes if b["plafond"] > actuelle["plafond"]),
        "meilleures_boites": [b for b in ordre[:5]],
        # ⭐⭐ LA DISTRIBUTION, ET PAS SEULEMENT LE MAXIMUM. Un maximum sans sa distribution ne
        # dit pas si le fragment est bon quelque part ou mauvais partout : « une boite sur cent
        # quarante-quatre fait mieux » est le verdict, et il n'est lisible qu'avec le reste.
        "plafonds": {str(k): sum(1 for b in toutes if b["plafond"] == k)
                     for k in sorted({b["plafond"] for b in toutes})},
        # ⚠⚠ LE CORPUS ECHOUE DANS LES DEUX SENS, et il faut le compter : un bras trop LOIN est
        # un trou de numerotation, un bras trop PRES est une paire de spires que la boite ne
        # separe pas. Les confondre sous « hors du pas nominal » perdrait ce qui distingue une
        # lacune d'un doublon.
        "bras_trop_loin": sum(1 for b in toutes for a in b["bras"]
                              if not a["au_pas_nominal"] and a["ecart_um"] > pre["ecart_um"]),
        "bras_trop_pres": sum(1 for b in toutes for a in b["bras"]
                              if not a["au_pas_nominal"] and a["ecart_um"] < pre["ecart_um"]),
        "bras_au_total": sum(len(b["bras"]) for b in toutes),
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    from le_corpus_des_spires import corpus_fabrique, geometrie_fabriquee  # noqa: PLC0415

    # ⚠ LE `foyer` DE LA FIXTURE EST LE CENTRE DU CERCLE, PAS CELUI DE LA MATIERE : il vit
    # quatre mille voxels sous les surfaces. Poser la boite dessus rend une chaine vide, ce qui
    # ressemble a un decoupage casse. Les spires fabriquees sont centrees sur `BOITE_CENTRE`.
    g0 = geometrie_fabriquee(6, 14, 3.0, 4000.0, 0.0)
    COTE_FIXTURE = 400.0
    pre = distances_par_paire(corpus_fabrique())
    # ⚠⚠ TOUTES LES PAIRES, parce qu'une spire ecartee fait sauter un rang.
    v("toutes les paires ordonnées sont précalculées",
      set(pre["distances"]) == {(i, j) for i in pre["rangs"] for j in pre["rangs"] if j > i},
      f"{len(pre['distances'])} paires pour {len(pre['rangs'])} spires")
    v("... et jamais une paire dans le mauvais sens",
      all(i < j for i, j in pre["distances"]))

    c = chaine_dans_la_boite(pre, BOITE_CENTRE, COTE_FIXTURE)
    v("la fixture donne une chaîne complète", c["spires"] == 6 and c["plafond"] == 5,
      f"spires={c['spires']} plafond={c['plafond']}")
    v("... et chaque bras publie ce que le corpus lui demande",
      len(c["bras"]) == 5 and all("au_pas_nominal" in b for b in c["bras"]),
      str([b["ecart_um"] for b in c["bras"]]))

    # ⚠⚠ UNE BOITE POSEE AILLEURS NE DOIT RENDRE AUCUNE CHAINE, sinon le découpage est décoratif.
    loin = np.asarray(BOITE_CENTRE, dtype=np.float64) + 90000.0
    vide = chaine_dans_la_boite(pre, loin, COTE_FIXTURE)
    v("une boîte posée hors de la matière ne rend aucune chaîne",
      vide["spires"] == 0 and vide["plafond"] == 0, str(vide["spires"]))

    # ⚠⚠⚠ LE PLAFOND S'ARRETE AU PREMIER SAUT, il ne compte pas les bras sains d'après.
    pre2 = distances_par_paire(corpus_fabrique(decalage_vx=0.0))
    faux = {"cellules": pre2["cellules"], "voxel_um": pre2["voxel_um"],
            "ecart_um": pre2["ecart_um"], "rangs": pre2["rangs"],
            "distances": dict(pre2["distances"])}
    trou = (pre2["rangs"][1], pre2["rangs"][2])
    faux["distances"][trou] = pre2["distances"][trou] + 900.0
    c2 = chaine_dans_la_boite(faux, BOITE_CENTRE, COTE_FIXTURE)
    v("le plafond s'arrête au premier saut, pas au dernier",
      c2["plafond"] == 1 and len(c2["bras"]) == 5,
      f"plafond={c2['plafond']} bras={[b['au_pas_nominal'] for b in c2['bras']]}")

    # ⚠ Le seuil de cellules doit être respecté, sinon il est décoratif.
    creuse = distances_par_paire(corpus_fabrique(creuse=3))
    c3 = chaine_dans_la_boite(creuse, BOITE_CENTRE, COTE_FIXTURE, minimum=MINIMUM)
    v("une spire trop pauvre est écartée de la chaîne",
      3 not in c3["chaine"], str(c3["chaine"]))
    # ⚠ Et son retrait fait SAUTER un rang : le bras devient 2→4, ce que le précalcul doit avoir.
    v("... et le bras qui l'enjambe existe quand même",
      any(b["de"] == 2 and b["vers"] == 4 for b in c3["bras"]),
      str([(b["de"], b["vers"]) for b in c3["bras"]]))

    # ⚠⚠ LE TRI DOIT ETRE DETERMINISTE : deux exécutions doivent rendre la MÊME meilleure boîte.
    # ⚠ Une boite ETROITE, sinon la fixture tient entiere dedans et le treillis n'a qu'un point :
    # un balayage a une seule boite ne peut pas montrer qu'il est deterministe.
    a = mesurer(cote=150.0, pas=60.0, corpus=corpus_fabrique())
    b = mesurer(cote=150.0, pas=60.0, corpus=corpus_fabrique())
    v("le balayage est déterministe", a["meilleure_boite"]["centre"] ==
      b["meilleure_boite"]["centre"], str(a["meilleure_boite"]["centre"]))
    v("... et il essaie plus d'une boîte", a["boites_essayees"] > 1,
      str(a["boites_essayees"]))
    # ⚠⚠ UN AXE PLUS COURT QUE LA BOITE NE DOIT PAS VIDER LE BALAYAGE : « aucune boîte ne fait
    # mieux » et « aucune boîte n'a été essayée » se ressemblent, et l'un est un verdict.
    large = mesurer(cote=100000.0, pas=1000.0, corpus=corpus_fabrique())
    v("une boîte plus grande que la matière donne quand même une boîte",
      large["boites_essayees"] == 1, str(large["boites_essayees"]))
    # ⚠⚠ LES DEUX SENS D'ECHEC SONT COMPTES A PART : un bras trop LOIN est une lacune de
    # numerotation, un bras trop PRES est une paire que la boite ne separe pas. Les additionner
    # sous un seul mot perdrait ce qui les distingue.
    v("les bras hors du pas sont comptés dans les deux sens, et leur somme est cohérente",
      a["bras_trop_loin"] + a["bras_trop_pres"] <= a["bras_au_total"],
      f"{a['bras_trop_loin']} + {a['bras_trop_pres']} sur {a['bras_au_total']}")
    v("... et la distribution des plafonds couvre toutes les boîtes",
      sum(a["plafonds"].values()) == a["boites_essayees"], str(a["plafonds"]))
    v("... et le gain est la différence des deux plafonds",
      a["gain_de_plafond"] == a["meilleure_boite"]["plafond"] -
      a["boite_actuelle"]["plafond"])

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cote", type=float, default=COTE)
    p.add_argument("--pas", type=float, default=480.0)
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    r = mesurer(cote=a.cote, pas=a.pas)
    act, mei = r["boite_actuelle"], r["meilleure_boite"]
    print(f"boîte de {r['cote']:.0f} vx · treillis au pas {r['pas_du_treillis']:.0f} · "
          f"{r['boites_essayees']} boîtes essayées\n")
    print(f"{'boîte':>10} {'centre (z,y,x)':>28} {'spires':>7} {'plafond':>8}  chaîne")
    for nom, b in (("actuelle", act), ("meilleure", mei)):
        c = " ".join(f"{x:.0f}" for x in b["centre"])
        print(f"{nom:>10} {c:>28} {b['spires']:>7} {b['plafond']:>8}  {b['chaine']}")
    print(f"\ngain de plafond : {r['gain_de_plafond']:+d}  ·  "
          f"{r['boites_meilleures']} boîte(s) sur {r['boites_essayees']} font mieux que "
          f"l'actuelle")
    print("plafonds atteints : " + " · ".join(f"{k} → {n} boîte(s)"
                                              for k, n in r["plafonds"].items()))
    hors = r["bras_trop_loin"] + r["bras_trop_pres"]
    print(f"bras hors du pas nominal : {hors} sur {r['bras_au_total']} "
          f"({r['bras_trop_loin']} trop loin, {r['bras_trop_pres']} trop près)")
    if r["gain_de_plafond"] > 0:
        print(f"\n⭐ une portée pourrait être mesurée jusqu'à {r['plafond_maximal']} bras "
              f"au lieu de {act['plafond']} — sans changer d'objet")
    else:
        print("\n⛔ aucune boîte de ce fragment ne desserre le plafond : le corpus, et non le "
              "placement, est la limite")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
