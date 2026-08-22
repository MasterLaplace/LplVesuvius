#!/bin/bash
# M8 — LE TEMOIN NEGATIF QUE LE DOMAINE N'A PAS.
#
# ⚠⚠ Pourquoi cette campagne existe. `32` §4.3 releve que le papier fondateur n'a AUCUN
# controle negatif au sens fort : il rapporte un taux de faux positifs, mais sur des images
# qui contiennent de l'encre partout autour. Il ne mesure jamais ce que le detecteur produit
# sur un substrat dont on SAIT qu'il n'en porte pas. Le temoin parfait etait pourtant dans
# leur scan -- la feuille de papier de support sur laquelle les fragments sont montes -- et
# le nettoyage manuel le supprime.
#
# ⭐⭐ Nous en avons un MEILLEUR, et il est deja mesure. `38` etablit qu'une de nos traces a
# alpha = +1,01 : sa distance a la matiere SUIT la fenetre de rendu, donc il n'y a aucune
# feuille a portee -- la surface est posee EN TRAVERS de l'empilement. Ce n'est pas une
# supposition sur un substrat, c'est une PREUVE GEOMETRIQUE qu'il n'y a pas de face de
# papyrus la. Toute « encre » que le modele y rapporte est donc un faux positif par
# construction.
#
# ⚠ Le controle positif est le segment officiel du MEME rouleau, a alpha = +0,00, rendu par
# le meme outil. Meme volume, meme voxel, meme modele, meme region, meme pas : la seule
# chose qui change est de savoir s'il y a une feuille sous la surface.
#
# ⚠⚠ La region est la MEME des deux cotes (1100 x 1100) parce que les couches officielles
# ne font que 1200 x 1200 : comparer une grande region a une petite ferait varier le nombre
# de fenetres, donc la dispersion, pour une raison etrangere au papyrus.
#
#   ./tools/campagne_temoin_negatif.sh
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/temoin_negatif}
STRIDE=${STRIDE:-8}
COTE=${COTE:-1100}
mkdir -p "$DEST"

cd "$ROOT/inference_xpu" || exit 2

# couches officielles : 1200x1200, 31 couches, surface a la 15 -> 26 couches centrees = 2..27
if [ ! -s "$DEST/sur_sa_feuille.npy" ]; then
  echo "== controle POSITIF — segment officiel, alpha = +0,00"
  uv run python src/infer_ink.py "$ROOT/data/couches/PHerc1447_20250702235910" \
    --model "$ROOT/data/models/timesformer_GP_scroll1" --start-layer 2 \
    --top 50 --left 50 --height "$COTE" --width "$COTE" --stride "$STRIDE" \
    --device xpu --out "$DEST/sur_sa_feuille.npy" || exit 3
else
  echo "== controle POSITIF deja fait"
fi

# notre trace : 5641x5721, 41 couches, surface a la 20 -> 26 couches centrees = 7..32
if [ ! -s "$DEST/en_travers.npy" ]; then
  echo "== controle NEGATIF — notre trace, alpha = +1,01, aucune feuille a portee"
  uv run python src/infer_ink.py "$ROOT/data/leur_graine/rendu_41" \
    --model "$ROOT/data/models/timesformer_GP_scroll1" --start-layer 7 \
    --top 2270 --left 2310 --height "$COTE" --width "$COTE" --stride "$STRIDE" \
    --device xpu --out "$DEST/en_travers.npy" || exit 3
else
  echo "== controle NEGATIF deja fait"
fi

cd "$ROOT/inference" || exit 2
uv run python "$ROOT/analysis/src/temoin_negatif.py" \
  --positif "$DEST/sur_sa_feuille.npy" --negatif "$DEST/en_travers.npy" \
  --json "$ROOT/docs/temoin_negatif.json"
