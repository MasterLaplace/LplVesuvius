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
done_count=0 failed=0 hors_domaine=0

for seg in "$CORPUS"/*/; do
    name="$(basename "$seg")"
    mesh=$(ls -d "$seg"mesh/*.tifxyz 2>/dev/null | head -1)
    if [ -z "$mesh" ]; then
        echo "  pas de maillage : $name" >&2
        failed=$((failed + 1)); continue
    fi
    # ⚠⚠⚠ APPEL PAR CHEMIN, PAS PAR MODULE. Ce script appelait `python -m excision.proximity`,
    # qui ne resout plus : « No module named 'excision' ». Combine au `2>/dev/null` ci-dessous,
    # l'echec etait AVALE et compte comme « trop courte » -- donc un run qui ne mesurait RIEN
    # rendait « 0 mesurees, 55 sans mesure » et sortait en 0. C'est le mode d'echec que ce
    # depot connait par coeur : une panne totale qui ressemble a une population vide. Et la
    # consequence est lourde : `proximity_scroll1.jsonl`, sur lequel repose tout l'arc
    # d'excision, n'a PAS ete regenere apres la correction de rayon de `07` §9, parce que son
    # producteur ne tournait pas.
    #
    # ⚠ Le code 3 est le SEUL echec legitime : une trace qui couvre moins d'un tour ne peut pas,
    # par construction, revenir pres d'elle-meme. Tout autre code est une vraie panne, et elle
    # est desormais RAPPORTEE avec sa sortie d'erreur au lieu d'etre confondue avec elle.
    err=$(cd "$ROOT" && uv run python src/excision/proximity.py \
            "$mesh" --label "$name" --json 2>&1 >> "$OUT")
    code=$?
    if [ "$code" -eq 0 ]; then
        done_count=$((done_count + 1))
    elif [ "$code" -eq 3 ]; then
        hors_domaine=$((hors_domaine + 1))
    else
        failed=$((failed + 1))
        echo "  PANNE ($code) : $name" >&2
        echo "$err" | tail -3 >&2
    fi
done

echo "traces mesurees : $done_count"
echo "hors domaine    : $hors_domaine (moins d'un tour : la metrique ne s'y applique pas)"
echo "en panne        : $failed"
echo "sortie          : $OUT"

# ⚠⚠ UN RUN QUI NE MESURE RIEN NE SORT PAS EN 0. C'est ce qui manquait : sans cette ligne, un
# producteur casse est indistinguable d'un corpus vide, et personne ne regenere le fichier.
if [ "$done_count" -eq 0 ] || [ "$failed" -gt 0 ]; then
    echo "ECHEC : $done_count mesuree(s), $failed en panne" >&2
    exit 1
fi
