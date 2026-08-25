#!/usr/bin/env bash
# La chaine tangentielle S ELOIGNE-T-ELLE de la matiere a mesure qu elle avance ?
#
# ⚠⚠ C EST LA QUESTION QUE L HORIZON LAISSE OUVERTE. `44` mesure qu une chaine purement
# geometrique tient six maillons puis s emballe. Ce que la geometrie ne peut pas dire, c est si
# la nappe reste POSEE SUR LA MATIERE en chemin -- une chaine peut garder un pas parfait en
# marchant droit hors de sa feuille.
#
# ⭐ Le recalage repond sans aucun rendu : de combien la matiere DEMANDERAIT-ELLE de bouger
# chaque point ? Une nappe deja sur sa crete demande peu ; une nappe partie ailleurs demande
# beaucoup, ou ne trouve plus rien.
#
# ⚠⚠ LE TEMOIN EST LA MOITIE DE LA MESURE : le segment PUBLIE, qui est par construction sur sa
# feuille. Sans lui, « la chaine demande 7 voxels » ne veut rien dire -- c est en le comparant
# aux 7 voxels que le segment publie demande AUSSI que le chiffre devient un verdict.
#
# Usage : ZARR=<boite locale> NIVEAU=2 tools/recalage_de_la_chaine.sh <tifxyz>...
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "le recalage est delegue" \
      'grep -q "recaler_sur_la_matiere.py" "$ROOT/tools/recalage_de_la_chaine.sh"'
  MOTEUR="vc_render""_tifxyz"
  chk "aucun rendu n est invoque" \
      '! grep -q "$MOTEUR" "$ROOT/tools/recalage_de_la_chaine.sh"'
  # ⚠⚠ Le niveau de pyramide n a PAS de defaut ici non plus : une coordonnee de niveau 2 lue
  # au niveau 0 designe un point quatre fois plus proche de l origine, dans le vide (`54`).
  chk "le niveau est exige" 'grep -q "NIVEAU:?" "$ROOT/tools/recalage_de_la_chaine.sh"'
  chk "la boite de prediction est exigee" 'grep -q "ZARR:?" "$ROOT/tools/recalage_de_la_chaine.sh"'
  # ⚠ La portee est bornee sous la demi-spire par l outil lui-meme, et le rouleau est donc
  # nomme : sans `--spire-um`, ce garde-fou ne peut pas se declencher.
  chk "la demi-spire est passee a l outil" \
      'grep -q -- "--spire-um" "$ROOT/tools/recalage_de_la_chaine.sh"'
  chk "aucun provisoire dans docs/" \
      'grep -q "TMP=\$(mktemp)" "$ROOT/tools/recalage_de_la_chaine.sh"'
  # ⚠⚠ `set -- $L` DANS la boucle ecraserait la liste de maillages elle-meme. Ce depot a deja
  # paye deux fois cette classe (les arguments d une fonction pris pour ceux du script) : les
  # sept champs se lisent dans des variables NOMMEES, et ce controle l impose.
  chk "aucun set -- positionnel" \
      '! grep -qE "^[[:space:]]*set -- " "$ROOT/tools/recalage_de_la_chaine.sh"'
  chk "... les champs sont lus par read -r" \
      'grep -q "read -r PARCOURU" "$ROOT/tools/recalage_de_la_chaine.sh"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

ZARR="${ZARR:?ZARR requis — une boite de prediction locale (tools/fetch_zarr_boite.py)}"
NIVEAU="${NIVEAU:?NIVEAU requis — celui de la boite, jamais defaute}"
PORTEE="${PORTEE:-4}"
SPIRE="${SPIRE:-173}"
JSON="${JSON:-$ROOT/docs/recalage_de_la_chaine.json}"
[ "$#" -gt 0 ] || { echo "usage : … tools/recalage_de_la_chaine.sh <tifxyz>..." >&2; exit 2; }

printf '%-26s %9s %9s %9s %9s %8s %8s\n' \
  "maillage" "parcouru" "recalés" "sans-mat" "borne" "crête" "demande"
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
echo "[" > "$TMP"
PREMIER=1
for D in "$@"; do
  [ -f "$D/meta.json" ] || { echo "  ⚠ $D : pas de meta.json" >&2; continue; }
  J=$(mktemp)
  uv run --project "$ROOT" python "$ROOT/analysis/src/recaler_sur_la_matiere.py" "$D" \
      --zarr "$ZARR" --niveau "$NIVEAU" --portee "$PORTEE" --spire-um "$SPIRE" \
      --json "$J" > /dev/null 2>&1 || { echo "  ⚠ $D : recalage échoué" >&2; rm -f "$J"; continue; }
  L=$(python3 -c "
import json, sys
c = json.load(open(sys.argv[1]))
m = json.load(open(sys.argv[2]))
print(round(float(m.get('parcouru_vox', 0.0)) * 2.4, 1), c['recales'], c['sans_matiere'],
      c['borne_atteinte'], round(c.get('crete_mediane', 0.0), 2),
      round(c.get('deplacement_median_vox', 0.0), 2), round(c.get('part_vers_le_plus', 0.0), 2))
" "$J" "$D/meta.json")
  # ⚠⚠ Des variables NOMMEES et pas `set -- $L`. Ce depot a deja paye deux fois la meme
  # classe : `$1` desigme les arguments du contexte courant, pas ceux qu on croit -- ici la
  # liste de maillages elle-meme. Sept champs lus dans sept noms, aucune ambiguite possible.
  read -r PARCOURU RECALES SANSMAT BORNE CRETE DEMANDE PART <<<"$L"
  printf '%-26s %9s %9s %9s %9s %8s %8s\n' "$(basename "$D")" \
    "$PARCOURU" "$RECALES" "$SANSMAT" "$BORNE" "$CRETE" "$DEMANDE"
  [ "$PREMIER" = 1 ] || echo "," >> "$TMP"
  PREMIER=0
  printf '{"maillage": "%s", "parcouru_um": %s, "recales": %s, "sans_matiere": %s, "borne": %s, "crete": %s, "demande_vox": %s, "part_vers_le_plus": %s}' \
    "$(basename "$D")" "$PARCOURU" "$RECALES" "$SANSMAT" "$BORNE" "$CRETE" "$DEMANDE" "$PART" >> "$TMP"
  rm -f "$J"
done
echo "]" >> "$TMP"
mv "$TMP" "$JSON"
echo "écrit : $JSON"
