Verdict chiffré, d'abord : sur **98 outils distincts audités, 22 existaient déjà** sous une forme utilisable (22 %), **50 partiellement** (une brique publiée, un assemblage à nous), **27 n'ont aucun équivalent** dans les 13 Go des 35 dépôts clonés. Oui, du temps a été perdu. Non, ce n'est pas « beaucoup » au sens où vous le craignez, et la raison n'est pas rassurante : la duplication s'est concentrée sur la moitié la moins chère du travail.

---

## 1. Le décompte par famille

| famille | outils | existait | partiel | rien | temps perdu |
|---|---:|---:|---:|---:|---:|
| commun + tracecheck | 10 | 1 | 6 | 3 | 4 |
| nappe | 9 | 5 | 3 | 1 | 5 |
| graine | 13 | 1 | 9 | 3 | 1 |
| encre | 11 | 1 | 7 | 3 | 2 |
| volume | 7 | 2 | 4 | 1 | 1 |
| excision | 13 | 3 | 8 | 2 | 3 |
| outils | 14 | 6 | 6 | 2 | 6 |
| dépôt | 22 | 3 | 7 | 12 | 1 |
| **total** | **99** | **22** | **50** | **27** | **23** |

(99 verdicts pour 98 fichiers : `src/commun/trouver_graine.py` a été audité deux fois, par deux agents, avec le même verdict.)

## 2. Où le temps a réellement été perdu — 22 fichiers, nommés

Par ordre de coût décroissant, tel que je peux l'établir.

**Le plus cher n'est pas du code, c'est une campagne de mesure.** `carte_difficulte.sh` + `src/nappe/espacement_spires.py` : `winding-ruler/atlas/winding_atlas_v1.py` mesure l'écart entre spires depuis la même prédiction m7/th0.2, et `winding-ruler/results/atlas_collection_v2.csv` contient **les 14 rouleaux de notre tableau**, plus 22 autres, avec les tailles de voxel que notre docstring dit « pas devinables ». Il n'y avait rien à adapter : un fichier à lire. Pire, `atlas/build_atlas_v2.py` a mesuré que le niveau 2 fusionne les feuilles voisines (pas surestimé de 10,3 %, 36/36 négatif) et a tout re-couru au niveau 1. Notre outil tourne encore au niveau 2 par défaut.

**`src/encre/typographie.py` (1066 l.)** : `villa/volume-cartographer/scripts/spiral/get_ink_metrics.py`, dans le monorepo officiel, mesure l'interligne par fenêtres glissantes de **512 px, la même valeur que la nôtre**, avec le garde-fou anti-bruit sur la proéminence des pics, plus la détection de colonnes que nous n'avons pas.

**`src/volume/apparier_volumes.py` (371 l.)** : nous reconstruisons par regex sur les noms de dossiers un appariement que `metadata.min.json` **déclare** (la prédiction de surface est nichée sous son volume, porteur du `scan_id`), et que `vesuvius-catalog/src/vesuvius_catalog/catalog.py` expose en une ligne. Le cas PHerc0172 qui nous force à rendre `None` n'existe pas de ce côté.

**`src/excision/measure.py`** : `windcheck/bench/normal_profile.py` fait l'échantillonnage excisées-vs-témoins appariés, avec **la même justification écrite** du témoin de voisinage et du groupement par requête, et sur 53 points le long de la normale là où nous lisons un voxel. Il vit à l'intérieur du dépôt dont nous auditions les réparations. `windcheck/src/windcheck/excise.py:2060` asserte déjà nos deux préconditions d'identité.

**`src/commun/trouver_graine.py`** : le plafond d'occupation dont notre README dit « the fix that mattered was not the criterion but the occupancy ceiling » est un **argument par défaut** dans `vesuvius-automesh/vesuvius_automesh/select_regions.py:27` (`max_occ: float = 0.50`), et la formule `(λ₁−λ₂)/λ₁` est littéralement `khartes/st.py:119` (`linearity = (lu-lv)/lu`), disponible en 3D sur volume entier via `villa/.../structure_tensor/create_st.py --confidence-metric linearity`.

**Les six scripts de `src/outils/`** : `balayage_maxedge.sh` → `windcheck/engines/selfcross.cpp:37` pose la question et donne la mesure (37 vs 1848 voxels) ; `mosaique_rouleau.sh` → `villa/.../spiral/render_ink.py`, qui concatène la géométrie avant de rendre (donc géométriquement juste, contrairement à notre empilement de JPEG) ; `tracer_une_graine.sh` → `villa/.../evaluation/eval_surface_tracer.py`, le harnais officiel ; `fetch_layers.sh` → `VesuviusDataDownload/`, où le listage `rclone` dissout le piège de largeur de nom dont notre docstring est fière ; `apercu_surface.sh` → `write_qc` de `first_letters/qc.py`.

**Le reste** : `suivre_nappe.py` et `champ_correction.py` → `first_letters/recenter.py` (par point, donc plus fin que le nôtre) ; `carte_segments.py` → `vc_seg_add_overlap.cpp`, officiel, qui écrit un `overlapping.json` **publié sur l'open data** ; `distance_a_la_matiere.py` → `herculaneum-scroll-tools/ct_support/audit_ct_support.py` ; `gauchir_nappe.py` → `khartes/base_fragment.py:254` ; `lire_selfcross.py` → `windcheck/bench/quickstart_gate.py:131` ; `corpus_par_energie.py` → `vesuvius-catalog` ; `empreinte_surface.py` → `spiralcheck/src/spiralcheck/split.py:70` (`patch_content_hash`, deux lignes d'import) ; `pyramid.py` et `sensibilite_centre.py`, traités plus bas parce que leur problème dépasse le temps perdu.

## 3. Où un équivalent existe mais n'aurait rien fait gagner

Les 50 « partiels » ne sont pas du temps perdu, et pas par indulgence. Trois motifs reviennent.

**L'équivalent nous aurait égarés.** `tifxyz-doctor/src/tifxyz_doctor/audit.py::_nonlocal_proximity` fait notre `proximity.py`, dix jours plus tôt, mais divise par un espacement **global** : exactement la constante dont notre propre docstring dit qu'« une constante avait déjà produit une conclusion fausse ». Partir de là aurait voulu dire refaire le même correctif.

**Le remède diverge parce que le choix en amont diverge.** Toute la famille `src/depot/` : `windcheck` et `spiralcheck` résolvent « un chiffre publié doit égaler son record » par **génération** (`build_release_index.py` : « Nothing here is hand-entered » ; `benchmark_card.py` refuse d'imprimer une figure qu'il n'a pas établie). Nous avons 58 documents de prose française écrite à la main, donc nous **vérifions**. Nos outils sont le prix d'un choix, pas une réinvention. La vraie question n'est pas l'antériorité, c'est : fallait-il écrire la prose à la main ?

**La brique existe, la question n'est pas la même.** Le chien de garde d'`eval_surface_tracer.py` compare au temps écoulé des pairs, donc ne s'arme jamais sur un run isolé, là où `rendre_surveille.sh` lit `/proc/<pid>/io`. La boucle de correction existe dans VC3D (`grow_patch_point_corrections.md`), mais avec **un humain** qui annote les points ; les nôtres viennent d'un juge automatique. `first_letters/qc.py` juge un rendu par un ratio à seuil étalonné sur un rouleau de contrôle ; `test_convergence.py` lit une pente, sans seuil ni échelle, donc transportable.

## 4. Ce qui n'a aucun équivalent — 27 outils

**L'instrument central.** Aucun des 35 dépôts ne fait varier la fenêtre d'analyse pour lire la dépendance au paramètre comme signal. Le grep sur « peak at the edge | edge_pinned | pinned to the edge » rend **zéro**. Et le mode de panne visé est déclaré **ouvert par les organisateurs** : `data/site/scrollprize.org/2026_open_problems.html` — « Sheet switches […] Current approach: VC3D inspection and manual correction ». Le dépôt public le plus proche par le sujet s'en exclut par écrit (`tifxyz-surgeon/README.md:203` : « Nothing here reads the volume »).

**Toute la couche statistique.** Sur 13 Go : zéro `spearman`, zéro `fisher_exact`, zéro `bonferroni`, zéro `binomtest`, zéro test de permutation, zéro analyse de puissance, zéro `mannwhitneyu`. Les 15 usages de `scipy.stats` sont des noyaux gaussiens et une métrique de distance. `winding-ruler` publie des « +3-5 pp » sans importer `scipy.stats`.

**Le juge automatique en aveugle.** Aucun appel à une API de modèle dans les 35 dépôts. Le protocole de jugement publié est humain et **sans condition de contrôle** : nulle part une image vierge n'est présentée à un juge pour mesurer son taux de fabrication.

**L'étage polaire** (`fusions.py`, `fusion_scan.py`, `track_z.py`, 1097 lignes) : zéro dépliage polaire d'une coupe CT, zéro suivi de crêtes, zéro modèle nul spatial, zéro statistique de rectitude.

**Douze outils de `src/depot/`** : aucune analyse statique d'hygiène (`import ast` n'apparaît que dans 4 fichiers, tous pour du chargement de modèle), aucun garde contre le radotage, aucun réécriveur de citations de chemin, aucune comptabilité disque consciente des liens durs (`st_nlink` : zéro occurrence).

## 5. Le verdict sur la faute

**Oui, l'état des lieux initial était insuffisant, et c'est ma responsabilité.** Le fait accablant n'est pas que ces dépôts existent : c'est qu'ils étaient **déjà clonés sur ce disque** avant que la plupart de ces scripts soient écrits. Le coût n'était pas d'aller les chercher, il était de les ouvrir.

Le mode de défaillance est précis, et c'est ce qui le rend réparable : **un échec de vocabulaire, pas de recherche**. Aucun équivalent ne porte notre nom. « Écart entre spires » s'appelle *winding pitch*, « saut de spire » *sheet consistency* ou *winding jump fraction*, « champ de correction » *subvoxel re-centering*, « distance à la matière » *CT support*, « planéité » *linearity*. Un grep sur nos concepts français ne rend rien ; un grep sur leurs noms anglais rend tout. L'état des lieux qu'il fallait faire tient en une ligne par outil, avant d'ouvrir un éditeur.

Deuxième constat, moins confortable que le premier : **la posture méthodologique n'est pas distinctive**. `windcheck/bench/reconcile.py` décrit notre panne de chiffres publiés dans nos mots (« a number that is TRUE OF A SUBSET, narrated as true of the whole »), `spiralcheck/scripts/mutation_check.py` écrit « this is the test of the tests », `benchmark_accept.py:162` écrit « comparing a tool to itself is a check that cannot fail ». Trois concurrents indépendants tiennent la même discipline. Ce qui reste à nous est le **mesurande**, pas la méthode.

Combien ça coûte, honnêtement : 22 fichiers sur 98, dont six scripts shell courts et plusieurs primitives de quelques dizaines de lignes. Le gros du gaspillage est concentré sur deux blocs — la campagne d'écart entre spires (13 rouleaux streamés pour un résultat publié sur 36, avec un biais déjà corrigé ailleurs) et la moitié « interligne » de `typographie.py`. Je situe le total dans l'ordre de la semaine de travail net, sans pouvoir le serrer davantage depuis l'audit seul. Ce n'est pas rien. Ce n'est pas non plus le projet.

**Ce qui devrait vous inquiéter plus que la comptabilité**, et qui est actionnable tout de suite :

1. `build_atlas_v2.py` **contredit** la conclusion de `pyramid.py` (« le niveau 2 conserve 89 % des murs »), et `fusion_scan.py` bâtit tout son balayage du rouleau entier dessus. Entrées différentes (CT brut chez nous, prédictions chez eux), donc à trancher, mais à trancher.
2. `espacement_spires.py` tourne au niveau 2, donc son biais se propage dans `ecart_de_maillages.en_micrometres()` via `spire_um`.
3. `sensibilite_centre.py` existe en entier à cause d'une prémisse fausse : l'ombilic **est** publié pour le rouleau qu'il nomme (`spiral-fitting/scroll1_umbilicus.py` cite `dl.ash2txt.org/.../umbilici/umbilicus-scroll1a_zyx.txt`) ; notre vérification portait sur le bucket S3, pas sur `dl.ash2txt.org`.

**Limites de cet audit, à ne pas lisser.** Les agents ont grepé les 35 dépôts par concept et lu les touches plausibles ; ni `villa` (7,3 Go) ni `windcheck` (4,3 Go) n'ont été lus intégralement. Le compte de 22 est donc un **minorant**. Et les clones sont en profondeur 1 : les dates citées sont des dates de dernier commit, donc des majorants — pour `villa/.../create_st.py` en particulier, je ne peux pas établir depuis ce disque s'il nous précède.