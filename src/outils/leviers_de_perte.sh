#!/bin/bash
# Les termes de perte que nos traces N'ONT JAMAIS ACTIVES.
#
# ⚠⚠ CE QUE LA LECTURE DE LA SOURCE ETABLIT, et qui rend cette campagne obligatoire.
# `vc_grow_seg_from_seed` n'est pas une propagation : c'est un moindres carres Ceres avec
# DOUZE familles de residus (`GrowPatch.cpp:1244`). Leurs poids par defaut :
#
#     SNAP 0,1   NORMAL 10   DIST 1   STRAIGHT 0,2   DIRECTION 1   SDIR 1   CORRECTION 1
#     NORMAL3DLINE 0   REFERENCE_RAY 0   SURFACE_SDT 0   SPACELINE 0   PATCH_NORMAL 0
#
# ⚠ NORMAL et SNAP passent par `NormalConstraintPlane`, et `GrowPatch.cpp:2050` sort
# immediatement sans `ngv` NI `patch_normals` : sans grille de normales, ces deux poids ne
# s'appliquent a RIEN. DIRECTION exige des `direction_fields`. Donc pour un run qui ne
# fournit ni l'un ni l'autre -- le cas de tous nos essais de base -- les seuls termes
# actifs sont DIST et STRAIGHT, c'est-a-dire de la GEOMETRIE PURE.
#
# ⭐⭐ Deux leviers n'ont JAMAIS ete essayes dans ce depot (verifie sur les 17 seed.json
# de `data/trace/PHerc0358/essai_*`) :
#   1. `sdt_weight` -- le terme de distance signee a la surface. Le tracer calcule bien un
#      SDT (`get_or_compute_sdt_chunk` : negatif dans la matiere, donc l'axe median est un
#      MINIMUM), mais son poids vaut ZERO par defaut, donc il ne tire rien ;
#   2. les fibres HORIZONTALES ET VERTICALES ENSEMBLE. `FiberDirectionLoss` demande que
#      l'axe u de la grille suive les horizontales et l'axe v les verticales -- c'est le
#      papyrus qui fournit son propre systeme de coordonnees. Nos essais ont teste
#      `normal` seul, `horizontal` seul, `vertical` seul, jamais la PAIRE.
#
# ⚠ Conception appariee : toutes les variantes partagent graine, rouleau, volume et
# generations. Une seule cle change a la fois, sinon on ne saurait pas laquelle a agi.
#
#   ./src/outils/lancer.sh --fond src/outils/leviers_de_perte.sh [dest]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/leviers}
ROULEAU=PHerc0358
UM=9.362
GENERATIONS=${GENERATIONS:-120}
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250821151737-9.362um-1.2m-113keV-masked.zarr"
SURF=$(curl -s --max-time 60 "$B/?list-type=2&prefix=$ROULEAU/representations/predictions/surfaces/&delimiter=/" \
       | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$' | head -1 | sed 's|/$||')
[ -z "$SURF" ] && { echo "pas de prediction publiee pour $ROULEAU" >&2; exit 3; }

# ⚠ La graine est celle de tous les essais de `26` : la reutiliser est ce qui rend cette
# campagne comparable a eux. En prendre une autre transformerait une comparaison de
# reglages en comparaison d'endroits.
GRAINE=$(python3 -c "
import json,glob,sys
for f in sorted(glob.glob('$ROOT/data/trace/$ROULEAU/essai_*/auto_grown_*/meta.json')):
    d=json.load(open(f))
    o=d.get('seed') or d.get('origin')
    if o: print(' '.join(str(int(v)) for v in o)); break
" 2>/dev/null)
[ -z "$GRAINE" ] && GRAINE=$(grep -hoE 'origin [0-9]+ [0-9]+ [0-9]+' "$ROOT/data/trace/$ROULEAU"/essai_*/trace.log 2>/dev/null | head -1 | sed 's/origin //')
[ -z "$GRAINE" ] && { echo "graine introuvable — voir data/trace/$ROULEAU/essai_*/" >&2; exit 3; }
echo "graine : $GRAINE   prediction : $SURF"

mkdir -p "$DEST"
# nom : cles JSON supplementaires (JSON valide, fusionne dans seed.json)
VARIANTES=(
  "temoin:{}"
  "sdt1:{\"sdt_weight\": 1.0}"
  "sdt10:{\"sdt_weight\": 10.0}"
  "fibres_hv:{\"direction_fields\": [{\"zarr\": \"$ROOT/data/champ_PHerc0358\", \"dir\": \"horizontal\", \"scale\": 2.0}, {\"zarr\": \"$ROOT/data/champ_PHerc0358\", \"dir\": \"vertical\", \"scale\": 2.0}]}"
  "sdt10_fibres_hv:{\"sdt_weight\": 10.0, \"direction_fields\": [{\"zarr\": \"$ROOT/data/champ_PHerc0358\", \"dir\": \"horizontal\", \"scale\": 2.0}, {\"zarr\": \"$ROOT/data/champ_PHerc0358\", \"dir\": \"vertical\", \"scale\": 2.0}]}"
)

for V in "${VARIANTES[@]}"; do
  NOM=${V%%:*}; SUP=${V#*:}
  W="$DEST/$NOM"; mkdir -p "$W"
  if [ ! -d "$W/trace" ]; then
    mkdir -p "$W/trace"
    python3 -c "
import json
p = json.load(open('$ROOT/data/artefacts/$ROULEAU/seed.json'))
p.update({'generations': $GENERATIONS, 'thread_limit': 1, 'voxelsize': $UM})
p.update(json.loads('''$SUP'''))
json.dump(p, open('$W/trace/seed.json', 'w'), indent=2)"
    ( cd "$W/trace" && timeout 7200 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
        -s $GRAINE > trace.log 2>&1 )
  fi
  M=$(ls -d "$W/trace"/auto_grown_* 2>/dev/null | head -1)
  if [ -z "$M" ]; then
    # ⚠ « aucun maillage » est un RESULTAT, pas une panne du script : un reglage peut
    # etouffer la croissance. Il doit apparaitre dans le tableau, pas disparaitre.
    echo "== $NOM : AUCUN MAILLAGE (le reglage empeche la croissance)"
    continue
  fi
  AIRE=$(grep -oE 'generated surface [0-9.]+ vx\^2 \([0-9.]+ cm\^2\)' "$W/trace/trace.log" \
         | grep -oE '\([0-9.]+' | tr -d '(' | tail -1)
  [ -s "$W/selfcross.json" ] || vc_tifxyz_selfcross --surface "$M" -o "$W/selfcross.json" > /dev/null 2>&1
  CROIS=$(python3 "$ROOT/src/nappe/lire_selfcross.py" "$W/selfcross.json" 2>/dev/null || echo "?")
  [ -d "$W/plat" ] || vc_flatten -i "$M" -o "$W/plat" > "$W/flatten.log" 2>&1
  [ -d "$W/plat" ] || { echo "== $NOM : ${AIRE:-?} cm², $CROIS croisements — vc_flatten a échoué"; continue; }
  SERIE=""
  for N in 41 161; do
    OUT="$W/profil_${N}c.json"
    if [ ! -s "$OUT" ]; then
      rm -rf "$W/rendu_$N"
      vc_render_tifxyz -v "$W/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$W/plat" \
          --tif-output "$W/rendu_$N" -n "$N" --slice-step 1 --auto-crop \
          > "$W/rendu_$N.log" 2>&1 || continue
      ( cd "$ROOT" && uv run python src/volume/depth_profile.py \
          "$W/rendu_$N" --grid --step 400 --traced-layer $((N / 2)) --voxel-um "$UM" \
          --out "$OUT" ) > "$W/profil_$N.log" 2>&1 || continue
    fi
    E_UM=$(python3 -c "
import json; d=json.load(open('$OUT')); d=d[0] if isinstance(d,list) else d
print(f\"{d['ecart_trace_um_median']:.2f}\")" 2>/dev/null) || continue
    SERIE="$SERIE$N:$E_UM,"
  done
  rm -rf "$W/cache"
  [ -z "$SERIE" ] && { echo "== $NOM : ${AIRE:-?} cm², $CROIS croisements — aucun profil"; continue; }
  echo "== $NOM  (${AIRE:-?} cm², $CROIS auto-intersections)"
  ( cd "$ROOT" && uv run python src/commun/test_convergence.py \
      --serie "${SERIE%,}" --nom "$NOM (${AIRE:-?} cm², $CROIS croisements)" \
      --json "$ROOT/docs/mesures/leviers_$NOM.json" | tail -3 )
done
