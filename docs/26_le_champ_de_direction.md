# `direction_fields` — le contrat, l'encodage, et un champ qui n'agit pas

2026-08-19, suite de [`25`](25_une_graine_choisie_sur_la_planeite.md). La moitié restante
de T1 : *où l'on part* était réglé, *comment on avance* ne l'était pas. Le paramètre qui
devait le régler s'appelle `direction_fields`, et rien ne le documente.

**Résultat en une ligne** : le contrat est **dérivé**, l'encodage des octets est **mesuré
et répliqué sur trois rouleaux** — et le champ, une fois branché, **ne change rien à la
croissance**. Six exécutions, dont trois avec des champs différents, produisent la **même
trajectoire au centième sur 118 générations**.

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

⭐ **Et il est bien consommé** : la densité d'auto-intersections chute d'un facteur **12**
entre `weight: 10` et `direction_weight: 100` (3 035 → 249 par cm²). Le champ organise donc
réellement quelque chose — simplement pas assez pour battre **zéro**.

> ⭐ **`direction_fields` ne peut donc pas être le remède d'une trace posée en travers de
> l'empilement** : la trajectoire est décidée pendant la croissance, et rien de ce
> paramètre n'y touche — ni sa présence, ni son orientation, ni son intensité.

### Ce que ça corrige de ce qu'on croyait

`24` §4 nommait `direction_fields` comme *la* cause de la trace qui coupe les spires, et
`25` reprenait ce diagnostic. **Il est faux, ou du moins hors de portée** : donner le champ
ne change pas la croissance, donc l'absence du champ ne peut pas expliquer la trajectoire.

## 4. ⭐⭐ Les dix poids de perte sont réglables — et personne ne le documente

`vc_grow_seg_from_seed` imprime au démarrage la ligne qui décide de tout :

```
GrowPatch loss weights:
  DIST: 1 STRAIGHT: 0.2 DIRECTION: 1 SNAP: 0.1 NORMAL: 10
  NORMAL3DLINE: 0 REFERENCE_RAY: 0 SURFACE_SDT: 0 SPACELINE: 0 SDIR: 1
```

Les dix noms se lisent dans `libvc_tracer.so`, et **les dix se règlent depuis le
`seed.json`** — vérifié en leur donnant des valeurs distinctes et en relisant la ligne :

| terme imprimé | clé du `seed.json` | défaut |
|---|---|---:|
| `DIST` | `dist_weight` | 1 |
| `STRAIGHT` | `straight_weight` | 0,2 |
| **`DIRECTION`** | **`direction_weight`** | **1** |
| `SNAP` | `snap_weight` | 0,1 |
| **`NORMAL`** | **`normal_weight`** | **10** |
| `NORMAL3DLINE` | `normal3dline_weight` | 0 |
| `REFERENCE_RAY` | `reference_ray_weight` | 0 |
| `SURFACE_SDT` | `surface_sdt_weight` | 0 |
| `SPACELINE` | `spaceline_weight` | 0 |
| `SDIR` | `sdir_weight` | 1 |

⚠ **`SDIR` n'est pas « surface direction »** : la bibliothèque le nomme
`conditional_sdirichlet_loss` — c'est un terme de **Dirichlet**, une régularité de
paramétrisation, sans rapport avec les champs de direction. Le terme que `direction_fields`
alimente est `DIRECTION`, à **1** contre un `NORMAL` à **10**.

⭐ **C'est probablement pourquoi le champ ne déplace pas la croissance** : son terme pèse
un dixième de celui qui domine. Le tester est immédiat une fois le nom connu, et c'est
exactement ce qu'aucune documentation ne donne.

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

## 6. ⏳ La piste qui reste, et elle est nommée

`libvc_core.so` contient un **second mécanisme**, distinct de `direction_fields`, dont les
messages décrivent exactement le format que le concours publie :

```
Not a normal-grid directory (expected xy/, xz/, yz/ subdirs and metadata.json).
Skipping normal_grid '{}': path does not exist
Remote normal_grid entry '{}' not yet supported.
```

C'est `NormalGridVolume(path, level)`, consommé par `NormalConstraintPlane::
calculate_normal_snapping_loss` — donc le terme **`NORMAL`, celui qui pèse 10**. Et les
`.normal-grids` publiées à côté de chaque prédiction (182 Mo, `xy/ xz/ yz/`) sont
**déjà dans ce format**, sans conversion : ce sont les sorties de `vc_gen_normalgrids`.

⚠ La clé `normal_grids` **n'est pas lue** par le `seed.json` de ce binaire (un tableau
d'objets passe sans un mot, quelle que soit la forme essayée). Elle vient donc d'ailleurs —
le paquet de volume, un manifeste `normal-grids-remote.json`, ou une découverte à côté du
volume, ce qu'une URL `https://` empêche. **C'est la prochaine chose à trouver**, et c'est
un meilleur candidat que `direction_fields` : c'est le terme dominant, et son format est
déjà publié.

## 7. Reproduire

```bash
# le champ, seulement autour de la trace (626 Mo au lieu de plusieurs Go)
python3 tools/fetch_champ_normal.py \
  PHerc0358/representations/predictions/lasagna/20250821151737-lasagna-20260419180421 \
  PHerc0358 data/champ_PHerc0358 --niveau 2 --boite 811 2144 837 2175 1595 2295

# l'encodage, mesure et non suppose
cd experiments && uv run python ../analysis/src/valider_champ_normal.py \
  "<prediction>.zarr" "<lasagna>" --rouleau PHerc0358 --centre 5842 5839 7386 \
  --balayage-centre 0 64 96 128 160 192 255
```

et dans `seed.json` :

```json
"direction_fields": [
  {"zarr": "/chemin/absolu/vers/champ", "dir": "normal", "scale": 2.0}
]
```
