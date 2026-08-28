#!/usr/bin/env python3
"""Ce qui distingue un rouleau dont l'encre se lit d'un rouleau ou le modele est inerte.

⚠⚠ Pourquoi ce fichier existe. [`58`](../../docs/58_resolution_ou_rouleau.md) a elimine la
resolution : le temoin ou le modele atteint AUC 0,925 est deja a 9 % des conditions de
`PHerc1447` sur les deux axes. Il restait « ce rouleau-ci », un mot qui ne nomme rien. Or les
noms de volumes du depot public portent trois grandeurs -- pas de voxel, distance de
propagation, energie du faisceau -- et personne n'avait regarde comment elles se repartissent
entre les rouleaux dont l'encre est publiee et ceux ou elle ne l'est pas.

⭐ Le partage observe sur six rouleaux, et que ce fichier mesure sur tout le corpus : les
rouleaux dont l'encre est publiee ont **plusieurs** volumes, dont un fin a courte propagation
(1,1 a 2,4 µm, 0,2 m, 53 a 78 keV) ; ceux ou le modele est inerte n'en ont **qu'un**, celui de
la campagne de reperage (8,6 a 9,4 µm, 1,2 m, 113 a 116 keV).

⚠⚠ Ce que ca n'etablit PAS, et il faut le dire a chaque usage :

1. « la communaute publie une carte d'encre » n'est pas « le modele de 2023 y repond ». C'est
   une trace de ce que quelqu'un a juge lisible et a pris la peine de rendre.
2. les trois grandeurs **co-varient par campagne** : un scan fin est aussi a courte
   propagation et a basse energie. Aucune des trois n'est isolee par cette mesure-ci.
3. l'ordre de causalite n'est pas donne. Un rouleau peut n'avoir qu'un scan grossier **parce
   que** personne n'y a encore lu de texte, plutot que l'inverse.

⭐ Ce que ca fait, et c'est deja beaucoup : ca remplace « ce rouleau-ci » par une propriete
**de la campagne de scan**, qui se teste et qui s'achete. Un rouleau ne change pas ; un scan,
si.

⚠⚠⚠ LIMITE DE L'INSTRUMENT, mesuree le 2026-08-28. Ce fichier n'interroge qu'UN des deux
layouts du depot public : le bucket open-data (`*-masked.zarr`, acquisitions 2025 et 2026).
Les rouleaux scannes AVANT ont des volumes dans `full-scrolls/<Scroll>/<nom>.volpkg/volumes/`
qu'il ne compte pas, donc son `n_volumes` est un **minorant** pour eux.

Ce n'est pas un detail : le volume ou le modele atteint AUC 0,925 -- `20230205180739`, un scan
de 2023 a 7,91 µm et **54 keV** -- est precisement dans ce layout-la, donc INVISIBLE ici. Les
cinq volumes que ce fichier trouve pour `PHercParis4` sont tous posterieurs et aucun n'est
celui du resultat de reference. Une inference du genre « les rouleaux lisibles ont ete
rescannes fin » se lit donc sur une liste qui ne contient pas le scan ayant produit la
lecture. Detaille dans `59`.

Usage :
    uv run python src/encre/campagnes_de_scan.py --lister --json docs/mesures/campagnes.json
    uv run python src/encre/campagnes_de_scan.py --depuis docs/mesures/campagnes.json
    uv run python src/encre/campagnes_de_scan.py --verifier
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "volume"))

import apparier_volumes as av  # noqa: E402  -- un seul lecteur de nom de volume

PRIX = tuple(r for r in av.ROULEAUX if r != "PHerc0139")
"""Les treize eligibles au Grand Prize. `PHerc0139` est le TEMOIN, jamais du classement."""

RACINE_ENCRE = Path("data/encre")
"""Ou vivent les cartes d'encre PUBLIEES que ce depot a recuperees (`fetch_cartes_encre.sh`)."""


def cartes_publiees(racine: Path) -> dict[str, int]:
    """Combien de cartes d'encre publiees ce depot tient, par rouleau.

    ⚠ C'est ce que NOUS avons recupere, pas ce que la communaute publie : `--help` n'est pas
    un rouleau, et un rouleau absent peut n'avoir jamais ete demande. La distinction est
    portee jusqu'au rapport, ou elle s'appelle `connu_lisible` et non `lisible`.
    """
    if not racine.is_dir():
        return {}
    out = {}
    for d in sorted(racine.iterdir()):
        if not d.is_dir() or d.name.startswith("-"):
            continue
        n = len([f for f in d.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")])
        if n:
            out[d.name] = n
    return out


def sonder_encre_publiee(rouleau: str, echantillon: int, lister=None) -> dict:
    """Le depot public publie-t-il une detection d'encre pour ce rouleau ?

    ⚠⚠ C'est la question que `cartes_publiees` ne repond PAS. Celle-la dit ce que NOUS avons
    telecharge, donc un rouleau absent peut n'avoir jamais ete demande -- et le partage qui
    en sortirait serait un fait sur nos telechargements deguise en fait sur le corpus.
    Celle-ci interroge le depot.

    ⚠ Elle sonde un ECHANTILLON de segments, pas tous : un rouleau en publie des dizaines et
    la reponse coute une requete chacun. Le compte sonde est rendu a cote du compte trouve,
    parce qu'un zero sur trois segments et un zero sur trente ne disent pas la meme chose.
    """
    lister = lister or av.lister
    segments = lister(f"{rouleau}/segments/")[:echantillon]
    avec = 0
    for seg in segments:
        sous = lister(f"{rouleau}/segments/{seg}/")
        if any(x == "ink-detection" for x in sous):
            avec += 1
    return {"segments_sondes": len(segments), "avec_encre_publiee": avec}


def decrire(rouleau: str, volumes: list[str]) -> dict:
    """Les trois grandeurs de chaque volume d'un rouleau, plus ce qu'elles disent ensemble.

    ⚠ Un volume dont le nom se tait sur une grandeur la rend `None` et est **compte**, jamais
    ecarte : un corpus ou les noms muets disparaissent se lit comme un corpus homogene.
    """
    lignes = []
    for v in volumes:
        lignes.append({
            "volume": v,
            "voxel_um": av.voxel_de(v),
            "distance_m": av.distance_de(v),
            "energie_kev": av.energie_de(v),
        })
    energies = [l["energie_kev"] for l in lignes if l["energie_kev"] is not None]
    voxels = [l["voxel_um"] for l in lignes if l["voxel_um"] is not None]
    distances = [l["distance_m"] for l in lignes if l["distance_m"] is not None]
    return {
        "rouleau": rouleau,
        "volumes": lignes,
        "n_volumes": len(lignes),
        "noms_muets_energie": sum(1 for l in lignes if l["energie_kev"] is None),
        "energie_min_kev": min(energies) if energies else None,
        "energie_max_kev": max(energies) if energies else None,
        "voxel_min_um": min(voxels) if voxels else None,
        "distance_min_m": min(distances) if distances else None,
        # ⭐ La grandeur qui a saute aux yeux sur six rouleaux : un scan FIN a COURTE
        # propagation. C'est un fait sur le volume, pas un jugement sur le rouleau.
        "a_un_scan_fin": any(l["voxel_um"] is not None and l["voxel_um"] <= 2.5
                             and l["distance_m"] is not None and l["distance_m"] <= 0.5
                             for l in lignes),
    }


def croiser(descriptions: list[dict], cartes: dict[str, int]) -> dict:
    """Repartit les rouleaux selon qu'on leur connait ou non des cartes d'encre publiees."""
    for d in descriptions:
        d["cartes_publiees"] = cartes.get(d["rouleau"], 0)
        d["connu_lisible"] = d["cartes_publiees"] > 0
        # ⚠ Le sondage, quand il a eu lieu, remplace le telechargement comme critere : il
        # parle du depot et non de nous. Sans sondage, on retombe sur ce qu'on tient, et le
        # rapport le dit par le champ `critere`.
        d["encre_publiee"] = (d.get("avec_encre_publiee", 0) > 0
                              if d.get("segments_sondes") else None)
        # ⚠⚠ TROIS etats, pas deux, et la distinction est celle qui decide. « Aucun segment
        # publie » veut dire que PERSONNE N'A TRACE ce rouleau -- ce n'est pas un verdict sur
        # son encre. Les melanger fait mesurer « sur quoi la communaute a travaille » en
        # croyant mesurer « ou l'encre se lit », et c'est ce que la premiere version de cette
        # mesure faisait.
        d["etat"] = ("aucun_segment" if not d.get("segments_sondes")
                     else "encre_publiee" if d["encre_publiee"] else "segments_sans_encre")

    def groupe(pred):
        g = [d for d in descriptions if pred(d)]
        e = [d["energie_min_kev"] for d in g if d["energie_min_kev"] is not None]
        return {
            "rouleaux": [d["rouleau"] for d in g],
            "n": len(g),
            "avec_scan_fin": sum(1 for d in g if d["a_un_scan_fin"]),
            "energie_min_kev": min(e) if e else None,
            "energie_max_kev": max(e) if e else None,
            "volumes_median": sorted(d["n_volumes"] for d in g)[len(g) // 2] if g else None,
            # ⚠ La PART, pas seulement le compte : « 6 avec un scan fin » ne se compare pas
            # a « 11 avec un scan fin » quand les groupes font 7 et 38.
            "part_scan_fin": round(sum(1 for d in g if d["a_un_scan_fin"]) / len(g), 3) if g else None,
        }

    sonde = any(d.get("segments_sondes") for d in descriptions)
    critere = (lambda d: d["encre_publiee"]) if sonde else (lambda d: d["connu_lisible"])
    a = groupe(lambda d: bool(critere(d)))
    b = groupe(lambda d: not bool(critere(d)))
    par_etat = {e: groupe(lambda d, e=e: d["etat"] == e)
                for e in ("aucun_segment", "segments_sans_encre", "encre_publiee")}
    enc, sans = par_etat["encre_publiee"], par_etat["segments_sans_encre"]
    return {
        "critere": "le dépôt publie une détection d'encre" if sonde
                   else "ce dépôt tient des cartes d'encre",
        "encre_publiee": a,
        "sans_encre_publiee": b,
        # ⚠⚠ Sans p, « 86 % contre 29 % » sur sept rouleaux et trente-huit se lit comme un
        # resultat alors que c'est peut-etre un tirage. Fisher exact et unilateral, parce
        # que l'hypothese a un sens : un scan fin devrait AIDER, pas nuire.
        "fisher": fisher_unilateral(a["avec_scan_fin"], a["n"] - a["avec_scan_fin"],
                                    b["avec_scan_fin"], b["n"] - b["avec_scan_fin"]),
        "par_etat": par_etat,
        # ⭐ Les treize du prix, a part : c'est la question que tout ce depot poursuit, et
        # elle a une reponse chiffree ici. ⚠ « aucun segment » et « trace sans encre » ne
        # disent pas la meme chose sur un rouleau du prix non plus.
        "rouleaux_du_prix": {
            "n": sum(1 for d in descriptions if d["rouleau"] in PRIX),
            "encre_publiee": [d["rouleau"] for d in descriptions
                              if d["rouleau"] in PRIX and d["etat"] == "encre_publiee"],
            "traces_sans_encre": [d["rouleau"] for d in descriptions
                                  if d["rouleau"] in PRIX and d["etat"] == "segments_sans_encre"],
            "jamais_traces": [d["rouleau"] for d in descriptions
                              if d["rouleau"] in PRIX and d["etat"] == "aucun_segment"],
        },
        # ⭐⭐ LA comparaison qui vaut : parmi les rouleaux QU'ON A TRACES, un scan fin
        # separe-t-il ceux dont l'encre est publiee des autres ? Le groupe « aucun segment »
        # est exclu parce qu'il ne dit rien sur l'encre -- il dit que personne n'a essaye.
        "fisher_traces": fisher_unilateral(
            enc["avec_scan_fin"], enc["n"] - enc["avec_scan_fin"],
            sans["avec_scan_fin"], sans["n"] - sans["avec_scan_fin"]),
    }


def fisher_unilateral(a: int, b: int, c: int, d: int) -> dict:
    """Fisher exact unilateral sur le tableau 2x2 (a b / c d), sans dependance externe.

    ⚠ Unilateral, et la direction est declaree AVANT de regarder : un scan fin devrait
    AIDER. Un test bilateral repondrait aussi « significatif » a l'effet inverse, ce qui
    voudrait dire qu'on n'avait pas d'hypothese.
    """
    from math import comb

    n = a + b + c + d
    lignes, colonnes = a + b, a + c
    total = comb(n, colonnes)
    if total == 0:
        return {"p": None, "raison": "tableau vide"}
    p = 0.0
    for k in range(a, min(lignes, colonnes) + 1):
        p += comb(lignes, k) * comb(n - lignes, colonnes - k) / total
    return {"table": [a, b, c, d], "p": p}


def verifier() -> int:
    """Auto-test HORS LIGNE : ni reseau, ni bucket."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    fin = "20260411134726-2.400um-0.2m-78keV-masked.zarr"
    reperage = "20250521151220-8.640um-1.2m-116keV-masked.zarr"
    muet = "20241024131839-7.910um-53keV-masked.zarr"

    d = decrire("R", [fin, reperage])
    v("les trois grandeurs de chaque volume sont lues",
      d["volumes"][0]["voxel_um"] == 2.4 and d["volumes"][1]["energie_kev"] == 116)
    v("l'energie minimale est celle du scan le plus doux", d["energie_min_kev"] == 78)
    v("un scan fin a courte propagation est reconnu", d["a_un_scan_fin"])
    v("... et un rouleau qui n'a que le reperage n'en a pas",
      not decrire("R", [reperage])["a_un_scan_fin"])
    # ⚠⚠ Le controle qui separe FIN de PROCHE : un scan fin a LONGUE propagation n'est pas
    # la meme chose, et les confondre ferait passer une campagne pour l'autre.
    v("... et un scan fin mais a longue propagation non plus",
      not decrire("R", ["20260101000000-2.400um-1.2m-78keV-masked.zarr"])["a_un_scan_fin"])

    # ⚠ Un nom muet est COMPTE, pas ecarte : un corpus dont les noms muets disparaissent se
    # lit comme un corpus homogene.
    m = decrire("R", [muet])
    v("un nom sans distance est compte, pas ecarte", m["n_volumes"] == 1)
    v("... et son absence de distance l'exclut du scan fin", not m["a_un_scan_fin"])
    v("... alors que son energie, elle, est bien lue", m["energie_min_kev"] == 53)
    mu = decrire("R", ["20230205180739-surface.zarr"])
    v("un nom muet sur l'energie est compte a part", mu["noms_muets_energie"] == 1)
    v("... et le rouleau n'en tire pas une energie inventee", mu["energie_min_kev"] is None)

    c = croiser([decrire("A", [fin, reperage]), decrire("B", [reperage])], {"A": 12})
    v("sans sondage, le critere est ce que CE depot tient",
      c["critere"] == "ce dépôt tient des cartes d'encre")
    v("un rouleau dont on tient des cartes est du bon cote",
      c["encre_publiee"]["rouleaux"] == ["A"])
    v("... et celui dont on n'en tient aucune de l'autre",
      c["sans_encre_publiee"]["rouleaux"] == ["B"])
    v("le comptage du scan fin suit le groupe",
      c["encre_publiee"]["avec_scan_fin"] == 1
      and c["sans_encre_publiee"]["avec_scan_fin"] == 0)
    v("... et la part est rendue, parce qu'un compte seul ne se compare pas",
      c["encre_publiee"]["part_scan_fin"] == 1.0
      and c["sans_encre_publiee"]["part_scan_fin"] == 0.0)
    # ⚠ Zero carte ne veut PAS dire illisible, seulement « on n'en tient aucune ». Le nom du
    # groupe le dit, et le controle verifie que le nom n'a pas glisse vers une affirmation.
    v("aucun groupe ne s'appelle « illisible »", "illisible" not in json.dumps(c))

    # ⚠⚠ Le controle qui donne son sens au sondage : des qu'il a eu lieu, c'est LUI qui
    # decide, et non ce que nous avons telecharge. Ici A est celui qu'on tient et B celui que
    # le depot publie -- les deux groupes doivent BASCULER.
    da = decrire("A", [fin, reperage]); da.update({"segments_sondes": 3, "avec_encre_publiee": 0})
    db = decrire("B", [reperage]);      db.update({"segments_sondes": 3, "avec_encre_publiee": 2})
    cs = croiser([da, db], {"A": 12})
    v("des qu'on a sonde, c'est le DEPOT qui decide, pas nos telechargements",
      cs["critere"] == "le dépôt publie une détection d'encre"
      and cs["encre_publiee"]["rouleaux"] == ["B"])
    v("... et un rouleau sonde a zero n'est pas classe lisible parce qu'on tient ses cartes",
      cs["sans_encre_publiee"]["rouleaux"] == ["A"])
    # ⚠ Un rouleau NON sonde ne doit pas etre declare sans encre : « on n'a pas regarde » et
    # « il n'y en a pas » sont deux faits, et les confondre gonfle le groupe negatif.
    v("un rouleau non sonde n'a pas de verdict de depot", da["encre_publiee"] is False
      and decrire("C", [reperage]).get("encre_publiee", "absent") == "absent")

    # --- le p, sans lequel « 86 % contre 29 % » n'est qu'un tirage possible ------------
    v("un tableau franchement separe rend un p petit",
      fisher_unilateral(10, 0, 0, 10)["p"] < 1e-4)
    v("... un tableau sans effet rend un p grand",
      fisher_unilateral(5, 5, 5, 5)["p"] > 0.4)
    # ⚠⚠ Le controle qui verifie que le test est bien UNILATERAL dans la bonne direction :
    # l'effet inverse ne doit PAS ressortir significatif.
    v("l'effet inverse n'est pas declare significatif",
      fisher_unilateral(0, 10, 10, 0)["p"] > 0.99)
    v("le tableau est rendu avec le p, pour qu'on puisse le refaire",
      fisher_unilateral(6, 1, 11, 27)["table"] == [6, 1, 11, 27])

    # --- LES TROIS ETATS, et le piege que la premiere version de ce fichier a paye -------
    def r(nom, vols, sondes=0, encre=0):
        x = decrire(nom, vols)
        if sondes:
            x.update({"segments_sondes": sondes, "avec_encre_publiee": encre})
        return x

    trois = croiser([r("A", [fin, reperage], 5, 1),      # trace, encre publiee, scan fin
                     r("B", [reperage], 5, 0),           # trace, pas d'encre, pas de scan fin
                     r("C", [fin, reperage])], {})       # JAMAIS TRACE, et il a un scan fin
    pe = trois["par_etat"]
    v("un rouleau jamais trace a son propre etat",
      pe["aucun_segment"]["rouleaux"] == ["C"])
    v("... distinct de « trace, sans encre »",
      pe["segments_sans_encre"]["rouleaux"] == ["B"])
    v("... et de « encre publiee »", pe["encre_publiee"]["rouleaux"] == ["A"])
    # ⚠⚠ Le controle qui EXISTE parce que la premiere version s'est trompee : le test qui
    # compte compare l'encre aux rouleaux TRACES SANS encre, jamais a tout le reste. Un
    # rouleau que personne n'a tente ne dit rien sur son encre, et l'inclure fait mesurer
    # « sur quoi la communaute a travaille » en croyant mesurer « ou l'encre se lit ».
    v("le test restreint exclut ceux que personne n'a tentes",
      trois["fisher_traces"]["table"] == [1, 0, 0, 1])
    v("... alors que le test large les inclut, et n'est donc pas le bon",
      trois["fisher"]["table"] == [1, 0, 1, 1])
    v("les deux tests ne rendent pas le meme p sur ce corpus",
      trois["fisher_traces"]["p"] != trois["fisher"]["p"])

    v("les treize du prix excluent le temoin", "PHerc0139" not in PRIX and len(PRIX) == 13)

    # --- le sondage lui-meme, avec un listeur de fixture ---------------------------------
    faux = {"R/segments/": ["s1", "s2", "s3"],
            "R/segments/s1/": ["mesh", "ink-detection"],
            "R/segments/s2/": ["mesh"],
            "R/segments/s3/": ["mesh", "surface-volumes"]}
    sonde = sonder_encre_publiee("R", 3, lambda p: faux.get(p, []))
    v("le sondage compte les segments qui publient une detection",
      sonde == {"segments_sondes": 3, "avec_encre_publiee": 1})
    v("... et l'echantillon borne le nombre de requetes",
      sonder_encre_publiee("R", 1, lambda p: faux.get(p, []))["segments_sondes"] == 1)
    # ⚠⚠ Le nom doit etre EXACT : un `startswith` classerait `ink-detection-old` comme une
    # publication, et un rouleau passerait du mauvais cote sur un dossier abandonne.
    v("le nom du dossier est compare exactement, pas par prefixe",
      sonder_encre_publiee("R", 1, lambda p: {"R/segments/": ["s1"],
                                              "R/segments/s1/": ["ink-detection-old"]}.get(p, [])
                           )["avec_encre_publiee"] == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Ce qui distingue un rouleau dont l'encre se lit d'un rouleau inerte.")
    p.add_argument("--lister", action="store_true",
                   help="interroger le depot public (le seul mode qui touche au reseau)")
    p.add_argument("--depuis", type=Path, help="re-deriver depuis un relevé deja ecrit")
    p.add_argument("--sonder-encre", type=int, default=0, metavar="N",
                   help="sonder N segments par rouleau pour savoir si le DÉPÔT publie une "
                        "détection d'encre — la question que le contenu de data/encre/ ne "
                        "répond pas")
    p.add_argument("--encre", type=Path, default=RACINE_ENCRE)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    args = p.parse_args()
    if args.verifier:
        return verifier()
    if not args.lister and args.depuis is None:
        p.error("donner --lister (réseau) ou --depuis <relevé>")

    if args.depuis is not None:
        d = json.loads(args.depuis.read_text())
        descriptions = d["rouleaux"]
    else:
        rouleaux = [r for r in av.lister("") if r.startswith("PHerc")]
        if not rouleaux:
            print("erreur : le dépôt public n'a rendu aucun rouleau — réseau ou format",
                  file=sys.stderr)
            return 2
        descriptions = []
        for r in rouleaux:
            volumes = av.lister(f"{r}/volumes/")
            d = decrire(r, volumes)
            if args.sonder_encre:
                d.update(sonder_encre_publiee(r, args.sonder_encre))
            descriptions.append(d)
            print(f"  {r:14} {len(volumes)} volume(s)"
                  + (f"  encre {d['avec_encre_publiee']}/{d['segments_sondes']} segments"
                     if args.sonder_encre else ""))

    cartes = cartes_publiees(args.encre)
    groupes = croiser(descriptions, cartes)
    rapport = {
        "question": "l'inertie du modèle suit-elle le ROULEAU ou sa CAMPAGNE de scan ?",
        "rouleaux": descriptions,
        "cartes_publiees_tenues": cartes,
        "groupes": groupes,
    }

    print(f"\ncritère : {groupes['critere']}")
    for e, g in (groupes.get("par_etat") or {}).items():
        if g["n"]:
            print(f"  {e:22} {g['n']:>2} rouleaux, {g['avec_scan_fin']} avec un scan fin "
                  f"({g['part_scan_fin']:.0%})")
    f = groupes.get("fisher") or {}
    if f.get("p") is not None:
        print(f"Fisher, encre contre TOUT le reste       {f['table']} : p = {f['p']:.4f}")
    ft = groupes.get("fisher_traces") or {}
    if ft.get("p") is not None:
        print(f"Fisher, encre contre les TRACÉS SANS encre {ft['table']} : p = {ft['p']:.4f}"
              "   ⭐ c'est celui-ci qui vaut")
    pr = groupes.get("rouleaux_du_prix") or {}
    if pr:
        print(f"\nles {pr['n']} rouleaux du prix : {len(pr['encre_publiee'])} avec encre publiée, "
              f"{len(pr['traces_sans_encre'])} tracés sans encre, "
              f"{len(pr['jamais_traces'])} jamais tracés")
    for nom, g in groupes.items():
        if nom in ("critere", "fisher", "fisher_traces", "par_etat", "rouleaux_du_prix"):
            continue
        print(f"\n{nom} : {g['n']} rouleaux, {g['avec_scan_fin']} avec un scan fin à courte "
              f"propagation ({g['part_scan_fin']:.0%}), énergie "
              f"{g['energie_min_kev']}–{g['energie_max_kev']} keV, "
              f"{g['volumes_median']} volume(s) en médiane")
        print("  " + ", ".join(g["rouleaux"][:12]) + (" …" if len(g["rouleaux"]) > 12 else ""))

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(rapport, indent=2, ensure_ascii=False) + "\n")
        print(f"\nrelevé : {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
