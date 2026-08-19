#!/bin/bash
# `step_size` est le SEUL parametre mesure qui deplace la trajectoire de croissance.
#
# ⚠⚠ Trois negatifs l'ont etabli (docs/26) : ni `direction_fields` (presence, orientation,
# semantique, intensite jusqu'a x100), ni les grilles de normales -- publiees ou generees
# depuis le volume, x17 de cout -- ne bougent la croissance d'un centieme. Le controle
# positif, lui, diverge des la generation 0 : c'est `step_size`.
#
# ⚠⚠ **On compare a SURFACE egale, pas a generations egales.** Une surface croit par un
# front, donc son aire va comme (k x pas)² : a 120 generations, un pas de 5 couvre SEIZE
# fois moins qu'un pas de 20. Comparer les comptes bruts ferait passer la lenteur pour de
# la qualite -- un petit morceau a moins d'occasions de se replier sur lui-meme. Le nombre
# de generations est donc mis a l'echelle en **1/pas**, et la grandeur lue reste le nombre
# d'auto-intersections **par cm²**, qui absorbe ce qu'il reste d'ecart.
#
# ⚠ Il n'existe PAS de cible d'aire : `target_area_vx2`, `target_area_cm` et `max_area_cm`
# sont ignores -- verifie, la trace depasse 2 cm² sans s'arreter. D'ou la mise a l'echelle.
#
# ⚠ Reprenable : un pas deja mesure est saute.
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/trace/PHerc0358/pas}
GRAINE=${2:-"5842 5839 7386"}
S="https://vesuvius-challenge-open-data.s3.amazonaws.com/PHerc0358/representations/predictions/surfaces/20250821151737-surface-20260413222639-surface-m7-L0-th0.2.zarr"
mkdir -p "$DEST"

for PAS in 5 10 15 20 30 40; do
  D="$DEST/pas_$PAS"
  if [ -s "$D/resume.json" ]; then
    echo "== pas $PAS deja fait"; continue
  fi
  rm -rf "$D"; mkdir -p "$D"
  GEN_CIBLE=$(python3 -c "print(max(20, round(120 * 20 / $PAS)))")
  python3 -c "
import json
p = json.load(open('$ROOT/artefacts/PHerc0358/seed.json'))
p['thread_limit'] = 1
p['step_size'] = float($PAS)
p['generations'] = $GEN_CIBLE
json.dump(p, open('$D/seed.json','w'), indent=2)"
  ( cd "$D" && timeout 3600 vc_grow_seg_from_seed -v "$S" -t . -p seed.json -s $GRAINE > trace.log 2>&1 )
  SURF=$(ls -d "$D"/auto_grown_* 2>/dev/null | head -1)
  AIRE=$(grep -oE 'generated surface [0-9.]+ vx\^2 \([0-9.]+ cm\^2\)' "$D/trace.log" | grep -oE '\([0-9.]+' | tr -d '(' | tail -1)
  GEN=$(grep -c '^gen ' "$D/trace.log")
  CROIS=""
  if [ -n "$SURF" ]; then
    vc_tifxyz_selfcross --surface "$SURF" -o "$D/selfcross.json" > /dev/null 2>&1
    CROIS=$(python3 -c "
import json; d=json.load(open('$D/selfcross.json'))
print(sum(c['transverse'] for c in d['census']))" 2>/dev/null)
  fi
  python3 -c "
import json
a = ${AIRE:-0} or 0
c = ${CROIS:-0} or 0
json.dump({'pas': $PAS, 'generations': $GEN, 'aire_cm2': a, 'transverse': c,
           'par_cm2': (c / a) if a else None},
          open('$D/resume.json','w'), indent=2)"
  printf 'pas %-3s  %3s gen  aire %8s cm²  croisements %-7s  par cm² %s\n' \
     "$PAS" "$GEN" "${AIRE:-?}" "${CROIS:-?}" \
     "$(python3 -c "print(f'{${CROIS:-0}/${AIRE:-1}:.1f}' if ${AIRE:-0} else '?')")"
done
echo "campagne des pas finie — $DEST"
