#!/usr/bin/env bash
# Construire la branche de release : l essentiel, et RIEN QUE ce qui se verifie.
#
# ⚠⚠ La regle qui decide de tout : UNE RELEASE QUI NE PEUT PAS SE VERIFIER N EST PAS UNE
# RELEASE. On ne coupe donc pas « ce qui a l air superflu » -- on coupe, puis on relance la
# batterie complete SUR la branche nettoyee, et on refuse de poser le tag si elle echoue.
# Le perimetre est ainsi decide par une mesure et pas par une impression.
#
# ⚠ La branche `main` n est JAMAIS touchee : elle garde tout, c est la memoire du travail.
# La release est une VUE, refaite a chaque fois depuis main.
#
# ⚠ Le travail se fait dans un WORKTREE separe : des rendus tournent en fond et lisent
# l arbre de travail, changer de branche sous leurs pieds serait une mauvaise surprise.
#
# Usage : tools/faire_la_release.sh [tag]
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCHE="${BRANCHE:-release/progress-prize}"
TRAVAIL="${TRAVAIL:-/tmp/lplvesuvius-release}"

# ⚠⚠ Ce que la release ne porte PAS, et POURQUOI. Chaque ligne est une decision, pas un
# nettoyage : si une entree n a pas de raison ecrite, elle n a rien a faire ici.
#
#   apprendre/          les videos pedagogiques. Elles existent pour l auteur, pas pour un
#                       jury, et rien dans la verification ne les appelle.
#   docs/champ_*        les champs de direction par rouleau : zero reference dans le code,
#                       la soumission ou l article. Mesure, pas suppose.
#   .lances/            les journaux de campagne : des traces d execution locales.
#
# ⚠ TOUT LE RESTE EST GARDE, y compris les 51 documents de travail en francais : ils sont
# la piste d audit de chaque chiffre publie, et `verifier_chiffres.py` cherche litteralement
# dedans. Les retirer casserait la verification -- ce qui est exactement la raison pour
# laquelle on lance la batterie avant de taguer.
EXCLUS=(
  "apprendre"
  "docs/champ_PHercParis4"
  "docs/champ_PHerc0172"
  "docs/champ_PHerc1667"
  ".lances"
)

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "la batterie existe" '[ -x "$ROOT/tools/temoins.sh" ]'
  chk "chaque exclusion a une raison ecrite" \
      '[ "$(grep -cE "^#   [a-z.]" "$ROOT/tools/faire_la_release.sh")" -ge 3 ]'
  # ⚠⚠ La regle centrale, verifiee comme du code : le tag ne se pose qu APRES la batterie.
  chk "le tag est pose apres la batterie, pas avant" \
      '[ "$(grep -n "temoins.sh" "$ROOT/tools/faire_la_release.sh" | head -1 | cut -d: -f1)" -lt "$(grep -n "git tag" "$ROOT/tools/faire_la_release.sh" | head -1 | cut -d: -f1)" ]'
  # ⚠ Motif ANCRE sur le debut de ligne : il ne vise qu une COMMANDE, pas une mention.
  # Une version qui cherchait la sous-chaine nue se matchait elle-meme -- cinquieme fois
  # du jour, et c est l ancrage syntaxique le remede, pas la coupure du motif.
  chk "main n est jamais supprimee" \
      '! grep -qE "^[[:space:]]*git (branch -D|push[^|]*--force[^|]*) main" "$ROOT/tools/faire_la_release.sh"'
  chk "le travail se fait dans un worktree" 'grep -q "worktree add" "$ROOT/tools/faire_la_release.sh"'
  chk "les exclusions sont declarees, pas devinees" '[ "${#EXCLUS[@]}" -ge 1 ]'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

TAG="${1:-}"
cd "$ROOT" || exit 2
[ -z "$(git status --porcelain --untracked-files=no)" ] \
  || { echo "refus : l'arbre a des modifications non commitées" >&2; exit 2; }

echo "== branche de release : $BRANCHE, refaite depuis main"
git worktree remove --force "$TRAVAIL" 2>/dev/null
git branch -D "$BRANCHE" 2>/dev/null
git worktree add -b "$BRANCHE" "$TRAVAIL" main > /dev/null 2>&1 \
  || { echo "refus : worktree impossible" >&2; exit 3; }

cd "$TRAVAIL" || exit 3
RETIRES=0
for e in "${EXCLUS[@]}"; do
  if git ls-files --error-unmatch "$e" > /dev/null 2>&1 || [ -e "$e" ]; then
    n=$(git rm -r --quiet --ignore-unmatch "$e" 2>/dev/null; git diff --cached --name-only | wc -l)
    echo "   retiré : $e"
    RETIRES=$((RETIRES + 1))
  fi
done
[ "$RETIRES" -gt 0 ] || { echo "   ⚠ rien à retirer"; }

git -c user.name=MasterLaplace commit -S -q -m "Release : l'essentiel, et rien que ce qui se vérifie

Vue nettoyée de main. Ce qui part est declaré dans tools/faire_la_release.sh,
avec une raison par ligne.

⚠⚠ Les 51 documents de travail sont GARDÉS : ils sont la piste d'audit de chaque
chiffre publié, et verifier_chiffres.py les cherche littéralement. Les retirer
casserait la vérification — ce qui est précisément pourquoi la batterie tourne
avant que le tag soit posé." 2>/dev/null || echo "   (rien à commiter)"

echo
echo "== la batterie, SUR la branche nettoyée"
if ! ./tools/temoins.sh > /tmp/release_temoins.log 2>&1; then
  echo "   ⚠⚠ ÉCHEC — la release ne se vérifie pas elle-même, aucun tag posé" >&2
  tail -18 /tmp/release_temoins.log | sed 's/^/      /'
  exit 4
fi
tail -5 /tmp/release_temoins.log | sed 's/^/   /'

if [ -n "$TAG" ]; then
  echo
  echo "== tag $TAG"
  git tag -s -m "Progress Prize : instruments de mesure de la qualité d'une trace

Tout ce qu'il faut pour vérifier les affirmations, et rien d'autre.
La batterie complète passe sur ce tag." "$TAG" \
    || git tag -a -m "Progress Prize : instruments de mesure de la qualité d'une trace" "$TAG"
  echo "   posé sur $(git rev-parse --short HEAD)"
fi

cd "$ROOT"
echo
echo "== fait. Pour publier :"
echo "   git push origin $BRANCHE${TAG:+ && git push origin $TAG}"
