# 86 — Le critère de marche perdue est au percentile 27 de son propre objet

> ⭐⭐⭐ **Ce dépôt dérive sa demi-feuille — 67,75 µm, le critère qui déclare une marche perdue —
> de 135,5 µm mesurés sur douze paires des treize spires publiées de `PHerc0500P2`. L'atlas de
> `winding-ruler` mesure 196,6 µm de médiane sur le MÊME fragment, p25 = 131,1 µm. Notre chiffre
> tombe donc au percentile 27 : la marche est jugée dans la moitié la plus serrée de la matière,
> et les portées publiées sont des BORNES BASSES.**

[`85`](85_le_sens_du_rang.md) conclut que le maillage à 45,532 µm ne peut pas donner le pas
inter-feuilles, et que la demi-feuille de `PHercParis4` **reste un chiffre à mesurer ailleurs**.
Elle était mesurée, à côté, dans un clone de l'arbre :
`data/repos/winding-ruler/results/atlas_collection_v2.csv` publie la période inter-spires de
**36 objets** — les treize du prix, le témoin, l'objet courant et le candidat.

⚠ C'est la **sixième fois** que « chercher dehors ce qu'on croit absent » paie dans ce dépôt, et
[`67`](67_audit_des_outils.md) §1 l'avait déjà écrit pour ce fichier précis.

![la demi-feuille, objet par objet](../images/86_la_demi_feuille_par_objet.png)

## 1. La confrontation, et ce qu'elle n'est pas

| | valeur | population |
|---|---:|---|
| ce dépôt (`les_wraps_publies`) | **135,5 µm** | 12 paires consécutives des 13 spires publiées, maillages à 2,215 µm |
| l'atlas (`winding-ruler`) | **196,6 µm** (p25 131,1 · p75 337,0) | 16 coupes × 812 rayons du fragment entier, prédictions de surface au niveau 1 |
| rapport | **×1,45** | |
| **percentile de notre chiffre** | **27** | |

⚠⚠ **Ce ne sont pas deux mesures contradictoires, et la différence est de population.** Les deux
nomment la même grandeur — la distance d'une surface de feuille à la suivante — mais l'une porte
sur douze paires d'une région et l'autre sur le fragment entier. Le lire comme une contradiction
serait la faute ; le lire comme un **échantillon** est le résultat.

⚠⚠ **Et les chaînes d'instrument diffèrent, ce qui borne la confiance dans un sens connu** :
l'atlas lit des **prédictions** de surface le long de rayons, et une prédiction qui fusionne deux
feuilles voisines **saute** un écart et en rapporte un double — donc l'atlas **surestime** plutôt
qu'il ne sous-estime. Notre chiffre vient de surfaces publiées, donc plus direct, mais local.

## 2. ⭐⭐⭐ La conséquence sur tout l'appareil de marche

Un critère dérivé du quartile le plus **serré** est plus exigeant que l'objet. Donc les portées
que ce dépôt publie — **4** pour le pas normal, **5** avec la nappe lissée, **6** pour la borne —
sont des **bornes basses**, pas des plafonds. Le même marcheur jugé à la demi-feuille médiane du
fragment (98,3 µm au lieu de 67,75) disposerait de **45 % de tolérance en plus**.

⚠ Ce qui ne change pas : **c'est le bon endroit pour juger.** La marche marche là où les spires
sont publiées, et c'est là que le critère doit valoir. L'atlas ne corrige pas notre chiffre, il
dit **quelle partie de l'objet** il décrit — ce que nous ne savions pas.

## 3. ⭐⭐ Le prix du changement d'objet, que `85` disait non chiffré

| | demi-feuille |
|---|---:|
| `PHerc0500P2` (objet courant, local) | **67,75 µm** |
| `PHercParis4` (candidat, médiane atlas) | **91,20 µm** |
| | **+34,6 % de tolérance** |

⚠ Les deux ne sont pas commensurables terme à terme — le premier est local, le second est une
médiane de fragment. La comparaison honnête à médiane contre médiane est **98,3 → 91,2 µm**, soit
`PHercParis4` **7 % plus serré**. ⭐ Les deux lectures sont dans la mesure ; celle qui compte
dépend de la région où la marche marchera, et cette région n'existe pas encore pour le candidat.

## 4. ■ Mais comme critère de choix de rouleau, il ne choisit pas

| | demi-feuille |
|---|---|
| les treize du prix | **86,4 à 103,7 µm** — un facteur **1,20** |
| l'atlas entier (36) | jusqu'à un facteur **1,71** |

⭐ **L'étroitesse est donc celle des treize et non celle de la mesure.** La géométrie ne sépare pas
mieux que la part comprimée de [`33`](33_incertitude_de_la_carte.md) — et elle est *déjà* mesurée,
donc contrairement à la part comprimée elle ne coûte rien à essayer. Les deux réponses
concordent : **rien dans les treize ne désigne un rouleau.**

## 5. ⚠⚠ Une faute à moi, corrigée par une sonde

Ma première version rendait un **mot** — « au premier quartile » — en tolérant **5 % autour de
p25**. Ce 5 % était un **seuil choisi pour que le chiffre du jour passe**, soit le piège numéro un
de ce dépôt : une sonde qui le retirait faisait basculer le verdict en « entre le quartile et la
médiane ».

⭐ Remplacé par un **percentile**, qui n'a aucun seuil et rend un nombre. L'interpolation est
linéaire entre les trois quantiles publiés et **ne prétend pas plus** : hors des bornes elle
**borne** au lieu d'extrapoler sur une queue que personne n'a mesurée.

⚠ Et un second défaut, dans ma garde de figure : le glyphe `⛔` sortait **en carré** dans la ligne
du panneau A qui porte le verdict, parce que `prose_tracable` ne lit que la prose du bas. Une garde
qui ne voit qu'une partie de ce qu'elle garde est un **angle mort**. Corrigé par
`figure_commune.Tracee`, un calque qui **retient tout le texte dessiné** — posé dans le module
commun parce que le dépôt compte plus de cent figures et que l'angle mort y est le même.

## Reproduire

```
git clone https://github.com/pscamillo/winding-ruler data/repos/winding-ruler
uv run python src/nappe/la_demi_feuille_par_objet.py
uv run python src/nappe/la_demi_feuille_par_objet.py --verifier
uv run python src/nappe/la_demi_feuille_par_objet.py \
    --json docs/mesures/la_demi_feuille_par_objet.json
uv run python src/figures/figure_la_demi_feuille_par_objet.py --verifier
```
