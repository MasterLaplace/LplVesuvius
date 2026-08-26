#!/usr/bin/env bash
# Passe la metrique de proximite sur tous les segments d'un corpus local.
#
# Sortie JSON Lines : une ligne par trace, directement joignable a l'index publie
# de windcheck (meme cle `segment`).
#
# Usage: ./run_proximity.sh <dossier_corpus> <fichier_sortie>
#   ex.: ./run_proximity.sh data/repos/windcheck/data/scroll1_tifxyz docs/mesures/proximity_scroll1.jsonl
set -u

# ⚠ DEUX niveaux : ce script vit dans `src/excision/`, pas dans `src/excision/`.
# Un seul `..` rendrait `src/` et chaque chemin construit dessous serait faux d un
# cran -- sans erreur, juste des fichiers introuvables.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CORPUS="${1:?dossier corpus attendu}"
OUT="${2:?fichier de sortie attendu}"

: > "$OUT"
done_count=0 failed=0

for seg in "$CORPUS"/*/; do
    name="$(basename "$seg")"
    mesh=$(ls -d "$seg"mesh/*.tifxyz 2>/dev/null | head -1)
    if [ -z "$mesh" ]; then
        echo "  pas de maillage : $name" >&2
        failed=$((failed + 1)); continue
    fi
    # Une trace qui couvre moins d'un tour ne peut PAS, par construction, revenir
    # pres d'elle-meme : l'outil sort en 3 et le dit. Ce n'est pas un echec, c'est
    # une population vide -- compte a part plutot que confondu avec une erreur.
    if (cd "$ROOT" && uv run python -m excision.proximity \
            "$mesh" --label "$name" --json >> "$OUT" 2>/dev/null); then
        done_count=$((done_count + 1))
    else
        failed=$((failed + 1))
    fi
done

echo "traces mesurees : $done_count"
echo "sans mesure     : $failed (trop courtes, ou maillage absent)"
echo "sortie          : $OUT"
