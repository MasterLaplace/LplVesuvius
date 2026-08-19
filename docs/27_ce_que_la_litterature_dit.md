# Ce que la littérature primaire dit — et le seuil de 4 µm

2026-08-19. `06` §0 notait deux papiers « à lire », depuis le 17 août. Ils ne l'avaient
jamais été. Les voici lus, et **l'un des deux change une décision**.

⚠ Les deux sont du **cœur de l'équipe** du concours — Paul Henderson écrit les deux, et
W. Brent Seales cosigne le second. Ce ne sont pas des travaux périphériques.

---

## 1. *Ink Detection from Surface Topography of the Herculaneum Papyri*

Angelotti, Nicolardi, Henderson, Seales — arXiv **2603.27698**, 29 mars 2026.

**La thèse** : la **morphologie de surface** d'une région écrite porte assez de signal
pour distinguer l'encre du papyrus, **sans contraste d'absorption**. L'encre carbonée
laisse une **empreinte physique** — un creux — et c'est ça qu'on détecte.

**La méthode** : profilométrie optique 3D sur des papyri **ouverts mécaniquement**, puis
un modèle appris sur ce relief.

### ⭐⭐ Le chiffre qui compte pour nous : **4 µm de résolution latérale**

Les auteurs dégradent volontairement la résolution et mesurent l'effondrement du DICE.
Ils en tirent une **cible de résolution pour la tomographie des rouleaux fermés** :
**~4 µm latéraux**.

⚠⚠ **Et ça se heurte à `16` de plein fouet.** Les treize rouleaux du Grand Prize sont
scannés à **8,640–9,362 µm** — soit **deux fois trop grossier** pour cette voie.
Autrement dit :

| corpus | résolution | sous la cible de 4 µm ? |
|---|---:|---|
| volumes de surface Scroll 1 | **1,129 / 2,400 µm** | ✅ oui |
| PHerc0139, PHerc1667 (surface) | 1,129 / 2,399 µm | ✅ oui |
| **les 13 rouleaux du prix** (volume) | **8,640–9,362 µm** | ❌ **non, d'un facteur 2,2** |

> ⭐ **Conséquence pour First Letters** : sur un rouleau du prix, espérer voir l'encre
> *dans le rendu, sans modèle* — ce que le règlement autorise explicitement — n'est pas
> une question de chance mais de **résolution**, et le papier chiffre le manque. Ça ne
> ferme pas la porte (leur cible vaut pour la voie topographique, pas pour un détecteur
> appris sur du CT), mais ça dit **pourquoi** c'est dur, et ça donne un argument mesuré à
> qui demande un rescan plus fin.

### ⚠ Ce que ça N'invalide PAS chez nous, et la différence est nette

Notre instrument de profondeur (`12`, `25` §5) et ce papier mesurent **deux choses
différentes**, et il faut le dire avant qu'un lecteur croie à un doublon :

| | leur mesure | la nôtre |
|---|---|---|
| donnée | profilométrie optique, papyrus **ouvert** | volume CT, rouleau **fermé** |
| grandeur | le **relief** de la face écrite | la **distribution de matière le long de la normale** |
| ce qu'elle sert à faire | **détecter l'encre** | juger si la **trace** suit la feuille |
| a besoin d'un modèle appris | oui | **non** |

⚠ Le point de contact réel est leur résultat de dégradation : *« segmentation performance
degrades with lower lateral resolution, revealing characteristic spatial scales that must
be resolved »*. C'est la même forme que notre `12` §H2 (un d′ **baisse** quand on résout
plus de structure) et que le balayage de fenêtre de `25` §5. **Deux mesures indépendantes
disent que la résolution décide** — à citer comme convergence, pas comme priorité.

## 2. *Virtually Unrolling the Herculaneum Papyri by Diffeomorphic Spiral Fitting*

Paul Henderson — arXiv **2512.04927**, 4 décembre 2025.

**La thèse** : la **première** méthode descendante qui ajuste automatiquement un modèle de
surface à un CT de rouleau sévèrement abîmé. Un modèle paramétrique explicite de la
géométrie déformée est ajusté aux prédictions du réseau, et la surface obtenue est
**garantie être une seule nappe 2D continue** — *y compris là où elle n'est pas détectable
dans le CT*.

⭐ C'est exactement la famille « spiral fitting » que `00` §2 décrit, et la garantie citée
est ce que `00` §2 appelle *« immunisé au sheet switching par construction »*. Le papier
le formule mieux que nous : la continuité n'est pas un résultat, c'est une **contrainte du
modèle**.

**Résultats** : deux rouleaux à haute résolution, « de larges régions » déroulées, et une
performance **supérieure à la seule méthode automatique existante** adaptée à ces données.
⚠ Les chiffres détaillés sont dans le corps du PDF, qui dépasse la limite de récupération
d'ici — **à extraire dans une prochaine session**, c'est le premier reste de ce document.

### ⚠⚠ Ce que ça dit de notre journée

`26` a mesuré que la trajectoire de `vc_grow_seg_from_seed` ne répond ni aux champs de
direction, ni aux grilles de normales, ni à leurs poids — seulement à `step_size` et à la
prédiction. Le papier de Henderson attaque le **même problème par l'autre bout** : au lieu
de contraindre un traceur ascendant, il impose la continuité **dans le modèle**.

> ⭐ Ce n'est pas une contradiction, c'est la carte du §2 de `00` qui se vérifie : *l'un
> porte une contrainte globale sans souplesse locale, l'autre l'inverse*. Nos trois
> négatifs disent que le second **ne se laisse pas contraindre par ce qu'on lui donne**.

---

## 3. Ce que la lecture complète des documents a trouvé d'autre

⚠ Un `grep` attrape les marqueurs, pas ce qui a été laissé en passant. Les 8 310 lignes
de `docs/` et de la passation ont donc été lues. Reste ouvert, dans l'ordre de valeur :

| # | quoi | où c'est dit |
|---|---|---|
| **1** ⭐⭐ | **appliquer la correction — un GAUCHISSEMENT — et montrer le gain** | `00` §9.3, `18` J6, `22` R2. C'est le dernier ⏳ du « vrai produire », et le seul obstacle écrit (« la chaîne maillage → rendu n'est pas ici ») **est tombé** : VC3D est construit |
| 2 | extraire les chiffres du papier spiral fitting | §2 ci-dessus |
| 3 | publier la table de qualité de trace, et le dépôt | `22` Q3, `15` §5, `21` |
| 4 | `06` §2.3 « vérifier 1.11 avec le vrai ombilic » | ⚠ **périmé** : `18` M1 l'a clos **sans** l'ombilic, mesuré à 1,75 % contre un cv de 1,8 % |
| 5 | `06` §3bis C « un second rouleau » | ⚠ **périmé** : fait quatre fois (`19` §11) |
| 6 | `06` §3bis D « boucler la métrique sur le résultat » | ⚠ **périmé** : c'est la mesure 3.8, et la réponse est **NON** |

⭐ **Le reste nº 1 est le seul qui vaille un lot.** Les trois « périmés » sont corrigés
ci-dessous plutôt que laissés à piéger le prochain lecteur.
