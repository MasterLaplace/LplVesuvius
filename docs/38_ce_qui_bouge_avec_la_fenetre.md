# Ce qui bouge avec la fenêtre — un test de trace sans seuil ni vérité terrain

2026-08-20, fin d'après-midi. **Ce document est né de trois hypothèses réfutées le même
jour**, et c'est la forme de leur échec qui a produit l'instrument.

---

## 0. La forme, d'un coup d'œil

![deux surfaces, la meme mesure, des fenetres de plus en plus larges](images/38_convergence.png)

> **Une surface qui suit sa feuille garde sa distance quand on élargit la fenêtre. Une
> surface posée en travers de l'empilement voit son « pic » s'éloigner avec elle.**
> α = **+0,00** contre **+1,01**.

Figure : `src/figures/figure_convergence.py`, depuis `docs/convergence.json`.

## 1. Les trois hypothèses, et pourquoi elles sont tombées

| hypothèse | ce qui l'a tuée |
|---|---|
| **la trace est à UNE spire de sa feuille** — 0,65 à 1,25 spire sur seize mesures | toutes censurées ou mesurées dans une fenêtre plus étroite que 1,4 spire. Pour `PHerc1447`, le plafond vaut **exactement** l'écart inter-spires (172,8 µm) : « 1,00 spire » y était indistinguable d'une troncature |
| **alors DEUX spires** — 1,80 / 1,80 / 2,08, serré | ces valeurs valent **90 à 94 %** de leur propre plafond, et le même tirage lisait 159,8 µm à 41 couches contre 311,0 à 81 |
| **alors ce n'est pas une distance mais une FORME** — 0 % de fenêtres plates côté officiel contre 14–55 % côté nous | `part_plates` baisse aussi avec la fenêtre : 0,896 → 0,740 → 0,552 quand elle triple. Et l'officiel avait été rendu sur 31 couches contre 21/41/81 pour les nôtres |

⭐⭐ **Le motif commun est le résultat.** Trois fois, la mesure suivait le **réglage** au lieu
de suivre le papyrus. Une quatrième tentative de trouver « la bonne statistique » aurait été
une quatrième occasion de se tromper — alors que la dépendance elle-même distingue les deux
surfaces mieux que n'importe quelle valeur.

## 2. ⭐⭐⭐ Le test

Rendre la **même** surface dans des fenêtres de plus en plus profondes, et regarder si la
distance mesurée bouge.

| fenêtre rendue | segment officiel `20250702235910` | notre tirage `PHerc1447 r2` |
|---:|---:|---:|
| 21 couches | — | 86,4 µm |
| 31 | **17,3 µm** | — |
| 41 | — | 159,8 µm |
| 81 | **17,3 µm** | 311,0 µm |
| 161 | — | **682,6 µm** |

> ✅ **L'officiel : ×1,00 pour ×2,6 de fenêtre, α = +0,00.** La matière est là, tout près ;
> la mesure ne dépend pas du réglage, donc c'est une **distance**.
>
> ⚠⚠ **Réserve ajoutée le 2026-08-22, voir [`49`](49_alpha_ne_separe_pas_deux_pannes.md).**
> α ≈ 1 a **deux** causes : un pic qui recule, et **aucun pic du tout**. Un profil plat
> rapporte le bord de la fenêtre par défaut, et le rapport de deux bords vaut celui des
> fenêtres — donc α = 1 par identité. Le seul profil de cette trace encore sur disque (41
> couches) a une amplitude de **0,0194** pour un seuil de détection de 0,02, et un écart de
> **172,80 µm** qui est exactement la demi-fenêtre à 8,64 µm. Les trois autres fenêtres de
> la série ne sont pas dans l'arbre.
>
> ⭐ Ce que ça change : le verdict *pratique* tient — « aucune feuille dans la fenêtre » est
> vrai sous les deux lectures — mais l'affirmation que la surface **coupe** l'empilement
> repose sur la géométrie du rendu, pas sur ce profil. Et **aucun verdict de convergence
> n'est touché** : l'α de plafond vaut ~1, donc une trace qui converge en est loin par
> construction (mesuré : 0 série convergente sur 107).

> ⚠⚠ **Le nôtre : ×7,90 pour ×7,7 de fenêtre, α = +1,01.** Le « pic » n'est pas une feuille,
> c'est **le plus fort de ce que la fenêtre contenait** — et il s'éloigne avec elle. À
> 691 µm de portée, soit **quatre spires**, il n'a toujours rien trouvé.

**Ce n'est donc pas « notre trace est à 311 µm de sa feuille ».** C'est : **il n'y a aucune
feuille à portée.** La surface est posée *en travers* de l'empilement — exactement ce que
montrait déjà l'image de [`24`](24_premiere_trace_rouleau_du_prix.md), des lamelles
concentriques, le rouleau vu par la tranche. Ce document met un nombre dessus.

## 2 bis. ⭐⭐ Et l'œil est d'accord avec le test

Un verdict qu'on peut vérifier en regardant vaut mieux qu'un verdict qu'il faut croire. Les
deux surfaces, rendues par la même chaîne sur le même rouleau :

| une feuille — α = +0,00 | des tranches — α = +1,01 |
|---|---|
| ![face d une feuille](images/36_papyrus_PHerc1447.png) | ![tranches d un empilement](images/38_en_travers.png) |
| segment officiel, 25 × 27 mm | notre trace depuis **leur** graine, 49 × 49 mm |
| **treillis de fibres croisées**, trous, bords déchirés — la *face* d'une feuille | **longues striations parallèles** — les *bords* de dizaines de feuilles empilées |

> ⚠ **Et la seconde est SIX FOIS plus grande.** Une surface plus étendue n'est pas une
> meilleure surface : c'est plus de rouleau vu par la tranche. L'aire mesure jusqu'où le
> traceur est allé, jamais s'il est allé au bon endroit — `25` le disait déjà, cette image
> le montre.

⭐ C'est la validation visuelle du test : là où il dit « converge », l'œil voit une feuille ;
là où il dit « suit la fenêtre », l'œil voit une coupe. Aucun seuil n'a été réglé pour
obtenir cet accord.

## 3. Pourquoi ce test vaut mieux que ce qu'il remplace

| propriété | les instruments précédents | celui-ci |
|---|---|---|
| **seuil** | `12` : « écart > ~50 µm ⇒ illisible » ; `25` : « pic dans le tiers central » | **aucun** — on compare une mesure à elle-même |
| **vérité terrain** | il faut un segment de référence, et [`36`](36_lorigine_de_la_pile.md) montre qu'un segment officiel n'en est pas une | **aucune** |
| **échelle** | dépend de la taille de voxel et du rouleau | **sans dimension** — un rapport traverse les résolutions |
| **fenêtre de rendu** | ⚠⚠ toutes les valeurs en dépendent, mesuré | c'est **le sujet** de la mesure |

⚠ **Ce qu'il ne dit pas : de combien corriger.** Une trace qui ne converge pas n'a pas de
distance à sa feuille, puisqu'il n'y a pas de feuille à portée. Le test sépare *posée à côté*
de *posée en travers*, et rien d'autre — ce qui est déjà ce que rien ne faisait.

⚠ **Il faut au moins deux fenêtres dans un rapport d'au moins deux.** Deux mesures trop
proches rendraient un rapport proche de 1 quelle que soit la surface, c'est-à-dire un test
incapable d'échouer. `src/commun/test_convergence.py` **refuse** de rendre un verdict dans
ce cas, et son témoin le sonde.

## 4. Ce que ça change

- ⚠⚠ **Toutes les distances publiées par ce dépôt sont sans objet pour nos traces** — les
  94 µm de `24`, les 146–187 µm de `37`, les 311 µm de ce matin. Ce ne sont pas des
  sous-estimations : ce sont des mesures d'une grandeur qui n'existe pas ici. Elles restent
  valides pour les surfaces qui **convergent**, comme le segment officiel.
- ⭐ **Le vrai objectif devient nommable** : ce n'est pas « réduire l'écart de 311 à 17 µm »,
  c'est **faire converger la mesure**. Une trace qui converge, même à 60 µm, suit une
  feuille ; une trace à α = 1 n'en suit aucune, quelle que soit sa valeur.
- ⭐⭐ Et c'est un **critère de sélection** utilisable dans la boucle de [`31`](31_roadmap.md)
  §4 : deux rendus par tirage, aucun seuil à régler, aucune référence à choisir.

## 5. ⚠ Ce que ce document ne dit pas

- **Il ne mesure qu'un tirage** pour la série complète (`PHerc1447 r2`, cinq fenêtres) et un
  segment officiel. La forme est franche — α de 0,00 contre 1,01 — mais deux surfaces ne
  font pas une population.
- **Il ne dit pas pourquoi** la trace est posée en travers. Le traceur, la graine, la
  prédiction de surface, ou les trois.
- **Il ne remplace pas l'auto-intersection** : une surface peut converger *et* se croiser.
  Les deux axes de [`37`](37_les_deux_axes_ne_saccordent_pas.md) restent indépendants, et
  celui-ci est une meilleure version du second, pas du premier.

## L'hypothèse qui inverse : testée, et le résultat va dans son sens

2026-08-20, soir. Une coupe radiale **ne peut pas** se croiser elle-même ; une surface qui
suit une spire revient près d'elle-même à chaque tour. Si c'est vrai, le filtre
d'auto-intersection écarte précisément les bonnes traces — et
[`34`](34_un_verdict_qui_ne_mesure_rien.md) a déjà montré que ce filtre ne mesure pas ce
qu'il prétend.

Deux essais du même rouleau, passés au test de convergence
(`src/outils/convergence_des_essais.sh`, en fond) :

| essai | auto-intersections | 41 couches | 161 couches | **α** | verdict |
|---|---:|---:|---:|---:|---|
| `essai_scale1` | **0** | 187,2 µm | 730,2 µm | **+0,99** | suit la fenêtre — **en travers** |
| `essai_ng2` | **112 139** | 112,3 µm | 271,5 µm | **+0,65** | intermédiaire |

⭐ **Celui qui a zéro croisement est le plus radial des deux.** L'essai catastrophique au
sens du filtre est celui qui se rapproche le plus d'une feuille. C'est la direction que
l'hypothèse prédisait, et elle a été écrite **avant** la mesure.

⚠ **Mais α = +0,65 n'est pas une trace qui suit une feuille** : le segment officiel donne
+0,00. Un intermédiaire n'est pas un demi-succès, c'est une surface qui traverse *moins*
d'empilement — peut-être une feuille suivie par morceaux, peut-être une coupe oblique. Le
test sépare « posée à côté » de « posée en travers » et ne dit rien de plus.

⚠ **Ce qui joue contre l'hypothèse, dit d'avance et toujours vrai** : le segment officiel
converge **sans** compte de croisements catastrophique. Si se croiser était la marque d'une
bonne trace, il devrait en avoir. Donc au mieux « beaucoup de croisements » est un
*symptôme* de suivi de spire, jamais son critère.

## ⭐⭐ Une cause candidate, trouvée le lendemain

⚠ **Une première version de cette section accusait le masque binaire** (`…-th0.2.zarr`,
deux valeurs). C'était faux et [`41`](41_marcher_le_long_dune_nappe.md) §6ter le corrige :
le traceur calcule lui-même un champ de distance **signé** à partir du masque.

⭐⭐ **Ce qui manque n'est pas le champ, c'est son poids.** Lu dans `GrowPatch.cpp` :
`SURFACE_SDT` vaut **0** par défaut, `NORMAL`/`SNAP` ne s'appliquent qu'avec une grille de
normales, `DIRECTION` qu'avec des champs de direction. Nos runs de base n'ont aucun des
trois. ⚠ **Mais « il ne reste que la géométrie » serait trop fort** : la doc officielle du
traceur décrit un terme de données primaire (`thresholdedDistance`) que je n'ai pas su
suivre jusqu'aux résidus — corrigé dans [`41`](41_marcher_le_long_dune_nappe.md) §6ter.
Ce qui est vérifié, c'est que **trois leviers de données sont éteints chez nous**.

⚠⚠ **C'est une hypothèse, pas la conclusion de ce document.** Elle expliquerait α = +1,01,
et elle est cohérente avec le fait qu'`essai_ng2` — le seul essai poussé avec une grille de
normales — soit le moins radial (α = +0,65). L'établir demande de relancer les mêmes traces
avec `sdt_weight` puis avec les fibres, et de voir la convergence changer :
`src/outils/leviers_de_perte.sh`.

## Reproduire

```bash
# une trace, plusieurs fenêtres
for n in 21 41 81 161; do
  ./src/outils/lancer.sh src/campagnes/campagne_second_axe.sh "$PWD/data/second_axe_$n" $n "$PWD/data/tirages/PHerc1447/r2"
done
# le segment officiel dans la même fenêtre
./src/outils/lancer.sh src/outils/officiel_fenetre_appariee.sh "$PWD/data/officiel_appariee" 81

(cd experiments && uv run python ../src/commun/test_convergence.py \
  --serie "31:17.28,81:17.30"                      --nom "segment officiel" \
  --serie "21:86.4,41:159.84,81:311.04,161:682.56" --nom "notre trace" \
  --json ../docs/convergence.json)
uv run python src/figures/figure_convergence.py
```
