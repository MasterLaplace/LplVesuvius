#!/bin/bash
# La pile est-elle rendue DU BON COTE de la surface ?
#
# ⚠⚠ Pourquoi cette experience existe, et pourquoi elle vient si tard. `38` mesure que nos
# traces ne convergent pas : le pic de matiere est au BORD de la pile rendue, a toutes les
# fenetres essayees. Une trace de 0,98 cm² posee sur la graine meme d'un segment officiel
# fait pareil -- ce qui est difficile a mettre sur le dos de la trace.
#
# ⭐ `vc_render_tifxyz` porte un drapeau `--flip-normals` : « Negate surface normals
# (reverses slice ordering along the normal) ». Si nos maillages ont leurs normales dans
# l'autre sens que ceux du concours, la pile part du MAUVAIS COTE de la surface -- et la
# matiere se retrouve systematiquement au bord oppose, exactement ce qu'on mesure.
#
# ⚠ Le controle qui rend l'experience concluante : le segment OFFICIEL, rendu par la meme
# chaine, CONVERGE (α = +0,00). Si le sens de la normale etait faux pour tout le monde, il
# ne convergerait pas non plus. La question est donc bien « nos maillages » et pas « notre
# rendu ».
#
# ⚠ On rend la MEME surface deux fois, avec et sans le drapeau, dans la MEME fenetre. Une
# comparaison a fenetre differente ne dirait rien, `38` l'a etabli.
#
# ⚠⚠⚠ CE QUE CE SCRIPT NE PEUT PAS TRANCHER, et il faut le lire avant ses chiffres. Le
# depouillement compare l'ecart entre le pic et la COUCHE TRACEE, prise au milieu de la pile
# (`--traced-layer $((COUCHES / 2))`, 20 de 41). Renverser l'ordre envoie la couche p sur
# n-1-p, donc |n-1-p - m| = |p - m| lorsque m = (n-1)/2 : l'ecart est identique PAR
# CONSTRUCTION, quel que soit le volume. Les trois verdicts ci-dessous existent, un seul est
# atteignable, et c'est celui qui s'imprime. Voir `38` § « Le sens de la normale ».
#
# ⭐⭐ La question de fond se tranche autrement, et elle EST tranchee : les deux rendus portent
# les memes images en ordre inverse (41/41 identiques apres renversement, 1/41 a l'endroit),
# donc le drapeau RENUMEROTE la pile sans la deplacer. La fenetre est centree sur la surface
# et il n'existe pas de « mauvais cote ». C'est ce que mesure, sur les rendus produits ici :
#     uv run python src/rendu/le_drapeau_de_normale.py \
#         data/sens_normale/rendu_normal data/sens_normale/rendu_inverse
#
#   ./src/outils/lancer.sh --fond src/outils/sens_de_la_normale.sh [dest] [plat] [couches]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/sens_normale}
PLAT=${2:-$ROOT/data/petite_trace/g30/plat}
COUCHES=${3:-41}
UM=8.64
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="$B/PHerc1447/volumes/20250521151220-8.640um-1.2m-116keV-masked.zarr"
[ -d "$PLAT" ] || { echo "⚠ surface aplatie absente : $PLAT"; exit 3; }
mkdir -p "$DEST"

for SENS in normal inverse; do
  OUT="$DEST/${SENS}_${COUCHES}c.json"
  [ -s "$OUT" ] && continue
  DRAPEAU=""
  [ "$SENS" = inverse ] && DRAPEAU="--flip-normals"
  rm -rf "$DEST/rendu_$SENS"
  # shellcheck disable=SC2086
  vc_render_tifxyz -v "$DEST/cache" --remote-url "$VOL" --scale 1 -g 0 -s "$PLAT" \
      --tif-output "$DEST/rendu_$SENS" -n "$COUCHES" --slice-step 1 --auto-crop $DRAPEAU \
      > "$DEST/rendu_$SENS.log" 2>&1 || { echo "⚠ rendu $SENS échoué"; continue; }
  ( cd "$ROOT" && uv run python src/volume/depth_profile.py \
      "$DEST/rendu_$SENS" --grid --step 200 --traced-layer $((COUCHES / 2)) \
      --voxel-um "$UM" --out "$OUT" ) > "$DEST/profil_$SENS.log" 2>&1 \
    || echo "⚠ dépouillement $SENS échoué"
done
rm -rf "$DEST/cache"

python3 - "$DEST" "$COUCHES" "$UM" <<'PY'
import json, sys
dest, couches, um = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
plafond = (couches // 2) * um

def lis(p):
    try:
        d = json.load(open(p))
    except OSError:
        return None
    return d[0] if isinstance(d, list) else d

print(f"\nmême surface, même fenêtre ({couches} couches, plafond {plafond:.1f} µm)\n")
print(f"  {'sens de la normale':<22} {'écart µm':>9} {'centre':>8} {'bord':>7} {'plates':>8}")
print("  " + "-" * 58)
res = {}
for sens in ("normal", "inverse"):
    d = lis(f"{dest}/{sens}_{couches}c.json")
    if not d:
        print(f"  {sens:<22} {'non mesuré':>9}")
        continue
    res[sens] = d
    marque = "  ⚠ au plafond" if d["ecart_trace_um_median"] >= plafond - 1e-6 else ""
    print(f"  {sens:<22} {d['ecart_trace_um_median']:>9.2f} "
          f"{d['tiers_central_intensite']:>8.3f} {d['au_bord_intensite']:>7.3f} "
          f"{d['part_plates']:>8.3f}{marque}")
if len(res) == 2:
    n, i = res["normal"]["ecart_trace_um_median"], res["inverse"]["ecart_trace_um_median"]
    json.dump({"couches": couches, "plafond_um": plafond,
               "normal": res["normal"], "inverse": res["inverse"]},
              open(f"{dest}/comparaison.json", "w"), indent=2)
    if i < n / 2:
        print(f"\n  ⭐⭐⭐ INVERSER LA NORMALE DIVISE L'ÉCART PAR {n / i:.1f}.")
        print("     La pile était rendue du mauvais côté de la surface : ce n'était pas")
        print("     la trace qui traversait, c'était le rendu qui regardait à l'envers.")
    elif n < i / 2:
        print("\n  ✅ Le sens actuel est le bon — inverser aggrave. La cause est ailleurs.")
    else:
        # ⚠⚠ C'est la SEULE branche atteignable : la couche tracée étant au milieu, le
        # renversement préserve l'écart pour tout pic. Ce « les deux se valent » n'est donc
        # pas une mesure, c'est une identité — et l'afficher comme un verdict a fait passer
        # une tautologie pour un résultat pendant tout un lot.
        print("\n  ⚠⚠ Les deux écarts sont égaux PAR CONSTRUCTION : la couche tracée est au")
        print("     milieu de la pile, donc renverser l'ordre préserve |pic − tracée|. Cette")
        print("     comparaison ne peut pas trancher le sens de la normale, quelle que soit")
        print("     la surface. Ce qui tranche est l'identité des deux piles :")
        print("       uv run python src/rendu/le_drapeau_de_normale.py \\")
        print(f"           {dest}/rendu_normal {dest}/rendu_inverse")
    print(f"  écrit : {dest}/comparaison.json")
PY
