#!/bin/bash
# Separabilite des feuilles sur les 13 rouleaux du Grand Prize, plus des temoins.
#
# ⚠⚠ CE QUE LE CONCOURS NOMME COMME MANQUANT. Le tableau des goulots de
# `2026_open_problems` dit, pour les regions comprimees : « What would help : **scan-
# quality metrics** ». Et il definit le defaut : « some regions lose effective
# **separability** between layers ». C'est exactement ce qu'un d′ mesure.
#
# ⚠ Le temoin decisif est PHerc0139 : il a ete trace ET son titre a ete retrouve, et il
# possede un scan au MEME protocole que les 13 (9,362 µm / 1,2 m / 113 keV). Comparer
# les rouleaux du prix a lui, c'est comparer a scroll tractable a qualite egale.
set -u
cd "$(dirname "$0")/.." || exit 2
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
OUT=${1:-docs/carte_separabilite}
mkdir -p "$OUT"
for s in PHerc0125 PHerc0191 PHerc0211 PHerc0257 PHerc0268 PHerc0358 \
         PHerc0800 PHerc0813 PHerc0826 PHerc1203 PHerc1218 PHerc1447 PHerc1545; do
  f="$OUT/$s.json"
  [ -s "$f" ] && { echo "  $s deja fait"; continue; }
  # ⚠ Le nom du volume porte la taille de voxel : on la LIT au lieu de la deviner.
  k=$(curl -s --max-time 40 "$B/?list-type=2&prefix=$s/volumes/&delimiter=/" \
      | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep -E '(8\.640|9\.362)um' | head -1)
  [ -z "$k" ] && { echo "  $s : aucun volume au protocole du prix"; continue; }
  v=$(grep -oE '[0-9]+\.[0-9]+um' <<<"$k" | head -1 | tr -d 'um')
  echo "=== $s (voxel $v µm) ==="
  ( cd inference_xpu && uv run python ../analysis/src/separabilite_scan.py "${k%/}" \
      --level 1 --voxel-um "$v" --chunks 27 --out "../$f" 2>&1 \
      | grep -E "grille|chunks mesures|d′" | sed "s/^/  [$s] /" )
done
echo "termine"
