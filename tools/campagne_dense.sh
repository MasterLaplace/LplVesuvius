#!/bin/bash
# Re-mesurer la part de matiere avec un sondage DENSE.
#
# ⚠ `19` §9 a montre que le classement par `avec_matiere` n'est que moderement stable
# entre deux grilles (rho +0,280). Le remede nomme la est de mesurer mieux, pas de
# choisir la grille qui donne le meilleur p. 392 points au lieu de 72.
set -u
cd "$(dirname "$0")/.." || exit 2
SCROLL=${1:-PHercParis4}
MOTIF=${2:-2.4um}
OUT=${3:-docs/profondeur_dense.json}
FILS=${4:-24}
KEYS=$(awk -F'\t' -v m="$MOTIF" '$2 ~ m {print $2}' "docs/volumes_surface_$SCROLL.txt")
cd inference_xpu || exit 2
# shellcheck disable=SC2086
uv run python ../analysis/src/zarr_depth.py $KEYS --windows 200 --fils "$FILS" --out "../$OUT"
