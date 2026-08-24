#!/usr/bin/env bash
# Rendre une surface DEJA aplatie a plusieurs profondeurs, et juger sa convergence.
#
# ⚠⚠ Ce fichier existe parce que TROIS appelants en avaient besoin et que deux l avaient
# deja recopie : tracer_une_graine.sh (qui trace puis profile), controle_resolution.sh (qui
# profile une surface existante a deux niveaux de pyramide) et la campagne du plafond. Deux
# profils qu on COMPARE doivent avoir ete faits pareil -- pas de tranche, recadrage, couche
# tracee -- sinon la comparaison mesure la difference des scripts.
#
# ⚠⚠ LE PIEGE D UNITES, en un seul endroit. Au niveau g de la pyramide un voxel fait 2^g
# fois le voxel de base, donc UNE TRANCHE COUVRE 2^g fois plus d epaisseur. Rendre 41
# tranches au niveau 1 couvre DEUX FOIS la profondeur physique de 41 tranches au niveau 0 :
# on comparerait deux fenetres differentes en croyant comparer deux resolutions. Le nombre
# de tranches est donc DIVISE par 2^g et --voxel-um MULTIPLIE par 2^g.
#
# Usage : PLAT=<dir> NIVEAU=1 JSON=<out> tools/profiler_une_surface.sh
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ⚠ La conversion est une FONCTION, appelee par tout le monde, et non un calcul recopie.
#
# ⚠⚠ L arrondi est « au superieur a la moitie » (int(x+0.5)) et PAS round(). Deux raisons,
# et la seconde est la vraie :
#   - round() en Python arrondit au PAIR : round(41/2) rend 20, pas 21. Un lecteur qui
#     verifie a la main obtient 21 et croit a un bug.
#   - une fenetre est CENTREE sur sa couche tracee (--traced-layer N/2), donc elle doit
#     rester IMPAIRE : 41 -> 21 -> 11 garde un centre, 41 -> 20 n en a pas. Une fenetre
#     paire decale le centre d une demi-tranche a chaque niveau, silencieusement.
# ⚠⚠ LE PLANCHER DE LA PYRAMIDE, et il depend de la SURFACE, pas de la machine.
# `depth_profile` analyse par fenetres carrees de 1024 px et REFUSE une image plus petite --
# refus correct, retrecir la fenetre mesurerait autre chose. Donc plus la surface est
# petite, moins on peut regarder grossier : mesure, 2361 px tiennent jusqu au niveau 1,
# 8000 px jusqu au niveau 2.
#
# ⚠ Le controle passe AVANT le rendu. Sans lui on paie un calcul entier pour recevoir le
# refus a la derniere etape -- ce qui vient d arriver deux fois, sur les fenetres 10 et 40.
FENETRE_ANALYSE=${FENETRE_ANALYSE:-1024}

tranches_au_niveau() { python3 -c "print(max(3, int($1 / 2**$2 + 0.5)))"; }
voxel_au_niveau()    { python3 -c "print($1 * 2**$2)"; }
# ⚠⚠ LE COMPTE DE COUCHES QUE LE VERDICT LIRA, qui n est pas le compte de tranches. Le
# profil enregistre `couche_tracee = N / 2` (division entiere) et `test_convergence` en
# deduit `2 x couche_tracee + 1`. Une fenetre de 40 tranches est donc relue comme 41
# couches. Sans cette fonction on raisonne sur 40 et 81 -- rapport 2,03, admissible --
# alors que le verdict verra 41 et 81, rapport 1,98, et REFUSERA apres deux rendus.
couches_effectives() { python3 -c "print(2 * ($1 // 2) + 1)"; }
# ⚠⚠ Une FONCTION et pas un test en ligne, pour que la sonde porte sur le COMPORTEMENT et
# pas sur une orthographe. Ce depot a paye ce matin meme une sonde qui visait un appel ecrit
# en une ligne et laissait passer le meme appel ecrit sur deux : elle attrapait la facon
# d ecrire la regle, jamais la regle.
garder_rendu() { [ "${GARDER_RENDU:-0}" = 1 ]; }

if [ "${1:-}" = "--verifier" ]; then
  ok=0; n=0
  chk() { n=$((n+1)); if eval "$2"; then :; else echo "  FAIL $1"; ok=1; fi; }
  chk "au niveau 0, rien ne bouge" '[ "$(tranches_au_niveau 41 0)" = 41 ] && [ "$(voxel_au_niveau 2.4 0)" = 2.4 ]'
  chk "au niveau 1, les tranches sont divisees" '[ "$(tranches_au_niveau 41 1)" = 21 ]'
  chk "... et le voxel multiplie" '[ "$(voxel_au_niveau 2.4 1)" = 4.8 ]'
  chk "au niveau 2 aussi" '[ "$(tranches_au_niveau 161 2)" = 40 ] && [ "$(voxel_au_niveau 2.4 2)" = 9.6 ]'
  # ⚠⚠ Une fenetre impaire le RESTE : elle est centree sur sa couche tracee, et une
  # fenetre paire n a pas de centre -- le decalage serait d une demi-tranche par niveau,
  # en silence. ⚠ round() de Python arrondit au PAIR et rendrait 20 : la sonde le fixe.
  chk "une fenetre impaire reste impaire au niveau 1" \
      '[ "$(python3 -c "print($(tranches_au_niveau 41 1) % 2)")" = 1 ]'
  chk "... et 161 aussi" '[ "$(tranches_au_niveau 161 1)" = 81 ]' 
  # ⚠⚠ La propriete qui compte : la PROFONDEUR PHYSIQUE est conservee a une tranche pres.
  # Si elle ne l etait pas, deux niveaux mesureraient deux fenetres differentes et l ecart
  # d alpha qu on lirait serait celui des fenetres, pas celui des resolutions.
  chk "la profondeur physique est conservee au niveau 1" \
      '[ "$(python3 -c "a=41*2.4; b=$(tranches_au_niveau 41 1)*$(voxel_au_niveau 2.4 1); print(abs(a-b) <= $(voxel_au_niveau 2.4 1))")" = True ]'
  chk "... et au niveau 2" \
      '[ "$(python3 -c "a=161*2.4; b=$(tranches_au_niveau 161 2)*$(voxel_au_niveau 2.4 2); print(abs(a-b) <= $(voxel_au_niveau 2.4 2))")" = True ]'
  # ⚠ Un plancher de trois tranches : une fenetre de deux ne porte aucun profil, et une
  # division agressive la produirait en silence.
  chk "une fenetre trop divisee est plancheee a 3" '[ "$(tranches_au_niveau 5 4)" = 3 ]'
  out=$(PLAT=/inexistant "$ROOT/tools/profiler_une_surface.sh" 2>&1); rc=$?
  chk "une surface absente est refusee (2)" '[ "$rc" = 2 ]'
  chk "le plancher de la pyramide est verifie avant de rendre" \
      'grep -q "FENETRE_ANALYSE" "$ROOT/tools/profiler_une_surface.sh"'
  chk "le refus a son propre code de sortie" \
      'grep -q "exit 5" "$ROOT/tools/profiler_une_surface.sh"'
  chk "la lecture d en-tete est deleguee, pas recopiee" \
      '[ -f "$ROOT/analysis/src/dimensions_tiff.py" ] && grep -q dimensions_tiff "$ROOT/tools/profiler_une_surface.sh"'
  chk "au moins un appelant utilise ce script" \
      'grep -lq profiler_une_surface.sh "$ROOT"/tools/*.sh'
  # ⚠⚠ Le controle du correctif de chemin : ce script `cd` dans deux sous-projets, donc
  # tout chemin qu il recoit doit etre rendu absolu AVANT le premier `cd`. Sans ca le rendu
  # reussit et le profil meurt sur un fichier qui existe pourtant.
  # ⚠⚠ Le niveau de la reference : sans lui, une reference rendue au niveau 1 fait refuser
  # une surface analysable. La regle est testee sur les deux formes de chemin.
  niv_ref() { case "$1" in */g[0-9]_n[0-9]*/rendu/*) echo "$1" | sed -n 's|.*/g\([0-9]\)_n[0-9]*/rendu/.*|\1|p' ;; *) echo 0 ;; esac; }
  # ⚠⚠ Le +1 : une fenetre de 40 tranches est relue comme 41 couches, donc un couple
  # 40/81 a un rapport de 1,98 et non 2,03. Le refuser AVANT le rendu est le meme argument
  # que le refus a 1024 px, que ce fichier applique deja.
  chk "40 tranches valent 41 couches" '[ "$(couches_effectives 40)" = 41 ]'
  chk "81 tranches en valent 81" '[ "$(couches_effectives 81)" = 81 ]'
  chk "83 tranches en valent 83" '[ "$(couches_effectives 83)" = 83 ]'
  L_REFUS=$(grep -n 'exit 6' "$ROOT/tools/profiler_une_surface.sh" | cut -d: -f1 | head -1)
  L_RENDU=$(grep -n 'rendre_surveille.sh' "$ROOT/tools/profiler_une_surface.sh" | cut -d: -f1 | head -1)
  chk "le refus du rapport sort AVANT le rendu" \
      '[ -n "$L_REFUS" ] && [ -n "$L_RENDU" ] && [ "$L_REFUS" -lt "$L_RENDU" ]'
  # ⚠⚠ Une campagne tronquee doit se DIRE. Sans ca son JSON ressemble a un resultat.
  chk "une campagne tronquee est signalee" \
      'grep -q "CAMPAGNE TRONQUEE" "$ROOT/tools/profiler_une_surface.sh"'
  chk "... et la mention voyage dans le JSON" \
      'grep -q "campagne_complete" "$ROOT/tools/profiler_une_surface.sh"'
  chk "les fenetres produites sont comptees, pas supposees" \
      '[ "$(grep -c "PRODUITES=\$((PRODUITES + 1))" "$ROOT/tools/profiler_une_surface.sh")" = 1 ]'
  chk "une reference dans g1_n163 est lue au niveau 1" \
      '[ "$(niv_ref a/g1_n163/rendu/000.tif)" = 1 ]'
  chk "une reference hors de cette forme est au niveau 0" \
      '[ "$(niv_ref a/rendu_41/000.tif)" = 0 ]'
  chk "le guard ramene la cote au niveau 0 avant de descendre" \
      'grep -q "COTE0=\$((COTE \* (1 << NIV_REF)))" "$ROOT/tools/profiler_une_surface.sh"'
  chk "les chemins sont rendus absolus avant tout cd" \
      '[ "$(grep -cE "^(PLAT|DEST|JSON)=.*pwd" "$ROOT/tools/profiler_une_surface.sh")" -ge 3 ]'
  # ⚠ Les deux numeros sont lus dans des variables et testes pour etre NON VIDES d abord :
  # une premiere version comparait directement, et quand un motif ne matchait plus le
  # controle sortait « test: invalid integer » -- un echec illisible se lit comme un bug de
  # la sonde et finit par etre ignore.
  # ⚠⚠ ANCRES EN DEBUT DE LIGNE, et c est la huitieme fois que ce depot paie ce piege : sans
  # le `^`, chacun de ces deux greps matche SA PROPRE LIGNE ici meme, donc le controle reste
  # vert quand le correctif disparait. Verifie par sonde : retirer la resolution laissait la
  # batterie verte. Le remede n est pas de couper le motif, c est de l ancrer sur la syntaxe
  # -- les vraies occurrences sont en colonne zero, les mentions sont indentees.
  L_MKDIR=$(grep -n '^mkdir -p "$DEST"' "$ROOT/tools/profiler_une_surface.sh" | cut -d: -f1 | head -1)
  L_RESOL=$(grep -n '^DEST=$(cd' "$ROOT/tools/profiler_une_surface.sh" | cut -d: -f1 | head -1)
  chk "... et la destination est creee avant d etre resolue" \
      '[ -n "$L_MKDIR" ] && [ -n "$L_RESOL" ] && [ "$L_MKDIR" -lt "$L_RESOL" ]'
  # ⚠⚠ La pile rendue est le seul artefact relisible a une AUTRE geometrie. Les trois
  # sondes portent sur la fonction elle-meme : par defaut on jette, `1` garde, et rien
  # d autre ne garde -- un `GARDER_RENDU=oui` qui conserverait remplirait le disque en
  # silence a 562 Mo la pile.
  chk "par defaut la pile est jetee" '! ( unset GARDER_RENDU; garder_rendu )'
  chk "GARDER_RENDU=1 la conserve" 'GARDER_RENDU=1 garder_rendu'
  chk "une autre valeur ne garde pas" '! GARDER_RENDU=oui garder_rendu'
  # ⚠⚠ Le garde de taille cherche un RENDU, pas un fichier dont le chemin contient le mot.
  # Sonde : un arbre ou le maillage vit sous un dossier nomme `..._rendu` -- exactement le
  # cas qui a refuse quatre surfaces le 2026-08-24.
  T_REF=$(mktemp -d)
  mkdir -p "$T_REF/temoin_rendu/morceaux/m0" "$T_REF/vrai/rendu_161"
  : > "$T_REF/temoin_rendu/morceaux/m0/x.tif"
  : > "$T_REF/vrai/rendu_161/000.tif"
  chk "un maillage sous un dossier « ...rendu » n est pas pris pour un rendu" \
      '[ -z "$(find "$T_REF/temoin_rendu/morceaux" \( -path "*/rendu/*" -o -path "*/rendu_*/*" \) -name "*.tif" 2>/dev/null)" ]'
  chk "... alors qu un vrai rendu est bien trouve" \
      '[ -n "$(find "$T_REF/vrai" \( -path "*/rendu/*" -o -path "*/rendu_*/*" \) -name "*.tif" 2>/dev/null)" ]'
  chk "... et l ancienne forme, elle, se trompait" \
      '[ -n "$(find "$T_REF/temoin_rendu/morceaux" -path "*rendu*" -name "*.tif" 2>/dev/null)" ]'
  rm -rf "$T_REF"
  chk "le cache part dans tous les cas" \
      '[ "$(grep -c '"'"'^    rm -rf "$W/cache"$'"'"' "$ROOT/tools/profiler_une_surface.sh")" = 1 ]'
  echo "$([ $ok = 0 ] && echo 'ALL PASS' || echo FAILURES) ($ok failures, $n checks)"
  exit $ok
fi

PLAT="${PLAT:-}"
[ -d "$PLAT" ] || { echo "refus : surface aplatie absente — PLAT=$PLAT" >&2; exit 2; }
# ⚠⚠ LES CHEMINS SONT RENDUS ABSOLUS ICI, et c est un correctif paye le 2026-08-23. Ce
# script fait `cd` dans deux sous-projets (`inference_xpu` pour le profil, `experiments`
# pour le verdict), donc un chemin RELATIF passe par l appelant cesse d exister apres le
# premier `cd`. Le symptome ne ressemble pas a la cause : le rendu reussit, puis le profil
# meurt sur un `FileNotFoundError` nommant un chemin qui existe bel et bien -- depuis le
# repertoire de l appelant. Resoudre au bord, une fois, est le seul endroit ou ca se fait.
PLAT=$(cd "$PLAT" && pwd)
NIVEAU="${NIVEAU:-0}"
FENETRES_BASE="${FENETRES_BASE:-41 161}"
UM_BASE="${UM_BASE:-2.4}"
PATIENCE="${PATIENCE:-420}"
DEST="${DEST:?DEST requis}"
ETIQUETTE="${ETIQUETTE:-$(basename "$DEST")}"
JSON="${JSON:?JSON requis}"
# ⚠ `mkdir -p` avant de resoudre : un chemin qui n existe pas encore n a pas de forme
# absolue, et la destination est justement ce que ce script cree.
mkdir -p "$DEST" "$(dirname "$JSON")"
DEST=$(cd "$DEST" && pwd)
JSON="$(cd "$(dirname "$JSON")" && pwd)/$(basename "$JSON")"
B="https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOL="${VOL:-PHercParis4/volumes/20260411134726-2.400um-0.2m-78keV-masked.zarr}"

UM=$(voxel_au_niveau "$UM_BASE" "$NIVEAU")
echo "== niveau $NIVEAU  (voxel ${UM} µm)  ·  $ETIQUETTE"

# ⚠ La taille est estimee depuis un rendu DEJA fait de la meme surface, s il en existe un :
# c est la seule facon de la connaitre sans rendre. Sans reference on n avertit pas -- une
# garde qui devine serait pire que pas de garde.
# ⚠⚠ LE COMPOSANT DE CHEMIN, PAS LA SOUS-CHAINE. La premiere version cherchait `*rendu*`
# n importe ou dans le chemin -- donc n importe quel DOSSIER dont le nom contient « rendu »
# empoisonnait l estimation. Paye le 2026-08-24 : les morceaux du temoin vivent sous
# `data/temoin_rendu/`, le find y a trouve le `x.tif` du MAILLAGE (119 x 120 points de
# grille), et le garde a refuse quatre surfaces parfaitement rendables en annoncant « ~119
# px de cote » -- pour des surfaces qui en font 2400. Un maillage n est pas un rendu, et la
# seule chose qui les distingue de facon fiable est le nom du DOSSIER qui les contient.
REF=$(find "$(dirname "$PLAT")" \( -path "*/rendu/*" -o -path "*/rendu_*/*" \) \
        -name "*.tif" 2>/dev/null | head -1)
if [ -n "$REF" ]; then
  COTE=$(python3 "$ROOT/analysis/src/dimensions_tiff.py" "$REF" --cote 2>/dev/null || true)
  # ⚠⚠ LE NIVEAU DE LA REFERENCE, lu et non suppose. La premiere version divisait la cote
  # trouvee par 2^NIVEAU en la croyant toujours au niveau 0 : quand la reference est
  # elle-meme un rendu au niveau 1 -- ce que ce script produit, dans `g1_n<N>/rendu/` -- le
  # calcul divise deux fois et refuse une surface parfaitement analysable. Mesure le
  # 2026-08-24 sur `ps256_c2_g200` : reference a 4001 px au niveau 1, le guard annoncait
  # 1000 px au niveau 2 alors que le rendu y fait 2001. Le nom du dossier porte le niveau,
  # donc on le lit plutot que de le deviner.
  NIV_REF=0
  case "$REF" in
    */g[0-9]_n[0-9]*/rendu/*) NIV_REF=$(echo "$REF" | sed -n 's|.*/g\([0-9]\)_n[0-9]*/rendu/.*|\1|p') ;;
  esac
  if [ -n "${COTE:-}" ]; then
    # ⚠ La cote est d abord ramenee au niveau 0, PUIS descendue au niveau demande.
    COTE0=$((COTE * (1 << NIV_REF)))
    ICI=$((COTE0 / (1 << NIVEAU)))
    if [ "$ICI" -lt "$FENETRE_ANALYSE" ]; then
      echo "   ⚠⚠ refus : au niveau $NIVEAU cette surface ferait ~${ICI} px de côté," >&2
      echo "      sous la fenêtre d'analyse de ${FENETRE_ANALYSE}. La rendre serait payer" >&2
      echo "      un calcul entier pour un refus à la toute dernière étape." >&2
      exit 5
    fi
  fi
fi
# ⚠⚠ LE REFUS AVANT DE PAYER, et ce fichier le pratiquait deja pour la taille de fenetre
# d analyse sans l appliquer au RAPPORT. Paye le 2026-08-24 : un couple demande a 40 et 81
# tranches a coute deux rendus, puis le verdict a repondu « fenetres trop proches (41 et 81,
# rapport 1.98) ». Le meme argument que le refus a 1024 px vaut ici -- rendre serait payer
# un calcul entier pour un refus a la toute derniere etape.
RAPPORT_MIN=2
EFF=""
for F in $FENETRES_BASE; do
  EFF="$EFF $(couches_effectives "$(tranches_au_niveau "$F" "$NIVEAU")")"
done
if ! python3 -c "import sys; c=sorted(int(x) for x in sys.argv[1].split()); sys.exit(0 if len(c)<2 or c[-1]/c[0] >= float(sys.argv[2]) else 1)" "$EFF" "$RAPPORT_MIN"; then
  echo "   ⚠⚠ refus : au niveau $NIVEAU ces fenetres seront relues comme$EFF couches," >&2
  echo "      dont le rapport est sous $RAPPORT_MIN. Le verdict refuserait APRES le rendu." >&2
  echo "      Une fenetre de N tranches vaut 2*(N//2)+1 couches : 40 tranches font 41." >&2
  exit 6
fi

PROFILS=""
DEMANDEES=0; PRODUITES=0
for F in $FENETRES_BASE; do
  DEMANDEES=$((DEMANDEES + 1))
  N=$(tranches_au_niveau "$F" "$NIVEAU")
  W="$DEST/g${NIVEAU}_n${N}"
  OUT="$W/profil.json"
  if [ ! -s "$OUT" ]; then
    rm -rf "$W"; mkdir -p "$W"
    "$ROOT/tools/rendre_surveille.sh" "$W/rendu" "$PATIENCE" -- \
        -v "$W/cache" --remote-url "$B/$VOL" --scale 1 -g "$NIVEAU" -s "$PLAT" \
        --tif-output "$W/rendu" -n "$N" --slice-step 1 --auto-crop \
        > "$W/rendu.log" 2>&1 || { echo "   ⚠ rendu n=$N abandonné"; continue; }
    ( cd "$ROOT/inference_xpu" && uv run python ../analysis/src/depth_profile.py \
        "$W/rendu" --grid --step 200 --traced-layer $((N / 2)) --voxel-um "$UM" \
        --out "$OUT" ) > "$W/profil.log" 2>&1 \
      || { echo "   ⚠ profil n=$N échoué"; continue; }
    # ⚠⚠ Le cache part toujours -- c est du volume telecharge, reconstructible et enorme.
    # La PILE, elle, est le seul artefact qu un second lecteur puisse relire a une AUTRE
    # geometrie ; la jeter oblige a repayer le rendu pour poser une question differente sur
    # la meme surface. C est exactement ce qu il a fallu faire pour situer nos traces dans
    # leur corpus. `GARDER_RENDU=1` la conserve ; le defaut reste de la jeter, parce qu une
    # campagne de plusieurs fenetres remplirait le disque en silence (562 Mo par pile).
    rm -rf "$W/cache"
    garder_rendu || rm -rf "$W/rendu"
  fi
  echo "   n=$N couches"
  PRODUITES=$((PRODUITES + 1))
  PROFILS="$PROFILS --profil $OUT"
done
[ -n "$PROFILS" ] || { echo "   ⚠ aucun profil produit"; exit 3; }
# ⚠⚠ UNE CAMPAGNE TRONQUEE NE DOIT PAS RESSEMBLER A UNE CAMPAGNE COMPLETE. Paye le
# 2026-08-24 : un run interrompu au second rendu a quand meme ecrit son JSON, avec une serie
# a UN point et un verdict « indecidable ». Le fichier est arrive dans `docs/` et rien en lui
# ne disait qu il venait d un run avorte -- un lecteur y voit un resultat.
#
# ⚠ On ECRIT quand meme, et on refuse de se taire : jeter le fichier perdrait la fenetre qui,
# elle, a bien ete rendue. Ce qui manquait n est pas le refus, c est la MENTION.
if [ "$PRODUITES" -lt "$DEMANDEES" ]; then
  echo "   ⚠⚠ CAMPAGNE TRONQUEE — $PRODUITES fenêtre(s) sur $DEMANDEES demandées." >&2
  echo "      Le verdict qui suit ne porte que sur ce qui a été produit." >&2
fi
( cd "$ROOT/experiments" && uv run python ../analysis/src/test_convergence.py $PROFILS \
    --nom "$ETIQUETTE" --json "$JSON" | tail -4 )
# ⚠ La mention voyage AVEC le resultat, pas seulement dans le terminal : un JSON relu six
# mois plus tard n a pas le journal de son run a cote.
python3 - "$JSON" "$PRODUITES" "$DEMANDEES" <<'PY'
import json, sys
chemin, produites, demandees = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
try:
    d = json.load(open(chemin, encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    raise SystemExit(0)
if isinstance(d, dict):
    d["fenetres_produites"] = produites
    d["fenetres_demandees"] = demandees
    d["campagne_complete"] = produites == demandees
    json.dump(d, open(chemin, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
