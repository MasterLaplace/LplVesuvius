#!/bin/bash
# Quels segments publient un volume de surface Zarr — donc un profil de profondeur
# lisible A DISTANCE pour 1,78 Mo la fenetre, au lieu de 32 Go la pile.
#
# ⚠ On liste par SEGMENT, jamais le prefixe entier du rouleau : c'est le piege nº 16
# du depot (`aws s3 cp --include` enumere tout avant de filtrer).
set -u
cd "$(dirname "$0")/../.." || exit 2
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
SCROLL=${1:-PHercParis4}
OUT=${2:-docs/volumes_surface_$SCROLL.txt}

# ⚠ Un fichier VIDE disait deux choses a la fois : « ce rouleau ne publie aucun volume
# de surface » et « le listage a echoue ». PHerc0800 et PHerc1203 etaient dans ce cas,
# versionnes vides, indistinguables d'un run mort. On separe les deux : le listage des
# segments est teste AVANT d'ecrire, et le fichier porte toujours une ligne d'en-tete
# qui dit ce qui a ete cherche et ce qui a ete trouve.
# ⚠⚠ L'en-tete ne doit contenir AUCUNE tabulation. fetch_cartes_encre.sh filtre par
# `awk -F'\t' '$3>0'`, et awk compare NUMERIQUEMENT des que le champ commence par un
# chiffre : un en-tete tabule dont le 3e champ etait une date « 2026-... » passait le
# test et sortait comme un segment. Teste, attrape, corrige. Sans tabulation, $2 et $3
# sont vides et les quatre consommateurs ignorent la ligne.
SEGMENTS=$(curl -s --max-time 60 "$B/?list-type=2&prefix=$SCROLL/segments/&delimiter=/&max-keys=1000" \
  | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||')
if [ -z "$SEGMENTS" ]; then
  echo "ECHEC : aucun segment liste pour $SCROLL — reseau, ou nom de rouleau faux." >&2
  echo "  (le fichier $OUT n'est PAS ecrit : un vide se lirait comme « pas de volume »)" >&2
  exit 3
fi
: > "$OUT"
printf '# %s -- %s segments listes -- %s\n' "$SCROLL" "$(wc -l <<< "$SEGMENTS")" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUT"
echo "$SEGMENTS" | while read -r p; do
  seg=$(basename "$p")
  keys=$(curl -s --max-time 40 "$B/?list-type=2&prefix=${p}surface-volumes/&delimiter=/" \
         | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$')
  [ -z "$keys" ] && continue
  # ⚠ Une carte d'encre publiee, quand elle existe, donne le RESULTAT sans qu'on ait a
  # lancer 43 minutes d'inference. C'est ce qui rend la validation abordable.
  ink=$(curl -s --max-time 30 "$B/?list-type=2&prefix=${p}ink-detection/&max-keys=3" \
        | grep -c "<Key>")
  while read -r z; do
    printf '%s\t%s\t%s\n' "$seg" "${z%/}" "$ink" >> "$OUT"
  done <<< "$keys"
  echo "  $seg : $(wc -l <<< "$keys") volume(s), $ink carte(s) d'encre"
done
N=$(grep -vc '^#' "$OUT")
if [ "$N" -eq 0 ]; then
  printf '# AUCUN volume de surface publie pour ce rouleau (mesure, pas echec)\n' >> "$OUT"
  echo "ecrit : $OUT  — AUCUN volume de surface, et le fichier le DIT"
else
  echo "ecrit : $OUT  ($N volume(s))"
fi
