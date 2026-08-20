#!/bin/bash
# Le traceur est-il un tirage AILLEURS que sur la graine de `24` ?
#
# ⚠⚠ Pourquoi cette campagne existe. `30` a mesure que `vc_grow_seg_from_seed` rend un
# resultat different a chaque execution -- mais sur UNE graine, d'UN rouleau, en quatorze
# tirages. Le taux de mauvais tirages (~13 %) a un intervalle de confiance large, et rien
# ne dit qu'il vaut ailleurs. `29` M1bis le marque ⚠⚠. Cette campagne repond en repetant
# sur PLUSIEURS rouleaux.
#
# ⚠ La grandeur qui DISCRIMINE n'est pas le compte d'auto-intersections -- il peut valoir
# zero partout, et « zero mauvais tirage » ne se distingue alors pas de « le traceur est
# deterministe ici ». C'est l'ETENDUE DES AIRES qui separe les deux : elle est non nulle
# des que le tirage varie, meme quand tous les tirages sont propres. Les deux sont
# mesurees, et `table_tirages.py` refuse de conclure sur le taux seul.
#
# ⚠ Les graines viennent de `docs/table_graines.json` (versionne), critere « planarite »
# -- le seul qui ait replique (10 fois sur 12, p = 0,0386). Le volume et la taille de
# voxel sont RELUS sur S3 et CONFRONTES a la table : un desaccord arrete le rouleau au
# lieu de tracer a la mauvaise echelle. Sans `voxelsize` juste, l'aire sort nulle et
# `vc_grow_seg_from_seed` rejette toute surface en accusant la surface.
#
# ⚠ Reprenable au tirage pres : un tirage qui a deja son `resume.json` est saute.
#
#   ./tools/campagne_tirages.sh [dest] [repetitions] [rouleaux...]
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/tirages}
REPETITIONS=${2:-6}
shift 2 2>/dev/null || true
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
mkdir -p "$DEST"

if [ "$#" -gt 0 ]; then
  ROULEAUX="$*"
else
  ROULEAUX=$(python3 -c "
import json
d = json.load(open('$ROOT/docs/table_graines.json'))
print(' '.join(l['rouleau'] for l in d['lignes'] if l.get('planarite')))")
fi

lister() { curl -s --max-time 60 "$B/?list-type=2&prefix=$1&delimiter=/" \
           | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep -vxF "$1"; }

for R in $ROULEAUX; do
  echo "== $R"
  read -r X Y Z UM_TABLE <<<"$(python3 -c "
import json, sys
d = json.load(open('$ROOT/docs/table_graines.json'))
for l in d['lignes']:
    if l['rouleau'] == '$R' and l.get('planarite'):
        p = l['planarite']
        print(p['x'], p['y'], p['z'], l['voxel_um']); break
else:
    sys.exit(1)")" || { echo "   ⚠ pas de graine planarite dans la table — rouleau saute"; continue; }

  SURF=$(lister "$R/representations/predictions/surfaces/" | grep '\.zarr/$' | head -1 | sed 's|/$||')
  VOL=$(lister "$R/volumes/" | head -1 | sed 's|/$||')
  if [ -z "$SURF" ] || [ -z "$VOL" ]; then echo "   ⚠ pas de prediction ou pas de volume"; continue; fi
  UM=$(basename "$VOL" | grep -oE '[0-9]+\.[0-9]+um' | head -1 | sed 's/um$//')
  if [ -z "$UM" ]; then echo "   ⚠ taille de voxel illisible dans « $(basename "$VOL") » — rouleau saute"; continue; fi
  # Le desaccord ARRETE le rouleau : tracer a une echelle qui n'est pas celle de la table
  # rendrait des aires incomparables a tout ce que ce depot a deja mesure.
  #
  # ⚠⚠ La comparaison est NUMERIQUE, pas textuelle. La premiere version comparait les deux
  # chaines et a saute PHerc0268 et PHerc0800 en annoncant « 8.640 µm ≠ 8.64 µm » -- deux
  # ecritures du meme nombre. Une garde qui refuse pour une raison fausse est pire qu'une
  # garde absente : elle retire des donnees en ayant l'air de proteger.
  if ! python3 -c "
import sys
sys.exit(0 if abs(float('$UM') - float('$UM_TABLE')) < 1e-6 else 1)"; then
    echo "   ⚠ voxel S3 $UM µm ≠ table $UM_TABLE µm — rouleau sauté (aires incomparables)"; continue
  fi
  echo "   graine $X $Y $Z   voxel $UM µm"

  for I in $(seq 1 "$REPETITIONS"); do
    D="$DEST/$R/r$I"
    if [ -s "$D/resume.json" ]; then echo "   -- r$I deja fait"; continue; fi
    rm -rf "$D"; mkdir -p "$D"
    sed "s/\"voxelsize\": [0-9.]*/\"voxelsize\": $UM/" \
        "$ROOT/artefacts/PHerc0358/seed.json" > "$D/seed.json"
    ( cd "$D" && timeout 2400 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
        -s "$X" "$Y" "$Z" > trace.log 2>&1 )
    RC=$?
    SURFDIR=$(ls -d "$D"/auto_grown_* 2>/dev/null | head -1)
    AIRE=$(grep -oE 'generated surface [0-9.]+ vx\^2 \([0-9.]+ cm\^2\)' "$D/trace.log" \
           | grep -oE '\([0-9.]+' | tr -d '(' | tail -1)
    GEN=$(grep -c '^gen ' "$D/trace.log")
    CROIS=""
    if [ -n "$SURFDIR" ]; then
      vc_tifxyz_selfcross --surface "$SURFDIR" -o "$D/selfcross.json" > /dev/null 2>&1
      # ⚠ `lire_selfcross.py` REFUSE (code 3) un rapport ou aucune paire n'a ete testee :
      # l'outil declare alors « propre » sans avoir rien mesure. Voir docs/34.
      CROIS=$(python3 "$ROOT/analysis/src/lire_selfcross.py" "$D/selfcross.json" 2>/dev/null)
    fi
    if [ "$RC" -eq 124 ]; then STATUT=timeout
    elif [ -z "$SURFDIR" ] || [ -z "${AIRE:-}" ]; then STATUT=sans_maillage
    else STATUT=ok; fi
    python3 -c "
import json
ok = '$STATUT' == 'ok'
json.dump({'rouleau': '$R', 'repetition': $I, 'statut': '$STATUT',
           'graine': [$X, $Y, $Z], 'voxel_um': $UM, 'surface': '$SURF',
           'generations': $GEN,
           'aire_cm2': (${AIRE:-0} or 0) if ok else None,
           'transverse': (${CROIS:-0} or 0) if ok else None},
          open('$D/resume.json', 'w'), indent=2)"
    printf '   r%-2s %-13s gen=%-4s aire=%-11s croisements=%s\n' \
      "$I" "$STATUT" "$GEN" "${AIRE:-?}" "${CROIS:-?}"
  done
done
echo "campagne finie — $DEST"
