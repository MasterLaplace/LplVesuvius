#!/bin/bash
# Reprendre ce qui a ete gele pour liberer la machine (reunion Zoom du 2026-08-18).
#
# ⚠ Les calculs ont ete SIGSTOP, pas tues : ils reprennent a l'identique, sans perdre
# le travail deja fait. Le telechargement, lui, a ete coupe -- il est reprenable par
# conception (`curl --continue-at -`), donc on le relance simplement.
set -u
cd "$(dirname "$0")/../.." || exit 2
n=0
for p in $(pgrep -f 'venv/bin/python3 src/infer_ink|venv/bin/python3 src/excision/fusion_scan'); do
  kill -CONT "$p" && { echo "  repris : PID $p"; n=$((n+1)); }
done
[ "$n" -eq 0 ] && echo "  aucun calcul gele"
# Couches 41 a 64 de Scroll 4 : reprend ou il s'etait arrete.
if [ ! -f data/layers/scroll4_20231111135340/64.tif ]; then
  echo "  relance du telechargement 41-64"
  setsid nohup ./src/outils/fetch_layers.sh \
    "https://dl.ash2txt.org/full-scrolls/Scroll4/PHerc1667.volpkg/paths/20231111135340" \
    data/layers/scroll4_20231111135340 3 41 64 >> docs/fetch_scroll4_haut.log 2>&1 < /dev/null &
fi
# ⚠ La bande B a peut-etre ete perdue : `src/outils/bandes_niveau0.sh` saute ce qui est deja
# fait, donc le relancer est sans risque et sans doublon.
[ -s docs/bande_niveau0_B.json ] || {
  echo "  relance de la bande B niveau 0"
  setsid nohup nice -n 12 ./src/outils/bandes_niveau0.sh >> docs/bandes_niveau0.log 2>&1 < /dev/null &
}
echo "termine"
