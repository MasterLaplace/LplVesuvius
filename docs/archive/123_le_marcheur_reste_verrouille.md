# 123 — Le marcheur reste verrouillé sur les feuilles, et le naïf dérive

> ⭐⭐⭐⭐ **`119` A MESURÉ OÙ LE MARCHEUR VA ; CELUI-CI MESURE SUR QUELLE FEUILLE IL TOMBE.** Un
> marcheur peut aller parfaitement droit en atterrissant chaque fois un peu trop loin, et c'est
> exactement ce que l'humain corrige d'une spire à l'autre. La question n'est pas mesurable sur le
> vrai volume — on n'y sait pas où sont les feuilles — mais elle l'est **au centième de feuille**
> sur une pile fabriquée.
>
> ⭐⭐⭐⭐ **LE DÉCALAGE NE GRANDIT DANS AUCUNE DES QUATRE CONDITIONS.** Pile propre :
> **0,1249 → 0,1249** (p 1,0). Avec bruit : 0,1270 → 0,1155. À 35° d'obliquité, il **diminue**
> significativement — **0,1620 → 0,1354**, p **0,0137** : le marcheur se **re-verrouille**.
>
> ⭐⭐⭐⭐ **ET L'AVANCE VAUT UNE FEUILLE PAR PAS À 0,7 % PRÈS** dans les quatre conditions
> (1,0037 · 1,0065 · 1,0061 · 1,0067). Sur les **112 pas** qu'une traversée complète demande, ça
> fait moins d'une feuille d'excès cumulé.
>
> ⭐⭐⭐ **LE TÉMOIN, LUI, DÉRIVE** : un pas nominal imposé sur la même pile oblique passe de
> **0,2287 à 0,2713** (p **0,0005**), parce qu'il n'avance que de **0,8192** feuille par pas. Sans
> lui, « le décalage ne grandit pas » serait sans puissance.
>
> ⚠⚠ **Analytique, et ça borne ce que ça dit** : le vrai rouleau n'est pas une pile plane à pas
> constant. Ce qui est établi est une propriété du **mécanisme**, comme `controle_fabrique` établit
> que le naïf échoue dès qu'il y a de l'obliquité.

## 1. Pourquoi ce fichier

`119` a mesuré que la trajectoire n'accumule rien : la rectitude tient et les virages se compensent.
C'est une réponse sur la **direction**. Le transfert de spire à spire échoue autrement : en
atterrissant du mauvais côté d'une feuille. Un marcheur peut aller droit et rater sa cible.

⚠ Et cette question-là ne se pose pas sur le vrai volume, où l'on ne sait pas où sont les feuilles.
Sur une pile analytique, la phase d'un point est sa projection sur la normale divisée par le pas :
**une phase entière veut dire « sur une feuille »**. C'est pour ça que ce document est fabriqué.

## 2. Ce que mesure « le décalage »

Pour chaque atterrissage, l'écart à la feuille la plus proche, en feuilles, dans [−0,5 ; 0,5]. Le
test compare le **premier tiers** d'une marche à son **dernier**, apparié à l'intérieur de la
marche.

⚠⚠ Les douze marches d'une condition partent de **phases différentes**, réparties régulièrement sur
une feuille. Partir toujours d'une feuille mesurerait la réponse à une seule mise en place, et un
décalage acquis au premier pas ressemblerait à une propriété du mécanisme.

⚠ La projection est prise du point **réellement atteint**, pas de la distance parcourue : la marche
s'écarte de la normale, donc `parcouru / pas` surestimerait l'avance d'autant.

## 3. ⭐⭐⭐⭐ Le décalage ne grandit nulle part

| obliquité | bruit | 1ᵉʳ tiers | dernier tiers | p | grandit |
|---:|---:|---:|---:|---:|---|
| 0° | 0 | **0,1249** | **0,1249** | 1,0 | non |
| 0° | 8 | 0,1270 | 0,1155 | 0,7910 | non |
| 35° | 0 | **0,1620** | **0,1354** | **0,0137** | non — il **diminue** |
| 35° | 8 | 0,1253 | 0,1380 | 0,3804 | non |

⭐ La troisième ligne est la plus intéressante : à 35° d'obliquité le marcheur **récupère**. Il
commence plus décalé — l'obliquité rend la première mise en place plus difficile — et il se
rapproche de la feuille à mesure qu'il avance.

⚠ La quatrième ligne monte un peu (0,1253 → 0,1380) sans être significative (p 0,3804) : avec du
bruit ET de l'obliquité, le test **cesse de rejeter** la croissance, il ne l'exclut pas. Douze
marches ne donnent pas la puissance de trancher un écart de 0,013 feuille.

## 4. ⭐⭐⭐⭐ Une feuille par pas, à moins d'un pour cent

| condition | avance médiane par pas |
|---|---:|
| 0°, sans bruit | **1,0037** |
| 0°, bruit 8 | 1,0065 |
| 35°, sans bruit | 1,0061 |
| 35°, bruit 8 | 1,0067 |

Sur les **112 pas** qu'une traversée de 4,07 à 23,8 mm demande (`122`), un excès de 0,67 % fait
**0,75 feuille** cumulée — moins d'une feuille sur toute la largeur du rouleau.

⚠ Et ce n'est **pas** une erreur qui s'accumule : le marcheur relit le profil à chaque pas, donc il
recale sa cible depuis là où il se trouve. C'est ce que la ligne à 35° montre en clair.

## 5. ⭐⭐⭐ Le témoin, qui donne au résultat sa puissance

Un pas **nominal imposé** le long du rayon, sur la même pile inclinée de 35° :

| | 1ᵉʳ tiers | dernier tiers | p |
|---|---:|---:|---:|
| pas nominal imposé | **0,2287** | **0,2713** | **0,0005** |

Il n'avance que de **0,8192** feuille par pas — exactement `cos(35°)`, donc une dérive connue
d'avance, et c'est ce qui en fait un étalon.

⚠⚠ Sans ce témoin, « le décalage ne grandit pas » serait satisfait par un marcheur parfait comme
par un instrument aveugle. Le test **voit** une dérive quand il y en a une.

## 6. Ce que ça change pour le graal

- La panne que l'humain répare d'une spire à l'autre est un atterrissage du mauvais côté d'une
  feuille. **Sur le mécanisme, elle ne se produit pas** : le décalage est stable, il diminue même
  sous obliquité, et l'avance vaut une feuille par pas à moins d'un pour cent.
- ⭐ Avec `119` (la direction ne dérive pas, les virages se compensent) et `117` (la matière seule
  refuse au plus un pas sur onze), la liste de ce qu'un remplaçant de l'humain doit faire se réduit
  encore : il reste à **s'arrêter honnêtement** (`116`) et à **exprimer l'espacement local**
  (`118`, `121`, `122`).
- ⚠⚠ Ce qui n'est **pas** établi : rien de ceci ne porte sur le vrai rouleau. Une pile plane à pas
  constant n'a ni déchirure, ni feuille qui fusionne, ni région sans matière. C'est le **mécanisme**
  qui est mesuré, et c'est la re-course qui dira ce que la matière en fait.

## 7. Les registres

Fait `R4-F51` (le décalage à la feuille ne grandit pas, et le naïf dérive). Aucune porte ouverte :
ce que ce document laisse est ce que `R4-P20` demande déjà.

## Reproduire

```bash
uv run python src/nappe/le_marcheur_reste_t_il_verrouille.py --verifier   # 10 contrôles
uv run python src/nappe/le_marcheur_reste_t_il_verrouille.py \
    --json docs/mesures/le_marcheur_reste_t_il_verrouille.json
```

⚠ **Tout est analytique** : aucune lecture distante, aucune figure. Le marcheur est **importé** de
`combien_de_pas_la_matiere_porte.py` et les piles fabriquées le sont aussi — un second marcheur
serait deux implémentations d'une même marche, et c'est la marche elle-même qu'on mesure.
