# Ce qui gouverne la trajectoire du traceur — et tout ce qui ne la gouverne pas

2026-08-19, suite de [`25`](25_une_graine_choisie_sur_la_planeite.md). La moitié restante
de T1 : *où l'on part* était réglé, *comment on avance* ne l'était pas. Deux paramètres
étaient censés le régler — `direction_fields` et les grilles de normales — et **rien ne
documente ni l'un ni l'autre**.

**Résultat en une ligne** : les deux contrats sont **dérivés du binaire**, l'encodage des
octets est **mesuré et répliqué sur trois rouleaux**, les **douze poids de perte** sont
identifiés et réglables (⚠ **douze**, pas dix — deux des noms annoncés ici n'existaient
pas, corrigé au §4 contre le code source) — et **aucun des deux mécanismes ne déplace la croissance d'un
centième**, y compris à ×100 d'intensité et avec 1,53 Go de vraies grilles qui coûtent
**29 fois** le temps de calcul. Le contrôle positif montre que la méthode sait pourtant
détecter un changement : `step_size` fait diverger dès le premier pas.

> ⭐⭐ **La trajectoire répond à la prédiction et à la géométrie du pas, à rien d'autre.**
> C'est pourquoi la **graine** reste le seul levier mesuré (`25`) — et c'est un résultat
> utile en soi : il évite à quiconque de chercher le remède là où il n'est pas.

---

## 1. Le contrat, dérivé clé par clé

Aucune documentation, aucune source locale. Mais le binaire refuse une clé manquante avec
son nom, donc il suffit de lui donner un objet vide et de lire ce qu'il réclame :

```
{}                                        -> key 'zarr' not found
{"zarr": "/nexistepas"}                   -> key 'dir' not found
{"zarr": …, "dir": "x"}                   -> WARNING: invalid direction … skipping
{"zarr": …, "dir": "normal"}              -> key 'scale' not found
{"zarr": …, "dir": "normal", "scale": 2}  -> direction field dataset shape [3686,1946,1946,]
```

> **Le contrat** : `"direction_fields": [{"zarr": <base>, "dir": <sens>, "scale": <niveau>}]`
> — l'outil ouvre alors `<base>/x/<niveau>`, `<base>/y/<niveau>`, `<base>/z/<niveau>`.
> Sens valides : **`normal`**, **`horizontal`**, **`vertical`** (`x`, `y`, `z`, `nx`, `xy`,
> `radial`, `tangent`… sont tous refusés). Deux clés facultatives existent aussi dans le
> binaire : `weight` et `weight_zarr`.

⚠ Le chemin est **local** : `std::filesystem::path`, pas d'URL. ⚠ Et `scale` sélectionne le
**niveau de pyramide**, c'est-à-dire le nom du sous-dossier, pas un facteur d'échelle.

⭐ **On ne télécharge pas le rouleau.** Un zarr rend sa valeur de remplissage pour les
chunks absents, donc seule la boîte autour de la trace est récupérée : **626 Mo** au lieu
de plusieurs gigaoctets, et le reste du volume dit simplement « pas de contrainte ».

## 2. ⭐⭐ L'encodage, mesuré — parce que le deviner ne produit aucune erreur

Chaque rouleau publie, à côté de sa prédiction, un dossier `lasagna/` contenant
`_nx.ome.zarr` et `_ny.ome.zarr` : les composantes horizontales de la normale, en
**uint8**. Rien ne dit ce que ces octets valent. Et se tromper de convention **ne lève
aucune erreur** — le traceur suit un champ faux, et le résultat ressemble à « les champs
de direction ne servent à rien ».

La vérification n'a demandé aucune donnée nouvelle : le **tenseur de structure** que
[`25`](25_une_graine_choisie_sur_la_planeite.md) calcule déjà sur la prédiction rend la
normale locale de la feuille. On balaye alors l'hypothèse de zéro :

| valeur uint8 supposée nulle | écart angulaire médian |
|---:|---:|
| 0 | 53,1° |
| 64 | 37,9° |
| 96 | 17,6° |
| **128** | **6,6°** |
| 160 | 21,5° |
| 192 | 36,7° |
| 255 | 46,2° |

**Un pic net, pas un plateau contre une borne** — c'est la forme qu'a un encodage correct.
Donc **`(v − 128) / 127`**.

⭐ **Et répliqué**, parce qu'un fait établi sur un corpus n'est pas un fait :

| rouleau | blocs comparés | meilleur centre | écart |
|---|---:|---:|---:|
| `PHerc0358` | 13 659 | **128** | **6,6°** |
| `PHerc0125` | 13 697 | **128** | **5,7°** |
| `PHerc1447` | 1 488 | **128** | **6,2°** |

⚠⚠ **Conséquence directe** : la composante `z`, qu'aucun rouleau ne publie, se remplit de
**128** et non de 0 — zéro voudrait dire **−1**, c'est-à-dire une normale verticale
partout. Et comme c'est la valeur de remplissage du zarr, elle **ne coûte pas un octet**.

### ⚠⚠ Un défaut de mon propre outil, trouvé par un 0,7071 exact

La première passe donnait 128 sur deux rouleaux et **0** sur `PHerc1447`. Le signe était
un `|cos|` de **0,7071 exactement** pour deux centres symétriques autour de 128 — la
signature d'un champ **constant**, pas d'une mesure.

Cause : `PHerc1447` n'est couvert qu'à **46 %** dans la fenêtre sondée, et je comparais la
**valeur de remplissage** comme si c'était une donnée. Un chunk absent décode en un vecteur
parfaitement défini et parfaitement faux. L'absence se lit sur les valeurs **brutes**
(`nx = ny = 0`), avant tout décodage : un vecteur (−1, −1) a une norme de 1,41 et ne peut
pas être une normale unitaire. Après correction, les trois rouleaux s'accordent.

⚠ **Le témoin mélangé, lui, ne discrimine pas** (0,891) : dans une fenêtre de 192 voxels,
les normales pointent déjà presque toutes dans la même direction. C'est le **balayage** qui
tranche, pas le mélange — et c'est pour ça qu'il est dans l'outil.

## 3. ⚠⚠ Le champ charge, s'annonce — et ne change pas la croissance

Le champ est branché, l'outil confirme :
`direction field dataset shape [3686,1946,1946,]`.

Et pourtant, en comparant les **journaux de croissance** et non les seules aires finales :

| exécution | croissance, 118 générations | surface sauvée | auto-intersections |
|---|---|---:|---:|
| sans champ, `thread_limit: 0` ×2 | **identique** | 19,834872 / 19,821850 | 0 / 0 |
| sans champ, `thread_limit: 1` ×2 | **identique** | 19,838660 / 19,823302 | 0 / 0 |
| **avec champ**, `dir: normal` | **identique** | **20,747079** | **1176** |
| **avec champ, axes x/y PERMUTÉS** | **identique** | 21,561857 | **8282** |

Toutes finissent la croissance à **1985,73 mm²**, au centième près. Même un champ dont les
axes sont délibérément **permutés** — donc faux de 90° — ne déplace pas un seul pas.

> ⭐⭐ **`direction_fields` n'intervient pas dans la croissance.** Il est lu, sa forme est
> annoncée, et la trajectoire est exactement celle d'un traceur qui n'en a pas.

⚠⚠ **Mais là où il agit — l'étape finale, la seule qui varie d'une exécution à l'autre —
il agit vraiment, et il fait empirer.** Et le classement est ordonné, ce qui est le fait
important :

| champ donné à l'étape finale | aire sauvée | auto-intersections |
|---|---:|---:|
| aucun (4 exécutions) | 19,82 cm² | **0** |
| le champ mesuré, `dir: normal` | 20,75 | 1 176 |
| le même, **axes x/y permutés** (faux de 90°) | 21,56 | 8 282 |
| le même, `dir: horizontal` | 20,33 | 10 623 |
| le même, `dir: vertical` | 20,70 | **16 983** |

⭐ **Le classement est ordonné sur un facteur 14, et c'est le fait qui compte.** Notre champ
en `normal` bat une permutation d'axes de **7×**, un contresens `horizontal` de **9×**, et
`vertical` de **14×**. Donc le champ **est bel et bien consommé**, la sémantique `normal`
est **la bonne**, et notre champ est **substantiellement juste** — assez pour dominer
largement les trois erreurs délibérées, pas assez pour faire mieux que rien.

### ⭐⭐ Et l'intensité se règle — ce qui ferme la question

Deux réglages agissent sur l'intensité : la clé **`weight`** *dans* l'entrée, et le poids
global **`direction_weight`** (§4). Les deux ont été balayés :

| réglage | croissance, 118 générations | aire sauvée | auto-intersections | par cm² |
|---|---|---:|---:|---:|
| aucun champ | **identique** | 19,82 cm² | **0** | **0** |
| défaut | **identique** | 20,75 | 1 176 | 57 |
| entrée `weight: 10` | **identique** | 26,84 | **81 464** | 3 035 |
| entrée `weight: 100` | **identique** | 26,71 | 69 580 | 2 605 |
| `direction_weight: 10` | **identique** | 27,84 | 66 243 | 2 380 |
| **`direction_weight: 100`** | **identique** | **137,98** | 34 340 | 249 |

⚠⚠ **Six exécutions, six intensités, et la croissance est identique au centième dans
toutes** — les 118 générations finissent à **1985,73 mm²** partout, y compris pour le
réglage qui multiplie l'aire **sauvée** par sept. C'est le fait qui ferme la question :
ce que le paramètre amplifie est **uniquement l'étape finale**, qui à `direction_weight:
100` fabrique **sept fois** la surface que la croissance avait produite.

⭐ ~~**Et il est bien consommé** : la densité d'auto-intersections chute d'un facteur **12**
entre `weight: 10` et `direction_weight: 100` (3 035 → 249 par cm²). Le champ organise donc
réellement quelque chose — simplement pas assez pour battre **zéro**.~~ **Retiré le
2026-08-20 — voir juste en dessous : la mesure dit l'inverse.**

⚠⚠ **Réserve ajoutée le 2026-08-20, et elle porte précisément sur la phrase ci-dessus.**
L'audit de [`34`](34_un_verdict_qui_ne_mesure_rien.md) montre que les **cinq** comptes de ce
tableau ont été mesurés avec des quads **jetés** par le filtre `--maxedge` — de 3 358 à
**82 000** selon la ligne. Un compte ne porte donc pas sur la même fraction de surface d'une
ligne à l'autre, et ce tableau les compare.

- Trois re-mesures **filtre désactivé** donnent un ratio serré — `weight: 10` ×2,73,
  `weight: 100` ×2,87, `direction_weight: 10` ×2,79 — donc **entre ces trois-là la
  comparaison tient**.
- ⚠⚠ **`direction_weight: 100` a rendu, et il RETOURNE la phrase.** C'est la ligne au compte
  publié le plus **bas** et au nombre de quads jetés le plus **haut** (82 000, trois fois les
  autres). Filtre désactivé, elle mesure **2 455 822** auto-intersections au lieu de 34 340 —
  un ratio de **71,5×**, contre 2,7 à 2,9 pour les trois autres.

**Le tableau, relu sur la totalité de chaque surface** (`docs/mesures/sans_filtre.json`,
`src/outils/remesurer_sans_filtre.sh`) :

```
bash src/outils/remesurer_sans_filtre.sh   # → docs/mesures/sans_filtre.json
```

⚠ Sans argument il reprend les **onze** essais nommés dans le script lui-même ; un sous-ensemble
s'écrit `bash src/outils/remesurer_sans_filtre.sh data/sans_filtre essai_ng2 essai_scale1`.

> ⚠⚠⚠ **2026-09-04 — cette mesure a été perdue puis restaurée**, comme celle de
> [`34`](34_un_verdict_qui_ne_mesure_rien.md) et par **le même commit de rangement**
> (`a5901be`, 2026-08-26) : `"lignes": []` écrit par-dessus les quatre lignes du tableau
> ci-dessous. Restaurée depuis `79fba93` et vérifiée — les quatre lignes du fichier sont
> exactement les quatre du tableau (81 464 / 222 272, 69 580 / 199 833, 66 243 / 184 587,
> 34 340 / 2 455 822). ⭐ `src/depot/mesures_videes.py` garde désormais contre la **régression**
> — une mesure que l'historique a vue pleine et qui est vide — et non contre le vide, parce que
> cinq mesures de ce dépôt sont vides **depuis toujours** et que leur vide **est** le résultat.

| réglage | aire | publié | par cm² | **sans filtre** | **par cm² corrigé** |
|---|---:|---:|---:|---:|---:|
| entrée `weight: 10` | 26,84 | 81 464 | 3 035 | 222 272 | **8 281** |
| entrée `weight: 100` | 26,71 | 69 580 | 2 605 | 199 833 | **7 481** |
| `direction_weight: 10` | 27,84 | 66 243 | 2 380 | 184 587 | **6 630** |
| **`direction_weight: 100`** | 137,98 | 34 340 | 249 | **2 455 822** | **17 798** |

⚠⚠ **La densité ne chute donc pas d'un facteur 12 : elle DOUBLE** (8 281 → 17 798 par cm²).
La phrase ci-dessus — *« le champ organise donc réellement quelque chose »* — est **retirée**.
Elle reposait entièrement sur un compte que le filtre avait vidé des trois quarts de sa
surface, précisément sur la configuration qui produit la géométrie la plus dégénérée.

⚠ **Aucune des deux lectures n'est « la vérité »**, et il faut le dire : filtre actif on
compare des fractions différentes ; filtre désactivé on teste des triangles bâtis à travers
une discontinuité de grille, que l'aide de l'outil décrit comme *« crossing everything it
passes through »*. Ce qui rend la seconde utilisable dans un tableau n'est pas une prétention
à l'exactitude — c'est qu'elle **traite les quatre lignes pareil**.

⚠ Ce qui n'est **pas** en cause : jeter des quads ne peut que **retirer** des croisements,
jamais en ajouter. Les comptes publiés sont donc des sous-estimations, et l'énoncé qui porte
tout le §7 — *tous ces réglages font bien pire que zéro* — en sort **renforcé**, pas
affaibli. Seule la comparaison **entre lignes** est en suspens.

> ⭐ **`direction_fields` ne peut donc pas être le remède d'une trace posée en travers de
> l'empilement** : la trajectoire est décidée pendant la croissance, et rien de ce
> paramètre n'y touche — ni sa présence, ni son orientation, ni son intensité.

⭐ **La correction du 2026-08-20 RENFORCE cette conclusion au lieu de l'affaiblir.** Ce qui
tombe est la consolation — « le champ organise quand même quelque chose » ; ce qui reste est
que monter son intensité fait passer la densité d'auto-intersections de **8 281 à 17 798 par
cm²**, contre **zéro** sans champ du tout. Le paramètre ne rate pas sa cible : **il tire dans
la mauvaise direction.**

### Ce que ça corrige de ce qu'on croyait

`24` §4 nommait `direction_fields` comme *la* cause de la trace qui coupe les spires, et
`25` reprenait ce diagnostic. **Il est faux, ou du moins hors de portée** : donner le champ
ne change pas la croissance, donc l'absence du champ ne peut pas expliquer la trajectoire.

## 4. ⭐⭐ Les DOUZE poids de perte, et pourquoi la moitié ne peut rien faire

⚠⚠ **Corrigé le 2026-08-19, contre le code source.** Cette section annonçait **dix**
poids et en nommait **deux qui n'existent pas**. Vérifié dans
`data/repos/villa/volume-cartographer/core/src/GrowPatch.cpp` :
`applyJsonWeights()`, lignes 1304–1315, lit **douze** clés, et `surface_sdt_weight`
comme `spaceline_weight` ont **zéro occurrence dans tout le dépôt villa**.

⭐ **Et cette table n'est plus transcrite : elle est DÉRIVÉE.**
`src/nappe/poids_growpatch.py` la lit dans le source à chaque exécution — clés,
défauts, gardes — et `--verifier` sort en **3** si elle cesse de s'accorder avec ce qui
est écrit ici. C'est une batterie de `src/outils/temoins.sh`. La raison est la faute
elle-même : *une table de correspondance recopiée à la main se désaccorde de sa source
dès que la source bouge, et rien ne le dit.*

> ⚠ Deux pièges payés en écrivant ce script, tous deux « le premier match n'est pas le
> bon » : `find("gen_normal_loss")` tombe sur la **déclaration avancée** (l. 1581), qui
> n'a pas de corps, donc la garde paraissait absente d'un source où elle est bien là ;
> et la garde de `DIRECTION` vit dans **`conditional_direction_loss`**, pas dans
> `gen_direction_loss` — deux fonctions au nom voisin, et c'est la seconde qui
> court-circuite. Plus un troisième, plus grave : le bloc d'échec imprimait **`ALL
> PASS (1 failures, …)`**, la chaîne exacte que `temoins.sh` cherche pour déclarer une
> batterie verte. Le contrôle serait passé au vert **en affichant ses propres échecs**.
> Corrigé, puis **sondé** : casser une clé attendue fait bien sortir en 3, sans
> `ALL PASS`.

`vc_grow_seg_from_seed` imprime au démarrage (`GrowPatch.cpp:3468`) la ligne qui décide
de tout :

```
GrowPatch loss weights:
  DIST: 1 STRAIGHT: 0.2 DIRECTION: 1 SNAP: 0.1 NORMAL: 10
  NORMAL3DLINE: 0 REFERENCE_RAY: 0 SURFACE_SDT: 0 SPACELINE: 0 SDIR: 1
```

⚠ **Le nom imprimé n'est PAS la clé JSON**, et c'est exactement ce qui a produit
l'erreur : la ligne affiche `SURFACE_SDT` et `SPACELINE`, mais les clés sont
`sdt_weight` et `space_line_weight`. La table exacte, lue dans le source :

| terme imprimé | clé du `seed.json` | défaut | ⚠ garde : le terme rend **0** si… |
|---|---|---:|---|
| `DIST` | `dist_weight` | 1 | — |
| `STRAIGHT` | `straight_weight` | 0,2 | — |
| **`DIRECTION`** | **`direction_weight`** | **1** | `direction_fields` est vide — ⚠ garde dans `conditional_direction_loss` (`:2316`), **pas** dans `gen_direction_loss` (`:2185`) |
| `SNAP` | `snap_weight` | 0,1 | ni `ngv` ni `patch_normals` |
| **`NORMAL`** | **`normal_weight`** | **10** | **ni `ngv` ni `patch_normals`** (`:2050`) |
| `NORMAL3DLINE` | `normal3dline_weight` | 0 | — |
| `REFERENCE_RAY` | `reference_ray_weight` | 0 | pas de `reference_raycast.surface` |
| `SURFACE_SDT` | ⚠ **`sdt_weight`** *(pas `surface_sdt_weight`)* | 0 | pas de `cell_reopt_mode` |
| `SPACELINE` | ⚠ **`space_line_weight`** *(pas `spaceline_weight`)* | 0 | pas de `space_line_volume` |
| `SDIR` | `sdir_weight` | 1 | — |
| — | ⚠ **`correction_weight`** *(absent de notre liste)* | 1 | — |
| — | ⚠ **`patch_normal_weight`** *(absent de notre liste)* | 0 | — |

⚠ **Et le lecteur est MUET sur une clé inconnue** :

```cpp
const auto set_weight = [&](const char* key, LossType type) {
    if (!params.contains(key) || params[key].is_null()) {
        return;                       // ← aucun avertissement
    }
```

Donc régler `surface_sdt_weight: 7` ne produit ni erreur, ni avertissement, ni effet.

⚠⚠ **La vérification annoncée dans la version précédente ne pouvait pas couvrir ces
deux clés.** Elle disait « vérifié en leur donnant des valeurs distinctes et en relisant
la ligne » — or relire `SURFACE_SDT: 0` après avoir posé `surface_sdt_weight: 7` aurait
sauté aux yeux. Les deux n'ont donc pas été testées individuellement, et la phrase
couvrait plus que ce qui avait été fait. **Une vérification qui porte sur « les dix » et
n'en exerce que huit est une vérification incapable d'échouer sur les deux autres.**

### ⭐⭐ Le fait qui explique nos trois négatifs mieux que ce qu'on avait écrit

> **`NORMAL` pèse 10 — dix fois `DIST` — et il rend `0` tant qu'aucune grille de normales
> n'est chargée.**
>
> ```cpp
> static int gen_normal_loss(...)
> {
>     if (!trace_data.ngv && !trace_data.patch_normals) return 0;
> ```

Autrement dit : **dans toutes nos traces de base, le terme dominant de la fonction de
coût ne créait aucun résidu.** Ce que le traceur optimisait réellement, c'était
`DIST` (1), `SDIR` (1), `DIRECTION` (1) et `STRAIGHT` (0,2) — pas ce que la ligne
imprimée laisse croire.

⭐ Ça affine, sans le contredire, le bilan du §8 : quand on **a** chargé une vraie grille
(T1c), `NORMAL` s'est activé, le coût par génération a été multiplié par 29 — et **la
trajectoire n'a toujours pas bougé sur 118 générations**, alors que l'étape finale, elle,
est passée de 0 à 112 139 auto-intersections. Le terme dominant s'allume et ne déplace
pas la croissance : c'est un résultat plus fort que « le champ pèse un dixième du terme
dominant », qui était l'explication proposée ici et qui **était fausse**.

⚠ **`SDIR` n'est toujours pas « surface direction »** : la bibliothèque le nomme
`conditional_sdirichlet_loss` — un terme de **Dirichlet**, une régularité de
paramétrisation, sans rapport avec les champs de direction.

### ⚠ Un piège de priorité, où le commentaire dit l'inverse du code

`GrowPatch.cpp:3446`. Le commentaire annonce
`explicit param > normal_grid > resume_surf > default` ; le code fait :

```cpp
if (params.contains("step_size"))   step = params.value("step_size", 20.0f);
else if (resume_surf)               step = 1.0f / resume_surf->scale()[0];   // ← avant ngv
else if (ngv)                       step = ngv->outputSpiralStep();
else                                step = 20.0f;
```

**`resume_surf` passe avant `ngv`.** En reprise de trace, la grille de normales ne fixe
donc pas le pas — contrairement à ce que la documentation du fichier promet.

## 5. ⚠ `scale` n'est pas seulement un nom de dossier

Trois exécutions sur des données **strictement identiques** — le même niveau 2, exposé par
liens symboliques sous les noms `1`, `3` et `4` :

| `scale` | aire sauvée | auto-intersections |
|---:|---:|---:|
| 1,0 | 19,782036 | **0** |
| **2,0** | 20,747079 | **1 176** |
| 3,0 | 19,773946 | **0** |
| 4,0 | 19,773791 | **0** |

⭐ Même contenu, quatre résultats. Donc `scale` sert **aussi** de facteur de conversion de
coordonnées : à 1, 3 et 4 les lectures tombent hors du champ et la contrainte est inerte ;
à **2** elles tombent dedans. **2,0 est donc la bonne registration** — et c'est bien là que
le champ nuit.

## 6. ⭐⭐ Le SECOND mécanisme, celui qui manquait : `normal_grid_path`

`libvc_core.so` porte un mécanisme distinct de `direction_fields`, et ses messages
décrivent exactement le format que le concours publie :

```
Not a normal-grid directory (expected xy/, xz/, yz/ subdirs and metadata.json).
```

C'est `NormalGridVolume(chemin, niveau)`, consommé par `NormalConstraintPlane::
calculate_normal_snapping_loss` — donc le terme **`NORMAL`, celui qui pèse 10**, le
dominant.

⚠⚠ **Et la clé est `normal_grid_path`, au singulier et à la racine du `seed.json`.**
Elle est bel et bien lue :

```
Loaded normal grid level 0 (coordinate_scale=1, output_spiral_step=20)
```

> ⚠⚠ **Correction d'une affirmation que j'avais publiée quelques heures plus tôt** :
> j'avais écrit que la clé « n'est pas lue ». Elle l'est. Mon sondage passait un chemin
> **inexistant**, et le chargeur l'ignore **sans un mot** — c'est un échec silencieux, pas
> une absence de clé. La leçon est celle que ce dépôt connaît : *sonder avec une entrée
> valide, sinon on mesure le silence d'un refus au lieu de la présence d'une
> fonctionnalité.*

⚠ `output_spiral_step=20` doit valoir le `step_size` du traceur — l'outil se plaint sinon
d'un « step_size parameter mismatch ». Les grilles publiées sont à **20,0**, comme le
défaut du traceur, donc ça tombe juste.

### Ce que ça pèse, mesuré

⚠ **Correction d'un second chiffre** : j'avais écrit « 182 Mo » de mémoire. Inventaire réel
des `.normal-grids` de `PHerc0358` :

| dossier | indexé par | fichiers | taille | médiane |
|---|---|---:|---:|---:|
| `xy/` | z | 14 744 | 3,83 Go | 276 ko |
| `xz/` | y | 7 783 | 3,27 Go | 433 ko |
| `yz/` | x | 7 783 | 3,30 Go | 404 ko |
| **total** | | **30 310** | **10,40 Go** | |

⭐ **Mais on n'en prend pas 10 Go** : chaque dossier étant indexé par un seul axe, une boîte
se traduit en trois intervalles de tranches. Une boîte de ±700 voxels autour de la graine
fait **1,1 Go**, récupéré en moins d'une minute avec le pool de connexions persistantes.

```
uv run python src/outils/fetch_normal_grids.py \
    PHerc0358/representations/predictions/surfaces/20250821151737-surface-20260413222639-surface-m7-L0-th0.2.normal-grids \
    data/champ_PHerc0358 --boite 5142 6542 5139 6539 6686 8086
```

⚠ La boîte est en voxels du **niveau 0** et elle est ±700 autour de la graine `5842 5839 7386`
(celle de [`25`](25_une_graine_choisie_sur_la_planeite.md)). ⚠⚠ Les trois dossiers `xy`, `xz`,
`yz` sont indexés chacun par **un seul axe**, donc une boîte devient trois intervalles de
tranches — c'est ce découpage qui fait passer de 10,40 Go à 1,1, pas une décimation.

⭐ Le pool de connexions persistantes est `src/outils/telecharger.py` : une poignée de main TLS
par objet coûterait **7 objets/s** sur les 30 310 fichiers du dossier ; une connexion gardée
ouverte est ce qui rend la minute possible.

### ⭐ Le chaînon que l'aide de `vc_ngrids` révèle

```
- Input can be a directory created by vc_gen_normalgrids (contains metadata.json and xy/xz/yz).
- Or, input can be a normals zarr root (contains x/0, y/0, z/0 datasets).
    --output-zarr PATH  Write fitted normals to a zarr directory (direction-field encoding)
    --align-normals     Align normals in an existing normals zarr
```

**Les deux formats sont les deux bouts d'une même chaîne** : `vc_ngrids --fit-normals
--output-zarr` convertit une `NormalGridVolume` en la disposition `x/0, y/0, z/0` que
`direction_fields` attend — celle-là même que j'avais fabriquée à la main depuis les
`nx`/`ny` de lasagna.

⚠⚠ **Ce qui explique pourquoi mon champ nuisait** : les `nx`/`ny` de lasagna sont un champ
**2D**, sans composante verticale, et je forçais `z` à zéro. Un vrai champ de normales de
feuille en a une. J'avais mesuré l'accord à 6°, mais **uniquement sur les composantes
x et y** — la seule chose que je pouvais comparer, et donc la seule chose que j'ai
validée.

## 7. ⭐⭐⭐ La grille de normales est consultée massivement — et ne change rien

Avec **1,53 Go** de vraies grilles (une boîte de ±700 voxels autour de la graine, soit
4 203 tranches) :

| | vitesse de croissance | trajectoire, **118 générations** | aire sauvée | auto-intersections |
|---|---:|---|---:|---:|
| sans grille | **73,45 mm²/s** | référence | 19,82 cm² | **0** |
| **avec grille** | **2,57 mm²/s** | **identique au centième** | 24,06 | **112 139** |

⚠⚠ **Un facteur 29 de ralentissement pour zéro déplacement, sur la course entière.** La
contrainte n'est donc pas ignorée — elle est évaluée à chaque pas, et elle coûte vingt-neuf
fois le temps de calcul — mais la trajectoire qu'elle produit est **exactement** celle du
traceur sans elle, du premier pas au dernier.

⚠ Et comme pour `direction_fields`, elle n'agit que dans l'**étape finale** — où elle fait
le pire résultat de tout ce qui a été testé : **112 139** auto-intersections contre zéro.

### Et l'explication est dans le nom du dossier

```
20250821151737-surface-…-th0.2.zarr           <- la prediction que le traceur suit
20250821151737-surface-…-th0.2.normal-grids   <- les grilles
```

⭐⭐ **Les grilles sont dérivées de la prédiction elle-même.** Les redonner au traceur est
une **tautologie** : il suit déjà cette prédiction, la contrainte est donc satisfaite
partout par construction, et tout ce qu'elle ajoute est son coût. C'est cohérent avec les
trois mesures : le champ charge, il coûte, et il ne déplace rien.

### Ce que ça désigne, et c'est actionnable

⭐ `vc_gen_normalgrids -i /chemin/volume.zarr -o sortie/` génère des grilles **depuis un
volume**, pas depuis une prédiction. Des grilles calculées sur le **volume masqué** —
c'est-à-dire sur la matière elle-même — porteraient une information que la prédiction n'a
pas, et c'est la seule façon de contraindre le traceur avec autre chose que ce qu'il suit
déjà. ⚠ C'est un gros calcul (l'outil balaye toutes les tranches, avec `--sparse-volume`
pour en sauter), donc un lot à soi.

⚠ **Et la conclusion pratique tient** : sur ce rouleau, la seule chose mesurée qui ait
changé la trace reste **la graine** — ni le champ de direction, ni la grille de normales,
ni les poids, ni leur intensité.

## 8. ⭐⭐ Et depuis le VOLUME, pas depuis la prédiction

Le §7 disait que les grilles publiées sont une tautologie : elles viennent de la prédiction
que le traceur suit déjà. La seule façon de le contredire est d'en fabriquer depuis le
**volume masqué** — la matière elle-même.

### Ce que ça a demandé

⚠ `vc_gen_normalgrids` **n'accepte pas d'URL** : il itère un répertoire local. Et le volume
fait **893 Go**. La sortie est le motif de la boîte :

> Un zarr rend sa valeur de remplissage pour les chunks absents. En copiant le `.zarray`
> tel quel et en ne peuplant que la boîte, on obtient un tableau **de la taille d'origine**
> — donc lisible sans la moindre translation de coordonnées — qui ne pèse que la boîte.
> ⭐ **3,44 Go** pour ±700 voxels autour de la graine, au lieu de 893.

⚠ Le volume est **non compressé** (`"compressor": null`), donc un chunk de 128³ pèse
exactement 2 Mio et la taille se calcule d'avance au lieu de se découvrir.

Puis `--num-parts` / `--part-id` shardent **par dalle de chunks** : 116 dalles en `xy`,
61 en `xz` et `yz`. On ne calcule que les **12 dalles par direction** qui recouvrent la
boîte — 36 sur 238.

### Le résultat

| couverture | vitesse | ralentissement | trajectoire |
|---|---:|---:|---|
| sans grille | 23,80 mm²/s | — | référence |
| `xy` seul (1 536 tranches) | 2,15 mm²/s | ×11 | **identique** sur 18 générations |
| **les trois directions** (4 608 tranches, 540 Mo) | **1,07 mm²/s** | **×22** | **identique sur 68 générations** |

⚠⚠ **Vingt-deux fois plus lent, et pas un centième de déplacement** — jusqu'à 667,52 mm²,
exactement la même valeur des deux côtés. Les grilles sont donc massivement consultées, et
une information qui ne vient **pas** de la prédiction ne change pas davantage la trajectoire
que celle qui en vient.

> ⚠ **La course a été interrompue à la 69ᵉ génération par mon propre nettoyage de
> processus**, pas par une erreur — c'est dit plutôt que maquillé. Celle avec les grilles
> **publiées** a été comparée sur **118 générations**, la course entière (§7), et dit la
> même chose.

## 9. ⭐⭐ Le contrôle : quelque chose déplace-t-il la croissance ?

Sans lui, « croissance identique » pourrait n'être qu'une comparaison cassée. Deux
paramètres testés sur les mêmes 20 générations :

| paramètre | trajectoire |
|---|---|
| **`step_size: 15`** (défaut 20) | **diverge dès la génération 0** — 0,42 → 0,24 mm² |
| `search_effort: 3` (défaut 10) | identique sur 18 générations |

⭐ **La méthode sait donc détecter un changement**, et l'invariance mesurée pour les champs
et les grilles est réelle.

### Le bilan de ce qui gouverne la trajectoire, mesuré

| ce qu'on fournit | la croissance bouge ? |
|---|---|
| `step_size` | ✅ **oui**, dès le premier pas |
| `search_effort` | ❌ non |
| `direction_fields` — présence, orientation, sémantique | ❌ non |
| `direction_fields` — intensité, jusqu'à ×100 | ❌ non |
| `normal_grid_path` — 1,53 Go de vraies grilles, 29× plus lent | ❌ non |

> ⭐⭐ **La trajectoire est décidée par la prédiction et par la géométrie du pas, pas par
> une contrainte qu'on puisse fournir.** C'est exactement pourquoi la **graine** a été le
> seul levier qui ait changé quelque chose (`25`) : elle décide *où* la prédiction est lue,
> et c'est la prédiction qui décide de tout le reste.

## 9bis. ⭐⭐⭐ Les deux leviers jamais essayés, essayés — les deux DÉGRADENT

La lecture de la source établissait que deux termes de perte n'avaient jamais été activés
dans ce dépôt : **`sdt_weight`**, que le traceur calcule pourtant (`get_or_compute_sdt_chunk`)
mais dont le poids vaut **zéro** par défaut, et les fibres **horizontales et verticales
ensemble** — les 17 essais ont testé `normal` seul, `horizontal` seul, `vertical` seul,
jamais la **paire**, alors que `FiberDirectionLoss` demande précisément que l'axe *u* suive
les horizontales et l'axe *v* les verticales.

Campagne appariée — même graine, même rouleau, même volume, mêmes 120 générations, **une
seule clé change à la fois** :

| variante | aire cm² | auto-intersections | **tiers central** | au bord | α |
|---|---:|---:|---:|---:|---:|
| **témoin** | 19,825 | **0** | **32 %** | **39 %** | 1,332 |
| `sdt_weight` 1 | 19,824 | 0 | 9 % | 66 % | 0,901 |
| `sdt_weight` 10 | 19,824 | 0 | 6 % | 58 % | 0,971 |
| fibres h+v | 22,431 | **8 926** | 9 % | 53 % | 1,038 |
| `sdt` 10 + fibres h+v | 22,836 | **8 538** | 6 % | 59 % | 1,038 |

> ❌ **Les quatre dégradent la trace d'un facteur 3 à 5** sur la part des fenêtres dont le
> pic tombe dans le tiers central. Le témoin est le meilleur des cinq.

**`sdt_weight` ne mord pas.** Son aire est identique au témoin à la cinquième décimale
(−0,00 %), ses auto-intersections restent à zéro, et — le fait qui tranche — **le poids 1
et le poids 10 rendent exactement le même écart** (84,26 µm). Multiplier un poids par dix
sans rien déplacer veut dire que le terme ne tire sur rien.

**La paire de fibres CASSE le maillage** : 8 926 auto-intersections là où le témoin en a
**zéro**. Son gain d'aire (+13 %) est un artefact de ce repli — la surface se recouvre
elle-même, ce que confirme son compte de fenêtres avec matière, **128 contre 66** pour
13 % d'aire en plus.

### ⚠⚠ Et α disait l'inverse, parce que c'est un rapport de nombres CENSURÉS

L'α de convergence descend de 1,332 (témoin) à 0,901 (`sdt1`), ce qui se lit comme une
amélioration. C'est faux, et la raison est arithmétique : l'écart médian des **quatre**
variantes vaut **84,26 µm = exactement 9,00 couches**, soit la demi-fenêtre de 19. Leur pic
médian est donc **au bord**, et 84,26 µm n'est pas une mesure mais la **borne** de ce que
la fenêtre peut rapporter. α est le rapport de deux telles bornes.

> **Le témoin est le seul dont le pic médian tombe DANS la fenêtre** (couche 8 sur 19).
> C'est ce qui rend son 65,5 µm comparable à rien d'autre du tableau — et c'est pourquoi la
> colonne qui décide est le **tiers central**, qui compte des fenêtres et non une médiane.

⚠ **Fenêtres de 19 et 41 couches, et c'est une contrainte, pas un réglage.** Le pas
inter-feuilles de PHerc0358 vaut **187,2 µm** à 9,362 µm par voxel : 19 couches font
0,95 pas, 41 en font **2,05**, et les 161 de la version initiale de cette campagne en
faisaient **8,05**. Au-delà d'un pas, la fenêtre contient plusieurs feuilles et l'argmax
désigne celle qui se trouve être la plus brillante (`20` §9). La campagne a été **arrêtée
et relancée** pour cette raison.

## 10. Reproduire

```bash
# le champ, seulement autour de la trace (626 Mo au lieu de plusieurs Go)
python3 src/outils/fetch_champ_normal.py \
  PHerc0358/representations/predictions/lasagna/20250821151737-lasagna-20260419180421 \
  PHerc0358 data/champ_PHerc0358 --niveau 2 --boite 811 2144 837 2175 1595 2295

# l'encodage, mesure et non suppose
uv run python src/nappe/valider_champ_normal.py \
  "<prediction>.zarr" "<lasagna>" --rouleau PHerc0358 --centre 5842 5839 7386 \
  --balayage-centre 0 64 96 128 160 192 255
```

et dans `seed.json` :

```json
"direction_fields": [
  {"zarr": "/chemin/absolu/vers/champ", "dir": "normal", "scale": 2.0}
]
```


---

## 9. T1f — le balayage complet, deux graines et deux tirages

2026-08-19, nuit. Balayage {5, 10, 15, 20, 30, 40} sur PHerc0358, **deux graines** — celle
de `25` (planéité) et celle de `24` — dépouillé par `src/tables/table_pas.py`.

Le balayage lui-même, puis son dépouillement :

```
bash src/campagnes/campagne_pas.sh                                         # bonne graine
bash src/campagnes/campagne_pas.sh \
    data/trace/PHerc0358/pas_mauvaise_graine "1544 1544 7768"              # celle de 24

uv run python src/tables/table_pas.py                                      # bonne graine
uv run python src/tables/table_pas.py data/trace/PHerc0358/pas_mauvaise_graine
```

⚠ Les deux graines sont **lues dans les traces**, pas retapées : `seed location [5842, 5839,
7386]` d'un côté, `[1544, 1544, 7768]` de l'autre. La première est le défaut du script, ce qui
est aussi pourquoi la seconde était irreproductible sans lire le code.

⚠⚠ La campagne est **reprenable, et seulement sur un succès** : un pas déjà mesuré est sauté
uniquement si son résumé porte `statut: ok`. Le 2026-08-19 un `timeout` fixe a tué `pas_5` à la
génération 406 sur 480 alors qu'il croissait bien — pas de maillage, donc `aire_cm2: 0` et
`transverse: 0`, c'est-à-dire **exactement le résultat qu'on espère**, pour un run qui n'a rien
produit. Et la garde de reprise l'aurait sauté pour toujours.

⚠ Vérifié le 2026-09-05 : les deux commandes rendent **exactement** les deux colonnes du tableau
ci-dessous, y compris les étendues relatives de **5,5 %** et **12,0 %**. La première n'a pas
d'argument parce que la bonne graine est le défaut de l'outil — ce qui est aussi pourquoi la
seconde colonne était irreproductible sans lire le code.

⚠ **La comparaison n'est pas triviale, et c'est la moitié du travail.** Une surface croît
par un **front**, donc son aire va comme (k × pas)² : à générations égales, un pas de 5
couvre **seize fois moins** qu'un pas de 20. Comparer des comptes bruts ferait passer la
**lenteur** pour de la **qualité**. Le nombre de générations est donc mis à l'échelle en
**1/pas**, et la première chose que le dépouillement vérifie est que les aires obtenues
sont comparables — elles le sont, à **5,5 %** et **12,0 %** près.

| `step_size` | bonne graine — aire / croisements | mauvaise graine — aire / croisements |
|---:|---:|---:|
| **5** | 20,42 cm² / **16 426** *(804 par cm²)* | 9,49 cm² / **7 304** *(770 par cm²)* |
| 10 | 20,18 cm² / **4 613** | 8,42 cm² / 0 |
| 15 | 19,95 cm² / 0 | 8,84 cm² / 0 |
| 20 | 19,82 cm² / 0 | 8,68 cm² / 0 |
| 30 | 19,57 cm² / 0 | 9,05 cm² / 0 |
| 40 | 19,33 cm² / 0 | 8,80 cm² / 0 |

### ⭐⭐ Et un second tirage est tombé par accident — il démolit la première lecture

Le correctif de la garde de reprise (`statut == ok`) a fait **rejouer tout le balayage de
la bonne graine**, puisque les résumés antérieurs n'avaient pas ce champ. On dispose donc
de **deux tirages indépendants du même réglage** :

| `step_size` | 1er tirage | 2e tirage |
|---:|---:|---:|
| 5 | *tué par le timeout* | **16 426** |
| **10** | **0** | **4 613** |
| **15** | **947** | **0** |
| 20 | 0 | 0 |
| 30 | 0 | 0 |
| 40 | 0 | 0 |

⚠⚠ **Les pas 10 et 15 se contredisent avec eux-mêmes.** La première version de cette
section concluait « 4 pas sur 5 rendent zéro, l'anomalie à 15 est un point isolé ». Cette
lecture reposait sur **un tirage par réglage** — exactement ce que
[`30`](30_le_traceur_est_un_tirage.md) a mesuré comme n'étant pas une mesure.

### Ce qui survit à la répétition, et c'est utilisable

| constat | réplication |
|---|---|
| ⭐ **un pas de 5 détruit la trace** | **deux graines**, ~800 croisements par cm² des deux côtés |
| ⭐ **au-delà de 20, c'est propre** | deux graines **et** deux tirages, zéro partout |
| ⚠ **entre les deux (10, 15), le résultat n'est pas reproductible** | 0 contre 4 613 sur le même réglage |

> **Règle utilisable : `step_size` ≥ 20.** Ce n'est pas un réglage à optimiser, c'est un
> **plancher à ne pas franchir** — et la zone 10–15 est celle où la variance du traceur
> domine.

⚠⚠ **Et ça inverse l'hypothèse de `24` §4** — *« réduire `step_size` : moins de liberté à
chaque pas, donc moins de chances de sauter »*. La mesure dit le contraire, et lourdement :
un pas plus petit demande **quatre fois plus de générations** pour la même aire, donc
quatre fois plus d'occasions pour la surface de se replier sur elle-même. Ce n'est pas une
anomalie de réglage, c'est un effet mesuré des deux côtés.

### ⭐ Ce que la campagne a coûté, mesuré

| | `thread_limit: 1` | `thread_limit: 0` |
|---|---:|---:|
| durée d'une trace | **65,2 s** | **21,4 s** |
| CPU | **329 %** (3,3 cœurs) | **1431 %** (14,3 cœurs sur 22) |
| RAM crête | **91 Mo** | **117 Mo** |
| réseau | **0,2 Mo** | **0,1 Mo** |

Trois faits qui répondent à « est-ce que c'est optimisé ? » :

1. ⭐ **Ce n'est pas borné par le réseau.** 0,1 Mo par trace : la prédiction est en cache
   local (`cache_size: 6 Gio`). C'est **borné par le CPU**.
2. ⭐ **Ce n'est pas borné par la mémoire non plus.** 117 Mo de crête, sur une machine qui
   en a 31 Gio. Rien à optimiser de ce côté.
3. ⚠⚠ **`thread_limit: 1` coûte un facteur 3 en temps**, et il ne veut **pas** dire
   « mono-thread » : il tourne quand même à 3,3 cœurs. Nos campagnes l'ont posé pour
   réduire la variance entre exécutions — or `30` a mesuré que **ça ne la réduit pas**
   (le mauvais tirage est arrivé à `thread_limit: 0`, et les deux valeurs donnent des
   aires variables). **On a payé ×3 pour un déterminisme qu'on n'obtient pas.**

⚠ Et à `thread_limit: 0` l'outil n'utilise que **14,3 cœurs sur 22**. La croissance est
**séquentielle en générations** — chaque génération dépend de la précédente — donc le
parallélisme est borné par la taille du front, petit au début. C'est une limite de
l'algorithme, pas du réglage.

> ⭐⭐ **Conséquence pour la stratégie d'échantillonnage de `30`** : pour tirer N traces, ce
> qui compte n'est pas la latence d'une trace mais le **débit**. À 3,3 cœurs par trace on
> en lance **6 en parallèle** sur 22 cœurs ; à 14,3 cœurs, une seule et demie. *(Calcul,
> pas mesure : 22/3,3 × 1/65 s ≈ **1 trace toutes les 10 s** contre 22/14,3 × 1/21,4 s ≈
> **1 toutes les 14 s**.)* `thread_limit: 1` est donc le bon réglage — mais pour une
> raison de **débit**, pas pour la raison de déterminisme qu'on croyait.

⚠ `use_cuda` est à **false**, et le reste : le chemin GPU de l'outil est **CUDA**, et cette
machine a un iGPU **Intel Arc**. Il n'y a pas de GPU à saturer ici.

