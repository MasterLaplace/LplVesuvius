# Roadmap — fermer la chaîne géométrique, et la leur donner à lancer

> ⭐⭐ **Pour « par quoi continuer », lire [`55`](55_les_murs_et_leurs_causes.md)** : un tableau
> par mur, une ligne par cause candidate, son verdict et le document qui le porte. Ce document
> **-ci** dit ce que le projet vise ; le `55` dit ce qui a été éliminé et ce qui reste ouvert.

2026-08-19. ⚠⚠ **Deuxième version, après recadrage de l'auteur.** La première traitait le
Grand Prize comme un problème de **lecture** et le déclarait hors de portée parce que
l'état de l'art vient de dérouler un rouleau avec **775 heures d'annotation**. C'était à
l'envers : **les 775 heures ne sont pas une barrière à l'entrée, elles sont la cible à
supprimer.** Le prix ne demande pas de lire du grec ni d'entraîner un gros modèle — il
demande une **chaîne géométrique automatique**, et il demande qu'on puisse la **lancer**.

---

## 1. Ce que le prix demande vraiment — lu mot pour mot

Trois lignes de `/prizes`, et elles décident de tout :

> *« **100 % of the papyrus recto surface unrolled.** If the scroll possesses flakes or
> detached patches, they should also be segmented and unrolled […] It is permissible to
> skip disconnected outer patches if they constitute less than 10 % […] »*

> *« Ink detection **or renders with ink** should be produced from or on top of the
> flattened images. […] at least **70 %** of each counted column's preserved characters
> are legible. »*

> *« The unrolling pipeline should be **fully automated**; up to **8 documented hours** of
> human annotation / input are tolerated. »*

> ⭐⭐ *« For **fully automated software**, consider a **Docker image that we can easily
> run** to reproduce your work, and please include system requirements. »*

**Ce que ça dit, en clair :**

| ce que le prix demande | ce que ça n'est PAS |
|---|---|
| dérouler **100 % du recto** | traduire, transcrire, lire du grec |
| **automatiquement**, ≤ 8 h d'humain | 775 h d'atelier |
| un **rendu** sur lequel l'encre est visible | entraîner un modèle d'encre — *« or renders with ink »*, et le modèle de 2023 est public |
| **une image Docker qu'ILS lancent** | un résultat qu'on leur demande de croire |

⭐ La dernière ligne est celle qui définit le livrable. **Le prix est un prix
d'algorithmique de géométrie, et son critère d'acceptation est l'exécutabilité.** Un
concours open source ne se conçoit pas pour être gagnable seulement par qui possède des
H100 et des téraoctets ; ce qu'il récompense, c'est une **méthode que d'autres peuvent
rejouer**.

## 2. La thèse

> **Construire une chaîne assez intelligente pour cartographier correctement n'importe
> quel papyrus, si cabossé et carbonisé soit-il — par l'algorithmique, et par
> l'optimisation extrême là où la performance bloque. Puis la leur donner à lancer.**

Ce qui reste hors périmètre, et l'assumer sert la crédibilité plutôt qu'elle ne la coûte :

- ❌ traduire, transcrire, juger du grec — c'est le métier de papyrologues, et `29` §3
  garde ce cap ;
- ❌ dérouler les 53 rouleaux sur cette machine — c'est leur calcul, pas le nôtre ;
- ❌ scanner quoi que ce soit — les volumes sont publiés ;
- ❌ entraîner un modèle massif — le modèle du Grand Prize 2023 est public, et le papier
  de juin 2026 mesure qu'il **généralise en *zero-shot*** à des rouleaux non vus.

**Ce que ça laisse est exactement le goulot que l'équipe déclare** : *« No method yet
traces a complete, correct surface through a scroll automatically »*.

## 3. ⭐⭐ Le capital réel : ce que le Laplace Project a déjà résolu

C'est l'argument que la première version ratait. Ce dépôt n'attaque pas ce problème depuis
zéro : il l'attaque depuis un environnement qui a déjà **construit et prouvé** les
machineries dont il a besoin.

### 3.1 La représentation — et c'est le pont le plus fort

`00` §2 dit ce qui manque entre les deux familles de mailleurs :

> *« Ce qui manque […] est le **numéro d'enroulement** — la seule quantité qui rende le
> sheet switching **nommable** : deux points d'une même feuille le partagent, un saut de
> spire l'incrémente. »*

⭐⭐⭐ **LplPlugin a résolu exactement ce problème de représentation, pour des mondes.**
`ecs::WorldPosition` : un point n'est pas un flottant global, c'est **un index de cellule
entier plus un décalage local borné**. La raison écrite dans `procgen/Chunking.hpp` :

> *« Far from the origin a float loses the precision to distinguish adjacent cells, and a
> world that quietly degrades at its edges is worse than one with a hard boundary. »*

**Transposé au rouleau** : un point n'est pas (x, y, z) flottant, c'est
**(numéro d'enroulement entier, position d'arc, hauteur)** en virgule fixe. Conséquences
immédiates, et ce sont exactement celles que le domaine cherche :

| propriété | conséquence |
|---|---|
| l'index d'enroulement est un **entier** | un saut de spire est une **discontinuité entière** — exactement détectable, **sans seuil** |
| la précision est **constante partout** | elle ne se dégrade pas vers le cœur, là où les spires se serrent |
| la normalisation vit en **un seul endroit** | `normaliseWorldPosition` existe parce que *« deux implémentations finiraient par ne pas s'accorder sur le côté d'une frontière, et un corps sauterait d'une largeur de chunk »* — c'est mot pour mot le saut de spire |

⚠ Et ce n'est pas une analogie : c'est **le même bug**, résolu **une fois**, dans un dépôt
voisin, avec sa justification écrite.

### 3.2 L'échelle — un volume de 20 To n'est pas un problème neuf

Le papier de juin 2026 donne **20 To par volume reconstruit**, jusqu'à **100 To bruts**.
LplPlugin a traité la même forme de problème et l'a mesurée :

| machinerie | ce qu'elle a prouvé | où |
|---|---|---|
| `math::ReliefMosaic` + `ReliefStreamer` | relief tuilé à résidence **bornée**, 64 tuiles max, **aucune allocation**, lisible en ring 0 | Terre entière = 1,78 To à 30 m ; le niveau grossier tient en **27 Mo** |
| `harvest::CatalogueStream` | bake en flux : **11,9 Go projetés → 7 Mo de RSS**, plat de 4 à 256 tuiles | 19,6 M de lignes en 79 s |
| `harvest::MappedFile` | interroger **3,71 Go** en **220 Ko** de RSS anonyme, et survivre à un cgroup de 512 Mo qui tue une allocation de 1 Gio | mesuré sous contrainte |
| partitionnement + `cataloguePartPath` | découper quand ça dépasse, **refuser un ensemble troué** plutôt que répondre sur un sous-ensemble | plafond 4 Gio |

⭐ **La conclusion qui compte** : « le volume est trop gros » n'est pas un obstacle dans ce
projet, c'est un problème déjà résolu deux fois, avec les mesures pour le prouver.

### 3.3 Le déterminisme — et ce que la mesure de ce soir en fait

`30` a mesuré que `vc_grow_seg_from_seed` **n'est pas reproductible** : quatorze tirages à
paramètres identiques, treize propres, un à 79 croisements, et un maillage archivé à 240
qu'aucun tirage ne reproduit. Les aires vont de **5,69 à 10,34 cm²**.

⚠⚠ **Une chaîne dont un maillon rend un résultat différent à chaque exécution ne peut pas
être « fully automated » au sens du prix** : « automatique » veut dire qu'on peut la
lancer et obtenir le résultat annoncé, pas qu'on peut la lancer.

Or **le déterminisme est la culture centrale de LplKernel** : vingt et une portes de
parité (P6 à P21) exigent qu'un calcul soit **bit-identique** entre un oracle Linux et un
noyau i686. La machinerie qui rend ça possible est disponible :

- **arithmétique en virgule fixe** (`Fixed32`, Q16.16) et **CORDIC** — aucun flottant dans
  l'état autoritatif, donc aucune dérive d'ordre d'opérations ;
- **la règle** : *le flottant n'existe que dans les chemins non autoritatifs* ;
- **les portes de parité** comme forme de preuve — un nombre, deux cibles, bit à bit.

> ⭐⭐ **Un traceur dont la sortie est reproductible au bit près serait, en soi, une
> contribution que personne n'a.** Et c'est une contribution d'algorithmique, pas de
> matériel.

### 3.4 Les autres pièces déjà écrites et éprouvées

| pièce | ce qu'elle fait ailleurs | ce qu'elle ferait ici |
|---|---|---|
| grille de hachage spatial, octree persistant | broad-phase de collision, **0 allocation par pas** mesurée | adjacence de feuilles, voisinage de spire |
| `procgen` + **portes de jouabilité** | générer une structure **puis vérifier qu'elle est traversable** (Dijkstra, `evaluateCaveSystem`, `goalReachable`) | tracer une surface **puis vérifier qu'elle est une nappe unique** — *même forme de garantie* |
| `src/outils/temoins.sh`, 143 batteries, 3802 contrôles | une vérification doit pouvoir échouer, et on le **sonde** | ce qui rend nos résultats opposables |
| `test-tick-allocations` | prouver **zéro allocation** dans une boucle chaude | l'optimisation extrême, quand elle sera nécessaire |

## 4. Le livrable — et pourquoi il rend le test trivial pour eux

Le prix le dit : *« a Docker image that we can easily run »*. Donc le livrable n'est pas
un résultat, c'est **une chaîne exécutable qui s'insère dans la leur**.

Ce que ça implique, concrètement :

1. **Consommer leurs formats, produire leurs formats.** `tifxyz` en entrée et en sortie,
   volumes OME-Zarr lus **en streaming depuis leur bucket** — `24` a déjà prouvé que le
   volume de 893 Go n'a jamais besoin d'être téléchargé.
2. **Utiliser leurs outils là où ils existent.** `vc_tifxyz_selfcross` est officiel depuis
   le 4 août ; nos instruments s'ajoutent, ils ne le remplacent pas.
3. **Rendre le verdict lisible dans leur interface.** Écrire les sites de défaut en
   *point collection* JSON rechargeable dans VC3D, et **un code de sortie distinct** pour
   « défaut trouvé » (3) et « erreur » (1) — les deux conventions que `28` §7 a relevées
   comme étant celles du dépôt.
4. **Une image Docker, et les besoins système écrits.**

⭐ **C'est ça, « ils n'auront pas le choix de tester »** : si lancer coûte une commande et
que la sortie se recharge dans l'outil qu'ils utilisent déjà, l'essai coûte moins cher que
la discussion.

## 5. La chaîne, étage par étage — et ce qui manque à chacun

| étage | état | ce qui manque |
|---|---|---|
| **choisir où commencer** | ✅ `trouver_graine.py`, critère de planéité, répliqué sur 13 rouleaux (p = 0,0225) | rien de bloquant |
| **tracer** | ⚠ l'outil officiel marche mais **n'est pas reproductible** (`30`) | soit le rendre déterministe, soit **tirer N fois et sélectionner** |
| **juger sans vérité terrain** | ✅ deux axes : auto-intersection (`03`) et profondeur (`12`) | ⭐ **leur désaccord** — §6 |
| **corriger** | ✅ **pas fixe + recalage sur la matière**, mesurés indépendants et composables ([`44`](44_ou_la_chaine_se_trouve.md)) | le **gauchissement difféomorphe** reste pour la correction de forme — §7 |
| **couvrir 100 %** | ⚠ **la chaîne tient 5,76 mm**, et elle **GLISSE** hors de la feuille connue (−69 µm, 73 % du même côté) sans y **sauter** ([`44`](44_ou_la_chaine_se_trouve.md)) | ⭐ **corriger la dérive** — sa pente est mesurée et elle décélère ; puis l'**encre**, pour savoir si le texte suit |
| **aplatir** | ✅ `vc_flatten` / SLIM | rien |
| **rendre** | ✅ `vc_render_tifxyz` | ⚠ la fenêtre de profondeur doit être **centrée sur le pic mesuré**, pas sur la couche tracée (`12`) |
| **lire** | ❌ **hors périmètre, et c'est délibéré** | eux |

## 6. ⭐ L'instrument : le désaccord entre deux axes

L'auteur du meilleur détecteur géométrique communautaire écrit, dans son propre code :

> *« Gross excursions are caught; a minimal one-wrap switch on a tight winding is not, and
> **no geometry-only test can separate it from bending**. »*

Nous ne sommes pas géométrie seule : nous lisons le volume. Un endroit où la **géométrie
dit propre** et où le **volume dit que le pic de matière est à une distance
inter-feuilles** est exactement la panne que Henderson nomme — *« the surface wanders
between two true windings »* — et qu'aucun test géométrique n'attrape.

**Sans seuil à régler** : l'unité n'est pas le micromètre, c'est **l'écart inter-feuilles
du rouleau**, que `16` et `17` mesurent déjà rouleau par rouleau. Un pli donne une dérive
**lisse** ; un saut donne une **marche d'une unité**.

⭐⭐ Et avec la représentation du §3.1, ce test devient **exact** : la marche est un
**incrément entier** de l'index d'enroulement, pas une quantité à seuiller.

## 7. La correction : un gauchissement qui ne peut pas créer le défaut qu'il enlève

`20` a mesuré que l'erreur est structurée et que **translater ne la répare pas**. Le
remède est un gauchissement — et le danger évident est de **fabriquer** les
auto-intersections qu'on prétend enlever.

La parade est dans un papier qu'on vient de lire : Henderson paramètre sa déformation
comme l'**intégrale d'un champ de vitesse lisse**, ce qui la rend **difféomorphe par
construction** — *« the space of flow fields is the Lie algebra that generates the Lie
group of diffeomorphisms »*. Un difféomorphisme ne peut ni déchirer, ni recoller, ni
replier, donc **il ne peut pas créer d'auto-intersection**.

⭐ **La combinaison est neuve** : il pilote cette machinerie par un **a priori global** (la
spirale) ; nous la piloterions par une **mesure locale directe du volume**. Même garantie,
information différente — et la nôtre n'exige aucune vérité terrain.

⚠ Trois choses à vérifier avant d'y croire : l'intégration discrète ne préserve pas la
garantie gratuitement (Henderson le dit) ; le champ de profondeur est bruité et le
régulariser peut effacer le signal ; et **rien ne prouve encore que corriger serve à
quelque chose** — §9.

## 8. Couvrir 100 % — et pourquoi c'est un problème d'ingénierie, pas de matériel

C'est l'étage vide, et c'est celui qui vaut le prix.

La stratégie que l'état de l'art utilise est le **transfert de spire à spire** : une fois
une spire bien tracée, on la décale le long de sa normale jusqu'à rencontrer la
prédiction suivante. C'est ce que le papier de juin 2026 appelle le *« wrap by wrap copy
tool »*, et c'est là que ses **~25 h par spire** sont dépensées — en **correction
manuelle** de ce que le transfert rate.

**Donc la question du prix se réduit à une seule** :

> **Qu'est-ce qui remplace l'humain qui corrige le transfert de spire à spire ?**

Et la réponse que ce dépôt peut donner est composée de pièces qui existent :

1. **détecter** que le transfert a fauté → §6, sans vérité terrain, en 0,05 s ;
2. **corriger** → §7, sans pouvoir empirer la topologie ;
3. **ne pas propager** → une spire n'est acceptée que si elle passe les deux axes, sinon
   on retire et on retire — l'échantillonnage de `30` ;
4. **tenir 31 spires × 1231 cm² en mémoire bornée** → §3.2, déjà résolu deux fois ;
5. **rester reproductible** → §3.3.

⚠ **Ce qui n'est pas résolu et qu'il ne faut pas se cacher** : les régions comprimées, où
`villa#191` mesure que **78 %** des points de vérité montrent un **pic unique large
couvrant deux feuilles**. Là, l'information **n'est pas dans le CT**. Aucune algorithmique
ne la fabrique. Le prix tolère *« less than 10 % »* de patches déconnectés sautés — c'est
la marge dans laquelle ce problème doit tenir, et **le mesurer par rouleau est une des
premières choses à faire**, parce que ça dit sur quel rouleau le prix est jouable.

## 9. ⭐⭐ La question qui commande tout, et qui n'est toujours pas tranchée

> *« Une surface propre donne un meilleur texte » est une affirmation **sur le pipeline**,
> et **elle n'est pas prouvée. »* — `03`:137

Elle change de sens dans ce cadrage, et devient **plus** importante, pas moins : si la
qualité géométrique ne décide de rien en aval, alors tout l'appareil d'instruments est un
raffinement sans conséquence, et le prix se gagnerait avec une chaîne médiocre mais
complète.

Le dessin est apparié et à notre portée : un segment **publié** de Scroll 1, deux versions
(originale et gauchie), le **même** modèle d'encre, la **même** carte publiée — avec un
gauchissement **nul** et un **aléatoire de même amplitude** comme contrôles.

⚠ Et EduceLab (`32`) montre qu'il faut aller plus loin que ce que le domaine fait :
mesurer aussi sur un **substrat connu sans encre**, parce qu'un détecteur qui ne se tait
jamais ne détecte rien.

## 10. Le calendrier

| quand | quoi | pourquoi |
|---|---|---|
| **avant le 31 août** | Progress Prize | ⚠ `15` se déclare **périmé sur deux points** ; à refaire avant l'envoi, pas après |
| **septembre** | §9 — *corriger sert-il à quelque chose ?* | c'est le socle, et publiable dans les deux sens |
| septembre | l'échantillonnage de `30` : N tirages, sélection sur un axe, **validation sur l'autre** | bon marché, le levier est mesuré |
| septembre | ⭐ **mesurer la part comprimée rouleau par rouleau**, à **50 fenêtres** minimum | ça dit **sur lequel des treize** le prix est jouable — ⚠⚠ et [`33`](33_la_carte_nest_pas_resolue.md) mesure que la campagne de `16`, à 15–35 fenêtres, **ne sépare aucune paire** : l'effectif est le paramètre qui décide, pas l'instrument |
| octobre | §6 — l'instrument de désaccord | c'est la contribution que le concours nomme |
| oct.–nov. | §3.1 — la représentation en **index d'enroulement + décalage** | c'est elle qui rend §6 exact au lieu d'approché |
| nov.–janv. | §8 — l'enchaînement automatique de spire à spire | l'étage vide, celui qui vaut le prix |
| févr.–avril | 100 % d'**un** rouleau, en Docker, avec les besoins système | le livrable |
| **en continu** | un Progress Prize par mois | 20 000 $/mois, et c'est ce qui garde l'attention du jury |

⭐ **L'ordre n'est pas négociable sur deux points** : §9 avant §7 (ne pas construire un
correcteur avant de savoir si corriger sert), et **la mesure de compressibilité avant de
choisir le rouleau** (ne pas dépenser six mois sur un rouleau où l'information n'est pas
dans le scan).

## 11. ⚠ Les quatre façons dont cette roadmap peut se tromper

1. **Si §9 rend « corriger ne change rien »** : les instruments restent vrais, mais ils
   cessent d'être une voie vers le prix. La chaîne bascule alors sur la **couverture** —
   tracer 100 %, même moyennement, plutôt que tracer bien.
2. **Si les treize rouleaux sont tous trop comprimés** : le prix devient inatteignable sur
   ce corpus, quelle que soit l'algorithmique. ⭐ **C'est mesurable en septembre**, et
   c'est la mesure qui doit venir tôt. ⚠⚠ **Et on ne sait pas encore la faire assez
   finement** : [`33`](33_la_carte_nest_pas_resolue.md) montre qu'aux effectifs de `16`
   aucun des treize n'a d'intervalle qui exclut d'être sous 10 %, ni au-dessus. La
   question n'a aujourd'hui de réponse pour **aucun** rouleau. Et la campagne dense du
   2026-08-20 a **inversé le classement** (rho −0,297, treize rangs changés) : le rouleau
   par lequel commencer n'est pas celui que `16` désignait.
3. **Si le traceur ne peut pas être rendu déterministe** et que l'échantillonnage ne suffit
   pas : « fully automated » devient un mot qu'on ne peut pas tenir. Le repli honnête est
   de publier le **détecteur** seul, qui n'a pas ce problème.
4. ⚠⚠ **Si le temps de calcul explose** : 31 spires × 1231 cm², plus N tirages par spire,
   plus un gauchissement. C'est là que l'optimisation extrême devient le sujet — et c'est
   la compétence de LplKernel, pas un souhait.
