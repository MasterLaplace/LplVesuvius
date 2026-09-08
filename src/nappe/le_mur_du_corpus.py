#!/usr/bin/env python3
"""La portée mesure-t-elle le MARCHEUR, ou le mur du corpus ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL AUDITE LE RESULTAT CENTRAL DU DEPOT. `la_portee_du_raccrochage`
publie cote a cote « la borne (oracle) : 6 » et « ce que le corpus autorise : 6 », et
`la_portee_tient_elle_ailleurs` conclut que le signe tient sur **5/5 ancres**. Personne n'avait
demande si les deux 6 sont le meme 6 — et ils le sont. **L'oracle est au mur du corpus sur les
CINQ ancres**, sans exception : 6/6, 5/5, 4/4, 3/3, 2/2.

⭐⭐⭐ UNE PORTEE EGALE AU PLAFOND DU CORPUS EST UNE OBSERVATION **CENSUREE A DROITE**. Elle dit
« au moins ce nombre » et rien de plus. « La borne vaut 6 » n'est donc pas etabli : la vraie borne
est inconnue et **au moins** 6. C'est le peche numero un de ce depot — une limite de grille
publiee comme une limite materielle — present dans son resultat le plus cite.

⭐⭐⭐ ET LES CINQ ANCRES NE SONT PAS CINQ REPLICATIONS. Elles meurent toutes au **meme** mur : un
saut de 1000,6 µm entre les spires **10 et 11**, la ou le pas nominal en demande 135,5. Le plafond
de chaque ancre vaut donc exactement `10 - ancre` — 6, 5, 4, 3, 2 — et « 5/5 ancres » compte cinq
fois un seul defaut du corpus.

⚠⚠ AUCUN MARCHEUR DE CETTE FAMILLE NE PEUT FRANCHIR CE SAUT, l'oracle compris, et c'est
arithmetique : le decalage atteignable est de **±67,8 µm**, une demi-feuille exactement, quand le
bras en demande **865,1 µm** de plus que le pas nominal — **12,8 demi-feuilles**. Le bras 7 n'est
donc pas un echec de methode, c'est une impossibilite de construction.

⚠ ET DEUX ANCRES NE DISTINGUENT RIEN DU TOUT. A l'ancre 7 (plafond 3) les sept marcheurs aveugles
rendent tous **2** ; a l'ancre 8 (plafond 2) tous **1**. Une ancre dont le plafond vaut 2 offre
trois valeurs possibles dont une censuree : elle ne peut pas separer deux methodes, quelles
qu'elles soient. Les compter comme des confirmations, c'est compter du silence.

⚠ Ce fichier ne remesure RIEN : il relit deux artefacts versionnes et croise ce que ni l'un ni
l'autre ne croisait. Il tourne hors ligne.

Usage :
    uv run python src/nappe/le_mur_du_corpus.py
    uv run python src/nappe/le_mur_du_corpus.py --verifier
    uv run python src/nappe/le_mur_du_corpus.py --json docs/mesures/le_mur_du_corpus.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
MARCHE = RACINE / "docs" / "mesures" / "la_portee_du_raccrochage.json"
AILLEURS = RACINE / "docs" / "mesures" / "la_portee_tient_elle_ailleurs.json"

# ⚠ L'oracle est la BORNE de la famille, donc c'est lui dont la censure coute le plus cher : une
# borne censuree ne borne rien. Il est nomme ici parce que le verdict le distingue des autres.
BORNE = "oracle"


def premier_saut(bras: list[dict]) -> dict | None:
    """Le premier bras que le corpus publie hors du pas nominal — le mur, s'il existe.

    ⚠⚠ LE PREMIER, PAS LE PIRE. Une portée s'arrête au **premier** échec, donc c'est le premier
    saut qui plafonne et non le plus grand : publier le plus grand ferait croire à un plafond
    plus lointain que celui qui s'applique.
    """
    for b in bras:
        if not b["au_pas_nominal"]:
            return b
    return None


def censure(portees: dict, plafond: int) -> dict:
    """Chaque marcheur : sa portée, et si elle est collée au plafond du corpus.

    ⚠⚠⚠ UNE PORTEE EGALE AU PLAFOND EST CENSUREE A DROITE. Le marcheur a réussi tous les bras
    que le corpus offre au pas nominal ; sa vraie portée est **au moins** ce nombre, et rien
    dans cette mesure ne dit de combien. La lire comme une valeur, c'est publier une limite de
    corpus comme une limite de méthode.

    ⚠ Une portée SUPERIEURE au plafond serait un marcheur qui a franchi le saut ; c'est possible
    en principe et le champ le dit plutôt que de le supposer impossible.
    """
    out = {}
    for nom, p in portees.items():
        out[nom] = {"portee": int(p), "plafond": int(plafond),
                    "censuree": bool(p >= plafond),
                    "marge": int(plafond - p)}
    return out


def pouvoir_de_separer(portees: dict, plafond: int) -> int:
    """Combien de valeurs DISTINCTES et non censurées les marcheurs aveugles rendent ici.

    ⭐ C'est la dynamique réelle de l'ancre. Une ancre où tous les marcheurs rendent le même
    nombre ne confirme ni n'infirme quoi que ce soit : elle ne peut pas séparer deux méthodes,
    donc la compter comme une réplication compte du silence.

    ⚠ L'oracle est exclu : il n'est pas une méthode candidate, c'est la borne de la famille.
    """
    vues = {p for n, p in portees.items() if n != BORNE and p < plafond}
    return len(vues)


def mesurer(marche: Path = MARCHE, ailleurs: Path = AILLEURS) -> dict:
    """Croise les portées publiées avec le plafond que le corpus impose à chaque ancre."""
    m = json.loads(marche.read_text())
    a = json.loads(ailleurs.read_text())
    saut = premier_saut(m["bras_du_corpus"])
    glissement = float(m["glissement_maximal_um"])
    demi = float(m["demi_feuille_um"])

    lignes = []
    for ligne in a["lignes"]:
        plafond = int(ligne["bras_au_pas_nominal"])
        par = censure(ligne["portees"], plafond)
        lignes.append({
            "ancre": int(ligne["ancre"]),
            "bras_offerts": len(ligne["spires_visees"]),
            "plafond": plafond,
            # ⭐ LE PLAFOND EST-IL EXPLIQUE PAR LE MEME MUR ? Si oui, les cinq ancres partagent
            # un seul défaut du corpus et ne sont pas cinq réplications indépendantes.
            "plafond_attendu_du_mur": (int(saut["de"]) - int(ligne["ancre"])) if saut else None,
            "marcheurs": par,
            "censures": sorted(n for n, x in par.items() if x["censuree"]),
            "pouvoir_de_separer": pouvoir_de_separer(ligne["portees"], plafond),
        })

    censure_borne = [l["ancre"] for l in lignes if l["marcheurs"][BORNE]["censuree"]]
    return {
        "source_marche": str(marche.relative_to(RACINE)),
        "source_ailleurs": str(ailleurs.relative_to(RACINE)),
        "fragment": m["fragment"],
        "demi_feuille_um": demi,
        "glissement_maximal_um": glissement,
        "mur": saut,
        # ⚠⚠ CE RAPPORT EST CE QUI REND LE MUR INFRANCHISSABLE PAR CONSTRUCTION, et non
        # « difficile » : ce que le bras demande, divisé par ce que la famille peut décaler.
        "mur_en_demi_feuilles": (round(saut["ecart_au_pas_um"] / demi, 1) if saut else None),
        "mur_en_glissements": (round(saut["ecart_au_pas_um"] / glissement, 1) if saut else None),
        "ancres": len(lignes),
        "lignes": lignes,
        "ancres_ou_la_borne_est_censuree": censure_borne,
        "la_borne_est_censuree_partout": len(censure_borne) == len(lignes),
        "le_meme_mur_explique_tout": all(l["plafond"] == l["plafond_attendu_du_mur"]
                                         for l in lignes) if saut else False,
        "ancres_sans_pouvoir_de_separer": [l["ancre"] for l in lignes
                                           if l["pouvoir_de_separer"] <= 1],
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  FAIL {nom} — {detail}")

    # --- la mécanique, sur des données fabriquées ---------------------------------------------
    bras = [dict(bras=1, de=1, vers=2, ecart_au_pas_um=2.0, au_pas_nominal=True),
            dict(bras=2, de=2, vers=3, ecart_au_pas_um=900.0, au_pas_nominal=False),
            dict(bras=3, de=3, vers=4, ecart_au_pas_um=1.0, au_pas_nominal=True),
            dict(bras=4, de=4, vers=5, ecart_au_pas_um=999.0, au_pas_nominal=False)]
    # ⚠⚠ LE PREMIER SAUT, PAS LE PIRE : une portée s'arrête au premier échec.
    v("le mur est le PREMIER saut, pas le plus grand", premier_saut(bras)["bras"] == 2,
      str(premier_saut(bras)))
    v("... et un corpus sans saut n'a pas de mur", premier_saut(bras[:1]) is None)

    c = censure({"a": 3, "b": 5, "c": 6}, plafond=5)
    v("une portée sous le plafond n'est pas censurée", not c["a"]["censuree"] and c["a"]["marge"] == 2)
    v("... une portée AU plafond l'est", c["b"]["censuree"] and c["b"]["marge"] == 0)
    # ⚠ Franchir le saut est possible en principe ; le dire plutôt que le supposer impossible.
    v("... et une portée au-DELA l'est aussi, avec une marge négative",
      c["c"]["censuree"] and c["c"]["marge"] == -1, str(c["c"]))

    # ⭐ Le pouvoir de séparer ne compte que les valeurs NON censurées, et jamais la borne.
    v("une ancre où tous rendent la même valeur ne sépare rien",
      pouvoir_de_separer({"x": 2, "y": 2, "oracle": 3}, plafond=3) == 1)
    v("... et deux valeurs distinctes en séparent deux",
      pouvoir_de_separer({"x": 1, "y": 2, "oracle": 3}, plafond=3) == 2)
    v("... la borne est exclue du compte",
      pouvoir_de_separer({"x": 1, "oracle": 2}, plafond=5) == 1, "l'oracle ne doit pas compter")

    if not (MARCHE.is_file() and AILLEURS.is_file()):
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    r = mesurer()
    par_ancre = {l["ancre"]: l for l in r["lignes"]}

    # --- le verdict sur les artefacts réels ---------------------------------------------------
    # ⭐⭐⭐ LA BORNE EST CENSUREE PARTOUT : « la borne vaut 6 » n'est pas établi.
    v("la borne est collée au plafond du corpus sur les CINQ ancres",
      r["la_borne_est_censuree_partout"] and len(r["ancres_ou_la_borne_est_censuree"]) == 5,
      str(r["ancres_ou_la_borne_est_censuree"]))
    # ⭐⭐⭐ UN SEUL MUR EXPLIQUE LES CINQ PLAFONDS : les ancres ne sont pas indépendantes.
    v("un seul saut du corpus explique les cinq plafonds", r["le_meme_mur_explique_tout"],
      str([(l["ancre"], l["plafond"], l["plafond_attendu_du_mur"]) for l in r["lignes"]]))
    v("... et ce saut est entre les spires 10 et 11",
      (r["mur"]["de"], r["mur"]["vers"]) == (10, 11), str(r["mur"]))
    # ⚠⚠ INFRANCHISSABLE PAR CONSTRUCTION, pas difficile.
    v("le saut est hors de portée du décalage atteignable, d'un facteur au moins dix",
      r["mur_en_glissements"] >= 10, f"{r['mur_en_glissements']} glissements")
    v("... soit plus de douze demi-feuilles", r["mur_en_demi_feuilles"] > 12,
      str(r["mur_en_demi_feuilles"]))
    # ⚠ DEUX ANCRES NE SEPARENT RIEN : les compter comme des confirmations compte du silence.
    v("deux ancres n'ont aucun pouvoir de séparer",
      r["ancres_sans_pouvoir_de_separer"] == [7, 8],
      str([(l["ancre"], l["pouvoir_de_separer"]) for l in r["lignes"]]))
    v("... et à l'ancre 8 tous les marcheurs aveugles rendent le même nombre",
      len({x["portee"] for n, x in par_ancre[8]["marcheurs"].items() if n != BORNE}) == 1,
      str({n: x["portee"] for n, x in par_ancre[8]["marcheurs"].items()}))
    # ⭐ Le plafond décroît d'une unité par ancre, ce qui est la signature d'un mur unique.
    v("le plafond décroît exactement d'une unité par ancre",
      [l["plafond"] for l in r["lignes"]] == [6, 5, 4, 3, 2],
      str([l["plafond"] for l in r["lignes"]]))
    # ⚠⚠ ET L'ANCRE 4 RESTE INFORMATIVE : sans ça, tout le résultat de portée tomberait, et il
    # ne tombe pas — c'est la moitié du verdict qu'il ne faut pas exagérer.
    v("l'ancre 4 sépare encore, elle",
      par_ancre[4]["pouvoir_de_separer"] >= 3, str(par_ancre[4]["pouvoir_de_separer"]))
    v("... et le lissage y est sous le plafond, donc sa portée mesure bien le marcheur",
      not par_ancre[4]["marcheurs"]["rien_lisse"]["censuree"],
      str(par_ancre[4]["marcheurs"]["rien_lisse"]))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()

    r = mesurer()
    mur = r["mur"]
    print(f"{r['fragment']} · demi-feuille {r['demi_feuille_um']} µm · glissement atteignable "
          f"±{r['glissement_maximal_um']} µm\n")
    print(f"⛔ LE MUR : bras {mur['bras']}, spires {mur['de']} → {mur['vers']}, "
          f"{mur['ecart_um']} µm soit {mur['ecart_au_pas_um']} µm hors du pas nominal — "
          f"{r['mur_en_demi_feuilles']} demi-feuilles, {r['mur_en_glissements']}× le glissement "
          f"atteignable.\n")
    marcheurs = [n for n in r["lignes"][0]["marcheurs"] if n != BORNE]
    print(f"{'ancre':>5} {'offerts':>8} {'plafond':>8} {'sépare':>7}  "
          + " ".join(f"{n[:9]:>9}" for n in marcheurs) + f" {BORNE:>8}")
    for l in r["lignes"]:
        cases = " ".join(
            f"{str(l['marcheurs'][n]['portee']) + ('*' if l['marcheurs'][n]['censuree'] else ''):>9}"
            for n in marcheurs)
        o = l["marcheurs"][BORNE]
        print(f"{l['ancre']:>5} {l['bras_offerts']:>8} {l['plafond']:>8} "
              f"{l['pouvoir_de_separer']:>7}  {cases} "
              f"{str(o['portee']) + ('*' if o['censuree'] else ''):>8}")
    print("\n* = collée au plafond du corpus, donc CENSUREE A DROITE : « au moins », pas « vaut »")
    if r["la_borne_est_censuree_partout"]:
        print(f"\n⛔⛔⛔ la borne est censurée sur {r['ancres']}/{r['ancres']} ancres — "
              "« la borne vaut 6 » n'est PAS établi, la vraie borne est inconnue et ≥ 6")
    if r["le_meme_mur_explique_tout"]:
        print(f"⛔⛔ un SEUL saut du corpus explique les {r['ancres']} plafonds "
              f"(plafond = {mur['de']} − ancre) : les ancres ne sont pas des réplications")
    if r["ancres_sans_pouvoir_de_separer"]:
        print(f"⛔ ancres sans aucun pouvoir de séparer : "
              f"{r['ancres_sans_pouvoir_de_separer']} — elles ne confirment rien")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
