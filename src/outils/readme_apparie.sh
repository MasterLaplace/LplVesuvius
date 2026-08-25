#!/usr/bin/env bash
# Les commandes du README existent-elles, et tournent-elles ?
#
# ⚠⚠ « L appariement le plus rentable qui existe » selon les regles de l auteur : extraire
# les blocs de commandes d un README et les EXECUTER. Un exemple perime est la premiere
# cause de perte de confiance dans une doc, et il ne se voit jamais a la relecture -- le
# chemin a change, le drapeau a ete renomme, le README dit encore l ancien.
#
# ⚠ Deux niveaux, parce que tout n est pas executable : les commandes courtes et hors ligne
# sont LANCEES ; les campagnes longues sont seulement verifiees EXISTANTES, avec leurs
# drapeaux acceptes. Pretendre executer une campagne d une heure dans un controle serait un
# controle que personne ne lance.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 2
FICHIER="${1:-README.md}"

extraire() {
  # ⚠ Uniquement les blocs ```bash, et on saute les lignes de commentaire et les vides.
  awk '/^```bash$/{d=1;next} /^```$/{d=0} d' "$1" | grep -vE '^\s*(#|$)'
}

if [ "${2:-}" = "--verifier" ] || [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  T=$(mktemp -d)
  printf 'texte\n```bash\n# un commentaire\necho un\n\necho deux\n```\nsuite\n' > "$T/a.md"
  chk "les commandes sont extraites" '[ "$(extraire "$T/a.md" | wc -l)" = 2 ]'
  chk "les commentaires sont sautes" '! extraire "$T/a.md" | grep -q "^#"'
  printf 'pas de bloc ici\n' > "$T/b.md"
  chk "un fichier sans bloc rend zero commande" '[ -z "$(extraire "$T/b.md")" ]'
  # ⚠⚠ Le controle qui compte : une commande dont le FICHIER n existe pas doit etre
  # attrapee. C est la panne reelle -- un chemin renomme dans l arbre, pas dans la prose.
  printf '```bash\npython3 src/mesures/inexistant_xyz.py --verifier\n```\n' > "$T/c.md"
  out=$("$ROOT/src/outils/readme_apparie.sh" "$T/c.md" 2>&1); rc=$?
  chk "un chemin mort est attrape" '[ "$rc" != 0 ]'
  chk "... et il est nomme" 'printf "%s" "$out" | grep -q inexistant_xyz'
  printf '```bash\npython3 src/encre/langue.py --verifier\n```\n' > "$T/d.md"
  chk "une commande valide passe" '"$ROOT/src/outils/readme_apparie.sh" "$T/d.md" >/dev/null 2>&1'
  chk "... et elle est comptee comme LANCEE" \
      '"$ROOT/src/outils/readme_apparie.sh" "$T/d.md" 2>/dev/null | grep -q "1 lancee"'
  # ⚠⚠ Le controle du silence : un README dont AUCUNE commande n est executable doit le
  # DIRE, sinon « 0 probleme » se lit comme une garantie que rien n appuie.
  printf '```bash\n./src/outils/temoins.sh\n```\n' > "$T/e.md"
  chk "un README sans commande executable le signale" \
      '"$ROOT/src/outils/readme_apparie.sh" "$T/e.md" 2>&1 | grep -q "AUCUNE commande"' 
  rm -rf "$T"
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

[ -f "$FICHIER" ] || { echo "refus : $FICHIER introuvable" >&2; exit 2; }
MAUVAIS=0; LANCEES=0; VUES=0

while IFS= read -r cmd; do
  [ -n "$cmd" ] || continue
  VUES=$((VUES + 1))
  # Le premier chemin cite dans la commande doit exister.
  for mot in $cmd; do
    case "$mot" in
      */*)
        chemin="${mot%%\"*}"
        if [ ! -e "$chemin" ] && [ ! -e "${chemin#./}" ]; then
          echo "  ⚠ chemin absent : $chemin"
          echo "     dans : $cmd"
          MAUVAIS=$((MAUVAIS + 1))
        fi
        break ;;
    esac
  done
  # ⚠ On LANCE ce qui est hors ligne et court : un --verifier, un --help. Le reste est une
  # campagne, et l executer ici ferait de ce controle quelque chose que personne ne lance.
  case "$cmd" in
    *--verifier*|*--help*|*selftest*)
      if timeout 180 bash -c "$cmd" > /dev/null 2>&1; then
        LANCEES=$((LANCEES + 1))
      else
        echo "  ⚠ echoue : $cmd"; MAUVAIS=$((MAUVAIS + 1))
      fi ;;
  esac
done < <(extraire "$FICHIER")

# ⚠⚠ Le compte des NON LANCEES est imprime, et ce n est pas un detail : « 0 lancee,
# 0 probleme » se lit exactement comme un succes alors que rien n a tourne. Un controle
# doit dire ce qu il n a PAS fait, sinon son silence passe pour une garantie.
NON_LANCEES=$((VUES - LANCEES))
echo "$VUES commande(s) lues · $LANCEES lancee(s) · $NON_LANCEES verifiee(s) au chemin seul"
[ "$NON_LANCEES" = 0 ] || echo "   (les non lancees sont longues ou demandent le reseau)"
if [ "$LANCEES" = 0 ] && [ "$VUES" -gt 0 ]; then
  echo "   ⚠ AUCUNE commande n a ete executee : ce controle n a verifie que des chemins" >&2
fi
[ "$MAUVAIS" = 0 ] && echo "$MAUVAIS probleme" || { echo "$MAUVAIS probleme(s)"; false; }
