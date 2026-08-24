#!/usr/bin/env bash
# Reprofiler nos traces A LA GEOMETRIE D UN CORPUS PUBLIE, puis les y situer.
#
# ⚠⚠ POURQUOI UN OUTIL ET PAS UNE BOUCLE DE TERMINAL. Le relief depend de la fenetre de
# lecture -- exposant -0,83 dans le plan, +1,01 en profondeur -- donc comparer une de nos
# traces au corpus publie exige de la RELIRE dans la fenetre du corpus. Les parametres de
# cette relecture (taille, profondeur, couche centrale, sous-fenetre de la pile) sont
# quatre occasions de se tromper, et une boucle tapee au terminal les perd a la premiere
# session qui se ferme.
#
# ⚠ La sous-fenetre est CALCULEE depuis la pile et la profondeur cible, jamais posee : une
# pile de 161 couches lue sur 109 doit etre centree, sinon on compare deux profondeurs en
# croyant comparer deux surfaces.
#
# Usage : CORPUS=docs/balayage_scroll1.csv COUCHES=109 FENETRE=128 tools/situer_nos_traces.sh <pile>...
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

sous_fenetre() {  # pile_couches profondeur_cible -> "premiere derniere centre"
  python3 -c "
n, cible = int($1), int($2)
if cible > n: raise SystemExit('la pile a moins de couches que la cible')
debut = (n - cible) // 2
print(debut, debut + cible - 1, cible // 2)"
}

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  # ⚠ La sous-fenetre est CENTREE : 161 couches lues sur 109 laissent 26 de chaque cote.
  chk "161 sur 109 est centree" '[ "$(sous_fenetre 161 109)" = "26 134 54" ]'
  chk "une cible egale a la pile ne rogne rien" '[ "$(sous_fenetre 109 109)" = "0 108 54" ]'
  # ⚠⚠ La couche tracee est le MILIEU DE LA SOUS-FENETRE, pas de la pile : la donner en
  # coordonnees de pile decalerait le profil de vingt-six couches sans rien signaler.
  chk "la couche tracee est le milieu de la SOUS-fenetre" \
      '[ "$(sous_fenetre 161 109 | cut -d" " -f3)" = 54 ]'
  chk "une cible plus profonde que la pile est refusee" \
      '! sous_fenetre 41 109 >/dev/null 2>&1'
  chk "l outil delegue le profil, il ne le recalcule pas" \
      'grep -q depth_profile.py "$ROOT/tools/situer_nos_traces.sh"'
  chk "et la situation aussi" \
      'grep -q calibration_corpus.py "$ROOT/tools/situer_nos_traces.sh"'
  # ⚠ Le corpus est un PARAMETRE : coder un chemin en dur ferait de cet outil un script a
  # usage unique, et la question se reposera sur un autre rouleau.
  chk "le corpus est un parametre" 'grep -q "CORPUS:?" "$ROOT/tools/situer_nos_traces.sh"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

CORPUS="${CORPUS:?CORPUS requis — le balayage du corpus publie}"
COUCHES="${COUCHES:-109}"
FENETRE="${FENETRE:-128}"
PAS="${PAS:-200}"
VOXEL="${VOXEL:-2.4}"
[ $# -ge 1 ] || { echo "donner au moins une pile de couches rendues" >&2; exit 2; }

printf '%-34s %9s %9s %8s\n' "trace" "relief" "×plancher" "rang"
for PILE in "$@"; do
  N=$(ls "$PILE"/*.tif 2>/dev/null | wc -l)
  [ "$N" -gt 0 ] || { echo "  ⚠ $PILE : aucune couche" >&2; continue; }
  read -r DEB FIN CENTRE <<< "$(sous_fenetre "$N" "$COUCHES")"
  OUT=$(mktemp --suffix=.json)
  ( cd "$ROOT/inference_xpu" && uv run python ../analysis/src/depth_profile.py \
      "$ROOT/${PILE#"$ROOT/"}" --grid --size "$FENETRE" --step "$PAS" \
      --from-layer "$DEB" --to-layer "$FIN" --traced-layer "$CENTRE" \
      --voxel-um "$VOXEL" --out "$OUT" ) >/dev/null 2>&1 \
    || { echo "  ⚠ $PILE : profil échoué" >&2; rm -f "$OUT"; continue; }
  LIGNE=$(python3 "$ROOT/analysis/src/calibration_corpus.py" "$CORPUS" \
      --layers "$COUCHES" --situer "$OUT" 2>/dev/null \
      | grep -E "relief|rang" | tr '\n' ' ')
  REL=$(echo "$LIGNE" | grep -oE 'relief [0-9.]+' | awk '{print $2}')
  RAP=$(echo "$LIGNE" | grep -oE '×[0-9.]+ le plancher' | grep -oE '[0-9.]+')
  RANG=$(echo "$LIGNE" | grep -oE 'rang [0-9]+ sur [0-9]+' | sed 's/rang //; s/ sur /\//')
  printf '%-34s %9s %9s %8s\n' "$(basename "$(dirname "$PILE")")/$(basename "$PILE")" \
      "${REL:-?}" "${RAP:-?}" "${RANG:-?}"
  rm -f "$OUT"
done
