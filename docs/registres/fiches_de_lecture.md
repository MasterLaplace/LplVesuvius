# Fiches de lecture des 70 documents — 2026-09-03

> Produit par dix agents, un lot chacun, consigne : lire chaque fichier INTÉGRALEMENT et
> rendre par document sa nature, son résumé, ses conclusions falsifiables avec leurs
> chiffres, ses rétractations internes, et **deux citations verbatim numérotées** — une
> après 60 % du fichier, une dans les 15 dernières lignes.
>
> ⚠⚠ Les citations sont la garde : sans elles, « j'ai tout lu » est une promesse. Les **140
> citations** ont été cherchées dans les fichiers cités et **140 ont été retrouvées à leur
> ligne** (`verifier_citations.py`, fenêtre de ±4 lignes pour tolérer un décalage d'index sans
> tolérer une citation absente).
>
> ⚠⚠⚠ **Ce compte a d'abord été publié à 88, et c'était faux.** Le motif de la garde ne
> connaissait qu'une écriture (« ligne 104 ») ; les fiches en portent deux autres
> (« l. 271 », « lignes 89–90 »), et **44 citations sur 132 n'étaient donc jamais
> vérifiées** — un tiers. La garde ne mentait pas sur ses 88, son **dénominateur** était le
> sous-ensemble qu'elle savait lire. C'est le péché capital de ce dépôt dans un costume neuf.
> Corrigé le 2026-09-03 : les trois écritures sont reconnues, et surtout la garde **compte les
> lignes de preuve qu'elle n'a pas su lire et échoue dessus**, donc une quatrième écriture
> fera échouer au lieu de disparaître.
>
> ⚠ Elle signale aussi la **dérive** : une citation retrouvée ailleurs que sa ligne annoncée
> veut dire que le document a été édité depuis la fiche. C'est arrivé le jour même — le `07`
> a reçu 28 lignes en tête, ses deux citations ont dérivé de +28, et **la garde d'alors ne
> l'a pas vu** puisqu'elle ne lisait pas ce format.
>
> ⚠ `docs/69` est hors périmètre sur consigne de l'auteur et n'a pas été lu.

**70 fiches · 23 389 lignes lues · 1328 conclusions extraites.**



Lu le 2026-09-03. Chaque fichier a été lu du premier au dernier caractère ;
`wc -l` relevé avant lecture, citations vérifiées par numéro de ligne.

---

### docs/00_carnet_de_bord.md
- **lignes** : 464
- **nature** : MIXTE
- **résumé** : README/carnet de bord du dépôt. Il tient d'un côté l'appareil de PROCÉDÉ (arborescence, environnement, table de tous les documents `00` à `67`, commandes de rejeu, état de la récupération de données) et de l'autre une très longue table « ce qui marche / ce qui ne marche pas encore » datée du 2026-08-20 qui agrège des résultats mesurés ailleurs, avec leurs chiffres. Une grande partie de cette table est constituée d'annulations et de re-lectures de résultats antérieurs du même dépôt — c'est le document où les rétractations sont recensées.
- **conclusions extractibles** :
  - La chaîne `trace → auto-intersection → aplatissement → rendu` tourne de bout en bout sur un rouleau du Grand Prize jamais touché (`24`) et sur un segment officiel d'un autre (`36`).
  - « nos propres traces ne suivent aucune feuille » : en élargissant la fenêtre de rendu, la distance à la matière la plus proche reste identique sur une bonne surface (α = +0,00) et suit la fenêtre sur les nôtres (α = +1,01) ; à quatre spires de portée le pic n'a rien trouvé.
  - Dix-sept essais pour poser une surface sur une feuille en partant d'une graine, tous à α ≈ 1.
  - Ce qui décide où la surface se pose est la **portée physique** du test de sortie du rayon (`exit_count × pas`), à tenir entre **0,25 et 0,5 voxel** ; le pas peut être affiné librement si `exit_count` suit.
  - À pas égal, changer la seule portée fait passer l'α de **+0,327 à +0,130** ; deux campagnes de pas différant d'un facteur deux mais partageant la portée 0,25 donnent +0,102 et +0,130.
  - Chaîne de spires : 9 tours, **6 convergent** au pas de rayon 0,25. Sur la figure des sept bandes, **4 sur 7 convergent**, la 7ᵉ casse (α = +1,475).
  - Écart entre nappes de la chaîne : **113 µm** — elle avance d'une feuille à la fois. Chaque fenêtre couvre **10 % d'un tour** ; il en faudrait au moins huit côte à côte pour fermer un tour.
  - Toute la chaîne radiale perd **15,6 % d'aire utile par tour**.
  - Extension d'une nappe le long d'elle-même : aire utile **4,28 → 12,97 cm²**, sommets valides **59 → 96 %**, arc **21,9 → 37,2 mm**, à **α = +0,000**.
  - `VC_GROWPATCH_RNG_SEED` + `thread_limit: 1` rendent le traçage par croissance reproductible : deux exécutions donnent des maillages identiques **octet pour octet**. `mode: resume` n'était pas déterministe (générateur `thread_local` semé par `std::random_device`, 22 threads OpenMP).
  - « consistent with » quantifié : épaisseur de trait **AUC 0,857**, netteté du pic **0,753** suivent le contraste d'encre publié ; la séparation des lignes **va contre** (0,319).
  - Témoin négatif : sur une trace à α ≈ 1, le détecteur répond **plus fort** que sur une vraie feuille (σ **0,7111** contre **0,5894**) tout en rendant deux cartes étrangères (ρ = **−0,0100**).
  - Second témoin négatif : graine tirée par l'outil, **α = +0,99**, **13,89 cm²** ; groupé au premier il rend **1 fenêtre périodique sur 7** contre **8 sur 12** pour `PHerc1447` — Fisher `[8, 4, 1, 6]`, **p = 0,0399**. Une seule fenêtre suffirait à le renverser (0,1299 ou 0,0799 selon le sens).
  - **13 traces sur 16** butent sur le plafond du rendu, qui double avec la profondeur — donc un seuil absolu compare des réglages et non des surfaces.
  - α ≈ 1 a deux causes (un pic qui recule, aucun pic du tout) ; l'audit des **217 profils** donne **20 séries sur 107**, **0 verdict positif touché**.
  - Rouleaux traçables et rouleaux lisibles sont **disjoints** (13 contre 3) ; l'expérience « réparer sert-il ? » doit donc être montée sur `PHercParis4`.
  - Un rendu était limité par une ressource non mesurée : **28,2 Go de RSS sur 32**, **3,4 Go en swap**, **23,7 % d'un cœur sur 22** ; le cache de chunks vaut 16 Go par défaut et aucun des **28 appels** du dépôt ne le réglait.
  - Le plafond de générations ne fabriquait pas le résultat négatif : à budget **×3,3** l'aire est **×11,5** mais α passe de **+0,89 à +0,95**, sous le bruit du tireur (0,16). Un seul tirage par budget.
  - Un relief se lit sur une moyenne de patch, donc il dépend de la fenêtre : la trace lue à **1024 px** paraissait plate et ne l'est pas.
  - Un morceau de segment publié, passé par notre chaîne de rendu, revient au-dessus de la médiane de son propre corpus (le rendu n'écrase pas le relief).
  - Le vide d'un rendu suit la **graine**, pas la prédiction ; `m7` et `ps256` sont au même endroit. `vide` vaut `pic == 0` lu dans les TIFF.
  - **39 batteries sur 105** ne pouvaient pas échouer : le verdict imprimait « ALL PASS » et rendait 0 inconditionnellement ; aucune ne cachait d'échec réel.
  - Le rendu « lent » a varié d'un facteur **43 sur lui-même** (0,267 / 1,200 / 11,429 fen/s) et atteint le même pic que le rapide (**11,4 contre 12,3**) ; l'A/B donne **×1,47** au lieu de ×4,6 ; la réfutation de cache tient (le rassemblement est **×2142** trop petit).
  - Première vérité terrain du dépôt : contre les `inklabels` de `Frag1`, la chaîne rend **AUC 0,746** (mélange à **0,500**, gain de précision **×1,7**) ; ramener le fragment au pas d'entraînement **dégrade** l'AUC (0,746 → 0,693 → 0,686).
  - La réplication ne confirme pas : trois fragments donnent **0,746 / 0,600 / 0,575** sur « tout le segment » et **0,677 / 0,581 / 0,704** sur les tuiles annotées ; la chaîne rend **entre 0,52 et 0,75** selon fragment ET domaine, étendue **0,12** sur le domaine le plus resserré.
  - De tuile à tuile **dans** un fragment l'AUC varie d'un écart-type de **0,2243**, contre **0,0391 entre** fragments — soit **5,7×** ; le fragment d'origine explique **3 %** de l'écart ; il aurait fallu **27 tuiles par fragment** là où on en avait 10, 11 et 2.
  - La formule usuelle d'erreur-type est **109× trop étroite** sur une carte d'encre (pixels non indépendants) ; appliquée telle quelle elle déclarerait significatifs deux tirages du même fragment.
  - σ arrive **quatrième sur six** grandeurs (p de Holm **0,739**) ; l'intervalle à 9,72 µm, **[0,455 ; 0,745]**, contient 0,5. Au natif la lisibilité est établie.
  - Sur cinq rouleaux interrogés, quatre ne publient **aucune** étiquette d'encre et `Scroll1` n'en a que dans son jeu d'entraînement ; seuls **4 fragments** sont mesurables.
  - `load_layer_stack` normalisait par **65535** alors que **211 des 214 piles** de l'arbre sont uint8 — elles arrivaient au modèle **257 fois trop sombres**. `PHerc1447` passe de σ **0,0171** à **0,6558**, soit **1,2×** le témoin.
  - La résolution n'explique pas l'inertie du modèle d'encre : le témoin à AUC 0,925 est à **9 %** des conditions de `PHerc1447` sur les deux axes (**506,2 contre 553,0 µm** par tuile, **205,7 contre 224,6 µm** de profondeur) et dix fois cet écart ne rend qu'un facteur **2,1** sur les **45** à expliquer.
  - Sur 45 rouleaux, **31 n'ont aucun segment publié** ; ranger ceux-là avec « pas d'encre » fait rendre **p = 0,0081** à un partage qui, restreint aux rouleaux tentés, rend **p = 0,50**.
  - Aucun des **treize** rouleaux du prix ne publie de détection d'encre ; **dix des treize** n'ont aucun segment publié, trois ont été tracés sans rendre d'encre.
  - `vc_grow_seg_from_seed` est un moindres carrés à **douze familles de résidus** ; dans les runs de base **trois des quatre** termes qui regardent les données sont inactifs (`SURFACE_SDT` poids nul par défaut, `NORMAL`/`SNAP` exigent une grille de normales, `DIRECTION` des champs de direction) ; aucun des 17 essais ne règle `sdt_weight`.
  - La cible assemblée : **44 spires consécutives** de PHerc0172, sans un trou — le déroulage étant celui de l'équipe du concours, le dépôt n'ajoutant que l'ordre.
  - PHerc. 1667 (arXiv 2606.29085, juin 2026) : **31 spires, 1231 cm², 22 colonnes** ; **~25 heures d'annotation manuelle par spire**, soit **~775 h** pour ce rouleau, quand le Grand Prize 2027 en tolère **huit**.
  - Ordres de grandeur des données : région *grand-prize-banner* **77 Go** en Zarr et **390 Go** en pile TIFF ; jeu `spiral-input` de Paris4 **49,6 Go**.
  - Un chunk Zarr = une colonne de profondeur entière, pour **1,78 Mo et 1,03 s**.
  - État de la récupération (2026-08-19) : miroir **81/81 pages** (228 Mo), **35 dépôts** clonés (13 Go), **80/80** cartes d'encre de Scroll 1, **81** volumes de surface Scroll 1 et **46** Scroll 4, campagnes 45,5 / 2,4 / 1,13 µm ; total sur disque **103G** hors `.git`, dont **79 Go** pour `data/` seul ; **797 Go libres**. `lukeboi/scroll-viewer` renvoie 404.
  - `temoins.sh` : **163 batteries, 4275 contrôles** hors ligne, tous verts ; `verifier_chiffres.py` recalcule **333 chiffres depuis 66 fichiers de résultat**.
  - Deux spires voisines sont à 300 µm, une feuille fait 40 µm.
- **rétractations / corrections internes** :
  - Table d'état, ligne encre : « ~~le modèle de 2023 sort une **constante** à 8,6 µm~~ — **annulé**, ce σ mesurait notre échelle et non le rouleau (`60`) » ; M1ter est **ROUVERT**, `46` est **REFAIT** (« sa conclusion a changé de signe ») et `54` **RELU** (il tient).
  - Même ligne : le ρ du témoin négatif vaut **−0,0100 et non +0,9979** — « c'était la signature du bug d'échelle ».
  - Ligne `62` §7 : « il n'y avait pas d'écart : un débit publié depuis un CUMUL » ; l'auteur avait lu « 1586 % de CPU sur 2200 » comme « pas de contention ». Un débit ne se publie pas depuis un cumul.
  - Ligne `61` : trente-neuf batteries sur cent cinq ne pouvaient pas échouer ; les batteries en **shell** restent à instruire.
  - Ligne `58` : « le chiffre qui portait la question était faux — `36` §5bis disait 2,4 µm là où le volume déclare **7,91** ».
  - Ligne `44` : l'érosion de l'aire **utile** vaut **15,6 % par tour** « et non 4,0 %, qui portait sur la grille » ; et l'hypothèse « la rupture est une érosion » est **réfutée** — le meilleur prédicteur est le simple numéro de la spire.
  - Ligne `43` : la rupture tombe au tour 07 (α = +0,702 puis +1,321) « au lieu du tour 06 ».
  - §« Ce que le concours a résolu » : « ⚠ **Et "l'encre est résolue" est faux**, contrairement à ce que ce paragraphe disait avant le 2026-08-19 ».
  - §Arborescence : « ⚠ Ce bloc décrit l'état APRÈS le repli du 2026-08-26 (trois dossiers). Il en annonçait quatre auparavant, dont un `tools/` qui n'existe plus. »
  - §État de la récupération : « ⚠⚠ Mesuré le 2026-08-19 : 103G, contre "~76 Go" annoncé ici » — le plafond de 100 Go que le dépôt s'était donné est franchi.
  - §Rejouer : les compteurs de `temoins.sh` sont écrits par le script ; « la version precedente disait 18 et 741, recopies a la main et donc faux depuis longtemps ».
  - Ligne `50` : « ⚠ un seul tirage par budget : on ne peut pas AFFIRMER que le budget est sans effet, seulement qu'on ne le voit pas ».
  - Ligne `46` : « le contrôle **typographique** de ce témoin a manqué d'**une** fenêtre (5 rendues, 6 nécessaires) ».
  - Note explicite d'exclusion : `55`, `56` et `57` sont hors de la table d'état, délibérément, parce qu'aucun ne porte une affirmation sur le rouleau.
  - La cause candidate lue dans la source du traceur est marquée « Hypothèse, pas conclusion ».
- **preuve de lecture intégrale** :
  - l. 285 : `| [`docs/08_premiere_passe_complete.md`](08_premiere_passe_complete.md) | ⭐ **la passe complete** : des couches aux lettres grecques, AUC 0,92 hors entrainement |`
  - l. 449 : `| Total sur disque | ⚠ **103G** hors `.git` — **le plafond de 100 Go est franchi** |`

---

### docs/00_etat_de_lart.md
- **lignes** : 487
- **nature** : MIXTE
- **résumé** : État de l'art consolidé le 2026-08-17, sourcé sur le miroir du site (81/81 pages), les 33/35 dépôts clonés et des mesures locales. La revue de littérature et l'inventaire des acteurs relèvent du PROCÉDÉ ; les §7 et §9 rapportent des mesures propres au dépôt (reproduction `windcheck`, excision, profondeur de surface, corrélations). Le §10, ajouté le 2026-08-29, est un audit qui déclare le document lui-même insuffisant sur ses conclusions majeures.
- **conclusions extractibles** :
  - Un rouleau scellé a été entièrement déroulé et lu : PHerc. 1667, arXiv 2606.29085, 27 juin 2026, 27 auteurs — **31 spires, 1231 cm², 22 colonnes**, transcrites par huit papyrologues.
  - L'équipe écrit un mois plus tard : *« No method yet traces a complete, correct surface through a scroll automatically »*.
  - **~25 heures d'annotation manuelle par spire**, soit **31 × 25 ≈ 775 heures** ; le Grand Prize 2027 en tolère **huit** — un facteur **~100**.
  - Protocole de scan BM18/ESRF : **2,4 µm, 0,22 m, 78 keV, Paganin δ/β = 1000** ; sur PHerc. Paris 4 l'encre devient directement visible dans le volume.
  - Dans l'article qui lit un rouleau entier, « sheet switches » n'apparaît **qu'une seule fois** et **aucun taux d'erreur de traçage n'est publié**, ni avant ni après correction manuelle.
  - Spiral fitting : Henderson mesure un *winding jump fraction* de **3,20 %**.
  - Surface tracer : **~4 h par soumission** d'intervention humaine.
  - Deux spires voisines sont à **300 µm** ; une feuille fait **40 µm**.
  - `vesuvius-automesh` : **279,4 cm²** de surface rendue vérifiée (~4× les segments tracés à la main), sans annotation manuelle et sans GPU, en streamant depuis S3 ; suivi de la surface humaine à **28–41 µm** de médiane ; seules **61 fenêtres sur 106** passent le contrôle de topologie et seule cette aire est revendiquée.
  - Vérificateurs : `windcheck` **284** traces statuées (274 avec référence propre) ; `tifxyz-doctor` **450** racines ; `winding-sync` **910 germes, 1583 contraintes** (PHerc0358) ; `herculaneum-scroll-tools` **125/125**.
  - `winding-ruler` : les annotations humaines de winding n'apportent que **+3 à 5 pp** là où les patches s'éclaircissent, et **trois générateurs de contraintes successivement meilleurs dégradent tous le fit** ; l'explication pré-enregistrée a été falsifiée par ses auteurs (**93,0 % grossier contre 88,3 % fin**).
  - Corpus : **45 échantillons** (35 rouleaux, 10 fragments), **310 segments** ; **33 sur 45** sans surface tracée ; quatre échantillons concentrent **210 des 310**.
  - Ce qui sépare un échantillon tracé d'un vierge est la **résolution du scan** (1,129 µm et mieux → tracé ; 8,64–9,36 µm → zéro), corrélation de sens indéterminé.
  - Trois échelles par rouleau : surfaces **~220 Mio**, prédictions **~19,6 Gio**, volume **~2,1 Tio** ; pyramide à six niveaux, rouleau entier en 3D dans **33 Gio au niveau 2** (9,6 µm), où une feuille fait ~4 voxels et l'écart entre spires ~31.
  - Reproduction `windcheck` : **364 tests passés** (80 sautés, non comptés) ; niveau 1 reproduit exactement (4 et 7 contacts) ; niveau 2 → **0 contact** ; niveau 3 → **53/53 verdicts et 53/53 comptes de triangles** concordants ; **52 nettoyées, 1 déjà propre, 0 échec**.
  - Les traces `auto_grown` sont **~9× plus atteintes** (**192** événements en médiane contre **21**) — non normalisé par l'aire.
  - Ampleur réelle de l'excision : **0,16 %** de l'aire en médiane, **0,51 %** en moyenne, jusqu'à **2,79 %** ; le segment donné en exemple par le README (0,001 %) est le **moins touché des 52**.
  - Excision : sur 52 segments, **75 810 cellules excisées** contre **303 235 témoins appariés** — moyenne **72,1** des deux côtés, médiane **65** des deux côtés, **p = 0,859**, delta de Cliff **−0,000**. H₀ n'est pas rejetée.
  - Prix : Progress Prizes **20 k$ garantis/mois** + lots 0,5 à 20 k$ ; First Letters **50 k$ par rouleau (≤ 500 k$)** ; Titre de PHerc. Paris 4 **50 k$** ; Grand Prize 2027 **1 M$** — échéance **25 juin 2027**.
  - §9 : **91 des 99 commits** du dépôt sont postérieurs au 2026-08-17, 49 fichiers créés, 12 outils d'analyse, **58 contrôles hors ligne**.
  - Corrélation par tuile entre l'anomalie géométrique de `07` et l'accord encre-prédite ↔ étiquetage humain : **rho +0,019 à n = 89**, contrôle plat ; à ce n la mesure détecterait un rho de 0,3 à 80 % de puissance. « La métrique mesure un défaut de la TRACE, pas du RÉSULTAT. »
  - Fusions localisées en 3D et persistantes (**p = 0,0001**), défaut qui dérive de **1,50 mm de rayon par mm de hauteur**.
  - Traçage de fibres réfuté : l'orientation est mesurable (cohérence **0,64**) mais le signe s'inverse de n = 12 (**+0,330**) à n = 54 (**−0,192**).
  - Sur Scroll 4, sur **61 %** du segment la feuille est **hors du volume de surface**.
  - Métrique de `07` : domaine de définition > 1 tour de couverture, seuil justifié par un **plateau de 0,15 à 0,40** (facteur 2,7), réplication **rho +0,700, p = 0,0012** sur PHerc1667.
  - Profondeur de surface : Scroll 1 **24 et 32 µm** ; Scroll 4 **63 µm**, p90 **134 µm**, et **61 %** des fenêtres ont leur pic à un bord de la pile. Coût **1,78 Mo et 1,03 s par fenêtre** contre **32 Go par segment** par téléchargement des couches — rapport **18 000**.
  - Écarter les 20 % de segments dont le volume de surface porte le moins de matière fait monter le contraste d'encre médian de **+0,381**, **p = 0,0005** contre 2000 permutations, avec un plateau **15–25 %**.
  - Champ de correction : une translation n'enlèverait que **21,7 / 35,3 / 28,6 %** de l'erreur sur trois rouleaux ; correction appliquée, le pic médian revient sur la couche tracée et l'écart tombe de **58 à 8 µm**, la dispersion ne bougeant pas.
  - `PHerc0358` (rouleau du Grand Prize sans segment publié) tracé — **8,48 cm², 13,9 s** —, aplati et rendu (**29,4 × 29,2 mm**), sans jamais télécharger le volume de **893 Go** ; la trace est mauvaise : **240 auto-intersections**, pénétration maximale **200 µm**, mesurées en **0,05 s** avant tout rendu, sur un rouleau dont l'écart inter-feuilles est de **187 µm**.
  - Rayon de recherche dérivé de la physique (pas mesuré **142,8 µm, cv 1,8 %**) : Scroll 1 **+0,769 → +0,840** (p = 1,1e-12) ; PHerc0139 **+0,284 (p = 0,093) → +0,666** (p = 2,3e-05) ; PHerc1667 **+0,700 → +0,579** (p = 0,019). Les 13 rouleaux éligibles sont tous scannés à **8,640–9,362 µm**.
  - Audits adversariaux du 2026-08-29 : sur nos **résultats**, 14 examinés → **6 déjà publiés, 8 à moitié, 0 nouveau** ; sur nos **outils**, 98 examinés → **22 existaient déjà, 50 partiellement, 27 sans équivalent**.
  - Ce qui reste libre sur les 35 dépôts : zéro `binomtest`, zéro test de permutation, zéro analyse de puissance, **aucun intervalle de confiance sur un score d'encre** ; aucun appel à une API de modèle et aucune condition de contrôle dans le protocole publié ; zéro dépliage polaire d'une coupe CT.
  - Sur les **13 rouleaux du Grand Prize**, le monde entier publie **21 segments et 0 carte d'encre**, et **11 sur 13** n'ont aucun segment publié ; le critère demande **100 % du recto**.
  - Raymarcher volumique livré le 2026-08-31 (**162 contrôles verts**) ; **aucun seuil ne sépare les feuilles** — balayage de 130 à 198 sur un chunk niveau 0, feuilles = rubans de **3 à 5 voxels** espacés de **30 à 40**, milieu dont le creux vaut **115 à 130, pas zéro**.
  - Autres repères repris : AUC **0,925** sur 44,7 M de pixels, juge de langue calibré à **15/16** sans fabrication, onde radiale et ses **176 spires** avec invariant à **cv 1,8 %**, corpus passé de 2,6 Go à **~76 Go**.
- **rétractations / corrections internes** :
  - §2 : « ⚠⚠ **Correction du 2026-08-19 : "immunisé au sheet switching par construction" était FAUX** » — la garantie du spiral fitting est topologique, pas sémantique ; *winding jump fraction* 3,20 %.
  - §1 (tableau des étages) : la détection d'encre est « ⚠ **pas "résolu"** » — *« ink segmentation remains weak, varies across ink recipes and local degradation states »*.
  - §9.2, problème 5 : traçage de fibres **❌ réfuté** — « Le site en fait pourtant *le* critère visuel — l'idée est bonne et **notre mesure ne l'était pas** ».
  - §9.4 : « ⚠⚠ **Corrigé le 2026-08-19.** Ce paragraphe annonçait **trois** mesures indépendantes » — la troisième jambe (« 64 % des fenêtres piquant au bord » et une « distribution bimodale ») est **retirée** : la fenêtre de 21 couches ne fait que ±94 µm et **61 % des profils y sont plats** (amplitude médiane 1,5 %), le bruit fabriquant la bimodalité. Le verdict tient sur deux instruments, pas trois.
  - §9.4 : « `20` §4 écrivait que c'était hors de portée "parce que la chaîne maillage → rendu n'est pas ici". **C'était faux, et corrigé le jour même** ».
  - §9.5 : correction d'une correction — « J'ai cru mesurer qu'elle séparait aussi la métrique de `07` elle-même… **C'était le RAYON, pas la résolution** » ; le rayon fixé en voxels couvrait 749 µm à 9,362 µm, soit plusieurs écarts inter-feuilles. PHerc1667 **baisse** et c'est le plus petit corpus — « deux sur trois s'améliorent, à rapporter tel quel plutôt qu'à moyenner ».
  - §10 : « **Ce document date du 2026-08-17 et il a été insuffisant, de façon nommable.** » Le §4 (« six vérificateurs, et c'est saturé ») et le §9.3 (« ce qui n'existait dans aucun des six ») « étaient justes sur les **conclusions** de ces outils et faux sur leur **contenu** : quatre équivalents de nos instruments dormaient dans leur code ». Mode de défaillance nommé : le vocabulaire (*winding pitch*, *linearity*, *subvoxel re-centering*, *CT support*, *sheet consistency*).
  - §0 : « ⚠ **Portée honnête de cette lecture** : elle dit que la case est ouverte, pas que nous l'occupons. »
  - §9.4 : « ⚠⚠ **On a des mesures et des instruments, pas une amélioration.** Aucun maillage n'a été rendu meilleur. »
  - §7 : « ⚠ Portée : un rouleau, une campagne de scan, un outil de réparation. »
- **preuve de lecture intégrale** :
  - l. 300 : `une carte d'encre. **rho +0,019 à n = 89**, contrôle plat, et à ce n la mesure`
  - l. 477 : `⚠⚠ Et un fait mesuré qui contraint toute approche par surface : **aucun seuil ne sépare les`

---

### docs/01_goulot_deroulage.md
- **lignes** : 218
- **nature** : PROCEDE
- **résumé** : Note de cadrage du 2026-08-16 : où en est le concours, ce que « maillage de la surface » veut dire, les deux familles de mailleurs, quatre pistes cotées coût/valeur, l'alignement sur les prix, puis une recommandation. Le corps du document est une feuille de route, et sa partie la plus substantielle est une **auto-correction** : la piste recommandée d'abord (A, « écrire un vérificateur ») est retirée parce que six outils l'occupent déjà, et remplacée par A′.
- **conclusions extractibles** :
  - La chaîne a six étages et **cinq sont automatiques** ; le maillage de la surface est le seul semi-manuel.
  - Deux spires adjacentes sont séparées d'environ **300 µm** ; une feuille fait environ **40 µm** ; là où le rouleau est comprimé, cet écart tombe à zéro.
  - Le spiral fitting mesure un *winding jump fraction* de **3,20 %**, avec pour limite déclarée que la surface erre parfois entre deux enroulements vrais.
  - Le surface tracer coûte encore **~4 h d'intervention humaine** par soumission.
  - Le winding est **déjà calculé** par le concours : `villa/lasagna/` (`labels_to_winding_volume.py`, `opt_loss_winding_volume.py`, `opt_loss_winding_density.py`), `vc_diffuse_winding.cpp`, `apps/diffusion/spiral*.{hpp,cpp}` sur Ceres. Le manque du problème ouvert nº7 est d'**évaluer**, pas de produire.
  - **ThaumatoAnakalyptor est déprécié**, pas seulement migré : il vit dans `villa/deprecated/thaumato-anakalyptor` (avec `crackle-viewer` et `vesuvius-c`).
  - Le **source markdown du site est dans villa** (`scrollprize.org/docs/`, **34 fichiers**), supérieur au miroir HTML pour lire.
  - Six vérificateurs existent déjà (`spiralcheck`, `winding-sync`, `herculaneum-scroll-tools`, `windcheck`, `tifxyz-doctor`, `winding-ruler`) ; `winding-sync` revendique 910 germes / 1583 contraintes sur PHerc0358, `herculaneum-scroll-tools` 125/125, `windcheck` 284 traces (274 avec référence propre), `tifxyz-doctor` 450 racines.
  - `winding-ruler` : **+3 à 5 pp** seulement là où les patches s'éclaircissent, et **trois générateurs de contraintes successivement meilleurs dégradent tous le fit** ; explication pré-enregistrée falsifiée par ses auteurs (**93,0 % grossier contre 88,3 % fin**).
  - `vesuvius-automesh` ne revendique que **61 fenêtres sur 106**.
  - Prix : Progress Prizes **20 k$ garantis/mois** (+ 0,5 à 20 k$), échéance 31 août 2026 puis chaque mois ; Grand Prize 2027 **1 M$** (800/100/50/50), dérouler un rouleau entier avec **70 % de caractères lisibles** ; First Letters **50 k$ par rouleau (≤ 500 k$)**, 10 lettres sur 4 cm² ; Titre de PHerc. Paris 4 **50 k$**.
  - Recommandation retenue : **A′ — fermer la boucle sur UN défaut de bout en bout**, en consommant les six outils au lieu d'en ajouter un.
  - Licence **CC-BY-NC 4.0** : usage non commercial, attribution obligatoire, contrainte propagée à tout dérivé.
- **rétractations / corrections internes** :
  - §3 : « ⚠⚠ **Corrigé le 2026-08-19.** Ce paragraphe disait "structurellement **immunisée** contre le sheet switching". C'est faux, et le papier de la méthode le mesure » — 3,20 %.
  - §3 : « ⚠ **Correction, obtenue en lisant le code plutôt que le site.** J'allais écrire que le concours "n'a pas de moyen de calculer le winding". C'est faux, et l'erreur aurait orienté tout le reste ».
  - §3, deuxième correction : ThaumatoAnakalyptor est **déprécié**, pas seulement migré.
  - §5 : « ### ⚠ Correction : la piste A est déjà occupée six fois » — « Recommander A était une erreur, corrigée en lisant les dépôts du manifeste plutôt que leurs seuls intitulés. »
  - §5, en-tête du tableau des pistes : « Aucune n'est engagée — c'est une liste à trancher, pas un plan. ⭐ **TRANCHÉE depuis** ».
  - §5 : « ⚠ **Rien de tout ça n'est acquis tant qu'on n'a pas mesuré.** » — marquée ⭐ **FAITE depuis** → `03`.
  - §6, première puce : marquée ⭐ **TRANCHÉE** → `02` §1 (on travaille sur les surfaces, pas le volume entier).
- **preuve de lecture intégrale** :
  - l. 147 : `### ⚠ Correction : la piste A est déjà occupée six fois`
  - l. 218 : `  Le jour où il y en a, c'est un lecteur `harvest::` de plus, pas une architecture.`

---

### docs/02_inventaire_mesure.md
- **lignes** : 158
- **nature** : MIXTE
- **résumé** : Inventaire du 2026-08-16 dont tous les chiffres sont mesurés par `src/outils/s3_size.py` sans rien télécharger. Il établit les trois échelles de données (surfaces / prédictions / volumes), corrige son propre cadrage initial en montrant que la pyramide OME-Zarr rend la 3D accessible au niveau 2, dresse l'inventaire des segments par échantillon, et corrige une seconde hypothèse de travail sur ce qui sépare un échantillon tracé d'un échantillon vierge.
- **conclusions extractibles** :
  - PHerc0332 : `segments/` **219,1 Mio** (14 objets), `representations/` **19,6 Gio** (308 416 objets), `volumes/` **2,1 Tio** (1 081 602 objets).
  - Pyramide OME-Zarr à **six niveaux**, voxel de base **2,399 µm** : niveau 0 ~1,8 Tio, niveau 1 (4,8 µm) ~260 Gio, **niveau 2 (9,6 µm) 33,0 Gio**, niveau 3 (19,2 µm) 4,9 Gio, niveau 4 (38,4 µm) 810 Mio, niveau 5 (76,8 µm) 178 Mio.
  - Au niveau 2 une feuille fait **~4 voxels** et l'écart entre spires **~31 voxels** ; au niveau 3, ~2 et ~16 ; au niveau 4 (38,4 µm), **~1 voxel** et ~8 — « trop grossier : deux feuilles ne se séparent plus ».
  - Une surface tracée pèse **~10 Mio**, un volume **~2 Tio** — cinq ordres de grandeur.
  - Les volumes de surface sont publiés en OME-Zarr avec des chunks **`[109, 128, 128]` non compressés** : un chunk porte toute la colonne de profondeur d'une fenêtre 128×128 pour **1,78 Mo et 1,03 s**, contre **32 Go par segment** en téléchargeant les couches — rapport **18 000**.
  - **45 échantillons** publiés (35 rouleaux, 10 fragments) et **310 segments**. Par échantillon : PHercParis4 **81** (1,129 µm), PHerc0172 **53** (7,91 µm), PHerc0139 **38** (1,129 µm), PHerc0500P2 **38** (0,55 µm), PHerc1667 **20** (1,129 µm), PHerc0814 **19** (1,129 µm), PHerc0009B **19** (2,401 µm), PHerc1447 **15** (8,64 µm), PHercMANBp **11** (1,129 µm), PHerc0343P **8** (2,215 µm), PHerc0800 **6** (8,64 µm), PHerc0332 **2** (2,399 µm), **33 autres à 0** (8,64 à 9,362 µm).
  - **33 échantillons sur 45 n'ont aucune surface tracée** ; les quatre premiers concentrent **210 sur 310**, soit deux tiers.
  - Tous les échantillons à 0 segment sont scannés à **8,64 ou 9,362 µm** ; tous ceux qui portent beaucoup de segments sont à **1,129 µm ou mieux** ; aucun échantillon fin n'est à zéro, aucun échantillon grossier n'est bien tracé.
  - `windcheck` recense **284 traces** terminalement statuées (274 avec référence propre) sur les **310** publiées — un quasi-exhaustif, donc rien à gagner à refaire le recensement.
  - Budget à ce stade : miroir du site **228 Mio**, dépôts **2,4 Gio**, surfaces `tifxyz` **~409 Mio** (212 fichiers épinglés par SHA-256) — total **~3 Gio**, soit **3 %** du plafond de 100 Go.
- **rétractations / corrections internes** :
  - §1 : « ### ⚠ Correction : "2,1 Tio" ne veut PAS dire "pas de 3D" » — « Formuler l'étage volume comme un mur était une erreur de cadrage, et elle aurait fait renoncer à toute la 3D pour une mauvaise raison. » Le mur n'était pas la 3D mais la pleine résolution sur tout le rouleau à la fois.
  - §2 : « ### Correction d'une hypothèse de travail » — l'hypothèse que les **petits** échantillons sont plus friables donc plus durs à dérouler n'est pas soutenue par les données ; ce qui sépare tracé de vierge est la résolution du scan.
  - §2 : « ⚠ À ne pas surinterpréter : la corrélation ne dit pas le sens. Il est tout aussi plausible qu'on ait **choisi de rescanner finement** les rouleaux jugés prometteurs. »
- **preuve de lecture intégrale** :
  - l. 112 : `⚠ **33 échantillons sur 45 n'ont aucune surface tracée.** Les quatre premiers en`
  - l. 158 : `première question ne demande pas de données massives, elle demande un instrument.`

---

### docs/03_reproduction_windcheck.md
- **lignes** : 139
- **nature** : RESULTAT
- **résumé** : Reproduction de l'outil `windcheck` à trois niveaux de sévérité croissante (reproduction ponctuelle, recensement indépendant sur les octets relus, recensement de tout le corpus Scroll 5 confronté à la publication). Tous les chiffres publiés par l'outil sont retrouvés exactement. Le document conclut en séparant explicitement ce que la reproduction établit (l'outil fait ce qu'il annonce) de ce qu'elle n'établit pas (que réparer serve à quelque chose).
- **conclusions extractibles** :
  - Environnement : `uv sync` 0 erreur ; noyau C++ `engines/selfcross` compilé en `clang++ -O3 -std=c++17 -pthread`, **53 Kio** ; suite de tests **364 passés, 80 sautés, 122 s** ; données PHerc0172 **212 fichiers, 0,41 Go, VERIFIED, all files match**.
  - Niveau 1 : contacts transverses diagonale 0 **4 annoncés / 4 obtenus**, diagonale 1 **7 / 7** ; verdict *NOT clean* (11 contacts, 1 événement) ; durée 0,2 s chez eux, 0,3 s ici.
  - Segment témoin `20251205115859-w094_…_flatboi` : grille **563 × 520**, **416 398 triangles**.
  - Réparation (`windcheck transform`) : **6 quads retirés**, **99,9989 % de surface conservée**, statut *clean*.
  - Niveau 2 (recensement indépendant sur octets relus, sous les deux triangulations canoniques) : triangles **416 398 → 416 386** (12 = les 6 quads), diagonale 0 **4 → 0**, diagonale 1 **7 → 0**, événements **1 → 0**, verdict **NOT clean → clean**.
  - Niveau 3 (53 segments de PHerc0172 confrontés à `results/index.json`) : noms appariés **53/53**, verdicts concordants **53/53**, comptes de triangles identiques **53/53** — aucun désaccord.
  - Sur Scroll 5, **1 trace saine sur 53** (52 atteintes), alors que le chiffre global publié est « 184 transformées / 90 déjà propres » : la propreté varie énormément d'un échantillon à l'autre et un taux global masque cette dispersion.
  - Par famille : `auto_grown` (9 traces) **9/9 atteintes**, médiane **192** événements de croisement, maximum **664** ; autres (44 traces) **43/44**, médiane **21**, maximum **215** — soit environ **neuf fois** plus atteintes en médiane.
  - Les `auto_grown` vont jusqu'à **3,58 M de triangles** contre **402 k** au minimum.
- **rétractations / corrections internes** :
  - §2 : « ⚠ **80 tests sautés** : à ne pas lire comme "80 tests verts". Ce sont des tests conditionnés à des données absentes. » — le *dénominateur silencieux*.
  - §2 : « ⚠ **Portée de cette décision, précisée le 2026-08-18** » — l'installation du client `aws` dans l'environnement de `windcheck` vaut pour reproduire `windcheck` ; pour la récupération propre au dépôt, `aws` est inutile (bucket public en HTTPS, listage par préfixe, piège nº 16).
  - §5 : « ⚠ **Un écart apparent, levé par la confrontation.** » — le « 1 saine sur 53 » ressemblait à une erreur de mesure et ne l'était pas.
  - §5 : « ⚠ Corrélation, pas causalité : les `auto_grown` sont aussi les plus grandes… Normaliser par l'aire avant d'en conclure quoi que ce soit. »
  - §6 : mise en garde explicite contre la confusion entre « une surface propre est une meilleure surface » (géométrie, prouvée) et « une surface propre donne un meilleur texte » (pipeline, non prouvée).
- **preuve de lecture intégrale** :
  - l. 102 : `pour ce rouleau : 1 saine, 52 atteintes. **La propreté varie donc énormément d'un`
  - l. 139 : `> ressemblent assez pour qu'on prenne la première pour la seconde.`

---

### docs/04_experience_excision.md
- **lignes** : 261
- **nature** : MIXTE
- **résumé** : Conception d'expérience écrite avant le code (§1–5 : question, protocole, hypothèse nulle, contrôles anti-bug, menaces, note de perf) suivie du résultat mesuré (§6) et de sa portée (§7). La question est de savoir si les cellules que `windcheck` excise échantillonnaient autre chose que du papyrus. Réponse : non, H₀ n'est pas rejetée, et un recalcul du 2026-08-22 renforce le résultat en retirant le niveau de gris 0 tout en signalant qu'un chiffre du document reste irreproductible.
- **conclusions extractibles** :
  - §6, **ajouté le 2026-09-05** : les deux commandes de l'arc — `analyse.py` sur `docs/mesures/excision_samples.tsv` (hors ligne, rend exactement p = **0,859**, δ **−0,000**, 52 segments, 75 810 contre 303 235) et `measure.py` pour l'échantillonnage, qui demande le volume. Aucune des deux n'était écrite dans un document, donc le résultat publié n'avait pas de producteur joignable.
  - Le certificat `windcheck` porte `displacement/applied = False` ; l'excision est portée par le masque (`mask = 0` **et** `x = y = z = -1`) ; *« Every RETAINED coordinate is bit-identical to the input »*.
  - Sur le segment témoin : **6 quads sur 416 398 triangles**, **896,8 unités d'aire sur 83 256 262**, soit **0,0011 %**.
  - Le volume utilisé est `20241024131839` à **7,910 µm** ; une feuille y fait **~5 voxels**.
  - Perf : un voxel échantillonné individuellement coûte **512 ms**, une itération de boucle Python **65 ns** — un facteur **huit millions** ; chaque accès rapatriait un chunk de 128³ (~2 Mio) pour lire un octet. Le correctif algorithmique (grouper par chunk) donne **×8** sur 200 points répartis sur 19 chunks, **valeurs identiques**.
  - RÉSULTAT sur **52 segments** de PHerc0172 (le 53ᵉ étant déjà propre) : **75 810 cellules excisées** contre **303 235 témoins appariés**.
  - Statistiques descriptives identiques des deux côtés : moyenne **72,1**, médiane **65**, Q1 **40**, Q3 **105**, écart-type **42,0**.
  - Mann-Whitney U **11 489 329 924**, **p = 0,859**, delta de Cliff **−0,000** (**−0,0004** au recalcul), écart des médianes **+0,0** niveau de gris. **H₀ n'est pas rejetée.**
  - Recalcul du 2026-08-22 sans le niveau de gris 0 : **p = 0,504, δ de Cliff = −0,0016** — la conclusion survit et n'était pas portée par du vide partagé. Le niveau 0 pèse **3,4 %** des excisées contre **3,5 %** des témoins.
  - Contrôle contre l'explication ennuyeuse (une colonne recopiée deux fois) : **256/256 niveaux diffèrent en densité**.
  - Les écarts **par segment** s'étalent sur **±15,6 niveaux de gris** — les segments diffèrent individuellement et s'annulent en agrégat.
  - Décomposition du préliminaire : famille `20250926*` (8 segments, 11 449 excisées) delta **−0,0242** ; tous les autres (44 segments, 64 361) **+0,0047** ; tout (52, 75 810) **−0,0004**.
- **rétractations / corrections internes** :
  - §6 : « ⚠⚠ **La réserve que personne n'avait posée : le niveau 0 est du vide** » — comparer deux échantillons contenant chacun une part de néant dilue toute différence réelle vers zéro ; le p de 0,859 aurait été « rassurant pour une mauvaise raison ».
  - §6 : « ⚠ **Un chiffre de ce document reste irreproductible** » — la ligne par segment (30 négatifs, 22 positifs, médiane **−0,011**) ; le recalcul donne **29 / 23, médiane −0,478** pour un écart de moyennes et **29 / 17 / 6 nuls, médiane −1** pour un écart de médianes. « La statistique d'origine était une troisième quantité, dont le code n'est pas dans l'arbre. Elle est gardée telle quelle et signalée, plutôt que remplacée en silence. »
  - §6 : « ### ⚠ Pourquoi le résultat préliminaire disait le contraire » — une mesure intermédiaire sur 5 segments donnait un effet systématique (delta **−0,072**, répliqué 4/4), qui s'explique par un **biais d'échantillonnage par ordre alphabétique**.
  - §6 : « ⚠ **Et une erreur de lecture à moi, corrigée** : j'avais relevé `n = 1761` pour `w084` alors que c'était `w080` ».
  - §6 : « ⚠⚠ Ce que la figure montre et que le tableau cachait » — « "Pas de différence en moyenne" n'est pas "pas de différence" ».
  - §6/§7 : portée explicitement bornée (un rouleau, une campagne de scan, un outil de réparation) et interdiction de glisser de « les cellules excisées échantillonnent autre chose » à « réparer améliore le texte ».
- **preuve de lecture intégrale** :
  - l. 190 : `> ⭐ **Refait sans le niveau 0 : p = 0,504, δ de Cliff = −0,0016.** La conclusion **survit**,`
  - l. 261 : `papyrologique ; le premier est de la physique mesurable cet après-midi.`

---

### docs/05_le_predicat_est_trop_etroit.md
- **lignes** : 154
- **nature** : RESULTAT
- **résumé** : Mesures sur PHerc0172 montrant que la donnée `separation_rev` de `windcheck` partage le corpus en deux populations, que le résultat négatif de `04` tient dans les deux bandes, et surtout que la réparation d'auto-intersection **supprime le contact sans supprimer l'approche** entre régions distantes de la paramétrisation. Le §4bis retire ensuite la moitié du §4 en montrant que le « 300 µm entre spires » était emprunté à un autre rouleau et faux ici (177 µm mesurés).
- **conclusions extractibles** :
  - `windcheck` publie une séparation en tours de spire (`separation_rev`, `band`) : bande **< 0,15 tour = 43 traces** (croisement local), bande **≥ 1,6 tour = 9 traces**, la trace traversant jusqu'à **5,04 tours**.
  - Les **9 sévères sont exactement les traces `auto_grown`**.
  - Le résultat négatif de `04` tient dans les deux bandes : **< 0,15 tour** — 43 segments, 22 703 excisées, delta de Cliff **−0,0216**, p **4,6e-07** ; **≥ 1,6 tour** — 9 segments, 53 107 excisées, **+0,0090**, p **1,3e-03**. Deux effets négligeables, de signes opposés.
  - Sur `auto_grown_…_1` (grille **629 × 2815**, **654** événements) : à 2 vx (16 µm) **0** paire à ≥ 500 colonnes d'écart ; à 5 vx (**40 µm**, une feuille) **0** (une paire à 329 colonnes) ; à 10 vx (79 µm) **4** ; à 20 vx (158 µm) **8** ; à 40 vx (316 µm) **9**.
  - Énoncé défendable : aux sites de croisement sévères, deux parties de la trace séparées de **jusqu'à 1564 colonnes** dans l'image aplatie s'approchent à **79–158 µm** en 3D.
  - La réparation ne retire pas cette approche : à **10 vx (79 µm)**, **9 croisements avant** → **8 encore après** ; les valeurs sont littéralement inchangées (**974 → 974, 1564 → 1564, 589 → 589, 585 → 585**). La réparation retire **3 220 cellules** (0,2 % des **1 592 534**) et le recensement passe de *NOT clean* à *clean*.
  - Espacement réel mesuré sur la trace (distance de chaque cellule à la partie non adjacente la plus proche, 4 000 cellules) : p1 **61 µm**, p5 **101 µm**, p25 **141 µm**, **p50 177 µm**, p75 **231 µm**, p90 **303 µm**.
  - **37,2 %** des cellules sont à moins de **158 µm** d'une partie non adjacente ; seules **2,1 %** sont à moins de **79 µm**.
  - Le prédicat vérifié est plus étroit que le défaut : `windcheck` rend la surface sans contact transverse et le prouve, mais l'anomalie de proximité survit intacte à la réparation.
  - Ce qui reste, non mesuré par personne : la **proximité anormale entre régions non adjacentes de la paramétrisation**, grandeur continue calculable depuis la trace seule, sans volume ni modèle.
- **rétractations / corrections internes** :
  - §3 : « ⚠ **Correction d'une revendication trop forte.** J'ai d'abord mesuré à 40 voxels et conclu "le même papyrus est rendu deux fois". C'est faux : 40 voxels valent 316 µm, soit l'écart entre spires voisines… À une vraie épaisseur de feuille (5 vx), l'effet **disparaît**. »
  - §4bis : « ⚠⚠ **Correction : "300 µm entre spires" était emprunté, pas mesuré** » — le chiffre venait du README de `vesuvius-automesh` et portait sur le **Scroll 3** ; l'écart typique mesuré ici est **177 µm**. Conséquence : le résultat à **20 vx (158 µm)** portait sur une distance parfaitement ordinaire, **il ne prouve rien et il est retiré** (barré dans le tableau du §4) ; le résultat à **10 vx (79 µm)** tient.
  - §4bis : la correction est déclenchée par une observation de l'auteur sur une image du site, pas par une relecture de code ; leçon de conception : toute métrique de proximité doit être normalisée par l'espacement local, jamais comparée à une constante.
  - §5 : « ⚠ **Portée** : un rouleau, une trace analysée en détail pour la §3–4, un outil de réparation. À étendre aux 9 sévères avant toute revendication générale. »
- **preuve de lecture intégrale** :
  - l. 114 : `**L'écart typique est 177 µm, pas 300.** Et **37,2 %** des cellules sont à moins de`
  - l. 154 : `réparation. À étendre aux 9 sévères avant toute revendication générale.`

---

### docs/06_mesures_a_faire.md
- **lignes** : 663 ⚠ (643 quand la fiche a été écrite ; commandes de régénération de `33` et `37`, puis l'avertissement que la commande de `proximity_scroll1.jsonl` n'écrit plus le même fichier, le 2026-09-04)
- **nature** : MIXTE
- **résumé** : Carnet de mesures — registre des mesures faites, à faire, écartées, chacune avec son critère de réfutation. C'est structurellement un PROCÉDÉ (liste de tâches et règles de méthode), mais plusieurs entrées portent leur résultat en entier : la théorie du dommage par tranche de rayon (§2.4), l'ellipticité (§2.4bis), la table des mesures 3.x, et surtout le §7 « onde radiale » qui est un compte rendu complet de quatre formulations successives dont trois ont échoué. Le document se termine sur une section « ce qui ne marche pas ».
- **conclusions extractibles** :
  - Contexte vérifié : début du texte = extérieur du rouleau, fin du texte + colophon = cœur ; ce qui est perdu si les couches externes sont abîmées est le **début**.
  - Papiers primaires : cible de résolution latérale de l'ordre de **~1 µm**, et seul **1,02 µm** passe encore le seuil de DICE **0,70** ; les 13 rouleaux du prix sont à **8,64–9,36 µm**, soit un facteur **8,6 à 9,4** trop grossier ; un modèle appris sur du fin rend **zéro** à **3,40 µm**.
  - 1.11 : espacement **158 µm au cœur → 203 µm dehors** (+28 %, monotone sur 5 tranches).
  - 1.15 : iGPU Arc utilisable depuis WSL2 — **×4,5** (104 → 23 ms/fenêtre), sortie identique au CPU à **4,9e-6**.
  - 1.17 : passe complète du pipeline — **AUC 0,919** hors entraînement, lettres grecques visibles, **52 s/cm²**.
  - 1.18 : l'étiquetage de vérité terrain est **partiel** — 50 % des lignes sans étiquette, donc la précision est un **plancher**.
  - 1.16 : pas de balayage 21 vs 32 — corrélation **0,941**, mais **17,9 %** de désaccord au seuil médian et **3,0 %** sur l'encre franche.
  - 1.14 : la métrique survit à la réparation — recensement **11 673 → 0**, métrique **0,37 → 0,38 %**, témoin sain **0,09 %**.
  - Matériel : NPU **non exposé à WSL2** (`/dev/accel` absent) ; OpenVINO ne convertit pas le modèle (einsum des rotary embeddings) ; le GPU fonctionne sans `/dev/dri`, par `/dev/dxg` ; 22 fils CPU s'effondrent à **734 ms/fenêtre** ; 4 cm² en **5,6 min**, segment entier en **3,4 h** au pas 21.
  - 2.3 : `umbilicus.txt` n'existe **sur aucun des 4 corpus** ; déplacer le centre de **3,16 mm** (22 écarts inter-feuilles) bouge l'invariant de **1,75 %**, c'est-à-dire **sous** son propre cv de **1,8 %**.
  - 2.4 : contraste feuille/interstice par tranche de rayon sur 3 coupes — le cœur est le plus dégradé sur 2 coupes sur 3 (déficit **20 %** contre la meilleure couronne) ; l'extérieur ne décline que de **5 à 8 %**. Le profil **n'est pas un U**.
  - 2.4bis : le rouleau est nettement elliptique partout — rapport des axes **1,26 à 1,57** (le plus écrasé au milieu, 1,57 en z = 4300), périmètre du contour **144,0 à 157,7 mm** (cv 0,035), rayon médian **21,3 à 25,1 mm** (cv 0,051).
  - 3.1 : sur 46 traces de Scroll 1, rho **+0,769** avec les croisements, **+0,820 / +0,944 / +0,739** par tercile de longueur ; rho longueur~croisements **0,05** — le confond de `05` n'existe pas dans Scroll 1.
  - 3.2 ⚠ **ANCIEN RAYON, marge périmée le 2026-09-04 (`07` §11)** — au rayon corrigé boule 400 **+0,803**, boule 200 **+0,738**, colonnes 150 **+0,840** : le verdict survit (la bande reste devant) mais l'écart tombe de **0,209 à 0,036**, sous le bruit du rho. Ce qui reste est la **couverture** (boule 100 : 20,7 %). Texte d'origine : la fenêtre « locale » couvre **96,9 % d'un tour** et le rayon y varie de **59,5 %** de l'étendue radiale, mais le remède de principe (référence en boule) rend la métrique **pire** : **+0,474** (boule 200 vx) et **+0,560** (boule 400 vx) contre **+0,769**. Les fenêtres en colonnes forment un plateau **+0,755 à +0,805** de ±10 à ±150. Boule/bande vaut **1,001** en médiane sur les cellules ordinaires (45 traces) et **0,766** aux cellules signalées (43 traces sur 45, Wilcoxon apparié **p = 1,4e-09**).
  - 3.3 : recensement Scroll 1 vs publication — **55/55 triangles et 55/55 contacts** concordants.
  - 3.4 : le lien orientation des fibres ~ croisements est **réfuté** — signe s'inversant de n = 12 (**+0,330**) à n = 54 (**−0,192**) ; cohérence jusqu'à **0,64** ; angle restant à **90–97° sur les 109 couches** ; la cohérence tombe à **0,06** dans l'interstice ; désaccord entre fenêtres voisines **4,3° à 42,5°** sur 12 segments ; à n = 12 la mesure ne détecte qu'un rho ≥ **0,73**.
  - 3.5 : **89 %** des murs conservés au niveau 2 (**33 Gio**) contre le niveau 0 (**2100 Gio**) ; la falaise est entre les niveaux **2 et 3** (89 % → **47 %**).
  - 3.6 : le bucket publie les volumes de surface en **45,532 / 2,4 / 1,129 µm** et **37 segments de Scroll 1 les ont tous les trois** ; à 1,129 µm une pile de 109 couches ne fait que **123 µm**, soit moins qu'une épaisseur de feuille. PHerc0172 ne publie que du **7,91 µm** (deux volumes), donc les 4 sites de fusion ne peuvent pas être revus plus fin.
  - 3.7 : supprimer le seuil dégrade la métrique (**+0,340** contre **+0,769**) ; plateau de **0,15 à 0,40** (rho **0,759 à 0,779**) puis effondrement au-delà de 0,5.
  - 3.8 : corrélation proximité ~ lisibilité sur `20230909121925` — tuiles de **512 px** n = 34 rho **+0,186** (p = 0,29) ; tuiles de **256 px** n = 89 rho **+0,019** (p = 0,86) ; contrôle plat des deux côtés (**−0,031** et **−0,010**) ; à n = 89 un rho de 0,3 serait détectable à 80 % de puissance. **La réponse est NON.**
  - 3.11 : profondeur de surface — Scroll 1 **63 %** et **50 %**, Scroll 4 **7 %** ; écart interquartile **4,0 / 11,5** contre **22,0** ; Scroll 4 est **bimodal** (92 fenêtres au bord bas, 49 au bord haut) ; le filtre de couches change le résultat (**76 % → 63 %**). Elle **ne classe pas** la lisibilité.
  - 3.13 : sur les 53 traces de Scroll 5, **44 rendent zéro cellule** ; la coupure est exactement à **un tour** (mesurées **2,99–9,07**, écartées **0,50–1,00**) ; les 9 survivantes sont neuf morceaux du même segment, donc **n = 1**.
  - 3.14 : aucune grandeur sans seuil n'égale `fraction_below_third` — `shortfall` **+0,340**, `ratio_p5` **−0,512**, contre **+0,769**.
  - 3.12 : passe complète Scroll 4 — **107 730 fenêtres, 42,6 min, 48,1 M pixels** ; le juge calibré rend une lisibilité de **1 à 3** quand le calibrage sépare vierge **0–1** de texte **3–6** : pas de séparation. Scroll 4 n'offre aucun témoin vierge (bande la plus pauvre à **4,59 %** contre **1,14 %** sur Scroll 1). Le même panneau à température zéro donne **1 puis 2 puis 0** glyphes selon son voisin.
  - 3.10 : le défaut **dérive** — piste de **5 coupes traversant 4,75 mm de rayon** (dérive **1,50 mm/mm**) contre 3 coupes / 1,42 mm à fenêtre fixe ; **p = 0,0010**, **0,005 après Bonferroni** sur 5 grandeurs. Dans la même plage de z, le niveau 0 trouve le site à **77–88 %** du tour et le niveau 2 **rien entre 74 % et 88 %** ; les **18 %** de colocation du rouleau entier portent donc sur une autre population de sites.
  - 3.9 : les **7 traces à 0 croisement** s'étalent de **0,020 % à 0,372 %**, facteur **18** — la métrique ne classe pas, elle corrèle.
  - A : segment `20230909121925` entier — **99 918 fenêtres, 38,5 min** sur l'iGPU Arc, **AUC 0,925** sur **44,7 M de pixels**, contrôle mélangé à **0,500**, **4 à 5 lignes** de grec lisible sur **91,7 × 30,7 mm**.
  - B : contrôle en aveugle des modèles de langue — **15/16, zéro fabrication**, lisibilité séparant sans chevauchement le vierge (0–1) du texte (3–6).
  - C : la règle **ne réplique pas** — Scroll 1 **+0,539**, PHerc0139 **−0,229**, PHerc1667 **+0,425**, PHerc0172 **−0,217**.
  - §7 onde radiale, PHerc0172, une coupe, 36 rayons : **158 feuilles en médiane** (120 à 194), espacement **136 à 158 µm**, rayon extérieur **22,7 mm**, longueur estimée du papyrus **11,2 m** (borne **inférieure**) ; monotonie de l'angle mesurée à **1,000**.
  - Dépliage polaire : coupe dépliée en **3000 × 18 850** ; dérive **0,125 voxel par colonne**.
  - Premier passage de suivi : **13 074 pistes** retenues et **12 249 « fusions »** sur une coupe qui compte 158 feuilles, longueur médiane **111 colonnes sur 18 850** (~80 morceaux par feuille) ; répartition **6488 en deçà / 6496 au-delà** du rayon médian.
  - Diagnostic : **142 murs par colonne, cv 0,11** ; tolérance 40 → **139** pistes traversantes ; prédiction de pente **21 → 69** longues pistes.
  - Trois hypothèses réfutées : appariement hongrois **17** pistes longues contre **69** pour le glouton ; sursis 0 → 10 contre sursis 20 → **17** ; le détecteur retrouve **92 %** des murs à moins de **2 voxels**, **99,2 %** à 12, médiane **0**.
  - Vraie cause : par colonne, **126 murs trouvés, 125 appariés**, **186 pistes vivantes**, **1** piste neuve ; le compte local est propre à **126 ± 3** murs, soit **2,4 %** de dispersion.
  - Doublement d'écart : contrôle sur lignes fabriquées → **0 site** intactes, **exactement 1** avec une soudure. Au rayon r = 100, `2πr/18850` fait **0,03 voxel**, donc une trentaine de colonnes lisent le même pixel — le cœur est inexploitable par construction et exclu sous **2,4 mm**.
  - Balayage de la coupe : 1,6 mm → 11 cellules (site le plus interne 1,4 mm) ; 2,4 → 8 (2,4) ; 3,6 → 5 (3,3) ; **4,7 → 4 (17,1)** ; 6,3 → 4 (17,1). Le site le plus interne suit la coupe exactement → artefacts de bord.
  - Résultat : à la coupe validée de 4,7 mm, **4 cellules anormales sur 1392** (0,29 %), fond **6,6 %** — 18,0 mm/~14 000 (**20,3 %**), 17,1 mm/~16 500 (19,3 %), 17,6 mm/~15 500 (18,8 %), 17,1 mm/~16 000 (17,1 %) — groupées dans un secteur angulaire d'environ **50°**, à 17 mm sur un rayon extérieur de 22,7 mm.
  - Ce qui ne marche pas : la localisation des fusions par déficit de compte donne **475 sites sur 180 rayons** (2,6 par rayon), **tous concentrés entre 0,5 et 2 mm de rayon** — c'est une carte des endroits où le compteur est peu fiable.
- **rétractations / corrections internes** :
  - §0 : « ⚠ Une première version de cette ligne annonçait "4 µm, facteur 2,2" : chiffre écrit depuis le résumé sans ouvrir le corps de l'article, corrigé après lecture intégrale. »
  - §2.1 : « ❌ ÉCARTÉE — remplacée par le dépliage polaire » ; `winding.py` « n'a jamais tourné jusqu'au bout » et le fichier est **supprimé plutôt que gardé « au cas où »**.
  - 1.10 : « le "9×" était tautologique » (bande sévère ≡ couverture > 1 tour).
  - §2.4 : l'hypothèse du dommage en **U** est **à moitié confirmée seulement** — « Ce qu'elle perd : l'extérieur n'est **pas** le plus abîmé… Le profil n'est donc **pas un U** ». Limite : la bande extérieure a 30 % d'échantillons en moins, donc une part du déclin est un effet de bord.
  - §2.4bis : « ⚠⚠ **Deux défauts de ma propre mesure, trouvés avant de conclure** » — (1) la portée plafonnait à 22,7 mm et l'axe long ressortait à **22,7 mm sur les huit coupes**, la mesure saturant contre sa propre limite ; (2) le « périmètre » valait `Σ r·dθ`, c'est-à-dire **2π × rayon moyen**, donc comparer sa dispersion à celle du rayon revenait à comparer une grandeur à elle-même.
  - §3.2 : le remède de principe (référence en boule) est **faux** — « une référence doit être **large dans la direction où l'anomalie est petite** ».
  - §3.4 : **❌ RÉFUTÉE** — « Le site en fait *le* critère visuel : l'idée est bonne, notre mesure ne l'était pas. »
  - §3.5 : « ⚠ Et un premier essai rendait "53 feuilles au niveau 1" : c'était un artefact de **seuil**, pas de résolution. »
  - §3.6 : « ❌ **IMPOSSIBLE pour les 4 sites** ».
  - §3.10 : « ⚠ Ma grandeur discriminante annoncée (la *rectitude*) a **échoué** : p = 0,82, une chaîne aléatoire de 3 points est monotone une fois sur deux. »
  - §3bis A : « ⚠ **Et elle a réfuté la raison pour laquelle elle était prioritaire.** » — le segment entier n'a pas plus de lignes, le juge mécanique a donc échoué une troisième fois.
  - §3bis C : « ⚠ Et mon explication par un effet de plancher couvrait **un corpus sur trois**. »
  - §5, règle 1 : « ⚠ Corrigé le 2026-08-19 : cette ligne annonçait "un facteur **trois**", et les deux chiffres que ce document mesure lui-même donnent **+28 %**… soit un facteur **1,28**. » ⚠ Le §7 (doublement d'écart) réutilise pourtant toujours la formulation « l'espacement varie d'un facteur trois selon le rayon (158 µm près du cœur, 203 µm vers l'extérieur) » — la correction du §5 n'a pas été propagée là.
  - §7 : « ⚠⚠ **Conséquence : les 12 249 "fusions" du premier passage étaient des changements d'étiquette, pas des soudures.** Le chiffre ne mesurait rien de physique. »
  - §7 : « ⚠ **Correction d'une attente** : à grande échelle les spires ne sont **pas** horizontales, ce sont de larges dômes ».
  - §7 : « ⚠⚠ **Le code de cette section a failli etre perdu.** » — écrit en `python -c`, récupéré du transcript de session ; d'où la règle §5.6.
  - §7 : « ⚠ **Ce qui n'est PAS établi** : que ces quatre cellules soient des soudures. »
- **preuve de lecture intégrale** :
  - l. 420 : `   2026-08-19 : cette ligne annonçait « un facteur **trois** », et les deux chiffres que`
  - l. 663 : `rayon). Il faut la suivre, pas la recompter.`

---

### docs/07_reparee_nest_pas_propre.md
- **lignes** : 1179 ⚠ (438 quand la fiche a été écrite, 482 le 2026-09-03 ; deux sections neuves le 2026-09-04, §10 et §11, qui **périment le §8**)
- **nature** : RESULTAT
- **résumé** : Le résultat central du dépôt sur la métrique de proximité : la réparation d'auto-intersection ramène les contacts à zéro et **ne déplace pas** la proximité anormale (0,37 → 0,38 %). Le document se corrige ensuite trois fois — il retire l'affirmation que la métrique **sépare** saines et réparées, il montre que le remède de principe pour la référence locale (une boule 3D) rend la mesure pire, et il découvre que la métrique est **inapplicable** sous un tour de couverture (44 traces de Scroll 5 sur 53 rendent zéro cellule). Le §9 remplace enfin le rayon de recherche par une constante physique. ⚠ Le fichier contient deux sections numérotées « ## 6 ».
- **conclusions extractibles** :
  - Dispositif à longueur contrôlée : trois traces du même rouleau à **7,66 / 7,82 / 7,92 tours**, portant **0 / 52 / 408** croisements publiés ; comptes de triangles **1 047 154 · 3 615 528 · 5 850 912** et contacts **1 584 · 11 673** concordants avec la publication.
  - `fraction_below_third` : témoin **0,09 %** (espacement médian 160 µm), peu atteinte **0,15 %** (140 µm), très atteinte **0,37 %** (138 µm) — monotone avec le nombre de croisements, à longueur égale.
  - La réparation retire **3 689 quads** (**0,12 %** de l'aire), fait tomber les contacts de **11 673 à zéro**, et la métrique passe de **0,37 à 0,38 %**.
  - Population des traces à zéro croisement (n = 7) : médiane **0,090 %**, étendue **0,020 – 0,372 %** ; avec croisements (n = 39) : médiane **0,230 %**, à partir de 0,040 %. Seules **36 %** des traces atteintes dépassent la pire des saines.
  - Sur 46 traces de Scroll 1 : rho proximité~croisements **+0,769** (p = **4,3e-10**) ; proximité~longueur **−0,232** (p = 0,12, non significatif) ; longueur~croisements **+0,050**.
  - Par tercile de couverture : 0,26–2,03 tours (n = 16) **+0,820** ; 2,03–3,97 (n = 15) **+0,944** ; 3,98–18,03 (n = 15) **+0,739**.
  - Coût de calcul : arbre k-d, **0,4 s** de construction sur **1,6 M de points** ; ni volume, ni modèle, ni étiquette.
  - Balayage de la référence ⚠ **ANCIEN RAYON** (au corrigé : colonnes ±150 **+0,840**, boule 400 **+0,803**, boule 200 **+0,738**) : colonnes ±50 **+0,805** (1,6e-11) ; ±100 **+0,793** ; ±150 **+0,769** ; ±20 **+0,765** ; ±10 **+0,755** ; boule 400 vx **+0,560** ; boule 200 vx **+0,474** (couverture 94 %) ; boule 100 vx **+0,206** (p = 0,17, couverture 24 %).
  - ±150 colonnes couvrent **96,9 % d'un tour** et le rayon y varie de **8,62 mm**, soit **59,5 %** de l'étendue radiale.
  - Rapport boule/bande : sur les cellules ordinaires **1,001** en médiane sur 45 traces, p10–p90 **[0,995 ; 1,015]** ; aux cellules signalées **0,766**, p10–p90 **[0,454 ; 0,945]**, effondrement spécifique sur **43 traces sur 45** (Wilcoxon apparié **p = 1,4e-09**). Ampleur : **23 %** de baisse aux cellules signalées contre **0,1 %** partout ailleurs ; **2 traces sur 45** vont dans l'autre sens.
  - §7 : sur les 53 traces de Scroll 5, **9 seulement** rendent une mesure, **44 rendent zéro cellule** ; les 9 mesurées couvrent **2,99 à 9,07 tours**, les 44 écartées **0,50 à 1,00**. Les 9 sont `auto_grown_20251115002740308_{0..8}`, neuf morceaux du même segment — **n = 1**.
  - Populations par corpus : PHerc0814 13 traces, médiane **3,10** tours, **12** > 1 tour ; PHerc1667 20 / **1,29** / 17 ; PHerc0139 38 / **1,11** / 35 ; Scroll 1 55 / **2,70** / 37 ; Scroll 5 53 / **0,92** / 10.
  - §8 ⚠ **ANCIEN RAYON, périmé par le §11** : `fraction_below_third` **+0,769** ; `fraction_below_half` **+0,659** ; `ratio_p5` **−0,512** ; `shortfall` **+0,340**. Au rayon corrigé : **+0,840**, **+0,877**, **−0,851**, **+0,785**. Balayage du seuil : 0,15 → **0,759** ; 0,20 → 0,773 ; 0,25 → 0,770 ; 0,30 → **0,779** ; 1/3 → 0,769 ; 0,40 → 0,774 ; 0,50 → **0,659** ; 0,60 → 0,488 ; 0,70 → 0,282. Un facteur **2,7** sur le seuil sans que le rho bouge, puis effondrement.
  - §9 : balayage du rayon sur la donnée grossière — 10 vx (**94 µm**) **+0,446** (p = 0,064, 18 traces) ; **20 vx (187 µm) +0,609** (p = 1,3e-04, 34) ; 40 vx (374 µm) **+0,459** (p = 0,0056, 35) ; 80 vx (749 µm, valeur en vigueur) **+0,284** (p = 0,093, 36) ; 160 vx (1498 µm) **−0,143** (p = 0,407, 36). Au-delà, la corrélation **s'inverse**.
  - Le pas inter-feuilles a été mesuré ailleurs et avant : **142,8 µm, cv 1,8 %**.
  - Avec le rayon issu de la physique : Scroll 1 **+0,769 → +0,840** (p = 1,1e-12) ; PHerc0139 **+0,284 → +0,666** (p = 2,3e-05) ; PHerc1667 **+0,700 → +0,579** (p = 0,019).
  - Sur Scroll 1, le rayon issu de la physique (**+0,840**) bat le meilleur rayon du balayage (**+0,829** à 16 voxels).
  - Les **13 rouleaux éligibles au Grand Prize 2027 sont tous scannés à 8,640–9,362 µm**, et le règlement interdit d'utiliser des scans plus fins du même rouleau.
- **rétractations / corrections internes** :
  - ✅✅ **2026-09-04, §12, LA CONCLUSION-TITRE EST CONFIRMÉE — cette fois avec un instrument
    capable de la contredire.** Le bruit d'échantillonnage a été **retiré** au lieu d'être borné :
    la grille de paramétrisation ne change pas quand la réparation retire des quads (756 x 2940
    des deux côtés, 142 cellules perdues sur deux millions), donc un tirage par **position de
    grille** rend le même échantillon des deux côtés. Effet médian sur `shortfall` :
    **1,58 % → 0,07 %**, facteur 22, et **10 traces sur 10** sous leur propre bruit de graine
    contre 4 sur 10 qui en sortaient. ⭐ Le plus parlant est le compte : **7 traces sur 10 comptent
    exactement les mêmes cellules sous le tiers avant et après**. La borne passe de ~5 % à
    **0,6 %** au pire. ⚠ Ce n'est pas « ne fait rien » : la réparation supprime bien les contacts
    (11 673 → 0) ; ce qu'elle ne déplace pas, c'est la proximité entre régions non adjacentes.
  - ⚠⚠⚠ **2026-09-04, §10, LA RÉTRACTATION CI-DESSOUS EST ELLE-MÊME ANNULÉE** — postérieure à
    cette fiche. La mesure qui renversait la conclusion-titre portait sur
    `fraction_below_third`, dont le bruit d'échantillonnage **domine l'effet mesuré** : à
    maillage identique, changer la seule graine du tirage la déplace de **35 à 229 %**, soit plus
    que la réparation sur **9 traces sur 10**, et son numérateur tient sur un chiffre (les
    +398 % sont **une cellule qui en devient cinq**). Le contrôle que j'avais écrit pour m'en
    protéger — « trois runs rendent le même nombre » — ne pouvait rendre qu'un seul résultat :
    il vérifiait la **reproductibilité** et j'en tirais la **stabilité sous
    ré-échantillonnage**. Rejouée sur `shortfall` (sans seuil, bruit < 5 %), la réparation ne
    déplace **rien de mesurable** : 0 paire sur 10 au-delà du bruit, signe mélangé. **La
    conclusion-titre d'origine est restaurée**, pour une bien meilleure raison qu'elle ne
    donnait. Mesures : `le_bruit_de_lechantillon.py`, `reparation_et_proximite.py`.
  - ✅ **2026-09-04, §9, LA QUESTION LAISSÉE OUVERTE EST TRANCHÉE PAR L'ARTEFACT LUI-MÊME.**
    Le §9 écrit que `sweep_PHerc1667.jsonl` « n'enregistre ni le zarr ni la taille de voxel, donc
    rien ici ne tranche ». Le fichier date du 2026-08-26, le paragraphe du 2026-09-03, et il
    déclare `voxel_um 7,91`. Les deux branches du §9 supposaient **2,399 µm par voxel** : à 7,91,
    18 voxels font **142,4 µm**, apparié aux 142,8 de Scroll 1 et aux ~140 de PHerc0139. **La
    ligne PHerc1667 est lisible** et sa conclusion tient. ⚠ Reste vraie la moitié « ni le zarr ».
    ⭐ Et la leçon d'outillage du §9 — *« un artefact de mesure doit porter la résolution sur
    laquelle il a été pris »* — n'avait **jamais** été appliquée à `proximity.py`, ce qui est
    exactement ce qui a coûté l'archéologie du §11. Les deux producteurs écrivent désormais le
    même bloc `echelle`.
  - ⭐⭐⭐ **2026-09-04, §11, LA CAUSE COMMUNE** — postérieure à cette fiche. **Trois**
    familles de paramètres cessent de compter ensemble au rayon corrigé : le seuil (chute
    **0,477 → 0,025**), la grandeur (écart `fbt` / `shortfall` **0,429 → 0,054**) et la référence
    locale (écart bande/boule **0,209 → 0,036**). Aucun des trois n'était mal choisi : un rayon
    4× trop grand injecte une erreur structurée — la **spire voisine** — et toute variation ne
    changeait que la part qui en fuyait. Les fichiers le disent eux-mêmes : une distance est
    plafonnée par le rayon, donc l'ancien fichier impose **≥ 382,6 µm**, soit **2,7 pas de
    feuille**, contre **0,88** au corrigé. ⚠ Ce qui RESTE une vraie différence est la
    **couverture** : la boule de rayon 100 ne mesure que **20,7 %** des cellules.
    Outils : `le_seuil_au_bon_rayon.py`, `le_rayon_des_mesures.py`.
  - ✅ **2026-09-04, §11, MAIS L'EXPLICATION DU §6 SURVIT — plus forte.** Le mécanisme
    (« l'anomalie normalise sa propre référence » : une boule centrée sur un site de croisement
    est pleine d'autres cellules du même site) tient au rayon corrigé, et sur **34 traces sur
    34** au lieu de 43 sur 45, Wilcoxon **1,2e-10**. Ce qui a disparu est sa **conséquence** sur
    la corrélation. ⚠ Cette mesure n'avait **aucun consommateur** — le bloc `contamination` est
    écrit par `baseline_sweep.py` depuis toujours et rien ne le relisait ; le lecteur existe
    désormais et **retrouve exactement** les quatre nombres publiés.
  - ⚠⚠⚠ **2026-09-04, §11, LE §8 EST PÉRIMÉ** — postérieure à cette fiche. Le §9 a corrigé le
    rayon de recherche (4× trop grand) et n'a re-mesuré **qu'une colonne** ; le §8, qui compare
    les grandeurs entre elles, porte encore l'ancien rayon. Au bon rayon l'écart
    `fraction_below_third` / `shortfall` tombe de **0,429 à 0,054**, et le « plateau puis
    effondrement » qui justifiait le seuil devient un plateau **sur toute la plage** (chute
    **0,477 → 0,025**). Donc *« aucune grandeur sans seuil ne l'égale »* et *« le seuil n'est
    pas supprimable »* sont faux sur l'instrument corrigé : **le seuil ne sélectionne aucun
    régime**. ⚠ Et personne ne l'avait rejoué parce que le producteur `run_proximity.sh` ne
    tournait plus — il avalait son erreur et un run qui ne mesurait rien sortait en 0.
  - ✅ **2026-09-04, §10, LA CAUSE EST NOMMÉE PAR L'OUTIL LUI-MÊME.** Le remède de `44`
    (graine + un seul fil) était la première hypothèse : **testée et réfutée** — à `--threads 1`,
    huit réparations rendent encore trois géométries. Le certificat, lui, déclare
    `selection_status: mixed`, `method_mix: 163 exact / 18 glouton`,
    `minimum_area_claim_admissible: False`, et la politique gelée de `windcheck` porte
    `improvement_budget_s_per_segment: 120.0` — *« SEGMENT-WIDE wall-clock budget shared by all
    components »*. Combien de composantes atteignent le solveur exact dépend de la vitesse de la
    machine. **Corrélation mesurée** : `(163 exact, 18 glouton) → 3 696` cinq fois,
    `(164, 17) → 3 691` une fois — une composante de plus à l'optimum, cinq quads de moins.
    ⭐ Ce n'est donc **pas un défaut** : la `failure_rule` dit qu'un dépassement de budget
    *« NEVER removes the feasible incumbent; it costs an optimality claim, never an artifact »*.
    La sortie est toujours valide, seule son optimalité varie. ⚠ Aucun drapeau utilisateur ne
    peut la rendre bit-reproductible ; le remède est de réparer **une fois** et garder la sortie.

  - ⚠⚠⚠ **2026-09-03, en-tête, RÉTRACTATION DE LA CONCLUSION-TITRE** — postérieure à cette
    fiche. Le chiffre central (0,37 → 0,38 %, « la réparation ne déplace pas ») a été rendu
    recalculable pour l'article : réparer une trace, remesurer. **Il ne se généralise pas.**
    Sur les deux traces de Scroll 5 où la métrique s'applique, la proximité **baisse** —
    1,464 → 0,735 % et 3,483 → 2,707 %, soit −49,8 % et −22,3 % — et **pas proportionnellement
    à ce qui est retiré**. Ce qui reste établi : la corrélation (ρ = +0,769) et le rayon dérivé
    de la physique. Mesure : `docs/mesures/reparation_deplace_la_proximite.json`.
  - ⚠⚠⚠ **2026-09-03, §9, UNE CORRECTION QUI ÉTAIT ELLE-MÊME FAUSSE** — postérieure à cette
    fiche. Le §9 annulait sa ligne `PHerc1667` en affirmant que ce rouleau « n'a AUCUN volume
    à 7,91 µm ». Il en publie un (`20231117161658-7.910um-53keV`), et le maillage lu par le
    balayage le nomme. La vue interrogée listait des **volumes de surface**, pas des scans.
    **Troisième occurrence du même angle mort** (après `59` et `67` §4.2), d'où un garde-fou
    plutôt qu'une troisième correction : `src/volume/ou_vit_ce_rouleau.py`.
  - §3 : « ### ⚠⚠ Correction : "quatre fois au-dessus d'une trace saine" était faux » — c'était une comparaison à un seul témoin, qui se trouvait être bas. **L'énoncé qui tombe** : que la mesure sépare proprement « réparée » de « saine ». « Elle ne le fait pas — c'est un indicateur continu corrélé, pas un classifieur. »
  - §6 (« La référence locale ») : « **Le remède de principe rend la métrique nettement pire** » ; et « un gain de +0,036 en passant de 150 à 50 ne vaut pas qu'on retienne 50 ». Réserve explicite : que la chute de rho de 0,805 à 0,560 soit **entièrement** expliquée par l'effondrement de référence « n'est pas établi par cette mesure seule ».
  - §7 : « la métrique n'est pas *moins bonne*, elle est **inapplicable** » sous un tour de couverture — « Elle ne rend pas un mauvais chiffre — elle ne rend **rien**. » Et : « ⚠ La corrélation observée sur ces 9 morceaux (**rho +0,433, p = 0,244**) **ne doit pas être citée** : n = 1 observation indépendante ».
  - §7 : le confond longueur/qualité de `05` s'explique par le fait que, sur Scroll 5, seules les traces longues sont mesurables.
  - §9 : « J'ai d'abord cru à un effet de **résolution du scan**. Le contrôle l'a réfuté. » — « Ce n'est pas la résolution : c'est le rayon. »
  - §9 : « ⚠⚠ **Corrigé le 2026-08-19 : PHerc1667 n'a AUCUN volume à 7,91 µm.** » La ligne PHerc1667 du tableau **ne peut pas être lue** (rayon physique de 140 µm → ~58 voxels à 2,399 µm, ou 18 voxels → 43 µm seulement) ; « L'artefact `docs/mesures/sweep_PHerc1667.jsonl` **n'enregistre ni le zarr ni la taille de voxel**, donc rien ici ne tranche. ✅ **À rejouer en enregistrant la résolution** ».
  - §9 : « ⚠ **PHerc1667 baisse**… Deux corpus sur trois s'améliorent, le troisième se dégrade — à rapporter tel quel, pas à moyenner. »
  - §5 : « **La corrélation est établie (46 traces), la séparation ne l'est pas.** » ; « **Aucun plancher** : les 7 traces à zéro croisement s'étalent de 0,020 % à 0,372 %, un facteur 18. Ce que la mesure attrape sur une trace sans croisement reste **inexpliqué**. »
  - §6 (« Ce que ça vaut pour le concours ») : « ⚠ En l'état ce n'est pas encore soumissionnable ».
  - §8 : « ⚠ Ce qui **reste** vrai du §5 : le seuil sélectionne une queue dont on ne sait toujours pas ce qu'elle contient sur une trace sans croisement… Le plateau justifie le *choix* du seuil, pas l'interprétation de ce qu'il attrape. »
- **preuve de lecture intégrale** :
  - l. 299 : `Une trace qui ne fait pas un tour **ne peut pas se recouvrir** : il n'existe alors`
  - l. 503 : `rouleau. C'est exactement le régime où la correction compte.`



Sept documents lus intégralement (`wc -l` mesuré avant chaque lecture).

---

### docs/08_premiere_passe_complete.md
- **lignes** : 172
- **nature** : RESULTAT
- **résumé** : Premier bout-en-bout du pipeline de détection d'encre, du téléchargement des couches rendues publiées jusqu'à une carte d'encre où des lettres grecques se lisent à l'œil, sur un segment absent du jeu d'entraînement. Il établit le portage GPU (iGPU Arc), le choix du pas de balayage, et l'AUC sur deux régions. Son §5 argumente que la précision mesurée est un plancher parce que l'étiquetage humain est partiel — argument que son propre §7, ajouté après coup, corrige et remplace.
- **conclusions extractibles** :
  - Les couches rendues sont déjà publiées sur `dl.ash2txt.org` et l'accès y est libre — ni `vc_render_tifxyz` à construire, ni volume de 2,1 Tio à streamer.
  - Une couche pèse 474 Mo, donc 65 couches feraient 31 Go ; les modèles n'en lisent que **26** (`start_idx=15`, `in_chans=26`).
  - iGPU Arc via `torch 2.9.1+xpu` : **×4,5** (104 → 23 ms/fenêtre) contre CPU seul réglé à 104 ms/fenêtre (16 fils, lot 4).
  - Le NPU n'est pas exposé à WSL2 (`/dev/accel` absent) ; OpenVINO ne convertit pas ce modèle (einsum des *rotary embeddings*).
  - Sortie GPU identique au CPU à **4,9e-6** près (bruit fp32).
  - Le GPU fonctionne sous WSL2 **sans `/dev/dri`**, par `/dev/dxg`, avec `intel-opencl-icd libze-intel-gpu1 libze1` ; le nom `intel-level-zero-gpu` n'existe pas sous Ubuntu 26.04.
  - Coût final : 4 cm² en **5,6 min**, segment entier en **3,4 h**.
  - Pas de balayage 21 contre 32 : corrélation des deux cartes **0,941**, désaccord au seuil médian **17,9 %**, désaccord sur l'encre franche (p90) **3,0 %** — le pas 21 est conservé.
  - Étiquettes en 11776×4096, couches en 11591×3882 ; multiples de 512 dont le remplissage est entièrement vide, donc alignement en (0,0) vérifié.
  - Sur `20230909121925` (segment jamais vu) : région 1024² (1,0 M pixels) AUC **0,893**, précision @0,5 **0,712**, rappel **0,751** ; région 2560×3072 (7,8 M pixels) AUC **0,919**, précision **0,553**, rappel **0,777**.
  - Sur le segment d'entraînement `20231022170901` : AUC **0,874** — le modèle fait aussi bien sur du papyrus inconnu.
  - **50 % des lignes du segment ne portent aucune étiquette**.
  - Précision selon découpage : toute la région **0,553**, lignes annotées seulement **0,585**, lignes densément annotées **0,587** ; l'AUC reste 0,919 dans tous les découpages.
  - La région commune aux images fait 2560 × 3072 px, soit 20 × 24 mm à 7,91 µm/px.
  - Sortie du modèle au **1/16** de l'entrée (4×4 par fenêtre de 64×64) puis ré-agrandie.
  - Coût : **84 secondes par cm²** (336 s / 4).
  - Sur 23 bandes, la densité prédite suit la densité étiquetée à **rho = +0,796** (p = 5,7 × 10⁻⁶) ; les bandes que l'humain laisse vides sont pour la plupart vides aussi pour le modèle (**0,35 à 1,66 %**).
- **rétractations / corrections internes** :
  - §6 : le chiffre de coût est corrigé le 2026-08-19 — « 84 secondes par cm² », pas 52 ; « les deux chiffres ne pouvaient pas être vrais en même temps ».
  - §7 (bloc entier, 2026-08-17) : deux rectifications apportées par `10_segment_complet.md`. (1) l'AUC monte à **0,925** sur 44,7 M de pixels contre 0,919 sur 7,8 M ici, avec contrôle mélangé à 0,500 exactement. (2) ⚠ « La §5 de ce document manquait sa ligne de base » — la densité d'encre passe de 3,3 % à 24,4 % quand on restreint, donc le hasard y est plus précis ; le gain **décroît** de 10,8× à 2,8×. La hausse de précision est « largement un effet de taux de base et non la preuve que les faux positifs sont des trous d'annotation ». L'argument du §5 est remplacé par le rho = +0,796 sur 23 bandes.
  - §5 s'auto-limite : « la restriction par lignes est grossière […] la zone non annotée est surtout faite de **colonnes**, pas de lignes ».
- **preuve de lecture intégrale** :
  - ligne 121 : `⚠ **Nettement plus clairsemée que la prédiction**, et c'est le fait qui a déclenché`
  - ligne 172 : `modèle** (0,35 à 1,66 %). Un détecteur qui fabriquerait de l'encre les remplirait.`

---

### docs/09_protocole_jugement_modele.md
- **lignes** : 616
- **nature** : MIXTE
- **résumé** : Le document ouvre sur un protocole (§1–5) pour faire juger un rendu d'encre par un modèle de langue sans se laisser servir du grec plausible : trois familles d'images mélangées, témoin négatif obligatoire, prompt qui rend le refus facile. À partir du §6 il devient un journal de mesures : deux juges mécaniques essayés et échoués, un calibrage réel exécuté sur 16 panneaux, le verdict sur une bande douteuse, puis le transport du juge sur Scroll 4 — où le détecteur ne sépare pas. Le §8 corrige la cause diagnostiquée au §6, et le §12 découvre une limite du protocole lui-même.
- **conclusions extractibles** :
  - Kraken 7.1 avec CLLG Polytonic Greek : sur les 65 modèles de reconnaissance disponibles, **aucun n'est entraîné sur des papyri** ; texte réel → 4 lignes segmentées, **6** caractères (`Eʹ 1 4 e`) ; papyrus sans encre → 2 lignes, 2 caractères. Inutilisable.
  - Score structurel : périodicité verticale 0,815 (texte réel) contre **0,889** (sans encre) — mauvais sens ; variation de trait 0,944 contre 0,977 ; variation de hauteur 1,151 contre **0,821** — mauvais sens. Il ne discrimine pas.
  - Diagnostic du score structurel : les interlignes trouvés valent 8 et 12 px alors qu'une lettre fait ~400 px — c'est la **grille de ré-agrandissement ×16** qui est mesurée ; sur la vérité terrain l'autocorrélation ne trouve aucun pic, la région ne contenant que 4 ou 5 lignes.
  - Sur l'image `08_verite.png`, contre l'affirmation d'un modèle d'une régularité d'interligne « exacte » : **3** bandes horizontales portant de l'encre, espacements **590 px et 1251 px** (facteur 2,1), écart-type/moyenne **0,36**, pic d'autocorrélation (200–1200 px) **0,159**.
  - Le segment entier mesure 91,7 × 30,7 mm et porte **5 lignes de texte dans la vérité terrain, 4 dans la prédiction**, d'interligne 3,6 à 7,1 mm.
  - Au seuil de décision du modèle, une région qui montre des centaines de lettres ne rend que **41 composantes connexes** — les lettres voisines fusionnent.
  - Calibrage `gemini-3.5-flash`, 8 appels, température 0, 16 panneaux : **15 sur 16, zéro fabrication** ; sur les 8 panneaux vierges, 6 refus au mot près et 2 abstentions par `·`.
  - Conditions du calibrage : `texte|vierge` 4/4 ; `vierge|texte` 3/4 (1 manqué) ; `vierge|vierge` **4/4** ; `texte|texte` 4/4 — 0 fabrication dans les quatre.
  - `LISIBILITE` : panneaux vierges 0·0·0·0·0·0·1·1 (médiane **0**), panneaux texte 3·3·4·4·4·5·5·6 (médiane **4**) — **aucun chevauchement**, max(vierge) = 1, min(texte) = 3.
  - Trois modèles éliminés par mesure : `gemini-2.5-flash`/`-pro` répondent 404, `gemini-3.1-pro-preview` et `gemini-pro-latest` 429, `gemini-3.7-flash` 503.
  - La bande 7168–8192 listée comme « vierge » mesure en fait **3,75 %** d'encre prédite.
  - La seule zone franchement vierge du segment fait ~2000 lignes, donc les trois fenêtres de témoin **se recouvrent** — ce ne sont pas trois observations indépendantes.
  - Bande douteuse 8704–9728 (7,6 à 9,8 % d'encre prédite, 0,00 % d'étiquetage) : le juge calibré donne `LISIBILITE` **1** (à gauche, 0 glyphe) et **2** (à droite, 1 glyphe), le témoin vierge refusant les deux fois — c'est le régime du vierge (0–1), pas celui du texte (3–6).
  - Coût du calibrage et du verdict : **10 appels, ~34 000 jetons**.
  - Sélecteur `--auto-bands` : la première bande candidate est **3584** (13,91 %), c'est-à-dire exactement `TEXT_BANDS[0]` choisie à la main ; bandes suivantes 9728 (12,43 %), 1024 (9,46 %), 8192 (8,17 %) ; bande vierge **6656** (1,14 %).
  - Le segment n'a de la place que pour **UNE** bande vierge, quel qu'en soit le nombre demandé (règle « pas de recouvrement, 512 lignes d'écart »).
  - Sans plafond, demander trois bandes vierges en rend trois à **1,14 %, 6,58 % et 8,17 %** d'encre prédite ; `--blank-ceiling` vaut **0,02** par défaut.
  - Scroll 4, segment `20231111135340`, région 6038 × 8000 : **107 730 fenêtres en 42,6 min**, 48,1 M pixels couverts.
  - Comparaison Scroll 1 / Scroll 4 : encre prédite globale 7,34 % / **9,71 %** ; logit médian −1,130 / **−1,385** ; logit p95 +0,826 / **+0,610** ; bande la plus pauvre (1024 lignes) 1,14 % / **4,59 %** ; bande la plus riche 13,91 % / 17,38 %.
  - Aucune fenêtre de 1024 lignes de Scroll 4 ne passe sous 2 % : la condition `vierge|vierge` n'a pas de témoin, plafond relevé à 5 % et consigné dans le fichier de résultats (`control_kind`).
  - Le juge sur Scroll 4 tombe à **1–3** de lisibilité — dans la plage du vierge et au plancher de celle du texte : **il ne sépare pas**.
  - La bande de contrôle à 4,59 % est **refusée trois fois sur trois**.
  - Le même panneau candidat, à température zéro, rend **1 glyphe, puis 2, puis 0**, et pas les mêmes glyphes (Ο une fois, Θ+Μ une autre, rien deux fois) : **la lecture d'un panneau dépend de son voisin**.
  - Test de la cause nº 1 (tranche de couches) : `--start-layer 0` donne encre prédite 10,06 % contre 9,71 %, bande candidate 18,32 % contre 17,38 %, et le juge **refuse les quatre panneaux** (lisibilité 1) ; les deux cartes se ressemblent à **rho +0,700** et **88,7 %** d'accord de classement.
  - Jeu du juge bâti le 2026-08-28 : 18 PNG de 512 px, 6 positives (`ink_segment_complet.npy`), 6 négatives (`en_travers_grand.npy`, α = +1,01), 6 inconnues (cartes `PHerc1447`) ; étirement **commun aux dix-huit tuiles** (percentiles 2 et 98 de toutes les cartes, −1,776 … 1,334) ; 18 contrôles dans `jeu_du_juge.py` ; écrire le compte par famille dans la consigne fait tomber **six** contrôles ; les tuiles se regénèrent octet pour octet identiques à graine égale.
  - `src/outils/temoins.sh` : 14 contrôles hors ligne ; un bug réel trouvé — la séparation était imposée à l'intérieur de chaque genre mais **pas entre les deux**.
- **rétractations / corrections internes** :
  - §8 (titre explicite, 2026-08-17) : « Le §6 s'était trompé de cause ». Le §6 concluait qu'aucune mesure de cohérence ne peut fonctionner sur 20 × 24 mm et qu'il faut le segment entier ; le segment entier a été passé et **n'a pas plus de lignes**. Cause corrigée : manque de LIGNES, et les glyphes fusionnent.
  - §9 : « ⚠⚠ Et mon dépouilleur accusait à tort » — un panneau vierge n'était compté correct que s'il portait la phrase de refus au mot près ; le verdict imprimé était « le modèle fabrique » sur un modèle qui s'était correctement abstenu par `·`. Corrigé.
  - §10 : « ⚠ Ma lecture initiale — “trou d'annotation” — est donc réfutée » pour la bande 8704–9728.
  - §11 : « ⚠ Et le mot “texte” devient un mensonge » sans étiquetage — le genre est renommé **candidat**.
  - §2 bis : la session qui a rendu les cartes de `PHerc1447` les a regardées, elle est donc **disqualifiée comme juge** par la règle du §2.
  - §12 : le test de la cause nº 1 « ne pouvait pas trancher » — sur **61 %** du segment le cœur de matière est hors des 65 couches (renvoi à `12` §7).
  - §12 : ajout au protocole — « toute lecture isolée à lisibilité ≤ 3 doit être **répétée en compagnie différente** avant d'être retenue ».
  - §7 : l'image envoyée à Gemini était la mauvaise (`08_verite.png`, la vérité terrain), d'où la règle de nommage `A_positif.png` / `B_negatif.png`.
  - §11 : ⚠⚠ « Les coordonnées de `TEXT_BANDS` / `BLANK_BANDS` ne se transportent PAS ».
  - Le premier témoin négatif (bruit gaussien) a été jeté comme trop facile à rejeter (§6 fin) ; `B_negatif.png` refait à partir du même segment et de la même passe (§8).
- **preuve de lecture intégrale** :
  - ligne 406 : `**1 et 2, c'est le régime du papyrus vierge** (0–1), pas celui du texte (3–6).`
  - ligne 613 : `# l'image de calibrage à deux panneaux, témoin inclus — c'est ce que le protocole exige`

---

### docs/10_segment_complet.md
- **lignes** : 197
- **nature** : RESULTAT
- **résumé** : Une passe du modèle d'encre sur le segment `20230909121925` entier, avec sa mesure contre l'étiquetage humain (AUC 0,925 sur 44,7 M de pixels et contrôle mélangé à 0,500). Le document corrige trois choses tenues pour acquises : la ligne de base manquante de `08` §5, la lecture « trou d'annotation » d'une bande douteuse, et la cause de l'échec du juge structurel diagnostiquée dans `09` §6. Il porte aussi deux défauts de sa propre mesure trouvés en la refaisant.
- **conclusions extractibles** :
  - Passe complète : **99 918 fenêtres, 38,5 min sur l'iGPU Arc, 23 ms par fenêtre**, sortie 11 591 × 3 882, **99,4 %** de pixels couverts.
  - Segment de **91,7 × 30,7 mm** à 7,91 µm/px, portant **4 à 5 lignes** de texte grec d'un interligne de 5 à 7 mm.
  - Tout le segment : 44 725 780 pixels, 3,29 % d'encre, **AUC 0,925**, précision 0,355, rappel 0,793, F1 0,491.
  - Lignes annotées : 22 331 970 pixels, 6,59 % d'encre, AUC 0,920, précision 0,488, rappel 0,793, F1 0,604.
  - Tuiles annotées (256 px) : 6 029 312 pixels, 24,41 % d'encre, AUC 0,908, précision 0,681, rappel 0,793, F1 0,732.
  - Seuil = **zéro sur le logit**, la frontière de décision du modèle lui-même.
  - Contrôle : la même chaîne sur une prédiction **mélangée** rend AUC **0,500** dans les trois domaines, exactement.
  - Un seuil par médiane rend une précision de **0,061** et a été rejeté.
  - Gain contre le hasard : tout le segment 0,355 contre 0,033 = **10,8×** ; lignes annotées 0,488 contre 0,066 = 7,4× ; tuiles annotées 0,681 contre 0,243 = 2,8× — le gain **décroît** quand on restreint.
  - Sur 23 bandes de 512 lignes, densité étiquetée contre densité prédite : **Spearman rho = +0,796, p = 5,7 × 10⁻⁶**.
  - Bandes 5632–7680 et 11264+ : étiquette 0,00–0,35 %, modèle **0,35–1,66 %** — les deux disent vierge. Bandes 2048–2560 et 8704–9728 : étiquette 0,00–0,48 %, modèle **7,6–9,8 %** — désaccord.
  - Nombre de lignes : vérité terrain **5** (interlignes 5,4 · 7,1 · 4,5 · 3,6 mm), prédiction **4** (interlignes 6,9 · 5,8 · 7,0 mm).
  - Les interlignes prédits sont plus réguliers que ceux de la vérité terrain : cv **0,08 contre 0,25**.
  - **41 composantes connexes** dans une région qui montre des centaines de lettres — au seuil de décision les lettres fusionnent.
  - L'orientation de lecture est une rotation de **270°** ; dans le repère du fichier les lignes de texte courent le long des lignes du tableau.
  - Tâche D (bande douteuse = saut de feuille ?) : **rho +0,019 à n = 89 tuiles**, contrôle plat ; à ce n la mesure détecterait un rho de 0,3 à 80 % de puissance. La proximité géométrique ne prédit pas la lisibilité.
- **rétractations / corrections internes** :
  - §2bis, titre explicite : « Correction de `08` : la restriction est en partie mécanique » — la ligne de base manquait à `08` §5.
  - §3bis : « J'ai d'abord lu les bandes 8704–9728 comme de l'annotation manquante. **Le rendu dit autre chose** » ; puis « ⭐ **Tranché depuis** (`09` §10) […] ma lecture “trou d'annotation” est réfutée ».
  - §4, titre explicite : « le juge structurel échoue une troisième fois — et `09` s'était trompé de cause » ; diagnostic corrigé : « ce n'est pas la surface qui manquait, c'est le nombre de lignes ».
  - §4, deux défauts de la mesure propre du document : (1) la normalisation par quantile « répondait à l'envers » — forcer 8 % des pixels à compter comme encre dans une bande vierge y fabrique de la structure, la bande vierge ressortant avec l'espacement le plus régulier ; corrigé en retirant le réglage. (2) l'écart minimal entre lignes était « un ordre de grandeur trop petit » (80 px quand une lettre en fait 400), d'où 8 « lignes » espacées de 1,5 mm.
  - §5 : « ⚠⚠ **PÉRIMÉ — la tâche D a été faite le 2026-08-17, et la réponse est NON.** » Le blocage annoncé (maillage `tifxyz` absent) « était une prudence mal placée, pas un fait matériel ».
- **preuve de lecture intégrale** :
  - ligne 125 : `Le diagnostic corrigé est donc : **ce n'est pas la surface qui manquait, c'est le`
  - ligne 197 : `Sortie brute conservée dans `docs/mesures/eval_segment_complet.txt`.`

---

### docs/11_onde_radiale_et_fusions.md
- **lignes** : 686
- **nature** : RESULTAT
- **résumé** : L'idée d'une onde radiale traversant toutes les couches depuis le centre est menée jusqu'à une liste de quatre sites précis à examiner sur `PHerc0172`, en passant par un dépliage polaire, quatre formulations dont trois échouées, et un balayage le long de z. Le document corrige son propre chiffre principal (11,2 m devient ~13,87 m parce que le bon estimateur est le maximum et non la moyenne), établit un invariant d'espacement inter-feuilles, puis départage la question de la persistance des sites en z. Les §§ 9 à 13, ajoutés après coup, montrent que le niveau 2 de la pyramide regarde ailleurs et que la migration est l'exception plutôt que la règle.
- **conclusions extractibles** :
  - Récupération du calcul perdu : feuilles par rayon 158 attendu / **158** obtenu, rayon extérieur 22,7 mm / **22,7 mm**, longueur 11,2 m / **11,2 m**, centre re-dérivé de zéro à **écart 0,0 voxel**.
  - `PHerc0172` : longueur axiale **164 mm**, diamètre 48 mm, papyrus déroulé ~11 à 14 m ; le rouleau occupe 163,9 des 164,7 mm scannés.
  - La longueur croît avec les spires (140 → 9,98 m ; 200 → 14,26 m) : c'est une borne **inférieure**, et un ordre de grandeur, pas une borne certifiée.
  - Profil sur 20 tranches (extraits) : z 1 336 → 176 feuilles, 25,1 mm, 13,87 m ; z 9 634 → 150 feuilles, 21,3 mm, 10,04 m ; z 12 598 → 169 feuilles, 24,3 mm, 12,92 m.
  - La passe de raffinement (6 tranches) ne trouve **aucune rupture** ; le plus grand écart entre voisins valait 11 feuilles et les valeurs intermédiaires sont 170, 164, 173, 165, 166, 153. Il n'y a pas de dégât localisé détectable par le compte le long de z, à l'échelle de 0,6 mm entre tranches.
  - Profil en U : 25,1 mm et 24,3 mm aux bouts contre 21,3 mm au centre.
  - Invariant : feuilles par rayon 150 à 176 (cv 4,2 %), rayon extérieur 21,3 à 25,1 mm (cv 4,6 %), **rayon / feuilles 138 à 148 µm (cv 1,8 %)** ; corrélation feuilles ↔ rayon **rho = +0,927** ; espacement **142,8 µm**.
  - Estimateurs de N : une seule coupe (z = 6967) 158 → 11,27 m ; moyenne sur 20 tranches 161 → 11,71 m ; **maximum sur 20 tranches 176 → 13,87 m**.
  - Dépliage polaire : coupe transformée en (rayon × angle) 3000 × 18 850 ; dérive mesurée **0,125 voxel par colonne**.
  - Quatre formulations : (1) comptage par rayon → **475 sites**, presque tous au centre ; (2) suivi de spires → **12 249 « fusions »** pour 158 feuilles ; (3) chaînage des écarts doublés → persistance 200 contre groupes plafonnés à **164** ; (4) densité de doublement par cellule → 4 candidats stables.
  - Trois hypothèses sur la fragmentation du tracker, trois réfutées : le Hongrois est **pire** (17 pistes longues contre 69), plus de sursis **améliore**, **92 %** des murs retrouvés à moins de 2 voxels.
  - Vraie cause du churn : **125 murs sur 126 appariés à chaque colonne, pour 186 pistes vivantes** — c'est l'identité qui churne.
  - Contrôle du doublement d'écart : lignes fabriquées intactes → **0 site**, avec une soudure → exactement **1**.
  - Dégénérescence du cœur : à r = 100, deux colonnes voisines échantillonnent des points distants de **0,03 voxel**, donc une trentaine de colonnes lisent le même pixel.
  - Validation de la coupe : 1,6 mm → 11 cellules (site le plus interne à 1,4 mm) ; 2,4 mm → 8 (2,4 mm) ; 3,6 mm → 5 (3,3 mm) ; **4,7 mm → 4 (17,1 mm)** ; 6,3 mm → 4 (17,1 mm).
  - Résultat : **4 cellules anormales sur 1392 (0,29 %)**, taux de fond 6,6 % ; rayons 17,1 à 18,0 mm, colonnes ~14 000 à ~16 500 sur 18 850, soit un secteur angulaire d'environ **50°** ; taux de doublement 17,1 % à 20,3 %.
  - Le fond est stable sur les 5 coupes (**6,4 · 6,5 · 6,6 · 6,9 · 7,0 %**) ; bruit d'échantillonnage sur 1400 écarts **0,66 %** ; une cellule à 20 % est à **~20 écarts-types** du fond.
  - Persistance en z : coupes espacées de 22,3 mm → **0 % (0/21)** de coïncidences contre 2,1 % au hasard, indistinguable ; coupes espacées de **0,8 mm** → **7,0 % (9/128)** contre 1,1 %, **p = 0,0001**.
  - Structure continue : z 6867 → 7167, rayon **17,1 → 19,5 mm** et angle ~14 000 → ~16 000 colonnes, soit sur 2,4 mm de hauteur **+2,4 mm de rayon et +38°**.
  - Contrôle d'inclinaison : hauteur balayée 3,16 mm, déplacement du barycentre **0,65 mm** contre 2,40 mm de migration à expliquer (facteur 3,7) ; direction du déplacement 150° contre position angulaire des sites 286°, composante radiale **−0,47 mm** — le sens est opposé, l'inclinaison est écartée et masque partiellement la migration.
  - Niveau 2 de la pyramide : conserve **89 %** des murs pour **33 Gio au lieu de 2100**, facteur **64** ; taux de fond 10,0–10,5 % contre 6,4–6,6 % au niveau 0 ; rayons des sites 5,2–22,8 mm contre 17–19 mm ; coïncidences inter-coupes **30,6 %** (hasard 4,3 %) contre 7,0 % (hasard 1,1 %). Les deux niveaux ne trouvent pas les mêmes sites — c'est un **crible**, pas un substitut.
  - Bande large (9 coupes, 6567 à 7367, espacement 0,8 mm) : **3,5 %** de coïncidences contre 1,1 % au hasard (p95 = 2,0 %) ; décomposé par distance, 0,8 mm → 108 paires, 10 coïncidences, **9,3 %** ; 1,6 mm → 92, 0, 0,0 % ; 2,4 mm → 80, 0, 0,0 % ; 3,2 à 6,3 mm → 171, 6, 3,5 %.
  - Suivi prédictif contre fenêtre fixe contre permutation : piste la plus longue **5 coupes** contre 3 contre 2,64 (p = 0,014) ; **étendue radiale 4,75 mm** contre 1,42 mm contre 0,95 mm (**p = 0,0010**, Bonferroni × 5 = **0,005**) ; pistes ≥ 4 coupes 1 contre 0 contre 0,11 (p = 0,113).
  - Chaîne du site : z6867 r 17,1 → z6967 r 17,6 → z7067 r 18,5 → z7167 r 19,9 → z7267 r 21,8. **Dérive médiane 1,50 mm de rayon par millimètre de hauteur**, 4,75 mm de rayon sur 3,16 mm de hauteur.
  - La rectitude proposée comme grandeur discriminante a échoué : **1,000 observé contre p95 nul à 1,000, p = 0,82**.
  - Balayage du rouleau entier au niveau 2 : **0 bande sur 10** significative, Fisher **p = 0,999**, étendues 0,00 à 0,47 mm. Dans la même plage de z, le niveau 0 trouve r 15,7 → 21,8 mm à 77–88 % du tour, le niveau 2 des sites à 21 %, 32 %, 53 % et 95 % et **rien entre 74 % et 88 %** — le crible regarde ailleurs.
  - `umbilicus.txt` n'existe pas : **zéro occurrence** du mot sur PHercParis4, PHerc0139, PHerc1667 et Scroll1.
  - Le centre n'est pas un barycentre : il est ajusté sur la monotonie de l'angle le long de la trace, refusée en dessous de 0,9 ; celui de PHerc0172 vaut **1,000**.
  - Sensibilité au centre (niveau 0, 6 tranches, décalage en diagonale) : décalage 0 → invariant **142,5 µm** ; 50 voxels (396 µm) → 145,0 µm, **+1,75 %** (maximum) ; 400 voxels (**3164 µm**) → 141,3 µm, −0,83 %. Déplacer le centre de 3,16 mm, soit 22 écarts inter-feuilles, déplace l'invariant de 1,75 % au maximum — **sous** le cv de 1,8 % mesuré le long de z. L'ombilic n'est pas nécessaire.
  - Six bandes au niveau 0 : C (1400–2200) étendue 0,47 mm, p 0,79 ; A (3188–3988) 0,47 mm, p 0,75 ; D (5000–5800) 1,42 mm, p 0,084 ; **E témoin positif (6600–7400) 1,90 mm, dérive 1,20 mm/mm, p 0,0285** ; B (8892–9692) 0,00 mm, p 1,00 ; **F (10500–11300) dérive 0,90 mm/mm, p < 0,05**. Fisher sur les 6 : **khi² = 19,4, p = 0,079** ; deux bandes sur six passent contre 0,3 attendue, enrichissement **6,7×**.
- **rétractations / corrections internes** :
  - §2 : « ⚠ **Et le sens de la borne avait été noté à l'envers** » — la longueur croît avec les spires, c'est une borne inférieure.
  - §3 : le chiffre principal change — « ⚠⚠ Et ça change le chiffre principal : ~14 m, pas 11,2 » ; le bon estimateur est le maximum sur z, pas la moyenne.
  - §4 : « ⚠ **Correction d'une attente** : à grande échelle les spires ne sont **pas** horizontales, ce sont de larges dômes ».
  - §5 : « ⚠⚠ **Donc les 12 249 “fusions” étaient des changements d'étiquette, pas des soudures.** Le chiffre ne mesurait rien de physique. »
  - §8 : « **Premier essai : verdict “bruit de coupe”, et le verdict était FAUX** » — les cinq coupes espacées de 22,3 mm ne pouvaient rien détecter.
  - §8 : nombre de tirages de l'hypothèse nulle corrigé le 2026-08-19 — **2 000** et non « 20 000 », « faux d'un facteur dix ».
  - §10 : compte de coïncidences corrigé le 2026-08-19 — 10 + 0 + 0 + 6 fait **16 en tout et 6 au-delà de 0,8 mm** ; le « 10 » reprenait le compte à 0,8 mm et l'attribuait à ce qui vient après.
  - §7 : « ⚠ **Ce qui n'est PAS établi** : que ce soient des soudures » ; et note ajoutée que la piste ESRF 2,4 µm est **impossible**, PHerc0172 ne publiant que du 7,91 µm.
  - §11 : « ⚠ **Ma grandeur discriminante proposée a échoué** » (la rectitude) ; c'est l'étendue qui a tranché.
  - §11 : les **18 %** de colocation du balayage du rouleau entier portent sur une **autre population de sites** que les 4 candidats du §7.
  - §12 : deux artefacts traversés — niveau 2 à 6 tranches **invalide** (42 feuilles au lieu de 176), niveau 0 à 3 tranches donnant **5,65 %** et une « marche » de 4 % qui n'existe pas (bruit d'échantillonnage).
  - §12 : « ⭐ **Le centre n'est pas un barycentre**, contrairement à ce que `06` §2.3 dit ».
  - §13 : « ⚠⚠ La lecture “le défaut d'un millimètre” du §7 tient donc **sur la majorité du rouleau**, et échoue là où un site migre » ; « ⚠ et le §7 avait tiré sa lecture d'**un** site ».
  - §1 : le code de la première mesure « avait été perdu » — lancé en ligne de commande, récupéré du transcript.
- **preuve de lecture intégrale** :
  - ligne 510 : `**Dérive médiane : 1,50 mm de rayon par millimètre de hauteur.** Le site traverse`
  - ligne 685 : `⚠ Ce script écrit un **marqueur de fin** : juger son avancement par artefact et non par PID,`

---

### docs/12_profondeur_de_surface.md
- **lignes** : 640
- **nature** : RESULTAT
- **résumé** : Né d'une enquête sur l'échec du détecteur d'encre sur Scroll 4, ce document construit un instrument qui mesure, sans vérité terrain ni modèle ni juge, à quelle distance de la surface tracée se trouve réellement la feuille. Il porte en tête un avertissement disant que l'instrument a changé deux fois et qu'il faut lire le §10 en premier ; les §1 à §9 sont conservés bien qu'en partie faux. Les §11 à §14 valident l'instrument contre un recensement indépendant sur 80 segments, le répliquent sur un second rouleau, confirment son point zéro, puis testent la prédiction chiffrée qu'il avait posée — le sens tient, le seuil tombe, la forme forte est réfutée.
- **conclusions extractibles** :
  - `vc_layers_from_ppm -r 32 -f tif` engendre **65 couches** ; la couche 32 EST la surface tracée, les autres s'en écartant d'un voxel par indice.
  - Le détecteur GP-2023 lit **26 couches**, ici les couches 15 à 40.
  - Balayage contraste, plage commune 15–40 : `20231022170901` (Scroll 1) pic dans le tiers central **63 %**, écart interquartile **4,0** couches, pic au bord 15 % ; `20230909121925` (Scroll 1) 50 %, 11,5, 37 % ; `scroll4_20231111135340` **7 %**, **22,0**, **61 %**.
  - §1bis, **corrigé le 2026-09-05** : la figure publiée ne se régénérait plus depuis les mesures de l'arbre. Elle en porte désormais la commande et **trois** panneaux — Scroll 1 pic couche **26** (**47 µm** de la trace), et **deux fenêtres du MÊME segment** de Scroll 4 dont les pics tombent aux bords **opposés** : couches **36** et **16**, soit **32** et **127 µm**. La version publiée annonçait « pic 28 / 32 µm » et un seul panneau Scroll 4. ⚠ Ce que la figure trace est l'**intensité**, pas le contraste.
  - §2, **corrigé le 2026-09-05** : la phrase « c'est le contraste qui localise » est retirée — elle contredisait le §10 de la même page depuis le 2026-08-18, et deux campagnes de `75` §C2 l'ont payée le 2026-09-05 en plaçant leur fenêtre « face » sur une spire voisine d'un volume à 2,399 µm.
  - Le chiffre de `20231022170901` passe de 76 % à **63 %** une fois la plage restreinte à 15–40 (ce segment avait été téléchargé avec 38 couches, les deux autres avec 26).
  - Scroll 4 est **bimodal** : 92 fenêtres piquant à la couche 15 et 49 à la couche 40, milieu presque vide ; l'écart interquartile passe de 4,0 à 22,0.
  - Pile complète 0–40 sur Scroll 4, 230 fenêtres : pic à la **couche 0** pour 100 fenêtres, couches 1 à 39 pour 104 fenêtres, **couche 40** pour 26.
  - Sur la pile complète 0–64 de Scroll 4 : matière et contraste maximal dès la couche 0 jusqu'à ~28, creux d'intensité aux couches 34 et 46, matière qui remonte encore de 48 à 64 ; les deux blocs sont séparés de **plus de 64 voxels** entre leurs cœurs.
  - Distance de la couche 32 au sommet de matière le plus proche : `20230909121925` (AUC 0,925) sommets aux couches 16 et 26, **6 voxels (47 µm)** ; `scroll4_…` (pile complète 0–64) **aucun sommet dans les 65 couches**, **≥ 32 voxels (253 µm)**.
  - Segment Scroll 4 entier, 232 fenêtres avec matière sur 65 couches : pic à la couche 0 pour 45 fenêtres (**19 %**), à la couche 64 pour 96 (**41 %**), donc **141 fenêtres — 61 % — ont leur cœur hors du volume de surface** ; 91 (39 %) à l'intérieur ; **3 %** dans le tiers central. Écart interquartile **61 couches**.
  - Correction du §10, défaut 1 : sur un volume à 2,4 µm la courbe moyenne de contraste est un **U** (couche 0 → 0,648 maximal ; couche 36 → 0,418 ; couche 63 → 0,254 minimal, dans la feuille ; couche 108 → 0,570 maximal) pendant que l'intensité pique franchement à la couche 36. **L'intensité est le localisateur ; le contraste ne l'est pas.**
  - Effet du passage contraste → intensité, tiers central : `20231022170901` 63 % → **96 %** ; `20230909121925` 50 % → **80 %** ; `scroll4_…` 7 % → **19 %**. La séparation passe de « 50–63 contre 7 » à « 80–96 contre 19 ».
  - Écart médian pic ↔ trace (nouvelle grandeur) : `20231022170901` **24 µm** (p90 40 µm) ; `20230909121925` **32 µm** (p90 63 µm) ; `scroll4_…` **63 µm** (p90 **134 µm**) — bornes inférieures, 37 % des fenêtres de Scroll 4 étant tronquées.
  - Volumes de surface en OME-Zarr : shape [109, 21380, 115820], chunks [109, 128, 128], dtype u1, sans compression ; **1,78 Mo et 1,03 s** par fenêtre contre 32 Go pour télécharger une pile.
  - Validation sur 80 segments de Scroll 1, 54 communs avec `windcheck` : tiers central **rho = −0,487 (p < 0,001)** ; pic d'intensité médian +0,484 (p < 0,001) ; écart médian pic ↔ trace **+0,388 (p = 0,004)** ; au bord de la pile +0,252 (p = 0,066) ; version contraste du tiers central **−0,250 (p = 0,068)**.
  - Bonferroni sur neuf grandeurs : 0,004 × 9 = **0,036**, et < 0,001 × 9 reste < 0,01. À n = 54 la mesure détecte un rho de **0,37** à 80 % de puissance.
  - Réplication sur PHerc1667 (18 segments, volumes 2,399 µm) : pic d'intensité **+0,698 (p = 0,001)** ; écart à la trace +0,478 (p = 0,045) ; au bord de la pile +0,517 (p = 0,028) ; tiers central −0,427 (p = 0,077). Les quatre grandeurs gardent leur signe sur les deux rouleaux. À n = 18 la mesure ne détecte qu'un rho de 0,62.
  - Distributions comparées : écart médian **67 µm** sur Scroll 1 contre **58 µm** sur PHerc1667 ; tiers central **38 %** contre **41 %**.
  - Confond de longueur (corrélation avec la couverture en tours) : écart à la trace +0,152 (Scroll 1) contre **−0,681** (PHerc1667) ; tiers central −0,310 contre **+0,636** ; **pic d'intensité −0,032 contre −0,167** — le pic d'intensité est quasiment libre du confond.
  - Point zéro de l'instrument : sur Scroll 1 (80 segments, 109 couches) trace supposée **54**, pic d'intensité médian observé **53** (quartiles 47–63) ; sur PHerc1667 (18 segments) 54 contre **55** (quartiles 49–61). Sur 90 segments de deux rouleaux, la matière tombe à une couche près, soit **± 2,4 µm**.
  - Test de la prédiction des 50 µm sur 80 segments : au-delà du seuil, contraste d'encre médian **4,927** ; en deçà, **5,911** ; Mann-Whitney unilatéral **p = 0,0171**.
  - Balayage de seuils : 40 µm → 72 segments, p 0,093 ; **50 → 64, p 0,017** ; 60 → 52, p 0,092 ; 70 → 32, p 0,0042 ; 80 → 16, p 0,013 ; 90 → 7, p 0,013 ; 100 → 5, p 0,0029. **60 µm est pire que 50 et que 70** — pas de point de coupure.
  - L'écart médian du corpus vaut **67,2 µm**, au-dessus du seuil proposé : il classerait **64 segments sur 80** comme dépourvus d'encre lisible alors que la plupart en portent. **8 %** des segments au-delà du seuil tombent dans le premier décile d'encre, contre **10 %** attendus si le seuil ne disait rien.
  - Sur les 80 segments l'écart médian s'étale de **24 à 120 µm**.
  - Branche « volume plus épais » fermée le 2026-08-27 : de 61 à 121 couches le pic ne bouge pas sur `PHerc0358`, l'écart médian suivant la demi-fenêtre, **262 → 562 µm** ; doubler l'épaisseur retire **40,8 %** de la réponse du modèle d'encre.
  - Le compte de croisements lui-même ne prédit pas la lisibilité (rho +0,019 à n = 89, rappel de `06` §3.8).
  - Reproduction, sans rien télécharger : `stack_structure.py docs/mesures/profil_pile_complete.json
    docs/mesures/profil_profondeur.json --out docs/mesures/structure_pile.json` rend le fichier
    à l'identique (vérifié le 2026-09-05).
- **rétractations / corrections internes** :
  - En-tête : « ⚠⚠ **L'instrument a changé deux fois. Lire le §10 en premier** — il donne la version courante et dit ce que les §1 à §9 avaient de faux. »
  - §6 : « ⚠⚠ CORRECTION — la pile complète dément mon arithmétique de ce matin » — le raisonnement importait le pas inter-feuilles de PHerc0172 (142,8 µm) vers PHerc1667 ; « C'est le piège nº 6 du dépôt — un chiffre emprunté n'est pas une mesure — et je l'ai commis. » L'égalité annoncée n'existe pas.
  - §6 : reste non tranché — dire que c'est un *saut de spire* demanderait le pas inter-feuilles de ce rouleau-là, non mesuré.
  - §7 : « ⚠⚠ Conséquence directe, et elle disqualifie le test que je venais de lancer » — si le cœur est hors des 65 couches, aucune fenêtre de 26 couches ne peut le contenir ; le test était sous-dimensionné par construction.
  - §10, défaut 1 : le pic était celui du contraste local ; corrigé en intensité, « trouvé en **affichant la courbe** au lieu de faire confiance à son argmax ».
  - §10, défaut 2 : « le tiers central » ne veut pas dire la même chose partout ; remplacé par l'écart en micromètres.
  - §10 : « ⚠ **La prédiction est REPOSÉE**, parce que changer de statistique l'invalide » — l'ancienne (« sous ~20 % de fenêtres au tiers central, pas d'encre lisible ») ne s'applique plus.
  - §11 : « ⚠ Le seuil posé d'avance n'a pas survécu » — l'écart médian du corpus est 67 µm, la majorité dépasse le seuil ; l'instrument est **ordinal**.
  - §13 : « ⚠⚠ **Corrigé le 2026-08-19 : le “72” venait d'une AUTRE campagne.** » Le 72 est le nombre de fenêtres de la campagne fibres (treillis 6 × 12) et avait migré dans une phrase parlant de segments de profondeur ; les artefacts donnent 80 entrées et 50 fenêtres pour la profondeur.
  - §14, titre explicite : « La prédiction du §10 est TESTÉE — le sens tient, le seuil non, la forme forte est réfutée ».
  - §5 point 1 (« trois segments, deux rouleaux ») marqué dépassé par les §11 et §12.
  - §9 : la branche « volume plus épais » est marquée FERMÉE ; le test `--start-layer 0` est « fait, et négatif », et « ⚠ Mais §7 explique pourquoi ce test ne pouvait pas trancher ».
  - Portée ajoutée le 2026-08-20 : l'instrument ne rend une distance que si la surface a une feuille à portée ; sur une surface en travers la valeur suit la fenêtre de rendu (α = +1,01 contre +0,00), donc le seuil de ~50 µm ne s'applique qu'aux surfaces dont la mesure converge.
- **preuve de lecture intégrale** :
  - ligne 467 : `> Le passage du contraste à l'intensité n'était pas un ajustement esthétique : il`
  - ligne 633 : `⭐ C'est la règle nº 1 du dépôt qui gagne : *aucun seuil absolu sur une grandeur physique`

---

### docs/13_batch_epuisement.md
- **lignes** : 151
- **nature** : MIXTE
- **résumé** : Registre de clôture : huit voies (A à H) listant tout ce qui restait ouvert dans la documentation et la passation, chaque item devant se fermer soit par une mesure, soit par une raison écrite. La plupart des cases renvoient à des mesures faites ailleurs, mais la voie G porte un chiffrage de passage à l'échelle qui lui est propre. La clôture du 2026-08-19 déclare les huit voies fermées et renvoie trois items de géométrie et la suite « produire » au batch suivant.
- **conclusions extractibles** :
  - **Ajouté le 2026-09-05** : la commande de `cout_passage_echelle.py`, vérifiée — elle rend le tableau du document (**1,3 / 5,2 / 77,8 Go**, **0,00421 %**) sans rien télécharger, ses valeurs par défaut étant celles du corpus publié.
  - A1/A2 : sur les 53 traces de Scroll 5, **44 sur 53 rendent ZÉRO cellule** ; la métrique de proximité est **inapplicable** — elle exige une trace qui se recouvre et 44 traces couvrent ≤ 1 tour ; les 9 mesurables sont 9 morceaux du même segment, donc n = 1.
  - A4 : aucune grandeur sans seuil n'égale la métrique à seuil (`shortfall` +0,340, `ratio_p5` −0,512 contre **+0,769**) ; le plateau tient de 0,15 à 0,40, un facteur **2,7** sans que rho bouge.
  - A5 : **71 traces mesurées** sur trois corpus — PHerc0139 (38) **+0,666** (p = 2,3e-05), PHerc1667 (20) +0,579, PHerc0814 (13) +0,141 (n = 12, sous-puissant) ; le gain est le plus grand **à 9,362 µm**.
  - B1 : un chunk Zarr = une colonne de profondeur entière pour **1,78 Mo et 1,03 s**.
  - B2 : **81 segments** de Scroll 1 avec volume de surface, **80 avec une carte d'encre publiée**, et **3 campagnes** : 45,5 / 2,4 / 1,13 µm.
  - B4 : croisements `+0,388` (p = 0,0038, n = 54).
  - C1 : tenseur de structure → orientation locale, cohérence jusqu'à **0,64**.
  - C3 : les deux instruments ne s'accordent pas — le signe s'INVERSE de n = 12 à n = 54 (**+0,330 → −0,192**).
  - G : coût de passage à l'échelle — 13 rouleaux : 1,3 Go, 6 min (1 fil), < 1 min (16 fils), **0,0042 %** du volume ; 53 rouleaux : 5,2 Go, 30 min, 4 min, 0,0042 % ; **800 rouleaux : 78 Go, 7,2 h, 0,9 h, 0,0042 %**.
  - G1 : **97 Mo, 30 s** pour un rouleau non tracé.
  - G3 : parallélisme mesuré **×8,35** (21,80 s → 2,61 s sur 16 fenêtres), sortie **bit-pour-bit identique** au sérialisé.
  - Ce qui ne passe pas à l'échelle : la détection d'encre (**42 min par segment** sur cet iGPU) et le traçage, qui reste semi-manuel.
  - H2 : un d′ **baisse** quand on résout plus de structure — valide à résolution égale seulement.
  - H3 : témoin apparié disponible — PHerc0139 en 9,362 **et** 2,399 µm.
  - H4 : **13 rouleaux mesurés** ; compression et médiane de qualité écartées, c'est la **queue** qui sépare (témoin 0 %, les treize 4–24 %).
- **rétractations / corrections internes** :
  - A5 : « ⚠ qui est le **haut** de la plage des 13 rouleaux du prix, pas leur résolution : ils sont à **8,640–9,362 µm** […] Corrigé le 2026-08-19 ».
  - B3 : « ⚠⚠ **L'instrument a été corrigé deux fois** (`12` §10) : l'intensité localise, le contraste non ; et l'écart se mesure à la trace en µm, pas en “tiers central” d'une fenêtre non centrée » ; prédiction **reposée**.
  - G : « ⚠ **La colonne “16 fils” est désormais MESURÉE** (×8,35, 2026-08-19), plus supposée. La première version divisait par 16 […] donc annonçait 0,5 h là où la mesure dit **0,9 h**. »
  - H4 : « ⚠⚠ `PHerc0358` “désigné” corrigé le 2026-08-20 » — `33` mesure 0 des 78 paires séparées et 0 des 13 distinguables du témoin après Holm, le classement n'est pas résolu ; campagne dense lancée le jour même, **les treize changent tous de rang**, `PHerc0800` devient le meilleur, le témoin passe de 0 à 4 %.
  - E1 : l'ombilic est marqué 404 à l'adresse notée, puis **CLOS SANS LUI** — le fichier n'existe sur aucun des quatre corpus.
  - E3 : « ❌ **IMPOSSIBLE, pas en attente** » — le scan fin n'existe pas sur `PHerc0172`.
  - C3/C4 : la voie fibres est marquée **réfutée**, C4 écarté parce que « la grandeur dont il dépend n'a pas survécu à la montée en puissance ».
  - F1 : `10` §5 « bloqué sur le maillage » — « ✅ corrigé — c'était une prudence mal placée, pas un fait matériel ».
  - F2 : « le suivi n'a pas été réparé, il a été **remplacé** ».
- **preuve de lecture intégrale** :
  - ligne 100 : `> On lit **quatre millièmes de pour-cent** d'un rouleau pour le juger. C'est ce que`
  - ligne 151 : `| H — qualité de scan | ✅ métrique, limite d'échelle, témoin apparié, carte des 13 |`

---

### docs/14_direction_des_fibres.md
- **lignes** : 214
- **nature** : RESULTAT
- **résumé** : Mesure de l'orientation des fibres de papyrus par tenseur de structure, sur volumes de surface à 2,4 µm, avec deux hypothèses : la bascule recto/verso en profondeur, et le désaccord d'orientation entre fenêtres voisines comme marqueur de saut de feuille. La première ne se voit pas ; la seconde donne un rho encourageant à n = 12 mais non significatif, avec une analyse de puissance qui dit qu'il faut n ≈ 70. Le §8, ajouté le 2026-08-19 avec la campagne complète sur 80 segments, **inverse le signe** et clôt la voie ; le §7 déclare l'ensemble sans objet et conserve l'archive.
- **conclusions extractibles** :
  - Le tenseur de structure : `J = [[<gx²>, <gx·gy>], [<gx·gy>, <gy²>]]`, `θ = ½·atan2(2·<gx·gy>, <gx²> − <gy²>)` ; une orientation est modulo 180°, donc tout se moyenne en angle double.
  - Résolution nécessaire (~10–20 µm pour une fibre) : 1 à 2 voxels à 7,91 µm, 4 à 8 à 2,4 µm, une quinzaine à 1,129 µm.
  - Sur `20230702185753` (2,4 µm), fenêtre la plus cohérente : couche 0 → 89,8°/0,42 ; couche 25 → 94,4°/0,62 ; **couche 35 → 93,6°/0,64** ; couche 65 → 111,8°/**0,08** ; couche 80 → 97,1°/0,32 ; couche 105 → 95,4°/0,15. **L'orientation reste à 90–97° sur les 109 couches — pas de bascule.**
  - La mesure répond au contenu : l'angle ne devient erratique (111,8°, 79,2°) que là où la cohérence s'effondre à 0,06–0,08, c'est-à-dire dans l'interstice entre deux feuilles.
  - La fenêtre lue à 2,4 µm fait 109 × 2,4 µm = **262 µm** ; à 1,129 µm elle ne fait que **123 µm**, soit moins qu'une épaisseur de feuille — elle ne peut structurellement pas traverser les deux plis.
  - Sur 11 segments listés (le document annonce n = 12) : désaccord médian entre voisins de **4,3° à 42,5°**, cohérence 0,244 à 0,330, part > 30° de 18 % à 67 %.
  - À n = 12, contre le recensement `windcheck` : désaccord médian entre voisins **+0,330 (p = 0,294)** ; cohérence médiane +0,354 (p = 0,259) ; part des voisins > 30° +0,118 (p = 0,715) ; bascule médiane en profondeur −0,189 (p = 0,557).
  - À n = 12 la mesure ne détecte qu'un **rho ≥ 0,73** à 80 % de puissance ; pour qu'un rho de 0,33 soit détectable il faut **n ≈ 70**, et le corpus en offre 80.
  - Premier segment de PHerc1667 : désaccord **38,7°**, > 30° sur 62 % des paires — haut mais dans l'intervalle de Scroll 1 (4,3–42,5°).
  - Campagne complète, 80 segments mesurés, 54 communs : désaccord médian entre voisins **+0,330 (n = 12) → −0,192 (n = 54), p = 0,165** ; part des voisins > 30° +0,118 → −0,268, p = 0,050 ; cohérence médiane +0,354 → −0,246, p = 0,073 ; bascule médiane en profondeur −0,189 → −0,064, p = 0,644. **Rien n'atteint le seuil après correction pour tests multiples.**
  - Une fenêtre de 128×128 voxels à 2,4 µm fait **307 µm de côté**.
  - Le site du Grand Prize 2027 désigne la continuité des fibres comme critère visuel : *« check if you can visually follow horizontal papyrus fibers across the page — this is an indication the segmentation is good (and not jumping between sheets) »*.
  - Reproduction : `bash src/campagnes/campagne_fibres.sh` → `docs/mesures/fibres_corpus.json`.
    Sans argument : le corpus est DÉRIVÉ de `volumes_surface_PHercParis4.txt`, une liste passée
    à la main serait une seconde réponse à « quels segments ».
- **rétractations / corrections internes** :
  - §4 : « ⚠⚠ **Le tableau ci-dessous n'a que ONZE lignes**, alors que ce titre et toutes les statistiques qui suivent disent **n = 12** […] **Une des deux valeurs est fausse et rien ici ne tranche laquelle** » — n = 12 est repris dans `13` A5, `15` §4 et `06` §3.4.
  - §4 : « ⚠ **Bug attrapé en le mesurant** » — la première version tirait des fenêtres séparées d'une vingtaine de chunks, aucune n'étant voisine d'aucune autre, et la statistique rendait `NaN` sur **0 paire comparée** au lieu de signaler qu'elle n'avait rien mesuré.
  - §7, titre explicite : « ❌ Rien ne reste — la voie est close » (2026-08-19) — la liste des suites envisagées est « sans objet », le signe s'étant inversé ; le §7 bis conserve l'archive « pour que la raison de l'abandon reste lisible ».
  - §8 : « **Le signe s'est inversé.** Le +0,330 de n = 12 était du bruit, et l'analyse de puissance le disait déjà. »
  - §5 : la bascule en profondeur ne corrèle avec rien (−0,189) — « elle ne mesure pas ce qu'elle prétendait ».
  - §8 « Ce que ça ne condamne pas » : l'orientation est mesurable et répond au contenu ; ce qui échoue est l'hypothèse que le désaccord entre voisins signale un saut de feuille, avec trois raisons possibles non départagées, dont « le compte de croisements de `windcheck` n'est peut-être pas le bon référent ».
  - §3 : la bascule recto/verso reste **non expliquée**, trois explications non départagées.
- **preuve de lecture intégrale** :
  - ligne 126 : `> ⚠⚠ **À n = 12, la mesure ne détecte qu'un rho ≥ 0,73 à 80 % de puissance.** Le +0,330`
  - ligne 213 : `**le long d'une ligne de texte**, comme un œil le fait, plutôt que la dispersion entre`



Dépôt : `/home/masterlaplace/LplVesuvius`. Les sept fichiers ont été lus du premier au
dernier caractère ; les nombres de lignes sont mesurés par `wc -l`.

---

### docs/15_soumission_progress_prize.md
- **lignes** : 273
- **nature** : PROCEDE
  (inventaire / triage de ce qui est soumissionnable au Progress Prize ; **aucun chiffre
  n'y est établi**, tous sont importés de `07`, `11`, `12`, `19`, `20`, `23`, `24`, `33`,
  `34`, `35`, `16`.)
- **résumé** : Le document trie ce que le dépôt possède contre les critères écrits sur la
  page `Prizes` du miroir, à 12 jours de l'échéance du 31 août 2026. Il classe cinq
  candidats (écart feuille↔trace, rayon corrigé par la physique, la règle d'écartement, le
  champ de correction, le paquet `tracecheck`), puis liste ce qui n'est pas soumissionnable.
  Ses §5.6 et §7 déclarent le tri lui-même périmé sur trois points datés (2026-08-19 et
  2026-08-20). Le §7.4 ajoute trois candidats neufs qui portent sur l'**outillage** de la
  communauté et non sur le papyrus.
- **conclusions extractibles** :
  - Barème du Progress Prize : **20 000 $ garantis** à la meilleure soumission du mois,
    puis 10 k / 5 k / 2,5 k / 1 k / 0,5 k selon l'importance.
  - Sur un segment publié de PHerc1667, **61 % des fenêtres ont leur pic de matière à un
    bord de la pile**, c'est-à-dire que la feuille est hors du volume de surface.
  - Validation contre `windcheck`, 54 segments communs : rho **−0,487** (p < 0,001) pour la
    part de fenêtres centrées, **+0,388** (p = 0,004) pour l'écart en µm ; Bonferroni sur
    9 grandeurs, les deux survivent.
  - La mesure coûte **1,78 Mo et 1,03 s par fenêtre**, à distance ; la même mesure par les
    couches rendues coûte **32 Go par segment**.
  - L'instrument **ne prédit pas la lisibilité** : `06` §3.8 mesure rho **+0,019** à
    n = 89 pour la métrique cousine.
  - Rayon de recherche corrigé : **+0,769 → +0,840** sur Scroll 1 et **+0,284 → +0,666**
    sur PHerc0139, en remplaçant un rayon de 749 µm par le pas inter-feuilles mesuré de
    **142,8 µm**.
  - **Les 13 rouleaux du Grand Prize 2027 sont tous à 8,640–9,362 µm**, avec interdiction
    d'utiliser un scan plus fin du même rouleau ; PHerc0139 est à 9,362 µm.
  - Règle d'écartement : écarter les **20 %** de segments dont le volume de surface porte le
    moins de matière fait monter le contraste d'encre médian du corpus de **+0,381**, contre
    **2000 permutations** de même effectif : **p = 0,0005**.
  - Le confond d'emprise est réel : emprise ↔ critère **+0,384**, emprise ↔ encre
    **+0,463** ; la corrélation **partielle** passe de −0,315 à **−0,382**.
  - Le seuil est défendu par un plateau : 15–25 % tiennent tous à p ≤ 0,001, 5 % ne fait
    rien (p = 0,054), 30 % se dégrade.
  - Champ de correction : **98 segments sur 98**, deux rouleaux, battent leur propre témoin
    de mélange ; une translation n'enlèverait que **22,1 %** de l'erreur ; **1 segment sur
    80** saute de feuille sur Scroll 1.
  - `tracecheck` : un fichier, `numpy` seul, lit **~300 chunks** (~15 s) et rend six
    grandeurs ; `selftest.py` donne **16 contrôles hors ligne** avec leurs cas négatifs.
  - Sortie citée de `tracecheck` : `material 68.5 %`, `rigid share 23.4 %`,
    `vs 173 um sheet pitch: 0.74 sheets`.
  - La direction des fibres **ne valide pas** : rho **−0,192** à n = 54, signe inversé
    depuis n = 12.
  - Généralité atteinte : **71 traces** sur PHerc0139 / PHerc1667 / PHerc0814, **80
    segments** de profondeur, **99 champs de correction** sur deux rouleaux.
  - `PHerc0358/segments/` est **vide** (vérifié).
  - Le volume publié de PHerc0358 est `[14744, 7783, 7783]` u8, chunks 128³ non compressés.
  - VC3D construit, `24` a tracé PHerc0358 : **8,48 cm² sur un rouleau du prix que personne
    n'avait touché**.
  - Prix ouverts par là : **First Letters 50 000 $ × 10 rouleaux** (10 lettres dans UNE zone
    de 4 cm², 25 juin 2027) et **titre de PHerc. Paris 4, 50 000 $** (25 juin 2027).
  - **Dix rouleaux sur treize n'ont aucun segment** (`23`).
  - Non-réplication de la règle sur 110 segments de trois autres rouleaux : Scroll 1
    n = 80, 2,4 µm, étendue 1,008, rho **+0,539** ; PHerc0139 n = 38, 2,399 µm, étendue
    1,628, rho **−0,229** ; PHerc1667 n = 19, 2,399 µm, étendue 0,720, rho **+0,425** ;
    PHerc0172 n = 53, 7,91 µm, étendue 0,220, rho **−0,217**.
  - Sur Scroll 1, `material` identifie une **classe d'échecs** : **14 segments quasi
    vierges sur 80**.
  - Candidat neuf : `vc_tifxyz_selfcross` (officiel depuis le 4 août) rend
    `clean_of_transverse_self_intersection: true` avec **`pairs_tested: 0`** dès que
    `--maxedge` a jeté tous les quads, ce qui arrive **au réglage par défaut** sur un
    maillage à pas ≥ 60.
  - Candidat neuf : `vc_grow_seg_from_seed` rend un résultat différent à chaque exécution —
    **78 tirages, 13 rouleaux, 5 rouleaux où le VERDICT bascule**, **0 reproductible** ;
    le papier du déroulage complet ne publie **aucun** taux d'erreur de traçage.
  - Candidat neuf : le même maillage, décimé sans changement de géométrie, passe de **240**
    croisements à 123, 72, 49.
  - Coût de mesure à l'échelle : ~300 requêtes par segment, **0,9 h pour 800 rouleaux**.
- **rétractations / corrections internes** :
  - §1 : ⚠⚠ « Corrigé le 2026-08-19 : les deux derniers mots manquaient » — la citation du
    critère visuel omettait *« IN CROSS-SECTION »* sous un titre annonçant « mot pour mot ».
  - §5.6 : le tri du document entier est déclaré à refaire ; trois choses l'ont périmé (la
    non-réplication de la règle de `19`, la construction de VC3D, et le 2026-08-20 le
    classement des treize rouleaux).
  - §7.1 : le candidat « solide » du §2 **a perdu sa portée** — la règle ne réplique pas ;
    et l'explication par effet de plancher est déclarée fausse (« couvrait **un corpus sur
    trois** »).
  - §7.2 : le §6 (« nos outils sont des juges », « un juge n'a rien à mesurer sur un rouleau
    non tracé ») **n'est plus vrai**.
  - §7.4 : le §7.2 est lui-même périmé sur sa dernière phrase (« `16` le dit :
    `PHerc0358` ») — `33` mesure **0 des 78 paires séparée** et la campagne dense a inversé
    le classement (rho de Spearman **−0,297**), `PHerc0800` devenant le meilleur point
    observé.
- **preuve de lecture intégrale** :
  - ligne 206 (après 60 % du fichier) : `signe opposé. **La règle est une propriété du corpus publié de Scroll 1.**`
  - ligne 273 (dans les 15 dernières lignes non vides) : `| les résultats **négatifs** avec leur puissance | — |`

---

### docs/16_carte_difficulte_rouleaux_du_prix.md
- **lignes** : 339
- **nature** : RESULTAT
  (première mesure du dépôt portant sur les rouleaux du prix eux-mêmes : écart inter-spires
  et séparabilité d′, avec témoins appariés. Comporte une recommandation actionnable, mais
  la substance est mesurée ici.)
- **résumé** : Deux cartes sur les 13 rouleaux du Grand Prize, chacune avec un témoin
  apparié (`PHercParis4` pour la géométrie, `PHerc0139` pour la séparabilité). La médiane ne
  sépare rien dans les deux cas ; c'est la **queue** qui sépare. Le tableau de géométrie a
  été refait le 2026-08-27 sur l'étendue entière (108 sondes au lieu de 64 sur la moitié
  centrale) et le corpus s'est révélé plus dur. Le document retire lui-même, à deux endroits
  datés du 2026-08-20, la conclusion qui désignait `PHerc0358` comme premier rouleau à
  attaquer.
- **conclusions extractibles** :
  - **Ajouté le 2026-09-05** : la commande de la figure, vérifiée **octet pour octet** (`figure_difficulte.py docs/carte_separabilite docs/images/16_carte_difficulte.png`, md5 `a163cd185ca73bcbf855c6bfee281f32`).
  - Séparabilité **médiane** : les quatorze rouleaux tiennent entre **1,37 et 1,62**, et
    **six des treize** font aussi bien ou mieux que le témoin.
  - Le témoin est à **0 %** de fenêtres indissociables ; les treize s'étalent de **4 %** à
    **24 %**.
  - **Trois** rouleaux du prix ont des segments publiés : PHerc1447 (16), PHerc0800 (6),
    PHerc1203 (1) — donc **dix sur treize** non tracés, dont `PHerc0358` dont le
    `segments/` est vide.
  - La période / les valeurs mesurées d'écart inter-spires : 156 / 169 / 173 / 187 / 190 /
    225 µm, soit **8,3 à 12,0 voxels** à 18,7 µm.
  - La prédiction de surface publiée est **binaire** (0 et 255, `th0.2` dans le nom du
    fichier), donc balayer le seuil ne peut rien dire.
  - Les 13 partagent la même prédiction de surface (modèle `m7`, seuil 0,2, même date
    d'entraînement), et le témoin aussi.
  - Tableau géométrie 2026-08-27 (écart médian / p10 / min / <150 µm / fenêtres) :
    PHerc1218 147/121/121/50 %/16 · PHerc0125 150/135/131/52 %/23 · PHerc1447
    156/138/121/38 %/21 · **PHercParis4 (LU) 173/134/134/14 %/28** · PHerc0211
    178/150/131/25 %/20 · PHerc0257 187/169/169/0 %/21 · PHerc0813 187/150/131/14 %/28 ·
    PHerc1203 187/150/131/21 %/33 · PHerc0800 190/156/156/0 %/26 · PHerc0191
    206/150/131/13 %/30 · PHerc0358 206/150/131/15 %/27 · PHerc1545 206/146/131/21 %/19 ·
    PHerc0268 207/173/156/0 %/38 · PHerc0826 225/139/131/21 %/19.
  - La correction du 2026-08-27 fait **perdre de la puissance** : 16 à 38 fenêtres
    exploitables par rouleau contre 27 à 62 auparavant.
  - **Dix des treize sont aussi lâches ou plus que le rouleau déjà lu** (neuf avant la
    correction du 2026-08-27).
  - `PHerc0257`, `PHerc0800` et `PHerc0268` sont les plus lâches — **0 %** de zones sous
    150 µm tous les trois, contre **14 %** pour le témoin.
  - `PHerc0125` (52 %) et `PHerc1218` (50 %) sont les deux nettement plus comprimés que le
    témoin.
  - Cause « qualité du scan » **testée puis rejetée** : partage naïf 86 % contre 29 % de
    scans fins (p = 0,0081), mais 31 des 38 du groupe négatif n'avaient jamais été tracés ;
    restreint aux rouleaux tentés, 86 % contre 71 %, **p = 0,50**.
  - `59` mesure que **31 rouleaux sur 45 n'ont aucun segment publié**, et qu'aucun des
    treize du prix ne publie de détection d'encre.
  - Énergies : 113 keV et 116 keV pour les rouleaux du prix contre **78 keV** pour le
    témoin de géométrie.
  - Témoin de séparabilité `PHerc0139` : tracé, titre retrouvé, protocole exact des 13
    (9,362 µm / 1,2 m / 113 keV).
  - Tableau d′ (médian / p10 / min / sous 1,0) : PHerc0125 1,62/0,83/0,52/24 % · PHerc0211
    1,55/1,13/0,89/5 % · PHerc1447 1,53/1,28/0,92/6 % · PHerc0358 1,53/1,15/0,88/**4 %** ·
    PHerc1218 1,52/0,95/0,92/24 % · PHerc0257 1,50/1,15/0,79/11 % · **PHerc0139 (tracé et
    lu) 1,45/1,15/1,00/0 %** · PHerc0813 1,43/0,97/0,85/15 % · PHerc1203
    1,42/0,90/0,68/19 % · PHerc0191 1,42/0,94/0,68/23 % · PHerc1545 1,40/0,96/0,78/12 % ·
    PHerc0826 1,40/0,86/0,74/13 % · PHerc0268 1,39/1,10/0,48/9 % · PHerc0800
    1,37/0,97/0,93/20 %.
  - Réserve : **15 à 35 chunks par rouleau** ; ce qui se défend est l'ordre de grandeur
    (0 contre 4–24 %), pas le zéro exact.
  - Limite valant pour les deux instruments : ils comparent des scans **à résolution
    égale**. Même rouleau, mêmes segments — 9,362 µm (28 couches) : profondeur 262 µm,
    écart 28 µm, tiers central 66 % ; 2,399 µm (109 couches) : 261 µm, 44 µm, 49 % ;
    1,129 µm (116 couches) : **131 µm**, 18 µm, 59 %.
  - La pile à 1,129 µm ne couvre que **131 µm**, donc elle tronque, et son 18 µm est une
    borne inférieure.
- **rétractations / corrections internes** :
  - §0 : ⚠⚠ « Corrigé le 2026-08-20 : la dernière proposition de ce bloc a été retirée » —
    la phrase *« et c'est ce qui désigne `PHerc0358` (4 %) comme le premier à attaquer »* est
    supprimée ; `33` trouve **0 des 78 paires** séparée et **0 des 13** distinguable du
    témoin après Holm.
  - §1 : ⚠⚠ « Corrigé le 2026-08-19 : "aucun" est FAUX » — trois rouleaux du prix ont des
    segments publiés ; l'affirmation exacte est dix sur treize.
  - §2 : ⚠⚠ « Corrigé le 2026-08-19, et les DEUX versions étaient fausses » — le §2
    annonçait « 8 à 16 » voxels et le §5 « 7 à 12 » pour la même grandeur ; le vrai est
    8,3 à 12,0.
  - §3 : le tableau du 2026-08-18 est remplacé par celui du 2026-08-27, l'ancien étant
    conservé en `<details>` parce que l'écart entre les deux est le résultat.
  - §5.2 : la limite « 27 chunks par rouleau — nombre nominal ; l'échantillonnage réel
    varie et les artefacts ne l'enregistrent pas » est corrigée le 2026-08-27.
  - §6 : ⚠⚠ « Corrigé le 2026-08-20 » — le paragraphe qui disait « C'est lui qu'on
    attaquerait en premier » ne tient pas ; l'IC exact de `PHerc0358` va de **0,1 % à
    18,3 %** et recouvre celui des douze autres. Campagne dense lancée le jour même : à
    57–115 fenêtres par rouleau, **les treize changent tous de rang** (rho de Spearman
    **−0,297**), `PHerc0358` passe du 1ᵉʳ au **6ᵉ**, `PHerc0800` devient le meilleur à
    **2,6 %**, et le témoin n'est plus à 0 % mais à **4 %**.
- **preuve de lecture intégrale** :
  - ligne 264 (après 60 % du fichier) : `**Six des treize ont une séparabilité médiane égale ou meilleure que le témoin.**`
  - ligne 339 (dans les 15 dernières lignes non vides) : `résolue** — 0 des 78 paires séparées, 0 des 13 rouleaux distingué du témoin après Holm.`

---

### docs/17_saut_de_spire_par_la_phase.md
- **lignes** : 214
- **nature** : RESULTAT
  (résultat **négatif**, établi puis rendu définitif : le titre porte déjà le verdict
  « ❌ ÉCHEC (définitif, §10) ».)
- **résumé** : Tentative de détecter un saut de spire par la marche de la phase
  d'enroulement (canal `cos` du groupe `lasagna`) entre cellules voisines d'une trace. Le
  §3 la présente comme « positive, cohérente et NON ÉTABLIE », puis le §7 constate que rho
  fond quand n monte, et le §10 (2026-08-19) ferme la dernière porte ouverte en montrant
  qu'il n'existe pas de niveau plus fin que le 3 et que la quantification n'écrase rien.
  Le document conserve son échec avec la puissance qui l'accompagne, et compare avec les
  instruments qui, eux, ont tenu.
- **conclusions extractibles** :
  - Verdict final : à n = 38, rho **+0,149** (p = 0,37) ; la trajectoire est **+0,517
    (n=8) → +0,306 (n=30) → +0,149 (n=38)**.
  - Le canal `cos` est publié en OME-Zarr, chunks 32³ à ~32 Ko compressés, pour **quatre
    rouleaux**, dont les trois qui ont des traces.
  - La période de la phase vaut **3 à 7 fois le pas inter-feuilles** (614 à 1228 µm pour un
    pas de ~170 µm) — le champ est diffusé.
  - Bug de conception corrigé : le code prenait **une cellule sur quarante** au lieu de
    comparer des voisines ; corrigé en segments contigus de **48 cellules**.
  - Symptôme du bug : la trace la plus atteinte (17 croisements) avait le p99 et le max les
    plus bas, une trace propre montait à max = 124.
  - Tableau du §3 : n=8 marche médiane +0,498 (p 0,210, détectable 0,85) · n=8 p95 +0,517
    (0,190) · n=30 marche médiane +0,301 (0,105, détectable 0,49) · n=30 p95 +0,306
    (0,100) · n=30 p99 +0,219 (0,246) · n=30 max +0,167 (0,378).
  - Établir un rho de 0,30 demanderait **n ≈ 85** ; PHerc0139 en offre 38, avec PHerc1667
    (20) et PHerc0814 (13) on monte à **71**.
  - Test croisé entre nos deux instruments, mêmes 30 segments : marche de phase (p95) ~
    écart feuille↔trace **+0,242** (p = 0,198) ; ~ tiers central **−0,256** (p = 0,172).
  - L'instrument de profondeur atteint la significativité sur PHerc0139 : rho **+0,369,
    p = 0,045** ; Scroll 1 (n = 54) tiers central **−0,487** (p < 0,001) ; PHerc1667
    (n = 18) pic d'intensité **+0,698** (p = 0,001).
  - Le volume `cos` n'est publié qu'aux niveaux **3, 4, 5** — le niveau 3 (shape
    `[9620, 3314, 3314]`, chunks `[32,32,32]`) est le plus fin qui existe ; les niveaux 0,
    1 et 2 sont absents (`.zarray` du niveau 2 absent).
  - Distribution des marches sur 38 traces : marche médiane min 6,0 / médiane **12,2** /
    max 16,0 ; p95 37,0 / 55,5 / 70,0 ; max 93,0 / 117,0 / 185,0.
  - **35 551 marches, et ZÉRO trace sur 38 dont la marche médiane soit nulle** ; 14 valeurs
    distinctes de marche médiane sur 38 traces.
  - Bilan comparatif : profondeur Scroll 1 −0,487 (<0,001), PHerc1667 +0,698 (0,001),
    PHerc0139 +0,369 (0,045) ; fibres Scroll 1 −0,192 (0,165 ❌) ; phase PHerc0139 +0,150
    (0,368 ❌).
- **rétractations / corrections internes** :
  - §2 : bug de conception dans le code, contredisant le docstring de l'auteur (une cellule
    sur quarante au lieu de cellules voisines) — corrigé.
  - §6 : la section entière est marquée « ❌ *(sans objet — le §10 a tranché)* », conservée
    « pour que le raisonnement reste lisible ».
  - §8 point 2 : la piste « refaire au niveau 0 ou 1 changerait peut-être tout » est barrée
    et marquée **RÉFUTÉE le 2026-08-19, deux fois**.
  - §10.1 : ⚠ « C'est une correction de ma propre formulation du §8, qui présentait un
    niveau imposé par l'éditeur comme un réglage de notre campagne. »
- **preuve de lecture intégrale** :
  - ligne 133 (après 60 % du fichier) : `**La marche de phase entre cellules voisines ne prédit pas les croisements recensés.**`
  - ligne 214 (dans les 15 dernières lignes non vides) : `prochaine idée qui aura besoin de la phase d'enroulement.`

---

### docs/18_batch_produire.md
- **lignes** : 140
- **nature** : PROCEDE
  (registre de batch : sept voies I à O, chacune avec ses tâches numérotées et leur état ;
  les chiffres cités renvoient à `19`, `20`, `17`, `16`, `11`.)
- **résumé** : Le batch « produire » part d'une remarque de `00` §9 — tous les instruments
  du dépôt **jugent**, aucun n'a encore **changé** quoi que ce soit — et ouvre sept voies
  pour passer du jugement à la décision, puis à la réparation. Chaque ligne porte son état
  (✅ / ❌ / ⚠) et, pour les échecs, la raison de l'abandon. La voie O, ouverte après coup le
  2026-08-19 et fermée le même jour, corrige un contrôle de robustesse faux qui avait
  affaibli à tort un résultat juste.
- **conclusions extractibles** :
  - I2 : 5 grandeurs de trace × 4 grandeurs d'encre, n = 80 — **5 couples tiennent
    Bonferroni**, `avec_matiere` en tête (**+0,539**).
  - I4 : la décision contre 2000 permutations donne **+0,381, p = 0,0005** en écartant
    20 %.
  - I5 : plateau contigu **15–25 %**, encadré par 5 % qui ne fait rien et 30 % qui se
    dégrade.
  - J2 : sans passe de repérage, **6 fenêtres utiles sur 96**.
  - J3 : campagne sur Scroll 1 — **80/80** battent leur témoin (p = 1,3e-25) ; re-mesuré le
    2026-08-26 : **79/79**, un segment ayant été retiré en amont.
  - J4 : Scroll 4 — **19/19** (p = 7,4e-08) ; le segment `20231111135340` (celui des 61 % au
    bord) n'a pas de volume de surface publié.
  - J5 : résiduel **+0,428** (p = 0,0012) contre les croisements, **−0,028** contre
    l'encre — un défaut de la TRACE, pas du RÉSULTAT.
  - J6 : une translation n'enlèverait que **21,7 %** de l'erreur (35,3 % sur Scroll 4) ;
    re-mesuré à **22,1 %** le 2026-08-26 sur 79 segments.
  - K1 : parallélisation du lecteur Zarr **×8,35 mesuré** (21,80 s → 2,61 s), sortie
    **bit-pour-bit identique** au sérialisé.
  - K3 : **0,9 h pour les 800 rouleaux**, contre 0,5 h annoncé par un modèle qui divisait
    par 16.
  - K4 : **dix** des 13 rouleaux du prix n'ont aucune trace (PHerc1447 en a 16, PHerc0800
    6, PHerc1203 1).
  - L1 : rejouer une trace au niveau 1 est **impossible** — le volume `cos` n'est publié
    qu'aux niveaux 3, 4, 5.
  - L3 : marche médiane **12,2 / 255**, **0 trace sur 38** à médiane nulle.
  - M1 : déplacer le centre de **3,16 mm** (22 écarts inter-feuilles) bouge l'invariant de
    **1,75 %**, soit sous le cv de 1,8 % ; deux artefacts traversés avant produisaient
    5,65 % et une « marche » qui n'existe pas.
  - M2 : **6 bandes** au niveau 0 — la migration est l'exception, **2 sur 6**, Fisher
    p = 0,079 ; le témoin positif (bande E) ressort.
  - M3 : les 4 sites de fusion sont sur **PHerc0172**, qui ne publie que du **7,91 µm**
    (deux volumes, vérifié sur le bucket) — le scan plus fin n'existe pas pour ce rouleau.
  - N4 : `src/outils/temoins.sh` — **13 contrôles de plus, 79 au total**.
  - O1 : le contrôle comparait `zarr_depth` à `champ_correction`, dont le `avec_matiere`
    mélange repérage et blocs posés sur la matière ; rho **+0,280**.
  - O4 : même définition, 72 contre 392 points — **rho +0,841** (témoin 0,223).
  - O5 : le plateau 15–25 % survit à un quintuplement de la densité (p = 0,0010 / 0,0005 /
    0,0030).
- **rétractations / corrections internes** :
  - Voie O, O1 : le contrôle de robustesse est déclaré ⚠ **faux** — il comparait deux
    grandeurs différentes, et l'auteur « en a conclu à tort à une instabilité ».
  - Voie O, O2 : « **conclusion invalidée par O1** : la dégradation venait d'une grandeur
    différente, pas d'une grille différente ».
  - Voie O, O4 : « **la question était mal posée** ».
  - Voie J, J3/J6 : les chiffres publiés (80/80, 21,7 %) sont re-mesurés le 2026-08-26 en
    79/79 et 22,1 % à cause d'un segment retiré en amont et de trois volumes changés.
  - Voie D de `13` : explicitement **remplacée** par la voie J.
  - Voie N1 : « `00` §9.5 périmé | ✅ corrigé — et c'était **le rayon, pas la
    résolution** ».
- **preuve de lecture intégrale** :
  - ligne 100 (après 60 % du fichier) : `| L3 | l'échec est **définitif** | ✅ `17` §10, et mesuré : marche médiane **12,2 / 255**, **0 trace sur 38** à médiane nulle. La quantification n'écrase rien |`
  - ligne 138 (dans les 15 dernières lignes non vides) : `> exactement ce qui l'a rendu difficile à voir. **La prudence n'est pas une méthode.**`

---

### docs/19_ecarter_avant_de_payer.md
- **lignes** : 461
- **nature** : RESULTAT
  (établit la règle d'écartement sur Scroll 1, son témoin de permutation, sa correction de
  confond — puis, dans ses §§9 à 12, la corrige, la re-valide, et **restreint sa portée à un
  seul corpus**.)
- **résumé** : Le document pose la première règle du dépôt qui **change une décision** :
  écarter les 20 % de segments les plus pauvres en matière fait monter le contraste d'encre
  médian de +0,381 contre 2000 permutations (p = 0,0005). Le §9, ajouté quelques heures plus
  tard, affaiblit ce résultat en dénonçant une dépendance à la grille de sondage ; le §10,
  quelques heures encore plus tard, déclare le §9 **faux** (il comparait deux grandeurs
  différentes) et rétablit le §5. Le §11 puis le §12 réduisent ensuite la portée : la règle
  détecte une **classe** et non un gradient, et elle **ne réplique pas** sur trois autres
  corpus.
- **conclusions extractibles** :
  - La règle : écarter les **20 %** de segments dont le volume de surface contient le moins
    de matière fait monter le contraste d'encre médian du corpus de **+0,381**, contre
    p = 0,0005 sur 2000 permutations.
  - Elle coûte **36 requêtes HTTP par segment** et se calcule avant toute inférence.
  - À n = 80, la mesure détecte un rho de **0,31** à 80 % de puissance ; seuil de
    Bonferroni sur 20 croisements : p < 0,0025.
  - Corrélations : `avec_matiere` × `encre_contraste_p90_p50` **+0,539** (p 0,00000 ✅) ·
    × `encre_ecart_type` +0,534 ✅ · × `encre_moyenne` +0,487 ✅ · ×
    `encre_contraste_p99_p50` +0,398 (0,00026 ✅) · `ecart_a_la_trace` ×
    `encre_contraste_p99_p50` **−0,344** (0,00176 ✅) · `ecart_a_la_trace` ×
    `encre_contraste_p90_p50` −0,315 (0,0044 ❌ nominal seulement) · `au_bord` ×
    `encre_contraste_p99_p50` −0,298 (0,0073 ❌) · `tiers_central`, `iqr` ≤ 0,15 (≥ 0,19 ❌).
  - Confond de taille : emprise → `ecart_a_la_trace` **+0,384** (0,0004) · emprise → encre
    moyenne **+0,463** · emprise → `encre_contraste_p90_p50` +0,101 (0,373) · emprise →
    `avec_matiere` +0,189 (0,093).
  - Corrélations partielles (emprise retirée en rangs) : `ecart_a_la_trace` × p90_p50
    −0,315 → **−0,382** (p = 0,0005) ; × p99_p50 −0,344 → −0,273 (p = 0,014) ;
    `avec_matiere` × p90_p50 +0,539 → **+0,561** (p < 1e-6).
  - Table de la décision (écartés / gardés / avant / après / gain / témoin p95 / p) :
    5 %/76/5,061/5,178/+0,117/5,178/0,054 · 10 %/72/5,308/+0,247/5,178/0,0075 ·
    15 %/68/5,361/+0,300/5,260/**0,0010** · 20 %/64/5,442/**+0,381**/5,260/**0,0005** ·
    25 %/60/5,442/+0,381/5,308/**0,0005** · 30 %/56/5,361/+0,300/5,333/0,0255 ·
    40 %/48/5,480/+0,419/5,361/0,0015 · 50 %/40/5,456/+0,395/5,402/0,0250.
    Huit fractions testées, seuil retenu 0,05 / 8 = **0,0063**.
  - Critères perdants : avec `ecart_a_la_trace`, le gain croît de façon monotone
    (+0,199 → +0,500) sans plateau ; avec `tiers_central`, la règle s'effondre au-delà de
    25 % (p = 0,10 puis 0,14).
  - §9 : `zarr_depth.py` treillis 6 × 12, **72 points**, part de matière médiane 48,0 % ;
    `champ_correction.py` repérage 10 × 20, 200 points, 32,4 % ; accord des classements
    rho = **+0,280** (p = 0,012) contre témoin |rho| p95 = 0,219.
  - §10 : même outil, même définition, 72 contre **392 points** — médiane 48,0 % → 73,3 %,
    accord des classements **rho +0,841** (p = 1,7e-22), témoin |rho| p95 = 0,223.
  - §10 : rejouée sur la mesure dense, la table de p est identique à celle du §5 sauf 25 %
    (0,0005 → 0,0030) et 50 % (0,0250 → 0,0010) — le plateau 15–25 % survit intact.
  - §11 : Scroll 5 (PHerc0172, 53 segments, 7,91 µm) — `avec_matiere` × contraste d'encre
    **−0,217** (p = 0,118), décision à 20 % **−0,020** (p = 0,84), **0/20** corrélations
    passant Bonferroni contre 5/20 sur Scroll 1.
  - §11.1 : contraste d'encre p10 → p90 — Scroll 1 : 1,25 → 6,36 (facteur **5,1**), étendue
    relative **1,008** ; Scroll 5 : 2,20 → 2,76 (facteur **1,25**), étendue relative
    **0,220**. À n = 53 la mesure détecterait un rho de 0,37.
  - §11.2 : sur Scroll 1, **14 segments sur 80** ont un contraste sous 2,5 ; en les
    retirant : 66 au-dessus de 2,5 → rho +0,249 (p = 0,044) ; 64 au-dessus de 3,0 →
    **+0,190 (p = 0,132)** ; 58 au-dessus de 4,0 → +0,157 (p = 0,239).
  - §12 : test apparié à résolution égale — Scroll 1 n=80, 2,4 µm, étendue 1,008,
    **+0,539** (détectable 0,31) · PHerc0139 n=38, **2,399 µm**, étendue **1,628**,
    **−0,229** (p = 0,17, détectable 0,44) · PHerc1667 n=19, 2,399 µm, étendue 0,720,
    **+0,425** (p = 0,070, détectable 0,60) · PHerc0172 n=53, 7,91 µm, étendue 0,220,
    **−0,217** (p = 0,12, détectable 0,37).
  - §12 : **17 des 38 segments** de PHerc0139 sont sous un contraste de 2,5 et le corpus
    rend quand même le signe opposé.
  - Motif d'ensemble identique à celui des fibres (+0,330 à n = 12, **−0,192** à n = 54) et
    du détecteur de phase.
  - La règle est déclarée **une propriété du corpus publié de Scroll 1, pas du problème** ;
    testée sur **110 segments** de plus.
  - Coût cité au §12 : la mesure coûte **300 requêtes** et se calcule avant l'inférence.
- **rétractations / corrections internes** :
  - Titre : « ✅ *(§9 corrigé au §10)* ».
  - §5 : encadré ⚠⚠ « **ce paragraphe ne tient plus tel quel — voir le §9** » (interprétation
    trop large, le tableau reste exact).
  - §9 : conclut que le plateau 15–25 % est une propriété de la grille A et non du
    phénomène — puis est lui-même invalidé.
  - §10 : ⚠⚠ « **Le §9 était FAUX — je comparais deux grandeurs différentes** ». Les deux
    affirmations du §9 (critère « modérément reproductible » à +0,280 ; plateau = artefact
    de grille) sont déclarées fausses. Ce qui est gardé du §9 : qu'il fallait tester la
    dépendance à la grille, et que la mesure de `champ_correction` n'est pas comparable
    telle quelle ; ce qui est retiré : l'instabilité du critère et l'artefact de grille.
  - §7 : ⚠ trois nombres circulent pour des grandeurs voisines — **36**, **50**, **72** — et
    le document ne le dit nulle part ; marqué ✅ à démêler.
  - §12 : ⚠⚠ « **Le test apparié RÉFUTE l'explication du §11** » — l'effet de plancher
    « couvrait un corpus sur trois et je l'avais écrite comme si elle les couvrait tous ».
- **preuve de lecture intégrale** :
  - ligne 289 (après 60 % du fichier) : `« modérément » reproductible, c'est très reproductible.`
  - ligne 461 (dans les 15 dernières lignes non vides) : `découvrir après.`

---

### docs/20_le_champ_de_correction.md
- **lignes** : 656
- **nature** : RESULTAT
  (mesure du champ d'erreur fenêtre par fenêtre sur trois rouleaux, puis application réelle
  d'une correction avec son témoin de signe opposé et son ré-aplatissement.)
- **résumé** : Le document sépare deux défauts qu'une médiane confond — une pose ratée
  (réparable par translation) et un saut de feuille — en mesurant l'écart fenêtre par
  fenêtre sur des blocs contigus. Il établit que l'erreur d'une trace est **structurée**
  (98 segments sur 98 battent leur témoin de mélange), qu'une **translation est le mauvais
  remède** (22,1 % de l'erreur sur Scroll 1), et que le champ prédit un défaut de la trace
  (+0,428 contre les croisements) mais **pas** son résultat (−0,028 contre l'encre). Les
  §§8 et 9, plus tardifs, livrent l'export par fenêtre, corrigent une règle « au bord »
  écrite deux fois, puis appliquent réellement la correction : le pic médian atterrit sur la
  couche tracée et l'écart tombe d'un facteur 7 — avec une distorsion qui n'est levée qu'en
  ré-aplatissant, ce qui coûte 2 % de surface.
- **conclusions extractibles** :
  - Échantillonnage : la grille entière ferait 167 × 905 chunks, soit **4228 requêtes** par
    segment ; sans passe de repérage, **6 fenêtres utiles sur 96**.
  - Cohérence des voisins : Scroll 1 (PHercParis4, 2,4 µm, 79 segments) médiane **+0,325**,
    témoin −0,008, **79/79** (p = 3,6e-25) · Scroll 4 (PHerc1667, 2,399 µm, 19) **+0,481**,
    témoin −0,035, **19/19** (p = 7,4e-08) · Scroll 5 (PHerc0172, 7,91 µm, 53) **+0,183**,
    témoin −0,030, **50/53** (p = 1,3e-14).
  - Cas le plus net : `20260623163339-w110-112`, cohérence **+0,694** (témoin −0,074), le
    maximum sur 80. Cas médian : `20230702185753`, cohérence **+0,310**.
  - Part de l'erreur qu'une translation enlèverait : Scroll 1 **22,1 %** (p90 47,8 %),
    Scroll 4 **35,3 %** (p90 62,8 %), Scroll 5 **28,6 %** (p90 45,8 %).
  - Forme brute et sans normalisation : sur Scroll 1 le décalage médian vaut **14,4 µm** et
    le résiduel **56,4 µm** — quatre fois plus petit que ce qu'une translation laisserait.
  - Un segment de Scroll 5 rendait `rigid_share` = **0,67** ; les 53 segments mettent la
    médiane à 28,6 % — c'était une exception. Conclusion étendue à **trois rouleaux, deux
    résolutions et 152 segments**.
  - Saut de feuille : Scroll 1 (pas 172,8 µm) résiduel médian 56,4 µm = **0,33** écart,
    **1/79 (1 %)** au-dessus d'un écart (`20260701183146-w118-119`, à 1,02 écart) ; Scroll 5
    (pas 142,8 µm) résiduel 39,6 µm = **0,28**, **0/53 (0 %)**.
  - Le champ **ne prédit pas** le résultat : contre les cartes d'encre à n = 79 (rho 0,311
    détectable) — `coherence_voisins` −0,025 (0,83), `residuel_median_um` −0,013 (0,91),
    `|decalage_median_um|` −0,065 (0,57), `part_au_bord` **−0,242** (0,032).
  - Test apparié sur les 39 segments les plus décalés : **4,882 contre 4,865, p = 0,22**.
  - Contre les croisements `windcheck` (n = 54) : `residuel_median_um` **+0,428**
    (p = 0,0012), `coherence_voisins` +0,270 (p = 0,048) ; à n = 54 rho 0,37 est détectable,
    Bonferroni p < 0,025 — seul le résiduel tient.
  - Le résiduel contre les croisements **+0,428** (0,0012) et contre l'encre **−0,028**
    (0,80) : un défaut de la TRACE, pas du RÉSULTAT.
  - Position dans le rouleau, non établie : Scroll 1 (n = 57) `residuel_p90_um` +0,283
    (0,033) et `residuel_median_um` +0,214 (0,110) ; Scroll 4 (n = 19)
    `residuel_median_um` +0,487 (0,035) et `residuel_p90_um` +0,127 (0,61). Détectable :
    0,36 à n = 57, 0,60 à n = 19.
  - Règle « au bord » : les piles réelles du dépôt sont **impaires** (33 et 109) ; sur
    `PHercParis4/20230702185753`, pile de 109, la fenêtre fautive a son pic à la couche
    **107**, la dernière étant la 108.
  - Reclassement de la correction : Scroll 1 (pile 109) 75 / 7 499 fenêtres sur 48 / 79
    segments, taux **1,00 %** (uniforme 0,92 %) · Scroll 4 (109) 17 / 1 741 sur 8 / 19,
    **0,98 %** (0,92 %) · Scroll 5 (33) 108 / 4 987 sur 45 / 53, **2,17 %** (uniforme
    **3,03 %**).
  - Saturation par rouleau : Scroll 4 est le plus saturé (**15,4 %** contre 8,4 et 11,4) et
    tombe exactement sur le taux uniforme.
  - Encadrement dû à la censure : Scroll 1 — 7 499 fenêtres, 630 saturées, part applicable
    0,927 / 0,737, encadrement 3,6 / **30,0 µm** · Scroll 4 — 1 741, **268**, 0,860 /
    **0,615**, 9,6 / **82,8 µm** · Scroll 5 — 4 987, 569, 0,890 / 0,771, **0,0** / 7,9 µm.
  - Seuils du dépôt : `carte_segments.py` publie **40 µm** (même feuille, raccordable) et
    **250 µm** (feuilles voisines) ; l'encadrement de Scroll 4 (82,8 µm) est **le double**
    du seuil.
  - Segment `20260701183128-w053-058` (le plus réparable des 79 : cohérence +0,405,
    résiduel 44,4 µm, 6 % au bord) — médianes par bloc en couches : −34, +26, +17, +15,
    +25, −18 ; segment (90 fenêtres) **+19**, étendue **101**, écart-type 30,4.
  - Étendue de 101 couches = **242 µm** = 1,4 fois le pas inter-feuilles (172,8 µm) ;
    retirer la médiane du segment enlève **+19 couches = 46 µm**.
  - La censure peut inverser un signe : la médiane du bloc 5 vaut **+22** avec les fenêtres
    saturées et **−18** sans.
  - Correction appliquée (bloc 1, 128 × 128 cellules, 61 couches = 146 µm, recadrage
    2560×2560 from (0,0)) : base — pic couche 6, écart **58 µm**, tiers central 31 %, au
    bord 12 % · **+26 voxels** — pic couche 30, écart **8 µm**, 56 %, 25 % · témoin −26 —
    pic couche 15, 41 µm, **0 %**, 25 %.
  - Ce qui ne s'améliore pas : le p90 passe de 68 à 72 µm, la part au bord de 12 à 25 %.
  - La distorsion n'est pas un repli (`vc_tifxyz_selfcross` rend **zéro** auto-intersection
    transversale sur les trois maillages) ni un bruit de normales (cohérence de l'étirement
    **+0,764** contre témoin **+0,000**) : c'est la **courbure**, aire d'une maille décalée
    de `d` = `(1 − 2Hd + Kd²)` fois la sienne.
  - Aires selon le déplacement : ±5 voxels — médiane ≈ 1,000, p01 0,952, p99 1,048, totale
    0,999 / 1,001 · **±26** — ≈ 1,000, **0,765**, **1,255**, 0,996 / 1,004 · ±60 — ≈ 0,997,
    **0,476**, **1,608**, 0,990 / 1,010. Effet **linéaire en `d`**.
  - Ré-aplatissement : étendue relative des aires — base **0,095**, +26 voxels **0,479**,
    +26 puis ré-aplati **0,085** ; anisotropie 1,072 → **1,001**.
  - Profondeur après ré-aplatissement : base 31 % / 12 % / 58 µm · +26 56 % / 25 % / 8 µm ·
    **+26 ré-aplati 60 % / 15 % / 8 µm** · témoin −26 0 % / 25 % / 41 µm.
  - Coût du ré-aplatissement : trous du quadrillage 0 / 0 / **1 087**, valide en moitié
    basse 100 % / 100 % / **92,6 %**, aire conservée 100,0 % / 99,6 % / **98,0 %** ; part de
    pixels noirs du cinquième inférieur **7,3 % → 14,5 %**.
  - Les quatre pavés ne sont pas au même endroit : ré-aplatir re-rastérise (recadrage
    **2721×2541** contre 2560×2560).
  - Le maillage publié du segment fait **3 660 × 9 244** points ; à l'échelle 1 son rendu
    ferait ~73 000 × 185 000 pixels.
  - La trace de PHerc0358 ne peut pas servir de sujet : distribution de pics **bimodale**
    (11 fenêtres à la couche 0, 5 à la couche 20, **16 %** seulement dans le tiers central).
  - À 9,362 µm, 61 couches valent 3 pas inter-feuilles et 121 en valent 6 ; passer de 61 à
    121 couches laisse le pic au bord et fait passer l'écart médian de **262 à 562 µm**.
  - Règle : une fenêtre de profondeur doit rester **sous le pas inter-feuilles** ; les
    volumes publiés de Scroll 1 la respectent (109 × 2,4 = 262 µm pour un pas de 172,8, soit
    ±0,75 pas).
  - Reproduction des deux figures : `figure_champ.py <clé du volume de surface>
    <sortie> --voxel-um 2.4 --pas-um 172.8 --cote 7`, sur
    `20260623163339-w110-112` et `20230702185753`. Vérifié le 2026-09-05, **octet
    pour octet** (`c43b6dab92d1afcc8f49e6fb57944bd0`, `684c7a4c13b9a882e0e9fb189c7b3123`).
    ⚠ `--pas-um` borne l'échelle de couleur : le changer sans le dire ferait lire deux
    figures comme comparables alors qu'elles ne le seraient plus.
- **rétractations / corrections internes** :
  - §4 (fin) : ⚠⚠ alerte posée puis **levée par la mesure le même jour** — le
    `rigid_share` = 0,67 sur un segment de Scroll 5 avait fait restreindre la conclusion à
    deux rouleaux ; les 53 segments lèvent la restriction.
  - §5 : ⚠⚠ « **Correction d'une mesure faite deux heures plus tôt dans cette même
    session** » — le pas de 142,8 µm (mesuré sur PHerc0172) avait été appliqué à des
    segments de PHercParis4, gonflant le compte de sauts d'un facteur **4** (4 segments
    signalés au lieu de 1). Remède : `--pas-um` n'a plus de défaut.
  - §6 : le tableau a bougé — la version publiée disait **−0,275** à n = 80 et le test
    apparié 4,758 / p = 0,12 ; trois causes distinctes (un segment retiré en amont, **trois
    volumes de surface changés en amont**, la règle « au bord » corrigée) et l'auteur
    **refuse de décomposer** le déplacement entre elles.
  - §6 : ⚠ note interne « (`07` §7 — ce document n'a pas de §16) », correction d'une
    référence.
  - §8 : ⚠⚠ « deux réponses à "le pic est-il au bord" » — `zarr_depth.py` et
    `champ_correction.py` avaient chacun leur règle ; la seconde se trompe d'une couche pour
    une pile impaire. La règle est désormais écrite une seule fois.
  - §8 : ⚠ « la vérification passait pour la seule raison qui la rendait incapable
    d'échouer » — toutes les fixtures avaient une profondeur paire.
  - §8 : ❌ prédiction écrite avant mesure (3,03 % pour une pile de 33) — **elle échoue** :
    2,17 % contre 3,03 %, soit 28 % en dessous. Et le mécanisme supposé (la censure dépeuple
    la couche voisine) est éliminé par Scroll 4.
  - §8 : « **Correction d'une affirmation que ce document portait depuis deux commits** » —
    « la censure ne déplace aucune décision de raccordement » est vrai de Scroll 1 et
    **faux de Scroll 4** (61,5 % de fenêtres applicables sur le pire segment).
  - §9 : le §4 écrivait que corriger était hors de portée « parce que la chaîne maillage →
    rendu n'est pas ici » ; elle y est depuis le 2026-08-19.
  - §9 : ⚠⚠⚠ « le ré-aplatissement COÛTE de la surface, et aucune de ces mesures ne le
    voyait » — les statistiques d'étirement ne portent que sur les mailles valides des deux
    côtés, donc elles pouvaient s'améliorer pendant que la surface se perdait ; le verdict
    « strictement meilleur » d'abord écrit devient **un verdict à trois faces**. Défaut
    signalé par un lecteur regardant l'image, contre tous les chiffres.
- **preuve de lecture intégrale** :
  - ligne 411 (après 60 % du fichier) : `feuille » — mais sur **Scroll 4 il vaut 82,8 µm, soit le double du seuil**.`
  - ligne 656 (dans les 15 dernières lignes non vides) : `n'est pas rendu — refuser une réponse vaut mieux qu'en rendre une fausse.`

---

### docs/21_texte_de_soumission.md
- **lignes** : 512
- **nature** : PROCEDE
  (brouillon du texte de soumission — catégorie explicitement rangée en PROCEDE. ⚠ Réserve :
  ses §§10bis, 11, 12 et 13, ajoutés après coup les 2026-08-20/21/22, sont rédigés comme des
  résultats et portent des mesures (α, tirages, extension) dont ce document est ici la
  formulation citée ; il les impute à `30`, `35`, `38`, `43`, `44`.)
- **résumé** : Brouillon en anglais visant le Progress Prize d'août 2026, encadré en
  français par des notes de méthode et des corrections datées. Le corps expose les trois
  mesures de `tracecheck`, la règle d'écartement **avec sa non-réplication**, les résultats
  négatifs, le choix de graine mesuré, la reproductibilité du traceur officiel, le test de
  convergence α, le mode `gen_neighbor` et l'extension latérale d'un segment publié. Le §10
  originel est déclaré **périmé et à remplacer** (et non à nuancer) par le §10 bis. Le
  document se termine par une liste de quatre choses à faire avant l'envoi, dont la décision
  de forme restée ouverte.
- **conclusions extractibles** :
  - Un chunk d'un volume de surface OME-Zarr `[depth, 128, 128]` est **toute la colonne de
    profondeur** d'une fenêtre 128×128 ; accélération mesurée à 16 fils **×8.35**, sortie
    byte-identique.
  - Un segment entier se juge à partir de **~300 range reads**, quelques mégaoctets, ~15 s ;
    juger les **~800 rouleaux** lirait **0.004 %** de leur volume en **0.9 heures**.
  - `material` : rho **+0.539** contre 80 cartes d'encre publiées de Scroll 1 (p < 1e-6 ;
    **+0.561** en retirant l'aire) ; **+0.190, ns** une fois les segments quasi vierges
    retirés ; **ne réplique pas** sur trois autres rouleaux.
  - `edge_pinned` : rho **−0.275** (p = 0.014). `offset` : rho **+0.388** contre les
    auto-croisements publiés (n = 54, p = 0.004). `residual` : rho **+0.428** (p = 0.0012).
    `rigid_share` : **22.1 %** médian sur 79 segments. `coherence` : **148/151** segments
    sur trois rouleaux battent leur témoin de mélange (79/79, 19/19, 50/53).
  - Sur un segment publié de PHerc1667, **61 % des fenêtres** ont leur pic de matière
    épinglé à un bord de pile — la feuille est hors du volume de surface de **65 couches**
    que lit le modèle d'encre.
  - Règle : sur Scroll 1, `material` identifie une classe dont la carte d'encre est quasi
    plate — **14 sur 80** ; écarter les 20 % les plus pauvres monte le contraste médian de
    **+0.381** contre 2000 tirages (**p = 0.0005**).
  - Retirer les **16** segments sous un contraste de 3.0 fait tomber la corrélation de
    **+0.539 à +0.190 (p = 0.13, non significatif)**.
  - Non-réplication sur 110 segments : Scroll 1 n=80, 2.4 µm, étendue 1.008, **+0.539**
    (détectable 0.31) · PHerc0139 n=38, 2.399 µm, étendue **1.628**, **−0.229** (0.44) ·
    PHerc1667 n=19, 2.399 µm, 0.720, +0.425 (0.60) · PHerc0172 n=53, 7.91 µm, 0.220,
    −0.217 (0.37).
  - Sauts de feuille : sur 80 segments publiés de Scroll 1, **1** dépasse un écart
    inter-feuilles, et il est nommé.
  - Réparation : sur Scroll 1, décalage médian **14.4 µm** contre résiduel médian
    **56.4 µm** ; parts : **22.1 %** (Scroll 1, 79), **35.3 %** (Scroll 4, 19), **28.6 %**
    (Scroll 5, 53).
  - **Quatre** résultats négatifs rapportés : orientation des fibres (+0.330 à n = 12 →
    **−0.192** à n = 54) ; marches de phase (+0.517 à n = 8, +0.306 à n = 30, **+0.150** à
    n = 38 ; niveau `cos` le plus fin = 3 ; marche médiane 12.2 / 255, zéro trace sur 38 à
    zéro) ; mesures de profondeur comme prédicteurs de lisibilité (rho **−0.028** à n = 80,
    0.31 détectable) ; seuil en µm séparant « lisible » de « non » (direction tenue —
    4.93 contre 5.91, p = 0.017 — mais 60 µm score plus mal que 50 et 70 ; l'écart médian du
    corpus est **67 µm**, donc le seuil condamnerait **64 des 80** segments portant
    visiblement de l'encre, et **8 %** de ceux au-dessus tombent dans le décile d'encre le
    plus bas contre 10 % attendus par hasard).
  - Choix de graine : le critère « le plus de surface prédite » rend **huit candidats tous
    à 255** sur PHerc0358 ; ce qui est classé à la place est le tenseur de structure 3D
    `(lam1 - lam2) / lam1`, moyenné sur le voisinage 3×3×3 (~13 800 blocs par chunk). Biais
    d'orientation balayé 0–90° : planarité brute 0.828–1.000, floutée 0.947–1.000.
  - Campagne appariée sur 13 rouleaux du prix (dix sans segment publié) : planarité contre
    voisinage — aire, test des signes **11 – 2, p = 0.0225** ; auto-intersections **0 vs 0**.
  - Le résultat d'auto-intersections **ne réplique pas** : sur PHerc0358 le changement de
    graine passe de **240** à 0 ; sur les douze autres les deux critères rendent zéro. Sur
    PHerc0125 et PHerc0826 la graine de voisinage cale à **0.85 cm²** là où la planarité
    atteint 19.82 et 13.14.
  - Le correctif qui a compté sur PHerc0358 n'était pas le critère mais le plafond
    d'occupation : le mauvais bloc a **occupancy 1.000**, donc un tenseur de structure nul.
  - Amplitude du profil de profondeur, fenêtre appariée de 1.2 mm : Scroll 1
    `20230909121925` (AUC 0.925) **50.1 %** · segment officiel PHerc1447 **28.8 %** ·
    Scroll 4 `20231111135340` (échec connu) **19.3 %** · notre meilleure trace PHerc0358
    **8.7 %**.
  - Le critère « le pic de matière est-il dans le tiers central » **ne transporte pas** : le
    segment officiel PHerc1447 y échoue (**2 %**) plus mal que les deux nôtres (16 % et
    20 %) ; il a été retiré.
  - §10 bis : **78 tirages**, treize rouleaux du prix, six par rouleau, paramètres et
    graines strictement identiques — **0 des 13** rouleaux dont les six runs rendent la même
    aire ; **5 sur 13** où le verdict bascule ; mauvais tirages **5 / 78 = 6,4 %**
    (IC 95 % exact **2,1 % – 14,3 %**). Les cinq bascules : 1615, 428, 607, 140, 1371
    auto-intersections contre zéro sur les cinq autres runs du même rouleau.
  - L'ampleur ne dit pas quel tirage a mal tourné : les trois rouleaux dont les six aires
    s'accordent à un tiers de pour cent près portent les pires comptes ; excentricité de
    rang **0,60** là où 0,50 est ce que prédit « l'aire ne dit rien », sur quatre événements.
  - Test de convergence α = `log(growth) / log(widening)` : segment officiel PHerc1447
    31 → 81 couches, 17.28 → 17.30 µm, **α = +0.00** ; une de nos traces, même rouleau,
    même chaîne, 21 → 161 couches, 86.40 → 682.56 µm, **α = +1.01**.
  - Conséquence : toute distance surface↔feuille publiée pour nos traces non convergentes —
    **94 µm, 146–187 µm, 311 µm** — est **sans objet**.
  - **Dix-sept** tentatives de croissance depuis une graine donnent toutes α ≈ 1 ; quatre
    runs rembobinés-corrigés atteignent **+0.89** au mieux.
  - Audit des profils de profondeur : **aucun verdict convergent n'est affecté** ; le plus
    grand α convergent mesuré est **+0.4222** contre un plus petit non discriminant
    **+0.8729**.
  - Mode `gen_neighbor` chaîné : le segment officiel de départ **+0.00**, et **six surfaces
    consécutives** générées chacune depuis la précédente, **toutes ≤ +0.246**.
  - Balayage du pas `neighbor_step` à profondeur de chaîne égale : 1.0 → α moyen +0.357
    (pire spire +1.475) · 0.5 → +0.129 (+0.583) · **0.25 → +0.102 (+0.246)** · 0.125 →
    +0.327 (+0.758). Courbe en U.
  - Ce que le pas ne change pas : érosion à **4.0 %** de l'aire de grille par tour sur les
    quatre réglages, distance mesurée entre feuilles consécutives **102–116 µm**.
  - Limites : sur la surface portant réellement de la matière, l'érosion est **15.6 %** par
    tour (moitié de l'aire perdue en quatre tours) ; la fraction de sommets valides tombe de
    **58 % à 23 %** sur une chaîne de neuf spires ; chaque fenêtre couvre ~10 % d'un tour et
    les spires consécutives sont à **113 µm** dans la même fenêtre angulaire.
  - Meilleur prédicteur de l'α d'une spire, sur quatre campagnes et quarante spires : sa
    **position ordinale dans la chaîne** (ρ = **+0.53**, p = 0.001).
  - α sur deux fenêtres ne discrimine pas mieux que **±0.2** ; près d'un quart des verdicts
    de spire distincts tombent dans cette largeur, l'un à deux millièmes de son seuil.
  - Extension latérale : segment publié tel que téléchargé — 4.28 cm², arc 21.9 mm, 59 % de
    sommets valides, α **+0.000** ; après une extension — **12.97 cm²**, **37.2 mm**,
    **96 %**, α **+0.000**.
  - Le mode de croissance tire d'un générateur non semé et tourne multi-thread : trois runs
    identiques ont donné **0, 596 et 0** auto-intersections et α **+0.000, +0.422, +0.000** ;
    graine fixée et un seul fil rendent le même maillage bit pour bit.
  - Budget de croissance : **100** → 12.97 cm², **0** auto-intersections, α **+0.000** ·
    200 → 28.62 cm², 25 036, **+1.313** · 200 en deux sessions de 100 → 50.30 cm², 4 996,
    +1.040.
  - Réparation par élagage : élaguer l'extension à ses dix premières générations rend
    **6.02 cm²** avec une périphérie aussi propre que la source — **41 % de matière validée
    en plus** que le segment publié, à α = +0.000.
  - Le cycle élaguer-étendre **converge vers un point fixe près de 6 cm²** : étendre la
    surface propre converge (α = +0.000) mais l'élaguer redonne 6.02 cm² exactement.
  - Recoudre des segments publiés **n'a aucun candidat** : ce rouleau a **15 segments
    publiés**, 51 de leurs 105 paires se recouvrent par boîte englobante, mais l'écart
    médian point-à-point donne **0 paire sous 40 µm**, 2 entre 40 et 250 µm ; **la paire la
    plus proche du rouleau est à 79 µm**. Coût de l'établissement : 4.5 Mo et quelques
    secondes.
  - `src/depot/verifier_chiffres.py` recalcule **333 chiffres** depuis leurs JSON et les
    cherche littéralement dans les documents ; sort **1** si l'un manque, **2** si un
    fichier de résultat est absent.
- **rétractations / corrections internes** :
  - §4, puce du confond de taille : ⚠⚠ « **Corrigé le 2026-08-19** » — la puce vivait sous
    une section parlant de `material` et **importait les chiffres d'un autre critère** ;
    +0.384, +0.463, −0.315 → −0.382 appartiennent à `ecart_a_la_trace`. « Deux fautes en
    une : le mauvais critère, et une réserve omise que la source porte » (le critère ne
    passe que le seuil nominal, pas Bonferroni).
  - §7 : « ⚠ **Four** ideas were tested and did not survive *(corrigé le 2026-08-19 : le
    texte annonçait « three » et la liste en compte quatre)* ».
  - §10 originel : ⚠⚠ « **Le §10 ci-dessus est PÉRIMÉ, et sa dernière phrase est fausse** »
    — sa conclusion *« the surface is not reproducible, the verdict is »* est réfutée par
    `30` puis `35` ; le §10 est **à remplacer**, pas à nuancer.
  - §10 originel, dans le texte anglais : « ⚠ **Five** runs of the same seed *(corrigé : le
    texte disait « six » et l'énumération en décrit cinq)* » ; et « ⚠ We first wrote "the
    tracer is not reproducible", which is true but too coarse ».
  - §10 bis : « ⚠ **This corrects our own earlier claim.** … The verdict is not reproducible
    either; we had simply not repeated on enough scrolls to see it. »
  - §11 : déclare sans objet toute distance surface↔feuille publiée par les auteurs pour
    leurs traces non convergentes (94 µm, 146–187 µm, 311 µm) — « Not an underestimate: a
    measurement of a quantity that does not exist at that location. »
  - §12 : note méthodologique — une conclusion reposant sur une spire à deux millièmes de
    son seuil a été publiée puis **rétractée le jour même**.
  - §12 : ⚠ la formulation « lying across the stack » est signalée comme sur-affirmative
    puisque α ≈ 1 a deux causes, dont l'absence totale de pic.
  - §13 : ⚠⚠ le premier résultat mesuré était « a coin flip » (0, 596, 0
    auto-intersections) ; tous les nombres publiés viennent de la configuration épinglée.
  - §9 : le critère « le pic dans le tiers central » est **retiré** parce qu'une référence
    officielle y échoue.
  - En-tête : ⚠ « Ce brouillon ne s'envoie pas tel quel » — chaque chiffre à revérifier, et
    l'adresse du dépôt public n'existe pas encore.
- **preuve de lecture intégrale** :
  - ligne 388 (après 60 % du fichier) : `> we produce that the convergence test does not condemn.**`
  - ligne 512 (dans les 15 dernières lignes non vides) : `| 4 | ⚠ décider si le corps part en anglais — c'est la seule décision de forme ouverte |`



Dépôt : `/home/masterlaplace/LplVesuvius`. Chaque fichier a été lu du premier au dernier
caractère, couverture vérifiée par `wc -l` avant lecture.

---

### docs/22_batch_repliquer.md
- **lignes** : 112
- **nature** : MIXTE
  (l'ossature est un registre de batch — quatre voies P/Q/R/S avec colonne « état » — mais
  le document tranche lui-même plusieurs verdicts mesurés et enregistre trois rétractations.)
- **résumé** : Batch ouvert le 2026-08-19 pour attaquer la faiblesse structurelle de la
  règle de `19` — elle repose sur un seul corpus (80 segments de Scroll 1). Il pose la
  prédiction *avant* la mesure, falsifiable dans les deux sens, et l'applique à 110
  segments supplémentaires répartis sur trois corpus (PHerc0172, PHerc0139, PHerc1667).
  Verdict : la règle **ne réplique pas**, et deux des explications avancées en cours de
  route sont tombées. Le lot se clôt sur un terrain qu'il n'avait pas prévu — la première
  trace d'un rouleau du prix (`24`).
- **conclusions extractibles** :
  - Trois corpus publient à la fois volumes de surface et cartes d'encre : PHerc0172
    (Scroll 5) 53 segments à 7,91 µm, PHerc0139 38 segments à 9,362 / 2,399 / 1,129 µm,
    PHerc1667 (Scroll 4) 19 segments à 2,399 / 1,129 µm — **110 segments de plus**, sur
    trois rouleaux et quatre résolutions.
  - P1 : 110 cartes d'encre récupérées (PHerc0172 53, PHerc0139 38, PHerc1667 19).
  - P2 : `avec_matiere` mesuré avec la définition standard (`zarr_depth`) sur 110 segments
    à 392 points.
  - P4 : rejouée contre 2000 permutations corpus par corpus, **la règle ne réplique pas**.
  - P5 : le plateau ne se retrouve **pas** hors de Scroll 1 ; PHerc0139, à la même
    résolution et avec une étendue **plus grande**, rend le signe **opposé**.
  - Trois effets nets sur une population ont déjà fondu sur la suivante dans ce dépôt : les
    fibres (+0,330 → **−0,192**), la phase (+0,52 → **+0,15**), le seuil des 50 µm
    (direction gardée, seuil perdu).
  - Q1 : défaut trouvé en essayant le mode lot — à faible échantillonnage, `coherence`
    0,435 contre un témoin à **0,423** ; le contrôle avait cessé de discriminer et rien ne
    le disait. `pairs` et `coherence_reliable` voyagent désormais avec.
  - S2 : la migration des bandes niveau 0 est l'**exception** — 2 sur 6, Fisher p = 0,079,
    et le témoin positif ressort.
  - Un gauchissement déplace le maillage, donc régénère un autre volume de surface ; les
    volumes de surface sont des artefacts publiés, donc ce lot ne peut livrer que le champ
    lui-même, pas la correction.
  - Il ne faut pas agréger les quatre corpus en un seul n : résolutions et traceurs
    différents ne se moyennent pas (confond de `07` §9).
- **rétractations / corrections internes** :
  - §Clôture : « ⚠ **Trois voies sur quatre sont fermées** *(corrigé le 2026-08-19 : cette
    ligne disait « les quatre »)* ».
  - P5 : « Mon explication par un effet de plancher était **fausse** : PHerc0139, à la même
    résolution et avec une étendue **plus grande**, rend le signe opposé ».
  - P2 : le `avec_matiere` de `champ_correction` n'est **pas** comparable — il mélange
    repérage et blocs, « et c'est ce qui a produit le faux contrôle de `19` §9 ».
  - R1 / voie R : la limite écrite (« la chaîne maillage → rendu n'est pas ici ») est
    **périmée le jour même** — VC3D est construit, et `24` la pilote de bout en bout.
  - R2 : l'écart sort en index de couche, pas en µm le long de +n ; l'export a trouvé une
    **seconde** réponse à « le pic est-il au bord », fausse sur les piles impaires.
  - §final : trois conclusions propres corrigées par la mesure — le contrôle de robustesse
    de `19` §9 comparait deux grandeurs différentes ; l'explication par effet de plancher
    couvrait un corpus sur trois ; « la chaîne de production n'est pas ici » était faux
    (32 dépôts clonés, dont le monorepo officiel).
- **preuve de lecture intégrale** :
  - l. 68 : « pas ici. Ce qui **est** livrable, c'est le champ lui-même — de combien, où, et si c'est »
  - l. 112 : « aplati, rendu — et **condamné par nos propres instruments avant qu'on regarde l'image**. »

---

### docs/23_rouleaux_du_prix_traces.md
- **lignes** : 72
- **nature** : MIXTE
  (§1 est un inventaire compté ; §2 est une mesure de trace, la première sur un rouleau du
  prix ; §3 est une procédure de reproduction.)
- **résumé** : Inventaire complet des treize rouleaux du Grand Prize, produit par un script
  versionné : dix sur treize n'ont été tracés par personne, les treize publient volume,
  prédiction de surface avec normal-grids et champ `lasagna`. `PHerc1447` est le seul à
  publier des volumes de surface (4 segments sur 16, à 8,64 µm, aucune carte d'encre), ce
  qui permet la première application de nos instruments à un rouleau du prix. Le quatrième
  segment sort comme hors du papyrus, et trois grandeurs indépendantes le disent ensemble.
- **conclusions extractibles** :
  - Dix rouleaux sur treize (PHerc0125, 0191, 0211, 0257, 0268, 0358, 0813, 0826, 1218,
    1545) ont **0 segment** ; PHerc1203 en a 1, PHerc0800 6, PHerc1447 **16**.
  - Les treize publient tous un volume, une prédiction de surface avec ses *normal-grids*,
    et le champ d'enroulement `lasagna`.
  - `PHerc1447` est le **seul** des treize à publier des volumes de surface : 4 segments sur
    16, à **8,64 µm**, et **aucune carte d'encre**.
  - Les quatre segments mesurés : matière 57,5 / 51,0 / 59,0 / **9,0 %** ; au bord 0,0 / 3,6
    / 6,0 / **17,4 %** ; écart −17,3 / −13,0 / −8,6 / **+86,4 µm** ; résiduel 8,6 / 13,0 /
    77,8 / 43,2 ; part rigide 66,7 / 50,0 / 10,0 / 66,7 % ; cohérence −0,144 / +0,504 /
    +0,635 / +0,269.
  - Le quatrième segment (`20251105093211-z_dbg_gen_00320`) est hors du papyrus : 9 % de
    fenêtres avec matière quand les autres sont à 51–59 %, 17,4 % de pics collés à un bord,
    écart de +86 µm quand les autres sont sous 18.
  - Le diagnostic coûte **300 requêtes par segment** et se calcule avant toute inférence.
  - n = 4 : ce qui est solide est le diagnostic d'un segment, pas une statistique sur le
    rouleau.
  - Les trois bons segments ont des parts rigides hautes (66,7 / 50,0 / 10,0 %), donc
    contrairement à Scroll 1, 4 et 5, une translation y enlèverait souvent la moitié de
    l'erreur — observation, pas résultat, à 8,64 µm et sur quatre segments.
  - Pour `PHerc0358`, la lecture « le prix y est intact » est la plus probable : `16` en
    fait le moins difficile des treize (bonne séparabilité médiane, seulement 4 % de poches
    indissociables).
- **rétractations / corrections internes** : aucune rétractation d'un énoncé publié
  antérieurement. Le document signale une erreur corrigée **pendant** son écriture (§1) :
  une réponse S3 contient le préfixe interrogé en plus de ses sous-préfixes, et compter les
  lignes sans l'exclure décalait la table de « un partout » — « et une table décalée d'un
  cran ressemble parfaitement à une table juste ». Il pose aussi deux réserves explicites
  (§1 : deux lectures d'un zéro que rien ici ne départage ; §2 : n = 4).
- **preuve de lecture intégrale** :
  - l. 51 : « **Ça coûte 300 requêtes par segment et se calcule avant toute inférence.** C'est »
  - l. 63 : « observation, pas un résultat. »

---

### docs/24_premiere_trace_rouleau_du_prix.md
- **lignes** : 176
- **nature** : RESULTAT
  (le document établit des faits mesurés — aire, auto-intersections, profils de profondeur,
  image — la §5 « Reproduire » n'étant qu'un mode opératoire annexe.)
- **résumé** : VC3D construit, chaîne officielle pilotée en ligne de commande, et
  `PHerc0358` — un des dix rouleaux du prix sans segment publié — tracé pour la première
  fois, en une heure et sans télécharger le volume de 893 Go. La trace est condamnée par nos
  propres instruments **avant** le rendu : 240 auto-intersections transverses avec
  pénétration maximale de 200 µm, soit plus d'un écart inter-feuilles. Le titre a lui-même
  été corrigé (« trois instruments » → deux), la jambe « profondeur » ayant été retirée du
  verdict le jour même, et la **cause** proposée au §4 a été réfutée deux fois ensuite.
- **conclusions extractibles** :
  - Chaîne complète mesurée : trace `vc_grow_seg_from_seed` **8,48 cm²**, 79 générations,
    **13,9 s** ; contrôle `vc_tifxyz_selfcross` **240 auto-intersections**, 0,05 s ;
    aplatissement grille 159×158, 96,2 % des points rastérisés ; rendu 21 couches,
    3141×3121, **29,4 × 29,2 mm**.
  - `-v` accepte `https://` pour le traçage : le volume de **893 Go** n'est jamais
    téléchargé, il streame par chunks.
  - 240 contacts transverses sur 48 040 triangles, localisés (~0,35 % de la surface), avec
    une pénétration maximale de **21,5 voxels = 200 µm**, soit plus d'un écart
    inter-feuilles (**187 µm** mesuré sur ce rouleau).
  - Instrument de profondeur sur notre rendu : **64 %** de fenêtres dont le pic est au bord,
    16 % dans le tiers central, écart médian pic ↔ couche tracée **94 µm** (à comparer aux
    61 % au bord de `12` §9 sur Scroll 4).
  - Distribution bimodale : 15 fenêtres piquent à la couche 0, 9 à la couche 20, une seule
    au milieu.
  - `voxelsize` vaut 0 par défaut, donc l'aire en cm² est nulle par construction et toute
    surface est rejetée avec « area 0 below min_area_cm » ; `seed.json` doit porter
    `"voxelsize": 9.362`.
  - `[tif] all slices exist, skipping` : l'outil saute par-dessus 21 fichiers tronqués
    laissés par un run tué — « un outil qui saute ses sorties existantes saute aussi ses
    sorties corrompues ».
  - Le rendu montre deux plaques séparées par du vide, et le détail à pleine résolution
    (1000 × 1000 px = 9,4 × 9,4 mm) montre des striations qui bifurquent, s'enroulent et se
    superposent : plusieurs feuilles vues par la tranche, non les fibres parallèles d'une
    seule feuille.
  - Les instruments construits sur des segments publiés ont correctement condamné une trace
    faite une heure plus tôt, avant tout rendu, et leur diagnostic est confirmé par l'image.
  - Le verdict tient sur **deux** instruments et non trois : les 240 auto-intersections
    mesurées avant tout rendu, et l'image.
- **rétractations / corrections internes** :
  - **Titre** : « ⚠ **Ce titre disait « trois instruments » jusqu'au 2026-08-19.** La
    troisième jambe — la profondeur — a été retirée du verdict le jour même (§2), et le
    titre ne l'avait pas suivi. »
  - §2, correction du 2026-08-19 (`25` §5) : la jambe profondeur ne tient pas — la fenêtre
    de 21 couches vaut ±94 µm, soit une demi-distance inter-feuilles, **61 % des profils y
    sont plats** (amplitude médiane 1,5 %) et la « bimodalité » en est en partie
    l'artefact ; sur 61 couches, la trace **officielle** d'un rouleau du prix rend **2 %**
    au tiers central contre 16 % ici.
  - §2, signalement levé le 2026-08-20 : l'hypothèse d'une mauvaise origine de mesure a été
    **réfutée** par `36` sur le même segment mesuré des deux façons — 3,00 µm dans le volume
    publié contre 17,28 µm dans notre rendu, soit 14,3 µm d'écart.
  - §4, correction du 2026-08-19 au soir : « le verdict tient, la CAUSE non » — `30` a
    rejoué la graine **quatorze fois** à paramètres identiques et obtenu **treize traces
    propres sur quatorze** ; un tirage rend 8,477096 cm² contre 8,476817 pour le maillage
    archivé (0,003 % d'écart d'aire, 0 croisement contre 240). « 240 était un tirage dans la
    queue. »
  - §4 : le diagnostic « le traceur n'a reçu aucune information d'orientation
    (`direction_fields` absent) » est **FAUX** et mesuré comme tel par `26` — le champ ne
    déplace pas la croissance d'un centième, ni par sa présence, ni par son orientation, ni
    à cent fois son intensité, ni sous forme de grilles dérivées du volume (×22 de coût, 68
    générations identiques).
  - §4 : deux chiffres du paragraphe étaient faux — les `normal-grids` font **10,40 Go** et
    non 182 Mo, et elles sont lues par `normal_grid_path`, pas par `direction_fields`.
  - §4, tableau : la piste « réduire `step_size` » est marquée ~~balayage en cours~~ →
    rendu dans `26` §9.
- **preuve de lecture intégrale** :
  - l. 106 : « faite une heure plus tôt, avant tout rendu, et leur diagnostic est confirmé par l'image.** »
  - l. 176 : « ⚠ `seed.json` **doit** porter `"voxelsize": 9.362`, sinon tout est rejeté à 0 cm². »

---

### docs/25_une_graine_choisie_sur_la_planeite.md
- **lignes** : 516
- **nature** : RESULTAT
  (mesures appariées sur treize rouleaux, campagnes, balayages de fenêtre, témoins ; les §6
  et §7 sont des annexes de reproduction et de contrôle.)
- **résumé** : Le critère de choix de graine passe de la moyenne d'un cube de voisinage
  (qui saturait à 255 et ne classait rien) à la **planéité** du tenseur de structure 3D,
  avec plafond d'occupation et voxel allumé. Sur `PHerc0358` la seule graine fait passer 240
  auto-intersections à 0 — mais la réplication sur douze autres rouleaux montre que ce 240
  est l'accident d'un rouleau, et que ce qui réplique réellement est que le traceur **va
  plus loin avant de caler** (11 sur 13, p = 0,0225). Le §5 retire ensuite la moitié du
  résultat : la graine ne règle pas la pose de la surface, qui reste **en travers** de
  l'empilement (amplitude 8,7 % contre 50,1 % pour une trace à AUC 0,925).
- **conclusions extractibles** :
  - Le critère de `24` ne classait rien : huit candidats à **255,0** exactement, c'est-à-dire
    le plafond du format sur une prédiction seuillée (`th0.2`), donc binaire.
  - Planéité = (λ₁ − λ₂) / λ₁ du tenseur de structure J = ⟨∇f ∇fᵀ⟩ ; une feuille rend 1,00,
    deux feuilles parallèles 1,00, une jonction à 90° 0,00, du bruit isotrope 0,04, un bloc
    uniforme un tenseur nul (écarté).
  - Biais d'orientation mesuré : sur un plan synthétique tourné de 0° à 90° la planéité brute
    descend de 1,000 à **0,828** (écart 0,172) ; un lissage 3³ avant les gradients ramène
    l'écart à **0,053**.
  - Le second piège de saturation : l'argmax de la planéité sur les 13 824 blocs d'un chunk
    de 192³ rend **quatre candidats à 1,0000 exactement**. Après passage à la moyenne 3³ la
    part planaire va de **0,121 à 0,967**, et les niveaux 0 et 1 désignent le même endroit à
    un tiers de chunk près.
  - `PHerc0358`, un seul paramètre changé : graine A (1544 1544 7768) → 8,48 cm², 48 040
    triangles, 387 151 paires, **240** auto-intersections, pénétration 21,5 vx = 201 µm ;
    graine B planéité (5842 5839 7386) → **19,82 cm²**, 112 338 triangles, 852 135 paires,
    **0**, pénétration 0. Contrôle : segment officiel `PHerc1447` (2,89 cm², 388 083 paires,
    **0**), issu de la même chaîne (`source: "vc_grow_seg_from_seed"`, `mode:
    "explicit_seed"`, `min_area_cm: 0.3`).
  - L'aire n'est pas un critère : deux traces planaires s'arrêtent à la génération 119 sur
    120 et rendent **19,821 592** et **19,823 246 cm²** — un plafond, pas une mesure ; la
    même graine poussée à 600 générations atteint **127,9 cm²**.
  - La graine de `24` a une occupation de **1,000** (bloc entièrement plein, tenseur nul).
  - Campagne appariée sur 13 rouleaux du prix, aire : **planéité 11, voisinage 2, aucun ex
    æquo, test des signes p = 0,0225**. Sur les 11 paires informatives (au moins un critère
    s'arrête de lui-même) : **11 à 0, p = 0,0010**. Le treizième rouleau fait passer 10/12 à
    p = 0,0386 à **11/13 à p = 0,0225**.
  - 7 traces de planéité sur 13 butent sur le plafond de générations ; les deux « défaites »
    se jouent à 0,09 et 0,001 cm², sur les deux seuls rouleaux (PHerc0268, PHerc0800) où les
    quatre traces s'arrêtent toutes à 118 générations.
  - Auto-intersections : **0 partout, des deux côtés** sur les douze autres rouleaux — le
    « 240 → 0 » ne réplique pas comme propriété du critère. Cas extrêmes : sur `PHerc0125`
    et `PHerc0826` le voisinage cale à **0,85 cm²** quand la planéité atteint 19,82 et 13,14.
  - Appariement surface/volume : `head -1` sur deux listages n'apparie que par position ;
    sur les quatorze rouleaux du prix, **0 est mal apparié aujourd'hui** et **2 ont plusieurs
    scans** (PHerc0139, PHerc1203) — défaut latent, pas actif.
  - Reproductibilité : quatre exécutions de la même graine rendent 19,834872 / 19,821850 /
    19,838660 / 19,823302 cm², toutes à **0** auto-intersection ; `thread_limit: 1` ne
    supprime pas l'écart (~0,08 %). Mais **les 118 générations sont identiques au centième
    dans les six exécutions**, toutes finissant à **1985,73 mm²** : la croissance est
    déterministe, l'étape finale ne l'est pas.
  - Balayage de fenêtre spatiale sur la même pile : 9,6 mm → amplitude 3,5 %, 22 % de
    profils plats ; 4,8 mm → 3,4 % / 15 % ; 2,4 mm → 5,4 % / 7 % ; **1,2 mm → 8,7 % / 1 %**.
  - Comparaison à taille physique égale (1,2 mm, ±281 µm) : Scroll 1 AUC 0,925 → amplitude
    **50,1 %**, tiers central 77 %, bord 5 % ; Scroll 4 (échec connu) → 19,3 % / 13 % / 29 % ;
    notre A → 14,8 % / 16 % / 27 % ; notre B → 8,7 % / 20 % / 28 % ; officiel `PHerc1447` →
    28,8 % / **2 %** / 38 %.
  - Sur `PHerc1447`, les quatre segments qui publient un volume de surface rendent **18,2 %,
    25,0 %, 62,5 % et 68,2 %** de pics dans le tiers central — un facteur 3,7 — et le dernier
    est `z_dbg_gen_00320`, un artefact de débogage à 4 fenêtres exploitables sur 50.
  - L'amplitude a une signification physique : une surface parallèle aux feuilles a une
    normale qui traverse l'empilement (profil oscillant), une surface qui coupe l'empilement
    garde sa normale dans une même matière (profil plat). Notre surface B est posée **en
    travers** de l'empilement — compatible avec zéro auto-intersection.
  - L'amplitude est nécessaire, pas suffisante : Scroll 4 échoue d'une troisième façon (la
    trace est dans le vide) pour une amplitude plus haute que la nôtre.
  - Témoins : 22 contrôles hors ligne, cinq sondes qui remplacent une garde par sa version
    fautive, chacune faisant tomber 1 témoin.
  - Reproduction des deux figures, vérifiée le 2026-09-05 **octet pour octet** :
    `figure_deux_traces.py` sur `render_a61` et `essai_b/render_b61`
    (`64e766bf227558322c0091915d0d2267`), `figure_signatures.py` sur les quatre couches
    tracées — 32 pour les deux références, 30 pour les deux piles de 61 —
    (`d127f8216be82aa5d387141ecaecb7ae`). ⚠ Le voxel passé à chaque vignette est ce qui
    rend l'échelle commune ; deux valeurs différentes feraient passer une surface deux
    fois plus grande pour une surface identique.
- **rétractations / corrections internes** :
  - §4, correction du 2026-08-19 au soir : l'explication par le bloc plein (occupation
    1,000) « ne survit pas à la répétition » — `30` rejoue la graine de `24` quatorze fois
    et obtient une trace propre treize fois sur quatorze ; le plafond d'occupation
    n'explique **pas** les 240.
  - §4 : le « 240 → 0 » est retiré comme propriété générale du critère ; ce qui est répliqué
    est la distance parcourue avant de caler.
  - §4bis : « ⚠ Corrigé le 2026-08-19 : ce paragraphe disait « les **deux** qui en ont ».
    L'inventaire versionné en recense **trois** » (PHerc1447 16 segments, PHerc0800 6,
    PHerc1203 1).
  - §4bis, corrigé pour de bon le 2026-08-22 : l'absence de `PHerc1203` était un trou de
    `campagne_graines.sh`, trouvé par `35` §5.
  - §4bis : « Le compte de traces tronquées était faux » — le plafond était cherché dans les
    **aires** (19,8 cm² à 9,362 µm, 16,9 à 8,64 µm), donnant **5 sur 13** au lieu de **7** ;
    il se lit désormais dans les générations.
  - §3 : le piège de saturation a été repayé un étage plus haut, « dans le fichier qui
    documentait déjà le piège ».
  - §3 : l'ancien code rendait le centre du bloc et « a marché **par chance**, sur un bloc
    saturé donc plein ».
  - §4ter : « l'affirmation « le traceur n'est pas reproductible » est trop grossière, et la
    mesure suivante l'a corrigée » — c'est l'étape finale qui varie, pas la croissance.
  - §5 : première mesure de profondeur « fausse par construction » (62 % de pics au bord sur
    une fenêtre de 21 couches valant ±94 µm, 61 % de profils plats).
  - §5, corrigé le 2026-08-20 : « le raisonnement tient, la PRÉMISSE non » — le soupçon
    d'origine décalée est **réfuté** par `36` (14,3 µm d'écart) ; ce qui reste est qu'« un
    segment officiel n'est pas une référence ». Le critère du tiers central est
    « reconsidéré, pas rétabli ».
  - §5 : « Cela oblige à corriger `24` » — le verdict y passe de trois jambes à deux.
  - §5 : la piste `direction_fields` a « depuis été mesurée NÉGATIVE trois fois » (`26`).
  - §5 : les `normal-grids` font **10,40 Go**, « pas 182 Mo ».
  - §7 : « Trois de ces cinq sondes passaient au vert à la première tentative : mes fixtures
    ne pouvaient pas échouer » — trois raisons données, sondes refaites.
- **preuve de lecture intégrale** :
  - l. 304 : « un rouleau à deux scans, il sort en erreur en nommant ce qui existe. »
  - l. 504 : « ⚠ **Trois de ces cinq sondes passaient au vert à la première tentative** : mes fixtures ne »

---

### docs/26_le_champ_de_direction.md
- **lignes** : 758 ⚠ (701 quand la fiche a été écrite ; la mesure du tableau « sans filtre » a été **perdue puis restaurée** le 2026-09-04)
- **nature** : RESULTAT
  (série de mesures avec contrôle positif ; le §10 « Reproduire » et la seconde §9 « T1f »
  sont eux-mêmes des campagnes mesurées.)
- **résumé** : Deux mécanismes censés gouverner la trajectoire du traceur —
  `direction_fields` et `normal_grid_path` — sont dérivés du binaire faute de
  documentation, leur encodage est mesuré et répliqué sur trois rouleaux, et **aucun des
  deux ne déplace la croissance d'un centième**, y compris à ×100 d'intensité et avec 1,53
  Go de vraies grilles coûtant 29 fois le temps de calcul. Le contrôle positif montre que la
  méthode sait pourtant détecter un changement (`step_size` diverge dès le premier pas). Le
  document identifie douze poids de perte (et non dix), montre que le terme dominant
  `NORMAL` rendait zéro dans toutes nos traces de base, et se termine sur un balayage de pas
  dont une partie n'est pas reproductible. Une conclusion du §3 est explicitement retirée le
  2026-08-20 après un audit de filtre.
- **conclusions extractibles** :
  - §9, **ajouté le 2026-09-05** : les deux commandes de `table_pas.py`, vérifiées — la colonne « bonne graine » sort du défaut de l'outil, la « mauvaise graine » de `data/trace/PHerc0358/pas_mauvaise_graine`, et les deux rendent le tableau publié y compris les étendues de 5,5 % et 12,0 %.
  - Contrat dérivé : `"direction_fields": [{"zarr": <base>, "dir": <sens>, "scale":
    <niveau>}]`, l'outil ouvrant `<base>/x/<niveau>`, `/y/`, `/z/` ; sens valides `normal`,
    `horizontal`, `vertical` ; clés facultatives `weight` et `weight_zarr` ; chemin local
    (`std::filesystem::path`), pas d'URL.
  - Le champ n'exige que **626 Mo** au lieu de plusieurs gigaoctets, un zarr rendant sa
    valeur de remplissage pour les chunks absents.
  - Encodage mesuré par balayage du zéro supposé : 0 → 53,1°, 64 → 37,9°, 96 → 17,6°,
    **128 → 6,6°**, 160 → 21,5°, 192 → 36,7°, 255 → 46,2° ; donc **(v − 128) / 127**.
  - Répliqué : `PHerc0358` 13 659 blocs, centre 128, écart **6,6°** ; `PHerc0125` 13 697,
    128, **5,7°** ; `PHerc1447` 1 488, 128, **6,2°**.
  - Conséquence : la composante `z`, qu'aucun rouleau ne publie, se remplit de **128** et
    non de 0 (zéro voudrait dire −1, une normale verticale partout).
  - `direction_fields` n'intervient pas dans la croissance : sans champ ×2, sans champ
    `thread_limit: 1` ×2, avec champ `dir: normal`, et avec champ aux axes x/y **permutés**,
    les 118 générations sont identiques et finissent toutes à **1985,73 mm²**.
  - Le champ agit dans l'étape finale et fait empirer, avec un classement ordonné sur un
    facteur 14 : aucun 0 ; `normal` 1 176 ; axes permutés 8 282 ; `horizontal` 10 623 ;
    `vertical` **16 983** auto-intersections.
  - Balayage d'intensité : aucun champ 19,82 cm² / 0 ; défaut 20,75 / 1 176 ; `weight: 10`
    26,84 / 81 464 ; `weight: 100` 26,71 / 69 580 ; `direction_weight: 10` 27,84 / 66 243 ;
    `direction_weight: 100` **137,98 cm²** / 34 340 — croissance identique dans les six.
  - Remesure filtre `--maxedge` désactivé : `weight: 10` 222 272 (**8 281**/cm²),
    `weight: 100` 199 833 (**7 481**), `direction_weight: 10` 184 587 (**6 630**),
    `direction_weight: 100` **2 455 822** (**17 798**/cm²), ratio 71,5× contre 2,73–2,87
    pour les trois autres. La densité **double** au lieu de chuter d'un facteur 12.
  - `GrowPatch.cpp` `applyJsonWeights()` lignes 1304–1315 lit **douze** clés ; `DIST` 1,
    `STRAIGHT` 0,2, `DIRECTION` 1, `SNAP` 0,1, `NORMAL` **10**, `NORMAL3DLINE` 0,
    `REFERENCE_RAY` 0, `SURFACE_SDT` (clé `sdt_weight`) 0, `SPACELINE` (clé
    `space_line_weight`) 0, `SDIR` 1, plus `correction_weight` 1 et `patch_normal_weight` 0.
  - Le lecteur de poids est **muet sur une clé inconnue** : `surface_sdt_weight: 7` ne
    produit ni erreur, ni avertissement, ni effet.
  - `NORMAL` pèse 10 — dix fois `DIST` — et rend 0 tant qu'aucune grille de normales n'est
    chargée (`if (!trace_data.ngv && !trace_data.patch_normals) return 0;`) : dans toutes nos
    traces de base le terme dominant ne créait aucun résidu.
  - Piège de priorité : le commentaire annonce `explicit param > normal_grid > resume_surf >
    default`, le code place `resume_surf` **avant** `ngv`.
  - `scale` sert aussi de facteur de conversion de coordonnées : sur des données identiques,
    1,0 → 19,782036 / 0 ; **2,0 → 20,747079 / 1 176** ; 3,0 → 19,773946 / 0 ; 4,0 →
    19,773791 / 0. 2,0 est la bonne registration.
  - `normal_grid_path` (singulier, racine du `seed.json`) est bel et bien lue : « Loaded
    normal grid level 0 (coordinate_scale=1, output_spiral_step=20) ».
  - Inventaire réel des `.normal-grids` de `PHerc0358` : `xy/` 14 744 fichiers 3,83 Go,
    `xz/` 7 783 / 3,27 Go, `yz/` 7 783 / 3,30 Go — **30 310 fichiers, 10,40 Go** ; une boîte
    de ±700 voxels autour de la graine fait **1,1 Go**.
  - Avec 1,53 Go de vraies grilles : vitesse 73,45 → **2,57 mm²/s** (facteur 29), trajectoire
    **identique au centième** sur 118 générations, aire 24,06 cm², **112 139**
    auto-intersections contre 0.
  - Les grilles publiées sont dérivées de la prédiction elle-même (même préfixe de nom), donc
    les redonner au traceur est une tautologie.
  - Grilles générées depuis le **volume masqué** (893 Go, boîte de 3,44 Go, 36 dalles sur
    238) : sans grille 23,80 mm²/s ; `xy` seul 2,15 mm²/s (×11), identique sur 18
    générations ; les trois directions 1,07 mm²/s (**×22**), **identique sur 68
    générations**, jusqu'à 667,52 mm² exactement des deux côtés.
  - Contrôle positif : `step_size: 15` (défaut 20) **diverge dès la génération 0** (0,42 →
    0,24 mm²) ; `search_effort: 3` identique sur 18 générations.
  - Bilan : la croissance bouge avec `step_size` (oui), pas avec `search_effort`, pas avec
    `direction_fields` (présence, orientation, sémantique, intensité jusqu'à ×100), pas avec
    `normal_grid_path`.
  - §9bis, campagne appariée à une clé près : témoin 19,825 cm² / 0 croisement / **32 %** au
    tiers central / 39 % au bord / α 1,332 ; `sdt_weight` 1 → 19,824 / 0 / 9 % / 66 % /
    0,901 ; `sdt_weight` 10 → 19,824 / 0 / 6 % / 58 % / 0,971 ; fibres h+v → 22,431 /
    **8 926** / 9 % / 53 % / 1,038 ; `sdt` 10 + fibres → 22,836 / **8 538** / 6 % / 59 % /
    1,038. Les quatre dégradent d'un facteur 3 à 5 ; le témoin est le meilleur.
  - `sdt_weight` ne mord pas : poids 1 et poids 10 rendent exactement le même écart
    (84,26 µm). La paire de fibres casse le maillage (128 fenêtres avec matière contre 66
    pour 13 % d'aire en plus).
  - α est un rapport de nombres **censurés** : l'écart médian des quatre variantes vaut
    84,26 µm = exactement 9,00 couches, soit la demi-fenêtre de 19 ; seul le témoin a son pic
    médian dans la fenêtre (couche 8 sur 19, 65,5 µm).
  - Le pas inter-feuilles de PHerc0358 vaut **187,2 µm** à 9,362 µm/voxel : 19 couches font
    0,95 pas, 41 en font 2,05, 161 en font 8,05.
  - Balayage `step_size` : un pas de **5 détruit la trace** sur deux graines (~800 croisements
    par cm² des deux côtés) ; **au-delà de 20 c'est propre** (deux graines, deux tirages,
    zéro partout) ; entre les deux (10, 15) le résultat n'est **pas reproductible** (0 contre
    4 613 sur le même réglage). Règle : `step_size` ≥ 20.
  - Coût d'une trace : `thread_limit: 1` 65,2 s / 329 % CPU / 91 Mo RAM / 0,2 Mo réseau ;
    `thread_limit: 0` 21,4 s / 1431 % / 117 Mo / 0,1 Mo. Ce n'est borné ni par le réseau ni
    par la mémoire, mais par le CPU ; à `thread_limit: 0` l'outil n'utilise que 14,3 cœurs
    sur 22 (croissance séquentielle en générations).
  - Reproduction : `bash src/campagnes/campagne_pas.sh` (bonne graine, `5842 5839 7386`) et
    `… data/trace/PHerc0358/pas_mauvaise_graine "1544 1544 7768"` — les deux coordonnées sont
    LUES dans les traces (`seed location [...]`), pas retapées. Puis `table_pas.py` dépouille.
    La remesure sans filtre : `bash src/outils/remesurer_sans_filtre.sh` →
    `docs/mesures/sans_filtre.json`, onze essais par défaut.
  - Reproduction de la récupération des grilles :
    `fetch_normal_grids.py <prefixe .normal-grids> data/champ_PHerc0358 --boite …`,
    boîte de ±700 voxels du **niveau 0** autour de la graine `5842 5839 7386`.
    ⚠⚠ Les trois dossiers `xy`/`xz`/`yz` sont indexés chacun par **un seul axe**, donc une
    boîte devient trois intervalles de tranches — c'est ce découpage qui fait 10,40 Go →
    **1,1 Go**, pas une décimation.
- **rétractations / corrections internes** :
  - En-tête : « **douze**, pas dix — deux des noms annoncés ici n'existaient pas, corrigé au
    §4 contre le code source » (`surface_sdt_weight` et `spaceline_weight`, zéro occurrence
    dans tout le dépôt villa).
  - §3, retiré le 2026-08-20 : la phrase « la densité d'auto-intersections chute d'un facteur
    **12** … le champ organise donc réellement quelque chose » est **barrée et retirée** — la
    remesure sans filtre montre que la densité **double** (8 281 → 17 798 par cm²).
  - §3 : les cinq comptes du tableau d'intensité ont été mesurés avec des quads **jetés** par
    `--maxedge` (de 3 358 à 82 000 selon la ligne), donc les lignes ne portent pas sur la même
    fraction de surface ; « aucune des deux lectures n'est « la vérité » ».
  - §3, « Ce que ça corrige de ce qu'on croyait » : le diagnostic de `24` §4 (repris par `25`)
    nommant `direction_fields` comme cause « est faux, ou du moins hors de portée ».
  - §4 : « la vérification annoncée dans la version précédente ne pouvait pas couvrir ces deux
    clés » — « une vérification qui porte sur « les dix » et n'en exerce que huit est une
    vérification incapable d'échouer sur les deux autres ».
  - §4 : l'explication proposée ici (« le champ pèse un dixième du terme dominant ») **était
    fausse** — le terme dominant s'allume (×29 de coût) et ne déplace pas la croissance.
  - §4, pièges d'écriture du script : le bloc d'échec imprimait « ALL PASS (1 failures, …) »,
    la chaîne exacte que `temoins.sh` cherche — « le contrôle serait passé au vert en
    affichant ses propres échecs ».
  - §2 : défaut de mon propre outil, un `|cos|` de 0,7071 exact — la valeur de remplissage
    d'un chunk absent était comparée comme si c'était une donnée (`PHerc1447` couvert à 46 %).
  - §6 : « Correction d'une affirmation que j'avais publiée quelques heures plus tôt » —
    j'avais écrit que `normal_grid_path` « n'est pas lue » ; elle l'est, mon sondage passait un
    chemin inexistant, ignoré sans un mot.
  - §6 : « Correction d'un second chiffre : j'avais écrit « 182 Mo » de mémoire » → 10,40 Go.
  - §6 : mon champ nuisait parce que les `nx`/`ny` de lasagna sont un champ **2D** et que je
    forçais `z` à zéro ; l'accord à 6° n'était validé que sur x et y.
  - §9 (T1f) : « La première version de cette section concluait « 4 pas sur 5 rendent zéro,
    l'anomalie à 15 est un point isolé ». Cette lecture reposait sur **un tirage par
    réglage** » — démolie par un second tirage (pas 10 : 0 puis 4 613 ; pas 15 : 947 puis 0).
  - §9 : inverse l'hypothèse de `24` §4 (« réduire `step_size` … moins de chances de sauter ») :
    la mesure dit le contraire.
  - §9 : « On a payé ×3 pour un déterminisme qu'on n'obtient pas » — `thread_limit: 1` avait
    été posé pour réduire la variance, or `30` a mesuré que ça ne la réduit pas. Il reste le
    bon réglage, mais pour une raison de **débit** et non de déterminisme.
- **preuve de lecture intégrale** :
  - l. 459 : « ⚠⚠ **Un facteur 29 de ralentissement pour zéro déplacement, sur la course entière.** La »
  - l. 757 : « machine a un iGPU **Intel Arc**. Il n'y a pas de GPU à saturer ici. »

---

- ⚠⚠⚠ **2026-09-04, alerte de conservation** : `docs/mesures/sans_filtre.json`, la donnée du
  tableau « sans filtre », avait été **écrasée par un fichier vide** par le commit de rangement
  `a5901be` — le même qui a vidé la mesure de `34`. Restaurée depuis `79fba93` et vérifiée : les
  quatre lignes du fichier sont exactement les quatre du tableau publié. ⭐ Garde posée :
  `src/depot/mesures_videes.py` détecte la **régression** (une mesure vue pleine dans
  l'historique et vide maintenant), pas le vide — cinq mesures du dépôt sont vides depuis
  toujours et leur vide **est** le résultat.
### docs/27_ce_que_la_litterature_dit.md
- **lignes** : 692
- **nature** : PROCEDE
  (revue de littérature — trois articles primaires lus intégralement — plus, en §4, un
  registre de ce qui reste ouvert et, en fin de fichier, une bibliographie et un inventaire
  des sources, du miroir de site et des dépôts.)
- **résumé** : Trois papiers du cœur de l'équipe du concours sont lus en entier — après une
  première version du document écrite depuis les seuls résumés, qui contenait un chiffre
  faux, une paraphrase entre guillemets et une affirmation réfutée par l'un des papiers. Ils
  établissent ensemble : un rouleau scellé lu de bout en bout mais à ~25 h d'humain par
  spire ; une nappe unique garantie par construction mais avec 3,20 % de traversées de
  spire ; l'encre lisible par le seul relief à 0,34 µm mais avec une cible d'environ 1 µm.
  Le document en tire ce que chacun laisse ouvert, et ce que cela dit de nos propres
  instruments, qui n'exigent aucune vérité terrain.

  **Ce que chaque article établit, et ce que le document lui reproche :**

  **[P1] — *Ink Detection from Surface Topography of the Herculaneum Papyri*** (Angelotti,
  Nicolardi, Henderson, Seales, arXiv 2603.27698, 29 mars 2026, Scientific Reports).
  *Établit* : la morphologie de surface d'une région écrite porte assez de signal pour
  distinguer l'encre du papyrus **sans contraste d'absorption** ; c'est un signal composite
  (rugosité **plus** déformations de pression), la seule rugosité filtrée ne séparant pas ;
  la segmentation fiable demande un échantillonnage latéral de **1 µm ou plus fin**, seuls
  les modèles à 1,02 µm ou mieux dépassant DICE = 0,70 ; DICE 0,890/0,899 à 0,34 µm,
  0,754/0,758 à 1,02 µm, effondrement à 0,029 puis 0,003 pour un modèle entraîné à 0,34 µm
  et testé à 3,40 puis 5,44 µm ; la quantification verticale ne coûte au plus que 0,026 de
  DICE.
  *Reproches du document* : le corpus est de **16 lettres en 14 échantillons** sur 3 papyrus
  ouverts, régions d'~1,5 mm de côté ; les lettres sont choisies pour leur lisibilité et leur
  faible dommage ; les masques de vérité viennent d'une photographie annotée à la main, donc
  « ce papier ne révèle aucune écriture invisible » ; les surfaces sont exposées à l'air
  depuis ~200 ans ; le plateau à ~0,47 de la colonne réentraînée « n'est pas un succès » ;
  et surtout le **leave-one-papyrus-out** rend 0,757 / 0,817 / **0,475** selon le papyrus
  retiré, moyenne poolée **0,691**, donc **sous le seuil de 0,70 que le papier utilise
  lui-même** — résultat que le résumé ne met pas en avant. La transposition au CT est
  conditionnelle (les auteurs insistent sur « effective » plutôt que nominal).

  **[P2] — *Virtually Unrolling the Herculaneum Papyri by Diffeomorphic Spiral Fitting***
  (Henderson seul, arXiv 2512.04927, 4 déc. 2025, accepté à WACV 2026, code publié).
  *Établit* : première méthode descendante ajustant automatiquement un modèle de surface au
  CT d'un rouleau sévèrement abîmé ; spirale d'Archimède à un seul paramètre inconnu ω,
  composée d'un difféomorphisme à trois étages ; la garantie que la sortie est une nappe
  unique sans intersection est **topologique** et bien fondée (algèbre de Lie des champs de
  vitesse) ; l'aplatissement est gratuit (θ et z **sont** U et V) ; l'intervention humaine se
  réduit à **un bit** (le sens d'enroulement) ; 19 h sur une RTX 3090 dont 16 h de
  post-traitement ; supérieur à ThaumatoAnakalyptor en ChD (5,29 vs 5,59) et AD (0,0568 vs
  0,1567).
  *Reproches du document* : la garantie « garantit que la sortie EST une nappe, jamais que
  c'est LA nappe » — WJF **3,20 %** de traversées de spire, et aucune configuration du
  tableau d'ablations n'atteint zéro (2,77 % à 3,90 %) ; deux métriques en tension directe
  (retirer la contrainte de numéro d'enroulement améliore le WJF à 2,77 % mais fait passer le
  MRWD de 7,64 à **25,67**) ; WJF et MRWD **ne sont pas comparables au concurrent**, donc
  « personne n'a jamais comparé le taux de saut de spire de deux méthodes de traçage » ; la
  comparaison AD est probablement 0,0933 vs 0,1567 à conditions égales ; le travail humain
  **hérité** (les trois U-Net communautaires) n'est pas chiffré ; le code porte trois réserves
  écrites par l'auteur et absentes de l'article (mesure faite en espace spirale et non en
  espace rouleau, métrique biaisée par la densité de la solution, et un défaut connu non
  corrigé de la vérité terrain, qui « saute elle-même d'une spire » à la tranche 1350, avec
  un appariement choisi pour rendre les meilleures métriques) ; un mode de panne silencieux
  du MRWD (rayons complétés par répétition de la dernière valeur au lieu d'être pénalisés) ;
  les unités de MRWD et ChD ne sont jamais données ; l'exactitude dans les régions non
  détectées — le bénéfice unique revendiqué — n'est jamais mesurée ; aucun texte n'est
  transcrit ; et l'idéalisation d'une spirale d'épaisseur nulle laisse sans réponse laquelle
  des deux faces d'une bi-couche séparée porte l'encre.

  **[P3] — *Complete virtual unwrapping and reading of a rolled Herculaneum papyrus***
  (27 auteurs dont Friedman et Seales, arXiv 2606.29085, 27 juin 2026).
  *Établit* : PHerc. 1667, rouleau scellé, entièrement déroulé virtuellement et lu — 31
  spires, 1231 cm² de papyrus, ≈ 860 cm² d'écriture préservée, 22 colonnes, transcrites par
  huit papyrologues ; le protocole de scan est le morceau le plus solide (2,4 µm isotrope,
  0,22 m de propagation, 78 keV, Paganin δ/β = 1000, BM18 ESRF, ~20 To reconstruits), fondé
  sur un raisonnement de **décohérence** et validé par une campagne 4×4 énergies × distances ;
  sur PHerc. Paris 4 ce protocole rend l'encre **directement visible** dans le volume (dépôts
  de 10–20 µm) coïncidant avec la région du Banner du Grand Prize 2023.
  *Reproches du document* : le mot qui porte le titre est « rolled », pas « complete » —
  PHerc. 1667 est le plus petit et le plus abîmé des objets (8 cm de haut, 2 cm de diamètre,
  31 spires contre 19–24 cm, 4–6 cm et plusieurs centaines), son diamètre étant passé de 4,9
  à 2 cm et son poids de 14 g à ~6 g par deux siècles de tentatives destructrices ; le titre
  du traité n'est pas récupéré et 4 colonnes sur 22 sont « en traces » sans une lettre
  transcrite ; le chiffre décisif — **~25 heures d'annotation manuelle par spire** — est dans
  la sous-section la plus discrète, en une ligne, et le papier ne fait pas le produit ; il ne
  publie **aucun taux d'erreur de traçage**, ni avant ni après correction ; il n'a **aucun
  détecteur automatique d'erreur**, son seul rempart étant un masque d'approbation humain
  (« Regions judged geometrically consistent with a single sheet ») ; « sheet switches »
  n'apparaît qu'**une** fois dans tout l'article, comme mode de panne non résolu ; le
  prédicteur de surface est faible et rétrogradé par les auteurs eux-mêmes (Dice 0,308, IoU
  0,189 pour la classe surface) ; l'entraînement a été arrêté à 3 864 epochs sur 7 500 et le
  pré-entraînement DINOv2 à 342 558 itérations sur 1 000 000 ; **~20 objets ont été scannés,
  3 portent un résultat**, sans aucun compte rendu d'échec pour les quinze autres — « un biais
  de sélection non discuté » ; la visibilité directe de l'encre est ponctuelle (« under at
  least one optimized scan regime ») et ne s'étend pas à PHerc. 1667 ni 139 ; et une partie
  de la lecture vient d'un scan complémentaire à 1,129 µm, hors volume de production.
- **conclusions extractibles** :
  - Les treize rouleaux du Grand Prize sont publiés à **8,64–9,36 µm**, soit un facteur 8,6 à
    9,4 par rapport à la cible de ~1 µm de [P1], et au-delà de son point d'effondrement de
    3,40 µm ; et un facteur **3,6 à 3,9** par rapport au volume de production de [P3] à
    2,4 µm, **8 à 8,3** par rapport à son scan de secours à 1,1 µm.
  - Les volumes de surface Scroll 1 / PHerc0139 / PHerc1667 sont à **1,129 / 2,399 /
    2,400 µm** : le plus fin est au-dessus de 1,02 µm, de peu.
  - **31 spires × 25 h ≈ 775 heures**, soit ~97 jours-personne, ~4,5 mois à temps plein, et un
    débit de **1,6 cm² de papyrus déroulé par heure d'humain** (la multiplication est du
    document, pas du papier). Le Grand Prize 2027 tolère **8 heures** d'annotation humaine
    documentée : un facteur ~100.
  - Ces 775 heures ne couvrent que le déroulage — ni photogrammétrie, ni annotation des labels
    d'entraînement, ni cinq tours de pseudo-labellisation d'encre, ni les 256 voxels cliqués
    pour le prototype DINO, ni la revue par huit papyrologues ; un poste permanent de
    direction des annotations est occupé sans interruption depuis mai 2023.
  - Les distances opérationnelles de propagation par taille de pixel : **0,22 m à 2,4 µm,
    ~0,5 m à 4,6 µm, ~2 m à 8 µm**.
  - Nos instruments (auto-intersection, profondeur) n'ont besoin d'**aucune vérité terrain**,
    contrairement à WJF, `winding_error_fraction` et aux métriques de niveau voxel — ce qui
    les rend utilisables sur les treize rouleaux du prix, dont aucun n'a de maillage de
    référence.
  - Une méthode dont la sortie est *garantie* propre produit quand même 3,2 % de traversées :
    un contrôle qui ne regarderait que la topologie déclarerait cette sortie parfaite.
  - Le mode d'échec change de forme, pas de nature : ascendant = saut discret, fragment,
    recollage faux ; descendant = dérive lisse. `12` et `25` §5 ne sont donc pas redondants
    avec `03`/`24`.
  - `pmh47/spiral-fitting` a reçu un prix de **30 000 $** du concours et n'était pas dans
    `tools/repos.tsv` ; `tools/repos.tsv` porte le manifeste de **44 dépôts** en quatre
    niveaux ; le miroir local du site couvre **81 pages sur 81**.
- **rétractations / corrections internes** :
  - En-tête : « Première version de ce document : écrite depuis les RÉSUMÉS. Elle contenait un
    chiffre faux (« cible de 4 µm », §1), une citation qui était une paraphrase entre
    guillemets, et elle reprenait à son compte une affirmation de `00` que le papier de
    Henderson **réfute avec un nombre** (§2). »
  - §1, correction du 2026-08-19, deuxième passe : le « 4 µm » « n'est **nulle part dans le
    papier** » ; la cible est de ~1 µm (1,02 µm au tableau 1), « quatre fois plus fine — ce
    qui change la conclusion, pas seulement le chiffre ».
  - §1 : la première version donnait une **paraphrase entre guillemets** du résumé, « ce qui
    est une faute de citation » ; la phrase exacte est rétablie.
  - §1 : renvoi corrigé — « notre **`13` H2** (⚠ pas `12` §H2 : ce document n'a pas de section
    H2) ».
  - §2 : « La garantie est TOPOLOGIQUE, et ce n'est pas ce que `00` en disait. »
  - §2 : la comparaison AD est probablement **0,0933 vs 0,1567** et non 0,0568 vs 0,1567, à
    conditions égales (SLIM des deux côtés) — l'avantage tombe de ×2,76 à ×1,68.
  - §4 : trois entrées marquées **périmées** — `06` §2.3 (clos par `18` M1 sans l'ombilic,
    1,75 % contre un cv de 1,8 %), `06` §3bis C (fait quatre fois, `19` §11), `06` §3bis D
    (la réponse est **NON**) ; et l'item 2 marqué ✅ FAIT.
  - §4 : « Cette phrase disait « les trois « périmés » sont corrigés **ci-dessous** » — et
    c'était la dernière ligne du fichier, donc rien ne suivait. » Le renvoi était faux, pas le
    travail.
  - Références : le quatrième papier (EduceLab-Scrolls, arXiv 2304.02084), d'abord annoncé
    « non lu ici », est marqué ✅ lu le 2026-08-19 (v3) → `32`.
  - Références : « `pmh47/spiral-fitting`, le code de [P2], n'est **PAS** dans le manifeste. À
    ajouter. »
  - §1 : la version lue de [P1] est le preprint v1, dont le champ *Comments* dit « currently
    under review » — la version de revue peut différer.
- **preuve de lecture intégrale** :
  - l. 426 : « virtuellement et lu**. 31 spires, **1231 cm²** de papyrus, **≈ 860 cm²** de surface »
  - l. 691 : « `src/outils/temoins.sh`, et la chaîne complète — tests, builds, boot, parité — dans »

---

### docs/28_le_paysage_du_controle_qualite.md
- **lignes** : 198
- **nature** : MIXTE
  (dominante inventaire — position officielle, outils `villa`, paysage communautaire,
  soumissions refusées, conventions — mais le §4 rapporte des seuils mesurés par un tiers et
  le §7.3 rapporte le résultat d'un test de mutation exécuté sur notre propre outil le jour
  même.)
- **résumé** : Recensement de ce qui existe en contrôle qualité de trace, avant d'en écrire
  un de plus, avec une séparation explicite entre ce qui a été vérifié de visu dans les
  clones et ce qui vient de l'API GitHub et de lectures de README. Le fait central est écrit
  par un auteur indépendant : la docstring de `find_sheet_switches` de `tifxyz-surgeon`
  déclare qu'**aucun test purement géométrique** ne peut séparer un saut d'une spire d'une
  courbure sur un enroulement serré — ce qui désigne notre axe (lire le volume) comme le
  complément nommé par celui qui a épuisé l'autre. La limite symétrique est posée dans la
  foulée : en zone comprimée, l'information n'est pas dans le CT.
- **conclusions extractibles** :
  - La quasi-totalité de cet écosystème a été créée entre le **1er juin et le 3 août 2026**.
  - `/2026_open_problems` (10 juillet 2026) nomme trois défauts — *mergers*, *holes*, *sheet
    switches* — et décrit le système comme **semi-automated**, la croissance automatique ayant
    encore besoin d'inspection et de correction humaines.
  - `vc_tifxyz_selfcross` est le seul outil officiel **autonome** ; `vc_calc_surface_metrics`,
    `vc_fiber_trace_metric` et `segmentation/evaluation/metrics/` exigent tous une annotation
    ou une vérité terrain.
  - `vc_tifxyz_selfcross` a été fusionné le **2026-08-04** (PR #1303) par un contributeur
    communautaire, l'auteur de `windcheck`.
  - Sa thèse : aucun seuil de distance ne sépare les bonnes traces des mauvaises, alors qu'une
    auto-intersection transverse est « un défaut sans lecture innocente, et sans seuil à
    débattre ». Ses deux limites sont écrites : « not a general statement of surface quality »
    et « They rank severity; they do not count places. »
  - `vc_tifxyz_selfcross.cpp:79` pose `--maxedge` à **60 voxels** par défaut et écarte les
    quads dont une arête dépasse : un trou peut fabriquer des croisements, et le filtre qui
    l'évite peut en masquer. Les 240 croisements de `24` n'ont jamais été relus sous un autre
    `--maxedge`.
  - `find_sheet_switches` (`src/tifxyz_surgeon/detect.py:339`) déclare : « a minimal one-wrap
    switch on a tight winding is not [caught], and no geometry-only test can separate it from
    bending » ; sur segments serrés l'écart entre spires (18–58 vx) est à peine plus large
    qu'une cellule de grille (20 vx).
  - Son seuil est mesuré : sur 14 segments propres la dérive de pointe va de **0,46 à 2,00
    cellules** et ne croît pas avec la fenêtre (5 à 150 colonnes), le pire segment abîmé
    atteignant **10,7** — d'où une barre plate à 4 cellules.
  - Limite symétrique (`villa#191`) : sur **200 points de vérité en région comprimée**,
    **78 %** montrent un pic unique large couvrant deux feuilles, et seulement **0,5 %** sont
    deux pics résolus. En zone comprimée l'information n'est pas dans le CT, donc un
    instrument qui lit le volume y est aveugle par construction.
  - Le paysage communautaire compte une douzaine de dépôts, tous à moins de quatre étoiles et
    tous récents (`tifxyz-surgeon`, `tifxyz-doctor`, `windcheck` 284 traces indexées,
    `vesuvius-automesh` 157 fenêtres étiquetées, `scrollfiesta_public` gate `turn_off` ≥ 5 %,
    `vesuvius-unmerge` 200 patchs, `spiralcheck`, `tifxyz-repair`).
  - Forme des soumissions : #1013 `plumbline` (signal **indirect** dérivé de la prédiction
    d'encre, 115 tests) fermé après deux mois ; #1293 `ScrollAnchor` (discontinuités
    « explicitement pas » des sauts confirmés) non fusionnée ; #1303 `vc_tifxyz_selfcross`
    (question géométrique sans seuil, réponse binaire, exit 3) **fusionnée en 24 heures**.
  - Ce qui reste libre : le saut de spire sans vérité terrain dans le cas serré ; un score de
    segment agrégé et comparable (rien n'existe, `spiralcheck` score au niveau du rouleau
    entier) ; et la comparaison inter-méthodes du taux de saut de spire, que personne n'a
    jamais faite.
  - Test de mutation exécuté le jour même (`src/tracecheck/mutation.py`) : les **sept**
    fonctions porteuses — `judge`, `planarity_map`, `_neighbourhood`, `lit_voxel`, `decode`,
    `chunk_key`, `find_surface_volume` — portent du poids ; débrancher n'importe laquelle fait
    tomber `selftest.py`. L'auteur de `tifxyz-surgeon` avait découvert que **trois de ses
    quatre détecteurs** pouvaient disparaître sans qu'aucun test le remarque.
  - La formule de la métrique Kaggle « topometrics » citée est
    `0,30·TopoScore + 0,35·SurfaceDice + 0,35·VOI`, tirée d'un commentaire d'issue.
- **rétractations / corrections internes** : aucune rétractation d'un énoncé publié
  antérieurement. Le document borne en revanche explicitement sa propre portée à deux
  endroits — en-tête (« ce qui est vérifié ici de mes yeux » vs « ce qui vient d'une recherche
  sur l'API GitHub et de lectures de README ») et §8 « Ce que je n'ai pas vérifié » (chiffres
  de corpus des dépôts communautaires non reproduits, code de la métrique Kaggle non lu, fils
  Discord non publics, branches hors-amont de **19 forks seulement** sur les 133 forks de
  `villa`). Il rapporte aussi un piège corrigé pendant l'écriture (§7.3) : le python système
  de la machine n'a pas numpy, et le script annonçait « la suite de référence est déjà rouge »
  sur une suite parfaitement verte — « le pire des diagnostics : faux, et confiant ». Enfin il
  désigne une mesure à faire sur un résultat antérieur : relire les 240 croisements de `24`
  sous un autre `--maxedge`.
- **preuve de lecture intégrale** :
  - l. 119 : « comprimée**, que **78 %** montrent **un pic unique large couvrant deux feuilles** au lieu »
  - l. 198 : « forks de `villa` a été comparée, mais les branches hors-amont de 19 forks seulement. »



Dépôt : `/home/masterlaplace/LplVesuvius`. Sept fichiers lus du premier au dernier caractère.

---

### docs/29_ce_qui_reste.md
- **lignes** : 199 (mesuré, `wc -l`)
- **nature** : PROCEDE
  (registre consolidé de travail ouvert : il replie des mesures faites ailleurs, il n'en produit aucune.)
- **résumé** : Registre daté du 2026-08-19 qui replie **525** énoncés de travail ouvert relevés dans la lecture intégrale des 34 documents du dépôt, chaque entrée portant ses sources en `fichier:ligne`. Il hiérarchise ce qui reste en six sections (le socle non prouvé, appliquer la correction, le cap papyrologique, les limites de portée, les mesures nommées non faites, ce que le registre ne remplace pas). Une grande partie des entrées a été mise à jour en place après coup, avec des ✅ et des blocs de rétractation datés du 2026-08-22 au 2026-08-28. Le document se déclare lui-même daté et faillible.
- **conclusions extractibles** :
  - Les 525 énoncés se répartissent en : limite connue 296, à faire 102, question ouverte 64, non mesuré 31, en attente 16, non publié 16.
  - « Une surface propre donne un meilleur texte » est une affirmation sur le pipeline, et elle n'est pas prouvée (`03`:137) ; personne ne l'a testée (`03`:133).
  - Les cellules que `windcheck` excise sont indiscernables, dans le CT, du papyrus qu'il garde : 52 segments, p = 0,859, delta de Cliff −0,000 (`04`).
  - Sur `PHerc1447`, à la constante corrigée, le détecteur répond : σ du positif = **76,4 %** du modèle qui marche (contre 2,4 % annoncés) et rend deux cartes étrangères, ρ = **−0,0100** (contre +0,9979).
  - Le détecteur rapporte **plus** de dispersion sur une surface qui ne peut pas porter d'encre : 0,7111 contre 0,5894.
  - Là où le détecteur atteint AUC 0,925, sa sortie a σ = **0,7712** ; c'est la référence de la condition d'entrée.
  - Les **13** rouleaux qu'on sait tracer et les **3** dont la sortie publiée porte du texte sont des ensembles **disjoints**.
  - `PHercParis4` publie **deux** prédictions du même scan à 2,4 µm, et l'appariement refuse de tirer au sort.
  - La correction appliquée (`20` §9) fait passer le pic médian de la couche 6 à la couche **30** et l'écart de **58 à 8 µm** ; le témoin de signe opposé dégrade ; le p90 passe de 68 à 72 µm.
  - « Le modèle retrouve les traits encrés » est mesuré (AUC 0,92, `08`) ; « le texte est lisible » ne l'est pas.
  - Trois juges mécaniques ont échoué à remplacer l'expert ; le score structurel sur segment entier échoue définitivement, un segment de ce type ne portant que 4 à 5 lignes.
  - `PHerc1203` : planéité **19,84 cm²**, voisinage **9,60 cm²**, 0 auto-intersection des deux côtés ; la campagne appariée passe de 12 à **13 rouleaux** et le résultat se renforce de 10/12 p = 0,0386 à **11/13 p = 0,0225**.
  - Protocole « sélectionner sur un axe, valider sur l'autre » : **1 accord sur 8**, là où le hasard en donnerait 4 (`37`).
  - Le rendu impose un plafond proportionnel à sa profondeur : **13 traces sur 16** butent dessus au rendu le moins profond ; le critère `au_bord` dérive quand même (médiane **0,075**, max **0,450** entre les rendus 21 et 41).
  - Nos traces n'ont aucune feuille à portée : la distance mesurée suit la fenêtre (α = **+1,01**) là où un segment officiel ne bouge pas (α = **+0,00**), et à quatre spires de portée le pic n'a rien trouvé.
  - Relever le plafond de 120 à 400 générations sur deux rouleaux plafonnés fait passer la dispersion médiane de **0,55 % à 86,00 %** (facteur 156) et les tirages sales de **1/12 à 9/12** ; à plafond relevé une trace atteint 40 min.
  - Échéance Progress Prize : **31 août 2026, 23 h 59 Pacific** (`15`:3) ; le reste vise le 25 juin 2027.
  - La règle de `19` ne réplique pas hors de Scroll 1 : sur Scroll 5, rho −0,217, p = 0,12.
  - Le « 240 → 0 » de `24` ne réplique pas : zéro auto-intersection des deux côtés sur 12 rouleaux.
  - Sur Scroll 4 rien n'est lisible et la cause est en amont du modèle : **61 %** des pics au bord de la pile.
  - L'inventaire des treize : **dix** sans segment, pas treize.
  - `step_size` a un plancher ≥ 20 : un pas de 5 rend ~800 croisements/cm² sur les deux graines ; entre 10 et 15 le résultat se contredit avec lui-même.
  - Un compte de croisements n'est pas comparable entre deux pas : le même maillage décimé sans changement de géométrie passe de 240 à 123, 72, 49.
  - Un verdict « propre » peut sortir sur zéro paire testée, au réglage `--maxedge` par défaut, dès que le maillage a un pas ≥ 60.
  - Le classement des treize rouleaux n'existe pas : rho de Spearman **−0,297** entre deux échantillonnages, treize rangs changés, le témoin passe de 0 % à 4 %.
  - Le traceur est un tirage : 4 rouleaux sur 12 où le verdict bascule à paramètres identiques, 0 reproductible, et l'aire ne signale pas le mauvais tirage.
  - Quatre segments publiés d'un même rouleau : 18,2 / 25,0 / 62,5 / 68,2 % de pics dans le tiers central — « officiel » n'est pas synonyme de « bon ».
  - L'origine de nos piles de rendu est bonne : sur le même segment officiel, 3,00 µm côté publié, 17,28 µm côté nous.
  - En zone comprimée l'information n'est pas dans le CT : **78 %** de pics uniques couvrant deux feuilles (`villa#191`).
  - Aucun test géométrique ne sépare un saut d'une spire d'une courbure dans le cas serré : écart inter-spires 18–58 vx contre 20 vx de cellule.
  - M1bis : 78 tirages, 13 rouleaux, **5 rouleaux où le verdict bascule**, 0 reproductible, taux **6,4 %** IC [2,1–14,3 %].
  - `PHerc1447` rend **σ = 0,6558**, soit **1,2×** le témoin.
  - Fenêtre large sur les quatre surfaces publiées : **8 fenêtres périodiques sur 12** contre **0** pour leur mélange, p = **0,0007**.
  - Les six fragments du layout `fragments/` portent **7 paires qui isolent l'énergie** (même objet, même pas de 3,24 µm, 54 contre 88 keV) et **2 qui isolent la résolution**.
  - Sur cinq rouleaux, **zéro rouleau mesurable** : quatre sans étiquette d'encre publiée, `Scroll1` avec des étiquettes qui sont son jeu d'entraînement ; seuls **4 fragments** sont mesurables.
  - σ ne prédit pas la qualité mesurée : quatrième sur six, p de Holm **0,739** (`65`).
  - M7 : sur **190 cartes d'encre publiées**, épaisseur de trait **AUC 0,857**, netteté du pic **0,753**, séparation des lignes **AUC 0,319**, ρ = **−0,281**.
  - M7 §7 : sur 23 tuiles étiquetées de `Frag1`–`Frag3`, **aucune** des cinq grandeurs ne survit à la correction de Holm.
  - M8 : σ du contrôle positif **0,5894** (76,4 % du modèle qui marche), ρ = **−0,0100**, σ du négatif = **0,7111**.
  - Second témoin sans feuille : graine tirée par l'outil, α = **+0,99**, **13,89 cm²** ; `PHerc1447` rend **8/12** fenêtres périodiques contre **1/7** pour les deux témoins, Fisher `[8, 4, 1, 6]`, p = **0,0399** ; une seule fenêtre renverserait le résultat (0,1299 ou 0,0799 selon le sens).
  - M4, branche « plus épais », réfutée deux fois : de 61 à 121 couches sur `PHerc0358` le pic reste au bord et l'écart suit la demi-fenêtre, **262 → 562 µm** ; et une fenêtre deux fois plus épaisse coûte **40,8 %** de la réponse du modèle d'encre.
  - M5 impossible : `PHerc0172` ne publie que du 7,91 µm.
  - Le pas du témoin de `58` était noté 2,4 µm et vaut **7,91 µm** ; il est déjà à **9 %** des conditions de `PHerc1447` sur les deux axes, et dix fois cet écart ne rendrait qu'un facteur **2,1** sur les **45** à expliquer.
- **rétractations / corrections internes** :
  - §1 : bloc « ⚠⚠⚠ **CONDITION LEVÉE LE 2026-08-28** » — le paragraphe qui disait que l'aval était aveugle sur `PHerc1447` et qu'aucune réparation ne pouvait y montrer de gain reposait sur la mesure du 2026-08-22 faite avec une constante fausse ; refaite, elle dit l'inverse (σ 76,4 % au lieu de 2,4 %, ρ −0,0100 au lieu de +0,9979). Le lot est rouvert.
  - §3bis N1 : « `PHerc1203` n'a jamais eu de graine cherchée » barré, fait le 2026-08-22.
  - §3bis N4 : « choisir une référence défendable » barré — la question se dissout, il faut un critère auto-référentiel.
  - §3bis N5 : la formulation « à 311 µm de leur feuille » est explicitement rejetée au profit de « aucune feuille à portée ».
  - §3bis N3 : « la dispersion d'aire n'est pas expliquée » barré, mesuré le 2026-08-22 — la stabilité était une troncature.
  - §4 : `15` se déclare lui-même périmé sur deux points (`15`:153, 175) : la règle de `19` ne réplique pas hors de Scroll 1, et le tri de ce qui est soumissionnable est à refaire, avant l'envoi.
  - §6 M1ter : rouvert le 2026-08-27 ; la réponse négative reposait sur un σ qui mesurait notre échelle et non le rouleau. Le texte annulé du 2026-08-20 (« σ 45 fois plus petit ») est conservé en clair, précédé de « *Ce qui suit est le texte annulé du 2026-08-20 :* ». La sous-clause « Il ne reste que CE ROULEAU-CI » est barrée et déclarée non testable avec le corpus publié.
  - §6 M7 : « Reste : le transport vers une région sans vérité du même objet » barré — répondu négativement le 2026-08-28.
  - §6 M8 : « ⚠⚠⚠ **TOUT CE QUI SUIVAIT ÉTAIT LA SIGNATURE D'UN BUG** » — les affirmations « le détecteur est inerte sur ce rouleau (σ = 0,0129, soit 1,7 %) » et « ρ = +0,9979 » sont annulées ; elles venaient de la constante de normalisation corrigée par `60`. « Reste : le contrôle typographique sur ce témoin » est barré, fait le 2026-08-28.
  - §6 M4 : branche « plus épais » fermée le 2026-08-27, déclarée non seulement inutile mais nuisible.
  - §7 : le registre se déclare daté du 2026-08-19 et prévient qu'« une entrée close ailleurs et pas ici devient un piège ».
- **preuve de lecture intégrale** :
  - ligne 143 (72 % du fichier) : `⚠ **Échéance : 31 août 2026, 23 h 59 Pacific** (`15`:3). C'est la seule date courte ;`
  - ligne 199 (dernière ligne non vide) : `lui comme au reste : corriger sur place, en disant ce qui était écrit avant.`

---

### docs/30_le_traceur_est_un_tirage.md
- **lignes** : 148 (mesuré)
- **nature** : RESULTAT
- **résumé** : Campagne de quatorze tirages de `vc_grow_seg_from_seed` à paramètres strictement identiques et même graine, sur `PHerc0358`, dépouillée par `src/tables/table_thread_limit.py`. Elle établit que le traceur n'est pas reproductible : 13 tirages propres sur 14, une aire allant de 5,69 à 10,34 cm². Le document est explicitement structuré en « ce que ça coûte » (deux explications causales tombent) et « ce que ça rapporte » (l'échantillonnage devient une méthode). Il ouvre son texte en rappelant que les repères ⭐ marquent ce qui compte, pas ce qui va bien.
- **conclusions extractibles** :
  - Quatorze tirages, paramètres strictement identiques, même graine : **13 tirages propres sur 14**.
  - L'aire va de **5,69 à 10,34 cm²**, une étendue relative de **53,5 %** à paramètres identiques.
  - Le maillage archivé de `24` remesure **240 auto-intersections**, exactement ; la mesure est fidèle.
  - Maillage de `24` archivé : aire **8,476817 cm²**, **240** auto-intersections ; tirage `tl=1 r=4`, mêmes paramètres : aire **8,477096 cm²**, **0** auto-intersection. Soit **0,003 % d'écart d'aire** et deux verdicts opposés.
  - `thread_limit` n'explique pas l'écart : le mauvais tirage est arrivé à 0, les quatre tirages à 1 sont propres, et dix tirages à 0 le sont aussi.
  - Taux mesuré : **2 mauvais tirages sur 15** (les 14 plus l'archivé), soit ~13 % ; avec trois tirages la probabilité d'en avoir au moins un propre est ~99,8 %, *si* les tirages sont indépendants.
  - Une trace coûte **~14 s** ; le juge du dépôt coûte **0,05 s**, sans vérité terrain.
  - Les tableaux d'ablation de la littérature donnent une ligne par configuration, sans répétition ni barre d'erreur (`27` §2), et le papier du déroulage complet ne publie aucun taux d'erreur de traçage (`27` §3).
  - L'équipe du concours corrige à la main **~25 h par spire** (`27` §3).
- **rétractations / corrections internes** :
  - §3.1 : le diagnostic causal de `24` §4 (la trace couperait les spires parce que le traceur n'a reçu aucune information d'orientation) est déclaré faux ; il tombe une seconde fois ici.
  - §3.2 : l'explication de rechange de `25` §4bis (plafond d'occupation, `occup. = 1,000`, tenseur nul) tombe aussi — la graine est toujours dans le même bloc plein et produit une trace propre 13 fois sur 14. Ce qui reste vrai de `25` est explicitement isolé : le critère de planéité fait aller plus loin, 11 fois sur 13, p = 0,0225.
  - §3.3 : autocritique de méthode — « Un seul tracé n'est pas une mesure. Nous avons construit deux documents sur un tirage unique, et deux explications causales dessus. »
  - §5 : la cause de la non-reproductibilité n'est pas identifiée ; l'hypothèse concurrente « la prédiction distante a changé entre le matin et le soir » n'a pas pu être écartée proprement (l'interrogation S3 de la date de modification n'a rien rendu) ; 14 tirages ne font pas une distribution ; rien ne dit qu'une trace propre est une bonne trace.
- **preuve de lecture intégrale** :
  - ligne 104 (70 % du fichier) : `Le taux mesuré : **2 mauvais tirages sur 15** (les 14 d'aujourd'hui plus l'archivé),`
  - ligne 147 (dans les 15 dernières lignes non vides) : `vc_tifxyz_selfcross --surface data/artefacts/PHerc0358/mesh.tifxyz -o /tmp/recheck.json`

---

### docs/31_roadmap.md
- **lignes** : 345 (mesuré)
- **nature** : PROCEDE
  (feuille de route ; les chiffres qu'elle porte sont cités d'autres documents, plus un cadrage d'auteur ajouté le 2026-08-29.)
- **résumé** : Deuxième version de la roadmap, écrite après recadrage de l'auteur : le Grand Prize n'est pas un problème de lecture mais une chaîne géométrique automatique et exécutable, et les 775 heures d'annotation de l'état de l'art sont la cible à supprimer, pas une barrière. Le document lit le règlement mot pour mot, énumère le capital technique déjà prouvé dans LplPlugin/LplKernel (représentation en index d'enroulement, streaming borné, déterminisme bit-à-bit), décrit la chaîne étage par étage avec ce qui manque à chacun, puis pose un calendrier et quatre façons dont la roadmap peut se tromper. Un §8 bis ajouté le 2026-08-29 sépare explicitement l'étage géométrie de l'étage lecture.
- **conclusions extractibles** :
  - Le règlement exige 100 % du recto déroulé, tolère de sauter des patches externes déconnectés s'ils font *« less than 10 % »*, demande au moins **70 %** des caractères préservés lisibles par colonne comptée, et tolère jusqu'à **8 heures documentées** d'intervention humaine.
  - Le règlement demande une image Docker que l'équipe puisse lancer facilement, avec les besoins système.
  - L'état de l'art a déroulé un rouleau avec **775 heures d'annotation**.
  - Le papier de juin 2026 mesure que le modèle d'encre du Grand Prize 2023 généralise en *zero-shot* à des rouleaux non vus.
  - L'équipe déclare : *« No method yet traces a complete, correct surface through a scroll automatically »*.
  - Le papier de juin 2026 donne **20 To par volume reconstruit**, jusqu'à **100 To bruts**.
  - `math::ReliefMosaic` + `ReliefStreamer` : résidence bornée, 64 tuiles max, aucune allocation ; Terre entière = 1,78 To à 30 m, niveau grossier en **27 Mo**.
  - `harvest::CatalogueStream` : **11,9 Go projetés → 7 Mo de RSS**, plat de 4 à 256 tuiles, 19,6 M de lignes en 79 s.
  - `harvest::MappedFile` : interroger **3,71 Go** en **220 Ko** de RSS anonyme, sous un cgroup de 512 Mo qui tue une allocation de 1 Gio.
  - LplKernel porte **vingt et une portes de parité (P6 à P21)** exigeant un calcul bit-identique entre oracle Linux et noyau i686.
  - `24` a prouvé que le volume de **893 Go** n'a jamais besoin d'être téléchargé.
  - `vc_tifxyz_selfcross` est officiel depuis le **4 août**.
  - Conventions de `28` §7 : point collection JSON rechargeable dans VC3D, code de sortie 3 pour « défaut trouvé » et 1 pour « erreur ».
  - Étage « choisir où commencer » : `trouver_graine.py`, critère de planéité, répliqué sur 13 rouleaux (p = 0,0225).
  - Étage « couvrir 100 % » : la chaîne tient **5,76 mm** et glisse hors de la feuille connue (**−69 µm**, **73 %** du même côté) sans y sauter (`44`).
  - Henderson, dans son propre code : *« Gross excursions are caught; a minimal one-wrap switch on a tight winding is not, and no geometry-only test can separate it from bending. »*
  - Henderson paramètre sa déformation comme l'intégrale d'un champ de vitesse lisse, ce qui la rend difféomorphe par construction ; un difféomorphisme ne peut pas créer d'auto-intersection.
  - Le transfert de spire à spire (*« wrap by wrap copy tool »*) est là où les **~25 h par spire** sont dépensées, en correction manuelle.
  - `villa#191` mesure que **78 %** des points de vérité en région comprimée montrent un pic unique large couvrant deux feuilles ; l'information n'est pas dans le CT.
  - Cible d'échelle : **31 spires × 1231 cm²**.
  - `33` mesure que la campagne de `16`, à 15–35 fenêtres, ne sépare aucune paire ; la campagne dense a inversé le classement (rho **−0,297**, treize rangs changés).
  - Plancher de bruit chiffré (`64`, 2026-08-28) : l'AUC d'une tuile de 256 px varie d'un écart-type de **0,2243** d'une tuile à l'autre du même objet au même réglage ; établir un écart de 0,05 en demande au moins **316** tuiles par condition, un écart de 0,10 en demande **79** — et ce sont des minorants, la formule supposant des tuiles indépendantes.
  - Progress Prize : **20 000 $/mois**.
  - `30` : quatorze tirages, treize propres, un à **79** croisements, un maillage archivé à **240** qu'aucun tirage ne reproduit, aires de **5,69 à 10,34 cm²**.
- **rétractations / corrections internes** :
  - En-tête : « ⚠⚠ **Deuxième version, après recadrage de l'auteur.** La première traitait le Grand Prize comme un problème de **lecture** et le déclarait hors de portée […] C'était à l'envers ».
  - En-tête : renvoi explicite vers `55` pour « par quoi continuer » — ce document-ci ne dit que ce que le projet vise.
  - §10 : `15` se déclare périmé sur deux points, à refaire avant l'envoi et pas après.
  - §11.2 : la mesure de compressibilité rouleau par rouleau est déclarée pas encore faisable assez finement — aux effectifs de `16`, aucun des treize n'a d'intervalle qui exclut d'être sous 10 % ni au-dessus, donc la question n'a de réponse pour aucun rouleau ; et le rouleau par lequel commencer n'est pas celui que `16` désignait.
  - §9 : la question « corriger sert-il à quelque chose ? » reste non tranchée et commande tout le reste ; §7 nomme trois choses à vérifier avant de croire au gauchissement.
  - §8 bis (ajout du 2026-08-29) : corrige une façon de lire tout le dépôt — un « non, pas de lettres » n'invalide pas les mesures de géométrie.
- **preuve de lecture intégrale** :
  - ligne 235 (68 % du fichier) : `> **Qu'est-ce qui remplace l'humain qui corrige le transfert de spire à spire ?**`
  - ligne 343 (dans les 15 dernières lignes non vides) : `4. ⚠⚠ **Si le temps de calcul explose** : 31 spires × 1231 cm², plus N tirages par spire,`

---

### docs/32_educelab_le_papier_fondateur.md
- **lignes** : 220 (mesuré)
- **nature** : PROCEDE
  (lecture d'un article primaire — revue de littérature — assortie de deux mesures nommées à faire ; un seul calcul dérivé y est produit, et il est explicitement signalé comme n'étant pas du papier.)
- **résumé** : Lecture intégrale de *EduceLab-Scrolls* (Parsons, Parker, Chapman, Hayashida, Seales, arXiv 2304.02084, v3 du 30 octobre 2023), la mesure M3 de `29`. Le document extrait ce que l'article établit (le corpus, la doctrine de vérifiabilité, six pratiques à reprendre) puis, en §4, les contrôles que l'article n'a pas faits : la précision d'alignement jamais mesurée, le contrôle « consistent with » nommé mais jamais outillé, l'absence de contrôle négatif fort alors que le témoin parfait était dans les données, et un critère d'acceptation sourcé à un reportage télévisé. Deux mesures en sortent, M7 et M8, toutes deux marquées faites depuis.
- **conclusions extractibles — ce que l'article établit** :
  - Entraînement labellisé : **16 scans de 6 fragments issus de 4 rouleaux** ; rouleaux intacts : **9 scans couvrant 4 rouleaux** ; total disque **11,5 To** ; **55,8 Go** suffisent pour reproduire le papier (les seuls *surface volumes*) ; licence **CC BY-NC 4.0**.
  - `P.Herc.Paris. 4` (Scroll 1) a été scanné à Diamond Light Source, ligne I12, en 2019, à **7,91 µm**, en deux moitiés (le rouleau dépassait la course du portique, d'où un cric de laboratoire manuel). Les fragments labellisés sont à **3,24 µm**.
  - Défaut déclaré : par une erreur de calcul de la position projetée de l'axe de rotation, un cylindre de diamètre **≈4,8 mm** au cœur de `P.Herc.Paris. 4` n'est pas représenté dans les images de projection ; le trou est toujours là.
  - Le mot `volpkg` n'apparaît nulle part dans ce papier, ni « segment » au sens du concours ; ce sont des conventions de Volume Cartographer.
  - La vérifiabilité est une propriété du jeu de données, pas de la méthode : des fragments détachés dont la surface est photographiée en infrarouge, dans une autre modalité, par un autre laboratoire (BYU), vingt ans plus tôt.
  - *« recall higher than the false positive rate by a factor of 8 »* — un rapport plutôt qu'un seuil.
  - F0.5 : β = 0,5 inscrit dans la métrique qu'un faux positif coûte plus cher qu'un faux négatif.
  - Le sens de l'erreur est choisi en amont : *« This slight preference for false negatives is deliberately chosen … as false positives … can bias the subsequent meshing step »*.
  - µ et σ sont pris sur la seconde moitié de **620 000** batches d'entraînement, jamais le meilleur point de contrôle.
  - Notation stricte contre soi-même : même les caractères jugés incertains par le papyrologue sont notés, et le papier dit que les exclure améliorerait encore les résultats.
  - Le juge humain est calibré par transcription appariée : un papyrologue qui n'a jamais vu les fragments transcrit la sortie, puis le même expert transcrit la vérité terrain, et on compare transcription contre transcription.
  - Épaisseur d'encre estimée **5–10 µm**, d'où l'argument physique qu'il faut un voxel qui l'approche.
  - Phrase de 2023 qui décrit le signal exploité par tout le domaine : *« a much more subtle signal … likely relating not only to image intensity but to morphological (texture, or shape) differences between ink and blank papyrus »*.
  - Performance déclarée périmée : recall caractère **0,42**, donné par le papier *« primarily as a benchmark against which future improvements can be evaluated »*.
  - FPR rapporté : **0,051**.
- **conclusions extractibles — les contrôles reprochés au papier** :
  - La précision de l'alignement photo IR ↔ scan CT n'est **ni mesurée, ni bornée, ni validée** : aucune erreur en pixels ou microns, aucun RMS sur les points d'appui, aucune validation croisée, aucune étude de sensibilité. L'alignement est manuel (Photoshop *Puppet Warp*) parce que l'automatique a échoué : *« we have not yet discovered an automated method that is capable of successfully aligning the texture and infrared images. »* Le papier se contente de *« Since the label alignment is a manual process, some small error can be assumed. »*
  - L'erreur est traitée par évitement : dilatation de rayon **16** autour des contours du label, seul chiffre du papier qui encode l'incertitude d'alignement, choisi empiriquement. (Calcul dérivé, signalé comme n'étant pas du papier : à 3,24 µm, 16 pixels ≈ **52 µm**, soit 5 à 10 fois l'épaisseur d'encre estimée.)
  - L'exclusion est appliquée à l'entraînement et **pas à l'évaluation** : les métriques sont calculées sur toute l'image, frontières comprises, donc elles mesurent en partie le bruit de la référence.
  - Le seul contrôle sans vérité terrain — *« the scale, line separation, and script of the revealed characters are consistent with those observed on the fragment surfaces »* — est laissé au jugement de l'œil : ni l'échelle, ni l'interligne, ni le trait ne sont mesurés, alors que les trois sont mesurables sans connaître le contenu (interligne par autocorrélation, échelle par tailles de composantes connexes, taux de couverture, épaisseur de trait par distances au squelette).
  - Aucun contrôle négatif au sens fort : le FPR de 0,051 est mesuré sur des images qui contiennent de l'encre partout autour ; le papier ne mesure jamais ce que le détecteur produit sur un substrat dont on sait qu'il ne porte pas d'encre.
  - Le témoin parfait existe dans le même scan — la feuille de papier de support (*« the paper fibers are visible on the backing sheet to which the fragment is mounted »*), substrat fibreux, même session, même voxel, même fenêtre d'intensité — et le pipeline le supprime : *« These are removed manually, by selecting and deleting the extraneous points. »*
  - Autres contrôles absents et constructibles : papyrus vierge, étiquettes permutées, volume désaligné (décaler le recalage de N pixels donnerait la sensibilité au désalignement), second annotateur (variance de la vérité terrain), second papyrologue — **un seul** expert a jugé les **125** caractères, aucun accord inter-juges.
  - Le critère d'acceptation le plus haut (*« To be readable, letters should form lines with uniform and expected scale, spacing, and margins »*) est sourcé à `60minutes`, un reportage, et n'est jamais opérationnalisé.
- **rétractations / corrections internes** :
  - En-tête : une **v4** du papier existe (20 mai 2024) ; c'est la **v3** qui a été lue.
  - §1 : correction de vocabulaire vérifiée — `volpkg` et « segment » au sens du concours ne viennent pas de cet article.
  - §4.2 : le texte inclut une insertion tardive « ✅ **CONSTRUIT** — la ligne 143 juste en dessous le dit », qui corrige en place la phrase annonçant un instrument à construire.
  - §4.2 / §6 M7 : le résultat mesuré contredit partiellement le papier — épaisseur de trait AUC 0,857, netteté 0,753, mais séparation des lignes **0,319**, à contre-sens ; « La phrase du papier réunit trois propriétés qui, mesurées, ne vont pas ensemble. »
  - §4.3 / §6 M8 : marqués faits ; le témoin négatif a été **refait le 2026-08-28** après correction d'échelle, et le détecteur répond **plus fort** sur la surface sans feuille.
  - §5 : « ⚠ La partie “périmé” de ce paragraphe engage des connaissances du domaine hors du papier ; elle est à recouper avec `27` et `28` ».
- **preuve de lecture intégrale** :
  - ligne 151 (69 % du fichier) : `Le papier n'a **aucun contrôle négatif au sens fort**. Il rapporte un FPR de 0,051, mais`
  - ligne 220 (dernière ligne non vide) : `  — il est déjà acquis, dans les mêmes conditions.`

---

### docs/33_la_carte_nest_pas_resolue.md
- **lignes** : 195 (mesuré)
- **nature** : RESULTAT
- **résumé** : Relecture des artefacts versionnés `docs/carte_separabilite/*.json` par `src/commun/incertitude_carte.py`, sans acquisition de donnée nouvelle, pour mesurer l'incertitude du classement des treize rouleaux que `16` avait publié sans barre d'erreur. Le résultat annule le classement : aucune des 78 paires n'est séparée, aucun rouleau ne se distingue du témoin après correction de Holm, et le zéro du témoin est compatible avec un taux réel jusqu'à 14,2 %. Le §3 calcule qu'il faut 50 fenêtres par rouleau ; le §4bis rapporte que la campagne dense a effectivement tourné le même jour et confirme la prédiction, avec un rho de Spearman de −0,297 et treize rangs changés.
- **conclusions extractibles** :
  - Rouleaux distinguables du témoin après correction de Holm : **0 sur 13** ; au seuil nominal sans correction : **5 sur 13**.
  - Paires de rouleaux réellement séparées : **0 sur 78**.
  - Intervalle du mieux classé, `PHerc0358` (1/28) : **0,1 % – 18,3 %**.
  - Intervalle du témoin, `PHerc0139` (0/24) : **0,0 % – 14,2 %** — au-dessus de la part observée de huit des treize rouleaux.
  - Les cinq p nominaux vont de **0,014 à 0,028**, exactement la zone que treize essais produisent tout seuls.
  - Ce qui tient : les treize pris ensemble, **42/300 = 14,0 %** contre **0/24**, p = **0,031** ; et **13 sur 13** ont une queue au-dessus de celle du témoin.
  - Le p groupé de 0,031 est une borne basse : les 300 fenêtres sont groupées par rouleau, donc l'effectif effectif est plus petit que 300 et le vrai p est plus grand.
  - Puissance exacte à séparer 3,6 % de 23,8 %, par énumération des (n+1)² tables : 25 fenêtres → **39 %** ; **50 → 80 %** ; 100 → **99 %** ; 200 → **100 %**.
  - Les paires du milieu (`PHerc0257` à 10,5 % contre `PHerc1545` à 11,8 %) resteront hors de portée à tout effectif raisonnable.
  - Séparer un rouleau du témoin — 0 % contre 3,6 % — demande des milliers de fenêtres.
  - La part mesurée est une fraction de **fenêtres sondées**, celle du prix une fraction de **surface de recto** : deux grandeurs différentes.
  - Aucun des treize n'a un intervalle qui exclut d'être sous 10 %, et aucun n'a un intervalle qui exclut d'être au-dessus.
  - Campagne dense (57 à 115 fenêtres par rouleau) : **rho de Spearman = −0,297**, **13/13 rouleaux changent de rang**.
  - `PHerc0358` passe de **3,6 % (1ᵉʳ)** à **12,8 % (6ᵉ)**, écart **+9,2** ; `PHerc0800` passe de **20,0 % (10ᵉ)** à **2,6 % (1ᵉʳ)**, écart **−17,4**.
  - À échantillonnage dense, le témoin `PHerc0139` mesure **4 %** et non 0 %.
  - **12 des 13** estimations denses tombent dans l'intervalle de la campagne creuse : le sondage creux n'était pas biaisé, il était bruité ; le seul rouleau hors intervalle est `PHerc0800`.
  - À 57–115 fenêtres, **1 paire sur 78** est séparée et **1 rouleau sur 13** se distingue du témoin.
  - Le dépouilleur `src/encre/comparer_cartes.py` avait ses seuils d'interprétation posés d'avance : rho > 0,7 réfute ce document, rho < 0,3 le confirme.
- **rétractations / corrections internes** :
  - §1 et §4bis : la phrase de `16` — *« le témoin a une propriété qu'aucun des treize ne partage : 0 % »* — est déclarée décrire une observation et non une propriété, puis démentie par un chiffre (4 % en dense).
  - §5 : tableau de ce que ce document rend faux ailleurs — `16` §0/§6 (« c'est la queue qui sépare » comme énoncé de classement, et la désignation de `PHerc0358`), `13` H4 (« `PHerc0358` désigné »), `31` §10/§11.2 (« ça dit sur lequel des treize le prix est jouable »).
  - §5, bloc « ⚠⚠ **Mis à jour le 2026-08-20, après la campagne dense** » : `PHerc0358` n'est plus le meilleur point observé, c'est `PHerc0800` (2,6 % contre 12,8 %) ; mais rien n'oblige à changer de rouleau, puisqu'à 78 paires une seule est séparée.
  - §6 : le document ne dit pas que la carte est fausse, seulement qu'elle est sous-échantillonnée ; il ne remet pas en cause l'instrument `separabilite_scan.py`, ni le témoin apparié, ni le niveau 1 de la pyramide ; et il ne mesure pas la part comprimée en surface.
- **preuve de lecture intégrale** :
  - ligne 124 (64 % du fichier) : `> ⭐⭐ **rho de Spearman = −0,297. 13/13 rouleaux changent de rang.** Le`
  - ligne 192 (dans les 15 dernières lignes non vides) : `./src/outils/carte_separabilite.sh docs/carte_separabilite_dense 125`

---

### docs/34_un_verdict_qui_ne_mesure_rien.md
- **lignes** : 173 ⚠ (138 quand la fiche a été écrite ; la mesure de la figure a été **perdue puis restaurée** le 2026-09-04, et le document le dit)
- **nature** : RESULTAT
- **résumé** : Réponse à la mesure M2 de `29` — relire les 240 auto-intersections de `24` sous un autre `--maxedge`. La réponse directe est rassurante (les 240 survivent à la désactivation complète du filtre, donc ni masqués ni fabriqués), mais le balayage trouve davantage : un mode de panne silencieux de `vc_tifxyz_selfcross`, où « propre » et « rien mesuré » sortent par le même champ JSON. Le document mesure ensuite, par décimation d'une géométrie inchangée, ce que perd un maillage plus grossier, et impose un lecteur unique qui refuse un rapport sans paire testée.
- **conclusions extractibles** :
  - **Ajouté le 2026-09-05** : le **reproducteur minimal** de ce mode de panne (`src/tracecheck/repro_empty_verdict.py`) n'était cité dans **aucun** document — une démonstration qui existait et que personne ne pouvait lancer. Il tourne **hors ligne** (carré plat 24 × 24 au pas 20, rien à télécharger) : `--maxedge 60` → `clean` sur **12 320** paires testées, `--maxedge 19` → `clean` sur **0** paire, et `--fail-on-crossing` y sort en **0**.
  - Sur le maillage condamné de `24`, avec le filtre désactivé (`--maxedge 0`) : **240** croisements, **751 169** paires testées, **0** quad jeté.
  - À `--maxedge 30 · 40 · 60 · 80 · 120 · 200 · 400` : **240** croisements, **751 169** paires testées, **0** quad jeté — le filtre est inerte sur ce maillage.
  - À `--maxedge 20` : **0** paire testée, **48 040** quads jetés, croisements non mesurés, et le rapport dit `"clean_of_transverse_self_intersection": true`.
  - Le pas de la trace vaut **20** voxels, donc à `--maxedge 20` chaque quad a au moins une arête au-dessus du seuil.
  - Un portail bâti sur `--fail-on-crossing` avec un `--maxedge` sous le pas de la trace laisse passer n'importe quelle surface, et sort avec le code 0 que le script attend.
  - Le maillage propre apparié — même graine, mêmes paramètres, aire à 0,003 % près — rend **0** à tous les réglages.
  - Décimation (une ligne et une colonne sur *k*), défaut `--maxedge 60` / paires testées / filtre désactivé : facteur 1 (pas 20) → **240** / 751 169 / 240 ; facteur 2 (pas 40) → **123** / 32 255 / 123 ; facteur 3 (pas 60) → **0** / **0** / **72** ; facteur 4 (pas 80) → **0** / **0** / **49**.
  - Deux pertes distinctes : le maillage (240 → 123 → 72 → 49 sur une géométrie qui ne bouge pas) et le filtre (qui transforme les 72 et les 49 en zéros au réglage par défaut, sans message).
  - La règle de `26` §9 (`step_size ≥ 20`) tient : l'audit des rapports bruts montre `quads_dropped = 0` à tous ses pas et `pairs_tested` non nul partout (**36 149** au pas 40) ; aucun de ses zéros n'est un zéro muet.
  - Mais ses zéros ne se valent pas : sur une surface qui porte 240 croisements, un maillage au pas 40 n'en retrouve que **123, soit 51 %**.
  - Six scripts du dépôt lisaient le rapport sans jamais regarder `pairs_tested` ; `src/nappe/lire_selfcross.py` est désormais le seul lecteur et refuse (code 3) un rapport sans paire testée.
- ⚠⚠⚠ **2026-09-04, alerte de conservation** : la mesure de la figure
  (`docs/mesures/sensibilite_maillage.json`) a été **écrasée par un fichier vide** lors d'un
  commit de rangement, et le maillage source `artefacts/PHerc0358/mesh.tifxyz` **n'existe
  plus** — donc elle n'est pas refaisable. Restaurée depuis l'historique et vérifiée : l'image
  régénérée est **identique octet pour octet** à celle qui est publiée. Deux gardes posées
  (le script refuse d'écrire un résultat vide ; la figure le dit au lieu de lever).
- **rétractations / corrections internes** :
  - §1 : la réponse à M2 est explicitement rassurante — le verdict de `24` n'est ni masqué ni fabriqué par un réglage. Aucune rétractation d'un résultat antérieur.
  - §4 : nuance apportée à `26` §9 — la règle tient mais « zéro croisement au pas 40 » est une affirmation plus faible que « zéro au pas 20 », et l'écart est mesuré, pas supposé. La décimation est un **modèle** de la perte, pas la campagne elle-même.
  - §6 : le document n'accuse pas l'outil d'être faux ; il ne mesure pas la fréquence du cas en pratique (un seul réglage volontairement absurde l'a produit, plus les décimations construites pour ça, et aucun résultat publié n'en dépend) ; et il ne dit pas quel pas choisir.
- **preuve de lecture intégrale** :
  - ligne 84 (61 % du fichier) : `` `26` §9 conclut que **`step_size ≥ 20`** rend une trace propre, sur la foi de comptes nuls ``
  - ligne 171 (dans les 15 dernières lignes non vides) : `python3 src/nappe/lire_selfcross.py --verifier`

---

### docs/35_le_tirage_sur_douze_rouleaux.md
- **lignes** : 223 (mesuré)
- **nature** : RESULTAT
- **résumé** : Généralisation de `30` (M1bis) : la campagne couvre **treize** rouleaux et **78** tirages, six par rouleau, à paramètres strictement identiques — le nom du fichier dit « douze » et le document explique en tête que c'est l'état du 2026-08-20, gardé pour que les liens résolvent, `PHerc1203` ayant été ajouté le 2026-08-22. Elle établit que le verdict bascule sur 5 rouleaux sur 13, que l'aire ne signale pas le mauvais tirage, et — en §3bis, mesure faite le 2026-08-22 — que la faible dispersion et la propreté étaient toutes deux des artefacts du plafond de générations. Le document contient un avertissement explicite contre la sur-interprétation d'un chiffre (§3) suivi de sa vérification (§3bis).
- **conclusions extractibles** :
  - Tirages exploitables **78**, rouleaux **13**, rouleaux dont l'aire est identique sur les six tirages **0 sur 13**, rouleaux où le verdict bascule **5 sur 13**, mauvais tirages **5 / 78 = 6,4 %** (IC 95 % exact : 2,1 % – 14,3 %).
  - Les cinq basculements, croisements par tirage et dispersion d'aire : `PHerc0125` **1615**, 0, 0, 0, 0, 0 — 0,31 % ; `PHerc0257` 0, 0, 0, 0, 0, **428** — 0,24 % ; `PHerc0268` **607**, 0, 0, 0, 0, 0 — 0,33 % ; `PHerc1203` **140**, 0, 0, 0, 0, 0 — 0,63 % ; `PHerc1447` 0, 0, 0, **1371**, 0, 0 — 35,14 %.
  - Le taux de 6,4 % est compatible avec les 13 % de `30` (2 sur 15) ; l'apport est un intervalle quatre fois plus étroit et une généralité.
  - Excentricité moyenne du rang d'aire des mauvais tirages : **0,60**, contre **~0,50** attendu si l'aire ne disait rien — mais sur quatre événements, ça n'est rien. La conclusion utilisable est négative : on ne peut pas écarter un mauvais tirage en regardant sa taille.
  - Dispersion médiane : **0,3 %** chez les rouleaux qui basculent contre **12,8 %** chez les autres (facteur 43) ; par plafond, **0,5 %** contre **19,9 %** (facteur 40).
  - Association basculement/plafond non significative : **4 basculements sur 6 rouleaux plafonnés contre 1 sur 7**, test exact **p = 0,10**.
  - §3bis, plafond 120 vs 400, six tirages chacun, seul le budget change : `PHerc0125` 118–118 générations, 19,83 cm², **0,3 %**, 1/6 sales → 207–333 générations, **71,31 cm²**, **115 %**, **5/6** sales. `PHerc0191` 118–118, 19,83 cm², **0,8 %**, 0/6 → 216–283, **80,39 cm²**, **57 %**, **4/6**.
  - La dispersion médiane passe de **0,55 % à 86,00 %** — un facteur **156** : la stabilité était une troncature.
  - Les tirages qui s'auto-intersectent passent de **1 sur 12** à **9 sur 12** : la propreté aussi était une troncature ; les traces étaient propres parce qu'elles étaient courtes.
  - Troisième rouleau écarté du verdict mais nommé : `PHerc0358`, 19,83 → **211,43 cm²** (facteur **10,7**) avec **9 907** auto-intersections, sur un seul tirage.
  - Coût mesuré : à plafond relevé, le tirage de `PHerc0358` a pris **40 minutes** contre ~2 à 4 au plafond d'origine ; la campagne a été arrêtée après **treize tirages sur vingt-quatre**, les onze restants coûtant ~7 heures, et `PHerc0358` bute déjà à **386 générations sur 400**.
  - Un tirage coûte **~70 s** sur ces rouleaux, donc trois tirages ~3,5 min par départ ; le juge coûte **0,05 s** sans vérité terrain.
  - `PHerc1203` : deux graines, planéité **19,84 cm²** et voisinage **9,60 cm²**, zéro auto-intersection des deux côtés ; la campagne appariée de `25` passe de 12 à **13 rouleaux** et le résultat passe de **10/12 à p = 0,0386** à **11/13 à p = 0,0225**. Ses six tirages butent tous sur le plafond (118–118) et sa dispersion d'aire vaut **0,63 %**.
  - `PHerc1203` est l'un des deux seuls rouleaux du prix à avoir plusieurs scans, donc le seul endroit où l'appariement surface/volume par position aurait mordu.
  - Cohérence externe : `44` mesure budget 200 → **25 036** auto-intersections sur l'extension tangentielle.
- **rétractations / corrections internes** :
  - En-tête : le titre du fichier dit « douze » et c'est explicitement l'état du 2026-08-20, gardé pour que les liens résolvent ; la campagne en couvre **treize** depuis le 2026-08-22.
  - §3 : « ⚠⚠ **Ce chiffre est recalculé, il ne l'était pas.** La version du 2026-08-20 écrivait “un test exact donne p ≈ 0,55” — un nombre sans producteur dans l'arbre, donc une anecdote […] et périmé dès que le treizième rouleau est arrivé. » Le plafond est désormais dérivé de la campagne plutôt qu'écrit en dur.
  - §3 : la mise en garde « Rien n'est encore établi sur la CAUSE » porte une insertion « ⭐⭐ **LA MESURE A ÉTÉ FAITE** → §3bis […] la stabilité **était** une troncature, et l'hypothèse est confirmée. »
  - §3 : l'observation « dispersion 0,3 % chez ceux qui basculent contre 12,8 % » est explicitement désignée comme « une observation qu'il ne faut PAS transformer en résultat » — « C'est trop beau, et ça ne tient pas debout », le confond étant le plafond de générations.
  - §3bis : « ⚠ **Ce que ça ne dit pas.** Deux rouleaux au verdict, pas treize » ; et rien sur la cause du non-déterminisme.
  - §4 : le tableau porte une insertion « ⚠⚠ **Le protocole a été TESTÉ** → `37`, et le résultat est **négatif** : sélectionner sur un axe ne valide pas sur l'autre » ; le corps du §4 dit encore que le protocole honnête « reste » celui de `31` §4.
  - §5 : le manque de `PHerc1203` est barré par « ✅ **COMBLÉ le 2026-08-22**, aux deux endroits » ; le trou était en amont (`campagne_graines.sh` ne le listait pas alors que `carte_separabilite.sh` le liste) et valait aussi pour `25`.
  - §5 : limites déclarées — la campagne ne dit pas pourquoi (`30` avait écarté `thread_limit`, rien ne l'a remplacé) ; une trace propre n'est pas une bonne trace ; six tirages par rouleau ne mesurent pas un taux par rouleau.
  - Chiffres résiduels non mis à jour après l'arrivée du treizième rouleau, encore à l'état « douze » dans le corps du texte : §2 « Sur quatre événements » et « généralisée à douze rouleaux » ; §4 « 4 mauvais tirages sur 72, IC [1,5 % – 13,6 %] » ; §5 « Le 5,6 % est un taux **groupé** » — alors que l'en-tête et le §1 publient 5/78 = 6,4 %, IC [2,1–14,3 %].
  - Reproduire : « la première exécution de cette campagne a été **tuée par une édition du script pendant qu'il tournait** », d'où l'obligation de passer par `src/outils/lancer.sh`.
- **preuve de lecture intégrale** :
  - ligne 138 (62 % du fichier) : `⭐ Un **troisième** rouleau va dans le même sens sans pouvoir entrer dans le verdict :`
  - ligne 223 (dernière ligne non vide) : `reprendre. Le wrapper gèle une copie avant de lancer.`



Dépôt : `/home/masterlaplace/LplVesuvius`. Sept documents lus du premier au dernier caractère.

---

### docs/36_lorigine_de_la_pile.md
- **lignes** : 243
- **nature** : MIXTE
- **résumé** : Le document part de l'hypothèse que notre chaîne de rendu (`vc_flatten` → `vc_render_tifxyz`) décale l'origine de la pile de couches par rapport aux volumes de surface publiés, et un contrôle apparié sur un seul segment officiel la **réfute** : les deux producteurs s'accordent à 14,3 µm près, et notre chaîne place même mieux sa pile (100 % de pics dans le tiers central contre 62,5 %). La réfutation déplace la cause vers le **segment** et établit qu'« officiel » n'est pas synonyme de « bon » : sur un seul rouleau, la part du tiers central va de 18 % à 68 %. En passant, le contrôle produit la seule comparaison appariée du dépôt (segment officiel contre nos tirages, même rouleau, même chaîne) et un rendu de papyrus par notre propre chaîne. Le document est ensuite recadré deux fois : par `38` (les distances mesurées sur nos traces sont sans objet) et par `60` (la section M1ter est annulée).
- **conclusions extractibles** :
  - Contrôle apparié sur le même segment officiel : volume de surface publié = 31 couches, écart médian **3,00 µm**, tiers central 62,5 %, au bord 12,5 % ; notre `vc_flatten` → `vc_render_tifxyz` = 31 couches, écart médian **17,28 µm**, tiers central **100 %**, au bord **0 %**.
  - « 14,3 µm d'écart sur le même segment. Les deux producteurs s'accordent. » L'hypothèse du milieu transporte.
  - Le seuil de décision (50 µm) était écrit dans le script **avant** la mesure, avec ses deux issues.
  - Les quatre segments de `PHerc1447` publiant un volume de surface : `20250703025628` 22/50 fenêtres, tiers central **68,2 %**, 3,0 µm ; `20250702235910` 24/50, 62,5 %, 3,0 µm ; `20250703034159` 22/50, **18,2 %**, 10,5 µm ; `20251105093211-z_dbg_gen_00320` **4**/50, 25,0 %, 11,0 µm.
  - « Officiel » n'est pas synonyme de « bon » : sur un seul rouleau le tiers central varie d'un facteur **3,7** (18 % → 68 %).
  - Comparaison appariée `PHerc1447`, notre chaîne : segment officiel `20250702235910` **17,28 µm** (plafond 129,6, non censuré) ; notre tirage `r2` **159,84 µm** ; `r1` et `r4` **≥ 172,80 µm** (au plafond) → facteur d'au moins **9,2**, borne basse.
  - Le même tirage `r2` rendu dans une fenêtre de deux spires (81 couches, plafond 345,6 µm) lit **311,0 µm** non censuré, contre 159,84 à 41 couches → toutes les valeurs d'écart du dépôt sont des sous-estimations, et le facteur réel contre le segment officiel est **≥ 18**, pas 9,2.
  - Le rendu publié : `PHerc1447`, segment officiel `20250702235910`, **25,4 × 27,5 mm**, couche 11 sur 31 — treillis de fibres croisées, trous, bords déchirés : « La chaîne déroule et aplatit ; ce n'est pas le maillon qui manque. »
  - Confirmation par le test de convergence sur deux segments publiés de `PHerc1447`, mêmes fenêtres (31 et 81 couches) : `20250702235910-auto_grown_…292` → 17,28 / 17,30 µm, 0 % de pics au bord, **α = +0,00** ; `auto_grown_20250502160708188` (2,89 cm²) → 129,6 / 345,6 µm, **72–78 %** au bord, **α = +1,02** — le second ne converge pas.
  - Piège de nommage mesuré : le répertoire local `data/trace/PHerc1447_officiel/` désigne le segment à α = +1,02, pas celui à +0,00 ; « Le nom d'un répertoire n'est pas une mesure. » Remède : `src/outils/spire_suivante.sh` refuse de partir d'une surface qui ne converge pas.
  - Le contrôle porte sur **un** segment : il réfute « le producteur décale systématiquement », pas « il ne décale jamais ».
- **rétractations / corrections internes** :
  - ⚠⚠ Le document entier est écrit sur une hypothèse que sa propre mesure réfute (en-tête + §2) ; il est conservé sous cette forme délibérément.
  - §4 : `25` avait retiré le critère du tiers central en s'appuyant sur **un** segment officiel traité comme **la** référence — le raisonnement est juste, le choix de référence ne l'est pas. Le critère est déclaré « à reconsidérer, pas rétabli ».
  - §5 : « Le signalement posé ce matin est **retiré** » concernant `24` §2 (écart médian 94 µm).
  - §5, encadré : ⚠⚠ recadrage du 2026-08-20 par `38` — toute distance mesurée sur une de NOS traces est sans objet (α = +1,01), ce ne sont pas des sous-estimations mais des mesures d'une grandeur qui n'existe pas là.
  - §5 bis : **section M1ter ANNULÉE** par `60` — `infer_ink.load_layer_stack` normalisait par `65535` sur une pile **uint8**, donc arrivée au modèle 257 fois trop sombre ; à l'échelle corrigée σ = **0,6558**, soit 1,2 fois le témoin, au lieu de σ = 0,0171. Le texte annulé est conservé tel quel.
  - §5 bis : la ligne « 2,4 µm » était FAUSSE, corrigée le 2026-08-27 en **7,91 µm** (confusion avec la campagne ESRF) ; deux documents du dépôt portaient deux pas différents pour la même pile.
  - §5 bis : la prémisse « 26 couches couvrent 225 µm là où l'entraînement en voyait 62 » **tombe** avec le pas corrigé — à 7,91 µm elles couvrent **205,7 µm**, et le facteur n'est pas quatre mais **1,09**.
- **preuve de lecture intégrale** :
  - ligne 164 : « > **Le modèle sort une constante — σ 45 fois plus petit.** Ce n'est pas « peu d'encre », »
  - lignes 230–231 : « en le nommant. Enchaîner depuis une surface posée en travers mesurerait la propagation d'un / défaut, et le résultat aurait l'air d'un résultat. »

---

### docs/37_les_deux_axes_ne_saccordent_pas.md
- **lignes** : 136
- **nature** : RESULTAT
- **résumé** : Le document teste pour la première fois la parade écrite dans `31` §4 contre la malédiction du vainqueur — « sélectionner sur un axe, valider sur l'autre » — en comparant l'axe géométrique (`vc_tifxyz_selfcross`, auto-intersection) et l'axe de profondeur (position de la matière lue dans le volume), en comparaison **intra-rouleau**. Résultat : 1 accord sur 8 comparaisons là où le hasard seul en donnerait ~4 ; sélectionner sur la géométrie n'achète rien sur la profondeur. Le document reconnaît que sa colonne « écart » est largement censurée par la fenêtre de rendu, et un recadrage ultérieur par `38` rend ses distances absolues sans objet, mais sa conclusion (l'ordre relatif intra-rouleau) survit.
- **conclusions extractibles** :
  - Résultat principal : fenêtre **21 couches** → **0 / 4** d'accord (3 ex-aequo), part au bord 0/4 ; fenêtre **41 couches** → **0 / 4** d'accord (2 ex-aequo), part au bord 1/4. Soit **1 accord sur 8 comparaisons, là où le hasard seul en donnerait ~4**.
  - Sur deux des quatre rouleaux en fenêtre large, le tirage condamné par la géométrie est **strictement le meilleur** selon la profondeur : `PHerc0268` (0,386 contre 0,645 et 0,814 au bord) et `PHerc0257` (0,406 contre 0,495 et 0,438).
  - Le seul accord du lot est `PHerc0125` en fenêtre large : le tirage condamné y est bien le plus mauvais des trois (0,767 contre 0,600 et 0,566).
  - Quatre rouleaux ne rendent aucun de ces comptes significatif ; ce qui se lit est la **direction**, et seulement parce qu'elle est franche — 0/4 et 1/4 disent quelque chose, 2/4 ne dirait rien.
  - L'écart à la trace est censuré à `(couches / 2) × voxel`, soit **93,6 µm à 21 couches** et **187,2 µm à 41** ; mesuré **13 valeurs sur 16 au plafond** en fenêtre étroite et **encore 9 sur 16** en large — doubler la fenêtre n'a pas suffi.
  - La censure est elle-même un résultat : sur ces seize rendus, le pic de matière est hors d'une fenêtre de ±187 µm pour **plus de la moitié**.
  - La conclusion survit à `36` parce que les seize rendus sortent du même producteur avec le même `-n` : un décalage commun ne change pas *quel tirage est le pire* d'un même rouleau. Ce qui tomberait, ce sont les valeurs absolues et les comparaisons entre producteurs.
  - Coût mesuré : un rendu ≈ 10 min, donc les 72 tirages de `35` feraient 12 h ; `src/graine/choisir_tirages.py` retient 4 mauvais + 8 propres appariés + 4 témoins = 16 tirages, 2,7 h.
  - Conséquence de méthode : la sélection par échantillonnage doit porter sur **les deux axes à la fois**, pas sur l'un puis vérifier sur l'autre — et le coût change de nature (un rendu par tirage, pas 0,05 s de juge géométrique).
  - Ce que le document ne dit pas : ni que l'axe 2 est le bon (aucune vérité terrain), ni que les tirages « propres » sont mauvais ; il ne mesure rien sur 8 des 12 rouleaux de `35`.
- **rétractations / corrections internes** :
  - §3 : ⚠⚠ recadrage du 2026-08-20 par `38` — toute distance mesurée sur une de NOS traces est **sans objet** (α = +1,01) ; ce ne sont pas des sous-estimations mais des mesures d'une grandeur qui n'existe pas là. Elles restent valides pour une surface qui converge (segment officiel, α = +0,00).
  - §4 : si l'origine de nos piles était décalée (hypothèse de `36`), les valeurs absolues du document seraient fausses — la conclusion relative, elle, est explicitement préservée.
  - §3 : la colonne « écart » est déclarée « presque inutilisable telle quelle », ses ex-aequo étant des ex-aequo **par censure**, pas par mesure.
- **preuve de lecture intégrale** :
  - ligne 82 (début) : « ⚠⚠ **Recadré le 2026-08-20 par [`38`](38_ce_qui_bouge_avec_la_fenetre.md).** Toute distance mesurée sur une de NOS traces est sans objet : le test de convergence montre que la mesure **suit la f… »
  - ligne 120 : « - **Il ne dit pas que l'axe 2 est le bon.** Aucun des deux n'a de vérité terrain ici. »

---

### docs/38_ce_qui_bouge_avec_la_fenetre.md
- **lignes** : 274
- **nature** : RESULTAT
- **résumé** : Trois hypothèses réfutées le même jour (la trace est à une spire de sa feuille, puis à deux, puis c'est une question de forme) ont un motif commun — la mesure suit le **réglage** au lieu de suivre le papyrus — et ce motif devient l'instrument central du dépôt : le test de convergence, noté α. Le document établit qu'un segment officiel converge (α = +0,00) tandis que notre trace suit la fenêtre (α = +1,01), c'est-à-dire qu'il n'y a **aucune feuille à portée** même à quatre spires, et il valide ce verdict à l'œil (une face de feuille contre des tranches d'empilement). Il en tire une reformulation de l'objectif (faire converger la mesure, pas réduire l'écart) et une cause candidate ajoutée le lendemain, dont une première version accusant à tort le masque binaire est corrigée.
- **conclusions extractibles — définition de l'instrument α** :
  - **Le test** : « Rendre la **même** surface dans des fenêtres de plus en plus profondes, et regarder si la distance mesurée bouge. »
  - Mesure appariée, même rouleau, même chaîne, même instrument : segment officiel `20250702235910` → 31 couches **17,3 µm**, 81 couches **17,3 µm** ; notre tirage `PHerc1447 r2` → 21 couches **86,4 µm**, 41 **159,8 µm**, 81 **311,0 µm**, 161 **682,6 µm**.
  - L'officiel : « ×1,00 pour ×2,6 de fenêtre, **α = +0,00** » — la mesure ne dépend pas du réglage, donc c'est une **distance**. Le nôtre : « ×7,90 pour ×7,7 de fenêtre, **α = +1,01** » — le « pic » est le plus fort de ce que la fenêtre contenait et s'éloigne avec elle. α est donc l'exposant de la loi de puissance liant l'écart mesuré à la largeur de fenêtre (instrument nommé : `src/commun/test_convergence.py`, α = log(croissance des écarts) / log(élargissement des fenêtres)).
  - Conclusion opérationnelle : « Ce n'est donc pas “notre trace est à 311 µm de sa feuille”. C'est : **il n'y a aucune feuille à portée.** » À 691 µm de portée, soit **quatre spires**, il n'a toujours rien trouvé.
  - Trois propriétés que l'instrument a et qu'aucun autre du dépôt n'a toutes : **aucun seuil** (on compare une mesure à elle-même), **aucune vérité terrain**, **aucune échelle** (rapport sans dimension, traverse les résolutions). La fenêtre de rendu, dont toutes les autres valeurs dépendent, est ici **le sujet** de la mesure.
  - **Condition de validité** : il faut au moins deux fenêtres dans un rapport d'au moins deux ; deux mesures trop proches rendraient un rapport proche de 1 quelle que soit la surface, c'est-à-dire un test incapable d'échouer — `src/commun/test_convergence.py` **refuse** de rendre un verdict dans ce cas.
- **conclusions extractibles — ce que α NE distingue PAS** :
  - ⚠⚠ Réserve du 2026-08-22 (`49`) : **α ≈ 1 a deux causes** — « un pic qui recule, et **aucun pic du tout**. Un profil plat rapporte le bord de la fenêtre par défaut, et le rapport de deux bords vaut celui des fenêtres — donc α = 1 par identité. » Le seul profil de cette trace encore sur disque (41 couches) a une amplitude de **0,0194** pour un seuil de détection de **0,02**, et un écart de **172,80 µm** qui est exactement la demi-fenêtre à 8,64 µm.
  - Ce que la réserve change : le verdict *pratique* tient (« aucune feuille dans la fenêtre » est vrai sous les deux lectures), mais l'affirmation que la surface **coupe** l'empilement repose sur la géométrie du rendu, pas sur ce profil ; **aucun verdict de convergence n'est touché** (α de plafond ≈ 1, mesuré : **0 série convergente sur 107**).
  - Il ne dit pas **de combien corriger** : une trace qui ne converge pas n'a pas de distance à sa feuille. Il sépare *posée à côté* de *posée en travers*, et rien d'autre.
  - Il ne remplace **pas** l'auto-intersection : une surface peut converger *et* se croiser ; les deux axes de `37` restent indépendants et celui-ci est une meilleure version du second, pas du premier.
  - Il ne dit pas **pourquoi** la trace est posée en travers (traceur, graine, prédiction de surface, ou les trois), et il ne mesure qu'un tirage pour la série complète plus un segment officiel : « deux surfaces ne font pas une population ».
  - Un α intermédiaire n'est pas un demi-succès : α = +0,65 est « une surface qui traverse *moins* d'empilement — peut-être une feuille suivie par morceaux, peut-être une coupe oblique ».
- **autres conclusions extractibles** :
  - Validation visuelle : le segment officiel (α = +0,00, 25 × 27 mm) montre un treillis de fibres croisées, la *face* d'une feuille ; notre trace depuis **leur** graine (α = +1,01, 49 × 49 mm) montre de longues striations parallèles, les *bords* de dizaines de feuilles empilées — et elle est **six fois plus grande** : « L'aire mesure jusqu'où le traceur est allé, jamais s'il est allé au bon endroit. » Aucun seuil n'a été réglé pour obtenir cet accord.
  - Toutes les distances publiées par le dépôt sont sans objet pour nos traces (les 94 µm de `24`, les 146–187 µm de `37`, les 311 µm) ; elles restent valides pour les surfaces qui convergent.
  - Le vrai objectif devient : **faire converger la mesure**, pas « réduire l'écart de 311 à 17 µm » — « Une trace qui converge, même à 60 µm, suit une feuille ; une trace à α = 1 n'en suit aucune, quelle que soit sa valeur. »
  - Hypothèse qui inverse (une coupe radiale ne peut pas se croiser), testée sur deux essais du même rouleau : `essai_scale1` → **0** auto-intersection, 187,2 µm à 41 couches, 730,2 à 161, **α = +0,99** (en travers) ; `essai_ng2` → **112 139** auto-intersections, 112,3 / 271,5 µm, **α = +0,65** (intermédiaire). Celui qui a zéro croisement est le plus radial des deux ; la direction avait été écrite avant la mesure.
  - Ce qui joue contre cette hypothèse : le segment officiel converge **sans** compte de croisements catastrophique ; donc « beaucoup de croisements » est au mieux un *symptôme*, jamais un critère.
  - Cause candidate, vérifiée ligne à ligne : `SURFACE_SDT` vaut **0** par défaut, `NORMAL`/`SNAP` n'agissent qu'avec une grille de normales, `DIRECTION` qu'avec des champs de direction — **trois leviers de données sont éteints** dans nos runs de base.
- **rétractations / corrections internes** :
  - §2, encadré : ⚠⚠ réserve ajoutée le 2026-08-22 par `49` (les deux causes de α ≈ 1, ci-dessus).
  - Section « Une cause candidate » : ⚠ « Une première version de cette section accusait le masque binaire (`…-th0.2.zarr`, deux valeurs). C'était faux » — corrigé par `41` §6ter : le traceur calcule lui-même un champ de distance **signé** à partir du masque.
  - Même section : « il ne reste que la géométrie » est déclaré **trop fort** — la doc officielle du traceur décrit un terme de données primaire (`thresholdedDistance`) que l'auteur n'a pas su suivre jusqu'aux résidus ; ce qui est vérifié se limite aux trois leviers éteints. La cause candidate est explicitement « une hypothèse, pas la conclusion de ce document ».
  - §1 : les trois hypothèses successives (une spire, deux spires, une question de forme) sont chacune énoncées puis tuées, avec la raison de leur mort.
- **preuve de lecture intégrale** :
  - ligne 154 : « ⭐ **Celui qui a zéro croisement est le plus radial des deux.** L'essai catastrophique au »
  - lignes 185–179 : « avec `sdt_weight` puis avec les fibres, et de voir la convergence changer : / `src/outils/leviers_de_perte.sh`. »

---

  - Reproduction : `bash src/outils/convergence_des_essais.sh` → `docs/mesures/convergence_<essai>.json`,
    `essai_ng2` et `essai_scale1` par défaut, c'est-à-dire les deux lignes du tableau.
  - ⚠⚠⚠ Le sens de la normale, cause candidate ÉLIMINÉE — et l'expérience qui l'a testée ne
    pouvait pas trancher : le dépouillement compare l'écart au pic depuis la couche tracée,
    prise au MILIEU de la pile (20 de 41), et renverser l'ordre envoie p sur n−1−p, donc
    |n−1−p − m| = |p − m| quand m = (n−1)/2. L'écart est identique **par construction**, deux
    des trois verdicts du script sont inatteignables, et la mesure tenait sur UNE fenêtre.
  - La réponse de fond, lue dans les rendus déjà sur disque : `--flip-normals` **renumérote**
    la pile — **41/41** couches identiques après renversement, **1/41** à l'endroit (le milieu).
    Donc la fenêtre est centrée sur la surface et il n'existe pas de « mauvais côté » :
    l'hypothèse n'est pas infirmée, elle est **inexprimable** avec ce drapeau.
    ⚠ Les DEUX comptes sont requis — une pile constante satisferait le premier seul.
  - Reproduction : `uv run python src/rendu/le_drapeau_de_normale.py data/sens_normale/rendu_normal
    data/sens_normale/rendu_inverse --json docs/mesures/le_drapeau_de_normale.json`, puis
    `figure_drapeau_de_normale.py` (12 + 4 contrôles).
### docs/39_le_seam_de_correction.md
- **lignes** : 127
- **nature** : PROCEDE
- **résumé** : Le document répond à la question de `31` §8 — « qu'est-ce qui remplace l'humain qui corrige le transfert de spire à spire ? » — en établissant que l'API de correction existe déjà et est publique dans `vc_grow_seg_from_seed` (`--resume`, `--rewind-gen`, `--correct`, `--resume-opt`, `--resume-generations`), et que c'est le *wrap by wrap copy tool* où le papier de juin 2026 dépense ses ~25 heures par spire. Il en déduit la chaîne complète et localise le seul maillon manquant : produire, pour une trace donnée, une liste de points 3D par lesquels elle aurait dû passer. Il ne fait rien tourner, et note pourquoi le maillon ne peut pas être construit depuis le volume ce soir-là.
- **conclusions extractibles** :
  - `--correct` charge un **`PointCollections`** (format *point collection* de VC3D) ; une correction est une liste de points 3D (plus un ancrage 2D optionnel dans la grille) vers lesquels le traceur tire la surface pendant qu'il la refait pousser ; `--correct` **exige** `--resume` : « on ne corrige pas une trace, on la **re-pousse** en lui donnant des points de passage ».
  - Dès qu'il y a des corrections, la surface est rechargée avec `SURF_LOAD_IGNORE_MASK` : le masque d'une trace corrigée est jeté.
  - État des maillons : tracer ✅ (`vc_grow_seg_from_seed`), juger ✅ (`38`, sans seuil ni vérité terrain), **dire où la surface aurait dû passer ❌ (le trou)**, appliquer ✅ (`--resume --rewind-gen --correct`), revérifier ✅ (le même test de convergence).
  - Le trou est reformulé : « Ce n'est plus “corriger une trace” — c'est “écrire un fichier de points”. »
  - Pourquoi ce n'est pas fait depuis le volume : sur nos traces l'instrument de profondeur ne trouve rien — **`part_plates = 1,000`**, aucune structure de profondeur dans aucune fenêtre, dans les deux sens de normale. « Une surface couchée dans le plan des spires n'a pas de feuille “au-dessus” ni “en-dessous” […] Il n'y a rien vers quoi tirer. »
  - Sortie possible : corriger **depuis la prédiction** et non depuis le volume — `src/nappe/sonder_point.py` mesure qu'au point de départ la prédiction publiée a une planarité de **0,993**.
  - Deuxième pièce manquante, plus petite : `--rewind-gen` demande de choisir une génération, donc de savoir *à partir d'où* la trace a divergé, alors que le test de convergence rend un verdict sur une trace entière. Remède retenu : **balayer** quelques valeurs (une trace de ce rouleau coûte une vingtaine de secondes, « le balayage est moins cher que le raisonnement »).
  - Une reprise qui ne produit aucun maillage est rapportée comme **résultat sur le seam**, pas comme panne du script.
  - Ce que le document ne dit pas : il n'a **rien fait tourner** (aucune correction écrite ni appliquée) ; il ne dit pas que les segments officiels sont hand-corrigés — c'est plausible mais leur métadonnée ne l'enregistre pas, et « supposer une provenance est exactement ce que `36` a payé ».
  - Reproduction de la planarité 0,993, vérifiée le 2026-09-05 : `sonder_point.py` sur la
    prédiction publiée de `PHerc1447`, `--xyz 4682 2740 13350 --level 0 --bloc 8`. Elle rend
    aussi ce que la planarité seule ne dit pas — occupation **0,457** dans la cellule,
    médiane **0,156** sur le chunk, **0,0 %** de fenêtres saturées : la prédiction porte une
    structure de feuille et non un bloc plein, ce qui est la condition pour qu'un gradient
    existe. ⚠ Les seuils (0,02 / 0,80) sont ceux de `trouver_graine.py`, donc la sonde reste
    comparable à la sélection au lieu d'introduire une troisième échelle.
- **rétractations / corrections internes** : aucune rétractation d'un fait mesuré. Le document est mis à jour a posteriori par la section « La boucle entière, écrite », qui signale que le chaînon manquant a depuis été construit (`41`) et que `src/outils/boucle_de_correction.sh` met les maillons bout à bout — donc le « ❌ le trou » du §2 et le « rien fait tourner » du §4 sont périmés par `41` et `42`.
- **preuve de lecture intégrale** :
  - ligne 64 : « ⭐ La sortie possible est donc de **corriger depuis la prédiction et non depuis le volume** : »
  - lignes 112–90 : « ⚠ `--rewind-gen` demande toujours de choisir une génération, et notre juge porte sur une / trace entière. On **balaie** donc quelques valeurs plutôt que d'en deviner une : une trace »

---

### docs/40_le_rouleau_entier.md
- **lignes** : 130
- **nature** : MIXTE
- **résumé** : Le document assemble 44 spires consécutives publiées de `PHerc0172` (052 → 095, sans trou) en une seule image de 4518 × 10000 px, en insistant sur le fait que tout le travail de déroulage et de détection d'encre est celui de l'équipe du concours : ce dépôt n'ajoute que l'ordonnancement et la vérification qu'aucune spire ne manque. Il mesure ensuite où ce matériel existe rouleau par rouleau et constate que les rouleaux du prix sont exactement ceux qui n'ont rien. Il rapporte enfin un instrument tenté (`score_de_lignes`, périodicité) qui a demandé deux corrections et qui reste publié mais **pas utilisé**.
- **conclusions extractibles** :
  - **44 spires consécutives** de `PHerc0172`, de la 052 à la 095, sans un trou ; image de **4518 × 10000 px**.
  - L'image est le travail de l'équipe du concours ; ce dépôt n'y ajoute que l'assemblage et le fait, mesuré, qu'il ne manque aucune spire entre la première et la dernière. « Nous ne déroulons rien ici : **nous ordonnons**. »
  - Les bandes sont alignées à gauche, **pas recalées** : l'origine du dépliage est propre à chaque segment, donc une colonne de l'image ne désigne pas la même position d'une bande à l'autre. Les largeurs varient de **666 à 1247 px, soit 47 %**.
  - La largeur croît avec le numéro de spire, et ce n'est pas un artefact : une spire extérieure fait un tour plus long qu'une spire intérieure — l'image porte la géométrie du rouleau.
  - Coût mesuré : **21 Mo** téléchargés (44 cartes d'encre `ds8`), 44 listages + 44 fichiers, **~3 min**, et **rien** de tracé, aplati ou rendu localement.
  - Le rendu pleine résolution d'un seul segment pèse **1,84 Go** sur le dépôt public ; les vignettes `ds8` sont 8× plus petites par côté donc **64× plus légères**, et un caractère y fait environ **six pixels**.
  - Inventaire du matériel publié : `PHercParis4` 81 segments / 80 avec carte d'encre (segments datés, pas de numéro de spire) ; `PHerc0172` 53 / 53 (**052 → 095 sans trou**) ; `PHerc0139` 38 / 38 (**023 → 059 sans trou**) ; `PHerc1667` 19 / 19 (trois trous) ; `PHerc1447` 4 segments / **0** carte d'encre ; `PHerc0800` 0 / 0 ; `PHerc1203` 0 / 0.
  - « Les rouleaux du prix sont ceux qui n'ont rien » : la mosaïque est possible là où le travail est déjà fait et impossible là où le prix se gagne.
  - σ ne répond pas à « quelle spire porte le plus de texte » : un mouchetis et une écriture ont le même écart-type, et la spire la plus contrastée du rouleau (081, σ 58,6) est justement du speckle.
  - `score_de_lignes` (périodicité) sépare proprement sur données fabriquées : **0,96 contre 0,13**, et retrouve le pas exact.
  - Correction 1 : un lag minimum fixé à 4 px « pour éviter le grain » élisait un interligne de 4 px, soit **0,4 mm**, dix fois trop serré — c'était le grain du JPEG, mieux noté que n'importe quelle vraie ligne. Les bornes viennent maintenant de la physique (3 à 12 mm d'interligne).
  - Correction 2 : un grain a des harmoniques — un motif de période 3 rejoue à 21, 30, 42, donc à l'intérieur de la fenêtre plausible ; mesuré, sur un mélange grain-3 + lignes-30 borné sur [20, 45], le score élit **21**. Un passe-bas à l'échelle du grain supprime la famille entière.
  - Sur les vraies bandes l'instrument ne suffit pas : **37 spires sur 44 élisent l'axe vertical** là où l'œil lit des lignes horizontales, et les interlignes s'agglutinent contre la borne basse (20 à 22 px sur 44 bandes) — signature d'une mesure qui ne trouve pas de vraie période. Il est **publié et pas utilisé** ; la spire du détail a été choisie à l'œil.
  - Ce que ça ne résout pas : rien de ce qui bloque la chaîne du dépôt — `38` tient (nos traces sont des coupes radiales) et `39` tient (le maillon manquant est *dire où la surface aurait dû passer*).
- **rétractations / corrections internes** :
  - §6, deux corrections internes de l'instrument `score_de_lignes`, « les deux attrapées par un témoin et non par relecture » : la borne de lag choisie pour la commodité (classement entièrement faux) et l'insuffisance du bornage face aux harmoniques du grain.
  - Le document se déclare lui-même en retrait sur `score_de_lignes` : « pas encore assez pour choisir », publié mais pas utilisé.
- **preuve de lecture intégrale** :
  - ligne 88 : « ⚠ **Les rouleaux du prix sont ceux qui n'ont rien.** `PHerc1447` publie quatre volumes de »
  - lignes 127–130 : « Rien de ce qui bloque notre propre chaîne. [`38`](38_ce_qui_bouge_avec_la_fenetre.md) / tient toujours : nos traces sont des **coupes radiales**, et / [`39`](39_le_seam_de_correction.md) tient toujours : le maillon manquant est *dire où la / surface aurait dû passer*. Cette image est la cible, pas le chemin. »

---

### docs/41_marcher_le_long_dune_nappe.md
- **lignes** : 310
- **nature** : MIXTE
- **résumé** : Le document construit le maillon manquant de `39` — un marcheur de nappe qui produit les points de passage — et mesure pourquoi la méthode naïve « au plus proche » échoue : dans un rouleau, le voisin d'à côté est plus loin que le voisin d'en face. Il expose les trois gestes retenus (normale par tenseur de structure, recentrage sous-voxel sur la crête, avance reprojetée) et la garde qui refuse un recentrage de plus de 2 voxels, puis mesure sur la vraie prédiction publiée. Il contient trois corrections internes majeures, dont une (§6ter) qui **annule l'explication du §6** : le masque binaire n'était pas le problème, le traceur calcule déjà un champ de distance signé — ce qui manque est son **poids**. Une seconde correction, une heure plus tard, retire même la conclusion « il ne reste que la géométrie ».
- **conclusions extractibles** :
  - « Au plus proche » échoue, mesuré sur deux spires à 4 voxels l'une de l'autre avec un trou de 17 voxels : au plus proche → écart max **5,94 voxels** à sa spire de départ (au-delà de la spire voisine), continue 200 pas ; sur la crête → **0,67 voxel**, s'arrête au trou, 31 pas. **Facteur 9.**
  - Le chemin fautif reste connexe et plausible : « Rien dans sa forme ne dit qu'il a changé de feuille — seul son rayon le dit. Un contrôle de régularité ne l'attraperait pas. »
  - Raison géométrique : « dans un rouleau, le voisin d'à côté est plus loin que le voisin d'en face » — un pas le long de la spire fait un voxel, la spire suivante est à quatre.
  - Garde décisive : un recentrage de plus de **2 voxels** est refusé ; la marche s'arrête et dit laquelle des deux choses lui est arrivée (fin de nappe ou saut refusé). L'ordre des deux tests est le diagnostic, et il avait été écrit à l'envers.
  - Sortie : un `PointCollections`, format **lu dans la source** (`core/src/PointCollections.cpp`), pas deviné. L'**ordre des points est signifiant** : `PointCorrection` trie par identifiant croissant et s'en sert comme d'un chemin — un nuage non ordonné donnerait un fichier valide et un résultat absurde.
  - Coordonnées écrites en `(x, y, z)` alors que la marche travaille en `(z, y, x)` ; les mélanger tire la surface vers un point parfaitement faux sans que rien n'ait l'air cassé (assertion dédiée).
  - `vc_grow_seg_from_seed` **n'est pas une propagation** : c'est un problème de moindres carrés résolu par Ceres, chaque point de grille portant une famille de résidus (`GrowPatch.cpp:1244`) — DIST, STRAIGHT, DIRECTION, SNAP, NORMAL, NORMAL3DLINE, SDIR, CORRECTION, REFERENCE_RAY, SURFACE_SDT, SPACELINE, PATCH_NORMAL.
  - `DIRECTION` prend des `DirectionField` (`horizontal`, `vertical`, `normal`) et `FiberDirectionLoss` demande que l'axe u de la grille suive les fibres horizontales et l'axe v les verticales : « le papyrus fournit son propre système de coordonnées ». `CORRECTION` est le résidu que nos points de passage alimentent.
  - La prédiction publiée de `PHerc1447` est un **masque binaire** (`…-surface-m7-L0-th0.2.zarr`, valeurs distinctes : 2 → 0 et 255) : pas de gradient à l'intérieur de la matière, un plateau.
  - Marche sur le même bloc réel, même départ, même code : masque brut → 106 pas, distance au bord médiane **1,34 vx**, 0 vide traversé, arrêt sur saut de nappe refusé ; **transformée de distance** → **138 pas**, **1,74 vx**, 0 vide traversé, arrêt par sortie du bloc. **283 points de passage** dans les deux sens, soit ≈ **2,4 mm** de nappe suivie à 8,64 µm le voxel.
  - Sur un masque binaire sans `--distance`, l'outil **refuse de marcher** et nomme le remède.
  - Poids par défaut des douze familles de résidus (`GrowPatch.cpp:1264`) : SNAP 0,1 · NORMAL 10 · DIST 1 · STRAIGHT 0,2 · DIRECTION 1 · SDIR 1 · CORRECTION 1 · NORMAL3DLINE 0 · REFERENCE_RAY 0 · SURFACE_SDT 0 · SPACELINE 0 · PATCH_NORMAL 0.
  - Faits vérifiés ligne par ligne : `SURFACE_SDT` vaut 0 par défaut (`GrowPatch.cpp:1274`) et son résidu n'est **pas créé** si le poids est nul (`:1789`) ; `NORMAL`/`SNAP` sortent immédiatement sans grille de normales (`:2050`) ; `DIRECTION` exige des `direction_fields` (`:2204`) ; aucun de nos **17** `seed.json` ne règle `sdt_weight`.
  - « Il ne reste alors que `DIST` et `STRAIGHT` » → une surface optimisée pour ces deux-là seuls est une grille plate et régulière, et « posée dans un rouleau, une grille plate est une **coupe radiale** » — cohérent avec `essai_ng2`, seul essai poussé avec une grille de normales, qui est le moins radial (α = +0,65 contre +0,99 et +1,01).
  - Panne d'installation qui avait pris la forme d'un fait sur le rouleau : `numcodecs` manquait dans l'environnement `inference/`, donc aucun chunk *blosc* n'était décodable et `lire_chunk` rendait `None` — la même valeur que pour un chunk absent. Le chunk `0/69/14/24` existe bien et porte **19,3 %** de matière. Corrigé : `decode` **lève** `CodecIndisponible`.
  - Coût mesuré d'un orphelin : `src/outils/verifier_zarr.sh` décrivait exactement cette panne dans son en-tête et n'a pas tourné parce qu'aucun document ne le nommait — **une heure, et une mesure publiée fausse**.
  - Ce que le lot ne fait pas : il ne dit pas quelle nappe suivre ; il produit des chemins **1D, pas une surface** ; et il **ne résout pas le numéro de spire**, problème global et non local (`ColPoint` porte `wind_a`, la collection `winding_is_absolute`).
  - Reproduction : `GENERATIONS=120 bash src/outils/leviers_de_perte.sh` →
    `docs/mesures/leviers_<levier>.json`. ⚠ La prédiction de surface est LISTÉE sur le bucket
    et non écrite en dur : un chemin figé vieillirait sans bruit à la prochaine republication.
- **rétractations / corrections internes** :
  - §6ter (⚠⚠ CORRECTION) : « **Mon explication ci-dessus est fausse telle qu'elle est formulée** » — le traceur calcule bien un champ de distance, et même **signé** (`get_or_compute_sdt_chunk` : `binaire ? -edt_interieur : edt_exterieur`), donc le remède présenté au §6 comme manquant est dans le code depuis toujours. Ce qui manque est le **poids**.
  - §6ter, seconde correction une heure plus tard : « “il ne reste que la géométrie” est trop fort » — la doc officielle décrit un terme de données primaire (`thresholdedDistance`, `GrowPatch.cpp:3078`, une transformée de distance seuillée à 170 et plafonnée à 15) que l'auteur n'a pas su suivre jusqu'aux résidus. « “il ne reste que `DIST` et `STRAIGHT`” n'est pas une mesure, c'est une extrapolation — et c'est la deuxième fois aujourd'hui que je transforme “j'ai trouvé un interrupteur éteint” en “rien n'est allumé”. »
  - §6, encadré « deux mesures que j'ai failli publier fausses » : (1) une comparaison entre deux blocs différents — « 9 pas sur le masque » (cube de rayon 64) opposé à « 138 sur la distance » (cube de rayon 128), présentée comme un facteur 15 ; les chiffres du tableau sont désormais appariés ; (2) un chemin 3D projeté sur une seule tranche, image « accablante, et fausse » — la marche avait parcouru **125 voxels en z pour 57 en y**, et la distance au bord ne descend jamais sous **1,22** sans traverser un vide.
  - §6ter : la note « deux leviers n'ont JAMAIS été essayés » est barrée en place — « ⭐⭐ **LES DEUX LEVIERS ONT ÉTÉ ESSAYÉS** → `26` §9bis (2026-08-27), en campagne appariée ».
  - §6bis : la mesure « la graine n'était pas couverte par la prédiction publiée » était **fausse** (panne `numcodecs`), et le document dit l'avoir failli publier.
  - §7 : deux items marqués faits a posteriori — « Il n'a rien tracé » → `42` (la boucle a tourné, appariée et jugée) ; « Il produit des chemins 1D » → `42` §3, mode `--nappe` (échine et côtes).
  - §7, note « Reproduire » : « ⚠ “le seul env qui a numcodecs” était faux : la racine en a aussi, mesuré le 2026-08-25 ».
- **preuve de lecture intégrale** :
  - lignes 190–191 : « optimisée pour ces deux-là seuls est une grille plate et régulière**. Posée dans un rouleau, / une grille plate est une **coupe radiale**. »
  - lignes 291–284 : « pourquoi `ColPoint` porte un champ `wind_a` et la collection un `winding_is_absolute`. / Aucune marche locale ne peut y répondre. »

---

### docs/42_la_boucle_tourne_et_ne_suffit_pas.md
- **lignes** : 287
- **nature** : RESULTAT
- **résumé** : La boucle de correction complète (tracer → marcher la prédiction → écrire les points → `--resume --rewind-gen --correct` → juger) tourne pour la première fois, appariée avec un témoin, et le seam fonctionne mécaniquement — mais 318 points de passage contre 56 630 points de grille, soit 0,56 % de la surface, ne suffisent pas : α reste à 1, la surface est encore posée en travers. Le balayage montre que `correction_weight` ne réoriente pas la surface mais la fait **fuir** (jusqu'à 204 cm² puis 3 603 cm²), et un audit ultérieur (`49`) établit que les quatre séries sont indiscernables de leur propre plafond, donc non ordonnables. Le §7 relit tout dans une fenêtre de profondeur **valide** et trouve que la conclusion tient alors que sa preuve initiale ne tenait pas : le témoin bat toutes les corrections, à tous les poids.
- **conclusions extractibles** :
  - Le seam fonctionne mécaniquement : la reprise corrigée lit le fichier, en tient compte, et produit une surface différente — c'était l'inconnue de `39`.
  - Résultat apparié (graine `5842 5839 7386`, même volume, mêmes paramètres, seuls les points de passage diffèrent) : témoin → 19,82 cm², **0** auto-intersection, 187,2 µm à 41 c, 711,5 µm à 161 c, **α = +0,98** ; corrigé 318 points → 20,65 cm², **11 753** auto-intersections, 168,5 µm, 692,8 µm, **α = +1,03** ; segment officiel → 17,3 / 17,3 µm, **α = +0,00**.
  - « La correction a changé la trace et n'a pas changé sa nature. » Les écarts baissent d'une dizaine de pour cent et α reste à 1.
  - Rapport de forces mesuré des deux côtés : **318 points de passage contre 56 630 points de grille**, soit **0,56 %** de la surface, avec un `correction_weight` qui vaut **1,0 par défaut** — le même ordre que `DIST`, qui s'applique partout. « Une correction de 318 points est un coup de pouce local, pas une réorientation. »
  - Semis mesuré sur `PHerc0358`, même point de départ : ligne (`--deux-sens`) = 318 points, 1 collection, **0,56 %** ; **nappe** (échine + 48 côtes) = **5 695** points, **49** collections, **10,1 %**.
  - Chaque côte est sa propre collection : `PointCorrection` traite une collection comme un chemin et ancre sur son premier point, donc concaténer les côtes ferait un chemin qui saute d'un bord à l'autre à chaque rangée.
  - Couverture vérifiée sur un cylindre de contrôle : tous les points restent à moins de **0,32 voxel** de la nappe, et les côtes explorent **89 voxels** le long de l'axe que l'échine ne parcourt pas (0,0).
  - Seuil juste dans une unité, faux dans l'autre : plancher `0,15` (calibré pour une probabilité) → **4 côtes sur 48** traversent un vide, minimum des minima 0,15 ; plancher **`1,0`** (un voxel de matière) → **0 sur 48**, minimum 1,01. « Un seuil est attaché à une unité, et changer le champ change l'unité. » Coût de la correction : **12 points sur 5 707**.
  - Balayage : témoin 19,8 cm² / 0 croisement / 187,2 / 711,5 / +0,98 ; ligne gen 5 poids 1 → 20,7 cm² / 11 753 / 168,5 / 692,8 / +1,03 ; ligne gen 5 **poids 100** → **204,2 cm²** / 2 766 / 177,9 / 655,3 / +0,95 ; **ligne gen 40 poids 1** → 20,7 cm² / **18** / **154,5** / **519,6** / **+0,89**.
  - Le poids fort n'achète presque rien et coûte cher : α passe de 0,98 à 0,95 pendant que la surface passe de 19,8 à **204 cm²** (dix fois plus) ; le rendu qui en découle fait **17 601 × 17 181**. `correction_weight` « ne pousse pas la surface vers la bonne feuille : il la fait **s'étendre** ».
  - `correction_weight: 100` donne **204 cm²** à `--rewind-gen 5` et **3 603 cm²** à `--rewind-gen 40`, soit **182 fois** le témoin ; son rendu à 41 couches pèse **8,9 Go**. La cellule a été interrompue délibérément parce qu'un écart médian mesuré sur 3 603 cm² et un mesuré sur 19,8 cm² n'échantillonnent pas le même rouleau (le chiffre obtenu, 140,4 µm à 41 couches, aurait été le plus flatteur et le moins interprétable).
  - Aucune variante ne s'approche de +0,00 : la meilleure est à 0,89, le segment officiel à 0,00. « Le seam de correction, à tous les réglages essayés, ne transforme pas une coupe radiale en suiveuse de feuille. »
  - Ce que le plateau désigne : `--rewind-gen N` garde les N premières générations, poussées par l'objectif **non contraint**, donc déjà un morceau de coupe radiale ; `DIST` et `STRAIGHT` s'opposent à leur pivotement. La correction doit donc venir **avant** elles et porter une information à **deux dimensions** — « un fil ne définit pas une orientation de surface ».
  - L'hypothèse qui inverse (`38`) perd son dernier appui indirect : une trace passe de **0 à 11 753** auto-intersections et son α ne s'améliore pas (+0,98 → +1,03) ; beaucoup de croisements n'est « ni un symptôme de bon suivi ni son contraire : c'est une propriété indépendante ».
  - Ce que ça ne dit pas : que les points de passage soient faux — `41` mesure que la marche suit une nappe sur ≈ 2,4 mm sans traverser un seul vide ; « ils sont simplement trop peu nombreux et trop peu pondérés ».
  - Sortie par le haut : le mode public **`gen_neighbor`** (`apps/src/vc_grow_seg_from_seed.cpp:625`), jamais lancé dans ce dépôt, prend une surface par `--resume`, tire un rayon depuis chaque sommet le long de la normale (`neighbor_dir` = `in` ou `out`), avance par pas de `neighbor_step` voxels et s'arrête dès qu'il touche de la matière au-dessus de `neighbor_threshold` — c'est le *wrap by wrap copy tool* du papier de juin 2026, et il est public. Question posée : « **La convergence survit-elle à l'enchaînement, et sur combien de spires ?** » (spire 0 = le segment officiel **rejugé par notre chaîne**, jamais son chiffre repris).
  - Relecture dans une fenêtre **valide** (§7) : pour `PHerc0358`, pas inter-feuilles **187,2 µm** à **9,362 µm** par voxel, donc 41 et 161 couches font **2,05** et **8,05 pas** — au-delà d'un pas la fenêtre contient plusieurs feuilles et l'argmax désigne la plus brillante. Les 19 couches centrales du rendu de 41 font **0,95 pas**.
  - Résultat dans la fenêtre valide : témoin → pic médian 15, **tiers central 22 %**, au bord 43 % ; corrigé gen 5 → 17, 8 %, 76 % ; corrigé gen 40 → 13, 18 %, 49 % ; corrigé gen 5 poids 100 → 19, 8 %, 55 % ; corrigé sur nappe gen 1 poids 100 → rendu **7061 × 261**, une lanière de 13 cellules, trop étroite pour une fenêtre.
  - « **Le témoin bat toutes les corrections, à tous les poids.** » Et `correction_weight` est **réglé** : poids 1 et poids 100 donnent le même 8 % au tiers central — « il ne manquait donc pas un réglage ».
- **rétractations / corrections internes** :
  - §3bis, ⚠⚠ correction du 2026-08-22 : « “le meilleur résultat” n'est pas défendable, et ce document se contredisait » — il notait qu'un écart de 0,03 est dans le bruit puis classait quatre valeurs séparées par **0,09 au plus**. « Un écart sous la résolution ne range rien. »
  - §3bis, audit de `49` : les **quatre** séries sont **non discriminantes de leur plafond** — témoin α mesuré +0,976 contre +1,014 si tout était au bord ; corrigé gen5 +1,034 / +1,014 ; gen5 poids 100 +0,953 / +1,014 ; gen40 +0,887 / +1,014. « Aucune des quatre ne peut dire si son pic reculait ou s'il n'y en avait pas. » Ce qui tient : les quatre sont condamnées ; ce qui ne tient pas : les ordonner entre elles.
  - §5 : la tendance « rembobiner moins fait mieux » (α 0,98 → 0,89, écart à 161 couches −27 %) est marquée « à confirmer par le balayage, pas à annoncer », puis ⚠⚠ « Confirmé par la négative » → `49` : aucune tendance ne peut y être lue.
  - §5 : « Trois leviers de données restent éteints chez nous » est **barré** — « ⭐ Les trois leviers ont été allumés et mesurés » → `26` §9bis (`sdt_weight` 1 et 10, fibres h+v, sdt+fibres).
  - §6 : « ~~**Rien de tout ça n'est encore mesuré.**~~ ⭐ **Mesuré depuis** → `43` : la campagne `spire_suivante.sh` a tourné. »
  - §3 : la ligne « `correction_weight` […] n'avait jamais été réglée ici » est amendée en place — « elle l'est depuis : le §3bis la balaye (poids 1 et poids 100) et le §7 conclut qu'elle est réglée ».
  - §7 : ⚠⚠ « **Aucun des α de ce document n'était interprétable** » — tout ce qui précède a été mesuré sur des fenêtres de 41 et 161 couches, soit 2,05 et 8,05 pas inter-feuilles. La conclusion tient, sa preuve ne tenait pas.
  - §7, fausse piste notée : à 41 couches le témoin rapporte **187,24 µm**, exactement 20 couches = la demi-fenêtre, donc une valeur **censurée**, pendant que les corrigés rendent 154 et 168 « qui sont dedans » — on y lit volontiers que la correction a ramené le pic à l'intérieur, « **la mesure le réfute** » : la saturation du témoin tombait sur une feuille voisine.
- **preuve de lecture intégrale** :
  - lignes 177–178 : « trace passe de **0 à 11 753 auto-intersections** et son α **ne s'améliore pas** (+0,98 → / +1,03). »
  - lignes 270–272 : « fenêtre » l'a masqué. **La mesure le réfute** : dans une fenêtre valide, c'est le témoin / qui a le plus de fenêtres au tiers central. La saturation du témoin à 41 couches tombait / sur une **feuille voisine**, ce qui ne dit rien du mérite de personne. »



Dépôt : `/home/masterlaplace/LplVesuvius`. Sept documents lus intégralement, du premier au
dernier caractère. Lignes mesurées par `wc -l`.

---

### docs/43_la_chaine_des_spires.md

- **lignes** : 593
- **nature** : RESULTAT
- **résumé** : Le document mesure une chaîne de spires produites par `mode: gen_neighbor`,
  chaque spire servant de source à la suivante, toutes jugées dans les mêmes fenêtres par le
  test de convergence (α). Il établit que 4 spires sur 7 convergent à pas de rayon 1,0 et que
  la 7ᵉ casse, puis, campagne après campagne, que le paramètre qui décide n'est pas le pas mais
  la **portée physique du test de sortie** du rayon. Il documente en chemin plusieurs
  hypothèses de son auteur qui ont été publiées puis réfutées par la mesure.
- **conclusions extractibles** :
  - Sur la chaîne à pas de rayon 1,0 : **4 spires sur 7 convergent, 2 sont intermédiaires, et
    la 7ᵉ casse** (spire 06, α = +1,475, « suit la fenêtre »).
  - C'est la première fois du dépôt qu'une surface produite par l'auteur converge ; toutes les
    traces poussées en `mode: seed` — dix-sept essais — sont à α ≈ 1 sans exception.
  - La grille rétrécit à chaque tour : **7,12 → 5,39 cm² en six tours = 24 %, ou 4,0 % par
    tour** (aire de grille) ; à ce rythme la moitié de la surface est perdue en douze tours.
  - Sur l'aire réellement portée par de la matière, l'érosion est de **15,6 % par tour**
    (renvoi à `44` §5), pas 4 %.
  - `vc_tifxyz_selfcross` rapporte `clean_of_transverse_self_intersection: true` et
    `report_only: true` sur les sept spires **sans `pairs_tested` et sans compte de
    croisements** : un portail bâti sur `clean` accepterait ces sept surfaces sans avoir rien
    testé.
  - La repousse (`mode: resume`, 20 générations) rend de la surface — grille 157×145 → 212×200,
    aire **6,71 → 12,47 cm²** — et **dégrade la convergence** : α passe de +0,000 à +0,422 sur
    la spire 01, de +0,190 à +0,573 sur la spire 02.
  - La chaîne de base tient six tours ; **la chaîne repoussée casse au troisième** (spire 03
    repoussée : +1,461, 26,20 cm², 2 921 auto-intersections), et la dégradation accélère
    (+0,42, +0,38, puis +0,93).
  - Le sens `in` n'est **ni meilleur ni pire** que le sens `out` : `in` se dégrade plus vite au
    début (02 et 03 nettement pires) puis se rétablit (spire 05 à +0,000) là où `out` tient
    longtemps puis casse au 06.
  - Corrélation de rang au décalage 1 entre α(tour N) et α(tour N+1), sur les 12 paires des
    deux chaînes cumulées : **ρ = +0,299, p (permutation) = 0,344, puissance à ρ = 0,7 de
    68 %, puissance à l'effet observé (ρ = 0,30) de 15 %.** Verdict : pas de dérive forte ; une
    dérive modérée n'est pas exclue.
  - Un juge à un seul rendu n'existe pas : sur les 18 spires déjà jugées des deux façons,
    `au_bord_relief` donne **ρ = +0,226 (p = 0,360)** contre α, et l'écart médian à 31 couches
    **ρ = +0,204 (p = 0,408)**. Aucune relation détectable.
  - Halver le pas du rayon de 1,0 à 0,5 fait passer la chaîne de 4 spires convergentes sur 7 à
    **6 sur 7 et supprime la rupture** (la spire 06 tombe de +1,475 à +0,583), à érosion
    identique (4,0 % par tour).
  - Le pas du rayon a une **courbe en U** : à profondeur égale (7 premiers tours), α moyen vaut
    +0,357 (pas 1,0), +0,129 (0,5), **+0,102 (0,25)** et +0,327 (0,125) ; α du pire tour vaut
    +1,475, +0,583, **+0,246**, +0,758.
  - Le mécanisme est arithmétique et lu dans `vc_grow_seg_from_seed.cpp` : `neighbor_exit_count`
    (défaut 1) et `neighbor_spike_window` (défaut 2) **comptent des pas** et non une distance,
    donc leur portée physique vaut `exit_count × neighbor_step` — 1,0 voxel = 8,6 µm à pas 1,0,
    0,125 voxel = 1,1 µm à pas 0,125. Seul `neighbor_min_clearance` est exprimé en distance et
    correctement converti (`ceil(min_clearance / neighbor_step)`, ligne 677).
  - Prédiction confirmée : **à pas égal (0,125), changer la seule portée fait passer l'α moyen
    de +0,327 à +0,130** ; deux campagnes de pas différant d'un facteur deux mais partageant la
    portée 0,25 donnent le même α (+0,102 et +0,130), et deux spires sont identiques au
    millième (02 à +0,202, 06 à +0,246). **Ce n'est donc pas le pas qui décide, c'est la
    portée.**
  - Consigne opérationnelle : **la portée du test de sortie doit tomber entre 0,25 et 0,5
    voxel** ; à l'intérieur le dépôt ne sait pas distinguer (les quatre campagnes s'étalent sur
    0,083 quand l'instrument ne discrimine pas à ±0,2 près), en dehors l'α triple.
  - `spike_window` est **inerte** : la campagne qui divise la portée de pic par deux à portée
    de sortie constante rend dix spires identiques une par une, et les maillages sont
    identiques **octet pour octet** sur les quatre spires vérifiées. La source explique
    pourquoi — le message `if (fold_corrections > 0)` (ligne 929) n'apparaît dans aucun journal
    de campagne.
  - `gen_neighbor` n'utilise **aucun** générateur aléatoire (vérifié dans la source), ni
    l'aplatissement, ni le rendu : les résultats sont rejouables au bit.
  - L'érosion vaut **4,0 % par tour pour les quatre campagnes** à profondeur égale, constante
    sur un facteur huit de pas : le pas décide où la surface se pose, pas combien elle en perd.
    Sur l'aire utile, 12,8 à 13,0 % par tour à profondeur égale.
  - Hypothèse énoncée puis réfutée : un pas trop fin ferait s'arrêter le rayon avant la nappe
    suivante — mesuré 115 µm à pas 0,125 sur toute la chaîne, indistinguable des 113 et 114 des
    deux autres.
- **rétractations / corrections internes** :
  - §6quater : « après trois tours, j'avais écrit que ça ne changeait rien » — la conclusion
    publiée « les tours qui ratent ne ratent pas par manque de résolution » est déclarée
    **fausse** ; la campagne complète montre que la différence apparaît là où la chaîne de
    référence cède. Leçon de méthode : les premiers tours d'une chaîne ne discriminent pas.
  - §6bis : la première version du verdict dérive/loterie était « trop généreuse » — elle
    concluait « loterie » dès que la puissance à ρ = 0,7 dépassait 50 %, alors que le test n'a
    que 15 % de puissance à l'effet observé.
  - §6quinquies : la première version de la section, publiée le matin même, annonçait « la
    rupture est repoussée du tour 06 au tour 07 » et **a été retirée** — elle reposait sur un
    verdict à deux millièmes de son seuil (`pas025_spire07`), « un lancer de pièce publié comme
    un résultat ».
  - §6quinquies : « le pas du rayon a un optimum à 0,25 » est corrigé en **« c'est un
    BASSIN »** — désigner la plus basse des quatre campagnes serait « un podium sur un bassin
    plat ».
  - §6quinquies : la phrase « le mécanisme de la dégradation reste inconnu » est barrée et
    corrigée (trouvée dans la source) ; l'hypothèse du rayon s'arrêtant trop tôt, précédemment
    déclarée « réfutée », est requalifiée en « juste en direction » — « c'était une réfutation
    trop rapide ».
  - §6quinquies : « les allocations… » — l'érosion lue sur toute la longueur de chaque chaîne
    semblait suivre le pas (13,2 → 18,0 %) : « c'était entièrement l'artefact de profondeurs
    inégales ».
  - §3 : la note « repousse = repousse » est amendée en « MESURÉE et CONTRE-PRODUCTIVE » (§6).
  - §2 : la réserve « rien ne dit que c'est la spire immédiatement voisine » est amendée par un
    renvoi mesuré à `44` §4 (écart entre nappes de 113 µm).
  - Tâches ouvertes : « repousser entre deux tours » barré (« mesuré, et c'est non ») ;
    « recoller les spires en une seule surface » barré comme **tâche mal posée** (`44` §7) ;
    « pourquoi la 7ᵉ casse : l'érosion ? » barré comme **hypothèse réfutée par un contrôle**
    (`44` §8).
  - ⚠ Le document déclare explicitement ne compter **aucun verdict** dans son tableau final, et
    dit pourquoi : le compte exact « change à chaque campagne, et le recopier dans plusieurs
    documents l'a fait périmer quatre fois dans la même journée ».
- **preuve de lecture intégrale** :
  - ligne 459 (77 % du fichier) : `⭐⭐⭐ **Donc ce n'est pas le pas qui décide, c'est la PORTÉE.** La courbe en U du paragraphe`
  - ligne 579 (13ᵉ ligne non vide avant la fin) : `| 6 | ⚠⚠ ~~pourquoi la 7ᵉ casse : l'érosion ?~~ **hypothèse RÉFUTÉE par un contrôle** : [`44`](44_ou_la_chaine_se_trouve.md) §8. Le simple **numéro** de la spire prédit α mieux que l'érosion, l'arc, l'aire ou n'importe quelle statistique de rendu (ρ = +0,534, et 4 condamnées signalées sur 4 contre 3). Tout ce qu'on a mesuré n'est qu'un proxy de la profondeur dans la chaîne |`

---

### docs/44_ou_la_chaine_se_trouve.md

- **lignes** : 2001 ⚠ (1968 quand la fiche a été écrite ; `etendre_nappe.sh` a reçu sa commande de lancement le 2026-09-04 — elle n'était écrite nulle part, donc l'outil passait pour exécuté par personne)
- **nature** : MIXTE
- **résumé** : Le document mesure d'abord *où* la chaîne radiale de `43` se trouve dans le
  rouleau, et établit que la tâche « recoller les spires » était mal posée : une chaîne radiale
  est une **colonne**, pas une bande. Il construit ensuite, sur des centaines de lignes, la
  chaîne **tangentielle** manquante — projection le long de la tangente plutôt que de la
  normale — et la mesure avec une batterie d'instruments dont plusieurs ne coûtent aucun rendu
  (boîte englobante, pas réellement parcouru, écart de maillages, contact avec la matière,
  plancher du hasard, couverture par la surface publiée). Il explore en parallèle
  l'**extension** (`mode: resume`) et le raccordement des segments publiés, et referme les deux
  voies. Le document contient un très grand nombre de rétractations explicites de son propre
  auteur, dont plusieurs sections entières barrées.
- **conclusions extractibles** :
  - L'angle balayé se lit sur la **flèche** de l'arc, `φ = 2·arctan(2·flèche/corde)`, sans
    approximation petit-angle et **sans connaître l'axe du rouleau** : le rayon s'élimine.
  - La sentinelle d'invalidité des `tifxyz` vaut **`-1`**, pas `(0,0,0)` ; une spire porte
    **deux** maillages (`trace/neighbor_out_*` et `plat/`) ; l'axe circonférentiel **n'est pas
    le même pour toute la chaîne** — `spire00` l'a en colonnes, les huit autres en rangées.
    Décider l'axe une fois faisait rendre des rayons de **312 mètres**.
  - Sur la chaîne à pas 0,25, neuf nappes : la part de sommets valides tombe de **58 % à 23 %**,
    l'aire utile de **4,13 à 1,07 cm²**, l'arc de 21,9 à 8,7 mm. **Aire utile totale : 22,5 cm²
    sur neuf nappes.**
  - **L'écart entre deux nappes consécutives a une médiane de 113 µm** (de 100 à 138), mesuré
    comme distance au plus proche voisin, sans modèle : c'est le seul chiffre du dépôt qui dise
    que la chaîne avance d'une nappe à la fois.
  - **Correction d'un chiffre publié** : l'érosion est de **15,6 % par tour** sur l'aire utile
    (74 % au total en huit tours), pas 4,0 % ; la moitié de la surface est perdue en **quatre**
    tours, pas douze.
  - Le **rayon de la nappe est refusé** sur 9 nappes sur 9 : deux estimateurs indépendants se
    contredisent d'un facteur deux (17–30 mm contre 38–43 mm), et le résidu d'ajustement vaut
    0,5 mm quand les nappes sont à 0,113 mm l'une de l'autre. Sur un cylindre exact ou bruité à
    trois voxels, les deux estimateurs s'accordent à moins de 1 % ; sur une nappe gondolée
    synthétiquement, ils divergent de plus de 40 %. Seul l'ordre de grandeur survit : 2 à 4 cm.
  - Chaque fenêtre couvre **environ 10 % d'un tour**, donc il en faudrait **au moins 8** côte à
    côte pour fermer un seul tour. « Au moins » est le sens du biais : l'angle mesuré est un
    majorant.
  - **Aucun mode de `vc_grow_seg_from_seed` ne fait une chaîne tangentielle** (vérifié dans la
    source) : `gen_neighbor` projette le long des normales de sommet (`:622`, `:684`),
    `expansion` tire un point au hasard près du bord et repart en croissance libre (`:392`) et
    son générateur est semé par l'horloge (`std::default_random_engine rng(clock())`), `resume`
    laisse repousser.
  - Deux sondes bon marché rendent **le même chiffre à 0 µm et à 2,4 mm** (bloc avec matière
    9/10 partout, valeur médiane au point 42–45) : ni « le bloc contient de la matière » ni « la
    valeur au point » ne peut dire si une nappe est sur sa feuille. Raisons physiques : un bloc
    zarr fait 128 voxels = **307 µm** quand les feuilles sont à 10–20 µm.
  - Courbe de portée de la projection tangentielle unique (9 points, rendus de 41 couches) :
    l'**amplitude** monte jusqu'à un maximum à **238 µm** (0,2162, au-dessus du contrôle 0,1929)
    puis décline régulièrement ; le **pic au bord** reste à **0,0 % jusqu'à 381 µm** puis saute
    à **18,4 % à 476 µm** et 61,2 % à 2 381 µm. **Deux grandeurs, deux seuils, qui ne tombent
    pas au même endroit.**
  - À **95 µm par maillon**, trois projections enchaînées étalent le maillage exactement autant
    qu'un seul bond de la même longueur (**×1,01 des deux côtés**) ; à 238 µm par maillon, cinq
    maillons donnent **×2,38** contre ×1,10 pour le bond direct.
  - Le **pas réellement parcouru précède la boîte** comme instrument d'alerte : au quatrième
    maillon de 238 µm il est déjà à +47 % quand la boîte n'est qu'à +22 %. Cinq maillons de
    238 µm ont parcouru **2 044 µm et non 1 190**.
  - Deux maillages issus d'une même source partagent leur paramétrisation, donc se soustraient
    sans rendu : la chaîne 3 × 95 µm et le bond direct finissent à **0,047 spire** l'un de
    l'autre (8,1 µm), la chaîne 5 × 238 µm à **5,33 spires** (922,5 µm).
  - La chaîne courte a un désaccord **modérément localisé** (pire dixième des colonnes = 24 %
    du total, contre 13 % pour un champ uniforme) ; la chaîne longue n'a plus de structure
    (13 % et 10 %) — **14 276 points sur 14 280** au-delà d'une demi-spire.
  - À 286 µm de la source, la chaîne (3 × 95 µm) rend **amplitude 0,2146** contre **0,1807**
    pour le bond direct, alors que le pic au bord va dans l'autre sens (4,1 % contre 2,0 %).
  - **À ~478 µm, le bond quitte sa feuille et la chaîne y reste** : bond direct 0,1140 /
    **18,4 %** de pic au bord, chaîne 5 × 95 µm **0,1491 / 2,0 %** — neuf fois moins de pic au
    bord et +31 % d'amplitude.
  - **L'horizon d'une chaîne à pas de GRILLE est de six maillons, 580 µm** : le pas décroche au
    sixième (×1,11) puis le maillage se détruit — au vingtième il ne reste que **615 points
    valides sur 14 280** (pas 256 397 µm, boîte ×4 976 545). C'est **le centième d'un tour**,
    donc une chaîne tangentielle purement géométrique ne fera jamais le tour d'une feuille.
  - Après trois maillons, la nappe demande presque exactement ce que la source publiée demande
    (**8 003 points recalés contre 8 248**, crête 2,64 contre 2,63, déplacement 6,95 contre
    7,00 vox) ; le bond direct à la même distance en a **968 de moins**.
  - **L'emballement vient du PAS, pas de l'enchaînement.** Fixer le déplacement en voxels coupe
    la boucle de rétroaction : vingt maillons tiennent **96,0 µm (×1,00)**, boîte **×1,55**,
    **14 280 / 14 280 points valides**, distance totale 1 920 µm.
  - **L'emballement géométrique et le départ de la feuille sont deux pannes différentes** :
    avec le pas fixe, la chaîne garde tous ses points et n'a plus que **39,7 %** de points sur
    du papyrus dès 768 µm.
  - Le **plancher du hasard** (la même nappe translatée en bloc dans une direction tirée au
    sort) rend les pourcentages interprétables : segment publié **78,9 % posé contre 48,4 % de
    plancher = +30,6 points** ; chaîne à 1 920 µm **35,4 % contre 37,1 % = −1,7 point, SOUS le
    hasard**. Les deux planchers diffèrent de onze points, donc le plancher se mesure par
    maillage et jamais une fois pour toutes.
  - **Les deux corrections ensemble** (pas fixe + recalage sur la matière à chaque maillon)
    font vivre la chaîne quatre fois plus loin : là où la chaîne sans recalage est morte à
    768 µm (+1,5), celle avec recalage est à **+19,0** à 768 µm et **+15,1 à 1 920 µm**.
  - Le confondant de circularité est **vérifié et écarté** : la mesure sur la projection AVANT
    recalage donne le même « posé » à la première décimale (`projete_8` 64,6 % / +19,1 contre
    `maillon_8` 64,6 % / +19,0), alors que la colonne « demande » vaut 1,60 puis 3,44 vox avant
    et 0,06 après.
  - Poussée à **soixante maillons, la chaîne tient 5,76 mm** : l'avantage sur le hasard passe de
    +29,0 (288 µm) à **+6,9 (5 760 µm)**, avec une pente qui s'aplatit sur le dernier
    millimètre (+6,7 puis +6,9). Coût mesuré : 95 minutes pour les maillons 31 à 60, boîte
    ×5,32.
  - Contre la surface publiée, **la chaîne GLISSE, elle ne SAUTE pas** : l'écart croît de façon
    lisse et monotone et il est du même côté pour **73 %** des points. À 5,76 mm elle est à
    **−28,8 vox = −69 µm** — elle a quitté la bande « même feuille » (40 µm) vers 3,5 mm et est
    encore loin de la bande « feuille voisine » (250 µm). La dérive **décélère** : 15,9 µm/mm à
    768 µm, 14,6 à 1 920 µm, 12,0 à 5 760 µm.
  - La dérive est une **loi extrapolable hors échantillon** : ajustée sur les cinq premiers
    maillons, une **droite par l'origine à 1 paramètre** enlève **68,3 %** de l'erreur des cinq
    derniers (15,5 µm contre 49,0 pour le modèle nul), **p = 0,0015** par tirage. Corrigée, la
    chaîne à 5,76 mm repasse de −69,2 µm à **+21,8 µm**. Elle **sur-corrige** (résiduel 2,3 →
    21,8 µm), et le test extrapole **à l'intérieur du segment publié**, pas au-delà.
  - Sur du **bruit pur**, une droite affine ajustée sur la première moitié enlève encore
    **1,8 %** de l'erreur de la seconde : un critère « mieux que ne rien faire » est satisfait
    par le hasard.
  - Deux explications concurrentes de la dérive écartées par la mesure : la chaîne ne sort pas
    par le **bord** du segment publié (0,0 % jusqu'à 2,9 mm, **0,1 % à 5,76 mm**) ; et l'écart
    n'est pas seulement latéral (48,0 vox total contre **28,8 vox** projetés sur la normale).
  - Le **traçage par croissance était irreproductible** : le générateur des perturbations est
    `thread_local` et semé par `std::random_device` (`GrowPatch.cpp:99-107`), la graine se pose
    par `VC_GROWPATCH_RNG_SEED` (ligne 83) et `set_random_perturbation_seed` est
    `[[maybe_unused]]`, donc jamais appelée. Avec la graine posée et `thread_limit: 1`, deux
    exécutions donnent un maillage **identique octet pour octet** (13,024947 cm² d'aire de méta,
    écart de **0 µm** mesuré par un second instrument).
  - **Étendre le segment officiel triple sa surface utile en la laissant sur sa feuille, et
    c'est rejouable** : 4,28 → **12,97 cm²**, arc 21,9 → 37,2 mm, 0 auto-intersection,
    **α = +0,000** ; la part de sommets valides passe de 59 % à **96 %**.
  - `resume_generations` **n'est lu par personne** : c'est une variable locale (`GrowPatch.cpp`
    lignes 3493 et 3579), le traceur lit `params.value("generations", 100)` (ligne 3428) et la
    clé `--resume-generations` (app ligne 308) est un paramètre mort qui apparaît dans l'aide,
    dans le méta du maillage et dans les scripts de campagne.
  - **Le gros budget ne tient pas** : budget 100 → 12,97 cm², 0 croisement, α = +0,000 ;
    budget 200 → 28,62 cm², **25 036 auto-intersections**, α = **+1,313** ; budget 400 →
    78,30 cm², **168 104** croisements.
  - **α cache une minorité** : l'extension à budget 100 a le même écart médian que la source
    (17,3 µm) mais **9,1 % de ses fenêtres ont leur pic au bord** contre 0,0 % pour la source.
    α étant une médiane, il est insensible à une minorité ; le complément `au_bord_relief` est
    désormais porté par chaque verdict au-delà de **5 %**.
  - `au_bord_relief` est une fraction, donc mécaniquement sensible au rapport périmètre/aire
    (extension à budget 50 : 12 % pour 7,54 cm², contre 9 % pour 12,97 cm²) — mais la taille
    n'explique pas tout, le segment officiel étant le plus petit (4,28 cm²) et à **0 %**.
  - « Enchaîner à budget constant » **n'existe pas** : un `resume` reprend le compteur de
    générations de la surface reprise et s'arrête dès que `generation >= stop_gen`
    (`GrowPatch.cpp:4680`). Le pas *I* doit viser *I × G*.
  - **Découper aide OU nuit, et ce qui décide n'est pas la taille du pas** : budget 200 d'un
    coup → 28,62 cm², 25 036 croisements, α = +1,313, 30 % au bord ; en deux fois 100 →
    50,30 cm², 4 996 croisements, α = +1,040, **56 %** au bord. Budget 100 d'un coup →
    12,97 cm², 0 croisement, α = +0,000, 9 % ; **en deux fois 50 → 20,06 cm², 0 croisement,
    α = +1,806, 20 %**.
  - **Zéro auto-intersection ne veut pas dire « bien posée »** : la pire surface de la campagne
    (α = +1,806) a **0 auto-intersection** et serait passée sans broncher la porte à 100
    croisements/cm².
  - **Rogner la périphérie tardive** ramène la part sans feuille de 9 % à **2 %** (gen ≤ 25,
    6,93 cm²) et à **0 %** (gen ≤ 10, 6,02 cm², soit +41 % de surface propre en plus que la
    source). 33 % des sommets sont à la génération 1 et 41 % viennent des générations 50 à 99.
  - **Ce qui prédit le succès d'une extension est la propreté de la périphérie de sa source** :
    deux sources à 0 % au bord donnent α = +0,000 ; celle à 2 % donne +0,422. Hypothèse
    soutenue par trois points, pas une loi.
  - **Le cycle rogner-étendre ne diverge pas : il converge vers un point fixe autour de 6 cm²**
    de surface propre. Les options du second tour sont 6,02 cm² **propre** (identique au tour
    précédent) ou 7,51 cm² **à 2 %** — et une source à 2 % est mesurée pour rendre +0,422 au
    tour suivant.
  - **Aucun des 15 segments publiés de `PHerc1447` n'est un patch de la même feuille qu'un
    autre** : sur les 105 paires, 51 se recouvrent d'au moins 5 % par boîte englobante, mais
    l'écart médian au plus proche voisin donne **0 paire sous 40 µm**, **2 paires entre 40 et
    250 µm** (79 et 89 µm), 45 à ≥ 318 µm et 4 hors de portée. Coût de le savoir : **4,5 Mo**.
  - Une mesure tentée et **écartée** : l'étalement radial ne mesure pas l'épaisseur mais l'écart
    à la circularité — le segment officiel qui converge parfaitement affiche déjà **12,3 écarts
    entre nappes** d'« épaisseur ».
  - **Le contrôle qui tue l'hypothèse de l'érosion** : sur n = 40 spires et quatre campagnes,
    le simple **indice de spire** prédit α mieux que tout le reste — ρ = **+0,530**, p = 0,001,
    **7/8** condamnées signalées, contre `aire_petite` (+0,460), `arc_court` (+0,442),
    `erosion` (+0,429), `ecart_un_rendu_um` (+0,327) et `au_bord` (+0,265). Contre-exemple :
    `spires_repousse/spire03` a 93 % de sommets valides et un arc de 35,8 mm, et α = +1,461.
  - **Le seuil sur α était écrit DEUX fois** : `test_convergence.py` tranchait à **0,70** et
    `juge_a_un_rendu.py` à **0,75** ; `spires_pas0125/spire04` sort à α = +0,722, donc « suit la
    fenêtre » pour l'un et « pas condamnée » pour l'autre.
  - Une constante `SUIT_LA_FENETRE = 1.6` vivait dans `test_convergence.py`, **définie et
    utilisée nulle part**, portant le nom d'un verdict que α seul décide.
  - **11 verdicts fragiles sur 48 séries distinctes (23 %, presque un quart)**, le plus fragile
    étant `pas025_spire07` à **0,002** de son seuil. La fragilité se répartit très inégalement :
    4/11 pour la campagne à pas 0,125, **0/10** pour les deux campagnes à portée compensée.
  - Le recensement **dédoublonne** : neuf campagnes ont écrit **75** verdicts pour seulement
    **48** séries distinctes ; compter 75 aurait sous-estimé la fragilité (12/75 = 16 % contre
    11/48 = 23 %).
  - La marche guidée par la **matière** (`41`) va jusqu'à **≈ 2,4 mm** et s'arrête parce que le
    bloc se termine, là où la chaîne **géométrique** s'arrête à **580 µm** parce qu'elle se
    détruit. ⚠ Le facteur quatre est une indication et non un résultat : les deux mesures ne
    sont ni sur le même rouleau ni à la même échelle (`PHerc1447` à 8,64 µm contre
    `PHercParis4` à 2,4 µm).
  - ⭐⭐ **Le 2,4 µm de cette page est RATTACHÉ à un volume publié** (2026-09-05) : il était
    posé par cohérence interne, jamais contre un volume déclaré. Désigné par une contrainte
    dure — la boîte englobante du maillage est en voxels du niveau 0, donc **un seul** des
    cinq volumes de `PHercParis4` a une grille assez grande pour la contenir, et il est à
    **2,400 µm**. ⚠ Aucun chiffre de la page ne bouge, la constante était juste ; ce qui
    change est qu'elle est **mesurée**, donc la correction de budget de `77` §10 devient
    calculable en micromètres (69,2 → 66,4 µm).
- **rétractations / corrections internes** :
  - §1 : la **première version du discriminant était fausse** — elle ajustait un cercle et
    divisait la longueur d'arc par le rayon ; sur une ligne droite l'ajustement est singulier et
    rendait un angle de 3,9 rad, donc « une surface plane pour un rouleau ».
  - §2 : « mon témoin testait ma propre hypothèse » — un contrôle écrit depuis la même croyance
    que le code ne peut pas la contredire. La convention `z <= 0 invalid` était écrite noir sur
    blanc par l'outil de vc.
  - §5 : **correction d'un chiffre publié dans `43`** — l'érosion est de 15,6 % par tour, pas
    4,0 %.
  - La première version de `axe_le_plus_long` comparait la somme des tangentes locales, qui
    « rendait le même nombre des deux côtés et ne départageait rien ».
  - Section « ~~⚠⚠⚠ Et enchaîner est STRICTEMENT PIRE qu'un seul bond~~ » : **barrée et
    déclarée dépassée** — le verdict est juste pour un pas de grille de 238 µm et **faux comme
    énoncé sur l'enchaînement** ; à 95 µm par maillon la chaîne ne coûte rien. « Le verdict
    n'appartenait pas à l'enchaînement mais au PAS. »
  - **TROISIÈME correction de la même courbe** (portée tangentielle) : à 3 points « une pente,
    pas un décrochement » ; à 6 points « la chaîne a un pas franc de 240 µm » ; à 9 points
    « maximum puis descente douce, rupture séparée plus loin ». « Chaque forme était plausible
    et chaque forme était fausse. »
  - « La mesure a corrigé ma lecture à l'œil » sur les traînées de la carte de désaccord :
    l'auteur allait écrire « quelques colonnes portent tout », le nombre dit 24 % contre 13 %.
  - **CORRECTION d'une conclusion publiée une heure plus tôt** : « à 1 920 µm, un seul bond
    garde plus de matière que vingt petits » (46,1 % contre 35,4 %) et le **croisement** qui en
    était tiré sont barrés — lus contre leurs propres planchers, les deux sont au niveau du
    hasard (+1,6 et −1,7 points). « Deux mesures mortes comparées sur une échelle brute. »
  - « Mon extrapolation précédente annonçait un zéro vers 7,5 mm. Elle était **trop
    pessimiste** : la courbe ne descend pas linéairement. »
  - « Ma première version de ce contrôle NE POUVAIT PAS se déclencher » (sortie par le bord) :
    elle définissait le bord par la forme de la grille, alors que le maillage publié laisse une
    marge vide de cinq cases — « 0 % au bord » était vrai **par construction**.
  - La phrase « il faut de l'encre » pour savoir si la chaîne suit la bonne feuille est
    corrigée : le point de départ étant un morceau de segment **publié**, la bonne feuille est
    connue sur toute son emprise, et `couverture_publiee.py` répond en quelques secondes.
  - **CORRECTION — le ×3 d'aire utile à α = +0,000 est UN TIRAGE, pas une propriété** : trois
    exécutions censées faire la même chose donnent 0, 596 et 0 croisements et α +0,000, +0,422,
    +0,000. Se propage en arrière : le +0,422 de `spires_repousse` (`43` §6) peut être le même
    mauvais tirage, donc « resume sur une surface projetée dérive » **n'est pas établi**.
  - **Revendication retirée** : « le rayon devient déterminé sur cette surface » était vrai du
    tirage non déterministe (accord à 17 %) et **faux du run reproductible** (38,4 et 47,9 mm,
    25 % d'écart, donc toujours indéterminé).
  - Section « ~~⚠⚠ Mais le cycle ne se referme pas — l'extension est une opération UNIQUE~~ » :
    marquée **(réfuté ci-dessus)**.
  - Section « ~~La question qui reste est celle du pas~~ » : **répondue négativement** —
    « découper 100 en deux nuit gravement ».
  - « Une erreur de ma part, corrigée par la mesure » : rogner l'extension 3 aux mêmes seuils
    que la première (20, 30, 45) rendait exactement la source telle quelle — un `resume` ne
    renumérote pas, il continue le compteur (extension 3 : gens 1–10 héritées puis tout entre
    100 et 109) ; les seuils utiles sont **103 et 106**.
  - « Correction d'un chiffre publié la veille » (segments publiés) : la dernière ligne écrivait
    **49** au lieu de 45, en supposant que les 51 paires recouvrantes avaient toutes été
    mesurées alors que 4 ne l'ont pas été.
  - « La formulation de la réserve dépend du verdict, et ma première version ne le faisait
    pas » : elle disait « et α ne le montre pas » même sur une surface déjà condamnée.
  - Le câblage de la réserve **n'avait pas pris** sur une campagne parce que `lancer.sh` gèle
    une copie du script avant de lancer ; les verdicts ont été re-jugés depuis leurs profils
    existants.
  - Deux défauts d'outillage « de la famille vérification incapable d'échouer » : une colonne
    « médiane » dans l'en-tête pendant que l'extraction rendait `bloc_absent`, la sonde restant
    verte parce qu'elle cherchait le *mot* ; et `$1` dans une fonction `chk` désignant
    l'argument de la fonction et non la colonne.
- **preuve de lecture intégrale** :
  - ligne 1477 (73 % du fichier) : `> **Le cycle rogner-étendre ne diverge pas : il converge vers un point fixe autour de 6 cm² de`
  - ligne 1988 (12ᵉ ligne non vide avant la fin) : `uv run python src/nappe/geometrie_chaine.py --verifier`

---

### docs/45_consistent_with_quantifie.md

- **lignes** : 230
- **nature** : RESULTAT
- **résumé** : Le document outille pour la première fois le « consistent with » du papier
  fondateur d'EduceLab — le seul contrôle sans vérité terrain dont le domaine dispose — en
  mesurant quatre grandeurs typographiques (interligne, échelle de caractère, taux de
  couverture, épaisseur de trait) sur 190 cartes d'encre publiées de quatre rouleaux, sans
  jamais lire une lettre. Il établit que deux grandeurs indépendantes suivent le contraste
  d'encre publié tandis que la séparation des lignes va **à contre-sens**, et il ajoute le
  2026-08-28 un § 7 qui valide (négativement) le transport là où la vérité existe encore.
- **conclusions extractibles** :
  - Le seuil de périodicité est **dérivé et non choisi** : l'autocorrélation d'un bruit blanc
    de *n* points a un écart-type de 1/√n et son maximum sur *k* décalages vaut de l'ordre de
    √(2 ln k)/√n. Une première version écrivait 0,15 en dur.
  - Corpus : PHerc0139 14/38 cartes « écrites » (interligne médian 62 px, trait 4,5 px,
    couverture 0,088) ; **PHerc0172 49/53** (41 px, 2,0 px, 0,201) ; PHerc1667 13/19 (85 px,
    4,0 px, 0,069) ; PHercParis4 44/80 (85 px, 5,7 px, 0,133).
  - Test de transport contre le contraste d'encre publié, sur les 80 cartes de `PHercParis4` :
    couverture **AUC 0,965 / ρ = +0,869** (quasi-tautologique), **épaisseur de trait AUC 0,857 /
    ρ = +0,687**, **netteté du pic AUC 0,753 / ρ = +0,598**, hauteur des composantes 0,682 /
    +0,192, nombre de composantes 0,592 / +0,161, et **séparabilité des lignes AUC 0,319 /
    ρ = −0,281 — elle va CONTRE**.
  - La couverture est quasi-tautologique et il faut le dire : le contraste publié est bâti sur
    des percentiles d'encre, donc elle mesure deux fois la même chose.
  - Le papier met *scale*, *line separation* et *script* dans un même souffle ; **mesurées,
    elles ne vont pas ensemble**. Par quartile de contraste, la séparabilité médiane vaut 0,616 /
    0,489 / 0,448 / 0,500 — association faible et **non monotone**.
  - **§ 7 (2026-08-28) : le transport n'est ni établi ni réfuté.** Sur les 23 tuiles de 256 px,
    aire médiane des taches ρ = **−0,448** (p permutation 0,0312, **p Holm 0,156**), hauteur
    médiane −0,319 (0,1258 / 0,503), composantes +0,284 (0,1848 / 0,554), **épaisseur de trait
    −0,108** (0,6279 / 1,000), couverture −0,097 (0,6529 / 1,000). **Aucune ne survit à Holm** ;
    sous l'hypothèse nulle le hasard met au moins une des cinq sous 0,05 dans **23 %** des cas.
  - L'épaisseur de trait est **la pire des cinq** au § 7 (ρ = −0,108) alors qu'elle est la
    meilleure du § 4 (AUC 0,857) : les deux mesures ne posent pas la même question.
  - La grandeur à prédire est elle-même bruitée (écart-type **0,2243** d'une tuile à l'autre),
    donc toute corrélation mesurée est **atténuée** ; 23 tuiles ne suffisent pas.
  - L'instrument ne dit pas qu'un texte est du grec ni qu'il veut dire quelque chose : c'est un
    contrôle **nécessaire, jamais suffisant**.
  - Le contraste d'encre **n'est pas une vérité terrain non plus** : c'est une autre sortie du
    même pipeline.
- **rétractations / corrections internes** :
  - §5.1 : « ma sonde du masque était posée à l'envers » — la docstring affirmait que sans
    masque « presque tout le papyrus passe pour de l'encre ». **Mesuré : faux (0,066).** Le vrai
    défaut est que sans masque la couverture dépend du **recadrage**.
  - §5.2 : « une marge vierge n'est pas une période » — la première version déclarait
    périodique, avec une netteté de 0,88, un profil dont l'autocorrélation décroît de façon
    monotone : « elle prenait le bord du fragment pour de l'écriture ».
  - §5.3 : « la carte entière est le mauvais domaine » — **64 cartes sur 80** ne rendaient
    aucune période alors qu'elles portent une écriture parfaitement lignée à l'œil, parce que
    deux blocs de texte côte à côte s'annulent quand on moyenne sur toute la largeur.
  - §5.5 : « ma figure contredisait son propre tableau » — le panneau traçait la couverture de
    190 cartes de quatre rouleaux alors que l'AUC porte sur le contraste de 80 cartes d'un seul.
    « Une figure qui contredit son propre tableau est pire qu'aucune figure. »
  - §6 : le résidu « **le transport vers une région sans vérité n'est pas encore fait** » est
    barré et **répondu négativement au § 7** ; le texte d'origine est conservé.
  - §6 : le résidu « **M8 reste ouvert** » est barré, **clos le jour même** par le commit
    `83fa630` → `46`.
  - Le document note que **aucun des cinq défauts n'a été trouvé en relisant le code** : trois
    viennent des témoins synthétiques, un du corpus réel, le dernier d'avoir regardé la figure.
- **preuve de lecture intégrale** :
  - ligne 195 (85 % du fichier) : `⚠⚠⚠ **Une grandeur sur cinq passe sous 0,05 brut, et ça ne veut rien dire.** Cinq tests ont`
  - ligne 229 (2ᵉ ligne non vide avant la fin) : `uv run python src/encre/typographie.py --verifier`

---

### docs/46_le_temoin_negatif.md

- **lignes** : 418
- **nature** : RESULTAT
- **résumé** : Le document construit le contrôle négatif au sens fort qui manque au papier
  fondateur d'EduceLab : une surface dont `38` prouve **géométriquement** (α = +1,01) qu'aucune
  feuille n'est à portée, opposée au segment officiel du même rouleau (α = +0,00), même volume,
  même voxel, même modèle. **Le document a été REFAIT le 2026-08-28 et sa conclusion a changé de
  nature.** Il ajoute ensuite, le même jour, un contrôle typographique dur à deux témoins
  négatifs indépendants.
- **conclusions extractibles** (état COURANT, mesure du 2026-08-28) :
  - **Le modèle répond à ses entrées.** La corrélation pixel à pixel entre les deux cartes vaut
    **ρ = −0,0100** (au lieu de +0,9979 avant correction) : les deux cartes n'ont plus rien à
    voir l'une avec l'autre.
  - **Le détecteur répond avec autant de confiance, davantage même, sur la surface dont on a la
    preuve géométrique qu'elle ne porte pas de feuille** : σ du négatif **0,7111** contre
    **0,5894** pour le positif (rapport des dispersions **×0,83**), et il est plus contrasté
    (**1,869** contre 1,471). « Ce que le détecteur rapporte là est un faux positif **par
    construction**, et **rien dans la sortie ne le distingue** d'une vraie détection. »
  - σ du positif rapporté au modèle qui marche (0,7712) : **76,4 %** (contre 2,4 % avec la
    constante cassée).
  - Écart médian entre les deux cartes : **0,4342**, soit **66,8 %** de ce que chaque carte
    varie, là où deux cartes étrangères en donneraient **95,4 %** — il reste donc un signal
    commun aux deux volumes (la texture du bloc, probablement) que ce témoin ne sépare pas.
  - **La conclusion pour le domaine est plus dure que celle de 2026-08-22, et non plus douce** :
    un modèle bloqué se repère (il rend deux fois la même chose), un modèle qui hallucine une
    structure différente et convaincante sur chaque entrée **ne se repère par aucune inspection
    de sa sortie**.
  - La référence **95,4 %** est **dérivée et non choisie** : deux cartes indépendantes de même
    dispersion σ ont une différence d'écart-type σ√2, dont la médiane absolue vaut
    0,6745·σ√2 = **0,9539·σ**.
  - Les deux entrées sont **pleines et distinctes** (contrôle du contrôle) : moyenne 89,45 /
    σ 39,26 / 93,4 % non nul pour le positif ; 96,86 / 34,95 / 100,0 % pour le négatif — leurs
    dispersions diffèrent de **11,0 %**. L'explication ennuyeuse (deux fenêtres hors des
    données) est écartée par la mesure.
  - Le seuil exact pour porter huit fenêtres au réglage calibré (réduction 8, fenêtre 256) est
    **5128 × 5128 pixels de carte**, pas 2100 : `par_fenetres` balaye
    `range(0, dim - taille//2, taille)`, donc le compte n'est pas `dim/2048`.
  - Première expérience typographique (5128 × 5128, pas 21, 36 471 fenêtres rendues sur 58 564,
    52 minutes) : nos quatre cartes `PHerc1447` **8/12 périodiques (67 %)**, période 30 à 48 px,
    p = **0,0007** contre leur mélange ; **témoin négatif 1/5 (20 %)**, période 20 px,
    p = 0,5000. Mais **l'expérience ne pouvait pas trancher** : à cinq fenêtres, un témoin se
    comportant exactement comme nos cartes rendrait p = **0,0833**, donc pas significatif non
    plus. Il fallait **6 fenêtres** (p = 0,0303) — il a manqué d'**une seule**.
  - Agrandir ne sert à rien (à 5641 px le compte de candidates reste **9**) et déplacer non
    plus : `ab_segments --densite 5128` mesure que la région rendue est **déjà la plus dense
    possible** (59,1 % de matière au coin (0,0), gain +0,00 point). La matière forme une bande
    centrale, donc 5 des 9 candidates tombent sur du papyrus.
  - Un **second témoin indépendant** a été produit le 2026-08-28, avec `GRAINE=""` laissant
    `vc_grow_seg_from_seed` en mode `random_seed` : graine `[2078, 5227, 5113]`, aire tracée
    **13,89 cm²**, 0 auto-intersection, écart 172,8 → 669,6 µm, **α = +0,99** (marge 0,29
    au-dessus du seuil), couches 4321 × 4341.
  - **Le contrôle dur PASSE** (2026-08-28 au soir) : `PHerc1447` 4 surfaces publiées **8/12
    fenêtres périodiques (67 %)**, témoins négatifs 2 traces à α ≈ +1 **1/7 (14 %)**, Fisher
    unilatéral `[8, 4, 1, 6]` → **p = 0,0399**. « La périodicité de nos cartes n'est pas ce
    qu'une surface sans feuille produit. »
  - **La fragilité de ce p se lit avec lui** : une fenêtre périodique de plus au témoin donne
    p = **0,1299** (renverse) ; une de moins, 0,0065 ; une de moins au rouleau, **0,0799**
    (renverse). **Une seule fenêtre suffirait à renverser le résultat.**
  - Le groupement des deux témoins est légitime parce qu'ils ont **deux graines différentes**,
    ce que `fisher_periodicite_groupee` exige et qui serait faux pour deux rendus d'une même
    surface.
  - **Sur `PHerc1447`, l'aval est aveugle** : une différence de surface bien plus grande que
    celle entre une trace fautive et sa réparation ne fait pas bouger le détecteur, donc
    **aucune réparation ne peut montrer de gain à travers lui ici**. Condition d'entrée nommable
    et vérifiable avant de dépenser : σ de la sortie du modèle sur le rouleau visé rapporté aux
    **0,7712**, ce qui coûte une inférence sur une fenêtre.
  - Ce document **n'établit pas qu'il n'y a pas d'encre là** : il établit que ce modèle, sur ce
    rouleau, ne répond pas à ce qu'on lui donne.
- **rétractations / corrections internes** :
  - ⚠⚠⚠ **RÉTRACTATION PRINCIPALE, en tête de document (§ bandeau)** : la mesure du 2026-08-22
    a été faite avec la constante de normalisation que `60` a corrigée — **les piles `uint8`
    arrivaient au modèle 257 fois trop sombres**, donc les deux cartes étaient quasi
    **constantes**, et deux constantes corrèlent parfaitement. **Le `ρ = +0,9979` publié alors
    n'était pas un fait sur le modèle, c'était la signature du bug.** Le titre disait « rend la
    même carte » ; **ce n'est pas vrai**. La conclusion refaite est **différente et plus dure
    pour le domaine** : les deux cartes sont étrangères l'une à l'autre — donc le détecteur
    répond bel et bien à ses entrées — et il répond avec autant de confiance, davantage même,
    sur la surface qui ne peut pas porter de feuille.
  - §2 : le bloc « À REFAIRE — le contrôle positif de cette expérience était plat pour une
    raison instrumentale » (le lecteur divisait des piles `uint8` par 65535) ; « le texte
    ci-dessous est conservé tel qu'il a été publié ».
  - §3 : le tableau porte explicitement les valeurs barrées du 2026-08-22 en regard des valeurs
    refaites : ~~+0,9979~~ → −0,0100 ; ~~0,00038~~ → 0,4342 ; ~~2,9 %~~ → 66,8 %.
  - §3 ter : « ⚠⚠ **Et j'ai d'abord écrit "~2100 × 2100", ce qui est FAUX** » — le seuil exact
    est 5128 × 5128. Puis, deuxième erreur sur le même dimensionnement : 5128 px porte huit
    fenêtres **candidates**, et `fenetres_par_region.py` avertit dans sa propre docstring que le
    masque n'en retient qu'une part — **5 sur 9** ont été retenues. « J'ai écrit l'avertissement
    puis dimensionné sans le suivre. »
  - §3 ter : **CORRECTION du 2026-08-28** sur `rendu_161` — le paragraphe disait « les TIFF sont
    vides, forme `(0,)` », c'est **faux sur les deux points** : 161 fichiers portant **2,0 Go de
    pixels**, tous avec un offset d'index nul, `rendu_161.log` s'arrêtant à la bande 31 sur 45 —
    le rendu a été **tué à 68 %**, il n'est pas vide. La conclusion tient pour une raison plus
    forte : `data/leur_graine/trace/` ne contient **qu'une seule** trace et un seul `seed.json`,
    donc `rendu_41` et `rendu_161` sont la même surface rendue à deux profondeurs.
  - §3 ter : « Tant que cette mesure n'est pas faite, le p = 0,0007 de `60` reste ce qu'il
    dit… » est **barré** — la mesure est faite.
  - §5.1 : le chemin d'impression du verdict « on a mesuré, et ça ne conclut pas » était
    **inatteignable** — il partageait la clé `raison` avec « on n'a pas pu mesurer », donc il
    sortait par le chemin d'erreur, **sans aucun JSON écrit**.
  - §5.2 : « mon critère de "la même carte" était faux, et ce sont les témoins qui l'ont dit » —
    il demandait que l'écart médian soit petit devant l'échelle utile du modèle, critère que
    **deux cartes plates indépendantes satisfont**.
  - §5.3 : « la figure peignait du hasard » — 8784 pixels non finis convertis en entiers donnent
    un octet arbitraire, sur une figure dont toute la thèse est « il n'y a pas de structure ».
  - §5.4 : « mon premier remède se contredisait lui-même » — le commentaire annonçait une teinte
    « hors de la plage utile » et la valeur choisie, 0,5, tombe au **milieu** de cette plage.
- **preuve de lecture intégrale** :
  - ligne 286 (67 % du fichier) : `> ⭐⭐⭐ **LA MESURE EST FAITE — 2026-08-28 au soir. Le contrôle dur PASSE.**`
  - ligne 416 (3ᵉ ligne non vide avant la fin) : `uv run python src/encre/temoin_negatif.py --verifier`

---

### docs/47_le_critere_doit_etre_relatif.md

- **lignes** : 118
- **nature** : RESULTAT
- **résumé** : Le document répond à la tâche `29` N4 — « choisir une référence défendable pour
  le critère du tiers central » — en mesurant, sur 16 traces rendues à deux profondeurs et
  quatre rouleaux, que la question **se dissout au lieu de se résoudre**. La distance à la
  matière est censurée par un plafond qui est le réglage lui-même, et même les critères sans
  plafond dérivent quand seule la profondeur du rendu change.
- **conclusions extractibles** :
  - Le plafond de la distance à la matière vaut **93,62 µm** à 21 couches et **187,24 µm** à
    41 couches — il monte d'un facteur **2,00** pour un facteur 1,95 de profondeur : **il est le
    réglage**.
  - **13 traces sur 16** sont au plafond à 21 couches, **10 sur 16** à 41 couches. Seules
    **2 traces** sont mesurées entre les deux plafonds des deux côtés, et leur écart médian vaut
    **88,939 µm**, soit presque le plafond du rendu bas tout entier.
  - « Un seuil absolu comparé à une valeur censurée ne compare pas deux surfaces, il compare
    deux réglages » — c'est la même troncature que `35` a payée sur le budget de générations,
    dans un **troisième** endroit du dépôt.
  - Un critère **sans plafond** bouge quand même : `au_bord` (16 comparées, 0 censurée) a une
    dérive médiane de **0,075** et max **0,450** ; `part_plates` **0,153** et max 0,250 ; contre
    `ecart_um` (2 comparées, **14 censurées**) 88,939 et 93,620. Une dérive max de 0,450 sur une
    grandeur qui vaut typiquement 0,5, en changeant **uniquement** la profondeur du rendu.
  - **Deux critères ne se transfèrent pas l'un à l'autre** : `ρ(au_bord, part_plates) = −0,528`,
    ils bougent en sens opposés, donc ce ne sont ni la même quantité ni des complémentaires.
  - **Tant qu'une part notable des traces bute sur le plafond, aucune référence n'est
    défendable** — non parce qu'on n'a pas trouvé la bonne, mais parce que la grandeur comparée
    n'est pas celle qu'on croit comparer.
  - Le remède proposé : **le critère doit devenir auto-référentiel**, mesuré à deux profondeurs
    et lu comme un rapport, comme l'exposant α — qui n'a besoin d'aucune référence, d'aucun
    seuil et d'aucune échelle.
  - Ce document **n'établit pas** que la forme relative fonctionne ; il établit que la forme
    absolue ne peut pas.
  - Sur l'arbre entier, **92 séries** ont au moins deux fenêtres et **aucun** profil posé sur
    son bord : le lot suivant n'est pas bloqué par le manque de matière.
- **rétractations / corrections internes** :
  - §4 : un défaut de figure **faisait disparaître la moitié de la censure**. La cohorte mélange
    deux tailles de voxel (8,64 et 9,362 µm), donc il y a **deux plafonds** à chaque profondeur
    (86,40 et 93,62 µm en bas, 172,80 et 187,24 en haut) ; la première version traçait celui de
    l'en-tête du fichier, **un seul**, et les traces de l'autre voxel apparaissaient **sous** le
    plafond alors qu'elles étaient exactement **au** leur. Trouvé en **regardant la figure**,
    pas en relisant le code.
  - §5 : **Correction du 2026-08-22** — le paragraphe disait que « le dépôt en a **deux** »
    (traces rendues à deux profondeurs sans censure). Ce deux est juste pour la **cohorte de 16
    traces** du second axe, **pas pour le dépôt** : l'audit de `49` balaie les fichiers
    `profil*.json` que cette cohorte n'utilise pas — **deux populations disjointes**. Mesuré sur
    l'arbre entier : 92 séries. La correction est « de bonne nouvelle ».
- **preuve de lecture intégrale** :
  - ligne 87 (74 % du fichier) : `> ⭐⭐ **Le critère doit devenir auto-référentiel** : mesuré à **deux profondeurs**, et lu`
  - ligne 116 (3ᵉ ligne non vide avant la fin) : `python3 src/graine/derive_avec_profondeur.py --verifier`

---

### docs/48_ou_monter_lexperience.md

- **lignes** : 421
- **nature** : MIXTE
- **résumé** : Le document ne répond pas à la question centrale du dépôt (« réparer une trace
  sert-il à quelque chose ? ») : il mesure **pourquoi elle n'est pas montable sur ce qui est en
  main**, en croisant trois mesures déjà faites — l'ensemble des rouleaux traçables et
  l'ensemble des rouleaux lisibles ont une intersection **vide**. Il tranche ensuite, par une
  campagne 2×2 croisée répétée quatre fois par cellule, le blocage restant sur `PHercParis4`
  (deux prédictions de surface concurrentes), et découvre en chemin que le budget de
  générations du dépôt a été dimensionné sur un coût de rendu qui n'existe pas.
- **conclusions extractibles** :
  - **L'intersection des traçables (13) et des lisibles (3) est vide (0).** Parts de cartes
    « écrites » : PHerc0139 14/38 = 37 % (non), **PHerc0172 49/53 = 92 %**, **PHerc1667 13/19 =
    68 %**, **PHercParis4 44/80 = 55 %**.
  - « Pas dans la cohorte tracée » n'est pas « pas traçable » : la disjonction dit **où**
    l'expérience doit être montée, pas qu'elle est impossible.
  - `PHerc0172` **ne publie pas de `representations/`**, donc ne peut pas recevoir la campagne
    quelle que soit la qualité de son encre — la recherche de graine part d'une prédiction de
    surface.
  - `PHercParis4` publie **deux prédictions de surface du même scan**, toutes deux à 2,4 µm,
    issues du même volume (`2.4um_PHerc-Paris4_masked.zarr`), générées à deux secondes
    d'intervalle, par **deux modèles différents** : `ps256_trainpy` à seuil 0,45 et `m7_nnunet`
    à seuil 0,2.
  - Les scores internes **ne tranchent pas** : les deux meilleures graines sont aux extrêmes de
    la bande admissible — `ps256` à une occupation de **0,0215** quand le plancher est 0,02,
    `m7` à **0,75** avec une planarité de **1,0** quand le plafond est 0,80 (signature d'une
    prédiction **saturée**).
  - **2×2 croisé, quatre tirages par cellule (seize runs équilibrés)** : `ps256` sur graine
    `ps256` → +1,12 · +1,01 · +0,94 · +1,09, médiane **+1,05** ; `m7` sur graine `ps256` →
    +1,01 · +1,01 · +0,97 · +0,95, médiane **+0,99** ; les huit cellules sur graine `m7` sont
    indécidables. **L'écart entre prédictions passe de 0,17 à 0,06 en répétant** — il a
    *rétréci*, comportement d'une différence due au bruit ; il faudrait au moins **0,20** pour
    distinguer.
  - Le **bruit de tirage** est mesuré et non déduit : l'étendue intra-cellule vaut **0,18** sur
    la cellule la plus dispersée ; le même `vc_grow_seg_from_seed`, sur la même graine, rend
    déjà α de **+0,89 à +1,12**. Ce n'est pas la même quantité que le ±0,2 de `43`, qui est une
    demi-largeur sur un mode déterministe.
  - **Huit candidats tracés, zéro convergence sur huit** : les cinq graines `m7` rendent un
    profil **plat**, les trois `ps256` donnent α = +1,01 · +1,17 · +1,01 ; l'α le plus bas
    obtenu est **+1,01** pour un seuil de condamnation à 0,7. Les propriétés de graine varient
    d'un facteur vingt en occupation et de trois en nombre de voisins ; le résultat ne varie que
    par rouleau.
  - L'instrument **refuse de calculer une corrélation** sur trois α : à huit points, la
    corrélation détectable à 80 % de puissance dépasse **0,84** — « un ρ moyen ne serait pas une
    absence d'effet, ce serait une absence de puissance ».
  - **Les huit aires butent sur le même plafond** : entre 0,3174 et 0,3176 cm², soit **0,06 %**
    d'écart, pour des graines séparées par des kilovoxels dans deux prédictions différentes —
    les huit s'arrêtent à la **génération 59**. L'aire mesure le réglage, pas la donnée.
  - Le plafond de 60 générations a été fixé sur une estimation de rendu à **57 Kio/s**, faite
    sur **un seul échantillon de quinze minutes** ; les mesures suivantes donnent **1108, 1116,
    3848 et 1834 Kio/s** (et le texte cite ailleurs 1108–5861 Kio/s), soit vingt à cent fois
    plus vite. « Tout ce que ce dépôt affirme sur ce rouleau a été mesuré sous un budget
    dimensionné pour un coût qui n'existe pas. »
  - À 200 générations la trace passe de 0,317 à **3,655542 cm²** — onze fois plus, donc la
    troncature est bien levée.
  - Condition d'entrée vérifiable avant de dépenser : σ de la sortie du modèle sur le rouleau
    visé, rapporté aux **0,7712** de référence ; une inférence sur une fenêtre suffit.
  - Ce document n'établit pas que la statistique typographique prouve qu'une carte porte du
    texte, ni que le détecteur répond sur les trois rouleaux lisibles (il n'est mesuré
    directement que sur `PHercParis4` et `PHerc1447`), ni que réparer sert à quelque chose.
  - Reproduction : `GENERATIONS=60 FENETRES="41 161" bash src/outils/tracer_prediction_paris4.sh`
    → `docs/mesures/prediction_paris4_<cas>.json`. ⚠ Les deux fenêtres FONT le test : α se lit
    sur leur rapport, donc une seule rendrait un nombre et non un verdict.
  - ⭐⭐⭐ **Une graine mieux ÉTAYÉE ne trace pas mieux** (2026-09-05, campagne
    `tracer_tous_candidats.sh` qui avait tourné sans être publiée) : **zéro convergence sur
    huit** candidats, étai de **9 à 27 voisins** et occupation de **0,0215 à 0,75** — donc la
    plage est couverte, et les trois candidats à bloc 3×3×3 plein échouent exactement comme
    les deux moins soutenus. `trouver_graine` classe sur la planarité seule et met devant un
    point à 1,0000 sur NEUF voisins là où les suivants ont vingt-sept : trois dix-millièmes
    de planarité contre un facteur vingt d'occupation.
  - ⭐⭐ Signature plus dure que « α ≈ 1 » : pour **7 candidats sur 8** l'écart rapporté vaut
    **exactement la demi-fenêtre** (48,0 = 20 × 2,4 à 41 couches, 192,0 = 80 × 2,4 à 161).
    Un écart égal au bord dans les DEUX fenêtres n'est pas une distance à une feuille, c'est
    l'absence de tout pic — la panne de `49` §2 — et α vaut 1 par identité.
    ⚠ Conclusion **négative et bornée** : rien ne convergeant, aucune propriété de graine ne
    peut prédire une convergence qu'aucune graine n'obtient.
- **rétractations / corrections internes** :
  - §1 : ⚠⚠⚠ **RENVERSÉ LE 2026-08-28.** Le passage écrit depuis la mesure du 2026-08-22 (avec
    la constante corrigée par `60`) est **barré** : « le détecteur rend la même carte
    (ρ = 0,9979) » et « sa dispersion vaut 1,7 % » sont faux. Le détecteur **répond** — σ du
    contrôle positif = **76,4 %**, cartes **étrangères** (ρ = **−0,0100**) — donc **la condition
    d'entrée de ce lot est levée**. Ce qui reste vrai et est même plus dur : le détecteur
    rapporte **plus** de dispersion sur la surface qui ne peut pas porter d'encre (0,7111 contre
    0,5894).
  - §3 : « un défaut à moi, et c'est la sonde réseau qui l'a corrigé » — la première
    recommandation « commencer par `PHerc0172`, 92 % de cartes écrites » est **irréalisable**,
    faute de `representations/`.
  - §4 : **Corrigé le 2026-08-24** — le profil de `m7` n'est pas plat, il est **vide** : sa pile
    rendue n'a aucun pixel allumé, parce que la graine vient du produit `…-m7-L2-`, au niveau 2,
    rendu contre le niveau 0.
  - §4 : **Corrigé le 2026-08-24** — les huit cellules « indécidables » sont **huit rendus
    vides** (max 0, 0,0 % allumé des deux côtés) ; ce n'est pas la prédiction qui décide, c'est
    la **graine**. « Le `L2` était dans le nom du fichier depuis le début, et rien ne le
    lisait. » Donc « cet endroit n'a pas de feuille » **n'a jamais été mesuré : on n'a jamais
    regardé cet endroit**.
  - §4 : **Corrigé le 2026-08-23** — la plupart des cellules rendent l'identité **+1,0135** du
    couple de fenêtres, donc leur accord est **arithmétique et non empirique** ; l'étendue
    intra-cellule de 0,18 mélange deux choses non séparées. « **La conclusion "c'est l'endroit
    qui décide" n'est plus portée par ces nombres.** »
  - §4 : **Corrigé le 2026-08-23** — « les trois α de ce tableau n'en sont pas » : les trois
    candidats `ps256` ont eux aussi leur fenêtre étroite sous le seuil de détection, et deux
    d'entre eux ont *les deux* écarts posés exactement sur la demi-fenêtre. **Vingt séries de
    l'arbre rendent exactement +1,0135**, qui est log(192/48)/log(161/41). La conclusion
    pratique ne bouge pas (un appui au bord condamne la trace), c'est la **quantification** qui
    tombe ; il reste **une** série `PHercParis4` sur 27 dont les deux appuis mesurent
    (`paris4_croise/ps256_sur_graine_ps256`, α = **+1,12**).
  - §4 : « c'est ce rapport qui a corrigé mon propre diagnostic » — le « plus de douze heures »
    de rendu était une extrapolation depuis un seul échantillon de quinze minutes ; le rendu
    suivant a écrit **148 Mo en 131 s = 1108 Kio/s**, vingt fois plus. L'auteur déclare ne pas
    savoir ce qui explique l'écart (localité contre variabilité réseau, non séparées).
  - §4 : « je n'ai **pas** inventé un score composite pour reclasser : choisir la pondération,
    c'est choisir la réponse avant de l'avoir mesurée » — les huit candidats ont été tracés.
- **preuve de lecture intégrale** :
  - ligne 346 (78 % du fichier) : `> ⭐⭐ **Zéro convergence sur huit.** L'α le plus bas obtenu est **+1,01**, pour un seuil de`
  - ligne 419 (3ᵉ ligne non vide avant la fin) : `python3 src/graine/eligibilite_aval.py --verifier`

---

### docs/49_alpha_ne_separe_pas_deux_pannes.md

- **lignes** : 131
- **nature** : RESULTAT
- **résumé** : Le document établit que le verdict α = 1 « suit la fenêtre » confond **deux
  pannes distinctes** — le pic qui recule avec la fenêtre, et le pic qui n'existe pas — parce
  qu'un profil dont les deux lectures sont les bords de fenêtre rend α ≈ 1 **par identité
  arithmétique**, quoi qu'il y ait dans le volume. Il corrige l'instrument (refus au lieu de
  conclusion), audite tout l'arbre, et montre que la moitié rassurante tient : aucun verdict
  positif n'est touché.
- **conclusions extractibles** :
  - À 41 couches la demi-fenêtre vaut 20 × 2,4 = **48 µm**, à 161 couches 80 × 2,4 = **192 µm**.
    Une trace lisant `41c→48.0  161c→192.0` a ses deux lectures **au bord de la fenêtre**, donc
    leur rapport vaut celui des fenêtres et **α = 1,01 sort par identité arithmétique**.
  - Le profil le disait déjà : `amplitude_mediane = 0,0` pour un seuil `amplitude_min = 0,02`,
    `au_bord = 1,0`, `au_bord_relief = nan`. « Il n'y a pas de pic. Il n'y en a nulle part. »
  - « Le pic s'éloigne avec la fenêtre » est une phrase sur un pic : quand il n'y a pas de pic,
    elle **n'a pas d'objet**, et elle est affirmée avec la même assurance que sur une vraie
    mesure.
  - Audit de tout l'arbre : **225 profils lus dans 114 séries**, **21 profils dont l'écart EST
    le bord de la fenêtre**, **15 profils plats**, **4 séries dont aucune fenêtre ne mesure
    rien**, **24 séries sur 111 jugées** dont α ne sépare pas les deux pannes.
  - Ces totaux **bougent** (l'audit balaie l'arbre, chaque campagne en ajoute) : ils valaient
    217 / 110 / 20 à l'écriture. Ce qui ne bouge pas, ce sont les deux bornes suivantes.
  - **Les deux populations ne se recouvrent même pas** : le plus petit α non discriminant vaut
    **+0,8729**, le plus grand α convergent **+0,4222**, et **0 série convergente** n'est
    concernée.
  - **Aucun verdict positif n'est touché** : ce qui perd son pouvoir de discrimination est
    exactement le verdict « suit la fenêtre », et ses deux causes possibles condamnent la trace
    toutes les deux. La conclusion pratique tient ; c'est la **formulation** qui sur-affirme.
  - L'audit balaie les profils **présents sur disque**, pas ceux qui ont produit les tableaux
    publiés : `data/spires_pas025/spire03` porte des profils de **14 h 29** alors que le verdict
    tabulé par `43` date de **08 h 02 le même jour**. Les deux sont justes et ne parlent pas du
    même run.
  - Une campagne qui réécrit sa propre destination **détruit la preuve** derrière un tableau
    déjà publié : les verdicts survivent dans `docs/`, les profils non. La règle « un run à
    paramètres différents prend sa propre destination » vaut aussi pour un run aux **mêmes**
    paramètres, puisque le traceur est un tirage.
  - Pour `38` (α = +1,01 sur notre trace) : sa série a quatre fenêtres et **un seul de ses
    profils est encore sur disque** — celui à 41 couches, amplitude **0,0194** pour un seuil de
    0,02, écart **172,80 µm**, exactement la demi-fenêtre à 8,64 µm. Les trois autres ne sont
    pas dans l'arbre, donc **on ne peut pas les vérifier**, ce qui est par la règle du dépôt une
    anecdote. Le verdict pratique survit, mais l'affirmation que la surface **coupe
    l'empilement** repose sur la géométrie du rendu et non sur ce profil.
  - Pour `46` (le témoin négatif) : **le témoin tient** — un profil plat veut dire qu'aucune
    structure de feuille n'est dans la fenêtre, et cette prémisse est la même sous les deux
    lectures.
  - Les 20 séries listées sont toutes des traces **déjà condamnées** ; aucune n'était présentée
    comme un succès.
  - Le remède qui compte n'est pas d'avoir mieux regardé : c'est que **l'instrument lise
    lui-même ce que le profil dit et refuse** (`test_convergence.py` accepte désormais
    l'amplitude et le seuil de détection, et un chemin `--profil` construit la série depuis les
    fichiers de profil au lieu de recopier les écarts à la main).
- **rétractations / corrections internes** :
  - Le document est lui-même une rétractation d'instrument : le verdict « SUIT LA FENÊTRE — le
    pic s'éloigne avec la fenêtre — il n'y a aucune feuille à portée, la surface est posée en
    travers de l'empilement » est déclaré sans objet quand le profil est plat, et remplacé par
    un refus explicite « INDÉCIDABLE — profil PLAT ».
  - §4 : l'affirmation de `38` selon laquelle la surface **coupe l'empilement** est rétrogradée
    — elle repose sur la géométrie du rendu et non sur le profil, dont trois fenêtres sur quatre
    ne sont plus vérifiables.
  - §5 : « c'est en les recopiant [les écarts] que j'ai lancé un verdict sur un profil plat sans
    le voir ».
  - §3 : l'auteur signale que les totaux publiés dans ce document sont **périssables** et ont
    déjà grandi entre l'écriture et la publication (217/110/20 → 225/114/21).
- **preuve de lecture intégrale** :
  - ligne 88 (67 % du fichier) : `> ⚠ **La vraie leçon est en amont** : une campagne qui réécrit sa propre destination détruit`
  - ligne 129 (3ᵉ ligne non vide avant la fin) : `python3 src/commun/audit_profils_plats.py --verifier`



Sept documents lus du premier au dernier caractère (`wc -l` relevé avant chaque lecture).

---

### docs/50_le_rendu_attendait_la_memoire.md
- **lignes** : 363
- **nature** : RESULTAT
- **résumé** : Un rendu de 1 h 58 sur une surface de 3,656 cm² n'était pas limité par le calcul mais par la mémoire : 28,2 Go de RSS sur 31,8 de RAM, 23,7 % d'un cœur sur 22 disponibles. La cause est le défaut `--cache-gb 16`, jamais posé dans aucun des 28 appels à `vc_render_tifxyz` du dépôt, combiné à des tampons `float32` qui croissent avec l'aire × la profondeur. Un étalonnage de 15 rendus établit que `--cache-gb 1` donne le pic le plus bas et la médiane la plus basse à sorties `sha256` identiques, et un contrôle de résolution montre que la pyramide rend le même nombre à deux niveaux (écart 0,02 pour une résolution de 0,20). Le document se corrige ensuite deux fois : les α qu'il publie ne sont pas des α, parce que leur fenêtre étroite ne mesure rien.
- **conclusions extractibles** :
  - Relevé sur le processus vivant après 1 h 58 de rendu de 3,656 cm² : RSS 28,2 Go sur 31,8 de RAM, mémoire libre 274 Mo, cache de pages écrasé à 442 Mo, swap 3,4 Go, CPU moyen 23,7 % d'un cœur, 22 cœurs disponibles, 59 threads.
  - Le cache de chunks vaut 16 Go par défaut (`--cache-gb arg (=16)`), et aucun des 28 appels à `vc_render_tifxyz` du dépôt, répartis sur 14 scripts, ne réglait cette valeur.
  - Sur la petite surface le pic sature à 4,53 Go même à `--cache-gb 16` : le cache est alloué paresseusement et ne se remplit qu'à hauteur de ce que la surface touche.
  - L'en-tête TIFF du rendu terminé de la petite surface donne 2361 × 2341 pixels pour 0,317 cm² ; le rapport d'aire avec la grande vaut 3,656 / 0,317 = 11,5×, donc la grande fait 64 Mpx par tranche.
  - Mémoire attendue : tampons `float32` 9,7 Go à 41 tranches et 38,2 Go à 161 tranches ; total attendu 25,7 Go et 54,2 Go ; observé 28,2 Go à 41 tranches.
  - La fenêtre de 161 couches fait 38,2 Go de tampons à elle seule sur une machine de 31,8 Go, quel que soit `--cache-gb` : la mesure était impossible, pas lente.
  - Étalonnage, 15 rendus : `--cache-gb 1` → 71 s médian, étendue 13,1 s, pic RSS 1,81 Go ; 2 → 110 s, 61,7 s, 2,98 Go ; 4 → 118 s, 21,9 s, 4,36 Go ; 8 → 141 s, 23,8 s, 4,53 Go ; 16 (défaut) → 135 s, 22,6 s, 4,52 Go.
  - Les quinze sorties de l'étalonnage sont identiques au `sha256`.
  - La conclusion sur le temps penche sans trancher : l'écart entre valeurs (70,3 s) ne dépasse l'étendue intra-valeur (61,7 s à `--cache-gb 2`) que d'un facteur 1,14 ; la mémoire, elle, tranche (1,81 contre 4,53 Go).
  - Ce que le plafond change pour la grande surface : fenêtre 41 au défaut 25,7 Go (swap), fenêtre 41 à `--cache-gb 1` 10,7 Go (tient), fenêtre 161 à `--cache-gb 1` 39,2 Go (ne tient pas).
  - Contrôle de résolution sur 0,317 cm² : niveau 0 (voxel 2,4 µm, fenêtres 41 / 161) rend +0,91 ; niveau 1 (voxel 4,8 µm, fenêtres 21 / 81) rend +0,89 ; écart 0,02 pour une résolution déclarée de 0,20.
  - Le nombre de tranches doit être divisé par 2^g et `--voxel-um` multiplié ; l'arrondi doit garder une fenêtre impaire — avec l'arrondi pair l'écart entre niveaux valait 0,10, avec l'arrondi impair il tombe à 0,02.
  - Mémoire de la fenêtre profonde : 38,2 Go au niveau 0 (impossible), ≈ 4,8 Go au niveau 1 (tient largement).
  - Effet du plafond de générations, même graine, même maillage, même niveau : 60 générations → 0,317 cm², α = +0,89 ; 200 générations → 3,656 cm², α = +0,95. Variation +0,06 pour un bruit de tireur de 0,16, donc sous le bruit.
  - L'aire a bien été multipliée par onze et demi : le plafond bornait la surface, pas le verdict.
  - Contrôle de résolution sur la grande surface : 0,317 cm² niveaux 0 et 1 → +0,91 / +0,89, écart 0,02 ; 3,656 cm² niveaux 1 et 2 → +0,95 / +1,01, écart 0,06. Les deux écarts restent sous la résolution de α (0,20).
  - La petite surface ne peut pas valider le niveau 2 : à 9,6 µm elle ferait 590 px de côté, sous la fenêtre d'analyse de 1024.
  - Décompte des heures : tentative niveau 0 à 161 couches → 4 h 32 pour rien (toutes les tranches pré-allouées, index jamais écrit) ; mesure niveau 1 deux fenêtres → ~2 h, α = +0,95 ; mesure niveau 2 de contrôle → ~2 min, α = +1,01 ; l'image de comparaison → 40 s.
  - Un rendu orphelin de la veille tournait encore 4 h 32 plus tard, à 24,6 Go, laissant 274 Mo à tout le reste.
- **rétractations / corrections internes** :
  - §2 : « J'ai d'abord écrit que la cause, c'est `--cache-gb 16` » — corrigé, l'étalonnage dit « à moitié » (allocation paresseuse, plafond atteint et non payé).
  - §6 : le point « la pyramide sauve la fenêtre profonde » passe d'inconnue à mesuré (§7).
  - §7, encadré « ⚠⚠ Corrigé le 2026-08-23 : ces deux nombres ne sont pas des α » — les deux séries `controle_resolution#g0` et `#g1` ont leur fenêtre étroite sous le plancher, appuis *plat / mesure*, borne **aucune** ; ce qui survit est « le même calcul à deux résolutions rend le même nombre », ce qui tombe est d'appeler ce nombre un α.
  - §8, encadré « ⚠⚠ Corrigé le 2026-08-23 : ces deux α ne portent pas de verdict non plus » — `paris4_plafond/ps256_c2_g60#g1` appuis *plat / mesure* (borne aucune) et `ps256_c2_g200#g1` appuis *au bord / mesure* (borne majorant). La comparaison budget à budget garde son sens ; « α passe de +0,89 à +0,95 » sur-affirme.
  - §9 : correction méthodologique — l'image de comparaison aurait pu être obtenue à n'importe quel moment des quatorze heures précédentes ; le script supprimait le rendu après en avoir tiré son profil.
- **preuve de lecture intégrale** :
  - ligne 219 : « pas, et le décalage serait d'une demi-tranche par niveau, en silence. La mesure l'a »
  - ligne 355 : « src/outils/controle_resolution.sh                   # la pyramide préserve-t-elle α ? »

---

### docs/51_une_pente_a_deux_appuis.md
- **lignes** : 508
- **nature** : RESULTAT
- **résumé** : Une pente a deux appuis, et un appui dont la fenêtre ne mesure rien n'en est pas un ; le refus de `49` agrégeait les amplitudes par un maximum et ne voyait donc pas son propre cas. Le recensement de tout l'arbre trouve 138 séries jugeables dont 39 rendent un verdict que leurs appuis ne portent pas, et vingt séries rendent exactement le même nombre — l'identité arithmétique +1,0135 de leur couple de fenêtres. Le document mesure ensuite quel couple de fenêtres pourrait porter une pente, achète le couple prédit, constate qu'il ne porte pas non plus, et trouve en chemin un bug de son propre instrument sur le second bord d'une fenêtre paire. Il dégage enfin un signal binaire (relief de la fenêtre étroite) qui sépare 0/75 des convergentes de 34/63 des condamnées, puis retire une heure après publication le seuil qu'il venait d'offrir au README public.
- **conclusions extractibles** :
  - Les trois candidats `ps256`, publiés dans `48` avec α = +1,01 · +1,17 · +1,01, ont tous leur fenêtre étroite sous le seuil de détection : amplitudes 0,0175, 0,0193 et 0,0138 pour un seuil de 0,02.
  - Quand les deux appuis sont au bord, α vaut log(192/48)/log(161/41) = 1,013497 — une propriété du couple de fenêtres et de rien d'autre.
  - Vingt séries indépendantes (graines séparées par des kilovoxels, deux prédictions, plusieurs tirages) rendent α = +1,0135 à la quatrième décimale : ce n'est pas une mesure robuste, c'est une mesure absente.
  - Recensement de l'arbre : 138 séries jugeables ; 92 à deux appuis mesurés (α exact) ; 16 appui étroit au bord (α majorant) ; 0 appui large au bord (α minorant) ; 30 sans aucun appui qui porte ; 39 séries dont le verdict ne tient plus ; 7 sauvées par le signe de la borne ; 75 convergentes ; 0 convergente perdue.
  - Sur les 27 séries `PHercParis4` de l'arbre, 26 tombent ; il en reste une qui condamne, `paris4_croise/ps256_sur_graine_ps256`, α = +1,12, borne exacte, verdict *suit la fenêtre*.
  - `data/leur_graine/rendu_161` : 161 fichiers, 1,89 Gio sur disque, tous illisibles — en-tête `II*\0` correct puis offset du premier répertoire d'image à `0x00000000`, malgré 12,4 à 12,8 Mo de charge utile par fichier ; confirmé par `tifffile` et PIL. `rendu_41` au même endroit s'ouvre : 41 fichiers, une page, 5641 × 5721.
  - `data/leur_graine/profil_41c.json` a un écart de 172,80 µm pour une demi-fenêtre de 20 × 8,64 = 172,80 µm et une amplitude de 0,0194 pour un seuil de 0,02 : appui au bord et plat.
  - Les six séries retrouvées : `controle_resolution#g0` +0,9104 (plat/mesure, borne aucune) ; `controle_resolution#g1` +0,8919 (plat/mesure, aucune) ; `paris4_plafond/ps256_c2_g200#g1` +0,9489 (au bord/mesure, majorant) ; `#g2` +1,0147 (au bord/mesure, majorant) ; `ps256_c2_g60#g1` +0,8919 (plat/mesure, aucune) ; `fenetre_profonde/ps256_c0#g1` +1,3870 (plat/au bord, aucune).
  - Fenêtre utilisable : 96 séries ont un couple confortable disponible, 9 un couple sans marge, 33 exigent de rendre une fenêtre plus profonde.
  - Pour les trois candidats `PHercParis4`, la cible vaut 73,9, 72,6 et 74,6 couches avec un facteur d'extrapolation de ×1,00 (donc une interpolation dans l'intervalle 41→161 déjà mesuré).
  - La couche tracée étant au centre, une fenêtre de demi-largeur n compte 2n+1 couches : 81/41 = 1,976, sous le rapport 2 exigé — un couple utilisable exige un saut d'un facteur quatre en demi-fenêtre, d'où (41, 161) aujourd'hui et (81, 321) demain.
  - Effet de la pyramide sur l'amplitude (voxel 2,4 → 4,8 µm) : à 99,6 µm, 0,0146 → 0,0147 (+0,4 %), même camp (sous le plancher) ; à 387,6 µm, 0,0463 → 0,0360 (−22,1 %), même camp (au-dessus).
  - Le couple (81, 321) rendu au niveau 1 : 196,8 µm / 41 tranches / amplitude 0,0125 (sous le plancher) / 1 fenêtre d'analyse ; 772,8 µm / 161 tranches / 0,0985 (au-dessus) / 1 fenêtre.
  - Sur la grande surface (3,656 cm², 4001×3991 px au niveau 1), avec 225 fenêtres d'analyse : 100,8 µm / 21 tranches / 0,0068 (sous) ; 388,8 µm / 81 tranches / 0,0267 (au-dessus). La platitude de la fenêtre étroite n'est donc pas un artefact de la petite surface.
  - Avec β = +1,01 sur la grande surface, la plus petite fenêtre qui dégage le plancher est à 81 tranches (387 µm) et son double à 163 (782 µm) ; la loi mémoire donne 10,4 Go pour 4001×3991 × 163, qui tiennent dans les 31,8 Go de la machine.
  - Le couple admissible rendu au niveau 2 (41 et 83 couches, 796,8 µm de portée, 25 fenêtres) rend α = +1,06 ; après correction du bug de bord, la fenêtre de 41 couches a un écart de 182,4 µm pour des bords {182,4 · 192,0} — appui au bord — et celle de 83 couches un écart de 384,0 µm pour un bord {393,6} — mesure : borne majorant, donc le couple acheté ne porte pas de verdict.
  - À 100,8 µm, à 384 µm et à 796,8 µm de portée, 100 % des fenêtres ont leur pic sur un bord de pile.
  - Contraste : 0 / 75 séries convergentes ont leur fenêtre étroite plate, contre 34 / 63 séries condamnées ; la plus basse série convergente est à 2,25× le plancher, la médiane des condamnées à 0,94×.
  - Comparaison des deux signaux : amplitude sous le plancher → 0 / 75 convergentes et 34 / 63 condamnées ; pic au bord sur ≥ 90 % des fenêtres (`edge_pinned`) → 6 / 75 et 39 / 63.
  - Le contraste n'est pas parfait dans l'autre sens : 29 séries condamnées ont une fenêtre étroite qui mesure — la condition est suffisante, non nécessaire.
  - Effet de la fenêtre d'analyse sur une pile inchangée : 1024 px → relief 0,046 ; 512 px → 0,081 ; 256 px → 0,146 ; exposant −0,830, rapport ×3,16 entre les extrêmes.
  - Les segments publiés de Scroll1 lisent 0,74 à 0,85, contre 0,08 à 0,19 pour nos séries convergentes — un facteur dix sans explication physique.
  - Témoin positif : les séries convergentes n'ont aucun des deux appuis au bord (sur toutes celles vérifiées) quand nos traces `PHercParis4` ont 100 % de leurs fenêtres au bord ; amplitudes 0,08 à 0,19 contre 0,007 à 0,046.
  - L'amplitude brute des deux familles n'est pas directement comparable : les séries convergentes sont à 31/81 couches de 8,64 µm (699,8 µm) et les nôtres à 81 couches de 4,8 µm (388,8 µm).
- **rétractations / corrections internes** :
  - §1 : la règle du maximum d'amplitude de `49` est juste pour « y a-t-il quelque chose ici ? » et fausse pour « quelle est la pente ? ».
  - §4 : « Ce tableau a d'abord annoncé 132 séries, et il en manquait six » — deux conventions de rangement, clé de série corrigée pour inclure le niveau. (⚠ Note de lecture : le corps du §4 écrit « quatorze séries ont leur appui étroit au bord » quand son propre tableau en annonce 16 ; le document ne signale pas cet écart.)
  - §5 : la conclusion du 2×2 de `48`, « ce n'est pas la prédiction qui décide, c'est l'endroit », ne tient plus — la plupart des cellules rendent l'identité +1,0135, donc leur accord est arithmétique et non empirique ; l'« étendue de tirage » de 0,18 mélange deux choses non séparées.
  - §5 : les α que `50` publie pour la pyramide (+0,91 contre +0,89, écart 0,02) et pour le plafond (+0,89 → +0,95) ne portent aucun verdict ; celle à 200 générations porte en plus une borne majorant sur une condamnation, donc elle ne tient pas.
  - §5 : l'α le plus cité du dépôt (+1,01 de `38`, repris par `N5` et `M8` de `29`) n'est pas jugeable ici — un seul de ses profils est encore sur disque, cause nommée le 2026-08-25 (les 161 fichiers de `rendu_161` sont illisibles).
  - §6ter : « ⚠⚠⚠ Faux, et je l'ai failli publier » — l'α = +1,06 annoncé avec deux appuis mesurés venait d'un bug de l'instrument (une fenêtre de N tranches centrée n'est pas symétrique quand N est pair ; l'écart de 182,4 µm est 19 × 9,6, l'autre bord). Corrigé par `bords_um`.
  - §6ter, second défaut : `juger_serie` prenait les extrêmes (11/83) et jetait le couple pour lequel un rendu venait d'être payé ; il retient désormais le plus large couple dont les deux bouts mesurent et dit lequel.
  - §6 (encadré) : la prédiction de fenêtre est l'extrapolation d'un modèle non réfutable (deux profondeurs, aucun résidu) ; le pas suivant est de rendre une fenêtre intermédiaire et de mesurer.
  - §6bis : « La prédiction a été mesurée, et elle était fausse » — mais deux choses ont changé à la fois (profondeur et niveau), donc le run ne réfute pas proprement la loi de puissance.
  - §6 (tableau pyramide) : la première version appariait par profondeur seule et rapportait « −53,8 % » en comparant deux traces sans rapport ; l'outil exige désormais `--niveaux <dossiers>`.
  - « Corrigé une heure après l'avoir publié » : le seuil de 2,25 fois le plancher est retiré du README public — il venait de fenêtres de 1024 px et était offert à un outil qui lit 128 px.
  - §7 : le document n'établit pas que la fenêtre de 41 couches soit trop étroite pour ce rouleau, ni que les 26 séries tombées soient fausses (un verdict retiré n'est pas un verdict inversé), ni que le signe suffise toujours.
- **preuve de lecture intégrale** :
  - ligne 309 : « ## 6ter. ⚠⚠ Le couple acheté ne porte pas non plus, et un bug de l'instrument l'a d'abord caché »
  - ligne 500 : « # le couple admissible, sur la grande surface »

---

### docs/52_calibrer_sur_son_corpus.md
- **lignes** : 208
- **nature** : RESULTAT
- **résumé** : Trois nombres ont été transportés hors de la géométrie qui les avait produits en une seule nuit, aucun trouvé en relisant ; le remède est mis dans le code à trois endroits (l'outil écrit sa géométrie, le calibrateur refuse deux géométries dans un même fichier, la figure l'imprime). Le refus paie au premier usage réel : le corpus publié de Scroll1 n'est pas homogène (80 segments à 109 couches, 1 à 6). La calibration à 128 px × 109 couches sur 80 segments donne un relief médian de 0,744, et notre trace `ps256_c0` relue à cette même géométrie donne 0,1978 — dix fois le plancher, mais premier percentile de son propre rouleau. La ligne `m7` du tableau des candidats est corrigée en cours de document : elle mesurait du vide.
- **conclusions extractibles** :
  - Le relief est lu sur une moyenne de patch, donc il dépend de la profondeur (exposant +1,01) et de l'étendue dans le plan (exposant −0,830).
  - La profondeur du corpus n'est pas « 65 couches » de mémoire : elle vaut 109.
  - `calibration_corpus` a refusé le balayage complet : « layers n'est pas unique dans ce fichier : ['109', '6'] ». Sur les 81 segments de `Scroll1`, quatre-vingts sont lus sur 109 couches et un sur 6.
  - Calibration à 128 px × 109 couches sur 80 segments : relief minimum 0,040, médiane 0,744, maximum 0,975, 0 sous le plancher de 0,02 ; `edge_pinned` minimum 0,000, médiane 0,073, maximum 0,254, 0 au-dessus de 0,90.
  - Le corpus publié se tient à ×2 du plancher au plus bas, ×37 à la médiane, ×49 au plus haut.
  - `edge_pinned` n'atteint jamais, sur ce corpus, le seuil de 90 % auquel il avait été déclaré fautif : sur cet instrument, les deux signaux ne se départagent pas.
  - Un segment publié est à ×2 du plancher : `20260701183151-w128-129`, relief 0,040, `material` 0,49 ; le second plus bas est déjà à 0,373, soit ×19.
  - `Scroll 1` est `PHercParis4` — le corpus calibré est celui du rouleau sur lequel toutes nos traces ont échoué.
  - Notre trace `ps256_c0` reprofilée à 128 px × 109 couches donne un relief de 0,1978, soit ×9,9 le plancher, rang 1ᵉʳ sur 80 ; corpus médiane 0,7441 (×37,2), minimum 0,0400 (×2,0).
  - Lue à 1024 px la même trace donnait 0,046 : la platitude était en partie un artefact de la fenêtre de lecture.
  - Notre trace est au premier percentile de son propre rouleau, à ×0,27 de la médiane publiée ; un seul segment publié fait moins bien.
  - Les trois `ps256` c0…c2, relus à la géométrie du corpus, donnent 0,164 – 0,198, soit ×8,2 – ×9,9, tous au rang 1 sur 80.
  - Le correctif d'instrument ne déplace pas le chiffre des `ps256` d'un dix-millième : 0,19779944 avant comme après.
  - La sous-fenêtre est calculée et centrée : une pile de 161 couches lue sur 109 laisse 26 de chaque côté, et la couche tracée est le milieu de la sous-fenêtre.
- **rétractations / corrections internes** :
  - §6, encadré « ⚠⚠ CORRIGÉ le 2026-08-24 » : l'affirmation « les cinq `m7` lisent exactement zéro, même à la géométrie du corpus, donc leur platitude est réelle et non un artefact de fenêtre » est **fausse**. Les cinq piles rendues sont entièrement noires (maillage écrit au niveau 2, rendu contre le niveau 0), et l'instrument a compté « 49 fenêtres avec matière » sur des images noires parce que son seuil de matière était relatif au maximum de la pile.
  - Conséquence déclarée dans le même encadré : la coupure entre les deux familles de prédiction n'est plus établie, et cinq traces reviennent dans le jeu ; mesuré depuis, le morceau de `m7_c0` qui a de la matière donne 0,1589 — rang 1ᵉʳ sur 80, exactement où sont les `ps256` : la coupure est **réfutée**.
  - §6 : la formulation « nos traces ne montrent aucun relief » doit être qualifiée — à la géométrie du corpus publié, elles en montrent, tout en bas. Le contraste 0/75 contre 34/63 de `51` §6 reste valide, car interne à une seule géométrie.
  - §7 : le document n'établit pas que le relief mesure la qualité d'une surface, ni que cette distribution vaille pour une autre géométrie, ni que les deux signaux soient équivalents.
- **preuve de lecture intégrale** :
  - ligne 127 : « ### ⭐⭐ Les huit candidats, et la coupure est nette »
  - ligne 205 : « # les témoins, hors ligne »

---

### docs/53_le_temoin_positif_du_rendu.md
- **lignes** : 166
- **nature** : RESULTAT
- **résumé** : Le classement des candidats reposait sur une hypothèse sans contrôle : que notre chaîne de rendu produise des piles comparables à celles que la communauté publie. Le contrôle est direct parce que le format d'entrée est le même (`tifxyz`), et son critère de décision est écrit avant la mesure (le document est commité avec sa §3 vide). Un maillage publié découpé à la taille de nos candidats, rendu par notre chaîne et relu à 128 px × 109 couches, revient à 0,8726 — au-dessus de la médiane de son propre corpus. Le déficit de relief de nos traces est donc une propriété de nos traces, pas de notre instrument.
- **conclusions extractibles** :
  - Le maillage publié d'un segment est un `tifxyz` (`meta.json` + `x.tif`/`y.tif`/`z.tif`, `format: tifxyz`, `scale: 0.05`), exactement ce que notre aplatissement produit dans `plat/`.
  - Le segment publié `20230702185753` a une bbox [[14037, 11637, 29438], [21223, 24400, 73919]], scale 0,05 et une grille 2530 × 1820 ; le nôtre a une bbox [[9627, 9461, 38722], [11875, 11758, 39341]], scale 0,05 et une grille 120 × 119 — soit 320 fois l'aire.
  - Le maillage publié du segment `20230702185753`, découpé à la taille de nos candidats, rendu par notre chaîne et relu à 128 px × 109 couches, donne un relief de 0,8726, soit ×43,6 le plancher, rang 72ᵉ sur 80 ; le segment d'origine tel que publié lit 0,7912 (×39,6) ; la médiane du corpus est 0,7441 (×37,2) ; nos `ps256` sont à 0,164 – 0,198 (×8,2 – ×9,9), rang 1ᵉʳ.
  - Le morceau publié revient au-dessus de la médiane de son propre corpus : pas d'effondrement, pas de facteur quatre — donc le déficit de relief de nos traces est une propriété de nos traces et non de notre instrument.
  - L'écart entre 0,8726 et 0,7912 n'est pas une amélioration : ce sont deux aires d'échantillonnage différentes du même segment.
  - Coût mesuré : 80 minutes de rendu pour un morceau de 2380 × 2400 px sur 161 couches, soit 399 Mo, à 81 Kio/s de débit soutenu.
  - Le garde de taille de `profiler_une_surface.sh` cherchait un rendu de référence avec `find -path "*rendu*"` (une sous-chaîne) : il a trouvé le `x.tif` du maillage (119 × 120 points de grille) et refusé quatre surfaces parfaitement rendables en annonçant « ~119 px de côté » pour des surfaces qui en font 2400.
  - `profiler_une_surface.sh` jetait systématiquement la pile rendue ; `GARDER_RENDU=1` la conserve ; une pile pèse 562 Mo et sa reconstruction coûte dix-sept minutes de rendu par morceau.
- **rétractations / corrections internes** :
  - En-tête du tableau §1 : la ligne « nos `m7` : 0,0000 » est barrée et retirée — cinq rendus vides, renvoi vers `54`.
  - §3 : le document déclare d'avance ce que le témoin ne tranchera pas — le morceau publié couvre une fraction du segment quand la valeur publiée (0,7912) est lue sur ses 96 fenêtres ; un écart de quelques dixièmes ne se lira pas comme une panne, un effondrement d'un facteur quatre si.
  - §3 bis : le classement de `52` tient « pour la partie `ps256`, qui est celle qui reste après `54` ».
  - §4 : correction d'un défaut d'outil (motif `find` devenu un composant de chemin `*/rendu/*` ou `*/rendu_*/*`) et d'un défaut de conception (la pile jetée).
- **preuve de lecture intégrale** :
  - ligne 101 : « **Donc le déficit de relief de nos traces est une propriété de NOS TRACES, et non de notre »
  - ligne 165 : « src/outils/profiler_une_surface.sh --verifier »

---

### docs/54_cinq_rendus_vides.md
- **lignes** : 554
- **nature** : RESULTAT
- **résumé** : Cinq piles `m7` déclarées « plates » étaient en réalité entièrement noires, et un défaut d'instrument (`alive = peak_value >= floor * peak_value.max()`, vrai partout sur un tableau de zéros) les avait comptées comme « 49 fenêtres avec matière ». Le document remonte trois fois la chaîne causale : d'abord un maillage au niveau 2 rendu contre le niveau 0, puis — en se corrigeant lui-même — la **graine** et non le maillage, et enfin le fait que la graine `m7` ne désigne aucune matière dans aucun repère (≤ 7,1 spires de la feuille la plus proche). Relue correctement, la famille `m7` se situe exactement où sont les `ps256`, ce qui réfute la coupure entre familles de prédiction ; et une comparaison d'images montre que nos traces sont des spires coupées en travers, non des feuilles vues de face. Un audit des 322 piles du dépôt trouve 31 piles vides et trois causes distinctes.
- **relecture datée en tête** : le document porte une relecture du **2026-08-28** qui **CONFIRME** sa conclusion (« ⭐ RELU LE 2026-08-28, ET IL TIENT »). La question posée était de savoir si « vide » voulait dire « le rendu n'a rien produit » ou « on l'a montré au modèle 257 fois trop sombre » ; la mesure ne passe pas par le modèle du tout, `vide` étant défini comme `pic == 0`, maximum de pixel lu directement dans les TIFF. Réserve maintenue : le document ne dit rien de ce que le modèle aurait rendu sur une pile non vide mal mise à l'échelle.
- **conclusions extractibles** :
  - Tailles de fichiers : `ps256_c0` 562 Mo pour 161 couches (3,7 Mo par couche) ; `m7_c0` 7,6 Mo (47 Ko par couche) — un facteur 80 sur des images de mêmes dimensions (2361 × 2341 contre 2341 × 2361).
  - Lecture directe des pixels, une couche sur vingt, sur les huit candidats : `m7_c0` … `m7_c4` (5 piles, 161 couches) → max 0, 0,0 % de pixels allumés ; `ps256_c0` … `c2` (3 piles) → max 255, 95,8 – 96,3 %.
  - Le test de matière `alive = peak_value >= floor * peak_value.max()` est vrai partout sur une pile entièrement noire, puisque `peak_value.max()` vaut 0 : un tableau de zéros satisfait le test de matière à 100 %.
  - Le correctif `alive = (peak_value >= floor * pic_global) & (peak_value > 0.0)` ne déplace aucun chiffre réel : `ps256_c0` relu à la géométrie du corpus rend `amplitude_mediane = 0,19779944`, exactement la valeur publiée (0,1978).
  - `depth_profile.py`, l'instrument dont sort chaque relief du projet, n'avait aucune batterie ; il en a une de 14 contrôles, avec trois piles de contrôle (noire → refusée, uniforme éclairée → acceptée et lue plate, avec bosse → relief et pic sur la bosse).
  - Le traceur `m7` ouvre un zarr de [18946, 8174, 8174] quand le rendu ouvre [75784, 32693, 32693] — rapport 4,0000 / 3,9996 / 3,9996, donc niveau 2.
  - Boîtes englobantes : `m7_c0` tel quel z 7 822 – 9 500, ×4 z 31 286 – 38 001 ; `ps256_c0` (niveau 0) z 38 723 – 39 342 ; segment publié `20230702185753` z 29 438 – 73 920.
  - Les cinq `m7` sont au niveau 2, les trois `ps256` au niveau 0.
  - `m7_c0` remis à l'échelle ×4 puis rendu au niveau 2 (21 couches, 591 × 586 px) : max 255, 24,4 % des pixels allumés sur toutes les couches, contre 0 et 0,0 % pour le même maillage rendu tel quel.
  - Sur les seize piles du 2×2 croisé : prédiction `ps256` → graine `ps256` max 255 et 94,2 – 95,9 % allumé, graine `m7` max 0 et 0,0 % ; prédiction `m7` → graine `ps256` max 255 et jusqu'à 96,4 % allumé, graine `m7` max 0 et 0,0 %. Le vide suit la graine, pas la prédiction.
  - Bilan : 13 piles entièrement noires — les 5 candidats plus les 8 cellules « graine `m7` » du 2×2.
  - Sondage de matière (un bloc zarr par point, sur la surface) : `ps256_c0` niveau 0 → 13 / 13 points dans la matière, 0 bloc absent ; `m7_c0` niveau 2 → 3 / 11, avec 8 / 11 blocs absents du dépôt. Les deux méthodes s'accordent : 24,4 % de pixels allumés au rendu contre 27 % de points dans la matière au sondage.
  - Les trois quarts du maillage `m7` tombent là où il n'y a pas de données (hors du masque du scan), pas là où le papyrus est plat.
  - Première vraie lecture d'une trace `m7` (morceau de 30 × 30 points de grille, sans trou, 9 sondages sur 9 dans la matière, rendu 2400 × 2400 px sur 161 couches, 600 Mo, 87,1 % de pixels allumés) : relief 0,1589, ×7,9 le plancher, rang 1ᵉʳ sur 80 — contre 0,164 – 0,198 (×8,2 – ×9,9, rang 1ᵉʳ) pour les `ps256`, 0,7441 (×37,2) pour la médiane du corpus et 0,8726 (×43,6, rang 72ᵉ) pour un maillage publié passé par notre chaîne.
  - Comparaison d'images à étendue égale (512 voxels de côté, soit 1,2 mm) : référence publiée relief 0,791 (une feuille de face) ; maillage publié passé par notre chaîne 0,873 (une feuille aussi) ; `ps256_c0` 0,198 (des rubans clairs séparés de vide) ; `m7_c0` 0,159 (la même chose, plus serrée). Nos traces ressemblent à des spires coupées en travers.
  - Les vignettes 2, 3 et 4 sortent du même moteur avec les mêmes réglages : seule l'entrée change, et la catégorie du résultat change avec elle.
  - Tableau des quatre cellules du 2×2 : `m7_sur_graine_m7` (volume 18 946³, graine [2924, 5324, 9260], z 8 675 – 10 238) vide ; `ps256_sur_graine_m7` (volume 75 784³, même graine, z 8 298 – 10 130) vide ; `m7_sur_graine_ps256` (volume 18 946³, graine [10752, 10616, 38740] hors de ses bornes, z 38 528 – 39 083) matière ; `ps256_sur_graine_ps256` (75 784³, z 38 513 – 39 706) matière. Le maillage suit le repère de la graine, pas celui du volume ouvert.
  - Sondage des deux graines à pleine résolution : `ps256` [10752, 10616, 38740] → valeur 34, bloc allumé à 100 %, 8 traces avec matière ; `m7` [2924, 5324, 9260] → bloc absent du dépôt, 13 rendus entièrement noirs.
  - Le traceur ne refuse rien : il imprime `seed location [2924, 5324, 9260] value is 0` puis `empty space tracing` puis il pousse — et il annonce `value is 0` sur les quatre cellules, y compris celles qui marchent, donc cette ligne ne discrimine pas.
  - Distances à la matière : `ps256` dans son repère (niveau 0) valeur 34, bloc 100 %, 0 µm ; `ps256` converti en niveau 2 valeur 35, bloc 100 %, 0 µm ; `ps256` lu en niveau 2 sans conversion → rien dans 8 blocs, 4 913 requêtes ; `m7` dans son propre repère (niveau 2) → rien, ≤ 1 229 µm ≈ 7,1 spires ; `m7` converti en niveau 0 → rien, ≤ 1 536 µm ≈ 8,9 spires ; `m7` lu en niveau 0 sans conversion → rien dans 8 blocs, 4 913 requêtes.
  - La graine `ps256` désigne de la matière dans les deux repères, la graine `m7` dans aucun : ce n'est pas un défaut de conversion, l'endroit est vide. À 173 µm d'espacement inter-spires, la graine `m7` rate la feuille de sept épaisseurs de papyrus. Les distances sont des majorants (la recherche s'arrête au premier bloc publié, un bloc fait 128 voxels de côté).
  - Le traceur écrivait `voxelsize: 2,4 µm` quelle que soit la prédiction, alors qu'un voxel `m7` fait 9,6 µm : chaque longueur est sous-estimée d'un facteur 4 et chaque aire d'un facteur seize.
  - Sur deux maillages de même grille (120 × 119, ~13 777 points valides) : `ps256` (L0) pas de grille 48 µm, aire annoncée et réelle 0,317 cm² ; `m7` (L2) pas de grille 192 µm, aire annoncée 0,317 cm², **aire réelle 5,079 cm²**. Les deux se sont arrêtées au même nombre de points parce que `min_area_cm: 0.3` était évalué dans deux unités différentes.
  - Audit des 322 piles rendues de l'arbre (175 Go), une couche sur quarante : 291 avec de la matière, 31 entièrement noires, 9 illisibles (rendu en cours au moment de l'audit).
  - Des 31 piles vides, 29 viennent d'une graine `m7` et 2 sont `boucle/corrige_nappe_gen1_poids100`, dont le `plat` est une grille de 364 × 14 points dont le plan `x` est entièrement négatif (minimum −1239, maximum −1, zéro point positif sur 5096, quand `y` et `z` en ont 2370) — un aplatissement dégénéré, ni un problème de niveau ni un problème de masque.
  - Aucun document ne cite la pile `corrige_nappe_gen1_poids100` (vérifié par recherche sur tout `docs/`, `analysis/src/` et `tools/`).
- **rétractations / corrections internes** :
  - En-tête : correction d'un résultat publié — `52` §6 affirmait que « les cinq `m7` lisent zéro à toutes les géométries essayées : leur platitude est réelle, pas un artefact de fenêtre ». C'est faux.
  - §3 sexies : « ⚠⚠ CORRECTION de ma propre §3 : c'est la GRAINE, pas le maillage ». Le rapport de formes valait bien 4, mais ce n'était pas le mécanisme — c'était un corrélat ; le mécanisme est un cran en amont, prouvé par deux cellules du 2×2.
  - §3 sexies : le 2×2 croisé n'était pas en position de conclure — sa colonne « graine `m7` » tenait un *nombre* constant et non un *endroit*, et l'endroit n'a jamais été tenu constant.
  - §3 quater / §4 : la « coupure nette entre les deux familles de prédiction » annoncée par `52` §6 était entièrement un artefact des rendus vides ; mesurées correctement les deux familles sont indiscernables (0,159 contre 0,164 – 0,198, toutes au rang 1 sur 80).
  - §4 : « Cet endroit n'a pas de feuille » n'est plus établi, alors que c'était la conclusion la plus robuste du 2×2 (8 répétitions sur 8) ; ce qui reste établi est que le vide suit la graine, pour une raison de repère.
  - §3 octies : ce qui est fermé est la cause pour la famille `m7` (l'endroit est vide) ; ce qui ne l'est pas est le mur — la famille `ps256` part d'un point sur de la matière et porte quand même quatre à cinq fois moins de structure que le segment publié.
  - §3 septies : toute comparaison d'aire entre les deux familles est fausse d'un facteur 16, y compris le tableau de `48` §4 qui annonce « 0,317 cm² » des deux côtés ; la comparaison « prédiction contre prédiction, au même endroit » reste à faire.
  - §3 quinquies : la réponse à « aura-t-on un jour une vue des vraies feuilles aplaties ? » est non — ce dépôt n'a jamais produit une vue de vraie feuille aplatie ; il en a mesuré l'absence de plusieurs façons sans jamais la regarder.
  - §5 bis : un troisième état est nommé — « il n'y a rien dedans » et « il n'y a rien encore » ne veulent pas dire la même chose ; les piles illisibles sont comptées et rapportées à part.
  - §1 : défaut d'environnement — le projet racine n'avait pas `imagecodecs`, donc `tifffile` refusait de décoder les piles réelles (LZW) pendant que la batterie passait au vert sur des fixtures non compressées.
- **preuve de lecture intégrale** :
  - ligne 332 : « ⚠⚠ **Et le traceur ne refuse rien.** Il imprime `seed location [2924, 5324, 9260] value is 0`, »
  - ligne 550 : « uv run --project . python src/volume/depth_profile.py --verifier »

---

### docs/55_les_murs_et_leurs_causes.md
- **lignes** : 131
- **nature** : PROCEDE
- **résumé** : Document **rendu** depuis `docs/registres/murs_et_causes.tsv` par `uv run python src/depot/murs_et_causes.py --rendre`, et non écrit à la main ; sa batterie vérifie que chaque ligne pointe vers un document contenant encore son ancre. Il recense **30 causes candidates sur 4 murs** : 19 éliminées, 10 confirmées, 1 bloquée, chacune avec la mesure qui l'a tranchée et le document d'origine. Sa thèse de forme est qu'un mur est un espace de causes dont on retire une entrée à la fois, et que la liste des causes éliminées — non celle des tâches — est le seul progrès mesurable. Une seule cause reste non tranchée, et elle est bloquée. (⚠ Note de lecture : l'en-tête compte 19 éliminations quand le §final écrit « les treize éliminations de ce document » ; le document ne signale pas l'écart. De même, il ne contient aucune cause ⏳ *ouverte* alors que son propre tableau de symboles définit ce statut.)
- **conclusions extractibles** : *(les murs recensés, avec pour chacun les causes éliminées et celles qui restent ouvertes)*

  **Mur 1 — « Le tracé ne suit pas de feuille »** (❌ 6 éliminées · ✅ 5 confirmées · 🔒 1 bloquée)
  - ❌ **éliminée — la fenêtre de lecture** : relu à 128 px × 109 couches, la géométrie du corpus, le classement ne bouge pas (`52`).
  - ❌ **éliminée — la chaîne de rendu** : un maillage PUBLIÉ passé par notre chaîne revient à 0,873, au-dessus de la médiane du corpus (`53`).
  - ❌ **éliminée — le champ de normales (NORMAL pèse 10)** : chargé pour de vrai, coût par génération ×29, trajectoire INCHANGÉE sur 118 générations (`26`).
  - ❌ **éliminée — le plafond de générations** : budget ×3,3, aire ×11,5, α +0,89 → +0,95, sous le bruit du tireur (0,16) (`50`).
  - ❌ **éliminée — le niveau de pyramide** : 0,02 d'écart entre niveaux 0 et 1 pour une résolution de 0,20 (`50`).
  - ❌ **éliminée — la prédiction de surface (ps256 contre m7)** : lues correctement, les deux familles sont indiscernables, 0,159 contre 0,164 – 0,198 (`54`).
  - ✅ confirmée — la graine, c'est-à-dire l'endroit : la graine m7 n'a AUCUNE matière à ≈ 7,1 spires dans son repère ni à ≈ 8,9 converties, quand la graine ps256 est SUR de la matière dans les deux repères (0 µm) — l'endroit explique la famille m7, **pas le mur** (`54`).
  - ✅ confirmée — le traceur accepte une graine qui ne désigne rien : bloc absent du dépôt, et il trace quand même, 13 rendus noirs (`54`).
  - ✅ confirmée — le traceur est un tirage, pas une fonction : 13 traces propres sur 14 à paramètres identiques (`30`).
  - ✅ confirmée — la surface est EN TRAVERS de l'empilement : des spires coupées en travers, vues à l'image à étendue égale contre une feuille publiée (`25`).
  - ✅ confirmée — le niveau de la prédiction n'était propagé nulle part : trois conséquences, dont des aires m7 fausses d'un facteur 16 (`54`).
  - 🔒 **RESTE OUVERTE (bloquée) — comparer le relief d'une trace L2 à une trace L0** : à aire égale un maillage L2 rend quatre fois moins de pixels de côté, donc les deux ne tiennent jamais dans la même fenêtre d'analyse — le relief ne peut pas les départager (`54`).

  **Mur 2 — « Les patchs publiés ne se recollent pas »** (❌ 1 éliminée · ✅ 1 confirmée)
  - ❌ **éliminée — raccorder deux segments officiels** : l'outil exige des surfaces qui se recouvrent, et il n'existe AUCUN candidat — mesuré sur 4,5 Mo de catalogue (`44`).
  - ✅ confirmée — un patch par feuille, pas par région : la paire la plus proche est à 79 µm, soit environ deux fois le seuil de séparation (`44`).
  - **aucune cause ouverte sur ce mur.**

  **Mur 3 — « L'extension tangentielle est un point fixe »** (❌ 8 éliminées · ✅ 3 confirmées)
  - ❌ **éliminée — augmenter le budget d'un seul coup** : budget 200 → 28,6 cm² mais 25 036 auto-intersections et α = +1,313, la surface se replie sur elle-même (`44`).
  - ❌ **éliminée — enchaîner rogner puis étendre** : le cycle converge vers un point fixe autour de 6 cm² (`44`).
  - ❌ **éliminée — juger une courbe sur trois points** : trois points donnaient « pente monotone », six « plateau puis falaise », neuf « maximum puis descente douce » (`44`).
  - ❌ **éliminée — juger la projection par un sondage de points** : bloc avec matière et valeur au point rendent le MÊME chiffre de 0 µm à 2,4 mm ; un bloc fait 307 µm quand les feuilles sont à 10-20 µm (`44`).
  - ❌ **éliminée — enchaîner la projection à GRAND pas (238 µm/maillon)** : cinq maillons étalent la boîte ×2,38 à nombre de points constant contre ×1,10 pour le bond direct, et finissent 5,33 SPIRES à côté ; le pas réel dérive de 238 à 963 µm par maillon (`44`).
  - ❌ **éliminée — l'emballement du pas d'une chaîne** : ce n'était pas l'enchaînement mais l'UNITÉ ; à pas FIXE en voxels, vingt maillons tiennent 96,0 µm (×1,00), boîte ×1,55, 14 280 points sur 14 280 — contre ×2 692, ×4 976 545 et 615 points au pas de grille (`44`).
  - ❌ **éliminée — un pas contrôlé suffit-il à rester sur la feuille ?** : non, et les deux pannes sont distinctes ; à pas fixe la géométrie est saine sur 20 maillons et le contact matière tombe à 39,7 % dès 768 µm puis plafonne vers 35 % (`44`).
  - ❌ **éliminée — le recalage mesure-t-il sa propre sortie ? (circularité)** : +19,1 contre +19,0 à 768 µm et +15,3 contre +15,1 à 1 920, identiques à la première décimale, alors que la demande de déplacement passe de 1,6 et 3,4 voxels à 0,06 (`44`).
  - ✅ confirmée — une extension UNIQUE puis rognage : 4,28 → 12,97 cm² à α = +0,000, ramenée à 6,02 cm² propres, soit +41 % de matière validée (`44`).
  - ✅ confirmée — la chaîne TANGENTIELLE : elle marche à DEUX conditions qui se composent (pas FIXE en voxels et RECALAGE sur la matière à chaque maillon) ; 60 maillons de 96 µm, pas tenu à 96,0 exactement, +6,9 points au-dessus du plancher du hasard à 5 760 µm, là où la chaîne sans recalage est morte dès 768 (+1,5) (`44`).
  - ✅ confirmée — enchaîner la projection à PETIT pas (95 µm/maillon) : un LEVIER qui marche À COURTE DISTANCE ; à 478 µm la chaîne est encore sur sa feuille (2,0 % de pic au bord contre 18,4 % pour un seul bond) avec +31 % d'amplitude ; contre le plancher du hasard, +30,5 points à 288 µm, +24,1 à 480, puis +1,5 à 768 (`44`).
  - **aucune cause ouverte sur ce mur.**

  **Mur 4 — « La chaîne casse au sixième tour »** (❌ 4 éliminées · ✅ 1 confirmée)
  - ❌ **éliminée — halver le pas indéfiniment** : il y a un OPTIMUM à 0,25 ; à 0,125 l'α moyen remonte de +0,102 à +0,327 (`43`).
  - ❌ **éliminée — le sens de croissance (in contre out)** : ni meilleur, ni pire (`43`).
  - ❌ **éliminée — juger par le compte d'auto-intersections** : c'est une propriété de l'échantillonnage autant que de la surface, le même maillage décimé passe de 240 à 49 (`43`).
  - ❌ **éliminée — juger sur un seul rendu** : mesuré AVANT de s'en servir, et il ne marche pas (`43`).
  - ✅ confirmée — le pas du rayon : halvé de 1,0 à 0,5, 4 spires convergentes sur 7 deviennent 6 sur 7 et la rupture disparaît, gratuitement (`43`).
  - **aucune cause ouverte sur ce mur.**

  **Autres énoncés du document :**
  - 30 causes candidates sur 4 murs : 19 éliminées, 10 confirmées, 1 bloquée.
  - La seule entrée de la section « Ce qui reste ouvert, tous murs confondus » est la cause bloquée du mur 1 (comparer le relief d'une trace L2 à une trace L0).
  - Une cause éliminée ne se rouvre pas sans une mesure neuve ; une cause absente du document n'est pas une cause éliminée, c'est une cause à laquelle personne n'a pensé.
  - La figure `55_espace_de_causes.png` n'est pas une jauge de progression : rien ne dit que l'espace est borné.
- **rétractations / corrections internes** : aucune rétractation déclarée. Le document précise en revanche deux bornes de portée sur des causes confirmées : « la graine, c'est-à-dire l'endroit » explique la famille m7 **et pas le mur**, et la chaîne tangentielle « ne dit pas que c'est la BONNE feuille (il faut de l'encre), et part d'un segment PUBLIÉ et non d'une de nos traces ». Il retire aussi explicitement une affirmation antérieure : « ⚠⚠ Le “croisement” que j'avais publié à 1 920 µm n'existe pas : chaîne ET bond y sont au niveau du hasard (−1,7 et +1,6) ».
- **preuve de lecture intégrale** :
  - ligne 97 : « | enchaîner la projection à GRAND pas (238 µm/maillon) | ❌ | cinq maillons de 238 µm étalent la boîte ×2,38 à nombre de points constant, contre ×1,10 pour le bond direct — et finissent 5,33 SPIRES à côté de lui. ⚠ Le pas réel dérive avant la boîte : 238 → 963 µm par maillon | [`44`](44_ou_la_chaine_se_trouve.md) | »
  - ligne 127 : « cause à laquelle personne n'a pensé. Le tableau borne ce qu'on a testé, jamais ce qui »

---

### docs/56_le_grand_menage.md
- **lignes** : 949
- **nature** : MIXTE
- **résumé** : Document qui se déclare lui-même « un PLAN, pas un résultat », écrit pour être repris par une session neuve, mais dont chaque chiffre est mesuré et dont les quatre chantiers sont ensuite marqués comme clos au fil du texte. Il commence par corriger l'impression de départ (« sept dossiers blindés de scripts, une montagne de doublons ») : trois points sur quatre sont vrais, la vraie montagne est `data/` (177 Gio sur 203) et non les venvs (4,24 Gio récupérables, pas 16,6). Les quatre chantiers sont A (cache de rendu par contenu, livré, avec la découverte que 58,6 % du contenu dupliqué est constitué de fenêtres imbriquées), B (réorganisation de `data/`, **clos par la mesure qui contredit son propre plan**), C (`lplv`, livré) et D (dessin unifié et `docs/` rangé par nature, livré). Une section entière énumère ce qu'on décide de **ne pas** faire, avec sa raison mesurée.
- **conclusions extractibles** :
  - Fichiers source, lignes et poids : `analysis/` 123 fichiers / 35 561 lignes / 3,2 M ; `tools/` 73 / 8 359 / 624 K ; `src/excision/` 16 / 3 464 / 624 K de poids réel pour 351 M total ; `src/tracecheck/` 4 / 1 310 / 144 K ; `htr/` 1 / 185 / 264 K ; `src/xpu/` 1 / 169 / 128 K pour 6,3 G ; `inference/` 0 / 0 / 256 K.
  - Les « 16,6 Go » de venvs n'existent pas : `uv` installe ses paquets en liens durs. Pour `htr/` + `inference/.venv` : nlink 1 → 8 228 fichiers, 0,15 Gio (libéré tout de suite) ; nlink 2 → 42 994 fichiers, 4,09 Gio (libéré après `uv cache prune`) ; nlink ≥ 3 → 9 516 fichiers, 3,06 Gio (jamais libéré). Soit 4,24 Gio de récupérable réel, un facteur quatre d'écart.
  - Les « 25 sites d'appel » à `inference/` n'étaient pas des besoins mais des emprunts : la racine déclare `pillow>=10.0`, et `inference/` n'a pas `numcodecs` — ce trou a fait rendre vides tous les chunks *blosc* d'une prédiction, donc conclure à tort qu'une graine n'était pas couverte par la prédiction publiée. Les 25 sites sont repointés sur la racine et les 11 batteries concernées passent depuis là.
  - Le dépôt pèse 203 Gio, dont 177 dans `data/` ; les 4,24 Gio de venvs sont 2 % du problème.
  - Duplication de code : 630 fonctions définies, 328 noms distincts, 40 noms répétés ; `main` ×122, `verifier`/`_verifier` ×75 ; `_police` 15 copies pour 4 variantes distinctes, `_pixels` 14 copies pour 3 variantes, palette 14. Soit ~300 lignes sur 35 561, 0,8 %.
  - `data/` : 177 Go, 80 dossiers de premier niveau, 68 540 fichiers ; 324 dossiers `rendu*` pour 97 Go (55 %), `data/layers/` 51 Go (29 %), `data/traces/` 17 Go (10 %).
  - Recalcul mesuré le 2026-08-25 : la même surface (`morceau_00`) rendue et profilée deux fois dans deux campagnes donne un résultat bit-pour-bit identique (`c1ff66d445eea26dadfa5f4d0b1e6173`), soit ~15 minutes de rendu payées deux fois, parce que le cache est par répertoire de destination et non par contenu.
  - L'hypothèse « téléchargé en double » ne tient pas dans `layers/` et `traces/` : le proxy « même nom + même taille » n'y trouve que 1,0 Go, presque uniquement des `meta.json`. Sur tout `data/` le même proxy annonce 17,4 Go mais surcompte.
  - `docs/` : 528 entrées — 57 markdown, 341 JSON, 73 images, ~57 `.log`/`.csv`/`.jsonl`. `.lances/` : 196 fichiers, ~65 lancements.
  - Chantier A, doublonnage mesuré par hachage sur 68 540 fichiers : **35,58 Gio de contenu identique**, avec trois étages (taille, hachage partiel de 64 Kio, hachage complet sur 15 473 fichiers seulement).
  - Répartition des doublons : fenêtres imbriquées 20,85 Gio (58,6 %), autre 10,51 Gio, même fenêtre dans deux campagnes 4,22 Gio.
  - La tranche `i` de n=31 EST la tranche `i+25` de n=81, au bit près ; les paires trouvées sont (31, 81) sur 2232 groupes et (41, 161) sur 861. Rendre n=161 produit déjà n=81, n=41 et n=31.
  - Un cache indexé sur (surface, niveau, N) ne peut pas voir les fenêtres imbriquées, puisque N diffère ; seul un cache par tranche le verrait.
  - Le raccourci de rendu est éprouvé par 8 mesures indépendantes et 5 tentatives de réfutation (13 agents, 2,95 M tokens) : 6 sites confirment, chacun avec toutes ses tranches identiques octet pour octet et 23 mesures de profil identiques sur 23, zéro différence ; les 2 restants sont IMPOSSIBLE pour des raisons de données ; aucun site ne réfute.
  - Le décalage entre fenêtres est `N_large // 2 − N_étroite // 2` et non `(N_large − N_étroite) / 2` — les deux coïncident sur toute la série impaire du dépôt.
  - Piège d'instrument : la console réimprime les indices de pic en absolu, le JSON les stocke relatifs à la fenêtre ; sur la même mesure la console dit « couche 42 » d'un côté et « couche 17 » de l'autre, un écart de 25, alors que le JSON porte 17,0 des deux côtés.
  - Le témoin du fichier du raccourci est passé de 33 à 50 contrôles, et quatre des premiers étaient faux (comparaison de numéros de ligne, `$?` du harnais, grep du fichier qui se compte lui-même, motifs qui matchaient la prose).
  - Chantier B, quatre mesures contre le déplacement : `data/` est entièrement gitignoré (0 fichier suivi) ; 11 des 81 dossiers seulement nomment un rouleau, 86 % sont des expériences ; `data/trace/` groupe déjà par rouleau à l'intérieur ; le coût est de 296 citations sur 64 chemins distincts plus 177 Gio à déplacer.
  - `donnees_sans_appelant.py` : 25 dossiers orphelins pour 44,3 Gio, 3 dossiers nommés en journal seulement pour 6,3 Gio, 52 dossiers vivants. Les plus lourds sont les campagnes d'extension tangentielle (`ext_*`, huit dossiers, ~24 Gio) et les balayages de convergence.
  - Chantier C : sur 123 modules de `analysis/src/`, 122 ont un `main()`, 75 exposent `--verifier`, 63 exposent `--json`.
  - `lplv` : 218 verbes découverts, zéro nom ambigu, 98 qui s'auto-testent, 72 qui rendent du JSON. (⚠ Note de lecture : le tableau d'en-tête du document annonce « 233 verbes découverts » pour le même chantier ; l'écart avec les 218 du §C et de la légende de figure n'est pas signalé.)
  - L'arbre allégé de la release, construit à partir de la seule liste `GARDES`, rend 204 verbes au lieu de 218, sans erreur et sans configuration : c'est la définition d'un palier additif.
  - Rangement `src/` : `analysis/src` (126 fichiers à plat) et `tools/` (73) deviennent `src/` en dix familles, dont trois issues des préfixes réels (`figure_*` 37, `table_*` 10, `campagne_*` 12).
  - Coût du déplacement : 1011 citations de chemin réécrites dans 182 fichiers, 62 scripts shell remontant d'un cran, 50 modules dont le `sys.path` supposait un dossier plat, 12 chemins assemblés que nulle réécriture ne peut voir. L'estimation de départ disait ~490 citations : deux fois moins que la mesure.
  - Descente des échecs du rangement : 37 → 35 → 12 → 3 → 1 → 0.
  - Trois orphelins révélés qui l'étaient déjà : `fetch_normal_grids.py`, `telecharger.py`, `valider_blocs.py`.
  - Chantier D : le garde-fou lent passe de 160 s à 2,9 s (il lançait un `grep -r` sur tout le dépôt par fichier, 0,80 s × ~200), après un palier intermédiaire à 38 s.
  - Le garde-fou révèle 27 scripts que rien n'exécute — de la dette de documentation, signalée et jamais en échec.
  - `figure_commune.py` : quinze copies, quatre variantes, zéro image déplacée — elles ne diffèrent que par les tailles demandées.
  - Six images de `docs/` ne correspondaient plus à leurs données ; `fraicheur_des_figures.py` régénère et compare les octets en 4,9 s pour les 36 figures. Sa première version ne reconnaissait qu'une forme de déclaration sur trois et jugeait 11 figures sur 36 tout en annonçant « chacune ».
  - `docs/` à la racine passe de 522 fichiers à 58 : 58 documents, `docs/mesures/` 384, `docs/journaux/` 79, `docs/registres/` 1. Le partage vient d'une mesure : les `.json` sont cités 77 fois par les documents, les `.log` jamais ; second signal concordant, les `.log` sont gitignorés.
  - `verifier_chiffres.py` lisait ses 50 mesures en `racine / "docs" / "x.json"`, écrit quarante-quatre fois, chaque lecture gardée par `if p.exists():` — un `docs/` rangé aurait fait sauter jusqu'à cinquante sources en restant vert. Après remède : 50 sources, 0 manquante, avant comme après.
  - 81 fichiers seraient entrés dans le dépôt sans un mot, parce que `.gitignore` dit `/docs/*.log`, une règle ancrée à la racine de `docs/`.
  - `git mv` a déplacé 14 fichiers puis s'est arrêté sur le premier `.log` qu'il ne suivait pas.
  - 19 endroits réparés à la main, dont sept `--docs` dont le défaut désignait `docs/` et treize blocs de reproduction qui passaient `--docs docs` ; cinq blocs « Reproduire » du document 44 écrivaient `$PWD/docs/chaine_*.json`.
  - 125 chemins appartiennent à la classe « écrit dans un résultat publié », dont un recensement qui en cite 51 à lui seul.
  - `deplacer.py` recompilait 464 motifs pour chacun des 355 textes du dépôt, soit 165 000 compilations : deux minutes sans réponse → 21 secondes.
  - `.lances/` : purge par script (les 5 plus récents), 197 → 63 fichiers ; le premier passage a ramené `.lances/` de 197 fichiers à 4, et `.lances/` est gitignoré donc c'est perdu. `PART_MAX_PURGEE` vaut 50 % par défaut.
  - `permalien.py` : `HEAD` était 43 commits en avance sur `origin/main` — un lien vers `HEAD` aurait rendu 404 pour tout le monde sauf cette machine. 34 contrôles, deux sondes.
  - Le dépôt est **privé** : sa racine GitHub rend 404 sans session quand la même URL sur un dépôt public du même compte rend 200 ; un permalien vaut donc pour l'auteur, pas pour un lecteur extérieur, mais `git show <commit>:<chemin>` marche depuis n'importe quel clone.
  - Après le repli final du 2026-08-26, la racine ne porte plus que trois dossiers.
  - ⚠⚠ `valider_blocs.py` (2026-09-05) : ce n'est pas un appelant qui lui manque, c'est sa
    RÉFÉRENCE. Il tourne — 63 blocs, 19 976 cellules, `below_030` **0,00025** en 9 min hors
    ligne — mais la valeur de l'arbre global sur ce maillage n'existe nulle part et ne peut
    pas exister : 45 M de cellules, celui-là même dont `proximity_vs_ink` écrit qu'un cKDTree
    global « a fait tomber la machine trois fois ». Sans elle, la comparaison et sa tolérance
    de 10 % sont inatteignables. Le lot qui le rend utile est de lui trouver un maillage assez
    petit pour que les DEUX passent, ce que son propre en-tête réclame.
  - ⚠⚠⚠ **Un des trois « orphelins » n'en était pas un** (corrigé le 2026-09-05) :
    `telecharger.py`, le pool de connexions HTTPS, est **importé par trois modules**.
    Le garde comptait `source x.sh` comme une exécution — *« sourcer une bibliothèque
    shell, c'est l'exécuter »* — et **l'équivalent Python manquait**, donc tout module
    écrit pour être importé était déclaré mort. ⭐ Le remède n'est pas de compter un
    import comme un appel (ce serait mentir sur le verbe) mais d'ouvrir une **catégorie
    à part**, rendue avec QUI l'importe ; un orphelin devient « rien ne l'exécute ni ne
    l'importe ». ⚠ Faux positif possible : un module du dépôt masquant un nom standard —
    mesuré **0 sur 263**, et le contrôle le réasserte.
- **rétractations / corrections internes** :
  - En-tête, note du 2026-08-26 : le §1.1 comptait « sept dossiers de scripts » et concluait qu'ils étaient « DEUX dossiers et cinq environnements » — juste comme diagnostic, faux comme conclusion, car un environnement n'a pas besoin d'être à la racine, il a besoin d'être avec son code.
  - §1.1, « ⚠⚠ Deux affirmations de ce paragraphe étaient FAUSSES — corrigées le 2026-08-25 » : (1) les « 16,6 Go » n'existent pas (liens durs `uv`, 4,24 Gio réels) ; (2) les « 25 sites d'appel » étaient des emprunts à un environnement strictement plus pauvre que la racine.
  - §1.1 : « ⚠⚠ `inference/` est parti aussi, et c'est une correction de MA conclusion » — l'auteur a objecté que le témoin devait être un mode et non un dossier ; la mesure va plus loin que son argument, les deux dossiers portaient deux constructions de torch différentes, donc la comparaison mélangeait l'appareil ET la build.
  - §1.3 / §4 : le proxy « même nom + même taille » (17,4 Go) surcompte sur les chunks zarr homonymes — et la mesure par hachage montre qu'il se trompait dans les deux sens (35,58 Gio réels, dont tout ce qui ne porte pas le même nom).
  - §B, « ⚠⚠ 2026-08-26 — la mesure CONTREDIT ce plan, et c'est le plan qui cède » : quatre mesures contre le déplacement ; le plan d'origine est gardé « pour ce qu'il vaut », et le manifeste n'a aucun consommateur donc l'écrire serait un orphelin.
  - §A : « ⚠⚠ Non exercé sur un vrai rendu » — ce qui est vérifié est la forme (compteurs imprimés, dépôt après le profil, clé venue de l'instrument), pas le gain ; la première campagne réelle sera la mesure.
  - §A, « ⚠ Ce qui n'est PAS fait (historique) » : la phrase « Le raccourci n'est pas encore câblé dans `profiler_une_surface.sh` » est barrée — il l'est désormais.
  - §A : « ⚠⚠ Quatre contrôles à moi qui ne pouvaient pas échouer » — quatre des 33 contrôles initiaux étaient faux et sont remplacés.
  - §D : « ⚠⚠ Une régression que J'AVAIS introduite » — six figures écrivaient dans `../docs/images/`, ce qui était juste quand elles tournaient depuis `inference/` ; rien ne l'a vu parce que leurs batteries n'écrivent pas d'image.
  - §D, encadré `.lances/` : « ⚠⚠⚠ Et elle a effacé trop, pour de vrai » — 197 fichiers ramenés à 4, mécanisme non reproduit ; la leçon n'est pas d'écrire un meilleur motif mais qu'une purge capable d'effacer la quasi-totalité d'un dossier doit refuser. Et le contrôle mesurait le plafond en croyant mesurer la rétention.
  - §D : deux contradictions internes des outils corrigées — `deplacer.py` refusait de laisser une citation qu'il avait décidé exprès de ne pas réparer (donc aucun plan touchant un fichier nommé dans un résultat ne pouvait aboutir), et la docstring de `REGISTRES` promettait une vérification qui n'existait pas (elle a corrigé sa propre liste : `verbes.json` est une sortie, pas un registre).
  - §4 : deux lignes du tableau « ce qu'on décide de ne pas faire » sont barrées comme faites — « Supprimer `inference/` » (FAIT le 2026-08-25) et « Toucher aux `.venv` » (partiellement fait).
- **preuve de lecture intégrale** :
  - ligne 552 : « **218 verbes découverts, zéro nom ambigu, 98 qui s'auto-testent, 72 qui rendent du JSON.** »
  - ligne 947 : « 4. **les points d'extension justifiés par un deuxième cas RÉEL** — le registre l'est par 123 ; »



Six fiches. Lot des **réfutations** : trois documents renversent tout ou partie de leur
propre thèse (59, 60, 62), un quatrième porte une réserve ajoutée après coup qui change le
statut de son raisonnement (58 et 60), et un cinquième (61) attaque l'instrument de
vérification du dépôt lui-même.

---

### docs/57_les_taches_laissees.md
- **lignes** : 214
- **nature** : MIXTE
- **résumé** : Instruction mécanique des tâches laissées ouvertes dans le dépôt (41 sabliers sur
  18 documents, 56 items numérotés dans trois documents de backlog), désormais dérivée par
  `src/depot/taches_ouvertes.py` et arbitrée par `docs/registres/taches.tsv` avec vérification
  dans les deux sens. La réponse courte est « rien n'a été sauté », mais plusieurs sabliers
  **mentaient** : trois questions sont fermées par la mesure et deux lectures publiées sont
  corrigées. Le document se termine sur une limite du garde-fou des chiffres et la moitié de
  cette limite qui EST mécanisable (`chiffres_sans_record.py`).
- **conclusions extractibles** :
  - Les deux artefacts de balayage sont sur la **même grille 7,91 µm** : `sweep_PHerc1667.jsonl`
    à rayon **80 vox = 632,8 µm**, `sweep_1667_pas.jsonl` à rayon **18 vox = 142,4 µm** — donc
    ni la branche « 43 µm » ni la branche « 142 µm » du dilemme initial n'était la bonne lecture.
  - La reconstruction avec ces paramètres rend les **18** et **16** enregistrements **identiques**
    (`cells` et `measured` au chiffre près), seul le champ `echelle` étant nouveau.
  - Sans `--variante`, le script prend la grille **alphabétiquement première** — 3,24 µm sur ce
    corpus, pas 7,91 — donc un run avec `--voxel-um 7.91` sans variante **déclarerait** 142 µm
    pour un rayon de 58.
  - « 36 contre 72 » n'est pas une contradiction : **36** est la valeur par défaut de `--windows`
    (budget nominal), **72** est un compte réalisé (`sondees`) ; le code sonde
    `steps × min(2·steps, grid_x)` avec `steps = int(sqrt(windows))`, soit environ le double.
    `docs/mesures/fibres_corpus.json` : 80 entrées, `sondees = 72` constant (9 amas → 18 ancres
    × 4 chunks).
  - Il existe un régime où la nappe gagne de l'aire en restant convergée, et il est borné :
    budget `generations = 100` → aire utile **12,968 cm²**, **0** auto-intersection, α **+0,000**
    (contre 4,28 cm² pour la source officielle) ; à 200 → 28,62 cm², 25 036 auto-intersections,
    α +1,313 ; à 400 → 78,30 cm², 168 104 auto-intersections, replié, non jugé.
  - Ce régime est une **propriété, pas un tirage** : deux exécutions identiques rendent le même
    maillage, écart **0 µm** mesuré par un second instrument.
  - Le passage α **+0,98 → +1,03** de `42` n'est **pas** une dégradation : les deux valeurs sont
    à **0,0375** et **0,0200** de l'α de plafond (+1,0135), donc sous la résolution **0,20** de
    l'instrument.
  - La vraie dégradation appariée, elle, est **0 → 11 753** auto-intersections à `step_size`
    identique.
  - Le rouleau mesuré dans M1ter n'est **pas** PHerc0172 mais **PHerc1447** ; PHerc0172 est un
    autre rouleau, à 7,91 µm, hors des treize du prix.
  - `16` (cartes de difficulté) est fait : les **14** artefacts de `docs/carte_difficulte/`
    portent tous `sondes: 108` ; `PHerc1447` médiane 155,52 → **156 µm**, p10 138,24 → 138,
    min 120,96 → 121, 0,3809 → **38 %**, 21 chunks → 21 fenêtres.
  - Le transport vers une région sans vérité est **impossible sur ce couple** : la face n'est
    périodique qu'à une taille de fenêtre où les enroulements ne rendent **aucune** fenêtre.
  - Témoin négatif refait le 2026-08-28 : ρ passe de **+0,9979 à −0,0100** et σ du positif de
    **2,4 % à 76,4 %** du modèle qui marche ; le détecteur répond **plus** sur la surface sans
    feuille (**0,711 contre 0,589**).
  - `verifier_chiffres.py` vérifie qu'un chiffre recalculé apparaît dans un document, et ne peut
    pas vérifier la réciproque : un nombre publié sans record lui est **invisible**.
  - Cadrage mesuré de `chiffres_sans_record.py` : **1154** écritures à ≥ 3 décimales dans les
    documents, dont **1060 déjà adossées** à un fichier de `docs/mesures/` ; résidu **51 chiffres
    dans 17 documents**, remesuré le soir même à **53 chiffres dans 19 documents**. La batterie
    asserte `< 200` plutôt qu'un compte figé.
  - L'effacement des spans et blocs de code avant recherche a retiré **cinq** faux positifs
    (56 → 51), dont `3686,1946` qui est la forme de tableau `[3686,1946,1946,]`.
  - `+0,9984` **échappe** à la garde : il coïncide avec `0.9984133775266987`, ratio médian de
    `proximity_scroll1.jsonl`, c'est-à-dire d'un autre rouleau — collision attendue à quatre
    décimales sur plusieurs centaines de milliers de nombres. Deux contrôles assertent la
    collision plutôt que de régler le seuil.
  - Cinq orphelins vérifiés (`19,834872`, `20,747079`, `1,5036`, `0,825755`, `22,431`) :
    **aucun fichier de l'arbre entier** ne les porte.
- **rétractations / corrections internes** :
  - §1.1 — l'auteur rétracte sa **propre première mesure** : le corpus avait été cherché dans
    `data/repos/windcheck/data/`, d'où « PHerc1667 n'y est pas » et une mesure faite sur
    `scroll1_tifxyz`, un autre corpus. `data/traces/PHerc1667/` existe (20 traces, quatre grilles).
  - §2.1 — corrige la lecture publiée de `42` : « la correction dégrade α » est faux, les deux
    valeurs sont sous la résolution de l'instrument.
  - §2.2 — corrige un libellé publié : le rouleau de M1ter est `PHerc1447`, pas `PHerc0172`.
  - §3 — l'entrée de backlog « régénérer les cartes de difficulté » était **périmée** (la
    régénération avait eu lieu le 2026-08-27, la ligne ne l'avait pas suivi) ; l'ancien tableau
    à 64 sondes est conservé replié et daté.
  - §3 — la ligne « thèse forte du témoin négatif » : les anciens chiffres (ρ +0,9979, σ 2,4 %)
    sont déclarés « la signature de la constante cassée, deux quasi-constantes corrélant
    parfaitement » et remplacés.
  - §3 — la ligne M1ter est mise à jour : le pas du témoin « noté 2,4 µm » vaut **7,91 µm**
    (renvoi à `58`).
  - §3 (garde) — l'adossement de `+0,9984` via `docs/mesures/taches_ouvertes.json` est déclaré
    **circulaire** (fichier dérivé des documents) et les registres dérivés sont exclus.
- **preuve de lecture intégrale** :
  - l. 133 : `nombre publié sans record est donc **invisible pour lui**, quel que soit son nombre d'étoiles.`
  - l. 206 : `lplv taches_ouvertes                      # l'inventaire, dérivé des documents`

---

### docs/58_resolution_ou_rouleau.md
- **lignes** : 503
- **nature** : MIXTE (dominante RESULTAT)
- **résumé** : Le document ferme la cause « résolution » de M1ter en commençant par corriger le
  chiffre sur lequel la question reposait : le pas du témoin où le modèle marche n'est pas
  2,4 µm mais **7,91 µm**, donc les deux objets sont à **9 %** l'un de l'autre sur les deux axes.
  Il mesure ensuite ce que coûtent un doublement en plan et un doublement en profondeur, montre
  qu'ils s'aggravent, et conclut que même en créditant la résolution de dix fois son écart réel
  on n'obtient qu'un facteur 2,1 sur les 45 à expliquer. Le document est ensuite **surchargé de
  corrections postérieures** : sa prémisse d'entrée (le facteur 45) est annulée par `60`, deux
  réserves de `65` changent le statut de σ, l'axe « énergie » qu'il ajoute est contredit par une
  ablation publiée, et son §8 quater se corrige lui-même le jour même.
- **conclusions extractibles** :
  - Le pas des couches déclaré à la source : Scroll 1, segment `20230909121925`, volume
    `20230205180739`, `voxelsize` **7,91 µm** ; Scroll 4, segment `20231111135340`, volume
    `20231107190228`, **3,24 µm**. `PHerc1447` est à **8,64 µm** (nom du volume publié).
  - Les deux objets sont à **9 %** l'un de l'autre sur les deux axes : une tuile de 64 px couvre
    506,2 µm contre 553,0 µm (rapport **1,092**), 26 couches couvrent 205,7 µm contre 224,6 µm
    (rapport **1,092**) ; σ de sortie 0,7712 contre 0,0171, rapport **45,2**.
  - Le modèle atteint **AUC 0,925** dans les conditions de `PHerc1447`.
  - Échelle en plan (Scroll 1, profondeur maintenue à 205,7 µm) : 7,91 µm → σ 1,5202 ; 15,82 µm →
    σ 1,4352 (mesuré/attendu **0,945**) ; 23,73 µm → σ 0,9200 (**0,605**) ; 31,64 µm → σ 0,4118
    (**0,271**).
  - Le moyennage n'explique pas la chute : le σ attendu passe de 1,5202 à 1,5176, soit **0,17 %**,
    quand la chute mesurée à 31,64 µm est de **72,9 %**.
  - **Doubler l'échantillonnage en plan coûte 5,6 %** ; l'écart réel entre les deux objets est de
    9 %, soit un neuvième d'un doublement.
  - Échelle en profondeur (Scroll 4, 65 couches à 3,24 µm) : (3,24 ; 84,2 µm) σ 0,8258 ;
    (6,48 ; 84,2) σ 0,8232 (**0,997**) ; (3,24 ; 168,5) σ 0,4887 (**0,592**) ; (6,48 ; 168,5)
    σ 0,4078 (**0,494**). À facteur égal, doubler la profondeur coûte **40,8 %** et doubler le
    plan **0,3 %**.
  - Les deux axes ne sont pas indépendants : la prédiction 0,997 × 0,592 = **0,590** contre un
    mesuré de **0,494**, soit **1,195 fois pire**. Doubler le plan coûte **0,32 %** quand la
    profondeur est juste et **16,6 %** quand elle est déjà doublée — cinquante fois plus.
  - Compte le plus généreux : 0,944 (plan) × 0,592 (profondeur) avec la pénalité 1,195 →
    **0,468**, quand il faudrait **0,022** (= 1/45,2). La résolution rend un facteur **2,1** là
    où il en faut **45** : elle est **éliminée**.
  - Le témoin σ natif de la fenêtre choisie vaut **1,5202**, le double du σ publié sur le segment
    entier (0,7712), parce que la fenêtre est choisie pour son encre (σ = 1,5036, `top=10080
    left=2520`).
  - Écart d'énergie entre les deux objets : **54 keV contre 116 keV**, soit **114,8 %**, contre
    **9,2 %** sur le pas de voxel.
  - Les trois grandeurs ne varient pas indépendamment : dans tout le corpus, **les 31 scans à
    1,2 m** sont ceux de la campagne 8,64/9,36 µm à 113–116 keV — c'est une campagne, pas un
    réglage.
  - Contraste dans le papyrus, chaque pile normalisée par le plafond de son type : témoin 54 keV
    (`uint16`) σ 0,1676, interquartile 0,2742, p95−p50 0,2264 ; objet 116 keV (`uint8`, papyrus
    88 %) σ 0,1349, 0,2235, 0,1765 — rapports **1,243 / 1,227 / 1,283**. **115 % d'écart
    d'énergie ne produit que 24 % d'écart de contraste.**
  - Le contraste reçu (**1,243**) et le σ rendu (0,7712 / 0,6558 = **1,176**) coïncident à
    **5,4 %** : la réponse du modèle suit le contraste d'entrée presque un pour un.
  - Le `.zarray` du dépôt déclare `|u1` : les huit bits de l'objet sont ceux de la campagne, pas
    de notre pont.
  - Plan d'expérience déjà scanné dans le layout `fragments/` : **7 paires isolent l'énergie,
    2 la résolution** (`Frag1`–`Frag4` : 54 et 88 keV tous deux à 3,24 µm ; `Frag5` : 70 keV à
    3,24 et 7,91 µm ; `Frag6` : 53/70/88 keV à 3,24 µm + 53 keV à 7,91 µm).
  - Contrôles de reproductibilité exacts : σ 0,825755 par deux chemins de code (pas 1) et
    σ 0,488698 par deux chemins (pas 2).
  - L'outil ne tournait plus : `torch`, `transformers` et `timesformer_pytorch` n'étaient dans
    aucun groupe de dépendances ; `transformers` doit être borné **sous 5** (la 5.16 exige
    `all_tied_weights_keys`, absent d'un modèle écrit pour 4.46.3) ; l'index CPU ramène
    l'environnement de **4,9 Gio à 1,2 Gio** ; `uv sync` a **désinstallé 19 paquets** (zarr,
    fsspec, s3fs et leur suite) importés à l'intérieur de fonctions et déclarés nulle part.
  - La fenêtre Scroll 4 (`top=2500 left=8000`) est celle des trois candidats (8 000, 20 000,
    32 000) qui rend une étendue franche (−1,813 à +1,257 contre −1,805 à −1,153).
- **rétractations / corrections internes** :
  - §1 — corrige un chiffre publié de `36` §5bis : les « 2,4 µm » de Scroll 1 « ne viennent de
    nulle part » (repris de la campagne ESRF) ; le pas réel est 7,91 µm. Deux documents du même
    dépôt (`12` §, « 6 voxels (47 µm) ») disaient déjà deux pas différents pour la même pile.
  - En-tête — **la prémisse d'entrée du document est tombée** : le facteur 45 venait d'un σ de
    0,0171 qui mesurait une erreur d'échelle (`60`) ; à l'échelle corrigée `PHerc1447` rend
    σ = 0,6558 et **il n'y a plus de facteur 45**. Le document déclare que ses mesures propres
    tiennent, car faites sur les piles **uint16** publiées, hors du bug.
  - §8, deux réserves du 2026-08-28 (`65`) : (1) l'élimination est menée sur des **rapports de
    σ** et rien n'avait vérifié qu'un σ élevé veut dire que le modèle lit — σ arrive **quatrième
    sur six** grandeurs, p de Holm = **0,739** ; (2) le 0,686 d'AUC à 9,72 µm de `63` ne peut pas
    être cité comme preuve, son intervalle **[0,455 ; 0,745]** contient 0,5.
  - §8 — la cause « ce rouleau-ci » est déclarée **non testable** avec le corpus publié : **zéro
    rouleau mesurable** sur cinq interrogés, seuls **4 fragments** le sont.
  - §8 — condition préalable chiffrée (`64`) : l'AUC d'une tuile de 256 px varie d'un écart-type
    de **0,2243** sur le même objet au même réglage ; un écart de 0,10 demande **79 tuiles par
    condition**, de 0,05 en demande **316**. Le premier essai du patron (`63`) avait **10, 11 et
    2** tuiles : « de deux à treize fois trop petit ».
  - §8 bis — **CORRECTION du 2026-08-29 : « l'énergie » n'est pas un axe isolé.** Trois grandeurs
    bougent ensemble (voxel, distance de propagation, énergie) ; la distance de propagation était
    dans l'identifiant long et n'avait jamais été lue.
  - §8 bis — **contredit par une ablation publiée** (`66` §3, Angelotti et al., Extended Data
    Fig. 2) : le « sweet spot » publié pour ~8 µm est **100–120 keV**, donc les 116 keV de
    `PHerc1447` sont **dans** la fenêtre optimale.
  - §8 bis — le **114,8 %** tenait au choix du témoin : contre le seul volume de `PHercParis4`
    portant une prédiction d'encre publiée (2,4 µm / 78 keV), l'écart en énergie tombe à ~48 %
    et celui en résolution monte à ~260 %, ce qui **inverse le classement des axes**.
  - §8 quater — **CORRECTION du même jour** : « il n'y a rien à émuler » tombe. Les fragments qui
    ont la vérité terrain (`Frag1`–`Frag3`) n'ont **pas de recalage** (`transforms/` vide) et
    celui qui a le recalage complet (`Frag6`) n'a **pas d'étiquettes** ; les volumes d'une paire
    n'ont pas la même forme (`Frag1` : 7219 × 1399 × 7198 à 54 keV contre 7229 × 1608 × 7332 à
    88 keV), et `volumes_standardized/` ne recale rien.
- **preuve de lecture intégrale** :
  - l. 323 : `⭐ Les trois mesures s'accordent : **115 % d'écart d'énergie ne produit que 24 % d'écart de`
  - l. 500 : `` ⚠ La fenêtre de Scroll 4 (`top=2500 left=8000`) a été trouvée en sondant trois candidats à ``

---

### docs/59_la_campagne_plutot_que_le_rouleau.md
- **lignes** : 218
- **nature** : MIXTE (dominante RESULTAT négatif)
- **résumé** : Le document se déclare lui-même « RÉFUTATION de sa propre première version ». Il a
  cru remplacer la cause « ce rouleau-ci » par la **campagne de scan**, sur la foi d'un Fisher
  exact à p = 0,0081 ; en séparant un **troisième état** (« jamais tracé ») du groupe « pas
  d'encre », la séparation disparaît (p = 0,5000). Deux corrections supplémentaires du 2026-08-28
  retirent ce qui restait de l'intuition : `PHerc1447` n'est plus « inerte » (bug d'échelle,
  `60`), et le relevé n'énumérait même pas le volume où le modèle marche. Ce qui survit est un
  état des lieux du corpus, pas un discriminant.
- **ce qui a été cru → ce qui l'a remplacé → ce qui reste établi** :
  - **cru** : la campagne de scan (fin, courte propagation, basse énergie) sépare les rouleaux
    lisibles des inertes, Fisher exact unilatéral sur `[6, 1, 11, 27]`, **p = 0,0081**.
  - **remplacé par** : il y a **trois** états, pas deux. Restreinte aux rouleaux réellement
    tentés (`[6, 1, 5, 2]`, 86 % contre 71 %), la comparaison donne **p = 0,5000** — aucune
    séparation. Le scan fin suit **l'attention** de la communauté, pas la lisibilité.
  - **reste établi** : les trois faits du §5 (corpus non tenté, treize du prix, cadre à trois
    états) plus l'énumération de `ou_la_verite_existe.py`.
- **conclusions extractibles** :
  - Partage à deux groupes : encre publiée, 7 rouleaux, 6 (86 %) avec scan fin à courte
    propagation, 53–111 keV, médiane 3 volumes ; pas d'encre publiée, 38 rouleaux, 11 (29 %),
    59–116 keV, médiane 1 volume — Fisher `[6, 1, 11, 27]` **p = 0,0081**.
  - Partage à trois états : **aucun segment publié** 31 rouleaux, 6 (19 %) ; tracé sans encre
    7 rouleaux, 5 (**71 %**) ; encre publiée 7 rouleaux, 6 (**86 %**). Restreint aux tentés :
    `[6, 1, 5, 2]`, **p = 0,5000**.
  - **Trente-et-un rouleaux sur quarante-cinq n'ont aucun segment publié.**
  - **Aucun des treize rouleaux du prix ne publie de détection d'encre** ; dix des treize n'ont
    aucun segment publié ; trois seulement ont été tracés (`PHerc0800`, `PHerc1203`, `PHerc1447`)
    et aucun n'a rendu d'encre.
  - Le même corpus rend **p = 0,0081 ou p = 0,50** selon qu'on range « jamais tracé » avec « pas
    d'encre » ou à part.
  - Le segment où le modèle atteint AUC 0,925 est `20230909121925`, dans le volume
    `20230205180739` : un scan **de 2023, 7,91 µm, 54 keV**, dans l'ancien layout
    `full-scrolls/Scroll1/PHercParis4.volpkg/`, qui ne contient que **deux** volumes (les deux
    moitiés recousues du même scan à 54 keV).
  - Énumération `ou_la_verite_existe.py` : `mesurable` **4 fragments** ; `entraine_dessus`
    **1** (`Scroll1`) ; `sans_verite` **4 rouleaux, 2 fragments`. **Zéro rouleau mesurable.**
  - Le motif de recherche exclut les sorties de modèle : `PHerc0172` publie quatre fichiers
    `ink-detection/…timesformer_scroll5….tif` qui sont des **prédictions**.
  - Les six fragments du layout `fragments/` font varier les grandeurs indépendamment :
    **7 paires isolent l'énergie, 2 la résolution**, et ces fragments portent une vérité terrain
    d'encre publiée.
- **rétractations / corrections internes** :
  - En-tête — le document se déclare « RÉFUTATION de sa propre première version » ; la piste de
    la campagne « ne tient pas ».
  - §1 — correction 1 : `PHerc1447` n'est plus « inerte ». Le σ de 0,0171 mesurait une constante
    de normalisation **de notre côté** ; à l'échelle corrigée il vaut **0,6558**, soit **1,2×**
    le témoin. La colonne « verdict du modèle » portait donc, pour un de ses six rouleaux, un
    fait sur nous. La ligne du tableau est barrée.
  - §1 — correction 2 : `campagnes_de_scan.py` n'interroge que le bucket open-data, donc
    **n'énumère pas le volume où le modèle marche** ; l'inférence « les rouleaux lisibles ont été
    rescannés fin » tombe, puisque **la lecture de référence n'a pas été faite sur un rescan
    fin**. `n_volumes` est un **minorant** pour les rouleaux d'avant la campagne open-data.
  - §2 — la première version de la mesure était « un fait sur NOUS » : `data/encre/<rouleau>/`
    contient ce qui a été **téléchargé** sur demande, pas ce que le dépôt publie.
  - §3 bis — annule le p = 0,0081 du §3 : « la campagne de scan n'est donc pas établie comme le
    discriminant ».
  - §4.3 — la mise en garde sur l'ordre de causalité avait été « laissée à côté du chiffre au
    lieu d'être retirée du chiffre ».
  - §5 — la dernière phrase du document (« aucun rouleau du corpus ne fait varier les grandeurs
    indépendamment ») est barrée puis déclarée **FAUSSE** : vraie des rouleaux, fausse du corpus,
    à cause des six fragments. C'est le **deuxième** effet du même angle mort de
    `campagnes_de_scan.py`.
- **preuve de lecture intégrale** :
  - l. 137 : `**La piste de la campagne ne survit pas** : à corpus restreint aux rouleaux tentés, p = 0,50.`
  - l. 206 : `> voit qu'une moitié du dépôt produit des conclusions justes **sur cette moitié**, et il faut`

---

### docs/60_la_constante_qui_rendait_le_modele_muet.md
- **lignes** : 405
- **nature** : MIXTE (dominante RESULTAT)
- **résumé** : Une constante en dur (`stack / 65535.0`) dans `load_layer_stack` divisait les piles
  **uint8** par le plafond d'un **uint16**, envoyant au modèle des entrées 257 fois trop sombres —
  donc du noir, donc une constante en sortie, qui se lit comme « il n'y a pas d'encre ici ». Le
  partage « le modèle répond / le modèle est inerte » suivait **exactement** le partage des types
  de piles (3 uint16 contre 211 uint8). Le document annule une conclusion publiée du dépôt (`36`
  §5bis) et rouvre M1ter, puis mène une campagne typographique sur les quatre surfaces de
  `PHerc1447` avec critère déclaré à l'avance. Une réserve ajoutée le lendemain (`65`) remet en
  cause **tout le raisonnement**, qui repose sur σ.
- **ce qui a été cru → ce qui l'a remplacé → ce qui reste établi** :
  - **cru** (`36` §5bis) : l'encre n'est pas lisible à 9 µm, sur la foi d'un σ 45 fois plus petit
    que le témoin.
  - **remplacé par** : ce σ mesurait une erreur d'échelle **de notre côté** ; à l'échelle corrigée
    `PHerc1447` rend σ = 0,6558, soit **1,2×** le témoin — le même régime. M1ter est **rouvert,
    pas répondu par l'affirmative**.
  - **réserve ajoutée le 2026-08-28** : tout le document raisonne sur σ, et rien n'avait vérifié
    qu'un σ élevé veut dire que le modèle **lit**. Testé sur les 23 tuiles étiquetées de `63` :
    σ arrive **quatrième sur six**, ρ = **+0,263**, p de Holm = **0,739**. Statut de l'inférence
    changé de « fait » à « hypothèse testée une fois sans succès ».
  - **reste établi** : le bug et son correctif (mesurés, avec contrôle uint16 inchangé), le
    partage des types, le résultat du test groupé de périodicité (p = 0,0007) avec ses cinq
    réserves.
- **conclusions extractibles** :
  - Une pile uint8 divisée par 65535 arrive au modèle **257 fois trop sombre** : moyenne
    **0,002** au lieu de **0,6**.
  - Partage des types dans l'arbre : **3 piles uint16** (`data/layers/`, les stacks publiés :
    Scroll 1 ×2, Scroll 4) contre **211 piles uint8** ; les σ autour de 0,77 sont tous sur les
    trois uint16, les σ autour de 0,015 tous sur des uint8.
  - Même fenêtre, seule l'échelle changeant : `PHerc0172` uint8 divisé par 65535 →
    −1,215 / −1,121 / −1,008, étendue **0,207** ; remise à l'échelle à la main → −1,815 / −0,526
    / +2,463, étendue **4,278** ; après correctif → **identique au chiffre près**.
  - Contrôle uint16 : la même fenêtre de Scroll 1 rend **−1,778 / −1,559 / +1,691** avant et
    après, au chiffre près — aucun résultat publié sur les piles publiées ne bouge.
  - Renversement : `PHerc1447` σ **0,0171 → 0,6558** (1,2× le témoin) ; `PHerc0172` étendue 0,207
    → σ **1,0217** (0,8×) ; Scroll 1 σ 0,7712 inchangé.
  - Surface publiée entière de `PHerc1447` (2980 × 3240, soit **25,7 × 28,0 mm**) : σ = **0,4838**
    sur 9,58 M pixels, étendue **4,266**, soit **1,6×** sous le témoin — et à l'œil c'est de la
    **moucheture**, sans lettres, lignes ni colonnes.
  - Calibrage typographique : à la réduction 4, Scroll 1 (texte lisible à l'œil) rend **0 %** de
    fenêtres périodiques ; sur les **190 cartes publiées** mesurées à la réduction 4, **156 ont
    au moins une fenêtre périodique** et la part médiane de `PHerc0172` vaut 1,0. Réglage
    calibré : réduction **8**, fenêtre **256** → Scroll 1 rend **8/12 (67 %), période 38 px =
    2,4 mm**.
  - `PHerc1447`, surface entière : **2/2 (100 %)**, période 48 px → **3,3 mm**, netteté 0,672 ;
    ses pixels mélangés rendent **0/2**.
  - Couvertures mesurées par le pont zarr : `20250702235910` 392 chunks lus / 232 absents =
    **52,5 %** ; `20250703034159` 742 / 447 = **50,5 %** ; `20251105093211` 744 / **6211** =
    **8,5 %** (226 925 fenêtres sur 251 683, soit 90 %, vides et sautées, contre 40–43 % ailleurs).
  - Résultat de la campagne (2026-08-28, 04h28), réglage calibré : témoin Scroll 1 12 fenêtres,
    8 périodiques (67 %), 38 px, netteté 0,751, mélange 0/12 ; `20250702235910` 2 / 2 (100 %),
    48 px, 0,672, 0/2 ; `20250703025628` 3 / 2 (67 %), 37 px, 0,759, 0/3 ; `20250703034159`
    4 / 2 (50 %), 30 px, 0,710, 0/4 ; `20251105093211` 3 / 2 (67 %), 43 px, 0,492, 0/3.
  - Tests : par carte `20250703034159` `[2, 2, 0, 4]` → **p = 0,2143** ; témoin Scroll 1
    `[8, 4, 0, 12]` → **p = 0,0007** ; **groupé sur les quatre surfaces** `[8, 4, 0, 12]` →
    **p = 0,0007**. Le seuil déclaré est franchi : la périodicité de `PHerc1447` n'est pas un
    tirage — et cela ne dit **pas** que c'est du texte.
  - Réserves sur ce résultat : les périodes ne s'accordent pas (30, 37, 43 et 48 px, étendue
    18 px, rapport **1,6**) ; chaque carte rend exactement **deux** fenêtres périodiques
    (2/2, 2/3, 2/4, 2/3) ; le mélange rend **zéro à chaque fois** ; la quatrième carte est
    nettement moins nette (0,492) et n'est couverte qu'à 8,5 % ; le contrôle par mélange est un
    contrôle **faible**.
  - Témoin négatif réel (`46` §3 ter) : **1 fenêtre périodique sur 5 (20 %)** contre 8/12 (67 %),
    p = **0,50** — mais à cinq fenêtres, un sujet au taux exact de nos cartes rendrait p = 0,083,
    donc le test manquait d'**une** fenêtre pour discriminer et **cette mesure n'établit rien**.
  - Arithmétique du seuil : deux cartes de deux fenêtres groupées font 4 contre 4, soit exactement
    huit, et le plus petit p qu'un Fisher unilatéral puisse rendre vaut `1/C(8,4) = 0,0143`.
  - Prédiction posée avant lecture : 1 à 2 fenêtres mesurables pour la quatrième carte (contre les
    24 annoncées par ses dimensions) ; elle en a rendu **3**.
  - Nouvelles gardes : une pile dont le maximum normalisé est **sous 1/64 de la pleine échelle**
    est refusée (une pile mal mise à l'échelle d'un facteur 257 plafonne à **0,0039**) ; une pile
    dont les couches changent de type est refusée.
  - Reproduction : `FILS=16 bash src/campagnes/campagne_encre_1447.sh` →
    `docs/mesures/typographie_de_nos_cartes.json`. ⚠ `FILS` n'est pas du confort : deux
    campagnes lancées ensemble sur 22 cœurs ont brûlé 26 h et 19 h de CPU pour 2 h de temps
    réel chacune, l'essentiel en contention — elles finissent PLUS TARD qu'en série.
- **rétractations / corrections internes** :
  - En-tête — **réserve ajoutée le 2026-08-28** (`65` §1) qui porte sur tout le document :
    rien n'avait vérifié qu'un σ élevé veut dire que le modèle lit ; σ arrive quatrième sur six,
    p de Holm = 0,739. Le document précise que ça ne réfute pas σ mais change le **statut** de
    l'inférence.
  - §4 bis — M1ter est **rouvert, pas répondu par l'affirmative** ; le même σ qui a fondé le
    résultat négatif ne peut pas fonder le résultat positif.
  - §4 ter — le réglage par défaut de `typographie.py` « ne peut rien conclure sur nos cartes ».
  - §4 quater — **CORRECTION une demi-heure plus tard** : le tableau de comptes de fenêtres est
    calculé depuis les dimensions et ignore la **couverture** ; le nombre de fenêtres mesurables
    de la quatrième carte n'est pas 24.
  - §4 quinquies — **le défaut qui a failli être publié** : la première exécution du test groupé
    a sorti `[16, 8, 0, 24] sur 5 cartes : p = 0,0000` en incluant le **témoin Scroll 1**, dont la
    moitié du signal groupé venait. La docstring disait « du même rouleau » et rien ne le
    vérifiait ; c'est maintenant l'appelant qui nomme ses témoins (`--temoin`).
  - §5 (table des conséquences) : `36` §5bis **ANNULÉ** ; `46` §3–4 **REFAIT**, conclusion changée
    de signe (ρ +0,9979 → −0,0100, σ du positif 2,4 % → 76,4 %) ; `54` **relu, TIENT** ; `58`
    **TIENT** mais sa prémisse d'entrée tombe (plus de facteur 45) ; `59` déjà réfuté le même jour.
  - §6 — le premier jet de contrôles restait vert **quand la constante était remise**, parce qu'il
    portait sur la règle sans traverser `load_layer_stack`.
- **preuve de lecture intégrale** :
  - l. 282 : `⭐ Le seuil déclaré est franchi par le test groupé. Selon le tableau du §4, écrit avant la`
  - l. 398 : `uv run python src/encre/comparer_encre.py data/out/ink_PHerc1447_corrige.npy \`

---

### docs/80_la_batterie_natteint_pas_le_nombre.md
- **lignes** : 254
- **nature** : MIXTE (RESULTAT sur le dépôt lui-même + remède livré sur un module + règle de garde)
- **résumé** : Suite directe de [`61`](../61_les_batteries_qui_ne_pouvaient_pas_echouer.md), qui
  se terminait sur la limite que celui-ci franchit — *« ce contrôle dit qu'une batterie peut
  échouer, jamais qu'elle teste quelque chose d'utile »*. Le 2026-09-05 un patch appliqué à
  moitié a laissé `derouler_des_deux_bords.py` avec un enregistrement référençant trois
  variables inexistantes, **et la batterie est restée verte** : elle n'appelle pas `mesurer`. Le
  balayage syntaxique de tout l'arbre montre que ce n'est pas une exception, et le document
  livre le remède sur le module fautif, ses six sondes, puis un second constat trouvé en chemin.
- **compte exact et cause** :
  - **67 modules en dette sur 152 qui publient une mesure ou une figure** (44 %), **102
    fonctions** hors de portée, relevés par `src/depot/le_chemin_du_nombre_publie.py`, qui ferme
    le graphe d'appels de chaque module et rend `atteintes(main) − atteintes(verifier)`.
  - ⚠⚠ **La portée a été resserrée en cours de route** : la première règle comptait comme
    publieur tout module *mentionnant* `docs/mesures`, donc aussi les purs **lecteurs** —
    trouvé en voyant `le_corpus_des_spires.py` apparaître en dette pour la seule fonction qui
    lit le dépôt distant. Le signe retenu est l'**écriture**, sous ses deux formes : sérialiser
    et écrire un fichier (une mesure), ou enregistrer une image (une figure). Exiger la
    première seule aurait effacé les figures, or `dessiner` est la deuxième branche la plus
    souvent laissée dehors.
  - **Cause** : le chemin qui produit le nombre **lit le dépôt distant**, or `temoins.sh` exige
    que ses batteries tournent hors ligne. Le chemin le plus important du module était donc le
    seul qu'on ne pouvait pas exercer.
- **conclusions extractibles** :
  - ⭐⭐ **La branche laissée dehors porte toujours le même nom** : `mesurer` dans **13** modules,
    `dessiner` dans **10**, `rapporter` dans **6**, `lire` dans **4** — les deux premiers étant
    exactement les verbes qui publient, l'un le nombre, l'autre l'image.
  - Dette non uniforme : `graine` **9 sur 10**, `encre` **23 sur 32**, `nappe` **12 sur 29**
    (elle était à 15), `figures` **10 sur 50**.
  - ⚠⚠ **Un chiffre calculé puis RETIRÉ de la mesure** : « les modules dont la tête de chemin est
    dehors », 67 sur 67. C'est une **identité** — la couverture se propage vers le bas — donc un
    nombre qui ne peut prendre qu'une valeur et se lirait comme une découverte.
  - Le remède : la matière est injectée par paramètre, **pas le découpage** — boîte, seuil de
    cellules, choix des encadrements, marche, combinaison, pondération et enregistrement restent
    dans `mesurer`, donc restent couverts. Le défaut par défaut reste le dépôt distant, donc le
    nombre publié ne bouge pas.
  - ⚠⚠⚠ **La fixture doit être ONDULÉE** : des spires parfaitement décalées du pas sont atteintes
    exactement par un pas normal, donc toutes les erreurs vaudraient zéro et chaque comparaison
    serait satisfaite par des zéros. La phase de l'ondulation **tourne** d'une spire à l'autre,
    sinon c'est encore un décalage exact.
  - L'affichage est sorti de `main` : un bloc de `main` ne peut être exercé qu'en lisant le dépôt
    distant, et c'est là que le patch de septembre a laissé son enregistrement cassé.
  - **Traçabilité dans l'autre sens** : les clés que la figure lit sont extraites de **son arbre
    syntaxique** et confrontées à ce que la mesure publie — une liste dérivée, jamais recopiée.
  - **Vingt-deux sondes**, chacune remettant un défaut — fixture aplatie, spires collées, volume
    décalé d'un demi-pas, volume à un autre pas que le corpus, bloc lointain rendu noir au lieu
    d'absent, absence réessayée, incident persistant devenu absence, lecture rendant le centre de
    sa fenêtre, témoin mélangé qui ne l'est plus, hasard qui n'est plus tiré au hasard, balayage
    rendu à l'envers, boîte qui ne découpe plus, seuil qui ne filtre plus, clé renommée dans un
    affichage ou lue par une figure… Toutes font rougir la batterie qu'elles visent.
    ⚠ Une reste **verte** à bon droit : le contrôle de forme du corpus a déménagé chez son
    propriétaire, et le dupliquer chez ses cinq appelants ferait cinq copies d'une même exigence.
  - ⭐ **La matière est promue dès le deuxième appelant** : `src/nappe/le_corpus_des_spires.py`
    porte l'unique lecteur du corpus, l'unique fixture de spires **et** le volume fabriqué, là où
    cinq modules de `src/nappe/` avaient chacun leur copie du lecteur — deux dérouleurs comparés
    sur deux lectures différentes mesurent d'abord leur désaccord de lecture. **Cinq modules
    réparés** : `derouler_des_deux_bords` 32 → 46, `derouler_par_le_pas_normal` 9 → 17,
    `le_raccrochage_a_la_matiere` 46 → 54, `la_longueur_locale_du_pas` 20 → 30,
    `derouler_en_raccrochant` 63 → 75 contrôles.
  - ⚠⚠⚠ **DEUX VUES D'UN MÊME OBJET, PAS DEUX OBJETS** : les spires sont des **surfaces**, le
    volume une **intensité**. Décrire l'objet deux fois mettrait ses feuilles ailleurs que le
    volume ne les met, et le raccrochage snapperait sur de la matière qui contredit ses ancres,
    en rendant des nombres parfaitement stables. La géométrie est dite une fois, l'intensité en
    est **dérivée**, et le contrôle qui les lie est que le gabarit lu autour d'une spire ait sa
    **crête sur zéro**.
  - **Trois ronds-trips** : feuilles injectées à 135,5 µm → « ne pas bouger » coûte **136,3 µm**,
    longueur lue **136,1 µm**, pas entre crêtes **63,0 voxels** contre 61,2. Tolérance **dérivée**
    de l'ondulation (trois amplitudes), jamais choisie.
  - Le seul point du lecteur de volume qui touche le monde — la requête — est devenu injectable,
    donc ses **trois réponses** sont exercées pour la première fois : une absence se mémorise, un
    incident se réessaie, un incident qui persiste **lève**. Cette logique avait été écrite après
    un incident réel (232 blocs jetés) sans qu'aucune batterie ne puisse l'atteindre.
  - ⚠⚠ **Deux contrôles qui ne pouvaient pas échouer, trouvés par les sondes** : un refus « hors
    de la boîte » où seules les spires étaient déplacées — le volume n'ayant rien à lire là-bas,
    la mesure refusait pour **absence de matière** — et une inégalité **large** qu'un découpage
    inerte satisfait, devenue stricte (20 contre 196 cellules). Même défaut de méthode : un
    contrôle dont on n'a pas cherché par quelle autre voie il pourrait passer au vert.
  - ⚠⚠ Second constat, trouvé en cherchant où inscrire la batterie : **44 batteries que
    `temoins.sh` ne lançait pas**, dont toute la campagne de déroulage et ses figures — le
    harnais rendait « 184 batteries ALL PASS » sans les voir. Le garde-fou qui les nomme existait
    déjà ; il n'avait pas tourné, le harnais complet étant long. Les 44 ont été lancées **une par
    une avant d'être inscrites**, toutes vertes, la plus lente en soixante secondes.
  - Portée : **une fonction atteinte n'est pas une fonction testée** ; le graphe ne suit que les
    appels **par nom**, donc la dette est **surestimée**, jamais cachée ; et seuls les modules qui
    publient une mesure sont comptés.
- **rétractations / corrections internes** :
  - §2 — un chiffre est retiré de la mesure après avoir été calculé, parce qu'il est vrai par
    construction (67 sur 67) et se lirait comme un constat.
  - §2 bis — la **portée elle-même** est corrigée après le premier chiffre publié : la règle
    comptait les purs lecteurs de `docs/mesures` comme des publieurs.
  - §5 — la portée de l'instrument est bornée contre lui-même : il dit qu'une batterie traverse
    une fonction, pas qu'elle y vérifie quoi que ce soit.
- **preuve de lecture intégrale** :
  - l. 225 : `il n'avait simplement pas tourné depuis, le harnais complet étant long. Un contrôle qu'on ne`
  - l. 240 : `tourne. L'erreur va dans le sens prudent : la dette est **surestimée**, jamais cachée.`

---

### docs/61_les_batteries_qui_ne_pouvaient_pas_echouer.md
- **lignes** : 112
- **nature** : MIXTE (RESULTAT sur le dépôt lui-même + règle de garde)
- **résumé** : Trouvé par accident le 2026-08-27 en sondant un autre correctif, sur la phrase
  auto-contradictoire `ALL PASS (2 failures, 28 checks)` : le `verifier()` de
  `src/encre/typographie.py` **imprime** son compte d'échecs puis **le jette** avec un `return 0`
  littéral. Le balayage syntaxique de tout l'arbre montre que ce n'est pas une exception. Le
  document expose ensuite pourquoi sa première règle de détection ratait son propre cas, et le
  cas symétrique découvert le lendemain — une batterie verte comptée ÉCHEC parce que le lanceur
  ne sait pas lire son verdict.
- **compte exact et cause** :
  - **39 batteries incapables d'échouer sur 105 batteries Python** (`src/*/*.py`), relevées par
    `src/depot/batteries_incapables_dechouer.py` qui lit l'arbre syntaxique de chaque
    `verifier()`.
  - **Cause** : `print(f"ALL PASS ({echecs} failures, {controles} checks)")` suivi de `return 0`
    — le compte est tenu, imprimé, et jeté ; la batterie sort verte quoi que disent ses contrôles.
    `temoins.sh` la comptait verte parce que son critère
    (`[ "$rc" -eq 0 ] && grep -q "ALL PASS"`) est exactement celui que cette ligne satisfait par
    construction.
- **conclusions extractibles** :
  - **105** batteries Python, **39** incapables d'échouer.
  - **Aucune ne cachait un échec réel** : les trente-neuf, une fois corrigées, passent toutes.
  - Sur une batterie qui passe, le lanceur n'imprime **que** la ligne de verdict, donc les `❌`
    d'un contrôle en échec n'auraient pas été visibles.
  - La première règle (« tous les `return` rendent le littéral 0 ») a rendu **0 batterie
    signalée** sur la sonde qui remettait le défaut d'origine, parce que ce `verifier()` porte un
    `return 1` ailleurs (refus d'argument).
  - La règle qui décide : **la sortie qui suit le verdict imprimé doit dépendre du compteur
    d'échecs** — propriété syntaxique, donc lisible sans exécuter.
  - Les `return` des **fonctions imbriquées** ne comptent pas (un helper `v(...)` rend `None` ;
    les compter ferait signaler tout le dépôt).
  - Cas symétrique : deux batteries écrites le 2026-08-28 imprimaient `TOUS LES TEMOINS PASSENT`
    et rendaient 0 — elles passaient et auraient été comptées rouges. **132 fichiers sur 135**
    emploient la formule attendue, donc la divergence était invisible à la relecture.
  - La première version de `verdicts_illisibles` cherchait la chaîne `ALL PASS` dans le **texte du
    fichier**, donc était satisfaite par le commentaire et la docstring qui la citent : « une
    garde contre les vérifications incapables d'échouer qui en était une ». La version juste passe
    par l'arbre syntaxique et ne regarde que les littéraux dans les appels à `print`, f-strings
    comprises, avec **quatre contrôles négatifs**.
  - Portée : les **batteries en shell ne sont pas jugées** ; et le contrôle dit qu'une batterie
    **peut** échouer, jamais qu'elle **teste** quelque chose d'utile.
- **rétractations / corrections internes** :
  - §3 — la première règle de détection est déclarée « trop faible » et « elle a raté son propre
    cas » (0 batterie signalée sur la sonde).
  - §3 bis — la première version de `verdicts_illisibles` est déclarée elle-même incapable
    d'échouer (« la sonde n'a pas tiré ») et remplacée.
  - §3 bis (ⓘ) — incohérence apparente assumée et expliquée : `_est_le_verdict` accepte
    « témoins passent » comme verdict, ce qui n'est pas une contradiction car les deux questions
    diffèrent.
- **preuve de lecture intégrale** :
  - l. 82 : `⚠⚠ Et il a fallu s'y reprendre à deux fois, pour la raison exacte que ce document décrit.`
  - l. 102 : `⚠ Ce contrôle dit qu'une batterie **peut** échouer, jamais qu'elle **teste** quelque chose`

---

### docs/62_une_hypothese_qui_meritait_detre_construite.md
- **lignes** : 262
- **nature** : MIXTE (RESULTAT négatif + leçons de méthode)
- **résumé** : Une hypothèse de **falaise de cache L3** est construite pour expliquer un écart de
  ×4,6 entre deux rendus du même rouleau : la bande vivante de 26 × 64 × largeur × 4 octets
  franchit les 24 Mio de L3 à 3780 colonnes, exactement entre les deux segments observés. La
  mesure la réfute — pas de coude à 3780, et surtout un ordre de grandeur ×2142 trop petit. Puis,
  **le lendemain, la question elle-même se dissout** : l'écart n'existait pas, c'était de la
  contention, et le §1 avait mal lu sa propre mesure (1586 % de CPU sur une machine qui en offre
  2200). Le document est délibérément conservé dans l'ordre où il a appris.
- **ce qui a été cru → ce qui l'a remplacé → ce qui reste établi** :
  - **cru (§1)** : la contention est écartée par mesure — `ps` donne 1586 % de CPU et
    `/proc/loadavg` vaut les seize fils demandés.
  - **cru (§2)** : la falaise de cache explique le ×4,6, largeur critique **3780 colonnes**.
  - **remplacé (§3)** : aucun coude à 3780 (6000 colonnes coûtent **moins** que 4260), et le
    rassemblement le plus cher coûte **0,167 ms** par fenêtre quand l'écart à expliquer en vaut
    **356,6** — rapport **×2142**.
  - **remplacé (§7)** : « FAUX, et c'est l'erreur qui a tout déclenché » — 1586 % sur une machine
    qui offre **2200 %** veut dire que **six cœurs faisaient autre chose**, donc exactement la
    contention déclarée écartée. Le facteur 4,6 est un artefact de contention.
  - **reste établi** : la réfutation du §3 (intacte, elle ne dépend pas de l'existence d'un
    écart) et l'argument du §4 (aucune partie de la boucle ne peut dépendre de la taille du
    segment), confirmé par un troisième point.
- **conclusions extractibles** :
  - Les deux rendus : `PHerc1447_complet` 2980 × 3240, 21 128 fenêtres, 2079,5 s, **98 ms par
    fenêtre** ; `1447_20250703025628` 4100 × 4260, **455 ms par fenêtre** — un facteur **4,6**
    pour une surface 1,8 fois plus large.
  - Écartés par mesure : mémoire (33 Gio libres, zéro swap, 2,4 Gio de RSS), type et profondeur
    (`uint8`, 31 couches, `tifffile`), pas et fenêtre (21 et 64 ; 139 × 152 = 21 128 et
    193 × 200 = 38 600).
  - La bande vivante vaut 20,6 Mio à 3240 colonnes (tient dans 24 Mio de L3) et **27,0 Mio** à
    4260 (ne tient plus) ; largeur critique **3780 colonnes**.
  - Mesure du rassemblement (largeur / bande / cache / en ligne / par blocs) : 1024 / 6.50 Mio /
    oui / 0.072 / 0.064 ; 2048 / 13.00 / oui / 0.069 / 0.067 ; 3240 / 20.57 / oui / 0.127 /
    0.166 ; 4260 / 27.04 / NON / 0.167 / 0.121 ; 6000 / 38.09 / NON / 0.119 / 0.075.
  - Une réfutation par **ordre de grandeur** ne se rouvre pas, contrairement à une réfutation par
    la forme d'une courbe.
  - Les trois étapes de la boucle (rassembler, appeler le modèle, disperser) sont indépendantes
    de la taille du segment ; la cause est nécessairement **hors du segment**.
  - A/B sur le même crop, mêmes fils, à la suite : `20250703025628` crop (640, 2560), remplissage
    100 %, **432,1 ms/fenêtre**, **0,5785 fen/fil-s** ; `20250703034159` crop (1920, 1280), 100 %,
    **293,5 ms**, **0,8518** — rapport tombé à **×1,47**. Le crop du segment « lent » rend à
    0,5785 quand son run complet donnait **0,132**, soit **4,4 fois plus vite**.
  - Allure instantanée contre cumul : `20250703025628` cumul 2,109 fen/s, min/médiane/max
    **0,267 / 1,200 / 11,429**, amplitude **×42,9** ; `20250703034159` cumul 7,675, **3,200 /
    7,355 / 12,267**, amplitude ×3,8. **Les deux rendus atteignent le même pic** (11,4 contre
    12,3 fen/s).
  - Même crop du même segment, machine libre : 338,8 s / 432,1 ms / 0,5785 pendant que le segment
    3 rendait, contre **134,1 s / 171,0 ms / 1,4616** sur machine libre — **×2,5**. Le débit
    obtenu **dépasse** la référence de `cout_du_rendu.py` étiquetée « machine libre » (**0,635**),
    donc cette référence était elle-même contendue.
  - La carte rendue est **identique au bit** entre les deux exécutions (écart maximal 0,0, mêmes
    pixels non couverts).
  - Le segment 3 est **plus grand** (3620 × 5220 contre 4100 × 4260) et rend plus vite.
  - Un débit ne se publie pas depuis un **cumul** ; `cout_du_rendu.py` publie des cumuls, ses
    **cinq** observations sont à relire avec cette réserve, et sa colonne « machine partagée » est
    **binaire** là où la contention est continue.
  - Piège de lecture des lignes de progression : `35m04` = 35 min 4 s, `2h54` = 2 h 54 min ; un
    motif qui lirait les deux comme « premier, second » compterait `2h54` pour 2 min 54, soit une
    allure **soixante fois trop grande**.
  - Instruments : `cout_de_la_fenetre.py` (27 contrôles), `figure_hypothese_refutee.py` (13),
    `ab_segments.py` (12), `allure_du_rendu.py` (21).
- **rétractations / corrections internes** :
  - En-tête — « le lendemain, la question elle-même s'est dissoute : il n'y avait pas d'écart à
    expliquer » ; le §7 corrige le §1 ; l'ordre du document est conservé délibérément, une version
    réécrite depuis la fin « ferait passer trois erreurs pour un raisonnement droit ».
  - §1 — la ligne « la contention est écartée » est **barrée** et déclarée « FAUX, et c'est
    l'erreur qui a tout déclenché » : le chiffre (1586 %) était juste, la lecture était fausse
    (machine à 2200 %).
  - §3 — l'hypothèse de la falaise de cache est réfutée (pas de coude, ordre de grandeur ×2142).
  - §4 — le remède (balayage par blocs) est déclaré « mort avec sa cause » et gardé uniquement
    comme **preuve** qu'il n'y avait rien à remédier.
  - §5 — confusion **Mio / Mo** dans la première rédaction (21,6 et 28,4 en mégaoctets décimaux),
    attrapée par la batterie et **gardée dans le fichier** plutôt que corrigée en silence.
  - §5 — une vérification incapable d'échouer écrite deux heures après `61` (condition toujours
    vraie à côté), désormais doublée de son contrôle négatif.
  - §5 — deux batteries imprimaient `TOUS LES TEMOINS PASSENT` alors que `temoins.sh` exige
    `ALL PASS` : vertes, comptées ÉCHEC, **quarante contrôles** perdus du total.
  - §7.4 — table explicite : la réfutation du §3 et l'argument du §4 sont **intacts** ; le
    « facteur 4,6 » du §1 et « la contention est écartée par mesure » **tombent**.
  - §6 — section conservée avec l'avertissement qu'elle est antérieure au §7 : « L'écart de ×4,6
    n'est plus "inexpliqué" : il n'existe pas » ; sa dernière ligne « était la bonne piste et je
    l'avais rangée en dernier ».
- **preuve de lecture intégrale** :
  - l. 165 : `même code, 4,4 fois plus vite.** Ce n'est donc ni sa taille ni son contenu.`
  - l. 247 : `⚠ Ce n'est pas bloquant pour le Graal : la campagne livre ses quatre cartes dans tous les cas.`



Dépôt : `/home/masterlaplace/LplVesuvius`. Six fichiers lus intégralement, comptes de lignes
mesurés par `wc -l` avant lecture. `docs/69_*.md` non lu, hors périmètre sur consigne.

---

### docs/63_la_premiere_verite_terrain.md
- **lignes** : 172
- **nature** : RESULTAT
- **résumé** : Premier document du dépôt à mesurer une AUC contre de vraies étiquettes
  (`inklabels.png` des fragments du concours de détection d'encre) et non contre un rendu
  publié. Il établit un signal réel sur `PHercParis2Fr47` (AUC 0,746, contrôle par mélange à
  0,500), puis élimine une seconde fois l'axe résolution en montrant que ramener le fragment
  au pas d'entraînement **fait baisser** l'AUC. La réplication sur deux autres fragments ne
  confirme pas le chiffre, et le document se corrige lui-même en cours de route sur la façon
  de rapporter cette dispersion.
- **conclusions extractibles** :
  - `PHercParis2Fr47` (`Frag1`), surface exposée à 54 keV, 65 couches publiées dont les **26 du
    milieu**, fenêtre de 1024 px : sur tout le segment, 1 018 081 pixels, 31,9 % d'encre,
    **AUC 0,746**, précision 0,552, rappel 0,609, F1 0,579.
  - Sur les lignes annotées : 748 678 pixels, 43,3 % d'encre, AUC 0,701, précision 0,609,
    rappel 0,609, F1 0,609.
  - Sur les tuiles annotées (256 px) : 628 705 pixels, 51,6 % d'encre, AUC 0,677,
    précision 0,654, rappel 0,609, F1 0,631.
  - Le contrôle par mélange rend exactement 0,500 sur les trois domaines ; le gain de
    précision sur le hasard vaut 1,7× / 1,4× / 1,3×.
  - La fenêtre a été choisie sur la couverture de papyrus lue dans `mask.png`, triée par
    distance au centre de masse, sans regarder les étiquettes ; la part d'encre portée
    (31,8 %) est rapportée, jamais choisie. Le contrôle asserte que la signature de
    `fenetre_pleine` ne prend aucune étiquette (12 contrôles).
  - `Frag1` est scanné à 3,24 µm quand le modèle a été entraîné à 7,91 µm, soit un écart de
    144 %, là où `58` en éliminait un de 9 %.
  - Balayage d'échelle sur `Frag1` : 3,24 µm (×1) AUC 0,746 / précision 0,552 / rappel 0,609 ;
    6,48 µm (×2) AUC 0,693 / 0,429 / 0,821 ; 9,72 µm (×3) AUC 0,686 / 0,408 / 0,864.
  - Ramener le fragment au pas d'entraînement n'améliore pas l'AUC : elle tombe, et de façon
    monotone. Les facteurs ×2 et ×3 encadrent les 7,91 µm de l'entraînement et les deux sont
    sous le natif. La résolution n'explique donc pas l'écart aux 0,925.
  - Seconde élimination indépendante de l'axe résolution : `58` l'avait éliminé par émulation
    sur `Scroll 1` contre une carte publiée ; ici c'est un autre objet, contre de vrais labels.
  - Décimer fait dire l'encre plus souvent : le rappel monte de 0,609 à 0,864 pendant que la
    précision tombe de 0,552 à 0,408.
  - `Frag2` (`PHercParis2Fr143`), fenêtre à (7824, 4032), encre 20,6 % : AUC 0,600,
    précision 0,257, rappel 0,345, gain sur le hasard 1,3×.
  - 0,746 n'est pas reproductible sur un second objet : l'écart est de 0,146 d'AUC, et il ne
    s'explique pas par la densité d'encre, l'AUC étant indépendante de la prévalence par
    construction (mesure de rang, pas de taux).
  - Le contrôle par mélange rend 0,500 dans les deux cas : les deux portent un signal réel, le
    désaccord porte sur *combien*, pas sur *s'il y en a*.
  - `Frag3` (`PHercParis1Fr34`), fenêtre à (3424, 2352), 1,55 % d'encre dans la fenêtre.
  - Tableau à trois fragments : `Frag1` 31,8 % → 0,746 / 0,701 / 0,677 ; `Frag2` 20,6 % →
    0,600 / 0,594 / 0,581 ; `Frag3` 1,55 % → 0,575 / 0,523 / 0,704. Étendues respectives :
    0,171 (tout le segment), 0,178 (lignes annotées), 0,122 (tuiles annotées).
  - L'exception change selon le domaine rapporté : sur « tout le segment » c'est `Frag1` qui se
    détache par le haut ; sur les tuiles annotées c'est `Frag2` qui se détache par le bas, et
    `Frag3` remonte de 0,575 à 0,704, au-dessus de `Frag1`.
  - Formulation juste retenue : notre chaîne rend entre 0,52 et 0,75 selon le fragment ET le
    domaine, avec une étendue de 0,12 même sur le domaine le plus resserré.
  - Renvoi mesuré vers `64` : dispersion dans un fragment 0,2243 contre 0,0391 entre fragments,
    soit 5,7 fois moins ; savoir de quel fragment vient une tuile explique 3 % de l'écart ;
    2 paires sur 3 ont des intervalles de confiance qui se recouvrent ; il aurait fallu
    27 tuiles par fragment pour établir l'écart de 0,171, on en avait 10, 11 et 2.
  - Une tuile sur cinq est sous le hasard : 5 sur 23, la plus basse à 0,158.
  - Réserve : la décimation conserve le détail en profondeur qu'un vrai scan grossier n'aurait
    pas, donc les deux AUC décimées sont un majorant — ce qui renforce la conclusion puisqu'elles
    sont déjà plus basses que le natif.
  - Réserve : on ne peut pas vérifier d'ici si `Frag1` était dans l'entraînement du modèle
    (`timesformer_GP_scroll1` vient des étiquettes du Grand Prize 2023, Scroll 1 ; les fragments
    sont le jeu du concours antérieur).
  - Réserve : un fragment n'est pas un rouleau — surface ouverte, plate, n'ayant pas traversé
    de déroulage virtuel.
- **rétractations / corrections internes** :
  - §2 ter, explicitement : « **Correction de ce que le §2 bis publiait il y a une heure.**
    “Entre 0,60 et 0,75 selon le fragment” a été écrit sur deux points lus sur “tout le
    segment”. Ce domaine est **contaminé** ». Remplacé par « entre 0,52 et 0,75 selon le
    fragment ET le domaine ».
  - Fin de §2 ter (« la dispersion est réelle […] et elle n'est pas expliquée ») est marquée
    **RÉPONDU le 2026-08-28** par un encadré renvoyant à `64` : « Il n'y avait pas de cause à
    chercher ». Et la consigne renforcée : « les trois chiffres ne doivent pas être comparés
    entre eux », ni servir de référence pour juger un réglage.
  - §3 point 4 : le texte « Une seule fenêtre, un seul fragment. » est **barré**, ainsi que
    « Ce qui reste ouvert n'est plus “répliquer” mais expliquer la dispersion. » — remplacés
    par le renvoi à `64` (ICC 0,030, expérience deux à treize fois trop petite).
  - §3 point 5 ajouté après coup : une tuile sur cinq sous le hasard, « aucune des trois AUC
    publiées ne le laisse voir ».
- **preuve de lecture intégrale** :
  - ligne 114 (après 60 % du fichier) : `ⓘ Et aucun domaine ne les fait s'accorder. La dispersion est réelle, elle est plus grande que`
  - ligne 170 (dans les 15 dernières lignes non vides) : `**Voir aussi** : [`58`](58_resolution_ou_rouleau.md) §8 bis et §8 quater,`

---

### docs/64_la_dispersion_netait_pas_un_effet.md
- **lignes** : 141
- **nature** : RESULTAT
- **résumé** : Répond à la seule tâche laissée ouverte par `63` en montrant qu'il n'y avait pas
  de cause à chercher : la dispersion tuile à tuile **dans** un fragment est 5,7 fois celle
  **entre** fragments, l'ICC vaut 3,0 %, et 2 intervalles sur 3 se recouvrent. Le document
  documente aussi le piège de l'erreur-type de Hanley–McNeil (cent fois trop étroite sur des
  cartes auto-corrélées), réfute une hypothèse de l'auteur par sa propre mesure, et sort le
  calcul de taille d'échantillon qui manquait avant de lancer l'expérience.
- **conclusions extractibles** :
  - Écart-type dans un fragment, de tuile à tuile : 0,2243. Écart-type entre fragments :
    0,0391. Rapport : 5,7×.
  - Part attribuable au fragment (corrélation intraclasse) : 3,0 %.
  - Paires de fragments dont les intervalles de confiance se recouvrent : 2 sur 3.
  - Savoir de quel fragment vient une tuile explique 3 % de la dispersion ; l'écart publié
    entre `Frag1` et `Frag2` est plus petit que l'écart entre deux tuiles voisines du même
    fragment.
  - Erreur-type par tuiles contre Hanley–McNeil : `Frag1` 0,0601 contre 0,00055 (×109) ;
    `Frag2` 0,0712 contre 0,00072 (×99) ; `Frag3` 0,0822 contre 0,00239 (×34).
  - La formule de Hanley–McNeil suppose des tirages indépendants et une carte d'encre est
    massivement auto-corrélée ; appliquée telle quelle elle déclarerait significatif n'importe
    quel écart entre n'importe quelles cartes, y compris deux tirages du même fragment.
  - Sur `Frag3`, l'AUC groupée vaut 0,575 quand la moyenne des AUC par tuile vaut 0,845, même
    modèle et mêmes étiquettes.
  - Alignement des niveaux par rang dans chaque tuile : `Frag1` 0,677 → 0,626 (−0,052) ;
    `Frag2` 0,581 → 0,531 (−0,050) ; `Frag3` 0,801 → 0,703 (−0,098).
  - Aligner les niveaux rend l'AUC pire sur les trois fragments : les différences de niveau
    entre tuiles portent du signal, et la retirer coûte de 0,05 à 0,10.
  - 5 tuiles sur 23 sont sous le hasard, la plus basse à 0,158 ; `Frag2` sort à 0,600 en
    portant trois tuiles sous 0,35.
  - Corrélation entre l'AUC d'une tuile et sa densité d'encre : −0,248 (les tuiles les plus
    encrées s'en sortent légèrement moins bien).
  - Établir l'écart de 0,171 d'AUC au seuil usuel, avec un écart-type de tuile de 0,2243,
    demande **27 tuiles par fragment** ; on en avait 10, 11 et 2. Et c'est un minorant, la
    formule supposant des tuiles indépendantes.
  - Le contrôle par mélange rend 0,500 sur les trois fragments et les trois domaines : la
    question « le modèle lit-il de l'encre » reste répondue par oui ; ce qui tombe est le
    classement entre eux.
- **rétractations / corrections internes** :
  - §3, explicitement titré « Une hypothèse à moi, réfutée par sa propre mesure » : l'hypothèse
    d'un décalage de niveau par région est fausse, et son contraire est vrai.
  - §2 : condamnation d'usage de Hanley–McNeil dans ce contexte — gardée dans le fichier « non
    pour servir, mais pour que personne ne la rapplique un jour en croyant bien faire ».
  - §6.1 : deux intervalles qui se recouvrent ne prouvent pas l'égalité ; il reste possible que
    `Frag1` soit réellement meilleur que `Frag2`.
  - §6.2 : `Frag3` repose sur 2 tuiles — « Ce n'est pas un résultat, c'est un avertissement ».
  - §6.3 : la tuile de 256 px est un choix non balayé ; l'ampleur (mais pas le sens) de la
    conclusion dépend de la maille.
  - Note d'instrument : sonde de l'ICC naïf « qui passait au vert avant d'être écrite ».
- **preuve de lecture intégrale** :
  - ligne 102 (après 60 % du fichier) : `> **27 tuiles par fragment.** On en avait **10, 11 et 2.**`
  - ligne 136 (dans les 15 dernières lignes non vides) : `**Voir aussi** : [`63`](63_la_premiere_verite_terrain.md) pour les trois AUC dont ce document`

---

### docs/65_ce_que_sigma_ne_dit_pas.md
- **lignes** : 123
- **nature** : RESULTAT
- **résumé** : Teste pour la première fois deux inférences que le dépôt faisait depuis des
  semaines — qu'un σ élevé signifie que le modèle lit, et que 0,686 d'AUC à 9,72 µm signifie
  que l'encre y est lisible. Aucune des deux ne survit telle quelle : σ arrive quatrième sur
  six et ne tranche pas ; à 6,48 et 9,72 µm l'intervalle de confiance contient 0,5. Le document
  montre aussi, par balayage de maille, que redécouper plus fin ne sauve pas la mesure.
- **conclusions extractibles** :
  - Corrélations de rang contre l'AUC par tuile (23 tuiles) : aire médiane des taches −0,448,
    IC 95 % [−0,70 ; −0,07], p permutation 0,0312, p Holm 0,187 ; hauteur médiane −0,319,
    [−0,69 ; +0,11], 0,1258, 0,629 ; composantes +0,284, [−0,11 ; +0,61], 0,1848, 0,739 ;
    **σ +0,263**, [−0,22 ; +0,64], 0,2244, **0,739** ; épaisseur de trait −0,108,
    [−0,54 ; +0,32], 0,6279, 1,000 ; couverture −0,097, [−0,50 ; +0,31], 0,6529, 1,000.
  - σ arrive quatrième sur six et ne tranche pas : son signe est celui qu'on espère, mais
    l'intervalle contient zéro et la valeur p corrigée vaut 0,739.
  - `60` fait reposer « le modèle n'est pas inerte sur `PHerc1447` » sur un σ de 0,6558, soit
    1,2× le témoin.
  - Découpage 4 × 4, chaque tuile couvrant le seizième du même morceau de papyrus à toutes les
    échelles : natif 3,24 µm → AUC groupée 0,746, moyenne des tuiles 0,674, IC 95 %
    [0,541 ; 0,788], n = 11, témoin par mélange [0,498 ; 0,502] ; ×2 6,48 µm → 0,693 / 0,594 /
    [0,468 ; 0,722], n = 10, témoin [0,495 ; 0,500] ; ×3 9,72 µm → 0,686 / 0,599 /
    [0,455 ; 0,745], n = 10, témoin [0,495 ; 0,500].
  - À 3,24 µm la lisibilité est établie : l'intervalle exclut 0,5, et c'est la première fois que
    le dépôt l'établit contre de vraies étiquettes plutôt que contre un rendu publié.
  - À 6,48 et 9,72 µm la lisibilité n'est pas établie : les deux intervalles contiennent 0,5.
  - Le témoin par mélange est serré autour de 0,5 aux trois échelles ([0,495 ; 0,502]) : ce
    n'est pas lui qui élargit les intervalles.
  - Balayage de maille (largeur d'intervalle, nombre de tuiles gardées) : natif 3×3 0,227 (7),
    4×4 0,248 (11), 5×5 0,184 (16), 6×6 0,155 (23), 8×8 0,189 (35) ; ×2 0,228 (7), 0,250 (10),
    0,212 (16), 0,202 (21), 0,179 (33) ; ×3 0,197 (7), 0,288 (10), 0,220 (16), 0,212 (21),
    0,202 (32).
  - À 9,72 µm la largeur reste autour de 0,20 quelle que soit la maille : l'écart-type grandit
    aussi vite que le compte de tuiles, cette carte ne peut pas trancher. Ce qu'il faut n'est
    pas un meilleur découpage mais plus de surface rendue.
  - Au natif, 6×6 donne la largeur la plus faible (0,155) et 8×8 remonte à 0,189.
  - Ce qui est mesuré aux échelles décimées est un majorant de ce qu'un vrai scan à 9,72 µm
    rendrait ; un majorant qui n'établit rien ne répond rien.
- **rétractations / corrections internes** :
  - §1 : requalification explicite du statut de σ — « “σ est élevé donc il y a du signal” était
    traité comme un fait et n'est qu'une **hypothèse non testée**, qui a maintenant été testée
    une fois sans succès ». Ne vaut pas réfutation (§4.2).
  - §2 : le chiffre 0,686 à 9,72 µm publié par `63` §2 « se lit comme une réponse et n'en est
    pas une » — il répondait à une autre question (la résolution explique-t-elle l'écart aux
    0,925 ?).
  - §4.1 : le document n'établit pas que l'encre soit illisible à 9,72 µm ; un intervalle qui
    contient 0,5 dit que la différence n'est pas établie, jamais qu'elle est nulle.
  - §4.3 : ne renverse pas `58` (deux objets réels à 9 % l'un de l'autre contre un objet décimé
    d'un facteur 3), mais interdit de citer « 0,686 à 9,72 µm » comme preuve que la résolution
    ne coûte rien.
  - §1 (limite) : les tuiles viennent de fragments à 3,24 µm, pas du rouleau à 8,64 µm ; un
    lien σ↔qualité pourrait exister là et pas ici.
- **preuve de lecture intégrale** :
  - ligne 83 (après 60 % du fichier) : `À 9,72 µm la largeur reste autour de **0,20** quelle que soit la maille : l'écart-type grandit`
  - ligne 120 (dans les 15 dernières lignes non vides) : `**Voir aussi** : [`64`](64_la_dispersion_netait_pas_un_effet.md) pour le plancher de bruit qui`

---

### docs/66_audit_danteriorite.md
- **lignes** : 173
- **nature** : MIXTE (registre d'audit d'antériorité, mais §3 établit des faits vérifiés
  contre le papier officiel et contre les métadonnées du checkpoint)
- **résumé** : Audit adversarial du 2026-08-29 par quinze agents (un chercheur par résultat
  cadré pour réfuter la nouveauté, puis deux sceptiques par résultat encore dit nouveau), mené
  sur le miroir du site du prix et 35 dépôts déjà clonés sur le disque. Verdict global : sur
  14 résultats principaux, 6 sont déjà publiés, 8 partiellement, aucun n'est revenu « rien
  trouvé ». Deux cas sont pires qu'une antériorité (un résultat possiblement faux, un résultat
  contredit), et l'audit se conclut lui-même sur un constat de radotage : sa « conclusion » et
  sa recommandation phare étaient déjà dans l'article et déjà faites.
- **conclusions extractibles** :
  - **Décompte global : sur 14 résultats principaux, 6 sont déjà publiés, 8 le sont à moitié,
    et AUCUN n'est revenu « rien trouvé ».**
  - Six résultats sur quatorze sont réfutés par des fichiers de `data/site/` et
    `data/repos/villa/`, c'est-à-dire le miroir du site du prix et son monorepo officiel, tous
    deux clonés depuis le début.
  - **VERDICT « déjà connu » (6 / 14)**, avec la source citée par l'audit :
    1. **l'énergie du faisceau** → `2026_open_problems.html` (« Three coupled scan
       parameters », mêmes trois paramètres) et mesuré dans le papier officiel (`pdf/main.pdf`,
       Angelotti et al., Extended Data Fig. 2) : balayage 4×4 énergie × distance.
    2. **aucune vérité terrain sur rouleau** → `villa/scrollprize.org/static/data/datasets/ink-labels-README.md`
       (« For scrolls — where no infrared ground truth exists ») et le goulot 2026
       (« reliably tell "no ink" apart from "no ink recovered yet" »).
    3. **le fold de validation du GP** → `fragments=['20231210121321']` est une ligne du script
       d'entraînement publié, repris octet pour octet dans `villa/ink-detection/`.
    4. **α suit la fenêtre** → `windcheck/engines/atlas_query.cpp` (« "no surface within the
       search radius" is a different statement from "the nearest surface is exactly this
       far" ») ; `selfgap.py` fait varier le rayon 256→1024.
    5. **étendre une nappe** → workflow officiel, même geste (« Grow this segmentation some
       small-ish number of generations at a time, between 10-30 […] Repeat until you feel like
       stopping », `villa/…/35_segmentation.md`).
    6. **la graine décide** → `vesuvius-automesh/render_driver.py` + `villa/lasagna/volume_scale.py`,
       qui contient déjà notre `niveau_du_maillage.py`.
  - **VERDICT « partiellement connu » (8 / 14)**, ligne de partage constante : le mécanisme et
    la question sont publiés en prose ou en code, le nombre ne l'est pas. Six sont détaillés :
    1. `dispersion-fenetre` : l'argument existe sur le pas d'enroulement (« it is the variance,
       not the mean, that decides usability », `winding-ruler`) ; notre ICC de 0,030 et le n
       requis, non.
    2. `hanley-mcneil` : le bootstrap par grappes est implémenté et justifié (`tifxyz-doctor`),
       « patches are not independent draws » (`windcheck`) ; le facteur 109× et son portage à
       une AUC, non — le versant encre n'a jamais mis d'incertitude sur une AUC, ni `ink-id`,
       ni `villa`, ni `LSM`.
    3. `temoin-negatif-alpha` : la surface en travers comme classe d'échec est chiffrée
       (`vesuvius-automesh`), « null control » écrit mot pour mot (`windcheck/selfgap.py`) ;
       faire tourner un détecteur d'encre dessus, non (le dépôt le mieux placé écrit « not from
       a known-ink control », « there are no ink claims here »).
    4. `juge-modele` : la question est dans la FAQ et dans les critères du prix depuis 2023, et
       le domaine exclut explicitement l'outil (« No OCR or language model was used ») ; le
       juge modèle de langue avec témoin dans l'image et condition `vierge | vierge`, non.
    5. `pas-de-trace` : 20 est le défaut partout, et `GrowPatch.cpp` lève une exception sur tout
       `step_size` différent du pas de la grille de normales — cinq des six points de notre
       balayage sont interdits par le logiciel ; recommander `step_size ≥ 20` restitue un
       réglage d'usine.
    6. `etendre-nappe` : le workflow officiel a trois étapes par pas (grandir / corriger /
       recommencer) quand nos chaînes en ont deux.
  - Le checkpoint que trois projets indépendants désignent comme *le* modèle d'encre du Grand
    Prize s'appelle `timesformer_wild15_20230702185753_0_fr_i3depoch=12.ckpt`, donc fold de
    validation = 20230702185753, et non 20231210121321.
  - On ne peut pas trancher depuis ici : notre copie est au format HuggingFace et la conversion
    a effacé la provenance — `model.safetensors` ne porte que `{'format': 'pt'}`, aucun
    hyperparamètre, aucun nom de run (vérifié le 2026-08-29).
  - Le test qui tranche ne demande aucune métadonnée : mesurer le modèle sur les deux segments ;
    celui sur lequel il score le moins bien est celui qu'il n'a pas vu.
  - Le papier officiel publie une ablation contrôlée dont le verdict va contre le nôtre : « For
    a pixel size of about 8 µm the empiric sweet spot for the energy is between 100 and 120 keV
    with propagation distances of about 3 m. » Les 116 keV de `PHerc1447` sont donc dans la
    fenêtre optimale publiée pour sa résolution, pas hors norme.
  - Sur un second balayage (62 / 77 / 89 keV) : « the general contrast drop is visible but
    gentle, however the layer separability increases ».
  - Notre chiffre tenait au choix du témoin : le seul volume de `PHercParis4` portant une
    prédiction d'encre publiée est à 2,4 µm / 78 keV, pas 7,91 µm / 54 keV. Contre ce témoin,
    l'écart en énergie tombe à ~48 % et celui en résolution monte à ~260 % — le classement des
    axes s'inverse.
  - Cinq angles morts nommés que l'audit ne pouvait pas voir : le Discord du Vesuvius Challenge
    (non miroité) ; les discussions Kaggle 2023 ; `vesuvius-repro` (TAUIL, non cloné, dont la
    citation de prix nomme « negative-result analysis of cross-scroll ink-signal
    measurement ») ; le PDF OverthINKingSegmenter (« Ink detection model resolution analysis »,
    primé 1 500 $, absent du disque) ; toute la littérature académique (Obuchowski 1997 sur les
    courbes ROC groupées, l'analyse d'image documentaire, la littérature sur l'hallucination
    des modèles vision-langage).
  - Sur quatre de nos sept fragments résistants, l'antériorité hors domaine est probable à très
    probable.
  - Les cinq dépôts que l'audit recommandait de citer (`vesuvius-automesh`, `windcheck`,
    `winding-sync`, `tifxyz-doctor`, `winding-ruler`) sont **tous les cinq déjà cités** ;
    `00_etat_de_lart.md` est un état de l'art entier bâti dessus, et `windcheck` seul apparaît
    dans vingt documents.
  - `src/depot/deja_dit.py` signale 164 paires de documents qui redisent la même chose sans se
    citer, au premier passage, dont `00_etat_de_lart.md` et `01_goulot_deroulage.md` qui portent
    le même état de l'art.
  - Coût de l'instrument : workflow `audit-anteriorite`, 15 agents, 14 résultats, 4,5 M jetons,
    873 appels d'outil, 14 min.
- **rétractations / corrections internes** :
  - §3, second bloc : le résultat « énergie » n'est pas seulement précédé, il est **contredit**
    par l'ablation du papier officiel ; et « le 114,8 % venait d'avoir pris pour référence un
    scan de 2023 que le pipeline actuel n'utilise plus » — le classement des axes s'inverse
    contre le bon témoin.
  - §3, premier bloc : le fold de validation `20231210121321` cité par le dépôt est
    possiblement le mauvais (`20230702185753`), et le résultat peut donc être faux, pas
    seulement connu ; indécidable depuis ce disque.
  - §6 : « Correction du 2026-08-29, sur une remarque de l'auteur » — la conclusion de l'audit
    (« on n'a rien découvert, on a juste fait des outils de mesure ») était déjà la thèse écrite
    de `docs/article/article.typ`, qui cite déjà `@angelotti2026complete`. Trois fois dans la
    même session ce cadrage a été présenté comme une trouvaille.
  - §6 bis : « LA RECOMMANDATION PHARE DE L'AUDIT ÉTAIT DÉJÀ FAITE » ; défaut imputé à la
    conception du workflow (chercher l'antériorité dehors sans vérifier si elle était déjà citée
    dedans), pas aux agents.
  - §5 : une absence de trouvaille n'est pas une preuve de nouveauté.
- **preuve de lecture intégrale** :
  - ligne 113 (après 60 % du fichier) : `⚠⚠ Sur quatre de nos sept fragments résistants, l'antériorité **hors domaine** est probable à`
  - ligne 169 (dans les 15 dernières lignes non vides) : `**Instrument** : workflow `audit-anteriorite` (15 agents, 14 résultats, 4,5 M jetons, 873 appels`

---

### docs/67_audit_des_outils.md
- **lignes** : 134
- **nature** : MIXTE (audit/inventaire des outils, avec trois corrections techniques mesurées
  au §4 et une auto-correction au §6)
- **résumé** : Second audit adversarial (2026-08-29), déclenché par une question de l'auteur :
  et si même nos outils de mesure existaient déjà ? Réponse : oui en partie, et la faute est
  imputée à l'assistant — les dépôts équivalents étaient déjà clonés sur le disque avant que la
  plupart des scripts soient écrits. Le mode de défaillance est un échec de vocabulaire (aucun
  équivalent ne porte notre nom français), le coût est chiffré à l'ordre de la semaine de
  travail net, et 27 outils restent sans équivalent — statistique, juge automatique en aveugle,
  test de convergence, étage polaire, hygiène de dépôt.
- **conclusions extractibles** :
  - **Décompte global annoncé : 98 outils audités — 22 existaient déjà, 50 partiellement,
    27 sans équivalent — dans les 13 Go des 35 dépôts clonés, avec 23 verdicts de temps
    réellement perdu.** (⚠ le tableau du §1 totalise **99** outils et le bloc « Relevés » parle
    de « 99 verdicts », alors que le titre et le §7 écrivent 98 ; le document porte les deux
    nombres.)
  - **VERDICT par famille** (outils / existait / partiel / rien / temps perdu) :
    - `commun` + `tracecheck` : 10 / 1 / 6 / 3 / 4
    - `nappe` : 9 / **5** / 3 / 1 / **5**
    - `graine` : 13 / 1 / 9 / 3 / 1
    - `encre` : 11 / 1 / 7 / 3 / 2
    - `volume` : 7 / 2 / 4 / 1 / 1
    - `excision` : 13 / 3 / 8 / 2 / 3
    - `outils` (shell) : 14 / **6** / 6 / 2 / **6**
    - `depot` : 22 / 3 / 7 / **12** / 1
    - **total : 99 / 22 / 50 / 27 / 23**
  - 22 est un minorant : ni `villa` (7,3 Go) ni `windcheck` (4,3 Go) n'ont été lus
    intégralement ; les clones sont en profondeur 1, donc les dates citées sont des dates de
    dernier commit et, pour certains fichiers, l'antériorité est indécidable depuis ce disque.
  - Aucun équivalent ne porte notre nom : écart entre spires = *winding pitch* ; saut de spire =
    *sheet consistency* / *winding jump fraction* ; champ de correction = *subvoxel
    re-centering* ; distance à la matière = *CT support* ; planéité = *linearity*. Un `grep` sur
    nos concepts français ne rend rien, un `grep` sur leurs noms anglais rend tout.
  - Le bloc le plus cher n'est pas du code mais une campagne : `carte_difficulte.sh` +
    `nappe/espacement_spires.py` — `winding-ruler/atlas/winding_atlas_v1.py` mesure l'écart
    entre spires depuis la même prédiction m7/th0.2, et `results/atlas_collection_v2.csv`
    contient les 14 rouleaux de notre tableau plus 22 autres, avec les tailles de voxel que
    notre docstring dit « pas devinables ».
  - `encre/typographie.py` (1066 l.) → `villa/volume-cartographer/scripts/spiral/get_ink_metrics.py`,
    monorepo officiel, mesure l'interligne par fenêtres glissantes de 512 px, la même valeur que
    la nôtre, avec un garde-fou anti-bruit et une détection de colonnes que nous n'avons pas.
  - `volume/apparier_volumes.py` (371 l.) → appariement que `metadata.min.json` déclare et que
    `vesuvius-catalog` expose en une ligne.
  - `excision/measure.py` → `windcheck/bench/normal_profile.py` fait le même échantillonnage
    apparié avec la même justification écrite, sur 53 points le long de la normale là où nous
    lisons un voxel ; il vit dans le dépôt dont nous auditions les réparations.
  - `commun/trouver_graine.py` → le plafond d'occupation est un argument par défaut dans
    `vesuvius-automesh/select_regions.py:27` (`max_occ: float = 0.50`), et notre formule de
    planéité est littéralement `khartes/st.py:119`.
  - Six scripts de `src/outils/` ont un équivalent : `balayage_maxedge.sh`,
    `mosaique_rouleau.sh`, `tracer_une_graine.sh` (le harnais officiel), `fetch_layers.sh`,
    `apercu_surface.sh`.
  - `build_atlas_v2.py` contredit la conclusion de `pyramid.py` : ils ont mesuré que le niveau 2
    fusionne les feuilles voisines — pas surestimé de 10,3 %, 36/36 négatif — et ont tout
    recalculé au niveau 1 ; notre outil tourne encore au niveau 2 par défaut et le biais se
    propage dans `ecart_de_maillages.en_micrometres()` via `spire_um`.
  - `sensibilite_centre.py` existe à cause d'une prémisse fausse : l'ombilic est publié pour le
    rouleau qu'il nomme (`spiral-fitting/scroll1_umbilicus.py` cite
    `dl.ash2txt.org/.../umbilici/umbilicus-scroll1a_zyx.txt`) ; notre vérification portait sur
    le bucket S3, pas sur `dl.ash2txt.org`.
  - La posture méthodologique n'est pas distinctive : `windcheck/bench/reconcile.py` décrit
    notre propre panne de chiffres publiés dans nos mots (« a number that is TRUE OF A SUBSET,
    narrated as true of the whole ») ; `spiralcheck/scripts/mutation_check.py` écrit « this is
    the test of the tests » ; `benchmark_accept.py:162` écrit « comparing a tool to itself is a
    check that cannot fail ». Trois concurrents indépendants tiennent la même discipline.
  - **VERDICT « aucun équivalent » — 27 outils**, dont :
    - la statistique : dans les 35 dépôts, zéro `binomtest`, zéro test de permutation, zéro
      analyse de puissance, zéro `mannwhitneyu` ; les 15 usages de `scipy.stats` sont des noyaux
      gaussiens et une métrique de distance ; `winding-ruler` publie des « +3–5 pp » sans
      importer `scipy.stats` ;
    - le juge automatique en aveugle : aucun appel à une API de modèle dans les 35 dépôts, et le
      protocole de jugement publié est humain et sans condition de contrôle — nulle part une
      image vierge n'est présentée à un juge pour mesurer son taux de fabrication ;
    - le test de convergence (`commun/test_convergence.py`), recherche négative documentée : le
      voisin le plus proche est le balayage de paramètre de `windcheck`, qui mesure le
      détecteur, pas l'objet, et `tifxyz-surgeon/README.md:203` s'en exclut explicitement ;
    - l'étage polaire (1097 l.) : zéro dépliage polaire d'une coupe CT dans le corpus ;
    - douze outils de `src/depot/` : aucune analyse statique d'hygiène, aucun garde contre le
      radotage, aucune comptabilité disque consciente des liens durs.
  - Coût chiffré : 22 fichiers sur 98, dont six scripts shell courts et plusieurs primitives de
    quelques dizaines de lignes ; le gros est concentré sur deux blocs (la campagne d'écart
    entre spires — 13 rouleaux streamés pour un résultat publié sur 36, avec un biais déjà
    corrigé ailleurs — et la moitié « interligne » de `typographie.py`). « De l'ordre de la
    semaine de travail net. »
  - Coût de l'instrument : workflow `audit-outils`, 9 agents, 8 familles, 2,9 M jetons,
    543 appels d'outil, 17 min.
- **rétractations / corrections internes** :
  - §6, « Une correction que je me dois » : l'annonce faite à l'auteur **avant** l'audit selon
    laquelle `windcheck/selfgap.py` portait déjà l'idée du test de convergence n'est **pas
    confirmée** — `selfgap.py` fait varier un rayon de recherche pour caractériser son propre
    détecteur, pas pour lire une propriété de la surface. « Je m'étais accusé plus vite que la
    mesure ne le permettait ».
  - §4.1 : la conclusion de `pyramid.py` (surestimation de 10,3 %) est contredite ; l'outil
    tourne encore au niveau 2 par défaut et propage un biais.
  - §4.2 : `sensibilite_centre.py` repose sur une prémisse fausse (l'ombilic est publié).
  - §1 : le décompte de 22 est explicitement un minorant, deux dépôts n'ayant pas été lus
    intégralement.
  - §2 : le défaut de vocabulaire est le même que celui de `66`, « commis une semaine plus tôt,
    sur le matériau qui le rendait le plus cher ».
- **preuve de lecture intégrale** :
  - ligne 97 (après 60 % du fichier) : `- **la statistique.** Dans les 35 dépôts : zéro `binomtest`, zéro test de permutation, zéro`
  - ligne 128 (dans les 15 dernières lignes non vides) : `**De l'ordre de la semaine de travail net.** Ce n'est pas rien. Ce n'est pas non plus le projet.`

---

### docs/68_lire_le_papier_en_entier.md
- **lignes** : 317
- **nature** : MIXTE (mesures nouvelles — nombre de Fresnel sur 59 scans, 103 cases vides,
  taille de tuile — et reconstitution de méthode / feuille de route)
- **résumé** : Relecture intégrale du papier de référence (Angelotti et al., arXiv 2606.29085,
  46 pages, 27 auteurs) avec une question différente de celle du `27` : non pas « qu'est-ce qui
  est déjà pris » mais « comment le referait-on ». Elle montre que deux conclusions fermées du
  dépôt sont fausses, que les 775 heures humaines tiennent à une seule étape sur dix-sept dont
  l'interface d'intégration est un simple fichier `.tif`, que les trois paramètres de scan
  couplés se ramènent à un nombre de Fresnel, et qu'il existe 103 cases vides du régime du prix
  avec témoin positif publié sur le même segment.
- **conclusions extractibles** :
  - Source : `data/site/scrollprize.org/pdf/main.pdf`, Angelotti *et al.*, « Complete virtual
    unwrapping and reading of a rolled Herculaneum papyrus », arXiv 2606.29085, 27 juin 2026,
    46 pages.
  - Coût humain (p. 28) : « a wrap by wrap copy tool combined with ~25 hours per wrap of manual
    annotation » → 31 spires × 25 h ≈ 775 heures.
  - Le commit épinglé (p. 30) est `github.com/ScrollPrize/villa/commit/e583fb67468f483fadd73d52e06f0ab0fe5ba813` ;
    notre clone en profondeur 1 ne le portait pas, il a été récupéré le 2026-09-02.
  - Le geste qui coûte les 775 heures est un pinceau : `ApprovalMaskBrushTool.cpp` /
    `.hpp` dans `volume-cartographer/apps/VC3D/segmentation/tools/`, avec modes
    `Approve` / `Unapprove`, coups de brosse, pile d'annulation et raccourci clavier.
  - L'interface est ouverte : `QuadSurface::channel(nom)` charge paresseusement
    `<dossier_du_segment>/<nom>.tif`, et le chargeur adopte tout `.tif` du dossier dont le nom
    n'est ni `x`, ni `y`, ni `z` (`core/src/QuadSurface.cpp:1861-1865`). Le masque est lu sous
    le nom `"approval"` et gouverne la ré-optimisation du maillage (`core/src/GrowPatch.cpp`,
    `make_approved_mask`, l. 133). Écrire `approval.tif` à côté de `x.tif`, `y.tif`, `z.tif`
    est l'intégration entière : pas d'API, pas de patch, pas de fork.
  - Sur dix-sept étapes de la méthode publiée, quatre sont humaines, et une seule porte les
    775 heures : l'étape 11 (correction). Tout le reste est déjà automatique et publié.
  - Paramètres publiés relevés : scan BM18 ESRF 2,4 µm / 0,22 m / 78 keV ; phase Paganin
    δ/β = 1000 puis masque flou inverse c = 4,0 ; σ = 1,2 px, écrêtage [10⁻⁶, 10] avant log ;
    alignement par corrélation des recouvrements tous les 5° ; sortie uint8 OME-Zarr 6 niveaux,
    ~20 To par volume ; prédiction de surface nnU-Net 3D résiduel, patchs 256³, 116 531 patchs,
    arrêté à 3 864 epochs sur 7 500 ; rendu 65 échantillons le long de la normale, Δ = 1 voxel,
    offsets −32…+32, soit 153,6 µm à 2,4 µm ; modèle d'encre U-Net à encodeur ResNet3D-50
    (`r3d50_KM_200ep`), entrée 62 × 256 × 256, Dice 0,5 + SoftBCE 0,5 (lissage 0,25), AdamW
    OneCycle 3·10⁻⁴, 1 × H100, ≈ 2 h par run ; pseudo-labels 5 tours,
    3 396 → 8 970 → 15 286 → 24 773 → 33 061 tuiles ; relecture par 8 papyrologues.
  - Le rendu ne fait pas d'isosurface : il empile 65 échantillons le long de la normale.
  - Le maillage n'est pas la sortie du réseau : la prédiction voxel est « used only as an
    intermediate cue » (p. 17), et le Dice de la classe surface vaut 0,308 (Suppl. Table 1,
    p. 41).
  - Le contraste ne vient pas de l'absorption (p. 14 : « the absorption contrast being very low
    for carbon-based material in hard X-rays ») mais des franges de Fresnel ; la largeur de la
    première frange vaut √(λD) et le critère est F = √(λD)/p avec λ = hc/E.
  - Mesuré sur les 59 scans publiés (`nombre_de_fresnel.py`, 13 contrôles), F ordonne les
    verdicts que les auteurs écrivent sous leurs propres panneaux : F 0,245–0,298 (45,5 µm /
    11 m) = repérage grossier ; F 0,388–0,415 (31 scans, dont les 13 rouleaux du prix) = « the
    9.362 µm panel is pixel-limited » (p. 36) ; F 0,733–0,747 (2,4 µm / 0,2 m, production) =
    « the 2.4 µm appears as the best possible resolution on a setup compatible with large
    scrolls » (p. 36) ; F 0,848 (4,317 µm / 1,2 m) = « haze-limited » ; F 0,954 (2,215 µm /
    0,4 m) = supervision fragments ; F 1,816 (1,129 µm / 0,2 m) = « fine delaminations begin to
    blur due to a too long propagation distance for a so small pixel size ».
  - Les 13 rouleaux du prix sont à F = 0,39, soit 53 % du régime de production.
  - F n'explique pas la décohérence : 500P2 à 4,317 µm / 1,2 m (F = 0,85) est « haze-limited » ;
    le même fragment à 2,215 µm / 0,4 m (F = 0,95) ne l'est pas — même F, verdict opposé, et la
    seule chose qui change est D. Le modèle honnête a deux termes.
  - Les 13 rouleaux sont du mauvais côté des deux à la fois : F = 0,39 et D = 1,2 m, distance à
    laquelle le papier mesure l'apparition de la décohérence sur `PHerc0268`, lui-même l'un des
    treize (Ext. Data Fig. 2c, p. 34 : « starts to affect the resolution at 1.2m »).
  - Les deux contraintes sont incompatibles à ce pas : atteindre F = 0,73 à 9,362 µm / 113 keV
    demanderait D = 4,3 m, très au-delà du seuil de décohérence — raison physique jamais écrite
    ainsi dans le papier pour laquelle le domaine est descendu à 2,4 µm.
  - Les 13 rouleaux n'ont pas un mauvais scan, ils ont un scan de repérage optimisé pour le
    débit, à distance unique pour tout le lot.
  - `data/metadata.min.json` publie un champ que rien ici ne lisait : `volume_transforms`, des
    matrices de recalage entre volumes d'un même objet. Dix objets en portent ; six relient le
    régime de repérage (1,2 m) au régime de production (≤ 0,4 m) ; trois de ces six sont
    exactement les trois fragments dont le papier tire toute sa supervision d'encre —
    `PHerc0009B`, `PHerc0343P`, `PHerc0500P2` (Methods p. 20).
  - Cas décisif `PHerc0500P2`, segment `20250628074500-500P2_front` (Ext. Data Fig. 5, p. 38) :
    surface transformée et pile de couches rendues aux trois régimes (2,215 µm / 0,4 m ;
    4,317 µm / 1,2 m ; 9,362 µm / 1,2 m), carte d'encre présente ×2 au premier, absente au
    second, et **vide au régime du prix**.
  - 103 cases vides du régime du prix, toutes avec un témoin positif sur le même segment,
    réparties sur quatre objets : `PHerc0139` 38 (le rouleau dont le papier a lu et publié le
    titre), `PHerc0500P2` 38, `PHerc0814` 19, `PHerc0343P` 8. Les 118 autres cases vides sont du
    repérage grossier à 45,5 µm / 11 m et sont comptées à part.
  - Remplir la case ne demande ni faisceau, ni annotation manuelle, ni rescan : les couches sont
    déjà rendues.
  - La garantie anti-hallucination du papier (p. 20) tient à « moins qu'une lettre » et non à
    « 256 pixels » : la fenêtre de 256 px correspond à environ 614 µm. Or les deux cartes
    d'encre publiées du segment 500P2 portent `tile256-stride128` dans leur nom de fichier, et à
    9,362 µm une tuile de 256 pixels couvre 2 397 µm, soit quatre fois la fenêtre des auteurs.
  - Pour conserver la propriété au pas du prix il faut une tuile d'environ 66 pixels.
  - La validation du papier ne peut pas attraper l'hallucination structurée : Ext. Data Fig. 7
    (p. 40), ligne `c` = segment de validation `ℓ5` « never used for creating labels », décrit
    p. 20 comme « gradually revealed » — un jugement visuel, sans aucune métrique sur la ligne
    `c`. La défense du §5 (fenêtre plus petite qu'une lettre) interdit l'hallucination d'une
    lettre entière, pas qu'une boucle de pseudo-labels amplifie une texture qui n'est pas de
    l'encre.
  - Sondes : les deux batteries d'instruments ont été cassées exprès et échouent — remplacer
    √(λD) par √(λ/D) fait tomber 3 contrôles, oublier le rapport au pixel en fait tomber 5 ;
    présumer l'encre partout où il y a des couches en fait tomber 2, poser le seuil de régime au
    milieu du groupe de production en fait tomber 3.
  - Règle méthodologique tirée : un papier se lit deux fois, avec deux questions différentes —
    « qu'est-ce qui est déjà pris ? » et « comment le referait-on ? ». Les quatre résultats de
    ce document viennent tous de la seconde lecture, et aucun n'était visible depuis la
    première.
- **rétractations / corrections internes** :
  - En-tête et §4 : « Deux conclusions fermées de ce dépôt sont fausses » —
    (a) `HANDOFF.md` : « énergie isolée contre étiquettes ❌ impossible en l'état » ;
    (b) `ou_la_verite_existe.py` : « zéro rouleau mesurable sur cinq ». Les deux étaient vraies
    de ce qu'elles regardaient (l'ancien layout `fragments/` et cinq rouleaux) et sont fausses
    du corpus ESRF publié depuis (`la_case_vide.py`, 8 contrôles).
  - §7 : la ligne « énergie isolée contre étiquettes : impossible » de `HANDOFF.md` est
    **périmée** ; `ou_la_verite_existe.py` doit être relancé sur le corpus ESRF, pas sur les
    cinq rouleaux.
  - §3 : le cadrage « trois paramètres couplés » (site du prix) et le blocage de
    `campagnes_de_scan.py` (« aucune des trois n'est isolée par cette mesure-ci ») sont levés —
    il n'y a pas à les isoler.
  - §8 : le `27` §3, 196 lignes sur ce papier, « l'a lu pour se situer, pas pour refaire » ; il
    n'a jamais ouvert les Supplementary Tables, ni le commit épinglé, ni regardé une figure.
  - §1 et §7 : ne change pas — rien ne dit que nos masques valent un masque humain, on ne l'a
    jamais mesuré contre un masque d'approbation humain et aucun n'est publié à notre
    connaissance.
  - §7 : le coût du régime du prix n'est pas mesuré, il est diagnostiqué — F = 0,39 dit que la
    frange est sous le pixel, il ne dit pas combien de caractères survivent.
  - §5 : à vérifier avant d'en faire un reproche à quiconque — on n'a pas relevé quelle tuile
    les modèles d'encre de la communauté utilisent à 9 µm.
- **preuve de lecture intégrale** :
  - ligne 194 (après 60 % du fichier) : `Ce n'est pas un cas isolé : **103 cases vides du régime du prix**, toutes avec un témoin positif`
  - ligne 314 (dans les 15 dernières lignes non vides) : `**Sondes** : les deux batteries ont été cassées exprès et échouent — remplacer $\sqrt{\lambda D}$`


### docs/72_le_second_papier.md
- **lignes** : 100
- **nature** : PLAN
- **résumé** : Inventaire d'un lot écarté de l'article en cours par `70` §3.1 — non pas parce qu'il ne tient pas, mais parce qu'il relève d'un autre sujet : le premier papier juge une **géométrie**, celui-ci jugerait un **régime d'imagerie**. Le document porte en tête une réserve ajoutée le 2026-09-03 qui vaut pour tout son contenu : c'est une **occasion de publication**, pas un progrès vers le prix, et l'auteur doit l'arbitrer comme tel. Il liste cinq résultats déjà mesurés, nomme la seule mesure qui manque, et énumère trois vérifications à faire avant d'écrire.
- **conclusions extractibles** :
  - Thèse : les treize rouleaux du Grand Prize n'ont pas un mauvais scan, ils ont un **scan de repérage** — et l'expérience qui dirait ce que ça coûte est publiée mais non faite.
  - Les trois paramètres se réduisent à un : $F = \sqrt{\lambda D}/p$ ordonne **les verdicts que les auteurs écrivent sous leurs propres panneaux**, aux deux bouts, calculé sur les **59 scans publiés** sans télécharger un octet (`nombre_de_fresnel.py`, 13 contrôles).
  - **103 cases vides** du régime du prix — couches rendues publiées, sans carte d'encre, avec un témoin positif sur le même segment — dont **38 sur `PHerc0139`**.
  - La garantie anti-hallucination ne se transporte pas : 256 px valent 614 µm à 2,4 µm et **2 397 µm** à 9,362 ; il faudrait **66 px**.
  - La résolution est éliminée **deux fois** et par deux voies indépendantes (`58` par émulation, `63` contre de vraies étiquettes) : ramener un fragment au pas d'entraînement **dégrade** l'AUC.
  - La campagne de scan s'effondre comme facteur : p de 0,0081 à **0,50** en séparant « jamais tracé » de « pas d'encre » (`59`).
  - ⚠⚠ **Corrigé le 2026-09-05** : « une seule mesure » est incomplet — la **scorer** demande un **recalage** entre l'aplatissement des étiquettes (`dl.ash2txt.org`, 27 160 × 14 990) et celui du segment publié (26 440 × 15 060). Mesuré traitable (Dice **0,971**) mais **affine**, pas similitude (3,2 % d'écart d'aspect).
  - Ce qui manque est **une seule mesure** : rendre une carte d'encre depuis la pile **déjà publiée** à 9,362 µm d'un fragment de supervision et la scorer contre les **mêmes étiquettes infrarouges** que le témoin positif à 2,215 µm. Ni faisceau, ni annotation, ni rescan.
  - Trois vérifications avant d'écrire : l'**antériorité** de $F$ (audit sur le concept, pas le nom) ; le contrôle **P1 bis** de `71` (×15,9 exigé contre ×3,8 observé) — ✅ **fait le 2026-09-05**, l'hypothèse tient (densité 2 812–2 857 cellules/cm² sur 24 tirages) ; le **fold du modèle GP** (`66` §3), indécidable depuis les métadonnées mais décidable par la mesure — scorer sur les deux segments, celui où il fait le moins bien est celui qu'il n'a pas vu.
- **rétractations / corrections internes** :
  - Deux résultats annoncés ici (dispersion et Holm, `64` et `65`) sont **partis dans le premier papier** §6.2 et ne sont plus disponibles pour celui-ci — partage assumé : ce sont des résultats de **méthode**, pas d'imagerie.
  - §5 : le document ne dit pas que le papier doit être écrit, ni quand ; il nomme le risque de l'écrire **sans** remplir la case vide — un diagnostic sans coût mesuré, c'est-à-dire ce que le premier papier reproche à la littérature.
- **preuve de lecture intégrale** :
  - ligne 60 (après 65 % du fichier) : `**Ni faisceau, ni annotation manuelle, ni rescan.** Les couches sont rendues.`
  - ligne 100 (dernière ligne non vide) : `papier reproche à la littérature.`

### docs/77_le_predicat_didentite.md
- **lignes** : 741
- **nature** : RESULTAT
  (construction et mesure d'un champ d'enroulement, puis quatre lots qui s'enchaînent : le
  masque d'approbation à cinq bras, le second rouleau qui ne sépare pas, le trou angulaire
  trouvé en regardant, et la surface publiée confrontée à la matière.)
- **résumé** : Construit la **moitié manquante** que [`73`](../73_seconde_passe_ce_que_le_depot_change.md)
  avait nommée. Le dépôt avait la **présence** (α) et le **placement** (`offset`) ;
  l'**identité** — est-ce la même feuille qu'il y a un tour ? — n'existait pas, et c'est là que
  partent les 775 heures de pinceau par rouleau. Le champ d'enroulement, bâti sur les spires
  publiées de [`76`](../76_le_sens_des_indices.md), **compte les feuilles** : avance par tour
  0,00 → 1,10 → 1,96 → 2,85 pour 0, 1, 2, 3 feuilles franchies. Le document est ensuite une
  suite de corrections de lui-même, dont trois majeures : le prédicat ne sépare **pas** sur le
  second rouleau, la cause en est un **trou de matière** trouvé en dessinant, et l'estimateur du
  §10 **enjambait deux feuilles**, gonflant ses chiffres de 25 à 37 %.
- **conclusions extractibles** :
  - ⭐⭐⭐ **La grandeur qui décide est l'avance d'indice sur un tour**, et elle a été corrigée
    **deux fois par la mesure**. L'étendue le long d'une spire ne sépare presque rien (1,44
    contre 2,57) parce qu'**une spire EST un tour de spirale** : exiger un indice constant, c'est
    exiger que le rouleau ne soit pas enroulé. Et l'avance prédite « +1 par tour » vaut **0** —
    la spirale est **absorbée** dans le champ, ce qu'un nombre d'enroulement doit faire.
  - `PHerc0139`, validation **à spire exclue** : vraie spire **−0,005** [−0,170 ; +0,230],
    saut d'une feuille **1,103** [0,753 ; 1,479], de deux **1,962**, de trois **2,851**. Les
    deux populations **ne se recouvrent pas**.
  - ⚠⚠⚠ **Et cette phrase est fausse de `PHerc0172`** (§7, ajouté après avoir fait tourner le
    **même code**) : vraie spire +0,022 [−0,554 ; **+0,634**] contre saut à 1,073 [**−0,067** ;
    1,820]. La **rampe** se reproduit parfaitement (0,02 → 1,07 → 2,00 → 2,98) ; ce qui diffère
    est la **dispersion**. Le prédicat doit être **étalonné par rouleau**, et le code **mesure
    et rapporte sa propre applicabilité** au lieu de la supposer.
  - ⚠⚠ **Une tranche isolée ne suffit JAMAIS**, sur aucun des deux rouleaux — la séparation du
    §2 est celle de la **spire entière**, une médiane sur ~24 tranches. Taille minimale mesurée :
    **2 tranches** sur `PHerc0139`, **aucune** sur `PHerc0172`. C'est la version chiffrée de ce
    que `42` disait qualitativement (« désigner des régions, pas des points »).
  - ⭐⭐⭐ **Validation croisée** : sur 32 sauts fabriqués, **deux** ne montent pas — `w041`→`w042`
    (0,169) et `w045`→`w046` (−0,141) — et ce sont **exactement** les deux défauts de référent
    que `76` avait signalés par une méthode qui ne partage rien avec celle-ci. Le contrôle est
    écrit « les positions qui n'avancent pas sont **exactement** `[41, 45]` », donc il échoue si
    le prédicat en rate une **ou** s'il en invente une.
  - ⭐⭐ **Le champ donne DEUX prédicats et il faut les deux** : le **placement** est la partie
    fractionnaire (0,001 sur une feuille, 0,502 dans l'interstice), l'**identité** est l'avance.
    Une copie translatée d'un demi-pas a une avance **nulle** — elle suit parfaitement une
    feuille qui n'existe pas — donc un masque qui n'aurait que l'identité **approuverait une
    surface posée dans le vide**.
  - ⚠⚠⚠ Le masque d'approbation, cinq bras : spire par son propre champ **98,7 %** (circulaire),
    **quart de pas 92,7 %** (le témoin positif réaliste), spire à spire exclue 53,9 %
    (pathologique par construction), **demi-pas 2,1 %**, saut d'une feuille **0,0 %**.
    **Le quatrième bras est celui sans lequel le contrôle ne peut pas échouer** : approuver une
    spire et refuser un masque vide ou plein se satisfait d'un masque qui approuve tout.
  - ⚠⚠ **Une spire publiée ne peut pas être son propre témoin positif** : avec son champ 100 %
    mais circulaire, sans lui 70 % parce que la retirer la place **exactement au milieu de
    l'intervalle que son retrait vient de créer**.
  - ⚠⚠⚠ Le bug le plus coûteux du lot : retirer du champ la spire qui **borne** la surface jugée
    détruit l'information qui détecte un interstice — **un demi-pas passait de 2,1 % à 37,6 %
    d'approbation**, d'un refus net à une approbation nette, sans qu'aucun nombre n'ait l'air
    faux. La sonde fait tomber **4 contrôles**.
  - ⭐⭐⭐ §8, **un TROU angulaire trouvé en dessinant** (consigne de l'auteur : « la solution
    sera forcément visible visuellement, il faut trouver le bon angle de caméra »). Sur
    `PHerc0172`, un faisceau de spires extérieures se croise entre **330° et 360°**. La
    statistique du §7 ne le voyait pas parce qu'elle comparait la violation **moyenne** (5,2
    contre 5,6 %, indiscernable) là où ce qui diffère est la **concentration** : pire secteur
    ×1,42 contre **×5,18**, et 24,3 % de la violation portée par 6 secteurs sur 72.
  - ⚠⚠ **L'explication d'abord donnée — la couture de la spirale — était fausse**, et deux
    mesures la réfutent : **densité 3 points par cellule contre 286** (donc de la matière
    **absente**, pas mal ordonnée) et **7 spires sur 43 à exactement 0 %** (donc pas un angle
    commun à toutes). ⚠ Laquelle des causes — déchirure, perte, écrasement — **n'est pas
    décidable d'ici**, et le fichier ne tranche pas.
  - ⚠⚠⚠ **La première exclusion était fausse aussi, et le témoin l'a attrapée** : étendre l'arc
    par contiguïté donnait 15 secteurs, dont l'exclusion restaure la séparation — mais écarter
    **autant de secteurs SAINS** la restaure aussi. L'effet mesuré était celui du **filtre de
    couverture**, pas celui du trou. À **six** secteurs la distinction tient, et c'est la seule
    version publiée. Coût : **8 % de la circonférence**.
  - §9, jusqu'où le champ porte : **une feuille**. Au-delà du bord publié, erreur **47 µm**
    (0,31 feuille) à +1, 79 à +2, 125 à +3, 293 à +8. ⚠⚠ **Le champ est un JUGE, pas un
    générateur** — réinjecter la spire prédite ne change rien au chiffre près, parce qu'une
    spire prédite **ne porte aucune information neuve**.
  - ⚠ Une structure angulaire **réelle et inutile** : l'écart inter-feuilles varie de **74 µm**
    avec l'angle (45 % de sa médiane), signature de l'écrasement — et l'exploiter donne **0,33**
    contre 0,31 pour un pas global. Les deux moitiés sont publiées ensemble, parce que la
    première invite à croire qu'on peut s'en servir.
  - §10, ⭐⭐ **la surface publiée n'est pas sur la feuille** : sur le même rouleau, le champ
    prédit à **49 µm** et le référent est lui-même à **27 µm** de la matière — donc une part de
    l'erreur de prédiction est l'erreur du **référent**. Bornes 41 µm (erreurs indépendantes) à
    22 µm (parfaitement corrélées) ; l'indépendance n'étant pas vérifiable, **deux bornes plutôt
    qu'un chiffre**.
  - ⭐⭐⭐ **Trois rouleaux, et le fait n'apparaît qu'en unités de FEUILLE** : 17,8–20,1 µm
    (`PHerc0172`), 13,8–16,5 (`PHerc1447`), 23,8 (`PHercParis4`) — qui se contredisent en
    micromètres et disent la même chose en feuilles, **0,121 – 0,146**. Le contrôle qui
    comparait les micromètres a dûment échoué, ce qui est ce qui l'a fait changer.
  - ⭐⭐ Un TIFF de 30 Go lu **sans le télécharger** : les couches de Scroll 1 sont des TIFF non
    compressés à une bande, donc une fenêtre de lignes est une **plage contiguë** — **1,35 Gio**
    par requête `Range` au lieu de 30 Go. ⚠ Le coût est **annoncé avant d'être payé**
    (`--estimer`).
  - §11, **α ne se calcule PAS sur un volume de surface**, et B2 reste ouverte pour une raison
    mesurée : α demande deux fenêtres emboîtées et une dalle fait **±0,9 écart** — 25 refus sur
    36, et les 11 cas mesurables rendent +0,000 à +1,771 sur des positions voisines. Avec une
    dalle de 3,0 écarts, deux obstacles **différents** : centrer sur le lobe est **circulaire**
    (l'argmax d'une fenêtre centrée sur l'argmax est au centre), et transporter la profondeur
    d'une fenêtre à l'autre est **confondu par le serpentage** (0,13 écart ≈ 2,8 couches, l'ordre
    de la fenêtre étroite).
  - ⚠⚠⚠ **§10 bis CORRIGÉ le 2026-09-05, la prémisse était fausse** : `PHercParis4` ne
    publie pas « deux volumes à 7,91 µm » mais **cinq**, dont **aucun à 7,91** — ce
    chiffre est le voxel de `PHerc0172`, emprunté, et `la_surface_et_la_feuille.py`
    posait `2.4: "PHercParis4"` dans sa propre table. ⭐⭐ La provenance se reconstruit
    par une contrainte **dure** : la boîte d'un `tifxyz` est en voxels du niveau 0, donc
    un volume dont la grille ne peut pas la contenir n'est pas le sien — **un seul** des
    cinq contient `z = 73 635`, et il est à **2,400 µm**, la constante posée. La
    correction de budget passe de transportable-en-feuilles à **calculable en
    micromètres** (69,2 → 66,4 µm).
- **rétractations / corrections internes** :
  - §12, ⚠⚠⚠ **l'estimateur du §10 enjambait deux feuilles** : le centre de masse pris sur toute
    la dalle atterrit **dans le creux entre deux lobes**, et 9 des 12 piles en contiennent deux à
    quatre. Borner à ±0,5 écart — la plus grande fenêtre qui ne peut pas contenir deux feuilles,
    donc **pas un réglage** — corrige de **−27 à −37 %**. ⭐ Et `PHercParis4` n'était pas un
    rouleau à part : son 37,7 µm aberrant était l'estimateur enjambant deux feuilles de plus.
  - §12 : **un contrôle a changé de sens et ça RENFORCE le résultat**. Il assertait que l'écart
    décroît avec l'agrégation, donc qu'une part était du bruit de pixel ; une fois l'estimateur
    borné il ne décroît plus (19,2 au pixel contre 19,9 à 20 px). **Ce qui décroissait était le
    biais d'enjambement.**
  - §10 : « j'ai comparé deux rouleaux différents sans que rien ne le signale » — 47 µm de
    `PHerc0139` contre 28 µm de `PHerc0172`, deux tailles de voxel. Le contrôle qui l'aurait
    attrapé **n'existait pas** ; il existe, et la sonde qui rejoue l'erreur le fait tomber.
  - §10 : le gain de l'estimateur avait été attribué à un **lissage 9 × 9** ; mesuré séparément,
    le lissage ne fait rien à l'argmax et rend le centre de masse **légèrement pire**. Tout le
    gain vient du **centre de masse**. ⭐ « Je ne savais pas laquelle des deux choses faisait le
    travail et j'avais publié la mauvaise. La sonde qui ne mordait pas était le signal. »
  - §9 : le modèle de pas a été **choisi par la mesure contre le raisonnement de l'auteur** — un
    pas par cellule est le **pire partout** (0,37 contre 0,31). « L'argument était juste sur la
    physique et faux sur la statistique. »
  - §11 : ⚠⚠⚠ « j'ai d'abord lu un résultat là où il n'y en avait pas » — l'amplitude était
    passée **sans son seuil**, donc la branche de refus de `49` §2 était **inatteignable** et les
    trois positions rendaient des chiffres identiques au millième, pris pour une réponse.
  - §4 : une sonde ne mordait pas parce que le seuil était trop lâche (`erreur < 0,5` acceptait
    0,0876 **et** 0,0000) — or **0,0000 est la signature d'un champ qui a LU la spire** au lieu
    de l'interpoler. Contrôle « … et elle n'est pas nulle » ajouté.
  - §10 bis : ⚠⚠⚠ les micromètres de `44` **ne se composent pas** — sa constante `UM_PAR_VOXEL
    = 2.4` n'est reliée à aucun volume alors que les deux volumes du rouleau nommé sont à
    7,91 µm. Le code le **dit** (`provenance_du_voxel_reconstructible: false`) au lieu de
    composer avec.
- **preuve de lecture intégrale** :
  - ligne 431 (après 61 % du fichier) : `L'argument était juste sur la **physique** et faux sur la **statistique** : un pas estimé sur`
  - ligne 740 (dernière ligne non vide) : `traceur pourrait corriger, et exactement ce que du bruit ne serait pas.`


### docs/78_lombilic_publie.md
- **lignes** : 177
- **nature** : RESULTAT
- **résumé** : Écrit en cherchant de quoi construire `A2 bis`, ce document corrige d'abord une affirmation du dépôt — « Scroll 1 est le seul rouleau qui publie un ombilic » — en montrant que **cinq** en publient un sur le bucket ouvert, et que l'erreur est le même angle mort que `59`, commis pour la troisième fois. Il se sert ensuite de l'axe publié de `PHerc0139` (391 points annotés à la main) comme référence **indépendante** pour tester la robustesse de `76` et `77` : le biais de l'axe ajusté est grand, et la mesure appariée n'en bouge pas. Il finit sur un résultat **négatif** qui fixe le cahier des charges d'`A2 bis` : l'axe seul ne débloque rien.
- **conclusions extractibles** :
  - §2, **corrigé le 2026-09-05** : le renvoi vers `representations/predictions/fibers/` annonçait `nx`/`ny`/**`nz`** — **il n'y a pas de `nz`**. Trois canaux publiés (`nx`, `ny`, `presence`), manifeste `.lasagna.json` sans autre groupe, alors qu'`inference.json` déclare `fiber3d-prediction` et `output_channels = 7`. ⭐⭐ Ce n'est pourtant **pas** le champ 2D de `26` §7 : mesuré sur trois fenêtres, $n_x^2+n_y^2$ vaut **0,797 / 0,806 / 0,309** en médiane (max 1,013–1,014, soit l'arrondi sur huit bits, donc l'encodage est confirmé), donc $\lvert n_z\rvert$ est récupérable — **0,451 / 0,441 / 0,831** — et seul le **signe** est perdu. ⚠⚠ Ce qui borne `A2 bis` est la **résolution** : le niveau 0 n'est pas publié, les seuls présents sont 3 et 4 (**19,2** et 38,4 µm/cellule), donc un pas de feuille tient en **7,8** cellules au plus fin — assez pour voir une feuille, pas pour en séparer deux.
  - **Cinq** rouleaux publient un ombilic sous `<rouleau>/representations/umbilicus/` — `PHerc0125` (83 points, 9,362 µm), **`PHerc0139` (391 points, 2,399 µm, David Josey)**, `PHerc0211` (87), `PHerc0332` (169, 2,399 µm, David Josey), `PHerc0826` (49). Balayage sur les **46 préfixes de premier niveau**, pas sur une liste écrite à la main.
  - Le biais de l'axe ajusté par cercles sur arcs partiels est **réel et grand** : médiane **3,01 mm**, jusqu'à **27 écarts inter-feuilles**. Les deux axes ont même forme et même sens mais ne se superposent pas.
  - **Et la mesure appariée n'en bouge pas** : vers l'extérieur **94,8 %** des deux côtés, écart inter-feuilles **155,8 µm** (axe ajusté) contre **156,8** (axe publié). Un axe faux de 4 mm déplace le verdict de zéro point et l'écart d'un micromètre.
  - ⭐ Une sonde **localise** l'immunité : un centre **global** au lieu d'un centre par tranche ne change rien non plus (94,6 % contre 94,5 %). L'immunité ne vient donc pas de la qualité du centre mais du fait que les deux spires sont comparées **dans la même cellule angulaire autour du même centre, quel qu'il soit**.
  - `laxe_ne_suffit_pas.py` : erreur d'indice de **44,5 feuilles** pour la dispersion radiale d'une seule spire autour de l'axe publié, **11,36** pour le modèle d'Archimède ($w = (r-r_0)/\lambda + \theta/2\pi$), **0,088** pour le champ bâti sur les spires de `77`. La **forme** des spires vaut donc un facteur **130**.
  - La cause est mesurée : un rouleau d'Herculanum est **écrasé**, donc aucun modèle en $(r, \theta)$ à section circulaire ne sépare des feuilles distantes d'une seule.
  - ⚠ Les `.normal-grids` publiées sont **dérivées de la prédiction de surface** que le traceur suit déjà (`26` §7) : les lui redonner est une tautologie mesurée (×29 de ralentissement, trajectoire identique au centième). Ce qui reste ouvert pour `A2 bis` est un champ bâti sur l'axe **et l'orientation des fibres** (`representations/predictions/fibers/`, publié en `nx`/`ny`/`nz`).
- **rétractations / corrections internes** :
  - §0 : `laxe_nest_pas_une_ligne.py` affirmait que Scroll 1 était le **seul** à publier un ombilic. La vérification était juste et sa conclusion fausse — elle portait sur **un** serveur et **une** convention de chemin. La correction est écrite dans le fichier fautif, pas seulement ici. ⚠ Le mot faux était « seul », pas la mesure : les deux serveurs se complètent.
  - §3 : le document n'établit **pas** que l'axe publié soit juste et l'ajusté faux — seulement qu'ils diffèrent et que la conclusion n'en dépend pas ; **pas** que les cinq axes soient de même qualité (49 à 391 points, deux annotateurs nommés) ; **pas** que la conversion de repère soit exacte (facteur d'échelle lu dans le champ `volume` et validé contre les résolutions publiées — mélanger 2,399 et 9,362 µm sans conversion donnerait un axe faux d'un facteur 3,9).
  - §4 : les **44,5 feuilles** sont prises autour de l'axe **publié** ; autour du centre **ajusté par tranche** la dispersion vaut ~17 feuilles. Ce n'est pas une contradiction — l'ajustement minimise cette dispersion par construction.
- **preuve de lecture intégrale** :
  - ligne 128 (après 68 % du fichier) : `jugement **indépendant** du nôtre, ce qu'il fallait pour tester une robustesse.`
  - ligne 177 (dernière ligne non vide) : `axes restent équivalents pour la mesure **appariée** du §1, qui ne lit jamais un rayon absolu.`

### docs/79_aucun_seuil_ne_separe_les_feuilles.md
- **lignes** : 147
- **nature** : RESULTAT
  (balayage de seuil sur deux chunks à pleine résolution, avec une attente dérivée de la
  géométrie, plus la réfutation d'un profil radial mesuré au niveau 5.)
- **résumé** : Établit dans l'arbre ce que [`00`](../00_etat_de_lart.md) §10.3 affirmait en
  renvoyant à un fichier **gitignoré** : aucun seuil d'intensité ne sépare les feuilles. Sur
  `PHerc0172` à 7,910 µm, au centre et au bord, à six seuils de 100 à 144, le plus gros morceau
  connexe tient **93,2 à 100 %** de la matière — là où des feuilles séparées en mettraient
  **14,1 %**. Le document tire en passant une seconde conclusion, contre lui-même : le profil
  radial spectaculaire du niveau 5 (écart-type qui **quintuple** vers l'extérieur) **ne survit
  pas** à la pleine résolution, où l'écart-type *diminue* — il mesurait la taille du voxel, pas
  la compaction du rouleau.
- **conclusions extractibles** :
  - ⭐⭐⭐ **L'attente est DÉRIVÉE, pas choisie** : un chunk de 128 voxels de 7,910 µm traverse
    $n = 128 \times 7{,}910 / 142{,}8 = 7{,}09$ feuilles, donc des feuilles séparées mettraient
    $1/n = 14{,}1$ % dans le plus gros morceau. Juger un seuil par un autre seuil choisi à la
    main ne dirait rien ; un écart de **facteur sept** n'est rattrapé par aucun réglage.
    ⚠ Le pas de 142,8 µm est celui de **ce rouleau-là** (`table_champ_0172.json`), pas emprunté.
  - Balayage, centre (rayon 0,5 mm) puis bord (19,7 mm) : à 100/110/120/128 le plus gros morceau
    tient **100,0 %** des deux côtés ; à 136, **99,3** et **99,1 %** (13 et 12 morceaux) ; à 144,
    **97,3** et **93,2 %** (48 et 78 morceaux). Matière restante à 144 : **49,6** et **41,7 %**.
  - ⚠ La part de matière est publiée **à côté** du poids du plus gros parce que sans elle on
    croirait que les seuils hauts fabriquent des morceaux en vidant le volume. Les 48 et 78
    morceaux de 144 sont du poivre au bord des lamelles, pas des feuilles.
  - ⚠⚠ La connexité est à **6 voisins** : en 26-connexité deux feuilles qui se frôlent par un
    coin fondraient en une, et le contrôle deviendrait **incapable d'échouer** — tout empilement
    serait un seul morceau quelle que soit la donnée.
  - Ce que ça interdit : **une isosurface affirmerait une frontière que le scan n'a jamais
    résolue**. Une surface maillée sur un seuil ne suit pas une feuille, elle suit le bord d'une
    motte. C'est une contrainte sur la **méthode**, pas sur ce rouleau.
  - Coût de maillage mesuré, pas majoré : **0,32 à 0,79 face par voxel**, jusqu'à **1,0 M de
    faces** par chunk de 128³ — le compte réel des interfaces plein/vide, bords compris.
  - ⚠⚠⚠ **Le profil radial du niveau 5 est un artefact du niveau 5.** Écart-type 6,1 à
    r = 40–50 contre **31,9** à r = 100–110 (voxels de 253,1 µm) ; à pleine résolution,
    **25,1** au centre contre **19,1** à 23,7 mm. Deux causes connues : un voxel de 253 µm
    moyenne feuilles et interstices d'un pas de 142,8 µm, et près du bord il mélange rouleau et
    vide du masque. La sonde a servi **en se démentant elle-même**, ce que son propre en-tête
    réclamait.
  - Ce que le niveau 5 dit et qui tient : **97,4 %** des 21,3 M de voxels non nuls du rouleau
    entier tombent entre 128 et 176, moyenne 147,2, écart-type 16,9 — une plage dynamique
    étroite, cohérente avec le fait qu'aucun seuil ne tranche. ⚠ 3 chunks sur 36 sont **absents
    du bucket**, comptés et non silencieux.
  - Déduplication au passage : `composantes` et `faces` étaient écrites **deux fois**
    (`sonde_maillage.py`, `sonde_exterieur.py`) et les copies avaient **déjà divergé** — arité
    différente et garde du cas vide dans une seule. Une définition, testée
    (`src/rendu/topologie_du_volume.py`) ; les deux sondes rendent **exactement** la même sortie
    qu'avant, ce qui est le contrôle du refactor.
- **rétractations / corrections internes** :
  - §7 : le document borne lui-même sa portée — **deux régions d'un rouleau**, pas treize ; et
    **une seule résolution** (à 2,4 µm le pas ferait 60 voxels au lieu de 18, et rien ici ne dit
    ce qu'un seuil y ferait).
  - §7 : la « bimodalité » que `sonde_exterieur.py` rapporte (2 pics au centre, 1 au-delà) sort
    d'un détecteur de pics grossier sur histogramme lissé ; elle **n'est pas reprise** comme
    résultat.
  - §7 : « aucun seuil ne sépare » ne veut pas dire « le scan est mauvais » — la prédiction de
    surface publiée porte une planarité de **0,993** au même genre d'endroit (`39`).
- **preuve de lecture intégrale** :
  - ligne 93 (après 63 % du fichier) : `l'écart-type vaut **25,1** au centre et **19,1** à 23,7 mm — il *diminue* légèrement vers`
  - ligne 147 (dernière ligne non vide) : `résultat ; le balayage de seuil, lui, ne dépend d'aucun réglage de ce genre.`


### docs/71_les_trois_resultats_de_tete_audites.md
- **lignes** : 108
- **nature** : AUDIT
- **résumé** : `70` §5 nommait la seule tâche à faire avant tout envoi — trois des quatre résultats de tête de l'article n'avaient jamais été audités pour antériorité, et aucune des 14 clés de `66` ne les couvrait. Trois agents adversariaux, un par résultat, cadrés pour **réfuter** ; rapports intégraux dans `registres/anteriorite_resultats_de_tete.md`. **Les trois rendent partiellement** : aucun n'est un doublon, aucun n'est intact. Le document corrige l'article section par section et finit sur ce qui reste ouvert.
- **conclusions extractibles** :
  - §5.1 « le traceur est un tirage » : le mécanisme est **dans le code publié, littéralement** (`vc_grow_seg_from_seed.cpp:357 srand(clock())`, `GrowPatch.cpp:99-108 std::mt19937(std::random_device{}())`) et l'article ne le nommait pas. ⚠ Sa phrase « draws from an **unseeded** generator » était attaquable : `VC_GROWPATCH_RNG_SEED` existe, donc le comportement est connu de ses auteurs — corrigé en « unseeded *by default* ».
  - ⭐⭐ Et l'audit a trouvé un argument à **récupérer** : la doc officielle publie que le vérificateur est déterministe (*« Two runs on the same surface produce identical reports regardless of thread count »*), et `windcheck` le remesure sur neuf configurations. Donc **une bascule de verdict ne peut pas venir de l'instrument** — c'est une garantie de l'amont qui renforce l'observable.
  - Ce qui reste sans équivalent en §5.1 : la mesure (78 exécutions, 0/13 rendant deux fois la même aire, 5/13 basculant, **5/78 = 6,4 %**) ; la **bascule de verdict** comme observable ; et le fait que l'aire ne signale pas le mauvais tirage.
  - ⚠⚠ §5.2 : la moitié « propreté » est **déjà publiée, quantifiée, sur 278 traces**, presque mot pour mot (`windcheck/docs/FULL-CORPUS.md` : *« a small trace is clean substantially because it is small […] the 86% figure […] is not a property of those samples »*). Corrigé en **confirmation intra-instance** d'une loi publiée ; ce que le dessin ajoute est le **sens de l'inférence** — leur loi est transversale sur des tailles réalisées, la nôtre change le budget sur le même rouleau.
  - ⭐ La moitié « stabilité » ne trouve **rien**, pour une raison structurelle : **personne ne tire le traceur plusieurs fois à configuration identique pour en mesurer l'étalement.** C'est le cœur défendable de la section.
  - §5.7 : **trois composants sur quatre sont antérieurs** — le tutoriel officiel porte la prémisse (*« you end up with a big pile of small pieces […] gluing the pieces together directly is hard »*) et `QuadSurface::overlap()` porte le discriminant (boîte englobante puis **distance point-à-surface de deux voxels**). Ce qui survit est le **recensement** : les antérieurs mesurent 6 paires, 150 paires échantillonnées, 9 fenêtres — personne n'a fait **les 105 paires d'un rouleau**, et `PHerc1447` n'apparaît pas dans le papier de référence.
  - La formulation « **une pièce par feuille** » est absente du corpus, qui dit « sparse », « scattered », « pieces with gaps » — la nôtre est plus forte et plus falsifiable.
  - **Verdict global, à ajouter aux 14 de `66`** : 17 résultats audités, **6 déjà connus, 11 partiellement**, aucun intact et aucun sans valeur. Le motif tient : *le domaine publie les mécanismes et les questions ; ce qui résiste est la mesure, sa répétition, et son incertitude.*
- **rétractations / corrections internes** :
  - §4 : la **contre-position du rapport « pavage »** — la doc de `volume-cartographer` affirmerait qu'aucun seuil de distance fixe ne sépare les feuilles, ce qui viserait notre seuil de 40 µm. ⚠ **La citation n'a pas été retrouvée à la source**, donc elle n'est pas reprise dans l'article : *une antériorité qu'on ne peut pas citer ne se cite pas.*
  - §4 : le **contrôle P1 bis** (×15,9 exigé contre ×3,8 observé) était laissé « à faire tourner sur nos propres grilles ». ✅ **Fait le 2026-09-05** (`src/tracecheck/modele_de_proprete.py`, `75` §D2) : la densité vaut **2 812 à 2 857 cellules par cm²** sur 24 tirages, donc cellules ∝ aire, et l'hypothèse tient.
  - ⚠ Le document note que les citations portant une correction de l'article ont été **revérifiées à la source ligne par ligne** — « la discipline qui a payé cinq fois cette session ».
- **preuve de lecture intégrale** :
  - ligne 75 (après 69 % du fichier) : `> physically overlap or touch** »*.`
  - ligne 108 (dernière ligne non vide) : `résiste est la mesure, sa répétition, et son incertitude.**`

### docs/69_reponse_dun_chercheur_exterieur.md
- **lignes** : 646
- **nature** : REVUE
  (réponse à un prompt « chercheur senior » : hypothèses falsifiables, mathématiques,
  algorithmes décrits pour être implémentés, emprunts hors domaine avec références réelles.
  ⚠ Aucun code, aucune mesure neuve — le document le dit lui-même.)
- **résumé** : Diagnostique que **le goulot n'est pas la détection d'encre mais le pinceau
  d'approbation**, et le chiffre : à la cadence du papier (25 h par spire), les treize rouleaux
  du prix demandent **1 500 à 8 060 heures chacun**, soit deux à quatre années-personne pour
  le seul masque. Corrige deux fois le cadrage du prompt sur la physique — les franges de
  Fresnel ne sont pas ce qu'on regarde (Paganin les supprime), et 9,362 µm est un **choix
  d'export** (`binmean2` d'une acquisition à 4,681 µm), pas une limite du détecteur. Pose sept
  hypothèses avec leur mesure et ce qu'elle discrimine, puis sept algorithmes, et sa
  contribution structurelle est de reformuler le rouleau comme un **champ de phase à vortex**
  dont les défauts sont des **résidus** — ce qui rend le problème identique à un dépliage InSAR,
  exact et polynomial.
- **conclusions extractibles** :
  - ⭐⭐⭐ **Le goulot est géométrique et dix fois plus large que dans le papier** : 775 h pour
    31 spires sur 8 cm, contre 60 à 129 spires sur 19 à 24 cm pour les rouleaux du prix.
    PHerc0826 **1 500 h** à 8 cm / **3 750** à 20 cm ; PHerc0268 **3 225** / **8 060**. « Le prix
    n'est pas gagné en améliorant la détection d'encre : il est gagné ou perdu sur **ce qui
    remplace le pinceau**. » Les pièces amont sont publiées pour les treize.
  - ⚠⚠ **$F$ ne mesure pas ce que le prompt croit.** Tous les volumes publiés sont reconstruits
    après Paganin à δ/β = 1000, qui **supprime** les franges. Ce que $F$ ordonne est
    $L_P/p$ — combien de pixels fait le noyau de récupération de phase : **3,5 px** au régime du
    prix contre **7,0** en production. Les deux verdicts du papier (*pixel-limited* contre
    sur-échantillonné) sont ceux-là.
  - ⭐⭐ **« 53 % du régime de production » se lit comme une dégradation uniforme et ce n'en est
    pas une.** Le gain de contraste de phase vaut $2\pi\lambda D f^2$, donc il est **3,8 fois
    plus élevé** au régime du prix à toute fréquence que la grille résout. Ce qui est perdu est
    **une bande** — les périodes de 4,8 à 19 µm — plus un flou ∝ D. **Un passe-bas, pas une
    atténuation.** Si l'encre vit dans un dépôt lisse de dizaines de µm, le régime du prix la
    porte **mieux** que la production.
  - **9,362 µm est un export** : `binmean2` d'une acquisition à 4,681 µm, et le papier dit que
    toutes les reconstructions ont des versions binées ×2 et ×4. Sur le même fragment 500P2 le
    papier rend **deux verdicts pour un même bras de 1,2 m** (4,317 µm *haze-limited*, 9,362 µm
    *pixel-limited*), donc la résolution physique y est bornée par la **décohérence** entre 4,3
    et 9,4 µm. Prédiction : le débinage rendrait **au plus 1,3–1,5×**.
  - ⭐⭐⭐ **Le rouleau comme champ de phase** (§3.2) : $\psi$ vaut $2\pi k$ sur la $k$-ième
    spire, l'ensemble $\{\psi \in 2\pi\mathbb{Z}\}$ est **une seule surface connexe**, et
    $\psi$ a un **vortex** sur l'ombilic. Le recto est le bord $\psi$-décroissant : **son
    identification est gratuite**. Ce que le spiral fitting n'a pas : un difféomorphisme **ne
    peut pas représenter une terminaison de feuille**, donc il « erre » là où la vérité a un
    défaut ; le champ de phase le **représente** comme un résidu et une coupure.
  - Les **résidus** (Goldstein 1988) sont les charges topologiques ±2π du champ d'orientation
    mesuré ; les coupures de branche de coût minimal sont un **flot à coût minimal sur le graphe
    dual** (Costantini 1998), **exact et polynomial**, implémenté publiquement par SNAPHU.
  - ⭐⭐ **Les spires comme $K$ surfaces couplées** (§3.3, Li *et al.* 2006) : une **seule coupe
    minimale** globalement optimale, où le prior de pas mesuré (160–210 µm, soit 17–22 voxels)
    **est** la contrainte de séparation. Ce que ça règle : les pertes L1 de Henderson convergent
    vers la **médiane** quand deux spires se contredisent, d'où l'errance — une coupe est
    **discrète**, elle choisit. ⚠ Elle vient **après** le champ de phase, dans une bande étroite,
    parce qu'un pli où la feuille n'est pas univoque en $\rho$ la fait échouer.
  - ⭐⭐ **Détection d'encre comme test statistique** (§3.4) : la nulle empirique est le **verso**
    (H7), les valeurs p passent par Benjamini–Hochberg, et une carte d'encre rend alors **le
    nombre attendu de fausses lettres**. C'est le *look-elsewhere effect* que l'audit `66` note
    absent de tout le domaine — « une tuile plus petite qu'une lettre borne ce qu'un modèle peut
    **inventer**, pas combien de fois il se trompe ».
  - ⭐ Et pour « des colonnes visibles partout » : le **repliement d'époque** (Leahy 1983) sur la
    périodicité de l'interligne gagne $\sqrt{n}$ — une colonne de 30 lignes gagne **×5,5** — donc
    on détecte **qu'il y a du texte et où sont les lignes** bien avant de lire une lettre. ⚠ Le
    test ne rend pas de lettre, il rend la **grille**.
  - Les sept hypothèses, chacune avec ce qui la falsifie : **H1** l'AUC survit à la bande perdue
    (plate jusqu'à 20 µm) ; **H2** le débinage ne rend presque rien (< 0,03 d'AUC) ; **H3** la
    décohérence est un flou local en $D/E^\alpha$ ⚠ dont **six points ne fixent pas
    l'exposant** ($\alpha = 1$ classe aussi bien que 2) ; **H4** le coût humain suit les
    **régions ambiguës** et non l'aire (< 10 % de la surface) ; **H5** les résidus prédisent les
    sauts de spire (AUC > 0,8, **sans vérité terrain**) ; **H6** le prior d'enroulement est
    universel ; **H7** le verso est le témoin nul du recto (AUC ≈ 0,5).
  - ⚠ **Le sens de l'erreur est choisi**, deux fois : le masque automatique doit
    **sous-approuver** (« mieux vaut laisser au pinceau que figer une erreur »), et si H7 est
    fausse le test devient **conservateur** — « il manque des lettres, il n'en invente pas ».
  - ⚠ **Analogies rejetées après réflexion**, pour qu'on ne les repropose pas : les *contact
    maps* Hi-C (pas de géométrie d'enroulement régulière), la théorie des nœuds (le rouleau
    n'est pas noué, sa topologie est celle d'un disque), la cristallographie au-delà du §3.5.
  - **Données manquantes par ordre de valeur** : (1) les volumes non binés à 4,3–4,7 µm des
    treize, **qui existent** à l'ESRF ; (2) la paire 0,6 m / 1,2 m de PHerc0268 ; (3) les masques
    d'approbation humains de 1667 ; (4) l'exposition et le nombre de projections (pour
    $\sigma_I$) ; (5) les étiquettes d'entraînement de `surface-m7`.
- **rétractations / corrections internes** :
  - §7 déclare six doutes, dont trois qui portent sur ses propres piliers : le modèle du §3.1
    **suppose un objet de phase faible et δ/β homogène**, ce qu'un rouleau de 5 cm n'est ni l'un
    ni l'autre ; les **résidus pourraient mesurer la qualité de `m7`** et non la topologie du
    rouleau — « sans le contrôle de co-localisation, A2 est un détecteur de bruit avec un beau
    nom » ; et la coupe à $K$ surfaces **suppose un ordre en $\rho$** qui n'existe peut-être pas
    là où le papier dépense ses 25 h.
  - ⚠ « Tout le raisonnement en SNR est suspendu à $\sigma_I$ » — la dose par voxel des scans du
    prix n'est pas connue, et **une seule mesure de bruit sur une fenêtre vierge par régime
    tranche**.
  - ⚠ Le voisin conceptuel non lu est nommé : l'assignation de « winding angle » de
    ThaumatoAnakalyptor. « Si elle est déjà un dépliage avec résidus sous un autre nom, la
    contribution du §3.2 se réduit à l'exactitude du flot. La règle du `66` s'applique à moi :
    chercher le concept, jamais le nom. »
  - ⚠⚠ Sa recommandation de rouleau (**PHerc0826**, le moins de spires) est **renversée par**
    [`73`](../73_seconde_passe_ce_que_le_depot_change.md) §1 H6 : par la carte dense c'est le
    **pire des treize** (22,8 % de fenêtres indissociables contre 2,6 % pour `PHerc0800`).
    Le document avait posé la réserve — « peu de spires peut vouloir dire un *midollo* abîmé,
    c'est H6 qui départage » — et H6 a départagé contre lui.
  - ⚠⚠ Son §1.2 (« le débinage ne rend presque rien ») est le paragraphe que `73` §1 H2 a d'abord
    contredit puis **rétabli** : `73` a sur-affirmé l'inverse avant de constater que `69`
    portait déjà le contre-argument, marqué `[établi]`.
- **preuve de lecture intégrale** :
  - ligne 403 (après 62 % du fichier) : `Une colonne de 30 lignes gagne un facteur ~5,5 sur une ligne seule : on détecte **qu'il y a du`
  - ligne 646 (dernière ligne non vide) : `reproduites en clair ci-dessus pour qu'un instrument du dépôt puisse les reprendre.*`


### docs/70_ce_que_larticle_condense.md
- **lignes** : 183
- **nature** : AUDIT
- **résumé** : Réponse mesurée à une question de l'auteur — *« j'aimerais que l'article soit l'extrait de tout ce qu'on a appris ; est-ce le cas ? »* — posée après avoir constaté que la vérification précédente n'avait lu que les premières lignes de chaque document. **Non** : environ 21 documents sur 48 porteurs de résultat ont leur conclusion dans l'article. Le reste se répartit en trois familles dont **une seule** est un vrai manque. Le document croise document par document, ouvre chaque correspondance en contexte, et finit par une recommandation courte de ce qu'il faut faire avant tout envoi.
- **conclusions extractibles** :
  - Compte : **22** documents de **procédé** (plan, inventaire, registre, texte de soumission), **21** de résultat **dans** l'article, **27** de résultat **hors** de l'article. ⚠ La frontière procédé/résultat est un jugement et plusieurs documents sont mixtes — c'est un ordre de grandeur, pas une constante.
  - ⭐ « 68 documents → 27 pages » n'est **pas** la bonne comparaison : un tiers du corpus est le procédé, qu'aucun article ne contient. Ce qui se compare est l'ensemble des **résultats**, et là il en manque plus qu'il n'y en a.
  - **Méthode** : les 70 documents lus **intégralement** (23 389 lignes) par dix agents, chacun devant rendre nature, résumé, conclusions falsifiables, rétractations, et **deux citations verbatim numérotées** — une après 60 % du fichier, une dans les quinze dernières lignes. **140 citations, 140 retrouvées à leur ligne, 0 introuvable.**
  - ⚠⚠ Ce compte a d'abord été publié à **88** : la garde ne reconnaissait qu'une des trois écritures de numéro de ligne et **sautait 44 citations en silence**. Elle compte désormais les lignes de preuve qu'elle ne sait pas lire, et échoue dessus.
  - ⚠ **Le croisement ne se fait pas par les chiffres** : essayé, il rend « partiel » pour les 70 documents et ne discrimine rien, et il fabrique des faux positifs — `0,030` matchant la couleur CSS `#b03030`, `105` matchant « 105 paires de segments », `14,3` matchant une borne d'intervalle. Chaque correspondance a donc été **ouverte et lue en contexte**.
  - **Famille 1, hors périmètre (5 documents)** : `08`, `10`, `58`, `59`, `68` §3–4 — tous côté encre et régime de scan. L'article s'appelle *« Measuring segmentation quality »* ; y verser l'encre le rendrait incohérent. **Ils ne manquent pas, ils attendent leur propre papier.**
  - **Famille 2, résultats négatifs (5 documents)** : `17` (la phase d'enroulement publiée ne détecte pas un saut de spire — ρ **+0,517 (n=8) → +0,306 (n=30) → +0,149 (n=38)**, p = 0,37, l'effet fond quand l'échantillon grandit) ; `26` (`direction_fields` et `normal_grid_path` **ne déplacent pas** la trajectoire d'un centième, même à ×100 et avec 1,53 Go de vraies grilles coûtant ×29 en temps) ; `36` (notre chaîne ne décale pas l'origine de la pile : accord à **14,3 µm**, et elle place mieux sa pile — 100 % de pics dans le tiers central contre 62,5 %) ; `37` (« sélectionner sur un axe, valider sur l'autre » : **1 accord sur 8** là où le hasard en donnerait 4) ; `62` (falaise de cache L3 réfutée par sa propre mesure, d'un facteur **×2142**).
  - **Famille 3, le seul vrai manque (17 documents)** : l'**arc excision/réparation** (`03`, `04`, `05`, `07`) — le mot « excision » apparaît **zéro fois** dans l'article ; `33` (le classement des treize rouleaux de `16` **annulé par sa propre incertitude**, aucune des 78 paires séparée après Holm — c'est la thèse de l'article sur son propre corpus) ; `34` (mode de panne **silencieux** de `vc_tifxyz_selfcross` : « propre » et « rien mesuré » sortent par le même champ JSON) ; `54`, `53`, `42`, `41`, `16`, `43`, `11`, `12`, `14`, `20`, `24`, `55`.
  - **Recommandation, à faire avant tout envoi** : auditer pour antériorité les **trois résultats de tête** jamais audités — « le traceur est un tirage », « la stabilité est un artefact de budget », « les segments publiés ne pavent pas une feuille ». Aucune des 14 clés de `66` ne les couvre. → fait dans [`71`](../71_les_trois_resultats_de_tete_audites.md).
  - **À ne pas faire** : verser les 27 documents restants. *« Un article qui contient tout ne démontre rien. »*
- **rétractations / corrections internes** :
  - §5, point 2 : ~~écrire l'arc excision/réparation~~ **RETIRÉ le 2026-09-03** — en voulant rendre son chiffre-clé recalculable, la réparation a été rejouée et **le résultat ne tient pas** : sur les deux traces mesurables de Scroll 5 la proximité **baisse de 22 à 50 %** là où `07` publie qu'elle ne bouge pas. L'arc reste le plus gros manque, et il demande d'abord d'être **refondé**.
  - §4 : deux défauts **du dépôt**, pas de l'article — `nappe/espacement_spires.py` tourne encore au **niveau 2** de pyramide, qui **fusionne les feuilles voisines** (pas mesuré **−10,3 %** en repassant au niveau 1, 36/36 négatif, sd 2,6), et propage le biais dans `ecart_de_maillages.en_micrometres()` ; `sensibilite_centre.py` repose sur une **prémisse fausse**, l'ombilic étant publié sur `dl.ash2txt.org` alors que la vérification portait sur le bucket S3.
  - ⚠ La correction du premier a été **vérifiée à la source** (`winding-ruler/atlas/build_atlas_v2.py:7-15`) et non arbitrée entre deux résumés : la fiche du `67` se lisait comme si l'article attribuait à tort ce chiffre à `winding-ruler`, alors que **les deux moitiés sont bien d'eux et la phrase de l'article est exacte**.
- **preuve de lecture intégrale** :
  - ligne 117 (après 64 % du fichier) : `zéros) les comptait comme « 49 fenêtres avec matière ».`
  - ligne 183 (dernière ligne non vide) : `[`registres/fiches_de_lecture.md`](registres/fiches_de_lecture.md).`

### docs/73_seconde_passe_ce_que_le_depot_change.md
- **lignes** : 426
- **nature** : REVUE
  (réponse à un second prompt externe, en quatre livrables : hypothèses révisées contre ce
  que le dépôt a mesuré, revue adverse de l'article, plan repondéré, et une observation neuve.)
- **résumé** : Reprend les sept hypothèses de [`69`](../69_reponse_dun_chercheur_exterieur.md)
  et les confronte à ce que le dépôt a **déjà** mesuré : deux sont mortes comme instruments
  (H3, H6 — le dépôt porte déjà la carte de séparabilité dense et l'atlas d'enroulement),
  deux passent au budget « étalonner la règle » (H1, H7), une devient un courriel conditionnel
  (H2), et deux **deviennent le plan** (H4, H5). Le document prend le cadrage au mot — *l'encre
  est la règle graduée* — et en tire une conséquence que `69` n'avait pas : une règle a une
  propriété à établir **avant** de s'en servir, elle lit quelque chose ; d'où trois semaines et
  non quatre mois. Sa thèse de fond est la séparation de **trois** prédicats — présence,
  placement, identité — dont le troisième est absent du dépôt et **est celui sur lequel le prix
  se gagne**.
- **conclusions extractibles** :
  - ⭐⭐⭐ Livrable 4 : **les segments publiés portent leur numéro de spire dans leur nom, et
    aucun instrument du dépôt ne le lit.** `PHerc0139` `w023`–`w059`, `PHerc1667` `w011`–`w041`
    — **57 segments, 56 spires distinctes**, approuvés par des humains, dont `0139` transformé
    dans le repère du régime du prix. C'est le référent d'**identité** que le prédicat du
    pinceau exige (*single sheet*), et celui que `17` n'avait pas : il a tourné sur **ces
    38 segments-là** contre des auto-intersections.
  - ⚠⚠ §2.1, la sur-affirmation la plus attaquable de l'article : *« the predicate is the same
    one α estimates »* est faux, il en manque deux tiers. Le pinceau juge l'**identité** (rester
    sur la feuille $k$), α juge la **présence** (une feuille est à portée), `offset` juge le
    **placement**. Remède : retirer *« the same judgement made two ways »* et **verser `17` dans
    cette section** comme le résultat négatif qu'il est.
  - ⚠⚠ §2.2 : *« no threshold on a physical quantity »* est vrai de α et faux du **verdict**.
    Une surface parallèle aux feuilles posée dans l'interstice a $d_0 = d_1$, donc **α = 0** et
    la convergence tient — l'instrument dirait « la feuille est là ». Ce qui l'en distingue est
    $d$ contre la demi-épaisseur, **un seuil en micromètres**. Test proposé : translater un
    segment convergent d'un demi-pas le long de ses normales.
  - ⚠⚠ §2.3 : les **113 µm** de l'article sont un écart **face à face** et non centre à centre —
    `gen_neighbor` arrête son rayon au premier échantillon au-dessus du seuil. Corrigé :
    113 + 24 à 60 d'épaisseur = **137 à 173 µm**, ce qui réconcilie avec les 156 de `16` et les
    172,8 de l'atlas que l'article cite trois lignes plus loin.
  - ⚠ §2.4 : le témoin négatif n'est **pas sans encre par construction**. La surface à α ≈ 1
    traverse des feuilles, donc leurs faces recto, donc l'encre — en rubans de largeur
    $t/\sin\theta$, **2 à 4 pixels** à 8,64 µm. Ce que la géométrie exclut est une **face** à
    portée, pas de la matière : la conclusion dure reste que la réponse du détecteur n'est pas
    spécifique d'une face.
  - ⚠ §2.5 : la méthode de la flèche suppose un axe droit, or l'axe erre de **21,6 mm sur
    108 mm** sur Scroll 1. §2.6 : les quinze segments de §5.7 sont des `auto_grown_*`, sorties
    d'un traceur à graine aléatoire — les nommer rend le résultat plus petit et inattaquable.
    §2.7 : « 13 » et « 14 traces » sont **deux définitions** (censurées à la profondeur basse,
    contre à l'une au moins des deux), toutes deux vraies, employées comme une seule.
  - ⚠⚠ §2.8, la limite non déclarée : **α n'a jamais vu de courbe ROC** — la validation est
    UN vert contre les traces condamnées du dépôt. Si la majorité des 75 séries convergentes
    sont des segments publiés, α **re-dérive** une approbation humaine plus qu'il ne la
    remplace. Les 57 segments indexés donnent 57 positifs, leurs copies translatées d'un
    demi-pas 57 négatifs : une ROC sur 114 surfaces fermerait §2.2 et §2.8 d'un coup.
  - ⭐⭐ Les trois prédicats : **présence** construite (`38`, `49`, `51`), **placement**
    construit (`20`), **identité absente** — `17` a échoué contre le mauvais référent, et le
    référent existe. « Le pinceau peint le troisième. Les deux premiers l'assistent et ne le
    remplacent pas. »
  - Budget de la règle, trois semaines et pas quatre mois : semaines 1–2 la case vide de `68`
    §4 **native** à 9,362 µm sur `PHerc0500P2` avec ≥ 40 tuiles de 256 px, semaine 3 le nul
    verso. Sortie : deux nombres avec leur intervalle. Si l'AUC native ne se sépare pas de 0,5,
    « colonnes visibles partout » devra être jugé par la typographie et par le juge à condition
    vierge — **une conclusion sur la méthode de validation, pas sur le prix**.
  - Dimensionnement **[calculé]** avec σ = 0,2243 : séparer l'AUC à 9,72 µm (0,599) de 0,5
    demande **40 tuiles** par condition, séparer 3,24 de 9,72 µm en demande **140**. On en avait
    10, 11 et 2. ⚠ Ce sont des **minorants** — les tuiles voisines ne sont pas indépendantes.
  - Choix de rouleau **révisé contre `69`** : `PHerc0826` était recommandé pour son faible
    nombre de spires (60) et c'est **le pire des treize** par la carte dense — **22,8 %** de
    fenêtres indissociables contre **2,6 %** pour `PHerc0800` et **7,0 %** pour `PHerc1447`.
    « Le compte de spires mesure le coût d'un pinceau ; la queue mesure la chance qu'un traceur
    suive. » **Jamais `0826`.**
  - Le contrôle du masque d'approbation prend un **quatrième bras** : la copie translatée d'un
    demi-pas, que le masque doit **refuser**. Sans lui, un masque qui approuve tout passe le
    contrôle à trois bras.
  - Mesure de succès de l'extraction : l'aire utile par spire contre le **point fixe de
    6,02 cm²** du cycle rogner-étendre ; une spire entière de `0800` fait 60 à 300 cm².
    ⚠ L'érosion d'une extraction est **à mesurer, pas à supposer** égale aux 15,6 % par tour
    d'une chaîne.
  - Trois vérifications faites à la source parce que les livrables en dépendent : les
    « croisements » de `17` sont des **auto-intersections** (`windcheck`), les segments publiés
    portent bien leur indice de spire, et **aucun `approval.tif` n'est publié** à côté des
    `x/y/z.tif` (listage S3).
- **rétractations / corrections internes** :
  - §1 H2 : ⚠⚠⚠ « **CE PARAGRAPHE SUR-AFFIRME, et `69` porte déjà le contre-argument** »
    (2026-09-04). À 1,2 m le papier rend deux verdicts pour la **même acquisition** — 4,317 µm
    *haze-limited*, 9,362 µm *pixel-limited* — donc la résolution est bornée par la
    **décohérence** : plus de voxels sur un signal déjà flou ne relèvent pas $d'$. Le courriel à
    l'ESRF devient **conditionnel**, et « aucune expérience à monter avant la réponse » est
    barré — l'expérience est justement ce qui décide s'il faut écrire.
  - §5 déclare quatre doutes, dont deux qui portent sur ses propres attaques : §2.2 repose sur
    une **lecture** de §3.6 et non sur une mesure, et §2.3 suppose que la source de la chaîne
    était centrée. « Le fichier tranche, pas moi. »
  - ⚠ Le `[je ne sais pas]` de §5 sur le **sens** des indices `w` — depuis le centre ou depuis
    l'extérieur — a été **fermé depuis** par [`76`](../76_le_sens_des_indices.md) : depuis le
    centre vers l'extérieur, 95,0 % et 95,1 % sur deux rouleaux. Et sa réserve « la numérotation
    peut être discontinue » s'est avérée : `76` mesure **3 paires sur 79 (~4 %)** où deux indices
    désignent la même surface publiée.
- **preuve de lecture intégrale** :
  - ligne 270 (après 63 % du fichier) : `rivaliser avec la flèche circonférentielle d'une corde de 8 à 22 mm sur un rayon de 2 à 4 cm.`
  - ligne 426 (dernière ligne non vide) : `premiers rouleaux tracés.`

### docs/74_le_73_audite.md
- **lignes** : 190
- **nature** : AUDIT
- **résumé** : Audit de `73` après lecture intégrale, avec la méthode de `71` : chaque revendication porteuse **rejouée contre la source**, pas contre le résumé qui en parle. Verdict de tête — *« `73` a fait ce que `69` n'avait pas fait : il a lu le dépôt »* ; ses quatre livrables portent, ses attaques sur l'article sont largement fondées, sa découverte de tête est réelle. Le document corrige trois choses, dont **une qui change la cible du plan** : le rouleau sur lequel `73` propose de déployer n'a aucun référent d'identité, et le bon rouleau était dans ses propres données.
- **conclusions extractibles** :
  - ✅ **`windcheck` compte bien des auto-intersections** (README : *« Self-intersection checks for Herculaneum surface traces »*). Donc `17` a testé « marche de phase locale contre auto-intersections » et son négatif ne porte **pas** sur « résidus contre sauts de spire » : **la réhabilitation de H5 tient** — un résultat négatif propre avait été lu comme fermant une question qu'il n'avait pas posée.
  - ✅ Les **15 segments de `PHerc1447`** de l'article §5.7 sont des sorties de traceur automatique : **14 `auto_grown_*` + 1 `z_dbg_gen_00320`**, et **zéro** segment indexé. Les nommer pour ce qu'ils sont rend le résultat plus petit et inattaquable.
  - ✅ Les **deux comptes** « 13 of 16 » et « 14 of 16 » sont tous deux dans `derive_profondeur.json`, avec des définitions différentes (`censurees_en_bas = 13` au plafond du rendu le moins profond ; `n_censurees = 14` à l'une au moins des deux profondeurs). L'article les emploie comme un seul nombre — correctif : **dire lequel est lequel**.
  - ⚠⚠ **113 µm n'est pas une propriété du rouleau, c'est la valeur d'une grandeur qui dépend d'un réglage** : `43` mesure **116 → 109 → 107 → 102 µm** quand `neighbor_step` est halvé trois fois. Le mécanisme de `73` (arrêt au premier échantillon au-dessus du seuil) est **périmé** — `43` va chercher dans la source (`vc_grow_seg_from_seed.cpp`) et trouve que le rayon doit d'abord **quitter** la nappe, donc peut sortir puis **y rentrer** et se poser sur la face proche de **sa nappe de départ**.
  - ⚠ Réserve **contre** `73` sur son propre appui : les **172,8 µm** de l'atlas de `winding-ruler` valent `lambda_med_lvlvox = 10.0` **voxels entiers** de niveau 1, soit un pas de quantification de 17,28 µm, IQR **121 à 250,6**. Ça ne contredit 113 que par son p25. L'appui solide est `16` (**156 µm** médian sur le même rouleau).
  - ⚠⚠ **La découverte de tête est réelle et sous-comptée ×1,8** : **101 segments indexés sur 3 rouleaux**, pas 57 sur deux. `PHerc0139` 37/38 indexés (spires `w023`–`w059`, **0 trou**), `PHerc0172` **44**/53 (`w052`–`w095`, **0 trou**) — absent de l'inventaire de `73` —, `PHerc1667` 20/20 mais **3 trous**. `PHercParis4` publie **58 plages** (`w010-027`, …), 28 distinctes : une plage nomme un intervalle, pas une feuille, et les compter gonflerait le référent d'un facteur cinq.
  - ⭐⭐ **Ce qui compte n'est pas le compte mais la CONTINUITÉ** : `73` bâtit H1′ (« un entier constant par spire, consécutif entre `w_k` et `w_{k+1}` ») en nommant `PHerc1667`, qui **saute** 13→18, 18→23, 23→28. Deux rouleaux portent une course **sans aucun trou** — `PHerc0139` (37) et `PHerc0172` (44), soit **81 spires consécutives**. H1′ est testable là, et pas sur celui qu'il a choisi.
  - ⚠⚠⚠ **Le plan de `73` §3.3 déploie là où le référent n'existe pas** : `PHerc0800` publie 6 segments tous `auto_grown`, `PHerc1447` 15 dont 14 — **aucun ne porte un indice de spire**. Le prédicat serait validé sur un rouleau et déployé sur un autre, et ce transport est une hypothèse que le plan n'énonce pas.
  - ⭐⭐⭐ **Un rouleau porte les deux, `PHerc0139`** : 37 spires consécutives approuvées par des humains, une carte dense sur **91 fenêtres** (au-dessus des 50–100 que `33` exige), une queue à **4,4 %** — deuxième des quatorze, devant `PHerc1447` (7,0 %) — et il est **déjà transformé dans le repère du régime du prix**. ⚠ Pourquoi `73` ne l'a pas vu : son fichier de carte dense s'appelle `_TEMOIN_PHerc0139.json`, lu comme un témoin donc écarté du classement, alors que le préfixe dit son rôle dans **une autre** mesure.
  - ⚠ Réserve honnête reprise de `73` : rien ne montre encore qu'un rouleau à 4,4 % se trace mieux qu'un rouleau à 22,8 % (`55` : le mur 1 vient de la graine, pas du scan). `0139` ne se justifie **pas** par sa queue seule — il se justifie parce que c'est le seul endroit où l'on peut **mesurer si le prédicat marche**.
- **rétractations / corrections internes** :
  - §5 : **la première version de `les_indices_de_spire.py` assertait que « aucun rouleau ne porte à la fois un référent d'identité et une carte dense »**. Le contrôle a **échoué**, et il avait raison — `PHerc0139` porte les deux, et c'est toute la conclusion du §4. *« Une assertion qui échoue est la seule chose qui sépare une conclusion d'une conviction. »*
  - §6, non vérifié ici : `73` §2.2 (une surface dans l'interstice donne α ≈ 0 — repose sur une lecture, pas une mesure ; se tranche en un rendu), §2.4 (le témoin négatif de §6.5 traverse des faces — se mesure en comptant les rubans traversés), §2.8 (α n'a jamais vu de courbe ROC — juste, et la ROC passe de 57 à **101** positifs avec le compte corrigé), §2.5 (la flèche axiale — la réserve se déclare, elle ne se mesure pas sur le rouleau de §5.5).
- **preuve de lecture intégrale** :
  - ligne 128 (après 67 % du fichier) : `première ligne du lecteur, comme `73` §4 le dit.`
  - ligne 190 (dernière ligne non vide) : `réserve se déclare, elle ne se mesure pas sur le rouleau de §5.5.`

### docs/75_registre_des_taches.md
- **lignes** : 3151
- **nature** : REGISTRE
  (le registre vivant des tâches ouvertes par `69`, `72`, `73` et `74`, tenu à jour au fil des
  mesures ; il porte donc **aussi** les résultats de celles qui se sont fermées.)
- **résumé** : Existe parce que quatre documents ont déposé des tâches en même temps et qu'un
  registre éparpillé dans quatre proses est un registre qu'on ne tient pas. Cinq colonnes —
  **A** remplacer le pinceau, **A′** ce qui reste sous les ✅, **B** l'article, **C** la règle
  graduée, **D** la dette — et **une seule compte** : ce qui remplace le pinceau. La règle de
  tri est le cadrage de `HANDOFF` §0–1 et rien d'autre : *le but est le déroulement, l'encre
  est la règle graduée, pas l'ouvrage.* ⚠ Ce n'est pas un document de résultats mais il en
  contient, parce que chaque tâche close y a déposé sa mesure avant de renvoyer au document qui
  la porte.
- **conclusions extractibles** :
  - ⭐⭐⭐ **A′ existe à cause d'une remarque de l'auteur, et c'est la meilleure idée de forme du
    fichier** : *« tu vois le logo vert de A3, tu vois le A3 bis, mais tu ne lis pas entre, et
    tu loupes les tâches que tu laisses comme ça. »* **Un ✅ fait arrêter de lire.** Tout
    « ⚠ Restant sur X » enfoui sous un titre coché est donc **recopié** dans une seule section,
    et la règle est écrite : marquer une tâche ✅ **oblige** à ajouter sa ligne dans A′ ou à
    écrire qu'il n'en reste rien.
  - ⚠⚠ **A4 corrige le plan de `73` §3.3** : le rouleau de déploiement est **`PHerc0139`**, ni
    `0800` ni `1447`. `0800` publie 6 segments tous `auto_grown`, `1447` en publie 15 dont 14
    — **aucun indice de spire**. `0139` est le seul à porter les deux : 37 spires consécutives,
    queue à 4,4 %, et **déjà transformé dans le repère du régime du prix**. ⚠ Il ne se choisit
    **pas** sur sa queue mais parce que c'est le seul endroit où l'on peut **mesurer si le
    prédicat marche**.
  - ⚠⚠⚠ **A5 bis : l'expérience que j'allais proposer était déjà faite**, et c'est la lecture
    des fiches qui l'a dit, deux fois de suite. `44` a **déjà jugé l'identité** : le point de
    départ étant un morceau de segment publié, la bonne feuille est connue sur toute l'emprise.
    Verdict — **la chaîne GLISSE, elle ne SAUTE pas** : écart lisse, monotone, du même côté pour
    **73 %** des points, **69 µm à 5,76 mm**, franchissant les 40 µm « même feuille » vers
    3,5 mm et restant loin des 250 µm « feuille voisine ».
  - ⭐⭐ Ce que la session ajoute est **plus petit et plus juste** : la surface publiée étant
    elle-même à 27 µm de la matière (`77` §10), **le budget d'écart de la chaîne est gonflé** —
    69 µm mesurés, ≈ **64** en retirant le référent en quadrature, donc le franchissement est
    **plus tardif** qu'annoncé.
  - ⚠⚠ **On ne compose PAS les micromètres de `44`** : `couverture_publiee.py` pose
    `UM_PAR_VOXEL = 2.4` justifié par cohérence **interne**, jamais contre un volume déclaré, et
    les deux volumes publiés du rouleau nommé sont à **7,91 µm**. Ce qui voyage est le référent
    **en feuilles** (0,121 – 0,146 sur trois rouleaux). Ce qui reste à faire est petit : que
    `44` **nomme son volume**.
  - **A6** : α n'a jamais vu de courbe ROC. Avec le compte corrigé ce sont **101 positifs** (et
    non 57) plus leurs 101 copies translatées d'un demi-pas — cela fermerait `73` §2.2 et §2.8
    d'un coup. ⚠ C'est **le seul poste du registre qui exige le volume** (rendre 101 surfaces à
    deux profondeurs).
  - **A5** : l'article a fermé les **deux** voies ascendantes par la mesure — l'extension
    converge vers un point fixe de **6,02 cm²**, les patchs ne pavent pas. Ce qui reste est
    l'**extraction** depuis un champ global, mesurée contre ce point fixe (une spire entière
    fait 60 à 300 cm²). ⚠ L'érosion se **mesure**, pas se suppose : une extraction n'érode pas
    comme une chaîne (15,6 % par tour).
  - ⚠ **C est borné exprès à trois semaines.** `46` mesure que le détecteur rend **plus** de
    dispersion sur une surface sans face (0,7111) que sur une face (0,5894) : une règle qui
    marque autant sur le vide que sur le plein ne valide aucun déroulage. Mais c'est un
    **étalonnage**, il se fait une fois et il s'arrête.
  - ⭐⭐ **C2, le nul verso, s'est INVERSÉ en cours de route** : sur une face **vierge** la
    dispersion du détecteur ne tombe que de **6 %** alors que le contraste local est **14 fois
    plus bas** — donc « il y a de la structure ici » ne discrimine pas. Le **niveau**, lui, se
    déplace (−0,27 contre −1,50). ⚠ Et la première campagne était **fausse**, sa cause écrite
    dans le module qu'elle appelait.
  - ⭐⭐ **C3 est mesuré et le courriel à l'ESRF n'est PAS justifié** : le débinage ne rend rien
    (rapport **1,01**). La condition que `69` §1.2 posait en toutes lettres — *« si elle est
    fausse, la donnée manquante la plus précieuse est une demande à l'ESRF »* — n'est pas
    remplie.
  - **D1 est FERMÉ et la conclusion de tête de `07` est CONFIRMÉE** : ce qui la démentait était
    une mesure **sans producteur**, prise sur une colonne dominée par son bruit
    d'échantillonnage. Sur `shortfall` (sans seuil, bruit < 5 %) : **0 paire sur 10** au-delà du
    bruit, signe mélangé. Ce qui est établi est une **borne**, pas une absence.
  - **D2 tient** : densité **2 812 à 2 857 cellules/cm²** sur 24 tirages (étendue **1,6 %**),
    donc cellules ∝ aire ; le modèle exige **×15,9** là où l'observé est **×4,0** — le
    basculement est plus raide que la taille. ⚠ Le « blocage » était une **erreur de recherche**
    : le rapport était dans l'arbre, cherché par un **nom** au lieu du **concept**.
  - **E, ce qui est hors registre avec sa raison** : la soumission (hors périmètre décidé par
    l'auteur) ; le second papier de `72`, qui est ⚠⚠⚠ **une occasion de publication et non un
    progrès vers le prix** et n'avance qu'avec C ; H3 et H6 de `69`, répondues par le dépôt.
  - ⛔⭐⭐⭐ **La piste des ancres est REFERMÉE le 2026-09-06** (`combien_dancres`, 46 contrôles,
    431 jeux d'ancres sur 9 cibles, même boîte 640 et même portée 4 que l'étude qu'elle
    prolonge). L'estimateur est la **droite des moindres carrés en bras signé, évaluée en zéro** :
    aucun paramètre libre, et à deux ancres de signes opposés elle rend **exactement** la
    pondération par les bras déjà mesurée — identité algébrique vérifiée sur six paires de bras,
    donc la généralisation **contient** le résultat qu'elle étend. Poids qui ne dépendent **que**
    des bras, jamais des données : un dérouleur pourrait l'appliquer sans regarder sa cible.
    **Courbe** : 70,3 → 42,5 → 37,2 → 35,3 µm ; sur les seuls jeux qui encadrent, 36,7 → 35,5 →
    35,3. ⛔ **La deuxième ancre enlève 27,8 µm, la troisième 1,2 et la quatrième 0,2.**
  - ⚠⚠ **Un chiffre publié sur une population confondue, corrigé** : la saturation était calculée
    sur la courbe **agrégée**, qui descend encore — or la part de jeux encadrants passe de 0 à 50,
    80 puis 95 % avec le nombre d'ancres, donc son affaissement mesure d'abord ce **changement de
    composition**. Les deux courbes sont publiées, la seconde tranche.
  - ⚠⚠⚠ **La prémisse de l'estimateur est FAUSSE au-delà du local, et la mesure le dit** : la
    dérive d'une ancre vaut 41,1 / 63,1 / 100,8 / **149,4 µm** aux bras 1 à 4, soit des incréments
    de **22,0 / 37,7 / 48,6** — elle **accélère**. Une droite n'en annule que la pente ; le résidu
    de l'encadrement accélère lui aussi (**4,0 / 10,6 / 19,2**). ⭐⭐⭐ C'est le **mécanisme qui
    manquait** à la tranche précédente, laquelle avait constaté que `1+4` et `2+4` nuisent en
    écrivant *« ce corpus ne dit PAS si c'est la longueur absolue ou le déséquilibre qui casse »* :
    c'est la **longueur** — à bras équilibrés, l'erreur passe de 30,0 à 63,8 µm entre ±1 et ±4.
  - ⛔ **Et la parabole ne paie pas non plus, mesurée avant d'être écrite comme une piste.** Un
    ajustement de **degré deux** annulerait la courbure et demanderait trois ancres pour être
    identifié, ce qui redonnerait un rôle à la troisième. Sur les **235 jeux d'au moins trois
    ancres qui encadrent — les mêmes jeux** — il rend **37,5 µm contre 35,3** pour la droite et ne
    gagne que sur 87 : sur des bras entiers de 1 à 4, identifier une courbure coûte plus de
    **variance** qu'elle n'enlève de **biais**.
  - Consigne pratique : deux ancres à **±2 tours** tiennent la feuille à **34,0 µm** (4 cas) ; à
    ±4, encore 63,8 µm mais sur **2 cas** seulement — le compte est publié **attaché** au chiffre.
  - ⚠ Une différence de méthode explique l'écart entre 36,7 et 35,9 µm sur ce qui est presque la
    même chose : la tranche précédente combinait **dans les deux sens** et mettait les distances en
    commun, celle-ci prend pour référence le nuage de l'ancre la plus basse.
  - ⚠⚠⚠ **D4 ouverte le 2026-09-06** — *le chemin qui produit le nombre publié n'est atteint
    par aucune batterie* : **67 modules sur 152**, **102 fonctions**, et la branche laissée
    dehors porte toujours le même nom (`mesurer` dans 13, `dessiner` dans 10). **Cinq modules**
    sont réparés et la matière **promue** en un lecteur unique plus deux fixtures qui décrivent
    le même objet (matière injectée par paramètre, découpage laissé dedans, batteries 32 → 46,
    9 → 17, 46 → 54, 20 → 30 et 63 → **75 contrôles**, vingt-deux sondes qui les font rougir) ;
    en cherchant où l'inscrire, **44 batteries que
    `temoins.sh` ne lançait pas** sont apparues. Document dédié :
    [`80`](../80_la_batterie_natteint_pas_le_nombre.md).
  - ✅✅ **D3 refermé le 2026-09-05** : `41 → 32 → 30 → 3` scripts sans appelant, et les onze
    documents sans fiche en ont une, celui-ci compris. ⚠⚠⚠ Le contrôle des fiches avait un
    **troisième** point aveugle : les fiches 43 à 49 séparent leur titre de leur compte par une
    LIGNE VIDE et le motif exigeait l'enchaînement immédiat — sept fiches **invisibles**, dont
    trois dérivaient réellement (`48` annonçait 342 lignes pour 405 pendant que le registre
    disait « 0 en dérive »).
  - ✅✅ **A5 bis refermé le 2026-09-05** : `44` nomme son volume, désigné par la
    géométrie et non par un argument. Un seul des cinq volumes publiés a une grille
    assez grande pour contenir le maillage, et il est à 2,400 µm. ⚠ Le contrôle
    `provenance_du_voxel_reconstructible`, écrit dans le sens « ce n'est PAS
    reconstructible » avec la note qu'il tomberait ce jour-là, **est tombé** — c'est
    exactement ce pour quoi il avait été écrit.
  - ⚠⚠⚠ **A2 ter est BORNÉE par le pas de la grille** (2026-09-05), et la mesure est faite
    AVANT d'intégrer quoi que ce soit. `PHerc0139` est le seul rouleau qui publie **à la fois**
    les spires indexées et des `normal-grids` (`PHerc0172` n'en publie aucune). Le produit
    déclare son pas **deux fois et d'accord** — `grid-step: 64` dans son `metadata.json`, `0x40`
    dans l'en-tête de chaque `.grid` : **64 voxels = 599 µm = 3,89 écarts inter-feuilles par
    cellule**.
  - ⭐⭐⭐ Un résidu est une intégrale de boucle **feuille à feuille** ($|\nabla\psi| = 2\pi/b$),
    donc il faut **deux échantillons par écart** — **8,23 voxels** au plus. Le produit publié est
    **7,8 fois trop grossier**. ⚠ Ce n'est pas un seuil choisi, c'est **Nyquist** : un pas plus
    grand ne dégrade pas la mesure, il la **replie**, et un gradient replié rend un résidu sans
    rapport avec la feuille. Même classe de borne qu'`A2 bis`, sur un **autre produit** — deux
    champs d'orientation publiés, deux fois trop grossiers pour compter des feuilles.
    ⚠ La sortie est nommée (`26` §7, `vc_gen_normalgrids` depuis un **volume**), et son coût
    aussi : à un pas de 8 voxels le produit serait **512 fois** plus volumineux que 10,4 Go.
  - ✅✅ **A5 bis répondu le 2026-09-05, et SANS recaler quoi que ce soit.** Le contrôle
    réclamait de refaire la mesure contre une surface recalée ; il se tranche par la **forme**
    du signal, parce qu'une erreur de référent a deux parts qui ne se retirent pas pareil :
    un **biais** est constant et **s'annule dans les différences**, une **dispersion** se
    retire en quadrature. La part qu'aucun biais ne peut expliquer vaut donc exactement
    $|e_N - e_1| / |e_N|$ — aucun ajustement, aucun seuil.
  - ⭐⭐⭐ La chaîne part à **0,3 µm** de la surface publiée et finit à **69,2** : un biais
    explique **au plus 0,5 %** de l'écart final, et le référent entier **au plus 4,5 %**
    (dispersion 19,5 µm en quadrature). ⚠ La borne n'est valide que si tous les écarts ont le
    **même signe** — vérifié, les dix sont négatifs — et le code **refuse** une série à signes
    mêlés. ⚠ $|e_1|$ **majore** le biais (le premier maillon a déjà parcouru 96 µm), donc la
    borne est conservatrice.
  - ⭐ « Un référent mal placé produit un **décalage** ; la chaîne produit une **rampe**. Ce ne
    sont pas les mêmes objets, et une rampe ne se corrige pas en déplaçant une origine. »
  - ⚠⚠⚠ **C1 : l'agrégation LOCALE ne recale pas non plus** (2026-09-05, sur les mêmes 34
    carreaux). Le remède classique de l'ouverture est Lucas–Kanade — agréger un voisinage
    plutôt qu'imposer une forme globale. Sur la **norme entière** il marche aux grands rayons
    (47,8 contre 60,4 pour le champ nul, 21 % de mieux), et **j'avais assuré l'inverse** :
    c'est la mesure qui a corrigé.
  - ⚠⚠⚠ **Et c'est un MIRAGE** : sur la composante **normale**, la seule que chaque carreau
    mesure, aucun rayon ne bat le champ nul — de 2 à 25 voisins. Le gain de la norme entière
    vient **entièrement de la direction non contrainte**, donc d'une grandeur que personne
    n'a mesurée. ⭐ Péché cardinal sous un costume de plus : **une amélioration sur la
    composante que la mesure ne contient pas**. Les contrôles qui l'attrapent sont que les
    deux métriques doivent se **contredire** quelque part et que la composante soit
    **strictement** plus petite que la norme.
  - ⚠ Le voisinage reste local (au plus 25 carreaux sur 34), donc ce n'est pas un modèle
    global déguisé, et le conditionnement des directions plafonne à **0,60** pour 1 en
    isotropie : même à seize carreaux, **les bords ne couvrent pas le plan**. Ce qui manque
    n'est pas la forme du modèle mais la **matière** — du contenu intérieur.
  - ⭐⭐ **C1 : le contenu intérieur EXISTE** (2026-09-05) — **348** trous d'au moins 64 px dans
    le masque, dont **314** dont le bord couvre assez le plan. Un trou est un repère
    **géométrique**, donc s'en servir ne rend pas circulaire la mesure d'encre qui suit,
    contrairement à l'optimum obtenu en regardant l'encre. 314 repères **intérieurs** contre
    34 carreaux de **bord**, chacun mieux conditionné que le meilleur voisinage de bord (0,60).
  - ⚠⚠⚠ **Mais la moitié qui manque est de l'AUTRE côté** : le régime du prix ne publie
    **aucun masque de surface** — l'empreinte disponible est le **support de la carte d'encre**,
    une propriété du détecteur, et seulement à 1024 de large. Des 314 repères il en reste
    **19** à cette résolution. Le prix de la voie est donc **un masque publié**, ou les
    étiquettes rendues au régime du prix — la case vide de `68` §4 par un autre chemin.
  - ⚠ La réduction est par **majorité de bloc** et non par échantillonnage : sinon le compte de
    repères dépendrait de l'alignement de la grille. Sur une fente de trois pixels, la sonde
    qui échantillonne rend **1 trou contre 0** selon un décalage de cinq pixels.
  - ✅✅ **Et les repères ONT un vis-à-vis** (2026-09-05) : là où il n'y a pas de matière un
    détecteur ne peut rien rendre, donc le **support de la carte publiée porte les trous du
    fragment** — c'est un masque de fait. **55** repères transportables à l'échelle de la
    carte (3305 × 1883) contre **71** trous du support, appariés à **40,3** cellules en
    médiane (1er décile 16,1) contre **319,6** pour autant de points tirés au hasard dans la
    même empreinte : **huit fois mieux**. La voie de C1 est ouverte **sans rien demander**.
  - ⚠⚠⚠ **ET CE « VIS-À-VIS » EST CORRIGÉ LE JOUR MÊME, par la carte à pleine résolution.** Le
    segment publie aussi `ink-detection` en `.tif` natif (26 440 × 15 060, 20,5 Mo) à côté du
    `.jpg` réduit ×8 que tout le lot lisait par habitude. L'échelle du transport passe de 0,12 à
    0,97, donc les **314** repères utilisables sont **tous** transportables au lieu de 55.
    ⚠⚠ Mais le support n'y porte que **36** vides intérieurs quand le masque en a **348**, et le
    témoin tranche : réduire le support natif ×8 par la même règle rend **19** composantes de
    fond, pas **420**. Les 71 « trous » du réduit sont donc en grande part du **crénelage de
    `.jpg`**, qui sonne aux bords à fort contraste — le pourtour des vrais trous. « Le support
    est un masque de fait » est **faux** ; ce qui survit est que les repères se posent **7,7×**
    plus près des vides qui existent que le hasard (796 px contre 6 114).
  - ⚠⚠ **Et le gain est de la DENSITÉ, pas de l'étendue** : la couverture de l'empreinte à
    1,1 mm passe de 4,9 % à 10,5 % et à 8,9 mm de 53,5 % à 94,0 %, mais le 80 % central du semis
    ne passe que de 24,1 × 16,1 % de la carte à **28,7 × 18,1 %** pour **5,7 fois** plus de
    repères. C'est le dessin qui l'a imposé, pas les chiffres. **Le goulot a déménagé côté
    cible**, il n'a pas disparu.
  - ⭐ Leçon de méthode : **le fichier par défaut d'un index n'est pas le meilleur fichier de
    l'index**. Cinquante-neuf repères sur soixante étaient perdus par un choix de lecture.
  - ⛔⛔ **ET L'APPARIEMENT LUI-MÊME EST ENTERRÉ, par un témoin qui ne casse qu'une chose.** Les
    deux tranches précédentes comparaient à un semis **uniforme**, qui casse la place ET le
    groupement — or les repères sont groupés, donc un semis uniforme est loin de tout **par
    construction**. Le témoin juste garde la géométrie du nuage au bit près et ne déplace que sa
    position : sur **20 poses**, la vraie place fait **796 px** contre **638** pour la meilleure,
    **1 015** en médiane et **1 411** au pire. **Rang 6 sur 21, p = 0,29** — cinq poses au hasard
    font mieux. Le « ×8 » puis le « ×7,7 » mesuraient le **groupement**, pas une correspondance.
  - ⭐ Ce qui reste établi et solide : le support publié **est un masque**, et l'histogramme le
    dit sans ambiguïté — **37,5 %** de zéros puis un **vide de 27 niveaux** avant la première
    valeur rendue (28). Un détecteur qui prédit peu occupe 1, 2, 3 ; un pipeline qui masque écrit
    un zéro franc. C'est donc le masque du **régime du prix**, avec ses 36 vides à lui.
  - ⚠⚠⚠ **La leçon de méthode qui vaut pour tout le dépôt** : *un témoin doit casser une seule
    chose*. Celui qui en casse deux ne peut pas dire laquelle comptait, et il rend un rapport
    flatteur qui ne mesure que le confond oublié.
  - ⚠⚠ **La figure a attrapé une sur-affirmation de ma propre prose** : j'y écrivais les
    repères « répartis à l'intérieur », et le dessin montre qu'ils sont **groupés d'un côté**
    — 12 sur 55 dans la boîte centrale. Ils sont dans l'**aire** du fragment et non sur son
    contour, ce que les 34 carreaux de bord n'étaient pas ; ils ne sont pas **étalés** pour
    autant.
  - ⚠ Le contrôle négatif est un **décalage d'une demi-maille**, pas « des trous ailleurs » :
    ma première version mettait les repères dans les coins et ils **battaient quand même** le
    témoin, un coin restant systématiquement plus proche qu'un point tiré n'importe où sur une
    empreinte dont les cibles sont sur une grille.
  - ⚠ L'échelle des flèches est prise au **9e décile** (91 cellules) et non au maximum : un
    appariement raté à **492** écrasait tout le reste à l'invisible. **Le maximum n'est pas le
    champ, c'est son échec.**
  - ⭐⭐⭐ **Et le résidu n'était PAS un champ : c'est une TRANSLATION** (2026-09-05). Tout C1
    avait été jugé sur **une** fenêtre ; refait sur **127**, chaque fenêtre demande à peu près
    le même décalage — médiane **(−24, 0)** cases, soit **425 µm**, dispersion **471 µm** —
    quand les deux champs candidats déplacent de **60,4** et **40,3** cases, donc **plus que le
    désaccord qu'ils prétendent corriger**. Une simple constante porte l'AUC médiane de
    **0,755 à 0,852** en améliorant **116 fenêtres sur 127**, et l'accord publié sur toute
    l'empreinte de **0,756 à 0,857** : *le nombre de référence de tout le lot mesurait aussi un
    défaut de recalage.* Le maximum est **intérieur** au balayage, contrairement au (−104, −120)
    publié plus haut.
  - ⭐⭐⭐ **La question suivante n'est pas « laquelle est la meilleure » mais « laquelle a le
    DROIT d'être appliquée »** (2026-09-05). Appliquer le (−24, 0) trouvé sur l'encre serait
    circulaire, donc la règle est de **provenance** : seule une translation tirée de la
    géométrie peut être retranchée, et `applicables()` exclut l'autre **par construction**. La
    retenue est l'optimum des silhouettes **(−8, −8)**, Dice **0,975255** contre 0,974601, et
    l'encre le confirme de l'extérieur : **0,7561 → 0,7943**, soit **37,8 %** du plafond que
    l'encre situe à 0,8571. ⚠ Il reste **17,9 cases, 317 µm**.
  - ⚠⚠ **La géométrie n'IDENTIFIE pas la translation, elle la borne** : quatre critères sans
    encre donnent quatre réponses étalées sur **16,9 cases** et atteignant de **13,7 %** à
    **68,6 %** du plafond. Ce n'est pas un nombre, c'est un intervalle aussi large que la
    translation elle-même.
  - ⚠⚠⚠ **Et le critère des silhouettes est CONTRAIRE, pas seulement faible** : les **trois**
    translations qui font monter l'AUC font toutes **baisser** le Dice, y compris l'optimum de
    l'encre, dont le Dice (0,97263) est **sous** celui de l'affine non corrigée (0,974601). Une
    procédure de recalage pilotée par le recouvrement des contours s'éloigne donc de la bonne
    réponse en croyant s'en approcher — c'est, en une phrase, pourquoi le champ de bord, le
    modèle lisse et l'agrégation locale ont tous échoué.
  - ✅ **Le contrôle de signe tombe au dernier chiffre** : corriger l'affine ou décaler la
    lecture donnent **0,79431 contre 0,79431**, écart 0,0000. Il n'était pas remplaçable par une
    relecture, une correction à l'envers ne levant rien — elle rend juste un accord plus bas.
  - ⚠⚠⚠ **Le plan des SILHOUETTES explique l'échec des bords** : jugé sur le Dice, le même plan
    de décalages s'étend sur **0,0315** quand celui de l'encre s'étend sur **0,4234** (témoin
    mélangé : **0,0025**), et son sommet est **(−8, −8)**, pas (−24, 0). Les silhouettes
    arbitrent — douze fois le plancher de bruit — mais **treize fois moins fort que l'encre, et
    vers un autre point** : un champ ajusté dessus l'est sur le mauvais signal.
  - ⭐⭐ **Les repères sont prédictifs, les carreaux non, et c'est pourtant la constante des
    BORDS qui gagne.** Laisser-un-dehors : repères **31,8** contre 40,2 au champ nul et 42,8 au
    meilleur de 20 mélanges de positions ; carreaux **77,5** contre 60,5 et 58,8, donc échec aux
    deux témoins. Mais (−13, +2), la médiane des carreaux, est à **11** cases de l'optimum quand
    celle des repères est à **22** — les repères sont **groupés d'un côté**, les carreaux sont
    **répartis**. **Quand ce qu'on cherche est une constante, la couverture bat la précision.**
  - ⭐⭐⭐ **ET L'INDEX PUBLIAIT TREIZE SPIRES DE CE FRAGMENT, jamais ouvertes** (2026-09-05, sur
    l'intuition de l'auteur *« regarde sur les autres serveurs au cas où »*). `PHerc0500P2`
    compte **39** segments dont **13** nommés `wrap01` à `wrap13`, chacun publiant sa surface en
    `tifxyz` **sur les trois volumes** et sa carte d'encre pleine résolution. Mesuré : l'écart
    médian entre spires **consécutives** vaut **135,5 µm**, contre **147,4 µm** mesurés ailleurs
    dans le dépôt **sur un autre rouleau** — 8 % d'écart avec une prédiction extérieure. Et il
    **croît avec le rang** : 135,5 puis **320,7** (×2,37) puis **454,6** (×3,35), donc ce sont
    des tours empilés et pas treize morceaux quelconques.
  - ⚠ **Quatre paires sur douze s'écartent de moitié ou plus** (4→5 à 232 µm, 10→11 à 292,
    11→12 à 327, et 12→13 à **65**, plus près qu'une feuille) : la numérotation n'est pas
    géométriquement parfaite partout. Elles sont dessinées comme les autres.
  - ⭐⭐ Ce que ça ouvre : une **vérité de terrain du déroulement**, publiée et exacte, contre
    laquelle une chaîne reconstruite peut être **notée** ; et un **repère commun entre les deux
    régimes**, chaque spire publiant son `tifxyz` sur le volume de production **et** sur celui
    du prix — la tâche « une fenêtre dans un repère commun » cesse d'être une estimation.
  - ⚠⚠⚠ **Cinquième occurrence du même angle mort** : le référent avait été déclaré absent faute
    d'avoir interrogé un serveur ; ici c'est un dossier de l'index qu'on n'avait jamais énuméré.
    **Ce qu'on croit absent doit être cherché avant d'être reconstruit.**
  - ⭐⭐ **Et l'angle mort est maintenant OUTILLÉ** (`ce_que_les_serveurs_publient`, 13 contrôles).
    L'inventaire corrige l'hypothèse : **39 segments sur S3, 39 dans l'index, 0 écart** — le cache
    n'était pas périmé, personne ne l'avait **énuméré**. La vraie cause est structurelle : les deux
    serveurs ne publient **pas la même chose**. `segments/` (les 13 spires) et `photos/` ne sont
    que sur **S3** ; `paths/` (les étiquettes et le masque), `cases/` et `multispectral/` que sur
    **`dl.ash2txt.org`**. Les étiquettes venaient de l'un, les segments de l'autre, et personne
    n'avait croisé les deux listages.
  - ⛔ **Et les treize spires ne sont PAS la région de C1 : elles en sont une SECONDE** (2026-09-05).
    Deux seuils, aucun choisi : la coïncidence à **67,75 µm** (la moitié de l'écart mesuré entre
    spires) et la barre du verdict à **56,74 %** (le plafond qu'une spire atteint sur une AUTRE
    spire, mesuré sur 156 paires). Le segment `500P2_front` couvre **0,0 %** des treize et de leur
    union, et sa surface la plus proche est à **2 134 µm**, soit **15,7 épaisseurs de feuille**.
    ⭐⭐ Le corpus **double** — treize surfaces de plus, géométrie exacte sur les trois volumes,
    chacune avec sa carte d'encre pleine résolution — mais C1 n'y gagne **aucun voisinage**.
  - ⭐⭐⭐ **ET LA PRIMITIVE DU DÉROULEMENT EST VALIDÉE SUR CETTE VÉRITÉ DE TERRAIN** (2026-09-06).
    Toute la colonne « chaîne » reposait sur une supposition jamais confrontée à autre chose
    qu'elle-même : *un écart inter-feuilles le long de la normale tombe sur la feuille voisine*.
    Mesuré sur les douze paires de spires consécutives : **ne rien faire 135 µm**, **un écart
    60 µm**, **deux écarts 151 µm**. Le V est le résultat — le pas nul retombe sur l'écart mesuré
    (135 contre 135,5), donc les spires sont voisines ; le simple le divise par plus de deux ; et
    le **double dépasse**, donc la distance franchie est bien celle d'**une feuille** et non une
    quantité quelconque. **11 paires sur 12**, et le sens retenu est le **même pour les douze** —
    les grilles publiées partagent une orientation, ce qu'aucune mesure n'avait établi.
  - ⭐⭐⭐ **ET LE GRAAL EST RAMENÉ À UNE MESURE : un dérouleur aveugle tient DEUX tours**
    (2026-09-06). Le pas normal **itéré**, grille conservée donc normales recalculées sur la
    surface **prédite**, un seul bit de supervision (le sens, fixé au premier pas). Erreur : 52 µm
    au tour 1, **102 au tour 2**, 135 au 3, 689 au 12 — contre 129, 311, 418 et 1 648 pour
    l'immobilité. ⛔ **La feuille est perdue au tour 2**, l'erreur dépassant la demi-épaisseur
    (67,75 µm). ⭐⭐ **Et pourtant il déroule** : il bat l'immobilité à **chacun des douze tours**,
    deux à trois fois.
  - ⭐⭐⭐ **La dérive vaut 53 µm par tour, soit 39 % d'une feuille** — ajustée par moindres carrés
    sur toute la marche et non prise entre deux extrémités. **C'est le chiffre à battre** : la
    feuille suivante est toujours dans la bonne direction, elle est juste un peu plus loin ou un
    peu plus près que l'épaisseur nominale, et personne ne recale. C'est exactement ce qu'un
    recalage sur la matière doit tuer à chaque pas.
  - ⭐⭐ **Et la dérive est à UN CINQUIÈME un biais, le reste une dispersion** (2026-09-06). La
    question vient avant tout recalage lourd : il serait absurde de lire le volume si les 53 µm
    par tour venaient d'une longueur de pas mal estimée. Longueur ajustée sur **six** paires et
    jugée sur les **six réservées** — coupure **sur le rang**, parce que deux spires voisines
    partagent leur géométrie. Résultat : ajustée **108,4 µm** contre **135,5** nominaux, soit un
    biais de **27,1 µm** ; sur la moitié réservée **54,1 µm** contre **67,6**. ⭐ Le biais est
    réel — elle gagne sur ce qu'elle n'a jamais vu — ⚠⚠ mais il n'explique que **20 %**, et le
    plancher de la courbe réservée est à **50,5 µm**. ⛔ **Un meilleur nombre ne remplacera pas
    un raccrochage à la matière**, et l'étalon de la tranche suivante est de passer sous 50 µm.
  - ⛔ **Et le raccrochage ne peut PAS se bâtir sur ce qui est publié** (2026-09-06). Chaque spire
    publie un `surface-volumes` en **(couche, u, v)**, donc l'indice de couche EST une distance
    signée le long de la normale — mais les métadonnées ne disent **pas** où est la surface.
    Mesuré sur **1 459 592 colonnes** de trois spires : le pic tombe à **−1,5 couche** du centre
    (tolérance une demi-feuille = 30,6 couches), donc **la convention du milieu tient**. La pile
    porte alors à **129,6 µm**, soit **0,956 feuille**, quand la voisine est à 135,5 : **il manque
    5,9 µm**. Il faut le **volume brut**. Le savoir coûte une mesure ; l'apprendre après avoir
    écrit le raccrochage aurait coûté le raccrochage.
  - ⚠⚠ Le piège du profil : sur trois blocs voisins pris isolément le pic tombait à **66, 78 et
    85** — un bloc de 128 × 128 colonnes ne voit qu'un morceau de feuille. Le profil n'a de sens
    que **cumulé**, et le compte de colonnes est rendu pour qu'un profil bâti sur trois d'entre
    elles ne passe pas pour une mesure.
  - ⚠ La surface retenue est le **centre**, pas le pic : le pic la confirme, mais la prendre ferait
    dépendre la géométrie d'un contraste local.
  - ⚠ La première fixture de cette batterie a échoué pour la bonne raison : elle balayait 20 à
    40 µm pour une cible à 30 **voxels**, soit 60 µm. C'est le drapeau `au_bord` qui l'a dit — ce
    dépôt a déjà publié un optimum au bord et l'a payé.
  - ⚠ La grille fond de **1 983 à 536** cellules sur douze tours (une normale demande quatre
    voisins), et le compte est rendu **à côté** de l'erreur : un dérouleur qui « réussirait » en
    ne gardant que trois cellules aurait rétréci, pas déroulé.
  - ⚠ La seule paire qui échoue est **12 → 13**, dont l'écart vaut 63 µm, moins d'une demi-feuille :
    un pas entier y dépasse forcément. C'est la paire anormale déjà signalée.
  - ⚠⚠ Ce que ça ne dit **pas** : le pas tombe **à 60 µm** de la feuille suivante, soit 44 % d'un
    écart. C'est la précision réelle de la primitive — assez pour ne pas confondre une feuille
    avec sa voisine, pas assez pour se passer d'un recalage local ensuite.
  - ⚠ Nuance rendue visible par la calibration : **les spires publiées ne sont pas disjointes**,
    la meilleure paire se recouvrant à **56,7 %** sous une demi-épaisseur. « Treize tours
    consécutifs » ne veut donc pas dire treize feuilles séparées.
  - ⚠⚠ Deux défauts de méthode de cette tranche, tous deux miens : un `str.replace` **sans
    assertion** est un no-op silencieux — la calibration annoncée n'avait jamais été appliquée et
    le verdict tournait encore sur des seuils choisis (0,8 / 0,2) ; et une **part de recouvrement
    nulle sans son échelle n'est pas une mesure**, le même 0 % valant pour 70 µm et pour 7 mm.
  - ⚠ Le **refus** fait partie de l'outil : un listage vide est une coupure, pas un verdict, et le
    comparer à un index plein dirait « l'index a tout inventé ».
  - ⚠⚠ Défaut de mon propre outil attrapé avant publication : `index_local` ignorait son argument
    et rendait les **311** segments des 45 objets, d'où un faux « 272 à l'index seulement ». Un
    inventaire qui crie faux est un inventaire qu'on cesse d'écouter.
  - ✅✅✅ **SUR LE VOLUME BRUT, LE RACCROCHAGE PASSE SOUS L'ÉTALON : 33,3 µm** (2026-09-06). Le
    volume de scan de `PHerc0500P2` est publié (28096 × 18209 × 18209 voxels, blocs de 128³ **non
    compressés**), et son nom porte l'horodatage du volume *et* sa taille de voxel — tous deux
    confrontés à ce que les spires déclarent avant qu'un octet ne soit lu. Sur sept paires :
    **ne pas bouger 93,9 µm**, **pas normal seul 46,7**, **raccroché 33,3**, contre l'étalon de
    **50,5** que laisse la meilleure longueur constante. Le raccrochage fait donc ce qu'aucun
    nombre transporté ne peut faire.
  - ⛔⛔ **Et ce n'est PAS la matière la plus proche qui raccroche, c'est la FORME d'une feuille.**
    Le **maximum brut** d'intensité rend **46,1 µm**, c'est-à-dire *rien* de plus que le pas seul :
    la crête est large de trente voxels, un maximum s'y pose n'importe où. Ce qui travaille est la
    **corrélation normalisée** de la ligne avec le profil de feuille lu **sur la spire de départ**
    — donc un gabarit qui ne sait **rien** de la cible.
  - ⭐⭐ **La convention se mesure avant tout raccrochage** : sur **2401 lignes** de sept spires, la
    crête de matière est à **−6,6 µm** de la surface publiée et le creux d'air à **+33,2 µm**,
    contraste **40,7**. ⚠⚠ Ma première version a trouvé un « pas de crêtes » de **8,9 µm**, soit
    quatre voxels — l'ondulation de l'échantillonnage. **Chercher un pic sur un profil non lissé
    trouve du bruit**, et le rend avec toute la précision d'une mesure. ⚠ Et un créneau seul ne
    suffit pas : une ride d'un échantillon est **exactement Nyquist**, seul un noyau de longueur
    paire (le `[1, 2, 1]` ajouté au créneau) l'annule à zéro.
  - ⭐ **Trois témoins, chacun ne cassant qu'une chose** : gabarit **mélangé** 56,6 µm (le lien
    décalage↔matière), fenêtre d'une **feuille entière** 76,6 µm (la fenêtre dérivée d'une
    demi-épaisseur), et **raccrocher sans avoir bougé** ne déplace que de **10,8 µm** — le gabarit
    retrouve donc sa propre feuille.
  - ⚠⚠ **Deux paires sur sept empirent, et pour deux causes différentes, toutes deux nommées** :
    9→10 part déjà à **70,1 µm**, au-delà de la demi-fenêtre de 67,8, donc la bonne feuille n'est
    **pas à portée** ; 6→7 a un gabarit qui ne retrouve pas sa feuille de départ (30,5 µm sur
    place). ⚠ Ce déplacement sur place est calculable **sans la réponse** — ce serait le bon signal
    de confiance — mais il **ne sépare pas** les deux échecs ici. Dit plutôt que vendu.
  - ⚠ **L'accord des voisins n'ajoute rien, et c'est son témoin qui le dit** : une feuille est
    lisse, donc la médiane du voisinage 3×3 devrait corriger l'isolé — elle reprend **0,7 µm**
    quand la médiane de **neuf décalages sans rapport** en reprend déjà 8,6 sur la même queue. Ce
    qui travaillait était la médiane, pas le voisinage.
  - ⚠ Une paire n'est retenue que si la spire d'**arrivée** passe dans la boîte, critère
    **géométrique** : sans lui 10→11 entrait avec mille micromètres d'erreur, non parce que le
    raccrochage échoue mais parce que la spire 11 ne couvre pas cette région. Écarter sur l'erreur
    aurait été choisir sur le résultat.
  - ⛔⛔ **ET À L'ITÉRATION, RIEN NE DÉROULE** (2026-09-06, sur 906 cellules et six tours). Le
    raccrochage par point dérive de **+56,1 µm par tour** contre **+22,3** pour l'aveugle, et il
    dérive plus que lui aux **trois** tailles de boîte mesurées (384, 512, 640 voxels). Ni
    l'accord des voisins (+33,6) ni une fenêtre deux fois plus étroite (+43,0) ne le rattrapent.
    ⛔ **Aucun contendant ne tient la feuille au dernier tour, et le moins mauvais est celui qui
    ne lit rien.**
  - ⭐⭐⭐ **ET LA RAISON EST MESURÉE : le gain ne survit pas à UN tour.** La trajectoire de
    référence avance **en aveugle** — donc une surface qui vieillit sans que le raccrochage y
    soit pour rien — et à chaque tour on en tire **deux pas depuis le même point**, un aveugle
    et un raccroché ; une seule variable change. Depuis une spire **publiée** le raccrochage
    gagne **+12,7 µm** ; dès qu'**un seul** tour aveugle a été fait il gagne **−0,2**, et sur les
    quatre âges suivants la médiane vaut −0,2 avec un signe qui change quatre fois.
    ⛔⛔ **Le raccrochage ne raccroche que ce qui est déjà à sa place** : les 33,3 µm d'un pas
    sont un gain **conditionnel au point de départ**, pas une capacité de la méthode.
  - ⚠⚠ **Le critère est structurel, pas un seuil** : ma première version demandait « moins de la
    moitié du gain initial » et elle est tombée sur **6,8 contre 6,35**, un verdict décidé au
    dixième de micromètre par un nombre que j'avais choisi. Ce qui distingue un effet d'un bruit
    n'est pas sa taille — c'est que le bruit **change de signe** et qu'un effet non.
  - ⭐ **Un lissage sert d'autant plus que la nappe est grande** : à 191 cellules l'accord des
    voisins n'apportait rien, à 906 il reprend un tiers de la dérive du par-point. C'est
    l'inverse de ce que la petite boîte laissait croire, et seule la boîte élargie l'a montré.
  - ⚠ Le groupement des perdues a **inversé mon hypothèse** : celles du par-point sont à peine
    groupées (2,33 puis 1,0) quand celles de l'aveugle le sont fortement (3,46 puis 4,14). Le
    raccrochage échange une erreur **cohérente** contre une erreur **éparpillée**.
  - ⚠ Le pas aveugle de ce fichier **est** celui du dérouleur publié — `raccrocher=False`
    traverse le même code, et la batterie vérifie l'égalité **au bit près**.
  - ⭐⭐⭐ **LE MÉCANISME, trouvé en éliminant : ce sont les NORMALES.** Trois soupçons testés et
    écartés, chacun ne cassant qu'une chose — fenêtre deux fois plus étroite (**+43,0**),
    décalages accordés au voisinage (**+33,6**), gabarit **figé** lu une fois sur la spire de
    départ (**+54,2** contre +56,1 sans remède, et son contraste ne s'effondre pas : 51, 78, 53,
    40, 47, 51). La surface ressemble encore à une feuille ; c'est la **direction** de recherche
    qui se perd.
  - ⭐⭐⭐ **Lisser les NORMALES divise par deux la dérive du raccrochage (+56,1 → +25,3) et ne
    fait RIEN pour l'aveugle (+22,3 → +22,0).** C'est la seconde moitié qui prouve la première :
    si les normales étaient mauvaises pour tout le monde, les lisser aiderait les deux marches.
    Elles ne le sont que là où le raccrochage est passé — **il ride la nappe, la nappe gâte ses
    normales, et la mauvaise normale gâte le pas suivant.**
  - ⚠⚠ **Ce n'est pas le même geste que l'accord des voisins** : accorder lisse **de combien** on
    bouge, lisser les normales lisse **dans quelle direction** on cherche. Les deux ensemble
    donnent **+29,4**, moins bien que les normales seules — ils se recouvrent et sur-lissent.
  - ⭐⭐ **Et c'est le contendant le plus stable des dix au balayage** : +26,0 · +25,8 · +25,3 aux
    trois tailles, quand le pas aveugle oscille de +13,3 à +25,5. Aux deux plus grandes tailles
    les deux sont **à égalité** — le raccrochage réparé ne coûte plus rien et ne rapporte
    toujours rien.
  - ⚠ La **dispersion angulaire** du champ de normales (2,8° → 10,9° sur six tours) est le seul
    signal de confiance de la tranche qui **n'exige pas de connaître la réponse** : un dérouleur
    peut la calculer sur lui-même en marchant.
  - ⛔⛔ **ET CETTE DISPERSION EST UN SYMPTÔME, PAS LA CAUSE.** Une normale est une **dérivée**,
    donc élargir le support de la différence centrée divise le bruit d'autant — mesuré, un
    support de deux le divise par **sept** (10,9° → 1,5°) et l'écart latéral qu'il prédit
    (`L·sin θ`) passe de **26 µm à 4**. ⛔ Et au premier tour, seule comparaison non confondue
    par l'érosion (500 à 800 cellules partout), **la dispersion tombe de 43 % et l'erreur du pas
    ne bouge pas d'un micromètre** : 42,7 · 42,2 · 42,3 · 41,7 µm. **Quatre soupçons testés,
    quatre écartés** — la fenêtre, les décalages, le gabarit, les normales.
  - ⚠⚠ **La comparaison au-delà du premier tour est CONFONDUE** : un support large mange le bord
    d'une cellule de plus par côté et par tour, donc 349 cellules contre 41 au sixième. Les deux
    moitiés du verdict sont exigées ensemble — « la dispersion baisse » seul dirait que ça
    marche, « l'erreur ne suit pas » seul dirait que ça ne sert à rien.
  - ⚠ Deux défauts de ce contrôle, tous deux miens : il vérifiait d'abord que **60·sin(10°) vaut
    10,42**, c'est-à-dire mon arithmétique contre elle-même — remplacé par l'accord des **deux
    colonnes publiées** ; et sa fixture de bruit avait une **période de trois** que le support
    trois annulait exactement, donc il passait à 0,00°, vrai pour une raison qui n'était pas
    celle qu'on teste.
  - ⚠ Un délai réseau a tué un balayage après **232 blocs déjà téléchargés**. Le lecteur avait
    raison de refuser de confondre « pas de réponse » et « pas de matière », mais un incident ne
    dit rien du contenu : il se **réessaie**, borné, compté et rendu.
  - ⛔⛔ **ET LA LONGUEUR LOCALE DU PAS NE SE LIT PAS NON PLUS** (2026-09-06). C'était la
    dernière quantité que toutes les marches tenaient pour acquise. La médiane lue vaut
    **136,9 µm** contre **135,5** publiée — un accord à sept millièmes qui ne prouve **rien** :
    la médiane d'un tirage uniforme dans `[0,5 L ; 1,5 L]` vaut exactement `L`, et le témoin
    mélangé rend 131,1.
  - ⛔ **La queue haute est tronquée par construction** : la fenêtre se ferme à **203,2 µm** quand
    le p90 publié est à **311,3**. Exclure la deuxième voisine et atteindre le neuvième décile
    sont **deux exigences incompatibles** sur ce corpus — un fait sur la nappe, pas un réglage.
  - ⭐⭐ **Le verdict est cellule par cellule, contre un étalon CALCULÉ** : la lecture et son
    témoin s'écartent de **0,292** de la largeur de la fenêtre quand deux tirages **indépendants**
    s'en écarteraient de **0,293** (`W(1 − 1/√2)`), soit **99,7 %**. ⚠⚠⚠ Et le **sens** était codé en dur derrière un commentaire qui prétendait le dériver — corrigé par la force de la corrélation, ce qui a changé les sens retenus et **renforcé** le verdict. Seconde preuve sans cible : le sens n'est pas unanime (3 spires sur 9 au minoritaire) alors que les grilles publiées partagent une orientation. ⚠⚠ Ma première version
    comparait à 0,15, un nombre posé, et rendait le verdict **inverse** — remplacer un seuil
    choisi par une quantité dérivée a retourné la conclusion.
  - ⚠⚠ **Et les DÉCILES ne tranchent rien** : lecture et témoin rendent les mêmes trois quantiles.
    Le champ qui annonçait « elle bat le témoin » sur cette base a été **retiré du JSON** — deux
    verdicts contradictoires dans un même fichier sont un piège.
  - ⚠⚠⚠ **Le témoin du gabarit mélangé a une limite, mesurée** : contre une crête isolée et très
    piquée il la retrouve **quand même**, une permutation gardant la distribution des valeurs du
    gabarit. Il discrimine sur la donnée réelle, bruitée ; pas sur une fixture propre. Le témoin
    qui tranche là est un volume **sans feuille dans la fenêtre** (étalement 30,4 contre 0,7).
  - ⚠ Deux fixtures de cette batterie ne pouvaient pas discriminer, pour deux raisons
    différentes : feuilles **régulièrement espacées** (la ligne est périodique, n'importe quel
    motif y trouve la période) et volume **constant en x et y** (les vingt-quatre lignes sont la
    même ligne, donc le témoin a un échantillon de un).
  - ⛔⛔⛔ **Cinq soupçons, cinq écartés** : la fenêtre, les décalages, le gabarit, les normales,
    la longueur du pas. Le volume brut donne **un** gain, à un pas, depuis une surface déjà juste.
  - ⭐⭐⭐ **DEUX ANCRES VALENT BIEN MIEUX QU'UNE** (2026-09-06, et c'est le premier positif du
    chantier). La spire `m` reconstruite depuis une ancre de chaque côté, **56 encadrements**
    portée 4 dont 14 symétriques : branches seules **58,3** et **90,7 µm**, **encadrée 43,1** —
    sous la demi-épaisseur de 67,75, donc la feuille est tenue. Elle bat les **deux** branches sur
    **41 sur 56**, et bat aussi « la meilleure des deux » (50,3) qui demande de savoir laquelle.
  - ⭐⭐ **OÙ POSER LA SECONDE ANCRE : RÉGULIÈREMENT.** À somme de bras égale — donc à même
    écartement — la symétrie gagne : `2+2` rend **33,2 µm** contre **41,3** pour `1+3`, et `3+3`
    rend **48,6** contre **64,6** pour `2+4`.
  - ⛔ **Et un encadrement trop déséquilibré NUIT** : sur `1+4` et `2+4` il rend **pire** que sa
    meilleure branche — la branche lointaine a tant dérivé que la moyenne tire la bonne avec elle.
    ⚠⚠ **Le chiffre trompeur n'est pas publié** : le déséquilibre minimal des fautives vaut deux,
    mais `1+3` a le même et ne nuit pas. Ce qu'elles partagent est leur **bras long**, égal à la
    portée mesurée — ce corpus ne dit donc pas si c'est la longueur ou le déséquilibre.
  - ⭐⭐⭐ **ET PONDÉRER LES DEUX BRANCHES PAR LEURS BRAS RÉPARE EXACTEMENT CE QUI ÉTAIT CASSÉ.**
    Le désaccord est **symétrique**, donc il ne peut pas dire laquelle croire ; ce qui les
    distingue **sans la réponse** est la longueur du bras. Si l'erreur y croît linéairement,
    l'estimateur qui annule deux erreurs de signes opposés est l'**interpolation linéaire entre
    les ancres** — la branche au bras court pèse `bras_long / somme`, **aucun paramètre libre**.
    Résultat : **35,9 µm** contre 43,1 à parts égales, et **53,2** pour le témoin de poids
    **inversé**.
  - ⭐⭐ **Et elle répare les DEUX paires cassées** (`1+4`, `2+4`) **sans toucher aux
    symétriques**, puisqu'à bras égaux le poids vaut un demi. Un remède qui ne PEUT PAS abîmer
    les cas sains n'a pas besoin d'être vérifié sur eux. ⚠⚠ Les quatre verdicts sont exigés
    ensemble — sans « répare les cassées », « ça améliore la médiane » pourrait vouloir dire
    qu'elle a déplacé des cas déjà bons.
  - ⚠ L'hypothèse dont le poids est tiré est **vérifiée dans la batterie** : sur deux branches
    dont les dérives valent `d` et `4d` de part et d'autre, l'interpolation les annule
    exactement, la moyenne non, et le poids inversé fait pire.
  - ⭐⭐ **Le mécanisme est un BIAIS annulé** : écarts **signés** +45,3 et −82,8 µm, de signes
    opposés sur **48 encadrements sur 56**. Moyenner du bruit gagne √2 au mieux ; annuler un biais
    gagne **tout le biais**. ⚠ Le témoin : deux branches du **même côté** ont un milieu qui ne bat
    pas la plus proche.
  - ⭐⭐⭐ **Et le DÉSACCORD entre branches PRÉDIT l'erreur** (ρ = 0,409, p = 0,0018, n = 56) —
    c'est la **seule** mesure du chantier qui ne demande pas la réponse, donc un dérouleur peut la
    calculer en marchant. ⚠⚠⚠ **Ce verdict s'est inversé avec l'échantillon, dans le bon sens** :
    sur les douze encadrements symétriques seuls il ne prédisait rien (ρ = 0,28, p = 0,38). Même
    leçon que la boîte, à l'envers — **un verdict sur un petit échantillon n'est pas un verdict**,
    positif ou négatif.
  - ⚠⚠ **Ce n'est pas une méthode, c'est une BORNE** : encadrer suppose de connaître les deux
    bouts et coûte **deux** bits de supervision. Mais elle répond à la question qui décide de
    l'effort — cinq soupçons sur la mécanique du pas n'ont rien rendu, une **seconde ancre** divise
    l'erreur par 1,35, et jusqu'à ×2,3 au bras 3+4.
  - ⚠ Aucune lecture du volume. Chaque branche marche le nombre de tours de **son** bras (un
    compte commun ferait marcher l'une trop loin) et l'appariement des nuages est **spatial**, les
    deux branches venant de deux paramétrages distincts.
  - ⚠ Deux défauts de ma prose de figure, attrapés par ses propres contrôles : elle **calculait**
    un rapport absent du JSON — une figure ne doit pas inventer de nombre — et portait une
    **étoile** que la police ne rend pas, qui serait sortie en carré vide.
- **rétractations / corrections internes** :
  - ⛔⛔⛔ **« Un décalage UNIQUE par tour déroule » est RETIRÉ** (publié et retiré le
    2026-09-06). À **191 cellules et quatre tours**, le décalage unique rendait une dérive
    **négative** (−19,5 µm par tour) et était le seul des six à tenir la feuille. Au **même
    endroit**, avec le **même code**, sur **494** puis **906** cellules : **+67,3** puis
    **+56,3**. ⛔ **Un résultat qui s'inverse quand l'échantillon grandit n'était pas un
    résultat**, et il s'inverse à deux tailles indépendantes, pas une.
  - ⛔⛔ **Et une seconde revendication tombe avec** : la « longueur de pas équivalente » du
    décalage global valait 114,7 µm à 191 cellules — *« à six micromètres de la longueur ajustée
    sur les cibles »* — et vaut **161,3 µm** à 906. C'était une coïncidence de boîte.
  - ⚠⚠ **La leçon de méthode** : la boîte n'était pas un choix de résultat, c'était un choix de
    **coût** — un bloc fait 2 Mio non compressés et 384 voxels était ce qui tenait dans le cache
    du jour. Un paramètre choisi pour sa facture n'a **aucune raison** d'être neutre sur la
    mesure, donc il se balaye **avant** de conclure, pas après.
  - ⚠⚠⚠ **« Le résidu est très variable dans l'espace » est ANNULÉ** : il reposait sur un
    optimum à (−104, −120) qui touchait **le bord** de son balayage, donc sur une borne et non
    sur un déplacement. Sur 127 fenêtres les optima se serrent autour de (−24, 0). Ce qui reste
    vrai est que la fenêtre du régime du prix est **atypique**.
  - ⚠⚠ Le recoupement du plan des silhouettes avec le `dice_apres` déjà publié a **échoué deux
    fois pour deux raisons différentes**, et les deux fois c'était l'assertion qui avait tort :
    l'ancien mesure sur une **réduction 1024²**, et il **réduit avant de seuiller** — seuiller
    d'abord donne une réduction par majorité, donc un autre nombre (0,9737 contre 0,9746).
  - ⚠⚠⚠ A5 bis : « l'expérience que personne ne pouvait poser » était **faux** — elle était
    faite. Et dans la même section, « `44` mesure sur `PHerc1447` » est corrigé en
    **`PHercParis4`**, son `um_par_voxel` de 2,4 le disant.
  - ⚠⚠ Le référent avait été déclaré **absent** faute d'avoir interrogé **un seul serveur** —
    `dl.ash2txt.org` publie les 65 couches. **Quatrième fois** pour cet angle mort, et la
    première où c'est l'auteur qui le voit.
  - ⚠⚠ Les chiffres du référent étaient **gonflés de 25 à 37 %** par un centre de masse qui
    enjambait deux feuilles (`77` §12) ; bornés, `PHercParis4` cesse d'être aberrant — « ce
    n'était pas un rouleau à part, c'était l'estimateur ».
  - **B2 est testé et NON tranchable** par la voie qui semblait à portée : une dalle de volume
    de surface fait ±0,9 écart, donc **25 refus sur 36** ; sur une dalle de 3,0 écarts, le
    positif centré sur le lobe est **circulaire** et le transport d'une fenêtre à l'autre est
    **confondu par le serpentage**.
  - ⚠ Le registre déclare son propre point aveugle et **ne le comble pas tout de suite** : les
    dix documents les plus récents n'avaient aucune fiche, et « écrire dix fiches demande de
    lire dix documents pour de bon — **une fiche bâclée est pire que pas de fiche**, elle a
    l'air d'une lecture ». Ce qui est fait, c'est que la tâche ne peut plus être oubliée en
    silence.
  - ⚠ Une fausse alerte déclarée : `proximity_scroll1.json` cru manquant, il existe en
    `.jsonl` — « mon motif cherchait la mauvaise extension ».
- **preuve de lecture intégrale** :
  - ligne 2459 (après 60 % du fichier) : `chercher sur l'un et refuser sur l'autre garantit de trouver ce qui sera refusé.`
  - ligne 3151 (dernière ligne non vide) : `déjà sous deux formes, et le prior n'est pas universel.`


### docs/76_le_sens_des_indices.md
- **lignes** : 258
- **nature** : RESULTAT
- **résumé** : Ferme la tâche `A1` en répondant à la question que `73` §5 déclarait honnêtement `[je ne sais pas]` : **`w` compte-t-il depuis le centre ou depuis l'extérieur ?** Tant qu'on l'ignore, « consécutif » est une propriété des **noms** et non de la géométrie — et un prédicat d'identité qui se trompe de sens ne rate pas la moitié des cas, il les rate **tous**. Réponse : **depuis le centre vers l'extérieur**, sur les **deux** rouleaux mesurés, donc c'est une convention du projet. Le document rend en prime un écart inter-feuilles qui ne dépend d'aucun réglage de traceur, trouve **deux défauts du référent** en regardant sa propre figure, et reformule le §5.7 de l'article.
- **conclusions extractibles** :
  - Sens des indices : **95,0 %** vers l'extérieur sur `PHerc0139` (37 spires, `w023`–`w059`, 57 510 cellules) et **95,1 %** sur `PHerc0172` (44 spires, `w052`–`w095`, 54 449). ⚠ Les deux rouleaux ne partagent **ni le régime de scan, ni la disposition de publication, ni le contenu de leurs metas**, et s'accordent au dixième de point.
  - ⚠⚠⚠ **La taille de voxel ne se lit PAS dans le nom du volume** : les 37 segments d'un même rouleau en déclarent **trois** différents (`2um_srf_ds2`, `4.681um_…`, et un qui n'en porte aucun), aucun n'étant le bon — le nom porte la résolution **avant** sous-échantillonnage. Un lecteur qui parse le nom se tromperait **d'un facteur différent par segment**, rendant les spires incomparables pendant que chaque nombre resterait plausible. Le voxel se **décode du meta** : $\sqrt{\text{area\_cm2} \times 10^8 / \text{area\_vx2}} = 9{,}3620$ µm, validé par l'extérieur (9,362 µm est un régime de scan publié). **Sonde** : lire le nom fait tomber deux contrôles et l'écart devient **32,9 µm**.
  - La mesure **doit** être appariée : un rouleau écrasé donne une étendue p10–p90 de **566 voxels** (~17 feuilles) sur le rayon d'une seule spire, et l'axe erre de **2,6 mm sur 30 mm**. Deux spires ne se comparent qu'à la même hauteur et au même angle (24 tranches × 72 secteurs), centre ajusté sur l'**union**. **Sonde** : un centre par spire fait tomber le sens de 95,0 à **87,0 %**.
  - ⭐⭐ **Écart inter-feuilles sans traceur** : **154,1 µm** (p25 107, p75 218) sur des spires approuvées par des humains, contre 113 µm de l'article (⚠ dépendant de `neighbor_step`), 156 de `16`, 172,8 de l'atlas (⚠ quantifié à 17,28). **Confirmation indépendante** par `carte_segments.ecart_entre` : **155,0 / 157,4 / 177,8 µm**.
  - ⭐ **La linéarité rend « consécutif » vérifiable** : Δw = 1/2/3/5 donne 154,1 / 308,9 / 458,7 / 782,4 µm, soit ×2,00 / ×2,98 / ×5,08. ⚠ La droite est **construite sur le seul point Δw = 1**, donc elle **pose une prédiction** que les trois autres confirment — une régression ne pourrait rien contredire.
  - ⚠⚠ **Le référent a des défauts, trouvés en REGARDANT la figure** : **`w045` et `w046` sont la même surface publiée sous deux indices** (0,0 µm par les deux méthodes, 18,4 % vers l'extérieur), et `w041`→`w042` vaut une demi-feuille. `PHerc0172` en a un aussi (`w075`/`w076`) : **3 paires sur 79, ~4 %**. Un test d'identité qui supposerait que chaque paire vaut une feuille ferait passer un bon prédicteur pour un prédicteur à 94 %.
  - ⭐⭐⭐ §7 : **le traçage automatique ÉCHANTILLONNE, une segmentation curatée PAVE**. Avec le seuil de l'article (≤ 250 µm) : `PHerc1447` `auto_grown` **4 sur 14 (29 %)**, `PHerc0139` curaté **37 sur 37 (100 %)**, `PHerc0172` **44 sur 44**.
  - ⚠⚠⚠ **Et le piège est mesuré** : l'écart médian sur **toutes** les paires ne discrimine pas — 2202 µm (`PHerc1447`) contre 1901 (`PHerc0139`), **rapport 0,86, indiscernables** — parce que les paires lointaines d'une bande contiguë de 37 spires tirent la médiane. La question doit donc porter sur la **couverture**, pas sur une moyenne.
  - §6, ce que ça débloque : `A5` gagne son étalon publié — une spire approuvée de `PHerc0139` fait **38,4 cm² médian** (15,5 à 75,7 sur 34) contre le point fixe de **6,02 cm²** du cycle rogner-étendre, soit **×6,4**, et **même la plus petite spire dépasse le point fixe**.
- **rétractations / corrections internes** :
  - §6 : « ma première rédaction annonçait **21 à 39 cm²** — un chiffre lu à l'œil sur une liste tronquée, et faux dans le sens qui **minimise** le résultat. Il est désormais calculé dans le script, pas dans un terminal. »
  - §5.4, dit plutôt que tu : **une sonde sur quatre ne mord pas** — retirer le filtre des points invalides laisse tous les contrôles verts (95,0 → 94,6 %, 154,1 → 152,3 µm). Il est gardé parce qu'il est **juste**, pas parce que le résultat en dépend.
  - §7.3 : **deux sondes de conception ne mordent pas** non plus (voisin le plus lointain, segments non mesurés comptés sans voisin : 29 → 27 %). Le contraste survit à ces deux choix et **pas** au troisième, celui du piège.
  - §5 : le sens n'est établi que sur **deux** des quatre rouleaux indexés — `PHerc1667` est lacunaire (3 trous) et `PHercParis4` publie des **plages**. ⚠ `PHerc0172` a un meta dépouillé (ni `area_cm2` ni `volume`), donc son voxel vient du **chemin** et **trois contrôles sont sautés en le disant** : « un contrôle qui n'a rien à vérifier ne doit pas rendre ok ».
- **preuve de lecture intégrale** :
  - ligne 174 (après 67 % du fichier) : `vérifier ne doit pas rendre « ok ».`
  - ligne 258 (dernière ligne non vide) : `assez grand pour survivre à ces deux choix ; il ne survit pas au troisième, celui du piège.`
