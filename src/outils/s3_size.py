#!/usr/bin/env python3
"""Mesure la taille d'un prefixe du bucket public Vesuvius, sans rien telecharger.

Le bucket est ouvert en lecture anonyme, donc l'API REST suffit et aucune
dependance (boto3, awscli) n'est requise -- ce qui compte ici : on veut pouvoir
decider quoi telecharger AVANT d'avoir installe quoi que ce soit.

Sortie humaine par defaut, `--json` pour une sortie machine pure (aucune ligne
de commentaire, aucun bandeau) destinee a etre redirigee.

Usage:
    ./s3_size.py PHerc0332/segments/
    ./s3_size.py PHerc0332/ --depth 2
    ./s3_size.py PHerc0332/volumes/ --json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ElementTree

BUCKET = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com"
NAMESPACE = "{http://s3.amazonaws.com/doc/2006-03-01/}"


def iter_objects(prefix: str):
    """Enumere (cle, taille) sous un prefixe, en suivant la pagination S3.

    S3 rend au plus 1000 cles par reponse et signale la suite par un jeton de
    continuation ; ignorer ce jeton donne un total silencieusement tronque, ce
    qui ressemble exactement a un prefixe plus petit qu'il n'est.
    """
    token = None
    while True:
        params = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            params["continuation-token"] = token
        url = f"{BUCKET}/?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=60) as response:
            root = ElementTree.fromstring(response.read())

        for content in root.findall(f"{NAMESPACE}Contents"):
            key = content.findtext(f"{NAMESPACE}Key") or ""
            size = int(content.findtext(f"{NAMESPACE}Size") or 0)
            yield key, size

        if (root.findtext(f"{NAMESPACE}IsTruncated") or "false") != "true":
            return
        token = root.findtext(f"{NAMESPACE}NextContinuationToken")
        if not token:
            return


def human(size: int) -> str:
    value = float(size)
    for unit in ("o", "Kio", "Mio", "Gio", "Tio"):
        if value < 1024.0 or unit == "Tio":
            return f"{value:.1f} {unit}" if unit != "o" else f"{int(value)} o"
        value /= 1024.0
    return f"{value:.1f} Tio"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Taille d'un prefixe du bucket Vesuvius, sans telechargement.",
        epilog="Exemple: %(prog)s PHerc0332/segments/ --depth 1",
    )
    parser.add_argument("prefix", help="prefixe S3, p.ex. PHerc0332/volumes/")
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="niveaux de sous-dossiers a detailler sous le prefixe (defaut: 1)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="sortie machine pure sur stdout",
    )
    args = parser.parse_args()

    groups: dict[str, list[int]] = {}
    total_size = 0
    total_count = 0

    base_depth = args.prefix.count("/")
    for key, size in iter_objects(args.prefix):
        total_size += size
        total_count += 1
        parts = key.split("/")
        label = "/".join(parts[: base_depth + args.depth]) or key
        entry = groups.setdefault(label, [0, 0])
        entry[0] += size
        entry[1] += 1

    if args.as_json:
        json.dump(
            {
                "prefix": args.prefix,
                "total_bytes": total_size,
                "object_count": total_count,
                "groups": [
                    {"prefix": name, "bytes": data[0], "objects": data[1]}
                    for name, data in sorted(groups.items(), key=lambda kv: -kv[1][0])
                ],
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0

    if total_count == 0:
        print(f"{args.prefix} : aucun objet (prefixe inexistant ou vide)")
        return 1

    print(f"{args.prefix}  ->  {human(total_size)}  ({total_count} objets)")
    for name, (size, count) in sorted(groups.items(), key=lambda kv: -kv[1][0])[:25]:
        print(f"  {human(size):>12}  {count:>7} obj  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
