#!/bin/bash
# Relancer TOUS les temoins du depot d'un coup.
#
# ⚠ Un depot dont on ne rejoue jamais les controles ne sait plus s'ils passent. Ceux-ci
# tournent tous HORS LIGNE -- ni reseau, ni volume distant, ni cle d'API -- justement
# pour qu'aucune raison exterieure ne puisse les empecher de tourner.
#
# Sort non nul si un seul echoue.
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT=$PWD
FAIL=0

# ⚠⚠ Une batterie est verte si elle satisfait DEUX conditions, pas une. La version
# precedente ne testait que la presence de "ALL PASS" quelque part dans la sortie, et
# perdait le code de sortie dans le tube. Deux batteries ecrites le 2026-08-19 sont
# passees au vert en echouant, pour la meme raison : elles imprimaient la chaine magique
# AILLEURS qu'a leur ligne de verdict -- l'une dans un bloc d'echec ("ALL PASS (1
# failures, ...)"), l'autre en recopiant la ligne de reference d'une autre suite.
#
# Deux remedes, tous deux structurels :
#   1. le code de sortie compte (`PIPESTATUS`, sinon `grep` masque tout) ;
#   2. le verdict lu est le DERNIER "ALL PASS", pas le premier -- une ligne de contexte
#      imprimee avant ne peut donc plus se faire passer pour le verdict.
# ⚠⚠ Les totaux sont COMPTES, pas ecrits dans une doc. `README` annoncait « 18 batteries,
# 741 controles » alors qu'il y en avait 24 et 1092 : un chiffre recopie a la main dans une
# prose vieillit en silence, et c'est precisement le defaut que ce depot outille ailleurs
# (`src/depot/verifier_chiffres.py`). Ils sont donc ecrits dans `docs/temoins.json` et
# gardes comme tous les autres chiffres publies.
BATTERIES=0
CONTROLES=0

run() {
  local nom=$1; shift
  local sortie rc
  sortie=$("$@" 2>&1); rc=$?
  sortie=$(grep -vE "SyntaxWarning|if amt" <<<"$sortie")
  BATTERIES=$((BATTERIES + 1))
  if [ "$rc" -eq 0 ] && grep -q "ALL PASS" <<<"$sortie"; then
    CONTROLES=$((CONTROLES + $(grep -o 'ALL PASS.*' <<<"$sortie" | tail -1 \
                  | grep -oE '[0-9]+ checks' | grep -oE '[0-9]+' || echo 0)))
    printf '  ✅ %-28s %s\n' "$nom" "$(grep -o 'ALL PASS.*' <<<"$sortie" | tail -1)"
  else
    printf '  ❌ %-28s ECHEC (code %s)\n' "$nom" "$rc"
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
import sys; import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
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
import sys; import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
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
import sys; import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
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
import sys, numpy as np; import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
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
import sys; import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
from zarr_depth import chunk_key, decode, CodecIndisponible
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
# ⚠ Le troisieme axe n'est pas toujours zero : un volume CT se sonde en z aussi. Il
# etait recolle a la main par un remplacement de chaine dans un appelant -- exactement
# la forme sous laquelle un bug silencieux revient.
ck(chunk_key({"dimension_separator": "."}, 1, 4, 5, 9) == "1/9.4.5")
ck(chunk_key({"dimension_separator": "/"}, 1, 4, 5, 9) == "1/9/4/5")
# ⚠ « absent » et « illisible » doivent rester distincts d'un chunk vide.
ck(decode(b"abc", {}, 3) == b"abc")                 # brut, taille juste
ck(decode(b"ab", {}, 3) is None)                    # brut tronque -> refus
# ⚠⚠ CE CONTROLE A CHANGE DE SENS LE 2026-08-20, et le changement est le correctif.
# Avant, un codec que la machine ne sait pas lire rendait None -- donc la meme valeur
# qu'un chunk absent. Paye : `numcodecs` manquait dans un environnement, TOUS les chunks
# blosc d'une prediction sont revenus vides, et j'en ai conclu que la graine n'etait pas
# couverte par la prediction publiee. Elle l'etait. Un defaut d'installation avait pris
# la forme d'un fait sur le rouleau. Desormais ca LEVE.
try:
    decode(b"xx", {"compressor": {"id": "inconnu"}}, 3)
    raise AssertionError("un codec inconnu doit LEVER, pas rendre None")
except CodecIndisponible:
    ck(True)
print(f'ALL PASS (0 failures, {n} checks)')
PY

run "juge : choix des bandes" uv run python - <<'PY'
import sys, pathlib, numpy as np; import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
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
import sys; import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
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

cd "$ROOT/inference_xpu" || exit 2
run "champ de correction" uv run python - <<'PY'
import sys, time, random
from pathlib import Path
import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
import numpy as np
import champ_correction as C
import zarr_depth as Z

n = 0
def ck(c, quoi=""):
    global n
    assert c, quoi
    n += 1

# --- l'ordre du parallelisme : la propriete qui rend la version parallele substituable.
# Des profils DIFFERENTS par fenetre, des delais ALEATOIRES, et le resultat doit etre
# celui de la version serie. Sans la garantie d'ordre de executor.map, les medianes et
# la courbe moyenne dependraient de la latence reseau du moment.
META = {"chunks": [16, 8, 8], "shape": [16, 64, 64], "dtype": "|u1",
        "dimension_separator": "/"}
def faux(url, level, meta, cy, cx, timeout):
    time.sleep(random.random() * 0.004)
    pic = (cy * 3 + cx) % 16
    mean = np.zeros(16, dtype=np.float32); mean[pic] = 1.0
    return mean, mean
Z.array_meta = lambda *a, **k: META
Z.chunk_profile = faux
C.array_meta = lambda *a, **k: META
C.chunk_profile = faux
serie = Z.survey("x", 0, 16, 1.0, 0, threads=1)
par = Z.survey("x", 0, 16, 1.0, 0, threads=8)
ck(serie == par, "parallele != serie")
ck(serie["avec_matiere"] > 0, "temoin vide : il passerait tout")

# --- un bloc de cote 1 ne produit AUCUNE paire de voisins. C'est pour ca que `cote`
# existe : une grandeur « entre voisins » sans voisins rend NaN sur zero paire (§8.22).
g = np.full((6, 6), np.nan)
g[2, 2] = 5.0
a, b = C._paires_voisines(g, 1)
ck(a.size == 0, "une fenetre isolee ne peut pas avoir de voisine")

# --- un champ PARFAITEMENT lisse est coherent ; le melange des memes valeurs l'effondre.
lisse = np.add.outer(np.arange(8.0), np.arange(8.0))
st = C._statistiques(lisse, 1, 32, 2.4, 64, "x")
ck(st["coherence_voisins"] > 0.9, "un champ lisse doit etre coherent")
ck(abs(st["coherence_temoin_melange"]) < 0.5, "le melange doit s'effondrer")
ck(st["paires_voisines"] == 2 * 8 * 7, "compte de paires")

# --- et un champ de BRUIT ne doit pas l'etre : sans ce cas negatif, la mesure
# pourrait rendre « coherent » sur n'importe quoi.
bruit = np.random.default_rng(1).normal(size=(12, 12))
sb = C._statistiques(bruit, 1, 32, 2.4, 144, "x")
ck(abs(sb["coherence_voisins"]) < 0.35, "du bruit ne doit pas paraitre coherent")

# --- la translation qui minimise l'ecart, et le residuel qui reste apres.
decale = np.full((6, 6), 7.0)
sd = C._statistiques(decale, 1, 32, 2.0, 36, "x")
ck(abs(sd["decalage_median_um"] - 14.0) < 1e-9, "decalage en um")
ck(sd["residuel_median_um"] == 0.0, "un decalage pur a un residuel NUL")

print(f"ALL PASS (0 failures, {n} checks)")
PY

run "decision par permutation" uv run python - <<'PY'
import sys
from pathlib import Path
import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
import numpy as np
from croiser_encre import decision

n = 0
def ck(c, quoi=""):
    global n
    assert c, quoi
    n += 1

# Un critere qui separe PARFAITEMENT : les pires ecarts portent la pire encre.
ecarts = np.arange(40.0)
encre = 100.0 - np.arange(40.0)
d = decision(ecarts, encre, 0.25, 2000, 0)
ck(d["gain"] > 0, "une regle parfaite doit ameliorer")
ck(d["p_permutation"] < 0.01, "et battre le hasard")

# ⚠ LE CAS NEGATIF, sans lequel la verification ne peut pas echouer : une cible qui
# n'a RIEN a voir avec le critere. Le p doit alors etre banal.
rng = np.random.default_rng(0)
sans = decision(ecarts, rng.permutation(encre), 0.25, 2000, 0)
ck(sans["p_permutation"] > 0.05, "un critere sans rapport ne doit pas passer")

# Le sens compte : ecarter les pires doit garder n - k segments, pas n.
ck(d["segments_gardes"] == 30, "effectif garde")
print(f"ALL PASS (0 failures, {n} checks)")
PY

cd "$ROOT/inference_xpu" || exit 2
run "tracecheck (outil public)" uv run python "$ROOT/tracecheck/selftest.py"
# ⚠ Un cran au-dessus du selftest : celui-ci verifie que chaque detecteur est PORTEUR.
# Un controle par injection attrape un detecteur aveugle, pas un detecteur absent -- une
# suite qui n'assertit jamais sur une sortie ne distingue pas "n'a rien trouve" de "n'a
# jamais ete consulte". Cf docs/28 §7.
run "tracecheck : mutation"     python3 "$ROOT/tracecheck/mutation.py"

run "robustesse : deux mesures  " uv run python - <<'PY'
import sys
from pathlib import Path
import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
import numpy as np
from scipy.stats import spearmanr

n = 0
def ck(c, quoi=""):
    global n
    assert c, quoi
    n += 1

# ⚠ Ce que le controle de `19` §9 verifie tient en une propriete : un accord de rangs
# doit se comparer a un temoin de PERMUTATION, pas a zero. Sur 80 points, un |rho| de
# 0,2 arrive au hasard une fois sur vingt -- donc l'annoncer sans temoin serait annoncer
# du bruit.
rng = np.random.default_rng(0)
x = rng.normal(size=80)
nuls = np.array([abs(spearmanr(x, rng.permutation(x))[0]) for _ in range(1000)])
ck(0.15 < np.percentile(nuls, 95) < 0.30, "le p95 du hasard a n=80 vaut ~0,22")
ck(np.median(nuls) < 0.12, "et sa mediane est proche de zero")

# Un accord PARFAIT doit le battre ; un accord NUL ne doit pas.
ck(abs(spearmanr(x, x)[0]) > np.percentile(nuls, 95))
ck(abs(spearmanr(x, rng.permutation(x))[0]) < 0.5,
   "une permutation ne doit pas ressembler a un accord")

# ⚠⚠ Et le fait que `19` §10 rapporte, APRES correction : la comparaison propre -- meme
# definition, densite 5,4x differente -- rend +0,841 contre un temoin a 0,223. Le premier
# controle (+0,280) comparait deux GRANDEURS differentes ; il est conserve ici comme
# contre-exemple, parce que c'est exactement la forme d'un faux « resultat prudent ».
ck(0.841 > 3 * 0.223, "la comparaison propre ecrase le hasard")
ck(0.280 < 2 * 0.219, "et le controle FAUX ressemblait, lui, a une instabilite reelle")
print(f'ALL PASS (0 failures, {n} checks)')
PY

run "graine : planarite"      uv run python - <<'PY'
import sys; import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
import numpy as np
from trouver_graine import scores_du_chunk, classement, voxel_allume, _agreger_voisins

n = 0
K = 8

def cube(shape):
    return np.zeros(shape, np.uint8)

def pla(K, theta, ep=1.2, shape=None):
    shape = shape or (K, K, K)
    g = np.indices(shape).astype(np.float32) - (np.array(shape).reshape(3,1,1,1) - 1) / 2.0
    n_ = np.array([np.cos(np.radians(theta)), np.sin(np.radians(theta)), 0.0])
    d = n_[0]*g[0] + n_[1]*g[1] + n_[2]*g[2]
    return ((np.abs(d) < ep).astype(np.uint8)) * 255

def p1(b, k=K):
    return float(scores_du_chunk(b, k)["planarite"][0])

# --- une feuille est planaire ; DEUX feuilles PARALLELES le sont autant. C'est la
# --- revendication qui distingue ce critere d'un detecteur de « peu de matiere ».
un = cube((K,K,K)); un[4] = 255
deux = cube((K,K,K)); deux[2] = 255; deux[6] = 255
assert p1(un) > 0.99, p1(un); n += 1
assert p1(deux) > 0.99, p1(deux); n += 1

# --- une JONCTION a 90 degres s'effondre : c'est le cas que le critere existe pour voir.
croix = cube((K,K,K)); croix[4] = 255; croix[:, 4, :] = 255
assert p1(croix) < 0.10, p1(croix); n += 1

# --- du bruit isotrope n'est pas une feuille, meme s'il occupe autant de voxels.
bruit = (np.random.default_rng(0).random((K,K,K)) < 0.15).astype(np.uint8) * 255
assert p1(bruit) < 0.20, p1(bruit); n += 1

# --- un bloc UNIFORME (tout vide ou tout plein) a un tenseur nul : ses valeurs propres
# --- sont du bruit ordonne, donc un score parfaitement defini et parfaitement vide de
# --- sens. La barriere doit l'ecarter, pas le classer.
for b in (cube((K,K,K)), np.full((K,K,K), 255, np.uint8)):
    s = scores_du_chunk(b, K)
    assert float(s["trace"][0]) == 0.0; n += 1
    cl = classement(s, 0.02, 0.80, 0, 0.90)
    assert not bool(cl["retenu"][0]); n += 1
# ⚠ Sur du binaire la bande d'occupation ecarte deja ces deux cas : la barriere sur la
# trace ne se distingue que si l'on RELACHE la bande, ce qu'un appelant a le droit de
# faire. C'est la seule forme de ce controle qui puisse echouer.
s = scores_du_chunk(np.full((K,K,K), 255, np.uint8), K)
cl = classement(s, 0.0, 1.0, 0, 0.90)
assert not bool(cl["retenu"][0]), "bloc plein retenu malgre un tenseur nul"; n += 1

# --- le biais d'orientation, MESURE : sans lissage il vaut 0,172 ; le lissage le divise
# --- par trois. Le controle porte sur la comparaison, pas sur un seuil choisi.
K2 = 16
brut = [float(scores_du_chunk(pla(K2, t), K2, 0)["planarite"][0]) for t in range(0, 91, 10)]
lisse = [float(scores_du_chunk(pla(K2, t), K2, 1)["planarite"][0]) for t in range(0, 91, 10)]
assert (max(brut) - min(brut)) > 2.5 * (max(lisse) - min(lisse)), (brut, lisse); n += 1
assert min(lisse) > 0.85, min(lisse); n += 1
# --- et le biais reste tres en dessous du signal : le pire plan bat la meilleure jonction
assert min(lisse) > p1(croix) + 0.8; n += 1

# --- la graine rendue est un voxel ALLUME. Bloc traverse en diagonale : le centre
# --- geometrique est vide, et l'ancienne version le rendait quand meme.
bord = cube((K,K,K)); bord[1] = 255           # feuille au bord : le centre est VIDE
assert bord[K//2, K//2, K//2] == 0; n += 1
pose = voxel_allume(bord, K, 0, 0, 0)
assert pose is not None and bord[pose] > 0, pose; n += 1
assert pose[0] == 1, pose; n += 1
vide = cube((K,K,K))
assert voxel_allume(vide, K, 0, 0, 0) is None; n += 1

# --- l'agregation 3x3x3 ne doit pas ENROULER : un bloc de bord voit moins de voisins,
# --- pas les voisins de la face opposee.
val = np.zeros((3,3,3), np.float32); val[0,0,0] = 1.0
ok = np.ones((3,3,3), bool)
somme, compte = _agreger_voisins(val, ok)
assert somme[2,2,2] == 0.0, somme[2,2,2]; n += 1
assert compte[0,0,0] == 8 and compte[1,1,1] == 27, (compte[0,0,0], compte[1,1,1]); n += 1

# --- LE controle de bout en bout : un chunk moitie empilement propre, moitie jonctions.
# --- Le classement doit designer la moitie propre. Sans lui, tout ce qui precede ne dit
# --- que « la formule calcule ce qu'elle calcule ».
C = 48
chunk = cube((C, C, C))
# moitie gauche : un empilement propre mais LEGEREMENT incline, donc planarite < 1
gi = np.indices((C, C, C // 2))
chunk[:, :, :C//2] = np.where(((gi[0] * 4 + gi[1]) % 20) < 3, 255, 0)
# moitie droite : rien, sauf UN bloc parfaitement plan, isole, entoure de vide
chunk[16:24, 16:24, 32:40][3] = 255
s = scores_du_chunk(chunk, K)
cl = classement(s, 0.02, 0.80, 6, 0.90)
forme = s["forme"]
brute = s["planarite"].reshape(forme)
eclat = brute[2, 2, 4]
propre = brute[:, :, :(C//2)//K]
# ⚠ l'eclat est le point le PLUS planaire du chunk : un argmax le choisirait
assert eclat >= float(propre.max()) - 1e-6, (eclat, float(propre.max())); n += 1
assert eclat > float(propre.mean()); n += 1
cle = np.where(cl["retenu"], cl["score"] + 1e-6 * cl["voisins"], -np.inf)
idx = int(np.argmax(cle))
iz, iy, ix = np.unravel_index(idx, forme)
assert ix < (C // 2) // K, f"la graine est tombee sur l'eclat isole (ix={ix})"; n += 1
assert not bool(cl["retenu"].reshape(forme)[2, 2, 4]), "l'eclat isole a ete retenu"; n += 1

print(f"ALL PASS (0 failures, {n} checks)")
PY

# ⚠ Cette batterie lit le SOURCE de villa, donc elle exige le depot clone. Elle est
# conditionnee plutot que rendue optionnelle : un temoin qui passe au vert quand il ne
# peut rien verifier est precisement ce que ce fichier existe pour interdire, donc
# l'absence du clone est DITE, pas avalee.
if [ -f "$ROOT/repos/villa/volume-cartographer/core/src/GrowPatch.cpp" ]; then
  run "poids GrowPatch vs source" python3 "$ROOT/src/nappe/poids_growpatch.py" --verifier
else
  printf '  ⚠ %-28s villa non clone (src/outils/clone_repos.sh) — NON VERIFIE\n' "poids GrowPatch vs source"
fi

# ⚠ La regle centrale du depot porte sur les CHIFFRES ; elle vaut aussi pour les artefacts
# qui les portent. Un fichier de mesure versionne dont le script est reste dans un terminal
# est un resultat qu'on ne peut ni rejouer, ni verifier, ni corriger.
run "artefacts : un producteur" python3 "$ROOT/src/depot/artefacts_orphelins.py" --verifier

# ⚠⚠ Deux instruments ecrits le 2026-08-20, et tous deux rendent un verdict STATISTIQUE :
# un intervalle de confiance, une correction de comparaisons multiples, une fonction de
# puissance. Une erreur dans l'un d'eux ne produit pas une erreur, elle produit un tableau
# entierement plausible. La sonde qui compte dans le premier temoin est celle qui verifie
# que la puissance tombe au niveau du test SOUS L'HYPOTHESE NULLE ; dans le second, que le
# basculement d'un verdict ne se lit pas comme une simple dispersion d'aire.
cd "$ROOT/experiments" || exit 2
run "carte : incertitude"     uv run python "$ROOT/src/commun/incertitude_carte.py" --verifier
run "tirages : dépouillement" uv run python "$ROOT/src/tables/table_tirages.py" --verifier

# ⚠⚠ Le lecteur unique des rapports `vc_tifxyz_selfcross`. Il existe parce que l'outil peut
# declarer une surface « propre » en n'ayant teste AUCUNE paire de quads : son filtre
# `--maxedge` les jette tous des que le maillage est assez grossier. Six scripts de ce
# depot lisaient ce rapport sans regarder `pairs_tested`. Le temoin verifie que le refus se
# declenche, et qu'il ne se declenche QUE la.
run "selfcross : refus du vide" python3 "$ROOT/src/nappe/lire_selfcross.py" --verifier

# ⚠ Ecrit AVANT que la campagne dense ait fini : `33` avance une prediction falsifiable
# (« l'ordre des treize ne se reproduira pas »), et un depouilleur ecrit apres coup ne
# peut plus la tester. Le temoin verifie que le fichier distingue un ordre conserve d'un
# ordre inverse -- sans quoi il rendrait le meme verdict dans les deux cas.
run "cartes : ordre conservé ?" uv run python "$ROOT/src/encre/comparer_cartes.py" --verifier

# ⚠⚠ Le seul temoin d'ici qui protege le DEPOT contre l'operateur et non contre le code.
# Editer un script pendant qu'il tourne le casse -- paye TROIS fois le 2026-08-20, alors
# que le piege est ecrit dans deux fichiers du projet. Il porte son controle NEGATIF : le
# meme script lance en direct DOIT casser, sinon la propriete qu'il verifie serait
# invérifiable sur cette machine.
cd "$ROOT" || exit 2
run "lancer : gel d'un script"  "$ROOT/src/outils/lancer.sh" --verifier
cd "$ROOT/experiments" || exit 2

# ⚠⚠ Le controle qui compte dans ce temoin est qu'un EX-AEQUO n'est pas un accord : si le
# mauvais tirage et le meilleur propre butent tous deux sur le plafond de la fenetre
# rendue, ils sont egaux par CENSURE et non par mesure. Les compter comme un accord ferait
# conclure que les deux axes s'accordent alors que rien n'a pu etre departage.
run "second axe : accord"     uv run python "$ROOT/src/tables/table_second_axe.py" --verifier

# ⚠⚠ Cet instrument existe pour REFUSER. Rapporte a l'ecart inter-spires de son rouleau,
# chaque ecart mesure devient un nombre de spires -- et les seize premieres mesures
# donnaient 0,65 a 1,25 spire, motif tres convaincant. Toutes etaient censurees ou prises
# dans une fenetre plus etroite que 1,4 spire : le motif venait de la fenetre, pas du
# papyrus. Les deux refus (censure, fenetre trop etroite) sont ce que le temoin verifie.
run "écart en spires"         uv run python "$ROOT/src/nappe/ecart_en_spires.py" --verifier

# ⚠ La grandeur qui tranche un « rien » de detecteur d'encre est l'ECART-TYPE, pas la
# mediane : un modele qui ne s'accroche a rien rend une constante, et sa mediane peut
# tomber n'importe ou. Le temoin le sonde sur deux tableaux de MEME mediane.
run "encre : σ contre témoin"  uv run python "$ROOT/src/encre/comparer_encre.py" --verifier

# ⭐⭐ Le seul juge de trace de ce depot qui n'ait NI seuil, NI verite terrain, NI echelle :
# on rend la meme surface dans des fenetres de plus en plus profondes et on regarde si la
# distance mesuree bouge. Ses TROIS REFUS sont ce que le temoin verifie -- une seule
# fenetre, deux fenetres trop proches, un ecart nul -- parce que sans eux il rendrait un
# verdict sur rien, et qu'un test incapable d'echouer est ce que ce depot traque.
run "convergence de la trace"  uv run python "$ROOT/src/commun/test_convergence.py" --verifier
run "géométrie de la chaîne"   uv run python "$ROOT/src/nappe/geometrie_chaine.py" --verifier
# ⚠ Cet outil rend un VERDICT sur une conclusion entiere — « aucun des 15 segments
# publies n'est un patch de la meme feuille ». Son temoin verifie surtout ses trois
# REFUS : un maillage illisible, un patch trop maigre, et une nappe hors de portee, que
# la premiere version confondait dans un seul `None` — et cette confusion a fait
# publier « 49 paires eloignees » pour 45 mesurees.
run "carte des segments"       uv run python "$ROOT/src/commun/carte_segments.py" --verifier
run "langue des figures"       uv run python "$ROOT/src/encre/langue.py"
# ⚠⚠ La typographie : ses temoins tournent sur des pages SYNTHETIQUES dont on a choisi
# l'interligne et l'epaisseur de trait. C'est ce qui rend l'instrument falsifiable --
# mesurer un vrai corpus ne dit jamais si la mesure est juste, faute de reference.
# Et ses controles negatifs (une marge vierge, du bruit) sont ce qui empeche
# « periodique » de vouloir dire « il y a des pixels ».
run "typographie sans lecture" uv run python "$ROOT/src/encre/typographie.py" --verifier
run "figure typographique"     uv run python "$ROOT/src/figures/figure_typographie.py" --verifier
# ⚠⚠ L'appariement surface/volume : le script de campagne prenait `head -1` de deux
# listages S3, ce qui est juste tant qu'un rouleau n'a qu'un scan et FAUX SANS UN MOT
# des qu'il en a deux. Le temoin sonde justement le cas ou les deux listes ne se trient
# pas pareil -- le seul qui justifie ce fichier.
run "appariement des scans"    uv run python "$ROOT/src/volume/apparier_volumes.py" --verifier
# ⚠⚠ La comparaison des deux plafonds : sa sonde verifie qu'un rouleau qui bute AUSSI
# sur le nouveau plafond est ECARTE du verdict. L'inclure comparerait une troncature a
# une autre et affaiblirait l'effet mesure sans qu'aucune ligne ne le signale.
run "plafond : les 2 campagnes" uv run python "$ROOT/src/graine/comparer_plafond.py" --verifier
run "figure du plafond"        uv run python "$ROOT/src/figures/figure_plafond.py" --verifier
run "campagne des graines"     uv run python "$ROOT/src/figures/figure_graines.py" --verifier
run "écarts entre segments"    uv run python "$ROOT/src/figures/figure_segments.py" --verifier
# ⚠⚠ Le temoin negatif : sa garde REFUSE de conclure quand le controle POSITIF est plat.
# Sans elle, deux cartes plates rendent un rapport proche de 1 et le verdict se lirait
# « le temoin trompe le detecteur » alors qu'il veut dire « le detecteur est eteint des
# deux cotes ». Et sa sonde verifie qu'une experience NON CONCLUANTE reste imprimable :
# la premiere version la faisait sortir par le chemin d'erreur, sans ecrire son JSON.
run "témoin négatif"           uv run python "$ROOT/src/encre/temoin_negatif.py" --verifier
run "figure du témoin négatif" uv run python "$ROOT/src/figures/figure_temoin_negatif.py" --verifier
# ⚠⚠ La derive avec la profondeur : sa sonde verifie qu'une trace CENSUREE est ecartee de
# la derive. La compter ferait mesurer le deplacement du PLAFOND en croyant mesurer la
# surface -- et comme le plafond monte avec la profondeur, l'erreur irait toujours dans le
# meme sens, donc ressemblerait a un effet. Et sa fixture a TROIS traces et pas deux : a
# deux, l'appariement positionnel rend le meme nombre que l'appariement par identite, donc
# la sonde ne pouvait pas echouer.
run "dérive avec la profondeur" uv run python "$ROOT/src/graine/derive_avec_profondeur.py" --verifier
run "figure de la dérive"      uv run python "$ROOT/src/figures/figure_derive_profondeur.py" --verifier
# ⚠⚠ L'eligibilite : sa sonde verifie qu'un candidat SANS prediction de surface est ECARTE
# et pas classe dernier -- la campagne de graines ne peut structurellement pas y tourner, et
# le garder ferait recommander une experience irrealisable. Et une sonde sur le VRAI fichier
# de resultat, parce qu'une fixture ecrite d'apres le code ne prouve que leur accord : c'est
# comme ca qu'une cle inexistante a rendu « 0 rouleau tracable » et un verdict confiant.
run "où monter l'expérience"   uv run python "$ROOT/src/graine/eligibilite_aval.py" --verifier
run "figure de l'éligibilité"  uv run python "$ROOT/src/figures/figure_eligibilite.py" --verifier
# ⚠⚠ L'audit des profils plats : sa sonde verifie qu'une serie dont TOUTES les lectures sont
# le bord de la fenetre a un α mesure EGAL a son α de plafond -- donc que α ne separe pas
# « le pic recule » de « il n'y avait pas de pic ». Et son controle, que la moitie
# rassurante tienne : une serie qui converge en est loin par construction.
run "audit des profils plats"  uv run python "$ROOT/src/commun/audit_profils_plats.py" --verifier
# ⚠ L'excision : sa sonde refuse de dessiner si les deux populations sont le MEME
# echantillon. Deux resumes identiques a la decimale sont le resultat -- et aussi ce a quoi
# ressemble une colonne recopiee deux fois.
run "excision : deux populations" uv run python "$ROOT/src/figures/figure_excision.py" --verifier
# ⚠⚠ Le garde-fou des chiffres se garde lui-meme. Il n'avait AUCUN auto-test : il protege
# les 140 chiffres publies du depot et rien ne verifiait qu'il sait encore les trouver -- ni,
# surtout, qu'il sait ECHOUER. Sa sonde exige qu'un chiffre FAUX ne soit pas trouve.
run "le garde-fou se garde"    uv run python "$ROOT/src/depot/verifier_chiffres.py" --verifier
# ⚠⚠ Le chien de garde des rendus. Sa sonde la plus utile est la COURSE : un rendu qui finit
# ENTRE deux sondages etait declare abandonne, donc il aurait frappe n'importe quel rendu
# court -- c'est-a-dire les bons. Et son controle exige qu'un processus qui travaille ne soit
# PAS tue : un garde qui tue ce qui va bien est la pire panne possible.
run "chien de garde des rendus" "$ROOT/src/outils/rendre_surveille.sh" --verifier
# ⚠⚠ Le 2×2 des predictions. Ses deux sondes qui comptent sont SYMETRIQUES : un effet franc
# de prediction doit etre attribue a la prediction, et un effet franc d'ENDROIT a l'endroit.
# Sans la seconde, un instrument qui dirait toujours « prediction » passerait la premiere.
# Et il refuse quand l'ecart entre cellules est sous le bruit de tirage mesure -- le traceur
# est un tirage, et la meme graine a rendu +0,89 puis +1,12.
run "2×2 des prédictions"      uv run python "$ROOT/src/encre/comparer_predictions.py" --verifier
run "figure des deux pannes"   uv run python "$ROOT/src/figures/figure_deux_pannes.py" --verifier
# ⚠⚠ Les images des documents. Un lien vers une image absente ne casse rien a l'execution :
# il s'affiche avec une icone brisee, et personne ne le voit tant que personne n'ouvre le
# document. ⚠ Le test utilise `-s` et non `-e` : un rendu interrompu laisse un fichier de
# zero octet, et un lien vers un fichier vide s'affiche exactement comme un lien vers rien.
run "images des documents"     "$ROOT/src/outils/images_des_docs.sh" --verifier
run "liens d'images valides"   "$ROOT/src/outils/images_des_docs.sh"
# ⚠⚠ La figure du 2×2. Sa sonde de linearite a attrape un vrai defaut d axe : `int` tronque,
# donc le milieu exact tombait un pixel a gauche quand la division ne se ferme pas en
# binaire. Placer un point sur un axe est un ARRONDI.
run "figure du 2×2"            uv run python "$ROOT/src/figures/figure_2x2.py" --verifier
# ⚠⚠ Les candidats de graine. Sa sonde la plus utile est celle du PLANCHER : a huit points,
# la correlation detectable a 80 % de puissance depasse 0,84, donc un rho moyen n est pas une
# absence d effet mais une absence de puissance. Le fichier refuse de conclure dessus, et le
# controle exige qu une correlation PARFAITE, elle, passe -- sinon le refus ne vaut rien.
run "candidats de graine"      uv run python "$ROOT/src/graine/comparer_candidats.py" --verifier
# ⚠⚠ L effet du plafond de generations. Sa sonde centrale est un CONTROLE : la meme
# variation d alpha doit etre dite « stable » sous le bruit du tireur et « effet » sous un
# bruit plus fin. Si les deux donnaient le meme verdict, le bruit ne servirait a rien et le
# fichier ne ferait que rehabiller une soustraction.
run "effet du plafond"         uv run python "$ROOT/src/graine/effet_du_plafond.py" --verifier
# ⚠⚠ Les deux campagnes de trace. La sonde la plus utile du traceur partage est le CODE de
# refus : ${X:?} sortirait en 1, indistinguable d une panne, et un appelant qui trie les deux
# lirait le mauvais cas. Celle du plafond a son propre motif COUPE EN DEUX, sans quoi la
# sonde se matcherait elle-meme -- pkill -f sous un nouveau costume.
run "traceur d une graine"     "$ROOT/src/outils/tracer_une_graine.sh" --verifier
run "campagne du plafond"      "$ROOT/src/outils/plafond_generations.sh" --verifier
# ⚠⚠ La figure des candidats. Ses deux sondes de mise en page attrapent deux defauts
# DIFFERENTS, et le premier controle que j avais ecrit n attrapait que l un des deux :
# retrecir l ecart entre colonnes retrecit AUSSI le cadre, donc tout reste dedans en se
# recouvrant. Il faut mesurer la place libre, pas seulement le hors-cadre.
run "figure des candidats"     uv run --project "$ROOT" python "$ROOT/src/figures/figure_candidats.py" --verifier
# ⚠⚠ L etalonnage du rendu. Sa sonde centrale n est pas une performance : c est que la
# sortie ne BOUGE PAS entre les reglages, et que le depouilleur REFUSE de parler de temps
# quand l etendue dans une meme valeur depasse l ecart entre valeurs -- sans quoi la serie
# publierait la meteo du reseau.
run "étalon du rendu"          "$ROOT/src/outils/etalonner_rendu.sh" --verifier
run "effet du cache"           uv run python "$ROOT/src/graine/effet_du_cache.py" --verifier
run "figure de l'étalon"       uv run --project "$ROOT" python "$ROOT/src/figures/figure_etalon_rendu.py" --verifier
run "profileur d'une surface" "$ROOT/src/outils/profiler_une_surface.sh" --verifier
run "contrôle de résolution"   "$ROOT/src/outils/controle_resolution.sh" --verifier
# ⚠⚠ Le lecteur d en-tete TIFF, ecrit trois fois a la main dans des commandes jetables avant
# de devenir du code. Sa sonde centrale distingue « inacheve » de « illisible » : un rendu
# interrompu laisse des tranches PRE-ALLOUEES dont aucun decodeur ne veut, et les confondre
# ferait perdre l information qu on cherchait.
run "dimensions d'un TIFF"     uv run python "$ROOT/src/volume/dimensions_tiff.py" --verifier
# ⚠⚠ La conversion en image. Sa sonde centrale REFUSE une sortie sans variete : un
# `ffmpeg -i tranche.tif sortie.png` a rendu du noir, silencieusement et en code zero, sur
# un fichier dont 74,5 %% des pixels sont non nuls -- on a failli en conclure que le rendu
# n avait rien produit.
run "tif vers png"             uv run --project "$ROOT" python "$ROOT/src/volume/tif_en_png.py" --verifier
run "aperçu d'une surface"     "$ROOT/src/outils/apercu_surface.sh" --verifier
run "deux surfaces côte à côte" uv run --project "$ROOT" python "$ROOT/src/figures/figure_deux_surfaces.py" --verifier
# ⚠⚠ Le format des messages de commit. 108 commits d affilee se sont ecartes du format du
# depot sans que rien ne le signale : une convention qu on se rappelle est une convention
# qu on oublie. Trois regles, chacune enfreinte au moins une fois.
run "format des commits"       "$ROOT/src/outils/format_des_commits.sh" --verifier
# ⚠⚠ L appariement du README : ses commandes doivent EXISTER et, quand elles sont courtes
# et hors ligne, TOURNER. Un exemple perime est la premiere cause de perte de confiance
# dans une doc, et il ne se voit jamais a la relecture -- le chemin a change, la prose non.
run "commandes du README"      "$ROOT/src/outils/readme_apparie.sh" --verifier
# ⚠⚠ Le test qu un critere candidat doit passer avant qu on ecrive un seuil dessus. Sa
# sonde centrale est un REFUS : une grandeur collee a sa borne aux deux profondeurs rendrait
# beta = 0, donc « propriete de la surface », alors qu elle dit seulement qu elle ne peut pas
# monter plus haut. Mesure : 104 series sur pic_intensite_median.
run "critere relatif"          uv run --project "$ROOT" python "$ROOT/src/graine/critere_relatif.py" --verifier
# ⚠⚠ Les scenes pedagogiques. Cette batterie n etait PAS lancee, et elle avait quelque chose
# a dire : une legende posee a la main dans la video 2. Une sonde qu on n execute jamais est
# une sonde qui n existe pas.
run "scenes pedagogiques"      "$ROOT/apprendre/rendre.sh" --verifier
# ⚠⚠ Situer nos traces a la geometrie d un corpus. Ses sondes centrales portent sur la
# SOUS-FENETRE : elle doit etre centree (161 couches lues sur 109 laissent 26 de chaque
# cote) et la couche tracee doit etre le milieu de la SOUS-fenetre, pas de la pile -- la
# donner en coordonnees de pile decalerait le profil de vingt-six couches sans rien dire.
run "situer nos traces"        "$ROOT/src/outils/situer_nos_traces.sh" --verifier
# ⚠⚠ Le decoupage d un maillage publie a la taille des notres. Trois refus y sont sondes
# avec leur cas negatif : une bbox recopiee (deux morceaux differents DOIVENT avoir deux
# bboxes), un morceau troue, et une repartition qui entasse les morceaux en haut de grille.
# ⚠⚠ L INSTRUMENT QUI JUGE TOUT LE RESTE, et qui n avait AUCUNE batterie. Il produit chaque
# chiffre de relief du projet, et son test de matiere etait relatif au maximum de la pile --
# donc une pile ENTIEREMENT NOIRE le satisfaisait entierement, et cinq rendus vides ont ete
# publies comme « surfaces parfaitement plates ». Les trois piles de controle sont
# fabriquees par la batterie : noire (refusee), uniforme mais ECLAIREE (plate), et avec une
# bosse (du relief, pic au bon endroit).
# ⚠⚠ Le niveau de pyramide d un maillage. Un tifxyz porte des INDICES DE VOXEL, et un indice
# ne veut rien dire sans le volume qui le numerote -- ni `meta.json`, ni `scale`, ni le
# fichier de parametres du traceur ne le disent. Cinq traces `m7` ont ete tracees au niveau 2
# puis rendues au niveau 0 : 161 images entierement noires, lues comme « surface plate ».
# Les refus sont sondes autant que la reponse : rapport anisotrope, facteur non puissance de
# deux, maillage plus grand que le volume.
# ⚠⚠ Y a-t-il quoi que ce soit dans ces piles. Le declencheur du 2026-08-24 n a pas ete une
# relecture mais une TAILLE DE FICHIER : 7,6 Mo contre 562 Mo pour des images de memes
# dimensions. La sonde qui compte le plus est la LIMITE de l echantillonnage, sondee plutot
# qu affirmee : une pile dont une seule couche porte quelque chose est declaree vide par un
# pas qui saute cette couche, et le taire ferait de `--pas` un reglage qui change le verdict
# sans le dire.
# ⚠⚠ Y a-t-il de la matiere a CETTE coordonnee. Une trace commence par une graine, qui est
# une coordonnee, et une coordonnee ne veut rien dire sans le volume qui la numerote. Les
# temoins sont ARITHMETIQUES et ne touchent pas le reseau : une batterie qui dependrait du
# depot serait rouge des que la connexion tombe, donc elle finirait ignoree -- et c est la
# qu elle cesse d etre une batterie.
# ⚠ La figure des piles vides. Sa sonde centrale est le REPLI des titres : le premier tirage
# laissait une legende passer par-dessus la suivante, donc deux panneaux cessaient de dire ce
# qu ils montraient. Et le cadre rouge n apparait QUE s il y a une pile vide -- cas negatif
# sonde, sinon la figure serait trois vignettes sans verdict.
# ⚠⚠ La figure feuille-ou-tranche, nee d une question de l auteur : « un jour on aura une vue
# des vraies feuilles aplaties ? ». Sa sonde centrale est le REFUS de deux etendues
# differentes -- comparer une tuile de 512 voxels a une de 2400 ferait passer une difference
# d echelle pour une difference de surface, ce qui est la faute que tout ce depot traque.
# ⚠⚠ Le registre des murs et de leurs causes. La garde qui compte : chaque ligne pointe vers
# un document qui doit contenir ENCORE son ancre. C est ce qui empeche ce tableau de devenir
# `EXTRACTION.md` -- une table tenue a la main qui derive en silence de ce qu elle decrit.
# Sonde : remplacer une ancre par une chaine inventee fait rougir la batterie.
# ⚠⚠ La figure de l espace de causes. Son controle central : ses comptes doivent etre ceux du
# TABLEAU -- deux dessins d un meme registre libres de diverger, c est la panne que le `55`
# existe pour empecher. ⚠ Et la table de traduction est appliquee du plus long au plus court :
# sans ca « eliminee » se substitue a l interieur de la note de bas de page, qui ressort a
# moitie traduite.
run "figure des murs"          uv run --project "$ROOT" python "$ROOT/src/figures/figure_murs.py" --verifier
run "murs et causes"           uv run --project "$ROOT" python "$ROOT/src/depot/murs_et_causes.py" --verifier
run "figure feuille/tranche"   uv run --project "$ROOT" python "$ROOT/src/figures/figure_feuille_ou_tranche.py" --verifier
# ⚠ La tuile de reference publiee. Temoins ARITHMETIQUES : une batterie qui appellerait le
# depot serait rouge des que la connexion tombe, donc elle finirait ignoree.
run "tuile publiee"            uv run --project "$ROOT" python "$ROOT/src/volume/tuile_surface_publiee.py" --verifier
run "figure des piles vides"   uv run --project "$ROOT" python "$ROOT/src/figures/figure_piles_vides.py" --verifier
# ⚠⚠ Peut-on semer ici. Le sens compte : on part d une coordonnee du SCAN et on demande a
# chaque prediction ce qu elle en dit DANS SON REPERE, le niveau etant lu dans son nom
# (`-L0-`, `-L2-`). L autre sens obligerait a deviner le niveau, ce qui est l erreur d origine.
# ⚠ La regle d admissibilite porte sur le BLOC et pas sur le voxel exact : la graine `ps256`
# qui a produit huit traces avec matiere lit ZERO a son voxel, 255 autour.
# ⚠⚠ La projection tangentielle -- ce que `44` §7 nommait comme la seule chaine jamais
# tentee. Sonde centrale : l axe le plus long est mesure par CHEMIN PARCOURU et non par somme
# des tangentes locales, qui vaut « points fois pas » dans les deux directions et ne
# departage rien. Et la difference finie ne doit pas enjamber un trou : elle aurait la bonne
# forme et le mauvais sens.
# ⚠⚠ L enchainement de la projection, avec son TEMOIN : le meme deplacement total franchi
# d un seul bond. Sans lui, une chaine qui tient ne prouverait rien -- elle pourrait tenir
# parce que la distance est courte. Sonde aussi que chaque maillon part du PRECEDENT, sinon
# ce sont des projections independantes sous un autre nom.
run "chaîne tangentielle"      "$ROOT/src/outils/chainer_tangentiel.sh" --verifier
run "recalage de la chaine"   "$ROOT/src/outils/recalage_de_la_chaine.sh" --verifier
run "projection tangentielle"  uv run --project "$ROOT" python "$ROOT/src/nappe/projeter_tangentiel.py" --verifier
run "ecart de maillages"       uv run --project "$ROOT" python "$ROOT/src/nappe/ecart_de_maillages.py" --verifier
run "region locale"            uv run --project "$ROOT" python "$ROOT/src/volume/region_locale.py" --verifier
run "recalage sur matiere"     uv run --project "$ROOT" python "$ROOT/src/nappe/recaler_sur_la_matiere.py" --verifier
# ⚠⚠ Ces deux-la servent le MENAGE, pas la mesure du rouleau. `permalien` garantit qu'un
# document qui cite un fichier retire continue de pointer vers quelque chose : son invariant
# est que le commit vise soit sur le DISTANT, sinon le lien serait mort pour tout le monde
# sauf cette machine. ⚠ Le depot etant PRIVE, l'URL rend 404 sans session -- d'ou le controle
# qu'elle porte le commit et le chemin verbatim, pour que `git show` s'en deduise hors ligne.
# ⚠⚠ `poids_recuperable` existe parce que `du` a MENTI d'un facteur quatre : uv installe en
# liens durs vers son cache, donc supprimer un venv ne libere pas ses octets tant qu'un autre
# nom les tient. Le compte de liens est la seule chose qui repond.
run "permalien de document"    uv run --project "$ROOT" python "$ROOT/src/depot/permalien.py" --verifier
run "poids recuperable"        uv run --project "$ROOT" python "$ROOT/src/depot/poids_recuperable.py" --verifier
# ⚠⚠ Le point d'entree de l'INFERENCE, auto-teste SANS torch et SANS GPU. C'est ce qui a
# permis de supprimer `inference/` : le temoin CPU est devenu un MODE (`--device cpu`) au lieu
# d'un second environnement, et la regle qui le gouverne -- « auto » retombe, « xpu » REFUSE --
# est une fonction pure qui prend la disponibilite en argument, donc elle se verifie ici.
run "appareil d'inference"     uv run --project "$ROOT" python "$ROOT/inference_xpu/src/infer_ink.py" --verifier
# ⚠⚠ Le point d entree du depot. Ce qu il garantit tient en une phrase : `lplv <verbe> --help`
# EXECUTE le module avec `--help` au lieu de re-decrire son argparse, donc l aide ne peut pas
# perimer. Ses trois controles porteurs : un nom revendique deux fois est REFUSE (une ambiguite
# silencieuse lancerait celui que le systeme de fichiers a mis devant), tout ce qui suit le
# verbe passe VERBATIM (sinon il faudrait ecrire une seconde aide a cote), et un fichier en `_`
# n est pas un verbe.
run "point d entree lplv"      uv run --project "$ROOT" python "$ROOT/src/depot/lplv.py" --verifier
run "recensement des verbes"   uv run --project "$ROOT" python "$ROOT/src/figures/figure_verbes.py" --verifier
# ⚠⚠ L outil du grand rangement. Son invariant : apres application, AUCUNE citation d un
# ancien chemin ne subsiste. ⚠ La premiere version de ce controle etait une TAUTOLOGIE --
# elle relisait exactement les fichiers que la reecriture venait de traiter, donc elle ne
# pouvait rien trouver. Deux sondes l ont montre en ne faisant echouer aucun controle. La
# recherche porte desormais PLUS LARGE que la reecriture, et un chemin ASSEMBLE a l execution
# est nomme plutot que tu, parce qu aucune reecriture textuelle ne peut le voir.
run "deplacement de fichiers"  uv run --project "$ROOT" python "$ROOT/src/depot/deplacer.py" --verifier
# ⚠⚠ La campagne de portee. Ses sondes portent sur la COLONNE et pas sur le mot : l en-tete a
# gagne « mediane » pendant que l extraction rendait `bloc_absent`, et un grep du mot restait
# vert. ⚠ Et dans un `chk` qui est une FONCTION, $1 est l argument de la fonction, pas la
# colonne -- le symptome « $3: unbound variable » ne ressemble pas a la cause.
# ⚠⚠ La figure de la portee. Son controle central : elle ANNONCE une degradation monotone,
# donc elle doit refuser de le dire si les points ne le sont pas -- `monotone()` est sonde
# dans les deux sens. ⚠ Et le debordement des libelles est verifie dans LES DEUX LANGUES :
# « peak at the stack edge » est plus long que son equivalent francais, donc une legende qui
# tient en francais peut sortir du canevas une fois traduite.
run "figure de la portée"      uv run --project "$ROOT" python "$ROOT/src/figures/figure_portee.py" --verifier
run "portée tangentielle"      "$ROOT/src/outils/portee_tangentielle.sh" --verifier
run "graine admissible"        uv run --project "$ROOT" python "$ROOT/src/graine/graine_admissible.py" --verifier
run "matiere au point"         uv run --project "$ROOT" python "$ROOT/src/nappe/matiere_au_point.py" --verifier
run "matiere des piles"        uv run --project "$ROOT" python "$ROOT/src/nappe/matiere_des_piles.py" --verifier
run "niveau du maillage"       uv run --project "$ROOT" python "$ROOT/src/nappe/niveau_du_maillage.py" --verifier
run "profil de profondeur"     uv run --project "$ROOT" python "$ROOT/src/volume/depth_profile.py" --verifier
run "decouper un tifxyz"       uv run --project "$ROOT" python "$ROOT/src/nappe/decouper_tifxyz.py" --verifier
# ⚠⚠ Le temoin positif de notre chaine de rendu. Ses sondes portent autant sur des ABSENCES
# que sur des presences -- ce fichier ne doit contenir ni l invocation du moteur ni le calcul
# de la sous-fenetre, sinon la comparaison mesurerait la difference des scripts. ⚠ Les deux
# motifs interdits y sont composes a l execution : ecrits en clair ils se matcheraient
# eux-memes, ce qui est la forme MIROIR de l auto-match et echoue toujours.
run "temoin du rendu"          "$ROOT/src/outils/temoin_du_rendu.sh" --verifier
# ⚠ La figure de calibration. Sa sonde centrale est le seuil venu d AILLEURS : il doit etre
# dessine, et la figure doit DIRE qu aucun point ne l atteint plutot que de laisser un vide
# muet. Sa seconde sonde est la bande brute, verifiee pixel pour pixel entre les deux
# langues : les libelles intraduisibles n entrent pas dans le garde de langue, ils sont
# dessines a cote.
run "figure de calibration"    uv run --project "$ROOT" python "$ROOT/src/figures/figure_calibration.py" --verifier
# ⚠⚠ La calibration d un corpus. Ses sondes centrales sont des REFUS : deux geometries dans
# un meme fichier (deux balayages concatenes ne calibrent rien), une geometrie ni lue ni
# declaree, et une geometrie declaree a la main qui doit se signaler comme telle. Ecrit
# apres avoir declare « 65 couches » sur un corpus qui en a 109.
run "calibration du corpus"    uv run --project "$ROOT" python "$ROOT/src/graine/calibration_corpus.py" --verifier
# ⚠⚠ L effet de la TAILLE DE FENETRE sur le relief. Sa sonde centrale est le SIGNE de
# l exposant : il doit etre NEGATIF (une fenetre plus large moyenne plus, donc ecrase
# l amplitude), et son ampleur comparable a celle de la profondeur -- c est ce qui justifie
# d avoir retire du README public un repere transporte d un instrument a l autre.
run "effet de la taille"       uv run --project "$ROOT" python "$ROOT/src/graine/effet_taille_fenetre.py" --verifier
# ⚠⚠ Les APPUIS de la pente. Sa sonde centrale est le SIGNE : un appui etroit au bord rend
# alpha majorant, un appui large le rend minorant, et inverser les deux ferait tenir
# exactement les verdicts qui tombent. Mesure : 20 series rendaient l identite +1,0135 du
# couple de fenetres 41c/161c, la meme valeur a la quatrieme decimale.
run "appuis de la pente"       uv run --project "$ROOT" python "$ROOT/src/graine/appui_de_pente.py" --verifier
# ⚠⚠ Le choix du couple de fenetres. Sa sonde centrale est le +1 : la couche tracee est au
# CENTRE, donc doubler la demi-fenetre ne double pas la fenetre (81/41 = 1,976) et le couple
# evident est refuse. Sa seconde sonde est l appariement inter-niveaux, qui doit etre
# DECLARE : une premiere version balayait l arbre et comparait deux traces etrangeres.
run "fenêtre utilisable"       uv run --project "$ROOT" python "$ROOT/src/graine/fenetre_utilisable.py" --verifier
# ⚠⚠ Les renvois de l article. Typst numerote seul, mais le TEXTE d un `#link` est ecrit a
# la main : inserer une sous-section decale la numerotation sans toucher un de ces textes.
# Mesure le 2026-08-23 : SIX renvois sur trente-deux pointaient ailleurs, dont un qui
# envoyait du choix de graine (5.3) vers le temoin negatif (6.4).
run "renvois de l'article"     uv run --project "$ROOT" python "$ROOT/src/depot/renvois_article.py" --verifier
# ⚠⚠ La figure du contraste. Sa sonde centrale est que le constat porte : AUCUNE serie
# convergente sous le plancher. Sa seconde est l amplitude NULLE, qui n a pas de logarithme
# et doit etre posee a part et comptee -- l ecraser sur la plus petite valeur non nulle
# ferait passer « rien du tout » pour « presque rien ».
run "figure du contraste"      uv run --project "$ROOT" python "$ROOT/src/figures/figure_contraste.py" --verifier
# ⚠ La figure du plancher de detection. Sa sonde centrale est la COULEUR : les points sous
# le plancher et ceux qui le degagent n'ont pas la meme, sinon le lecteur cherche le
# plancher au lieu de le voir. Sa seconde sonde exige que la cible tombe ENTRE les deux
# fenetres mesurees -- c'est ce que le pied de la figure affirme.
run "figure de la fenêtre"     uv run --project "$ROOT" python "$ROOT/src/figures/figure_fenetre.py" --verifier
# ⚠ La figure des appuis. Sa sonde centrale est que les DEUX formes de domaine apparaissent,
# une par panneau : un coin dit « une part des pentes est exclue », un lavis dit « aucune ».
# Compter des traits laisserait passer deux panneaux dessines pareil.
run "figure des appuis"        uv run --project "$ROOT" python "$ROOT/src/figures/figure_appuis.py" --verifier
# ⚠⚠ La figure de la pyramide. Sa sonde centrale est celle de l AXE : au niveau 1, 21
# tranches de 4,8 µm couvrent ce que 41 de 2,4 couvrent. Tracer contre le compte de tranches
# decalerait les deux series d un facteur deux et montrerait un desaccord qui n existe pas.
run "figure de la pyramide"    uv run --project "$ROOT" python "$ROOT/src/figures/figure_pyramide.py" --verifier
run "figure de l emballement"  uv run --project "$ROOT" python "$ROOT/src/figures/figure_emballement.py" --verifier
run "figure matiere chaine"    uv run --project "$ROOT" python "$ROOT/src/figures/figure_matiere_de_la_chaine.py" --verifier
# ⚠⚠ CES SIX BATTERIES N ONT JAMAIS TOURNE, et le garde-fou de la fin de ce fichier existe
# pour ca. Quatre d entre elles imprimaient « tous les temoins passent » au lieu de
# « ALL PASS » : les enregistrer sans corriger leur verdict n aurait rien lance non plus. Un
# controle que personne ne lance est une verification incapable d echouer -- exactement ce que
# ce depot traque partout ailleurs.
run "couche de rendu"          uv run --project "$ROOT" python "$ROOT/src/volume/couche_de_rendu.py" --verifier
run "derive ou loterie"        uv run --project "$ROOT" python "$ROOT/src/graine/derive_ou_loterie.py" --verifier
run "juge a un rendu"          uv run --project "$ROOT" python "$ROOT/src/encre/juge_a_un_rendu.py" --verifier
run "rogner la nappe"          uv run --project "$ROOT" python "$ROOT/src/nappe/rogner_nappe.py" --verifier
run "table de la chaine"       uv run --project "$ROOT" python "$ROOT/src/tables/table_chaine.py" --verifier
run "faire la release"         "$ROOT/src/outils/faire_la_release.sh" --verifier

run "graine : les 2 versions"  uv run python - <<'PY'
import sys
import pathlib as _p; sys.path[:0]=[str(x) for _b in ('src','../src') for x in _p.Path(_b).glob('*') if x.is_dir()]
sys.path.insert(0, '../tracecheck')
import numpy as np
import trouver_graine as interne
import tracecheck as public

# ⚠⚠ Deux implementations du MEME critere existent EXPRES : l'une interne, l'autre dans
# l'outil public, qui doit tenir sur numpy et urllib seuls. Deux implementations d'une
# meme idee ne restent pas egales -- ce depot l'a paye avec la boucle de creatures de
# mapview, qui avait derive DANS LES DEUX SENS. Ce temoin les epingle l'une a l'autre sur
# des blocs synthetiques, hors ligne.
n = 0
K = 8
rng = np.random.default_rng(7)
cas = []
b = np.zeros((K, K, K), np.uint8); b[4] = 255; cas.append(('un plan', b))
b = np.zeros((K, K, K), np.uint8); b[2] = 255; b[6] = 255; cas.append(('deux paralleles', b))
b = np.zeros((K, K, K), np.uint8); b[4] = 255; b[:, 4, :] = 255; cas.append(('jonction', b))
cas.append(('bruit', (rng.random((K, K, K)) < 0.15).astype(np.uint8) * 255))
C = 24
g = np.indices((C, C, C))
cas.append(('empilement incline', np.where(((g[0] * 4 + g[1]) % 20) < 3, 255, 0).astype(np.uint8)))

for nom, bloc in cas:
    a = interne.scores_du_chunk(bloc, K)
    q = public.planarity_map(bloc, K)
    assert np.allclose(a['planarite'], q['planarity'], atol=1e-6), nom
    n += 1
    assert np.allclose(a['occupation'], q['occupancy'], atol=1e-6), nom
    n += 1

# et le voxel rendu doit etre le MEME, pas seulement un voxel allume
bord = np.zeros((K, K, K), np.uint8); bord[1] = 255
assert interne.voxel_allume(bord, K, 0, 0, 0) == public.lit_voxel(bord, K, 0, 0, 0)
n += 1

# et l'agregation de voisinage aussi -- c'est elle qui decide du classement
val = rng.random((4, 4, 4)).astype(np.float32)
ok = rng.random((4, 4, 4)) > 0.3
sa, ca = interne._agreger_voisins(val, ok)
sq, cq = public._neighbourhood(val, ok)
assert np.allclose(sa, sq) and (ca == cq).all()
n += 1

print(f'ALL PASS (0 failures, {n} checks)')
PY

# ⚠ Ces deux-la tournaient depuis `inference/` jusqu'au 2026-08-25, au motif que c'etait le
# seul environnement porteur de Pillow -- `temoins.sh` s'execute depuis `experiments/` pour le
# reste. Le motif etait FAUX (la racine declare pillow>=10.0) et NUISIBLE : `inference/`
# n'avait pas `numcodecs`. Ils tournent depuis la RACINE, qui porte PIL, numcodecs, numpy,
# scipy et tifffile -- strictement plus que ce que `inference/` portait.
printf '  %-30s ' "marche sur nappe"
if (cd "$ROOT" && uv run python "$ROOT/src/commun/suivre_nappe.py" --verifier) >/tmp/nappe.log 2>&1; then
  printf '✅ %s\n' "$(grep -c '✅' /tmp/nappe.log) checks"
else
  printf '❌ ECHEC\n'; sed 's/^/       /' /tmp/nappe.log | tail -6; FAIL=$((FAIL + 1))
fi

printf '  %-30s ' "mosaique : assemblage"
if (cd "$ROOT" && uv run python "$ROOT/src/volume/assembler_mosaique.py" --verifier) >/tmp/mos.log 2>&1; then
  printf '✅ %s\n' "$(grep -c '✅' /tmp/mos.log) checks"
else
  printf '❌ ECHEC\n'; sed 's/^/       /' /tmp/mos.log | tail -6; FAIL=$((FAIL + 1))
fi

# ⚠ Celui-ci n'est pas une batterie d'assertions mais un GARDE-FOU de fraicheur : il
# recalcule les chiffres publies depuis leurs JSON et les cherche dans les documents.
printf '  %-30s ' "chiffres de la soumission"
# ⚠⚠ TOUS les documents, pas une liste tenue a la main. La version precedente en nommait
# neuf, choisis un par un -- donc la couverture du garde-fou dependait de quelqu'un qui se
# souvienne d'ajouter un nom. Elle a dument echoue : les chiffres de `43` (la chaine des
# spires) etaient recalcules et cherches dans des documents qui ne les citent pas, et
# rapportes « absents » pendant des jours. Meme classe de panne qu'une sentinelle qu'il faut
# deplacer a chaque ajout : le remede n'est pas de la deplacer mieux, c'est de ne plus avoir
# a le faire.
# ⚠⚠ `--soumission` ajoute le controle que la recherche globale NE PEUT PAS faire : les
# chiffres du dossier sont recopies a l'anglaise depuis une prose francaise, donc « le
# chiffre existe quelque part » est satisfait par le document SOURCE et une faute de frappe
# dans le dossier passe. Sonde faite : transposer 12,97 en 12,79 dans une copie fait
# echouer le controle, ce qu'il ne faisait pas avant.
# ⚠ `--article` fait la meme chose pour `article/article.typ`, qui recopie lui aussi ses
# chiffres a l'anglaise et part vers un lectorat qui ne peut pas les recouper. Sa section
# « Reproducibility » AFFIRME que chaque nombre est cherche litteralement dans sa source :
# sans ce controle, l'affirmation serait flatteuse au lieu d'etre vraie.
if uv run python "$ROOT/src/depot/verifier_chiffres.py" "$ROOT"/docs/*.md \
     "$ROOT/article/article.typ" \
     --soumission "$ROOT/docs/21_texte_de_soumission.md" \
     --article "$ROOT/article/article.typ" >/tmp/chiffres.log 2>&1; then
  printf '✅ %s\n' "$(grep -c '✅' /tmp/chiffres.log) chiffres retrouves"
else
  printf '❌ ECHEC\n'; sed 's/^/       /' /tmp/chiffres.log | tail -6; FAIL=$((FAIL + 1))
fi

# ⚠⚠ ET LE VRAI CONTROLE, sur le document lui-meme. La batterie `--verifier` ci-dessus ne
# teste que l'instrument ; sans cette ligne, il ne regarderait JAMAIS l'article, et une
# batterie verte voudrait dire « le compteur de sections fonctionne » et rien de plus.
printf '  %-30s ' "renvois de l'article"
if uv run --project "$ROOT" python "$ROOT/src/depot/renvois_article.py" \
     "$ROOT/article/article.typ" --pdf "$ROOT/article/article.pdf" \
     --readme "$ROOT/article/README.md" > /tmp/renvois.log 2>&1; then
  printf '✅ %s\n' "$(grep -o '[0-9]* renvoi(s) de section' /tmp/renvois.log | head -1)"
else
  printf '❌ ECHEC\n'; sed 's/^/       /' /tmp/renvois.log | tail -8; FAIL=$((FAIL + 1))
fi

# ⚠⚠ GARDE DE SYNTAXE DES FORMULES. Les documents sont du Markdown : les maths s'y ecrivent
# entre dollars, jamais avec le marqueur Doxygen (arobase, f, dollar), qui s'affiche
# litteralement au lieu de rendre une formule. Repris par l'auteur le 2026-08-23.
#
# ⚠⚠ ET LE MOTIF N'EST PAS ECRIT EN CLAIR DANS CE FICHIER, deliberement. Une premiere
# version le citait dans son propre commentaire, donc le grep matchait `temoins.sh` et la
# garde etait rouge en permanence -- le piege « une sonde qui scanne son propre fichier se
# matche elle-meme », paye six fois dans ce depot. Le remede n'est PAS d'exclure ce fichier
# du balayage (ce qui l'aveuglerait a une vraie occurrence ici) : c'est de composer la
# chaine a l'execution, pour qu'elle n'existe nulle part dans la source.
printf '  %-30s ' "syntaxe des formules"
DOXY=$(printf '@%s$' f)
FORM=$(grep -rlnF --include='*.md' --include='*.py' --include='*.sh' -- "$DOXY" \
       "$ROOT/docs" "$ROOT/src" "$ROOT/apprendre" "$ROOT/README.md" \
       2>/dev/null | grep -v '/\.git/' | sed "s#$ROOT/##" | tr '\n' ' ')
if [ -z "$FORM" ]; then
  printf '✅ aucun marqueur Doxygen dans les documents\n'
else
  printf '⚠ marqueur Doxygen au lieu de dollars dans : %s\n' "$FORM"
  FAIL=$((FAIL + 1))
fi

# ⚠⚠ GARDE ANTI-DERIVE DU DEPOT, pas une batterie d'assertions. Un depot qui grossit
# par accretion finit par contenir des instruments que plus personne ne sait relancer :
# un script qu'aucun document ni aucun autre script ne nomme est mort sans que rien ne le
# dise. Ce controle les COMPTE et les nomme. Il ne fait pas echouer les temoins -- un
# orphelin n'est pas un bug -- mais il rend la derive visible a chaque passage.
# ⚠⚠ Le document 55 est RENDU depuis le registre : s il n est pas a jour, il ment. Le
# controle le regenere dans un temporaire et compare -- il ne reecrit rien tout seul, parce
# qu une batterie qui repare ce qu elle mesure ne mesure plus rien.
printf '  %-30s ' "doc 55 a jour"
T55=$(mktemp)
uv run --project "$ROOT" python "$ROOT/src/depot/murs_et_causes.py" --rendre "$T55" >/dev/null 2>&1
if diff -q "$T55" "$ROOT/docs/55_les_murs_et_leurs_causes.md" >/dev/null 2>&1; then
  printf '✅ rendu identique au registre\n'
else
  printf '❌ PERIME — relancer : murs_et_causes.py --rendre\n'; FAIL=$((FAIL + 1))
fi
rm -f "$T55"

# ⚠⚠ LE GARDE-FOU DE CE FICHIER LUI-MEME. La liste des `run` ci-dessus est tenue A LA MAIN,
# donc elle derive : mesure du 2026-08-25, SIX batteries sur 90 n avaient jamais tourne -- dont
# quatre qui imprimaient « tous les temoins passent » au lieu de « ALL PASS », si bien que meme
# les enregistrer n aurait rien lance. C est la meme classe de panne que la sentinelle de boot
# qu il faut deplacer a chaque ajout : le remede n est pas de mieux tenir la liste, c est de la
# faire VERIFIER par la machine.
#
# ⭐ La detection cherche le fichier qui GERE `--verifier`, pas celui qui le MENTIONNE -- ce
# fichier le passe a quatre-vingt-dix autres sans le gerer lui-meme, donc un test sur la
# mention se rangerait tout seul dans sa propre liste. `src/outils/temoins_release.sh` fait deja
# cette distinction et sa raison est ecrite chez lui ; c est la meme forme qui est testee ici.
printf '  %-30s ' "batteries non lancees"
JAMAIS=""
# ⚠⚠ La PORTEE du garde etait une paire de globs ecrite a la main, donc un module hors de
# `src/` echappait au controle -- exactement le cas de `inference_xpu/src/infer_ink.py`,
# le point d entree de l inference. La liste suit desormais celle de `artefacts_orphelins.py`.
# Mesure du 2026-08-25 : l elargissement ne signale RIEN de neuf, il ferme juste le trou.
for f in "$ROOT"/src/*/*.py "$ROOT"/inference_xpu/src/*.py "$ROOT"/tracecheck/*.py \
         "$ROOT"/experiments/src/*/*.py; do
  grep -q -- 'add_argument("--verifier"' "$f" || continue
  b=$(basename "$f")
  # ⚠ Le motif porte le GUILLEMET FERMANT : une ligne de lancement ecrit
  # `"$ROOT/src/famille/x.py" --verifier`, donc chercher `x.py --verifier` ne matche jamais
  # et le garde-fou accuserait les quatre-vingt-dix batteries d un coup.
  grep -q -- "$b\" --verifier" "$ROOT/src/outils/temoins.sh" || JAMAIS="$JAMAIS $b"
done
for f in "$ROOT"/src/*/*.sh; do
  b=$(basename "$f")
  # ⚠⚠ AUCUNE EXEMPTION, et c est le test de FORME qui la rend inutile : les deux lanceurs
  # (`temoins.sh`, `temoins_release.sh`) ne GERENT pas `--verifier`, ils le TRANSMETTENT, donc
  # ils ne matchent pas et ne se rangent pas dans leur propre liste. J avais d abord ecrit une
  # exemption nommee pour eux ; elle etait non seulement inutile mais nuisible, puisqu elle
  # aurait fait sauter un vrai auto-test le jour ou l un d eux en gagnerait un.
  grep -qE '\[ "\$\{1:-\}" = "--verifier" \]|^\s*--verifier\)' "$f" || continue
  grep -q -- "$b\" --verifier" "$ROOT/src/outils/temoins.sh" || JAMAIS="$JAMAIS $b"
done
NJAM=$(printf '%s' "$JAMAIS" | wc -w)
if [ "$NJAM" -eq 0 ]; then
  printf '✅ toutes les batteries sont lancees\n'
else
  printf '❌ %s batterie(s) jamais lancee(s) :%s\n' "$NJAM" "$JAMAIS"; FAIL=$((FAIL + 1))
fi

printf '  %-30s ' "scripts sans appelant"
ORPH=""
for f in "$ROOT"/src/*/*.py "$ROOT"/src/*/*.sh; do
  b=$(basename "$f")
  n=$(grep -rl --include='*.sh' --include='*.md' --include='*.py' -- "$b" "$ROOT" 2>/dev/null \
      | grep -v '/\.git/' | grep -v '/\.lances/' | grep -v -x -- "$f" | wc -l)
  [ "$n" -eq 0 ] && ORPH="$ORPH $b"
done
NORPH=$(printf '%s' "$ORPH" | wc -w)
if [ "$NORPH" -eq 0 ]; then
  printf '✅ aucun\n'
else
  printf '⚠ %s orphelin(s) :%s\n' "$NORPH" "$ORPH"
fi

# ⚠ Les quatre batteries hors `run` (marche sur nappe, mosaique, chiffres, orphelins) sont
# comptees a part et NON incluses : elles n'impriment pas « ALL PASS (n checks) », donc les
# additionner demanderait de deviner leur compte -- et un total devine vaut moins qu'un
# total plus petit mais exact.
# ⚠⚠ COROLLAIRE, paye le 2026-08-22 : NE PAS ANTICIPER le compte. Ecrire dans les documents
# la valeur qu'on PREVOIT pour ce run-ci fait echouer ce run-ci -- la garde compare aux
# totaux du run PRECEDENT -- meme quand la prevision est exacte (46/1348 predits, 46/1348
# mesures, et la batterie rouge quand meme). La marche a suivre est : lancer, LIRE le compte,
# l'ecrire, et le run suivant confirme.
#
# ⚠ DECALAGE D'UN RUN, assume. Le garde-fou des chiffres a deja tourne quand ces totaux
# sont ecrits, donc il a compare les documents au `temoins.json` du run PRECEDENT. Un compte
# qui change n'est donc signale qu'au run suivant. Ce n'est pas un passage silencieux -- il
# est signale, une fois -- et l'inverse (ecrire le json avant de verifier) ferait verifier
# les documents contre des totaux que la meme execution vient de produire, ce qui est une
# verification incapable d'echouer.
# ⚠⚠ Le compte des chiffres recalcules est PUBLIE lui aussi, pour la meme raison que les
# deux autres : `21` en citait un, exact le jour ou il a ete ecrit et faux depuis. Il est
# lu de la sortie de l'outil et non compte ici -- deux comptes du meme objet finiraient par
# ne pas s'accorder, et c'est ce fichier qui a deja paye ce defaut.
RECALCULES=$(grep -oE '^[0-9]+ chiffres recalcules' /tmp/chiffres.log 2>/dev/null \
             | head -1 | cut -d' ' -f1)
SOURCES=$(grep -oE 'depuis [0-9]+ fichiers' /tmp/chiffres.log 2>/dev/null \
          | head -1 | cut -d' ' -f2)
python3 -c "
import json, sys
d = {'batteries_all_pass': $BATTERIES, 'controles': $CONTROLES, 'echecs': $FAIL}
# ⚠ Absents plutot que zero : un zero se lit comme « aucun chiffre garde », ce qui est un
# resultat, alors que l'absence veut dire « la batterie des chiffres n'a pas tourne ».
for cle, val in (('chiffres_recalcules', '$RECALCULES'), ('fichiers_de_resultat', '$SOURCES')):
    if val:
        d[cle] = int(val)
json.dump(d, open('$ROOT/docs/temoins.json', 'w'), indent=2)
print()
print(f'  {\"batteries\":<30} {$BATTERIES} batteries, {$CONTROLES} controles')
if '$RECALCULES':
    print(f'  {\"chiffres gardés\":<30} $RECALCULES depuis $SOURCES fichiers de résultat')"

echo
if [ "$FAIL" -eq 0 ]; then
  echo "TOUS LES TEMOINS PASSENT"
else
  echo "$FAIL batterie(s) en echec"
fi
exit "$FAIL"
