#!/usr/bin/env bash
# ⚠⚠ Le plafond de generations est-il en train de FABRIQUER le resultat negatif ?
#
# Toute trace jamais faite sur PHercParis4 s arrete a la generation 59. Ce budget de 60
# a ete choisi le jour ou j estimais le rendu a 57 Kio/s -- une extrapolation faite sur UN
# echantillon, corrigee depuis par la mesure : 1108 a 5861 Kio/s, soit vingt a cent fois
# plus vite. Le budget etait donc dimensionne pour un cout qui n existe pas.
#
# Ce que ce script mesure : α a budget croissant, MEME graine, meme prediction. Deux
# issues, et elles ne se ressemblent pas.
#
#   α stable        -- 60 generations suffisaient pour juger, le resultat negatif tient,
#                      et on le saura au lieu de l esperer.
#   α qui baisse    -- la surface avait besoin de place pour reveler sa feuille, et TOUT
#                      ce que ce depot affirme sur ce rouleau est a refaire plus grand.
#
# ⚠ Ce n est pas un test de convergence de plus : c est le test de l INSTRUMENT qui a
# produit tous les autres. Il passe donc avant d ajouter une seizieme trace a 60.
#
# ⚠ La graine est passee en argument et pas devinee : la campagne des candidats vient de
# montrer que trouver_graine classe sur la planarite seule, donc « la » graine d une
# prediction n est pas une notion qui va de soi.
#
# Usage : tools/plafond_generations.sh <prediction> <indice-candidat> [budgets...]
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRED="${1:?prediction (m7 ou ps256)}"
IDX="${2:?indice du candidat}"
shift 2
BUDGETS=("${@:-60 200}")
[ $# -gt 0 ] && BUDGETS=("$@")

GRAINES="$ROOT/data/prediction_paris4/graines_${PRED}.json"
[ -f "$GRAINES" ] || { echo "graines absentes : $GRAINES" >&2; exit 2; }

lire() { python3 - "$GRAINES" "$IDX" "$1" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); c=d["candidats"][int(sys.argv[2])]
print(c[sys.argv[3]] if sys.argv[3] in c else c["xyz"][{"x":0,"y":1,"z":2}[sys.argv[3]]])
PY
}
X=$(lire x); Y=$(lire y); Z=$(lire z)
echo "graine ${PRED} c${IDX} : ${X} ${Y} ${Z}"
echo "budgets : ${BUDGETS[*]}"

for G in "${BUDGETS[@]}"; do
  DEST="$ROOT/data/paris4_plafond/${PRED}_c${IDX}_g${G}"
  if [ -s "$DEST/profil.json" ]; then echo "== g${G} deja mesure, saute"; continue; fi
  mkdir -p "$DEST"
  echo "== g${G} — trace"
  # ⚠ DEST est ABSOLU : depth_profile tourne depuis inference_xpu, un chemin relatif
  # y designerait un autre dossier. Piege deja paye une fois.
  if ! GENERATIONS="$G" DEST="$DEST" "$ROOT/tools/tracer_une_graine.sh" "$X" "$Y" "$Z" \
        > "$DEST/trace.log" 2>&1; then
    echo "   trace en echec (voir $DEST/trace.log) — on s arrete la, un budget plus grand"
    echo "   ne peut que couter davantage"; break
  fi
  A=$(grep -oE 'generated surface .*\(([0-9.]+) cm\^2\)' "$DEST/trace.log" | grep -oE '[0-9.]+ cm' | tr -d ' cm' | tail -1)
  echo "   aire ${A:-?} cm²"
  echo "== g${G} — profil de profondeur"
  if ! "$ROOT/tools/rendre_surveille.sh" "$DEST" > "$DEST/profil.log" 2>&1; then
    echo "   rendu en echec ou tue par le chien de garde (voir $DEST/profil.log)"; break
  fi
  uv run --project "$ROOT" python "$ROOT/analysis/src/test_convergence.py" \
      --profil "$DEST/profil.json" --json "$ROOT/docs/plafond_${PRED}_c${IDX}_g${G}.json" \
      2>&1 | tail -4
done

echo
echo "== confrontation"
uv run --project "$ROOT" python "$ROOT/analysis/src/effet_du_plafond.py" \
    --docs "$ROOT/docs" --prediction "$PRED" --candidat "$IDX" \
    --json "$ROOT/docs/plafond_${PRED}_c${IDX}.json" || true
