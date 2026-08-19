# Reprise de session — état au 2026-08-19

Document de passation. **À lire en entier avant de reprendre.**

---

## 1. ⭐⭐ L'OBJECTIF — et ce n'est pas le texte

> **Le but est le DÉROULEMENT, pas la lecture.** Traduire n'est pas notre métier.
> Repérer quelques lettres sert à **s'assurer que le rouleau assemblé et déroulé fait
> du sens** — l'encre est la **règle graduée**, pas l'ouvrage.
> *(cadrage de l'auteur, 2026-08-17)*

| famille | rôle |
|---|---|
| fusions, onde radiale, dépliage polaire, proximité géométrique, direction des fibres | **le travail** |
| détection d'encre, juge calibré, second rouleau | **l'instrument** |

⚠ Pousser l'AUC plus haut, chercher un meilleur détecteur d'encre ou faire transcrire
davantage **ne sert pas** l'objectif.

## 2. ⚠ CE QUI TOURNE (2026-08-19, fin de journée)

**Rien.** Toutes les campagnes ont rendu : celle des graines (12 rouleaux) et les six
variantes de `direction_fields`. ⚠ VSCode a été fermé pendant les dernières — **aucune
n'a été perdue**, elles avaient toutes fini leurs 118 générations. Vérifier l'**état des
fichiers** avant de conclure qu'un lot est mort : un `ps` vide ne dit rien de ce qui a
été écrit.

```bash
ps -eo etime,pcpu,cmd | grep -E "[z]arr_depth|[c]hamp_correction|[v]c_grow|[v]c_render"
```

⚠ **Juger sur un fichier de résultat, jamais sur une notification**, et **vérifier
l'horodatage d'un log avant d'en citer le verdict** — un log vieux de sept heures a déjà
été lu comme un résultat frais. ⚠ Python **bufferise** : lancer avec `python -u`.

⚠⚠ **`kill $!` sur un `nohup uv run … &` ne tue que le WRAPPER** ; le travailleur est un
petit-fils et il survit, en continuant d'écrire dans le `--out` qu'on croyait abandonné.
Payé **deux fois dans la même heure**. Tuer le petit-fils via `ps -eo pid,ppid,args`.

⚠ Pour libérer la machine : `kill -STOP` les calculs, tuer les `curl` — c'est la **bande
passante** qui fait bégayer un Zoom. Toutes les campagnes sont **reprenables** (un fichier
par segment).

## 2bis. ⭐ La liste de ce qui reste ouvert

**Trois batchs, tous clos** : [`13`](docs/13_batch_epuisement.md) *(fermer ce qui était
ouvert)*, [`18`](docs/18_batch_produire.md) *(produire, pas juger)*,
[`22`](docs/22_batch_repliquer.md) *(un résultat sur un corpus n'est pas un résultat)*.

⭐⭐ **Et le 22 a viré ailleurs qu'où il visait.** Il devait consolider la règle de `19` ;
il l'a **réfutée hors de Scroll 1**, puis a débouché sur autre chose : **VC3D est
construit**, la chaîne officielle est pilotable en ligne de commande, et
[`24`](docs/24_premiere_trace_rouleau_du_prix.md) a tracé un **rouleau du Grand Prize**.

⭐⭐ **Et le lot du 19 août après-midi a fermé T1**, avec deux corrections que la mesure a
imposées : [`25`](docs/25_une_graine_choisie_sur_la_planeite.md). Le critère de graine passe
sur la **planéité locale**, la campagne appariée sur **12 rouleaux du prix** donne
p = 0,0386 sur l'aire — et **zéro auto-intersection des deux côtés**, donc le « 240 → 0 »
de `24` est l'accident d'un seul rouleau. Le vrai coupable de `24` est ailleurs et il est
nommé : sa graine était dans un bloc **entièrement plein** (occupation 1,000), donc sans
géométrie à suivre.

> **Le prochain lot n'est plus un batch de mesure.** Il est décrit au §7.

## 3. Le projet

`~/LplVesuvius` — Vesuvius Challenge vu depuis Laplace. Contexte non versionné dans
`PRIVE.md` (gitignoré). **Budget disque** : 100 Go, ~52 Go utilisés.

⚠ Aucun remote git configuré. Ne jamais pousser.

### Ordre de lecture

| doc | contenu |
|---|---|
| `00` | point d'entrée : la chaîne, les acteurs, les prix |
| `01`–`05` | le goulot, l'inventaire, la reproduction `windcheck`, l'excision |
| **`06`** | **le carnet de mesures** — faites, en attente, écartées |
| `07` | la réparation ne déplace pas le défaut |
| `08`, `10` | ⭐ la passe d'encre : **AUC 0,925** sur un segment entier |
| `09` | juge par modèle : 3 juges mécaniques en échec, 1 calibré qui marche |
| **`11`** | ⭐ **onde radiale, dépliage polaire, fusions localisées en 3D, la dérive** |
| **`12`** | ⭐⭐ **la profondeur de surface : qualité de tracé SANS vérité terrain** — lire le §10 d'abord, l'instrument a été corrigé deux fois |
| **`13`** | **la liste du batch d'épuisement**, cochée au fur et à mesure |
| `14` | ⭐ la direction des fibres — ❌ **réfutée**, le signe s'inverse quand n monte |
| `16` | ⭐ quel rouleau du prix attaquer — `PHerc0358`, désigné par la mesure |
| `17` | ❌ le saut de spire par la phase — **échec définitif** (§10) |
| **`18`** | **le batch en cours** : produire, pas juger |
| **`15`** | ⭐ **ce qui est soumissionnable**, trié contre les critères écrits du concours |
| **`19`** | ⭐⭐ **la première règle qui CHANGE une décision** — p = 0,0005 contre 2000 permutations |
| **`20`** | ⭐⭐ **le champ de correction** : l'erreur d'une trace est structurée, et **translater ne la répare pas** |
| **`21`** | **le brouillon de la soumission**, résultats négatifs compris. ⚠ Ses chiffres sont gardés par `verifier_chiffres.py`, lancé dans `tools/temoins.sh` |
| `22` | le batch « répliquer » — clos, et il a réfuté ce qu'il devait consolider |
| `23` | ⭐ **l'inventaire des 13 rouleaux du prix** — 10 n'ont AUCUN segment |
| **`24`** | ⭐⭐ **la première trace d'un rouleau du prix**, condamnée par nos instruments avant le rendu. ⚠ Son §2 est **corrigé** : le verdict tient sur deux instruments, pas trois |
| **`25`** | ⭐⭐ **la graine choisie sur la planéité** — et la réplication sur 12 rouleaux qui a corrigé la revendication deux fois |
| **`26`** | ⭐⭐ **ce qui gouverne la trajectoire du traceur** — et les deux mécanismes qui ne la gouvernent pas, contrats dérivés et encodage mesuré |

## 4. L'outillage, et comment le relancer

```bash
./tools/temoins.sh                      # 79 contrôles hors ligne, tous verts
./tools/mirror_site.sh                  # miroir + contrôle de couverture
./tools/fetch_layers.sh <url> <dest> <largeur> <de> <a>   # couches, reprenable
./tools/ppm_to_tifxyz.py <in.ppm> <out.tifxyz>            # .ppm de VC -> tifxyz
./tools/survey_fusions.sh <out> <bandes> <par> <pas>      # fusions, niveau 2
./tools/bandes_niveau0.sh                                 # bandes niveau 0, hors site
./tools/fetch_traces.py <index.json> <corpus> <dest>      # traces tifxyz, SANS aws
./tools/lister_volumes_surface.sh <rouleau> <sortie>      # qui publie un volume Zarr
./tools/fetch_cartes_encre.sh <rouleau> <dest>            # cartes d'encre PUBLIEES
./tools/reprendre.sh                                      # degeler apres un kill -STOP
./tools/campagne_champ.sh <rouleau> <motif> <voxel_um>    # champ de correction, REPRENABLE
./tools/campagne_dense.sh <rouleau> <motif> <dest>        # part de matiere, 392 points
./tools/etat_rouleaux_prix.sh                             # ⭐ l'inventaire des 13

cd experiments   # geometrie
uv run python src/excision/radial.py {centre|compter|profil|deplier|axe} …
uv run python src/excision/fusions.py {controle|ecarts-controle|densite|ecarts} …
uv run python src/excision/fusion_scan.py …               # persistance en z
uv run python src/excision/track_z.py <scans.json> …      # appariement PREDICTIF
uv run python src/excision/baseline_sweep.py <traces> <out.jsonl>   # references locales
uv run python src/excision/variant_correlate.py <sweep> <index.json>
uv run python src/excision/pyramid.py <volume>            # separabilite par niveau
uv run python src/excision/sensibilite_centre.py <nom> <volume>    # l'invariant tient-il ?
uv run python src/excision/shape.py {degradation|ellipticite} <volume>
uv run python -m excision.proximity <mesh.tifxyz> --json

cd inference_xpu # encre
uv run python src/infer_ink.py <layers> --model … --device xpu --out out.npy
uv run python ../analysis/src/{evaluate_segment,render_segment,structure}.py …
uv run python ../analysis/src/judge_api.py --list-models
uv run python ../analysis/src/judge_api.py <pred.npy> --bands-only   # sans cle
uv run python ../analysis/src/depth_profile.py <couches…> --grid     # qualite de trace
uv run python ../analysis/src/zarr_depth.py <cle .zarr> --courbe --fils 16   # ⭐ x8,35
uv run python ../analysis/src/fiber_orientation.py <cle .zarr>       # ⭐ fibres
uv run python ../analysis/src/croiser_instruments.py <index.json> <mesures.json>
uv run python ../analysis/src/champ_correction.py <cle .zarr> --voxel-um 2.4  # ⭐⭐ REPARABLE ?
uv run python ../analysis/src/croiser_encre.py <profondeur.json> <cartes/>    # ⭐⭐ la DECISION
uv run python ../analysis/src/table_champ.py <champs/> --encre <rapport.json>
uv run python ../analysis/src/resolution_phase.py <saut_spire/>
uv run python ../analysis/src/trouver_graine.py <prediction .zarr>    # ⭐ graine A DISTANCE
uv run python ../analysis/src/regarder_rendu.py <render/> --png-dir …  # apercus + stats
uv run python ../analysis/src/tester_prediction_50um.py <rapport.json>
uv run python ../analysis/src/robustesse_material.py <A> <B>
uv run python ../analysis/src/verifier_chiffres.py <docs…>            # fraicheur
uv run python ../analysis/src/compare_maps.py <a.npy> <b.npy>
uv run python ../analysis/src/proximity_vs_ink.py <mesh> <pred> <labels>
```

### ⭐⭐ VC3D — la chaîne de production, construite le 2026-08-19

**45 outils en ligne de commande** sous `/usr/local/bin/vc_*`, plus le GUI `VC3D`.
Construits depuis `repos/villa/volume-cartographer/build_from_src_debian.sh`
(⚠ demande `sudo`, 17 paquets).

```bash
vc_grow_seg_from_seed -v <zarr|URL> -t <dir> -p seed.json -s <x> <y> <z>
vc_tifxyz_selfcross --surface <tifxyz> -o rapport.json    # auto-intersections
vc_flatten -i <tifxyz> -o <tifxyz_flat>
vc_render_tifxyz -v <cache> --remote-url <URL> --scale 1 -g 0 \
    -s <flat> --tif-output <dir> -n 21 --auto-crop
```

⭐ **`-v` accepte `https://` pour le traçage** : le volume de 893 Go n'est **jamais**
téléchargé. ⚠ Mais `vc_render_tifxyz` veut un chemin **local** en `-v` — c'est
`--remote-url` qui fait le streaming, et `-v` désigne alors le **cache**.

⚠⚠ **Trois pièges silencieux, chacun ressemblant à un succès** :
1. **`voxelsize` vaut 0 par défaut** dans `seed.json` → l'aire en cm² est nulle *par
   construction* et toute surface est rejetée (« area 0 below min_area_cm ») ;
2. **`--segment-name` fait écrire DANS `-t`** — il tente de remplacer le répertoire
   courant par lui-même ;
3. **`[tif] all slices exist, skipping`** saute par-dessus les fichiers **tronqués** d'un
   run tué. Effacer le répertoire de sortie avant de relancer.

### Matériel

| voie | verdict |
|---|---|
| **iGPU Arc via `torch 2.9.1+xpu`** | ✅ ×4,5, sortie identique au CPU à 4,9e-6 |
| NPU | ❌ non exposé à WSL2 |
| OpenVINO | ❌ ne convertit pas ce modèle |

⚠ `sudo apt install intel-opencl-icd libze-intel-gpu1 libze1`. Le nom
`intel-level-zero-gpu` **n'existe pas** sous Ubuntu 26.04 et apt annule **toute** la
transaction sur un nom inconnu.

## 5. Les résultats acquis

### Géométrie — le travail

1. **Onde radiale** : **176 spires** (max sur 20 tranches), rayon 25,1 mm →
   **~13,9 m** de papyrus. ⚠ Borne **inférieure** : deux feuilles fondues comptent
   pour une. Longueur **axiale** du rouleau : 164 mm ; diamètre 48 mm.
2. **Invariant fort** : rayon / feuilles = **142,8 µm, cv 1,8 %** sur toute la hauteur,
   alors que chaque grandeur varie de 4-5 %. Profil en **U** (25,1 → 21,3 → 24,3 mm).
3. **Le rouleau est écrasé** : rapport d'axes **1,26 à 1,57**, le plus au milieu.
   ⚠ Le périmètre perd quand même 9 % — écrasement **et** perte, aucune écartée.
4. **Fusions localisées en 3D** : 4 candidats vers 17 mm, persistants à **p = 0,0001**
   (coupes à 0,8 mm), et **18 %** de colocation sur le rouleau entier par bandes.
   Le défaut **migre** : +2,4 mm de rayon et +38° sur 2,4 mm de hauteur.
   ⚠ L'inclinaison de l'axe est **écartée** — elle joue en sens opposé (−0,47 mm).
5. **Le niveau 2 de la pyramide suffit** : **89 %** des murs pour **33 Gio au lieu de
   2100**. Falaise entre les niveaux 2 et 3. ⚠ C'est un **crible** : les deux niveaux
   ne trouvent pas les mêmes sites (fond 10,3 % contre 6,6 %), donc tout candidat se
   confirme au niveau 0.
6. **Théorie du dommage de l'auteur** : à moitié. Cœur dégradé (−20 %), extérieur à
   peine (−5 à 8 %). **Pas un U.** ⚠ Bonne nouvelle : ce qu'on a perdu du **début**
   des textes est moindre que craint.

7. ⭐ **Le défaut DÉRIVE, et le crible ne peut pas le voir** (`11` §11). Appariement
    **prédictif** — même tolérance, seul le *centre* de la fenêtre devient une
    prédiction. Le site du §7 forme une piste de **5 coupes traversant 4,75 mm de
    rayon** (dérive **1,50 mm/mm**) contre 3 coupes / 1,42 mm à fenêtre fixe,
    **p = 0,0010** (0,005 après Bonferroni). ⚠⚠ Le niveau 2 est **aveugle** à ce site :
    même plage de z, niveau 0 à 77–88 % du tour, niveau 2 rien entre 74 % et 88 %. Les
    **18 %** de colocation du balayage portent sur une **autre population**.
8. ⚠ **La migration n'est PAS la règle.** Une seconde bande au niveau 0 (z 3188→3988)
    a ses sites **stationnaires** : piste la plus longue plate à 0,47 mm, p = 0,74. Le
    site à z ≈ 7000 est particulier.
9. ⭐⭐ **Un chunk Zarr = une colonne de profondeur entière, pour 1,78 Mo et 1,03 s.**
   Les volumes de surface sont publiés en OME-Zarr non compressé, chunks
   `[109, 128, 128]`. Une campagne qui demandait **32 Go par segment** en demande
   quelques mégaoctets. Conséquences : **81 segments** de Scroll 1 avec volume de
   surface, **80 avec une carte d'encre publiée** (récupérées — le résultat sans lancer
   43 min d'inférence), **3 campagnes** de scan (45,5 / 2,4 / 1,13 µm) dont 37 segments
   les ont toutes, et **aucune troncature** du profil. Ça débloque `12` §5 *et* `06` §3.6.

10. ⭐⭐ **La profondeur de surface** (`12`) — une mesure de **qualité de tracé** qui ne
   demande **ni vérité terrain, ni modèle, ni juge**, et se calcule **avant** toute
   inférence. La grandeur est l'**écart entre le pic d'intensité et la surface tracée**,
   en µm : `20231022170901` **24 µm**, `20230909121925` (AUC 0,925) **32 µm**,
   Scroll 4 **63 µm** (p90 **134**). ⚠ Ces trois chiffres sont des **bornes
   inférieures** — la fenêtre 15–40 tronque, et 37 % des fenêtres de Scroll 4 y sont
   écrêtées. Sur la pile complète de Scroll 4, **61 %** des fenêtres ont leur pic **à un
   bord** : la feuille est hors du volume de surface.
   ⚠⚠ **L'instrument a été corrigé DEUX fois le même jour** (`12` §10), et aucun défaut
   n'a été trouvé en relisant : (a) le **contraste** ne localise pas la matière — sur un
   volume à 2,4 µm sa courbe est un **U**, maximal aux deux bords et minimal dans la
   feuille, parce qu'il suit les interfaces et le bruit ; l'**intensité** localise ;
   (b) « tiers central » se rapportait à la **fenêtre lue**, qui n'est pas centrée sur
   la couche tracée — d'où l'écart en µm.
   ⚠ **Correction d'une de mes conclusions du même jour** : j'avais annoncé « l'écart
   vaut une épaisseur de feuille, donc saut de spire » en important le pas de PHerc0172
   vers PHerc1667. Piège nº 6. La pile complète le dément : les deux blocs sont séparés
   de plus de 64 voxels.

### Encre — l'instrument

11. **AUC 0,925** sur 44,7 M de pixels d'un segment entier, contrôle mélangé à **0,500**.
   9,2 cm de grec lisible. ⚠ Orientation de lecture = **rotation 270°**.
12. **Juge de langue calibré** : **15/16, zéro fabrication**, lisibilité séparant sans
   chevauchement le vierge (0–1) du texte (3–6). Protocole : `data/juge/PROTOCOLE.md`.

13. ⚠⚠ **Rien de lisible sur Scroll 4, et la cause est EN AMONT du modèle** (`09` §12,
   `12`). Deux passes complètes (couches 15–40 puis 0–25, ~43 min chacune). Le juge
   calibré : lisibilité **1–3** sur la première, **refus de tous les panneaux** sur la
   seconde, quand le calibrage sépare vierge **0–1** de texte **3–6**. Recentrer les
   couches n'a rien sauvé (les deux cartes : rho **+0,700**, **88,7 %** d'accord).
   ⚠⚠ Et ça ne pouvait pas marcher : sur **61 %** du segment le cœur de matière est
   **hors des 65 couches**. On ne détecte pas d'encre sur une surface que le volume de
   surface ne contient pas. ⚠ Limite du protocole mesurée au passage : **la lecture
   d'un panneau dépend de son voisin** (même image, 1 puis 2 puis 0 glyphes, à
   température zéro).

### 2026-08-19 — de juger à décider

17. ⭐⭐ **La première règle qui change une décision** (`19`). Écarter les **20 %** de
   segments dont le volume de surface porte le moins de matière (`avec_matiere`) fait
   monter le contraste d'encre médian du corpus de **+0,381**, contre **2000
   permutations** de même effectif : **p = 0,0005**. Cible = les **cartes d'encre
   publiées**, donc la sortie d'un **autre** pipeline. Coût : **36 requêtes** par segment,
   **avant** toute inférence.
   ⭐ Ce qui la défend est sa **forme** : un plateau contigu **15–25 %**, encadré par 5 %
   qui ne fait rien (p = 0,054) et 30 % qui se dégrade. Un réglage sur-ajusté ferait un
   **pic** — même critère que le seuil d'un tiers de `07` §8.
   ⚠⚠ Le **confond de taille était réel** (emprise ↔ écart +0,384, emprise ↔ encre
   +0,463) et la corrélation **partielle le RENFORCE** au lieu de le dissoudre
   (−0,315 → **−0,382**, p = 0,0005). C'est le contraire d'un effet de taille.
   ⚠ Confond non levé, et il faut le dire : une carte vide peut vouloir dire « la trace a
   raté » **ou** « ce papyrus est vierge ». C'est un **tri de corpus**, pas un diagnostic.
   ⚠⚠ **ET LA RÉPLICATION ÉCHOUE SUR SCROLL 5** (`19` §11) : rho **−0,217** (p = 0,12),
   décision p = 0,84. Deux mesures qualifient ce zéro. **(a)** La cible y est plate —
   contraste sur un facteur 1,25 contre 5,1 sur Scroll 1, étendue relative **4,6× plus
   petite** — donc le test est **non concluant**, pas réfutant. **(b)** Et sur Scroll 1 la
   règle sépare une **CLASSE**, pas un gradient : retirer les 16 segments sous un contraste
   de 3,0 fait tomber rho de **+0,539 à +0,190 (p = 0,13, ns)**. ⚠⚠ **Et le test apparié a réfuté l'explication (a)** (`19` §12) : PHerc0139, à la **même**
   résolution que Scroll 1 et avec une étendue **plus grande** (1,628 contre 1,008), rend
   quand même **−0,229**. L'effet de plancher couvrait un corpus sur trois. **La règle est
   une propriété du corpus publié de Scroll 1, pas du problème** — elle y reste solide,
   c'est sa PORTÉE qui tombe.
   ⭐ **Robustesse vérifiée** (`19` §10) : re-mesuré à **5,4× la densité de sondage**
   (72 → 392 fenêtres), l'accord des classements vaut **+0,841** (témoin 0,223) et le
   **plateau 15–25 % survit intact**. ⚠⚠ Un premier contrôle avait conclu l'inverse
   (+0,280) — il comparait deux **grandeurs différentes**, et j'ai passé une heure à
   affaiblir un résultat juste. **La prudence n'est pas une méthode.**

18. ⭐⭐ **Le champ de correction** (`20`) : l'erreur d'une trace est **structurée** —
   **150 segments sur 152**, sur **trois** rouleaux, battent leur propre témoin de mélange
   (80/80, 19/19, 51/53).
   ⭐⭐ Et le chiffre qui décide de la production : une **translation** du maillage
   n'enlèverait que **21,7 / 35,3 / 28,6 %** de l'erreur (Scroll 1 / 4 / 5). Le bon remède
   est un **gauchissement**, pas une translation.
   ⚠ Un **seul** segment de Scroll 5 rendait 0,67 et j'avais restreint la conclusion à
   deux rouleaux ; les 53 rendent 28,6 %. **Une contre-indication vue sur un point a
   fondu** — la règle « n = 1 n'est pas un résultat » vaut dans les deux sens.
   ⚠ Saut de feuille : **1/80** sur Scroll 1 et **0/53** sur Scroll 5, chacun contre le pas
   mesuré **sur ce rouleau-là**.
   ⚠ Le champ **ne prédit pas** l'encre (rho −0,023 à n = 80, où 0,31 est détectable)
   mais **prédit les croisements** (résiduel **+0,428**, p = 0,0012, n = 54) : un défaut
   de la **TRACE**, pas du **RÉSULTAT** — mesuré des deux côtés.
   ⚠⚠ **Piège nº 6 commis puis attrapé dans la même séance** : j'ai appliqué le pas de
   PHerc0172 (142,8 µm) à des segments de PHercParis4 (**172,8 µm** mesuré), ce qui
   gonflait le compte de sauts de feuille d'un facteur 4. `--pas-um` **n'a plus de
   défaut** et le compte n'est pas rendu sans lui.

19. ⭐ **L'échelle est réelle, pas promise** : `--fils` sur le lecteur Zarr donne **×8,35**
   mesuré (21,80 s → 2,61 s), sortie **bit pour bit identique**. Le modèle de coût
   divisait par 16 — corrigé : les **800 rouleaux de la villa** se jugent en **0,9 h**,
   pas 0,5 h. Un modèle de coût qui se flatte n'est pas un modèle de coût.

19bis. ⚠⚠ **La prédiction des 50 µm de `12` est testée, et elle se scinde en trois**
   (`12` §13). Le **sens tient** (4,93 contre 5,91, p = 0,017). Le **seuil tombe** : au
   balayage, 60 µm est pire que 50 **et** que 70 — une courbe qui monte, redescend et
   remonte n'a pas de point de coupure, c'est le contraire du plateau de `07` §8. Et la
   **forme forte est réfutée** : l'écart médian du corpus vaut **67,2 µm**, donc le seuil
   condamnerait 64 segments sur 80 qui portent visiblement de l'encre, et **8 %** seulement
   de ceux qui le dépassent tombent dans le premier décile contre 10 % attendus au hasard.

19ter. ✅ **L'invariant tient à un centre faux** (`11` §12) : déplacer le centre de
   **3,16 mm** — 22 écarts inter-feuilles — bouge l'invariant de **1,75 %** au maximum,
   soit **sous** le cv de 1,8 %. `06` §2.3 est donc clos **sans ombilic**, lequel n'est de
   toute façon pas publié (zéro occurrence sur 4 corpus).
   ⚠⚠ **Deux artefacts traversés avant d'y arriver, et ils se ressemblent** : au niveau 2
   les seuils de comptage trouvaient 42 feuilles au lieu de 176 (piège nº 1) ; à **3
   tranches** le bruit d'échantillonnage produisait **5,65 %** et une « marche » nette dès
   la plus petite perturbation, avec une explication toute prête. À 6 tranches, plus rien.
   **Un effet réel ne fond pas quand on l'échantillonne mieux.**

20. ❌ **Le saut de spire par la phase est mort définitivement** (`17` §10). Le volume
   `cos` n'est publié qu'aux niveaux **3, 4, 5** — le niveau 3 EST le plus fin, donc
   « refaire au niveau 0 » n'avait pas d'objet. Et la quantification n'écrase rien :
   marche médiane **12,2 / 255**, **0 trace sur 38** à médiane nulle.

### 2026-08-19 (fin) — de juger à produire

21. ⚠⚠ **LA RÈGLE DE `19` NE RÉPLIQUE PAS** (`19` §11–§12). Testée sur **110 segments** de
   trois autres rouleaux, mêmes outils, même définition :

   | corpus | n | voxel | étendue de la cible | rho |
   |---|---:|---:|---:|---:|
   | **Scroll 1** | 80 | 2,4 µm | 1,008 | **+0,539** |
   | **PHerc0139** | 38 | **2,399 µm** | **1,628** | **−0,229** |
   | PHerc1667 | 19 | 2,399 µm | 0,720 | +0,425 |
   | PHerc0172 | 53 | 7,91 µm | 0,220 | −0,217 |

   ⚠ Ma première explication (effet de plancher) couvrait **un corpus sur trois** :
   PHerc0139 est à la même résolution que Scroll 1, a une étendue **plus grande**, et rend
   le signe opposé. **La règle est une propriété du corpus publié de Scroll 1.**
   ⚠⚠ Et sur Scroll 1 même, elle sépare une **CLASSE** et non un gradient : retirer les 16
   segments quasi vierges fait tomber rho de **+0,539 à +0,190 (p = 0,13, ns)**.
   ⭐ La revendication corrigée est **meilleure** : « je repère une classe d'échecs avant
   que vous payiez l'inférence » est le goulot que le concours nomme mot pour mot.

22. ⭐⭐ **UNE TRACE PRODUITE SUR UN ROULEAU DU GRAND PRIZE** (`24`). `PHerc0358`, l'un des
   **dix** des treize sans aucun segment publié : **8,48 cm²** en **13,9 s** de calcul, le
   volume de 893 Go n'étant jamais téléchargé. Puis aplati et rendu, 29,4 × 29,2 mm.
   ⚠ **La trace est mauvaise** — elle coupe à travers les spires. Ce qui compte est
   **comment on le sait** : trois mesures indépendantes, **deux avant l'image**.
   240 auto-intersections à pénétration 200 µm (> 1 écart inter-feuilles) ; **64 %** des
   fenêtres piquant au bord de la pile, distribution **bimodale** (15 à la couche 0, 9 à
   la 20, une au milieu) — la signature d'une surface posée **entre** deux feuilles.
   ⭐ **C'est la validation qui manquait** : les instruments jugeaient le travail des
   autres ; ils viennent de condamner le nôtre, en 0,05 s, avant le rendu.
   ⚠ Cause identifiée : `direction_fields` absent, donc **aucune information
   d'orientation** — et une surface qui coupe les spires satisfait la prédiction seuillée
   autant qu'une qui en suit une.

23. ⭐ **L'inventaire des treize** (`23`) : **dix rouleaux n'ont AUCUN segment**, et les
   treize publient tous volume + prédiction de surface + `normal-grids` + `lasagna`.
   `PHerc1447` en a 16, `PHerc0800` 6, `PHerc1203` 1. Et `PHerc1447` est le **seul** à
   publier des volumes de surface (4, à 8,64 µm) : nos instruments y trouvent
   immédiatement un segment **hors du papyrus** (9 % de matière contre 51–59 %, 17,4 % au
   bord, écart +86 µm).

24. ⚠ **La migration est l'exception** (`11` §13) : 2 bandes sur 6, Fisher p = 0,079 — et
   le **témoin positif** (bande E, autour du site connu) ressort à p = 0,0285 avec une
   dérive de 1,20 mm/mm. La méthode retrouve la migration là où elle existe, donc les
   quatre bandes muettes sont de **vrais** négatifs.

25. ⚠⚠ **La prédiction des 50 µm est testée et scindée en trois** (`12` §13) : le **sens**
   tient (4,93 contre 5,91, p = 0,017), le **seuil** tombe (60 µm est pire que 50 *et* que
   70 — une courbe qui monte, redescend et remonte n'a pas de point de coupure), et la
   **forme forte est réfutée** (l'écart médian du corpus vaut 67,2 µm, donc le seuil
   condamnerait 64 segments sur 80 qui portent visiblement de l'encre).

### La jonction, et le domaine de définition

14. ⚠⚠ **La métrique de proximité a un DOMAINE DE DÉFINITION** (`07` §7). Elle exige une
   trace qui **repasse au-dessus d'elle-même** : sur les 53 traces de Scroll 5, **44
   rendent zéro cellule**, et la coupure est exactement à **un tour** (mesurées
   2,99–9,07, écartées 0,50–**1,00**). Ce n'est pas « moins bon sur un second rouleau »,
   c'est **inapplicable** à cette population. ⚠ Les 9 mesurables sont neuf morceaux du
   **même** segment : n = 1. ⭐ Le vrai second rouleau est PHerc0139 / PHerc1667 /
   PHerc0814, majoritairement au-dessus d'un tour — traces récupérées.
15. ✅ **Le seuil d'un tiers de `07` : ni arbitraire, ni supprimable** (`07` §8). Aucune
   grandeur sans seuil ne l'égale (**+0,340** et **−0,512** contre **+0,769**) — le
   signal est dans la queue extrême. Ce qui le défend est un **plateau** : rho 0,759 à
   0,779 de 0,15 à 0,40, un facteur **2,7**, puis effondrement. Un réglage sur-ajusté
   ferait un **pic**.

16. ⚠⚠ **La proximité géométrique ne prédit PAS la lisibilité.** rho **+0,019** à
   n = 89 tuiles (contrôle plat), et à ce n la mesure détecterait un rho de 0,3.
   La métrique de `07` corrèle avec les croisements publiés (+0,77) mais pas avec le
   résultat : **elle mesure un défaut de la TRACE, pas du RÉSULTAT**. Elle reste un
   contrôle qualité de trace bon marché ; elle n'est pas un argument sur le rendu.
   ⚠ Une seule trace — la seule qui ait maillage **et** encre.

## 6. ⚠ Le cap n'est PAS franchi

> **On ne publie rien sans une passe complète — rouleau déroulé, texte extrait, soumis
> à un expert qui dise si ça fait sens — et sur plusieurs rouleaux.**

Trois juges mécaniques ont échoué : Kraken (aucun modèle entraîné sur papyri), score
structurel sur région, score structurel sur segment entier. ⚠ La dernière cause est
définitive : **ce type de segment ne porte que 4 à 5 lignes de texte**, et les glyphes
**fusionnent** au seuil du modèle. Le juge calibré de `09` est le seul disponible.

## 7. ⏳ CE QUI RESTE — et le prochain lot n'est plus une mesure

⭐⭐ **Le cadrage a changé le 2026-08-19.** Objectif de l'auteur : *tout publiable pour le
31 août, les confirmations viennent après*. Et la lecture de la page des prix a corrigé la
cible — le pool ouvert fait **2 140 000 $** et le Grand Prize n'est pas le seul lot :

| prix | montant | ce qu'il faut | échéance |
|---|---:|---|---|
| **First Letters** | **50 000 $ × 10 rouleaux** | **10 lettres dans UNE zone de 4 cm²** | 25 juin 2027 |
| **Titre de PHerc. Paris 4** | **50 000 $** | l'image du titre, lisible par leurs papyrologues | 25 juin 2027 |
| Progress Prize | 20 000 $ / mois | la meilleure soumission du mois | **31 août** |
| Grand Prize | 800 000 $ | **100 %** du recto, intégré VC3D, ≤ 8 h d'annotation | 25 juin 2027 |

> ⭐ *« Sometimes ink is visible **directly in the flattened render, with no model at all**…
> **that by itself qualifies for the prize**. »* — donc l'étape suivante n'est pas
> d'entraîner, c'est de **regarder**.

| # | quoi | blocage |
|---|---|---|
| ~~T1~~ | ~~faire suivre une feuille au traceur~~ | ✅ **fermé le 2026-08-19** — mais en **deux moitiés**, et une seule est faite (`25`). *Où l'on part* est réglé ; *comment on avance* ne l'est pas |
| ~~T1b~~ | ~~brancher `direction_fields`~~ | ✅ **fait, et le résultat est un NÉGATIF** (`26`) : le contrat est dérivé, l'encodage mesuré sur 3 rouleaux, le champ se charge — et la croissance est **identique au centième**, même avec les axes délibérément permutés. Il n'agit que dans l'étape finale, où il fait empirer |
| ~~T1c~~ | ~~brancher `NormalGridVolume`~~ | ✅ **fait — second négatif** (`26` §7). La clé est **`normal_grid_path`** et elle est bien lue ; avec 1,53 Go de vraies grilles la vitesse tombe **×29** et la trajectoire ne bouge pas d'un centième **sur les 118 générations** ; l'étape finale, elle, rend **112 139** auto-intersections contre zéro. ⭐ Raison : les `.normal-grids` sont **dérivées de la prédiction que le traceur suit déjà** — les lui rendre est une tautologie |
| ~~T1d~~ | ~~régler `direction_weight`~~ | ✅ fait, jusqu'à ×100 : rien ne bouge (`26` §3) |
| ~~T1e~~ | ~~générer des grilles depuis le volume masqué~~ | ✅ **fait — troisième négatif** (`26` §8). 3,44 Go de volume en boîte à coordonnées absolues, 36 dalles sur 238, 4 608 tranches de grilles : **×17 de ralentissement, trajectoire identique**. Une information qui ne vient PAS de la prédiction ne change pas plus la trajectoire |
| **T1f** ⭐ | ce qui reste : la trajectoire ne répond qu'à **`step_size`** et à la **prédiction**. Explorer `step_size`, ou attaquer la prédiction elle-même | ⚠ ne PAS re-tenter les champs et les grilles : trois négatifs mesurés, chacun avec son contrôle |
| — | ⭐⭐ **le bilan qui cadre la suite** (`26` §8) : la trajectoire ne répond qu'à `step_size` et à la prédiction. Ni les champs, ni les grilles, ni les poids ne la déplacent — **la graine reste le seul levier mesuré** |
| ~~T2~~ | ~~rejouer la boucle sur d'autres rouleaux~~ | ✅ **fait** — `tools/campagne_graines.sh`, 12 rouleaux, appariée, reprenable |
| **T3** ⭐ | le **titre de Scroll 1** — *« looking somewhere new »* | c'est un problème de **recherche** sur le corpus où tous nos instruments marchent |
| T4 | finir et envoyer la soumission Progress Prize | ⏳ le texte existe (`21`), les chiffres sont gardés, il reste à publier le dépôt et à joindre les figures |
| R2 | exporter le champ de correction en coordonnées de fenêtre | — |
| — | le **pas inter-feuilles de PHerc1667** | ⚠ aucune prédiction de surface publiée pour ce rouleau : on ne juge pas ses sauts de feuille |
| — | le trend **position dans le rouleau** ↔ résiduel | ⚠ **NON établi** : trois corpus, trois motifs différents |

## 7bis. ⭐ T1 — ce qui a été fait, et ce qui reste (mis à jour le 2026-08-19)

> ✅ **La moitié « où l'on part » est faite** : `analysis/src/trouver_graine.py` classe sur
> la planéité locale, `tracecheck.py --seed` la publie, et la campagne appariée sur
> 12 rouleaux la valide (`25`). ⚠ **La moitié « comment on avance » ne l'est pas** — voir
> T1b. Ce qui suit est le contexte d'origine, gardé parce qu'il reste exact.

### Le contexte d'origine

**L'état exact** : la chaîne tourne de bout en bout (`docs/24`), les artefacts sont dans
[`artefacts/PHerc0358/`](artefacts/PHerc0358/) (2,2 Mo, dont le maillage et les paramètres
qui marchent), et **le seul défaut connu est que le traceur n'a aucune information
d'orientation**.

### Ce qui est établi et n'est pas à refaire

| fait | où |
|---|---|
| VC3D et ses 44 outils CLI sont installés sous `/usr/local/bin/` | §4 |
| `vc_grow_seg_from_seed -v` accepte `https://` — le volume n'est jamais téléchargé | `24` §1 |
| `seed.json` **doit** porter `"voxelsize"`, sinon tout est rejeté à 0 cm² | `24` §1 |
| la graine `1544 1544 7768` (ordre **x y z**) donne 8,48 cm² en 13,9 s | `artefacts/PHerc0358/` |
| la trace obtenue **coupe les spires** — 240 auto-intersections, 64 % de pics au bord | `24` §2 |
| `PHerc0358` est le rouleau **le moins difficile** des treize | `16` |
| **dix** rouleaux sur treize n'ont aucun segment | `23` |

### Les trois pistes, dans l'ordre du moins cher

1. ⭐ **Une graine choisie sur la PLANÉITÉ locale**, pas sur la valeur de voisinage.
   `analysis/src/trouver_graine.py` classe aujourd'hui par la moyenne d'un cube 5³ — ce qui
   trouve « beaucoup de surface », y compris une **jonction** entre spires. Ce qu'il faut
   est un endroit où la prédiction forme un **plan** : mesurer l'anisotropie locale (le
   tenseur de structure de `analysis/src/fiber_orientation.py` sait déjà le faire) et
   retenir les points les plus plans. **Aucune donnée nouvelle à télécharger.**
2. **`step_size` réduit** (défaut 20) : moins de liberté par pas, donc moins de chances de
   sauter. Un essai coûte ~15 min.
3. **`direction_fields`**. ⚠ Deux obstacles vérifiés : le paramètre attend un chemin
   **local** (`std::filesystem::path`, pas d'URL) et la disposition `<zarr>/{x,y,z}/<niveau>`,
   alors que les `normal-grids` publiées (182 Mo) sont en `xy/ xz/ yz/`. Il faut soit les
   convertir, soit les régénérer avec `vc_gen_normalgrids`, qui est installé.

### La boucle complète, une fois une trace obtenue

```bash
cd ~/LplVesuvius/data/trace/PHerc0358
S=".../surfaces/20250821151737-surface-...-th0.2.zarr"     # prediction
V=".../volumes/20250821151737-9.362um-1.2m-113keV-masked.zarr"
vc_grow_seg_from_seed -v "$S" -t . -p seed.json -s <x> <y> <z>
vc_tifxyz_selfcross --surface auto_grown_* -o selfcross.json   # ⚠ JUGER AVANT DE RENDRE
vc_flatten -i auto_grown_* -o flat
rm -rf render && vc_render_tifxyz -v cache_vol --remote-url "$V" --scale 1 -g 0 \
    -s flat --tif-output render -n 21 --slice-step 1 --auto-crop
cd ~/LplVesuvius/inference_xpu
uv run python ../analysis/src/depth_profile.py ../data/trace/PHerc0358/render \
    --grid --step 400 --traced-layer 10 --voxel-um 9.362
uv run python ../analysis/src/regarder_rendu.py ../data/trace/PHerc0358/render --png-dir ../data/trace/PHerc0358/png
```

⭐ **Le critère de succès est mesurable avant de regarder** : une bonne trace doit rendre
la part de pics **au bord** BASSE et le pic **centré**. La mauvaise trace de `24` donne
**64 % au bord, 16 % au centre, distribution bimodale**. C'est le nombre à faire descendre.

⚠ Et le but n'est que **4 cm²** avec 10 lettres — la trace ratée en faisait déjà 8,48.

## 8. ⚠ Les pièges payés, à ne pas repayer

**Mesure**
1. **Un seuil calé sur le niveau 0 ne se transporte pas** à une résolution réduite —
   réduire *moyenne* les voxels et remonte le fond. (« 53 feuilles au niveau 1 ».)
2. **Une valeur identique partout** = saturation contre sa propre borne. (Axe long à
   22,7 mm sur les 8 coupes.)
3. **Comparer une grandeur à elle-même.** (Mon « périmètre » valait 2π × rayon moyen.)
4. **Échantillonner à l'échelle de l'objet** et non de la structure cherchée : coupes
   à 22 mm pour un défaut millimétrique → verdict inversé.
5. **Décimer mange la queue** : −60 % du signal, parce qu'il *est* dans la queue.
6. **Un chiffre emprunté n'est pas une mesure** (« 300 µm entre spires »).
7. ⚠⚠ **Une référence locale doit être LARGE là où l'anomalie est PETITE.** Une boule
   3D autour d'un site de croisement est pleine de ce site : l'anomalie normalise sa
   propre référence. Mesuré : boule/bande = **1,001** partout, **0,766** aux cellules
   signalées, 43 traces sur 45, Wilcoxon **p = 1,4e-09** (`07` §6).
8. **Un seuil calibré sur un segment ne se transporte pas** : `TEXT_BANDS`/`BLANK_BANDS`
   sont des lignes mesurées sur `20230909121925`. Ailleurs, `--auto-bands`.
9. ⚠ **Un « témoin » où le détecteur trouve du signal n'est pas un témoin.** Refuser
   d'en rendre plutôt que d'en rendre de faux (`--blank-ceiling`).

**Outillage**
9bis. ⚠⚠ **`pgrep -x <nom>` échoue en silence au-delà de 15 caractères.** Linux tronque
    `comm` à 15 octets, donc `pgrep -x vc_render_tifxyz` ne matche **jamais** — et une
    boucle d'attente bâtie dessus sort **immédiatement**. Symptôme : on lit un TIFF dont
    l'IFD vaut `0x00000000`, c'est-à-dire un rendu à moitié écrit qui ressemble à un rendu
    fini. Attendre **par PID** (`while kill -0 $PID`), ou matcher le nom tronqué.
9ter. ⚠⚠ **Un argmax sur un échantillon nombreux sature contre la borne du score.** Le
    maximum de 13 824 blocs pour un score borné par 1 vaut ~1 quel que soit le terrain.
    C'est le piège nº 2 à un étage de plus, et je l'ai écrit **dans le fichier qui
    documentait déjà le piège**. Classer sur une **moyenne de voisinage**, pas sur un max.
9quater. ⚠⚠ **Une fenêtre plus étroite que la structure mesurée ne peut rien voir.** 21
    couches à 9,362 µm valent ±94 µm, soit une **demi**-distance inter-feuilles : le profil
    est plat à 1,5 %, et l'argmax d'un profil plat sort **aux deux bords**, ce qui imite
    une bimodalité. Vérifier l'**amplitude** avant de lire une position de pic.
9quinquies. ⚠⚠ **Un entier nu dans une recherche littérale ne peut pas être absent.**
    `verifier_chiffres` cherchait « 80 » et « 10 » dans des documents en prose : trouvés
    toujours, donc contrôles incapables d'échouer — **deux entrées antérieures** étaient
    concernées. Un chiffre se garde **avec son contexte** (« 80 segments »), jamais nu.
9septies. ⚠⚠ **Un processus par requête coûte une poignée de main TLS par requête.**
    41 538 chunks avec un `curl` par chunk : **7 chunks/s**. Avec un pool de connexions
    **persistantes** — une par fil, gardée ouverte sur des milliers de requêtes —
    **195 à 209 chunks/s**, soit **×28**. C'est la **latence** qui coûte, pas le débit.
    ⚠ LplKnowledge avait mesuré ×7,9 sur la même bascule (binaire `curl` → `libcurl`).
    ⚠⚠ **Ma première mesure du gain était fausse — ×6,8 — parce qu'elle a été prise
    pendant que les `curl` de l'ancienne version tournaient encore.** Un chiffre mesuré
    sous contention n'est pas le chiffre : arrêter l'ancien avant de mesurer le nouveau.
9octies. ⚠⚠ **`&&` après une commande qui échoue coupe la chaîne — et le commit ment.**
    `git rm … && python3 - <<EOF … EOF` : le `git rm` a refusé (modifications locales),
    donc le patch n'a **jamais** été appliqué, et le message de commit décrivait un
    changement absent. C'est le piège nº 18 sous un nouveau costume. Vérifier l'effet,
    pas le code de retour de la dernière commande.
9sexies. ⚠⚠ **`vc_grow_seg_from_seed` n'est pas reproductible**, même en `thread_limit: 1`
    (la valeur que VC3D utilise) : quatre exécutions de la même graine rendent quatre
    aires, à 0,08 % près. Les quatre rendent **0 auto-intersection** — donc juger par un
    **invariant**, jamais par l'artefact.
10. ⚠⚠ **Un outil validé sur 300 K cellules ne tient pas sur 21 M** : un `cKDTree`
   global y prend des gigaoctets et **a fait tomber la machine trois fois**. Découper
   en **blocs 3D** (validé à 0,0 % d'écart), jamais en tuiles de paramétrisation —
   la métrique cherche justement les points loin en paramétrisation et proches en 3D.
11. **`pkill -f` / `pgrep -f` matchent leur propre ligne de commande** (payé 4×).
12. **Le code de sortie d'un pipeline est celui de sa DERNIÈRE commande** (payé 3×).
13. **Chemin relatif après un `cd`** : `mkdir` à un endroit, écriture à un autre →
    10 bandes calculées puis perdues.
14. **Éditer un script pendant qu'il tourne** le casse (bash lit par offset).
15. **Une boucle d'attente sans borne** survit à la disparition de ce qu'elle attend
    (payé : 3 h 19).
16. **`aws s3 cp --include` énumère TOUT le préfixe.**
17. **Vérifier l'alignement avant toute comparaison d'images** (remplissage à 512).
18. ⚠ **`cd` dans un `&&` qui échoue coupe la chaîne** : le patch ne s'applique pas et
    la commande suivante tourne sur l'ancien code, dont la sortie a l'air plausible.
    Chemins **absolus** dans les scripts de patch (payé 3× le 2026-08-18).
19. **Mesurer là où la mesure a eu lieu** : le profil de profondeur a d'abord été pris
    à `left 2000` quand l'inférence tournait à `left 17000`, et il a répondu l'inverse.
20. ⚠⚠ **Afficher la courbe avant de croire son argmax.** Le contraste local a servi
    d'instrument jusqu'à ce qu'on trace sa courbe : sur un volume à 2,4 µm c'est un
    **U**, maximal aux deux bords et minimal dans la feuille — il suit les interfaces et
    le bruit. L'intensité localise la matière ; le contraste non. Les deux coïncidaient
    à 7,91 µm, donc rien ne les distinguait.
21. **Une statistique « relative à la fenêtre » n'est pas comparable entre fenêtres.**
    Le « tiers central » de la fenêtre 15–40 n'est pas centré sur la couche tracée 32,
    alors qu'il l'est sur un volume de surface. Rapporter un **écart à la trace en µm**.
22. **Une mesure « entre voisins » exige des voisins** : la première version tirait des
    fenêtres à vingt chunks d'écart et rendait `NaN` sur **0 paire comparée**.
23. ⚠ **Un zéro se rapporte avec sa puissance, et la puissance dit quoi faire.** À
    n = 12, seul un rho ≥ 0,73 est détectable : un +0,330 n'est alors ni confirmé ni
    infirmé, et la réponse est d'aller chercher n ≈ 70 — pas de conclure.
24. ⚠⚠ **Le piège nº 6 se repaie même en le connaissant** (2026-08-19). J'ai pris
    l'invariant de **PHerc0172** (142,8 µm) comme seuil pour des segments de
    **PHercParis4**, dont le pas mesuré vaut **172,8 µm** — quatre segments signalés au
    lieu d'un. Le remède n'est pas une note, c'est **retirer le défaut du paramètre** :
    sans `--pas-um`, l'outil ne rend plus le compte du tout.
25. ⚠⚠ **Un modèle de coût qui se flatte n'est pas un modèle de coût.** Le tableau
    d'échelle divisait par 16 fils ; la mesure dit **×8,35**. 0,5 h annoncé, 0,9 h réel.
26. ⚠ **Fermer un confond d'un seul côté ne le ferme pas.** Savoir que l'encre suit
    l'emprise ne suffit pas : il faut aussi savoir si le **critère** la suit. Les deux
    branches existaient (+0,463 et +0,384) — seule la corrélation **partielle** a tranché,
    et elle a **renforcé** la relation au lieu de la dissoudre.
27. ⚠ **Un échantillonnage régulier tombe dans le remplissage.** Un volume de surface est
    majoritairement du vide : des blocs posés à intervalles réguliers ont rendu **6
    fenêtres utiles sur 96**. Il faut **trouver la matière avant de la sonder**.
28quater. ⚠⚠ **Un outil qui saute ses sorties existantes saute aussi ses sorties
    CORROMPUES.** `vc_render_tifxyz` a affiché « all slices exist, skipping » sur 21 TIFF
    **tronqués** laissés par un run tué — et ça ressemble parfaitement à un rendu réussi.
    Effacer le répertoire de sortie avant de relancer.
28ter. ⚠⚠ **Un défaut par défaut peut annuler une vérification entière.** `voxelsize` vaut
    **0** dans les paramètres de `vc_grow_seg_from_seed`, donc l'aire en cm² est nulle *par
    construction* et **toute** surface est rejetée avec « area 0 below min_area_cm ». Le
    message accuse la surface ; le fautif est le paramètre absent.
28bis. ⚠⚠ **`kill $!` sur un `nohup uv run … &` ne tue que le WRAPPER.** Le vrai
    travailleur est un petit-fils (`uv run` → `python`), il survit, et il continue
    d'écrire dans le `--out` qu'on croyait abandonné. Payé **deux fois dans la même
    heure** : deux campagnes orphelines ont brûlé de la bande passante pendant 37 minutes
    en doublonnant celles qu'on venait de relancer, et le symptôme était une campagne
    « lente » et non une campagne fantôme. Remède : `ps -eo pid,ppid,etime,args` puis tuer
    **le petit-fils**, ou lancer avec `setsid` et tuer le groupe.
29. ⚠⚠ **Une réponse S3 contient le PRÉFIXE INTERROGÉ** en plus de ses sous-préfixes.
    Compter les lignes sans l'exclure décale une table de **un partout** — et une table
    décalée d'un cran ressemble parfaitement à une table juste.
30. ⚠⚠ **Un contrôle de robustesse doit d'abord prouver qu'il compare LA MÊME GRANDEUR.**
    J'ai passé une heure à affaiblir un résultat juste parce que je comparais un
    `avec_matiere` neutre à un mélange repérage+blocs. **La prudence n'est pas une
    méthode** : affaiblir semblait la position sûre, et c'est ce qui l'a rendu difficile
    à voir.
31. ⚠⚠ **Trop peu d'échantillons fabriquent des effets qui n'existent pas, avec leur
    explication toute prête.** À 3 tranches, la sensibilité du centre donnait **5,65 %** et
    une « marche » nette dès la plus petite perturbation, expliquée par « la mesure compte
    des pics, donc elle procède par marches ». À 6 tranches : **1,75 %**, aucune marche.
28. ⚠ Deux corrections de nom vérifiées sur le fichier plutôt que devinées : `events` est
    un **compte** dans l'index de `windcheck`, pas une liste ; et le volume `cos` du
    `lasagna` déclare ses niveaux dans son `.zattrs` — il n'en a pas de plus fin que 3.

## 9. Règles de mesure tenues ici

1. **Aucun seuil absolu** sur une grandeur physique — normaliser, ou être **ordinal**.
2. **Vérifier le confond avant de conclure.**
3. **Un contrôle qui ne peut pas échouer ne prouve rien** : témoin apparié + cas négatif.
4. **Mesurer d'abord, expliquer ensuite.** La lecture du code a produit une hypothèse
   fausse à chaque fois qu'elle a précédé l'instrument.
5. ⚠⚠ **Un chiffre publié dont le calcul n'est pas dans l'arbre n'est pas un résultat,
   c'est une anecdote.** Payé : l'onde radiale a dû être récupérée du transcript.
6. **Une idée testée et écartée est un actif** — à condition que la *raison* soit
   écrite. Quatre formulations des fusions, trois échecs, et c'est le troisième qui a
   désigné la bonne méthode.
7. **Rapporter la puissance avec un zéro** : « pas de corrélation » ne veut rien dire
   sans le rho que la taille d'échantillon permettait de détecter.
