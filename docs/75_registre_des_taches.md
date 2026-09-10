# 75 — Registre des tâches, après `69`, `72`, `73` et `74`

> Ouvert le 2026-09-03. Ce fichier existe parce que quatre documents ont déposé des tâches en
> même temps et qu'un registre éparpillé dans quatre prose est un registre qu'on ne tient pas.
> Il remplace la liste de `HANDOFF` §7 pour tout ce qui a été ouvert depuis `68`.
>
> ⚠⚠ **La règle de tri est le cadrage de `HANDOFF` §0–1**, et rien d'autre : *le but est le
> déroulement ; l'encre est la règle graduée, pas l'ouvrage.* Une tâche est classée par ce
> qu'elle fait avancer, pas par son intérêt.
>
> **Trois colonnes, et une seule compte** : ce qui remplace le pinceau.

---

## 0. Le tri, en une table

| | tâches | ce que ça fait avancer |
|---|---:|---|
| **A — remplacer le pinceau** | 8 (dont **3 faites**) | le prix. Un prédicat d'identité, son témoin, son déploiement |
| **A′ — ce qui reste sous les ✅** | 13 lignes | ⚠ la section qu'un ✅ fait sauter |
| **B — l'article** | 5 (dont **4 faites**) | une publication, et la crédibilité des mesures qui la portent |
| **C — la règle graduée** | 3 | savoir si une carte d'encre peut **valider** un déroulage. Borné à trois semaines |
| **D — dette** | 3 | ce qui pourrit si on n'y touche pas |

⚠ **C est borné exprès.** `73` §3.1 défend qu'une règle doit d'abord montrer qu'elle lit
quelque chose, et l'argument est bon : `46` mesure que le détecteur rend **plus** de dispersion
sur une surface sans face (0,7111) que sur une face (0,5894). Une règle qui marque autant sur
le vide que sur le plein ne valide aucun déroulage. Mais c'est un **étalonnage**, il se fait
une fois, et il s'arrête.

---

## A. Remplacer le pinceau

> Le prédicat du pipeline de référence est cité dans l'article : *« regions judged
> geometrically consistent with a single sheet »*. C'est un prédicat d'**identité**. Le dépôt
> a construit la **présence** (α, relief en fenêtre étroite) et le **placement** (`offset`).
> **L'identité manque, et c'est là que se gagne le prix.**

### ~~A1~~ ✅ — lire les indices de spire publiés — **FAIT le 2026-09-04** (`76`)

**Le référent est inventorié** (`les_indices_de_spire.py`, `74` §3) : 101 segments indexés sur
3 rouleaux, dont **81 spires consécutives sans aucun trou**.

**Et son sens est mesuré** (`le_sens_des_indices.py`, `76`) : `w` compte **du centre vers
l'extérieur**, dans **95,0 %** de 57 510 cellules (hauteur, angle) de `PHerc0139`. La
comparaison est **appariée** — même hauteur, même angle, centre ajusté sur l'union — parce
qu'un rouleau écrasé n'a pas de rayon absolu et que son axe erre de 2,6 mm sur 30 mm.

⭐⭐ **Trois choses tombées avec, qu'on ne cherchait pas :**

1. un **écart inter-feuilles qui ne dépend d'aucun paramètre de traceur** : **154,1 µm**, à
   comparer aux 113 µm de l'article qui bougent avec `neighbor_step` (→ **B3**) ;
2. l'**étalon d'aire** que A5 réclamait, et il était publié : une spire approuvée fait
   **38,4 cm²** médian, soit **×6,4** le point fixe de 6,02 cm², et **même la plus petite le
   dépasse** ;
3. ⚠⚠ **le référent a des défauts** : `w045`/`w046` sont **la même surface** (0,0 µm, confirmé
   par deux méthodes indépendantes) et `w041`/`w042` sont à une demi-feuille. **2 paires sur
   36** — de quoi faire passer un bon prédicteur pour un prédicteur à 94 % si on les compte
   comme des échecs du prédicteur.

~~⚠ Restant sur A1 : `PHerc0172` n'est pas mesuré.~~ ✅ **Fait le même jour** — 95,1 % contre
95,0 %, donc le sens est une convention du **projet** et pas du rouleau. Son meta étant
dépouillé, son voxel est lu dans le chemin du maillage et validé contre les scans publiés.

### ~~A2~~ ✅ — le prédicat d'identité — **FAIT le 2026-09-04** (`77`), par une autre voie

⭐⭐⭐ **Un prédicat d'identité existe**, adossé au référent plutôt qu'au champ d'orientation :
un **champ d'enroulement** interpolé entre les 37 spires approuvées de `PHerc0139`, et la
grandeur qui décide est l'**avance d'indice sur un tour**.

| surface | avance par tour | p10 | p90 |
|---|---:|---:|---:|
| vraie spire | **−0,005** | −0,170 | **+0,230** |
| saut d'**1** feuille | **1,103** | **0,753** | 1,479 |
| saut de 2 | 1,962 | 1,369 | 2,517 |
| saut de 3 | 2,851 | 2,314 | 3,300 |

**Les deux populations ne se recouvrent pas** (+0,230 contre 0,753) et l'avance **compte** les
feuilles. Validation à spire exclue ; témoins **construits** à chaque position.

⚠⚠⚠ **Mais c'est vrai de `PHerc0139` et FAUX de `PHerc0172`** (`77` §7) : la rampe se reproduit
(0,02 → 1,07 → 2,00 → 2,98) mais les populations s'y **recouvrent**, à tout niveau d'agrégation
testé. Le prédicat **mesure et rapporte** désormais sa propre applicabilité, et le contrôle est
asserté dans les **deux** sens.

⚠⚠ **Et une tranche isolée ne suffit JAMAIS**, sur aucun des deux rouleaux. La séparation du
§2 est celle de la spire entière. C'est la mesure de ce que `42` disait qualitativement — *des
régions, pas des points* — et elle en donne la taille : **2 tranches** sur `PHerc0139`.

⭐⭐⭐ **La cause est TROUVÉE, en regardant** (`77` §8, consigne de l'auteur) : un **trou
angulaire** entre 330° et 360° dans les spires extérieures de `PHerc0172` — densité **3 points
par cellule contre 286**, donc de la matière **absente**. L'écarter restaure la séparation
(16 tranches) ; écarter autant de secteurs **sains** ne restaure rien. Coût : **8 % de la
circonférence**.

⚠⚠ **Et mes deux premières explications étaient fausses**, toutes deux attrapées par une
mesure ou un témoin : « couture » (réfutée par la densité et par le fait que 7 spires sont
intactes) et « étendre l'arc par contiguïté » (le témoin à compte égal a mordu).

⭐⭐⭐ **Validation croisée** : les deux seules positions qui n'avancent pas sont **exactement**
les deux défauts que `76` avait trouvés par une méthode qui ne partage rien avec celle-ci.

⚠ **Ce qui reste de A2, et c'est ce qui déploie** : ce prédicat a besoin du référent. Le champ
dérivé du **volume** (résidus d'orientation sur `normal-grids` + `m7`, `69` A2) répondrait
**sans** référent — c'est lui qui sortirait de la bande publiée. Les trois raisons de `73` §1
qui rouvraient la question restent valides et non testées.

### A2 bis ⭐⭐⭐ — le champ d'identité SANS référent — **l'entrée est INVENTORIÉE le 2026-09-05**

> Mesure : `src/nappe/le_champ_de_fibres.py` (13 contrôles),
> `docs/mesures/le_champ_de_fibres.json`.
>
> ```
> uv run python src/nappe/le_champ_de_fibres.py --json docs/mesures/le_champ_de_fibres.json
> ```

⭐ **Cinq rouleaux publient leur axe** (`78`), dont `PHerc0139`. Mais `78` §4 mesure aussi que
**l'axe seul ne débloque rien** : erreur d'indice **44,5 feuilles** pour la dispersion radiale
d'une spire, **11,36** pour le modèle d'Archimède, contre **0,088** pour le champ bâti sur les
spires. La forme des spires vaut un facteur **130**, et c'est elle qu'un champ dérivé du volume
devra retrouver.

⚠ Ce que le dépôt sait déjà et qui borne l'espoir (`26` §7) : les `.normal-grids` publiées sont
**dérivées de la prédiction** que le traceur suit déjà. Un champ bâti dessus hériterait de la
prédiction, pas d'une information neuve.

### ⚠⚠⚠ L'autre entrée, celle que `78` §2 annonçait — vérifiée, et sa description était fausse

`78` §2 renvoyait vers `representations/predictions/fibers/`, *« publié pour `PHerc0139` en
`nx`/`ny`/`nz` »*. **Il n'y a pas de `nz`** : le préfixe publie **trois** canaux — `nx`, `ny`,
`presence` — et le manifeste `.lasagna.json` n'en déclare pas d'autre, alors que `inference.json`
annonce `artifact_kind: fiber3d-prediction` et `output_channels = 7`.

⭐⭐ **Mais ce n'est PAS le champ 2D contre lequel `26` §7 met en garde**, et c'est mesuré sur
**trois** fenêtres portant de la matière plutôt que supposé :

| fenêtre (chunk) | présence | $n_x^2+n_y^2$ médian | max | $\lvert n_z\rvert$ impliqué |
|---|---:|---:|---:|---:|
| (71, 36, 14) | 60,2 % | **0,797** | 1,014 | 0,451 |
| (74, 39, 28) | 57,2 % | **0,806** | 1,014 | 0,441 |
| (35, 24, 35) | 50,4 % | **0,309** | 1,013 | 0,831 |

La somme n'est **jamais collée à un**, donc ces deux canaux sont la **projection d'un vecteur à
trois composantes** ; la troisième se récupère **en module**. ⚠ Le **signe** est définitivement
perdu — une racine carrée rend un module. Pour un nombre d'enroulement ça peut suffire, une
normale et son opposée décrivant la même feuille, mais ça se dit plutôt que se découvre.

⚠ **L'encodage n'est pas deviné** : la somme plafonne à **1,013–1,014** partout, soit exactement
l'arrondi d'une quantification sur huit bits. Un facteur d'échelle faux l'aurait fait plafonner à
2, à 4 ou à 0,25 — et « le champ n'est pas unitaire » aurait alors porté sur notre lecture.

### ⚠⚠ Ce qui borne vraiment `A2 bis` : la RÉSOLUTION, pas le `nz` manquant

Le **niveau 0 n'est pas publié**. Les seuls présents sont **3 et 4** :

| niveau | µm/cellule | cellules par pas de feuille (~150 µm) |
|---|---:|---:|
| 3 (le plus fin publié) | **19,2** | **7,8** |
| 4 | 38,4 | 3,9 |
| 6 (pour mémoire) | 153,5 | **0,98** — deux feuilles partagent une cellule |

Huit cellules par pas suffisent à **voir** une feuille et pas à en **séparer** deux qui se
touchent — or c'est exactement là que le déroulage échoue. C'est une contrainte sur ce qu'`A2 bis`
peut espérer, pas un défaut du champ.

### ⚠⚠⚠ Et la question qui décide : ce champ compte-t-il des feuilles ? **Mesuré : non**

Un nombre d'enroulement **compte des feuilles**. Si le champ ne les sépare pas radialement, il ne
peut pas les compter, quelle que soit la qualité de son orientation. Le long d'un rayon tiré depuis
**l'axe publié** (391 points annotés, `78`), avec son **contrôle tangentiel** :

![le champ publié compte-t-il des feuilles ?](images/75_le_champ_de_fibres.png)

*Figure : `src/figures/figure_le_champ_de_fibres.py` (9 contrôles).*

```
uv run python src/figures/figure_le_champ_de_fibres.py --sortie docs/images/75_le_champ_de_fibres.png
```

*⚠ Le trait vert marque **un pas de feuille**. Chaque pic mesuré est loin à sa droite, et sur deux
panneaux sur trois c'est la courbe **grise** — le contrôle — qui oscille le plus fort.*

| fenêtre | rayon | période **radiale** | autocorr. radiale | autocorr. **tangentielle** |
|---|---:|---:|---:|---:|
| (71, 36, 14) | 936 cellules | **441 µm** | +0,245 | **−0,069** ✅ sépare |
| (74, 39, 28) | 949 | **422 µm** | +0,302 | **+0,311** ❌ |
| (35, 24, 35) | 500 | **307 µm** | +0,237 | **+0,397** ❌ |

⚠⚠ **Le contrôle tangentiel est ce qui rend la mesure lisible** : une feuille est une *surface*,
donc elle se répète **en travers** et pas **le long**. Une périodicité radiale n'est une feuille
que si la même mesure prise perpendiculairement est plus faible. Elle ne l'est que sur **une
fenêtre sur trois**.

⚠⚠ **Et là où une période radiale apparaît, elle vaut 307 à 441 µm** — soit **2 à 3 pas de
feuille** (~150 µm), jamais un. C'est ce qu'on attend d'un champ dont la résolution *effective*
est plus grossière que sa grille : il voit des **groupes** de feuilles, pas des feuilles.

⚠ **Deux explications alternatives écartées par la mesure, pas par l'argument.** (1) Le moyennage
en profondeur aurait pu effacer la structure si les feuilles penchent : mesuré sur **1, 8 et 64**
tranches, l'écart de période est de **0 à 2 cellules** — ce n'est pas le lissage. (2) Le détecteur
de période lui-même : ma première version prenait le **maximum global** de l'autocorrélation, qui
pour un signal lisse est toujours son plus petit décalage — les trois fenêtres rendaient
« 2 cellules » dans les deux directions, c'est-à-dire la largeur de lissage du champ et **rien du
tout** sur les feuilles. Corrigé en cherchant le premier maximum **local après le passage sous
zéro**, qui est la définition d'un retour.

### ⚠ Et la porte de sortie évidente est fermée, par deux raisons indépendantes

`PHerc0139` publie un **second** champ d'orientation, sous `representations/predictions/lasagna/`,
avec deux canaux que `fibers/` n'a pas : **`cos`** et **`grad_mag`**. Le nom `cos` suggère
exactement la composante manquante — donc il a été testé par **identité** et non par son nom : si
`(n_x, n_y, \cos)` est un vecteur unitaire, la somme de leurs carrés vaut un.

| mesuré sur `lasagna`, niveau 4 | valeur |
|---|---:|
| $n_x^2+n_y^2$ | 0,520 |
| $n_x^2+n_y^2+\cos^2$ | **0,853** médiane, p90 **1,356**, **max 1,936** |

**Un vecteur unitaire plafonnerait à l'arrondi près.** `cos` est donc autre chose, et aucun
raisonnement sur son nom ne le rattrape.

⚠ Et ce préfixe est de toute façon **plus grossier** : ses `nx`/`ny` ne descendent qu'au **niveau
4**, soit **3,9 cellules par pas** contre 7,8 pour `fibers`.

> **Conséquence pour `A2 bis`** : l'entrée que `78` §2 désignait ne peut pas, **telle qu'elle est
> publiée**, porter un nombre d'enroulement. Ce n'est pas le `nz` manquant qui bloque — il se
> récupère en module — c'est que le champ **ne distingue pas deux feuilles voisines**, et l'autre
> produit publié est encore plus grossier. Ce qui reste possible : demander le **niveau 0** à son
> producteur (il existe chez lui — `output_channels = 7` le dit), ou construire l'enroulement sur
> autre chose que ces champs.

### A2 ter — le test d'identité par les résidus (ex-H5 de `69`, révisée par `73` §1)

*Le champ déplié assigne-t-il un entier constant le long de chaque spire publiée, et des
entiers consécutifs à deux spires consécutives ?*

Trois choses que `73` a établies et qui rendent la question ouverte alors qu'on la croyait
fermée :

1. `17` a testé la marche de phase contre les **auto-intersections** de `windcheck`
   (confirmé à la source, `74` §1) — pas contre des sauts de spire. Son négatif ne porte pas
   sur cette question.
2. La grandeur de `17` est **locale**, sur un champ `lasagna` dont la période vaut 3 à 7 fois
   le pas. Un résidu est une **intégrale de boucle** feuille-à-feuille.
3. ⚠ Les `nx`/`ny` de `lasagna` sont un champ **2D** (`26` l'a payé) : le résidu se calcule sur
   les grilles `xy`/`xz`/`yz` des `normal-grids`, jamais sur `lasagna` complété d'un `z` forcé.

**Ce qui la ferait échouer, énoncé d'avance** : des résidus distribués comme le bruit de `m7`
et sans rapport avec les bords de spire. Alors l'identité doit venir d'ailleurs — la coupe à
$K$ surfaces couplées (`69` §3.3), qui s'engage sur une feuille par construction.

### ⚠⚠⚠ A2 ter est BORNÉE par le pas de la grille, et ce n'est pas le bruit de `m7`

> Mesure : `src/nappe/le_pas_de_la_grille.py` (17 contrôles, 4 sondes qui mordent), le
> 2026-09-05. ⚠ Faite **avant** d'intégrer quoi que ce soit — c'est le piège nº 27 du dépôt
> appliqué à un autre produit : *trouver la matière avant de sonder.*

`PHerc0139` est le bon endroit pour ce test et le seul : il publie **à la fois** les 37 spires
indexées qui servent de référent et des `normal-grids`. ⚠ `PHerc0172`, l'autre rouleau à
indices, **n'en publie aucune**.

Le produit déclare son pas d'échantillonnage, **deux fois et d'accord** — `grid-step: 64` dans
son `metadata.json`, et `0x40` dans l'en-tête binaire de chaque `.grid` :

| rouleau | pas de grille | en µm | **écarts inter-feuilles par cellule** | pas maximal utile | résout ? |
|---|---:|---:|---:|---:|:---:|
| `PHerc0139` | 64 vx | 599 | **3,89** | 8,23 vx | **NON** |
| `PHerc0358` | 64 vx | 599 | **3,99** | 8,01 vx | **NON** |

![le peigne d'echantillonnage contre le reseau de feuilles](images/75_le_pas_de_la_grille.png)

Figure : `src/figures/figure_le_pas_de_la_grille.py`, depuis
`docs/mesures/le_pas_de_la_grille.json`.

```
uv run python src/figures/figure_le_pas_de_la_grille.py
```

⭐⭐ **La bande du bas est le contrôle, et sans elle la figure ne prouverait rien** : le *même*
réseau, échantillonné à la demi-période, est traversé par **39** points là où le produit publié
en pose **6**. Ce n'est donc pas « le réseau est trop fin pour être échantillonné », c'est
« ce produit-là l'échantillonne trop grossièrement » — deux énoncés que la bande du haut seule
confond.

⭐⭐⭐ **Une cellule de la grille couvre presque QUATRE feuilles.** Or un résidu est une
intégrale de boucle **feuille à feuille** : la grandeur intégrée est $\nabla\psi$, dont la
norme vaut $2\pi/b$ avec $b$ le pas local. Un champ échantillonné à quatre feuilles par cellule
ne porte pas ce gradient — **il est replié**.

⚠⚠ Et la borne n'est pas un seuil choisi : c'est **Nyquist**, deux échantillons par période,
donc un pas de grille d'au plus une demi-période. Ici **8,23 voxels** contre les 64 publiés,
soit **7,8 fois trop grossier**. Prendre un pas plus grand ne dégrade pas la mesure, il
l'**alias** — et un gradient replié rend un résidu qui n'a aucun rapport avec la feuille.

```
uv run python src/nappe/le_pas_de_la_grille.py \
    --json docs/mesures/le_pas_de_la_grille.json
```

⭐ **C'est la même classe de borne que celle qui a fermé `A2 bis`** — *« ce qui borne vraiment
A2 bis, c'est la RÉSOLUTION, pas le `nz` manquant »* — sur un **autre produit** et pour une
autre raison : là c'était le niveau de pyramide d'un champ de fibres, ici c'est le pas
d'échantillonnage d'un champ de normales. Deux produits d'orientation publiés, deux fois trop
grossiers pour compter des feuilles.

⚠ **Ce que ça n'établit pas** : que les grilles soient inutiles, ni que le test soit
impossible. Il dit qu'**il ne se monte pas sur ce produit-là**. La sortie est déjà nommée par
[`26`](26_le_champ_de_direction.md) §7 : `vc_gen_normalgrids -i <volume.zarr> -o sortie/`
génère des grilles **depuis un volume** plutôt que depuis une prédiction — et rien n'oblige à
garder le pas de 64. ⚠⚠ C'est un gros calcul, et il faut le dire : à un pas de 8 voxels le
produit serait **512 fois plus volumineux** que les 10,4 Go inventoriés par `26`.

⚠ Et la panne annoncée d'avance — *« des résidus distribués comme le bruit de `m7` »* — n'est
**pas** ce qui bloque, ni écartée pour autant : elle reste à tester le jour où une grille assez
fine existera. Ce qui est mesuré ici la précède.

### ~~A3~~ ✅ — le masque d'approbation — **FAIT le 2026-09-04** (`77` §6)

⭐⭐⭐ `approval.tif` est **calculé**, aux cinq bras de contrôle, et les deux populations se
séparent : **quart de pas 92,7 %** approuvé (le témoin positif réaliste) contre **demi-pas
2,1 %** et **saut d'une feuille 0,0 %**.

⚠⚠ **Le champ donne DEUX prédicats et je les avais confondus** : une copie translatée d'un
demi-pas a une avance d'identité **nulle** — elle suit parfaitement une feuille qui n'existe
pas. C'est le **placement** (la partie fractionnaire de l'indice) qui la refuse.

⚠⚠ **Une spire publiée ne peut pas être son propre témoin positif de placement** : avec son
champ c'est circulaire (100 %), sans lui c'est pathologique (70 %) — la retirer la place
exactement au milieu de l'intervalle que son retrait vient de créer.

⚠⚠⚠ **Le bug que j'avais écrit** : retirer du champ la spire qui **borne** la surface jugée
détruit l'information qui détecte un interstice. Un demi-pas passait de **2,1 % à 37,6 %**.
La sonde fait tomber 4 contrôles.

⚠⚠⚠ **A3 était bloqué en AMONT de `villa`, pas en aval — et c'est réparé.** Cette entrée
disait *« le canal est écrit au bon nom et au bon format ; rien ne fait tourner `villa` »*.
Vérifié le 2026-09-04 : **rien n'écrivait le canal du tout** — aucun `imwrite` dans
`le_masque_dapprobation.py`, pas de drapeau `--ecrire` dans son parseur malgré sa propre ligne
d'usage, aucun `approval.tif` sur disque.

### ✅✅ Fait le 2026-09-05 : le masque est écrit, et `villa` l'accepte

> Mesure : `uv run python src/excision/le_masque_dapprobation.py --ecrire` (12 contrôles),
> `docs/mesures/le_masque_dapprobation_ecrit.json`.

`--ecrire` porte le verdict du champ **(z, θ)** sur la grille **tifxyz** d'une trace — ce qui
demande le centre par tranche que `_grille` calcule sur l'union des spires, un centre global
mélangeant des feuilles (`76`) — puis écrit `approval.tif` à côté de `x/y/z.tif`.

| | mesuré |
|---|---|
| trace | `PHerc0139 / w040`, grille **615 × 431**, 106 579 sommets valides |
| verdict | **749 / 1 359** cellules approuvées (55,1 %) |
| masque | 59 565 sommets à 1 — **55,9 %** des valides |
| **`villa`** | ✅ **ACCEPTE** (`load_approval_mask` + `_load_tifxyz_arrays`) |

⭐ Les deux fonctions d'acceptation sont **importées, jamais recopiées** : le contrat est celui
de `villa`, et une seconde version ici finirait par ne plus l'être. Elles n'importent que
`numpy` et `tifffile`, donc elles tournent **sans l'optimiseur**.

⚠⚠ **Et le bras négatif est là**, sans quoi le contrôle ne pourrait pas échouer : une forme
fausse et un dossier incomplet doivent être **refusés**, et ils le sont (`ValueError`).
« `villa` accepte notre masque » est satisfait par un lecteur qui accepte tout. Un second bras
exige que le masque n'approuve **ni rien ni tout** — un canal constant ne porte aucune
information.

⚠ **Reste hors de portée** : que la **ré-optimisation** en tire quelque chose. Le contrat de
fichier est honoré ; ce que `lasagna` fait ensuite du masque n'est pas exercé.

⚠ Piège traversé : l'import dynamique de `approval_inpaint.py` échoue si le module n'est pas
dans `sys.modules` **avant** son exécution — il déclare un `@dataclass`, et `dataclasses`
remonte à `sys.modules[cls.__module__]`. L'erreur est un `AttributeError` sur `NoneType` qui ne
nomme ni le module ni la cause.

⚠ Et **aucun `approval.tif` peint n'est publié** (vérifié au listing S3, `73` §0), donc la
comparaison « le calculé vaut-il l'humain » reste non montable, quoi qu'on écrive.

### A3 bis — l'ancienne formulation, gardée pour mémoire

Écrire un `approval.tif` à côté des `x/y/z.tif` (article §6.7). **Quatre bras de contrôle**,
et le quatrième est celui sans lequel le contrôle ne peut pas échouer :

| bras | attendu |
|---|---|
| masque automatique sur une spire publiée | approuve ≥ 80 % de l'aire |
| masque vide / masque plein | écart de maillage mesurable |
| **copie translatée d'un demi-pas** | **refuse ≥ 90 %** |

⚠ Sans le quatrième bras, **un masque qui approuve tout passe le contrôle**.

⚠ Le prédicat doit désigner des **régions**, pas des points : corriger 0,56 % de la surface ne
change pas α (`42`). Et il ne peut pas empiler des α : 39 verdicts sur 138 ne tiennent plus
sous la règle des deux appuis (`51` §4). Il lit **le relief dans la fenêtre étroite**.

### A4 ⭐⭐ — le rouleau de déploiement : `PHerc0139`, pas `0800` ni `1447`

⚠⚠⚠ **Correction du plan de `73` §3.3** (`74` §4). `PHerc0800` publie 6 segments, tous
`auto_grown` ; `PHerc1447`, 15 dont 14 — **aucun indice de spire**. Y déployer un prédicat
d'identité validé ailleurs est un transport non énoncé.

`PHerc0139` est le seul rouleau qui porte les deux : 37 spires consécutives, carte dense sur
91 fenêtres, queue à **4,4 %** (2ᵉ des quatorze, devant `1447`), et **déjà transformé dans le
repère du régime du prix**.

⚠ Réserve, reprise de `73` §5 : rien ne montre encore qu'un rouleau à 4,4 % se trace mieux
qu'un à 22,8 % (`55` : le mur 1 vient de la graine, pas du scan). `0139` ne se choisit pas sur
sa queue — il se choisit parce que c'est le **seul endroit où l'on peut mesurer si le prédicat
marche**.

### A5 bis ⭐⭐ — la chaîne GLISSE et ne saute pas — et son budget d'écart est gonflé

> ⚠⚠⚠ **Corrigé le 2026-09-04, deux fois de suite, par la lecture.** L'auteur a demandé si des
> docs avaient étudié `suivre_nappe`, puis m'a renvoyé à `registres/fiches_de_lecture.md`, *« le
> doc qui servait à noter les conclusions de chaque doc »*. Les deux ont **remplacé** ce que
> j'allais faire, et la seconde a annulé ce que la première venait de me faire écrire.

**Ce qui est déjà fait, et qu'il ne faut pas refaire :**

- **la boucle de correction est un cul-de-sac mesuré** (`42`) : le témoin bat toutes les
  corrections, à tous les poids, en fenêtre valide. 318 points = 0,56 % de la surface, et le
  mode `--nappe` (10,1 %) ne renverse pas le verdict ;
- **la chaîne de spires tourne** (`43`) : `gen_neighbor`, l'outil « wrap by wrap » public.
  4 spires sur 7 convergent à pas 1,0, **6 sur 7 à pas 0,5**, et le levier est la **portée du
  test de sortie** du rayon, pas le pas ;
- ⭐⭐⭐ **et l'identité a DÉJÀ été jugée** (`44`, `src/nappe/couverture_publiee.py`) : le point
  de départ étant un morceau de segment **publié**, la bonne feuille est connue sur toute son
  emprise. Verdict : **la chaîne GLISSE, elle ne SAUTE pas** — écart lisse, monotone, du même
  côté pour **73 %** des points, **69 µm à 5,76 mm**. Elle quitte la bande « même feuille »
  (40 µm) vers 3,5 mm et reste loin de « feuille voisine » (250 µm). Et la dérive est une
  **loi** qui prédit hors échantillon.

⚠⚠ **Donc l'expérience que j'allais proposer était déjà faite**, et mon prédicat d'identité y
confirmerait ce qu'on sait. Je l'avais écrite ici comme « l'expérience que personne ne pouvait
poser ». C'était faux.

⭐⭐ **Ce que cette session ajoute vraiment, et c'est plus petit et plus juste** : `77` §10
mesure que la surface publiée est elle-même à **27 µm** de la matière (20,8 à l'échelle d'une
cellule). L'écart de la chaîne est mesuré **contre cette surface**, donc **son budget est
gonflé** :

| | |
|---|---|
| écart mesuré à 5,76 mm | **69 µm** |
| en retirant le référent en quadrature | ≈ **64 µm** |
| franchissement des 40 µm « même feuille » | mesuré à **3,5 mm** — donc **plus tard** en réalité |

⚠⚠ **Correction : `44` mesure sur `PHercParis4`, pas sur `PHerc1447`** — son `um_par_voxel` de
2,4 le dit, et je m'étais trompé de rouleau ici même.

⭐⭐⭐ **Et le référent Y EST MAINTENANT MESURÉ** (`77` §10) : `dl.ash2txt.org` publie les
65 couches de son segment de référence, que j'avais déclarées absentes après n'avoir interrogé
**qu'un seul serveur** — quatrième fois pour cet angle mort, et c'est l'auteur qui l'a vue.
Lues par fenêtre (`src/volume/couches_distantes.py`, 1,35 Gio au lieu de 30,5 Go).

| rouleau | en feuilles |
|---|---:|
| `PHerc0172` | **0,121 – 0,136** |
| `PHerc1447` | **0,122 – 0,146** |
| **`PHercParis4`** *(celui de `44`)* | **0,138** |

⚠⚠ **Chiffres corrigés le 2026-09-04** (`77` §12) : les premiers étaient **gonflés de 25 à
37 %** par un centre de masse qui **enjambait deux feuilles** — les dalles couvrent 1,8 à 3,0
écarts, donc 9 sur 12 en contiennent plusieurs. Borné à ±0,5 écart, `PHercParis4` cesse d'être
aberrant (37,7 → 23,8 µm) : ce n'était pas un rouleau à part, c'était l'estimateur.

⚠⚠⚠ **Mais on ne compose PAS les micromètres.** `couverture_publiee.py` pose
`UM_PAR_VOXEL = 2.4` justifié par cohérence **interne**, jamais contre un volume déclaré — et
les deux volumes publiés de `PHercParis4` sont à **7,91 µm**. Tous les micromètres du tableau
de couverture de `44` reposent donc sur une constante que rien ne relie à un volume.

> ~~**Ce qui reste à faire, et c'est petit** : que `44` nomme son volume.~~ ✅✅ **FAIT le
> 2026-09-05**, et ma prémisse était fausse : `PHercParis4` publie **cinq** volumes, dont
> **aucun à 7,91 µm** — ce chiffre est celui de `PHerc0172`, emprunté. La boîte englobante du
> maillage étant en voxels du niveau 0, un volume trop petit pour la contenir **n'est pas** le
> sien : **un seul** des cinq la contient, et il est à **2,400 µm** — la constante posée.
> `provenance_du_voxel_reconstructible` est passé à vrai, et la correction est désormais
> **calculable en micromètres** (`69,2 → 66,4 µm`). Mesure :
> `src/nappe/le_volume_du_maillage.py` (18 contrôles, 3 sondes qui mordent).

> ~~⚠ **Le seul contrôle qui vaudrait d'être monté** : refaire `couverture_publiee.py` contre la
> surface **recalée sur la bande** plutôt que contre la surface publiée.~~ ✅✅ **RÉPONDU le
> 2026-09-05, et sans recaler quoi que ce soit** — voir ci-dessous.

### ✅✅ A5 bis — la dérive n'est PAS l'erreur du référent, et un biais est CONSTANT

> Mesure : `src/nappe/la_derive_nest_pas_le_referent.py` (16 contrôles, 4 sondes qui mordent).

Le contrôle réclamait un recalage. Il n'en a pas besoin, parce qu'une erreur de référent se
décompose en **deux parts qui ne se retirent pas de la même façon** :

| part | ce qu'elle fait à l'écart mesuré | comment elle se retire |
|---|---|---|
| **biais** — le référent est décalé d'un côté | ajoute la **même** chose à tous les maillons | elle **s'annule dans les différences** |
| **dispersion** — le référent bruite autour de la matière | ajoute une variance | **en quadrature**, ce que `77` §10 a fait |

![la derive de la chaine contre l'echelle du referent](images/75_la_derive_et_le_referent.png)

Figure : `src/figures/figure_la_derive_et_le_referent.py`, depuis
`docs/mesures/la_derive_nest_pas_le_referent.json`.

```
uv run python src/figures/figure_la_derive_et_le_referent.py
```

⚠⚠ **La bande verte est ancrée sur le PREMIER maillon, pas sur zéro**, et c'est tout l'argument :
un biais déplace la courbe entière, donc il déplace l'**origine**. La rampe en sort au quatrième
maillon (1,2 mm) et **n'y revient jamais** — ce que le contrôle asserte, avec son témoin : une
série qui sortirait puis rentrerait ne serait pas une sortie définitive, et une série plate ne
sortirait pas du tout.

⭐⭐⭐ **Donc la part de l'écart final qu'aucun biais ne peut expliquer vaut exactement**
$|e_N - e_1| / |e_N|$ — aucun ajustement, aucun seuil, aucune fenêtre choisie.

| parcouru | 96 µm | 288 | 480 | 768 | 1152 | 1920 | 2880 | 3840 | 4800 | **5760** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| écart | **−0,3** | −1,5 | −3,8 | −12,2 | −20,5 | −28,1 | −34,8 | −44,9 | −56,8 | **−69,2** |

Le premier maillon est à **0,3 µm** de la surface publiée, le dernier à **69,2**. Un biais
constant explique donc **au plus 0,5 %** de l'écart final ; avec la dispersion retirée en
quadrature (19,5 µm), **le référent entier en explique au plus 4,5 %**.

```
uv run python src/nappe/la_derive_nest_pas_le_referent.py \
    --json docs/mesures/la_derive_nest_pas_le_referent.json
```

⚠⚠ **La borne n'est valide qu'à une condition, et elle est vérifiée** : tous les écarts médians
doivent porter le **même signe**, sinon un biais de signe opposé à la dérive pourrait dépasser
$|e_1|$. Les dix maillons sont négatifs, et le code **refuse** une série à signes mêlés au lieu
de rendre une borne qui ne tiendrait pas.

⚠ Et $|e_1|$ **majore** le biais : le premier maillon a déjà parcouru 96 µm, donc il contient le
biais *plus un peu de dérive*. La borne est conservatrice — elle sous-estime ce que la chaîne
fait, jamais l'inverse.

⭐⭐ **Ce que ça règle** : la correction de `77` §10 tient (69,2 → 66,4 µm) et elle est **petite**,
et la question « et si tout l'écart venait du référent ? » est fermée par la **forme** du signal.
Un référent mal placé produit un décalage ; la chaîne produit une **rampe**. Ce ne sont pas les
mêmes objets, et une rampe ne se corrige pas en déplaçant une origine.

### A5 ⭐ — extraire, pas faire pousser

L'article a fermé les deux voies ascendantes **par la mesure** : l'extension converge vers un
point fixe de 6,02 cm² (§5.6), les patchs ne pavent pas (§5.7). Ce qui reste est l'extraction
de **toutes** les spires depuis un champ global.

**Mesure de succès** : aire utile par spire, à présence + placement + identité, contre
6,02 cm². Une spire entière fait 60 à 300 cm².

⚠ Et l'érosion se **mesure**, pas se suppose : une extraction n'érode pas comme une chaîne
(15,6 % par tour, `44` §5).

### A6 — la ROC de α et de $d$

`73` §2.8 : α n'a jamais vu de courbe ROC — sa validation de §3.3 est **un** vert contre les
traces condamnées. Avec le compte corrigé, ce sont **101 positifs** (et non 57) et leurs
101 copies translatées d'un demi-pas comme négatifs. Ferme §2.2 et §2.8 d'un coup, avec les
instruments existants.

---

## A' — ⚠⚠⚠ CE QUI RESTE SOUS LES ✅

> Remarque de l'auteur, et elle vise un défaut réel de ce fichier : *« c'est typiquement le cas
> où tu vois le logo vert de A3, tu vois le A3 bis, mais tu ne lis pas entre, et tu loupes les
> tâches que tu laisses comme ça. »*
>
> ⚠ Un ✅ fait arrêter de lire. Tout « ⚠ Restant sur X » enfoui sous un titre coché est donc
> **recopié ici**, et cette section est la seule qu'il faut lire pour savoir ce qui traîne.
> **Règle** : marquer une tâche ✅ oblige à ajouter sa ligne ici, ou à écrire qu'il n'en reste
> rien.

| d'où | ce qui reste | pourquoi ça n'a pas été fait |
|---|---|---|
| **A1** | — | ✅ rien : `PHerc0172` mesuré le même jour |
| **A2** | le champ a besoin du **référent** | c'est **A2 bis** / **A2 ter**, une tâche à part |
| **A2** | la cause du trou de `PHerc0172` : déchirure, perte, collage ? | la densité dit qu'il n'y a **pas de matière**, pas pourquoi. ⚠ Demanderait un autre visuel — une coupe longitudinale, ou le volume |
| **A3** | ✅✅ **le masque est écrit et `villa` l'accepte** | fait le 2026-09-05 : `--ecrire` porte le verdict du champ sur la grille tifxyz et écrit `approval.tif` ; les deux fonctions d'acceptation de `villa` sont **importées** et acceptent, avec leurs bras négatifs (forme fausse et dossier incomplet **refusés**). ⚠ Reste hors de portée : ce que la ré-optimisation en tire |
| **A3** | ⚠⚠ **aucun `approval.tif` peint n'est publié** | donc « le calculé vaut-il l'humain » reste **non montable**. Vérifié au listing S3 (`73` §0) |
| **A3** | le masque n'a été mesuré que sur `PHerc0139` | `PHerc0172` ne sépare qu'après exclusion du trou |
| **A5** | ⭐⭐ le **plancher** : une spire publiée est à **20,8 µm** de la matière *à l'échelle où le champ travaille* (`77` §10), donc l'erreur propre du champ est entre **28 et 49 µm**, **44** si indépendantes — et l'indépendance est **vérifiée** (corrélation ≤ 0,08 entre voisines) | mesuré en coupe sur **six** spires, dont cinq consécutives ; resserrer demanderait une règle autre que la spire publiée |
| **A5** | l'extraction porte **une feuille** (47 µm), pas deux | mesuré : réinjecter une spire prédite ne change **rien** — le champ est un juge, pas un générateur |
| **A5** | ⚠ la structure angulaire de l'écart (**71 µm**, 45 % de la médiane) **n'améliore pas** l'extrapolation | mesuré : un pas par cellule mis en commun donne 52 µm à une feuille contre 47 pour le pas global. Meilleur à longue portée (1,71 contre 1,90 feuille à huit), inutile là où ça compte |
| **A5 bis** | ⚠ ~~juger la chaîne par l'identité~~ — **déjà fait** (`44`) : elle **glisse**, elle ne saute pas. Ce qui reste est de refaire la mesure contre une surface **recalée**, son budget étant gonflé (**69,2 → 64,7 µm**, conjecture) | corrigé par la lecture des fiches ; mesuré sur 2 rouleaux, **pas** sur `PHercParis4` où `44` a mesuré |
| **A6** | la ROC de α n'est pas faite | demande de **rendre** 101 surfaces à deux profondeurs — le seul poste de ce registre qui exige le volume |
| **B2** | « no threshold » pas encore rétréci dans l'abstract | ⚠⚠ **testé et NON tranchable ainsi** (`77` §11) : translater = décentrer la fenêtre dans la même pile, l'idée est bonne mais une dalle de volume de surface fait ±0,9 écart et ne permet pas d'emboîter deux fenêtres. **25 refusés sur 36**. Retenté sur une dalle de 3,0 écarts : le positif centré sur le lobe est **circulaire**, et le transport d'une fenêtre à l'autre est **confondu par le serpentage** (0,13 écart ≈ la fenêtre étroite). Il faudrait un positif **indépendant** — carte d'encre ou annotation |
| **C** | la règle graduée | ✅✅ **C2 et C3 mesurés les 2026-09-04/05.** C3 : le débinage ne rend rien (rapport 1,01), donc le courriel à l'ESRF n'est pas justifié. C2 : sur une face **vierge**, la dispersion du détecteur ne tombe que de **6 %** alors que le contraste local est **14× plus bas** — « il y a de la structure ici » ne discrimine pas ; le **niveau**, lui, se déplace (−0,27 contre −1,50). ⚠ Reste C1, plus petit qu'annoncé |
| **D1** | ✅✅ l'arc d'excision (`03`–`07`) — **FERMÉ : la conclusion de tête de `07` est CONFIRMÉE** | ce qui la démentait était une mesure sans producteur, prise sur une colonne dominée par son bruit d'échantillonnage. Sur `shortfall` (sans seuil, bruit < 5 %) : **0 paire sur 10** au-delà du bruit, signe mélangé. Ce qui est établi est une **borne**, pas une absence |
| **D2** | ✅✅ le contrôle P1 bis de `71` — **FAIT le 2026-09-05, l'hypothèse tient** | ⚠ le « blocage » était une erreur de recherche à moi : le rapport est dans l'arbre (`registres/anteriorite_resultats_de_tete.md:593`), j'avais cherché un fichier **nommé** budget au lieu du **concept**. Mesuré : densité **2 812 à 2 857 cellules/cm²** sur 24 tirages (étendue 1,6 %), donc cellules ∝ aire ; le modèle exige **×15,9**, l'observé est **×4,0** — le basculement est plus raide que la taille |
| **D3** | ✅✅ ~~41~~ → ~~32~~ → ~~30~~ → **0** script sans appelant | ⚠ **entamé** : deux figures dont l'image est **utilisée** dans un doc ne portaient pas leur commande de régénération — c'est la règle du dépôt, et c'est réparé (vérifié : les deux se régénèrent à l'identique). Le reste est classé ci-dessous |

---

## B. L'article

> `73` §2.9 : *« la thèse tient, étroitement »*, et il **vaut d'être publié** à trois
> conditions. Les voici, plus deux que l'audit a ajoutées.

### ~~B1~~ ✅ — rétrécir §6.7 : présence ≠ identité — **FAIT le 2026-09-04**

La phrase *« the predicate is the same one α estimates »* sur-affirme. α répond à la
**présence** ; le pinceau peint l'**identité**. Remplacer par : *α automates the presence half
of the approval predicate; the identity half is open, and the referent to test it against is
published.* Et **verser `17` dans cette section** comme le résultat négatif qu'il est.

⭐ **Écrit**, et avec les chiffres mesurés plutôt qu'annoncés : α automatise la **moitié
présence** ; l'identité est ouverte et son référent est publié — 101 segments approuvés portant
leur numéro de spire, deux courses sans trou (`w023`–`w059`, `w052`–`w095`), l'indice comptant
vers l'extérieur à 95,0 % et 95,1 %, et un pas d'indice valant 154,1 et 147,4 µm. Plus un
encadré qui déclare les **trois défauts du référent** : un test noté contre lui doit les
exclure, sinon un bon prédicteur se lit comme un prédicteur à 94 %.

### B2 ⚠⚠ — rétrécir *no threshold* dans l'abstract et en §3

Vrai de α, faux du **placement** : distinguer une surface sur sa feuille d'une surface dans
l'interstice se fait par $d$ contre la demi-épaisseur — un seuil en micromètres.

⚠ **À mesurer avant d'écrire** (`73` §5 le concède) : translater un segment convergent d'un
demi-pas et mesurer α. Prédiction : α ≈ 0 avec $d$ ≈ 80–90 µm. Si α ≈ 1, la revendication tient
et B2 tombe.

### ~~B3~~ ✅ — le 113 µm — **FAIT le 2026-09-03/04**

`74` §2. La conclusion de `73` est juste — ce n'est pas un écart centre à centre — mais son
mécanisme cite une phrase de `43` §6quater que `43` **corrige plus loin dans le même
document**, depuis la source. Le vrai mécanisme est pire : le rayon peut sortir puis **rentrer
dans la même feuille**, et l'écart mesuré **dépend d'un réglage** — 116 → 109 → 107 → 102 µm
quand `neighbor_step` est halvé trois fois.

Donc : ligne 201 (relabelliser **et** nommer le réglage), ligne 352 (l'exemple d'échelle),
§5.5 (*« which is one sheet »* devient une inférence, avec renvoi à `16` : 156 µm médian).

⚠ Et **ne pas s'appuyer sur la médiane de l'atlas** (172,8 µm) : c'est 10,0 voxels **entiers**
de niveau 1, quantifiés à 17,28 µm, d'IQR 121–250,6. L'appui solide est `16`.

### ~~B4~~ ✅ — nommer les quinze segments de §5.7 — **FAIT, et le résultat a grandi**

14 `auto_grown_<horodatage>` + 1 `z_dbg_gen_00320` (confirmé). *« The published segmentation of
a prize scroll »* laissait croire à un effort curaté.

⭐⭐ **Et nommer les segments a fait grandir le résultat au lieu de le rétrécir** (`76` §7) : les
spires curatées **pavent** (37/37 et 44/44 ont une voisine à une feuille) là où l'automatique
échantillonne (4/14). Le titre de §5.7 devient *« Automatic tracing samples, curated
segmentation tiles »*, et un encadré porte le piège — la médiane sur toutes les paires rend
2202 contre 1901 µm, **indiscernable**.

### ~~B5~~ ✅ — les deux comptes, 13 et 14 — **FAIT le 2026-09-03**

Les deux sont dans `derive_profondeur.json` avec des définitions différentes (`74` §1).
Dire lequel est lequel, en une incise.

---

## C. La règle graduée — trois semaines, et on s'arrête

### C1 ⭐⭐ — la case vide : **une case est REMPLIE le 2026-09-05**, sur `PHerc0139`

> Mesure : `src/encre/la_case_vide_remplie.py` (19 contrôles),
> `docs/mesures/la_case_vide_remplie.json`. Figure : `src/figures/figure_case_vide_remplie.py`
> (7 contrôles).
>
> ```
> uv run python src/encre/la_case_vide_remplie.py --segment 20260325000000-w046_20260325 \
>     --json docs/mesures/la_case_vide_remplie.json
> uv run python src/encre/la_case_vide_remplie.py --controle \
>     --segment 20260325000000-w046_20260325 --json docs/mesures/la_case_vide_remplie.json
> uv run python src/figures/figure_case_vide_remplie.py --sortie docs/images/75_la_case_vide_remplie.png
> ```

⚠ **Ce n'est PAS la case de `PHerc0500P2`** que `68` §4 désigne comme celle qui décide — celle-là
porte une vérité terrain infrarouge et reste à faire. C'est une des **38 cases vides de
`PHerc0139`**, choisie parce que `C2` venait d'y travailler et que sa carte de production existe
déjà, donc la mesure coûte une inférence au lieu d'une campagne.

### ⭐⭐⭐ Le fait qui rend la mesure simple : un volume de surface est une dalle en MICROMÈTRES

| régime | taille de voxel | couches | pile | ce que les 26 du modèle couvrent |
|---|---:|---:|---:|---:|
| production | 2,399 µm | **109** | 261 µm | **62 µm** |
| **prix** | 9,362 µm | **28** | 262 µm | **243 µm** |

Les deux volumes couvrent **la même épaisseur physique** ; le nombre de couches n'est que la
taille de voxel. Deux conséquences, et elles vont dans des sens opposés :

- au régime du prix la fenêtre du modèle **est** le volume — **aucun choix de profondeur à
  faire**, donc aucune façon de se tromper de fenêtre ;
- et c'est le régime **grossier** qui lit les **243 µm** proches des 206 µm de l'entraînement,
  pendant que le régime **fin** n'en lit que 62. Le scan de repérage est, sur ce point précis,
  **celui qui ressemble à l'entraînement**.

⚠ C'est aussi pourquoi le nul apparié de `C2` est **structurellement impossible** au régime du
prix : 28 couches pour une fenêtre de 26 laissent deux couches de marge. `le_nul_verso.py` y
refuse plutôt que d'inventer une fenêtre.

### La confrontation, et c'est elle qui porte le résultat

« Ce que le détecteur rend à 9,362 µm » est un nombre sans référence. Le même segment publie une
carte d'encre **à 2,399 µm**, produite par la communauté avec son propre modèle
(`new_canon_autoresearch_recipe`) : la meilleure réponse disponible à *« y a-t-il de l'encre
ici ? »*, et elle est **indépendante de nous**.

![l'accord avec la carte publiée, seuil par seuil](images/75_la_case_vide_remplie.png)

| seuil (quantile de la carte publiée) | p50 | p75 | p90 | p95 | **p99** |
|---|---:|---:|---:|---:|---:|
| **production** (2,399 µm) | 0,345 | 0,395 | 0,432 | 0,516 | **0,755** |
| **régime du prix** (9,362 µm) | 0,398 | 0,409 | 0,354 | 0,380 | **0,391** |
| témoin, nos pixels mélangés | 0,499 | 0,502 | 0,503 | 0,500 | 0,499 |

⭐⭐ **Le résultat est une FORME, pas un nombre** : en production l'accord **monte** avec le seuil
d'encre — notre carte retrouve l'encre **forte** de la carte publiée — pendant qu'au régime du
prix il reste **plat**. C'est la différence entre les deux régimes, et c'est ce que `68` §4
demandait de mesurer.

⭐ **Le témoin par mélange tient 0,500 aux cinq seuils.** C'est lui qui autorise à lire une AUC
sous 0,5 comme un fait sur les cartes et non comme un biais du montage — sans lui, tout le
tableau pourrait n'être qu'un défaut de comparaison.

### ⚠⚠ Trois réserves, et la première suffit à interdire une conclusion forte

1. **Le point le plus haut ne porte que 32 pixels.** L'AUC de 0,755 est prise sur le centile
   supérieur d'une région de 249 × 249 pixels réduits. C'est une **tendance**, pas une mesure.
2. **Le bas des deux courbes ordonne du bruit de JPEG.** Les trois quarts de la région publiée
   tiennent entre **30 et 39 sur 255** : au seuil médian on compare deux moitiés de fond
   compressé. ⚠ C'est une correction de ma propre première version, qui prenait la médiane comme
   frontière encre/fond et mesurait donc l'ordre relatif du bruit.
3. **Ce n'est pas une vérité terrain.** Deux modèles peuvent se tromper ensemble, et un désaccord
   ne dit pas lequel a tort. La vérité terrain infrarouge existe sur `PHerc0500P2`, pas ici.

⚠ **Et l'alignement a été vérifié avant de conclure quoi que ce soit.** Une AUC *fiablement* sous
0,5 n'est pas un désaccord au hasard — c'est du signal partagé, retourné. Les **huit
transformations du carré** ont donc été testées : identité **0,398**, miroir de colonnes 0,619,
rot270 0,543, les autres autour de 0,5. Aucune ne rend un accord franc, donc l'orientation est
innocentée. Et les deux grilles sont dans le rapport de leurs tailles de voxel (3,893 contre
3,903 attendu, 0,3 % d'écart), ce que la mesure asserte plutôt que de le supposer.

### ⚠⚠⚠ La case qui décide demande UNE CHOSE DE PLUS, que ni `68` ni `72` ne nomment

> Mesure : `src/encre/deux_aplatissements.py` (10 contrôles),
> `docs/mesures/deux_aplatissements.json`.
>
> ```
> uv run python src/encre/deux_aplatissements.py --json docs/mesures/deux_aplatissements.json
> ```

`68` §4 et `72` §3 disent que remplir la case de `PHerc0500P2` ne demande *« ni faisceau, ni
annotation manuelle, ni rescan »*. **C'est vrai, et incomplet** : la **scorer** contre la vérité
terrain infrarouge demande un **recalage entre deux aplatissements**.

⭐⭐ **Vérifié sur les DEUX serveurs**, parce que n'interroger qu'une vue du corpus est l'angle
mort que `78` §0 recense trois fois — et la première réponse était fausse. L'index ouvert ne
publie **aucune** étiquette d'encre (0 sur les 14 types de données du corpus) ; `dl.ash2txt.org`,
lui, en publie :

| | serveur | forme |
|---|---|---|
| `500P2_inklabels.png`, `_ir.png`, `_mask.png` | `dl.ash2txt.org/fragments/PHerc0500P2/paths/2um_front_surface/` | **27 160 × 14 990** |
| couches du chemin des étiquettes | même chemin | 65 couches, **2 µm seulement** |
| couches du **régime du prix** | bucket ouvert, `segments/…-500P2_front/` | 28 couches, 9,362 µm, **6 280 × 3 580** |
| couches de production | même segment | 118 couches, 2,215 µm, **26 440 × 15 060** |

⚠⚠ **26 440 × 15 060 contre 27 160 × 14 990** : même fragment, **paramétrisations différentes**.
Un aplatissement n'est pas unique, donc les étiquettes ne se transportent pas pixel pour pixel.
Et le chemin des étiquettes ne publie **aucun volume à 9,362 µm** — les deux moitiés de
l'expérience sont sur deux surfaces.

⚠⚠⚠ **Et le recalage ne peut pas être exact, faute de coordonnées.** Le segment publie son
`tifxyz-transformed` — une position 3D par cellule — donc apparier deux surfaces par leur
**géométrie** serait un plus proche voisin, exact et bon marché. Le chemin des étiquettes ne
publie **que des images** : ni `tifxyz`, ni `obj`. L'appariement doit se faire **par l'image**.

### ⭐⭐ Mais c'est traitable, et c'est mesuré

| | valeur |
|---|---:|
| recouvrement des deux empreintes (Dice, grille 256) | **0,971** sans décalage, **0,972** au mieux |
| écart des rapports d'aspect | **3,2 %** |

**Les deux aplatissements sont presque la même carte.** Un recalage fin est donc un **lot
défini**, pas un problème de recherche — au-dessous de 0,80 il aurait fallu un champ de
déformation.

⚠ Deux réserves. À 256 cellules une case vaut ~100 µm : ce qui est établi est l'accord des
**silhouettes**, et une lettre fait ~600 µm — la registration au niveau de la lettre reste à
faire. Et les 3,2 % d'écart d'aspect ne sont pas rien : sur 27 160 lignes, c'est ~870 lignes de
dérive cumulée, soit **~1,9 mm**, donc trois lettres d'un bout à l'autre. Il faudra une **affine**
(échelle anisotrope), pas une similitude.

⚠ L'empreinte du segment est tirée de la **région non nulle de sa carte d'encre réduite**, faute
de masque publié — donc ce n'est pas un masque de surface mais « là où le détecteur a rendu
quelque chose ». Le recouvrement mesuré est un **minorant**.

### ⭐⭐ L'affine est construite et VALIDÉE par une référence externe

> Mesure : `src/encre/le_recalage_des_etiquettes.py` (13 contrôles),
> `docs/mesures/le_recalage_des_etiquettes.json`.
>
> ```
> uv run python src/encre/le_recalage_des_etiquettes.py --json docs/mesures/le_recalage_des_etiquettes.json
> uv run python src/encre/le_recalage_des_etiquettes.py --prix --regime prix       --json docs/mesures/le_regime_du_prix_score.json
> uv run python src/encre/le_recalage_des_etiquettes.py --prix --regime production --json docs/mesures/le_regime_production_score.json
> uv run python src/encre/le_recalage_des_etiquettes.py --residu --json docs/mesures/le_regime_du_prix_score.json
> ```

Affine **diagonale** estimée par les deux boîtes occupées — une échelle par axe et une
translation, ce qu'un écart de rapport d'aspect décrit exactement. Extrémités aux **percentiles
1 et 99** : un seul pixel isolé fixerait la boîte et décalerait toute la carte.

⭐⭐⭐ **Et le recalage n'est pas jugé par lui-même.** La carte d'encre **publiée par la
communauté** — celle dont le papier de référence montre qu'elle marche — est scorée contre les
étiquettes recalées : **AUC 0,756**, témoin par mélange **0,500**, sur **256 266 pixels d'encre
contre 3,66 millions**. Le Dice passe de 0,973 à **0,975** à 1024 de côté.

### ⚠⚠⚠ MAIS L'AFFINE GLOBALE NE SUFFIT PAS LOCALEMENT, et c'est mesuré

Sur la fenêtre la plus encrée du fragment, la **même carte publiée** tombe à **0,418** —
*sous le hasard*. Une AUC sous le hasard n'est pas un manque de signal : c'est du signal
**anti-aligné**, et un texte est fait de traits quasi périodiques, donc un décalage d'une
demi-largeur de trait suffit à mettre l'encre prédite dans les blancs.

| décalage local appliqué aux étiquettes | AUC de la carte **publiée** |
|---|---:|
| aucun | **0,418** |
| (−104, −120) cellules, soit **2,1 mm** | **0,711** |

⚠ **Et le maximum est encore au bord du balayage**, donc **2,1 mm est un minorant**. Trois
lettres et demie de résidu local. ⚠⚠⚠ **Et un maximum au bord ne désigne rien** : le balayage
refait à ±48 cases sur 127 fenêtres place l'optimum à **(−24, 0)**, *à l'intérieur* — voir plus
bas, « le résidu est une translation ».

> **Conséquence, et elle annule les chiffres suivants plutôt que de les nuancer** : aucun nombre
> mesuré **par fenêtre** à travers ce recalage n'est interprétable tant qu'il n'est pas local.
> Les trois AUC obtenues sont enregistrées **comme non interprétables**, avec leur raison :
>
> | | fenêtre | AUC | pourquoi elle ne dit rien |
> |---|---|---:|---|
> | notre détecteur, régime du **prix** | top 5474, left 637 (27,8 % d'encre) | **0,254** | référence appariée **0,418** sur la même fenêtre — les deux échouent, et le résidu vaut 2,1 mm |
> | notre détecteur, **production** | top 24320, left 4607 (**91,1 %** d'encre) | 0,529 | **344 pixels de fond** seulement : la fenêtre n'a presque pas de négatifs |
> | carte publiée, toute l'empreinte | — | 0,756 | moyenne sur des régions aux décalages locaux **différents**, donc un minorant dilué |

⚠⚠ **Une erreur de comparaison payée en chemin, et c'est celle qui a mis le résidu en évidence.**
J'ai d'abord comparé notre 0,254 (une fenêtre) au 0,756 de la carte publiée (**toute
l'empreinte**). Sur la même fenêtre, la publiée fait **0,418** : l'écart que j'allais publier
était celui de deux **régions**, pas de deux **régimes**. Toute AUC est désormais rendue
**appariée** — notre carte et la carte publiée, sur les mêmes pixels, contre les mêmes
étiquettes.

⚠ Et une seconde, dans le balayage lui-même : ma première recherche portait sur **±12 cellules**
(±212 µm, un tiers de lettre) et son maximum tombait **au bord** — ce qui ne dit rien d'autre que
« la recherche était trop courte ». La portée vient maintenant d'une mesure : les 3,2 % d'écart
d'aspect impliquent jusqu'à **~90 cellules** de dérive. `maximum_au_bord` est **asserté**, pas
noté.

### ⭐⭐⭐ Le résidu est GÉOMÉTRIQUE, et c'est une validation croisée qui le dit

> ```
> uv run python src/encre/le_recalage_des_etiquettes.py --champ --json docs/mesures/le_regime_du_prix_score.json
> uv run python src/figures/figure_champ_de_recalage.py --sortie docs/images/75_champ_de_recalage.png
> ```

![le résidu que l'affine globale ne corrige pas](images/75_champ_de_recalage.png)

⚠⚠⚠ **Le champ est ajusté sur les SILHOUETTES, jamais sur l'encre — et c'est le piège central de
tout ce lot.** Maximiser l'accord entre la carte d'encre publiée et les étiquettes ferait deux
choses à la fois : rendre cet accord élevé **par construction**, et tailler la géométrie sur les
erreurs d'un détecteur qui n'est pas le nôtre. Scorer ensuite notre carte à travers ce champ, ce
serait la juger contre une géométrie faite pour quelqu'un d'autre.

| | valeur |
|---|---:|
| carreaux portant un **bord** (les seuls où le décalage est contraint) | **34** |
| Dice médian après décalage local | **0,951** |
| norme du décalage : médiane / p90 / max | **60 / 152 / 160** cellules — **1,1 / 2,7 / 2,8 mm** |
| accord de l'**encre** sur la fenêtre, **sans** le champ | **0,418** |
| ... **avec** le champ tiré des silhouettes | **0,612** |

> **Un champ qui n'a jamais vu une étiquette ni une carte d'encre remonte l'accord de l'encre de
> +0,194.** Le résidu est donc bien géométrique — ce n'est pas le détecteur qui échoue, c'est la
> géométrie qui est fausse d'un millimètre.

⭐ **Et il n'atteint pas l'optimum trouvé en regardant l'encre (0,711), ce qui est la bonne
nouvelle** : un champ indépendant qui l'égalerait serait suspect. L'écart dit ce qu'un champ plus
dense reste à gagner — le carreau le plus proche de la fenêtre est à **277 cellules**.

⚠⚠⚠ **Ce +0,194 est vrai sur CETTE fenêtre et ne se généralise pas.** Sur les 42 fenêtres où ce
même champ répond, il gagne **+0,035** en médiane et n'améliore que **25 sur 42** — quand sa
propre **constante** gagne +0,067 et en améliore **36**. Le champ de bord ne bat donc pas la
médiane de ses propres carreaux ; voir la section « le résidu est une translation ».

⚠ Un carreau **plein** ne contraint rien : il se ressemble à lui-même partout, donc son décalage
optimal est arbitraire. Seuls les carreaux à occupation intermédiaire sont retenus, et leur
nombre est rendu — un champ estimé sur trois carreaux n'est pas un champ.

### ⚠⚠⚠ Mais un champ LISSE ne se laisse pas ajuster — le problème d'ouverture, mesuré

J'ai essayé de densifier le champ par un modèle polynomial, puisque les 34 carreaux sont sur les
bords et que la fenêtre mesurée est à 277 cellules du plus proche. **Ça ne marche pas, et la
raison est mesurée.**

| | erreur en laissant-un-dehors | le champ **nul** en fait |
|---|---:|---:|
| polynôme degré 2, deux équations par carreau (90 carreaux, pas 64) | **66** cellules | 65 |
| polynôme degré 2, **flot normal** (34 carreaux, pas 128) | **21** cellules | **17** |

⭐⭐ **La cause est le problème d'ouverture, et il est chiffré** : le plateau des décalages
atteignant 95 % du meilleur recouvrement est **allongé 9 fois sur 1 en médiane** (p90 **15,3**),
sur **33 carreaux sur 34**. Un bord droit ne contraint que la composante **perpendiculaire** ;
glisser le long du bord ne change rien au recouvrement.

⚠ Passer au **flot normal** — une seule équation par carreau, celle qu'il mesure vraiment — fait
tomber l'erreur de 66 à 21 cellules. C'est trois fois mieux, et **toujours pas mieux que zéro**.

> **Donc la déformation entre les deux aplatissements n'est pas une carte lisse de bas degré.**
> Il faut un champ **dense** — flot optique sur les masques, ou des repères intérieurs — et non
> un modèle paramétrique.

### ⚠⚠⚠ Et l'agrégation LOCALE non plus — avec un mirage en chemin

> Mesure : `src/encre/le_recalage_local.py` (19 contrôles, 4 sondes qui mordent), le
> 2026-09-05, sur les **mêmes 34 carreaux** — rien n'est recalculé.

Le remède classique de l'ouverture n'est pas un modèle global mais l'**agrégation locale** :
deux carreaux voisins dont les bords ne sont pas parallèles donnent deux équations
indépendantes et déterminent ensemble les deux composantes. C'est Lucas–Kanade, et c'est
exactement ce qu'un polynôme de bas degré **ne fait pas**.

| rayon | voisins (méd.) | conditionnement | erreur **norme entière** | champ nul | erreur **composante normale** | champ nul |
|---:|---:|---:|---:|---:|---:|---:|
| 256 | 2 | 0,26 | 125,6 | 66,8 | 30,4 | 14,6 |
| 384 | 3 | 0,26 | 75,0 | 62,1 | 24,7 | 17,7 |
| 512 | 4 | 0,34 | 71,2 | 60,5 | 27,8 | 16,1 |
| 768 | 7 | 0,43 | 65,2 | 60,4 | 20,8 | 17,2 |
| **1024** | 9 | 0,44 | **53,4** | 60,4 | 21,6 | 17,2 |
| **1536** | 16 | 0,60 | **47,8** | 60,4 | 18,4 | 17,2 |

⭐ **Sur la norme entière, l'agrégation locale bat le champ nul** aux deux plus grands rayons —
47,8 contre 60,4, soit 21 % de mieux. J'avais écrit l'assertion dans l'autre sens, en supposant
qu'elle échouerait comme le polynôme ; **c'est la mesure qui a corrigé**.

⚠⚠⚠ **Et c'est un mirage.** Sur la composante **normale** — la seule que chaque carreau
mesure réellement — **aucun rayon ne bat le champ nul**, à aucune taille de voisinage, de 2 à
25 carreaux. Le gain de la norme entière vient donc **entièrement de la direction non
contrainte**, c'est-à-dire d'une grandeur que personne n'a mesurée.

> ⭐⭐ C'est le péché cardinal du dépôt sous un costume de plus : non pas une vérification
> incapable d'échouer, mais **une amélioration sur la composante que la mesure ne contient
> pas**. Le contrôle qui l'attrape est écrit : les deux métriques doivent se **contredire**
> quelque part, et la composante normale doit être **strictement** plus petite que la norme —
> sans quoi la remplacer par la norme entière ne ferait rien échouer.

⚠ Le voisinage reste **local** — au plus 25 carreaux sur 34, jamais tout le fragment — donc ce
n'est pas un modèle global d'ordre zéro déguisé. Et la cause est la même, chiffrée autrement :
le conditionnement des directions plafonne à **0,60** là où l'isotropie vaudrait 1. Même en
réunissant seize carreaux, **les bords du fragment ne couvrent pas le plan**.

```
uv run python src/encre/le_recalage_local.py \
    --json docs/mesures/le_recalage_local.json
```

⭐⭐⭐ **Ce que ça règle** : la conclusion de C1 §1 ne dit plus « il faut un champ dense » comme
une préférence, elle le dit comme un fait mesuré **deux fois**. Ni un modèle lisse global, ni
une agrégation locale ne recalent ces masques — parce que le problème n'est pas la **forme** du
modèle mais la **matière** qu'on lui donne : des bords, et rien à l'intérieur. Il faut du
contenu intérieur, et c'est la seule voie qui reste.

### ⭐⭐ Le contenu intérieur EXISTE — 348 trous, et la moitié qui manque est de l'autre côté

> Mesure : `src/encre/les_reperes_interieurs.py` (15 contrôles, 3 sondes qui mordent), le
> 2026-09-05. ⚠ Posée **avant** d'écrire un recaleur : c'est une question sur l'**entrée**.

Les deux échecs ci-dessus désignent la même sortie — *« il faut du contenu intérieur »* — sans
dire s'il en existe. Un **trou** du masque en est un, et il a la propriété qui compte : il est
**géométrique**, donc s'en servir pour recaler ne rend pas circulaire la mesure d'encre qui
suit, contrairement à l'optimum de (−104, −120) cellules obtenu **en regardant l'encre**.

| | |
|---|---:|
| trous intérieurs d'au moins 64 pixels | **348** |
| dont le bord couvre assez le plan (conditionnement ≥ 0,25) | **314** |
| le plus grand | 16 907 px, 137 × 234, conditionnement **0,51** |

⭐ **314 repères intérieurs contre 34 carreaux de bord** — et ils sont *intérieurs*, donc
répartis sur le fragment au lieu d'être confinés à sa frontière. Chacun est individuellement
mieux conditionné que le voisinage de bord le plus large (0,60 au meilleur rayon).

```
uv run python src/encre/les_reperes_interieurs.py \
    --json docs/mesures/les_reperes_interieurs.json
```

⚠⚠ **Un trou rond contraint les deux composantes, une fente une seule** — c'est le problème
d'ouverture un cran plus bas, et c'est pourquoi le conditionnement est mesuré par trou plutôt
que supposé. Le seuil de 0,25 n'est pas choisi ici : c'est **celui que les carreaux de bord
atteignent déjà**, donc un repère qui ne ferait pas mieux qu'un bord droit n'apporterait rien.

⚠ Et un « trou » est une composante du complément qui **ne touche pas le bord de l'image** :
ce qui le touche est l'extérieur du fragment. Les confondre compterait le fond entier comme un
repère parfaitement isotrope — un faux positif parfait, et la sonde qui retire ce test fait
tomber **six** contrôles.

### ⚠⚠⚠ Mais la moitié qui manque est de l'AUTRE côté, et elle n'est pas publiée

Un repère ne sert que s'il existe **dans les deux** aplatissements. Or `deux_aplatissements`
l'écrit déjà : *« le corpus ouvert ne publie pas de masque pour ce segment »*. L'empreinte
disponible au régime du prix est le **support de la carte d'encre**, c'est-à-dire là où le
détecteur a rendu quelque chose — une propriété du **détecteur**, pas du fragment.

Et elle n'existe qu'à **1024 de large**. À cette résolution, des 314 repères il en reste **19** :

| | repères utilisables |
|---|---:|
| à pleine résolution (27 160 × 14 990) | **314** |
| à 1024 de large, là où l'autre aplatissement existe | **19** |

⚠ La réduction est faite **par majorité de bloc** et non par échantillonnage — sinon le compte
de repères dépendrait de l'endroit où la grille tombe. La sonde qui la remplace par un
échantillonnage au pas fait tomber le contrôle de stabilité : sur une fente de trois pixels
alignée sur le pas, elle rend **1 trou contre 0** selon un décalage de cinq pixels.

> ⭐⭐⭐ **Ce que ça change pour C1** : la voie n'est pas fermée, et son **prix est nommé**. Il
> faut soit un **masque de surface publié** pour l'aplatissement du régime du prix — ce qui est
> une demande, pas un calcul — soit les étiquettes rendues **à ce régime-là**, ce qui est la
> case vide de `68` §4 par un autre chemin.

### ⛔ Et ils N'ONT PAS de vis-à-vis, contrairement à ce que cette section conclut

> Mesure : `src/encre/les_reperes_apparies.py` (10 contrôles), figure
> `src/figures/figure_les_reperes_apparies.py` (7 contrôles), le 2026-09-05.

⚠⚠⚠ **CETTE SECTION EST CORRIGÉE PAR UNE MESURE DU MÊME JOUR, plus bas.** Elle conclut que « le
support de la carte publiée porte les trous du fragment, donc il est un masque de fait ». À
pleine résolution il en porte **36** quand le masque en a **348**, et le témoin est net : réduire
le support natif ×8 par la même règle rend **19** composantes de fond et non **420**. Les 71
« trous » comptés ici sont donc en grande part du **crénelage de compression** — la carte réduite
est un `.jpg`, et un `.jpg` crénelle les bords à fort contraste, c'est-à-dire le pourtour des
vrais trous. Ce qui survit : les repères se posent bel et bien **7,7 fois plus près** des vides
qui existent que le hasard. ⛔⛔ **Et même ce « 7,7 fois » tombe** : contre un témoin qui garde
la FORME du nuage au lieu de la casser avec sa place, la vraie position est la **6ᵉ sur 21**
(p = 0,29). Le rapport mesurait le **groupement** des repères, pas une correspondance. Voir
« le goulot n'était pas le fragment » puis « le témoin JUSTE enterre l'appariement ».

⚠⚠ **Le paragraphe ci-dessus supposait qu'il n'y avait rien en face. C'est faux, et la mesure
le dit.** Là où il n'y a **pas de matière**, un détecteur ne peut rien rendre — donc si le
support de la carte publiée porte les mêmes trous que le masque, il est un **masque de fait**,
et les repères ont un vis-à-vis sans qu'on ait rien à demander à personne.

![les reperes interieurs et leur vis-a-vis](images/75_les_reperes_apparies.png)

Figure : `src/figures/figure_les_reperes_apparies.py`, depuis
`docs/mesures/les_reperes_apparies.json`.

| | |
|---|---:|
| repères du masque, utilisables | 314 |
| dont transportables à l'échelle de la carte (3305 × 1883) | **55** |
| trous intérieurs du **support publié** | **71** |
| distance d'appariement, médiane | **40,3** cellules |
| ... au 1er décile | 16,1 |
| **témoin — autant de points tirés au hasard dans la même empreinte** | **319,6** |

⭐⭐⭐ **Huit fois mieux que le hasard.** Le témoin est obligatoire et il est de **même compte** :
sur une empreinte trouée, n'importe quel semis tombe parfois près d'un trou, donc 40 cellules
ne veulent rien dire sans les 320 qu'un semis aléatoire obtient sur la **même** empreinte.

```
uv run python src/encre/les_reperes_apparies.py \
    --json docs/mesures/les_reperes_apparies.json
uv run python src/figures/figure_les_reperes_apparies.py
```

⚠⚠ **Et la figure a attrapé une sur-affirmation de la prose que j'avais écrite** : j'y disais
les repères « répartis à l'intérieur », et le dessin montre qu'ils sont **groupés d'un côté** —
**12 sur 55** dans la boîte centrale. Ils sont dans l'**aire** du fragment et non sur son
contour, ce qui est déjà ce que les 34 carreaux de bord n'étaient pas ; ils ne sont pas
**étalés** pour autant, et la prose le dit maintenant.

⚠ Le contrôle négatif du module est un **décalage d'une demi-maille** et non « des trous
ailleurs » : ma première version mettait les repères dans les coins et ils **battaient quand
même** le témoin, parce que sur une empreinte dont les cibles sont sur une grille, un coin reste
systématiquement plus proche qu'un point tiré n'importe où. Le négatif juste est la panne
qu'on veut exclure — un recalage faux d'un demi-pas.

⚠ L'échelle des flèches est prise au **neuvième décile** (91 cellules) et non au maximum : un
appariement raté à **492** cellules — un repère accroché à un trou lointain — écrasait toutes
les autres flèches à l'invisible. **Le maximum n'est pas le champ, c'est son échec.**

> ⭐⭐ **Ce que C1 gagne** : 55 repères appariés, dans l'aire du fragment, avec un écart mesuré
> de 40 cellules en médiane. C'est la matière que ni le modèle lisse ni l'agrégation locale
> n'avaient — et elle vient d'une géométrie, pas de l'encre, donc la mesure d'encre qui suivra
> ne sera pas circulaire.

### ⚠⚠ Et ça corrige un de mes propres chiffres

J'ai écrit plus haut que le résidu vaut « **1,1 mm en médiane** ». C'est la norme du décalage
**entier** par carreau — or une bonne moitié de ce décalage est dans la direction **non
contrainte**. La composante réellement **mesurée** vaut **17 cellules, soit ~0,3 mm** en médiane.

⚠⚠⚠ **ET LE PARAGRAPHE QUI SUIVAIT EST ANNULÉ PAR LA SECTION SUIVANTE, PAS NUANCÉ.** J'écrivais :
*« près de la fenêtre mesurée, le résidu est grand — un décalage de (−104, −120) cellules y
remonte la carte publiée de 0,418 à 0,711 […] le résidu est donc très variable dans l'espace :
petit en médiane, de l'ordre de deux millimètres là où il compte. »* Les deux affirmations
tombent : **(−104, −120) était un maximum au BORD de son balayage**, donc une borne et non un
déplacement ; et sur **127 fenêtres** de l'empreinte les optima se serrent autour de
**(−24, 0)**, à 27 cases près. Ce qui reste vrai est que la fenêtre du régime du prix est
**atypique** — pas que le résidu varie.

### ⚠⚠⚠ Posée sur TOUTE l'empreinte, la question se renverse : le résidu est une TRANSLATION

> Mesure : `src/encre/le_residu_est_une_translation.py` (39 contrôles) →
> `docs/mesures/le_residu_est_une_translation.json`. Figure :
> `src/figures/figure_le_residu_est_une_translation.py` (16 contrôles), le 2026-09-05.
>
> ```
> uv run python src/encre/le_residu_est_une_translation.py --json docs/mesures/le_residu_est_une_translation.json
> uv run python src/figures/figure_le_residu_est_une_translation.py --sortie docs/images/75_le_residu_est_une_translation.png
> ```

⚠⚠⚠ **Tout ce qui précède a été jugé sur UNE fenêtre** — celle du régime du prix, retenue parce
qu'elle est la plus encrée. Une fenêtre n'est pas une mesure, et la même validation refaite sur
**127 fenêtres** de l'empreinte ne dit pas la même chose.

![le résidu est une translation, pas un champ](images/75_le_residu_est_une_translation.png)

#### 1. Ce que chaque fenêtre demande, quand on la laisse choisir

| | valeur |
|---|---:|
| décalage préféré, **médiane** sur 127 fenêtres | **(−24, 0)** cases, soit **425 µm** |
| **dispersion** de ces préférences | (16,8 ; 20,6) cases, soit **471 µm** |
| optima touchant le bord du balayage | 15 sur 127 |
| amplitude du **champ de bord** (norme médiane) | **60,4** cases |
| amplitude du **champ des repères** | **40,3** cases |

⭐⭐⭐ **Les fenêtres s'accordent ; les champs bougent plus qu'elles ne le demandent.** Les deux
champs candidats déplacent de **40** et **60** cases là où les fenêtres ne divergent que de
**27** — un champ dont l'amplitude dépasse le désaccord qu'il corrige n'en corrige pas un, il en
**invente** un.

#### 2. Une CONSTANTE bat les deux champs, et de loin

AUC médiane de la carte publiée, sur les **127** fenêtres de l'empreinte :

| décalage constant | AUC médiane | fenêtres améliorées |
|---|---:|---:|
| aucun — l'affine publiée | 0,7547 | — |
| **médiane du champ de bord**, (−13, +2) | **0,8523** | **116 sur 127** |
| médiane du champ des repères, (−3,2 ; +8,2) | 0,7776 | 81 sur 127 |
| **optimum balayé sur l'encre**, (−24, 0) | **0,885** | — |

⚠ Ce maximum-là est **intérieur** au balayage (±48 cases), contrairement au (−104, −120) publié
plus haut qui touchait sa borne. `maximum_au_bord` est **asserté**, pas noté.

Et le champ contre **sa propre constante**, sur les 42 fenêtres où le champ de bord répond :

| | AUC médiane | gain | améliorées |
|---|---:|---:|---:|
| champ de bord | 0,6534 | +0,0354 | 25 sur 42 |
| **sa constante** (−13, +2) | **0,7382** | **+0,0669** | **36 sur 42** |

#### 3. Et ça déplace le 0,756 de référence

L'accord de la carte publiée avec les étiquettes, sur **toute** l'empreinte et non par fenêtre :

| | AUC |
|---|---:|
| l'affine publiée | **0,7561** |
| avec la constante des bords (−13, +2) | 0,8254 |
| avec l'optimum des fenêtres (−24, 0) | **0,8571** |

⚠⚠ **Le 0,756 qui sert de référence à tout ce lot mesurait donc aussi un défaut de recalage.**
Translater les étiquettes de 425 µm — un demi-caractère — le porte à **0,857**.

#### 4. Les deux témoins obligatoires

| témoin | ce qu'il donne | ce qu'il exclut |
|---|---|---|
| la **carte d'encre mélangée**, même plan | plat : 0,4989 à 0,5014, étendue **0,0025** | que le relief du plan A soit celui de l'**empreinte** et non de l'encre |
| les **positions des repères mélangées** | 42,8 au mieux de 20 tirages | que le champ des repères soit une **constante déguisée** |

#### 5. Ce que les repères gagnent, et ce que les bords perdent

Laisser-un-dehors à 300 cases, chacun contre **son** champ nul et **ses** positions mélangées :

| | erreur médiane | champ nul | meilleur mélange | verdict |
|---|---:|---:|---:|---|
| **champ des repères** (55) | **31,8** | 40,2 | 42,8 | ✅ bat les deux |
| champ de bord (34 carreaux) | 77,5 | 60,5 | 58,8 | ❌ échoue aux deux |

⭐⭐ **Les repères sont bel et bien prédictifs dans l'espace, les carreaux non** — ce que
`le_recalage_local` avait établi sur la composante normale, retrouvé ici par un autre chemin.

⚠⚠ **Et pourtant c'est la constante des BORDS qui gagne sur l'encre, pas celle des repères** :
(−13, +2) est à **11** cases de l'optimum quand (−3,2 ; +8,2) est à **22**. La raison est
géométrique — les repères sont **groupés d'un côté**, donc leur médiane est le déplacement de
**leur** quartier ; les 34 carreaux sont mauvais un par un mais **répartis**, donc leur médiane
échantillonne le fragment. ⭐ **Quand ce qu'on cherche est une constante, la couverture bat la
précision.**

#### 6. Et le plan des SILHOUETTES dit pourquoi les bords ont échoué

Le même plan de décalages, jugé cette fois sur le Dice du masque recalé contre le support publié :

| plan | étendue | sommet |
|---|---:|---|
| **A**, l'**encre** (AUC) | **0,4234** | (−24, 0) |
| **B**, les **silhouettes** (Dice) | 0,0315 | (−8, −8) |
| **C**, le **témoin** mélangé (AUC) | 0,0025 | — |

⚠⚠⚠ **Les silhouettes arbitrent — leur étendue vaut douze fois le plancher de bruit — mais
treize fois moins fort que l'encre, et elles pointent ailleurs.** C'est l'explication de tout le
programme des bords : un champ ajusté sur les silhouettes est ajusté sur le **moins** informatif
des deux signaux, et **biaisé** d'une quinzaine de cases par rapport à celui qui compte.

#### 7. Ce que ça change pour C1

1. ⭐ **Le recalage des deux aplatissements se corrige d'abord par une TRANSLATION**, pas par un
   champ : (−24, 0) cases, **425 µm**, et ça vaut **+0,10 d'AUC** sur toute l'empreinte. ⚠ Elle
   est **mesurée et pas appliquée** : rien dans le dépôt ne la retranche encore, et c'est la
   tranche suivante — `affine_par_boites` gagne un terme, ou l'appelle qui la veut la passe.
2. **Ce qui reste après elle est une dispersion de 471 µm** — l'ordre d'une lettre — et c'est
   *elle* qu'un champ devrait capturer. Les **55 repères** sont le seul matériau qui en prédise
   quelque chose, mais ils ne couvrent qu'un quartier : les densifier **ailleurs** est ce qui
   reste à faire, pas les remplacer.
3. ⚠ **Ce que ça ne dit PAS** : d'où vient la translation. Le plan B écarte que les silhouettes
   la voient de la même façon ; il ne dit pas si ce sont les **étiquettes** qui sont posées de
   travers dans leur aplatissement ou la **carte publiée** dans le sien. Les deux se corrigent
   pareil ici — pas ailleurs.

### ⚠⚠⚠ Et la question suivante n'est pas « laquelle est la meilleure » mais « laquelle a le DROIT d'être appliquée »

> Mesure : `src/encre/la_translation_applicable.py` (15 contrôles) →
> `docs/mesures/la_translation_applicable.json`. Figure :
> `src/figures/figure_la_translation_applicable.py` (9 contrôles), le 2026-09-05.
>
> ```
> uv run python src/encre/la_translation_applicable.py --json docs/mesures/la_translation_applicable.json
> uv run python src/figures/figure_la_translation_applicable.py --sortie docs/images/75_la_translation_applicable.png
> ```

⚠⚠⚠ **Appliquer le (−24, 0) trouvé sur l'encre serait circulaire.** L'accord de l'encre
deviendrait élevé **par construction**, et le chiffre cesserait de mesurer quoi que ce soit. La
règle est donc de **provenance** et non de valeur : une translation tirée de la géométrie —
silhouettes, carreaux, repères — n'a jamais vu d'encre, donc l'encre reste un arbitre extérieur
après qu'on l'a appliquée. Une translation tirée de l'encre est un **plafond**. `applicables()`
exclut la seconde **par construction**, pas par vigilance.

![ce que la géométrie a le droit de corriger](images/75_la_translation_applicable.png)

| candidate | provenance | décalage | Dice | AUC | part du plafond |
|---|---|---:|---:|---:|---:|
| aucune correction | géométrie | (0, 0) | 0,974601 | 0,7561 | 0 % |
| **optimum des silhouettes** ⭐ retenue | géométrie | (−8, −8) | **0,975255** | 0,7943 | **37,8 %** |
| médiane des carreaux de bord | géométrie | (−13, +2) | 0,973854 | **0,8254** | 68,6 % |
| médiane des repères intérieurs | géométrie | (−3,2 ; +8,2) | 0,972523 | 0,7700 | 13,7 % |
| optimum sur l'encre | **encre** | (−24, 0) | 0,97263 | **0,8571** | 100 %, ⛔ non applicable |

⚠ La retenue est celle qui **maximise le Dice** parmi les applicables, et ce critère est déclaré
**avant** de regarder l'encre — sinon « la meilleure candidate géométrique » serait choisie sur
l'encre et la règle de provenance ne servirait à rien.

#### ⚠⚠ La géométrie n'IDENTIFIE pas la translation, elle la borne

Quatre critères sans encre donnent quatre réponses étalées sur **16,9 cases**, qui atteignent de
**13,7 %** à **68,6 %** du plafond. La retenue en atteint **37,8 %**, et il reste **17,9 cases**
— **317 µm** — entre elle et l'optimum de l'encre. Ce n'est donc pas un nombre que la géométrie
rend, c'est un **intervalle**, et sa largeur est du même ordre que la translation elle-même.

#### ⚠⚠⚠ Et le fait qui explique tout : le critère des silhouettes est CONTRAIRE

**Les trois translations qui font monter l'AUC font toutes baisser le Dice** — y compris
l'optimum de l'encre, qui rend le meilleur accord d'encre (0,8571) avec un Dice (0,97263)
**inférieur** à celui de l'affine non corrigée (0,974601).

> Le recouvrement des silhouettes n'est pas seulement **treize fois moins sensible** que l'encre
> (`0,0315` d'étendue contre `0,4234`) : dans la plage qui compte, il pointe **dans l'autre
> sens**. Toute procédure de recalage pilotée par le recouvrement des contours s'éloigne donc de
> la bonne réponse en croyant s'en approcher — et c'est, en une phrase, pourquoi le champ de
> bord, le modèle lisse et l'agrégation locale ont tous échoué.

#### ✅ Le contrôle de signe, au dernier chiffre

Corriger l'**affine** et décaler la **lecture** sont deux façons d'appliquer la même translation.
Elles doivent donner le même accord, et elles le donnent : **0,79431 contre 0,79431, écart
0,0000**. Une correction appliquée à l'envers ne lève rien — elle rend simplement un accord plus
bas, ce qui ressemble à une mauvaise candidate et non à un bug — donc ce contrôle n'était pas
remplaçable par une relecture.

#### Ce que ça change pour C1

1. ⭐ **Une correction géométrique est disponible et légitime** : `corriger(affine, −8, −8)`,
   Dice **0,975255** contre 0,974601, et l'encre le confirme de l'extérieur (**0,7943** contre
   0,7561). Elle est publiée dans `la_translation_applicable.json` avec sa provenance.
2. ⚠⚠ **Elle ne suffit pas, et on sait de combien** : 317 µm de résidu que les silhouettes ne
   voient pas, soit un demi-caractère.
3. ⚠⚠⚠ **Et il ne faut PAS chercher mieux du côté des contours.** Le critère y est contraire :
   ce qui reste ne se gagnera qu'avec de la matière **intérieure**, c'est-à-dire les repères,
   qui sont le seul champ prédictif mesuré — et qui doivent être densifiés **ailleurs** que dans
   leur quartier.

### ⚠⚠⚠ Le goulot n'était pas le fragment, c'était le FICHIER — et les 71 trous du support étaient du bruit de compression

> Mesure : `src/encre/les_reperes_a_pleine_resolution.py` (20 contrôles) →
> `docs/mesures/les_reperes_a_pleine_resolution.json`. Figure :
> `src/figures/figure_les_reperes_a_pleine_resolution.py` (10 contrôles), le 2026-09-05.
>
> ```
> uv run python src/encre/les_reperes_a_pleine_resolution.py --json docs/mesures/les_reperes_a_pleine_resolution.json
> uv run python src/figures/figure_les_reperes_a_pleine_resolution.py --sortie docs/images/75_les_reperes_a_pleine_resolution.png
> ```

⭐⭐⭐ **Le segment publie AUSSI la carte d'encre à sa résolution native** — `ink-detection`,
**26 440 × 15 060**, un `.tif` de **20,5 Mo** — à côté du `ink-detection-downsampled` réduit ×8
en `.jpg` que tout ce lot lisait par habitude. L'échelle du transport passe de **0,12** à
**0,97**, donc un trou de 64 pixels du masque reste un trou de 64 pixels.

![les repères à pleine résolution, et leur couverture](images/75_les_reperes_a_pleine_resolution.png)

**Côté source, le goulot disparaît d'un coup** : les **314** trous utilisables du masque sont
**tous** transportables, contre **55** au réduit.

#### ⚠⚠⚠ Mais côté cible il s'effondre, et le compte brut dit pourquoi

| support | composantes de fond | intérieures | d'aire ≥ 4 |
|---|---:|---:|---:|
| le réduit publié (`.jpg`) | **420** | 419 | **153** |
| **témoin** : le plein réduit ×8 par la même règle | **19** | 18 | 15 |
| le plein (`.tif`) | 37 | 36 | 31 |

⚠⚠⚠ **Réduire le support à pleine résolution par la même règle ne rend pas 420 composantes, il
en rend 19.** Les trous du support réduit ne sont donc pas dans la **matière**, ils sont dans le
**fichier** : un `.jpg` est compressé avec perte et crénelle les bords à fort contraste,
c'est-à-dire précisément le pourtour des vrais trous. Le témoin est monté en faveur de ce qu'il
conteste — la règle de réduction est « plein dès qu'il y a de la matière », la plus généreuse.

> **Ce qui est corrigé, et c'était publié six heures plus tôt** : « le support de la carte
> publiée porte les trous du fragment, donc il est un masque de fait » est **faux**. Il en porte
> **36**, quand le masque en a **348**. Le support n'est pas un masque du fragment ; c'est une
> carte de détecteur qui en montre une poignée.

#### ⛔ Ce que je croyais survivre, et qui ne survit pas non plus

J'ai écrit ici que les **314** repères se posent **7,7 fois plus près** de ces 36 vides que le
hasard — **796 px** contre **6 114 px** — et que « les vides qui existent sont ceux du fragment,
c'est le compte qui était faux, pas l'appariement ». ⚠⚠⚠ **Faux aussi.** Le témoin uniforme casse
la place ET le groupement ; le témoin qui ne casse que la place met la vraie position **6ᵉ sur
21** (p = 0,29). Il n'y a pas d'appariement. Voir la section suivante.

#### ⚠⚠ Et la figure impose une seconde nuance : le gain est de la DENSITÉ, pas de l'étendue

| | 55 repères (réduit) | 314 repères (plein) |
|---|---:|---:|
| couverture à 500 px (1,1 mm) | 4,9 % | **10,5 %** |
| … à 1 000 px (2,2 mm) | 12,3 % | 23,9 % |
| … à 2 000 px (4,4 mm) | 27,6 % | 52,1 % |
| … à 4 000 px (8,9 mm) | 53,5 % | **94,0 %** |
| **étendue du 80 % central** | 24,1 × 16,1 % de la carte | **28,7 × 18,1 %** |

⚠ **Cinq fois et demie plus de repères pour un cinquième d'étendue en plus.** Le dessin le montre
sans ambiguïté : les 314 suivent **la même bande** que les 55. Multiplier la densité là où il y
avait déjà de la matière ne donne rien à un recalage qui manque de matière **ailleurs**.

#### Ce que ça change pour C1

1. ✅ **Le côté source est réglé** : 314 repères au lieu de 55, sans rien demander à personne —
   il suffisait de lire l'autre fichier. ⚠ Et c'est une leçon de méthode : le fichier par
   défaut d'un index n'est pas le meilleur fichier de l'index.
2. ⚠⚠⚠ **Le goulot a DÉMÉNAGÉ, il n'a pas disparu.** Il est maintenant du côté **cible** — 36
   vides publiés contre 348 dans le masque — et du côté **étendue** : une seule bande du
   fragment.
3. ⚠⚠ **Et la voie « le support est un masque de fait » est fermée.** Ce qui reste ouvert est ce
   que `68` §4 nommait déjà : demander un **masque de surface publié** au régime du prix, ou les
   étiquettes rendues dans son repère.

### ⛔⛔ Et le témoin JUSTE enterre l'appariement : la vraie place des repères n'a rien de particulier

> Mesure : `src/encre/le_temoin_de_meme_forme.py` (14 contrôles) →
> `docs/mesures/le_temoin_de_meme_forme.json`. Figure :
> `src/figures/figure_le_temoin_de_meme_forme.py` (8 contrôles), le 2026-09-05.
>
> ```
> uv run python src/encre/le_temoin_de_meme_forme.py --json docs/mesures/le_temoin_de_meme_forme.json
> uv run python src/figures/figure_le_temoin_de_meme_forme.py --sortie docs/images/75_le_temoin_de_meme_forme.png
> ```

⚠⚠⚠ **LE TÉMOIN DES DEUX TRANCHES PRÉCÉDENTES ÉTAIT TROP FACILE, ET C'EST MA FAUTE.** Elles
jugeaient l'appariement contre un semis tiré **uniformément** dans l'empreinte. Or les repères
sont **groupés** — leur 80 % central tient sur 29 % × 18 % de la carte — et les vides du support
sont eux aussi peu nombreux et localisés. Un semis uniforme est donc plus loin de tout **par
construction** : il casse **deux** choses à la fois, la place et le groupement, donc il ne peut
pas dire laquelle des deux explique un bon score.

⭐⭐⭐ **Le témoin juste garde la forme et ne casse que la place** : le même nuage de 314 repères,
sa géométrie interne intacte au bit près, posé ailleurs dans l'empreinte, vingt fois.

![la vraie place des repères n'a rien de particulier](images/75_le_temoin_de_meme_forme.png)

| | distance médiane d'appariement |
|---|---:|
| **la vraie place** | **796 px** |
| le témoin de MÊME FORME, meilleure des 20 poses | **638 px** |
| … sa médiane | 1 015 px |
| … sa pire pose | 1 411 px |
| le témoin **uniforme** d'avant | 6 114 px |

> ⛔ **Rang de la vraie place : 6ᵉ sur 21. p = 0,29.** Cinq poses au hasard font mieux qu'elle.
> Il n'y a **pas de correspondance** entre les trous du masque et les vides du support : le
> « ×8 » de la première tranche et le « ×7,7 » de la deuxième étaient le **groupement**, pas un
> appariement.

⚠ Le semis uniforme est à **6 114 px**, c'est-à-dire **hors** de l'étendue des vingt poses
(576 à 1 473). C'est la mesure de sa facilité : il ne pouvait pas ne pas être battu.

#### ⭐ Ce qui reste établi, et c'est solide

Le support publié **est un masque**, et ça se lit dans l'histogramme sans ambiguïté :
**37,5 %** des pixels exactement à zéro, puis un **vide de 27 niveaux** avant la première valeur
rendue (28). Un détecteur qui prédirait peu d'encre occuperait 1, 2, 3 ; un pipeline qui
**masque** écrit un zéro franc. ⚠ C'est donc bien un masque — celui du **régime du prix** — et
c'est pour ça qu'il n'a que 36 vides intérieurs : sa segmentation n'a pas les trous de l'autre
aplatissement, elle a les siens.

#### Ce que ça change pour C1

1. ⛔ **La voie « prendre les cibles dans la carte publiée » est FERMÉE**, et pas faute de
   résolution : à pleine résolution il y a 314 repères d'un côté et 14 cibles utilisables de
   l'autre, sans correspondance mesurable.
2. ⚠⚠⚠ **Et une leçon de méthode qui vaut pour tout le dépôt** : un témoin doit casser **une
   seule** chose. Celui qui en casse deux ne peut pas dire laquelle comptait, et il rend un
   rapport flatteur — ici **×7,7** — qui ne mesure que le confond qu'on a oublié de contrôler.
3. ⭐ Ce qui reste ouvert est ce que `68` §4 nommait déjà, et c'est maintenant la **seule** voie :
   un **masque de surface publié** au régime du prix, ou les étiquettes rendues dans son repère.

### Ce qui reste de C1, et c'est maintenant précis

1. ✅✅ **Ce n'était pas un champ, c'était une TRANSLATION — et sa part applicable est
   PUBLIÉE.** ⚠ Ce qu'on a le droit de retrancher est la translation **géométrique**
   (−8, −8), pas celle de l'encre : `la_translation_applicable.json` la porte avec sa
   provenance, elle gagne 0,7561 → **0,7943** d'accord publié, soit **37,8 %** du plafond, et il
   reste **317 µm** que les silhouettes ne voient pas. ⚠⚠⚠ Et il ne faut pas chercher mieux du
   côté des contours : dans la plage qui compte, leur recouvrement pointe **dans l'autre sens**.
   Le champ à
   34 carreaux, le modèle lisse et l'agrégation locale ont tous échoué, et la mesure sur
   **127 fenêtres** dit pourquoi : les fenêtres s'accordent toutes sur **(−24, 0)** cases
   (**425 µm**) à 27 cases près, quand les champs candidats déplacent de **40** et **60**. Une
   simple constante porte l'AUC médiane de **0,755 à 0,852** en améliorant **116 fenêtres sur
   127**, et l'accord publié sur toute l'empreinte de **0,756 à 0,857**. ⚠⚠ Le plan des
   **silhouettes** explique l'échec des bords : il arbitre **treize fois moins fort** que celui
   de l'encre et pointe ailleurs — un champ ajusté dessus l'est sur le mauvais signal.
   ⭐ **Ce qui reste à faire est plus petit et mieux défini** : après la translation il subsiste
   une dispersion de **471 µm**, l'ordre d'une lettre. Les **55 repères** sont le seul matériau
   qui en prédise quelque chose — laisser-un-dehors **31,8** contre **40,2** au champ nul et
   **42,8** au meilleur mélange de positions, là où les 34 carreaux échouent aux deux (77,5
   contre 60,5 et 58,8). ⭐ **Et ils sont désormais 314 et non 55** : il suffisait de lire la
   carte publiée à sa résolution native au lieu de sa réduction ×8. ⛔⛔ **Mais ils n'ont PAS de
   vis-à-vis** : contre un témoin qui garde la forme du nuage, la vraie place est la **6ᵉ sur
   21** (p = 0,29), donc l'appariement mesuré aux deux tranches précédentes était le
   **groupement** des repères. Le support publié est bien un **masque** — 37,5 % de zéros puis un
   vide de 27 niveaux — mais c'est celui du **régime du prix**, avec **36** vides à lui et non les
   348 de l'autre aplatissement. **La voie est fermée ; il faut un masque de surface publié.**
2. **Une fenêtre choisie dans un repère COMMUN**, pas dans la grille de chaque régime : les deux
   campagnes ont atterri sur deux régions différentes (27,8 % et 91,1 % d'encre), donc leurs
   nombres ne se comparaient pas même sans le problème de recalage.
3. **≥ 40 tuiles** pour un intervalle (`64` §1, σ = 0,2243), au lieu d'une fenêtre.
4. ⚠ **L'unité de notation reste à choisir séparément de la fenêtre du modèle** : 256 px valent
   **2 397 µm** au régime du prix contre 614 en production — près de quatre lettres au lieu d'une.
   La tuile équivalente à une lettre y ferait **66 px**.
- **≥ 40 tuiles** au lieu d'une fenêtre : l'intervalle de `64` §1 (σ = 0,2243) demande 40 tuiles
  pour séparer une AUC de 0,599 de 0,5. Une fenêtre unique ne donne pas d'intervalle.
- ⚠ **Et l'unité de notation reste à choisir séparément de la fenêtre du modèle** : une tuile de
  256 px vaut **2 397 µm** au régime du prix contre 614 en production — près de quatre lettres au
  lieu d'une, donc la garantie anti-hallucination ne se transporte pas. La tuile équivalente à une
  lettre y ferait **66 px**.

### ⭐⭐⭐ Et l'index publiait TREIZE SPIRES de ce fragment, que rien n'avait jamais ouvertes

> Mesure : `src/nappe/les_wraps_publies.py` (10 contrôles) →
> `docs/mesures/les_wraps_publies.json`. Figure :
> `src/figures/figure_les_wraps_publies.py` (9 contrôles), le 2026-09-05.
>
> ```
> uv run python src/nappe/les_wraps_publies.py --json docs/mesures/les_wraps_publies.json
> uv run python src/figures/figure_les_wraps_publies.py --sortie docs/images/75_les_wraps_publies.png
> ```

⚠⚠⚠ **L'index connaît 39 segments pour `PHerc0500P2`, dont TREIZE nommés `wrap01` à `wrap13`**,
chacun publiant sa surface en `tifxyz` **sur les trois volumes** (2,215 / 4,317 / 9,362 µm), plus
sa carte d'encre pleine résolution. **Aucune mesure du dépôt ne les avait jamais ouvertes.** Tout
le travail sur la chaîne, la spire et l'écart inter-feuilles a été fait en reconstruisant depuis
le volume brut, alors qu'une **vérité de terrain du déroulement** était publiée à côté.

⭐ **C'est la cinquième fois que cet angle mort coûte quelque chose**, et cette fois c'est l'auteur
qui l'a rouvert : *« regarde sur les autres serveurs au cas où »*. Le référent avait été déclaré
absent faute d'avoir interrogé un serveur ; ici c'est un dossier de l'index qu'on n'avait jamais
énuméré. **Ce qu'on croit absent doit être cherché avant d'être reconstruit.**

![treize spires publiées, et l'écart qui les sépare](images/75_les_wraps_publies.png)

#### Est-ce que ce sont vraiment des spires consécutives ? — oui, et c'est mesuré

| saut de rang | paires | écart médian |
|---:|---:|---:|
| **1** (voisines) | 12 | **135,5 µm** |
| 2 | 11 | 320,7 µm  (×2,37) |
| 3 | 10 | 454,6 µm  (×3,35) |

⭐⭐⭐ **L'écart croît avec le rang**, donc ce sont bien des tours **empilés** et non treize
morceaux quelconques. Et l'écart entre voisines, **135,5 µm**, tombe à **8 %** de l'attendu
**147,4 µm** — mesuré ailleurs dans le dépôt (`la_surface_et_la_feuille`), **sur un autre
rouleau**. Un accord avec une prédiction extérieure vaut mieux qu'un accord avec soi-même.

⚠ **Quatre paires sur douze s'écartent de moitié ou plus** et elles sont dessinées comme les
autres, pas gommées : 4→5 à 232 µm, 10→11 à 292, 11→12 à 327, et 12→13 à **65** — plus près
qu'une feuille. La numérotation n'est donc pas géométriquement parfaite partout, et les p90
montent jusqu'à 3 mm là où deux spires ne se recouvrent que par un bord.

#### Ce que ça ouvre

1. ⭐⭐⭐ **Une vérité de terrain du DÉROULEMENT, publiée et exacte**, sur laquelle une chaîne
   reconstruite peut enfin être **notée** au lieu d'être seulement cohérente avec elle-même.
2. ⭐⭐ **Un repère commun entre les deux régimes, gratuit** : chaque spire publie son `tifxyz`
   sur le volume de production **et** sur celui du prix. La tâche « une fenêtre choisie dans un
   repère COMMUN » cesse d'être un problème d'estimation ; c'est une lecture.
3. ⚠ Et une question à poser avant de s'en servir : les treize spires couvrent-elles la même
   région que le segment `500P2_front` sur lequel tout C1 a été bâti, ou une autre ?

#### ⭐⭐ Et l'angle mort est désormais outillé, parce qu'il a coûté cinq fois

> Mesure : `src/depot/ce_que_les_serveurs_publient.py` (13 contrôles) →
> `docs/mesures/ce_que_les_serveurs_publient.json`, le 2026-09-05.
>
> ```
> uv run python src/depot/ce_que_les_serveurs_publient.py --fragment PHerc0500P2
> ```

L'inventaire compare les deux serveurs à l'index **en cache** du dépôt, et le résultat corrige
mon hypothèse : **39 segments sur S3, 39 dans l'index, 0 écart**. L'angle mort n'était donc pas
la péremption du cache — c'était que **personne ne l'avait énuméré**.

⭐⭐⭐ **Et la vraie cause structurelle est là** : les deux serveurs ne publient pas la même chose.

| | S3 | `dl.ash2txt.org` |
|---|---|---|
| `segments/` (dont les 13 spires) | **oui** | non |
| `paths/` (dont les étiquettes et le masque) | non | **oui** |
| `photos/` | **oui** | non |
| `cases/`, `multispectral/` | non | **oui** |
| `representations/`, `volumes/` | oui | oui |

Les étiquettes viennent de `dl`, les segments de `S3`, et **personne n'avait jamais croisé les
deux listages**. « Regarder sur les autres serveurs » cesse d'être une superstition : c'est une
règle avec une base mesurée, et elle est maintenant une commande.

⚠ Le refus fait partie de l'outil : un serveur injoignable rend une liste vide, et comparer une
liste vide à un index plein dirait « l'index a tout inventé ». Un listage vide est **refusé**,
pas interprété — c'est la panne qui ressemble le plus à un résultat.

⚠⚠ Et un défaut de mon propre outil, attrapé avant publication : `index_local` ignorait son
argument et rendait les **311** segments des quarante-cinq objets du catalogue, d'où un faux
« 272 segments à l'index seulement ». Un inventaire qui crie faux est un inventaire qu'on cesse
d'écouter. Le filtre par objet est désormais **asserté dans les deux sens**.

#### ⛔ Et les treize spires ne sont PAS la région de C1 : elles en sont une seconde

> Mesure : `src/nappe/lemprise_des_spires.py` (15 contrôles) →
> `docs/mesures/lemprise_des_spires.json`. Figure :
> `src/figures/figure_lemprise_des_spires.py` (9 contrôles), le 2026-09-05.
>
> ```
> uv run python src/nappe/lemprise_des_spires.py --json docs/mesures/lemprise_des_spires.json
> uv run python src/figures/figure_lemprise_des_spires.py --sortie docs/images/75_lemprise_des_spires.png
> ```

![où le segment de C1 tombe parmi les treize spires](images/75_lemprise_des_spires.png)

⚠⚠ **Deux seuils, et aucun n'est choisi.** Le seuil de coïncidence vaut **67,75 µm**, la moitié
de l'écart mesuré entre spires consécutives : sous une demi-épaisseur, deux surfaces sont la
**même** feuille. Et la barre du verdict est le **plafond entre spires distinctes** — la part
maximale d'une spire couverte par une **autre** spire, **56,74 %**, mesurée sur les 156 paires.
Franchir ce que deux feuilles différentes atteignent au mieux, c'est être la même feuille.

| | valeur |
|---|---:|
| part du segment à moins du seuil d'**une** spire | **0,0 %** sur les treize |
| … de leur **union** | **0,0 %** |
| barre mesurée (plafond entre spires distinctes) | 56,74 % |
| **distance minimale** segment → union | **2 134 µm** |
| … soit, en épaisseurs de feuille | **15,7** |
| distance médiane | 8 458 µm |

⛔ **Le segment `500P2_front`, sur lequel toute la colonne C est bâtie, est AILLEURS** : il ne
colle pas mieux aux spires que deux spires distinctes ne collent entre elles, et sa surface la
plus proche est à **seize épaisseurs**. Les treize spires ne donnent donc **aucun voisinage** à
C1 — elles sont une **seconde région** du fragment.

⭐⭐ **Ce qui reste, et c'est un gain net** : le corpus double. Treize surfaces de plus, avec une
géométrie exacte **sur les trois volumes**, là où `500P2_front` n'en couvrait qu'une région — et
elles portent chacune leur carte d'encre pleine résolution.

⚠ Une nuance que la calibration a rendue visible : **les spires publiées ne sont pas disjointes**.
La meilleure paire se recouvre à **56,7 %** sous une demi-épaisseur, donc « treize tours
consécutifs » ne veut pas dire treize feuilles séparées — certaines partagent largement une même
feuille. Le compte de tours et le compte de feuilles ne sont pas le même nombre.

#### ⭐⭐⭐ Et la PRIMITIVE du déroulement est validée sur cette vérité de terrain

> Mesure : `src/nappe/le_pas_normal_atteint_la_spire.py` (11 contrôles) →
> `docs/mesures/le_pas_normal_atteint_la_spire.json`. Figure :
> `src/figures/figure_le_pas_normal.py` (9 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/le_pas_normal_atteint_la_spire.py --json docs/mesures/le_pas_normal_atteint_la_spire.json
> uv run python src/figures/figure_le_pas_normal.py --sortie docs/images/75_le_pas_normal.png
> ```

⚠⚠⚠ **Toute la colonne « chaîne » repose sur une supposition jamais confrontée à autre chose
qu'elle-même** : *depuis une feuille, avancer d'un écart inter-feuilles le long de la normale
tombe sur la feuille voisine*. C'est ce que fait un dérouleur, pas après pas, et si c'est faux
tout ce qui suit dérive. Les treize spires publiées la rendent **falsifiable**.

![le pas normal contre ses deux témoins](images/75_le_pas_normal.png)

| | distance médiane à la spire suivante |
|---|---:|
| **ne rien faire** (pas nul) | **135 µm** |
| **un** écart le long de la normale | **60 µm** |
| **deux** écarts | 151 µm |

⭐⭐⭐ **Le V est là, et c'est lui qui prouve quelque chose.** Le pas nul retombe sur l'écart
inter-feuilles mesuré (135 contre 135,5 µm) — donc les spires sont bien voisines. Le pas simple
le divise par plus de deux. Et le **double dépasse** : la distance franchie est donc bien celle
d'**une feuille**, pas une quantité quelconque qui améliorerait tout.

**11 paires sur 12** sont rapprochées, et ⭐ **le sens retenu est le même pour les douze** — les
grilles publiées partagent une orientation, ce qu'aucune mesure n'avait établi.

⚠ **La seule paire qui échoue est 12 → 13**, dont l'écart vaut **63 µm**, soit moins d'une
demi-feuille : un pas d'une feuille entière y dépasse forcément. C'est la même paire anormale que
la tranche précédente avait déjà signalée, et elle échoue pour la raison qu'on lui connaît.

⚠⚠ **Ce que ça ne dit pas** : le pas ne tombe pas *sur* la feuille suivante, il tombe **à 60 µm**
d'elle — 44 % d'un écart. C'est la précision réelle de la primitive, et elle suffit exactement à
ce qu'il faut : ne pas confondre une feuille avec sa voisine. Elle ne suffit pas à se passer d'un
recalage local ensuite.

#### ⭐⭐⭐ Et le graal, ramené à une mesure : un dérouleur aveugle tient DEUX tours

> Mesure : `src/nappe/derouler_par_le_pas_normal.py` (9 contrôles) →
> `docs/mesures/derouler_par_le_pas_normal.json`. Figure :
> `src/figures/figure_derouler_par_le_pas_normal.py` (11 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/derouler_par_le_pas_normal.py --json docs/mesures/derouler_par_le_pas_normal.json
> uv run python src/figures/figure_derouler_par_le_pas_normal.py --sortie docs/images/75_derouler_par_le_pas_normal.png
> ```

⚠⚠⚠ **Dérouler, ce n'est pas faire un pas, c'est les enchaîner.** La primitive vaut 60 µm sur un
pas ; la question qui décide est *au bout de combien de tours l'erreur dépasse une feuille* — car
à ce moment-là le dérouleur ne sait plus **sur laquelle** il est, et tout ce qu'il écrit ensuite
est faux.

![combien de tours un dérouleur aveugle survit-il](images/75_derouler_par_le_pas_normal.png)

Le protocole est **aveugle par construction** : la grille est conservée à chaque pas, donc les
normales du tour suivant se calculent sur la surface **prédite**. ⚠ Un **seul bit de
supervision**, déclaré et compté : le sens de la normale, fixé au premier pas. Le rechoisir à
chaque tour en regardant la cible reviendrait à souffler la route.

| tours | erreur | ne pas bouger |
|---:|---:|---:|
| 1 | **52 µm** | 129 µm |
| 2 | **102 µm** | 311 µm |
| 3 | 135 µm | 418 µm |
| 6 | 230 µm | 920 µm |
| 12 | **689 µm** | 1 648 µm |

⛔ **La feuille est perdue au tour 2** : l'erreur dépasse la demi-épaisseur (67,75 µm), donc le
dérouleur ne peut plus dire sur quelle feuille il se trouve.

⭐⭐ **Et pourtant il déroule.** Il bat l'immobilité à **chacun des douze tours**, deux à trois
fois — à douze tours il est à 689 µm quand ne rien faire en met 1 648. Ce n'est pas un échec du
pas normal, c'est la mesure de ce qui lui manque.

⭐⭐⭐ **La dérive vaut 53 µm par tour**, soit **39 % d'une feuille — ajustée par moindres carrés
sur toute la marche**, pas prise entre deux extrémités. C'est *le* chiffre à battre : **c'est
exactement ce qu'un recalage sur la matière doit tuer à chaque pas.** La feuille suivante est
toujours dans la bonne direction ; elle est juste un peu plus loin ou un peu plus près que
l'épaisseur nominale, et personne ne recale.

⚠ La grille fond de **1 983 à 536** cellules sur douze tours — une normale demande quatre voisins
valides, donc un anneau part par tour. Le compte est rendu **à côté** de l'erreur : un dérouleur
qui « réussirait » en ne gardant que trois cellules n'aurait pas déroulé, il aurait rétréci.

⚠ Et la marche n'est pas monotone (306 µm au tour 5, 230 au tour 6) : les spires publiées ont
elles-mêmes leurs irrégularités, déjà signalées.

#### ⭐⭐ Et la dérive est à UN CINQUIÈME un biais, le reste une dispersion

> Mesure : `src/nappe/la_derive_est_elle_un_biais.py` (9 contrôles) →
> `docs/mesures/la_derive_est_elle_un_biais.json`. Figure :
> `src/figures/figure_la_derive_est_elle_un_biais.py` (9 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/la_derive_est_elle_un_biais.py --json docs/mesures/la_derive_est_elle_un_biais.json
> uv run python src/figures/figure_la_derive_est_elle_un_biais.py --sortie docs/images/75_la_derive_est_elle_un_biais.png
> ```

⚠⚠⚠ **Cette question vient avant tout recalage lourd.** Un raccrochage à la matière demande de
lire le volume ; il serait absurde de le construire si les 53 µm par tour venaient simplement
d'une **longueur de pas mal estimée**. Un biais est une constante — il se retranche une fois et
disparaît. Une dispersion, non.

![la dérive du pas : un cinquième de biais, le reste en dispersion](images/75_la_derive_est_elle_un_biais.png)

⚠ Le piège est évident et il est évité : choisir la longueur qui minimise l'erreur **sur les
spires qu'on mesure ensuite**, c'est ajuster sur la réponse. Elle est donc ajustée sur **six**
paires et jugée sur les **six réservées**, qu'elle n'a jamais vues — et la coupure se fait **sur
le rang**, parce que deux spires voisines partagent leur géométrie et qu'un tirage au hasard
mettrait la même région des deux côtés.

| | valeur |
|---|---:|
| longueur **nominale** (écart médian publié) | 135,5 µm |
| longueur **ajustée** sur six paires | **108,4 µm** |
| biais entre les deux | **27,1 µm** |
| erreur sur la moitié réservée, nominale | 67,6 µm |
| … **ajustée** | **54,1 µm** |
| part de l'erreur expliquée par le biais | **20 %** |

⭐ **Le biais est réel** : la longueur ajustée gagne sur des spires qu'elle n'a jamais vues, ce qui
est le seul sens acceptable de « elle gagne ». ⚠⚠ **Mais elle n'explique qu'un cinquième.** Le
plancher de la courbe réservée est à **50,5 µm** : aucune longueur constante ne descend en
dessous.

> ⛔ **Les quatre cinquièmes qui restent sont une dispersion locale**, et c'est la réponse à la
> question posée : **un meilleur nombre ne remplacera pas un raccrochage à la matière.** La
> tranche qui suit est donc justifiée, et elle a maintenant son étalon — passer sous **50 µm**
> par pas.

⚠ Le minimum du balayage est **intérieur** (54 à 217 µm, optimum à 108,4), donc il désigne bien
une longueur. Et ⚠ la première fixture de la batterie a échoué pour la bonne raison : elle
balayait 20 à 40 µm pour une cible à 30 **voxels**, soit 60 µm — c'est le drapeau `au_bord` qui
l'a dit.

#### ⛔ Et le raccrochage ne peut PAS se bâtir sur ce qui est publié : il manque 5,9 µm

> Mesure : `src/nappe/la_portee_des_piles_publiees.py` (8 contrôles) →
> `docs/mesures/la_portee_des_piles_publiees.json`. Figure :
> `src/figures/figure_la_portee_des_piles.py` (8 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/la_portee_des_piles_publiees.py --json docs/mesures/la_portee_des_piles_publiees.json
> uv run python src/figures/figure_la_portee_des_piles.py --sortie docs/images/75_la_portee_des_piles.png
> ```

⚠⚠⚠ **Cette question évite de construire la mauvaise chose.** Un raccrochage lit l'intensité
**autour de la position prédite**, qui est à une épaisseur de feuille du départ. Chaque spire
publie un `surface-volumes` en **(couche, u, v)** — donc l'indice de couche **est** une distance
signée le long de la normale. Reste à savoir si la pile va assez loin.

![la pile publiée s'arrête à six micromètres de la feuille voisine](images/75_la_portee_des_piles.png)

⭐ **Les métadonnées ne disent pas où est la surface** — `num_slices`, `slice_step`, translation
nulle, rien d'autre. Ça se mesure, et c'est mesuré : sur **1 459 592 colonnes** cumulées de trois
spires, le pic d'intensité tombe à **−1,5 couche** du centre (tolérance : une demi-feuille, soit
30,6 couches). **La convention du milieu tient**, donc l'axe des distances est bon.

⚠⚠ Et c'était un piège : sur trois blocs voisins pris isolément, le pic tombait à **66, 78 et
85**. Un bloc de 128 × 128 colonnes ne voit qu'un morceau de feuille — le profil n'a de sens que
cumulé, et le compte de colonnes est rendu pour qu'un profil bâti sur trois d'entre elles ne passe
pas pour une mesure.

| | valeur |
|---|---:|
| couches de la pile | 118 à 2,215 µm |
| portée autour de la surface | **129,6 µm** |
| … en épaisseurs de feuille | **0,956** |
| écart inter-feuilles | 135,5 µm |
| **ce qui manque** | **5,9 µm** |

> ⛔ **La pile publiée s'arrête à quatre pour cent de la feuille voisine.** Le raccrochage à la
> matière ne peut donc **pas** se bâtir sur ce qui est publié : il faut le **volume brut**. Le
> savoir maintenant coûte une mesure ; l'apprendre après avoir écrit le raccrochage aurait coûté
> le raccrochage.

⚠ La surface retenue reste le **centre** et non le pic : le pic la *confirme*, mais la prendre
ferait dépendre la géométrie d'un contraste local, et une pile un peu plus dense d'un côté
déplacerait la surface.

#### ✅✅ Sur le VOLUME BRUT, le raccrochage passe sous l'étalon : 33,3 µm

> Mesure : `src/nappe/le_raccrochage_a_la_matiere.py` (42 contrôles) →
> `docs/mesures/le_raccrochage_a_la_matiere.json`. Figure :
> `src/figures/figure_le_raccrochage_a_la_matiere.py` (17 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/le_raccrochage_a_la_matiere.py --json docs/mesures/le_raccrochage_a_la_matiere.json
> uv run python src/figures/figure_le_raccrochage_a_la_matiere.py --sortie docs/images/75_le_raccrochage_a_la_matiere.png
> ```

Le volume de scan de `PHerc0500P2` est publié : `20250526151718-2.215um-0.4m-111keV-masked.zarr`,
**28096 × 18209 × 18209 voxels, blocs de 128³ NON compressés**. ⚠⚠ Le nom porte l'horodatage du
volume *et* sa taille de voxel, et les deux sont **confrontés à ce que les spires déclarent**
avant qu'un octet ne soit lu — lire les bonnes coordonnées dans le mauvais volume est la panne
qui a coûté treize rendus noirs (`54`).

![ce n'est pas la matière la plus proche qui raccroche, c'est la forme d'une feuille](images/75_le_raccrochage_a_la_matiere.png)

⭐⭐ **La convention se mesure avant qu'aucun raccrochage n'ait lieu.** Une spire publiée est-elle
posée sur une **crête** de matière ou dans un **creux** entre deux feuilles ? Rien ne le dit, et se
tromper enverrait le raccrochage chercher l'air. Sur **2401 lignes** cumulées de sept spires : la
crête est à **−6,6 µm** de la surface publiée, le creux d'air à **+33,2 µm**, contraste **40,7**.

⚠⚠ **Et ma première version a trouvé un pas de crêtes de 8,9 µm** — quatre voxels, c'est-à-dire
l'ondulation de l'échantillonnage. Chercher un pic sur un profil **non lissé** trouve du bruit, et
le rend avec toute la précision d'une mesure. ⚠ Un créneau seul ne suffit pas non plus : une ride
d'un échantillon est **exactement la fréquence de Nyquist**, et seul un noyau de longueur paire
— ici le `[1, 2, 1]` ajouté au créneau — l'annule à zéro. C'est la batterie qui l'a dit, pas
l'usage réel.

| ce qu'on essaie | ce qu'il reste, en médiane |
|---|---:|
| ne pas bouger | 93,9 µm |
| fenêtre d'une **feuille entière** (témoin) | 76,6 µm |
| **gabarit mélangé** (témoin) | 56,6 µm |
| le pas normal seul | 46,7 µm |
| le **maximum brut** d'intensité | 46,1 µm |
| **le gabarit** | **33,3 µm** |
| … accordé aux voisins de grille | 32,6 µm |

⛔⛔ **Le maximum brut ne fait RIEN** — 46,1 contre 46,7 pour le pas seul. La crête est large de
trente voxels ; un maximum d'intensité se pose n'importe où sur ce plateau. Ce qui raccroche n'est
pas la matière la plus proche, c'est **la forme d'une feuille entière** : la corrélation normalisée
de la ligne avec le profil lu **sur la spire de départ**.

⚠⚠⚠ **Le gabarit ne sait rien de la cible**, et c'est ce qui rend la mesure honnête : on se tient
sur la spire `k`, donc son profil est une donnée qu'on a ; celui de la spire `k+1` serait la
réponse. ⚠ Ce qui reste circulaire est dit : les spires publiées ont elles-mêmes été segmentées
dans ce volume, donc l'accord n'est pas une découverte indépendante — ce qui est neuf est **la
part de l'erreur résiduelle qu'un raccrochage local enlève**, le pas géométrique ne lisant, lui,
aucun voxel.

**Trois témoins, chacun ne cassant qu'une seule chose :**

| témoin | ce qu'il casse | ce qu'il rend |
|---|---|---:|
| gabarit **mélangé** | le lien entre le décalage et la matière, rien d'autre | 56,6 µm |
| fenêtre d'une **feuille entière** | la fenêtre dérivée, la voisine devient atteignable | 76,6 µm |
| raccrocher **sans avoir bougé** | rien — le gabarit doit retrouver SA propre feuille | déplace de **10,8 µm** |

> ✅✅ **33,3 µm par pas, contre un étalon de 50,5.** L'étalon n'est pas choisi : c'est l'erreur que
> laisse la **meilleure longueur de pas constante** sur des paires réservées (section précédente).
> Le raccrochage fait donc ce qu'aucun nombre transporté ne peut faire — parce qu'il redemande à
> la matière, à chaque pas, où la feuille se trouve.

⚠⚠ **Deux paires sur sept empirent, et elles sont dessinées comme les autres.** Elles n'ont pas la
même cause, et les deux se nomment : pour 9→10 le pas seul laisse déjà **70,1 µm**, au-delà de la
demi-fenêtre de 67,8 — la bonne feuille n'est **pas à portée**, et aucun gabarit ne rattrape ça ;
pour 6→7 le gabarit ne retrouve pas sa propre feuille de départ (30,5 µm de déplacement sur place).
⚠ Ce déplacement sur place est calculable **sans la réponse**, donc ce serait le bon signal de
confiance — sauf qu'il **ne sépare pas** les deux échecs ici (12→13 déplace de 37,9 µm et gagne
quand même). Dit plutôt que vendu.

⚠ **L'accord des voisins n'ajoute rien**, et c'est son témoin qui le dit : une feuille est lisse,
donc la médiane des décalages du voisinage 3×3 devrait corriger l'isolé — elle reprend **0,7 µm**,
et son propre témoin (la médiane de **neuf décalages sans rapport**) en reprend déjà 8,6 sur la
même queue. Ce qui travaillait était la médiane, pas le voisinage. ⚠ La mesure a d'ailleurs exigé
un **sous-rectangle** de grille et non un tirage aléatoire : un tirage garde la même erreur médiane
et détruit le voisinage, donc rend l'accord inmesurable.

⚠ **Une paire n'est retenue que si la spire d'arrivée passe dans la boîte**, et le critère est
**géométrique**. Sans lui, 10→11 entrait avec mille micromètres d'erreur — non parce que le
raccrochage échoue, mais parce que la spire 11 publiée ne couvre pas cette région. Écarter sur
l'erreur aurait été choisir sur le résultat.

⚠ Le coût est rendu parce qu'un bloc fait **2 Mio non compressés** : **197 Mio** en cache pour
toute la boîte, 3 blocs neufs à la dernière exécution. Le cache est sur disque, sinon le chiffre
publié dépendrait de la patience de qui le rejoue.

> ⭐⭐⭐ **La tranche suivante est le déroulement ITÉRÉ raccroché.** Le dérouleur aveugle perd la
> feuille au tour 2 avec 53 µm de dérive par tour ; le raccrochage vaut 33,3 µm sur **un** pas.
> Ce qu'il reste à mesurer est la seule chose qui décide : **est-ce que l'erreur cesse de
> s'accumuler**, ou est-ce qu'elle s'accumule seulement plus lentement.

#### ⛔⛔ Et à l'ITÉRATION rien ne déroule — le gain du raccrochage ne survit pas à UN tour

> Mesure : `src/nappe/derouler_en_raccrochant.py` (47 contrôles) →
> `docs/mesures/derouler_en_raccrochant.json` (boîte de 640 voxels) et
> `docs/mesures/derouler_en_raccrochant_balayage.json` (trois tailles). Figure :
> `src/figures/figure_derouler_en_raccrochant.py` (17 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/derouler_en_raccrochant.py --cote 640 --json docs/mesures/derouler_en_raccrochant.json
> uv run python src/nappe/derouler_en_raccrochant.py --balayer 384,512,640 --json docs/mesures/derouler_en_raccrochant_balayage.json
> uv run python src/figures/figure_derouler_en_raccrochant.py --sortie docs/images/75_derouler_en_raccrochant.png
> ```

⚠⚠⚠ **Les deux nombres précédents ne se composaient pas, et c'est la mesure qui a tranché.** Un
dérouleur aveugle perd la feuille au tour 2 ; un raccrochage reprend un tiers de l'erreur sur
**un** pas. Enchaînés, ils ne s'additionnent pas — et la raison est maintenant chiffrée.

![le raccrochage gagne un pas et perd la marche](images/75_derouler_en_raccrochant.png)

##### ⛔⛔⛔ RÉTRACTATION : « un décalage UNIQUE par tour déroule » est retiré

La première version de cette section, publiée le matin même, mesurait sur **191 cellules et
quatre tours** et concluait que le décalage unique par tour rendait une dérive **négative** et
qu'il était **le seul des six à tenir encore la feuille**. Refait sur des morceaux de nappe plus
larges, au **même endroit**, avec le **même code** :

| côté de la boîte | cellules | tours | par point | accordé | étroite | **décalage unique** | aveugle | hasard |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 384 vx | 191 | 4 | +27,8 | +28,9 | +22,0 | **−19,5** | +13,3 | +43,6 |
| 512 vx | 494 | 6 | +49,9 | +35,1 | +43,2 | **+67,3** | +25,5 | +73,6 |
| 640 vx | 906 | 6 | +56,1 | +33,6 | +43,0 | **+56,3** | +22,3 | +65,7 |

*(dérive en µm par tour, ajustée par moindres carrés sur toute la marche)*

⛔ **Un résultat qui s'inverse quand l'échantillon grandit n'était pas un résultat.** Et il
s'inverse à **deux** tailles indépendantes, pas une. Une seconde revendication tombe avec :
la « longueur de pas équivalente » du décalage global valait 114,7 µm à 191 cellules — *« à six
micromètres de la longueur ajustée sur les cibles »* — et vaut **161,3 µm** à 906. C'était une
coïncidence de boîte, pas un fait sur la nappe.

⚠⚠ **La boîte n'était pas un choix de résultat, elle était un choix de COÛT** : un bloc de ce
volume fait 2 Mio non compressés, et 384 voxels était ce qui tenait dans le cache du jour. C'est
exactement pour ça qu'il fallait la balayer avant de conclure — un paramètre choisi pour sa
facture n'a aucune raison d'être neutre sur la mesure.

##### La marche, sur le plus grand morceau mesuré (906 cellules, 6 tours)

| tour | cell. | par point | accordé | étroite | décalage unique | aveugle | hasard | rugosité | perdues |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 795 | **30 µm** | 28 | 43 | 40 | 43 | 72 | 6 µm | 0,30 |
| 2 | 692 | 53 | 40 | 55 | 64 | **51** | 73 | 17 µm | 0,38 |
| 3 | 596 | 97 | 89 | 76 | 152 | **55** | 129 | 25 µm | 0,64 |
| 6 | 349 | 309 | 192 | 256 | 306 | **161** | 368 | 25 µm | 0,87 |

⛔ **Aucun contendant ne tient la feuille au dernier tour, et le moins mauvais est celui qui ne
lit rien** : l'aveugle dérive de **+22,3 µm par tour** quand le meilleur raccrochage — l'accordé
aux voisins — en fait +33,6. ⭐ Le seul ordre stable aux trois tailles est celui-là : **le
raccrochage par point dérive plus que l'aveugle partout**, et le gabarit mélangé est pire que
tout partout.

##### ⭐⭐⭐ Et la RAISON est mesurée : le gain ne survit pas à un seul tour

L'expérience qui manquait tient en une phrase : la mesure d'**un** pas part toujours d'une spire
**publiée**, dont les normales sont propres ; une marche part de sa propre reconstruction, qui ne
l'est plus. Ici la trajectoire de référence est la marche **aveugle** — une surface qui vieillit
sans que le raccrochage y soit pour rien — et à chaque tour on en tire **deux pas depuis le même
point** : un aveugle, un raccroché. Une seule variable change.

| âge de la surface | pas aveugle | pas raccroché | **gain** |
|---:|---:|---:|---:|
| **0 tour — une spire publiée** | 42,7 µm | **30,0 µm** | **+12,7** |
| 1 tour | 50,8 | 51,0 | **−0,2** |
| 2 tours | 54,8 | 68,3 | −13,5 |
| 3 tours | 71,0 | 68,5 | +2,5 |
| 4 tours | 108,3 | 101,4 | +6,8 |
| 5 tours | 161,3 | 170,8 | −9,5 |

> ⛔⛔⛔ **Le raccrochage ne raccroche que ce qui est déjà à sa place.** Il gagne **12,7 µm**
> depuis une spire publiée et **plus rien** dès qu'un seul tour aveugle a été fait — ensuite la
> médiane vaut **−0,2 µm** et le signe change quatre fois. Les 33,3 µm de la tranche précédente
> sont donc un gain **conditionnel au point de départ**, pas une capacité de la méthode.

⚠⚠ **Le critère est structurel, pas un seuil.** Ma première version demandait « moins de la
moitié du gain initial » et elle est tombée sur **6,8 contre 6,35** — un verdict décidé au dixième
de micromètre par un nombre que j'avais choisi. Ce qui distingue un effet d'un bruit n'est pas sa
taille, c'est que le bruit **change de signe** et qu'un effet non.

⚠ La rugosité dit la même chose autrement : le champ de décalages par point ride la nappe de
**6 à 25 µm** au fil des tours, et la rugosité mesurée **depuis la surface aveugle** monte elle
aussi (6 → 22 µm). Ce n'est pas le raccrochage qui abîme la surface au point de se saborder — la
surface se dégrade toute seule, et le raccrochage cesse simplement d'y voir une feuille.

##### ⭐⭐⭐ Le MÉCANISME, trouvé en éliminant : ce sont les NORMALES

Trois soupçons ont été testés et écartés avant celui qui tient, et chacun ne cassait qu'une chose.

| soupçon | ce qui a été changé | dérive par tour |
|---|---|---:|
| les cellules sautent sur la feuille voisine | fenêtre deux fois plus **étroite** | +43,0 µm |
| le champ de décalages est bruité | décalages **accordés** au voisinage 3×3 | +33,6 µm |
| le gabarit se dégrade avec la surface | gabarit **figé**, lu une fois sur la spire de départ | **+54,2 µm** |
| — | *raccrochage par point, sans remède* | +56,1 µm |
| **la direction de recherche se dégrade** | **normales lissées** avant le pas | **+25,3 µm** |
| — | *le pas aveugle, qui ne raccroche rien* | **+22,3 µm** |
| la même chose, sans raccrochage du tout | aveugle + **normales lissées** | **+22,0 µm** |

⛔ **Le gabarit n'était pas la panne** : le figer ne change rien (+54,2 contre +56,1), et son
**contraste ne s'effondre pas** — 51, 78, 53, 40, 47, 51 au fil des tours. La surface continue de
ressembler à une feuille ; c'est la **direction** dans laquelle on la cherche qui se perd.

> ⭐⭐⭐ **Lisser les NORMALES divise par deux la dérive du raccrochage — et ne fait RIEN pour
> l'aveugle.** C'est la seconde moitié qui prouve la première : si les normales étaient
> simplement mauvaises pour tout le monde, les lisser aiderait les deux marches. Elles ne sont
> mauvaises que là où le raccrochage est passé. **Il ride la nappe, la nappe gâte ses normales,
> et la mauvaise normale gâte le pas suivant.**

⚠⚠ **Ce n'est pas le même geste que l'accord des voisins**, et la distinction est tout le sujet :
accorder lisse **de combien** on bouge, lisser les normales lisse **dans quelle direction** on
cherche. Les deux ensemble donnent **+29,4**, soit *moins bien* que les normales seules — ils ne
s'additionnent pas, ils se recouvrent et finissent par sur-lisser.

⭐⭐ **Et c'est le contendant le plus STABLE des dix au balayage** : normales lissées rend
**+26,0 · +25,8 · +25,3** aux trois tailles de boîte, quand le pas aveugle lui-même oscille de
+13,3 à +25,5. Aux deux plus grandes tailles les deux sont donc **à égalité** — le raccrochage
réparé ne coûte plus rien, il ne rapporte simplement toujours rien.

⚠ La dispersion angulaire du champ de normales est mesurée à chaque tour et **ne demande aucune
cible** : 2,8° puis 2,7 · 3,7 · 6,9 · 10,1 · 10,9. Un dérouleur peut donc la calculer sur
lui-même en marchant — c'est le seul signal de confiance de toute la tranche qui n'exige pas de
connaître la réponse.

⛔⛔ **Et malgré tout ça, aucun raccrochage ne bat l'aveugle** : le meilleur, normales lissées, est
à **+25,3** contre **+22,3**. Le mécanisme est réparé aux deux tiers et le geste ne se paie
toujours pas — ce qui est cohérent avec la mesure du vieillissement, puisqu'il n'y a de gain à
récupérer qu'au tout premier pas.

##### ⛔⛔ Et la dispersion des normales est un SYMPTÔME — quatre soupçons, quatre écartés

Une normale est une **dérivée**, et une dérivée estimée entre voisins immédiats divise le bruit de
position par la maille : ici seize voxels, donc une erreur d'un voxel fait déjà quatre degrés.
Élargir le support de la différence centrée divise ce bruit d'autant — et coûte le bord, une
cellule de plus de chaque côté **par tour**. Les deux effets sont opposés, donc le support se
**balaye**.

| support | tours | cellules (1er → fin) | dérive/tour | dispersion finale | écart latéral attendu |
|---:|---:|---:|---:|---:|---:|
| 1 | 6 | 795 → 349 | +22,3 µm | **10,9°** | **26 µm** |
| 2 | 6 | 693 → 41 | +32,7 µm | **1,5°** | 4 µm |
| 3 | 4 | 597 → 41 | +23,1 µm | 1,4° | 3 µm |
| 4 | 3 | 509 → 41 | +25,4 µm | 1,4° | 3 µm |

⭐ **Un support de deux divise la dispersion par sept** (10,9° → 1,5°), et l'écart latéral qu'elle
prédit — un pas de longueur `L` le long d'une normale fausse de θ atterrit à `L·sin θ` de côté —
passe de **26 µm à 4**. Ce 26 µm est du même ordre que la dérive mesurée, ce qui faisait de la
dispersion une cause parfaitement plausible.

⚠⚠ **La comparaison des dérives est CONFONDUE par l'érosion** : au sixième tour il reste 349
cellules à support 1 contre 41 aux autres, donc les marches ne sont plus jugées sur la même
population. La seule comparaison honnête est celle du **premier tour**, où tous partent de cinq à
huit cents cellules :

| support | cellules | erreur du pas | dispersion |
|---:|---:|---:|---:|
| 1 | 795 | **42,7 µm** | 2,78° |
| 2 | 693 | 42,2 µm | 2,29° |
| 3 | 597 | 42,3 µm | 1,93° |
| 4 | 509 | **41,7 µm** | **1,59°** |

> ⛔⛔ **La dispersion tombe de 43 %, l'erreur du pas ne bouge pas d'un micromètre.** La dispersion
> angulaire des normales est donc un **symptôme**, pas la cause de la dérive. Quatre soupçons
> testés, quatre écartés : la fenêtre, les décalages, le gabarit, les normales.

⚠ Le seuil du verdict est un vingtième de l'erreur, soit l'ordre de l'arrondi publié, et non un
nombre choisi pour que la phrase passe. Et les deux moitiés sont exigées ensemble : « la
dispersion baisse » seul dirait que ça marche, « l'erreur ne suit pas » seul dirait que ça ne sert
à rien — c'est leur conjonction qui dit *symptôme*.

⚠ Un contrôle de cette tranche **ne pouvait pas échouer** et a été réécrit : il vérifiait que
60·sin(10°) vaut 10,42, c'est-à-dire mon arithmétique contre elle-même. Ce qui se teste vraiment
est que les **deux colonnes publiées s'accordent** — un écart latéral calculé sur une autre
dispersion que celle rendue à côté serait un chiffre plausible et faux. ⚠ Et sa fixture de bruit
avait une **période de trois**, que le support trois annulait exactement : le contrôle passait à
0,00°, vrai pour une raison qui n'était pas celle qu'on teste.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante.** Le raccrochage sur la matière est **clos
> comme moteur de déroulement** — il gagne 12,7 µm depuis une spire publiée, plus rien après un
> tour, et aucune de ses variantes ne bat le pas aveugle — et **les quatre soupçons sur la
> mécanique du pas sont tous écartés** : la fenêtre, les décalages, le gabarit, les normales.
> Ce qui n'a **jamais** été essayé est la seule quantité que toutes ces marches tiennent pour
> acquise : **la LONGUEUR du pas, une par cellule.** Le corpus dit qu'elle varie d'un facteur
> cinq d'un endroit à l'autre — les écarts entre spires consécutives vont de 60,5 µm au premier
> décile à 295,1 au neuvième — et tout ce qui a été mesuré ici avance de la **même** médiane de
> 135,5 µm partout. `la_derive_est_elle_un_biais` avait ajusté une constante **globale** et n'en
> avait tiré qu'un cinquième ; une longueur **locale**, lue dans le volume, n'a pas d'équivalent
> mesuré. Et elle est lisible sans cible : la crête suivante le long de la normale **est** la
> longueur du pas.

#### ⛔⛔ Et la LONGUEUR locale ne se lit pas non plus : ce qui revient est un tirage dans la fenêtre

> Mesure : `src/nappe/la_longueur_locale_du_pas.py` (18 contrôles) →
> `docs/mesures/la_longueur_locale_du_pas.json`. Figure :
> `src/figures/figure_la_longueur_locale_du_pas.py` (10 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/la_longueur_locale_du_pas.py --cote 640 --json docs/mesures/la_longueur_locale_du_pas.json
> uv run python src/figures/figure_la_longueur_locale_du_pas.py --sortie docs/images/75_la_longueur_locale_du_pas.png
> ```

C'était la dernière quantité que toutes les marches tenaient pour acquise. La crête suivante le
long de la normale **est** la feuille voisine, et elle se lit **sans la cible** : le gabarit dit à
quoi ressemble une feuille, une fenêtre ouverte vers l'extérieur dit à quelle distance est la
prochaine. ⚠⚠ La fenêtre est **dérivée** — d'une demi-longueur nominale à une et demie : en deçà
on retrouve la feuille de départ, au-delà on saute la voisine.

![la longueur locale ne se lit pas](images/75_la_longueur_locale_du_pas.png)

⚠⚠⚠ **Le nombre qui trompe est la médiane** : **136,9 µm lus contre 135,5 publiés**, un accord à
un centième. Il ne prouve **rien** — la médiane d'un tirage uniforme dans `[0,5 L ; 1,5 L]`
vaut exactement `L`. Et le témoin du gabarit mélangé rend **131,1**.

| | p10 | médiane | p90 |
|---|---:|---:|---:|
| lues dans le volume | 82,7 µm | **136,9** | 193,0 |
| publiées (spires) | 67,2 | **135,5** | **311,3** |
| témoin mélangé | 78,2 | 131,1 | 190,6 |

⛔ **La queue haute est TRONQUÉE, et par construction** : la fenêtre se ferme à **203,2 µm** quand
le neuvième décile publié est à **311,3**. Exclure la deuxième voisine et atteindre le neuvième
décile sont **deux exigences incompatibles** sur ce corpus — ce n'est pas un réglage à corriger,
c'est un fait sur la nappe : ses écarts varient trop pour qu'une fenêtre bien posée les couvre.

> ⛔⛔ **Et le verdict est cellule par cellule.** La lecture et son témoin s'écartent de **0,292**
> de la largeur de la fenêtre, quand deux tirages **indépendants** s'en écarteraient de
> **0,293** — la médiane de `|X − Y|` pour deux uniformes sur `W` vaut `W(1 − 1/√2)`, un étalon
> qui se **calcule** et ne se choisit pas. La mesure en atteint **99,7 %**. Ce qui revient n'est pas
> une longueur, c'est un tirage dans la fenêtre où on la cherche.

⭐⭐ **Et une seconde preuve, qui ne demande AUCUNE cible** : les grilles publiées partagent une
orientation — mesuré ailleurs, le sens retenu est le même pour les douze paires. Une lecture qui
porterait du signal choisirait donc le même sens partout. Elle en change : **trois spires sur neuf**
au sens minoritaire.

⚠⚠⚠ **Et le sens était CODÉ EN DUR derrière un commentaire qui prétendait le dériver.** Le code le
choisissait par le nombre de lignes lisibles — presque toujours égal des deux côtés — donc son
`max` retombait sur le premier sens essayé, et les neuf spires rendaient « + ». Corrigé par la
**force de la corrélation**, ce qui a changé les sens retenus *et* renforcé le verdict : l'écart au
témoin passe de 0,277 à **0,292** pour un étalon de 0,293.

⚠⚠ **Ma première version comparait à 0,15**, un nombre que j'avais posé — et il rendait le verdict
inverse. Le remplacer par une quantité dérivée a retourné la conclusion, ce qui est exactement ce
qu'un seuil choisi permet de ne jamais voir.

⚠⚠ **Et la comparaison des DÉCILES ne tranche rien** : la lecture et son témoin rendent les mêmes
trois quantiles à quelques micromètres près. Un verdict bâti dessus aurait été vrai
arithmétiquement et faux au sens qui compte ; le champ qui l'annonçait a été retiré du JSON, parce
que deux verdicts contradictoires dans un même fichier sont un piège.

⚠ Deux fixtures de ma batterie ne pouvaient pas discriminer, et pour deux raisons différentes.
La première avait des feuilles **régulièrement espacées** : la ligne entière est alors périodique,
donc n'importe quel motif y trouve la période et le gabarit mélangé rendait 59,9 pour une vraie
réponse de 60. La seconde était constante en `x` et en `y` : les vingt-quatre lignes étaient **la
même ligne**, donc le témoin avait un échantillon de **un**.

⚠⚠⚠ **Et le témoin du gabarit mélangé a une limite, mesurée plutôt qu'invoquée** : contre une
crête **isolée et très piquée**, il la retrouve quand même — une permutation garde la distribution
des valeurs du gabarit, et presque n'importe quel vecteur de cette distribution corrèle au maximum
sur la crête. Il discrimine sur la donnée réelle, bruitée et peu piquée ; il ne discrimine pas sur
une fixture propre. Le témoin qui tranche là est un volume **sans feuille dans la fenêtre** : les
longueurs lues s'y étalent sur **30,4** contre **0,7** avec une feuille.

> ⛔⛔⛔ **Cinq soupçons, cinq écartés.** La fenêtre, les décalages, le gabarit, les normales, et
> maintenant la longueur du pas. Le volume brut donne **un** gain, à un pas, depuis une surface
> déjà juste — et rien d'autre. ⭐ Ce qui reste n'est plus une variante de la même marche : c'est
> que **la marche elle-même part d'une seule spire et n'a que sa propre reconstruction pour se
> juger**. Les treize spires publiées offrent douze départs indépendants ; personne n'a encore
> mesuré si un dérouleur qui part de **plusieurs** endroits à la fois — et dont les branches
> doivent s'accorder là où elles se rencontrent — fait mieux qu'un seul qui part d'un bout.

#### ⭐⭐⭐ DEUX ANCRES VALENT BIEN MIEUX QU'UNE — espacées régulièrement, et PONDÉRÉES

> Mesure : `src/nappe/derouler_des_deux_bords.py` (32 contrôles) →
> `docs/mesures/derouler_des_deux_bords.json`. Figure :
> `src/figures/figure_derouler_des_deux_bords.py` (19 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/derouler_des_deux_bords.py --cote 640 --json docs/mesures/derouler_des_deux_bords.json
> uv run python src/figures/figure_derouler_des_deux_bords.py --sortie docs/images/75_derouler_des_deux_bords.png
> ```

Cinq soupçons écartés portaient tous sur **la même marche** : une qui part d'une seule spire et
n'a que sa propre reconstruction pour se juger. Celle-ci change la **structure** : la spire `m` est
reconstruite depuis une ancre `a < m` **et** une ancre `b > m`.

⭐⭐ **Et là, pour la première fois, deux reconstructions se rencontrent.** Des spires concentriques
ne se croisent jamais, donc « plusieurs départs » ne veut rien dire tant qu'on marche tous dans le
même sens ; **encadrer**, si. **56 encadrements** mesurés, portée 4, dont 14 symétriques.

![deux ancres valent bien mieux qu'une](images/75_derouler_des_deux_bords.png)

| | erreur médiane |
|---|---:|
| branche montante seule | 58,3 µm |
| branche descendante seule | 90,7 µm |
| « la meilleure des deux » *(demande de savoir laquelle)* | 50,3 µm |
| **encadrée** | **43,1 µm** |

> ⭐⭐⭐ **L'encadrement bat les DEUX branches sur 41 encadrements sur 56**, et sa médiane est
> **sous la demi-épaisseur** (67,75 µm) : la feuille est tenue. ⚠⚠ Battre la plus mauvaise serait
> gratuit — « prendre la meilleure » y suffirait, et savoir laquelle demande la réponse. Il bat
> aussi celle-là.

##### ⭐⭐ Où poser la seconde ancre : régulièrement

| bras | cas | encadrée | meilleure branche | |
|---|---:|---:|---:|---|
| 1+1 | 5 | **30,1 µm** | 36,1 | symétrique |
| 1+2 | 10 | 32,7 | 40,0 | |
| 1+3 | 9 | 41,3 | 42,7 | |
| **1+4** | 7 | **59,9** | 42,7 | ⛔ **nuit** |
| 2+2 | 4 | **33,2** | 54,5 | symétrique |
| 2+3 | 7 | 39,4 | 66,8 | |
| **2+4** | 5 | **64,6** | 58,3 | ⛔ **nuit** |
| 3+3 | 3 | 48,6 | 86,2 | symétrique |
| 3+4 | 4 | 50,4 | **113,8** | |
| 4+4 | 2 | 62,6 | 102,3 | symétrique |

> ⭐⭐ **À somme de bras égale — donc à même écartement d'ancres — la symétrie gagne** : `2+2`
> rend **33,2 µm** contre **41,3** pour `1+3`, et `3+3` rend **48,6** contre **64,6** pour `2+4`.
> C'est une réponse pratique à « où poser la seconde ancre » : **espacer régulièrement**, pas
> grouper.

⛔ **Et il y a une limite : un encadrement trop déséquilibré NUIT.** Sur `1+4` et `2+4`,
l'encadrement rend **pire** que sa meilleure branche — la branche lointaine a tellement dérivé que
la moyenne tire la bonne avec elle. ⚠⚠ **Le chiffre qui serait trompeur n'est pas publié** : le
déséquilibre minimal des paires fautives vaut deux, mais `1+3` a exactement ce déséquilibre et ne
nuit pas. Ce que les deux fautives partagent est leur **bras long**, et il vaut la portée mesurée —
donc ce corpus ne dit **pas** si c'est la longueur absolue ou le déséquilibre qui casse. Les deux
faits sont rendus, la conclusion non.

##### ⭐⭐⭐ Et PONDÉRER les deux branches par leurs bras répare exactement ce qui était cassé

Le désaccord entre branches est **symétrique** — c'est le même nombre pour les deux — donc il ne
peut pas dire laquelle croire. Ce qui les distingue **sans regarder la réponse** est la longueur de
leur bras, et la mesure a établi que l'erreur croît avec elle. Si elle croît **linéairement**,
l'estimateur qui annule deux erreurs de signes opposés est l'**interpolation linéaire entre les
deux ancres** : la branche au bras court pèse `bras_long / (somme)`. ⭐ **Aucun paramètre libre.**

| | erreur médiane |
|---|---:|
| encadrée à parts égales | 43,1 µm |
| **pondérée par les bras** | **35,9 µm** |
| témoin : poids **inversé** | 53,2 µm |

> ⭐⭐⭐ **Et elle répare EXACTEMENT les deux paires que la mesure avait dites cassées** — `1+4` et
> `2+4` — **sans toucher aux symétriques**, parce qu'à bras égaux le poids vaut un demi et rend le
> milieu. Un remède qui ne peut pas abîmer les cas qui marchaient n'a pas besoin qu'on le vérifie
> sur eux ; celui-ci ne le peut pas **par construction**.

⚠⚠ Les quatre verdicts sont exigés **ensemble** : elle bat le milieu, elle bat son témoin de poids
inversé, elle laisse les symétriques intacts, et elle répare **toutes** les paires cassées. Sans le
dernier, « ça améliore la médiane » pourrait vouloir dire qu'elle a déplacé des cas déjà sains.

⚠ L'hypothèse dont le poids est tiré — l'erreur croît linéairement avec le bras — est **vérifiée
dans la batterie** plutôt que supposée : sur deux branches dont les dérives valent `d` et `4d` de
part et d'autre, l'interpolation les annule exactement, la moyenne à parts égales non, et le poids
inversé fait bien pire.

##### ⭐⭐ Le mécanisme est mesuré : c'est un BIAIS qui s'annule, pas du bruit qu'on moyenne

Une distance est toujours positive, donc deux branches qui se trompent en sens contraires ont
exactement le même profil d'erreur qu'une qui se trompe deux fois dans le même sens. Le **signe**
les sépare, et il est mesuré en projetant l'écart de chaque branche sur la direction de marche de
la montante : **+45,3 µm** contre **−82,8 µm**, de **signes opposés sur 48 encadrements sur 56**.

> ⭐ Moyenner du bruit gagne √2 au mieux ; annuler un biais gagne **tout le biais**. Les deux
> mécanismes rendent la même médiane et ne promettent pas du tout la même chose ailleurs.

⚠ Le contrôle qui rend ça vérifiable est dans la batterie : **deux branches du MÊME côté** de la
cible ont un milieu qui reste du même côté, donc pas meilleur que la plus proche.

##### ⭐⭐⭐ Et le désaccord entre branches PRÉDIT l'erreur — le premier signal sans cible qui sert

Le désaccord entre les deux branches (162,5 µm médian) est la **seule** mesure de tout le chantier
qui ne demande pas la réponse : un dérouleur pourrait la calculer **en marchant**. Elle prédit
l'erreur de l'encadrement — **ρ = 0,409, p = 0,0018 sur 56**.

⚠⚠⚠ **Et ce verdict s'est INVERSÉ avec l'échantillon, dans le bon sens.** Sur les douze
encadrements **symétriques** seuls, il ne prédisait rien (ρ = 0,28, p = 0,38) et la première
version de cette section l'écrivait comme un échec. Élargir aux 56 encadrements — symétriques et
non — le rend significatif. C'est la même leçon que la boîte, dans l'autre sens : **un verdict sur
un petit échantillon n'est pas un verdict**, qu'il soit positif ou négatif.

⚠⚠ **CE QUE CETTE MESURE EST, ET CE QU'ELLE N'EST PAS.** Un vrai dérouleur n'a qu'une ancre :
encadrer suppose de connaître les deux bouts et coûte **deux** bits de supervision au lieu d'un.
Ce n'est donc pas une méthode, c'est une **borne**. Mais elle répond à la question qui décide de
l'effort : cinq soupçons sur la mécanique du pas n'ont rien rendu, et une **seconde ancre** divise
l'erreur par **1,35**, avec un gain qui se creuse jusqu'à **×2,3** au bras 3+4.

⚠ Aucune lecture du volume dans cette tranche : le pas aveugle est le meilleur dérouleur mesuré et
il ne lit rien. ⚠ Chaque branche marche le nombre de tours de **son** bras — avec des encadrements
asymétriques les deux n'en font plus autant, et un compte commun ferait marcher l'une trop loin.
⚠ L'appariement des deux nuages se fait dans l'**espace**, par plus proche voisin : les deux
branches viennent de deux spires publiées, donc de deux paramétrages, et les moyenner cellule à
cellule apparierait des points sans rapport.

⚠ Deux défauts de ma prose de figure, tous deux attrapés par ses propres contrôles : elle
**calculait** un rapport absent du JSON — une figure ne doit pas inventer de nombre, donc le
rapport est publié dans la mesure — et elle portait une **étoile** que la police ne rend pas, qui
serait sortie en carré vide.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante.** Le corpus publie **treize** spires, donc
> douze ancres, et la mesure dit qu'elles valent bien plus qu'un meilleur pas — mais aussi qu'un
> bras de quatre est déjà trop long. La question suivante est donc **ce qui se passe entre
> ancres** : le désaccord prédit l'erreur, faiblement (ρ = 0,41) ; s'en servir pour **pondérer**
> les deux branches au lieu de les moyenner à parts égales est le geste que cette mesure rend
> possible, et il ne demande toujours aucune cible.

#### ⛔⭐⭐⭐ LA TROISIÈME ANCRE NE PAIE PAS — et la piste des ancres est refermée

> Mesure : `src/nappe/combien_dancres.py` (38 contrôles) → `docs/mesures/combien_dancres.json`.
> Figure : `src/figures/figure_combien_dancres.py` (18 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/combien_dancres.py --cote 640 --portee 4 --kmax 4 \
>     --json docs/mesures/combien_dancres.json
> uv run python src/figures/figure_combien_dancres.py --sortie docs/images/75_combien_dancres.png
> ```

La tranche précédente avait ouvert **une** piste et une seule : *« ce n'est pas une méthode,
c'est une borne — elle dit si l'effort doit aller vers une meilleure propagation ou vers PLUS
D'ANCRES »*. Cette tranche la referme. **431 jeux d'ancres sur 9 cibles**, même boîte (640) et
même portée (4) que l'étude qu'elle prolonge, donc les chiffres se comparent.

![la deuxième ancre fait tout](images/75_combien_dancres.png)

##### L'estimateur, et pourquoi il n'a aucun paramètre libre

Si l'erreur d'une ancre croît linéairement avec son bras, la prédiction de l'ancre $i$ vaut
$p_i \simeq p + \beta s_i$ où $s_i$ est son bras **signé**. Ce qui annule $\beta$ est la droite
des moindres carrés en $s$, évaluée en $s = 0$.

> ⭐⭐ **À deux ancres de signes opposés, elle rend EXACTEMENT la pondération par les bras déjà
> mesurée.** Pour $s = (-a, +b)$ on obtient $w = (b, a)/(a+b)$ : ce n'est pas une ressemblance de
> forme, c'est une **identité algébrique**, et la batterie la vérifie sur six paires de bras.
> La généralisation ne remplace pas le résultat précédent, elle le **contient**.

⚠⚠ **Les poids ne dépendent que des bras, jamais des données** — l'ordonnée à l'origine d'une
régression s'écrit $\sum_i w_i p_i$ avec des $w_i$ qui ne contiennent que les $s_i$. Aucun bit de
la cible n'entre donc dans la combinaison : un dérouleur pourrait l'appliquer sans jamais regarder
où il doit arriver.

##### ⛔ Le verdict : le gain s'arrête à DEUX ancres qui encadrent

| ancres | jeux | ajusté | *dont ceux qui encadrent* |
|---|---:|---:|---:|
| 1 | 48 | 70,3 µm | — |
| 2 | 112 | 42,5 µm | **36,7 µm** *(56 jeux)* |
| 3 | 149 | 37,2 µm | **35,5 µm** *(119)* |
| 4 | 122 | 35,3 µm | **35,3 µm** *(116)* |

⚠ Le contendant sans information de bras — la **moyenne plate** des mêmes nuages — rend 53,3 /
45,7 / 38,4 µm : l'ajustement le bat en médiane à tous les nombres d'ancres, mais **jeu par jeu**
seulement 191 fois sur 291 chez les encadrants. Il gagne **gros** quand il gagne et perd **petit**
quand il perd, et un seul compte agrégé laisserait croire à un ex æquo.

> ⛔⭐⭐ **La deuxième ancre enlève 27,8 µm. La troisième, à jeux comparables, en enlève 1,2 ; la
> quatrième, 0,2.** Le problème n'est **pas** le nombre d'ancres — cette piste est refermée.

⚠⚠ **UN CHIFFRE PUBLIÉ SUR UNE POPULATION CONFONDUE, CORRIGÉ.** J'avais d'abord calculé la
saturation sur la courbe **agrégée**, qui descend encore — et elle ment : la part de jeux qui
encadrent passe de **0 à 50, 80 puis 95 %** avec le nombre d'ancres, donc son affaissement mesure
d'abord ce **changement de composition**. Les deux courbes sont publiées, la seconde est celle qui
tranche.

##### ⛔ Le panneau B a porté une affirmation RETIRÉE le jour même

| bras | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| **une** ancre | 41,1 µm | 63,1 | 100,8 | **149,4** |
| incréments *depuis le bras zéro* | **+41,1** | +22,0 | +37,7 | +48,6 |
| coût **par tour** | 41,1 | 31,6 | 33,6 | 37,4 |
| **deux** ancres à ±ce bras | 30,0 µm | 34,0 | 44,6 | **63,8** |
| coût **par tour** | 30,0 | 17,0 | 14,9 | 16,0 |

> ⛔⚠⚠ **J'avais publié « la dérive ACCÉLÈRE », et c'était faux.** Le critère employé — *« les
> incréments consécutifs croissent »* — **omettait le plus grand incrément de tous** : celui du
> bras zéro, dont l'erreur est nulle **par définition**, au bras un. La suite complète est
> **41,1 puis 22,0 / 37,7 / 48,6** : le premier pas est le plus cher, et il n'y a pas de tendance
> après lui. Retiré par `pourquoi_la_derive_accelere` le même jour, section suivante.

⭐⭐ **Ce qui est vrai et reproduit sur deux populations** : l'erreur au bras `k` reste **SOUS**
`k` fois celle du bras un, et le **coût par tour est stable** — 31,6 / 33,6 / 37,4 µm ici, 31,4 /
34,5 / 33,5 sur l'autre population. La dérive est donc à peu près **linéaire** avec un premier pas
plus cher. C'est exactement la prémisse dont l'estimateur a besoin — et c'est **pourquoi la
parabole ne trouve rien à annuler**, ce qui rend l'ensemble cohérent au lieu de contradictoire.

⚠ **Et l'explication que j'avais donnée à `1+4` et `2+4` qui nuisent tombe avec elle.** Ce n'est
pas la courbure. L'encadrement divise le coût par tour par deux (17 contre 33 µm), donc la pente
est bien annulée ; ce qu'un bras de quatre injecte est la **variance** de sa branche — 149 µm
d'erreur, même à 20 % de poids, font ±30 µm de bruit. La question *« longueur ou déséquilibre »*
reste donc **ouverte**, et la retirer d'ici est plus honnête que la laisser répondue à tort.

##### Ce que ça donne comme consigne

> ⭐⭐ **Deux ancres à ±2 tours tiennent la feuille à 34,0 µm** (4 cas), la moitié de la
> demi-épaisseur. À ±4, encore **63,8 µm** — sous les 67,75 —, mais sur **2 cas** seulement, et ce
> dépôt a déjà vu un verdict s'inverser quand l'échantillon a grandi.

⚠ Une différence de méthode avec la tranche précédente, qui explique l'écart entre **36,7** et
**35,9 µm** sur ce qui est presque la même chose : là-bas la combinaison était faite **dans les
deux sens** et les distances mises en commun ; ici le nuage de référence est celui de l'ancre la
plus basse. Deux populations de points, deux médianes voisines — et le dire vaut mieux que
laisser croire à une contradiction.

##### ⛔ Et la parabole ne paie pas non plus — mesurée avant d'être écrite comme une piste

La courbure étant réelle, l'estimateur qui l'annulerait n'est plus une droite mais une
**parabole** — ce qui demande **trois** ancres pour être identifiée, et redonnerait donc un rôle à
la troisième : non plus moyenner, mais **mesurer la courbure**. J'allais l'écrire comme la seule
lecture qui ouvre quelque chose. Elle est mesurée à la place.

> ⛔ **Sur les 235 jeux d'au moins trois ancres qui encadrent — les MÊMES jeux, pas deux
> populations — le degré deux rend 37,5 µm contre 35,3 pour la droite, et il ne gagne que sur 87.**
> Sur des bras entiers de 1 à 4, identifier une courbure coûte plus de **variance** qu'elle
> n'enlève de **biais**.

⚠ Ce que ce négatif dit exactement, et pas plus : la courbure est réelle et mesurée, mais elle
n'est pas **estimable** depuis trois ou quatre bras entiers. Un corpus qui offrirait des bras plus
fins, ou plus nombreux, poserait la question autrement — et ce n'est pas ce corpus.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante, et c'est un inventaire de portes fermées.**
> Le bilan des cinq soupçons avait laissé **deux** pistes : une meilleure propagation du pas, ou
> plus d'ancres. La première était déjà close (cinq soupçons éliminés). Cette tranche ferme la
> seconde — la troisième ancre ne paie pas — **et** la troisième piste que la mesure elle-même
> avait suggérée, l'estimateur d'un degré de plus. Ce qui reste debout est le fait, pas le
> remède : **la dérive accélère avec le bras**, et deux ancres qui encadrent en annulent la pente.
> Toute suite qui prétend faire mieux devra s'attaquer à ce qui produit cette accélération, pas à
> la façon de la combiner après coup.

#### ⭐⭐ L'ITÉRATION NE PAIE QUE DE LA NAPPE — un seul grand pas fait aussi bien

> Mesure : `src/nappe/pourquoi_la_derive_accelere.py` (24 contrôles) →
> `docs/mesures/pourquoi_la_derive_accelere.json`. Figure :
> `src/figures/figure_pourquoi_la_derive_accelere.py` (15 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/pourquoi_la_derive_accelere.py --cote 640 --bras-max 4 \
>     --json docs/mesures/pourquoi_la_derive_accelere.json
> uv run python src/figures/figure_pourquoi_la_derive_accelere.py \
>     --sortie docs/images/75_pourquoi_la_derive_accelere.png
> ```

Cette tranche devait écarter deux artefacts qui auraient pu **fabriquer** l'accélération publiée
juste avant. Elle en a trouvé un troisième, et il était dans le critère lui-même.

![elle n'accélère pas](images/75_pourquoi_la_derive_accelere.png)

##### Les deux artefacts, écartés

| suspect | mesure | verdict |
|---|---|---|
| le **masque** qui rétrécit (996 → 671 cellules) | erreur sur le sous-ensemble commun à tous les bras | ⛔ **il n'y est pour rien** — 1,5 / 2,1 / 2,7 / 0,0 µm d'écart |
| la **spire de départ**, différente à chaque bras | la forme de la courbe à départ **fixe** | ✅ elle tient — 4 départs sur 6 à trois bras ou plus |

##### ⛔ Le troisième était le critère

> ⛔⚠⚠ **« Les incréments consécutifs croissent » omet le plus grand incrément de tous** : celui
> du bras **zéro**, dont l'erreur est nulle par définition, au bras un. Et il bascule sur deux
> micromètres — il rend **OUI** sur une population et **NON** sur l'autre, alors que les deux
> mesurent la même chose.

Le critère retenu est **sans seuil** et il a un sens : *l'erreur au bras `k` est-elle au-dessus ou
en dessous de `k` fois celle du bras un ?* Elle est **en dessous partout**, et le coût par tour
est **stable** : 44,2 puis 31,4 / 34,5 / 33,5 µm. Il vit dans un seul endroit, `sous_lineaire`,
et `combien_dancres` l'**importe** — deux implémentations d'une même règle finiraient par rendre
deux verdicts, ce qui est exactement ce que le critère précédent a fait.

##### ⭐⭐ Et le résultat actionnable : l'itération ne sert à rien

La marche libre de `k` pas est comparée à **un seul pas de longueur `k` fois le pas**, pris le
long des normales de la surface de départ. Les deux vont au même endroit et ne diffèrent que par
une chose : la seconde ne recalcule **jamais** ses normales, donc elle ne peut pas dégrader sa
propre surface — ni ronger la grille plus d'une fois.

| bras | marche itérée | un seul grand pas | cellules gardées |
|---|---:|---:|---:|
| 1 | 44,2 µm | 44,2 µm | 996 contre 996 |
| 2 | 62,7 | 62,8 | 996 contre 896 |
| 3 | 103,5 | **96,6** | 996 contre 698 |
| 4 | 134,1 | **132,1** | **996 contre 671** |

> ⭐⭐ **À erreur égale, un seul grand pas rend 48 % de nappe en plus au bras 4.** Recalculer les
> normales à chaque tour n'apporte **rien** — la marche libre n'est meilleure que sur 8 marches
> sur 24 — et coûte un anneau de cellules par tour. Le dérouleur itéré peut donc être remplacé
> par un pas unique, plus simple et qui rend plus de surface.

⚠ Ce que ça ne dit **pas** : que la marche soit bonne. **Un seul pas coûte déjà 44,2 µm**, soit
les deux tiers d'une demi-feuille — et c'est ce premier pas, pas l'accumulation, qui est le vrai
poste de dépense.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante.** Le tableau des pistes est enfin cohérent :
> la dérive est **linéaire à ~33 µm par tour** avec un **premier pas à 44**, l'estimateur linéaire
> est donc le bon (d'où l'échec de la parabole), l'encadrement divise ce coût par deux (d'où son
> gain), et une troisième ancre n'a rien de plus à annuler (d'où son inutilité). Le seul poste qui
> reste est **le premier pas** : 44 µm pour un tour, là où l'accumulation n'en coûte que 33. C'est
> lui qu'il faut attaquer, et c'est une question sur **un** pas — donc mesurable sans marcher.

#### ⭐⭐⭐ LE TIERS DU COÛT D'UN PAS EST UNE LONGUEUR PRISE SUR LA MAUVAISE POPULATION

> Mesure : `src/nappe/le_cout_dun_seul_pas.py` (25 contrôles) →
> `docs/mesures/le_cout_dun_seul_pas.json`. Figure : `src/figures/figure_le_cout_dun_seul_pas.py`
> (18 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/le_cout_dun_seul_pas.py --cote 640 \
>     --json docs/mesures/le_cout_dun_seul_pas.json
> uv run python src/figures/figure_le_cout_dun_seul_pas.py \
>     --sortie docs/images/75_le_cout_dun_seul_pas.png
> ```

La tranche précédente avait laissé **un seul poste** : le premier pas coûte 42,7 µm là où
l'accumulation n'en coûte que 33 par tour. C'est une question sur **un** pas, donc mesurable sans
jamais marcher.

![le tiers du coût d'un pas](images/75_le_cout_dun_seul_pas.png)

##### La décomposition est une hiérarchie de LIBERTÉS

Chaque niveau donne à la marche **un paramètre de plus**, et l'écart entre deux niveaux est
exactement ce qu'une classe de remèdes rapporterait **au mieux**.

| niveau | ce qu'on donne | erreur | ce que l'écart mesure |
|---|---|---:|---|
| `E0` | rien — pas nominal, normales calculées | 42,7 µm | *(le départ)* |
| `E1` | **une** longueur, la meilleure | 28,7 | **14,0 µm — 33 %** |
| `E2` | plus **une** rotation globale | 27,4 | 1,3 µm — 3 % |
| `E3` | une longueur **par point**, le long de sa normale | 19,1 | 8,3 µm — 19 % |
| — | *le plancher, que rien ne prend* | **19,1** | 45 % |

> ⚠⚠⚠ **CE NE SONT PAS DES MÉTHODES, CE SONT DES BORNES.** `E1`, `E2` et `E3` sont choisis **en
> regardant la cible** : aucun dérouleur ne peut les atteindre. Et la liberté donnée est bornée
> **exprès** — laisser chaque point aller où il veut rendrait zéro et ne dirait rien.

⚠⚠ **Un défaut de conception attrapé par une sonde.** Ma première version mesurait `E3` le long de
la normale **de départ**, donc elle ne contenait pas la liberté de `E2` : les niveaux n'étaient pas
emboîtés, et une paire avait `E2` **meilleur** que `E3`. Une décomposition dont les niveaux ne
s'emboîtent pas ne décompose rien — ses écarts cessent de nommer une classe de remèdes. `E3` se
mesure désormais sur la normale **tournée**. ⚠ Et le contrôle « les quatre parts se somment à un »
**ne pouvait pas échouer** : la somme télescope par construction, et elle était verte sur la
version cassée, avec une part négative. Ce qui se vérifie est que chaque part soit **positive**.

##### ⭐⭐⭐ Et pourquoi le premier tiers existe : le pas nominal vient d'ailleurs

| paire | 4→5 | 5→6 | 6→7 | 7→8 | 8→9 | 9→10 | 12→13 |
|---|---:|---:|---:|---:|---:|---:|---:|
| écart **local** *(ne pas bouger)* | 171,0 | 104,1 | 100,3 | 115,4 | 114,5 | 70,9 | 63,9 |
| meilleure **longueur** | 152,4 | 111,8 | 105,0 | 115,2 | 98,2 | ⛔ 67,8 | ⛔ 63,9 |

> ⭐⭐⭐ **L'écart inter-feuilles mesuré DANS LA BOÎTE vaut 104,1 µm, pas les 135,5 µm du pas
> nominal.** Le nominal est la médiane sur **toutes** les spires du fragment ; la boîte où toute
> cette campagne mesure est une région plus serrée. La meilleure longueur suit l'écart **local**
> plutôt que le nominal sur **4 paires sur 5** hors butée. Ce tiers du coût n'est donc pas un
> réglage à trouver, **c'est un nombre à mesurer**.

⚠ **Deux paires butent sur le bord de la fenêtre de recherche** : leur minimum est ailleurs, ce
n'est pas un optimum mais un **refus**, et la médiane des longueurs est publiée **aussi** sans
elles — 111,8 µm sur 5 paires.

⚠⚠ **Une comparaison à seuil, retirée.** J'avais d'abord exigé que la meilleure longueur **égale**
l'écart local à deux pas de balayage près (3,4 µm) — un seuil qui demande plus de précision que la
médiane d'un nuage n'en a, et qui rendait **NON** pour 7,7 µm sur 110. La question qui se pose
vraiment est comparative et **sans seuil** : la meilleure longueur ressemble-t-elle plus à l'écart
local qu'au nominal ? Oui, 4 fois sur 5.

##### Ce que les autres niveaux disent

⛔ **La rotation globale ne prend rien** — 1,3 µm sur 42,7, soit 3 %. Il n'y a pas de biais
systématique de direction à corriger, et cette piste est fermée avant d'avoir été ouverte.

⭐ **Le plancher tient la feuille** : 19,1 µm contre 67,75. Un raccrochage **parfait** le long de
la normale laisserait donc largement de quoi tenir — rien n'interdit au raccrochage de marcher. Mais
il n'a que **19 %** du coût à prendre, là où la longueur en a **33 %** pour rien.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante, et c'est enfin une piste positive.** Un
> dérouleur réel ne connaît pas l'écart local — c'est justement ce qu'il cherche. Mais il connaît
> l'écart entre les spires qu'il a **déjà**, et la question devient : *l'écart local se prédit-il
> depuis les précédents ?* Douze paires consécutives sont publiées, donc la corrélation entre
> l'écart d'une paire et celui de la suivante se mesure **tout de suite et sans rien lire**. Si
> elle existe, le tiers du coût est récupérable sans regarder la cible.

#### ⛔ L'ÉCART DÉJÀ FRANCHI NE DIT PRESQUE RIEN DU SUIVANT — la dernière piste, fermée

> Mesure : `src/nappe/lecart_deja_franchi.py` (16 contrôles) →
> `docs/mesures/lecart_deja_franchi.json`. Figure : `src/figures/figure_lecart_deja_franchi.py`
> (16 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/lecart_deja_franchi.py --cote 640 \
>     --json docs/mesures/lecart_deja_franchi.json
> uv run python src/figures/figure_lecart_deja_franchi.py \
>     --sortie docs/images/75_lecart_deja_franchi.png
> ```

Un tiers du coût d'un pas vient d'une longueur prise sur la mauvaise population, et un dérouleur
ne peut pas mesurer l'écart qu'il n'a **pas encore** franchi. Il peut mesurer celui qu'il **vient
de** franchir : un dérouleur parti d'une paire d'ancres `r − 1` et `r` connaît, en chaque point,
la distance entre ces deux surfaces. C'était la seule piste positive qui restait, et elle est
mesurée sur **5 triplets, 5163 cellules**.

![l'écart déjà franchi](images/75_lecart_deja_franchi.png)

##### ⛔ Il ne prédit pas, et ce qu'il prédit va dans le mauvais sens

| | | | | | | | | | |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| écart **franchi** *(décile)* | 60 | 78 | 90 | 100 | 109 | 118 | 128 | 140 | 197 |
| écart **suivant** *(médiane)* | 135 | 101 | 98 | 108 | 108 | 106 | 96 | 89 | 113 |

> ⛔ **Quand l'écart franchi parcourt 137 µm, le suivant n'en parcourt que 46 — et en
> descendant.** ρ = **−0,119** sur 5163 cellules (p = 9·10⁻¹⁸) : négatif, significatif seulement
> parce que l'échantillon est grand, et minuscule. Si le premier prédisait le second, les points
> suivraient la diagonale du panneau B ; ils sont plats.

##### En erreur de marche, les quatre contendants

| | erreur médiane | bat le nominal sur |
|---|---:|---|
| pas **nominal** | 39,0 µm | *(la référence)* |
| **prédit** par point | 38,5 | **2 triplets sur 5** |
| **recentré** *(la médiane du franchi)* | **37,2** | **4 triplets sur 5** |
| témoin **mélangé** | 43,3 | 0 — il fait **pire** |
| *oracle (demande la réponse)* | *18,8* | — |

⚠⚠ **Un verdict sur la médiane que le compte par cas contredit n'est pas un verdict**, et c'est
une correction : la première version rendait « la prédiction bat le nominal : **OUI** » sur un
écart de **0,5 µm** alors qu'elle ne gagnait que sur deux triplets sur cinq. Les deux conditions
sont désormais exigées ensemble.

⚠⚠ **Le témoin mélangé fait PIRE que le nominal** (−4,3 µm). Une longueur par point tirée dans la
bonne distribution mais attribuée au mauvais point coûte donc plus qu'elle ne rapporte : c'est le
bruit d'un prédicteur qui ne prédit pas.

⚠ **Une part à dénominateur négligeable, retirée.** La première version publiait « la part
vraiment locale est **9,6** » — un rapport supérieur à un, qui n'a aucun sens comme part, parce
qu'il divisait par un gain de 0,5 µm. Aucune part n'est publiée quand son dénominateur est plus
petit que la marge de la mesure.

##### ⭐ Ce qui reste, petit mais réel

> ⭐ **Le RECENTRAGE seul** — la médiane de l'écart franchi, prise comme longueur unique et sans
> aucune information par point — bat le nominal sur **4 triplets sur 5**, pour **1,8 µm** des
> **20,2** que connaître le vrai écart rapporterait. Un dixième, gratuit et sans regarder la
> cible.

##### ⚠⚠⚠ Et un contrôle du dépôt qui était en retard par construction

Le `⛔` de la première version de cette figure est sorti en **carré vide**, et le contrôle de
traçabilité l'a laissé passer : `GLYPHES_ABSENTS` est une **liste écrite à la main**, donc en
retard sur tout caractère que personne n'y a ajouté.

> ⭐⭐ **La question est désormais posée à la POLICE.** Un caractère absent rend toujours le même
> dessin, celui du glyphe de secours : il suffit de comparer chaque caractère à un point de code
> de la zone à **usage privé**, où aucune police générale ne met de dessin. La liste ne sert plus
> que de **sonde** — elle vérifie que la question rend au moins les réponses déjà connues.

⚠ Et sa docstring **affirmait** écrire ces caractères en séquences d'échappement alors que le
fichier les portait **en clair** : un commentaire qui dit l'inverse de son code. Corrigé, et
vérifié par un contrôle sur la ligne de la constante — ⚠ resserré après une première version qui
les interdisait dans **tout** le fichier, où `✅` et `❌` servent légitimement à l'affichage du
terminal. Un contrôle trop large refuse du travail correct.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante.** Les trois postes du coût d'un pas sont
> maintenant chiffrés et leurs remèdes évalués : la **longueur** vaut 33 % et n'est récupérable
> qu'à un dixième depuis ce qu'un dérouleur possède ; la **direction** vaut 3 % ; le **point à
> point** vaut 19 % et c'est le domaine du raccrochage, dont le plancher (19,1 µm) tient
> largement la feuille. Le seul poste qui garde une marge inexpliquée est donc celui-là — et la
> question devient : **pourquoi le raccrochage mesuré n'en prend-il rien**, alors que sa borne
> parfaite en prendrait 19 % ?

#### ⭐⭐⭐ LE RACCROCHAGE LIT MAL — et c'est pourtant sa lecture qui le sauve

> Mesure : `src/nappe/le_raccrochage_choisit_il_bien.py` (16 contrôles) →
> `docs/mesures/le_raccrochage_choisit_il_bien.json`. Figure :
> `src/figures/figure_le_raccrochage_choisit_il_bien.py` (17 contrôles), le 2026-09-06.
>
> ```
> uv run python src/nappe/le_raccrochage_choisit_il_bien.py --cote 640 \
>     --json docs/mesures/le_raccrochage_choisit_il_bien.json
> uv run python src/figures/figure_le_raccrochage_choisit_il_bien.py \
>     --sortie docs/images/75_le_raccrochage_choisit_il_bien.png
> ```

Le poste **point à point** vaut 19 % du coût d'un pas et sa borne parfaite tient largement la
feuille — mais le raccrochage n'en prenait presque rien. **Deux explications restaient, avec des
remèdes opposés** : soit la géométrie refuse le gain, soit la lecture est mauvaise. Cette tranche
les sépare en confrontant les deux choix **sur les mêmes cellules** : 7 paires, **5442 cellules**.

![le raccrochage choisit-il bien](images/75_le_raccrochage_choisit_il_bien.png)

##### ⛔ Il lit, très peu

| | ρ avec le choix de l'oracle | écart médian au choix de l'oracle |
|---|---:|---:|
| **raccrochage** | **+0,076** *(p = 2·10⁻⁸, n = 5442)* | 17,35 voxels |
| gabarit **mélangé** | −0,006 *(p = 0,66)* | 19,3 |
| ne pas bouger | — | 18,59 |

> ⚠⚠ **L'oracle est borné à la MÊME fenêtre.** Le laisser viser hors de la fenêtre du
> raccrochage ferait de la comparaison une mesure de la **fenêtre** et non d'une lecture : il
> pourrait choisir un décalage que l'autre ne peut pas atteindre, et son avance ne dirait rien de
> leur accord.

⭐ **La lecture voit donc quelque chose** — son accord bat nettement celui du gabarit mélangé, qui
reste à zéro. ⚠ Mais **0,076 de corrélation, c'est un demi pour cent de variance** : elle voit
très peu, et son choix n'est que marginalement plus proche du bon que **ne pas bouger du tout**.

##### ~~⭐⭐⭐ Et le fait contre-intuitif : son déplacement d'ENSEMBLE nuit~~ — RETRACTÉ

> ⚠⚠⚠ **Ce qui suit est conservé pour la preuve, et le verdict est retiré.** Les nombres de ce
> tableau sont des **différences de médianes** ; l'écart apparié dit **+1,0 µm avec un intervalle
> qui enjambe zéro**. Voir [la rétraction](#-retraction-partielle-de-cette-tranche--trois-de-ses-quatre-affirmations-ne-survivent-pas-à-lappariement)
> plus bas. Ce qui tient : la lecture **par cellule** bat sa propre médiane, apparié compris.

| | erreur médiane |
|---|---:|
| ne pas bouger | 42,7 µm |
| **raccroché** | **37,1** |
| raccroché, **son biais retiré** | **36,5** |
| sa propre **médiane seule** | **47,5** |
| gabarit mélangé | 52,9 |
| *oracle (même fenêtre)* | *19,8* |

> ~~⭐⭐⭐ **Le déplacement d'ensemble que le raccrochage trouve est NUISIBLE**~~ ⛔ RETRACTÉ : sa médiane
> appliquée partout rend **47,5 µm** contre 42,7 en ne bougeant pas, soit **−4,8**. C'est sa
> lecture **par cellule** qui reprend tout et le fait descendre à 37,1 — elle bat sa propre
> médiane sur **4 paires sur 7**. Ce n'était pas l'hypothèse : on aurait attendu qu'une
> corrélation de 0,076 ne serve à rien et qu'un recentrage fasse le travail.

⚠ **Mais son erreur ne bat PAS celle de son gabarit mélangé** (3 paires sur 7). La lecture est
mesurablement meilleure que le bruit dans ce qu'elle **choisit**, pas encore dans ce qu'elle
**coûte**.

##### ⭐⭐ Ce que ça tranche

> ⭐⭐⭐ **La géométrie ne refuse RIEN.** L'oracle prend **22,9 µm** dans la même fenêtre, avec les
> mêmes points et les mêmes directions. Ce n'est donc pas la borne qui est illusoire — **c'est la
> lecture qui est le chantier**.
>
> ⭐⭐ **C'est la seule affirmation de cette tranche que l'appariement RENFORCE** : −23,8 µm sur
> **sept pas sur sept**, intervalle [−25,2 ; −21,1]. Là où tout gain du raccrochage s'évanouit dès
> qu'on apparie, celui de sa borne ne bouge pas — le chantier n'est pas aux trois quarts ouvert,
> il l'est **entier**.

⚠ Un défaut de dessin attrapé par la figure elle-même : une barre **négative** — l'accord du
mélange, précisément ce qu'on veut montrer — faisait **lever** PIL, qui exige que le coin haut
d'un rectangle vienne en premier. Les deux ordonnées sont triées.

##### ⭐ Le remède d'une ligne, mesuré avant d'être écrit comme une piste

Son déplacement d'ensemble étant nuisible, le premier geste n'est pas de lire mieux mais de
**retirer le biais** : le même raccrochage, sa lecture par cellule intacte, son décalage médian
soustrait.

> ⭐ **Ça marche, et c'est l'une des deux affirmations qui SURVIVENT à l'appariement** :
> **−1,5 µm, 5 pas sur 7, intervalle [−6,0 ; −1,1]** entièrement négatif. La différence de
> médianes annonçait 0,6 µm ; l'écart apparié, qui est le bon instrument ici, en donne 1,5.
> C'est le premier gain que cette campagne obtienne en **changeant** quelque chose plutôt qu'en
> mesurant une borne — et il tient.

⚠⚠ **Mais il vaut 0,6 µm et non les 4,8 que j'avais annoncés**, et la correction est faite avant
publication parce que la mesure a précédé la phrase. « Sa médiane seule coûte 4,8 µm » et « son
biais coûte 4,8 µm » ne sont **pas la même quantité** : le premier compare un déplacement
d'ensemble **sans** lecture par cellule à l'immobilité ; le second retire ce déplacement **d'une**
lecture par cellule. Le biais et la lecture ne s'additionnent pas.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante.** Pour la première fois la campagne désigne un
> **chantier** plutôt qu'une porte fermée : améliorer ce que le raccrochage **lit**. Le geste
> gratuit — retirer son biais — est pris ; il reste l'essentiel de l'écart entre le raccrochage et
> l'oracle, dans la même fenêtre et sur les mêmes cellules. Et la mesure dit où chercher : avec
> ρ = 0,076, ce que la corrélation de gabarit choisit n'a presque rien à voir avec le bon décalage.
> La question suivante porte donc sur le **gabarit lui-même** — lu sur une seule spire, sur une
> largeur d'un quart de pas, et jamais comparé à ce qu'un gabarit lu ailleurs, ou plus large,
> donnerait.

#### ⚠⚠⚠ RETRACTION PARTIELLE DE CETTE TRANCHE — trois de ses quatre affirmations ne survivent pas à l'appariement

> 2026-09-06, en construisant `le_gabarit_lu_ailleurs`. Instrument :
> `src/commun/lecart_apparie.py` (9 contrôles). Mesure re-lancée :
> `src/nappe/le_raccrochage_choisit_il_bien.py` (21 contrôles).

**Le défaut est un choix d'instrument, pas un calcul faux.** Cette tranche comparait des méthodes
par la **différence de leurs médianes**. Or sur les sept pas de la boîte, **ne rien faire coûte de
32,2 à 73,9 µm selon le pas** : la dispersion d'un pas à l'autre vaut **quatre fois** l'écart entre
deux méthodes. Une différence de médianes s'y fait donc décider par le tirage des pas.

Les mêmes six questions, reprises **pas par pas** — chaque écart avec son intervalle quand
n'importe quel pas sort :

| comparaison | écart apparié | pas améliorés | à un pas de moins | verdict |
|---|---:|---:|---|---|
| raccroché contre **ne pas bouger** | **−1,2 µm** | 4/7 | [−5,2 ; +2,5] | ⛔ ne tranche pas |
| son **biais retiré** contre raccroché | **−1,5 µm** | 5/7 | [−6,0 ; −1,1] | ✅ **tranche** |
| raccroché contre son **mélange** | +0,1 µm | 3/7 | [−3,2 ; +5,8] | ⛔ ne tranche pas |
| raccroché contre **sa propre médiane** | **−2,0 µm** | 4/7 | [−4,0 ; −1,0] | ✅ **tranche** |
| **sa médiane seule** contre ne rien faire | +1,0 µm | 3/7 | [−1,1 ; +5,8] | ⛔ ne tranche pas |
| ⭐⭐ **l'ORACLE** contre ne pas bouger | **−23,8 µm** | **7/7** | [−25,2 ; −21,1] | ✅✅ **tranche** |

⛔ **Ce qui tombe** : le gain de **5,6 µm** du raccrochage sur l'immobilité — l'écart apparié vaut
−1,2 µm et son intervalle enjambe zéro ; et la **nuisance de son déplacement d'ensemble**
(−4,8 µm annoncés), dont l'écart apparié vaut **+1,0 µm** avec un intervalle qui enjambe zéro
lui aussi. Les deux nombres restent dans le fichier de mesure : **retirer un nombre publié
effacerait la preuve de sa propre correction.**

✅ **Ce qui tient, et le motif est cohérent** : les deux comparaisons qui survivent sont exactement
celles qui confrontent le raccrochage à **une variante de lui-même sur les mêmes cellules** — sa
lecture par cellule bat sa propre médiane (−2,0 µm, intervalle entièrement négatif), et retirer son
biais améliore (−1,5 µm, idem). Elles sont **appariées par construction** ; les trois qui tombent
ne l'étaient pas.

> ⭐⭐⭐ **Et la conclusion de la tranche sort RENFORCÉE, pas affaiblie.** « La géométrie ne refuse
> rien » repose sur l'avance de l'oracle : **−23,8 µm, sept pas sur sept, intervalle entièrement
> négatif**. C'est le résultat le plus solide de toute la campagne de déroulage. Là où tout gain du
> raccrochage s'évanouit dès qu'on apparie, celui de sa borne ne bouge pas — **le chantier de la
> lecture n'est pas seulement ouvert, il est entier**.

⚠⚠ **Et la règle que ce dépôt s'était donnée en prose est devenue un calcul.** « Un verdict qui
change avec la population n'est pas un verdict » était écrit depuis des semaines ; à sept cas, on
ne le respecte qu'en le **mesurant**. `lecart_apparie.tranche` exige donc trois choses, dont
aucune n'est un seuil : l'écart médian négatif, la **majorité** des cas améliorés, et l'intervalle
à un cas de moins **entièrement** négatif.

#### ⭐⭐⭐ LE GABARIT LUI-MÊME, MIS EN QUESTION — seize formes, et la meilleure vaut 0,9 µm

> Mesure : `src/nappe/le_gabarit_lu_ailleurs.py` (49 contrôles) →
> `docs/mesures/le_gabarit_lu_ailleurs.json`. Figure :
> `src/figures/figure_le_gabarit_lu_ailleurs.py` (23 contrôles), le 2026-09-06.
>
> ```bash
> uv run python src/nappe/le_gabarit_lu_ailleurs.py --cote 640 \
>     --json docs/mesures/le_gabarit_lu_ailleurs.json
> uv run python src/figures/figure_le_gabarit_lu_ailleurs.py \
>     --sortie docs/images/75_le_gabarit_lu_ailleurs.png
> ```

Le raccrochage cherche une **forme**, et cette forme n'avait jamais été mise en question : lue sur
**une seule spire** — celle du départ — sur une demi-largeur d'**un quart de pas**, et jamais
comparée à rien. Seize formes sont balayées : **quatre demi-largeurs** (8, 15, 31, 61 voxels,
dérivées de la demi-feuille de 30,59 et non choisies — la valeur en service est l'un des barreaux)
× **quatre sources** — la spire de **départ**, la plus **ancienne déjà atteinte**, la **moyenne**
de toutes celles déjà déroulées, et ⛔ celle d'**arrivée**, qui n'existe pas en production et sert
de **borne**.

![le gabarit lu ailleurs](images/75_le_gabarit_lu_ailleurs.png)

⚠⚠ **Deux propriétés rendent le balayage honnête, et sans elles il mesurerait autre chose.** La
**fenêtre de recherche est invariante** : `correler` ne rend que les positions où le gabarit tient
entier, donc les centres balayés valent toujours ±une demi-feuille quelle que soit la largeur —
sans quoi une forme large gagnerait en visant des décalages que les autres ne peuvent pas
atteindre. Et **toutes sont jugées sur les mêmes cellules** : la ligne la plus longue est lue
**une fois** et chaque largeur en est une tranche centrée, sinon un gabarit large écarterait plus
de cellules et l'on comparerait des populations.

##### ⚠⚠⚠ Le témoin LIT — et il fait même mieux que la vraie forme

**Neuf des seize gabarits MÉLANGÉS s'accordent positivement avec l'oracle**, et à demi-largeur 31
le mélange obtient **+0,192 contre +0,175** pour la forme qu'il détruit. Ce n'est pas un défaut :
une ligne qui traverse des feuilles est **périodique**, donc n'importe quel vecteur fixe y trouve
ses maxima aux mêmes phases. Comparer les accords **bruts** créditerait donc une forme large pour
ce que son propre mélange lit aussi bien — ce que la première version de cette mesure a failli
publier. Chaque forme est désormais jugée sur son accord **net de son propre mélange**.

##### ⭐⭐ La forme en service ne bat pas l'immobilité — et une autre, si

| forme | accord NET | contre ne rien faire | contre le déployé |
|---|---:|---|---|
| **en service** — 15 vx / départ | +0,176 | −0,4 µm, 3/6, [−1,1 ; +0,3] ⛔ | 0 |
| meilleure **lecture** — 8 vx / départ | **+0,196** | −1,1 µm, 3/6, [−3,9 ; +1,7] ⛔ | **+2,8 µm** (pire) |
| ⭐ meilleure **marche** — 8 vx / **ailleurs** | +0,054 | **−2,2 µm, 4/6, [−2,8 ; −1,7]** ✅ | **−0,9 µm, 4/6, [−1,7 ; −0,1]** ✅ |
| ⛔ borne — 15 vx / arrivée | +0,057 | −1,4 µm, 3/6, [−3,1 ; +0,3] ⛔ | −0,2 µm, [−1,4 ; +1,1] ⛔ |

> ⭐⭐⭐ **Un gabarit deux fois plus étroit, lu sur une spire ANTÉRIEURE, est la seule des seize à
> trancher sur les deux comparaisons** : −0,9 µm contre la forme en service et −2,2 µm contre
> l'immobilité, sur 4 pas sur 6, intervalles entièrement négatifs. C'est petit, et c'est le
> premier gain de forme que la campagne obtienne qui survive à l'appariement.

⚠⚠ **Et les deux critères se contredisent, ce qui est le second résultat.** La forme qui **lit** le
mieux (8 vx / départ, net 0,196) **marche** plus mal que celle en service (+2,8 µm). Un accord de
rang est **invariant d'échelle** : mieux **ordonner** les décalages n'est pas mieux **marcher**.
Publier un seul des deux critères aurait fait passer ce désaccord pour un accord.

##### ⛔ La famille des gabarits est pauvre, et la borne le prouve

Le gabarit de la spire d'**arrivée** — celui qu'on ne peut pas avoir, puisque l'arrivée est ce que
la marche calcule — **ne lit pas mieux** (2 pas sur 6) et **ne marche pas mieux de façon
décidable** (−0,2 µm, intervalle [−1,4 ; +1,1]).

> ⛔ **Même parfaite, la forme ne rend presque rien.** Le meilleur gain de toute la famille vaut
> **0,9 µm** sur les **30,7** qui séparent le déployé de l'oracle. Ce qui manque à la lecture
> n'est donc **ni la forme cherchée, ni où on l'apprend**.

##### ⚠⚠ Le remède évident, mesuré puis REFUTÉ

Un accord de rang étant invariant d'échelle, l'explication naturelle du désaccord entre les deux
critères est l'**amplitude** : une forme qui choisit des décalages mal calibrés garde son rang et
paie son coût. Mesuré : la forme en service choisit une amplitude **0,856×** celle de l'oracle.
Recaler par un facteur unique, **ajusté hors échantillon** — chaque pas jugé au facteur que les
**autres** pas ont préféré —, **coûte 4,0 µm**.

⚠ L'ajustement hors échantillon n'est pas une précaution décorative : soixante-trois facteurs
essayés sur les pas qui les jugent garantissent qu'un tombe bien. Le contrôle qui l'impose est
construit pour **discriminer** — un cas dont l'optimum est à l'opposé de celui des autres doit
recevoir le facteur des autres, pas le sien.

##### ⚠⚠⚠ Et la limite est COMPTÉE plutôt que déplorée

La raison pour laquelle ces écarts sont si petits par rapport à leurs intervalles est mesurée :

| côté de boîte | spires lisibles | pas complets |
|---:|---:|---:|
| 640 vx (publié) | 9 | **6** |
| 960 vx | 10 | **8** |
| 1280 vx | 10 | 8 |
| 1920 vx | 10 | 8 |

> ⚠⚠⚠ **Élargir la fenêtre plafonne à huit pas.** Ce qui borne la campagne n'est donc **pas la
> boîte** mais le **nombre de spires segmentées** dans cette région. À six ou huit pas, un écart
> de quelques micromètres ne se distingue pas de la dispersion entre pas — et c'est exactement ce
> que la rétraction ci-dessus a montré. Le prochain gain de résolution de mesure ne vient pas d'un
> réglage : il vient de **plus de spires**.

⚠ **Un vrai défaut attrapé en relisant les spires lues** : la source « ailleurs » était écrite
comme « la plus ancienne spire **autre que le départ** », ce qui rendait la spire **5** pour le pas
4 → 5, c'est-à-dire **exactement la surface que la marche cherche**, dans une variante annoncée
disponible en production. La règle est désormais la même que pour la moyenne — rien au-delà du
départ — et le premier pas de la boîte, qui n'a alors aucun candidat, est **écarté entier et
compté** plutôt que servi par une source qui triche.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante.** Le chantier de la lecture reste **entier** —
> l'oracle prend 23,8 µm sur sept pas sur sept — et trois portes viennent de se fermer dessus : ce
> n'est ni la **forme** cherchée (16 variantes, la meilleure vaut 0,9 µm), ni **où** on l'apprend
> (une spire ancienne fait aussi bien qu'une spire parfaite), ni l'**amplitude** de ce qu'elle
> choisit (le recalage coûte). Ce qui n'a pas été mis en question, c'est le **critère** : une
> corrélation normalisée d'intensité, cellule par cellule et sans voisinage — alors que
> `le_raccrochage_a_la_matiere` possède déjà `accorder_les_voisins`, que ces deux tranches
> **n'utilisent pas**. Et il faudra le juger sur **huit pas**, pas six.

#### ⭐⭐⭐ LE CRITÈRE — et la mesure évaluait un raccrochage plus grossier que celui qui tourne

> Mesure : `src/nappe/le_critere_du_raccrochage.py` (22 contrôles) →
> `docs/mesures/le_critere_du_raccrochage.json` (**8 pas**, boîte de 960) et
> `docs/mesures/le_critere_du_raccrochage_640.json` (**7 pas**, boîte de 640). Figure :
> `src/figures/figure_le_critere_du_raccrochage.py` (22 contrôles), le 2026-09-06.
>
> ```bash
> uv run python src/nappe/le_critere_du_raccrochage.py --cote 960 \
>     --json docs/mesures/le_critere_du_raccrochage.json
> uv run python src/nappe/le_critere_du_raccrochage.py --cote 640 \
>     --json docs/mesures/le_critere_du_raccrochage_640.json
> uv run python src/figures/figure_le_critere_du_raccrochage.py \
>     --sortie docs/images/75_le_critere_du_raccrochage.png
> ```

⚠⚠⚠ **Le défaut de méthode d'abord, parce qu'il invalide la question précédente.** Le raccrochage
**déployé** — celui de `le_raccrochage_a_la_matiere`, qui produit les nombres publiés — passe ses
décalages par `accorder_les_voisins`, la médiane du voisinage 3×3 **de grille**. Les deux tranches
précédentes **ne l'appelaient pas** : elles échantillonnaient des cellules au hasard, ce qui
détruit l'adjacence et rend l'accord inappelable. Elles jugeaient donc un raccrochage **plus
grossier que celui qui tourne** — c'est-à-dire, mot pour mot, le défaut que ce dépôt a nommé : une
batterie verte sur un module dont le seul chemin non testé est celui qui produit le nombre publié.

Cette mesure travaille donc **sur la grille**. La forme cherchée et la fenêtre sont **fixées** ;
ce qui varie est le **critère**, c'est-à-dire comment on désigne un décalage.

![le critère du raccrochage](images/75_le_critere_du_raccrochage.png)

##### ⭐⭐ Le chemin déployé bat l'immobilité — et tout son gain vient du VOISINAGE

Huit pas, 16 537 cellules retenues sur 16 569 lisibles (boîte de 960 voxels) :

| critère | erreur | contre ne rien faire | contre sa version brute |
|---|---:|---|---|
| ne rien faire | 43,6 µm | — | — |
| maximum d'intensité | 51,1 | +1,3 · 3/8 · [+0,1 ; +2,5] ⛔ | — |
| corrélation seule | 45,8 | −0,2 · 4/8 · [−1,6 ; +1,2] ⛔ | — |
| ⭐ **corrélation + accord** *(déployé)* | **37,5** | **−2,1 · 7/8 · [−2,2 ; −1,9]** ✅ | **−4,2 · 5/8 · [−4,3 ; −4,2]** ✅ |
| corrélation centrée | 45,5 | −0,2 · 4/8 · [−1,0 ; +0,5] ⛔ | — |
| ⭐ **corrélation + accord + centrage** | 37,6 | **−3,5 · 7/8 · [−3,7 ; −3,2]** ✅ | −3,6 · 5/8 ✅ |
| *témoin : mélange* | 60,2 | +4,7 · 1/8 ⛔ | — |
| *témoin : mélange accordé* | 57,1 | +1,9 · 2/8 ⛔ | −2,7 · 6/8 · [−2,8 ; −2,6] ✅ |
| ⛔ oracle | 20,0 | **−23,5 · 8/8 · [−23,6 ; −23,4]** ✅ | — |

> ⭐⭐⭐ **C'est la première fois que le raccrochage déployé est mesuré TEL QU'IL TOURNE, et il
> gagne** : 37,5 µm contre 43,6, sur 7 pas sur 8, intervalle entièrement négatif.
>
> ⚠⚠⚠ **PORTÉE DE CE VERDICT, marquée le 2026-09-07 : il vaut pour UN pas, et pour un pas
> seulement.** Mesuré depuis : sur une marche de huit bras qui repart de sa propre prédiction, le
> même raccrochage porte **2 spires contre 4** pour le pas normal seul, et l'écart apparié
> tranche **dans l'autre sens** (−52,0 µm, 6/8 bras). Voir *« LA MARCHE : le raccrochage déployé
> porte MOINS LOIN que le pas normal seul »*. Le gain sur un pas n'est pas rétracté ; ce qui l'est
> est son extension implicite à un déroulement.

⚠⚠ **Et le fait qui redéfinit le chantier : la corrélation SEULE ne tranche pas** (−0,2 µm,
4 pas sur 8). Tout le gain vient de l'**accord de voisinage**, c'est-à-dire d'un énoncé sur la
**matière** — *une feuille de papyrus est lisse à l'échelle de trois cellules de grille* — et non
d'une lecture d'intensité. Le maximum d'intensité, lui, est **pire que ne rien faire** (+1,3 µm),
ce qui confirme ce que `le_raccrochage_a_la_matiere` avait mesuré.

##### ⚠⚠⚠ Le témoin refuse la lecture facile — et le lire correctement la renforce

Une médiane de voisinage améliore **n'importe quoi**. Le même accord appliqué aux décalages d'un
gabarit **mélangé** gagne **−2,7 µm** sur sa propre version brute, et il **tranche** lui aussi.
Une part du gain de l'accord est donc du **lissage pur**.

> ⚠⚠ **Mais il faut lire ce chiffre au bon endroit** : ce gain est pris contre sa propre version
> brute, qui est catastrophique. Le mélange **accordé** reste à **57,1 µm**, soit **+1,9 au-dessus
> de ne rien faire** — le lissage répare du bruit, il n'en fabrique pas un gain. L'avance de la
> lecture (−4,2 contre −2,7) est ce qui reste après avoir retiré ce que le lissage rend tout seul.

##### ⚠⚠⚠ DEUX populations, parce qu'un verdict d'une seule bascule

La tranche précédente a mesuré qu'à six ou sept pas un verdict change quand un pas sort. Cette
mesure est donc publiée **deux fois**, sur deux boîtes :

| | 8 pas / 16 537 cellules | 7 pas / 6 582 cellules |
|---|---|---|
| l'accord améliore la **lecture** | −4,2 ✅ | −2,5 ✅ |
| accord + centrage bat l'**immobilité** | −3,5 ✅ | −5,8 ✅ |
| le chemin déployé seul bat l'immobilité | −2,1 ✅ | −4,1 ⛔ (4/7, [−7,9 ; +0,4]) |
| le lissage améliore le **bruit** | −2,7 ✅ | −0,5 ⛔ |

> ⭐⭐ **Ce qui est ACQUIS est ce qui tranche des deux côtés** : l'accord de voisinage améliore la
> lecture, et **corrélation + accord + retrait du biais bat l'immobilité**. Les deux autres lignes
> ont **basculé** avec la population — et les publier sans la seconde boîte aurait été exactement
> la faute que la rétraction ci-dessus vient de corriger.

⚠ Le contrôle de la figure l'impose plutôt que de l'espérer : la seconde population **n'est pas
optionnelle** une fois la première publiée. La sauter quand elle manque serait une vérification
incapable de s'exécuter, là même où l'on sait qu'un verdict bascule.

⚠ **Un vrai défaut attrapé par le vrai volume, que la fixture laissait passer par chance.** Le
critère `maximum` recevait la ligne **entière** avec les décalages de la seule **fenêtre** :
`sommet` prenait donc l'argmax sur 92 colonnes et indexait un tableau de 62. Sur le fragment ça
lève ; sur la fixture, dont le maximum tombe toujours dans les premières colonnes, **ça passait**.
Le commentaire disait « cherché sur la tranche » pendant que le code cherchait partout. Le
contrôle ajouté est construit pour discriminer : une ligne dont le maximum **global** est hors
fenêtre doit rendre le meilleur point **de la fenêtre**.

⚠ Coût : **149 blocs, 298 Mio** téléchargés pour passer de la boîte de 640 à celle de 960 —
c'est le prix des deux pas supplémentaires que le relevé de la tranche précédente annonçait.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante, et c'est un chantier neuf.** Ce qui fait
> marcher le raccrochage n'est **pas** la corrélation d'intensité — elle ne tranche pas seule —
> mais la **contrainte de lissité de la feuille**. Or cette contrainte est aujourd'hui exploitée
> de la façon la plus pauvre possible : une médiane sur un voisinage de **trois cellules**,
> appliquée **une fois**. Il reste **17,5 µm** entre le chemin déployé (37,5) et l'oracle (20,0),
> et la question suivante est de savoir jusqu'où la lissité peut aller — un voisinage plus large,
> plusieurs passes, ou un **ajustement de surface** plutôt qu'une médiane. ⚠ Et le témoin du
> mélange accordé devra suivre à chaque étage : plus on lisse, plus le bruit s'améliore aussi.

#### ⛔ LA LISSITÉ EST ÉPUISÉE À L'ÉTAGE DÉPLOYÉ — au-delà, tout le gain est du lissage

> Mesure : `src/nappe/la_lissite_de_la_feuille.py` (19 contrôles) →
> `docs/mesures/la_lissite_de_la_feuille.json`. Figure :
> `src/figures/figure_la_lissite_de_la_feuille.py` (16 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/la_lissite_de_la_feuille.py --cote 960 \
>     --json docs/mesures/la_lissite_de_la_feuille.json
> uv run python src/figures/figure_la_lissite_de_la_feuille.py \
>     --sortie docs/images/75_la_lissite_de_la_feuille.png
> ```

Le voisinage s'élargit — 3×3, 5×5, 9×9, 17×17 — et s'itère — une passe, deux, trois. Huit pas,
**15 618 cellules** retenues sur 16 569, tous les étages jugés sur **la même population**, fixée
par le plus large : sans ça un 17×17 serait noté sur le cœur de la grille pendant qu'un 3×3 le
serait sur presque tout, et l'écart mesuré porterait sur les bords.

![la lissité de la feuille](images/75_la_lissite_de_la_feuille.png)

| étage | voisins | LECTURE | contre ne rien faire | BRUIT | **hors lissage** |
|---|---:|---:|---|---:|---:|
| brut | 1 | 44,2 µm | −0,4 · 4/8 · [−1,2 ; +0,5] ⛔ | 59,6 | +0,0 |
| ⭐ **3×3, une passe** *(déployé)* | 9 | **35,7** | −2,5 · 6/8 · [−2,6 ; −2,4] ✅ | 57,6 | **−1,1** |
| 5×5 | 25 | 35,9 | −2,7 · 7/8 · [−3,2 ; −2,2] ✅ | 55,7 | −0,8 |
| 9×9 | 81 | 40,9 | −3,1 · 5/8 · [−3,5 ; −2,6] ✅ | 52,6 | **+2,8** |
| 17×17 | 289 | 42,6 | −0,7 · 4/8 · [−2,2 ; +0,9] ⛔ | 47,4 | **+6,4** |
| 3×3, deux passes | 9 | 35,8 | −2,6 · 6/8 ✅ | 57,2 | −0,9 |
| 3×3, trois passes | 9 | 35,6 | −2,8 · 6/8 ✅ | 56,6 | −1,0 |

> ⛔ **Aucun étage ne bat celui en service.** Le meilleur écart apparié au déployé vaut **+0,4 µm**
> (3 pas sur 8, intervalle [0,0 ; 0,9]) : il ne tranche pas, et il est du mauvais côté.

##### ⭐⭐⭐ Et la colonne qui explique tout : la part HORS LISSAGE

Contre l'immobilité, élargir **semble** aider : −2,5 → −2,7 → −3,1 µm. Mais le même lissage
appliqué aux décalages d'un gabarit **mélangé** gagne de plus en plus, lui aussi. Ce qui reste
une fois cette part retirée — ce que la **lecture** apporte à cet étage — **s'effondre et change
de signe** : −1,1 → −0,8 → **+2,8** → **+6,4**.

> ⭐⭐⭐ **Au-delà du 3×3, tout le gain supplémentaire est du lissage pur.** Un voisinage large
> n'améliore pas la lecture : il l'efface. Le panneau A le montre sans commentaire — l'erreur de
> la lecture et celle du bruit **convergent** quand la fenêtre s'élargit, de **21,9 µm** d'écart
> au 3×3 à **4,8 µm** au 17×17. Deux courbes qui se rejoignent, c'est un lissage qui a détruit ce
> qui distinguait la lecture du hasard.

⚠ **Itérer ne paie pas davantage qu'élargir** : deux et trois passes du 3×3 rendent 35,8 et
35,6 µm, avec des parts hors lissage de −0,9 et −1,0 — soit la même chose que la passe unique
(−1,1). Les deux façons d'élargir butent au même endroit.

> ⛔ **Le 3×3 une passe n'est donc pas un réglage heureux : c'est l'optimum de la famille**, et la
> mesure dit pourquoi. C'est la **quatrième porte fermée** sur la lecture, après la forme, l'endroit
> où on l'apprend et l'amplitude de ce qu'elle choisit. Il reste **15,7 µm** entre l'étage déployé
> (35,7) et l'oracle (20,0), et la lissité n'ira pas les chercher.

⚠ **Deux vrais défauts, dans le code que cette tranche a dû généraliser.**

1. `accorder_les_voisins` avait un seuil de **cinq** voisins écrit en dur. Ce n'était pas un
   réglage — neuf cellules, cinq est la **majorité** — mais le laisser fixe pendant que la fenêtre
   grandit aurait laissé un 9×9 s'accorder sur cinq cellules sur quatre-vingt-une, c'est-à-dire
   fabriquer une confiance que le voisinage ne porte pas. Il est désormais **dérivé**, et le
   contrôle vérifie qu'il retombe exactement sur le 5 déployé.
2. Un décalage **plus grand que la grille** faisait lever numpy sur des formes incompatibles : les
   tranches décalées cessent de se correspondre dès que le décalage dépasse la dimension. Un voisin
   qui n'existe pas est désormais **sauté** — ce qui est exact, il ne compte ni dans la médiane ni
   dans le décompte de majorité — et une fenêtre plus grande que la grille ne retient simplement
   rien, au lieu de tracer.

⚠ **Et une affirmation à moi, corrigée par la mesure** : j'avais écrit que le masque rétrécit à
**chaque** passe. Faux — sur une grille pleine il se stabilise dès la seconde (77 → 77 → 77),
parce que seuls les coins manquent de majorité et que leur absence n'en prive personne d'autre.
Le contrôle dit désormais ce qui est vrai (le masque ne **grandit** jamais) et le rend
discriminant par un cas où il rétrécit vraiment : un **îlot** de cellules lisibles, mangé
passe après passe jusqu'à rien.

⚠ **Un refactor, avec son contrôle** : le parcours des pas — une traversée du volume pour le
gabarit, une pour les lignes — est extrait dans `parcourir_les_pas` et partagé par les deux
mesures. Le contrôle est que les **deux images publiées de `le_critere_du_raccrochage` sortent
identiques** après extraction. De même, l'échelle horizontale d'écarts appariés vit désormais dans
`figure_commune.echelle_appariee`, avec un contrôle qui compare deux rendus ne différant **que**
par l'intervalle : s'ils sortaient identiques, le trait ne serait pas dessiné et la figure ferait
lire un verdict là où il n'y en a pas.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante.** Quatre portes sont fermées sur la lecture —
> la forme, son lieu d'apprentissage, son amplitude, sa lissité — et le chantier vaut toujours
> **15,7 µm**. Ce qui n'a jamais été mis en question, c'est ce que le raccrochage **lit** : une
> **intensité**. Or `le_champ_de_fibres` et `fiber_orientation` existent dans ce dépôt et
> décrivent la matière autrement — par l'**orientation** locale plutôt que par la brillance. Un
> gabarit d'orientation n'aurait pas le défaut mesuré ici, qui est que l'intensité d'une feuille
> ressemble à celle de sa voisine. ⚠ Et il faudra le juger avec les mêmes instruments : population
> unique, écart apparié, témoin mélangé à chaque étage.

#### ⭐⭐⭐ LA MOITIÉ DE L'ERREUR EST UN PLANCHER — et la vérité, elle, est plate

> Mesure : `src/nappe/loracle_est_il_atteignable.py` (17 contrôles) →
> `docs/mesures/loracle_est_il_atteignable.json`. Figure :
> `src/figures/figure_loracle_est_il_atteignable.py` (15 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/loracle_est_il_atteignable.py --cote 960 \
>     --json docs/mesures/loracle_est_il_atteignable.json
> uv run python src/figures/figure_loracle_est_il_atteignable.py \
>     --sortie docs/images/75_loracle_est_il_atteignable.png
> ```

⚠⚠⚠ **Cette tranche vient AVANT la cinquième idée de lecture, et c'est délibéré.** Quatre portes
se sont fermées sur la lecture et l'écart au chemin déployé vaut toujours une quinzaine de
micromètres. Avant d'en ouvrir une cinquième, il fallait demander si cet écart est **prenable** —
c'est-à-dire décomposer les 20 µm de la borne elle-même. L'oracle choisit **le long de la
normale**, **dans une fenêtre**, sur une **grille d'un voxel** : chacune de ces trois contraintes
a un prix, et le reste est du sol.

![l'oracle est-il atteignable](images/75_loracle_est_il_atteignable.png)

| | erreur médiane |
|---|---:|
| ne rien faire | 43,6 µm |
| chemin **déployé** | 37,5 |
| oracle, grille d'un voxel | 20,0 |
| oracle, grille **fine** (¼ de voxel) | 20,0 |
| ⭐ **le RAYON**, tout décalage confondu | **18,2** |

| terme | écart apparié | verdict |
|---|---|---|
| ce que coûte la **grille** d'un voxel | +0,0 µm · 0/8 · [0,0 ; 0,0] | ⛔ **rien** |
| ce que coûte la **fenêtre** | −2,2 µm · 8/8 · [−2,5 ; −2,0] | ✅ tranche |
| ce qui reste au chemin **déployé** | −20,1 µm · 8/8 · [−23,3 ; −16,8] | ✅ tranche |

> ⛔ **Affiner le décalage ne rendrait pas un micromètre.** La grille d'un voxel coûte
> **exactement zéro**, sur zéro pas sur huit : une piste évidente se ferme d'avance.

> ⭐⭐⭐ **Et la moitié de ce que coûte un pas n'est PAS une affaire de lecture.** Le rayon laisse
> **18,2 µm**, soit **48,5 %** de l'erreur du chemin déployé : c'est la distance à laquelle la
> normale passe de la feuille visée, et **aucun décalage sur cette normale ne descend en dessous**.
> Seule une autre **direction** la prendrait. Ce qui reste à la lecture est l'écart apparié
> **−20,1 µm**, qui tranche sur huit pas sur huit.

⚠ La fenêtre, elle, coûte 2,2 µm — mais **l'élargir n'est pas une méthode** : une fenêtre plus
large peut se poser sur la feuille **voisine**. C'est un terme de décomposition, pas un remède.

##### ⭐⭐⭐ Et la découverte : le champ que devrait produire une méthode parfaite est PLAT

| champ de décalages | rugosité |
|---|---:|
| l'**ORACLE** — ce qu'une méthode parfaite produirait | **0,00 vx** |
| le **RACCROCHAGE** déployé | **3,48** |
| *témoin : gabarit mélangé (bruit pur)* | *6,26* |

La rugosité est *de combien un décalage s'écarte de la médiane de ses voisins de grille*. Celle de
l'oracle vaut **zéro** — son champ est constant par morceaux à l'échelle du voxel — et le lisser ne
coûte que **0,2 µm** sur 20. Celui du raccrochage est à **0,556** de la rugosité du **bruit pur**.

> ⭐⭐⭐ **Le raccrochage ne produit pas un champ un peu bruité autour du bon : il produit un champ
> à mi-chemin du hasard, là où la vérité est plate.** Ce qui manque n'est donc pas une meilleure
> **forme** à chercher — quatre tranches l'ont déjà fermé — mais un champ **lisse par
> construction**, là où le lissage actuel ne fait que moyenner du bruit après coup.

⚠⚠ **Un verdict que sa propre mesure contredisait, corrigé avant publication.** J'avais tiré « le
champ de l'oracle est-il lisse ? » d'un `tranche` sur le coût du lissage : celui-ci vaut +0,2 µm
de façon parfaitement consistante, donc le booléen répondait **NON** pendant que la rugosité du
même champ valait **zéro**. `tranche` répond « y a-t-il une différence consistante », jamais
« est-elle grande » : deux nombres publiés côte à côte se contredisaient. Le booléen est supprimé
au profit d'une **comparaison sans seuil** — la rugosité de l'oracle contre celle du raccrochage
et celle du bruit — et un contrôle interdit désormais qu'il revienne.

⚠ **Et un chiffre non apparié dans une conclusion**, corrigé de même : « il reste 19,3 µm » était
une différence de médianes, alors que tout le reste de la famille se juge en **écart apparié**
(−20,1). Les deux sont publiés, le second nommé comme celui qui décide.

⚠ **Une seconde affirmation à moi corrigée par la mesure** : le contrôle de rugosité exigeait
qu'un damier dépasse 1,0 ; la mesure a rendu exactement **1,0**, et le seuil aurait été un nombre
choisi pour que le cas du jour passe. Il est remplacé par un **ordre** — une rampe est plus lisse
qu'un damier, qui est plus lisse que du bruit — qui ne demande aucun seuil.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante, et elle redistribue tout.** Le chantier de la
> lecture vaut **20,1 µm** appariés et il est réel ; mais **18,2 µm de plus sont hors d'atteinte
> le long de la normale**, donc la moitié du coût d'un pas relève de la **direction**, pas du
> volume. Deux chantiers, pas un :
>
> 1. ⭐ **Un champ lisse par construction** — la vérité a une rugosité nulle, notre champ est à
>    mi-chemin du bruit. Le lissage après coup plafonne (tranche précédente) ; ce qu'il faut est
>    une méthode dont le champ est lisse **avant** d'être corrigé, par exemple un ajustement de
>    surface sur les décalages plutôt qu'une médiane de voisinage.
> 2. ⚠ **La direction** — `le_cout_dun_seul_pas` a mesuré que la rotation ne vaut que 3 %, mais
>    avec l'instrument **non apparié** que la rétraction de ce registre a invalidé, et sur une
>    autre population. Ce chiffre est à refaire avant d'en conclure quoi que ce soit.

#### ⛔ TOURNER LE PAS NE REND RIEN — et l'oracle qui semblait le dire n'était pas une borne

> Mesure : `src/nappe/la_direction_du_pas.py` (19 contrôles) →
> `docs/mesures/la_direction_du_pas.json`. Figure :
> `src/figures/figure_la_direction_du_pas.py` (14 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/la_direction_du_pas.py --cote 960 \
>     --json docs/mesures/la_direction_du_pas.json
> uv run python src/figures/figure_la_direction_du_pas.py \
>     --sortie docs/images/75_la_direction_du_pas.png
> ```

Le pas angulaire est **dérivé** — **0,9366°** est la rotation qui déplace le point d'arrivée d'**un
voxel**, exactement comme la grille des décalages — et le cône n'est pas choisi mais **balayé** :
quatre demi-angles emboîtés, sur la même population que le plancher.

![la direction du pas](images/75_la_direction_du_pas.png)

| demi-angle | rotations | oracle par cellule | contre sans rotation | ensemble (hors éch.) | contre sans rotation |
|---:|---:|---:|---|---:|---|
| 0,94° | 1 | 20,0 µm | +0,0 · 0/8 | 20,0 | +0,0 · 3/8 ⛔ |
| 1,87° | 13 | 19,3 | −0,7 · 8/8 · [−0,7 ; −0,6] ✅ | 20,1 | +0,0 · 3/8 ⛔ |
| 3,75° | 49 | 18,4 | −1,4 · 8/8 · [−1,5 ; −1,4] ✅ | 19,9 | −0,1 · 5/8 ✅ |
| 7,49° | 197 | **16,9** | −2,9 · 8/8 · [−3,0 ; −2,9] ✅ | 20,1 | −0,1 · 4/8 ⛔ |

> ⛔ **Une rotation d'ENSEMBLE ne rend rien.** Ajustée **hors échantillon** — chaque pas jugé à
> l'angle que les **autres** pas ont préféré —, elle donne au mieux **−0,1 µm**, et ne prend que
> **3,4 %** de ce que prend l'oracle par cellule. **Le « 3 % » de `le_cout_dun_seul_pas` est
> confirmé**, cette fois avec l'écart apparié et sur huit pas.

⚠ Le verdict « tranche » à 3,75° porte sur **un dixième de micromètre** : `tranche` répond « y
a-t-il une différence consistante », jamais « est-elle grande ». C'est exactement la lecture que la
tranche précédente a dû corriger, et le rapport à l'oracle est publié pour l'empêcher.

##### ⚠⚠⚠ Et le contrôle qui a payé immédiatement : ce n'était pas une borne

> ⚠⚠⚠ **96,6 % des cellules choisissent le BORD du cône.** Ce que l'oracle de direction rend
> n'est donc pas une **borne** mais un **plancher du balayage**. Publier ses 2,9 µm comme « ce que
> la direction vaut » aurait présenté la limite d'une **grille** comme une limite de la
> **matière** — et rien dans les chiffres eux-mêmes ne l'aurait signalé.

Et l'élargir ne le sauverait pas : le **point le plus proche** du nuage se trouve à **33,5°** de
la normale. L'optimum non borné est donc « viser ce qui est le plus près » — or deux surfaces se
correspondent par leur **paramétrage**, jamais par leur proximité.

> ⛔ **L'oracle de direction par cellule est DÉGÉNÉRÉ**, et aucun cône ne le rend légitime. La
> question « de combien une meilleure direction aiderait » n'a donc pas de réponse par cette voie,
> et c'est dit plutôt que remplacé par un nombre qui aurait l'air d'en être une.

##### ⭐ Ce qui reste vrai, et qui pointe ailleurs

Le champ des rotations optimales est **lisse localement** — rugosité **0,0°** pour un pas de
0,9366° — et **étendu à travers la feuille** : **10,3° / 9,37°** d'écart interquartile.

> ⭐⭐ **C'est précisément pourquoi un biais global n'en prend rien** : ce qui aiderait varie
> **lentement d'un bout de la feuille à l'autre**, et un seul angle ne peut pas suivre. Même forme
> que la découverte de la tranche précédente sur les décalages — le champ utile est lisse et non
> constant. ⚠ Et cette lecture est **mesurée**, pas supposée : publier la seule rugosité aurait
> laissé conclure « le champ est constant », qui est la lecture la plus naturelle et la fausse.

⚠ **Une promotion, avec son contrôle** : `recaler_hors_echantillon` devient
`lecart_apparie.choisir_hors_echantillon`, parce qu'un facteur d'échelle sur des décalages et une
rotation d'ensemble sont **le même problème** — choisir un réglage sur les autres cas. Le contrôle
est que l'image publiée de `le_gabarit_lu_ailleurs` sort **identique** après le déplacement.
⚠ Et un contrôle de plus y est ajouté : le réglage est ajusté sur la **médiane** des coûts et non
sur leur somme, ce qui se vérifie par un cas où un dossier bruyant essaierait de décider pour tous.

⚠ **Deux défauts de publication attrapés en chemin** : un champ nommé `angles_retenus` qui
contenait des **indices de grille** — un nombre sans unité qui se lit comme des degrés — et une
phrase affirmant que la distance publiée était « ce qu'une direction libre obtiendrait », alors
que c'est la distance du point d'**arrivée** au nuage, c'est-à-dire l'erreur de ne pas bouger.

> ⭐⭐⭐ **Ce que cette tranche laisse à la suivante.** La direction est **fermée par les deux
> bouts** : un biais global ne rend rien, et l'oracle par cellule n'est pas une question bien
> posée. Il ne reste donc qu'**un** chantier, celui que la tranche précédente avait nommé en
> premier — un champ de décalages **lisse par construction**. Les deux tranches convergent
> dessus : le champ utile, décalage comme rotation, est **lisse localement et étendu
> globalement**, et c'est exactement ce qu'un **ajustement de surface** produit, là où une médiane
> de voisinage ne fait que moyenner du bruit après coup.

#### ⛔⛔ ÊTRE LISSE NE SUFFIT PAS — la lissité du champ vrai était un INDICE, pas une recette

> Mesure : `src/nappe/le_champ_lisse_par_construction.py` (18 contrôles) →
> `docs/mesures/le_champ_lisse_par_construction.json`. Figure :
> `src/figures/figure_le_champ_lisse_par_construction.py` (14 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/le_champ_lisse_par_construction.py --cote 960 \
>     --json docs/mesures/le_champ_lisse_par_construction.json
> uv run python src/figures/figure_le_champ_lisse_par_construction.py \
>     --sortie docs/images/75_le_champ_lisse_par_construction.png
> ```

Une médiane de voisinage est un **ajustement local par une constante**. Ce qui est essayé ici est
un champ dont la lissité est une propriété de sa **forme** : une surface polynomiale de degré 0 à
3 sur toute la grille — qui ne *peut pas* être bruitée, faute de degrés de liberté —, un plan
ajusté localement sur un 9×9, et la composition du voisinage en service avec une surface.

![un champ lisse par construction](images/75_le_champ_lisse_par_construction.png)

| ajustement | paramètres | rugosité | LECTURE | contre le déployé | BRUIT | hors lissage |
|---|---:|---:|---:|---|---:|---:|
| brut | — | 3,48 | 45,3 µm | +4,1 · 3/8 | 60,2 | +1,3 |
| ⭐ **voisinage 3×3** *(déployé)* | — | 0,34 | **36,6** | 0 | 57,0 | 0 |
| surface, degré 0 | 1 | **0,00** | 43,9 | +3,6 · 1/8 | 46,8 | +3,7 |
| surface, degré 1 | 3 | **0,00** | 44,6 | +3,2 · 1/8 | 47,2 | +3,5 |
| surface, degré 2 | 6 | **0,00** | 43,6 | +3,3 · 1/8 | 46,5 | +4,0 |
| surface, degré 3 | 10 | **0,00** | 41,9 | +2,4 · 1/8 | 46,3 | +3,6 |
| plan local (9×9) | — | 0,24 | 40,9 | +1,4 · 2/8 · [1,2 ; 1,6] | 46,8 | +3,7 |
| voisinage puis surface | 3 | **0,00** | 45,1 | +3,4 · 1/8 | 47,5 | +3,7 |

> ⛔ **Aucun ne bat le voisinage en service**, et le meilleur — le plan local — perd de façon
> **consistante** : +1,4 µm, intervalle **entièrement positif** [1,2 ; 1,6].

##### ⭐⭐⭐ Et le panneau B dit pourquoi, ce qu'aucun classement ne montrerait

**À rugosité NULLE on trouve deux choses** : le champ de l'**oracle**, qui rend **20,0 µm**, et
les surfaces ajustées, qui en rendent **41,9 à 44,6**. Les surfaces font donc **exactement ce
qu'on leur demandait** — elles sont parfaitement lisses — et elles marchent plus mal.

> ⭐⭐⭐ **Être lisse était une propriété NÉCESSAIRE du bon champ, jamais une propriété
> SUFFISANTE.** Deux tranches l'avaient prise pour une recette, et c'était une inférence tirée
> d'une corrélation : « le champ vrai est lisse » ne dit pas « rends ton champ lisse ».

⚠⚠ Le témoin le confirme étage par étage : les surfaces améliorent **énormément le bruit** (60,2 →
46,3 µm) et **à peine la lecture** (45,3 → 41,9). Leur part **hors lissage** est **positive
partout** (+3,5 à +4,0 µm) : elles rendent **moins sur la lecture que sur le hasard**.

> ⚠⚠⚠ **Ce que ça corrige** : le champ vrai est plat, mais ce qui distingue une lecture d'un bruit
> est **local et de haute fréquence spatiale**. La médiane 3×3 le garde, une surface globale
> l'écrase **avec** le bruit. Ce que le voisinage réussit n'est donc pas « lisser » — c'est
> **lisser juste assez**.

⚠ Deux propriétés numériques valaient d'être vérifiées plutôt que supposées : un ajustement de
degré trois sur des indices bruts est **mal conditionné** au point de rendre un champ qui oscille,
donc les coordonnées sont normalisées dans [−1, 1] — et le contrôle exige qu'une cubique soit
rendue **exactement**. Et un plan local sur un 3×3 aurait neuf points pour trois paramètres,
c'est-à-dire une interpolation du bruit : la demi-fenêtre est à quatre, soit 81 points.

> ⭐⭐⭐ **Ce que cette tranche laisse, et c'est un état des lieux plutôt qu'une piste.** Cinq
> portes sont fermées sur la lecture — la **forme** cherchée, le **lieu** où on l'apprend, son
> **amplitude**, la **largeur** du lissage, et un champ **lisse par construction** — plus la
> **direction**, fermée par les deux bouts. Il reste **16,6 µm** entre le voisinage en service
> (36,6) et l'oracle (20,0), et **18,2 µm** de plancher sous l'oracle que rien le long de la
> normale ne prend.
>
> ⚠ Ce que la campagne sait maintenant et ne savait pas il y a cinq tranches : le raccrochage
> déployé **gagne SUR UN PAS** (37,5 contre 43,6, 7 pas sur 8 — ⚠ et **perd sur une marche**,
> mesuré le 2026-09-07 : voir *« LA MARCHE »* plus bas), tout son gain vient du **voisinage** et
> non de la corrélation, et l'information qui reste à prendre est **locale**. Ce qui n'a jamais été
> essayé, c'est de faire lire au raccrochage autre chose qu'une **intensité** — la piste que la
> tranche sur le gabarit avait nommée et qu'aucune n'a encore ouverte, parce que le champ de
> fibres publié ne couvre pas ce fragment. ⚠ Vérifier d'abord si `PHerc0500P2` a un préfixe
> `fibers/`, plutôt que de supposer que non.

#### ⛔⛔⛔ LA VOIE DE L'ORIENTATION EST FERMÉE PAR LA DONNÉE — vérifié sur les DEUX serveurs

> Mesure : `src/nappe/ou_vit_le_champ_de_fibres.py` (17 contrôles) →
> `docs/mesures/ou_vit_le_champ_de_fibres.json`. Figure :
> `src/figures/figure_ou_vit_le_champ_de_fibres.py` (14 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/ou_vit_le_champ_de_fibres.py \
>     --json docs/mesures/ou_vit_le_champ_de_fibres.json
> uv run python src/figures/figure_ou_vit_le_champ_de_fibres.py \
>     --sortie docs/images/75_ou_vit_le_champ_de_fibres.png
> ```

⚠⚠ **La consigne était de ne pas se contenter d'un serveur**, et elle était justifiée : ce dépôt
a déjà été mordu **trois fois** pour avoir interrogé **une** vue du corpus et conclu sur **le**
corpus — c'est la raison d'être de `ou_vit_ce_rouleau`. La question « `PHerc0500P2` a-t-il un
champ de fibres ? » est donc posée aux **deux** sources, et le serveur dans ses **deux**
arborescences (`fragments/` et `full-scrolls/<Scroll>/<objet>.volpkg/`).

![où vit le champ de fibres](images/75_ou_vit_le_champ_de_fibres.png)

**46 objets interrogés.** Cinq publient un champ de fibres — `PHerc0139`, `PHerc0332`,
`PHerc1299`, `PHerc1451` et **`PHercParis4`**, qui est le rouleau 1. Un seul publie des
**spires** : `PHerc0500P2`, celui que la campagne déroule.

> ⛔⛔⛔ **L'INTERSECTION EST VIDE.** Un champ d'orientation ne sert à cette campagne que sur un
> objet qui publie **aussi** des spires — c'est sur elles que la marche s'appuie et entre elles
> que l'erreur se mesure. La voie de l'orientation est donc fermée **par la donnée**, pas par la
> méthode, et c'est une porte qu'aucune tranche de mesure ne pouvait ouvrir.

##### ⚠⚠⚠ Et deux défauts de méthode attrapés dans la mesure elle-même

**1. Trente-huit désaccords qui étaient des erreurs d'adresse.** La première version demandait à
**tous** les objets l'adresse `fragments/<objet>/…`, y compris aux rouleaux, qui vivent sous
`full-scrolls/<Scroll>/<objet>.volpkg/`. Elle rapportait donc **38 désaccords sur 38** — un
artefact de construction d'URL présenté comme un fait sur le corpus, c'est-à-dire **exactement le
mode de panne que ce fichier existe pour éviter**, commis à l'intérieur de lui-même.

**2. Une comparaison entre deux étages de l'arbre.** Le relevé annonçait ensuite que « les deux
sources ne partagent aucun mot de vocabulaire » — vrai, et trivial : il comparait les **genres**
du bucket (deux niveaux sous `representations/predictions/`) aux dossiers de **premier niveau** du
serveur. La question posée au même niveau donne un fait utile : **un seul objet** a un dossier
`representations/` sur le serveur, et il n'y a **aucun étage `predictions/`** dessous.

> ⚠ **L'absence de fibres sur le serveur parle donc de son RANGEMENT, pas du corpus** — et c'est
> le bucket qui répond à la question des fibres. Le relevé écrit cette portée dans la mesure
> elle-même : *absent veut dire absent des sources interrogées, jamais inexistant*.

⚠ **Un paramètre mort corrigé au passage**, trouvé en cherchant qui publie des spires :
`les_wraps_publies.wraps_du_fragment(fragment)` **ignorait son argument** et balayait tout l'index
en retenant tout segment nommé `wrapNN`. Sans conséquence aujourd'hui — un seul objet du corpus en
publie, mesuré — mais le jour où un second en publierait, la campagne aurait marché sur les spires
de **deux objets mélangées** sans que rien ne le signale. Un paramètre qui ne fait rien est un
piège qui attend sa donnée ; il filtre désormais, et un contrôle l'épingle.

> ⭐⭐⭐ **Ce que cette tranche laisse.** Les six portes de la lecture sont fermées, et la
> septième — l'orientation — l'est par la **donnée**. Ce qui reste ouvert n'est donc plus une
> idée de méthode mais une question de **matière** : obtenir un champ d'orientation sur
> `PHerc0500P2`, ou des spires sur un objet qui en a un. La seconde est la moins chère des deux —
> `PHercParis4` publie des fibres **et** de l'`ink-3d`, et c'est le rouleau le plus segmenté du
> concours. ⚠ Mais ce serait changer d'objet, donc de campagne : à trancher avec l'auteur plutôt
> qu'à décider ici.

---

#### ⛔⛔⛔ LA MARCHE : le raccrochage déployé porte **MOINS LOIN** que le pas normal seul

> Mesure : `src/nappe/la_portee_du_raccrochage.py` (18 contrôles) →
> `docs/mesures/la_portee_du_raccrochage.json`. Figure :
> `src/figures/figure_la_portee_du_raccrochage.py` (17 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/la_portee_du_raccrochage.py --cote 960 \
>     --json docs/mesures/la_portee_du_raccrochage.json
> uv run python src/figures/figure_la_portee_du_raccrochage.py \
>     --sortie docs/images/75_la_portee_du_raccrochage.png
> ```

⚠⚠⚠ **Pourquoi cette mesure, et pourquoi elle vient maintenant.** Les sept tranches précédentes
mesurent toutes **un pas** : on part d'une spire publiée, on en vise la suivante, on lit l'erreur.
Or le but n'est pas un pas, c'est le **DÉROULEMENT** — et rien, dans une mesure sur un pas, ne dit
ce que la même méthode fait sur huit. La marche ici ne connaît **que sa spire d'ancrage** : à
chaque bras elle repart de sa **propre prédiction**, y recalcule ses normales et y relit son
gabarit. Relire les spires publiées en chemin serait se ré-ancrer à chaque pas, et la portée
mesurerait les ancres au lieu de la marche.

⚠⚠ **Le critère vient de la matière, pas d'un réglage.** Une marche est perdue quand son erreur
dépasse la **demi-feuille** (67,75 µm) : au-delà, le point prédit est plus près de la feuille
**voisine** que de la sienne, et rien en aval ne peut le savoir. Et la portée **s'arrête au
premier échec** — repasser sous le seuil après l'avoir franchi n'est pas rattraper, c'est bâtir
sur une erreur.

![jusqu'où la marche va avant d'être plus près de la mauvaise feuille](images/75_la_portee_du_raccrochage.png)

**Sur 8 bras, ancre = spire 4, `--cote 960`, ~1 800 cellules au départ :**

| marcheur | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | portée |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pas normal seul | 44,0 | 50,1 | 49,5 | 67,2 | 72,2\* | 114,2\* | 1016,5\* | 177,3\* | **4** |
| ⭐ raccrochage déployé | 34,7 | 44,3 | 71,8\* | 120,4\* | 207,2\* | 274,6\* | 1067,2\* | 499,5\* | **2** |
| ⭐ **+ nappe lissée entre deux bras** | 36,6 | 42,8 | 48,9 | 74,4\* | 120,9\* | 160,8\* | 940,7\* | 354,7\* | **3** |
| ⭐⭐⭐ **pas normal + nappe lissée** | 44,4 | 50,0 | 48,8 | 64,8 | **61,2** | 99,8\* | 995,8\* | 160,0\* | **5** |
| ⭐⭐ **état au pas normal, sortie raccrochée** | 34,7 | 52,0 | 56,1 | 66,1 | 79,5\* | 110,6\* | 1015,8\* | 173,2\* | **4** |
| nappe lissée + sortie raccrochée | 34,7 | 50,8 | 57,6 | 64,5 | 81,7\* | 101,2\* | 1002,5\* | 163,7\* | 4 |
| témoin mélangé | 62,4 | 64,9 | 92,6\* | 149,4\* | 267,5\* | 334,2\* | 1141,7\* | 597,5\* | 2 |
| ⛔ la borne | 19,9 | 17,5 | 19,0 | 17,9 | 19,4 | 22,1 | 849,0\* | 105,4\* | **6** |
| *ce que le corpus demande* | *170,0* | *119,5* | *100,6* | *120,0* | *137,6* | *89,2* | ***1000,6*** | *76,7* | *6* |

*\* = au-delà de la demi-feuille. Toutes les valeurs en µm, médianes sur les cellules vivantes.*

> ⛔⛔⛔ **LE VERDICT, ET IL VA CONTRE LA MÉTHODE EN SERVICE.** Le raccrochage déployé traverse
> **2 spires**, le pas normal seul en traverse **4**. Et l'écart apparié bras par bras **tranche
> dans l'autre sens** : le pas normal est à **-52.0 µm** du raccrochage sur **6/8 bras**,
> intervalle **[-53.2, -50.7]** — les trois conditions sans seuil, les trois tenues.

⚠⚠⚠ **Ce que ça RÉTRACTE, et ce que ça ne rétracte pas.** Le gain sur **un** pas reste mesuré et
reste vrai : le raccrochage bat le pas normal aux bras 1 et 2 (34,7 contre 44,0 ; 44,3 contre
50,1), exactement ce que la tranche du critère avait publié. Ce qui est rétracté est
l'**extension** de ce gain à un déroulement, que rien n'avait mesuré et que la campagne tenait
pour acquise. La différence n'est pas un détail de statistique : **l'erreur d'un bras devient la
surface sur laquelle le suivant estime ses normales et relit son gabarit**, donc elle ne s'ajoute
pas, elle se compose. Un décalage de 35 µm au bras 1 fait une normale légèrement fausse au bras 2,
qui fait un gabarit lu de travers au bras 3.

⚠⚠ **Et le raccrochage se compose PLUS VITE que le pas normal**, ce qui est le fait mécanique
derrière le verdict : il **déplace** le point le long de la ligne, donc il déplace aussi la
surface sur laquelle le bras suivant travaille. Un pas normal qui ne fait rien laisse au bras
suivant une surface **régulière quoique décalée** ; un raccrochage qui glisse cellule par cellule
lui laisse une surface **froissée**. Le témoin mélangé, qui glisse au hasard, porte exactement
aussi loin que le raccrochage (2) — et c'est la seconde moitié du diagnostic : sur une marche, ce
qui compte n'est plus *où* on glisse mais *qu'on glisse*.

⚠⚠⚠ **RECTIFIÉ LE JOUR MÊME, et l'erreur était à moi.** J'avais publié que la fenêtre du
raccrochage vaut **±100,6 µm — 1,48 demi-feuille** et conclu qu'un **seul** raccrochage peut poser
la cellule sur la feuille voisine. **Faux** : ±100,6 µm est la demi-largeur de la **LIGNE LUE**,
pas le décalage atteignable. La corrélation consomme la demi-largeur du **gabarit** à chaque bout,
donc le décalage que le raccrochage peut réellement proposer vaut **±67,8 µm — 1,00 demi-feuille
exactement**, mesuré sur les décalages que la corrélation rend et non déduit du code. Le chiffre
publié était **un pouvoir que le raccrochage n'a pas**, et il est remplacé par celui qu'il a. Un
contrôle exige désormais que ce qui est **appliqué** tienne dans ce qui est **annoncé**.

> ⭐⭐ **Et le fait corrigé est meilleur que le faux.** La construction du raccrochage lui interdit
> de traverser une demi-feuille **en un seul mouvement** — ce n'est pas une coïncidence, c'est ce
> que `t_ligne = ±(demi-pas + demi-gabarit)` produit exactement. Le glissement **appliqué** est
> d'ailleurs bien plus petit : **22 · 24 · 19 · 19 · 18 · 16 · 15 · 14 µm** bras par bras (médiane des |t|), soit environ un tiers de
> la borne. Ce qui dérive n'est donc **pas un pas mais leur somme** — huit bras à une vingtaine de
> µm dans le même sens font deux demi-feuilles — et c'est ce qu'on attend d'un glissement guidé par
> une surface de plus en plus froissée. ⚠ La corrélation des signes d'un bras à l'autre n'est pas
> encore mesurée ; l'affirmer serait refaire la faute qu'on vient de corriger.

##### ⭐⭐⭐ LA PRÉMISSE EST MESURÉE, ET LE REMÈDE REPREND PRESQUE TOUT

⚠⚠ **D'abord la prémisse, parce que sans elle « la marche froisse ce qu'elle laisse » est une
histoire.** La rugosité du champ de décalage — de combien une cellule s'écarte de la médiane de son
voisinage — est mesurée bras par bras : **0.34 · 0.57 · 0.81 · 1.48 · 2.01 · 1.95 · 1.79 · 1.84** voxels pour le chemin déployé. Elle **croît**, et
elle triple entre le premier bras et le cinquième. Le pas normal seul la publie à **zéro partout**,
puisqu'il ne glisse pas ; la borne la garde entre 0 et 1, ce qui redit sur une marche ce que la
tranche de l'oracle avait mesuré sur un pas — **le champ qu'une méthode parfaite produirait est
plat**.

⭐⭐⭐ **Ensuite le remède, et il n'ajoute AUCUN réglage.** Sept tranches ont lissé le champ de
**décalage** d'un pas ; ce qu'une marche abîme est la **NAPPE**, et personne n'avait jamais lissé
celle-là entre deux bras. Le cinquième marcheur applique donc à la surface prédite le voisinage
**déjà déployé** sur le champ de décalage : même demi-largeur, même règle de majorité, et une
cellule dont le voisinage ne suffit pas garde sa valeur non lissée — exactement ce que fait le
raccrochage en service.

| comparaison, appariée bras par bras sur les cellules **communes** | écart médian | bras améliorés | intervalle | verdict |
|---|---:|---:|---|---|
| nappe lissée **contre raccrochage** | **-65.9 µm** | 7/8 | [-85.9, -45.9] | ⭐ **elle tranche** |
| nappe lissée **contre pas normal seul** | +3.3 µm | 4/8 | [-0.6, 7.2] | ne tranche **dans aucun sens** |

> ⭐⭐⭐ **Le lissage de la nappe reprend presque tout ce que le raccrochage coûte à une marche.**
> Sa portée passe de **2 à 3**, et face au pas normal seul il revient à **parité** : ni l'un ni
> l'autre ne tranche, l'intervalle chevauchant zéro. ⚠ Ce n'est donc pas encore un gain — c'est la
> récupération d'une perte, obtenue sans un seul paramètre neuf.

⚠⚠ **Et l'appariement a été refait pour que ce chiffre veuille dire quelque chose.** Deux marcheurs
divergent, donc leurs masques divergent : le marcheur lissé garde **841** cellules au dernier bras
là où le raccrochage en garde 864. Comparer les deux médianes publiées serait comparer deux
populations, et une médiane sur moins de cellules n'est pas une médiane meilleure. Chaque écart
apparié est désormais pris sur l'**intersection**, cellule par cellule, et **publie combien de
cellules elle contient**. ⚠ Un contrôle vérifie que l'intersection écarte bien les cellules qu'un
seul des deux a gardées — un contrôle qui ne relirait que les médianes passerait aussi bien avec
deux populations disjointes.

⚠ **Ce que cette mesure-là ne disait PAS** — et la suivante l'a démontré, voir plus bas : le lien
entre la rugosité qui monte et l'erreur qui explose était **plausible et non démontré**. La rugosité publiée
pour le marcheur lissé reste proche de celle du raccrochage (le champ mesuré est le décalage du
**snap**, en amont du lissage), donc ce que le lissage répare est visible dans l'**erreur** et pas
dans ce champ-là. Mesurer la rugosité de la **surface** est un instrument de plus, pas une lecture
de celui-ci.

##### ⭐⭐⭐ SÉPARER L'ÉTAT DE LA SORTIE : le premier marcheur aveugle à battre le pas normal

⚠⚠⚠ **Le raisonnement, et il tient en une phrase.** Sept tranches mesurent qu'un raccrochage gagne
quelques µm sur **un** pas ; la tranche de la marche mesure qu'il en **coûte cinquante** sur huit,
parce que ce qu'il corrige devient la surface où le bras suivant estime ses normales. Les deux
faits tiennent ensemble dès qu'on cesse de **RÉINJECTER** la correction : la marche avance au pas
normal — donc rien ne se compose — et le raccrochage n'est appliqué qu'à ce qui est **PUBLIÉ**.
C'est la séparation ordinaire entre l'**état** d'un système et sa **sortie**, et elle n'ajoute
aucun réglage.

> ⭐⭐⭐ **Il gagne, et il tranche.** Portée **4**, et l'écart apparié au pas normal seul vaut
> **-0.9 µm** sur **5/8 bras**, intervalle **[-1.1, -0.7]** : médiane négative, majorité de bras
> améliorés, intervalle entièrement négatif. C'est le **premier marcheur aveugle** de toute la
> campagne à battre le pas normal **sur une marche**.

⚠⚠ **Et il démontre le mécanisme que la tranche précédente disait plausible.** Le **MÊME**
raccrochage, lu sur la surface lisse du pas normal, produit un champ de décalage **lisse**
(0.34 · 0.46 · 0.56 · 0.71 · 0.92) là où, lu sur sa propre prédiction, il en produit un **rugueux** (0.34 · 0.57 · 0.81 · 1.48 · 2.01). La rugosité du champ
n'est donc **pas une propriété du raccrochage** : elle est **HÉRITÉE** de la surface sur laquelle
il lit. Le contrôle porte sur la comparaison des deux séries, pas sur un seuil.

⚠ **Ce que ça ne fait pas, et il faut le dire.** La portée reste à **4** : le bras 5 échoue
toujours, à 79,5 µm pour un seuil de 67,75. Le pas normal seul y lit 72,2, donc il manquait
**4,5 µm** et ce marcheur en gagne **0,9**. Le gain est **constant** — c'est ce que l'intervalle
dit — mais il est **cinq fois trop petit** pour sauver un bras. Un gain qui tranche et une portée
qui bouge sont deux choses différentes, et publier la première en laissant croire la seconde
serait la faute que ce registre corrige en boucle.

> ⭐⭐ **L'état des lieux de la marche, après trois marcheurs neufs.** Le corpus autorise **6** bras
> et la borne les prend tous. Le pas normal seul en fait **4**, le raccrochage déployé **2**, le
> lissage de la nappe **3**, et la séparation état/sortie **4 avec un gain qui tranche**. Ce qui
> reste entre 4 et 6 n'est donc plus une question de *lecture* — les sept portes de la lecture sont
> fermées et la borne, qui lit parfaitement, ne fait pas mieux que 6 non plus. C'est une question
> de **propagation** : ce que la marche transporte d'un bras au suivant.

##### ⭐⭐⭐ ET C'EST LA PROPAGATION : lisser la NAPPE achète un bras, sans un réglage de plus

⚠⚠⚠ **L'instrument manquait, et il manquait depuis le début.** La rugosité déjà instrumentée
porte sur le champ de **DÉCALAGE** — un scalaire le long de la normale. Elle ne dit **rien** de la
surface, qui est pourtant ce sur quoi le bras suivant estime ses normales.
`la_lissite_de_la_feuille.rugosite_de_la_nappe` mesure la seconde : de combien un point s'écarte
de la médiane de ses voisins, en µm, avec le voisinage **déployé**. Elle est nulle sur un plan
**et sur une pente** — une inclinaison n'est pas un froissement — et l'ordre plan < ondulation <
bruit tient sans qu'aucun seuil soit choisi.

> ⚠⚠ **Deux angles morts, écrits plutôt que découverts plus tard.** Un **damier de période deux**
> lui est invisible : dans un 3×3, la valeur du centre est en majorité (cinq contre quatre), donc
> la médiane rend le centre. Et une **pointe isolée** l'est aussi : une médiane prise sur toutes
> les cellules ne bouge pas pour une seule aberrante. Ce nombre répond à *« la nappe est-elle
> froissée »*, jamais à *« y a-t-il une cellule aberrante »* — confondre les deux ferait lire un
> zéro comme une garantie qu'il ne donne pas.

⚠⚠⚠ **Et il contredit ce que la tranche précédente laissait croire.** Le pas normal seul a un
champ de décalage **identiquement nul** — il ne glisse jamais — et sa **nappe se froisse quand
même** : **0.0 · 0.0 · 0.3 · 1.2 · 2.8 · 5.1 · 9.9 · 19.9** µm bras par bras. Elle se froisse par les **NORMALES**, estimées sur une surface
déjà fausse. « Il ne glisse pas donc rien ne se compose » était une conclusion tirée de la
**mauvaise grandeur**, et un contrôle l'épingle désormais.

⭐⭐⭐ **Le remède suit du diagnostic, et il n'ajoute AUCUN réglage** : le pas normal seul, avec le
voisinage **déjà déployé** appliqué à la **NAPPE** entre deux bras. Sa nappe reste à **0.0 · 0.0 · 0.0 · 0.0 · 0.0 · 0.0 · 0.1 · 1.9** µm.

| marcheur | portée | écart apparié au pas normal seul | verdict |
|---|---:|---|---|
| ⭐⭐⭐ **pas normal + nappe lissée** | **5** | **-6.7 µm · 7/8 bras · [-11.0, -2.4]** | ⭐ **il tranche** |
| nappe lissée + sortie raccrochée | 4 | -6.0 µm · 5/8 bras · [-9.3, -2.7] | il tranche |

> ⭐⭐⭐ **CINQ des SIX bras que le corpus autorise**, contre 4 sans lissage, par un marcheur qui
> **ne contient aucun raccrochage du tout**. C'est le meilleur marcheur aveugle de la campagne, et
> il est plus **simple** que celui qui tourne.
>
> ⚠⚠⚠ **PORTÉE DE CE TITRE, mesurée le jour même sur CINQ ancres** : le **gain apparié** tient
> partout, le **bras gagné** non. Voir *« Le verdict tient-il depuis une autre ancre ? »*.

⚠⚠ **La borne dit la dernière moitié du mécanisme.** Sa nappe se froisse aussi — **0.0 · 0.5 · 2.7 · 5.9 · 10.7 · 18.1 · 51.3 · 114.1** µm — et
son erreur reste **plate** (17 à 22 µm sur six bras). Elle ne subit jamais ce qu'elle laisse,
parce qu'elle se raccroche à la **vraie spire** à chaque bras. Ce qu'un marcheur aveugle paie
n'est donc pas d'avoir une nappe froissée : c'est de **devoir repartir de la sienne**.

⚠ **Et ajouter la sortie raccrochée par-dessus fait PERDRE le bras** (portée 4 contre 5) : au bras
5 la sortie raccrochée lit 81,7 µm là où la nappe lissée seule en lit 61,2. Le raccrochage lu sur
une surface propre reste moins bon que la prédiction de cette surface. C'est mesuré, contraire à
l'intuition, et publié tel quel.

##### ⚠⚠⚠ LE VERDICT TIENT-IL DEPUIS UNE AUTRE ANCRE ? Le GAIN oui, le BRAS non

> Mesure : `src/nappe/la_portee_tient_elle_ailleurs.py` (12 contrôles) →
> `docs/mesures/la_portee_tient_elle_ailleurs.json`. Figure :
> `src/figures/figure_la_portee_tient_elle_ailleurs.py` (10 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/la_portee_tient_elle_ailleurs.py --cote 960 --ancres 5 \
>     --json docs/mesures/la_portee_tient_elle_ailleurs.json
> uv run python src/figures/figure_la_portee_tient_elle_ailleurs.py \
>     --sortie docs/images/75_la_portee_tient_elle_ailleurs.png
> ```

⚠⚠⚠ **Pourquoi cette mesure, et elle vient d'une faute déjà payée.** Le titre précédent est tiré
d'**une seule** marche, depuis **une seule** ancre. Or ce registre a déjà vu trois verdicts
s'inverser en changeant la population — passer de 7 à 6 pas déplaçait l'erreur du chemin déployé
de 36,0 à 48,5 µm — et c'est cette découverte qui a produit `lecart_apparie`. Un verdict tiré
d'une population est une **hypothèse** sur les autres tant que les autres n'ont pas été regardées.

![le verdict tient-il depuis une autre ancre](images/75_la_portee_tient_elle_ailleurs.png)

⚠⚠ **Les ancres ne sont PAS comparables entre elles, donc rien n'est moyenné.** Une ancre plus
haute a moins de bras devant elle et rencontre d'autres spires ; agréger leurs portées ferait la
moyenne de choses différentes. Ce qui s'agrège est le **COMPTE** des ancres où le signe tient, ce
qui est un fait sur la **robustesse** et non sur la matière.

> ⭐⭐⭐ **LE GAIN TIENT PARTOUT.** L'écart apparié du marcheur lissé au pas normal seul est
> **négatif aux 5 ancres sur 5** — -6.7, -3.1, -5.9, -5.6, -8.6 µm — avec la majorité des bras améliorée à chaque fois
> (7/8, 7/8, 7/7, 5/6, 4/5). Le gain de la nappe lissée n'est donc **pas** une propriété de l'ancre où il a été trouvé.

> ⚠⚠⚠ **MAIS LE BRAS GAGNÉ, NON : une ancre sur cinq.** Portées, référence → candidat :
> 4 : 4 → 5 | 5 : 2 → 2 | 6 : 3 → 3 | 7 : 2 → 2 | 8 : 1 → 1. Un gain de six micromètres est **constant et fin** ; un bras gagné demande que l'erreur
> passe **SOUS** le seuil de la demi-feuille, ce qui n'arrive que là où elle en était déjà
> proche — à l'ancre 4, le pas normal seul lisait 72,2 µm pour un seuil de 67,75. **Publier le
> second à la place du premier ferait passer la chance d'une ancre pour une propriété de la
> méthode**, et un contrôle exige désormais que les deux comptes soient publiés séparément.

⚠⚠ **Et la colonne du corpus tombe avec l'ancre** (6, 5, 4, 3, 2) : plus on part haut, moins il reste de bras
que le corpus demande au pas nominal avant son trou. Les portées courtes des ancres hautes ne sont
donc **pas un échec de méthode** — c'est la matière qui s'arrête, et un contrôle vérifie qu'aucune
portée ne dépasse ce que le corpus autorise à son ancre.

> ⭐⭐ **Ce que la campagne peut dire, maintenant, sans surinterpréter.** Lisser la nappe entre deux
> bras avec le voisinage **déjà déployé** rend **entre 3 et 9 µm** sur une marche, de façon
> **constante** et sur **toutes** les ancres essayées, et ne coûte **aucun réglage**. Que ça
> traduise en spires supplémentaires dépend de la marge que l'ancre avait, ce qui est une
> propriété de la **matière** à cet endroit et pas de la méthode.




##### ⚠⚠ UNE GARDE QUI N'EST PAS ATTEIGNABLE NE GARDE RIEN — trois batteries retrouvées

> Garde : `src/depot/batteries_enregistrees.py` (9 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/depot/batteries_enregistrees.py
> ```

⚠⚠⚠ **Le défaut n'était pas l'absence de garde.** `temoins.sh` la porte déjà : il balaie
`src/*/*.py`, retient ceux qui déclarent `--verifier`, et signale ceux qu'aucune de ses lignes ne
lance. Le problème est qu'elle **n'est atteignable qu'en run COMPLET** — or le run complet prend
trop longtemps pour tourner à chaque tranche, et la consigne permanente est de ne lancer que les
batteries touchées. **Une garde qu'on ne peut pas se permettre de faire tourner est une garde qui
ne garde rien.**

⭐ Ce qui l'a révélé : `la_cellule_sait_elle_quelle_a_tort` a vécu **deux tranches** sans être
enregistrée, parce qu'un patch d'édition avait échoué en silence. Elle était verte à chaque fois
qu'on la lançait à la main, et n'était jamais lancée autrement.

**Ce que la garde a trouvé en une seconde :**

| trouvaille | ce que c'était |
|---|---|
| `la_cellule_sait_elle_quelle_a_tort` | oubliée depuis deux tranches |
| `combien_de_fenetres` | oubliée le jour même |
| ⭐ **`suivre_nappe`** (45 contrôles) | oubliée **depuis toujours** |
| ⭐ **`assembler_mosaique`** (21 contrôles) | oubliée **depuis toujours** |
| `src/famille/x.py` | ⚠ **faux positif de MA garde** : un chemin d'exemple dans un **commentaire** |

⚠⚠ **Et la vraie cause des deux dernières est une leçon en soi.** Elles passaient, mais disaient
« tous les témoins passent » au lieu du `ALL PASS (0 failures, N checks)` que `run()` exige. Une
batterie qui passe **sans savoir le dire dans le format du dépôt** ne peut pas être comptée — donc
personne ne l'enregistre, donc elle disparaît. Les deux parlent désormais la convention, et
apportent **66 contrôles** que le dépôt n'avait jamais comptés.

⚠ **Le faux positif est gardé dans le fichier**, parce qu'il dit quelque chose : ma première
version lisait tout `temoins.sh` et accusait un chemin d'exemple écrit dans un commentaire qui
explique justement un motif de recherche. **Une garde qui accuse un commentaire est une garde
qu'on apprend à ignorer** — elle ne lit plus que les lignes `run`.

---
##### ⛔⛔⛔ COMBIEN DE FENÊTRES POUR QUE LA CARTE DES TREIZE DÉCIDE ? — 315× le budget actuel

> Mesure : `src/commun/combien_de_fenetres.py` (19 contrôles) →
> `docs/mesures/combien_de_fenetres.json`. Figure :
> `src/figures/figure_combien_de_fenetres.py` (11 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/commun/combien_de_fenetres.py \
>     --json docs/mesures/combien_de_fenetres.json
> uv run python src/figures/figure_combien_de_fenetres.py \
>     --sortie docs/images/75_combien_de_fenetres.png
> ```

⚠⚠⚠ **Pourquoi cette mesure vient AVANT la campagne de septembre.** [`31`](31_roadmap.md) §10
inscrit *« mesurer la part comprimée rouleau par rouleau, à 50 fenêtres minimum »* et dit que
c'est ce qui décide **sur lequel des treize** dépenser six mois. [`33`](33_la_carte_nest_pas_resolue.md)
a déjà montré qu'aux effectifs actuels la carte ne sépare **rien**. Restait la question qui
précède la campagne : **à quel effectif la question deviendrait-elle décidable ?** Une campagne
lancée sans ce chiffre est une campagne dont on ne sait pas si elle peut conclure.

![combien de fenêtres pour que la carte décide](images/75_combien_de_fenetres.png)

⚠⚠ **Et 50 est le chiffre de la MAUVAISE question.** Séparer un rouleau du **témoin** — « ce
rouleau a-t-il plus de zones comprimées que celui qui n'en a pas ? » — n'est pas la décision.
La décision est **quel rouleau attaquer**, donc séparer les rouleaux **entre eux** : deux
estimations incertaines au lieu d'une contre un quasi-zéro, ce qui est strictement plus dur.

| fenêtres par rouleau | paires séparées, nominal | après Holm |
|---:|---:|---:|
| 25 | 0 | 0 |
| 50 | 1 | 0 |
| 100 | 15 | 0 |
| 200 | 31 | 13 |
| 400 | 47 | 29 |

> ⛔ **À 50 fenêtres — le chiffre du calendrier — on sépare UNE paire sur 78 au seuil nominal, et
> ZÉRO après correction de Holm.** Et la correction n'est pas un raffinement optionnel : 78
> comparaisons au seuil de 5 % produisent des « significatifs » par pur hasard, et ce registre a
> déjà eu à retirer un classement pour cette raison exacte.

##### ⭐⭐⭐ La paire qui DÉCIDE est la plus chère de toutes, et c'est structurel

Choisir où dépenser six mois demande de séparer les **deux mieux classés** — donc les deux dont
les parts sont les plus **proches**.

| | |
|---|---|
| la paire | **PHerc0358** (3.6 %) contre **PHerc0211** (5.0 %) |
| écart | **1.4 %** |
| puissance à 50 fenêtres | **0.8 %** |
| effectif exact nécessaire, après Holm | **> 400** (puissance plafonnée à 0.5 %) |
| ⭐ borne **BASSE** sur l'effectif | **7277 fenêtres par rouleau** |
| soit, pour les treize | **94601 fenêtres** — **315.3×** le budget actuel de 300 |

⚠ **La borne est BASSE et le sens de l'erreur est ce qui la rend utilisable** : elle vient de
l'approximation normale, qui **surestime la puissance** sur des parts de quelques pour-cent —
`incertitude_carte` l'écrit déjà — donc elle **sous-estime l'effectif**. Le vrai coût est plus
grand que 315×.

##### ⚠⚠ Et le calendrier sous-finance même la question facile

| rouleau | part | contre le témoin, nominal | après Holm |
|---|---:|---:|---:|
| PHerc0358 | 3.6 % | 400 | 400 |
| PHerc0211 | 5.0 % | 200 | 400 |
| PHerc1447 | 5.6 % | 200 | 400 |
| PHerc0268 | 8.6 % | 100 | 200 |

Séparer le mieux classé du témoin demande **400 fenêtres** après correction, là où le calendrier
en inscrit **50**. **Les deux questions sont sous-financées, et celle qui décide l'est de deux
ordres de grandeur.**

> ⛔⛔⛔ **CE QUE ÇA CHANGE POUR LA ROADMAP.** L'item de septembre de [`31`](31_roadmap.md) —
> *« mesurer la part comprimée rouleau par rouleau »* — n'est pas seulement à lancer : **son
> critère de décision n'est pas mesurable à ce prix**. Il faut soit un **autre critère de choix
> de rouleau**, soit accepter de choisir autrement et le dire. ⚠ Et ça ne dit **pas** que le prix
> est hors de portée : ça dit qu'une procédure de décision proposée ne tient pas, ce qui coûte
> infiniment moins cher à apprendre maintenant que six mois passés sur le mauvais rouleau.

---
##### ⛔⛔⛔ ET LA RÉPONSE DE CE CRITÈRE N'EST MÊME PAS EXÉCUTABLE — 0 rang de spire sur 13

> Mesure : `src/depot/les_spires_consecutives_publiees.py` (30 contrôles) →
> `docs/mesures/les_spires_consecutives_publiees.json`. Figure :
> `src/figures/figure_les_spires_consecutives.py` (13 contrôles), le 2026-09-08.
> Document : [`81`](81_le_rouleau_designe_ne_publie_rien.md).
>
> ```bash
> uv run python src/depot/les_spires_consecutives_publiees.py \
>     --json docs/mesures/les_spires_consecutives_publiees.json
> uv run python src/figures/figure_les_spires_consecutives.py \
>     --sortie docs/images/81_les_spires_consecutives.png
> uv run python src/depot/ce_que_les_serveurs_publient.py --fragment PHerc0358
> ```

⚠⚠⚠ **La tranche précédente disait « trop cher » ; celle-ci dit « pas exécutable », et c'est
gratuit.** Avant de payer 315× pour départager les treize, il fallait demander sur lequel on
aurait de quoi vérifier quoi que ce soit. **Onze des treize ne publient aucun segment. Les treize,
sans exception, ne publient aucun rang de spire.** Le classement de [`16`](16_carte_difficulte_rouleaux_du_prix.md)
désigne donc un objet sur lequel il n'existe **ni ancre pour partir, ni vérité de terrain pour
dire jusqu'où on est allé**.

![sur quel objet peut-on vérifier trente et une spires](images/81_les_spires_consecutives.png)

⭐⭐ **Le critère qui reste est celui de l'OBJECTIF, pas celui de l'encre** : le nombre de spires
**consécutives** publiées, parce qu'une portée est un nombre de spires traversées avant que
l'erreur dépasse la demi-feuille — et qu'au-delà du dernier rang publié d'affilée, il n'existe plus
rien contre quoi dire qu'on a franchi une spire de plus.

| objet | segments | rangs | plus longue suite | porte les 31 ? |
|---|---:|---:|---:|:--:|
| `PHercParis4` | 81 | 120 | **120** (w010..w129, 0 trou) | ✅ |
| `PHerc0172` | 53 | 44 | **44** (w052..w095) | ✅ |
| `PHerc0139` — le **témoin** de la carte | 38 | 37 | **37** (w023..w059) | ✅ |
| `PHerc1667` — l'objet des **775 h** | 20 | 19 | 14 (12 trous) | ⛔ |
| **`PHerc0500P2`** — l'objet **courant** | 39 | 13 | **13** | ⛔ |
| `PHercMANBp` | 11 | 9 | 9 | ⛔ |
| **les treize du prix** | 0 ×11, 6, 15 | **0** | **0** | — |

⚠⚠ **Segments et rangs sont deux comptes différents, et c'est le second qui décide.**
`PHerc0800` (6) et `PHerc1447` (15) ne publient que des `auto_grown_*`, **sans rang de spire** :
on ne peut pas les mettre en spirale sans les remesurer, et « les remesurer » est exactement le
travail qu'un corpus publié existe pour éviter.

⚠ **Confronté aux serveurs, pas lu du cache seul** — l'angle mort déjà payé cinq fois. S3 confirme
l'absence de dossier `segments/` pour `PHerc0358`, `PHerc0211`, `PHerc0125` ; un seul écart trouvé
(`PHerc1447` : 15 en cache, 16 sur S3), sans effet sur le verdict.

⚠⚠ **Deux erreurs à moi, gardées par des contrôles nommés.** (1) J'ai d'abord lu `w046-052` comme
un **rang** au lieu d'un **intervalle** : `PHercParis4` sortait à 28 spires et **91 trous**, donc
le pire du tableau au lieu du meilleur — sonde, sa suite tombe de **120 à 1**. (2) Mon filtre
« géométrie » ne retenait que `tifxyz` et publiait `PHerc0172` à **une** spire marchable sur 44 —
une limite de mon filtre présentée comme une limite du corpus, le péché n° 1 du dépôt ; corrigé en
lisant `deux_aplatissements`, qui avait déjà établi que `tifxyz-transformed` porte une position 3D
par cellule.

##### ⚠⚠⚠ ET UN TROU GÉOMÉTRIQUE AU MILIEU D'UNE NUMÉROTATION CONTINUE — la limite du critère

⚠⚠⚠ **J'ai failli publier une coïncidence comme un recoupement.** Le majorant dérivé du corpus
(une suite de $N$ spires majore la portée mesurable à $N-1$, l'ancre étant la spire la plus basse
de la boîte) donne **12** pour `PHerc0500P2` ; `la_portee_du_raccrochage` publie *« ce que le
corpus autorise : 6 »*, et j'ai d'abord écrit que ce 6 était $13/2$, la portée d'une ancre
centrale. **Vérifié dans la mesure, c'est faux** — l'ancre n'est pas centrale (c'est la spire 4,
la plus basse de la boîte), les bras montent seulement, et il y en a huit.

Le 6 vient d'ailleurs, et de bien plus instructif :

| bras | de → vers | écart mesuré | au pas nominal ? |
|---:|---|---:|:--:|
| 6 | 9 → 10 | 89,2 µm | ✅ |
| **7** | **10 → 11** | **1000,6 µm** | ⛔ |
| 8 | 11 → 12 | 76,7 µm | ✅ |

⭐⭐⭐ **Les spires 10 et 11 se suivent par leur NUMÉRO et sont à 7,4 feuilles l'une de l'autre dans
la matière.** Le plafond de 6 n'est ni la méthode, ni la longueur du corpus : c'est un **trou
géométrique** au milieu d'une numérotation continue.

⚠⚠ **Donc compter les rangs publiés est NÉCESSAIRE et NON SUFFISANT.** Un corpus de 120 spires
numérotées peut porter le même saut, et le compte des noms ne le verra pas. Vérifier que deux
voisines par leur nom le sont dans la matière coûte un téléchargement — c'est ce que
`les_wraps_publies` fait pour `PHerc0500P2`, et ce qui reste à faire pour tout objet retenu.

⚠ La leçon de méthode : **un chiffre qui tombe juste n'est pas un recoupement.** Deux routes qui
rendent 6 pour deux raisons sans rapport se lisent comme une confirmation, et c'est la forme de
faux verdict la plus difficile à voir — celle qu'on n'a aucune raison d'aller vérifier.

> ⛔⛔⛔ **CE QUE ÇA CHANGE POUR L'OBJET COURANT.** `PHerc0500P2` publie **13** spires consécutives
> là où le prix en demande **31**. Sur lui, tenir 31 spires n'est pas seulement difficile : c'est
> **INVÉRIFIABLE**, faute de quoi que ce soit à comparer au-delà de la treizième. C'est la forme
> mesurée du facteur 97×, et elle dit que ce facteur **ne se réduira pas par du travail sur cet
> objet-là**. Trois objets portent les 31 : `PHercParis4` (120), `PHerc0172` (44), `PHerc0139`
> (37).
>
> ⚠ **Le changement d'objet reste une décision de l'auteur.** Ce registre lui donne le chiffre,
> pas le choix, et nomme les deux coûts : tout ce qui est calibré sur `PHerc0500P2` (voxel
> 2,215 µm, pas nominal 135,5 µm, boîte et ancres) est à re-dériver, et la **demi-feuille de
> 67,75 µm est une mesure DE CET OBJET**, donc à remesurer avant d'être réutilisée comme critère
> ailleurs.

---
##### ⛔⛔⛔ LA BORNE QU'ON PUBLIAIT ÉTAIT LE MUR — l'oracle est censuré sur 5/5 ancres

> Mesure : `src/nappe/le_mur_du_corpus.py` (18 contrôles, hors ligne) →
> `docs/mesures/le_mur_du_corpus.json`. Figure : `src/figures/figure_le_mur_du_corpus.py`
> (10 contrôles), le 2026-09-08. Document : [`82`](82_la_borne_etait_le_mur.md).
>
> ```bash
> uv run python src/nappe/le_mur_du_corpus.py --json docs/mesures/le_mur_du_corpus.json
> uv run python src/figures/figure_le_mur_du_corpus.py \
>     --sortie docs/images/82_le_mur_du_corpus.png
> ```

⚠⚠⚠ **`la_portee_du_raccrochage` publie côte à côte « la borne (oracle) : 6 » et « ce que le
corpus autorise : 6 », et personne n'avait demandé si les deux 6 sont le même 6.** Ils le sont, et
sur les **cinq** ancres : 6/6, 5/5, 4/4, 3/3, 2/2. Une portée égale au plafond du corpus est une
observation **censurée à droite** — elle dit « au moins », jamais « vaut ».

![la portée mesure-t-elle le marcheur, ou le mur du corpus](images/82_le_mur_du_corpus.png)

| ancre | bras offerts | plafond du corpus | oracle | pouvoir de séparer |
|---:|---:|---:|---:|---:|
| 4 | 8 | **6** | **≥6** | 4 |
| 5 | 8 | **5** | **≥5** | 3 |
| 6 | 7 | **4** | **≥4** | 2 |
| 7 | 6 | **3** | **≥3** | **1** |
| 8 | 5 | **2** | **≥2** | **1** |

⭐⭐⭐ **La cause est unique, et c'est le trou trouvé par accident dans la tranche précédente** :
les spires **10 et 11** se suivent par leur numéro et sont à **1000,6 µm** l'une de l'autre, soit
865,1 µm de plus que le pas nominal — quand le décalage que cette famille sait appliquer vaut
**±67,8 µm**, une demi-feuille. Le bras 7 demande donc **12,8×** ce que le meilleur d'entre eux
peut atteindre. **Ce n'est pas un échec de méthode, c'est une impossibilité de construction**, et
l'oracle est dedans : il regarde la cible mais *garde la longueur de son pas*.

⚠⚠ **Les cinq ancres ne sont donc pas cinq réplications** : leurs plafonds valent exactement
`10 − ancre`. « Le signe tient sur 5/5 ancres » compte cinq fois un seul défaut du corpus.
⛔ Et **deux d'entre elles ne séparent rien** : à l'ancre 7 les sept marcheurs aveugles rendent
tous **2**, à l'ancre 8 tous **1**. Une ancre de plafond 2 offre trois valeurs dont une censurée ;
les compter comme des confirmations, c'est **compter du silence**.

> ★★ **CE QUI TIENT, ET IL FAUT LE DIRE AUSSI.** À l'ancre 4 le plafond vaut 6, quatre valeurs
> distinctes sortent, et le pas normal (4) comme sa version lissée (5) sont **sous** le plafond :
> cette comparaison-là mesure bien les marcheurs, et **le gain d'un bras par le lissage n'est pas
> touché**. Ce qui tombe est la **borne**, pas le résultat.
>
> ⚠ Ce qui tombe aussi : la lecture « il ne reste qu'un bras de marge avant la borne ». La marge
> réelle est **inconnue** — elle pourrait être bien plus grande, ce qui serait une **bonne
> nouvelle pour l'objectif** — et la mesurer demande un corpus sans ce trou.

---
##### ⛔⛔ ET DÉPLACER LA BOÎTE N'Y CHANGE PRESQUE RIEN — 8 au mieux, sur 1296 placements

> Mesure : `src/nappe/ou_poser_la_boite.py` (20 contrôles) →
> `docs/mesures/ou_poser_la_boite.json`. Figure : `src/figures/figure_ou_poser_la_boite.py`
> (10 contrôles), le 2026-09-08. Document : [`83`](83_le_corpus_et_non_la_boite.md).
>
> ```bash
> uv run python src/nappe/ou_poser_la_boite.py --cote 960 \
>     --json docs/mesures/ou_poser_la_boite.json
> uv run python src/figures/figure_ou_poser_la_boite.py \
>     --sortie docs/images/83_ou_poser_la_boite.png
> ```

![existe-t-il une boîte où la portée cesse d'être censurée](images/83_ou_poser_la_boite.png)

| plafond atteint | 0 | 1 | 2 | 3 | 4 | 5 | **6** | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| placements | **597** | 217 | 101 | 44 | 110 | 50 | **161** | 11 | 5 |

⭐⭐ **Le plafond n'est pas un défaut de placement.** Aucun des 1296 placements ne dépasse **8**,
alors que douze spires sont présentes dans les meilleurs. Ce n'est pas la boîte qui manque de
matière, c'est le corpus qui ne présente pas une spirale au pas nominal.
★★ Ce que le déplacement achète quand même : **+2 bras de dynamique**, sans changer d'objet
(centre `8655 10820 21924` au lieu de `10615 10571 19831`) — pas une marche meilleure, une **mesure
capable de juger deux bras plus loin**.

⚠⚠ **Le corpus échoue dans les DEUX sens** : sur 8589 bras, **3395 hors du pas nominal (40 %)** —
**2226 trop loin** (un trou de numérotation) et **1169 trop près** (deux spires que la boîte ne
sépare pas). ⭐⭐⭐ Et **la même paire ne demande pas la même chose partout** : sur les **12 paires
de rangs voisins**, l'écart médian varie d'un facteur **2,6 à 63,1**, et **huit** de plus de dix —
`10→11` de **19,4 à 1224,8 µm** (**×63,1**), `8→9` ×22,3, `4→5` ×18,9, jusqu'à `2→3` à ×2,6.

⚠⚠⚠ **J'avais d'abord écrit « aucune paire ne varie de moins d'un facteur dix », et ma propre
batterie l'a démenti en une exécution** : `2→3` varie de ×2,6, et le compte mélangeait les paires à
**saut de rang**, qui n'existent que dans les boîtes où une spire intermédiaire est trop pauvre —
donc décrivent une population de boîtes et non l'écart entre deux feuilles voisines. Le drapeau
`consecutif` est désormais publié par la mesure.

⚠⚠⚠ **Le maximum dépend du treillis, donc il est publié comme un MINORANT** : au pas 480 il sort à
7, au pas 240 à 8. Un treillis plus grossier ne peut que **rater** un bon placement, jamais en
inventer un. ⚠ **Et ce piège s'est refermé pendant l'écriture** : `--pas` prenait un scalaire avec
son propre défaut, donc le balayage de treillis n'était **atteignable par aucune ligne de
commande**, et le premier run publié annonçait un minorant qu'il n'avait pas mesuré. Le défaut est
désormais **lu sur la fonction**, et un contrôle le vérifie.

⚠ Et une garde de ce dépôt a attrapé ma propre faute en une seconde : `ou_poser_la_boite` est
parti dans le commit précédent sans être enregistré dans `temoins.sh`, et
`batteries_enregistrees` — écrite la veille pour exactement ça — l'a nommée aussitôt.

---
##### ⭐⭐⭐ LA VÉRITÉ DE TERRAIN DU GOULOT EXISTE SUR UN OBJET, ET UN SEUL — 92 contre 0

> Mesure : `src/depot/une_surface_combien_de_spires.py` (20 contrôles, hors ligne) →
> `docs/mesures/une_surface_combien_de_spires.json`. Figure :
> `src/figures/figure_une_surface_combien_de_spires.py` (12 contrôles), le 2026-09-08.
> Document : [`84`](84_une_surface_combien_de_spires.md).
>
> ```bash
> uv run python src/depot/une_surface_combien_de_spires.py \
>     --json docs/mesures/une_surface_combien_de_spires.json
> uv run python src/figures/figure_une_surface_combien_de_spires.py \
>     --sortie docs/images/84_une_surface_combien_de_spires.png
> ```

⚠⚠⚠ **Une surface publiée qui ne couvre qu'UNE spire ne contient AUCUN transfert de spire à
spire** — elle dit où sont les feuilles, jamais comment on passe de l'une à l'autre. Or c'est
exactement le goulot de l'objectif. Mesuré sur l'index, sans un téléchargement :

![combien de spires une seule surface traverse-t-elle](images/84_une_surface_combien_de_spires.png)

| objet | bandes | spires | spires/surface | la + longue | **franchissements dans une maille** |
|---|---:|---:|---:|---:|---:|
| **`PHercParis4`** | 28 | 120 | **4,29** | **18** | **92** |
| `PHerc0172` | 44 | 44 | 1,0 | 1 | **0** |
| `PHerc0139` | 37 | 37 | 1,0 | 1 | **0** |
| `PHerc1667` | 19 | 19 | 1,0 | 1 | **0** |
| `PHerc0500P2` | 13 | 13 | 1,0 | 1 | **0** |
| `PHercMANBp` | 9 | 9 | 1,0 | 1 | **0** |

⭐⭐ **Et la longueur des bandes décroît sans une seule inversion** — `18 10 8 7 6 5 5 4 4 4 4 4 3
3 3 3 3 3 3 3 3 2 2 2 2 2 2 2` — en pavant `w010..w129` **sans un trou**. Une bande est ce qu'une
passe humaine a produit d'un coup : c'est la **courbe de coût du déroulage manuel**, lue sans rien
mesurer soi-même. ⚠ Le **sens** du rang, lui, n'est pas établi : la circonférence croît vers
l'extérieur, ce qui expliquerait la décroissance, mais le trancher demande un rayon donc un
`tifxyz`.

⚠⚠⚠ **Même la meilleure bande reste sous le compte du prix : 18 contre 31.** Le corpus le plus
riche du concours ne contient pas une marche entière ; il contient dix-sept franchissements
d'affilée, puis il faut **recoudre 28 bandes** — le même problème une spire plus loin.

> ⭐⭐ **CE QUE ÇA DÉBLOQUE.** C'est la première fois que la **portée** de ce dépôt peut se situer
> contre du **travail humain publié** plutôt que contre une borne censurée par le corpus
> ([`82`](82_la_borne_etait_le_mur.md)) : une portée de **18** égalerait la meilleure passe humaine
> publiée, une portée de **31** la dépasserait de 72 %. Et le corpus qui permet cette comparaison
> est sur **un seul objet**.

⚠⚠ **Ma première version a effacé un objet en silence** : exiger que le nom d'un segment
**commence** par sa bande a fait disparaître `PHerc0500P2` (`0500P2-wrap01_0919`) — l'objet
courant, absent du tableau sans qu'une ligne le signale. Le contrôle « l'objet courant publie une
spire par surface » l'a dit **en levant sur une clef absente**, ce qui a produit une seconde
correction : ⭐ **un objet manquant est désormais un échec NOMMÉ, pas une exception** — une
batterie qui lève ne dit pas combien de contrôles ont tourné.

---
##### ⭐⭐⭐ LE RANG MONTE VERS LE DEHORS — 27/27, et une passe humaine couvre un tiers de mètre

> Mesure : `src/nappe/le_sens_du_rang.py` (34 contrôles) → `docs/mesures/le_sens_du_rang.json`.
> Figure : `src/figures/figure_le_sens_du_rang.py` (12 contrôles), le 2026-09-08.
> Document : [`85`](85_le_sens_du_rang.md). ⚠ 28 Mio de maillage rapatriés dans
> `data/paris4_bandes/` (gitignoré, retéléchargeable depuis l'index).
>
> ```bash
> uv run python src/nappe/le_sens_du_rang.py --telecharger --toutes-revisions
> uv run python src/nappe/le_sens_du_rang.py --json docs/mesures/le_sens_du_rang.json
> uv run python src/figures/figure_le_sens_du_rang.py \
>     --sortie docs/images/85_le_sens_du_rang.png
> ```

![le rang monte-t-il vers le dehors](images/85_le_sens_du_rang.png)

⭐⭐⭐ **La seule question que `84` avait laissée ouverte est tranchée** : le rayon des 28 bandes
monte **27 fois sur 27**, de **7,41 mm** au rang 10 à **24,84 mm** au rang 128, et l'ordre
**survit à un second centre**. ⭐ Sonde dans l'autre sens : forcer le centre à l'origine fait
tomber **sept** contrôles.

★★ **Et la prédiction ajoutée pour rendre l'explication FALSIFIABLE tient.** Si une passe humaine
couvre une longueur de feuille constante, `étendue × 2πR` l'est aussi :

| | |
|---|---:|
| médiane, 28 bandes | **384 mm** |
| bornes hors la bande du cœur (27) | **283 à 535 mm** (**×1,89**), écart-type relatif **17 %** |
| la bande du cœur, à part | 18 spires, **838 mm** — un second régime |

⚠⚠ **Le résidu de 17 % n'est pas du bruit, c'est de la quantification** : on ne coupe pas deux
spires et demie, et dans chacun des **9 paliers** d'étendue constante la longueur croît
mécaniquement avec le rayon. Les maximums avant chaque descente déclinent (838, 535, 498, 490,
459, 436, 433, 415 mm), ce qui *ressemblerait* à un budget par passe se réduisant vers
l'extérieur — mais un pas de quantification vaut une **circonférence entière** (156 mm au rang
128), donc **à cette précision les deux ne sont pas séparables** et la mesure ne tranche pas.

⚠⚠⚠ **ET CE MAILLAGE NE DONNE PAS LE PAS INTER-FEUILLES**, mesuré sur la grille elle-même : ses
cellules voisines sont à **905 µm**, trois à six fois l'écart cherché. Limite de **GRILLE**,
publiée comme telle — donc **la demi-feuille de `PHercParis4` reste un chiffre à mesurer
ailleurs**, et le coût d'un changement d'objet n'est pas encore chiffré.

> ⭐⭐ **CE QUE ÇA CHANGE.** Le coût humain se compte en **longueur de feuille**, pas en nombre de
> spires : la même heure couvre **neuf fois moins de spires** au bord qu'au cœur. Donc « 31
> spires » n'est pas l'unité naturelle de l'effort, et deux objets de 31 spires ne coûtent pas la
> même chose. ⚠ Ce que ça ne change pas : le prix demande toujours 31, et la plus longue bande
> publiée en vaut **18**.

⚠⚠ **Un contrôle corrigé DEUX fois, et les deux erreurs sont gardées.** Il comparait d'abord les
révisions **par position** dans deux listes de longueurs différentes — une bande manquante décalait
tout, et les « 16 % d'écart de rayon » étaient un désaccord de **mes deux listes**. Corrigé, il
exigeait ensuite l'égalité des rayons à 1 % : **ils diffèrent de 15,9 % et ce n'est pas un défaut**
— les deux révisions couvrent **50 877** et **78 453** cellules. Un contrôle qui exigerait
l'égalité ne peut pas passer pour une raison qui n'est pas un défaut. Ce qui est asserté est le
**classement**, qui survit entier.

---
##### ⭐⭐⭐ LE CRITÈRE DE MARCHE PERDUE EST AU PERCENTILE 27 DE SON PROPRE OBJET

> Mesure : `src/nappe/la_demi_feuille_par_objet.py` (21 contrôles, hors ligne) →
> `docs/mesures/la_demi_feuille_par_objet.json`. Figure :
> `src/figures/figure_la_demi_feuille_par_objet.py` (14 contrôles), le 2026-09-08.
> Document : [`86`](86_la_demi_feuille_par_objet.md).
>
> ```bash
> git clone https://github.com/pscamillo/winding-ruler data/repos/winding-ruler
> uv run python src/nappe/la_demi_feuille_par_objet.py \
>     --json docs/mesures/la_demi_feuille_par_objet.json
> uv run python src/figures/figure_la_demi_feuille_par_objet.py \
>     --sortie docs/images/86_la_demi_feuille_par_objet.png
> ```

⚠ `85` disait la demi-feuille de `PHercParis4` « à mesurer ailleurs ». **Elle était mesurée, à
côté, dans un clone de l'arbre** — `winding-ruler/results/atlas_collection_v2.csv`, période
inter-spires de **36 objets**. Sixième fois que « chercher dehors ce qu'on croit absent » paie, et
`67` §1 l'avait déjà écrit pour ce fichier précis.

![la demi-feuille, objet par objet](images/86_la_demi_feuille_par_objet.png)

| | valeur | population |
|---|---:|---|
| ce dépôt | **135,5 µm** → demi **67,75** | 12 paires des 13 spires publiées, maillages 2,215 µm |
| l'atlas | **196,6 µm** (p25 131,1 · p75 337,0) | 16 coupes × 812 rayons du fragment entier |
| **percentile du nôtre** | **27** | rapport ×1,45 |

⭐⭐⭐ **CONSÉQUENCE SUR TOUT L'APPAREIL DE MARCHE.** Un critère dérivé du quartile le plus
**serré** est plus exigeant que l'objet : les portées publiées — **4** pour le pas normal, **5**
avec la nappe lissée, **6** pour la borne — sont des **BORNES BASSES**, pas des plafonds. À la
demi-feuille médiane du fragment (98,3 µm), le même marcheur aurait **45 % de tolérance en plus**.

⚠⚠ **Ce ne sont pas deux mesures contradictoires** — même grandeur, deux **populations**. Et le
sens du biais est connu : l'atlas lit des **prédictions**, donc une fusion de deux feuilles saute
un écart et en rapporte un double, donc il **surestime**. ⚠ Ce qui ne change pas : la marche
marche là où les spires sont publiées, donc c'est le **bon endroit pour juger** — l'atlas ne
corrige pas le chiffre, il dit **quelle partie de l'objet** il décrit.

⭐⭐ **Le prix du changement d'objet est chiffré** : `PHercParis4` demi-feuille **91,20 µm** contre
67,75 local (**+34,6 %**), mais à médiane contre médiane **98,3 → 91,2**, donc le candidat est
**7 % plus serré**. Les deux lectures sont dans la mesure ; celle qui compte dépend d'une région
qui n'existe pas encore pour le candidat.

> ■ **ET COMME CRITÈRE DE CHOIX DE ROULEAU, IL NE CHOISIT PAS** : les treize tiennent dans un
> facteur **1,20** (86,4 à 103,7 µm) quand l'atlas entier va jusqu'à **1,71**. L'étroitesse est
> celle **des treize**, pas de la mesure — donc la géométrie ne sépare pas mieux que la part
> comprimée de `33`, et elle est *déjà mesurée*, donc gratuite à essayer. **Deux critères
> indépendants concordent : rien dans les treize ne désigne un rouleau.**

⚠⚠ **Deux fautes à moi, gardées.** (1) Ma première version rendait un **mot** — « au premier
quartile » — en tolérant **5 % autour de p25**, soit un **seuil choisi pour que le chiffre du jour
passe** ; une sonde qui le retirait faisait basculer le verdict. Remplacé par un **percentile**,
sans seuil, qui **borne** hors des quantiles publiés au lieu d'extrapoler. (2) Le glyphe `⛔`
sortait **en carré** dans la ligne du panneau A qui porte le verdict, parce que `prose_tracable`
ne lit que la prose du bas : ⭐ corrigé par **`figure_commune.Tracee`**, un calque qui retient
**tout** le texte dessiné, posé dans le module commun (5 contrôles) parce que le dépôt compte
**104 figures** et que l'angle mort y est le même — sans retrofit des 104.

---
##### ⭐⭐⭐ LA FORME DU DÉPÔT, MESURÉE — et la garde qui ne peut pas échouer

> Instrument : `src/depot/la_forme_du_depot.py` (22 contrôles) →
> `docs/mesures/la_forme_du_depot.json`. Document : [`87`](87_la_forme_du_depot.md), le
> 2026-09-08. ⚠ Ce n'est pas un audit ponctuel : c'est lui qui dira si un refactor a servi.
>
> ```bash
> uv run python src/depot/la_forme_du_depot.py --json docs/mesures/la_forme_du_depot.json
> ```

Plainte de l'auteur : *« plein de scripts dans tous les sens, pas un gros logiciel avec des
plugins, des duplicata, des trucs abandonnés qu'on refait sans le savoir, aucun test »*. Une
plainte se traite avec un chiffre.

⛔ **FAUX sur un point, et il faut le dire d'abord** : **267/356** modules (75 %) exposent
`--verifier` et **0** batterie n'est non enregistrée. **Les tests ne sont pas la panne.** Les
vrais trous sont `excision` **13/29** et `volume` **8/17** ; `apprendre` 8/8 et `outils` 8/8 sont
des récits et des lanceurs.

⭐ **Vrai et chiffré** : 356 modules, **393 arêtes** d'import, **152 (43 %)** n'importent rien du
dépôt, **117 (33 %) isolés**. Duplication hors contrat de greffon : `_leve` ×19, `_pixels` ×14,
`lire` ×13, `charger` ×10, `comparer` ×10, `rapporter` ×10.

⚠⚠⚠ **LA VRAIE PANNE, ET C'EST UNE GARDE DU DÉPÔT.** Sur **486** artefacts de `docs/mesures/`,
seuls **182 (38 %)** sont retrouvables par leur **nom complet** ; `artefacts_orphelins` déclare
« 0 orphelin » avec **46 % de son verdict reposant sur une tige de ≤12 caractères**, la plus courte
à **4** (`juge_scroll4.json` matché par le mot `juge`). ⚠ Le compromis est **assumé dans sa
docstring** — le nom exact signalait 389/568, « une alerte qui désigne les deux tiers du corpus ne
désigne rien » — donc le remède n'est pas un préfixe plus étroit : **le producteur doit être
DÉCLARÉ.** C'est la cause mécanique de « on refait des trucs existants ».

> ⭐⭐⭐ **ET UNE IDÉE DE L'AUTEUR A ANNULÉ UN REFACTOR.** Sa proposition — *« la liste de tous les
> mots du dépôt, les plus utilisés, ça peut faire des catégories ? »* — reformulée en la version
> qui marche : pas les mots de la prose (francophone, ils fuient des docstrings) mais le
> **vocabulaire de domaine lu par l'AST**, et pas la fréquence mais la **co-occurrence**.
>
> | dossier | rapport cohésion interne / hors dossier |
> |---|---:|
> | `apprendre` · `rendu` · `figures` | ×23,9 · ×10,5 · ×5,6 |
> | `depot` · `nappe` · `tables` | ×2,0 à ×2,3 |
> | `encre` (48) · `volume` (17) | ×1,35 · **×1,15** |
> | ⛔ **`tracecheck`** (5) | **×0,61** |
>
> Rapport global **×1,89**, et cohésion absolue **0,0385** — deux modules d'un même dossier
> partagent **4 %** de leur vocabulaire. ⛔ `tracecheck` est **sous le hasard** : ses modules se
> ressemblent moins entre eux qu'avec un module tiré au hasard. **CONCLUSION : il ne faut PAS
> re-partitionner.** Un reclassement gagnerait peut-être ×3 pour **353 déplacements** — la mesure
> désigne la **couche partagée** et la **provenance déclarée**, pas le rangement.

⚠⚠ **Une faute à moi, dans le module qui diagnostique les fautes** : mon compte de batteries
sortait à **zéro** (`Path(champ).name` sur un chemin entre guillemets) et **mon contrôle
n'assertait que « c'est un entier »** — une vérification incapable d'échouer, dans le module qui
diagnostique les vérifications incapables d'échouer. ⚠ Et **deux mesures jetées avant
publication** : « 348 artefacts nommés nulle part » puis « 240 », toutes deux fausses pour deux
raisons différentes. Une mesure jetée est une leçon sur l'instrument.

---
##### ⭐⭐⭐ LA COMPOSITION — et la provenance devient un fait OBSERVÉ

> Outil : `src/depot/enchainer.py` (32 contrôles) + `docs/chaines/*.chaine`. Document :
> [`88`](88_enchainer.md), le 2026-09-08. ⭐ Le lanceur est **lui-même un greffon** : il vit dans
> `src/depot/`, donc `lplv` le découvre comme les 190 autres, et un contrôle l'asserte.
>
> ```bash
> lplv enchainer docs/chaines/les_spires_publiees.chaine --sec
> lplv enchainer docs/chaines/les_spires_publiees.chaine \
>     --json docs/mesures/enchainer_les_spires_publiees.json
> ```

Choix de l'auteur, après le diagnostic de `87` : **la composition avant la provenance déclarée**.
Et la mesure lui donne raison — faire déclarer chaque module aurait demandé **314 motifs écrits à
la main** sur 486 artefacts, dont **105** nommés par plusieurs modules (un lit, un écrit) : une
seconde description, libre de dériver.

⭐⭐⭐ **Une chaîne qui tourne fait mieux qu'une déclaration : elle OBSERVE.** Inventaire des
racines surveillées avant et après chaque étage, puis différence. Mesuré sur la première chaîne
réelle : **6/6 étages en 2,71 s**, **6 artefacts attribués au verbe exact qui les a écrits** —
trois `.json` et trois `.png`, **sans un mot de déclaration**.

| décision | raison |
|---|---|
| `subprocess`, pas `os.execvp` | un processus remplacé ne revient jamais, donc un seul étage tournerait ; le code de sortie est **enregistré** plutôt que consulté au vol |
| ⚠⚠⚠ validation **avant** le premier étage | une coquille à la cinquième ligne ne doit pas coûter les quatre étages du dessus |
| « créé » et « modifié » = **deux** listes | régénérer un artefact n'est pas en produire un neuf |
| la portée de l'observation **voyage** avec le résultat | `data/` (98 275 fichiers, 168 Gio) est hors surveillance, donc « rien écrit **parmi les racines observées** » |
| ⚠⚠ ni parallélisme, ni cache, ni reprise, ni réessai | une couche se construit quand un **compteur** montre ce que celle du dessous laisse passer |

⚠ Les deux chaînes livrées rejouent ce qui était lancé **à la main** : les six étages de `84`/`85`/
`86` (dont deux téléchargements), et les quatre gardes de l'arbre — dont l'attente était réécrite
à chaque fois, et dont un `pkill -f` mal fermé a déjà tué le shell.

⚠⚠ **Deux fautes à moi, trouvées par mes propres sondes.** (1) Le run à sec annonçait **6 étages
muets** alors que rien n'avait tourné : il signalait l'absence d'un effet qu'il avait lui-même
empêché. (2) ⚠⚠⚠ Une sonde déplaçant la validation **au fil de l'eau passait les trente
contrôles** — j'assertais que l'exception nomme le verbe, **jamais que rien n'avait tourné**. Forme
falsifiable retenue : une chaîne dont le premier étage écrit et le second verbe est inconnu doit
laisser le disque **intact**.

> ⭐⭐ **CE QUE ÇA DÉBLOQUE.** `artefacts_orphelins` pourrait lire les enregistrements de chaîne et
> ne deviner que pour ce qu'aucune chaîne n'a jamais produit — le décompte deviendrait **visible et
> ne pourrait que rétrécir**. Tranche suivante, à part parce qu'elle touche une garde.

---
##### ⭐⭐⭐ L'ÉCHELLE DE LA PROVENANCE — ce que « 0 orphelin » cachait

> Garde : `src/depot/artefacts_orphelins.py`, désormais **9 contrôles de mécanique + 5 contrôles
> d'échelle + 1116 artefacts balayés**. Document : [`89`](89_lechelle_de_la_provenance.md), le
> 2026-09-08.
>
> ```bash
> uv run python src/depot/artefacts_orphelins.py --verifier
> lplv enchainer docs/chaines/les_gardes_de_larbre.chaine
> ```

| barreau | ce qu'il affirme | compte |
|---|---|---:|
| ⭐ **1 · OBSERVÉ** | une chaîne a **vu** ce fichier apparaître pendant un étage | **3** |
| ⚠ **2 · DEVINÉ** | l'heuristique de tige a matché, **et sa longueur est retenue** | **1111** |
| ⛔ **3 · ORPHELIN** | ni l'un ni l'autre | **0** |

**La dette : `4 car. ×12 · 5 car. ×275 · 6 car. ×30 · 7 car. ×22 · 8 car. ×162 · 9 car. ×70 ·
10 car. ×67 · 11 car. ×10 · 12 car. ×27`** — soit **675 verdicts sur 1111 (61 %) qui tiennent à
douze caractères ou moins**, et **12 à quatre**.

⚠⚠ **Le dépôt n'est pas en plus mauvais état qu'hier** : ces 1111 verdicts étaient déjà des
devinettes. Ce qui change est qu'ils **portent leur prix**, et qu'une chaîne écrite les déplace un
par un vers le barreau certain. ⚠ La dette ne fait **pas** échouer la garde — rouge sur 61 % du
corpus, elle se ferait désapprendre, et son propre compromis l'avait établi (389 orphelins sur 568
au nom exact).

⭐ **Neuf contrôles sur entrée fabriquée tournent AVANT le parcours** de **430,76 s** — 81 % du
budget des quatre gardes, chiffre que `lplv enchainer` venait de mesurer — et sortent sans le payer
s'ils échouent.

> ⭐⭐⭐ **TROIS DÉFAUTS ATTRAPÉS DÈS LE PREMIER PARCOURS, TOUS LES MIENS**, dont deux dans les
> contrôles que je venais d'écrire :
> 1. ⛔ « 3 enregistrements créditent un fichier disparu » — **les trois PNG existent**. Je testais
>    « disparu » contre la liste **filtrée** (`SUFFIXES` n'a pas `.png`), pas contre le disque.
> 2. ⛔ le compte des barreaux tombait **à une unité près** : je soustrayais `len(EXEMPTS)` en
>    supposant tous les exemptés rencontrés.
> 3. ⭐⭐ **et cette unité cachait une EXEMPTION MORTE** — `src/outils/repos.tsv` exempté d'un
>    parcours qui ne retenait que `docs/` et `data/`, donc une décision qui **ne protégeait rien**.
>    Réparation d'**accessibilité** et non suppression (le skill : injoignable = défaut), coût
>    **zéro** — `git ls-files src/**` ne rend qu'**un** fichier à suffixe d'artefact, exactement
>    celui que la table nomme. Un contrôle neuf garde le cas pour de bon.

⚠ **Piège d'outillage repayé sous une forme neuve** : mes relances ont laissé **trois parcours de
430 s tourner en concurrence**, se disputant les entrées-sorties — aucun ne finissait et aucune
sortie n'apparaissait, les tampons n'étant vidés qu'à la fin. Variante en **lecture seule** du
piège « deux `validate.sh` concurrents ». Tués **par PID**, jamais par motif.

---
##### ⭐⭐⭐ L'AXE DU ROULEAU EST UNE COURBE — 63,9 épaisseurs de feuille, et `85` rétracté

> Mesure : `src/nappe/laxe_est_une_courbe.py` (21 contrôles) →
> `docs/mesures/laxe_est_une_courbe.json` + `laxe_trace.json`. Figure :
> `src/figures/figure_laxe_est_une_courbe.py` (14 contrôles). Chaîne :
> `docs/chaines/laxe_et_le_cout.chaine`. Document : [`90`](90_laxe_est_une_courbe.md), le
> 2026-09-08.
>
> ```bash
> lplv enchainer docs/chaines/laxe_et_le_cout.chaine
> ```

![l'axe du rouleau est une courbe](images/90_laxe_est_une_courbe.png)

⚠ `85` estime l'axe comme **UN** point (x, y). Un contrôle que je n'avais pas fait le réfute :
l'étendue radiale d'une bande vaut **×2,4 à ×38** ce que « étendue × période » prédit, et le
rapport **croît** quand l'étendue diminue — une bande de deux spires couvrirait l'équivalent de
soixante-dix-sept spires.

⭐⭐⭐ **MESURE : le centre par tranche se déplace de 12,6 mm en x et 19,8 mm en y sur 144 mm de z,
EN REVENANT SUR SES PAS**, et s'écarte de sa **propre droite** de 11,6 mm — soit **63,9 épaisseurs
de feuille**. Le rouleau est **courbé**, ce qui est l'état normal d'un papyrus carbonisé.

⚠⚠ **Le confondant est levé, pas supposé** : si une tranche ne contenait pas un tour complet, sa
médiane serait tirée vers le secteur présent, et un secteur variant avec z se lirait comme une
courbure. Mesuré **100 % des 36 secteurs dans chaque tranche**. ⭐ C'est **une sonde fabriquée qui
m'a appris à poser cette question, en échouant**.

| | axe plat (`85`) | axe **courbe** |
|---|---|---|
| classement des rayons | 27/27 | **27/27** |
| longueur par passe | 384 mm, 283 à **838** (**×2,97**) | **362 mm, 273 à 460** (**×1,68**) |
| hors le cœur | ×1,89, étr 17 % | ×**1,51**, étr **12,7 %** |

⚠⚠⚠ **RÉTRACTATION — le « second régime » de `85` n'existe pas.** La bande du cœur y valait
**838 mm**, un facteur 2,2 au-dessus des autres, et je l'avais publiée comme une population à
part. Elle vaut **460 mm** et rentre dans la distribution. **Il n'y avait pas deux régimes : il y
avait mon erreur d'axe, concentrée sur la bande la plus PROCHE de l'axe**, donc la plus sensible à
s'être trompé dessus. La rétractation est portée **en tête de `85`**, là où le chiffre faux a été
publié.

> ⭐⭐⭐ **POURQUOI ÇA COMPTE POUR LE GRAAL.** Un marcheur qui supposerait un axe droit se trompe
> de **deux centimètres**, soit une **centaine d'épaisseurs de feuille** : un tel cadre placerait
> **une spire à la place d'une autre**, ce qui *est* exactement l'erreur que l'humain corrige à la
> main. ⭐ Donc **aucun repère global ne remplacera cet humain** — ce qui le remplacera devra être
> **local**, comme la marche l'est déjà.

⚠⚠ **Trois seuils que j'aurais réglés sur ce qui passe** (« ×10 » quand la sonde donnait 7,4,
« <5 % » pour 6,3). Remplacés par des **comparaisons** : l'écart à sa propre droite en épaisseurs
de feuille (**1,0** droit contre **14,1** courbé), et « bien plus serré qu'un centre unique ».
⚠ Le troisième cachait une vérité que ma revendication ignorait — **une tranche a une épaisseur,
donc l'axe bouge dedans** : « le rayon par tranche est parfait » n'a jamais été vrai.

⚠ Et deux défauts de figure : les **graduations d'axe inversées** (`lo` écrit en haut alors que le
tracé le place en bas — une figure étiquetée à l'envers dit la mauvaise **direction**, qui est tout
le sujet), et un détail de contrôle affichant un **message d'échec sur un succès**.

---
##### ⭐⭐⭐ LE PAS LU SUR LES TRANSFERTS QUE L'HUMAIN A RÉUSSIS — et un gradient rétracté

> Mesure : `src/nappe/le_pas_lu_sur_les_transferts.py` (15 contrôles) →
> `docs/mesures/le_pas_lu_sur_les_transferts.json`. Figure :
> `src/figures/figure_le_pas_lu_sur_les_transferts.py` (14 contrôles).
> Document : [`91`](91_le_pas_lu_sur_les_transferts.md), le 2026-09-08.

![le pas lu sur les transferts](images/91_le_pas_lu_sur_les_transferts.png)

`84` établit que `PHercParis4` publie **92 franchissements de spire dans une seule maille**, et
zéro ailleurs. Une bande est donc **un transfert déjà fait à la main**, et sa géométrie se lit
**sans toucher au volume**.

⭐⭐⭐ **L'ÉTENDUE DÉCLARÉE EST LE NOMBRE DE TOURS** : écart médian **−0,01 tour**, **27 bandes
sur 28** à moins d'un dixième. `w028-037` rend **9,97** pour 10, `w116-117` rend **1,99** pour 2.
Les noms ne sont pas des étiquettes — donc les 92 franchissements sont **92 transferts réels**.
⚠ Une exception nommée : `w010-027`, **12,75** tours pour 18.

⭐⭐ **ET LE PAS VAUT 164 µm** (136 à 207) sur les 12 bandes d'au moins 4 tours, contre **182,4 µm**
à l'atlas `winding-ruler`. Les deux chemins ne partagent **ni la donnée, ni la méthode, ni
l'auteur** — prédictions de surface le long de rayons contre maillages publiés par des humains — et
s'accordent à 10 %.

⚠ La lecture est valide parce qu'une **ligne** de grille est iso-z : **0,73 mm** d'écart-type
contre **41,8 mm** pour une colonne. Vérifié, pas supposé.

⚠⚠⚠ **UN GRADIENT RÉTRACTÉ AVANT D'ÊTRE PUBLIÉ.** La pente brute donne ~205 µm au cœur et
**~1000 µm au bord** — les 16 bandes courtes rendent **391 µm** de médiane, qu'on lirait comme une
**délamination**. Le contrôle le tue sans aucune hypothèse, sur **UNE SEULE bande de dix tours**,
donc à pas constant **par construction** :

| fenêtre | 10 | 6 | 4 | 3 | 2 | 1 |
|---|---:|---:|---:|---:|---:|---:|
| pente | **202** | 208 | 224 | 287 | **523** | **1817** µm |

⭐⭐ **RÈGLE POUR TOUT MARCHEUR : on ne mesure pas le pas d'un enroulement sur un arc court.**

⚠⚠ **Et la cause n'est PAS établie**, écrit plutôt que deviné. Une section **ovale** ne gonfle pas
la pente, elle la **DÉGONFLE** (200,3 contre 183,2) — c'était ma première explication, fausse : un
`cos(2θ)` fait deux périodes par tour. Un **centre décalé** gonfle dans le bon sens (200 / 216 /
233 / 270 pour 0 à 2 mm) mais il faudrait des **dizaines** de mm pour atteindre 1817. ⭐ **Le
contrôle tient sans la cause**, et les deux explications réfutées sont **gardées dans les
contrôles** pour qu'on ne les re-propose pas.

> ⭐ **CE QUE ÇA DONNE AU GRAAL.** La demi-feuille de `PHercParis4` devient un chiffre **établi
> par deux instruments indépendants** et non emprunté : **82 à 91 µm**, contre 67,75 µm sur
> l'objet courant. Le coût d'un changement d'objet, chiffré par `86` à l'atlas seul, est
> **corroboré**.

---
##### ⭐⭐⭐ LES TRANSFERTS HUMAINS SONT CONTINUS AU CŒUR, BRISÉS AU BORD

> Mesure : `src/nappe/la_continuite_des_transferts.py` (16 contrôles) →
> `docs/mesures/la_continuite_des_transferts.json`. Figure :
> `src/figures/figure_la_continuite_des_transferts.py` (14 contrôles).
> Document : [`92`](92_la_continuite_des_transferts.md), le 2026-09-08.

![la continuité des transferts](images/92_la_continuite_des_transferts.png)

Le plus grand saut entre deux cellules **voisines** d'une même ligne de grille, rapporté au pas
d'échantillonnage — une grandeur **sans unité à choisir** :

| tiers | rapport médian | max | bandes |
|---|---:|---:|---:|
| **cœur** | **1,7** | 2,4 | 9 |
| **milieu** | **5,9** | 22,1 | 9 |
| **bord** | **31,0** | 41,1 | 10 |

⭐⭐ **Là où le rouleau est intact, un humain trace continûment ; là où il ne l'est pas, MÊME UN
HUMAIN rend une surface discontinue.** Un automate ne peut donc pas être jugé sur les bandes
externes comme sur les internes. ⭐ Et ça **complète** `84` : l'étendue qui tombe de 18 à 2 spires
n'est pas seulement la circonférence qui croît (`85`), c'est aussi **la continuité qui casse**.

⚠⚠ **Une première lecture fausse, gardée.** J'ai vu les sauts sur les lignes 3, 4 et 181 d'une
grille de 198 et conclu « effilochage du bord ». Le test **structurel** — une cellule est
intérieure quand ses **quatre** voisines sont valides, sans marge choisie — les **garde** : les
sauts de trente millimètres sont dans de la matière réellement maillée.

⚠⚠⚠ **Et une seconde, réfutée par le test direct.** Les sauts corrèlent à **r = 0,797** avec le
gonflement de pente que `91` n'expliquait pas — 173 µm de pente médiane sous 5 mm de saut, **393**
au-delà. **J'ai failli publier la cause.** Mais **retirer les lignes qui contiennent un saut change
la pente de 0,2 % en médiane et 1,5 % au pire**, sur 15 bandes.

> **Une corrélation de 0,80 entre deux quantités qui montent ensemble n'est pas un mécanisme.**
> Retirer la cause supposée et regarder si l'effet bouge, si.

⚠ La cause de `91` reste donc **non trouvée**, avec **trois** candidats réfutés : section ovale
(elle dégonfle), centre décalé (dix fois trop faible), sauts (moins de 2 % d'effet).

---
##### ⭐⭐⭐ OÙ LES SPIRES SONT-ELLES PARALLÈLES ? AU MILIEU — et les deux échecs sont au BORD

> Mesure : `src/nappe/deux_modes_dechec_du_transfert.py` (20 contrôles) →
> `docs/mesures/deux_modes_dechec_du_transfert.json`. Figure :
> `src/figures/figure_ou_les_spires_sont_elles_paralleles.py` (14 contrôles).
> Document : [`93`](93_ou_les_spires_sont_elles_paralleles.md), le 2026-09-08.

![où les spires sont-elles parallèles](images/93_ou_les_spires_sont_elles_paralleles.png)

⭐⭐ **Le panneau B de la figure est la carte du problème** : il superpose la continuité de `92` et
le parallélisme de `93` par tiers, et montre que **les deux montent au même endroit**. Écrire « le
problème est localisé » sans les mettre côte à côte demanderait qu'on le croie.

Un marcheur transfère le long de la **normale**, et ce pas n'atterrit sur la spire voisine que si
les deux spires sont **parallèles** — à 30° de désalignement, un pas de 182 µm tombe à **91 µm de
côté**, la moitié du pas.

| bande | rayon | rot./cellule | adjacent | **un tour** | rapport |
|---|---:|---:|---:|---:|---:|
| `w010-027` | 4,1 mm | **13,3°** | 11,6° | 42,4° | ⚠ **non résolue** |
| `w073-076` | 14,0 mm | 3,2° | 6,2° | **7,7°** | **×1,23** |
| `w128-129` | 23,8 mm | 1,9° | 6,3° | **26,3°** | **×4,18** |

⭐⭐⭐ **La réponse est un U** : ni « pire au cœur » ni « pire au bord », **minimal au milieu**.
Par tiers : cœur ×1,88 · milieu ×1,80 · **bord ×3,67**.

⚠⚠⚠ **Les deux bandes internes ne sont pas désalignées, elles sont NON RÉSOLUES** : `w010-027`
n'a que 27 colonnes par tour, donc sa normale est moyennée sur **13,3° d'arc** — plus que son
propre désaccord adjacent. ⭐ Le critère d'exclusion est **dérivé** de cette comparaison, pas
choisi, et il exclut exactement deux bandes.

> ⭐⭐ **LES DEUX MODES D'ÉCHEC SONT AU BORD**, pas aux deux bouts : la surface y est **brisée**
> (×31, `92`) *et* les spires y sont **désalignées** (×3,67 au même tiers). Au milieu, les deux sont propres.
> **Un automate a un problème localisé, pas uniforme.**

⚠⚠⚠ **Une erreur à moi qui a INVERSÉ la conclusion.** Mon exploration comparait la **bande 0** à
la **bande 7** en appelant la seconde « le bord » — or les deux sont dans le tiers intérieur. J'en
avais tiré « désaligné au cœur, parallèle au bord ». **Un tiers se compte sur le corpus entier,
pas sur les premières lignes d'un tableau.**

⚠⚠ **Et le « plancher » n'est pas du bruit** : le désaccord entre cellules adjacentes est dominé
par la **rotation** de la normale (13,3° au cœur, 1,9° au bord). Preuve : une spirale **parfaite**
à 60 colonnes/tour rend **6,0° = 360/60**. Deux fixtures qui affirmaient l'inverse sont corrigées.

⚠ **Et `--verifier` est resté vert à 17 contrôles pendant que `main()` plantait** sur une clef
renommée. ⭐ L'affichage vit désormais dans `main_affichage(r)`, **que la batterie lance** — une
batterie qui n'emprunte jamais le chemin de l'utilisateur ne garde pas ce qu'il voit.

---
##### ⛔⛔ LE CUBE LU MOINS CHER — l'économie est RÉFUTÉE par le corpus, et par ma propre sonde

> Mesure : `src/nappe/le_cube_lu_moins_cher.py` (22 contrôles) →
> `docs/mesures/le_cube_lu_moins_cher.json`. Figure :
> `src/figures/figure_le_cube_lu_moins_cher.py` (18 contrôles).
> Document : [`103`](103_le_cube_lu_moins_cher.md), le 2026-09-10.

![le cube lu moins cher](images/103_le_cube_lu_moins_cher.png)

`102` a mesuré que la matière porte **au moins** deux pas, et sa portée est **censurée** : 17 bandes
sur 28 butent sur le plafond. Relever ce plafond coûterait **quatorze heures** à 15,4 s le cube.
Avant de subir ce coût, il fallait savoir s'il était réductible.

Une économie existait **en principe** : **échantillonner** le cube plus grossièrement — un voxel sur
deux, **même portée** de 98,4 µm — ne change pas ce qu'on regarde, seulement ce qu'on paie.

| pas | rangées | s/cube | gain | écart médian | p90 | **> 10°** | marches de 6 pas abîmées |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1681 | 14,40 | ×1,00 | — | — | — | — |
| 2 | 441 | 8,37 | **×1,72** | 2,09° | 6,18° | **7,3 %** | **36,5 %** |
| 3 | 196 | 4,82 | ×2,99 | 4,39° | 10,87° | 10,9 % | 50,0 % |
| 4 | 121 | 3,76 | ×3,83 | 5,77° | 16,36° | 29,1 % | 87,3 % |

> ⛔ **Aucune économie ne passe : le cube se lit au voxel près.**

⭐⭐⭐ **Et c'est la conséquence ENCHAÎNÉE qui décide.** Pris **un** pas à la fois, 7,3 % n'a l'air de
rien — mais `102` **enchaîne**, et `1 − (1 − p)^6` vaut **36,5 %** de marches abîmées. Publier le
taux par pas sans sa conséquence laisserait croire l'économie inoffensive.

##### ⚠⚠⚠ Ma propre sonde disait l'inverse, sur deux bandes

Le premier contrôle apparié, sur **2 bandes**, donnait **0 %** de cellules au-delà de dix degrés au
pas 2. J'allais adopter l'économie sur cette base ; les **28 bandes** disent **7,3 %**.

> ⚠⚠ *Un bord se compte sur le corpus entier, pas sur les bandes qu'on a sondées* — la faute que
> `93` a payée, que `95` a réécrite, et que je viens de repayer. ⭐ Ce qui l'a attrapée n'est pas
> une relecture : c'est d'avoir relancé sur le corpus **avant** de publier, parce que la règle
> était écrite.

##### ⚠⚠⚠ Et le gain de temps n'est pas le gain de points

| pas | prédit par les points | **mesuré** |
|---|---:|---:|
| 2 | ×7,44 | **×1,72** |
| 3 | ×25,12 | ×2,99 |
| 4 | ×51,78 | ×3,83 |

Une lecture distante est dominée par le nombre de **plages d'octets** — une par rangée `(z, y)` — et
par un **fixe par cube** (plancher de **3,76 s**), pas par le nombre de points. **Le coût se mesure,
il ne se modélise pas.** ⚠ Et le rapport de points lui-même n'est pas huit : `(41/21)³ = 7,44`.

##### ⚠⚠ Trois corrections de contrôle, dont deux sur mes propres assertions

- ⚠ **La référence n'est pas une économie à juger**, c'est le statu quo. La compter produisait la
  ligne absurde « pas 1 — la garde ne tient pas », qui se lit comme un refus de lire le cube entier.
- ⚠⚠ **J'avais asserté que la barre du nul est plus haute pour un cube grossier** ; la mesure dit
  l'inverse à demi = 10, et le balayage montre qu'elle n'est **pas monotone** (8,91 / 11,21 / 7,54 /
  6,00). Le contrôle asserte désormais qu'elle est **refaite par forme**, pas son sens.
- ⚠ **Mes contrôles assertaient le RÉSULTAT** — « un pas plus grossier est retenu » — ce qui aurait
  obligé à les réécrire le jour où la réponse change, c'est-à-dire un contrôle incapable d'échouer
  honnêtement. Ils sont devenus **structurels**.

##### ⚠ Ce que la tranche ne débloque pas, et ce qu'elle laisse

- **La portée de `102` reste à quatorze heures** pour trente pas : la borne se lèvera au prix plein,
  ou pas du tout.
- ⭐ **Mais le coût est mesuré et non supposé** — 15,4 s par cube, plancher de 3,76 s, temps qui suit
  les rangées — donc chaque mesure future se chiffre **d'avance** au lieu de se découvrir après sept
  heures.
- ⚠ Le verdict porte sur **ce** cube (98,4 µm, demi = 20) et **ce** fragment ; et la garde du
  fabriqué est éprouvée à **un** niveau de bruit (σ = 15) qui n'est pas celui, inconnu, du volume.

---
##### ⭐⭐⭐ COMBIEN DE PAS LA MATIÈRE PORTE — le premier acquis POSITIF, et sa borne

> Mesure : `src/nappe/combien_de_pas_la_matiere_porte.py` (21 contrôles) →
> `docs/mesures/combien_de_pas_la_matiere_porte.json`. Figure :
> `src/figures/figure_combien_de_pas_la_matiere_porte.py` (18 contrôles).
> Document : [`102`](102_combien_de_pas_la_matiere_porte.md), le 2026-09-10.

![combien de pas la matière porte](images/102_combien_de_pas_la_matiere_porte.png)

`99` rend le **pas**, `101` la **direction**. Mais dérouler n'est pas faire **un** pas, c'est les
**enchaîner** — et la question qui décide est *au bout de combien de pas la matière cesse de
confirmer*. Le prix tolère 8 h d'humain là où l'état de l'art en dépense 775 sur la correction du
transfert ; cette tranche mesure jusqu'où on va sans lui.

| | mesuré |
|---|---:|
| pas confirmés, médiane, en **interrogeant la matière** | **2,00** |
| pas confirmés, médiane, **automate naïf** (pas nominal, direction radiale) | **0,00** |
| avantage | **+2,00 pas** |
| distance médiane portée | **583,9 µm** = **3,4** feuilles nominales |
| sorties du volume | **0** sur 28 bandes |

> ⭐⭐⭐ **C'est la PREMIÈRE fois de la campagne que la voie « interroger la matière » BAT l'état
> de l'art**, au lieu de simplement ne pas être réfutée. Et il n'y a **aucun référent humain** dans
> la boucle : direction du tenseur de structure, pas du balayage calibré, vérification par le
> critère de `98`. Le maillage ne sert qu'à dire **où commencer**.

⭐⭐ **Le lecteur est un seam**, donc le **même** marcheur tourne sur un volume fabriqué dont on
connaît la réponse et sur le vrai volume. Une fixture qui n'exerce pas le chemin réel ne prouve
rien.

##### ⭐⭐⭐ Le témoin n'est pas un homme de paille, et c'est la condition pour que son zéro compte

| empilement fabriqué | matière | naïf |
|---|---:|---:|
| obliquité **0°** — pas nominal et rayon **justes** | **6** (plafond) | **6** (plafond) |
| obliquité **35°** — ce que `100` et `101` ont mesuré | **6** (plafond) | **1** |

⚠ Le départ est recalé sur la famille de plans à chaque obliquité : une cellule qui tombe **entre**
deux feuilles ne correspond à aucune polarité du gabarit, et le contrôle mesurerait alors sa propre
erreur de mise en place — le défaut que la fixture de `100` a payé.

##### ⛔⛔ Le vérificateur ne pouvait pas échouer, et le naïf passait huit pas sur huit

Ma première version vérifiait chaque pas avec le **balayage** de `99`, qui cherche la meilleure
période le long de la direction donnée. Sur un empilement oblique à 35°, la période le long du
**rayon** vaut `173 / cos(35°) = 211 µm` — **dans la fenêtre** — donc le balayage la trouve et
**confirme**.

> ⛔ Elle testait *« la matière est-elle feuilletée ici »* — vrai partout — et non *« le pas a-t-il
> franchi UNE feuille »*, qui est la seule question. Le péché nº 1 du dépôt, sous sa forme la plus
> sournoise.

⭐⭐ **Les deux rôles sont désormais séparés** : `99` **décide** de combien avancer, `98` **vérifie**
à gabarit **fixe** ce que l'avance a traversé, sur le segment réellement parcouru. Après
correction, sur le même empilement oblique : **naïf 1, matière 8**.

##### ⚠⚠⚠ La borne, et elle se dit avant le résultat qu'elle borne

| maximum sur les cellules de la bande | 0 | 1 | 2 | 3 | 4 | 5 | **6 (plafond)** |
|---|---:|---:|---:|---:|---:|---:|---:|
| bandes | 0 | 3 | 1 | 2 | 2 | 3 | **17** |

> ⚠⚠ **17 bandes sur 28, soit 61 %, ont une cellule AU PLAFOND** : « 2,00 pas » est une **borne
> inférieure**, pas une valeur.

Le plafond est un **budget de lecture** : une sonde chronométrée mesure **15,4 s par cube** de 41³
voxels, donc les 672 cubes de la course font **2 h 52 de plancher incompressible** — elle a pris
**7 h**. Le publier comme une limite de matière serait la **butée** de `99`.

##### ⚠⚠ Deux faux zéros et une mesure muette, corrigés dans la foulée

- ⛔ **`x or float('nan')` affichait un ZÉRO MESURÉ comme « pas de donnée »**, parce que `0.0` est
  faux en Python — et un témoin qui confirme zéro pas est le résultat le plus informatif qu'il
  puisse rendre. Corrigé par `nombre_ou_absent`, **une seule** définition dans le module que les
  deux autres importent, avec sa fixture. Même famille que le faux zéro de corrélation de `101`.
- ⚠ **Le verdict ne s'émet plus sans donnée de témoin** : `bool(naif and …)` rendait *False* sur
  une liste vide, c'est-à-dire « la matière ne porte pas plus loin » alors que la vérité est « le
  témoin n'a pas tourné ».
- ⚠⚠⚠ **La mesure a tourné SEPT HEURES sans rien imprimer**, et il a fallu chronométrer une sonde
  pour savoir s'il fallait l'attendre ou la tuer. Une mesure qui coûte des heures et se tait oblige
  à décider sans donnée, ce que ce dépôt refuse partout ailleurs. Les trois mesures longues
  impriment désormais une ligne par bande avec une fin estimée, **sur stderr** — jamais sur stdout,
  qui peut être redirigé ou lu par un autre programme.

##### ⚠ Ce que la tranche ne dit pas

- **Deux pas ne sont pas cent vingt.** Le graal demande 31 spires ; ceci mesure la **pente**, et
  elle est **censurée par le haut**. Relever le plafond est la marche suivante, et son coût est
  chiffré : ~15 s par cellule et par pas supplémentaire.
- ⚠ Le marcheur part d'une cellule de maillage — il n'en a plus besoin ensuite, mais **il faut
  bien partir de quelque part**, et ce bit-là reste de la supervision.
- ⚠ La corrélation avec la rupture de continuité (**−0,167**) est **trop faible** pour être un
  signal de confiance, et c'est dit plutôt que publié comme tel.

---
##### ⭐⭐⭐ LA DIRECTION QUE LA MATIÈRE MONTRE — l'obliquité est RÉELLE, et le graal gagne son second nombre

> Mesure : `src/nappe/la_direction_que_la_matiere_montre.py` (42 contrôles) →
> `docs/mesures/la_direction_que_la_matiere_montre.json`. Figure :
> `src/figures/figure_la_direction_que_la_matiere_montre.py` (19 contrôles).
> Document : [`101`](101_la_direction_que_la_matiere_montre.md), le 2026-09-09.

![la direction que la matière montre](images/101_la_direction_que_la_matiere_montre.png)

`100` laissait **deux lectures** indistinguables dans le maillage : soit la matière est réellement
oblique au rayon et le maillage la suit, soit c'est le **maillage** qui est oblique à la matière —
c'est-à-dire que la surface tracée par les humains ne repose pas sur une feuille. Seule la matière
pouvait trancher, et le **tenseur de structure** du volume fin le fait sans aucun maillage.

| | mesuré |
|---|---:|
| angle de la matière au **maillage** | **13,32°** |
| angle de la matière au **rayon** | **34,59°** |
| ce que `100` lisait sur le maillage seul | **34,06°** |
| part de cellules orientées | **0,636** |
| planarité médiane (contre 0,3365 au bruit pur) | **0,685** |

> ⭐⭐⭐ **La matière suit le maillage.** L'obliquité est donc une propriété de la **matière**, et
> le recoupement est le fait qui porte : **34,59°** contre **34,06°**, par deux instruments qui ne
> partagent ni les données ni le principe.

⚠⚠ **Et la nuance sur le référent humain compte** : le maillage est sur la matière en
**orientation**, à treize degrés — alors que `97` a mesuré qu'il se trompe de plus d'une
demi-feuille en **identité**. Deux pannes différentes, une seule fatale.

##### ⭐⭐⭐ Un axe décalé est réfuté par sa signature en 1/r

`90` a mesuré que l'axe **dérive de 12,6 mm**, donc l'hypothèse n'était pas farfelue — mais elle
prédit `arctan(d/r)`, et cette forme-là est falsifiable.

| | valeur |
|---|---:|
| décalage qui explique le **cœur** (4,1 mm, 35,2° mesurés) | **2,87 mm** |
| ... prédit au bord | **6,9°** pour **24,0°** mesurés |
| décalage qui explique le **bord** (23,8 mm, 24,0° mesurés) | **10,61 mm** |
| ... prédit au cœur | **69,0°** pour **35,2°** mesurés |
| résidu du modèle d'axe (1 paramètre) | **12,2°** |
| résidu du modèle constant (1 paramètre) | **8,7°** |

⭐ **Et le verdict sait dire oui**, ce qui est la condition pour que son « non » veuille dire
quelque chose : sur un jeu fabriqué à `d = 5 mm` il retrouve **5,0 mm** et conclut que l'axe
explique ; sur des angles constants, il conclut que non.

##### ⛔⛔ La planarité est réfutée comme juge, et la garde qui la remplace n'a pas de modèle nul

| σ | gradient du bruit / voxel | angle lu | planarité |
|---:|---:|---:|---:|
| 0 | 0,0 | 0,02° | 1,000 |
| 8 | 11,3 | 1,74° | 0,370 |
| 15 | 21,2 | **7,51°** | **0,345** |

Le gradient du **signal** par voxel vaut **3,49**, celui du **bruit** **21,2** à σ = 15 : le bruit
domine d'un facteur **six**, et la direction reste juste — parce qu'un bruit isotrope s'annule dans
la **moyenne** des produits extérieurs sans s'annuler dans leur **rapport**.

> ⛔ Fermer sur la planarité aurait donc été **une garde qui supprime ce qu'elle doit laisser
> passer** — le péché de `97`. Elle est publiée, mais comme mesure de contraste.

⭐ La garde retenue est l'**accord des deux moitiés disjointes** du cube : si la direction est
réelle les deux s'accordent, sinon non. Elle se calibre elle-même.

##### ⚠⚠⚠ Et la garde elle-même MENTAIT avant correction

`np.gradient` prend des différences **unilatérales** sur les plans extrêmes de chaque axe, de
variance **quatre fois** celle d'une différence centrée. Couper le cube en deux crée donc un
nouveau bord en z et biaise les **deux** moitiés vers z.

> ⚠ **Sur du bruit pur, elles s'accordaient à 10,4°** au lieu des **~60°** que deux directions au
> hasard donnent en trois dimensions. La garde paraissait stricte tout en laissant passer du bruit,
> et la direction de la matière aurait été tirée vers z.

Plans de bord jetés, le nul remonte à **62,03°** et la barre devient **8,88°** (p1 du bruit pur).
⚠ La taille du cube est **dérivée** : à demi = 10 l'empilement bruité ne passe pas (40,1° contre
15,5), à demi = 20 il passe (**3,46°** contre 10,06).

##### ⚠⚠ La condition qui rend la confrontation possible, mesurée

L'angle du maillage vit à **45,532 µm**, la direction de la matière à **2,4 µm**. Une
transformation qui cisaillerait ne conserverait pas les angles, et l'écart serait **silencieux**.
Mesure : conditionnement **1,0075**, défaut **0,301°**.

⚠ Et une **direction** ne se transporte pas comme un point — la translation ne s'y applique pas.
`appliquer_direction` vit à côté d'`appliquer`, dans le seul endroit qui connaît l'inversion
d'axes : passer une direction à `appliquer` ajouterait le décalage de 5000 voxels de la matrice et
rendrait un vecteur pointant vers un coin du volume, parfaitement fini et parfaitement faux.

##### ⭐⭐ Un signal pour le graal, et son confondant retiré

| | brut | à rayon tenu |
|---|---:|---:|
| part orientée contre la rupture | **+0,581** | **+0,452** |
| écart maillage/matière contre la rupture | +0,078 | −0,366 |
| part orientée contre le rayon | **+0,421** | |
| rupture contre le rayon | **+0,815** | |

> ⭐⭐ **La direction survit là où le pas ne survit pas** : la matière donne une direction sur
> **64 %** des cellules, **plus souvent au bord**, là où `99` perdait la périodicité (0,54
> d'utilisable). Avec le **pas** de `99` et la **direction** d'ici, un automate a les deux nombres
> qu'il faut pour franchir une feuille sans humain.

⛔ **Et ce qui n'est pas un signal est dit** : l'écart du maillage à la matière ne prédit **pas** la
rupture (+0,078 brut, −0,366 à rayon tenu sur 28 bandes). Faible et de signe instable.

⛔ **Un faux zéro attrapé pendant la réagrégation** : les corrélations sortaient à **+0,000** parce
que la continuité n'était pas jointe, et « +0,000 » se lit *rien ne corrèle* au lieu de *la donnée
est absente*. Une corrélation sans donnée est désormais **déclarée absente**. C'est le même zéro
que le dépôt a déjà payé sous la forme d'un compteur que personne ne remplissait.

##### ⚠⚠ Ce que la tranche ne dit pas

- **Pourquoi la surface est oblique n'est pas tranché** — écrasement, cône réel, ou propriété du
  traçage. Le fait est confirmé par deux instruments indépendants ; sa cause non.
- **L'écart de pas de `99` reste inexpliqué** : l'obliquité est réelle sans l'expliquer, puisque le
  pas ne dépend pas de la direction.
- ⚠ Le tenseur lit une orientation **locale** (98,4 µm) : il dit *comment la feuille est posée*, pas
  *quelle* feuille. Il ne remplace donc pas à lui seul l'humain qui corrige l'**identité**, qui est
  la panne mesurée par `97`.

---
##### ⛔⛔⛔ LA NORMALE N'EST PAS LE RAYON — l'item A bis, et l'explication tombe

> Mesure : `src/nappe/la_normale_nest_pas_le_rayon.py` (30 contrôles) →
> `docs/mesures/la_normale_nest_pas_le_rayon.json`. Figure :
> `src/figures/figure_la_normale_nest_pas_le_rayon.py` (20 contrôles).
> Document : [`100`](100_la_normale_nest_pas_le_rayon.md), le 2026-09-09.

![la normale n'est pas le rayon](images/100_la_normale_nest_pas_le_rayon.png)

`99` laissait **21 % d'écart inexpliqué** entre le pas de la matière (198,9 µm) et celui des
transferts humains (`91`, 164 µm). Une explication évidente se présentait : si le rayon n'est pas
perpendiculaire à l'empilement, la distance radiale entre deux feuilles vaut $p / \cos\theta$.
Et l'accord numérique était **stupéfiant** — `1/cos` médian **1,212** contre un rapport observé
198,9 / 164,0 = **1,213**.

> ⚠⚠⚠ **C'est exactement la forme du piège que `94` a enregistré avec la sagitta.** Rien n'a été
> publié avant d'avoir lancé le test qui tranche.

| | mesuré |
|---|---:|
| rapport pas radial / pas normal, médiane (28 bandes) | **1,018** |
| son étendue | 0,84 à 1,333 |
| ce que l'obliquité prédirait (`1/cos`, médiane) | **1,184** |
| écart du rapport à **1** | **0,083** |
| écart du rapport à **1/cos** | **0,16** |
| corrélation du rapport contre `1/cos` | **+0,153** |

> ⛔ **L'hypothèse est réfutée deux fois, et les deux verdicts sont indépendants.** Le rapport est
> **deux fois** plus proche de 1 que de `1/cos` ; et la **dépendance** que l'hypothèse prédit —
> le rapport suit `1/cos` d'une bande à l'autre — n'existe pas non plus. Comparer deux médianes
> peut rater un effet noyé dans la dispersion, donc il fallait tester la pente séparément.

##### ⭐⭐⭐ Mais le test laisse un fait plus lourd que ce qu'il réfute

Sur une spirale d'Archimède, la feuille n'est inclinée sur le rayon que de
$\arctan(p / 2\pi r)$, soit **0,07 à 0,39°** sur ce fragment. Or la normale du maillage en est à
**34,06°** — **378 fois** plus.

| | mesuré |
|---|---:|
| angle de la normale de la **grille** au rayon | **34,06°** |
| angle de la normale par **ACP** au rayon | **33,59°** |
| écart entre les deux estimateurs | **1,59°** |
| part hors du plan (feuilles **coniques**) | **14,62°** |
| part dans le plan (section non **circulaire**) | **24,04°** |
| corrélation de l'angle contre le rayon | **−0,549** |

⭐⭐ **Et ce n'est pas l'estimateur.** La normale par **ACP** — plus petit vecteur propre de la
covariance des 30 voisins, donc **indépendante de la grille** — s'accorde à **1,59°** près. Deux
estimateurs sans hypothèse commune s'accordent, donc l'obliquité est dans la **matière tracée**.
⚠ Fixture : sur un plan échantillonné **8× anisotrope** — le cas réel, `97` a mesuré des rangs à
~800 µm pour des colonnes à ~100 — l'ACP rend la normale du plan à **0,0000°**.

##### ⚠⚠ Bruit ou structure ? Le contrôle de `96`, appliqué à une direction

| voisins de l'ACP | 10 | 30 | 100 | 300 | 1000 |
|---|---:|---:|---:|---:|---:|
| angle médian | **35,78°** | 33,59° | 30,14° | 26,62° | **21,22°** |

⭐ **Les deux moitiés sont publiées ensemble.** L'angle **décroît**, donc une part est de la
rugosité locale ; mais il **ne converge pas vers zéro** — à mille voisins il reste **236 fois** la
prédiction. Publier la décroissance seule laisserait croire que tout s'efface.

##### ⭐⭐⭐ Le contrôle qui rend ce résultat NÉGATIF lisible

> **Un test qui ne voit rien est indiscernable d'un test aveugle.**

`empilement_oblique` fabrique une pile de feuilles planes dont l'angle **et** l'espacement vrai
sont connus.

| empilement fabriqué | angle mesuré | pas normal lu | rapport lu | `1/cos` attendu |
|---|---:|---:|---:|---:|
| θ = 0° | **0,00°** | 181,7 µm | **1,000** | 1,000 |
| θ = 35° | **35,00°** | 181,7 µm | **1,238** | **1,221** |

⚠⚠ **Et la fixture a d'abord ÉCHOUÉ, pour une raison qui valait d'être écrite.** Avec un rayon de
départ rond (10 mm) et un pas de 173 µm, la cellule tombe à la **phase 0,80** d'une période — ni
sur une feuille, ni dans un interstice — donc **aucune** des deux polarités du gabarit ne peut
correspondre, et la recherche rend **242 µm** pour 173 injectés. *Un contrôle doit poser sa cellule
là où la matière la poserait.*

##### ⚠⚠⚠ Ce que cela corrige dans `98`, et ce qui sauve sa mesure

La docstring de `combien_dinterstices_traverses.segments` affirmait *« le segment est radial et à z
constant, **donc** il traverse l'empilement perpendiculairement »*. La seconde moitié est mesurée
**fausse** : le segment coupe l'empilement de biais, de 34°.

> ⭐⭐⭐ **Ce qui sauve la mesure de `98` n'est pas ce qui était écrit**, c'est l'autre résultat de
> ce fichier — le pas ignore la direction. Pour une raison qui **n'est pas** celle que la docstring
> donnait, et qui reste **inexpliquée**. La correction est faite sur place, avec sa mesure.

##### ⭐⭐⭐ Deux gardes de figure neuves, et elles ont mordu tout de suite

La docstring de `textes_debordants` nommait elle-même son angle mort : *« elle laisse passer un
texte qui déborde d'un panneau vers son voisin »*. Il est refermé dans le module **commun**, pas
dans cette figure seule.

- **`textes_hors_cadre`** — un texte qui tient dans la **toile** en débordant de son **panneau**,
  où il recouvre ce que le voisin dit. Il a attrapé **deux** légendes d'axe.
- **`textes_qui_se_recouvrent`** — un texte parfaitement placé mais **écrit par-dessus** un autre,
  donc illisible. Il a attrapé **trois** paires, dont la légende de série du panneau A que l'œil
  avait vue avant la garde. ⚠ Marge à **zéro** volontairement : un chevauchement d'un pixel est un
  chevauchement, et une marge choisie pour que la figure du jour passe serait un seuil réglé sur ce
  qui passe.

⭐ **Et le panneau C était illisible en barres** — 28 bandes × 2 barres se recouvraient. Refait en
**nuage** (rapport observé contre `1/cos`), avec les **deux** hypothèses tracées : la diagonale
rouge de l'obliquité et l'horizontale verte de l'indépendance. Sans la diagonale, l'horizontale
n'aurait été qu'une référence et la figure n'aurait rien opposé.

##### ⚠⚠ Ce que la tranche ne dit pas

- **L'écart de `99` reste inexpliqué** : un candidat est éliminé, pas remplacé. **A bis** reste
  ouvert, avec une piste de moins.
- **Pourquoi la surface est oblique n'est pas tranché** — écrasement, cône réel, ou propriété du
  traçage humain. Le fait est mesuré et confirmé ; sa cause non.
- Le plateau à **21,22°** est une **borne inférieure** sur ce qui est réel, pas une mesure de la
  seule structure.

⭐ **Et `--reagreger` sépare ce qui est MESURÉ de ce qui en est DÉRIVÉ** : les pas par bande sont
la mesure, les verdicts n'en sont qu'une lecture. Ajouter une quantité dérivée ne doit pas coûter
une demi-heure de lecture réseau — et le contrôle asserte que la réagrégation laisse les lignes par
bande **intactes**, sinon un recalcul deviendrait une nouvelle mesure sans que rien ne le dise.
⚠ Le verdict est aussi testé **dans l'autre sens** : sur une fixture dont le rapport **suit**
`1/cos`, il doit dire que l'obliquité explique — un verdict qui répond « réfuté » quoi qu'on lui
donne ne trancherait rien.

---
##### ⭐⭐⭐ LE PAS QUE LA MATIÈRE MONTRE — `98` cesse d'auditer et se met à décider

> Mesure : `src/nappe/le_pas_que_la_matiere_montre.py` (22 contrôles) →
> `docs/mesures/le_pas_que_la_matiere_montre.json`. Figure :
> `src/figures/figure_le_pas_que_la_matiere_montre.py` (16 contrôles).
> Document : [`99`](99_le_pas_que_la_matiere_montre.md), le 2026-09-09.

![le pas que la matière montre](images/99_le_pas_que_la_matiere_montre.png)

La tranche du dessous **audite** : elle vérifie un pas qu'on lui donne. Un automate a besoin de
l'inverse — qu'on lui **dise** le pas. Le même filtre le fait en **balayant** la distance.
⚠ La dégénérescence est levée en fixant **k = 1** : un segment de `2p` traversé par deux
interstices est indiscernable d'un segment de `p` traversé par un.

| tiers | utilisable | butée | pas µm | / nominal | > 10 % | continuité |
|---|---:|---:|---:|---:|---:|---:|
| cœur (9) | **0,750** | 0,142 | **198,9** | 1,15 | 0,837 | ×1,7 |
| milieu (9) | 0,742 | 0,100 | 198,9 | 1,15 | 0,811 | ×5,9 |
| bord (10) | **0,542** | 0,117 | **214,05** | 1,24 | 0,824 | ×31,0 |

⭐⭐ **La part de cellules où la matière répond corrèle à −0,845 avec la rupture** — le signal au
bon signe **le plus fort de toute la campagne**, et il est au niveau de la **bande**, donc
utilisable pour dire où un automate doit ralentir.

⭐ **Et le pas montré n'est pas le nominal** : 198,9 à 214,05 µm contre **173**, avec plus de
**81 %** des cellules à plus d'un dixième. Un pas constant est donc faux **quatre fois sur cinq**.

##### ⛔⛔⛔ Le premier résultat était un ARTEFACT, et seul le nul pouvait le montrer

La recherche rendait un pas médian de **147 µm** sur le vrai volume. Contrôle : la **même**
recherche sur du **bruit pur** rendait **147 µm** aussi.

> ⭐ **Le « pas que la matière montre » était donc indiscernable du biais de la recherche.**

Cause chiffrée : un segment court rééchantillonné sur le même nombre de points est
**sur-échantillonné**, donc plus lisse, donc mieux corrélé — le nul passe de **0,1582** au plus
court à **0,0925** au plus long, soit **×1,71**.

> ⭐⭐⭐ **Un modèle nul doit s'appliquer à CHAQUE quantité qu'une recherche rapporte, pas
> seulement à sa confiance.** Le nul du **score** existait et était juste ; celui de la **longueur
> choisie** manquait, et c'est là que vivait l'artefact.

Après calibration par candidat, la même recherche sur du bruit pur choisit **207,6 µm** pour une
fenêtre centrée à 216, avec un histogramme quasi plat.

##### ⚠⚠⚠ Et une seconde erreur de nul, corrigée avant celle-là

La barre comparait le **maximum sur 62 essais** (31 candidats × 2 polarités) au nul d'**un seul**
test — l'erreur des comparaisons multiples, qui rend la mesure **incapable d'échouer** : la part
lue sautait à **0,98**.

| barre | valeur |
|---|---:|
| nul d'un seul essai (`98`) | 0,3311 |
| nul du balayage, non calibré | 0,512 |
| **nul du balayage, calibré** | **4,357** (écarts-types) |

⚠ Les trois sont publiées, parce que leur **écart** montre l'ampleur de chaque correction.

##### ⭐⭐⭐ Le contrôle qui décide si la longueur est une mesure

La distribution des longueurs retenues est confrontée à celle que le **même** balayage retient sur
du **bruit pur**, au-dessus de la **même** barre et avec le même rejet des butées :
**Kolmogorov-Smirnov D = 0,603, p = 1,41·10⁻⁵**, médiane **198,9 µm** contre **276,8** au nul, et
la barre ne laisse passer que **1,03 %** du bruit.

⚠⚠ **Ce que ça ne dit pas** : le pas montré dépasse aussi celui de `91` sur les transferts humains
(164 µm) et celui de l'atlas (182,4), de 9 à 21 %. `97` a établi que le maillage humain n'a pas de
valeur unique, donc un désaccord est attendu — mais son **ampleur n'est pas expliquée ici**.

---
##### ⭐⭐⭐ LE PREMIER CRITÈRE DONT LE SEUIL VIENT DE LA MATIÈRE — et il est faible là où il compte

> Mesure : `src/nappe/combien_dinterstices_traverses.py` (32 contrôles) →
> `docs/mesures/combien_dinterstices_traverses.json`. Figure :
> `src/figures/figure_combien_dinterstices_traverses.py` (17 contrôles).
> Document : [`98`](98_combien_dinterstices_traverses.md), le 2026-09-09.

![combien d'interstices traversés](images/98_combien_dinterstices_traverses.png)

La tranche du dessous a mesuré qu'**aucun signal calibré contre un maillage humain ne peut
l'être**. Il fallait donc un critère que la **matière** tranche, et il s'énonce en une phrase :
entre une cellule et le point situé un pas de feuille plus loin, le profil doit valoir
*brillant – sombre – brillant*, soit **un** interstice. Zéro voudrait dire qu'on est revenu sur la
même feuille, deux qu'on en a sauté une. Aucun maillage, aucun oracle, aucune supervision.

| tiers | matière répond | accord | 1 interstice | 2 ou + | sur la feuille | continuité |
|---|---:|---:|---:|---:|---:|---:|
| cœur (9) | 0,740 | 0,457 | **0,557** | 0,443 | 0,487 | ×1,7 |
| milieu (9) | 0,690 | 0,429 | 0,536 | 0,464 | 0,474 | ×5,9 |
| bord (10) | **0,540** | **0,353** | **0,518** | 0,482 | 0,506 | ×31,0 |

⭐⭐ **Le signe est correct** : −0,354 avec le rayon, **−0,411** avec la rupture. La part de
transferts que la matière confirme **baisse là où la continuité casse**. C'est le second signal
après la fermeture à avoir le bon signe, et le **premier dont le seuil soit matériel**.

⚠⚠ **Et il est faible là où il compte** : au bord l'accord médian vaut **0,353** pour une barre de
**0,3311**, et la matière ne répond que **54 %** du temps contre 74 % au cœur. Cohérent avec `94` —
au bord le maillage humain a **enjambé** ce qu'il ne pouvait pas suivre, donc il n'y a pas toujours
de matière à interroger.

##### ⭐⭐⭐ La question de l'auteur, et pourquoi la réponse n'est pas d'adapter le seuil

*« Il faut être adaptatif par rapport au rouleau testé, non ? »* — oui, et la mesure rend la
question plus forte : dans **une seule bande du bord**, l'étendue du profil varie d'un facteur
**146** (p10 = 0, p90 = 146 niveaux), et de **2,4** au milieu. Un seuil absolu de « sombre » est
donc sans espoir, et une constante **par rouleau** serait déjà un paramètre ajusté.

> ⭐ **Mais la bonne réponse n'est pas d'adapter le seuil : c'est de choisir une quantité qui n'en
> a pas besoin.** Une corrélation normalisée est invariante en amplitude **et** en décalage.

⚠ Asséré plutôt que supposé : mettre signal **et** bruit à l'échelle ×0,05 puis ×50 laisse le score
**identique au bit près**. Et le seuil vient d'un **modèle nul fabriqué** — le p99 de ce qu'un
bruit blanc atteint, **0,3311**, calculable sans regarder le rouleau — dont l'indépendance en σ
(0,1482 · 0,1502 · 0,1497 pour σ = 2, 10, 40) est le contrôle de l'invariance d'échelle : un nul
qui dépendrait du bruit trahirait un paramètre caché.

##### ⭐⭐ Un second verdict gratuit, et il fallait le distinguer d'un tirage

Le gabarit existe en deux polarités, et la cellule part **sur** une feuille **une fois sur deux**
(0,487 · 0,474 · 0,506). ⚠⚠⚠ Ce nombre a **deux lectures opposées** : soit le maillage est
réellement dans un interstice la moitié du temps, soit les deux gabarits sont à égalité et le choix
est un **tirage**. Seule la **marge** les sépare — **0,376** au cœur, comparable à l'accord
lui-même (0,457), et **81 %** des profils lus l'ont franche.

> ⭐ **L'instrument tranche donc, et ce qu'il tranche est que la moitié des cellules du maillage
> humain partent d'un interstice et non d'une feuille.**

##### ⛔⛔ Le compteur de minima, réfuté et gardé — et son échec se généralise

| proéminence | faux positifs (bruit pur) | détection (un interstice réel) |
|---:|---:|---:|
| ×3 | 0,988 | 0,265 |
| ×4 | 0,769 | 0,285 |
| ×6 | 0,087 | 0,060 |

Lisser fait monter la détection à **0,95** sans rien changer aux faux positifs (0,6 à 1,0).

> ⭐⭐⭐ **Une proéminence exprimée en unités du bruit propre au profil est invariante d'échelle,
> donc lisser abaisse le bruit ET le seuil ensemble.** La discrimination ne peut pas venir de la
> **profondeur** — elle vient de la **forme**.

⚠ Et son estimateur de bruit était faux : une différence **première** lit aussi la **pente** du
signal cherché (6,9 niveaux pour une amplitude de 40). Corrigé en différence **seconde**,
insensible à une pente (0,3 niveau).

##### ⚠⚠⚠ Trois défauts payés, tous gardés

**Les gabarits étaient de signe INVERSÉ** — `−cos(2π(k+1)t)` commence et finit sombre, alors qu'un
segment partant du centre d'une feuille doit commencer brillant. Trouvé **en lisant les comptes** :
40 % des profils réels s'appariaient à un gabarit dont la lecture correcte est « la cellule est
dans un interstice », et je publiais ce compte sous le nom « zéro interstice ». **Deux états sous
une seule étiquette.**

**Mon test de platitude ne pouvait pas voir le cas dégénéré** : un profil **exactement constant** a
une étendue nulle *et* un bruit nul, donc `0 < 4×0` est faux, et il ressortait « non muet » avec un
compte de zéro — ce qui se lit « même feuille » au lieu de « on ne sait pas ». Une mesure satisfaite
par l'absence de ce qu'elle mesure.

**Et deux contrôles à moi mal formulés**, corrigés plutôt que contournés : j'affirmais que le score
ne dépend pas de l'**amplitude** à bruit fixe — faux, à SNR 3 il baisse légitimement, l'invariance
portant sur l'**échelle** ; et j'exigeais une marge de polarité supérieure à **1,0**, un nombre pris
au hasard que la fixture rendait à 0,952, remplacé par un rapport au **nul**.

⚠ « Zéro interstice » n'est **pas** exprimable en gabarit : un segment restant sur la même feuille
est plat, donc de norme nulle après centrage. C'est le cas **sans accord**, et le refus est
explicite plutôt que silencieux.

---
##### ⭐⭐⭐ DEUX HUMAINS SUR LA MÊME MATIÈRE DIVERGENT DE PLUS D'UNE DEMI-FEUILLE, PARTOUT

> Mesure : `src/nappe/deux_humains_sur_la_meme_matiere.py` (18 contrôles) →
> `docs/mesures/deux_humains_sur_la_meme_matiere.json`. Figure :
> `src/figures/figure_deux_humains_sur_la_meme_matiere.py` (15 contrôles).
> Document : [`97`](97_deux_humains_sur_la_meme_matiere.md), le 2026-09-09.

![deux humains sur la même matière](images/97_deux_humains_sur_la_meme_matiere.png)

La tranche du dessous a nommé ce qui manquait — un **référent** — et le dépôt en télécharge un
depuis le début sans l'avoir employé : chaque bande existe en **deux révisions**, soit deux tracés
humains **indépendants** de la même matière. Là où les deux s'accordent, la matière a dicté la
réponse ; là où ils divergent, au moins l'un des deux se trompe, et **aucun oracle n'est requis**.

| tiers | au plan local | au plus proche voisin ⛔ | hors ½ | > 1 feuille | continuité |
|---|---:|---:|---:|---:|---:|
| cœur (9) | **121,7 µm** | 270,8 µm | 0,629 | 0,339 | ×1,7 |
| milieu (9) | 110,9 µm | 276,9 µm | 0,622 | 0,303 | ×5,9 |
| bord (10) | **106,6 µm** | 315,4 µm | 0,609 | 0,301 | ×31,0 |

⭐⭐⭐ **Pour une demi-feuille de 82 à 91 µm** (`91`), les deux humains sont donc à **plus d'une
demi-feuille** l'un de l'autre, et **34 %** des points à plus d'une feuille **entière**. ⭐ Et c'est
**PLAT** (corrélation avec le rayon **+0,081**) : ce n'est pas un problème de bord, c'est partout —
ce qui en fait un **plancher** plutôt qu'une région à traiter à part.

⚠ **Aucune translation systématique** : restreint au recouvrement en z, le vecteur moyen de A vers B
tombe à **8–38 µm**. Le désaccord est réel et local, pas un décalage de convention.

⛔ **Et ce référent ne calibre PAS la fermeture de la tranche du dessous** : le désaccord ne suit ni
le rayon (+0,081), ni la rupture (−0,097), ni la fermeture (**+0,079**). Là où les deux humains
divergent n'est donc pas là où la fermeture échoue.

##### ⛔⛔ L'estimateur réfuté, gardé — et c'est le facteur qui compte

Au plus proche voisin le désaccord rend **270 à 315 µm** contre **107 à 122** au plan local, soit un
facteur **2,2 à 3,0**. Les rangs de l'ancienne révision sont espacés d'environ **800 µm**, donc un
point à mi-chemin entre deux rangs en est loin **même si les deux surfaces coïncident exactement** —
et la fixture le montre en rendant une distance non nulle sur deux surfaces **identiques**.

> ⭐ **Publier ce nombre aurait été publier une limite de GRILLE comme une limite de MATIÈRE**, le
> péché nº 1 de ce dépôt.

##### ⚠⚠⚠ Une garde à moi qui supprimait ce qu'elle devait laisser mesurer

Mon critère de bord — *« mes voisins sont-ils tous du même côté ? »* — était d'abord mesuré dans
l'**espace**, où il mélange deux choses : être au **bord** d'une couverture, et être **loin** de la
surface. Mesure du défaut : sur deux plans séparés de 2 avec des voisins à 2,4, le rapport **ne
descendait jamais sous 0,354** — donc appliqué au réel il aurait écarté **exactement** les points où
les deux humains divergent le plus.

> **Une garde qui supprime ce qu'elle doit laisser mesurer est pire qu'aucune garde.**

Mesuré dans le **plan tangent**, il ne voit plus que le bord, et le désaccord publié **double** : de
53 à **122 µm**. ⚠ Le critère est **borné dans [0, 1]** par construction et son défaut est **mesuré
sur fixture** — 0,13 à l'intérieur, 0,49 sur la bordure, donc 0,35 entre les deux — avec le balayage
publié.

⚠⚠ Et le **confondant de couverture** est traité avant tout le reste, comme `85` l'avait déjà payé :
l'ancienne révision ne couvre que **65 %** de l'étendue en z de la récente (119 rangs contre 184), et
sans restriction le vecteur moyen valait 5918 µm dominé par 5567 en z — c'est-à-dire qu'on mesurait
la couverture.

##### ⭐⭐⭐ Ce que ça change pour le graal, et c'est plus lourd que la calibration cherchée

Le prix demande d'automatiser un travail dont **l'état de l'art ne reproduit pas sa propre sortie à
une feuille près**.

> ⛔ **La cible d'un automate ne peut donc pas être « égaler le maillage humain » — cette cible n'a
> pas de valeur unique.** Elle doit être un critère que la **matière** tranche, pas un maillage.

⭐ Et ça donne un sens neuf aux trois échecs précédents : le pli, la pose sur la matière et la
fermeture cherchaient tous un signal qui prédise l'écart **à un maillage humain**, ou calibré
**contre** lui. Les trois mesuraient contre une règle dont on sait maintenant qu'elle bouge de plus
d'une demi-feuille selon qui la tient.

---
##### ⭐⭐⭐ LE PREMIER SIGNAL DONT LE SIGNE EST LE BON — et le plancher qui l'empêche de certifier

> Mesure : `src/nappe/la_fermeture_dun_tour.py` (28 contrôles) →
> `docs/mesures/la_fermeture_dun_tour.json`. Figure :
> `src/figures/figure_la_fermeture_dun_tour.py` (15 contrôles).
> Document : [`96`](96_la_fermeture_dun_tour.md), le 2026-09-09.

![la fermeture d'un tour](images/96_la_fermeture_dun_tour.png)

Les deux tranches du dessous ont échoué de la **même** façon, et le motif est établi : au bord,
l'humain qui ne peut pas suivre la vraie feuille en trace une autre, **proprement**. Ce qui échoue
n'est donc pas la **qualité locale** mais l'**identité** de la feuille. La **fermeture** est un
énoncé d'identité : partir d'une cellule, faire **un tour complet**, et le rayon doit avoir monté
d'**un** pas de feuille — zéro voudrait dire qu'on est revenu sur la même, deux qu'on en a sauté
une. Aucune supervision n'entre.

| tiers | fermeture | dispersion | hors ½ | sautée | continuité |
|---|---:|---:|---:|---:|---:|
| cœur (9) | 0,998 | 2,30 | **0,621** | 0,348 | ×1,7 |
| milieu (9) | 1,022 | 2,73 | 0,710 | 0,376 | ×5,9 |
| bord (10) | 0,952 | 4,65 | **0,804** | 0,397 | **×31,0** |

⭐⭐⭐ **LE SIGNE EST ENFIN LE BON** : **+0,858** avec le rayon et **+0,822** avec la rupture, là où
le pli donnait −0,825 et la pose sur la matière −0,694. C'est le premier renversement de signe de la
campagne. ⭐ Et le pas est juste partout (0,95 à 1,02 feuille) : ce n'est pas le pas qui manque,
c'est la fermeture **cellule par cellule**.

⚠⚠⚠ **ET ELLE NE CERTIFIE POURTANT AUCUNE CELLULE** : 0,621 au **cœur**, là où la continuité est
intacte (×1,7). Un signal qui marque trois cellules sur cinq dans la région propre ne peut rien
garantir. Reste à savoir si c'est du **bruit**, qui se moyennerait, ou de la **structure**.

##### ⭐⭐⭐ Bruit ou structure ? Le balayage de fenêtre répond sans aucun seuil

| fenêtre | réel (5 bandes) | fixture bruit seul | fixture + saut |
|---:|---:|---:|---:|
| 1 tour | **0,556** | 0,312 | 0,398 |
| 2 tours | 0,530 | 0,061 | 0,211 |
| 3 tours | 0,517 | **0,004** | 0,096 |
| 5 tours | **0,495** | 0,000 | ⚠ 0,002 |

⭐⭐⭐ **Le réel est PLAT là où le bruit s'effondre** : allonger la fenêtre ×5 fait tomber le réel de
**11 %** quand le même estimateur écrase un bruit blanc à **zéro**. L'irrégularité radiale des
maillages humains n'est donc **pas du bruit**.

⚠⚠ **La colonne à 5 tours de la fixture n'est pas un témoin** : sur une spirale de huit tours, une
fenêtre de cinq n'en laisse que trois de testables et efface l'échelon elle aussi. La plage où le
balayage **discrimine** est 2 à 3 tours. ⚠ Et le corpus borne le remède : les bandes du bord ne
portent que **deux tours**.

⭐⭐⭐ **LA MÉDIANE EST AVEUGLE, LA PART NON**, et seule une fixture pouvait l'établir : sur une
spirale où **une feuille est sautée**, la fermeture médiane reste à **1,000** pendant que la part
hors demi-feuille l'attrape à 0,200, entièrement attribuée à *sautée*. C'est pourquoi la part est
publiée avant la médiane, et pourquoi la pente globale de `91` — qui ajuste une droite sur tout le
rang — ne pouvait pas la voir.

⭐⭐ **Et l'argument qui rend la mesure possible vient de `91` lui-même** : son avertissement dit
qu'une pente sur arc court lit l'ovalité comme une montée (202 µm sur dix tours, **1817 sur un**).
À **exactement 2π** l'oscillation revient sur elle-même, donc la fermeture y est **immune** —
asséré sur fixture, une section ovale à 15 % ne déplace rien.

⚠⚠⚠ **Un obstacle d'échelle interdit la version naïve** : un pas de cellule vaut ~905 µm pour un
pas de feuille de ~173, donc une cellule fait **cinq feuilles** et indexer par colonnes entières ne
peut pas résoudre une feuille. La fermeture est lue en **interpolant** le rang par son angle
déroulé — erreur d'interpolation ≈ **5 µm**, trente-cinq fois sous le pas.

##### ⚠⚠⚠ Deux défauts payés dans cette tranche, tous deux gardés

**Le balayage a dû être refait à sous-ensemble CONSTANT.** Ma première version prenait toutes les
bandes disponibles à chaque fenêtre — 28 à un tour, 5 à cinq — or les cinq qui portent cinq tours
sont les plus **internes**, donc les plus propres : la baisse mesurée était celle du
**sous-ensemble**, pas celle de la fenêtre.

> **C'est la faute que `93` avait déjà payée** en comparant la bande 0 à la bande 7.

⭐ Le confondant retiré rend le fait **plus fort** — 11 % contre les 30 % annoncés — et la forme
confondue est gardée à côté, nommée, parce que les comparer montre l'ampleur du confondant.

**Un défaut de centre trouvé en regardant.** J'indexais le centre d'enroulement **par cellule**, or
`axe_par_tranche` le rend constant par tranche et l'axe dérive de 12,6 mm : deux cellules d'un même
rang enjambant une frontière voyaient des centres écartés de centaines de µm, et l'écart tombait
directement dans la fermeture. Mesure du défaut : **22 % des fermetures sortaient négatives**, c'est
à dire un maillage qui rentrerait vers l'intérieur après un tour entier une fois sur cinq. Centre
désormais **interpolé** en z. ⚠ Un ajustement global comme `91` en est en partie protégé par
moyennage ; une fermeture par tour ne l'est **pas du tout**.

##### ⛔ Ce que ça laisse : la direction est bonne, le RÉFÉRENT manque

La fixture prouve que l'estimateur **sait** détecter une feuille sautée (0,096 contre 0,004 à trois
tours). Ce qui manque n'est donc pas l'instrument mais un **référent** : ces maillages ne ferment
pas eux-mêmes à la demi-feuille près — **62 % des cellules y échouent au cœur** — donc ils ne
peuvent pas servir à calibrer le seuil d'un automate.

> ⭐ **C'est le même plancher que `95` sur un autre axe : l'erreur du référent, pas la mienne.**
> `95` mesurait que la surface publiée n'est pas **sur** la feuille ; `96` mesure qu'elle ne
> **ferme** pas non plus. Une confiance par cellule bâtie sur la fermeture est donc **écrivable et
> non calibrable** avec ce corpus.

---
##### ⛔⛔⛔ LA SURFACE HUMAINE EST MIEUX POSÉE SUR LA FEUILLE LÀ OÙ LE TRANSFERT CASSE

> Mesure : `src/nappe/la_surface_et_la_feuille_par_rayon.py` (26 contrôles) →
> `docs/mesures/la_surface_et_la_feuille_par_rayon.json`. Outils partagés :
> `src/commun/voxel_distant.py` (16 contrôles), `src/commun/transformations_de_volume.py`
> (12 contrôles). Figure : `src/figures/figure_la_surface_et_la_feuille_par_rayon.py`.
> Document : [`95`](95_la_surface_et_la_feuille_par_rayon.md), le 2026-09-09.

![la surface et la feuille par rayon](images/95_la_surface_et_la_feuille_par_rayon.png)

La tranche du dessous a tué le froissement parce qu'il est une propriété du **maillage** ; il
fallait une observable de la **matière**. Le dépôt en avait une — `la_surface_et_la_feuille`, l'écart
entre la spire publiée et le ruban qu'elle suit — mais elle ne couvre `PHercParis4` que par **une
bande**. Étendue aux 28, à 2,4 µm :

| tiers | dispersion | contraste | part au remplissage | continuité |
|---|---:|---:|---:|---:|
| cœur (9) | **20,0 µm** | 107,5 | 0,011 | ×1,7 |
| milieu (9) | 17,1 µm | 108,5 | 0,068 | ×5,9 |
| bord (10) | **13,85 µm** | 114,5 | 0,167 | **×31,0** |

⛔⛔⛔ **La surface est donc MIEUX posée là où le transfert casse** : −0,702 avec le rayon, −0,694
avec la rupture de continuité.

⭐⭐⭐ **CE QUI A RENDU LES 28 BANDES ABORDABLES**, et les deux outils valent au-delà de cette
tranche : les chunks du dépôt sont écrits **sans compression**, donc l'octet d'un voxel est à un
décalage calculable et une requête `Range` suffit — 20,7 Go lus sans rien rapatrier ; et la matrice
`45,532 µm → 2,4 µm` est **publiée** dans `metadata.min.json`. ⚠⚠ Le volume fin n'est pas un
luxe : à 45,532 µm un demi-écart inter-feuilles vaut **deux voxels**, donc y mesurer un décalage de
vingt micromètres publierait une **limite de grille** comme une limite de matière.

⚠ Et la convention de la matrice ne se devine pas : mesurée sur 400 cellules réelles, **+0,412**
pour « matrice sur (x,y,z) puis inversion » contre **+0,073** pour l'autre lecture. Un mauvais
ordre d'axes rend des octets parfaitement valides, pris ailleurs dans le rouleau.

⭐⭐ **LE CONFONDANT EST TRAITÉ PAR TROIS CHEMINS QUI DOIVENT S'ACCORDER.** Le volume est masqué et
la part au remplissage monte à **+0,800** avec le rayon, donc sans la retirer « la surface est mieux
posée au bord » et « le volume s'arrête au bord » seraient la **même observation**.

| chemin | dispersion / rayon | dispersion / continuité |
|---|---:|---:|
| brut | −0,702 | −0,694 |
| corrélation **partielle** | **−0,550** | **−0,533** |
| en **jetant** les bandes rongées (16) | −0,658 | −0,434 |

⭐ Retirer un confondant par une formule et le retirer en jetant les cas concernés sont **deux
gestes différents** : s'ils ne s'accordent pas, c'est la formule qui a tort, parce qu'elle suppose
une relation linéaire que des bandes à 0,2 et 0,4 de remplissage ne respectent pas.

⭐⭐⭐ **Et le seuil n'est pas réglé, c'est vérifiable** : le balayage publié donne **−0,630 ·
−0,658 · −0,646 · −0,738 · −0,753** de 5 % à 30 % de remplissage toléré.

⚠⚠⚠ **Une erreur à moi, gardée.** Ma sonde exploratoire prenait **trois** bandes — cœur, milieu,
`w128-129` — et voyait le contraste tomber de **119 à 11**. Or `w128-129` est l'une des **deux
seules** bandes dont le contraste s'effondre, et celle dont le remplissage est le plus fort (0,385).
Sur les 28, le contraste n'a **aucune relation stable** au rayon (−0,276 brut, +0,356 masque retiré,
signe changeant selon le seuil).

> **Un bord se compte sur le corpus entier, pas sur les bandes qu'on a sondées.**

C'est la faute que `93` avait déjà payée en comparant la bande 0 à la bande 7, réécrite sous une
autre forme.

⚠⚠ **La dispersion ne se lit jamais sans son contraste** : sans relief, le centre de masse d'un
profil de bruit se pose au **milieu** de la fenêtre, donc il disperse peu. Lue seule, la colonne
dirait « la surface est la mieux placée au bord » pour une bande où il n'y a rien à mesurer.

##### ⚠⚠⚠ Un résultat qui bougeait entre deux exécutions du même calcul

Les deux premiers runs ont rendu des médianes par tiers **différentes** (bord 13,85 puis 13,1 µm)
alors que toutes les valeurs par bande étaient identiques : la bande `w110-112` avait **65 cellules
au lieu de 90**, vingt-cinq perdues par coupure réseau passagère, **en silence**.

> **Un nombre publié dont la valeur dépend de l'humeur du réseau n'est pas un résultat.**

Deux remèdes, et il faut les **deux** : les lectures sont **réessayées** — sur les pannes réseau
seulement, jamais sur un code HTTP, qui est une réponse et non une panne — et le compte de cellules
perdues est **publié** par bande et en tête. Un réessai qui échoue quand même laisserait sinon
exactement le même trou muet. Le contrôle est dans la batterie de `voxel_distant` : une panne
réseau doit être réessayée trois fois, un 404 rendu du premier coup.

##### ⭐⭐⭐ ET LE VRAI RÉSULTAT EST LE MOTIF, PAS LA CORRÉLATION

**Deux observables locales indépendantes** — le pli du maillage et la pose sur la matière — disent
toutes deux « plus propre » exactement là où le transfert échoue. Ce n'est plus une coïncidence.

> ⭐⭐⭐ **Au bord, l'humain qui ne peut pas suivre la vraie feuille en trace une autre,
> proprement. Le maillage épouse très bien UNE feuille — simplement pas la bonne.**

⛔⛔ **Donc ce qui échoue au bord n'est pas la QUALITÉ locale mais l'IDENTITÉ de la feuille**, et
une observable locale ne peut pas la voir par construction : elle mesure à quel point on est bien
posé sur ce qu'on suit, jamais si c'est ce qu'il fallait suivre. Un signal de confiance bâti sur
l'une ou l'autre de ces deux familles **classerait l'abandon comme une réussite**. Le signal à
chercher est **topologique**, donc global.

---
##### ⛔⛔⛔ LE FROISSEMENT DÉSIGNE-T-IL OÙ LE TRANSFERT ÉCHOUE ? Non — il désigne l'INVERSE

> Mesure : `src/nappe/le_froissement_mesure_la_rugosite.py` (15 contrôles) →
> `docs/mesures/le_froissement_mesure_la_rugosite.json`. Figure :
> `src/figures/figure_le_froissement_mesure_la_rugosite.py` (16 contrôles).
> Document : [`94`](94_le_froissement_mesure_la_rugosite.md), le 2026-09-09.

![le froissement mesure la rugosité](images/94_le_froissement_mesure_la_rugosite.png)

`93` dit **où** le pas géométrique échoue ; ce qui manque est un signal que le marcheur peut lire
**tout seul**. Le **pli** était le candidat, et il est mesuré prédictif **par cellule** juste en
dessous (« Une cellule peut-elle savoir qu'elle a tort »). Testé sur les 28 bandes humaines de
`PHercParis4`, du cœur au bord :

| tiers | froissement | désalignement | continuité |
|---|---:|---:|---:|
| cœur (9 bandes) | **15,2 µm** | ×1,88 | ×1,7 |
| milieu (9) | 10,1 µm | ×1,80 | ×5,9 |
| bord (10) | **3,8 µm** | ×3,67 | **×31,0** |

⛔⛔⛔ **Il est ANTI-prédictif** : −0,957 avec le rayon, **−0,825** avec la rupture de continuité.
Un marcheur qui s'en servirait signalerait le **cœur**, où tout est propre, et **se tairait au
bord**. ⚠⚠ Normaliser par la sagitta retire le rayon (−0,404) mais **pas le signe** (−0,678).

⭐⭐⭐ **Et ce que le champ mesure est établi par FIXTURE, pas par corrélation.**
`champ_de_froissement` prend la **médiane** d'un voisinage 3×3, donc il est **exactement aveugle à
la courbure lisse** :

| cas | R = 5 mm | R = 20 mm | rapport |
|---|---:|---:|---:|
| cylindre parfait | **0,00 µm** | **0,00 µm** | — |
| + axe courbe (celui que `90` mesure) | **0,00 µm** | **0,00 µm** | — |
| + bruit 5 µm | 7,54 | 6,87 | **×1,10** |
| + bruit 20 µm | 29,10 | 27,06 | ×1,08 |

⭐⭐ **Le verdict devient donc plus fort, pas plus faible.** Le réel tombe de **×5,2** du cœur au
bord là où la rugosité seule n'en donnerait que ×1,1 : les maillages humains sont **cinq fois plus
lisses au bord**. Or un maillage lisse qui porte des **sauts de 30 mm** (`92`) et des spires
**désalignées** (`93`) a **enjambé ce qu'il ne pouvait pas suivre**. **La douceur au bord n'est pas
de la qualité, c'est la signature d'un pontage** — et un signal de confiance bâti dessus
**classerait l'abandon comme une réussite**.

⚠⚠⚠ **Une cause publiée puis rétractée avant d'être committée.** J'avais expliqué la chute en 1/R
par la **sagitta** d'un cercle, `s²/(8R)`, avec un accord frappant : **1,11 en médiane** sur 28
bandes. La fixture la réfute d'un coup — elle prédit **20,2 µm** à R = 5 mm là où le champ rend
**zéro**.

> ⭐ **Une corrélation sur vingt-huit points ne vaut pas une fixture dont on connaît la réponse.**

⚠ Elle est **gardée** dans le code, réfutée et nommée : un accord de cet ordre réapparaîtra à qui
refera la mesure, et le trouver sans trouver sa réfutation conduirait à le republier.

⚠⚠ **Avertissement de niveau, qui ne rétracte pas la tranche du dessous.** Elle compare des
**cellules** à rayon presque constant, celle-ci compare des **bandes** à travers les rayons — et
elle bornait **déjà** sa portée (*« il l'est là où il y a des plis »*). ⭐ Une marche de 31 spires
change le rayon d'un **facteur six**, donc tout signal de confiance doit être **vérifié à travers
les rayons**, ou il classera par rayon en croyant classer par difficulté.

⚠⚠ **Deux angles morts d'outillage attrapés ici.** (1) La revendication porteuse **n'était pas
publiée** — la fixture ne vivait que dans `verifier()`, donc aucun document ne pouvait citer ses
nombres ; `ce_que_le_champ_voit()` sert maintenant la mesure, la batterie et la figure. (2) **Le
garde de largeur ne lisait que la prose du bas**, donc une ligne de **verdict** d'un panneau
pouvait être **coupée à mi-mot** ; `Tracee` retient désormais la **position** avec le texte, et le
contrôle a attrapé **une seconde ligne coupée que l'œil avait laissée passer**.

⚠ **Et une citation inventée, corrigée avant commit** : j'avais attribué « le pli prédit l'erreur
par cellule » à `78`, qui est *Cinq rouleaux publient leur axe*.

---
##### ⭐⭐⭐ UNE CELLULE PEUT-ELLE SAVOIR QU'ELLE A TORT, sans regarder la cible ?

> Mesure : `src/nappe/la_cellule_sait_elle_quelle_a_tort.py` (14 contrôles) →
> `docs/mesures/la_cellule_sait_elle_quelle_a_tort.json`. Figure :
> `src/figures/figure_la_cellule_sait_elle_quelle_a_tort.py` (10 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/la_cellule_sait_elle_quelle_a_tort.py --cote 960 \
>     --json docs/mesures/la_cellule_sait_elle_quelle_a_tort.json
> uv run python src/figures/figure_la_cellule_sait_elle_quelle_a_tort.py \
>     --sortie docs/images/75_la_cellule_sait_elle_quelle_a_tort.png
> ```

⚠⚠⚠ **Pourquoi cette question est celle du BUT, et pourquoi elle est indépendante de toute
amélioration de méthode.** Un dérouleur qui livre une nappe livre aussi, implicitement, la
prétention que **chaque cellule est à sa place**. Si le **PLI** d'une cellule — son écart à la
médiane de ses voisins, observable **sans aucune supervision** — prédit son **ERREUR**, alors un
marcheur aveugle peut publier une **confiance par cellule**. Il ne sait pas où est la vérité, mais
il sait où il se trompe.

![une cellule peut-elle savoir qu'elle a tort](images/75_la_cellule_sait_elle_quelle_a_tort.png)

⚠⚠ **Aucun seuil n'est choisi.** Les cellules sont **classées** par leur pli et la **fraction
gardée** est balayée : la courbe entière est l'objet livré, et le point où l'on se place appartient
à l'auteur. ⚠⚠⚠ Et elle ne veut rien dire sans son **témoin** — garder la moitié d'un échantillon
**au hasard** déplace déjà sa médiane, donc ce qui compte est l'écart entre les deux, à fraction
égale et sur les mêmes cellules.

| écart médian sur les bras (classé − hasard, µm) | 100 % | 90 % | 75 % | 50 % | 35 % | 25 % | 10 % |
|---|---:|---:|---:|---:|---:|---:|---:|
| rien | +0.0 | -5.1 | -5.4 | -0.6 | +1.6 | -0.3 | -1.8 |
| rien_lisse | +0.0 | -1.2 | +1.2 | +3.0 | +7.1 | +5.5 | -0.8 |
| raccroche | +0.0 | -13.2 | -27.9 | -43.2 | -44.6 | -46.6 | -50.3 |

| bras où le pli gagne | 100 % | 90 % | 75 % | 50 % | 35 % | 25 % | 10 % |
|---|---:|---:|---:|---:|---:|---:|---:|
| rien | 0/8 | 7/8 | 8/8 | 5/8 | 4/8 | 4/8 | 5/8 |
| rien_lisse | 0/8 | 6/8 | 1/8 | 3/8 | 3/8 | 3/8 | 4/8 |
| raccroche | 0/8 | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | 7/8 |

> ⚠⚠ **Le pli prédit fortement chez le RACCROCHAGE** — -43.2 µm à moitié gardée, -50.3 à un
> dixième, et il gagne sur **8 bras sur 8**. Il prédit **faiblement** chez le pas normal (-5.4 µm
> à trois quarts) et **pas du tout** chez le pas normal lissé (+7.1 µm, donc **pire** que le
> hasard).

> ⭐⭐ **Et cette dernière ligne est le fait le plus intéressant des trois.** Le lissage retire les
> plis, donc il retire **aussi le signal** qui permettait de savoir où l'on se trompe. La même
> opération qui améliore la nappe **aveugle** le marcheur sur ses propres cellules. C'est un
> arbitrage à connaître, pas un défaut — et il n'apparaît que parce que les deux quantités ont été
> mesurées ensemble.

##### ⭐⭐⭐ Et le seul chiffre actionnable : « prédire » et « SAUVER » sont deux affirmations

Un gain de cinquante micromètres sur une nappe à trois cents en est **encore à trois cents**. Un
bras n'est **SAUVÉ** que s'il était **perdu** à couverture pleine et **passe sous la demi-feuille**
en classant.

| marcheur | bras perdus | sauvés en classant | sauvés au hasard | fraction qui suffit |
|---|---:|---:|---:|---:|
| rien | 4 | **1** | 0 | 90 % |
| rien_lisse | 3 | **0** | 0 | — |
| raccroche | 6 | **1** | 0 | 90 % |

> ⭐⭐⭐ **Le pas normal sauve un bras en jetant les DIX POUR CENT de cellules les plus pliées, et
> le témoin au hasard n'en sauve AUCUN.** À comparer aux **45 %** que garde le marcheur qui refuse
> ses plis à un **seuil** : **classer coûte cinq fois moins de couverture pour le même bras**. Et
> c'est le même bras que le lissage achète — donc les trois voies mènent au bras 5 et aucune ne
> mène au 6.

⚠ **Ce que ça ne dit pas** : que le pli soit une bonne confiance **en général**. Il l'est là où il
y a des plis, et le pas normal lissé en a si peu que son classement fait **pire** que le hasard.
Une confiance par cellule utilisable demandera donc soit une autre observable, soit de ne pas
lisser — et les deux se mesurent.

---
##### ⭐⭐⭐ ET LA SECONDE OBSERVABLE EXISTE : l'OBSCURITÉ prend le relais là où le pli échoue

⚠⚠⚠ **La tranche précédente laissait la question ouverte** : le pli est une confiance utilisable
**là où il y a des plis**, et le pas normal lissé en a si peu que son classement fait **pire** que
le hasard. Il fallait donc une **autre observable**, et la plus physique était à portée : **le
volume au point prédit lui-même**. Une feuille est un **ruban brillant**, donc une cellule qui
atterrit dans un **vide entre deux feuilles** le voit.

> ⚠⚠ **Lire son propre point n'est PAS de la supervision** : la cible n'est jamais consultée. C'est
> exactement ce qu'un vrai dérouleur a en main, et c'est un **seul échantillon** par cellule — pas
> une ligne — donc le coût d'un marcheur qui ne raccroche pas reste proche de celui qui ne lit rien.

⚠⚠ **La convention est que GRAND veut dire SUSPECT**, et le pli l'est déjà. L'intensité est dans
l'autre sens, donc on classe sur son **opposé** — et le dire ici plutôt que le cacher dans un signe
est ce qui évite de publier une courbe parfaitement **inversée**, défaut qui se lirait comme
« cette observable anti-prédit », c'est-à-dire comme un résultat.

![une cellule peut-elle savoir qu'elle a tort](images/75_la_cellule_sait_elle_quelle_a_tort.png)

| observable | marcheur | 100 % | 90 % | 75 % | 50 % | 35 % | 25 % | 10 % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| pli | rien | +0.0 | -5.1 | -5.4 | -0.6 | +1.6 | -0.3 | -1.8 |
| pli | rien_lisse | +0.0 | -1.2 | +1.2 | +3.0 | +7.1 | +5.5 | -0.8 |
| pli | raccroche | +0.0 | -13.2 | -27.9 | -43.2 | -44.6 | -46.6 | -50.3 |
| obscurite | rien | +0.0 | -0.4 | -3.1 | -8.1 | -6.6 | -7.8 | +10.5 |
| obscurite | rien_lisse | +0.0 | -0.6 | -3.6 | -10.8 | -13.1 | -12.6 | -3.2 |
| obscurite | raccroche | +0.0 | -0.3 | -1.5 | -6.6 | -8.0 | -20.6 | +15.2 |

*écart médian sur les bras, classé moins hasard, en µm. Négatif = l'observable **prédit**.*

> ⭐⭐⭐ **LES DEUX OBSERVABLES SONT COMPLÉMENTAIRES, et celle qui marche est celle que le
> traitement n'a pas détruite.** Le **pli** prédit fortement chez le raccrochage (-43.2 µm à
> moitié gardée, -50.3 à un dixième, **8 bras sur 8**) et **pas du tout** chez le pas normal
> lissé (+7.1, donc pire que le hasard). L'**obscurité** fait l'inverse : -13.1 µm chez le pas
> normal lissé sur **7 bras sur 8**, et -8.1 chez le pas normal. Le lissage peut effacer les
> plis, il ne peut **pas** empêcher une cellule tombée dans un vide de lire **sombre**.

##### ⚠⚠ Et le chiffre actionnable ne bouge pas : elles disent où il se trompe sans le rendre juste

| marcheur | bras perdus | sauvés par le PLI | sauvés par l'OBSCURITÉ | au hasard |
|---|---:|---:|---:|---:|
| rien | 4 | **1** à 90 % | **1** à 50 % | 0 |
| rien_lisse | 3 | **0** | **0** | 0 |
| raccroche | 6 | **1** à 90 % | **0** | 0 |

> ⚠ **Aucune des deux ne sauve un bras du pas normal LISSÉ**, et c'est le point à retenir : une
> confiance par cellule dit **où** un marcheur se trompe, elle ne le rend pas **juste**. Ce qu'elle
> change est ce qu'un déroulement peut **livrer** — une nappe accompagnée de sa propre carte de
> doute — et c'est indépendant de toute amélioration de méthode.

⚠ Et à un dixième gardé, l'obscurité **cesse de prédire** (+10,5 et +15,2 µm) : classer sur si peu
de cellules mesure surtout le tirage. La courbe le montre, et c'est pourquoi c'est la **courbe
entière** qui est livrée plutôt qu'un point.

---
##### ⛔ COMBINER LES DEUX OBSERVABLES : sans aucun paramètre, et aucune ne DOMINE

⚠⚠⚠ **Combiner deux observables demande normalement un POIDS**, donc un réglage — et un réglage
choisi sur ce qu'il juge ne peut que gagner. Le passage en **RANG** le supprime **deux fois** : les
unités disparaissent (un pli en µm et une obscurité en niveaux de gris ne s'additionnent pas), et
les trois façons de recombiner deux rangs n'ont plus **rien à régler**.

| combinaison | ce qu'elle dit |
|---|---|
| **ou** | le **max** des rangs : suspect dès qu'**une** des deux le dit |
| **et** | le **min** : suspect seulement si les **deux** le disent |
| **moyenne** | les deux comptent pareil — le seul poids qu'on n'a pas choisi, puisqu'il est le seul qui ne privilégie personne |

![une cellule peut-elle savoir qu'elle a tort](images/75_la_cellule_sait_elle_quelle_a_tort.png)

| colonne | marcheur | 100 % | 90 % | 75 % | 50 % | 35 % | 25 % | 10 % | partout |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| pli | rien | +0.0 | -5.1 | -5.4 | -0.6 | +1.6 | -0.3 | -1.8 |  |
| pli | rien_lisse | +0.0 | -1.2 | +1.2 | +3.0 | +7.1 | +5.5 | -0.8 |  |
| pli | raccroche | +0.0 | -13.2 | -27.9 | -43.2 | -44.6 | -46.6 | -50.3 | ⭐ |
| obscurite | rien | +0.0 | -0.4 | -3.1 | -8.1 | -6.6 | -7.8 | +10.5 |  |
| obscurite | rien_lisse | +0.0 | -0.6 | -3.6 | -10.8 | -13.1 | -12.6 | -3.2 | ⭐ |
| obscurite | raccroche | +0.0 | -0.3 | -1.5 | -6.6 | -8.0 | -20.6 | +15.2 |  |
| ou | rien | +0.0 | -2.7 | -5.2 | -6.1 | -7.7 | -9.4 | -12.3 | ⭐ |
| ou | rien_lisse | +0.0 | -1.7 | -1.2 | -0.9 | +1.5 | -8.4 | +2.1 |  |
| ou | raccroche | +0.0 | -5.5 | -15.1 | -37.2 | -47.9 | -53.0 | -65.3 | ⭐ |
| moyenne | rien | +0.0 | -1.9 | -2.3 | -3.8 | -6.7 | -8.4 | +2.7 |  |
| moyenne | rien_lisse | +0.0 | -0.9 | +0.4 | +0.3 | -3.4 | -5.9 | -8.3 |  |
| moyenne | raccroche | +0.0 | -11.0 | -22.1 | -40.1 | -46.8 | -54.4 | -60.5 | ⭐ |
| et | rien | +0.0 | -1.6 | -2.1 | -1.4 | -2.8 | +0.4 | -3.7 |  |
| et | rien_lisse | +0.0 | +0.1 | -0.1 | -4.7 | -3.4 | -2.8 | -8.0 |  |
| et | raccroche | +0.0 | -10.8 | -22.1 | -35.3 | -40.8 | -44.3 | -29.0 | ⭐ |

*écart médian sur les bras, classé moins hasard, en µm. Négatif = l'observable **prédit**.
⭐ = elle prédit à **toutes** les fractions.*

> ⛔ **LE VERDICT STRICT EST VIDE** : aucune combinaison ne bat **les deux** observables seules à
> **toutes** les fractions, chez aucun des trois marcheurs. Le publier autrement — désigner « la
> meilleure des cinq » après les avoir vues — serait choisir sur ce qu'on juge, la faute nº1 de ce
> registre.

> ⭐⭐ **Ce qui se publie sans rien choisir est un COMPTE.** Quelles colonnes prédisent à **toutes**
> les fractions : pour le **pas normal**, `ou` **et elle seule** ; pour le **pas normal lissé**,
> l'obscurité seule ; pour le **raccrochage**, quatre colonnes sur cinq. ⚠ Donc `ou` n'est
> **meilleure nulle part** et **la seule utilisable partout** chez le pas normal : c'est de la
> **robustesse au point de fonctionnement**, pas de la domination — et c'est exactement ce dont un
> dérouleur qui ne choisit pas sa fraction a besoin.

| marcheur | bras perdus | pli | obscurite | ou | moyenne | et | au hasard |
|---|---:|---:|---:|---:|---:|---:|---:|
| rien | 4 | 1 | 1 | 1 | 1 | 1 | 0 |
| rien_lisse | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| raccroche | 6 | 1 | 0 | 2 | 2 | 1 | 0 |

⚠ **Le seul endroit où une combinaison ajoute un bras est chez le raccrochage** : `ou` et
`moyenne` en sauvent **2 sur 6** contre 1 pour le pli seul. Chez le pas normal, les cinq colonnes
sauvent le même unique bras — à des fractions différentes (90 % par le pli, 50 % par l'obscurité,
75 % par `et`), ce qui est une information de **coût** et pas de capacité.

---
##### ⛔⛔⛔ REFUSER SES PROPRES PLIS : la portée monte, et l'écart apparié vaut EXACTEMENT ZÉRO

⚠⚠⚠ **L'idée était bonne et vient de la tranche précédente** : les plis sont **localisés**, et une
cellule pliée est détectable **SANS la cible** — son écart à la médiane de ses voisins dépasse la
demi-feuille, donc elle est plus près de la feuille voisine que du plan de ses **propres** voisins.
Un marcheur peut donc la **refuser** au lieu de la porter au bras suivant. Le critère vient de la
matière, l'observation ne demande **aucune supervision**, et le prix annoncé est la couverture.

| marcheur | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | portée |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pas normal seul | 44,0 | 50,1 | 49,5 | 67,2 | 72,2\* | 114,2\* | 1016,5\* | 177,3\* | 4 |
| **pas normal, plis REFUSÉS** | 44,0 | 50,1 | 48,6 | 64,4 | **58,0** | 103,9\* | 975,0\* | 101,0\* | **5** |
| **nappe lissée, plis refusés** | 44,4 | 50,0 | 48,7 | 63,9 | **57,9** | 90,5\* | 865,4\* | 138,0\* | **5** |

⭐ **Et la nappe reste PLATE** : le marcheur qui lisse **et** refuse ses plis publie une rugosité de
nappe de **0,00 µm aux HUIT bras**, là où le pas normal seul monte à 19,87. Le refus des plis à lui
seul la plafonne à 2,14 au lieu de 19,87.

> ⛔⛔⛔ **ET POURTANT IL NE GAGNE RIEN — ce que seul l'appariement sur les cellules COMMUNES pouvait
> dire.** Sur les cellules que le marcheur élagué et sa référence ont **tous les deux** gardées,
> l'écart apparié vaut **+0.0 µm, intervalle [0.0, 0.0]** : **exactement zéro**. Refuser une cellule ne change
> **rien** à celles qui restent — c'est même la seule chose qu'un refus puisse faire.

⚠⚠⚠ **Tout le gain apparent vient donc de ce qu'il JETTE.** Il garde **0.453** de la nappe du pas
normal au dernier bras (391 cellules contre 864). Une erreur qui s'améliore parce qu'on a écarté
les cellules difficiles n'est pas une méthode meilleure, **c'est un échantillon plus facile** — et
c'est exactement le mode de panne qu'un contrôle écrit deux tranches plus tôt nommait, appliqué
cette fois à mon propre marcheur.

> ⭐ **Ce n'est pas rien pour autant, et il faut le dire dans les deux sens.** Un dérouleur peut
> parfaitement préférer **la moitié de la nappe à 58 µm** plutôt que toute à 72, parce que les
> cellules écartées sont précisément celles qui seraient **fausses**. Mais c'est un **arbitrage
> couverture / justesse**, jamais un gain de méthode, et publier la portée de 5 sans la part gardée
> de 0.453 serait le présenter pour ce qu'il n'est pas.

⚠⚠ **Et le panneau C de la figure a changé de forme pour ça** : il dessine désormais **une courbe
par marcheur** au lieu d'une seule. Tant que tous gardaient les mêmes cellules, une courbe suffisait
et le disait ; dès qu'un marcheur en refuse, une courbe unique laisserait lire une portée gagnée
sans son coût.

##### ⚠⚠ Un défaut de ma part, attrapé par la sortie d'un contrôle et pas par une relecture

Les deux marcheurs neufs sont d'abord tombés dans la branche du **RACCROCHAGE** : je les avais
ajoutés à `MARCHEURS` sans élargir la condition qui nomme la famille du pas normal. Ils lisaient
donc le volume, corrélaient un gabarit, et publiaient sous un nom qui annonce l'inverse. Ce qui l'a
dit : la **rugosité de champ** publiée par `rien_elague` était exactement celle de `raccroche` —
un marcheur qui ne glisse pas ne peut pas avoir un champ de décalage rugueux.

> ⚠ La famille est désormais nommée **en un seul endroit** (`FAMILLE_DU_PAS_NORMAL`), et deux
> contrôles l'épinglent : aucun marcheur de cette famille n'a de rugosité de champ non nulle, et
> tout marcheur dont le nom porte « lisse » publie une part lissée non nulle. Un nom qui ment sur
> ce que le code fait est le pire des défauts silencieux, parce que toute la lecture en aval en
> dépend.

---
##### ⭐⭐⭐ OÙ la nappe se froisse — et ce que les MÉDIANES cachaient

> Mesure : `src/nappe/ou_la_nappe_se_froisse.py` (15 contrôles) →
> `docs/mesures/ou_la_nappe_se_froisse.json`. Figure :
> `src/figures/figure_ou_la_nappe_se_froisse.py` (11 contrôles). Pont vers l'instrument
> volumétrique : `src/nappe/la_nappe_en_obj.py` (27 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/ou_la_nappe_se_froisse.py --cote 960 \
>     --json docs/mesures/ou_la_nappe_se_froisse.json
> uv run python src/figures/figure_ou_la_nappe_se_froisse.py \
>     --sortie docs/images/75_ou_la_nappe_se_froisse.png
> ```

⚠⚠⚠ **CETTE TRANCHE VIENT D'AVOIR REGARDÉ, et c'est l'auteur qui l'a rappelé** : ce dépôt a un
instrument volumétrique (`lpl-scrollwalk`, `lpl::voxel` et `lpl::zarr` dans LplPlugin) et sept
tranches de marche l'avaient ignoré. Toute la campagne publiait le froissement en **MÉDIANES** —
5,11 µm pour le pas normal au bras 6, 151,81 pour le raccrochage. Une médiane dit **combien**,
jamais **où**.

![où la nappe se froisse](images/75_ou_la_nappe_se_froisse.png)

**Une TACHE est une cellule dont l'écart à la médiane de ses voisins dépasse la demi-feuille.**
Le seuil vient de la matière : au-delà, le point est plus près de la feuille **voisine** que du
plan de ses **propres** voisins, donc la nappe y est localement **pliée** et non bosselée.

| marcheur, part de cellules pliées | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rien | 0.0 % | 0.0 % | 1.9 % | 6.9 % | 13.0 % | 18.6 % | 26.3 % | 32.8 % |
| rien_lisse | 0.0 % | 0.0 % | 0.2 % | 1.0 % | 2.1 % | 3.9 % | 4.8 % | 6.5 % |
| raccroche | 0.2 % | 4.6 % | 38.3 % | 71.3 % | 91.0 % | 83.0 % | 91.0 % | 96.6 % |
| oracle | 0.0 % | 1.2 % | 4.0 % | 7.5 % | 14.2 % | 26.1 % | 43.4 % | 62.8 % |

> ⚠⚠⚠ **LE FROISSEMENT DU PAS NORMAL N'EST PAS DISTRIBUÉ.** Il commence à **zéro**, apparaît au
> bras 3 et atteint **33 %** des cellules au bras 8 — pendant que sa rugosité **médiane** reste
> à une vingtaine de micromètres. Une médiane sur une nappe **surtout lisse avec quelques régions
> ruinées**, et une médiane sur une nappe **uniformément tiède**, sont le même nombre. C'est
> exactement ce qu'une médiane ne peut pas distinguer, et c'est pour ça qu'il fallait regarder.

> ⭐⭐⭐ **ET C'EST LA MESURE LA PLUS NETTE DE CE QUE LE LISSAGE FAIT** : il ramène la part pliée de
> **33 % à 7 %**, soit **80 % des cellules pliées en moins**. Dit comme ça, c'est un tout
> autre énoncé que « six micromètres de mieux » — et c'est le **même fait**.

⚠⚠ **Le raccrochage est une panne d'une AUTRE NATURE** : 38 % des cellules dès le bras 3,
97 % au bras 8. Ce n'est plus une tache qui grandit, c'est la nappe **entière** qui plie.

> ⚠⚠⚠ **ET LA BORNE SE FROISSE AUSSI — 63 % au dernier bras — en gardant une erreur de 17 à
> 22 µm.** Donc **un froissement n'est PAS ce qui perd une marche** : il ne le devient que si rien
> ne vient recaler ce qui repart dessus. Ça affine le diagnostic de la tranche précédente, qui
> disait « ce qu'un marcheur aveugle paie, c'est de devoir repartir de sa propre nappe » — la
> nappe froissée est une **condition**, le défaut de recalage est la **cause**.

##### ⚠⚠ Les taches coïncident-elles ? Oui, et faiblement — le témoin le dit

⚠⚠⚠ **Cette question ne se répond pas sans témoin.** Deux ensembles de taches couvrant chacun
soixante pour cent d'une même région se recouvrent largement **par construction** : le
recouvrement brut mesure surtout leurs **tailles**. Le témoin est le recouvrement de deux
ensembles de **mêmes tailles** tirés au hasard dans les **mêmes cellules**.

| paire | recouvrement | témoin au hasard | rapport |
|---|---:|---:|---:|
| rien / rien_lisse | 0.182 | 0.060 | **×3.03** |
| rien / raccroche | 0.331 | 0.325 | **×1.02** |
| rien / oracle | 0.415 | 0.274 | **×1.51** |
| rien_lisse / raccroche | 0.066 | 0.065 | **×1.02** |
| rien_lisse / oracle | 0.094 | 0.063 | **×1.49** |
| raccroche / oracle | 0.624 | 0.615 | **×1.01** |

> ⚠ **Les 6 paires sont au-dessus de leur témoin, et le rapport médian n'est que de 1.26.** « Au
> dessus du témoin » est satisfait par un rapport de **1,01**, donc le verdict tient sur un
> **signe** et pas sur une marge — la mesure le publie, et le rapport le plus faible est rendu à
> côté du oui.

> ⭐ **Ce qui reste** : les deux paires où les taches sont encore **minoritaires** montrent une
> vraie co-localisation — **×3,0** pour pas normal / pas normal lissé, **×1,5** pour pas normal /
> borne. Le froissement est donc **en partie** une propriété du **LIEU** et pas seulement du
> marcheur. Modestement, et à vérifier sur d'autres ancres avant d'en faire quoi que ce soit.

##### ⚠ Le pont vers l'instrument volumétrique, et ce qu'il a montré

`la_nappe_en_obj` écrit une nappe prédite en **OBJ** — coordonnées en échantillons de niveau 0,
ordre `x y z`, celui du corpus et celui que `scroll::loadSegmentObj` lit **droit** — plus ses
**coordonnées de texture**, sans lesquelles `--segment-ink` ne peut pas peindre une mesure **sur**
la surface qu'elle décrit. Et un écrivain **PGM** pour la carte elle-même, format choisi par
`lpl-scrollwalk` parce qu'un PNG demanderait un décompresseur qu'un outil porterait pour toujours.
La pose de caméra est **lue dans le rendu** et non devinée : `--at Z Y X` pose
`camera.position = (X, Y, Z)` et `voxel::FreeCamera::eye` construit
`avant = (sin lacet · cos tangage, sin tangage, cos lacet · cos tangage)`.

⚠⚠ **Ce que le raymarcher a montré, et ce qu'il ne peut pas montrer.** Mesuré : à 2 600
échantillons de la nappe — 5,8 mm de papyrus — **tous** les rayons saturent avant de l'atteindre,
et à 240 échantillons la nappe remplit le cadre. Le milieu est opaque à l'échelle d'une nappe de
mille échantillons, donc une vue en première personne d'un patch entier est du **brouillard**.
L'instrument répond à *« cette nappe est-elle posée sur de la matière »*, pas à *« de quelle forme
est ce froissement »* — et c'est pour la seconde que les cartes existent.

---
##### ⛔ COMBIEN LISSER ? Le balayage TRANCHE et n'autorise pourtant RIEN

> Mesure : `src/nappe/combien_lisser_la_nappe.py` (17 contrôles) →
> `docs/mesures/combien_lisser_la_nappe.json`. Figure :
> `src/figures/figure_combien_lisser_la_nappe.py` (11 contrôles), le 2026-09-07.
>
> ```bash
> uv run python src/nappe/combien_lisser_la_nappe.py --cote 960 --ancres 5 \
>     --json docs/mesures/combien_lisser_la_nappe.json
> uv run python src/figures/figure_combien_lisser_la_nappe.py \
>     --sortie docs/images/75_combien_lisser_la_nappe.png
> ```

⚠⚠⚠ **Pourquoi ce balayage, et pourquoi il devait être hors échantillon.** Le lissage de la nappe
tourne avec le voisinage **déployé** — demi-largeur un, une passe — et ce réglage n'avait jamais
été balayé **sur une marche**. La tranche qui l'a balayé le faisait sur **un** pas, où elle a
conclu que la largeur s'épuise à 3×3 ; une marche est un autre régime. Et essayer neuf étages
pour publier le meilleur, c'est publier le hasard du meilleur tirage : chaque ancre est donc
jugée à l'étage que les **quatre autres** ont préféré, avec `choisir_hors_echantillon`.

![combien faut-il lisser la nappe](images/75_combien_lisser_la_nappe.png)

| ancre | brut | m1 | m2 | m4 | m8 | m16 | m32 | m1×2 | m1×3 | choisi par les autres | portée |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 4 | 69.7 | 63.0 | 59.8 | 49.3 | 55.7 | 101.3 | 69.7 | 62.0 | 62.2 | **median_16** | 5 → **0** |
| 5 | 120.0 | 109.7 | 100.0 | 91.8 | 83.7 | 70.8 | 100.6 | 107.3 | 106.0 | **median_8** | 2 → **3** |
| 6 | 119.5 | 113.6 | 115.3 | 104.2 | 70.1 | 42.8 | 104.8 | 113.7 | 109.0 | **median_16** | 3 → **3** |
| 7 | 116.2 | 110.2 | 106.3 | 96.8 | 67.5 | 72.1 | 112.2 | 107.1 | 105.9 | **median_16** | 2 → **2** |
| 8 | 124.7 | 105.9 | 109.8 | 106.7 | 99.2 | 72.5 | 123.9 | 102.7 | 103.4 | **median_8** | 1 → **1** |
| *part lissée* | 0.00 | 1.00 | 0.99 | 0.98 | 0.95 | 0.80 | 0.17 | 1.00 | 1.00 | | |

⚠⚠⚠ **PREMIÈRE FAUTE, ATTRAPÉE ET CORRIGÉE : l'optimum était AU BORD de ma famille.** La première
version s'arrêtait à `median_8`, et c'est exactement là que l'optimum est tombé — c'est-à-dire au
bord du balayage, donc **un plancher de ce qu'on a essayé et non une propriété de la matière**.
C'est la faute que le balayage du cône de directions a déjà payée. La famille a été **étendue** à
`median_16` et `median_32` ; l'optimum est désormais **intérieur**, et un drapeau le publie.

⚠⚠ **Seconde précaution, et elle était nécessaire : la part de nappe RÉELLEMENT lissée.** Une
fenêtre large exige une majorité de voisins présents, donc elle est **refusée** près des bords.
Mesuré : 1,00 · 0,99 · 0,98 · 0,95 · **0,80** · **0,17** de `median_1` à `median_32`. Sans ce
nombre, « la fenêtre 65×65 gagne » pourrait vouloir dire « elle ne s'applique presque plus » — et
un contrôle exige qu'un étage qui ne lisse rien coûte **exactement** ce que coûte le brut.

> ⚠⚠⚠ **ET LE RÉSULTAT TRANCHE : -26.0 µm sur 4/5 ancres, intervalle [-32.1, -16.4].** Une fenêtre bien
> plus large que celle qui tourne gagne vingt-six micromètres hors échantillon. Sur la seule
> grandeur d'erreur, il n'y a pas de doute.

⛔⛔⛔ **SAUF QUE CE N'EST PAS LA QUESTION DU BUT, et le coût en BRAS dit l'inverse.** À l'ancre 4
— **la seule dont la marche va quelque part** — l'étage que les autres ancres lui donnent fait
tomber sa portée de **5 à ZÉRO** : la marche échoue au premier bras. La cause est dans la
définition du premier coût : c'est la **médiane des erreurs par bras**, et cette médiane inclut
les bras où la marche est **DÉJÀ PERDUE**. Passer de 120 à 70 µm sur une marche perdue n'est pas
un progrès — les deux sont au-delà de la demi-feuille — donc **un réglage choisi là-dessus est
choisi sur la qualité de ses échecs**.

⚠⚠ **Et le coût en bras ne peut RIEN discriminer sur ce matériau** : aux ancres 6, 7, 8 la portée est
la **même à tous les étages**, donc sa médiane ne sépare pas et son « choix » est le premier de la
liste. C'est une limite de la **matière**, pas de l'instrument : il faudrait des ancres dont la
marche soit vivante, et le corpus n'en offre qu'une.

> ⛔ **DONC LE BALAYAGE N'AUTORISE PAS À CHANGER LE RÉGLAGE DÉPLOYÉ**, et la porte est **fermée
> par défaut** dans le code : il faut que l'optimum ne soit pas au bord, **que** le gain tranche,
> **et** qu'aucune ancre ne voie sa portée diminuer. Un contrôle vérifie qu'une portée qui empire
> ferme la porte — sans lui, un gain médian sur des marches déjà perdues suffirait à déplacer le
> réglage qui tourne.

> ⭐⭐ **Ce qui RESTE de ce balayage, et c'est un fait à garder.** À l'ancre 4, la fenêtre
> `median_8` donne une portée de **6** — le plafond du corpus, celui que la **borne** atteint.
> Une fenêtre large **peut** faire marcher un marcheur aveugle jusqu'à la borne. Mais la largeur
> qui y arrive **dépend de l'ancre** (6 à `median_8`, 0 à `median_16`), et hors échantillon on ne
> la trouve pas. C'est une piste avec sa condition : il faut plus d'ancres dont la marche soit
> vivante, donc une boîte plus grande ou un objet moins troué.

⚠ **Pour mémoire, le résultat de la tranche précédente se reproduit sur ces mêmes ancres** :
l'étage déployé bat le brut de **-6.7 µm** sur 5/5 ancres, intervalle [-8.5, -6.4] — il tranche. Lisser
vaut mieux que ne pas lisser ; c'est **combien** qui n'est pas tranché.

##### ⚠⚠ Ce que le corpus demande, et pourquoi il fallait le mesurer à part

La dernière ligne du tableau ne fait intervenir **aucun marcheur** : c'est la distance médiane de
la spire de départ à la spire d'arrivée, dans la boîte. Le bras 7 y demande **1000,6 µm**, soit
**7,4 fois** le pas nominal — les spires 10 et 11 sont voisines par leur **numéro** et éloignées
de huit feuilles dans la **matière**. Sans cette ligne, l'effondrement du bras 7 se lirait comme
un échec de méthode ; avec elle, c'est un trou du corpus, et c'est pourquoi **la borne elle-même y
échoue**.

> ⭐⭐ **Et la borne s'arrête exactement là où le corpus s'arrête** : elle porte **6** bras, et
> **6** est le nombre de bras que le corpus demande au pas nominal à une demi-feuille près. Ce
> qui l'arrête est la **matière**, pas la méthode — la seule des deux qui ne se corrige pas.

##### ⚠ Trois précautions, chacune un contrôle de la batterie

1. **Le plancher est dérivé, jamais choisi.** Une distance à un nuage est **1-lipschitzienne** :
   un point à distance *d*, déplacé de *L*, ne peut pas être à moins de |*d* − *L*|. Chaque bras
   publie donc une borne inférieure sur son erreur, et un contrôle exige qu'elle ne dépasse jamais
   l'erreur mesurée. ⚠ Le déplacement n'est **pas** le pas : le raccrochage glisse de *t* voxels
   sur la même ligne, donc la cellule bouge de |pas + *t*|. Prendre le pas nominal ici aurait
   donné un « plancher » que l'erreur mesurée pouvait passer sous — c'est-à-dire pas un plancher.
2. **Une seule population.** Les quatre marcheurs gardent **exactement les mêmes cellules** à
   chaque bras (1 805 → 864, soit 0,479 de la nappe), donc aucune différence de ce tableau ne
   s'explique par qui est compté. La perte est réelle et publiée à côté de l'erreur : une erreur
   qui s'améliorerait pendant que la couverture s'effondre ne serait pas un progrès.
3. **La question est posée dans les DEUX sens.** `tranche` répond « y a-t-il une différence
   constante **en faveur du premier** », donc un faux ne veut pas dire « les deux se valent ». La
   moitié renversée est publiée à côté, avec le même instrument et sans seuil ajouté — sans elle,
   un raccrochage qui **coûte** se lirait comme un raccrochage qui **n'apporte rien**, ce qui est
   un tout autre verdict. Un contrôle exige que les deux ne soient jamais vrais ensemble.

> ⭐⭐⭐ **Ce que cette tranche laisse, et c'est la première piste neuve depuis sept tranches.**
> La question à laquelle la campagne répondait — *« quelle méthode fait le meilleur pas ? »* —
> n'est pas celle du but. Celle du but est *« quelle méthode va le plus loin ? »*, et les deux
> ont des réponses **différentes** sur la même donnée. Trois conséquences immédiates, dans
> l'ordre où elles se testent :
>
> 1. ✅ **Le froissement se mesure** — FAIT dans la même tranche : la rugosité du champ de
>    décalage **croît** de 0,34 à 2,01 voxels sur les cinq premiers bras, elle est **nulle
>    partout** pour le pas normal seul, et **entre 0 et 1** pour la borne. La prémisse tient.
> 2. ✅ **Le lissage devrait porter sur la SURFACE, pas sur le décalage** — FAIT : portée 2 → 3,
>    et retour à **parité** avec le pas normal seul, sans un réglage de plus.
> 3. ⚠ **Ce qui reste, et c'est le seul des trois qui demande une décision.** Un marcheur qui
>    raccroche puis s'arrête de raccrocher aurait besoin d'un critère d'arrêt — et « après le
>    deuxième bras » serait un seuil **choisi sur le résultat qu'on mesure**, c'est-à-dire la
>    faute nº1 de ce dépôt. Le critère devrait venir de ce que la méthode **peut savoir**, donc
>    pas de son erreur, qui est de la supervision. La rugosité de son propre champ, elle, est
>    observable sans cible : c'est la piste, et elle demande d'abord de vérifier qu'elle prédit
>    l'échec plutôt que de l'accompagner.

---

### C2 ⭐ — le nul verso (H7)

Un rendu décalé par segment, sur les mêmes couches et sur trois segments `w` de `0139`. C'est
le nul **propre** — parallèle à une face, sans arête de feuille — que `46` n'est pas.

⚠ **Plus urgent depuis `46`, pas moins** : le détecteur y rend *plus* de dispersion sur la
surface sans face que sur une face. Tant qu'on ne sait pas ce qu'il rend sur une face
**vierge**, « l'encre valide le déroulage » n'est pas utilisable.

### ✅✅ C2 — le nul verso : MESURÉ sur TROIS segments le 2026-09-05, et le résultat s'est INVERSÉ en cours de route

> Mesure : `src/encre/le_nul_verso.py` (20 contrôles par segment + 5 contrôles joints),
> `docs/mesures/le_nul_verso_*.json`. Figure : `src/figures/figure_le_nul_verso.py` (15 contrôles).
>
> ```
> uv run python src/encre/le_nul_verso.py --tous          # les trois segments, l'un après l'autre
> uv run python src/encre/le_nul_verso.py --verifier       # la batterie, sur tout ce qui est mesuré
> uv run python src/figures/figure_le_nul_verso.py --tous --sortie docs/images/75_le_nul_verso.png
> ```

⭐⭐⭐ **Aucun rendu n'était nécessaire.** Les `layers-zarr` publiés de `PHerc0139` font
**109 couches** (`shape [109, 23280, 32160]`) là où le détecteur n'en lit que **26**. Décaler
`--start-layer` donne donc le nul dans **la même pile** : même volume, même segment, même région,
même modèle, même pas — un seul paramètre bouge, ce qui est la conception appariée que `46`
réclame.

### ⚠⚠⚠ La première campagne était FAUSSE, et sa cause était écrite dans le module qu'elle appelait

Elle plaçait sa fenêtre « face » sur le pic de **contraste local**. Or `depth_profile.py` dit
lui-même que *« sur un volume à 2,4 µm le contraste devient un U — maximal aux DEUX bords,
minimal dans la feuille — parce qu'il suit les interfaces et le bruit, pas la matière »*, et le
§10 de [`12`](12_profondeur_de_surface.md) porte cette correction depuis le 2026-08-18.

Mesuré : sur `w058` et `w056` le contraste pique aux couches **0** et **104** d'une pile de 109,
**avec son minimum au milieu**. La fenêtre « face » tombait donc sur une **spire voisine** et la
fenêtre « nulle », choisie au minimum, tombait **dans la feuille**. Le couple était **inversé**,
et il rendait une AUC de **0,50** que j'ai failli publier comme « le détecteur ne distingue pas
le papyrus du vide ».

⭐ **Deux gardes plutôt qu'une vigilance** : le choix se fait désormais sur l'**intensité**, et
un pic hors de la **moitié centrale** de la pile fait **refuser** la mesure — avant de payer deux
inférences, pas après. Le chercheur de tuiles score sur **le même critère** que la garde :
chercher sur l'un et refuser sur l'autre garantit de trouver ce qui sera refusé.

### La mesure, sur les trois segments

![une face et un vide, sur trois segments](images/75_le_nul_verso.png)

*Même échelle de gris **par segment**, prise sur les percentiles 1 et 99 des deux cartes : rendre
chacune à sa propre plage ferait paraître le vide aussi structuré que la face, c'est-à-dire
illustrerait la panne au lieu de la montrer. ⚠ L'échelle n'est pas commune aux trois — deux
campagnes n'ont pas la même plage de sortie, et une échelle globale comparerait des campagnes au
lieu de comparer face et vide.*

| segment | fenêtres | **AUC face/vide** | médiane face | médiane vide | matière face/vide | contraste face/vide |
|---|---|---:|---:|---:|---:|---:|
| `w056` | 39–65 contre 83–109 | **0,519** | −0,839 | −0,869 | **5,9×** | 0,717 / 0,191 |
| `w058` | 60–86 contre 5–31 | **0,371** | −0,665 | **−0,240** | **2,6×** | 0,187 / **0,639** |
| `w046` | 35–61 contre 61–87 | **0,382** | −0,812 | **−0,394** | **3,6×** | 0,245 / **0,383** |

> ⚠⚠⚠ **Le détecteur ne sépare la feuille du vide sur AUCUN des trois.** Le mieux qu'il fasse est
> **0,519**, c'est-à-dire le hasard. Et sur deux segments il fait **pire que le hasard** : le vide
> se lit **plus encré** que la feuille, alors que la face y porte **2,6 à 5,9 fois** plus de
> matière.

⭐⭐ **Ce qui prédit la réponse n'est pas la matière, c'est le CONTRASTE.** Le signe de
`AUC − 0,5` suit celui de `contraste_face − contraste_vide` sur les **trois** segments, tandis que
le rapport de matière — qui penche partout du côté de la face — ne prédit rien. ⚠ Trois points :
un accord de signe sur trois vaut une chance sur huit sous une règle tirée au hasard. C'est une
observation **compatible avec** « le détecteur suit le contraste local et non la feuille », pas
une preuve — et le contrôle est écrit pour **tomber** si un quatrième segment ne suivait pas.

### ⚠⚠⚠ Et la cause probable est une erreur d'échelle qui touche TOUT le dépôt

Le modèle lit **26 couches**. Ce qui compte n'est pas ce compte mais l'**épaisseur** :

| pile | taille de voxel | 26 couches couvrent |
|---|---:|---:|
| Scroll 1 `20230909121925`, où le modèle atteint 0,925 | 7,91 µm | **206 µm** |
| segments officiels de `PHerc1447` | 8,64 µm | 225 µm |
| **volumes de surface de `PHerc0139`** | **2,399 µm** | **62 µm** |

**62 µm, c'est moins qu'une épaisseur de feuille** (~100 µm). Sur ces volumes le détecteur ne voit
donc pas « une feuille et ses voisines » comme à l'entraînement : il voit une tranche **intérieure**
à une feuille — où il n'y a aucune surface — pendant que la fenêtre « nulle », posée entre deux
spires, en contient une. **Cela expliquerait exactement le renversement mesuré.**

⚠⚠ `infer_ink.py` portait le contraire, et à l'envers : *« à 8,64 µm, 26 couches couvrent 225 µm là
où l'entraînement en voyait 62 »*. Or 62 = 26 × 2,4, c'est-à-dire précisément la ligne que
[`36`](36_lorigine_de_la_pile.md) §5bis **déclare fausse** depuis le 2026-08-27. Corrigé.

⭐⭐⭐ **La prédiction, écrite AVANT la mesure.** `load_layer_stack` prend depuis août un pas de
profondeur qui épaissit la fenêtre sans changer le nombre d'images — et **aucun drapeau ne
l'exposait**, donc la seule grandeur capable de corriger la profondeur lue était injoignable
depuis la ligne de commande. Il l'est désormais (`--pas-couches`). À **pas 3** les 26 couches
couvrent **187 µm**, soit le régime d'entraînement à 9 % près, et la fenêtre « face » contient
alors la surface **et** ses voisines.

> **Si la fenêtre trop mince est la cause**, l'écart-type de la sortie doit monter avec le pas et
> la face doit cesser d'être moins encrée que le vide. **Sinon**, la profondeur est innocentée et
> cet axe est clos — ce qui vaut d'être écrit aussi.

### ✅ Mesuré le même jour : **la prédiction est RÉFUTÉE, et l'axe est clos**

> Mesure : `src/encre/la_profondeur_lue.py` (15 contrôles), `docs/mesures/la_profondeur_lue.json`.
> Figure : `src/figures/figure_profondeur_lue.py` (5 contrôles).
>
> ```
> uv run python src/encre/la_profondeur_lue.py --segment 20260325000000-w046_20260325 \
>     --json docs/mesures/la_profondeur_lue.json
> uv run python src/figures/figure_profondeur_lue.py --sortie docs/images/75_la_profondeur_lue.png
> ```

![la même fenêtre, lue à trois profondeurs](images/75_la_profondeur_lue.png)

| pas | profondeur lue | couches | **σ** | médiane |
|---:|---:|---|---:|---:|
| 1 | **62 µm** (le régime actuel) | 35–60 | **0,718** | −0,812 |
| 2 | 122 µm | 18–68 | 0,554 | −1,046 |
| 3 | **182 µm** (le régime d'entraînement) | 1–76 | **0,423** | −1,137 |

⚠⚠⚠ **σ TOMBE, de façon monotone, au lieu de monter.** Ramener la fenêtre au régime
d'entraînement rend la carte **plus terne**, pas plus riche — c'est visible sur la figure, où
elle ne devient pas bruitée mais s'éteint.

⭐⭐ **Et à la profondeur actuelle le modèle est VIVANT** : σ = **0,718**, soit l'étalon de `36`
§5bis là où le modèle atteint 0,925 (**0,771**), et non son étalon muet (**0,017**). L'incapacité
mesurée en `C2` à séparer la feuille du vide n'est donc **pas** « le détecteur ne répond pas sur
ce rouleau » — il répond normalement, et sa réponse ne suit simplement pas la feuille.

> **Donc la fenêtre trop mince n'explique pas `C2`, et cet axe est clos.** C'est la **troisième**
> élimination indépendante de l'échelle comme explication, après `58` (émulation sur Scroll 1) et
> `63` (contre de vraies étiquettes) — et la première qui porte sur la **profondeur** et non sur
> le pas en plan.

⚠⚠ **Le confond, nommé plutôt que tu** : épaissir la fenêtre ne change pas que sa profondeur. À
pas 3 elle couvre les couches **1 à 76** d'une pile de 109, donc elle contient la feuille **et**
l'interstice que `C2` utilise comme vide. Ce n'est pas un défaut de montage — c'est ce qu'une
fenêtre de 182 µm contient physiquement à cet endroit — mais ça interdit de lire la baisse comme
« le modèle aime moins la profondeur » : il voit aussi autre chose.

⭐ Ce qui reste acquis quoi qu'il en soit : `--pas-couches` **existe désormais sur la ligne de
commande**. Le paramètre était pris par `load_layer_stack` depuis août, testé par sa batterie, et
joignable par personne — donc la seule grandeur capable de corriger la profondeur lue était hors
d'atteinte de toute campagne.

### ⚠⚠ Ce que ce contrôle ne peut pas faire, et ce qu'il ne dit pas

- **Il ne dit pas que la feuille est vierge.** Les fenêtres sont choisies sur la **matière**, pas
  sur l'encre : rien ici ne sait si ces trois faces portent de l'écriture. « Le détecteur ne les
  distingue pas d'un vide » est ce qui est mesuré ; « il n'y a rien à lire » ne l'est pas.
- **Il ne peut pas écarter la spire voisine.** La corrélation entre les deux cartes vaut
  **−0,102 / +0,105 / −0,009** : la carte du vide n'est donc **pas un décalque** de celle de la
  face, pas une transparence de la même colonne. Elle ne dit **rien** de la spire d'à côté, dont
  l'encre n'a aucune raison de tomber là où celle de cette face-ci tombe.
- **À ce pas de balayage la carte est trop petite pour porter une typographie** (`46` le dit déjà
  de lui-même). On compare le **niveau**, la **dispersion** et l'**AUC**, jamais l'interligne.

### ⚠ Ce qui est retiré de la version publiée le matin même

La version précédente annonçait que *« le NIVEAU, lui, se déplace franchement (−0,27 contre
−1,50), donc une lecture par seuil distingue les deux »* — la moitié rassurante du résultat. Sur
des fenêtres réellement posées sur la feuille, cet écart tombe à **−0,03 / −0,43 / −0,42** : nul,
puis **négatif** deux fois. Le niveau ne sauve rien, et la batterie l'asserte désormais dans ce
sens-là.

⚠ Un piège d'outillage payé au passage, pour la troisième fois dans ce dépôt : **deux campagnes ont
tourné en parallèle** sur les mêmes cartes, parce qu'un `nohup` survivant était invisible à
`ps -C python` — le processus s'appelle `python3`. Le remède est un **verrou `flock`** dans l'outil,
pas une vigilance : il est relâché par le noyau quand le processus meurt, quelle que soit la façon
dont il meurt.

---

### C3 ⚠⚠⚠ — le courriel à l'ESRF (ex-H2) : **conditionnel, et sa condition est testable**

~~Coût nul, aucune expérience à monter avant la réponse.~~ Argument géométrique : à 4,7 µm une
feuille fait 8 à 10 voxels au lieu de 4 à 5, donc `d′` monterait pour les treize — au prix de
×8 en volume (20 → 160 To), que le lecteur par fenêtres absorbe.

> ⚠⚠⚠ **2026-09-04 — DEUX DOCUMENTS DE CE DÉPÔT SE CONTREDISENT ICI, et c'est `73` qui a
> sur-affirmé.** Sa formulation — « coût nul, aucune expérience à monter avant la réponse » —
> tient un argument **géométrique** (plus de voxels par feuille). Or [`69`](69_reponse_dun_chercheur_exterieur.md)
> §1.2 donne l'argument **physique** contraire, et il est marqué `[établi]` : à 1,2 m le papier
> rend deux verdicts pour la **même acquisition** — 4,317 µm *haze-limited*, 9,362 µm
> *pixel-limited* — donc la résolution physique y est bornée par la **décohérence** entre 4,3 et
> 9,4 µm, et le binning ×2 a coûté peu. Prédiction chiffrée : le débinage rendrait **au plus
> 1,3–1,5×** de résolution effective.
>
> **Plus de voxels échantillonnant un signal déjà flou ne relèvent pas `d′`.** L'argument
> géométrique de `73` ne suit donc pas de la physique de `69`, et `69` écrit sa condition en
> toutes lettres : *« Cette prédiction est testable sur des données publiques (H2), et **si elle
> est fausse**, la donnée manquante la plus précieuse du prix est une demande à l'ESRF. »*
>
> ⭐⭐ **Et la condition est testable aujourd'hui.** `uv run python src/volume/ou_vit_ce_rouleau.py PHerc0500P2`
> rend `scans publiés → 0.550, 2.215, 4.317, 9.362` et **`volumes reconstruits → les mêmes`** :
> le même objet est publié et téléchargeable aux **deux** échantillonnages, et le lecteur par
> fenêtres (`src/volume/couches_distantes.py`) l'absorbe sans rapatrier 20 To.
>
> **Ordre corrigé** : H2 d'abord, sur données publiques, puis le courriel **seulement si** H2
> réfute la prédiction. Envoyer une demande de 160 To sur un argument que la physique de ce
> dépôt prédit faux coûterait un contact, pas rien.

### ✅✅ H2 est MESURÉ, et la condition du courriel n'est PAS remplie

> 2026-09-04. Mesure : `src/encre/le_debinage_rend_il_quelque_chose.py` (8 contrôles),
> `docs/mesures/le_debinage.json`. Figure : `src/figures/figure_le_debinage.py` (14 contrôles).

Le même objet, `PHerc0500P2`, aux deux échantillonnages natifs, même bras de 1,2 m :

| volume | `d′` médian | IC 95 % | fenêtres |
|---|---:|---|---:|
| natif **fin**, 4,317 µm, 111 keV | **1,44** | [1,25 ; 1,71] | 36 / 700 |
| natif **grossier**, 9,362 µm, 113 keV | **1,43** | [1,32 ; 1,67] | 51 / 700 |
| *fin biné ×2, 8,634 µm (contrôle)* | *1,25* | *[1,18 ; 1,40]* | *39 / 700* |

**Rapport = 1,01**, là où `69` prédisait au plus 1,3–1,5×. Et **les intervalles des deux natifs
se recouvrent largement** — [1,25 ; 1,71] contre [1,32 ; 1,67] — donc rien ne les sépare.

![Le débinage rend-il quelque chose ?](images/75_le_debinage.png)

*Une fenêtre = un point. La bande claire est l'IC 95 % de la médiane, par bootstrap sur les
fenêtres — `64` §1 établit qu'un résumé sans sa dispersion **ne peut pas établir** une
différence, donc trois traits seuls auraient refait cette faute en image.*

> ⭐⭐⭐ **La physique de `69` tient, l'argument géométrique de `73` ne se vérifie pas**, et la
> condition que `69` posait — *« si elle est fausse »* — **n'est pas remplie**. Le courriel à
> l'ESRF n'est donc pas justifié par cette voie.

⚠ **Trois réserves, dites plutôt que tues.**

1. **Ce ne sont pas une acquisition binée deux fois** mais deux acquisitions (mai / 111 keV,
   août / 113 keV). Le bras est le même et 2 keV sur 112 font 1,8 %, dans la plage où `66` §3
   mesure une sensibilité *douce* — le confond est petit et nommé, pas absent.
2. **Le contrôle du binage logiciel donne 1,25**, plus bas que les deux natifs. Son intervalle
   [1,18 ; 1,40] touche celui du grossier, donc il n'est pas non plus séparé — mais il n'appuie
   pas l'idée que biner *n'enlève rien*.
3. **`d′` n'est pas l'AUC d'encre.** C'est la grandeur que l'argument de `73` invoque, et elle
   est sans dimension donc comparable entre campagnes ; une AUC répondrait à une question plus
   large, et c'est `C1`.

⚠ **Ma propre lecture intermédiaire était fausse**, et c'est la leçon de méthode : à 5 et
7 fenêtres j'avais lu 1,18 contre 1,64 et conclu *« le scan fin est pire »*. À 36 et 51, c'est
1,44 contre 1,43. Le piège nº27 du dépôt — **un volume est surtout du remplissage**, 93 % des
sondes tombent dans le vide — et `33` §3–4 bis qui exige 50 à 100 fenêtres.

⚠ **Et l'envoi appartient à l'auteur.** Un courriel à un tiers est un acte vers l'extérieur ;
ce registre peut en préparer la matière, pas le poster.

⚠⚠ **Et un outil disait que le test était impossible.** `corpus_par_energie.py` collectait les
résolutions en filtrant sur `scans[*].properties.pixel_size_um` — or **un seul scan de tout le
corpus** n'a pas cette propriété, et c'est `PHerc0500P2 / 20250507210011-4.317um-1.2m-111keV`,
celui dont H2 a besoin. Il disparaissait donc en silence, et le relevé publiait **trois**
résolutions pour ce rouleau au lieu de quatre. Corrigé (repli sur le `long_id`, en réutilisant
l'analyseur de `ou_vit_ce_rouleau`) : le fichier publie désormais `[0.55, 2.215, 4.317, 9.362]`.

**Première mesure de H2, la moins chère et la plus directe** : `src/encre/separabilite_scan.py`
rend un `d′` **sans dimension, donc comparable entre campagnes** — c'est exactement la grandeur
que l'argument de `73` invoque. Le lancer sur les deux volumes de `PHerc0500P2`, **même région
physique**, décide.

⚠ Deux précautions pour que la comparaison soit appariée : la même région physique n'est pas le
même index de morceau (les voxels n'ont pas la même taille), et `--level` doit être choisi pour
comparer **le natif au natif**, pas un niveau de pyramide d'un volume à un autre.

**Sortie de C** : deux nombres avec leur intervalle. Si l'AUC native à 9,362 µm ne se sépare
pas de 0,5 avec 40 tuiles, la règle ne lit pas à ce régime, et « colonnes visibles partout »
devra être jugé par la typographie (`45`) et le juge à condition vierge (`09`). C'est une
conclusion sur la **méthode de validation**, pas sur le prix.

---

## D. Dette

### D1 ⚠⚠ — re-fonder l'arc d'excision (`03`, `04`, `05`, `07`) — **débloqué**

La conclusion de tête de `07` est **détruite par notre propre mesure** : la réparation fait
passer la proximité de 1,464 → 0,735 % et 3,483 → 2,707 % (−50 % et −22 %), contre son
« 0,37 → 0,38 %, ça ne bouge pas ».

⭐⭐⭐ **Débloqué le 2026-09-04** (`07` §8), et par deux trouvailles :

1. ⚠⚠⚠ **La mesure qui a renversé `07` n'avait AUCUN producteur** dans l'arbre — faite au
   terminal. Le pire cas de `D3` : une mesure qui renverse une conclusion et qu'on ne peut pas
   relancer. `src/excision/reparation_et_proximite.py` existe désormais.
2. ⭐⭐ **Le blocage venait d'une généralisation depuis le mauvais rouleau.** `07` §7 conclut que
   le cas discriminant n'est pas montable ; c'est vrai de `PHerc0172` (10 traces éligibles) et
   **faux de Scroll 1**, qui en a **34**, curatées, span médian 2,70 tours.

**Et à provenance égale, le SIGNE change** : `w010-027` **+398 %**, `w028-037` **−17 %**.

3. ⚠⚠⚠ **Puis la mesure passée à n = 10 a détruit ce résultat-là aussi, et le contrôle que
   j'avais écrit pour l'en protéger ne pouvait pas échouer** (`07` §10). J'avais vérifié que
   trois runs de la *même* commande rendent le *même* nombre — c'est-à-dire la
   **reproductibilité** — et j'en avais conclu la **stabilité sous ré-échantillonnage**, qui est
   une autre propriété. Or `proximity.py` tire `choice(points.shape[0], …)` : la réparation
   change le nombre de points, donc le tirage, donc « avant » et « après » ne portent pas sur les
   mêmes cellules. Balayage de 12 graines sur le **même fichier** : `fraction_below_third` bouge
   de **35 à 229 %**, soit plus que la réparation sur **9 traces sur 10**. Et son numérateur
   tient sur un chiffre — les +398 % sont **une cellule qui en devient cinq**.

⭐⭐ **Ce que ça laisse debout, et c'est plus que ça n'en a l'air.** Le premier §8 de `07` valide
cette colonne par un rho de +0,769 **entre traces**, où le signal (403 %) écrase le bruit (82 %) :
ce classement tient. Ce qui tombe est son transport vers une **différence appariée**, où l'effet
médian (35 %) est plus petit que le bruit. Et `proximity.py` publie déjà la colonne qu'il fallait
lire — `shortfall`, sans seuil, dont l'étendue de graine reste **sous 5 %**.

⭐⭐⭐ **Rejouée sur `shortfall`, la réparation ne déplace RIEN de mesurable** : zéro paire sur
dix au-delà du bruit de graine (±5 %), signe mélangé (3 en hausse, 7 en baisse), et face au bruit
de sa *propre* trace la majorité reste dedans. **Le titre d'origine de `07` est donc restauré**,
pour une bien meilleure raison que celle qu'il donnait. ⚠ *Ne déplace rien de mesurable* n'est pas
*ne fait rien* : ce qui est établi est une **borne** — un effet inférieur à ~5 %, la dispersion
d'un tirage de 20 000 cellules. Le distinguer demanderait un tirage **apparié**, c'est-à-dire
mesuré sur les cellules qui survivent à la réparation, des deux côtés.

4. ⚠⚠⚠ **Et la réparation elle-même n'est pas déterministe.** Le même `windcheck transform`, sur
   la même trace, a retiré **3 696** quads puis **3 698** — donc le Δ de cette trace passe de
   −3,5 % à **+21,2 %** entre deux exécutions du même pipeline. Un signe qui s'inverse quand rien
   n'a changé est la démonstration la plus courte que la table du §8 ne portait pas d'information.
   ⭐ Le dépôt a déjà rencontré cette forme (`44` : rng semé par l'horloge + 22 fils), et son
   remède est connu — une graine posée et `thread_limit: 1`.

5. ⭐⭐⭐ **Et le balayage `--population` a trouvé bien plus que ça : le premier §8 de `07` est
   PÉRIMÉ.** Le §9 a corrigé le rayon de recherche (4× trop grand, il trouvait la spire voisine
   et noyait l'anomalie dedans) et n'a re-mesuré **qu'une colonne**. Le §8, qui compare les
   grandeurs entre elles et conclut que le seuil *« n'est ni arbitraire ni supprimable »*, porte
   encore l'ancien rayon. Au bon rayon : l'écart entre `fraction_below_third` et `shortfall`
   tombe de **0,429 à 0,054**, et le « plateau puis effondrement » qui justifiait le seuil devient
   un plateau **sur toute la plage** (chute 0,477 → **0,025**). **Le seuil ne sélectionne aucun
   régime.**

6. ⚠⚠⚠ **Et personne ne l'avait rejoué parce que le producteur ne tournait plus.**
   `run_proximity.sh` appelait `python -m excision.proximity`, qui ne résout plus, et avalait
   l'erreur : un run qui ne mesurait **rien** rendait « 0 mesurées, 55 sans mesure » **et sortait
   en 0**. La panne totale ressemblait à une population vide. Corrigé, et un run qui ne mesure
   rien ne sort plus en 0.

7. ⚠⚠⚠ **Trois passages sur la même affirmation, tranchés par la mesure à chaque fois.**
   (1) J'écris que `windcheck transform` n'est pas déterministe, depuis **deux sorties de
   terminal** (3 696 puis 3 698 quads). (2) Le mode `--determinisme` à trois répétitions rend
   trois certificats **identiques** : je rétracte. (3) À **six** répétitions — 3698, 3696, 3696,
   3696, **3691**, 3696 — **trois certificats distincts**. La première affirmation était juste,
   la rétractation était fausse, et elle l'était **par chance**. ⭐ Son propre commentaire disait
   pourtant que trois répétitions sont une preuve faible de déterminisme : **une réserve écrite
   ne dispense pas de la mesure qu'elle appelle**. Variation bornée à **0,19 %** des quads
   retirés, cause inconnue, forme déjà rencontrée dans `44` (rng semé par l'horloge, 22 fils).

⭐ **Conséquence pratique** : `shortfall` devient la colonne de référence de l'arc. Elle ordonne
aussi bien (médiane +0,765 contre +0,780) et son bruit est **4,5 fois plus serré**. Pour toute
question de **différence** — celle que la chaîne de déroulage pose en boucle — c'est la seule des
deux qui puisse répondre.

8. ⭐⭐⭐ **Et la cause est COMMUNE aux trois familles.** Rejoué au bon rayon, `06` §3.2 aussi :
   boule 400 **+0,560 → +0,803**, boule 200 **+0,474 → +0,738**. Le verdict survit (la bande
   reste devant) mais l'écart tombe de **0,209 à 0,036**, sous le bruit du rho, et la **largeur**
   de la bande cesse aussi de compter (étendue 0,050 → **0,010**). Donc **trois** paramètres
   cessent de compter ensemble : aucun n'était mal choisi, c'est le **rayon** qui les faisait
   paraître importants. Les fichiers le disent eux-mêmes — une distance est plafonnée par le
   rayon, donc l'ancien impose **≥ 382,6 µm = 2,7 pas de feuille**, contre **0,88** au corrigé.

9. ✅ **Mais l'explication du §6 de `07` SURVIT, plus forte.** Le mécanisme (« l'anomalie
   normalise sa propre référence ») tient au rayon corrigé sur **34 traces sur 34** au lieu de
   43 sur 45, Wilcoxon **1,2e-10**. Ce n'était donc pas un artefact du rayon ; c'est sa
   **conséquence** sur la corrélation qui a disparu. ⚠ Cette mesure n'avait **aucun
   consommateur** : le lecteur existe et retrouve **exactement** les quatre nombres publiés.

10. ⚠ **Ce qui reste une vraie différence après correction est la COUVERTURE**, pas le rho : la
    boule de rayon 100 ne mesure que **20,7 %** des cellules, et aucun rayon ne répare ça.

11. ✅ **Et la leçon d'outillage du §9 est enfin appliquée** : `proximity.py` n'écrivait pas son
    instrument, `baseline_sweep.py` l'écrivait depuis août sous le nom `echelle`. Les deux
    écrivent désormais le **même** bloc. Conséquence immédiate : la question que `07` §9 déclarait
    insoluble est **tranchée par l'artefact** — `sweep_PHerc1667.jsonl` déclare
    `voxel_um 7,91`, donc 18 voxels y font **142,4 µm** et la ligne PHerc1667 était bien appariée.

⭐⭐ **La marche suivante est identifiée ET rendue possible par une mesure.** La borne de 5 % vient
du tirage **non apparié** : `proximity.py` tire dans l'index des cellules *valides*, dont le nombre
change avec la réparation. Or **la grille de paramétrisation, elle, ne change pas** — mesuré sur
`w064-068` : `756 × 2940` des deux côtés, 1 999 850 → 1 999 708 cellules valides, soit **142
perdues sur deux millions**. Donc la cellule (i, j) d'avant EST celle d'après, et un tirage par
**position de grille** (plutôt que par index de cellule valide) serait apparié par construction —
le bruit d'échantillonnage disparaîtrait du comparatif au lieu d'être borné.

⚠ Ce doit être un mode **opt-in** (`--tirage-par-position`) : changer le tirage par défaut
déplacerait toute mesure déjà publiée.

12. ✅✅ **D1 EST FERMÉ — la conclusion-titre de `07` est confirmée par un instrument capable de
    la contredire.** Le tirage apparié est écrit et mesuré (`07` §12) : effet médian sur
    `shortfall` **1,58 % → 0,07 %**, facteur **22**, et **10 traces sur 10** sous leur propre
    bruit de graine contre 4 qui en sortaient. ⭐ Le plus parlant n'est pas le pourcentage mais
    le **compte** : à échantillon égal, **7 traces sur 10 comptent exactement les mêmes cellules
    sous le tiers avant et après**. La réparation retire des centaines à des milliers de quads et
    ne déplace **aucune** des cellules que la métrique signale. La borne passe de ~5 % à
    **0,6 %** au pire.

⚠ Ce n'est pas « la réparation ne fait rien » : elle supprime bien les contacts d'auto-intersection
(`07` §3, 11 673 → 0). Ce qu'elle ne déplace pas, c'est la **proximité anormale entre régions non
adjacentes**, qui est une autre propriété du même maillage.

⚠ **Restant** : les `sweep_PHerc*.jsonl` des **autres rouleaux** sans déclaration
(`sweep_PHerc0139`, `sweep_0139_*`, `sweep_s1_pas`) n'ont aucune trace commune avec Scroll 1, donc
`le_rayon_des_mesures.py` ne peut ni les dater par comparaison ni lire leur déclaration — il
faudrait les régénérer, ce qui les fera déclarer. ✅ **Et la non-reproductibilité de la réparation est ÉLUCIDÉE** (`07` §10) : ce n'est
pas un défaut mais une propriété déclarée. L'excision est une optimisation résolue composante par
composante sous un **budget d'horloge par segment** (`improvement_budget_s_per_segment: 120.0`,
*« never a per-component budget »*), donc combien de composantes atteignent le solveur exact
dépend de la vitesse de la machine. Corrélation mesurée : `(163 exact, 18 glouton) → 3 696`,
`(164, 17) → 3 691`. La `failure_rule` de `windcheck` dit qu'un dépassement *« costs an
optimality claim, never an artifact »* — la sortie est toujours **valide**. ⚠ Le remède de `44`
(graine + un fil) a été **testé et réfuté**. Aucun drapeau utilisateur ne peut rendre la
réparation bit-reproductible ; il faut **réparer une fois et garder la sortie**, ce que fait déjà
chaque paire du §12.

### ✅✅ D2 — le contrôle P1 bis : **FAIT le 2026-09-05, et l'hypothèse TIENT**

> ⚠⚠⚠ **Ce n'était pas bloqué, et le blocage était mon erreur de recherche.** Ce registre
> annonçait « le rapport *budget* n'est ni dans `docs/`, ni dans `src/`, ni dans `store/` ». Il
> **est** dans l'arbre, à `docs/registres/anteriorite_resultats_de_tete.md:593`. J'avais cherché
> un fichier **nommé** « budget » au lieu de chercher le **concept** — la règle que ce dépôt
> écrit partout, enfreinte par celui qui l'écrit.

> Mesure : `src/tracecheck/modele_de_proprete.py` (15 contrôles), `docs/mesures/p1bis.json`.
>
> ```
> uv run python src/tracecheck/modele_de_proprete.py --json docs/mesures/p1bis.json
> uv run python src/tracecheck/modele_de_proprete.py --verifier
> ```

⚠⚠ **Et le ×15,9 n'avait pas de producteur non plus.** Le rapport annonce *« Vérification
reproductible : `scratchpad/check_windcheck_model.py` (calcul dans l'arbre, pas en ligne de
commande) »* — **ce fichier n'existe pas**. Un nombre publié dont le calcul n'est nulle part est
exactement ce que ce dépôt refuse ailleurs. Il est désormais dans l'arbre, et il reproduit les
trois nombres du rapport : **12 085 → 192 541 cellules, ×15,93**.

⭐ Le facteur exigé est **indépendant de `q`** — c'est un rapport de deux logarithmes — donc le
résultat survit à une révision du modèle publié par `windcheck`.

### Le contrôle lui-même : « cellules ∝ aire » — **oui, à 1,6 % près**

Le rapport laissait l'hypothèse ouverte : *« cellules ∝ aire est une hypothèse que l'article n'a
pas vérifiée et qu'il peut trancher sur ses propres grilles »*. Les grilles sont sur le disque aux
**deux** plafonds (`data/tirages/` à 120, `data/tirages_plafond/` à 400).

| rouleau | cellules valides | aire | rapport des deux croissances |
|---|---:|---:|---:|
| `PHerc0125` | 56 644 → 202 591 (**×3,58**) | 19,83 → 71,31 cm² (**×3,60**) | **0,99** |
| `PHerc0191` | 56 644 → 227 528 (**×4,02**) | 19,83 → 80,39 cm² (**×4,05**) | **0,99** |

⭐⭐ **Et la forme forte, qui est celle qui tranche** : sur les **24 tirages** des deux rouleaux et
des deux plafonds, la densité vaut **2 812 à 2 857 cellules par cm²** — une étendue relative de
**1,6 %**. « Proportionnel » n'est plus une hypothèse ; un rapport de médianes aurait pu coïncider
pour deux raisons, une densité constante sur vingt-quatre tirages non.

> **Donc P1 bis tient.** Le modèle publié exige **×15,9** de cellules pour passer de 1 tirage sale
> sur 12 à 9 sur 12 ; l'observé est **×4,0 au plus**. Le basculement de propreté est **plus raide
> que la seule arithmétique de taille**, donc le budget fait quelque chose au-delà de grandir la
> surface — et ça, `windcheck` ne le dit pas.

⚠ **La seconde réserve du rapport reste entière** : 1/12 et 9/12 sur n = 12 portent des intervalles
larges. Ce qui est levé est l'hypothèse (a), pas (b).

### ⚠⚠⚠ Un fait trouvé en chemin : au plafond d'origine, les DOUZE tirages ont le même compte

**56 644 cellules valides exactement**, pour les six tirages de `PHerc0125` **et** les six de
`PHerc0191`, sur une grille 242 × 242 remplie à 96,7 %. Les aires, elles, diffèrent légèrement
(19,823 à 19,981 cm²) : les traces sont bien différentes, mais leur **compte de cellules est fixé
par le plafond**, pas par la trace. C'est *« la stabilité était une troncature »* (`35` §3bis) vu
d'un angle plus net — et ça rend le point de départ **dégénéré**, ce que la batterie assère plutôt
que de le masquer. Le contrôle ne tient donc pas par ce point-là mais par la **densité**, mesurée
des deux côtés.

⚠ **Deux sondes n'ont rien trouvé, et c'est ce qui a produit le contrôle suivant.** Compter
**toutes** les cellules de la grille, puis n'en lire qu'**un seul** plan : la batterie est restée
verte les deux fois. Non par faiblesse — sur ces grilles les trois plans déclarent les mêmes
absents (`x = y = z = 56 644`) et le remplissage est de 96,7 %, donc les trois comptages
coïncident. Mais « ils coïncident ici » est une **propriété des données**, et s'y fier sans la
mesurer est le piège habituel : `concordance_des_plans` la mesure désormais.

---

### D4 ⚠⚠⚠ — 67 batteries vertes sur 160 n'atteignent pas le nombre qu'elles publient

Document dédié : [`80`](80_la_batterie_natteint_pas_le_nombre.md). Suite de
[`61`](61_les_batteries_qui_ne_pouvaient_pas_echouer.md), dont il franchit la limite finale —
*« ce contrôle dit qu'une batterie peut échouer, jamais qu'elle teste quelque chose d'utile »*.

![le chemin du nombre publié](images/80_le_chemin_du_nombre_publie.png)

**Le défaut, payé le 2026-09-05** : un de mes patchs a échoué à mi-course et n'a écrit que son
dernier bloc, laissant l'enregistrement de `derouler_des_deux_bords.py` référencer trois
variables inexistantes — **et la batterie est restée verte**, parce qu'elle n'appelle pas
`mesurer`. Une batterie verte sur un module dont le seul chemin non testé est celui qui produit
le nombre publié est une batterie qui ne peut pas échouer **là où ça compte**.

⚠ La raison n'est pas de la négligence, elle est mécanique : ce chemin **lit le dépôt distant**,
et `temoins.sh` exige que ses batteries tournent hors ligne. Le chemin le plus important du
module était le seul qu'on ne pouvait pas exercer.

**Le balayage** (`src/depot/le_chemin_du_nombre_publie.py`, propriété du graphe d'appels, lue
sans rien exécuter) :

| | |
|---|---:|
| modules qui publient une mesure ou une figure | **160** |
| dont la batterie n'atteint pas ce chemin | **67** (44 %) |
| fonctions hors de portée | **102** |

⚠⚠ **La portée a été resserrée après le premier chiffre**, et il était trop large : la règle
comptait comme publieur tout module *mentionnant* `docs/mesures`, donc aussi les purs lecteurs.
Le signe retenu est l'**écriture**, sous ses deux formes — sérialiser et écrire un fichier (une
mesure), ou enregistrer une image (une figure).

⭐ **La branche laissée dehors porte toujours le même nom** : `mesurer` dans **13** modules,
`dessiner` dans **10**, `rapporter` dans **6**. Ce sont les deux verbes qui publient — l'un rend
le nombre, l'autre l'image. Par famille : `graine` **9/10**, `encre` **23/32**, `nappe`
**12/29** (elle était à 15), `figures` **10/50**.

⚠⚠ **Un chiffre calculé puis retiré** : « les modules dont la tête de chemin est dehors », 67 sur
67. C'est une **identité** — la couverture se propage vers le bas — donc un nombre qui ne peut
prendre qu'une valeur et se lirait comme une découverte.

**Réparé, cinq modules et une matière fabriquée.** `derouler_des_deux_bords`,
`derouler_par_le_pas_normal`, `le_raccrochage_a_la_matiere`, `la_longueur_locale_du_pas` et
`derouler_en_raccrochant` reçoivent leur matière par paramètre, le défaut restant le dépôt
distant (donc les nombres publiés ne bougent pas d'une virgule). Ce qui est injectable est la
**matière**, pas le découpage : boîte, seuil de cellules, encadrements, marche, combinaison,
pondération et enregistrement restent dans `mesurer`. Les batteries : 32 → **46**, 9 → **17**,
46 → **54**, 20 → **30**, 63 → **75**.

⭐ Et la matière est **promue dès le deuxième appelant** : `src/nappe/le_corpus_des_spires.py`
(**16 contrôles**) porte l'unique lecteur du corpus, l'unique fixture de spires **et** le volume
fabriqué. Cinq modules de `src/nappe/` avaient chacun leur copie du lecteur, et deux dérouleurs
comparés sur deux lectures différentes mesurent d'abord leur désaccord de lecture.

⚠⚠⚠ **DEUX VUES D'UN MÊME OBJET, PAS DEUX OBJETS.** Un dérouleur lit les spires comme des
**surfaces** et le volume comme une **intensité** : décrire l'objet deux fois ferait un corpus
dont les feuilles ne sont pas là où le volume les met, et le raccrochage snapperait sur de la
matière qui contredit ses ancres — en rendant des nombres parfaitement stables. La géométrie est
dite **une fois**, l'intensité en est **dérivée**. Le contrôle qui lie les deux : le gabarit lu
autour d'une spire doit avoir sa **crête sur zéro**.

**Trois ronds-trips** : on injecte des feuilles à 135,5 µm, la mesure rend 136,3 µm (ne pas
bouger), 136,1 µm (longueur lue) et 63,0 voxels contre 61,2 (pas entre crêtes). Tolérance
**dérivée** de l'ondulation, jamais choisie. Et les trois réponses du lecteur de volume — une
absence se mémorise, un incident se réessaie, un incident qui persiste **lève** — sont exercées
pour la première fois, alors qu'elles avaient été écrites après un incident réel.

⚠⚠⚠ **La fixture doit être ONDULÉE** : des spires parfaitement décalées du pas sont atteintes
*exactement* par un pas normal, donc toutes les erreurs vaudraient zéro et chaque comparaison
serait satisfaite par des zéros. **Dix sondes** remettent chacune un défaut — fixture aplatie,
spires collées, boîte qui ne découpe plus, seuil qui ne filtre plus, corpus qui gagne une clé,
affichage lisant une clé renommée, figure lisant une clé absente, spire absente non refusée,
demi-épaisseur devenue épaisseur, témoin du pas nul figé — et toutes font rougir la batterie
qu'elles visent. ⚠ Une sonde reste **verte** à bon droit : le contrôle de forme du corpus a
déménagé chez son propriétaire, et le dupliquer chez ses cinq appelants ferait cinq copies d'une
même exigence, libres de diverger.

⚠⚠ **Et un second constat, trouvé en cherchant où inscrire la batterie corrigée : 44 batteries
que `temoins.sh` ne lançait pas** — toute la campagne de déroulage et ses figures. Le harnais
rendait « 184 batteries ALL PASS » sans les voir. Le garde-fou qui les nomme existait déjà ; il
n'avait pas tourné, le harnais complet étant long. Un contrôle qu'on ne lance pas est, pour la
durée où on ne le lance pas, exactement un contrôle absent. Les 44 ont été lancées **une par une
avant d'être inscrites** : toutes vertes, la plus lente en soixante secondes.

⚠⚠ **Deux de mes contrôles ne pouvaient pas échouer, et ce sont les sondes qui l'ont dit.** Un
refus « hors de la boîte » où seules les spires étaient déplacées : le volume n'ayant rien à lire
là-bas, la mesure refusait pour **absence de matière**, et retirer le découpage laissait le
contrôle vert. Et une inégalité **large** (« pas moins de cellules ») qu'un découpage inerte
satisfait, devenue stricte. Les deux sont le même défaut de méthode : un contrôle dont on n'a pas
cherché par quelle autre voie il pourrait passer au vert.

**Reste à faire** : 67 modules. L'ordre suit la mesure — `mesurer` d'abord (13), puis `dessiner`
(10), c'est-à-dire le nombre puis l'image. La famille `graine` (**9 sur 10**) et `encre`
(**23 sur 32**) sont les prochaines par densité.

```
uv run python src/depot/le_chemin_du_nombre_publie.py   # le balayage, par famille et par nom
```

### D3 ⚠ — 41 → **33** scripts sans appelant, et aucune des huit réparations n'était une formalité

> Entamé le 2026-09-04. `src/depot/appelants.py` juge **307 scripts**. La méthode : demander
> pour chaque orphelin *« son résultat est-il publié quelque part ? »*.

⭐⭐ **Un script cité sans commande n'est pas du code mort — c'est une mesure NON
REPRODUCTIBLE**, ce qui est pire, parce que ça ne se voit pas.

**Les huit réparées, et ce qu'elles cachaient :**

| quoi | ce qui n'était pas refaisable |
|---|---|
| `figure_comparaison`, `figure_deux_axes` | deux images **affichées dans un doc** sans leur commande de régénération — la règle du dépôt. ⚠ Vérifié qu'elles régénèrent **à l'identique** |
| `couches_distantes` | la fenêtre de Scroll 1 du `77` §10, mentionnée sans sa commande |
| `apprendre/04` à `08` | le README documente **8 épisodes** et n'en montrait que **2** à fabriquer |
| **`run_proximity.sh`** | ⚠⚠ produit `proximity_scroll1.jsonl`, la mesure de **tout l'arc d'excision** (D1), citée dans deux documents — **sa commande n'était nulle part** |

**Ce qui reste, mesuré plutôt que supposé :**

| catégorie | n | constat |
|---|---:|---|
| **cités dans un doc, sans leur commande** | **9** | même défaut que les huit ci-dessus — à traiter pareil |
| cités nulle part, aucune sortie JSON | 4 | ⭐ **LUS — aucun n'est mort**, voir ci-dessous |
| figures sans sortie par défaut | 5 | l'image est passée en argument, donc rien ne dit laquelle |
| reste | 15 | non classé |

#### ⭐⭐ Les quatre « candidats à déclarer morts », lus — et aucun ne l'est

La règle disait *« à lire avant : un script de 122 lignes peut porter un savoir »*. Elle a payé :
les quatre portent une **question ouverte**, et ils sont orphelins parce que leur **résultat**
n'a jamais été publié, pas parce qu'ils ne valent rien.

| script | ce qu'il demande |
|---|---|
| `campagne_prediction_paris4` | **laquelle des deux prédictions de surface** de `PHercParis4` vaut-il mieux tracer ? (`48` monte l'expérience là ; ce rouleau en publie **deux**) |
| `sens_de_la_normale` | la pile est-elle rendue **du bon côté** de la surface ? (`38` mesure que le pic est au bord **à toutes les fenêtres**, même sur une trace posée sur la graine d'un segment officiel) |
| `tracer_tous_candidats` | et si la graine choisie était la **moins bien soutenue** de celles qu'on avait ? (`trouver_graine` classe sur la planéité **seule**) |
| `juger_nappe` | ⚠⚠⚠ cas à part — voir ci-dessous |

#### ⚠⚠⚠ `juger_nappe.sh` : une déduplication écrite, jamais adoptée, et devenue une 3ᵉ copie

Son en-tête dit pourquoi il existe : `spire_suivante.sh` et `etendre_nappe.sh` portaient chacun
une copie **verbatim** de la fonction de jugement, et les deux **avaient déjà divergé** — la
réserve `--au-bord` câblée dans l'une avant l'autre, si bien qu'*« un verdict de campagne portait
le complément et l'autre non »*.

**Vérifié aujourd'hui** : ni l'un ni l'autre ne l'appelle. La divergence a été réparée **dans
chaque copie** — les trois passent maintenant `--au-bord`. Donc :

- ✅ la divergence de l'époque est **corrigée** ;
- ⚠⚠ mais la déduplication n'a **pas** été adoptée, et il y a désormais **trois** exemplaires de
  la même logique de jugement. L'argument de son propre en-tête — *deux chemins de jugement sont
  deux occasions de ne pas s'accorder* — vaut à trois.

> ⭐ **Le remède n'est pas de le déclarer mort**, c'est de l'**adopter** dans les deux appelants.

#### ✅ **Fait le 2026-09-04, et l'équivalence est PROUVÉE avant l'adoption**

⚠⚠⚠ **Les trois copies n'étaient pas équivalentes** : `spire_suivante` **n'avait pas la garde
`REPLIEE`** — le plafond de croisements par cm² vérifié *avant de payer les rendus*. Il payait
donc des rendus sur des surfaces manifestement repliées que les deux autres abandonnaient.

**Un refactor ne change pas le comportement.** Le plafond est donc devenu **désactivable** par
une chaîne vide, et `spire_suivante` le désactive — l'activer est une décision à prendre à part,
puisqu'il a produit des résultats publiés.

**La preuve, statique et insensible à l'ordre** (un jugement complet paie un rendu, donc une
preuve par exécution coûterait vingt minutes par cas) :

| appelant | chemin adopté | ancienne fonction | différences |
|---|---:|---:|---|
| `spire_suivante` | 41 lignes | 41 lignes | **0** |
| `etendre_nappe` | 54 | 55 | **5, toutes expliquées** |

Les cinq d'`etendre_nappe` : le `if` gagne un test `-n "$PLAFOND"` qui est **vrai** chez lui, et
l'`echo` passe de deux arguments à un. ⚠ **Ce dernier change la sortie d'un espace** — l'ancien
écrivait `cm²,␣␣au-dessus` (espace final + espace de jointure), le nouveau `cm²,␣au-dessus`.
Cosmétique, et dit plutôt que passé sous silence.

⚠ Un piège payé en chemin : `VAR=x . fichier` a une sémantique subtile — un test a montré que
`PLAFOND` prenait et `LIGNES_VERDICT` non. Les deux sont sur leurs **propres lignes**.

#### ⭐⭐ Et le détecteur ne voyait pas le sourcing — un vrai manque, pas un cas à contourner

`appelants.py` ne reconnaissait aucune forme `. fichier` / `source fichier`. Or **sourcer une
bibliothèque shell, c'est l'exécuter** : son code de premier niveau tourne et ses fonctions
deviennent disponibles. Toute bibliothèque shell du dépôt passait donc pour orpheline — ce qui
est exactement arrivé à `juger_nappe.sh`, écrit pour dédupliquer et signalé comme exécuté par
personne.

La forme est **ancrée en début de ligne**, ce qui sépare une exécution d'une mention. ⚠ Sonde :
un document qui cite le fichier au fil d'une phrase rend `[]`, un `.` à chemin calculé et un
`source` littéral sont détectés. Les 21 contrôles du détecteur restent verts.

**24 orphelins** (41 au départ). ⭐ Huit de plus rattachés le **2026-09-05**, et aucun n'était
une formalité :

| quoi | ce qui n'était pas refaisable |
|---|---|
| `figure_profondeur` (`12` §1bis) | l'image **ne se régénérait plus depuis les données de l'arbre** : trois nombres du document avaient dérivé, et la version publiée montrait deux panneaux là où les mesures en donnent trois |
| `figure_difficulte` (`16`) | vérifié **octet pour octet** (md5 `a163cd18…`) |
| `campagne_temoin_typographique` (`46`) | tous ses réglages sont des variables d'environnement, donc la commande nue reproduit la campagne — encore fallait-il l'écrire |
| **`excision/measure.py` + `analyse.py`** (`04`) | ⚠⚠ le `p = 0,859` est cité dans **quatre** documents et `analyse.py` n'est nommé dans **aucun**. Vérifié hors ligne : rend le tableau publié à l'identique |
| `table_pas` (`26` §9) | la colonne « mauvaise graine » n'était atteignable qu'en lisant le code, la bonne étant le défaut de l'outil |

### ⚠⚠⚠ Et le registre de lecture avait un point aveugle de dix documents

`src/depot/fiches_a_jour.py` (17 contrôles) compare chaque fiche au document qu'elle résume —
rien ne le faisait, donc une fiche pouvait décrire un fichier qui avait bougé de trente-cinq
lignes. Trois avaient dérivé, et **dix fiches sur soixante-trois portaient une remarque derrière
leur nombre** (« ⚠ (438 quand la fiche a été écrite…) ») qui les rendait invisibles à ma première
version du motif — le contrôle était aveugle à la population la plus à risque.

Puis le point aveugle **symétrique**, qui vaut plus cher : **les dix documents les plus récents —
`69` à `78` — n'ont aucune fiche**. Le registre se lit *à la place* des documents, donc son silence
sur eux se lisait comme une couverture complète.

> ⚠ **Non fait le 2026-09-04, et volontairement** : écrire dix fiches demande de lire dix
> documents pour de bon. Une fiche bâclée est pire que pas de fiche — elle a l'air d'une lecture.
> C'est une tâche à part ; ce qui était fait, c'est qu'elle ne pouvait plus être **oubliée en
> silence**.
>
> ✅✅ **FAIT le 2026-09-05** : les onze documents sans fiche en ont une, celui-ci compris, chacune
> avec ses deux lignes de preuve de lecture intégrale. **81 fiches, 0 document sans fiche.**
>
> ⚠⚠⚠ **Et le contrôle lui-même avait un TROISIÈME point aveugle, plus silencieux que les deux
> précédents.** Les fiches `43` à `49`, écrites d'un même lot, séparent leur titre de leur compte
> par une **ligne vide**, et le motif exigeait l'enchaînement immédiat : ces **sept fiches
> n'étaient pas « en dérive », elles étaient INVISIBLES**. `48` annonçait 342 lignes pour un
> document qui en faisait 405 pendant que le registre disait « 0 en dérive », et **trois** des
> sept dérivaient réellement — dont deux documents auxquels la session n'avait pas touché.
> ⭐ Un garde-fou ne doit pas dépendre d'un blanc : le séparateur est désormais **capturé et
> recopié** plutôt que normalisé, parce que réécrire sept fiches pour satisfaire une regex serait
> laisser le contrôle changer les données.
```
uv run python src/depot/fiches_a_jour.py            # dérives + documents sans fiche
uv run python src/depot/fiches_a_jour.py --corriger  # les comptes seulement, jamais le résumé
```

⚠ Une fausse alerte à moi : j'ai cru `proximity_scroll1.json` manquant, il existe en `.jsonl`.
Mon motif cherchait la mauvaise extension.

⚠⚠ La règle reste celle du registre : **rattaché à un appelant ou déclaré mort**, jamais laissé
dans l'entre-deux — un script gardé « au cas où » est un script que personne ne relancera et qui
pourrira sans que rien ne le dise.

---

## E. Ce qui est HORS registre, et pourquoi

- **La soumission Progress Prize** — l'auteur l'a mise hors périmètre (*« fait tout sauf la
  soumission »*).
- **Le second papier (`72`)** — ⚠⚠⚠ c'est une **occasion de publication, pas un progrès vers
  le prix**, et sa mesure porteuse est C1. Il n'avance qu'avec C.
- **H3 et H6 de `69`** — répondues par le dépôt (`73` §1) : la carte locale de qualité existe
  déjà sous deux formes, et le prior n'est pas universel.
