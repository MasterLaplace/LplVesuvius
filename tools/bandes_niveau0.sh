#!/bin/bash
# Deux bandes au NIVEAU 0, loin du site migrant, pour trancher une question que le
# crible niveau 2 ne peut pas trancher.
#
# ⚠⚠ POURQUOI PAS LE CRIBLE. Mesure : dans la MEME plage de z, le niveau 0 trouve le
# site migrant a 77-88 % du tour et le niveau 2 ne trouve rien entre 74 % et 88 %. Le
# crible n'est donc pas seulement moins sensible, il regarde AILLEURS -- ses 18 % de
# colocation portent sur une autre population de sites. Toute question sur la
# migration doit se poser au niveau 0.
#
# ⚠ Bandes de 9 coupes a 100 voxels (0,79 mm), la geometrie exacte ou la migration a
# ete vue : changer le pas changerait ce qu'une piste peut suivre.
set -u
VOL=${VOL:-s3://vesuvius-challenge-open-data/PHerc0172/volumes/20241024131839-7.910um-53keV-masked.zarr}
cd /home/masterlaplace/LplVesuvius/experiments || exit 2
# ⚠⚠ Les bandes couvrent la HAUTEUR du rouleau (z 1336 → 12598), et l'une d'elles (E)
# encadre le site migrant du §11 EXPRÈS : c'est le témoin positif. Une méthode qui ne
# retrouverait pas la migration là où elle a déjà été vue ne dirait rien de son absence
# ailleurs -- et une campagne sans témoin positif ne peut conclure que dans un sens.
for band in "3188 3988 A" "8892 9692 B" \
            "1400 2200 C" "5000 5800 D" "6600 7400 E" "10500 11300 F"; do
  set -- $band
  OUT="/home/masterlaplace/LplVesuvius/docs/bande_niveau0_$3.json"
  [ -s "$OUT" ] && { echo "bande $3 deja faite"; continue; }
  echo "=== bande $3 : z $1 -> $2, niveau 0, 9 coupes ==="
  uv run python src/excision/fusion_scan.py PHerc0172 "$VOL" "$OUT" \
      --level 0 --slices 9 --z-min "$1" --z-max "$2"
done
echo "termine"
