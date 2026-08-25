#!/bin/bash
# Verifier qu'un lot de volumes Zarr est bien dans la forme que notre lecteur suppose.
#
# ⚠⚠ Ne d'un bug qui n'aurait PAS leve d'erreur. `dimension_separator` vaut `/` sur les
# volumes de Scroll 1 et `.` sur au moins un de PHerc1667, et certains chunks sont
# compresses en blosc. Un lecteur qui code `/` en dur et ignore le compresseur ne plante
# pas : il recoit des 404, les compte en « chunk vide », et rapporte un segment
# DEPOURVU DE MATIERE. C'est-a-dire un resultat, faux, sans le moindre signe.
#
# Ce script existe pour que la question « nos mesures portaient-elles sur des volumes
# lisibles ? » ait une reponse, et pas une presomption.
set -u
cd "$(dirname "$0")/../.." || exit 2
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
LISTE=${1:?usage: verifier_zarr.sh <fichier de cles zarr>}
n=0; sep_autre=0; compresse=0
while read -r z; do
  [ -z "$z" ] && continue
  n=$((n+1))
  m=$(curl -s --max-time 25 "$B/$z/0/.zarray" | tr -d ' \n')
  s=$(grep -o '"dimension_separator":"[^"]*"' <<<"$m" | cut -d'"' -f4)
  c=$(grep -o '"compressor":{[^}]*}' <<<"$m")
  [ "${s:-.}" != "/" ] && { sep_autre=$((sep_autre+1)); echo "  separateur '${s}' : $z"; }
  [ -n "$c" ] && { compresse=$((compresse+1)); echo "  compresse $c : $z"; }
done < "$LISTE"
echo "$n volumes verifies : $sep_autre a separateur non-'/', $compresse compresses"
