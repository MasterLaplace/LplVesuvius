#!/bin/bash
# Champ de correction sur tous les segments d'un rouleau qui publient un volume de surface.
#
# ⚠ La campagne est REPRENABLE : chaque segment ecrit son propre fichier, donc une
# interruption ne coute que le segment en cours. C'est la lecon des 10 bandes calculees
# puis perdues (piege nº 13).
set -u
cd "$(dirname "$0")/../.." || exit 2
SCROLL=${1:-PHercParis4}
MOTIF=${2:-2.4um}
VOXEL=${3:-2.4}
DEST=${4:-docs/champ_$SCROLL}
FILS=${5:-24}
mkdir -p "$DEST"
awk -F'\t' -v m="$MOTIF" '$2 ~ m {print $1"\t"$2}' "docs/volumes_surface_$SCROLL.txt" \
| while IFS=$'\t' read -r seg key; do
  out="$DEST/$seg.json"
  [ -s "$out" ] && continue
  (cd inference_xpu && uv run python ../src/nappe/champ_correction.py "$key" \
      --voxel-um "$VOXEL" --fils "$FILS" --out "../$out") || echo "  $seg ECHEC" >&2
done
echo "termine : $(ls "$DEST"/*.json 2>/dev/null | wc -l) segments"
