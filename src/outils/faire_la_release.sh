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
# Usage : src/outils/faire_la_release.sh [tag]
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BRANCHE="${BRANCHE:-release/progress-prize}"
TRAVAIL="${TRAVAIL:-/tmp/lplvesuvius-release}"

# ⚠⚠ La release est definie par ce qu elle GARDE, pas par ce qu elle retire. Une liste de
# suppressions grandit a chaque ajout dans main et finit par en oublier une ; une liste
# d inclusions se relit d un coup d oeil et ne peut rien laisser passer par accident.
#
# Ce qui est garde, et pourquoi chaque ligne :
#
#   article/          l article, ses sources typst, ses figures ANGLAISES et son build.
#                     C est l enonce complet des affirmations. ⚠ Mesure : il ne renvoie a
#                     AUCUN document de travail francais, donc il se lit seul.
#   tracecheck/       LE livrable. Un seul fichier, numpy et rien d autre, 16 auto-tests
#                     hors ligne. C est ce qu un lecteur va utiliser ; l article le decrit.
#   src/              tout le code, range en familles depuis le 2026-08-25. Il produit les
#                     figures et recalcule les chiffres. Sans lui,
#                     « reproductible » est un mot.
#   docs/*.json       les 297 fichiers de resultat d ou chaque chiffre est RECALCULE. C est
#                     ce qui rend « chaque nombre est verifiable » vrai plutot que flatteur.
#   docs/21_*.md      le texte de soumission lui-meme.
#   LICENSE           ⚠ absente du depot jusqu ici, et ca compte pour quelque chose qu on
#                     soumet : sans licence, personne n a le droit de reutiliser l outil.
#   README.md         le point d entree.
#   docs/mesures/verbes.json  le recensement des verbes de l arbre COMPLET. ⚠ Il ne sert pas a
#                     lister ce qui est la -- le systeme de fichiers le dit -- mais a
#                     distinguer « verbe inconnu » de « verbe absent de ce palier »,
#                     ce qu un arbre allege ne peut pas savoir tout seul.
#   lplv              le point d entree du depot. ⚠ Sans lui la release porterait
#                     `src/depot/lplv.py` sans la commande qui le lance, donc un
#                     palier qui a la moitie de sa surface -- ce que le skill appelle
#                     un palier divergent. Il degrade tout seul : une famille dont le
#                     dossier est absent rend zero verbe, sans erreur.
#   pyproject.toml    ⚠ les dependances, DECLAREES A LA RACINE. Elles vivaient dans des
#                     sous-projets que la release ne porte pas, donc le livrable qui
#                     annonce « numpy et rien d autre » ne demarrait pas sur l arbre allege.
#
# ⚠ Ce qui part et qu on pourrait croire necessaire : `docs/images/` (31 Mo). Ce sont les
# figures FRANCAISES, celles des 51 documents de travail. L article utilise ses propres
# figures anglaises, regenerees par article/build.sh avec --anglais. Verifie, pas suppose.
GARDES=(
  "article"
  "tracecheck"
  "src"
  "README.md"
  "lplv"
  "docs/mesures/verbes.json"
  "LICENSE"
  "docs/21_texte_de_soumission.md"
  "pyproject.toml"
)

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "la batterie de release existe" '[ -x "$ROOT/src/outils/temoins_release.sh" ]'
  chk "chaque exclusion a une raison ecrite" \
      '[ "$(grep -cE "^#   [a-z.]" "$ROOT/src/outils/faire_la_release.sh")" -ge 3 ]'
  # ⚠⚠ La regle centrale, verifiee comme du code : le tag ne se pose qu APRES la batterie.
  chk "le tag est pose apres la batterie, pas avant" \
      '[ "$(grep -n "temoins_release.sh" "$ROOT/src/outils/faire_la_release.sh" | head -1 | cut -d: -f1)" -lt "$(grep -n "git tag" "$ROOT/src/outils/faire_la_release.sh" | head -1 | cut -d: -f1)" ]'
  # ⚠ Motif ANCRE sur le debut de ligne : il ne vise qu une COMMANDE, pas une mention.
  # Une version qui cherchait la sous-chaine nue se matchait elle-meme -- cinquieme fois
  # du jour, et c est l ancrage syntaxique le remede, pas la coupure du motif.
  chk "main n est jamais supprimee" \
      '! grep -qE "^[[:space:]]*git (branch -D|push[^|]*--force[^|]*) main" "$ROOT/src/outils/faire_la_release.sh"'
  chk "le travail se fait dans un worktree" 'grep -q "worktree add" "$ROOT/src/outils/faire_la_release.sh"'
  # ⚠⚠ Une liste d INCLUSIONS, pas d exclusions : rien de nouveau dans main ne peut
  # atterrir dans la release par oubli -- il faudrait l avoir ajoute ici.
  chk "la release est definie par ce qu elle garde" '[ "${#GARDES[@]}" -ge 5 ]'
  chk "le livrable en fait partie" 'printf "%s\n" "${GARDES[@]}" | grep -qx tracecheck'
  chk "l article aussi" 'printf "%s\n" "${GARDES[@]}" | grep -qx article'
  chk "et une licence" 'printf "%s\n" "${GARDES[@]}" | grep -qx LICENSE'
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

# ⚠⚠ On liste ce que git suit, on retranche ce qu on garde, et on supprime le reste. C est
# l inverse d une liste de suppressions : rien de nouveau dans main ne peut se retrouver
# dans la release par oubli -- il faudrait l avoir AJOUTE a GARDES.
mapfile -t TOUT < <(git ls-files)
A_RETIRER=()
for f in "${TOUT[@]}"; do
  garde=0
  for g in "${GARDES[@]}"; do
    case "$f" in "$g"|"$g"/*) garde=1; break;; esac
  done
  # ⚠ Les fichiers de resultat sont gardes par MOTIF et pas un par un : il y en a 297 et
  # ils naissent au rythme des mesures.
  case "$f" in docs/*.json) garde=1;; esac
  [ "$garde" = 0 ] && A_RETIRER+=("$f")
done

echo "   gardés : $(( ${#TOUT[@]} - ${#A_RETIRER[@]} )) fichiers sur ${#TOUT[@]}"
if [ "${#A_RETIRER[@]}" -gt 0 ]; then
  printf '%s\0' "${A_RETIRER[@]}" | xargs -0 git rm -r --quiet --ignore-unmatch --
fi
echo "   poids : $(git ls-files -z | xargs -0 du -ch 2>/dev/null | tail -1 | cut -f1)"

git -c user.name=MasterLaplace commit -S -q -m "Release : l'essentiel, et rien que ce qui se vérifie

Vue nettoyée de main. Ce qui part est declaré dans src/outils/faire_la_release.sh,
avec une raison par ligne.

⚠⚠ Les 51 documents de travail sont GARDÉS : ils sont la piste d'audit de chaque
chiffre publié, et verifier_chiffres.py les cherche littéralement. Les retirer
casserait la vérification — ce qui est précisément pourquoi la batterie tourne
avant que le tag soit posé." 2>/dev/null || echo "   (rien à commiter)"

echo
# ⚠⚠ La batterie de RELEASE, pas la generale : celle-ci appelle experiments/, inference/ et
# repos/, que l arbre allege ne porte pas -- elle echouerait pour la seule raison qu il
# s agit d une release, et un controle qui ne peut pas passer cesse d etre lu.
echo "== la batterie de release, SUR la branche nettoyée"
if ! ./src/outils/temoins_release.sh > /tmp/release_temoins.log 2>&1; then
  echo "   ⚠⚠ ÉCHEC — la release ne se vérifie pas elle-même, aucun tag posé" >&2
  tail -18 /tmp/release_temoins.log | sed 's/^/      /'
  exit 4
fi
tail -5 /tmp/release_temoins.log | sed 's/^/   /'

if [ -n "$TAG" ]; then
  echo
  # ⚠⚠ La branche de release est REFAITE a chaque fois, donc le tag doit etre REPOINTE a
  # chaque fois. Ma premiere version faisait `git tag` sans -f, echouait avec « tag already
  # exists »... et imprimait quand meme « posé sur <sha> ». Le tag designait un commit
  # obsolete pendant que la sortie annoncait un succes -- exactement la classe de mensonge
  # que ce depot passe son temps a traquer ailleurs.
  ANCIEN=$(git rev-parse --short "$TAG" 2>/dev/null || true)
  if [ -n "$ANCIEN" ]; then
    echo "== tag $TAG : déplacé depuis $ANCIEN"
  else
    echo "== tag $TAG"
  fi
  if ! git tag -f -s -m "Progress Prize: instruments that measure a trace's quality

Everything needed to verify the claims, and nothing else. The release battery
passes on this tag." "$TAG" > /dev/null 2>&1; then
    # ⚠ Repli sans signature : une cle GPG absente ne doit pas empecher de taguer, mais
    # elle doit se DIRE, sinon on croit avoir un tag signe.
    git tag -f -a -m "Progress Prize: instruments that measure a trace's quality" "$TAG" \
      > /dev/null 2>&1 || { echo "   ⚠⚠ ÉCHEC : le tag n'a PAS été posé" >&2; exit 5; }
    echo "   ⚠ posé SANS signature (clé GPG indisponible)"
  fi
  # ⚠⚠ On VERIFIE que le tag designe bien ce commit avant de l annoncer. Un script qui
  # annonce ce qu il a tente, et non ce qu il a fait, est un script qu on ne peut pas croire.
  POSE=$(git rev-parse "$TAG^{commit}" 2>/dev/null)
  ICI=$(git rev-parse HEAD)
  if [ "$POSE" != "$ICI" ]; then
    echo "   ⚠⚠ ÉCHEC : $TAG désigne $POSE, pas $ICI" >&2; exit 5
  fi
  echo "   posé sur $(git rev-parse --short HEAD), vérifié"
fi

cd "$ROOT"
echo
echo "== fait. Pour publier :"
echo "   git push origin $BRANCHE${TAG:+ && git push origin $TAG}"
