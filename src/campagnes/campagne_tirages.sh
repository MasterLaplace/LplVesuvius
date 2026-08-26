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
# ⚠ Les graines viennent de `docs/mesures/table_graines.json` (versionne), critere « planarite »
# -- le seul qui ait replique (10 fois sur 12, p = 0,0386). Le volume et la taille de
# voxel sont RELUS sur S3 et CONFRONTES a la table : un desaccord arrete le rouleau au
# lieu de tracer a la mauvaise echelle. Sans `voxelsize` juste, l'aire sort nulle et
# `vc_grow_seg_from_seed` rejette toute surface en accusant la surface.
#
# ⚠ Reprenable au tirage pres : un tirage qui a deja son `resume.json` est saute.
#
# ⭐ `GENERATIONS` releve le plafond de generations du seed.json (defaut : celui du
# fichier). C'est la mesure que `29` N3 nomme : les rouleaux a faible dispersion d'aire
# sont ceux dont les six tirages BUTENT sur ce plafond (118 sur 118), donc dont la trace
# sature -- et une dispersion mesuree sous une troncature commune ne mesure pas la
# dispersion du traceur, elle mesure la troncature. Relever le plafond et rejouer tranche.
# ⚠ Un run a plafond releve doit avoir sa PROPRE destination : ses aires ne sont pas
# comparables a celles du plafond d'origine, et les melanger dans un meme dossier ferait
# un tableau dont les lignes ne parlent pas de la meme chose.
#
#   ./src/campagnes/campagne_tirages.sh [dest] [repetitions] [rouleaux...]
#   GENERATIONS=400 ./src/campagnes/campagne_tirages.sh data/tirages_plafond 6 PHerc0125
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/tirages}
REPETITIONS=${2:-6}
GENERATIONS=${GENERATIONS:-}
shift 2 2>/dev/null || true
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
mkdir -p "$DEST"

if [ "$#" -gt 0 ]; then
  ROULEAUX="$*"
else
  ROULEAUX=$(python3 -c "
import json
d = json.load(open('$ROOT/docs/mesures/table_graines.json'))
print(' '.join(l['rouleau'] for l in d['lignes'] if l.get('planarite')))")
fi

lister() { curl -s --max-time 60 "$B/?list-type=2&prefix=$1&delimiter=/" \
           | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep -vxF "$1"; }

for R in $ROULEAUX; do
  echo "== $R"
  read -r X Y Z UM_TABLE <<<"$(python3 -c "
import json, sys
d = json.load(open('$ROOT/docs/mesures/table_graines.json'))
for l in d['lignes']:
    if l['rouleau'] == '$R' and l.get('planarite'):
        p = l['planarite']
        print(p['x'], p['y'], p['z'], l['voxel_um']); break
else:
    sys.exit(1)")" || { echo "   ⚠ pas de graine planarite dans la table — rouleau saute"; continue; }

  # ⚠⚠ Surface et volume sont apparies par IDENTITE DE SCAN, pas par position dans deux
  # listages -- meme correctif que `campagne_graines.sh`, et pour la meme raison : `head -1`
  # de chaque liste n'est le meme scan que si les deux se trient pareil, ce que rien ne
  # garantit des qu'un rouleau a plusieurs scans (PHerc0139, PHerc1203).
  #
  # ⭐ Ici la resolution cible n'a meme pas a etre declaree : c'est celle de la TABLE, donc
  # celle a laquelle la graine a ete trouvee. Le scan choisi est par construction celui
  # auquel cette graine se rapporte, et un rouleau qui n'aurait pas de scan a cette
  # resolution est arrete au lieu d'etre trace a une autre echelle.
  if ! PAIRE=$(python3 "$ROOT/src/volume/apparier_volumes.py" "$R" --pour-campagne \
                 --voxel-um "$UM_TABLE" 2>"$DEST/$R.appariement.log"); then
    echo "   ⚠ appariement refuse : $(cat "$DEST/$R.appariement.log")"; continue
  fi
  read -r SURF VOL UM <<<"$PAIRE"
  if [ -z "$SURF" ] || [ -z "$VOL" ] || [ -z "$UM" ]; then
    echo "   ⚠ pas de prediction ou pas de volume"; continue
  fi
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
    if [ -n "$GENERATIONS" ]; then
      sed -i "s/\"generations\": [0-9]*/\"generations\": $GENERATIONS/" "$D/seed.json"
    fi
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
      CROIS=$(python3 "$ROOT/src/nappe/lire_selfcross.py" "$D/selfcross.json" 2>/dev/null)
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
           'plafond_generations': json.load(open('$D/seed.json'))['generations'],
           'aire_cm2': (${AIRE:-0} or 0) if ok else None,
           'transverse': (${CROIS:-0} or 0) if ok else None},
          open('$D/resume.json', 'w'), indent=2)"
    printf '   r%-2s %-13s gen=%-4s aire=%-11s croisements=%s\n' \
      "$I" "$STATUT" "$GEN" "${AIRE:-?}" "${CROIS:-?}"
  done
done
echo "campagne finie — $DEST"
