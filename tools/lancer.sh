#!/bin/bash
# Lancer un script long depuis une COPIE FIGEE, pour qu'on puisse editer l'original.
#
# ⚠⚠ Pourquoi ce fichier existe. `bash` lit un script **par offset au fil de l'execution** :
# editer le fichier pendant qu'il tourne decale les octets sous ses pieds et il reprend au
# milieu d'un token. Le symptome est une « erreur de syntaxe » a une ligne parfaitement
# valide, longtemps apres l'edition, sur un fichier que `bash -n` accepte.
#
# Ce piege est ecrit dans le CLAUDE.md de l'espace de travail et dans le HANDOFF de ce
# depot. Il a ete paye **trois fois le 2026-08-20** : deux campagnes tuees en cours de
# route, dont une qui a perdu son dernier rouleau. La vigilance a donc echoue trois fois
# sur trois, et le remede ne peut pas etre une note de plus.
#
# La copie est figee AVANT le lancement. Editer l'original devient sans effet sur le run,
# ce qui est exactement la propriete voulue -- on corrige un script pendant que sa version
# precedente finit son travail.
#
# ⚠⚠ OU la copie vit n'est pas un detail. Les scripts d'ici commencent tous par
# `cd "$(dirname "$0")/.."`, donc le gel doit etre un ENFANT DIRECT de la racine pour que
# ce `..` retombe dessus. Une copie sous `data/.lances/` ferait atterrir la campagne dans
# `data/`, ou elle chercherait `analysis/src/...` et ne le trouverait pas. D'ou `.lances/`
# a la racine -- verifie par le temoin de ce fichier, pas suppose.
#
#   ./tools/lancer.sh tools/campagne_x.sh arg1 arg2 …
#   ./tools/lancer.sh --fond tools/campagne_x.sh …     # en tache de fond, imprime le PID
set -u
cd "$(dirname "$0")/.." || exit 2
RACINE=$PWD
FOND=0
[ "${1:-}" = "--fond" ] && { FOND=1; shift; }
SCRIPT=${1:?usage: tools/lancer.sh [--fond] <script> [args...]}; shift

if [ "${1:-}" = "--verifier" ] || [ "$SCRIPT" = "--verifier" ]; then
  # ⭐ Deux proprietes, et la seconde est la raison d'etre du fichier.
  #
  # ⚠⚠ La cible reproduit la FORME exacte de la panne du 2026-08-20, obtenue par mesure
  # apres deux modeles faux : une boucle qui tourne, une edition pendant qu'elle tourne, et
  # DU SCRIPT APRES la boucle. `bash` parse un compound command en entier, l'execute, puis
  # cherche la commande suivante a son offset sauve -- que l'edition a decale. Il reprend
  # alors au milieu d'une ligne.
  #
  # ⚠ Le symptome n'est pas seulement un arret : dans le repro, le dernier tour de boucle
  # s'execute DEUX FOIS avant l'erreur. Une edition en cours d'execution peut donc rejouer
  # du travail, pas seulement l'interrompre.
  #
  # ⚠ L'edition doit reecrire le fichier EN PLACE. `sed -i` cree un nouvel inode et renomme
  # par-dessus, donc le bash en cours garde son ancien inode et n'est PAS touche : un temoin
  # bati sur `sed -i` passe au vert quoi qu'il arrive (sonde du 2026-08-20, il etait aveugle).
  T=$(mktemp -d); E=0; N=0
  ok() { N=$((N+1)); [ "$2" = "$3" ] || { E=$((E+1)); echo "  ECHEC  $1 — attendu « $3 », obtenu « $2 »"; }; }
  CIBLE="$RACINE/tools/.temoin_lancer.sh"
  ecrire_cible() {
    cat > "$CIBLE" <<'FIN'
#!/bin/bash
cd "$(dirname "$0")/.." || exit 2
echo "racine=$PWD"
for i in 1 2 3; do
  sleep 0.4
  printf 'tour %s
' "$i"
done
echo "phase2=original"
FIN
    chmod +x "$CIBLE"
  }
  editer_en_place() {
    python3 -c "
import pathlib, sys
p = pathlib.Path(sys.argv[1]); p.write_text('# ligne inseree pendant que ca tourne\n' + p.read_text())" "$CIBLE"
  }

  # 1. le gel se localise a la racine du depot, malgre son `cd \$(dirname \$0)/..`
  ecrire_cible
  R=$("$RACINE/tools/lancer.sh" tools/.temoin_lancer.sh 2>/dev/null | grep '^racine=' | cut -d= -f2)
  ok "le gel trouve la racine du dépôt" "$R" "$RACINE"

  # 2. ⭐ le CONTROLE NEGATIF : lance en direct, l'edition DOIT casser le run. Sans lui,
  # la propriete 3 passerait sur une machine ou l'edition ne casse rien, et le fichier
  # entier serait une precaution invérifiable.
  ecrire_cible
  ( cd "$RACINE" && bash tools/.temoin_lancer.sh ) > "$T/direct" 2>&1 &
  PD=$!; sleep 0.5; editer_en_place; wait $PD 2>/dev/null
  ok "lancé en direct, l'édition casse le run" "$(grep -c 'phase2=original' "$T/direct")" "0"

  # 3. ⭐ la propriete : par le gel, la meme edition ne change RIEN au run.
  ecrire_cible
  # ⚠ La sortie de l'enfant va au JOURNAL, pas au tube de l'appelant, depuis que `--fond`
  # detache vraiment. Le temoin le lit donc la, en imposant le chemin par LPLV_JOURNAL --
  # sinon il verifierait le message du wrapper et pas le travail du script.
  LPLV_JOURNAL="$T/gel" "$RACINE/tools/lancer.sh" --fond tools/.temoin_lancer.sh > /dev/null 2>&1
  # ⚠ On attend le PID que le wrapper ecrit, pas `wait` : le travailleur est un petit-fils
  # du shell de test, donc `wait` ne le voit pas (piege nº 28bis du HANDOFF).
  PID=$(cat "$RACINE"/.lances/.temoin_lancer-*.pid 2>/dev/null | tail -1)
  sleep 0.5; editer_en_place
  for _ in $(seq 1 80); do kill -0 "$PID" 2>/dev/null || break; sleep 0.2; done
  ok "par le gel, l'édition ne change rien" "$(grep -c 'phase2=original' "$T/gel")" "1"

  rm -f "$CIBLE" "$RACINE"/.lances/.temoin_lancer-*; rm -rf "$T"
  if [ "$E" -gt 0 ]; then echo "ECHEC ($E failures, $N checks)"; exit 1; fi
  echo "ALL PASS ($E failures, $N checks)"; exit 0
fi

[ -f "$SCRIPT" ] || { echo "introuvable : $SCRIPT" >&2; exit 2; }
LANCES="$RACINE/.lances"
mkdir -p "$LANCES"
HORO=$(date +%Y%m%d-%H%M%S)
GEL="$LANCES/$(basename "$SCRIPT" .sh)-$HORO.sh"
cp "$SCRIPT" "$GEL"
chmod +x "$GEL"
echo "figé : $GEL"

if [ "$FOND" -eq 1 ]; then
  # ⚠ La sortie de l'enfant est REDIRIGEE vers un journal, et non heritee. Sans ça il garde
  # le tube de l'appelant ouvert, donc un `tools/lancer.sh --fond … | tail` bloque jusqu'a
  # la fin de la campagne -- c'est-a-dire l'inverse de ce que « en fond » veut dire.
  JOURNAL=${LPLV_JOURNAL:-$LANCES/$(basename "$GEL" .sh).log}
  ( cd "$RACINE" && exec bash "$GEL" "$@" ) > "$JOURNAL" 2>&1 < /dev/null &
  echo "$!" > "$LANCES/$(basename "$GEL" .sh).pid"
  echo "lancé en fond — pid $!"
  echo "  journal : $JOURNAL"
  echo "  pidfile : $LANCES/$(basename "$GEL" .sh).pid"
else
  ( cd "$RACINE" && exec bash "$GEL" "$@" )
fi
