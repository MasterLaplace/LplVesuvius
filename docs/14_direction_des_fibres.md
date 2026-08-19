# La direction des fibres — problème ouvert nº 5

2026-08-18. `06` §3.4 et la voie C du batch. **Discriminant physique**, donc déroulement
pur : il ne demande ni vérité terrain, ni modèle d'encre, ni juge.

---

## 1. L'idée, et pourquoi elle appartient à l'objectif

Une feuille de papyrus est faite de **deux plis collés, fibres perpendiculaires** — le
recto horizontal, le verso vertical. C'est une propriété de la matière, visible sans
encre. Deux conséquences se déduisent directement :

1. en **traversant** une feuille, l'orientation dominante devrait basculer de ~90° ;
2. deux feuilles voisines n'ont aucune raison de partager un sens, donc une trace qui
   **saute d'une spire à l'autre** traverse une discontinuité d'orientation.

## 2. La mesure

`analysis/src/fiber_orientation.py`. Tenseur de structure — la covariance des gradients
donne en forme close la direction le long de laquelle l'image varie le moins :

```
J = [[<gx²>, <gx·gy>], [<gx·gy>, <gy²>]]     θ = ½·atan2(2·<gx·gy>, <gx²> − <gy²>)
```

⚠ **Une orientation est modulo 180°, pas 360°** — une fibre n'a pas de sens. Tout se
moyenne en **angle double** : sinon 179° et 1° donnent une moyenne de 90°, soit
exactement leur perpendiculaire.

⚠ **La cohérence est rapportée à côté de l'angle**, et ce n'est pas décoratif : sur une
zone sans texture, l'angle est **aléatoire mais parfaitement défini**. Sans la
cohérence, du bruit se lit comme une direction.

⚠ Exige un volume qui résout les fibres (~10–20 µm) : 1 à 2 voxels à 7,91 µm, 4 à 8 à
2,4 µm, une quinzaine à 1,129 µm. Donc les **volumes de surface ESRF**, lus chunk par
chunk à distance (`12` §10).

## 3. ⚠⚠ La bascule recto/verso ne se voit PAS

Mesure sur `20230702185753`, volume 2,4 µm, la fenêtre la plus cohérente :

| couche | angle | cohérence |
|---:|---:|---:|
| 0 | 89,8° | 0,42 |
| 25 | 94,4° | 0,62 |
| **35** | 93,6° | **0,64** |
| 65 | 111,8° | **0,08** |
| 80 | 97,1° | 0,32 |
| 105 | 95,4° | 0,15 |

**L'orientation reste à 90–97° sur les 109 couches.** Pas de bascule.

✅ Mais la mesure **répond bien au contenu** et non à un artefact : l'angle ne devient
erratique (111,8°, 79,2°) que là où la cohérence s'effondre à 0,06–0,08 — c'est-à-dire
**dans l'interstice entre deux feuilles**, exactement où il n'y a rien à orienter. Un
biais de rééchantillonnage aurait donné un angle constant *partout*, cohérence comprise.

⚠ Et ~90° n'est pas suspect : dans les coordonnées **aplaties** d'un volume de surface,
un pli dont les fibres suivent l'axe du rouleau est aligné sur un axe de l'image. C'est
attendu pour **un** pli ; c'est l'autre qui manque.

Trois explications non départagées :
- à 2,4 µm les deux plis ne se distinguent pas en contraste ;
- la fenêtre lue (109 × 2,4 µm = **262 µm**) est mal centrée sur la feuille ;
- ⚠ à 1,129 µm la fenêtre ne fait que **123 µm**, soit **moins qu'une épaisseur de
  feuille** — elle ne peut structurellement pas traverser les deux plis.

## 4. 🎯 Le pivot : l'orientation est une propriété SPATIALE

Ce qui n'est pas exploitable en profondeur l'est en surface. Deux fenêtres voisines
posées sur la **même** feuille doivent s'accorder ; une trace qui saute d'une spire à
l'autre fait sauter l'orientation.

⚠ La dispersion se mesure entre fenêtres **voisines**, jamais globalement : la courbure
du rouleau fait varier l'orientation lentement d'un bout à l'autre d'un segment, et une
dispersion globale confondrait cette variation légitime avec un saut.

⚠ **Bug attrapé en le mesurant** : la première version tirait des fenêtres sur une
grille lâche, donc séparées d'une vingtaine de chunks — **aucune n'était voisine
d'aucune autre**, et la statistique rendait `NaN` sur **0 paire comparée** au lieu de
signaler qu'elle n'avait rien mesuré. Corrigé en échantillonnant des **amas de 2×2
chunks** répartis : plusieurs mesures *locales* à plusieurs endroits.

### Résultats sur 12 segments de Scroll 1 (volumes 2,4 µm)

| segment | cohérence | désaccord médian entre voisins | > 30° |
|---|---:|---:|---:|
| `20231005123336` | 0,307 | **4,3°** | 18 % |
| `20230702185753` | 0,291 | 7,7° | 38 % |
| `20231022170901` | 0,308 | 13,3° | 33 % |
| `20231221180251` | 0,302 | 14,5° | 36 % |
| `20231007101619` | 0,273 | 15,4° | 38 % |
| `20231210121321` | 0,330 | 20,0° | 32 % |
| `20231031143852` | 0,271 | 21,6° | 40 % |
| `20231106155351` | 0,327 | 23,9° | 48 % |
| `20230929220926` | 0,244 | 26,0° | 45 % |
| `20231012184424` | 0,322 | 42,3° | 56 % |
| `20231016151002` | 0,287 | **42,5°** | 67 % |

L'étalement est large — **4,3° à 42,5°** sur un seul rouleau — ce qui est la première
condition pour qu'une grandeur puisse discriminer quoi que ce soit.

## 5. ⚠⚠ Le test contre un recensement indépendant : NON CONCLUANT, et c'est la puissance

`windcheck` publie un compte de **croisements** par segment, obtenu par une méthode
entièrement différente. C'est le seul contrôle disponible qui ne demande ni vérité
terrain, ni encre, ni juge.

| grandeur | rho ~ croisements | p |
|---|---:|---:|
| **désaccord médian entre voisins** | **+0,330** | 0,294 |
| cohérence médiane | +0,354 | 0,259 |
| part des voisins > 30° | +0,118 | 0,715 |
| bascule médiane en profondeur | −0,189 | 0,557 |

> ⚠⚠ **À n = 12, la mesure ne détecte qu'un rho ≥ 0,73 à 80 % de puissance.** Le +0,330
> observé va dans le sens attendu et **le zéro n'est pas informatif** : il dit que
> l'échantillon est trop petit, pas que l'effet est absent.

C'est la règle nº 7 du dépôt (rapporter la puissance avec un zéro), et elle dit ici quoi
faire plutôt que quoi conclure : pour qu'un rho de 0,33 soit détectable au même niveau
il faut **n ≈ 70**. Le corpus en offre **80**, et la campagne complète est lancée
(`tools/campagne_fibres.sh`, en file derrière celle de la profondeur — les deux lisent
le même bucket, se les disputer allongerait les deux).

⚠ Noter aussi : la **bascule en profondeur** ne corrèle avec rien (−0,189), ce qui est
cohérent avec le §3 — elle ne mesure pas ce qu'elle prétendait.

## 6. ⚠ Le contrôle Scroll 4 ne sépare pas non plus, pour l'instant

Premier segment de PHerc1667 : désaccord **38,7°**, > 30° sur 62 % des paires. C'est
haut, mais **dans l'intervalle de Scroll 1** (4,3–42,5°). Un segment ne tranche rien
contre une distribution aussi étalée ; la campagne dira si la *distribution* de Scroll 4
est décalée.

## 7. ❌ Rien ne reste — la voie est close

*(2026-08-19)* Ce qui suit était la liste des suites envisagées. **Elle est sans objet** :
la campagne sur 80 segments a fait **inverser le signe** (+0,330 à n = 12 → **−0,192** à
n = 54), et une grandeur dont le signe dépend de la taille de l'échantillon ne se
prolonge pas, elle se jette. Conservé tel quel ci-dessous pour que la raison de l'abandon
reste lisible.

## 7 bis. *(archive)* Ce qui restait avant la réfutation

- la campagne sur les 80 segments de Scroll 1 (**en file**), qui donnera la puissance ;
- ⭐ **le contraste avec Scroll 4** sur une distribution et non un point ;
- ⚠ la bascule recto/verso reste **non expliquée** : trois causes candidates (contraste
  entre plis trop faible à 2,4 µm, fenêtre mal centrée, ou fenêtre plus courte qu'une
  épaisseur de feuille à 1,129 µm) et aucune départagée.


---

## 8. ⚠⚠ La campagne complète : l'instrument NE valide PAS, et le signe s'inverse

80 segments mesurés, 54 communs avec l'index publié de `windcheck`.

| grandeur | n = 12 | **n = 54** | p |
|---|---:|---:|---:|
| **désaccord médian entre voisins** | **+0,330** | **−0,192** | 0,165 |
| part des voisins > 30° | +0,118 | −0,268 | 0,050 |
| cohérence médiane | +0,354 | −0,246 | 0,073 |
| bascule médiane en profondeur | −0,189 | −0,064 | 0,644 |

> **Le signe s'est inversé.** Le +0,330 de n = 12 était du bruit, et l'analyse de
> puissance le disait déjà : à n = 12, seul un rho ≥ 0,73 était détectable.

Rien n'atteint le seuil après correction pour tests multiples. **L'orientation des
fibres, telle que mesurée ici, ne prédit pas les croisements recensés.**

### ⚠ Ce que ça ne condamne pas

L'orientation **est** mesurable (cohérence jusqu'à 0,64) et la mesure répond au
contenu. Ce qui échoue est l'hypothèse que j'en ai tirée : *deux fenêtres voisines en
désaccord signalent un saut de feuille*. Trois raisons possibles, non départagées :

1. la fenêtre de 128×128 voxels à 2,4 µm fait **307 µm de côté** — une seule cellule de
   texture, peut-être trop petite pour une orientation stable ;
2. la courbure du rouleau fait varier l'orientation légitimement, et le filtre « entre
   voisins » ne l'absorbe qu'imparfaitement ;
3. ⚠ le compte de croisements de `windcheck` n'est peut-être pas le bon référent — il
   mesure l'auto-intersection d'un maillage, pas le saut de feuille.

### ⭐ Et ce que le site du concours en dit, mot pour mot

> *« check if you can visually follow **horizontal papyrus fibers** across the page —
> this is an indication the segmentation is good (**and not jumping between sheets**) »*
> — page *Prizes*, section « How to get started » du Grand Prize 2027.

Les organisateurs désignent donc la continuité des fibres comme **le** critère visuel
de bonne segmentation. L'idée n'est pas fausse ; c'est **notre façon de la mesurer** qui
ne corrèle pas. La bonne suite n'est pas d'abandonner mais de mesurer la continuité
**le long d'une ligne de texte**, comme un œil le fait, plutôt que la dispersion entre
carrés voisins.
