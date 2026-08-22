# Le tirage, sur treize rouleaux — M1bis

> ⚠ Le nom du fichier dit « douze » : c'est l'état du 2026-08-20, et il est **gardé** pour
> que les liens des autres documents continuent de résoudre. La campagne en couvre **treize**
> depuis le 2026-08-22 — `PHerc1203` a reçu ses graines et ses six tirages (§5).

2026-08-20. `30` avait mesuré que `vc_grow_seg_from_seed` rend un résultat différent à
chaque exécution — mais sur **une** graine, d'**un** rouleau, en quatorze tirages. `29`
marquait le manque ⚠⚠ : *« 14 tirages ne font pas une distribution, et le taux de 13 % n'a
été mesuré que sur une graine »*.

**78 tirages, 13 rouleaux, six par rouleau, paramètres strictement identiques.**

---

## 0. La forme, d'un coup d'œil

![treize rouleaux, six tirages chacun](images/35_tirages.png)

> **Si le traceur était déterministe, chaque ligne serait un point unique.** Aucune ne
> l'est. Et sur cinq lignes un point est rouge : le même appel qui rend une trace propre
> cinq fois rend une trace auto-intersectée la sixième.

Figure : `analysis/src/figure_tirages.py`, depuis `docs/table_tirages.json`.

## 1. Ce que la campagne mesure

| | |
|---|---:|
| tirages exploitables | **78** |
| rouleaux | **13** |
| rouleaux dont l'aire est identique sur les six tirages | **0 sur 13** |
| ⭐ rouleaux où le **VERDICT bascule** d'un tirage à l'autre | **5 sur 13** |
| mauvais tirages | **5 / 78 = 6,4 %** (IC 95 % exact : 2,1 % – 14,3 %) |

Les cinq basculements, avec le pire compte du rouleau :

| rouleau | croisements par tirage | dispersion d'aire |
|---|---|---:|
| `PHerc0125` | **1615**, 0, 0, 0, 0, 0 | 0,31 % |
| `PHerc0257` | 0, 0, 0, 0, 0, **428** | 0,24 % |
| `PHerc0268` | **607**, 0, 0, 0, 0, 0 | 0,33 % |
| `PHerc1203` | **140**, 0, 0, 0, 0, 0 | 0,63 % |
| `PHerc1447` | 0, 0, 0, **1371**, 0, 0 | 35,14 % |

> ⭐ **Un basculement est la preuve la plus forte disponible** : deux exécutions à
> paramètres strictement identiques, deux verdicts opposés. Aucun seuil, aucune vérité
> terrain, aucune interprétation. Le résultat de `30` ne tenait pas à sa graine.

⚠ Le taux de 6,4 % est **compatible** avec les 13 % de `30` (2 sur 15) — les deux
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

**C'est trop beau, et ça ne tient pas debout.** Le confond est visible dans le tableau : les
rouleaux à faible dispersion sont ceux dont les six tirages atteignent le **plafond de
générations**, donc dont la trace **sature**. Une dispersion mesurée sous une troncature
commune ne mesure pas le traceur, elle mesure la troncature.

⭐ **Et le partage par plafond est plus net que le partage par basculement**, ce qui désigne
lequel des deux explique l'autre :

| partage | dispersion médiane | | facteur |
|---|---:|---:|---:|
| par **basculement** | 0,3 % | 12,8 % | 43 |
| par **plafond** | **0,5 %** | **19,9 %** | **40** |

Et l'association entre les deux reste **non significative** : **4 basculements sur 6
rouleaux plafonnés contre 1 sur 7** — test exact **p = 0,10**.

⚠⚠ **Ce chiffre est recalculé, il ne l'était pas.** La version du 2026-08-20 écrivait
« un test exact donne p ≈ 0,55 » — un nombre sans producteur dans l'arbre, donc une anecdote
au sens de la règle de ce dépôt, et périmé dès que le treizième rouleau est arrivé.
`analysis/src/table_tirages.py` le calcule désormais, avec le plafond **dérivé** de la
campagne (le maximum de générations observé) plutôt qu'écrit en dur : une constante
deviendrait fausse en silence le jour où le budget du `seed.json` change.

> **Rien n'est encore établi sur la CAUSE.** C'est noté parce qu'une hypothèse écartée avec
> sa raison vaut mieux qu'une hypothèse oubliée, et parce que la mesure qui trancherait est
> bon marché : relever le plafond de générations et rejouer. C'est désormais un paramètre —
> `GENERATIONS=400 ./tools/campagne_tirages.sh data/tirages_plafond 6 <rouleaux>` — et le
> plafond effectif voyage dans chaque résumé, pour que deux campagnes à plafonds différents
> ne produisent pas des lignes indistinguables.

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
  couvre 12 des 13 parce que `docs/table_graines.json` en contenait 12 : **`PHerc1203`
  n'avait jamais eu de graine cherchée**, sur aucune campagne — `tools/campagne_graines.sh`
  ne le listait pas, alors que `tools/carte_separabilite.sh` le liste. Ce n'était donc pas
  une limite de cette campagne-ci, c'était un trou en amont, et il valait aussi pour `25`.

  ✅ **Comblé le 2026-08-22, côté graines** : `PHerc1203` a maintenant ses deux graines,
  planéité **19,84 cm²** et voisinage **9,60 cm²**, zéro auto-intersection des deux côtés.
  La campagne appariée de [`25`](25_une_graine_choisie_sur_la_planeite.md) passe de 12 à
  **13 rouleaux**, et le résultat se **renforce** : 10/12 à p = 0,0386 devient **11/13 à
  p = 0,0225**. ⚠ Le combler a demandé de réparer d'abord un appariement surface/volume
  par POSITION, décrit dans `25` §4bis — `PHerc1203` est l'un des deux seuls rouleaux du
  prix à avoir plusieurs scans, donc le seul endroit où ce défaut latent aurait mordu.

  ⏳ **Et il reste ouvert du côté des tirages** : cette campagne-ci, elle, couvre toujours
  **12 rouleaux**, parce que les six tirages de `PHerc1203` n'ont pas été faits. Le chiffre
  publié ici (5,6 %, IC [1,5–13,6 %]) porte donc sur douze rouleaux, et le dire est moins
  coûteux que de laisser croire qu'il en couvre treize.

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
