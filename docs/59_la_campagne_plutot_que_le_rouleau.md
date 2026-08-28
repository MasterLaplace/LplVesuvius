# 59 — La campagne de scan : une piste qui s'est effondrée en deux temps

> ⚠⚠ **Suite directe de [`58`](58_resolution_ou_rouleau.md), et RÉFUTATION de sa propre
> première version.** La résolution éliminée, il ne restait qu'une cause à l'inertie du
> modèle d'encre : *ce rouleau-ci*. Ce document a d'abord cru la remplacer par la **campagne
> de scan** — et deux corrections plus tard, la piste ne tient pas. Ce qui reste vaut quand
> même la lecture : ce sont **deux façons de mesurer le mauvais objet**, la seconde n'ayant
> été trouvée que parce que l'auteur a demandé ce qu'il y avait dans `data/encre/`.

## 1. Ce que les noms de volumes portaient sans que personne les lise ensemble

Le dépôt public nomme ses volumes `<scan>-<voxel>um-<distance>m-<énergie>keV-masked.zarr`.
Trois grandeurs, dans chaque nom, jamais rassemblées. Le lecteur existait déjà à moitié —
`src/volume/apparier_volumes.py` lisait le voxel — et il lit désormais les trois. ⚠ **Un
seul lecteur**, et c'est délibéré : deux finiraient par ne pas s'accorder sur un nom
inhabituel, et on comparerait deux campagnes en croyant comparer deux rouleaux.

Ce que ça donne sur les six rouleaux qui ont motivé la mesure :

| rouleau | volumes | énergies | verdict du modèle |
|---|---:|---|---|
| `PHercParis4` | 5 | 74, 78, 78, 110, 137 keV | **marche** (AUC 0,925) |
| `PHerc0172` | 2 | 53, 53 | encre publiée |
| `PHerc1667` | 2 | 59, 78 | encre publiée |
| `PHerc0139` | 7 | 59, 77×4, 78, 113 | encre publiée |
| `PHerc1447` | **1** | **116** | ~~**inerte** (σ = 0,0171)~~ ⚠ **σ = 0,6558**, cf. ci-dessous |
| `PHerc0358` | **1** | **113** | — |

⭐ Ce n'est pas d'abord une histoire d'énergie : c'est le **nombre de campagnes**. Les
rouleaux dont l'encre se lit ont tous été rescannés **fin et en propagation courte**
(1,1 à 2,4 µm, 0,2 m) ; les deux où le modèle est inerte n'ont que le scan de **repérage**
(8,6 à 9,4 µm, 1,2 m, 113 à 116 keV).

### ⚠⚠⚠ Deux corrections du 2026-08-28, et la seconde touche l'inférence ci-dessus

**1. `PHerc1447` n'est plus « inerte ».**
[`60`](60_la_constante_qui_rendait_le_modele_muet.md) a montré que le σ de 0,0171 mesurait une
constante de normalisation de notre côté, pas le rouleau. À l'échelle corrigée il vaut
**0,6558**, soit **1,2×** le témoin — le même régime. La colonne « verdict du modèle » de ce
tableau portait donc, pour l'un de ses six rouleaux, un fait sur **nous**.

**2. ⚠⚠ Le relevé n'énumère pas le volume où le modèle marche.**
`campagnes_de_scan.py` interroge le bucket **open-data** (`*-masked.zarr`, acquisitions 2025
et 2026). Pour `PHercParis4` il trouve bien cinq volumes — 45,5 µm à 74 et 110 keV, puis
2,4 et 1,1 µm à 137 et 78 keV. **Aucun n'est celui du résultat de référence.** Le segment où
le modèle atteint AUC 0,925 est `20230909121925`, dans le volume **`20230205180739`** :
un scan **de 2023**, **7,91 µm**, **54 keV**, qui vit dans l'ancien layout
`full-scrolls/Scroll1/PHercParis4.volpkg/` — lequel ne contient que **deux** volumes, les
deux moitiés recousues du même scan à 54 keV (vérifié à la source le 2026-08-28).

⚠⚠⚠ **Conséquence sur l'inférence.** La phrase ci-dessus dit que les rouleaux lisibles ont
été « rescannés fin et en propagation courte », et invite à y voir la cause. Or **la lecture
de référence n'a pas été faite sur un rescan fin** : elle a été faite sur un scan grossier de
7,91 µm, c'est-à-dire à **9 %** du pas de `PHerc1447` ([`58`](58_resolution_ou_rouleau.md) §7).
Le rescan fin existe sur ce rouleau, mais il n'est pas ce qui a produit le résultat qu'on
cherche à expliquer.

⭐ Ce document avait déjà rétrogradé sa propre conclusion le jour même (p = 0,50 sur les
rouleaux réellement tentés). Cette correction-ci retire ce qui en restait comme intuition :
*le rescan fin n'explique pas la lisibilité, puisque la lisibilité a été obtenue sans lui.*

⚠ Et une limite de l'instrument, à connaître : `campagnes_de_scan.py` ne voit qu'un des deux
layouts du dépôt public. Les rouleaux scannés avant la campagne open-data ont des volumes
qu'il ne compte pas, donc son `n_volumes` est un **minorant** pour eux.

## 2. ⚠⚠ La première version de cette mesure était un fait sur NOUS

`data/encre/<rouleau>/` contient quatre rouleaux, et il était tentant d'en faire le groupe
« lisible ». C'est faux : ce dossier contient ce que
[`fetch_cartes_encre.sh`](../src/outils/fetch_cartes_encre.sh) a **téléchargé**, un rouleau
à la fois, sur demande. Un rouleau absent peut n'avoir jamais été demandé.

⭐ La bonne question s'adresse au dépôt : **publie-t-il une détection d'encre pour ce
rouleau ?** `src/encre/campagnes_de_scan.py --sonder-encre 5` sonde cinq segments par
rouleau et regarde si l'un d'eux porte un dossier `ink-detection/`. Les deux critères sont
gardés côte à côte dans le rapport et **ne sont jamais mélangés** — le champ `critere` dit
lequel a décidé.

⚠ Le sondage porte sur **cinq segments**, pas sur tous : un rouleau en publie des dizaines
et la réponse coûte une requête chacun. C'est donc une **borne inférieure** sur le groupe
positif, et le compte sondé est rendu à côté du compte trouvé — zéro sur cinq et zéro sur
cinquante ne disent pas la même chose.

## 3. Le partage à deux groupes — et pourquoi il ne veut rien dire

| | rouleaux | avec un scan fin à courte propagation | énergies | volumes (médiane) |
|---|---:|---:|---|---:|
| le dépôt publie une détection d'encre | 7 | 6 (86 %) | 53–111 keV | 3 |
| il n'en publie pas | 38 | 11 (29 %) | 59–116 keV | 1 |

Fisher exact unilatéral sur `[6, 1, 11, 27]` : **p = 0,0081**. Écrit tel quel, ça se lit
comme un résultat.

## 3 bis. ⚠⚠ Il y a TROIS états, pas deux, et le troisième mange le résultat

**« Le dépôt ne publie pas d'encre pour ce rouleau » recouvre deux faits sans rapport** :
un rouleau qu'on a tracé sans y lire d'encre, et un rouleau que **personne n'a jamais
tracé**. Le second ne dit rien sur son encre — il dit que la question n'a pas été posée.

| état | rouleaux | avec un scan fin |
|---|---:|---:|
| **aucun segment publié** — personne n'a tracé | **31** | 6 (19 %) |
| tracé, sans encre publiée | 7 | 5 (**71 %**) |
| encre publiée | 7 | 6 (**86 %**) |

⭐⭐ **Trente-et-un des trente-huit du groupe « pas d'encre » n'ont jamais été tracés.** Le
scan fin ne suit donc pas la lisibilité : il suit **l'attention** que la communauté a portée
à un rouleau, ce qui est exactement ce qu'on attend — on rescanne finement ce sur quoi on
travaille.

⭐⭐⭐ **La comparaison qui vaut** est restreinte aux rouleaux qu'on a **tentés** :
7 avec encre contre 7 tracés sans encre, `[6, 1, 5, 2]`, **86 % contre 71 %** —
**p = 0,5000**. Il n'y a **aucune séparation**.

> ⚠⚠ **La campagne de scan n'est donc pas établie comme le discriminant.** La première
> version de ce document l'annonçait ; elle mesurait « sur quoi la communauté a travaillé »
> en croyant mesurer « où l'encre se lit ».

## 4. Ce que ça n'établit pas, et il faut le dire à chaque usage

1. **« Le dépôt publie une carte » n'est pas « le modèle de 2023 y répond ».** C'est la trace
   de ce que quelqu'un a jugé lisible et a pris la peine de rendre.
2. **Les trois grandeurs co-varient par campagne.** Un scan fin est aussi à courte
   propagation et à basse énergie. Aucune des trois n'est isolée par cette mesure — c'est le
   même défaut que `58` §1 a corrigé sur la résolution, et il faudra le même genre de
   dégradation contrôlée pour les séparer.
3. ⚠⚠ **L'ordre de causalité n'est pas donné, et le §3 bis montre qu'il est probablement
   inverse.** C'était la troisième mise en garde de la première version, écrite et **laissée
   à côté du chiffre au lieu d'être retirée du chiffre** : la mesure la contenait, et il a
   fallu séparer les trois états pour qu'elle cesse d'être une note et devienne le résultat.
   Un test qui trancherait vraiment : prendre un rouleau rescanné et lui redemander son
   ancien scan de repérage seul. C'est exactement la forme de `58` — rendre l'objet qui
   marche semblable à celui qui ne marche pas, une propriété à la fois.

## 5. Ce qui survit

**La piste de la campagne ne survit pas** : à corpus restreint aux rouleaux tentés, p = 0,50.
« Ce rouleau-ci » n'est donc **pas** remplacé, et reste la seule cause en lice.

Ce qui survit, et qui n'est pas rien :

1. ⭐ **Trente-et-un rouleaux sur quarante-cinq n'ont aucun segment publié.** La prémisse du
   prix, chiffrée : le corpus n'est pas *difficile*, il est en grande partie **non tenté**.
2. ⭐⭐ **Aucun des treize rouleaux du prix ne publie de détection d'encre** — et dix des
   treize n'ont **aucun segment publié du tout**. Trois seulement ont été tracés
   (`PHerc0800`, `PHerc1203`, `PHerc1447`) et aucun n'a rendu d'encre.
3. ⭐ **Le cadre à trois états**, et la preuve qu'un cadre à deux est un piège : le même
   corpus rend p = 0,0081 ou p = 0,50 selon qu'on range « jamais tracé » avec « pas d'encre »
   ou à part.

⚠ Et un test resterait valable si on obtenait la donnée : un second scan de `PHerc1447`, fin
et à courte propagation, ou le scan de repérage seul d'un rouleau qu'on sait lire. ~~Il
faudrait de toute façon séparer les trois grandeurs de la campagne — pas, distance, énergie —
qu'aucun rouleau du corpus ne fait varier indépendamment.~~

> ⚠⚠⚠ **ET LE DISCRIMINANT QUE CE DOCUMENT RÉCLAME N'EST PAS CHERCHABLE ICI — établi par
> énumération le 2026-08-28**, pas par un échec à le trouver.
> [`src/encre/ou_la_verite_existe.py`](../src/encre/ou_la_verite_existe.py) relit les deux
> dépôts et range chaque objet en trois états :
>
> | statut | ce que ça veut dire | combien |
> |---|---|---:|
> | `mesurable` | étiquettes publiées, modèle **pas** entraîné dessus | **4 fragments** |
> | `entraine_dessus` | étiquettes, mais c'est le jeu d'entraînement → mesurer n'y prouve rien | 1 (`Scroll1`) |
> | `sans_verite` | **aucune étiquette publiée** | 4 rouleaux, 2 fragments |
>
> ⭐⭐⭐ **Zéro rouleau mesurable.** Chercher « ce qui sépare un rouleau où le modèle lit d'un
> rouleau où il ne lit pas » suppose de mesurer la lecture **des deux côtés** — et elle n'est
> mesurable d'**aucun** côté rouleau. Ce n'est pas une recherche qui a échoué, c'est une
> propriété du corpus publié.
>
> ⚠⚠ Trois états et non deux, et c'est ce qui empêche une fausse issue : `Scroll1` **a** des
> étiquettes, et publier des étiquettes de plus dessus ne débloquerait rien, puisque c'est
> précisément ce sur quoi le modèle a été entraîné. Fondre `entraine_dessus` dans
> `sans_verite` ferait croire le contraire.
>
> ⚠ Et le motif de recherche **exclut les sorties de modèle** : `PHerc0172` publie quatre
> fichiers `ink-detection/…timesformer_scroll5….tif`, qui sont des **prédictions**. Les
> compter comme vérité ferait mesurer un modèle contre un autre modèle — un chiffre élevé et
> vide de sens. Asséré dans les deux sens.
>
> **Ce que ça N'établit PAS** : que le modèle ne lise pas sur un rouleau. Seulement qu'on ne
> peut pas le mesurer. Relevé : [`ou_la_verite_existe.json`](mesures/ou_la_verite_existe.json).

> ⭐⭐⭐ **LA DERNIÈRE PHRASE EST FAUSSE, mesuré le 2026-08-28.** « Aucun rouleau du corpus »
> était vrai des rouleaux et **faux du corpus** : les six **fragments** du layout
> `fragments/` — celui-là même que le relevé de ce document n'interroge pas — font varier les
> grandeurs **indépendamment**, et il y en a neuf paires.
>
> | | volumes | ce que la paire isole |
> |---|---|---|
> | `Frag1` à `Frag4` | 54 et 88 keV, **tous deux à 3,24 µm** | **l'énergie**, résolution tenue |
> | `Frag5` | 70 keV, **3,24 et 7,91 µm** | la résolution, énergie tenue |
> | `Frag6` | 53, 70, 88 keV à 3,24 µm **+** 53 keV à 7,91 µm | **trois** paires d'énergie, une de résolution |
>
> **7 paires isolent l'énergie, 2 la résolution**, et ces fragments portent en prime une
> **vérité terrain d'encre** publiée. Le test que cette phrase déclarait hors de portée est
> donc à portée, et il ne demande aucune donnée nouvelle du côté de l'acquisition — seulement
> de télécharger ce qui est déjà en ligne. Détail :
> [`58`](58_resolution_ou_rouleau.md) §8 quater, relevé
> [`docs/mesures/paires_denergie.json`](mesures/paires_denergie.json).
>
> ⚠ C'est le **deuxième** effet de l'angle mort de `campagnes_de_scan.py` sur ce document : le
> premier lui faisait argumenter depuis une liste sans le volume qui marche (§1), le second
> lui faisait déclarer impossible un test que l'autre layout rend possible. Une mesure qui ne
> voit qu'une moitié du dépôt produit des conclusions justes **sur cette moitié**, et il faut
> le dire à chaque fois qu'on s'en sert.

## Reproduire

```bash
# le relevé (le seul mode qui touche au réseau)
uv run python src/encre/campagnes_de_scan.py --lister --sonder-encre 5 \
    --json docs/mesures/campagnes_de_scan.json

# re-dériver hors ligne depuis le relevé
uv run python src/encre/campagnes_de_scan.py --depuis docs/mesures/campagnes_de_scan.json
```
