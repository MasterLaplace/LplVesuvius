#!/usr/bin/env bash
# Les deux graines du 2x2, sondees dans le volume SCANNE — six mesures, un JSON.
#
# ⚠⚠ POURQUOI CETTE CAMPAGNE. `54` laisse la cause « la graine, c'est-a-dire l'endroit »
# OUVERTE, avec un prealable ecrit : *sonder la graine avant de payer le trace*. Le 2x2 croise
# ne pouvait pas conclure parce que sa colonne « graine m7 » tenait un NOMBRE constant et non
# un ENDROIT -- le meme nombre designe deux points differents dans deux reperes.
#
# ⭐ Ce que cette campagne mesure, et que personne n avait mesure : chaque graine est sondee
# DANS SON PROPRE REPERE, puis CONVERTIE dans l autre, puis lue SANS CONVERSION (ce que le 2x2
# casse faisait). Six sondes, et la comparaison ne veut dire quelque chose que parce que les
# trois formes sont la.
#
# ⚠ La distance est rendue en blocs ET en micrometres : « un bloc » ne veut rien dire tant
# qu on ne sait pas ce qu il vaut au niveau demande (307 µm au niveau 0, 1229 µm au niveau 2).
#
# Usage :
#   ./src/campagnes/campagne_graines_endroit.sh            # ecrit docs/mesures/graines_endroit.json
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  CORPS=$(awk '/^if \[ "\$\{1:-\}" = "--verifier" \]; then$/{d=1} d==0{print} /^fi$/{d=0}' "$0")
  # ⚠⚠ Les deux graines sont ecrites en (x, y, z) dans `54` et l instrument prend (z, y, x).
  # Inverser l ordre lirait un autre endroit du rouleau et rendrait « pas de matiere » avec le
  # meme aplomb -- c est exactement la classe de panne que cette campagne existe pour fermer.
  chk "les sondes passent le point en (z, y, x)" \
      'printf "%s" "$CORPS" | grep -q -- "--point \$Z \$Y \$X"'
  # ⚠ Le facteur de conversion entre niveaux est 2^niveau, et il est ECRIT une fois.
  chk "la conversion entre reperes est un decalage de bits, pas un nombre recopie" \
      'printf "%s" "$CORPS" | grep -qF "<< 2"'
  chk "chaque graine est sondee dans les TROIS formes" \
      '[ "$(printf "%s" "$CORPS" | grep -c "^sonde ")" -ge 6 ]'
  chk "le resultat va dans un JSON, pas seulement a l ecran" \
      'printf "%s" "$CORPS" | grep -qF "graines_endroit.json"'
  chk "l instrument de distance est celui du depot" \
      'printf "%s" "$CORPS" | grep -qF "distance_a_la_matiere.py"'
  chk "le corps examine exclut bien le bloc de temoin" \
      '! printf "%s" "$CORPS" | grep -q "le corps examine exclut bien"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

SORTIE="${SORTIE:-$ROOT/docs/mesures/graines_endroit.json}"
RAYON="${RAYON:-8}"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT

# ⚠ `sonde <etiquette> <niveau> <z> <y> <x>` — un seul point d appel, pour que les six mesures
# soient produites par le meme code. Six lignes recopiees finiraient par ne plus passer les
# memes options, et l une des six serait fausse sans que rien ne le dise.
sonde() {
  local nom=$1 niv=$2 Z=$3 Y=$4 X=$5
  echo "  $nom ..." >&2
  uv run --project "$ROOT" python "$ROOT/src/nappe/distance_a_la_matiere.py" \
      --niveau "$niv" --point $Z $Y $X --rayon "$RAYON" --json "$TMP/$nom.json" >&2 || true
  [ -s "$TMP/$nom.json" ] || echo '{}' > "$TMP/$nom.json"
}

# Les deux graines de `54`, ecrites la-bas en (x, y, z).
M7_X=2924;   M7_Y=5324;   M7_Z=9260      # coordonnee de NIVEAU 2
PS_X=10752;  PS_Y=10616;  PS_Z=38740     # coordonnee de NIVEAU 0

sonde m7_dans_son_repere        2 $M7_Z $M7_Y $M7_X
sonde m7_converti_en_L0         0 $((M7_Z << 2)) $((M7_Y << 2)) $((M7_X << 2))
sonde m7_lu_en_L0_sans_conversion 0 $M7_Z $M7_Y $M7_X
sonde ps256_dans_son_repere     0 $PS_Z $PS_Y $PS_X
sonde ps256_converti_en_L2      2 $((PS_Z >> 2)) $((PS_Y >> 2)) $((PS_X >> 2))
sonde ps256_lu_en_L2_sans_conversion 2 $PS_Z $PS_Y $PS_X

uv run --project "$ROOT" python - "$TMP" "$SORTIE" <<'PY'
import json, pathlib, sys
tmp, sortie = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
ESPACEMENT_UM = 173.0   # espacement inter-spires median du rouleau, `16`
sondes = {}
for f in sorted(tmp.glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    if d.get("trouve") and d.get("distance_blocs") is not None:
        um = d["distance_blocs"] * d["cote_bloc"] * 2.4 * (2 ** d["niveau"])
        d["distance_um_max"] = um
        d["distance_spires_max"] = um / ESPACEMENT_UM
    sondes[f.stem] = d
sortie.write_text(json.dumps({"espacement_um": ESPACEMENT_UM, "sondes": sondes},
                             indent=1, ensure_ascii=False), encoding="utf-8")
print(f"{len(sondes)} sonde(s) -> {sortie}")
for n, d in sondes.items():
    if not d:
        print(f"  {n:36} (pas de mesure)")
    elif d.get("trouve"):
        print(f"  {n:36} {d['distance_blocs']} bloc(s)  "
              f"≤ {d.get('distance_um_max', 0):.0f} µm  "
              f"≈ {d.get('distance_spires_max', 0):.1f} spire(s)")
    else:
        print(f"  {n:36} AUCUNE matière dans {d.get('rayon_regarde')} bloc(s)")
PY
