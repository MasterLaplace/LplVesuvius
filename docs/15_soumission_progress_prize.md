# Ce qui est soumissionnable, et ce qui ne l'est pas

2026-08-18. Échéance Progress Prize : **31 août 2026, 23 h 59 Pacific** — dans **13
jours**. Ce document trie ce qu'on a **contre les critères écrits sur la page `Prizes`
du miroir**, pas contre une impression.

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

## 4. ⚠ Ce qui n'est PAS soumissionnable, et pourquoi

| | raison |
|---|---|
| **La direction des fibres** (`14`) | **ne valide pas** : rho −0,192 à n = 54, et le signe s'est inversé depuis n = 12. Le site en fait pourtant *le* critère visuel — donc l'idée est bonne et **notre mesure ne l'est pas** |
| **Le NON de la tâche D** (`06` §3.8) | scientifiquement propre, mais un prix récompense une amélioration. À citer comme **garde-fou**, pas comme contribution |
| **Les fusions en 3D** (`11`) | mesurées dans le volume, pas sur un maillage — rien en aval ne les consomme |
| **Le juge de langue calibré** (`09`) | utile ici, mais c'est de l'évaluation d'encre, et l'encre est *l'instrument*, pas l'ouvrage |

## 5. ⏳ Ce qui manque pour soumettre

1. ⭐⭐ **La généralité** — l'instrument est validé sur **un** rouleau (Scroll 1, 54
   segments). Le passer sur PHerc1667, PHerc0139 et PHerc0814 le rendrait défendable.
   *(lancé)*
2. **Un paquet autonome** : un script, un README, un exemple qui tourne sur une clé S3
   publique sans rien télécharger. C'est le critère *« actually get used »*.
3. **Une image** : le site insiste partout sur la preuve visuelle. Montrer un segment
   sain et un segment hors feuille, côte à côte, avec leur profil.
4. ⚠ La **langue**. L'auteur juge que ce n'est pas un problème ; noté une fois, et on
   n'y revient pas.

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
