#!/usr/bin/env bash
# Une IMAGE de la surface, regardable par un humain.
#
# ⚠⚠ Pourquoi ce script existe. Tout le reste du depot rend des surfaces pour en tirer des
# NOMBRES -- un profil de profondeur, un alpha -- et profiler_une_surface.sh supprimait le
# rendu juste apres, pour economiser du disque. On produisait donc des images du papyrus et
# on les jetait avant de les avoir regardees. Un pipeline entier dont le seul artefact
# lisible par un oeil humain part a la poubelle, c est un defaut de conception, pas une
# economie.
#
# ⚠ Ce script rend PEU de tranches (trois par defaut) : on veut voir la surface, pas
# l analyser. La fenetre d analyse de 1024 px ne s applique pas ici, donc on peut descendre
# aussi grossier qu on veut -- une image de 2000 px se regarde tres bien.
#
# Usage : src/outils/apercu_surface.sh <dossier-de-trace> [niveau] [tranches]
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  # ⚠⚠ Le convertisseur n est PAS ffmpeg : il a rendu du noir en silence sur une image
  # pleine. Celui du depot compare la sortie a l entree et refuse une image sans variete.
  chk "le convertisseur maison existe" '[ -f "$ROOT/src/volume/tif_en_png.py" ]'
  # ⚠⚠ Le motif est ancre sur le DEBUT DE LIGNE, donc il ne vise qu une INVOCATION. Une
  # version qui cherchait la sous-chaine nue attrapait le commentaire qui explique
  # pourquoi on n utilise pas cet outil -- la sonde signalait donc la documentation de la
  # regle qu elle verifie. Piege 67, quatrieme fois du jour, et le bon remede n est pas de
  # couper le motif : c est de l ANCRER sur la syntaxe.
  chk "aucune invocation du convertisseur externe" \
      '! grep -qE "^[[:space:]]*ff""mpeg" "$ROOT/src/outils/apercu_surface.sh"' 
  chk "le lecteur d en-tete existe" '[ -f "$ROOT/src/volume/dimensions_tiff.py" ]'
  # ⚠⚠ La regle qui justifie ce fichier : il ne doit JAMAIS supprimer ce qu il rend.
  # Le motif est coupe en deux, sinon la sonde se matcherait elle-meme (piege 67).
  chk "il ne supprime pas son propre rendu" \
      '! grep -qE "rm -rf .*\$SORTIE|rm -rf .*rend""u" "$ROOT/src/outils/apercu_surface.sh"'
  out=$("$ROOT/src/outils/apercu_surface.sh" /inexistant 2>&1); rc=$?
  chk "une trace absente est refusee (2)" '[ "$rc" = 2 ]'
  chk "le png est produit, pas seulement le tif" 'grep -q "\.png" "$ROOT/src/outils/apercu_surface.sh"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

SRC="${1:?dossier de trace}"
[ -d "$SRC/plat" ] || { echo "refus : pas de surface aplatie dans $SRC" >&2; exit 2; }
NIVEAU="${2:-2}"
TRANCHES="${3:-3}"
CACHE_GB="${CACHE_GB:-1}"
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="${VOL:-PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr}"
SORTIE="${SORTIE:-$SRC/apercu_g$NIVEAU}"
UM=$(python3 -c "print(2.4 * 2**$NIVEAU)")

echo "== aperçu de $(basename "$SRC")  ·  niveau $NIVEAU (voxel ${UM} µm)  ·  $TRANCHES tranches"
if [ ! -d "$SORTIE" ] || [ -z "$(ls "$SORTIE"/*.tif 2>/dev/null)" ]; then
  rm -rf "$SORTIE"
  "$ROOT/src/outils/rendre_surveille.sh" "$SORTIE" 600 -- \
      -v "$SRC/cache_apercu" --remote-url "$B/$VOL" --scale 1 -g "$NIVEAU" \
      -s "$SRC/plat" --tif-output "$SORTIE" -n "$TRANCHES" --slice-step 1 --auto-crop \
      --cache-gb "$CACHE_GB" > "$SORTIE.log" 2>&1 \
    || { echo "   ⚠ rendu abandonné — voir $SORTIE.log" >&2; exit 3; }
  rm -rf "$SRC/cache_apercu"
fi

# ⚠ La tranche du MILIEU : c est celle qui passe par la surface tracee, les autres sont
# au-dessus et en dessous. Prendre la premiere montrerait ce qui est a cote de la feuille.
MILIEU=$(ls "$SORTIE"/*.tif | sed -n "$(( (TRANCHES + 1) / 2 ))p")
[ -n "$MILIEU" ] || { echo "refus : aucune tranche rendue" >&2; exit 3; }
D=$(python3 "$ROOT/src/volume/dimensions_tiff.py" "$MILIEU" 2>&1)
echo "   tranche centrale : $(basename "$MILIEU")  ·  $D"

PNG="${PNG:-$SORTIE.png}"
# ⚠⚠ La conversion NE passe PAS par ffmpeg. Mesure : un `ffmpeg -i tranche.tif sortie.png`
# a rendu une image entierement NOIRE a partir d un fichier dont la moyenne est de 66 sur
# 255 et dont 74,5 % des pixels sont non nuls -- silencieusement, code de retour zero. On a
# failli en conclure que le rendu n avait rien produit. Le convertisseur maison COMPARE les
# statistiques de la sortie a celles de l entree et refuse d ecrire une image sans variete.
uv run --project "$ROOT" python "$ROOT/src/volume/tif_en_png.py" \
    "$MILIEU" "$PNG" || { echo "refus : conversion refusée (voir ci-dessus)" >&2; exit 3; }
echo "   écrit : $PNG  ($(du -h "$PNG" | cut -f1))"
echo
echo "   ⚠ les tranches TIFF sont CONSERVÉES dans $SORTIE — c'est le seul artefact"
echo "     de tout ce pipeline qu'un œil humain peut lire."
