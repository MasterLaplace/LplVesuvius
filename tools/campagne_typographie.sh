#!/bin/bash
# Mesurer la signature typographique des cartes d'encre publiees.
#
# ⚠ Un script plutot qu'une commande tapee : c'est une mesure dont le resultat sera cite,
# donc son calcul doit etre dans l'arbre. Il ne fait qu'appeler l'instrument.
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
cd "$ROOT/inference" || exit 2
uv run python ../analysis/src/typographie.py "$ROOT/data/encre" \
  --json "$ROOT/docs/typographie.json" --reduire "${REDUIRE:-4}" \
  --encre "$ROOT/docs/croisement_encre.json"
