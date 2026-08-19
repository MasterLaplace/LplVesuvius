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
>   are visible on your output surface, and it doesn't jump across sheets** »*

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
| l'erreur d'une trace est **structurée**, pas du bruit | **99 segments sur 99**, deux rouleaux, battent leur propre témoin de mélange |
| **quelle réparation** vaut la peine | une translation n'enlèverait que **21,7 %** de l'erreur → le remède est un **gauchissement** |
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
2. ✅ **Un paquet autonome** — *fait* : `tracecheck/`, un fichier, `numpy` seul,
   16 contrôles hors ligne.
3. ✅ **Une image** — *fait* : `profondeur_deux_cas.png` (segment sain / hors feuille) et
   les deux figures de champ avec leur témoin.
4. ⚠ La **langue**. L'auteur juge que ce n'est pas un problème ; l'outil public est
   néanmoins en anglais. Noté une fois, et on n'y revient pas.
5. ⏳ **Le texte de la soumission lui-même** — il n'est pas écrit. C'est désormais le seul
   reste, et il ne demande aucune machine.

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
