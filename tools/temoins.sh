#!/bin/bash
# Relancer TOUS les temoins du depot d'un coup.
#
# ⚠ Un depot dont on ne rejoue jamais les controles ne sait plus s'ils passent. Ceux-ci
# tournent tous HORS LIGNE -- ni reseau, ni volume distant, ni cle d'API -- justement
# pour qu'aucune raison exterieure ne puisse les empecher de tourner.
#
# Sort non nul si un seul echoue.
set -u
cd "$(dirname "$0")/.." || exit 2
ROOT=$PWD
FAIL=0

run() {
  local nom=$1; shift
  local sortie
  sortie=$("$@" 2>&1 | grep -vE "SyntaxWarning|if amt")
  if grep -q "ALL PASS" <<<"$sortie"; then
    printf '  ✅ %-28s %s\n' "$nom" "$(grep -o 'ALL PASS.*' <<<"$sortie" | head -1)"
  else
    printf '  ❌ %-28s ECHEC\n' "$nom"
    sed 's/^/       /' <<<"$sortie" | tail -5
    FAIL=$((FAIL + 1))
  fi
}

echo "TEMOINS DU DEPOT — tous hors ligne"
echo

cd "$ROOT/experiments" || exit 2
run "fusions : pistes"        uv run python src/excision/fusions.py controle
run "fusions : ecarts"        uv run python src/excision/fusions.py ecarts-controle
run "fusion_scan : colocation" uv run python - <<'PY'
import sys; sys.path.insert(0,'src')
from excision.fusion_scan import colocation, null_model
n=0
same=[[{'radius_mm':17.1,'column':16000}],[{'radius_mm':17.3,'column':16200}]]
far =[[{'radius_mm':17.1,'column':16000}],[{'radius_mm': 5.0,'column':  200}]]
assert colocation(same,1.0,1000)['colocated']==1; n+=1
assert colocation(far ,1.0,1000)['colocated']==0; n+=1
# une seule coupe ne produit AUCUNE paire : la regle inter-coupes
assert colocation([[{'radius_mm':17.1,'column':16000},{'radius_mm':17.2,'column':16100}]],1.0,1000)['pairs']==0; n+=1
h=null_model(same,(5.,20.),18850,1.0,1000,300,0)
assert 0.0 <= h['mean'] <= 1.0; n+=1
print(f'ALL PASS (0 failures, {n} checks)')
PY

run "track_z : suiveur predictif" uv run python - <<'PY'
import sys; sys.path.insert(0,'src')
from excision.track_z import track, straightness, summarise, permute
import numpy as np
n=0
def ck(c):
    global n
    assert c; n+=1
# Un site qui DERIVE d'un millimetre par coupe : la fenetre fixe le perd, la
# prediction le suit. C'est la revendication entiere du §11, en quatre lignes.
# ⚠ Les pas sont ceux MESURES sur le vrai site (0,5 / 0,9 / 1,4 / 1,9 mm) et non une
# derive constante : a derive constante egale a la tolerance on teste une egalite au
# bord, et le vrai defaut ACCELERE. ⚠ Limite reelle du suiveur, visible ici : le
# PREMIER lien se fait toujours a vitesse nulle, donc un site qui derive plus vite que
# la tolerance des sa premiere coupe ne peut pas etre amorce.
derive=[{'z':100*i,'cells':[(r, 1000.0)]} for i,r in enumerate([10.0,10.5,11.4,12.8,14.7])]
ck(len(max(track(derive,1.0,1000.0,True ),key=len))==5)
ck(len(max(track(derive,1.0,1000.0,False),key=len))<5)
# ⚠ Un site STATIONNAIRE doit donner le MEME resultat des deux cotes : sans quoi la
# prediction ne serait pas une prediction, ce serait une fenetre elargie.
fixe=[{'z':100*i,'cells':[(10.0, 1000.0)]} for i in range(5)]
ck(len(max(track(fixe,1.0,1000.0,True),key=len))==len(max(track(fixe,1.0,1000.0,False),key=len))==5)
# Un ecart angulaire au-dela de la tolerance rompt, meme si le rayon colle.
loin=[{'z':0,'cells':[(10.0,1000.0)]},{'z':100,'cells':[(10.0,9000.0)]}]
ck(len(max(track(loin,1.0,1000.0,True),key=len))==1)
ck(abs(straightness([(0,10.,0),(1,11.,0),(2,12.,0)])-1.0)<1e-9)   # monotone
ck(straightness([(0,10.,0),(1,12.,0),(2,10.,0)])==0.0)            # zigzag pur
ck(abs(summarise(track(derive,1.0,1000.0,True))['span_mm']-4.7)<1e-9)
ck(len(max(track(derive,1.0,1000.0,False),key=len))==3)   # la fenetre fixe s'arrete a 3
# La permutation conserve le multiensemble ET les effectifs par coupe.
g=np.random.default_rng(0); q=permute(derive,g)
ck(sorted(c for s in q for c in s['cells'])==sorted(c for s in derive for c in s['cells']))
ck([len(s['cells']) for s in q]==[len(s['cells']) for s in derive])
print(f'ALL PASS (0 failures, {n} checks)')
PY

run "reference : boule vs bande" uv run python - <<'PY'
import sys; sys.path.insert(0,'src')
import numpy as np
from excision.proximity import local_baseline
from excision.baseline_sweep import ball_baseline, contamination
n=0
def ck(c):
    global n
    assert c; n+=1
g=np.random.default_rng(0)
N=1200
# Un nuage ou l'espacement est UNIFORME a 100, sauf 40 cellules groupees en une boule
# serree ou il tombe a 30 : c'est la forme d'un site de croisement, region 3D compacte.
pts=g.uniform(0,4000,size=(N,3)); cols=g.integers(0,3000,size=N).astype(float)
d=np.full(N,100.0); bad=np.arange(40)
pts[bad]=np.array([2000.,2000.,2000.])+g.uniform(-60,60,size=(40,3)); d[bad]=30.0
sample=np.arange(N)
bande=local_baseline(cols,sample,d,50)
boule=ball_baseline(pts,sample,d,400.0)
# ⚠ LA revendication du §6 de docs/07, sur une donnee dont on connait la verite :
# la bande garde 100 aux cellules anormales (ses voisins en colonne sont sains),
# la boule tombe a 30 (ses voisins en 3D SONT l'anomalie).
ck(abs(np.median(bande[bad])-100.0)<1.0)
ck(abs(np.median(boule[bad])-30.0)<1.0)
ck(abs(np.median(bande[40:])-100.0)<1.0)
c=contamination(d,bande,boule)
ck(c['flagged']==40)                                  # les 40 sont signalees
ck(abs(c['shrink_partout']-1.0)<0.05)                 # ailleurs, les deux s'accordent
ck(c['shrink_aux_signalees']<0.4)                     # la, la boule s'effondre
ck(c['shrink_aux_signalees'] < c['shrink_partout'])   # et c'est SPECIFIQUE
print(f'ALL PASS (0 failures, {n} checks)')
PY

cd "$ROOT/inference_xpu" || exit 2
run "pile : sommet ou borne"   uv run python - <<'PY'
import sys, numpy as np; sys.path.insert(0,'../analysis/src')
from stack_structure import describe
n=0
def ck(c):
    global n
    assert c; n+=1
L=list(range(65))
# Une pile ou la matiere PIQUE a la couche 26 : le sommet est reel, la distance aussi.
c=[np.exp(-((i-26)/6.0)**2) for i in L]
r=describe(L,c,c)
ck(r['sommets']==[26]); ck(r['distance_au_sommet']==6); ck(not r['distance_est_une_borne'])
# ⚠ LA regle qui compte : une pile dont le contraste est MAXIMAL au bord n'a pas de
# sommet -- c'est le flanc d'un sommet situe dehors. Rendre 0 comme distance ferait
# passer « je ne sais pas ou est la feuille » pour « la trace est dessus ».
c=[1.0-i/64.0 for i in L]
r=describe(L,c,c)
ck(r['sommets']==[]); ck(r['distance_est_une_borne']); ck(r['distance_au_sommet']==32)
ck(r['monte_encore_au_bord_bas'] and not r['monte_encore_au_bord_haut'])
# Deux blocs, coeurs hors pile des deux cotes : le cas Scroll 4.
c=[max(1.0-i/40.0, (i-46)/18.0 if i>46 else 0.0) for i in L]
r=describe(L,c,c)
ck(r['sommets']==[]); ck(r['distance_est_une_borne'])
ck(r['monte_encore_au_bord_bas'] and r['monte_encore_au_bord_haut'])
# Une pile qui ne contient pas la couche 32 doit REFUSER, pas deviner.
try:
    describe(list(range(15,31)),[1.0]*16,[1.0]*16); ck(False)
except ValueError:
    ck(True)
print(f'ALL PASS (0 failures, {n} checks)')
PY

run "zarr : clef de chunk"    uv run python - <<'PY'
import sys; sys.path.insert(0,'../analysis/src')
from zarr_depth import chunk_key, decode
n=0
def ck(c):
    global n
    assert c; n+=1
# ⚠⚠ LE BUG QUE CE TEMOIN GARDE, et il ne levait AUCUNE erreur. Le niveau est toujours
# un repertoire ; seuls les indices de chunk utilisent `dimension_separator`. Une clef
# `0.0.0.0` rend un 404, le lecteur comptait le 404 en « chunk vide », et le segment
# entier passait pour depourvu de matiere -- un resultat, faux, sans le moindre signe.
ck(chunk_key({"dimension_separator": "/"}, 0, 12, 34) == "0/0/12/34")
ck(chunk_key({"dimension_separator": "."}, 0, 12, 34) == "0/0.12.34")
ck(chunk_key({}, 2, 5, 7) == "2/0.5.7")            # defaut zarr v2 : le point
# ⚠ « absent » et « illisible » doivent rester distincts d'un chunk vide.
ck(decode(b"abc", {}, 3) == b"abc")                 # brut, taille juste
ck(decode(b"ab", {}, 3) is None)                    # brut tronque -> refus
ck(decode(b"xx", {"compressor": {"id": "inconnu"}}, 3) is None)
print(f'ALL PASS (0 failures, {n} checks)')
PY

run "juge : choix des bandes" uv run python - <<'PY'
import sys, pathlib, numpy as np; sys.path.insert(0,'../analysis/src')
from judge_api import choose_bands, TEXT_BANDS
n=0
def ck(c):
    global n
    assert c; n+=1
# ⚠ Une carte fabriquee avec DEUX zones encrees separees, et pas une seule : avec une
# seule, le plancher de candidat en rejette la deuxieme et le temoin plante au lieu de
# tester ce qu'il annonce.
faux=np.full((6144,600),-3.0,dtype=np.float32); faux[:1024]=+3.0; faux[3072:4096]=+3.0
haut,bas,fr=choose_bands(faux,1024,2,512)
ck(fr['candidat'][0]>0.9 and fr['vierge'][0]<0.05)
ck(all(abs(a-b)>=1024+512 for (a,_) in haut for (b,_) in bas))   # pas de recouvrement
ck(abs(haut[0][0]-haut[1][0])>=1024+512)                         # ni entre elles
# ⚠ LE CONTROLE QUI COMPTE, sur la VRAIE carte de Scroll 1 : le choix automatique
# doit retrouver la bande de texte mesuree a la main, et surtout ne jamais rendre un
# faux temoin -- la bande (7168,1024) porte 3,75 % d'encre et avait ete retiree.
carte=pathlib.Path('../data/out/ink_segment_complet.npy')
if carte.is_file():
    v=np.asarray(np.load(carte, mmap_mode='r'))
    for count in (1,2,3,4):
        h,b,f=choose_bands(v,1024,count,512)
        ck(h[0][0]==TEXT_BANDS[0][0])            # retrouve la bande de texte a la main
        ck(len(b)==1 and f['vierge'][0]<0.02)    # UNE seule zone franchement vierge
    # ⚠ Le compteur du selecteur doit RETROUVER la mesure faite a la main : la bande
    # (7168,1024) avait ete listee comme temoin puis retiree apres mesure a 3,75 %.
    # Si le compteur rendait autre chose ici, le plafond protegerait contre un chiffre
    # qui n'est pas celui du depot -- et le faux temoin repasserait un jour.
    ck(abs(float((v[7168:8192] > 0.0).mean()) - 0.0375) < 0.005)
    ck(float((v[7168:8192] > 0.0).mean()) > 0.02)        # donc inadmissible
    # ⚠ Le plafond doit etre CE QUI limite, et pas un bug : le relever doit rendre
    # plus de bandes. Sans ce controle, « une seule bande vierge » serait aussi ce
    # que rendrait un selecteur casse.
    _,large,fl=choose_bands(v,1024,3,512,blank_ceiling=0.10)
    ck(len(large)>1 and max(fl['vierge'])>0.02)
print(f'ALL PASS (0 failures, {n} checks)')
PY

run "juge : depouilleur"      uv run python - <<'PY'
import sys; sys.path.insert(0,'../analysis/src')
from judge_api import parse
n=0
def ck(c):
    global n
    assert c; n+=1
ck(parse('LIGNES: 2\nL1: X\nLISIBILITE: 8') == {})          # format mono-panneau rejete
r=parse('PANNEAU: GAUCHE\nAUCUNE LETTRE VISIBLE\nLISIBILITE: 0\n\nPANNEAU: DROITE\nLIGNES: 2\nL1: ΠΑΡΑ·\nL1_CONFIANCE: 99986\nL2: ΥΙΤΕΡΦ\nLISIBILITE: 8')
ck(r['gauche']['refused'] and r['gauche']['glyphs']==0)
ck(not r['droite']['refused'])
ck(r['droite']['glyphs']==10)                                # 4 + 6, le · exclu
ck(r['droite']['legibility']==8)
f=parse('PANNEAU: GAUCHE\nLIGNES: 1\nL1: ΤΟΥ\nLISIBILITE: 5\nPANNEAU: DROITE\nAUCUNE LETTRE VISIBLE')
ck(not f['gauche']['refused'] and f['gauche']['glyphs']==3)   # fabrication detectable
print(f'ALL PASS (0 failures, {n} checks)')
PY

echo
if [ "$FAIL" -eq 0 ]; then
  echo "TOUS LES TEMOINS PASSENT"
else
  echo "$FAIL batterie(s) en echec"
fi
exit "$FAIL"
