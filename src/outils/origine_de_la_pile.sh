#!/bin/bash
# La couche tracee est-elle AU MILIEU de la pile ? -- selon QUI l'a produite.
#
# ⚠⚠ Pourquoi cette experience existe. Tout l'instrument de profondeur (`12`) se rapporte a
# « la couche tracee, SUPPOSEE au milieu de la pile ». `12` §13 verifie cette hypothese --
# mais sur les **volumes de surface publies**, engendres autour de la trace par
# `vc_layers_from_ppm -r 32`. Nos propres piles viennent d'un AUTRE producteur,
# `vc_render_tifxyz`, dont la convention n'a jamais ete verifiee.
#
# ⭐ Et l'ecart mesure entre les deux est enorme, sur des segments OFFICIELS de PHerc1447 --
# donc qui suivent leur feuille par construction :
#     volume de surface publie : ecart median   3,0 µm, tiers central 62,5 %
#     notre rendu              : ecart median 237,6 µm, tiers central  2 %
# Un facteur 79. Soit un segment officiel est a 238 µm de sa feuille, soit l'origine de nos
# piles n'est pas celle qu'on suppose.
#
# ⚠ Ces deux chiffres portent sur des segments DIFFERENTS, donc ils confondent le
# producteur et le segment. Cette experience leve le confond : **le meme segment**, mesure
# des deux facons. C'est la seule forme qui tranche.
#
# ⚠⚠ Ce qui en depend : `24` §2 (« ecart median 94 µm »), `25` (le critere du tiers central
# RETIRE parce qu'un segment officiel y echouait), et toute la campagne du second axe du
# 2026-08-20. Si l'origine est fausse, ces mesures ne sont pas bruitees : elles sont
# DECALEES, ce qui est pire, parce qu'un decalage a l'air d'un resultat.
#
#   ./src/outils/lancer.sh --fond src/outils/origine_de_la_pile.sh [dest] [segment] [couches]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/origine_pile}
SEG=${2:-20250702235910-auto_grown_20250702235910292}
COUCHES=${3:-31}
ROULEAU=PHerc1447
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/$ROULEAU/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr"
UM=8.64
mkdir -p "$DEST"

# 1. Le volume de surface PUBLIE -- le producteur que `12` §13 a verifie.
SV="$ROULEAU/segments/$SEG/surface-volumes/8.64um-1.2m-116keV-volume-20250521151220.zarr"
if [ ! -s "$DEST/publie.json" ]; then
  ( cd "$ROOT" && uv run python src/commun/zarr_depth.py "$SV" \
      --windows 25 --out "$DEST/publie.json" ) > "$DEST/publie.log" 2>&1 \
    || echo "  ⚠ lecture du volume publié échouée"
fi

# 2. NOTRE rendu du MEME segment.
if [ ! -s "$DEST/rendu.json" ]; then
  M="$DEST/mesh.tifxyz"
  if [ ! -f "$M/meta.json" ]; then
    mkdir -p "$M"
    # ⚠ Le chemin a ete LISTE, pas devine : la premiere version cherchait
    # `<segment>/<segment>.tifxyz/` -- la convention d'un maillage local -- et le bucket
    # range le sien sous `mesh/tifxyz/`. Elle a echoue sur « meta.json absent », message
    # qui accuse le segment la ou le fautif etait le chemin.
    #
    # ⭐ Et le listage a montre autre chose : le segment publie aussi un
    # `<segment>_flattened.obj`. LEUR chaine aplatit donc elle aussi, ce qui rend la
    # comparaison plus juste qu'espere -- ce ne sont pas deux chaines de formes
    # differentes, ce sont deux executions de la meme forme.
    for f in meta.json x.tif y.tif z.tif mask.tif; do
      curl -sfL --max-time 600 -o "$M/$f" \
        "$B/$ROULEAU/segments/$SEG/mesh/tifxyz/$f" || rm -f "$M/$f"
    done
    # ⚠ `mask.tif` est optionnel selon les segments ; les trois grilles et le meta ne le
    # sont pas. On refuse plutot que de rendre une surface incomplete.
    for f in meta.json x.tif y.tif z.tif; do
      [ -s "$M/$f" ] || { echo "  ⚠ $f absent — ce segment ne publie pas son tifxyz ici"; exit 3; }
    done
  fi
  rm -rf "$DEST/plat" "$DEST/rendu"
  vc_flatten -i "$M" -o "$DEST/plat" > "$DEST/flatten.log" 2>&1 \
    || { echo "  ⚠ vc_flatten a échoué"; exit 3; }
  vc_render_tifxyz -v "$DEST/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$DEST/plat" \
      --tif-output "$DEST/rendu" -n "$COUCHES" --slice-step 1 --auto-crop \
      > "$DEST/rendu_tif.log" 2>&1 \
    || { echo "  ⚠ vc_render_tifxyz a échoué"; exit 3; }
  MILIEU=$(( COUCHES / 2 ))
  ( cd "$ROOT" && uv run python src/volume/depth_profile.py \
      "$DEST/rendu" --grid --step 400 --traced-layer "$MILIEU" --voxel-um "$UM" \
      --out "$DEST/rendu.json" ) > "$DEST/profil.log" 2>&1 \
    || { echo "  ⚠ depth_profile a échoué"; exit 3; }
  rm -rf "$DEST/cache"
fi

python3 - "$DEST" "$SEG" "$COUCHES" <<'PY'
import json, sys
dest, seg, couches = sys.argv[1], sys.argv[2], int(sys.argv[3])

def lis(p):
    """Les deux producteurs n'ecrivent pas les memes noms de champs.

    ⚠ `zarr_depth.py` ecrit `ecart_a_la_trace` / `tiers_central` / `au_bord` et un `layers`
    ENTIER ; `depth_profile.py` ecrit `ecart_trace_um_median` / `tiers_central_intensite` /
    `au_bord_intensite` et un `layers` LISTE. La premiere version de ce rapport supposait
    les seconds partout et levait un TypeError sur `len(int)` -- donc l'experience decisive
    ne rendait rien alors que ses deux moities avaient abouti.
    """
    try:
        d = json.load(open(p))
    except OSError:
        return None
    d = (d[0] if isinstance(d, list) else d)
    lay = d.get("layers")
    return {
        "couches": lay if isinstance(lay, int) else len(lay or []),
        "ecart": d.get("ecart_trace_um_median", d.get("ecart_a_la_trace")),
        "centre": d.get("tiers_central_intensite", d.get("tiers_central")),
        "bord": d.get("au_bord_intensite", d.get("au_bord")),
    }

pub, ren = lis(f"{dest}/publie.json"), lis(f"{dest}/rendu.json")
print(f"\nsegment {seg} — LE MÊME, mesuré deux fois\n")
print(f"  {'producteur':<28} {'couches':>8} {'écart µm':>9} {'centre':>8} {'bord':>7}")
print("  " + "-" * 64)
for nom, d in (("volume de surface publié", pub), ("notre vc_render_tifxyz", ren)):
    if not d:
        print(f"  {nom:<28} {'—':>8} {'non mesuré':>9}")
        continue
    print(f"  {nom:<28} {d['couches'] or couches:>8} "
          f"{d['ecart']:>9.2f} {d['centre']:>8.3f} {d['bord']:>7.3f}")
if pub and ren:
    ecart = abs(ren["ecart"] - pub["ecart"])
    json.dump({"segment": seg, "couches": couches, "publie": pub, "rendu": ren,
               "difference_um": ecart},
              open(f"{dest}/comparaison.json", "w"), indent=2)
    print(f"\n  différence : {ecart:.1f} µm sur le MÊME segment.")
    if ecart > 50:
        print("  ⚠⚠ L'origine de la pile DIFFÈRE selon le producteur. Tout écart mesuré")
        print("     depuis un rendu `vc_render_tifxyz` est pris depuis un mauvais point.")
    else:
        print("  ✅ Les deux producteurs s'accordent : l'hypothèse du milieu transporte,")
        print("     et l'écart de 237 µm du segment officiel est une propriété du segment.")
    print(f"  écrit : {dest}/comparaison.json")
PY
