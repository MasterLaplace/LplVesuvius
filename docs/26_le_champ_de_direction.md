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
| le même, `dir: horizontal` | 20,33 | **10 623** |

⭐ **Le classement est ordonné, et c'est le fait qui compte.** Un champ délibérément faux
est **7 fois pire** que le nôtre, et une mauvaise *sémantique* (`horizontal` au lieu de
`normal`) est pire encore — **9 fois**. Donc le champ **est bel et bien consommé**, et le
nôtre est **le moins faux des quatre** : assez juste pour battre largement une permutation
et un contresens, pas assez pour aider.

⚠ Ce qui désigne un défaut de **registration** plutôt que d'encodage — l'encodage, lui, est
mesuré à 6° sur trois rouleaux. Le suspect nommé est la sémantique de `scale` : s'il
signifie *facteur* et non *niveau*, chaque lecture est décalée d'un facteur deux, ce qui
donne exactement ce profil — approximativement juste près de l'origine, de plus en plus
faux en s'en éloignant.

### Ce que ça corrige de ce qu'on croyait

`24` §4 nommait `direction_fields` comme *la* cause de la trace qui coupe les spires, et
`25` reprenait ce diagnostic. **Il est faux, ou du moins hors de portée** : donner le champ
ne change pas la croissance, donc l'absence du champ ne peut pas expliquer la trajectoire.

## 4. Reproduire

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
