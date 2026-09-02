# 68 — Lire le papier en entier, et ce que ça rouvre

> ⚠⚠⚠ **Deux conclusions fermées de ce dépôt sont fausses, et c'est la lecture intégrale du
> papier de référence qui l'a montré.** 46 pages, 27 auteurs, figures comprises. Le
> [`27`](27_ce_que_la_litterature_dit.md) §3 l'avait lu pour **auditer sa nouveauté** — ce
> qu'il ne fait pas, ce qu'il ne mesure pas, ce qu'il laisse ouvert. Il ne l'avait jamais lu
> pour la question que l'auteur a posée le 2026-09-02 : *« vingt personnes ont fait le travail
> à la main pendant 700 heures — ultimement, en dernier recours, on peut faire exactement comme
> eux, avec la puissance des machines. »*

**La source** : `data/site/scrollprize.org/pdf/main.pdf`, Angelotti *et al.*,
« Complete virtual unwrapping and reading of a rolled Herculaneum papyrus », arXiv
**2606.29085**, 27 juin 2026, 46 pages. Toutes les citations ci-dessous portent leur page.

---

## 1. ⭐⭐⭐ Le geste qui coûte 775 heures est un **pinceau**, et son interface est un fichier

Le papier chiffre le coût en une ligne, p. 28 :

> *« The unwrapping was completed using the most efficient semi-automated segmentation tooling
> available at the time, a wrap by wrap copy tool combined with **~25 hours per wrap of manual
> annotation**. »*

31 spires × 25 h ≈ **775 heures**. Ce que le `27` n'avait pas fait, c'est ouvrir le code pour
voir **à quoi** ces heures se dépensent. Le papier publie un commit épinglé (p. 30) :

> *« Code sufficient to reproduce the main analyses […] is available at
> `github.com/ScrollPrize/villa/commit/e583fb67468f483fadd73d52e06f0ab0fe5ba813`. »*

⚠ Notre clone de `villa` est en profondeur 1 et ne le portait pas ; il a été récupéré
(`git fetch --depth 1 origin e583fb6…`, 2026-09-02) et il est maintenant sur le disque. Ce
qu'on y trouve, dans `volume-cartographer/apps/VC3D/segmentation/tools/` :

    ApprovalMaskBrushTool.cpp
    ApprovalMaskBrushTool.hpp

Un **pinceau**. Avec des modes `Approve` / `Unapprove`, des coups de brosse, une pile d'annulation
et un raccourci clavier. C'est ce que le papier appelle, p. 18, sa seule barrière qualité — la même phrase que
[`27`](27_ce_que_la_litterature_dit.md) §3 cite pour dire qu'aucune métrique ne la remplace :

> *« **Regions judged geometrically consistent with a single sheet** were marked with an
> approval mask. »*

⭐⭐⭐ **Et l'interface est ouverte.** `QuadSurface::channel(nom)` charge paresseusement
`<dossier_du_segment>/<nom>.tif`, et le chargeur adopte **tout** `.tif` du dossier dont le nom
n'est ni `x`, ni `y`, ni `z` (`core/src/QuadSurface.cpp:1861-1865`). Le masque est lu sous le
nom `"approval"` et il **gouverne la ré-optimisation du maillage** (`core/src/GrowPatch.cpp`,
`make_approved_mask`, l. 133).

> **Écrire `approval.tif` à côté de `x.tif`, `y.tif`, `z.tif` EST l'intégration entière.**
> Pas d'API, pas de patch, pas de fork. Un fichier.

⚠⚠ Ce que ça veut dire pour ce dépôt, et il faut le dire sans emphase : l'article qu'on écrit
s'appelle *« Measuring segmentation quality without ground truth in virtual unwrapping »*.
C'est **exactement** la question que le pinceau pose à un humain, région par région, 775 heures
durant. Nos instruments ne sont pas une contribution à côté du problème — ils calculent la
grandeur que ce pinceau peint à la main, et le point d'entrée pour la livrer est un `.tif`.

⚠ Ce que ça ne veut PAS dire : que nos masques seraient assez bons. On ne l'a jamais mesuré
contre un masque d'approbation humain, et aucun n'est publié à notre connaissance. C'est la
première chose à chercher.

---

## 2. La méthode, telle qu'elle est réellement, pour pouvoir la refaire

Reconstituée depuis les Methods (p. 12-21), dans l'ordre. **Ce qui est humain est marqué.**

| # | étape | outil / paramètres publiés | humain ? |
|---|---|---|---|
| 1 | photogrammétrie de l'extérieur | Sony α6300, plateau Foldio360, marqueurs ArUco ; masques SAM 2.1 ; `pgs-recon` (OpenMVG + OpenMVS) | pose et manipulation |
| 2 | coque de transport | `ScrollCase` → STL → nylon HP Multi Jet Fusion | conservateur |
| 3 | scan | BM18 ESRF, **2,4 µm / 0,22 m / 78 keV**, wiggler filtré saphir 20 mm + or 0,1 mm, scintillateur GAGG:Ce 50 µm, optique tandem Zeiss Otus 100 + Nikkor 200 (ON 0,35), PCO edge bi-10 ; hélicoïdal jusqu'à 4 positions latérales | non |
| 4 | prétraitement détecteur | dark/flat, pixels chauds (médiane 3×3, seuil 0,1), correction de distorsion par grille de fentes, rééchantillonnage bilinéaire arrière | non |
| 5 | phase | Paganin **δ/β = 1000**, puis masque flou inverse **c = 4,0 ; σ = 1,2 px**, écrêtage [10⁻⁶, 10] avant log | non |
| 6 | fusion et reconstruction | apodisation en fonction d'erreur, centre de rotation **dépendant de z**, alignement par corrélation des recouvrements tous les **5°**, rétroprojection hiérarchique généralisée sur GPU | non |
| 7 | sortie | 32 → 16 bits (saturation 0,01 %), binning ×2 et ×4, JPEG2000 lossy 10, **uint8 OME-Zarr 6 niveaux**, ~**20 To** par volume | non |
| 8 | prédiction de surface recto | nnU-Net 3D résiduel, patchs **256³**, z-score, 2 canaux, perte **Medial Surface Recall** + CE + Dice, batch 2, AMP fp16, clip 12 ; **116 531 patchs** ; arrêté à **3 864 epochs sur 7 500** | **labels manuels** |
| 9 | maillage quad `tifxyz` | centre-lignes sur 3 familles de coupes → évidence d'orientation en bacs spatiaux ; croissance depuis une graine ; optimisation conjointe régularité / lissage / orientation / proximité | graines |
| 10 | assemblage | outil de traçage sur un grand jeu de maillages de base chevauchants ; `mesh-offset` par lancer de rayons le long des normales | choix des régions |
| 11 | **correction** | points de contrôle, déplacement de sommets, `push`/`pull` le long de la normale, inspection sur coupes orthogonales, **masque d'approbation au pinceau**, ré-optimisation locale, *inpainting* géométrique des trous | ⭐ **~25 h / spire** |
| 12 | aplatissement | quads → triangles, UV initiales depuis la grille, **SLIM** avec énergie de Dirichlet symétrique, bord contraint | non |
| 13 | rendu | 65 échantillons le long de la normale, Δ = 1 voxel, offsets −32…+32, soit **153,6 µm** à 2,4 µm ; interpolation trilinéaire | non |
| 14 | étiquettes d'encre | photographies IR MegaVision (E7 50 Mpx, objectif apochromatique UV-IR), projection orthographique du volume, **recalage par points de contrôle manuels** | ⭐ recalage |
| 15 | modèle d'encre | U-Net à encodeur **ResNet3D-50** (Kinetics-700 `r3d50_KM_200ep`) et décodeur 2D, *pooling* sur la profondeur ; entrée **62 × 256 × 256** ; Dice 0,5 + SoftBCE 0,5 (lissage 0,25) ; AdamW, OneCycle 3·10⁻⁴ ; **1 × H100** ; ≈ **2 h** par run | non |
| 16 | pseudo-labels | 5 tours ; 3 396 → 8 970 → 15 286 → 24 773 → **33 061** tuiles | ⭐ jugement visuel |
| 17 | relecture | 8 papyrologues, translittération, crochets et points souscrits | ⭐ |

**Ce qu'il faut retenir pour « faire comme eux, en plus vite »** : sur dix-sept étapes, quatre
sont humaines, et **une seule** porte les 775 heures — l'étape 11. Tout le reste est déjà
automatique et publié. La question n'est donc pas de refaire le pipeline : c'est de **remplacer
l'étape 11**.

⚠ Deux détails qui coûteraient cher à redécouvrir :

- le rendu ne fait **pas** d'isosurface : il empile 65 échantillons le long de la normale. Notre
  marcheur volumique a trouvé la même chose par la mesure (aucun seuil ne sépare les feuilles) ;
- le maillage n'est **pas** la sortie du réseau. La prédiction voxel n'est *« used **only as an
  intermediate cue** »* (p. 17) parce qu'elle contient fusions, trous et faux positifs. Le Dice
  de la classe surface vaut **0,308** (Suppl. Table 1, p. 41). Un projet qui prendrait la
  segmentation pour la surface reproduirait un défaut que les auteurs ont explicitement écarté.

---

## 3. ⭐⭐⭐ « Trois paramètres couplés » n'en font qu'**un**

Le site du prix nomme *« Three coupled scan parameters »* et `campagnes_de_scan.py` bute
dessus : *« les trois grandeurs co-varient par campagne […] aucune des trois n'est isolée par
cette mesure-ci. »*

**Il n'y a pas à les isoler.** Le contraste ne vient pas de l'absorption — le papier le dit,
p. 14 : *« the absorption contrast being very low for carbon-based material in hard X-rays »* —
il vient des franges de Fresnel. La largeur de la première frange vaut $\sqrt{\lambda D}$, et
ce qui décide de sa visibilité est son rapport au pas d'échantillonnage :

$$ F = \frac{\sqrt{\lambda D}}{p}, \qquad \lambda = \frac{hc}{E} $$

Mesuré sur les **59 scans publiés** (`nombre_de_fresnel.py`, 13 contrôles) : $F$ **ordonne les
verdicts que les auteurs écrivent sous leurs propres panneaux**, aux deux bouts.

| $F$ | scans | ce que le papier écrit |
|---:|---|---|
| 0,245–0,298 | 45,5 µm / 11 m | repérage grossier |
| **0,388–0,415** | **31 scans, dont les 13 rouleaux du prix** | *« the 9.362 µm panel is **pixel-limited**, the inset shows the bare voxel grid »* (p. 36) |
| **0,733–0,747** | **2,4 µm / 0,2 m — production** | *« the 2.4 µm appears as the **best possible resolution** on a setup compatible with large scrolls »* (p. 36) |
| 0,848 | 4,317 µm / 1,2 m | *« haze-limited »* |
| 0,954 | 2,215 µm / 0,4 m | supervision fragments |
| **1,816** | 1,129 µm / 0,2 m | *« fine delaminations begin to blur due to a **too long propagation distance for a so small pixel size** »* |

⭐ La dernière ligne est la vérification qui compte : *« distance trop longue pour un pixel si
petit »* **est la définition de $F > 1$**, écrite en mots par les auteurs, sur un panneau qu'ils
jugent dégradé.

**Les 13 rouleaux du prix sont à $F = 0{,}39$, soit 53 % du régime de production.**

⚠⚠ **Ce que $F$ n'explique pas, et le corpus le prouve** : la **décohérence**. 500P2 à 4,317 µm
/ 1,2 m ($F = 0{,}85$) est *« haze-limited »* ; le même fragment à 2,215 µm / 0,4 m
($F = 0{,}95$) ne l'est pas. Même $F$, verdict opposé, et **la seule chose qui change est $D$**.
Le modèle honnête a deux termes : $F$ dit si la frange est résolue, $D$ dit si l'échantillon
l'a déjà brouillée. `--verifier` contrôle **les deux**, et le second est un contre-contrôle :
un fichier qui vendrait $F$ comme théorie complète cacherait sa moitié manquante.

### ⚠⚠⚠ Et le diagnostic des 13, qui suit des deux

Ils sont du mauvais côté **des deux à la fois** : $F = 0{,}39$ (frange non résolue) **et**
$D = 1{,}2$ m — la distance à laquelle le papier mesure l'apparition de la décohérence, sur
`PHerc0268`, **qui est lui-même l'un des treize** (Ext. Data Fig. 2c, p. 34) :

> *« Once again, this is due to the decoherence effect that **starts to affect the resolution
> at 1.2m**. »*

Et les deux contraintes sont **incompatibles à ce pas** : atteindre $F = 0{,}73$ à 9,362 µm /
113 keV demanderait **$D = 4{,}3$ m**, très au-delà du seuil de décohérence. C'est la raison
physique — jamais écrite ainsi dans le papier, qui dit seulement *« finer voxel sizes lead to
higher image quality »* — pour laquelle le domaine est descendu à 2,4 µm : **c'est le seul coin
où l'on obtient à la fois une frange résolue et une propagation courte.**

⭐ Conséquence de cadrage, et elle est plus utile que « les pixels sont trop gros » : les 13
rouleaux n'ont pas un mauvais scan, ils ont un scan de **repérage**, optimisé pour le débit,
à distance unique pour tout le lot.

---

## 4. ⭐⭐⭐⭐ Le plan d'expérience est publié, et il lui manque exactement une case

Deux conclusions de ce dépôt disent que la mesure décisive est hors de portée :

- `HANDOFF.md` : *« **énergie** isolée contre étiquettes ❌ impossible en l'état »* ;
- `ou_la_verite_existe.py` : **zéro rouleau mesurable sur cinq**.

Les deux étaient vraies de ce qu'elles regardaient — l'ancien layout `fragments/` et cinq
rouleaux. **Elles sont fausses du corpus ESRF publié depuis** (`la_case_vide.py`, 8 contrôles).

`data/metadata.min.json` publie un champ que rien ici ne lisait : **`volume_transforms`**, des
matrices de recalage entre volumes d'un même objet. Dix objets en portent ; **six** relient le
régime de repérage (1,2 m) au régime de production (≤ 0,4 m). Et **trois de ces six sont
exactement les trois fragments dont le papier tire toute sa supervision d'encre** — `PHerc0009B`,
`PHerc0343P`, `PHerc0500P2` (Methods p. 20 : *« a dataset composed of PHerc. 9B, PHerc. 343P and
PHerc. 500P2 »*).

**Le cas qui décide**, `PHerc0500P2`, segment `20250628074500-500P2_front` — celui-là même que
l'Extended Data Fig. 5 (p. 38) montre avec sa photographie infrarouge recalée :

| représentation publiée | 2,215 µm / 0,4 m | 4,317 µm / 1,2 m | **9,362 µm / 1,2 m** |
|---|:---:|:---:|:---:|
| surface transformée dans ce repère | ✅ | ✅ | ✅ |
| pile de couches rendue | ✅ | ✅ | ✅ |
| **carte d'encre** | ✅ ×2 | — | ❌ **vide** |

Même objet, même surface, même aplatissement, une vérité terrain infrarouge, un témoin positif
publié — **et la case du régime du prix est vide**.

Ce n'est pas un cas isolé : **103 cases vides du régime du prix**, toutes avec un témoin positif
sur le même segment, réparties sur quatre objets :

| objet | cases | ce que c'est |
|---:|---:|---|
| `PHerc0139` | **38** | ⭐ le rouleau **dont le papier a lu et publié le titre** |
| `PHerc0500P2` | 38 | ⭐ fragment de supervision, vérité terrain IR |
| `PHerc0814` | 19 | |
| `PHerc0343P` | 8 | ⭐ fragment de supervision, vérité terrain IR |

⚠ Les 118 autres cases vides sont du repérage grossier à 45,5 µm / 11 m — vides pour une raison
sans intérêt, et comptées à part plutôt que fondues dans le total.

⭐⭐ **Pourquoi c'est la mesure qui décide.** Le Grand Prix demande 70 % des caractères lisibles
sur des rouleaux qui n'existent **que** dans le régime du prix. Remplir cette case répond à la
question dont tout le reste dépend — *que reste-t-il de l'encre à $F = 0{,}39$ ?* — sur un objet
dont **la réponse est connue et transcrite**. Et ça ne demande **ni faisceau, ni annotation
manuelle, ni rescan** : les couches sont déjà rendues.

---

## 5. ⚠⚠ La garantie anti-hallucination ne se transporte pas au pas du prix

C'est le pilier de la crédibilité du papier, p. 20 :

> *« We choose an input size of a 256 pixel window, which roughly corresponds to **614 µm**.
> **This input size is smaller than all letters detected** to push the model to learn the
> underlying signal […] making full-letterform hallucinations from linguistic or word-level
> priors practically impossible. »*

Ce qui produit la garantie n'est pas « 256 pixels », c'est « **moins qu'une lettre** ». Or les
deux cartes d'encre publiées du segment 500P2 portent dans leur nom de fichier `tile256-stride128`,
et à 9,362 µm une tuile de 256 pixels couvre **2 397 µm** — soit **quatre fois** la fenêtre des
auteurs, et bien plus qu'une lettre.

> ⭐ **Pour conserver la propriété au pas du prix il faut une tuile d'environ 66 pixels.**
> Qui hériterait le 256 garderait le nombre et jetterait la garantie.

⚠ À vérifier avant d'en faire un reproche à quiconque : on n'a pas relevé quelle tuile les
modèles d'encre de la communauté utilisent à 9 µm. C'est une mesure à faire, pas un fait acquis.

---

## 6. ⚠⚠ Ce que la validation du papier ne peut pas attraper

Extended Data Fig. 7 (p. 40) montre les cinq tours de pseudo-labellisation. La ligne `c` est le
segment de validation `ℓ5`, *« never used for creating labels »*, et le texte dit (p. 20) :

> *« As the iterations progress, text near the top of the validation column is **gradually
> revealed**, with performance saturating around iteration 5. »*

⚠⚠ **« Revealed » est un jugement visuel. Il n'y a aucune métrique sur la ligne `c`.** Le
protocole est : s'auto-entraîner cinq tours sur ses propres prédictions, et regarder si la
sortie ressemble davantage à du texte.

C'est très exactement le mode de panne que [`46`](46_le_temoin_negatif.md) a établi ici :
*un modèle bloqué se repère ; un modèle qui hallucine une structure **différente et
convaincante** sur chaque entrée ne se repère par aucune inspection de sa sortie.*

⚠ Et il faut être juste : le papier a une vraie défense, celle du §5 — une fenêtre plus petite
qu'une lettre. Elle interdit l'hallucination d'une **lettre entière** ; elle n'interdit pas
qu'une boucle de pseudo-labels amplifie une texture qui n'est pas de l'encre. La différence
entre les deux est exactement ce que nos instruments mesurent, et personne d'autre ne la mesure.

---

## 7. Ce que la lecture change, et ce qu'elle ne change pas

⭐ **Rouvre** :

1. la vérité terrain existe pour le régime du prix — 103 cases, quatre objets, deux fragments
   avec IR ;
2. `ou_la_verite_existe.py` doit être relancé sur le corpus ESRF, pas sur les cinq rouleaux ;
3. la ligne « énergie isolée contre étiquettes : impossible » de `HANDOFF.md` est périmée ;
4. la sortie de nos instruments a un **point de branchement d'une ligne** : `approval.tif`.

⚠ **Ne change pas** :

- le coût du régime du prix n'est pas mesuré, il est **diagnostiqué**. $F = 0{,}39$ dit que la
  frange est sous le pixel ; il ne dit pas combien de caractères survivent. C'est précisément la
  case vide qui le dirait ;
- rien ici ne dit que nos masques valent un masque humain. Aucun masque d'approbation humain
  n'a été trouvé publié ; le chercher est la première tâche ;
- le papier reste, comme le `27` le disait, le meilleur état de l'art, et sa conclusion tient :
  *« The remaining challenge is not whether sealed Herculaneum texts can be read non-invasively,
  but how broadly, robustly and efficiently the workflow can be extended. »*

---

## 8. Ce que la lecture a coûté, et pourquoi elle n'avait pas été faite

⚠⚠ Le `27` §3 fait 196 lignes sur ce papier. Ce n'est pas rien, et pourtant il manquait
l'essentiel. La raison est nommable : **il l'a lu pour se situer, pas pour refaire.** Il
cherchait ce que le papier ne fait pas — c'est un audit d'antériorité, et il l'a bien fait. Il
n'a jamais ouvert les Supplementary Tables pour les hyperparamètres, ni le commit épinglé, ni
regardé une figure.

⭐ La règle qui en sort, et elle vaut pour toute la bibliographie de ce dépôt : **un papier se
lit deux fois, avec deux questions différentes** — *qu'est-ce qui est déjà pris ?* et
*comment le referait-on ?* La seconde lecture n'est pas un luxe : les quatre résultats de ce
document en viennent tous, et aucun n'était visible depuis la première.

---

**Instruments** : [`nombre_de_fresnel.py`](../src/encre/nombre_de_fresnel.py) (13 contrôles),
[`la_case_vide.py`](../src/encre/la_case_vide.py) (8 contrôles).
**Sondes** : les deux batteries ont été cassées exprès et échouent — remplacer $\sqrt{\lambda D}$
par $\sqrt{\lambda / D}$ fait tomber 3 contrôles, oublier le rapport au pixel en fait tomber 5 ;
présumer l'encre partout où il y a des couches en fait tomber 2, poser le seuil de régime au
milieu du groupe de production en fait tomber 3.
