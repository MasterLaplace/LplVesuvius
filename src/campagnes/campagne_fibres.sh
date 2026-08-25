#!/bin/bash
# Campagne fibres sur TOUT le corpus Scroll 1, en file derriere la campagne profondeur.
#
# ⚠⚠ POURQUOI TOUT LE CORPUS. Sur 12 segments, le desaccord d'orientation entre
# fenetres voisines corrèle a **rho +0,330** avec les croisements publies, **p = 0,294**.
# Or a n = 12 la mesure ne detecte qu'un rho de **0,73** a 80 % de puissance : ce zero
# n'est PAS informatif, il dit seulement que l'echantillon est trop petit. Pour qu'un
# rho de 0,33 soit detectable au meme niveau il faut **n ≈ 70**, et le corpus en offre
# 80. C'est la regle nº 7 du depot appliquee a l'endroit : rapporter la puissance avec
# le zero, puis aller chercher la puissance.
#
# ⚠ En FILE et non en parallele : les deux campagnes lisent le meme bucket, et se les
# disputer ne les accelere pas -- ca allonge les deux.
set -u
cd "$(dirname "$0")/../.." || exit 2
while pgrep -f "zarr_depth.py" > /dev/null; do sleep 60; done
grep "2\.4um" docs/volumes_surface_PHercParis4.txt | cut -f2 > /tmp/fib_tous.txt
cd inference_xpu || exit 2
exec nice -n 12 uv run python ../src/nappe/fiber_orientation.py \
    $(cat /tmp/fib_tous.txt | tr '\n' ' ') --windows 36 --out ../docs/fibres_corpus.json
