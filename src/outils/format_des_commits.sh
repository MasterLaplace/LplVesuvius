#!/usr/bin/env bash
# Les messages de commit suivent-ils le format du depot ?
#
# ⚠⚠ Pourquoi ce controle existe. Le depot a un format depuis son premier commit --
# `type(scope): sujet en minuscules, sans accents` -- et 108 commits d affilee s en sont
# ecartes sans que rien ne le signale. Une convention qu on se rappelle est une convention
# qu on oublie ; une convention verifiee est une convention.
#
# ⚠ Le controle porte sur les commits RECENTS, pas sur tout l historique : le passe est
# ecrit et le reecrire coute plus que ce qu il rapporte. Ce qui compte est que la derive
# s arrete ici.
#
# Trois regles, et chacune a ete enfreinte :
#   1. `type(scope): sujet`  -- 108 commits d affilee sans prefixe.
#   2. EN ANGLAIS, comme les autres depots de l auteur.
#   3. AUCUN tiret cadratin. C est une marque d ecriture generee, et l auteur l a dit
#      assez de fois pour que ce soit une regle et non une preference.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 2

# ⚠ Les types sont ceux REELLEMENT en usage dans l historique, releves et non inventes :
# `git log --format=%s | grep -oE '^[a-z]+\(' | sort -u`. « measure » et « resultat » sont
# propres a ce depot et disent quelque chose que « feat » ne dit pas -- une mesure n est
# pas une fonctionnalite, et un resultat encore moins.
TYPES="chore|clean|docs|feat|fix|measure|mesure|perf|resultat|test"
MOTIF="^($TYPES)\([a-z0-9_,-]+\): .+"
PORTEE="${PORTEE:-30}"

# ⚠⚠ Le tiret cadratin et son cousin le tiret demi-cadratin. La detection est litterale :
# un caractere, pas une heuristique.
CADRATINS=$'\u2014\u2013'

# ⚠ La detection du francais est DELEGUEE a src/encre/langue.py, qui porte deja la
# liste de mots-temoins et ses propres temoins. Une seconde liste ici serait une seconde
# definition de « est-ce du francais », libre de diverger de la premiere.
francais() {
  python3 -c "
import sys
sys.path[:0] = [str(p) for p in __import__('pathlib').Path('$ROOT/src').glob('*') if p.is_dir()]
from langue import reste_du_francais
sys.exit(0 if reste_du_francais(sys.argv[1]) else 1)
" "$1" 2>/dev/null
}

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  # ⚠⚠ Les sondes portent sur des chaines FABRIQUEES, pas sur l historique : un controle
  # dont les cas de test sont les donnees qu il controle ne peut pas etre teste a vide.
  bon="feat(vesuvius): mesurer le plafond de generations"
  chk "un sujet conforme passe" '[[ "$bon" =~ $MOTIF ]]'
  chk "sans type, refuse" '! [[ "Le depot part sur GitHub" =~ $MOTIF ]]'
  chk "sans scope, refuse" '! [[ "feat: quelque chose" =~ $MOTIF ]]'
  chk "un type inconnu, refuse" '! [[ "wip(vesuvius): bidule" =~ $MOTIF ]]'
  chk "un scope numerique passe" '[[ "docs(43): la chaine des spires" =~ $MOTIF ]]'
  chk "un scope multiple passe" '[[ "fix(00,01,27): un enonce faux" =~ $MOTIF ]]'
  # ⚠ « measure » et « resultat » sont propres a ce depot : les perdre reviendrait a
  # ranger une mesure sous « feat », ce qui efface la distinction que l auteur fait.
  chk "le type measure est admis" '[[ "measure(vesuvius): 78 tirages" =~ $MOTIF ]]'
  chk "le type resultat aussi" '[[ "resultat(vesuvius): H0 non rejetee" =~ $MOTIF ]]'
  chk "un sujet vide est refuse" '! [[ "feat(vesuvius): " =~ $MOTIF ]]'
  # ⚠⚠ Les deux regles ajoutees apres coup, et chacune parce qu elle a ete enfreinte.
  chk "un tiret cadratin est detecte" '[[ "feat(x): a — b" == *[$CADRATINS]* ]]'
  chk "... et son cousin demi-cadratin aussi" '[[ "feat(x): a – b" == *[$CADRATINS]* ]]'
  chk "un sujet sans cadratin passe" '! [[ "feat(x): a - b" == *[$CADRATINS]* ]]'
  chk "un sujet francais est detecte" 'francais "mesurer le plafond de generations"'
  chk "un sujet anglais ne l est pas" '! francais "measure the generation ceiling"' 
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

MAUVAIS=0
signale() { echo "  ⚠ $1"; echo "     $2"; MAUVAIS=$((MAUVAIS + 1)); }

while IFS= read -r h; do
  sujet=$(git log --format="%s" -1 "$h")
  corps=$(git log --format="%b" -1 "$h")
  [[ "$sujet" =~ $MOTIF ]] || signale "$sujet" "pas de type(scope):"
  case "$sujet$corps" in
    *[$CADRATINS]*) signale "$sujet" "contient un tiret cadratin" ;;
  esac
  if francais "$sujet"; then signale "$sujet" "sujet en francais, attendu en anglais"; fi
done < <(git log --format="%H" -n "$PORTEE")

if [ "$MAUVAIS" -gt 0 ]; then
  echo
  echo "$MAUVAIS sujet(s) hors format sur les $PORTEE derniers."
  echo "Format : type(scope): subject in lowercase english"
  echo "Types  : $(printf '%s' "$TYPES" | tr '|' ' ')"
  echo "⚠ pas de tiret cadratin, ni dans le sujet ni dans le corps"
  exit 1
fi
echo "les $PORTEE derniers commits suivent le format"
