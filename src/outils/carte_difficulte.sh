#!/bin/bash
# Ecart entre spires sur les 13 rouleaux ELIGIBLES au Grand Prize 2027, plus un temoin.
#
# ⚠⚠ POURQUOI CETTE MESURE EXISTE. Ces 13 rouleaux n'ont AUCUNE trace publiee -- c'est
# tout l'objet du prix. Nos autres instruments jugent une trace ; ici il n'y en a pas.
# Ce qui se mesure quand meme, c'est ce que `docs/00` §1 nomme comme LA difficulte :
# « deux spires voisines sont a 300 µm ; une feuille fait 40 µm ; la ou le rouleau est
# comprime, cet ecart tombe a zero ».
#
# ⚠ Les 13 partagent la MEME prediction de surface (`m7`, `th0.2`, meme date
# d'entrainement), donc la comparaison entre eux ne melange pas les modeles. Le temoin
# est PHercParis4 -- un rouleau qu'on a su derouler ET lire -- avec la meme prediction.
#
# ⚠ Taille de voxel par rouleau, lue sur la page des prix : 8,640 µm pour 268/800/1218/
# 1447, 9,362 µm pour les neuf autres. Elle n'est PAS devinable depuis le nom du .zarr,
# et se tromper dessus rendrait des micrometres faux d'un facteur 1,08.
set -u
cd "$(dirname "$0")/../.." || exit 2
OUT=${1:-docs/carte_difficulte}
mkdir -p "$OUT"
mesure() {  # rouleau  voxel  cle
  local f="../$OUT/$1.json"
  [ -s "$f" ] && { echo "  $1 deja fait"; return; }
  uv run python src/nappe/espacement_spires.py "$3" \
      --level 1 --voxel-um "$2" --chunks 27 --out "$f" 2>&1 \
      | grep -E "niveau|chunks avec|0\.50" | sed "s/^/  [$1] /"
}
while read -r k; do
  s=$(cut -d/ -f1 <<<"$k")
  case "$s" in
    PHerc0268|PHerc0800|PHerc1218|PHerc1447) v=8.640 ;;
    *) v=9.362 ;;
  esac
  echo "=== $s (voxel $v µm) ==="
  mesure "$s" "$v" "$k"
done < /tmp/pred_prix.txt
echo "=== TEMOIN : PHercParis4, deroule et LU ==="
mesure PHercParis4 9.600 \
  "PHercParis4/representations/predictions/surfaces/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr"
echo "termine"
