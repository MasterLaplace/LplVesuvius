#!/bin/bash
# JUGER UNE NAPPE : aplatir, rendre dans deux fenetres, mesurer la convergence.
#
# ⚠⚠ CE FICHIER EXISTE PARCE QUE J'AVAIS COPIE CETTE FONCTION. `spire_suivante.sh` et
# `etendre_nappe.sh` en portaient chacun une version verbatim, et les deux ont DEJA diverge :
# la reserve `--au-bord` a ete cablee dans l'une avant l'autre, si bien qu'un verdict de
# campagne portait le complement et l'autre non. Deux chemins de jugement sont deux occasions
# de ne pas juger pareil, et ce depot a paye ce motif assez souvent pour ne pas le laisser
# passer une fois de plus.
#
# ⭐ Il sert aussi a juger une nappe qui ne vient d'AUCUNE campagne — une surface rognee, un
# maillage recupere, un essai a la main. Sans lui, chaque cas de ce genre serait une commande
# tapee dans un terminal, c'est-a-dire perdue.
#
# S'utilise soit en le SOURCANT (les campagnes), soit en ligne de commande :
#   ./tools/juger_nappe.sh <dossier-de-travail> <maillage> <nom> [etiquette]

# --- reglages partages, surchargeables par l'appelant ---------------------------------
ROULEAU=${ROULEAU:-PHerc1447}
SURF=${SURF:-PHerc1447/representations/predictions/surfaces/20250521151220-surface-20260413222639-surface-m7-L0-th0.2.zarr}
FENETRES=${FENETRES:-"31 81"}
UM=${UM:-8.64}
B=${B:-https://vesuvius-challenge-open-data.s3.amazonaws.com}
VOL=${VOL:-$B/$ROULEAU/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr}

# ⚠⚠ Un plafond de croisements PAR CENTIMETRE CARRE, verifie AVANT de payer les rendus.
# Mesure du 2026-08-22 : 0/cm2 sur la surface qui converge, 875/cm2 sur la premiere qui casse,
# 2147/cm2 sur la suivante. Le seuil est a 100/cm2, un ordre de grandeur de chaque cote.
#
# ⚠⚠ CE N'EST PAS UN CRITERE DE QUALITE, et le contre-exemple est mesure : une surface a ZERO
# croisement a rendu α = +1,806, la pire de sa campagne. Se replier sur soi-meme et etre mal
# posee sont DEUX DEFAUTS DIFFERENTS ; ce plafond attrape le premier et ignore le second. Il
# ne sert qu'a ne pas bruler vingt minutes de rendu sur une surface manifestement repliee.
PLAFOND_CROISEMENTS_PAR_CM2=${PLAFOND_CROISEMENTS_PAR_CM2:-100}

juger_nappe() {
  local W=$1 M=$2 NOM=$3 ETIQ=${4:-}
  local R="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
  mkdir -p "$W"
  [ -s "$W/selfcross.json" ] || vc_tifxyz_selfcross --surface "$M" -o "$W/selfcross.json" > /dev/null 2>&1
  local CROIS SERIE AIRE
  CROIS=$(python3 "$R/analysis/src/lire_selfcross.py" "$W/selfcross.json" 2>/dev/null || echo "?")
  AIRE=$(python3 -c "
import json;print(f\"{json.load(open('$M/meta.json'))['area_cm2']:.2f}\")" 2>/dev/null || echo "?")

  if [ "$CROIS" != "?" ] && [ "$AIRE" != "?" ]; then
    local TROP
    TROP=$(python3 -c "
c, a, p = $CROIS, $AIRE, $PLAFOND_CROISEMENTS_PAR_CM2
print(1 if a > 0 and c / a > p else 0)" 2>/dev/null || echo 0)
    if [ "$TROP" = "1" ]; then
      echo "== $NOM  ($AIRE cm², $CROIS auto-intersections)"
      echo "   ⚠⚠ REPLIEE : $(python3 -c "print(f'{$CROIS/$AIRE:.0f}')") croisements/cm², au-dessus du plafond de $PLAFOND_CROISEMENTS_PAR_CM2 — rendus NON payés."
      touch "$W/ABANDONNE"
      return 1
    fi
  fi

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
      ( cd "$R/inference_xpu" && uv run python ../analysis/src/depth_profile.py \
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

  # ⚠ Le complement d'α, lu dans le profil de la fenetre la plus ETROITE — c'est la que
  # « le pic tombe au bord » a un sens, une fenetre large finissant par contenir quelque
  # chose. α est une mediane et ne montre pas cette part.
  local N0 BORD
  N0=$(echo "$FENETRES" | awk '{print $1}')
  BORD=$(python3 -c "
import json,sys
d=json.load(open(sys.argv[1])); d=d[0] if isinstance(d,list) else d
print(d.get('au_bord_relief',''))" "$W/profil_${N0}c.json" 2>/dev/null || echo "")

  echo "== $NOM  ($AIRE cm², $CROIS auto-intersections)"
  ( cd "$R/experiments" && uv run python ../analysis/src/test_convergence.py \
      ${BORD:+--au-bord "$BORD"} \
      --serie "${SERIE%,}" --nom "$NOM ($AIRE cm², $CROIS croisements)" \
      --json "$R/docs/${ETIQ}$NOM.json" | tail -4 )
}

# Appel direct : juger une nappe qui ne vient d'aucune campagne.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  set -u
  ROOT=$(cd "$(dirname "$0")/.." && pwd)
  juger_nappe "${1:?dossier de travail}" "${2:?maillage}" "${3:?nom}" "${4:-jugement_}"
fi
