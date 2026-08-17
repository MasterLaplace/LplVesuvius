# L'onde radiale, le dépliage polaire, et quatre candidats

2026-08-17. L'idée de l'auteur — *« envoyer une onde traversant toutes les couches
depuis le centre »* — menée jusqu'à une liste d'endroits précis à examiner.

**Fichiers** : `experiments/src/excision/{radial,fusions,fusion_scan}.py`.
Aucune mesure de ce document n'est en `python -c` (règle `06` §5.6, payée le jour même).

---

## 1. ⚠⚠ Le code de la première mesure avait été perdu

Le résultat « 158 feuilles, 11,2 m de papyrus » était dans un document et **le calcul
nulle part** : il avait été lancé en ligne de commande. Récupéré du transcript de
session et installé dans `radial.py`.

**Contrôle de la récupération** — c'est ce qui distingue « j'ai retrouvé quelque
chose » de « j'ai retrouvé le bon » :

| | attendu | obtenu |
|---|---|---|
| feuilles par rayon | 158 | **158** |
| rayon extérieur | 22,7 mm | **22,7 mm** |
| longueur du papyrus | 11,2 m | **11,2 m** |
| centre re-dérivé de zéro | — | **écart 0,0 voxel** |

Le centre vit désormais dans `data/axes/PHerc0172.json`, plus dans `/tmp` où la
version inline l'écrivait — donc la mesure survit à un redémarrage.

## 2. ⚠ « Longueur » désignait trois choses

Malentendu réel avec l'auteur, levé par la mesure :

| grandeur | PHerc0172 |
|---|---|
| **longueur axiale** — le rouleau posé debout | **164 mm** |
| diamètre — 2 × le rayon extérieur | 48 mm |
| papyrus **déroulé** — la spirale mise à plat | ~11 à 14 m |

Le rouleau occupe 163,9 des 164,7 mm scannés : le scan est taillé au ras.

⚠ **Et le sens de la borne avait été noté à l'envers.** Deux feuilles fondues comptent
pour une, donc les spires vraies sont ≥ au compte, et la longueur **croît** avec les
spires (140 → 9,98 m ; 200 → 14,26 m). C'est donc une borne **inférieure**. ⚠ Sens
garanti par cet argument seul : un pic parasite pousse en sens inverse, et ce taux
n'est pas mesuré — donc **ordre de grandeur**, pas borne certifiée.

## 3. Le profil le long de z — deux échantillonnages qu'il ne faut pas mélanger

Idée de l'auteur : balayer *z* pour obtenir une courbe plutôt qu'un point.

⚠ **Les deux buts demandent des échantillonnages opposés** :

| but | échantillonnage | pourquoi |
|---|---|---|
| estimer la **longueur** | **uniforme** | une moyenne non biaisée |
| localiser un **dégât** | **dichotomique** | raffiner là où le compte saute |

Raffiner pour le premier sur-échantillonnerait les tranches atypiques et **tirerait la
moyenne vers elles**. D'où deux passes dans `radial.py profil`, dont la seconde
n'alimente jamais la statistique de la première.

⚠ **Et la moyenne ne corrige pas le biais, seulement le bruit** : toutes les tranches
sous-comptent leurs fusions, donc penchent du même côté. C'est le **maximum** sur *z*
qui approche le mieux ce que le rouleau portait — une tranche abîmée perd des spires,
elle n'en invente pas.

Premiers résultats (mesure en cours) :

| z | feuilles | rayon | longueur |
|---:|---:|---:|---:|
| 1 336 | 176 | 25,1 mm | 13,87 m |
| 1 929 | 167 | 23,9 mm | 12,54 m |
| 2 521 | 173 | 24,2 mm | 13,15 m |
| 3 114 | 162 | 23,2 mm | 11,82 m |
| 3 707 | 170 | 23,8 mm | 12,71 m |
| 4 300 | 160 | 23,5 mm | 11,82 m |
| 6 967 | 158 | 22,7 mm | 11,27 m |

La variation est **réelle et non du bruit** : le rouleau est nettement plus épais à
une extrémité (25,1 mm) qu'au milieu (22,7 mm).

## 4. Le dépliage polaire : la représentation qui débloque tout

`radial.py deplier` transforme la coupe en (rayon × angle), 3000 × 18 850.

![Coupe dépliée](images/11_polaire.png)

Et à pleine résolution angulaire, les feuilles se lisent une à une :

![Détail du dépliage](images/11_polaire_zoom.png)

⚠ **Correction d'une attente** : à grande échelle les spires ne sont **pas**
horizontales, ce sont de larges dômes — PHerc0172 n'est pas concentrique autour d'un
centre unique à cette coupe, il est écrasé. Le dépliage n'exige donc pas la
concentricité, seulement que les feuilles varient **doucement** avec l'angle (dérive
mesurée : 0,125 voxel par colonne).

⚠ **L'échantillonnage angulaire est fixé par la circonférence extérieure.** À un rayon
*r*, un degré couvre `r·π/180` pixels : un pas confortable pour le cœur perdrait de la
matière au bord, et une fusion manquée au bord est précisément ce qu'on cherche.

## 5. ⚠⚠ Quatre formulations, trois échecs, et ce que chacun a appris

Localiser les fusions a demandé quatre tentatives. **Les échecs sont conservés parce
qu'ils disent ce qu'il aurait fallu** — c'est la §4 « Écartées » de `06` appliquée.

| # | méthode | verdict | ce que la mesure a dit |
|---|---|---|---|
| 1 | comptage par rayon, déficit = fusion | ❌ | **475 sites**, presque tous au centre : une carte du détecteur |
| 2 | suivi des spires, mort de piste = fusion | ❌ | **12 249 « fusions »** pour 158 feuilles |
| 3 | chaînage des écarts doublés | ❌ | persistance 200 contre groupes plafonnés à **164** |
| 4 | **densité de doublement par cellule** | ✅ | 4 candidats stables |

### Ce que le suivi a coûté, et rapporté

Trois hypothèses posées sur la fragmentation du tracker, **trois réfutées** :

| hypothèse | verdict |
|---|---|
| le glouton fragmente → affectation globale (Hongrois) | ❌ **pire** : 17 pistes longues contre 69 |
| les pistes en sursis volent des murs | ❌ plus de sursis **améliore** |
| le détecteur perd les murs | ❌ **92 %** retrouvés à moins de 2 voxels |

⚠ Le Hongrois est pire pour une **raison de fond** : il minimise le coût *total*, donc
il sacrifie un appariement quasi certain pour améliorer la somme ailleurs. En suivi,
un coût nul ne doit jamais s'échanger. *L'optimalité globale n'est pas le bon objectif
ici* — l'inverse de ce que la littérature suggère pour un champ dense.

**La vraie cause, mesurée** : 125 murs sur 126 sont appariés à chaque colonne, pour
186 pistes vivantes. La couverture est quasi parfaite ; c'est l'**identité** qui
churne, parce qu'une piste qui perd son mur extrapole et ne le retrouve jamais.

⚠⚠ **Donc les 12 249 « fusions » étaient des changements d'étiquette, pas des
soudures.** Le chiffre ne mesurait rien de physique.

## 6. La méthode qui tient : le doublement d'écart

Une soudure ne fait pas disparaître un mur dans le bruit du comptage : elle **double
l'écart local** entre deux murs voisins. C'est local, mesuré dans une colonne unique,
et **sans aucun appariement entre colonnes** — donc immunisé aux trois hypothèses
ci-dessus.

⚠ Normalisé par l'espacement **local**, jamais par un seuil en micromètres :
l'espacement varie d'un facteur trois selon le rayon.

**Contrôle** (`fusions.py ecarts-controle`) : lignes fabriquées intactes → **0 site**,
avec une soudure → exactement **1**.

### ⚠⚠ Le cœur est dégénéré par construction, pas bruité

Au rayon *r*, deux colonnes voisines de l'image dépliée échantillonnent des points
distants de `2πr/18850` voxels : à *r* = 100, c'est **0,03 voxel**, donc une trentaine
de colonnes lisent **le même pixel**. Sans exclusion, la mesure redécouvrait
exactement le mode d'échec nº 1 (rayon médian 0,5 mm).

**La coupe est validée par mesure**, pas choisie :

| coupe | cellules | rayon du site le plus interne |
|---:|---:|---:|
| 1,6 mm | 11 | 1,4 mm |
| 2,4 mm | 8 | 2,4 mm |
| 3,6 mm | 5 | 3,3 mm |
| **4,7 mm** | **4** | **17,1 mm** |
| **6,3 mm** | **4** | **17,1 mm** |

Le site le plus interne **suit la coupe** — ce sont des artefacts de bord. Au-delà de
4,7 mm ils disparaissent et il reste **4 cellules que déplacer encore la coupe ne bouge
plus**.

## 7. 🎯 Le résultat : quatre candidats, groupés dans le tiers externe

**4 cellules anormales sur 1392** (0,29 %), taux de fond 6,6 % :

| rayon | colonne | taux de doublement | écarts |
|---:|---:|---:|---:|
| 18,0 mm | ~14 000 | **20,3 %** | 1389 |
| 17,1 mm | ~16 500 | 19,3 % | 1350 |
| 17,6 mm | ~15 500 | 18,8 % | 1437 |
| 17,1 mm | ~16 000 | 17,1 % | 1439 |

Elles sont **groupées** : rayons 17,1 à 18,0 mm, colonnes 14 000 à 16 500 sur 18 850,
soit un secteur angulaire d'environ **50°**. Ce n'est pas une dispersion de bruit,
c'est **une région** — et elle est à 17 mm sur un rayon extérieur de 22,7 mm, donc dans
le **tiers externe**, cohérent avec la théorie de l'auteur sur les couches externes les
plus abîmées.

⚠ **Ce qui n'est PAS établi** : que ce soient des soudures. Ce sont des endroits où
l'écart double trois fois plus souvent qu'ailleurs — compatible avec une soudure, une
déchirure ou un vide. Mais c'est désormais **quatre endroits précis** au lieu d'un
rouleau entier, ce qui est exactement ce que la piste « revoir les sites suspects à
2,4 µm (ESRF) » attendait.

## 8. 🔄 En cours : tiennent-ils le long de z ?

Groupées dans **une** coupe, quatre cellules sur 1392 peuvent encore tomber côte à côte
par hasard. La troisième dimension tranche : **un dégât physique occupe une hauteur ;
du bruit de détection, non.**

`fusion_scan.py` répète la mesure sur cinq coupes et compare le regroupement
**inter-coupes** à une hypothèse nulle **calculée** — mêmes nombres de cellules, mêmes
étendues, positions tirées au hasard. Sans elle, « elles sont proches » est une
impression et non une mesure.

⚠ Les paires ne sont comptées qu'entre coupes **différentes** : deux cellules voisines
dans la même coupe sont déjà ce que la §7 montre, et les compter ferait passer ce
résultat pour sa propre confirmation.

### ⚠⚠ Premier essai : verdict « bruit de coupe », et le verdict était FAUX

Cinq coupes réparties sur toute la hauteur, 0 coïncidence sur 21 paires contre 2,1 %
au hasard → *indistinguable du hasard*.

**Le test ne pouvait rien détecter.** Ces cinq coupes sont espacées de **22,3 mm** :
pour apparaître dans deux d'entre elles, une soudure devrait faire plus de 22 mm de
**haut**. J'avais échantillonné à l'échelle de l'objet et non à celle de la structure
cherchée.

Et la même mesure dit l'inverse de son propre verdict :

| grandeur | valeur |
|---|---|
| taux de fond, sur les 5 coupes | **6,4 · 6,5 · 6,6 · 6,9 · 7,0 %** |
| bruit d'échantillonnage sur 1400 écarts | 0,66 % |
| une cellule à 20 % est donc à | **~20 écarts-types du fond** |

Le fond est remarquablement stable sur toute la hauteur du rouleau, donc **les
anomalies sont réelles** et non du bruit d'échantillonnage. C'est leur *persistance*
qui restait à tester — et le test n'en était pas un.

**Relancé** avec des coupes espacées de **0,8 mm** autour de z = 6967.

---

## Reproduire

```bash
cd experiments

# l'axe, DERIVE d'une trace et verifiable (monotonie de la spirale)
uv run python src/excision/radial.py centre PHerc0172 \
    ../repos/windcheck/data/scroll5_tifxyz/20251115002741-*/mesh

# l'onde radiale : feuilles, espacement, longueur
uv run python src/excision/radial.py compter PHerc0172 "$VOL"

# le profil le long de z : 20 tranches uniformes + 6 de raffinement
uv run python src/excision/radial.py profil PHerc0172 "$VOL" ../docs/profil_z_0172.json \
    --slices 20 --refine 6

# le depliage polaire
uv run python src/excision/radial.py deplier PHerc0172 "$VOL" \
    ../data/out/polaire_0172.npy --reach 3000 --png ../data/out/polaire.png

# les candidats -- ⚠ lancer le temoin AVANT la mesure
uv run python src/excision/fusions.py ecarts-controle
uv run python src/excision/fusions.py densite ../data/out/polaire_0172.npy --min-radius 600

# tiennent-ils en z ?
uv run python src/excision/fusion_scan.py PHerc0172 "$VOL" ../docs/fusions_z_0172.json
```

avec `VOL=s3://vesuvius-challenge-open-data/PHerc0172/volumes/20241024131839-7.910um-53keV-masked.zarr`.
