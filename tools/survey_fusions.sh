#!/bin/bash
# Balayer le rouleau ENTIER a la recherche de fusions, par BANDES.
#
# ⚠⚠ Pourquoi des bandes et non un balayage continu. La mesure de persistance ne
# porte que sur des coupes ADJACENTES : mesure, tout le signal est a 0,8 mm d'ecart
# (9,3 % de coincidences contre 1,1 % au hasard) et il n'y a plus rien
# d'interpretable au-dela. Un balayage continu du rouleau a ce pas ferait 20 000
# coupes ; des bandes courtes reparties donnent la meme information locale pour un
# centieme du travail.
#
# ⚠ Au NIVEAU 2 : `pyramid.py` a etabli qu'il conserve 89 % des murs pour 33 Gio au
# lieu de 2100. C'est un CRIBLE — les candidats qu'il sort doivent etre confirmes au
# niveau 0, parce que les deux niveaux ne trouvent pas les memes sites (fond 10,3 %
# contre 6,6 %).
set -u
VOL=${VOL:-s3://vesuvius-challenge-open-data/PHerc0172/volumes/20241024131839-7.910um-53keV-masked.zarr}
OUT=${1:-/home/masterlaplace/LplVesuvius/docs/survey}
BANDS=${2:-10}
PER=${3:-5}
STEP=${4:-100}        # 100 voxels = 0,8 mm, l'ecart ou le signal existe
Z0=${5:-1336}
Z1=${6:-12598}

mkdir -p "$OUT"
cd /home/masterlaplace/LplVesuvius/experiments || exit 2
SPAN=$(( (Z1 - Z0) / BANDS ))
echo "balayage par bandes : $BANDS bandes de $PER coupes, pas $STEP vx, de $Z0 a $Z1"
for b in $(seq 0 $((BANDS - 1))); do
  LO=$(( Z0 + b * SPAN ))
  HI=$(( LO + (PER - 1) * STEP ))
  F="$OUT/bande_$(printf '%02d' "$b").json"
  [ -s "$F" ] && { echo "  bande $b deja faite"; continue; }
  echo "  bande $b : z $LO -> $HI"
  uv run python src/excision/fusion_scan.py PHerc0172 "$VOL" "$F" \
      --level 2 --slices "$PER" --z-min "$LO" --z-max "$HI" 2>/dev/null \
      | grep -E "anormales|coincidentes|VERDICT" | sed 's/^/      /'
done
touch "$OUT/.complet"
echo "termine"
