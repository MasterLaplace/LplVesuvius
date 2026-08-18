#!/bin/bash
# Quels segments publient un volume de surface Zarr — donc un profil de profondeur
# lisible A DISTANCE pour 1,78 Mo la fenetre, au lieu de 32 Go la pile.
#
# ⚠ On liste par SEGMENT, jamais le prefixe entier du rouleau : c'est le piege nº 16
# du depot (`aws s3 cp --include` enumere tout avant de filtrer).
set -u
cd "$(dirname "$0")/.." || exit 2
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
SCROLL=${1:-PHercParis4}
OUT=${2:-docs/volumes_surface_$SCROLL.txt}
: > "$OUT"
curl -s --max-time 60 "$B/?list-type=2&prefix=$SCROLL/segments/&delimiter=/&max-keys=1000" \
  | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | while read -r p; do
  seg=$(basename "$p")
  keys=$(curl -s --max-time 40 "$B/?list-type=2&prefix=${p}surface-volumes/&delimiter=/" \
         | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$')
  [ -z "$keys" ] && continue
  # ⚠ Une carte d'encre publiee, quand elle existe, donne le RESULTAT sans qu'on ait a
  # lancer 43 minutes d'inference. C'est ce qui rend la validation abordable.
  ink=$(curl -s --max-time 30 "$B/?list-type=2&prefix=${p}ink-detection/&max-keys=3" \
        | grep -c "<Key>")
  while read -r z; do
    printf '%s\t%s\t%s\n' "$seg" "${z%/}" "$ink" >> "$OUT"
  done <<< "$keys"
  echo "  $seg : $(wc -l <<< "$keys") volume(s), $ink carte(s) d'encre"
done
echo "ecrit : $OUT  ($(wc -l < "$OUT") lignes)"
