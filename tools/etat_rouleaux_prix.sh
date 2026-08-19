#!/bin/bash
# Ce que chaque rouleau du Grand Prize publie -- et si quelqu'un l'a deja trace.
#
# ⚠⚠ La colonne « segments » est celle qui compte pour First Letters : un rouleau a
# 0 segment n'a ete trace par personne, donc son prix de 50 000 $ est intact. Un rouleau
# qui en a deja est un rouleau ou quelqu'un travaille -- ce qui ne l'exclut pas, mais
# change ce qu'on y risque.
set -u
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
# ⚠ La reponse S3 contient le prefixe INTERROGE en plus des sous-prefixes : compter les
# lignes « Prefix> » sans l'exclure donne un decalage de UN partout, et une table decalee
# d'un cran ressemble parfaitement a une table juste. On exclut explicitement.
n() { curl -s --max-time 30 "$B/?list-type=2&prefix=$1&delimiter=/" \
      | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' \
      | grep -vxF "$1" | grep -c . || true; }
printf '%-12s %9s %9s %9s %9s\n' rouleau volumes surfaces lasagna segments
for R in PHerc0125 PHerc0191 PHerc0211 PHerc0257 PHerc0268 PHerc0358 \
         PHerc0800 PHerc0813 PHerc0826 PHerc1203 PHerc1218 PHerc1447 PHerc1545; do
  printf '%-12s %9s %9s %9s %9s\n' "$R" \
    "$(n "$R/volumes/")" \
    "$(n "$R/representations/predictions/surfaces/")" \
    "$(n "$R/representations/predictions/lasagna/")" \
    "$(n "$R/segments/")"
done
