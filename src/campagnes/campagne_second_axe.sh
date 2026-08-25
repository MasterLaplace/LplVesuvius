#!/bin/bash
# SELECTIONNER SUR UN AXE, VALIDER SUR L'AUTRE — la parade a la malediction du vainqueur.
#
# ⚠⚠ Pourquoi cette campagne existe. `35` mesure que le traceur est un tirage : 4 rouleaux
# sur 12 rendent des verdicts opposes a parametres identiques. `31` §4 en tire une methode
# -- tirer N fois et selectionner -- et nomme aussitot son piege : prendre le minimum de N
# tirages avec un juge bruite fait remonter la CHANCE autant que la qualite. Le protocole
# honnete est de selectionner sur un axe et de valider sur l'autre.
#
# Cette campagne produit le SECOND axe pour des tirages deja juges sur le premier.
#
#   axe 1 (deja acquis) : `vc_tifxyz_selfcross` -- geometrie de la surface sur elle-meme ;
#   axe 2 (ici)         : la profondeur -- ou est la matiere par rapport a la trace, lue
#                         dans le VOLUME. Aucune information commune avec le premier.
#
# ⚠ La chaine est `vc_flatten` -> `vc_render_tifxyz` -> `depth_profile.py`. Elle demande le
# volume brut, lu en streaming depuis S3 : rien n'est telecharge en entier (`24`).
#
# ⚠ Reprenable au tirage pres. Un tirage sans maillage est saute et compte.
#
# ⚠⚠ Lancer par `src/outils/lancer.sh` : cette campagne dure des heures et editer son fichier
# pendant qu'elle tourne la tue (piege 45 du HANDOFF, paye trois fois le 2026-08-20).
#
#   ./src/outils/lancer.sh --fond src/campagnes/campagne_second_axe.sh [dest] [couches] [tirages...]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/second_axe}
COUCHES=${2:-21}
shift 2 2>/dev/null || true
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
mkdir -p "$DEST"

TIRAGES=${*:-$(ls -d "$ROOT"/data/tirages/*/r* 2>/dev/null)}

lister() { curl -s --max-time 60 "$B/?list-type=2&prefix=$1&delimiter=/" \
           | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep -vxF "$1"; }

declare -A VOLUME_DE UM_DE
for T in $TIRAGES; do
  R=$(basename "$(dirname "$T")"); I=$(basename "$T")
  OUT="$DEST/${R}_${I}.json"
  [ -s "$OUT" ] && { echo "== $R/$I déjà fait"; continue; }
  M=$(ls -d "$T"/auto_grown_* 2>/dev/null | head -1)
  [ -z "$M" ] && { echo "== $R/$I : aucun maillage"; continue; }

  # Le volume BRUT du rouleau (pas la prediction) : resolu une fois par rouleau.
  if [ -z "${VOLUME_DE[$R]:-}" ]; then
    V=$(lister "$R/volumes/" | grep -E '(8\.640|9\.362)um' | head -1 | sed 's|/$||')
    [ -z "$V" ] && { echo "== $R : aucun volume au protocole du prix"; continue; }
    VOLUME_DE[$R]="$B/$V"
    UM_DE[$R]=$(basename "$V" | grep -oE '[0-9]+\.[0-9]+um' | head -1 | sed 's/um$//')
  fi

  W="$DEST/$R.$I.travail"; rm -rf "$W"; mkdir -p "$W"
  DEBUT=$(date +%s)
  # ⚠ `vc_render_tifxyz` SAUTE ses sorties existantes, y compris CORROMPUES (piege 28quater
  # du HANDOFF) : le repertoire est efface avant chaque rendu, jamais reutilise.
  if ! vc_flatten -i "$M" -o "$W/plat" > "$W/flatten.log" 2>&1; then
    echo "== $R/$I : vc_flatten a échoué"; continue
  fi
  if ! vc_render_tifxyz -v "$W/cache" --remote-url "${VOLUME_DE[$R]}" --scale 1 -g 0 \
        -s "$W/plat" --tif-output "$W/rendu" -n "$COUCHES" --slice-step 1 --auto-crop \
        > "$W/rendu.log" 2>&1; then
    echo "== $R/$I : vc_render_tifxyz a échoué"; continue
  fi
  # ⚠ La couche « tracee » est celle du MILIEU de la pile rendue, pas 0 : `--slice-step 1`
  # centre la pile sur la surface. La donner fausse decale tout profil d'ecart.
  MILIEU=$(( COUCHES / 2 ))
  ( cd "$ROOT/inference_xpu" && uv run python ../src/volume/depth_profile.py \
      "$W/rendu" --grid --step 400 --traced-layer "$MILIEU" \
      --voxel-um "${UM_DE[$R]}" --out "$OUT" ) > "$W/profil.log" 2>&1 \
    || { echo "== $R/$I : depth_profile a échoué"; continue; }
  FIN=$(date +%s)
  # ⚠ `depth_profile.py --out` ecrit une LISTE (une entree par repertoire de couches), pas
  # un dictionnaire. La premiere version annotait `d['rouleau']` et levait un TypeError sur
  # chaque tirage -- la mesure etait ecrite, l'etiquette perdue. On enveloppe.
  python3 -c "
import json
d = json.load(open('$OUT'))
profils = d if isinstance(d, list) else [d]
json.dump({'rouleau': '$R', 'repetition': '$I', 'secondes': $FIN - $DEBUT,
           'couches': $COUCHES, 'profils': profils}, open('$OUT','w'), indent=2)
print(f\"== $R/$I  {$FIN - $DEBUT} s\")"
  rm -rf "$W/cache"
done
echo "campagne finie — $DEST"
