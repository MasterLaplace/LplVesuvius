#!/bin/bash
# Assembler un `direction_fields` local pour `vc_grow_seg_from_seed`.
#
# ⚠⚠ Le contrat n'est documente nulle part ; il a ete DERIVE des exceptions du binaire :
#     "direction_fields": [{"zarr": "<base>", "dir": "normal", "scale": 2.0}]
# et l'outil ouvre alors `<base>/x/2`, `<base>/y/2`, `<base>/z/2`. Directions valides :
# `normal`, `horizontal`, `vertical`.
#
# ⚠⚠ L'encodage des uint8 n'est pas documente non plus. Il est MESURE :
# `analysis/src/valider_champ_normal.py` compare le champ publie a la normale que notre
# tenseur de structure calcule sur la prediction, et balaye l'hypothese. Le zero tombe
# a **128** (6,6° d'ecart) contre 37 a 53° pour toute autre valeur -- un pic net, pas un
# plateau. Donc la composante `z`, que le rouleau ne publie pas, se remplit de **128**
# et non de 0 : zero voudrait dire -1, c'est-a-dire une normale verticale partout.
#
# ⭐ On ne telecharge PAS le rouleau : un zarr rend sa valeur de remplissage pour les
# chunks absents, donc seules les tuiles autour de la trace sont recuperees. Le reste du
# volume reste « pas de contrainte ».
#
# ⚠ Reprenable : un chunk deja present est saute. Un 404 est NORMAL (hors du rouleau) et
# n'est pas une erreur -- il est compte a part.
set -u
cd "$(dirname "$0")/.." || exit 2
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"

usage() { echo "usage: $0 <lasagna_prefix> <rouleau> <dest> <niveau> <x0> <x1> <y0> <y1> <z0> <z1>"; echo "  bornes en voxels DU NIVEAU demande"; exit 2; }
[ $# -eq 10 ] || usage
LAS=${1%/}; ROU=$2; DEST=$3; NIV=$4; X0=$5; X1=$6; Y0=$7; Y1=$8; Z0=$9; Z1=${10}
FILS=${FILS:-16}

for AXE in x y z; do mkdir -p "$DEST/$AXE/$NIV"; done

# Le .zarray de reference vient de nx : meme forme, meme decoupe, meme compresseur.
REF=$(curl -sf --max-time 60 "$B/$LAS/${ROU}_nx.ome.zarr/$NIV/.zarray") || { echo "pas de .zarray au niveau $NIV"; exit 1; }
echo "$REF" > "$DEST/x/$NIV/.zarray"
echo "$REF" > "$DEST/y/$NIV/.zarray"
# ⚠ La composante z n'existe pas cote publication. On la fabrique VIDE avec fill_value 128,
# ce qui vaut exactement zero une fois decode -- et ne coute pas un octet.
python3 -c "
import json,sys
m=json.loads(sys.stdin.read()); m['fill_value']=128; m['compressor']=None
json.dump(m, open('$DEST/z/$NIV/.zarray','w'))" <<< "$REF"

read -r CZ CY CX <<<"$(python3 -c "
import json
m=json.loads(open('$DEST/x/$NIV/.zarray').read()); print(*m['chunks'])")"
SEP=$(python3 -c "
import json
print(json.loads(open('$DEST/x/$NIV/.zarray').read()).get('dimension_separator','.'))")

liste=$(python3 -c "
import sys
cz,cy,cx=$CZ,$CY,$CX
for z in range($Z0//cz, $Z1//cz+1):
    for y in range($Y0//cy, $Y1//cy+1):
        for x in range($X0//cx, $X1//cx+1):
            print(z,y,x)")
N=$(wc -l <<<"$liste")
echo "$N chunks par composante · chunks ${CZ}x${CY}x${CX} · separateur « $SEP »"

for C in nx ny; do
  AXE=${C#n}
  echo "== $C -> $DEST/$AXE/$NIV"
  echo "$liste" | while read -r z y x; do
    K="$z$SEP$y$SEP$x"
    F="$DEST/$AXE/$NIV/$(echo "$K" | tr '/' '_')"
    [ "$SEP" = "/" ] && { F="$DEST/$AXE/$NIV/$z/$y/$x"; mkdir -p "$(dirname "$F")"; }
    [ -s "$F" ] && continue
    echo "$B/$LAS/${ROU}_${C}.ome.zarr/$NIV/$K -o $F"
  done | xargs -P "$FILS" -L1 curl -sf --max-time 120 2>/dev/null
  PRESENTS=$(find "$DEST/$AXE/$NIV" -type f ! -name ".zarray" -size +0c | wc -l)
  echo "   $PRESENTS chunks presents ($(du -sh "$DEST/$AXE/$NIV" | cut -f1))"
done
echo "champ pret : $DEST  (z est vide, fill_value 128 = zero)"
