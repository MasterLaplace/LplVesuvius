# Ce que la littérature primaire dit — et le seuil de 1 µm

2026-08-19. `06` §0 notait deux papiers « à lire », depuis le 17 août. Ils ne l'avaient
jamais été. Les voici lus, et **l'un des deux change une décision**.

⚠ Les deux sont du **cœur de l'équipe** du concours — Paul Henderson écrit les deux, et
W. Brent Seales cosigne le second. Ce ne sont pas des travaux périphériques.

---

## 1. *Ink Detection from Surface Topography of the Herculaneum Papyri*

Angelotti, Nicolardi, Henderson, Seales — arXiv **2603.27698**, 29 mars 2026, publié
dans **Scientific Reports** (DOI `10.1038/s41598-026-58467-1`).
⚠ La version lue ici est le **preprint v1**, dont le champ *Comments* dit encore
« currently under review » : la version de revue peut différer.

**La thèse** : la **morphologie de surface** d'une région écrite porte assez de signal
pour distinguer l'encre du papyrus, **sans contraste d'absorption**. L'encre carbonée
laisse une **empreinte physique** et c'est ça qu'on détecte. ⚠ Pas un simple creux :
les auteurs mesurent que filtrer la seule rugosité **ne sépare pas** l'encre du support,
et concluent à *« a composite signal: surface roughness together with pressure-induced
deformations from ink deposition »*.

**Le matériel, et il faut le dire précisément** : profilomètre optique confocal
Sensofar S lynx 2, **0,34 µm** latéral, **8 nm** vertical, sur **3 papyrus ouverts
mécaniquement** — PHerc. 248 et 250, deux *scorze* découpées dans les années 1750 puis
grattées couche par couche au XIX siècle, et PHerc. 500P2, une pièce détachée.
**16 lettres en 14 échantillons**, régions d'environ **1,5 mm de côté**.

⚠ **Trois biais que le papier assume, et qui bornent ce qu'on peut en tirer** :
les lettres sont *« selected based on visible legibility and minimal physical damage »* ;
les masques de vérité viennent d'une **photographie en fond clair annotée à la main**,
donc l'encre devait être **déjà visible optiquement** — ce papier ne révèle aucune
écriture invisible ; et les surfaces mesurées sont exposées à l'air depuis ~200 ans, ce
que les auteurs signalent eux-mêmes (*« possible effacement on long-exposed opened
fragments »*).

### ⭐⭐ Le chiffre qui compte pour nous : **1 µm de résolution latérale**

⚠⚠ **Correction du 2026-08-19, deuxième passe.** La première version de ce document
annonçait **4 µm**, et ce nombre n'est **nulle part dans le papier**. Il a été écrit
depuis le résumé, sans ouvrir le corps de l'article. Le papier a été lu en entier
depuis, et sa cible est **quatre fois plus fine** — ce qui change la conclusion, pas
seulement le chiffre. Les trois phrases qui la portent, verbatim :

> *« On our dataset, reliable segmentation benefits from lateral sampling on the order
> of **1 µm or finer**. »* (Conclusion)

> *« Only models at or finer than **1.02 µm** exceed the Dice = 0.70 reference
> threshold. »* (légende du tableau 1)

> *« volumetric scans delivering effective isotropic resolution **at or below 1 µm**
> could be sufficient for morphology-based ink detection. »* (Discussion)

Les auteurs dégradent la résolution par moyennage de blocs et mesurent le DICE. Le
tableau 1 donne deux courbes, et **il faut les distinguer** — les confondre est
exactement ce qui produit un chiffre faux :

| taille de pixel | modèle **entraîné à cette résolution** | modèle **entraîné à 0,34 µm**, testé dégradé |
|---:|---:|---:|
| 0,34 µm | **0,890** | **0,899** |
| 0,68 µm | 0,817 | 0,881 |
| **1,02 µm** | **0,754** | 0,758 |
| 1,36 µm | 0,586 | 0,634 |
| 2,04 µm | 0,516 | 0,494 |
| 2,72 µm | 0,478 | 0,235 |
| 3,40 µm | 0,483 | **0,029** |
| 5,44 µm | 0,475 | **0,003** |
| 10,88 µm | 0,467 | **0,007** |

*(DICE médian ; seuil de référence 0,70 ; n = 14.)*

⚠ **Le plateau à ~0,47 de la colonne de gauche n'est pas un succès.** Un modèle
réentraîné à chaque résolution ne descend jamais sous 0,46 — mais il reste sous le
seuil de 0,70 dès 1,36 µm, et un DICE de 0,47 sur une tâche à deux classes est proche
de ce qu'une segmentation dégénérée rapporte. La colonne qui décrit **notre** situation
est celle de droite : un modèle appris sur du fin, appliqué à du grossier. Elle
**s'effondre à zéro** dès 3,40 µm.

⚠ Et la mesure la plus proche de la tomographie est une **troisième** colonne du papier,
non reproduite ici : les auteurs quantifient la hauteur en pas égaux au pixel latéral
pour émuler un voxel isotrope. Le DICE bouge alors d'au plus **0,026**. Autrement dit,
ce n'est pas la quantification verticale qui tue le signal, c'est bien
l'échantillonnage latéral.

⚠⚠ **Et ça se heurte à `16` de plein fouet**, bien plus durement que la première
version ne le disait :

| corpus | résolution | face à la cible de ~1 µm |
|---|---:|---|
| volumes de **surface** Scroll 1 / PHerc0139 / PHerc1667 | **1,129 / 2,399 / 2,400 µm** | ⚠ le plus fin est **au-dessus** de 1,02 µm, de peu ; les autres sont à 2,4 µm |
| **les 13 rouleaux du prix** (volume) | **8,640–9,362 µm** | ❌ **facteur 8,6 à 9,4** — et au-delà du point d'effondrement de 3,40 µm |

> ⭐ **Conséquence pour First Letters** : sur un rouleau du prix, espérer voir l'encre
> *dans le rendu, sans modèle* — ce que le règlement autorise explicitement — n'est pas
> une question de chance. À 9 µm on est **neuf fois** au-dessus de la résolution où
> cette voie fonctionne, et cinq fois au-delà de celle où elle rend zéro. Ça ne ferme
> pas First Letters (leur cible vaut pour la voie **topographique**, pas pour un
> détecteur appris sur du CT, qui exploite autre chose que le microrelief), mais ça dit
> **pourquoi** c'est dur, et ça donne un argument chiffré à qui demanderait un rescan.

⚠ **La transposition au CT est conditionnelle, et les auteurs insistent sur un mot.**
*« **If** volumetric imaging of closed scrolls can deliver comparable **effective**
resolution at the layer surfaces […] then morphology-only detection **becomes
plausible** inside sealed scrolls. We emphasize “effective” rather than nominal pixel
size because point-spread, partial-volume effects, scattering, reconstruction
regularization, and other artifacts can all diminish resolvable detail. »* Un scan
annoncé à 7,91 µm a donc une résolution **effective** moins bonne que 7,91 µm — l'écart
réel est pire que le rapport des nombres nominaux.

⚠ **Ce que le papier ne prétend pas** : *« This trend reflects our dataset and is not
claimed as a universal bound »*, et *« The exact requirement will depend on data
quantity and diversity, signal-to-noise, model architecture, and critically on the
amount and preservation state of ink »*. La cible de 1 µm est une **observation sur 16
lettres de trois papyrus**, pas une loi.

### ⚠⚠ Et le résultat que le résumé ne met pas en avant : ça ne généralise pas encore

Les auteurs font un **leave-one-papyrus-out** à 0,34 µm — entraîner sur deux papyrus,
tester sur le troisième. C'est la question qui décide si la méthode est un outil ou une
démonstration :

| papyrus retiré | n | DICE médian |
|---|---:|---:|
| PHerc. 248 | 5 | 0,757 |
| PHerc. 250 | 5 | 0,817 |
| **PHerc. 500P2** | 4 | **0,475** |
| **tous held-out, moyenne** | **14** | **0,691** |

**La moyenne poolée, 0,691, passe sous le seuil de 0,70 que le papier utilise
lui-même** — et sur un papyrus des trois, le DICE tombe à 0,475, soit ce que donne un
pas latéral de 2 à 10 µm sur un papyrus *déjà vu*. Phrase exacte : *« indicating
heterogeneous cross-manuscript transfer on this dataset »*. Les auteurs bornent
eux-mêmes : *« each papyrus contributes only 4–5 samples; thus, cross-papyrus estimates
are preliminary »*.

> ⭐ **Pour nous, ça change la lecture de la voie topographique.** Elle ne bute pas
> seulement sur la résolution des scans — elle n'a pas encore montré qu'elle transfère
> d'un manuscrit à l'autre, sur des données **quinze fois plus fines** que les nôtres et
> sur des surfaces **déjà lisibles à l'œil**. Ce n'est pas une porte fermée, c'est une
> piste beaucoup plus jeune que son résumé ne le laisse croire.

### ⚠ Ce que ça N'invalide PAS chez nous, et la différence est nette

Notre instrument de profondeur (`12`, `25` §5) et ce papier mesurent **deux choses
différentes**, et il faut le dire avant qu'un lecteur croie à un doublon :

| | leur mesure | la nôtre |
|---|---|---|
| donnée | profilométrie optique, papyrus **ouvert** | volume CT, rouleau **fermé** |
| grandeur | le **relief** de la face écrite | la **distribution de matière le long de la normale** |
| ce qu'elle sert à faire | **détecter l'encre** | juger si la **trace** suit la feuille |
| a besoin d'un modèle appris | oui | **non** |

⚠ Le point de contact réel est leur résultat de dégradation. Phrase exacte du résumé —
la première version de ce document en donnait une **paraphrase entre guillemets**, ce
qui est une faute de citation : *« Diminishing segmentation performance with decreasing
lateral resolution provides insight into the characteristic spatial scales that must be
resolved on our dataset to exploit the morphological signal. »* C'est la même forme que notre `12` §H2 (un d′ **baisse** quand on résout
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
