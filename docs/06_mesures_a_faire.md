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
| 1.17 | ⭐ **Passe complète du pipeline** (couches → modèle → encre) | **AUC 0,919** hors entraînement, lettres grecques visibles, 52 s/cm² | `08` |
| 1.18 | Étiquetage de vérité terrain | ⚠ **PARTIEL** : 50 % des lignes sans étiquette → la précision est un plancher | `08` |
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
| 3.1 | ✅ **FAITE** — métrique sur 46 traces de Scroll 1 | rho **+0,769** avec les croisements, **+0,820 / +0,944 / +0,739** par tercile de longueur ; le confond de `05` **n'existe pas** dans Scroll 1 (rho longueur~croisements = 0,05) |
| 3.2 | Normaliser la proximité **par le rayon** en plus du voisinage | 1.11 montre un gradient de 28 % non corrigé aujourd'hui |
| 3.3 | ✅ **FAITE** — recensement Scroll 1 vs publication | **55/55 triangles et 55/55 contacts** concordants. Deux corpus entiers vérifiés |
| 3.4 | Direction des fibres (recto/verso) comme contrainte d'orientation | problème ouvert nº5 ; les prédictions nnUNet existent déjà |
| 3.5 | Le niveau 2 de la pyramide suffit-il à séparer les spires ? | déciderait si on peut travailler à 33 Gio au lieu de 2,1 Tio |
| 3.6 | Effet de la campagne de scan (DLS 7,91 µm vs ESRF 2,4 µm) | le site montre que ça change la séparabilité ; le chiffrer |
| 3.7 | ✅ **FAITE** — seuil : suppression impossible, mais PLATEAU établi | **Le supprimer dégrade la métrique** : le déficit moyen sans seuil tombe à rho +0,340 (contre +0,769), parce qu'il est dilué par la masse des cellules normales — **le signal est dans la queue extrême**. Mais le balayage montre un **plateau de 0,15 à 0,40** (rho 0,759 à 0,779), puis un effondrement au-delà de 0,5. Le seuil n'est donc pas réglé : n'importe quelle valeur de la plage donne la même réponse |
| 3.8 | La proximité prédit-elle une perte de **lisibilité** ? | la frontière que ni `04` ni `07` ne franchissent : on mesure une anomalie géométrique, pas une perte de texte. Demande un rendu et un jugement — le maillon le plus cher, et le seul qui convertirait la métrique en argument sur le résultat final |
| 3.9 | ✅ **FAITE** — pas de plancher | Les **7** traces à 0 croisement s'étalent de **0,020 % à 0,372 %**, facteur 18. Donc la métrique **ne classe pas** : elle corrèle. A obligé à corriger `07` |

## 3bis. ⭐ LA SUITE, dans l'ordre

Le cap de `1bis` n'est pas franchi : on a des **lettres**, pas un **texte jugé par
un expert**. Ce qui manque, du plus décisif au moins :

### A. ✅ FAITE — une colonne entière de texte (`10_segment_complet.md`)

Segment `20230909121925` entier : 99 918 fenêtres, **38,5 min** sur l'iGPU Arc (et
non 3,4 h — l'estimation d'ici était pessimiste d'un facteur 5). Résultat :
**AUC 0,925** sur 44,7 M de pixels, contrôle mélangé à 0,500, et **4 à 5 lignes** de
grec lisible sur 91,7 × 30,7 mm.

⚠ **Et elle a réfuté la raison pour laquelle elle était prioritaire.** On l'attendait
pour débloquer le juge structurel, qui *croyait* manquer de surface (`09` §6). Le
segment entier n'a **pas plus de lignes** — c'est une bande coupée en travers du
texte, l'allonger allonge les lignes sans en ajouter. Le juge mécanique a donc échoué
une troisième fois, avec une troisième cause. Voir `09` §8.

### B. Le contrôle en aveugle des modèles de langue

Prévu en `1bis`, pas encore fait. Soumettre des rendus **dont le texte est publié**,
mélangés à des rendus de bruit, et mesurer si le modèle retrouve les premiers et
refuse les seconds. Sans cette calibration, son avis sur du texte inconnu n'est pas
une donnée. ⚠ À faire **avant** de lui montrer quoi que ce soit d'inconnu, sinon on
ne pourra plus le calibrer sans biais.

### C. Un second rouleau

Tous les chiffres de `07` et `08` viennent de Scroll 1. Scroll 5 se comporte déjà
différemment sur le confond longueur/qualité. Rien ne dit que l'AUC voyage.

### D. ⭐ Boucler la métrique de `07` sur le résultat de `08`

⚠ **Bloquée sur un fait matériel, constaté le 2026-08-17** : le maillage `tifxyz` de
`20230909121925` n'est pas dans `repos/windcheck/data/scroll1_tifxyz`, et les 46
traces de `docs/proximity_scroll1.jsonl` ne l'incluent pas. La première étape est
donc un téléchargement, pas un calcul. Une fois là, `10` §3bis donne une question
précise à lui poser : *les bandes 8704–9728, où le modèle produit du signal informe
que personne n'a annoté, portent-elles une proximité anormale ?* Si oui, ce « signal »
est une feuille voisine vue à travers, et la métrique devient un prédicteur.

#### La question de fond

La question qui relie les deux moitiés du travail : **une trace à forte proximité
anormale donne-t-elle une encre moins lisible ?** C'est la mesure 3.8, et elle est
maintenant *faisable* — on a la métrique d'un côté, l'AUC de l'autre, et 46 traces
mesurées. Si la corrélation existe, la métrique cesse d'être un diagnostic
géométrique pour devenir un **prédicteur de lisibilité**, ce qui est exactement ce
qu'un Progress Prize récompense.

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
6. ⚠ **Un chiffre publié dont le calcul n'est pas dans l'arbre n'est pas un
   résultat, c'est une anecdote.** Aucune mesure qui entre dans un document ne reste
   en `python -c`. Payé le 2026-08-17 : l'onde radiale (158 feuilles, 11,2 m) a dû
   être récupérée du transcript de session.
7. ⚠ **Une idée testée et écartée est un actif, pas un déchet** — à condition que la
   *raison* soit écrite. C'est ce que la §4 « Écartées » sert à conserver : sans
   elle, on repaie la même impasse.

---

## 7. L'onde radiale : ce qui marche, ce qui ne marche pas

⚠⚠ **Le code de cette section a failli etre perdu.** Il avait ete ecrit en
`python -c` inline : les resultats sont partis dans ce document et **le calcul
n'etait dans aucun fichier**. Recupere du transcript de session le 2026-08-17 et
installe dans **`experiments/src/excision/radial.py`** (sous-commandes `centre`,
`compter`, `deplier`).

**Controle de la recuperation** : le fichier reproduit exactement les chiffres
publies ici — 158 feuilles, rayon 22,7 mm, 11,2 m — et le centre re-derive de zero
tombe **au voxel pres** sur la valeur recuperee (ecart 0,0). Le centre vit desormais
dans `data/axes/PHerc0172.json`, **pas dans `/tmp`**, ou la version inline l'ecrivait.

**Regle qui en decoule** (§5.6) : *un chiffre publie dont le calcul n'est pas dans
l'arbre n'est pas un resultat, c'est une anecdote.* Aucune mesure qui entre dans un
document ne reste en ligne de commande.

2026-08-17. Idée de l'auteur : *« c'est envoyer une onde traversant toutes les
couches depuis le centre »* — chaque mur franchi est une feuille. Mesurable
**directement dans le volume**, donc sans dépendre d'aucun traçage : ça donne la
vérité contre laquelle juger les traçages.

### ✅ Ce qui marche

Centre **dérivé de la trace** (celui qui rend l'angle monotone le long du
déroulement, monotonie mesurée à **1,000**) — l'ombilic publié par
ThaumatoAnakalyptor est dans un repère qui ne correspond pas à ces traces, et
dériver se vérifie là où lire un fichier se suppose.

Sur PHerc0172, une coupe, 36 rayons :

| grandeur | valeur |
|---|---|
| feuilles traversées | **158 en médiane** (120 à 194) |
| espacement entre feuilles | **136 à 158 µm** |
| rayon extérieur | 22,7 mm |
| **longueur estimée du papyrus** | **11,2 m** ⚠ borne INFÉRIEURE (voir ci-dessous) |

⚠ **Borne supérieure** : deux feuilles fondues comptent pour une, donc le vrai
nombre de spires est **supérieur**. Et une seule coupe ne dit rien de la variation
le long du rouleau.

### 🔄 C2 — le dépliage polaire : la REPRÉSENTATION marche, le suivi PAS ENCORE

2026-08-17. `radial.py deplier` + `fusions.py`. **Classé : en cours, diagnostic établi.**

**Ce qui est acquis** : la coupe se déplie en (rayon × angle), 3000 × 18 850, et les
spires y deviennent des lignes suivables. Le zoom montre les feuilles une à une, les
zones déchirées, et des endroits où deux lignes convergent.

⚠ **Correction d'une attente** : à grande échelle les spires ne sont **pas**
horizontales, ce sont de larges dômes — PHerc0172 n'est pas concentrique autour d'un
centre unique à cette coupe, il est écrasé. Le dépliage n'exige donc pas la
concentricité, seulement que les feuilles varient **doucement** avec l'angle (dérive
mesurée : 0,125 voxel par colonne, très en deçà de toute tolérance utile).

**Ce qui ne marche pas encore** : le suivi **fragmente**. Premier passage complet —
13 074 pistes retenues et **12 249 « fusions »** sur une coupe qui compte 158
feuilles, longueur médiane 111 colonnes sur 18 850, soit ~80 morceaux par feuille.

✅ **Un point est quand même gagné sur la tentative précédente** : la répartition des
événements est **6488 en deçà du rayon médian, 6496 au-delà**. Le mode d'échec de
l'ancienne méthode — tout concentré près du centre — a disparu.

**Diagnostic, mesuré et non supposé** :

| observation | ce qu'elle élimine |
|---|---|
| 142 murs par colonne, cv **0,11** | ce n'est pas le détecteur qui flotte |
| tolérance 40 → 139 pistes traversantes | l'appariement PEUT suivre les feuilles |
| mais 40 voxels > **2 espacements** (~18) | …au prix de sauts de spire invisibles |
| prédiction de pente : 21 → **69** longues pistes | améliore ×3, ne suffit pas |

**La marche suivante est nommée, et ce n'est pas un réglage de plus** : l'appariement
est **glouton au plus proche**, ce qui est le mode d'échec classique dans un champ
dense — deux pistes se disputent le même mur et l'une repart de zéro. Le remède connu
est une **affectation globale par colonne** (Hongrois / transport optimal) qui
minimise le coût total au lieu de servir les pistes dans l'ordre d'arrivée. C'est ça
qu'il faut écrire, pas une tolérance plus large.

### ❌ Ce qui ne marche pas : la localisation des fusions par déficit de compte

Idée suivante de l'auteur : là où l'onde traverse le mauvais nombre de feuilles, il
y a une anomalie, donc on sait **où aller regarder**. Le principe est juste.

**L'implémentation ne tient pas** : 475 sites sur 180 rayons, soit 2,6 par rayon,
et **tous concentrés entre 0,5 et 2 mm de rayon** — près du centre, là où les spires
sont les plus serrées et où la détection de crêtes décroche. Ce n'est pas une carte
de fusions, c'est une carte des endroits où le compteur est peu fiable.

**Diagnostic** : compter des crêtes indépendamment à chaque angle jette
l'information qui compte — une feuille est une **courbe continue** en (angle,
rayon). Il faut la suivre, pas la recompter.
