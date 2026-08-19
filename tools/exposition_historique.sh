#!/bin/bash
# Combien de commits exposent une phrase donnee, et de quelle facon.
#
# ⚠ Deux comptes differents repondent a deux questions differentes, et les confondre
# sous-estime le risque :
#   - `git log -S` compte les commits qui CHANGENT le nombre d'occurrences : celui qui
#     ajoute, celui qui retire. C'est deux, et ca ne dit rien de l'exposition.
#   - ce qui compte pour une fuite, c'est le nombre de commits dont l'ARBRE porte encore
#     la phrase : n'importe quel `git checkout` de l'un d'eux la rend visible.
#
# ⚠ La phrase cherchee est un ARGUMENT, jamais en dur : ce script est versionne, et y
# ecrire la phrase privee annulerait ce qu'il sert a mesurer.
#
#   ./tools/exposition_historique.sh <motif> [fichier]
set -u
cd "$(dirname "$0")/.." || exit 2
MOTIF=${1:?usage: $0 <motif> [fichier]}
FICHIER=${2:-HANDOFF.md}

CHANGENT=$(git log --oneline --all -S "$MOTIF" -- "$FICHIER" | wc -l)

PORTENT=0; PREMIER=""; DERNIER=""
while read -r h; do
  if git show "$h:$FICHIER" 2>/dev/null | grep -q -- "$MOTIF"; then
    PORTENT=$((PORTENT + 1))
    [ -z "$DERNIER" ] && DERNIER=$h
    PREMIER=$h
  fi
done < <(git rev-list --all)

echo "motif   : $MOTIF"
echo "fichier : $FICHIER"
echo "commits qui CHANGENT le compte d'occurrences : $CHANGENT"
echo "commits dont l'ARBRE porte la phrase         : $PORTENT   <- c'est l'exposition"
[ "$PORTENT" -gt 0 ] && echo "  du plus ancien $PREMIER au plus recent $DERNIER"
echo
if [ -n "$(git remote -v)" ]; then
  echo "⚠⚠ UN REMOTE EXISTE — l'historique peut partir :"
  git remote -v | sed 's/^/    /'
else
  echo "aucun remote : rien ne sort tant qu'il n'y en a pas."
fi
