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
#   ./docs/article/build.sh
set -eu
# ⚠ TROIS niveaux depuis `docs/article/` : ce script vivait a la racine dans
# `docs/article/`, il en est a deux crans maintenant.
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
FIG="$ROOT/docs/article/figures"
TYPST=${TYPST:-$HOME/.local/bin/typst}

echo "== figures (anglais)"
# ⚠ Tournait depuis `inference/` (l'environnement temoin CPU) jusqu'au 2026-08-25 : la
# racine porte PIL, numcodecs, numpy, scipy et tifffile, donc STRICTEMENT plus. `inference/`
# reste ce qu'il declare etre -- le temoin CPU du ×4,5 XPU -- et n'est plus emprunte pour
# des figures, ce qui evite de garder chaud un venv de 2,5 Gio pour du dessin.
cd "$ROOT"
uv run python src/figures/figure_convergence.py --anglais --sortie "$FIG/38_convergence.png"
uv run python src/figures/figure_tirages.py     --anglais --sortie "$FIG/35_tirages.png"
uv run python src/figures/figure_plafond.py     --anglais --sortie "$FIG/35_plafond.png"
uv run python src/figures/figure_graines.py     --anglais --sortie "$FIG/25_campagne_graines.png"
uv run python src/figures/figure_segments.py    --anglais --sortie "$FIG/44_ecarts_segments.png"
uv run python src/figures/figure_temoin_negatif.py --anglais \
    --json "$ROOT/docs/mesures/temoin_negatif.json" \
    --positif "$ROOT/data/temoin_negatif/sur_sa_feuille.npy" \
    --negatif "$ROOT/data/temoin_negatif/en_travers.npy" \
    --sortie "$FIG/46_temoin_negatif.png"
uv run python src/figures/figure_candidats.py --anglais \
    --json "$ROOT/docs/mesures/paris4_candidats.json" --sortie "$FIG/48_candidats.png"
uv run python src/figures/figure_deux_pannes.py --anglais \
    --json "$ROOT/docs/mesures/audit_profils.json" --sortie "$FIG/49_deux_pannes.png"
uv run python src/figures/figure_derive_profondeur.py --anglais \
    --json "$ROOT/docs/mesures/derive_profondeur.json" --docs "$ROOT/docs/mesures" \
    --sortie "$FIG/47_derive_profondeur.png"
uv run python src/figures/figure_appuis.py --anglais \
    --json "$ROOT/docs/mesures/appui_de_pente.json" --sortie "$FIG/51_appuis.png"
uv run python src/figures/figure_contraste.py --anglais \
    --json "$ROOT/docs/mesures/appui_de_pente.json" --sortie "$FIG/51_contraste.png"
# ⚠ Celle-ci est DEJA en anglais : elle a ete ecrite pour l'article, donc elle n'a pas de
# table de traduction — la traduire serait traduire vers sa propre langue.
uv run python src/figures/figure_typographie.py           --sortie "$FIG/45_typographie.png"
uv run python src/nappe/geometrie_chaine.py "$ROOT/data/spires_pas025" \
    --voxel-um 8.64 --anglais --figure "$FIG/44_geometrie_chaine.png" > /dev/null

# ⚠ Ces deux-la sont des RENDUS, pas des graphiques : ils ne portent aucun texte, donc ils
# se copient tels quels. Les regenerer demanderait le volume complet, qui n'est pas ici.
cp "$ROOT/docs/images/38_en_travers.png" "$FIG/"
cp "$ROOT/docs/images/44_extension.jpg"  "$FIG/"

echo "== PDF"
cd "$ROOT/article"
"$TYPST" compile article.typ article.pdf
echo "écrit : $ROOT/docs/article/article.pdf"
