#!/bin/bash
# Laquelle des deux predictions de PHercParis4 donne une trace qui SUIT UNE FEUILLE ?
#
# ⚠⚠ Le critere, et pourquoi ce n'est pas un proxy. `campagne_prediction_paris4.sh` mesure
# ce que chaque prediction OFFRE : `ps256` propose une graine a occupation 0,0215 -- le
# plancher admissible est 0,02 -- et `m7` une a occupation 0,75 avec une planarite de 1,0,
# le plafond etant 0,80. Les deux sont aux extremes de la bande, et « tout est surface ET
# parfaitement plan » est la signature d'une prediction SATUREE que `39` §3 decrit : il n'y
# a alors aucun gradient a suivre. Les scores ne peuvent donc pas trancher.
#
# ⭐ Ce qui tranche est le test de convergence de `38` : on trace la meilleure graine de
# chacune, avec des parametres identiques, on rend la surface a DEUX profondeurs de fenetre
# et on lit l'exposant alpha. Une trace posee sur sa feuille rend alpha ~ 0 ; une trace
# posee en travers de l'empilement rend alpha ~ 1, parce que son « pic » n'est que la chose
# la plus forte que la fenetre contenait.
#
# ⚠ Le volume est celui du SCAN des predictions, derive et jamais ecrit -- la version
# precedente de la campagne avait emprunte la resolution d'un rouleau voisin, et le chiffre
# se lisait comme juste.
#
# ⚠⚠ C'est cher. Le rouleau est scanne a 2,4 µm, donc un meme volume physique porte ~64 fois
# plus de voxels qu'un rouleau du prix a 9,4 µm. `GENERATIONS` borne la pousse pour que le
# premier essai reponde en un temps fini ; une trace tronquee ne dit rien de la convergence
# d'une trace complete, et le plafond est donc RAPPORTE a cote du verdict -- c'est
# exactement la lecon de `35`.
#
# ⚠⚠ UNE CELLULE = UN TIRAGE, ET LE TRACEUR EST UN TIRAGE. C'est le constat fondateur de
# `30` et `35`, et il vaut jusqu'ici : la MEME graine, dans la MEME prediction, au MEME
# plafond et a la MEME echelle, a rendu alpha = +0,89 puis +1,12 sur deux executions --
# 0,23 d'ecart, soit PLUS que la resolution de +-0,2 que `38` §3.4 declare pour son propre
# alpha. Le premier run lisait 41c→48,00 (le plafond) et le second 41c→38,40 (une vraie
# mesure) : les deux tirages n'ont meme pas trouve la meme chose.
#
# ⚠ Donc ce 2×2 a un tirage par cellule ne peut PAS separer trois facteurs -- la prediction,
# l'endroit, et le bruit de tirage. Il donne une premiere forme ; conclure demande de
# repeter chaque cellule. C'est le meme piege que `35` a documente pour l'aire, applique a
# alpha, et je l'ai vu en comparant deux runs que je croyais identiques.
#
# ⚠ Reprenable a chaque etape : ce qui existe est saute.
#
#   ./tools/tracer_prediction_paris4.sh [dest]
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/prediction_paris4}
# ⚠⚠ RENDRE LA DESTINATION ABSOLUE. Plusieurs etapes s'executent depuis un autre repertoire
# (`inference_xpu` pour le profil de profondeur), donc un chemin relatif passe en argument
# se resout ailleurs et le fichier « n'existe pas » alors qu'il vient d'etre ecrit. Paye le
# 2026-08-22 : le rendu a produit 148 Mo et l'etape suivante a rapporte
# `FileNotFoundError: data/paris4_croise/.../rendu_41`. Un script qui marche ou casse selon
# la forme de son argument est un script qui casse.
case "$DEST" in /*) ;; *) DEST="$ROOT/$DEST" ;; esac
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
S="PHercParis4/representations/predictions/surfaces"
GENERATIONS=${GENERATIONS:-60}
FENETRES=${FENETRES:-"41 161"}
# ⚠⚠ L'ECHELLE DU RENDU, et pourquoi elle est un parametre. Mesure du 2026-08-22 : a
# `--scale 1` sur ce rouleau a 2,4 µm, une surface de 3,65 cm² rendait ~57 Ko/s, soit plus
# de DOUZE HEURES pour une fenetre -- et quatre fois plus pour la fenetre a 161 couches.
#
# ⭐ Une echelle plus grossiere reduit l'echantillonnage DANS LE PLAN, pas le long de la
# normale : le profil de profondeur mesure le long de la normale au pas de `--slice-step`,
# donc ses microns restent des microns. Ce qui change est le NOMBRE de fenetres, plus
# grosses et moins nombreuses -- c'est une vraie difference de mesure, et c'est pourquoi
# les DEUX predictions sont rendues a la meme echelle. La comparaison reste une
# comparaison ; c'est la valeur absolue qui n'est pas comparable a un run a l'echelle 1.
ECHELLE=${ECHELLE:-1}
# ⚠ Patience du chien de garde, en secondes SANS croissance de la sortie. Le temps ecoule
# ne dit rien -- un rendu long n'est pas un rendu bloque.
PATIENCE=${PATIENCE:-300}

declare -A PRED=(
  [ps256]="$S/20260411134726-surface-20260413141734-surface-recto-2um-ps256-L0-th0.45.zarr"
  [m7]="$S/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr"
)

SCAN=$(basename "${PRED[ps256]}" | cut -d- -f1)
VOLS=$(curl -s --max-time 60 "$B/?list-type=2&prefix=PHercParis4/volumes/$SCAN&delimiter=/" \
       | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$')
if [ "$(printf '%s\n' "$VOLS" | grep -c .)" -ne 1 ]; then
  echo "refus : le scan $SCAN ne designe pas exactement un volume" >&2; exit 3
fi
VOL=$(printf '%s' "$VOLS" | sed 's|/$||')
UM=$(printf '%s' "$VOL" | grep -oE '[0-9]+\.[0-9]+um' | head -1 | sed 's/um$//')
[ -n "$UM" ] || { echo "refus : resolution illisible sur $VOL" >&2; exit 3; }
echo "== volume $(basename "$VOL")  ($UM µm)  ·  plafond $GENERATIONS generations  ·  échelle $ECHELLE"

# ⚠⚠ UN 2×2, ET PAS DEUX TRACES. Chaque prediction propose sa meilleure graine, et les deux
# tombent a des endroits TOTALEMENT DIFFERENTS du rouleau -- (10752, 10616, 38740) contre
# (2924, 5324, 9260). Tracer chacune dans sa propre prediction confond donc « quelle
# prediction » avec « quel endroit », a n'importe quel plafond de generations : c'est un
# defaut de conception, pas de budget.
#
# ⭐ Les deux predictions couvrent LE MEME VOLUME, donc une graine est une coordonnee valide
# dans les deux. On trace les DEUX graines dans les DEUX predictions. Si une prediction est
# meilleure, elle gagne aux deux graines ; si c'est l'endroit qui compte, les deux
# predictions se comportent pareil a chaque graine. Le 2×2 separe les deux facteurs, et
# c'est la conception appariee que `campagne_graines.sh` defend deja.
for GRAINE in ps256 m7; do
 G="$DEST/graine_$GRAINE.json"
 [ -s "$G" ] || { echo "== graine $GRAINE absente — lancer campagne_prediction_paris4.sh"; continue; }
 read -r X Y Z <<<"$(python3 -c "
import json,sys
c=json.load(open('$G'))['candidats']
print(c[0]['x'], c[0]['y'], c[0]['z']) if c else sys.exit(1)")" || { echo "== graine $GRAINE : json vide"; continue; }
 for NOM in ps256 m7; do
  CAS="${NOM}_sur_graine_${GRAINE}"

  W="$DEST/$CAS"; mkdir -p "$W"
  echo "== prédiction $NOM · graine de $GRAINE  ($X $Y $Z)"

  # ⚠ Le seed.json de reference, avec SA resolution et SON plafond. Le patcher plutot que
  # d'en ecrire un neuf garde tous les autres parametres identiques entre les deux
  # predictions -- c'est ce qui fait de la comparaison une comparaison.
  if [ ! -s "$W/seed.json" ]; then
    python3 - "$ROOT/artefacts/PHerc0358/seed.json" "$W/seed.json" "$UM" "$GENERATIONS" <<'PY'
import json, sys
src, dst, um, gen = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
d = json.load(open(src))
d["voxelsize"] = um
d["generations"] = gen
json.dump(d, open(dst, "w"), indent=2)
PY
  fi

  M=$(ls -d "$W"/auto_grown_* 2>/dev/null | head -1)
  # ⚠⚠ RAPPORTER LE BUDGET DE LA TRACE, PAS CELUI QU'ON A DEMANDE. Le script saute la pousse
  # quand une surface existe deja -- et son `seed.json` peut porter un tout autre plafond que
  # la variable d'environnement du run courant. Paye le 2026-08-22 : la campagne a imprime
  # « plafond 60 generations » en jugeant une trace poussee a 200. Un en-tete qui decrit
  # l'intention plutot que l'artefact est un nombre qui ment.
  BUDGET=$(python3 -c "
import json,sys
try: print(json.load(open('$W/seed.json'))['generations'])
except Exception: print('$GENERATIONS')" 2>/dev/null)
  if [ -n "$M" ] && [ "$BUDGET" != "$GENERATIONS" ]; then
    echo "   ⚠ surface déjà là, poussée à $BUDGET générations (et non $GENERATIONS demandées)"
  fi
  if [ -z "$M" ]; then
    ( cd "$W" && timeout 7200 vc_grow_seg_from_seed -v "$B/${PRED[$NOM]}" -t . \
        -p seed.json -s "$X" "$Y" "$Z" ) > "$W/trace.log" 2>&1
    M=$(ls -d "$W"/auto_grown_* 2>/dev/null | head -1)
  fi
  if [ -z "$M" ]; then
    # ⚠⚠ « aucune surface » est un RESULTAT sur cette prediction, pas une panne du script :
    # une prediction saturee ne donne rien a suivre, et c'est precisement ce qu'on teste.
    echo "   ⚠ aucune surface produite — resultat sur $NOM, pas panne du script"
    tail -3 "$W/trace.log" 2>/dev/null | sed 's/^/     /'
    continue
  fi
  AIRE=$(grep -oE 'generated surface .* \(([0-9.]+) cm\^2\)' "$W/trace.log" \
         | grep -oE '\(([0-9.]+)' | tr -d '(' | tail -1)
  vc_tifxyz_selfcross --surface "$M" -o "$W/selfcross.json" > /dev/null 2>&1
  CROIS=$(python3 "$ROOT/analysis/src/lire_selfcross.py" "$W/selfcross.json" 2>/dev/null || echo "?")
  [ -d "$W/plat" ] || vc_flatten -i "$M" -o "$W/plat" > "$W/flatten.log" 2>&1

  SERIE=""; PROFILS=""
  for N in $FENETRES; do
    OUT="$W/profil_${N}c.json"
    if [ ! -s "$OUT" ]; then
      rm -rf "$W/rendu_$N"
      if ! "$ROOT/tools/rendre_surveille.sh" "$W/rendu_$N" "$PATIENCE" -- \
          -v "$W/cache" --remote-url "$B/$VOL" --scale "$ECHELLE" -g 0 -s "$W/plat" \
          --tif-output "$W/rendu_$N" -n "$N" --slice-step 1 --auto-crop \
          > "$W/rendu_$N.log" 2>&1; then
        echo "   ⚠ rendu $N couches abandonné :"
        sed 's/^/     /' "$W/rendu_$N.log" | tail -4
        continue
      fi
      sed -n '/rendu :/p' "$W/rendu_$N.log"
      ( cd "$ROOT/inference_xpu" && uv run python ../analysis/src/depth_profile.py \
          "$W/rendu_$N" --grid --step 200 --traced-layer $((N / 2)) --voxel-um "$UM" \
          --out "$OUT" ) > "$W/profil_$N.log" 2>&1 || { echo "   ⚠ profil $N echoue"; continue; }
    fi
    E=$(python3 -c "
import json; d=json.load(open('$OUT')); d=d[0] if isinstance(d,list) else d
print(f\"{d['ecart_trace_um_median']:.2f}\")" 2>/dev/null) || continue
    SERIE="$SERIE$N:$E,"
    PROFILS="$PROFILS --profil $OUT"
  done
  rm -rf "$W/cache"
  echo "   aire ${AIRE:-?} cm²  croisements ${CROIS:-?}  série ${SERIE%,}"
  if [ -n "$PROFILS" ]; then
    # ⚠⚠ `--profil` et pas `--serie` : le juge lit alors l'amplitude et la part au bord DANS
    # le profil, donc il refuse quand le profil est plat. La premiere version recopiait les
    # ecarts a la main, et a rendu un verdict confiant « suit la fenetre » sur un profil
    # dont l'amplitude etait nulle -- voir `49`. Recopier un nombre, c'est perdre ce qui
    # l'accompagne.
    ( cd "$ROOT/experiments" && uv run python ../analysis/src/test_convergence.py \
        $PROFILS --nom "$CAS (${AIRE:-?} cm²)" \
        --json "$ROOT/docs/prediction_paris4_$CAS.json" | tail -4 )
  else
    echo "   ⚠ aucune fenetre rendue — pas de verdict de convergence"
  fi
 done
done
