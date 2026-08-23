#!/usr/bin/env bash
# Rendre une surface DEJA aplatie a plusieurs profondeurs, et juger sa convergence.
#
# ⚠⚠ Ce fichier existe parce que TROIS appelants en avaient besoin et que deux l avaient
# deja recopie : tracer_une_graine.sh (qui trace puis profile), controle_resolution.sh (qui
# profile une surface existante a deux niveaux de pyramide) et la campagne du plafond. Deux
# profils qu on COMPARE doivent avoir ete faits pareil -- pas de tranche, recadrage, couche
# tracee -- sinon la comparaison mesure la difference des scripts.
#
# ⚠⚠ LE PIEGE D UNITES, en un seul endroit. Au niveau g de la pyramide un voxel fait 2^g
# fois le voxel de base, donc UNE TRANCHE COUVRE 2^g fois plus d epaisseur. Rendre 41
# tranches au niveau 1 couvre DEUX FOIS la profondeur physique de 41 tranches au niveau 0 :
# on comparerait deux fenetres differentes en croyant comparer deux resolutions. Le nombre
# de tranches est donc DIVISE par 2^g et --voxel-um MULTIPLIE par 2^g.
#
# Usage : PLAT=<dir> NIVEAU=1 JSON=<out> tools/profiler_une_surface.sh
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ⚠ La conversion est une FONCTION, appelee par tout le monde, et non un calcul recopie.
#
# ⚠⚠ L arrondi est « au superieur a la moitie » (int(x+0.5)) et PAS round(). Deux raisons,
# et la seconde est la vraie :
#   - round() en Python arrondit au PAIR : round(41/2) rend 20, pas 21. Un lecteur qui
#     verifie a la main obtient 21 et croit a un bug.
#   - une fenetre est CENTREE sur sa couche tracee (--traced-layer N/2), donc elle doit
#     rester IMPAIRE : 41 -> 21 -> 11 garde un centre, 41 -> 20 n en a pas. Une fenetre
#     paire decale le centre d une demi-tranche a chaque niveau, silencieusement.
tranches_au_niveau() { python3 -c "print(max(3, int($1 / 2**$2 + 0.5)))"; }
voxel_au_niveau()    { python3 -c "print($1 * 2**$2)"; }

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "au niveau 0, rien ne bouge" '[ "$(tranches_au_niveau 41 0)" = 41 ] && [ "$(voxel_au_niveau 2.4 0)" = 2.4 ]'
  chk "au niveau 1, les tranches sont divisees" '[ "$(tranches_au_niveau 41 1)" = 21 ]'
  chk "... et le voxel multiplie" '[ "$(voxel_au_niveau 2.4 1)" = 4.8 ]'
  chk "au niveau 2 aussi" '[ "$(tranches_au_niveau 161 2)" = 40 ] && [ "$(voxel_au_niveau 2.4 2)" = 9.6 ]'
  # ⚠⚠ Une fenetre impaire le RESTE : elle est centree sur sa couche tracee, et une
  # fenetre paire n a pas de centre -- le decalage serait d une demi-tranche par niveau,
  # en silence. ⚠ round() de Python arrondit au PAIR et rendrait 20 : la sonde le fixe.
  chk "une fenetre impaire reste impaire au niveau 1" \
      '[ "$(python3 -c "print($(tranches_au_niveau 41 1) % 2)")" = 1 ]'
  chk "... et 161 aussi" '[ "$(tranches_au_niveau 161 1)" = 81 ]' 
  # ⚠⚠ La propriete qui compte : la PROFONDEUR PHYSIQUE est conservee a une tranche pres.
  # Si elle ne l etait pas, deux niveaux mesureraient deux fenetres differentes et l ecart
  # d alpha qu on lirait serait celui des fenetres, pas celui des resolutions.
  chk "la profondeur physique est conservee au niveau 1" \
      '[ "$(python3 -c "a=41*2.4; b=$(tranches_au_niveau 41 1)*$(voxel_au_niveau 2.4 1); print(abs(a-b) <= $(voxel_au_niveau 2.4 1))")" = True ]'
  chk "... et au niveau 2" \
      '[ "$(python3 -c "a=161*2.4; b=$(tranches_au_niveau 161 2)*$(voxel_au_niveau 2.4 2); print(abs(a-b) <= $(voxel_au_niveau 2.4 2))")" = True ]'
  # ⚠ Un plancher de trois tranches : une fenetre de deux ne porte aucun profil, et une
  # division agressive la produirait en silence.
  chk "une fenetre trop divisee est plancheee a 3" '[ "$(tranches_au_niveau 5 4)" = 3 ]'
  out=$(PLAT=/inexistant "$ROOT/tools/profiler_une_surface.sh" 2>&1); rc=$?
  chk "une surface absente est refusee (2)" '[ "$rc" = 2 ]'
  chk "au moins un appelant utilise ce script" \
      'grep -lq profiler_une_surface.sh "$ROOT"/tools/*.sh'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

PLAT="${PLAT:-}"
[ -d "$PLAT" ] || { echo "refus : surface aplatie absente — PLAT=$PLAT" >&2; exit 2; }
NIVEAU="${NIVEAU:-0}"
FENETRES_BASE="${FENETRES_BASE:-41 161}"
UM_BASE="${UM_BASE:-2.4}"
PATIENCE="${PATIENCE:-420}"
DEST="${DEST:?DEST requis}"
ETIQUETTE="${ETIQUETTE:-$(basename "$DEST")}"
JSON="${JSON:?JSON requis}"
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="${VOL:-PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr}"

UM=$(voxel_au_niveau "$UM_BASE" "$NIVEAU")
echo "== niveau $NIVEAU  (voxel ${UM} µm)  ·  $ETIQUETTE"
PROFILS=""
for F in $FENETRES_BASE; do
  N=$(tranches_au_niveau "$F" "$NIVEAU")
  W="$DEST/g${NIVEAU}_n${N}"
  OUT="$W/profil.json"
  if [ ! -s "$OUT" ]; then
    rm -rf "$W"; mkdir -p "$W"
    "$ROOT/tools/rendre_surveille.sh" "$W/rendu" "$PATIENCE" -- \
        -v "$W/cache" --remote-url "$B/$VOL" --scale 1 -g "$NIVEAU" -s "$PLAT" \
        --tif-output "$W/rendu" -n "$N" --slice-step 1 --auto-crop \
        > "$W/rendu.log" 2>&1 || { echo "   ⚠ rendu n=$N abandonné"; continue; }
    ( cd "$ROOT/inference_xpu" && uv run python ../analysis/src/depth_profile.py \
        "$W/rendu" --grid --step 200 --traced-layer $((N / 2)) --voxel-um "$UM" \
        --out "$OUT" ) > "$W/profil.log" 2>&1 \
      || { echo "   ⚠ profil n=$N échoué"; continue; }
    rm -rf "$W/cache" "$W/rendu"
  fi
  echo "   n=$N couches"
  PROFILS="$PROFILS --profil $OUT"
done
[ -n "$PROFILS" ] || { echo "   ⚠ aucun profil produit"; exit 3; }
( cd "$ROOT/experiments" && uv run python ../analysis/src/test_convergence.py $PROFILS \
    --nom "$ETIQUETTE" --json "$JSON" | tail -4 )
