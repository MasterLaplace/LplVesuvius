# Le grand ménage — plan, mesuré avant d'être écrit

> ⚠⚠ **Ce document est un PLAN, pas un résultat.** Il est écrit pour être repris par une session
> neuve qui n'a pas le contexte. Tout ce qu'il avance est mesuré, et la commande qui produit
> chaque chiffre est donnée. Ce qu'il **décide de ne pas faire** est écrit aussi — c'est la
> partie qu'on oublie et c'est celle qui empêche la question de revenir tous les quinze jours.

Cadré avec le skill [`concevoir-avant-coder`](../../LplCraftSkills/skills/concevoir-avant-coder/SKILL.md) :
besoin avant solution, YAGNI sur ses deux axes, ossature en stubs, modules et paliers, pipeline
adaptatif par modes et compteurs, échelle d'escalade.

---

## 1. Ce qui est MESURÉ, et ce que ça corrige de l'impression de départ

L'impression était : *« sept dossiers blindés de scripts, une montagne de doublons, des données
en double, des choses recalculées »*. Trois de ces quatre points sont vrais, un est faux, et
c'est le plus gros.

### 1.1 ⚠⚠ Les « sept dossiers de scripts » sont DEUX dossiers et cinq environnements

| dossier | fichiers **source** | lignes | poids réel | poids total |
|---|---:|---:|---:|---:|
| `analysis/` | **123** | 35 561 | 3,2 M | 3,2 M |
| `tools/` | **73** | 8 359 | 624 K | 624 K |
| `experiments/` | 16 | 3 464 | 624 K | **351 M** |
| `tracecheck/` | 4 | 1 310 | 144 K | 144 K |
| [`htr/`](https://github.com/MasterLaplace/LplVesuvius/tree/3caf6910914eedaca3b3b26a3b2ea206762d6a9f/htr) | **1** | 185 | 264 K | ~~5,1 G~~ **retiré le 2026-08-25** |
| `inference_xpu/` | **1** | 169 | 128 K | **6,3 G** |
| `inference/` | **0** | 0 | 256 K | ~~5,2 G~~ **retiré le 2026-08-25** |

[`htr/`](https://github.com/MasterLaplace/LplVesuvius/tree/3caf6910914eedaca3b3b26a3b2ea206762d6a9f/htr), `inference/` et `inference_xpu/` ne portent **aucun code** ou presque : ce sont des
`.venv`. Ce qui donne l'impression d'une montagne est un environnement, pas un programme.

### ⚠⚠ Deux affirmations de ce paragraphe étaient FAUSSES — corrigées le 2026-08-25

**1. Les « 16,6 Go » n'existent pas.** Le chiffre venait de trois `du -sh` invoqués séparément,
et `du` ne peut pas voir ce qui se passe ici : `uv` installe ses paquets en **liens durs** vers
`~/.cache/uv`. Un fichier de venv n'est donc pas une copie, c'est un **nom de plus** sur des
octets déjà là, et supprimer le nom ne libère rien tant qu'il en reste un autre. Le compte de
liens est la seule chose qui réponde, et voici sa réponse pour `htr/` + `inference/.venv` :

| nlink | fichiers | octets | ce que ça veut dire |
|---:|---:|---:|---|
| 1 | 8 228 | **0,15 Gio** | exclusif → libéré tout de suite |
| 2 | 42 994 | **4,09 Gio** | cache + ce venv → libéré après `uv cache prune` |
| ≥ 3 | 9 516 | **3,06 Gio** | tenu par d'autres venvs → jamais libéré |

Soit **4,24 Gio** de récupérable réel là où ce plan annonçait 16,6 : un facteur quatre. Et
*rien* n'est libéré sans `uv cache prune`, qui touche une ressource **partagée avec le reste de
la machine** et n'est donc pas une décision de ce dépôt. Calcul dans l'arbre —
`src/depot/poids_recuperable.py` (10 contrôles), résultat dans `docs/poids_recuperable.json`.

**2. Les « 25 sites d'appel » n'étaient pas des besoins, c'étaient des EMPRUNTS.** Le motif
écrit partout — *« le seul environnement du dépôt qui porte Pillow »* — était faux : la racine
déclare `pillow>=10.0`. Pire, `inference/` **n'a pas `numcodecs`**, et c'est précisément ce trou
qui a fait rendre vides tous les chunks *blosc* d'une prédiction, donc conclure à tort qu'une
graine n'était pas couverte par la prédiction publiée (`src/commun/zarr_depth.py`). Les
scripts empruntaient un environnement **strictement plus pauvre** que celui d'où ils pouvaient
tourner. Les 25 sites sont repointés sur la racine, et les **11 batteries** concernées passent
depuis là — vérifié, pas supposé.

**Ce qui est parti, et ce qui ne l'est pas.** `htr/` : un seul fichier, remplacé par
`src/encre/structure.py`, **zéro site d'appel** sous quelque orthographe que ce soit.
⚠⚠ **`inference/` est parti aussi, et c'est une correction de MA conclusion.** J'avais écrit
qu'il restait, sur l'argument de son propre README : témoin CPU du ×4,5 iGPU, et *« une
accélération qu'on ne peut plus vérifier n'est pas une accélération »*. L'auteur a objecté que
le témoin devait être un **mode**, pas un dossier — *« au pire faire un mode fallback vers cpu
si gpu pas dispo, c'est ça un pipeline adaptatif »*. Il a raison, et la mesure va plus loin que
son argument : **deux dossiers, c'étaient deux constructions de torch différentes** (générique
d'un côté, `2.9.1+xpu` de l'autre), donc la comparaison mélangeait l'appareil ET la build. Le
témoin en mode change **une** variable, ce qu'un témoin doit faire. Vérifié le 2026-08-25 : la
build `+xpu` exécute le chemin CPU sans rien de particulier.

`inference_xpu/src/infer_ink.py` prenait déjà `--device {cpu,xpu}` ; il prend désormais
**`--device auto` par défaut**, et la règle qui le gouverne est la seule chose qui distingue un
pipeline adaptatif d'un pipeline silencieux : **« auto » retombe, « xpu » REFUSE.** Demander
explicitement le GPU et obtenir le CPU sans le savoir ferait publier un temps mesuré sur l'autre
appareil — la panne exacte que le repli est censé éviter, déplacée d'un cran. Le choix est une
**fonction pure** qui prend la disponibilité en argument, donc il s'auto-teste sans GPU, sans
torch, et sans modèle : 10 contrôles hors ligne, deux sondes.

`inference_xpu/` reste entier : c'est l'environnement de l'encre, et l'encre est le prochain
chantier nommé.

⚠⚠ **Et la vraie montagne n'a jamais été là.** Le dépôt pèse **203 Gio**, dont **177 dans
`data/`**. Les 4,24 Gio de venvs sont **2 %** du problème. Le lever, c'est le chantier A (97 Gio
de rendus recalculés) et le B, pas celui-ci.

```bash
for d in analysis experiments htr inference inference_xpu tools tracecheck; do
  n=$(find "$d" \( -name '*.py' -o -name '*.sh' \) -not -path '*/.venv/*' | wc -l)
  printf '%-16s %4s fichiers  %8s total\n' "$d" "$n" "$(du -sh "$d" | cut -f1)"
done
grep -rl -- "--project.*inference\b" tools/*.sh analysis/src/*.py | wc -l
```

### 1.2 ⭐ La duplication de code est PETITE en volume et DÉJÀ DIVERGENTE

630 fonctions définies, **328 noms distincts**, **40 noms répétés**. Mais les gros répétés sont
**structurels** et voulus : `main` ×122 (un par verbe), `verifier`/`_verifier` ×75 (une batterie
par module — c'est la règle du dépôt).

Les vrais doublons sont petits, et c'est leur **divergence** qui coûte :

| fonction | copies | **variantes distinctes** |
|---|---:|---:|
| `_police` | 15 | ⚠⚠ **4** |
| `_pixels` | 14 | ⚠ **3** |
| palette `FOND`/`ENCRE`/`GRIS`/`TRAIT` | 14 | à vérifier |

**~300 lignes sur 35 561, soit 0,8 %.** Quatre variantes de la même fonction, c'est exactement la
classe de défaut que ce dépôt traque partout ailleurs : *la même chose qui n'est plus la même*.

```bash
grep -hoP '^def \K\w+' analysis/src/*.py | sort | uniq -c | sort -rn | head -20
for f in $(grep -l "^def _police" analysis/src/*.py); do
  awk '/^def _police/,/^$/' "$f" | md5sum | cut -c1-8
done | sort | uniq -c
```

### 1.3 ⚠⚠⚠ Le vrai gaspillage : **97 Go de rendus**, et un cas mesuré de recalcul

`data/` pèse **177 Go**, 80 dossiers de premier niveau, **68 540 fichiers**. Dont :

| | poids | part |
|---|---:|---:|
| **324 dossiers `rendu*`** | **97 Go** | ⚠⚠ **55 %** |
| `data/layers/` | 51 Go | 29 % |
| `data/traces/` | 17 Go | 10 % |

Et le recalcul n'est pas une hypothèse — **il a été mesuré le 2026-08-25** : la même surface
(`morceau_00`) a été rendue et profilée **deux fois**, dans deux campagnes différentes, pour un
résultat **bit-pour-bit identique** :

```
c1ff66d445eea26dadfa5f4d0b1e6173  data/chaine_tangentielle/profil_morceau_00/g0_n41/profil.json
c1ff66d445eea26dadfa5f4d0b1e6173  data/chaine_courte/profil_morceau_00/g0_n41/profil.json
```

**~15 minutes de rendu payées deux fois**, parce que le cache de `profiler_une_surface.sh` est
**par répertoire de destination**, pas par contenu.

⚠ **En revanche, l'hypothèse « téléchargé en double » ne tient PAS** dans `layers/` et
`traces/` : le proxy « même nom + même taille » n'y trouve que **1,0 Go**, presque uniquement
des `meta.json` de quelques centaines d'octets, qui sont légitimement un par maillage. Sur tout
`data/`, le même proxy annonce 17,4 Go — mais il **surcompte** : ce sont des chunks zarr nommés
`40`, `41`… de 2 Mio, qui portent le même nom dans des volumes différents **sans être le même
contenu**. À confirmer par hachage réel avant d'effacer quoi que ce soit.

```bash
find data -maxdepth 3 -type d -name "rendu*" | wc -l
find data -maxdepth 3 -type d -name "rendu*" -exec du -s {} + | awk '{t+=$1} END {printf "%.1f Go\n", t/1048576}'
```

### 1.4 ⚠ `docs/` mélange quatre natures de choses, et `.lances/` s'accumule

`docs/` : **528 entrées** — 57 markdown (de la prose), **341 JSON** (des résultats), 73 images
(des figures), et **~57 `.log` / `.csv` / `.jsonl`** (des sorties brutes de campagne). Quatre
choses qui n'ont ni le même cycle de vie ni le même lecteur, dans un seul dossier.

`.lances/` : **196 fichiers**, soit ~65 lancements × (`.log`, `.pid`, `.sh`). Rien ne les purge.

---

## 2. Le besoin, avant la solution

Ce que le ménage doit rendre **observable**, et qui le constate :

1. **Un rendu déjà calculé n'est jamais recalculé.** Constatable : relancer une campagne qui
   partage une surface avec une autre ne relance aucun rendu, et le journal le dit.
2. **Un rouleau se voit d'un seul endroit.** Constatable : `ls data/PHercParis4/` montre tout ce
   qu'on possède de ce rouleau, et une seule commande dit ce qui est calculé, ce qui manque et
   ce qui a coûté quoi.
3. **Un verbe se découvre sans lire la doc.** Constatable : `lplv --help` liste les verbes,
   `lplv <verbe> --help` décrit celui-là, et **aucun des deux ne peut périmer** puisqu'ils sont
   dérivés du code.
4. **Une fonction de dessin existe en un seul exemplaire.** Constatable : `_police` est définie
   une fois, et le garde-fou des batteries échoue si une seconde apparaît.

⚠ **Ce qui est vrai aujourd'hui et ne le sera plus** : les chemins `data/<campagne>/…` sont
écrits en dur dans des dizaines de scripts et dans les blocs « Reproduire » de 57 documents. Une
réorganisation de `data/` **casse ces chemins**. C'est la contrainte dure du chantier B, et elle
décide de son ordre.

---

## 3. Les quatre chantiers, indépendants, ordonnés par rapport bénéfice/risque

> ⚠ **Ils sont indépendants EXPRÈS.** Chacun se livre seul, se juge seul, et se retire seul.
> Un « grand refactor » monolithique est exactement ce que le §2 du skill interdit : un diff que
> personne ne peut relire, donc approuvé au lieu d'être relu.

### ⭐ Chantier A — le cache de rendu par CONTENU (le seul qui rapporte des gigaoctets)

**Le besoin** : ne jamais recalculer un rendu déjà calculé, même dans une autre campagne.

**La forme** : une clé = `hash(contenu du tifxyz) + paramètres de fenêtre + niveau`. Un dossier
`data/cache/rendus/<clé>/`, et les campagnes y font un lien plutôt qu'un rendu.

- ⭐ Il y a **déjà** un cache, mais indexé par *destination* : le rendre indexé par *contenu*
  est un changement local dans `src/outils/profiler_une_surface.sh` et rien d'autre.
- ⚠ **Ce qui doit être compté** (skill §8, règle 1) : `cache_hit` / `cache_miss`, écrits dans le
  journal. Un cache dont on ne mesure pas le taux de succès est une devinette avec un dossier.
- ⚠⚠ **Et le repli est bruyant** : un manque de cache se dit, il ne se déduit pas d'un temps
  d'exécution.
- **La porte de sortie** : relancer la campagne `chaine_courte` après `chaine_tangentielle` ne
  déclenche **aucun** rendu de `morceau_00`, et le compteur dit `cache_hit=1`.

**Ce que ça rapporte, mesuré** : sur 324 dossiers de rendu et 97 Go, la part réellement
dupliquée reste **à mesurer par hachage** — c'est la première tâche du chantier, et elle est
bon marché. Le cas connu vaut 15 minutes ; il y en a probablement des dizaines.

#### ✅ Chantier A, première moitié — le doublonnage MESURÉ, et ce qu'il révèle

![Le contenu identique de data/, par motif](images/56_doublons.png)

```bash
uv run python src/depot/contenu_en_double.py data --json docs/contenu_en_double.json
uv run python src/figures/figure_doublons.py     # → docs/images/56_doublons.png
```

**35,58 Gio de contenu identique**, mesurés par **hachage** sur 68 540 fichiers. ⚠ Le proxy
« même nom + même taille » de §1.3 annonçait 17,4 Go et se trompait **dans les deux sens** :
il comptait des chunks zarr homonymes de contenu différent, et il ratait tout ce qui suit,
qui ne porte pas le même nom.

⭐ Trois étages, du moins cher au plus cher, sans quoi hacher 177 Gio est absurde : la
**taille** (une taille unique n'est jamais lue), un **hachage partiel** de 64 Kio qui casse
les gros groupes, et le **hachage complet** sur ce qui reste — **15 473 seulement**, sur
68 540 fichiers.

⚠⚠ Le hachage partiel ne conclut **jamais** seul : deux rendus partagent leur en-tête, et
s'arrêter là déclarerait identiques deux images différentes. C'est sondé en le cassant.

##### ⭐⭐ Et la découverte, qui vaut plus que du disque : **58,6 % sont des fenêtres imbriquées**

| motif | poids | ce que c'est |
|---|---:|---|
| **fenêtres imbriquées** | **20,85 Gio** | la tranche `i` de n=31 **EST** la tranche `i+25` de n=81 |
| autre | 10,51 Gio | — |
| même fenêtre, deux campagnes | 4,22 Gio | le doublon que le cache par contenu supprime |

Une fenêtre de 31 couches est le **centre** d'une fenêtre de 81 rendue au même endroit : la
distance au centre est la même, donc c'est **le même fichier, au bit près**. Les paires
trouvées sont exactement la série de convergence du dépôt — **(31, 81)** sur 2232 groupes et
**(41, 161)** sur 861.

⭐ **La conséquence n'est donc pas 20 Gio de disque, c'est le temps de rendu de toute campagne
de convergence** : rendre n=161 produit **déjà** n=81 et n=41. ⚠ Et un cache indexé sur
(surface, niveau, N) — celui qu'on vient d'écrire — **ne peut pas le voir**, puisque N diffère.
Seul un cache par **tranche** le verrait. C'est la seconde moitié du chantier A, et elle n'est
pas faite.

#### ✅ Chantier A, seconde moitié — le cache par CONTENU (livré, non exercé)

`src/depot/empreinte_surface.py` donne la clé : `hash(contenu du tifxyz)` + niveau + couches +
taille de voxel. `profiler_une_surface.sh` la consulte avant de rendre et y dépose après.

⚠⚠ Ce qui est **délibérément exclu de la clé**, et chacun est une panne évitée : la **date de
modification** (recopier une surface d'un disque à l'autre la change sans changer un octet, et
le cache manquerait pour rien), le **chemin absolu** (deux machines ne partageraient jamais un
cache), et l'**ordre du système de fichiers** (`iterdir` ne promet aucun ordre, donc deux
exécutions donneraient deux clés — le tri est ce qui fait d'une clé une clé).

⚠ Et ce qui y **entre** : tout réglage qui change le profil. Un réglage absent de la clé fait
rendre le profil d'un **autre** réglage, ce qui est pire qu'un cache absent — c'est un résultat
faux qui a l'air d'un résultat. `--scale 1` et `--auto-crop` sont aujourd'hui des constantes ;
le jour où l'un devient un paramètre, il entre dans la clé.

⚠ **Le repli est bruyant** : `cache_hit=` / `cache_miss=` sont **imprimés**, et une empreinte
indisponible n'arrête pas le rendu — elle le dit. Un cache est une optimisation ; en faire une
condition de fonctionnement serait un recul.

⚠⚠ **Non exercé sur un vrai rendu.** La porte de sortie du plan — relancer `chaine_courte`
après `chaine_tangentielle` et lire `cache_hit=1` — demande quinze minutes de rendu et un
volume distant. Ce qui est vérifié ici est la **forme** : les compteurs sont imprimés, le dépôt
suit le profil au lieu de le précéder, et la clé vient de l'instrument et non d'une recette
locale. La première campagne réelle sera la mesure.

⚠ **Rien n'est supprimé.** `contenu_en_double.py` mesure et nomme ; un effacement n'est pas
réversible, et la décision appartient à qui a téléchargé les données.

#### ⭐⭐ Le raccourci de rendu — vérifié adversarialement, et il tient

![La géométrie du raccourci](images/56_sous_fenetre.png)

```bash
uv run python src/depot/sous_fenetre.py 31 41 81 161   # → 3 rendus évités sur 4
uv run python src/figures/figure_sous_fenetre.py       # → docs/images/56_sous_fenetre.png
```

Les 20,85 Gio de fenêtres imbriquées disent une chose simple : **rendre n=161 produit déjà
n=81, n=41 et n=31.** Et il n'y a **rien à construire** — `depth_profile.py` porte déjà
`--from-layer`, `--to-layer` et `--traced-layer`. Ce qui manquait n'est pas une capacité, c'est
l'**arithmétique énoncée une fois** : `src/depot/sous_fenetre.py`.

**Éprouvé par 8 mesures indépendantes et 5 tentatives de réfutation** (13 agents, 2,95 M
tokens) : **6 sites confirment**, chacun avec **toutes** ses tranches identiques octet pour
octet et **23 mesures de profil identiques sur 23**, zéro différence. Les 2 restants sont
IMPOSSIBLE pour des raisons de **données**, pas de méthode — voir plus bas. **Aucun site ne
réfute.**

##### ⚠⚠ Les quatre bornes, dont trois n'étaient vérifiées par RIEN

| borne | ce qui arrive si elle tombe | où elle est vérifiée |
|---|---|---|
| **même parité** de N large et N étroite | les centres sont décalés d'une demi-tranche, le profil dérivé est décalé | `peut_deriver`, refus |
| **pile contiguë de 0 à N−1** | `--from-layer` désigne des **numéros de fichier**, pas des positions : sur une pile trouée la sous-plage rend un profil **plus court, en silence** | `verifier_pile`, **écrit ce lot** |
| **même `--layer-step` des deux côtés** | `peak_iqr` est multiplié par le pas | dit, pas encore imposé |
| **même surface** entre les deux rendus | le recadrage suit le maillage, pas la pile | dit, pas encore imposé |

⭐ Et le réfuteur « arithmétique » a **redérivé indépendamment** la formule : l'instrument
compare `--traced-layer` au **numéro de fichier** (`depth_profile.py:208`), donc le décalage est
`N_large // 2 − N_étroite // 2` et **non** `(N_large − N_étroite) / 2`. Les deux coïncident sur
toute la série du dépôt, qui est impaire ; la seconde n'est même pas entière ailleurs. C'est
exactement le refus que `peut_deriver` portait déjà — la réfutation a validé le module en
tombant sur la formulation naïve de sa consigne.

##### ⚠⚠ Un piège de l'instrument, que TROIS vérificateurs ont failli lire comme une réfutation

La **console** réimprime les indices de pic en **ABSOLU** (elle rajoute `layers[0]`) pendant
que le **JSON** les stocke **RELATIFS** à la fenêtre. Sur la même mesure, la console dit « pic
médian couche 42 » d'un côté et « couche 17 » de l'autre — un écart de 25, exactement le
décalage — alors que le JSON porte `17.0` **des deux côtés**. Ce n'est pas un défaut (l'absolu
est ce qu'un humain veut voir), mais ce n'était **dit nulle part**. La ligne d'en-tête le dit
désormais, et la docstring l'explique.

##### ⚠ Deux pannes de DONNÉES, trouvées en vérifiant tout autre chose

- **`data/leur_graine/rendu_161`** : les 161 fichiers sont **illisibles** — en-tête `II*\0`
  correct puis offset d'IFD nul, donc zéro page, pour **1,89 Gio** sur le disque. Vérifié par
  moi contre deux lecteurs. [`51`](51_une_pente_a_deux_appuis.md) disait « le profil
  **survivant** » sans nommer ce qui avait tué l'autre ; c'est écrit là-bas maintenant. ⚠ Ce
  n'est **pas** la panne de [`54`](54_cinq_rendus_vides.md), qui décrit des piles **noires** :
  celles-là s'ouvrent et ne contiennent rien, celle-ci ne s'ouvre pas.
- **`data/paris4_candidats/m7_c0/rendu_161`** : pile entièrement noire — c'est l'un des cinq de
  `54`, et l'« IMPOSSIBLE » rapporté ici est **le correctif qui fonctionne** : l'instrument
  d'aujourd'hui refuse (`pile_vide`) ce que l'ancien comptait comme « 49 fenêtres avec
  matière ».

##### ✅ Câblé — et **incapable d'empirer les choses**

`profiler_une_surface.sh` demande son plan à l'instrument (`--shell`), rend les fenêtres
`RENDRE` d'abord, **garde leur pile** tant que des filles peuvent en dériver, puis dérive.

⭐ **Trois replis, chacun bruyant, et c'est ce qui rend le raccourci sans risque** : un plan
incalculable → chaque fenêtre est rendue comme avant ; une pile absente ou **inexploitable**
(`verifier_pile`) → la fenêtre est rendue ; une dérivation qui échoue → la fenêtre est rendue.
On ne peut donc jamais **perdre** une fenêtre à cause du raccourci ; au pire on ne gagne rien.
`DERIVER=0` le désactive entièrement, sans le retirer.

⚠ **Un seul site de dépôt dans le cache**, et il porte sa garde chez lui (`deposer_cache`). Il y
en avait deux — la branche dérivée et la branche rendue — et deux sites finissent par ne plus
poser la même garde ; celui qu'on oublie dépose un profil à moitié écrit, que **toutes** les
campagnes suivantes reliront comme un résultat.

##### ⚠⚠ Quatre contrôles à moi qui ne pouvaient pas échouer, et comment ils sont devenus vrais

Le témoin de ce fichier est passé de 33 à 50 contrôles, et **quatre des premiers étaient
faux** :

| ce qui n'allait pas | ce qui l'a remplacé |
|---|---|
| comparer des **numéros de ligne** pour dire « après » — muet dès que l'appel passe dans une fonction | la propriété : le dépôt est **gardé** par un profil non vide |
| `chk '[ $? = 0 ]'` — `$?` lit le retour du **harnais**, pas de la fonction | capturer le code **tout de suite** : `deposer_cache … ; RC=$?` |
| grepper le fichier **qui contient le contrôle** — il se compte lui-même | grepper le corps **privé de son bloc de témoin**, plus un contrôle qui vérifie que l'exclusion marche |
| des motifs qui matchaient la **prose du commentaire** | des motifs qui visent le **site d'appel** (`--shell`, `verifier_pile(Path(`) |

⚠ Et deux pièges de shell payés au passage : un motif traversant trois couches de guillemets
(`chk` → `eval` → `grep`) voit son `${…}` devenir une **ancre de fin de ligne** et ne matche
plus rien tout en ayant l'air correct ; et `grep -qF "--shell"` prend `--shell` pour une
**option**, donc le contrôle annonce que le code a disparu. `-e` le force à être un motif.

##### ⚠ Ce qui reste

Le raccourci est **câblé et sondé, pas encore exercé sur un vrai rendu** : la première campagne
de convergence sera la mesure. Ce qui est vérifié ici est la forme et les replis ; ce qui est
vérifié ailleurs est l'arithmétique (37 contrôles) et la parité des profils (6 sites, 23/23).

##### ⚠ Ce qui n'est PAS fait (historique)

~~Le raccourci n'est **pas encore câblé** dans `profiler_une_surface.sh`.~~ Il y faudrait garder le
rendu large vivant pendant toute la boucle des fenêtres, alors que le script le supprime par
défaut à chaque tour (`garder_rendu || rm -rf "$W/rendu"`, 562 Mo par pile) — c'est un
changement d'ordonnancement **et** de disposition sur disque dans un script qui produit des
résultats publiés. L'arithmétique, elle, est livrée et éprouvée.

⚠ **Piège d'outillage rapporté par un agent** : deux vérificateurs concurrents ont écrit leur
comparateur sous le **même nom** dans le scratchpad partagé, et l'un a écrasé l'autre entre
deux exécutions — donc deux résultats produits par deux codes différents. L'agent l'a vu et a
relancé sous un nom qui lui était propre. Un scratchpad partagé n'est pas un espace privé.

### ⭐⭐ Chantier B — un dossier par ROULEAU, et un manifeste JSON par rouleau

**Le besoin** : que ce qu'on possède d'un rouleau se lise d'un seul endroit, et que la mise à
jour soit une écriture dans **un** objet plutôt que dans quinze fichiers éparpillés.

**La forme proposée** :

```
data/
  PHercParis4/
    manifeste.json          ← l'objet unique : ce qu'on a, où, calculé quand, par quoi
    volumes/                ← boîtes zarr locales (prédictions, scan)
    couches/                ← rendus de couches téléchargés
    maillages/              ← tifxyz : traces, morceaux, chaînes
    campagnes/              ← résultats de campagne, un dossier par campagne
  PHerc1447/  …
  cache/rendus/             ← partagé entre rouleaux (chantier A)
```

Le **manifeste** est l'objet flexible demandé : une entrée par artefact, avec sa provenance
(commande, date, version du code), son coût, et son hash. C'est lui qui rend le reste
interrogeable, et c'est lui qui remplace « chercher dans quinze dossiers ».

⚠⚠ **La contrainte dure, et elle commande l'ordre du chantier** : des dizaines de scripts et
les blocs « Reproduire » de 57 documents écrivent `data/<campagne>/…` en dur. Donc :

1. **d'abord** un verbe `lplv chemin <rouleau> <genre> <nom>` qui rend le chemin — un seul
   endroit qui sait où sont les choses ;
2. **ensuite** la migration, avec des **liens symboliques** depuis les anciens chemins, pour que
   rien ne casse pendant la transition ;
3. **enfin** le retrait des liens, quand un garde-fou confirme que plus aucun script ni document
   ne cite un ancien chemin.

⚠ **Écrire la migration comme un script rejouable**, pas comme une session de `mv`. Une
réorganisation de 177 Go faite à la main n'est pas reproductible, donc pas vérifiable.

### ⭐⭐⭐ Chantier C — nommer le pipeline à plugins qui EXISTE DÉJÀ

**C'est le chantier le plus rentable, et c'est aussi celui qui demande le moins de code neuf**,
parce que l'architecture est déjà là — elle n'a simplement pas de nom.

Mesuré : sur **123 modules** de `analysis/src/`, **122 ont un `main()`**, **75 exposent
`--verifier`**, **63 exposent `--json`**. C'est-à-dire que **123 greffons de forme uniforme
existent**, sans registre et sans point d'entrée.

> ⚠⚠ Le skill (§7) dit de ne pas construire une architecture à plugins avant le **deuxième
> implémenteur réel**. Ici il y en a **cent vingt-trois**. La question n'est donc pas *faut-il
> des plugins*, elle est *pourquoi n'ont-ils pas de registre*.

**La forme** : un point d'entrée `lplv` qui découvre les modules, expose `lplv <verbe> --help`
dérivé de l'`argparse` du module, et `lplv --help` qui liste les verbes avec la première ligne
de leur docstring.

Ce que ça achète, et c'est la raison invoquée par l'auteur : **une aide qui ne peut pas
périmer**, parce qu'elle est dérivée du code et non recopiée à côté (skill `doc-derivee`).

⚠ **Ce qu'il ne faut PAS faire** : un registre à l'exécution avec cycle de vie, versions de
contrat et mode dégradé. Les modules sont dans le même dépôt, compilés ensemble : la découverte
par le système de fichiers suffit, et tout le reste serait le prix d'un liage tardif dont
personne n'a besoin ici (skill §7, tableau palier/plugin).

**Les paliers** tombent alors tout seuls, et le dépôt en a déjà trois de fait :

| palier | ce qu'il contient | ce qui le prouve |
|---|---|---|
| **prod** | ce que la branche de release porte | `src/outils/faire_la_release.sh` la construit déjà |
| **dev** | plus l'outillage de campagne | c'est ce qu'on lance tous les jours |
| **debug** | plus les sondes et les verbes de diagnostic | `--plancher`, les cartes, les sondes |

⚠ Le piège nommé par le skill (§7) s'applique déjà : **le palier que personne ne construit
pourrit**. La release est construite par un script ; le vérifier reste une tâche de ce chantier.

#### ✅ Livré le 2026-08-25 — `lplv`, et ce que la mesure a dit

![Les 218 greffons du dépôt](images/56_verbes.png)

```bash
./lplv --verbes --json > docs/verbes.json
uv run python src/figures/figure_verbes.py     # → docs/images/56_verbes.png
```

**218 verbes découverts, zéro nom ambigu, 98 qui s'auto-testent, 72 qui rendent du JSON.**
Rien n'est déclaré à la main : la famille vient du chemin, `--verifier` et `--json` sont lus
dans le fichier, le résumé est la première ligne de docstring — c'est-à-dire **exactement la
chaîne que le module donne déjà à son `argparse`**, donc l'aide de `lplv` et celle du module ne
peuvent pas diverger : c'est le même octet.

⭐ **`lplv <verbe> --help` EXÉCUTE le module avec `--help`.** L'alternative tentante — relire
son `argparse` pour en refabriquer une aide — produirait une **seconde description** de la même
chose, libre de dériver de la première, c'est-à-dire précisément la panne que ce point d'entrée
existe pour empêcher. On délègue ; il n'y a donc rien à tenir à jour.

Trois règles portent le reste, chacune sondée en la cassant :

| règle | ce qu'elle empêche | la sonde |
|---|---|---|
| un nom revendiqué deux fois est **refusé** | `lplv x` lancerait celui que le système de fichiers a mis devant, en silence | départager → 2 échecs |
| tout ce qui suit le verbe passe **verbatim** | manger un `--help` obligerait à écrire une seconde aide à côté | filtrer `--help` → 1 échec |
| un fichier en `_` n'est pas un verbe | `lplv __init__` ne veut rien dire | le réadmettre → 3 échecs |

**Et les paliers tombent tout seuls, mesuré plutôt qu'affirmé.** L'arbre allégé de la release a
été construit dans un dossier temporaire à partir de la seule liste `GARDES` : `./lplv --help`
y rend **204 verbes au lieu de 218**, sans erreur et sans configuration, parce que
`experiments/src` et `inference_xpu/src` n'y sont pas. C'est la définition d'un palier
**additif** — et le piège du skill §7 (« le palier que personne ne construit pourrit ») est
traité en ajoutant `lplv` aux `GARDES` : sans ça la release aurait porté `src/depot/lplv.py`
sans la commande qui le lance, soit la moitié d'une surface.

⚠ `os.execvp` et non `subprocess` : le verbe **remplace** le processus, donc son code de sortie
et ses signaux sont les siens. Un sous-processus ajouterait un maillon qui peut avaler un
Ctrl-C ou un code de retour — et un code de retour avalé est exactement ce qui fait lire un
échec comme un succès. Ce dépôt a payé ce piège trois fois dans la même journée, sous la forme
du code de sortie d'un pipeline.

⚠ **Ce qui n'est PAS fait, et qui appartient au chantier D** : les deux gardes-fous de
`src/outils/temoins.sh` (« batteries non lancées », « scripts sans appelant ») redérivent chacun
*leur* réponse à « quels sont les modules de ce dépôt », alors que `lplv --verbes --json` la
donne. Ce sont trois réponses à une question, et c'est le motif que ce dépôt paie en boucle. La
portée du premier a quand même été élargie ici, parce que la batterie neuve de `infer_ink.py`
en dépendait — mesuré : l'élargissement ne signale rien de neuf, il ferme un trou.

⚠ **Et un emprunt d'environnement du même genre que celui d'`inference/` reste ouvert** :
quatorze blocs « Reproduire » font `cd experiments` pour emprunter son venv. Mesuré le
2026-08-25 : la racine porte numcodecs, PIL, numpy, scipy et tifffile ; `experiments/.venv`
**n'a pas PIL**. C'est le même diagnostic, et il n'a pas été appliqué ici pour ne pas mélanger
deux chantiers dans un diff.

#### ✅ Le rangement en `src/` — livré le 2026-08-25, sur demande de l'auteur

> *« je ne veux plus qu'un dossier `src` à la fin »*, *« voir une centaine de fichiers python
> tous au même endroit ça donne vraiment mal au crâne »*, *« je veux à minima des
> plugin/module/famille avec namespace »*.

`analysis/src` (126 fichiers à plat) et `tools/` (73) deviennent **`src/` en dix familles**.
Les préfixes réels ont fourni trois d'entre elles (`figure_*` 37, `table_*` 10, `campagne_*`
12) ; les sept autres classent par **objet d'étude**, et c'est le dossier qui porte ce
jugement — pas une table à tenir à jour.

⭐ **`src/commun/` n'est pas un fourre-tout, c'est une mesure** : exactement les modules
importés par leurs frères. La première mesure en annonçait 8 ; elle était **fausse**, ancrée
sur `^import x` et aveugle à `import x  # commentaire`. Le remède n'a pas été de mieux
compter mais de **cesser de compter** : chaque module met toutes les familles sur son chemin,
donc un reclassement futur ne casse aucun import.

| ce que le déplacement a cassé | mesuré |
|---|---:|
| citations de chemin réécrites | **1011** dans **182** fichiers |
| scripts shell qui remontaient d'un cran vers la racine | 62 |
| modules dont le `sys.path` supposait un dossier plat | 50 |
| chemins **assemblés** que nulle réécriture ne peut voir | 12 |

⚠⚠ **Ce que `du` était à l'espace disque, la relecture l'est aux chemins** : mon estimation de
départ disait ~490 citations, la mesure en a trouvé **1011**. Deux fois plus.

**La descente des échecs, et aucun trouvé en relisant** : 37 (les extraits en ligne de
`temoins.sh` pointaient chacun vers un dossier) → 35 → 12 (mon insertion de `sys.path`
**ignorait l'indentation**, 18 occurrences étaient indentées, donc `IndentationError`) → 3
(sept chemins assemblés) → 1 → 0.

⭐ **Et le témoin de `lancer.sh` a attrapé une conséquence que personne n'aurait vue** : son
en-tête dit que le **gel** d'un script doit vivre à la profondeur que ce script suppose pour
retrouver la racine. Les scripts remontant désormais de deux crans, `.lances/` devient
`.lances/gel/`. La règle n'a pas changé, seule la profondeur — et c'est un auto-test qui l'a
dit, pas une relecture.

⚠ **Trois orphelins révélés, qui l'étaient déjà** : `fetch_normal_grids.py`, `telecharger.py`,
`valider_blocs.py`. Le garde « scripts sans appelant » ne scannait pas `tools/*.py` ; le glob
`src/*/*` a élargi sa portée sans qu'on le demande, et il les a trouvés.

⚠ **Ce qui n'a PAS bougé, avec la raison** : `tracecheck/` est **le livrable** que l'article
décrit et que la release identifie ; `experiments/` et `inference_xpu/` portent chacun leur
propre environnement. Les déplacer est une décision par dossier, pas un coup de balai.

### ⭐ Chantier D — l'extraction du dessin, et le rangement de `docs/`

#### ✅ Livré le 2026-08-26 — deux des quatre points, et trois trouvailles en chemin

**1. Le garde-fou lent : 160 s → 2,9 s.** Il lançait un `grep -r` sur tout le dépôt **par
fichier** (0,80 s × ~200). `src/depot/appelants.py` fait **un** parcours, indexe, puis cherche
dedans. ⚠ Et le coût s'était déplacé à 38 s dans ma première version — 210 scripts × 355 textes
× 7 motifs — jusqu'à ce qu'un test d'appartenance de chaîne écarte 99 % des paires avant
qu'une regex ne tourne.

⚠⚠ **Et il ne se tait plus.** L'ancien comptait comme appelant **toute occurrence du nom**,
prose comprise : trois orphelins réels signalés, puis silencieux au run suivant parce qu'un
document venait de les nommer. Une mention n'est pas un appelant — c'est même souvent le
contraire. Le nouveau ne compte que ce qui **exécute**, en sept formes, dont `lplv <verbe>` :
depuis que le dépôt a un point d'entrée, un script peut n'être lancé que par lui.

⭐ Ce que ça révèle : **27 scripts que rien n'exécute**. Ce ne sont pas des défauts, c'est de la
**dette de documentation** — aucun bloc ne dit comment les lancer. Signalé, jamais en échec :
une batterie rouge en permanence cesse d'être lue.

**2. `figure_commune.py` — quinze copies, quatre variantes, zéro image déplacée.** Elles ne
diffèrent que par les **tailles** demandées ; le mécanisme est identique. Une fonction
**paramétrée** les remplace toutes sans changer une figure, puisque chaque appelant passe les
siennes. ⭐ Unifier en imposant des tailles aurait déplacé quinze images pour du rangement,
c'est-à-dire exactement le refactor qu'on ne fait pas. Un garde-fou empêche le retour : *aucune
seconde définition de `_police` dans l'arbre*.

##### ⚠⚠ Trois trouvailles que seul le fait de construire les gardes a produites

- **Six images de `docs/` ne correspondaient plus à leurs données**, et rien ne le disait :
  `51_appuis.png` est commise le 23 août, son entrée bouge le 24, l'image n'est jamais refaite.
  Une figure périmée s'affiche exactement comme une figure à jour.
  `src/depot/fraicheur_des_figures.py` régénère dans un dossier temporaire et compare les
  octets — **4,9 s pour les 36 figures**. ⚠ Il ne touche jamais `docs/images/` : dire qu'une
  image est périmée et la remplacer sont deux actes.
- ⚠⚠ **Une régression que J'AVAIS introduite** : six figures écrivaient dans `../docs/images/`,
  ce qui était juste quand elles tournaient depuis `inference/` et ne l'est plus depuis que je
  les ai repointées sur la racine. `../docs` n'existe pas. Rien ne l'a vu, parce que leurs
  batteries n'écrivent pas d'image. Leur racine se dérive désormais du fichier, jamais du
  répertoire courant — c'est ce qui les rend lançables depuis n'importe où, `lplv` compris.
- ⚠ **Ma première version du garde de fraîcheur ne reconnaissait qu'une forme de déclaration
  sur trois** : elle jugeait 11 figures sur 36 tout en annonçant « chacune ». Un libellé qui
  affirme ce que l'assertion ne vérifie pas.

##### ⚠ Ce qui reste du chantier D

- **`docs/` séparé par nature** : 58 `.md`, 345 `.json`, 72 `.png`, 79 `.log`. ⚠ Les blocs
  « Reproduire » citent ces chemins — c'est `src/depot/deplacer.py` qui doit le faire, avec son
  refus de laisser une citation pendante.
- ~~**`.lances/` se purge**~~ ✅ **fait** : rétention **par script** (les 5 plus récents,
  `GARDES_PAR_SCRIPT`), écrite dans `lancer.sh` — le script qui les crée, comme le plan le
  demandait. **197 → 63 fichiers.** ⭐ Par script et non globale : garder les N plus récents
  tout court effacerait toute trace d'un script lancé une seule fois, c'est-à-dire précisément
  celui dont on veut la trace. ⚠⚠ Et un lancement **vivant** n'est jamais effacé, quel que soit
  son âge : perdre le `.pid` d'un processus en cours ferait perdre le seul moyen de le
  retrouver, et `--fond` existe pour des campagnes qui durent des heures. ⚠ La purge **se
  dit** : une suppression silencieuse d'artefacts est ce qui fait chercher une demi-heure un
  journal qu'on a soi-même effacé.

  > ⚠⚠⚠ **Et elle a effacé trop, pour de vrai.** Le premier passage a ramené `.lances/` de
  > **197 fichiers à 4**, et `.lances/` est gitignoré : c'est perdu. La fonction passe pourtant
  > son test sur fixture — 5 par script, vérifié — et **je n'ai pas su reproduire le
  > mécanisme**.
  >
  > ⭐ La leçon n'est donc pas « écrire un meilleur motif », puisque je ne sais pas lequel était
  > faux. C'est qu'une purge **capable** d'effacer la quasi-totalité d'un dossier doit
  > **refuser** au lieu de faire confiance à son propre calcul. `PART_MAX_PURGEE` vaut **50 %**
  > par défaut : au-delà, c'est qu'on s'est trompé de dossier ou de motif, jamais qu'il y avait
  > vraiment tant à jeter. Le refus se dit sur la sortie d'erreur, et il est sondé.
  >
  > ⚠ Le plafond gagne sur la rétention, et c'est le bon ordre — mais il fallait le dire : ma
  > propre fixture demandait d'effacer 62 %, donc le plafond la bloquait, et le contrôle
  > mesurait le plafond en croyant mesurer la rétention.


Deux petites choses, groupées parce qu'elles ne coûtent presque rien.

1. **`analysis/src/figure_commune.py`** : `_police`, `_pixels`, la palette. C'est le seul endroit
   où des copies ont **réellement divergé** (4 variantes de `_police`). ⚠ Et un garde-fou dans
   `src/outils/temoins.sh`, sur le modèle de « batteries non lancées » : *aucune seconde définition
   de `_police` dans l'arbre*. Sans lui, les copies reviendront.
2. **`docs/` séparé par nature** : la prose reste, les 341 JSON de résultats et les ~57 logs
   partent dans `docs/resultats/` et `docs/journaux/`. ⚠ **Les blocs « Reproduire » citent ces
   chemins** — même précaution que le chantier B, et le garde-fou `src/outils/images_des_docs.sh`
   existe déjà pour les images.
3. **`.lances/` se purge** : 196 fichiers, ~65 lancements. Une rétention (les N derniers, ou
   les 30 derniers jours), écrite dans le script qui les crée.
4. ⚠⚠ **Le garde « scripts sans appelant » se tait dès qu'un document NOMME l'orphelin.**
   Constaté le 2026-08-25 : trois orphelins réels signalés, puis silencieux au run suivant
   parce que ce document venait de les citer. Une mention en prose n'est pas un appelant —
   c'est même souvent le contraire, on écrit le nom d'un script *parce qu'il ne sert plus*.
   Le remède est de ne compter comme appelant qu'une **exécution** (`bash x.sh`,
   `python x.py`, une ligne `run`), pas une occurrence du nom.
5. ⚠ **Le garde-fou « scripts sans appelant » parcourt tout le dépôt, 196 fois.** Mesuré :
   **0,78 s** pour un `grep -rl` sur l'arbre, et il en fait un **par fichier** — soit ~2,5 min
   à lui seul, sur les 203 Go (dont `data/` et les trois `.venv`). Le remède est un seul
   parcours qui construit un index, puis 196 recherches dedans. ⭐ C'est le contrôle le plus
   lent de la batterie, et le seul dont le coût croît avec les **données** plutôt qu'avec le
   **code** — donc il empirera à chaque campagne.

```bash
/usr/bin/time -f "%e s" grep -rl --include='*.py' -- "figure_portee.py" . >/dev/null
ls analysis/src/*.py tools/*.sh | wc -l   # x ce nombre
```

---

### ⭐ L'outil qui rend les trois autres chantiers possibles — `permalien.py` (livré)

Un ménage se heurte tout de suite à la même question : **un document cite un fichier qu'on
retire, que devient la citation ?** La réponse évidente — un `sed` vers une URL GitHub —
produit des liens morts *en silence*, ce que ce dépôt paie en boucle. Ce qui mérite du code
n'est pas la fabrication de l'URL, qui tient en une ligne, c'est l'**invariant** :

> ⭐ un permalien ne vaut que si son commit est **sur le distant** et que le chemin **existe**
> à ce commit. Les deux sont vérifiables, donc ils sont vérifiés, jamais espérés.

⚠ Le piège concret, mesuré : `HEAD` était **43 commits en avance** sur `origin/main`. Un lien
vers `HEAD` aurait rendu 404 pour tout le monde sauf cette machine, et la panne ne se serait vue
qu'après un `push`, c'est-à-dire trop tard pour la relier à sa cause. L'outil vise donc le
commit le plus récent qui contient le chemin **et** qui est un ancêtre de la référence distante
— aucun `push` requis, aucune attente.

Trois refus délibérés, chacun une panne évitée : un chemin jamais poussé n'est **pas** lié et
est **nommé** ; une mention dans un bloc de code reste intacte (`python htr/src/coherence.py`
est une commande, pas une référence) ; une mention déjà liée n'est pas ré-enrobée, donc une
seconde passe est un **no-op** — asserté.

⚠⚠ **Et un fait mesuré qui borne ce que le lien promet : ce dépôt est PRIVÉ.** Sa racine GitHub
rend 404 sans session, quand la même URL sur un dépôt public du même compte rend 200. Un
permalien vaut donc pour l'auteur, pas pour un lecteur extérieur — acceptable dans un document
interne, **piège dans un texte de soumission**, où un 404 est pire qu'un chemin mort : un chemin
dit honnêtement « ce fichier était là », un lien cassé dit « ce lien est cassé ». La parade est
dans la forme même de l'URL, qui porte le commit et le chemin **verbatim** : `git show
<commit>:<chemin>` marche depuis n'importe quel clone, connecté ou non. Un contrôle le garantit.

`src/depot/permalien.py`, 34 contrôles, deux sondes (ignorer les blocs de code → 4 échecs ;
laisser un préfixe mordre son voisin, donc confondre `inference` et `inference_xpu` → 1 échec).
Il resservira aux chantiers **B** et **D**, qui déplacent respectivement des données et des
documents.

## 4. ⚠⚠ Ce qu'on décide de NE PAS faire, et pourquoi

C'est la partie que le skill dit qu'on oublie toujours d'écrire.

| Écarté | La raison, mesurée |
|---|---|
| **Un grand refactor monolithique** | 0,8 % de duplication réelle. Les chiffres ne le justifient pas, et un diff que personne ne peut relire est approuvé, pas relu |
| ~~**Supprimer `inference/`**~~ **FAIT le 2026-08-25** | la raison écrite ici est tombée à la mesure : les 25 sites étaient des **emprunts** à un environnement plus pauvre que la racine. Le témoin CPU est devenu `--device auto/cpu`, un mode et non un dossier |
| **Fusionner `analysis/` et `tools/`** | frontière réelle et à sens unique : `tools/*.sh` orchestre, `analysis/src/*.py` mesure. Aucune mesure n'appelle un outil. C'est déjà la bonne direction (skill §7) |
| **Un registre de plugins à l'exécution** | même dépôt, même build : la découverte par le système de fichiers suffit. Le liage tardif n'a aucun demandeur |
| **Effacer les 17,4 Go de « doublons »** | le proxy *même nom + même taille* **surcompte** sur les chunks zarr. À hacher avant d'effacer — et un effacement n'est pas réversible |
| ~~**Toucher aux `.venv`**~~ **partiellement fait** | les « 16,6 Go » n'existaient pas (liens durs, §1.1). `htr/` et `inference/` sont partis avec leur code ; `experiments/` et `inference_xpu/` gardent le leur, ils portent de vraies sources |
| **Réécrire les 57 documents** | ils portent des mesures datées. Les chemins qu'ils citent se réparent par des liens, pas par une réécriture |

---

## 5. L'ordre recommandé, et pourquoi celui-là

1. **C (le registre `lplv`)** en premier : aucun risque, aucun déplacement de données, et il
   donne le vocabulaire dont B a besoin (`lplv chemin …`).
2. **A (le cache par contenu)** ensuite : c'est le seul qui rapporte des gigaoctets et du temps,
   et il est local à un fichier.
3. **D (le dessin, `docs/`, `.lances/`)** : bon marché, et le garde-fou empêche la rechute.
4. **B (la réorganisation de `data/`)** en dernier : c'est le seul qui casse des chemins, donc
   le seul qui a besoin que tout le reste soit stable.

⚠ **Et chacun se termine par la même porte** : `./src/outils/temoins.sh` vert, avec le compte relu et
réécrit dans `docs/31_roadmap.md` et `HANDOFF.md`.

---

## 6. La porte de sortie, avant d'implémenter quoi que ce soit

Les cinq réponses que le skill exige, pour le chantier qu'on attaquera :

1. **le comportement observable qui change** — § 2 ci-dessus, quatre énoncés constatables ;
2. **l'ossature en stubs** — à écrire, une par chantier, avec des noms définitifs et des corps
   qui **lèvent** ;
3. **ce qui est injecté** — le chemin d'un rouleau, le cache, le journal. Rien d'autre : ce sont
   les trois choses qui touchent le monde ;
4. **les points d'extension justifiés par un deuxième cas RÉEL** — le registre l'est par 123 ;
   rien d'autre ne l'est ;
5. **ce qu'on a décidé de ne pas faire** — § 4 ci-dessus.
