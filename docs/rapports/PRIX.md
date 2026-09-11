# Les prix — les règles au 2026-09-11, et où le dépôt se tient

> **Source** : `https://scrollprize.org/prizes` et `https://scrollprize.org/winners`, téléchargées le
> **2026-09-11** et comparées au miroir du **2026-08-16**. Le miroir vit dans
> `data/site/scrollprize.org/` (gitignoré) — c'est pourquoi les règles qui décident sont citées
> **verbatim** ici : la source n'est pas dans l'arbre, ce document doit se tenir seul.
>
> ⚠ Ce document ne dit pas ce que le dépôt *devrait* viser. Il dit ce que chaque prix exige, ce que
> le dépôt possède qui y répond, et ce qui manque — pour que l'arbitrage soit fait sur des faits.

**Cagnotte ouverte : 2 140 000 $.** Échéance commune des trois prix de jalon : **25 juin 2027**.
Prix mensuels : prochaine échéance **30 septembre 2026**.

| prix | montant | ce qu'il paie | le dépôt a-t-il déjà soumis ? |
|---|---:|---|:--:|
| Grand Prize 2027 | 800 k$ + 100 + 50 + 50 | **un rouleau entier** déroulé et lisible, automatiquement | non |
| First Letters | 50 k$ × ≤ 10 rouleaux | **10 lettres dans 4 cm²** sur un rouleau où rien n'a été lu | non |
| Titre de PHerc. Paris 4 | 50 k$ | le **titre** de Scroll 1 | non |
| Progress Prizes | 20 k$/mois garanti + paliers 20k…250 | outils, résultats, **résultats négatifs**, audits | **non — jamais** |

---

## 0. Ce qui a changé entre le 16 août et le 11 septembre

Trois différences dans le texte des règles, dont **une qui touche le dépôt**.

**1. La règle de la fenêtre a été RÉÉCRITE.** Le 16 août :

> *« We strongly discourage submissions that use window sizes larger than 0.5x0.5 mm to generate
> images from machine learning models. If your submission uses larger window sizes, we may reject
> it and ask you to modify and resubmit. »*

Le 11 septembre, dans les trois prix de jalon :

> *« The larger your model's window size, the easier it is for it to invent plausible letterforms
> instead of recovering real ink. Large windows are fine, but you must demonstrate that the text is
> not hallucinated — for example by finding plausible text on held-out regions. »*

⚠ **Conséquence pour le dépôt.** La borne de **66 px** à 9,362 µm (`archive/68` §5, `archive/75` C1)
était dérivée de la règle du 16 août — *« pour conserver la propriété au pas du prix »*. Cette
propriété n'est plus une exigence de taille : c'est une exigence de **démonstration**. Ce que le
dépôt a construit pour la démontrer — le témoin négatif géométrique (`archive/46`), le juge à
condition vierge (`archive/09`), le nul verso (`archive/75` C2), la constante qui rendait le modèle
muet (`archive/60`) — répond **littéralement** à la nouvelle phrase. La contrainte s'est déplacée
vers l'endroit où le dépôt a le plus travaillé.

**2. First Letters passe de 13 à 23 rouleaux éligibles.** Dix de plus *« where no text has been read
yet »* : `PHerc0175A`, `0175B`, `0306B`, `0343`, `0483A`, `0483B`, `0490A`, `0490B`, `0846A`,
`0846B`. ⚠ Toute la cartographie du dépôt sur *« quel rouleau attaquer »* (`archive/16`, `33`, `81`,
`86`) porte sur les **13** du Grand Prize. Les dix nouveaux ne sont mesurés par rien.

**3. Cosmétique** : les liens Neuroglancer des volumes sont remplacés par leurs identifiants nus.

---

## 1. Grand Prize 2027 — 1 000 000 $

**Treize volumes éligibles**, identifiés par leur horodatage :
`PHerc0125 20250821151825` · `0191 20250821151635` · `0211 20250821151803` · `0257 20250821151750` ·
`0268 20251110183117` · `0358 20250821151737` · `0800 20250521135224` · `0813 20250821151723` ·
`0826 20250821151701` · `1203 20250820131727` · `1218 20250521120456` · `1447 20250521151220` ·
`1545 20250821151648`.

### Les conditions qui décident, verbatim

- *« **100% of the papyrus recto surface unrolled.** […] It is permissible to skip disconnected outer
  patches if they constitute less than 10% of the total scroll surface. »*
- *« Columns of text should be visible everywhere. Verify that at least **70%** of each counted
  column's preserved characters are legible. […] If text is not displayed, that area will be counted
  as "non legible" unless an explanation for the lack of ink is provided. »*
- *« The unrolling pipeline should be **fully automated**; up to **8 documented hours** of human
  annotation / input are tolerated. »*
- *« Pipeline should be **seamlessly integrated in the VC3D** software. »*
- *« Please create a **Docker image** that we can easily run to reproduce your work. »*
- *« At most **one mesh per full column** of text (plus its margins) will be accepted »* — nommés
  `column_01.tifxyz`, `column_02.tifxyz`… *« following the order of the windings »*.
- *« **Data derived from higher resolution scans of the submitted scroll volume cannot be used.** »*
- *« If any part of training or inference is stochastic, **random seeds must be fixed and
  reported**. »* et *« the full experiment-tracking run (e.g. Weights & Biases) must be shared »*.
- *« In case there are multiple teams that submit qualifying results, **the team that submitted
  first will win**. »*
- Repli : *« If no team meets the criteria by the deadline, we reserve the right to award the prizes
  to the teams that came closest. »*

### Où le dépôt se tient

| exigence | état | où c'est mesuré |
|---|---|---|
| dérouler automatiquement | ⛔ **portée maximale mesurée : 5 spires sur 6 offertes**, sur `PHerc0500P2` — qui n'est **pas** éligible | `archive/75` §A5, `82`, `83` |
| référent pour vérifier 31 spires | ⛔ **les treize éligibles publient ZÉRO rang de spire** ; les trois objets qui portent 31 spires consécutives (`PHercParis4` 120, `0172` 44, `0139` 37) sont **tous hors éligibilité** | `archive/81` |
| ce qui remplace l'humain (identité de feuille) | ⚠ un prédicat d'identité existe, adossé à un **référent** (`0139`) ; sans référent, deux produits d'orientation publiés sont trop grossiers (×7,8) | `archive/77`, `75` A2 bis/ter |
| ≤ 8 h d'humain | — jamais mesuré, faute de déroulement complet | — |
| VC3D, Docker, seeds | ⚠ `approval.tif` est écrit et **accepté par `villa`** ; rien d'autre n'est intégré | `archive/75` A3 |
| 70 % lisible par colonne | ⛔ au régime du prix (9,362 µm) le détecteur **ne sépare pas la feuille du vide** sur 3 segments sur 3 | `archive/75` C2 |

⚠ **Le fait le plus lourd est structurel, pas technique** : le dépôt a bâti son référent d'identité
sur des objets que le prix n'admet pas, et les objets que le prix admet n'ont pas de référent.
Toute méthode validée sur `0139` devra être **transportée** sur un des treize sans vérité de terrain
— ce que `archive/74` §4 nommait *« un transport non énoncé »*.

---

## 2. First Letters — 50 000 $ par rouleau, 500 000 $ au plus

> *« $50,000 to the first team that uncovers **10 letters within a single 4 cm² area** of that
> scroll — and open sources their methods and results (after winning the prize). »*
> *« The review bar is deliberately high — we'd rather be slow than wrong. »*

**Vingt-trois volumes éligibles** — les 13 du Grand Prize plus les dix nommés au §0.

### Les conditions qui décident, verbatim

- *« For software with a **human in the loop**, please provide written instructions and a video »*
  — l'humain est **permis** ici, contrairement au Grand Prize.
- *« Sometimes ink is visible directly in the flattened render, **with no model at all** […] If
  that's already enough legible letters, that by itself qualifies. »*
- *« **We don't yet know whether our existing ink models will work on these scrolls.** They might,
  or they might not — it may be necessary to train a scroll-specific model. »*
- *« Annotate the rows of text. Usually, letters […] run overwhelmingly parallel to the horizontal
  papyrus fibers — where possible, overlay your ink predictions on a **fiber-visible rendering**. »*
- même clause de non-hallucination qu'au §0, et *« Do not include overlap between training and
  prediction regions »*.

### Où le dépôt se tient

| ce qu'il faut | ce que le dépôt a | où |
|---|---|---|
| un rendu de 4 cm² sur un des 23 | **aucune tentative** | — |
| savoir si les modèles publiés lisent au régime du prix | ⭐ **mesuré, et la réponse est NON pour les modèles publiés** : accord plat à 9,362 µm là où il monte en production ; face et vide indiscernables (AUC 0,371–0,519) | `archive/75` C1, C2 |
| démontrer la non-hallucination | ⭐ le harnais complet : témoin négatif, juge à condition vierge, nul verso, contrôle par mélange à 0,500 | `archive/46`, `09`, `60`, `75` C2 |
| diagnostic du régime de scan | ⭐ le nombre de Fresnel ordonne les verdicts des auteurs ; les 13 sont à **53 %** du régime de production | `archive/68` §3 |
| où la vérité terrain existe pour ce régime | ⭐ **103 cases vides** sur 4 objets, dont 38 sur `0139` et 38 sur `0500P2` | `archive/68` §4 |
| quel rouleau | ⚠ la queue de `d′` ne sépare **rien** parmi les treize après Holm ; le critère de décision coûte 315× le budget | `archive/33`, `75` (combien de fenêtres) |

⚠ Ce que la mesure de `C2` dit à ce prix : *avec les modèles publiés*, aucun des treize n'a de
chance. Un First Letters demande donc soit un **modèle spécifique au rouleau** (ce que le site
anticipe), soit de l'encre **visible sans modèle**. Le dépôt n'a exploré ni l'un ni l'autre.

---

## 3. Le titre de PHerc. Paris 4 — 50 000 $

> *« Scroll 1 is one of our most-read scrolls […] yet its author and title remain unknown. **The
> expected title region has shown no detectable ink so far** — possibly a different ink, and the
> top rows are physically missing — so finding it may take better methods, higher resolution, or
> looking somewhere new. »*

Tous les volumes de Scroll 1 sont admis, **y compris les 2,4 µm** — c'est le seul prix où la haute
résolution est permise. *« You do not have to read the title yourself — you have to produce an image
of it that our team of papyrologists is able to read. »* Et : *« Submissions remain open until the
prize is won: if we discover months from now that your method was right all along, you will then
win. »*

### Où le dépôt se tient

Rien n'a visé le titre. Mais **tout le corpus de la campagne de déroulage géométrique est sur cet
objet** : 28 bandes humaines, 120 spires consécutives sans trou, l'axe courbe, la continuité des
transferts, le pas lu sur les transferts (`archive/84`–`93`). Et `PHercParis4` publie des fibres
**et** de l'`ink-3d` (`archive/75`, « où vit le champ de fibres »). C'est l'objet le plus instrumenté
du dépôt, et le prix qui le vise n'a jamais été regardé.

---

## 4. Progress Prizes — 20 000 $ garantis chaque mois, plus des paliers

> *« Best Submission of the Month: $20,000, guaranteed every month »* ; puis *« typically $20,000,
> $10,000, $5,000, $2,500, $1,000, $500 or $250 »*. Prochaine échéance : **30 septembre 2026**.

### Ce que le jury dit favoriser, verbatim

- *« Are released or open-sourced **early**. »*
- *« **Actually get used.** We'll look for signals from the community. »*
- *« Improve results quantitatively and/or qualitatively on real data. »*
- *« **Reveal insightful, actionable information.** If you are building analytic tools, show how
  they facilitated improvements […] for example by **detecting failure-cases of existing methods
  on real scroll data**. »*
- *« Are well documented. »*
- *« Any contribution that makes any of the Open Problems easier to address will be eligible. »*

### Ce que les lauréats montrent de ce qui se PAIE (page *winners*, 2026-09-11)

Les deux derniers mois, **64 500 $** sur **28 lauréats**. Ce qui a été payé dans la bande
250–2 500 $, c'est-à-dire la bande où le dépôt a de la matière :

| lauréat | montant | ce qui a été payé | ce que le dépôt a de comparable |
|---|---:|---|---|
| **windcheck** (J. Carreras, juillet) | 1 000 $ | détecter les auto-intersections des tifxyz | le dépôt l'a **reproduit** et audité (`archive/03`–`07`) |
| **TIFXYZ Doctor** (A. Cohen, juillet) | 1 000 $ | QA déterministe des grilles tifxyz | `src/depot/`, `tracecheck/` |
| **TAUIL** (juillet) | 1 000 $ | *« a **negative-result analysis** of cross-scroll ink-signal measurement »* | `archive/17`, `26`, `62`, `114` — quatre résultats négatifs propres |
| **scroll-data-audit** (M. Bulloni, juillet) | 1 000 $ | *« Defect-hunting across the open-data catalog »* | `ce_que_les_serveurs_publient`, `les_spires_consecutives_publiees` (`archive/81`) |
| Miller & Müller (août) | 1 000 $ | First Letters sur `0826` **de bout en bout, échecs et coûts publiés** | le dépôt n'a jamais publié une tentative |
| pscamillo (août) | 1 000 $ | combien de couches de profondeur le modèle 9 µm exige | `archive/75` C2 — la profondeur lue, mesurée, réfutée comme cause |
| D. Russo (août) | 1 000 $ | benchmark des 14 checkpoints 9 µm publiés | `archive/66` §3 : le fold du modèle GP est indécidable depuis les métadonnées |
| B. Hamm (août) | 1 000 $ | labels *« much closer to the true surface »* | `archive/95`, `97` : la surface humaine est à 20,8 µm de la matière, deux humains divergent d'une demi-feuille |
| **W. Stevens** (août) | **20 000 $** | *« detects when the 2D alignments of overlapping patches imply incompatible 3D locations, drops the offending patches, and joins the rest »* — 365 cm² sur `1667` | ⚠ **c'est la question du raccrochage de spire à spire**, la campagne `R4` entière — et Stevens n'est cité dans **aucun** doc du dépôt |

⚠ **Le motif est net : le jury paie des résultats négatifs, des audits de données et des outils de
QA à 1 000 $ pièce**, et le dépôt en a une dizaine qu'il n'a jamais soumis. Ce n'est pas le graal.
C'est de l'argent laissé sur la table chaque mois depuis août.

---

## 5. Ce que la page *Open Problems* (10 juillet 2026) dit, et que le dépôt a retrouvé seul

Inchangée depuis le 16 août à quatre URL près. Trois passages recoupent des mesures du dépôt :

1. **Appendice A, « Methods we tried »** — deux traceurs neuraux mis *« on hold »* pour la même
   raison : *« running either model over a multi-step rollout […] surfaces a **drift problem**: small
   errors compound across steps instead of staying bounded. […] a long, multi-step rollout is the
   regime real production use needs. »* ⭐ C'est **exactement** ce que `archive/75` §A5 a mesuré sur
   le raccrochage : un gain sur un pas, une perte sur une marche, 53 µm de dérive par tour. Le dépôt
   a redécouvert, par la mesure, la panne que l'équipe a rencontrée sur ses propres modèles.
2. **Tableau des goulots, ligne « Sheet switches »** : *« What would help: Stronger local continuity
   constraints and **conservative failure detection**. »* — le prédicat d'identité et le masque
   d'approbation de `archive/77`.
3. **Spiral fit** : *« **relative winding number annotations** seem to have a great impact on the
   spiral fit. Automating these procedures will boost scalability by a great extent! »* — les indices
   de spire et le champ d'enroulement de `archive/76`–`77`.

Et la phrase qui reste le graal, mot pour mot : *« **No method yet traces a complete, correct
surface through a scroll automatically** — and the labels used to train surface models are themselves
approximate. »*

---

## 6. Registre des changements de ce document

| date | ce qui a été fait |
|---|---|
| 2026-09-11 | première version, depuis les téléchargements du jour et le diff contre le 16 août |
