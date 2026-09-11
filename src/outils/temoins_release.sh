#!/usr/bin/env bash
# Les temoins de la BRANCHE DE RELEASE : exactement ce qui est livre, et rien d autre.
#
# ⚠⚠ Pourquoi une seconde batterie plutot que la premiere. `temoins.sh` appelle
# `src/excision/`, `inference/`, `src/xpu/` et `data/repos/`, que la release ne porte pas --
# elle echouerait donc pour la seule raison qu il s agit d une release. Un controle qui ne
# peut pas passer cesse d etre lu, et une release qu on ne verifie pas n en est pas une.
#
# ⚠ Ce n est PAS une batterie au rabais : elle lance tous les auto-tests des fichiers
# livres. Ce qu elle ne lance pas, ce sont ceux d un code qui n est pas la.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 2

# ⚠⚠ UN SEUL EXEMPLAIRE A LA FOIS. Plusieurs auto-tests ecrivent des fixtures a des chemins
# FIXES -- `tools/.temoin_lancer.sh`, les journaux de `.lances/` -- et deux batteries
# concurrentes se les arrachent. Le symptome ne ressemble pas a la cause : un test parfait
# echoue avec « attendu la racine, obtenu vide », et on part chercher un bug dans le code.
# Paye ici en lancant a la main, pendant la batterie, le test dont je diagnostiquais l echec.
VERROU="$ROOT/.lances/.temoins_release.verrou"
mkdir -p "$(dirname "$VERROU")"
if ! ( set -o noclobber; echo "$$" > "$VERROU" ) 2>/dev/null; then
  autre=$(cat "$VERROU" 2>/dev/null)
  if [ -n "$autre" ] && kill -0 "$autre" 2>/dev/null; then
    echo "refus : une batterie tourne deja (pid $autre)" >&2
    exit 2
  fi
  # ⚠ Un verrou dont le proprietaire est mort est un verrou perime, pas un verrou : le
  # relever silencieusement est correct, le laisser bloquerait le depot apres un kill.
  echo "$$" > "$VERROU"
fi
trap 'rm -f "$VERROU"' EXIT INT TERM

FAIL=0; BATTERIES=0; CONTROLES=0

# ⚠⚠ Certains controles dependent d une entree qui n est PAS livree : le depot amont clone
# dans `data/repos/`, ou le code d une experience que la release ne porte pas. Sur l arbre
# complet ils tournent ; sur l arbre allege ils echoueraient pour la seule raison que leur
# entree est ailleurs.
#
# ⚠ Le saut est CONDITIONNEL a l absence reelle, verifiee ici : si l entree est presente, le
# controle TOURNE. Une liste de sauts inconditionnelle serait une facon de balayer un echec
# sous le tapis, et elle finirait par cacher une vraie panne le jour ou l entree revient.
#
#   poids_growpatch     lit GrowPatch.cpp du depot amont volume-cartographer
#   artefacts_orphelins exige que le producteur de chaque artefact soit dans l arbre
declare -A DEPEND=(
  [poids_growpatch]="data/repos/villa/volume-cartographer"
  [artefacts_orphelins]="src"
)
SAUTES=0

run() {
  local nom=$1; shift
  local dep="${DEPEND[$nom]:-}"
  if [ -n "$dep" ] && [ ! -e "$ROOT/$dep" ]; then
    printf '  ⏭  %-33s SAUTÉ — %s absent de la release\n' "$nom" "$dep"
    SAUTES=$((SAUTES + 1))
    return 0
  fi
  local sortie rc
  sortie=$("$@" 2>&1); rc=$?
  sortie=$(grep -vE "SyntaxWarning|DeprecationWarning|^  [a-z_]+ =" <<<"$sortie")
  BATTERIES=$((BATTERIES + 1))
  # ⚠⚠ Le depot a DEUX conventions de verdict, mesurees : 41 fichiers disent « ALL PASS
  # (n checks) », 6 disent « tous les temoins passent » et comptent leurs ✅. Ma premiere
  # version n en connaissait qu une et declarait les six en ECHEC -- avec un code de retour
  # ZERO, ce qui aurait du me mettre la puce a l oreille : un echec sans code d erreur n en
  # est pas un. Uniformiser les six serait du churn ; les reconnaitre est une ligne.
  if [ "$rc" -eq 0 ] && grep -q "ALL PASS" <<<"$sortie"; then
    CONTROLES=$((CONTROLES + $(grep -o 'ALL PASS.*' <<<"$sortie" | tail -1 \
                  | grep -oE '[0-9]+ checks' | grep -oE '[0-9]+' || echo 0)))
    printf '  ✅ %-34s %s\n' "$nom" "$(grep -o 'ALL PASS.*' <<<"$sortie" | tail -1)"
  elif [ "$rc" -eq 0 ] && grep -q "tous les témoins passent" <<<"$sortie"; then
    n=$(grep -c '✅' <<<"$sortie")
    CONTROLES=$((CONTROLES + n))
    printf '  ✅ %-34s %s\n' "$nom" "$n checks"
  else
    printf '  ❌ %-34s ECHEC (code %s)\n' "$nom" "$rc"
    sed 's/^/       /' <<<"$sortie" | tail -4
    FAIL=$((FAIL + 1))
  fi
}

echo "TEMOINS DE LA RELEASE — tout hors ligne"
echo

# ── Le livrable ────────────────────────────────────────────────────────────────
run "tracecheck"               uv run --project "$ROOT" python "$ROOT/src/tracecheck/selftest.py"
run "tracecheck : mutation"    uv run --project "$ROOT" python "$ROOT/src/tracecheck/mutation.py"

# ── Les instruments livres, decouverts et non listes ───────────────────────────
# ⚠⚠ La liste est DERIVEE de l arbre, pas ecrite a la main : un instrument ajoute demain
# est teste demain, sans que personne ait a penser a l inscrire. Une liste ecrite a la main
# est une liste qui vieillit -- c est exactement ce que ce depot reproche aux README.
for f in "$ROOT"/src/*/*.py; do
  # ⚠ Meme regle cote python : le fichier doit DECLARER l option, pas seulement la citer.
  grep -q -- 'add_argument("--verifier"' "$f" || continue
  run "$(basename "$f" .py)" uv run --project "$ROOT" python "$f" --verifier
done

# ── Les outils livres ──────────────────────────────────────────────────────────
# ⚠⚠ On cherche le fichier qui GERE `--verifier`, pas celui qui le MENTIONNE. `temoins.sh`
# le passe a quarante autres scripts sans le gerer lui-meme : ma premiere version l a donc
# lance, et il a relance la batterie complete depuis l interieur de la batterie. C est le
# vrai defaut de l auto-decouverte -- l arbre ne distingue pas un drapeau traite d un
# drapeau transmis, sauf a regarder la FORME du test qui le traite.
for f in "$ROOT"/src/*/*.sh; do
  grep -qE '\[ "\$\{1:-\}" = "--verifier" \]|^\s*--verifier\)' "$f" || continue
  run "$(basename "$f" .sh)" "$f" --verifier
done

# ── Les chiffres publies ───────────────────────────────────────────────────────
# ⚠⚠ En mode ARBRE RESTREINT : un chiffre dont le document citant n est pas livre est hors
# perimetre, pas en echec. Mais les listes exigees par l article et le texte de soumission
# restent DURES -- c est precisement la que « chaque nombre est verifiable » doit tenir.
printf '  %-36s ' "chiffres de l'article"
if uv run --project "$ROOT" python "$ROOT/src/depot/verifier_chiffres.py" \
     "$ROOT/docs/article/article.typ" "$ROOT"/docs/archive/*.md "$ROOT"/docs/rapports/*.md \
     --article "$ROOT/docs/article/article.typ" \
     --soumission "$ROOT/docs/archive/21_texte_de_soumission.md" \
     --hors-perimetre > /tmp/release_chiffres.log 2>&1; then
  printf '✅ %s\n' "$(grep -c '✅' /tmp/release_chiffres.log) chiffres retrouves"
else
  printf '❌ ECHEC\n'; tail -4 /tmp/release_chiffres.log | sed 's/^/       /'
  FAIL=$((FAIL + 1))
fi

echo
printf '  %-36s %s\n' "batteries" "$BATTERIES batteries, $CONTROLES controles"
# ⚠ Les sauts sont COMPTES et imprimes : un controle saute en silence est un controle qu on
# croit avoir passe. Zero saut sur l arbre complet, deux sur la release -- et la difference
# doit se voir.
[ "$SAUTES" -gt 0 ] && printf '  %-36s %s\n' "sautés" \
    "$SAUTES, faute d'une entrée hors périmètre"
echo
if [ "$FAIL" -gt 0 ]; then echo "$FAIL batterie(s) en echec"; exit 1; fi
echo "LA RELEASE SE VERIFIE ELLE-MEME"
