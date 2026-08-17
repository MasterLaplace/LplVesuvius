#!/bin/bash
# Relancer TOUS les temoins du depot d'un coup.
#
# ⚠ Un depot dont on ne rejoue jamais les controles ne sait plus s'ils passent. Ceux-ci
# tournent tous HORS LIGNE -- ni reseau, ni volume distant, ni cle d'API -- justement
# pour qu'aucune raison exterieure ne puisse les empecher de tourner.
#
# Sort non nul si un seul echoue.
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
FAIL=0

run() {
  local nom=$1; shift
  local sortie
  sortie=$("$@" 2>&1 | grep -vE "SyntaxWarning|if amt")
  if grep -q "ALL PASS" <<<"$sortie"; then
    printf '  ✅ %-28s %s\n' "$nom" "$(grep -o 'ALL PASS.*' <<<"$sortie" | head -1)"
  else
    printf '  ❌ %-28s ECHEC\n' "$nom"
    sed 's/^/       /' <<<"$sortie" | tail -5
    FAIL=$((FAIL + 1))
  fi
}

echo "TEMOINS DU DEPOT — tous hors ligne"
echo

cd "$ROOT/experiments" || exit 2
run "fusions : pistes"        uv run python src/excision/fusions.py controle
run "fusions : ecarts"        uv run python src/excision/fusions.py ecarts-controle
run "fusion_scan : colocation" uv run python - <<'PY'
import sys; sys.path.insert(0,'src')
from excision.fusion_scan import colocation, null_model
n=0
same=[[{'radius_mm':17.1,'column':16000}],[{'radius_mm':17.3,'column':16200}]]
far =[[{'radius_mm':17.1,'column':16000}],[{'radius_mm': 5.0,'column':  200}]]
assert colocation(same,1.0,1000)['colocated']==1; n+=1
assert colocation(far ,1.0,1000)['colocated']==0; n+=1
# une seule coupe ne produit AUCUNE paire : la regle inter-coupes
assert colocation([[{'radius_mm':17.1,'column':16000},{'radius_mm':17.2,'column':16100}]],1.0,1000)['pairs']==0; n+=1
h=null_model(same,(5.,20.),18850,1.0,1000,300,0)
assert 0.0 <= h['mean'] <= 1.0; n+=1
print(f'ALL PASS (0 failures, {n} checks)')
PY

cd "$ROOT/inference_xpu" || exit 2
run "juge : depouilleur"      uv run python - <<'PY'
import sys; sys.path.insert(0,'../analysis/src')
from judge_api import parse
n=0
def ck(c):
    global n
    assert c; n+=1
ck(parse('LIGNES: 2\nL1: X\nLISIBILITE: 8') == {})          # format mono-panneau rejete
r=parse('PANNEAU: GAUCHE\nAUCUNE LETTRE VISIBLE\nLISIBILITE: 0\n\nPANNEAU: DROITE\nLIGNES: 2\nL1: ΠΑΡΑ·\nL1_CONFIANCE: 99986\nL2: ΥΙΤΕΡΦ\nLISIBILITE: 8')
ck(r['gauche']['refused'] and r['gauche']['glyphs']==0)
ck(not r['droite']['refused'])
ck(r['droite']['glyphs']==10)                                # 4 + 6, le · exclu
ck(r['droite']['legibility']==8)
f=parse('PANNEAU: GAUCHE\nLIGNES: 1\nL1: ΤΟΥ\nLISIBILITE: 5\nPANNEAU: DROITE\nAUCUNE LETTRE VISIBLE')
ck(not f['gauche']['refused'] and f['gauche']['glyphs']==3)   # fabrication detectable
print(f'ALL PASS (0 failures, {n} checks)')
PY

echo
if [ "$FAIL" -eq 0 ]; then
  echo "TOUS LES TEMOINS PASSENT"
else
  echo "$FAIL batterie(s) en echec"
fi
exit "$FAIL"
