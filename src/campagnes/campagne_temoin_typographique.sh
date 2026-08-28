#!/bin/bash
# L'EXPERIENCE DECISIVE : le temoin negatif est-il PERIODIQUE ?
#
# ⚠⚠ Pourquoi cette campagne existe. Le resultat de `60` §4 quinquies -- nos quatre cartes
# de `PHerc1447` sont periodiques la ou leurs pixels melanges ne le sont pas, p = 0,0007 --
# repose sur un controle FAIBLE. Melanger les pixels detruit toute structure spatiale, donc
# le test repond « nos cartes sont structurees », ce qui est plus pauvre que « nos cartes
# portent de l'ecriture ».
#
# ⭐⭐ Le controle DUR est un temoin negatif reel : une surface qui n'est pas une feuille
# mais qui garde la texture du bloc. `38` prouve geometriquement qu'aucune feuille n'est a
# portee de `data/leur_graine/rendu_41` (alpha = +1,01). Si cette surface rend AUTANT de
# fenetres periodiques que nos cartes, la periodicite n'est pas une signature d'encre.
#
# ⚠⚠ LA TAILLE N'EST PAS UN CHOIX. `src/encre/fenetres_par_region.py` etablit qu'il faut
# **5128** px de cote pour porter huit fenetres au reglage calibre (reduction 8, fenetre
# 256) -- et non 2100, comme je l'avais d'abord ecrit sur une formule fausse. Les couches du
# temoin font 5641 x 5721, donc ca tient tout juste.
#
# ⚠⚠ ET LE PAS EST CELUI DE LA CAMPAGNE, pas celui du temoin de `46`. Les cartes auxquelles
# on compare sont rendues au pas 21 ; comparer une carte au pas 8 a des cartes au pas 21
# ferait varier le lissage, donc la periodicite, pour une raison etrangere au papyrus.
#
# ⚠ La region part de l'origine et couvre presque toute la couche : la preuve geometrique de
# `38` porte sur la TRACE, pas sur un carre particulier de celle-ci, donc toute la surface
# rendue est un temoin negatif valide.
#
#   ./src/campagnes/campagne_temoin_typographique.sh
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
COUCHES=${COUCHES:-$ROOT/data/leur_graine/rendu_41}
MODELE=${MODELE:-$ROOT/data/models/timesformer_GP_scroll1}
DEPART=${DEPART:-7}
COTE=${COTE:-5128}
PAS=${PAS:-21}
FILS=${FILS:-16}
SORTIE=$ROOT/data/temoin_negatif/en_travers_grand.npy

[ -d "$COUCHES" ] || { echo "couches absentes : $COUCHES" >&2; exit 2; }

if [ ! -s "$SORTIE" ]; then
  echo "== temoin NEGATIF, ${COTE}x${COTE}, pas ${PAS} -- assez grand pour huit fenetres"
  uv run python "$ROOT/src/xpu/infer_ink.py" "$COUCHES" \
    --model "$MODELE" --start-layer "$DEPART" --threads "$FILS" \
    --top 0 --left 0 --height "$COTE" --width "$COTE" \
    --stride "$PAS" --out "$SORTIE" 2>&1 \
    | grep --line-buffered -E "encre  min|fenetres|fenêtres|erreur" | sed -u 's/^/  /'
else
  echo "== temoin NEGATIF grand deja rendu"
fi

[ -s "$SORTIE" ] || { echo "rendu absent, on ne teste rien" >&2; exit 3; }

echo
echo "== le temoin negatif contre son propre melange, reglage calibre"
# ⚠ Aucun `--temoin` ici : c'est le sujet de la mesure, pas un temoin a ecarter du groupe.
uv run python "$ROOT/src/encre/typographie.py" --npy "$SORTIE" \
    --reduire 8 --taille-fenetre 256 --controle-melange \
    --json "$ROOT/docs/mesures/typographie_du_temoin_negatif.json"
