#!/bin/bash
cd "$(dirname "$0")/.." || exit 2
echo "racine=$PWD"
for i in 1 2 3; do
  sleep 0.4
  printf 'tour %s
' "$i"
done
echo "phase2=original"
