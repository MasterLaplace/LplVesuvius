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

### 2.2 Le témoin qui sépare longueur et qualité

1.10 a montré que « les traces automatiques sont plus atteintes » est confondu par
la longueur. Scroll 1 fournit ce que Scroll 5 n'a pas :

- **`20231022170901`** : 7,66 tours, **0 croisement** — long ET propre ;
- **paire appariée `w038-045`** : deux traces de la même région, 7,92 et 7,82 tours,
  avec **408 contre 52** croisements.

**Ce que ça tranche** : si la métrique de proximité sépare ces deux-là, elle mesure
la qualité ; si elle les confond, elle mesure la longueur. *(Téléchargement en
cours.)*

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
| 3.1 | Métrique de proximité sur les 36 traces longues de Scroll 1 | passage de l'anecdote à la distribution |
| 3.2 | Normaliser la proximité **par le rayon** en plus du voisinage | 1.11 montre un gradient de 28 % non corrigé aujourd'hui |
| 3.3 | Recensement `windcheck` sur Scroll 1, confronté à leur publication | 4ᵉ vérification indépendante, sur un autre rouleau |
| 3.4 | Direction des fibres (recto/verso) comme contrainte d'orientation | problème ouvert nº5 ; les prédictions nnUNet existent déjà |
| 3.5 | Le niveau 2 de la pyramide suffit-il à séparer les spires ? | déciderait si on peut travailler à 33 Gio au lieu de 2,1 Tio |
| 3.6 | Effet de la campagne de scan (DLS 7,91 µm vs ESRF 2,4 µm) | le site montre que ça change la séparabilité ; le chiffrer |

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
