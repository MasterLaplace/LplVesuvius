# Le traceur est un tirage — et ça coûte deux explications avant d'en rendre une

2026-08-19, soir.

> ⚠ **Lire le signe avant les étoiles.** Ce document contient un résultat qui **nous
> aide** et deux qui **nous coûtent**. Les repères `⭐` de ce dépôt marquent *ce qui
> compte*, pas *ce qui va bien* — et la distinction s'était perdue. Elle est rétablie
> ici : chaque bloc dit s'il ajoute ou s'il retire.

---

## 1. Ce qui a déclenché la mesure

La campagne de `26` §9 devait rejouer le balayage de `step_size` sur la **mauvaise
graine** — celle de `24`, `1544 1544 7768`, qui avait donné **240 auto-intersections**.
Elle a rendu **zéro** à tous les pas sauf 5.

Or `24` avait tracé cette graine à `step_size` **20**, et la campagne aussi. La seule
différence entre les deux fichiers de paramètres était `thread_limit` : **0** contre
**1**. D'où une mesure directe : rejouer, en répétant.

## 2. Le résultat, mesuré

`src/campagnes/campagne_thread_limit.sh`, dépouillé par `src/tables/table_thread_limit.py`.
Quatorze tirages, **paramètres strictement identiques**, même graine.

| `thread_limit` | essai | générations | aire (cm²) | auto-intersections |
|---:|---:|---:|---:|---:|
| 0 | 1 | 84 | 9,886931 | 0 |
| 0 | 2 | 80 | 8,920213 | 0 |
| 0 | 3 | 78 | **8,475839** | 0 |
| 0 | 4 | 79 | 8,697002 | 0 |
| **0** | **5** | **79** | **8,693065** | **79** |
| 0 | 6 | 86 | 10,341790 | 0 |
| 0 | 7 | 78 | 8,476525 | 0 |
| 0 | 8 | 64 | 5,691978 | 0 |
| 0 | 9 | 81 | 9,158762 | 0 |
| 0 | 10 | 80 | 8,913921 | 0 |
| 1 | 1–4 | 78–79 | 8,477–8,699 | 0 |

**13 tirages propres sur 14.** L'aire va de **5,69 à 10,34 cm²** — une étendue relative de
**53,5 %** à paramètres identiques.

### ⚠ Le contrôle qui rend le résultat lisible

Le maillage de `24` est **archivé** (`data/artefacts/PHerc0358/mesh.tifxyz`). Remesuré
aujourd'hui : **240 auto-intersections**, exactement. Le maillage original de la journée
(`data/trace/PHerc0358/auto_grown_20260819113515563`) aussi. **La mesure est fidèle.**

| | aire | auto-intersections |
|---|---:|---:|
| maillage de `24`, archivé | **8,476817** cm² | **240** |
| tirage `tl=1 r=4`, mêmes paramètres | **8,477096** cm² | **0** |

**0,003 % d'écart d'aire. Deux verdicts opposés.**

> **La différence entre une trace condamnée et une trace propre n'est ni dans les
> paramètres, ni dans l'étendue de la trace. Elle est dans le tirage.**

⚠ `thread_limit` n'y est pour rien : le mauvais tirage est arrivé à **0**, et les quatre
tirages à **1** sont propres — mais dix tirages à 0 le sont aussi. Ce paramètre n'explique
pas l'écart, il ne fait que ne pas le supprimer.

## 3. 🔻 Ce que ça COÛTE — deux explications tombent

### 3.1 Le diagnostic causal de `24` est faux

`24` §4 concluait que la trace coupait les spires **parce que** le traceur n'avait reçu
aucune information d'orientation. Ce diagnostic était déjà tombé (`26`, trois négatifs
mesurés). Il tombe une seconde fois, autrement : **la même trace, sans plus
d'information, sort propre 13 fois sur 14.**

### 3.2 ⚠⚠ Et l'explication de rechange de `25` tombe aussi

`25` §4bis avait remplacé le diagnostic par un autre, plus solide en apparence :

> *« `occup. = 1,000`. Le bloc est **entièrement plein** de matière prédite. Un bloc
> uniforme a un tenseur nul […] le traceur est parti d'un endroit où il n'existait aucune
> géométrie à suivre. […] le **plafond d'occupation** écarte à lui seul la graine de
> `24`. »*

**C'est une histoire plausible, et la mesure ne la soutient pas.** La graine est toujours
dans le même bloc plein, le tenseur y est toujours nul — et elle produit une trace propre
treize fois sur quatorze. Le plafond d'occupation écarte peut-être une graine *risquée* ;
il n'explique **pas** les 240.

> ⚠ **Ce qui reste vrai de `25`** : le critère de planéité fait aller le traceur **plus
> loin**, 11 fois sur 13, sur treize rouleaux appariés (p = 0,0225 sur l'aire). Ça, c'est
> mesuré et répliqué. Ce qui tombe, c'est l'attribution des 240 — que `25` avait **déjà**
> commencé à retirer en constatant que le « 240 → 0 » ne répliquait pas.

### 3.3 Ce que ça dit de notre méthode

**Un seul tracé n'est pas une mesure.** Nous avons construit deux documents sur un tirage
unique, et deux explications causales dessus.

⚠ Et ce n'est pas une faiblesse locale : les tableaux d'ablation de la littérature donnent
**une ligne par configuration**, sans répétition ni barre d'erreur (`27` §2), et le papier
du déroulage complet ne publie **aucun** taux d'erreur de traçage (`27` §3). **Personne ne
répète.**

## 4. 🔺 Ce que ça RAPPORTE — un levier que personne n'utilise

Le taux mesuré : **2 mauvais tirages sur 15** (les 14 d'aujourd'hui plus l'archivé),
soit ~13 %. Avec trois tirages, la probabilité d'en avoir au moins un propre est de
~99,8 % — *si* les tirages sont indépendants, ce que ces données ne prouvent pas.

| fait | conséquence |
|---|---|
| une trace coûte **~14 s** | on peut en tirer beaucoup |
| notre juge coûte **0,05 s**, sans vérité terrain | on peut toutes les juger |
| la qualité est un **tirage** | **échantillonner puis sélectionner devient une méthode** |

**Personne ne le fait, et la raison est précise : il faut un juge assez bon marché.**
L'équipe du concours corrige à la main, ~25 h par spire (`27` §3) ; les outils
communautaires jugent *après coup* un maillage qu'on a déjà décidé de garder (`28`).

⚠⚠ **Le piège à traiter dès la conception : la malédiction du vainqueur.** Prendre le
minimum de N tirages avec un juge bruité fait remonter la **chance** autant que la
qualité. Le protocole honnête est de **sélectionner sur un axe et valider sur l'autre** —
ce que `31` §4 décrit, et ce que nos deux instruments indépendants rendent possible.

## 5. ⚠ Ce que cette mesure ne dit pas

- **La cause de la non-reproductibilité n'est pas identifiée.** Le parallélisme est le
  suspect naturel, mais le mauvais tirage est arrivé à `thread_limit: 0` *et* les autres
  tirages à 0 sont propres. Une charge machine différente, un ordre de chunks différent au
  cache — rien n'est établi.
- ⚠ **Une hypothèse concurrente n'a pas pu être écartée proprement** : que la prédiction
  distante ait changé entre le matin et le soir. L'interrogation S3 de la date de
  modification n'a rien rendu. Ce qui plaide contre : les aires des tirages **encadrent**
  celle de `24` (5,69 à 10,34 contre 8,48) au lieu de se décaler en bloc, et deux tirages
  retombent à 0,003 % de son aire.
- **14 tirages ne font pas une distribution.** Le taux de 13 % a un intervalle de confiance
  large, et rien ne dit qu'il vaut pour une autre graine ou un autre rouleau.
- **Rien ici ne dit qu'une trace propre est une BONNE trace.** L'absence
  d'auto-intersection est une condition nécessaire, pas suffisante — `28` §4 mesure
  qu'aucun test géométrique ne voit un saut d'une seule spire dans le cas serré.

## 6. Reproduire

```bash
./src/campagnes/campagne_thread_limit.sh "$PWD/data/trace/PHerc0358/thread_limit" "1544 1544 7768" 10
uv run python src/tables/table_thread_limit.py --json docs/mesures/table_thread_limit.json

# le contrôle : le maillage archivé remesure-t-il bien 240 ?
vc_tifxyz_selfcross --surface data/artefacts/PHerc0358/mesh.tifxyz -o /tmp/recheck.json
```
