#!/bin/bash
# Le critere de graine tient-il sur les DIX rouleaux du prix que personne n'a traces ?
#
# ⚠⚠ Conception APPARIEE, et c'est tout l'interet : sur chaque rouleau on trace DEUX fois,
# une graine par critere, tout le reste identique (memes parametres, meme prediction, meme
# machine). Un rouleau est alors son propre temoin, et la difference ne peut pas etre mise
# sur le dos de « ce rouleau-la est plus facile ».
#
# ⚠ La taille de voxel est LUE sur le nom du volume de chaque rouleau, jamais empruntee a
# un autre. Sans `voxelsize`, `vc_grow_seg_from_seed` calcule une aire nulle et rejette
# TOUTE surface avec « area 0 below min_area_cm » -- le message accuse la surface, le
# fautif est le parametre. Et emprunter le chiffre d'un rouleau voisin est le piege nº 6.
#
# ⚠ Reprenable : un rouleau deja mesure est saute. Chaque rouleau ecrit son propre JSON.
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/graines}
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
mkdir -p "$DEST"

# Les dix rouleaux du Grand Prize SANS aucun segment publie (docs/23) : leur prix
# First Letters de 50 000 $ est intact.
#
# ⭐ Plus les TROIS rouleaux qui, eux, ont des segments officiels -- et c'est la seule facon
# de lever le confond « notre trace » contre « ce rouleau-la est moins bien scanne ». Leurs
# segments s'appellent `auto_grown_*` et leur meta.json dit `source: vc_grow_seg_from_seed`
# avec `mode: explicit_seed` : c'est EXACTEMENT notre chaine, pilotee par le concours. Sur
# ces trois rouleaux on peut donc comparer a resolution egale, sur le meme volume.
#
# ⚠⚠ `PHerc1203` manquait, et son absence n'etait ecrite nulle part : `docs/35` §5 l'a
# trouvee en constatant que la campagne des tirages ne couvrait que douze rouleaux sur
# treize. Il est l'un des trois a segment publie, donc l'un des rares comparables.
ROULEAUX="PHerc0125 PHerc0191 PHerc0211 PHerc0257 PHerc0268 PHerc0358 PHerc0813 PHerc0826 PHerc1218 PHerc1545 PHerc1447 PHerc0800 PHerc1203"

# ⚠⚠ `ROULEAUX` peut etre remplace -- et un run qui le remplace DOIT avoir sa propre
# destination. La liste ci-dessus n'est pas un defaut commode, c'est la definition de la
# comparaison appariee de `25` : y ajouter un rouleau change ce que le test des signes
# compte, sans qu'aucune ligne ne le dise. Meme discipline que `GENERATIONS` dans
# `campagne_tirages.sh`, et pour la meme raison -- des mesures qui ne repondent pas a la
# meme question ne doivent pas atterrir dans le meme dossier.
#
# ⭐ L'usage prevu est celui que `48` nomme : etendre la recherche de graine a un rouleau
# LISIBLE (dont la sortie publiee porte du texte), pour qu'il existe enfin un rouleau ou
# l'on sait a la fois tracer et lire.
#
#   ROULEAUX_CIBLE=PHerc0172 ./tools/campagne_graines.sh data/graines_lisibles
#
# ⚠ La regle « sa propre destination » est IMPOSEE et pas seulement ecrite : un override
# vers le dossier par defaut est refuse. Une regle qu'on doit se rappeler de suivre n'est
# pas une garantie -- ce depot l'a paye avec la sentinelle de boot et avec la liste des
# figures a joindre.
if [ "${ROULEAUX_CIBLE:-}" != "" ]; then
  if [ "$DEST" = "$ROOT/data/graines" ]; then
    echo "refus : ROULEAUX_CIBLE demande sa PROPRE destination — ses mesures ne répondent" >&2
    echo "        pas à la même question que la cohorte appariée de \`25\`." >&2
    echo "        ex. ROULEAUX_CIBLE=$ROULEAUX_CIBLE $0 data/graines_lisibles" >&2
    exit 2
  fi
  ROULEAUX=$ROULEAUX_CIBLE
fi

# ⚠⚠ La resolution a prendre quand un rouleau a PLUSIEURS scans. `PHerc1203` est scanne a
# 9,362 µm ET a 2,403 µm ; les douze autres sont tous a 8,64 ou 9,362. La campagne est une
# comparaison APPARIEE, donc le treizieme doit etre trace dans la resolution de la cohorte
# -- sinon il n'est comparable a rien, et rien ne le dirait. Un rouleau absent d'ici et a
# scan unique n'a pas de choix a faire ; un rouleau a plusieurs scans absent d'ici fait
# ECHOUER l'appariement, ce qui est le comportement voulu.
declare -A VOXEL_COHORTE=( [PHerc1203]=9.362 [PHerc0139]=9.362 [PHercParis4]=2.4 )
# ⚠ `PHercParis4` n'est PAS de la cohorte appariee -- il n'entre que par `ROULEAUX_CIBLE`,
# donc dans sa propre destination. Sa resolution est ici pour une autre raison : il a DEUX
# predictions et cinq volumes, donc l'appariement REFUSE sans resolution demandee (c'est le
# seul rouleau ou l'appariement par position donne le mauvais volume). 2,4 µm est celle ou
# `36` §5bis mesure le detecteur a AUC 0,925 -- choisir une autre resolution reviendrait a
# tracer la ou on ne sait pas lire, ce qui annulerait la raison d'y aller.

lister() { curl -s --max-time 60 "$B/?list-type=2&prefix=$1&delimiter=/" \
           | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep -vxF "$1"; }

for R in $ROULEAUX; do
  OUT="$DEST/$R.json"
  if [ -s "$OUT" ]; then echo "== $R deja fait"; continue; fi
  echo "== $R"

  # ⚠⚠ Surface et volume sont apparies par IDENTITE DE SCAN, pas par position dans deux
  # listages. La version d'avant prenait `head -1` de chacun : juste tant qu'un rouleau
  # n'a qu'un scan, et faux des qu'il en a deux si les deux listes ne se trient pas
  # pareil. La panne serait muette -- tracer la surface d'un scan avec la resolution d'un
  # autre rend une surface dont l'aire et la geometrie sont fausses d'un facteur constant,
  # sans un seul message. Mesure du 2026-08-22 : le defaut est LATENT (0 rouleau mal
  # apparie aujourd'hui), et deux rouleaux ont plusieurs scans.
  CIBLE=${VOXEL_COHORTE[$R]:-}
  if ! PAIRE=$(python3 "$ROOT/analysis/src/apparier_volumes.py" "$R" --pour-campagne \
                 ${CIBLE:+--voxel-um "$CIBLE"} 2>"$DEST/$R.appariement.log"); then
    echo "   ⚠ appariement refuse : $(cat "$DEST/$R.appariement.log")"; continue
  fi
  read -r SURF VOL UM <<<"$PAIRE"
  if [ -z "$SURF" ] || [ -z "$VOL" ] || [ -z "$UM" ]; then
    echo "   ⚠ pas de prediction ou pas de volume"; continue
  fi
  echo "   voxel $UM µm  ($(sed 's/^ *# *//' "$DEST/$R.appariement.log"))"

  WORK="$DEST/$R.trace"; rm -rf "$WORK"; mkdir -p "$WORK"
  sed "s/\"voxelsize\": [0-9.]*/\"voxelsize\": $UM/" \
      "$ROOT/artefacts/PHerc0358/seed.json" > "$WORK/seed.json"

  LIGNES=""
  for CRIT in planarite voisinage; do
    # ⚠ « voisinage » est rejoue dans SA configuration d'origine (niveau 2, bloc 5), celle
    # qui a produit la trace de docs/24. Le comparer dans la configuration de l'autre
    # critere ne dirait rien de ce qui a ete reellement fait.
    if [ "$CRIT" = planarite ]; then NIV=0; BLOC=8; else NIV=2; BLOC=5; fi
    GJ="$DEST/$R.$CRIT.json"
    ( cd "$ROOT/experiments" && timeout 1800 uv run python -u ../analysis/src/trouver_graine.py \
        "$SURF" --level $NIV --chunks 25 --bloc $BLOC --critere "$CRIT" --candidats 1 \
        --voxel-um "$UM" --out "$GJ" ) > "$DEST/$R.$CRIT.log" 2>&1
    if [ ! -s "$GJ" ]; then echo "   ⚠ $CRIT : aucune graine"; continue; fi
    read -r X Y Z <<<"$(python3 -c "
import json,sys
c=json.load(open('$GJ'))['candidats']
print(c[0]['x'], c[0]['y'], c[0]['z']) if c else sys.exit(1)")" || { echo "   ⚠ $CRIT : json vide"; continue; }

    SEG="$WORK/$CRIT"; rm -rf "$SEG"; mkdir -p "$SEG"; cp "$WORK/seed.json" "$SEG/"
    ( cd "$SEG" && timeout 1800 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
        -s "$X" "$Y" "$Z" ) > "$DEST/$R.$CRIT.trace.log" 2>&1
    AIRE=$(grep -oE 'generated surface .* \(([0-9.]+) cm\^2\)' "$DEST/$R.$CRIT.trace.log" \
           | grep -oE '\(([0-9.]+)' | tr -d '(' | tail -1)
    SURFDIR=$(ls -d "$SEG"/auto_grown_* 2>/dev/null | head -1)
    if [ -z "$SURFDIR" ]; then echo "   ⚠ $CRIT : aucune surface produite"; continue; fi
    vc_tifxyz_selfcross --surface "$SURFDIR" -o "$DEST/$R.$CRIT.selfcross.json" \
        > "$DEST/$R.$CRIT.selfcross.log" 2>&1
    # ⚠ Refus (code 3) si aucune paire n'a ete testee — voir docs/34.
    CROIS=$(python3 "$ROOT/analysis/src/lire_selfcross.py" \
              "$DEST/$R.$CRIT.selfcross.json" 2>/dev/null || echo "?")
    printf '   %-10s graine %6s %6s %6s   aire %8s cm²   auto-intersections %s\n' \
        "$CRIT" "$X" "$Y" "$Z" "${AIRE:-?}" "$CROIS"
    LIGNES="$LIGNES{\"critere\":\"$CRIT\",\"x\":$X,\"y\":$Y,\"z\":$Z,\"aire_cm2\":${AIRE:-null},\"transverse\":${CROIS:-null}},"
  done
  printf '{"rouleau":"%s","voxel_um":%s,"surface":"%s","essais":[%s]}\n' \
      "$R" "$UM" "$SURF" "${LIGNES%,}" > "$OUT"
done
echo "campagne finie — $DEST"
