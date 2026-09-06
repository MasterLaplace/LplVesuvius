# 55 — Les murs, et l'espace de causes qui rétrécit

> ⚠⚠ **Ce document est RENDU, pas écrit.** Sa source est
> [`docs/registres/murs_et_causes.tsv`](registres/murs_et_causes.tsv) et son producteur est
> `uv run python src/depot/murs_et_causes.py --rendre`. L'éditer à la main serait perdre
> la modification au rendu suivant — et surtout perdre la garde : la batterie vérifie que
> **chaque ligne pointe vers un document qui contient encore son ancre**.

Un mur n'est pas une tâche, c'est un **espace de causes** dont on retire une entrée à
la fois. Une feuille de route qui liste des tâches laisse croire qu'on avance quand on
tourne ; celle-ci liste des causes **éliminées**, et montre l'espace rétrécir. C'est le
seul progrès mesurable sur un problème que personne n'a résolu.

**49 causes candidates** sur **4 murs** : ❌ **35** éliminées · ✅ **11** confirmées · 🔒 **3** bloquées

| symbole | verdict | ce que ça veut dire |
|---|---|---|
| ❌ | **éliminée** | testée, ce n'est pas la cause |
| ✅ | **confirmée** | testée, c'en est une — ou un levier qui marche |
| ⏳ | **ouverte** | nommée, pas encore testée |
| 🔒 | **bloquée** | ne peut pas être testée aujourd'hui, et on dit pourquoi |

![l'espace de causes, mur par mur](images/55_espace_de_causes.png)

*Une case par cause, dans l'ordre du vocabulaire — donc ce qui reste à faire tombe
toujours à droite. Ce n'est **pas** une jauge de progression : rien ne dit que
l'espace est borné. Produite par `src/figures/figure_murs.py`, dont les comptes
viennent du même registre et sont vérifiés contre ce tableau.*

## 1. Le tracé ne suit pas de feuille

❌ 17 éliminées · ✅ 6 confirmées · 🔒 3 bloquées

| cause candidate | | ce qui a été mesuré | où |
|---|---|---|---|
| la graine, c'est-à-dire l'endroit | ✅ | sondée dans le volume scanné : la graine m7 n'a AUCUNE matière à ≈ 7,1 spires dans son repère ni à ≈ 8,9 converties, quand la graine ps256 est SUR de la matière dans les deux repères (0 µm) — l'endroit explique la famille m7, pas le mur | [`54`](54_cinq_rendus_vides.md) |
| le traceur accepte une graine qui ne désigne rien | ✅ | graine m7 : bloc absent du dépôt, et il trace quand même — 13 rendus noirs ; graine ps256 : bloc allumé à 100 %, 8 traces avec matière | [`54`](54_cinq_rendus_vides.md) |
| le traceur est un tirage, pas une fonction | ✅ | 13 traces propres sur 14 à paramètres identiques ; toute comparaison à un seul tirage ne vaut rien | [`30`](30_le_traceur_est_un_tirage.md) |
| ce qui est établi : la surface est EN TRAVERS de l'empilement | ✅ | des spires coupées en travers, vues à l'image à étendue égale contre une feuille publiée | [`25`](25_une_graine_choisie_sur_la_planeite.md) |
| le niveau de la prédiction n'était propagé nulle part | ✅ | trois conséquences : graine dans le vide, maillage rendu hors du scan, et min_area_cm évalué dans deux unités — les aires m7 sont fausses d'un facteur 16 | [`54`](54_cinq_rendus_vides.md) |
| lisser le champ de NORMALES avant le pas répare ce que le raccrochage abîme | ✅ | la dérive du raccrochage tombe de +56,1 à +25,3 um par tour, et le même lissage ne fait RIEN pour le pas aveugle (+22,3 contre +22,0) — donc le dégât était bien celui du raccrochage ; +26,0 / +25,8 / +25,3 aux trois tailles de boîte, le contendant le plus stable des dix | [`75`](75_registre_des_taches.md) |
| la fenêtre de lecture | ❌ | relu à 128 px × 109 couches, la géométrie du corpus : le classement ne bouge pas | [`52`](52_calibrer_sur_son_corpus.md) |
| la chaîne de rendu | ❌ | un maillage PUBLIÉ passé par notre chaîne revient à 0,873 — au-dessus de la médiane du corpus | [`53`](53_le_temoin_positif_du_rendu.md) |
| le champ de normales (NORMAL pèse 10) | ❌ | chargé pour de vrai : coût par génération ×29, trajectoire INCHANGÉE sur 118 générations | [`26`](26_le_champ_de_direction.md) |
| le plafond de générations | ❌ | budget ×3,3 : aire ×11,5, α +0,89 → +0,95, sous le bruit du tireur (0,16) | [`50`](50_le_rendu_attendait_la_memoire.md) |
| le niveau de pyramide | ❌ | 0,02 d'écart entre niveaux 0 et 1, pour une résolution de 0,20 | [`50`](50_le_rendu_attendait_la_memoire.md) |
| la prédiction de surface (ps256 contre m7) | ❌ | lues correctement, les deux familles sont indiscernables : 0,159 contre 0,164 – 0,198 | [`54`](54_cinq_rendus_vides.md) |
| le sens de la normale du rendu (--flip-normals) | ❌ | le drapeau RENUMÉROTE la pile : 41/41 couches identiques après renversement, 1/41 à l'endroit — la fenêtre est centrée sur la surface, il n'y a pas de « mauvais côté » | [`38`](38_ce_qui_bouge_avec_la_fenetre.md) |
| le classement de graine désigne le point le moins étayé | ❌ | huit candidats tracés sur PHercParis4, étai de 9 à 27 voisins et occupation 0,02 à 0,75 : ZÉRO convergence, et 7 écarts sur 8 valent exactement le bord de la fenêtre | [`48`](48_ou_monter_lexperience.md) |
| l'écart de la chaîne serait l'erreur du référent | ❌ | un biais est CONSTANT donc il s'annule dans les différences : la chaîne part à 0,3 µm et finit à 69,2, donc un biais explique au plus 0,5 %, et le référent entier au plus 4,5 % en quadrature | [`75`](75_registre_des_taches.md) |
| le pas normal d'un écart inter-feuilles ne mènerait pas à la feuille voisine | ❌ | sur 12 paires de spires publiées : ne rien faire 135 um, un écart 60 um, deux écarts 151 um — le pas nul retombe sur l'écart mesuré, le simple le divise par deux et le double dépasse, donc la distance franchie est bien celle d'une feuille ; 11 paires sur 12 | [`75`](75_registre_des_taches.md) |
| le pas normal itéré suffirait à dérouler sans recalage | ❌ | déroulement aveugle depuis la spire 1 : la feuille est perdue au tour 2 (erreur 102 um contre une demi-épaisseur de 67,75), et la dérive vaut 53 um par tour soit 39 % d'une feuille — alors qu'il bat l'immobilité aux douze tours | [`75`](75_registre_des_taches.md) |
| la dérive du pas normal viendrait d'une longueur mal estimée | ❌ | longueur ajustée sur six paires et jugée sur six réservées : 108,4 um contre 135,5 nominaux, erreur 54,1 contre 67,6 sur la moitié réservée — le biais est réel mais n'explique que 20 %, et le plancher de la courbe réservée est à 50,5 um | [`75`](75_registre_des_taches.md) |
| le raccrochage à la matière ne ferait pas mieux qu'une longueur de pas bien choisie | ❌ | sur le volume brut de PHerc0500P2, sept paires de spires : le pas normal seul laisse 46,7 um, le maximum brut d'intensité 46,1 — soit rien — et la corrélation avec le gabarit de feuille lu sur la spire de DÉPART 33,3 um, sous l'étalon de 50,5 que laisse la meilleure longueur constante ; témoins gabarit mélangé 56,6 et fenêtre d'une feuille entière 76,6 | [`75`](75_registre_des_taches.md) |
| le raccrochage point par point suffirait à dérouler | ❌ | sur 906 cellules et six tours, il dérive de +56,1 um par tour contre +22,3 pour l'aveugle, et il dérive plus que lui aux TROIS tailles de boîte mesurées (384, 512, 640 voxels) ; ni l'accord des voisins (+33,6) ni une fenêtre deux fois plus étroite (+43,0) ne le rattrapent | [`75`](75_registre_des_taches.md) |
| raccrocher par un décalage UNIQUE pour toute la nappe, un par tour | ❌ | RÉTRACTÉE le jour même : à 191 cellules la dérive sortait NÉGATIVE (-19,5 um par tour) et le décalage unique était le seul à tenir la feuille ; à 494 puis 906 cellules, au même endroit et avec le même code, elle vaut +67,3 puis +56,3 — un résultat qui s'inverse quand l'échantillon grandit n'était pas un résultat | [`75`](75_registre_des_taches.md) |
| le gain d'un pas raccroché survivrait à une surface reconstruite | ❌ | depuis une spire PUBLIÉE le raccrochage gagne +12,7 um sur le pas aveugle ; dès qu'UN seul tour aveugle a été fait il gagne -0,2 um, et sur les quatre âges suivants la médiane vaut -0,2 avec un signe qui change quatre fois — le raccrochage ne raccroche que ce qui est déjà à sa place | [`75`](75_registre_des_taches.md) |
| ce qui se dégrade sous un dérouleur raccroché est le gabarit qu'il relit | ❌ | geler le gabarit sur la spire de départ donne +54,2 um par tour contre +56,1 sans remède, et son contraste ne s'effondre pas (51, 78, 53, 40, 47, 51 au fil des six tours) : la surface ressemble encore à une feuille, c'est la DIRECTION de recherche qui se perd | [`75`](75_registre_des_taches.md) |
| comparer le relief d'une trace L2 à une trace L0 | 🔒 | à aire égale un maillage L2 rend quatre fois moins de pixels de côté, donc les deux ne tiennent jamais dans la même fenêtre d'analyse — le relief ne peut pas les départager | [`54`](54_cinq_rendus_vides.md) |
| les résidus du champ d'orientation publié (A2 ter) | 🔒 | le pas de grille publié vaut 64 voxels, soit 3,89 écarts inter-feuilles par cellule contre 0,5 exigés par Nyquist : le champ est REPLIÉ, pas bruité | [`75`](75_registre_des_taches.md) |
| bâtir le raccrochage à la matière sur les piles de surface publiées | 🔒 | la pile porte à 129,6 um autour de la surface, soit 0,956 feuille, quand la voisine est à 135,5 : il manque 5,9 um — mesuré sur 1 459 592 colonnes, avec la convention du centre vérifiée (pic à -1,5 couche) | [`75`](75_registre_des_taches.md) |

## 2. Les patchs publiés ne se recollent pas

❌ 6 éliminées · ✅ 1 confirmée

| cause candidate | | ce qui a été mesuré | où |
|---|---|---|---|
| un patch par feuille, pas par région | ✅ | la paire la plus proche est à 79 µm, soit environ deux fois le seuil de séparation | [`44`](44_ou_la_chaine_se_trouve.md) |
| raccorder deux segments officiels | ❌ | l'outil exige des surfaces qui se recouvrent, et il n'existe AUCUN candidat — mesuré sur 4,5 Mo de catalogue | [`44`](44_ou_la_chaine_se_trouve.md) |
| recaler les deux aplatissements par un champ ajusté sur leurs BORDS | ❌ | ni un modèle lisse global ni une agrégation locale (rayons 256 à 1536, 2 à 25 voisins) ne battent le champ nul sur la composante normale ; le conditionnement des directions plafonne à 0,60 pour 1 en isotropie | [`75`](75_registre_des_taches.md) |
| recaler les deux aplatissements par un CHAMP plutôt que par une translation | ❌ | sur 127 fenêtres de l'empreinte les optima se serrent autour de (−24, 0) à 27 cases près, quand les champs candidats déplacent de 60 et 40 ; une constante porte l'AUC médiane de 0,755 à 0,852 en améliorant 116 fenêtres sur 127, et l'accord publié de 0,756 à 0,857 | [`75`](75_registre_des_taches.md) |
| recaler les deux aplatissements sur le recouvrement de leurs CONTOURS | ❌ | le critère est contraire dans la plage qui compte : les trois translations qui font monter l'AUC de l'encre font toutes baisser le Dice, y compris l'optimum de l'encre dont le Dice (0,97263) est sous celui de l'affine non corrigée (0,974601) | [`75`](75_registre_des_taches.md) |
| prendre le support de la carte d'encre publiée pour un masque du fragment | ❌ | à pleine résolution le support ne porte que 36 vides intérieurs quand le masque en a 348, et réduire le support natif ×8 par la même règle rend 19 composantes de fond et non 420 : les trous du réduit sont en grande part du crénelage de .jpg | [`75`](75_registre_des_taches.md) |
| apparier les trous du masque aux vides du support publié | ❌ | contre un témoin qui garde la FORME du nuage et ne casse que sa place, la vraie position est la 6e sur 21 (p = 0,29) : le rapport de 7,7 contre un semis uniforme mesurait le groupement des repères, pas une correspondance | [`75`](75_registre_des_taches.md) |

## 3. L'extension tangentielle est un point fixe

❌ 8 éliminées · ✅ 3 confirmées

| cause candidate | | ce qui a été mesuré | où |
|---|---|---|---|
| une extension UNIQUE, puis rognage | ✅ | 4,28 → 12,97 cm² à α = +0,000, ramenée à 6,02 cm² propres, soit +41 % de matière validée | [`44`](44_ou_la_chaine_se_trouve.md) |
| la chaîne TANGENTIELLE, qui suivrait une feuille autour du tour | ✅ | elle marche, à DEUX conditions qui se composent : un pas FIXE en voxels (la géométrie) et un RECALAGE sur la matière à chaque maillon (la donnée). 60 maillons de 96 µm : pas tenu à 96,0 exactement, et +6,9 points au-dessus du plancher du hasard à 5 760 µm — là où la chaîne sans recalage est morte dès 768 (+1,5). La pente s'aplatit sur le dernier millimètre : plateau bas, pas chute. ⚠ Ne dit pas que c'est la BONNE feuille (il faut de l'encre), et part d'un segment PUBLIÉ et non d'une de nos traces | [`44`](44_ou_la_chaine_se_trouve.md) |
| enchaîner la projection à PETIT pas (95 µm/maillon) | ✅ | un LEVIER qui marche À COURTE DISTANCE, confirmé sur trois grandeurs indépendantes. À 478 µm, là où un seul bond quitte sa feuille (18,4 % de pic au bord), la chaîne y est encore (2,0 %) avec +31 % d'amplitude ; et lue contre le PLANCHER DU HASARD elle est à +30,5 points à 288 µm, +24,1 à 480, puis +1,5 à 768 — soit morte entre les deux. ⚠⚠ Le « croisement » que j'avais publié à 1 920 µm n'existe pas : chaîne ET bond y sont au niveau du hasard (−1,7 et +1,6) | [`44`](44_ou_la_chaine_se_trouve.md) |
| augmenter le budget d'un seul coup | ❌ | budget 200 : 28,6 cm² mais 25 036 auto-intersections et α = +1,313, la surface se replie sur elle-même | [`44`](44_ou_la_chaine_se_trouve.md) |
| enchaîner rogner puis étendre | ❌ | le cycle converge vers un point fixe autour de 6 cm² : chaque tour regagne ce qu'il vient de perdre | [`44`](44_ou_la_chaine_se_trouve.md) |
| juger une courbe sur trois points | ❌ | trois points donnaient « pente monotone », six « plateau puis falaise », neuf « maximum puis descente douce » — chaque forme plausible, chaque forme fausse | [`44`](44_ou_la_chaine_se_trouve.md) |
| juger la projection par un sondage de points | ❌ | bloc avec matière et valeur au point rendent le MÊME chiffre de 0 µm à 2,4 mm : un bloc fait 307 µm quand les feuilles sont à 10-20 µm | [`44`](44_ou_la_chaine_se_trouve.md) |
| enchaîner la projection à GRAND pas (238 µm/maillon) | ❌ | cinq maillons de 238 µm étalent la boîte ×2,38 à nombre de points constant, contre ×1,10 pour le bond direct — et finissent 5,33 SPIRES à côté de lui. ⚠ Le pas réel dérive avant la boîte : 238 → 963 µm par maillon | [`44`](44_ou_la_chaine_se_trouve.md) |
| l'emballement du pas d'une chaîne | ❌ | ce n'était pas l'enchaînement mais l'UNITÉ : un pas de grille couvre pas × longueur de tangente, donc un maillage qui cisaille s'envoie lui-même plus loin. À pas FIXE en voxels, vingt maillons tiennent 96,0 µm (×1,00), boîte ×1,55, 14 280 points sur 14 280 — contre ×2 692, ×4 976 545 et 615 points au pas de grille | [`44`](44_ou_la_chaine_se_trouve.md) |
| un pas contrôlé suffit-il à rester sur la feuille ? | ❌ | non, et les deux pannes sont distinctes : à pas fixe la géométrie est saine sur 20 maillons (tous les points, pas au dixième de µm) et le contact matière tombe quand même à 39,7 % dès 768 µm puis plafonne vers 35 % | [`44`](44_ou_la_chaine_se_trouve.md) |
| le recalage mesure-t-il sa propre sortie ? (circularité) | ❌ | contrôle sur la projection AVANT son recalage : +19,1 contre +19,0 à 768 µm et +15,3 contre +15,1 à 1 920 — identiques à la première décimale, alors que la demande de déplacement passe de 1,6 et 3,4 voxels à 0,06. La mesure ne dépend pas du recalage | [`44`](44_ou_la_chaine_se_trouve.md) |

## 4. La chaîne casse au sixième tour

❌ 4 éliminées · ✅ 1 confirmée

| cause candidate | | ce qui a été mesuré | où |
|---|---|---|---|
| le pas du rayon | ✅ | halvé de 1,0 à 0,5 : 4 spires convergentes sur 7 deviennent 6 sur 7, et la rupture disparaît — gratuitement | [`43`](43_la_chaine_des_spires.md) |
| halver le pas indéfiniment | ❌ | il y a un OPTIMUM à 0,25 : à 0,125 l'α moyen remonte de +0,102 à +0,327 | [`43`](43_la_chaine_des_spires.md) |
| le sens de croissance (in contre out) | ❌ | mesuré au lieu d'être supposé : ni meilleur, ni pire | [`43`](43_la_chaine_des_spires.md) |
| juger par le compte d'auto-intersections | ❌ | c'est une propriété de l'échantillonnage autant que de la surface : le même maillage décimé passe de 240 à 49 | [`43`](43_la_chaine_des_spires.md) |
| juger sur un seul rendu | ❌ | mesuré AVANT de s'en servir, et il ne marche pas | [`43`](43_la_chaine_des_spires.md) |

## Ce qui reste ouvert, tous murs confondus

⭐ C'est la seule liste courte du dépôt qui dise *par quoi continuer*.

| mur | cause | pourquoi elle est encore ouverte |
|---|---|---|
| le tracé ne suit pas de feuille | **comparer le relief d'une trace L2 à une trace L0** | à aire égale un maillage L2 rend quatre fois moins de pixels de côté, donc les deux ne tiennent jamais dans la même fenêtre d'analyse — le relief ne peut pas les départager |
| le tracé ne suit pas de feuille | **les résidus du champ d'orientation publié (A2 ter)** | le pas de grille publié vaut 64 voxels, soit 3,89 écarts inter-feuilles par cellule contre 0,5 exigés par Nyquist : le champ est REPLIÉ, pas bruité |
| le tracé ne suit pas de feuille | **bâtir le raccrochage à la matière sur les piles de surface publiées** | la pile porte à 129,6 um autour de la surface, soit 0,956 feuille, quand la voisine est à 135,5 : il manque 5,9 um — mesuré sur 1 459 592 colonnes, avec la convention du centre vérifiée (pic à -1,5 couche) |

⚠ **Une cause éliminée ne se rouvre pas sans une mesure neuve.** Les treize
éliminations de ce document ont chacune coûté une campagne ; les refaire par doute
serait payer deux fois pour le même renseignement.

⚠⚠ Et une cause **absente** de ce document n'est pas une cause éliminée : c'est une
cause à laquelle personne n'a pensé. Le tableau borne ce qu'on a testé, jamais ce qui
est possible.

