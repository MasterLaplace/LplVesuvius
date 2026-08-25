#!/bin/bash
# Toute image qu'un document reference existe-t-elle vraiment ?
#
# ⚠⚠ Pourquoi ce controle existe. Un document qui pointe une image absente ne casse rien a
# l'execution : il s'affiche avec une icone brisee, et personne ne le voit tant que personne
# ne l'ouvre. Le depot a 50 documents et 55 images ; la seule facon de le savoir est de le
# demander a chaque lien.
#
# ⭐ Et le controle SYMETRIQUE, qui vaut autant : une image que plus aucun document ne
# reference est du poids mort -- soit un renommage a moitie fait, soit une figure remplacee
# dont l'ancienne version traine. Elle est signalee et pas supprimee : effacer un fichier
# appartient a son auteur.
#
#   ./src/outils/images_des_docs.sh
#   ./src/outils/images_des_docs.sh --verifier   (le controle du controle)
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DOCS=${DOCS:-$ROOT/docs}
IMAGES=${IMAGES:-$DOCS/images}
# ⚠⚠ Le README pointe des images depuis la RACINE, donc il doit etre balaye lui aussi -- et
# il doit etre surchargeable, sinon l'auto-test ramasse le vrai README du depot pendant qu'il
# examine un dossier de fixture, et ses deux cas positifs echouent sur des liens qui n'ont
# rien a voir. Paye des le premier lancement.
# ⚠ `${X-defaut}` et NON `${X:-defaut}` : le second substitue aussi quand la variable est
# VIDE, donc un `EXTRA=""` explicite retombait sur le README et l'auto-test examinait le
# vrai depot en croyant examiner sa fixture. « Vide » et « absent » sont deux intentions
# differentes, et seule la forme sans deux-points les distingue.
EXTRA=${EXTRA-$ROOT/README.md}

if [ "${1:-}" = "--verifier" ]; then
  T=$(mktemp -d); E=0; N=0
  v() { N=$((N + 1)); if [ "$2" != "$3" ]; then E=$((E + 1))
        echo "  ECHEC  $1 — attendu $3, obtenu $2"; fi; }
  mkdir -p "$T/docs/images"
  printf '![ok](images/la.png)\n' > "$T/docs/a.md"
  printf 'x' > "$T/docs/images/la.png"
  DOCS="$T/docs" IMAGES="$T/docs/images" EXTRA="" "$0" > "$T/ok.log" 2>&1
  v "un lien qui pointe une image presente passe" "$?" "0"
  # ⚠⚠ LA sonde : un lien casse doit FAIRE ECHOUER. Sans elle, un controle qui repondrait
  # toujours « tout va bien » aurait l'air d'une garantie.
  printf '![absente](images/pas_la.png)\n' >> "$T/docs/a.md"
  DOCS="$T/docs" IMAGES="$T/docs/images" EXTRA="" "$0" > "$T/ko.log" 2>&1
  v "un lien casse fait echouer" "$?" "1"
  grep -q "pas_la.png" "$T/ko.log"; v "... en nommant l'image" "$?" "0"
  # ⚠⚠ Une image de ZERO OCTET est cassee, pas presente. Le test utilise `-s` et non `-e`
  # pour cette raison : un rendu interrompu laisse un fichier vide, et un lien vers un
  # fichier vide s'affiche exactement comme un lien vers rien.
  printf '![vide](images/vide.png)\n' > "$T/docs/a.md"
  : > "$T/docs/images/vide.png"
  DOCS="$T/docs" IMAGES="$T/docs/images" EXTRA="" "$0" > "$T/vide.log" 2>&1
  v "une image de zero octet est cassee" "$?" "1"
  printf '![ok](images/la.png)\n' > "$T/docs/a.md"
  rm -f "$T/docs/images/vide.png"

  # ⚠ Une image orpheline est SIGNALEE mais ne fait pas echouer : du poids mort n'est pas
  # une panne, et confondre les deux ferait ignorer les vraies.
  printf 'x' > "$T/docs/images/orpheline.png"
  printf '![ok](images/la.png)\n' > "$T/docs/a.md"
  DOCS="$T/docs" IMAGES="$T/docs/images" EXTRA="" "$0" > "$T/orph.log" 2>&1
  v "une image orpheline ne fait pas echouer" "$?" "0"
  grep -q "orpheline.png" "$T/orph.log"; v "... mais elle est nommee" "$?" "0"
  rm -rf "$T"
  if [ "$E" -gt 0 ]; then echo "ECHEC ($E failures, $N checks)"; exit 1; fi
  echo "ALL PASS (0 failures, $N checks)"; exit 0
fi

# ⚠ On lit les liens markdown `](images/…)` ET `](docs/images/…)` : le README pointe depuis
# la racine, les documents depuis `docs/`. Ne chercher qu'une des deux formes laisserait la
# moitie des liens non verifies, ce qui est pire que pas de controle.
LIENS=$(grep -rhoE '\]\((\.\./)?(docs/)?images/[^)]+\)' "$DOCS" $EXTRA 2>/dev/null \
        | sed 's/^](//; s/)$//; s|^\.\./||; s|^docs/||' | sort -u)
CASSES=0; N=0
for f in $LIENS; do
  N=$((N + 1))
  [ -s "$IMAGES/$(basename "$f")" ] || { echo "  CASSE  $f"; CASSES=$((CASSES + 1)); }
done

ORPHELINES=0
for img in "$IMAGES"/*; do
  [ -e "$img" ] || continue
  b=$(basename "$img")
  printf '%s\n' "$LIENS" | grep -qF "$b" || { echo "  orpheline : $b"; ORPHELINES=$((ORPHELINES + 1)); }
done

if [ "$CASSES" -gt 0 ]; then
  echo "ECHEC ($CASSES failures, $N checks) — $CASSES lien(s) pointent une image absente"
  exit 1
fi
SUF=""
[ "$ORPHELINES" -gt 0 ] && SUF="  ⚠ $ORPHELINES image(s) orpheline(s), signalées et gardées"
echo "ALL PASS (0 failures, $N checks)$SUF"
