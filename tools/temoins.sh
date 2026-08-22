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
# (`analysis/src/verifier_chiffres.py`). Ils sont donc ecrits dans `docs/temoins.json` et
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

cd "$ROOT/inference_xpu" || exit 2
run "champ de correction" uv run python - <<'PY'
import sys, time, random
from pathlib import Path
sys.path.insert(0, str(Path("../analysis/src").resolve()))
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
sys.path.insert(0, str(Path("../analysis/src").resolve()))
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
sys.path.insert(0, str(Path("../analysis/src").resolve()))
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
import sys; sys.path.insert(0, '../analysis/src')
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
  run "poids GrowPatch vs source" python3 "$ROOT/analysis/src/poids_growpatch.py" --verifier
else
  printf '  ⚠ %-28s villa non clone (tools/clone_repos.sh) — NON VERIFIE\n' "poids GrowPatch vs source"
fi

# ⚠ La regle centrale du depot porte sur les CHIFFRES ; elle vaut aussi pour les artefacts
# qui les portent. Un fichier de mesure versionne dont le script est reste dans un terminal
# est un resultat qu'on ne peut ni rejouer, ni verifier, ni corriger.
run "artefacts : un producteur" python3 "$ROOT/analysis/src/artefacts_orphelins.py" --verifier

# ⚠⚠ Deux instruments ecrits le 2026-08-20, et tous deux rendent un verdict STATISTIQUE :
# un intervalle de confiance, une correction de comparaisons multiples, une fonction de
# puissance. Une erreur dans l'un d'eux ne produit pas une erreur, elle produit un tableau
# entierement plausible. La sonde qui compte dans le premier temoin est celle qui verifie
# que la puissance tombe au niveau du test SOUS L'HYPOTHESE NULLE ; dans le second, que le
# basculement d'un verdict ne se lit pas comme une simple dispersion d'aire.
cd "$ROOT/experiments" || exit 2
run "carte : incertitude"     uv run python "$ROOT/analysis/src/incertitude_carte.py" --verifier
run "tirages : dépouillement" uv run python "$ROOT/analysis/src/table_tirages.py" --verifier

# ⚠⚠ Le lecteur unique des rapports `vc_tifxyz_selfcross`. Il existe parce que l'outil peut
# declarer une surface « propre » en n'ayant teste AUCUNE paire de quads : son filtre
# `--maxedge` les jette tous des que le maillage est assez grossier. Six scripts de ce
# depot lisaient ce rapport sans regarder `pairs_tested`. Le temoin verifie que le refus se
# declenche, et qu'il ne se declenche QUE la.
run "selfcross : refus du vide" python3 "$ROOT/analysis/src/lire_selfcross.py" --verifier

# ⚠ Ecrit AVANT que la campagne dense ait fini : `33` avance une prediction falsifiable
# (« l'ordre des treize ne se reproduira pas »), et un depouilleur ecrit apres coup ne
# peut plus la tester. Le temoin verifie que le fichier distingue un ordre conserve d'un
# ordre inverse -- sans quoi il rendrait le meme verdict dans les deux cas.
run "cartes : ordre conservé ?" uv run python "$ROOT/analysis/src/comparer_cartes.py" --verifier

# ⚠⚠ Le seul temoin d'ici qui protege le DEPOT contre l'operateur et non contre le code.
# Editer un script pendant qu'il tourne le casse -- paye TROIS fois le 2026-08-20, alors
# que le piege est ecrit dans deux fichiers du projet. Il porte son controle NEGATIF : le
# meme script lance en direct DOIT casser, sinon la propriete qu'il verifie serait
# invérifiable sur cette machine.
cd "$ROOT" || exit 2
run "lancer : gel d'un script"  "$ROOT/tools/lancer.sh" --verifier
cd "$ROOT/experiments" || exit 2

# ⚠⚠ Le controle qui compte dans ce temoin est qu'un EX-AEQUO n'est pas un accord : si le
# mauvais tirage et le meilleur propre butent tous deux sur le plafond de la fenetre
# rendue, ils sont egaux par CENSURE et non par mesure. Les compter comme un accord ferait
# conclure que les deux axes s'accordent alors que rien n'a pu etre departage.
run "second axe : accord"     uv run python "$ROOT/analysis/src/table_second_axe.py" --verifier

# ⚠⚠ Cet instrument existe pour REFUSER. Rapporte a l'ecart inter-spires de son rouleau,
# chaque ecart mesure devient un nombre de spires -- et les seize premieres mesures
# donnaient 0,65 a 1,25 spire, motif tres convaincant. Toutes etaient censurees ou prises
# dans une fenetre plus etroite que 1,4 spire : le motif venait de la fenetre, pas du
# papyrus. Les deux refus (censure, fenetre trop etroite) sont ce que le temoin verifie.
run "écart en spires"         uv run python "$ROOT/analysis/src/ecart_en_spires.py" --verifier

# ⚠ La grandeur qui tranche un « rien » de detecteur d'encre est l'ECART-TYPE, pas la
# mediane : un modele qui ne s'accroche a rien rend une constante, et sa mediane peut
# tomber n'importe ou. Le temoin le sonde sur deux tableaux de MEME mediane.
run "encre : σ contre témoin"  uv run python "$ROOT/analysis/src/comparer_encre.py" --verifier

# ⭐⭐ Le seul juge de trace de ce depot qui n'ait NI seuil, NI verite terrain, NI echelle :
# on rend la meme surface dans des fenetres de plus en plus profondes et on regarde si la
# distance mesuree bouge. Ses TROIS REFUS sont ce que le temoin verifie -- une seule
# fenetre, deux fenetres trop proches, un ecart nul -- parce que sans eux il rendrait un
# verdict sur rien, et qu'un test incapable d'echouer est ce que ce depot traque.
run "convergence de la trace"  uv run python "$ROOT/analysis/src/test_convergence.py" --verifier
run "géométrie de la chaîne"   uv run python "$ROOT/analysis/src/geometrie_chaine.py" --verifier
# ⚠ Cet outil rend un VERDICT sur une conclusion entiere — « aucun des 15 segments
# publies n'est un patch de la meme feuille ». Son temoin verifie surtout ses trois
# REFUS : un maillage illisible, un patch trop maigre, et une nappe hors de portee, que
# la premiere version confondait dans un seul `None` — et cette confusion a fait
# publier « 49 paires eloignees » pour 45 mesurees.
run "carte des segments"       uv run python "$ROOT/analysis/src/carte_segments.py" --verifier
run "langue des figures"       uv run python "$ROOT/analysis/src/langue.py"
# ⚠⚠ La typographie : ses temoins tournent sur des pages SYNTHETIQUES dont on a choisi
# l'interligne et l'epaisseur de trait. C'est ce qui rend l'instrument falsifiable --
# mesurer un vrai corpus ne dit jamais si la mesure est juste, faute de reference.
# Et ses controles negatifs (une marge vierge, du bruit) sont ce qui empeche
# « periodique » de vouloir dire « il y a des pixels ».
run "typographie sans lecture" uv run python "$ROOT/analysis/src/typographie.py" --verifier
run "figure typographique"     uv run python "$ROOT/analysis/src/figure_typographie.py" --verifier
# ⚠⚠ L'appariement surface/volume : le script de campagne prenait `head -1` de deux
# listages S3, ce qui est juste tant qu'un rouleau n'a qu'un scan et FAUX SANS UN MOT
# des qu'il en a deux. Le temoin sonde justement le cas ou les deux listes ne se trient
# pas pareil -- le seul qui justifie ce fichier.
run "appariement des scans"    uv run python "$ROOT/analysis/src/apparier_volumes.py" --verifier
# ⚠⚠ La comparaison des deux plafonds : sa sonde verifie qu'un rouleau qui bute AUSSI
# sur le nouveau plafond est ECARTE du verdict. L'inclure comparerait une troncature a
# une autre et affaiblirait l'effet mesure sans qu'aucune ligne ne le signale.
run "plafond : les 2 campagnes" uv run python "$ROOT/analysis/src/comparer_plafond.py" --verifier
run "figure du plafond"        uv run python "$ROOT/analysis/src/figure_plafond.py" --verifier
run "campagne des graines"     uv run python "$ROOT/analysis/src/figure_graines.py" --verifier
run "écarts entre segments"    uv run python "$ROOT/analysis/src/figure_segments.py" --verifier
# ⚠⚠ Le temoin negatif : sa garde REFUSE de conclure quand le controle POSITIF est plat.
# Sans elle, deux cartes plates rendent un rapport proche de 1 et le verdict se lirait
# « le temoin trompe le detecteur » alors qu'il veut dire « le detecteur est eteint des
# deux cotes ». Et sa sonde verifie qu'une experience NON CONCLUANTE reste imprimable :
# la premiere version la faisait sortir par le chemin d'erreur, sans ecrire son JSON.
run "témoin négatif"           uv run python "$ROOT/analysis/src/temoin_negatif.py" --verifier
run "figure du témoin négatif" uv run python "$ROOT/analysis/src/figure_temoin_negatif.py" --verifier
# ⚠⚠ La derive avec la profondeur : sa sonde verifie qu'une trace CENSUREE est ecartee de
# la derive. La compter ferait mesurer le deplacement du PLAFOND en croyant mesurer la
# surface -- et comme le plafond monte avec la profondeur, l'erreur irait toujours dans le
# meme sens, donc ressemblerait a un effet. Et sa fixture a TROIS traces et pas deux : a
# deux, l'appariement positionnel rend le meme nombre que l'appariement par identite, donc
# la sonde ne pouvait pas echouer.
run "dérive avec la profondeur" uv run python "$ROOT/analysis/src/derive_avec_profondeur.py" --verifier
run "figure de la dérive"      uv run python "$ROOT/analysis/src/figure_derive_profondeur.py" --verifier
# ⚠⚠ L'eligibilite : sa sonde verifie qu'un candidat SANS prediction de surface est ECARTE
# et pas classe dernier -- la campagne de graines ne peut structurellement pas y tourner, et
# le garder ferait recommander une experience irrealisable. Et une sonde sur le VRAI fichier
# de resultat, parce qu'une fixture ecrite d'apres le code ne prouve que leur accord : c'est
# comme ca qu'une cle inexistante a rendu « 0 rouleau tracable » et un verdict confiant.
run "où monter l'expérience"   uv run python "$ROOT/analysis/src/eligibilite_aval.py" --verifier
run "figure de l'éligibilité"  uv run python "$ROOT/analysis/src/figure_eligibilite.py" --verifier
# ⚠⚠ L'audit des profils plats : sa sonde verifie qu'une serie dont TOUTES les lectures sont
# le bord de la fenetre a un α mesure EGAL a son α de plafond -- donc que α ne separe pas
# « le pic recule » de « il n'y avait pas de pic ». Et son controle, que la moitie
# rassurante tienne : une serie qui converge en est loin par construction.
run "audit des profils plats"  uv run python "$ROOT/analysis/src/audit_profils_plats.py" --verifier
# ⚠ L'excision : sa sonde refuse de dessiner si les deux populations sont le MEME
# echantillon. Deux resumes identiques a la decimale sont le resultat -- et aussi ce a quoi
# ressemble une colonne recopiee deux fois.
run "excision : deux populations" uv run python "$ROOT/analysis/src/figure_excision.py" --verifier
# ⚠⚠ Le garde-fou des chiffres se garde lui-meme. Il n'avait AUCUN auto-test : il protege
# les 140 chiffres publies du depot et rien ne verifiait qu'il sait encore les trouver -- ni,
# surtout, qu'il sait ECHOUER. Sa sonde exige qu'un chiffre FAUX ne soit pas trouve.
run "le garde-fou se garde"    uv run python "$ROOT/analysis/src/verifier_chiffres.py" --verifier
# ⚠⚠ Le chien de garde des rendus. Sa sonde la plus utile est la COURSE : un rendu qui finit
# ENTRE deux sondages etait declare abandonne, donc il aurait frappe n'importe quel rendu
# court -- c'est-a-dire les bons. Et son controle exige qu'un processus qui travaille ne soit
# PAS tue : un garde qui tue ce qui va bien est la pire panne possible.
run "chien de garde des rendus" "$ROOT/tools/rendre_surveille.sh" --verifier
# ⚠⚠ Le 2×2 des predictions. Ses deux sondes qui comptent sont SYMETRIQUES : un effet franc
# de prediction doit etre attribue a la prediction, et un effet franc d'ENDROIT a l'endroit.
# Sans la seconde, un instrument qui dirait toujours « prediction » passerait la premiere.
# Et il refuse quand l'ecart entre cellules est sous le bruit de tirage mesure -- le traceur
# est un tirage, et la meme graine a rendu +0,89 puis +1,12.
run "2×2 des prédictions"      uv run python "$ROOT/analysis/src/comparer_predictions.py" --verifier
run "figure des deux pannes"   uv run python "$ROOT/analysis/src/figure_deux_pannes.py" --verifier
# ⚠⚠ Les images des documents. Un lien vers une image absente ne casse rien a l'execution :
# il s'affiche avec une icone brisee, et personne ne le voit tant que personne n'ouvre le
# document. ⚠ Le test utilise `-s` et non `-e` : un rendu interrompu laisse un fichier de
# zero octet, et un lien vers un fichier vide s'affiche exactement comme un lien vers rien.
run "images des documents"     "$ROOT/tools/images_des_docs.sh" --verifier
run "liens d'images valides"   "$ROOT/tools/images_des_docs.sh"
# ⚠⚠ La figure du 2×2. Sa sonde de linearite a attrape un vrai defaut d axe : `int` tronque,
# donc le milieu exact tombait un pixel a gauche quand la division ne se ferme pas en
# binaire. Placer un point sur un axe est un ARRONDI.
run "figure du 2×2"            uv run python "$ROOT/analysis/src/figure_2x2.py" --verifier

run "graine : les 2 versions"  uv run python - <<'PY'
import sys
sys.path.insert(0, '../analysis/src')
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

# ⚠ Ces deux-la tournent depuis `inference/` : c'est le seul environnement du depot qui
# porte Pillow, et `temoins.sh` s'execute depuis `experiments/` pour le reste. Lance
# ailleurs, l'import echoue en disant « pas de module PIL », ce qui se lit comme une
# dependance manquante et non comme un mauvais repertoire.
printf '  %-30s ' "marche sur nappe"
if (cd "$ROOT/inference" && uv run python "$ROOT/analysis/src/suivre_nappe.py" --verifier) >/tmp/nappe.log 2>&1; then
  printf '✅ %s\n' "$(grep -c '✅' /tmp/nappe.log) checks"
else
  printf '❌ ECHEC\n'; sed 's/^/       /' /tmp/nappe.log | tail -6; FAIL=$((FAIL + 1))
fi

printf '  %-30s ' "mosaique : assemblage"
if (cd "$ROOT/inference" && uv run python "$ROOT/analysis/src/assembler_mosaique.py" --verifier) >/tmp/mos.log 2>&1; then
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
if uv run python "$ROOT/analysis/src/verifier_chiffres.py" "$ROOT"/docs/*.md \
     "$ROOT/article/article.typ" \
     --soumission "$ROOT/docs/21_texte_de_soumission.md" \
     --article "$ROOT/article/article.typ" >/tmp/chiffres.log 2>&1; then
  printf '✅ %s\n' "$(grep -c '✅' /tmp/chiffres.log) chiffres retrouves"
else
  printf '❌ ECHEC\n'; sed 's/^/       /' /tmp/chiffres.log | tail -6; FAIL=$((FAIL + 1))
fi

# ⚠⚠ GARDE ANTI-DERIVE DU DEPOT, pas une batterie d'assertions. Un depot qui grossit
# par accretion finit par contenir des instruments que plus personne ne sait relancer :
# un script qu'aucun document ni aucun autre script ne nomme est mort sans que rien ne le
# dise. Ce controle les COMPTE et les nomme. Il ne fait pas echouer les temoins -- un
# orphelin n'est pas un bug -- mais il rend la derive visible a chaque passage.
printf '  %-30s ' "scripts sans appelant"
ORPH=""
for f in "$ROOT"/analysis/src/*.py "$ROOT"/tools/*.sh; do
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
