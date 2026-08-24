#!/usr/bin/env bash
# JUSQU OU la tangente d une nappe reste-t-elle sur la nappe ?
#
# ⚠⚠ C EST LA MESURE QUI DECIDE DE LA CHAINE TANGENTIELLE. `44` §7 la nomme comme la seule
# chaine jamais tentee : suivre UNE feuille autour du tour, au lieu de traverser les feuilles.
# Le principe a reutiliser y est ecrit -- ne pas faire CROITRE une surface mais en PROJETER
# une, le long de sa tangente au lieu de sa normale.
#
# Une tangente est valable localement. La question n est donc pas « est-ce que ca marche »
# mais « SUR QUELLE DISTANCE » : c est elle qui donne le pas d une chaine, ou qui dit qu il
# n y en a pas. On projette a plusieurs pas et on mesure, a chaque fois, la part des points
# qui tombent encore dans de la matiere scannee.
#
# ⭐ Le sujet doit etre une nappe DONT ON SAIT qu elle suit une feuille -- un maillage PUBLIE.
# Le faire sur une de nos traces mesurerait la tangente d une surface posee en travers, ce qui
# ne repond pas a la question posee.
#
# Usage : SOURCE=<tifxyz publie> DEST=<dir> tools/portee_tangentielle.sh [pas...]
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ⚠⚠ UNE FONCTION, parce qu une sonde qui grep un mot ne verifie pas une COLONNE. Paye ici
# meme : l en-tete a gagne « mediane » pendant que l extraction rendait toujours
# `bloc_absent`, et les temoins sont restes verts parce que le mot `valeur_mediane` existait
# ailleurs dans le fichier. Un tableau dont l en-tete dit une chose et la colonne une autre
# est pire qu un tableau sans en-tete.
ligne_de() {
  python3 -c "
import json, sys
try: d = json.load(open(sys.argv[1]))
except Exception: print('? ? ? ?'); sys.exit(0)
c = d['comptes']; t = d['sondes']
print(f\"{c['matiere']}/{t}\", d.get('valeur_mediane'), d.get('valeurs_nulles'),
      round(c['matiere'] / t, 3) if t else 0)" "$1" 2>/dev/null
}

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "la projection est deleguee" \
      'grep -q "projeter_tangentiel.py" "$ROOT/tools/portee_tangentielle.sh"'
  chk "la mesure de matiere est deleguee" \
      'grep -q "matiere_au_point.py" "$ROOT/tools/portee_tangentielle.sh"'
  # ⚠ Les deux outils existent : un script qui delegue a un fichier absent echoue au premier
  # pas d une campagne, apres avoir eu l air de demarrer.
  chk "l outil de projection existe" '[ -f "$ROOT/analysis/src/projeter_tangentiel.py" ]'
  chk "l outil de matiere existe" '[ -f "$ROOT/analysis/src/matiere_au_point.py" ]'
  # ⚠⚠ Le pas ZERO est le CONTROLE de la campagne : la nappe non deplacee doit rendre une part
  # de matiere proche de 1, sinon c est le sujet qui est mauvais et non la tangente. Sans lui,
  # une part faible a dix pas ne voudrait rien dire.
  chk "le pas zero est dans les defauts" \
      'printf "%s" "$(grep -m1 "^PAS_DEFAUT=" "$ROOT/tools/portee_tangentielle.sh")" | grep -q "0 "'
  chk "SOURCE est un parametre" 'grep -q "SOURCE:?" "$ROOT/tools/portee_tangentielle.sh"'
  # ⚠⚠ La colonne qui decide est la VALEUR AU POINT. Sans elle la campagne rendait le meme
  # chiffre a toutes les distances -- une mesure incapable de distinguer ce qu elle mesure.
  # ⚠⚠ LA SONDE PORTE SUR LA COLONNE, PAS SUR LE MOT. Un grep du mot `valeur_mediane` restait
  # vert alors que l extraction rendait `bloc_absent` sous un en-tete « mediane ».
  T_J=$(mktemp)
  cat > "$T_J" <<'JSON'
{"comptes": {"matiere": 7, "bloc_vide": 0, "bloc_absent": 3, "hors_volume": 0},
 "sondes": 10, "valeur_mediane": 44, "valeurs_nulles": 2}
JSON
  # ⚠⚠ Des variables NOMMEES et pas $1/$2/$3 : `chk` est une FONCTION, donc a l interieur de
  # son `eval` les positionnels sont ceux de la fonction, pas ceux du script. Ma premiere
  # version lisait les arguments de `chk` en croyant lire les colonnes -- et sortait sur
  # « $3: unbound variable », ce qui ne ressemble pas du tout a la cause.
  L=$(ligne_de "$T_J")
  COL_MAT=$(printf '%s' "$L" | cut -d" " -f1)
  COL_MED=$(printf '%s' "$L" | cut -d" " -f2)
  COL_NUL=$(printf '%s' "$L" | cut -d" " -f3)
  chk "la colonne matiere est la matiere" '[ "$COL_MAT" = "7/10" ]'
  chk "la colonne mediane est la MEDIANE" '[ "$COL_MED" = 44 ]'
  chk "... et pas le compte de blocs absents" '[ "$COL_MED" != 3 ]'
  chk "la colonne nulles est le compte de nuls" '[ "$COL_NUL" = 2 ]'
  chk "un JSON illisible ne fait pas tomber la campagne" \
      '[ "$(ligne_de /inexistant)" = "? ? ? ?" ]'
  rm -f "$T_J"
  # ⚠⚠ Le profil de profondeur est la seule mesure qui tranche, et il est OPTIONNEL parce
  # qu il coute un rendu par pas -- les deux colonnes bon marche, elles, ne coutent qu une
  # requete et ne tranchent rien. Delegue, jamais recopie.
  chk "le profil est delegue au profileur" \
      'grep -q "profiler_une_surface.sh" "$ROOT/tools/portee_tangentielle.sh"'
  chk "... et le moteur de rendu n est PAS invoque ici" \
      '! grep -q "vc_render""_tifxyz" "$ROOT/tools/portee_tangentielle.sh"'
  chk "le rendu est opt-in" 'grep -q "RENDRE:-0" "$ROOT/tools/portee_tangentielle.sh"'
  chk "le resultat part dans un JSON" 'grep -q "portee_tangentielle.json" "$ROOT/tools/portee_tangentielle.sh"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

SOURCE="${SOURCE:?SOURCE requis — un tifxyz dont on sait qu il suit une feuille}"
DEST="${DEST:-$ROOT/data/portee_tangentielle}"
JSON="${JSON:-$ROOT/docs/portee_tangentielle.json}"
SONDES="${SONDES:-12}"
PAS_DEFAUT="0 1 2 5 10 20 50"
PAS="${*:-$PAS_DEFAUT}"

mkdir -p "$DEST"
echo "[" > "$JSON.tmp"
PREMIER=1
# ⚠⚠ LA COLONNE QUI DECIDE EST « mediane », PAS « matiere ». Premiere version de cette
# campagne : elle ne rapportait que la part de points dont le BLOC contient de la matiere, et
# a rendu 9/10 a 0 µm comme a 2,4 mm -- une reponse identique aux sept distances, donc une
# mesure qui ne mesure rien. Un bloc fait 128 voxels de cote (307 µm) et les feuilles sont a
# 10-20 µm : a l interieur d un rouleau, presque tout bloc contient du papyrus. Ce qui
# discrimine est la valeur AU POINT.
printf '%6s %10s %10s %10s %9s\n' "pas" "voxels" "matière" "médiane" "nulles"
for K in $PAS; do
  D="$DEST/pas_$K"
  if [ ! -f "$D/meta.json" ]; then
    uv run --project "$ROOT" python "$ROOT/analysis/src/projeter_tangentiel.py" \
        "$SOURCE" --dest "$D" --pas "$K" > "$D.log" 2>&1 || { echo "  ⚠ projection $K échouée"; continue; }
  fi
  VOX=$(python3 -c "
import json;print(round(json.load(open('$D/meta.json'))['pas_voxels'],1))" 2>/dev/null)
  R="$DEST/mesure_$K.json"
  uv run --project "$ROOT" python "$ROOT/analysis/src/matiere_au_point.py" \
      --maillage "$D" --niveau 0 --balayer --combien "$SONDES" --json "$R" > "$D.mesure" 2>&1
  # ⚠⚠ LE PROFIL DE PROFONDEUR EST LA SEULE MESURE QUI TRANCHE, et il coûte un rendu par pas.
  # Les deux colonnes bon marché ci-dessus rendent le même chiffre de 0 µm à 2,4 mm : un bloc
  # zarr fait 307 µm quand les feuilles sont à 10-20 µm, et un voxel isolé d un rouleau
  # comprimé lit un gris moyen presque partout. Ce qui distingue « sur la feuille » de « entre
  # deux spires » est la traversée air → papyrus → air, donc le profil.
  #
  # ⚠ Le rendu est DELEGUE a `profiler_une_surface.sh` : il porte l invocation du moteur et le
  # piege d unites de la pyramide, et une seconde copie serait libre d en diverger.
  if [ "${RENDRE:-0}" = 1 ]; then
    W="$DEST/profil_$K"
    if [ ! -s "$W/verdict.json" ]; then
      GARDER_RENDU=0 PLAT="$D" NIVEAU="${NIVEAU_RENDU:-0}" FENETRES_BASE="${FENETRES:-41}" \
        UM_BASE="${UM_BASE:-2.4}" DEST="$W" ETIQUETTE="portee_$K" \
        JSON="$W/verdict.json" "$ROOT/tools/profiler_une_surface.sh" \
        > "$W.profil.log" 2>&1 || echo "   ⚠ profil du pas $K abandonné"
    fi
  fi
  LIGNE=$(ligne_de "$R")
  set -- $LIGNE
  printf '%6s %10s %10s %10s\n' "$K" "${VOX:-?}" "${1:-?}" "${2:-?}"
  [ "$PREMIER" = 1 ] || echo "," >> "$JSON.tmp"
  PREMIER=0
  printf '{"pas": %s, "pas_voxels": %s, "matiere": "%s", "valeur_mediane": %s, "valeurs_nulles": %s, "part": %s}' \
      "$K" "${VOX:-0}" "${1:-0/0}" "${2:-null}" "${3:-0}" "${4:-0}" >> "$JSON.tmp"
done
echo "]" >> "$JSON.tmp"
mv "$JSON.tmp" "$JSON"
echo "écrit : $JSON"
