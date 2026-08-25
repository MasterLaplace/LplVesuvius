#!/usr/bin/env bash
# LE TEMOIN POSITIF DE NOTRE CHAINE DE RENDU : rendre une surface PUBLIEE avec nos outils.
#
# ⚠⚠ POURQUOI. Tout le classement des candidats repose sur une hypothese que rien n avait
# mise a l epreuve : que NOTRE chaine de rendu produit des piles comparables a celles que la
# communaute publie. Si elle ecrase le relief, « nos traces sont plates » ne dit rien sur nos
# traces -- c est une propriete de notre instrument, et le classement est un artefact.
#
# Le controle est direct parce que le maillage publie est dans le format EXACT du notre
# (`tifxyz` : meta.json + x/y/z.tif, scale 0,05). On decoupe donc un morceau publie a la
# taille de nos candidats (`src/nappe/decouper_tifxyz.py`), on le rend AVEC NOTRE CHAINE,
# et on lit son relief a la geometrie du corpus.
#
# ⭐ CE QUI SE DECIDE, et il faut l ecrire AVANT de mesurer :
#   - le morceau publie revient dans la distribution du corpus  => notre chaine est fidele,
#     et le deficit de nos traces est une propriete de NOS TRACES ;
#   - il revient effondre, au niveau de nos candidats             => c est notre chaine qu il
#     faut reparer avant de juger quoi que ce soit d autre.
# Un temoin dont on n a pas dit d avance ce qu il condamnerait ne condamne jamais rien.
#
# ⚠ Le rendu et la situation sont DELEGUES : `profiler_une_surface.sh` porte l invocation du
# moteur (une seule dans ce depot) et `situer_nos_traces.sh` porte la relecture a la
# geometrie du corpus. Recopier l une ou l autre ici en ferait deux, libres de diverger sur
# le pas, la couche tracee ou la sous-fenetre -- et la comparaison mesurerait la difference
# des scripts.
#
# Usage : CORPUS=docs/balayage_scroll1.csv src/outils/temoin_du_rendu.sh <morceau>...
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  # ⚠ Les deux delegations : ce fichier ne doit contenir NI l appel au moteur de rendu NI
  # le calcul de la sous-fenetre. Les sondes portent sur l absence autant que sur la
  # presence, parce que c est la recopie qui est le defaut, pas l oubli.
  chk "le rendu est delegue au profileur" \
      'grep -q "profiler_une_surface.sh" "$ROOT/src/outils/temoin_du_rendu.sh"'
  # ⚠⚠ LES DEUX MOTIFS INTERDITS SONT COMPOSES A L EXECUTION. Ecrits en clair, ces deux
  # sondes contiendraient exactement ce qu elles interdisent et echoueraient toujours -- ce
  # qui vient d arriver au premier lancement. C est la dixieme fois que ce depot paie
  # l auto-match, et sa forme MIROIR : une sonde qui exige une ABSENCE se contredit
  # elle-meme, la ou une sonde qui exige une presence se contente d avoir tort en silence.
  MOTEUR="vc_render""_tifxyz"
  COUCHE="traced""-layer"
  chk "... et le moteur n est PAS invoque ici" \
      '! grep -q "$MOTEUR" "$ROOT/src/outils/temoin_du_rendu.sh"'
  chk "la situation est deleguee" \
      'grep -q "situer_nos_traces.sh" "$ROOT/src/outils/temoin_du_rendu.sh"'
  chk "... et la sous-fenetre n est PAS recalculee ici" \
      '! grep -q "$COUCHE" "$ROOT/src/outils/temoin_du_rendu.sh"'
  # ⚠⚠ La pile doit etre CONSERVEE, sinon la relecture a 128 px n a rien a lire et on
  # repaie dix-sept minutes de rendu par morceau pour poser la seconde question.
  chk "la pile rendue est conservee" \
      'grep -q "GARDER_RENDU=1" "$ROOT/src/outils/temoin_du_rendu.sh"'
  # ⚠⚠ Ce que le temoin condamnerait doit etre ECRIT, et dans le fichier -- pas dans la tete
  # de qui le lance. Un temoin sans critere annonce s explique toujours apres coup.
  chk "le critere de condamnation est ecrit" \
      'grep -q "CE QUI SE DECIDE" "$ROOT/src/outils/temoin_du_rendu.sh"'
  chk "le corpus est un parametre" 'grep -q "CORPUS:?" "$ROOT/src/outils/temoin_du_rendu.sh"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

CORPUS="${CORPUS:?CORPUS requis — le balayage du corpus publie}"
COUCHES="${COUCHES:-109}"
FENETRE_PILE="${FENETRE_PILE:-161}"
DEST="${DEST:-$ROOT/data/temoin_rendu/rendus}"
JSON="${JSON:-$ROOT/docs/temoin_du_rendu.json}"
[ $# -ge 1 ] || { echo "donner au moins un morceau tifxyz" >&2; exit 2; }

PILES=""
for M in "$@"; do
  [ -f "$M/meta.json" ] || { echo "  ⚠ $M : pas un tifxyz" >&2; continue; }
  NOM=$(basename "$M")
  W="$DEST/$NOM"
  PILE="$W/g0_n${FENETRE_PILE}/rendu"
  if [ ! -d "$PILE" ]; then
    echo "== rendu de $NOM (publie) avec notre chaine"
    GARDER_RENDU=1 PLAT="$M" DEST="$W" ETIQUETTE="publie_$NOM" \
      FENETRES_BASE="$FENETRE_PILE" JSON="$W/convergence.json" \
      "$ROOT/src/outils/profiler_une_surface.sh" || echo "  ⚠ $NOM : rendu abandonné"
  else
    echo "== $NOM : pile déjà rendue"
  fi
  [ -d "$PILE" ] && PILES="$PILES $PILE"
done
[ -n "$PILES" ] || { echo "aucune pile rendue" >&2; exit 3; }

echo
echo "== les morceaux PUBLIES, relus a la geometrie du corpus"
CORPUS="$CORPUS" COUCHES="$COUCHES" "$ROOT/src/outils/situer_nos_traces.sh" $PILES \
  | tee "$JSON.txt"
echo
echo "⚠ a comparer a la distribution du corpus (docs/calibration_scroll1.json) et a nos"
echo "  candidats (docs/situer_nos_traces.json) — le critere est en tete de ce fichier."
