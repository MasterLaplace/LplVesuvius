#!/bin/bash
# `vc_render_tifxyz` sous surveillance : un rendu qui n'avance plus le DIT.
#
# ⚠⚠ Pourquoi ce script existe. Le 2026-08-22, un rendu de PHercParis4 a tourne QUINZE
# MINUTES en produisant 41 fichiers de 8 octets -- des souches vides. Mesure prise sur
# `/proc/<pid>/io` : 51 Mo lus, 1592 octets ecrits, soit ~57 Ko/s. Pour une surface de
# 3,65 cm² a 2,4 µm (~2,6 milliards de voxels) cela faisait plus de DOUZE HEURES, et rien
# dans la sortie ne le disait. Une campagne qui peut brasser une journee sans le signaler
# est une campagne qui gaspille une journee.
#
# ⭐ Le chien de garde ne mesure pas le temps ecoule -- un rendu long n'est pas un rendu
# bloque -- mais l'ACTIVITE DU PROCESSUS, lue dans `/proc/<pid>/io`.
#
# ⚠⚠ Et pas la croissance de la SORTIE, qui etait ma premiere version et qui etait fausse :
# `vc_render_tifxyz` telecharge tout avant d'ecrire. Mesure prise sur le run suivant --
# `rchar` passait de 6,56 a 8,21 Mo en douze secondes pendant que `wchar` restait a 500
# octets et que la sortie restait a 328. Un chien de garde sur la sortie aurait tue un rendu
# parfaitement sain, ce qui est pire que pas de chien de garde du tout : on aurait conclu
# « ce rendu est injouable » sur un rendu qui marchait.
#
# ⚠ Et il rapporte le debit dans les deux cas, succes compris : c'est ce chiffre qui dit si
# la meme campagne est jouable a une autre echelle, et le deviner apres coup est impossible.
#
#   ./tools/rendre_surveille.sh <sortie_tif> <patience_s> -- <arguments de vc_render_tifxyz>
set -u

# ⚠⚠ La commande est INJECTABLE, et c'est une prise de test assumee. Un chien de garde qui
# ne peut etre exercé qu'en lancant un vrai rendu de cent mégaoctets n'est pas exercé -- et
# celui-ci a DEJA eu un defaut (il surveillait la taille de la sortie, donc il aurait tué un
# rendu sain). La valeur par defaut reste `vc_render_tifxyz` ; seule la batterie de temoins
# la remplace.
RENDU=${RENDU:-vc_render_tifxyz}

if [ "${1:-}" = "--verifier" ]; then
  T=$(mktemp -d); E=0; N=0
  v() { N=$((N + 1)); if [ "$2" != "$3" ]; then E=$((E + 1))
        echo "  ECHEC  $1 — attendu $3, obtenu $2"; fi; }

  # ⚠ Un processus qui ne fait RIEN doit etre abandonne. `sleep` ne lit ni n'ecrit, donc son
  # compteur d'activite ne bouge pas : c'est exactement le cas que le chien de garde existe
  # pour attraper.
  # ⚠⚠ Le plafond de cache ne doit se poser que sur le VRAI moteur. Un faux moteur qui le
  # recevrait echouerait sur un argument inconnu -- ce qui est exactement arrive quand je
  # l ai pose sans condition, et que cette batterie a attrape dans la seconde.
  RENDU="echo" "$0" "$T/faux" 10 -- args > "$T/faux.log" 2>&1
  grep -q -- "--cache-gb" "$T/faux.log"; v "un faux moteur ne reçoit PAS --cache-gb" "$?" "1"
  # ⚠ Un faux moteur PORTANT LE NOM du vrai : « $RENDU » est un chemin de commande, pas une
  # ligne de shell, donc on ne peut pas y glisser un argument. Il faut un exécutable.
  mkdir -p "$T/bin"
  printf '#!/bin/sh\necho "$@"\n' > "$T/bin/vc_render_tifxyz"; chmod +x "$T/bin/vc_render_tifxyz"
  RENDU="$T/bin/vc_render_tifxyz" "$0" "$T/vrai" 10 -- args > "$T/vrai.log" 2>&1
  grep -q -- "--cache-gb 1" "$T/vrai.log"; v "le vrai moteur le reçoit" "$?" "0"
  RENDU="$T/bin/vc_render_tifxyz" CACHE_GB=7 "$0" "$T/sept" 10 -- args > "$T/sept.log" 2>&1
  grep -q -- "--cache-gb 7" "$T/sept.log"; v "... et CACHE_GB le pilote" "$?" "0"
  RENDU="$T/bin/vc_render_tifxyz" "$0" "$T/expl" 10 -- --cache-gb 9 > "$T/expl.log" 2>&1
  test "$(grep -o -- "--cache-gb" "$T/expl.log" | wc -l)" = "1"
  v "... et un choix explicite n'est pas doublé" "$?" "0"
  grep -q -- "--cache-gb 9" "$T/expl.log"; v "... c'est le choix de l'appelant qui reste" "$?" "0"

  RENDU="sleep" "$0" "$T/vide" 10 -- 120 > "$T/vide.log" 2>&1; v "un processus inactif est abandonné" "$?" "4"
  grep -q "ABANDONNE" "$T/vide.log"; v "... en le disant" "$?" "0"
  grep -q "octets d'activité" "$T/vide.log"; v "... avec son activité mesurée" "$?" "0"

  # ⚠⚠ Le controle : un processus qui TRAVAILLE ne doit pas etre tue. Sans lui, un chien de
  # garde qui tuerait tout passerait ses temoins -- c'est le defaut qu'il a deja eu.
  # ⚠ Le travail est fait EN PROCESSUS, par le builtin `read` -- c'est un modele fidele de
  # l'appelant reel. Ma premiere version bouclait sur `cat`, donc l'I/O partait dans des
  # ENFANTS et les compteurs du parent restaient plats : le controle echouait sur une forme
  # que `vc_render_tifxyz` n'a pas, et il aurait fait « corriger » l'outil contre un cas
  # imaginaire.
  RENDU="bash" "$0" "$T/actif" 10 -- -c 'for i in $(seq 1 60); do read -r _ < /etc/hostname; sleep 0.3; done' \
      > "$T/actif.log" 2>&1; v "un processus qui travaille n'est PAS tué" "$?" "0"
  grep -q "rendu :" "$T/actif.log"; v "... et son débit est rapporté" "$?" "0"

  # ⚠⚠ LA COURSE : un rendu qui finit ENTRE deux sondages ne doit pas etre declare
  # abandonne. Le sondage vaut 10 s, donc une commande de ~12 s traverse exactement ce cas.
  RENDU="bash" "$0" "$T/court" 10 -- -c 'for i in $(seq 1 40); do read -r _ < /etc/hostname; sleep 0.3; done' \
      > "$T/court.log" 2>&1; v "un rendu qui finit entre deux sondages réussit" "$?" "0"
  grep -q "ABANDONNE" "$T/court.log"; v "... et n'est pas dit abandonné" "$?" "1"

  # ⚠ Un processus qui echoue doit propager SON code, pas un succes.
  RENDU="false" "$0" "$T/rate" 10 -- > "$T/rate.log" 2>&1; v "un rendu qui échoue propage son code" "$?" "1"

  rm -rf "$T"
  if [ "$E" -gt 0 ]; then echo "ECHEC ($E failures, $N checks)"; exit 1; fi
  echo "ALL PASS (0 failures, $N checks)"; exit 0
fi

SORTIE=${1:?sortie tif}
PATIENCE=${2:?patience en secondes}
shift 2
[ "${1:-}" = "--" ] && shift

taille() { du -sb "$SORTIE" 2>/dev/null | cut -f1 || echo 0; }
# ⚠ Somme des octets lus ET ecrits : un rendu qui telecharge fait bouger `rchar` seul, un
# rendu qui vide ses tampons fait bouger `wchar` seul. Prendre l'un des deux raterait la
# moitie des phases.
#
# ⚠⚠ Et la TAILLE DE SORTIE s'ajoute, en OU et pas en ET. Les compteurs de `/proc` ne
# couvrent que le processus DIRECT : une commande qui fait son travail dans des processus
# ENFANTS a des compteurs immobiles alors qu'elle avance. Trouve par le controle de
# l'auto-test, qui utilisait `cat` dans une boucle -- le chien de garde a tue un processus
# parfaitement actif. N'importe lequel des deux signaux suffit desormais a dire « vivant ».
#
# ⚠⚠ LIMITE ASSUMEE, et j'ai d'abord voulu la retirer plutot que l'ecrire. Le OU ne couvre
# pas le cas ou une commande fait TOUT son travail dans des processus enfants ET n'ecrit
# rien avant la fin : les deux signaux restent alors plats et elle sera abandonnee a tort.
# La couvrir demanderait de marcher l'arbre de processus a chaque sondage, ce qui est de la
# complexite pour une forme que l'appelant n'a pas -- `vc_render_tifxyz` est un processus
# unique a threads, et les threads PARTAGENT les compteurs de `/proc`. La limite est donc
# nommee ici pour que le prochain appelant verifie, plutot que codee contre un cas
# hypothetique.
# ⚠⚠ Rend une chaine VIDE quand `/proc/<pid>/io` n'existe plus, et jamais zero. Le processus
# peut finir entre le `kill -0` et cette lecture : lire alors « 0 » se lit comme une
# inactivite totale, et le chien de garde declare abandonne un rendu qui VIENT DE REUSSIR.
# Trouve par l'auto-test, sur un rendu de 18 secondes -- donc il aurait frappe n'importe
# quel rendu court, c'est-a-dire les bons.
activite() {
  [ -r "/proc/$1/io" ] || return 1
  A=$(awk '/^rchar:|^wchar:/{t += $2} END{print t + 0}' "/proc/$1/io" 2>/dev/null) || return 1
  [ -n "${A:-}" ] || return 1
  echo $(( A + $(taille) ))
}

mkdir -p "$SORTIE"
DEBUT=$(date +%s)

# ⚠⚠ Le cache de chunks, plafonne ICI parce que c est le seul endroit que toutes les
# campagnes traversent. Son defaut est 16 Go -- la moitie de cette machine -- et aucun des
# 28 appels du depot ne le reglait : sur une surface de 3,66 cm2 il l atteint reellement et
# met la machine en swap (28,2 Go de RSS, 274 Mo libres, 23,7 % d UN c ur sur 22).
#
# ⚠ La valeur vient d une MESURE (docs/50, tools/etalonner_rendu.sh) : quinze rendus, cinq
# valeurs, trois repetitions. 1 Go donne le pic le plus bas ET la mediane la plus basse, et
# surtout les quinze sorties sont IDENTIQUES au sha256 -- donc plafonner ne change aucun
# resultat deja publie. Sans cette verification on ne pourrait pas le poser ici.
#
# ⚠ Un appelant qui passe deja --cache-gb garde le sien : le defaut ne doit pas ecraser un
# choix explicite, sinon on ne pourrait plus etalonner.
# ⚠⚠ Conditionne au MOTEUR : ce script est generique (RENDU est surchargeable, et sa propre
# batterie l appelle avec `sleep`), donc ajouter un drapeau specifique a vc_render_tifxyz a
# tout ce qui passe casse l auto-test -- il l a d ailleurs attrape dans la seconde. Un
# drapeau propre a un programme ne se pose que sur ce programme.
CACHE_GB=${CACHE_GB:-1}
case "$RENDU" in
  *vc_render_tifxyz*)
    case " $* " in
      *" --cache-gb "*) ;;
      *) set -- "$@" --cache-gb "$CACHE_GB" ;;
    esac
    ;;
esac

"$RENDU" "$@" &
PID=$!

DERNIERE=$(activite "$PID" || echo 0); IMMOBILE=0
while kill -0 "$PID" 2>/dev/null; do
  sleep 10
  # ⚠ Si la lecture echoue, le processus est parti : on sort par la porte normale et c'est
  # `wait` qui donnera son code. Le traiter comme « inactif » serait tuer un mort et le
  # rapporter comme un echec.
  T=$(activite "$PID") || break
  if [ "${T:-0}" -gt "${DERNIERE:-0}" ]; then
    DERNIERE=$T; IMMOBILE=0
  else
    IMMOBILE=$((IMMOBILE + 10))
    if [ "$IMMOBILE" -ge "$PATIENCE" ]; then
      # ⚠⚠ On tue par PID et jamais par motif : `pkill -f` matche sa PROPRE ligne de
      # commande, ce qui a deja tue trois shells dans ce depot.
      kill "$PID" 2>/dev/null
      wait "$PID" 2>/dev/null
      ECOULE=$(( $(date +%s) - DEBUT ))
      echo "⚠⚠ RENDU ABANDONNE — ni activité du processus ni sortie depuis ${PATIENCE} s" >&2
      echo "   ${DERNIERE} octets d'activité en ${ECOULE} s, sortie $(taille) octets" >&2
      echo "   Ce n'est pas une panne du script : c'est la mesure que ce rendu-la n'est" >&2
      echo "   pas jouable a cette echelle. Baisser --scale, ou reduire l'aire." >&2
      exit 4
    fi
  fi
done
wait "$PID"; RC=$?
ECOULE=$(( $(date +%s) - DEBUT ))
FIN=$(taille)
# ⚠ Division gardee : un rendu instantane ferait diviser par zero, et un debit infini
# n'apprend rien a personne.
if [ "$ECOULE" -gt 0 ]; then
  echo "   rendu : ${FIN} octets en ${ECOULE} s ($((FIN / ECOULE / 1024)) Kio/s)"
else
  echo "   rendu : ${FIN} octets en moins d'une seconde"
fi
exit "$RC"
