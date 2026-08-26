#!/bin/bash
# Un maillage grossier VOIT-IL les auto-intersections qu'il traverse ?
#
# ⚠⚠ Pourquoi cette mesure existe. `26` §9 conclut que `step_size >= 20` rend une trace
# propre, sur la foi de comptes nuls. En auditant les rapports bruts de cette campagne,
# une asymetrie apparait : `vc_tifxyz_selfcross` teste 348 millions de paires de quads a
# pas 5, et 36 149 a pas 40. « Zero croisement » pourrait donc dire deux choses : la trace
# est propre, ou le detecteur ne voit plus.
#
# ⭐ Le protocole les separe. On prend une surface dont on SAIT qu'elle se croise -- le
# maillage condamne de `24`, 240 auto-intersections, archive dans l'arbre -- et on degrade
# sa DESCRIPTION sans toucher a sa GEOMETRIE, en ne gardant qu'une ligne et une colonne
# sur k. Tout changement de verdict vient alors du maillage seul.
#
# ⚠ Chaque degradation est lue DEUX fois : au reglage par defaut (`--maxedge 60`) et
# filtre DESACTIVE (`--maxedge 0`). Sans les deux, on ne saurait pas si un zero vient de
# la grossierete du maillage ou du filtre qui jette les quads devenus longs -- deux causes
# tres differentes, et une seule des deux est reparable par un reglage.
#
#   ./src/outils/sensibilite_maillage.sh [dest] [maillage] [facteurs...]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/sensibilite_maillage}
MESH=${2:-$ROOT/data/artefacts/PHerc0358/mesh.tifxyz}
shift 2 2>/dev/null || true
FACTEURS=${*:-"1 2 3 4"}
mkdir -p "$DEST"

PAS=$(python3 -c "
import json; print(json.load(open('$MESH/meta.json'))['vc_gsfs_params']['step_size'])" 2>/dev/null || echo 20)
echo "maillage : $MESH  (step_size $PAS)"

LIGNES=""
for K in $FACTEURS; do
  if [ "$K" -eq 1 ]; then
    M=$MESH
  else
    M="$DEST/decime_k$K"
    if [ ! -f "$M/meta.json" ]; then
      ( cd "$ROOT" && uv run python src/nappe/decimer_tifxyz.py \
          "$MESH" "$M" --facteur "$K" ) > "$DEST/decime_k$K.log" 2>&1 \
        || { echo "  ⚠ décimation k=$K échouée"; continue; }
    fi
  fi
  for MODE in defaut brut; do
    [ "$MODE" = defaut ] && E=60 || E=0
    F="$DEST/k${K}_${MODE}.json"
    [ -s "$F" ] || vc_tifxyz_selfcross --surface "$M" --maxedge "$E" -o "$F" \
        > "$DEST/k${K}_${MODE}.log" 2>&1
  done
  # ⚠ Ce script LIT le rapport en direct au lieu de passer par
  # `src/nappe/lire_selfcross.py`, et c'est deliberate : ce lecteur REFUSE un rapport
  # sans paire testee, or le cas « zero paire testee » est precisement le SUJET de cette
  # mesure. Un instrument qui refuse de lire ce qu'il doit mesurer ne mesure rien.
  L=$(python3 -c "
import json
def lis(p):
    d = json.load(open(p))
    return (sum(c['pairs_tested'] for c in d['census']),
            sum(c['quads_dropped_for_edge_length'] for c in d['census']),
            sum(c['transverse'] for c in d['census']),
            bool(d['clean_of_transverse_self_intersection']))
pd_, qd, td, cd = lis('$DEST/k${K}_defaut.json')
pb, qb, tb, cb = lis('$DEST/k${K}_brut.json')
print(json.dumps({'facteur': $K, 'pas_equivalent': $PAS * $K,
                  'defaut': {'paires': pd_, 'jetes': qd, 'transverse': td, 'declare_propre': cd},
                  'brut':   {'paires': pb, 'jetes': qb, 'transverse': tb, 'declare_propre': cb}}))")
  LIGNES="$LIGNES$L,"
  printf 'k=%-2s pas≈%-4s  défaut: %7s croisements (%10s paires)   brut: %7s croisements (%10s paires)\n' \
    "$K" "$(python3 -c "print(int($PAS*$K))")" \
    "$(python3 -c "import json;print(json.loads('''$L''')['defaut']['transverse'])")" \
    "$(python3 -c "import json;print(json.loads('''$L''')['defaut']['paires'])")" \
    "$(python3 -c "import json;print(json.loads('''$L''')['brut']['transverse'])")" \
    "$(python3 -c "import json;print(json.loads('''$L''')['brut']['paires'])")"
done
python3 -c "
import json
lignes = json.loads('[' + '''${LIGNES%,}''' + ']')
json.dump({'maillage': '$MESH', 'step_size': $PAS, 'lignes': lignes},
          open('$ROOT/docs/mesures/sensibilite_maillage.json', 'w'), indent=2)
print('écrit : docs/mesures/sensibilite_maillage.json')"
