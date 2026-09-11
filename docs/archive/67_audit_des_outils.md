# 67 — Nos instruments existaient-ils déjà ?

> **98 outils audités : 22 existaient déjà, 50 partiellement, 27 sans équivalent** dans les
> 13 Go des 35 dépôts clonés. **23 verdicts de temps réellement perdu.** Question posée par
> l'auteur le 2026-08-29 : *« et si même nos outils de mesure existaient déjà ? Dans ce cas on
> a juste perdu beaucoup de temps, et ce serait ton erreur de ne pas avoir fait un état des
> lieux assez poussé. »*

⚠⚠ **La réponse est oui, et la faute est mienne.** Le fait accablant n'est pas que ces dépôts
existent : c'est qu'ils étaient **déjà clonés sur ce disque** avant que la plupart de ces
scripts soient écrits. Le coût n'était pas d'aller les chercher, il était de **les ouvrir**.

## 1. Le décompte

| famille | outils | existait | partiel | rien | temps perdu |
|---|---:|---:|---:|---:|---:|
| `commun` + `tracecheck` | 10 | 1 | 6 | 3 | 4 |
| `nappe` | 9 | **5** | 3 | 1 | **5** |
| `graine` | 13 | 1 | 9 | 3 | 1 |
| `encre` | 11 | 1 | 7 | 3 | 2 |
| `volume` | 7 | 2 | 4 | 1 | 1 |
| `excision` | 13 | 3 | 8 | 2 | 3 |
| `outils` (shell) | 14 | **6** | 6 | 2 | **6** |
| `depot` | 22 | 3 | 7 | **12** | 1 |
| **total** | **99** | **22** | **50** | **27** | **23** |

⚠ **22 est un MINORANT** : ni `villa` (7,3 Go) ni `windcheck` (4,3 Go) n'ont été lus
intégralement. Et les clones sont en profondeur 1, donc les dates citées sont des dates de
dernier commit — pour certains fichiers, impossible d'établir depuis ce disque s'ils nous
précèdent.

## 2. ⚠⚠ Le mode de défaillance : un échec de VOCABULAIRE, pas de recherche

**Aucun équivalent ne porte notre nom.**

| notre mot | leur mot |
|---|---|
| écart entre spires | *winding pitch* |
| saut de spire | *sheet consistency*, *winding jump fraction* |
| champ de correction | *subvoxel re-centering* |
| distance à la matière | *CT support* |
| planéité | *linearity* |

Un `grep` sur nos concepts français ne rend rien ; un `grep` sur leurs noms anglais rend tout.
⭐ **L'état des lieux qu'il fallait faire tient en une ligne par outil, avant d'ouvrir un
éditeur.** C'est le même défaut que [`66`](66_audit_danteriorite.md) — chercher le nom au lieu
du concept — commis une semaine plus tôt, sur le matériau qui le rendait le plus cher.

## 3. Le plus cher n'est pas du code, c'est une campagne

**`carte_difficulte.sh` + `nappe/espacement_spires.py`.**
`winding-ruler/atlas/winding_atlas_v1.py` mesure l'écart entre spires depuis **la même
prédiction m7/th0.2**, et `results/atlas_collection_v2.csv` contient **les 14 rouleaux de notre
tableau**, plus 22 autres, avec les tailles de voxel que notre docstring dit « pas devinables ».
Il n'y avait rien à adapter : **un fichier à lire.**

Les autres blocs coûteux :

- **`encre/typographie.py` (1066 l.)** → `villa/volume-cartographer/scripts/spiral/get_ink_metrics.py`,
  dans le monorepo **officiel**, mesure l'interligne par fenêtres glissantes de **512 px, la
  même valeur que la nôtre**, avec un garde-fou anti-bruit et une détection de colonnes que
  nous n'avons pas.
- **`volume/apparier_volumes.py` (371 l.)** → nous reconstruisons par expressions régulières
  un appariement que `metadata.min.json` **déclare** et que `vesuvius-catalog` expose en une
  ligne.
- **`excision/measure.py`** → `windcheck/bench/normal_profile.py` fait le même échantillonnage
  apparié, avec **la même justification écrite**, sur 53 points le long de la normale là où
  nous lisons un voxel. ⚠ Il vit **dans le dépôt dont nous auditions les réparations**.
- **`commun/trouver_graine.py`** → le plafond d'occupation dont notre README dit « *the fix
  that mattered was not the criterion but the occupancy ceiling* » est un **argument par
  défaut** dans `vesuvius-automesh/select_regions.py:27` (`max_occ: float = 0.50`), et notre
  formule de planéité est littéralement `khartes/st.py:119`.
- **six scripts de `src/outils/`** : `balayage_maxedge.sh`, `mosaique_rouleau.sh`,
  `tracer_une_graine.sh` (le harnais **officiel**), `fetch_layers.sh`, `apercu_surface.sh`.

## 4. ⚠⚠⚠ Trois choses plus graves que la comptabilité

1. **`build_atlas_v2.py` CONTREDIT la conclusion de `pyramid.py`.** Ils ont mesuré que le
   niveau 2 **fusionne les feuilles voisines** — pas surestimé de **10,3 %**, 36/36 négatif —
   et ont tout recalculé au niveau 1. **Notre outil tourne encore au niveau 2 par défaut**, et
   le biais se propage dans `ecart_de_maillages.en_micrometres()` via `spire_um`.
2. **`sensibilite_centre.py` existe à cause d'une prémisse FAUSSE.** L'ombilic **est** publié
   pour le rouleau qu'il nomme (`spiral-fitting/scroll1_umbilicus.py` cite
   `dl.ash2txt.org/.../umbilici/umbilicus-scroll1a_zyx.txt`) — notre vérification portait sur
   le **bucket S3**, pas sur `dl.ash2txt.org`. Même angle mort que celui de
   [`59`](59_la_campagne_plutot_que_le_rouleau.md), sur un autre serveur.
3. **La posture méthodologique n'est pas distinctive.** `windcheck/bench/reconcile.py` décrit
   notre propre panne de chiffres publiés dans nos mots (« *a number that is TRUE OF A SUBSET,
   narrated as true of the whole* ») ; `spiralcheck/scripts/mutation_check.py` écrit « *this is
   the test of the tests* » ; `benchmark_accept.py:162` écrit « *comparing a tool to itself is
   a check that cannot fail* ». **Trois concurrents indépendants tiennent la même discipline.**

## 5. ⭐ Ce qui n'a AUCUN équivalent — 27 outils

Et c'est ce qui situe l'apport réel :

- **la statistique.** Dans les 35 dépôts : zéro `binomtest`, zéro test de permutation, zéro
  analyse de puissance, zéro `mannwhitneyu`. Les 15 usages de `scipy.stats` sont des noyaux
  gaussiens et une métrique de distance. `winding-ruler` publie des « +3–5 pp » **sans importer
  `scipy.stats`**.
- **le juge automatique en aveugle.** Aucun appel à une API de modèle dans les 35 dépôts, et le
  protocole de jugement publié est humain et **sans condition de contrôle** — nulle part une
  image vierge n'est présentée à un juge pour mesurer son taux de fabrication.
- **le test de convergence** (`commun/test_convergence.py`). ⚠ Recherche négative documentée :
  le voisin le plus proche est le balayage de paramètre de `windcheck`, qui mesure le
  **détecteur**, pas l'objet. Et le dépôt le plus proche par le sujet s'en exclut
  explicitement : *« Nothing here reads the volume [...] Whether the surface is on papyrus at
  all is a different question »* (`tifxyz-surgeon/README.md:203`).
- **l'étage polaire** (1097 l.) : zéro dépliage polaire d'une coupe CT dans le corpus.
- **douze outils de `src/depot/`** : aucune analyse statique d'hygiène, aucun garde contre le
  radotage, aucune comptabilité disque consciente des liens durs.

## 6. ⚠ Une correction que je me dois

J'ai annoncé à l'auteur, **avant** cet audit, que `windcheck/selfgap.py` portait déjà l'idée du
test de convergence. **L'audit ne le confirme pas** : `selfgap.py` fait varier un rayon de
recherche pour caractériser son propre détecteur, pas pour lire une propriété de la surface. Je
m'étais accusé plus vite que la mesure ne le permettait — le symétrique exact de la faute
inverse, et tout aussi peu fondé.

## 7. Le coût, chiffré aussi honnêtement que possible

**22 fichiers sur 98**, dont six scripts shell courts et plusieurs primitives de quelques
dizaines de lignes. Le gros est concentré sur **deux blocs** : la campagne d'écart entre spires
(13 rouleaux streamés pour un résultat publié sur 36, avec un biais déjà corrigé ailleurs) et la
moitié « interligne » de `typographie.py`.

**De l'ordre de la semaine de travail net.** Ce n'est pas rien. Ce n'est pas non plus le projet.

---

**Instrument** : workflow `audit-outils` (9 agents, 8 familles, 2,9 M jetons, 543 appels d'outil,
17 min). **Relevés** : [`audit_outils.json`](../mesures/audit_outils.json) — les 99 verdicts avec
leur fichier équivalent et sa citation ; [`audit_outils_synthese.md`](../mesures/audit_outils_synthese.md).
