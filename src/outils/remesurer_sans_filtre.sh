#!/bin/bash
# Les comptes d'un tableau portent-ils sur la MEME fraction de surface ?
#
# ⚠⚠ Pourquoi cette mesure existe. `26` §7 compare six reglages du champ de direction par
# leur nombre d'auto-intersections, et en tire une conclusion sur ce que le champ
# « organise ». L'audit de `34` a montre que ces comptes ont ete pris avec des quads
# JETES par le filtre `--maxedge` -- de 3 358 a 82 000 selon la ligne. Un compte ne porte
# donc pas sur la meme fraction de surface d'une ligne a l'autre, et le tableau les compare.
#
# ⭐ Ce script relit chaque maillage avec `--maxedge 0`, filtre desactive : c'est la seule
# lecture ou toutes les lignes portent sur la totalite de leur surface.
#
# ⚠ Ni l'une ni l'autre lecture n'est « la verite ». Filtre actif, on compare des fractions
# differentes ; filtre desactif, on teste des triangles batis a travers une discontinuite
# de grille, que l'aide de l'outil decrit comme « crossing everything it passes through ».
# Ce qui est comparable est la lecture SANS filtre, parce qu'elle traite toutes les lignes
# pareil -- et c'est cette propriete-la, pas une pretention a l'exactitude, qui la rend
# utilisable dans un tableau.
#
# ⚠ Les rapports sans filtre pesent jusqu'a 1,4 Go (l'outil ecrit chaque site de contact).
# On les depouille EN FLUX et on ne garde que les compteurs ; le rapport est efface apres,
# sauf si --garder est passe.
#
#   ./src/outils/remesurer_sans_filtre.sh [dest] [--garder] [essais...]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/sans_filtre}; shift 2>/dev/null || true
GARDER=0
[ "${1:-}" = "--garder" ] && { GARDER=1; shift; }
ESSAIS=${*:-"essai_poids_10 essai_poids_100 essai_dw10 essai_dw100 essai_ng2 essai_horizontal essai_vertical essai_xy_permute essai_scale1 essai_scale3 essai_scale4"}
mkdir -p "$DEST"

LIGNES=""
for E in $ESSAIS; do
  M=$(ls -d "$ROOT/data/trace/PHerc0358/$E"/auto_grown_* 2>/dev/null | head -1)
  [ -z "$M" ] && { echo "  ⚠ $E : aucun maillage"; continue; }
  DEFAUT="$ROOT/data/trace/PHerc0358/$E/selfcross.json"
  RESUME="$DEST/$E.json"
  if [ ! -s "$RESUME" ]; then
    BRUT="$DEST/$E.brut.json"
    vc_tifxyz_selfcross --surface "$M" --maxedge 0 -o "$BRUT" > "$DEST/$E.log" 2>&1 \
      || { echo "  ⚠ $E : selfcross a échoué"; continue; }
    python3 - "$E" "$DEFAUT" "$BRUT" "$RESUME" <<'PY'
import json, re, sys
essai, defaut, brut, sortie = sys.argv[1:5]

def flux(chemin):
    """Compter en lisant par blocs : ces rapports atteignent 1,4 Go."""
    tr = pt = qd = 0
    with open(chemin) as fh:
        reste = ""
        while True:
            bloc = fh.read(1 << 22)
            if not bloc:
                break
            txt = reste + bloc
            for m in re.finditer(
                    r'"(transverse|pairs_tested|quads_dropped_for_edge_length)":\s*(\d+)', txt):
                k, v = m.group(1), int(m.group(2))
                tr += v if k == "transverse" else 0
                pt += v if k == "pairs_tested" else 0
                qd += v if k == "quads_dropped_for_edge_length" else 0
            reste = txt[-80:]
    return tr, pt, qd

td, pd_, qdd = flux(defaut)
tb, pb, qdb = flux(brut)
json.dump({"essai": essai,
           "defaut": {"transverse": td, "paires": pd_, "jetes": qdd},
           "sans_filtre": {"transverse": tb, "paires": pb, "jetes": qdb},
           "ratio": (tb / td) if td else None},
          open(sortie, "w"), indent=2)
PY
    [ "$GARDER" -eq 1 ] || rm -f "$BRUT"
  fi
  L=$(cat "$RESUME"); LIGNES="$LIGNES$L,"
  python3 -c "
import json; d=json.load(open('$RESUME'))
r = d['ratio']
print(f\"  {d['essai']:<20} défaut {d['defaut']['transverse']:>9} ({d['defaut']['jetes']:>6} jetés)\"
      f\"   sans filtre {d['sans_filtre']['transverse']:>9}\"
      f\"   ratio {r:>7.2f}×\" if r else '')"
done
python3 -c "
import json
lignes = json.loads('[' + '''${LIGNES%,}''' + ']')
json.dump({'source': 'data/trace/PHerc0358', 'lignes': lignes},
          open('$ROOT/docs/sans_filtre.json', 'w'), indent=2)
print('écrit : docs/sans_filtre.json')"
