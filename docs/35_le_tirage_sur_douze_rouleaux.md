# Le tirage, sur douze rouleaux — M1bis

2026-08-20. `30` avait mesuré que `vc_grow_seg_from_seed` rend un résultat différent à
chaque exécution — mais sur **une** graine, d'**un** rouleau, en quatorze tirages. `29`
marquait le manque ⚠⚠ : *« 14 tirages ne font pas une distribution, et le taux de 13 % n'a
été mesuré que sur une graine »*.

**72 tirages, 12 rouleaux, six par rouleau, paramètres strictement identiques.**

---

## 0. La forme, d'un coup d'œil

![douze rouleaux, six tirages chacun](images/35_tirages.png)

> **Si le traceur était déterministe, chaque ligne serait un point unique.** Aucune ne
> l'est. Et sur quatre lignes un point est rouge : le même appel qui rend une trace propre
> cinq fois rend une trace auto-intersectée la sixième.

Figure : `analysis/src/figure_tirages.py`, depuis `docs/table_tirages.json`.

## 1. Ce que la campagne mesure

| | |
|---|---:|
| tirages exploitables | **72** |
| rouleaux | **12** |
| rouleaux dont l'aire est identique sur les six tirages | **0 sur 12** |
| ⭐ rouleaux où le **VERDICT bascule** d'un tirage à l'autre | **4 sur 12** |
| mauvais tirages | **4 / 72 = 5,6 %** (IC 95 % exact : 1,5 % – 13,6 %) |

Les quatre basculements, avec le pire compte du rouleau :

| rouleau | croisements par tirage | dispersion d'aire |
|---|---|---:|
| `PHerc0125` | **1615**, 0, 0, 0, 0, 0 | 0,31 % |
| `PHerc0257` | 0, 0, 0, 0, 0, **428** | 0,24 % |
| `PHerc0268` | **607**, 0, 0, 0, 0, 0 | 0,33 % |
| `PHerc1447` | 0, 0, 0, **1371**, 0, 0 | 35,14 % |

> ⭐ **Un basculement est la preuve la plus forte disponible** : deux exécutions à
> paramètres strictement identiques, deux verdicts opposés. Aucun seuil, aucune vérité
> terrain, aucune interprétation. Le résultat de `30` ne tenait pas à sa graine.

⚠ Le taux de 5,6 % est **compatible** avec les 13 % de `30` (2 sur 15) — les deux
intervalles se recouvrent largement. Ce que la campagne apporte n'est pas un taux plus
petit, c'est un intervalle **quatre fois plus étroit** et une **généralité** : le phénomène
existe sur des rouleaux, des graines et des tailles de trace différents.

## 2. ⭐⭐ Et l'étendue ne signale PAS le mauvais tirage

C'est le résultat que la figure a fait apparaître, et il compte pour la suite : **les trois
rouleaux dont les six tirages ont pratiquement la même aire sont ceux qui portent les pires
comptes.**

Mesuré plutôt que lu à l'œil. Pour chaque mauvais tirage, son **rang d'aire** dans son
propre rouleau, centré-normalisé — 0 = l'aire médiane du rouleau, 1 = l'extrême :

> **excentricité moyenne : 0,60**, contre **~0,50** attendu si l'aire ne disait rien.

⚠ **Sur quatre événements, 0,60 contre 0,50 n'est rien.** La conclusion utilisable est
négative et elle suffit : **on ne peut pas écarter un mauvais tirage en regardant sa
taille.** Il faut le juger — ce qui est précisément ce que nos instruments savent faire pour
0,05 s.

C'est la même leçon que `30` §2 avait établie sur un cas isolé — deux maillages à 0,003 %
d'aire l'un de l'autre, deux verdicts opposés — généralisée à douze rouleaux.

## 3. ⚠ Une observation qu'il ne faut PAS transformer en résultat

La dispersion médiane vaut **0,3 %** chez les rouleaux qui basculent et **12,8 %** chez les
autres — un facteur 40, dans le sens contraire de l'intuition.

**C'est trop beau, et ça ne tient pas debout sur ces effectifs.** Quatre rouleaux contre
huit, et un confond visible dans le tableau : les rouleaux à faible dispersion sont ceux
dont les six tirages atteignent le **plafond de générations** (118 sur 118), donc dont la
trace sature. Répartis ainsi, 3 basculements sur 6 rouleaux plafonnés contre 1 sur 6 non
plafonnés — un test exact donne p ≈ 0,55.

> **Rien n'est établi ici.** C'est noté parce qu'une hypothèse écartée avec sa raison vaut
> mieux qu'une hypothèse oubliée, et parce que la mesure qui trancherait est bon marché :
> relever le plafond de générations et rejouer.

## 4. Ce que ça change pour la chaîne

`31` §5 disait que l'étage « tracer » est le maillon dont *« l'outil officiel marche mais
n'est pas reproductible »*, et proposait deux issues : rendre le traceur déterministe, ou
**tirer N fois et sélectionner**. Cette campagne chiffre la seconde.

| fait mesuré | conséquence |
|---|---|
| 4 mauvais tirages sur 72, IC [1,5 % – 13,6 %] | à **trois tirages**, la probabilité d'en avoir au moins un propre est **99,75 %** même à la borne haute de l'intervalle — ⚠ *si les tirages sont indépendants*, ce que ces données ne prouvent pas |
| un tirage coûte **~70 s** sur ces rouleaux | trois tirages coûtent ~3,5 min par départ |
| notre juge coûte **0,05 s**, sans vérité terrain | on peut tous les juger |
| ⭐ **l'aire ne prédit pas le verdict** | on **ne peut pas** faire l'économie du juge |

⚠⚠ **Et le piège de conception reste entier** : prendre le minimum de N tirages avec un juge
bruité fait remonter la **chance** autant que la qualité. Le protocole honnête reste celui
de `31` §4 — **sélectionner sur un axe, valider sur l'autre** — et cette campagne ne le
teste pas.

## 5. ⚠ Ce que cette campagne ne dit pas

- **Elle ne dit pas pourquoi.** La cause de la non-reproductibilité n'est toujours pas
  identifiée. `30` avait écarté `thread_limit` ; rien ne l'a remplacé.
- **Elle ne dit pas qu'une trace propre est une BONNE trace.** L'absence
  d'auto-intersection est nécessaire, pas suffisante — `28` §4 mesure qu'aucun test
  géométrique ne voit un saut d'une seule spire dans le cas serré.
- **Six tirages par rouleau ne mesurent pas un taux PAR rouleau.** Le 5,6 % est un taux
  **groupé** ; savoir si un rouleau est plus instable qu'un autre demanderait bien plus de
  tirages, exactement comme `33` le mesure pour la carte de difficulté.
- ⚠ **Un rouleau du prix manque, et pas pour la raison qu'on croirait.** La campagne
  couvre 12 des 13 parce que `docs/table_graines.json` en contient 12 : **`PHerc1203` n'a
  jamais eu de graine cherchée**, sur aucune campagne — `tools/campagne_graines.sh` ne le
  liste pas, alors que `tools/carte_separabilite.sh` le liste. Ce n'est donc pas une
  limite de cette campagne-ci, c'est un trou en amont, et il vaut aussi pour `25`. ⏳ À
  combler : `PHerc1203` est l'un des trois rouleaux du prix qui ont un segment publié
  (`16` §1), donc l'un des rares où l'on pourrait comparer notre trace à la leur.

## Reproduire

```bash
./tools/lancer.sh --fond tools/campagne_tirages.sh "$PWD/data/tirages" 6
cd experiments
uv run python ../analysis/src/table_tirages.py --json ../docs/table_tirages.json
cd ../inference && uv run python ../analysis/src/figure_tirages.py
```

⚠ Passer par `tools/lancer.sh` n'est pas décoratif : la première exécution de cette
campagne a été **tuée par une édition du script pendant qu'il tournait**, et il a fallu la
reprendre. Le wrapper gèle une copie avant de lancer.
