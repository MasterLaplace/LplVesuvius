# Le prédicat vérifié est plus étroit que le défaut

2026-08-17. Trouvé en cherchant ce qu'il restait à tester avant d'attaquer.
Toutes les mesures sont sur PHerc0172 (Scroll 5) et rejouables.

---

## 1. La donnée que personne n'exploitait

`windcheck` publie, pour chaque trace, une **séparation en tours de spire** :
de combien de spires sont éloignées les deux parties qui se croisent. Elle est dans
`results/index.json` (`separation_rev`, `band`) et elle partage le corpus en deux
populations qui n'ont rien à voir :

| bande | traces | lecture |
|---|---|---|
| `< 0,15 tour` | **43** | croisement **local** — deux bouts voisins de la même spire |
| `≥ 1,6 tour` | **9** | la trace traverse **jusqu'à 5,04 tours** |

Les 9 sévères sont **exactement les traces `auto_grown`**. Un croisement à cinq
tours n'est pas un tremblement numérique : c'est le *sheet switching*, quantifié.

## 2. Le résultat négatif de `04` tient dans les deux bandes

Le soupçon était qu'agréger les deux bandes noyait un signal des sévères. Vérifié :

| bande | segments | n excisées | delta de Cliff | p |
|---|---|---|---|---|
| `< 0,15 tour` | 43 | 22 703 | **−0,0216** | 4,6e-07 |
| `≥ 1,6 tour` | 9 | 53 107 | **+0,0090** | 1,3e-03 |

Deux effets négligeables, **de signes opposés**. Le résultat de `04` — les cellules
excisées sont du papyrus ordinaire — est donc robuste au facteur de confusion le
plus évident.

## 3. Ce que le croisement fait à l'image aplatie

Une trace `tifxyz` **est déjà** la paramétrisation 2D : chaque cellule de grille
porte sa position 3D. Un croisement veut donc dire que **deux endroits éloignés de
l'image pointent vers des positions 3D voisines**.

Mesuré sur `auto_grown_…_1` (grille 629 × 2815, 654 événements de croisement), en
cherchant les cellules proches de chaque site de croisement :

| rayon | en µm | croisements avec ≥ 500 colonnes d'écart (sur 10) |
|---|---|---|
| 2 vx | 16 | **0** — aucune paire |
| 5 vx | **40 (une feuille)** | **0** (une paire à 329 col) |
| 10 vx | 79 | 4 |
| 20 vx | 158 | 8 |
| 40 vx | 316 (≈ inter-spire) | 9 |

⚠ **Correction d'une revendication trop forte.** J'ai d'abord mesuré à 40 voxels et
conclu « le même papyrus est rendu deux fois ». C'est faux : 40 voxels valent 316 µm,
soit **l'écart entre spires voisines**, donc le rayon attrapait la spire d'à côté. À
une vraie épaisseur de feuille (5 vx), l'effet **disparaît**.

L'énoncé défendable est plus étroit et suffit :

> Aux sites de croisement sévères, deux parties de la trace séparées de **jusqu'à
> 1564 colonnes** dans l'image aplatie s'approchent à **79–158 µm** en 3D — bien à
> l'intérieur des 300 µm qui séparent deux spires, sans être à l'épaisseur d'une
> feuille.

## 4. ⚠ La réparation ne retire pas cette approche

C'est le point qui compte. Même mesure, avant et après `windcheck transform` :

| rayon | croisements à ≥ 500 col **avant** | encore ≥ 500 col **après** |
|---|---|---|
| **10 vx (79 µm)** | **9** | **8** |
| ~~20 vx (158 µm)~~ | ~~15~~ | ~~15~~ — **voir la correction §4bis** |

Et les valeurs sont **littéralement inchangées** : 974 → 974, 1564 → 1564,
589 → 589, 585 → 585. Sur cette trace la réparation retire 3 220 cellules
(0,2 % des 1 592 534), le recensement passe de « NOT clean » à « clean », et
l'approche entre deux régions distantes de l'image **reste exactement où elle
était**.

### Ce que ça veut dire, précisément

`windcheck` fait **exactement ce qu'il annonce** : rendre la surface sans contact
transverse, et il le prouve. Ce n'est pas un défaut de l'outil, c'est la portée de
son prédicat.

Mais un consommateur qui lit « cette trace est propre » en déduira volontiers
« cette trace est une feuille unique bien plongée ». **Ce n'est pas ce qui est
livré.** L'anomalie géométrique — deux régions de l'image qui se frôlent en 3D à
un cinquième de l'écart entre spires — survit intacte à la réparation.

Autrement dit : **le prédicat vérifié est plus étroit que le défaut.** C'est le
motif que ce projet connaît sous un autre nom — une vérification qui passe pour une
raison qui ne veut pas dire ce qu'on croit.

## 4bis. ⚠⚠ Correction : « 300 µm entre spires » était emprunté, pas mesuré

Déclenchée par une observation de l'auteur sur une image du site — *« ça a l'air très
packé, même à haut niveau de précision »*. Il avait raison, et ça invalide la moitié
du §4.

Le chiffre de 300 µm venait du README de `vesuvius-automesh` et portait sur le
**Scroll 3**. Mesuré ici, sur la trace elle-même — distance de chaque cellule à la
partie **non adjacente** la plus proche, 4 000 cellules échantillonnées :

| percentile | distance |
|---|---|
| p1 | 61 µm |
| p5 | 101 µm |
| p25 | 141 µm |
| **p50** | **177 µm** |
| p75 | 231 µm |
| p90 | 303 µm |

**L'écart typique est 177 µm, pas 300.** Et **37,2 %** des cellules sont à moins de
158 µm d'une partie non adjacente.

Donc :

- le résultat à **20 vx (158 µm)** portait sur une distance **parfaitement
  ordinaire** — plus d'un tiers de la trace est aussi proche. Il ne prouve rien et
  il est retiré ;
- le résultat à **10 vx (79 µm)** tient : seules **2,1 %** des cellules sont aussi
  proches, donc c'est bien une queue de distribution.

### Ce que cette correction apprend pour la suite

Une proximité ne veut rien dire dans l'absolu : **100 µm est banal là où les couches
sont à 120 µm, et alarmant là où elles sont à 400 µm.** Le tassement varie le long
d'un même rouleau — c'est exactement ce que montre la comparaison DLS 7,91 µm /
ESRF 2,4 µm publiée sur le site, où une région comprimée sépare mal ses couches.

Toute métrique de proximité doit donc être **normalisée par l'espacement local**,
jamais comparée à une constante. C'est la principale leçon de conception de cette
passe, et elle vient d'un doute exprimé sur une capture d'écran, pas d'une relecture
de code.

## 5. Ce que ça ouvre

Les trois mesures se recoupent en une lecture cohérente :

1. les cellules excisées sont du papyrus ordinaire (`04`, 75 810 cellules, H₀ non
   rejetée) — donc le défaut n'est pas dans le **contenu** ;
2. les croisements sévères relient des régions distantes de l'image, et sont
   concentrés dans les traces **automatiques** ;
3. la réparation supprime le contact et **laisse l'approche** — donc le défaut n'est
   pas non plus dans le **contact**.

Ce qui reste, et qui n'est mesuré par personne, c'est la **proximité anormale entre
régions non adjacentes de la paramétrisation**. C'est une grandeur continue, calculable
depuis la trace seule, sans volume, sans modèle — et elle sépare déjà les traces
automatiques des traces supervisées.

⚠ **Portée** : un rouleau, une trace analysée en détail pour la §3–4, un outil de
réparation. À étendre aux 9 sévères avant toute revendication générale.
