# Audits d'antériorité des trois résultats de tête — 2026-09-03

> Trois agents adversariaux, un par résultat, cadrés pour RÉFUTER la nouveauté, sur le
> miroir du site (81 pages) et les 35 dépôts clonés (13 Go). Chaque preuve porte son
> `fichier:ligne` et sa citation verbatim. **Les trois rendent PARTIELLEMENT.**


---

# Audit d'antériorité — « Le traceur de référence est un tirage, pas une fonction »

Cible : `docs/article/article.typ` §5.1 (`<sec:draw>`). Audit mené à charge : le but était de
trouver que quelqu'un l'avait déjà publié.

---

## verdict

**PARTIELLEMENT**

Le découpage, en une phrase par étage :

| étage du résultat | statut |
|---|---|
| le *mécanisme* (RNG non semé + OpenMP dans le traceur) | **présent en clair dans le code**, jamais énoncé |
| le *fait* « un segmenteur de volume-cartographer n'est pas déterministe » | **DÉJÀ DOCUMENTÉ**, mot pour mot — mais sur un **autre** segmenteur, retiré depuis |
| le *fait* « la recherche du traceur est stochastique » | **déjà écrit** par un tiers (`windcheck`), qui retire son module au lieu de mesurer |
| une section « Determinism » en bonne et due forme | **existe dans villa** — pour le **vérificateur**, jamais pour le producteur |
| le *remède* (semer + un seul fil) | **à moitié publié**, et justifié par une raison qui n'est pas la bonne |
| la *méthode* (répliques d'un traceur VC, vérif. de déterminisme) | **déjà exécutée par un tiers**, mais dans les conditions qui suppriment l'effet |
| la *mesure* (78 exécutions, 5/13 bascules, 6,4 %) | **RIEN TROUVÉ** |
| « aucune répétition ni barre d'erreur dans la littérature primaire » | **VÉRIFIÉ, la critique tient** |

Ce n'est pas un DEJA_CONNU : personne n'a mesuré la variabilité du traceur. Ce n'est pas non plus
un RIEN_TROUVE : la phrase « **Cette non-reproductibilité n'est pas documentée** » est vraie pour
`vc_grow_seg_from_seed`, mais un lecteur informé peut opposer trois choses — un avertissement
explicite sur le segmenteur frère, une variable d'environnement de graine qui n'existe que parce
que le problème est connu, et une campagne de répliques tierce. **§5.1 doit se resserrer** (voir
« ce qui reste neuf », dernier point).

---

## preuves

### A. Le mécanisme est dans le code, et il est plus lourd que ce que §5.1 dit

**A1 — RNG C non reproductible, semé à l'horloge, sans échappatoire.**
`data/repos/villa/volume-cartographer/apps/src/vc_grow_seg_from_seed.cpp:357`

```
    srand(clock());
```

**A2 — RNG C++ par défaut non semé, dans le cœur du traceur.**
`data/repos/villa/volume-cartographer/core/src/GrowPatch.cpp:99-108`

```
std::mt19937& thread_rng()
{
    static thread_local std::mt19937 rng = [] {
        if (const auto seed = environment_seed()) {
            return std::mt19937(*seed);
        }
        return std::mt19937(std::random_device{}());
    }();
    return rng;
}
```

*En quoi ça précède* : le mécanisme que §5.1 postule est là, littéralement. Mais il **précise
aussi** le résultat : le défaut est `std::random_device{}()`, donc « unseeded » est exact **par
défaut** — il existe cependant un opt-in, ce que §5.1 ne dit pas (point D1).

**A3 — le tirage est consommé DANS une région OpenMP : semer ne suffit pas.**
`core/src/GrowPatch.cpp:4802` ouvre la région, `4859` y tire :

```
             #pragma omp parallel
```
```
                    cv::Vec3d init = trace_params.dpoints(best_l) + random_perturbation();
```

Même chose dans l'autre moitié du traceur — `core/src/GrowSurface.cpp:2736` ouvre `#pragma omp
parallel`, et `2812` y appelle le `rand()` global :

```
                    : avg + cv::Vec2d((rand() % 1000)/500.0-1, (rand() % 1000)/500.0-1);
```

*En quoi ça compte* : les générateurs sont `thread_local` et reçoivent **la même** graine, mais
l'ordonnancement OpenMP décide **quel fil traite quel point**. Fixer la graine ne rétablit donc
pas le déterminisme — il faut **aussi** un seul fil. C'est exactement le remède que l'auteur
décrit ailleurs (`article.typ:1038`, « Pinning the generator's seed and forcing a single thread »),
et cette preuve **confirme** sa nécessité au lieu de l'affaiblir.

**A4 — le point de départ lui-même est tiré.** `core/src/GrowSurface.cpp:1811`

```
            seed_loc = {rand() % seed_points.rows, rand() % seed_points.cols };
```

---

### B. ⚠ Le fait EST documenté — sur le segmenteur d'à côté

**B1 — fork EduceLab.**
`data/repos/volume-cartographer-educelab/segmentation/include/vc/segmentation/OpticalFlowSegmentation.hpp:27-28`

```
 * @warning This algorithm is non-deterministic and yields slightly different
 * results each run.
```

**B2 — fork Schilling, même phrase, sur une ligne.**
`data/repos/volume-cartographer-schilling/segmentation/include/vc/segmentation/OpticalFlowSegmentation.hpp:31`

```
 * Warning: This Algorithm is not deterministic and yields slightly different results each run.
```

*En quoi ça précède* : c'est **le énoncé de §5.1**, publié dans un en-tête public de
volume-cartographer, signé Julian Schilliger, daté « May 2023 ». Un lecteur hostile citera cette
ligne contre la phrase « This is not documented ».

**B3 — ⚠ un tiers a écrit noir sur blanc que la recherche du traceur est STOCHASTIQUE.**
`data/repos/windcheck/docs/HISTORY.md:158-162`

```
Retired for two reasons. First, it is a proximity measurement and inherits every
objection in §3.1. Second, the comparison it rested on is not sound as stated:
the tracer's guard runs at growth time on a coarse grid via a stochastic search,
while the published tifxyz is post-optimisation and is rewritten with no
re-check, so "inside the pipeline's own rejection criterion" does not mean "the
pipeline would have rejected it".
```

*En quoi ça précède* : c'est l'énoncé communautaire le plus proche de §5.1 — le garde
anti-auto-intersection du traceur est qualifié de **recherche stochastique**, et l'auteur en tire
qu'on ne peut pas se fier à son verdict interne. Il **retire** son module plutôt que de mesurer.
Le caractère stochastique du traceur est donc **reconnu** dans l'écosystème, jamais quantifié.

**B4 — ⚠⚠ Et villa SAIT écrire une section « Determinism » — pour le vérificateur, jamais pour le
producteur.** `data/repos/villa/volume-cartographer/docs/tifxyz_selfcross.md:75-78`

```
## Determinism

Two runs on the same surface produce identical reports regardless of thread
count. A triangle pair can share several broad-phase cells; each pair is
```

*En quoi c'est la formulation la plus dure de l'omission* : la documentation officielle consacre
une **section entière et titrée** à prouver que « deux exécutions sur la **même surface** donnent
des rapports identiques **quel que soit le nombre de fils** » — exactement la propriété, exactement
l'argument sur les fils. Pour `vc_tifxyz_selfcross`, le **vérificateur**. La question symétrique —
deux traçages de la même graine donnent-ils la même surface ? — n'est posée nulle part.
*Corollaire utile à §5.1* : puisque le vérificateur est déterministe et invariant au nombre de
fils, une **bascule de verdict** ne peut pas venir de lui. Elle mesure bien un changement de
surface. Le choix de l'observable de §5.1 est donc adossé à une garantie publiée.
`data/repos/windcheck/docs/submission.md:307-309` le corrobore indépendamment : « **Determinism.**
Counts are invariant across thread counts and broad-phase cell sizes — 10,907 transverse and 1,989
grazing across nine configurations, pinned by two regression tests. »

*Pourquoi B1/B2 ne sont PAS le même résultat, et la distinction est vérifiée* :
- il porte sur `OpticalFlowSegmentation`, un segmenteur **différent** (propagation de chaîne par
  flot optique) de la croissance de patch `vc_grow_seg_from_seed`/`GrowPatch` ;
- `villa` **ne livre plus du tout** OpticalFlowSegmentation — `find . -iname "*OpticalFlow*"` sur
  `data/repos/villa/volume-cartographer` ne renvoie **rien**, et `grep -rn "yields slightly
  different"` sur tout `villa` renvoie **0 ligne** ;
- l'avertissement est **qualitatif** (« slightly different »), sans chiffre, sans répétition, sans
  taux ;
- et surtout : **dans le fork Schilling, les deux coexistent**. Le même dépôt, la même époque,
  documente OFS et laisse `apps/src/vc_grow_seg_from_seed.cpp:110` (`srand(clock());`) sans un mot
  — `grep -iE "determin|reproduc|warning" apps/src/vc_grow_seg_from_seed.cpp` n'y renvoie aucun
  avertissement. L'omission est donc **ciblée**, pas un style de maison.

---

### C. Le remède est à moitié publié — et justifié par la mauvaise raison

**C1 — la doc officielle recommande un seul fil, sans dire pourquoi.**
`data/site/scrollprize.org/segmentation.html:160`

```
<li><code>OMP Threads</code> : limits the amount of threads each process can use (recommend to set this to 1)</li>
```

**C2 — et le code donne la raison, qui est le débit, pas le déterminisme.**
`data/repos/villa/volume-cartographer/apps/src/vc_grow_seg_from_seed.cpp:576-583`

```
    else if (omp_get_max_threads() > 8) {
        // Tracing throughput peaks at a small thread count and degrades well
        // past it: measured on an i7-10700F (8C/16T) and a Ryzen 9 8940HX
        // (16C/32T), wall time per cm2 traced is lowest at 4 threads on both,
        // and running unbounded costs 2.2x and 3.5x respectively. The penalty
        // grows with core count, so the default is worst exactly on the large
        // machines used for batch tracing. VC3D already passes thread_limit=1
        // when it launches this tool (SegmentationCommandHandler.cpp).
```

*En quoi ça précède, et en quoi ça ne suffit pas* : la moitié « un seul fil » du remède est **la
recommandation officielle par défaut**, et VC3D l'applique déjà (`apps/VC3D/SegmentationCommandHandler.cpp:3313`,
`paramsJson.insert(QStringLiteral("thread_limit"), 1);`). Mais le seul motif écrit est le **temps
de calcul**. Aucune ligne du dépôt ne relie `thread_limit` à la reproductibilité.

**C3 — la graine existe et n'est documentée NULLE PART.**
`data/repos/villa/volume-cartographer/core/src/GrowPatch.cpp:83`

```
        const char* env = std::getenv("VC_GROWPATCH_RNG_SEED");
```

Recherche sur **tout le monorepo** (7,4 Go), `--include` md/txt/rst/cpp/hpp/py/sh/yml/yaml/json :
**une seule occurrence**, celle-ci — le site de lecture. Pas un README, pas une aide en ligne de
commande, pas un test.

*En quoi c'est une antériorité partielle* : cette variable n'existe que parce que quelqu'un, en
amont, a rencontré le problème. Le mécanisme est donc **connu des auteurs**. Mais il n'est ni
énoncé, ni mesuré, ni atteignable par un utilisateur qui lit la documentation.

**C4 — le projet sait documenter une RNG quand il le veut.** Deux outils frères le font :
`apps/src/vc_merge_patch.cpp:1289` — `"RANSAC RNG seed (0 = nondeterministic).")` — et
`apps/src/vc_merge_tifxyz.cpp:2373` — `"Per-edge RANSAC RNG seed (0 = nondeterministic).")`.
Et la charte du dépôt l'exige : `data/repos/villa/AGENTS.md:50`, « Avoid nondeterminism (race
conditions, unordered iteration affecting results, data-loader shuffles without fixed seeds,
etc.). » L'absence d'avertissement sur le traceur est donc une **omission**, pas une convention.

---

### D. ⚠ Quelqu'un a déjà fait des répliques sur un traceur VC — c'est l'antériorité la plus sérieuse

**D1 — le protocole, et sa conclusion opposée.**
`data/repos/tifxyz-doctor/verification/trace-impact/experiment-protocol.md:22`

```
Each variant was deterministic across three replicates. Baseline and
```

et `:53`

```
On the public PHerc1447 source selected below, three replicates per variant are
deterministic.
```

et `:214`

```
Also verify that each variant is deterministic across its three replicates.
```

**D2 — c'est même une assertion outillée, pas une remarque.**
`data/repos/tifxyz-doctor/verification/trace-impact/source-confirmation/vc3d_trace_evidence.py:1397`

```
        f"{variant}: three replicates are not deterministic: {keys}",
```

*En quoi ça précède* : un tiers du concours a exécuté **le même appel plusieurs fois, à paramètres
identiques, et comparé les sorties par hachage**, avec un contrôle automatisé qui échoue si les
répliques divergent. La *méthode* de §5.1 n'est donc pas neuve dans l'écosystème.

*Pourquoi ça ne réfute pas le résultat — quatre écarts, chacun vérifié dans les fichiers* :

1. **Ils ont épinglé les fils**, c'est-à-dire supprimé l'effet mesuré.
   `verification/trace-impact/run-manifest.json:50-51` (et identiquement pour les répliques 2 et 3,
   lignes 100-101, 150-151) :
   ```
          "OMP_NUM_THREADS": "1",
          "OMP_DYNAMIC": "FALSE",
   ```
   `verification/trace-impact/README.md:127` les appelle « `- Controls: OMP_NUM_THREADS=1, OMP_DYNAMIC=FALSE` »
   — **« controls », sans dire ce qu'ils contrôlent**. C'est la moitié du remède de l'auteur,
   appliquée sans que sa raison soit écrite (même motif qu'en C1/C2).
2. **Ce n'est pas le même binaire** : `run-manifest.json:48` lance
   `.../vc_grow_seg_from_segments`, pas `vc_grow_seg_from_seed`.
3. **Ce n'est pas une trace, c'est un pas** : `verification/trace-impact/resume-one-generation.json`
   fixe `"resume_growth": true`, `"disable_grid_expansion": true`, `"steps": 1`,
   `"global_steps_per_window": 1`. Une génération sur une reprise, là où la campagne de §5.1 fait
   croître 120 à 400 générations.
4. **Ce n'est pas un vrai volume** : la commande pointe sur `${TRACE_IMPACT_DIR}/fake-volume-pherc1447`.

Leur « deterministic » et le « 6,4 % de mauvais tirages » de §5.1 ne portent donc pas sur le même
objet, ni dans les mêmes conditions. Les deux peuvent être vrais ensemble — et c'est précisément
ce que la mesure de §5.1 explique.

---

### E. La critique de la littérature primaire tient — vérifiée deux fois, indépendamment

`data/site/scrollprize.org/pdf/main.pdf` (Angelotti et al., 46 p.). Les trois copies du corpus sont
le même fichier (md5 `6216b7b2c9d81b9379a9e4f5be78069e` pour `site/.../pdf/main.pdf`,
`repos/villa/scrollprize.org/static/pdf/main.pdf` et `site/.../assets/files/main-596e7e21…pdf`).

**E1 — la section « Statistics and reproducibility » ne contient aucune statistique.** p. 28, la
section entière :

> « **Statistics and reproducibility**
> The complete virtual unwrapping of PHerc. 1667 amounted to 31 wraps and 1231 cm2 of papyrus
> surface. The unwrapping was completed using the most efficient semi-automated segmentation
> tooling available at the time, a wrap by wrap copy tool combined with ~25 hours per wrap of
> manual annotation. »

Pas un n, pas un intervalle, pas une répétition. La rubrique imposée est remplie par une
description d'effort humain.

**E2 — les résultats sont des nombres nus.** p. 5 : « 22 columns or column-equivalents over
approximately **860 cm2** of preserved writing surface » ; « amounting to **33 cm2** ». Aucun `±`.
Recherche exhaustive du caractère `±` sur les 46 pages : **3 occurrences**, toutes des plages de
paramètres (`ShiftScaleRotate(rot ±360°, shift ±0.15, scale ±0.10, p=0.75)` p. 42 ; « surface
annotations placed **± 3 voxels** » p. 44 ; « humidity is controlled at 50% **+/-5%** » p. 16).
Aucun `±` sur un résultat. Seule occurrence de « bar » dans une légende : « Scale bars, 5 mm ».

**E3 — l'asymétrie est la preuve la plus nette.** Le papier sait fixer et déclarer le déterminisme
— pour le réseau de neurones seulement. p. 42 :

```
130697
cudnn.deterministic = True, cudnn.benchmark = False
```

(lignes du tableau « Random seed » et « Determinism »), et p. 41 « Train / val split 0.98 / 0.02
(seed = 42) ». Rien d'équivalent n'existe pour la géométrie. Le papier **ne nomme jamais** le
traceur : grep `vc_grow|GrowPatch|VC3D|volume.cartographer|Ceres` sur les 46 pages → 0 occurrence.

**E4 — le site non plus.** Sur les 81 pages HTML, la non-reproductibilité du traceur n'est
mentionnée nulle part. `data/site/scrollprize.org/2026_open_problems.html:157` **nomme** pourtant
le fichier (`vc_grow_seg_from_seed.cpp and GrowPatch.cpp`) et discute ses échecs (`:154`, « it
fails when the prediction topology does not match the real papyrus topology » ; `:158`, « if the
source mesh contains a local error, that error can propagate ») — toujours comme des échecs
**déterministes conditionnés par l'entrée**. Le tableau des sept goulots d'étranglement (`:321`)
ne mentionne pas le non-déterminisme. Le plus proche est `segmentation.html:230`, « The tracer will
run for an **indeterminate amount of time** […] This could be 10cm^2, or it could be 2800cm^2 -- it
completely depends on the surface prediction and patch quality » : « indeterminate » y qualifie la
**durée**, et la variabilité d'aire est imputée à l'**entrée**.

**E5 — la règle du concours ne couvre que le ML.** `data/site/scrollprize.org/prizes.html:66` :
« If any part of training or inference is stochastic, random seeds must be fixed and reported, for
both training and inference. » — « training or inference », jamais la géométrie.

**E6 — la littérature alternative ne fait pas mieux.** ThaumatoAnakalyptor
(`data/repos/ThaumatoAnakalyptor/documentation/ThaumatoAnakalyptor___Technical_Report_and_Roadmap.pdf`) :
0 occurrence de `non-determin|reproduc|error bar|standard deviation|repeated|each run|variance`.

---

### F. Ce que la communauté a fait qui ressemble, sans être ça

- **`windcheck`** compte des auto-intersections — la métrique de verdict de §5.1 — et se dit
  « replicated » : `data/repos/windcheck/README.md:363-368`, « a pre-registered, replicated
  measurement of transverse self-intersection in ScrollFiesta's tifxyz strip export […] 327
  clustered events on the canonical fixture, 273–278 on a held-out disjoint window ». La
  réplication est **entre fenêtres de données disjointes**, pas entre exécutions identiques, et
  porte sur une sortie ScrollFiesta.
- **`spiralcheck`** décrit windcheck comme « a label-free, **deterministic** self-intersection
  validator » et se positionne sur « runs and **run-to-run comparison** »
  (`data/repos/spiralcheck/README.md:238-240`) — mais « deterministic » y qualifie le **validateur**,
  et « run-to-run » compare des **ajustements différents**, pas des répétitions.
- **`vesuvius-automesh`** exécute le traceur en masse : `vesuvius_automesh/tracer_sweep.py:1`,
  « Seed-sweep orchestrator for vc_grow_seg_from_seed coverage growth ». Le balayage porte sur des
  **points de départ différents**, jamais sur la répétition d'un même appel.
- **La position officielle sur la stochasticité existe — pour un autre étage.**
  `data/repos/villa/volume-cartographer/scripts/spiral/autoresearch.md:52` : « **Stochasticity**:
  The code is sensitive to the random seed and CUDA non-determinism. […] a cheap robustness check
  is to run the same change under two seeds concurrently and see if the ink gain survives. » C'est
  le raisonnement de §5.1 (répéter pour distinguer un effet d'un tirage), écrit dans le monorepo
  officiel — mais sur le pipeline spiral/encre, pas sur le traceur géométrique.
- Même chose pour `scripts/spiral/tests/golden_run_compare.py:2-11` : « calibrating tolerance bands
  from repeated baseline runs […] asserted within a band derived from the observed run-to-run
  spread plus margin (GPU kernels are not deterministic enough for bit-exact assertions) ». Un
  harnais de répétition **existe** dans le dépôt officiel — pour l'entraînement, pas pour la trace.
- **⚠ Le seul endroit du corpus où quelqu'un lance `vc_grow_seg_from_seed` « deux fois pareil »
  et n'en tire aucune dispersion.** `data/repos/scrollreading/pipeline5/readme.md:32` : « I tried
  both **from the same seed point on the same hardware (single threaded, no GPU)**:
  vc_grow_seg_from_seed ran at an average speed of 50mm^2/s, simpaper9 ran at 33mm^2/s. » Une
  exécution de chaque, pour comparer un **débit** — et, là encore, en **mono-fil**.
- **`villa/.../scripts/evaluation/eval_surface_tracer.py`** exécute le traceur en masse
  (`:290`, « Running vc_grow_seg_from_seed seeding for {len(seed_points)} seed points ») et lit
  l'aire (`:344`, `area = float(meta.get("area_vx2", 0.0) or 0.0)`) — mais pour **trier et
  filtrer** les patches, jamais pour agréger une dispersion : aucune statistique dans les 721
  lignes du script.
- **Aucun test de déterminisme sur la croissance** : `grep -iE "determin|reproduc|VC_GROWPATCH|twice|repeat"`
  sur `core/test/test_growth_helpers.cpp` et `core/test/test_growth_config.cpp` → **0 ligne** ;
  `ls core/test/ | grep -iE "determin|repro|random|seed"` → **vide**.

---

## ce que j'ai cherché et où

**Code du traceur (question 1).** `data/repos/villa/volume-cartographer/`, motifs
`random_device|mt19937|rand\(\)|srand|default_random_engine|uniform_|shuffle|seed` sur
`apps/src/vc_grow_seg_from_seed.cpp` (1535 l.), `core/src/GrowPatch.cpp`, `core/src/GrowSurface.cpp`,
puis `core/src/` et `core/include/` entiers ; `pragma omp (parallel|for)` sur `core/src/` avec
localisation de la région englobante de chaque site de tirage (`awk` sur la dernière `pragma omp`
précédente) ; `VC_GROWPATCH_RNG_SEED` sur **tout** `data/repos/villa` (md/txt/rst/cpp/hpp/py/sh/yml/yaml/json) ;
`thread_limit` sur tout le sous-dépôt ; `docs/tracing.md` (28 l., lu en entier), `docs/`, `README.md`,
`AGENTS.md` ; `core/test/` (liste complète + les deux tests de croissance).
Forks : `volume-cartographer-educelab` et `volume-cartographer-schilling`, mêmes motifs.

**35 dépôts (question 2).** Balayage `data/repos/` sur
`non.?determinis|not deterministic|run.?to.?run (variab|varian|differ)|same (parameters|inputs|seed).{0,40}(different|vary|varies)|different results each|varies between runs`
(md/txt/py/cpp/hpp/json), puis `vc_grow_seg_from_seed` sur md/py/sh hors `villa` pour trouver les
appelants tiers. Lecture ciblée de `tifxyz-doctor/verification/trace-impact/` (protocole, README,
`run-manifest.json`, `resume-one-generation.json`, `vc3d_trace_evidence.py`),
`windcheck/README.md`, `spiralcheck/{README,VALIDATION,DESIGN}.md`,
`vesuvius-automesh/{README,TECHNICAL_NOTES}.md` + `tracer_sweep.py`,
`villa/vesuvius/.../evaluation/evaluate_vc3d.py`, `scrollreading/pipeline5/readme.md`.
Un sous-agent a doublé ce balayage sur les 35 dépôts, en 15 passes de motifs distinctes (exclusions
systématiques `.git .venv node_modules site-packages build deps third_party dist nnunet` — sans
elles le signal se noie dans les lexers Pygments et botocore de `windcheck/.venv`) :
`vc_grow_seg_from_seed` (12 fichiers hors artefacts CMake, tous inspectés) ·
`non-?determinis|reproducib|flaky|std ?dev|error ?bar|variance|variabilit|rerun|run twice|repeated run|N runs|replicate|jitter|identical (params|inputs)`
(~120 hits triés) · `srand\(clock|unseeded|rng.*clock` · `self.?cross|self.?intersect` (~40 fichiers) ·
`intersection count|crossing count|number of self.?intersections` · `±` sur md/txt (**24 hits, tous
des tolérances géométriques — aucune barre d'erreur sur une aire**) ·
`(area|cm2|mm2).*(std|stddev|variance|error bar|spread)` (6 hits, tous faux positifs sauf
`run_release_bounds_ablation.py:54`) ·
`num_runs|n_runs|num_trials|n_trials|num_repeats|--repeat|n_replicates|n_seeds|--trials`
(~40 hits, **aucun** ne pilote une répétition du traceur) ·
`same (params|config|seed|inputs).*(twice|again|differ|vary)` (1 hit) ·
`same seed point|twin run|identical run|repeat(ed)? (the )?trac` (5 hits) ·
`(trace|tracer|patch|surface).*(vary|varies|differs) (from|between|across) run` → **0 hit** ·
`vc_tifxyz_selfcross` (20 hits, tous windcheck).

**Négatifs nets, vérifiés au-delà du grep** : `winding-ruler` (ne mentionne jamais le traceur ; son
« seven runs » porte sur `predict3d` à des scaledowns différents) · `tifxyz-surgeon` (0 occurrence
de determin/reproduc/varian/repeat/selfcross/vc_grow) · `winding-sync` (ses « runs » sont des
*run-length* de pixels) · `spiral-fitting` · `spiralcheck` (ne cite `vc_grow_seg_from_seed.cpp` que
comme lecture de source sur la tolérance d'overlap, `DESIGN.md:491`, `VALIDATION.md:178` — ne
l'exécute jamais) · `windcheck` (tout son travail statistique porte sur des **défauts injectés**
dans des surfaces existantes, ou sur le déterminisme du *validateur*) · `vesuvius-automesh` (son
`n_runs: 16683` est un comptage de *runs de pixels*). Les 26 dépôts restants ne mentionnent pas le
traceur ; leurs hits `variance`/`covariance` sont des matrices 3×3 pour PCA de normales
(`scrollfiesta`) ou des normalisations de datasets ML (`ThaumatoAnakalyptor`, `ink-id`).

**Littérature (question 3).** `main.pdf` extrait par `pdftotext` (2524 lignes) : motifs
`determinis|reproducib|error bar|standard deviation|std\. dev|repeated|replicate|trial|±|run.?to.?run|variance`,
puis inventaire de tous les `Table`/`Fig.`, puis lecture des sections « Statistics and
reproducibility » (p. 28), « Determinism » (p. 42), et des tableaux p. 41-44. Vérifié par un
sous-agent indépendant, qui a couvert en plus : Seales « Reading the Invisible Library »
(`assets/files/retro-*.pdf`), `scrollreading/report{,2..10,12}.pdf` (11 fichiers),
`scrollfiesta/submission.pdf` + `submission_may.pdf`, ThaumatoAnakalyptor (2 PDF),
`Scroll_Equalizer.pdf`, et les 81 pages HTML de `data/site/scrollprize.org/` (balises retirées)
avec ~40 motifs, dont une passe « barres d'erreur » site-wide → 0 sur 81 pages.
Écartés comme dépendances tierces : `deps/taucs`, `deps/clapack`, `deps/src/zlib`, `libigl`, `mask3d`.

**Limite de couverture à connaître — c'est le trou principal de cet audit.**
⚠ **Tous les clones sont superficiels.** Sur `villa` : `git rev-list --count HEAD` = **1**,
`.git/shallow` présent ; idem sur les 9 dépôts prioritaires. **Aucun message de commit, aucune PR,
aucun historique n'est minable localement** — `git log --grep=determin|reproduc|varian|flaky|repeat`
ne peut rien rendre. De plus il n'existe **aucun dossier `issues/` local**, les 8 `.github/`
présents ne contiennent que des workflows, et le corpus entier ne compte **qu'un seul CHANGELOG**
(`spiralcheck/CHANGELOG.md`, sans rien de pertinent). Je ne peux donc pas exclure qu'un commit, une
PR ou une issue GitHub documente le non-déterminisme du traceur ; ce trou ne peut être comblé
qu'en ligne. Enfin, les trois `main.pdf` du corpus sont le même fichier — la littérature primaire
couverte se réduit à **un** papier de référence, plus les rapports communautaires listés.

---

## ce qui reste neuf

1. **La mesure.** Aucune campagne de répétitions à paramètres identiques sur
   `vc_grow_seg_from_seed` n'existe dans les 35 dépôts. Les chiffres — 78 exécutions, 13 rouleaux,
   **0/13** rendant deux fois la même aire, **5/13** basculant de verdict, **5/78 = 6,4 %** — n'ont
   d'équivalent nulle part. La seule campagne de répliques trouvée (D1) conclut l'inverse parce
   qu'elle a épinglé les fils, changé de binaire, limité à une génération et utilisé un faux volume.
2. **La bascule de verdict comme observable.** Faire porter la non-reproductibilité sur une
   **réponse binaire du vérificateur officiel** — donc sans seuil et sans vérité terrain — n'est
   fait nulle part. `windcheck` compte des auto-intersections sur une exécution unique ;
   `tifxyz-doctor` compare des hachages entre répliques. Personne ne compare des **verdicts**.
3. **Le constat que l'aire ne signale pas le mauvais tirage** (rang normalisé moyen 0,68) : aucun
   antécédent, et c'est ce qui interdit l'échappatoire « jeter la valeur aberrante ».
4. **Le lien mécanisme → conséquence.** Que le remède exige **les deux moitiés** (graine *et* un
   seul fil), parce que le tirage est consommé dans une région OpenMP (A3), n'est écrit nulle part :
   le monorepo publie la moitié « un fil » pour une raison de **débit** (C2) et cache la moitié
   « graine » dans une variable d'environnement citée une seule fois dans 7,4 Go (C3).
5. **Un argument à RÉCUPÉRER, pas à craindre.** La documentation officielle publie que le
   vérificateur est déterministe et **invariant au nombre de fils**
   (`docs/tifxyz_selfcross.md:75-78`), et `windcheck` le remesure sur neuf configurations
   (`docs/submission.md:307-309`). Une bascule de verdict ne peut donc pas venir de
   l'instrument : elle prouve que **la surface a changé**. §5.1 gagnerait à citer cette
   garantie — elle transforme l'observable en mesure adossée à une propriété publiée par
   l'amont lui-même.
6. ⚠ **Correction à apporter à §5.1 — deux phrases sont attaquables telles quelles.**
   - « draws from an **unseeded** generator » : vrai **par défaut**, mais `VC_GROWPATCH_RNG_SEED`
     existe (A2/C3) et `srand(clock())` est semé à l'horloge, pas non semé. Formulation plus sûre :
     *« semé par `std::random_device` et par `clock()`, avec un unique opt-in non documenté »*.
   - « **This is not documented** » : vrai pour ce traceur, mais un relecteur produira B1/B2 —
     le même énoncé, dans un en-tête public de volume-cartographer, pour le segmenteur frère.
     Formulation plus sûre, et **plus forte** : *« volume-cartographer a documenté exactement cet
     avertissement pour `OpticalFlowSegmentation` ; le traceur qui l'a remplacé n'en porte
     aucun. »* Le fait que l'avertissement ait existé puis disparu avec l'algorithme qu'il
     décrivait est un meilleur argument que son absence.

---

# Audit d'antériorité adversarial — §5.2 « la stabilité et la propreté sont des artefacts du budget »

Corpus : `data/site/scrollprize.org/` (531 fichiers, 81 pages + 4 PDF) et `data/repos/` (35 dépôts, 13 Go).
Rien n'a été téléchargé. Tous les chemins ci-dessous sont relatifs à `/home/masterlaplace/LplVesuvius/`.

---

## verdict

**PARTIELLEMENT**

Le résultat se scinde en deux moitiés qui n'ont pas le même statut, et l'article les présente comme
une seule.

| moitié de la revendication | statut |
|---|---|
| **la propreté** — « les traces étaient propres parce qu'elles étaient courtes » | **DÉJÀ CONNU**, publié, quantifié, sur 278 traces, dans `windcheck` |
| **la stabilité** — dispersion d'aire écrasée par une troncature commune (0,55 % → 86 %, ×156) | **RIEN TROUVÉ** — personne dans l'écosystème ne mesure une dispersion sur des tirages répétés |
| le mécanisme général (troncature → fausse cohérence) | **PARTIELLEMENT** — la *forme* du raisonnement est présente quatre fois dans ce domaine, jamais énoncée sur un budget |
| le diagnostic proposé (« enregistrer la condition d'arrêt ») | **PARTIELLEMENT** — implémenté, en plus strict, dans un *autre* traceur de `villa` |

⚠ Le point le plus dommageable : l'article a un encadré de prior art (`docs/article/article.typ:277-287`,
« A prior-art audit of our own instruments (2026-08-29) found 22 of 98 already present in this
toolchain ») et **ne cite pas** le modèle de taille de `windcheck`, alors qu'il cite `windcheck` trois
fois pour d'autres vertus. C'est l'omission qu'un relecteur adverse trouvera en premier.

---

## preuves

### P1 — La propreté : antériorité DIRECTE, quantifiée, corpus entier

`data/repos/windcheck/docs/FULL-CORPUS.md:84-89`, verbatim :

> **So the size effect is mostly arithmetic, and that is the honest
> reading.** A larger surface has more opportunities to fold through
> itself; a small trace is clean substantially because it is small. This
> is not a claim that any tracer is better or worse than another, and the
> 86% figure published for the original five samples is not a property of
> those samples — it is what happens when you trace large surfaces.

**En quoi ça précède.** Deux phrases de l'article sont ici mot pour mot, à la variable près :

- article : « *The traces were clean because they were short.* » → windcheck : « a small trace is
  clean substantially because it is small ».
- article : « It was not a property of the scroll; it was the budget cutting them. » → windcheck :
  « the 86% figure … **is not a property of those samples** — it is what happens when you trace large
  surfaces ».

Ce n'est pas une remarque en passant : c'est le titre d'une section, `FULL-CORPUS.md:49`
(« ## The rate depends mostly on size »), ouverte par la mise en garde contre exactement la lecture
que l'article corrige — `FULL-CORPUS.md:51-53` :

> The new samples self-intersect at 30% against 86% in the five original
> ones. Read naively that says the new samples are three times cleaner. It
> does not.

Et c'est appuyé par un modèle ajusté, `FULL-CORPUS.md:68-71` :

> If every valid cell independently carried a crossing with probability
> `q`, then a trace of `N` cells would self-intersect with probability
> `1 − (1−q)^N`. Fitting that single parameter over all 278 traces gives
> **q = 7.2 × 10⁻⁶ per valid cell**, and the observed rates track it:

suivi d'un tableau à six bandes de taille, et de `FULL-CORPUS.md:82` : « Within about ten points
across five orders of magnitude of surface size. »

**La comparaison appariée par la taille est déjà opérationnelle**, `FULL-CORPUS.md:55-57` :

> Their median trace is **5.8× smaller** — 49,650 valid cells against
> 286,784. Matched by size the difference largely disappears, and in the
> band above 150,000 cells the new samples are if anything worse:

Et elle sert de ligne de base dans un audit publié, `data/repos/windcheck/README.md:374-376` :

> 96.7 million valid cells, 40 minutes, no GPU**. 84,311 are transverse-clean
> and five self-intersect, against 527 expected at the rate published traces
> of the same scroll self-intersect **when cut to the same size**.

Le résumé en tête de dépôt, `data/repos/windcheck/README.md:329-333` :

> That page also reports what the corpus says about size: self-intersection
> probability follows a one-parameter independent-cell model at
> **q = 7.2 × 10⁻⁶ per valid cell**, within about ten points across five
> orders of magnitude. A large surface is likely to fold through itself
> mostly because it is large.

**Portée exacte de l'antériorité.** La variable de windcheck est la **taille réalisée** (cellules
valides), celle de l'article est le **budget** (le bouton qu'on règle). C'est une différence réelle —
observation transversale contre intervention intra-instance — mais elle est plus mince qu'elle n'en a
l'air : windcheck normalise déjà « à taille égale » (`README.md:376`), et le budget n'agit sur la
propreté qu'*à travers* la taille. La chaîne « budget → étendue → propreté apparente » n'est jamais
écrite ; ses deux maillons le sont.

### P1 bis — mais le chiffre de l'article ne colle PAS au modèle publié, et c'est ce qui lui reste

Vérification reproductible :
`scratchpad/check_windcheck_model.py` (calcul dans l'arbre, pas en ligne de commande).

```
propreté observée      : 0.083 -> 0.750
N exigé par le modèle  : 12,085 -> 192,540 cellules   (facteur 15.9x)
aire observée          : 19.83 -> 75.85 cm2           (facteur 3.8x)
```

Sous le modèle `q = 7.2e-6`, passer de 1/12 à 9/12 de tirages sales exige **15,9×** plus de cellules,
alors que l'article n'observe que **3,8×** d'aire. Si les cellules valides croissent proportionnellement
à l'aire, le basculement mesuré est **plus raide que la seule arithmétique de taille** — donc le budget
ferait quelque chose *au-delà* de grandir.

⚠ Deux réserves, à ne pas escamoter : (a) « cellules ∝ aire » est une hypothèse que l'article n'a pas
vérifiée et qu'il peut trancher sur ses propres grilles ; (b) 1/12 et 9/12 sur n = 12 portent des
intervalles larges. Si (a) tient, **c'est là qu'est le résultat neuf sur la propreté**, et il est plus
fort que celui que l'article revendique aujourd'hui — mais il ne s'énonce qu'*en confrontation avec
windcheck*, pas en l'ignorant.

### P2 — La stabilité (dispersion d'aire) : rien, et pour une raison structurelle

Aucune trace, nulle part, d'une mesure de dispersion sur des tirages répétés du traceur.

Le seul endroit de l'écosystème qui exécute le traceur **plusieurs fois à configuration identique** est
`data/repos/tifxyz-doctor/verification/trace-impact/`, et il le fait à **une seule génération** :

`data/repos/tifxyz-doctor/verification/trace-impact/experiment-protocol.md:151-152` :

> `step=1` is essential: it makes resume initialization visit every possible
> integer cell origin, including row `H-2` and column `W-2`. **One generation makes
> this a tracer run while keeping runtime bounded.**

`data/repos/tifxyz-doctor/verification/trace-impact/README.md:17-18` :

> All four source variants ran three times. TIF arrays, masks, selected metadata,
> and parsed scientific log observations were identical within every variant.

**En quoi ça ne précède pas — et pourquoi c'est quand même la pièce la plus gênante.** C'est le
phénomène de l'article, exécuté : des réplicats tronqués au budget sortent **identiques au bit près**.
Mais l'accord y est *recherché* (c'est un contrôle de déterminisme pour une ablation de bug), jamais
interrogé. Personne ne demande si l'accord vient de la troncature. L'écosystème **utilise** l'artefact
sans le **nommer** — ce qui est exactement la position que l'article décrit chez lui-même dans son
propre encadré (`article.typ:844-852`, « we read it as nothing at all for a week »).

Corollaire vérifié indépendamment : les métadonnées officielles des segments publiés n'enregistrent
**ni budget, ni aire, ni condition d'arrêt**. Sur `data/metadata.min.json` (gzip), 311 segments publiés
(`auto_grown_*`), et les clés `max_gen`, `generations`, `area_cm2`, `area_vx2`, `elapsed_time_s`, `seed`,
`stop` apparaissent **0 fois**. Le diagnostic que §6 recommande n'est donc pas faisable depuis le corpus
publié.

### P3 — Le diagnostic « enregistrer la condition d'arrêt » existe déjà, ailleurs dans `villa`

`data/repos/villa/vesuvius/src/vesuvius/neural_tracing/fiber_trace_2d/runner.py:9843-9844` :

> "Trace2CP trace exhausted max_steps before reaching the opposite CP "
> "x-column; **this is not a valid metric result.** "

**En quoi ça précède.** §6 de l'article écrit : « The diagnostic is cheap: record the stopping condition
alongside the result, and check whether the low-variance instances are the ones that hit it. » Le traceur
neuronal de `villa` fait plus strict : il enregistre la raison de terminaison (`termination_reason`,
valeurs `"max_steps"`, `"target_columns"`, `"partial_target_columns"`, `"missing_target_columns"`) et
**refuse de rendre la mesure** quand le budget a mordu (`_raise_trace2cp_max_steps`, lignes 9819-9848).

**En quoi ça ne précède pas.** (a) C'est un *autre* traceur ; le `GrowPatch.cpp` qu'étudie l'article
n'a **aucune** notion de raison d'arrêt — vérifié : `grep -i "stop_reason\|stopping\|terminat\|converged\|
plateau\|saturat"` sur `core/src/GrowPatch.cpp` et `apps/src/vc_grow_seg_from_seed.cpp` rend **zéro
ligne**. La sortie du budget (`GrowPatch.cpp:4680`, `if (stop_gen && generation >= stop_gen) break;`) et
la sortie par frange vide (`:4672`, `while (!fringe.empty())`) produisent le même artefact, indistinguable ;
seul `surf->meta["max_gen"] = stop_gen` (`:3732`) est écrit, c'est-à-dire le budget **demandé**, jamais
celui atteint. (b) Le motif y est la validité d'une mesure isolée, pas l'écrasement d'une dispersion.

### P4 — Un balayage de budget contrôlé existe : `spiralcheck`, sur un autre budget et une autre question

`data/repos/spiralcheck/VALIDATION.md:557` : `## 8. The quality scale: 4x the step budget, on identical sealed evidence`

`VALIDATION.md:559-566` :

> Two fresh `fit_spiral` runs on the section 6 window, this time twins by
> construction: same Kaggle T4, same docker image (pinned by sha256), same
> seed, … differing in **exactly one key**: `num_training_steps`,
> 1,500 vs 6,000.

`VALIDATION.md:590-593` :

> - **Primary criterion: not met.** Paired distance deltas span zero in both
>   tails: p50 -0.41 [-0.82, +0.06] vox, p99 +0.40 [-1.40, +2.64] vox. Four
>   times the budget left the distance profile statistically unchanged on this
>   window.

**En quoi ça précède.** L'écosystème sait déjà qu'un budget est une variable qui mérite une expérience
contrôlée, pré-enregistrée, avec bootstrap apparié — donc « on a fait varier le budget » n'est pas neuf
comme geste.

**En quoi ça ne précède pas.** Trois écarts, tous décisifs : (a) c'est un budget de **pas d'entraînement**
d'un modèle, pas la boucle de croissance d'un traceur ; (b) la question est *l'exactitude* (le long run
ajuste-t-il mieux ?), pas *la dispersion* ; (c) il y a **un seul run par budget**, donc l'expérience ne
peut structurellement pas voir l'artefact — deux estimations ponctuelles ne dispersent pas.
`examples/analysis_plan_quality2.md:53-57` envisage même le régime **inverse** (« 1,500 steps may be
enough to converge on a 300-slice window … the 6,000 budget may only add polish ») : un budget qui *ne
mord pas*.

### P5 — Le mouvement de raisonnement (« mesurer le plafond ») est un lieu commun du domaine

`data/repos/windcheck/bench/interp_ceiling.py:7-15` :

> That number is uninterpretable on its own. At 20 vx sampling a genuinely
> touching surface still has its nearest vertex up to half a grid pitch away
> tangentially, so there is a ceiling on how well raw vertices *can* separate a
> real contact. This measures that ceiling on planted defects, where the answer is
> known exactly.
>
> Read it honestly in both directions:
>   ceiling ~0.82  -> real traces are at the ceiling; test C's "partial" is a
>                     limit of the sampling, not evidence against the flags

**En quoi ça précède.** C'est le raisonnement de §5.2, à la variable près : un nombre publié est peut-être
borné par l'**instrument** et non par le phénomène ; le remède est de mesurer le plafond, pas de
réinterpréter le nombre. Ici le paramètre limitant est le pas d'échantillonnage, chez l'article le budget.

Trois autres occurrences du même mouvement, toutes sur d'autres variables :

- **Censure nommée, avec bornes plutôt qu'un point** —
  `data/repos/windcheck/case-studies/scrollfiesta-pherc0139-4x5x5/prereg/PREREG-COVER-APPLICABILITY.md:124-126` :
  > 4. OUTCOMES: SOLVED / UNSOLVED_EXHAUSTED / CENSORED_TIMEOUT_OR_CAP
  >    (**the 64-switch cap is censoring too**). G2 bounds per diagonal:
  >    lower = solved/all; upper = (solved+censored)/all.

  C'est le mot « censure » appliqué à un **plafond de recherche**, avec la conséquence inférentielle
  correcte (un intervalle, pas une estimation ponctuelle). Le budget y est un plafond de temps/commutations,
  pas de générations.
- **Vacuité d'un test sur petites surfaces** — `data/repos/windcheck/docs/PATCH-AUDIT.md:53-57` :
  > A small patch is nearly planar and has limited room to fold through
  > itself, so **a null result could be an artifact of size.** That was checked
  > before any claim was made
- **Saturation d'un instrument** — `data/repos/vesuvius-automesh/TECHNICAL_NOTES.md:244-246` :
  > 3. **found_fraction ≥ 0.9 is calibrated, not control-validated — and it saturates on
  >    zero-gap fused terrain.**

**En quoi ça ne précède pas.** Aucune de ces quatre occurrences n'énonce la règle **générale** de §6
(« toute procédure d'ajustement itérative avec un budget produira, sur les instances où le budget mord,
des sorties qui s'accordent pour une raison étrangère à l'instance »). Le domaine a le réflexe, pas le
théorème — et surtout ne l'a jamais tourné vers un budget de générations.

### P6 — La documentation officielle attribue l'aire au rouleau, jamais au budget

`data/repos/villa/scrollprize.org/docs/35_segmentation.md:341` (= `data/site/scrollprize.org/segmentation.html:210`) :

> 2. Grow this segmentation some small-ish number of generations at a time, somewhere between 10-30 is a reasonable number

Le pas suivant donne la seule justification jamais offerte, et elle est ergonomique :
`35_segmentation.md:342-343` :

> 3. Check for errors, and fix ones that appear
> 4. Repeat steps 1-3 until you feel like stopping

Même justification côté `volume-cartographer`,
`data/repos/villa/volume-cartographer/docs/extending_and_modifying_segmentations.md:30` :

> i'd stick with a small number of steps for now, likely somewhere between 5-20, as **its easier to
> correct a small error than one that has gone on for some time**

La seule conséquence quantitative jamais énoncée pour le budget est la taille et la durée,
`data/site/scrollprize.org/tutorial_VC3D.html:91` :

> the more iterations you have selected, the bigger the resulting segment, but the longer it will take
> to complete. Later iterations take longer due to the edges of the surface being longer.

Et la doc affirme même l'inverse de l'article pour l'autre traceur,
`data/repos/villa/scrollprize.org/docs/35_segmentation.md:376` :

> The tracer will run for an indeterminate amount of time , until it runs out of area in which it can
> continue to grow. This could be 10cm^2 , or it could be 2800cm^2 -- **it completely depends on the
> surface prediction and patch quality.**

**En quoi ça soutient la nouveauté.** L'aire atteinte y est attribuée *entièrement* au rouleau
(« surface prediction and patch quality »). C'est précisément l'erreur d'attribution que §5.2 corrige.
⚠ Nuance à ne pas gommer : cette phrase décrit la méthode « tracer » (`vc_grow_seg_from_segments`), non
budgétée, pas le `vc_grow_seg_from_seed` qu'étudie l'article.

### P7 — Le papier de référence ne connaît pas la question

`data/site/scrollprize.org/pdf/main.pdf`, extrait `pdftotext` (2524 lignes) : `budget` n'apparaît que dans
des tables d'hyperparamètres d'entraînement (« Epoch budget (ink5) », l. 1952 ; « Max iterations
(scheduled) », l. 2103 et 2186). La description du traceur (l. 632-640) est purement qualitative
(« iteratively proposing and refining vertices ») et sa section « Statistics and reproducibility »
rapporte des surfaces et des heures de travail, aucune dispersion. Aucun lien budget↔mesure.

---

## ce que j'ai cherché et où

**Site** (531 fichiers ; tous les `.html`/`.md`/`.txt`/`.json`, plus 4 PDF via `pdftotext`) : motifs
`generation(s)`, `budget`, `max_gen`, `stop(ping)`, `truncat`, `censor`, `cut ?off`, `iterat`, `max_iter`,
`converge`, `plateau`, `saturat`, `10-30`, `grow`, `regrow`, `resume`, `variance`, `dispersion`, `spread`,
`reproducib`, `self.?intersect`, `artefact|artifact`, `bias`, `confound`, plus une passe sémantique
(`artificially`, `too similar`, `looks clean|stable`, `underestimat`, `spurious`, `same result`,
`error bar`, `standard deviation`, `confidence interval`). Lus intégralement : `segmentation.html`
(100-234), `tutorial_VC3D.html`, `unwrapping.html` (110-190), `2026_open_problems.html` (sections
tracing/bottlenecks), `open_problems/winding_annotations.html`, les 3 README de datasets, plus tous les
tutoriels et `faq.html`/`prizes.html` par grep avec inspection de chaque hit en contexte.
`bias` ne matche que « Tobias Reinhardt » et « Weights & Biases » ; `truncat` que la classe CSS
`text--truncate`. **Aucun énoncé de biais.**

**Dépôts** (35, includes `*.py *.md *.cpp *.hpp *.h *.rs *.json *.yaml *.yml *.txt *.ipynb *.sh`, excludes
`build .git node_modules third_party vendor target .venv site-packages`) : 14 passes sur tout l'arbre, dont
`artefact of|artifact of|confound|spurious agreement|false coherence|ceiling effect|floor effect|censor|
survivorship|selection bias` ; `generation budget|max_gen|stop_gen|--generations|"generations"` ;
`\bbudget\b` (515 hits, dépouillés par dépôt) ; `low variance|dispersion|coefficient of variation|
run-to-run` ; `saturat|plateau|\bceiling\b` ; `clean because|stable because|look(s) clean|short(er) runs|
more generations` ; et une **passe d'adjacence** (`grep -B3 -A3` autour de `budget|max_iter|iteration
(limit|cap)|generations|stop_gen`, filtrée sur `artifact of|confound|bias|spurious|low variance|not a
property of|nothing to do with`) qui rend **une seule ligne sur tout l'arbre, et c'est un faux positif**
(`fiber_trace_2d/planning/specs.md:2047`, « center-biased closest-approach »).

Passes ciblées : tous les fichiers `*sweep*|*ablation*|*sensitivity*|*scaling*` (27, classés un par un —
aucun ne balaie un budget de générations : `windcheck` balaie le *jitter* d'injection, `vesuvius-automesh`
les *graines* avec `generations` figé à 200 (`tracer/params_seed_v3.json:5`), `scrollfiesta` les itérations
LOP (`scripts/lop_iter_sweep.sh:18`, `for N in 10 20 … 90`) mais sur un lissage de nuage de points, pas un
traceur) ; `villa` sur `vc_grow_seg_from_seed` (60 hits) ; lecture intégrale de
`windcheck/docs/FULL-CORPUS.md`, `windcheck/docs/PATCH-AUDIT.md`, `spiralcheck/VALIDATION.md` §8,
`tifxyz-doctor/verification/trace-impact/{README,experiment-protocol}.md`.

**Sources propres** : `data/metadata.min.json` (gzip, 45 échantillons, 311 segments) inspecté par walk de
clés ; `docs/article/article.typ` §2, §5.2, §6 et `references.bib` lus pour situer ce que l'article
concède déjà.

**Lacunes de couverture, déclarées.** (a) Les 35 dépôts sont des clones **`--depth 1`** — `git log` rend
1 commit chacun, donc **les messages de commit, les issues et les discussions de PR n'ont pas pu être
fouillés**, et c'est justement là qu'un « stopping early gives fake convergence » s'écrit souvent. C'est
la lacune sérieuse de cet audit. (b) Pas de Discord, pas de forum, pas de littérature externe (hors
périmètre par consigne). (c) Sorties `.ipynb` et binaires non inspectées. (d) Les blogs de
`villa/scrollprize.org` hors `docs/` n'ont pas été lus intégralement.

---

## ce qui reste neuf

1. **La dispersion d'aire comme artefact de troncature.** Rien de comparable dans le corpus. C'est le
   cœur défendable, et il tient à une propriété que l'audit confirme : **personne ne tire le traceur
   plusieurs fois à configuration identique pour en mesurer l'étalement** — le seul réplicat existant
   (`tifxyz-doctor`) est à une génération et cherche l'accord au lieu de l'interroger.
2. **L'intervention intra-instance.** windcheck établit une loi transversale sur des tailles réalisées ;
   l'article change le budget *sur le même rouleau, tout le reste égal*, et observe le basculement. C'est
   un design plus fort, et il est neuf ici — mais il faut le présenter comme tel, pas comme la découverte
   du lien taille↔propreté.
3. **L'excès sur le modèle publié** (P1 bis) : ×15,9 exigé contre ×3,8 observé. Si l'hypothèse
   cellules ∝ aire tient, le budget fait plus que grandir la surface, et *ça* windcheck ne le dit pas.
   À vérifier sur les grilles de l'article avant d'en faire quoi que ce soit.
4. **La contamination d'une comparaison publiée** (le test des signes graine-planarité 11–2, dont 7 traces
   sur 13 s'arrêtent au budget et dont les deux « défaites » sont les deux rouleaux où *les deux* critères
   butent). Aucune antériorité : personne ne compare deux réglages sur des sorties tronquées ni ne signale
   ce que ça invalide.
5. **L'énoncé général de §6.** La forme circule (P5) ; la règle sur les budgets n'est écrite nulle part.

### ⚠ Ce qu'il faut corriger dans l'article avant soumission

- **Citer `windcheck/docs/FULL-CORPUS.md`** dans §5.2, pas seulement dans l'encadré de toolchain, et
  requalifier la phrase « The traces were clean because they were short » en confirmation intra-instance
  d'un résultat publié. Laissée telle quelle, elle se lit comme une découverte et un relecteur la cassera
  en une ligne.
- **Citer `runner.py:9843` dans §6** : le diagnostic recommandé existe déjà, en plus strict, dans le même
  monorepo. Le dire renforce la recommandation (« ce que `villa` fait pour son traceur neuronal, personne
  ne le fait pour `GrowPatch` ») au lieu de l'exposer.
- **Mentionner `spiralcheck` §8** comme le précédent du geste (budget contrôlé, pré-enregistré) et dire
  pourquoi un run par budget ne peut pas voir l'artefact.
- **Faire tourner P1 bis** et, si l'hypothèse tient, en faire le résultat principal de la moitié
  « propreté » — c'est le seul énoncé de cette moitié qui survive à windcheck.

---

# Audit d'antériorité adversarial — « les segments publiés échantillonnent, ils ne pavent pas »

Cible : `docs/article/article.typ` §5.7 `<sec:merge>` (lignes 1065–1102).

---

## VERDICT

**PARTIELLEMENT** — et la partie déjà connue est la plus grosse.

Décomposé, le résultat a quatre composants. Trois sont antérieurs, un seul survit :

| Composant du résultat | Statut |
|---|---|
| « L'outil de couture exige des surfaces qui se recouvrent » | **DEJA_CONNU** — écrit noir sur blanc dans la doc officielle et dans le papier de référence. L'article le concède déjà. |
| « Les segments publiés sont des pièces éparses avec des trous entre elles, ils ne couvrent pas le rouleau » | **DEJA_CONNU** — c'est la *motivation déclarée* du spiral fit dans le tutoriel officiel. |
| « Un recouvrement de boîte englobante ne distingue pas même-feuille de feuille-voisine ; le discriminant est l'écart point-à-point » | **DEJA_CONNU** — nommé verbatim dans `windcheck`, et *implémenté* dans `volume-cartographer` (la bbox n'y est qu'un rejet bon marché, la décision est une distance point-à-surface à 2 voxels). Mesuré en µm contre l'épaisseur de feuille par `vesuvius-automesh`, et en médiane par paire par `spiralcheck`. |
| « Sur `PHerc1447`, 15 segments, 105 paires, 51 recouvrements de boîte, 0 sous 40 µm, la plus proche à 79 µm » | **RIEN_TROUVE** — aucune trace de cette mesure, sur ce rouleau ni sur un autre, dans les 81 pages du site, les 35 dépôts, ou le papier. |

Autrement dit : **l'idée, le discriminant et l'instrument sont tous antérieurs ; seul le chiffre sur ce rouleau est neuf.**

⚠ Et il y a pire qu'une antériorité : une **contradiction méthodologique publiée**, §D ci-dessous — la doc de `volume-cartographer` affirme qu'*aucun* seuil de distance ne sépare les feuilles, ce qui vise directement le « seuil de même-feuille » à 40 µm sur lequel repose la table §5.7.

---

## PREUVES

### A. Question 1 — « les segments échantillonnent au lieu de paver » : déjà écrit, et c'est la motivation officielle du spiral fit

**A1.** `data/repos/villa/scrollprize.org/docs/38_tutorial_spiral.md:46`
(rendu : `data/site/scrollprize.org/tutorial_spiral.html:34`)

> « Most of our segmentation tools work bottom-up. GrowPatch, lasagna, and manual segmentation in VC3D all produce *patches* — pieces of papyrus surface that you grow bigger and bigger until they hit a tricky region and stall. Other tools trace individual fibers. Either way you end up with a big pile of small pieces: segments, fibers, point annotations. What we really want is the *whole scroll* — one surface covering every winding of the original papyrus sheet, from the center to the outer shell. **However, gluing the pieces together directly is hard, especially where there are gaps between them.** »

*En quoi ça précède :* c'est exactement la prémisse de §5.7 — un tas de pièces, des trous entre elles, et le collage direct déclaré difficile *à cause de* ces trous. Publié par les organisateurs, en tête du tutoriel.

**A2.** `data/repos/villa/scrollprize.org/docs/38_tutorial_spiral.md:59` (note de bas de page `[^tracer]`)

> « The surface tracer is an earlier attempt at this problem: it stitches overlapping patches into large segments automatically. **But it requires the patches to physically overlap or touch,** and it becomes unreliable at whole-scroll scale. »

*En quoi ça précède :* la phrase de l'article « The tool exists and needs surfaces that *overlap* » (`article.typ:1067–1068`) est cette note, en plus court.

**A3.** `data/repos/villa/scrollprize.org/docs/38_tutorial_spiral.md:83`
(rendu : `tutorial_spiral.html:50`)

> « **None of these individually needs to cover the scroll. Sparse, scattered evidence — a patch in one region, a fiber in another,** a few relative-winding annotations in an ambiguous area — is combined by the fit into one consistent global solution »

*En quoi ça précède :* « sparse, scattered evidence — a patch in one region » est la formulation officielle de « un ensemble d'échantillons, une pièce par feuille ».

**A4.** `data/repos/villa/scrollprize.org/docs/38_tutorial_spiral.md:48`

> « Where the evidence is dense, the fitted surface follows it closely; **where there are gaps, the spiral bridges them smoothly instead of stopping or leaving a gap.** »

et `tutorial_spiral.html:52` :

> « a full set of surfaces that conform to the input constraints, **covering the whole fitted region including places no patch ever reached.** »

*En quoi ça précède :* la conclusion de l'article (« there is nothing to stitch », donc la route est fermée) a déjà sa réponse publiée — on ne coud pas, on ajuste un spiral global. « places no patch ever reached » dit que les patchs ne pavent pas.

**A5.** `data/repos/villa/scrollprize.org/docs/35_segmentation.md:349`
(rendu : `data/site/scrollprize.org/segmentation.html:215–216`)

> « The tracer method requires a "seeded" volume , **containing thousands of overlapping segmentations with some metadata marking which ones overlap eachother.** »

et `35_segmentation.md:359` :

> « Place these manual seeds until you've covered a decent portion of the volume, such that if these patches were grown, they could reasonably cover the entire volume. »

*En quoi ça précède :* le recouvrement n'est pas censé venir des segments publiés — il est **fabriqué exprès** par un semis dense. §5.7 mesure l'absence d'une propriété que la doc n'a jamais attribuée à ce corpus.

**A6.** Le papier de référence lui-même, `data/site/scrollprize.org/pdf/main.pdf` (texte extrait, p. 18) :

> « Initial unwrappings for new scans were created with a surface-based tracing tool that used a large dataset of smaller meshes generated by the seed- and prediction-based mesh-growing procedure described above. **Seed locations and seed density were chosen to ensure substantial overlap between base meshes.** »

*En quoi ça précède :* Angelotti et al. déclarent que le recouvrement est une propriété **construite** par le choix de densité de semis. C'est la même chose qu'A5, dans l'article primaire.

**A7.** `data/repos/villa/scrollprize.org/docs/12_grand_prize.md:79`

> « Segmenting the scrolls. The Herculaneum scrolls are especially long, tightly wrapped, damaged, and distorted. **To date, no one has successfully done a large-scale segmentation of these scrolls to identify the surfaces of all the rolled layers.** »

*En quoi ça précède :* l'inexistence d'un pavage est la position publique déclarée du challenge.

**A8.** `data/site/scrollprize.org/open_problems/winding_annotations.html:79`

> « **These constraints do not need to form a dense surface or cover the entire scroll.** They tell the optimizer how **disconnected pieces of local evidence** relate to the scroll's global rolled structure. »

---

### B. Question 2 — l'écart point-à-point entre segments publiés, et le tri même-feuille / feuille-voisine : mesuré par au moins quatre outils, dont trois que l'article cite déjà

**B1. `volume-cartographer` : le prédicat officiel de recouvrement fait déjà exactement ce que l'article présente comme son discriminant.**

`data/repos/villa/volume-cartographer/core/src/QuadSurface.cpp:3108–3126` :

```cpp
bool overlap(QuadSurface& a, QuadSurface& b, int max_iters)
{
    if (!intersect(a.bbox(), b.bbox()))
        return false;

    cv::Mat_<cv::Vec3f> points = a.rawPoints();
    for(int r=0; r<std::max(10, max_iters/10); r++) {
        ...
        if (b.pointTo(ptr, loc, 2.0, max_iters) <= 2.0) {
            return true;
        }
    }
    return false;
}
```

*En quoi ça précède :* **la boîte englobante n'est qu'un rejet bon marché ; la décision est une distance point-à-surface avec un seuil dur de 2,0 voxels.** L'affirmation « a box overlap cannot tell two patches of one sheet from two adjacent sheets » (`article.typ:1071–1073`) n'est pas une découverte : c'est le motif d'implémentation du code de référence, et l'article cite `villa` dans sa bibliographie (`references.bib:55`). Même seuil dans `contains()` juste en dessous (`QuadSurface.cpp:3128`), et dans le fork historique `volume-cartographer-schilling/core/src/Surface.cpp:1414–1432`.

**B2. Un outil dédié existe dont le métier est précisément « quelles paires de segments se recouvrent ».**

`data/repos/villa/volume-cartographer/apps/src/vc_seg_add_overlap.cpp:30` :
```cpp
constexpr float kOverlapTolerance = 2.0f;
```
`vc_seg_add_overlap.cpp:132–134` (aide en ligne) :
> « Builds a stride-1 surface patch index for target-dir and adds / overlapping.json metadata for overlaps found from the source. / source may be one tifxyz segment directory or a directory of segments. »

**B3. Et un balayage par paires à l'échelle du corpus, avec la distance sommet-vers-surface, existe en Python.**

`data/repos/villa/volume-cartographer/scripts/spiral/connect_overlapping_patches.py:1–15` :
> « Find pairs of overlapping tifxyz patches via the surface patch spatial index. […] Every *other* patch whose surface lies within ``--tolerance`` of those vertices is an overlap candidate; the number of the patch's vertices that land on the other patch is the (directed) overlap amount. / **Both directions of each pair are measured**, then combined »

`connect_overlapping_patches.py:513–514` :
```python
@click.option('--tolerance', type=float, default=2.0, show_default=True,
              help='max distance (voxels) from a vertex to another patch surface to count as overlapping')
```

*En quoi ça précède :* c'est l'instrument de la mesure de §5.7, déjà écrit, déjà dans le dépôt officiel.

**B4. `spiralcheck` — la médiane point-à-surface par paire, sur des patchs *publiés*, avec l'arbitrage explicite même-feuille / winding voisin. C'est l'antériorité la plus proche du résultat.**

`data/repos/spiralcheck/scripts/real_overlap_check.py:1–3` :
> « Real-data null control: **overlapping verified patches trace the same sheet**, so the distance from one patch's quad centers (restricted to the partner's bounding box) to the partner's surface should be small. »

`real_overlap_check.py:77–78, 89` :
```python
        med.append(float(np.median(dist)))
        p95.append(float(np.percentile(dist, 95)))
    print(f"pairs with median <= 2 vox: {(med_a <= 2).mean() * 100:.1f}%")
```

`data/repos/spiralcheck/DESIGN.md:481–500` :
> « Overlap null-control (150 pairs from `overlapping.json`) […] the typical pair agrees to sub-voxel across its zone (per-pair p95 distance: median 0.80 vox), and 80.7% of pairs have median <= 2 vox. […] `overlapping.json` records that two surfaces touch *somewhere*: both geometric producers test at 2 voxels (`apps/src/vc_seg_add_overlap.cpp`, `kOverlapTolerance = 2.0f`, and `core/src/QuadSurface.cpp`'s `overlap()` […]). **A 2 voxel test cannot pair surfaces a winding pitch apart, so the earlier working hypothesis (radially adjacent patches on neighbouring windings) is ruled out by villa's own code.** »

*En quoi ça précède :* médiane point-à-surface par paire de patchs publiés + hypothèse concurrente « winding voisin » explicitement posée et tranchée. C'est la démarche de §5.7, sur un autre rouleau, publiée par un outil que l'article **cite déjà** (`references.bib:96`, `article.typ:270`).

**B5. `vesuvius-automesh` — la même mesure, dans les mêmes unités, contre les mêmes échelles physiques.**

`data/repos/vesuvius-automesh/README.md:9–10` :
> « The best-overlapped windows track the human surface at a **median 28–41 µm** (**papyrus sheet thickness ≈ 40 µm; the neighboring wrap is 300+ µm away**). »

`README.md:36–38` :
> « Numbers, per overlapping window (`qc/overlap_distance_stats.json`; **distances are nearest-point distances from window vertices to the human mesh**…) »

Artefact machine, `data/repos/vesuvius-automesh/qc/overlap_distance_stats.json` :
```json
{"window": "auto_grown_20260612115408589_w0000_0387", "segment": "142020",
 "overlap_frac": 0.6918429003021148, "dist_p50_um": 27.582783432975027, "n_pts": 229}
```

*En quoi ça précède :* écart **médian point-à-point en µm** entre deux surfaces, comparé à l'épaisseur de feuille (~40 µm) et à la distance au wrap voisin (300+ µm). C'est le seuil de 40 µm et l'« ordre de l'écart inter-feuilles » de l'article, publiés avant lui, par un outil que l'article **cite** (`references.bib:72`, `article.typ:255`).

**B6. `winding-sync` — comparaison par paires de segments *publiés*, « combien de feuilles les séparent », et le piège nommé.**

`data/repos/winding-sync/README.md:181–190` :
> « Verified against labelled ground truth: **the PHerc. Paris 4 segments are named by absolute winding number** (`w116-117`, `w120-121`, …), giving per-location truth. **Median counts over four geometrically-filtered segment pairs** […] »

`README.md:203–208` :
> « **Measured winding spacing differs per scroll.** From the labelled Paris 4 meshes, that scroll's radial spacing is **165 µm** […] ~136 µm perpendicular »

**B7. `windcheck` — le discriminant même-feuille / winding-différent comme moteur de première classe.**

`data/repos/windcheck/engines/atlas_query.cpp:6–14` :
> « w1, d1 winding of the nearest reference surface, and the distance to it / **w2, d2 the same for the nearest surface of a *different* winding** / **d1 is a true point-to-surface distance** (nearest point on the bilinear quad, via its two triangles), not a distance to the nearest grid sample. That matters: the reference grids are sampled every ~20 voxels while **adjacent sheets sit ~30 voxels apart**, so a nearest-sample lookup has only a ~1.5x margin and cannot certify anything. **Nearest-point drives d1 to ~0 on the correct sheet while d2 stays at the sheet spacing.** »

Les surfaces de référence sont les segments publiés — `data/repos/windcheck/src/windcheck/atlas.py:3–6` :
> « The 44 single-winding segments (`w052`-`w095`, contiguous) say where each sheet physically is. »

`data/repos/windcheck/bench/orphan_skip.py:1–6, 61` :
> « GATE CONDITION 1: are there zero sheets between known-adjacent wraps? / The 44 labelled windings of PHerc0172 are consecutive sheets, w_k and w_{k+1}. »
```python
    good = np.isfinite(d) & (d > 8) & (d < 30)             # a plausible one-sheet gap
```

`data/repos/windcheck/bench/disagreement.py:7–9, 47–50, 67–68` :
> « The patch set is 84,316 independent reconstructions of one scroll. **Where two overlap they disagree about where the sheet is, and that disagreement is measurable EVERYWHERE they overlap** »
```python
def disagreement(a: Path, b: Path, max_samples: int = 4000) -> dict | None:
    """Median distance from A's points inside B's box to B's surface.

    Median rather than mean: one bad corner must not carry the statistic.
```

*En quoi ça précède :* « médiane plutôt que moyenne », distance de A vers la surface de B, sur des patchs publiés — le geste exact de §5.7. `windcheck` est cité par l'article (`references.bib:64`, `article.typ:265`).

---

### C. Question 3 — le piège « la boîte ne discrimine pas » : nommé verbatim

**C1.** `data/repos/windcheck/docs/PATCH-AUDIT.md:216–219` :

> « **Bounding-box overlap is a weak proxy** for the pairs a merger would actually join, so the 2.2% is over box-overlapping pairs, not over merge candidates. The rate among genuine merge neighbours is unmeasured and could be higher or lower. »

avec, `PATCH-AUDIT.md:147–148` :
> « Of 84,316 bounding boxes, **27,778,181 pairs overlap**. Of 459 sampled and censused, **10 interpenetrate — 2.2%** »

*En quoi ça précède :* c'est le cœur revendiqué de §5.7 — « un recouvrement de boîte ne dit pas ce qu'on croit » — écrit comme limite explicite, à l'échelle de 27,8 M de paires.

**C2.** `data/repos/winding-sync/README.md:211–214` :

> « **Naive probe pairing is unreliable.** Nearest-neighbour matching between two segment surfaces finds wherever they happen to come close, including edges and near-touching regions: **40–59% of candidate pairs traverse gaps too small to contain the claimed winding count.** Filter on expected gap before scoring. »

*En quoi ça précède :* le piège est nommé un cran plus loin que dans l'article — même le plus proche voisin, pas seulement la boîte, induit en erreur entre deux segments.

**C3.** `data/repos/villa/volume-cartographer/core/test/test_tifxyz_selfcross.cpp:299–302` (le caveat AABB en test de régression) :

> « a collapsed triangle beyond the proper one's hypotenuse (x + y = 8): / **boxes overlap, but the nearest segment point (4,6) sits 1.41 from the triangle** -- comfortably outside the touch tolerance »

**C4.** `data/repos/villa/volume-cartographer/apps/src/vc_merge_tifxyz.cpp:369–374` — l'outil de fusion s'est déjà fait piéger par des feuilles voisines prises pour la même :

> « This rejects two pathologies **seen with fused windings** — degenerate near-identity **"stacked" placements** (shift << consensus) and wild-scale "diagonal" models […] It auto-disables for **co-located patch merges**, where the consensus shift is itself ~0. »

et `vc_merge_tifxyz.cpp:791–793` :
> « Centroid shift (cells) a pair model implies on its own anchor set […] **~0 for a stacked/co-located placement, ~one wrap width for a true winding-advance seam.** »

**C5.** `data/repos/villa/lasagna/docs/claude_context.md:190` — la même confusion, en version plus-proche-voisin, signalée comme bug :

> « This 3D nearest-neighbor search fails for combined tifxyz with multiple disconnected windings because **it can find nearest points on the wrong winding**. »

---

### D. ⚠ Contre-position publiée — pas une antériorité, une objection au discriminant lui-même

`data/repos/villa/volume-cartographer/docs/tifxyz_selfcross.md:9–13` :

> « **Proximity between wraps is normal in a crushed scroll and can be arbitrarily small while the trace is correct, so no distance threshold separates good traces from bad ones.** A transverse self-intersection is different in kind […] and no threshold to argue about. »

`tifxyz_selfcross.md:20–22` :
> « `coplanar` — (near) coplanar triangles with overlapping projections. **Two sheets pressed flat against each other look like this**, so it is reported but never counted as a crossing. »

Position identique, argumentée, chez trois autres :
- `data/repos/windcheck/docs/submission.md:101–105` : « An earlier version of this tool measured **proximity** […] Two volume-cartographer maintainers pointed out, independently and correctly, **that this is undecidable**: > *"some wraps are in reality very tightly packed in places (~5um)"* »
- `data/repos/windcheck/engines/selfcross.cpp:3–6` : « That question is **irreducibly ambiguous**, because wraps in a crushed scroll genuinely lie very close together, so **a small distance can never by itself mean the trace is wrong.** »
- `data/repos/tifxyz-surgeon/README.md:195–200` : « Of the 16 segments, exactly **one** has a wrap spacing this detector can work with. **Eleven have a wrap gap under 3 cells — as low as 0.4** »

*Pourquoi c'est important pour l'article :* la table de §5.7 (`article.typ:1088–1091`) traite « < 40 µm ⇒ même feuille, mergeable » et « 40–250 µm ⇒ feuilles voisines, must not be merged » comme une partition acquise. Quatre sources indépendantes du corpus affirment que l'espacement inter-wrap **descend jusqu'à ~5 µm par endroits**, donc qu'aucun seuil fixe ne sépare les deux populations. La conclusion « il n'y a rien à recoudre » ne suit pas du fait qu'aucune paire ne passe sous 40 µm — sauf à défendre le seuil contre cette littérature. C'est le point d'attaque le plus dangereux du référé, et il est actuellement non traité dans l'article.

---

### E. Caveat de données à connaître

**E1.** `data/repos/villa/scrollprize.org/docs/06_tutorial_VC3D.md:109` :
> « Let's start with PHerc1447. **This scroll (as of July 13, 2026) has no public surfaces**, so let's make one. »

⚠ **Ce n'est PAS une réfutation de la prémisse** : j'ai vérifié l'index officiel, `data/repos/villa/scrollprize.org/static/data_browser/index.json` (entrée `id = PHerc1447`), qui porte `n_segments = 15`, `min_px = 8.64`. Les 15 segments existent. La phrase du tutoriel est datée et périmée. À noter tout de même : le tutoriel montre que ces surfaces sont récentes et non-manuelles.

**E2.** Le comptage « 51 paires se recouvrent par boîte englobante » repose sur les `bbox` des `meta.json`, dont la fiabilité est un défaut documenté — `data/site/scrollprize.org/community_projects.html:270–272` :
> « detects the **stale-bbox corruption** of villa#1272 (**106 of 4,922 verified PHercParis4 spiral-input patches affected**, independently reproducing the issue's counts) »

---

## CE QUE J'AI CHERCHÉ ET OÙ

### Site (fait par moi)
`data/site/scrollprize.org/` — 81 pages HTML, converties en texte puis grepées intégralement (sauf `data_browser/`, parcouru séparément).
- Motifs : `tiling|tile|stitch|overlap|adjacent|coverage|merge|one patch|sample|contiguous|seam|gap|do not overlap|no overlap|cover the entire|one segment per|per winding|nothing to stitch|bounding box|bbox|aabb|point-to-point|hausdorff|chamfer|median distance|nearest neighbour|sheet spacing|inter-sheet|winding pitch|sheet-to-sheet`.
- Pages lues en entier : `tutorial_spiral.html`, `segmentation.html`, `unwrapping.html`, `2026_open_problems.html`, `open_problems/winding_annotations.html`, `community_projects.html`, `data_datasets.html`, `data.html`, `data_browser/PHerc1447.html`.
- **Négatif notable** : sur tout le site, `bounding box|bbox|aabb` ne donne que 3 occurrences, toutes sur la corruption de métadonnées `bbox` (`winners.html:99`, `community_projects.html:270,272`) — **le piège de la boîte n'est nommé nulle part sur le site**. `point-to-point|hausdorff|chamfer|median distance` : **0 occurrence** hors une mention d'interpolation ImageJ (`tutorial1.html:176`).

### Papier de référence (fait par moi)
`data/site/scrollprize.org/pdf/main.pdf` → texte (2524 lignes). Motifs : `tile|tiling|stitch|overlap|merge|adjacent sheet|neighbouring|bounding box|coverage|point-to-point`.
- **`PHerc. 1447` n'apparaît pas une seule fois dans le papier.**
- `coverage` n'apparaît qu'à propos des critères de lecture de PHerc. 1667 et du tuilage de l'acquisition annulaire, jamais du pavage d'une feuille par des segments.

### `villa` (7,4 Go — sous-agent, résultats vérifiés par moi sur les 4 citations décisives)
Chemins : `volume-cartographer/{apps/src,apps/VC3D,core/{src,include,test},docs,scripts/spiral,utils}`, `scrollprize.org/docs` (40 fichiers `.md`/`.mdx`), `scrollprize.org/static/data_browser/index.json`, `segmentation/`, `lasagna/`, `vesuvius/`, `foundation/`, `CLAUDE.md`, `AGENTS.md`, `README.md`.
- Outils de fusion recensés exhaustivement : `vc_merge_patch.cpp`, `vc_merge_tifxyz.cpp`, `vc_merge_tifxyz_grid.{cpp,hpp}`, `vc_seg_add_overlap.cpp`. Aucun `vc_stitch*`/`vc_fill*` n'existe.
- **Négatifs auditables (0 occurrence dans tout `villa`)** : `same-sheet threshold`, `sheet threshold`, `79 µm`, `40 µm`, `one patch per sheet`, `one segment per sheet`, `not a tiling`, `do not tile`, `nothing to stitch`.
- **Négatif** : aucun résultat de distance inter-segments n'est *enregistré* nulle part (`closest pair|pairwise distance|distance between segments|distance between patches` → seulement du code d'algorithme).
- **Négatif** : tous les seuils de recouvrement du code sont en **voxels** (2,0), jamais en µm.

### Dépôts d'outils (sous-agent, citations décisives vérifiées par moi)
`windcheck` (restreint à `src/ bench/ docs/ engines/ tests/ reproduce/ case-studies/ README.md` — `data/` 1,3 Go et `out/` 2,6 Go exclus), `winding-ruler`, `winding-sync`, `tifxyz-doctor`, `tifxyz-surgeon`, `vesuvius-automesh`, `spiral-fitting`, `spiralcheck`, `scrollreading`, `slim-flatboi`, `khartes`, `ThaumatoAnakalyptor`, `Volumetric_Instance_to_Mesh`, `vesuvius-catalog`, `vesuvius-browser`, `vesuvius-py`, `herculaneum-scroll-tools`.
- Motifs : `cKDTree|KDTree|hausdorff|chamfer|point-to-point|point-to-surface|nearest neighbour` ; `same sheet|adjacent sheet|neighbouring sheet|inter-sheet|sheet spacing|different sheet|two sheets` ; `bounding box|bbox|AABB` croisé avec `insufficient|weak|misleading|proxy|cannot|naive|coarse` ; `micron|µm` ; `collision` ; `do not tile|only sample|one per sheet|nothing to stitch|no overlap`.

### Dépôts traités par moi seul
`volume-cartographer-schilling` (a le même prédicat `overlap()`, `core/src/Surface.cpp:1414`, et `apps/src/vc_seg_add_overlap.cpp` d'origine), `volume-cartographer-educelab` (`utils/src/MergePointSets.cpp` — fusion de nuages, `--overwrite-overlap`, pas de test de feuille), `scrollfiesta` (`src/split/{oracle,bridge_cut,overlap_sep}.md` : compteur de feuilles par lancer de rayons, `GAP_THRESHOLD = 8.0` voxels — discriminant même-feuille/feuilles-multiples mais **intra-composante**, pas entre segments publiés), `scrollreading`, `Hraun`, `Vesuvius-Grandprize-Winner`.

### Précision de périmètre importante
Les outils qui *auditent* un patch (`tifxyz-doctor`, `tifxyz-surgeon`) sont **100 % intra-patch** : vérifié sur leurs propres listes de contrôles (`tifxyz-doctor/README.md:29–59`, `tifxyz-surgeon/README.md:37–42`, plus `tifxyz-surgeon/README.md:203` « Nothing here reads the volume. Every judgement is about the surface's self-consistency »). Ils ne mesurent **pas** l'écart entre deux segments publiés, et je ne les compte donc pas comme antériorité pour la question 2.

---

## CE QUI RESTE NEUF

Trois choses, et elles sont plus étroites que la formulation actuelle de §5.7 :

1. **La mesure sur `PHerc1447`.** Aucun dépôt, aucune page, aucun papier ne rapporte l'écart par paires entre les 15 segments publiés de ce rouleau. Les mesures antérieures portent sur PHerc0172 (windcheck, 6 paires de windings), PHercParis4 (spiralcheck, 150 paires ; winding-sync, 4 paires) et Scroll 3 (automesh, 9 fenêtres). **`PHerc. 1447` n'apparaît même pas dans le papier de référence.**

2. **L'exhaustivité.** Les antérieurs sont soit un contrôle nul (150 paires échantillonnées), soit une porte retirée (`windcheck/docs/HISTORY.md:70,189` classe `bench/orphan_skip.py` dans « the proximity and self-gap era »), soit une validation à 9 fenêtres. **Personne n'a fait les 105 paires d'un rouleau, ni conclu quoi que ce soit sur la structure de couverture du corpus publié.** C'est la revendication défendable : *systématisation et complétude*, pas *idée* ni *méthode*.

3. **La formulation « un ensemble d'échantillons, une pièce par feuille ».** Confirmé absent des deux balayages : le corpus dit « sparse, scattered », « pieces with gaps », « places no patch ever reached » — jamais *une pièce par feuille*, qui est une affirmation plus forte et plus vérifiable.

⚠ **Ce qui n'est PAS défendable en l'état** : présenter « une boîte englobante ne distingue pas deux pièces d'une feuille de deux feuilles voisines ; le discriminant est l'écart médian point-à-point » comme le discriminant de l'article. C'est le comportement du code de référence (`QuadSurface.cpp:3108`), une limite écrite par `windcheck` (`PATCH-AUDIT.md:216`), et la méthode de `spiralcheck` (`real_overlap_check.py`) et d'`automesh` (`README.md:9`) — trois outils que l'article cite déjà nommément dans §2.3. Il faudrait le reformuler en « nous appliquons le discriminant établi par X, Y, Z à un corpus qu'ils n'ont pas couvert », et **répondre à la contre-position du §D** (aucun seuil fixe ne sépare les wraps, qui descendent à ~5 µm) avant que le seuil de 40 µm ne porte la conclusion.
