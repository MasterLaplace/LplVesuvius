#!/usr/bin/env bash
# ENCHAINER la projection tangentielle, et comparer au saut direct de meme longueur.
#
# ⚠⚠ C EST LA QUESTION QUE LA CHAINE TANGENTIELLE POSE, et une projection unique n y repond
# pas. `44` mesure qu une nappe projetee reste sur sa feuille jusqu a ~380 µm et y est le mieux
# posee vers 240. Reste a savoir si on peut RECOMMENCER depuis la projection : une chaine n est
# utile que si l erreur ne s accumule pas plus vite qu on n avance.
#
# ⭐ Le pouvoir de la comparaison vient du TEMOIN : la meme distance totale, franchie d un
# seul bond. Si l enchainement tient la ou le bond direct casse, la chaine gagne quelque chose
# que la projection seule n a pas -- et si les deux se valent, l enchainement ne sert a rien et
# il vaut mieux le savoir avant de l ecrire.
#
# ⚠ La projection est DELEGUEE, et elle compose parce qu elle lit un tifxyz et en ecrit un.
# C est la seule raison pour laquelle ce fichier peut etre court.
#
# Usage : SOURCE=<tifxyz> PAS=5 MAILLONS=5 DEST=<dir> tools/chainer_tangentiel.sh
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "la projection est deleguee" \
      'grep -q "projeter_tangentiel.py" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "le profil est delegue" \
      'grep -q "profiler_une_surface.sh" "$ROOT/tools/chainer_tangentiel.sh"'
  MOTEUR="vc_render""_tifxyz"
  chk "le moteur n est PAS invoque ici" \
      '! grep -q "$MOTEUR" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ LE TEMOIN EST LA MOITIE DE L EXPERIENCE. Sans le saut direct de meme longueur, un
  # enchainement qui tient ne prouve rien : il pourrait tenir parce que la distance totale est
  # courte, et non parce que l enchainement aide.
  chk "le saut direct de meme longueur est calcule" \
      'grep -q "DIRECT=" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "... et il vaut pas x maillons" \
      'grep -q "PAS \* MAILLONS" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠ Chaque maillon part de la SORTIE du precedent : c est ce qui fait une chaine plutot
  # qu une serie de projections independantes depuis la meme source.
  chk "chaque maillon part du precedent" \
      'grep -q "COURANT=" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ Aucun provisoire dans `docs/`. Le motif est compose a l execution, sinon cette ligne
  # contiendrait ce qu elle interdit -- piege paye trois fois dans ce depot.
  INTERDIT="JSON"".brouillon"
  chk "aucun fichier provisoire dans docs/" \
      '! grep -q "$INTERDIT" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "... le provisoire passe par mktemp" \
      'grep -q "TMP=\$(mktemp)" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "SOURCE est un parametre" 'grep -q "SOURCE:?" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ La geometrie est mesuree AVANT les profils, et sans eux. Un pas qui derive refute une
  # chaine pour zero rendu ; payer deux rendus pour l apprendre serait payer pour rien.
  chk "la geometrie est mesuree sans rendu" \
      'grep -q -- "--croissance" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "... et elle precede les profils" \
      '[ "$(grep -n -- "--croissance" "$ROOT/tools/chainer_tangentiel.sh" | head -1 | cut -d: -f1)" \
        -lt "$(grep -n "profiler_une_surface.sh" "$ROOT/tools/chainer_tangentiel.sh" | tail -1 | cut -d: -f1)" ]'
  chk "PROFILS=0 permet de s arreter la" \
      'grep -q "PROFILS:-1" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ La chaine CORRIGEE : projeter puis reposer sur la matiere avant de repartir.
  # Sans le recalage, la chaine est purement geometrique et son horizon est mesure a 580 µm.
  chk "RECALER=1 existe" 'grep -q "RECALER:-0" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "... et delegue le recalage" \
      'grep -q "recaler_sur_la_matiere.py" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠ Le niveau de pyramide n a PAS de defaut : une coordonnee de niveau 2 lue au niveau 0
  # designe un point quatre fois plus proche de l origine, dans le vide (`54`).
  chk "... en exigeant le niveau" 'grep -q "NIVEAU:?" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "... et la boite" 'grep -q "ZARR:?" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ Le maillon RECALE est ce qui alimente le suivant, sinon la correction serait
  # ecrite puis jetee et la chaine resterait geometrique en ayant l air corrigee.
  chk "... et le maillon recale alimente le suivant" \
      'grep -q "CIBLE=\"\$DEST/projete_" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ PAS_VOX casse la retroaction : un pas de GRILLE couvre `pas x longueur de
  # tangente`, donc un maillage etire s envoie lui-meme plus loin au coup suivant. Mesure sur
  # vingt maillons de « 95 µm » : le pas reel va jusqu a 650.
  chk "PAS_VOX existe" 'grep -q "PAS_VOX:-" "$ROOT/tools/chainer_tangentiel.sh"'
  chk "... et il est passe a la projection" \
      'grep -q -- "--pas-vox" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠ Le temoin suit la MEME unite que la chaine, sinon on compare deux longueurs
  # differentes en croyant comparer deux methodes.
  chk "... et le temoin suit la meme unite" \
      'grep -q "ARG_DIRECT=(--pas-vox" "$ROOT/tools/chainer_tangentiel.sh"'
  # ⚠⚠ Un temoin PERIME est un temoin qui ment : la campagne est reprenable, donc la
  # relancer avec PLUS de maillons laisserait le bond direct de l ANCIENNE longueur se comparer
  # a une chaine qui va desormais plus loin, sans que rien dans le tableau ne le dise.
  chk "un temoin perime est refait" \
      'grep -q "temoin perime" "$ROOT/tools/chainer_tangentiel.sh"'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

SOURCE="${SOURCE:?SOURCE requis — un tifxyz dont on sait qu il suit une feuille}"
PAS="${PAS:-5}"
MAILLONS="${MAILLONS:-5}"
DEST="${DEST:-$ROOT/data/chaine_tangentielle}"
JSON="${JSON:-$ROOT/docs/chaine_tangentielle.json}"
FENETRES="${FENETRES:-41}"
UM_BASE="${UM_BASE:-2.4}"
# ⚠⚠ PAS_VOX : un pas FIXE en voxels, qui casse la retroaction d une chaine. Un pas de
# GRILLE couvre `pas x longueur moyenne de tangente`, donc un maillage qui cisaille s envoie
# lui-meme plus loin au coup suivant : mesure sur vingt maillons de « 95 µm », le pas reel va
# 95 · 96 · 97 · 101 · 110 · 127 · 159 · 223 · 360 · 650. Avec PAS_VOX la distance ne depend
# plus du maillage.
# ⚠ Le TEMOIN suit la meme unite que la chaine, sinon on comparerait deux longueurs
# differentes en croyant comparer deux methodes.
PAS_VOX="${PAS_VOX:-}"
if [ -n "$PAS_VOX" ]; then
  ARG_PAS=(--pas-vox "$PAS_VOX")
  ARG_DIRECT=(--pas-vox "$(python3 -c "print($PAS_VOX * $MAILLONS)")")
  DIRECT="${PAS_VOX}vox x $MAILLONS"
else
  ARG_PAS=(--pas "$PAS")
  ARG_DIRECT=(--pas "$((PAS * MAILLONS))")
  DIRECT=$((PAS * MAILLONS))
fi

mkdir -p "$DEST"
if [ -n "$PAS_VOX" ]; then
  echo "== chaîne : $MAILLONS maillons de $PAS_VOX voxels FIXES  ·  témoin : un bond direct de $DIRECT"
else
  echo "== chaîne : $MAILLONS maillons de $PAS pas  ·  témoin : un bond direct de $DIRECT pas"
fi

# ⚠⚠ RECALER=1 : la chaine CORRIGEE. Chaque maillon est reprojete puis **repose sur la
# matiere** avant de servir de source au suivant. C est le geste que `44` nomme comme le seul
# qui puisse depasser l horizon geometrique de 580 µm, et que `41` §6 mesure deja sur une
# ligne (2,4 mm, arretee parce que le bloc se termine).
# ⚠ Le maillon recale REMPLACE le maillon projete dans la chaine, dans son propre DEST : la
# chaine pure garde le sien, donc les deux restent comparables ligne a ligne. Melanger les deux
# dans un meme dossier rendrait impossible de dire lequel a produit un chiffre.
RECALER="${RECALER:-0}"
if [ "$RECALER" = 1 ]; then
  : "${ZARR:?RECALER=1 exige ZARR — une boite de prediction locale}"
  : "${NIVEAU:?RECALER=1 exige NIVEAU — celui de la boite, jamais defaute}"
fi
PORTEE="${PORTEE:-4}"
SPIRE="${SPIRE:-173}"

COURANT="$SOURCE"
for M in $(seq 1 "$MAILLONS"); do
  D="$DEST/maillon_$M"
  if [ ! -f "$D/meta.json" ]; then
    CIBLE="$D"
    [ "$RECALER" = 1 ] && CIBLE="$DEST/projete_$M"
    uv run --project "$ROOT" python "$ROOT/analysis/src/projeter_tangentiel.py" \
        "$COURANT" --dest "$CIBLE" "${ARG_PAS[@]}" > "$D.log" 2>&1 \
      || { echo "   ⚠ maillon $M échoué — la chaîne s arrête là" >&2; break; }
    if [ "$RECALER" = 1 ]; then
      uv run --project "$ROOT" python "$ROOT/analysis/src/recaler_sur_la_matiere.py" \
          "$CIBLE" --zarr "$ZARR" --niveau "$NIVEAU" --portee "$PORTEE" --spire-um "$SPIRE" \
          --dest "$D" >> "$D.log" 2>&1 \
        || { echo "   ⚠ recalage du maillon $M échoué — la chaîne s arrête là" >&2; break; }
    fi
  fi
  # ⚠⚠ LE MAILLON SUIVANT PART D ICI. Repartir de `$SOURCE` a chaque fois donnerait des
  # projections independantes de longueurs croissantes, c est-a-dire l experience deja faite,
  # sous un autre nom.
  COURANT="$D"
  echo "   maillon $M → $(basename "$D")"
done

# ⚠⚠ UN TEMOIN PERIME EST UN TEMOIN QUI MENT. La campagne est reprenable — elle saute les
# maillons deja calcules — mais si on la relance avec PLUS de maillons, le bond direct deja
# ecrit couvre l ANCIENNE longueur et se compare a une chaine qui va desormais plus loin.
# Rien dans le tableau ne le dirait. On verifie donc que le temoin porte bien la longueur
# demandee, et on le refait sinon.
if [ -f "$DEST/direct/meta.json" ] && [ -n "$PAS_VOX" ]; then
  ATTENDU=$(python3 -c "print(round($PAS_VOX * $MAILLONS, 3))")
  TROUVE=$(python3 -c "
import json; print(round(float(json.load(open('$DEST/direct/meta.json')).get('pas_voxels', 0)), 3))")
  if [ "$ATTENDU" != "$TROUVE" ]; then
    echo "   ⚠ temoin perime ($TROUVE voxels au lieu de $ATTENDU) - refait" >&2
    rm -rf "$DEST/direct"
  fi
fi

if [ ! -f "$DEST/direct/meta.json" ]; then
  uv run --project "$ROOT" python "$ROOT/analysis/src/projeter_tangentiel.py" \
      "$SOURCE" --dest "$DEST/direct" "${ARG_DIRECT[@]}" > "$DEST/direct.log" 2>&1 \
    || echo "   ⚠ témoin direct échoué" >&2
fi

# ⚠⚠ PROFILS=0 : enchainer et ne mesurer que la GEOMETRIE. Le pas reellement parcouru et le
# volume englobant se lisent dans les `meta.json`, donc ils coutent zero rendu -- et un pas qui
# derive suffit a REFUTER une chaine. Une chaine longue se sonde donc d abord comme ca, et on ne
# paie les rendus que si la geometrie a tenu.
# ⚠ Necessaire, pas suffisant : une chaine peut garder un pas parfait en marchant droit hors de
# sa feuille. Cette voie ne peut que refuter, et c est precisement ce qui la rend bon marche.
uv run --project "$ROOT" python "$ROOT/analysis/src/projeter_tangentiel.py" --croissance \
    "$SOURCE" $(for M in $(seq 1 "$MAILLONS"); do
        [ -f "$DEST/maillon_$M/meta.json" ] && printf '%s ' "$DEST/maillon_$M"; done) \
    $([ -f "$DEST/direct/meta.json" ] && printf '%s' "$DEST/direct") \
    --json "${CROISSANCE:-${JSON%.json}_croissance.json}"

if [ "${PROFILS:-1}" = 0 ]; then
  echo "PROFILS=0 — geometrie seule, aucun rendu"
  exit 0
fi

printf '\n%-14s %10s %12s %12s\n' "surface" "µm" "amplitude" "pic au bord"
# ⚠⚠ Le provisoire passe par `mktemp`, PAS par un suffixe dans `docs/`. Je viens d ecrire ce
# defaut une seconde fois, dans un fichier neuf, une heure apres l avoir repare ailleurs : un
# repertoire de resultats ne doit contenir que des resultats, et une campagne interrompue y
# laisserait un JSON a moitie ecrit.
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
echo "[" > "$TMP"
PREMIER=1
for NOM in "$SOURCE" "$COURANT" "$DEST/direct"; do
  [ -f "$NOM/meta.json" ] || continue
  ETQ=$(basename "$NOM")
  W="$DEST/profil_$ETQ"
  if [ ! -s "$W/g0_n$FENETRES/profil.json" ]; then
    GARDER_RENDU=0 PLAT="$NOM" NIVEAU=0 FENETRES_BASE="$FENETRES" UM_BASE="$UM_BASE" \
      DEST="$W" ETIQUETTE="chaine_$ETQ" JSON="$W/verdict.json" \
      "$ROOT/tools/profiler_une_surface.sh" > "$W.log" 2>&1 \
      || { echo "   ⚠ profil de $ETQ abandonné"; continue; }
  fi
  L=$(python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))[0]
m = json.load(open(sys.argv[2]))
print(round(m.get('pas_voxels', 0.0) * $UM_BASE, 1), round(d['amplitude_mediane'], 4),
      round(d['au_bord_intensite'], 3))" "$W/g0_n$FENETRES/profil.json" "$NOM/meta.json" 2>/dev/null)
  set -- $L
  printf '%-14s %10s %12s %12s\n' "$ETQ" "${1:-?}" "${2:-?}" "${3:-?}"
  [ "$PREMIER" = 1 ] || echo "," >> "$TMP"
  PREMIER=0
  printf '{"surface": "%s", "um": %s, "amplitude": %s, "au_bord": %s}' \
      "$ETQ" "${1:-0}" "${2:-0}" "${3:-0}" >> "$TMP"
done
echo "]" >> "$TMP"
mv "$TMP" "$JSON"
echo "écrit : $JSON"
