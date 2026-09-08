# 83 — C'est le corpus, et non la boîte, qui plafonne la mesure

> ⚠⚠⚠ **Sur 1296 placements de boîte, le meilleur plafond du fragment vaut 8. Le prix en demande
> 31.** [`82`](82_la_borne_etait_le_mur.md) a établi que toutes les portées publiées sont censurées
> par un plafond de six. Ce document pose la question suivante, et elle est gratuite : en déplaçant
> la boîte sur le même fragment, ce plafond se desserre-t-il ?

![existe-t-il une boîte où la portée cesse d'être censurée](images/83_ou_poser_la_boite.png)

## 1. Ce qui est balayé, et ce qui ne l'est pas

Le **plafond du corpus** est le nombre de bras qu'un marcheur *parfait* parcourrait avant que les
spires publiées lui demandent un saut qu'aucun membre de la famille ne sait faire — le décalage
atteignable vaut une demi-feuille, 67,8 µm. Au-delà, toute portée mesurée est censurée.

⭐⭐ **Ce balayage ne fait tourner aucun marcheur.** Il ne regarde que ce que les spires publiées se
demandent les unes aux autres, donc la boîte se choisit sur le **corpus** et jamais sur le résultat.
Choisir celle où la marche est belle serait choisir l'endroit où le verdict arrange, ce que ce dépôt
refuse partout ailleurs ; choisir celle où le corpus est mesurable est le contraire — c'est retirer
une limite d'instrument, pas fabriquer un résultat.

## 2. ⛔ Le fragment est mauvais partout, pas bon ailleurs

| plafond atteint | 0 | 1 | 2 | 3 | 4 | 5 | **6** | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| placements | **597** | 217 | 101 | 44 | 110 | 50 | **161** | 11 | 5 |

597 des 1296 placements n'offrent même pas un bras. La boîte actuelle atteint **6**, et seules
**16** font mieux. Le meilleur du fragment entier vaut **8** — en posant la boîte en
`8655 10820 21924` au lieu de `10615 10571 19831`, avec douze spires présentes au lieu de dix.

★★ **Ce que ça achète quand même : +2 bras, sans changer d'objet.** Ce n'est pas une marche
meilleure, c'est une **mesure capable de juger deux bras plus loin** — et un marcheur peut
parfaitement échouer au deuxième bras d'une chaîne qui en offre huit, ce qu'un plafond à six
interdisait d'observer.

## 3. ⚠⚠⚠ Le maximum dépend du treillis, donc il est publié comme un minorant

| pas du treillis | boîtes | meilleur plafond |
|---:|---:|---:|
| 480 | 144 | **7** |
| 240 | 1152 | **8** |

Un treillis plus grossier ne peut que **rater** un bon placement, jamais en inventer un : le sens de
l'erreur est donc connu, et **8 est un minorant**. Publier un seul pas aurait fait lire une limite
de treillis comme une limite de fragment — le péché exact que [`82`](82_la_borne_etait_le_mur.md)
vient d'auditer.

⚠ **Et ce piège s'est refermé une fois pendant l'écriture** : `--pas` prenait un scalaire avec son
propre défaut, donc le balayage de treillis — la raison d'être de la fonction — **n'était atteignable
par aucune ligne de commande**, et le premier run publié annonçait un minorant qu'il n'avait pas
mesuré. Le défaut de la ligne de commande est désormais **lu sur la fonction**, et un contrôle le
vérifie.

## 4. ⚠⚠ Le corpus échoue dans les DEUX sens

Sur les **8589** bras de tous les placements, **3395 sont hors du pas nominal — 40 %**.

| | |
|---|---:|
| **trop loin** (un trou de numérotation) | **2226** |
| **trop près** (deux spires que la boîte ne sépare pas) | **1169** |

Les confondre sous un seul mot perdrait ce qui distingue une **lacune** d'un **doublon** : la
première demande un saut qu'aucun marcheur ne franchit, la seconde veut dire que deux surfaces
publiées comme voisines sont, là, la même feuille.

## 5. ⭐⭐⭐ La même paire de spires ne demande pas la même chose partout

Sur les **12 paires de rangs voisins** vues dans plusieurs boîtes, l'écart médian varie d'un
facteur **2,6 à 63,1**, et **huit d'entre elles de plus de dix** :

| paire | boîtes | écart médian, du plus petit au plus grand | rapport |
|---|---:|---|---:|
| `10→11` | 543 | 19,4 → **1224,8 µm** | **×63,1** |
| `8→9` | 938 | 56,2 → 1251,0 µm | ×22,3 |
| `4→5` | 842 | 82,7 → 1560,9 µm | ×18,9 |
| `5→6` | 860 | 70,4 → 1301,4 µm | ×18,5 |
| `12→13` | 943 | 23,5 → 362,6 µm | ×15,4 |
| … | | | |
| `7→8` | 990 | 66,0 → 248,4 µm | ×3,8 |
| `2→3` | 149 | 123,9 → 319,0 µm | **×2,6** |

« Les spires publiées sont des feuilles voisines » est donc vrai **localement** et faux comme
énoncé sur le fragment : à 19 µm deux spires sont la même feuille, à 1225 µm elles sont à neuf
feuilles l'une de l'autre.

⚠⚠⚠ **J'avais d'abord écrit « aucune paire ne varie de moins d'un facteur dix », et c'est ma
propre batterie qui l'a démenti** en une exécution. Deux fautes dans la même phrase : `2→3` varie
de ×2,6, et le compte mélangeait les paires à **saut de rang** — `5→7` n'existe que dans les boîtes
où la spire 6 est trop pauvre, donc son étendue décrit une population de boîtes et non l'écart
entre deux feuilles voisines. La mesure publie désormais un drapeau `consecutif`, et le contrôle
asserte ce qu'elle dit plutôt que ce que j'aurais voulu.

⚠ **Ce que cette mesure ne sépare PAS**, et il faut le dire : un bras n'existe que si les **deux**
spires ont au moins trente cellules dans la boîte, donc l'explication « la spire cible n'est pas là »
est largement écartée — mais trente cellules est un seuil bas, et une spire qui n'effleure qu'un
coin de la boîte peut légitimement faire monter la médiane. Distinguer « les feuilles sont vraiment
plus écartées ici » de « la surface publiée s'arrête ici » demanderait une mesure de couverture, qui
n'est pas celle-ci.

## 6. Ce que ça change

⭐⭐ **Le plafond n'est pas un défaut de placement.** Aucun des 1296 placements ne dépasse 8, alors
que douze spires sont présentes dans les meilleurs : ce n'est pas la boîte qui manque de matière,
c'est le corpus qui ne présente pas une spirale au pas nominal.

⚠ Et ça recoupe [`81`](81_le_rouleau_designe_ne_publie_rien.md) par un troisième chemin : le corpus
de `PHerc0500P2` borne ce qu'on peut **prouver** (13 spires publiées), ce qu'on peut **apprendre**
(portée censurée à 6), et maintenant ce qu'on peut **atteindre en le déplaçant** (8 au mieux). Les
31 spires du prix ne sont pas au bout de ce fragment, quel que soit l'endroit où l'on regarde.

> ⚠ **Le déplacement de la boîte, lui, est disponible et n'engage rien** : il ne change pas d'objet,
> ne recalibre rien, et rendrait deux bras de dynamique à toutes les comparaisons de marcheurs. Le
> faire ou non appartient à l'auteur ; ce document lui donne le centre et le chiffre.

## Reproduire

```
uv run python src/nappe/ou_poser_la_boite.py --verifier
uv run python src/nappe/ou_poser_la_boite.py --cote 960 \
    --json docs/mesures/ou_poser_la_boite.json
uv run python src/figures/figure_ou_poser_la_boite.py --verifier
```
