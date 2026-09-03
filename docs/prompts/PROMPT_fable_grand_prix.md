# Prompt — Fable 5.1 : trouver ce qui débloque le Grand Prix Vesuvius

> ⚠⚠⚠ **CE PROMPT A DEUX DÉFAUTS CONNUS, corrigés dans `PROMPT_fable_seconde_passe.md`.**
> Gardé tel quel comme trace de ce qui a réellement été demandé.
>
> 1. **Il n'énonce nulle part le cadrage de l'auteur** — *« le but est le DÉROULEMENT, pas la
>    lecture ; l'encre est la règle graduée »* (`HANDOFF.md` §0 et §1) — et il met en tête deux
>    résultats sur la **lisibilité** : le nombre de Fresnel et les 103 cases vides. Le rapport
>    qui en est sorti ([`69`](../69_reponse_dun_chercheur_exterieur.md)) consacre en conséquence
>    **4 mois sur 10** à la règle graduée et titre son mois 1 *« trancher la physique avant la
>    géométrie »*, l'inversion exacte du cadrage.
> 2. **Il ne demande pas de juger notre travail.** Il donne nos résultats comme une liste
>    d'hypothèses éliminées — des contraintes sur la recherche, pas du travail à arbitrer.
>    Mesuré sur `69` : **6 de nos 74 documents cités**, l'article **zéro fois**, et aucun de nos
>    quatre résultats de tête nommé.

> ⚠ **À lire par le modèle invité, pas par nous.** Ce fichier est versionné pour que la
> question posée soit reproductible, et pour qu'on puisse comparer deux réponses.
> Généré le 2026-08-31 depuis l'état mesuré du dépôt.

---

## 0. Ce qu'on te demande, et ce qu'on ne te demande pas

Tu es sollicité comme **chercheur senior**, pas comme exécutant. On ne te demande ni du code,
ni un plan de projet, ni de l'encouragement. On te demande de **penser**, et de rendre :

1. des **hypothèses falsifiables** sur pourquoi le problème résiste ;
2. des **formulations mathématiques** — équations, transformations, invariants, formes
   variationnelles — qui capturent quelque chose que les approches actuelles ratent ;
3. des **algorithmes**, décrits assez précisément pour être implémentés ;
4. des **mesures à faire**, chacune avec ce qu'elle discriminerait et pourquoi ;
5. des **analogies hors domaine** dont tu tires ensuite une méthode concrète — pas la
   métaphore pour elle-même.

⚠⚠ **La contrainte qui rend ta réponse utile** : chaque proposition doit atterrir sur quelque
chose de **mesurable avec les données publiques**, ou dire explicitement quelle donnée
manquante la débloquerait. Une idée qu'on ne peut ni tester ni chiffrer ne nous sert pas —
nous en avons déjà.

⚠ Et **dis quand tu ne sais pas**. Ce dépôt a payé cher, cette semaine, la différence entre
« mesuré » et « raisonné » : six de nos quatorze résultats principaux étaient déjà publiés, et
vingt-deux de nos quatre-vingt-dix-huit instruments existaient déjà. Une réponse qui distingue
ce que tu établis de ce que tu conjectures vaut infiniment plus qu'une réponse assurée.

---

## 1. Le prix, mot pour mot

Source : `data/site/scrollprize.org/prizes.html` (miroir local du site officiel, lu le
2026-08-31).

> **$800 000** au premier qui **déroule entièrement et rend lisible** un rouleau de la liste
> ci-dessous. Deuxième $100 000, troisième et quatrième $50 000. **Total $1 000 000.**
> **Échéance : 25 juin 2027.**

**Critères de soumission** (mêmes sources) :

- pipeline **entièrement reproductible**, open source, publié sur GitHub ;
- pipeline **intégré à VC3D** ;
- **100 % de la surface recto** déroulée (les écailles détachées comprises ; tolérance de 10 %
  pour des morceaux extérieurs déconnectés) ;
- détection d'encre **produite sur les images aplaties** ;
- **des colonnes de texte visibles partout** ;
- **≥ 70 % des caractères conservés de chaque colonne comptée doivent être lisibles**,
  identifiés **lettre par lettre, sans reconstruction papyrologique**.

**Les 13 rouleaux éligibles**, avec leur volume exact :

| rouleau | volume | µm | distance | keV |
|---|---|---|---|---|
| PHerc. 125 | 20250720091415 | 9,362 | 1,2 m | 113 |
| PHerc. 191 | 20250720024445 | 9,362 | 1,2 m | 113 |
| PHerc. 211 | 20250720140115 | 9,362 | 1,2 m | 113 |
| PHerc. 257 | 20250720113058 | 9,362 | 1,2 m | 113 |
| PHerc. 268 | 20250511054932 | 8,640 | 1,2 m | 116 |
| PHerc. 358 | 20250719150703 | 9,362 | 1,2 m | 113 |
| PHerc. 800 | 20250510225703 | 8,640 | 1,2 m | 116 |
| PHerc. 813 | 20250720160015 | 9,362 | 1,2 m | 113 |
| PHerc. 826 | 20250720174915 | 9,362 | 1,2 m | 113 |
| PHerc. 1203 | 20250720004030 | 9,362 | 1,2 m | 113 |
| PHerc. 1218 | 20250510170249 | 8,640 | 1,2 m | 116 |
| PHerc. 1447 | 20250509011039 | 8,640 | 1,2 m | 116 |
| PHerc. 1545 | 20250720045926 | 9,362 | 1,2 m | 113 |

⭐⭐⭐ **Regarde la dernière colonne.** Les treize sont dans **le même régime de scan** —
8,6 à 9,4 µm, 1,2 m de propagation, 113 à 116 keV. Et le site du prix **classe lui-même ce
régime comme inférieur** : *« We scanned many samples with a lower resolution configuration
which seemed to be "optimal" (but not as good as the first): around 9 µm isotropic voxels,
1.2 m propagation distance, and about 110 keV average incident energy »*
(`data/site/scrollprize.org/2026_open_problems.html`).

**Le prix est donc défini sur les données les plus dures du corpus.** C'est un fait de
cadrage, pas un détail.

---

## 2. Où en est le monde — mesuré, pas estimé

Relevé depuis `metadata.min.json`, l'index que le dépôt public publie lui-même (45
échantillons, 67 scans). Instrument : `src/encre/corpus_par_energie.py`.

| sur les **13 rouleaux du prix** | |
|---|---:|
| segments publiés, **tous auteurs confondus** | **21** |
| cartes de détection d'encre publiées | **0** |
| rouleaux sans **aucun** segment publié | **11 sur 13** |

Deux rouleaux portent tous les segments : `PHerc1447` (15) et `PHerc0800` (6).

⚠⚠ **Personne n'est proche.** Le critère demande **100 % du recto** d'un rouleau ; le total
mondial publié sur ces treize est de vingt et un segments et zéro encre. L'étage qui bloque
n'est donc pas le raffinement de la détection d'encre — c'est que **la segmentation de ces
rouleaux-là n'a pratiquement pas commencé**.

Pour comparaison, sur les rouleaux **hors prix** : `PHercParis4` (Scroll 1) publie 81 segments
et 80 cartes d'encre, `PHerc0172` 53 et 53. Ces deux-là ont des scans à 53–54 keV.

---

## 2 bis. ⭐⭐⭐ Deux résultats du 2026-09-02, tirés d'une relecture intégrale du papier de référence

Le papier `data/site/scrollprize.org/pdf/main.pdf` (Angelotti *et al.*, arXiv 2606.29085,
46 p.) avait été lu ici pour **auditer sa nouveauté**. Relu pour **refaire sa méthode**, il a
rendu deux choses que la première lecture ne pouvait pas voir. Détail complet : `docs/68`.

### A. Les « trois paramètres couplés » n'en font qu'**un**, et il se calcule sans rien télécharger

Le contraste ne vient pas de l'absorption (*« very low for carbon-based material in hard
X-rays »*, p. 14) : il vient des franges de Fresnel. Ce qui décide de leur visibilité est la
largeur de frange **rapportée au pas d'échantillonnage** :

$$ F = \frac{\sqrt{\lambda D}}{p}, \qquad \lambda = \frac{hc}{E} $$

Mesuré sur les **59 scans publiés** (`src/encre/nombre_de_fresnel.py`, 13 contrôles), $F$
**ordonne les verdicts que les auteurs écrivent sous leurs propres panneaux** :

| $F$ | ce que c'est | ce que le papier en dit |
|---:|---|---|
| **0,39–0,42** | **les 13 rouleaux du prix** | *« pixel-limited […] the bare voxel grid »* |
| **0,73–0,75** | le régime de **production** (2,4 µm / 0,2 m) | *« the best possible resolution on a setup compatible with large scrolls »* |
| **1,82** | 1,129 µm / 0,2 m | *« too long propagation distance for a so small pixel size »* — c'est la **définition** de $F > 1$, écrite en mots |

**Les 13 rouleaux du prix sont à 53 % du régime de production.** Et ils sont du mauvais côté
d'un **second** critère, indépendant : $D = 1{,}2$ m est la distance à laquelle le papier
mesure l'apparition de la **décohérence** — sur `PHerc0268`, qui est **l'un des treize**
(Ext. Data Fig. 2c). Les deux contraintes sont **incompatibles à ce pas** : atteindre le $F$ de
production à 9,362 µm demanderait $D = 4{,}3$ m.

⚠ Ce que $F$ **n'explique pas** : la décohérence elle-même, qui dépend de $D$ en absolu. Deux
scans à $F$ voisin (0,85 et 0,95) ont des verdicts opposés, et la seule chose qui change est
$D$. Le modèle a deux termes, et le fichier contrôle les deux.

⭐ Ce que ça t'offre : une grandeur **prédictive et réfutable** pour juger n'importe quel scan
existant ou futur, sans en ouvrir un seul.

### B. Le plan d'expérience du régime du prix est **publié**, et il lui manque exactement une case

`data/metadata.min.json` porte un champ que rien ne lisait ici : **`volume_transforms`**, des
matrices de recalage entre volumes d'un même objet. **Six objets** relient le régime du prix
(1,2 m) au régime de production (≤ 0,4 m) — dont **les trois fragments dont le papier tire
toute sa supervision d'encre** (`9B`, `343P`, `500P2`), qui portent une **vérité terrain
infrarouge**.

Sur `PHerc0500P2`, segment `20250628074500-500P2_front` — celui que l'Ext. Data Fig. 5 montre
avec sa photographie IR recalée :

| | 2,215 µm / 0,4 m | 4,317 µm / 1,2 m | **9,362 µm / 1,2 m** |
|---|:---:|:---:|:---:|
| surface transformée | ✅ | ✅ | ✅ |
| pile de couches rendue | ✅ | ✅ | ✅ |
| **carte d'encre** | ✅ ×2 | — | ❌ **vide** |

**103 cases vides du régime du prix**, toutes avec un témoin positif sur le même segment :
`PHerc0139` **38** (⭐ le rouleau **dont le titre est transcrit et publié**), `PHerc0500P2` 38,
`PHerc0814` 19, `PHerc0343P` 8. Relevé : `src/encre/la_case_vide.py`, 8 contrôles.

⭐⭐ **C'est la mesure qui décide de la stratégie du prix** — *que reste-t-il de l'encre à
$F = 0{,}39$ ?* — sur des objets dont la réponse est connue. Elle ne demande **ni faisceau, ni
annotation manuelle, ni rescan** : les couches sont déjà rendues.

⚠⚠ **Et un piège à ne pas hériter.** La défense anti-hallucination du papier n'est pas
« 256 pixels », c'est *« smaller than all letters detected »* — 256 px valent **614 µm** à
2,4 µm. À 9,362 µm la même tuile couvre **2 397 µm**, soit bien plus qu'une lettre : **la
garantie ne se transporte pas.** Pour la conserver il faut une tuile d'environ **66 px**.

### C. Le geste qui coûte 775 heures est un **pinceau**, et son interface est un fichier

Le papier chiffre son coût : *« ~25 hours per wrap of manual annotation »* × 31 spires. Le
commit épinglé qu'il publie (`ScrollPrize/villa@e583fb6`, récupéré ici) montre à quoi elles se
dépensent : `ApprovalMaskBrushTool.cpp` — un **pinceau** avec lequel un humain peint
région par région *« regions judged geometrically consistent with a single sheet »*.

Et `QuadSurface::channel()` charge **tout `.tif` du dossier du segment** dont le nom n'est ni
`x`, ni `y`, ni `z`. Le masque est lu sous le nom `"approval"` et gouverne la ré-optimisation
du maillage.

> **Écrire `approval.tif` à côté de `x.tif`/`y.tif`/`z.tif` EST l'intégration entière.** Pas
> d'API, pas de fork. Un fichier.

⭐ C'est le point de branchement de tout ce que ce dépôt sait faire — mesurer la qualité d'une
surface **sans vérité terrain**, ce que le pinceau demande à un humain de juger à l'œil.

---

## 3. Ce qui est ÉLIMINÉ — ne le repropose pas sans argument neuf

Chacun de ces points est **mesuré** dans ce dépôt, avec son relevé JSON et son instrument.

| hypothèse | verdict | où |
|---|---|---|
| « c'est une question de **résolution** » | **éliminée deux fois**, par deux voies indépendantes. Ramener un fragment au pas d'entraînement du modèle **dégrade** l'AUC : 0,746 → 0,693 → 0,686 | `docs/58`, `docs/63` |
| « σ élevé ⇒ le modèle lit » | **non validé** : σ arrive quatrième sur six grandeurs, p de Holm 0,739 | `docs/65` §1 |
| « l'**énergie** explique l'échec » | **contredit** par une ablation contrôlée publiée : à ~8 µm, l'optimum empirique annoncé est **100–120 keV**, donc les 116 keV sont *dedans*. ⚠ **Mais l'énergie seule était la mauvaise question** — voir §2 bis, les trois paramètres n'en font qu'un | `docs/66` §3, `docs/68` §3 |
| « la **campagne de scan** sépare les rouleaux lisibles » | **rétrogradé** : restreint aux rouleaux réellement tentés, p passe de 0,0081 à **0,50** | `docs/59` |
| ~~« on peut mesurer si le modèle lit **sur un rouleau** »~~ | ⭐⭐⭐ **RÉOUVERT le 2026-09-02.** L'ancienne réponse valait des **cinq** rouleaux interrogés, pas du corpus. Voir §2 bis : `PHerc0139` porte les deux régimes **recalés**, et son titre est transcrit et publié | `docs/68` §4, `src/encre/la_case_vide.py` |
| « papyrus vierge » | fermé | `docs/46` §3 |

⚠ Et une limite de méthode qui vaut pour toi aussi : **un écart relatif large sur un paramètre
ne prouve pas qu'il est le facteur limitant.** Il faut la **sensibilité**, pas la distance.
Nous avons commis exactement cette faute sur l'énergie.

---

## 4. Ce qui est DÉJÀ PUBLIÉ par d'autres — ne le redécouvre pas

Deux audits adversariaux du 2026-08-29 (`docs/66`, `docs/67`), sur le miroir du site et
**35 dépôts clonés localement** (13 Go, tous lisibles depuis `data/repos/`).

**Sur nos résultats** : 14 examinés, **6 déjà publiés, 8 à moitié, 0 nouveau.**
**Sur nos outils** : 98 examinés, **22 existaient déjà, 50 partiellement, 27 sans équivalent.**

⚠⚠ **Le mode de défaillance était le vocabulaire**, et il te concerne directement : aucun
équivalent ne porte le même nom. « écart entre spires » = *winding pitch* ; « planéité » =
*linearity* ; « champ de correction » = *subvoxel re-centering* ; « distance à la matière » =
*CT support* ; « saut de spire » = *sheet consistency* / *winding jump fraction*.
**Cherche le concept, jamais le nom.**

**Ce qui n'a AUCUN équivalent dans les 35 dépôts**, et qui situe donc l'espace libre :

- **la statistique** — zéro `binomtest`, zéro test de permutation, zéro analyse de puissance,
  zéro intervalle de confiance sur un score d'encre, dans *tout* le corpus, `ink-id`, `villa`
  et le modèle du Grand Prize compris. `winding-ruler` publie des « +3–5 pp » sans importer
  `scipy.stats` ;
- **un juge automatique en aveugle** — aucun appel à une API de modèle, et le protocole de
  jugement publié n'a **pas de condition de contrôle** (jamais d'image vierge présentée) ;
- **le test de convergence** (comparer une mesure à elle-même sous un changement de paramètre
  de rendu, au lieu de la comparer à un seuil) ;
- **l'étage polaire** — zéro dépliage polaire d'une coupe CT, zéro suivi de crêtes, zéro
  modèle nul spatial.

---

## 5. Les instruments dont tu disposes

### 5.1 Un point d'entrée unique

```bash
./lplv --help              # 277 verbes découverts dans l'arbre, chacun avec sa première ligne de docstring
./lplv <verbe> --help      # SON aide, produite par le module lui-même
./src/outils/temoins.sh    # 163 batteries, 4275 contrôles, hors ligne
```

⭐ Chaque script porte une **docstring qui dit pourquoi il existe**, souvent avec le défaut
qu'il a coûté. Lis-les : elles sont la vraie documentation.

### 5.2 Les familles

| famille | ce qu'elle mesure |
|---|---|
| `commun/`, `tracecheck/` | le **test de convergence** : α = log(croissance)/log(élargissement). α ≈ 1 ⇒ aucune feuille à portée ; α ≈ 0 ⇒ une vraie feuille. Aucun seuil, aucune vérité terrain, aucune échelle |
| `nappe/` | géométrie d'une surface tracée : auto-intersections, écart de maillages, espacement des spires, saut de spire par la **phase**, champ de correction, distance à la matière, orientation des fibres |
| `graine/` | où poser une graine : planéité par tenseur de structure, critère **relatif**, éligibilité en aval |
| `encre/` | typographie (interligne par autocorrélation), témoin négatif, dispersion par tuiles, transport de calibration, juge par API, corpus par énergie |
| `volume/` | lecture distante d'un volume de surface (**1,78 Mo et ~1 s par fenêtre** au lieu de 32 Go), profil de profondeur, évaluation contre étiquettes |
| `excision/` | retirer une région et mesurer ce que ça change |
| `depot/` | l'hygiène : recalcul de **333 chiffres publiés** contre leur JSON, détection des batteries incapables d'échouer, des idées déjà écrites ailleurs |

### 5.3 ⭐⭐⭐ La capacité neuve : on peut **marcher dans le rouleau**

Livré le 2026-08-31. Un **raymarcher volumique** rend un vrai rouleau à l'échelle du micron et
on s'y déplace. Ce n'est pas une visualisation : c'est un **instrument d'inspection**.

- `lpl::voxel` (LplPlugin) — rendu volumique direct, mosaïque multi-niveaux, résidence par
  anneaux, saut d'espace vide, **ombrage par gradient**, opacité de frontière
- `lpl::zarr` (LplPlugin) — le format chunké, générique
- `lpl::scroll`, `lpl-scrollwalk`, `lpl-scrollfly` (LplVesuvius) — pose entrée, image sortie
- **162 contrôles verts**. `PHerc0172` niveau 0 : 135 bricks, 33 M échantillons en 9,6 s

⚠⚠ **Et une décision de conception qui est un fait sur les données** : il n'y aura **pas de
mailleur d'isosurface**. Mesuré sur un vrai chunk niveau 0 — les feuilles sont des rubans
clairs de **3 à 5 voxels** (24–40 µm) espacés de **30 à 40 voxels** (240–320 µm), *dans un
milieu qui n'est pas vide* : le creux entre deux feuilles vaut **115 à 130**, pas zéro.
Balayage de seuil de 130 à 198 : **aucun seuil ne sépare les feuilles sans en détruire la
moitié**. Une isosurface affirmerait une frontière que le scan n'a jamais résolue.

⚠ Autre fait du même rendu, qui pourrait t'inspirer : **sans ombrage par gradient, rien n'est
visible** — l'émission-absorption pure sur un champ dont la densité varie de quelques pour cent
donne une brume uniforme. Le **gradient du champ est la normale** de la surface qui passe par
l'échantillon. Toute l'information de feuille est dans la **dérivée**, pas dans la valeur.

Les rendus sont dans `data/rendu/` (14 images) : coupe du rouleau, marche entre les feuilles,
minimap position, prédiction de surface superposée, normales en RGB.

---

## 6. Les données, et ce qu'on peut vraiment en faire

- **`metadata.min.json`** à la racine du bucket public : 45 échantillons, 67 scans, chacun avec
  `energy_keV`, `pixel_size_um`, et la liste de ce qui existe par segment. **Une requête.**
- Les volumes sont en **OME-Zarr v2**, anonymes, lisibles par plage d'octets. Un chunk
  `[109,128,128]` contient **toute la colonne de profondeur** d'une fenêtre 128×128 — c'est ce
  qui rend une campagne de corpus possible du tout.
- **35 dépôts clonés** dans `data/repos/` (13 Go), dont `villa` (le monorepo officiel, avec
  Volume Cartographer, VC3D, ink-detection et lasagna) et 34 outils communautaires.
- **Le miroir du site** dans `data/site/scrollprize.org/` (35 pages + `pdf/main.pdf`, le papier
  de référence Angelotti et al. avec ses ablations contrôlées en Extended Data).
- **Les étiquettes d'encre du Grand Prize 2023** : 46 fichiers dans
  `data/repos/Vesuvius-Grandprize-Winner/all_labels/` — ce sont des segments de Scroll 1, donc
  le jeu d'entraînement du modèle publié.

⚠ Ce qui **n'existe pas** : aucune vérité terrain d'encre sur un rouleau que le modèle n'ait
pas vu. C'est la contrainte structurelle du domaine, et le site du prix l'énonce comme problème
ouvert : *« reliably tell "no ink" apart from "no ink recovered yet" »*.

---

## 7. Les contraintes dures — ce qui ne se contourne pas

1. **L'encre est du carbone sur du carbone.** Le contraste d'atténuation est quasi nul ; ce
   qu'on lit est du **contraste de phase**, donc une propriété de la **frontière**, pas du
   matériau.
2. **Les trois paramètres de scan sont couplés** (le site le dit ainsi) : taille de voxel,
   distance de propagation, énergie. Monter l'énergie réduit la décohérence *et* le contraste.
   On ne peut pas en bouger un seul.
3. **Les scans sont acquis, pas commandables.** Les 13 rouleaux du prix ont le scan qu'ils ont.
4. **Le critère est lettre par lettre**, sans reconstruction papyrologique. Un résultat qui
   « ressemble à du grec » ne compte pas.
5. **Le pipeline doit s'intégrer à VC3D.** Une méthode qui ne s'y branche pas ne peut pas
   gagner, quelle qu'elle soit.

---

## 8. ⭐⭐ Ce qu'on attend vraiment de toi : élargis le champ

Le patron de résolution qu'on croit juste : **les problèmes impossibles se débloquent en
trouvant des motifs**, et les motifs viennent souvent d'ailleurs. Quelques directions, dont
aucune n'est prescriptive — trouve-en de meilleures :

- **La feuille est un ruban dans un milieu continu.** Quels domaines savent suivre une surface
  fine, contrastée à quelques pour cent, dans un volume bruité ? *Sismique de réflexion*
  (suivi d'horizons, attributs de cohérence, *dip steering*), *imagerie médicale*
  (segmentation de fascias, de rétine par OCT — où les couches sont exactement ce problème),
  *microscopie électronique* (suivi de membranes), *météorologie* (suivi de fronts).
- **Le rouleau est une spirale à pas quasi constant.** Cela ressemble à : *diffraction* (une
  spirale régulière a une signature dans l'espace de Fourier), *cristallographie* (l'espacement
  périodique donne des pics de Bragg — un rouleau est un cristal 1D déformé), *ADN et
  chromatine* (enroulement, appariement, *contact maps* de Hi-C), *tomographie de bobines
  industrielles*.
- **Le problème est un appariement global sous contrainte topologique.** Cela ressemble à :
  *coupe minimale / flot maximal*, *appariement de graphes*, *reconstruction de puzzle*,
  *alignement de séquences* (un rouleau déroulé est une séquence, ses tours sont des
  répétitions), *théorie des nœuds*.
- **La détection d'encre est un problème de signal faible dans un fond structuré.** Cela
  ressemble à : *astronomie* (détection de sources sous le bruit de fond, statistiques de
  comptage), *physique des particules* (le look-elsewhere effect, les corrections de
  multiplicité — que ce domaine n'applique pas), *stéganalyse*.
- **Le geste global qui manque peut-être** : personne ne semble exploiter que **les treize
  rouleaux sont le même objet physique treize fois**. Y a-t-il un a priori partagé, un modèle
  génératif de l'enroulement, un apprentissage inter-rouleaux ?

⚠⚠ Pour chaque analogie que tu retiens : **va lire les articles réels du domaine emprunté**,
cite-les, et dis **quelle équation ou quel algorithme précis** se transporte. Une métaphore
sans transport est une jolie phrase.

---

## 9. Le format de ce qu'on veut recevoir

Structure-le ainsi, et n'hésite pas à être long :

1. **Ton diagnostic** — où est le vrai goulot, et pourquoi tu le crois. Distingue ce que tu
   déduis des faits ci-dessus de ce que tu conjectures.
2. **Trois à sept hypothèses**, chacune avec : l'énoncé falsifiable, la mesure qui la
   trancherait, ce qu'elle prédirait si vraie, ce qu'elle prédirait si fausse, et le coût.
3. **Les mathématiques** — équations, invariants, formes variationnelles, avec leur
   dérivation ou leur source.
4. **Les algorithmes** — assez précis pour être implémentés, avec leur complexité et ce qui
   les fait échouer.
5. **Les emprunts hors domaine** — avec les références réelles, et le transport explicite.
6. **Ce que tu ferais en premier** si tu avais nos instruments et dix mois.
7. ⚠ **Ce dont tu doutes** — les points où tu penses avoir tort, et ce qui te ferait changer
   d'avis.

⚠⚠ **Source tout.** Nous devons pouvoir aller vérifier chacune de tes affirmations, et nous
inspirer de tes sources. Un chiffre sans source, dans ce dépôt, n'est pas un résultat : c'est
une anecdote.

---

## 10. Les sources de ce prompt

Tout ce qui précède est vérifiable dans le dépôt :

| affirmation | où |
|---|---|
| les critères du prix, les 13 rouleaux | `data/site/scrollprize.org/prizes.html` |
| le régime de scan jugé inférieur | `data/site/scrollprize.org/2026_open_problems.html` |
| l'ablation énergie × distance | `data/site/scrollprize.org/pdf/main.pdf`, Extended Data Fig. 2 |
| 21 segments et 0 encre sur les 13 | `docs/mesures/corpus_par_energie.json`, `src/encre/corpus_par_energie.py` |
| résolution éliminée deux fois | `docs/58`, `docs/63`, `docs/mesures/frag1_echelles.json` |
| σ ne prédit pas la qualité | `docs/65`, `docs/mesures/transport_de_calibration.json` |
| aucun rouleau mesurable | `docs/mesures/ou_la_verite_existe.json` |
| l'audit d'antériorité des résultats | `docs/66`, `docs/mesures/audit_anteriorite.json` |
| l'audit d'antériorité des outils | `docs/67`, `docs/mesures/audit_outils.json` |
| le marcheur volumique et ses mesures | `~/LplKnowledge/store/LplKernel/PLAN_papyrus_marchable.md` |
| le nombre de Fresnel des 59 scans | `docs/68` §3, `src/encre/nombre_de_fresnel.py`, `docs/mesures/nombre_de_fresnel.json` |
| les 103 cases vides du régime du prix | `docs/68` §4, `src/encre/la_case_vide.py`, `docs/mesures/la_case_vide.json` |
| le pinceau d'approbation et son format | `data/repos/villa` au commit `e583fb6` (`volume-cartographer/apps/VC3D/segmentation/tools/ApprovalMaskBrushTool.cpp`, `core/src/QuadSurface.cpp:1861`, `core/src/GrowPatch.cpp:133`) |
| la méthode du papier, étape par étape | `docs/68` §2 (17 étapes, 4 humaines) |
| l'état de l'art du domaine | `docs/00_etat_de_lart.md` |
| l'article en cours | `docs/article/article.typ` (25 p., 17 références) |
