#!/bin/bash
# Compte de feuilles le long de z : une rupture brutale localise un degat en 3D.
# ⚠ Ecrit un marqueur de FIN : juger l'avancement par artefact et non par PID, parce
# qu'un wrapper qui rend la main ne dit rien du travail qu'il a lance.
set -u
OUT=/home/masterlaplace/LplVesuvius/data/out
VOL=s3://vesuvius-challenge-open-data/PHerc0172/volumes/20241024131839-7.910um-53keV-masked.zarr
cd /home/masterlaplace/LplVesuvius/experiments
for Z in "$@"; do
  uv run python src/excision/radial.py compter PHerc0172 "$VOL" \
      --slice "$Z" --json "$OUT/z_$Z.json" > /dev/null 2>&1
done
touch "$OUT/SCAN_Z_FINI"
