#!/usr/bin/env bash
# ⚠⚠ Le plafond de generations est-il en train de FABRIQUER le resultat negatif ?
#
# Toute trace jamais faite sur PHercParis4 s arrete a la generation 59, et leurs aires
# coincident a quatre chiffres -- elles mesurent le PLAFOND, pas la donnee. Or ce budget de
# 60 a ete fixe le jour ou j estimais le rendu a 57 Kio/s, une extrapolation faite sur UN
# echantillon ; la mesure l a corrige a 1108-5861 Kio/s, vingt a cent fois plus vite.
#
# Deux issues, et elles ne se ressemblent pas :
#   α stable      -- 60 suffisaient pour juger, le resultat negatif tient, et on le SAURA.
#   α qui baisse  -- la surface avait besoin de place, et tout ce rouleau est a refaire.
#
# ⚠ Ce n est pas un test de convergence de plus : c est le test de l INSTRUMENT qui a
# produit tous les autres.
#
# ⚠ La trace elle-meme est deleguee a tracer_une_graine.sh. Deux traces qu on compare
# doivent avoir ete faites pareil ; les ecrire deux fois serait mesurer la difference des
# scripts en croyant mesurer celle des budgets.
#
# Usage : src/outils/plafond_generations.sh <prediction> <indice> [budgets...]
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "le traceur partage existe" '[ -x "$ROOT/src/outils/tracer_une_graine.sh" ]'
  # ⚠⚠ Le motif est coupe en deux morceaux concatenes : ecrit d un bloc, il apparaitrait
  # dans le fichier que la sonde inspecte, donc la sonde se matcherait ELLE-MEME et
  # signalerait une duplication qui n existe pas. Meme piege que pkill -f.
  chk "aucune trace n est reecrite ici" \
      '! grep -q "vc_grow""_seg_from_seed" "$ROOT/src/outils/plafond_generations.sh"'
  chk "le depouilleur existe" '[ -f "$ROOT/src/graine/effet_du_plafond.py" ]'
  out=$("$ROOT/src/outils/plafond_generations.sh" inexistante 0 2>&1); rc=$?
  chk "une prediction sans graines est refusee (2)" '[ "$rc" = 2 ]'
  chk "... et le refus nomme le fichier attendu" 'printf "%s" "$out" | grep -q graine_inexistante'
  chk "au moins deux budgets par defaut" \
      'grep -qE "BUDGETS=\(60 200\)" "$ROOT/src/outils/plafond_generations.sh"'
  # ⚠ Le niveau entre dans le NOM du resultat, sinon deux niveaux ecriraient le meme
  # fichier et le dernier ecraserait l autre -- en silence.
  chk "le niveau entre dans le nom du resultat" \
      'grep -q "SUFFIXE" "$ROOT/src/outils/plafond_generations.sh"'
  chk "un maillage deja trace n est pas retrace" \
      'grep -q "on profile seulement" "$ROOT/src/outils/plafond_generations.sh"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

PRED="${1:-}"; IDX="${2:-}"
[ -n "$PRED" ] && [ -n "$IDX" ] || { echo "usage : $0 <prediction> <indice> [budgets...]" >&2; exit 2; }
shift 2
BUDGETS=(60 200)
[ $# -gt 0 ] && BUDGETS=("$@")

G="$ROOT/data/prediction_paris4/graine_${PRED}.json"
[ -s "$G" ] || { echo "refus : graines absentes — $G" >&2; exit 2; }
read -r X Y Z PLAN OCC VOIS <<<"$(python3 -c "
import json
c = json.load(open('$G'))['candidats'][$IDX]
print(c['x'], c['y'], c['z'], round(c['planarite'], 4), round(c['occupation'], 4), c['voisins'])")" \
  || { echo "refus : candidat $IDX absent de $G" >&2; exit 2; }

echo "== ${PRED} candidat ${IDX}  planarité $PLAN  occupation $OCC  voisins $VOIS  ($X $Y $Z)"
echo "== budgets : ${BUDGETS[*]}"

# ⚠⚠ Le NIVEAU de pyramide fait partie de l identite d une mesure, donc du nom du fichier.
# Comparer un budget mesure au niveau 0 a un budget mesure au niveau 1 confondrait le
# plafond avec la resolution : l ecart d alpha serait credible et indechiffrable. Le
# depouilleur REFUSE d ailleurs un lot melange.
NIVEAU="${NIVEAU:-0}"
SUFFIXE=""
[ "$NIVEAU" != "0" ] && SUFFIXE="_niv${NIVEAU}"
echo "== niveau de pyramide $NIVEAU"

for B in "${BUDGETS[@]}"; do
  J="$ROOT/docs/plafond_${PRED}_c${IDX}_g${B}${SUFFIXE}.json"
  if [ -s "$J" ]; then echo "== g${B} déjà mesuré, sauté"; continue; fi
  echo "== g${B}"
  D="$ROOT/data/paris4_plafond/${PRED}_c${IDX}_g${B}"
  if [ -d "$D/plat" ]; then
    # ⚠ Le maillage existe deja : on ne le RETRACE pas. Un nouveau tirage changerait la
    # surface, donc l ecart mesure porterait le bruit du traceur en plus du budget --
    # exactement le confond que ce fichier existe pour eviter.
    echo "   maillage déjà tracé, on profile seulement"
    PLAT="$D/plat" NIVEAU="$NIVEAU" DEST="$D" JSON="$J" \
      ETIQUETTE="${PRED}_c${IDX} @ ${B} générations, niveau $NIVEAU" \
      "$ROOT/src/outils/profiler_une_surface.sh"
  else
    PREDICTION="$PRED" DEST="$D" GENERATIONS="$B" NIVEAU="$NIVEAU" \
      ETIQUETTE="${PRED}_c${IDX} @ ${B} générations" JSON="$J" \
      "$ROOT/src/outils/tracer_une_graine.sh" "$X" "$Y" "$Z"
  fi
  rc=$?
  # ⚠ 4 = la graine n a rien fait pousser : c est un resultat, et un budget PLUS GRAND ne
  # peut pas y changer quoi que ce soit, donc on s arrete plutot que de payer la suite.
  [ "$rc" = 4 ] && { echo "   aucune surface — inutile d'aller plus haut"; break; }
done

echo
echo "== confrontation"
uv run --project "$ROOT" python "$ROOT/src/graine/effet_du_plafond.py" \
    --docs "$ROOT/docs/mesures" --prediction "$PRED" --candidat "$IDX" --niveau "$NIVEAU" \
    --json "$ROOT/docs/plafond_${PRED}_c${IDX}${SUFFIXE}.json"
