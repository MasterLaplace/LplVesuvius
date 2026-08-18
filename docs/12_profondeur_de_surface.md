# La profondeur de surface : un instrument de tracé sans vérité terrain

> ⚠⚠ **L'instrument a changé deux fois. Lire le §10 en premier** — il donne la version
> courante et dit ce que les §1 à §9 avaient de faux. Le reste est conservé parce que
> la trace des corrections vaut plus que la propreté du récit.

2026-08-18. Né d'une enquête sur l'échec du détecteur d'encre sur Scroll 4 (`09` §12),
et devenu autre chose que ce qu'il cherchait.

---

## 1. D'où ça vient

Le détecteur GP-2023 lit **26 couches** d'une pile — ici les couches 15 à 40.

⚠ **La convention est vérifiée à la source, pas supposée.** Le tutoriel officiel
(miroir local, `site/scrollprize.org/tutorial_VC.html`) donne la commande qui les
engendre :

```
vc_layers_from_ppm -v "/full_scrolls/$SCROLL" -p "$SEGMENT.ppm"     --output-dir layers/ -r 32 -f tif
```

> *« The result of this process are the 65 tifs in the /layers/ directory, also
> referred to as a "surface volume". »*

**Rayon 32, 65 couches : la couche 32 EST la surface tracée**, et les autres s'en
écartent d'un voxel par indice. Si la trace suit bien la feuille, la surface tombe donc
au même indice partout — au voisinage de 32 — et le modèle la trouve là où il la
cherche. ⚠ Sans cette vérification, tout ce qui suit serait un raisonnement sur une
convention devinée.

La première cause candidate à l'échec sur Scroll 4 était donc : *et si la surface
n'était pas dans la fenêtre lue ?* Elle se teste **sans rien télécharger** — la réponse
est déjà dans les couches qu'on a.

## 2. La mesure

`analysis/src/depth_profile.py`. Pour chaque couche, sur une fenêtre : l'**intensité
moyenne** (où est la matière) et le **contraste local**, écart-type d'un passe-haut 3×3
(où est la *structure*). C'est le second qui localise : il pique là où les fibres et
l'encre sont nettes, c'est-à-dire à la surface.

⚠ **Chaque profil est normalisé dans sa propre pile.** Deux campagnes de scan n'ont ni
la même dynamique ni le même gain ; comparer des niveaux bruts comparerait les
scanners. Ce qui se compare est la **forme** — où est le pic.

⚠ **Les couches sont lues une fois chacune, toutes fenêtres confondues.** Une couche
fait ~500 Mo et se décode entière ; boucler sur les fenêtres à l'extérieur relirait la
pile autant de fois qu'il y a de fenêtres.

⚠ Une fenêtre sans matière n'a pas de surface : celles dont l'intensité maximale reste
sous la moitié du maximum global sont **écartées et comptées**.

## 3. 🎯 Ce qu'on voit

Le segment de Scroll 1 qui donne l'**AUC 0,925**, profil sur une fenêtre : une courbe
**unimodale propre**, pic de contraste à la couche **26**, au milieu de ce qui est lu.
Le même profil sur Scroll 4, à l'endroit exact où l'inférence a tourné : le contraste
est **maximal à la couche 15** — la première lue — et décroît jusqu'à 40. **La surface
est au-dessus de la fenêtre.**

⚠⚠ Et une autre fenêtre du **même** segment Scroll 4 donne son pic à la couche **40**,
l'autre bord. Les deux extrêmes, sur le même segment. C'est ce désaccord qui a
transformé un diagnostic en instrument.

### Le balayage complet — trois segments, même plage de couches

| segment | rouleau | pic dans le **tiers central** | écart interquartile | pic **au bord** |
|---|---|---:|---:|---:|
| `20231022170901` | Scroll 1 | **63 %** | **4,0** couches | 15 % |
| `20230909121925` | Scroll 1 | 50 % | 11,5 | 37 % |
| `scroll4_20231111135340` | Scroll 4 | **7 %** | **22,0** | **61 %** |

⚠ Le filtre `--from-layer 15 --to-layer 40` n'est pas un confort : `20231022170901` a
été téléchargé avec **38** couches et les deux autres avec 26. Sans restreindre à une
plage commune, les « tiers centraux » n'ont pas la même largeur et les pourcentages ne
veulent pas dire la même chose. Le chiffre de ce segment passe de 76 % à 63 % une fois
la comparaison rendue légitime.

### ⚠⚠ La forme importe autant que la position

Scroll 4 n'est pas simplement **décalé** : sa distribution est **bimodale**, 92 fenêtres
piquant à la couche 15 et 49 à la couche 40, avec un milieu presque vide. Un décalage
uniforme — « ce rouleau engendre ses couches autour d'un autre indice » — déplacerait la
médiane **sans gonfler l'écart interquartile**. Or celui-ci passe de 4,0 à **22,0**.

> **La surface de ce segment ne se tient pas à une profondeur constante : elle
> voyage d'un bout à l'autre de ce qui est lu.** C'est la signature d'une trace qui
> dérive, et c'est exactement le défaut que le déroulement doit éviter.

## 4. Pourquoi c'est utile

Cette mesure ne demande **ni vérité terrain, ni modèle d'encre, ni juge**. Elle ne lit
que les couches, qui existent pour tout segment publié. C'est la première grandeur du
dépôt qui parle de la **qualité d'une trace** sans passer par ce qu'on arrive à lire
dessus — et l'objectif est le déroulement, pas la lecture.

Et elle explique l'échec de `09` §12 sans invoquer un décalage de domaine : le modèle
ne s'est pas trompé sur l'encre de Scroll 4, **il a regardé à côté**.

## 5. ⚠ Ce que ça ne dit PAS

1. **Trois segments, deux rouleaux.** Ce n'est pas un corpus. La grandeur est plausible
   et mesurée ; elle n'est pas validée sur une population.
2. **Elle ne classe pas la qualité de détection d'encre.** `20230909121925` est celui
   qui donne l'AUC 0,925, et il est **moins bon** ici que `20231022170901` (50 % contre
   63 %). Prétendre qu'elle prédit la lisibilité répéterait exactement l'erreur que la
   tâche D a coûté cher à écarter (`06` §3.8).
3. **La bimodalité pourrait venir de l'engendrement des couches** plutôt que de la
   trace. Pour les départager il faudrait un segment dont on sait indépendamment qu'il
   est propre, avec sa pile complète.
4. Le passe-haut 3×3 est une mesure de netteté locale parmi d'autres. Un autre noyau
   déplacerait les chiffres ; il ne déplacerait pas un facteur 7.

## 6. ⚠⚠ Avec la pile complète 0–40 : le trait est plus dur

Les couches 0 à 14 ont été téléchargées (7,5 Go) pour voir **sous** la fenêtre lue.
Résultat sur le segment Scroll 4, 230 fenêtres :

| pic de contraste | fenêtres |
|---|---:|
| **couche 0** (le bord absolu de la pile) | **100** |
| couches 1 à 39 | 104, dispersées |
| **couche 40** | **26** |

⚠ Un pic au bord peut être un **artefact de bord** — un passe-haut réagit fort à une
troncature. La forme le réfute : à l'endroit exact où l'inférence a tourné
(`top 2560, left 20000`), le contraste **décroît de façon lisse et monotone** de 1,000 à
la couche 0 jusqu'à 0,000 à la couche 40, et l'intensité moyenne fait de même (plateau
0,99–1,00 des couches 0 à 5, puis chute à 0 vers la couche 36). C'est une courbe, pas
une pointe.

> **La matière occupe les couches 0 à ~28 et le reste est du vide.** La surface tracée
> est la couche **32** : elle tombe donc **dans le vide**, à une vingtaine de voxels au
> moins de la feuille — soit plus qu'une épaisseur de feuille (142,8 µm, `11` §3).
> **La trace est posée à côté du papyrus.**

Pour comparaison, le segment Scroll 1 qui donne l'AUC 0,925 a son pic **à l'intérieur**
de ce qui est lu (couche 26), avec une courbe unimodale propre qui retombe à zéro vers
34 puis **remonte** légèrement en 39–40 — la feuille suivante.

### ⚠⚠ CORRECTION — la pile complète dément mon arithmétique de ce matin

J'avais écrit, sur la fenêtre 0–40 : *« l'écart vaut une épaisseur de feuille, donc
c'est la signature d'un saut de spire »*. Le raisonnement importait le pas
inter-feuilles **mesuré sur PHerc0172** (142,8 µm, `11` §3) vers **PHerc1667**, qui est
un autre rouleau avec sa propre compaction. **C'est le piège nº 6 du dépôt — un chiffre
emprunté n'est pas une mesure — et je l'ai commis.**

Les 24 couches manquantes (41 à 64) ont été téléchargées. La pile complète le dément :

| couche | ce qu'on voit |
|---|---|
| 0 à ~28 | matière, contraste **maximal dès la couche 0** |
| 34 et **46** | deux **creux** d'intensité — du vide |
| 48 à 64 | matière **qui remonte encore** à la dernière couche |

Les deux blocs sont donc séparés de **plus de 64 voxels** entre leurs cœurs, soit
plusieurs fois le pas de PHerc0172. L'égalité que j'annonçais n'existe pas.

### 🎯 Ce qui se mesure sans rien emprunter

`analysis/src/stack_structure.py`. La question devient : **à quelle distance la couche
tracée est-elle du sommet de matière le plus proche, dans sa propre pile ?**

⚠ Un maximum atteint **au bord** n'est pas un sommet — c'est le flanc d'un sommet situé
dehors. Il est rapporté comme une **borne inférieure**, jamais comme une distance.

| segment | sommets de matière | distance de la couche 32 au plus proche |
|---|---|---|
| `20230909121925` (AUC 0,925) | **16 et 26** | **6 voxels (47 µm)** |
| `scroll4_…` (pile complète 0–64) | **aucun dans les 65 couches** | **≥ 32 voxels (253 µm)** |

Six voxels sur Scroll 1 : l'ordre d'une demi-épaisseur de feuille, ce qu'on attend
puisque le contraste marque la **face encrée** et non le milieu de la feuille. **La
trace est sur la feuille.**

⚠⚠ Sur Scroll 4, **aucun sommet n'existe dans la pile entière** : le contraste est
maximal dès la couche 0 *et* monte encore à la couche 64. La surface tracée est posée
entre deux blocs de matière dont **aucun cœur n'est visible**, à 253 µm au moins du plus
proche. Ce n'est plus une extrapolation depuis une demi-fenêtre : c'est tout ce que le
volume de surface contient.

⚠ Ce qui reste **non tranché** : dire que c'est un *saut de spire* demanderait le pas
inter-feuilles **de ce rouleau-là**, qui n'est pas mesuré. Ce qui est établi, c'est que
la trace n'est sur aucune des deux feuilles.

⚠ Et la bimodalité demeure : 100 fenêtres au bord bas, 26 au bord haut. **Aucune plage
unique ne peut servir tout le segment.** Ce n'est pas un décalage constant qu'on
corrigerait avec un `--start-layer` ; c'est une trace qui n'est pas sur la feuille au
même endroit d'un bout à l'autre.

## 7. 🎯 Le segment entier, sur la pile complète — et le verdict

Balayage des 232 fenêtres avec matière, sur les **65** couches :

| où tombe le pic de contraste | fenêtres |
|---|---:|
| **couche 0** (bord bas) | 45 — **19 %** |
| **couche 64** (bord haut) | 96 — **41 %** |
| **à un bord, donc cœur HORS du volume de surface** | **141 — 61 %** |
| à l'intérieur | 91 — 39 % |
| dans le **tiers central**, près de la couche tracée | **3 %** |

Écart interquartile : **61 couches** — c'est-à-dire la pile presque entière.

> **Pour 61 % de ce segment, la feuille n'est pas dans le volume de surface du tout.**
> Et pour 3 % seulement le cœur de matière est près de la couche 32, là où une trace
> posée sur la feuille le mettrait.

⚠⚠ **Conséquence directe, et elle disqualifie le test que je venais de lancer** : si le
cœur est hors des 65 couches, **aucune fenêtre de 26 couches prise dedans ne peut le
contenir**. Décaler `--start-layer` ne pouvait pas sauver la détection sur la majorité
du segment — le test était sous-dimensionné par construction, et la mesure le disait
déjà avant que je le lance.

## 8. Ce que ça règle

L'échec de `09` §12 n'est pas d'abord un décalage de domaine, ni un mauvais choix de
couches. **Il est en amont** : on ne détecte pas d'encre sur une surface que le volume
de surface ne contient pas.

C'est aussi la raison pour laquelle cet instrument mérite d'exister : il se calcule
**avant** toute inférence, en quelques minutes, à partir des seules couches. Une passe
d'encre de 43 minutes sur un segment à 61 % hors feuille est du temps dépensé pour un
résultat qu'on pouvait prédire.

## 9. La suite que ça ouvre

✅ **Fait, et négatif** : l'inférence relancée sur `--start-layer 0` donne une carte
**très proche** de la première (corrélation de rang **+0,700**, **88,7 %** d'accord de
classement à logit 0, encre 10,06 % contre 9,71 %) et le juge y **refuse tous les
panneaux**, y compris la bande à 18,32 % d'encre — lisibilité **1 ou refus**, contre
1 à 3 auparavant. Recentrer a rendu le négatif **plus net**, pas positif.
⚠ Mais §7 explique pourquoi ce test ne pouvait pas trancher : le cœur de matière est
hors de la pile pour 61 % du segment.

⭐ **Valider l'instrument sur un corpus.** Les couches sont publiées pour tout segment :
c'est un téléchargement, pas une décision. La prédiction à faire d'avance, pour qu'elle
puisse échouer : *un segment dont moins de ~20 % des fenêtres ont leur pic dans le tiers
central ne donnera pas d'encre lisible.*

⭐ **Chercher la vraie feuille.** Le cœur de matière est hors des 65 couches ; il serait
retrouvé en engendrant un volume de surface plus épais (`vc_layers_from_ppm -r 64`) ou
en corrigeant la trace. C'est du côté du déroulement, donc de l'objectif.

## Reproduire

```bash
cd inference_xpu
# une fenêtre, profil détaillé
uv run python ../analysis/src/depth_profile.py ../data/layers/<segment> \
    --top 2560 --left 20000 --size 1024
# le segment entier
uv run python ../analysis/src/depth_profile.py ../data/layers/<a> ../data/layers/<b> \
    --grid --size 512 --step 1024 --from-layer 15 --to-layer 40 \
    --out ../docs/profil_grille.json
```


---

## 10. ⚠⚠ L'instrument corrigé — 2026-08-18, seconde moitié

Deux défauts trouvés en portant la mesure sur un autre type de volume. Aucun n'a été
trouvé en relisant le code.

### Défaut 1 — le contraste ne localise pas la matière

Jusqu'ici le pic était celui du **contraste local** (écart-type d'un passe-haut 3×3).
Sur les piles à 7,91 µm, contraste et intensité piquent au même endroit, donc rien ne
distinguait les deux. Sur un volume de surface à **2,4 µm**, la courbe moyenne de
contraste est un **U** :

```
couche    0   →  0,648      maximal
couche   36   →  0,418
couche   63   →  0,254      minimal, DANS la feuille
couche  108   →  0,570      maximal
```

pendant que l'**intensité** pique franchement à la couche **36**. Un passe-haut suit
les **interfaces et le bruit** ; à 2,4 µm l'intérieur d'une feuille est un bloc dense
assez uniforme et les bords de pile tombent dans les interstices. À 7,91 µm la
distinction ne se voyait pas.

> **L'intensité est le localisateur ; le contraste ne l'est pas.**

⚠ Trouvé en **affichant la courbe** au lieu de faire confiance à son argmax. Les deux
courbes sont désormais rapportées côte à côte, et ce n'est pas un détail d'affichage :
c'est ce qui empêche de relire l'une pour l'autre.

Effet sur les chiffres, mêmes segments, même balayage :

| segment | contraste, tiers central | **intensité, tiers central** |
|---|---:|---:|
| `20231022170901` | 63 % | **96 %** |
| `20230909121925` (AUC 0,925) | 50 % | **80 %** |
| `scroll4_…` | 7 % | **19 %** |

La séparation passe de « 50–63 contre 7 » à « **80–96 contre 19** ».

### Défaut 2 — « le tiers central » ne veut pas dire la même chose partout

Le tiers central se rapporte à **la fenêtre lue**. Or la fenêtre 15–40 d'une pile de 65
n'est **pas centrée sur la couche 32**, qui est la surface tracée — alors que sur un
volume de surface, elle l'est. Les deux mesures ne portaient donc pas sur la même chose.

**Remplacé par une grandeur sans convention : l'écart entre le pic de matière et la
surface tracée, en micromètres.**

| segment | écart médian | p90 |
|---|---:|---:|
| `20231022170901` (Scroll 1) | **24 µm** | 40 µm |
| `20230909121925` (AUC 0,925) | **32 µm** | 63 µm |
| `scroll4_…` | **63 µm** | **134 µm** |

⚠ **Ces trois chiffres sont des bornes INFÉRIEURES** : la fenêtre 15–40 tronque, donc un
pic réellement hors fenêtre est écrêté à son bord. 37 % des fenêtres de Scroll 4 sont
dans ce cas, donc son écart réel est plus grand que 63 µm.

### ⭐⭐ Et le vrai débloquage : lire le profil à distance

Les volumes de surface sont publiés en **OME-Zarr** :

```
shape [109, 21380, 115820]   chunks [109, 128, 128]   dtype u1, SANS compression
```

**Un chunk contient toute la colonne de profondeur d'une fenêtre de 128×128.** C'est
exactement l'unité dont le profil a besoin. Mesuré : **1,78 Mo et 1,03 s** par fenêtre,
contre 32 Go pour télécharger une pile.

Trois conséquences, et la troisième est la plus importante :

1. Une population de segments devient une affaire de minutes, pas de jours.
2. **Aucune troncature** : la colonne est entière, donc l'écart à la trace est une
   mesure et non une borne.
3. Ces volumes sont ceux de la campagne **ESRF à 2,4 µm** — donc `06` §3.6 (« effet de
   la campagne de scan ») se mesure par la même occasion, sur les mêmes segments.

`analysis/src/zarr_depth.py`, `tools/lister_volumes_surface.sh`.

### ⚠ La prédiction est REPOSÉE, parce que changer de statistique l'invalide

J'avais écrit : *« sous ~20 % de fenêtres au tiers central, pas d'encre lisible »* — pour
la statistique de **contraste**. Elle ne s'applique plus. La nouvelle, posée **avant**
la campagne sur corpus :

> **Un segment dont l'écart médian entre le pic de matière et la surface tracée dépasse
> ~50 µm ne donnera pas d'encre lisible.**

⚠ Le seuil est le **milieu de l'intervalle observé** entre les deux groupes connus
(24–32 µm contre ≥63 µm). C'est le choix le moins arbitraire disponible à n = 3, et il
est provisoire par construction. Il est écrit ici pour pouvoir échouer.
