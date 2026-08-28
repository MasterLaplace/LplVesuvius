#!/bin/bash
# LE PREMIER JEU DE TEST ETIQUETE DE CE DEPOT.
#
# ⚠⚠ POURQUOI CETTE CAMPAGNE EXISTE. Tous les controles positifs de ce depot sont des
# rendus PUBLIES -- `ink_segment_complet.npy` est ce que quelqu'un d'autre a juge lisible et
# a pris la peine de rendre, pas une verite. `09` §2 reclame un temoin positif « dont le texte
# est publie et lu », et on s'en est approche sans jamais avoir de LABELS.
#
# ⭐⭐⭐ Les fragments en ont. `Frag1` publie, alignes sur ses 65 couches de surface :
# `inklabels.png` (binaire, 18,3 % du papyrus), `mask.png` et `ir.png`. C'est le jeu du
# concours de detection d'encre, et il permet une chose que ce depot n'a jamais faite :
# mesurer l'AUC de NOTRE chaine contre une verite independante de tout modele.
#
# ⚠⚠⚠ LA FENETRE EST CHOISIE SANS REGARDER LES LABELS. Prendre la region la plus riche en
# encre flatterait l'AUC par construction -- c'est le meme defaut que choisir un seuil pour
# que le tirage du jour passe. Le critere est la COUVERTURE DE PAPYRUS, lue dans `mask.png`,
# et la part d'encre que la fenetre porte est RAPPORTEE plutot que choisie.
#
# ⚠ Ce que ca ne dit pas : si `Frag1` etait dans l'entrainement du modele. Le modele est
# `timesformer_GP_scroll1`, entraine sur les etiquettes du Grand Prize 2023 (Scroll 1), et
# les fragments sont le jeu du concours ANTERIEUR -- donc probablement hors entrainement,
# mais on ne peut pas le verifier depuis ici, et une AUC haute sur du vu ne voudrait rien
# dire. C'est ecrit ici pour que personne ne lise le chiffre sans cette reserve.
#
#   ./src/campagnes/campagne_frag1_verite_terrain.sh
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
COUCHES=${COUCHES:-$ROOT/data/couches/frag1_54keV}
LABELS=${LABELS:-$ROOT/data/frag1/labels}
MODELE=${MODELE:-$ROOT/data/models/timesformer_GP_scroll1}
COTE=${COTE:-1024}
PAS=${PAS:-21}
FILS=${FILS:-16}
DEPART=${DEPART:-0}
SORTIE=$ROOT/data/out/ink_frag1_54keV.npy

[ -d "$COUCHES" ] || { echo "couches absentes : $COUCHES" >&2; exit 2; }
[ -s "$LABELS/inklabels.png" ] || { echo "labels absents : $LABELS" >&2; exit 2; }

# ⚠ La fenetre est choisie par la couverture de papyrus, jamais par l'encre.
LIGNE=$(uv run python "$ROOT/src/encre/fenetre_sur_masque.py" \
          --masque "$LABELS/mask.png" --labels "$LABELS/inklabels.png" --cote "$COTE") || exit 3
echo "$LIGNE"
TOP=$(echo "$LIGNE" | grep -oP 'top=\K[0-9]+')
LEFT=$(echo "$LIGNE" | grep -oP 'left=\K[0-9]+')

if [ ! -s "$SORTIE" ]; then
  echo "== rendu de Frag1, 54 keV, ${COTE}x${COTE} en ($TOP,$LEFT)"
  uv run python "$ROOT/src/xpu/infer_ink.py" "$COUCHES" \
    --model "$MODELE" --start-layer "$DEPART" --threads "$FILS" \
    --top "$TOP" --left "$LEFT" --height "$COTE" --width "$COTE" \
    --stride "$PAS" --out "$SORTIE" 2>&1 \
    | grep --line-buffered -E "encre  min|fenetres|fenêtres|erreur" | sed -u 's/^/  /'
else
  echo "== rendu deja fait"
fi
[ -s "$SORTIE" ] || { echo "rendu absent" >&2; exit 4; }

# ⚠⚠ Les labels sont RECADRES sur la meme fenetre : `evaluate_segment` exige un alignement
# en (0,0), et lui donner l'image entiere le ferait refuser -- correctement.
uv run python "$ROOT/src/encre/fenetre_sur_masque.py" \
  --masque "$LABELS/mask.png" --labels "$LABELS/inklabels.png" --cote "$COTE" \
  --recadrer "$ROOT/data/frag1/labels_fenetre.png" >/dev/null || exit 5

echo
echo "== AUC contre la verite terrain"
uv run python "$ROOT/src/volume/evaluate_segment.py" \
  "$SORTIE" "$ROOT/data/frag1/labels_fenetre.png" --json \
  > "$ROOT/docs/mesures/frag1_verite_terrain.json" || exit 6
uv run python "$ROOT/src/volume/evaluate_segment.py" \
  "$SORTIE" "$ROOT/data/frag1/labels_fenetre.png"
echo "→ docs/mesures/frag1_verite_terrain.json"
