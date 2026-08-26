#!/bin/bash
# Une trace COURTE converge-t-elle ? -- la piste que la comparaison avec eux designe.
#
# ⚠⚠ Pourquoi cette experience existe. Avec LEUR graine et LEURS 200 generations, notre
# chaine produit 23,76 cm² la ou leur segment officiel en fait 3,95 -- six fois plus. Et
# `38` mesure que la notre ne suit aucune feuille (α = +1,01) quand la leur converge
# (α = +0,00).
#
# ⭐ L'hypothese que ca designe : le traceur part juste, puis se perd. Pres de la graine la
# feuille n'est pas ambigue ; loin, il traverse. Une trace ARRETEE TOT resterait alors sur
# sa feuille -- et c'est exactement la brique dont un enchainement spire a spire a besoin.
#
# ⚠ Le verdict est rendu par le test de convergence de `38`, donc DEUX rendus par trace. Un
# seul rendrait un nombre dont ce document montre qu'il ne veut rien dire tout seul.
#
# ⚠ Les fenetres sont choisies en PROFONDEUR PHYSIQUE et non en couches : a 8,64 µm, 41
# couches couvrent 354 µm et 161 en couvrent 1391. Une trace qui converge doit le faire
# dans les deux.
#
#   ./src/outils/lancer.sh --fond src/outils/petite_trace.sh [dest] [generations...]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/petite_trace}
shift 2>/dev/null || true
GENS=${*:-"15 30 60"}
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

for G in $GENS; do
  W="$DEST/g$G"
  if [ ! -d "$W/trace" ]; then
    mkdir -p "$W/trace"
    python3 -c "
import json
p = json.load(open('$ROOT/data/artefacts/PHerc0358/seed.json'))
p.update({'generations': $G, 'thread_limit': 1, 'voxelsize': $UM})
json.dump(p, open('$W/trace/seed.json','w'), indent=2)"
    ( cd "$W/trace" && timeout 1800 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
        -s $GRAINE > trace.log 2>&1 )
  fi
  M=$(ls -d "$W/trace"/auto_grown_* 2>/dev/null | head -1)
  [ -z "$M" ] && { echo "g=$G : aucun maillage"; continue; }
  AIRE=$(grep -oE 'generated surface [0-9.]+ vx\^2 \([0-9.]+ cm\^2\)' "$W/trace/trace.log" \
         | grep -oE '\([0-9.]+' | tr -d '(' | tail -1)
  vc_tifxyz_selfcross --surface "$M" -o "$W/selfcross.json" > /dev/null 2>&1
  CROIS=$(python3 "$ROOT/src/nappe/lire_selfcross.py" "$W/selfcross.json" 2>/dev/null || echo "?")
  [ -d "$W/plat" ] || vc_flatten -i "$M" -o "$W/plat" > "$W/flatten.log" 2>&1
  SERIE=""
  for N in 41 161; do
    OUT="$W/profil_${N}c.json"
    if [ ! -s "$OUT" ]; then
      rm -rf "$W/rendu_$N"
      vc_render_tifxyz -v "$W/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$W/plat" \
          --tif-output "$W/rendu_$N" -n "$N" --slice-step 1 --auto-crop \
          > "$W/rendu_$N.log" 2>&1 || continue
      ( cd "$ROOT/inference_xpu" && uv run python ../src/volume/depth_profile.py \
          "$W/rendu_$N" --grid --step 200 --traced-layer $((N / 2)) --voxel-um "$UM" \
          --out "$OUT" ) > "$W/profil_$N.log" 2>&1 || continue
    fi
    E=$(python3 -c "
import json; d=json.load(open('$OUT')); d=d[0] if isinstance(d,list) else d
print(f\"{d['ecart_trace_um_median']:.2f}\")" 2>/dev/null) || continue
    SERIE="$SERIE$N:$E,"
  done
  rm -rf "$W/cache"
  printf 'g=%-4s aire %-9s cm²  croisements %-6s  série %s\n' "$G" "${AIRE:-?}" "$CROIS" "${SERIE%,}"
  [ -n "$SERIE" ] && ( cd "$ROOT/experiments" && uv run python \
      ../src/commun/test_convergence.py --serie "${SERIE%,}" --nom "g=$G (${AIRE:-?} cm²)" \
      --json "$ROOT/docs/petite_trace_g$G.json" | tail -3 )
done
