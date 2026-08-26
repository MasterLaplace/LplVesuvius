#!/bin/bash
# EXACTEMENT leurs parametres -- rien de plus, rien de moins.
#
# ⚠⚠ Pourquoi cette experience existe, apres quatre autres. Avec leur graine, notre chaine
# produit une surface a plat quand la leur converge. Ont ete elimines par mesure :
#   - la graine            (c'est la leur)
#   - la prediction        (occupation 0,457, planarite 0,993 a ce point -- `sonder_point`)
#   - la longueur de trace (0,98 et 4,12 cm² echouent comme 23,76)
#   - le sens de la normale (identique dans les deux sens, `sens_de_la_normale`)
#
# ⭐ Reste une difference de PARAMETRES, et elle est lisible dans leur metadonnee. Leur
# `vc_gsfs_params` ne contient QUE :
#     generations 200, min_area_cm 0.3, mode random_seed, thread_limit 1, cache_root
# Le notre en contient deux de plus, hérités de `data/artefacts/PHerc0358/seed.json` :
#     search_effort 10, step_size 20.0
# Ne pas enregistrer un parametre veut dire l'avoir laisse au DEFAUT. Ce script part donc
# d'un fichier de parametres MINIMAL au lieu d'en retirer des cles d'un fichier existant --
# retirer laisse toujours planer le doute d'en avoir oublie une.
#
# ⚠ `voxelsize` est conserve : sans lui l'aire sort nulle et toute surface est rejetee
# (piege nº 28ter du HANDOFF). Ce n'est pas un reglage de trajectoire.
#
#   ./src/outils/lancer.sh --fond src/outils/leurs_parametres.sh [dest] [generations]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/leurs_parametres}
GEN=${2:-200}
ROULEAU=PHerc1447
GRAINE="4682 2740 13350"
UM=8.64
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr"
mkdir -p "$DEST"

lister() { curl -s --max-time 60 "$B/?list-type=2&prefix=$1&delimiter=/" \
           | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep -vxF "$1"; }
SURF=$(lister "$ROULEAU/representations/predictions/surfaces/" | grep '\.zarr/$' | head -1 | sed 's|/$||')
[ -z "$SURF" ] && { echo "⚠ pas de prédiction publiée"; exit 3; }

if [ ! -d "$DEST/trace" ]; then
  mkdir -p "$DEST/trace"
  cat > "$DEST/trace/seed.json" <<JSON
{
  "generations": $GEN,
  "min_area_cm": 0.3,
  "thread_limit": 1,
  "voxelsize": $UM
}
JSON
  ( cd "$DEST/trace" && timeout 3600 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
      -s $GRAINE > trace.log 2>&1 )
fi
M=$(ls -d "$DEST/trace"/auto_grown_* 2>/dev/null | head -1)
[ -z "$M" ] && { echo "⚠ aucun maillage — l'expérience ne dit RIEN sur les paramètres"; exit 3; }
AIRE=$(grep -oE 'generated surface [0-9.]+ vx\^2 \([0-9.]+ cm\^2\)' "$DEST/trace/trace.log" \
       | grep -oE '\([0-9.]+' | tr -d '(' | tail -1)
vc_tifxyz_selfcross --surface "$M" -o "$DEST/selfcross.json" > /dev/null 2>&1
CROIS=$(python3 "$ROOT/src/nappe/lire_selfcross.py" "$DEST/selfcross.json" 2>/dev/null || echo "?")
echo "aire ${AIRE:-?} cm² (eux : 3,95), $CROIS auto-intersections"
python3 -c "
import json, glob
d = json.load(open(glob.glob('$DEST/trace/auto_grown_*/meta.json')[0]))
print('  params effectifs :', json.dumps(d.get('vc_gsfs_params')))"

[ -d "$DEST/plat" ] || vc_flatten -i "$M" -o "$DEST/plat" > "$DEST/flatten.log" 2>&1
SERIE=""
for N in 41 161; do
  OUT="$DEST/profil_${N}c.json"
  if [ ! -s "$OUT" ]; then
    rm -rf "$DEST/rendu_$N"
    vc_render_tifxyz -v "$DEST/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$DEST/plat" \
        --tif-output "$DEST/rendu_$N" -n "$N" --slice-step 1 --auto-crop \
        > "$DEST/rendu_$N.log" 2>&1 || continue
    ( cd "$ROOT" && uv run python src/volume/depth_profile.py \
        "$DEST/rendu_$N" --grid --step 200 --traced-layer $((N / 2)) --voxel-um "$UM" \
        --out "$OUT" ) > "$DEST/profil_$N.log" 2>&1 || continue
  fi
  E=$(python3 -c "
import json; d=json.load(open('$OUT')); d=d[0] if isinstance(d,list) else d
print(f\"{d['ecart_trace_um_median']:.2f}\")" 2>/dev/null) || continue
  SERIE="$SERIE$N:$E,"
done
rm -rf "$DEST/cache"
[ -z "$SERIE" ] && { echo "⚠ aucun profil"; exit 3; }
( cd "$ROOT" && uv run python src/commun/test_convergence.py \
    --serie "${SERIE%,}" --nom "leurs paramètres exacts (${AIRE:-?} cm²)" \
    --json "$ROOT/docs/mesures/leurs_parametres.json" )
