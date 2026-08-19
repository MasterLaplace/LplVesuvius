#!/bin/bash
# Le critere de graine tient-il sur les DIX rouleaux du prix que personne n'a traces ?
#
# ⚠⚠ Conception APPARIEE, et c'est tout l'interet : sur chaque rouleau on trace DEUX fois,
# une graine par critere, tout le reste identique (memes parametres, meme prediction, meme
# machine). Un rouleau est alors son propre temoin, et la difference ne peut pas etre mise
# sur le dos de « ce rouleau-la est plus facile ».
#
# ⚠ La taille de voxel est LUE sur le nom du volume de chaque rouleau, jamais empruntee a
# un autre. Sans `voxelsize`, `vc_grow_seg_from_seed` calcule une aire nulle et rejette
# TOUTE surface avec « area 0 below min_area_cm » -- le message accuse la surface, le
# fautif est le parametre. Et emprunter le chiffre d'un rouleau voisin est le piege nº 6.
#
# ⚠ Reprenable : un rouleau deja mesure est saute. Chaque rouleau ecrit son propre JSON.
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/graines}
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
mkdir -p "$DEST"

# Les dix rouleaux du Grand Prize SANS aucun segment publie (docs/23) : leur prix
# First Letters de 50 000 $ est intact.
ROULEAUX="PHerc0125 PHerc0191 PHerc0211 PHerc0257 PHerc0268 PHerc0358 PHerc0813 PHerc0826 PHerc1218 PHerc1545"

lister() { curl -s --max-time 60 "$B/?list-type=2&prefix=$1&delimiter=/" \
           | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep -vxF "$1"; }

for R in $ROULEAUX; do
  OUT="$DEST/$R.json"
  if [ -s "$OUT" ]; then echo "== $R deja fait"; continue; fi
  echo "== $R"

  SURF=$(lister "$R/representations/predictions/surfaces/" | grep '\.zarr/$' | head -1 | sed 's|/$||')
  VOL=$(lister "$R/volumes/" | head -1 | sed 's|/$||')
  if [ -z "$SURF" ] || [ -z "$VOL" ]; then echo "   ⚠ pas de prediction ou pas de volume"; continue; fi

  # ⚠ La resolution est DANS le nom du volume (« ...-9.362um-... »). On la lit, on ne la
  # suppose pas -- et on refuse de tracer si elle est absente.
  UM=$(basename "$VOL" | grep -oE '[0-9]+\.[0-9]+um' | head -1 | sed 's/um$//')
  if [ -z "$UM" ]; then echo "   ⚠ taille de voxel illisible dans « $(basename "$VOL") » — rouleau saute"; continue; fi
  echo "   voxel $UM µm"

  WORK="$DEST/$R.trace"; rm -rf "$WORK"; mkdir -p "$WORK"
  sed "s/\"voxelsize\": [0-9.]*/\"voxelsize\": $UM/" \
      "$ROOT/artefacts/PHerc0358/seed.json" > "$WORK/seed.json"

  LIGNES=""
  for CRIT in planarite voisinage; do
    # ⚠ « voisinage » est rejoue dans SA configuration d'origine (niveau 2, bloc 5), celle
    # qui a produit la trace de docs/24. Le comparer dans la configuration de l'autre
    # critere ne dirait rien de ce qui a ete reellement fait.
    if [ "$CRIT" = planarite ]; then NIV=0; BLOC=8; else NIV=2; BLOC=5; fi
    GJ="$DEST/$R.$CRIT.json"
    ( cd "$ROOT/experiments" && timeout 1800 uv run python -u ../analysis/src/trouver_graine.py \
        "$SURF" --level $NIV --chunks 25 --bloc $BLOC --critere "$CRIT" --candidats 1 \
        --voxel-um "$UM" --out "$GJ" ) > "$DEST/$R.$CRIT.log" 2>&1
    if [ ! -s "$GJ" ]; then echo "   ⚠ $CRIT : aucune graine"; continue; fi
    read -r X Y Z <<<"$(python3 -c "
import json,sys
c=json.load(open('$GJ'))['candidats']
print(c[0]['x'], c[0]['y'], c[0]['z']) if c else sys.exit(1)")" || { echo "   ⚠ $CRIT : json vide"; continue; }

    SEG="$WORK/$CRIT"; rm -rf "$SEG"; mkdir -p "$SEG"; cp "$WORK/seed.json" "$SEG/"
    ( cd "$SEG" && timeout 1800 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
        -s "$X" "$Y" "$Z" ) > "$DEST/$R.$CRIT.trace.log" 2>&1
    AIRE=$(grep -oE 'generated surface .* \(([0-9.]+) cm\^2\)' "$DEST/$R.$CRIT.trace.log" \
           | grep -oE '\(([0-9.]+)' | tr -d '(' | tail -1)
    SURFDIR=$(ls -d "$SEG"/auto_grown_* 2>/dev/null | head -1)
    if [ -z "$SURFDIR" ]; then echo "   ⚠ $CRIT : aucune surface produite"; continue; fi
    vc_tifxyz_selfcross --surface "$SURFDIR" -o "$DEST/$R.$CRIT.selfcross.json" \
        > "$DEST/$R.$CRIT.selfcross.log" 2>&1
    CROIS=$(python3 -c "
import json
d=json.load(open('$DEST/$R.$CRIT.selfcross.json'))
print(sum(c['transverse'] for c in d['census']))" 2>/dev/null || echo "?")
    printf '   %-10s graine %6s %6s %6s   aire %8s cm²   auto-intersections %s\n' \
        "$CRIT" "$X" "$Y" "$Z" "${AIRE:-?}" "$CROIS"
    LIGNES="$LIGNES{\"critere\":\"$CRIT\",\"x\":$X,\"y\":$Y,\"z\":$Z,\"aire_cm2\":${AIRE:-null},\"transverse\":${CROIS:-null}},"
  done
  printf '{"rouleau":"%s","voxel_um":%s,"surface":"%s","essais":[%s]}\n' \
      "$R" "$UM" "$SURF" "${LIGNES%,}" > "$OUT"
done
echo "campagne finie — $DEST"
