#!/usr/bin/env bash
# Tracer UNE graine, la rendre a plusieurs profondeurs, et juger sa convergence.
#
# ⚠⚠ Ce fichier existe parce qu une SECONDE campagne en avait besoin. Le corps etait inline
# dans tracer_tous_candidats.sh, et plafond_generations.sh allait le recopier -- c est-a-dire
# creer deux definitions de « tracer une graine » libres de diverger sur le pas de tranche,
# le recadrage ou la couche tracee. Deux traces qu on compare doivent avoir ete faites
# pareil, sinon la comparaison mesure la difference des scripts.
#
# ⚠ Le volume et la taille de voxel sont passes par l ENVIRONNEMENT quand l appelant les
# connait deja : une campagne de huit graines qui les redemanderait a S3 huit fois paierait
# huit fois, et surtout pourrait tomber sur deux reponses differentes en cours de route.
#
# ⚠ Sortie 3 = refus (on ne sait pas quoi tracer), sortie 4 = la graine n a rien fait
# pousser. Le second n est PAS une panne : une graine posee dans du vide est un resultat.
#
# Usage : PREDICTION=ps256 DEST=/abs/dir tools/tracer_une_graine.sh <x> <y> <z>
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
S="PHercParis4/representations/predictions/surfaces"
declare -A PRED=(
  [ps256]="$S/20260411134726-surface-20260413141734-surface-recto-2um-ps256-L0-th0.45.zarr"
  [m7]="$S/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr"
)

resoudre_volume() {
  local scan="$1"
  curl -s --max-time 60 "$B/?list-type=2&prefix=PHercParis4/volumes/$scan&delimiter=/" \
    | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$' | sed 's|/$||'
}

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "les deux predictions sont declarees" '[ -n "${PRED[ps256]:-}" ] && [ -n "${PRED[m7]:-}" ]'
  chk "les deux pointent vers des zarr distincts" '[ "${PRED[ps256]}" != "${PRED[m7]}" ]'
  # ⚠ Une prediction inconnue doit etre REFUSEE et pas defauter : defauter tracerait une
  # autre surface que celle demandee, et le resultat porterait le mauvais nom.
  out=$(PREDICTION=inexistante DEST=/tmp/x "$ROOT/tools/tracer_une_graine.sh" 1 2 3 2>&1); rc=$?
  chk "une prediction inconnue est refusee (3)" '[ "$rc" = 3 ]'
  chk "... et le refus la nomme" 'printf "%s" "$out" | grep -q inexistante'
  out=$(PREDICTION=ps256 "$ROOT/tools/tracer_une_graine.sh" 1 2 3 2>&1); rc=$?
  chk "sans DEST, refus (3)" '[ "$rc" = 3 ]'
  # ⚠⚠ Un DEST relatif est refuse : depth_profile tourne depuis inference_xpu, donc un
  # chemin relatif y designerait un AUTRE dossier. Piege deja paye une fois.
  out=$(PREDICTION=ps256 DEST=relatif/ici "$ROOT/tools/tracer_une_graine.sh" 1 2 3 2>&1); rc=$?
  chk "un DEST relatif est refuse (3)" '[ "$rc" = 3 ]'
  chk "... et le refus dit pourquoi" 'printf "%s" "$out" | grep -qi absolu'
  out=$(PREDICTION=ps256 DEST=/tmp/x "$ROOT/tools/tracer_une_graine.sh" 1 2 2>&1); rc=$?
  chk "trois coordonnees exigees" '[ "$rc" = 3 ]'
  chk "le script est appele par au moins une campagne" \
      'grep -lq tracer_une_graine.sh "$ROOT"/tools/*.sh'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

# ⚠ Un refus sort en 3, jamais en 1 : ${X:?} sortirait en 1, indistinguable
# d une panne, et un appelant qui trie les deux lirait le mauvais cas.
NOM="${PREDICTION:-}"
[ -n "$NOM" ] || { echo "refus : PREDICTION (ps256 ou m7) requis" >&2; exit 3; }
[ -n "${PRED[$NOM]:-}" ] || { echo "refus : prédiction inconnue « $NOM »" >&2; exit 3; }
DEST="${DEST:-}"
[ -n "$DEST" ] || { echo "refus : DEST requis" >&2; exit 3; }
case "$DEST" in /*) ;; *) echo "refus : DEST doit être ABSOLU (depth_profile tourne depuis inference_xpu)" >&2; exit 3;; esac
[ $# -ge 3 ] || { echo "refus : trois coordonnées attendues" >&2; exit 3; }
X="$1"; Y="$2"; Z="$3"
GENERATIONS="${GENERATIONS:-60}"
FENETRES="${FENETRES:-41 161}"
PATIENCE="${PATIENCE:-420}"
ETIQUETTE="${ETIQUETTE:-$(basename "$DEST")}"
JSON="${JSON:-$ROOT/docs/trace_${ETIQUETTE}.json}"

if [ -z "${VOL:-}" ] || [ -z "${UM:-}" ]; then
  SCAN=$(basename "${PRED[ps256]}" | cut -d- -f1)
  VOL=$(resoudre_volume "$SCAN")
  UM=$(printf '%s' "$VOL" | grep -oE '[0-9]+\.[0-9]+um' | head -1 | sed 's/um$//')
fi
[ -n "${VOL:-}" ] && [ -n "${UM:-}" ] || { echo "refus : volume introuvable" >&2; exit 3; }

mkdir -p "$DEST"
[ -s "$DEST/seed.json" ] || python3 - "$ROOT/artefacts/PHerc0358/seed.json" "$DEST/seed.json" \
    "$UM" "$GENERATIONS" <<'PY'
import json, sys
src, dst, um, gen = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
d = json.load(open(src)); d["voxelsize"] = um; d["generations"] = gen
json.dump(d, open(dst, "w"), indent=2)
PY

M=$(ls -d "$DEST"/auto_grown_* 2>/dev/null | head -1)
if [ -z "$M" ]; then
  ( cd "$DEST" && timeout 7200 vc_grow_seg_from_seed -v "$B/${PRED[$NOM]}" -t . \
      -p seed.json -s "$X" "$Y" "$Z" ) > "$DEST/trace.log" 2>&1
  M=$(ls -d "$DEST"/auto_grown_* 2>/dev/null | head -1)
fi
# ⚠⚠ « aucune surface » est un RESULTAT sur cette graine, pas une panne du script.
[ -n "$M" ] || { echo "   ⚠ aucune surface — résultat sur cette graine"; exit 4; }
AIRE=$(grep -oE 'generated surface .* \(([0-9.]+) cm\^2\)' "$DEST/trace.log" \
       | grep -oE '\(([0-9.]+)' | tr -d '(' | tail -1)
[ -d "$DEST/plat" ] || vc_flatten -i "$M" -o "$DEST/plat" > "$DEST/flatten.log" 2>&1

PROFILS=""
for F in $FENETRES; do
  OUT="$DEST/profil_${F}c.json"
  if [ ! -s "$OUT" ]; then
    rm -rf "$DEST/rendu_$F"
    "$ROOT/tools/rendre_surveille.sh" "$DEST/rendu_$F" "$PATIENCE" -- \
        -v "$DEST/cache" --remote-url "$B/$VOL" --scale 1 -g 0 -s "$DEST/plat" \
        --tif-output "$DEST/rendu_$F" -n "$F" --slice-step 1 --auto-crop \
        > "$DEST/rendu_$F.log" 2>&1 || { echo "   ⚠ rendu $F abandonné"; continue; }
    ( cd "$ROOT/inference_xpu" && uv run python ../analysis/src/depth_profile.py \
        "$DEST/rendu_$F" --grid --step 200 --traced-layer $((F / 2)) --voxel-um "$UM" \
        --out "$OUT" ) > "$DEST/profil_$F.log" 2>&1 || { echo "   ⚠ profil $F échoué"; continue; }
  fi
  PROFILS="$PROFILS --profil $OUT"
done
rm -rf "$DEST/cache"
echo "   aire ${AIRE:-?} cm²"
[ -n "$PROFILS" ] && ( cd "$ROOT/experiments" && uv run python \
    ../analysis/src/test_convergence.py $PROFILS --nom "$ETIQUETTE" --json "$JSON" | tail -4 )
