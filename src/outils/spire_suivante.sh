#!/bin/bash
# ENCHAINER LES SPIRES : partir d'une surface qui CONVERGE, et generer sa voisine.
#
# ⚠⚠ CE QUE CE SCRIPT CHANGE DE STRATEGIE, et pourquoi. `42` etablit un plateau : le seam
# de correction, a tous les reglages essayes (deux rembobinages, deux poids, deux semis),
# ne transforme pas une coupe radiale en suiveuse de feuille. Le meilleur alpha obtenu est
# +0,89 quand le segment officiel est a +0,00. On arretait donc d'essayer de REDRESSER une
# trace mal orientee.
#
# ⭐⭐⭐ `vc_grow_seg_from_seed` a un mode que ce depot n'avait jamais lance :
# `mode: "gen_neighbor"`. Lu dans la source (`apps/src/vc_grow_seg_from_seed.cpp:625`), il
# prend une surface par `--resume`, tire un rayon depuis chaque sommet le long de la
# normale (`neighbor_dir` = "in" ou "out"), avance par pas de `neighbor_step` voxels, et
# s'arrete des qu'il touche de la matiere au-dessus de `neighbor_threshold`. Autrement dit
# il CONSTRUIT LA SPIRE VOISINE. C'est le « wrap by wrap copy tool » que le papier decrit,
# et il est public.
#
# ⭐ Et il n'a pas besoin d'etre redresse : on part d'un segment OFFICIEL dont la
# convergence est deja mesuree (alpha = +0,00 sur PHerc1447). La question devient donc
# celle du graal : **la convergence SURVIT-elle a l'enchainement, et sur combien de spires ?**
#
# ⚠ Conception : toutes les spires sont jugees dans les MEMES fenetres (31 et 81), celles
# ou l'officiel a ete mesure. Melanger les fenetres melangerait le reglage et la surface --
# c'est l'erreur que `38` a payee trois fois.
#
# ⚠ Un echec a une spire est un RESULTAT (« la chaine casse au tour k »), pas une panne du
# script : il est rapporte et la boucle s'arrete la, parce qu'on ne peut pas generer la
# voisine d'une surface qui n'existe pas.
#
#   ./src/outils/lancer.sh --fond src/outils/spire_suivante.sh [dest] [nombre de spires]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/spires}
N_SPIRES=${2:-4}
ROULEAU=PHerc1447
UM=8.64
SENS=${SENS:-out}
FENETRES=${FENETRES:-"31 81"}
# ⚠⚠ REPOUSSE : le nombre de generations a faire repousser APRES chaque `gen_neighbor`.
# Mesure de `43` : la grille perd **4,0 % par tour** (7,12 -> 5,39 cm2 en six tours), parce
# qu'un sommet dont le rayon ne trouve rien est perdu definitivement. `neighbor_fill` est
# deja a `true` ; ce qui manque est une repousse, c'est-a-dire ce que `mode: resume` sait
# faire.
#
# ⚠ ET C'EST UN PARI, pas une amelioration evidente : `mode: resume` fait tourner le traceur
# NON contraint, celui-la meme qui produit des coupes radiales (`42`). Faire repousser une
# bonne spire avec lui peut tres bien la tirer hors de sa feuille. D'ou le defaut a 0 (chaine
# inchangee) et la comparaison appariee : meme surface de depart, meme sens, memes fenetres,
# seule la repousse change.
REPOUSSE=${REPOUSSE:-0}
# ⚠ Le pas du rayon, en voxels. Defaut de l'outil : 1,0. C'est le levier le plus
# mecaniquement plausible pour la question « pourquoi un tour rate » : le rayon s'arrete au
# PREMIER echantillon au-dessus du seuil, donc un pas plus fin le localise plus precisement
# et peut cesser de manquer une nappe mince. Aucun autre reglage de `gen_neighbor` n'agit
# aussi directement sur ce qui est trouve ou pas.
PAS_RAYON=${PAS_RAYON:-1.0}

# ⚠⚠ LE PIEGE DU PAS, TROUVE DANS LA SOURCE LE 2026-08-21 (fin). Trois reglages de
# `gen_neighbor` comptent des PAS et non une distance, donc leur portee physique est
# silencieusement divisee quand on affine le pas :
#
#   `neighbor_exit_count`   (defaut 1) — nombre d'echantillons CONSECUTIFS sous le
#     demi-seuil qu'il faut voir pour declarer « j'ai quitte la nappe de depart »
#     (vc_grow_seg_from_seed.cpp:784). Sa portee vaut exit_count x pas :
#       pas 1,0   -> 1,0 voxel = 8,6 µm
#       pas 0,125 -> 0,125 voxel = 1,1 µm
#     A pas fin, UN SEUL echantillon sous-voxel interpole sous le demi-seuil suffit donc, et
#     le rayon peut sortir puis rentrer dans LA MEME feuille — il se pose sur la face proche
#     de sa nappe de depart au lieu de la suivante. Ca predit un ecart entre nappes plus
#     COURT, et c'est exactement ce que la mesure montre : 116 -> 109 -> 107 -> 102 µm quand
#     le pas est halve trois fois (`44` §4).
#
#   `neighbor_spike_window` (defaut 2) — alimente `max_fold_iters = spike_window * 4`
#     (:879), donc encore un compte de pas.
#
#   `neighbor_min_clearance` est le SEUL des trois exprime en distance, et la source le
#     convertit correctement (`ceil(min_clearance / neighbor_step)`, :677). L'auteur
#     connaissait donc le probleme pour celui-la ; les deux autres sont restes des comptes.
#
# ⭐ D'ou la compensation : pour garder une PORTEE PHYSIQUE constante, exit_count et
# spike_window doivent varier en 1/pas. La valeur de reference est celle du pas OPTIMAL
# mesure (0,25) avec les defauts, soit une portee de 0,25 voxel pour la sortie.
# Laisser ces variables vides garde les defauts de l'outil (aucune compensation).
SORTIE_PAS=${SORTIE_PAS:-}          # neighbor_exit_count
FENETRE_PIC=${FENETRE_PIC:-}        # neighbor_spike_window
DISTANCE_MAX=${DISTANCE_MAX:-250.0} # neighbor_max_distance, en VOXELS (une distance, elle)
DEGAGEMENT=${DEGAGEMENT:-}          # neighbor_min_clearance, en VOXELS (une distance aussi)
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr"
# ⚠⚠ LE SEGMENT DE DEPART DOIT CONVERGER, et le choisir sur son nom ne suffit pas. Paye le
# 2026-08-21 : `data/trace/PHerc1447_officiel/` porte « officiel » dans son nom, donc je l'ai
# pris pour le bon. Mesure : alpha = +1,02, 72 a 78 % de fenetres dont le pic tombe au BORD
# — il ne converge pas. Le segment qui converge est celui de `origine_pile`
# (17,28 um a 81 couches, 0 % de pics au bord). `36` avait deja etabli que « officiel »
# n'est pas synonyme de « bon » ; ici c'est le test de convergence qui le redit.
SOURCE=${SOURCE:-$ROOT/data/origine_pile/mesh.tifxyz}
[ -d "$SOURCE" ] || { echo "surface de depart absente : $SOURCE" >&2; exit 3; }
SURF=$(curl -s --max-time 60 "$B/?list-type=2&prefix=$ROULEAU/representations/predictions/surfaces/&delimiter=/" \
       | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$' | head -1 | sed 's|/$||')
[ -z "$SURF" ] && { echo "pas de prediction publiee pour $ROULEAU" >&2; exit 3; }
# ⚠⚠ LES VERDICTS PORTENT L'ETIQUETTE DE LA CAMPAGNE, et ca a ete paye. `juger` ecrivait
# `docs/spire_<nom>.json` sans tenir compte du repertoire de destination : deux campagnes
# (avec et sans repousse) ecrivaient donc dans LES MEMES fichiers, et la seconde ecrasait la
# ligne de base de la premiere **pendant** qu'on croyait les comparer. Pire, `table_chaine.py`
# lit ces fichiers : relancer le depouillement de la campagne A aurait rendu les chiffres de
# la campagne B, sans que rien n'ait l'air faux.
#
# ⚠⚠⚠ LA FONCTION DE JUGEMENT EST ADOPTEE, PLUS RECOPIEE. Ce fichier en portait une copie
# verbatim, `etendre_nappe.sh` une autre, et les deux avaient DEJA diverge : la reserve
# `--au-bord` avait ete cablee dans l'une avant l'autre. `juger_nappe.sh` avait ete ecrit pour
# les remplacer et n'avait jamais ete adopte -- il y avait donc TROIS exemplaires.
#
# ⚠⚠ LE PLAFOND DE CROISEMENTS EST DESACTIVE ICI, et c'est deliberе : la copie que portait ce
# fichier ne l'avait pas, et un refactor ne change pas le comportement d'une campagne qui a
# produit des resultats publies. L'activer est une decision a prendre a part.
#
# ⭐ Equivalence PROUVEE avant l'adoption : le chemin effectif de `juger_nappe` avec le
# plafond vide fait 41 lignes contre 41 pour l'ancien `juger()` de ce fichier, et la seule
# difference est la POSITION d'un `echo` -- le calcul qui les separe est capture par `$(...)`
# et n'affiche rien, donc rien d'observable ne change.
# ⚠ Sur leurs PROPRES lignes, pas en prefixe de `.` : une affectation en prefixe d'un builtin
# special a une semantique subtile, et un test l'a montre -- `PLAFOND` prenait, `LIGNES_VERDICT`
# non. Deux lignes ne laissent aucun doute.
PLAFOND_CROISEMENTS_PAR_CM2=""
LIGNES_VERDICT=3
. "$(dirname "${BASH_SOURCE[0]}")/juger_nappe.sh"
juger() { juger_nappe "$1" "$2" "$3" "spire_${ETIQUETTE}"; }

# --- spire 0 : la surface de depart, jugee par NOTRE chaine ---------------------
# ⚠ On la rejuge ici plutot que de reprendre le chiffre de `38` : la comparaison doit
# passer par la meme chaine que les spires generees, sinon un ecart entre la spire 0 et la
# spire 1 melangerait la surface et le chemin de mesure.
W0="$DEST/spire00"
mkdir -p "$W0"
# ⚠ Si la surface de depart a deja un aplatissement (cas de `origine_pile`), on le reutilise
# plutot que d'en refaire un : deux aplatissements de la meme surface n'ont aucune raison
# d'etre identiques, et la spire 0 doit etre jugee sur celui qui a servi a la mesurer.
if [ ! -d "$W0/plat" ] && [ -d "$(dirname "$SOURCE")/plat" ]; then
  ln -s "$(cd "$(dirname "$SOURCE")/plat" && pwd)" "$W0/plat"
  echo "  aplatissement de depart reutilise : $(dirname "$SOURCE")/plat"
fi
juger "$W0" "$SOURCE" "spire00" || { echo "la surface de depart ne se juge pas — la chaine ne dit RIEN" >&2; exit 4; }

# ⚠⚠ REFUSER DE PARTIR D'UNE SURFACE QUI NE CONVERGE PAS. Generer la voisine d'une surface
# posee en travers de l'empilement ne peut pas donner une surface posee sur une feuille : on
# mesurerait la propagation d'un defaut, pas une chaine. Et le resultat aurait l'air d'un
# resultat. Le verdict est LU dans le JSON du juge, pas suppose.
V0=$(python3 -c "
import json
print(json.load(open('$ROOT/docs/mesures/spire_${ETIQUETTE}spire00.json'))['series'][0]['verdict'])" 2>/dev/null)
if [ "$V0" != "converge" ]; then
  echo "REFUS : la surface de depart ne converge pas (verdict « ${V0:-inconnu} »)." >&2
  echo "  Enchainer depuis elle mesurerait la propagation d'un defaut, pas une chaine." >&2
  echo "  Choisir une autre surface avec SOURCE=<chemin vers un mesh.tifxyz>." >&2
  exit 5
fi
echo "spire 0 converge — on peut enchainer"

PREC=$SOURCE
for k in $(seq 1 "$N_SPIRES"); do
  KK=$(printf '%02d' "$k")
  W="$DEST/spire$KK"
  # ⚠⚠ Meme garde que `boucle_de_correction.sh`, et pour la meme raison : supprimer un
  # artefact n'arrete pas le travail, parce que le cache d'un rendu EST le signal d'arret du
  # script. Une decision humaine d'abandon s'ecrit dans un fichier que le script LIT.
  if [ -f "$DEST/ABANDONNE" ] || [ -f "$W/ABANDONNE" ]; then
    echo "== spire$KK : campagne ABANDONNEE — $(head -3 "$DEST/ABANDONNE" "$W/ABANDONNE" 2>/dev/null | tail -1)"
    break
  fi
  if [ ! -d "$W/trace" ]; then
    mkdir -p "$W/trace"
    python3 -c "
import json
par = {'mode': 'gen_neighbor', 'voxelsize': $UM, 'thread_limit': 0,
       'cache_size': 6000000000,
       'neighbor_dir': '$SENS', 'neighbor_step': $PAS_RAYON,
       'neighbor_max_distance': $DISTANCE_MAX, 'neighbor_threshold': 1.0,
       'neighbor_fill': True}
# ⚠ On n'ecrit un reglage que s'il est demande : ecrire le defaut de l'outil a la main
# ferait mentir le meta du maillage sur ce qui a ete choisi et ce qui a ete subi.
for cle, val in (('neighbor_exit_count', '$SORTIE_PAS'),
                 ('neighbor_spike_window', '$FENETRE_PIC'),
                 ('neighbor_min_clearance', '$DEGAGEMENT')):
    if val:
        par[cle] = float(val) if '.' in val else int(val)
json.dump(par, open('$W/trace/seed.json','w'), indent=2)"
    ( cd "$W/trace" && timeout 7200 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
        --resume "$PREC" > trace.log 2>&1 )
  fi
  # ⚠⚠ `gen_neighbor` nomme sa sortie `neighbor_<sens>_<horodatage>`, PAS `auto_grown_*` ni
  # `*.tifxyz`. Paye le 2026-08-21 : le journal disait « AUCUN MAILLAGE — la chaine casse au
  # tour 1 » alors que le maillage etait la, avec ses x.tif/y.tif/z.tif et son meta.json, et
  # que le log de trace annoncait « Output grid: 157x145 ». Un faux negatif produit par mon
  # propre glob, et qui avait exactement la forme du resultat attendu.
  M=$(ls -d "$W/trace"/neighbor_* 2>/dev/null | head -1)
  [ -z "$M" ] && M=$(ls -d "$W/trace"/auto_grown_* 2>/dev/null | head -1)
  [ -z "$M" ] && M=$(ls -d "$W/trace"/*.tifxyz 2>/dev/null | head -1)
  if [ -z "$M" ]; then
    echo "== spire$KK : AUCUN MAILLAGE — la chaîne casse au tour $k"
    sed 's/^/   /' "$W/trace/trace.log" | tail -6
    break
  fi
  # --- repousse optionnelle, avant de juger -----------------------------------
  if [ "$REPOUSSE" -gt 0 ] && [ ! -d "$W/repousse" ]; then
    mkdir -p "$W/repousse"
    python3 -c "
import json
json.dump({'mode': 'resume', 'voxelsize': $UM, 'thread_limit': 0,
           'cache_size': 6000000000, 'step_size': 20.0, 'search_effort': 10,
           'min_area_cm': 0.3, 'resume_generations': $REPOUSSE},
          open('$W/repousse/seed.json','w'), indent=2)"
    ( cd "$W/repousse" && timeout 7200 vc_grow_seg_from_seed -v "$B/$SURF" -t . \
        -p seed.json --resume "$M" > trace.log 2>&1 )
    MR=$(ls -d "$W/repousse"/auto_grown_* 2>/dev/null | head -1)
    [ -z "$MR" ] && MR=$(ls -d "$W/repousse"/neighbor_* 2>/dev/null | head -1)
    if [ -n "$MR" ]; then
      A_AV=$(python3 src/nappe/lire_selfcross.py "$W/selfcross.json" --grille 2>/dev/null || echo "? ?")
      echo "   repousse de $REPOUSSE generations : $(basename "$MR")"
      M=$MR
      rm -f "$W/selfcross.json"     # le verdict doit porter sur la surface REPOUSSEE
      rm -rf "$W/plat"
    else
      # ⚠ Une repousse qui ne produit rien est un RESULTAT sur la repousse, pas une panne :
      # on juge alors la spire non repoussee, et on le DIT, sinon le tableau melangerait
      # silencieusement des spires repoussees et des spires qui ne l'ont pas ete.
      echo "   ⚠ repousse SANS EFFET (aucun maillage) — la spire est jugée non repoussée"
      sed 's/^/      /' "$W/repousse/trace.log" | tail -3
    fi
  fi

  juger "$W" "$M" "spire$KK" || break
  PREC=$M
done
echo "fin — $(ls -d "$DEST"/spire* 2>/dev/null | wc -l) spire(s) traitée(s)"
