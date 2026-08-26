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
#   ./src/campagnes/campagne_temoin_negatif.sh
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/temoin_negatif}
STRIDE=${STRIDE:-8}
COTE=${COTE:-1100}
mkdir -p "$DEST"

# ⚠⚠ LES FENETRES SONT DECLAREES UNE FOIS. Elles servent DEUX fois -- a l'inference, et a
# la description de ce que le modele a recu (le controle du controle, sans lequel deux
# sorties identiques ont une explication ennuyeuse indistinguable de la conclusion). Deux
# litteraux qui doivent s'accorder finissent par ne plus s'accorder, et le desaccord serait
# invisible : la description parlerait d'une fenetre que l'inference n'a pas vue.
#
# couches officielles : 1200x1200, 31 couches, surface a la 15 -> 26 couches centrees = 2..27
POS_COUCHES="$ROOT/data/couches/PHerc1447_20250702235910"
POS_TOP=50 ; POS_LEFT=50 ; POS_DEPART=2
# notre trace : 5641x5721, 41 couches, surface a la 20 -> 26 couches centrees = 7..32
NEG_COUCHES="$ROOT/data/leur_graine/rendu_41"
NEG_TOP=2270 ; NEG_LEFT=2310 ; NEG_DEPART=7

MODELE="$ROOT/data/models/timesformer_GP_scroll1"

cd "$ROOT/inference_xpu" || exit 2

if [ ! -s "$DEST/sur_sa_feuille.npy" ]; then
  echo "== controle POSITIF — segment officiel, alpha = +0,00"
  uv run python src/infer_ink.py "$POS_COUCHES" \
    --model "$MODELE" --start-layer "$POS_DEPART" \
    --top "$POS_TOP" --left "$POS_LEFT" --height "$COTE" --width "$COTE" \
    --stride "$STRIDE" --device xpu --out "$DEST/sur_sa_feuille.npy" || exit 3
else
  echo "== controle POSITIF deja fait"
fi

if [ ! -s "$DEST/en_travers.npy" ]; then
  echo "== controle NEGATIF — notre trace, alpha = +1,01, aucune feuille a portee"
  uv run python src/infer_ink.py "$NEG_COUCHES" \
    --model "$MODELE" --start-layer "$NEG_DEPART" \
    --top "$NEG_TOP" --left "$NEG_LEFT" --height "$COTE" --width "$COTE" \
    --stride "$STRIDE" --device xpu --out "$DEST/en_travers.npy" || exit 3
else
  echo "== controle NEGATIF deja fait"
fi

# ⚠ Tournait depuis `inference/` (l'environnement temoin CPU) jusqu'au 2026-08-25 : la
# racine porte PIL, numcodecs, numpy, scipy et tifffile, donc STRICTEMENT plus. `inference/`
# reste ce qu'il declare etre -- le temoin CPU du ×4,5 XPU -- et n'est plus emprunte pour
# des figures, ce qui evite de garder chaud un venv de 2,5 Gio pour du dessin.
cd "$ROOT" || exit 2
uv run python "$ROOT/src/encre/temoin_negatif.py" \
  --positif "$DEST/sur_sa_feuille.npy" --negatif "$DEST/en_travers.npy" \
  --entree-positif "$POS_COUCHES" --fenetre-positif "$POS_TOP" "$POS_LEFT" "$POS_DEPART" \
  --entree-negatif "$NEG_COUCHES" --fenetre-negatif "$NEG_TOP" "$NEG_LEFT" "$NEG_DEPART" \
  --cote "$COTE" --json "$ROOT/docs/mesures/temoin_negatif.json" || exit 4

uv run python "$ROOT/src/figures/figure_temoin_negatif.py" \
  --json "$ROOT/docs/mesures/temoin_negatif.json" \
  --positif "$DEST/sur_sa_feuille.npy" --negatif "$DEST/en_travers.npy" \
  --sortie "$ROOT/docs/images/46_temoin_negatif.png"
