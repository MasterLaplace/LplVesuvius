# 100 — La normale de la nappe n'est pas le rayon, et l'obliquité n'explique pas l'écart de pas

> ⛔⛔⛔ **L'hypothèse qui expliquait le trou de `99` est RÉFUTÉE par la mesure.** Le long de la
> **normale**, le pas est le **même** que radialement : rapport médian **1,018** (de 0,84 à 1,33)
> là où l'obliquité en prédirait **1,184**. L'accord **1,212 contre 1,213** entre `1/cos` et le
> rapport 198,9/164,0 était une **coïncidence**.
>
> ⭐⭐⭐ **Mais le test laisse un fait plus lourd que ce qu'il réfute** : la normale du maillage
> est à **34,1°** du rayon là où une spirale de ce pas en prédit **0,09°** — **378 fois** moins.
> La surface que les humains ont tracée n'est pas une spirale vue de face.

![la normale n'est pas le rayon](images/100_la_normale_nest_pas_le_rayon.png)

## 1. Pourquoi ce fichier, et c'est l'item A bis du bloc de reprise

`99` a mesuré que la matière montre un pas de **198,9 µm** au cœur là où `91` publie **164 µm** sur
les transferts humains, et l'a écrit franchement : *« son ampleur n'est pas expliquée ici »*.

Une explication évidente se présentait. Si la direction radiale n'est pas perpendiculaire à
l'empilement, la distance radiale entre deux feuilles vaut

$$d_{\text{radial}} = \frac{p}{\cos\theta}$$

donc un pas apparent **plus grand** que le vrai. Et l'accord numérique était stupéfiant : la
médiane de `1/cos` mesurée sur le maillage vaut **1,212**, contre un rapport observé
198,9 / 164,0 = **1,213**. Un accord à un millième.

> ⚠⚠⚠ **C'est exactement la forme du piège que `94` a enregistré avec la sagitta** : une
> coïncidence numérique qui ressemble à un mécanisme. Le dépôt en a la règle — *une corrélation
> prise pour un mécanisme* — donc rien n'a été publié avant d'avoir lancé le test qui tranche.

## 2. ⭐⭐⭐ Le fait, et il est plus lourd que l'hypothèse qu'il devait servir

Sur une spirale d'Archimède, la feuille gagne un pas de rayon par tour, donc son inclinaison sur
le rayon local vaut

$$\theta_{\text{spirale}} = \arctan\!\left(\frac{p}{2\pi r}\right)$$

soit **0,15°** à 10 mm de rayon pour un pas de 164 µm, et **0,07 à 0,39°** sur toute l'étendue de
ce fragment. Une quantité qu'on confondrait avec zéro.

| | mesuré |
|---|---|
| angle de la normale de la **grille** au rayon | **34,1°** (médiane sur 28 bandes) |
| angle de la normale par **ACP** au rayon | **33,6°** |
| écart entre les deux estimateurs | **1,59°** |
| ce qu'une spirale de ce pas prédit | **0,09°** |
| **combien de fois la prédiction** | **378** |

## 3. ⭐⭐ Et ce n'est pas l'estimateur

La normale de la grille hérite de l'anisotropie du maillage — `97` a mesuré que les rangs de cette
révision sont espacés de ~800 µm quand ses colonnes sont à ~100. Un angle qui viendrait de là
mesurerait la **grille**, pas la surface.

Le contrôle est un second estimateur qui ne partage **aucune** hypothèse avec le premier : le plus
petit vecteur propre de la covariance des trente plus proches voisins. Il ne connaît ni les lignes
ni les colonnes, seulement des points dans l'espace.

> ⭐ Les deux s'accordent à **1,59°**. L'obliquité est donc dans la **matière tracée**, pas dans la
> façon de la lire.

⚠ La propriété est aussi vérifiée sur fixture : sur un plan échantillonné **huit fois** plus
serré dans un axe que dans l'autre, l'ACP rend la normale du plan à **0,0000°**.

## 4. ⚠⚠ Bruit ou structure ? Le contrôle de `96`, appliqué à une direction

Une normale locale est sensible à la rugosité de surface. Le contrôle qui sépare les deux est
celui que `96` a établi : la quantité survit-elle à un voisinage plus large ?

| voisins de l'ACP | 10 | 30 | 100 | 300 | 1000 |
|---|---|---|---|---|---|
| angle médian | **35,78°** | 33,59° | 30,14° | 26,62° | **21,22°** |

⭐ **Les deux moitiés comptent, et elles sont publiées ensemble.** L'angle **décroît**, donc une
part est bien de la rugosité locale. Mais il **ne converge pas vers zéro** : à mille voisins il
reste **21,22°**, soit **236 fois** la prédiction de la spirale.

## 5. ⚠ Décomposée, l'obliquité est les deux à la fois

Une composante hors du plan de la section et une composante dans ce plan n'ont pas la même
conséquence, et elles ne se corrigent pas de la même façon — un angle total seul ne dirait pas
laquelle on regarde.

| | médiane |
|---|---|
| part hors du plan (les feuilles seraient **coniques**) | **14,62°** |
| part dans le plan (la section n'est pas un **cercle**) | **24,04°** |

⚠ La seconde n'est pas une surprise : `91` signalait déjà que la section n'est pas circulaire. La
première l'est davantage — elle dit que les feuilles s'évasent le long du rouleau.

⚠ Et l'angle **décroît vers le bord** (corrélation **−0,549** avec le rayon) : 34,5° à 4 mm,
25,7° à 23,9 mm.

## 6. ⛔⛔⛔ Le test décisif, et l'hypothèse tombe

Le même instrument que `99` — même fenêtre, même nul par candidat, même barre — est lancé **deux
fois par bande** : une fois le long du rayon, une fois le long de la **normale**. Seule la
direction du segment change entre les deux colonnes.

| | mesuré |
|---|---|
| rapport pas radial / pas normal, médiane | **1,018** |
| son étendue | **0,84 à 1,333** |
| ce que l'obliquité prédirait (`1/cos`, médiane) | **1,184** |
| écart du rapport à **1** | **0,083** |
| écart du rapport à **1/cos** | **0,16** |

> ⛔ **Le rapport est deux fois plus proche de 1 que de 1/cos.** Le pas ne dépend pas de la
> direction, donc l'obliquité n'explique **pas** l'écart de `99`.

⭐⭐⭐ **Et un second verdict, indépendant du premier.** Comparer deux **médianes** peut rater un
effet réel noyé dans la dispersion. Si l'obliquité jouait, le rapport **suivrait** `1/cos` d'une
bande à l'autre, quelle que soit sa valeur moyenne. Corrélation mesurée : **+0,153**. Cette
dépendance-là est testée directement, et elle n'y est pas — c'est ce que le panneau C montre :
le nuage est sur l'**horizontale** verte, pas sur la **diagonale** rouge.

## 7. ⭐⭐⭐ Le contrôle qui rend ce résultat négatif lisible

> **Un test qui ne voit rien est indiscernable d'un test aveugle.**

C'est la pièce qui a manqué à plusieurs vérifications de ce dépôt avant qu'on ne s'en aperçoive, et
elle est ici centrale parce que le résultat **est** négatif. `empilement_oblique` fabrique une pile
de feuilles planes dont la normale fait un angle **connu** avec le rayon et dont l'espacement vrai
est connu :

| empilement fabriqué | angle mesuré | pas normal lu | rapport lu | `1/cos` attendu |
|---|---|---|---|---|
| θ = 0° | **0,00°** | 181,7 µm | **1,000** | 1,000 |
| θ = 35° | **35,00°** | 181,7 µm | **1,238** | **1,221** |

⭐ L'instrument **voit** l'obliquité quand elle existe, au cran de balayage près (8,65 µm). Il ne
la voit pas sur le vrai volume.

⚠⚠ Et la fixture a d'abord **échoué**, pour une raison qui valait d'être écrite : avec un rayon de
départ rond (10 mm) et un pas de 173 µm, la cellule tombe à la **phase 0,80** d'une période — ni
sur une feuille, ni dans un interstice — donc **aucune** des deux polarités du gabarit ne peut
correspondre, et la recherche rend une période fausse (242 µm pour 173 injectés). *Un contrôle doit
poser sa cellule là où la matière la poserait.*

## 8. ⚠⚠⚠ Ce que cela corrige dans `98`

La docstring de `combien_dinterstices_traverses.segments` affirmait :

> *« LE SEGMENT EST RADIAL ET A z CONSTANT, donc il traverse l'empilement perpendiculairement. »*

La seconde moitié est **mesurée fausse** : le segment radial coupe l'empilement de biais, de 34°.

⭐⭐⭐ **Et ce qui sauve la mesure de `98` n'est pas ce qui était écrit, c'est l'autre résultat de
ce fichier** : le pas ne dépend pas de la direction, donc le segment radial mesure bien la même
chose qu'un segment normal — pour une raison qui **n'est pas** celle que la docstring donnait, et
qui reste inexpliquée. La correction est faite sur place, avec sa mesure.

## 9. ⚠⚠ Ce que ce document ne dit pas

- **L'écart de `99` reste inexpliqué.** Un candidat est éliminé, pas remplacé. L'item **A bis** du
  bloc de reprise reste ouvert, avec une piste de moins.
- **Pourquoi la surface est oblique n'est pas expliqué non plus.** Le fait est mesuré et
  confirmé par deux estimateurs ; sa cause — écrasement, cône réel, ou une propriété du traçage
  humain — n'est pas tranchée ici.
- ⚠ La part de rugosité et la part de structure sont **séparées mais pas expliquées** : le
  plateau à 21,22° est une borne inférieure sur ce qui est réel, pas une mesure de la seule
  structure.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/la_normale_nest_pas_le_rayon.py --verifier
uv run python src/nappe/la_normale_nest_pas_le_rayon.py \
    --json docs/mesures/la_normale_nest_pas_le_rayon.json
uv run python src/nappe/la_normale_nest_pas_le_rayon.py --reagreger \
    --json docs/mesures/la_normale_nest_pas_le_rayon.json   # rederive les verdicts, sans reseau
uv run python src/figures/figure_la_normale_nest_pas_le_rayon.py --verifier
```
