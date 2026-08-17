# Carnet de mesures : faites, en attente, écartées

2026-08-17. Chaque entrée porte **ce qu'elle trancherait** et **ce qui la
falsifierait**. Une mesure sans critère de réfutation n'entre pas dans ce carnet.

---

## 0. Le fait de contexte, vérifié

**Début du texte = extérieur du rouleau. Fin du texte + titre (colophon) = cœur.**
Source : les équipes cherchent *« the end of the papyrus (the innermost part of the
carbonised scroll) where the colophon with the title of the work may be
preserved »* ([Bodleian](https://www.bodleian.ox.ac.uk/about/media/feb25/herculaneum-scroll),
[Herculaneum papyri](https://en.wikipedia.org/wiki/Herculaneum_papyri)). C'est aussi
ce qui justifie l'existence d'un **Title Prize** distinct.

**Conséquence** : si les couches externes sont les plus abîmées, ce qu'on perd est
le **début** — introduction, préface, dédicace. Et le titre, lui, est du côté le
mieux protégé.

Papiers primaires repérés, à lire :
[Diffeomorphic Spiral Fitting](https://arxiv.org/pdf/2512.04927) (le spiral fit),
[Ink Detection from Surface Topography](https://arxiv.org/pdf/2603.27698).

---

## 1. Faites

| # | mesure | résultat | où |
|---|---|---|---|
| 1.1 | Tailles S3 par étage | surfaces ~220 Mio · prédictions ~19,6 Gio · volume ~2,1 Tio | `02` |
| 1.2 | Pyramide OME-Zarr | 6 niveaux ; **rouleau entier en 3D = 33 Gio au niveau 2** (9,6 µm) | `02` |
| 1.3 | Inventaire des traces | 45 échantillons, 310 segments, **33/45 sans aucune trace** | `02` |
| 1.4 | Reproduction `windcheck` | **53/53** verdicts et comptes de triangles concordants | `03` |
| 1.5 | Ampleur de l'excision | **0,16 %** de l'aire en médiane, max 2,79 % | `03` |
| 1.6 | Contenu CT des cellules excisées | **H₀ non rejetée** — 75 810 cellules, p = 0,859, delta −0,000 | `04` |
| 1.7 | Idem, séparé par bande | −0,022 et +0,009 : pas de signal caché | `05` |
| 1.8 | Espacement réel entre parties non adjacentes | **médiane 177 µm**, p5 = 101, p90 = 303 — **pas 300 µm** | `05` |
| 1.9 | Survie de l'anomalie à la réparation | à 79 µm : **8/9 croisements survivent**, valeurs inchangées | `05` |
| 1.10 | Bande sévère ≡ couverture > 1 tour | **10 traces**, dont 9 `auto_grown` — le « 9× » était tautologique | `05` |
| 1.11 | Espacement selon le rayon | **158 µm au cœur → 203 µm dehors** (+28 %, monotone sur 5 tranches) | ici |
| 1.12 | Vérification des données Scroll 1 **par le comportement** | triangles et contacts diagonale 0 **exacts** vs publication | `07` |
| 1.13 | Métrique de proximité à longueur contrôlée (3 traces, ~7,8 tours) | ordonne correctement : **0,09 % → 0,15 % → 0,37 %** selon les croisements | `07` |
| 1.15 | ⭐ **iGPU Arc utilisable depuis WSL2** | **×4,5** (104 → 23 ms/fenêtre), sortie identique au CPU à **4,9e-6** (bruit fp32) | ici |
| 1.16 | Pas de balayage 21 vs 32 | **pas gratuit** : corr. 0,941, mais **17,9 %** de désaccord au seuil médian, 3,0 % sur l'encre franche | ici |
| 1.14 | ⭐ La métrique **survit à la réparation** | recensement 11 673 → **0** ; métrique 0,37 → **0,38 %** ; témoin sain **0,09 %** | `07` |

## 1bis. ⭐ LE CAP, fixé le 2026-08-17

Décision de l'auteur, et elle relève la barre au bon endroit :

> **On ne publie rien sans une passe complète du pipeline — rouleau déroulé, texte
> extrait, soumis à un expert qui dise si ça fait sens — et ce sur plusieurs
> rouleaux.**

C'est exactement l'exigence du concours lui-même (Grand Prize : papyrologues
indépendants, **70 % de caractères lisibles par colonne**). Une métrique géométrique
qui corrèle ne prouve **rien** sur du texte.

**Conséquence sur le travail** : tout ce qui précède (`04`, `05`, `07`) devient de
l'outillage de diagnostic, utile mais pas un livrable. Le livrable est une passe
complète.

### La passe complète, et où on en est

| étage | état chez nous | ce qui manque |
|---|---|---|
| trace `tifxyz` | ✅ 55 traces Scroll 1, 53 Scroll 5 | — |
| aplatissement | ✅ déjà fait en amont (`_flatboi`) | — |
| **rendu** en couches | ✅ **déjà publié** — `dl.ash2txt.org`, accès libre | rien : 31 couches (15-45), 17 Go, téléchargées |
| **détection d'encre** | ✅ modèle GP chargé, 38 M param. | rien : **104 ms/fenêtre** mesuré sur CPU |
| **inférence sur une région** | ✅ outil écrit, GPU câblé | 4 cm² en **5,6 min** ; segment entier en **3,4 h** |
| jugement | ❌ | un papyrologue — et le contrôle en aveugle des modèles de langue |

### Matériel : l'iGPU Arc EST utilisable, le NPU non

Core Ultra 7 165H, 22 cœurs, 31 Gio.

| voie | état |
|---|---|
| **iGPU Arc via `torch 2.9.1+xpu`** | ✅ **×4,5**, sortie identique (4,9e-6) |
| NPU | ❌ **non exposé à WSL2** (`/dev/accel` absent) |
| OpenVINO | ❌ ne convertit pas ce modèle (einsum des rotary embeddings) |
| CPU seul | 104 ms/fenêtre (16 fils, lot 4) |

⚠ **Ce qui a débloqué le GPU** : `intel-opencl-icd libze-intel-gpu1 libze1`. Le nom
`intel-level-zero-gpu` n'existe pas sous Ubuntu 26.04, et apt **annule toute la
transaction** sur un nom inconnu — d'où un premier essai où rien n'était installé.
Le GPU fonctionne **sans `/dev/dri`**, par `/dev/dxg`.

⚠ 22 fils CPU s'effondre à 734 ms/fenêtre — sur-souscription.

**Coût de l'inférence, au pas 21 (celui de la référence)** : 4 cm² en **5,6 min**,
segment entier en **3,4 h**.

### ⚠ Le contrôle sans lequel la passe ne vaut rien

Faire tourner le pipeline sur du texte **inconnu** ne prouve rien : on ne saura pas
si le résultat est juste. **La première passe doit viser une région dont le texte
est DÉJÀ LU** — les régions du Grand Prize 2023 sont publiées, et le jeu
`ink-labels` fournit des masques d'encre alignés. Si notre chaîne ne retrouve pas ce
qui est connu, son avis sur l'inconnu ne vaut rien.

### ⚠ Sur l'usage d'un modèle de langue comme juge intermédiaire

Idée de l'auteur, en attendant un expert disponible. Elle a un mode de panne
précis : devant une image de grec ancien dégradé, un modèle **produira du grec
plausible** — le motif « sortie fausse indistinguable d'une sortie juste » qu'on
traque depuis le début.

**Utilisable seulement avec son contrôle** : lui soumettre en aveugle des rendus
dont le texte est déjà publié et lu, mélangés à des rendus de bruit, et mesurer
s'il retrouve les premiers et refuse les seconds. Sans cette calibration, son avis
sur du texte inconnu n'est pas une donnée.

## 2. À faire — priorité haute

### 2.1 ⭐ Monotonie radiale du winding (l'idée la plus prometteuse)

**Ce que ça teste** : le long d'un rayon partant de l'ombilic, les feuilles sont
traversées dans un ordre, et cet ordre doit être **strictement croissant**. Un saut
de spire le viole.

**Pourquoi c'est supérieur à tout ce que j'ai essayé** : la mesure est **ordinale**,
donc elle n'a besoin d'**aucune référence locale**. Or 1.8 et 1.11 montrent que
l'espacement varie de 101 à 303 µm selon l'endroit et de +28 % selon le rayon —
c'est exactement ce qui a fait échouer ma métrique métrique.

**Ce qui existe déjà** : `vc::core::util::Umbilicus` (`theta(point, wrap_count)`,
`distance_to_umbilicus`, `center_at(z)` — un centre **par tranche**, donc la
déformation en cône est modélisée) ; les fichiers `umbilicus.txt` pour Scroll 1 et 3
dans ThaumatoAnakalyptor ; le lancer de rayons dans
`winding_model_dataset.py` (mais comme **entrée d'entraînement**, jamais comme
contrôle).

⚠ **Ce qui la falsifierait** : une déchirure ou un décollement viole légitimement la
monotonie sans être une erreur de traçage. Si on ne sait pas séparer les deux, on
refuse des reconstructions correctes — le piège exact de `CaveKind::Layered`.

⚠ **Manque** : pas d'`umbilicus.txt` pour Scroll 5. À dériver, ou travailler sur
Scroll 1 / Scroll 3.

### 2.2 ✅ FAITE — le témoin qui sépare longueur et qualité

Résultat en `07`. La métrique **ordonne correctement** à longueur contrôlée
(0,09 % / 0,15 % / 0,37 % pour 0 / 52 / 408 croisements), et surtout elle **survit à
la réparation** — ce qui écarte l'objection « elle ne fait que re-détecter les
croisements ».

⚠ **Leçon d'outillage payée ici** : le récupérateur de `windcheck` a tourné
**3 h 15** dont l'essentiel à énumérer un préfixe de **11 millions de clés et 20 To**
pour en extraire 400 Mo — il avait lu **15,26 Go** de réponses XML. Et trois de mes
propres boucles d'attente, dont la ligne de commande contenait `windcheck.fetch`,
se voyaient mutuellement via `pgrep -f` et tournaient depuis **15 heures**. C'est la
quatrième occurrence de ce piège dans ce projet : **tuer et attendre par PID, jamais
par motif.**

⚠ Conséquence assumée : le manifeste SHA-256 de Scroll 1 n'existe pas (écrit en fin
de course, interrompue). La vérification s'est faite **par le comportement**
(1.12) — plus forte, puisqu'elle prouve que la donnée est juste et pas seulement
intacte.

### 2.3 Vérifier 1.11 avec le vrai ombilic

1.11 utilise un barycentre par tranche, sur **une seule trace** qui ne couvre pas
tout le rouleau — donc centre biaisé. À refaire avec `umbilicus.txt` sur Scroll 1.

### 2.4 La théorie du dommage : le profil est-il en U ?

**L'hypothèse de l'auteur** : la fumée est passée par le **trou central**, donc les
toutes premières couches du cœur sont abîmées ; mais le rouleau est plus dense au
centre donc il a mieux résisté ; les couches externes ont pris le plus, **et sur de
plus grandes longueurs** (la circonférence croît avec le rayon).

**Prédiction falsifiable** : le dommage en fonction du rayon n'est **pas monotone**
mais en **U** — mauvais au cœur immédiat, bon dans la couronne intermédiaire,
mauvais à l'extérieur.

**Comment** : échantillonner le CT sur la surface et mesurer un indicateur de
dégradation (contraste feuille/interstice, ou dispersion d'intensité) par tranche de
rayon. La machinerie existe (`excision.measure`).

**Enjeu réel** : si le profil est en U, ça dit **où semer** en priorité, et ça donne
un argument mesuré sur ce qui est récupérable. Et vu 0, ça chiffrerait ce qu'on a
perdu du **début** des textes.

## 3. À faire — priorité moyenne

| # | mesure | ce que ça trancherait |
|---|---|---|
| 3.1 | 🔄 **EN COURS** — métrique de proximité sur **toutes** les traces de Scroll 1 | passage de trois anecdotes à une distribution ; corrélation avec les croisements publiés sur 55 traces au lieu de 3 |
| 3.2 | Normaliser la proximité **par le rayon** en plus du voisinage | 1.11 montre un gradient de 28 % non corrigé aujourd'hui |
| 3.3 | Recensement `windcheck` sur Scroll 1, confronté à leur publication | 4ᵉ vérification indépendante, sur un autre rouleau |
| 3.4 | Direction des fibres (recto/verso) comme contrainte d'orientation | problème ouvert nº5 ; les prédictions nnUNet existent déjà |
| 3.5 | Le niveau 2 de la pyramide suffit-il à séparer les spires ? | déciderait si on peut travailler à 33 Gio au lieu de 2,1 Tio |
| 3.6 | Effet de la campagne de scan (DLS 7,91 µm vs ESRF 2,4 µm) | le site montre que ça change la séparabilité ; le chiffrer |
| 3.7 | ✅ **FAITE** — seuil : suppression impossible, mais PLATEAU établi | **Le supprimer dégrade la métrique** : le déficit moyen sans seuil tombe à rho +0,340 (contre +0,769), parce qu'il est dilué par la masse des cellules normales — **le signal est dans la queue extrême**. Mais le balayage montre un **plateau de 0,15 à 0,40** (rho 0,759 à 0,779), puis un effondrement au-delà de 0,5. Le seuil n'est donc pas réglé : n'importe quelle valeur de la plage donne la même réponse |
| 3.8 | La proximité prédit-elle une perte de **lisibilité** ? | la frontière que ni `04` ni `07` ne franchissent : on mesure une anomalie géométrique, pas une perte de texte. Demande un rendu et un jugement — le maillon le plus cher, et le seul qui convertirait la métrique en argument sur le résultat final |
| 3.9 | Le plancher du témoin (0,09 %) est-il réel ? | `07` §5 : soit un plancher de la mesure, soit de vraies approches légitimes. Trancher en mesurant plusieurs traces à 0 croisement — il y en a **3** dans Scroll 1 |

## 4. Écartées, avec la raison

- **Écrire un septième vérificateur** — six existent (`01`, `00` §4). Doublon.
- **Refaire le recensement d'auto-intersection** — `windcheck` couvre 284 des 310
  traces publiées. Rien à gagner.
- **Télécharger un volume complet** — 2,1 Tio contre 100 Go de budget. La pyramide
  et le streaming rendent la question caduque.
- **Juger la qualité d'un rendu par l'œil** — non reproductible, et il existe des
  invariants calculables. À garder pour l'illustration, jamais pour la mesure.

## 5. Règles de mesure, apprises ici

1. **Aucun seuil absolu.** Trois mesures indépendantes (1.8, 1.11, la capture
   DLS/ESRF) montrent que l'espacement varie d'un facteur trois selon l'endroit.
   Toute grandeur doit être normalisée — ou mieux, être **ordinale**.
2. **Un chiffre emprunté n'est pas une mesure.** Le « 300 µm » venait d'un README
   sur un autre rouleau et a produit une conclusion fausse (`05` §4bis).
3. **Vérifier le confond avant de conclure.** « Les automatiques sont 9× pires »
   était un effet de longueur (1.10).
4. **Un contrôle qui ne peut pas échouer ne prouve rien.** Toute comparaison porte
   un témoin apparié et un cas négatif.
5. **Mesurer d'abord, expliquer ensuite.** Trois fois cette semaine, la lecture du
   code a produit une hypothèse fausse qu'un instrument a corrigée.
