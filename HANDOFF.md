# Reprise de session — état au 2026-08-18

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

## 2. ⚠ CE QUI TOURNE (2026-08-18, 11 h 30)

| quoi | sortie | reste |
|---|---|---|
| profondeur sur **80 segments** de Scroll 1 | `docs/profondeur_corpus_2.4um.json` | ~48 |
| **fibres sur 80 segments**, en file derrière | `docs/fibres_corpus.json` | tout |
| traces `tifxyz` de **PHerc0814** | `data/traces/PHerc0814` | ~13 |

```bash
ps -eo etime,pcpu,cmd | grep -E "[z]arr_depth|[f]iber_orient|[f]etch_traces"
grep -c couches docs/profondeur_corpus.log ; grep -c desaccord docs/fibres_corpus.log
```

⚠ **Juger sur un fichier de résultat, jamais sur une notification** : celles-ci
concernent le *wrapper*, pas le travail `nohup`, et un log vide veut dire « Python
bufferise ».

⚠ Pour libérer la machine sans rien perdre : `kill -STOP` les calculs (ils reprennent à
l'identique) et tuer les `curl` — c'est la **bande passante** qui fait bégayer un Zoom.
`./tools/reprendre.sh` remet tout en route.

## 2bis. ⭐ La liste de ce qui reste ouvert

**[`docs/13_batch_epuisement.md`](docs/13_batch_epuisement.md)** — six voies, et elles se
cochent là. Un item se ferme de **deux** façons également valables : *fait et mesuré*,
ou *écarté avec la raison écrite*.

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
| `14` | ⭐ la direction des fibres — problème ouvert nº 5 |

## 4. L'outillage, et comment le relancer

```bash
./tools/temoins.sh                      # 16 contrôles hors ligne, tous verts
./tools/mirror_site.sh                  # miroir + contrôle de couverture
./tools/fetch_layers.sh <url> <dest> <largeur> <de> <a>   # couches, reprenable
./tools/ppm_to_tifxyz.py <in.ppm> <out.tifxyz>            # .ppm de VC -> tifxyz
./tools/survey_fusions.sh <out> <bandes> <par> <pas>      # fusions, niveau 2
./tools/bandes_niveau0.sh                                 # bandes niveau 0, hors site
./tools/fetch_traces.py <index.json> <corpus> <dest>      # traces tifxyz, SANS aws
./tools/lister_volumes_surface.sh <rouleau> <sortie>      # qui publie un volume Zarr
./tools/fetch_cartes_encre.sh <rouleau> <dest>            # cartes d'encre PUBLIEES
./tools/reprendre.sh                                      # degeler apres un kill -STOP

cd experiments   # geometrie
uv run python src/excision/radial.py {centre|compter|profil|deplier|axe} …
uv run python src/excision/fusions.py {controle|ecarts-controle|densite|ecarts} …
uv run python src/excision/fusion_scan.py …               # persistance en z
uv run python src/excision/track_z.py <scans.json> …      # appariement PREDICTIF
uv run python src/excision/baseline_sweep.py <traces> <out.jsonl>   # references locales
uv run python src/excision/variant_correlate.py <sweep> <index.json>
uv run python src/excision/pyramid.py <volume>            # separabilite par niveau
uv run python src/excision/shape.py {degradation|ellipticite} <volume>
uv run python -m excision.proximity <mesh.tifxyz> --json

cd inference_xpu # encre
uv run python src/infer_ink.py <layers> --model … --device xpu --out out.npy
uv run python ../analysis/src/{evaluate_segment,render_segment,structure}.py …
uv run python ../analysis/src/judge_api.py --list-models
uv run python ../analysis/src/judge_api.py <pred.npy> --bands-only   # sans cle
uv run python ../analysis/src/depth_profile.py <couches…> --grid     # qualite de trace
uv run python ../analysis/src/zarr_depth.py <cle .zarr> --courbe     # ⭐ a DISTANCE
uv run python ../analysis/src/fiber_orientation.py <cle .zarr>       # ⭐ fibres
uv run python ../analysis/src/croiser_instruments.py <index.json> <mesures.json>
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
9bis. ⭐⭐ **Un chunk Zarr = une colonne de profondeur entière, pour 1,78 Mo et 1,03 s.**
   Les volumes de surface sont publiés en OME-Zarr non compressé, chunks
   `[109, 128, 128]`. Une campagne qui demandait **32 Go par segment** en demande
   quelques mégaoctets. Conséquences : **81 segments** de Scroll 1 avec volume de
   surface, **80 avec une carte d'encre publiée** (récupérées — le résultat sans lancer
   43 min d'inférence), **3 campagnes** de scan (45,5 / 2,4 / 1,13 µm) dont 37 segments
   les ont toutes, et **aucune troncature** du profil. Ça débloque `12` §5 *et* `06` §3.6.

9. ⭐⭐ **La profondeur de surface** (`12`) — une mesure de **qualité de tracé** qui ne
    demande **ni vérité terrain, ni modèle, ni juge**. Part des fenêtres dont le pic de
    contraste tombe dans le tiers central des couches lues : Scroll 1 **63 %** et
    **50 %**, Scroll 4 **7 %** (écart interquartile 4,0 / 11,5 contre **22,0**).
    Scroll 4 est **bimodal** — 92 fenêtres piquant au bord bas, 49 au bord haut : sa
    surface **voyage**, ce n'est pas un décalage uniforme.

### Encre — l'instrument

10. **AUC 0,925** sur 44,7 M de pixels d'un segment entier, contrôle mélangé à **0,500**.
   9,2 cm de grec lisible. ⚠ Orientation de lecture = **rotation 270°**.
11. **Juge de langue calibré** : **15/16, zéro fabrication**, lisibilité séparant sans
   chevauchement le vierge (0–1) du texte (3–6). Protocole : `data/juge/PROTOCOLE.md`.

12. ⚠⚠ **Rien de lisible sur Scroll 4, et la cause est EN AMONT du modèle** (`09` §12,
   `12`). Deux passes complètes (couches 15–40 puis 0–25, ~43 min chacune). Le juge
   calibré : lisibilité **1–3** sur la première, **refus de tous les panneaux** sur la
   seconde, quand le calibrage sépare vierge **0–1** de texte **3–6**. Recentrer les
   couches n'a rien sauvé (les deux cartes : rho **+0,700**, **88,7 %** d'accord).
   ⚠⚠ Et ça ne pouvait pas marcher : sur **61 %** du segment le cœur de matière est
   **hors des 65 couches**. On ne détecte pas d'encre sur une surface que le volume de
   surface ne contient pas. ⚠ Limite du protocole mesurée au passage : **la lecture
   d'un panneau dépend de son voisin** (même image, 1 puis 2 puis 0 glyphes, à
   température zéro).

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

### La jonction — et c'est un NON

13. ⚠⚠ **La proximité géométrique ne prédit PAS la lisibilité.** rho **+0,019** à
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

⭐ La liste complète et cochable est dans **`docs/13_batch_epuisement.md`**. Ci-dessous
seulement ce qui n'est ni fait ni en cours.

| # | quoi | blocage |
|---|---|---|
| **B4** ⭐⭐ | croiser la profondeur de surface avec les **80 cartes d'encre publiées** et les croisements de `windcheck` | attend la campagne (~48 segments). ⚠ Prédiction **reposée** avant mesure : *écart médian pic↔trace > ~50 µm ⇒ pas d'encre lisible*. Le seuil est le **milieu de l'intervalle observé** à n = 3, donc provisoire par construction |
| **C4** ⭐ | fibres sur les 80 segments | en file. ⚠ **À n = 12 la mesure ne détecte qu'un rho ≥ 0,73** : le +0,330 observé n'est ni confirmé ni infirmé. Il faut n ≈ 70 |
| **A5** ⭐ | la métrique de proximité sur PHerc0139 / PHerc1667 / PHerc0814 | traces récupérées (PHerc0814 en cours). C'est **le vrai second rouleau** : populations majoritairement > 1 tour, donc dans le domaine de définition |
| **D** ⭐ | retrouver la feuille de Scroll 4 | le cœur de matière est hors des 65 couches. ⚠ Les volumes de surface de PHerc1667 sont **repérés** (19 à 2,399 µm, 27 à 1,129 µm) : la mesure se fait à distance, sans réengendrer de couches |
| §2.3 | vrai ombilic | ⚠ `umbilicus.txt` renvoie **404** à l'adresse notée dans `06`. Chemin à retrouver dans le bucket |
| E2 | plus de bandes **niveau 0** | 2 faites (une migre, une non). Le crible niveau 2 ne peut PAS répondre — il regarde ailleurs. ~50 min par bande, `tools/bandes_niveau0.sh` |
| — | la **bascule recto/verso** des fibres | non expliquée. Trois causes candidates (`14` §3), aucune départagée. ⚠ À 1,129 µm la pile ne fait que **123 µm**, soit moins qu'une épaisseur de feuille |
| — | le **seuil** de la profondeur de surface | il vaut ce que vaut n = 3. La campagne le recalibrera, ou le cassera |

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
