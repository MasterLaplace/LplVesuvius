#!/bin/bash
# Assembler les SPIRES PUBLIEES d'un rouleau en une seule image.
#
# ⚠⚠ CE QUE CE SCRIPT FAIT ET CE QU'IL NE FAIT PAS. Il n'ouvre aucun rouleau : il
# ramasse les cartes d'encre que l'equipe du concours a DEJA publiees, une par spire,
# et les empile dans l'ordre de leur numero de spire. Le deroulement est le leur ;
# l'assemblage est le notre. Cette distinction doit rester ecrite partout ou l'image
# sort, sinon l'image ment sur son auteur.
#
# ⭐ Pourquoi ca vaut la peine quand meme : PHerc0172 publie les spires 052 a 095
# SANS TROU. Empilees dans l'ordre, elles sont un rouleau deroule -- l'image que ce
# projet vise, et surtout la REFERENCE contre laquelle mesurer notre propre chaine.
#
# ⚠ On liste par SEGMENT, jamais le prefixe entier du rouleau (piege nº 16 : un
# listage global enumere des dizaines de milliers de cles avant de filtrer, et sort
# en timeout). Un segment = deux requetes.
set -u
cd "$(dirname "$0")/../.." || exit 2
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
ROULEAU=${1:-PHerc0172}
MODELE=${2:-november}          # sous-chaine qui choisit le modele quand il y en a plusieurs
LISTE="docs/volumes_surface_$ROULEAU.txt"
DEST="data/mosaique/$ROULEAU"
INDEX="$DEST/index.tsv"

[ -f "$LISTE" ] || { echo "pas de liste de segments : $LISTE (lancer src/outils/lister_volumes_surface.sh $ROULEAU)" >&2; exit 3; }

# ⚠ Seuls les segments dont le NOM porte un numero de spire entrent : un segment
# « auto_grown » ou « title » n'a pas de place dans un empilement ordonne, et lui en
# inventer une produirait une image d'apparence correcte dont une bande est fausse.
SEGMENTS=$(grep -v '^#' "$LISTE" | cut -f1 | sort -u | grep -E -- '-w[0-9]+_')
[ -z "$SEGMENTS" ] && { echo "aucun segment numerote par spire dans $LISTE" >&2; exit 3; }

mkdir -p "$DEST"
: > "$INDEX"
n=0; manques=0
while read -r seg; do
  spire=$(sed 's/.*-w\([0-9]*\)_.*/\1/' <<< "$seg")
  cible="$DEST/spire_$spire.jpg"
  if [ ! -s "$cible" ]; then
    cles=$(curl -s --max-time 45 "$B/?list-type=2&prefix=$ROULEAU/segments/$seg/ink-detection/downsampled/&max-keys=40" \
           | tr '<' '\n' | grep '^Key>' | sed 's|^Key>||' | grep -i '\.jpg$')
    # ⚠ Quand plusieurs modeles sont publies, en prendre un AU HASARD melangerait deux
    # detecteurs dans une meme image : les spires n'auraient plus la meme signification.
    cle=$(grep -i -- "$MODELE" <<< "$cles" | head -1)
    [ -z "$cle" ] && cle=$(head -1 <<< "$cles")
    if [ -z "$cle" ]; then
      echo "  spire $spire : AUCUNE carte d'encre publiee" >&2
      manques=$((manques+1)); continue
    fi
    curl -s --max-time 180 -o "$cible" "$B/$cle" || { rm -f "$cible"; manques=$((manques+1)); continue; }
  fi
  printf '%s\t%s\t%s\n' "$spire" "$seg" "$cible" >> "$INDEX"
  n=$((n+1)); echo "  spire $spire : $(du -h "$cible" | cut -f1)"
done <<< "$SEGMENTS"

sort -n -o "$INDEX" "$INDEX"
echo "$n spire(s) recuperee(s), $manques manque(s) — index : $INDEX"
[ "$n" -eq 0 ] && exit 4
# ⚠ Tournait depuis `inference/` jusqu'au 2026-08-25, au motif que c'etait le seul
# environnement porteur de Pillow. C'etait FAUX depuis que la racine declare pillow>=10.0,
# et surtout NUISIBLE : `inference/` n'avait pas `numcodecs`, ce qui a deja fait conclure a
# tort qu'une graine n'etait pas couverte par la prediction (cf. `zarr_depth.py`). La racine
# porte PIL, numcodecs, numpy, scipy et tifffile -- strictement plus. `inference/` est retire.
uv run python src/volume/assembler_mosaique.py "$INDEX" \
   --sortie "docs/images/mosaique_$ROULEAU.png" --rouleau "$ROULEAU" \
   --json "docs/mosaique_$ROULEAU.json"
