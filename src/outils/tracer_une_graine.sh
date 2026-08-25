#!/usr/bin/env bash
# Tracer UNE graine, la rendre a plusieurs profondeurs, et juger sa convergence.
#
# ⚠⚠ Ce fichier existe parce qu une SECONDE campagne en avait besoin. Le corps etait inline
# dans tracer_tous_candidats.sh, et plafond_generations.sh allait le recopier -- c est-a-dire
# creer deux definitions de « tracer une graine » libres de diverger sur le pas de tranche,
# le recadrage ou la couche tracee. Deux traces qu on compare doivent avoir ete faites
# pareil, sinon la comparaison mesure la difference des scripts.
#
# ⚠ Le volume et la taille de voxel sont passes par l ENVIRONNEMENT quand l appelant les
# connait deja : une campagne de huit graines qui les redemanderait a S3 huit fois paierait
# huit fois, et surtout pourrait tomber sur deux reponses differentes en cours de route.
#
# ⚠ Sortie 3 = refus (on ne sait pas quoi tracer), sortie 4 = la graine n a rien fait
# pousser. Le second n est PAS une panne : une graine posee dans du vide est un resultat.
#
# Usage : PREDICTION=ps256 DEST=/abs/dir src/outils/tracer_une_graine.sh <x> <y> <z>
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# ⚠⚠ Le traceur est INJECTABLE, et c est une prise de test assumee -- meme raison que
# `rendre_surveille.sh` : un garde qu on ne peut exercer qu en lancant une vraie trace de deux
# heures n est pas exerce. Sans ca, seul le chemin de REFUS etait testable, donc la batterie
# ne verifiait jamais qu une graine VALIDE passe -- et un garde qui refuse tout est aussi
# inutile qu un garde qui n existe pas. La valeur par defaut reste le vrai traceur.
TRACEUR=${TRACEUR:-vc_grow_seg_from_seed}

B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
S="PHercParis4/representations/predictions/surfaces"
declare -A PRED=(
  [ps256]="$S/20260411134726-surface-20260413141734-surface-recto-2um-ps256-L0-th0.45.zarr"
  [m7]="$S/20260411134726-surface-20260413222639-surface-m7-L2-th0.2.zarr"
)

# ⚠⚠ LE NIVEAU DE PYRAMIDE EST ECRIT DANS LE NOM DE LA PREDICTION, et personne ne le lisait :
# `...-recto-2um-ps256-L0-th0.45.zarr` contre `...-m7-L2-th0.2.zarr`. Une graine donnee pour
# une prediction L2 est une coordonnee L2 ; la meme suite de chiffres, lue dans le volume
# scanne, designe un point QUATRE FOIS plus proche de l origine -- dans le vide. C est ce qui
# a produit treize rendus entierement noirs, et le renseignement etait dans l URL que ce
# script tient deja.
#
# ⚠ Un nom sans `-L<n>-` est REFUSE et pas defaute a zero : defauter ferait exactement
# l erreur qu on repare, en silence.
niveau_de_prediction() {
  printf '%s' "$1" | grep -oE -- '-L[0-9]+-' | head -1 | tr -dc '0-9'
}

resoudre_volume() {
  local scan="$1"
  curl -s --max-time 60 "$B/?list-type=2&prefix=PHercParis4/volumes/$scan&delimiter=/" \
    | tr '<' '\n' | grep "^Prefix>" | sed 's|^Prefix>||' | grep '\.zarr/$' | sed 's|/$||'
}

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "les deux predictions sont declarees" '[ -n "${PRED[ps256]:-}" ] && [ -n "${PRED[m7]:-}" ]'
  chk "les deux pointent vers des zarr distincts" '[ "${PRED[ps256]}" != "${PRED[m7]}" ]'
  # ⚠ Une prediction inconnue doit etre REFUSEE et pas defauter : defauter tracerait une
  # autre surface que celle demandee, et le resultat porterait le mauvais nom.
  out=$(PREDICTION=inexistante DEST=/tmp/x "$ROOT/src/outils/tracer_une_graine.sh" 1 2 3 2>&1); rc=$?
  chk "une prediction inconnue est refusee (3)" '[ "$rc" = 3 ]'
  chk "... et le refus la nomme" 'printf "%s" "$out" | grep -q inexistante'
  out=$(PREDICTION=ps256 "$ROOT/src/outils/tracer_une_graine.sh" 1 2 3 2>&1); rc=$?
  chk "sans DEST, refus (3)" '[ "$rc" = 3 ]'
  # ⚠⚠ Un DEST relatif est refuse : depth_profile tourne depuis inference_xpu, donc un
  # chemin relatif y designerait un AUTRE dossier. Piege deja paye une fois.
  out=$(PREDICTION=ps256 DEST=relatif/ici "$ROOT/src/outils/tracer_une_graine.sh" 1 2 3 2>&1); rc=$?
  chk "un DEST relatif est refuse (3)" '[ "$rc" = 3 ]'
  chk "... et le refus dit pourquoi" 'printf "%s" "$out" | grep -qi absolu'
  out=$(PREDICTION=ps256 DEST=/tmp/x "$ROOT/src/outils/tracer_une_graine.sh" 1 2 2>&1); rc=$?
  chk "trois coordonnees exigees" '[ "$rc" = 3 ]'
  # ⚠⚠ Le niveau lu dans le nom de la prediction : c est le renseignement qui manquait.
  chk "ps256 est lue au niveau 0" '[ "$(niveau_de_prediction "${PRED[ps256]}")" = 0 ]'
  chk "m7 est lue au niveau 2" '[ "$(niveau_de_prediction "${PRED[m7]}")" = 2 ]'
  chk "une URL sans -L<n>- ne rend rien" '[ -z "$(niveau_de_prediction "sans-niveau.zarr")" ]'
  # ⚠ Le facteur, qui est ce qui transforme une coordonnee de prediction en coordonnee de scan.
  chk "le niveau 2 vaut un facteur 4" '[ "$((1 << 2))" = 4 ]'
  chk "le niveau 0 ne change rien" '[ "$((1 << 0))" = 1 ]'
  # ⚠⚠ La sonde doit passer AVANT le trace, sinon elle ne sert a rien : on aurait deja paye.
  L_SONDE=$(grep -n "sonde de graine : prédiction" "$ROOT/src/outils/tracer_une_graine.sh" | cut -d: -f1 | head -1)
  # ⚠⚠ Le motif vise l INVOCATION, pas le nom du binaire : depuis que le traceur est
  # injectable, son nom apparait aussi dans la valeur par defaut, tout en haut du fichier --
  # donc chercher le nom faisait croire que le trace precede la sonde. Ce controle a attrape
  # sa propre fragilite a la seconde ou elle est apparue.
  L_TRACE=$(grep -n 'timeout 7200 "\$TRACEUR"' "$ROOT/src/outils/tracer_une_graine.sh" | cut -d: -f1 | head -1)
  chk "la sonde de graine passe AVANT le tracé" \
      '[ -n "$L_SONDE" ] && [ -n "$L_TRACE" ] && [ "$L_SONDE" -lt "$L_TRACE" ]'
  # ⚠⚠ LE CHEMIN QUI PASSE, exerce avec un faux traceur : sans ce controle la batterie ne
  # verifiait que le REFUS, et un garde qui refuse tout est aussi inutile qu un garde absent.
  T_OK=$(mktemp -d)
  out=$(PREDICTION=ps256 DEST="$T_OK" TRACEUR=true \
        VOL="PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr" UM=2.4 \
        timeout 300 "$ROOT/src/outils/tracer_une_graine.sh" 10752 10616 38740 2>&1); rc=$?
  chk "une graine VALIDE passe la sonde" '[ "$rc" != 5 ]'
  chk "... et la sonde a bien trouvé de la matière" \
      'printf "%s" "$out" | grep -q "valeur au point"'
  # ⚠ Et le hors-ligne : SANS_SONDE saute la sonde sans rien changer d autre.
  out=$(PREDICTION=m7 DEST="$T_OK/b" TRACEUR=true SANS_SONDE=1 \
        VOL="PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr" UM=2.4 \
        timeout 300 "$ROOT/src/outils/tracer_une_graine.sh" 2924 5324 9260 2>&1); rc=$?
  chk "SANS_SONDE saute la sonde" '[ "$rc" != 5 ]'
  chk "... et la sonde ne tourne alors PAS" \
      '! printf "%s" "$out" | grep -q "sonde de graine"'
  # ⚠⚠ Et le refus, exerce lui aussi de bout en bout : la graine m7 designe un bloc absent.
  out=$(PREDICTION=m7 DEST="$T_OK/c" TRACEUR=true \
        VOL="PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr" UM=2.4 \
        timeout 300 "$ROOT/src/outils/tracer_une_graine.sh" 2924 5324 9260 2>&1); rc=$?
  chk "la graine m7 est refusee (5)" '[ "$rc" = 5 ]'
  chk "... et le refus dit ce qui manque" 'printf "%s" "$out" | grep -q "aucune matière scannée"'
  rm -rf "$T_OK"
  # ⚠⚠ Le rebasage : sonder la graine ne suffit pas, le maillage sort dans le repere de la
  # prediction. Les deux moities du meme defaut, et la seconde a ete demontree EN PRODUCTION.
  chk "le maillage est rebasé quand la prédiction n est pas au niveau 0" \
      'grep -q "rebaser" "$ROOT/src/outils/tracer_une_graine.sh"'
  chk "... et le rendu suit le niveau de la prédiction" \
      'grep -q -- "-g \"\$NIVEAU_RENDU\"" "$ROOT/src/outils/tracer_une_graine.sh"'
  chk "... et le voxel du profil aussi" \
      'grep -q "2\*\*\$NIVEAU_RENDU" "$ROOT/src/outils/tracer_une_graine.sh"'
  # ⚠ Le facteur du rebasage est 2^niveau, pas le niveau.
  chk "le niveau 2 rebase par 4" '[ "$((1 << 2))" = 4 ]'
  # ⚠⚠ Le voxel ecrit dans seed.json suit le niveau de la PREDICTION : sinon `min_area_cm`
  # et l aire rapportee sont fausses d un facteur 2^(2n) -- seize au niveau 2.
  chk "le voxel du seed suit le niveau" \
      'grep -q "UM_PRED=\$(python3 -c \"print(\$UM \* 2\*\*\$NIV)\")" "$ROOT/src/outils/tracer_une_graine.sh"'
  chk "... et c est UM_PRED qui est passe au gabarit" \
      'grep -q "\"\$UM_PRED\" \"\$GENERATIONS\"" "$ROOT/src/outils/tracer_une_graine.sh"'
  chk "le niveau 2 quadruple le voxel" '[ "$(python3 -c "print(2.4 * 2**2)")" = 9.6 ]'
  chk "... donc seize fois l aire" '[ "$(python3 -c "print((2**2)**2)")" = 16 ]'
  chk "et une sortie propre existe pour le hors-ligne" \
      'grep -q "SANS_SONDE" "$ROOT/src/outils/tracer_une_graine.sh"'
  chk "le script est appele par au moins une campagne" \
      'grep -lq tracer_une_graine.sh "$ROOT"/src/outils/*.sh'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

# ⚠ Un refus sort en 3, jamais en 1 : ${X:?} sortirait en 1, indistinguable
# d une panne, et un appelant qui trie les deux lirait le mauvais cas.
NOM="${PREDICTION:-}"
[ -n "$NOM" ] || { echo "refus : PREDICTION (ps256 ou m7) requis" >&2; exit 3; }
[ -n "${PRED[$NOM]:-}" ] || { echo "refus : prédiction inconnue « $NOM »" >&2; exit 3; }
DEST="${DEST:-}"
[ -n "$DEST" ] || { echo "refus : DEST requis" >&2; exit 3; }
case "$DEST" in /*) ;; *) echo "refus : DEST doit être ABSOLU (depth_profile tourne depuis inference_xpu)" >&2; exit 3;; esac
[ $# -ge 3 ] || { echo "refus : trois coordonnées attendues" >&2; exit 3; }
X="$1"; Y="$2"; Z="$3"
GENERATIONS="${GENERATIONS:-60}"
FENETRES="${FENETRES:-41 161}"
PATIENCE="${PATIENCE:-420}"
ETIQUETTE="${ETIQUETTE:-$(basename "$DEST")}"
JSON="${JSON:-$ROOT/docs/trace_${ETIQUETTE}.json}"

if [ -z "${VOL:-}" ] || [ -z "${UM:-}" ]; then
  SCAN=$(basename "${PRED[ps256]}" | cut -d- -f1)
  VOL=$(resoudre_volume "$SCAN")
  UM=$(printf '%s' "$VOL" | grep -oE '[0-9]+\.[0-9]+um' | head -1 | sed 's/um$//')
fi
[ -n "${VOL:-}" ] && [ -n "${UM:-}" ] || { echo "refus : volume introuvable" >&2; exit 3; }

# ⚠⚠ LA SONDE DE GRAINE, ET ELLE PASSE AVANT TOUT. Une trace coute des heures, un bloc zarr
# coute une requete. Le 2026-08-24 : la graine `m7` designe un bloc que le depot n a jamais
# ecrit, et treize rendus entierement noirs en sont sortis -- pendant que le traceur imprimait
# `value is 0` puis `empty space tracing` et poussait quand meme. Il imprime la meme chose sur
# les graines qui MARCHENT, donc cette ligne ne discrimine rien ; ce qui discrimine est « y
# a-t-il de la matiere scannee la », et rien ne posait la question.
NIV=$(niveau_de_prediction "${PRED[$NOM]}")
[ -n "$NIV" ] || { echo "refus : impossible de lire le niveau (-L<n>-) dans « ${PRED[$NOM]} »" >&2; exit 3; }
if [ "${SANS_SONDE:-0}" != 1 ]; then
  # ⚠ La graine est donnee dans le repere de la PREDICTION ; le volume scanne est au niveau 0.
  F=$((1 << NIV))
  SX=$((X * F)); SY=$((Y * F)); SZ=$((Z * F))
  echo "== sonde de graine : prédiction $NOM (niveau $NIV) → scan ($SZ, $SY, $SX)"
  if ! uv run --project "$ROOT" python "$ROOT/src/nappe/matiere_au_point.py" \
       --point "$SZ" "$SY" "$SX" --niveau 0 --volume "$VOL" 2>&1 | tee /dev/stderr \
       | grep -q "valeur au point"; then
    echo "   ⚠⚠ refus : cette graine ne désigne aucune matière scannée. Tracer ici produirait" >&2
    echo "      une surface dans le vide, et son rendu serait entièrement noir." >&2
    echo "      Pour passer outre (hors ligne, ou graine volontairement dans le vide) :" >&2
    echo "      SANS_SONDE=1" >&2
    exit 5
  fi
fi

mkdir -p "$DEST"
# ⚠⚠ LE VOXEL ECRIT DANS seed.json EST CELUI DE LA PREDICTION, PAS CELUI DU SCAN. Le traceur
# s en sert pour convertir son aire en cm² ET pour appliquer `min_area_cm`. Une prediction L2
# a des voxels QUATRE fois plus gros, donc y ecrire 2,4 µm sous-estime chaque longueur d un
# facteur 4 et chaque aire d un facteur SEIZE.
#
# Mesure du 2026-08-24, sur deux maillages de meme grille (120 x 119, ~13 777 points valides) :
#   ps256 (L0) : pas de grille 48 µm  -> aire annoncee 0,317 cm², aire REELLE 0,317 cm²
#   m7    (L2) : pas de grille 192 µm -> aire annoncee 0,317 cm², aire REELLE 5,079 cm²
# Les deux se sont arretees au meme nombre de points parce que `min_area_cm: 0.3` etait
# evalue dans deux unites differentes. Toute comparaison d aire entre les deux familles de
# prediction de ce depot est donc fausse d un facteur 16 -- y compris le tableau de `48` qui
# annonce « 0,317 cm² » des deux cotes et ressemblait a une comparaison controlee.
UM_PRED=$(python3 -c "print($UM * 2**$NIV)")
[ -s "$DEST/seed.json" ] || python3 - "$ROOT/artefacts/PHerc0358/seed.json" "$DEST/seed.json" \
    "$UM_PRED" "$GENERATIONS" <<'PY'
import json, sys
src, dst, um, gen = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
d = json.load(open(src)); d["voxelsize"] = um; d["generations"] = gen
json.dump(d, open(dst, "w"), indent=2)
PY

M=$(ls -d "$DEST"/auto_grown_* 2>/dev/null | head -1)
if [ -z "$M" ]; then
  ( cd "$DEST" && timeout 7200 "$TRACEUR" -v "$B/${PRED[$NOM]}" -t . \
      -p seed.json -s "$X" "$Y" "$Z" ) > "$DEST/trace.log" 2>&1
  M=$(ls -d "$DEST"/auto_grown_* 2>/dev/null | head -1)
fi
# ⚠⚠ « aucune surface » est un RESULTAT sur cette graine, pas une panne du script.
[ -n "$M" ] || { echo "   ⚠ aucune surface — résultat sur cette graine"; exit 4; }
AIRE=$(grep -oE 'generated surface .* \(([0-9.]+) cm\^2\)' "$DEST/trace.log" \
       | grep -oE '\(([0-9.]+)' | tr -d '(' | tail -1)
[ -d "$DEST/plat" ] || vc_flatten -i "$M" -o "$DEST/plat" > "$DEST/flatten.log" 2>&1

# ⚠⚠ LE MAILLAGE SORT DANS LE REPERE DE LA PREDICTION, ET LE RENDU LIT LE SCAN. Sonder la
# graine ne suffit pas -- c est la MOITIE du defaut. Demontre en production le 2026-08-24 :
# une graine `m7` valide, sondee et acceptee, a quand meme produit un rendu entierement noir,
# parce que son maillage sort a z ~ 9 100 (repere L2) alors que le rouleau est a z ~ 30 000
# dans le scan. Le refus de `depth_profile` l a attrape immediatement, ce qui est exactement
# ce pour quoi il a ete ecrit.
#
# ⚠ Le rendu se fait alors AU NIVEAU DE LA PREDICTION : un maillage L2 a une resolution L2,
# donc le rendre a 2,4 µm interpolerait quatre fois entre deux points de grille -- on paierait
# seize fois le calcul sans gagner un bit d information.
PLAT="$DEST/plat"
NIVEAU_RENDU=0
if [ "$NIV" -gt 0 ]; then
  if [ ! -d "$DEST/plat_niveau0" ]; then
    uv run --project "$ROOT" python "$ROOT/src/nappe/niveau_du_maillage.py" \
        --maillage "$DEST/plat" --rebaser "$DEST/plat_niveau0" --facteur "$((1 << NIV))" \
        > "$DEST/rebase.log" 2>&1 || { echo "   ⚠ rebasage échoué" >&2; exit 6; }
  fi
  PLAT="$DEST/plat_niveau0"
  NIVEAU_RENDU="$NIV"
  echo "   maillage rebasé ×$((1 << NIV)) — rendu au niveau $NIV (voxel $(python3 -c "print($UM * 2**$NIV)") µm)"
fi

PROFILS=""
for F in $FENETRES; do
  OUT="$DEST/profil_${F}c.json"
  if [ ! -s "$OUT" ]; then
    rm -rf "$DEST/rendu_$F"
    "$ROOT/src/outils/rendre_surveille.sh" "$DEST/rendu_$F" "$PATIENCE" -- \
        -v "$DEST/cache" --remote-url "$B/$VOL" --scale 1 -g "$NIVEAU_RENDU" -s "$PLAT" \
        --tif-output "$DEST/rendu_$F" -n "$F" --slice-step 1 --auto-crop \
        > "$DEST/rendu_$F.log" 2>&1 || { echo "   ⚠ rendu $F abandonné"; continue; }
    ( cd "$ROOT/inference_xpu" && uv run python ../src/volume/depth_profile.py \
        "$DEST/rendu_$F" --grid --step 200 --traced-layer $((F / 2)) \
        --voxel-um "$(python3 -c "print($UM * 2**$NIVEAU_RENDU)")" \
        --out "$OUT" ) > "$DEST/profil_$F.log" 2>&1 || { echo "   ⚠ profil $F échoué"; continue; }
  fi
  PROFILS="$PROFILS --profil $OUT"
done
rm -rf "$DEST/cache"
echo "   aire ${AIRE:-?} cm²"
[ -n "$PROFILS" ] && ( cd "$ROOT/experiments" && uv run python \
    ../src/commun/test_convergence.py $PROFILS --nom "$ETIQUETTE" --json "$JSON" | tail -4 )
