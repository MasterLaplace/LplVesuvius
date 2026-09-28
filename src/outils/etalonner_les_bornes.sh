#!/bin/bash
# Les bornes d'une unité systemd, essayées l'une après l'autre sur la même étape : ce que chacune coûte en temps.
#
# Chaque essai tourne dans sa propre unité, sous ses bornes, et surveiller_lunite.sh relève ce qu'elles lui ont coûté.
# Les essais passent l'un après l'autre, jamais ensemble : deux essais simultanés se disputeraient la machine, et chacun
# mesurerait l'autre.
#
#   ./src/outils/etalonner_les_bornes.sh <dossier> <commande...> -- <étiquette>:<cœurs>:<quota>:<high>:<max> ...
#   ./src/outils/etalonner_les_bornes.sh --verifier
#
# La commande reçoit l'étiquette en dernier argument. <cœurs> vaut « tous », ou une liste que taskset comprend (0-5) :
# l'affinité passe aux processus enfants, et un rendu qui compte ses cœurs n'en voit alors pas plus qu'on ne lui en donne.
set -u

# Refuse un essai qui ne porte pas ses cinq champs, en le nommant.
valide() {
  IFS=: read -r e c q h m x <<< "$1"
  [ -n "$e" ] && [ -n "$c" ] && [ -n "$q" ] && [ -n "$h" ] && [ -n "$m" ] && [ -z "${x:-}" ] && return 0
  echo "refus : l'essai « $1 » ne porte pas étiquette:cœurs:quota:high:max" >&2
  return 2
}

if [ "${1:-}" = "--verifier" ]; then
  E=0; N=0
  v() { N=$((N + 1)); if [ "$2" != "$3" ]; then E=$((E + 1)); echo "  ECHEC  $1 — attendu $3, obtenu $2"; fi; }
  valide "A1:tous:600%:7G:10G" 2>/dev/null; v "un essai complet passe" "$?" "0"
  valide "A1:tous:600%:7G" 2>/dev/null; v "un champ manquant est refusé" "$?" "2"
  valide "A1:tous:600%:7G:10G:x" 2>/dev/null; v "un champ de trop est refusé" "$?" "2"
  valide "A1::600%:7G:10G" 2>/dev/null; v "un champ vide est refusé" "$?" "2"
  v "le refus nomme l'essai" "$(valide "Z9:tous" 2>&1 | grep -c Z9)" "1"
  echo "etalonner_les_bornes.sh   $([ $E -eq 0 ] && echo "ALL PASS" || echo "DES SONDES ONT ÉCHOUÉ") ($E failures, $N checks)"
  exit $((E > 0))
fi

DOSSIER=$1; shift
CMD=()
while [ $# -gt 0 ] && [ "$1" != "--" ]; do CMD+=("$1"); shift; done
[ $# -gt 0 ] || { echo "refus : aucun essai après --" >&2; exit 2; }
shift
for essai in "$@"; do valide "$essai" || exit 2; done
mkdir -p "$DOSSIER" && DOSSIER=$(cd "$DOSSIER" && pwd)
for essai in "$@"; do
  IFS=: read -r etiquette coeurs quota haute plafond <<< "$essai"
  unite="vesuvius-etalon-$etiquette"
  avant=(); [ "$coeurs" != "tous" ] && avant=(taskset -c "$coeurs")
  systemd-run --user --unit="$unite" --collect -E PATH="$PATH" -p Nice=15 -p CPUQuota="$quota" -p CPUWeight=10 \
    -p MemoryHigh="$haute" -p MemoryMax="$plafond" -p MemorySwapMax=0 -p WorkingDirectory="$PWD" \
    -p StandardOutput="file:$DOSSIER/$etiquette.log" -p StandardError="file:$DOSSIER/$etiquette.log" \
    "${avant[@]}" "${CMD[@]}" "$etiquette" > /dev/null || exit 2
  "$(dirname "$0")/surveiller_lunite.sh" "$unite" "$DOSSIER/${etiquette}_cgroup.tsv" 2 > /dev/null
  echo "$etiquette : $(cat "$DOSSIER/${etiquette}_cgroup.json")"
done
