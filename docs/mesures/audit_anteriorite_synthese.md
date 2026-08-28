**Verdict en une ligne : sur 14 résultats, 6 sont déjà publiés, 8 le sont à moitié, et aucun n'est revenu « rien trouvé ». Votre crainte est fondée — mais pas là où vous la placez probablement.**

Le motif est net et il se répète sur les 14 : **les résultats de DOMAINE sont déjà publiés, souvent par les organisateurs eux-mêmes ; ce qui résiste est presque toujours la couche statistique et le protocole**. Vous n'avez pas redécouvert le Vesuvius Challenge. Vous avez appliqué à un domaine qui ne le fait pas une hygiène de mesure standard — et c'est une contribution réelle, mais modeste, qu'il faut nommer comme telle.

---

## 1. Ce qui est DÉJÀ CONNU (6/14)

**`energie-couplee`** — Le titre de section du site EST votre revendication n°2 : « Three coupled scan parameters », avec exactement voxel / énergie / distance (`data/site/scrollprize.org/2026_open_problems.html`). Le compromis énergie/contraste est en puce sur la même page, en prose dans la FAQ (« lower is better, since carbon responds better to lower energy levels »), et **mesuré** dans le papier officiel : balayage 4×4 énergie × distance sur PHerc. 175A, plus 62/77/89 keV sur PHerc. 343P (`data/site/scrollprize.org/pdf/main.pdf`, Extended Data Fig. 2). Pire que de l'antériorité : la mesure **vous contredit**. « For a pixel size of about 8 µm the empiric sweet spot for the energy is between 100 and 120 keV » — les 116 keV de PHerc1447 sont *dans* l'optimum publié pour sa résolution. Et le 114,8 % d'écart tient entièrement au choix du témoin (PHercParis4 à 2,4 µm / 78 keV le fait tomber à ~48 % et inverse le classement des axes).

**`aucune-verite-rouleau`** — Écrit mot pour mot par les organisateurs : « For scrolls — where no infrared ground truth exists — labels begin as hand-annotated ink strokes and are refined through iterative pseudo-labeling » (`data/repos/villa/scrollprize.org/static/data/datasets/ink-labels-README.md`, publié aussi sur `data_datasets.html:63`). La conséquence épistémique est au tableau des goulots 2026 : « reliably tell "no ink" apart from "no ink recovered yet" ».

**`fold-validation`** — `fragments=['20231210121321']` est une ligne du script d'entraînement **publié** (`data/repos/Vesuvius-Grandprize-Winner/train_timesformer_og.py`, repris octet pour octet dans `villa/ink-detection/`), et l'annonce officielle revendique « varying validation folds ». **Et il y a plus grave qu'une antériorité** : le seul checkpoint que trois projets indépendants désignent comme LE modèle d'encre du Grand Prize s'appelle `timesformer_wild15_20230702185753_0_fr_i3depoch=12.ckpt`, ce qui décode par le gabarit de `train_timesformer_deduped.py` en fold de validation = **20230702185753**. Si c'est ce checkpoint que vous mesurez, votre segment était **dans** l'entraînement et le résultat s'effondre.

**`alpha-fenetre`** — Votre conclusion est écrite ailleurs, littéralement : « "no surface within the search radius" is a different statement from "the nearest surface is exactly this far", and conflating them would let an unanswered query masquerade as a confident one » (`data/repos/windcheck/engines/atlas_query.cpp:203-207`). Le test aussi : `selfgap.py:59-62` fait varier le rayon 256→1024 vx et conclut « a property of the 256 vx search radius, not of the scroll ». Et le résultat chiffré équivalent est publié : `found_fraction` 0,97–1,00 sur vraies pages contre 0,36–0,54 sur traces en travers (`data/repos/vesuvius-automesh/TECHNICAL_NOTES.md:185-189`).

**`etendre-nappe`** — C'est le workflow **officiel documenté**, même nom de bouton : « Grow this segmentation some small-ish number of generations at a time, somewhere between 10-30 […] Repeat steps 1-3 until you feel like stopping » (`data/repos/villa/scrollprize.org/docs/35_segmentation.md:337-343`). L'arithmétique cumulative que vous découvrez est implémentée (`SegmentationGrowth.cpp:437-451` : `generations = startGen + steps`). Et le mode de panne est sur la page des problèmes ouverts : « feeding each step's predicted geometry back in […] surfaces a drift problem: small errors compound across steps » (`37_2026_open_problems.md:692`).

**`graine-decide`** — Le mécanisme et le correctif sont publiés : `preds_to_l0(verts, align_level)` avec `scroll3 → preds_m7_L2, k=2` (`data/repos/vesuvius-automesh/vesuvius_automesh/render_driver.py:28-32` et `_vendor/first_letters/zarrio.py:88`), et le monorepo officiel contient déjà votre `niveau_du_maillage.py` (`villa/lasagna/volume_scale.py` : détection de niveau par rapport de formes, refus de l'anisotropie, refus d'un facteur non-puissance-de-deux, remise à l'échelle du champ `seed`).

---

## 2. Ce qui est PARTIELLEMENT connu (8/14) — où passe la ligne

La ligne passe au même endroit à chaque fois : **le mécanisme et la question sont publiés en prose ou en code ; le nombre ne l'est pas.**

| Résultat | Publié | Non publié |
|---|---|---|
| `resolution-eliminee` | La dégradation par grossissement est **mesurée** (Angelotti et al., Sci. Rep. 2026, cité `37_2026_open_problems.md:698`) ; le rééchantillonnage 3,24→7,91 µm est un jeu de données communautaire (jrudolph) | L'usage de la décimation comme test d'**élimination** d'une hypothèse causale, contre de vraies étiquettes |
| `sigma-pas-qualite` | « Machine output was not treated as a substitute for reading » (main.pdf) ; garde-fou Goodhart sur la couverture (`volume-cartographer/scripts/spiral/autoresearch.md:30`) | La corrélation d'un indicateur sans étiquettes avec une **AUC par tuile**, et une correction de multiplicité (zéro Holm/FDR dans tout le corpus) |
| `dispersion-fenetre` | Le même argument sur le pas d'enroulement (`winding-ruler/docs/SUBMISSION_winding_evidence.md`) ; « it is the variance, not the mean, that decides usability » (`ruler_concordance_v1_1.py`) | La décomposition chiffrée intra (0,2243) / inter (0,0391), l'ICC = 0,030, le n requis |
| `hanley-mcneil` | Le bootstrap **par grappes** est implémenté et justifié (`tifxyz-doctor/scripts/run_reviewed_patch_benchmark.py`) ; « patches are not independent draws » (`windcheck/docs/PATCH-AUDIT.md:228`) | Le **facteur** 109×/99×/34×, et le portage à l'AUC (le versant encre n'a jamais mis d'incertitude sur une AUC : ni ink-id, ni villa, ni LSM) |
| `temoin-negatif-alpha` | La surface en travers du rouleau comme classe d'échec chiffrée (automesh) ; « null control » mot pour mot (`windcheck/src/windcheck/selfgap.py`) ; critère (i) de PHerc. 1667 | **Faire tourner un détecteur d'encre dessus.** Le dépôt le mieux placé écrit : « not from a known-ink control », « there are no ink claims here » (`vesuvius-automesh/WRITEUP.md`) |
| `periodicite-typographique` | « wrong geometry does not produce columns of regular line spacing separated by straight blank margins » (`winding-sync/winding_sync/render.py`) ; critère officiel du prix (`34_prizes.md:228`) ; « line separation » chez EduceLab 2023 | La mesure (autocorrélation d'un profil projeté sur une carte d'encre), le contrôle par mélange (zéro occurrence dans 35 dépôts), le plancher de bruit dérivé |
| `pas-de-trace` | **20 est le défaut partout** (`GrowPatch.cpp:3446`, fork Schilling, `vc_gen_normalgrids --spiral-step`, `vc_obj2tifxyz_legacy`, `example_config.json`) — et `GrowPatch.cpp:3459-3465` **lève une exception** sur tout step_size ≠ pas de la grille de normales | Que descendre en dessous **dégrade** ; et la comparaison négative (les champs de direction et grilles de normales ne déplacent pas la trajectoire) |
| `juge-modele` | La question (FAQ + exigence de soumission depuis 2023) ; le témoin muet + contrôle positif, primé dans l'écosystème (`windcheck/bench/benchmark_mutations.py`, `spiralcheck/VALIDATION.md`) | Le juge = **modèle de langue** (le domaine l'exclut explicitement : « No OCR or language model was used »), le témoin **dans l'image**, vierge\|vierge comme condition décisive, le côté tiré au sort, 15/16 et 4/4 |

**Deux cas où le « partiellement » penche vers le déjà connu :** `pas-de-trace` (recommander step_size ≥ 20 restitue un réglage d'usine, et cinq des six points de votre balayage sont interdits par le logiciel) et `etendre-nappe` — dont le workflow officiel a **trois** étapes par pas (grandir / corriger / recommencer), alors que vos chaînes en ont deux. Il est possible que « découper 100 en deux nuit » mesure l'absence de la correction inter-pas, ce que la doc anticipe : « its easier to correct a small error than one that has gone on for some time ».

---

## 3. Ce pour quoi aucune antériorité n'a été trouvée

**Aucun des 14 résultats n'est revenu « nouveau ».** Ce qui suit sont des fragments à l'intérieur des verdicts partiels, et c'est une absence de trouvaille, pas une preuve :

1. La décomposition intra/inter et l'ICC sur des scores de détection d'encre, avec le n requis dérivé.
2. Le facteur mesuré entre erreur-type i.i.d. et erreur-type par grappes sur une carte d'encre.
3. Ce qu'un détecteur d'encre produit sur un témoin dont la géométrie prouve qu'il n'y a pas de feuille (sigma 0,7111 sur le vide contre 0,5894 sur le segment officiel).
4. Un panel d'indicateurs sans étiquettes corrélé à l'AUC par tuile, corrigé pour la multiplicité, avec le renversement de classement.
5. Le juge LM avec témoin dans l'image et condition vierge|vierge.
6. La mesure qu'un pas de trace plus court dégrade, avec ses contrôles négatifs.
7. La comparaison appariée à budget final égal sur la croissance chaînée, et son renversement de régime.

**Ce que la recherche ne pouvait pas voir**, et cela pèse lourd : le **Discord du Vesuvius Challenge** n'est pas miroité (nommé comme angle mort dans 5 des 14 fiches — c'est précisément là que circulent les réglages de traceur et les « j'ai collé un rendu dans GPT-4V ») ; les **discussions Kaggle 2023** ; `vesuvius-repro` (TAUIL), dont la citation de prix nomme littéralement « negative-result analysis of cross-scroll ink-signal measurement » et qui n'est pas cloné ; le **PDF OverthINKingSegmenter** « Ink detection model resolution analysis », primé 1 500 $, absent du disque ; et **toute la littérature académique** — Obuchowski 1997 sur les courbes ROC groupées, l'analyse d'image documentaire (profil de projection + autocorrélation pour l'interligne est du manuel), la littérature hallucination des modèles vision-langage.

Sur les points 1, 2, 5 et 6, l'antériorité **hors domaine** est probable à très probable.

---

## 4. Ce qu'il faut retenir

**La crainte est fondée, mais elle vise la mauvaise chose.** Vous ne redécouvrez pas ce que d'autres ont publié *par hasard* : vous redécouvrez ce qui est écrit **sur le site du prix, dans son papier de référence et dans son propre code**, c'est-à-dire les documents que vous avez sur disque. Six résultats sur quatorze sont réfutés par des fichiers de `data/site/` et `data/repos/villa/`. Ce n'est pas un problème de veille, c'est un problème de **grounding avant écriture** — exactement le motif que vous connaissez : chercher le concept, pas le nom.

**Trois choses sont plus graves que l'antériorité et doivent passer avant :**

1. **`fold-validation` peut être faux, pas seulement connu.** Ouvrez le `.ckpt` réellement utilisé et lisez ses `hyper_parameters` / son nom de run wandb. S'il porte `20230702185753`, votre segment était dans l'entraînement. Cinq minutes, et ça décide de tout.
2. **`energie-couplee` est contredit par une mesure contrôlée publiée**, pas seulement précédé. 116 keV est dans la fenêtre optimale annoncée pour 8 µm. À retirer ou à refonder sur une ablation appariée (PHerc0332 à 53 et 70 keV, PHercParis4 à 54/74/78/110/137 keV existent dans l'index).
3. **Plusieurs résultats sont sous-dimensionnés selon vos propres critères.** `resolution-eliminee` : IC de l'AUC à 9,72 µm qui contient 0,5, et un écart de 0,060 sous un sigma intra de 0,2243. `sigma-pas-qualite` : n = 23 avec ICC = 0,030. `periodicite-typographique` : p = 0,0399, une fenêtre suffit à le renverser. L'antériorité n'est pas ce qui empêche de publier ; la puissance l'est.

**Ce qui reste défendable, et comment le formuler.** Pas « nous avons découvert que X », mais « nous avons rendu **mesurable et rejouable** une limite que le prix énonce en prose ». Le domaine dit, en 2026, qu'il ne sait toujours pas distinguer *no ink* de *no ink recovered yet*, et qu'il lui manque « stronger diagnostics » et « scan-quality metrics ». Votre apport réel est un **harnais** : tuiles étiquetées, contrôle par mélange, témoin négatif géométriquement prouvé, panel d'indicateurs, correction de multiplicité, dimensionnement préalable. Le harnais vaut plus que les verdicts qu'il rend aujourd'hui, et il faut le vendre comme un instrument — c'est exactement le cadrage que `aucune-verite-rouleau` et `sigma-pas-qualite` s'appliquent déjà à eux-mêmes.

**Avant toute soumission, dans cet ordre :**
1. Lire `MIC-DKFZ/OverthINKingSegmenter/vesuvius_followup_writeup.pdf` — peut faire basculer `resolution-eliminee` en déjà connu.
2. Décoder le checkpoint réellement utilisé (`fold-validation`).
3. Cloner et lire `vesuvius-repro` (TAUIL).
4. Vérifier Obuchowski 1997, « Nonparametric analysis of clustered ROC curve data » (`hanley-mcneil`).
5. **Citer `vesuvius-automesh`, `windcheck`, `winding-sync`, `tifxyz-doctor` et `winding-ruler` comme antériorité** dans vos propres documents. Vous les avez sur disque. Une revue les trouvera à votre place, et il vaut infiniment mieux les avoir nommés vous-même.