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

### A2 bis ⭐⭐⭐ — le champ d'identité SANS référent — **débloqué le 2026-09-04** (`78`)

⭐ **Cinq rouleaux publient leur axe** (`78`), dont `PHerc0139`. Un nombre d'enroulement se
construit à partir de **l'axe et du pas**, pas de spires déjà tracées — donc il répondrait
**partout**, ce qui est précisément la limite dure du champ de `77`.

⚠ Ce que le dépôt sait déjà et qui borne l'espoir (`26` §7) : les `.normal-grids` publiées sont
**dérivées de la prédiction** que le traceur suit déjà. Un champ bâti dessus hériterait de la
prédiction, pas d'une information neuve.

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

⚠⚠⚠ **Restant sur A3, et c'est PLUS GRAVE que ce qui était écrit ici.** La phrase précédente
disait *« le canal est écrit au bon nom et au bon format ; rien ne fait tourner `villa` »*.
Vérifié le 2026-09-04 : **rien n'écrit le canal du tout.**

- `le_masque_dapprobation.py` ne contient **aucun `imwrite`**, et son parseur n'a **pas** le
  drapeau `--ecrire` que sa propre ligne d'usage documente — la commande écrite dans le fichier
  échoue sur `unrecognized arguments`.
- **Aucun `approval.tif` n'existe sur disque**, ni dans `data/`, ni dans `docs/`.
- Le blocage n'est donc pas en aval (`villa`) mais en amont : le fichier dont tout dépend n'est
  jamais produit.

⭐ **Et le contrat d'acceptation, lui, est lisible et bon marché à honorer.**
`data/repos/villa/lasagna/approval_inpaint.py` le dit en trois lignes :
`required = ["x.tif", "y.tif", "z.tif", "meta.json", "approval.tif"]`, la forme du masque doit
égaler celle de la grille, et *« any nonzero sample is approved »* — donc n'importe quel dtype.
Ses deux fonctions d'acceptation n'importent que `numpy` et `tifffile` : **elles se lancent sur
notre masque sans faire tourner l'optimiseur**, et c'est exactement ce que « l'accepte » veut
dire au niveau du fichier.

**Ce qu'il reste à faire, dans l'ordre** : (1) un `--ecrire` qui projette le verdict par cellule
du champ (z, θ) sur la **grille tifxyz** d'une trace réelle et écrit `approval.tif` à côté de
`x/y/z.tif` ; (2) le passer à `load_approval_mask` et `_load_tifxyz_arrays` de `villa`, avec un
bras négatif — un masque de mauvaise forme doit être **refusé**, sinon le contrôle ne peut pas
échouer.

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

> **Ce qui reste à faire, et c'est petit** : que `44` nomme son volume. Le contrôle
> `provenance_du_voxel_reconstructible` tombera ce jour-là, et la correction passera de
> transportable-en-feuilles à calculable-en-micromètres.

> ⚠ **Le seul contrôle qui vaudrait d'être monté** : refaire `couverture_publiee.py` contre la
> surface **recalée sur la bande** plutôt que contre la surface publiée. Si l'écart tombe, le
> budget est bien gonflé ; sinon, mon §10 ne s'applique pas à cette échelle-là.

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
| **A3** | ⚠⚠⚠ **rien n'écrit le canal** | corrigé le 2026-09-04 : `le_masque_dapprobation.py` n'a **aucun `imwrite`**, son `--ecrire` documenté **n'existe pas** dans le parseur, et aucun `approval.tif` n'est sur disque. Le blocage est en amont de `villa`, pas en aval |
| **A3** | ⚠⚠ **aucun `approval.tif` peint n'est publié** | donc « le calculé vaut-il l'humain » reste **non montable**. Vérifié au listing S3 (`73` §0) |
| **A3** | le masque n'a été mesuré que sur `PHerc0139` | `PHerc0172` ne sépare qu'après exclusion du trou |
| **A5** | ⭐⭐ le **plancher** : une spire publiée est à **20,8 µm** de la matière *à l'échelle où le champ travaille* (`77` §10), donc l'erreur propre du champ est entre **28 et 49 µm**, **44** si indépendantes — et l'indépendance est **vérifiée** (corrélation ≤ 0,08 entre voisines) | mesuré en coupe sur **six** spires, dont cinq consécutives ; resserrer demanderait une règle autre que la spire publiée |
| **A5** | l'extraction porte **une feuille** (47 µm), pas deux | mesuré : réinjecter une spire prédite ne change **rien** — le champ est un juge, pas un générateur |
| **A5** | ⚠ la structure angulaire de l'écart (**71 µm**, 45 % de la médiane) **n'améliore pas** l'extrapolation | mesuré : un pas par cellule mis en commun donne 52 µm à une feuille contre 47 pour le pas global. Meilleur à longue portée (1,71 contre 1,90 feuille à huit), inutile là où ça compte |
| **A5 bis** | ⚠ ~~juger la chaîne par l'identité~~ — **déjà fait** (`44`) : elle **glisse**, elle ne saute pas. Ce qui reste est de refaire la mesure contre une surface **recalée**, son budget étant gonflé (**69,2 → 64,7 µm**, conjecture) | corrigé par la lecture des fiches ; mesuré sur 2 rouleaux, **pas** sur `PHercParis4` où `44` a mesuré |
| **A6** | la ROC de α n'est pas faite | demande de **rendre** 101 surfaces à deux profondeurs — le seul poste de ce registre qui exige le volume |
| **B2** | « no threshold » pas encore rétréci dans l'abstract | ⚠⚠ **testé et NON tranchable ainsi** (`77` §11) : translater = décentrer la fenêtre dans la même pile, l'idée est bonne mais une dalle de volume de surface fait ±0,9 écart et ne permet pas d'emboîter deux fenêtres. **25 refusés sur 36**. Retenté sur une dalle de 3,0 écarts : le positif centré sur le lobe est **circulaire**, et le transport d'une fenêtre à l'autre est **confondu par le serpentage** (0,13 écart ≈ la fenêtre étroite). Il faudrait un positif **indépendant** — carte d'encre ou annotation |
| **C** | la règle graduée | ✅✅ **C3 RÉPONDU le 2026-09-04** : H2 mesuré sur données publiques — `d′` 1,44 (4,317 µm) contre 1,43 (9,362 µm), rapport **1,01**, intervalles recouvrants. La condition que `69` posait n'est **pas** remplie, donc le courriel à l'ESRF n'est pas justifié par cette voie. C1 et C2 restent, et C1 est plus petit qu'annoncé (les couches du régime du prix sont **déjà rendues**) |
| **D1** | ✅✅ l'arc d'excision (`03`–`07`) — **FERMÉ : la conclusion de tête de `07` est CONFIRMÉE** | ce qui la démentait était une mesure sans producteur, prise sur une colonne dominée par son bruit d'échantillonnage. Sur `shortfall` (sans seuil, bruit < 5 %) : **0 paire sur 10** au-delà du bruit, signe mélangé. Ce qui est établi est une **borne**, pas une absence |
| **D2** | ⛔ le contrôle P1 bis de `71` | **bloqué** : le rapport « budget » n'est ni dans `docs/`, ni dans `src/`, ni dans `store/` — `71` et `72` le citent tous deux **sans le définir**, donc la tâche ne peut ni être faite ni être refusée |
| **D3** | ~~41~~ → ~~32~~ → **30** scripts sans appelant | ⚠ **entamé** : deux figures dont l'image est **utilisée** dans un doc ne portaient pas leur commande de régénération — c'est la règle du dépôt, et c'est réparé (vérifié : les deux se régénèrent à l'identique). Le reste est classé ci-dessous |

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

### C1 ⭐⭐ — la case vide, en natif

`68` §4. Les couches **natives** à 9,362 µm de `PHerc0500P2` (39 segments publiés), **≥ 40
tuiles de 256 px**, intervalle par tuiles, témoin par mélange.

⚠ **Pourquoi 40 et pas 10** : avec σ = 0,2243 (`64` §1), séparer une AUC de 0,599 de 0,5
demande 40 tuiles à une condition ; séparer 3,24 µm de 9,72 µm en demande **140 par
condition**. On en avait 10, 11 et 2. Ce sont des **minorants** — les tuiles voisines ne sont
pas indépendantes.

⚠⚠ **Et « 256 px » ne veut PAS dire la même chose ici que chez les auteurs**, ce que
[`68`](68_lire_le_papier_en_entier.md) §4 mesure (`la_case_vide.py`, 8 contrôles, revérifiés le
2026-09-04) : une tuile de 256 px au pas du prix couvre **2 397 µm** — près de quatre lettres —
là où les 256 px des auteurs à 2,4 µm en couvrent **614**, soit une. La tuile équivalente à une
lettre au pas du prix ferait **66 px**.

⭐ Les deux ne se contredisent pas, et les confondre serait l'erreur : les 40 tuiles de 256 px
sont l'unité de **notation** (ce qui donne l'intervalle) ; le 66 px est ce que devient la
**fenêtre du modèle** si l'on veut transporter la garantie anti-hallucination. C1 doit choisir
les deux séparément et le dire.

⭐⭐ **Et C1 est plus petit qu'annoncé** : `68` §4 établit que pour `PHerc0500P2`, segment
`20250628074500-500P2_front`, la **surface transformée** et la **pile de couches** sont déjà
publiées au régime du prix (9,362 µm / 1,2 m) — **seule la carte d'encre manque**, et le même
segment en porte deux dans l'autre régime, avec une vérité terrain infrarouge. Il n'y a donc
**aucune campagne de rendu à monter**, contrairement à ce que « les couches natives » laisse
croire : elles existent.

⚠ Et `65` est une **décimation**, qui garde un détail en profondeur qu'un vrai scan n'a pas :
c'est un **majorant**. Seul le natif répond.

### C2 ⭐ — le nul verso (H7)

Un rendu décalé par segment, sur les mêmes couches et sur trois segments `w` de `0139`. C'est
le nul **propre** — parallèle à une face, sans arête de feuille — que `46` n'est pas.

⚠ **Plus urgent depuis `46`, pas moins** : le détecteur y rend *plus* de dispersion sur la
surface sans face que sur une face. Tant qu'on ne sait pas ce qu'il rend sur une face
**vierge**, « l'encre valide le déroulage » n'est pas utilisable.

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
> ⭐⭐ **Et la condition est testable aujourd'hui.** `src/volume/ou_vit_ce_rouleau.py PHerc0500P2`
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

### D2 ⛔ — le contrôle P1 bis de `71` : **bloqué sur une source absente de l'arbre**

×15,9 requis contre ×3,8 observé. ⚠⚠ **Cherché le 2026-09-04, et le rapport « budget » n'est
nulle part** : ni dans `docs/`, ni dans `src/`, ni dans `~/LplKnowledge/store/`. Les deux nombres
n'apparaissent que dans `71` §4 et `72` §4, **qui le citent tous les deux sans le définir** —
aucun des deux ne dit ce que le budget compte, sur quoi il est mesuré, ni comment ×15,9 est
dérivé.

> ⭐ C'est la dette `D3` déplacée d'un cran encore : on savait qu'une **mesure** sans producteur
> ne se relance pas et qu'un **contrôle** sans producteur ne s'audite pas. Celle-ci ajoute qu'une
> **tâche** dont la spécification vit hors de l'arbre ne peut ni être faite ni être refusée — elle
> se contente de traîner, ce que `72` §4 constate en toutes lettres (« qui traîne »).

**Ce qu'il faudrait pour la débloquer, dans l'ordre** : retrouver le rapport source (probablement
une session de recherche non versée dans `store/`), ou bien **redériver ×15,9 depuis nos propres
grilles** — auquel cas ce n'est plus un contrôle d'antériorité mais une mesure neuve, et elle
mérite son propre énoncé plutôt que d'hériter d'un chiffre qu'on ne peut pas vérifier.

⚠ Écrire le contrôle en devinant ce que P1 bis mesure produirait un résultat qui **répond à une
question qu'on aurait inventée**, et le comparer à ×15,9 lui donnerait l'air d'une réfutation.

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

**32 orphelins** (41 au départ).

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
