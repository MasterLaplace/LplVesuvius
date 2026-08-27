#!/bin/bash
# Rendre l'encre sur TOUTES les surfaces publiees d'un rouleau du prix, et mesurer leur
# signature typographique.
#
# ⚠⚠ POURQUOI CETTE CAMPAGNE EXISTE. `60` a montre que le modele n'etait pas inerte sur
# `PHerc1447` : il recevait du noir. Une fois l'echelle corrigee, la surface publiee du
# premier segment rend **deux** fenetres, toutes deux periodiques a un interligne plausible,
# et le controle par melange dit que c'est de la structure. Mais DEUX fenetres, c'est un
# tirage a pile ou face -- `33` a construit tout un document sur le fait qu'on ne classe pas
# treize rouleaux avec quinze fenetres.
#
# ⭐ Le seul moyen d'augmenter n est de rendre PLUS DE SURFACE. Ce rouleau en publie quatre,
# et une seule a ete rendue.
#
# ⚠ Le pont `zarr_vers_couches.py` ecrit des couches **uint8**, et c'est exactement le type
# qui a fonde le faux negatif. Le lecteur normalise desormais par le plafond du TYPE, et il
# REFUSE une pile dont le maximum tombe sous 1/64 de la pleine echelle -- donc si le bug
# revenait, cette campagne s'arreterait au lieu de produire des cartes muettes.
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
LISTE=${1:-docs/mesures/volumes_surface_PHerc1447.txt}
COUCHE_DEPART=${COUCHE_DEPART:-3}
# ⚠⚠ LE NOMBRE DE FILS EST UN PARAMETRE, et il faut le dire : `infer_ink` en prend **16**
# par defaut, ce qui est juste pour un seul rendu et desastreux pour deux. Mesure du
# 2026-08-27 : deux campagnes lancees ensemble sur une machine a 22 coeurs ont demande 32
# fils, et ont consomme 26 h et 19 h de CPU pour 2 h de temps reel chacune -- l'essentiel
# parti en contention. Deux rendus lances en meme temps finissent PLUS TARD que les memes
# lances l'un apres l'autre. Poser `FILS` quand une autre campagne tourne.
FILS=${FILS:-16}
MODELE="$ROOT/data/models/timesformer_GP_scroll1"

[ -s "$LISTE" ] || { echo "liste absente : $LISTE" >&2; exit 2; }
CARTES=""
while IFS=$'\t' read -r seg cle _; do
  [ -n "$seg" ] || continue
  out="$ROOT/data/out/ink_${seg%%-*}.npy"
  couches="$ROOT/data/couches/1447_${seg%%-*}"
  CARTES="$CARTES $out"
  [ -s "$out" ] && { echo "== $seg : deja rendu"; continue; }

  # ⚠ La taille se LIT dans le .zarray, jamais devinee : deux segments d'un meme rouleau
  # n'ont pas la meme etendue, et une fenetre plus grande que la surface rend des chunks
  # absents -- ce qui se lit ensuite comme des trous dans la carte.
  forme=$(curl -s --max-time 60 \
      "https://vesuvius-challenge-open-data.s3.amazonaws.com/$cle/0/.zarray" \
      | python3 -c "import json,sys; print(*json.load(sys.stdin)['shape'])" 2>/dev/null) || forme=""
  [ -n "$forme" ] || { echo "== $seg : .zarray illisible, saute" >&2; continue; }
  set -- $forme
  echo "== $seg : $2 x $3 sur $1 couches"

  if [ ! -d "$couches" ]; then
    uv run python src/volume/zarr_vers_couches.py "$cle" --sortie "$couches" \
        --top 0 --left 0 --hauteur "$2" --largeur "$3" || { echo "  pont echoue" >&2; continue; }
  fi
  uv run python src/xpu/infer_ink.py "$couches" --model "$MODELE" \
      --start-layer "$COUCHE_DEPART" --threads "$FILS" \
      --top 0 --left 0 --height "$2" --width "$3" \
      --out "$out" 2>&1 | grep -E "encre  min|fenetres|erreur" | sed 's/^/  /'
done < "$LISTE"

# ⚠⚠ La signature typographique est mesuree au reglage CALIBRE sur une carte dont on SAIT
# qu'elle porte du texte (`data/out/ink_segment_complet.npy`, Scroll 1) : reduction 8,
# fenetre 256. A reduction 4 -- le defaut -- cette meme carte rend 0 % de fenetres
# periodiques, donc le defaut ne peut RIEN conclure sur les notres.
echo
echo "== signature typographique, reglage calibre sur Scroll 1 =="
# shellcheck disable=SC2086
uv run python src/encre/typographie.py --npy $ROOT/data/out/ink_segment_complet.npy $CARTES \
    --reduire 8 --taille-fenetre 256 --controle-melange \
    --json docs/mesures/typographie_de_nos_cartes.json
