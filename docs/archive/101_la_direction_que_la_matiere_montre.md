# 101 — La direction que la matière montre : l'obliquité de `100` est réelle

> ⭐⭐⭐ **La matière suit le maillage, pas le rayon.** Le tenseur de structure du volume fin —
> sans aucun maillage — rend une normale à **13,3°** de celle du maillage humain et à **34,6°** du
> rayon, sur les 28 bandes. Et ce **34,6°** recoupe **indépendamment** le **34,06°** que `100`
> lisait sur le maillage seul : deux instruments qui ne partagent rien.
>
> ⭐⭐ **Avec le pas de `99` et la direction d'ici, un automate a les deux nombres qu'il faut**
> pour franchir une feuille sans humain — et la matière les donne sur **64 %** des cellules,
> **plus souvent au bord** que `99` n'y trouvait de périodicité.

![la direction que la matière montre](../images/101_la_direction_que_la_matiere_montre.png)

## 1. Pourquoi ce fichier, et c'est `100` qui l'impose

`100` a mesuré que la normale du maillage humain est à **34,1°** du rayon là où une spirale de ce
pas en prédit **0,09°**, et que deux estimateurs sans hypothèse commune s'accordent dessus. Il
restait **deux lectures**, et elles ne se distinguent pas dans le maillage :

| | lecture |
|---|---|
| **(a)** | la matière est réellement oblique au rayon, et le maillage la suit fidèlement |
| **(b)** | la matière est à peu près radiale, et c'est le **maillage** qui est oblique à la matière — c'est-à-dire que la surface tracée par les humains **ne repose pas sur une feuille** |

⭐ Seule la matière peut trancher, et elle le peut : le **tenseur de structure** — la covariance
des gradients d'intensité dans un petit cube du volume fin — a pour vecteur propre dominant la
direction dans laquelle l'image varie le **plus**, c'est-à-dire la normale de la feuille. Aucun
oracle, aucune supervision, aucun modèle.

⭐⭐ **Et la conséquence pour le graal est directe.** `99` rend le **pas** que la matière montre ;
ce fichier rend la **direction**. Les deux ensemble sont exactement ce qu'un automate doit savoir :
*avance de `p(matière)` le long de `n(matière)`*.

## 2. ⭐⭐⭐ Le verdict : la matière suit le maillage

| | mesuré |
|---|---|
| angle de la matière au **maillage** | **13,32°** |
| angle de la matière au **rayon** | **34,59°** |
| écart entre les deux lectures | **21,27°** |
| part de cellules **orientées** | **0,636** |
| planarité médiane de la matière | **0,685** — contre **0,3365** au bruit pur |
| bandes lues | **28** |

> ⭐ Et le recoupement est le fait qui compte : `100` lisait **34,06°** entre la normale du
> **maillage** et le rayon ; ce fichier lit **34,59°** entre la normale de la **matière** et le
> rayon, avec un instrument qui ne partage ni les données ni le principe. L'obliquité est donc une
> propriété de la **matière**, pas un artefact du maillage.

⚠⚠ **Ce que ça dit du référent humain, et c'est une nuance qui compte.** Le maillage est sur la
matière en **orientation**, à treize degrés — alors que `97` a mesuré qu'il se trompe de plus d'une
demi-feuille en **identité**. Ce sont **deux pannes différentes**, et une seule est fatale : savoir
sur *quelle* feuille on est.

## 3. ⭐⭐⭐ La dernière explication alternative est réfutée par sa signature

La direction radiale est calculée depuis l'axe du rouleau. Si cet axe est décalé de `d`, la
direction calculée tourne de `arctan(d / r)` — et `90` a mesuré que l'axe **dérive de 12,6 mm** sur
la hauteur du fragment, donc l'hypothèse n'était pas farfelue.

⭐⭐ **Mais elle prédit une décroissance en 1/r, et c'est ça qui la rend falsifiable.**

| | valeur |
|---|---|
| décalage qui explique le **cœur** (4,1 mm de rayon, 35,2° mesurés) | **2,87 mm** |
| ce même décalage prédit au bord | **6,9°** — où l'on mesure **24,0°** |
| décalage qui explique le **bord** (23,8 mm, 24,0° mesurés) | **10,61 mm** |
| ce même décalage prédit au cœur | **69,0°** — où l'on mesure **35,2°** |
| résidu du modèle **d'axe décalé** (1 paramètre) | **12,2°** |
| résidu du modèle **d'obliquité constante** (1 paramètre) | **8,7°** |

> ⛔ **Un axe décalé explique donc MOINS BIEN** qu'une obliquité constante, à nombre égal de
> paramètres libres.

⭐ **Et le verdict sait dire oui**, ce qui est la condition pour que son « non » veuille dire
quelque chose : sur un jeu fabriqué dont les angles suivent `arctan(d/r)` avec `d = 5 mm`, il
retrouve **5,0 mm** et conclut que l'axe explique. Sur un jeu d'angles constants, il conclut que
non.

## 4. ⚠⚠⚠ Deux corrections d'instrument, toutes deux trouvées par la mesure

### 4.1 ⛔ La planarité est réfutée comme juge de direction

La **planarité** — la part de la variation d'image qui tient dans une direction — était le juge
naturel de « la matière a-t-elle une orientation ici ». Le balayage de bruit dit non :

| σ du bruit | gradient du bruit / voxel | angle lu | planarité |
|---|---|---|---|
| — bruit pur, sans signal | — | (aléatoire) | **0,3365** |
| 0 | 0,0 | 0,02° | 1,000 |
| 4 | 5,7 | 0,42° | 0,455 |
| 8 | 11,3 | 1,74° | 0,370 |
| 15 | 21,2 | **7,51°** | **0,345** |

Le gradient du **signal** par voxel vaut `A · 2π / T` = **3,49** ; celui du **bruit** vaut
`σ · √2` = **21,2** à σ = 15. Le bruit domine donc le signal d'un facteur **six par voxel** — et
la direction reste juste, parce qu'un bruit isotrope s'annule dans la **moyenne** des produits
extérieurs sans s'annuler dans leur **rapport**.

> ⛔⛔ **Fermer sur la planarité aurait donc été une garde qui supprime ce qu'elle doit laisser
> passer** — le péché que `97` a payé avec son critère de bord. Elle est gardée et publiée, mais
> comme une mesure de contraste, jamais comme un juge de direction.

⭐ **La garde qui la remplace n'a besoin d'aucun modèle nul** : l'**accord des deux moitiés
disjointes** du même cube. Si la direction est réelle, les deux moitiés s'accordent ; si c'est du
bruit, non. C'est la discipline des « deux estimateurs sans hypothèse commune » de `100`, ramenée à
l'intérieur d'un seul cube — et elle se calibre elle-même.

### 4.2 ⚠⚠⚠ `np.gradient` injectait une anisotropie au bord du cube

Ses **plans extrêmes** prennent des différences **unilatérales**, dont la variance vaut **quatre
fois** celle d'une différence centrée. Le cube injecte donc une anisotropie à son propre bord : ses
plans extrêmes en z gonflent `gz`, ceux en y gonflent `gy`.

> ⚠ **Mesure du défaut** : sur du **bruit pur**, deux moitiés d'un même cube coupées selon z
> s'accordaient à **10,4°** au lieu des **~60°** que deux directions au hasard donnent en trois
> dimensions — parce que la coupe crée un nouveau bord en z et biaise les **deux** moitiés vers z.

C'est *un estimateur qui mesure la grille* (`97`) sous un nouveau costume, et il aurait rendu une
garde qui **paraît stricte tout en laissant passer du bruit**, plus une direction de matière tirée
vers z. Plans de bord jetés, le nul remonte à **62,03°** et la barre devient **8,88°** (le p1 du
bruit pur).

⚠ **Et la taille du cube est dérivée, pas choisie** : à demi = 10 le même empilement bruité **ne
passe pas** la garde (40,1° contre une barre de 15,5) parce qu'une moitié de dix plans n'en garde
que huit après le rejet des bords ; à demi = 20 il passe (**3,46°** contre 10,06). Le contraste
entre les deux tailles est asserté.

## 5. ⚠⚠ La condition qui rend la confrontation possible, vérifiée et non supposée

L'angle du maillage vit dans les voxels à **45,532 µm**, la direction de la matière dans ceux à
**2,4 µm**. Une transformation qui **cisaillerait** ne conserverait pas les angles, donc « 34° » ne
voudrait rien dire d'un volume à l'autre — et l'écart serait **silencieux**, les deux nombres
restant plausibles.

> ⭐ Mesure : conditionnement **1,0075**, écart maximal de `R Rᵀ` à l'identité **0,0053**, soit
> **0,301°**. Négligeable devant les dizaines de degrés mesurées, mais il fallait le montrer.

⚠ Et une **direction** ne se transporte pas comme un point : la translation ne s'y applique pas.
`appliquer_direction` vit à côté d'`appliquer`, dans le seul endroit qui connaît l'inversion
d'axes — passer une direction à `appliquer` ajouterait le décalage de 5000 voxels de la matrice et
rendrait un vecteur pointant vers un coin du volume, parfaitement fini et parfaitement faux.

## 6. ⚠⚠ Un signal, et son confondant retiré

| | brut | à rayon tenu |
|---|---|---|
| part orientée contre la rupture de continuité | **+0,581** | **+0,452** |
| écart maillage/matière contre la rupture | +0,078 | −0,366 |
| part orientée contre le rayon | **+0,421** | |
| rupture de continuité contre le rayon | **+0,815** | |

La part orientée monte vers le bord **et** la rupture monte vers le bord, donc « la matière répond
mieux là où le transfert casse » et « la matière répond mieux au bord » sont la **même
observation** tant que le rayon n'est pas tenu constant — et une seule des deux est un résultat.
⭐ L'instrument vient de `95`, importé et non recopié.

> ⭐⭐ **À rayon tenu, le lien survit : +0,452.** La matière donne une direction **plus souvent au
> bord**, là où `99` perdait la périodicité (0,54 d'utilisable). C'est un **acquis** : la direction
> survit là où le pas ne survit pas.

⛔ **Et ce qui n'est pas un signal, il faut le dire** : l'écart du maillage à la matière ne prédit
**pas** la rupture — **+0,078** brut, **−0,366** à rayon tenu, sur 28 bandes. C'est faible et de
signe instable ; s'en servir serait lire du bruit.

## 7. ⚠⚠ Ce que ce document ne dit pas

- **Pourquoi la surface est oblique n'est pas tranché** — écrasement, cône réel, ou propriété du
  traçage. Le fait est maintenant confirmé par deux instruments indépendants ; sa cause non.
- **L'écart de pas de `99` reste inexpliqué.** `100` en a éliminé un candidat, ce fichier confirme
  que l'obliquité est réelle sans pour autant expliquer l'écart — puisque le pas ne dépend pas de
  la direction.
- ⚠ Le tenseur de structure lit une orientation **locale**, à l'échelle de **98,4 µm**. Il ne dit
  pas *quelle* feuille, seulement *comment elle est posée* — donc il ne remplace pas à lui seul
  l'humain qui corrige l'**identité** de la feuille, qui est la panne que `97` a mesurée.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/la_direction_que_la_matiere_montre.py --verifier
uv run python src/nappe/la_direction_que_la_matiere_montre.py --cellules 12 --demi 20 \
    --json docs/mesures/la_direction_que_la_matiere_montre.json
uv run python src/nappe/la_direction_que_la_matiere_montre.py --reagreger \
    --json docs/mesures/la_direction_que_la_matiere_montre.json   # rederive, sans reseau
uv run python src/figures/figure_la_direction_que_la_matiere_montre.py --verifier
```
