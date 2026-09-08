# 85 — Le rang monte vers le dehors, et une passe humaine couvre un tiers de mètre

> ⭐⭐⭐ **27 montées de rayon sur 27 paires, et le verdict survit à un second centre.** Le rayon
> passe de **7,41 mm** au rang 10 à **24,84 mm** au rang 128. La lecture de
> [`84`](84_une_surface_combien_de_spires.md) tient donc : la décroissance des bandes est bien la
> direction radiale.

Et la prédiction que j'avais ajoutée pour rendre l'explication **falsifiable** a rendu davantage :
une passe humaine couvre **384 mm de feuille en médiane**, et hors la bande du cœur les 27 autres
tiennent dans **283 à 535 mm** — un facteur 1,9.

![le rang monte-t-il vers le dehors, et une passe couvre-t-elle une longueur constante](images/85_le_sens_du_rang.png)

## 1. Ce qui tranche, et ce que ça coûte

`84` mesure que les 28 bandes de `PHercParis4` décroissent sans une seule inversion, et nomme
explicitement ce qu'il ne sait pas : **dans quel sens va le rang**. Ce qui tranche est un **rayon**,
et il se lit sur le maillage le moins cher publié — le `tifxyz-transformed` sur le volume à
**45,532 µm**, 330 Kio par canal, **un mébioctet par bande**, vingt-huit mébioctets en tout.

⚠⚠ **L'axe est une estimation, et le verdict doit survivre à deux estimations.** Un centre pris sur
une bande partielle est biaisé vers son arc ; on prend donc la **médiane** de tous les points de
toutes les bandes, puis on refait le classement avec le centre de la seule bande intérieure. Les
deux rendent le même ordre. ⭐ Une sonde le confirme dans l'autre sens : forcer le centre à
l'origine fait tomber **sept** contrôles, dont le sens lui-même.

> ## ⚠⚠⚠ RÉTRACTATION — [`90`](90_laxe_est_une_courbe.md), le 2026-09-08
>
> **L'axe estimé ici est UN point (x, y). L'axe réel de ce fragment est une COURBE** : le centre
> par tranche se déplace de **12,6 mm en x et 19,8 mm en y** sur 144 mm de z, **en revenant sur
> ses pas**, et s'écarte de sa propre droite de **11,6 mm — 63,9 épaisseurs de feuille**.
>
> ⭐⭐ **Ce que §1 et §2 affirment SURVIT, et survit mieux** : le classement rend **27/27** sous
> l'axe courbe aussi, et la longueur par passe se **resserre** — 362 mm, 273 à 460, rapport
> **1,68** au lieu de 2,97.
>
> ⚠⚠⚠ **Ce qui est RETIRÉ : le « second régime » de la bande du cœur.** Elle valait 838 mm ici,
> un facteur 2,2 au-dessus des autres ; sous l'axe courbe elle vaut **460 mm** et rentre dans la
> distribution. Il n'y avait pas deux populations — il y avait mon erreur d'axe, concentrée sur la
> bande la plus **proche** de l'axe, donc la plus sensible à s'être trompé dessus. **Toutes les
> mentions d'un second régime ci-dessous sont fausses.**

## 2. ⭐⭐ La prédiction, et pourquoi elle rend l'explication falsifiable

Dire *« la circonférence croît vers l'extérieur, donc une passe y couvre moins de spires »* n'est
une histoire que tant qu'on ne la mesure pas. Si une passe couvre une **longueur de feuille** à peu
près constante, alors `étendue × 2πR` doit l'être aussi.

| | |
|---|---:|
| médiane sur les 28 bandes | **384 mm** |
| bornes, les 28 | 283 à 838 mm (**×2,97**) |
| bornes, **hors la bande du cœur** | **283 à 535 mm** (**×1,89**) |
| écart-type relatif, hors le cœur | **17 %** |

⭐ **Le nombre de spires tombe parce que les spires s'allongent, à longueur de feuille à peu près
constante.** La bande du cœur (18 spires, 838 mm) est publiée **à part** : c'est un second régime,
et une dispersion qui la mélangerait décrirait deux populations comme si elle en décrivait une.

## 3. ⚠⚠ Le résidu de 17 % n'est pas du bruit, c'est de la quantification

On ne coupe pas deux spires et demie. À l'intérieur d'un **palier** — une suite de bandes de même
étendue — la longueur croît donc **mécaniquement** avec le rayon, et l'étendue ne redescend qu'au
palier suivant. Mesuré : **9 paliers, et la longueur croît dans chacun des neuf**.

⚠ Les maximums atteints juste avant chaque descente d'étendue déclinent — **838, 535, 498, 490,
459, 436, 433, 415 mm** — ce qui **ressemble** à un budget par passe qui se réduit vers l'extérieur.
Mais un pas de quantification vaut une **circonférence entière** (156 mm au rang 128), donc à cette
précision les deux ne sont pas séparables. **La mesure rend les deux et ne tranche pas.**

## 4. ⚠⚠⚠ Ce que ce maillage NE peut pas donner, dit avant de s'en servir

Ses cellules voisines sont à **19,88 voxels** l'une de l'autre dans les deux directions de la
grille, soit **905 µm** — trois à six fois l'écart entre feuilles qu'on cherche. Une distance de
feuille à feuille lue dessus serait dominée par l'écart d'échantillonnage et non par la matière.

⭐ **C'est une limite de GRILLE, et elle est publiée comme telle** — mesurée sur la grille
elle-même, pas supposée. Conséquence directe : **la demi-feuille de `PHercParis4` reste un chiffre
à mesurer ailleurs**, et le coût d'un changement d'objet que
[`81`](81_le_rouleau_designe_ne_publie_rien.md) nommait n'est donc pas encore chiffré.

## 5. ⚠ Deux révisions d'une bande ne couvrent pas la même surface

Le maillage récent d'une bande porte **78 453** cellules valides sur une grille 184×448, l'ancien
**50 877** sur 119×449. Leurs rayons médians diffèrent donc, jusqu'à **15,9 %** sur la bande du
cœur, **0,5 %** en médiane.

⚠⚠ **Et c'est un contrôle que j'ai dû corriger deux fois.** D'abord il comparait les deux
révisions **par position** dans deux listes de longueurs différentes : une bande manquante décalait
tout, et l'écart annoncé — 16 % — était un désaccord de **mes deux listes**, pas des données.
Corrigé, il exigeait ensuite que les rayons ne bougent pas de plus d'un pour cent : **ils bougent de
15,9 %, et ce n'est pas un défaut**, c'est une différence de couverture. Un contrôle qui exigerait
l'égalité serait un contrôle qui ne peut pas passer pour une raison qui n'est pas un défaut.

⭐ Ce qui est **asserté** est donc le **classement**, et il survit entier — 27/27 montées sur
l'ancienne révision aussi. Une médiane est un résumé d'un échantillon ; un ordre est une propriété
de l'enroulement.

## 6. Ce que ça change

⭐⭐ **Le coût humain se compte en longueur de feuille, pas en nombre de spires.** Les ~25 h par
spire de l'état de l'art sont une moyenne sur un rouleau ; cette mesure dit que la même heure
couvre **neuf fois moins de spires** au bord qu'au cœur, à longueur de feuille égale. Donc « 31
spires » n'est pas l'unité naturelle de l'effort, et deux objets de 31 spires ne coûtent pas la
même chose.

⚠ Ce que ça ne change pas : les 31 spires restent ce que le prix demande, et la plus longue bande
publiée en vaut **18**.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --verifier
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/le_sens_du_rang.py --telecharger --toutes-revisions
uv run python src/nappe/le_sens_du_rang.py --json docs/mesures/le_sens_du_rang.json
uv run python src/figures/figure_le_sens_du_rang.py --verifier
```
