#!/bin/bash
# Rassembler ce qui PART : le texte, ses figures, et la preuve que ses chiffres tiennent.
#
# ⚠⚠ Pourquoi ce script existe. `21` porte depuis des semaines une liste « joindre telle
# figure », tenue a la main, cochee a la main. Une liste tenue a la main depend de quelqu'un
# qui se souvienne -- exactement la classe de panne que ce depot a deja payee avec la
# sentinelle de boot et avec la liste des documents du garde-fou des chiffres. Le remede
# n'est pas de mieux cocher, c'est de ne plus avoir a le faire.
#
# ⭐⭐ La liste des figures est DERIVEE DU DOCUMENT : toute image nommee entre backticks
# dans `21` doit exister et est copiee. Ajouter une figure au texte l'ajoute au dossier,
# sans toucher a ce script. En retirer une la retire.
#
# ⚠ Le script REFUSE de produire un dossier incomplet. Un dossier a qui il manque une
# figure ressemble a un dossier complet -- c'est pire que pas de dossier du tout, parce que
# personne ne va recompter les pieces jointes a l'arrivee.
#
# ⚠ Et il refait tourner le garde-fou des chiffres sur le document qui part : `29` porte
# « reverifier chaque chiffre le jour de l'envoi » comme une regle a executer. Une regle
# qu'un humain doit se rappeler d'executer n'est pas une garantie.
#
#   ./src/outils/dossier_soumission.sh [dest]
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
DEST=${1:-$ROOT/soumission}
TEXTE=$ROOT/docs/21_texte_de_soumission.md
MANQUE=0

[ -s "$TEXTE" ] || { echo "absent : $TEXTE" >&2; exit 2; }
rm -rf "$DEST"; mkdir -p "$DEST/figures"

echo "== figures nommées par le texte"
# ⚠ `sort -u` : le texte cite plusieurs fois la meme figure, et la copier deux fois n'est
# pas une erreur -- mais la COMPTER deux fois ferait un total qui ne veut rien dire.
FIGS=$(grep -oE '`[0-9a-zA-Z_]+\.(png|jpg)`' "$TEXTE" | tr -d '`' | sort -u)
N=0
for f in $FIGS; do
  if [ -s "$ROOT/docs/images/$f" ]; then
    cp "$ROOT/docs/images/$f" "$DEST/figures/$f"
    N=$((N + 1))
    printf '  ✅ %s\n' "$f"
  else
    printf '  ❌ %s — nommée par le texte, absente de docs/images/\n' "$f"
    MANQUE=$((MANQUE + 1))
  fi
done

echo "== texte"
cp "$TEXTE" "$DEST/"

echo "== chiffres du document qui part"
# ⚠ Tournait depuis `inference/` (l'environnement temoin CPU) jusqu'au 2026-08-25 : la
# racine porte PIL, numcodecs, numpy, scipy et tifffile, donc STRICTEMENT plus. `inference/`
# reste ce qu'il declare etre -- le temoin CPU du ×4,5 XPU -- et n'est plus emprunte pour
# des figures, ce qui evite de garder chaud un venv de 2,5 Gio pour du dessin.
cd "$ROOT" || exit 2
if uv run python "$ROOT/src/depot/verifier_chiffres.py" "$ROOT"/docs/*.md \
     "$ROOT/article/article.typ" --soumission "$TEXTE" --article "$ROOT/article/article.typ" \
     > "$DEST/chiffres.log" 2>&1; then
  printf '  ✅ %s chiffres retrouvés (journal joint)\n' "$(grep -c '✅' "$DEST/chiffres.log")"
else
  printf '  ❌ le garde-fou des chiffres échoue — voir %s\n' "$DEST/chiffres.log"
  MANQUE=$((MANQUE + 1))
fi
cd "$ROOT" || exit 2

# ⚠⚠ L'article n'est PAS dans le dossier de soumission : ce sont deux envois differents,
# vers deux publics differents, et melanger les deux ferait partir un preprint de 18 pages
# la ou le reglement attend un texte de concours. Le lien entre les deux se fait par le
# depot, pas par la piece jointe.

if [ "$MANQUE" -gt 0 ]; then
  echo
  echo "❌ dossier INCOMPLET ($MANQUE manque(s)) — rien n'est prêt à partir"
  echo "   Un dossier auquel il manque une pièce ressemble à un dossier complet."
  exit 1
fi
echo
echo "✅ $DEST — $N figure(s), le texte, et le journal des chiffres"
du -sh "$DEST" | sed 's/^/   /'
