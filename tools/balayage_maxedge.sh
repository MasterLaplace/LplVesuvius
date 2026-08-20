#!/bin/bash
# Le filtre `--maxedge` masque-t-il, ou fabrique-t-il, les auto-intersections ?
#
# ⚠⚠ Pourquoi ce balayage existe. `24` a condamne une trace sur 240 auto-intersections
# mesurees au reglage PAR DEFAUT de `vc_tifxyz_selfcross` (`--maxedge 60`). Ce reglage
# jette les quads dont une arete depasse 60 voxels, au motif ecrit dans l'aide de l'outil :
# « a triangle built across a grid discontinuity crosses everything it passes through ».
#
# Un filtre pose entre la surface et le verdict peut se tromper dans LES DEUX SENS, et
# `29` M2 le note ainsi : il peut MASQUER (jeter un quad long qui croisait vraiment) et il
# peut FABRIQUER (garder un quad long qui ne croise rien de reel). Une valeur par defaut
# n'est pas une mesure : c'est le reglage de quelqu'un d'autre.
#
# ⚠ Le balayage porte sur DEUX maillages, et c'est ce qui le rend lisible :
#   - le maillage CONDAMNE de `24` (240 croisements au defaut), archive dans l'arbre ;
#   - un maillage PROPRE ne le, meme graine, memes parametres (0 croisement au defaut).
# Sans le second, un compte qui bouge avec le reglage ne dirait pas si c'est le reglage
# qui cree le verdict ou la surface qui le porte.
#
# ⚠ `--maxedge 0` DESACTIVE le filtre : c'est la lecture sans aucun tri, et elle doit
# figurer dans le balayage sous peine de comparer des reglages entre eux sans jamais voir
# ce qu'ils retirent.
#
#   ./tools/balayage_maxedge.sh [dest] [maillage_condamne] [maillage_propre]
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/data/maxedge}
CONDAMNE=${2:-$ROOT/artefacts/PHerc0358/mesh.tifxyz}
PROPRE=${3:-}
mkdir -p "$DEST"

# Le maillage propre par defaut est le tirage dont l'aire est la plus proche de celle du
# condamne -- c'est le temoin apparie de `30` §2, celui qui rend deux verdicts opposes a
# 0,003 % d'aire pres. On le retrouve plutot que de coder son nom en dur.
if [ -z "$PROPRE" ]; then
  PROPRE=$(python3 -c "
import json, glob, os, sys
ref = None
m = '$ROOT/artefacts/PHerc0358/mesh.tifxyz/meta.json'
if os.path.exists(m): ref = json.load(open(m)).get('area_cm2')
best, ecart = None, None
for f in glob.glob('$ROOT/data/trace/PHerc0358/thread_limit/*/resume.json'):
    d = json.load(open(f))
    if d.get('statut') != 'ok' or d.get('transverse') != 0: continue
    if ref is None: best = f; break
    e = abs(d['aire_cm2'] - ref)
    if ecart is None or e < ecart: best, ecart = f, e
if not best: sys.exit(1)
import glob as g
s = g.glob(os.path.join(os.path.dirname(best), 'auto_grown_*'))
print(s[0] if s else '', end='')" 2>/dev/null)
fi
[ -z "$PROPRE" ] && { echo "⚠ aucun maillage propre apparie trouve — passer le chemin en 3e argument"; exit 2; }
echo "condamné : $CONDAMNE"
echo "propre   : $PROPRE"

for E in 0 20 30 40 60 80 120 200 400; do
  for R in condamne propre; do
    [ "$R" = condamne ] && M=$CONDAMNE || M=$PROPRE
    F="$DEST/${R}_maxedge${E}.json"
    [ -s "$F" ] && continue
    vc_tifxyz_selfcross --surface "$M" --maxedge "$E" -o "$F" > "$DEST/${R}_${E}.log" 2>&1 \
      || echo "  ⚠ échec à maxedge=$E sur $R"
  done
  # ⚠ `lire_selfcross.py` REFUSE un rapport sans paire testee, et c'est ce balayage qui
  # a rendu ce refus necessaire : a maxedge 20 l'outil declare « propre » en ayant jete
  # les 48 040 quads. Un « ? » dans la colonne veut donc dire « non mesure », jamais zero.
  printf 'maxedge %-4s condamné %-8s propre %s\n' "$E" \
    "$(python3 "$ROOT/analysis/src/lire_selfcross.py" "$DEST/condamne_maxedge${E}.json" 2>/dev/null || echo 'non mesuré')" \
    "$(python3 "$ROOT/analysis/src/lire_selfcross.py" "$DEST/propre_maxedge${E}.json" 2>/dev/null || echo 'non mesuré')"
done
echo "balayage fini — $DEST"
