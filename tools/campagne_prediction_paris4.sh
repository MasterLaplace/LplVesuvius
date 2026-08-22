#!/bin/bash
# Laquelle des DEUX predictions de surface de PHercParis4 vaut-il mieux tracer ?
#
# ⚠⚠ Pourquoi cette campagne existe. `48` etablit que l'experience « reparer sert-il ? »
# doit etre montee sur `PHercParis4` -- le seul rouleau ou le detecteur d'encre est mesure
# DIRECTEMENT (`36` §5bis : AUC 0,925, sigma 0,7712) et qui publie a la fois une prediction
# de surface et des segments. Et elle nomme le blocage : il publie DEUX predictions du meme
# volume, et l'appariement REFUSE de tirer au sort.
#
# ⭐ Ce ne sont pas deux versions d'une meme chose. Leurs metadonnees le disent : meme
# volume source (`2.4um_PHerc-Paris4_masked.zarr`), generees a deux secondes d'intervalle,
# par DEUX MODELES differents -- `ps256_trainpy` a seuil 0,45 et `m7_nnunet` a seuil 0,2.
# Choisir entre elles est donc une mesure, pas une convention.
#
# ⚠⚠ Le critere est celui du depot et pas un proxy : on trace une graine dans chacune, avec
# des parametres IDENTIQUES, et on juge les deux traces au test de convergence de `38`.
# Comparer les scores internes des deux predictions serait plus rapide et moins probant --
# ce qu'on veut savoir n'est pas laquelle a l'air mieux, c'est laquelle donne une trace qui
# suit une feuille.
#
# ⚠ Leurs chunks ne font pas la meme taille (256 contre 192), donc la recherche de graine ne
# visite pas les memes endroits dans les deux. C'est assume et dit : on compare ce que
# CHACUNE offre de mieux, pas le meme point vu deux fois.
#
# ⚠ Reprenable : une etape dont la sortie existe est sautee.
#
#   ./tools/campagne_prediction_paris4.sh [dest]
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/prediction_paris4}
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
S="PHercParis4/representations/predictions/surfaces"
VOL="PHercParis4/volumes/20241024131838-7.910um-53keV-masked.zarr"
mkdir -p "$DEST"

# ⚠ Les deux predictions, nommees par leur MODELE et pas par leur rang : « la premiere » et
# « la deuxieme » dependent de l'ordre d'un listage S3, qui n'est pas une propriete des
# donnees. Le repertoire de sortie porte le nom du modele, donc un resultat dit de qui il
# parle sans qu'on ait a se souvenir.
declare -A PRED=(
  [ps256]="$S/20260411134726-surface-20260413141734-surface-recto-2um-ps256-L0-th0.45.zarr"
  [m7]="$S/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr"
)

# ⚠⚠ La resolution du VOLUME, pas celle de la prediction. `vc_grow_seg_from_seed` calcule une
# aire avec `voxelsize` : s'y tromper rend une aire fausse d'un facteur constant, et le
# message d'erreur accuse la surface. Le volume publie de ce rouleau est a 7,910 µm.
VOXEL=7.910
NIVEAU=${NIVEAU:-2}
CHUNKS=${CHUNKS:-24}

for NOM in ps256 m7; do
  OUT="$DEST/graine_$NOM.json"
  if [ -s "$OUT" ]; then echo "== graine $NOM deja cherchee"; continue; fi
  echo "== graine $NOM  (niveau $NIVEAU, $CHUNKS chunks)"
  ( cd "$ROOT/experiments" && uv run python "$ROOT/analysis/src/trouver_graine.py" \
      "${PRED[$NOM]}" --level "$NIVEAU" --critere planarite --chunks "$CHUNKS" \
      --voxel-um "$VOXEL" --out "$OUT" ) || echo "  ⚠ echec sur $NOM — rapporte, pas masque"
done

echo
echo "== ce que chaque prediction a offert"
python3 - "$DEST" <<'PY'
import json, sys
from pathlib import Path
d = Path(sys.argv[1])
for nom in ("ps256", "m7"):
    p = d / f"graine_{nom}.json"
    if not p.is_file():
        print(f"  {nom:<8} aucune sortie — la recherche a echoue ou n'a pas tourne")
        continue
    j = json.loads(p.read_text())
    c = (j.get("candidats") or [])
    if not c:
        print(f"  {nom:<8} 0 candidat")
        continue
    m = c[0]
    print(f"  {nom:<8} {len(c)} candidat(s), meilleur : "
          f"xyz={m.get('x')},{m.get('y')},{m.get('z')} "
          f"planarite={m.get('planarite')} occupation={m.get('occupation')}")
PY
echo
echo "⏳ etape suivante : tracer une graine dans chacune et juger les deux traces au test"
echo "   de convergence. C'est le critere qui decide -- pas les scores ci-dessus, qui"
echo "   disent seulement ce que chaque prediction OFFRE."
