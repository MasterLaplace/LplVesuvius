# 84 — La vérité de terrain du goulot existe sur un objet, et un seul

> ⚠⚠⚠ **Une surface publiée qui ne couvre qu'UNE spire ne contient aucun transfert de spire à
> spire : elle donne la réponse en morceaux déjà séparés. `PHercParis4` publie ses 120 spires en
> 28 bandes — soit 92 franchissements contenus dans une seule maille. Les cinq autres objets du
> corpus publient une spire par surface, sans exception, donc zéro.**

Ce document est la vérification que [`81`](81_le_rouleau_designe_ne_publie_rien.md) avait nommée
comme restante — *les 120 spires de `PHercParis4` sont-elles voisines dans la matière, ou seulement
par leur nom ?* — et elle a rendu, **avant tout téléchargement**, quelque chose de plus important
que la question posée.

![combien de spires une seule surface traverse-t-elle](../images/84_une_surface_combien_de_spires.png)

## 1. Pourquoi ce compte-là est celui du goulot

L'objectif est de dérouler **automatiquement**, et son goulot est le **transfert de spire à
spire** — ce que l'état de l'art paie ~25 h d'humain par spire, ~775 h pour 31 spires.

⭐⭐ **Un franchissement contenu dans une seule maille est donc une vérité de terrain du goulot.**
Une surface d'une seule spire n'en contient aucun, quel que soit le nombre de surfaces publiées :
elle dit *où sont les feuilles*, jamais *comment on passe de l'une à l'autre*. Une surface qui en
couvre dix-huit contient **dix-sept** de ces passages, faits à la main et publiés.

## 2. Le compte, par objet

| objet | bandes | spires couvertes | spires/surface | la plus longue | **franchissements dans une maille** |
|---|---:|---:|---:|---:|---:|
| **`PHercParis4`** | 28 | 120 | **4,29** | **18** | **92** |
| `PHerc0172` | 44 | 44 | 1,0 | 1 | **0** |
| `PHerc0139` | 37 | 37 | 1,0 | 1 | **0** |
| `PHerc1667` | 19 | 19 | 1,0 | 1 | **0** |
| `PHerc0500P2` | 13 | 13 | 1,0 | 1 | **0** |
| `PHercMANBp` | 9 | 9 | 1,0 | 1 | **0** |

⚠ L'identité qui rend le compte lisible et vérifiable : *franchissements = spires couvertes −
bandes*. Un contrôle l'asserte sur chaque ligne, donc le 92 n'est pas un chiffre à part mais une
conséquence des deux autres.

⚠ **Deux révisions d'une même bande ne font pas deux bandes.** `PHercParis4` publie **58** segments
pour ses 28 bandes ; les compter deux fois doublerait le corpus sans qu'une seule spire de plus
soit publiée.

⚠ Et **aucun des treize rouleaux du Grand Prize n'apparaît dans ce tableau**, parce qu'aucun ne
publie une seule bande — le recoupement de `81` par un chemin de plus.

## 3. ⭐⭐ La longueur des bandes décroît sans une seule inversion

```
18 10 8 7 6 5 5 4 4 4 4 4 3 3 3 3 3 3 3 3 3 2 2 2 2 2 2 2
```

**Zéro remontée sur 28 bandes.** Ce n'est pas une tendance, c'est une **monotonie** — et une
monotonie se réfute d'une seule inversion, donc elle se mesure plutôt qu'elle ne s'affirme. Les
bandes **pavent** l'intervalle `w010..w129` **sans un trou**, ce qui est asserté à part : douze
bandes peuvent couvrir douze spires en sautant des rangs, et le compte de spires couvertes ne le
dirait pas.

⭐ Une bande est ce qu'une passe humaine a produit **d'un coup**. Cette suite est donc la **courbe
de coût du déroulage manuel**, lue sans rien mesurer soi-même.

⚠ **Ce que la suite ne dit PAS : dans quel sens va le rang.** La circonférence croît vers
l'extérieur, donc une passe d'effort constant y couvrirait moins de spires — ce qui expliquerait la
décroissance — mais rien ici ne l'établit, et l'écrire comme un fait serait une **lecture**, pas une
mesure. Le trancher demande un rayon, donc un `tifxyz` ; le moins cher publié est à 45,532 µm.

## 4. ⚠⚠⚠ Et même la meilleure bande reste sous le compte du prix

**18 spires contre 31.** Le corpus le plus riche du concours ne contient donc **pas une marche
entière** : il contient dix-sept franchissements d'affilée, puis il faut **recoudre 28 bandes**, ce
qui est le même problème une spire plus loin.

⭐⭐ C'est la première fois que ce dépôt peut situer sa propre grandeur — la **portée** — contre du
travail humain publié plutôt que contre une borne censurée par le corpus
([`82`](82_la_borne_etait_le_mur.md)). Une portée de 18 égalerait la meilleure passe humaine
publiée ; une portée de 31 la dépasserait de 72 %.

## 5. ⚠⚠ Une faute de lecture qui a effacé un objet en silence

Ma première version exigeait que le nom d'un segment **commence** par sa bande, pour écarter un
`w4` glissé dans un commentaire de révision. Elle a fait disparaître **`PHerc0500P2`**, dont les
surfaces s'appellent `0500P2-wrap01_0919` — l'objet courant du dépôt, absent du tableau sans qu'une
ligne le signale.

C'est le contrôle « l'objet courant publie une spire par surface » qui l'a dit, **en levant sur une
clef absente**. Deux corrections en sont sorties :

1. la bande est lue par le **lecteur partagé** de `les_spires_consecutives_publiees`, qui porte
   déjà la règle et ses sondes — deux lecteurs d'une même convention de nommage finiraient par ne
   pas s'accorder sur ce qu'est une bande ;
2. ⭐ **un objet manquant est désormais un échec NOMMÉ, pas une exception.** Une batterie qui lève
   ne dit pas combien de contrôles ont tourné : tous ceux qui suivaient le point de crash n'ont pas
   eu lieu, et le compte ne le disait pas.

## Reproduire

```
uv run python src/depot/une_surface_combien_de_spires.py
uv run python src/depot/une_surface_combien_de_spires.py --verifier
uv run python src/depot/une_surface_combien_de_spires.py \
    --json docs/mesures/une_surface_combien_de_spires.json
uv run python src/figures/figure_une_surface_combien_de_spires.py --verifier
```
