#!/bin/bash
# ETENDRE UNE NAPPE LE LONG D'ELLE-MEME : le compromis entre extension et derive.
#
# ⚠⚠ POURQUOI CET OUTIL EXISTE. `44` §7 etablit qu'une chaine RADIALE (`gen_neighbor`) est une
# COLONNE de nappes dans une meme fenetre angulaire, pas une bande de papyrus deroule : deux
# nappes voisines sont separees, le long du papyrus, par la circonference entiere qu'on ne
# possede pas. Pour un morceau de rouleau DEROULE il faut etendre une nappe le long
# d'elle-meme -- tangentiellement -- et aucun mode de `vc_grow_seg_from_seed` ne le fait :
#   - `gen_neighbor` projette le long des normales, donc radialement, et rien d'autre ;
#   - `expansion` repart en croissance libre depuis un germe tire au hasard (et son rng est
#     seme par l'horloge, donc il n'est meme pas rejouable) ;
#   - `resume` reprend une surface et la laisse repousser -- c'est le seul candidat.
#
# ⭐ ET LA QUESTION N'A JAMAIS ETE POSEE PROPREMENT. La campagne `spires_repousse` de `43` §6
# a bien fait repousser, mais avec `resume_generations = 20` et cette valeur SEULE, sur des
# surfaces deja projetees. Mesure : 7,12 -> 12,54 cm2 (+76 % d'aire) pour α = +0,422. Donc
# `resume` etend REELLEMENT, et il derive des le premier coup -- mais on ne sait rien de ce
# qui se passe entre 1 et 20 generations.
#
# ⭐⭐ CE QUE CET OUTIL MESURE : le compromis, en balayant `resume_generations` sur LA MEME
# surface convergente. Si un regime existe ou la surface gagne de l'aire en restant
# convergee, la chaine tangentielle est possible ; si α monte des que l'aire monte, elle ne
# l'est pas -- et c'est une reponse aussi utile, parce qu'elle ferme une piste.
#
# ⚠ Conception APPARIEE : meme source, meme aplatissement de depart, memes fenetres de rendu,
# une seule variable. Sans ca un ecart melangerait la surface et le reglage -- l'erreur que ce
# depot a payee trois fois le 2026-08-20.
#
# Usage :
#   ./src/outils/lancer.sh --fond src/outils/etendre_nappe.sh <dest> [generations...]
#   GENERATIONS="100 200 400" ./src/outils/lancer.sh --fond src/outils/etendre_nappe.sh "$PWD/data/ext"
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD

DEST=${1:?donner un dossier de destination}
shift || true
# ⚠⚠ LA CLE EST `generations`, PAS `resume_generations`. Piege paye le 2026-08-22 : la
# premiere version de ce script ecrivait `resume_generations`, qui est ce que la ligne de
# commande de l'outil accepte (`--resume-generations`, app :308) et que le JSON de la
# campagne `spires_repousse` porte aussi. Or dans `GrowPatch.cpp`, `resume_generations`
# n'est JAMAIS une cle de parametres : c'est une variable locale, le canal de generations
# par sommet de la surface reprise (:3493, :3579). Ce que le traceur lit reellement est
# `params.value("generations", 100)` (:3428). La cle ecrite par l'application n'est donc
# relue par personne, et TOUS nos runs ont tourne a 100 generations -- ce que le journal
# confirme (« gen 96, 97, 98, 99 »).
#
# ⭐ Consequence sur l'interpretation : la campagne `spires_repousse` (`resume_generations:
# 20`) et les premiers essais de ce script (1, 3, 10) ont tous fait la MEME chose. La
# difference mesuree entre eux ne peut donc pas venir du nombre de generations -- elle vient
# de la SOURCE, projetee dans un cas, officielle dans l'autre.
#
# ⭐ Ce que `generations` controle vraiment : `stop_gen`, donc a la fois quand la croissance
# s'arrete ET la taille de la grille de travail, via
# `gen_diff = stop_gen - start_gen` -> `grow_max_extra_cols/rows` (:3510-3515), par-dessus
# une marge fixe de 25 cellules de chaque cote. C'est donc le budget d'EXTENSION.
GENERATIONS=${GENERATIONS:-${*:-"100 200 400"}}

# ⚠⚠ DEUX MODES, et la difference compte pour ce qu'on mesure.
#   - BALAYAGE (defaut) : chaque reglage repart de LA MEME source. Conception appariee, donc
#     on mesure ce que le reglage fait, et rien d'autre.
#   - ENCHAINEMENT (`ENCHAINER=N`) : chaque pas repart de l'extension precedente, comme
#     `spire_suivante.sh` le fait radialement. C'est ce qui produirait une BANDE qui grandit,
#     mais ça compose aussi les erreurs — donc on refuse d'enchainer depuis une extension qui
#     ne converge pas, exactement comme la chaine radiale refuse un depart non convergent.
#
# ⚠ Ce sont deux questions differentes et il ne faut pas les melanger : le balayage dit
# « jusqu'ou un seul pas peut aller », l'enchainement dit « les pas se composent-ils ».
ENCHAINER=${ENCHAINER:-0}

ROULEAU=${ROULEAU:-PHerc1447}
SOURCE=${SOURCE:-$ROOT/data/origine_pile/mesh.tifxyz}
SURF=${SURF:-PHerc1447/representations/predictions/surfaces/20250521151220-surface-20260413222639-surface-m7-L0-th0.2.zarr}
FENETRES=${FENETRES:-"31 81"}
UM=${UM:-8.64}
# ⚠ Meme garde que `spire_suivante.sh` : `min_area_cm` borne la surface minimale d'un
# morceau garde. On reprend la valeur de la campagne de repousse pour que la comparaison
# avec son point a 20 generations reste appariee.
AIRE_MIN=${AIRE_MIN:-0.3}

# ⚠⚠⚠ `mode: resume` N'EST PAS DETERMINISTE PAR DEFAUT, et ça a failli me faire publier un
# tirage pour une propriete. Deux causes, toutes deux dans `GrowPatch.cpp` :
#
#   1. Le generateur aleatoire des perturbations est `thread_local` et, SANS GRAINE, il est
#      seme par `std::random_device` (:99-107). Avec 22 threads OpenMP, ça fait 22
#      generateurs irreproductibles. La graine se pose par la variable d'environnement
#      **`VC_GROWPATCH_RNG_SEED`** (:83) -- pas par une cle de parametres, et la fonction
#      `set_random_perturbation_seed` est marquee `[[maybe_unused]]`, donc jamais appelee.
#
#   2. Le nombre de threads. L'outil l'ecrit lui-meme au demarrage : « tracing does not
#      scale past a few threads. Set "thread_limit" in the params JSON (VC3D uses 1) ».
#      Meme graine identique sur tous les threads, l'ORDRE d'attribution du travail peut
#      varier -- d'ou `thread_limit: 1`.
#
# ⭐ La preuve que ça comptait : trois runs cense partager leurs parametres effectifs ont
# donne 0, 596 et 0 auto-intersections, et α = +0,000 / +0,422 / +0,000. Ce n'etait pas le
# parametre balaye (il est ignore), c'etait l'alea.
GRAINE=${GRAINE:-20260822}
FILS=${FILS:-1}
export VC_GROWPATCH_RNG_SEED="$GRAINE"

B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr"

ETIQUETTE=$(basename "$DEST"); ETIQUETTE=${ETIQUETTE#data_}
echo "etiquette des verdicts : extension_${ETIQUETTE}_<generations>.json"
echo "source : $SOURCE"
echo "generations balayees : $GENERATIONS   fenetres : $FENETRES   min_area_cm : $AIRE_MIN"
echo "  (cle JSON : 'generations' — 'resume_generations' n'est lu par personne, cf. en-tete)"
echo "  reproductibilite : VC_GROWPATCH_RNG_SEED=$GRAINE, thread_limit=$FILS"

[ -d "$SOURCE" ] || { echo "source absente : $SOURCE"; exit 3; }
mkdir -p "$DEST"

# ⚠⚠ LA SOURCE DOIT CONVERGER, et son nom ne le dit pas. Paye le 2026-08-21 : un dossier
# nomme `PHerc1447_officiel` contenait un segment a α = +1,02. On relit donc le verdict
# ECRIT plutot que de se fier au chemin. Si aucun verdict n'existe, on refuse : etendre une
# surface posee en travers ne mesure rien du tout.
VERDICT_SOURCE=${VERDICT_SOURCE:-$ROOT/docs/spire_pas025_spire00.json}
if [ -s "$VERDICT_SOURCE" ]; then
  V=$(python3 -c "
import json,sys
d=json.load(open('$VERDICT_SOURCE'))
print(d['series'][0].get('verdict','?'))" 2>/dev/null || echo "?")
  if [ "$V" != "converge" ]; then
    echo "REFUS : la source ne converge pas (verdict « $V » dans $(basename "$VERDICT_SOURCE"))."
    echo "  Etendre une surface posee en travers de l'empilement ne mesure rien."
    exit 4
  fi
  echo "source verifiee : converge"
else
  echo "REFUS : aucun verdict pour la source ($VERDICT_SOURCE)."
  echo "  Juger la source d'abord — un depart non juge rend toute comparaison illisible."
  exit 4
fi

# --- juger une surface, exactement comme `spire_suivante.sh` le fait ------------------
# ⚠⚠ Un plafond de croisements PAR CENTIMETRE CARRE, verifie AVANT de payer les rendus.
# Mesure du 2026-08-22 sur le balayage du budget d'extension :
#   budget 100 -> 12,97 cm2,     0 croisement     -> α = +0,000, converge
#   budget 200 -> 28,62 cm2,  25 036 croisements  -> α = +1,313, en travers
#   budget 400 -> 78,30 cm2, 168 104 croisements  -> (inutile de juger)
# Soit 0, 875 et 2147 croisements par cm2. Le seuil est pose a 100/cm2 : un ordre de grandeur
# au-dessus du bon cas et presque un ordre en dessous du premier mauvais.
#
# ⚠ CE N'EST PAS UN CRITERE DE QUALITE, et `43` §4 explique pourquoi : un compte de
# croisements est une propriete de l'ECHANTILLONNAGE autant que de la surface (le meme
# maillage decime passe de 240 a 49). Ce plafond ne sert donc qu'a une chose : ne pas bruler
# vingt minutes de rendu sur une surface qui s'est manifestement repliee sur elle-meme. Une
# surface sous le plafond n'est pas declaree bonne pour autant -- elle est jugee normalement.
PLAFOND_CROISEMENTS_PAR_CM2=${PLAFOND_CROISEMENTS_PAR_CM2:-100}

juger() {
  local W=$1 M=$2 NOM=$3
  [ -s "$W/selfcross.json" ] || vc_tifxyz_selfcross --surface "$M" -o "$W/selfcross.json" > /dev/null 2>&1
  local CROIS SERIE AIRE
  CROIS=$(python3 "$ROOT/src/nappe/lire_selfcross.py" "$W/selfcross.json" 2>/dev/null || echo "?")
  AIRE=$(python3 -c "
import json;print(f\"{json.load(open('$M/meta.json'))['area_cm2']:.2f}\")" 2>/dev/null || echo "?")
  # ⭐ La porte, avant les rendus.
  if [ "$CROIS" != "?" ] && [ "$AIRE" != "?" ]; then
    local TROP
    TROP=$(python3 -c "
c, a, p = $CROIS, $AIRE, $PLAFOND_CROISEMENTS_PAR_CM2
print(1 if a > 0 and c / a > p else 0)" 2>/dev/null || echo 0)
    if [ "$TROP" = "1" ]; then
      echo "== $NOM  ($AIRE cm², $CROIS auto-intersections)"
      echo "   ⚠⚠ REPLIEE : $(python3 -c "print(f'{$CROIS/$AIRE:.0f}')") croisements/cm², " \
           "au-dessus du plafond de $PLAFOND_CROISEMENTS_PAR_CM2 — rendus NON payés."
      echo "   (mesuré : 0/cm² sur la surface qui converge, 875/cm² sur la première qui casse)"
      touch "$W/ABANDONNE"
      return 1
    fi
  fi
  [ -d "$W/plat" ] || vc_flatten -i "$M" -o "$W/plat" > "$W/flatten.log" 2>&1
  [ -d "$W/plat" ] || { echo "== $NOM : $AIRE cm², $CROIS croisements — vc_flatten a échoué"; return 1; }
  SERIE=""
  for N in $FENETRES; do
    local OUT="$W/profil_${N}c.json"
    if [ ! -s "$OUT" ]; then
      rm -rf "$W/rendu_$N"
      vc_render_tifxyz -v "$W/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$W/plat" \
          --tif-output "$W/rendu_$N" -n "$N" --slice-step 1 --auto-crop \
          > "$W/rendu_$N.log" 2>&1 || continue
      ( cd "$ROOT/inference_xpu" && uv run python ../src/volume/depth_profile.py \
          "$W/rendu_$N" --grid --step 400 --traced-layer $((N / 2)) --voxel-um "$UM" \
          --out "$OUT" ) > "$W/profil_$N.log" 2>&1 || continue
    fi
    local E_UM
    E_UM=$(python3 -c "
import json; d=json.load(open('$OUT')); d=d[0] if isinstance(d,list) else d
print(f\"{d['ecart_trace_um_median']:.2f}\")" 2>/dev/null) || continue
    SERIE="$SERIE$N:$E_UM,"
  done
  rm -rf "$W/cache"
  [ -z "$SERIE" ] && { echo "== $NOM : $AIRE cm², $CROIS croisements — aucun profil"; return 1; }
  echo "== $NOM  ($AIRE cm², $CROIS auto-intersections)"
  # ⚠ Le complement d'α, lu dans le profil de la fenetre la plus ETROITE — c'est la que
  # « le pic tombe au bord » a un sens, une fenetre large finissant par contenir quelque
  # chose. α est une mediane et ne montre pas cette part ; sans elle un verdict se lit trop
  # bien (mesure : une extension a α = +0,000 dont 9,1 % des fenetres sont au bord).
  local N0 BORD
  N0=$(echo "$FENETRES" | awk '{print $1}')
  BORD=$(python3 -c "
import json,sys
d=json.load(open(sys.argv[1])); d=d[0] if isinstance(d,list) else d
print(d.get('au_bord_relief',''))" "$W/profil_${N0}c.json" 2>/dev/null || echo "")
  ( cd "$ROOT/experiments" && uv run python ../src/commun/test_convergence.py \
      ${BORD:+--au-bord "$BORD"} \
      --serie "${SERIE%,}" --nom "$NOM ($AIRE cm², $CROIS croisements)" \
      --json "$ROOT/docs/extension_${ETIQUETTE}_$NOM.json" | tail -4 )
}

# --- le balayage --------------------------------------------------------------------
# ⚠ Un reglage peut apparaitre DEUX FOIS dans la liste : c'est ainsi qu'on teste le
# determinisme, en refaisant exactement la meme chose. Le dossier prend donc un indice de
# repetition, sinon la seconde ecraserait la premiere et le test serait impossible.
# ⚠⚠ EN MODE ENCHAINEMENT, ON NE BALAIE PAS. Paye le 2026-08-22 : demander une chaine
# faisait d'abord tourner le balayage, dont le premier point (meme source, meme budget) EST
# le premier pas de la chaine — donc vingt minutes de croissance et deux rendus payes deux
# fois pour le meme resultat. Les deux modes repondent a deux questions differentes et il n'y
# a aucune raison de payer l'une quand on pose l'autre.
declare -A VU=()
for G in $([ "$ENCHAINER" -gt 0 ] && echo "" || echo "$GENERATIONS"); do
  VU[$G]=$(( ${VU[$G]:-0} + 1 ))
  if [ "${VU[$G]}" -gt 1 ]; then
    W="$DEST/gen$(printf '%03d' "$G")_bis${VU[$G]}"
  else
    W="$DEST/gen$(printf '%03d' "$G")"
  fi
  # ⚠ Sentinelle d'abandon : le cache de rendu EST le signal d'arret, donc supprimer un
  # rendu ne suffit pas a empecher un relancement de refaire 28 minutes de travail. Paye
  # le 2026-08-21.
  [ -f "$W/ABANDONNE" ] && { echo "== gen$G : abandonne, saute"; continue; }
  mkdir -p "$W/trace"
  if [ ! -d "$W/trace" ] || [ -z "$(ls -d "$W/trace"/auto_grown_* 2>/dev/null)" ]; then
    python3 -c "
import json
json.dump({'mode': 'resume', 'voxelsize': $UM, 'thread_limit': $FILS,
           'cache_size': 6000000000,
           'min_area_cm': $AIRE_MIN, 'generations': $G},
          open('$W/trace/seed.json','w'), indent=2)"
    ( cd "$W/trace" && timeout 7200 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
        --resume "$SOURCE" > extend.log 2>&1 )
  fi
  # ⚠⚠ `mode: resume` nomme sa sortie `auto_grown_*`, PAS `neighbor_*` : un glob repris de
  # `spire_suivante.sh` sans le changer ferait dire « aucun maillage » alors qu'il est la.
  # C'est exactement le piege paye le 2026-08-21 dans l'autre sens.
  M=$(ls -d "$W/trace"/auto_grown_* 2>/dev/null | head -1)
  if [ -z "$M" ]; then
    echo "== gen$G : AUCUN MAILLAGE — resume n'a rien produit"
    tail -3 "$W/trace/extend.log" 2>/dev/null | sed 's/^/     /'
    touch "$W/ABANDONNE"
    continue
  fi
  juger "$W" "$M" "$(basename "$W")"
done

if [ "$ENCHAINER" -gt 0 ]; then
  # ⚠ Un seul budget en enchainement : le premier de la liste. Enchainer ET balayer en meme
  # temps ferait varier deux choses par pas, et aucun ecart ne serait attribuable.
  G=$(echo "$GENERATIONS" | awk '{print $1}')
  echo
  # ⚠⚠ LE BUDGET EST CUMULATIF, ET C'EST MESURE. Un `resume` reprend le compteur de
  # generations de la surface reprise (`Resuming from generation 99` dans le journal) et
  # s'arrete des que `generation >= stop_gen` (GrowPatch.cpp:4680). Donc rejouer le MEME
  # budget sur une surface deja etendue n'autorise plus qu'une seule generation -- mesure le
  # 2026-08-22 : le pas 2 a rendu la meme aire a deux decimales pres, avec
  # « extra_cols=1, extra_rows=1 » dans son journal.
  #
  # ⭐ « Enchainer a budget constant » n'existe donc pas. Ce qui existe, c'est atteindre un
  # budget total en PLUSIEURS SEANCES, chacune relancant l'optimisation globale. Le pas I
  # vise donc I x G, et la question que la chaine pose devient nette : atteindre 200 en deux
  # fois 100 vaut-il mieux que 200 d'un coup (mesure a α = +1,313) ?
  echo "=== ENCHAINEMENT : $ENCHAINER pas, budget CUMULATIF par pas de $G ==="
  COURANTE="$SOURCE"
  for I in $(seq 1 "$ENCHAINER"); do
    W="$DEST/pas$(printf '%03d' "$I")"
    [ -f "$W/ABANDONNE" ] && { echo "== pas$I : abandonne, saute"; break; }
    mkdir -p "$W/trace"
    if [ -z "$(ls -d "$W/trace"/auto_grown_* 2>/dev/null)" ]; then
      python3 -c "
import json
json.dump({'mode': 'resume', 'voxelsize': $UM, 'thread_limit': $FILS,
           'cache_size': 6000000000,
           'min_area_cm': $AIRE_MIN, 'generations': $((I * G))},
          open('$W/trace/seed.json','w'), indent=2)"
      echo "   budget cumulatif du pas $I : $((I * G))"
      ( cd "$W/trace" && timeout 7200 vc_grow_seg_from_seed -v "$B/$SURF" -t . -p seed.json \
          --resume "$COURANTE" > extend.log 2>&1 )
    fi
    M=$(ls -d "$W/trace"/auto_grown_* 2>/dev/null | head -1)
    if [ -z "$M" ]; then
      echo "== pas$I : AUCUN MAILLAGE — resume n'a rien produit"
      tail -3 "$W/trace/extend.log" 2>/dev/null | sed 's/^/     /'
      touch "$W/ABANDONNE"; break
    fi
    juger "$W" "$M" "pas$(printf '%03d' "$I")"
    # ⚠⚠ REFUSER D'ENCHAINER DEPUIS UNE SURFACE QUI NE CONVERGE PAS. Sans ça la chaine
    # continue de s'etendre en travers de l'empilement et chaque pas suivant mesure une
    # surface qui n'a plus de feuille — exactement la panne que la chaine radiale evite.
    # ⚠ Le nom du verdict est calcule dans une variable AVANT d'entrer dans python : imbriquer
    # un `$(printf ...)` dans une chaine python entre guillemets melange les guillemets des
    # deux langages, et le script ne parse meme plus.
    VJ="$ROOT/docs/extension_${ETIQUETTE}_$(basename "$W").json"
    V=$(python3 -c "
import json,sys
print(json.load(open(sys.argv[1]))['series'][0].get('verdict','?'))" "$VJ" 2>/dev/null || echo "?")
    if [ "$V" != "converge" ]; then
      echo "   ARRET : le pas $I ne converge pas (« $V ») — enchainer plus loin ne mesurerait rien"
      break
    fi
    # ⚠⚠ ET REFUSER D'ENCHAINER DEPUIS UNE SURFACE QUI PORTE UNE RESERVE. Le verdict seul ne
    # suffit pas : mesure du 2026-08-22, deux chaines contradictoires que seule la reserve
    # separe.
    #   budget 100 atteint D'UN COUP depuis la source (0 % au bord)  -> α = +0,000, 9 % au bord
    #   budget 100 atteint EN DEUX FOIS 50, le pas 1 etant a 12 % au bord -> α = +1,806
    # Les deux pas 1 « convergent » ; celui qui porte 12 % de peripherie sans feuille propage
    # et amplifie ce defaut (20 % au pas 2) au lieu de le corriger. La qualite de la surface
    # dont on REPART compte donc au moins autant que la taille du pas.
    #
    # ⚠ Hypothese soutenue par trois points, pas une loi : source a 0 % -> succes, a 9 % ->
    # echec partiel, a 12 % -> echec franc. C'est monotone, et c'est tout ce qu'on peut dire.
    R=$(python3 -c "
import json,sys
print('1' if json.load(open(sys.argv[1]))['series'][0].get('reserve') else '0')" "$VJ" 2>/dev/null || echo "0")
    if [ "$R" = "1" ]; then
      B=$(python3 -c "
import json,sys
print(f\"{json.load(open(sys.argv[1]))['series'][0].get('au_bord',0)*100:.0f}\")" "$VJ" 2>/dev/null || echo "?")
      echo "   ARRET : le pas $I converge mais porte une RESERVE ($B % de fenêtres au bord)."
      echo "   Repartir d'une surface dont une part n'a pas de feuille propage ce défaut :"
      echo "   mesuré, 12 % au pas 1 sont devenus 20 % au pas 2, avec α = +1,806."
      break
    fi
    COURANTE="$M"
  done
fi

echo "fin — $(echo "$GENERATIONS" | wc -w) réglage(s) balayé(s)$([ "$ENCHAINER" -gt 0 ] && echo ", $ENCHAINER pas d'enchaînement demandés")"
