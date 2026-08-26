# Ce qui reste — registre consolidé

2026-08-19. Les **34 documents** du dépôt ont été lus **intégralement** — pas grepés :
onze lecteurs, chacun couvrant ses fichiers ligne à ligne. Ils ont relevé **525** énoncés
de travail ouvert, de limite connue ou de question non tranchée, répartis sur les
34 fichiers.

⚠ **525 lignes ne font pas 525 tâches.** La plupart sont des **répétitions** : la même
limite écrite dans le document qui l'a trouvée, dans celui qui s'y appuie, et dans la
passation. Ce document les replie. Chaque entrée porte ses sources en `fichier:ligne`,
pour qu'on puisse remonter à ce qui l'a dite plutôt qu'à ce résumé.

| nature | nombre |
|---|---:|
| limite connue | 296 |
| à faire | 102 |
| question ouverte | 64 |
| non mesuré | 31 |
| en attente | 16 |
| non publié | 16 |

---

## ⭐⭐⭐ 1. Le socle non prouvé : **réparer sert-il à quelque chose ?**

C'est le reste le plus profond du dépôt, et il n'est pas au bout de la chaîne — il est
**dessous**.

> *« Une surface propre donne un meilleur texte est une affirmation **sur le pipeline**,
> et elle n'est pas prouvée. »* — `03`:137
>
> *« [Réparer] peut parfaitement être **sans effet mesurable en aval**. C'est même
> l'hypothèse nulle honnête, et **personne ne l'a testée**. »* — `03`:133

Sources : `03`:130-137 · `02`:145 · `00`:117 (*« Whether removing it improves ink,
texturing, merging or tracing has not been measured »*, cité de `windcheck` lui-même).

⚠ **Tout l'appareil d'instruments de ce dépôt suppose cette proposition.** Un instrument
qui juge une trace n'a de valeur que si la qualité de trace décide de quelque chose en
aval. Et `04` a mesuré un fait qui *va contre* l'intuition : les cellules que `windcheck`
excise sont **indiscernables**, dans le CT, du papyrus qu'il garde (52 segments,
p = 0,859, delta de Cliff −0,000).

⭐ **Et ce n'est pas une faiblesse de ce dépôt : c'est un trou du domaine.** `28` montre
que l'équipe du concours ne publie **aucun taux d'erreur de traçage**, et `27` §2 que les
deux métriques qui portent l'argument du spiral fitting ne sont pas comparables à son
concurrent. **Personne n'a mesuré ce que coûte un défaut de trace.**

**Ce qu'il faudrait** : un cas où l'on tient les deux bouts — une trace fautive, sa
version réparée, et le **même** aval appliqué aux deux. C'est exactement le lot nº 2.

> ⚠⚠ **Et une condition préalable est désormais mesurée** ([`46`](46_le_temoin_negatif.md)
> §6) : sur `PHerc1447`, l'aval est **aveugle**. Le détecteur rend la même carte à
> ρ = 0,9979 sur une face de papyrus et sur une surface qui coupe l'empilement — une
> différence bien plus grande que celle entre une trace fautive et sa réparation. **Aucune
> réparation ne peut donc montrer de gain à travers lui sur ce rouleau.**
>
> ⭐ Ça ne ferme pas le lot, ça lui donne une **condition d'entrée vérifiable avant de
> dépenser** : σ de la sortie du modèle sur le rouleau visé, rapporté aux **0,7712** qu'il
> rend là où il atteint AUC 0,925. Une inférence sur une fenêtre suffit à le savoir.

> ⚠⚠ **Et la condition est mesurée sur tout le jeu** ([`48`](48_ou_monter_lexperience.md)) :
> les **13** rouleaux qu'on sait tracer et les **3** dont la sortie publiée porte du texte
> sont des ensembles **disjoints**. Le lot n'est donc pas montable sur ce qui est en main.
>
> ⭐ Ce n'est pas une impasse, c'est une adresse : l'expérience doit être montée sur
> **`PHercParis4`** — le seul rouleau où le détecteur est mesuré directement (AUC 0,925) et
> qui publie à la fois une prédiction de surface et des segments. ⚠ Un blocage court reste,
> nommé plutôt que contourné : il publie **deux** prédictions du même scan à 2,4 µm, et
> l'appariement refuse de tirer au sort. `sonder_point.py` sur les deux le tranche.

## ⭐⭐ 2. Appliquer la correction, et montrer le gain

Le seul ⏳ du « vrai produire », nommé dans cinq documents.

Sources : `00` §9.3 et §9.4:292-298 · `01`:179 (*« A′ — fermer la boucle sur UN défaut, de
bout en bout »*) · `18` J6 · `22` R2:74 · `27`:204.

- ✅ `20` a mesuré que **l'erreur d'une trace est structurée** et que **translater ne la
  répare pas** — donc le remède est un **gauchissement**, pas un décalage.
- ⏳ Reste : **exporter le champ en coordonnées de fenêtre** (`22` R2), l'appliquer, et
  rendre les deux versions.
- ⭐ **L'obstacle écrit est tombé** : `22` disait *« la chaîne maillage → rendu n'est pas
  ici »*. VC3D est construit depuis le 2026-08-19, et `24` a fait tourner la chaîne
  complète.

## ⭐⭐ 3. Le cap : un jugement de papyrologue

Écrit comme condition de publication depuis `06` §1bis, jamais franchi.

> *« On ne publie rien sans une passe complète — rouleau déroulé, texte extrait, **soumis
> à un expert qui dise si ça fait sens** — et sur plusieurs rouleaux. »*
> — `HANDOFF` §6:423, repris `06`:56

Sources : `06`:56, 78, 293 · `08`:141-146 · `09`:104-105 · `10`:8, 152 · `HANDOFF` §6.

⚠ **La distinction que ces documents tiennent, et qu'il ne faut pas laisser glisser** :
*le modèle retrouve les traits encrés* est **mesuré** (AUC 0,92, `08`) ; *le texte est
lisible* ne l'est **pas**. Des lettres reconnaissables ne font pas un texte suivi.

⚠ Et trois juges mécaniques ont **échoué** à remplacer l'expert (`HANDOFF` §6) : Kraken
(aucun modèle entraîné sur papyri), score structurel sur région, score structurel sur
segment entier — cette dernière cause étant **définitive** : un segment de ce type ne
porte que 4 à 5 lignes, et les glyphes fusionnent au seuil du modèle.

## ⭐ 3bis. Ce que le 2026-08-20 a ouvert

Trois entrées neuves, chacune née d'une mesure de la journée.

| # | quoi | source |
|---|---|---|
| **N1** | ~~**`PHerc1203` n'a jamais eu de graine cherchée**~~ ✅ **fait le 2026-08-22** → [`25`](25_une_graine_choisie_sur_la_planeite.md) §4bis : planéité **19,84 cm²**, voisinage **9,60 cm²**, 0 auto-intersection des deux côtés. La campagne appariée passe de 12 à **13 rouleaux** et le résultat se **renforce** (10/12 p = 0,0386 → **11/13 p = 0,0225**). ⚠ Le combler a d'abord exigé de réparer un appariement surface/volume **par position**, latent sur les 2 rouleaux à plusieurs scans. ✅ **Et les six tirages faits le même jour** : `35` couvre désormais **13 rouleaux, 78 tirages**, `PHerc1203` **bascule** (1 tirage sale sur 6) et rejoint les bascules — 4/12 → **5/13**, taux **6,4 %** (IC [2,1–14,3 %]) | `35` §5 |
| **N2** | **le protocole « sélectionner sur un axe, valider sur l'autre »** | ✅ **testé le 2026-08-20** → [`37`](37_les_deux_axes_ne_saccordent_pas.md) : **1 accord sur 8**, là où le hasard en donnerait 4. Sélectionner sur la géométrie n'achète rien sur la profondeur | `35` §4 · `31` §4 |
| **N4** | ~~**choisir une référence défendable**~~ ✅ **fait le 2026-08-22** → [`47`](47_le_critere_doit_etre_relatif.md), et la réponse est que **la question se dissout**. ⚠⚠ Le rendu impose un plafond PROPORTIONNEL à sa profondeur : **13 traces sur 16** butent dessus au rendu le moins profond, donc un seuil absolu compare des plafonds et non des surfaces — la troncature de `35` dans un troisième endroit. ⚠ Et un critère sans plafond dérive quand même (`au_bord` : médiane **0,075**, max **0,450** entre les rendus 21 et 41). ⭐⭐ Il faut donc un critère **auto-référentiel**, lu à deux profondeurs comme l'exposant α, qui n'a besoin d'aucune référence. ⏳ Reste : le construire, ce qui demande des traces non censurées des deux côtés — le dépôt en a **deux** | `36` §4 |
| **N5** ⚠⚠⚠ | **nos traces n'ont aucune feuille à portée** — pas « à 311 µm de leur feuille » : le test de convergence de [`38`](38_ce_qui_bouge_avec_la_fenetre.md) montre que la distance mesurée **suit la fenêtre** (α = +1,01) là où un segment officiel ne bouge pas (α = +0,00), et à quatre spires de portée le pic n'a toujours rien trouvé. ⭐ L'objectif devient **faire converger la mesure**, pas réduire un nombre | `38` |
| **N3** | ~~**la dispersion d'aire n'est pas expliquée**~~ ✅ **mesuré le 2026-08-22** → [`35`](35_le_tirage_sur_douze_rouleaux.md) §3bis : le plafond relevé de 120 à 400 générations sur deux rouleaux plafonnés fait passer la dispersion médiane de **0,55 % à 86,00 %** — un facteur 156. **La stabilité était une troncature.** ⚠⚠ Et un second résultat non cherché : les tirages sales passent de **1/12 à 9/12** — la propreté aussi était une troncature. ⚠ Deux rouleaux, pas treize, et le coût est mesuré : à plafond relevé une trace atteint le délai de 40 min | `35` §3 |

## ⭐ 4. Publier — et la seule échéance courte du dépôt

| quoi | où | état |
|---|---|---|
| publier le dépôt (`src/tracecheck/` au minimum) et mettre son adresse dans le texte | `21`:270 | ⏳ **l'adresse n'existe pas encore** |
| revérifier chaque chiffre contre son fichier de sortie **le jour de l'envoi** | `21`:16 | ⏳ règle posée, à exécuter |
| envoyer la soumission Progress Prize | `HANDOFF` T4, `15` | ⏳ le texte existe, les figures sont à joindre |

⚠ **Échéance : 31 août 2026, 23 h 59 Pacific** (`15`:3). C'est la seule date courte ;
tout le reste vise le 25 juin 2027.

⚠⚠ **Et `15` se déclare lui-même périmé sur deux points** (`15`:153, 175) : la règle de
`19` **ne réplique pas** hors de Scroll 1, et le tri de ce qui est soumissionnable est à
refaire. À faire **avant** d'envoyer, pas après.

## 5. Les limites de portée à ne jamais laisser tomber en route

Ce sont des **résultats**, pas des dettes — mais chacun a déjà été cité hors de son
domaine au moins une fois dans ce dépôt.

| limite | mesure | source |
|---|---|---|
| la règle de `19` est une propriété du **corpus publié de Scroll 1**, pas du problème | réplication échoue sur Scroll 5 : rho −0,217, p = 0,12 | `19` §11 · `21`:96 · `HANDOFF`:284-291 |
| le « 240 → 0 » de `24` **ne réplique pas** | zéro auto-intersection des deux côtés sur 12 rouleaux | `25` · `21`:204 |
| la métrique de proximité a un **domaine de définition** | > 1 tour de couverture | `07` §7 · `HANDOFF`:401 |
| sur Scroll 4, **rien n'est lisible, et la cause est en amont du modèle** | 61 % des pics au bord de la pile | `09` §12 · `12` · `HANDOFF`:237, 257 |
| l'inventaire des treize : **dix** sans segment, pas treize | `docs/mesures/etat_rouleaux_prix.txt` | `23` §1 |
| ⭐ **la trajectoire ne répond qu'à `step_size` et à la prédiction** | trois négatifs mesurés, contrôle positif | `26` |
| ⭐ **`step_size` a un PLANCHER : ≥ 20** | un pas de 5 rend ~800 croisements/cm² **sur les deux graines** ; au-delà de 20 c'est propre sur deux graines **et** deux tirages ; entre les deux (10, 15) le résultat **se contredit avec lui-même** | `26` §9 |
| ⚠⚠ **un compte de croisements n'est pas comparable entre deux pas** | le même maillage, décimé sans que sa géométrie change, passe de 240 à 123, 72, 49. « Zéro au pas 40 » vaut donc moins que « zéro au pas 20 » | `34` §3 |
| ⚠⚠ **un verdict « propre » peut sortir sur ZÉRO paire testée** | au réglage `--maxedge` par défaut, dès que le maillage a un pas ≥ 60. Un portail bâti sur `--fail-on-crossing` laisserait tout passer | `34` §2 |
| ⚠⚠ **le classement des treize rouleaux n'existe pas** | rho de Spearman **−0,297** entre deux échantillonnages, treize rangs changés ; le témoin passe de 0 % à 4 % | `33` §4bis |
| ⭐ **le traceur est un tirage sur douze rouleaux** | 4 rouleaux sur 12 où le verdict bascule à paramètres identiques ; 0 reproductible ; et **l'aire ne signale pas** le mauvais tirage | `35` |
| ⭐⭐ **les deux axes de jugement ne se recoupent pas** | 1 accord sur 8 comparaisons, sur deux tailles de fenêtre | `37` |
| ⚠⚠ **« officiel » n'est pas synonyme de « bon »** | quatre segments publiés d'un même rouleau : 18,2 / 25,0 / 62,5 / 68,2 % de pics dans le tiers central | `36` §3 |
| ✅ **l'origine de nos piles de rendu est bonne** | le même segment officiel : 3,00 µm côté publié, 17,28 µm côté nous | `36` §2 |
| ⚠ en **zone comprimée l'information n'est pas dans le CT** | 78 % de pics uniques couvrant deux feuilles | `28` §4 · `villa#191` |
| ⚠ **aucun test géométrique** ne sépare un saut d'une spire d'une courbure, dans le cas serré | écart inter-spires 18–58 vx contre 20 vx de cellule | `28` §4 |

## 6. Les mesures nommées, non faites

| # | quoi | coût | source |
|---|---|---|---|
| M1 | rejouer le balayage `step_size` sur la **mauvaise** graine de `24` | ✅ **fait** — 4 pas sur 5 à zéro, et ça a mené à `30` | `26` §9 |
| **M1bis** | **mesurer la distribution des tirages sur d'autres graines et d'autres rouleaux** | ✅ **fait le 2026-08-20** → [`35`](35_le_tirage_sur_douze_rouleaux.md) : 78 tirages, 13 rouleaux, **5 rouleaux où le verdict bascule**, 0 reproductible, taux 6,4 % IC [2,1–14,3 %]. ⭐ Et **l'aire ne signale pas** le mauvais tirage | `30` §5 |
| **M1ter** | **l'encre est-elle lisible à 9 µm ?** | ⚠⚠ **répondu le 2026-08-20, négativement** → [`36`](36_lorigine_de_la_pile.md) §5bis : sur une **bonne** surface d'un rouleau du prix (17 µm de sa feuille), le modèle sort une **constante** — σ **45 fois** plus petit que là où il marche. ⏳ La cause n'est pas isolée : résolution, rouleau, ou papyrus vierge | `31` §10 |
| M2 | relire les 240 croisements de `24` sous un autre `--maxedge` — le filtre peut **masquer comme fabriquer** | ✅ **fait le 2026-08-20** → [`34`](34_un_verdict_qui_ne_mesure_rien.md) : les 240 survivent au filtre **désactivé**, donc ni masqués ni fabriqués. ⚠⚠ Mais le balayage a trouvé qu'un verdict « propre » peut sortir sur **zéro paire testée**, et que ça arrive **au réglage par défaut** dès que le maillage grossit | `28` §2 |
| M3 | lire le quatrième article, *EduceLab-Scrolls* (arXiv 2304.02084) | ✅ **fait le 2026-08-19** → [`32`](32_educelab_le_papier_fondateur.md) | `27` Références |
| **M7** | ~~**quantifier « consistent with »**~~ ✅ **fait le 2026-08-22** → [`45`](45_consistent_with_quantifie.md) : les quatre grandeurs mesurées sur **190 cartes d'encre publiées**, sans lire une lettre. ⭐ Deux d'entre elles retrouvent franchement le classement du contraste d'encre publié — épaisseur de trait **AUC 0,857**, netteté du pic **0,753** — ce qui est le transport de calibration du papier, enfin chiffré. ⚠⚠ Et la **séparation des lignes va CONTRE** (AUC 0,319, ρ = −0,281) : le papier met échelle, séparation et tracé dans un même souffle, et mesurées elles ne vont pas ensemble. ⏳ Reste : le transport vers une région sans vérité du **même** objet | `32` §4.2 |
| **M8** | ~~**le témoin jeté**~~ ✅ **fait le 2026-08-22** → [`46`](46_le_temoin_negatif.md). ⭐⭐ Notre témoin est meilleur que celui d'EduceLab : une trace à **α = +1,01** est une *preuve géométrique* qu'aucune feuille n'est à portée, là où « feuille de support » n'est qu'une supposition sur un substrat. ⚠⚠ La thèse forte est **hors de portée** — le détecteur est inerte sur ce rouleau (σ = 0,0129, soit **1,7 %** de ce qu'il rend là où il marche), et l'instrument REFUSE de conclure plutôt que d'imprimer un verdict faux. ⭐⭐ Une thèse plus étroite est établie : **sa sortie ne dépend pas de la présence d'une feuille** — deux entrées distinctes de **11,0 %** rendent la même carte à **ρ = +0,9979**, soit **2,9 %** d'écart contre **95,4 %** si elles étaient étrangères. ⏳ Reste : la thèse forte, qui demande un rendu à α élevé sur un rouleau où le modèle marche | `32` §4.3 |
| M4 | chercher la vraie feuille en engendrant un volume plus profond que 65 couches | à chiffrer | `12`:259 |
| M5 | revoir les sites de fusion suspects à 2,4 µm | ⚠ **impossible** : PHerc0172 ne publie que du 7,91 µm | `06` §7:613, mesure 3.6 |
| M6 | savoir si le trend *position dans le rouleau ↔ résiduel* existe | ⚠ **non établi** : trois corpus, trois motifs | `HANDOFF` §7 |

## 7. ⚠ Ce que ce registre ne remplace pas

Il replie 525 lignes en une trentaine d'entrées, donc **il perd du détail par
construction**. Les 296 « limites connues » ne sont pas toutes ici : la plupart sont des
bornes de portée écrites au bon endroit, dans le document qui les a mesurées, et elles y
sont mieux qu'ici. Ce registre sert à **ne rien oublier de ce qui demande une action** ;
il ne sert pas de substitut à la lecture d'un document avant de s'appuyer dessus.

⚠ Et il a une date. Il a été construit le 2026-08-19 à partir d'une lecture intégrale ;
**une entrée close ailleurs et pas ici devient un piège**. La règle du dépôt s'applique à
lui comme au reste : corriger sur place, en disant ce qui était écrit avant.
