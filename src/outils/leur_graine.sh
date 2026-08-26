#!/bin/bash
# LEUR graine dans NOTRE chaine -- le seed suffit-il ?
#
# ⚠⚠ Pourquoi cette experience existe. `38` etablit qu'une trace a nous ne suit AUCUNE
# feuille : la distance mesuree suit la fenetre de rendu (α = +1,01) la ou un segment
# officiel ne bouge pas (α = +0,00). Reste a savoir d'ou vient la difference -- et le
# metadonnee `mesh/intermediate/tifxyz_original/meta.json` du segment officiel donne
# EXACTEMENT de quoi la lever :
#
#   seed            [4682.22, 2740.29, 13350.10]
#   source          vc_grow_seg_from_seed          <- le meme outil que nous
#   vc_gsfs_mode    explicit_seed
#   vc_gsfs_params  generations 200, min_area_cm 0.3, thread_limit 1, mode random_seed
#   scale           0.05  ->  step_size 20         <- le meme pas que nous
#
# ⭐ Trois issues, et chacune dit quoi faire ensuite :
#   converge  -> la GRAINE (ou ces parametres) fait tout ; notre choix de graine est en
#                cause, et `25` est a reprendre ;
#   ne converge pas -> notre chaine differe d'eux autrement (prediction, cache EDT,
#                version de l'outil), et c'est la qu'il faut chercher ;
#   pas de maillage -> le seul cas ou l'experience ne dit rien, et il faut le distinguer
#                des deux autres au lieu de le lire comme un echec de la graine.
#
# ⚠ Deux differences avec eux qu'on ne peut PAS effacer, et qui limitent la conclusion :
# ils lisent un cache EDT prive (`/workspace/caches/1447_edt_cache`) quand nous lisons la
# prediction de surface publiee, et leur version d'outil est « dev » a une date inconnue.
#
# ⚠ Le verdict est rendu par le test de convergence, donc DEUX rendus. Un seul rendrait un
# nombre dont `38` vient de montrer qu'il ne veut rien dire tout seul.
#
#   ./src/outils/lancer.sh --fond src/outils/leur_graine.sh [dest]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/leur_graine}
ROULEAU=PHerc1447
GRAINE="4682 2740 13350"
UM=8.64
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr"
mkdir -p "$DEST"

lister() { curl -s --max-time 60 "$B/?list-type=2&prefix=$1&delimiter=/" \
           | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep -vxF "$1"; }

if [ ! -d "$DEST/trace" ]; then
  SURF=$(lister "$ROULEAU/representations/predictions/surfaces/" | grep '\.zarr/$' | head -1 | sed 's|/$||')
  [ -z "$SURF" ] && { echo "⚠ pas de prédiction publiée"; exit 3; }
  mkdir -p "$DEST/trace"
  # Leurs parametres, pas les notres : 200 generations et thread_limit 1.
  python3 -c "
import json
p = json.load(open('$ROOT/artefacts/PHerc0358/seed.json'))
p.update({'generations': 200, 'thread_limit': 1, 'voxelsize': $UM})
json.dump(p, open('$DEST/trace/seed.json', 'w'), indent=2)"
  ( cd "$DEST/trace" && timeout 3600 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
      -s $GRAINE > trace.log 2>&1 )
fi
M=$(ls -d "$DEST/trace"/auto_grown_* 2>/dev/null | head -1)
[ -z "$M" ] && { echo "⚠ aucun maillage produit — l'expérience ne dit RIEN sur la graine"; exit 3; }
AIRE=$(grep -oE 'generated surface [0-9.]+ vx\^2 \([0-9.]+ cm\^2\)' "$DEST/trace/trace.log" \
       | grep -oE '\([0-9.]+' | tr -d '(' | tail -1)
vc_tifxyz_selfcross --surface "$M" -o "$DEST/selfcross.json" > /dev/null 2>&1
CROIS=$(python3 "$ROOT/src/nappe/lire_selfcross.py" "$DEST/selfcross.json" 2>/dev/null || echo "?")
echo "trace obtenue : ${AIRE:-?} cm², $CROIS auto-intersections  (eux : 3,95 cm²)"

[ -d "$DEST/plat" ] || vc_flatten -i "$M" -o "$DEST/plat" > "$DEST/flatten.log" 2>&1
SERIE=""
for N in 41 161; do
  OUT="$DEST/profil_${N}c.json"
  if [ ! -s "$OUT" ]; then
    rm -rf "$DEST/rendu_$N"
    vc_render_tifxyz -v "$DEST/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$DEST/plat" \
        --tif-output "$DEST/rendu_$N" -n "$N" --slice-step 1 --auto-crop \
        > "$DEST/rendu_$N.log" 2>&1 || { echo "⚠ rendu $N couches échoué"; continue; }
    ( cd "$ROOT/inference_xpu" && uv run python ../src/volume/depth_profile.py \
        "$DEST/rendu_$N" --grid --step 400 --traced-layer $((N / 2)) --voxel-um "$UM" \
        --out "$OUT" ) > "$DEST/profil_$N.log" 2>&1 || continue
  fi
  E=$(python3 -c "
import json; d=json.load(open('$OUT')); d=d[0] if isinstance(d,list) else d
print(f\"{d['ecart_trace_um_median']:.2f}\")" 2>/dev/null) || continue
  SERIE="$SERIE$N:$E,"
  echo "  $N couches : écart $E µm"
done
rm -rf "$DEST/cache"
[ -z "$SERIE" ] && { echo "⚠ aucun profil — verdict impossible"; exit 3; }
( cd "$ROOT/experiments" && uv run python ../src/commun/test_convergence.py \
    --serie "${SERIE%,}" --nom "leur graine, notre chaîne" \
    --json "$ROOT/docs/mesures/leur_graine.json" )
