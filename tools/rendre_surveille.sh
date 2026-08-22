#!/bin/bash
# `vc_render_tifxyz` sous surveillance : un rendu qui n'avance plus le DIT.
#
# ⚠⚠ Pourquoi ce script existe. Le 2026-08-22, un rendu de PHercParis4 a tourne QUINZE
# MINUTES en produisant 41 fichiers de 8 octets -- des souches vides. Mesure prise sur
# `/proc/<pid>/io` : 51 Mo lus, 1592 octets ecrits, soit ~57 Ko/s. Pour une surface de
# 3,65 cm² a 2,4 µm (~2,6 milliards de voxels) cela faisait plus de DOUZE HEURES, et rien
# dans la sortie ne le disait. Une campagne qui peut brasser une journee sans le signaler
# est une campagne qui gaspille une journee.
#
# ⭐ Le chien de garde ne mesure pas le temps ecoule -- un rendu long n'est pas un rendu
# bloque -- mais la CROISSANCE de la sortie. Tant que les octets augmentent, il attend.
#
# ⚠ Et il rapporte le debit dans les deux cas, succes compris : c'est ce chiffre qui dit si
# la meme campagne est jouable a une autre echelle, et le deviner apres coup est impossible.
#
#   ./tools/rendre_surveille.sh <sortie_tif> <patience_s> -- <arguments de vc_render_tifxyz>
set -u
SORTIE=${1:?sortie tif}
PATIENCE=${2:?patience en secondes}
shift 2
[ "${1:-}" = "--" ] && shift

taille() { du -sb "$SORTIE" 2>/dev/null | cut -f1 || echo 0; }

mkdir -p "$SORTIE"
DEBUT=$(date +%s)
vc_render_tifxyz "$@" &
PID=$!

DERNIERE=$(taille); IMMOBILE=0
while kill -0 "$PID" 2>/dev/null; do
  sleep 10
  T=$(taille)
  if [ "$T" -gt "$DERNIERE" ]; then
    DERNIERE=$T; IMMOBILE=0
  else
    IMMOBILE=$((IMMOBILE + 10))
    if [ "$IMMOBILE" -ge "$PATIENCE" ]; then
      # ⚠⚠ On tue par PID et jamais par motif : `pkill -f` matche sa PROPRE ligne de
      # commande, ce qui a deja tue trois shells dans ce depot.
      kill "$PID" 2>/dev/null
      wait "$PID" 2>/dev/null
      ECOULE=$(( $(date +%s) - DEBUT ))
      echo "⚠⚠ RENDU ABANDONNE — la sortie n'a pas grossi depuis ${PATIENCE} s" >&2
      echo "   ${DERNIERE} octets en ${ECOULE} s" >&2
      echo "   Ce n'est pas une panne du script : c'est la mesure que ce rendu-la n'est" >&2
      echo "   pas jouable a cette echelle. Baisser --scale, ou reduire l'aire." >&2
      exit 4
    fi
  fi
done
wait "$PID"; RC=$?
ECOULE=$(( $(date +%s) - DEBUT ))
FIN=$(taille)
# ⚠ Division gardee : un rendu instantane ferait diviser par zero, et un debit infini
# n'apprend rien a personne.
if [ "$ECOULE" -gt 0 ]; then
  echo "   rendu : ${FIN} octets en ${ECOULE} s ($((FIN / ECOULE / 1024)) Kio/s)"
else
  echo "   rendu : ${FIN} octets en moins d'une seconde"
fi
exit "$RC"
