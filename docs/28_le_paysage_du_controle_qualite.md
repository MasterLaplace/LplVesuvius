# Le paysage du contrôle qualité — ce qui existe, ce qui a échoué, ce qui reste

2026-08-19. Avant de construire un instrument, savoir ce qui existe. Le dépôt s'interdit
d'écrire un septième vérificateur (`00` §4) ; encore faut-il tenir la liste à jour, et
elle a beaucoup bougé — **la quasi-totalité de cet écosystème a été créée entre le
1er juin et le 3 août 2026**.

⚠ **Ce qui est vérifié ici de mes yeux** : le contenu du clone `repos/villa` (les douze
poids de perte, leurs gardes, l'existence et les options de `vc_tifxyz_selfcross`), et le
clone `repos/tifxyz-surgeon` (ses quatre détecteurs, leurs docstrings, sa suite de tests).
**Ce qui vient d'une recherche sur l'API GitHub et de lectures de README** : le reste du
tableau du §3, les numéros de PR, et les chiffres que leurs auteurs publient. C'est dit
ici plutôt que laissé à deviner.

---

## 1. La position officielle, et les deux endroits où elle nous nomme

`/2026_open_problems` (10 juillet 2026) énumère les trois défauts, mot pour mot :

> *« **mergers**, where two nearby sheets are joined by mistake ; **holes**, where the
> predicted surface disappears ; **sheet switches**, where a traced mesh jumps from the
> intended sheet to a neighboring wrap »*

Et l'état de l'outillage :

> *« The current system is therefore best described as **semi-automated** »* —
> *« automatic growth still needs **human inspection and correction** »*

⭐ La case est nommée **deux fois**, et c'est la nôtre :

- **tableau des goulots**, ligne *Sheet switches* — approche actuelle : *« VC3D inspection
  and **manual correction** »* ; ce qui aiderait : *« Stronger local continuity
  constraints and **conservative failure detection** »* ;
- **appel à contribution nº 2** : *« help with **automatic topology repair** — building
  tools that catch mesh-tracing errors like holes, mergers, and sheet switches **without
  a human checking every traced piece of surface by hand** »*.

## 2. Ce qui existe officiellement, dans `villa`

| outil | ce qu'il fait | autonome ? |
|---|---|---|
| **`vc_tifxyz_selfcross`** | recensement d'auto-intersection transverse | ✅ **oui** |
| `vc_calc_surface_metrics` | `winding_error_fraction`, `surface_missing_fraction`, `in_surface_metric` | ❌ exige une *point collection* annotée à la main |
| `vc_fiber_trace_metric` | erreurs de traçage de fibre | ❌ manifeste annoté |
| `segmentation/evaluation/metrics/` | composantes critiques/connexes, Dice de ligne centrale, VOI, Betti | ❌ niveau voxel, exige une vérité terrain |

⭐⭐ **`vc_tifxyz_selfcross` est l'outil que `24` a utilisé pour condamner notre propre
trace.** Il a été **fusionné le 2026-08-04** (PR #1303), par un contributeur
communautaire — l'auteur de `windcheck`. Sa thèse, dans sa propre doc, est la meilleure
formulation du problème que j'aie lue :

> *La proximité entre spires est normale dans un rouleau écrasé et peut être
> arbitrairement petite alors que la trace est correcte, donc **aucun seuil de distance
> ne sépare les bonnes traces des mauvaises**. Une auto-intersection transverse est
> différente en nature : une surface plongée ne peut pas se traverser, donc c'est **un
> défaut sans lecture innocente, et sans seuil à débattre**.*

⚠ **Et ses deux limites sont écrites noir sur blanc** : *« not a general statement of
surface quality »*, et *« Counts are triangle-pair contacts… **They rank severity; they
do not count places.** »*

⚠⚠ **Un piège pour nous, vérifié dans le source** :
`vc_tifxyz_selfcross.cpp:79` pose `--maxedge` à **60 voxels** par défaut, et écarte les
quads dont une arête dépasse. Raison donnée : un triangle bâti en travers d'un trou
traverse tout sur son passage **uniquement parce que le maillage a un trou là**. Donc
**un trou peut fabriquer des croisements, et le filtre qui l'évite peut en masquer**. Nos
240 croisements de `24` n'ont jamais été relus sous un autre `--maxedge` — c'est une
mesure à faire.

## 3. Le paysage communautaire

Une douzaine de dépôts, tous à moins de quatre étoiles, tous récents.

| dépôt | ce qu'il détecte | recouvrement avec nous |
|---|---|---|
| **`enisme/tifxyz-surgeon`** | **`hole`, `grid_tear`, `self_contact` (signature de merger), `sheet_switch`** | ⚠⚠ **le plus fort — voir §4** |
| `aviad12g/tifxyz-doctor` | intégrité de format, trous du treillis, triangles pliés, sauts de normale, énergie de Dirichlet | fort — mais **ne revendique pas** la détection de sauts naturels |
| `joe-carr-data/windcheck` | auto-intersection + réparation ; **284 traces indexées**, benchmark public | fort — c'est la source de l'outil officiel |
| `spencerdavis-tx/vesuvius-automesh` | **quatre modes d'échec du traceur, étiquetés**, 157 fenêtres passes **et** échecs | fort — c'est un **jeu étiqueté**, rare |
| `Hob3rMallow/scrollfiesta_public` | gate binaire `turn_off` ≥ 5 % = FAIL, sur la phase angulaire entre cubes voisins | fort, mais **interne à son pipeline** |
| `Jinhojeong/vesuvius-unmerge` + `…-surface-geometry-diagnostic` | scission de feuilles fusionnées ; 200 patchs de vérité terrain | fort sur le *merger* |
| `Nicodol/spiralcheck` | évaluation held-out d'un ajustement de rouleau entier, **matrice de défauts plantés** | moyen — la méthodo est réutilisable |
| `Nieuwlaar/tifxyz-repair` | métadonnées ; `inspect` rend « sheet-switch/merger suspects » par KD-tree | faible — métadonnées, et suspects non classés |

## 4. ⭐⭐⭐ La limite mesurée de la détection par la GÉOMÉTRIE SEULE

C'est le fait le plus important de ce document, et **ce n'est pas nous qui l'écrivons**.
`tifxyz-surgeon` porte les quatre détecteurs les plus proches de notre cible. La
docstring de `find_sheet_switches` (`src/tifxyz_surgeon/detect.py:339`, lue dans le
clone) énonce sa propre limite :

> **Known limit.** *This sees displacement that **outruns** the frame, not displacement
> the frame **follows**. Spread a wrap spacing smoothly across tens of columns and you
> get a few degrees of bend — which is what a rolled scroll does, and is **locally
> indistinguishable from clean sheet**. Worse, on tightly wound segments the wrap gap
> (18–58 vx) is barely wider than one grid cell (20 vx), so a single-wrap switch is a
> one-to-three-cell displacement **sitting inside the clean noise floor**. Gross
> excursions are caught; **a minimal one-wrap switch on a tight winding is not, and no
> geometry-only test can separate it from bending.***

⭐ Et son seuil est **mesuré, pas choisi** : sur 14 segments propres la dérive de pointe
va de **0,46 à 2,00 cellules** et ne croît **pas** avec la fenêtre (5 à 150 colonnes),
tandis que le pire segment abîmé atteint **10,7**. D'où une barre plate à 4 cellules —
et l'auteur explique pourquoi un seuil en *ratio* aurait dû être réglé par fenêtre.

> ⚠⚠ **C'est exactement l'axe que notre instrument de profondeur (`12`) ne prend pas.**
> `00` §9.3 dit déjà que les six vérificateurs recensés *« travaillent tous sur la
> géométrie du maillage »* et que le nôtre *« lit le volume de surface lui-même »*. Ce
> document ajoute la pièce qui manquait : **un auteur indépendant, qui a construit le
> meilleur détecteur géométrique disponible, écrit qu'aucun test géométrique ne peut
> trancher le cas serré.** Notre axe n'est pas une préférence, c'est le complément
> nommé par celui qui a épuisé l'autre.

### ⚠ Et la limite symétrique, qui nous concerne autant

Le diagnostic stratifié de `villa#191` mesure, sur **200 points de vérité en région
comprimée**, que **78 %** montrent **un pic unique large couvrant deux feuilles** au lieu
de deux pics séparés — et seulement **0,5 %** sont deux pics résolus qu'un séparateur
pourrait scinder.

**En zone comprimée, l'information n'est pas dans le CT.** Un instrument qui lit le
volume y sera aveugle **par construction, pas par défaut de méthode** — et c'est
précisément là que les traces fautent. À écrire dans le domaine de définition de `12`
avant toute publication.

## 5. Deux soumissions refusées, et ce qu'elles enseignent sur la FORME

| PR | quoi | issue |
|---|---|---|
| **#1013 `plumbline`** | « trace-quality checker » dérivé de la **prédiction d'encre** — signal **indirect**, tableau de bord HTML, 115 tests | ❌ ouverte 2026-06-04, fermée 2026-08-04. *« In this current state I don't think it is [helpful] »* |
| **#1293 `ScrollAnchor`** | remonte des discontinuités « **explicitement pas** comme des sauts confirmés » | ❌ non fusionnée |
| **#1303 `vc_tifxyz_selfcross`** | question **géométrique sans seuil**, réponse binaire, exit 3 | ✅ **fusionnée en 24 heures** |

> ⭐ **La leçon est nette** : le signal *indirect* et le signal *sans engagement* ont été
> refusés ; la question géométrique à laquelle la géométrie répond par oui ou non a été
> prise immédiatement. Un outil qui rend des « candidats » demande à quelqu'un d'autre de
> faire le travail de décider.

## 6. Ce qui reste libre — et où notre travail vaut

- **le saut de spire sans vérité terrain, dans le cas serré** : la seule métrique
  officielle (`winding_error_fraction`) exige une annotation manuelle ; le meilleur
  détecteur géométrique déclare le cas serré hors de portée de toute géométrie ;
- **un score de segment agrégé et comparable** : rien n'existe. `spiralcheck` score au
  niveau du **rouleau entier**, pas du segment ;
- ⚠ **et un trou dans la littérature, mesuré au §2 de [`27`](27_ce_que_la_litterature_dit.md)** :
  les deux métriques qui portent l'argument théorique du spiral fitting — WJF et MRWD —
  **ne sont pas comparables** à son concurrent, parce qu'elles exigent la spirale
  canonique. **Personne n'a jamais comparé le taux de saut de spire de deux méthodes de
  traçage.**

## 7. Trois conventions à reprendre plutôt qu'à réinventer

1. **Écrire les sites de défaut en *point collection* JSON** (`PointCollections::saveToJSON`),
   rechargeable dans VC3D. C'est ce que fait `vc_tifxyz_selfcross`, et c'est ce qui rend
   un rapport actionnable au lieu d'être un chiffre.
2. **Un code de sortie distinct** pour « défaut trouvé » (3) et « erreur » (1).
   `tracecheck` le fait déjà ; le garder.
3. ⭐⭐ **Le test de mutation**, emprunté à `tifxyz-surgeon/tests/test_mutation.py`, et sa
   justification vaut d'être citée entière :

   > *« Injection testing catches a detector that is **blind**. It does not catch a
   > detector that is **absent**, because a suite that never asserts on a detector's
   > output cannot tell the difference between “found nothing, correctly” and “was never
   > consulted”. »*

   Son auteur a découvert qu'il pouvait **supprimer trois de ses quatre détecteurs sans
   qu'aucun test ne le remarque**. C'est notre règle « une vérification incapable
   d'échouer » poussée d'un cran : ne pas seulement sonder qu'un contrôle *peut* échouer,
   mais remplacer chaque détecteur par un bouchon et **exiger le rouge**.

   ✅ **Fait le jour même** : `tracecheck/mutation.py`, batterie de `tools/temoins.sh`.
   Il remplace tour à tour sept fonctions porteuses par un bouchon **dégénéré** — pas
   cassé : lever une exception ferait rougir la suite pour la mauvaise raison, on veut
   prouver qu'une réponse *neutre et plausible* est détectée — et exige le rouge.

   **Résultat : les sept portent du poids.** `judge`, `planarity_map`, `_neighbourhood`,
   `lit_voxel`, `decode`, `chunk_key`, `find_surface_volume` — débrancher n'importe
   lequel fait tomber `selftest.py`. Là où l'auteur de `tifxyz-surgeon` a découvert que
   **trois de ses quatre détecteurs** pouvaient disparaître sans qu'un test le remarque.

   > ⚠ Piège payé en l'écrivant : le python système de cette machine **n'a pas numpy**,
   > et `temoins.sh` lance ses batteries par `uv run python` **depuis `experiments/`**.
   > Un script qui suppose son propre interpréteur annonçait « la suite de référence est
   > déjà rouge » sur une suite parfaitement verte — le pire des diagnostics : faux, et
   > confiant. Le script cherche donc un interpréteur qui a numpy, et le **dit**.

## 8. Ce que je n'ai pas vérifié

- Les chiffres de corpus des dépôts communautaires (284 traces, 157 fenêtres, 42
  suspects…) sont des **affirmations de leurs auteurs**, avec méthode publique, non
  reproduites ici.
- Le code de la métrique Kaggle « topometrics » est hébergé sur Kaggle et n'a pas été lu ;
  la formule `0,30·TopoScore + 0,35·SurfaceDice + 0,35·VOI` vient d'un commentaire d'issue.
- Les fils Discord où vivent plusieurs décisions ne sont pas publics.
- ⚠ La couverture des **branches** de forks est partielle : la branche par défaut des 133
  forks de `villa` a été comparée, mais les branches hors-amont de 19 forks seulement.
