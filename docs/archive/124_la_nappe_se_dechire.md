# 124 — La nappe se déchire trois fois sur quatre, et ça ne se voit pas tôt

> ⭐⭐⭐⭐ **TOUT CE QUE `113` À `123` MESURENT PORTE SUR UNE MARCHE. LE GRAAL DEMANDE UNE NAPPE.**
> Deux marches voisines qui finissent sur deux feuilles différentes produisent une **déchirure**
> dans l'image déroulée — et c'est précisément ce que l'humain recoud. La question n'est pas
> mesurable sur le vrai volume ; elle l'est au centième de feuille sur une pile fabriquée.
>
> ⭐⭐⭐⭐ **NEUF LOTS SUR DOUZE SE DÉCHIRENT.** Huit marches parties de la même feuille, écartées
> de 96 µm, sur une pile inclinée à 35° et bruitée, après les **112 pas** d'une traversée : le saut
> entre voisines vaut **1,02 feuille** en médiane, et va de **0,116 à 20,59**.
>
> ⭐⭐⭐⭐ **ET LA DÉCHIRURE NE SE VOIT PAS TÔT** : la dispersion au pas 16 ne prédit pas le saut
> final — rho **+0,4545**, p **0,1377** sur 12 lots. Contrairement à la cécité (`115`, `116`), dont
> la signature est disponible **avant** le pas, celle-ci ne s'annonce pas.
>
> ⚠⚠⚠ **ET C'EST UNE CORRECTION DE CE QUE J'ALLAIS PUBLIER.** La première mesure portait sur **un
> seul tirage de bruit** et rendait 0,504 — j'allais écrire « la nappe tient, tout juste ». Ce
> tirage était **le meilleur des douze**.
>
> ⭐ **Zéro lecture distante.**

## 1. Pourquoi ce fichier

`119` a mesuré que la trajectoire ne dérive pas, `123` que le marcheur reste verrouillé sur les
feuilles. Les deux portent sur **une** marche. Une image déroulée est une **surface** : des marches
voisines mises côte à côte. La panne d'une surface n'est pas la dérive d'une ligne, c'est la
**séparation de deux lignes voisines**.

⚠ Et elle ne se mesure pas sur le vrai volume, où l'on ne sait pas où sont les feuilles.

## 2. Ce qui compte comme une déchirure

Le **saut entre deux marches voisines** — la différence de leurs phases finales, en feuilles.

⚠⚠ **Ce n'est pas le numéro de feuille**, et c'est une correction du premier prédicat : un faisceau
resté groupé mais dont la moyenne vient s'asseoir **sur une frontière** rend deux numéros
différents par simple arrondi, sans que rien ne se soit séparé. Une sonde de la batterie remet ce
cas et exige qu'il ne soit **pas** compté comme une déchirure.

⭐ Et c'est la même quantité que `91` mesure chez l'humain — *« le plus grand saut entre deux
cellules voisines d'une même ligne de grille »* — ce qui rend les deux lisibles côte à côte.

⚠ Une demi-feuille n'est pas un seuil réglé : c'est la distance au-delà de laquelle aucune
affectation cohérente ne met deux voisines sur la même feuille.

## 3. ⭐⭐⭐⭐ Douze graines, et une seule ne suffisait pas

| | |
|---|---:|
| lots qui se déchirent | **9 / 12** |
| saut médian entre voisines | **1,020 feuille** |
| étendue | **0,116** à **20,59** |
| lots couplés à la matière | 7 / 12 |

Sauts triés : 0,116 · 0,120 · 0,216 · **0,504** · 1,011 · 1,012 · 1,028 · 2,996 · 11,473 · 12,625 ·
13,586 · 20,591.

⚠⚠ **La première mesure de ce fichier était 0,504 — la quatrième plus basse des douze.** Publier
une réalisation de bruit en croyant publier la seule aurait donné exactement le résultat inverse.

⭐ **L'issue n'est pas graduelle** : il n'y a **aucun lot entre 0,504 et 1,011**. Trois lots restent
serrés sous la demi-feuille, quatre se posent au bord d'une feuille entière, cinq explosent au-delà
de trois. Ou la matière tient les marches ensemble, ou elle ne les tient pas.

## 4. ⭐⭐⭐ Le témoin : elles sont couplées quand elles tiennent

Le témoin permute, à chaque pas, **quelle marche reçoit quel incrément de phase** : la distribution
des incréments est gardée exactement, seul le lien entre une marche et ses propres incréments est
détruit.

Les sept lots serrés dispersent **bien moins** que ce tirage (par exemple 0,079 contre 1,111) : la
matière les couple, chacune relit la structure locale et aucune ne peut s'éloigner. Les cinq lots
éclatés ne battent pas le tirage — la matière a cessé de les tenir.

⚠ Sur une pile **sans bruit** les huit marches sont identiques : dispersion 0,0 et témoin « non
couplées ». Ce n'est pas un échec, c'est le contraste qui montre que toute la dispersion mesurée
vient du **bruit** et non du mécanisme.

## 5. ⭐⭐⭐⭐ Et elle ne s'annonce pas

| | |
|---|---:|
| rho entre la dispersion au pas 16 et le saut final | **+0,4545** |
| p | **0,1377** |
| lots | 12 |

⚠⚠ C'est la mauvaise nouvelle pour le graal. Pour la cécité, `115` et `116` ont établi que la
signature est disponible **avant** le pas, donc qu'un automate peut s'arrêter à temps. Ici, les
seize premiers pas ne disent pas ce que les cent douze donneront : l'automate ne peut que
**constater** les dégâts.

⚠ n = 12 : le test **cesse de rejeter** l'absence de lien, il ne la prouve pas. Un rho de +0,45 sur
douze lots est ce qu'on obtient aussi d'un vrai lien faible.

## 6. Ce que ça change pour le graal

- `119` et `123` disaient qu'**une** marche ne dérive pas. Ce document dit que **la nappe**, elle,
  se déchire trois fois sur quatre sous bruit et obliquité. Ce ne sont pas deux résultats
  contradictoires : une marche peut rester droite et verrouillée pendant que sa voisine part sur
  une autre feuille.
- ⭐ **C'est donc là que vit la valeur de l'humain**, et le document le mesure plutôt que de le
  supposer : il recoud ce que le mécanisme sépare, et il le fait parce que la séparation ne
  s'annonce pas.
- ⚠⚠ **Analytique, et ça borne ce que ça dit.** Une pile plane à pas constant n'a ni déchirure de
  papyrus, ni feuille qui fusionne — or `91` mesure que la vérité de terrain **humaine** devient
  elle-même discontinue au bord du rouleau. Ce qui est établi est que le **mécanisme** ne suffit
  pas, pas que le rouleau soit pire.

## 7. Les registres

Faits : `R4-F52` (la nappe se déchire trois fois sur quatre), `R4-F53` (la déchirure ne se voit pas
au pas 16). Porte `R4-P25` : ce qui tient deux marches voisines ensemble.

## Reproduire

```bash
uv run python src/nappe/la_nappe_se_dechire_t_elle.py --verifier   # 15 contrôles
uv run python src/nappe/la_nappe_se_dechire_t_elle.py \
    --json docs/mesures/la_nappe_se_dechire_t_elle.json            # douze graines, ~30 min
```

⚠ **Tout est analytique.** Le marcheur et les piles fabriquées sont **importés** ; le calcul de
phase est importé de `123`. Un second marcheur serait deux implémentations d'une même marche, et
c'est la marche qu'on mesure.
