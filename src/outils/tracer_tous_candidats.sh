#!/bin/bash
# Et si la graine choisie etait la MOINS bien soutenue de celles qu'on avait ?
#
# ⚠⚠ Ce que la lecture des candidats a montre, et que personne n'avait regarde. `trouver_graine`
# classe par PLANARITE seule, et sur `PHercParis4` ce classement met devant :
#   ps256 : planarite 0,9977 / occupation 0,0215   (le plancher de la bande est 0,02)
#   m7    : planarite 1,0000 / occupation 0,7500 / NEUF voisins seulement
# alors que les candidats suivants ont 27 voisins -- un bloc 3x3x3 plein -- des planarites de
# 0,987 a 0,997 et des occupations en plein milieu de bande.
#
# ⭐⭐ Une planarite de 1,0000 sur 9 voisins n'est pas MEILLEURE que 0,987 sur 27 : elle est
# moins ETAYEE. Trois dix-milliemes separent les planarites la ou l'occupation varie d'un
# facteur vingt. Le classement a donc designe, a chaque fois, le point le moins soutenu -- et
# c'est cette graine-la que toutes les traces de `48` ont utilisee.
#
# ⚠ Ce script ne corrige PAS le classement : inventer un score composite serait choisir la
# reponse. Il trace TOUS les candidats et laisse la mesure dire quelle propriete predit la
# convergence. C'est plus cher et c'est la seule facon de le savoir.
#
# ⚠ Reprenable : un candidat deja trace est saute.
#
#   ./src/outils/tracer_tous_candidats.sh [dest]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/paris4_candidats}
case "$DEST" in /*) ;; *) DEST="$ROOT/$DEST" ;; esac
GRAINES=${GRAINES:-$ROOT/data/prediction_paris4}
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
S="PHercParis4/representations/predictions/surfaces"
GENERATIONS=${GENERATIONS:-60}
FENETRES=${FENETRES:-"41 161"}
PATIENCE=${PATIENCE:-420}
mkdir -p "$DEST"

declare -A PRED=(
  [ps256]="$S/20260411134726-surface-20260413141734-surface-recto-2um-ps256-L0-th0.45.zarr"
  [m7]="$S/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr"
)
SCAN=$(basename "${PRED[ps256]}" | cut -d- -f1)
VOL=$(curl -s --max-time 60 "$B/?list-type=2&prefix=PHercParis4/volumes/$SCAN&delimiter=/" \
      | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$' | sed 's|/$||')
UM=$(printf '%s' "$VOL" | grep -oE '[0-9]+\.[0-9]+um' | head -1 | sed 's/um$//')
[ -n "${VOL:-}" ] && [ -n "${UM:-}" ] || { echo "refus : volume introuvable pour $SCAN" >&2; exit 3; }
echo "== volume $(basename "$VOL")  ($UM µm)  ·  plafond $GENERATIONS générations"

for NOM in ps256 m7; do
  G="$GRAINES/graine_$NOM.json"
  [ -s "$G" ] || { echo "== graine $NOM absente"; continue; }
  N=$(python3 -c "import json;print(len(json.load(open('$G'))['candidats']))")
  for I in $(seq 0 $((N - 1))); do
    read -r X Y Z PLAN OCC VOIS <<<"$(python3 -c "
import json
c=json.load(open('$G'))['candidats'][$I]
print(c['x'], c['y'], c['z'], round(c['planarite'],4), round(c['occupation'],4), c['voisins'])")"
    CAS="${NOM}_c${I}"
    W="$DEST/$CAS"; mkdir -p "$W"
    echo "== $NOM candidat $I  planarité $PLAN  occupation $OCC  voisins $VOIS  ($X $Y $Z)"

    # ⚠ La trace, le rendu, le profil et le jugement sont delegues au traceur PARTAGE.
    # Ce corps etait inline ici et plafond_generations.sh allait le recopier -- deux
    # definitions de « tracer une graine », libres de diverger sur le pas de tranche ou le
    # recadrage, donc deux traces qu on croirait comparables.
    # ⚠ VOL et UM sont passes : les redemander a S3 huit fois couterait huit fois et
    # pourrait rendre deux reponses differentes en cours de campagne.
    PREDICTION="$NOM" DEST="$W" GENERATIONS="$GENERATIONS" FENETRES="$FENETRES" \
      PATIENCE="$PATIENCE" VOL="$VOL" UM="$UM" \
      ETIQUETTE="$CAS (occ $OCC, ${VOIS}v)" JSON="$ROOT/docs/mesures/candidat_paris4_$CAS.json" \
      "$ROOT/src/outils/tracer_une_graine.sh" "$X" "$Y" "$Z"
  done
done
