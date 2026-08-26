#!/bin/bash
# Separabilite des feuilles sur les 13 rouleaux du Grand Prize, plus des temoins.
#
# ⚠⚠ CE QUE LE CONCOURS NOMME COMME MANQUANT. Le tableau des goulots de
# `2026_open_problems` dit, pour les regions comprimees : « What would help : **scan-
# quality metrics** ». Et il definit le defaut : « some regions lose effective
# **separability** between layers ». C'est exactement ce qu'un d′ mesure.
#
# ⚠ Le temoin decisif est PHerc0139 : il a ete trace ET son titre a ete retrouve, et il
# possede un scan au MEME protocole que les 13 (9,362 µm / 1,2 m / 113 keV). Comparer
# les rouleaux du prix a lui, c'est comparer a scroll tractable a qualite egale.
#   ./src/outils/carte_separabilite.sh docs/carte_separabilite       27    # la carte de `16`
#   ./src/outils/carte_separabilite.sh docs/carte_separabilite_dense 125    # celle que `33` exige
set -u
cd "$(dirname "$0")/../.." || exit 2
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
OUT=${1:-docs/carte_separabilite}
# ⚠ `--chunks` n'est PAS le nombre de fenetres mesurees : le script en tire un pas de
# grille (`round(n^(1/3))+1` par axe), sonde ce cube, et jette les fenetres vides. 27
# donne 4³ = 64 sondes pour 15 a 35 fenetres reellement mesurees.
#
# ⚠⚠ Et cet effectif DECIDE de ce que la carte peut affirmer : `docs/mesures/incertitude_carte.json`
# mesure qu'a 15-35 fenetres AUCUNE des 78 paires de rouleaux n'est separee, et qu'il en
# faut 50 par rouleau pour separer les deux extremes a 80 % de puissance. D'ou ce
# parametre, et d'ou le fait qu'une campagne dense s'ecrit dans SON PROPRE dossier : les
# chiffres publies de `16` doivent rester reproductibles a cote.
SONDES=${2:-27}
mkdir -p "$OUT"
# ⚠⚠ Le temoin est DANS la boucle depuis le 2026-08-20. L'en-tete de ce fichier promettait
# « plus des temoins » depuis le debut et la boucle n'en produisait aucun : le temoin de
# `16` avait ete lance a la main, donc la campagne ne pouvait pas reproduire la comparaison
# qui porte tout son resultat. Une campagne qui ne refait pas son propre temoin ne se
# rejoue pas -- elle se rejoue a moitie, et c'est la moitie qui fixe le zero qui manque.
#
# ⚠ Il porte un prefixe `_TEMOIN_` parce que les depouilleurs le reconnaissent par la : il
# ne doit jamais entrer dans le classement qu'il sert a calibrer.
for s in PHerc0125 PHerc0191 PHerc0211 PHerc0257 PHerc0268 PHerc0358 \
         PHerc0800 PHerc0813 PHerc0826 PHerc1203 PHerc1218 PHerc1447 PHerc1545 \
         _TEMOIN_PHerc0139; do
  f="$OUT/$s.json"
  s=${s#_TEMOIN_}
  [ -s "$f" ] && { echo "  $s deja fait"; continue; }
  # ⚠ Le nom du volume porte la taille de voxel : on la LIT au lieu de la deviner.
  k=$(curl -s --max-time 40 "$B/?list-type=2&prefix=$s/volumes/&delimiter=/" \
      | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep -E '(8\.640|9\.362)um' | head -1)
  [ -z "$k" ] && { echo "  $s : aucun volume au protocole du prix"; continue; }
  v=$(grep -oE '[0-9]+\.[0-9]+um' <<<"$k" | head -1 | tr -d 'um')
  echo "=== $s (voxel $v µm) ==="
  ( cd inference_xpu && uv run python ../src/encre/separabilite_scan.py "${k%/}" \
      --level 1 --voxel-um "$v" --chunks "$SONDES" --out "../$f" 2>&1 \
      | grep -E "grille|chunks mesures|d′" | sed "s/^/  [$s] /" )
done
echo "termine"
