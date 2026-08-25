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
# Usage : src/outils/controle_resolution.sh [dossier-de-trace] [niveaux...]
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  # ⚠⚠ Ce fichier ne DOIT PAS savoir convertir tranches et voxel : c est le profileur
  # partage qui le sait, et une seconde copie -- fut-elle dans une sonde -- est une seconde
  # definition libre de diverger. La sonde verifie donc la DELEGATION, pas l arithmetique.
  chk "le profileur partage existe" '[ -x "$ROOT/src/outils/profiler_une_surface.sh" ]'
  chk "ce fichier le delegue" 'grep -q profiler_une_surface.sh "$ROOT/src/outils/controle_resolution.sh"'
  # ⚠⚠ Les motifs sont COUPES en deux morceaux concatenes. Ecrits d un bloc, ils
  # apparaitraient dans le fichier que la sonde inspecte -- donc la sonde se matcherait
  # ELLE-MEME et signalerait une duplication qui n existe pas. C est la TROISIEME fois que
  # ce piege se paie ici (pkill -f, la sonde du traceur, celle-ci) : une sonde qui scanne
  # son propre fichier ne doit jamais contenir son motif en clair.
  chk "... et ne recalcule pas les tranches lui-meme" \
      '! grep -qE "tranches_au""_niveau|traced-""layer" "$ROOT/src/outils/controle_resolution.sh"'
  chk "... ni ne rend lui-meme" \
      '! grep -q "rendre_""surveille" "$ROOT/src/outils/controle_resolution.sh"'
  chk "la conversion est testee la ou elle vit" \
      '"$ROOT/src/outils/profiler_une_surface.sh" --verifier >/dev/null 2>&1'
  chk "le depouilleur de convergence existe" '[ -f "$ROOT/src/commun/test_convergence.py" ]'
  out=$("$ROOT/src/outils/controle_resolution.sh" /inexistant 2>&1); rc=$?
  chk "une trace absente est refusee (2)" '[ "$rc" = 2 ]'
  chk "... et le refus nomme le chemin" 'printf "%s" "$out" | grep -q inexistant'
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
  # ⚠ Le rendu, le profil et le jugement sont delegues au profileur PARTAGE -- et surtout
  # la conversion tranches/voxel avec lui. Elle etait ecrite ici et tracer_une_graine.sh
  # allait la recopier : deux definitions du piege d unites, libres de diverger, dont l une
  # comparerait un jour deux fenetres physiques differentes en les appelant deux resolutions.
  PLAT="$SRC/plat" NIVEAU="$G" FENETRES_BASE="$FENETRES_BASE" UM_BASE="$UM_BASE" \
    CACHE_GB="$CACHE_GB" DEST="$DEST" ETIQUETTE="niveau $G" \
    JSON="$ROOT/docs/resolution_g${G}.json" \
    "$ROOT/src/outils/profiler_une_surface.sh"
done

echo
echo "== confrontation"
uv run --project "$ROOT" python - <<'PY'
import json, sys
from pathlib import Path
sys.path[:0] = [str(p) for p in __import__("pathlib").Path("src").glob("*") if p.is_dir()]
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
