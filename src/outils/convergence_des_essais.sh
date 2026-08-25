#!/bin/bash
# Les traces que nos instruments CONDAMNENT convergent-elles ?
#
# ⚠⚠ L'hypothese qui inverse tout, et il faut la tester avant d'y croire. `38` etablit que
# nos traces PROPRES -- zero auto-intersection -- sont des coupes radiales : leur profil de
# profondeur est plat, leur normale reste dans une meme feuille. Or une coupe radiale ne
# PEUT PAS se croiser elle-meme : c'est une nappe qui traverse le rouleau une fois.
#
# ⭐ A l'inverse, une surface qui suit reellement une spire revient pres d'elle-meme a chaque
# tour, et pres du coeur ou les spires se serrent, elle a toutes les raisons de se toucher.
# Il se pourrait donc que nous ayons jete les bonnes traces et garde les mauvaises.
#
# ⚠ Ce n'est PAS une raison de croire l'hypothese : elle est seduisante, et ce depot a
# refute quatre hypotheses seduisantes aujourd'hui. Elle se mesure, sur les traces deja sur
# le disque, avec le test de convergence.
#
# ⚠ Les essais compares viennent de `26` : ils partagent graine, rouleau et parametres a une
# cle pres, ce qui est la seule facon de ne pas confondre le reglage et la surface.
#
#   ./src/outils/lancer.sh --fond src/outils/convergence_des_essais.sh [dest] [essais...]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/convergence_essais}
shift 2>/dev/null || true
ESSAIS=${*:-"essai_ng2 essai_scale1"}
ROULEAU=PHerc0358
UM=9.362
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250821151737-9.362um-1.2m-113keV-masked.zarr"
mkdir -p "$DEST"

for E in $ESSAIS; do
  M=$(ls -d "$ROOT/data/trace/$ROULEAU/$E"/auto_grown_* 2>/dev/null | head -1)
  [ -z "$M" ] && { echo "$E : aucun maillage"; continue; }
  W="$DEST/$E"; mkdir -p "$W"
  CROIS=$(python3 "$ROOT/src/nappe/lire_selfcross.py" \
            "$ROOT/data/trace/$ROULEAU/$E/selfcross.json" 2>/dev/null || echo "?")
  [ -d "$W/plat" ] || vc_flatten -i "$M" -o "$W/plat" > "$W/flatten.log" 2>&1
  [ -d "$W/plat" ] || { echo "$E : vc_flatten a échoué"; continue; }
  SERIE=""
  for N in 41 161; do
    OUT="$W/profil_${N}c.json"
    if [ ! -s "$OUT" ]; then
      rm -rf "$W/rendu_$N"
      vc_render_tifxyz -v "$W/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$W/plat" \
          --tif-output "$W/rendu_$N" -n "$N" --slice-step 1 --auto-crop \
          > "$W/rendu_$N.log" 2>&1 || continue
      ( cd "$ROOT/inference_xpu" && uv run python ../src/volume/depth_profile.py \
          "$W/rendu_$N" --grid --step 400 --traced-layer $((N / 2)) --voxel-um "$UM" \
          --out "$OUT" ) > "$W/profil_$N.log" 2>&1 || continue
    fi
    E_UM=$(python3 -c "
import json; d=json.load(open('$OUT')); d=d[0] if isinstance(d,list) else d
print(f\"{d['ecart_trace_um_median']:.2f}\")" 2>/dev/null) || continue
    SERIE="$SERIE$N:$E_UM,"
  done
  rm -rf "$W/cache"
  [ -z "$SERIE" ] && { echo "$E : aucun profil"; continue; }
  echo "== $E  ($CROIS auto-intersections)"
  ( cd "$ROOT/experiments" && uv run python ../src/commun/test_convergence.py \
      --serie "${SERIE%,}" --nom "$E ($CROIS croisements)" \
      --json "$ROOT/docs/convergence_$E.json" | tail -3 )
done
