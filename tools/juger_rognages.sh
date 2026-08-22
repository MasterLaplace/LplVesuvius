#!/bin/bash
# Juger les nappes ROGNEES : la peripherie tardive retiree change-t-elle la part au bord ?
#
# ⚠ Un script plutot qu'une commande tapee : c'est une mesure dont le resultat sera cite, donc
# son calcul doit etre dans l'arbre. Il ne fait que boucler sur les rognages et appeler le
# chemin de jugement PARTAGE — aucune logique propre, donc rien qui puisse diverger.
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
# shellcheck source=/dev/null
. "$ROOT/tools/juger_nappe.sh"

# ⚠ La racine est un parametre : un second cycle de rognage doit pouvoir vivre dans son
# propre dossier, sinon `gen30` du cycle 1 et `gen30` du cycle 2 ecriraient le meme verdict.
RACINE=${1:-$ROOT/data/rogne}
ETIQ=${2:-rognage_}
for D in "$RACINE"/gen*; do
  [ -d "$D/trace/rogne" ] || continue
  G=$(basename "$D")
  juger_nappe "$D" "$D/trace/rogne" "$G" "$ETIQ"
done
echo "fin — $(ls -d "$RACINE"/gen* 2>/dev/null | wc -l) rognage(s) juge(s) dans $RACINE"
