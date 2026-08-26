#!/bin/bash
# `thread_limit` change-t-il le VERDICT, et pas seulement l'aire ?
#
# ⚠⚠ Pourquoi cette mesure existe. `24` a condamne une trace sur 240 auto-intersections,
# avec `thread_limit: 0`. La campagne des pas, qui pose `thread_limit: 1`, rejoue la MEME
# graine au MEME pas et rend ZERO. La seule difference entre les deux fichiers de
# parametres est cette ligne.
#
# ⚠ `25` §4ter avait mesure que les JOURNAUX DE CROISSANCE sont identiques au centieme
# quelle que soit la valeur -- mais que l'ETAPE FINALE ne l'est pas. Les auto-intersections
# se mesurent sur le maillage final. Si le verdict d'un document depend d'un reglage de
# threads, il faut le savoir, et ce n'est pas une question qu'une relecture tranche.
#
# On repete CHAQUE configuration pour separer l'effet du reglage de la variance de run.
# Une seule execution par valeur ne distinguerait pas les deux.
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/trace/PHerc0358/thread_limit}
GRAINE=${2:-"1544 1544 7768"}
REPETITIONS=${3:-2}
S="https://vesuvius-challenge-open-data.s3.amazonaws.com/PHerc0358/representations/predictions/surfaces/20250821151737-surface-20260413222639-surface-m7-L0-th0.2.zarr"
mkdir -p "$DEST"

for TL in 0 1; do
  for R in $(seq 1 "$REPETITIONS"); do
    D="$DEST/tl${TL}_r${R}"
    if [ -s "$D/resume.json" ]; then echo "== tl=$TL r=$R deja fait"; continue; fi
    rm -rf "$D"; mkdir -p "$D"
    python3 -c "
import json
p = json.load(open('$ROOT/data/artefacts/PHerc0358/seed.json'))
p['thread_limit'] = $TL
json.dump(p, open('$D/seed.json','w'), indent=2)"
    ( cd "$D" && timeout 900 vc_grow_seg_from_seed -v "$S" -t . -p seed.json -s $GRAINE > trace.log 2>&1 )
    RC=$?
    SURF=$(ls -d "$D"/auto_grown_* 2>/dev/null | head -1)
    AIRE=$(grep -oE 'generated surface [0-9.]+ vx\^2 \([0-9.]+ cm\^2\)' "$D/trace.log" | grep -oE '\([0-9.]+' | tr -d '(' | tail -1)
    GEN=$(grep -c '^gen ' "$D/trace.log")
    CROIS=""
    if [ -n "$SURF" ]; then
      vc_tifxyz_selfcross --surface "$SURF" -o "$D/selfcross.json" > /dev/null 2>&1
      # ⚠ Refus (code 3) si aucune paire n'a ete testee — voir docs/34.
      CROIS=$(python3 "$ROOT/src/nappe/lire_selfcross.py" "$D/selfcross.json" 2>/dev/null)
    fi
    if [ "$RC" -eq 124 ]; then STATUT=timeout
    elif [ -z "$SURF" ] || [ -z "${AIRE:-}" ]; then STATUT=sans_maillage
    else STATUT=ok; fi
    python3 -c "
import json
ok = '$STATUT' == 'ok'
json.dump({'thread_limit': $TL, 'repetition': $R, 'statut': '$STATUT',
           'generations': $GEN,
           'aire_cm2': (${AIRE:-0} or 0) if ok else None,
           'transverse': (${CROIS:-0} or 0) if ok else None},
          open('$D/resume.json','w'), indent=2)"
    printf 'thread_limit=%s essai %s  %s  gen=%s  aire=%s  croisements=%s\n' \
      "$TL" "$R" "$STATUT" "$GEN" "${AIRE:-?}" "${CROIS:-?}"
  done
done
echo "fini — $DEST"
