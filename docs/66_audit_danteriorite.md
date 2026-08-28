# 66 — Ce qui était déjà publié, et pourquoi on ne l'avait pas vu

> ⚠⚠⚠ **Sur 14 résultats principaux, 6 sont déjà publiés, 8 le sont à moitié, et AUCUN n'est
> revenu « rien trouvé ».** Audit adversarial du 2026-08-29 : un chercheur par résultat, cadré
> pour **réfuter** la nouveauté, puis deux sceptiques sur chaque résultat encore dit nouveau.
> Quinze agents, sur le miroir du site et les 35 dépôts clonés — **tout était sur le disque**.

⭐ Le motif est net et il se répète sur les quatorze : **les résultats de DOMAINE sont déjà
publiés, souvent par les organisateurs eux-mêmes ; ce qui résiste est la couche statistique et
le protocole.** Ce dépôt n'a pas redécouvert le Vesuvius Challenge — il a appliqué à un domaine
qui ne le fait pas une hygiène de mesure standard. C'est une contribution réelle et modeste,
et il faut la nommer ainsi.

## 1. ⚠⚠ Ce n'est pas un problème de veille, c'est un problème de grounding

Six résultats sur quatorze sont réfutés par des fichiers de `data/site/` et
`data/repos/villa/` — c'est-à-dire par le **miroir du site du prix** et par son **monorepo
officiel**, tous deux clonés ici depuis le début.

⚠ La règle que ce dépôt s'applique déjà au code — *chercher le CONCEPT, pas le nom, et
énumérer ce qui existe avant de construire* — n'avait jamais été appliquée à la
**bibliographie**. C'est la même faute, sur un autre matériau.

## 2. Déjà connu (6 / 14)

| résultat | où c'est publié |
|---|---|
| **l'énergie du faisceau** | `2026_open_problems.html` : « **Three coupled scan parameters** », mêmes trois paramètres. Et **mesuré** dans le papier officiel (`pdf/main.pdf`, Angelotti et al., Extended Data Fig. 2) : balayage 4×4 énergie × distance |
| **aucune vérité terrain sur rouleau** | `villa/scrollprize.org/static/data/datasets/ink-labels-README.md` : « *For scrolls — **where no infrared ground truth exists*** » ; et le goulot 2026 « *reliably tell "no ink" apart from "no ink recovered yet"* » |
| **le fold de validation du GP** | `fragments=['20231210121321']` est une ligne du script d'entraînement **publié**, repris octet pour octet dans `villa/ink-detection/` |
| **α suit la fenêtre** | `windcheck/engines/atlas_query.cpp` : « *"no surface within the search radius" is a different statement from "the nearest surface is exactly this far"* » ; et `selfgap.py` fait varier le rayon 256→1024 |
| **étendre une nappe** | workflow **officiel**, même geste : « *Grow this segmentation some small-ish number of generations at a time, between 10-30 […] Repeat until you feel like stopping* » (`villa/…/35_segmentation.md`) |
| **la graine décide** | `vesuvius-automesh/render_driver.py` + `villa/lasagna/volume_scale.py`, qui contient **déjà** notre `niveau_du_maillage.py` |

## 3. ⚠⚠⚠ Deux choses PIRES qu'une antériorité

### Le fold de validation peut rendre le résultat FAUX, pas seulement connu

Le checkpoint que trois projets indépendants désignent comme *le* modèle d'encre du Grand Prize
s'appelle `timesformer_wild15_**20230702185753**_0_fr_i3depoch=12.ckpt` — donc fold de
validation = **20230702185753**, et non `20231210121321`.

⚠ **Et on ne peut pas trancher depuis ici** : notre copie est au format HuggingFace, et la
conversion a **effacé la provenance** — `model.safetensors` ne porte que `{'format': 'pt'}`,
aucun hyperparamètre, aucun nom de run. Vérifié le 2026-08-29.

⭐ Le test qui tranche ne demande pourtant aucune métadonnée : **mesurer le modèle sur les deux
segments**. Celui sur lequel il score le moins bien est celui qu'il n'a pas vu. C'est la
méthode de ce dépôt — mesurer plutôt que raisonner — appliquée à sa propre incertitude.

### L'énergie n'est pas seulement précédée, elle est CONTREDITE

Le papier officiel publie une ablation contrôlée, et son verdict va contre le nôtre :

> *« For a pixel size of about 8 µm the empiric sweet spot for the energy is between
> **100 and 120 keV** with propagation distances of about 3 m. »*

Les **116 keV** de `PHerc1447` sont donc **dans** la fenêtre optimale publiée pour sa
résolution, pas hors norme. Et sur un second balayage (62 / 77 / 89 keV) : *« the general
contrast drop is visible but **gentle**, however the **layer separability increases** »*.

⚠⚠ **Et notre chiffre tenait au choix du témoin.** Le seul volume de `PHercParis4` portant une
prédiction d'encre publiée est à **2,4 µm / 78 keV**, pas 7,91 µm / 54 keV. Contre ce
témoin-là, l'écart en énergie tombe à ~48 % et celui en résolution monte à ~260 % — **le
classement des axes s'inverse**. Le 114,8 % venait d'avoir pris pour référence un scan de 2023
que le pipeline actuel n'utilise plus.

ⓘ Un écart relatif large sur un paramètre ne prouve pas qu'il est le facteur limitant : il faut
la **sensibilité**, pas la distance. Et la sensibilité mesurée est faible sur l'axe énergie.

## 4. Partiellement connu (8 / 14) — et la ligne passe toujours au même endroit

**Le mécanisme et la question sont publiés en prose ou en code ; le nombre ne l'est pas.**

- `dispersion-fenetre` : le même argument existe sur le pas d'enroulement — *« it is the
  variance, not the mean, that decides usability »* (`winding-ruler`). Notre ICC de 0,030 et le
  n requis, non.
- `hanley-mcneil` : le bootstrap **par grappes** est implémenté et justifié
  (`tifxyz-doctor`), *« patches are not independent draws »* (`windcheck`). Le facteur
  **109×** et son portage à une AUC, non — **le versant encre n'a jamais mis d'incertitude sur
  une AUC**, ni `ink-id`, ni `villa`, ni `LSM`.
- `temoin-negatif-alpha` : la surface en travers comme classe d'échec est chiffrée
  (`vesuvius-automesh`), « null control » est écrit mot pour mot (`windcheck/selfgap.py`).
  **Faire tourner un détecteur d'encre dessus**, non — le dépôt le mieux placé écrit
  explicitement *« not from a known-ink control »*, *« there are no ink claims here »*.
- `juge-modele` : la question est dans la FAQ et dans les critères du prix depuis 2023, et le
  domaine **exclut** explicitement l'outil (*« No OCR or language model was used »*). Le juge
  modèle de langue avec **témoin dans l'image** et condition `vierge | vierge`, non.
- `pas-de-trace` : ⚠ **20 est le défaut partout**, et `GrowPatch.cpp` **lève une exception**
  sur tout `step_size` différent du pas de la grille de normales — donc cinq des six points de
  notre balayage sont interdits par le logiciel. Recommander `step_size ≥ 20` restitue un
  réglage d'usine.
- `etendre-nappe` : ⚠ le workflow officiel a **trois** étapes par pas (grandir / **corriger** /
  recommencer) quand nos chaînes en ont deux. « Découper 100 en deux nuit » mesure peut-être
  l'absence de la correction inter-pas — ce que la doc anticipe : *« it's easier to correct a
  small error than one that has gone on for some time »*.

## 5. ⚠ Ce que l'audit ne pouvait PAS voir

Une absence de trouvaille n'est pas une preuve de nouveauté, et cinq angles morts sont nommés :

1. le **Discord du Vesuvius Challenge**, non miroité — là où circulent les réglages de traceur
   et les « j'ai collé un rendu dans un modèle de vision » ;
2. les **discussions Kaggle 2023** ;
3. **`vesuvius-repro`** (TAUIL), non cloné, dont la citation de prix nomme littéralement
   « *negative-result analysis of cross-scroll ink-signal measurement* » ;
4. le PDF **OverthINKingSegmenter**, « *Ink detection model resolution analysis* », primé
   1 500 $, absent du disque ;
5. **toute la littérature académique** — Obuchowski 1997 sur les courbes ROC **groupées**,
   l'analyse d'image documentaire (profil de projection + autocorrélation pour l'interligne est
   du manuel), la littérature sur l'hallucination des modèles vision-langage.

⚠⚠ Sur quatre de nos sept fragments résistants, l'antériorité **hors domaine** est probable à
très probable.

## 6. ⭐ Ce qui reste défendable, et comment le formuler

Pas « nous avons découvert que X », mais **« nous avons rendu mesurable et rejouable une limite
que le prix énonce en prose »**. Le domaine écrit, en 2026, qu'il ne sait toujours pas
distinguer *no ink* de *no ink recovered yet*, et qu'il lui manque « stronger diagnostics » et
« scan-quality metrics ».

L'apport réel est un **harnais** : tuiles étiquetées, contrôle par mélange, témoin négatif
géométriquement prouvé, panel d'indicateurs sans étiquettes, correction de multiplicité,
dimensionnement **préalable**. Le harnais vaut plus que les verdicts qu'il rend aujourd'hui.

⚠⚠ Et une chose à faire avant tout le reste, qui n'est pas une question d'antériorité :
**citer `vesuvius-automesh`, `windcheck`, `winding-sync`, `tifxyz-doctor` et `winding-ruler`
comme antériorité dans nos propres documents.** Ils sont sur le disque. Une revue les trouvera
à notre place, et il vaut infiniment mieux les avoir nommés soi-même.

---

**Instrument** : workflow `audit-anteriorite` (15 agents, 14 résultats, 4,5 M jetons, 873 appels
d'outil, 14 min).
**Relevés** : [`audit_anteriorite.json`](mesures/audit_anteriorite.json) — les 14 verdicts avec
leurs preuves citées et leur fichier ; [`audit_anteriorite_synthese.md`](mesures/audit_anteriorite_synthese.md)
— la synthèse complète.
