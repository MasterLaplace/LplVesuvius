#!/bin/bash
# Recuperer les couches rendues d'un segment, pour la detection d'encre.
#
# ⚠ Le modele GP-2023 ne lit que les couches 15 a 40 : les 157 d'un segment sont
# inutiles, et 26 x 519 Mo font deja 13,5 Go. Telecharger le reste couterait 68 Go
# pour rien.
#
# ⚠ La largeur du nom de fichier CHANGE d'un rouleau a l'autre — Scroll 1 ecrit
# `15.tif`, Scroll 4 ecrit `015.tif`. Elle est donc un parametre, pas une constante :
# la deviner ferait echouer le telechargement avec un 404 qui ressemble a « ce segment
# n'a pas de couches ».
set -u
BASE=$1          # URL du repertoire du segment
DEST=$2          # ou ecrire
WIDTH=${3:-2}    # largeur du nom : 2 pour Scroll 1, 3 pour Scroll 4
FROM=${4:-15}
TO=${5:-40}

mkdir -p "$DEST"
echo "couches $FROM a $TO, largeur $WIDTH -> $DEST"
for i in $(seq "$FROM" "$TO"); do
  NAME=$(printf "%0${WIDTH}d.tif" "$i")
  OUT="$DEST/$(printf '%02d.tif' "$i")"   # ⚠ renomme en 2 chiffres : infer_ink attend ce format
  if [ -s "$OUT" ]; then
    echo "  $NAME deja la"
    continue
  fi
  # ⚠ Transfert REPRENABLE. Ces fichiers font 519 Mo et le serveur coupe
  # ("Recv failure: Connection reset by peer") : sans reprise, 13,5 Go de
  # telechargement dependent de la chance. `--continue-at -` reprend le .part la ou
  # il s'est arrete, `--retry` rejoue les coupures, et `--fail` garde le refus franc
  # sur un 404 -- sinon une page d'erreur HTML finirait ecrite dans un .tif.
  if curl -sS --fail --location \
          --retry 20 --retry-delay 5 --retry-all-errors \
          --continue-at - -o "$OUT.part" "$BASE/layers/$NAME"; then
    mv "$OUT.part" "$OUT"
    echo "  $NAME  $(du -h "$OUT" | cut -f1)"
  else
    rm -f "$OUT.part"
    echo "  $NAME ECHEC" >&2
    exit 1
  fi
done
touch "$DEST/.complet"
echo "termine : $(du -sh "$DEST" | cut -f1)"
