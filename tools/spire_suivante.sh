#!/bin/bash
# ENCHAINER LES SPIRES : partir d'une surface qui CONVERGE, et generer sa voisine.
#
# ⚠⚠ CE QUE CE SCRIPT CHANGE DE STRATEGIE, et pourquoi. `42` etablit un plateau : le seam
# de correction, a tous les reglages essayes (deux rembobinages, deux poids, deux semis),
# ne transforme pas une coupe radiale en suiveuse de feuille. Le meilleur alpha obtenu est
# +0,89 quand le segment officiel est a +0,00. On arretait donc d'essayer de REDRESSER une
# trace mal orientee.
#
# ⭐⭐⭐ `vc_grow_seg_from_seed` a un mode que ce depot n'avait jamais lance :
# `mode: "gen_neighbor"`. Lu dans la source (`apps/src/vc_grow_seg_from_seed.cpp:625`), il
# prend une surface par `--resume`, tire un rayon depuis chaque sommet le long de la
# normale (`neighbor_dir` = "in" ou "out"), avance par pas de `neighbor_step` voxels, et
# s'arrete des qu'il touche de la matiere au-dessus de `neighbor_threshold`. Autrement dit
# il CONSTRUIT LA SPIRE VOISINE. C'est le « wrap by wrap copy tool » que le papier decrit,
# et il est public.
#
# ⭐ Et il n'a pas besoin d'etre redresse : on part d'un segment OFFICIEL dont la
# convergence est deja mesuree (alpha = +0,00 sur PHerc1447). La question devient donc
# celle du graal : **la convergence SURVIT-elle a l'enchainement, et sur combien de spires ?**
#
# ⚠ Conception : toutes les spires sont jugees dans les MEMES fenetres (31 et 81), celles
# ou l'officiel a ete mesure. Melanger les fenetres melangerait le reglage et la surface --
# c'est l'erreur que `38` a payee trois fois.
#
# ⚠ Un echec a une spire est un RESULTAT (« la chaine casse au tour k »), pas une panne du
# script : il est rapporte et la boucle s'arrete la, parce qu'on ne peut pas generer la
# voisine d'une surface qui n'existe pas.
#
#   ./tools/lancer.sh --fond tools/spire_suivante.sh [dest] [nombre de spires]
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/spires}
N_SPIRES=${2:-4}
ROULEAU=PHerc1447
UM=8.64
SENS=${SENS:-out}
FENETRES=${FENETRES:-"31 81"}
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr"
SOURCE=${SOURCE:-$ROOT/data/trace/$ROULEAU\_officiel/mesh.tifxyz}
[ -d "$SOURCE" ] || { echo "surface de depart absente : $SOURCE" >&2; exit 3; }
SURF=$(curl -s --max-time 60 "$B/?list-type=2&prefix=$ROULEAU/representations/predictions/surfaces/&delimiter=/" \
       | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$' | head -1 | sed 's|/$||')
[ -z "$SURF" ] && { echo "pas de prediction publiee pour $ROULEAU" >&2; exit 3; }
mkdir -p "$DEST"
echo "depart : $SOURCE"
echo "prediction : $SURF   sens : $SENS   fenetres : $FENETRES"

juger() {   # $1 = repertoire, $2 = maillage, $3 = nom
  local W=$1 M=$2 NOM=$3
  [ -s "$W/selfcross.json" ] || vc_tifxyz_selfcross --surface "$M" -o "$W/selfcross.json" > /dev/null 2>&1
  local CROIS SERIE AIRE
  CROIS=$(python3 "$ROOT/analysis/src/lire_selfcross.py" "$W/selfcross.json" 2>/dev/null || echo "?")
  AIRE=$(python3 -c "
import json;print(f\"{json.load(open('$M/meta.json'))['area_cm2']:.2f}\")" 2>/dev/null || echo "?")
  [ -d "$W/plat" ] || vc_flatten -i "$M" -o "$W/plat" > "$W/flatten.log" 2>&1
  [ -d "$W/plat" ] || { echo "== $NOM : $AIRE cm², $CROIS croisements — vc_flatten a échoué"; return 1; }
  SERIE=""
  for N in $FENETRES; do
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
  [ -z "$SERIE" ] && { echo "== $NOM : $AIRE cm², $CROIS croisements — aucun profil"; return 1; }
  echo "== $NOM  ($AIRE cm², $CROIS auto-intersections)"
  ( cd "$ROOT/experiments" && uv run python ../analysis/src/test_convergence.py \
      --serie "${SERIE%,}" --nom "$NOM ($AIRE cm², $CROIS croisements)" \
      --json "$ROOT/docs/spire_$NOM.json" | tail -3 )
}

# --- spire 0 : la surface de depart, jugee par NOTRE chaine ---------------------
# ⚠ On la rejuge ici plutot que de reprendre le chiffre de `38` : la comparaison doit
# passer par la meme chaine que les spires generees, sinon un ecart entre la spire 0 et la
# spire 1 melangerait la surface et le chemin de mesure.
W0="$DEST/spire00"
mkdir -p "$W0"
juger "$W0" "$SOURCE" "spire00" || { echo "la surface de depart ne se juge pas — la chaine ne dit RIEN" >&2; exit 4; }

PREC=$SOURCE
for k in $(seq 1 "$N_SPIRES"); do
  KK=$(printf '%02d' "$k")
  W="$DEST/spire$KK"
  if [ ! -d "$W/trace" ]; then
    mkdir -p "$W/trace"
    python3 -c "
import json
json.dump({'mode': 'gen_neighbor', 'voxelsize': $UM, 'thread_limit': 0,
           'cache_size': 6000000000,
           'neighbor_dir': '$SENS', 'neighbor_step': 1.0,
           'neighbor_max_distance': 250.0, 'neighbor_threshold': 1.0,
           'neighbor_fill': True},
          open('$W/trace/seed.json','w'), indent=2)"
    ( cd "$W/trace" && timeout 7200 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
        --resume "$PREC" > trace.log 2>&1 )
  fi
  M=$(ls -d "$W/trace"/auto_grown_* 2>/dev/null | head -1)
  [ -z "$M" ] && M=$(ls -d "$W/trace"/*.tifxyz 2>/dev/null | head -1)
  if [ -z "$M" ]; then
    echo "== spire$KK : AUCUN MAILLAGE — la chaîne casse au tour $k"
    sed 's/^/   /' "$W/trace/trace.log" | tail -6
    break
  fi
  juger "$W" "$M" "spire$KK" || break
  PREC=$M
done
echo "fin — $(ls -d "$DEST"/spire* 2>/dev/null | wc -l) spire(s) traitée(s)"
