# R4 — Le déroulement : qu'est-ce qui remplace l'humain du transfert de spire à spire ?

> Rapport de campagne, écrit le **2026-09-11** d'une seule lecture des documents `archive/76`–`79`,
> `81`–`86`, `90`–`112`, `114`, `archive/75` §A/§A′ et `archive/75` §C — la campagne `0500P2` des 5–7
> septembre (lignes 1476–3835 et 6268–6738), étiquetée « C » dans le registre parce qu'elle a commencé
> par une case vide d'encre, et qui est du déroulement d'un bout à l'autre (34 documents et un cahier,
> 2026-09-03 → 2026-09-11).
> Convention : `archive/NN §k` cite la preuve ; ce rapport est la lecture. Un fait porte un statut
> (`établi` · `borné` · `réfuté` · `rétracté` · `ouvert`) et son producteur (`src/…`, JSON de même
> nom dans `docs/mesures/`). Les statuts sont ceux du **11 septembre** ; `archive/113` tourne encore.

## 0. Fiche

| | |
|---|---|
| question | l'état de l'art déroule 31 spires en ~775 h d'humain, dépensées à corriger le **transfert de spire à spire** (`archive/68` §1, `84` §1). Le prix en tolère 8. **Qu'est-ce qui remplace cet humain ?** |
| objets | `PHerc0139` (37 spires publiées), `PHerc0172` (44), **`PHercParis4`** (120 spires en 28 bandes, seule vérité de terrain du goulot), `PHerc0500P2` (l'objet courant du dépôt jusqu'au 6 septembre, 13 spires) |
| ce qui a été construit | un **champ d'enroulement** (`77`), un **masque d'approbation** écrit et accepté par `villa` (`75` A3), une **lecture par plage HTTP** des volumes distants (`77` §10, `95`), un **critère à seuil matériel** (`98`), un **marcheur** sans référent humain (`102`, `107`), et l'appareil qui l'audite (`104`–`112`) ; et, deux jours avant le marcheur, un **dérouleur aveugle sur `0500P2`** avec son oracle, ses deux ancres, sa nappe lissée et sa confiance par cellule (`75` §C) |
| ce qui a été payé en réseau | `102` 7 h · `107` 3,53 h · `110` 2050 s · `111` 1158 s · `106` 2393 s · `103` 25 min · `113` en cours (~7 h) — chaque fois pour relire les mêmes voxels, jusqu'à ce que `111` garde les profils |
| réponse au 11 septembre | **Personne encore.** Ce que la campagne a établi est *où* l'humain travaille (l'identité de la feuille, pas la qualité locale), *contre quoi* on ne peut pas le juger (le maillage humain, qui bouge d'une demi-feuille selon qui le tient), et *ce que la matière donne sans lui* (un pas et une direction, confirmés à 57 % par pas, dont on ne sait pas encore la portée : `113`) |

## 1. La réponse courte — vingt faits qui tiennent aujourd'hui

| # | fait | valeur | statut | source · producteur |
|--:|---|---|---|---|
| 1 | `w` compte du centre vers l'extérieur, sur les deux rouleaux indexés | 95,0 % (`0139`), 95,1 % (`0172`) | établi | `76` §0 · `excision/le_sens_des_indices.py` |
| 2 | écart inter-feuilles **sans traceur**, un pas d'indice = une feuille | 154,1 µm (`0139`), 147,4 (`0172`) ; linéaire en Δw (×2,00, ×2,98, ×5,08) | établi | `76` §3 |
| 3 | le référent humain a des défauts : deux indices pour une même surface | `w045`/`w046` à 0,0 µm ; 3 paires sur 79 (~4 %) | établi | `76` §4, confirmé `77` §3 |
| 4 | un champ d'enroulement sépare « même feuille » de « une feuille sautée » **sur `0139`**, pas sur `0172` | 0139 : +0,230 vs 0,753 ; 0172 : recouvrement (+0,634 vs −0,067) ; jamais sur une tranche isolée | établi (par rouleau) | `77` §2, §7 · `excision/le_champ_denroulement.py` |
| 5 | la cause sur `0172` : un **trou angulaire** 330–360°, de la matière absente | 3 points/cellule contre 286 ; sans ces 6 secteurs → sépare ; 6 secteurs sains → non | établi | `77` §8 · `le_trou_angulaire.py` |
| 6 | la surface publiée n'est pas sur la feuille : elle serpente | 0,121–0,146 feuille sur trois rouleaux (17,8–23,8 µm) | établi | `77` §10, §12 · `la_surface_et_la_feuille.py` |
| 7 | l'axe seul ne fait pas un nombre d'enroulement ; la forme des spires vaut ×130 | Archimède 11,36 feuilles d'erreur, champ 0,088 | réfuté (modèle axe+pas) | `78` §4 · `laxe_ne_suffit_pas.py` |
| 8 | aucun seuil d'intensité ne sépare les feuilles | plus gros morceau 93–100 % contre 14,1 % attendu, 6 seuils, 2 régions | établi | `79` · `rendu/topologie_du_volume.py` |
| 9 | **les 13 rouleaux du Grand Prize publient 0 rang de spire** ; 11 publient 0 segment | Paris4 120, 0172 44, 0139 37, 1667 14 (suite), 0500P2 13 | établi | `81` §1 · `depot/les_spires_consecutives_publiees.py` |
| 10 | toutes les portées publiées avant le 6 septembre étaient **censurées** par le corpus (plafond 6 = spires 10→11 à 7,4 feuilles) | oracle = plafond sur 5/5 ancres ; borne réelle inconnue, ≥ 6 | borné | `82` · `nappe/le_mur_du_corpus.py` |
| 11 | `PHercParis4` est la seule vérité de terrain du goulot | 92 franchissements dans une maille ; 0 partout ailleurs ; plus longue bande 18 < 31 | établi | `84` · `depot/une_surface_combien_de_spires.py` |
| 12 | le coût humain se compte en **longueur de feuille** : ~360 mm par passe | 362 mm médian (273–460) sous l'axe courbe | établi | `85` §2, révisé `90` §3 |
| 13 | **l'axe est une courbe** : un repère cylindrique global se trompe de ~2 cm | 12,6 mm en x, 19,8 en y sur 144 mm de z ; 11,6 mm hors de sa droite = 63,9 feuilles | établi | `90` · `nappe/laxe_est_une_courbe.py` |
| 14 | pas de `PHercParis4` par deux instruments indépendants ; demi-feuille établie | 164 µm (transferts humains) vs 182,4 (atlas `winding-ruler`) ; demi-feuille 82–91 µm | établi | `91` §3, `86` §3 |
| 15 | **deux humains sur la même matière divergent de plus d'une demi-feuille, partout** | 121,7 / 110,9 / 106,6 µm par tiers ; 34 % des points à > 1 feuille ; ρ(rayon) = +0,081 | établi | `97` · `nappe/deux_humains_sur_la_meme_matiere.py` |
| 16 | la normale de la matière est à **34,6°** du rayon (spirale : 0,09°) ; le maillage humain la suit à 13° | 34,59° (tenseur, volume seul) recoupe 34,06° (maillage) | établi | `101` §2, `100` §2 |
| 17 | la matière n'est **pas** un empilement localement parallèle à l'échelle sondée (346 µm) | résidu 19,3 µm contre 0,72 sur pile fabriquée (×22,3) | établi | `106` §4 · `nappe/le_pas_selon_la_direction.py` |
| 18 | le critère « un pas confirmé » accepte de 0,68 à 1,38 feuille ; le sélecteur de production lisait **+18,4 %** trop haut | 120 pas confirmés = 82 à 166 spires ; brut 164,3 µm vs calibré 194,6 | établi | `104` §3, `105` §6 |
| 19 | un pas non confirmé n'est **pas** une chute ; la « portée » publiée était un run consécutif | confirmés médiane 4,0/6 contre run 1,0 ; manques non groupés (p = 0,28) | rétracté (la portée), établi (le test) | `109` · `nappe/un_pas_manque_nest_pas_une_chute.py` |
| 20 | dans le mode qui compte, **le compte suit le pas** ; la « falaise » du mode bas était celle de l'instrument | 1,012 → 1,085 feuille/pas ; bande bornée : mode bas −0,888 → −0,068 | établi | `110` §5, `111` §5 |

Et le seul résultat de la campagne qui rouvre une cause éliminée : brancher l'indice d'enroulement dans
le coût du tracker polaire ne rachète que **0,5 % du chemin** — un faux champ tourné prend 83 % du
gain (`114`, `excision/le_cout_qui_connait_la_spire.py`, statut **réfuté**).

### 1 bis. La campagne `0500P2` — dix faits de plus (`75` §C, 5–7 septembre)

Le premier dérouleur du dépôt a tourné sur les **13 spires publiées** de `PHerc0500P2`, deux jours
avant que `81` ne montre que ce corpus plafonne à 6 bras. Ses résultats sont mesurés sur **un pas**
(de la spire *k* à la spire *k* + 1, une spire publiée pour cible) puis sur une **marche** (repartir
de sa propre prédiction). Producteurs dans `src/nappe/`, figures dans `src/figures/figure_<nom>.py`.

| # | fait | valeur | statut | source · producteur |
|--:|---|---|---|---|
| 21 | un écart le long de la **normale** de la surface prédite tombe près de la spire suivante : la primitive du déroulement | 60 µm de la cible (ne rien faire 135 ; deux écarts 151) ; 11/12 paires ; le même sens pour les 12 | établi | `75` §C (l. 1606) · `le_pas_normal_atteint_la_spire.py` |
| 22 | un dérouleur **aveugle** (normales seules) perd la feuille au **deuxième tour** | erreur 52 / 102 / 135 / 230 / 689 µm à 1 / 2 / 3 / 6 / 12 tours ; dérive 53 µm par tour = 39 % d'une feuille ; un cinquième est un biais de longueur (135,5 nominale, 108,4 ajustée) | établi | `75` §C (l. 1647, 1698) · `derouler_par_le_pas_normal.py`, `la_derive_est_elle_un_biais.py` |
| 23 | le raccrochage à la matière (volume brut, gabarit du profil de départ) gagne sur **un pas** et **ne survit pas à un tour** | 33,3 µm contre 46,7 ; à l'itération l'aveugle (+22,3 µm/tour) bat tous les raccrochages ; « un décalage unique déroule » **rétracté** (la boîte était un choix de coût : −19,5 / +67,3 / +56,3 selon sa taille) | établi ; rétracté | `75` §C (l. 1791, 1886, 1905) · `le_raccrochage_a_la_matiere.py`, `derouler_en_raccrochant.py` |
| 24 | **deux ancres** qui encadrent, pondérées par les bras, valent mieux qu'une ; la troisième ne paie pas | 35,9 µm (une ancre 42,7 ; « meilleure des deux » 50,3) ; mécanisme = un biais qui s'annule (+45,3 / −82,8) ; 2 → 3 → 4 ancres : 36,7 → 35,5 → 35,3 ; « la dérive accélère » **rétracté** | établi (c'est une borne à 2 bits de supervision, pas une méthode) | `75` §C (l. 2164, 2303) · `derouler_des_deux_bords.py`, `combien_dancres.py` |
| 25 | l'itération ne paie que de la **nappe** : un seul grand pas fait la même erreur avec 48 % de cellules en plus | bras 4 : 132,1 contre 134,1 µm ; 996 contre 671 cellules ; le premier pas (44,2 µm) est le poste | établi | `75` §C (l. 2425) |
| 26 | la **géométrie ne refuse rien** : l'oracle dans la même fenêtre prend 23,8 µm ; le raccrochage lit très peu | −23,8 µm, 7/7, IC [−25,2 ; −21,1] ; ρ(raccrochage, oracle) 0,076 sur 5 442 cellules ; 16 gabarits essayés : le meilleur vaut **0,9 µm** sur les 30,7 qui séparent le déployé de l'oracle | établi (le plus solide de la campagne) | `75` §C (l. 2665, 2770, 2817) · `lecart_apparie.py`, `le_gabarit_lu_ailleurs.py` |
| 27 | le critère **déployé** bat l'immobilité sur un pas, et tout son gain vient du **voisinage** ; la lissité est épuisée au 3×3 ; la moitié du coût d'un pas est un plancher de **direction** | 37,5 contre 43,6 µm (7/8, [−2,2 ; −1,9]) ; corrélation seule −0,2 ; oracle 20,0 ; plancher 18,2 µm = 48,5 % ; rotation d'ensemble −0,1 µm ; surfaces lisses par construction pires (+3,5 à +4,0) | établi ; « tourner le pas » et « lisse par construction » réfutés | `75` §C (l. 2932, 3045, 3137, 3232, 3313) · `le_critere_du_raccrochage.py`, `loracle_est_il_atteignable.py`, `le_champ_lisse_par_construction.py` |
| 28 | **sur une marche**, le raccrochage déployé porte **moins loin** que le pas normal seul ; lisser la **nappe** entre deux bras achète un bras sans réglage | portées 2 / 4 / **5** (raccrochage / pas normal / pas normal + nappe lissée), borne 6, corpus 6 ; −6,7 µm, 7/8, [−11,0 ; −2,4] ; le gain tient sur 5 ancres (−3,1 à −8,6), le bras gagné sur une seule | établi (le gain) ; borné (le bras) | `75` §C (l. 3453, 3616, 3664) · `la_portee_du_raccrochage.py`, `la_portee_tient_elle_ailleurs.py` |
| 29 | le **pli** et l'**obscurité** disent à une cellule qu'elle a tort sans regarder la cible, et le lissage retire le premier signal ; refuser ses plis ne gagne **exactement rien** sur les cellules communes | pli : −43,2 µm à moitié gardée chez le raccrochage (8/8), +7,1 chez le pas normal lissé ; obscurité : −13,1 (7/8) chez le lissé ; refus : écart apparié +0,0 [0,0 ; 0,0], part gardée 0,453 | établi | `75` §C (l. 6268, 6343, 6458) · `la_cellule_sait_elle_quelle_a_tort.py` |
| 30 | le froissement du pas normal **n'est pas distribué** (0 → 33 % de cellules pliées pendant que la médiane reste à ~20 µm) ; lisser en retire 80 % ; la borne se froisse aussi (63 %) en gardant 17–22 µm | pliées au bras 8 : 32,8 / 6,5 / 96,6 / 62,8 % (pas normal / lissé / raccrochage / oracle) ; « combien lisser » : −26,0 µm hors échantillon 4/5, mais l'ancre vivante passe de 5 à **0** bras → porte fermée par défaut | établi ; borné | `75` §C (l. 6513, 6610) · `ou_la_nappe_se_froisse.py`, `combien_lisser_la_nappe.py` |

Et la voie de l'**orientation** est fermée par la donnée : les fibres sont publiées pour `0139`, `0332`,
`1299`, `1451`, `PHercParis4`, les spires pour `0500P2` seul — intersection vide sur les deux serveurs
(`75` §C l. 3388, `ou_vit_le_champ_de_fibres.py`). C'est ce qui a désigné `PHercParis4` (fibres +
`ink-3d`) comme objet, avant que `81`–`84` ne le confirment par le goulot.

## 2. La campagne en six mouvements

```
 M1 le référent          76 77 78 79 · 75 A1–A3        3–5 sept.
 M1′ le dérouleur aveugle 75 §C (0500P2, 13 spires)     5–7 sept.
 M2 le corpus est le mur 81 82 83 84 85 86             6–7 sept.
 M3 ce que l'humain fait 90 91 92 93 94 95 96 97        8 sept.
 M4 interroger la matière 98 99 100 101 102 103        9–10 sept.
 M5 l'instrument s'audite 104 105 106 107 108 109 110 111 112   10–11 sept.
 M6 rouvrir, et lever le plafond 114 · 113 (en cours)  11 sept.
```

**M1 — Le référent.** Les spires publiées portent un indice ; personne ne l'avait lu. `76` mesure son
sens et en tire un écart inter-feuilles sans traceur. `77` en fait un prédicat d'identité (le champ
d'enroulement), le mesure sur un rouleau (sépare), puis sur le second (ne sépare pas), trouve la cause
**en regardant** (un trou de matière), écrit le masque d'approbation que l'article annonçait (`75` A3),
et découvre en coupe que la surface publiée serpente sous la feuille (§10). `78` trouve cinq axes
publiés et montre qu'ils ne suffisent pas. `79` ferme la voie du seuil. **Ce mouvement établit que le
référent est bon à une feuille près et faux en dessous** — et qu'il faut l'avoir mesuré contre lui-même
pour le savoir.

![Une tranche dépliée : 37 spires emboîtées sur PHerc0139, et le faisceau qui se croise entre 330° et 360° sur PHerc0172](../article/figures/spires_a_plat.png)

*`archive/77` §8 — `src/figures/figure_les_spires_vues_a_plat.py`. Le trou de matière qui empêche le prédicat de séparer sur le second rouleau, vu au premier coup d'œil et non par les quatre statistiques testées avant.*

**M1′ — Le dérouleur aveugle sur `0500P2`.** Le 5 septembre, en cherchant où remplir une case vide
d'encre, l'index publie **treize spires** consécutives de `PHerc0500P2` que rien n'avait ouvertes
(cinquième fois de l'angle mort ; l'auteur : *« regarde sur les autres serveurs »*). En deux jours la
campagne va d'une primitive (un écart le long de la normale atterrit à 60 µm de la spire suivante) à
un dérouleur qui perd la feuille au deuxième tour, puis à tout ce qui aurait pu le sauver et qui est
mesuré **apparié, sur un pas et sur une marche** : le raccrochage à la matière gagne 13 µm sur un pas
et ne survit pas à un tour ; deux ancres encadrantes valent 35,9 µm et la troisième ne paie pas ;
l'oracle prend 23,8 µm dans la même fenêtre pendant que seize gabarits en rendent 0,9 ; la moitié du
coût d'un pas est un plancher de direction que rien le long de la normale n'atteint ; et **sur une
marche, le raccrochage porte moins loin que ne rien faire** (2 bras contre 4), parce que l'erreur
devient la surface où le bras suivant estime ses normales. Ce qui sort de là est le marcheur le plus
simple du dépôt — **pas normal + nappe lissée, 5 bras sur 6** — un gain constant sur cinq ancres, un
bras gagné sur une seule, et la première distinction entre *« quelle méthode fait le meilleur pas »*
et *« quelle méthode va le plus loin »*, qui sont deux questions avec deux réponses. La campagne
s'arrête sur le mur que `81`–`82` nomment le lendemain : le corpus de `0500P2` ne demande que six
bras, et le septième vaut 7,4 feuilles.

![Jusqu'où la marche va avant d'être plus près de la mauvaise feuille : raccrochage 2, pas normal 4, borne 6](../images/75_la_portee_du_raccrochage.png)

*`archive/75` §C l. 3453 — `src/figures/figure_la_portee_du_raccrochage.py` (17 contrôles). Le raccrochage qui gagne sur un pas perd sur une marche : les deux questions ne sont pas la même.*

![Où la nappe se froisse : une tache est une cellule plus près de la feuille voisine que du plan de ses propres voisins](../images/75_ou_la_nappe_se_froisse.png)

*`archive/75` §C l. 6513 — `src/figures/figure_ou_la_nappe_se_froisse.py` (11 contrôles). Une médiane dit combien ; cette carte dit où — et le froissement du pas normal commence à zéro et atteint un tiers des cellules pendant que sa médiane ne bouge pas.*

**M2 — Le corpus est le mur.** En cherchant sur quel rouleau du prix mesurer, `81` découvre qu'aucun
ne publie de rang de spire, et qu'un « 6 » cité depuis des semaines est un trou géométrique dans une
numérotation continue. `82` relit deux JSON déjà publiés et montre que toutes les portées du dépôt
étaient **censurées à droite**. `83` déplace la boîte 1 296 fois : le fragment est mauvais partout.
`84` compte les franchissements contenus dans une maille : Paris4 en a 92, tout le reste zéro. `85` et
`86` chiffrent le sens du rang et la demi-feuille. **Ce mouvement change d'objet de fait** — la
décision formelle reste à l'auteur (`81` §6).

![Sur quel objet peut-on vérifier trente et une spires : les treize rouleaux du prix publient zéro rang](../images/81_les_spires_consecutives.png)

*`archive/81` — `src/figures/figure_les_spires_consecutives.py`. Compter des segments ferait croire que deux des treize sont exploitables ; compter des rangs dit que zéro l'est.*

**M3 — Ce que l'humain a produit.** Sur les 28 bandes humaines de Paris4 : l'axe est une courbe
(`90`), le pas vaut 164 µm (`91`), la continuité casse au bord ×31 (`92`), les spires sont parallèles
au milieu et désalignées au bord (`93`). Trois candidats de **signal de confiance** échouent : le pli
est anti-prédictif (`94`), la pose sur la matière aussi (`95`), la fermeture d'un tour a le bon signe
mais ne se calibre pas (`96`). `97` explique pourquoi : deux humains divergent d'une demi-feuille
partout. **La cible d'un automate ne peut pas être « égaler le maillage humain ».**

![Deux humains sur la même matière : le désaccord est plat à travers les rayons, et supérieur à une demi-feuille partout](../images/97_deux_humains_sur_la_meme_matiere.png)

*`archive/97` — `src/figures/figure_deux_humains_sur_la_meme_matiere.py`. Le plancher que `95` et `96` nommaient sans pouvoir le chiffrer.*

**M4 — Interroger la matière.** `98` construit le premier critère dont le seuil vient d'un modèle nul
et non d'un maillage ; `99` le retourne en décision (quel pas ?) ; `100` réfute l'explication évidente
d'un écart et trouve une obliquité de 34° ; `101` montre par le volume seul que l'obliquité est celle
de la matière ; `102` enchaîne pas et direction sans référent humain et **bat l'automate naïf**
(2 pas contre 0) ; `103` réfute l'économie de lecture. Premier acquis positif, censuré par un plafond
de six pas.

![La direction que la matière montre : à 34,6° du rayon, à 13° du maillage humain, sur les 28 bandes](../images/101_la_direction_que_la_matiere_montre.png)

*`archive/101` — `src/figures/figure_la_direction_que_la_matiere_montre.py`. Avec le pas de `99`, les deux nombres qu'un automate doit connaître pour franchir une feuille sans humain.*

**M5 — L'instrument s'audite.** `104` mesure que le critère accepte 0,68–1,38 feuille par pas
confirmé ; `105` que le sélecteur lit +18,4 % trop haut ; `106` que la périodicité suivie n'est pas
l'espacement d'un empilement parallèle. `107` refait la marche avec le bon pas, garde les étapes, et
trouve deux populations ; `108` ce qui les sépare ; `109` que la portée publiée était une lecture du
critère ; `110` que le compte suit le pas dans le mode qui compte ; `111` que la bimodalité était
**instrumentale** (un plancher de fréquence relatif à la fenêtre) ; `112` pourquoi le remède ne
descend pas au pas. Neuf documents, aucune lecture neuve pour six d'entre eux.

![La falaise était celle de l'instrument : les mêmes profils sous la bande relative et sous la bande bornée par la physique](../images/111_une_bande_qui_ne_bouge_pas_avec_la_fenetre.png)

*`archive/111` — `src/figures/figure_une_bande_qui_ne_bouge_pas_avec_la_fenetre.py`. Le mode qui « ne comptait rien » franchit 0,951 feuille par pas.*

**M6 — Rouvrir, et lever le plafond.** `114` rouvre légitimement une cause éliminée (`55` exige une
mesure neuve : le champ d'enroulement en est une) et répond non. `113` lève le plafond de pas de 6 à
20 depuis les mêmes départs que `107`, en gardant départ, étapes et profils — parce que **56 marches
sur 56 avaient touché le plafond** et que la portée n'avait donc jamais été mesurée.

![Le coût qui connaît la spire : le champ tourné, faux par construction, obtient 83 % de la descente du vrai](../images/114_le_cout_qui_connait_la_spire.png)

*`archive/114` — `src/figures/figure_le_cout_qui_connait_la_spire.py`. La réouverture était légitime, la réponse est non : 0,5 % du chemin.*

## 3. Chronologie, document par document

Format : *question → résultat · statut · ce que ça déplace*. Les producteurs sont dans `src/nappe/`
sauf mention ; le JSON porte le même nom dans `docs/mesures/`.

**`75` §C · 2026-09-05 → 07 · la campagne `0500P2`** (`les_wraps_publies.py`, `le_pas_normal_atteint_la_spire.py`,
`derouler_par_le_pas_normal.py`, `le_raccrochage_a_la_matiere.py`, `derouler_en_raccrochant.py`,
`derouler_des_deux_bords.py`, `combien_dancres.py`, `le_cout_dun_seul_pas.py`, `lecart_apparie.py`,
`le_gabarit_lu_ailleurs.py`, `le_critere_du_raccrochage.py`, `la_lissite_de_la_feuille.py`,
`loracle_est_il_atteignable.py`, `la_direction_du_pas.py`, `le_champ_lisse_par_construction.py`,
`ou_vit_le_champ_de_fibres.py`, `la_portee_du_raccrochage.py`, `la_portee_tient_elle_ailleurs.py`,
`la_cellule_sait_elle_quelle_a_tort.py`, `ou_la_nappe_se_froisse.py`, `combien_lisser_la_nappe.py`)
Treize spires publiées, écart voisines 135,5 µm (12 paires ; 4 anormales : 232, 292, 327, 65 µm) ; le
segment de la case vide est ailleurs (2 134 µm = 15,7 feuilles). Faits 21–30 du §1 bis. Ce qui a été
fermé, dans l'ordre : le raccrochage itéré, la lecture de la longueur locale (ce qui revient est un
tirage uniforme dans la fenêtre : 0,292 contre 0,293 attendu), la troisième ancre, la parabole,
l'écart déjà franchi comme prédicteur (ρ −0,119), seize gabarits, la lissité au-delà du 3×3, la
rotation du pas, les surfaces lisses par construction, l'orientation (donnée absente), « combien
lisser » (l'ancre vivante meurt). Ce qui a été ouvert : la confiance par cellule (pli, obscurité), le
critère d'arrêt observable sans cible. → désigne `PHercParis4` ; rejoint par `81`–`84`.

**`76` · 2026-09-04 · le sens des indices** (`excision/le_sens_des_indices.py`, `paver_ou_echantillonner.py`)
`w` compte vers l'extérieur (95,0 / 95,1 %) ; un pas d'indice = 154,1 µm (`0139`), 147,4 (`0172`) ;
le voxel ne se lit pas dans le nom du volume (3 noms pour 37 segments) mais se décode de
`area_cm2/area_vx2` = 9,362 µm. Rouleau écrasé : p10–p90 du rayon d'une spire = 566 vx (~17
feuilles). Défauts du référent : `w045`/`w046` même surface, `w041`/`w042` demi-feuille, `0172`
`w075`/`w076`. Une spire approuvée fait 38,4 cm² (×6,4 le point fixe rogner-étendre de 6,02). §7 : le
traçage automatique **échantillonne** (1447 : 29 % avec une voisine), la curation **pave** (100 %) —
la médiane toutes paires ne discrimine pas (2202 vs 1901 µm). → corrige l'article §5.7 ; ouvre A2.

**`77` · 2026-09-04/05 · le prédicat d'identité** (`excision/le_champ_denroulement.py`,
`le_masque_dapprobation.py`, `le_trou_angulaire.py`, `extraire_la_spire_suivante.py`,
`la_surface_et_la_feuille.py`, `alpha_et_le_placement.py`, `volume/couches_distantes.py`,
`nappe/le_volume_du_maillage.py`)
La grandeur est l'**avance d'indice sur un tour** (pas l'étendue : une spire spirale d'un écart par
tour). `0139` : spire −0,005 [−0,170 ; +0,230], saut d'une feuille 1,103 [0,753 ; 1,479] — séparées
sur la spire entière, sur 2 tranches au moins, jamais sur une. Les deux sauts fabriqués qui ne
montent pas sont exactement les défauts de `76`. `0172` : la rampe se reproduit (0,02/1,07/2,00/2,98)
mais les populations se recouvrent ; quatre causes testées n'expliquent pas (couverture, dérive de
l'axe jusqu'à 106 feuilles par tranche, spires par cellule, monotonie) ; §8 la figure montre un
**trou** 330–360° (7 spires sur 43 à 0 %) ; l'écarter restaure la séparation à 16 tranches, écarter
6 secteurs sains non ; coût 8 % de circonférence. Masque `approval.tif` (§6) : deux prédicats —
placement (partie fractionnaire, seuil 0,30) et identité (avance, 0,45) ; quart de pas approuvé
92,7 %, demi-pas 2,1 %, saut 0,0 % ; retirer la spire qui borne fait passer le demi-pas à 37,6 %
(bug corrigé). §9 : le champ porte **une feuille** au-delà du bord (47 µm = 0,31), c'est un juge pas
un générateur. §10/§12 : la surface publiée est à 0,121–0,146 feuille de la matière sur trois
rouleaux ; première version gonflée de 25–37 % par un centre de masse qui enjambait deux feuilles.
§11 : α ne se calcule pas sur un volume de surface, et sur 65 couches le positif est soit circulaire
soit confondu par le serpentage — **B2 reste ouverte**. Correction du 09-05 : `PHercParis4` publie
cinq volumes, aucun à 7,91 µm ; celui de `44` est à 2,400 (seul contenant du maillage).
→ ferme A1, A2 (par rouleau), A3 ; ouvre A2 bis.

**`78` · 2026-09-04/05 · l'ombilic publié** (`excision/lombilic_publie.py`, `laxe_ne_suffit_pas.py`,
`nappe/le_champ_de_fibres.py`)
Cinq rouleaux publient un axe (`0125`, `0139` 391 pts, `0211`, `0332`, `0826`) ; le centre ajusté en
diffère de 3,01 mm médian, et la mesure appariée n'en bouge pas (94,8 % / 155,8 → 156,8 µm) :
l'immunité vient de l'appariement, pas du centre. §4 : Archimède (axe + pas) rend 11,36 feuilles
d'erreur, le champ des spires 0,088 — la **forme** vaut ×130. Fibres publiées : `nx`, `ny`,
`presence` (pas de `nz` ; |nz| récupérable, signe perdu), niveaux 3–4 seulement (19,2 µm : 7,8
cellules par pas). → A2 bis borné par la résolution.

**`79` · 2026-09-05 · aucun seuil ne sépare les feuilles** (`rendu/topologie_du_volume.py`)
Attendu dérivé : 128 × 7,910 / 142,8 = 7,09 feuilles par chunk → plus gros morceau 14,1 % ; mesuré
93,2–100 % à six seuils, centre et bord, 6-connexité. 97,4 % des voxels non nuls entre 128 et 176.
Le profil radial du niveau 5 (σ ×5 vers l'extérieur) était un artefact de la taille du voxel.
→ interdit l'isosurface ; le calcul que `00` §10.3 renvoyait hors de l'arbre est dans l'arbre.

**`81` · 2026-09-06 · le rouleau désigné ne publie rien** (`depot/les_spires_consecutives_publiees.py`,
`ce_que_les_serveurs_publient.py`)
Treize rouleaux du prix : 0 rang de spire (11 sans segment ; `0800` et `1447` en `auto_grown`
sans rang). Suites : Paris4 120 (intervalles `w010-027`…), `0172` 44, `0139` 37, `1667` 14,
`0500P2` 13. Le « 6 » de `la_portee_du_raccrochage` n'est pas 13/2 : le bras 10→11 demande
1000,6 µm = 7,4 feuilles. Compter des noms n'est pas compter des voisines. → la décision de `31` §10
(choisir un des 13 par la part comprimée) n'est ni dans le budget (×315) ni exécutable ; le
changement d'objet est à l'auteur.

**`82` · 2026-09-06 · la borne était le mur** (`le_mur_du_corpus.py`, hors ligne)
Oracle = plafond du corpus sur 5/5 ancres (10 − ancre) ; « la borne vaut 6 » devient « ≥ 6, inconnue ».
Ce qui tient : à l'ancre 4, pas normal 4 < lissé 5 < plafond 6, donc le gain du lissage n'est pas
touché. **Rétracté** : « il ne reste qu'un bras de marge ».

**`83` · 2026-09-06 · le corpus, pas la boîte** (`ou_poser_la_boite.py`)
1 296 placements : meilleur plafond 8 (minorant : treillis 480 → 7, 240 → 8) ; 597 sans un bras ;
40 % des 8 589 bras hors pas nominal (2 226 lacunes, 1 169 doublons) ; la paire 10→11 varie de
19,4 à 1 224,8 µm selon la boîte (×63). Déplacer la boîte rend +2 bras, sans changer d'objet.

**`84` · 2026-09-07 · une surface, combien de spires** (`depot/une_surface_combien_de_spires.py`)
Paris4 : 28 bandes, 120 spires, 4,29 spires par surface, plus longue 18 → **92 franchissements
contenus dans une maille** ; les cinq autres objets : 1 spire par surface, 0. Longueurs 18 10 8 7 6
5 5 4 4 4 4 4 3×9 2×7, monotones, sans trou = la courbe de coût du déroulage manuel. 18 < 31.

**`85` · 2026-09-07 · le sens du rang** (`le_sens_du_rang.py`, `tifxyz-transformed` à 45,532 µm)
27/27 montées de rayon (7,41 mm au rang 10 → 24,84 au rang 128). Une passe humaine couvre une
longueur de feuille à peu près constante ; 9 paliers de quantification. **Rétracté par `90`** : le
« second régime » de la bande du cœur (838 mm) était une erreur d'axe. Limite de grille dite : cellules
à 905 µm, le pas inter-feuilles ne se lit pas dessus.

**`86` · 2026-09-07 · la demi-feuille par objet** (`la_demi_feuille_par_objet.py`, atlas
`winding-ruler`, 36 objets)
Le 135,5 µm du dépôt (12 paires de `0500P2`) est au **percentile 27** de l'atlas du même fragment
(196,6 médian, p25 131,1) : les portées 4/5/6 sont des bornes basses (+45 % de tolérance à la
médiane). Paris4 : 91,2 µm ; les 13 du prix : 86,4–103,7 (×1,20) — la géométrie ne désigne aucun
rouleau. Ce n'est pas une contradiction, c'est une population (local vs fragment) ; l'atlas surestime.

**`90` · 2026-09-08 · l'axe est une courbe** (`laxe_est_une_courbe.py`)
Centre par tranche : 12,6 mm en x, 19,8 en y sur 144 mm, en revenant sur ses pas ; 11,6 mm hors de
sa droite = 63,9 feuilles. 100 % des 36 secteurs occupés par tranche (pas un artefact). Sous l'axe
courbe : 27/27, longueur par passe 362 mm (273–460, ×1,68). Verdict de courbure en épaisseurs de
feuille (droit 1,0, courbé 14,1). → aucun repère global ne remplace l'humain ; le remplaçant est local.

**`91` · 2026-09-08 · le pas lu sur les transferts** (`le_pas_lu_sur_les_transferts.py`)
L'étendue déclarée d'une bande est son nombre de tours mesuré (−0,01 tour médian ; 27/28 à moins de
0,1 ; exception `w010-027` : 12,75 pour 18). Pas 164 µm (136–207) vs 182,4 à l'atlas : deux
instruments sans rien en commun, à 10 %. **Rétracté avant publication** : un gradient « 1000 µm au
bord », artefact de fenêtre (pente sur 10/6/4/3/2/1 tours d'une même bande : 202/208/224/287/523/1817).

**`92` · 2026-09-08 · la continuité des transferts** (`la_continuite_des_transferts.py`)
Plus grand saut entre cellules voisines / pas d'échantillonnage : cœur 1,7, milieu 5,9, bord 31,0.
Même un humain rend une surface discontinue au bord. Corrélation sauts↔gonflement 0,80 mais retirer
les lignes à saut change la pente de 0,2 % : **pas la cause**.

**`93` · 2026-09-08 · où les spires sont parallèles** (`deux_modes_dechec_du_transfert.py`)
Rapport désalignement un tour / adjacent : `w073-076` (14 mm) ×1,23 ; `w128-129` (24 mm) ×4,18 ;
`w010-027` non résolue (27 colonnes par tour). En U, minimal au milieu. Les deux modes d'échec
(brisé, désaligné) sont au **bord**. Faute gardée : comparer la bande 0 à la bande 7 en l'appelant
« le bord » inversait la conclusion.

**`94` · 2026-09-08 · le froissement mesure la rugosité** (`le_froissement_mesure_la_rugosite.py`)
Pli médian : cœur 15,2 µm, bord 3,8 — anti-prédictif (ρ −0,957 rayon, −0,825 rupture). Fixture : le
champ est aveugle à la courbure lisse et mesure la rugosité (×1,1 entre R = 5 et 20 mm) ; le réel
chute ×5,2 → les maillages humains sont **cinq fois plus lisses au bord** : signature d'un pontage.
Sagitta (accord 1,11 médian) réfutée par la fixture (prédit 20,2 µm où le champ rend 0). Ne rétracte
pas `75` (pli prédictif par cellule à rayon constant) ; **tout signal de confiance se vérifie à
travers les rayons** (une marche de 31 spires change le rayon ×6).

**`95` · 2026-09-08 · la surface et la feuille par rayon** (`la_surface_et_la_feuille_par_rayon.py`,
`commun/voxel_distant.py`)
Dispersion surface↔ruban à 2,4 µm : cœur 20,0 µm, bord 13,85 — la surface est **mieux posée là où le
transfert casse** (ρ −0,702 ; partielle masque retiré −0,550 ; tient de 5 à 30 % de remplissage). Le
volume fin est une nécessité mesurée (à 45,5 µm un demi-écart = 2 voxels). **Motif nommé** : au bord,
l'humain trace proprement *une autre feuille* ; ce qui échoue est l'**identité**, qu'aucune observable
locale ne peut voir. Défaut d'outillage : un résultat qui bougeait entre deux runs (coupures réseau
silencieuses, 65 cellules sur 90) → réessais et compte publié.

**`96` · 2026-09-08 · la fermeture d'un tour** (`la_fermeture_dun_tour.py`)
Part de cellules hors demi-feuille après un tour : 0,621 cœur, 0,804 bord (ρ +0,858 rayon) — premier
signal au bon signe ; le pas est juste partout (0,95–1,02). Immune à l'ovalité. Bruit ou structure :
fenêtre ×5 → réel −11 %, bruit → 0 : **structure**. Mais 62 % d'échec au cœur, là où tout est intact :
un référent qui ne ferme pas lui-même ne calibre rien.

**`97` · 2026-09-08 · deux humains sur la même matière** (`deux_humains_sur_la_meme_matiere.py`)
Désaccord au plan local : 121,7 / 110,9 / 106,6 µm par tiers (plat, ρ +0,081) ; hors demi-feuille
0,61–0,63 ; > 1 feuille 0,30–0,34 ; aucune translation systématique (8–38 µm). Plus proche voisin
réfuté (270–315 µm : limite de grille). Ne corrèle ni au rayon, ni à la rupture, ni à la fermeture de
`96`. **La cible d'un automate ne peut pas être le maillage humain** ; `94`–`96` mesuraient contre
une règle qui bouge d'une demi-feuille selon qui la tient.

**`98` · 2026-09-09 · combien d'interstices** (`combien_dinterstices_traverses.py`)
Gabarit *brillant–sombre–brillant*, corrélation normalisée (sans seuil d'amplitude : l'étendue varie
×146 dans une bande) ; barre = p99 du bruit blanc = 0,331. Par tiers : la matière répond 0,740 /
0,690 / 0,540 ; ρ rupture −0,411 (bon signe, faible). La cellule part **sur** la feuille une fois
sur deux (marge franche). Réfuté : compteur de minima proéminents (invariant d'échelle → aucun point
de fonctionnement). **Réfuté par `104`** (la quantité) : la famille {1, 2, 3} ne dit jamais « moins
d'une feuille » ; remplacée par `feuilles_franchies` (continu, cos θ à 0,0022).

**`99` · 2026-09-09 · le pas que la matière montre** (`le_pas_que_la_matiere_montre.py`)
Le même filtre balaie la distance (moitié → double du nominal, k = 1). Premier résultat, 147 µm,
**identique sur du bruit pur** : un nul pour chaque quantité rapportée, pas seulement la confiance
(nul par candidat 0,158 → 0,093) ; comparaisons multiples (62 essais : barre 0,331 → 4,357 σ). Après
calibration : 198,9 µm cœur, 214,05 bord ; > 81 % des cellules à plus de 10 % du nominal ; KS réel
vs nul D = 0,603. La part « matière répond » corrèle **−0,845** à la rupture — le signal au bon signe
le plus fort. **Biaisé** (`105`) : le sélecteur calibré lit +18,4 % trop haut ; corrigé 164,3 µm.

**`100` · 2026-09-09 · la normale n'est pas le rayon** (`la_normale_nest_pas_le_rayon.py`)
L'explication « obliquité » de l'écart de `99` (1/cos = 1,212 vs 1,213 observé) est **réfutée** : pas
radial / pas normal = 1,018 vs 1,184 prédit ; ρ(rapport, 1/cos) = +0,153 ; l'instrument voit une
obliquité fabriquée (35° → 1,238). Fait plus lourd : la normale du maillage est à **34,1°** du rayon
(ACP 33,6°) où une spirale en prédit 0,09° ; plateau à 21° avec 1000 voisins ; 14,6° hors plan,
24,0° dans le plan. Corrige `98` (« segment ⟂ empilement » faux ; ce qui le sauve : le pas ne dépend
pas de la direction, raison inexpliquée). `106` reprend : l'anomalie survit (1,000 vs 1,155).

**`101` · 2026-09-09 · la direction que la matière montre** (`la_direction_que_la_matiere_montre.py`)
Tenseur de structure à 2,4 µm, cube de 98,4 µm : la matière est à 13,32° du maillage et **34,59°** du
rayon (recoupe `100`) ; orientée sur 63,6 % des cellules. Axe décalé réfuté par sa signature 1/r
(résidu 12,2° contre 8,7° pour une obliquité constante). Planarité réfutée comme juge (le bruit ×6 du
signal laisse la direction juste) → garde = accord des deux moitiés du cube (barre 8,88°) ;
`np.gradient` injectait une anisotropie au bord (nul 10,4° au lieu de 62°). À rayon tenu, la part
orientée suit la rupture (+0,452) : **la direction survit là où le pas ne survit pas**. Le maillage
humain est juste en orientation (13°), faux en identité (`97`) : deux pannes, une fatale.

**`102` · 2026-09-10 · combien de pas la matière porte** (`combien_de_pas_la_matiere_porte.py`, 7 h)
Pas confirmés consécutifs : matière **2,00** vs automate naïf **0,00** (médiane de médianes, 4
cellules par bande) ; 583,9 µm portés ; 0 sortie du volume ; aucun référent humain dans la boucle
(direction `101`, pas `99`, vérification `98`). Témoin : à 0° naïf = matière = 6. **Censuré** :
17/28 bandes au plafond de 6 pas (budget : 15,4 s par cube). Première vérification **incapable
d'échouer** (le balayage trouvait 211 µm dans la fenêtre → naïf 8/8) → `99` décide, `98` vérifie à
gabarit fixe. Statut du « 2,00 » au 11 septembre : **rétracté comme portée** (`109`), borne inférieure
d'une lecture du critère.

**`103` · 2026-09-10 · le cube lu moins cher** (`le_cube_lu_moins_cher.py`)
Un voxel sur deux : ×1,72 de gain (pas ×7,44 : le coût suit les plages d'octets, plancher 3,76 s)
mais 7,3 % des cellules à plus de 10° → 36,5 % des marches de six pas abîmées. **Réfuté.** La sonde
sur deux bandes disait 0 %.

**`104` · 2026-09-10 · un pas confirmé n'est pas une feuille** (`un_pas_confirme_nest_pas_une_feuille.py`, hors ligne)
Bande d'acceptation du critère de `102` : 0,68–1,38 feuille (0,72–1,32 à σ = 30 ; indépendante du
bruit = pouvoir de la forme) → 120 pas confirmés = 82 à 166 spires ; le retard est invisible, le saut
visible ; les quatre pas publiés (164, 173, 199, 214 µm) tombent tous dans la bande. Leçon chiffrée :
**un agrégat ne se désagrège pas** — `102` a marché 224 fois et gardé une médiane par bande, sa survie
n'est bornée qu'à 0,5 près. Le registre passe avant la portée.

**`105` · 2026-09-10 · le balayage rend-il le pas injecté** (`le_balayage_rend_il_le_pas_injecte.py`)
Sur profils fabriqués : brut +0,0016, calibré +0,050 (jusqu'à +0,112). Mécanisme : le nul par
candidat décroît avec la longueur, la calibration favorise les longs (retient 181,7 pour 173 injectés
avec un accord 0,9882 < 1,0000) — deux questions, une statistique. Le contrôle de `99` relisait le
sélecteur brut, pas celui de la production. Apparié sur le vrai volume (28 × 120, mêmes lectures) :
brut 164,3 / calibré 194,6 / deux rôles 164,3 (**+18,4 %**, 28/28 bandes) ; 164,3 = même case de
grille que les transferts humains (164,0). Le marcheur de `102` franchissait 1,184 feuille par pas
(120 pas = 142 spires), **dans** la bande de `104`. `99`–`102` non recalculés.

**`106` · 2026-09-10 · le pas selon la direction** (`le_pas_selon_la_direction.py`, éventail ±50°)
Modèle parallèle contre constante, un paramètre chacun, normale de `101` imposée : ∥ gagne 70 %,
gain ×1,355, résidu 19,30 µm contre **0,72** sur pile fabriquée (×22,3) ; amplitude 173 µm mesurée
vs 85 prédits. L'anomalie de `100` survit (1,000 vs 1,155). Réfuté : incohérence d'orientation sur la
sonde (le rapport monte). Fautes gardées : normale non orientée (rayon écrêté au bord de l'éventail =
limite de grille), médiane signée d'angle lue comme un accord (+2,50° pour 25,0° en absolu).

**`107` · 2026-09-10 · le marcheur avec le bon pas** (`le_marcheur_avec_le_bon_pas.py`, 3,53 h, étapes gardées)
Pas corrigé : 1,0 pas confirmés contre 1,0 (5/28 au plafond). **Le risque par pas baisse** : 0,382
(pas 1–3) → 0,105 (4–6), ×3,63, p = 0,042 — « la difficulté est de s'accrocher, pas de porter ».
Registre du trajet : 10 trajets à 1,08 feuille par pas, 14 à 0,125, même partage pour les deux
sélecteurs ; le score du **trajet** est plus haut pour les mauvaises (0,483 vs 0,371). Lire le cube
moins souvent refusé (la direction tourne de 10,12° par pas, barre 8,88°). Coût d'une étape : 55 s
(38 seul, 58,5 sous contention exclu). **Revu par `109` et `111`** : la portée est un run consécutif ;
les deux populations sont surtout celles de l'instrument.

**`108` · 2026-09-10 · ce qui sépare les deux populations** (`ce_qui_separe_les_deux_populations.py`, hors ligne)
Onze candidats déclarés avant, permutation sur le maximum (sans correction : 42,7 % de faux gagnants
sur du bruit). Deux survivent : score médian du **balayage** (force 0,664, p 0,0008) et accord de
l'interstice (0,563). Contraste : le score du pas (230 µm) sépare à l'endroit, celui du trajet
(1250 µm) à l'envers — une dérive lente s'ajuste mieux sur une longue fenêtre. Trois pas suffisent
(p 0,010), un non. Le mode qui ne compte rien marche **plus loin** (1276 vs 1189 µm). **Revu par
`111`** : le fait tient (il prédit quand l'estimateur non borné perd le signal), l'interprétation et
« repartir après trois pas » tombent.

**`109` · 2026-09-10 · un pas non confirmé n'est pas une chute** (`un_pas_manque_nest_pas_une_chute.py`, hors ligne)
Sur les 56 marches de `107` : confirmés médiane **4,0** contre run **1,0** ; 24 marches à 5–6/6 dont
6 créditées 0–1. Le run est déterminé par le taux (0,5744). Manques **non groupés** : rafale 2,286 vs
2,213 sous l'indépendance à même taux (p 0,28 ; mode haut p 0,59 ; nul à taux commun aurait dit
groupés, p 0,001 — faux sur fixture). Les marches entièrement confirmées dépassent (+0,292 feuille
par pas : troisième route vers `104`/`105`). Survie de 120 spires si « chute » : 2,7e-9 ; si
« manque » : 18 confirmations manquées. Ne prouve pas 120 spires.

**`110` · 2026-09-10 · le compte suit-il le pas** (`le_compte_suit_il_le_pas.py`, 56 lectures)
Préfixes des polylignes de `107` (départ re-dérivé, graine 613 : 48/56 reproduisent). Mode qui compte :
1,012 → 1,085 feuille par pas (+0,073, 9/22 baissent) — **aucun biais**. Mode bas : 1,008 → 0,12.
Ensemble : 1,008 → 0,199 (−42 spires sur 120) = **artefact de mélange**. Une dérive seule reproduit la
falaise sur une périodicité intacte (4/12 ; 0,128 vs 0,12) → observation indistinguable. 20 min
perdues par un `KeyError` d'agrégation → écrire les lectures avant le verdict.

**`111` · 2026-09-10 · une bande qui ne bouge pas avec la fenêtre** (`une_bande_qui_ne_bouge_pas_avec_la_fenetre.py`, profils gardés)
Le plancher `F_MIN = 0,35` de `98` est relatif à la fenêtre (λ admise 1314 µm à 2 pas, 3943 à 6).
Bande bornée par λ physiques (86,5–346 µm, les candidats de `105`), aucune ligne de `98` réécrite :
le mode bas passe de −0,888 à **−0,068** et franchit 0,951 feuille par pas ; écart entre modes
+0,965 → +0,134 ; ensemble −0,809 → −0,032. Prix : une bande étroite ne dit plus « pas de
périodicité » par son compte (dérive seule → 0,84 plausible) ; c'est le **score** qui écarte (0,28 →
0,02), et sa barre **baisse** avec la longueur (0,2874 → 0,1725 : 1/√n l'emporte). Dette : `99`–`110`
mesurés avec la bande non bornée.

**`112` · 2026-09-11 · pourquoi le remède ne descend pas au pas** (`pourquoi_le_remede_ne_descend_pas_au_pas.py`, hors ligne)
Sur un segment d'un pas (208 µm), f_lo = 0,6021 : aucun mode de Fourier retirable, le premier mode
**est** le signal → gain exactement 0 sur cinq dérives (contamination jusqu'à 0,34). Possible dès
2 pas (L ≥ λmax = 346 µm). Fautes de base : polynôme de degré 2 absorbe 0,9585 du gabarit ; grille
harmonique non entière 1,0 (rang par SVD, pas `qr`). Sur les segments réels : +6 à +9 points au-dessus
de la barre dès 2 pas, mais une fenêtre longue confirme moins souvent (0,607 vs 0,69).

**`114` · 2026-09-11 · le coût qui connaît la spire** (`excision/le_cout_qui_connait_la_spire.py`, 29 s)
Réouverture légitime (`55`) : l'indice d'enroulement dans le coût du tracker polaire (`0172`,
z = 6967, bande r 1563–3000, 72 murs par colonne). Morceaux par mur : témoin 99,12, champ 96,14,
constant 99,12, **tourné (faux) 96,64** → part spécifique 0,50 sur 98,1 = **0,5 % du chemin**.
Condition de mort passée : 1,006 feuille par pas d'indice (2342 pas, secteur par secteur ; 78
négatifs = section écrasée). Trois défauts attrapés par sonde : témoin translaté = no-op, métrique
`traversantes` dégénérée (0 partout), verdict OUI sur inégalité stricte. ⚠ Les 12 249 « fusions » de
`fusions_0172.json` sont des changements d'étiquette d'un tracker antérieur : **ne plus les citer**.
→ l'identité ne se récupère pas dans une coupe ; la question retourne en 3D (conservation de flot aux
jonctions d'une nappe).

**`113` · lancé le 2026-09-10, en cours** (`jusquou_va_t_il_si_on_le_laisse.py`)
56 marches sur 56 de `107` ont touché le plafond de 6 pas, zéro sortie du volume : rien n'a jamais
arrêté une marche, la portée est **entièrement censurée**. Plafond levé à 20 pas (~4,5 mm, l'ordre
auquel la chaîne de `44` tient), mêmes départs, départ + étapes + profils gardés. Ce qu'elle dira : le
registre et le taux de confirmation **en fonction de la profondeur**. Brouillon écrit après chaque bande
(`docs/mesures/jusquou_va_t_il_si_on_le_laisse.json`).

## 4. Le tableau des statuts

| statut | faits |
|---|---|
| **établi** | #1–6, 8, 9, 11–17, 20 du §1 ; pas d'indice = 1,006 feuille (`114` §2) ; bande d'acceptation 0,68–1,38 (`104`) ; biais du sélecteur +18,4 % (`105`) ; manques non groupés (`109`) ; falaise instrumentale (`111`) ; le champ est un juge, pas un générateur (`77` §9) ; la chaîne glisse, elle ne saute pas, et la dérive n'est pas le référent (`75` A5 bis) ; faits 21–30 du §1 bis ; l'oracle est plat (rugosité 0,00 contre 3,48 pour le raccrochage, `75` §C l. 3185) ; le froissement est une condition, le défaut de recalage la cause (`75` §C l. 6559) |
| **borné** | portée d'un marcheur aveugle : ≥ 6 bras (`82`) ; plafond du fragment `0500P2` : ≥ 8 (`83`) ; « la matière porte » ≥ 2 pas (`102`), ≥ 4 confirmés sur 6 (`109`) ; portée de `107` : 1,0 (17,9 % au plafond) ; le champ d'enroulement porte 1 feuille hors bande (`77` §9) ; A2 bis borné par la résolution des fibres (7,8 cellules par pas), A2 ter par le pas des grilles (Nyquist : 8,23 vx exigés, 64 publiés) ; la portée de `0500P2` par la boîte : 8 pas quelle que soit la boîte ≥ 960 (`75` §C l. 2895) ; le bras gagné par la nappe lissée : une ancre sur cinq (`75` §C l. 3664) ; « combien lisser » : `median_8` porte 6 à l'ancre 4 mais hors échantillon 0 (`75` §C l. 6610) |
| **réfuté** | le seuil d'intensité (`79`) ; Archimède axe+pas (`78` §4) ; le pli comme confiance (`94`) ; la pose sur la matière comme confiance (`95`) ; le plus proche voisin comme désaccord (`97` §4) ; le compteur de minima (`98` §7) ; l'obliquité comme cause de l'écart de pas (`100`) ; l'axe décalé comme cause de l'obliquité (`101` §3) ; l'économie de lecture (`103`) ; lire le cube moins souvent (`107` §5) ; l'incohérence d'orientation (`106` §6) ; le coût qui connaît la spire (`114`) ; couture, contiguïté (`77` §8) ; sagitta (`94` §5) ; ovale, centre décalé, sauts comme cause du gonflement (`91` §5, `92` §5) ; le polynôme et la grille harmonique comme base (`112` §4) ; le raccrochage itéré (`75` §C l. 1886) ; la lecture de la longueur locale (l. 2083) ; la 3ᵉ ancre et la parabole (l. 2303, 2400) ; l'écart déjà franchi (l. 2576) ; la rotation du pas et l'oracle de direction comme borne (l. 3232) ; être lisse comme recette (l. 3313) ; refuser ses plis comme gain de méthode (l. 6458) ; l'orientation, par la donnée (l. 3388) |
| **rétracté** | « la borne vaut 6 » et « un bras de marge » (`82`) ; le second régime de `85` (`90`) ; le gradient de pas au bord (`91` §4) ; le §10 de `77` gonflé de 25–37 % (`77` §12) ; « deux volumes à 7,91 µm » (`77` §10) ; « seul Scroll 1 publie un axe » (`78` §0) ; `nz` publié (`78` §2) ; « la matière porte deux pas » comme portée (`102` → `109`) ; les deux populations de `107` et « repartir après trois pas » (`108` → `111`) ; le biais de −42 spires (`110` §4) ; « la barre monte avec la longueur » (`111` §4) ; 12 249 fusions (`114` §1) ; « l'expérience que personne ne pouvait poser » (`75` A5 bis, déjà faite par `44`) ; « un décalage unique par tour déroule » (`75` §C l. 1905) ; « la dérive accélère » (l. 2360) ; « le déplacement d'ensemble du raccrochage nuit » et « gain de 5,6 µm sur l'immobilité » (l. 2702, 2770, après appariement) ; l'extension du gain d'un pas à un déroulement (l. 3453) ; « il ne glisse pas donc rien ne se compose » (l. 3616 : la nappe se froisse par les normales, 0 → 19,9 µm) |
| **ouvert** | voir §8 |

## 5. Contradictions et corrections internes à la campagne

Chaque ligne : *A a dit · B a dit · C tranche · statut*. À reporter dans `REGISTRE_contradictions.md`.

| A | B | C | statut |
|---|---|---|---|
| `77` §2 : « les deux populations ne se recouvrent pas » (propriété du prédicat) | `77` §7 : sur `0172` elles se recouvrent | `77` §8 : un trou de matière ; le prédicat rapporte sa `separation` par rouleau | tranché : propriété du **rouleau** |
| `77` §10 : référent à 23–38 µm ; Paris4 « à part » (37,7) | `77` §12 : le centre de masse enjambait deux feuilles | borné à ±0,5 écart : 17,8–23,8 µm, Paris4 dans la distribution | tranché |
| `77` §10 : Paris4 publie deux volumes à 7,91 µm | `77` (09-05) : cinq volumes, aucun à 7,91 ; 7,91 est le voxel de `0172` | `le_volume_du_maillage.py` : un seul volume contient le maillage de `44`, 2,400 µm | tranché ; `couverture_publiee.py` reconstructible |
| `laxe_nest_pas_une_ligne.py` : seul Scroll 1 publie un ombilic | `78` §0 : cinq rouleaux, sur le bucket | angle mort d'un seul serveur, 3ᵉ fois | tranché |
| `78` §2 : fibres en `nx/ny/nz` | `78` (09-05), `75` A2 bis : `nx/ny/presence`, niveaux 3–4 | ce qui borne est la résolution, pas `nz` | tranché |
| `la_portee_du_raccrochage` : borne oracle 6 | `82` : 6 = plafond du corpus sur 5/5 ancres | censure à droite ; borne ≥ 6 | tranché ; `81` §3 bis : le 6 n'est pas 13/2 |
| `85` : second régime de la bande du cœur (838 mm) | `90` : axe = courbe ; 460 mm | rétractation portée en tête de `85` | tranché |
| `91` (brouillon) : le pas quadruple au bord | `91` §4 : artefact de fenêtre | contrôle sur une seule bande de dix tours | tranché avant publication |
| `92` : sauts ↔ gonflement r = 0,80 | `92` §5 : retirer les lignes à saut change la pente de 0,2 % | corrélation ≠ mécanisme | tranché ; cause du gonflement **ouverte** |
| `93` (exploration) : désaligné au cœur, parallèle au bord | `93` §5 : les deux bandes comparées étaient dans le tiers intérieur | par tiers sur le corpus entier : U | tranché |
| `94` (brouillon) : la sagitta explique le pli en 1/R (accord 1,11) | `94` §5 : fixture → 0 là où la sagitta prédit 20,2 µm | gardée nommée | tranché |
| `94` attribuait le pli prédictif à `78` | c'est `75` (section « une cellule peut-elle savoir ») | citation non vérifiée = inventée | tranché |
| `75` A5 bis : « juger la chaîne par l'identité, expérience que personne ne pouvait poser » | `44` l'avait faite : la chaîne glisse | lecture des fiches, sur renvoi de l'auteur | tranché |
| `75` A5 bis : `44` mesure sur `1447` | `44` mesure sur `PHercParis4` (2,4 µm) | vérifié dans le code | tranché |
| `98` docstring : « le segment radial traverse l'empilement perpendiculairement » | `100` : la normale est à 34° du rayon | ce qui sauve `98` : le pas ne dépend pas de la direction (raison ouverte) | tranché, cause ouverte |
| `99` (brouillon) : le pas que la matière montre = 147 µm | le bruit pur rend 147 aussi | nul par candidat, comparaisons multiples → 198,9 | tranché |
| `99` : 198,9 µm (×1,15 nominal) | `105` : sélecteur biaisé +18,4 % ; corrigé 164,3 (×0,95) | `99`–`102` non recalculés ; le sens de l'écart s'inverse | tranché ; écart 164/182 **ouvert** |
| `100` : 1/cos explique l'écart (1,212 vs 1,213) | `100` §6 : rapport 1,018 vs 1,184 ; `106` : 1,000 vs 1,155 | coïncidence numérique | tranché ; anomalie **ouverte** |
| `102` : la matière porte 2,00 pas | `109` : run consécutif depuis le départ ; confirmés 4,0 | le compte ne peut pas dire « cinq sur six » | tranché ; portée → `113` |
| `102` : le critère confirme un pas | `104` : il confirme 0,68–1,38 feuille | `feuilles_franchies` (continu) | tranché |
| `107` : deux populations de la matière | `111` : surtout celles de l'instrument (bande relative) | mêmes échantillons, bande bornée : écart +0,965 → +0,134 | tranché ; le mode bas reste plus bas **en score** |
| `107` : « un seuil de score écarterait le bon mode » | `108` : c'est le score du **pas** qui sépare à l'endroit | `111` : ce score prédisait quand l'estimateur non borné perd le signal | tranché ; conséquence opérationnelle tombée |
| `107` : (1 − 0,105)^120 = 2·10⁻⁶ | `109` : suppose « manque = chute », réfuté | 18 confirmations manquées, pas une mort | tranché |
| `110` §4 : biais de −42 spires sur 120 | `110` §5 : mélange dont les proportions changent | partage par mode | tranché |
| `111` docstring : la barre monte avec la longueur | `111` §4 : elle baisse (pente −0,1149) | 1/√n l'emporte sur l'élargissement | tranché |
| `114` (brouillon) : témoin « décalé d'une spire », verdict OUI | `114` §5 : no-op par construction ; inégalité stricte | rotation de secteurs ; critère dérivé | tranché |
| `fusions_0172.json` : 12 249 fusions, 735 ruptures | `114` §1 : changements d'étiquette du tracker d'avant | ne plus citer comme fait sur le rouleau | tranché |
| `75` §C : le raccrochage gagne 33,3 µm sur un pas | `75` §C l. 1886 : à l'itération l'aveugle bat tous les raccrochages | le gain ne survit pas à un tour ; les normales, puis leur dispersion comme symptôme (4 soupçons écartés) | tranché |
| `75` §C l. 1905 : un décalage unique par tour déroule (−19,5 µm) | 494 cellules : +67,3 ; 906 : +56,3 | la boîte était un choix de coût | rétracté le jour même |
| `75` §C l. 2360 : la dérive accélère | le critère omettait l'incrément 0 → 1 (41,1 / 22,0 / 37,7 / 48,6) ; coût par tour stable 31,6–37,4 | erreur au bras k < k × bras 1 | rétracté |
| `75` §C l. 2665 : quatre affirmations sur la lecture du raccrochage | l. 2770 : `lecart_apparie.py` | trois tombent (gain 5,6 µm : −1,2 [enjambe 0] ; déplacement d'ensemble : +1,0), une est renforcée (oracle −23,8, 7/7) | tranché ; règle : différence de médianes → écart apparié |
| `75` §C l. 2932 : les deux tranches précédentes jugeaient le raccrochage | le critère mesuré n'était pas celui qui tourne (cellules au hasard, accord de voisinage inappelable) | déployé 37,5 vs 43,6 ; le gain est le voisinage | tranché |
| `75` §C l. 3137 : l'oracle de direction par cellule est une borne | l. 3267 : 96,6 % des cellules choisissent le **bord** du cône | plancher de balayage, pas une borne | tranché |
| `75` §C l. 3185 : la vérité est plate, donc lisser est la recette | l. 3313 : surfaces lisses par construction pires (+3,5 à +4,0) | nécessaire, jamais suffisant | tranché |
| `75` §C : le raccrochage déployé gagne (un pas) | l. 3453 : il porte 2 bras contre 4 (une marche) | deux questions : le meilleur pas ≠ aller le plus loin | tranché |
| `75` §C l. 3453 : fenêtre d'acceptation ±100,6 µm ; glissement 22 µm/bras | rectifié : ±67,8 µm (une demi-feuille exactement) ; 14 µm/bras | ce qui dérive est la somme | tranché |
| `75` §C l. 3616 : le pas normal ne glisse pas donc rien ne se compose | sa nappe se froisse par les normales (0 → 19,9 µm) | la mauvaise grandeur | tranché |
| `75` §C l. 6458 : refuser ses plis porte 5 (58,0 µm) | écart apparié sur les cellules communes +0,0 [0,0 ; 0,0] ; part gardée 0,453 | arbitrage couverture / justesse, pas gain de méthode | tranché |
| `75` §C l. 6498 : `rien_elague` et `rien_lisse_elague` mesurés | leur rugosité de champ était celle du raccrochage : ils tournaient dans la mauvaise branche | `FAMILLE_DU_PAS_NORMAL` + 2 contrôles | tranché (attrapé par une sortie de contrôle) |
| `75` §C l. 6610 : `median_8` optimal, −26 µm hors échantillon | l'optimum était au bord de la famille ; étendue à 16/32 ; l'ancre vivante passe de 5 à 0 bras | porte fermée par défaut : trois conditions | tranché |
| `31` §10 : la carte des 13 décide avec 50 fenêtres | `75` §C l. 3756 : 315× le budget ; puis l. 3836 : 0 rang de spire sur 13, pas exécutable | critère non mesurable, puis sans objet | tranché |
| `HANDOFF`:567 publie **1,213** sans record (`chiffres_sans_record`) ; `HANDOFF`:3210, :3222 `cd experiments`, `cd inference_xpu` (dossiers disparus) ; `86` §4 et les fiches lient `33_incertitude_de_la_carte.md`, qui n'a jamais existé (`33` s'appelle `la_carte_nest_pas_resolue`) | — | archive gelée : notés, non corrigés | à noter |

## 6. Les lois que la campagne a payées

À reporter dans `FILS_ROUGES.md`, avec le nombre de fois payé.

1. **Une limite de grille publiée comme une limite matérielle** — `81` §5 (filtre `tifxyz`), `82`
   (plafond du corpus), `83` (treillis), `85` §4 (905 µm), `97` §4 (plus proche voisin), `99` §7
   (butée), `106` §5 (éventail écrêté). Sept fois en huit jours.
2. **Une vérification qui ne peut pas échouer, ou qui n'emprunte pas le chemin de production** —
   `93` §7 (`--verifier` vert, `main()` planté), `102` §5 (naïf 8/8), `105` §2 (sélecteur brut audité,
   calibré en production), `114` §5 (inégalité stricte, témoin no-op), `104` §1 (au premier lancement).
3. **Un bord se compte sur le corpus entier, pas sur les bandes sondées** — `93` §5, `95` §6, `96`
   §7, `103` §4 (0 % sur 2 bandes, 7,3 % sur 28), `105` §6 (+6,75 % → +18,4 %).
4. **Une corrélation n'est pas un mécanisme** — `92` §5 (r = 0,80), `94` §5 (sagitta, 1,11), `100`
   §1 (1/cos, 1,212 vs 1,213). Le remède est toujours une fixture dont on connaît la réponse.
5. **Un nul pour chaque quantité rapportée, et chaque famille porte sa barre** — `99` §3 (la longueur
   choisie), `99` §4 (comparaisons multiples), `104` §6 (0,4018 vs 0,3475), `111` §4 (par longueur),
   `112` §7 (après retrait).
6. **Un agrégat ne se désagrège pas** — `102` (7 h, une médiane par bande), `107` (étapes sans départ),
   `110` (préfixes sans profils), `111` (profils gardés : toute relecture devient gratuite). Et
   `--reagreger` dès le premier jet (`110` §10).
7. **Une médiane sur un mélange n'est pas un résumé** — `107` §4 (0,199 feuille par pas), `110` §5
   (−42 spires), `108` §8 (loi en U → la moyenne).
8. **Un plafond n'est pas une valeur** — `82`, `83`, `102` §6, `107`, `113`. Publier le compte des
   censurés à côté du chiffre.
9. **Chercher dehors ce qu'on croit absent** — `77` §10 (65 couches sur l'autre serveur, sur
   insistance de l'auteur), `78` §0 (cinq axes), `86` (l'atlas dans `data/repos/`). Sixième fois pour
   le dépôt.
10. **Un signal de confiance se vérifie à travers les rayons, et une observable locale ne voit pas
    l'identité** — `94` §6, `95` §9, `96` §9, `97` §7.
11. **Quand les hypothèses de mesure ne mènent à rien, la réponse est visuelle** (consigne de
    l'auteur, `77` §8) — le trou angulaire, la bande qui serpente (`77` §10), le profil à deux lobes
    (`77` §12) ; et sept tranches de marche ont ignoré l'instrument volumétrique du dépôt
    (`lpl-scrollwalk`) jusqu'à ce que l'auteur le rappelle (`75` §C l. 6527).
12. **Une différence de médianes n'est pas un gain : l'écart apparié, sur les mêmes cellules** —
    `75` §C l. 2770 (trois affirmations sur quatre tombent), l. 6458 (un gain de portée entièrement
    fait de ce qu'on jette : +0,0 sur les cellules communes). Trois conditions sans seuil : médiane
    négative, majorité des cas, intervalle laissé-un-dehors entièrement négatif.
13. **Un pas n'est pas une marche : l'erreur se compose parce qu'elle devient la surface d'où l'on
    repart** — `75` §C l. 1886 (le raccrochage itéré), l. 3453 (2 bras contre 4), l. 6559 (la borne se
    froisse et reste juste : ce qu'un aveugle paie, c'est de repartir de sa propre nappe). Et un
    réglage choisi sur la médiane des bras inclut les bras **déjà perdus** (l. 6657).

## 7. Ce que la campagne dit du graal

**La question a changé de forme.** Au 3 septembre elle s'écrivait « construire le prédicat
d'identité que le pinceau peint » (`75` §A). Au 11 septembre :

1. **L'humain travaille sur l'identité, pas sur la qualité locale.** Au bord du rouleau il trace
   proprement une autre feuille (`94`, `95`) ; deux humains divergent d'une demi-feuille partout
   (`97`). Toute observable locale (pli, pose, planarité) est aveugle à cette panne par construction.
2. **Le maillage humain ne peut pas être la cible.** Il n'a pas de valeur unique à une feuille près.
   Le critère doit être tranché par la **matière** — et le seul construit (`98`) a un seuil matériel,
   le bon signe, et une résolution qui accepte 0,68–1,38 feuille par pas (`104`).
3. **La matière donne un pas et une direction sans référent** (`99`, `101`), et les enchaîner bat
   l'automate naïf (`102`). Mais la périodicité suivie n'est pas l'espacement d'un empilement
   parallèle à 346 µm (`106`), et l'écart entre le pas montré (164 µm corrigé) et l'atlas (182) reste
   à expliquer.
4. **La portée n'a jamais été mesurée.** Tout ce qui a été publié comme portée était un plafond
   (`82`), un run consécutif (`109`), ou une lecture du critère par un instrument à plancher relatif
   (`111`). `113` est la première mesure non censurée, et elle tourne. Et sur `0500P2` la campagne
   qui l'a précédée a établi ce qu'une marche coûte de plus qu'un pas : le raccrochage qui gagne sur
   un pas perd sur une marche, la nappe lissée gagne 3–9 µm partout et un bras à une seule ancre,
   et **la moitié du coût d'un pas est un plancher de direction** que la normale ne peut pas
   atteindre (`75` §C, faits 26–28).
5. **Le remplaçant sera local en géométrie** (l'axe est une courbe, `90`) **et global en identité**
   (la fermeture, `96` ; le flot aux jonctions, `114` §7). Ces deux exigences ne sont pas encore
   réunies dans un instrument.
6. **La preuve n'est pas montable sur un objet éligible.** Les treize rouleaux du Grand Prize
   publient zéro rang de spire (`81`) ; la seule vérité de terrain du goulot est `PHercParis4`
   (`84`), qui n'est pas dans la liste. Un déroulage qui marcherait sur Paris4 devrait être
   **transporté** sur un rouleau sans référent — ce que `PRIX.md` §2 et §5 recoupent avec l'annexe A
   des *Open Problems* (le *rollout drift* que l'équipe nomme est ce que `104`–`111` mesurent).

## 8. Portes ouvertes de R4

À reporter dans `PORTES_OUVERTES.md`, classées par ce qu'elles font avancer.

**Grand Prize — le graal**
- **`113`** (en cours) : la portée non censurée à 20 pas ; le registre et le taux de confirmation par
  profondeur. C'est la course en profondeur que `110` §9 demandait pour trancher biais / jitter.
- La politique « confirmer sur une fenêtre de 2 pas ou plus » (`112` §7) : chiffrée, à courir.
- La course qui déciderait `108` (48 trajets par sélecteur, 672 étapes, 7–10 h) — dont le sens a
  changé après `111` : ce qu'elle trancherait est la netteté de la périodicité, plus une partition.
- L'anomalie de `100`/`106` : le même pas dans deux directions à 34°, qu'un empilement parallèle
  interdit ; et la cause de l'obliquité (écrasement, cône, traçage).
- L'écart 164 / 182,4 µm entre transferts humains et atlas, et ce que la matière montre à 346 µm.
- La 3D : un « bout » est la bordure d'une nappe, la conservation de matière un flot aux jonctions
  (`114` §7, question de l'auteur du 11 septembre). Aucune mesure encore.
- L'objet : `0500P2` plafonne à 13 spires publiées ; trois objets portent les 31 (`81` §6). La
  décision et ses coûts (voxel, pas, demi-feuille à re-dériver) sont à l'auteur.
- Le **critère d'arrêt** du raccrochage, observable sans cible : la rugosité de son propre champ
  croît 0,34 → 2,01 sur cinq bras ; il reste à vérifier qu'elle **prédit** l'échec plutôt que de
  l'accompagner (`75` §C l. 6729). Et la confiance par cellule (pli + obscurité, en rang, `ou`) :
  livrable comme carte de doute, ne rend pas un marcheur juste (l. 6380).
- « Combien lisser » demande des ancres dont la marche soit **vivante** : le corpus n'en offre qu'une
  (l. 6665) ; sur `PHercParis4` (120 spires) la question se repose.
- Le plancher de direction (18,2 µm, la moitié du coût d'un pas) : ni la rotation d'ensemble ni un
  champ lisse ne l'atteignent (l. 3137–3313) ; ce qui le rendrait est une direction par cellule qui
  ne soit pas un balayage de cône.

**Grand Prize — le référent**
- A2 bis : un nombre d'enroulement sans référent. Les fibres publiées ne comptent pas des feuilles
  (période 307–441 µm = 2–3 pas) ; sortie : le niveau 0 chez le producteur (`output_channels = 7`)
  ou un autre champ (`75` A2 bis).
- A2 ter : les résidus sur des grilles à pas 8 (Nyquist) — `vc_gen_normalgrids` depuis le volume,
  ×512 le volume publié (`75` A2 ter).
- La cause du trou angulaire de `0172` : déchirure, perte, collage (`77` §8, `75` A′).
- Le masque d'approbation : ce que la ré-optimisation de `villa` en tire ; aucun `approval.tif`
  peint n'est publié, donc « le calculé vaut-il l'humain » n'est pas montable (`75` A3).
- A6 : la ROC de α et d (101 positifs, 101 demi-pas) — exige le volume. B2 : « no threshold » non
  tranchable sans positif indépendant (`77` §11).

**Progress Prizes — soumissible tel quel** (résultats négatifs, audits, outils ; voir `PRIX.md` §1.4)
- Les portées censurées et le mur du corpus (`82`, `83`) ; les treize rouleaux sans rang (`81`).
- Le référent d'identité et ses défauts mesurés contre lui-même (`76` §4, `77` §3, `97`).
- Le *rollout drift* mesuré : bande d'acceptation, biais du sélecteur, falaise instrumentale
  (`104`, `105`, `111`) — l'annexe A des *Open Problems* le nomme sans le chiffrer.
- Les outils : lecture par plage HTTP des volumes (`voxel_distant`, `couches_distantes`),
  `le_sens_des_indices`, `les_spires_consecutives_publiees`.

## 9. Sources pour un article

- **Le référent mesuré contre lui-même** : `76` §3–4, `77` §3, `97` — les spires approuvées ne sont
  pas une vérité de terrain à moins d'une demi-feuille, et deux passes humaines divergent partout.
  Antériorité : `winding-ruler` (atlas des périodes, `86`), la dérive de *rollout* de l'annexe A des
  *Open Problems* (`PRIX.md` §5).
- **La géométrie de `PHercParis4` lue sur les maillages humains** : `84`, `85`, `90`–`93` — courbe de
  coût du déroulage manuel, axe courbe, pas, continuité, parallélisme. Antériorité : W. Stevens
  (déroulage par patches, 20 000 $, non cité par le dépôt avant `PRIX.md` §4).
- **Un critère que la matière tranche** : `98`–`101`, `104`–`106`, `111`–`112` — le modèle nul comme
  seuil, la bande bornée par la physique, la bande d'acceptation d'un critère.
- **Le rouleau écrasé** : `76` §2, `78` §4, `90`, `100` — aucun modèle à section circulaire ne sépare
  des feuilles à une feuille près.
- Tout chiffre de ce rapport se recalcule par le producteur nommé ; le garde-fou
  `src/depot/verifier_chiffres.py` lit désormais `docs/rapports/`.
