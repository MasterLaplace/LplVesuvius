#!/bin/bash
# Compte de feuilles le long de z : une rupture brutale localise un degat en 3D.
# ⚠ Ecrit un marqueur de FIN : juger l'avancement par artefact et non par PID, parce
# qu'un wrapper qui rend la main ne dit rien du travail qu'il a lance.
set -u
# ⚠ La racine est DERIVEE, pas ecrite en dur : un chemin absolu reste le bon
# remede au piege du `cd` qui echoue, mais il ne doit pas porter le nom de
# compte de qui l'a ecrit -- le depot est destine a etre clone.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)" || exit 2
OUT=$ROOT/data/out
VOL=s3://vesuvius-challenge-open-data/PHerc0172/volumes/20241024131839-7.910um-53keV-masked.zarr
cd $ROOT/experiments
for Z in "$@"; do
  uv run python src/excision/radial.py compter PHerc0172 "$VOL" \
      --slice "$Z" --json "$OUT/z_$Z.json" > /dev/null 2>&1
done
touch "$OUT/SCAN_Z_FINI"
