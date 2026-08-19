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

## 2. ⚠ CE QUI TOURNE (2026-08-19, fin de séance)

| quoi | sortie | pourquoi ça compte |
|---|---|---|
| **sondage dense**, 392 points par segment | `docs/dense_PHercParis4/` (un fichier par segment) | ⭐⭐ tranche la voie O : le critère de `19` n'est reproductible qu'à **rho +0,280** entre deux grilles. Si l'accord monte avec la densité, c'était de l'erreur d'échantillonnage ; sinon les deux grilles mesurent des choses différentes |
| **sensibilité du centre, niveau 0** | `docs/sensibilite_centre_L0.json` | ferme `06` §2.3 autrement que par l'ombilic, qui n'existe pas |

```bash
ls docs/dense_PHercParis4/ | wc -l          # sur 80
tail -3 docs/sensibilite_centre_L0.log
ps -eo etime,pcpu,cmd | grep -E "[z]arr_depth|[s]ensibilite"
```

**Quand le dense aura rendu**, la mesure qui conclut la voie O tient en une ligne :

```bash
cd inference_xpu
uv run python ../analysis/src/robustesse_material.py \
    ../docs/dense_PHercParis4 ../docs/champ_PHercParis4 \
    --nom-a "dense (392 points)" --nom-b "champ (200 points)" \
    --out ../docs/robustesse_dense.json
```
⭐ **La prédiction est posée avant la mesure** : si l'accord monte nettement au-dessus de
+0,280, l'écart venait du bruit d'échantillonnage et un seuil redevient défendable. S'il
ne monte pas, il faut dire **ce que chaque grille mesure** au lieu d'en moyenner.

⚠ **Juger sur un fichier de résultat, jamais sur une notification**, et **vérifier
l'horodatage d'un log avant d'en citer le verdict** — un log vieux de sept heures a déjà
été lu comme un résultat frais. ⚠ Python **bufferise** : lancer avec `python -u`, sinon un
log vide ressemble à un job mort (payé une fois de plus aujourd'hui).

⚠ Pour libérer la machine sans rien perdre : `kill -STOP` les calculs (ils reprennent à
l'identique) et tuer les `curl` — c'est la **bande passante** qui fait bégayer un Zoom.
Les deux campagnes sont **reprenables** (un fichier par segment).

## 2bis. ⭐ La liste de ce qui reste ouvert

**[`docs/18_batch_produire.md`](docs/18_batch_produire.md)** — le batch en cours. Le
précédent, [`13`](docs/13_batch_epuisement.md), est **clos** : ses huit voies sont
fermées, chacune par une mesure ou par une raison écrite.

⭐ **Ce que `18` attaque est d'une autre nature.** `13` fermait ce qui était ouvert ;
`18` répond à la remarque que `13` a laissée derrière lui — *tous nos instruments
jugent, aucun n'a encore changé quoi que ce soit*. La voie I est **faite** (`19`), la
voie J est l'outil de réparation.

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
uv run python ../analysis/src/compare_maps.py <a.npy> <b.npy>
uv run python ../analysis/src/proximity_vs_ink.py <mesh> <pred> <labels>
```

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

## 7. ⏳ CE QUI RESTE, avec son blocage

⭐ La liste cochable est dans **`docs/18_batch_produire.md`**. Ci-dessous seulement ce qui
n'est ni fait ni écarté.

| # | quoi | blocage |
|---|---|---|
| **J7** ⭐⭐ | **le gauchissement** — la mesure dit que la translation n'enlève que 21,7 % de l'erreur, donc le remède utile est une déformation guidée par le champ | rien ne bloque, c'est le prochain gros morceau. ⚠ Et il faut un **critère de succès** qui ne soit pas circulaire : re-mesurer le champ après correction ne prouverait que l'arithmétique |
| **M1** | l'analyse de sensibilité du centre, **au niveau 0** | 🔄 lancée. ⚠ La version niveau 2 est **invalide** : les seuils sont calés au niveau 0 et y comptent 42 feuilles au lieu de 176 (piège nº 1) |
| M2 | plus de bandes **niveau 0** (2 faites : une migre, une non) | ~50 min par bande, `tools/bandes_niveau0.sh`. Le crible niveau 2 ne peut PAS répondre |
| M3 | **ESRF 2,4 µm** sur les 4 sites (`06` §3.6) | — |
| — | le **pas inter-feuilles de PHerc1667** | ⚠ **aucune prédiction de surface publiée** pour ce rouleau : la voie `espacement_spires.py` n'existe pas là. Tant qu'il manque, on ne juge pas ses sauts de feuille |
| — | la **bascule recto/verso** des fibres | non expliquée, et la voie est **réfutée** (`14`) — à ne rouvrir que si une autre mesure la réclame |
| — | le trend **position dans le rouleau** ↔ résiduel | ⚠ **NON établi** : Scroll 1 rend `p90` significatif et `median` nul, Scroll 4 l'inverse. Configuration exacte des fibres à n = 12. Il faut plus de segments |

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
28bis. ⚠⚠ **`kill $!` sur un `nohup uv run … &` ne tue que le WRAPPER.** Le vrai
    travailleur est un petit-fils (`uv run` → `python`), il survit, et il continue
    d'écrire dans le `--out` qu'on croyait abandonné. Payé **deux fois dans la même
    heure** : deux campagnes orphelines ont brûlé de la bande passante pendant 37 minutes
    en doublonnant celles qu'on venait de relancer, et le symptôme était une campagne
    « lente » et non une campagne fantôme. Remède : `ps -eo pid,ppid,etime,args` puis tuer
    **le petit-fils**, ou lancer avec `setsid` et tuer le groupe.
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
