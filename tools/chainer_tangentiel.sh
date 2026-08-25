#!/usr/bin/env bash
# ENCHAINER la projection tangentielle, et comparer au saut direct de meme longueur.
#
# ⚠⚠ C EST LA QUESTION QUE LA CHAINE TANGENTIELLE POSE, et une projection unique n y repond
# pas. `44` mesure qu une nappe projetee reste sur sa feuille jusqu a ~380 µm et y est le mieux
# posee vers 240. Reste a savoir si on peut RECOMMENCER depuis la projection : une chaine n est
# utile que si l erreur ne s accumule pas plus vite qu on n avance.
#
# ⭐ Le pouvoir de la comparaison vient du TEMOIN : la meme distance totale, franchie d un
# seul bond. Si l enchainement tient la ou le bond direct casse, la chaine gagne quelque chose
# que la projection seule n a pas -- et si les deux se valent, l enchainement ne sert a rien et
# il vaut mieux le savoir avant de l ecrire.
#
# ⚠ La projection est DELEGUEE, et elle compose parce qu elle lit un tifxyz et en ecrit un.
# C est la seule raison pour laquelle ce fichier peut etre court.
#
# Usage : SOURCE=<tifxyz> PAS=5 MAILLONS=5 DEST=<dir> tools/chainer_tangentiel.sh
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "la projection est deleguee" \
      'grep -q "projeter_tangentiel.py" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "le profil est delegue" \
      'grep -q "profiler_une_surface.sh" "$ROOT/tools/chainer_tangentiel.sh"'
  MOTEUR="vc_render""_tifxyz"
  chk "le moteur n est PAS invoque ici" \
      '! grep -q "$MOTEUR" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ LE TEMOIN EST LA MOITIE DE L EXPERIENCE. Sans le saut direct de meme longueur, un
  # enchainement qui tient ne prouve rien : il pourrait tenir parce que la distance totale est
  # courte, et non parce que l enchainement aide.
  chk "le saut direct de meme longueur est calcule" \
      'grep -q "DIRECT=" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "... et il vaut pas x maillons" \
      'grep -q "PAS \* MAILLONS" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠ Chaque maillon part de la SORTIE du precedent : c est ce qui fait une chaine plutot
  # qu une serie de projections independantes depuis la meme source.
  chk "chaque maillon part du precedent" \
      'grep -q "COURANT=" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ Aucun provisoire dans `docs/`. Le motif est compose a l execution, sinon cette ligne
  # contiendrait ce qu elle interdit -- piege paye trois fois dans ce depot.
  INTERDIT="JSON"".brouillon"
  chk "aucun fichier provisoire dans docs/" \
      '! grep -q "$INTERDIT" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "... le provisoire passe par mktemp" \
      'grep -q "TMP=\$(mktemp)" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "SOURCE est un parametre" 'grep -q "SOURCE:?" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ La geometrie est mesuree AVANT les profils, et sans eux. Un pas qui derive refute une
  # chaine pour zero rendu ; payer deux rendus pour l apprendre serait payer pour rien.
  chk "la geometrie est mesuree sans rendu" \
      'grep -q -- "--croissance" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "... et elle precede les profils" \
      '[ "$(grep -n -- "--croissance" "$ROOT/tools/chainer_tangentiel.sh" | head -1 | cut -d: -f1)" \
        -lt "$(grep -n "profiler_une_surface.sh" "$ROOT/tools/chainer_tangentiel.sh" | tail -1 | cut -d: -f1)" ]'
  chk "PROFILS=0 permet de s arreter la" \
      'grep -q "PROFILS:-1" "$ROOT/tools/chainer_tangentiel.sh"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

SOURCE="${SOURCE:?SOURCE requis — un tifxyz dont on sait qu il suit une feuille}"
PAS="${PAS:-5}"
MAILLONS="${MAILLONS:-5}"
DEST="${DEST:-$ROOT/data/chaine_tangentielle}"
JSON="${JSON:-$ROOT/docs/chaine_tangentielle.json}"
FENETRES="${FENETRES:-41}"
UM_BASE="${UM_BASE:-2.4}"
DIRECT=$((PAS * MAILLONS))

mkdir -p "$DEST"
echo "== chaîne : $MAILLONS maillons de $PAS pas  ·  témoin : un bond direct de $DIRECT pas"

COURANT="$SOURCE"
for M in $(seq 1 "$MAILLONS"); do
  D="$DEST/maillon_$M"
  if [ ! -f "$D/meta.json" ]; then
    uv run --project "$ROOT" python "$ROOT/analysis/src/projeter_tangentiel.py" \
        "$COURANT" --dest "$D" --pas "$PAS" > "$D.log" 2>&1 \
      || { echo "   ⚠ maillon $M échoué — la chaîne s arrête là" >&2; break; }
  fi
  # ⚠⚠ LE MAILLON SUIVANT PART D ICI. Repartir de `$SOURCE` a chaque fois donnerait des
  # projections independantes de longueurs croissantes, c est-a-dire l experience deja faite,
  # sous un autre nom.
  COURANT="$D"
  echo "   maillon $M → $(basename "$D")"
done

if [ ! -f "$DEST/direct/meta.json" ]; then
  uv run --project "$ROOT" python "$ROOT/analysis/src/projeter_tangentiel.py" \
      "$SOURCE" --dest "$DEST/direct" --pas "$DIRECT" > "$DEST/direct.log" 2>&1 \
    || echo "   ⚠ témoin direct échoué" >&2
fi

# ⚠⚠ PROFILS=0 : enchainer et ne mesurer que la GEOMETRIE. Le pas reellement parcouru et le
# volume englobant se lisent dans les `meta.json`, donc ils coutent zero rendu -- et un pas qui
# derive suffit a REFUTER une chaine. Une chaine longue se sonde donc d abord comme ca, et on ne
# paie les rendus que si la geometrie a tenu.
# ⚠ Necessaire, pas suffisant : une chaine peut garder un pas parfait en marchant droit hors de
# sa feuille. Cette voie ne peut que refuter, et c est precisement ce qui la rend bon marche.
uv run --project "$ROOT" python "$ROOT/analysis/src/projeter_tangentiel.py" --croissance \
    "$SOURCE" $(for M in $(seq 1 "$MAILLONS"); do
        [ -f "$DEST/maillon_$M/meta.json" ] && printf '%s ' "$DEST/maillon_$M"; done) \
    $([ -f "$DEST/direct/meta.json" ] && printf '%s' "$DEST/direct") \
    --json "${CROISSANCE:-${JSON%.json}_croissance.json}"

if [ "${PROFILS:-1}" = 0 ]; then
  echo "PROFILS=0 — geometrie seule, aucun rendu"
  exit 0
fi

printf '\n%-14s %10s %12s %12s\n' "surface" "µm" "amplitude" "pic au bord"
# ⚠⚠ Le provisoire passe par `mktemp`, PAS par un suffixe dans `docs/`. Je viens d ecrire ce
# defaut une seconde fois, dans un fichier neuf, une heure apres l avoir repare ailleurs : un
# repertoire de resultats ne doit contenir que des resultats, et une campagne interrompue y
# laisserait un JSON a moitie ecrit.
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
echo "[" > "$TMP"
PREMIER=1
for NOM in "$SOURCE" "$COURANT" "$DEST/direct"; do
  [ -f "$NOM/meta.json" ] || continue
  ETQ=$(basename "$NOM")
  W="$DEST/profil_$ETQ"
  if [ ! -s "$W/g0_n$FENETRES/profil.json" ]; then
    GARDER_RENDU=0 PLAT="$NOM" NIVEAU=0 FENETRES_BASE="$FENETRES" UM_BASE="$UM_BASE" \
      DEST="$W" ETIQUETTE="chaine_$ETQ" JSON="$W/verdict.json" \
      "$ROOT/tools/profiler_une_surface.sh" > "$W.log" 2>&1 \
      || { echo "   ⚠ profil de $ETQ abandonné"; continue; }
  fi
  L=$(python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))[0]
m = json.load(open(sys.argv[2]))
print(round(m.get('pas_voxels', 0.0) * $UM_BASE, 1), round(d['amplitude_mediane'], 4),
      round(d['au_bord_intensite'], 3))" "$W/g0_n$FENETRES/profil.json" "$NOM/meta.json" 2>/dev/null)
  set -- $L
  printf '%-14s %10s %12s %12s\n' "$ETQ" "${1:-?}" "${2:-?}" "${3:-?}"
  [ "$PREMIER" = 1 ] || echo "," >> "$TMP"
  PREMIER=0
  printf '{"surface": "%s", "um": %s, "amplitude": %s, "au_bord": %s}' \
      "$ETQ" "${1:-0}" "${2:-0}" "${3:-0}" >> "$TMP"
done
echo "]" >> "$TMP"
mv "$TMP" "$JSON"
echo "écrit : $JSON"
