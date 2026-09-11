# 81 — Le rouleau que la carte désigne ne publie rien contre quoi vérifier

> ⚠⚠⚠ **Onze des treize rouleaux du Grand Prize ne publient aucun segment. Les treize, sans
> exception, ne publient aucun rang de spire.** La feuille de route inscrit au calendrier de
> choisir l'un d'eux par sa part comprimée ; [`combien_de_fenetres`](../../src/commun/combien_de_fenetres.py)
> vient de montrer que ce critère coûte **315 fois** son budget. Ce document répond à la question
> qui le précède, et elle est **gratuite** : sur lequel des treize a-t-on de quoi vérifier quoi
> que ce soit ?

Suite directe de [`33`](33_la_carte_nest_pas_resolue.md), qui a montré que la carte ne sépare
rien, et de la tranche qui a chiffré ce qu'il faudrait pour qu'elle sépare. Celle-ci ne mesure
plus le prix du critère : elle mesure si sa réponse est **exécutable**.

![sur quel objet peut-on vérifier trente et une spires](../images/81_les_spires_consecutives.png)

## 0. La question, ramenée à l'objectif

L'objectif est de dérouler **100 % du recto d'un rouleau automatiquement**, et le goulot est le
**transfert de spire à spire** — ce que l'état de l'art paie ~25 h d'humain par spire, ~775 h
pour les 31 spires de `PHerc1667`. La grandeur que ce dépôt mesure depuis des semaines est la
**portée** : le nombre de spires traversées avant que l'erreur dépasse la demi-feuille.

⭐⭐ **Une portée ne se mesure que jusqu'où le corpus publie des spires consécutives.** Au-delà
du dernier rang publié d'affilée, il n'existe plus rien contre quoi dire qu'on a franchi une
spire de plus. Le corpus n'est donc pas une commodité : c'est **le plafond de ce qu'on peut
prouver**.

⚠ Et c'est une grandeur de l'**objectif**, pas de l'encre. La part comprimée que `16` classe est
une propriété de séparabilité encre/non-encre ; *l'encre est la règle graduée, pas l'ouvrage*.
Choisir un rouleau sur elle, c'est choisir sur ce qu'on saura **lire**, pas sur ce qu'on saura
**dérouler**.

## 1. Ce que l'index publie, mesuré

[`src/depot/les_spires_consecutives_publiees.py`](../../src/depot/les_spires_consecutives_publiees.py)
lit `data/metadata.min.json` — 45 échantillons — et compte, pour chacun, les rangs de spire que
ses segments **nomment**, puis la plus longue suite sans trou.

| objet | segments | rangs publiés | plus longue suite | de..à | porte les 31 ? |
|---|---:|---:|---:|---:|:--:|
| `PHercParis4` | 81 | 120 | **120** | 10..129 | ✅ |
| `PHerc0172` | 53 | 44 | **44** | 52..95 | ✅ |
| `PHerc0139` *(le témoin de la carte)* | 38 | 37 | **37** | 23..59 | ✅ |
| `PHerc1667` *(l'objet des 775 h)* | 20 | 19 | 14 | 28..41 | ⛔ |
| **`PHerc0500P2`** *(l'objet courant)* | 39 | 13 | **13** | 1..13 | ⛔ |
| `PHercMANBp` | 11 | 9 | 9 | 0..8 | ⛔ |
| **les treize rouleaux du prix** | 0 (×11), 6, 15 | **0** | **0** | — | — |

⚠ Les comptes ont été confrontés aux serveurs avec
[`ce_que_les_serveurs_publient`](../../src/depot/ce_que_les_serveurs_publient.py), parce qu'un index
en cache pris pour une autorité est un angle mort que ce dépôt a déjà payé cinq fois. S3 confirme
`PHercParis4` 81, `PHerc0172` 53, `PHerc0500P2` 39, `PHerc0139` 38, et — le point qui décide —
`PHerc0358`, `PHerc0211`, `PHerc0125` **sans dossier `segments/` du tout**. Un seul écart trouvé,
`PHerc1447` : 15 en cache, 16 sur S3, sans effet sur le verdict puisqu'aucun de ses segments ne
porte de rang.

## 2. ⭐⭐⭐ Les deux qui publient quelque chose n'en ordonnent rien

`PHerc0800` (6 segments) et `PHerc1447` (15) ne publient que des `auto_grown_*` : des morceaux
produits automatiquement, **sans rang de spire dans leur nom**. On ne peut donc pas les mettre en
spirale sans les remesurer — et « les remesurer » est exactement le travail qu'un corpus publié
existe pour éviter.

C'est pour ça que le tableau distingue **segments** et **rangs**. Un compte de segments ferait
croire que deux des treize sont exploitables ; le compte de rangs dit que **zéro** l'est.

⚠⚠ Ce que la mesure ne dit **pas** : que les treize soient des rouleaux difficiles. Zéro segment
publié est un fait sur l'**effort de la communauté**, pas sur le papyrus. Mais le prix se gagne en
livrant une image Docker qu'**ils** lancent, sur un résultat vérifiable — et un objet sans vérité
de terrain ne permet ni de développer, ni de prouver. Le fait, quelle qu'en soit la cause, décide
quand même.

## 3. Un compte ne suffit pas : il faut une **suite**

`PHerc1667` est l'objet de l'état de l'art — 31 spires déroulées à la main, 1231 cm², ~775 h. Il
publie **19 rangs sur une étendue de 31** : `w011`, `w012`, `w013`, puis `w018`, puis `w023`, puis
`w028` à `w041`. Douze trous, et sa plus longue suite tombe à **14**.

⚠⚠ **Un trou ne se recolle pas**, et c'est la raison d'être de la colonne « plus longue suite » :
le trou est précisément l'endroit où la marche cesserait d'être vérifiable. Deux tronçons de
sept spires ne témoignent pas d'une marche de quatorze.

## 3 bis. ⚠⚠⚠ Compter des NOMS n'est pas compter des VOISINES — et j'ai failli publier une coïncidence

Une portée est un nombre de **franchissements**, et le marcheur ancre sur la spire la plus basse
de la boîte puis monte : depuis une suite de $N$ spires, il en traverse donc au plus $N-1$.

| objet | suite publiée | portée maximale mesurable |
|---|---:|---:|
| `PHercParis4` | 120 | **119** |
| `PHerc0172` | 44 | 43 |
| `PHerc0139` | 37 | 36 |
| `PHerc0500P2` | 13 | **12** |

⚠⚠⚠ **Et j'ai d'abord cru y avoir recoupé un chiffre déjà publié — c'était faux.**
`la_portee_du_raccrochage` rapporte *« ce que le corpus autorise : 6 »*, et j'ai écrit que ce 6
était $13/2$, la portée d'une ancre centrale. **Vérifié dans la mesure, il ne l'est pas** : l'ancre
n'est pas centrale (c'est la spire la plus basse de la boîte, la 4), les bras montent seulement, et
il y en a **8**. Le 6 vient d'ailleurs, et d'un endroit beaucoup plus instructif :

| bras | de → vers | écart mesuré | au pas nominal ? |
|---:|---|---:|:--:|
| 5 | 8 → 9 | 137,6 µm | ✅ |
| 6 | 9 → 10 | 89,2 µm | ✅ |
| **7** | **10 → 11** | **1000,6 µm** | ⛔ |
| 8 | 11 → 12 | 76,7 µm | ✅ |

⭐⭐⭐ **Les spires 10 et 11 se suivent par leur NUMÉRO et sont à 7,4 feuilles l'une de l'autre dans
la matière.** Le plafond de 6 n'est donc ni la méthode, ni la longueur du corpus : c'est un **trou
géométrique** au milieu d'une numérotation continue.

⚠⚠ **Ce que ça impose au critère de ce document** : compter les rangs publiés est une condition
**nécessaire et non suffisante**. Un corpus de 120 spires numérotées peut porter le même genre de
saut, et le compte des noms ne le verra pas. Vérifier que deux spires voisines par leur nom le sont
dans la matière coûte un téléchargement — c'est exactement ce que
[`les_wraps_publies`](../../src/nappe/les_wraps_publies.py) fait pour `PHerc0500P2`, et ce qui reste à
faire pour tout objet qu'on retiendrait.

⚠ La leçon de méthode, gardée : **un chiffre qui tombe juste n'est pas un recoupement.** Deux
routes qui rendent 6 pour deux raisons sans rapport se lisent comme une confirmation, et c'est la
forme de faux verdict la plus difficile à voir — celle qu'on n'a aucune raison d'aller vérifier.

## 4. ⚠⚠ Une erreur de lecture qui aurait éliminé le meilleur objet du dépôt

Ma première lecture des noms de segments prenait `w046-052` pour un **rang**, en ne gardant que le
premier nombre. Sous cette lecture, `PHercParis4` rendait **28 spires et 91 trous** — un corpus
lacunaire, et le pire du tableau. Il en publie **120 d'affilée, sans un seul trou** : `w010-027`,
`w028-037`, … `w128-129`, des **intervalles** qui pavent la spirale.

⭐ Une lecture qui invente des trous ne se lit pas comme un bug : elle se lit comme un corpus
pauvre. La sonde le mesure — en réduisant les intervalles à leur borne basse, la plus longue suite
de `PHercParis4` tombe de **120 à 1**, parce que les bornes basses ne se touchent même pas.

⚠ Et le faux positif symétrique est gardé par la même batterie :
`auto_grown_20251115002740308_5_flatboi` finit par `_5_`, qui est un **indice de morceau** et non
un rang. Une expression assez lâche pour l'attraper ferait passer une pile de patches pour une
spirale ordonnée — l'inverse exact du service rendu. Sonde : `PHerc1447` et `PHerc0800` sortent
alors du lot des « sans rang », et le verdict change.

## 5. ⚠⚠⚠ Une limite de mon filtre, publiée un instant comme une limite du corpus

Le premier filtre « géométrie » ne retenait que le type `tifxyz`, et rendait
**`PHerc0172` : une seule spire marchable** sur quarante-quatre. Faux : `deux_aplatissements`
avait déjà établi que `tifxyz-transformed` publie **une position 3D par cellule**, donc que la
marche peut le consommer. C'est le péché numéro un de ce dépôt — une limite de grille publiée
comme une limite matérielle — et il est ici gardé par un contrôle nommé.

⚠ `tifxyz-flattened` et `tifxyz-normalized` restent **dehors**, et c'est une décision : aucune
mesure du dépôt n'a établi ce qu'ils portent, et les compter serait affirmer sans avoir regardé.

## 6. Ce que ça change, et ce que ça ne tranche pas

⭐⭐⭐ **La décision de septembre de [`31`](31_roadmap.md) §10 n'est pas seulement hors budget :
sa réponse n'est pas exécutable.** Le classement désigne un objet sur lequel il n'existe ni ancre
pour partir, ni vérité de terrain pour dire jusqu'où on est allé.

⚠⚠ **Et l'objet courant plafonne sous la moitié de ce que le prix demande.** `PHerc0500P2` publie
13 spires consécutives ; le prix en demande 31. Sur lui, tenir 31 spires n'est pas seulement
difficile — c'est **invérifiable**, faute de quoi que ce soit à comparer au-delà de la treizième.
C'est la forme mesurée du facteur 97× déjà nommé, et elle dit que ce facteur ne se réduira pas
par du travail sur cet objet-là.

Trois objets portent les 31 : `PHercParis4` (120), `PHerc0172` (44), `PHerc0139` (37).

⚠ **Le changement d'objet reste une décision de l'auteur.** Ce document lui donne le chiffre, pas
le choix — et il nomme les deux coûts qu'un changement porterait : tout ce qui est calibré sur
`PHerc0500P2` (voxel 2,215 µm, pas nominal 135,5 µm, boîte et ancres) est à re-dériver, et la
demi-feuille de 67,75 µm est une mesure **de cet objet**, donc à remesurer avant d'être réutilisée
comme critère ailleurs.

## Reproduire

```
uv run python src/depot/les_spires_consecutives_publiees.py
uv run python src/depot/les_spires_consecutives_publiees.py --verifier
uv run python src/depot/les_spires_consecutives_publiees.py \
    --json docs/mesures/les_spires_consecutives_publiees.json
uv run python src/figures/figure_les_spires_consecutives.py --verifier
uv run python src/depot/ce_que_les_serveurs_publient.py --fragment PHerc0358
```
