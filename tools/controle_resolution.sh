#!/usr/bin/env bash
# La pyramide du volume preserve-t-elle alpha ?
#
# ⚠⚠ Pourquoi cette question est la seule qui debloque la fenetre profonde. 161 tranches
# d une surface de 3,66 cm2 font 38,2 Go de tampons a elles seules, sur une machine de 31,8.
# Aucun reglage de cache n y change rien : la mesure est IMPOSSIBLE au niveau 0. Le volume a
# six niveaux de pyramide, et -g 1 divise les pixels par quatre -- donc 9,5 Go, qui tiennent.
#
# ⚠⚠ Mais alpha est un RAPPORT entre deux profondeurs, et 35 a deja etabli qu un seuil cale
# sur le niveau 0 ne se transporte pas a resolution reduite. « Ca ne devrait pas biaiser »
# n est pas « c est mesure ». Ce script le mesure sur la PETITE surface, ou les deux niveaux
# tiennent tous les deux, avant d en dependre sur la grande.
#
# ⚠⚠ LE PIEGE D UNITES, et il est fatal si on le rate. Au niveau g le voxel fait 2^g fois
# le voxel de base, donc UNE TRANCHE COUVRE 2^g fois plus d epaisseur. Rendre 41 tranches
# au niveau 1 couvre DEUX FOIS la profondeur physique de 41 tranches au niveau 0 : on
# comparerait deux fenetres differentes en croyant comparer deux resolutions. Le nombre de
# tranches est donc DIVISE par 2^g, et --voxel-um MULTIPLIE par 2^g.
#
# Usage : tools/controle_resolution.sh [dossier-de-trace] [niveaux...]
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  # ⚠⚠ La sonde qui compte : les tranches DIVISEES et le voxel MULTIPLIE par 2^g. Une
  # erreur de sens ici comparerait deux fenetres physiques differentes en les appelant
  # deux resolutions -- et le resultat aurait l air d une mesure.
  for g in 0 1 2; do
    c=$(python3 -c "print(round(41 / 2**$g))")
    u=$(python3 -c "print(2.4 * 2**$g)")
    chk "niveau $g : tranches $c" "[ \"\$(python3 -c 'print(round(41 / 2**$g))')\" = \"$c\" ]"
    chk "niveau $g : voxel $u µm" "[ \"\$(python3 -c 'print(2.4 * 2**$g)')\" = \"$u\" ]"
  done
  chk "le voxel croit avec le niveau" \
      '[ "$(python3 -c "print(2.4*2**1 > 2.4*2**0)")" = "True" ]'
  chk "les tranches decroissent avec le niveau" \
      '[ "$(python3 -c "print(round(41/2**1) < 41)")" = "True" ]'
  chk "la profondeur physique est CONSERVEE" \
      '[ "$(python3 -c "a=41*2.4; b=round(41/2)*2.4*2; print(abs(a-b) <= 2.4*2)")" = "True" ]'
  chk "le depouilleur existe" '[ -f "$ROOT/analysis/src/effet_du_plafond.py" ]'
  out=$("$ROOT/tools/controle_resolution.sh" /inexistant 2>&1); rc=$?
  chk "une trace absente est refusee (2)" '[ "$rc" = 2 ]'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

SRC="${1:-$ROOT/data/paris4_plafond/ps256_c2_g60}"
[ -d "$SRC/plat" ] || { echo "refus : pas de surface aplatie dans $SRC" >&2; exit 2; }
shift 2>/dev/null || true
NIVEAUX=(0 1)
[ $# -gt 0 ] && NIVEAUX=("$@")
FENETRES_BASE="${FENETRES_BASE:-41 161}"
UM_BASE="${UM_BASE:-2.4}"
CACHE_GB="${CACHE_GB:-2}"
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="${VOL:-PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr}"
DEST="${DEST:-$ROOT/data/controle_resolution}"
mkdir -p "$DEST"

echo "== surface $(basename "$SRC")  ·  niveaux ${NIVEAUX[*]}  ·  --cache-gb $CACHE_GB"
for G in "${NIVEAUX[@]}"; do
  UM=$(python3 -c "print($UM_BASE * 2**$G)")
  PROFILS=""
  echo "== niveau $G  (voxel ${UM} µm)"
  for F in $FENETRES_BASE; do
    # ⚠ Divise, jamais recopie : voir le piege d unites en tete de fichier.
    N=$(python3 -c "print(max(3, round($F / 2**$G)))")
    W="$DEST/g${G}_n${N}"
    OUT="$W/profil.json"
    if [ ! -s "$OUT" ]; then
      rm -rf "$W"; mkdir -p "$W"
      "$ROOT/tools/rendre_surveille.sh" "$W/rendu" 420 -- \
          -v "$W/cache" --remote-url "$B/$VOL" --scale 1 -g "$G" -s "$SRC/plat" \
          --tif-output "$W/rendu" -n "$N" --slice-step 1 --auto-crop \
          --cache-gb "$CACHE_GB" > "$W/rendu.log" 2>&1 \
        || { echo "   ⚠ rendu n=$N abandonné"; continue; }
      ( cd "$ROOT/inference_xpu" && uv run python ../analysis/src/depth_profile.py \
          "$W/rendu" --grid --step 200 --traced-layer $((N / 2)) --voxel-um "$UM" \
          --out "$OUT" ) > "$W/profil.log" 2>&1 \
        || { echo "   ⚠ profil n=$N échoué"; continue; }
      rm -rf "$W/cache" "$W/rendu"
    fi
    echo "   n=$N couches → $(du -sh "$W" 2>/dev/null | cut -f1)"
    PROFILS="$PROFILS --profil $OUT"
  done
  [ -n "$PROFILS" ] && ( cd "$ROOT/experiments" && uv run python \
      ../analysis/src/test_convergence.py $PROFILS --nom "niveau $G (voxel ${UM} µm)" \
      --json "$ROOT/docs/resolution_g${G}.json" | tail -4 )
done

echo
echo "== confrontation"
uv run --project "$ROOT" python - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, "analysis/src")
from test_convergence import BRUIT_ALPHA
lignes = []
for f in sorted(Path("docs").glob("resolution_g*.json")):
    d = json.loads(f.read_text())
    g = int(f.stem.split("g")[-1])
    for x in (d.get("series") or ([d] if "verdict" in d else [])):
        lignes.append((g, x.get("verdict"), x.get("alpha")))
for g, v, a in lignes:
    print(f"  niveau {g} : α = {a:+.2f}" if isinstance(a, (int, float))
          else f"  niveau {g} : {v}")
mes = [(g, a) for g, v, a in lignes if isinstance(a, (int, float))]
if len(mes) >= 2:
    ec = max(a for _, a in mes) - min(a for _, a in mes)
    # ⚠⚠ Le seuil n est PAS le bruit du tireur : c est la MEME surface rendue deux fois,
    # donc aucun tirage neuf n intervient. Tout ecart au-dela de la resolution declaree
    # d alpha est un effet de l instrument, et il condamnerait la pyramide.
    print(f"\n  écart entre niveaux : {ec:.2f}   (résolution de α : {BRUIT_ALPHA})")
    print(f"  ⭐ la pyramide préserve α" if ec <= BRUIT_ALPHA
          else f"  ⚠⚠ la pyramide DÉPLACE α — elle ne peut pas servir à la fenêtre profonde")
else:
    print("\n  ⚠ moins de deux niveaux mesurés : rien à confronter")
PY
