# 128 — Une faille d'une feuille n'existe pas dans la matière

> ⭐⭐⭐⭐ **`127` LAISSE `R4-P25` SUR UN LIEN QUI DEVRAIT SAVOIR QUAND SE RELÂCHER. CE DOCUMENT VA
> CHERCHER LA GÂCHETTE, ET TROUVE QU'ELLE N'EXISTE PAS POUR LA FAILLE QUI COMPTE.** Le saut d'un
> empilement est une **phase**, donc il est périodique : décaler les feuilles d'exactement un pas
> rend un volume dont l'écart maximal à l'original vaut **0,000000** sur 2000 points de part et
> d'autre du plan. Il n'y a rien à lire parce qu'il n'y a rien.
>
> ⭐⭐⭐⭐ **ET CE N'EST PAS UNE PANNE DU LECTEUR, PARCE QU'UNE FAILLE FRACTIONNAIRE, ELLE, SE DIT
> ET SE DIT FORT** : à une demi-feuille, le pire désaccord des moitiés passe de **8,49° à 88,52°**
> pour une barre de **10,06°**, avec p **0,0005** sur douze graines. Le lecteur voit très bien une
> rupture — celle d'une feuille entière n'en est pas une.
>
> ⭐⭐⭐ **LA PORTÉE EST EXACTEMENT LE CUBE DE LECTURE** : le signal est entier jusqu'à **20
> voxels** du plan (le demi-côté du cube), vaut encore **48,52°** à 25, et à 30 la pile rompue rend
> **8,64°** contre **8,61°** pour l'intacte. Au-delà du cube, la faille n'existe pas non plus.
>
> ⚠⚠⚠ **ET LA MARCHE PREND LA FAILLE POUR UNE FEUILLE.** Au pas de la rencontre elle avance
> **perpendiculairement au plan de faille** — part **1,0000** contre **0,0147** sur pile intacte,
> alors que la normale de l'empilement n'a aucune composante sur cet axe — de **216,2 µm**. Douze
> marches sur douze quittent le cube **dès ce pas**, et s'éloignent de **105,21 voxels** contre
> **15,32** intactes. La garde refuse le pas ; le pas est pris quand même.
>
> ⚠⚠ **ET MA PREMIÈRE LECTURE AVAIT RATÉ TOUT ÇA**, en résumant chaque marche par la **médiane**
> de ses pas : la faille n'en touche qu'un, donc une médiane sur vingt-quatre le noie. Le péché
> capital du dépôt — moyenner sur l'axe où vit la différence — commis sur mon propre instrument.
>
> ⭐ **Zéro lecture distante.**

## 1. Pourquoi ce fichier

`127` mesure qu'un lien latéral supprime la déchirure de bruit **en cassant le décrochement réel**,
et que ce qui manque est un lien qui sait **quand se relâcher**. Se relâcher demande un signal
disponible **au pas** : après coup, les dégâts sont faits. Ce fichier va chercher ce signal là où
il devrait être, dans ce que la marche lit **déjà**.

⚠ Aucun instrument neuf n'est introduit. Un signal qui exigerait une seconde lecture ne serait pas
disponible au moment où il faut, et serait un second lecteur libre de ne pas s'accorder avec le
premier.

## 2. ⭐⭐⭐⭐ Le témoin de `127` ne pouvait pas poser la question

Il décalait les **départs** des marches. La matière, elle, restait continue : une pile continue n'a
aucune faille à annoncer, donc l'absence de signal n'y aurait rien prouvé. Le fichier a donc besoin
d'une pile dont l'empilement **lui-même** est rompu, et `VolumeFabriqueAvecFaille` l'est.

Trois choix la définissent :

- ⚠⚠ **Le plan de faille est perpendiculaire à z.** En (z, y, x), c'est l'axe selon lequel les
  marches voisines d'une nappe sont écartées **et** celui selon lequel `accord_des_moities` coupe
  son cube. Une faille portée par un autre axe ne séparerait aucune marche de sa voisine et
  tomberait entièrement dans une seule moitié : elle ne mesurerait ni la déchirure ni la garde.
- ⚠ **Les deux côtés gardent la même normale et le même pas** : ce qui change est **où** tombent
  les feuilles, pas comment elles sont posées. Incliner un côté mélangerait une rupture et une
  déformation, et on ne saurait plus laquelle la lecture a vue.
- ⚠ La sous-classe ne redéfinit que la **géométrie** (`_projection_um`), donc le bruit, le
  contraste et les bornes du volume lui arrivent de la classe de base et ne peuvent pas en
  diverger. C'est la leçon de `126` appliquée avant d'en avoir besoin.

## 3. ⭐⭐⭐⭐ Une faille d'une feuille n'existe pas

2000 points tirés **de part et d'autre** du plan, comparés un à un entre la pile rompue et la pile
intacte.

| saut injecté | écart maximal de lecture | la matière change |
|---:|---:|:---:|
| 0,25 feuille | 56,568536 | oui |
| 0,50 feuille | **79,999989** | oui |
| 0,75 feuille | 56,568540 | oui |
| **1,00 feuille** | **0,000000** | **non** |

⭐ **79,999989 est le contraste entier de la pile** (amplitude 40, donc 80 de creux à crête) : une
demi-feuille de décalage met un côté exactement en opposition de phase avec l'autre. Et une feuille
entière ne met rien du tout.

⚠ Le plancher de comparaison est celui du **flottant**, pas un seuil réglé : le résidu d'un saut
d'une feuille vaut ~2·10⁻¹², trois décades sous le plancher retenu et treize sous le signal d'une
demi-feuille. Aucun choix raisonnable dans cet intervalle ne change la réponse.

⭐⭐⭐ **Et ce n'est pas une affaire de pas constant**, ce qui élargit le fait au-delà de la
fixture : ce qui cause l'invisibilité est que la pile soit une fonction de la **phase seule**,
périodique de période 1. La pile à **pas variable** de `122` le vérifie — deux points distants
d'exactement une feuille en phase y lisent la même chose, alors qu'une demi-feuille plus loin la
lecture a changé de tout le contraste. Donc un rouleau dont l'espacement varie d'un facteur cinq
(`118`) ne porte pas davantage l'identité d'une feuille.

## 4. ⭐⭐⭐⭐ Une faille fractionnaire se dit, et fort

Douze graines, marches de 24 pas, obliquité 35°, bruit 8, cube de ±20 voxels, barre du nul
**10,06°**. Le tableau donne le **pire** désaccord de chaque marche, apparié graine par graine à la
même marche sur la pile intacte. Saut de 0,5 feuille :

| distance au plan (vx) | intacte | rompue | écart | p |
|---:|---:|---:|---:|---:|
| 0 | 9,14 | **87,00** | +78,4250 | 0,0005 |
| 5 | 8,90 | **89,31** | +79,5800 | 0,0005 |
| 10 | 8,49 | **88,52** | +80,4150 | 0,0005 |
| 15 | 9,58 | **87,92** | +79,0800 | 0,0005 |
| 20 | 8,37 | **88,00** | +78,7300 | 0,0005 |
| 25 | 8,49 | 48,52 | +39,4550 | 0,0269 |
| 30 | 8,61 | 8,64 | −0,1950 | 0,7910 |
| 45 | 8,21 | 8,15 | −0,4900 | 0,2334 |

⭐ **Un désaccord de 88° est un angle droit** : les deux moitiés du cube ne pointent pas seulement
ailleurs, elles pointent perpendiculairement l'une à l'autre. Sur une pile intacte le pire pas
d'une marche entière reste **sous la barre**.

⭐⭐⭐ **La portée est le cube, et elle a été pincée plutôt que supposée** : 20 et 25 encadrent la
prédiction géométrique — le cube va de `centre − demi` à `centre + demi` **inclus**, donc un plan à
exactement 20 est sa face et se lit encore. À 30 la pile rompue et la pile intacte rendent le même
nombre à trois centièmes près.

⚠ La taille de la faille ne change presque rien (+72 à +80 selon qu'elle vaut 0,25, 0,50 ou 0,75) :
ce que le tenseur voit n'est pas l'amplitude du décalage, c'est **l'existence d'un plan de rupture**.

## 5. ⚠⚠ Et la marche prend la faille pour une feuille

Au pas de la rencontre, douze marches sur douze, à 10 voxels du plan :

| | rompue | intacte |
|---|---:|---:|
| désaccord des moitiés | **88,52°** | 4,92° |
| avance | **216,2 µm** | 190,3 µm |
| part de l'avance perpendiculaire au plan de faille | **1,0000** | 0,0147 |
| excursion latérale sur la marche entière | **105,21 vx** | 15,32 vx (max 26,67) |

⚠⚠⚠ **Une part de 1,0000 veut dire que la marche part exactement en travers du plan de faille**,
alors que la normale de l'empilement n'a **aucune** composante sur cet axe. Elle a lu le plan de
rupture comme si c'était une feuille, et elle l'a traversé comme on traverse une feuille. Elle
parcourt ainsi 216,2 µm dans une direction à 90° de l'empilement réel, et **12 marches sur 12**
quittent le demi-cube **dès ce pas** — rang médian de sortie **0,0**.

⚠ Le témoin est ce qui rend cette ligne lisible : une marche sur pile intacte s'éloigne de **15,32
voxels** en médiane sur les mêmes 24 pas, sous le demi-cube. Sans lui, « la marche s'éloigne de 105
voxels » ne distinguerait pas une éjection d'un vagabondage ordinaire, et les deux lectures mènent à
des conclusions opposées.

⭐⭐ **La garde refuse ce pas — et le pas est pris quand même.** `oriente` vaut faux, il est
enregistré, et la boucle avance dans cette direction. Sur les douze marches, 16 pas sont refusés et
**12 le sont au premier rang** : c'est le pas de la rencontre, et les quatre autres (rangs 12, 18,
18, 21) tombent après que la marche a déjà été chassée ailleurs.

## 6. ⚠⚠ Ce que ma première lecture avait raté

La première version résumait chaque marche par la **médiane** de ses pas. Une faille ne touche
qu'un pas — celui de la rencontre — donc une médiane sur vingt-quatre le noie : le tableau rendait
des écarts de −0,42 à +0,07 degré, avec des p entre 0,11 et 0,94, et j'allais écrire que la faille
ne se dit pas. Le pas fautif en portait **86**.

C'est le péché capital du dépôt — **moyenner sur l'axe où vit la différence** — commis sur mon
propre instrument, et il est arrivé pour la raison habituelle : la médiane par marche avait été
choisie pour une bonne raison (la réserve de grappe, les pas d'une marche ne sont pas indépendants)
et appliquée à une question pour laquelle elle est fausse. Les deux résumés sont désormais publiés
côte à côte : la médiane dit ce que la marche lit d'ordinaire, le pire dit si elle a **vu**
quelque chose.

⚠ Et le pire n'est pas pris dans le même sens pour tout : la planarité est un **contraste**, donc
son cas grave est le bas. Prendre le maximum partout aurait rendu le pire d'un signal et le
meilleur de l'autre sous un seul nom.

## 7. Ce que ça change pour le graal

- ⭐⭐⭐⭐ **La gâchette que `127` demande n'existe pas pour la faille qui compte.** `124` mesure
  des déchirures d'une feuille, `91` mesure que la vérité de terrain humaine devient discontinue au
  bord du rouleau d'à peu près autant — et une faille d'une feuille ne laisse **aucune trace** dans
  ce que la marche lit. Ce n'est pas une limite du lecteur, c'est une propriété de l'objet.
- ⭐⭐⭐ **Donc l'identité d'une feuille n'est pas portée par la matière, elle est portée par le
  COMPTE.** Une pile périodique dit où l'on est *dans* une feuille, jamais *laquelle*. Un compte ne
  se vérifie que contre un autre compte, jamais contre la matière — et c'est pourquoi `R4-F53`, la
  déchirure qui ne s'annonce pas, n'est pas un manque de mesure mais une conséquence.
- ⚠⚠ **Ce qui laisse une porte, et c'est la bonne**, parce que le rouleau n'est **pas** une pile
  périodique : ses feuilles sont des objets distincts, avec leur épaisseur, leur contraste, leur
  encre et leurs dégâts propres. Si quelque chose de local distingue la feuille *n* de la feuille
  *n+1* dans le vrai volume, la gâchette existe ; sinon aucun lien local ne pourra jamais savoir
  quand se relâcher. C'est `R4-P26`, et elle est mesurable.
- ⭐⭐ **Et il reste une prise immédiate** : la garde voit très bien une rupture **fractionnaire**,
  à 88° contre une barre de 10,06°, et elle refuse le pas. Ce qu'elle ne fait pas, c'est
  l'empêcher. Un marcheur qui **ne prend pas** le pas que sa propre garde refuse n'irait pas se
  faire chasser de 216 µm en travers de l'empilement.
- ⚠ **Analytique, et ça borne ce que ça dit.** La pile fabriquée est périodique par construction ;
  tout ce qui est établi ici l'est de cette pile et de la classe des piles qui sont fonction de la
  phase seule. Que le rouleau en soit une est précisément ce que `R4-P26` demande de mesurer.

## 8. Les registres

Faits `R4-F56` (une faille d'une feuille n'existe pas dans une pile fonction de la phase seule) et
`R4-F57` (une faille fractionnaire se dit à 88° pour une barre de 10,06°, sa portée est le cube, et
la marche la prend pour une feuille). Porte nouvelle `R4-P26` : la matière porte-t-elle l'identité
d'une feuille ? `R4-P25` reste ouverte et gagne la raison pour laquelle elle se refermait sur
elle-même.

## Reproduire

```bash
uv run python src/nappe/la_faille_se_dit_elle_dans_la_lecture.py --verifier   # 31 contrôles
uv run python src/nappe/la_faille_se_dit_elle_dans_la_lecture.py \
    --json docs/mesures/la_faille_se_dit_elle_dans_la_lecture.json            # ~5 min
uv run python src/nappe/combien_de_pas_la_matiere_porte.py --verifier         # 69 contrôles
```

⚠ **Tout est analytique.** La pile rompue vit dans `combien_de_pas_la_matiere_porte.py`, à côté des
deux autres fixtures : une seconde matière serait deux piles libres de ne pas s'accorder. Le
marcheur est importé, et le seam `_projection_um` n'a déplacé aucune valeur — les 69 contrôles de
son module le disent.
