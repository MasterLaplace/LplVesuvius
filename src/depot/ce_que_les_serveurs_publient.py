#!/usr/bin/env python3
"""Ce que les serveurs publient, contre ce que l'index local en connaît.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL A COÛTÉ CINQ FOIS. Le dépôt travaille depuis un index
**en cache** — `data/metadata.min.json` — et rien ne l'a jamais comparé à ce que les serveurs
publient réellement. Le prix payé, à chaque fois de la même façon :

  - le référent déclaré **absent** faute d'avoir interrogé un serveur, alors que `dl.ash2txt.org`
    publiait ses 65 couches ;
  - la carte d'encre lue en réduction ×8 par habitude alors que le natif était à côté, ce qui a
    coûté **259 repères sur 314** ;
  - et **treize spires publiées** de `PHerc0500P2`, avec leur géométrie exacte sur trois volumes,
    qu'aucune mesure n'avait ouvertes — une vérité de terrain du déroulement.

⭐⭐⭐ **La règle qui en sort est mécanisable, donc elle doit l'être** : *ce qu'on croit absent
doit être cherché avant d'être reconstruit*. Ce fichier énumère les deux serveurs, énumère
l'index, et rend les trois ensembles — au serveur seulement, à l'index seulement, aux deux.

⚠⚠ ET LE REFUS COMPTE AUTANT QUE LE RAPPORT. Un serveur injoignable rend une liste vide, et une
liste vide comparée à un index plein dirait « l'index a tout inventé ». Un listage vide est donc
**refusé** et non interprété : c'est la panne qui ressemble le plus à un résultat.

Usage :
    uv run python src/depot/ce_que_les_serveurs_publient.py --verifier
    uv run python src/depot/ce_que_les_serveurs_publient.py --fragment PHerc0500P2
    uv run python src/depot/ce_que_les_serveurs_publient.py \\
        --json docs/mesures/ce_que_les_serveurs_publient.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "encre"))

S3 = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
HTTP = "https://dl.ash2txt.org"
INDEX = RACINE / "data" / "metadata.min.json"

HREF = re.compile(r'href="([^"]+)"')


def prefixes_s3(xml: bytes) -> tuple[list[str], str | None]:
    """Les sous-dossiers d'un listage S3, et le jeton de la page suivante s'il y en a une.

    ⚠⚠ LE JETON N'EST PAS UNE COMMODITÉ. S3 rend **mille** clés par page ; ignorer la
    continuation donne une liste tronquée qui a l'air complète, donc un « ce serveur ne publie
    que ça » qui est faux sans que rien ne le dise. C'est la forme S3 du log périmé lu comme un
    résultat.

    ⚠ L'espace de noms est retiré du tag plutôt que déclaré : S3 en a changé par le passé, et un
    parseur qui épingle l'URI casse le jour où elle bouge.
    """
    racine = ET.fromstring(xml)

    def tag(e):
        return e.tag.split("}")[-1]

    noms = [c.text for e in racine if tag(e) == "CommonPrefixes"
            for c in e if tag(c) == "Prefix" and c.text]
    tronque = any(tag(e) == "IsTruncated" and (e.text or "").lower() == "true" for e in racine)
    jeton = next((e.text for e in racine if tag(e) == "NextContinuationToken"), None)
    return noms, (jeton if tronque else None)


def lister_s3(prefixe: str, timeout: float = 120.0, pages: int = 20) -> list[str]:
    """Les sous-dossiers immédiats d'un préfixe S3, toutes pages comprises."""
    from zarr_depth import get  # noqa: PLC0415

    out, jeton = [], None
    for _ in range(pages):
        url = f"{S3}/?list-type=2&prefix={prefixe}&delimiter=/"
        if jeton:
            url += f"&continuation-token={jeton}"
        brut = get(url, timeout)
        if brut is None:
            break
        noms, jeton = prefixes_s3(brut)
        out.extend(noms)
        if not jeton:
            break
    return sorted(set(out))


def liens_html(page: str) -> list[str]:
    """Les entrées d'un index de répertoire nginx, sans le lien de remontée.

    ⚠ Le lien `../` est écarté : le garder ferait remonter un dossier parent dans la liste des
    enfants, donc un dossier qui « existe » partout.
    """
    return sorted({h for h in HREF.findall(page) if h not in ("../", "/") and not h.startswith("?")})


def lister_html(chemin: str, timeout: float = 120.0) -> list[str]:
    """Les entrées publiées sous un chemin de `dl.ash2txt.org`."""
    from zarr_depth import get  # noqa: PLC0415

    brut = get(f"{HTTP}/{chemin.strip('/')}/", timeout)
    return liens_html(brut.decode(errors="replace")) if brut else []


def index_local(fragment: str) -> list[str]:
    """Les segments que l'index EN CACHE connaît **pour ce fragment**.

    ⚠⚠ LE FILTRE PAR OBJET N'EST PAS UN DÉTAIL, et l'oublier m'a fait publier « 272 segments à
    l'index seulement » — c'étaient ceux des quarante-quatre autres rouleaux. Un inventaire qui
    compare le catalogue entier au listage d'un fragment rapporte un écart énorme et faux, donc
    il crie assez fort pour qu'on cesse de l'écouter.
    """
    import la_case_vide as cv  # noqa: PLC0415

    fiche = cv._charger().get(fragment, {})
    return sorted({seg.get("long_id", sid)
                   for sid, seg in fiche.get("segments", {}).items()})


def comparer(serveur: list[str], index: list[str]) -> dict:
    """Les trois ensembles, et le refus quand le serveur n'a rien rendu.

    ⚠⚠⚠ UN LISTAGE VIDE EST UNE PANNE, PAS UN RÉSULTAT. Comparer une liste vide à un index plein
    rendrait « l'index connaît 39 choses que le serveur ne publie pas », c'est-à-dire un rapport
    alarmant produit par une coupure réseau. Le refus est explicite.

    ⚠⚠ Les deux sens sont rendus. Un outil qui ne regarderait que « ce que le serveur a en plus »
    ne verrait pas un index qui a **dérivé** — et c'est le même angle mort, pris par l'autre bout.
    """
    if not serveur:
        return dict(refuse="le serveur n'a rien rendu : coupure ou préfixe faux, pas un verdict")
    s, i = set(serveur), set(index)
    return dict(sur_le_serveur=len(s), dans_l_index=len(i),
                aux_deux=sorted(s & i),
                serveur_seulement=sorted(s - i),
                index_seulement=sorted(i - s))


def mesurer(fragment: str = "PHerc0500P2") -> dict:
    """L'inventaire des deux serveurs pour un fragment, contre l'index local."""
    seg_s3 = [p.rstrip("/").split("/")[-1]
              for p in lister_s3(f"{fragment}/segments/")]
    haut_s3 = [p.rstrip("/").split("/")[-1] for p in lister_s3(f"{fragment}/")]
    idx = index_local(fragment)
    dl_racine = lister_html(f"fragments/{fragment}")
    dl_chemins = lister_html(f"fragments/{fragment}/paths")
    return dict(
        fragment=fragment,
        index=dict(fichier=str(INDEX.relative_to(RACINE)),
                   octets=INDEX.stat().st_size if INDEX.is_file() else 0,
                   segments=len(idx)),
        s3=dict(racine=haut_s3, segments=len(seg_s3),
                exemples=seg_s3[:5]),
        dl_ash2txt=dict(racine=dl_racine, chemins=dl_chemins),
        segments=comparer(seg_s3, idx),
        # ⚠⚠ CE QUE dl.ash2txt.org PUBLIE ET QUE S3 N'A PAS, et l'inverse : les deux serveurs ne
        # portent pas la même chose, et croire qu'ils se recopient est exactement l'erreur qui a
        # fait déclarer le référent absent.
        racines=dict(sur_s3_seulement=sorted(set(haut_s3) - {d.rstrip("/") for d in dl_racine}),
                     sur_dl_seulement=sorted({d.rstrip("/") for d in dl_racine} - set(haut_s3))))


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    page1 = b"""<?xml version="1.0"?>
    <ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
      <IsTruncated>true</IsTruncated>
      <NextContinuationToken>JETON</NextContinuationToken>
      <CommonPrefixes><Prefix>F/segments/a/</Prefix></CommonPrefixes>
      <CommonPrefixes><Prefix>F/segments/b/</Prefix></CommonPrefixes>
    </ListBucketResult>"""
    noms, jeton = prefixes_s3(page1)
    v("le listage S3 rend ses préfixes", noms == ["F/segments/a/", "F/segments/b/"], str(noms))
    # ⚠⚠⚠ LE CONTRÔLE QUI COMPTE : une page tronquée doit rendre son jeton. Sans lui la liste
    # s'arrête à mille clés en ayant l'air complète, et « ce serveur ne publie que ça » est faux
    # sans que rien ne le dise.
    v("... et le jeton d'une page tronquée", jeton == "JETON", str(jeton))
    page2 = page1.replace(b"<IsTruncated>true</IsTruncated>",
                          b"<IsTruncated>false</IsTruncated>")
    v("... et aucun jeton quand la liste est complète", prefixes_s3(page2)[1] is None)
    sans_ns = page1.replace(b' xmlns="http://s3.amazonaws.com/doc/2006-03-01/"', b"")
    v("... et l'espace de noms n'est pas épinglé",
      prefixes_s3(sans_ns)[0] == noms)

    html = ('<a href="../">..</a><a href="cases/">cases/</a>'
            '<a href="volumes/">volumes/</a><a href="?C=N">tri</a>')
    v("le listage HTML rend les entrées", liens_html(html) == ["cases/", "volumes/"],
      str(liens_html(html)))
    v("... et écarte la remontée et les liens de tri", "../" not in liens_html(html))

    # --- la comparaison, dans les DEUX sens et avec son refus ---
    c = comparer(["a", "b", "c"], ["b", "c", "d"])
    v("ce que le serveur a en plus est rendu", c["serveur_seulement"] == ["a"], str(c))
    # ⚠⚠ Sans ce second sens, un index qui a DÉRIVÉ resterait invisible : c'est le même angle
    # mort pris par l'autre bout.
    v("... et ce que l'index a en trop aussi", c["index_seulement"] == ["d"])
    v("... et ce qu'ils partagent", c["aux_deux"] == ["b", "c"])
    # ⚠⚠⚠ LE CONTRÔLE QUI ATTRAPE LE DÉFAUT QUE J'AI COMMIS : l'index doit être filtré par
    # OBJET. Sans lui, la comparaison porte sur les quarante-cinq rouleaux du catalogue contre le
    # listage d'un seul, et rend un écart de plusieurs centaines qui ne mesure que l'oubli.
    import la_case_vide as cv  # noqa: PLC0415

    objets = list(cv._charger())
    if len(objets) >= 2:
        a_, b_ = index_local(objets[0]), index_local(objets[1])
        v("l'index est filtré par objet, pas rendu en entier",
          set(a_).isdisjoint(b_) and (a_ or b_),
          f"{len(a_)} et {len(b_)} segments, sans recouvrement")
        v("... et un objet inconnu ne rend rien plutôt que tout",
          index_local("objet-qui-n-existe-pas") == [])

    v("deux listes identiques ne signalent rien",
      comparer(["a"], ["a"])["serveur_seulement"] == []
      and comparer(["a"], ["a"])["index_seulement"] == [])
    # ⚠⚠⚠ LE REFUS : une coupure réseau rend une liste vide, et la comparer produirait un rapport
    # alarmant qui ne mesure que la panne.
    r = comparer([], ["a", "b"])
    v("un serveur muet est REFUSÉ, pas interprété",
      "refuse" in r and "index_seulement" not in r, str(r))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fragment", default="PHerc0500P2")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.fragment)
    print(f"{r['fragment']}\n")
    print(f"index en cache : {r['index']['fichier']} — {r['index']['segments']} segments")
    print(f"S3             : {r['s3']['segments']} segments, racines "
          f"{', '.join(x for x in r['s3']['racine'])}")
    print(f"dl.ash2txt.org : racines {', '.join(x.rstrip('/') for x in r['dl_ash2txt']['racine'])}")
    print(f"                 chemins {', '.join(x.rstrip('/') for x in r['dl_ash2txt']['chemins'])}")
    c = r["segments"]
    if "refuse" in c:
        print(f"\n⚠ {c['refuse']}")
    else:
        print(f"\nsegments : {c['sur_le_serveur']} sur S3, {c['dans_l_index']} dans l'index")
        print(f"  au serveur seulement ({len(c['serveur_seulement'])}) : "
              f"{', '.join(c['serveur_seulement'][:6]) or '—'}")
        print(f"  à l'index seulement  ({len(c['index_seulement'])}) : "
              f"{', '.join(c['index_seulement'][:6]) or '—'}")
    print(f"\nracines sur S3 seulement : {', '.join(r['racines']['sur_s3_seulement']) or '—'}")
    print(f"racines sur dl seulement : {', '.join(r['racines']['sur_dl_seulement']) or '—'}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
