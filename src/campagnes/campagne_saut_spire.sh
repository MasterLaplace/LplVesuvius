#!/bin/bash
# Detecteur de saut de spire sur TOUT le corpus PHerc0139, contre les croisements publies.
#
# ⚠⚠ POURQUOI TOUT LE CORPUS. Sur 8 traces, les quatre statistiques vont dans le bon
# sens (rho +0,44 a +0,52) et aucune n'est significative -- a n = 8 seul un rho de 0,85
# est detectable. C'est EXACTEMENT la situation ou les fibres se trouvaient a n = 12
# avec rho +0,330, et ou le signe s'est INVERSE en montant a n = 54. Un trend a n = 8
# n'est pas un resultat, c'est une invitation a mesurer.
#
# A n = 38, la mesure detecte un rho de ~0,44 -- soit exactement l'ordre observe. C'est
# le minimum pour que la reponse, quelle qu'elle soit, veuille dire quelque chose.
set -u
cd "$(dirname "$0")/../.." || exit 2
C="PHerc0139/representations/predictions/lasagna/20260102150214-lasagna-20260419180421-L2/PHerc0139-20260102150214-lasagna-20260724_cos.ome.zarr"
OUT=${1:-docs/saut_spire}
mkdir -p "$OUT"
cd inference_xpu || exit 2
for d in ../data/traces/PHerc0139/*/; do
  seg=$(basename "$d")
  f="../$OUT/$seg.json"
  [ -s "$f" ] && continue
  M=$(ls -d "$d"mesh/*2.399um.tifxyz 2>/dev/null | head -1)
  [ -z "$M" ] && continue
  uv run python ../src/nappe/saut_de_spire.py "$M" "$C" \
      --sample 960 --run 48 --label "$seg" --out "$f" 2>&1 | grep -E "marches|erreur"
done
echo "termine : $(ls "../$OUT"/*.json 2>/dev/null | wc -l) traces"
