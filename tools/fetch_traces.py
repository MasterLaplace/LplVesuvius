#!/usr/bin/env python3
"""Recuperer les traces `tifxyz` d'un corpus publie, depuis le bucket ouvert.

⚠ **Pourquoi pas `aws s3 cp`** : le client `aws` est absent de cette machine (deja note
dans `docs/03`), et de toute facon `--include` enumere TOUT le prefixe avant de filtrer
-- le piege nº 16 du depot. Le bucket est public en HTTPS et son API de listage accepte
un prefixe **par segment**, donc on ne liste que ce qu'on veut.

⚠ **Le nom du repertoire `tifxyz` porte le volume ET la taille de voxel** :
`<segment>-on-<volume>-<taille>um.tifxyz`. Il n'est donc pas devinable depuis le nom du
segment, et le supposer produirait des 404 qui ressemblent a « ce segment n'a pas de
maillage ». On le LIT dans le listage.

⭐ Et cette lecture a montre qu'un meme segment de PHerc0139 existe en **7,91 µm** et en
**2,403 µm** -- deux campagnes de scan, la meme trace. C'est ce que `06` §3.6 demande,
en comparaison appariee.

⚠ Transfert **reprenable** (`--continue-at -`) et refus franc sur un 404 (`--fail`),
pour la meme raison que `fetch_layers.sh` : sans ca, une page d'erreur HTML finirait
ecrite dans un `.tif`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"


def list_prefix(prefix: str, timeout: float = 60.0) -> list[str]:
    """Cles sous un prefixe, via l'API de listage S3 en HTTPS."""
    url = f"{BUCKET}/?list-type=2&prefix={prefix}&max-keys=1000"
    out = subprocess.run(["curl", "-s", "--max-time", str(int(timeout)), url],
                         capture_output=True, text=True)
    return re.findall(r"<Key>([^<]+)</Key>", out.stdout)


def fetch(key: str, target: Path, timeout: float) -> bool:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and target.stat().st_size > 0:
        return True
    part = target.with_suffix(target.suffix + ".part")
    done = subprocess.run(
        ["curl", "-sS", "--fail", "--location", "--retry", "10", "--retry-delay", "3",
         "--retry-all-errors", "--continue-at", "-", "--max-time", str(int(timeout)),
         "-o", str(part), f"{BUCKET}/{key}"],
        capture_output=True, text=True)
    if done.returncode != 0:
        part.unlink(missing_ok=True)
        print(f"    ECHEC {key}: {done.stderr.strip()[:120]}", file=sys.stderr)
        return False
    part.rename(target)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recuperer les traces tifxyz d'un corpus publie.",
        epilog="Le nom du repertoire tifxyz est LU dans le listage, jamais devine.",
    )
    parser.add_argument("index", type=Path, help="results/index.json de windcheck")
    parser.add_argument("corpus", help="ex: PHerc0139")
    parser.add_argument("dest", type=Path)
    parser.add_argument("--voxel", default="",
                        help="ne prendre que les tifxyz de cette taille de voxel "
                             "(ex: 7.91). Vide = toutes, ce qui recupere les deux "
                             "campagnes de scan quand elles existent")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=600.0)
    args = parser.parse_args()

    records = [r for r in json.loads(args.index.read_text()) if r["corpus"] == args.corpus]
    if args.limit:
        records = records[: args.limit]
    if not records:
        print(f"erreur : aucun segment pour le corpus {args.corpus}", file=sys.stderr)
        return 2
    print(f"{len(records)} segments dans {args.corpus}")

    taken = skipped = failed = 0
    for order, record in enumerate(records, 1):
        segment = record["segment"]
        keys = list_prefix(f"{args.corpus}/segments/{segment}/mesh/")
        wanted = [k for k in keys if k.endswith((".tif", "meta.json"))]
        if args.voxel:
            wanted = [k for k in wanted if f"-{args.voxel}um.tifxyz/" in k]
        if not wanted:
            print(f"  [{order}/{len(records)}] {segment[:40]:40} aucun maillage")
            skipped += 1
            continue
        ok = True
        for key in wanted:
            # ⚠ On rejoue la structure du bucket sous `dest` : deux campagnes de scan
            # du meme segment ne doivent PAS finir dans le meme repertoire.
            target = args.dest / key.split(f"{args.corpus}/segments/", 1)[1]
            ok &= fetch(key, target, args.timeout)
        variants = {k.split("/mesh/")[1].split("/")[0] for k in wanted}
        print(f"  [{order}/{len(records)}] {segment[:40]:40} {len(variants)} maillage(s) "
              f"{'ok' if ok else 'INCOMPLET'}", flush=True)
        taken += 1
        failed += 0 if ok else 1

    print(f"\n{taken} segments recuperes, {skipped} sans maillage, {failed} incomplets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
