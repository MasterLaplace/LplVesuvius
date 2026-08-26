#!/usr/bin/env bash
# Echantillonne le CT aux cellules excisees, pour tous les segments deja reparis.
#
# Se contente de ce qui est pret : la boucle de reparation tourne a part et met
# des heures, alors qu'un resultat partiel est deja lisible -- a condition de dire
# QUELS segments il couvre, ce que la sortie fait.
#
# Usage: ./run_measure.sh [fichier_de_sortie]
set -u

# ⚠ DEUX niveaux : ce script vit dans `src/excision/`, pas dans `src/excision/`.
# Un seul `..` rendrait `src/` et chaque chemin construit dessous serait faux d un
# cran -- sans erreur, juste des fichiers introuvables.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WINDCHECK="$ROOT/data/repos/windcheck"
VOLUME="s3://vesuvius-challenge-open-data/PHerc0172/volumes/20241024131839-7.910um-53keV-masked.zarr"
OUT="${1:-$ROOT/docs/mesures/excision_samples.tsv}"

# Quatre temoins par cellule excisee, et non seize. Decision de COUT, verifiee
# avant d'etre prise : sur les segments deja mesures, la taille d'effet vaut
# -0.0723 avec tous les temoins et -0.0713 +/- 0.0022 a ce ratio, soit une
# incertitude trente fois plus petite que l'effet. Seize temoins quadruplaient le
# temps de mesure sans rien acheter.
CONTROLS=4

printf "segment\tpopulation\trow\tcol\tintensity\n" > "$OUT"

covered=0 skipped=0
for transformed in "$WINDCHECK"/out/all/*/*_transformed.tifxyz; do
    [ -d "$transformed" ] || continue
    name="$(basename "$(dirname "$transformed")")"
    original=$(ls -d "$WINDCHECK/data/scroll5_tifxyz/$name/mesh/"*.tifxyz 2>/dev/null | head -1)
    if [ -z "$original" ]; then
        echo "  original introuvable : $name" >&2
        skipped=$((skipped + 1)); continue
    fi
    # Un segment deja propre n'a aucune cellule excisee : l'outil sort en 2 et le
    # dit. Ce n'est pas un echec de mesure, c'est une population vide, donc on le
    # compte separement plutot que de le confondre avec une erreur.
    if (cd "$ROOT" && uv run python -m excision.measure \
            "$original" "$transformed" --volume "$VOLUME" --segment "$name" \
            --controls-per-excised "$CONTROLS" \
            >> "$OUT" 2>/dev/null); then
        covered=$((covered + 1))
    else
        skipped=$((skipped + 1))
    fi
done

echo "segments mesures  : $covered"
echo "segments sautes   : $skipped (deja propres, ou original introuvable)"
echo "lignes ecrites    : $(( $(wc -l < "$OUT") - 1 ))"
echo "sortie            : $OUT"
