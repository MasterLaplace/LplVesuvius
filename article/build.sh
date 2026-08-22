#!/bin/bash
# Reconstruire l'article : les figures EN ANGLAIS, puis le PDF.
#
# ⚠⚠ Pourquoi les figures sont regenerees ici et pas simplement copiees. Les figures du
# depot sont en francais, comme ses documents ; l'article est en anglais. Une copie fige
# donc une traduction a un instant donne, et la prochaine fois qu'un chiffre bouge, la
# figure de l'article dit encore l'ancien. Les regenerer depuis les memes fichiers de
# resultat garantit que la figure de l'article et le tableau du depot parlent du meme run.
#
# ⚠ Chaque script REFUSE d'ecrire une figure a moitie traduite (`langue.Traduisant`), donc
# un libelle ajoute sans sa traduction fait echouer ce script au lieu de produire un PDF
# franglais.
#
#   ./article/build.sh
set -eu
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
FIG="$ROOT/article/figures"
TYPST=${TYPST:-$HOME/.local/bin/typst}

echo "== figures (anglais)"
cd "$ROOT/inference"
uv run python ../analysis/src/figure_convergence.py --anglais --sortie "$FIG/38_convergence.png"
uv run python ../analysis/src/figure_tirages.py     --anglais --sortie "$FIG/35_tirages.png"
uv run python ../analysis/src/figure_plafond.py     --anglais --sortie "$FIG/35_plafond.png"
uv run python ../analysis/src/figure_graines.py     --anglais --sortie "$FIG/25_campagne_graines.png"
uv run python ../analysis/src/figure_segments.py    --anglais --sortie "$FIG/44_ecarts_segments.png"
uv run python ../analysis/src/geometrie_chaine.py "$ROOT/data/spires_pas025" \
    --voxel-um 8.64 --anglais --figure "$FIG/44_geometrie_chaine.png" > /dev/null

# ⚠ Ces deux-la sont des RENDUS, pas des graphiques : ils ne portent aucun texte, donc ils
# se copient tels quels. Les regenerer demanderait le volume complet, qui n'est pas ici.
cp "$ROOT/docs/images/38_en_travers.png" "$FIG/"
cp "$ROOT/docs/images/44_extension.jpg"  "$FIG/"

echo "== PDF"
cd "$ROOT/article"
"$TYPST" compile article.typ article.pdf
echo "écrit : $ROOT/article/article.pdf"
