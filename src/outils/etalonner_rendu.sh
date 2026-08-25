#!/usr/bin/env bash
# Combien de RAM le rendu doit-il avoir, et combien lui en donner ?
#
# ⚠⚠ D ou vient cette mesure. Le rendu d une surface de 3,66 cm2 tenait 28,2 Go de RSS sur
# une machine de 31,8, avec 3,4 Go passes en swap, 274 Mo libres, le cache de pages du noyau
# ecrase a 442 Mo -- et 23,7 % d UN c ur alors que la machine en a 22 et que le processus
# avait 59 threads. Il n etait pas limite par le calcul : il attendait la memoire.
#
# La cause est dans NOS arguments : --cache-gb vaut 16 PAR DEFAUT, et aucun des 28 appels a
# vc_render_tifxyz de ce depot ne le regle. La moitie de la RAM partait en cache de chunks
# avant meme que la surface soit allouee.
#
# ⚠ Ce script ne devine pas la bonne valeur, il la mesure : meme surface, meme fenetre, seul
# --cache-gb change ; on releve le temps de mur et le pic de RSS.
#
# ⚠⚠ Le cache DISQUE est chauffe UNE FOIS avant la serie. Sans ca le premier essai paie le
# telechargement et les suivants lisent un disque chaud : on mesurerait la chaleur du cache
# et pas le reglage. C est le piege « comparer une grandeur a elle-meme » sous un costume
# de banc d essai.
#
# ⚠⚠ Et l on verifie que la sortie ne BOUGE PAS. Un reglage de performance qui change les
# pixels n est pas un reglage de performance -- ce serait dire que tous les rendus deja
# publies dependaient d une valeur que personne n avait posee.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "le depouilleur existe" '[ -f "$ROOT/src/graine/effet_du_cache.py" ]'
  chk "le pic de RSS est releve" 'grep -q "Maximum resident set size" "$ROOT/src/outils/etalonner_rendu.sh"'
  chk "le cache disque est chauffe avant la serie" 'grep -q "chauffe" "$ROOT/src/outils/etalonner_rendu.sh"'
  chk "chaque valeur est repetee" 'grep -q "REPETITIONS" "$ROOT/src/outils/etalonner_rendu.sh"'
  chk "... au moins trois fois par defaut" 'grep -qE "REPETITIONS:-[3-9]" "$ROOT/src/outils/etalonner_rendu.sh"'
  chk "la sortie est comparee entre essais" 'grep -q "sha256sum" "$ROOT/src/outils/etalonner_rendu.sh"'
  out=$("$ROOT/src/outils/etalonner_rendu.sh" /inexistant 2>&1); rc=$?
  chk "une surface absente est refusee (2)" '[ "$rc" = 2 ]'
  chk "... et le refus nomme le chemin" 'printf "%s" "$out" | grep -q inexistant'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

SRC="${1:-$ROOT/data/paris4_plafond/ps256_c2_g60}"
[ -d "$SRC/plat" ] || { echo "refus : pas de surface aplatie dans $SRC" >&2; exit 2; }
COUCHES="${COUCHES:-41}"
VALEURS="${VALEURS:-1 2 4 8 16}"
# ⚠⚠ REPETITIONS, et ce depot avait deja ecrit la lecon : campagne_thread_limit.sh dit
# « une seule execution par valeur ne distinguerait pas l effet du reglage de la variance
# de run ». Elle vaut DOUBLE ici -- le cache disque n est jamais materialise (verifie : le
# repertoire -v reste vide), donc chaque essai retelecharge et le chronometre porte autant
# le reseau que le reglage. Un seul essai par valeur mesurerait la meteo du reseau.
REPETITIONS="${REPETITIONS:-3}"
DEST="${DEST:-$ROOT/data/etalon_rendu}"
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="${VOL:-PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr}"
JSON="${JSON:-$ROOT/docs/etalon_rendu.json}"
mkdir -p "$DEST"

echo "== surface $(basename "$SRC")  ·  $COUCHES couches  ·  --cache-gb : $VALEURS"
echo "== RAM totale $(free -g | awk 'NR==2{print $2}') Go  ·  $(nproc) cœurs"

# ⚠⚠ Chauffe : un premier rendu jete, uniquement pour remplir le cache DISQUE. Sans lui le
# premier essai de la serie porte le telechargement de tout le volume et sort du lot pour
# une raison qui n a rien a voir avec le reglage mesure.
CACHE="$DEST/cache"
if [ ! -d "$CACHE" ]; then
  echo "== chauffe du cache disque (rendu jeté)"
  rm -rf "$DEST/chauffe"
  vc_render_tifxyz -v "$CACHE" --remote-url "$B/$VOL" --scale 1 -g 0 -s "$SRC/plat" \
      --tif-output "$DEST/chauffe" -n "$COUCHES" --slice-step 1 --auto-crop \
      --cache-gb 4 > "$DEST/chauffe.log" 2>&1 || { echo "   ⚠ chauffe échouée"; exit 3; }
  echo "   cache disque : $(du -sh "$CACHE" | cut -f1)"
fi

echo
printf '%10s %6s %12s %14s %14s\n' "cache-gb" "essai" "temps (s)" "pic RSS (Go)" "sortie"
REF=""
for G in $VALEURS; do
 for R in $(seq 1 "$REPETITIONS"); do
  D="$DEST/gb${G}_r${R}"
  rm -rf "$D"
  /usr/bin/time -v -o "$DEST/gb${G}_r${R}.time" \
    vc_render_tifxyz -v "$CACHE" --remote-url "$B/$VOL" --scale 1 -g 0 -s "$SRC/plat" \
      --tif-output "$D" -n "$COUCHES" --slice-step 1 --auto-crop \
      --cache-gb "$G" > "$DEST/gb${G}_r${R}.log" 2>&1
  rc=$?
  T=$(grep -oE "Elapsed \(wall clock\) time.*" "$DEST/gb${G}_r${R}.time" | grep -oE "[0-9:.]+$")
  SEC=$(printf '%s' "$T" | awk -F: '{n=NF; s=0; for(i=1;i<=n;i++) s=s*60+$i; print s}')
  RSS=$(grep -oE "Maximum resident set size \(kbytes\): [0-9]+" "$DEST/gb${G}_r${R}.time" \
        | grep -oE "[0-9]+$")
  H=$(cat "$D"/*.tif 2>/dev/null | sha256sum | cut -c1-12)
  [ -z "$REF" ] && REF="$H"
  MARQ=$([ "$H" = "$REF" ] && echo "identique" || echo "⚠ DIFFERENTE")
  [ "$rc" = 0 ] || MARQ="⚠ ECHEC($rc)"
  printf '%10s %6s %12s %14.2f %14s\n' "$G" "r$R" "${SEC:-?}" \
      "$(echo "${RSS:-0}/1048576" | bc -l)" "$MARQ"
  python3 - "$JSON" "$G" "${SEC:-0}" "${RSS:-0}" "$H" "$COUCHES" "$R" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
d = json.loads(p.read_text()) if p.exists() else {"essais": []}
rep = int(sys.argv[7])
d["essais"] = [e for e in d["essais"]
               if not (e["cache_gb"] == int(sys.argv[2]) and e.get("repetition", 1) == rep)]
d["essais"].append({"cache_gb": int(sys.argv[2]), "repetition": rep,
                    "secondes": float(sys.argv[3]),
                    "pic_rss_kio": int(sys.argv[4]), "empreinte": sys.argv[5],
                    "couches": int(sys.argv[6])})
d["essais"].sort(key=lambda e: (e["cache_gb"], e.get("repetition", 1)))
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
  rm -rf "$D"
 done
done

echo
uv run --project "$ROOT" python "$ROOT/src/graine/effet_du_cache.py" --json "$JSON"
