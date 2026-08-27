# 59 — « Ce rouleau-ci » est un mot ; la campagne de scan est une propriété

> ⚠⚠ **Suite directe de [`58`](58_resolution_ou_rouleau.md).** La résolution éliminée, il ne
> restait qu'une cause à l'inertie du modèle d'encre : *ce rouleau-ci*. C'est un mot qui ne
> nomme rien, ne se teste pas, et ne s'achète pas. Ce document le remplace par une propriété
> qui a les trois qualités inverses.

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
| `PHerc1447` | **1** | **116** | **inerte** (σ = 0,0171) |
| `PHerc0358` | **1** | **113** | — |

⭐ Ce n'est pas d'abord une histoire d'énergie : c'est le **nombre de campagnes**. Les
rouleaux dont l'encre se lit ont tous été rescannés **fin et en propagation courte**
(1,1 à 2,4 µm, 0,2 m) ; les deux où le modèle est inerte n'ont que le scan de **repérage**
(8,6 à 9,4 µm, 1,2 m, 113 à 116 keV).

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

## 3. ⭐⭐ Le partage, sur les 45 rouleaux du dépôt

| | rouleaux | avec un scan fin à courte propagation | énergies | volumes (médiane) |
|---|---:|---:|---|---:|
| **le dépôt publie une détection d'encre** | 7 | **6 (86 %)** | 53–111 keV | **3** |
| **il n'en publie pas** | 38 | **11 (29 %)** | 59–116 keV | **1** |

⭐⭐ **Fisher exact unilatéral sur `[6, 1, 11, 27]` : p = 0,0081.** La direction était
déclarée avant de regarder — un scan fin devrait *aider* — donc le test est unilatéral ; un
test bilatéral aurait aussi salué l'effet inverse, ce qui reviendrait à n'avoir eu aucune
hypothèse.

⚠ Et la médiane de volumes, 3 contre 1, dit la même chose plus crûment : **un rouleau dont
on lit l'encre est un rouleau qu'on a scanné plusieurs fois.**

## 4. Ce que ça n'établit pas, et il faut le dire à chaque usage

1. **« Le dépôt publie une carte » n'est pas « le modèle de 2023 y répond ».** C'est la trace
   de ce que quelqu'un a jugé lisible et a pris la peine de rendre.
2. **Les trois grandeurs co-varient par campagne.** Un scan fin est aussi à courte
   propagation et à basse énergie. Aucune des trois n'est isolée par cette mesure — c'est le
   même défaut que `58` §1 a corrigé sur la résolution, et il faudra le même genre de
   dégradation contrôlée pour les séparer.
3. ⚠⚠ **L'ordre de causalité n'est pas donné, et il pourrait être inverse.** Un rouleau peut
   n'avoir qu'un scan de repérage **parce que** personne n'y a encore lu de texte, plutôt que
   l'inverse. Un test qui trancherait : prendre un rouleau rescanné et lui redemander son
   ancien scan de repérage seul. C'est exactement la forme de `58` — rendre l'objet qui
   marche semblable à celui qui ne marche pas, une propriété à la fois.

## 5. Ce que ça change quand même

« Ce rouleau-ci » ne se teste pas et ne s'achète pas : un rouleau ne change pas. **Une
campagne de scan, si.** Le résultat déplace la question de l'objet vers le protocole, et il
dit ce qu'il faudrait obtenir pour la trancher : un second scan de `PHerc1447`, fin et à
courte propagation, ou le scan de repérage seul d'un rouleau qu'on sait lire.

⚠ ⏳ Reste à séparer les trois grandeurs de la campagne — pas, distance, énergie — entre
elles. Aucun rouleau du corpus ne les fait varier indépendamment, donc c'est encore une
donnée à obtenir, pas un réglage à trouver.

## Reproduire

```bash
# le relevé (le seul mode qui touche au réseau)
uv run python src/encre/campagnes_de_scan.py --lister --sonder-encre 5 \
    --json docs/mesures/campagnes_de_scan.json

# re-dériver hors ligne depuis le relevé
uv run python src/encre/campagnes_de_scan.py --depuis docs/mesures/campagnes_de_scan.json
```
