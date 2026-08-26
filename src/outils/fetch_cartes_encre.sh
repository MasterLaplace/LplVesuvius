#!/bin/bash
# Recuperer les cartes d'encre PUBLIEES (version reduite) d'un rouleau.
#
# ⚠⚠ C'est ce qui rend la validation abordable : le RESULTAT sans lancer 43 minutes
# d'inference par segment. La version `downsampled/*.jpg` pese ~2,8 Mo la ou la carte
# pleine resolution en pese des centaines.
#
# ⚠ Un JPG est compresse avec perte, donc il ne sert PAS a mesurer une valeur d'encre.
# Il sert a ce dont on a besoin ici : dire si un segment porte des formes de lettres,
# ce qu'un juge lit tout aussi bien sur une version reduite.
set -u
cd "$(dirname "$0")/../.." || exit 2
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
SCROLL=${1:-PHercParis4}
DEST=${2:-data/encre/$SCROLL}
mkdir -p "$DEST"
awk -F'\t' '$3>0{print $1}' "docs/mesures/volumes_surface_$SCROLL.txt" | sort -u | while read -r seg; do
  [ -s "$DEST/$seg.jpg" ] && continue
  key=$(curl -s --max-time 40 "$B/?list-type=2&prefix=$SCROLL/segments/$seg/ink-detection/downsampled/&max-keys=5" \
        | tr '<' '\n' | grep "^Key>" | sed 's|^Key>||' | grep -i '\.jpg$' | head -1)
  [ -z "$key" ] && { echo "  $seg : aucune version reduite"; continue; }
  if curl -sS --fail --location --retry 8 --retry-delay 3 --continue-at - \
          -o "$DEST/$seg.jpg.part" "$B/$key"; then
    mv "$DEST/$seg.jpg.part" "$DEST/$seg.jpg"
    echo "  $seg  $(du -h "$DEST/$seg.jpg" | cut -f1)"
  else
    rm -f "$DEST/$seg.jpg.part"; echo "  $seg ECHEC" >&2
  fi
done
echo "termine : $(ls "$DEST"/*.jpg 2>/dev/null | wc -l) cartes"
