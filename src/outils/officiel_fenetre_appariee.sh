#!/bin/bash
# Le segment officiel, rendu dans LA MEME fenetre que nos tirages.
#
# ⚠⚠ Pourquoi ce script existe. `36` compare un bon segment officiel (17,3 µm d'ecart,
# 0 % de fenetres plates) a nos tirages (311 µm, 14 a 55 % de plates) -- mais l'officiel a
# ete rendu sur 31 couches et les notres sur 21, 41 ou 81. Or AUCUNE statistique de cet
# instrument n'est independante de la fenetre :
#
#   PHerc0257 r6 : plates 0,896 (21 c.) -> 0,740 (41 c.) -> 0,552 (81 c.)
#   PHerc1447 r4 : plates 0,451        -> 0,275        -> 0,135
#
# Une fenetre plus large contient plus de matiere, donc moins de fenetres « plates » et
# moins de pics au bord. Comparer 31 couches a 81 compare donc deux reglages autant que
# deux surfaces. Ce script refait l'officiel dans la fenetre des notres.
#
# ⚠ Il n'y a pas de valeur « vraie » a atteindre : ce que la comparaison appariee etablit
# est un ECART entre deux surfaces mesurees pareil, jamais une distance absolue.
#
#   ./src/outils/lancer.sh --fond src/outils/officiel_fenetre_appariee.sh [dest] [couches]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/officiel_appariee}
COUCHES=${2:-81}
SEG=20250702235910-auto_grown_20250702235910292
ROULEAU=PHerc1447
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr"
UM=8.64
mkdir -p "$DEST"
OUT="$DEST/officiel_${COUCHES}c.json"
[ -s "$OUT" ] && { echo "déjà fait : $OUT"; exit 0; }

# Le maillage a deja ete telecharge par src/outils/origine_de_la_pile.sh ; on le reutilise
# plutot que de le reprendre, et on refuse s'il n'est pas la.
M="$ROOT/data/origine_pile/mesh.tifxyz"
[ -f "$M/meta.json" ] || { echo "⚠ maillage absent — lancer d'abord src/outils/origine_de_la_pile.sh"; exit 3; }
PLAT="$ROOT/data/origine_pile/plat"
[ -d "$PLAT" ] || { echo "⚠ surface aplatie absente"; exit 3; }

rm -rf "$DEST/rendu"
vc_render_tifxyz -v "$DEST/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$PLAT" \
    --tif-output "$DEST/rendu" -n "$COUCHES" --slice-step 1 --auto-crop \
    > "$DEST/rendu.log" 2>&1 || { echo "⚠ rendu échoué"; exit 3; }
MILIEU=$(( COUCHES / 2 ))
( cd "$ROOT/inference_xpu" && uv run python ../src/volume/depth_profile.py "$DEST/rendu" \
    --grid --step 400 --traced-layer "$MILIEU" --voxel-um "$UM" --out "$OUT" ) \
  > "$DEST/profil.log" 2>&1 || { echo "⚠ dépouillement échoué"; exit 3; }
rm -rf "$DEST/cache"
python3 -c "
import json
d = json.load(open('$OUT')); d = d[0] if isinstance(d, list) else d
print(f\"officiel à $COUCHES couches : écart {d['ecart_trace_um_median']:.1f} µm  \"
      f\"plates {d['part_plates']:.3f}  bord {d['au_bord_intensite']:.3f}  \"
      f\"centre {d['tiers_central_intensite']:.3f}\")"
