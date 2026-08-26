#!/usr/bin/env bash
# Rendre une video pedagogique, l assembler, et en EXTRAIRE des vignettes.
#
# ⚠⚠ La derniere etape n est pas un confort : une video qu on ne REGARDE pas est une video
# qu on ne peut pas controler. Une legende posee par-dessus une figure, un objet qui sort du
# cadre, un texte illisible -- rien de tout cela n apparait a la relecture du code, et tout
# saute aux yeux sur une vignette. Le premier rendu de la scene 2 avait sa legende plantee
# au milieu du dessin ; c est la vignette qui l a dit.
#
# ⚠ Les scenes sont rendues UNE PAR UNE puis concatenees, et pas ecrites en une seule classe
# geante : une scene qui casse ne doit pas emporter les autres, et on veut pouvoir en
# rejouer une seule.
#
# Usage : src/apprendre/rendre.sh <fichier_de_scenes.py> [qualite]
set -uo pipefail
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$ICI/.venv/bin/python"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "l environnement manim existe" '[ -x "$PY" ]'
  chk "manim est importable" '"$PY" -c "import manim" 2>/dev/null'
  chk "ffmpeg est la" 'command -v ffmpeg >/dev/null'
  # ⚠ Les scenes sont A PLAT dans `src/apprendre/` depuis le repli du 2026-08-26 :
# chaque famille de `src/` est plate, et un sous-dossier ici aurait ete la seule
# exception. Elles se reconnaissent a leur numero d ordre, qui est aussi celui
# dans lequel les videos se regardent.
  chk "au moins un fichier de scenes" 'ls "$ICI"/0*.py >/dev/null 2>&1'
  # ⚠⚠ Toute legende doit passer par `legende()`, qui l ancre en bas. Un `to_edge(DOWN)`
  # ecrit a la main est un endroit de plus ou l oubli est possible -- et l oubli ne se voit
  # qu au rendu. Le motif est coupe en deux : une sonde qui scanne des fichiers ne doit pas
  # se matcher elle-meme (piege 67).
  # ⚠ Le motif vise les appels avec une CHAINE LITTERALE : la definition du helper
  # `legende()` fait legitimement `phrase(txt, ...).to_edge(DOWN)` sur une variable, et
  # une premiere version de cette sonde l attrapait -- elle signalait donc l endroit meme
  # ou la regle est appliquee. Une sonde doit viser l usage, pas la definition.
  chk "aucune scene ne pose de legende a la main" \
      '! grep -rnE "phrase\\(\"[^\"]*\".*\\.to_""edge\\(DOWN" "$ICI"/0*.py'
  chk "les vignettes sont extraites" 'grep -q "vignettes" "$ICI/rendre.sh"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

FICHIER="${1:?fichier de scenes}"
# ⚠ Le repli cherche a cote du script, pas dans un sous-dossier `scenes/` : il a ete
# APLATI au repli du 2026-08-26, donc l ancien repli ne pouvait plus rien trouver et
# c etait le seul confort de ce script -- `rendre.sh 03_le_mur_invisible.py` depuis
# la racine tombait sur « scenes introuvables » alors que le fichier est la.
[ -f "$FICHIER" ] || FICHIER="$ICI/$(basename "$FICHIER")"
[ -f "$FICHIER" ] || { echo "refus : scenes introuvables — $1" >&2; exit 2; }
QUALITE="${QUALITE:-${2:-l}}"     # l = 480p rapide, h = 1080p, k = 4K
BASE=$(basename "$FICHIER" .py)
SORTIE="$ICI/videos"
VIGNETTES="$ICI/vignettes/$BASE"
mkdir -p "$SORTIE" "$VIGNETTES"

# ⚠ L ordre des scenes est celui du FICHIER, pas l ordre alphabetique : une video est une
# progression, et trier par nom la melangerait des qu une scene s appellerait « Alpha ».
mapfile -t SCENES < <(grep -oE "^class ([A-Za-z0-9_]+)\(" "$FICHIER" | sed 's/^class //; s/($//')
[ "${#SCENES[@]}" -gt 0 ] || { echo "refus : aucune classe de scene dans $FICHIER" >&2; exit 2; }
echo "== ${#SCENES[@]} scène(s) : ${SCENES[*]}"

LISTE="$SORTIE/.$BASE.txt"; : > "$LISTE"
for S in "${SCENES[@]}"; do
  echo "== rendu $S"
  if ! ( cd "$ICI" && "$PY" -m manim "-q$QUALITE" --disable_caching "$FICHIER" "$S" ) \
        > "$SORTIE/.$S.log" 2>&1; then
    echo "   ⚠ ÉCHEC — voir $SORTIE/.$S.log"; tail -3 "$SORTIE/.$S.log"; exit 3
  fi
  M=$(find "$ICI/media" -name "$S.mp4" -newermt '-10 minutes' | head -1)
  [ -n "$M" ] || { echo "   ⚠ vidéo introuvable pour $S"; exit 3; }
  echo "file '$M'" >> "$LISTE"
done

FINAL="$SORTIE/$BASE.mp4"
ffmpeg -loglevel error -y -f concat -safe 0 -i "$LISTE" -c copy "$FINAL" \
  || { echo "refus : concaténation échouée" >&2; exit 3; }
DUREE=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL")
echo "== assemblé : $FINAL  (${DUREE%.*} s)"

# ⚠⚠ Les VIGNETTES, pour pouvoir REGARDER sans lancer de lecteur. Une toutes les trois
# secondes : assez dense pour attraper une legende mal placee, assez rare pour qu on les
# parcoure toutes.
rm -f "$VIGNETTES"/*.png
ffmpeg -loglevel error -y -i "$FINAL" -vf "fps=1/3,scale=480:-1" "$VIGNETTES/v_%02d.png"
echo "== $(ls "$VIGNETTES" | wc -l) vignettes dans $VIGNETTES"
