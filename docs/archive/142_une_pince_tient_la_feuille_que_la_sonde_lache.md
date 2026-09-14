# 142 — Une pince tient la feuille que la sonde lâche

> ⭐⭐⭐⭐ **L'IDÉE DE L'AUTEUR EST MESURÉE, ET ELLE TIENT — SUR LA CAUSE QUE `140` A NOMMÉE.** Deux
> rouleaux compresseurs qui tiennent une feuille, transposés dans le volume : une **mâchoire** est
> un appui large qui repose sur un **interstice**, et une **pince** en a deux, une de chaque côté de
> la même feuille. Sur la spirale à l'écrasement **mesuré** (0,2782, celui que `135` impose) et à
> bruit 16, une sonde à une seule mâchoire finit sur la **bonne feuille 2 fois sur 12** ; la pince
> **10 fois sur 12** — et elle boucle **11** tours sur 12 contre **7**.
>
> ⭐⭐⭐⭐ **ET LES DEUX INGRÉDIENTS PAIENT SÉPARÉMENT.** La seconde mâchoire divise la dérive par
> **18,178**, la contrainte par **1,586** de plus, soit **28,826** en tout. La seconde mâchoire
> achète l'**épaisseur** : elle la mesure (**151,1 µm**) là où une seule ne peut que la supposer. La
> contrainte achète le refus : un appui n'a pas le droit de changer d'interstice en un pas.
>
> ⭐⭐⭐ **LE VERDICT EST UN COUPLE, ET C'EST CE QUI L'EMPÊCHE D'ÊTRE TAUTOLOGIQUE.** Une pince qui
> refuse tout ne dérive jamais et ne va nulle part. On mesure donc **sur quelle feuille** chaque
> bras finit *et* **jusqu'où** il va — et la pince gagne sur les deux à la fois, pas sur l'un aux
> dépens de l'autre.
>
> ⚠⚠ **ELLE NE GAGNE PAS PARTOUT, ET C'EST LA MOITIÉ IMPORTANTE.** Sur les **14** cases qui séparent
> quelque chose, elle en gagne **5** ; les **6** autres cases sont le témoin, où les trois bras
> réussissent tout. Elle perd sur les matières **froissées** : une pince exige de voir ses **deux**
> interstices, et un froissement assez raide lui en cache un — là, une seule mâchoire continue de
> marcher.
>
> ⚠⚠ **Et la matière que `140` retient — écrasée ET froissée à 100 µm — ne laisse AUCUN bras boucler
> un tour.** La pince est démontrée sur l'écrasement, pas sur toute la matière du rouleau. C'est dit
> ici plutôt que laissé à découvrir.

## 1. Pourquoi ce fichier

Le graal demande ce qui remplace l'humain qui corrige le transfert de spire à spire. Trois tranches
ont préparé la réponse, et chacune en a retiré une pièce :

- `138` : deux sondes **libres** séparées d'un seul voxel dérivent de **2,743 feuilles**, et l'écart
  entre elles n'y change rien. Ce n'est pas la matière qui les sépare, c'est le marcheur qui
  amplifie — donc il faut **contraindre** le marcheur, pas mieux le mesurer.
- `140` : la conversion est **prévisible depuis l'écrasement**, que le dépôt sait lire.
- `141` : il n'existe **pas** d'endroits où le chemin part de travers qu'une alarme pourrait
  signaler. La pièce manquante n'a donc rien à **détecter** — elle doit seulement ne jamais lâcher.

Ce qui restait était l'objet lui-même, et il vient de l'auteur : **deux rouleaux compresseurs**.

## 2. ⭐⭐⭐ Ce qu'est une mâchoire, et pourquoi elle a une largeur

Une mâchoire est un appui qui repose sur un **interstice**. Elle n'est pas un point, et c'est ce qui
la rend capable de donner une **orientation** : ses appuis latéraux tombent sur la surface de
l'interstice, donc la droite qui les joint est une tangente de cette surface, et la normale s'en
déduit. Deux points cherchés le long d'une même normale supposée sont alignés sur cette normale par
construction — ils ne la corrigent jamais.

⚠ **Les deux solutions de rechange sont mesurées, pas écartées d'un revers de main.** Sur la
spirale écrasée seule — sans froissement, pour que le plan moyen d'une mâchoire et la normale
ponctuelle coïncident — soixante poses par niveau de bruit :

| bruit | mâchoire | gradient au voxel | gradient au quart de pas | tenseur de structure |
|---|---|---|---|---|
| 0 | **0,108°** · 219 lectures | 0,015° · 6 | 8,515° · 6 | 68921 lectures |
| 4 | **3,857°** · 219 lectures | 53,769° · 6 | 21,08° · 6 | 68921 lectures |
| 8 | **4,358°** · 219 lectures | 53,514° · 6 | 33,227° · 6 | 68921 lectures |
| 16 | **6,217°** · 219 lectures | 51,628° · 6 | 51,631° · 6 | 68921 lectures |

Un gradient central est excellent **sans bruit** et s'effondre dès qu'il y en a : à bruit 4 il rend
**53,769°**, c'est-à-dire une direction qui ne veut plus rien dire. L'élargir ne le sauve pas — il
échange du bruit contre de la courbure, et finit au même endroit. La mâchoire tient **4,358°** à
bruit 8 pour **219** lectures, et le tenseur de structure qu'emploie `marcher` en coûte **68921** par
pas.

⚠ Trois appuis est le plus petit nombre qui laisse une redondance : deux définissent une droite
exactement, donc ne peuvent jamais la contredire. Un seul appui est **refusé** — un point ne forme
aucun nuage, donc il ne porte aucune direction.

## 3. ⭐⭐⭐ Les trois bras, et ce que chaque passage isole

Un seul ingrédient change d'un bras au suivant, ce qui est la seule façon de dire lequel paie.

1. **une mâchoire** — un appui sur l'interstice extérieur seulement. Elle doit alors **supposer** où
   est la feuille : une demi-épaisseur sous son appui, à la valeur nominale. C'est la sonde libre de
   `138`, rendue aussi capable qu'on peut la rendre.
2. **deux mâchoires libres** — les deux interstices, donc l'épaisseur est **mesurée** et le centre
   est le milieu de ce qu'on tient. Rien n'est refusé.
3. **la pince** — le bras 2, plus le refus.

⚠⚠ **Le refus n'est pas un seuil choisi.** Les interstices sont espacés d'une épaisseur, donc
l'appariement au plus proche bascule exactement à une **demi-épaisseur** : « c'est le même
interstice » et « le déplacement est inférieur à une demi-épaisseur » sont le **même énoncé**. Un pas
refusé est halvé puis retenté, jusqu'à ce que l'avance tombe sous le **voxel** — en dessous, un
déplacement n'est plus exprimable par le lecteur.

⚠⚠ **Et la seconde mâchoire achète une deuxième chose, qui n'est pas un choix mais une conséquence :
la fenêtre de recherche.** Le long d'une normale, le prochain interstice est à une demi-épaisseur et
le suivant à une épaisseur et demie, donc une fenêtre d'**une épaisseur** en contient exactement un.
Sur une matière écrasée l'espacement local va de **125 à 221 µm** pour un pas nominal de 173 : une
fenêtre nominale attrape alors le mauvais minimum. Une seule mâchoire n'a rien pour la régler — elle
ne mesure aucune épaisseur, et c'est exactement son infirmité.

## 4. ⭐⭐⭐⭐ La mesure

![La pince à ses proportions, ce qu'elle tient, et où elle gagne](../images/142_la_pince.png)

Un tour entier, **12 départs** par case, mâchoire de **43,2 µm**, avance **98,4 µm**. Chaque cellule
donne : sur combien de départs le bras finit sur la **bonne feuille**, la dérive médiane en feuilles,
et combien de tours il **boucle**.

| matière | bruit | une mâchoire | deux mâchoires libres | la pince |
|---|---|---|---|---|
| nue | 0 | 12/12 · 0,0 · 12/12 | 12/12 · 0,0 · 12/12 | 12/12 · 0,0 · 12/12 |
| nue | 4 | 12/12 · 0,0138 · 12/12 | 12/12 · 0,0143 · 12/12 | 12/12 · 0,0143 · 12/12 |
| nue | 8 | 12/12 · 0,0289 · 12/12 | 12/12 · 0,0143 · 12/12 | 12/12 · 0,0143 · 12/12 |
| nue | 16 | 12/12 · 0,0504 · 12/12 | 12/12 · 0,0323 · 12/12 | 12/12 · 0,0323 · 12/12 |
| écrasée | 0 | 12/12 · 0,0005 · 12/12 | 12/12 · 0,0 · 12/12 | 12/12 · 0,0 · 12/12 |
| écrasée | 4 | 10/12 · 0,021 · 10/12 | 8/12 · 0,0145 · 9/12 | 8/12 · 0,0145 · 10/12 |
| écrasée | 8 | 10/12 · 0,0623 · 11/12 | 11/12 · 0,0186 · 11/12 | 10/12 · 0,0186 · 10/12 |
| **écrasée** | **16** | **2/12 · 1,0925 · 7/12** | **8/12 · 0,0601 · 10/12** | **10/12 · 0,0379 · 11/12** |
| froissée 42,4 µm | 0 | 12/12 · 0,095 · 12/12 | 12/12 · 0,0369 · 12/12 | 12/12 · 0,0369 · 12/12 |
| froissée 42,4 µm | 4 | 12/12 · 0,1114 · 12/12 | 9/12 · 0,2794 · 4/12 | 8/12 · 0,3397 · 4/12 |
| froissée 42,4 µm | 8 | 12/12 · 0,0704 · 12/12 | 3/12 · 0,8921 · 4/12 | 7/12 · 0,4597 · 1/12 |
| froissée 42,4 µm | 16 | 5/12 · 0,9802 · 8/12 | 1/12 · 2,51 · 0/12 | 3/12 · 0,9526 · 0/12 |
| écrasée et froissée 42,4 µm | 0 | 11/12 · 0,141 · 8/12 | 10/12 · 0,0225 · 10/12 | 11/12 · 0,0225 · 10/12 |
| écrasée et froissée 42,4 µm | 4 | 1/12 · 1,6925 · 6/12 | 5/12 · 0,5638 · 5/12 | 5/12 · 0,5638 · 2/12 |
| écrasée et froissée 42,4 µm | 8 | 1/12 · 2,2403 · 5/12 | 1/12 · 1,6495 · 0/12 | 4/12 · 0,5237 · 1/12 |
| écrasée et froissée 42,4 µm | 16 | 0/12 · 4,4822 · 0/12 | 6/12 · 0,4977 · 0/12 | 4/12 · 0,8216 · 0/12 |
| écrasée et froissée 100 µm | 0 | 8/12 · 0,3576 · 0/12 | 6/12 · 0,4473 · 0/12 | 7/12 · 0,4257 · 0/12 |
| écrasée et froissée 100 µm | 4 | 4/12 · 2,1977 · 0/12 | 6/12 · 0,3619 · 0/12 | 7/12 · 0,3316 · 0/12 |
| écrasée et froissée 100 µm | 8 | 0/12 · 2,2961 · 0/12 | 3/12 · 0,7252 · 0/12 | 4/12 · 0,581 · 0/12 |
| écrasée et froissée 100 µm | 16 | 1/12 · 8,0314 · 0/12 | 0/12 · 1,6431 · 0/12 | 1/12 · 1,5735 · 0/12 |

⚠ **La question « sur quelle feuille » est exacte, pas tolérante.** On est sur la même feuille quand
la dérive est sous une **demi-feuille** : c'est là que l'appariement au plus proche bascule, comme la
demi-épaisseur qui décide qu'un appui a changé d'interstice. Départager 0,0138 de 0,0143 feuille
serait rendre un verdict sur du bruit — les deux disent la même chose, la bonne feuille.

⚠ **Le témoin existe et il est compté** : **6** cases sur 20 où les trois bras réussissent tout. Sans
elles, « la pince gagne » n'aurait rien à quoi se comparer. Et une case témoin n'est **pas** comptée
comme une victoire, sinon le score de la pince serait gonflé d'exactement ce que le témoin sert à
exclure.

⚠ **La largeur de mâchoire est balayée, jamais posée** — une mâchoire large moyenne davantage de
bruit et davantage de courbure, donc il y a un compromis et il se mesure. Sur la case de tête :

| largeur | la pince | une mâchoire |
|---|---|---|
| 0,125 pas (21,6 µm) | dérive 0,6263, **0** tour bouclé | 4,9832 |
| 0,25 pas (43,2 µm) | dérive **0,0379**, **11** tours | 1,0925 |
| 0,5 pas (86,5 µm) | dérive 0,043, **11** tours | 1,1274 |

La largeur de référence est au milieu de l'intervalle, et le balayage montre qu'une mâchoire deux
fois plus étroite ne boucle plus rien.

⚠ **Et le chemin, qui dit la même chose autrement** : sur la case de tête, une mâchoire met **1811**
pas pour un tour là où la pince en met **809**. Elle ne dérive pas seulement, elle **erre** — plus du
double du chemin pour le même tour.

## 5. ⭐⭐ Ce que ça change pour le graal

**La pièce manquante a maintenant une forme, et c'est un objet mécanique.** `138` disait qu'il faut
contraindre ; `141` disait que la contrainte n'a rien à détecter ; `142` montre qu'une contrainte qui
tient la feuille par ses **deux** interstices ramène le transfert de spire à spire de 2 réussites sur
12 à 10 sur 12, sur la cause que `140` a identifiée comme dominante.

**Et le partage avec le cap se lit tout seul.** `139` mesure que le cap récupère **73 %** de
l'obliquité d'un froissement, et `140` que le cap enlève ce qui **alterne**, pas ce qui **persiste**.
`142` montre l'inverse pour la pince : elle tient contre l'écrasement — la cause qui persiste — et
perd contre le froissement. Les deux instruments ne se remplacent pas, ils se complètent : le cap
contre ce qui alterne, la pince contre ce qui persiste.

⚠ **Ce que ça ne dit pas.** Que la pince suffise. Sur la matière que `140` retient — écrasée **et**
froissée à 100 µm — aucun bras ne boucle un tour, à aucun niveau de bruit, y compris sans bruit. Ce
qui est établi est plus étroit et plus solide : **sur l'écrasement mesuré, tenir les deux interstices
d'une feuille change le transfert de spire à spire d'un facteur vingt-neuf.**

## 6. ⚠ Ce que la mesure a corrigé d'elle-même

- **Un suiveur qui partait en vrille**, jusqu'à quarante feuilles de dérive sur un quart de tour.
  Deux causes, trouvées par sondes successives et non par relecture : un minimum accepté au **bord**
  de sa fenêtre — un centre qui dérive sur un interstice y trouve alors le plus petit échantillon au
  premier pas, l'épaisseur s'effondre, et la pince se referme sur elle-même ; et une fenêtre qui
  partait de zéro au lieu d'être **centrée sur l'endroit attendu**, ce qui lui faisait manquer un
  interstice poussé plus loin par le froissement.
- ⚠⚠ **Une dérive de exactement 1,0000 feuille par tour, que j'ai d'abord lue comme un échec de la
  pince.** C'est la **coupure angulaire** : la docstring de la fixture l'annonce depuis toujours — en
  franchissant `±π` la valeur de la phase saute d'une feuille alors que la matière est identique. La
  phase est déroulée avant d'être lue.
- **Une avance trop grossière** : 173 µm pour une longueur d'onde de froissement de 393,6. Le suiveur
  sous-échantillonnait l'ondulation qu'il devait suivre. L'avance est une fraction de la longueur
  d'onde, pas du pas.
- ⚠⚠ **Un de mes propres contrôles était incapable d'échouer** (`… is None or True`) — le péché nº 1
  de ce dépôt, écrit de ma main. Remplacé par un refus réel : une mâchoire à un seul appui est
  refusée, pas devinée.
- ⚠⚠ **Deux réponses à « cette case ne sépare rien »** : le tableau en comptait deux quand l'image en
  peignait cinq. Le critère vit maintenant chez le producteur, et la figure le lit.
- **Une mâchoire jugée sur la mauvaise question.** J'ai d'abord comparé la normale d'une mâchoire à
  la normale **ponctuelle** de la feuille et lu un échec de 20°. Une mâchoire de demi-largeur `w` suit
  le plan **moyen** sur `w` ; sur une feuille froissée les deux diffèrent réellement. Ce n'est pas la
  mâchoire qui ratait, c'est la question.

## 7. Les registres

Faits `R4-F91` (une pince à deux mâchoires ramène le transfert de spire à spire de 2 réussites sur 12
à 10 sur 12 sur l'écrasement mesuré), `R4-F92` (les deux ingrédients paient séparément : l'épaisseur
mesurée divise la dérive par 18,178, la contrainte par 1,586 de plus) et `R4-F93` (une pince perd sur
une matière froissée, parce qu'elle exige de voir ses deux interstices). Porte `R4-P26` : ce qu'elle
demandait — une lecture locale qui dise *quelle* feuille on tient — reçoit une réponse qui n'est pas
une lecture mais une **contrainte**.

## Reproduire

```bash
uv run python src/nappe/la_pince_tient_elle_la_feuille.py \
    --json docs/mesures/la_pince_tient_elle_la_feuille.json   # aucune lecture distante
uv run python src/figures/figure_la_pince_tient_elle_la_feuille.py \
    --json docs/mesures/la_pince_tient_elle_la_feuille.json \
    --sortie docs/images/142_la_pince.png
uv run python src/nappe/la_pince_tient_elle_la_feuille.py --verifier            # 37
uv run python src/figures/figure_la_pince_tient_elle_la_feuille.py --verifier   # 18
```

⚠ `--reagreger <json>` recalcule les résumés et le verdict depuis les suivis rangés, sans remarcher :
une règle de jugement qui change ne doit pas coûter dix minutes de marche. C'est le `--reagreger` de
`138` et le `--rejuger` de `141`, sous le même nom que le premier.

⚠ La vérité est connue parce que la mesure est sur **fixture** : sur une spirale d'Archimède, suivre
la feuille de phase `k` sur un tour entier y ramène exactement, ce que le vrai rouleau ne peut pas
offrir.
