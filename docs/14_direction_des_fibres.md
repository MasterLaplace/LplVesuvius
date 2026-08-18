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

Premiers résultats, Scroll 1, volumes 2,4 µm :

| segment | cohérence | désaccord médian entre voisins | > 30° |
|---|---:|---:|---:|
| `20231005123336` | 0,307 | **4,3°** | 18 % |
| `20230702185753` | 0,291 | **7,7°** | 38 % |

## 5. ⏳ Ce qui reste

- la campagne sur les 80 segments de Scroll 1 (lancée) ;
- ⭐ **le contraste avec Scroll 4**, dont `12` §10 dit que la trace n'est sur aucune
  feuille : la prédiction, posée ici avant de la mesurer, est un **désaccord entre
  voisins nettement plus élevé** ;
- ⭐ croiser avec les **croisements publiés** de `windcheck` : le désaccord d'orientation
  prédit-il ce qu'un recensement indépendant recense ?
