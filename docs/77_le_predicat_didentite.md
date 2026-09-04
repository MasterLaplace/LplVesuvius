# 77 — Le prédicat d'identité : le champ d'enroulement, et la moitié que le pinceau peint

> Écrit le 2026-09-04. Tâche **A2** du registre `75`. Mesure dans l'arbre :
> `src/excision/le_champ_denroulement.py` (9 contrôles, 2 sondes qui mordent).

---

## 0. Ce qui manquait, en une phrase

L'article établit que le prédicat peint à la main dans le pipeline de référence est un
prédicat d'**identité** — *« regions judged geometrically consistent with a **single sheet** »*
— et que c'est là que partent les **775 heures de pinceau par rouleau**. Le dépôt avait
construit la **présence** (α : il y a une feuille à portée) et le **placement** (`offset` : la
surface est *sur* elle). **L'identité manquait.**

`76` a rendu un référent utilisable : 81 spires consécutives approuvées, comptant vers
l'extérieur, un pas d'indice valant un écart constant. Ce document s'en sert pour construire un
**champ d'enroulement** — pour tout point, l'indice de spire, en continu — et le mesure.

**Résultat : le champ compte les feuilles, et les deux populations ne se recouvrent pas.**

---

## 1. La grandeur qui décide — et j'ai dû la corriger deux fois

⚠ **Première version, fausse par construction.** J'ai mesuré l'**étendue** de l'indice le long
d'une spire en attendant qu'elle soit nulle. Elle vaut **1,44 feuille**, et la surface témoin
qui traverse trois feuilles n'en rendait que **2,57** — un rapport de 1,8, qui ne sépare
presque rien.

La raison est physique : **une spire EST un tour de spirale**, donc son rayon croît d'exactement
un écart inter-feuilles sur 360°. Exiger que son indice soit constant, c'est exiger que le
rouleau ne soit pas enroulé.

⚠ **Deuxième correction, elle aussi venue de la mesure.** J'ai alors prédit une avance de
**+1 par tour** pour une feuille. C'est **0**. Le champ est bâti sur des spires qui spiralent
toutes de la même façon, donc **la spirale est absorbée dans le champ** : ses surfaces
d'iso-indice spiralent avec le rouleau. C'est exactement ce qu'un nombre d'enroulement doit
faire.

**La grandeur est donc l'avance d'indice sur un tour complet**, et la revendication est qu'elle
compte les feuilles franchies.

---

## 2. La mesure

Champ bâti sur les 37 spires de `PHerc0139`, **validation à spire exclue** — la spire jugée est
retirée du champ qui la juge.

| surface | avance par tour | p10 | p90 | n |
|---|---:|---:|---:|---:|
| **vraie spire** (approuvée) | **−0,005** | −0,170 | +0,230 | 35 |
| saut fabriqué de **1** feuille | **1,103** | 0,753 | 1,479 | 32 |
| saut fabriqué de **2** feuilles | **1,962** | 1,369 | 2,517 | 33 |
| saut fabriqué de **3** feuilles | **2,851** | 2,314 | 3,300 | 32 |

⭐⭐⭐ **Les deux populations ne se recouvrent pas** : une vraie spire monte au plus à **+0,230**,
un saut d'une feuille commence à **0,753**. C'est ce qui fait un prédicat plutôt qu'une
tendance.

⭐ Et l'avance **compte** : 0 → 1,10 → 1,96 → 2,85 pour 0, 1, 2, 3 feuilles franchies.

### ⚠⚠ Le témoin est CONSTRUIT, pas espéré

Une surface qui traverse l'empilement est fabriquée **depuis le référent lui-même** : fondu sur
l'angle entre la spire `k` et la spire `k+n`. Elle est lisse, plausible, et traverse `n`
feuilles **par construction**. Sans elle, « l'avance d'une vraie spire est nulle » serait
satisfait par un champ constant, qui ne mesure rien.

⚠ Et les témoins sont fabriqués **à chaque position**, pas une fois au milieu : un témoin
unique dirait « le champ voit CE saut-là » ; une distribution dit si les deux populations se
**séparent**, ce qu'un prédicat doit faire.

⚠ Les deux spires qui servent à fabriquer un témoin sont **retirées du champ qui le juge**,
sinon le champ reconnaîtrait ses propres bornes.

---

## 3. ⭐⭐⭐ La validation croisée : deux instruments, les mêmes deux défauts

Le saut d'une feuille est fabriqué à 32 positions. **Deux** ne montent pas :

| position | avance | ce que `76` en disait |
|---|---:|---|
| `w041` → `w042` | **0,169** | à **88 µm**, une demi-feuille |
| `w045` → `w046` | **−0,141** | à **0,0 µm** — **la même surface** |
| les 30 autres | 0,66 à 1,94 | des feuilles voisines |

**Ce ne sont pas des ratés du prédicat, ce sont des défauts du référent** — et ce sont
**exactement** les deux que `76` avait signalés par une méthode qui ne partage rien avec
celle-ci (comparaison radiale appariée, puis distance au plus proche voisin).

Un « saut d'une feuille » fabriqué entre deux surfaces qui sont la même surface **n'est pas un
saut**, et le champ le dit. C'est le contrôle le plus fort du fichier : il est écrit dans le
sens « les positions qui n'avancent pas sont **exactement** `[41, 45]` », donc il échoue si le
prédicat en rate une **ou** s'il en invente une.

---

## 4. ⚠ Les sondes — deux mordent, deux non

| sonde | effet |
|---|---|
| ne pas exclure la spire jugée du champ qui la juge | ⭐ **erreur exactement 0,0000** au lieu de 0,0876 — le champ **lit** au lieu d'interpoler |
| laisser les spires bornes dans le champ qui juge le témoin | ⭐ la validation croisée trouve `[45]` au lieu de `[41, 45]` |
| avance par la différence des extrémités au lieu d'une pente ajustée | ne mord pas (bandes plus serrées, sépare encore) |
| — | — |

⚠⚠ **La première sonde a corrigé un contrôle trop lâche.** Elle ne mordait pas d'abord : mon
seuil (`erreur < 0,5`) acceptait aussi bien 0,0876 que 0,0000. Or **0,0000 est la signature
d'un champ qui a lu la spire au lieu de l'interpoler**. Un contrôle « … et elle n'est **pas**
nulle » a été ajouté, et la sonde mord désormais. Sans lui, l'exclusion n'était vérifiée par
rien.

---

## 5. Ce que ça établit, et ce que ça n'établit pas

**Établi** : on peut dire d'une surface, sans la peindre à la main, si elle reste sur une
feuille — pourvu qu'elle soit dans la bande couverte par des spires connues. C'est la moitié
d'identité que l'article déclare ouverte, et le prédicat existe désormais.

⚠ **Non établi :**

1. **Que le champ vaille hors de la bande publiée.** Il interpole entre spires connues et
   **refuse** au-delà plutôt qu'extrapoler — un prédicat qui répond partout est un prédicat qui
   ne refuse jamais. C'est la limite qui compte pour un déploiement, et elle est dure : sur
   `PHerc0139` la bande fait 37 spires sur ~110.
2. **Que ce soit le seul prédicat d'identité possible.** C'en est un, **adossé au référent**.
   Un champ dérivé du volume (résidus d'orientation, `69` A2, `75` A2) répondrait **sans**
   référent, et reste à mesurer. C'est celui-là qui déploierait.
3. **Qu'un traceur puisse s'en servir en ligne.** Le champ est une table ; l'y brancher est un
   autre lot — c'est la tâche **A3** du registre.

---

## 6. ⭐⭐⭐ Suite immédiate : `approval.tif` calculé, aux quatre bras de contrôle

> Mesure : `src/excision/le_masque_dapprobation.py` (7 contrôles, 2 sondes qui mordent fort).

L'article §6.7 établit que l'intégration tient en **un fichier** : le chargeur du pipeline de
référence adopte tout `.tif` posé à côté de `x/y/z.tif` comme canal nommé, et `approval` est
celui qui autorise la ré-optimisation. Écrire `approval.tif` **est** l'intégration.

### ⚠⚠ Le champ donne DEUX prédicats, et je les avais confondus

| prédicat | grandeur | sur une feuille | dans l'interstice |
|---|---|---:|---:|
| **placement** | partie **fractionnaire** de l'indice | **0,001** | **0,502** |
| **identité** | **avance** de l'indice sur un tour | −0,005 | 0 *(!)* |

⚠ Une copie translatée d'un demi-pas a une avance **nulle** — elle suit parfaitement une
feuille qui n'existe pas. C'est le **placement** qui la refuse, jamais l'identité. Un masque
qui n'aurait que l'identité approuverait une surface posée dans le vide.

Les seuils sont posés **entre les deux populations mesurées**, pas réglés : placement 0,30
(la feuille monte à 0,204, le demi-pas descend à 0,435) et identité 0,45 (+0,230 contre 0,753).
Les populations ne se recouvrant pas, tout seuil de ces intervalles donne le même verdict.

### Les cinq bras

| bras | approuvé | p10 | p90 | ce que ça vaut |
|---|---:|---:|---:|---|
| spire lue par son propre champ | **98,7 %** | — | — | ⚠ circulaire — prouve seulement que le masque approuve **quelque chose** |
| **quart de pas** | **92,7 %** | 64,5 % | 96,1 % | ⭐ le **témoin positif réaliste** |
| spire à spire exclue | 53,9 % | 36,6 % | 68,3 % | ⚠⚠ **pathologique**, voir ci-dessous |
| **demi-pas** | **2,1 %** | 0,9 % | 6,1 % | ⭐ le bras qui mord |
| **saut d'une feuille** | **0,0 %** | 0,0 % | 0,0 % | refusé |

⚠⚠⚠ **Le quatrième bras est celui sans lequel le contrôle ne peut pas échouer.** Approuver une
spire, refuser un masque vide, refuser un masque plein : les trois se satisfont d'un masque qui
approuve tout. C'est la **copie translatée d'un demi-pas** qui mord — une surface lisse,
plausible, et posée là où il n'y a pas de papyrus.

### ⚠⚠ Une spire publiée ne peut pas être son propre témoin positif de placement

Ni avec son champ, ni sans :

- **champ complet** → **100 %**, mais le champ contient la spire qu'il juge : circulaire ;
- **à spire exclue** → **70 %**, parce que la retirer place la spire **exactement au milieu de
  l'intervalle que son retrait vient de créer**. Le champ la voit dans un interstice, **par
  construction**.

C'est pourquoi le témoin positif est le **quart de pas** : une surface près d'une feuille que
le champ connaît, et qui n'est pas un membre du champ — ce qui est exactement la situation
d'une trace neuve à l'usage.

### ⚠⚠⚠ Le bug que j'avais écrit, et ce qu'il coûtait

Ma première version retirait du champ la spire qui **borne** la surface jugée, en croyant
éviter une fuite. Ça **détruisait l'information qui détecte un interstice** : sans la borne
haute, le vide entre deux feuilles n'est plus un vide, c'est le milieu d'un intervalle de trois
feuilles.

**Un demi-pas passait de 2,1 % à 37,6 % d'approbation** — d'un refus net à une approbation
nette, sans qu'aucun nombre n'ait l'air faux. La sonde qui le rejoue fait tomber **4
contrôles**.

⚠ Et le réglage juste est aussi le plus **réaliste** : à l'usage, le champ est tout ce qui est
publié, et la surface jugée est une trace neuve, absente du champ.
