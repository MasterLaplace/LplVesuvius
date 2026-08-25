#!/usr/bin/env bash
# Clone (ou met a jour) les depots listes dans repos.tsv.
#
# Un clone --depth 1 suffit pour etudier du code : l'historique se retelecharge
# a la demande le jour ou on en a besoin, et villa seul pese plusieurs Gio.
#
# Usage: ./clone_repos.sh [tier_max]   (defaut: tous)
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MANIFEST="$ROOT/src/outils/repos.tsv"
DEST="$ROOT/repos"
LOG="$ROOT/docs/clone.log"
MAX_TIER="${1:-9}"
JOBS=6

mkdir -p "$DEST"
: > "$LOG"

clone_one() {
    local name="$1" url="$2" dir="$DEST/$1"
    if [ -d "$dir/.git" ]; then
        if git -C "$dir" fetch --depth 1 origin >/dev/null 2>&1 \
           && git -C "$dir" reset --hard "@{upstream}" >/dev/null 2>&1; then
            echo "UPDATED  $name"
        else
            echo "STALE    $name  (deja present, fetch echoue)"
        fi
        return 0
    fi
    if git clone --depth 1 --quiet "$url" "$dir" 2>/dev/null; then
        echo "CLONED   $name"
    else
        # Distinguer "le depot n'existe pas / est prive" d'une panne reseau :
        # les deux laissent un dossier absent, seul le code HTTP les separe.
        local code
        code="$(curl -s -o /dev/null -w '%{http_code}' "$url")"
        echo "FAILED   $name  (http=$code) $url"
        rm -rf "$dir"
    fi
}
export -f clone_one
export DEST

# Ni les noms ni les URL ne contiennent d'espace, donc -n2 est sans ambiguite.
grep -v '^#' "$MANIFEST" | grep -v '^[[:space:]]*$' \
  | awk -v m="$MAX_TIER" -F'\t' '$1 <= m {print $2, $3}' \
  | xargs -P "$JOBS" -n2 bash -c 'clone_one "$0" "$1"' \
  | tee -a "$LOG"

echo
echo "=== bilan ==="
printf "clones   : %s\n" "$(grep -c '^CLONED'  "$LOG")"
printf "mis a jour: %s\n" "$(grep -c '^UPDATED' "$LOG")"
printf "echecs   : %s\n" "$(grep -c '^FAILED'  "$LOG")"
grep '^FAILED' "$LOG" || true
