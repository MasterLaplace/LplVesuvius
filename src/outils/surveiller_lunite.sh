#!/bin/bash
# Ce que ses bornes coûtent à une unité systemd : le temps où ses tâches attendent le processeur ou la mémoire.
#
# Une unité sous CPUQuota et MemoryHigh peut aller trois fois moins vite sans qu'aucune ligne ne le dise, et rien
# n'indique laquelle des deux bornes la freine. Le noyau le compte : la pression (PSI) de chaque cgroup donne le temps
# où au moins une de ses tâches attendait (« some »), ou toutes (« full »). Ce script en prend l'écart, rapporté au
# temps écoulé, avec les périodes où le quota a suspendu l'unité et les fois où elle a dépassé MemoryHigh.
#
# Le relevé va dans <sortie.tsv>, le bilan en JSON dans <sortie>.json, avec les bornes que l'unité portait.
#
#   ./src/outils/surveiller_lunite.sh <unité> <sortie.tsv> [intervalle_s]
#   ./src/outils/surveiller_lunite.sh --verifier
set -u

# Le total en microsecondes d'une ligne de pression : `champ` vaut some ou full.
pression() { awk -v c="$2" '$1 == c { for (i = 2; i <= NF; i++) if ($i ~ /^total=/) { sub("total=", "", $i); print $i } }' "$1"; }
# Une clé d'un fichier « clé valeur » de cgroup.
cle() { awk -v k="$2" '$1 == k { print $2 }' "$1"; }
# L'écart de deux totaux en microsecondes, en millièmes du temps écoulé.
millieme() { awk -v a="$1" -v b="$2" -v t="$3" 'BEGIN { printf "%d", (t > 0) ? (b - a) / t * 1000 : 0 }'; }

# Le bilan de deux relevés, le premier et le dernier, en JSON dans <sortie>.json, avec les bornes connues.
bilan() {
  read -r t0 c0 s0 f0 p0 q0 h0 x0 _ <<< "$1"
  read -r t1 c1 s1 f1 p1 q1 h1 x1 _ pic _ <<< "$2"
  dt=$((t1 - t0))
  printf '{"lunite": "%s", "les_secondes": %d, "les_coeurs_permis": "%s", "le_quota": "%s", "memoryhigh": "%s", ' \
    "$UNITE" $((dt / 1000000)) "$COEURS" "$QUOTA" "$HAUTE" > "${SORTIE%.tsv}.json"
  printf '"memorymax": "%s", "lattente_du_processeur_pour_mille": %s, "lattente_de_la_memoire_pour_mille": %s, ' \
    "$PLAFOND" "$(millieme "$c0" "$c1" "$dt")" "$(millieme "$s0" "$s1" "$dt")" >> "${SORTIE%.tsv}.json"
  printf '"toutes_les_taches_attendent_la_memoire_pour_mille": %s, "les_periodes_suspendues": %d, "les_periodes": %d, ' \
    "$(millieme "$f0" "$f1" "$dt")" $((q1 - q0)) $((p1 - p0)) >> "${SORTIE%.tsv}.json"
  printf '"les_depassements_de_memoryhigh": %d, "les_depassements_de_memorymax": %d, "le_pic_de_memoire_mio": %d}\n' \
    $((h1 - h0)) $((x1 - x0)) $((${pic:-0} / 1048576)) >> "${SORTIE%.tsv}.json"
  cat "${SORTIE%.tsv}.json"
}

# ⚠ Un relevé dont la surveillance s'est arrêtée avant l'unité (session close, machine éteinte) n'a pas de bilan : celui-ci
# le refait depuis son premier et son dernier relevé. Les bornes n'y sont pas écrites, donc elles restent inconnues.
if [ "${1:-}" = "--bilan" ]; then
  SORTIE=$2; UNITE=$(basename "${SORTIE%.tsv}"); COEURS=inconnu; QUOTA=inconnu; HAUTE=inconnu; PLAFOND=inconnu
  bilan "$(sed -n 2p "$SORTIE" | tr '\t' ' ')" "$(tail -1 "$SORTIE" | tr '\t' ' ')"
  exit 0
fi

if [ "${1:-}" = "--verifier" ]; then
  T=$(mktemp -d); E=0; N=0
  v() { N=$((N + 1)); if [ "$2" != "$3" ]; then E=$((E + 1)); echo "  ECHEC  $1 — attendu $3, obtenu $2"; fi; }
  printf 'some avg10=0.00 avg60=0.00 avg300=0.00 total=123\nfull avg10=0.00 avg60=0.00 avg300=0.00 total=45\n' > "$T/p"
  v "la pression some lit son total" "$(pression "$T/p" some)" "123"
  v "la pression full lit le sien, pas celui de some" "$(pression "$T/p" full)" "45"
  printf 'nr_periods 10\nnr_throttled 4\nthrottled_usec 99\n' > "$T/c"
  v "une clé se lit par son nom" "$(cle "$T/c" nr_throttled)" "4"
  v "une clé absente ne rend rien" "$(cle "$T/c" absente)" ""
  v "un écart se rapporte au temps écoulé" "$(millieme 1000 1500 2000)" "250"
  v "un temps nul ne divise pas" "$(millieme 1 2 0)" "0"
  printf 'usec\tcpu_some\n1000000\t0\t0\t0\t10\t1\t0\t0\t5\t5\t0\t0\n3000000\t1000000\t500000\t0\t30\t11\t4\t0\t9\t2097152\t0\t0\n' > "$T/r.tsv"
  "$0" --bilan "$T/r.tsv" > /dev/null
  v "le bilan refait prend l'écart du premier au dernier relevé" \
    "$(grep -o '"les_periodes_suspendues": [0-9]*, "les_periodes": [0-9]*' "$T/r.json")" \
    '"les_periodes_suspendues": 10, "les_periodes": 20'
  v "... en millièmes du temps écoulé" "$(grep -o '"lattente_du_processeur_pour_mille": [0-9]*' "$T/r.json")" \
    '"lattente_du_processeur_pour_mille": 500'
  v "... et son pic est le dernier pic relevé" "$(grep -o '"le_pic_de_memoire_mio": [0-9]*' "$T/r.json")" \
    '"le_pic_de_memoire_mio": 2'
  rm -rf "$T"
  echo "surveiller_lunite.sh   $([ $E -eq 0 ] && echo "ALL PASS" || echo "DES SONDES ONT ÉCHOUÉ") ($E failures, $N checks)"
  exit $((E > 0))
fi

UNITE=$1; SORTIE=$2; PAS=${3:-5}
CG=""
for _ in $(seq 60); do
  g=$(systemctl --user show -p ControlGroup --value "$UNITE" 2>/dev/null)
  [ -n "$g" ] && [ -d "/sys/fs/cgroup$g" ] && { CG="/sys/fs/cgroup$g"; break; }
  sleep 1
done
[ -n "$CG" ] || { echo "l'unité $UNITE n'a pas de cgroup après 60 s" >&2; exit 2; }

lire() {
  echo "$(date +%s%N | cut -c1-16) $(pression "$CG/cpu.pressure" some) $(pression "$CG/memory.pressure" some)" \
       "$(pression "$CG/memory.pressure" full) $(cle "$CG/cpu.stat" nr_periods) $(cle "$CG/cpu.stat" nr_throttled)" \
       "$(cle "$CG/memory.events" high) $(cle "$CG/memory.events" max) $(cat "$CG/memory.current")" \
       "$(cat "$CG/memory.peak") $(cle "$CG/memory.stat" anon) $(cle "$CG/memory.stat" file)"
}
PID=$(systemctl --user show -p MainPID --value "$UNITE")
COEURS=$(awk '/^Cpus_allowed_list:/ { print $2 }' "/proc/$PID/status" 2>/dev/null)
QUOTA=$(cat "$CG/cpu.max"); HAUTE=$(cat "$CG/memory.high"); PLAFOND=$(cat "$CG/memory.max")
echo -e "usec\tcpu_some\tmem_some\tmem_full\tperiodes\tsuspendues\thigh\tmax\tmemoire\tpic\tanon\tfichiers" > "$SORTIE"
D=$(lire); echo "$D" | tr ' ' '\t' >> "$SORTIE"; F=$D
while [ -d "$CG" ]; do
  L=$(lire 2>/dev/null) || break
  [ -n "$L" ] || break
  F=$L; echo "$L" | tr ' ' '\t' >> "$SORTIE"
  sleep "$PAS"
done
bilan "$D" "$F"
