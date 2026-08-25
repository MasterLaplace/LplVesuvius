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

✅ **Papiers primaires — LUS le 2026-08-19, voir [`27`](27_ce_que_la_litterature_dit.md)** :
[Diffeomorphic Spiral Fitting](https://arxiv.org/abs/2512.04927) (Henderson, déc. 2025) et
[Ink Detection from Surface Topography](https://arxiv.org/abs/2603.27698) (Angelotti,
Nicolardi, Henderson, Seales, mars 2026). ⚠⚠ Le second donne une cible de **~1 µm** de
résolution latérale (*« lateral sampling on the order of 1 µm or finer »*, et seul
1,02 µm passe encore le seuil de DICE 0,70) — les 13 rouleaux du prix sont à
**8,64–9,36 µm**, soit un facteur **8,6 à 9,4 trop grossier**, très au-delà du point où
un modèle appris sur du fin rend **zéro** (3,40 µm). ⚠ Une première version de cette
ligne annonçait « 4 µm, facteur 2,2 » : chiffre écrit depuis le résumé sans ouvrir le
corps de l'article, corrigé après lecture intégrale.

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

### 2.1 ❌ ÉCARTÉE — remplacée par le dépliage polaire

`winding.py` mesurait la monotonie du numéro de spire le long d'un rayon. Il a été
écrit, **n'a jamais tourné jusqu'au bout** (trop lent : le découpage par tranche l'a
rendu impraticable), et il est aujourd'hui **superflu**.

Ce qu'il cherchait — une feuille qui revient sur une spire déjà dépassée — est mesuré
en mieux par `fusions.py` sur l'image dépliée : local, sans appariement, avec un témoin
sur données fabriquées, et validé en 3D à **p = 0,0001** (voir `11`).

⚠ **Le fichier est supprimé plutôt que gardé « au cas où ».** Un fichier versionné qui
ne s'exécute pas est pire qu'absent : il se lit comme une capacité disponible. La
raison de sa suppression est ici, ce qui est ce que « une idée écartée est un actif »
demande — on conserve la *raison*, pas le code mort.

### 2.1bis — le texte d'origine de l'idée

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

### 2.3 ✅ CLOSE SANS L'OMBILIC — le fichier n'existe pas, et ça n'a pas d'importance

`18` M1 : `umbilicus.txt` n'existe **sur aucun des 4 corpus** (zéro occurrence), et le
centre utilisé n'est pas un barycentre mais un **ajustement sur la monotonie** de la
spirale (mesurée à 1,000). Mesuré : déplacer le centre de **3,16 mm** — 22 écarts
inter-feuilles — bouge l'invariant de **1,75 %**, c'est-à-dire **sous** son propre cv de
1,8 %. La question était donc mal posée : l'invariant ne dépend pas du centre.

#### Le texte d'origine

1.11 utilise un barycentre par tranche, sur **une seule trace** qui ne couvre pas
tout le rouleau — donc centre biaisé. À refaire avec `umbilicus.txt` sur Scroll 1.

### 2.4 ✅ FAITE — la théorie du dommage : **à moitié confirmée, et ce n'est pas un U**

Mesuré sur 3 coupes (`shape.py degradation`, niveau 2), indicateur = **contraste
feuille/interstice** normalisé par la hauteur du pic, donc sans dimension.

| rayon | z = 2521 | z = 6967 | z = 11413 |
|---|---:|---:|---:|
| 0,0–2,8 mm (**cœur**) | **0,493** | **0,463** | 0,556 |
| 5,7–8,5 mm | 0,585 | 0,581 | 0,580 |
| 8,5–11,3 mm | 0,584 | **0,592** | 0,549 |
| 17,0–19,9 mm | 0,559 | 0,573 | 0,540 |
| 19,9–22,7 mm (**bord**) | **0,544** | **0,558** | **0,535** |

**Ce que l'hypothèse gagne** : le **cœur est réellement le plus dégradé** sur 2 coupes
sur 3 — déficit de **20 %** contre la meilleure couronne. C'est la partie « la fumée
est passée par le trou central ».

**Ce qu'elle perd** : l'extérieur n'est **pas** le plus abîmé. Il décline, mais de
**5 à 8 %** seulement, contre 20 % au cœur. Le profil n'est donc **pas un U** : c'est
*cœur mauvais → plateau → léger déclin*. Le minimum tombe à la bande 0 sur 2 coupes
sur 3, c'est-à-dire à un **bord** — or un U exige un minimum intérieur.

⚠ **Limite** : la bande extérieure a 30 % d'échantillons en moins (le rouleau s'y
termine), donc une part du déclin est un effet de bord et non une dégradation.

⚠ **Conséquence pratique, et elle est bonne** : si l'extérieur n'est pas ruiné, ce
qu'on a perdu du **début** des textes est bien moindre que craint. Et « où semer en
priorité » n'a pas de réponse tranchée par cette mesure — le plateau est large.

### 2.4bis ✅ Et pourquoi le rayon varie le long de z : le rouleau est ÉCRASÉ

`shape.py ellipticite`, 8 coupes, niveau 2 :

| grandeur | étendue | cv |
|---|---|---:|
| rapport des axes | **1,26 à 1,57** | — |
| périmètre du contour | 144,0 à 157,7 mm | 0,035 |
| rayon médian | 21,3 à 25,1 mm | 0,051 |

Le rouleau est **nettement elliptique partout**, et le plus écrasé au milieu (1,57 en
z = 4300) — exactement là où le rayon médian est le plus petit. C'est donc bien
l'écrasement qui explique une part du U mesuré le long de z.

⚠ **Mais la question n'est pas tranchée** : le périmètre est plus stable que le rayon
(rapport 0,69) sans l'être *beaucoup* plus. Un écrasement pur garderait le contour
constant ; ici il perd 9 %. **Les deux jouent, aucune n'est écartée.**

⚠⚠ **Deux défauts de ma propre mesure, trouvés avant de conclure** :
1. la portée plafonnait à 22,7 mm et l'axe long ressortait à **22,7 mm sur les huit
   coupes** — la mesure saturait contre sa propre limite. Symptôme à reconnaître : une
   valeur *identique* partout. Le code refuse désormais plutôt que de rendre un chiffre
   saturé ;
2. mon « périmètre » valait `Σ r·dθ`, c'est-à-dire **2π × rayon moyen** — il ne portait
   aucune information indépendante du rayon, donc comparer sa dispersion à celle du
   rayon revenait à **comparer une grandeur à elle-même**. Corrigé par la vraie
   longueur d'arc, avec le terme `dr/dθ`.

### 2.4ter — le texte d'origine de l'hypothèse

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
| 3.2 | ✅ **TRANCHÉE — le défaut est réel et SANS CONSÉQUENCE** | La fenêtre « locale » couvre bien **96,9 % d'un tour** et le rayon y varie de **59,5 %** de l'étendue radiale : le constat de non-localité tient. Mais le remède de principe — une référence en **boule 3D**, locale en rayon par construction — rend la métrique **nettement PIRE** : rho **+0,474** (boule 200 vx) et **+0,560** (boule 400 vx) contre **+0,769** pour la fenêtre actuelle. Et les fenêtres en colonnes forment un **plateau** : **+0,755 à +0,805** de ±10 à ±150 colonnes, donc la largeur n'est pas le facteur limitant. **Deux mesures expliquent pourquoi.** (1) Les deux références **s'accordent à 0,3 %** sur les cellules ordinaires (boule/bande = **1,001** en médiane sur 45 traces) : l'espacement ne varie pas assez avec le rayon pour que la non-localité compte. (2) La boule **s'effondre spécifiquement aux cellules signalées** (**0,766**, sur **43 traces sur 45**, Wilcoxon apparié **p = 1,4e-09**) — un site de croisement est une région 3D compacte, donc une boule centrée dessus est pleine d'autres cellules du même site, **l'anomalie normalise sa propre référence**. Une bande de colonnes est étroite en colonne mais **entière en ligne**, donc l'essentiel de son contenu vient de régions saines. ⚠ **Leçon générale** : une référence doit être **large dans la direction où l'anomalie est petite**. Outils : `baseline_sweep.py`, `variant_correlate.py` |
| 3.3 | ✅ **FAITE** — recensement Scroll 1 vs publication | **55/55 triangles et 55/55 contacts** concordants. Deux corpus entiers vérifiés |
| 3.4 | ❌ **RÉFUTÉE** — le signe s'inverse de n = 12 (+0,330) à n = 54 (**−0,192**), `14`. L'orientation reste mesurable (cohérence 0,64) ; c'est son lien aux croisements qui ne tient pas. ⚠ Le site en fait *le* critère visuel : l'idée est bonne, notre mesure ne l'était pas. Détail historique :  `14`. Tenseur de structure sur les volumes de surface ESRF, cohérence jusqu'à **0,64**. ⚠⚠ Mais l'angle reste à **90–97° sur les 109 couches** : pas de bascule. La mesure répond bien au contenu (l'angle ne s'affole que là où la cohérence tombe à 0,06, c'est-à-dire **dans l'interstice entre feuilles**). **Pivot** vers la cohérence *spatiale* : deux fenêtres voisines sur la même feuille doivent s'accorder. Sur 12 segments, désaccord **4,3° à 42,5°**, rho **+0,330** avec les croisements publiés — mais ⚠ **à n = 12 la mesure ne détecte qu'un rho ≥ 0,73**, donc le zéro n'est pas informatif. Campagne sur 80 segments en file |
| 3.5 | ✅ **FAITE — OUI, et c'est un facteur 64 sur la donnée** | **89 %** des murs conservés au niveau 2 (33 Gio) contre le niveau 0 (2100 Gio). La **falaise est entre les niveaux 2 et 3** : 89 % → 47 %. ⚠ Et un premier essai rendait « 53 feuilles au niveau 1 » : c'était un artefact de **seuil**, pas de résolution — réduire un volume moyenne les voxels, donc remonte le fond, et un seuil absolu calé sur le niveau 0 ne veut plus rien dire ailleurs. Outil : `pyramid.py` |
| 3.6 | ✅ **FAITE pour Scroll 1** · ❌ **IMPOSSIBLE pour les 4 sites** — PHerc0172 ne publie que du 7,91 µm (deux volumes, vérifié sur le bucket le 2026-08-19), donc les sites de fusion ne peuvent pas être revus plus fin. La partie appariée reste faite : | Le bucket publie les volumes de surface en **45,532 / 2,4 / 1,129 µm**, et **37 segments de Scroll 1 les ont tous les trois**. PHerc0139 publie même le même segment tracé en 7,91 **et** 2,403 µm. La comparaison est donc **appariée** — même trace, deux résolutions — au lieu d'être une comparaison entre corpus. ⚠ Et à 1,129 µm la pile de 109 couches ne fait que **123 µm**, soit **moins qu'une épaisseur de feuille** : c'est une limite à connaître avant d'y chercher une structure transverse |
| 3.7 | ✅ **FAITE** — seuil : suppression impossible, mais PLATEAU établi | **Le supprimer dégrade la métrique** : le déficit moyen sans seuil tombe à rho +0,340 (contre +0,769), parce qu'il est dilué par la masse des cellules normales — **le signal est dans la queue extrême**. Mais le balayage montre un **plateau de 0,15 à 0,40** (rho 0,759 à 0,779), puis un effondrement au-delà de 0,5. Le seuil n'est donc pas réglé : n'importe quelle valeur de la plage donne la même réponse |
| 3.8 | ✅ **FAITE — la réponse est NON, et elle est bien étayée** | Corrélation par tuile entre la proximité anormale et l'accord encre prédite ↔ étiquetage humain, sur le segment `20230909121925` (le seul qui ait **et** un maillage **et** une carte d'encre). **Tuiles de 512 px** : n = 34, rho **+0,186** (p = 0,29). **Tuiles de 256 px** : n = 89, rho **+0,019** (p = 0,86). ⚠ Et le **contrôle est plat des deux côtés** (−0,031 et −0,010 sur les tuiles vides), donc ce qu'on mesure n'est pas la quantité d'encre. À n = 89 la mesure détecterait un rho de 0,3 à 80 % de puissance : le zéro est donc **informatif**, pas un manque de données. Outil : `src/encre/proximity_vs_ink.py` |
| 3.11 | ✅ **FAITE — un instrument de tracé qui ne demande RIEN d'autre que les couches** | La **profondeur de surface** (`12`) : part des fenêtres dont le pic de contraste local tombe dans le tiers central des couches lues. Scroll 1 **63 %** (`20231022170901`) et **50 %** (`20230909121925`), Scroll 4 **7 %** ; écart interquartile 4,0 / 11,5 contre **22,0**. ⚠⚠ Scroll 4 est **bimodal** — 92 fenêtres au bord bas, 49 au bord haut — donc sa surface **voyage**, ce n'est pas un décalage uniforme. ⚠ Le filtre `--from-layer/--to-layer` est indispensable : un segment téléchargé avec 38 couches et un autre avec 26 n'ont pas des tiers centraux de même largeur (76 % → 63 % une fois la comparaison rendue légitime). ⚠ Elle **ne classe pas** la lisibilité : le segment qui donne l'AUC 0,925 est le moins bon des deux Scroll 1. Outil : `src/volume/depth_profile.py` |
| 3.13 | ✅ **FAITE — la métrique de `07` a un DOMAINE DE DÉFINITION, et personne ne l'avait écrit** | Sur les 53 traces de Scroll 5, **44 rendent zéro cellule** — pas « peu », zéro. La coupure est exactement à **un tour** : mesurées 2,99–9,07 tours, écartées 0,50–**1,00**. Une trace qui ne fait pas un tour ne repasse jamais au-dessus d'elle-même, donc il n'existe aucune paire éloignée-en-paramétrisation-et-proche-en-3D. ⚠ Et les 9 « survivantes » sont **neuf morceaux du même segment** : n = 1, pas 9. `07` §7. L'outil refuse désormais **avec sa raison** au lieu d'un message qui ressemble à une panne |
| 3.14 | ✅ **FAITE — le seuil d'un tiers : ni arbitraire, ni supprimable** | `07` §8. Aucune grandeur sans seuil ne l'égale (`shortfall` **+0,340**, `ratio_p5` **−0,512**, contre **+0,769**) : le signal est dans la queue extrême et toute moyenne l'y noie. Ce qui le défend est un **plateau** — rho 0,759 à 0,779 de 0,15 à 0,40, un facteur **2,7** sans que rien bouge, puis effondrement à 0,50. Un paramètre sur-ajusté fait un **pic** ; celui-ci fait un plateau |
| 3.12 | ✅ **FAITE — le détecteur ne transporte pas sur Scroll 4, et on sait probablement pourquoi** | Passe complète (107 730 fenêtres, 42,6 min, 48,1 M pixels). Le juge calibré rend une lisibilité de **1 à 3** sur la bande la plus chargée, quand le calibrage sépare vierge **0–1** de texte **3–6** : **pas de séparation**. ⚠ Scroll 4 n'offre **aucun témoin vierge** (bande la plus pauvre à **4,59 %** contre 1,14 % sur Scroll 1) — le plafond a été relevé en le disant, et le fichier de résultats porte `control_kind`. ⚠⚠ **Limite du protocole mesurée pour la première fois** : le même panneau, à température zéro, donne **1 puis 2 puis 0** glyphes selon son voisin — donc toute lecture isolée à lisibilité ≤ 3 doit être répétée en compagnie différente. Cause probable : 3.11 |
| 3.10 | ✅ **FAITE — le défaut DÉRIVE, et le crible ne peut pas le voir** | Appariement **prédictif** entre coupes (`track_z.py`) : même tolérance que la mesure publiée, seul le **centre** de la fenêtre devient une prédiction. Le site du §7 forme une piste de **5 coupes traversant 4,75 mm de rayon** (dérive **1,50 mm/mm**), contre 3 coupes / 1,42 mm à fenêtre fixe — **p = 0,0010** contre une permutation, **0,005 après Bonferroni** sur les 5 grandeurs. La lecture « défauts d'un millimètre » est **écartée**. ⚠⚠ Et le balayage niveau 2 ne peut pas confirmer : dans la **même plage de z**, le niveau 0 trouve le site à **77–88 % du tour** et le niveau 2 **rien entre 74 % et 88 %** — le crible regarde ailleurs, il ne rate pas par manque de sensibilité. Donc les **18 % de colocation** du rouleau entier portent sur une **autre population de sites**. ⚠ Ma grandeur discriminante annoncée (la *rectitude*) a **échoué** : p = 0,82, une chaîne aléatoire de 3 points est monotone une fois sur deux |
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

### B. ✅ FAITE — le contrôle en aveugle des modèles de langue

**Fait le 2026-08-17** : `09` §9, quatre conditions dont `vierge|vierge`, côté tiré au
sort, température zéro — **15/16, zéro fabrication**, lisibilité séparant sans
chevauchement le vierge (0–1) du texte (3–6). ⚠ Et une limite du protocole mesurée le
2026-08-18 (`09` §12) : **la lecture d'un panneau dépend de son voisin**, donc toute
lecture isolée à lisibilité ≤ 3 doit être répétée en compagnie différente.

Le texte d'origine de la tâche : Soumettre des rendus **dont le texte est publié**,
mélangés à des rendus de bruit, et mesurer si le modèle retrouve les premiers et
refuse les seconds. Sans cette calibration, son avis sur du texte inconnu n'est pas
une donnée. ⚠ À faire **avant** de lui montrer quoi que ce soit d'inconnu, sinon on
ne pourra plus le calibrer sans biais.

### C. ✅ FAITE — et la règle NE réplique PAS

Quatre corpus, 110 segments de plus (`19` §11-12) : Scroll 1 **+0,539**, PHerc0139
**−0,229**, PHerc1667 +0,425, PHerc0172 −0,217. ⚠ Et mon explication par un effet de
plancher couvrait **un corpus sur trois**. La règle est une propriété du corpus publié de
Scroll 1, et c'est publié comme tel.

#### Le texte d'origine

Tous les chiffres de `07` et `08` viennent de Scroll 1. Scroll 5 se comporte déjà
différemment sur le confond longueur/qualité. Rien ne dit que l'AUC voyage.

### D. ✅ FAITE — et la réponse est NON

C'est la mesure 3.8 : rho **+0,019 à n = 89**, contrôle plat, et à ce n un rho de 0,3
serait détectable à 80 %. Le maillage manquant a été obtenu par `src/outils/ppm_to_tifxyz.py`.
**La métrique mesure un défaut de la TRACE, pas du RÉSULTAT.**

#### Le texte d'origine

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

## 3ter. ⭐ Ce que le NON de 3.8 change

La métrique de `07` **corrèle avec les croisements publiés** (rho +0,77, `06` §3.1)
mais **pas avec la lisibilité** (rho +0,02 à n = 89). Les deux faits tiennent ensemble
et disent quelque chose de précis :

> *Elle mesure un défaut de la TRACE, pas un défaut du RÉSULTAT.*

Une auto-intersection est réelle et détectable géométriquement ; elle n'empêche
apparemment pas l'encre d'être trouvée là où un humain l'a tracée.

⚠ **Conséquence pour l'objectif** (le déroulement, pas le texte) : la proximité reste
un **contrôle qualité de trace** utile et bon marché — elle attrape ce que `windcheck`
attrape, sans volume ni modèle. Mais elle ne peut pas servir d'**argument sur le
résultat final**, et il ne faut plus la présenter comme telle.

⚠ **Portée honnête** : une seule trace. C'est la seule du dépôt qui ait à la fois un
maillage et une carte d'encre — les 46 traces mesurées en `07` n'ont pas d'encre, et
les segments à encre n'avaient pas de maillage avant que `src/outils/ppm_to_tifxyz.py`
n'existe. Élargir demande de convertir d'autres `.ppm`, ce qui est maintenant **une
commande**, plus une décision.

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
   DLS/ESRF) montrent que l'espacement varie **selon l'endroit**. ⚠ Corrigé le
   2026-08-19 : cette ligne annonçait « un facteur **trois** », et les deux chiffres que
   ce document mesure lui-même donnent **+28 %** (mesure 1.11 : 158 µm au cœur, 203 µm
   dehors), soit un facteur **1,28**. La règle qui suit — normaliser, ou mieux, rester
   **ordinal** — ne dépend pas de l'amplitude ; c'est le chiffre qui était faux, pas
   l'énoncé.
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

### ✅ C2 — le dépliage polaire : CLOS, le suivi a été remplacé et non réparé

**Clos le 2026-08-18.** Le suivi par continuité de crêtes fragmentait ; il n'a pas été
réparé, il a été **remplacé** par la méthode du **doublement d'écart** (`11` §6), qui
ne suit rien — elle normalise l'écart entre murs par l'espacement **local** et cherche
les cellules où il double. C'est la 4ᵉ formulation, et elle a donné les 4 candidats du
`11` §7, leur persistance à p = 0,0001, et la dérive mesurée du `11` §11.

⚠ La leçon vaut d'être gardée : trois formulations ont échoué, et c'est la troisième qui
a **désigné** la bonne — pas un réglage de la première. Le texte d'origine :

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

#### ⚠⚠ Trois hypothèses posées, TROIS réfutées par la mesure

Le 2026-08-17, après avoir nommé le glouton comme cause :

| hypothèse | verdict | mesure |
|---|---|---|
| l'appariement glouton fragmente → affectation globale (Hongrois) | ❌ **PIRE** | 17 pistes longues contre **69** pour le glouton |
| les pistes en sursis volent des murs aux saines | ❌ réfutée | sursis 0 → 10 pistes longues, sursis 20 → **17** |
| le détecteur perd les murs | ❌ réfutée | **92 %** des murs retrouvés à moins de **2 voxels**, 99,2 % à 12, médiane **0** |

⚠ Le Hongrois est pire **pour une raison de fond, pas de réglage** : il minimise le
coût *total*, donc il peut sacrifier un appariement quasi certain (distance 0,5) pour
améliorer la somme ailleurs. En suivi, un appariement à coût nul est presque sûrement
le bon et ne doit jamais être échangé. *L'optimalité globale n'est pas le bon
objectif ici* — ce qui est l'inverse de ce que la littérature suggère pour un champ
dense.

#### ✅ La vraie cause, mesurée : ce sont les ÉTIQUETTES qui churnent, pas les feuilles

| grandeur, par colonne | valeur |
|---|---|
| murs trouvés | 126 |
| murs **appariés à une piste** | **125** |
| pistes vivantes | 186 |
| pistes neuves | **1** |

**125 murs sur 126 sont appariés à chaque colonne.** La couverture est donc
quasi parfaite : aucune feuille ne disparaît. Ce qui meurt, c'est l'**identité** —
une piste qui perd son mur une fois continue d'extrapoler, s'éloigne, ne le retrouve
jamais, et une piste neuve reprend le mur.

⚠⚠ **Conséquence : les 12 249 « fusions » du premier passage étaient des changements
d'étiquette, pas des soudures.** Le chiffre ne mesurait rien de physique.

**Ce que ça change pour la suite.** Le signal de fusion ne doit pas être *la mort
d'une piste* — trop sensible à l'identité — mais **la disparition d'un mur**, c'est-à-
dire une baisse du COMPTE local qui **persiste** sur de nombreuses colonnes. Et cette
quantité-là, la mesure ci-dessus montre qu'elle est propre : 126 ± 3 murs par colonne,
soit 2,4 % de dispersion. Une soudure retirerait un mur *durablement*, ce qui sort de
cette dispersion.

C'est aussi la mesure qui ne demande **aucun suivi**, donc aucune des trois
hypothèses ci-dessus. À écrire ensuite.

#### ✅ Le doublement d'écart : la 4ᵉ formulation, la moins mauvaise

Une soudure ne fait pas disparaître un mur dans le bruit du comptage global : elle
**double l'écart local** entre deux murs voisins. C'est une quantité *locale*, mesurée
dans une colonne unique, qui ne demande **aucun appariement entre colonnes** — donc
aucune des trois hypothèses réfutées ci-dessus.

⚠ Normalisée par l'espacement **local** et jamais par un seuil en micromètres :
l'espacement varie d'un facteur trois selon le rayon (158 µm près du cœur, 203 µm vers
l'extérieur), donc un seuil absolu attraperait le cœur et raterait le bord.

**Contrôle** (`fusions.py ecarts-controle`) : lignes fabriquées intactes → **0 site**,
avec une soudure → exactement **1**.

**Deux versions ont échoué avant celle qui tient**, et les deux échecs sont instructifs :

1. **Chaînage de marques** — deux paramètres se battaient : la persistance exigeait
   200 marques par groupe, la fenêtre angulaire en plafonnait les groupes à **164**,
   donc zéro site. Les régler l'un contre l'autre jusqu'à voir des sites apparaître
   aurait été choisir un nombre pour que le réglage du jour passe. Cause mesurée : le
   marquage est **intermittent** (écart médian de 6 colonnes entre marques, q90 à
   **891**), et un drapeau binaire aussi bruité ne se chaîne pas.
2. **Densité sans exclusion du cœur** — a redécouvert *exactement* le mode d'échec
   historique : rayon médian **0,5 mm**, tous les premiers sites au centre.

⚠⚠ **Et la cause du second n'est pas du bruit, c'est une dégénérescence.** Au rayon
*r*, deux colonnes voisines de l'image dépliée échantillonnent des points distants de
`2πr/18850` voxels : à *r* = 100, cela fait **0,03 voxel**, donc une trentaine de
colonnes lisent **le même pixel**. Le cœur est inexploitable *par construction du
dépliage*. Exclu sous 2,4 mm, et la raison est écrite dans le code.

**État après exclusion** : **8 cellules anormales sur 1582** (0,51 %), taux de fond
6,6 %, réparties de 2,4 à 18,0 mm, **4 en deçà du rayon médian et 4 au-delà** — le
déséquilibre historique a disparu.

#### ✅ Le contrôle a été fait, et il a confirmé le doute

Le doute écrit ici même — *4 des 8 cellules sont pile à la frontière de coupe, ça
ressemble à un effet de bord* — a été tranché en faisant varier `--min-radius` :

| coupe | cellules | rayon du site le plus interne |
|---:|---:|---:|
| 1,6 mm | 11 | 1,4 mm |
| 2,4 mm | 8 | 2,4 mm |
| 3,6 mm | 5 | 3,3 mm |
| **4,7 mm** | **4** | **17,1 mm** |
| **6,3 mm** | **4** | **17,1 mm** |

**Le site le plus interne suit la coupe exactement** (1,4 pour une coupe à 1,6 ; 2,4
pour 2,4 ; 3,3 pour 3,6) — donc ce sont bien des **artefacts de bord**, et non des
soudures. Au-delà de 4,7 mm ils disparaissent et il reste **4 cellules stables**, que
déplacer encore la coupe ne bouge plus.

#### 🎯 Le résultat : 4 candidats stables, tous vers 17 mm

Coupe validée à 4,7 mm — **4 cellules anormales sur 1392** (0,29 %), fond 6,6 % :

| rayon | colonne | taux de doublement | écarts |
|---:|---:|---:|---:|
| 18,0 mm | ~14 000 | **20,3 %** | 1389 |
| 17,1 mm | ~16 500 | 19,3 % | 1350 |
| 17,6 mm | ~15 500 | 18,8 % | 1437 |
| 17,1 mm | ~16 000 | 17,1 % | 1439 |

⚠ Les quatre sont **groupés** : rayons 17,1 à 18,0 mm, colonnes 14 000 à 16 500 sur
18 850, soit un secteur angulaire d'environ **50°**. Ce n'est pas une dispersion de
bruit, c'est **une région**. Elle est à 17 mm sur un rayon extérieur de 22,7 mm, donc
dans le tiers externe — cohérent avec la théorie de l'auteur selon laquelle les
couches externes ont le plus souffert.

⚠ **Ce qui n'est PAS établi** : que ces quatre cellules soient des soudures. Elles sont
des endroits où l'écart entre feuilles double trois fois plus souvent qu'ailleurs, ce
qui est *compatible* avec une soudure, une déchirure ou un vide. Trancher demande de
les regarder — c'est ce que la piste C4 du vivier proposait (revoir les sites suspects
à 2,4 µm à l'ESRF), et c'est maintenant une liste de **quatre** endroits précis au lieu
d'un rouleau entier.

**Fichiers** : `experiments/src/excision/radial.py` (dépliage) et `fusions.py`
(`controle`, `chercher`, `ecarts`, `ecarts-controle`, `densite`). Tout est en fichiers
versionnés, pas en `python -c` — cf. §5.6.

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
