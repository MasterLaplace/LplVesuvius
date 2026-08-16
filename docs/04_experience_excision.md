# Expérience : les cellules excisées étaient-elles vraiment mauvaises ?

Conception, 2026-08-16. Écrite **avant** le code, et avec son critère de réfutation.

---

## 1. La question, réduite à quelque chose qui peut échouer

`windcheck` détecte qu'une trace se traverse elle-même, puis répare. Le certificat
dit exactement ce que « réparer » veut dire ici, et c'est plus étroit que le mot ne
le suggère :

- `displacement/applied = False` — rien n'est déplacé ;
- l'excision est portée par le **masque** : les cellules fautives sont marquées
  `mask = 0` **et** `x = y = z = -1` ;
- *« Every RETAINED coordinate is bit-identical to the input »*.

La trace propre est donc **l'originale moins quelques cellules**. Sur notre segment
témoin : 6 quads sur 416 398 triangles, **896,8 unités d'aire sur 83 256 262**, soit
0,0011 %.

La question « est-ce que réparer améliore l'aval » se réduit alors à une question
beaucoup plus dure à esquiver :

> **Les cellules retirées échantillonnaient-elles autre chose que du papyrus ?**

Si oui, la réparation retire de la donnée fausse et l'amélioration en aval est
plausible. Si non, elle retire du papyrus ordinaire, et c'est du nettoyage
géométrique sans conséquence sur le texte.

## 2. Pourquoi c'est mesurable sans modèle ni entraînement

La physique donne le discriminant. Une feuille de papyrus est **plus dense** que le
vide entre deux spires : en tomographie elle apparaît comme une crête d'intensité,
d'environ 40 µm d'épaisseur, séparée de la spire voisine par 300 µm et plus.

Une cellule qui a traversé vers la spire voisine, ou qui flotte dans l'interstice,
n'a donc pas la même signature d'intensité qu'une cellule posée sur sa feuille.
C'est lisible **directement dans le volume**, sans réseau et sans étiquette.

## 3. Le protocole

Pour chaque segment atteint :

1. lire la trace originale et la trace réparée ;
2. **cellules excisées** = celles dont le masque passe de 1 à 0. Leurs coordonnées
   originales sont connues (elles ne valent `-1` que dans la sortie) ;
3. **population témoin** = un échantillon de cellules retenues, **apparié** — même
   segment, tiré dans un voisinage des cellules excisées, pour ne pas comparer un
   bord de trace à son centre ;
4. échantillonner le volume `20241024131839` (7,910 µm) aux deux populations ;
5. comparer les distributions d'intensité.

### Hypothèse nulle

**H₀ : les cellules excisées ont la même distribution d'intensité que les cellules
retenues appariées.**

Ne pas pouvoir rejeter H₀ est un **résultat**, pas un échec : ça dirait que la
réparation retire du papyrus ordinaire, donc que le défaut géométrique n'a pas de
contrepartie matérielle — et c'est exactement ce que personne n'a publié.

### Le contrôle qui attrape MES bugs, pas l'hypothèse

Les coordonnées retenues sont bit-identiques entre l'entrée et la sortie. Donc :

> échantillonner une même cellule retenue depuis la trace originale et depuis la
> trace réparée **doit** rendre la même valeur, au bit près.

Si ce n'est pas le cas, c'est mon échantillonneur qui est faux — indexation,
convention d'axes, interpolation — et non l'hypothèse. **Sans ce contrôle, une
différence due à une inversion d'axes se lirait comme une découverte.**

Second contrôle, sur le dénominateur : le nombre de cellules excisées effectivement
échantillonnées doit être **non nul** et égal au compte annoncé par le certificat.
Une comparaison sur un ensemble vide serait verte et ne dirait rien — c'est le
*dénominateur silencieux*.

## 4. Ce qui menace la mesure, et ce qu'on en fait

| menace | traitement |
|---|---|
| **Taille d'échantillon** : 6 quads sur un segment, c'est ~24 cellules. Aucune puissance statistique. | Passer à l'échelle des **52 segments atteints** de Scroll 5 et agréger les cellules excisées. |
| **Convention d'axes** entre tifxyz et zarr (ordre z/y/x, origine) | Contrôle bit-à-bit ci-dessus ; en cas d'échec, on corrige l'échantillonneur avant toute lecture du résultat. |
| **Biais de bord** : les cellules fautives pourraient être aux bords de trace, là où l'intensité chute pour une raison sans rapport. | Témoin **apparié en voisinage**, et report séparé de la distance au bord. |
| **Interpolation** : un voxel voisin peut lisser la différence. | Échantillonnage au **plus proche voisin**, entier, sans interpolation — et c'est de toute façon la seule forme reproductible bit à bit entre machines. |
| **Le volume est à 7,91 µm** alors qu'une feuille fait 40 µm | Une feuille fait donc ~5 voxels : suffisant. À ne pas tenter au niveau 4 (38 µm), où une feuille tient dans un voxel. |

## 5. Note de perf : le langage n'était pas la variable

Question posée en cours de route — « Python ne nique pas les perfs, ce serait pas
mieux en C ? ». Mesuré plutôt que tranché à l'opinion :

| grandeur | mesure |
|---|---|
| un voxel échantillonné individuellement | **512 ms** |
| une itération de boucle Python | **65 ns** |

Un facteur **huit millions**. Chaque accès `array[z, y, x]` déclenchait le
rapatriement d'un chunk de 128³ (~2 Mio) depuis S3 pour lire **un octet**.
Réécrire en C++ aurait fait passer les 65 ns à ~1 ns et laissé les 512 ms intacts :
**gain nul**, pour du code plus long et plus fragile.

Le correctif est algorithmique — grouper les points par chunk, ne télécharger
chaque chunk qu'une fois — et les cellules examinées sont adjacentes par
construction, donc elles partagent leurs chunks. Mesuré sur 200 points répartis
sur 19 chunks : **×8**, valeurs **identiques** (contrôle obligatoire : une
optimisation qui déplace le résultat n'en est pas une).

⚠ La question reste juste sur le fond, et l'écosystème lui a déjà donné la bonne
réponse : le noyau qui compte — l'intersection de triangles sur 3,5 M de triangles
— **est** en C++ chez `windcheck` (`engines/selfcross.cpp`, `clang++ -O3 -pthread`),
avec Python autour pour l'orchestration. C'est le découpage à reprendre le jour où
on écrit du calcul lourd ; ce n'était pas le cas ici.

## 6. Ce que l'expérience ne prouvera pas

Elle ne dira **pas** que le texte est mieux lu. Elle dira si la matière retirée
diffère de la matière gardée. C'est un maillon, pas la chaîne — mais c'est le
premier maillon, et il est aujourd'hui manquant.

⚠ Ne pas glisser de *« les cellules excisées échantillonnent autre chose »* à
*« réparer améliore le texte »*. Le second demande un rendu et un jugement
papyrologique ; le premier est de la physique mesurable cet après-midi.
