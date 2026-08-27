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
MANQUANTS=""
mesure() {  # rouleau  voxel  cle
  local f="$OUT/$1.json"
  [ -s "$f" ] && { echo "  $1 deja fait"; return; }
  uv run python src/nappe/espacement_spires.py "$3" \
      --level 1 --voxel-um "$2" --chunks 27 --out "$f" 2>&1 \
      | grep -E "niveau|chunks avec|0\.50" | sed "s/^/  [$1] /"
}
# ⚠⚠ La liste des cles ETAIT lue dans `/tmp/pred_prix.txt`, un fichier que rien de ce depot
# ne produit et qui n'existe plus. La commande « Reproduire » de `16` etait donc MORTE :
# elle sortait sur « No such file » avant la premiere mesure. Meme classe de panne que
# l'outil d'inference du 2026-08-27 -- un chemin publie qu'on ne peut plus emprunter.
#
# ⭐ La cle et la taille de voxel se DERIVENT desormais, par `apparier_volumes.py
# --pour-campagne`, qui apparie surface et volume par identite de scan et lit le voxel dans
# le nom du volume. Plus de table de voxels tenue a la main -- elle etait juste, et elle
# etait une seconde source de verite.
for s in $(uv run python -c "
import sys; sys.path.insert(0, 'src/volume')
import apparier_volumes as av
print(' '.join(r for r in av.ROULEAUX if r != 'PHerc0139'))"); do
  # ⚠⚠ `--voxel-um 9.0` (tolerance 1,0) demande le scan de la COHORTE : les treize sont a
  # 8,640 ou 9,362 µm, et `PHerc1203` publie EN PLUS un scan a 2,403 µm. Sans ce choix il
  # est refuse comme ambigu et disparait du tableau -- ce qui est arrive au premier run, en
  # silence, avec un « termine » a la fin. La raison est celle qu'ecrit `choisir` : un
  # treizieme rouleau pris a une autre resolution n'est plus comparable aux douze autres.
  ligne=$(uv run python src/volume/apparier_volumes.py --pour-campagne "$s" --voxel-um 9.0 2>/dev/null) || {
    echo "=== $s : appariement non determine, saute ==="; MANQUANTS="$MANQUANTS $s"; continue; }
  k=$(cut -d' ' -f1 <<<"$ligne")
  v=$(cut -d' ' -f3 <<<"$ligne")
  echo "=== $s (voxel $v µm) ==="
  mesure "$s" "$v" "$k"
done
echo "=== TEMOIN : PHercParis4, deroule et LU ==="
mesure PHercParis4 9.600 \
  "PHercParis4/representations/predictions/surfaces/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr"
# ⚠⚠ Une campagne qui saute un rouleau et imprime « termine » se lit comme une campagne
# complete. Le compte attendu est celui de la cohorte plus son temoin ; en dessous, on SORT
# non nul et on nomme ce qui manque.
N=$(ls "$OUT"/*.json 2>/dev/null | wc -l)
ATTENDU=$(uv run python -c "
import sys; sys.path.insert(0, 'src/volume')
import apparier_volumes as av
print(len([r for r in av.ROULEAUX if r != 'PHerc0139']) + 1)")
if [ "$N" -lt "$ATTENDU" ]; then
  echo "INCOMPLET : $N artefacts sur $ATTENDU attendus —$MANQUANTS" >&2
  exit 1
fi
echo "termine : $N artefacts sur $ATTENDU"
