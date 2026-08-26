#!/bin/bash
# Lancer le GUI VC3D, et dire ce qui l'empeche quand il ne part pas.
#
# ⚠⚠ Ce fichier existe parce que « VC3D ne se lance plus » etait FAUX, et que la facon
# de s'en apercevoir coute une demi-heure. Mesure le 2026-08-26 :
#
#   * `VC3D --help` et `VC3D -h` font un SEGFAULT (code 139) et crachent un « CRASH
#     REPORT » de trente lignes. C'est le premier reflexe quand quelque chose cloche,
#     donc c'est ce qu'on voit -- et on en conclut que le binaire est casse. Il ne l'est
#     pas : lance SANS argument il demarre normalement. `--version`, lui, repond.
#   * Au demarrage il ecrit « Window state metadata mismatch; skipping restore ». Ce
#     n'est pas une panne, c'est le bon comportement : la geometrie sauvegardee porte la
#     signature de l'ecran ou elle a ete prise (`xcb|1|rdp-0:1920x1200+0+0@1.00`), et
#     VC3D REFUSE de restaurer une fenetre sur un ecran qui n'est plus le meme, plutot
#     que de la poser hors champ. L'avertissement se repete tant que la signature reste
#     dans le .ini ; `--repartir-de-zero` l'efface.
#
# ⚠ Le GUI n'est PAS la chaine de production. Les 44 outils `vc_*` de /usr/local/bin le
# sont, et c'est eux que `24` pilote. Le GUI sert a REGARDER.
set -u
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
BINAIRE=${VC3D_BIN:-/usr/local/bin/VC3D}
INI="$HOME/.VC3D/VC3D.ini"

usage() {
  cat <<'TXT'
lancer_vc3d.sh [--repartir-de-zero] [--verifier]

  (sans argument)        lance le GUI en arriere-plan, journal dans /tmp
  --repartir-de-zero     efface la geometrie memorisee avant de lancer
  --verifier             batterie hors ligne

⚠ Ne PAS passer --help au binaire lui-meme : il segfault (code 139). C'est un defaut
  amont, pas un signe qu'il est casse.
TXT
}

if [ "${1:-}" = "--verifier" ]; then
  # ⚠⚠ Des controles de COMPORTEMENT, pas de texte. La premiere version cherchait des
  # chaines DANS CE FICHIER -- donc la sonde qui retirait la chaine du message la retirait
  # aussi du motif, et les trois controles sont sortis MUETS. Un fichier ne peut pas se
  # verifier en se lisant : ce qu'on exerce ici est ce qu'il FAIT, avec un faux binaire.
  n=0; echecs=0
  chk() { n=$((n + 1)); if eval "$2" >/dev/null 2>&1; then :; else echo "  FAIL $1"; echecs=$((echecs + 1)); fi; }
  MOI="$ROOT/src/outils/lancer_vc3d.sh"
  BOITE=$(mktemp -d)
  # un faux VC3D qui NOTE ses arguments et reste en vie assez longtemps
  printf '#!/bin/bash\nprintf "%%s" "$#" > "%s/argv"\nsleep 30\n' "$BOITE" > "$BOITE/vivant"
  printf '#!/bin/bash\nexit 7\n' > "$BOITE/mort"
  chmod +x "$BOITE/vivant" "$BOITE/mort"

  # ⚠⚠ LE controle qui compte : le lanceur ne doit RIEN passer au binaire. C'est l'unique
  # chose que ce fichier existe pour empecher, puisque `VC3D --help` segfault (code 139).
  VC3D_BIN="$BOITE/vivant" VC3D_DELAI=1 "$MOI" --repartir-de-zero >/dev/null 2>&1
  chk "le binaire est lance SANS aucun argument" '[ "$(cat "$BOITE/argv" 2>/dev/null)" = 0 ]'
  pkill -f "$BOITE/vivant" 2>/dev/null

  # ... et le cas negatif, sans lequel le precedent passerait meme si rien n'etait lance.
  chk "le faux binaire a bien ete execute" '[ -f "$BOITE/argv" ]'

  # Un binaire qui meurt tout de suite doit etre RAPPORTE, pas annonce comme lance.
  VC3D_BIN="$BOITE/mort" VC3D_DELAI=1 "$MOI" >/dev/null 2>&1; rc=$?
  chk "un binaire qui meurt rend un code non nul" '[ "$rc" != 0 ]'

  # Sans affichage, refus AVANT de toucher au binaire : sinon on lit un crash Qt au lieu
  # de la vraie cause.
  rm -f "$BOITE/argv"
  ( unset DISPLAY WAYLAND_DISPLAY
    VC3D_BIN="$BOITE/vivant" VC3D_DELAI=1 "$MOI" >/dev/null 2>&1 ) ; rc=$?
  chk "sans affichage, le lanceur refuse" '[ "$rc" = 4 ]'
  chk "... et n'a PAS lance le binaire" '[ ! -f "$BOITE/argv" ]'

  # Un binaire absent est un refus nomme, pas un lancement silencieux.
  VC3D_BIN="$BOITE/pas-la" "$MOI" >/dev/null 2>&1; rc=$?
  chk "un binaire absent rend 3" '[ "$rc" = 3 ]'

  # Et `--help` DU LANCEUR doit expliquer, sans jamais atteindre le binaire.
  rm -f "$BOITE/argv"
  out=$(VC3D_BIN="$BOITE/vivant" "$MOI" --help 2>&1); rc=$?
  chk "l'aide du lanceur sort en 0" '[ "$rc" = 0 ]'
  chk "... sans lancer le binaire" '[ ! -f "$BOITE/argv" ]'
  chk "... et elle prévient du segfault" 'printf "%s" "$out" | grep -q 139'

  pkill -f "$BOITE/vivant" 2>/dev/null; rm -rf "$BOITE"
  if [ "$echecs" = 0 ]; then echo "ALL PASS (0 failures, $n checks)"; else
    echo "FAILURES ($echecs failures, $n checks)"; exit 1; fi
  exit 0
fi

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  --repartir-de-zero)
      if [ -f "$INI" ]; then
        cp "$INI" "$INI.avant-remise-a-zero"
        sed -i '/^geometry=/d; /^state=/d; /^state_meta\\/d' "$INI"
        echo "geometrie effacee (copie : $INI.avant-remise-a-zero)"
      fi ;;
  "") ;;
  *) echo "argument inconnu « $1 »" >&2; usage; exit 2 ;;
esac

[ -x "$BINAIRE" ] || { echo "refus : $BINAIRE introuvable ou non executable" >&2; exit 3; }
if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  echo "refus : aucun affichage (ni DISPLAY ni WAYLAND_DISPLAY)." >&2
  echo "  Sous WSL, verifier que /mnt/wslg existe et relancer un terminal." >&2
  exit 4
fi

JOURNAL=$(mktemp -t vc3d-XXXXXX.log)
nohup "$BINAIRE" > "$JOURNAL" 2>&1 &
PID=$!
sleep "${VC3D_DELAI:-8}"
if kill -0 "$PID" 2>/dev/null; then
  echo "VC3D lance (pid $PID) — journal : $JOURNAL"
  if grep -q "Window state metadata mismatch" "$JOURNAL"; then
    echo "  ⚠ geometrie non restauree (ecran different de celui enregistre) : c'est normal." \
         "Pour ne plus le voir : $0 --repartir-de-zero"
  fi
  exit 0
else
  echo "VC3D s'est arrete en moins de ${VC3D_DELAI:-8} secondes. Fin du journal :" >&2
  tail -12 "$JOURNAL" >&2
  exit 5
fi
