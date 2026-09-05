# Ce qui est soumissionnable, et ce qui ne l'est pas

2026-08-18, **révisé le 2026-08-19**. Échéance Progress Prize : **31 août 2026, 23 h 59
Pacific** — dans **12 jours**. Ce document trie ce qu'on a **contre les critères écrits
sur la page `Prizes` du miroir**, pas contre une impression.

---

## 1. Les critères, mot pour mot

> - *« Improve results **quantitatively and/or qualitatively on real data** »*
> - *« Resolve outstanding **bugs in tools that people are using**, and that you are
>   using yourself »*
> - *« Reveal **insightful, actionable** information… for example by **detecting
>   failure-cases of existing methods on real scroll data**, or producing information
>   that resulted in better model results »*
> - *« Are **released or open-sourced early** »* · *« Actually **get used** »*
> - *« If you are working on virtual unwrapping, show visually that **papyrus fibers
>   are visible on your output surface, and it doesn't jump across sheets IN
>   CROSS-SECTION** »*

⚠⚠ **Corrigé le 2026-08-19 : les deux derniers mots manquaient**, sous un titre qui
annonce « mot pour mot ». Vérifié dans le miroir (`data/site/scrollprize.org/prizes.html`).

⭐ Et ils ne sont pas décoratifs : *« in cross-section »* dit **comment** la démonstration
doit être faite — le maillage montré **contre les coupes du volume**, pas seulement le
rendu aplati. C'est exactement ce que produit `vc_tifxyz_selfcross` avec `--collection`,
une *point collection* rechargeable dans VC3D. **Le critère nomme la forme de la preuve,
et nous savons déjà la produire.**

Barème : **20 000 $ garantis** à la meilleure soumission du mois, puis 10 k / 5 k /
2,5 k / 1 k / 0,5 k selon l'importance.

## 2. ⭐⭐ Le candidat solide : l'écart feuille ↔ trace (`12`)

**Ce que c'est.** Une mesure de qualité de trace lue **dans le volume de surface**, pas
sur le maillage : où est la matière par rapport à la couche tracée.

**Pourquoi elle tombe pile sur le troisième critère.** Elle *detecte un failure-case
d'une méthode existante sur de la vraie donnée de rouleau* — sur un segment publié de
PHerc1667, **61 % des fenêtres ont leur pic de matière à un bord de la pile**,
c'est-à-dire que **la feuille est hors du volume de surface**. Et ça explique pourquoi
la détection d'encre n'y rend rien.

**Validation, contre un recensement indépendant** (`12` §11) : sur les 54 segments
communs avec l'index de `windcheck`, rho **−0,487** (p < 0,001) pour la part de fenêtres
centrées, **+0,388** (p = 0,004) pour l'écart en µm. Bonferroni sur 9 grandeurs : les
deux survivent.

**Pourquoi c'est utilisable par d'autres, tout de suite** : un chunk OME-Zarr contient
toute la colonne de profondeur, donc la mesure coûte **1,78 Mo et 1,03 s par fenêtre**,
**à distance**, sans rien télécharger. La même mesure par les couches rendues coûte
**32 Go par segment**.

⚠ Ce qu'elle ne fait PAS, et qu'il faut écrire dans la soumission : elle **ne prédit pas
la lisibilité**. `06` §3.8 l'a mesuré pour la métrique cousine (rho +0,019 à n = 89).
C'est un juge de **trace**, pas de **résultat**.

## 3. ⭐ Le second : le rayon de recherche, corrigé par la physique (`07` §9)

**+0,769 → +0,840** sur Scroll 1 et **+0,284 → +0,666** sur PHerc0139, en remplaçant un
rayon jamais justifié (749 µm) par le **pas inter-feuilles mesuré indépendamment**
(142,8 µm, `11` §3).

⚠ **Honnêteté à tenir** : la métrique corrigée est **la nôtre** (`05`, `07`), pas celle
d'un outil de la communauté. Ça compte comme *« improve results quantitatively on real
data »*, **pas** comme *« resolve bugs in tools that people are using »*. Ne pas
confondre les deux dans la soumission.

⭐ Ce qui le rend stratégique : le gain le plus fort est sur **PHerc0139, à 9,362 µm** —
et **les 13 rouleaux du Grand Prize 2027 sont tous à 8,640–9,362 µm**, avec interdiction
d'utiliser un scan plus fin du même rouleau.

## 3bis. ⭐⭐ Le troisième, et il tombe sur le critère le plus dur : la RÈGLE (`19`)

Les deux précédents **jugent**. Celui-ci **décide**, et c'est exactement le mot du
critère : *« detecting failure-cases of existing methods on real scroll data »*.

> Écarter les **20 %** de segments dont le volume de surface porte le moins de matière
> fait monter le contraste d'encre médian du corpus de **+0,381**, contre **2000
> permutations** de même effectif : **p = 0,0005**.

**Pourquoi c'est solide, en trois points qu'un relecteur peut vérifier :**

1. **La cible est la sortie d'un autre pipeline.** Les 80 cartes d'encre sont celles que
   le concours publie, récupérées telles quelles. Rien de notre chaîne n'entre dedans,
   donc la corrélation ne peut pas être un artefact partagé.
2. **Le confond de taille était réel et il est retiré.** L'emprise corrèle avec le
   critère (+0,384) *et* avec l'encre (+0,463) ; la corrélation **partielle** passe de
   −0,315 à **−0,382** — retirer le confond la **renforce**, ce qui est le contraire
   d'un effet de taille.
3. **Le seuil est défendu par un plateau, pas par un pic** : 15–25 % tiennent tous à
   p ≤ 0,001, 5 % ne fait rien (p = 0,054) et 30 % se dégrade. Un réglage sur-ajusté
   ferait un pic.

⚠ **Le confond qu'on ne lève pas, et qu'il faut écrire dans la soumission** : une carte
d'encre vide peut vouloir dire « la trace a raté la feuille » **ou** « ce papyrus est
vierge ». C'est un **tri de corpus**, jamais un diagnostic sur un segment isolé.

## 3ter. ⭐⭐ Le quatrième : le champ de correction (`20`), et le critère « ne saute pas de feuille »

Le dernier critère de la page est visuel et littéral : *« show visually that papyrus
fibers are visible on your output surface, and **it doesn't jump across sheets** »*.

`champ_correction.py` mesure ce saut fenêtre par fenêtre et le **montre** avec son
témoin à côté (`docs/images/20_champ_fort.png`, `20_champ_correction.png`).

| ce qu'on apporte | le chiffre |
|---|---|
| l'erreur d'une trace est **structurée**, pas du bruit | **98 segments sur 98**, deux rouleaux, battent leur propre témoin de mélange |
| **quelle réparation** vaut la peine | une translation n'enlèverait que **22,1 %** de l'erreur → le remède est un **gauchissement** |
| les segments qui **sautent** de feuille sont nommés | 1 sur 80 sur Scroll 1, avec son nom et son résiduel |

⚠ Et l'honnêteté qui doit accompagner la figure : sur le cas **médian** la différence
entre les deux panneaux **se voit mal**, ce qui est exactement ce que dit un rho de 0,31.
Les deux figures sont publiées, pas seulement la belle.

## 3quater. ⭐ Le cinquième : `tracecheck`, le paquet qui répond à « actually get used »

Un fichier, `numpy` et rien d'autre — ni `zarr`, ni `torch`, ni identifiants AWS. Il
découvre le volume de surface d'un segment depuis un alias de rouleau, lit **~300
chunks** (quelques mégaoctets, ~15 s) et rend les six grandeurs, chacune avec le rho qui
la défend. `selftest.py` en donne **16 contrôles hors ligne** avec leurs cas négatifs.

```
$ python3 tracecheck.py Scroll1 20230702185753 --voxel-um 2.4 --sheet-um 172.8
  material           68.5 %   <- strongest predictor of published ink (rho +0.54, n=80)
  rigid share        23.4 %   <- what a mesh translation would remove
  vs 173 um sheet pitch: 0.74 sheets  -> stays on its sheet
```

⚠ **Son README dit aussi ce qu'il NE fait pas** : il ne prédit pas la lisibilité, une
carte vide peut vouloir dire papyrus vierge, et `--sheet-um` **n'a pas de défaut** parce
que nous avons payé le chiffre emprunté. Un outil qui tait ses limites se fait jeter à la
première contradiction.

⚠ **La langue de l'outil est l'anglais**, celle des documents reste le français.
L'auteur a tranché que le français n'est pas un problème pour la soumission ; un outil
destiné à être *utilisé par d'autres* est un cas différent d'un document qui explique.

## 4. ⚠ Ce qui n'est PAS soumissionnable, et pourquoi

| | raison |
|---|---|
| **La direction des fibres** (`14`) | **ne valide pas** : rho −0,192 à n = 54, et le signe s'est inversé depuis n = 12. Le site en fait pourtant *le* critère visuel — donc l'idée est bonne et **notre mesure ne l'est pas** |
| **Le NON de la tâche D** (`06` §3.8) | scientifiquement propre, mais un prix récompense une amélioration. À citer comme **garde-fou**, pas comme contribution |
| **Les fusions en 3D** (`11`) | mesurées dans le volume, pas sur un maillage — rien en aval ne les consomme |
| **Le juge de langue calibré** (`09`) | utile ici, mais c'est de l'évaluation d'encre, et l'encre est *l'instrument*, pas l'ouvrage |

## 5. ⏳ Ce qui manque pour soumettre

1. ✅ **La généralité** — *fait* : **71 traces** sur PHerc0139 / PHerc1667 / PHerc0814
   (`07` §9), **80 segments** de profondeur, **99 champs de correction** sur deux
   rouleaux.
2. ✅ **Un paquet autonome** — *fait* : `src/tracecheck/`, un fichier, `numpy` seul,
   16 contrôles hors ligne.
3. ✅ **Une image** — *fait* : `12_profils_de_profondeur.png` (segment sain / hors feuille) et
   les deux figures de champ avec leur témoin.
4. ⚠ La **langue**. L'auteur juge que ce n'est pas un problème ; l'outil public est
   néanmoins en anglais. Noté une fois, et on n'y revient pas.
5. ✅ **Le texte** — brouillon écrit (`21`), résultats négatifs compris, chiffres gardés
   par `verifier_chiffres.py`.
6. ⚠⚠ **Et le tri de ce document est à refaire** — voir le §7. Deux choses l'ont périmé le
   2026-08-19 : la règle de `19` **ne réplique pas** hors de Scroll 1, et VC3D est
   construit, donc on **produit** au lieu de seulement juger. ⚠ **Une troisième le
   2026-08-20** (§7.4) : le classement des treize rouleaux est inversé par un
   échantillonnage plus dense, et trois candidats neufs portent sur **l'outillage de la
   communauté** plutôt que sur le papyrus.

## 6. Le lien avec le gros prix

Le Grand Prize 2027 (**800 000 $** en première place, 25 juin 2027) demande de dérouler
**entièrement** un des 13 rouleaux et d'y lire du texte. Nos outils sont des **juges**,
et un juge n'a rien à mesurer sur un rouleau non tracé — vérifié :
`PHerc0358/segments/` est **vide**.

Mais tout le reste y est publié : le volume (`[14744, 7783, 7783]` u8, chunks 128³ non
compressés, donc lisible par morceaux comme nos instruments le font déjà), les
prédictions de surface nnUNet, et le volume de winding `lasagna`.

> La trajectoire est donc en deux temps : **un juge que les autres utilisent**, puis
> **produire une trace** avec ce juge dans la boucle. Ce document ne couvre que le
> premier.


---

## 7. ⚠⚠ Ce document est périmé sur deux points, et il faut le dire

*(2026-08-19)*

### 7.1 Le candidat « solide » du §2 a perdu sa portée

`19` §12 : la règle qui écarte les segments pauvres en matière **ne réplique pas**. Testée
sur **110 segments** de trois autres rouleaux :

| corpus | n | voxel | étendue de la cible | rho |
|---|---:|---:|---:|---:|
| **Scroll 1** | 80 | 2,4 µm | 1,008 | **+0,539** |
| **PHerc0139** | 38 | **2,399 µm** | **1,628** | **−0,229** |
| PHerc1667 | 19 | 2,399 µm | 0,720 | +0,425 |
| PHerc0172 | 53 | 7,91 µm | 0,220 | −0,217 |

⚠ Ma première explication — un effet de plancher — couvrait **un corpus sur trois** :
PHerc0139 est à la même résolution que Scroll 1, a une étendue **plus grande**, et rend le
signe opposé. **La règle est une propriété du corpus publié de Scroll 1.**

⭐ Ce qui reste soumissionnable là-dedans est **plus honnête, pas moins** : sur Scroll 1,
`material` identifie une **classe d'échecs** (14 segments quasi vierges sur 80), et les
trois corpus où ça échoue sont publiés **avec** le résultat. Qui reprend la mesure sait
qu'elle doit être re-validée chez lui, au lieu de le découvrir après.

### 7.2 ⭐⭐ Et le §6 (« nos outils sont des juges ») n'est plus vrai

Il disait : *« un juge n'a rien à mesurer sur un rouleau non tracé »*. Depuis, VC3D est
construit et `24` a tracé `PHerc0358` — **8,48 cm² sur un rouleau du prix que personne
n'avait touché**.

Ça ouvre deux prix qui n'étaient pas dans ce document :

| prix | montant | ce qu'il faut | échéance |
|---|---:|---|---|
| **First Letters** | **50 000 $ × 10 rouleaux** | **10 lettres dans UNE zone de 4 cm²** | 25 juin 2027 |
| **Titre de PHerc. Paris 4** | **50 000 $** | l'image du titre, lisible par leurs papyrologues | 25 juin 2027 |

⭐ Et deux phrases de leur page changent le calcul :

> *« Sometimes ink is visible **directly in the flattened render, with no model at all**…
> **that by itself qualifies for the prize**. »*

> *(sur le titre)* *« …so finding it may take better methods, higher resolution, or
> **looking somewhere new**. »*

⚠ **Dix rouleaux sur treize n'ont aucun segment** (`23`). Ce n'est pas l'outil qui manque —
il est public — c'est de savoir par lequel commencer. `16` le dit : `PHerc0358`.

### 7.4 ⚠⚠ Un TROISIÈME point périmé, et trois candidats neufs *(2026-08-20)*

**Périmé** : le §7.2 finit par *« c'est de savoir par lequel commencer. `16` le dit :
`PHerc0358` »*. [`33`](33_la_carte_nest_pas_resolue.md) mesure que ce classement n'est pas
résolu — **0 des 78 paires séparée** — et la campagne dense l'a **inversé** : rho de
Spearman **−0,297**, les treize changent tous de rang, et `PHerc0800` devient le meilleur
point observé. ⚠ Ça n'invalide pas d'avoir commencé par `PHerc0358` ; ça invalide de dire
que **la mesure le désignait**.

**Et trois candidats neufs, qui portent sur l'outillage de la communauté elle-même** — donc
directement utilisables par elle, ce que le §2 de ce document classe comme le critère le
plus fort :

| candidat | pourquoi il est soumissionnable | source |
|---|---|---|
| ⭐⭐ **un verdict qui ne mesure rien** | `vc_tifxyz_selfcross` — officiel depuis le 4 août — rend `clean_of_transverse_self_intersection: true` avec **`pairs_tested: 0`** dès que `--maxedge` a jeté tous les quads, ce qui arrive **au réglage par défaut** sur un maillage à pas ≥ 60. Un portail bâti sur `--fail-on-crossing` laisse alors passer n'importe quelle surface, avec le code de sortie que le script attend. **Reproductible en deux commandes, et corrigeable en une ligne chez eux.** | [`34`](34_un_verdict_qui_ne_mesure_rien.md) |
| ⭐⭐ **le traceur est un tirage** | `vc_grow_seg_from_seed` rend un résultat différent à chaque exécution : **78 tirages, 13 rouleaux, 5 rouleaux où le VERDICT bascule** à paramètres strictement identiques, **0 reproductible**. Personne ne publie ni répétition ni barre d'erreur (`27` §2), et le papier du déroulage complet ne publie **aucun** taux d'erreur de traçage. ⭐ Et l'aire **ne signale pas** le mauvais tirage — on ne peut pas l'écarter sans le juger. | [`35`](35_le_tirage_sur_douze_rouleaux.md) |
| ⭐ **un compte n'est pas comparable entre deux pas** | le même maillage, décimé sans que sa géométrie change, passe de **240** croisements à 123, 72, 49. Toute table d'ablation qui compare des `step_size` par leur nombre d'auto-intersections compare des instruments de sensibilités différentes. | `34` §3 |

⚠ **Les trois sont des résultats sur des OUTILS, pas sur du papyrus.** C'est une force pour
un prix qui demande *« what would help : scan-quality metrics »* et dont la page insiste sur
la reproductibilité — et c'est une faiblesse s'ils cherchent des lettres. À présenter comme
ce qu'ils sont : de quoi **empêcher un résultat faux**, pas de quoi lire un rouleau.

⚠ Et le premier a une propriété que les autres n'ont pas : **il se corrige chez eux en une
ligne**, et il concerne un outil que le dépôt vient d'officialiser. C'est le candidat dont
l'utilité ne dépend d'aucune de nos hypothèses.

### 7.3 Ce que la soumission doit donc contenir

| ✅ à mettre | ❌ à ne plus prétendre |
|---|---|
| la mesure à distance : ~300 requêtes par segment, **0,9 h pour 800 rouleaux** | qu'une règle générale trie les corpus |
| les **quatre** corpus de `19`, échecs compris | que le seuil de 20 % vaille ailleurs |
| le **champ de correction** sur trois rouleaux, et que la translation est le mauvais remède | — |
| ⭐ **la première trace d'un rouleau du prix, condamnée par nos instruments avant le rendu** (`24`) | — |
| les résultats **négatifs** avec leur puissance | — |
