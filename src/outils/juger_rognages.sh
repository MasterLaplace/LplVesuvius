#!/bin/bash
# Juger les nappes ROGNEES : la peripherie tardive retiree change-t-elle la part au bord ?
#
# ⚠ Un script plutot qu'une commande tapee : c'est une mesure dont le resultat sera cite, donc
# son calcul doit etre dans l'arbre. Il ne fait que boucler sur les rognages et appeler le
# chemin de jugement PARTAGE — aucune logique propre, donc rien qui puisse diverger.
#
# Les deux invocations reellement passees, ecrites ici parce que l'etiquette fait partie du
# NOM du resultat : `docs/mesures/cycle2_gen103.json` n'est tracable que si `cycle2` apparait dans
# l'arbre. Sans elles, l'audit des artefacts signalait deux JSON sans producteur — et il
# avait raison, la commande vivait dans un terminal.
#
#   src/outils/juger_rognages.sh                                   # cycle 1 -> docs/rognage_gen*.json
#   src/outils/juger_rognages.sh data/rogne_cycle2 cycle2_         # cycle 2 -> docs/cycle2_gen*.json
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
# shellcheck source=/dev/null
. "$ROOT/src/outils/juger_nappe.sh"

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
