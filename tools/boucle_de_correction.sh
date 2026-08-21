#!/bin/bash
# LA BOUCLE ENTIERE : tracer -> juger -> dire ou la surface aurait du passer -> re-pousser.
#
# ⚠⚠ C'est le chainon que `39` a nomme et que `41` a construit, mis bout a bout pour la
# premiere fois. Chaque maillon existait separement ; ce script est le seul endroit ou la
# sortie de l'un entre dans l'entree du suivant, donc le seul endroit ou un desaccord de
# convention (ordre des axes, coordonnees relatives au bloc) peut se voir.
#
# ⭐ Conception APPARIEE : la trace corrigee et la trace temoin partagent graine, volume,
# parametres et nombre de generations. Une seule chose differe -- les points de passage.
# Sans cet appariement, un changement de convergence pourrait venir du reglage.
#
# ⚠ `--rewind-gen` demande de choisir une generation, et `39` le notait comme une deuxieme
# piece manquante : notre test de convergence juge une trace ENTIERE, pas une generation.
# On balaie donc quelques valeurs plutot que d'en deviner une -- une trace de ce rouleau
# coute une vingtaine de secondes, le balayage est moins cher que le raisonnement.
#
#   ./tools/lancer.sh --fond tools/boucle_de_correction.sh [dest]
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/boucle}
ROULEAU=PHerc0358
UM=9.362
GENERATIONS=${GENERATIONS:-120}
REWINDS=${REWINDS:-"5 40"}
# ⚠⚠ POURQUOI UN BALAYAGE DE POIDS, mesure a l'appui (`42`) : 318 points de passage contre
# 56 630 points de grille, soit 0,56 % de la surface, avec un `correction_weight` qui vaut
# 1,0 par defaut -- le meme ordre que `DIST`, qui s'applique partout. Une correction a ce
# poids est un coup de pouce local, pas une reorientation. La cle existe
# (`GrowPatch.cpp:1311`, `applyJsonWeights`) et n'avait jamais ete reglee ici.
POIDS=${POIDS:-"1 100"}
# ⚠⚠ DEUX SEMIS DE POINTS, et c'est la seconde reponse au diagnostic de `42`. Un seul fil
# de 318 points pese 0,56 % des 56 630 points de grille d'une trace ; le mode `nappe` de
# `suivre_nappe.py` (une echine et ses cotes) en produit **5707** sur le meme rouleau,
# soit ~10 %. Un solveur a qui l'on donne un fil doit deviner la surface autour ; a qui
# l'on donne un morceau de nappe, beaucoup moins.
SEMIS=${SEMIS:-"ligne nappe"}
RAYON=${RAYON:-128}
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250821151737-9.362um-1.2m-113keV-masked.zarr"
SURF=$(curl -s --max-time 60 "$B/?list-type=2&prefix=$ROULEAU/representations/predictions/surfaces/&delimiter=/" \
       | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$' | head -1 | sed 's|/$||')
[ -z "$SURF" ] && { echo "pas de prediction publiee pour $ROULEAU" >&2; exit 3; }
GRAINE=$(python3 -c "
import json,glob
for f in sorted(glob.glob('$ROOT/data/trace/$ROULEAU/essai_*/auto_grown_*/meta.json')):
    d=json.load(open(f)); o=d.get('seed') or d.get('origin')
    if o: print(' '.join(str(int(v)) for v in o)); break")
[ -z "$GRAINE" ] && { echo "graine introuvable" >&2; exit 3; }
set -- $GRAINE; GX=$1; GY=$2; GZ=$3
echo "graine : $GX $GY $GZ   prediction : $SURF"
mkdir -p "$DEST"

# --- 1. la trace temoin, sans aucune correction -------------------------------
T="$DEST/temoin"
if [ ! -d "$T/trace" ]; then
  mkdir -p "$T/trace"
  python3 -c "
import json
p = json.load(open('$ROOT/artefacts/$ROULEAU/seed.json'))
p.update({'generations': $GENERATIONS, 'thread_limit': 1, 'voxelsize': $UM})
json.dump(p, open('$T/trace/seed.json','w'), indent=2)"
  ( cd "$T/trace" && timeout 7200 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
      -s $GX $GY $GZ > trace.log 2>&1 )
fi
MT=$(ls -d "$T/trace"/auto_grown_* 2>/dev/null | head -1)
[ -z "$MT" ] && { echo "la trace temoin n'a rien produit — la boucle ne dit RIEN" >&2; exit 4; }

# --- 2. les points de passage, calcules depuis la PREDICTION -------------------
# ⚠ Pas depuis la trace : `38` etablit qu'elle est posee en travers, donc l'ecart a la
# feuille n'y existe pas. Le chemin est calcule independamment d'elle.
declare -A FICHIER_PTS
for SEM in $SEMIS; do
  case "$SEM" in
    ligne) PTS="$DEST/correction.json"; SUP_MARCHE="--deux-sens" ;;
    nappe) PTS="$DEST/nappe.json";      SUP_MARCHE="--nappe --ecart-cotes 6 --n-cotes 24" ;;
    *) echo "semis inconnu : $SEM" >&2; exit 3 ;;
  esac
  if [ ! -s "$PTS" ]; then
    ( cd "$ROOT/experiments" && uv run python ../analysis/src/suivre_nappe.py \
        --zarr "$SURF" --xyz $GX $GY $GZ --rayon "$RAYON" --n-pas 800 --distance \
        $SUP_MARCHE --sortie "$PTS" --json "$DEST/marche_$SEM.json" ) \
        > "$DEST/marche_$SEM.log" 2>&1
  fi
  if [ ! -s "$PTS" ]; then
    echo "semis $SEM : aucun point de passage — voir $DEST/marche_$SEM.log" >&2
    sed 's/^/   /' "$DEST/marche_$SEM.log" | tail -5 >&2
    continue
  fi
  FICHIER_PTS[$SEM]=$PTS
  N_PTS=$(python3 -c "
import json; d=json.load(open('$PTS'))
print(sum(len(c['points']) for c in d['collections'].values()), len(d['collections']))")
  echo "semis $SEM : $N_PTS (points, collections)"
done
[ ${#FICHIER_PTS[@]} -eq 0 ] && { echo "aucun semis utilisable" >&2; exit 4; }

# --- 3. juger : le temoin, puis chaque reprise corrigee ------------------------
juger() {   # $1 = repertoire de travail, $2 = maillage, $3 = nom
  local W=$1 M=$2 NOM=$3
  [ -s "$W/selfcross.json" ] || vc_tifxyz_selfcross --surface "$M" -o "$W/selfcross.json" > /dev/null 2>&1
  local CROIS AIRE SERIE
  CROIS=$(python3 "$ROOT/analysis/src/lire_selfcross.py" "$W/selfcross.json" 2>/dev/null || echo "?")
  AIRE=$(grep -oE 'generated surface [0-9.]+ vx\^2 \([0-9.]+ cm\^2\)' "$W/trace.log" 2>/dev/null \
         | grep -oE '\([0-9.]+' | tr -d '(' | tail -1)
  [ -d "$W/plat" ] || vc_flatten -i "$M" -o "$W/plat" > "$W/flatten.log" 2>&1
  [ -d "$W/plat" ] || { echo "== $NOM : ${AIRE:-?} cm², $CROIS croisements — vc_flatten a échoué"; return; }
  SERIE=""
  for N in 41 161; do
    local OUT="$W/profil_${N}c.json"
    if [ ! -s "$OUT" ]; then
      rm -rf "$W/rendu_$N"
      vc_render_tifxyz -v "$W/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$W/plat" \
          --tif-output "$W/rendu_$N" -n "$N" --slice-step 1 --auto-crop \
          > "$W/rendu_$N.log" 2>&1 || continue
      ( cd "$ROOT/inference_xpu" && uv run python ../analysis/src/depth_profile.py \
          "$W/rendu_$N" --grid --step 400 --traced-layer $((N / 2)) --voxel-um "$UM" \
          --out "$OUT" ) > "$W/profil_$N.log" 2>&1 || continue
    fi
    local E_UM
    E_UM=$(python3 -c "
import json; d=json.load(open('$OUT')); d=d[0] if isinstance(d,list) else d
print(f\"{d['ecart_trace_um_median']:.2f}\")" 2>/dev/null) || continue
    SERIE="$SERIE$N:$E_UM,"
  done
  rm -rf "$W/cache"
  [ -z "$SERIE" ] && { echo "== $NOM : ${AIRE:-?} cm², $CROIS croisements — aucun profil"; return; }
  echo "== $NOM  (${AIRE:-?} cm², $CROIS auto-intersections)"
  ( cd "$ROOT/experiments" && uv run python ../analysis/src/test_convergence.py \
      --serie "${SERIE%,}" --nom "$NOM (${AIRE:-?} cm², $CROIS croisements)" \
      --json "$ROOT/docs/boucle_$NOM.json" | tail -3 )
}

cp -n "$T/trace/trace.log" "$T/trace.log" 2>/dev/null || true
juger "$T" "$MT" "temoin"

for SEM in "${!FICHIER_PTS[@]}"; do
 PTS=${FICHIER_PTS[$SEM]}
 for G in $REWINDS; do
 for P in $POIDS; do
  # ⚠ Le nom porte les DEUX variables. Une premiere version nommait par la generation
  # seule : deux poids differents auraient ecrit dans le meme repertoire, et le second
  # aurait trouve la trace du premier deja la et ne l'aurait jamais refaite -- un balayage
  # qui rend deux fois le meme resultat en ayant l'air d'avoir teste deux reglages.
  # ⚠ Le nom porte les TROIS variables. Les runs deja faits en mode ligne a poids 1
  # gardent leur ancien nom, pour ne pas etre refaits pour rien.
  if [ "$SEM" = "ligne" ] && [ "$P" = "1" ]; then NOM="corrige_gen$G"
  elif [ "$SEM" = "ligne" ]; then NOM="corrige_gen${G}_poids$P"
  else NOM="corrige_${SEM}_gen${G}_poids$P"; fi
  W="$DEST/$NOM"
  if [ ! -d "$W/trace" ]; then
    mkdir -p "$W/trace"
    python3 -c "
import json
p = json.load(open('$T/trace/seed.json'))
if $P != 1: p['correction_weight'] = float($P)
json.dump(p, open('$W/trace/seed.json','w'), indent=2)"
    ( cd "$W/trace" && timeout 7200 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
        -s $GX $GY $GZ --resume "$MT" --rewind-gen "$G" --correct "$PTS" \
        > trace.log 2>&1 )
  fi
  M=$(ls -d "$W/trace"/auto_grown_* 2>/dev/null | head -1)
  if [ -z "$M" ]; then
    # ⚠ Un echec ici est un RESULTAT sur le seam, pas une panne du script : il veut dire
    # que la reprise corrigee ne produit rien, et c'est ce qu'il faut savoir.
    echo "== $NOM : AUCUN MAILLAGE — la reprise corrigée ne produit rien"
    sed 's/^/   /' "$W/trace/trace.log" | tail -4
    continue
  fi
  cp -n "$W/trace/trace.log" "$W/trace.log" 2>/dev/null || true
  juger "$W" "$M" "$NOM"
 done
 done
done
