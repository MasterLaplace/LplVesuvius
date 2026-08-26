#!/usr/bin/env bash
# Miroir de scrollprize.org, puis CONTROLE que chaque URL du sitemap est bien
# presente localement.
#
# Le controle n'est pas decoratif : le site est un Docusaurus dont les fiches
# /data_browser/<rouleau> ne sont atteignables que par du JS, donc un crawl par
# liens en rate 27 sur 81 -- et un miroir incomplet ressemble exactement a un
# miroir complet tant que personne ne compte.
#
# Usage: ./mirror_site.sh
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SITE="$ROOT/data/site"
DOCS="$ROOT/docs"
BASE="https://scrollprize.org"

mkdir -p "$SITE" "$DOCS"

echo "== passe 1 : crawl =="
( cd "$SITE" && wget --mirror --page-requisites --adjust-extension --convert-links \
    --no-parent --domains=scrollprize.org --no-verbose \
    --wait=0.2 --random-wait --tries=3 --timeout=30 \
    --reject 'mp4,webm,mov,m4v,avi' \
    -o "$DOCS/mirror_pass1.log" "$BASE/" )

echo "== passe 2 : pages du sitemap absentes du crawl =="
curl -sSL "$BASE/sitemap.xml" -o "$DOCS/sitemap.xml"
grep -oE '<loc>[^<]*</loc>' "$DOCS/sitemap.xml" | sed -E 's|</?loc>||g' \
  | sed "s|$BASE||; s|^/$|/index|; s|^/||" | grep -v '^$' > "$DOCS/sitemap_paths.txt"

missing=0 fetched=0 failed=0
while read -r p; do
    if [ -f "$SITE/scrollprize.org/$p.html" ] || [ -f "$SITE/scrollprize.org/$p/index.html" ]; then
        continue
    fi
    missing=$((missing + 1))
    out="$SITE/scrollprize.org/$p.html"
    mkdir -p "$(dirname "$out")"
    if curl -sSL -f --retry 4 --retry-delay 2 --retry-all-errors --connect-timeout 20 \
         -o "$out" "$BASE/$p"; then
        fetched=$((fetched + 1))
    else
        failed=$((failed + 1)); echo "  ECHEC $p"; rm -f "$out"
    fi
    sleep 0.2
done < "$DOCS/sitemap_paths.txt"

echo "== controle =="
want=$(wc -l < "$DOCS/sitemap_paths.txt")
have=0
while read -r p; do
    if [ -f "$SITE/scrollprize.org/$p.html" ] || [ -f "$SITE/scrollprize.org/$p/index.html" ]; then
        have=$((have + 1))
    fi
done < "$DOCS/sitemap_paths.txt"

echo "sitemap    : $want URL"
echo "absentes du crawl : $missing (recuperees: $fetched, echecs: $failed)"
echo "presentes  : $have / $want"
echo "volume     : $(du -sh "$SITE" | cut -f1)"

# Le script echoue si la couverture n'est pas totale : un miroir partiel doit se
# voir dans un code de sortie, pas seulement dans une ligne de log.
[ "$have" -eq "$want" ] || { echo "INCOMPLET"; exit 1; }
echo "COMPLET"
