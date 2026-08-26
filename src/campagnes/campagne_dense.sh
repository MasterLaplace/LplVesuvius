#!/bin/bash
# Re-mesurer la part de matiere avec un sondage DENSE, un fichier par segment.
#
# ⚠ `19` §9 a montre que le classement par `avec_matiere` n'est que moderement stable
# entre deux grilles (rho +0,280). Le remede nomme la est de mesurer mieux, pas de
# choisir la grille qui donne le meilleur p. 392 points au lieu de 72.
#
# ⚠⚠ REPRENABLE, un fichier par segment. La premiere version passait toutes les cles a
# un seul appel avec un unique --out : deux heures et demie de calcul suspendues a une
# seule ecriture finale, c'est-a-dire le piege nº 13 du depot (dix bandes calculees puis
# perdues) reecrit a l'identique.
set -u
cd "$(dirname "$0")/../.." || exit 2
SCROLL=${1:-PHercParis4}
MOTIF=${2:-2.4um}
DEST=${3:-docs/dense_PHercParis4}
FILS=${4:-24}
mkdir -p "$DEST"
awk -F'\t' -v m="$MOTIF" '$2 ~ m {print $1"\t"$2}' "docs/mesures/volumes_surface_$SCROLL.txt" \
| while IFS=$'\t' read -r seg key; do
  out="$DEST/$seg.json"
  [ -s "$out" ] && continue
  (uv run python src/commun/zarr_depth.py "$key" \
      --windows 200 --fils "$FILS" --out "../$out") || echo "  $seg ECHEC" >&2
done
echo "termine : $(ls "$DEST"/*.json 2>/dev/null | wc -l) segments"
