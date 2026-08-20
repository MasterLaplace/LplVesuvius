# La carte des treize rouleaux n'est pas résolue par ses propres données

2026-08-20. `16` classe les treize rouleaux du Grand Prize sur la **queue** de leur
séparabilité et en tire une désignation : *« c'est ce qui désigne `PHerc0358` (4 %) comme
le premier à attaquer »*. Ce document mesure **l'incertitude** de ce classement, que `16`
n'affichait pas. Elle l'annule.

Aucune nouvelle donnée n'a été acquise pour ce résultat : c'est une relecture des
artefacts versionnés, `docs/carte_separabilite/*.json`, par
`analysis/src/incertitude_carte.py`.

---

## 0. La forme, d'un coup d'œil

![les treize rouleaux avec leur intervalle de confiance](images/33_incertitude.png)

> **Chaque rouleau est un intervalle, pas un point** — et ils se recouvrent tous, y
> compris avec celui du témoin. C'est la raison pour laquelle aucune des 78 paires n'est
> séparée, et elle se voit sans qu'aucun test soit nécessaire.

Figure : `analysis/src/figure_incertitude.py`, depuis `docs/incertitude_carte.json`.

## 1. Ce que la mesure trouve

| question | réponse |
|---|---|
| rouleaux **distinguables du témoin** après correction de Holm | **0 sur 13** |
| ... au seuil nominal, sans correction | 5 sur 13 |
| **paires de rouleaux réellement séparées** | **0 sur 78** |
| intervalle du mieux classé, `PHerc0358` (1/28) | **0,1 % – 18,3 %** |
| intervalle du **témoin**, `PHerc0139` (0/24) | **0,0 % – 14,2 %** |

⚠⚠ **Le zéro du témoin n'est pas un zéro.** Sur 24 fenêtres, une observation de 0 est
compatible avec un taux réel allant jusqu'à **14,2 %** — c'est-à-dire au-dessus de la part
observée de **huit** des treize rouleaux. La phrase de `16` — *« le témoin a une propriété
qu'aucun des treize ne partage : 0 % »* — décrit une observation, pas une propriété.

⚠ **La correction de Holm n'est pas un raffinement optionnel ici.** Treize comparaisons au
seuil de 5 % rendent un « significatif » attendu par pur hasard ; les cinq p nominaux vont
de 0,014 à 0,028, donc exactement dans la zone que treize essais produisent tout seuls.
Ce dépôt a déjà écrit cette réserve ailleurs (`19` : *« ❌ nominal seulement »*), et elle
s'applique ici à l'identique.

## 2. Ce qui SURVIT

Un résultat négatif qui n'énonce pas ce qui reste vrai est aussi trompeur que le résultat
qu'il corrige.

| ce qui tient | ce qui ne tient pas |
|---|---|
| les treize **pris ensemble** : 42/300 = 14,0 % contre 0/24, p = 0,031 | le **classement** des treize entre eux |
| **13 sur 13** ont une queue au-dessus de celle du témoin — la direction est unanime | qu'un rouleau nommé soit meilleur qu'un autre rouleau nommé |
| la **médiane** ne sépare rien : ça, `16` l'établit et ce document ne le touche pas | la désignation de `PHerc0358` comme premier à attaquer |

⚠ **Et le p groupé est une borne basse, pas un p.** Il traite les 300 fenêtres comme
échangeables entre rouleaux, alors qu'elles sont **groupées par rouleau** : des fenêtres
du même rouleau se ressemblent plus qu'entre rouleaux, donc l'effectif effectif est plus
petit que 300 et le vrai p est plus grand que 0,031. À lire comme un ordre de grandeur,
et il est déjà marginal à cette lecture-là.

## 3. ⭐ Ce qui résoudrait la question — et c'est bon marché

La puissance a été calculée **exactement**, par énumération des (n+1)² tables possibles
pondérées par leur probabilité binomiale — pas par l'approximation normale, qui surestime
la puissance à ces effectifs et promettrait donc une campagne moins chère que la vraie.

| fenêtres par rouleau | puissance à séparer 3,6 % de 23,8 % |
|---:|---:|
| 25 | 39 % |
| **50** | **80 %** |
| 100 | 99 % |
| 200 | 100 % |

> ⭐ **50 fenêtres par rouleau suffisent**, contre **15 à 35** aujourd'hui. Ce n'est pas un
> instrument neuf, c'est un échantillonnage plus dense de celui qui existe.

⚠ Ça sépare les **extrêmes**, et rien de plus. Les paires du milieu — `PHerc0257` à 10,5 %
contre `PHerc1545` à 11,8 % — resteront hors de portée à tout effectif raisonnable, et
c'est une propriété du problème, pas de la campagne : ces deux rouleaux ne diffèrent
peut-être pas.

⚠ Et séparer un rouleau du **témoin** est une autre affaire : opposer 0 % à 3,6 % demande
des milliers de fenêtres. Ce qu'on peut établir, c'est le contraste entre les extrêmes des
treize, pas le contraste de chacun au témoin.

## 4. Le rapport à la marge du prix

Le règlement tolère *« less than 10 % »* de patches externes déconnectés sautés. La
tentation est de confronter les 4–24 % à ces 10 %.

⚠⚠ **Ce sont deux grandeurs différentes** : la part mesurée est une fraction de **fenêtres
sondées**, celle du prix une fraction de **surface de recto**. La figure trace la ligne des
10 % en pointillé pour cette raison, et le script l'imprime comme *indicative*.

Ce qu'on peut dire sans confondre : **aucun** des treize n'a un intervalle qui exclut d'être
sous 10 %, et **aucun** n'a un intervalle qui exclut d'être au-dessus. Sur cette donnée,
la question « ce rouleau tient-il dans la marge ? » n'a de réponse pour aucun des treize.

## 5. Ce que ce document change ailleurs

| document | ce qui devient faux | ce qui reste |
|---|---|---|
| `16` §0, §6 | *« c'est la queue qui sépare »* comme énoncé de classement ; la désignation de `PHerc0358` | la médiane ne sépare rien ; les treize pris ensemble diffèrent du témoin |
| `13` H4 | *« `PHerc0358` désigné »* | la carte existe, le témoin est apparié |
| `31` §10, §11.2 | *« ça dit **sur lequel** des treize le prix est jouable »* | *« mesurer la part comprimée rouleau par rouleau »* reste la bonne mesure — il faut juste **50 fenêtres**, pas 27 sondes |

⚠ **`PHerc0358` reste un choix défendable** — il a la part observée la plus basse, et il
faut bien commencer par un rouleau. Ce qui tombe, c'est que **la mesure le désigne**. Un
choix par le meilleur point observé sur des données qui ne séparent rien est un choix par
défaut assumé, pas une conclusion.

## 6. ⚠ Ce que ce document ne dit pas

- **Il ne dit pas que la carte est fausse.** Il dit qu'elle est **sous-échantillonnée**.
  Les parts mesurées sont les meilleures estimations disponibles ; c'est leur **ordre** qui
  n'est pas établi.
- **Il ne remet pas en cause l'instrument** (`separabilite_scan.py`), ni le choix du
  témoin apparié, ni le niveau 1 de la pyramide. Toutes ces décisions de `16` tiennent.
- **Il ne mesure pas la part comprimée en surface.** C'est une mesure différente, et la
  seule qui se compare vraiment à la marge du prix.

## Reproduire

```bash
cd experiments
uv run python ../analysis/src/incertitude_carte.py --json ../docs/incertitude_carte.json
cd ../inference
uv run python ../analysis/src/figure_incertitude.py
```

Une campagne dense s'écrit dans **son propre dossier**, pour que les chiffres publiés de
`16` restent reproductibles à côté :

```bash
./tools/carte_separabilite.sh docs/carte_separabilite_dense 125
```
