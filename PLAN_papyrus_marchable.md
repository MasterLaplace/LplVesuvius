# PLAN — Le papyrus marchable

Rendre un vrai rouleau d'Herculanum dans LplPlugin, à l'échelle du micron, et s'y promener.
Document autosuffisant. ⚠ Tous les chiffres ci-dessous sont **mesurés le 2026-08-28**, sur
le bucket ouvert et sur ce poste, par les scripts nommés en fin de document. Aucun n'est estimé.

---

## 0. Les faits qui commandent le reste

### 0.1 La donnée telle qu'elle est publiée

`PHerc0172/volumes/20241024131838-7.910um-53keV-masked.zarr`, OME-Zarr v2, chunks **128³**,
`dtype u1`, blosc/zstd clevel 3, séparateur `/`, **6 niveaux**, chacun divisé par deux.

| niveau | shape | pas | poids |
|---|---|---:|---:|
| 0 | 21000 × 6700 × 9100 | 7,9 µm | 1,2 To |
| 1 | 10500 × 3350 × 4550 | 15,8 µm | 149 Go |
| 2 | 5250 × 1675 × 2275 | 31,6 µm | 18,6 Go |
| 3 | 2625 × 838 × 1138 | 63,3 µm | 2,3 Go |
| 4 | 1312 × 419 × 569 | 126,6 µm | 298 Mo |
| 5 | 656 × 209 × 284 | 253,1 µm | **37 Mo** |

Un chunk = **2 Mio** décompressés, **~1,5 Mo** sur le fil (×1,4 mesuré sur 54 chunks denses).

⚠ **La pyramide EST l'échelle de LOD, et elle est publiée.** On ne calcule aucun mip : ils
existent côté serveur. C'est le cas idéal, et il ne se représentera pas souvent.

### 0.2 ⭐ Ce que la pyramide préserve, et ce qu'elle détruit

Mesuré en **apparié** — le même cube physique de 1,01 mm lu aux six niveaux, chaque niveau
grossier recadré exactement dessus (`seuil_par_niveau.py`).

| niveau | pas | côté | moyenne | **écart-type** | > 128 | > 160 |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 7,9 µm | 128 | 146,9 | **23,5** | 77,6 % | 27,6 % |
| 1 | 15,8 | 64 | 146,9 | 22,1 | 80,5 % | 27,6 % |
| 2 | 31,6 | 32 | 146,9 | 19,3 | 88,1 % | 27,1 % |
| 3 | 63,3 | 16 | 146,9 | 15,3 | 97,5 % | 23,9 % |
| 4 | 126,6 | 8 | 146,9 | **11,4** | 100 % | 13,1 % |
| 5 | 253,1 | 4 | 146,9 | **9,0** | 100 % | 1,6 % |

**La moyenne est préservée exactement** (146,9 partout) : le sous-échantillonnage publié est un
vrai filtre de boîte. **L'écart-type s'effondre de 23,5 à 9,0.**

⚠⚠ **Conséquence directe et non négociable : un seuil d'isosurface unique ne survit pas à la
pyramide.** Un seuil proche de la moyenne dérive de **+22 points** au niveau 4 ; un seuil loin
au-dessus s'effondre de **−26 points** au niveau 5. Ce n'est pas un défaut de la donnée, c'est
ce que fait une moyenne. Le remède est **mesuré, pas deviné** — une table de seuils par niveau
qui reproduit la même fraction de matière :

| niveau | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| **seuil** | 128 | 130 | 132 | 134 | 135 | 136 |

⚠ Cette table est **propre à ce volume**. Un autre rouleau a un autre histogramme, donc c'est un
**artefact calculé et rangé à côté du cache**, jamais une constante dans le code.

⚠ **Correction d'une affirmation que j'ai faite en cours de route** : j'avais écrit qu'au-delà
du niveau 2 « les feuilles fusionnent en un bloc plein » parce que le voxel devient plus épais
que la feuille. Le mécanisme réel, mesuré, est **l'effondrement du contraste**, pas
l'épaisseur — et avec le seuil corrigé la fraction de matière est restaurée. ⚠ Reste une
question **non mesurée** : les feuilles restent-elles topologiquement *séparées* à chaque
niveau ? Ça se tranche par un comptage de composantes connexes, pas par du raisonnement.
**Sonde à faire avant d'écrire le mailleur.**

### 0.3 La géométrie physique du sujet

Depuis `LplVesuvius/docs/` (01, 02, 04, 32) : une feuille fait **~40 µm** d'épaisseur, la spire
voisine est à **~300 µm**, l'encre est un dépôt de **5–10 µm**.

### 0.4 ⭐ L'échelle « Minimoys »

On cale le couloir d'air (260 µm) sur **3 m**. Facteur **×11 538**.

| | |
|---|---|
| 1 voxel | **9,1 cm** |
| épaisseur d'une feuille | 0,46 m |
| couloir entre deux feuilles | 3,00 m |
| pas de la spirale | 3,46 m |
| dépôt d'encre sur le mur | **9 cm de relief** — un voxel exactement |
| hauteur d'une lettre | **29 m** |
| le marcheur | 19 voxels de haut |
| le rouleau | **1,92 × 0,61 × 0,83 km** |
| un chunk 128³ | 11,7 m de côté |

Le résultat visé : **un canyon en fente de 1,9 km de haut et 3 m de large, qui spirale, avec des
lettres de 29 m en relief d'un voxel sur la paroi.**

⚠ « 1 voxel = 1 m », l'idée spontanée, donne un marcheur de 14 µm et un entre-feuille de 14 m :
on ne verrait plus que du mur. L'échelle est un **choix de mise en scène**, et il se prend ici.

### 0.5 Ce que le réseau tient, et pourquoi RDMA est hors sujet

Mesuré : **4,98 Mo/s = 40 Mb/s = 2,4 chunks/s** (54 chunks, 80,5 Mo en 16,1 s).

⚠⚠ **Il n'existe aucun chemin RDMA vers S3.** RDMA est du point-à-point sur réseau local ;
l'équivalent AWS (EFA) ne marche qu'entre instances EC2 d'un même placement group. Et ce poste
n'a de toute façon ni `/dev/infiniband`, ni `libibverbs`, ni `nvidia-smi` (WSL2). Optimiser le
chemin mémoire quand le tuyau est **2500× plus lent** que ce que RDMA adresse, c'est repolir la
poignée d'une porte fermée.

⚠ **Le cache disque n'est pas un compromis, il est plus rapide que le tout-RAM.** Le page cache
EST de la RAM, lue à zéro copie, et **réclamable** — mesuré ailleurs dans ce dépôt : un balayage
de 3,71 Go mappé tourne sous `MemoryMax=512M` avec `RssAnon` = 220 Ko, là où 1 Gio d'anonyme se
fait tuer. Sans cache, on repaie 14 minutes de réseau à chaque lancement.

⚠ **Ne pas mettre le cache dans `/tmp`** : c'est un tmpfs de 20 Go, donc de la RAM. Piège déjà
payé dans ce dépôt en mesurant `MappedFile`. Le cache va sur `/` — **718 Go libres**.

| cache permanent | poids | téléchargement unique |
|---|---:|---:|
| niveaux 3..5 | 2,7 Go | 10 min |
| **niveaux 2..5** | **21,3 Go** | **1 h 18** |
| niveaux 1..5 | 170 Go | 10 h |
| niveaux 0..5 | 1,3 To | ne tient pas |

⭐ **Décision : cacher les niveaux 2 à 5 une fois pour toutes.** Le problème du démarrage à froid
disparaît ; il ne reste à streamer que les niveaux 0 et 1, c'est-à-dire ce qui est sous le nez.

### 0.6 Le plafond de rendu

| voie | plafond ~ | chunks pleine résolution |
|---|---:|---:|
| immédiat `glVertex3f` | 1,5 M tri/frame | **7** |
| display list | 8 M | 36 |
| **VBO `glDrawElements`** | 25 M | **113** |

Pire cas mesuré : **221k triangles par chunk** au niveau 0.

État de l'arbre : `apps/mapview` est du **GLX fixed-function**, 78 sites `glBegin`/`glVertex3f`,
display lists reconstruites en bloc. `render/src/VulkanRenderer.cpp` fait **154 lignes** emballant
un « legacy VkWrapper » GLFW, gaté derrière `--renderer` — donc en pratique, pas de Vulkan.

⚠ Et **la géométrie sauve le budget** : le couloir fait 3 m de large, donc les feuilles
s'occultent. Un anneau R=2 au niveau 0 (125 chunks, 27,6 M triangles, portée 23 m) dépasse déjà
ce que l'œil atteint dans une fente.

---

## 1. La décision de rendu : maillage près, raymarching loin

Ce n'est pas un choix exclusif, c'est un **partage par distance**, et chaque moitié est choisie
pour une raison qui ne vaut que d'un côté :

| | près (niveaux 0–1) | loin (niveaux 2–5) |
|---|---|---|
| technique | isosurface → VBO | raymarching d'une texture 3D |
| pourquoi | il faut de la **vraie géométrie** : le corps s'y tient, l'encre y accroche la lumière | σ s'est effondré (mesuré 9,0 contre 23,5), donc c'est **lisse** ; et ça coûte des **pixels**, pas des triangles |
| collision | oui | non, jamais |
| contexte GL | compatibilité, sans shader | **GL 3.3 core + fragment shader** |

⚠ Le raymarching **impose de quitter le fixed-function**. C'est une vraie marche, pas un
réglage : elle se prend en phase 7, pas en phase 1.

---

## 2. Les phases

Chacune produit **quelque chose qui tourne**. Aucune ne se justifie par la suivante.

### P0 — La sonde (½ jour)
Un chunk de niveau 2, téléchargé, décodé, histogramme, une **coupe dumpée en PPM**. Zéro 3D.
Plus la sonde de composantes connexes de §0.2 : les feuilles restent-elles séparées par niveau ?
**Sortie** : on sait à quoi ressemble la matière avant d'écrire une ligne de rendu.

### P1 — Le mailleur, dans un module, avec sa cible de test
⚠⚠ **Il ne va PAS dans `apps/`.** `apps/` n'a aucune cible de test — c'est la raison documentée
pour laquelle la boucle des créatures de mapview a dérivé dans les deux sens sans que rien ne le
voie, et pourquoi neuf blocs de savoir en ont été extraits. Le mailleur va dans un module
(`voxel/`, ou dans `procgen/` à côté de `Extrusion.hpp`), l'app GL n'est que le **puits**.

- isosurface sur seuil → faces, par le patron de `procgen::forEachVoxelFace` (une énumération,
  plusieurs puits — il en a déjà deux : buffer GL et `fillPolygonClipped` logiciel) ;
- ⚠ **prédicat de bord** (`solidOutside`) : deux chunks voisins ne doivent pas se murer l'un
  contre l'autre. `test-map-mesh` asserte déjà exactement ça pour les cavernes ; le contrôle
  s'étend directement ;
- **occlusion ambiante par sommet** depuis le voisinage de voxels. Dans une fente de 3 m, l'AO
  *est* l'éclairage — sans elle un canyon de parois uniformément éclairées est illisible. Quasi
  gratuite au moment du maillage ;
- maillage glouton sur les faces coplanaires. ⚠ Ne pas en attendre grand-chose latéralement (le
  papyrus est bruité au voxel près) ; le vrai gain est de **n'émettre aucune face intérieure**.

**Cible neuve `test-voxel-mesh`** : un bloc 2×2×2 a 24 faces et non 48 ; une feuille plane donne
deux nappes ; deux chunks voisins ne se murent pas ; l'AO est plus sombre dans un coin concave.

### P2 — Le lecteur zarr C++ et le cache
- GET par plage HTTP (⚠ **libcurl en bibliothèque, pas le binaire** : une moisson fait des
  milliers de requêtes, et la connexion réutilisée est à la fois plus rapide et la façon polie
  de parcourir un serveur — mesuré ×7,9 sur le lot OAI-PMH de LplKnowledge) ;
- décodage blosc/zstd **directement dans l'arène résidente**, zéro fichier temporaire sur le
  chemin chaud (le patron de `CatalogueStream` : 11,9 Go projetés → 7 Mo de RSS réels) ;
- ⚠ **séparateur de dimension lu dans le `.zarray`**, jamais codé en dur. Le corpus mélange `/`
  et `.`, et le coder en dur ne produit pas une erreur — ça produit une requête vers une clé
  inexistante, comptée en « chunk vide », donc un rouleau entier rapporté sans matière ;
- **cache : enregistrements décompressés de 2 Mio fixes + un index, `mmap`'és.** On paie 1,4× de
  disque pour supprimer le blosc du chemin chaud. Réutiliser `harvest::MappedFile` ;
- **la table de seuils par niveau (§0.2) est bakée avec le cache**, calculée sur le volume.

**Cible `test-zarr-cache`** : un chunk relu depuis le cache est **octet pour octet** celui
décodé du réseau ; un séparateur inattendu est **refusé en le nommant**, jamais compté vide.

### P3 — Le client GL : le premier screenshot
- **VBO par chunk** (`glGenBuffers`, `glVertexPointer`/`glNormalPointer`/`glColorPointer` avec
  buffer lié, `glDrawElements`), orphan-and-refill au stream-in. ⚠ Ça marche dans un contexte de
  **compatibilité**, sans shader — pas besoin de Vulkan ni d'un profil core pour cette phase ;
- caméra première personne, une seule tuile résidente, GLX comme mapview.

**Sortie** : une paroi de papyrus reconnaissable à l'écran.

### P4 — Le streaming
- **`planVoxelResidency`** : la forme 3D de `planReliefResidency`. ⚠ **Du plus proche au plus
  lointain, anneau par anneau**, pour qu'un budget qui tronque perde la tuile la plus éloignée
  et jamais le sol sous les pieds (règle déjà établie et sondée côté relief) ;
- **mosaïque bornée non-possédante**, sur le patron de `math::ReliefMosaic`. ⚠ Et sa règle : un
  slot possède **sa projection ET son champ**, sinon un champ pendouillant lit de la mémoire
  démappée. ⚠⚠ Contre l'usage-après-libération, asserter une **identité structurelle** (les
  comptes), jamais une valeur relue — la mémoire libérée ment de façon convaincante, et c'est
  exactement comme ça qu'une sonde du lot relief est passée par chance ;
- ⭐ **prefetch le long du COULOIR, pas dans une boule.** On avance sur une spirale : les chunks
  suivants sont devant le long de l'arc. Un préchargement sphérique dépense le budget dans la
  roche. C'est un prefetch **de domaine** qu'un streamer générique ne peut pas faire, et c'est
  la différence entre marcher à 4 m/s et caler ;
- **file de priorité par erreur écran**, pas par distance : un chunk vu par la tranche ne
  contribue rien ;
- **décodage en fond sur le `ThreadPool`** du module `concurrency`.

**Cible `test-voxel-residency`** : marcher 200 pas, 0 frame sans sol, résidence bornée, et le
compte de chargements ne repart pas de zéro quand on reste immobile.

### P5 — La traversée : le Minimoy marche
- ⚠ `ITerrainQuery::standable(x, z)` **n'a pas de Y** et ne peut pas servir : un rouleau a
  plusieurs étages à la même (x, z). Réutiliser **`procgen::VerticalSpan`**, écrit pour les
  cavernes avec exactement la bonne raison — « le sol et le plafond sont UNE question », deux
  appels séparés pouvant rendre les moitiés de deux vides différents ;
- collision contre **le champ de voxels**, pas contre le maillage : le maillage est du LOD, il
  change avec la distance, et un corps ne doit pas traverser un mur parce qu'on s'en éloigne ;
- ⚠ **`ecs::WorldPosition` (cellule + offset) est obligatoire** : Q16.16 sature à 32767 et le
  rouleau fait 21000 voxels de haut au niveau 0. Même décision que pour la géographie.

### P6 — ⭐ L'encre : ce qui fait que c'est CE projet
Peindre la prédiction d'encre de LplVesuvius **sur la surface**, comme une seconde couche.
Marcher dans le couloir et voir les lettres émerger.

⚠⚠ **Et la garde qui n'est pas négociable.** `LplVesuvius/docs/46_le_temoin_negatif.md` établit
que le modèle **hallucine une structure différente et convaincante sur chaque entrée**, y compris
là où aucune feuille n'est à portée — et que ça **ne se repère par aucune inspection de la
sortie**. Donc :
- la confiance est **rendue visible** (opacité, ou hachure), jamais aplatie en un trait net ;
- un **mode CT pur, sans aucune prédiction, existe et est le défaut** ;
- l'écran affiche **de quelle carte** vient ce qu'il peint, et son AUC quand elle est connue.
Un viewer qui peindrait la prédiction comme un fait serait un instrument qui ment.

### P7 — Le lointain en raymarching
- **GL 3.3 core + fragment shader** ; texture 3D par chunk grossier ;
- **brickmap / min-max par bloc 8³** calculé au bake : l'empty-space skipping est ce qui rend un
  raymarcher tenable, et le rouleau est une spirale dans une boîte majoritairement vide ;
- composition profondeur-consciente avec le maillage du champ proche ;
- ⚠ **la frontière niveau 2 → 3 n'est pas un décalage, c'est un changement de topologie** : le
  fondu géométrique ne s'applique pas. Deux remèdes, à mesurer plutôt qu'à choisir d'avance : un
  fondu **stochastique** (dither) sur une bande, ou l'aveu que **l'occlusion du couloir cache la
  frontière** — ce qui est probablement vrai ici et coûterait zéro.

### P8 — La pose reproductible
Une commande qui prend **une pose** (position, orientation, niveau, seuil, couche d'encre) et
rend l'image. ⚠ Deux captures de la même pose doivent être **octet pour octet identiques** —
c'est déjà la propriété d'`agent::Vision`, et c'est ce qui transforme un joli screenshot en
**instrument**. Et la règle du dépôt : tout visuel porte la commande qui le régénère.

### P9 — Parité, si on la veut
⚠ **Honnêtement : ce viewer n'a aucune raison de tourner en ring 0.** L'ordre de link l'interdit
de toute façon (`libengine` ne peut pas appeler `libknowledge`), et un musée ne boote pas.
Ce qui reste utile sans inventer une gate : garder l'**arithmétique** en Fixed32 et testable —
conversion micron→monde, table de seuils, `VerticalSpan`, le pas de marche. Ça ne coûte rien et
ça garde la porte ouverte.

Si une gate est voulue un jour, sa forme est celle de **P21 relief** : folder l'arithmétique sur
des voxels **synthétiques dérivés d'une formule entière des deux côtés** (une gate ne peut pas
dépendre du réseau), et mesurer le vrai lecteur zarr **à part**, dans un test hôte.
⚠ Et ne rien folder dont la taille diffère entre hôte et ring 0 — la leçon de l'arène de P14.

---

## 3. Les extras qui valent leur coût

Par ordre de rapport qualité/effort décroissant.

| | quoi | pourquoi |
|---|---|---|
| ⭐⭐⭐ | **AO par sommet** (P1) | dans une fente, c'est *tout* l'éclairage. Quasi gratuit au maillage |
| ⭐⭐⭐ | **prefetch le long du couloir** (P4) | domaine-spécifique, imbattable par un streamer générique |
| ⭐⭐⭐ | **table de seuils par niveau** (P2) | sans elle le LOD ment sur la quantité de matière (mesuré, jusqu'à 22 pt) |
| ⭐⭐ | **brickmap min/max** (P7) | rend le raymarcher tenable, et accélère aussi le mailleur |
| ⭐⭐ | **cull de domaine « quel couloir »** (P4) | le frustum cull est faible dans une fente ; la spirale donne un cull presque parfait |
| ⭐⭐ | **pose reproductible** (P8) | transforme un screenshot en mesure |
| ⭐ | **lumière portée** (lampe) plutôt qu'un soleil | il n'y a pas de ciel dans un rouleau. Réutiliser le patron de `beginCaveFrame`, qui remplace le ciel par le noir de la caverne et **pointe la perspective aérienne existante dessus** — une lampe, pas un second modèle d'éclairage |
| ⭐ | **coupe interactive** (clipping plane) | voir la spirale en section, comme les figures du dépôt |
| ⭐ | **overlay « où suis-je »** — spire, tour, mm depuis l'axe | c'est la donnée que LplVesuvius manipule ; l'afficher relie le viewer au reste |

---

## 4. Écarté, avec la raison

- **Vulkan.** 154 lignes sur du legacy GLFW. Le rendre utilisable est un lot à soi, et GL
  compat + VBO suffit jusqu'à P6.
- **RDMA / GPUDirect.** §0.5. Pas de chemin vers S3, pas de matériel ici, et le tuyau est
  2500× en dessous du régime où ça compte.
- **Les créatures dans le rouleau.** Les six systèmes de `CreaturePipeline` supposent une
  fenêtre d'odeur 2D et un `standable(x, z)` sans Y — même blocage, mot pour mot, que celui déjà
  écrit pour les cavernes. Lot à part.
- **Mailler la nappe tracée plutôt que le volume.** Tentant (LplVesuvius produit déjà des `.obj`
  de segments, et c'est des ordres de grandeur moins cher), et ça **perd le canyon**. À garder
  comme *mode de comparaison* en P6, pas comme chemin principal.
- **Cacher le niveau 0 en entier.** 1,3 To contre 718 Go libres. On cache la région visitée.

---

## 5. Les pièges de ce dépôt qui s'appliquent ici

Tous déjà payés, tous consignés — les relire vaut mieux que les repayer.

1. **`xmake` sans `-P .`** construit le mauvais projet et répond « build ok » sans rien compiler.
   Toujours `cd` dans le projet **dans la même commande**.
2. **Le code de sortie d'un pipeline est celui de sa DERNIÈRE commande** — `prog | tail` a déjà
   fait passer un segfault pour un succès.
3. **`pkill -f` / `pgrep -f` matchent leur propre ligne de commande.** Tuer par PID.
4. **Vérifier la fraîcheur d'un log avant d'en citer le verdict.**
5. **Un `.cpp` neuf doit entrer dans les DEUX listes** de build noyau — si jamais ça y descend.
6. **Ne jamais éditer un script pendant qu'il tourne** : bash le lit par offset.
7. **Une valeur attendue se calcule à part, jamais en relisant le code testé.**
8. ⚠ **Une sonde par contrôle.** Un test vert au premier coup ne prouve rien : le casser exprès
   est la seule façon de savoir qu'il peut échouer.

---

## 6. Reproduire les chiffres

Scripts, dans le scratchpad de la session du 2026-08-28 (à déplacer dans l'arbre au moment où
la phase 0 démarre — un chiffre dont le calcul n'est pas dans l'arbre est une anecdote) :

- `dimensionner_papyrus.py` — la pyramide, la taille physique, le cache par niveaux
- `echelle_minimoys.py` — le facteur d'échelle et le budget de résidence
- `budget_triangles.py` — les triangles par chunk et le plafond GL
- `seuil_par_niveau.py` — ⭐ la comparaison appariée et la table de seuils

Et la mesure de débit, en une ligne : 54 chunks du niveau 2 en parallèle, chronométrés.

---

## 7. La première chose à faire demain

**P0.** Un chunk de niveau 2, une coupe en PPM, un comptage de composantes connexes. Deux
heures, aucune dépendance neuve, et ça tranche la seule question ouverte du §0.2 — celle dont
dépend la forme du mailleur.
