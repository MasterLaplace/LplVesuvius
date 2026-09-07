#!/usr/bin/env python3
"""Où vit un champ de fibres — et l'objet que la campagne déroule en a-t-il un ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL VIENT D'UN AVERTISSEMENT. Six tranches ont fermé les portes
de la lecture — la forme cherchée, le lieu où on l'apprend, son amplitude, la largeur du lissage,
un champ lisse par construction, et la direction. Il ne restait qu'une piste : faire lire au
raccrochage autre chose qu'une **intensité**, c'est-à-dire l'**orientation** des fibres. Et
`le_champ_de_fibres` établit qu'un tel champ est publié — pour `PHerc0139`.

⚠⚠ LE PIÈGE EST NOMMÉ DANS CE DÉPÔT, ET IL A DÉJÀ MORDU TROIS FOIS : *interroger UNE vue du
corpus et conclure sur LE corpus*. `ou_vit_ce_rouleau` existe pour cette raison exacte, du côté
des résolutions. Ce fichier fait la même chose du côté des **représentations** : il demande à
**chaque source** ce qu'elle publie, et il **juxtapose** au lieu de trancher.

⭐⭐ ET LA QUESTION UTILE N'EST PAS « QUI A DES FIBRES » MAIS « QUI A LES DEUX ». Un champ
d'orientation ne sert à cette campagne que sur un objet qui publie aussi des **spires** : c'est
sur elles que la marche s'appuie et c'est entre elles que l'erreur se mesure. L'intersection est
donc le seul nombre qui décide, et elle est publiée comme telle.

⚠ Un « absent » reste un **absent des sources interrogées** — le listage d'un serveur n'est pas
une preuve d'inexistence, et le fichier l'écrit ainsi plutôt que de conclure au-delà.

Usage :
    uv run python src/nappe/ou_vit_le_champ_de_fibres.py --verifier
    uv run python src/nappe/ou_vit_le_champ_de_fibres.py \\
        --json docs/mesures/ou_vit_le_champ_de_fibres.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre"):
    sys.path.insert(0, str(RACINE / "src" / _d))

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
SERVEUR = "https://dl.ash2txt.org"
# ⚠⚠ Les deux endroits où le serveur range ses objets. Ce ne sont pas deux copies : ce sont deux
# ARBORESCENCES, et un objet absent de l'une peut être présent dans l'autre.
LAYOUTS = ("fragments", "full-scrolls")
PREFIXE = re.compile(r"<Prefix>([^<]*)</Prefix>")
LIEN = re.compile(r'href="([^"]+)"')
# ⚠ Le nom du répertoire qui porte l'orientation des fibres, tel que le bucket l'écrit.
FIBRES = "fibers"


def _lire(url: str, delai: float = 60.0) -> str | None:
    """Le corps d'une page, ou None si la source ne répond pas.

    ⚠⚠ UNE SOURCE MUETTE N'EST PAS UNE SOURCE VIDE, et les confondre est exactement la faute
    que ce fichier existe pour éviter : un réseau coupé rendrait « aucun objet ne publie de
    fibres », ce qui a la même tête qu'un corpus qui n'en publie pas.
    """
    import urllib.error  # noqa: PLC0415
    import urllib.request  # noqa: PLC0415

    try:
        with urllib.request.urlopen(url, timeout=delai) as r:  # noqa: S310
            return r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError):
        return None


def _dossiers(corps: str) -> list[str]:
    """Les sous-dossiers d'une page de listage HTML, sans les liens de remontée."""
    return sorted({h.rstrip("/") for h in LIEN.findall(corps)
                   if h.endswith("/") and not h.startswith("/") and not h.startswith("?")})


def objets_du_bucket(lire=_lire) -> list[str] | None:
    """Les objets publiés à la racine du bucket, ou None si la source est muette."""
    corps = lire(f"{BUCKET}/?list-type=2&delimiter=/&prefix=")
    if corps is None:
        return None
    return sorted({p.rstrip("/") for p in PREFIXE.findall(corps)
                   if p.rstrip("/") and "/" not in p.rstrip("/")})


def predictions_du_bucket(objet: str, lire=_lire) -> list[str] | None:
    """Les genres de prédiction publiés pour cet objet sur le bucket."""
    base = f"{objet}/representations/predictions/"
    corps = lire(f"{BUCKET}/?list-type=2&delimiter=/&prefix={base}")
    if corps is None:
        return None
    return sorted({p[len(base):].rstrip("/") for p in PREFIXE.findall(corps)
                   if p.startswith(base) and p[len(base):].rstrip("/")})


def adresses_du_serveur(lire=_lire) -> dict[str, str]:
    """Où chaque objet vit sur le serveur, en parcourant ses DEUX arborescences.

    ⚠⚠⚠ SANS CE PARCOURS, LE RELEVÉ INVENTE DES ABSENCES. La première version de ce fichier
    demandait à tous les objets l'adresse `fragments/<objet>/…`, y compris aux rouleaux, qui
    vivent sous `full-scrolls/<Scroll>/<objet>.volpkg/`. Elle rapportait donc **trente-huit
    désaccords sur trente-huit** — un artefact de construction d'URL, présenté comme un fait
    sur le corpus. C'est précisément le mode de panne que ce fichier existe pour éviter, commis
    à l'intérieur de lui-même.
    """
    out: dict[str, str] = {}
    corps = lire(f"{SERVEUR}/fragments/")
    for nom in (_dossiers(corps) if corps else []):
        out[nom] = f"{SERVEUR}/fragments/{nom}"
    racine = lire(f"{SERVEUR}/full-scrolls/")
    for rouleau in (_dossiers(racine) if racine else []):
        page = lire(f"{SERVEUR}/full-scrolls/{rouleau}/")
        for volpkg in (_dossiers(page) if page else []):
            nom = volpkg[:-len(".volpkg")] if volpkg.endswith(".volpkg") else volpkg
            out.setdefault(nom, f"{SERVEUR}/full-scrolls/{rouleau}/{volpkg}")
    return out


def vocabulaire_du_serveur(objet: str, adresses: dict[str, str],
                           lire=_lire) -> dict | None:
    """Ce que le serveur publie pour cet objet — ses dossiers de premier niveau.

    ⚠⚠⚠ ET IL NE PARLE PAS LE MÊME VOCABULAIRE QUE LE BUCKET. Le bucket range sous
    `representations/predictions/<genre>` ; le serveur range sous `renders/`, `umbilici/`,
    `volumetric-instance-labels/`… Demander au serveur s'il a des `fibers/` est donc une
    **erreur de catégorie**, et répondre « non » ferait passer une différence d'arborescence
    pour une absence de donnée. Ce fichier rend donc ce que le serveur a, sans le traduire.

    ⚠ None veut dire « cet objet n'a pas d'adresse connue ici », ce qui n'est pas « il n'y a
    rien » : c'est une source qui ne dit rien sur lui.
    """
    base = adresses.get(objet)
    if base is None:
        return None
    corps = lire(f"{base}/")
    if corps is None:
        return None
    dossiers = _dossiers(corps)
    # ⚠⚠⚠ ET LA QUESTION POSÉE AU MÊME NIVEAU D'ARBRE. Comparer les GENRES du bucket — deux
    # niveaux sous `representations/predictions/` — aux dossiers de PREMIER niveau du serveur
    # est une comparaison entre deux étages : elle ne peut que rendre « aucun mot commun », ce
    # qui est vrai et ne dit rien. Ce qui se demande vraiment est si le serveur a, LUI AUSSI,
    # un étage `predictions/` — et la réponse est mesurée, pas supposée.
    genres = None
    if "representations" in dossiers:
        page = lire(f"{base}/representations/predictions/")
        genres = _dossiers(page) if page is not None else []
    return dict(adresse=base, dossiers=dossiers, genres=genres)


def objets_avec_spires(objets: list[str]) -> list[str]:
    """Les objets qui publient des spires, lus dans l'index local — sans réseau.

    ⚠⚠ C'EST L'AUTRE MOITIÉ DE LA QUESTION, et elle ne vient pas d'un serveur : les spires sont
    ce sur quoi la marche s'appuie, et un champ d'orientation sans spires ne sert à rien à cette
    campagne. Les demander à l'index plutôt qu'au réseau est aussi ce qui rend cette moitié
    vérifiable hors ligne.
    """
    from les_wraps_publies import wraps_du_fragment  # noqa: PLC0415

    return sorted(o for o in objets if wraps_du_fragment(o))


def mesurer(lire=_lire, objets: list[str] | None = None, avec_spires=None) -> dict:
    """Ce que chaque source publie pour chaque objet, et l'intersection qui décide."""
    connus = objets_du_bucket(lire) if objets is None else list(objets)
    if not connus:
        raise RuntimeError("aucune source n'a répondu : rien ne peut être conclu du corpus")
    adresses = adresses_du_serveur(lire)
    lignes = []
    for objet in connus:
        b = predictions_du_bucket(objet, lire)
        s = vocabulaire_du_serveur(objet, adresses, lire)
        lignes.append(dict(
            objet=objet, genres_du_bucket=b, bucket_muet=bool(b is None),
            adresse_serveur=(s or {}).get("adresse"),
            dossiers_du_serveur=(s or {}).get("dossiers"),
            genres_du_serveur=(s or {}).get("genres"),
            connu_du_serveur=bool(s is not None),
            a_des_fibres=bool(b and FIBRES in b)))
    spires = (objets_avec_spires(connus) if avec_spires is None else list(avec_spires))
    fibres = [e["objet"] for e in lignes if e["a_des_fibres"]]
    r = dict(
        bucket=BUCKET, serveur=SERVEUR, layouts=list(LAYOUTS),
        objets=len(lignes), lignes=lignes,
        objets_avec_fibres=fibres, objets_avec_spires=spires,
        # ⭐⭐⭐ LE SEUL NOMBRE QUI DÉCIDE : un champ d'orientation ne sert à cette campagne que
        # sur un objet qui publie AUSSI des spires.
        objets_avec_les_deux=sorted(set(fibres) & set(spires)),
        genres_du_bucket=sorted({g for e in lignes for g in (e["genres_du_bucket"] or [])}),
        dossiers_du_serveur=sorted({d for e in lignes
                                    for d in (e["dossiers_du_serveur"] or [])}),
        objets_absents_du_serveur=[e["objet"] for e in lignes if not e["connu_du_serveur"]],
        sources_muettes=[e["objet"] for e in lignes if e["bucket_muet"]])
    r["la_voie_de_lorientation_est_ouverte"] = bool(r["objets_avec_les_deux"])
    # ⚠⚠ LA COMPARAISON EST FAITE AU MÊME NIVEAU D'ARBRE, ou pas du tout. Les objets que le
    # serveur connaît ET qui y ont un dossier `representations/` sont les seuls sur lesquels la
    # question « publie-t-il des genres ? » ait un sens.
    comparables = [e for e in lignes if e["genres_du_serveur"] is not None]
    r["objets_comparables"] = [e["objet"] for e in comparables]
    r["genres_du_serveur"] = sorted({g for e in comparables
                                     for g in (e["genres_du_serveur"] or [])})
    r["vocabulaires_communs"] = sorted(set(r["genres_du_bucket"]) & set(r["genres_du_serveur"]))
    # ⭐⭐ ET LE FAIT PRÉCIS PLUTÔT QUE LE FAIT TRIVIAL : le serveur a-t-il seulement un étage
    # `predictions/` ? S'il n'en a aucun, l'absence de `fibers/` chez lui n'est pas un fait sur
    # le corpus mais sur son rangement.
    r["le_serveur_a_un_etage_predictions"] = bool(
        comparables and any(e["genres_du_serveur"] for e in comparables))
    r["les_sources_parlent_le_meme_vocabulaire"] = bool(r["vocabulaires_communs"])
    # ⚠⚠ ET LA RÉSERVE, ÉCRITE DANS LA MESURE PLUTÔT QU'À CÔTÉ : un absent est un absent des
    # sources interrogées. Le listage d'un serveur n'est pas une preuve d'inexistence.
    r["portee"] = ("absent veut dire absent des sources interrogées, jamais inexistant ; "
                   "et les deux sources rangent différemment, donc un genre vu sur l'une "
                   "n'est pas attendu sur l'autre")
    return r


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- des sources fabriquées, donc aucun réseau ---
    pages = {
        f"{BUCKET}/?list-type=2&delimiter=/&prefix=":
            "<Prefix>Aaa/</Prefix><Prefix>Bbb/</Prefix><Prefix>Aaa/volumes/</Prefix>",
        f"{BUCKET}/?list-type=2&delimiter=/&prefix=Aaa/representations/predictions/":
            "<Prefix>Aaa/representations/predictions/fibers/</Prefix>"
            "<Prefix>Aaa/representations/predictions/surfaces/</Prefix>",
        f"{BUCKET}/?list-type=2&delimiter=/&prefix=Bbb/representations/predictions/":
            "<Prefix>Bbb/representations/predictions/surfaces/</Prefix>",
        # ⚠ Bbb est un fragment, Aaa un rouleau : les deux arborescences du serveur.
        f"{SERVEUR}/fragments/": '<a href="/parent/">^</a><a href="Bbb/">b</a>',
        f"{SERVEUR}/full-scrolls/": '<a href="Rouleau1/">r</a>',
        f"{SERVEUR}/full-scrolls/Rouleau1/": '<a href="Aaa.volpkg/">a</a>',
        f"{SERVEUR}/full-scrolls/Rouleau1/Aaa.volpkg/":
            '<a href="renders/">r</a><a href="umbilici/">u</a><a href="config.json">c</a>',
        f"{SERVEUR}/fragments/Bbb/":
            '<a href="volumes/">v</a><a href="representations/">r</a>',
        # ⚠ Le serveur a bien un `representations/`, mais pas d'étage `predictions/` dessous :
        # c'est le fait que la mesure doit distinguer d'une absence de données.
        f"{SERVEUR}/fragments/Bbb/representations/predictions/": None,
    }

    def faux(url: str, delai: float = 0.0):
        return pages.get(url)

    v("la racine du bucket ne rend que les objets, pas leurs sous-dossiers",
      objets_du_bucket(faux) == ["Aaa", "Bbb"], str(objets_du_bucket(faux)))
    v("les genres de prédiction sont rendus sans leur préfixe",
      predictions_du_bucket("Aaa", faux) == ["fibers", "surfaces"],
      str(predictions_du_bucket("Aaa", faux)))
    v("un listage HTML ne retient que les dossiers, pas les fichiers ni la remontée",
      _dossiers('<a href="/haut/">^</a><a href="x/">x</a><a href="f.json">f</a>') == ["x"])
    # ⚠⚠⚠ LES DEUX ARBORESCENCES DU SERVEUR SONT PARCOURUES. La première version demandait
    # `fragments/<objet>` à tout le monde, y compris aux rouleaux, et rapportait trente-huit
    # absences qui étaient des erreurs d'adresse.
    adr = adresses_du_serveur(faux)
    v("les deux arborescences du serveur sont parcourues, fragments ET rouleaux",
      adr == {"Bbb": f"{SERVEUR}/fragments/Bbb",
              "Aaa": f"{SERVEUR}/full-scrolls/Rouleau1/Aaa.volpkg"}, str(adr))
    v("... et le suffixe .volpkg ne fait pas partie du nom de l'objet", "Aaa" in adr)
    # ⚠⚠⚠ LE VOCABULAIRE DU SERVEUR N'EST PAS CELUI DU BUCKET, et le rendre tel quel est ce qui
    # empêche de lire une différence d'arborescence comme une absence de donnée.
    voc = vocabulaire_du_serveur("Aaa", adr, faux)
    v("le serveur rend SES dossiers, sans les traduire dans le vocabulaire du bucket",
      voc["dossiers"] == ["renders", "umbilici"], str(voc))
    v("... et un objet sans adresse connue rend None, pas une liste vide",
      vocabulaire_du_serveur("Ccc", adr, faux) is None)
    v("une source muette rend None, jamais une liste vide",
      objets_du_bucket(lambda *a, **k: None) is None)
    muet = None
    try:
        mesurer(lambda *a, **k: None)
    except RuntimeError as exc:
        muet = str(exc)
    v("un corpus dont aucune source ne répond est REFUSÉ, pas rendu vide",
      muet is not None, str(muet))

    fab = mesurer(faux, avec_spires=["Bbb"])
    v("la mesure tourne de bout en bout sans réseau", fab["objets"] == 2)
    v("... les deux sources sont juxtaposées, pas fondues",
      fab["lignes"][0]["genres_du_bucket"] == ["fibers", "surfaces"]
      and fab["lignes"][0]["dossiers_du_serveur"] == ["renders", "umbilici"],
      str(fab["lignes"][0]))
    # ⚠⚠⚠ ET LE FAIT QUE LE RELEVÉ EXISTE POUR DIRE : les deux sources ne rangent pas pareil,
    # donc un genre vu sur l'une n'est pas attendu sur l'autre.
    # ⚠⚠⚠ LA COMPARAISON SE FAIT AU MÊME NIVEAU D'ARBRE, ou pas du tout. Comparer les genres
    # du bucket aux dossiers de premier niveau du serveur ne peut que rendre « aucun mot
    # commun » : c'est vrai et ça ne dit rien. Ce qui se demande est si le serveur a lui aussi
    # un étage `predictions/`.
    v("... la comparaison de vocabulaire se fait au MÊME niveau d'arbre",
      fab["objets_comparables"] == ["Bbb"]
      and not fab["le_serveur_a_un_etage_predictions"]
      and fab["vocabulaires_communs"] == [],
      f"comparables {fab['objets_comparables']} · genres serveur "
      f"{fab['genres_du_serveur']}")
    # ⭐⭐⭐ LE VERDICT QUI DÉCIDE : l'INTERSECTION, pas la présence de fibres quelque part.
    v("le verdict porte sur l'INTERSECTION fibres ∩ spires, jamais sur les fibres seules",
      fab["objets_avec_fibres"] == ["Aaa"] and fab["objets_avec_spires"] == ["Bbb"]
      and fab["objets_avec_les_deux"] == []
      and not fab["la_voie_de_lorientation_est_ouverte"],
      f"fibres {fab['objets_avec_fibres']} · spires {fab['objets_avec_spires']}")
    ouvert = mesurer(faux, avec_spires=["Aaa"])
    v("... et il s'ouvre dès qu'un objet porte les deux",
      ouvert["objets_avec_les_deux"] == ["Aaa"]
      and ouvert["la_voie_de_lorientation_est_ouverte"])
    v("la portée de l'absence est écrite DANS la mesure",
      "sources interrogées" in fab["portee"] and "rangent différemment" in fab["portee"])
    v("le résultat est sérialisable tel quel, sans type qui traîne",
      isinstance(json.dumps(fab), str))
    tampon, souci = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(tampon):
            afficher(fab)
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("l'affichage tourne sur ce résultat et va jusqu'à son verdict",
      souci is None and "INTERSECTION" in tampon.getvalue(),
      souci or f"{len(tampon.getvalue().splitlines())} lignes")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def afficher(r: dict) -> None:
    """Le compte rendu lisible d'un relevé de sources."""
    print(f"{r['objets']} objets · bucket : {', '.join(r['genres_du_bucket'])}")
    vus = r["dossiers_du_serveur"]
    suite = " ..." if len(vus) > 8 else ""
    print(f"serveur ({', '.join(r['layouts'])}) : {', '.join(vus[:8])}{suite}")
    print()
    print(f"{'objet':>14} {'genres du bucket':>34} {'sur le serveur':>15} {'spires':>7}")
    print("-" * 76)
    for e in r["lignes"]:
        if not e["genres_du_bucket"] and e["objet"] not in r["objets_avec_spires"]:
            continue
        b = "muet" if e["genres_du_bucket"] is None else (
            ", ".join(e["genres_du_bucket"]) or "—")
        marque = " ⭐" if e["objet"] in r["objets_avec_les_deux"] else ""
        srv = "oui" if e["connu_du_serveur"] else "—"
        spi = "oui" if e["objet"] in r["objets_avec_spires"] else "—"
        print(f"{e['objet']:>14} {b:>34} {srv:>15} {spi:>7}{marque}")
    print()
    print(f"objets avec un champ de FIBRES : {r['objets_avec_fibres']}")
    print(f"objets avec des SPIRES        : {r['objets_avec_spires']}")
    print(f"→ ⭐⭐⭐ INTERSECTION — les deux à la fois : "
          f"{r['objets_avec_les_deux'] or 'AUCUN'}")
    print(f"→ la voie de l'orientation est ouverte : "
          f"{'OUI' if r['la_voie_de_lorientation_est_ouverte'] else 'NON'}")
    print(f"⚠ objets où la question se pose au MÊME niveau d'arbre : "
          f"{r['objets_comparables'] or 'aucun'}")
    print(f"⚠ le serveur a-t-il un étage predictions/ ? "
          f"{'OUI ' + str(r['genres_du_serveur']) if r['le_serveur_a_un_etage_predictions'] else 'NON'}"
          " — sinon l'absence de fibres chez lui parle de son rangement, pas du corpus")
    if r["objets_absents_du_serveur"]:
        print(f"⚠ objets sans adresse connue sur le serveur : "
              f"{len(r['objets_absents_du_serveur'])} sur {r['objets']}")
    if r["sources_muettes"]:
        print(f"⚠ bucket muet sur : {r['sources_muettes']}")
    print(f"⚠ {r['portee']}")

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
