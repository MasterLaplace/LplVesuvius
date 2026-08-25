#!/bin/bash
# Mesurer la signature typographique des cartes d'encre publiees.
#
# ⚠ Un script plutot qu'une commande tapee : c'est une mesure dont le resultat sera cite,
# donc son calcul doit etre dans l'arbre. Il ne fait qu'appeler l'instrument.
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
# ⚠ Tournait depuis `inference/` (l'environnement temoin CPU) jusqu'au 2026-08-25 : la
# racine porte PIL, numcodecs, numpy, scipy et tifffile, donc STRICTEMENT plus. `inference/`
# reste ce qu'il declare etre -- le temoin CPU du ×4,5 XPU -- et n'est plus emprunte pour
# des figures, ce qui evite de garder chaud un venv de 2,5 Gio pour du dessin.
cd "$ROOT" || exit 2
uv run python src/encre/typographie.py "$ROOT/data/encre" \
  --json "$ROOT/docs/typographie.json" --reduire "${REDUIRE:-4}" \
  --encre "$ROOT/docs/croisement_encre.json"
