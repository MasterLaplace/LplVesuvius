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
#   ./tools/lancer.sh --fond tools/etendre_nappe.sh <dest> [generations...]
#   GENERATIONS="100 200 400" ./tools/lancer.sh --fond tools/etendre_nappe.sh "$PWD/data/ext"
set -u
cd "$(dirname "$0")/.." || exit 2
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

ROULEAU=${ROULEAU:-PHerc1447}
SOURCE=${SOURCE:-$ROOT/data/origine_pile/mesh.tifxyz}
SURF=${SURF:-PHerc1447/representations/predictions/surfaces/20250521151220-surface-20260413222639-surface-m7-L0-th0.2.zarr}
FENETRES=${FENETRES:-"31 81"}
UM=${UM:-8.64}
# ⚠ Meme garde que `spire_suivante.sh` : `min_area_cm` borne la surface minimale d'un
# morceau garde. On reprend la valeur de la campagne de repousse pour que la comparaison
# avec son point a 20 generations reste appariee.
AIRE_MIN=${AIRE_MIN:-0.3}

B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr"

ETIQUETTE=$(basename "$DEST"); ETIQUETTE=${ETIQUETTE#data_}
echo "etiquette des verdicts : extension_${ETIQUETTE}_<generations>.json"
echo "source : $SOURCE"
echo "generations balayees : $GENERATIONS   fenetres : $FENETRES   min_area_cm : $AIRE_MIN"
echo "  (cle JSON : 'generations' — 'resume_generations' n'est lu par personne, cf. en-tete)"

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
juger() {
  local W=$1 M=$2 NOM=$3
  [ -s "$W/selfcross.json" ] || vc_tifxyz_selfcross --surface "$M" -o "$W/selfcross.json" > /dev/null 2>&1
  local CROIS SERIE AIRE
  CROIS=$(python3 "$ROOT/analysis/src/lire_selfcross.py" "$W/selfcross.json" 2>/dev/null || echo "?")
  AIRE=$(python3 -c "
import json;print(f\"{json.load(open('$M/meta.json'))['area_cm2']:.2f}\")" 2>/dev/null || echo "?")
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
      ( cd "$ROOT/inference_xpu" && uv run python ../analysis/src/depth_profile.py \
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
  ( cd "$ROOT/experiments" && uv run python ../analysis/src/test_convergence.py \
      --serie "${SERIE%,}" --nom "$NOM ($AIRE cm², $CROIS croisements)" \
      --json "$ROOT/docs/extension_${ETIQUETTE}_$NOM.json" | tail -4 )
}

# --- le balayage --------------------------------------------------------------------
for G in $GENERATIONS; do
  W="$DEST/gen$(printf '%03d' "$G")"
  # ⚠ Sentinelle d'abandon : le cache de rendu EST le signal d'arret, donc supprimer un
  # rendu ne suffit pas a empecher un relancement de refaire 28 minutes de travail. Paye
  # le 2026-08-21.
  [ -f "$W/ABANDONNE" ] && { echo "== gen$G : abandonne, saute"; continue; }
  mkdir -p "$W/trace"
  if [ ! -d "$W/trace" ] || [ -z "$(ls -d "$W/trace"/auto_grown_* 2>/dev/null)" ]; then
    python3 -c "
import json
json.dump({'mode': 'resume', 'voxelsize': $UM, 'thread_limit': 0,
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
  juger "$W" "$M" "gen$(printf '%03d' "$G")"
done

echo "fin — $(echo "$GENERATIONS" | wc -w) réglage(s) balayé(s)"
