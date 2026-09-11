# Reprise de session

Document de passation. ⚠ Le bloc **REPRISE** ci-dessous est l'état courant ; le reste est
l'historique, daté, et se lit ensuite.

---

## ⭐⭐⭐⭐ REPRISE — 2026-09-10

⭐⭐⭐⭐ **ET `109` A RETIRÉ SON FONDEMENT AU CHIFFRE QUI AVAIT DÉCLARÉ LE GRAAL MORT, SANS UNE
LECTURE DE PLUS.** `102` et `107` publient « la matière porte deux pas confirmés » en comptant les
pas confirmés **CONSÉCUTIFS DEPUIS LE DÉPART** — un compte **borné par la position du premier
manque**, donc incapable de dire « cinq sur six ». Sur les **56** marches de `107` : médiane des pas
**réellement** confirmés **4,0** contre médiane du run **1,0**, et **24** marches confirment **5**
ou **6** pas sur **6** dont **6** créditées de zéro ou un. *Une marche `O . O O O O` et une marche
`O . . . . .` sont indiscernables par le nombre publié.*

⭐⭐⭐ **ET LE TEST QUI TRANCHE NE REGARDE JAMAIS LE REGISTRE DU TRAJET.** Une marche qui se PERD
manque en rafale ; une marche qui rate une confirmation manque au hasard. Mesuré : rafale moyenne
**2,286** contre **2,213** sous l'indépendance **à même taux** (p95 **2,393**), **p = 0,2829** — et
dans **aucun** des deux modes les manques ne sont groupés (haut **p = 0,5877** à taux **0,8485**,
bas **p = 0,2388** à **0,5192**). **Un pas non confirmé n'est pas une chute mais une confirmation
manquée.**

⭐⭐⭐ **DONC `(1 − risque)^120` NE S'APPLIQUE PAS.** Au taux du mode qui compte, la lecture « chute »
rend **2.74e-09** de survie ; la lecture « manque » rend **18,2** confirmations manquées sur 120 pas
et une marche qui continue. ⚠⚠⚠ **Cela ne prouve PAS qu'un marcheur tient cent vingt spires** : six
pas ne sont pas cent vingt, le mode qui ne compte rien fait **26** marches sur 48 décidables, et rien
ici ne mesure la dérive au-delà de six pas. Ce qui est prouvé est que **le nombre publié dépendait
d'une hypothèse que personne n'avait testée**.

⚠⚠ **ET LE NUL FAIT LA DÉCISION, CE QUE MA PREMIÈRE SONDE A PROUVÉ EN SE TROMPANT.** Avec un nul à
taux **COMMUN** le même test rend **p = 0,001** et déclare les manques groupés : il reproche à une
marche qui confirme un pas sur deux des rafales qui, à ce taux-là, sont la norme. Le groupement se
teste **à taux égal**, et la batterie le démontre sur un jeu fabriqué (**0,0205** contre
**0,1534**). ⚠ Le nul est **conservateur** : « non groupé » veut dire « aucun groupement au-delà du
taux », donc le verdict se lit **par mode**.

⚠⚠ **ET UNE AUTRE FAUTE À MOI, DANS LA MÊME TRANCHE** : ma première version de « un manque coûte-t-il
des feuilles » lisait *plus de feuilles* comme *mieux*. La cible est **exactement une feuille par
pas**, donc franchir 1,29 est aussi faux que franchir 0,71. Corrigé, le verdict est **non**
(écart à un **0,292** contre **0,269**, **p = 0,7098**) — mais il découvre que les **7** marches
**entièrement confirmées** franchissent **1,292** feuille par pas quand les **15** avec manque sont à
**1,005** : ⭐ *le critère confirme des pas qui traversent trop*, troisième route vers ce que `104`
(bande 0,68 à 1,38) et `105` (+18,4 %) avaient mesuré.

⭐ **ET LA SUITE QUE ÇA DÉSIGNE CHANGE** : la bonne question n'est plus « combien de pas la matière
porte » mais **de combien le compte DÉRIVE quand la marche est longue**, puisqu'un manque isolé ne
l'arrête pas. C'est la question que `104` posait déjà — *biais, qui coûte `n`, ou jitter de moyenne
nulle, qui coûte `√n` ?* — et elle demande des marches **longues**, pas nombreuses : le plafond de
six pas de `107` est exactement ce qui empêche de la poser.

---

⭐⭐⭐⭐ **ET `108` A RÉPONDU À LA QUESTION QUE `107` POSAIT EN PREMIER, SANS UNE LECTURE DE PLUS.**
`107` laissait deux populations « que rien d'autre ne distingue ». C'est faux, et la mesure le dit :
sur **onze candidats déclarés AVANT de regarder**, corrigés par permutation sur le maximum de la
famille, **deux survivent** — le **score médian du balayage** (force **0,664**, p corrigée
**0,0008** ; **6,054** pour les marches qui comptent contre **4,5852**) et l'**accord médian de
l'interstice** (force **0,563**, p corrigée **0,0046**). Les deux sont mesurés **sur le cube, à
chaque pas**, avant qu'aucun profil de trajet ne soit ajusté.

⭐⭐⭐ **ET LE FAIT CENTRAL EST UN CONTRASTE, PAS UN GAGNANT.** Le score du **trajet** sépare fort
(**0,6888**) et **à l'envers** ; le score du **pas** sépare presque autant (**0,6643**) et **à
l'endroit**. `107` avait raison sur le fait et tort sur la portée : *ce n'était pas le bon score, et
le bon était déjà calculé à chaque pas sans jamais être lu*. Le mécanisme est nommé — une dérive de
basse fréquence s'ajuste d'autant mieux qu'on lui laisse une longue fenêtre (1250 µm), et la
fenêtre d'un pas (230 µm) est trop courte pour qu'elle y passe pour une périodicité.

⚠⚠ **MAIS LE PREMIER PAS NE SUFFIT PAS** (force **0,0385**, p corrigée **0,9986**) : il en faut
**trois** (force **0,5035**, p corrigée **0,0100**), soit **trois cubes payés avant de savoir**. Un
automate ne peut pas savoir en partant ; il peut savoir assez tôt pour **repartir ailleurs** — ce
qui est exactement le remède que le risque décroissant de `107` désignait.

⚠⚠ **ET LA RÉPLICATION PAR SÉLECTEUR NE TIENT PAS**, ce qui borne tout le reste : `calibre` (12/12)
retient les deux, `deux_roles` (10/14) n'en retient **aucun** — même meilleur candidat des deux
côtés, force **0,6286**, mais à l'effectif d'un seul sélecteur la correction n'est plus franchie. Et
les **48** trajets de l'ensemble **ne sont pas indépendants** : deux marches partent de la même
cellule. ⚠ Trois candidats montent dans le sens attendu sans franchir la correction (planarité
médiane 0,434 et minimale 0,418, virage 0,378) : ce ne sont pas des non-résultats, c'est un effectif
qui ne décide pas.

⚠⚠⚠ **ET LE PIÈGE DE CETTE TRANCHE EST CHIFFRÉ AVANT SON RÉSULTAT.** Avec onze candidats et
quarante-huit trajets, un test par candidat sans correction déclare un gagnant sur du **bruit pur**
**42,7 %** du temps — **mesuré** (400 tirages), pas invoqué ; avec un seul candidat il retombe à
**7 %**. Le 95ᵉ centile de la plus grande force **sous le nul** vaut **0,4615**, et cinq candidats
sur onze franchissent 0,32.

⚠⚠⚠ **ET DEUX FAUTES À MOI, DONT UNE QUE `107` AVAIT DÉJÀ PAYÉE.** *Une médiane sur une loi en U
n'est pas un résumé* : le niveau de chance hors échantillon a une **moyenne** de 0,512 et une
**médiane** de 0,575, avec **37,5 %** des tirages **sous** le hasard — un seuil a un sens, donc
chaque tirage tombe du bon côté ou du mauvais. Attrapée par une sonde, pas après publication. Et
*un témoin positif mal spécifié n'est pas un témoin* : j'avais déclaré la longueur parcourue comme
devant séparer, et la matière l'a réfutée **à l'envers** — le mode qui ne compte **rien** marche
**plus loin** (**1276,0 µm** contre **1189,4**). ⭐ Le retard n'est donc pas une marche qui s'arrête
tôt : c'est une marche qui **avance sans rien traverser**. ⚠ Le témoin est resté **hors famille** :
l'y faire entrer après avoir vu les résultats aurait été la faute exacte que la correction existe
pour empêcher.

⭐⭐ **ET LE PRIX DE LA COURSE QUI LÈVERAIT LA BORNE EST CHIFFRÉ AVANT D'ÊTRE PAYÉ**, sur des
données déjà payées. En rééchantillonnant `deux_roles` — celui qui a échoué, force **0,6286** —
quatre chances sur cinq arrivent à **48** trajets par sélecteur, soit le **double** de `107` :
**28** bandes × **2** cellules × 2 sélecteurs × 6 pas = **672 étapes**, donc **10,27 h** au coût
retenu (55,0 s/étape) et **7,05 h** au rythme réel (37,8). ⚠⚠ C'est un **PLANCHER** — l'ampleur
rééchantillonnée est celle du **maximum** d'une famille de onze. ⚠⚠⚠ **Et ce n'est pas « combien
pour SAVOIR », ce que sa propre batterie mesure** : sur du **bruit pur** la même fonction fait
monter la réponse pareil, parce qu'elle traite l'ampleur observée comme la vérité. Le chiffre n'a
de sens que parce que l'ensemble établit ce candidat à p corrigée **0,0008** — *c'est la
correction, pas le prix, qui écarte le bruit*.

⭐ **ET LA PARTITION NE DÉPEND PAS DU SEUIL** : dernier trajet du mode bas **0,237** feuille par pas,
premier du mode haut **0,671**, pour un seuil à **0,5** — un **vide de 0,434**, et c'est le plus
grand vide de toute la distribution. Rien ne se tient près du seuil.

⚠ **ET LE NIVEAU DE CHANCE N'EST PAS LE TAUX DU MODE MAJORITAIRE.** Un seuil sur le score du pas
classe juste **75,0 %** hors échantillon contre **49,2 %** pour le niveau **mesuré** (200 tirages de
bruit au même effectif) — c'est **ce niveau-là** qu'il doit battre, pas les 54,2 % du mode
majoritaire, qui lui offriraient l'optimisme résiduel de la validation. Coût du seuil, chiffré en
marches : **7** bonnes jetées sur 22, **3** mauvaises gardées sur 26.

---

**Quatorze tranches d'une même campagne, `94` à `107`, et elles ont UNE conclusion — plus, désormais,
UN acquis.** L'arbre est propre, les gardes vertes, 109 fiches sans dérive, aucun artefact
versionné sans appelant. Ce
bloc remplace le précédent comme état courant ; tout ce qui suit est l'historique, daté.

⭐⭐ **Et la campagne s'est prolongée de deux tranches qui ne cherchaient plus un signal mais une
EXPLICATION** : `100` est allé chercher pourquoi le pas que la matière montre (199 µm) diffère de
celui des transferts humains (164). L'explication évidente — la nappe n'est pas perpendiculaire au
rayon — est **réfutée**, et le fait qu'elle laisse derrière elle est plus lourd qu'elle : la
surface tracée est à **34,1°** du rayon là où une spirale de ce pas en prédit **0,09°**.

⭐⭐⭐ **Puis `101` a demandé à la MATIÈRE de trancher, et elle a tranché.** Le tenseur de structure
du volume fin, sans aucun maillage, rend une normale à **13,3°** de celle du maillage humain et à
**34,6°** du rayon — et ce **34,6** recoupe **indépendamment** le **34,06** que `100` lisait sur le
maillage seul. L'obliquité est donc une propriété de la **matière**, un axe mal estimé est réfuté
par sa signature en 1/r, et **le maillage humain est sur la matière en ORIENTATION (13°) tout en
étant faux en IDENTITÉ** (`97`, plus d'une demi-feuille). Deux pannes différentes, une seule
fatale.

⭐⭐⭐ **ET `102` A ENCHAÎNÉ LES DEUX, CE QUI EST LA QUESTION DU GRAAL ELLE-MÊME.** Dérouler n'est
pas faire **un** pas mais les **enchaîner**, et le marcheur — direction du tenseur de structure,
pas du balayage calibré, vérification par le critère de `98`, **aucun référent humain** — confirme
**2,00 pas** là où l'automate naïf (pas nominal le long du rayon) en confirme **0,00**, sur les 28
bandes. Il porte **583,9 µm**, soit **3,4 feuilles nominales**, sans **aucune** sortie du volume.
⭐ Et le témoin **n'est pas un homme de paille** : sur un empilement fabriqué **droit** il atteint
le plafond exactement comme la matière ; c'est l'**obliquité** de `100`/`101` qui le fait tomber.

⭐⭐⭐ **ET `107` A REJOUÉ LA MARCHE AVEC LE BON PAS, EN GARDANT SES ÉTAPES — LE PREMIER RÉSULTAT
STRUCTUREL POSITIF DE LA CAMPAGNE.** Le pas corrigé **ne porte pas plus loin** (1,0 contre 1,0 pas
confirmés, 17,9 % au plafond), mais **le risque par pas BAISSE** : précoce **0,382** sur 55 pas en
risque, tardif **0,105** sur 19, soit **×3,63**, et **p = 0,0418** sous un risque constant. *La
difficulté est de s'accrocher, pas de porter* — donc le remède est un meilleur DÉPART, pas un
meilleur marcheur. ⚠⚠ Mais il ne baisse pas assez : `(1 − 0,105)^120` vaut **2·10⁻⁶**, et le tiers
tardif ne tient que sur 19 pas en risque.

⭐⭐⭐ **ET LE REGISTRE DU TRAJET ENTIER SÉPARE LES MARCHES EN DEUX POPULATIONS QUE RIEN D'AUTRE NE
DISTINGUE** : **10** trajets franchissent **6,478** feuilles pour six pas — **1,08 par pas**, ce que
le marcheur doit faire — et **14** n'en franchissent que **0,748**, soit **0,125**. ⭐ Les DEUX
sélecteurs se séparent de la même façon, donc c'est une propriété de la **matière** et non du
sélecteur. ⚠⚠⚠ Et **le score est PLUS HAUT pour les mauvaises** (0,483 contre 0,371) : une dérive de
basse fréquence s'ajuste mieux sur une longue fenêtre qu'un vrai signal périodique, donc **un seuil
de score écarterait le BON mode**. C'est le point de `104` mesuré sur la marche elle-même.

⚠⚠⚠ **ET TROIS FAUTES À MOI DANS CETTE TRANCHE, CHACUNE ATTRAPÉE PAR UNE MESURE.** *Une fraction
mesurée sur UN pas est tautologique* — les deux sélecteurs y rendent 1,007 et 1,010 malgré des pas
de 224,9 et 233,6 µm, parce que chacun CHOISIT son pas pour qu'une période y tienne ; seconde
réfutation d'un registre après `104`, par une autre route. *Une médiane sur une distribution
bimodale n'est pas un résumé* — la mienne valait 0,199 et tombait dans le mauvais mode. Et *un coût
mesuré sous contention n'est pas un coût* : j'ai chiffré la course à 58,5 s par étape sur un pilote
lancé à côté d'une autre batterie, puis à 38,0 sur des cellules déjà lues ; elle en coûte **55,0**.

⛔ **L'OPTIMISATION DU COÛT EST CHIFFRÉE PAR LA MÊME COURSE ET REFUSÉE.** Le cube fait **91 %** du
prix d'un pas (14,88 s contre 0,76 et 0,70), monter les fils de 32 à 96 ne gagne rien (15,62 s), et
`103` avait déjà réfuté de le lire moins cher. Restait de le lire **moins souvent** : la direction
tourne de **10,12°** d'un pas au suivant (p90 22,84°) pour une barre d'accord des demi-blocs de
**8,88°**, donc **non**. ⭐ Le chiffre est venu **sans une lecture de plus**, parce que les étapes
sont gardées.

⛔⛔⛔ **ET `106` A RETIRÉ AU MARCHEUR LE SENS DE CE QU'IL MESURE.** `100` avait comparé la période
dans DEUX directions séparées de 34° et rendu **1,018** là où un empilement parallèle prédit
**1,184** ; deux points ne décidant pas d'une courbe, `106` balaie un **éventail** de 21 directions
sur ±50° autour de la normale de `101`, avec le sélecteur que `105` a corrigé, **apparié** sur les
mêmes lectures. ⛔⛔ **Le même instrument ajuste une pile FABRIQUÉE à 0,72 µm et la matière à
19,30 — soit ×22,3 pire.** Battre une constante de 36 % ne rachète pas cela : **à l'échelle où le
balayage la sonde, la matière ne se comporte pas comme un empilement de feuilles parallèles.**

⚠⚠⚠ **LE REPÈRE D'UN INSTRUMENT EST CE QUE CE MÊME INSTRUMENT OBTIENT SUR DU CONNU**, pas une part
de son propre signal — correction de ma première version, qui comparait le résidu à l'amplitude de
la courbe et laissait donc passer un ajustement vingt fois pire que sur une réponse connue.

⛔⛔ **ET L'ANOMALIE DE `100` SURVIT À LA CORRECTION** : le rapport rayon/normale passe de **0,929**
à **1,000** pour **1,155** prédits — le sélecteur le déplace de **+0,071** et il reste **−0,155**
pour une résolution de **0,113**. ⛔ L'explication la plus plausible est réfutée en prime : une
famille de feuilles qui **tourne** le long de la sonde fait **monter** le rapport (1,200 à 1,523
pour 0 à 25°/100 µm), elle ne le ramène pas vers un.

⚠⚠⚠ **ET DEUX FAUTES À MOI, DONT UNE QUE J'AI ÉCRITE DANS UNE FIGURE.** *Un vecteur propre n'a pas
de sens* : sans orientation, **61 %** des cellules avaient le rayon hors de l'éventail et mon code
l'**écrêtait** sur le bord — une limite de grille publiée comme une limite matérielle. Ce qui l'a
attrapé est un chiffre absurde (`1/cos` à **1,556**, soit exactement le demi-angle), et la
correction s'est vérifiée **sur les données déjà lues** avant d'être repayée : replié, l'angle médian
donne **33,6°** contre les **34,59°** de `101`. Puis *une médiane SIGNÉE d'angle n'est pas un
accord* : le minimum est à **+2,50°** en signé et **25,0°** en absolu, pour un pas d'éventail de 5°.
J'avais lu le premier comme un accord avec `101` ; il ne dit que la symétrie de la dispersion.

⭐⭐⭐ **ET LES TROIS DERNIÈRES TRANCHES DISENT LA MÊME CHOSE SOUS TROIS ANGLES** : `104`, un pas
**confirmé** peut franchir entre 0,68 et 1,38 feuille sans que rien ne le signale ; `105`, le pas
dont le marcheur avance est **+18,4 %** trop grand ; `106`, la quantité que ce pas mesure **n'est
pas** l'espacement d'un empilement parallèle. ⚠ « La matière porte deux pas » ne veut donc pas ce
qu'on croyait.

⛔⛔⛔ **ET `105` A TROUVÉ L'INSTRUMENT EN DÉFAUT SOUS TOUT LE RESTE.** Le sélecteur que `99`
appelle réellement — `pas_montre_calibre` — **ne rend pas la période qu'on lui injecte** : sur des
profils fabriqués dont la réponse est exacte il lit **+5,0 %** trop haut, jusqu'à **+11,2 %**, là où
le sélecteur brut la retrouve au cran près (**+0,0016**). ⛔⛔ Et **la batterie de `99` ne pouvait
pas le voir** : son contrôle aller-retour relit par `pas_montre`, le **brut**, alors que la mesure
appelle le **calibré**. *Une vérification qui n'emprunte pas le chemin de la production.*

⭐⭐⭐ **SUR LE VRAI VOLUME, CONTRÔLE APPARIÉ — 28 bandes × 120 cellules, MÊMES lectures, même
garde — le calibré lit 194,6 µm là où le brut lit 164,3**, soit **+18,4 %**, et **28 bandes sur 28**
sont du même côté. ⭐ **164,3 tombe sur la même case de grille que les 164,0 µm des transferts
humains**, donc l'écart de 21,3 % que `99` laisse ouvert depuis cinq tranches est, pour l'essentiel,
**l'instrument**. ⚠ La précision revendiquée est celle de la grille — cran de **8,65 µm**, soit
5,3 % du pas — et le sens de l'écart au nominal **s'inverse** (×1,15 publié, ×0,95 corrigé).

⭐⭐⭐ **LE MÉCANISME EST MESURÉ** : le nul par candidat décroît avec la longueur (µ de **0,1582** à
**0,0925**), donc la calibration favorise les candidats longs — sur 173 µm injectés elle retient
**181,7** avec un accord brut de **0,9882** contre **1,0000**. *Une statistique qui rend deux
questions comparables n'en résout qu'une.* ⭐⭐ Le remède est le patron du dépôt : **le calibré
garde, le brut choisit parmi les admis** — et il passe le contrôle que `99` impose à sa propre
longueur **mieux que les deux autres** (D = **0,738**, p = **1,65e-08**).

⭐⭐⭐ **ET LA CONSÉQUENCE POUR LE MARCHEUR RELIE `104` ET `105`.** Le marcheur de `102` avance de ce
que ce sélecteur rend, donc il franchit **1,184 feuille par pas** : cent vingt pas en franchissent
**142**, soit **22 spires de trop**. Et `104` a mesuré que le critère accepte tout ce qui franchit
entre **0,70** et **1,36** feuille — **1,184 est dedans**, donc **chaque pas est confirmé et rien ne
le signale**. C'est le cas « biais » que `104` opposait au cas « taux d'échec », **mesuré** cette
fois au lieu d'être hypothétique.

⛔⛔⛔ **ET `104` A RÉFUTÉ LE CRITÈRE QUI PORTAIT TOUT.** En construisant le REGISTRE des feuilles
franchies — l'équivalent gratuit de ce que l'humain dit quand il corrige un transfert, *« tu es sur
la spire n »* — le contrôle de calibration a réfuté l'instrument **au premier lancement**, et en le
réfutant il a montré un défaut bien plus lourd : **le critère de `102` confirme tout ce qui franchit
entre 0,68 et 1,38 feuille**. Un pas de feuille implicite de **144 à 293 µm** là où le nominal est
173, et il **confond les 4 pas publiés** par la campagne — dont l'écart de 21,3 % que `99` laisse
ouvert, quatre fois plus étroit que la tolérance du critère.

⭐⭐⭐ **ET LA CONSÉQUENCE ENCHAÎNÉE MORD DANS L'AUTRE SENS QUE `103`, CE QUI EST PIRE.** `103`
chiffrait un **taux d'échec** : une chute se **voit**, le marcheur s'arrête. Ici c'est un **biais** —
cent vingt pas **tous confirmés** peuvent n'avoir franchi que **82 spires**, soit **38 de moins** que
le compte affiché, sans qu'aucune vérification n'ait rien signalé. *Une chute se voit ; un retard
s'accumule en silence.* ⚠⚠ Et la bande ne dépend **presque pas du bruit** (0,70 à σ = 0, 0,60 à
σ = 30) : ce n'est pas une limite du scan qu'un meilleur volume lèverait, c'est le pouvoir de
discrimination de la **forme** des gabarits — famille `{1, 2, 3}`, donc « moins d'une feuille » est
**inexprimable**.

⭐⭐ **LE REMPLAÇANT EXISTE ET IL EST CALIBRÉ** : `feuilles_franchies` (dans `98`, à côté du compteur
qu'elle remplace) estime la fraction sur une famille **continue**, donc elle peut valoir moins de un,
et elle reproduit `cos θ` à **0,0022** près sur quatre obliquités fabriquées. ⚠⚠ Deux gardes pour
deux pannes : **sous** la fenêtre le score ne garde rien (0,20 feuille ressort à 0,350 au score
0,996) et seule la **butée** le dit ; **loin au-delà** c'est le score qui écarte et la butée ne voit
rien.

⛔ **CONSÉQUENCE SUR L'ORDRE DES CHOSES : la portée de `102` n'est PLUS la prochaine dépense.**
Mesurer la forme de la survie d'un critère juste à 32 % près serait mesurer la mauvaise chose. Elle
reste chiffrée d'avance à **5,35 h** pour 840 étapes — en couverture (28 × 3 × 10, 84 marches) comme
en profondeur (28 × 1 × 30, 28 marches), et à budget égal la couverture rend **trois fois plus** de
chutes. ⭐⭐⭐ **Et la leçon générale a coûté sept heures : UN AGRÉGAT NE SE DÉSAGRÈGE PAS.** `102` a
marché 224 fois en ne gardant qu'une médiane par bande ; d'une médiane de quatre on ne tire que
`a2 <= m <= a3`, donc la survie n'y est bornée qu'à **0,5** près — un risque par pas **constant** de
0,056 à 0,546 y est également compatible. Les étapes existaient ; elles n'ont pas été écrites.

⛔⛔ **ET `103` AVAIT CHERCHÉ À LEVER CETTE BORNE MOINS CHER, SANS Y PARVENIR.** Échantillonner le cube
un voxel sur deux — **même portée** — coûterait **×1,72** moins, mais **7,3 %** des cellules s'en
écartent de plus de 10° du pas le plus fin, et comme `102` **enchaîne** les pas cela abîme
**36,5 %** des marches de six pas. ⚠ Ce que ce paragraphe concluait — « la portée se lèvera au prix
plein ou pas du tout » — est **dépassé par `104`** : elle ne se lèvera pas d'abord, le registre passe
devant.

⚠⚠⚠ **Et c'est MA PROPRE SONDE qui était tombée dans le piège** : sur **2 bandes** j'avais mesuré
**0 %** et j'allais adopter l'économie ; sur les **28**, c'est 7,3 %. *Un bord se compte sur le
corpus entier, pas sur les bandes qu'on a sondées* — `93`, réécrit par `95`, repayé ici. ⭐ Ce qui
l'a attrapé n'est pas une relecture mais d'avoir relancé sur le corpus **avant** de publier.

⭐ **Ce que `103` laisse quand même** : le coût d'une lecture distante est désormais **mesuré** —
**15,4 s** par cube, un **plancher de 3,76 s** qui ne descend jamais, et un temps qui suit les
**rangées** et non les points (le comptage de points prédisait ×7,44, la mesure rend ×1,72). Chaque
mesure future se chiffre donc **d'avance** au lieu de se découvrir après sept heures.

⚠⚠⚠ **MAIS LA PORTÉE EST CENSURÉE, ET ÇA SE DIT AVANT LE RÉSULTAT** : **17 bandes sur 28** (61 %)
ont une cellule au plafond de **6 pas**, donc **2,00 est une borne inférieure**. Le plafond est un
**budget de lecture** — **15,4 s par cube** mesurés, 2 h 52 de plancher pour 672 cubes, **7 h** de
course — et le publier comme une limite de matière serait la butée de `99`. **Deux pas ne sont pas
cent vingt** : ceci mesure la **pente**, pas le total.

⭐⭐⭐ **ET C'EST LE PREMIER ACQUIS POSITIF DE LA CAMPAGNE POUR LE GRAAL.** `99` donne le **pas**
que la matière montre, `101` donne la **direction** : *avance de `p(matière)` le long de
`n(matière)`* est un pas de transfert qui ne demande **aucun maillage**. La matière répond sur
**64 %** des cellules, et — confondant du rayon retiré (+0,452 à rayon tenu) — **plus souvent au
bord**, là où `99` perdait la périodicité (0,54). ⚠ Ce qui reste hors de portée est
l'**identité** de la feuille : le tenseur dit *comment elle est posée*, pas *laquelle*.

⚠ Le bloc précédent, daté du 2026-09-03, annonçait un état courant que ces onze tranches ont
dépassé. Il est conservé plus bas, sous son en-tête, parce que ses résultats tiennent.

### ⭐⭐ CE QUI VIENT ENSUITE, ET L'ORDRE EST DÉRIVÉ PLUTÔT QUE CHOISI

0. ⛔⛔⛔ **AVANT TOUT LE RESTE, ET `106` L'A DÉPLACÉ : ce n'est plus « relancer avec le sélecteur
   corrigé », c'est SAVOIR CE QUE LE PAS MESURE.** `106` montre que la périodicité que le balayage
   suit n'est pas l'espacement d'un empilement localement parallèle, donc relancer `99` à `102`
   avec le bon sélecteur rendrait des nombres justes pour une quantité dont le sens reste inconnu.
   ⚠ La question à trancher d'abord : à quelle échelle la matière EST-elle un empilement parallèle,
   si elle l'est ? La sonde fait 346 µm, imposée par le plus long candidat, et `101` mesure la
   cohérence d'orientation à ~100 µm. Une fenêtre de balayage plus courte demande son propre nul par
   candidat, donc c'est une tranche à soi.
1. ⛔ **Puis relancer avec le sélecteur corrigé.** `99`, `100`, `101` et `102`
   ont tous été calculés avec le sélecteur biaisé, et `105` montre que la correction n'est PAS un
   facteur à appliquer — il faut relancer. ⚠ `100` compare deux directions avec ce sélecteur, donc
   son anomalie d'isotropie hérite de la dérive ; `102` marche avec, donc sa portée est mesurée par
   un marcheur qui dépasse de 18 % à chaque pas.
1. ⭐⭐⭐⭐ **FAIT PAR `108`, ET CE QUI RESTE EST UNE COURSE, PAS UN CHIFFRE.** Le signal existe (le
   score du balayage, mesuré à chaque pas, lisible au troisième), mais **un signal n'est pas une
   politique**. Ce qui manque est la mesure appariée que `102` et `107` emploient déjà : *un
   marcheur qui REDÉMARRE ailleurs quand le score des trois premiers pas est bas porte-t-il plus
   loin qu'un marcheur qui ne le lit pas ?* Départs identiques, même corpus, deux politiques. ⚠ Et
   la borne à lever d'abord : la réplication par sélecteur ne tient pas (24 trajets par sélecteur),
   donc la course doit rendre assez de marches pour que chaque moitié décide seule. ⭐ **Le prix en
   est chiffré** : **48** trajets par sélecteur, soit **28 bandes × 2 cellules**, **672** étapes,
   **10,27 h** au coût retenu et **7,05 h** au rythme réel — et c'est un plancher.
2. ⭐⭐ **Le registre continu, sur le vrai volume.** `feuilles_franchies` est calibrée mais elle
   n'a **aucun appelant en production** : le marcheur de `102` n'accumule rien. Le brancher rend une
   question que rien n'a encore posée — *après k pas, combien de feuilles ai-je RÉELLEMENT
   franchies ?* — et sa réponse tranche la seule chose qui décide du graal : le retard est-il un
   **biais** (qui coûte `n`) ou un **jitter** de moyenne nulle (qui coûte `√n`) ?
2. ⛔⛔ **ET `109` INVERSE CET ORDRE-LÀ.** Ce point disait : la portée en **couverture**
   (28 × 3 × 10, 84 marches, 5,35 h) plutôt qu'en **profondeur**, « parce qu'à budget égal elle
   rend trois fois plus de chutes ». ⭐ Or `109` a mesuré qu'un pas non confirmé **n'est pas une
   chute** : compter des chutes est donc mesurer la mauvaise chose. La question qui reste est la
   **DÉRIVE** — *biais, qui coûte `n`, ou jitter de moyenne nulle, qui coûte `√n` ?* — et elle
   demande des marches **LONGUES**, pas nombreuses. C'est la **profondeur** qu'il faut payer, et le
   plafond de six pas de `107` est exactement ce qui empêche de poser la question.
3. ⚠⚠ **Et le marcheur devra GARDER ses étapes cette fois.** `102` les a jetées au profit d'une
   médiane par bande, et sept heures de course sont irrécupérables.

⛔⛔ **UNE PISTE À NE PAS REPRENDRE, ET ELLE EST SÉDUISANTE.** `104` montre que le critère confond
198,9 (le pas que la matière montre le long du RAYON) et 164,0 (celui des transferts humains), et
`101` donne 34,59° entre la normale de la matière et le rayon. Or `198,9 × cos(34,59°) = 163,7`, à
**0,2 %** de 164,0, et `1/cos(34,59°) = 1,215` contre les **21,3 %** que `99` laisse ouverts. La
tentation est de conclure que l'écart de `99` EST l'obliquité.

⚠⚠⚠ **`100` a déjà fait exactement cette mesure et elle est réfutée**, par bande et sur les 28 :
`le_pas_dans_les_deux_directions` balaie le pas le long du rayon ET le long de la normale, et rend
un rapport médian de **1,018** contre **1,184** prédit par `1/cos`. Le pas est le MÊME dans les deux
directions (198,9 radial contre 196,8 normal). L'accord global entre 163,7 et 164,0 est donc une
**coïncidence de médianes**, et la reprendre serait repayer une réfutation. ⚠ Et l'écart de 13°
entre la normale du maillage (que `100` utilise) et celle de la matière (`101`) ne peut pas
l'expliquer : `1/cos(13°) = 1,026`, soit 2,6 %.

⭐⭐ **CE QUE CETTE RÉFUTATION LAISSE, EN REVANCHE, EST UNE ANOMALIE QUE PERSONNE N'A RELEVÉE.** Un
empilement de feuilles PARALLÈLES ne peut pas avoir la même période dans deux directions séparées de
34° : sa période apparente est minimale le long de sa normale et plus grande partout ailleurs. Que
la mesure rende 1,018 veut donc dire que l'une de ces deux choses est vraie, et les deux comptent
pour le marcheur :
- ce que le balayage appelle « période » n'est pas l'espacement des feuilles ;
- ou les feuilles ne sont pas localement parallèles sur la longueur d'un segment (~199 µm), et la
  période mesurée est une moyenne où l'anisotropie se dissout.
⚠ Et le balayage est DISCRET (cran de 8,7 µm, **12** valeurs distinctes pour 28 bandes), donc le
rapport a un plancher de résolution de ~4,4 % : c'est à mesurer avec un pas de balayage plus fin
avant d'en tirer quoi que ce soit.

### ⭐⭐⭐ La question était : QU'EST-CE QUI REMPLACE L'HUMAIN QUI CORRIGE LE TRANSFERT ?

La carte du goulot était établie ([`90`](docs/90_laxe_est_une_courbe.md) à
[`93`](docs/93_ou_les_spires_sont_elles_paralleles.md)) : le transfert casse au **bord**, où la
surface est brisée (×31) et les spires désalignées (×3,67), et il suffit à **mi-rayon** (×1,23).
Ce qui manquait était un **signal de confiance** qu'un automate puisse lire seul. Quatre
candidats ont été testés, dans cet ordre, et chacun a fermé une famille entière :

| tranche | observable | verdict |
|---|---|---|
| [`94`](docs/94_le_froissement_mesure_la_rugosite.md) | le **pli** du maillage | ⛔ **anti-prédictif** — −0,825 avec la rupture |
| [`95`](docs/95_la_surface_et_la_feuille_par_rayon.md) | la **pose sur la matière** | ⛔ **anti-prédictif** — −0,694 |
| [`96`](docs/96_la_fermeture_dun_tour.md) | la **fermeture d'un tour** | ⭐ bon signe (**+0,822**), mais **aucun étalon** |
| [`97`](docs/97_deux_humains_sur_la_meme_matiere.md) | deux **tracés humains** de la même matière | ⛔ le **référent lui-même** diverge de plus d'une demi-feuille |
| [`98`](docs/98_combien_dinterstices_traverses.md) | le **compte d'interstices**, lu dans le volume | ⭐⭐ bon signe (**−0,411**) et **premier seuil matériel** — mais faible au bord |
| [`99`](docs/99_le_pas_que_la_matiere_montre.md) | le **pas que la matière montre** | ⭐⭐ `part_utilisable` à **−0,845**, le signal au bon signe le **plus fort** — et le pas montré (**199 à 214 µm**) n'est pas le nominal |
| [`100`](docs/100_la_normale_nest_pas_le_rayon.md) | l'**obliquité de la nappe** au rayon | ⛔ l'explication de l'écart de `99` est **réfutée** — mais la surface est à **34,1°** du rayon pour **0,09°** prédits |
| [`101`](docs/101_la_direction_que_la_matiere_montre.md) | la **direction que la matière montre**, lue dans le volume fin | ⭐⭐⭐ l'obliquité est **réelle** : la matière est à **13,3°** du maillage contre **34,6°** du rayon, et ce 34,6 recoupe le 34,06 de `100` par un instrument qui ne partage rien. ⭐⭐ **Le graal gagne son second nombre** |
| [`102`](docs/102_combien_de_pas_la_matiere_porte.md) | le pas de `99` et la direction de `101`, **enchaînés** | ⭐⭐⭐ **PREMIER ACQUIS POSITIF** : **2,00** pas confirmés contre **0,00** pour l'automate naïf, **sans aucun référent humain**. ⚠⚠⚠ Mais **censuré** — 17 bandes sur 28 au plafond, donc « 2,00 » est une **borne inférieure** |
| [`103`](docs/103_le_cube_lu_moins_cher.md) | peut-on lire le cube **moins cher** pour lever la borne de `102` ? | ⛔⛔ **Non** : l'économie (×1,72) écarte **7,3 %** des cellules de plus de 10°, ce qui abîme **36,5 %** des marches de six pas. ⚠⚠⚠ Ma sonde à **2 bandes** disait **0 %** — *un bord se compte sur le corpus entier*. ⭐ Mais le coût est désormais **mesuré** : 15,4 s/cube, plancher 3,76 s, temps qui suit les **rangées** |

### ⭐⭐⭐ LA CONCLUSION, ET ELLE TIENT EN UNE PHRASE

> **Aucun signal mesuré contre un maillage humain ne peut être calibré, parce que le maillage
> humain n'a pas de valeur unique** — deux tracés indépendants de la même matière divergent de
> **121,7 µm au cœur** pour une demi-feuille de 82 à 91, et de plus d'une feuille entière sur
> une part de **0,339** des points (`97`).

⭐⭐ **Et c'est ce qui explique les deux premiers négatifs plutôt que de les subir.** `94` et `95`
cherchaient un signal qui prédise l'écart **à un maillage** ; `96` un signal calibré **contre**
lui. Les trois mesuraient contre une règle dont on sait maintenant qu'elle bouge de plus d'une
demi-feuille selon qui la tient. Le motif commun des deux anti-prédictions a d'ailleurs sa
raison, mesurée : **au bord, l'humain qui ne peut pas suivre la vraie feuille en trace une autre,
proprement** — le maillage épouse très bien UNE feuille, simplement pas la bonne. Donc ce qui
échoue au bord n'est pas la **qualité locale** mais l'**identité** de la feuille, et aucune
observable locale ne peut la voir par construction.

### ⭐⭐ CE QUE ÇA ALIGNE AVEC LE PRIX, ET C'EST UNE BONNE NOUVELLE

[`31`](docs/31_roadmap.md) §1 cite le critère du prix mot pour mot : **100 % du recto déroulé**,
un **rendu sur lequel l'encre est visible**, jugé par leurs papyrologues à **70 %** des
caractères lisibles par colonne. Le critère d'acceptation n'est donc **pas** la ressemblance à un
maillage humain — c'est la lisibilité d'un rendu, que la **matière** tranche.

> ⭐ La campagne ne bute donc pas sur le prix : elle démontre que la voie « imiter le maillage
> humain » est fermée, et que la voie « interroger la matière » est la seule qui reste — ce qui
> est exactement ce que le prix demande.

### ⭐⭐ L'INSTRUMENT QUI EST PRÊT, ET CE QU'IL VAUT

`98` livre le premier critère dont le seuil ne vient **ni d'un maillage ni d'un réglage** : entre
une cellule et le point situé un pas de feuille plus loin, le profil doit valoir
*brillant – sombre – brillant*. Un **filtre adapté** le lit, et il est **invariant en amplitude
et en décalage** — donc rien n'est à adapter au rouleau, ce qui répond à la question de l'auteur
autrement qu'en adaptant un seuil. La barre vient d'un **modèle nul fabriqué** (p99 du bruit
blanc, **0,3311**), indépendant de σ.

| | mesuré |
|---|---|
| fixture : bon nombre d'interstices ET bon côté | **1,000** jusqu'à un bruit **égal** à l'amplitude |
| réel : la matière répond | **74 %** au cœur, **54 %** au bord |
| réel : accord médian | 0,457 au cœur, **0,353** au bord pour une barre de 0,3311 |
| réel : part confirmée à un interstice | 0,557 → 0,518, **−0,411** avec la rupture |

⚠⚠ **Sa limite est nommée** : au bord l'accord frôle la barre et la matière ne répond que la
moitié du temps. Cohérent avec `94` — le maillage y a **enjambé** ce qu'il ne pouvait pas suivre,
donc il n'y a pas toujours de matière à interroger. **Là où le transfert casse, la matière est
presque muette**, et c'est la contrainte dure que la suite doit affronter.

### ⏳ CE QUE LA CAMPAGNE DÉSIGNE COMME SUITE

| # | quoi | pourquoi maintenant |
|---|---|---|
| ~~**A**~~ | ~~faire de `98` une règle de décision~~ | ✅ **FAIT** → [`99`](docs/99_le_pas_que_la_matiere_montre.md). Le balayage rend le pas que la matière montre : **198,9 µm au cœur, 214,05 au bord** contre **173** nominal, et **>81 %** des cellules à plus d'un dixième — un pas constant est faux **quatre fois sur cinq**. ⭐⭐ Et la part où la matière répond corrèle **−0,845** avec la rupture, le signal au bon signe **le plus fort de la campagne**. ⛔ Deux erreurs de nul payées : le premier résultat (147 µm) était **indiscernable du bruit pur**, et la barre comparait le max de 62 essais au nul d'un seul. ⭐⭐⭐ **Un modèle nul doit s'appliquer à CHAQUE quantité qu'une recherche rapporte, pas seulement à sa confiance** |
| **A bis** ⭐⭐ | l'écart **non expliqué** entre le pas de la matière (199 µm) et celui des transferts humains (`91`, 164 µm) | 9 à 21 % : `97` rend un désaccord attendu, son AMPLEUR non. ⛔ **Un candidat éliminé le 2026-09-09** → [`100`](docs/100_la_normale_nest_pas_le_rayon.md) : l'obliquité de la nappe n'explique PAS l'écart — le pas lu le long de la **normale** égale le pas radial (rapport médian **1,018**, corrélation contre `1/cos` **+0,153**) là où l'obliquité en prédirait **1,184**. ⚠⚠⚠ L'accord **1,212 contre 1,213** était une **coïncidence**, le piège de la sagitta de `94`. ⭐⭐⭐ Mais le test laisse un fait **plus lourd** : la normale du maillage est à **34,1°** du rayon là où une spirale de ce pas en prédit **0,09°** — **378 fois** moins, confirmé par un estimateur **indépendant de la grille** (ACP, 33,6°). La surface tracée n'est **pas** une spirale vue de face : **14,6°** hors du plan (feuilles coniques) et **24,0°** dedans (section non circulaire) |
| **A quater** ⚠ | `src/nappe/la_longueur_locale_du_pas.py` fait la **même** lecture sur l'AUTRE objet, mais valide **contre les spires publiées** — un référent que `97` a montré non fiable, et son gabarit est pris **sur la surface de départ**, dont `98` mesure qu'elle est dans un interstice une fois sur deux | ⚠ Il n'a PAS été touché : `99` a porté le balayage sur `PHercParis4` plutôt que de modifier l'existant, parce que c'est là que sont les 92 vrais transferts. Le rapprocher des deux est un lot à soi |
| **B** ⭐⭐ | mesurer ce que la matière dit là où elle **répond** (mi-rayon, 74 %) plutôt que là où elle se tait | le graal demande 31 spires ; commencer par la zone où le critère est net est le seul ordre qui produise une marche mesurable |
| **C** ⚠ | le **bord** : quand la matière est muette, aucun critère local ne peut trancher | c'est le vrai mur, et il est maintenant **chiffré** plutôt que soupçonné |
| **D** | les deux `.venv` sous `src/` (27 245 fichiers), 482 lanceurs gelés dans `.lances/gel` | dette d'arbre, sans effet sur la mesure |

⚠⚠ **Ne pas re-tenter** : le pli (`94`), la pose sur la matière (`95`), et toute calibration
d'un signal **contre un maillage humain** (`97`). Trois négatifs mesurés, chacun avec son
contrôle, chacun avec sa raison écrite.

### ⚠⚠⚠ LES DÉFAUTS D'INSTRUMENT PAYÉS DANS CETTE CAMPAGNE, à ne pas repayer

- **Une sonde sur trois bandes prise pour le corpus** (`95`) : `w128-129` est l'une des deux
  seules bandes dont le contraste s'effondre. *Un bord se compte sur le corpus entier, pas sur
  les bandes qu'on a sondées* — la faute de `93`, réécrite.
- **Un balayage à sous-ensemble variable** (`96`) : 28 bandes à un tour contre 5 à cinq, et les
  cinq sont les plus internes donc les plus propres. Le confondant retiré rend le fait **plus**
  fort.
- **Un centre indexé par cellule** (`96`) alors que l'axe dérive de 12,6 mm : **22 %** des
  fermetures sortaient négatives.
- **Une garde qui supprimait ce qu'elle devait laisser mesurer** (`97`) : un critère de bord
  mesuré dans l'espace mélange « être au bord » et « être loin de la surface », donc il écartait
  exactement les points où les deux humains divergent. Mesuré dans le **plan tangent**, le
  désaccord publié **double**.
- **Un estimateur qui mesurait la grille** (`97`) : au tiers du **cœur**, le plus proche voisin
  rend **270,8 µm** quand le plan local rend **121,7** — parce qu'il mesure l'**espacement des
  rangs** de l'autre révision. *Une limite de grille publiée comme une limite de matière.*
  ⚠ Le vérificateur de chiffres ne sait pas de quel tiers un nombre parle, donc il signalait
  ce 270,8 comme périmé pour les tiers milieu et bord : nommer le tiers lève l'ambiguïté.
- **Des gabarits de signe inversé** (`98`), trouvés en **lisant les comptes** : 40 % des profils
  appariés à un gabarit signifiant « la cellule est dans un interstice », publiés sous le nom
  « zéro interstice ».
- **Un test de platitude aveugle au cas dégénéré** (`98`) : un profil exactement constant a une
  étendue nulle **et** un bruit nul, donc `0 < 4×0` est faux.
- ⚠⚠ **Une fixture qui posait sa cellule là où la matière ne la pose pas** (`100`) : avec un rayon
  de départ **rond** et un pas de 173 µm, la cellule tombe à la **phase 0,80** d'une période — ni
  sur une feuille, ni dans un interstice — donc **aucune** des deux polarités du gabarit ne peut
  correspondre, et le contrôle rendait **242 µm** pour 173 injectés. *Un contrôle doit poser sa
  cellule là où la matière la poserait.*
- ⭐⭐⭐ **Deux angles morts de figure, refermés dans le module commun** (`100`) : la docstring de
  `textes_debordants` nommait elle-même le premier — un texte peut tenir dans la **toile** en
  débordant de son **panneau**, où il recouvre ce que le voisin dit. Le second est plus silencieux
  encore : un texte parfaitement placé mais **écrit par-dessus** un autre. `textes_hors_cadre` et
  `textes_qui_se_recouvrent` ont mordu **cinq fois** sur la figure de cette tranche même, dont une
  paire que l'œil avait vue avant la garde. ⚠ Marge à **zéro** : une marge choisie pour que la
  figure du jour passe serait un seuil réglé sur ce qui passe.
- ⭐⭐ **Un verdict qui ne pouvait pas dire l'inverse** (`100`) : le contrôle est lancé **dans les
  deux sens** — sur une fixture dont le rapport **suit** `1/cos`, le verdict doit dire que
  l'obliquité explique. Un verdict qui répond « réfuté » quoi qu'on lui donne ne tranche rien.
- ⭐⭐ **Un modèle nul appliqué à la confiance mais pas à la valeur** — et son pendant ici : un
  résultat **négatif** doit prouver que son instrument n'est pas **aveugle**. Sur un empilement
  fabriqué d'angle connu, le même instrument lit **1,238** pour **1,221** attendu.
- ⛔⛔ **Une garde choisie sur le mauvais invariant** (`101`) : la **planarité** paraissait le juge
  naturel de « la matière a-t-elle une orientation ici », et un bruit isotrope écrase le
  **rapport** des valeurs propres sans déplacer la **direction** — à σ = 15 elle retombe à
  **0,345**, le niveau du bruit pur, là où la direction est encore juste à **7,51°**. Fermer sur
  elle aurait supprimé ce qu'elle devait laisser passer. La garde retenue — l'accord des **deux
  moitiés disjointes** du cube — n'a besoin d'aucun modèle nul.
- ⚠⚠⚠ **Une garde qui MENTAIT, et son mensonge venait de `np.gradient`** (`101`) : ses plans
  extrêmes prennent des différences **unilatérales**, de variance **×4**, donc couper un cube en
  deux crée un nouveau bord en z et biaise les **deux** moitiés vers z. Sur du **bruit pur** elles
  s'accordaient à **10,4°** au lieu des **~60°** du hasard : la garde paraissait stricte tout en
  laissant passer du bruit, et la direction mesurée aurait été tirée vers z. *Un estimateur qui
  mesure la grille*, troisième costume.
- ⛔ **Un faux zéro publié comme un résultat** (`101`) : une corrélation calculée sur une liste
  vide rend **+0,000**, ce qui se lit « rien ne corrèle » alors que cela veut dire « la donnée
  n'est pas jointe ». Une corrélation sans donnée est désormais **déclarée absente**. Même zéro
  que le compteur que personne ne remplissait.
- ⚠⚠ **Un angle transporté d'un volume à l'autre sans vérifier que la transformation conserve les
  angles** (`101`) : un cisaillement rendrait « 34° » vide de sens, et l'écart serait silencieux.
  Mesuré : conditionnement **1,0075**, défaut **0,301°**. Et une **direction** ne se transporte
  pas comme un point — la translation ne s'y applique pas.
- ⛔⛔ **Une vérification qui ne pouvait pas échouer, et le témoin passait huit pas sur huit**
  (`102`) : je vérifiais chaque pas avec le **balayage** de `99`, qui cherche la meilleure période
  le long de la direction donnée — or sur un empilement oblique à 35° la période **radiale** vaut
  `173/cos(35°) = 211 µm`, **dans la fenêtre**, donc il la trouve et confirme. Elle testait « la
  matière est-elle feuilletée ici » — vrai partout — au lieu de « le pas a-t-il franchi UNE
  feuille ». ⭐ Corrigé en **séparant les deux rôles** : `99` décide de combien avancer, `98`
  vérifie à gabarit **fixe** ce que l'avance a traversé. Après correction : naïf **1**, matière
  **8**.
- ⛔ **Un zéro mesuré affiché comme « pas de donnée »** (`102`) : `x or float('nan')` traite `0.0`
  comme faux, et un témoin qui confirme **zéro** pas est le résultat le plus informatif qu'il
  puisse rendre. Corrigé par `nombre_ou_absent`, **une seule** définition, avec sa fixture. Même
  famille que le faux zéro de corrélation de `101` : *zéro et « on ne sait pas » ne doivent jamais
  partager une représentation.*
- ⚠⚠⚠ **Un bord compté sur les bandes qu'on a sondées** (`103`) — la faute de `93`, réécrite par
  `95`, **repayée par moi**. Une sonde à **2 bandes** approuvait une économie de lecture (0 % de
  cellules hors tolérance) ; les **28 bandes** disent **7,3 %**. ⭐ Elle a été attrapée parce que la
  règle était écrite et que j'ai relancé sur le corpus **avant** de publier, pas par une relecture.
- ⭐⭐⭐ **Un taux par pas se lit avec sa conséquence ENCHAÎNÉE** (`103`) : `1 − (1 − p)^k`. 7,3 %
  par pas paraissent inoffensifs et abîment **36,5 %** des marches de six pas. Publier le premier
  sans le second laisserait croire l'économie sans danger.
- ⚠⚠⚠ **Le coût d'une lecture distante se MESURE, il ne se modélise pas** (`103`) : le comptage de
  points prédisait **×7,44**, la mesure rend **×1,72**. Il suit les **plages d'octets** — une par
  rangée — plus un fixe par cube. Le modèle était faux d'un facteur quatre.
- ⚠⚠ **Un contrôle qui asserte le RÉSULTAT** (`103`) : « un pas plus grossier est retenu » aurait dû
  être réécrit le jour où la réponse change, c'est-à-dire un contrôle incapable d'échouer
  honnêtement. Les contrôles sont devenus **structurels** — le verdict est rendu, chaque refus
  porte sa raison et sa conséquence, la référence n'est pas jugée.
- ⚠⚠⚠ **Une mesure de SEPT HEURES qui n'imprime rien** (`102`) : il a fallu chronométrer une sonde
  pour savoir s'il fallait l'attendre ou la tuer, c'est-à-dire décider sans donnée — ce que ce
  dépôt refuse partout ailleurs. Les trois mesures longues impriment désormais leur avancement
  **sur stderr**, jamais sur stdout, qui peut être redirigé ou lu par un autre programme.
- ⚠⚠⚠ **Et un garde qui accusait à tort, trouvé en écrivant ce bloc même** —
  `verifier_chiffres` signalait **six** citations périmées dans ce fichier, et **les six étaient
  fausses**, dont **deux sur du texte fraîchement écrit et correct**. Cause : le diagnostic
  remplace les chiffres d'une écriture attendue par un joker, donc `**276,9 µm**` devient
  `**<nombre> µm**` et `0,55 % à 86,00 %` devient `<nombre> % à <nombre> %` — des formes que
  toutes les phrases de mesure du dépôt partagent. ⭐ **Ce qui discrimine est le nom de la
  quantité**, jamais une unité ni un connecteur, et il en faut **deux** : un seul nom (`N
  segments`, `N fois`) est partagé par des quantités différentes. C'est la **quatrième** et
  **cinquième** occurrence du même mode d'échec dans ce fichier, dont la docstring nommait déjà
  les deux premières — *« un garde qui crie à tort finit ignoré »*.
  ⚠⚠ **Et le prix du resserrage est mesuré et publié plutôt que subi** : seuls **15 motifs sur
  568** peuvent encore accuser, donc le diagnostic PÉRIMÉ est presque muet. Ce qui tranche est
  qu'**ABSENT est la détection et il est intact** — PÉRIMÉ n'ajoute que *où* vit l'ancienne
  valeur, une commodité. ⛔ **Ne pas assouplir `perimee` en constatant son silence** : le silence
  est le prix choisi, et un contrôle le rend visible.
- ⭐ **Et une leçon d'estimateur qui se généralise** (`98`) : *une proéminence exprimée en unités
  du bruit propre au profil est invariante d'échelle, donc lisser abaisse le bruit ET le seuil
  ensemble.* La discrimination vient de la **forme**, jamais de la profondeur.

---

## ⭐⭐⭐⭐ REPRISE — 2026-09-03

**Douze commits depuis le 2 septembre.** L'arbre est propre, les sept gardes sont vertes,
l'article fait **27 pages**. Ce bloc remplace le précédent comme état courant ; tout ce qui
suit est l'historique, y compris l'ancienne REPRISE du 28 août.

### Ce qui a été tranché, et l'ordre importe

**1. ⭐⭐⭐ Le papier de référence lu EN ENTIER**, figures et Supplementary comprises →
[`68`](docs/68_lire_le_papier_en_entier.md). Le [`27`](docs/27_ce_que_la_litterature_dit.md)
l'avait lu pour *auditer sa nouveauté* ; relu pour *refaire sa méthode*, il rend quatre
choses que la première lecture ne pouvait pas voir. Les 775 heures humaines tiennent à **une
étape sur dix-sept**, un **pinceau** (`ApprovalMaskBrushTool`), et son interface est un
fichier : écrire `approval.tif` à côté de `x/y/z.tif` **est** l'intégration entière.
Les « trois paramètres couplés » n'en font **qu'un**, $F = \sqrt{\lambda D}/p$, qui ordonne
les verdicts publiés. Et **103 cases vides** du régime du prix sont publiées en couches
rendues, sans carte d'encre, **avec un témoin positif sur le même segment**.

**2. ⭐⭐⭐ Les 70 documents lus INTÉGRALEMENT** → [`70`](docs/70_ce_que_larticle_condense.md)
et [`registres/fiches_de_lecture.md`](docs/registres/fiches_de_lecture.md). Le compte :
**22 procédé, 21 dans l'article, 27 dehors**. Non, 27 pages ne contiennent pas tout — mais un
tiers du corpus est le *procédé*, qu'aucun article ne contient.

**3. ⭐⭐ Les trois résultats de tête audités** → [`71`](docs/71_les_trois_resultats_de_tete_audites.md).
**PARTIELLEMENT** tous les trois. Le mécanisme du tirage était **dans le code publié**
(`srand(clock())`) ; la moitié « propreté » du budget est **déjà publiée sur 278 traces** ;
le discriminant du pavage est **celui du code de référence**. Et un argument **récupéré** :
le vérificateur est garanti déterministe, donc une bascule de verdict **prouve que la surface
a changé**. L'article porte les trois corrections.

**4. L'article a gagné trois sections** — §6.2 (ce que coûte un point estimé), §6.6 (le juge),
§6.7 (où ça se branche) — parce que sa §2.4 annonçait trois apports et n'en livrait qu'un.
Plus le caveat du `33` en §6.1. **44 chiffres gardés**, tous recalculés depuis leur fichier.

### ⚠⚠ Ce qui a été DÉTRUIT, et c'est le plus important à savoir

**La conclusion-titre du [`07`](docs/07_reparee_nest_pas_propre.md) ne tient pas.** En voulant
rendre son chiffre recalculable pour l'article — réparer une trace, remesurer — la proximité
**baisse de 22 à 50 %** là où le document publie qu'elle ne bouge pas, et **pas
proportionnellement à ce qui est retiré**. La section que le `70` recommandait n'est donc
**pas écrite**. ⚠ Le cas discriminant (une trace peu atteinte) **n'est pas montable** : la
métrique exige plus d'un tour et sur ce rouleau toutes les traces longues sont les plus
atteintes.

**Et une correction du `07` §9 était elle-même fausse** : `PHerc1667` publie bien un scan à
7,91 µm. **Troisième occurrence du même angle mort** — interroger une vue du corpus et
conclure sur le corpus — après `59` et `67` §4.2. D'où un garde-fou plutôt qu'une troisième
correction : `src/volume/ou_vit_ce_rouleau.py`.

### ⚠⚠⚠ Deux gardes qui ne pouvaient pas voir ce qu'elles gardaient

- **`verifier_citations` comptait 88 sur 140.** Son motif ne connaissait qu'une des trois
  écritures de numéro de ligne, donc **44 citations sur 132 n'étaient jamais vérifiées**. Elle
  ne mentait pas sur ses 88 : son **dénominateur** était le sous-ensemble qu'elle savait lire.
  Corrigée, et surtout : elle **compte les lignes de preuve illisibles et échoue dessus**, et
  signale la **dérive** d'une citation dont le document a bougé. Elle a servi dès son premier
  usage réel.
- **`espacement_spires` tournait au niveau 2** de pyramide, qui fusionne les feuilles
  voisines — mesuré 36/36 par `winding-ruler`. Notre propre chiffre (« 89 % des murs
  conservés ») **était** le défaut, lu comme une vertu. Défaut passé à 1.

### ⭐ Un résultat neuf, tombé d'une prémisse fausse

**Un axe de rouleau n'est pas une droite** → `src/excision/laxe_nest_pas_une_ligne.py`.
L'ombilic **est** publié (241 points), et il erre de **21,6 mm sur 108 mm** de hauteur : le
remplacer par un centre unique coûte **16,75 mm au pire, soit 148 écarts inter-feuilles**.
⭐ Avec le contre-contrôle : le balayage de sensibilité **encadrait** cette dérive et
l'invariant n'y bouge que de **1,85 %** — la conclusion tient, sur une mesure cette fois.

### Ce qui reste, dans l'ordre

| | |
|---|---|
| **refonder l'arc excision** (`03` `04` `05` `07`) | le plus gros manque de l'article, et sa conclusion vient d'être déstabilisée |
| **le second papier, côté encre** | `58` `59` `63`, `68` §3-4, et la **case vide** à remplir |
| **`docs/69`** | écrit par Fable, **non lu** sur consigne de l'auteur |
| le contrôle P1 bis du `71` | ×15,9 exigé contre ×3,8 observé, à faire tourner |

### ⚠⚠⚠ UNE DÉCISION ATTEND L'AUTEUR — 2026-09-08 : l'objet courant ne peut pas porter la preuve

Mesuré et versionné ([`81`](docs/81_le_rouleau_designe_ne_publie_rien.md),
`src/depot/les_spires_consecutives_publiees.py`, confronté à S3) :

| objet | spires **consécutives** publiées |
|---|---:|
| `PHercParis4` | **120** (w010..w129, zéro trou) |
| `PHerc0172` | **44** |
| `PHerc0139` (le témoin de la carte) | **37** |
| `PHerc1667` (l'objet des 775 h) | 14 (19 rangs, 12 trous) |
| **`PHerc0500P2` — l'objet courant** | **13** |
| **les treize rouleaux du Grand Prize** | **0** |

⭐⭐ Une portée ne se mesure que jusqu'où le corpus publie des spires consécutives : au-delà du
dernier rang publié d'affilée, il n'existe plus rien contre quoi dire qu'on a franchi une spire de
plus. **Le prix en demande 31.** Sur `PHerc0500P2`, les tenir n'est donc pas seulement difficile —
c'est **invérifiable**, et aucun travail sur cet objet-là ne changera ça.

⚠⚠ Et la décision de septembre de [`31`](docs/31_roadmap.md) §10 tombe avec : **onze des treize
rouleaux du prix ne publient aucun segment, et les treize aucun rang de spire.** Son critère
n'était pas seulement 315× hors budget — sa réponse n'est pas exécutable.

> ⚠ **Le changement d'objet est la décision de l'auteur, pas la mienne.** Ses deux coûts sont
> nommés : tout ce qui est calibré sur `PHerc0500P2` (voxel 2,215 µm, pas nominal 135,5 µm, boîte
> et ancres) est à re-dériver, et la **demi-feuille de 67,75 µm est une mesure DE CET OBJET**, donc
> à remesurer avant d'être réutilisée comme critère ailleurs.

⚠⚠⚠ **Et l'audit qui a suivi ([`82`](docs/82_la_borne_etait_le_mur.md)) montre que le corpus ne
borne pas seulement ce qu'on peut PROUVER, il borne ce qu'on peut APPRENDRE.** Les spires 10 et 11
de `PHerc0500P2` se suivent par leur numéro et sont à **1000,6 µm** l'une de l'autre — 12,8× le
décalage que la famille sait appliquer — donc **l'oracle est collé au plafond du corpus sur les
cinq ancres**. « La borne vaut 6 » n'est pas établi : la vraie borne est **inconnue et ≥ 6**, et la
marge entre le meilleur marcheur aveugle et elle pourrait être bien plus grande qu'un bras.

★★ Ce qui **tient** : à l'ancre 4 le plafond vaut 6, le pas normal (4) et sa version lissée (5)
sont sous le plafond, donc le gain d'un bras par le lissage n'est pas touché. Ce qui tombe est la
**borne**, pas le résultat.

⛔⛔ **Et déplacer la boîte n'y change presque rien** ([`83`](docs/83_le_corpus_et_non_la_boite.md)) :
sur **1296 placements**, 597 n'offrent même pas un bras, la boîte actuelle atteint 6, **16 font
mieux**, et le meilleur du fragment vaut **8** — un **minorant**, puisqu'un treillis plus fin trouve
plus. 40 % des bras de tous les placements sont hors du pas nominal, et **aucune paire de spires ne
varie de moins d'un facteur dix** selon l'endroit (`10→11` : 19,4 à 1224,8 µm, ×63).

★ **Disponible et sans engagement** : poser la boîte en `8655 10820 21924` au lieu de
`10615 10571 19831` rend **+2 bras de dynamique** à toutes les comparaisons de marcheurs, sans
changer d'objet ni recalibrer quoi que ce soit.

⭐⭐⭐ **ET LE FAIT QUI PÈSE LE PLUS LOURD SUR LA DÉCISION D'OBJET**
([`84`](docs/84_une_surface_combien_de_spires.md)) : `PHercParis4` publie ses 120 spires en **28
bandes multi-spires**, donc **92 franchissements de spire contenus dans une seule maille**. Les
cinq autres objets du corpus — `PHerc0172`, `PHerc0139`, `PHerc1667`, `PHerc0500P2`, `PHercMANBp` —
publient **une spire par surface, sans exception**, donc **zéro**. Or le goulot de l'objectif
**est** le transfert de spire à spire : **la vérité de terrain de ce goulot existe sur un objet, et
un seul.**

⚠⚠ Et la plus longue bande vaut **18** spires contre les **31** du prix : même le corpus le plus
riche du concours ne contient pas une marche entière. Mais c'est la première fois que la portée de
ce dépôt peut se comparer à du **travail humain publié** plutôt qu'à une borne censurée.

⭐⭐⭐ **LE PREMIER CRITÈRE DONT LE SEUIL VIENT DE LA MATIÈRE, ET IL EST FAIBLE LÀ OÙ IL COMPTE**
([`98`](docs/98_combien_dinterstices_traverses.md)). `97` a mesuré qu'aucun signal calibré contre un
maillage humain ne peut l'être, donc il fallait un critère que la **matière** tranche : entre une
cellule et le point situé un pas de feuille plus loin, le profil doit valoir *brillant – sombre –
brillant*, soit **un** interstice. Mesuré sur les 28 bandes à 2,4 µm : la part confirmée vaut
**0,557 au cœur, 0,536 au milieu, 0,518 au bord**, et **baisse** avec la rupture de continuité
(**−0,411**) — signe correct, et **premier seuil matériel** de la campagne.

⚠⚠ **Et faible là où ça compte** : au bord l'accord médian vaut **0,353** pour une barre de
**0,3311**, et la matière ne répond que **54 %** du temps contre 74 % au cœur. Cohérent avec `94` :
au bord le maillage a **enjambé** ce qu'il ne pouvait pas suivre, donc il n'y a pas toujours de
matière à interroger.

⭐⭐⭐ **LA QUESTION DE L'AUTEUR — « faut-il être adaptatif par rapport au rouleau ? » — ET SA
RÉPONSE.** Oui, et la mesure la rend plus forte : dans **une seule bande du bord** l'étendue du
profil varie d'un facteur **146**, et de 2,4 au milieu, donc une constante par rouleau serait déjà
un paramètre ajusté. Mais la bonne réponse n'est pas d'adapter le seuil, c'est de **choisir une
quantité qui n'en a pas besoin** : une **corrélation normalisée** est invariante en amplitude ET en
décalage. Asséré — mettre signal et bruit à l'échelle ×0,05 puis ×50 laisse le score identique au
bit près. Et le seuil vient d'un **modèle nul fabriqué** (p99 du bruit blanc, **0,3311**),
indépendant de σ, ce qui est le contrôle qu'aucun paramètre ne se cache dedans.

⭐⭐ **Un second verdict gratuit** : la cellule part **sur** une feuille une fois sur deux. ⚠⚠⚠ Deux
lectures opposées se cachaient derrière ce 0,49 — un vrai désaccord ou un **tirage** entre gabarits
à égalité — et seule la **marge** les sépare : 0,376, comparable à l'accord (0,457), avec **81 %**
de polarités franches. Donc l'instrument tranche, et **la moitié des cellules du maillage humain
partent d'un interstice**.

⛔⛔ **Le compteur de minima est réfuté**, et son échec se généralise : à ×3 le bruit pur passe à
98,8 %, à ×6 un interstice réel n'est vu que 6 %. Lisser fait monter la détection à 0,95 sans rien
changer aux faux positifs, parce qu'**une proéminence en unités du bruit propre au profil est
invariante d'échelle — lisser abaisse le bruit ET le seuil ensemble**. La discrimination vient de la
**forme**, pas de la profondeur.

⚠⚠⚠ Trois défauts payés, gardés : les gabarits étaient de **signe inversé** (40 % des profils réels
appariés à un gabarit signifiant « la cellule est dans un interstice », publiés sous le nom « zéro
interstice ») ; le test de platitude ne voyait pas le cas **exactement constant** (`0 < 0` faux) ;
et l'estimateur de bruit prenait une différence **première**, qui lit la pente du signal cherché.

⭐⭐⭐ **DEUX HUMAINS SUR LA MÊME MATIÈRE DIVERGENT DE PLUS D'UNE DEMI-FEUILLE, PARTOUT — LE
PLANCHER EST CHIFFRÉ** ([`97`](docs/97_deux_humains_sur_la_meme_matiere.md)). `96` a nommé ce qui
manquait, un **référent**, et le dépôt en télécharge un depuis le début sans l'avoir employé :
chaque bande existe en **deux révisions**, soit deux tracés humains **indépendants** de la même
matière. Leur désaccord vaut **121,7 µm au cœur, 110,9 au milieu, 106,6 au bord**, pour une
demi-feuille de **82 à 91 µm** (`91`) — donc plus d'une demi-feuille l'un de l'autre, et **34 %**
des points à plus d'une feuille **entière**. ⭐ Et c'est **PLAT** (+0,081 avec le rayon) : pas un
problème de bord, un plancher. ⚠ **Aucune translation systématique** — restreint au recouvrement en
z, le vecteur moyen tombe à 8–38 µm.

⛔⛔ **ET LA CIBLE D'UN AUTOMATE NE PEUT DONC PAS ÊTRE « ÉGALER LE MAILLAGE HUMAIN », parce que
cette cible n'a pas de valeur unique.** Le prix demande d'automatiser un travail dont l'état de
l'art ne reproduit pas sa propre sortie à une feuille près. La cible doit être un critère que la
**matière** tranche, pas un maillage. ⭐ Et ça donne un sens neuf aux trois échecs précédents : `94`,
`95` et `96` mesuraient tous contre une règle dont on sait maintenant qu'elle bouge de plus d'une
demi-feuille selon qui la tient.

⛔ Ce référent ne **calibre pas** la fermeture pour autant : le désaccord ne suit ni le rayon
(+0,081), ni la rupture (−0,097), ni la fermeture (**+0,079**).

⛔⛔ **Et l'estimateur naïf était réfuté**, gardé publié : au plus proche voisin le désaccord rend
270 à 315 µm contre 107 à 122 au plan local, parce qu'il mesure l'**espacement des rangs**
(~800 µm) de l'autre révision — un point à mi-chemin entre deux rangs en est loin **même si les
deux surfaces coïncident**, ce que la fixture montre en rendant une distance non nulle sur deux
surfaces identiques. Le publier aurait été publier une limite de **grille** comme une limite de
**matière**.

⚠⚠⚠ Et une **garde à moi qui supprimait ce qu'elle devait laisser mesurer** : mon critère de bord,
mesuré dans l'espace, ne descendait jamais sous 0,354 sur deux plans décalés, donc il aurait écarté
exactement les points où les deux humains divergent le plus. Mesuré dans le **plan tangent**, le
désaccord publié **double** (53 → 122 µm). *Une garde qui supprime ce qu'elle doit laisser mesurer
est pire qu'aucune garde.*

⭐⭐⭐ **LE PREMIER SIGNAL DONT LE SIGNE EST LE BON — ET LE RÉFÉRENT QUI MANQUE POUR LE CALIBRER**
([`96`](docs/96_la_fermeture_dun_tour.md)). `95` a laissé que ce qui échoue au bord est l'**identité**
de la feuille, donc que le signal doit être **topologique**. La **fermeture** en est un : partir
d'une cellule, faire **un tour complet**, et le rayon doit avoir monté d'**un** pas de feuille —
zéro voudrait dire qu'on est revenu sur la même, deux qu'on en a sauté une, et aucune supervision
n'entre. Mesuré sur les 28 bandes : la part de cellules hors de la demi-feuille vaut **0,621 au cœur
et 0,804 au bord**, corrélations **+0,858** avec le rayon et **+0,822** avec la rupture — là où le
pli donnait −0,825 et la pose sur la matière −0,694. **Premier renversement de signe de la
campagne.**

⚠⚠⚠ **Et elle ne certifie pourtant aucune cellule** : 0,621 au **cœur**, là où la continuité est
intacte. ⭐⭐⭐ Le **balayage de fenêtre** dit pourquoi, sans aucun seuil : du bruit se moyenne quand
la fenêtre s'allonge, une structure non. Allonger ×5 fait tomber le réel de **11 %** (0,556 → 0,495)
quand le même estimateur écrase un bruit blanc à **zéro** (0,312 → 0,000). L'irrégularité radiale
des maillages humains n'est donc **pas du bruit**.

⛔ **CE QUI MANQUE N'EST PAS L'INSTRUMENT MAIS UN RÉFÉRENT.** La fixture prouve que l'estimateur
**sait** détecter une feuille sautée (0,096 contre 0,004 à trois tours) ; ce sont les maillages
humains qui ne ferment pas eux-mêmes à la demi-feuille près — **62 % des cellules y échouent au
cœur**. Une confiance par cellule bâtie sur la fermeture est donc **écrivable et non calibrable**
avec ce corpus. ⭐ Même plancher que `95` sur un autre axe : *l'erreur du référent, pas la mienne* —
`95` mesurait que la surface publiée n'est pas **sur** la feuille, `96` qu'elle ne **ferme** pas.

⭐⭐ **Et la médiane est aveugle là où la part voit** : sur une spirale fabriquée où **une feuille
est sautée**, la fermeture médiane reste à **1,000** pendant que la part hors demi-feuille l'attrape.
C'est pourquoi la pente globale de `91` — une droite ajustée sur tout le rang — ne pouvait pas la
voir, et pourquoi la part est publiée avant la médiane.

⚠⚠⚠ Deux défauts payés, gardés : **le balayage a dû être refait à sous-ensemble constant** (28
bandes à un tour contre 5 à cinq, et les cinq sont les plus internes donc les plus propres — la
faute de `93`, et le confondant retiré rend le fait PLUS fort) ; et **le centre était indexé par
cellule** alors que l'axe dérive de 12,6 mm, ce qui faisait sortir **22 % des fermetures
négatives**.

⛔⛔⛔ **DEUX OBSERVABLES LOCALES ÉCHOUENT DE LA MÊME FAÇON, ET C'EST LE MOTIF QUI COMPTE**
([`95`](docs/95_la_surface_et_la_feuille_par_rayon.md)). `94` a tué le froissement parce qu'il est
une propriété du **maillage** ; il fallait donc une observable de la **matière**, et le dépôt en
avait une — l'écart entre la surface publiée et le ruban qu'elle suit — qui ne couvrait
`PHercParis4` que par **une bande**. Étendue aux 28, à 2,4 µm : la dispersion vaut **20,0 µm au
cœur et 13,85 au bord**, donc la surface humaine est **MIEUX posée** là où `92` mesure une
continuité brisée (×31) et `93` des spires désalignées (×3,67 au même tiers). Corrélations **−0,702** avec le
rayon, **−0,694** avec la rupture.

⭐⭐ **Le confondant est traité par trois chemins qui s'accordent** : le volume est masqué et la part
au remplissage monte à **+0,800** avec le rayon, donc sans la retirer « la surface est mieux posée
au bord » et « le volume s'arrête au bord » seraient la même observation. Brut −0,694, **partielle
−0,533**, et en **jetant** les bandes rongées −0,434 sur 16 bandes. ⭐⭐⭐ Et le seuil n'est pas
réglé, c'est **vérifiable** : le balayage publié donne −0,630 · −0,658 · −0,646 · −0,738 · −0,753
de 5 % à 30 % de remplissage toléré.

⭐⭐⭐ **ET LE VRAI RÉSULTAT EST LE MOTIF.** Deux observables locales indépendantes disent « plus
propre » exactement là où le transfert échoue. **Au bord, l'humain qui ne peut pas suivre la vraie
feuille en trace une autre, proprement : le maillage épouse très bien UNE feuille, simplement pas
la bonne.** ⛔⛔ Donc ce qui échoue au bord n'est pas la **qualité locale** mais l'**identité** de
la feuille, et une observable locale ne peut pas la voir par construction — elle mesure à quel point
on est bien posé sur ce qu'on suit, jamais si c'est ce qu'il fallait suivre. **Le signal à chercher
est topologique, donc global.**

⭐⭐ **Deux outils partagés livrés au passage, et ils valent au-delà de cette tranche** : les chunks
du dépôt sont écrits **sans compression**, donc un voxel se lit par requête `Range`
(`src/commun/voxel_distant.py`, 20,7 Go lus sans rien rapatrier) ; et la matrice
`45,532 µm → 2,4 µm` est **publiée** dans `metadata.min.json`
(`src/commun/transformations_de_volume.py`). ⚠⚠ Le volume fin n'est pas un luxe : à 45,532 µm un
demi-écart inter-feuilles vaut **deux voxels**, donc y mesurer un décalage de vingt micromètres
publierait une **limite de grille** comme une limite de matière.

⚠⚠⚠ **Et un résultat qui bougeait entre deux exécutions du même calcul** : une bande avait perdu
**25 cellules sur 90** par coupure réseau passagère, en silence, ce qui déplaçait la médiane du
tiers du bord de 13,85 à 13,1 µm. Les lectures sont désormais **réessayées** (pannes réseau
seulement — un code HTTP est une réponse, pas une panne) **et** le compte de pertes est **publié**
par bande : il faut les deux, un réessai qui échoue quand même laissant le même trou muet.

⚠⚠⚠ Et une erreur à moi, gardée : ma sonde exploratoire prenait **trois** bandes et voyait le
contraste tomber de 119 à 11 — or `w128-129` est l'une des **deux seules** bandes dont le contraste
s'effondre, et celle dont le remplissage est le plus fort. **Un bord se compte sur le corpus entier,
pas sur les bandes qu'on a sondées** — la faute que `93` avait déjà payée, réécrite autrement.

⛔⛔⛔ **LE FROISSEMENT NE PEUT PAS SERVIR DE SIGNAL DE CONFIANCE — IL EST ANTI-PRÉDICTIF**
([`94`](docs/94_le_froissement_mesure_la_rugosite.md)). `93` dit **où** le pas géométrique échoue ;
ce qui manque est un signal que le marcheur lit **tout seul**, et le **pli** était le candidat —
`75` le mesure prédictif **par cellule** (8 bras sur 8 chez le raccrochage, **un bras sauvé**).
Testé sur les 28 bandes humaines de `PHercParis4` : **15,2 µm au cœur, 3,8 au bord**, alors que la
continuité y passe de ×1,7 à **×31**. Corrélations **−0,957** avec le rayon et **−0,825** avec la
rupture. ⛔ **Un marcheur qui s'en servirait signalerait le cœur, où tout est propre, et se tairait
au bord.** ⚠⚠ Normaliser par la sagitta retire le rayon (−0,404) mais **pas le signe** (−0,678).

⭐⭐⭐ **Et ce que le champ mesure est établi par FIXTURE, pas par corrélation** : il prend la
**médiane** d'un voisinage 3×3, donc il est **exactement aveugle à la courbure lisse** — un
cylindre parfait rend **0,00 µm**, un cylindre à **axe courbe** (celui que `90` mesure) **0,00 µm**
aussi, et seul du bruit le réveille, **presque sans dépendre du rayon** (×1,10 entre R = 5 et
R = 20 mm).

⭐⭐ **Donc le verdict devient plus fort** : le réel tombe de **×5,2** du cœur au bord là où la
rugosité seule n'en donnerait que ×1,1, donc les maillages humains sont **cinq fois plus lisses au
bord**. Or un maillage lisse qui porte des **sauts de 30 mm** (`92`) et des spires **désalignées**
(`93`) a **enjambé ce qu'il ne pouvait pas suivre**. **La douceur au bord n'est pas de la qualité,
c'est la signature d'un pontage** — et un signal de confiance bâti dessus **classerait l'abandon
comme une réussite**, le pire mode de panne pour un automate lancé sans surveillance.

⚠⚠⚠ Et une **cause publiée puis rétractée avant commit** : j'expliquais la chute en 1/R par la
**sagitta** d'un cercle, avec un accord de **1,11 en médiane** sur 28 bandes. La fixture la réfute
d'un coup — elle prédit **20,2 µm** là où le champ rend **zéro**. ⭐ **Une corrélation sur
vingt-huit points ne vaut pas une fixture dont on connaît la réponse.**

⚠⚠ **La contrainte que ça laisse au remplaçant de l'humain** : une marche de 31 spires change le
rayon d'un **facteur six**, donc **tout signal de confiance doit être vérifié À TRAVERS les
rayons**, ou il classera par rayon en croyant classer par difficulté. Le pli reste valable **à
rayon constant** — `94` ne rétracte pas `75`, il borne l'autre axe.

⭐⭐⭐ **OÙ LES SPIRES SONT-ELLES PARALLÈLES ? AU MILIEU**
([`93`](docs/93_ou_les_spires_sont_elles_paralleles.md)) — un pas le long de la normale n'atterrit
sur la spire voisine que si elles le sont, et à 30° d'écart un pas de 182 µm tombe à **91 µm de
côté**. Mesuré : **×1,23 à mi-rayon** (quasi parallèles), **×4,18 au bord**, et **2 bandes non
résolues** au cœur par un critère **dérivé** (la rotation d'une cellule y dépasse la variation
locale). ⭐⭐ **Donc les deux modes d'échec sont au BORD** : la surface y est brisée (×31, `92`)
*et* les spires y sont désalignées. Au milieu, les deux sont propres — **un automate a un problème
localisé, pas uniforme.**

⚠⚠⚠ Et une erreur à moi qui avait **inversé** la conclusion : je comparais la bande 0 à la bande 7
en appelant la seconde « le bord », alors que les deux sont dans le tiers intérieur. **Un tiers se
compte sur le corpus entier, pas sur les premières lignes d'un tableau.**

⭐⭐⭐ **LES TRANSFERTS HUMAINS SONT CONTINUS AU CŒUR, BRISÉS AU BORD**
([`92`](docs/92_la_continuite_des_transferts.md)) : le plus grand saut entre cellules voisines,
rapporté au pas d'échantillonnage, vaut **1,7 · 5,9 · 31,0** du cœur au bord. ⭐⭐ **Là où le
rouleau est intact un humain trace continûment ; là où il ne l'est pas, MÊME UN HUMAIN rend une
surface discontinue** — donc un automate ne peut pas être jugé partout de la même façon, et
l'étendue qui tombe de 18 à 2 spires n'est pas seulement la circonférence, c'est la continuité qui
casse.

⚠⚠⚠ Et une corrélation de **r = 0,797** suggérait que ces sauts expliquaient le gonflement de
pente de `91`. **Le test direct la refuse** : les retirer change la pente de **0,2 %**. Une
corrélation entre deux quantités qui montent ensemble n'est pas un mécanisme. La cause de `91`
reste **non trouvée**, avec **trois** candidats réfutés.

⭐⭐⭐ **LE NOM D'UNE BANDE EST SA GÉOMÉTRIE, DONC LES 92 FRANCHISSEMENTS SONT 92 TRANSFERTS
RÉELS** ([`91`](docs/91_le_pas_lu_sur_les_transferts.md)) : l'étendue déclarée **est** le nombre de
tours mesuré — écart médian **−0,01 tour, 27 bandes sur 28**. Et le pas lu sur ces transferts vaut
**164 µm** contre **182,4 µm** à l'atlas, par deux chemins qui ne partagent ni donnée, ni méthode,
ni auteur. ⭐ La demi-feuille de `PHercParis4` est donc **établie** et non empruntée : **82 à
91 µm**, contre 67,75 sur l'objet courant.

⚠⚠⚠ Et un **gradient rétracté avant publication** : la pente brute suggérait une délamination du
bord (~1000 µm), c'est **l'estimateur** — sur UNE bande à pas constant par construction, rétrécir
la fenêtre de 10 à 1 tour donne 202 → **1817 µm**. ⭐⭐ **Règle : on ne mesure pas le pas d'un
enroulement sur un arc court.** ⚠ La cause n'est pas établie et c'est écrit : une section ovale
*dégonfle*, un centre décalé gonfle d'un dixième de ce qu'il faudrait.

⭐⭐⭐ **L'AXE DU ROULEAU EST UNE COURBE, ET ÇA CONTRAINT LE REMPLAÇANT DE L'HUMAIN**
([`90`](docs/90_laxe_est_une_courbe.md)) : le centre par tranche se déplace de **12,6 mm en x et
19,8 mm en y sur 144 mm de z, en revenant sur ses pas**, et s'écarte de sa **propre droite** de
**63,9 épaisseurs de feuille**. ⚠⚠ Un marcheur qui supposerait un repère cylindrique global se
trompe de **deux centimètres** — une centaine d'épaisseurs — donc **placerait une spire à la place
d'une autre**, ce qui *est* l'erreur que l'humain corrige. ⭐ **Aucun repère global ne remplacera
cet humain : ce qui le remplacera devra être LOCAL, comme la marche l'est déjà.**

⚠⚠⚠ Et `85` est **rétracté en partie** : son « second régime » de la bande du cœur (838 mm)
n'existe pas — c'était mon erreur d'axe, concentrée sur la bande la plus proche de l'axe. Sous
l'axe courbe elle vaut **460 mm**. ⭐ Ce qui **survit et survit mieux** : le classement (27/27 sous
trois modèles d'axe) et la courbe de coût, qui se **resserre** à ×1,68 au lieu de ×2,97.

⭐⭐ **Et le coût humain se compte en LONGUEUR DE FEUILLE, pas en nombre de spires**
([`85`](docs/85_le_sens_du_rang.md)) : le rang monte vers le dehors (27/27 montées de rayon, de
7,41 à 24,84 mm, verdict survivant à un second centre), et une passe humaine couvre **384 mm de
feuille en médiane** — hors la bande du cœur, les 27 autres tiennent dans **283 à 535 mm**, un
facteur 1,89. La même heure couvre donc **neuf fois moins de spires au bord qu'au cœur**, et
« 31 spires » n'est pas l'unité naturelle de l'effort.

⭐⭐⭐ **ET LE CRITÈRE LE PLUS PORTEUR DE TOUT L'APPAREIL EST AU PERCENTILE 27 DE SON OBJET**
([`86`](docs/86_la_demi_feuille_par_objet.md)). La demi-feuille de **67,75 µm** vient de 135,5 µm
mesurés sur 12 paires des 13 spires publiées de `PHerc0500P2` ; l'atlas de `winding-ruler` mesure
**196,6 µm** de médiane sur le **même** fragment (p25 131,1). Donc **les portées publiées — 4, 5,
6 — sont des BORNES BASSES** : à la demi-feuille médiane du fragment, le même marcheur aurait
**45 % de tolérance en plus**. ⚠ Ce n'est pas une contradiction mais une différence de
**population**, et l'atlas lisant des prédictions il **surestime** plutôt qu'il ne sous-estime.

⚠ Le coût du changement d'objet est donc chiffré, et il se lit dans les deux sens :
`PHercParis4` demi-feuille **91,20 µm** contre 67,75 local (**+34,6 %**), mais **98,3 → 91,2** à
médiane contre médiane, donc **7 % plus serré**. Celle qui compte dépend d'une région qui n'existe
pas encore pour le candidat.

■ **Et par le côté géométrique, le choix de rouleau ne se décide pas non plus** : les treize
tiennent dans un facteur **1,20** de demi-feuille (86,4 à 103,7 µm) quand l'atlas entier va
jusqu'à 1,71. **Deux critères indépendants concordent : rien dans les treize ne désigne un
rouleau.**

---

⭐⭐⭐ **L'ARCHITECTURE — la composition existe, et la provenance est devenue un fait OBSERVÉ**
([`87`](docs/87_la_forme_du_depot.md) le diagnostic, [`88`](docs/88_enchainer.md) l'outil).

`lplv enchainer <chaîne>` enchaîne des verbes, s'arrête à la première panne, et **observe** quel
verbe a écrit quel fichier. Mesuré : **6/6 étages en 2,71 s, 6 artefacts attribués au verbe
exact, sans une déclaration**. Deux chaînes livrées — `docs/chaines/les_spires_publiees.chaine` et
`les_gardes_de_larbre.chaine`.

⚠⚠ **Le diagnostic de `87` corrige une partie de la plainte** : **267/356** modules exposent
`--verifier` et **0** batterie n'est non enregistrée — **les tests ne sont pas la panne**. La panne
est la **retrouvabilité** : seuls **38 %** des 486 artefacts sont retrouvables par leur nom, et
`artefacts_orphelins` déclare « 0 orphelin » avec **46 % de son verdict sur ≤12 caractères**.

⛔ **ET IL NE FAUT PAS RE-PARTITIONNER LES DOSSIERS**, mesuré par cohésion de vocabulaire de
domaine (AST, co-occurrence) : rapport global **×1,89**, `tracecheck` **×0,61** (sous le hasard).
Un reclassement gagnerait peut-être ×3 pour **353 déplacements**.

⭐⭐⭐ **ET `artefacts_orphelins` EST DEVENU UNE ÉCHELLE** ([`89`](docs/89_lechelle_de_la_provenance.md)) :
il ne dit plus « produit » mais **par quel barreau** — **3 observés** par une chaîne, **1111
devinés** par une tige (dont **675 sur ≤12 caractères**, 12 sur quatre), **0 orphelin**. ⚠ Le dépôt
n'est pas en plus mauvais état qu'hier : ces verdicts étaient déjà des devinettes, ils **portent
maintenant leur prix**, et chaque chaîne écrite en déplace vers le barreau certain. La dette ne
fait **pas** échouer la garde — rouge sur 61 % du corpus, elle se ferait désapprendre.

⚠ Trois défauts attrapés dès le premier parcours, dont ⭐ **une exemption morte** :
`src/outils/repos.tsv` était exempté d'un parcours qui ne retenait que `docs/` et `data/`, donc une
décision qui ne protégeait rien. Réparée par **accessibilité** (coût zéro : un seul fichier à
suffixe d'artefact sous `src/`), et gardée par un contrôle neuf.

⭐ **Reste de l'architecture, chiffré** : la couche partagée (`_leve` ×19, `_pixels` ×14, `lire`
×13, `charger` ×10 — le noyau de fait est `figure_commune` 77×, `zarr_depth` 22×) ; et les
**paliers de build**, qui coûtent **5 arêtes** puisque le graphe est déjà à sens unique à **96 %**.

---

## REPRISE (historique) — 2026-08-28, fin d'après-midi

**Trente-six commits depuis la nuit du 27.** L'arbre est propre, la suite est verte. Ce bloc
remplace le précédent comme état courant ; tout ce qui suit est l'historique.

### Les trois résultats du jour

**1. ⭐⭐⭐ La première vérité terrain de ce dépôt** →
[`63`](docs/63_la_premiere_verite_terrain.md). Les fragments publient `inklabels.png` aligné
sur leurs couches de surface — le jeu du concours de détection d'encre. Tous les contrôles
positifs d'ici étaient jusque-là des **rendus publiés**, pas des vérités.

| fragment | encre fenêtre | tout le segment | lignes | **tuiles annotées** |
|---|---:|---:|---:|---:|
| `Frag1` | 31,8 % | 0,746 | 0,701 | 0,677 |
| `Frag2` | 20,6 % | 0,600 | 0,594 | 0,581 |
| `Frag3` | 1,55 % | 0,575 | 0,523 | **0,704** |
| | *étendue* | 0,171 | 0,178 | **0,122** |

⚠⚠⚠ **La réplication ne confirme pas, et le DOMAINE décide qui est l'exception** : `Frag1`
se détache sur « tout le segment », `Frag2` sur les tuiles. Notre chaîne rend **entre 0,52 et
0,75 selon le fragment ET le domaine**, et **aucun domaine ne les fait s'accorder**. La
dispersion est plus grande que tout écart qu'on chercherait entre deux réglages. Le contrôle
par mélange rend `0,500` partout, donc le signal est réel — le désaccord porte sur *combien*.

⚠ La fenêtre est choisie sur le **masque seul**, jamais sur l'encre, et la part d'encre est
rapportée. ⚠ On ne peut pas vérifier d'ici si les fragments étaient dans l'entraînement.

**2. ⭐⭐⭐ La résolution éliminée une seconde fois, contre de vrais labels.** `Frag1` est à
3,24 µm, le modèle entraîné à 7,91 — 144 % d'écart. Ramener le fragment au pas
d'entraînement **dégrade** l'AUC : `0,746` → `0,693` (×2, 6,48 µm) → `0,686` (×3, 9,72 µm),
de façon monotone. Le document 58 l'avait éliminée par émulation sur Scroll 1 ; ici c'est un
autre objet, contre des étiquettes, et les deux convergent.

**3. ⭐⭐ Le témoin négatif refait, et sa conclusion a changé de signe** →
[`46`](docs/46_le_temoin_negatif.md). ρ passe de **+0,9979 à −0,0100** (les deux cartes sont
étrangères, donc le modèle répond) et σ du positif de **2,4 % à 76,4 %** du modèle qui marche
— mais **σ du négatif vaut 0,7111 contre 0,5894**, donc il répond **plus fort** sur une
surface dont `38` prouve géométriquement qu'aucune feuille n'est à portée. **La thèse forte
est établie**, et elle est plus dure que celle publiée : un modèle bloqué se repère, un modèle
qui hallucine une structure *différente et convaincante* sur chaque entrée ne se repère par
aucune inspection de sa sortie. ⭐ Deux documents (`29`, `48`) concluaient « l'aval est
aveugle, aucune réparation ne peut y montrer de gain » : **c'est faux, le lot rouvre**.

### ⚠⚠ Ce qui est ouvert, et pourquoi

| | état |
|---|---|
| ~~**expliquer la dispersion** 0,52–0,75 entre fragments~~ | ✅ **fait le 2026-08-28** → [`64`](docs/64_la_dispersion_netait_pas_un_effet.md), et **il n'y avait pas de cause** : la dispersion tuile à tuile **dans** un fragment vaut 0,2243 contre 0,0391 **entre** fragments, soit **5,7×**, l'ICC vaut **0,030**, et il aurait fallu **27 tuiles par fragment** là où on en avait 10, 11 et 2. ⚠ Conséquence à tenir : **les trois AUC ne se comparent pas entre elles** |
| le **juge** de [`09`](docs/09_protocole_jugement_modele.md) | ⭐ **DÉBLOQUÉ le 2026-08-29, et il ne l'a jamais vraiment été.** `src/encre/judge_api.py` existe et a été **calibré** le 2026-08-17 (`gemini-3.5-flash`, **15/16, zéro fabrication**, 4/4 sur la condition décisive `vierge \| vierge`). ⚠⚠ Il ne lisait que `os.environ` alors que le dépôt porte un **`.env` rempli** : il répondait « aucune clé », et j'en avais déduit qu'il fallait « un papyrologue ». **La capacité existait, la clé existait, il manquait la ligne qui les joint.** Reste à décider le protocole du prochain tirage — `09` §2 rappelle que **l'ordre est irréversible** |
| ~~contrôle **typographique** du témoin négatif~~ | ⭐⭐⭐ **FAIT le 2026-08-28** → [`46`](docs/46_le_temoin_negatif.md) §3. Le contrôle dur **passe** : `PHerc1447` **8/12** périodiques contre **1/7** pour les deux témoins sans feuille, `[8, 4, 1, 6]`, **p = 0,0399**. ⚠⚠ **Une seule fenêtre suffirait à le renverser** (0,1299 / 0,0799) — la fragilité se lit avec le p. Un troisième témoin le consoliderait : `GRAINE="" ./src/outils/leur_graine.sh <dest>` |
| ~~« il ne reste que **ce rouleau-ci** » (`M1ter`, `58`, `59`)~~ | ⚠ **NON TESTABLE avec le corpus publié, 2026-08-28** : `ou_la_verite_existe.py` compte **zéro rouleau mesurable** sur cinq — quatre sans aucune étiquette d'encre, `Scroll1` avec des étiquettes qui sont son jeu d'**entraînement**. ⭐ La condition qui rouvrirait : des étiquettes publiées sur un rouleau que le modèle n'a pas vu, et une commande le re-vérifie. ⚠⚠ **La portée de ce « 0 sur 5 » est celle des CINQ rouleaux interrogés, pas celle du corpus** : [`68`](docs/68_lire_le_papier_en_entier.md) §4 montre que `PHerc0139`, absent de ces cinq, porte le régime du prix ET le régime de production recalés, sur un rouleau dont le titre est **transcrit et publié**. À relancer sur le corpus ESRF |
| ~~**énergie** isolée contre étiquettes~~ | ⭐⭐⭐ **RÉOUVERT le 2026-09-02** → [`68`](docs/68_lire_le_papier_en_entier.md) §4. L'ancienne réponse — « impossible : `Frag1`–`Frag3` ont les labels sans recalage, `Frag5`/`Frag6` le recalage sans labels » — était vraie de l'**ancien layout** `fragments/` et **fausse du corpus ESRF**. `data/metadata.min.json` publie un champ `volume_transforms` que rien ne lisait : **6 objets** relient le régime du prix (1,2 m) au régime de production (≤ 0,4 m), dont **les 3 fragments de supervision du papier** (`9B`, `343P`, `500P2`), qui portent une vérité terrain infrarouge. `la_case_vide.py` compte **103 cases** publiées en couches rendues, sans carte d'encre, **avec un témoin positif sur le même segment** |
| la **soumission** | hors périmètre, sur demande de l'auteur |

### ⭐⭐⭐ Ce que le 28 août au soir a ajouté, et qui commande la suite

**Il n'y avait pas de dispersion à expliquer** → [`64`](docs/64_la_dispersion_netait_pas_un_effet.md).
L'AUC d'une tuile de 256 px varie d'un écart-type de **0,2243** d'une tuile à l'autre du
**même** fragment ; entre fragments, l'écart-type vaut **0,0391**. Savoir de quel fragment
vient une tuile explique **3 %** de la dispersion, et 2 paires sur 3 ont des intervalles qui
se recouvrent.

**La conséquence est une règle, pas une note** : toute comparaison future — deux réglages,
deux énergies, une nappe gauchie contre une nappe brute — doit se dimensionner **avant** et
se faire **appariée**, sur les mêmes tuiles.

| écart d'AUC à établir | tuiles par condition |
|---|---:|
| 0,10 | **79** |
| 0,05 | **316** |

⚠ Ce sont des **minorants** : la formule suppose des tuiles indépendantes, et deux tuiles
voisines ne le sont pas. La précondition est écrite là où le patron d'expérience vit
([`58`](docs/58_resolution_ou_rouleau.md) §8) et là où l'expérience qui commande tout est
décrite ([`31`](docs/31_roadmap.md) §9), pas seulement ici.

⚠⚠ **Et un fait que les trois AUC publiées ne laissent pas voir** : **5 tuiles sur 23** sont
**sous** le hasard, la plus basse à **0,158**. Sur celles-là le modèle range l'encre *sous* le
papyrus vierge — du signal réel, à l'envers, qu'une moyenne noie.

### ⭐⭐ Le 28 au soir, deuxième moitié : deux blocages levés, un troisième en cours

**Le second témoin négatif existe** → [`46`](docs/46_le_temoin_negatif.md) §3. Ce n'était pas
« une tâche à part » : toute la chaîne est dans `src/outils/leur_graine.sh`, l'outillage `vc_`
est installé, et la seule chose figée était **la graine**. `GRAINE=""` bascule le traceur en
`random_seed` — le mode de l'équipe d'origine — donc le témoin est indépendant **par
construction** plutôt que par mon jugement. Mesuré : graine `[2078, 5227, 5113]`, **13,89 cm²**
(contre 3,95 chez eux), 0 auto-intersection, **α = +0,99**, marge 0,29.

⭐⭐⭐ **Le contrôle typographique groupé est FAIT, et il passe.** C'est l'expérience qui avait
manqué d'une fenêtre. Résultat : `PHerc1447` rend **8/12** fenêtres périodiques, les deux
témoins sans feuille **1/7**, Fisher `[8, 4, 1, 6]`, **p = 0,0399**. ⚠⚠ **Une seule fenêtre
suffirait à le renverser** — la fragilité est publiée avec le p, parce que sept fenêtres de
témoin c'est peu et qu'un 0,04 se lirait sinon comme le 0,0007 du contrôle par mélange.

**Le transport de calibration (résidu M7) est répondu, négativement** →
[`45`](docs/45_consistent_with_quantifie.md) §7. L'étape que le résidu sautait était de
**valider** le prédicteur là où la vérité existe encore. Fait sur les 23 tuiles étiquetées :
une grandeur sur cinq passe le seuil brut, **aucune** ne survit à Holm, et cinq tests le
donnent au hasard une fois sur quatre. ⭐ L'épaisseur de trait, meilleure des 190 cartes
publiées, est ici la **pire** — classer des cartes entières et prédire l'AUC d'une tuile ne
sont pas la même question.

**σ ne prédit pas la qualité mesurée, et 9,72 µm n'est pas établi lisible** →
[`65`](docs/65_ce_que_sigma_ne_dit_pas.md). Deux inférences que le dépôt faisait depuis des
semaines, testées pour la première fois sur les 23 tuiles étiquetées. σ arrive **quatrième
sur six** grandeurs (p de Holm 0,739) ; à 9,72 µm l'intervalle [0,455 ; 0,745] contient 0,5,
et un balayage de maille montre que **cette carte ne peut pas trancher** — il faut plus de
surface rendue. ⭐ Au natif (3,24 µm), la lisibilité **est** établie, et c'est une première
contre de vraies étiquettes.

**Aucun rouleau n'est mesurable** → [`59`](docs/59_la_campagne_plutot_que_le_rouleau.md) et
`ou_la_verite_existe.py` : **0 sur 5**. Quatre ne publient aucune étiquette d'encre, `Scroll1`
en a mais c'est son jeu d'entraînement. Seuls **4 fragments** le sont. Chercher un discriminant
entre rouleaux suppose de mesurer la lecture des deux côtés, et elle ne l'est d'aucun côté
rouleau. ⚠ Ce n'est pas « le modèle ne lit pas sur un rouleau » — c'est qu'on ne peut pas le
mesurer.

**Tâches ouvertes : 14 → 8**, dont **5 sont la soumission** (hors périmètre) et **3 sont le
contrôle typographique en cours de rendu**.

### ⚠⚠⚠ Les DEUX audits du 2026-08-29 — à lire avant tout le reste

**Antériorité des RÉSULTATS** → [`66`](docs/66_audit_danteriorite.md) : 14 résultats,
**6 déjà publiés, 8 à moitié, 0 nouveau**.
**Antériorité des OUTILS** → [`67`](docs/67_audit_des_outils.md) : 98 instruments,
**22 existaient déjà, 50 partiellement, 27 sans équivalent**, et **23 verdicts de temps
réellement perdu** — de l'ordre de la semaine.

⚠⚠ **Le mode de défaillance est le même dans les deux, et il est nommable** : un échec de
**vocabulaire**. Aucun équivalent ne porte notre nom — « écart entre spires » s'appelle
*winding pitch*, « planéité » *linearity*, « champ de correction » *subvoxel re-centering*.
Un grep sur nos concepts français ne rend rien, un grep sur leurs noms anglais rend tout. Et
les dépôts étaient **déjà clonés sur ce disque** avant que la plupart de nos scripts soient
écrits : le coût n'était pas de les chercher, il était de **les ouvrir**.

⭐ **Ce qui n'a aucun équivalent, et qui situe l'apport** : la **statistique** (zéro
`binomtest`, zéro permutation, zéro analyse de puissance dans les 35 dépôts), le **juge
automatique en aveugle** (aucun appel à une API de modèle, et le protocole publié n'a pas de
condition de contrôle), le **test de convergence**, l'**étage polaire**, et douze outils
d'hygiène de dépôt.

⚠⚠⚠ **Trois choses plus graves que la comptabilité, actionnables tout de suite :**
1. `winding-ruler/atlas/build_atlas_v2.py` **contredit** `pyramid.py` — le niveau 2 fusionne
   les feuilles voisines (pas surestimé de **10,3 %**, 36/36) — et `espacement_spires.py`
   tourne **encore au niveau 2**, donc le biais se propage dans `ecart_de_maillages`.
2. `sensibilite_centre.py` existe à cause d'une **prémisse fausse** : l'ombilic **est** publié,
   sur `dl.ash2txt.org` — on avait vérifié sur le bucket S3 seulement.
3. La **posture méthodologique n'est pas distinctive** : trois dépôts concurrents écrivent nos
   propres règles dans nos propres mots (« *a number TRUE OF A SUBSET, narrated as true of the
   whole* », « *comparing a tool to itself is a check that cannot fail* »).

### ⚠⚠ Le détail de l'audit d'antériorité des résultats

**14 résultats, 6 déjà publiés, 8 à moitié, 0 nouveau** → [`66`](docs/66_audit_danteriorite.md).
Six sont réfutés par des fichiers **de notre propre disque** : le miroir du site et le monorepo
`villa`. ⚠ Ce n'est pas un problème de veille, c'est un problème de **grounding avant
écriture** — la règle « chercher le concept, pas le nom » n'avait jamais été appliquée à la
bibliographie.

**Deux choses pires qu'une antériorité, à traiter en premier :**

1. ⚠⚠⚠ **La piste du fold de validation peut être FAUSSE.** Le checkpoint que trois projets
   nomment est `timesformer_wild15_**20230702185753**_…`, donc fold = `20230702185753`, pas
   `20231210121321`. Et **on ne peut pas trancher depuis ici** : notre copie HuggingFace a
   perdu la provenance (`model.safetensors` ne porte que `{'format': 'pt'}`, vérifié).
   ⭐ Le test qui tranche ne demande aucune métadonnée : **mesurer sur les deux segments**,
   celui où le modèle score le moins bien est celui qu'il n'a pas vu.
2. ⚠⚠⚠ **L'axe énergie est contredit**, pas seulement précédé : 116 keV est **dans** l'optimum
   publié pour 8 µm, et notre 114,8 % tenait au choix d'un témoin de 2023 que le pipeline
   n'utilise plus.

**À faire, dans cet ordre** : lire le PDF *OverthINKingSegmenter* ; décoder le checkpoint par la
mesure ; cloner `vesuvius-repro` (TAUIL) ; vérifier Obuchowski 1997 sur les ROC **groupées** ;
et **citer `vesuvius-automesh`, `windcheck`, `winding-sync`, `tifxyz-doctor`, `winding-ruler`
comme antériorité dans nos documents** — ils sont sur le disque, une revue les trouvera à notre
place.

### ⭐⭐ La convention du sablier a changé — 2026-08-29

**Un ⏳ veut dire OUVERT, point.** Le registre acceptait un état `faite` : un sablier posé sur
une ligne dont le travail est fini, donc un caractère qui **ment** à qui lit le document sans
ouvrir le registre. Il y en avait **dix-neuf**.

- les dix-neuf sont devenus `✅`, et les six lignes dont la prose affirmait encore quelque
  chose de faux (« la seule piste restante », « M8 reste ouvert », « balayage en cours ») sont
  **barrées avec le pointeur vers leur réponse** ;
- `faite` et `perimee` **ne sont plus des états valides** : classer un sablier ainsi est une
  **contradiction** que `taches_ouvertes.py` refuse, avec le message « remplacer ⏳ par ✅ » ;
- **31 sabliers dans 16 documents → 12 dans 6**, registre **32 → 13 lignes**.

⚠ Conséquence pratique : « reste-t-il du travail ? » se lit désormais **sur le document**, sans
croiser un registre. Les trois états qui restent sont `ouverte`, `recit` (un titre de section
daté) et `legende` (le caractère expliqué dans la légende de `55`).

### ⚠ Les pièges payés aujourd'hui, à ne pas repayer

- **219 agents lancés d'un coup** ont épuisé la limite mensuelle de l'org : un vérificateur
  par candidat, 208 pour 11 lecteurs, sans plafond. Échantillonner aurait donné le même
  signal. Les 489 items extraits ont été récupérés du **journal** de la campagne.
- **`campagnes_de_scan.py` ne voit qu'UN des deux layouts** du dépôt public. Son `n_volumes`
  est un **minorant**, et cet angle mort a fait argumenter `59` depuis une liste qui ne
  contient pas le volume où le modèle marche — puis déclarer impossible un test que l'autre
  layout rend possible.
- **`volumes_standardized/` ne recale rien** : même forme, `uint8`. C'est une normalisation
  d'intensité, pas une transformation spatiale.
- **`round(49.5) == 50`** en Python : arrondi au pair.
- Le code de sortie d'une **chaîne** est celui de sa dernière commande — quatre fois.
- ⚠⚠ **`argsort` range les `NaN` EN TÊTE.** Une carte d'encre porte des pixels non couverts,
  et les oublier les classe comme les **mieux notés** du fragment. Payé le 28 au soir : ma
  première mesure rendait 0,731 là où le dépôt publie 0,746 — deux réponses à « quelle est
  l'AUC de ce fragment », attrapées parce que le nombre existait déjà. Passer par
  `np.isfinite`, comme `evaluate_segment` le fait.
- ⚠⚠ **Un chiffre dérivé se recalcule, il ne se transpose pas.** J'ai publié « 63 tuiles »
  dans `31` §9 : c'était juste pour un écart-type de 0,2 et faux pour le nôtre, qui vaut
  0,2243 — la vraie réponse est **79**. Corrigé en calculant plutôt qu'en raisonnant, et les
  deux comptes de référence sont désormais **dans le record**, donc gardés.
- ⚠⚠ **Un témoin à UN SEUL tirage n'est pas un témoin**, c'est un tirage de la loi nulle. Mon
  contrôle par mélange du transport a rendu −0,40 et −0,36 — autant que les vraies
  corrélations — et les deux lectures possibles (« le mélange corrèle donc rien ne vaut » /
  « hasard malheureux ») étaient également infondées. Ce qui répond est la **distribution** :
  une valeur p par permutation, puis **Holm**, parce que cinq tests mettent au hasard une
  grandeur sous 0,05 une fois sur quatre.
- ⚠ **Un `{:.1f}` sur des graduations décalées d'un demi-dixième** affiche deux fois le même
  libellé. La première figure de `64` portait « 0.8 » deux fois avec « 0.4 » manquant, et
  quatre tuiles **hors du cadre**. Une figure se **regarde** avant d'être publiée.

### Trente-six marqueurs périmés fermés

Le motif se répète : la réponse est presque toujours dans le **même document**, parfois quatre
lignes plus bas, et personne n'est revenu barrer la question. Un triage sur les 64 documents
a extrait **489 items** ; ⚠ sa vérification adversariale a été coupée, donc les classements
restent **non vérifiés** et je les reprends un par un.

---

## ⚠⚠⚠⚠ UNE CONSTANTE RENDAIT LE MODÈLE MUET — et elle a fondé un résultat négatif publié

[`60`](docs/60_la_constante_qui_rendait_le_modele_muet.md), 2026-08-27. **Le plus gros
résultat de la journée, et il annule une conclusion de ce dépôt.**

`src/xpu/infer_ink.py` normalisait par la constante `65535` — juste pour du **uint16**, et
fausse d'un facteur **257** pour du **uint8**. Or l'arbre contient **3 piles uint16** (les
stacks *publiés* de `data/layers/`) et **211 uint8** (tout ce que `vc_render_tifxyz` rend,
tout ce que `zarr_vers_couches.py` écrit). ⭐⭐⭐ **Le partage « le modèle répond / le modèle
est inerte » suivait EXACTEMENT ce partage-là.**

Un modèle à qui l'on donne du noir rend une constante, et une constante se lit comme « il n'y
a pas d'encre ici ». La panne ne ressemblait pas à une panne, elle ressemblait à un résultat.

| | avant | après | contre le témoin |
|---|---:|---:|---:|
| **`PHerc1447` — un rouleau du prix** | σ **0,0171** | σ **0,6558** | **1,2×** |
| `PHerc0172` — 53 keV, hors des treize | étendue 0,207 | σ **1,0217** | **0,8×** |
| Scroll 1 — le témoin | σ 0,7712 | σ 0,7712 (inchangé) | 1,0× |

⭐ Le correctif est vérifié dans les deux sens : sur uint8 il rend **exactement** ce que la
remise à l'échelle manuelle rend, et sur uint16 il ne bouge **rien** (`−1,778 / −1,559 /
+1,691` avant et après, au chiffre près).

**Ce que ça renverse** : `36` §5bis (M1ter, réponse négative) est **ANNULÉ** ; `46` (témoin
négatif) est **à refaire**, son contrôle positif était noir ; `54` (cinq rendus vides) est
**à relire**. ⭐ `58` **tient** — son échelle de dégradation tourne sur les piles uint16
publiées, donc hors du bug ; ce qui tombe est sa prémisse d'entrée, il n'y a plus de facteur
45 à expliquer.

⚠ **Répondre n'est pas lire.** σ dit que le modèle produit de la structure ; que ce soit des
lettres demande une fenêtre bien plus large — à 8,64 µm, 1024 px font 8,8 mm, quatre lettres
— et le juge calibré de `09`. **C'est la mesure suivante.**

⚠⚠ Et le premier jet de contrôles était **incapable d'attraper le bug** : il portait sur la
règle (« 255, 65535, rapport 257 ») sans traverser `load_layer_stack`, et il est resté vert
quand j'ai remis la constante pour le sonder. Le contrôle qui manquait écrit **deux vraies
piles**, une par type, et exige que le modèle reçoive les mêmes valeurs. Plus deux refus :
une pile dont le maximum normalisé est sous 1/64 de la pleine échelle, et une pile dont les
couches changent de type.

⭐ Nouvel outil : `src/depot/echelle_des_piles.py` — le coup d'œil qui a trouvé le bug, devenu
une batterie. Nouvelle figure : `src/figures/figure_echelle.py`.

---

## ⚠⚠⚠ LA CAMPAGNE DE SCAN : UNE PISTE OUVERTE ET REFERMÉE LE MÊME JOUR

[`59`](docs/59_la_campagne_plutot_que_le_rouleau.md), 2026-08-27. `58` avait éliminé la
résolution et laissé « ce rouleau-ci ». J'ai cru le remplacer par la **campagne de scan** —
et la piste s'est effondrée en deux temps, chacun trouvé par une question de l'auteur.

**Premier effondrement.** La mesure portait sur `data/encre/`, c'est-à-dire sur ce que
`fetch_cartes_encre.sh` a **téléchargé sur demande**. Un fait sur nous, pas sur le corpus.
Corrigé en interrogeant le dépôt : publie-t-il une détection d'encre pour ce rouleau ?

**Second effondrement, et c'est celui qui compte.** Il y a **TROIS états**, pas deux :

| état | rouleaux | avec un scan fin |
|---|---:|---:|
| **aucun segment publié** — personne n'a tracé | **31** | 6 (19 %) |
| tracé, sans encre publiée | 7 | 5 (71 %) |
| encre publiée | 7 | 6 (86 %) |

⭐⭐⭐ Trente-et-un des trente-huit du groupe « pas d'encre » **n'ont jamais été tracés**.
Restreint aux rouleaux qu'on a **tentés** — `[6, 1, 5, 2]`, 86 % contre 71 % — le p passe de
**0,0081 à 0,5000**. Aucune séparation. Le scan fin suit **l'attention** portée à un rouleau,
pas sa lisibilité.

⚠⚠ La mise en garde qui aurait dû tuer le chiffre était **écrite à côté de lui** dès la
première version (« l'ordre causal pourrait être inverse ») : la laisser en note au lieu de
la retirer du chiffre, c'est publier le chiffre quand même.

**Ce qui survit** : le corpus n'est pas *difficile*, il est largement **non tenté** (31 sur
45) ; **aucun des treize rouleaux du prix ne publie de détection d'encre**, dix n'ont aucun
segment du tout, trois ont été tracés sans rien rendre ; et le cadre à trois états, dont le
même corpus prouve qu'un cadre à deux est un piège.

⚠ **« Ce rouleau-ci » reste donc la seule cause en lice.** Il n'y a pas encore de discriminant.

### Les deux décisions que l'auteur a débloquées, faites

**M4 — fermée sur sa branche réfutée.** `12`:259 en proposait deux dès l'origine, « un volume
plus épais **ou** en corrigeant la trace ». La première est réfutée deux fois : `20` §9
(élargir ajoute des feuilles) et `58` §5 (doubler l'épaisseur coûte **40,8 %** de la réponse
du modèle d'encre). Plus profond n'est pas inutile, c'est **nuisible au seul consommateur en
aval**. La seconde branche, corriger la trace, est le fil vivant.

**`16` — les 14 cartes régénérées, et le tableau §3 a bougé.** Le balayage couvre désormais
**toute** l'étendue en x/y (108 sondes) au lieu de sa moitié centrale (64), et chaque
artefact porte `sondes` et `chunks_avec_matiere`. Cinq rouleaux se desserrent, trois se
resserrent, le témoin ne bouge pas d'un micromètre en médiane (173 µm). **Dix des treize**
sont désormais aussi lâches ou plus que le rouleau déjà lu, contre neuf. `PHerc0257` passe de
21 % à **0 %** de zones sous 150 µm et rejoint `PHerc0268` et `PHerc0800` en tête des plus
lâches. L'ancien tableau est conservé dans un repli, parce que l'écart entre les deux **est**
le résultat de la correction.

⚠⚠ **Et le prix de la correction est une PERTE de puissance** : l'échantillonnage complet
touche beaucoup de vide, donc chaque rouleau rend **moins** de fenêtres exploitables — 16 à
38 contre 27 à 62. Plus de sondes, moins de mesures. La limite de `33` sur le classement
n'est pas levée, elle est resserrée.

⚠ Et `carte_difficulte.sh` lisait sa liste de clés dans `/tmp/pred_prix.txt`, un fichier que
rien ne produit et qui n'existe plus : la commande « Reproduire » de `16` était **morte**.
Elle dérive désormais clés et voxels par `apparier_volumes.py --pour-campagne`, et **sort non
nul** si elle produit moins d'artefacts que la cohorte plus son témoin — le premier run en a
sauté un, `PHerc1203`, en silence, avec un « termine » à la fin.

---

## ⭐⭐⭐⭐⭐ M1ter — LA RÉSOLUTION EST ÉLIMINÉE, et le chiffre qui portait la question était faux

[`58`](docs/58_resolution_ou_rouleau.md), 2026-08-27. Trois causes restaient à l'inertie du
modèle d'encre sur `PHerc1447` ; [`46`](docs/46_le_temoin_negatif.md) §3 en avait fermé une.
Celle-ci tombe **en vérifiant un nombre au lieu de le citer**.

⚠⚠ `36` §5bis opposait « Scroll 1 `20230909121925`, **2,4 µm** » à « `PHerc1447`, 8,64 µm ».
La première valeur ne vient de nulle part : le segment déclare son volume, le volume déclare
`voxelsize: 7.91`. Et le dépôt le savait déjà ailleurs — `12` écrit « 6 voxels (47 µm) »
pour cette même pile, soit 7,83 µm par couche. **Deux documents du même dépôt portaient deux
pas différents pour la même pile**, et personne ne les avait mis côte à côte.

| | Scroll 1, 7,91 µm | `PHerc1447`, 8,64 µm | rapport |
|---|---:|---:|---:|
| ce qu'une tuile de 64 px couvre | 506,2 µm | 553,0 µm | **1,092** |
| ce que 26 couches couvrent | 205,7 µm | 224,6 µm | **1,092** |
| **σ de la sortie du modèle** | **0,7712** | **0,0171** | **45,2** |

⭐⭐⭐ **Le modèle atteint AUC 0,925 dans les conditions de `PHerc1447`.** Il faudrait qu'un
écart de 9 % produise un facteur 45.

Et le compte est chiffré, pas invoqué. En dégradant Scroll 1 par moyennage de bloc, un
**doublement** en plan coûte **5,6 %** ; sur les 65 couches de Scroll 4, un doublement en
**profondeur** coûte **40,8 %**, soit huit fois plus ; et les deux **s'aggravent** au lieu de
s'additionner — le croisé mesure **0,494** contre **0,590** que prédit l'indépendance, donc
un doublement en plan coûte 0,32 % sur une fenêtre juste et **16,6 %** sur une fenêtre déjà
doublée, cinquante fois plus. En créditant la résolution de tout ça — dix fois l'écart
qu'elle a, sur les deux axes, pénalité d'interaction comprise — elle rend **0,468**, soit un
facteur **2,1** là où il en faut **45**.

⚠ **Il ne reste que ce rouleau-ci**, seul — le sablier est porté par `58` §8 et inscrit au
registre, pas ici. Ce que le mot recouvre — conservation, chimie de
l'encre, énergie du faisceau, surface tracée — reste à découper, et `58` §8 donne le patron :
rendre l'objet qui marche semblable à celui qui ne marche pas, une propriété à la fois.

⭐ Le remède au piège est dans le code : `src/encre/resolution_ou_rouleau.py` n'a **plus de
constante de pas**, il exige `--voxel-um` et l'inscrit dans chaque rapport. C'est le même
remède que `57` §1.1 après « 18 voxels » qui pouvaient valoir 43 ou 142 µm.

### ⚠⚠ Le détour : l'outil d'inférence ne tournait plus du tout

`src/xpu/infer_ink.py` portait ses poids, validait ses arguments, puis mourait sur un
`ModuleNotFoundError` **nu** — `torch`, `transformers` et `timesformer_pytorch` n'étaient
dans **aucun** groupe de dépendances. Il refuse désormais **avant** de lire une couche, nomme
chaque module absent et la commande qui répare, et sort en **3**. Trois faits ne sont
apparus qu'en exécutant : `timesformer_pytorch` est demandé par le code du modèle via
`trust_remote_code` (donc invisible dans nos imports) ; `transformers` doit être **borné sous
5** (la 5.16 exige `all_tied_weights_keys`, absent de ce modèle écrit pour 4.46.3) ; et
l'index de roues par défaut tire **2,7 Gio de CUDA** inutile ici (4,9 Gio → **1,2 Gio** avec
l'index CPU).

⚠⚠ Et `uv sync` a **désinstallé 19 paquets** — `zarr`, `fsspec`, `s3fs` — que quatre outils
de `src/excision/` importent *dans leurs fonctions* et qu'aucun fichier ne déclarait. Ils
étaient là parce que quelqu'un les y avait posés à la main. **Un environnement reproductible
qui ne survit pas à sa propre commande de synchronisation ne l'est pas**, et la panne ne se
voit que le jour où on relit un volume. Les deux groupes sont déclarés, optionnels.

```bash
uv sync --extra encre --extra volume
```

---

---

## ⚠⚠⚠ UN RUN OUBLIÉ A ÉCRASÉ UN RÉSULTAT FRAIS — et `temoins.sh` a maintenant un verrou

`temoins.sh` **écrit** `docs/mesures/temoins.json` à la fin. Deux runs concurrents courent donc
dessus, et c'est **le plus LENT qui gagne** : un run lancé *avant* une correction peut écraser
le résultat vert d'un run lancé *après*. Vu en vrai le 2026-08-26 — un run oublié en
arrière-plan a remis `"echecs": 2` par-dessus un `"echecs": 0` frais, **plusieurs minutes
après le commit**.

⭐ C'est le cousin du piège déjà consigné ici (« un log périmé lu comme un résultat »), en pire :
là c'était une *lecture* périmée, ici c'est une **écriture** périmée. Aucune vigilance ne
protège de ça — seul un verrou le peut. `temoins.sh` refuse désormais de démarrer si un autre
run vit (verrou par PID, vérifié avec `kill -0`, donc un verrou orphelin ne bloque pas le
dépôt ; `--sans-verrou` pour le cas où on sait ce qu'on fait). Sondé : le second run refuse et
le dit, le verrou se libère à la sortie.

---

## ⭐⭐⭐⭐ `data/` RANGÉ — 43,4 Gio effacés, et la règle qui l'autorise

189 Gio → **146 Gio**, 81 dossiers → **61**. Rien n'a été effacé au jugé : `a_supprimer()`
(`src/depot/donnees_sans_appelant.py`) applique deux classes, et **aucune** ne touche un
dossier que quelque chose nomme.

| classe | dossiers | poids | la raison |
|---|---:|---:|---|
| **muette** | 7 | 1,94 Gio | rien ne la nomme **et** elle ne dit pas d'où elle vient |
| **dépensée** | 16 | 41,4 Gio | rien ne la nomme, elle dit d'où elle vient, **et son résultat est publié** |
| gardée | 6 | 7,2 Gio | tracée mais rien de publié — l'effacer emporterait une mesure |

⭐ **La première classe est la règle de l'auteur, écrite en code** : *« si on ne sait plus du
tout d'où ça vient ni ce que c'est, on peut le supprimer, parce que de toute façon on ne
sait pas »*. Un dossier de mesure porte sa propre trace — un `meta.json` qui nomme son parent
(`decoupe_de`, `projete_de`), un `seed.json` qui donne sa graine, un `.log` qui garde la
commande. Aucun des trois ⇒ ni rejouable, ni vérifiable, ni explicable.

⭐⭐ **La seconde est plus intéressante, et c'est elle qui pèse** : une campagne dont le
chiffre vit dans `docs/mesures/` et que `verifier_chiffres.py` recalcule **a rendu ce qu'elle
avait à rendre**. Chaque suppression a été vérifiée en nommant le fichier de résultat qui la
justifie — `ext_budget` → `extension_ext_budget_gen200.json`, `spires_pic025` →
`spire_pic025_spire00.json`, et ainsi de suite pour les seize.

⚠ Et `data/meshes` est **gardé** alors que rien ne le nomme : `docs/journaux/ppm_convert.log`
dit ce que c'est (`20230909121925.tifxyz`, le maillage du segment publié) et par quoi il se
refait (`src/outils/ppm_to_tifxyz.py`). Ce n'est pas « on ne sait pas », c'est « on sait, et
personne ne s'en sert en ce moment ».

### ⭐ « Fusionner ce qu'on peut » — mesuré, et la réponse n'est pas une suppression

`contenu_en_double.py` sur les 146 Gio : **71 970 fichiers, 3 782 groupes identiques,
15,56 Gio récupérables**. Le partage est ce qui décide de la suite :

| motif | poids | ce que c'est |
|---|---:|---|
| `fenetres_imbriquees` | **8,51 Gio** | `rendu_31/20.tif` **est** `rendu_81/45.tif` — une fenêtre étroite est déjà dans la large |
| `autre` | 7,05 Gio | des clones tiers (`data/repos/`), un PDF stocké trois fois, des rendus documentés |

⭐⭐ **Et la fusion des 8,51 Gio n'est pas un `rm`, c'est le raccourci de rendu du chantier A**
(`sous_fenetre.py`, `DERIVER=1`) : une fenêtre étroite se **dérive** de la large, octet pour
octet. ⚠ Mais il est **câblé et sondé, jamais exercé sur un vrai rendu** — effacer les
fenêtres étroites en pariant dessus serait faire confiance à une machinerie qu'aucune mesure
n'a encore fait tourner. Le gain est nommé, chiffré, et attend son premier vrai rendu.

⚠ Les 7,05 Gio restants ne sont pas non plus à effacer : `data/repos/` se reclone
(`src/outils/clone_repos.sh`), et les rendus qui s'y trouvent — `m7_c0/rendu_161`,
`leur_graine/rendu_161` — sont l'**objet même** de `54` et `51`. Effacer une preuve pour
gagner du disque, c'est effacer la mesure.

### ⚠ Ce que je n'ai PAS fait, et pourquoi

**Grouper `data/` en sous-dossiers** (`data/chaine/`, `data/paris4/`, `data/spires/`). Mesuré :
69 citations à réécrire pour 14 dossiers — mais surtout, **le préfixe EST déjà le groupe** et
il trie ensemble, et deux noms de la famille sont des frères par conception : `data/spires` et
`data/spires_dedans` existent tous les deux, `data/second_axe` et `data/second_axe_41` aussi.
Les imbriquer forcerait à renommer l'aîné. Le rangement se paierait en citations de blocs
« Reproduire » qui produisent des chiffres publiés, pour un gain d'affichage.

---

## ⭐⭐⭐⭐⭐ TROIS DOSSIERS — `src/`, `docs/`, `data/`, et rien d'autre

`tracecheck/`, `experiments/`, `inference_xpu/`, `apprendre/`, `article/`, `artefacts/`,
`repos/`, `site/` et `soumission/` sont **repliés**. La racine ne porte plus que trois
dossiers et les fichiers qui doivent y être (`README`, `LICENSE`, `pyproject.toml`, `lplv`).

| ce qui était à la racine | où c'est | pourquoi là |
|---|---|---|
| `tracecheck/` | `src/tracecheck/` | c'est du code de ce dépôt |
| `experiments/src/excision/` | `src/excision/` | idem, et son `pyproject` est replié dans celui de la racine |
| `inference_xpu/` | `src/xpu/` | son `pyproject` **reste avec son code** : torch/XPU épingle Python 3.13 et un index maison |
| `apprendre/` | `src/apprendre/` | à plat, comme toutes les familles |
| `article/` | `docs/article/` | c'est un document |
| `artefacts/` | `data/artefacts/` | ce sont des données |
| `repos/`, `site/`, `soumission/` | `data/` | tout ça se retélécharge |

⭐ **Le signe que la disposition est juste, c'est que trois listes se sont RÉDUITES.**
`lplv.FAMILLES` passe de cinq motifs à **deux** (`src/*/*.py`, `src/*/*.sh`),
`artefacts_orphelins.SOURCES` de quatre entrées à **une**, et `temoins.sh` perd ses **six**
changements de projet — il n'y a plus qu'un environnement à part, celui de `src/xpu`. Chacune
de ces listes ENREGISTRAIT la dispersion.

### ⚠⚠ Ce que le repli a cassé, et qu'il a fallu réparer

- **La liste blanche de la release se serait élargie toute seule.** Elle gardait `src` en
  bloc et laissait dehors `experiments/` et `inference_xpu/`, qui étaient des dossiers de
  premier niveau. Devenus des familles de `src/`, ils y seraient entrés — **6,3 Gio
  d'environnement torch dans la release, sans qu'une ligne ne change**. Les familles sont
  désormais listées **une par une**, et un contrôle échoue si `src` réapparaît en bloc.
- ⚠⚠⚠ **Un contrôle est passé de 90 secondes à plus de 47 MINUTES** — et il n'a jamais rendu
  la main. `artefacts_orphelins` faisait `rglob("*")` sur `src/`, qui contient maintenant
  `src/xpu/.venv` : 8 885 fichiers de `site-packages` lus, puis cherchés dans un corpus de
  centaines de mégaoctets. Élagué à la traversée. **Troisième fois que ce dépôt paie un
  `rglob` non élagué**, et la règle est maintenant écrite dans les deux walkers concernés.
- **Huit verbes qu'on ne pouvait pas exécuter.** Replier `apprendre/` a fait entrer huit
  **scènes Manim** dans le glob des verbes — or une scène n'a pas de ligne de commande, donc
  `lplv <scène> --help` échouait. ⭐ La règle qui les écarte est **dérivée, pas une liste
  d'exceptions** : un programme a une garde `__main__` ou du travail au niveau du module.
  Mesurée sur l'arbre, elle écarte exactement neuf fichiers — les huit scènes **plus**
  `telecharger.py`, une bibliothèque qu'une liste de dossiers aurait ratée.
- **`deplacer.py` refusait son propre travail correct.** Ranger `article/` sous `docs/`
  produit un chemin neuf qui **contient** l'ancien, donc chaque citation déjà réécrite était
  recomptée comme pendante : **40 fausses pendantes**. ⚠ Et ma première correction — refuser
  un `/` précédé d'un mot — cassait `"$ROOT/analysis/src/x.py"`, une citation parfaitement
  légitime ; deux contrôles l'ont dit tout de suite. Le masquage se fait donc là où l'outil
  connaît les **deux** chemins, pas dans le motif qui n'en connaît qu'un.
- **Un manque de dépendance rendu visible.** `src/volume/region_locale.py` importe `zarr`, et
  la racine ne le déclarait pas : il ne marchait **que lancé depuis `experiments/`**,
  c'est-à-dire par accident de répertoire courant. ⚠ Et `zarr` 2.x exige `numcodecs < 0.16`
  (`cbuffer_sizes` a disparu en 0.16) — l'environnement qui marchait portait 0.15.1, la
  racine 0.16.5.

⚠ L'environnement de `experiments/` est **supprimé** (350 Mio) : ses dépendances sont dans le
`pyproject.toml` de la racine, donc `src/excision/` tourne dans l'environnement principal —
vérifié en important `radial`, `proximity`, `fusions` et `zarr` depuis lui. Les deux
environnements qui restent le sont parce qu'ils **ne peuvent pas** fusionner : `src/xpu/.venv`
(torch/XPU, Python 3.13, index maison) et `src/apprendre/.venv` (manim).

---

## ⭐⭐⭐⭐⭐ LA CHAÎNE **GLISSE** HORS DE LA FEUILLE CONNUE — elle n'y SAUTE pas

Et on le sait **sans encre et sans rendre un seul voxel**. Le raisonnement qui manquait tient
en une phrase : le point de départ est un morceau d'un segment **publié**, donc la bonne
feuille est connue sur **toute l'emprise de ce segment**, pas seulement sous le morceau. Il
suffit de demander, maillon par maillon, à quelle distance de cette surface la chaîne est.
`src/nappe/couverture_publiee.py`, quelques secondes.

| maillon | parcouru | encore SUR la surface | **écart signé** | même côté |
|---:|---:|---:|---:|---:|
| 1 | 96 µm | **100,0 %** | −0,1 vox | 57 % |
| 8 | 768 µm | 56,3 % | −5,1 | 63 % |
| 20 | 1 920 µm | 45,4 % | −11,7 | 72 % |
| **60** | **5 760 µm** | ⚠ **27,2 %** | ⚠ **−28,8 vox = −69 µm** | **73 %** |

⭐⭐⭐ **Lisse, monotone, et du même côté pour 73 % des points.** Ce n'est ni un gauchissement
(qui s'écarterait des deux côtés) ni un saut de spire (qui serait une marche brusque). C'est
une **dérive systématique**, et les deux pannes n'ont pas le même remède.

⭐⭐ **Contre les seuils du dépôt, pas contre un nombre choisi** : `carte_segments.py` publie
40 µm (même feuille, raccordable) et 250 µm (feuilles voisines). À 5,76 mm la chaîne est à
**69 µm** — sortie de la première bande vers 3,5 mm, **encore loin** de la seconde. Elle n'a
donc **pas changé de feuille** ; elle n'est simplement plus raccordable à celle-ci. Et la
dérive **décélère** : 15,9 → 14,6 → 12,0 µm par mm parcouru.

### ⚠⚠ Deux explications concurrentes, écartées par la mesure

1. **« Elle sort par le bord du segment publié. »** Pas exotique : le morceau part à
   **29 cases du bord** (1,4 mm) et la chaîne parcourt 5,76 mm. Mesuré : **0,0 %** des points
   ont leur plus proche voisin sur la bordure jusqu'à 2,9 mm, **0,1 %** à 5,76 mm.
2. **« C'est latéral, pas de la profondeur. »** L'écart total (48,0 vox) et l'écart **projeté
   sur la normale** (28,8) sont mesurés séparément. La composante normale est réelle.

⚠⚠⚠ **Et ma première version du contrôle nº 1 NE POUVAIT PAS se déclencher** : elle
définissait le bord par la **forme** de la grille, or le maillage publié laisse une marge vide
de **cinq cases** — donc « 0 % au bord » était vrai **par construction**. C'est une sonde qui
l'a dit. Le bord est maintenant *là où le valide s'arrête* (une case valide qui touche une case
invalide) : exact, tient compte des trous, **aucune marge à choisir**.

### ⚠ Ce que ça ne dit toujours pas, et où la découverte commence

L'encre reste nécessaire pour savoir si le **texte** suit — mais cette mesure la **cible** :
la couverture s'effondre vers le **maillon 8**, donc c'est là qu'un rendu de plusieurs heures
vaut son prix, et pas au maillon 1 où la surface est encore à 100 % sur du terrain connu.

⚠ Feasibilité du rendu, mesurée : la boîte niveau 0 d'un maillon vaut **643 Gvox** au maillon 1
et **3 417 Gvox** au 60, et **aucun volume niveau 0 de ce rouleau n'est local**. Le rendu est
une opération **réseau**, pas de calcul.

⚠⚠ **Piège d'outillage payé en enregistrant la batterie** : `temoins.sh` **change de projet en
changeant de répertoire** (`cd "$ROOT/experiments"`, `cd "$ROOT/inference_xpu"`), donc
*l'endroit* où une batterie est enregistrée décide de *l'environnement* qu'elle reçoit.
`src/excision/` n'a pas PIL : une figure dont la batterie **dessine vraiment** y échoue sur un
`ModuleNotFoundError` qui ne dit rien de la figure. Les figures voisines de cette région s'en
tirent parce qu'elles importent PIL **à l'intérieur d'une fonction** — donc leur batterie ne
dessine pas, ce qui est exactement ce qu'on ne veut pas. Les deux nouvelles batteries sont
enregistrées dans la région `$ROOT`, et la raison est écrite sur place.

---

## ⭐⭐⭐⭐⭐ `docs/` EST RANGÉ — 522 fichiers à la racine → 58, et l'audit que ça a forcé

`docs/` : **58 documents**, plus `mesures/` (384), `journaux/` (79), `registres/` (1),
`images/` (77) et les treize dossiers de campagne, déjà rangés par rouleau.

⭐ **Une nature n'est pas une extension, c'est un usage**, et c'est mesuré : les `.json` sont
cités **77 fois** par les documents, les `.log` **jamais**. Deuxième signal concordant et
indépendant : les `.log` sont gitignorés. Et un **registre** bat son extension —
`murs_et_causes.tsv` est tenu à la main, donc une purge des sorties ne doit pas l'emporter.

### ⚠⚠ Ce que le rangement a forcé à auditer, et qui était CASSÉ avant lui

- **Tous les chiffres publiés du dépôt étaient à une réorganisation d'être « vérifiés » par
  personne.** `verifier_chiffres.py` lisait ses 50 mesures en `racine / "docs" / "x.json"`,
  écrit **quarante-quatre fois** — deux littéraux séparés, donc invisibles à toute réécriture
  textuelle — et chaque lecture est gardée par `if p.exists():`. Un `docs/` rangé aurait fait
  sauter cinquante sources **en restant vert**. Le remède n'est pas quarante-quatre
  réparations : c'est **dire l'endroit une seule fois** (`DOSSIER_MESURES`) et **enregistrer**
  ce qu'on a cherché. Mesuré : 50 sources, 0 manquante, avant comme après le déplacement.
- **81 fichiers seraient entrés dans le dépôt sans un mot.** `.gitignore` dit `/docs/*.log`,
  une règle **ancrée** : les journaux déplacés en sortent, donc entrent dans le suivi.
- **`git mv` refuse un fichier qu'il ne suit pas, et refuse au MILIEU du plan** : 14 fichiers
  déplacés puis un arrêt sec sur le premier `.log`.

### ⭐ Le danger visé, attrapé sur le premier vrai usage

Une citation morte se voit ; un **écrivain** non réparé recrée la mesure à la racine, à côté du
fichier rangé — **deux fichiers pour une mesure**, l'un frais et l'autre mort, sans qu'aucune
sortie ne change. `mentions_a_lancien_endroit()` a trouvé **cinq blocs « Reproduire » du
document 44** qui écrivent `$PWD/docs/chaine_*.json`, des fichiers *qui n'existent pas encore*
— donc invisibles pour tout outil qui ne connaît que ce qui est là. 19 endroits réparés.

### ⚠ Deux contradictions internes des outils

- `deplacer.py` **refusait de laisser une citation qu'il avait décidé exprès de ne pas
  réparer** : sa règle dit qu'un chemin écrit dans un résultat publié ne se réécrit pas, et son
  contrôle final le comptait comme pendant. Aucun plan touchant un fichier nommé dans un
  résultat ne pouvait aboutir — un refus que personne ne peut satisfaire. 125 chemins de cette
  classe ici, dont un recensement qui en cite 51. Ils sont **nommés dans le rapport**, et une
  citation dans un fichier qui n'est PAS un enregistrement fait toujours refuser.
- La docstring de `REGISTRES` **promettait une vérification qui n'existait pas**. En l'écrivant,
  elle a corrigé sa propre liste : `verbes.json` est lu comme une entrée par `lplv` mais
  **produit** par `./lplv --verbes --json`. Le classer en registre l'aurait mis hors de portée
  d'une purge de sorties alors que c'en est une.

### ⚠⚠ CORRECTION — ma section d'hier disait l'inverse, et c'est l'auteur qui a tranché

J'avais écrit que les six dossiers restants avaient chacun « une raison » de rester : un
environnement de dépendances, un livrable, des données versionnées. **L'auteur a redemandé le
repli deux fois**, et il avait raison sur le fond : une raison de rester n'est pas la même
chose qu'une raison d'être à la RACINE. Un environnement de dépendances peut vivre **avec son
code** (`src/xpu/pyproject.toml`), un livrable est un document (`docs/article/`), et des
données versionnées sont des données (`data/artefacts/`, avec l'exception `.gitignore` qui
va avec). Les trois « raisons » étaient des raisons de ne pas fusionner les
environnements — pas de garder neuf dossiers de premier niveau.

### ⚠⚠ Deux réponses à « qu'est-ce qu'un script de ce dépôt », et elles avaient divergé

`lplv.FAMILLES` nomme **cinq** familles (`src/`, `src/tracecheck/`, `src/xpu/`,
`src/excision/src/`) pendant qu'`appelants.py` jugeait **`src/` seul**, en dur. Donc `lplv`
savait lancer un verbe dont le garde-fou ne se demandait jamais si quelque chose l'exécutait :
**un orphelin hors de `src/` était invisible par construction**. Mesuré après unification :
**214 → 233 scripts jugés**, **27 → 31 orphelins**, les quatre nouveaux tous hors de `src/`.

⚠ Et `FAMILLES` n'est pas « tout le Python du dépôt » : `src/apprendre/*.py` en est
**délibérément** absent. Ce sont des définitions de scènes Manim, exécutées par
`manim <fichier> <Scene>`, pas des programmes — en faire des verbes créerait des verbes qui
échouent sur `lplv <verbe> --help`. La raison est écrite là où quelqu'un voudra les ajouter.

### ⚠⚠ CHANTIER B — la mesure CONTREDIT le plan, et c'est le plan qui cède

Le plan disait « un dossier par ROULEAU ». Mesuré avant d'y toucher :

- `data/` est **entièrement gitignoré** — **0 fichier suivi par git**. Le réorganiser ne change
  rien pour qui clone le dépôt ; ça ne touche que la machine de l'auteur.
- **11 des 81 dossiers seulement nomment un rouleau.** Les 86 % restants sont des
  *expériences* (`chaine_*`, `spires_*`, `ext_*`), et les forcer sous un rouleau serait faux.
- `data/trace/` groupe **déjà** par rouleau à l'intérieur — le rouleau est une SUBDIVISION
  d'une expérience, pas l'inverse.
- Coût : 296 citations sur 64 chemins distincts, plus 177 Gio à déplacer.

⭐ Donc le déplacement est cher, risqué, et n'achète rien de visible. Ce que `data/` appelle
vraiment, à 177 Gio, c'est **« qu'est-ce que je peux effacer »**.

**`src/depot/donnees_sans_appelant.py` répond, et le chiffre est là : 50,6 Gio.**

| classe | dossiers | poids | ce que ça veut dire |
|---|---:|---:|---|
| orphelins | 25 | **44,3 Gio** | aucun script, aucun document ne les nomme |
| en journal seulement | 3 | **6,3 Gio** | un journal se souvient d'eux ; aucun code vivant |
| vivants | 52 | — | nommés par un script ou un document |

⚠⚠ **NOMMER N'EST PAS EFFACER, et l'outil n'efface jamais.** Un dossier que rien ne nomme peut
être une entrée téléchargée une fois, ou le résultat d'une campagne qu'on n'a pas encore
écrite. Dire « périmé » et remplacer sont deux actes — même discipline que
`fraicheur_des_figures.py`, qui ne touche jamais `docs/images/`.

⚠ Et la nuance qui rend le verdict utilisable : un dossier nommé **seulement dans un journal**
n'est pas nommé par du code vivant. Un journal prouve un usage *passé*, pas un besoin
*présent* — les confondre ferait effacer ce qui permet de recouper une campagne déjà publiée.

⚠ Le nom nu ne compte pas, seul le chemin `data/<nom>` compte : `data/out` et `data/trace`
portent des mots courants, et chercher « out » les déclarerait vivants depuis n'importe quelle
prose. Même discipline que le préfixe d'identifiant, qui n'en est un que si un document en
définit un membre. Sondé dans les deux sens.

---

> ⚠⚠ **Un test cassé par un `push`, pas par un commit.** `permalien.py` vérifiait le genre
> d'un dossier au commit publié en nommant `analysis` — vrai jusqu'au rangement, et **faux dès
> que `origin/main` a rattrapé HEAD**. Le contrôle est passé rouge sans qu'une ligne de
> `permalien.py` ait bougé. La leçon : une fixture qui nomme un chemin doit viser un chemin
> **stable dans le commit visé**, et le vérifier au lieu de le supposer — c'est ce que fait
> désormais le contrôle « le dossier témoin existe bien dans le commit visé », ajouté à côté.

## ⭐⭐⭐⭐⭐ LE REGISTRE N'A PLUS AUCUNE CAUSE OUVERTE — la graine rate de SEPT SPIRES

![Où commence la matière sous chaque graine](docs/images/54_graines_endroit.png)

La dernière cause ouverte du dépôt — *« la graine, c'est-à-dire l'endroit »* — est **fermée par
la mesure**. `54` avait écrit le préalable (*sonder la graine avant de payer le tracé*) et
`matiere_au_point.py` répondait **oui ou non**. Mais « non » recouvrait deux situations qui ne
demandent pas la même chose : une graine **à côté** de la feuille, qu'un calcul corrige, et une
graine **dans le vide**, que rien ne sauve.

| sonde | distance à la matière |
|---|---:|
| `ps256` dans son repère (L0) | **0 µm** |
| `ps256` converti en L2 | **0 µm** |
| `m7` **dans son propre repère** (L2) | ≈ **7,1 spires** |
| `m7` converti en L0 | ≈ **8,9 spires** |
| l'un ou l'autre lu **sans conversion** | rien dans 8 blocs, 4 913 requêtes |

⭐⭐⭐ **`ps256` désigne de la matière dans LES DEUX repères ; `m7` n'en désigne dans AUCUN.**
Ce n'est donc pas un défaut de conversion : convertie correctement, elle rate quand même.
À 173 µm d'espacement inter-spires, elle rate la feuille de **sept épaisseurs de papyrus**.

⭐ **Ce que ça ferme** : l'endroit explique la famille `m7` — ses traces n'ont jamais eu de
feuille à suivre. C'est la **cause** de la note de portée de `54` (*« les trois quarts du
maillage tombent hors du volume »*) : c'est le **point de départ** qui est dehors.

⚠ **Ce que ça ne ferme pas** : le mur. `ps256` part **sur** de la matière et ses traces portent
quand même quatre à cinq fois moins de structure que le segment publié.

⚠⚠ Et lire une coordonnée dans le mauvais repère **ne rend pas une erreur** : 4 913 blocs
parcourus sans rien trouver, sans un refus ni un avertissement — *un autre endroit, ou rien,
avec le même aplomb*.

**Registre : 30 causes, 19 éliminées, 10 confirmées, 1 bloquée, ZÉRO ouverte.**

⚠ Trois fois dans la même passe, un contrôle a cherché son propre motif dans le fichier qui le
contient. La parade n'est pas un meilleur motif : c'est de faire de la chose contrôlée une
**donnée** (`LEGENDE`, `GLYPHES_ABSENTS`) au lieu d'un texte à grepper.

---

## ⭐⭐⭐⭐⭐ LE RACCOURCI EST CÂBLÉ — et il est incapable d'empirer les choses

`profiler_une_surface.sh` demande son plan à `sous_fenetre.py --shell`, rend les fenêtres
`RENDRE` d'abord, **garde leur pile** tant que des filles peuvent en dériver, puis dérive.
Sur la série du dépôt : **3 rendus évités sur 4**.

⭐ **Trois replis, chacun bruyant** — plan incalculable, pile absente ou inexploitable,
dérivation échouée — et chacun retombe sur *rendre comme avant*. On ne peut donc jamais
**perdre** une fenêtre à cause du raccourci ; au pire on ne gagne rien. `DERIVER=0` le
désactive sans le retirer.

⚠ **Un seul site de dépôt dans le cache**, portant sa garde chez lui (`deposer_cache`). Il y en
avait deux, et deux sites finissent par ne plus poser la même garde : celui qu'on oublie dépose
un profil à moitié écrit que **toutes** les campagnes suivantes reliront comme un résultat.

### ⚠⚠ Quatre de mes contrôles ne pouvaient pas échouer

Le témoin est passé de 33 à 50 contrôles, et **quatre des premiers étaient faux** :

- comparer des **numéros de ligne** pour dire « après » — muet dès que l'appel passe dans une
  fonction → remplacé par la propriété (le dépôt est **gardé** par un profil non vide) ;
- `chk '[ $? = 0 ]'` — `$?` lit le retour du **harnais**, pas de la fonction → capturé tout de
  suite ;
- grepper le fichier **qui contient le contrôle** → grepper le corps **privé de son témoin**,
  plus un contrôle qui vérifie que l'exclusion marche ;
- des motifs qui matchaient la **prose du commentaire** → des motifs qui visent le **site
  d'appel**.

⚠ Deux pièges de shell : un motif traversant `chk` → `eval` → `grep` voit son `${…}` devenir une
**ancre de fin de ligne** ; et `grep -qF "--shell"` prend `--shell` pour une **option**.

⚠ **Câblé et sondé, pas encore exercé sur un vrai rendu.** La première campagne de convergence
sera la mesure.

---

## ⭐⭐⭐⭐⭐ LE RACCOURCI DE RENDU — éprouvé par 13 agents, il tient

![La géométrie du raccourci](docs/images/56_sous_fenetre.png)

**Rendre n=161 produit déjà n=81, n=41 et n=31.** Ce sont **les mêmes fichiers**, pas des images
qui se ressemblent : un rendu de N couches est une pile **centrée** sur la surface, donc deux
fenêtres rendues au même endroit partagent toutes les tranches de la plus étroite.

⭐ **Et il n'y avait rien à construire** : `depth_profile.py` porte déjà `--from-layer`,
`--to-layer`, `--traced-layer`. Ce qui manquait était l'**arithmétique dite une fois** —
`src/depot/sous_fenetre.py`. Sur la série du dépôt : **3 rendus évités sur 4**.

**8 mesures indépendantes + 5 tentatives de réfutation** (13 agents, 2,95 M tokens) :
**6 sites confirment**, chacun **toutes** ses tranches identiques octet pour octet et **23
mesures de profil sur 23**, zéro différence. **Aucun ne réfute.** Les 2 restants sont
IMPOSSIBLE pour des raisons de **données**.

### ⚠⚠ Trois choses que je n'aurais pas trouvées seul

1. **Une borne que RIEN ne vérifiait** : `--from-layer` désigne des **numéros de fichier**, pas
   des positions. Sur une pile trouée, la sous-plage rend un profil **plus court, en silence**.
   `verifier_pile` refuse désormais — et une pile du dépôt utilise vraiment trois chiffres
   (`060.tif`), donc le contrôle porte sur l'**ensemble des numéros**, pas sur les noms.
2. **Un piège de l'instrument** : la **console** imprime les indices de pic en **ABSOLU**, le
   **JSON** les stocke **RELATIFS**. Trois vérificateurs ont failli conclure à une réfutation en
   lisant « couche 42 » contre « couche 17 » — un écart qui est exactement le décalage de
   fenêtre. Ce n'était dit nulle part ; ça l'est maintenant.
3. **1,89 Gio de TIFF illisibles** : `data/leur_graine/rendu_161`, 161 fichiers, en-tête `II*\0`
   correct puis offset d'IFD **nul**. [`51`](docs/51_une_pente_a_deux_appuis.md) disait « le
   profil **survivant** » sans nommer ce qui avait tué l'autre. ⚠ Ce n'est **pas** la panne de
   [`54`](docs/54_cinq_rendus_vides.md) : celles-là s'ouvrent et sont noires, celle-ci ne
   s'ouvre pas.

⭐ Le réfuteur « arithmétique » a **redérivé indépendamment** la condition de parité que
`peut_deriver` portait déjà : le décalage est `N//2 − N//2`, pas `(N_large − N_étroite)/2`. La
réfutation a validé le module en tombant sur la formulation naïve de ma consigne.

⚠ **Pas encore câblé** dans `profiler_une_surface.sh` : il faudrait garder le rendu large vivant
pendant toute la boucle, alors que le script le supprime à chaque tour (562 Mo par pile). C'est
un changement d'ordonnancement **et** de disposition disque dans un script qui produit des
résultats publiés. L'arithmétique, elle, est livrée et éprouvée.

---

## ⭐⭐⭐⭐ CHANTIER A — le doublonnage mesuré, et une découverte qui vaut du TEMPS

![Le contenu identique de data/, par motif](docs/images/56_doublons.png)

**35,58 Gio de contenu identique** dans `data/`, mesurés **par hachage** sur 68 540 fichiers.
⚠ Le proxy « même nom + même taille » du plan annonçait 17,4 Go et se trompait **dans les deux
sens** : il comptait des chunks zarr homonymes de contenu différent, et il ratait l'essentiel.

⭐⭐ **58,6 % ne sont pas un doublon de campagne, ce sont des FENÊTRES IMBRIQUÉES.** Une fenêtre
de 31 couches est le **centre** d'une fenêtre de 81 rendue au même endroit : la tranche `i` de
l'une **est** la tranche `i+25` de l'autre, au bit près. Les paires trouvées sont exactement la
série de convergence — **(31, 81)** sur 2232 groupes, **(41, 161)** sur 861.

| motif | poids |
|---|---:|
| **fenêtres imbriquées** | **20,85 Gio** |
| autre | 10,51 Gio |
| même fenêtre, deux campagnes | 4,22 Gio |

⭐ **Le gain n'est donc pas du disque, c'est le temps de rendu de toute campagne de
convergence** : rendre n=161 produit **déjà** n=81 et n=41. ⚠⚠ Et le cache qu'on vient
d'écrire, indexé sur (surface, niveau, N), **ne peut pas le voir** — seul un cache par
**tranche** le verrait. C'est la marche suivante, et elle n'est pas faite.

**Le cache par contenu est livré** (`src/depot/empreinte_surface.py` +
`src/outils/profiler_une_surface.sh`). ⚠ Exclu de la clé, chacun une panne évitée : la **date**
(recopier une surface la change sans changer un octet), le **chemin absolu** (deux machines ne
partageraient jamais un cache), l'**ordre du système de fichiers** (le tri est ce qui fait
d'une clé une clé). ⚠ **Non exercé sur un vrai rendu** : la porte de sortie du plan demande
quinze minutes et un volume distant. Ce qui est vérifié est la forme — compteurs imprimés,
dépôt **après** le profil, clé venant de l'instrument.

⚠ **Rien n'est supprimé** : l'outil mesure et nomme. Un effacement n'est pas réversible.

---

## ⭐⭐⭐⭐⭐ LE DÉPÔT EST RANGÉ — `src/` en dix familles, 1011 citations réécrites

`analysis/src` (126 fichiers à plat) et `tools/` (73) sont devenus **`src/`**, en dix familles.
Détail et mesures : [`56`](docs/56_le_grand_menage.md).

![Les 219 greffons du dépôt](docs/images/56_verbes.png)

```
src/outils/ 61   src/figures/ 37   src/nappe/ 22   src/volume/ 15   src/graine/ 15
src/encre/  13   src/campagnes/ 12  src/tables/ 10  src/depot/  8   src/commun/  8
```

⭐ **`src/commun/` est une mesure, pas un fourre-tout** : les modules importés par leurs
frères. ⚠ Ma première mesure en annonçait 8 et elle était **fausse** — ancrée sur `^import x`,
donc aveugle à `import x  # commentaire`. Le remède n'a pas été de mieux compter mais de
**cesser de compter** : chaque module met toutes les familles sur son chemin, donc un
reclassement futur ne casse aucun import.

⚠⚠ **Mon estimation disait ~490 citations, la mesure en a trouvé 1011.** Deux fois plus. Plus
62 scripts shell qui remontaient d'un cran vers la racine, 50 `sys.path` qui supposaient un
dossier plat, et 12 chemins **assemblés** qu'aucune réécriture textuelle ne peut voir —
`src/depot/deplacer.py` les NOMME au lieu de les taire.

**37 échecs → 0**, et aucun trouvé en relisant : les extraits en ligne de `temoins.sh`
pointaient chacun vers un dossier ; mon insertion de `sys.path` **ignorait l'indentation** (18
occurrences indentées → `IndentationError`) ; sept chemins assemblés ; et le témoin de
`lancer.sh` a attrapé que le **gel** d'un script doit vivre à la profondeur que ce script
suppose — les scripts remontant de deux crans, `.lances/` devient `.lances/gel/`.

⚠ **N'ont PAS bougé** : `src/tracecheck/` (le livrable que l'article décrit), `src/excision/` et
`src/xpu/` (chacun son environnement). Décision par dossier, pas coup de balai.

**Tout passe par `./lplv`** — `./lplv --help`, `./lplv <verbe> --help`, `./lplv --version` —
donc plus personne n'a besoin de connaître un chemin, et un reclassement futur est invisible.

---

## ⭐⭐⭐⭐ CHANTIER C LIVRÉ — `lplv`, le point d'entrée que 218 greffons attendaient

Le chantier C de [`56`](docs/56_le_grand_menage.md). **Aucune architecture n'a été créée ici :
elle a été constatée et nommée.**

![Les 218 greffons du dépôt](docs/images/56_verbes.png)

**218 verbes, zéro nom ambigu, 98 qui s'auto-testent, 72 qui rendent du JSON.** Rien n'est
déclaré à la main — la famille vient du chemin, `--verifier` et `--json` sont lus dans le
fichier, et le résumé est la première ligne de docstring, c'est-à-dire **exactement la chaîne
que le module donne déjà à son `argparse`**.

```bash
./lplv --help              # les verbes, chacun avec sa propre première ligne
./lplv <verbe> --help      # SON aide, produite par lui-même
./lplv --version           # de quel palier il s'agit
```

⭐ **`lplv <verbe> --help` EXÉCUTE le module.** Re-lire son `argparse` pour en refabriquer une
aide produirait une seconde description libre de dériver — la panne exacte que ce point d'entrée
existe pour empêcher (skill `doc-derivee`, cran 2).

**Les paliers tombent tout seuls, mesuré** : l'arbre allégé de la release, construit dans un
dossier temporaire depuis la seule liste `GARDES`, rend **204 verbes au lieu de 218**, sans
erreur ni configuration. Et un verbe absent de ce palier ne répond **pas** « commande
inconnue » : il dit qu'il existe ailleurs, nomme son dossier, et sort en 3 au lieu de 2.

### `inference/` est parti aussi — et c'est une CORRECTION de ma conclusion de la veille

J'avais écrit qu'il restait, sur l'argument de son README (témoin CPU du ×4,5 iGPU). L'auteur a
objecté que le témoin devait être un **mode**, pas un dossier. Il a raison, et la mesure va plus
loin : deux dossiers, c'étaient **deux constructions de torch différentes**, donc la comparaison
mélangeait l'appareil ET la build. `infer_ink.py` prend désormais `--device auto`, et la règle
qui en fait un pipeline adaptatif plutôt que silencieux est : **« auto » retombe, « xpu »
REFUSE**. Le choix est une fonction pure — 10 contrôles hors ligne, sans GPU, sans torch.

### ⚠ Ce qui est demandé et PAS fait, avec son coût mesuré

L'auteur veut **un seul `src/` avec des sous-dossiers et un namespace**. C'est le bon état final
et `lplv` est précisément ce qui le rend abordable — mais c'est un chantier à part, mesuré :
**~490 citations de chemin** (178 dans `tools/*.sh`, 227 dans `docs/*.md`, 86 dans `temoins.sh`),
plus 24 imports entre frères et 51 `sys.path.insert`. Il lui faut son propre outil de réécriture,
qui **refuse** de laisser une citation pendante. Familles dérivées des préfixes réels :
`figure_*` 38, `table_*` 10, `campagne_*` 12.

---

## ⭐⭐⭐ MÉNAGE — état au 2026-08-25 (nuit) : `htr/` retiré, les 25 emprunts repointés

Premier morceau du grand ménage ([`56`](docs/56_le_grand_menage.md)). Deux modules neufs, une
suppression, et **deux chiffres du plan corrigés d'un facteur quatre**.

### Ce qui est parti, et ce qui reste — avec la raison à chaque fois

| | verdict | preuve |
|---|---|---|
| `htr/` | **retiré** | un seul fichier, remplacé par `src/encre/structure.py`, **zéro site d'appel** sous quelque orthographe |
| `inference/` | **reste**, venv retiré | son README argumente qu'il est le **témoin CPU** du ×4,5 iGPU validé à sortie identique ; `pyproject`+`uv.lock` versionnés → rejouable |
| `src/xpu/` | **reste entier** | c'est l'environnement de l'encre, et l'encre est le prochain chantier nommé |

### ⚠⚠ Deux mesures qui contredisent le plan

**`du` ment ici d'un facteur quatre.** `uv` installe en **liens durs** vers `~/.cache/uv`, donc
un fichier de venv est un *nom de plus* sur des octets déjà là. Retirer `htr/` + `inference/.venv`
libère **0,15 Gio tout de suite**, 4,09 de plus **seulement après `uv cache prune`** (non lancé :
c'est une ressource partagée avec la machine, pas une décision du dépôt), et 3,06 **jamais**.
Soit 4,24 Gio, pas 16,6. Calcul dans l'arbre : `src/depot/poids_recuperable.py`.

**Les « 25 sites d'appel » d'`inference/` étaient des EMPRUNTS, pas des besoins.** Le motif écrit
partout — *« le seul environnement porteur de Pillow »* — était faux (la racine déclare
`pillow>=10.0`) et **nuisible** : `inference/` n'a pas `numcodecs`, le trou exact qui avait fait
conclure à tort qu'une graine n'était pas couverte. Les 25 sont repointés sur la racine ; les
**11 batteries** concernées passent depuis là.

### ⭐ `src/depot/permalien.py` — l'outil que les chantiers B et D réutiliseront

Son invariant : *un permalien ne vaut que si son commit est **sur le distant** et que le chemin
**existe** à ce commit.* ⚠ `HEAD` était **43 commits en avance** sur `origin/main` — un lien vers
`HEAD` aurait rendu 404 partout ailleurs qu'ici, et la panne ne se serait vue qu'après un push.
⚠⚠ Et **ce dépôt est privé** (mesuré : racine 404 sans session, dépôt public du même compte 200),
donc le lien vaut pour l'auteur et pas pour un lecteur extérieur — d'où le contrôle qu'il porte
le commit et le chemin **verbatim**, pour que `git show <commit>:<chemin>` s'en déduise hors ligne.

⚠ **La vraie montagne n'est pas là** : 203 Gio de dépôt, dont **177 dans `data/`**. Les venvs
sont 2 % du problème ; le levier reste le chantier A (97 Gio de rendus recalculés).

---

## ⭐⭐⭐⭐ REPRISE — état au 2026-08-25 (soir) : LA CHAÎNE TANGENTIELLE MARCHE

Le mur « l'extension tangentielle est un point fixe » a **une** cause qui marche, et elle a
**deux conditions qui se composent**. Détail complet : [`44`](docs/44_ou_la_chaine_se_trouve.md).

### Les deux corrections, et pourquoi il fallait les deux

1. **Un pas FIXE en voxels** (`PAS_VOX`), pas un pas de grille. Un pas de grille couvre
   `pas × longueur moyenne de tangente`, donc un maillage qui cisaille **s'envoie lui-même
   plus loin au coup suivant** : boucle de rétroaction, mesurée à 95 → **650 µm** en dix
   maillons. À pas fixe : **96,0 µm exactement sur vingt maillons**, boîte ×1,92, tous les
   points gardés.
2. **Un RECALAGE sur la matière à chaque maillon** (`RECALER=1`) : chaque point ramené sur la
   crête du champ de distance de la prédiction, le long de la normale du **maillage**.

⭐ **Le résultat, jugé contre le plancher du hasard mesuré à chaque distance :**

| parcouru | pas fixe seul | **les deux** |
|---:|---:|---:|
| 480 µm | +24,1 | +24,4 |
| **768 µm** | ⚠⚠ **+1,5** (mort) | ⭐⭐ **+19,0** |
| 1 920 µm | ⚠⚠ **−1,7** (mort) | ⭐⭐ **+15,1** |
| 3 840 µm | — | ⭐⭐ **+9,2** |
| **5 760 µm** | — | ⭐⭐⭐ **+6,9** |

**Poussée à SOIXANTE maillons, elle tient 5,76 mm** et ne meurt pas : l'avantage s'affaiblit de
+30 à +7, mais la pente **s'aplatit** sur le dernier millimètre (+6,7 puis +6,9). Plateau bas,
pas chute. Le segment publié, pour référence, est à +30,6.

⚠ **Coût** : 95 min pour les maillons 31→60, et ça ralentit (33 s au maillon 2, 114 s au 30)
parce que la boîte englobante grossit — **×5,32** à 60 maillons. Le pas fixe tient la
**distance**, pas la **forme**.

⚠⚠ **Réserve de portée** : tout part d'un **morceau de segment publié**, pas d'une de nos
traces. C'est ce qui rend la mesure propre, et c'est aussi un point de départ privilégié.

### ⚠⚠ Ce qui rend ces nombres lisibles, et sans quoi ils ne le sont pas

Un « % de points posés sur la matière » **ne veut rien dire seul** : une nappe jetée n'importe
où dans un volume dont un quart est de la matière en trouve sous une partie de ses points.
`--plancher` mesure ce hasard — **la même nappe translatée au hasard**, plusieurs tirages,
graine fixée — et **par maillage**, parce que la densité locale varie de onze points le long
d'une seule chaîne.

⭐ Il a corrigé une conclusion que je venais de publier : « à 1 920 µm un seul bond garde plus
de matière que vingt maillons » (46,1 contre 35,4 %) était **faux** — les deux sont au niveau
du hasard, +1,6 et −1,7. Ce n'était pas un croisement, c'était deux mesures mortes comparées
sur une échelle brute.

⭐ Et la circularité a été **contrôlée** : mesurer la projection **avant** son recalage donne
+19,1 et +15,3 contre +19,0 et +15,1 après. Identique à la première décimale, alors que la
demande de déplacement passe de 1,6 / 3,4 voxels à 0,06.

### ⚠ Ce que ça ne dit PAS

Que la chaîne suit la **bonne** feuille. Elle est sur *du* papyrus, franchement au-dessus du
hasard, sur près de deux millimètres. Savoir si c'est la feuille qui prolonge le texte demande
de l'**encre** — tâche ouverte de [`43`](docs/43_la_chaine_des_spires.md).

### Registre des murs

**30 causes sur 4 murs — 19 éliminées, 9 confirmées, 1 ouverte, 1 bloquée.**
La seule cause encore ouverte est **« la graine, c'est-à-dire l'endroit »**, sur le mur
« le tracé ne suit pas de feuille » ([`54`](docs/54_cinq_rendus_vides.md)).

---

## ⭐ REPRISE — état au 2026-08-25

### ⭐⭐⭐ Le dernier résultat : enchaîner la projection tangentielle MARCHE, et c'est borné

Trois mesures, dont deux ne coûtent **aucun rendu**. Détail complet :
[`44`](docs/44_ou_la_chaine_se_trouve.md) §7.

1. **À distance égale, la chaîne bat le bond.** À 478 µm, là où une projection unique
   **quitte sa feuille** (18,4 % de pic au bord, contre 0 à 6 % partout avant), la chaîne de
   cinq maillons de 95 µm y est **encore** : **2,0 %** de pic au bord et **+31 %** d'amplitude
   (0,1491 contre 0,1140).
2. **Et l'horizon est chiffré : six maillons, 580 µm.** Vingt maillons projetés en quelques
   secondes : marche droite jusqu'au 6ᵉ, puis emballement — au 20ᵉ il ne reste **615 points
   valides sur 14 280**. ⚠⚠ Une nappe de `PHercParis4` fait des dizaines de millimètres de
   tour : **580 µm est le centième d'un tour**, donc une chaîne **purement géométrique** ne
   fera jamais le tour d'une feuille.
3. **⚠⚠ CORRECTION d'un verdict antérieur** : « enchaîner est strictement pire qu'un seul
   bond » appartenait au **PAS** et non à l'enchaînement. À 95 µm par maillon, trois maillons
   étalent la boîte **×1,01** — exactement comme le bond direct de même longueur.

### ⭐⭐ L'instrument qui a tout permis, et il est gratuit

`--pas` est un pas de **grille**, donc la distance couverte vaut `pas × longueur de tangente` :
un maillage qui cisaille **couvre de plus en plus de terrain à commande constante**. La chaîne
de 238 µm a parcouru **2 044 µm et non 1 190**. Ce nombre est déjà écrit dans chaque
`meta.json` (`pas_voxels`, et désormais le cumul `parcouru_vox`), donc **une chaîne se réfute
sans rendu** :

```bash
SOURCE=… PAS=2 MAILLONS=20 PROFILS=0 DEST=… src/outils/chainer_tangentiel.sh
```

⚠ Nécessaire, pas suffisant : une chaîne peut garder un pas parfait en marchant droit hors de
sa feuille. Cette voie ne peut que **réfuter**, et c'est ce qui la rend bon marché.

### ⭐ La marche suivante, nommée avec son grounding

Recoller la nappe sur la **matière** entre les maillons. Ce n'est pas spéculatif :
[`41`](docs/41_marcher_le_long_dune_nappe.md) §6 fait déjà ce geste (transformée de distance +
recentrage sur la crête) et atteint **≈ 2,4 mm**, s'arrêtant *parce que le bloc se termine*.
⚠ Réserve : deux rouleaux, deux échelles — ce qui se compare, ce sont les **natures d'arrêt**.
La pièce manquante existe : `src/commun/suivre_nappe.py` expose `champ_de_distance`,
`normale_locale` et **`recentrer`**. ⚠ Contrainte : la boîte de notre nappe fait ~10 milliards
de voxels au niveau 0, donc il faut travailler au **niveau 2** de la pyramide (~156 Mio).

⚠⚠ **Ce n'est PAS `--correct` du traceur officiel**, déjà mesuré insuffisant par
[`43`](docs/43_la_chaine_des_spires.md) (« +0,89 au mieux »). Corriger une trace **après**
qu'elle a poussé et recaler une nappe **avant** de la reprojeter sont deux gestes différents.

### ⚠⚠ Six batteries n'avaient jamais tourné — le lanceur se vérifie maintenant lui-même

`src/outils/temoins.sh` tenait ses lignes de lancement **à la main**, donc la liste avait dérivé :
six fichiers sur quatre-vingt-dix portaient une batterie que personne ne lançait, et quatre
d'entre elles imprimaient « tous les témoins passent » là où le lanceur cherche `ALL PASS`.
Un garde-fou neuf (**« batteries non lancées »**) fait échouer le run si un fichier qui *gère*
`--verifier` n'est lancé par personne. ⚠ Le garde-fou « scripts sans appelant » ne pouvait pas
l'attraper : **une mention dans un document compte comme un appelant**.

---

## ⭐ REPRISE — état au 2026-08-23

Ce bloc est en tête pour une raison : c'est ce qu'il faut lire en premier après une coupure.

### Le prompt de la boucle, gardé ici parce qu'il se perd ailleurs

⚠ Il vit dans l'historique d'une session, donc il disparaît avec elle. Copié verbatim :

```
/loop LE GRAAL, ET IL EST ECRIT ICI PLUTOT QUE SUPPOSE : dérouler 100 % du recto d'un rouleau
AUTOMATIQUEMENT — le prix tolère 8 h d'humain là où l'état de l'art en dépense 775 (31 spires
× ~25 h de correction manuelle du transfert de spire à spire), et le livrable est une image
DOCKER qu'ils lancent. Ce n'est PAS lire du grec, PAS entraîner un modèle d'encre : l'encre
est la règle graduée, pas l'ouvrage, et pousser l'AUC ne sert pas l'objectif. La question se
réduit à une seule : QU'EST-CE QUI REMPLACE L'HUMAIN QUI CORRIGE LE TRANSFERT DE SPIRE A
SPIRE ? Cadrage complet : HANDOFF §0-§1 et docs/31_roadmap.md §1 ; problèmes ouverts de
l'équipe : data/repos/villa/scrollprize.org/docs/37_2026_open_problems.md.
Maintenant : continue à vider les tâches et tenter d'atteindre ce graal-là ; n'oublie
cependant pas de mettre à jour la documentation et que chaque script dans le terminal peut
être perdu, donc s'il mérite d'être du vrai code n'hésite pas. et également que c'est bien
les illustrations/figures/images dans les doc. NE PAS relancer temoins.sh en entier (trop long) — ne lancer que les batteries touchées.
```

Cinq exigences permanentes : **(a)** ⭐⭐⭐ **le graal est le déroulement AUTOMATIQUE livré en
Docker**, pas la lecture — il est rappelé dans le prompt lui-même parce qu'une session qui ne
l'a pas sous les yeux travaille sur un problème qu'elle n'a pas vérifié ; **(b)** vider le
registre de tâches ; **(c)** tenir la documentation à jour ; **(d)** tout script de terminal
qui mérite d'être du vrai code doit le devenir — un script perdu est une mesure perdue ;
**(e)** les illustrations, figures et images des documents comptent.

> ⚠⚠⚠ **Pourquoi le cadrage est DANS le prompt depuis le 2026-09-07.** Une session a passé
> une journée entière à mesurer le transfert de spire à spire — c'est-à-dire exactement le
> goulot du prix — **sans savoir que c'était ça**, puis a rendu une estimation de distance au
> graal tirée de sa mémoire au lieu des documents. Le cadrage était pourtant écrit ici en §0
> et §1, dans `31` §1, et les problèmes ouverts de l'équipe sont mirrorés dans le dépôt. Un
> objectif qui vit dans un document qu'on peut ne pas ouvrir n'est pas un objectif : il est
> désormais dans la première ligne de ce qui réveille la boucle.

### Où en est le dépôt

`MasterLaplace/LplVesuvius`, **privé**, `main` à jour. Une branche `release/progress-prize`
et un tag `v0.1.0-progress` portent la vue allégée : 922 fichiers sur 1116, 26 Mo. Elle se
reconstruit en une commande et **ne se tague que si sa batterie passe** :

```bash
src/outils/faire_la_release.sh v0.1.1-progress
git push origin release/progress-prize && git push origin v0.1.1-progress
```

### ⚠⚠ Le cadrage, qui n'a jamais changé

**L'objectif est le Grand Prix, quel que soit le temps que ça prend.** Le Progress Prize est
un jalon en chemin, pas la cible. Ne jamais rédiger comme si l'échéance du 31 août fermait
quoi que ce soit.

### Les quatre murs, mesurés, sur lesquels le travail continue

> ⭐⭐ **La feuille de route est [`55`](docs/55_les_murs_et_leurs_causes.md)** — un tableau par
> mur, une ligne par **cause candidate**, avec son verdict et le document qui le porte.
> **26 causes, 16 éliminées, 7 confirmées, 2 ouvertes, 1 bloquée.** Un mur n'est pas une tâche, c'est un
> espace de causes dont on retire une entrée à la fois : lister des tâches laisse croire qu'on
> avance quand on tourne, lister des éliminations montre l'espace rétrécir.
>
> ⚠ Le document est **rendu** depuis `docs/registres/murs_et_causes.tsv` et **gardé** : chaque ligne
> doit pointer vers un document qui contient encore son ancre, et la batterie compare le rendu
> au fichier. C'est la panne d'`EXTRACTION.md` — une table tenue à la main qui dérive en
> silence — rendue impossible.


| mur | ce qui est mesuré | document |
|---|---|---|
| le tracé ne suit pas de feuille | ⭐⭐ **la surface est EN TRAVERS de l'empilement, et ça se VOIT** : à étendue égale, une couche publiée montre une feuille de face, les nôtres des spires coupées en travers. Relief 0,79 et 0,87 contre 0,16 et 0,20. ⚠ Sur 27 séries, une seule porte un verdict α ; à 100,8, 384 et 796,8 µm, **100 % des fenêtres ont leur pic sur un bord de pile** | [`54`](docs/54_cinq_rendus_vides.md) §3 quinquies, [`53`](docs/53_le_temoin_positif_du_rendu.md), [`51`](docs/51_une_pente_a_deux_appuis.md) |
| les patchs publiés ne se recollent pas | un patch PAR feuille, paire la plus proche à 79 µm ≈ 2× le seuil | [`44`](docs/44_ou_la_chaine_se_trouve.md) |
| l'extension tangentielle est un point fixe | le cycle rogner-étendre converge vers ~6 cm². ⭐⭐ La projection **tangentielle** a **deux seuils** : contraste maximal vers **240 µm**, nappe encore sur sa feuille jusqu'à **~380 µm**. ⭐⭐⭐ **Enchaîner à PETIT pas est un levier qui MARCHE** : à 478 µm, là où un seul bond quitte sa feuille (**18,4 %** de pic au bord), la chaîne y est encore (**2,0 %**) avec +31 % d'amplitude. ⚠ Mais **borné** — au 6ᵉ maillon le pas s'emballe, l'horizon est **580 µm**, soit **1/100 de tour**. ⚠⚠ Le « strictement pire » mesuré à 238 µm par maillon appartenait au **pas**, pas à l'enchaînement | [`44`](docs/44_ou_la_chaine_se_trouve.md) §7 |
| la chaîne casse au sixième tour | et la repousse la coupe au troisième | [`43`](docs/43_la_chaine_des_spires.md) |

### Ce qui vient d'être fermé

- ⚠⚠ **Une pente a deux appuis, et vingt séries rendaient le même nombre.** Le refus « profil
  plat » de `49` agrège les amplitudes par un **maximum** — juste pour « y a-t-il quelque
  chose ici », faux pour « quelle est la pente ». `src/graine/appui_de_pente.py`
  (37 témoins) classe chaque appui et transforme un écart au bord en **borne signée** plutôt
  qu'en refus : appui étroit au bord ⇒ α majorant ⇒ une convergence tient ; appui large ⇒
  minorant ⇒ une condamnation tient ; les deux ⇒ rien. Sur 132 séries : 92 exactes,
  14 majorants, 0 minorant, 26 sans appui qui porte, **33 verdicts tombent**, 7 sauvés par le
  signe, et **0 des 75 convergentes** n'est perdue — parce que le seul signe observé préserve
  exactement ce qui est sous le seuil. ⭐⭐ **Vingt séries rendent +1,0135**, qui est
  `log(192/48)/log(161/41)`, l'identité du couple de fenêtres. Voir
  [`51`](docs/51_une_pente_a_deux_appuis.md).

- **Le plafond de générations ne fabriquait pas le résultat** : à budget ×3,3 l'aire est
  ×11,5 mais α passe de +0,89 à +0,95, **sous le bruit du tireur** (0,16). Voir
  [`50`](docs/50_le_rendu_attendait_la_memoire.md) §8. ⚠ Un seul tirage par budget, donc on
  ne peut pas *affirmer* que le budget est sans effet, seulement qu'on ne le voit pas.
- **La pyramide préserve α** : 0,02 d'écart entre niveaux 0 et 1 sur la petite surface, 0,06
  entre 1 et 2 sur la grande, pour une résolution de 0,20. Le plancher dépend de la
  **surface** : `depth_profile` refuse une image plus petite que sa fenêtre de 1024 px.
- **Le critère auto-référentiel a sa définition** : `src/graine/critere_relatif.py`
  (23 témoins). Ce n'est pas un critère de plus, c'est **le test qu'un candidat doit
  passer** — β = log(C₁/C₀)/log(n₁/n₀), lu comme α. ⚠ Appliqué au matériel réel : **une
  seule grandeur sur treize se lit en absolu** (`tiers_central`, 11 séries). Le profil
  n'offre pas de second critère absolu, ce qui **renforce** `47` au lieu de le lever.

### Ce que la nuit du 2026-08-24 a ajouté

- ⚠⚠ **Une fenêtre a DEUX bords.** Une fenêtre de N tranches centrée sur `couche_tracee`
  n'est pas symétrique quand N est pair : 40 tranches centrées sur la 20e atteignent 20
  couches d'un côté et **19** de l'autre. Comparer l'écart à la seule demi-fenêtre déclarait
  « intérieur » un écart posé sur l'autre bord — et allait faire publier α = +1,06 comme le
  premier α de ce rouleau dont les deux appuis mesurent. C'est `au_bord = 1,0` dans le
  profil, contre un verdict qui disait l'inverse, qui a tranché.
- ⚠ **Une série de plus de deux fenêtres a plusieurs couples.** Prendre les extrêmes
  maximise le bras de levier et peut réintroduire un appui vide : sur la campagne au
  niveau 2 (11, 41, 81, 83 couches) ça jetait le couple 41/83 qu'un rendu venait de payer.
  `juger_serie` retient le plus large couple **dont les deux bouts mesurent**, et dit lequel.
- ⚠ **Deux conventions de rangement des profils** coexistent, et une seule était vue :
  `audit_profils_plats.serie_de` les réconcilie, **niveau de pyramide inclus dans la clé**.
- ⭐ **Le niveau 2 coûte huit fois moins que le niveau 1** pour le même couple physique :
  6 h 30 contre ~11 min, mesuré. Le vérifier avant de lancer un rendu long.
- ⚠ **`profiler_une_surface.sh` refuse maintenant AVANT de rendre** un couple dont le
  rapport sera jugé insuffisant — une fenêtre de N tranches vaut `2*(N//2)+1` couches, donc
  40/81 tranches se lit 41/81, rapport 1,98, refusé après deux rendus payés.
- ⭐ **`rendre_surveille.sh` journalise son propre débit.** Sans ça j'ai mesuré à la main,
  avec une horloge que je ne contrôlais pas, et conclu « bloqué à 0,6 Kio/s » sur un rendu
  qui avançait à 89.

#### ⭐⭐ Le résultat de la nuit : 0 sur 75 contre 34 sur 63

« La fenêtre étroite montre-t-elle du relief » est **binaire, posée à l'intérieur de chaque
fenêtre** — ni seuil à régler, ni profondeurs à apparier, ni pente à poser sur deux appuis.
**Aucune** des 75 séries qui convergent n'a de fenêtre étroite plate ; **34 des 63**
condamnées en ont une. Suffisant, pas nécessaire. Le signal est entré dans l'outil public
(`tracecheck` publie `relief`), qui publiait jusque-là le moins bon des deux
(`edge_pinned`). Détail : [`51`](docs/51_une_pente_a_deux_appuis.md).

#### ⚠⚠⚠ LA RÈGLE À NE PAS ROUVRIR : une grandeur appartient à sa géométrie de lecture

**Trois fois dans la même nuit** j'ai déplacé un nombre hors de la géométrie qui l'avait
produit, et **aucune** n'a été trouvée par relecture — les trois par une mesure qui ne
collait pas :

1. le seuil de **2,25×** du README, mesuré en fenêtres de 1024 px, offert à un outil qui lit
   des morceaux de 128 px ;
2. les **taux d'erreur** comparant `relief` et `edge_pinned`, mesurés sur des piles rendues
   et présentés comme une propriété de l'outil ;
3. la **profondeur du corpus**, que j'ai déclarée « 65 couches » quand elle vaut **109**.

Le relief dépend de la profondeur (exposant **+1,01**) **et** de l'étendue dans le plan
(exposant **−0,830**, rapport ×3,16 entre 1024 et 256 px). La règle est désormais dans le
code à trois endroits plutôt que dans ma vigilance :

- `tracecheck` **écrit** `layers` et `window_px` dans son CSV ;
- `calibration_corpus.py` **refuse** deux géométries dans un fichier, et marque celle qu'on
  lui déclare à la main ;
- `figure_calibration.py` **l'imprime** sur le dessin.

#### ⭐ La calibration de `Scroll1`, et ce qu'elle ouvre

`tracecheck --all --csv` juge tous les segments publiés d'un rouleau en ~1,2 min chacun, sans
rien télécharger. Sur `Scroll1`, 80 segments à 128 px × 109 couches : relief **0,040 à
0,975**, médiane **0,744**, **aucun** sous le plancher. Détail et figure :
[`52`](docs/52_calibrer_sur_son_corpus.md).

⚠⚠ **Le refus a payé au premier usage réel** : un corpus publié n'est PAS homogène — 80
segments à 109 couches et **un à 6**. Une distribution unique les aurait fondus.

#### ⭐⭐⭐ ET C'EST FAIT : `Scroll 1` EST `PHercParis4`

L'alias de l'outil le dit — le corpus calibré **est** celui du rouleau qui nous résiste. Les
huit candidats relus **à la géométrie du corpus** (128 px × 109 couches, `src/outils/situer_nos_traces.sh`) :

| candidats | relief | ×plancher | rang sur 80 |
|---|---:|---:|---|
| ~~`m7` c0…c4~~ | ~~**0,0000**~~ | — | ⚠⚠ **retiré, voir ci-dessous** |
| `ps256` c0…c2 | 0,164 – 0,198 | ×8,2 – ×9,9 | **1** |

⚠⚠ **CORRIGÉ le 2026-08-24 — la ligne `m7` mesurait du VIDE.** Cette entrée affirmait que
« les cinq `m7` lisent zéro à toutes les géométries essayées, donc leur platitude est réelle
et non un artefact de fenêtre ». **Faux.** Les cinq piles rendues sont **entièrement noires**
(max 0, 0,0 % de pixels allumés, sur 161 couches) parce que leur maillage est écrit dans le
volume au **niveau 2** et a été rendu contre le **niveau 0** — le moteur a échantillonné des
coordonnées au quart de leur vraie position, donc dans le vide. Et l'instrument a compté
« 49 fenêtres avec matière » sur ces images noires, son seuil de matière étant **relatif au
maximum de la pile** : sur un tableau de zéros, `>= 0,5 × 0` est vrai partout.
⭐ Rebasé ×4 et rendu au niveau 2, `m7_c0` rend **max 255, 24,4 % de pixels allumés** : la
surface existe. **La coupure entre les deux familles de prédiction n'est plus établie**, et
cinq traces reviennent dans le jeu — elles n'ont jamais été lues. Détail, correctif et
batteries : [`54`](docs/54_cinq_rendus_vides.md).

⭐ Ce qui **reste** vrai : les trois `ps256` lisent de la structure (0,164 – 0,198, rang 1/80)
et restent au bas de leur propre rouleau. Leur maillage était dans la bonne frame, et le
correctif de l'instrument ne déplace pas leur chiffre d'un dix-millième.

#### ⭐⭐⭐ Et le témoin positif tranche : notre chaîne de rendu est FIDÈLE

La question que le classement n'avait jamais posée — *nos piles sont-elles comparables aux
piles publiées ?* — a sa réponse. Un maillage **publié** (segment `20230702185753`, format
`tifxyz` identique au nôtre), découpé à la taille de nos candidats, rendu **par notre chaîne**,
relu à 128 px × 109 couches :

| | relief | ×plancher | rang sur 80 |
|---|---:|---:|---|
| **notre rendu du maillage publié** | **0,8726** | **×43,6** | **72ᵉ sur 80** |
| le segment d'origine, tel que publié | 0,7912 | — | — |
| corpus, médiane | 0,7441 | — | — |
| nos `ps256` | 0,164 – 0,198 | ×8,2 – ×9,9 | 1ᵉʳ |

Le critère avait été **écrit et commité avant la mesure** ([`53`](docs/53_le_temoin_positif_du_rendu.md)
§3) : revenir dans la distribution ⇒ la chaîne est fidèle. Il revient **au-dessus de la
médiane**. Donc le déficit de relief de nos traces est une propriété de **nos traces**, pas de
notre instrument.

⚠ Coût : 80 min de rendu, 399 Mo, pour un morceau de 2380 × 2400 px sur 161 couches. Les trois
autres morceaux découpés n'ont pas été rendus — le critère ne demandait pas quatre points.

#### ⭐⭐⭐ La première VRAIE lecture d'une trace `m7` réfute la coupure

Le sondage disait **où** le maillage `m7` a de la matière. Ce morceau-là (30 × 30 points,
9 sondages sur 9 dans la matière) a été rendu au niveau 0 dans le repère rebasé — 2400 ×
2400 px, 161 couches, 600 Mo, 87,1 % de pixels allumés — puis relu à la géométrie du corpus :

| | relief | ×plancher | rang sur 80 |
|---|---:|---:|---|
| **`m7_c0`, enfin lisible** | **0,1589** | ×7,9 | **1ᵉʳ sur 80** |
| nos `ps256` | 0,164 – 0,198 | ×8,2 – ×9,9 | 1ᵉʳ sur 80 |
| corpus, médiane | 0,7441 | ×37,2 | — |
| maillage **publié** via notre chaîne | 0,8726 | ×43,6 | 72ᵉ sur 80 |

⭐⭐ **`m7` et `ps256` sont au même endroit.** La « coupure nette entre les deux familles de
prédiction » n'est pas seulement non établie : elle est **réfutée**. ⚠ Portée : cet énoncé
porte sur le morceau de `m7` **qui a de la matière**, pas sur le maillage entier, dont les
trois quarts tombent hors du volume scanné.

⭐ **Le mur se dit maintenant en une phrase au lieu de deux** : nos traces, quelle que soit la
prédiction dont elles sortent, portent **quatre à cinq fois moins** de structure en profondeur
que l'avant-dernier segment publié de leur propre rouleau — pendant qu'un maillage publié
passé par la même chaîne revient **au-dessus de la médiane**.

#### ⚠⚠⚠ TROIS conséquences du même oubli, et la troisième fausse toutes les aires

Le **niveau de la prédiction** n'était propagé nulle part, et trois choses en dépendaient :

1. **la graine** — un nombre L2 lu comme un nombre L0 désigne un point au quart de sa
   position, dans le vide → 13 rendus noirs ;
2. **le maillage** — il sort dans le repère de la prédiction, donc un rendu contre le scan
   tombe dans le vide même avec une graine valide (démontré en production le 2026-08-24) ;
3. ⚠⚠ **l'aire** — le traceur écrit `voxelsize` dans son `seed.json` et s'en sert pour
   `min_area_cm` **et** pour convertir en cm². On y écrivait 2,4 µm quelle que soit la
   prédiction ; un voxel `m7` fait **9,6 µm**, donc chaque aire est fausse d'un facteur
   **seize**.

| trace | pas de grille réel | aire annoncée | **aire réelle** |
|---|---:|---:|---:|
| `ps256` (L0) | 48 µm | 0,317 cm² | **0,317 cm²** |
| `m7` (L2) | **192 µm** | 0,317 cm² | ⚠⚠ **5,079 cm²** |

⭐⭐ Les deux se sont arrêtées au **même nombre de points** parce que `min_area_cm: 0.3` était
évalué dans deux unités. Le tableau de [`48`](docs/48_ou_monter_lexperience.md) §4, qui annonce
0,317 cm² des deux côtés, n'était pas un contrôle : c'était le même plancher dans deux systèmes.

⚠ **La comparaison « prédiction contre prédiction, au même endroit » reste donc à faire**, avec
des aires réellement appariées. Les trois correctifs sont dans `src/outils/tracer_une_graine.sh`.

#### ⚠⚠ CORRECTION — c'est la GRAINE, pas le maillage, et une requête HTTP l'aurait dit

J'ai écrit que « le maillage `m7` est écrit au niveau 2 et rendu contre le niveau 0 ». Le
rapport de formes valait bien 4, mais c'était un **corrélat**, pas le mécanisme. Deux cellules
du 2×2 le prouvent l'une par l'autre : `ps256_sur_graine_m7` ouvre le volume **pleine
résolution** et produit quand même un maillage dans le vide, tandis que `m7_sur_graine_ps256`
ouvre le volume **L2** avec une graine hors de ses bornes et produit un maillage **avec
matière**. **Le maillage suit le repère de la GRAINE**, pas celui du volume ouvert.

| graine | ce qu'il y a là (un bloc zarr) | ce que le traceur en a fait |
|---|---|---|
| `ps256` `[10752, 10616, 38740]` | valeur 34, bloc allumé à **100 %** | 8 traces avec matière |
| `m7` `[2924, 5324, 9260]` | ⚠⚠ **bloc absent du dépôt** | **13 rendus noirs** |

⚠⚠ Le traceur imprime `value is 0` puis `empty space tracing` et pousse quand même — sur les
**quatre** cellules, celles qui marchent comprises, donc cette ligne ne discrimine rien.

⭐⭐⭐ **Et le 2×2 croisé n'était pas en position de conclure** : sa colonne « graine `m7` »
tenait un **nombre** constant, pas un **endroit**. Préalable qui en sort, et il coûte une
requête : **sonder la graine dans le volume scanné avant de payer un tracé**
(`src/nappe/matiere_au_point.py`).

#### ⭐⭐⭐ ET EN REGARDANT : ce ne sont pas des feuilles, ce sont des spires en travers

Question de l'auteur devant la figure des piles vides : *« un jour on aura une vue des vraies
feuilles aplaties ou bien ? »*. Le dépôt mesurait le relief depuis des semaines **sans jamais
mettre une couche publiée à côté d'une des nôtres**. Fait, à étendue égale (512 voxels de
côté, 1,2 mm) et avec **la même chaîne de rendu** pour les trois dernières :

| vignette | ce qu'on voit | relief |
|---|---|---:|
| référence publiée | une **feuille de face** : fibres, mouchetures, déchirures | 0,791 |
| maillage publié, **notre** rendu | une feuille aussi : couverture continue, fibres | 0,873 |
| `ps256_c0` | des **rubans clairs séparés de vide**, des dizaines, parallèles | 0,198 |
| `m7_c0` | la même chose, plus serrée | 0,159 |

⭐⭐ **Ce ne sont pas deux qualités du même objet, ce sont deux objets.** Nos traces ne suivent
pas une feuille, elles en **traversent plusieurs**. Et c'est exactement ce que le relief disait
en moins lisible : une surface posée sur une feuille traverse air → papyrus → air, donc grande
amplitude ; une surface transverse rencontre du papyrus à toutes les profondeurs, donc profil
plat.

⚠ **La réponse à la question posée est NON** : ce dépôt n'a jamais produit une vue de vraie
feuille aplatie. Il en a mesuré l'absence de plusieurs façons sans jamais la regarder.
Figure et détail : [`54`](docs/54_cinq_rendus_vides.md) §3 quinquies.

#### ⭐ L'audit du dépôt entier : 31 piles vides sur 322, et le rayon de souffle est borné

322 piles rendues (175 Go) lues une couche sur quarante : **291 avec matière, 31 noires**,
9 illisibles (rendu en cours). Les 31 se rangent en **deux causes** : 29 viennent d'une graine
`m7` (repère de niveau 2), et 2 sont `boucle/corrige_nappe_gen1_poids100`, un **aplatissement
dégénéré** — grille 364 × 14, plan `x` entièrement négatif, zéro point valide sur 5096. ⭐ Aucun
document ne cite cette dernière. Détail : [`54`](docs/54_cinq_rendus_vides.md) §5.

⚠⚠ Corollaire à ne pas oublier : « nos traces sont plates » vaut pour `m7`, **pas** pour
`ps256` — lues à 1024 px elles donnaient 0,046, lues à 128 px elles donnent 0,198. Détail :
[`52`](docs/52_calibrer_sur_son_corpus.md) §6.

### ⚠ Les pièges qui se sont repayés, et leur remède définitif

- ⚠⚠ **`a && b && nohup c &` met TOUTE la liste en tâche de fond**, pas seulement `c`. Deux
  conséquences, et la seconde coûte cher : les variables affectées dans la chaîne
  n'atteignent jamais le shell appelant (symptôme : un `tail "$W/rendu.log"` qui lit
  `/rendu.log`), et surtout on n'a plus de poignée propre sur le processus. Payé le
  2026-08-24 : un rendu lancé ainsi a tourné **58 minutes** en écrivant dans un répertoire
  que j'avais supprimé, à manger 2,3 Go de RSS et la moitié de la bande passante, pendant
  que je cherchais pourquoi tout était lent. **Supprimer la sortie d'un rendu ne l'arrête
  pas.** Lancer en tâche de fond par l'outil prévu, et tuer **par PID**.

- ⚠⚠ **Une courbe se juge là où elle change — donc trois points ne suffisent jamais.** Payé
  **trois fois sur la MÊME courbe** le 2026-08-25 : à 3 points la portée tangentielle
  paraissait une pente monotone, à 6 un plateau suivi d'une falaise, à 9 un maximum suivi
  d'une descente douce **plus** une rupture ailleurs. Chaque forme était plausible et
  publiable, et chaque forme était fausse. ⭐ Le remède n'est pas « prendre plus de points »
  mais **densifier là où la forme bouge**, et l'admettre tant qu'on ne l'a pas fait.
- **`pkill -f` et `pgrep -f` matchent leur propre ligne de commande.** Payé **sept fois**,
  dont deux où mon shell est mort (exit 144) — la seconde le 2026-08-24, dans un
  `for p in $(pgrep -f …)` dont la boucle m'a tué moi-même. ⭐ Le remède qui marche vraiment
  n'est pas « tuer par PID » mais **ne pas chercher par ligne de commande** :
  `ps -eo pid,etime,comm | grep -E "vc_render|vc_grow"` ne peut pas se matcher lui-même,
  parce que `comm` est le nom court du binaire et non la ligne complète.
- **Une sonde qui scanne son propre fichier se matche elle-même.** Payé cinq fois. Le remède
  n'est pas de couper le motif : c'est de l'**ancrer sur la syntaxe** (début de ligne,
  position de commande).
- **Éditer un script pendant qu'il tourne le casse** : `bash` lit par offset, une insertion
  décale les octets et il reprend au milieu d'un token.
- **Un auto-test qui écrit sa fixture à un chemin FIXE ne supporte pas deux exécutions.**
  `src/outils/temoins_release.sh` a un verrou ; `src/outils/temoins.sh` n'en a pas encore.
- **Un échec avec un code de retour zéro n'est pas un échec** : c'est le lecteur qui se
  trompe de convention.
- **Une sonde qui cite son propre motif se matche elle-même** (septième fois, 2026-08-23 :
  la garde anti-`@f$` citait le marqueur dans son commentaire et voyait `temoins.sh`). Le
  remède n'est pas d'exclure le fichier — ça l'aveuglerait à une vraie occurrence — mais de
  **composer la chaîne à l'exécution**, pour qu'elle n'existe nulle part dans la source.
- **Les formules des documents s'écrivent entre dollars**, jamais avec le marqueur Doxygen,
  qui s'affiche littéralement. Repris par l'auteur ; `temoins.sh` le garde désormais.

### La règle de commit, désormais vérifiée

`type(scope): sujet`, **en anglais**, **zéro tiret cadratin**. Types : `chore clean docs feat
fix measure mesure perf resultat test`. `src/outils/format_des_commits.sh` (14 contrôles) le
vérifie, et la détection du français est déléguée à `src/encre/langue.py`.

### Vérifier que tout va bien, en deux commandes

```bash
./src/outils/temoins.sh            # tout, hors ligne
./src/outils/temoins_release.sh    # ce que la release livre, avec son verrou
```


## 0. ⚠⚠ LE CADRAGE — à lire avant tout le reste

Recadré par l'auteur le 2026-08-19, après qu'une première roadmap se soit trompée de
problème. **Ce projet ne vise ni à traduire, ni à transcrire, ni à dérouler 53 rouleaux
sur cette machine, ni à scanner, ni à entraîner un gros modèle.**

**Il vise à fermer la chaîne GÉOMÉTRIQUE** : une pipeline assez intelligente pour
cartographier un papyrus cabossé et carbonisé, **automatiquement**, par l'algorithmique
et par l'optimisation extrême là où ça bloque — puis **la leur donner à lancer**, pour
que les chercheurs fassent le calcul et la lecture à leur échelle.

⭐ Et c'est exactement ce que le prix demande, mot pour mot : *« The unrolling pipeline
should be **fully automated** »*, *« **or renders with ink** »*, et *« consider a **Docker
image that we can easily run** to reproduce your work »*. Les 775 heures d'annotation de
l'état de l'art ne sont **pas une barrière à l'entrée — elles sont la cible à
supprimer**.

> ⚠ Un concours open source ne se conçoit pas pour n'être gagnable que par qui possède des
> H100 et des téraoctets. Ce qu'il récompense est une **méthode que d'autres peuvent
> rejouer**.

Détail complet : [`31`](docs/31_roadmap.md).

## 1. ⭐⭐ L'OBJECTIF — et ce n'est pas le texte

> **Le but est le DÉROULEMENT, pas la lecture.** Traduire n'est pas notre métier.
> Repérer quelques lettres sert à **s'assurer que le rouleau assemblé et déroulé fait
> du sens** — l'encre est la **règle graduée**, pas l'ouvrage.
> *(cadrage de l'auteur, 2026-08-17)*

| famille | rôle |
|---|---|
| fusions, onde radiale, dépliage polaire, proximité géométrique, direction des fibres | **le travail** |
| détection d'encre, juge calibré, second rouleau | **l'instrument** |

⚠ Pousser l'AUC plus haut, chercher un meilleur détecteur d'encre ou faire transcrire
davantage **ne sert pas** l'objectif.

## 2bis. ⏳ REPRENDRE ICI — 2026-08-20, fin de journée

**Deux campagnes tournent en fond** (détachées, elles survivent à la fermeture de la session) :

```bash
tail -f docs/journaux/convergence_essais.log     # essai_ng2 puis essai_scale1, 4 rendus
ps -eo pid,etime,args | grep '\.lances/'   # ce qui vit encore
```

### Ce que la journée a établi, dans l'ordre où ça s'enchaîne

1. ⭐⭐⭐ **[`38`](docs/38_ce_qui_bouge_avec_la_fenetre.md) — le test de convergence.** On rend
   la même surface dans des fenêtres de plus en plus profondes. Un bon segment officiel garde
   sa distance (**α = +0,00**) ; nos traces la voient **suivre la fenêtre** (**α = +1,01**,
   jusqu'à 691 µm sans rien trouver). Aucun seuil, aucune vérité terrain, aucune échelle.
   **Toutes les distances publiées avant sont sans objet pour nos traces.**
2. **Ce que ça veut dire physiquement** : profil plat = la normale reste dans la même
   matière = **notre surface est une coupe radiale** à travers le rouleau. C'est ce que
   montre `docs/images/38_en_travers.png` à côté de `36_papyrus_PHerc1447.png`.
3. ⚠ **Cinq causes éliminées par mesure** : la graine (on a rejoué **la leur**), la
   prédiction (planarité 0,993 au point — `sonder_point.py`), la longueur (0,98 cm² échoue
   comme 23), le sens de la normale (identique avec `--flip-normals`), les paramètres
   (fichier minimal identique au leur → 23,05 cm² contre leurs 3,95).
4. ⭐⭐ **[`39`](docs/39_le_seam_de_correction.md) — le seam** : `vc_grow_seg_from_seed
   --resume --rewind-gen --correct <points.json>` prend une **liste de points 3D**. Chaque
   maillon existe **sauf un** : *dire où la surface aurait dû passer*.
5. ⚠⚠ **M1ter répondu, négativement, et disculpé** : le modèle du Grand Prize 2023 sort une
   **constante** sur un rouleau du prix (σ **45×** plus petit qu'où il marche) — et **le
   volume publié donne la même**, donc notre chaîne n'y est pour rien.

### Le lot en cours, et pourquoi

⭐ **L'hypothèse qui inverse** (`src/outils/convergence_des_essais.sh`, en fond) : une coupe
radiale **ne peut pas** se croiser elle-même ; une surface qui suit une spire revient près
d'elle-même à chaque tour. Nous aurions donc jeté les bonnes traces. `essai_ng2`
(112 139 croisements, poussée **avec** les vraies grilles de normales) est le candidat.
✅ **Rendu le 2026-08-20 au soir, et le résultat va dans le sens de l'hypothèse** :
`essai_scale1` (**0** croisement) donne **α = +0,99**, `essai_ng2` (**112 139**) donne
**α = +0,65**. Celui que le filtre condamne est le moins radial des deux.
⚠ Mais +0,65 n'est pas +0,00 : un intermédiaire n'est pas un demi-succès. Et ce qui joue
contre reste vrai — le segment officiel converge **sans** compte de croisements
catastrophique, donc « beaucoup de croisements » est au mieux un *symptôme*, jamais un
critère. Détail : [`38`](docs/38_ce_qui_bouge_avec_la_fenetre.md) §« l'hypothèse qui inverse ».

### ✅ Fait le 2026-08-20 au soir — la cible existe en image

⭐⭐⭐ **[`40`](docs/40_le_rouleau_entier.md) : 44 spires consécutives de `PHerc0172`, sans un
trou**, assemblées depuis les cartes d'encre publiées (`src/outils/mosaique_rouleau.sh`,
`src/volume/assembler_mosaique.py`, 18 témoins). 21 Mo téléchargés, ~3 min, **rien de
tracé ni rendu ici**.

⚠ **Le déroulement est le leur ; l'ordre est le nôtre.** Ce n'est pas un résultat de la
chaîne — c'est la **référence** qu'elle doit égaler, et jusqu'ici « ça marche » n'avait rien
à quoi se comparer.

⚠⚠ **Et ça referme la piste A** : la mosaïque est possible exactement là où le travail est
déjà fait (`PHerc0172` 53 segments, `PHerc0139` 38, `PHercParis4` 80) et **impossible sur les
rouleaux du prix** — `PHerc1447` publie 4 volumes de surface et **zéro** carte d'encre,
`PHerc0800` et `PHerc1203` ne publient ni l'un ni l'autre. Passer notre modèle sur ces 8
volumes reste faisable, mais `36` §5bis a déjà mesuré qu'il y sort une **constante**, et le
volume *publié* donne la même — donc la piste A n'est pas courte, elle est **bouchée à son
extrémité**.

### ✅ Fait dans la foulée — la piste B est construite (pas encore branchée)

⭐⭐⭐ **[`41`](docs/41_marcher_le_long_dune_nappe.md) : `src/commun/suivre_nappe.py`**,
24 témoins. Marche le long d'une nappe (tenseur de structure → normale, recentrage
sous-voxel sur la crête, reprojection de la direction à chaque pas) et écrit un
`PointCollections` que `--correct` sait relire — format **lu dans la source**, ordre des
points signifiant, coordonnées en (x, y, z).

⚠⚠ **Témoin négatif mesuré** : « au plus proche », sur deux spires à 4 voxels avec un trou
de 17, quitte sa nappe de **5,94 voxels** (au-delà de la voisine) là où la marche sur crête
reste à **0,67**. Facteur 9. Et le chemin naïf reste **connexe et plausible** — rien dans sa
forme ne le trahit.

⭐⭐⭐ **LA CAUSE CANDIDATE, LUE DANS LA SOURCE DU TRACEUR** (et elle CORRIGE une première
version de moi : j'avais accusé le masque binaire, à tort — le traceur en calcule
lui-même un champ de distance **signé**, `get_or_compute_sdt_chunk`).

`vc_grow_seg_from_seed` est un moindres carrés Ceres à **douze familles de résidus**, aux
poids par défaut `SNAP 0,1 · NORMAL 10 · DIST 1 · STRAIGHT 0,2 · DIRECTION 1 · SDIR 1 ·
CORRECTION 1`, et **`SURFACE_SDT 0`, `SPACELINE 0`, `REFERENCE_RAY 0`, `PATCH_NORMAL 0`**.
Trois verrous décident lesquels s'appliquent :

| terme | exige | nos runs de base |
|---|---|---|
| `NORMAL`, `SNAP` | `normal_grid_path` — `GrowPatch.cpp:2050` sort sans elle | **absent** |
| `DIRECTION` | `direction_fields` | **absents** |
| `SURFACE_SDT` | `sdt_weight` > 0 (`GrowPatch.cpp:1789`) | **0 par défaut** |

⚠⚠ **CORRECTION, une heure plus tard : « il ne reste que `DIST` et `STRAIGHT` » est trop
fort et j'avais écrit ça.** La doc officielle du traceur décrit le processus général comme
*« optimize a surface from a thresholded surface prediction »*, et `thresholdedDistance`
(`GrowPatch.cpp:3078`) **est** une transformée de distance. Il existe donc un terme de
données primaire que je n'ai pas su suivre jusqu'aux résidus (l'interpolateur est construit
lignes 3563/4804/4938, je n'ai pas trouvé où il entre dans l'optimisation).
⚠ **C'est la deuxième fois dans la même journée que je transforme « j'ai trouvé un
interrupteur éteint » en « rien n'est allumé ».** Le motif est à surveiller.

**Ce qui reste vérifié** : trois leviers de données sont **éteints chez nous**, et aucun de
nos 17 `seed.json` ne règle `sdt_weight`. C'est assez pour justifier l'expérience, pas pour
annoncer la cause.
⭐ Cohérent avec la mesure : `essai_ng2`, seul essai poussé avec une grille de normales, est
le moins radial (α = +0,65 contre +0,99 et +1,01).

⚠ **Deux leviers JAMAIS essayés ici** (vérifié sur les 17 `seed.json` de
`data/trace/PHerc0358/essai_*`) : **`sdt_weight`**, et **les fibres horizontales ET
verticales ENSEMBLE** (`normal` seul, `horizontal` seul, `vertical` seul ont été testés,
jamais la paire — alors que c'est la paire qui définit les axes u, v de la feuille).

⚠⚠ **CONTRAINTE MACHINE, MESURÉE, QUI COMMANDE TOUTE CAMPAGNE** : un seul
`vc_render_tifxyz` culmine à **16,7 Gio de RSS** sur une machine qui a **31 Gio**. Deux
rendus ne tiennent donc pas, et le processus qui meurt est **celui qui demande de la
mémoire ensuite**, pas celui qui l'a prise — le 2026-08-21, trois campagnes en parallèle
ont fait tuer une *trace* à la génération 104, sans erreur lisible, à l'autre bout du
pipeline. Le symptôme apparaît chez la victime, jamais chez le coupable.
⭐ Remède structurel plutôt qu'une note : **`src/outils/lancer.sh` REFUSE** un second exemplaire
du même script quand un tourne (`--apres <pid>` pour enchaîner, `LANCER_FORCE=1` pour
passer outre). Sondé : le refus se déclenche.

⚠ Et deux exemplaires du même script sont pires que deux campagnes différentes : ils
partagent leur répertoire de sortie, donc l'un lit les fichiers à moitié écrits de l'autre.
Même famille que « deux écrivains, un fichier de log » — payé le même jour sur
`temoins.sh`, dont la sortie mélangée annonçait **à la fois** « TOUS LES TÉMOINS PASSENT »
et « 1 batterie en échec », avec des NUL entre les deux.

⭐⭐⭐ **RÉSULTAT DU 2026-08-21 — la boucle tourne, et 318 points ne suffisent pas**
([`42`](docs/42_la_boucle_tourne_et_ne_suffit_pas.md)). Le seam `--resume --rewind-gen
--correct` **fonctionne mécaniquement** : la reprise lit le fichier et produit une surface
différente. Mais à conception appariée (même graine, même volume, mêmes paramètres, seuls
les points diffèrent) :

| | aire | croisements | **α** |
|---|---:|---:|---:|
| témoin | 19,82 cm² | **0** | **+0,98** |
| corrigé, 318 points | 20,65 cm² | **11 753** | **+1,03** |

⚠⚠ La correction change la trace et **pas sa nature**. Diagnostic mesuré : **318 points de
passage contre 56 630 points de grille** (0,56 % de la surface) avec un `correction_weight`
qui vaut **1,0 par défaut**, le même ordre que `DIST` qui s'applique partout. Un coup de
pouce local, pas une réorientation.
⭐ Levier suivant, jamais réglé ici : **`correction_weight`** — balayage `POIDS="1 100"`
ajouté à `src/outils/boucle_de_correction.sh`, chaîné derrière le run en cours.

⚠ Et ça retire son dernier appui à **l'hypothèse qui inverse** : une trace passe de 0 à
11 753 croisements sans que α s'améliore. Beaucoup de croisements n'est ni un symptôme de
bon suivi ni son contraire.

## ⭐⭐⭐ RÉSULTAT DU 2026-08-21 — LA CHAÎNE TIENT SIX TOURS

[`43`](docs/43_la_chaine_des_spires.md). Un segment officiel qui converge, puis **six spires
générées** par `mode: gen_neighbor`, chacune source de la suivante, toutes jugées dans les
mêmes fenêtres :

| spire | aire | 31 c | 81 c | **α** | verdict |
|---|---:|---:|---:|---:|---|
| 00 (officiel) | 7,12 cm² | 17,28 | 17,28 | **+0,000** | converge |
| 01 | 6,71 | 90,72 | 90,72 | **+0,000** | converge |
| 02 | 6,35 | 43,20 | 51,84 | +0,190 | converge |
| 03 | 6,14 | 12,96 | 21,60 | +0,532 | intermédiaire |
| 04 | 5,89 | 77,76 | 77,76 | **+0,000** | converge |
| 05 | 5,64 | 129,60 | 172,80 | +0,300 | intermédiaire |
| **06** | 5,39 | 69,12 | **285,12** | **+1,475** | ⚠⚠ **suit la fenêtre** |

⭐⭐⭐ **Première fois de tout ce dépôt qu'une surface que NOUS produisons converge.** Les
dix-sept essais en `mode: seed`, les quatre rembobinages corrigés, les deux semis et les deux
poids sont tous à α ≈ 1 sans exception. Ici six d'affilée ne le sont pas.

⚠ **α dit qu'une feuille est à portée, pas que c'est la bonne** : la spire 01 converge à
90,72 µm, pas à 17. Et α sur deux fenêtres ne discrimine pas à ±0,2 près — ce qui est solide,
c'est l'écart entre 0,00–0,53 et **1,475**.

⭐⭐ **L'érosion est mesurée et borne la chaîne avant la qualité** : la grille rétrécit de
**4,0 % par tour** (162×149 → 141×130, 7,12 → 5,39 cm²). À ce rythme, **la moitié est perdue
en douze tours**. Ce qui manque est une **repousse** entre deux tours — c'est-à-dire ce que
`mode: seed` sait faire et que la chaîne n'utilise pas.

⚠⚠ **LA REPOUSSE : mesurée, et elle échange de la surface contre de la convergence.**
Comparaison appariée sur la spire 01 (même départ, même sens, mêmes fenêtres ; seule la
repousse change) :

| spire 01 | grille | aire | 31 c | 81 c | **α** |
|---|---|---:|---:|---:|---:|
| sans repousse | 157×145 | 6,71 cm² | 90,72 | 90,72 | **+0,000** converge |
| repoussée (20 gén.) | **212×200** | **12,47 cm²** | 86,40 | **129,60** | **+0,422** intermédiaire |

La repousse **rend** la surface (près du double, bien au-delà de ce que l'érosion avait pris)
et **dégrade** la convergence. Le détail dit où : la fenêtre 31 s'améliore un peu, la 81 se
dégrade nettement — c'est **la part regagnée qui tire la mesure**.
⭐ Donc **l'érosion n'est pas un défaut à corriger, c'est le prix de rester sur la feuille** —
au moins avec ce repousseur, qui est le traceur non contraint de `42`.
⚠ Une seule paire pour l'instant ; la campagne continue.
⭐ La suite n'est pas « repousser plus » mais **repousser sous contrainte** : les points de
passage de `41` existent, `correction_weight` existe, et la repousse corrigée est la seule
combinaison des deux qui n'ait pas été essayée.

**Ce qui reste ouvert** : pourquoi la 7ᵉ casse (`neighbor_max_distance`,
`neighbor_min_clearance`) · repousser entre deux tours · le sens `in` · et la validation par
**l'encre**, parce que α ne dit pas qu'on lit du texte.

⭐⭐⭐ **LA SORTIE PAR LE HAUT, trouvée dans la source et jamais lancée ici** :
`mode: "gen_neighbor"` (`vc_grow_seg_from_seed.cpp:625`) prend une surface par `--resume`,
tire un rayon depuis chaque sommet le long de la normale et s'arrête sur la matière suivante
— **il construit la spire voisine**. C'est le « wrap by wrap copy tool » du papier, public.
Et il part d'un segment **officiel qui converge déjà** (α = +0,00), donc il n'a rien à
redresser. `src/outils/spire_suivante.sh` demande : **la convergence survit-elle à
l'enchaînement, et sur combien de spires ?** En file derrière le balayage.

⚠⚠ **PIÈGE DE DIAGNOSTIC PAYÉ LE 2026-08-21, ET IL FABRIQUE UN FAUX RÉSULTAT.**
`ps` affiche un **sous-shell bash avec la ligne de commande de son parent**. Deux lignes
identiques — même script gelé, même environnement — ne sont donc PAS forcément deux
instances : c'est souvent une instance et son sous-shell. Le seul indice était le temps
écoulé (`01:25` contre `00:00`).

J'ai lu ça comme un doublon et j'ai tué le « doublon ». C'était le
`vc_grow_seg_from_seed` de la cellule `corrige_nappe_gen1_poids1`, et le journal a alors
écrit **« AUCUN MAILLAGE — la reprise corrigée ne produit rien »** : un verdict **faux**,
d'apparence normale, sur une cellule qui n'avait simplement pas eu le temps de finir. La
cellule a été supprimée pour être refaite.

⭐ Remède : lire l'**arbre** (`ps -eo pid,ppid,etime,args | awk '$2==<pid>'`) avant de
conclure au doublon, et se rappeler qu'une campagne de ce dépôt lance des sous-shells à
chaque étape. Même famille que `pkill -f` qui matche sa propre ligne de commande.

⚠ Et le pendant structurel, déjà corrigé : **supprimer un artefact n'arrête pas le travail**
— le cache d'un rendu EST le signal d'arrêt du script, donc l'effacer fait tout refaire.
Une décision humaine d'abandon s'écrit dans un fichier que le script LIT
(`<cellule>/ABANDONNE`), jamais déduite d'une absence.

✅ **CAMPAGNES** — les deux sont dépouillées.

La **piste C** (relire `26` au test de convergence) : 3 verdicts sur 17 essais jugeables.

Les **leviers de perte** : campagne relancée et finie le 2026-08-27 → [`26`](docs/26_le_champ_de_direction.md) §9bis.
⭐⭐ **Les deux leviers jamais essayés DÉGRADENT la trace**, d'un facteur 3 à 5 sur la part
des fenêtres dont le pic tombe au tiers central (témoin **32 %**, les quatre variantes 6 à
9 %). `sdt_weight` **ne mord pas** — poids 1 et poids 10 rendent le même écart au
centième, et l'aire ne bouge pas d'une cinquième décimale. La paire de fibres **casse le
maillage** : 8 926 auto-intersections contre **zéro** au témoin, et son gain d'aire de
13 % est le repli lui-même.
⚠⚠ L'α de convergence disait l'inverse (1,332 → 0,901) : c'est un **rapport de deux
nombres censurés**, les quatre variantes ayant leur pic médian au bord de la fenêtre.

Conception appariée : même graine (5842 5839 7386), même volume, mêmes générations, une
seule clé change à la fois — c'est elle qui rend le témoin lisible.

✅ **Fait** : les points ont été donnés à `--resume --rewind-gen --correct`, jugés, et
**relus à travers une fenêtre valide** le 2026-08-27 → [`42`](docs/42_la_boucle_tourne_et_ne_suffit_pas.md) §7.
Le témoin bat toutes les corrections à tous les poids (**22 %** de fenêtres au tiers
central contre 8 à 18 %), et `correction_weight` — que `42` §3 désignait comme « le levier
suivant, jamais réglé » — donne le **même** résultat à 1 et à 100.
⚠⚠ Les α de `42` avaient été mesurés sur des fenêtres de 41 et 161 couches, soit **2,05 et
8,05 pas inter-feuilles** : ils n'étaient pas interprétables. La conclusion survit, sa
preuve a dû être refaite.

⚠⚠ **Piège payé, et il est générique** : `decode` (`src/commun/zarr_depth.py`) rendait
`None` aussi bien pour « ce chunk n'existe pas » que pour « je ne sais pas le décompresser »
— alors que sa propre docstring promettait de les distinguer. `numcodecs` manque dans
`inference/`, donc tous les chunks blosc sont revenus vides et j'ai **mesuré, puis écrit**,
que la graine n'était pas couverte par la prédiction publiée. Elle l'était. Corrigé : ça
**lève** `CodecIndisponible`. ⚠ Les lectures zarr se font depuis **`src/excision/`**.

### ⭐⭐ SUITE DU 2026-08-21 — le pas du rayon, puis OÙ la chaîne se trouve

**1. Le pas du rayon est LE levier, et ma conclusion provisoire était fausse.**
`neighbor_step` 1,0 → 0,5 → 0,25. Chaînes complètes, jugées dans les mêmes fenêtres :

| spire | pas 1,0 | pas 0,5 | **pas 0,25** |
|---|---:|---:|---:|
| 06 | **+1,475** ⚠⚠ | +0,583 | **+0,246** |
| 07 | — | — | **+0,702** ⚠⚠ |
| 08 | — | — | **+1,321** ⚠⚠ |
| | 4/7, 1 casse | 6/7, 0 casse | **6/9, casse au 07** |

> **Halver le pas ne supprime pas la rupture : il la repousse d'un tour.**

⚠⚠ **La leçon de méthode, payée cher** : après trois tours identiques j'ai publié « le pas du
rayon ne change rien ». Faux. **Les premiers tours d'une chaîne ne discriminent pas** — une
chaîne ne se juge qu'au tour où la référence cède. Corollaire : une campagne d'enchaînement
doit aller **jusqu'à la rupture de la référence**, sinon elle mesure le début facile.

**2. ⭐⭐ [`44`](docs/44_ou_la_chaine_se_trouve.md) — où la chaîne se trouve dans le rouleau.**
Nouvel instrument `src/nappe/geometrie_chaine.py` (39 témoins). Mesure sans connaître l'axe
du rouleau : une ligne de grille circonférentielle **tourne**, une ligne axiale est **droite**.

| ce qui est mesuré | valeur | portée |
|---|---|---|
| écart entre nappes | **113 µm** (100 à 138) | ⭐ le seul chiffre qui dise que la chaîne avance d'**une feuille à la fois** |
| érosion de l'aire **utile** | **15,6 % / tour** | ⚠ **corrige** les 4,0 % de `43`, qui portaient sur l'aire de GRILLE |
| sommets valides | **58 % → 23 %** | la grille se **creuse** autant qu'elle rétrécit |
| couverture angulaire | **10 % d'un tour** | il en faudrait **au moins 8** côte à côte pour fermer un tour |
| rayon d'une nappe | **REFUSÉ**, 9/9 | deux estimateurs en désaccord d'un **facteur 2** ; le gondolement (0,5 mm) est 10× l'écart entre nappes, donc un cercle n'est pas un modèle de cette surface |

**3. ⚠⚠ Deux résultats NÉGATIFS qui changent la suite.**

- **La tâche « recoller les spires en un morceau déroulé » était MAL POSÉE.** `gen_neighbor`
  avance radialement, donc les nappes occupent la **même** fenêtre angulaire à 113 µm l'une de
  l'autre. Dans un rouleau déroulé, deux nappes consécutives sont séparées par **une
  circonférence entière** — celle qu'on ne possède pas. Une chaîne radiale est une
  **colonne**. Il faut une chaîne **tangentielle**, qui suit UNE feuille autour du tour, et
  **elle n'a jamais été tentée**. C'est elle qui produirait un morceau de rouleau déroulé.
- **« La rupture est une érosion » est RÉFUTÉE.** `juge_a_un_rendu.py` généralisé à cinq
  candidats plus un **contrôle** : le simple **numéro** de la spire prédit α à ρ = **+0,534**
  (p = 0,001, 4 condamnées signalées sur 4), mieux que l'érosion (+0,415), l'arc (+0,444),
  l'aire (+0,445) et les deux proxys qui coûtent un rendu. Tout ce qui a été mesuré n'est
  qu'un proxy de la **profondeur dans la chaîne**. Contre-exemple qui ferme la porte :
  `spires_repousse/spire03` a **93 %** de sommets valides et α = **+1,461**.

⚠ Trois défauts de l'instrument trouvés par les vraies données, pas par relecture : la
sentinelle d'invalidité vaut **`-1`** et non `(0,0,0)` (mon témoin testait ma propre
hypothèse) ; une spire porte **deux** maillages (`trace/neighbor_out_*` poussé, `plat/`
aplati) ; et l'axe circonférentiel est en **colonnes** pour `spire00`, en **rangées** pour les
autres — le décider une fois rendait des rayons de **312 mètres**.

### Les deux pistes qui restent, par coût croissant

| # | quoi | pourquoi maintenant |
|---|---|---|
| **B** | écrire le producteur de points de correction **depuis la prédiction** (planarité 0,993) plutôt que depuis le volume (plat) | c'est le seul maillon manquant de `39` |
| **C** | relire tous les essais de `26` au test de convergence | ses conclusions ont été prises sur des critères aveugles à la coupe radiale |

⚠ **Une fenêtre de volume de surface tombe le plus souvent dans le vide** (piège nº 27) :
`zarr_vers_couches.py` imprime la couverture et alerte sous 5 %. Trouver la matière avant de
sonder.

## 2. ⚠ CE QUI TOURNE (2026-08-19, soirée)

✅ **`src/campagnes/campagne_pas.sh`** — le balayage de `step_size` sur PHerc0358, deux graines
(`pas/` et `pas_mauvaise_graine/`). Reprenable. C'est **T1f**.
✅ **Rendu** : sur les deux graines, 4 pas sur 5 donnent **zéro** auto-intersection
(`26` §9). `pas_5` des deux campagnes tournait encore au moment d'écrire.

⚠⚠ **Et une mesure lancée dans la foulée a coûté deux explications** :
[`30`](docs/30_le_traceur_est_un_tirage.md). La graine de `24`, rejouée **quatorze fois à
paramètres identiques**, rend **treize traces propres sur quatorze** — quand `24` en avait
une à **240 auto-intersections**, que le maillage archivé porte toujours. La mesure est
fidèle ; **c'est la trace qui n'est pas reproductible**. Ni le diagnostic de `24` (les
champs de direction) ni celui de `25` (le bloc plein) n'expliquent donc les 240.
**Un seul tracé n'est pas une mesure** — et personne dans la littérature ne répète.

> ⚠⚠ **Un bug de ce script a été attrapé pendant qu'il tournait, et il aurait produit un
> faux positif.** `timeout 3600` a tué `pas_5` à la génération 406 sur 480 — la trace
> croissait très bien (1437 mm² au journal) — donc aucun maillage écrit, donc
> `aire_cm2: 0` **et `transverse: 0`**, c'est-à-dire *exactement le résultat qu'on
> espère*, enregistré pour un run qui n'a rien produit. Corrigé : le code de sortie de
> `timeout` est lu, un champ `statut` (ok/timeout/sans_maillage) entre dans le résumé, la
> garde de reprise n'accepte que `ok`, et le budget de temps **suit** la cible de
> générations au lieu d'être constant — un budget constant favorisait mécaniquement les
> grands pas, donc biaisait la grandeur comparée. **`pas_5` est à refaire.**
>
> ⚠ Le script a été **basculé par `mv`**, pas édité en place : bash lit un script par
> offset au fil de l'exécution, et l'instance en cours aurait repris au milieu d'un token.

Toutes les autres campagnes ont rendu : celle des graines (13 rouleaux) et les six
variantes de `direction_fields`. ⚠ VSCode a été fermé pendant les dernières — **aucune
n'a été perdue**, elles avaient toutes fini leurs 118 générations. Vérifier l'**état des
fichiers** avant de conclure qu'un lot est mort : un `ps` vide ne dit rien de ce qui a
été écrit.

```bash
ps -eo etime,pcpu,cmd | grep -E "[z]arr_depth|[c]hamp_correction|[v]c_grow|[v]c_render"
```

⚠ **Juger sur un fichier de résultat, jamais sur une notification**, et **vérifier
l'horodatage d'un log avant d'en citer le verdict** — un log vieux de sept heures a déjà
été lu comme un résultat frais. ⚠ Python **bufferise** : lancer avec `python -u`.

⚠⚠ **`kill $!` sur un `nohup uv run … &` ne tue que le WRAPPER** ; le travailleur est un
petit-fils et il survit, en continuant d'écrire dans le `--out` qu'on croyait abandonné.
Payé **deux fois dans la même heure**. Tuer le petit-fils via `ps -eo pid,ppid,args`.

⚠ Pour libérer la machine : `kill -STOP` les calculs, tuer les `curl` — c'est la **bande
passante** qui fait bégayer un Zoom. Toutes les campagnes sont **reprenables** (un fichier
par segment).

## 2bis. ⭐ La liste de ce qui reste ouvert

**Trois batchs, tous clos** : [`13`](docs/13_batch_epuisement.md) *(fermer ce qui était
ouvert)*, [`18`](docs/18_batch_produire.md) *(produire, pas juger)*,
[`22`](docs/22_batch_repliquer.md) *(un résultat sur un corpus n'est pas un résultat)*.

⭐⭐ **Et le 22 a viré ailleurs qu'où il visait.** Il devait consolider la règle de `19` ;
il l'a **réfutée hors de Scroll 1**, puis a débouché sur autre chose : **VC3D est
construit**, la chaîne officielle est pilotable en ligne de commande, et
[`24`](docs/24_premiere_trace_rouleau_du_prix.md) a tracé un **rouleau du Grand Prize**.

⭐⭐ **Et le lot du 19 août après-midi a fermé T1**, avec deux corrections que la mesure a
imposées : [`25`](docs/25_une_graine_choisie_sur_la_planeite.md). Le critère de graine passe
sur la **planéité locale**, la campagne appariée sur **13 rouleaux du prix** donne
p = 0,0225 sur l'aire — et **zéro auto-intersection des deux côtés**, donc le « 240 → 0 »
de `24` est l'accident d'un seul rouleau. Le vrai coupable de `24` est ailleurs et il est
nommé : sa graine était dans un bloc **entièrement plein** (occupation 1,000), donc sans
géométrie à suivre.

> **Le prochain lot n'est plus un batch de mesure.** Il est décrit au §7.

⭐⭐ **Et depuis le 2026-08-19, tout ce qui reste est consolidé en un seul endroit :**
[`29`](docs/29_ce_qui_reste.md). Les 34 documents ont été lus **intégralement** — onze
lecteurs, ligne à ligne, pas de `grep` — et les **525** énoncés de travail ouvert relevés
y sont repliés en une trentaine d'entrées, chacune sourcée en `fichier:ligne`.

> ⭐⭐⭐ **Le reste le plus profond n'est pas au bout de la chaîne, il est dessous** :
> *« une surface propre donne un meilleur texte » est une affirmation sur le pipeline, et
> **elle n'est pas prouvée**.* (`03`:133-137). Tout l'appareil d'instruments de ce dépôt
> la suppose — et `28` montre que **personne dans le domaine ne l'a mesurée** non plus.

## 2ter. ⭐⭐ La littérature primaire, lue en entier le 2026-08-19

`06` §0 notait **deux** papiers « à lire ». Il y en avait **trois**, et le troisième est
le plus important. Tout est dans [`27`](docs/27_ce_que_la_litterature_dit.md) ; voici ce
qu'un repreneur doit savoir avant d'ouvrir quoi que ce soit d'autre.

**Un rouleau scellé a été entièrement déroulé et lu** — PHerc. 1667, arXiv 2606.29085,
27 juin 2026, 27 auteurs. 31 spires, 1231 cm², 22 colonnes, huit papyrologues.

**Et le problème reste ouvert**, dit par la même équipe un mois plus tard
(`/2026_open_problems`, 10 juillet 2026) : *« No method yet traces a complete, correct
surface through a scroll automatically. »*

⭐⭐ **Le chiffre qui réconcilie les deux, et qui cadre tout le reste** : *« ~25 hours per
wrap of manual annotation »*. **31 spires ≈ 775 heures d'humain.** Le Grand Prize 2027 en
tolère **huit**. Facteur **~100**.

⚠⚠ **Et le fait qui justifie ce dépôt** : dans cet article, **« sheet switches »
n'apparaît qu'UNE fois**, dans la liste des goulots non résolus. Le seul rempart contre
une trace fautive est *« regions **judged** geometrically consistent with a single
sheet »* — un masque d'approbation posé à la main. **Aucun taux d'erreur de traçage n'est
publié**, ni avant ni après correction. La grandeur que nos instruments produisent
n'existe nulle part dans la littérature.

⭐ La page officielle nomme la case en toutes lettres, deux fois :
- tableau des goulots, ligne *Sheet switches* → ce qui aiderait : *« Stronger local
  continuity constraints and **conservative failure detection** »* ;
- appel à contribution nº 2 : *« help with **automatic topology repair** — building tools
  that catch mesh-tracing errors like holes, mergers, and sheet switches **without a human
  checking every traced piece of surface by hand** »*.

**Trois corrections que cette lecture a imposées dans nos documents** :

| doc | ce qui était écrit | ce qui est mesuré |
|---|---|---|
| `27` §1 | cible de **4 µm** de résolution latérale, facteur 2,2 | **~1 µm** (*« on the order of 1 µm or finer »*), facteur **8,6–9,4**. Le 4 µm n'est **nulle part** dans le papier — écrit depuis le résumé |
| `00` §2, `01` §3 | le spiral fitting est **immunisé** au saut de spire *par construction* | Henderson mesure **WJF = 3,20 %** et écrit *« the surface sometimes wanders between two true windings »*. La garantie est **topologique**, pas sémantique |
| `00` §9.4 | **trois** instruments condamnent la trace de `24` | **deux** — la jambe « profondeur » a été retirée (`24` §2, `25` §5) et ce paragraphe la propageait |

⚠ **La leçon de méthode** : la première version de `27` était écrite depuis les
**résumés**. Elle portait un chiffre faux, une paraphrase entre guillemets, et reprenait
à son compte une affirmation qu'un des papiers réfute avec un nombre. *Un résumé dit ce
qu'un papier revendique, pas ce qu'il mesure.*

⭐ **Reste nommé** : le quatrième article, *EduceLab-Scrolls* (arXiv 2304.02084, 2023),
n'est **pas lu**. C'est le jeu de données des scans à 7,91 µm et la base de [P2].

## 3. Le projet

`~/LplVesuvius` — Vesuvius Challenge vu depuis Laplace. Contexte non versionné dans
`PRIVE.md` (gitignoré). **Budget disque** : 100 Go, ~52 Go utilisés.

⚠ Aucun remote git configuré. Ne jamais pousser.

### Ordre de lecture

| doc | contenu |
|---|---|
| `00` | point d'entrée : la chaîne, les acteurs, les prix |
| `01`–`05` | le goulot, l'inventaire, la reproduction `windcheck`, l'excision |
| **`06`** | **le carnet de mesures** — faites, en attente, écartées |
| `07` | la réparation ne déplace pas le défaut |
| `08`, `10` | ⭐ la passe d'encre : **AUC 0,925** sur un segment entier |
| `09` | juge par modèle : 3 juges mécaniques en échec, 1 calibré qui marche |
| **`11`** | ⭐ **onde radiale, dépliage polaire, fusions localisées en 3D, la dérive** |
| **`12`** | ⭐⭐ **la profondeur de surface : qualité de tracé SANS vérité terrain** — lire le §10 d'abord, l'instrument a été corrigé deux fois |
| **`13`** | **la liste du batch d'épuisement**, cochée au fur et à mesure |
| `14` | ⭐ la direction des fibres — ❌ **réfutée**, le signe s'inverse quand n monte |
| `16` | ⭐ quel rouleau du prix attaquer — `PHerc0358`, désigné par la mesure |
| `17` | ❌ le saut de spire par la phase — **échec définitif** (§10) |
| **`18`** | ✅ batch **clos** : produire, pas juger |
| **`15`** | ⭐ **ce qui est soumissionnable**, trié contre les critères écrits du concours |
| **`19`** | ⭐⭐ **la première règle qui CHANGE une décision** — p = 0,0005 contre 2000 permutations |
| **`20`** | ⭐⭐ **le champ de correction** : l'erreur d'une trace est structurée, et **translater ne la répare pas** |
| **`21`** | **le brouillon de la soumission**, résultats négatifs compris. ⚠ Ses chiffres sont gardés par `verifier_chiffres.py`, lancé dans `src/outils/temoins.sh` |
| `22` | le batch « répliquer » — clos, et il a réfuté ce qu'il devait consolider |
| `23` | ⭐ **l'inventaire des 13 rouleaux du prix** — 10 n'ont AUCUN segment |
| **`24`** | ⭐⭐ **la première trace d'un rouleau du prix**, condamnée par nos instruments avant le rendu. ⚠ Son §2 est **corrigé** : le verdict tient sur deux instruments, pas trois |
| **`25`** | ⭐⭐ **la graine choisie sur la planéité** — et la réplication sur 12 rouleaux qui a corrigé la revendication deux fois |
| **`26`** | ⭐⭐ **ce qui gouverne la trajectoire du traceur** — et les deux mécanismes qui ne la gouvernent pas, contrats dérivés et encodage mesuré. ⚠ Son §4 est **corrigé** : douze poids de perte, pas dix, et deux des noms annoncés n'existaient pas |
| **`27`** | ⭐⭐ **les trois articles primaires, lus en entier** — un rouleau lu de bout en bout, ~25 h d'humain par spire, et la garantie du spiral fitting qui est topologique et non sémantique |
| **`28`** | ⭐⭐ **le paysage du contrôle qualité** — ce qui existe, ce qui a été refusé, et la limite mesurée de la détection par la géométrie seule |
| **`29`** | ⭐ **le registre consolidé de tout ce qui reste** — 525 énoncés repliés, sourcés en `fichier:ligne`. **Commencer par là pour choisir un lot** |
| **`30`** | ⚠⚠ **le traceur est un TIRAGE** — 13 traces propres sur 14 à paramètres identiques, quand `24` en avait une à 240. Coûte deux explications causales, rapporte un levier |
| **`31`** | ⭐⭐ **la roadmap** — le Grand Prize est un prix d'**algorithmique de géométrie**, pas de lecture, et son critère d'acceptation est une **image Docker qu'ils lancent**. Ce que le Laplace Project a déjà résolu et qui transfère |
| **`32`** | ⭐ **EduceLab-Scrolls, le papier fondateur** — ce qu'il a posé, et les contrôles négatifs qu'il n'a pas faits (dont un témoin parfait que son pipeline **jette**) |

## 4. L'outillage, et comment le relancer

```bash
./src/outils/temoins.sh                      # toutes les batteries hors ligne ; compte imprime
                                             # par le script, et ecrit dans docs/mesures/temoins.json
./src/outils/dossier_soumission.sh           # le dossier qui PART : texte + figures + journal
                                        # ⚠ la liste des figures est DÉRIVÉE du texte, et le
                                        # script refuse un dossier incomplet (sonde faite)
./src/outils/mirror_site.sh                  # miroir + contrôle de couverture
./src/outils/fetch_layers.sh <url> <dest> <largeur> <de> <a>   # couches, reprenable
uv run python src/outils/ppm_to_tifxyz.py <in.ppm> <out.tifxyz>  # .ppm de VC -> tifxyz
./src/outils/survey_fusions.sh <out> <bandes> <par> <pas>      # fusions, niveau 2
./src/outils/bandes_niveau0.sh                                 # bandes niveau 0, hors site
./src/outils/fetch_traces.py <index.json> <corpus> <dest>      # traces tifxyz, SANS aws
./src/outils/lister_volumes_surface.sh <rouleau> <sortie>      # qui publie un volume Zarr
./src/outils/fetch_cartes_encre.sh <rouleau> <dest>            # cartes d'encre PUBLIEES
./src/outils/reprendre.sh                                      # degeler apres un kill -STOP
./src/campagnes/campagne_champ.sh <rouleau> <motif> <voxel_um>    # champ de correction, REPRENABLE
./src/campagnes/campagne_dense.sh <rouleau> <motif> <dest>        # part de matiere, 392 points
./src/outils/etat_rouleaux_prix.sh                             # ⭐ l'inventaire des 13

cd experiments   # geometrie
uv run python src/excision/radial.py {centre|compter|profil|deplier|axe} …
uv run python src/excision/fusions.py {controle|ecarts-controle|densite|ecarts} …
uv run python src/excision/fusion_scan.py …               # persistance en z
uv run python src/excision/track_z.py <scans.json> …      # appariement PREDICTIF
uv run python src/excision/baseline_sweep.py <traces> <out.jsonl>   # references locales
uv run python src/excision/variant_correlate.py <sweep> <index.json>
uv run python src/excision/pyramid.py <volume>            # separabilite par niveau
uv run python src/excision/sensibilite_centre.py <nom> <volume>    # l'invariant tient-il ?
uv run python src/excision/shape.py {degradation|ellipticite} <volume>
uv run python -m excision.proximity <mesh.tifxyz> --json

cd inference_xpu # encre
uv run python src/xpu/infer_ink.py <layers> --model … --device xpu --out out.npy
uv run python ../analysis/src/{evaluate_segment,render_segment,structure}.py …
uv run python src/encre/judge_api.py --list-models
uv run python src/encre/judge_api.py <pred.npy> --bands-only   # sans cle
uv run python src/volume/depth_profile.py <couches…> --grid     # qualite de trace
uv run python src/commun/zarr_depth.py <cle .zarr> --courbe --fils 16   # ⭐ x8,35
uv run python src/nappe/fiber_orientation.py <cle .zarr>       # ⭐ fibres
uv run python src/commun/croiser_instruments.py <index.json> <mesures.json>
uv run python src/nappe/champ_correction.py <cle .zarr> --voxel-um 2.4  # ⭐⭐ REPARABLE ?
uv run python src/nappe/champ_correction.py <cle .zarr> --voxel-um 2.4 \
    --fenetres docs/champ_X/fenetres      # ⭐⭐ le champ FENETRE PAR FENETRE (R2)
uv run python src/depot/chemins_des_scripts.py --verifier  # aucun script n'ecrit dehors
uv run python src/encre/croiser_encre.py <profondeur.json> <cartes/>    # ⭐⭐ la DECISION
uv run python src/tables/table_champ.py <champs/> --encre <rapport.json>
uv run python src/nappe/resolution_phase.py <saut_spire/>
uv run python src/commun/trouver_graine.py <prediction .zarr>    # ⭐ graine A DISTANCE
uv run python src/volume/regarder_rendu.py <render/> --png-dir …  # apercus + stats
uv run python src/encre/tester_prediction_50um.py <rapport.json>
uv run python src/nappe/robustesse_material.py <A> <B>
uv run python src/depot/verifier_chiffres.py <docs…>            # fraicheur
uv run python src/volume/compare_maps.py <a.npy> <b.npy>
uv run python src/encre/proximity_vs_ink.py <mesh> <pred> <labels>
```

### ⭐⭐ VC3D — la chaîne de production, construite le 2026-08-19

> ⚠⚠ **« VC3D ne se lance plus » est faux, et la façon de s'en apercevoir coûte une
> demi-heure** *(mesuré le 2026-08-26)*. Deux choses trompent, dans cet ordre :
>
> 1. **`VC3D --help` et `VC3D -h` font un SEGFAULT** (code 139) et crachent un « CRASH
>    REPORT » de trente lignes. C'est le premier réflexe quand quelque chose cloche, donc
>    c'est ce qu'on voit. `--version` répond normalement, et **lancé sans argument le GUI
>    démarre** : vérifié, 990 Mo résidents, stable.
> 2. Au démarrage il écrit `Window state metadata mismatch; skipping restore`. **Ce n'est
>    pas une panne, c'est le bon comportement** : `~/.VC3D/VC3D.ini` porte
>    `screen_signature=xcb|1|rdp-0:1920x1200+0+0@1.00`, et VC3D refuse de restaurer une
>    fenêtre sur un écran qui n'est plus celui-là plutôt que de la poser hors champ.
>
> `./src/outils/lancer_vc3d.sh` lance proprement, refuse avant de toucher au binaire quand
> il n'y a pas d'affichage, et `--repartir-de-zero` efface la géométrie mémorisée.

**44 outils en ligne de commande** *(compté le 2026-08-19 : `ls /usr/local/bin/vc_* | wc -l`)* sous `/usr/local/bin/vc_*`, plus le GUI `VC3D`.
Construits depuis `data/repos/villa/volume-cartographer/build_from_src_debian.sh`
(⚠ demande `sudo`, **31 paquets** dans sa liste principale — mesuré le 2026-08-19 sur `volume-cartographer/build_from_src_debian.sh`, qui fait par ailleurs **trois** appels `apt` distincts ; « 17 » était faux).

```bash
vc_grow_seg_from_seed -v <zarr|URL> -t <dir> -p seed.json -s <x> <y> <z>
vc_tifxyz_selfcross --surface <tifxyz> -o rapport.json    # auto-intersections
vc_flatten -i <tifxyz> -o <tifxyz_flat>
vc_render_tifxyz -v <cache> --remote-url <URL> --scale 1 -g 0 \
    -s <flat> --tif-output <dir> -n 21 --auto-crop
```

⭐ **`-v` accepte `https://` pour le traçage** : le volume de 893 Go n'est **jamais**
téléchargé. ⚠ Mais `vc_render_tifxyz` veut un chemin **local** en `-v` — c'est
`--remote-url` qui fait le streaming, et `-v` désigne alors le **cache**.

⚠⚠ **Trois pièges silencieux, chacun ressemblant à un succès** :
1. **`voxelsize` vaut 0 par défaut** dans `seed.json` → l'aire en cm² est nulle *par
   construction* et toute surface est rejetée (« area 0 below min_area_cm ») ;
2. **`--segment-name` fait écrire DANS `-t`** — il tente de remplacer le répertoire
   courant par lui-même ;
3. **`[tif] all slices exist, skipping`** saute par-dessus les fichiers **tronqués** d'un
   run tué. Effacer le répertoire de sortie avant de relancer.

### Matériel

| voie | verdict |
|---|---|
| **iGPU Arc via `torch 2.9.1+xpu`** | ✅ ×4,5, sortie identique au CPU à 4,9e-6 |
| NPU | ❌ non exposé à WSL2 |
| OpenVINO | ❌ ne convertit pas ce modèle |

⚠ `sudo apt install intel-opencl-icd libze-intel-gpu1 libze1`. Le nom
`intel-level-zero-gpu` **n'existe pas** sous Ubuntu 26.04 et apt annule **toute** la
transaction sur un nom inconnu.

## 5. Les résultats acquis

### Géométrie — le travail

1. **Onde radiale** : **176 spires** (max sur 20 tranches), rayon 25,1 mm →
   **~13,9 m** de papyrus. ⚠ Borne **inférieure** : deux feuilles fondues comptent
   pour une. Longueur **axiale** du rouleau : 164 mm ; diamètre 48 mm.
2. **Invariant fort** : rayon / feuilles = **142,8 µm, cv 1,8 %** sur toute la hauteur,
   alors que chaque grandeur varie de 4-5 %. Profil en **U** (25,1 → 21,3 → 24,3 mm).
3. **Le rouleau est écrasé** : rapport d'axes **1,26 à 1,57**, le plus au milieu.
   ⚠ Le périmètre perd quand même 9 % — écrasement **et** perte, aucune écartée.
4. **Fusions localisées en 3D** : 4 candidats vers 17 mm, persistants à **p = 0,0001**
   (coupes à 0,8 mm), et **18 %** de colocation sur le rouleau entier par bandes.
   Le défaut **migre** : +2,4 mm de rayon et +38° sur 2,4 mm de hauteur.
   ⚠ L'inclinaison de l'axe est **écartée** — elle joue en sens opposé (−0,47 mm).
5. **Le niveau 2 de la pyramide suffit** : **89 %** des murs pour **33 Gio au lieu de
   2100**. Falaise entre les niveaux 2 et 3. ⚠ C'est un **crible** : les deux niveaux
   ne trouvent pas les mêmes sites (fond 10,3 % contre 6,6 %), donc tout candidat se
   confirme au niveau 0.
6. **Théorie du dommage de l'auteur** : à moitié. Cœur dégradé (−20 %), extérieur à
   peine (−5 à 8 %). **Pas un U.** ⚠ Bonne nouvelle : ce qu'on a perdu du **début**
   des textes est moindre que craint.

7. ⭐ **Le défaut DÉRIVE, et le crible ne peut pas le voir** (`11` §11). Appariement
    **prédictif** — même tolérance, seul le *centre* de la fenêtre devient une
    prédiction. Le site du §7 forme une piste de **5 coupes traversant 4,75 mm de
    rayon** (dérive **1,50 mm/mm**) contre 3 coupes / 1,42 mm à fenêtre fixe,
    **p = 0,0010** (0,005 après Bonferroni). ⚠⚠ Le niveau 2 est **aveugle** à ce site :
    même plage de z, niveau 0 à 77–88 % du tour, niveau 2 rien entre 74 % et 88 %. Les
    **18 %** de colocation du balayage portent sur une **autre population**.
8. ⚠ **La migration n'est PAS la règle.** Une seconde bande au niveau 0 (z 3188→3988)
    a ses sites **stationnaires** : piste la plus longue plate à 0,47 mm, p = 0,74. Le
    site à z ≈ 7000 est particulier.
9. ⭐⭐ **Un chunk Zarr = une colonne de profondeur entière, pour 1,78 Mo et 1,03 s.**
   Les volumes de surface sont publiés en OME-Zarr non compressé, chunks
   `[109, 128, 128]`. Une campagne qui demandait **32 Go par segment** en demande
   quelques mégaoctets. Conséquences : **81 segments** de Scroll 1 avec volume de
   surface, **80 avec une carte d'encre publiée** (récupérées — le résultat sans lancer
   43 min d'inférence), **3 campagnes** de scan (45,5 / 2,4 / 1,13 µm) dont 37 segments
   les ont toutes, et **aucune troncature** du profil. Ça débloque `12` §5 *et* `06` §3.6.

10. ⭐⭐ **La profondeur de surface** (`12`) — une mesure de **qualité de tracé** qui ne
   demande **ni vérité terrain, ni modèle, ni juge**, et se calcule **avant** toute
   inférence. La grandeur est l'**écart entre le pic d'intensité et la surface tracée**,
   en µm : `20231022170901` **24 µm**, `20230909121925` (AUC 0,925) **32 µm**,
   Scroll 4 **63 µm** (p90 **134**). ⚠ Ces trois chiffres sont des **bornes
   inférieures** — la fenêtre 15–40 tronque, et 37 % des fenêtres de Scroll 4 y sont
   écrêtées. Sur la pile complète de Scroll 4, **61 %** des fenêtres ont leur pic **à un
   bord** : la feuille est hors du volume de surface.
   ⚠⚠ **L'instrument a été corrigé DEUX fois le même jour** (`12` §10), et aucun défaut
   n'a été trouvé en relisant : (a) le **contraste** ne localise pas la matière — sur un
   volume à 2,4 µm sa courbe est un **U**, maximal aux deux bords et minimal dans la
   feuille, parce qu'il suit les interfaces et le bruit ; l'**intensité** localise ;
   (b) « tiers central » se rapportait à la **fenêtre lue**, qui n'est pas centrée sur
   la couche tracée — d'où l'écart en µm.
   ⚠ **Correction d'une de mes conclusions du même jour** : j'avais annoncé « l'écart
   vaut une épaisseur de feuille, donc saut de spire » en important le pas de PHerc0172
   vers PHerc1667. Piège nº 6. La pile complète le dément : les deux blocs sont séparés
   de plus de 64 voxels.

### Encre — l'instrument

11. **AUC 0,925** sur 44,7 M de pixels d'un segment entier, contrôle mélangé à **0,500**.
   9,2 cm de grec lisible. ⚠ Orientation de lecture = **rotation 270°**.
12. **Juge de langue calibré** : **15/16, zéro fabrication**, lisibilité séparant sans
   chevauchement le vierge (0–1) du texte (3–6). Protocole : `data/juge/PROTOCOLE.md`.

13. ⚠⚠ **Rien de lisible sur Scroll 4, et la cause est EN AMONT du modèle** (`09` §12,
   `12`). Deux passes complètes (couches 15–40 puis 0–25, ~43 min chacune). Le juge
   calibré : lisibilité **1–3** sur la première, **refus de tous les panneaux** sur la
   seconde, quand le calibrage sépare vierge **0–1** de texte **3–6**. Recentrer les
   couches n'a rien sauvé (les deux cartes : rho **+0,700**, **88,7 %** d'accord).
   ⚠⚠ Et ça ne pouvait pas marcher : sur **61 %** du segment le cœur de matière est
   **hors des 65 couches**. On ne détecte pas d'encre sur une surface que le volume de
   surface ne contient pas. ⚠ Limite du protocole mesurée au passage : **la lecture
   d'un panneau dépend de son voisin** (même image, 1 puis 2 puis 0 glyphes, à
   température zéro).

### 2026-08-19 — de juger à décider

17. ⭐⭐ **La première règle qui change une décision** (`19`). Écarter les **20 %** de
   segments dont le volume de surface porte le moins de matière (`avec_matiere`) fait
   monter le contraste d'encre médian du corpus de **+0,381**, contre **2000
   permutations** de même effectif : **p = 0,0005**. Cible = les **cartes d'encre
   publiées**, donc la sortie d'un **autre** pipeline. Coût : **36 requêtes** par segment,
   **avant** toute inférence.
   ⭐ Ce qui la défend est sa **forme** : un plateau contigu **15–25 %**, encadré par 5 %
   qui ne fait rien (p = 0,054) et 30 % qui se dégrade. Un réglage sur-ajusté ferait un
   **pic** — même critère que le seuil d'un tiers de `07` §8.
   ⚠⚠ Le **confond de taille était réel** (emprise ↔ écart +0,384, emprise ↔ encre
   +0,463) et la corrélation **partielle le RENFORCE** au lieu de le dissoudre
   (−0,315 → **−0,382**, p = 0,0005). C'est le contraire d'un effet de taille.
   ⚠ Confond non levé, et il faut le dire : une carte vide peut vouloir dire « la trace a
   raté » **ou** « ce papyrus est vierge ». C'est un **tri de corpus**, pas un diagnostic.
   ⚠⚠ **ET LA RÉPLICATION ÉCHOUE SUR SCROLL 5** (`19` §11) : rho **−0,217** (p = 0,12),
   décision p = 0,84. Deux mesures qualifient ce zéro. **(a)** La cible y est plate —
   contraste sur un facteur 1,25 contre 5,1 sur Scroll 1, étendue relative **4,6× plus
   petite** — donc le test est **non concluant**, pas réfutant. **(b)** Et sur Scroll 1 la
   règle sépare une **CLASSE**, pas un gradient : retirer les 16 segments sous un contraste
   de 3,0 fait tomber rho de **+0,539 à +0,190 (p = 0,13, ns)**. ⚠⚠ **Et le test apparié a réfuté l'explication (a)** (`19` §12) : PHerc0139, à la **même**
   résolution que Scroll 1 et avec une étendue **plus grande** (1,628 contre 1,008), rend
   quand même **−0,229**. L'effet de plancher couvrait un corpus sur trois. **La règle est
   une propriété du corpus publié de Scroll 1, pas du problème** — elle y reste solide,
   c'est sa PORTÉE qui tombe.
   ⭐ **Robustesse vérifiée** (`19` §10) : re-mesuré à **5,4× la densité de sondage**
   (72 → 392 fenêtres), l'accord des classements vaut **+0,841** (témoin 0,223) et le
   **plateau 15–25 % survit intact**. ⚠⚠ Un premier contrôle avait conclu l'inverse
   (+0,280) — il comparait deux **grandeurs différentes**, et j'ai passé une heure à
   affaiblir un résultat juste. **La prudence n'est pas une méthode.**

18. ⭐⭐ **Le champ de correction** (`20`) : l'erreur d'une trace est **structurée** —
   **150 segments sur 152**, sur **trois** rouleaux, battent leur propre témoin de mélange
   (80/80, 19/19, 51/53).
   ⭐⭐ Et le chiffre qui décide de la production : une **translation** du maillage
   n'enlèverait que **21,7 / 35,3 / 28,6 %** de l'erreur (Scroll 1 / 4 / 5). Le bon remède
   est un **gauchissement**, pas une translation.
   ⚠ Un **seul** segment de Scroll 5 rendait 0,67 et j'avais restreint la conclusion à
   deux rouleaux ; les 53 rendent 28,6 %. **Une contre-indication vue sur un point a
   fondu** — la règle « n = 1 n'est pas un résultat » vaut dans les deux sens.
   ⚠ Saut de feuille : **1/80** sur Scroll 1 et **0/53** sur Scroll 5, chacun contre le pas
   mesuré **sur ce rouleau-là**.
   ⚠ Le champ **ne prédit pas** l'encre (rho −0,023 à n = 80, où 0,31 est détectable)
   mais **prédit les croisements** (résiduel **+0,428**, p = 0,0012, n = 54) : un défaut
   de la **TRACE**, pas du **RÉSULTAT** — mesuré des deux côtés.
   ⚠⚠ **Piège nº 6 commis puis attrapé dans la même séance** : j'ai appliqué le pas de
   PHerc0172 (142,8 µm) à des segments de PHercParis4 (**172,8 µm** mesuré), ce qui
   gonflait le compte de sauts de feuille d'un facteur 4. `--pas-um` **n'a plus de
   défaut** et le compte n'est pas rendu sans lui.

19. ⭐ **L'échelle est réelle, pas promise** : `--fils` sur le lecteur Zarr donne **×8,35**
   mesuré (21,80 s → 2,61 s), sortie **bit pour bit identique**. Le modèle de coût
   divisait par 16 — corrigé : les **800 rouleaux de la villa** se jugent en **0,9 h**,
   pas 0,5 h. Un modèle de coût qui se flatte n'est pas un modèle de coût.

19bis. ⚠⚠ **La prédiction des 50 µm de `12` est testée, et elle se scinde en trois**
   (`12` §13). Le **sens tient** (4,93 contre 5,91, p = 0,017). Le **seuil tombe** : au
   balayage, 60 µm est pire que 50 **et** que 70 — une courbe qui monte, redescend et
   remonte n'a pas de point de coupure, c'est le contraire du plateau de `07` §8. Et la
   **forme forte est réfutée** : l'écart médian du corpus vaut **67,2 µm**, donc le seuil
   condamnerait 64 segments sur 80 qui portent visiblement de l'encre, et **8 %** seulement
   de ceux qui le dépassent tombent dans le premier décile contre 10 % attendus au hasard.

19ter. ✅ **L'invariant tient à un centre faux** (`11` §12) : déplacer le centre de
   **3,16 mm** — 22 écarts inter-feuilles — bouge l'invariant de **1,75 %** au maximum,
   soit **sous** le cv de 1,8 %. `06` §2.3 est donc clos **sans ombilic**, lequel n'est de
   toute façon pas publié (zéro occurrence sur 4 corpus).
   ⚠⚠ **Deux artefacts traversés avant d'y arriver, et ils se ressemblent** : au niveau 2
   les seuils de comptage trouvaient 42 feuilles au lieu de 176 (piège nº 1) ; à **3
   tranches** le bruit d'échantillonnage produisait **5,65 %** et une « marche » nette dès
   la plus petite perturbation, avec une explication toute prête. À 6 tranches, plus rien.
   **Un effet réel ne fond pas quand on l'échantillonne mieux.**

20. ❌ **Le saut de spire par la phase est mort définitivement** (`17` §10). Le volume
   `cos` n'est publié qu'aux niveaux **3, 4, 5** — le niveau 3 EST le plus fin, donc
   « refaire au niveau 0 » n'avait pas d'objet. Et la quantification n'écrase rien :
   marche médiane **12,2 / 255**, **0 trace sur 38** à médiane nulle.

### 2026-08-19 (fin) — de juger à produire

21. ⚠⚠ **LA RÈGLE DE `19` NE RÉPLIQUE PAS** (`19` §11–§12). Testée sur **110 segments** de
   trois autres rouleaux, mêmes outils, même définition :

   | corpus | n | voxel | étendue de la cible | rho |
   |---|---:|---:|---:|---:|
   | **Scroll 1** | 80 | 2,4 µm | 1,008 | **+0,539** |
   | **PHerc0139** | 38 | **2,399 µm** | **1,628** | **−0,229** |
   | PHerc1667 | 19 | 2,399 µm | 0,720 | +0,425 |
   | PHerc0172 | 53 | 7,91 µm | 0,220 | −0,217 |

   ⚠ Ma première explication (effet de plancher) couvrait **un corpus sur trois** :
   PHerc0139 est à la même résolution que Scroll 1, a une étendue **plus grande**, et rend
   le signe opposé. **La règle est une propriété du corpus publié de Scroll 1.**
   ⚠⚠ Et sur Scroll 1 même, elle sépare une **CLASSE** et non un gradient : retirer les 16
   segments quasi vierges fait tomber rho de **+0,539 à +0,190 (p = 0,13, ns)**.
   ⭐ La revendication corrigée est **meilleure** : « je repère une classe d'échecs avant
   que vous payiez l'inférence » est le goulot que le concours nomme mot pour mot.

22. ⭐⭐ **UNE TRACE PRODUITE SUR UN ROULEAU DU GRAND PRIZE** (`24`). `PHerc0358`, l'un des
   **dix** des treize sans aucun segment publié : **8,48 cm²** en **13,9 s** de calcul, le
   volume de 893 Go n'étant jamais téléchargé. Puis aplati et rendu, 29,4 × 29,2 mm.
   ⚠ **La trace est mauvaise** — elle coupe à travers les spires. Ce qui compte est
   **comment on le sait** : trois mesures indépendantes, **deux avant l'image**.
   240 auto-intersections à pénétration 200 µm (> 1 écart inter-feuilles) ; **64 %** des
   fenêtres piquant au bord de la pile, distribution **bimodale** (15 à la couche 0, 9 à
   la 20, une au milieu) — la signature d'une surface posée **entre** deux feuilles.
   ⭐ **C'est la validation qui manquait** : les instruments jugeaient le travail des
   autres ; ils viennent de condamner le nôtre, en 0,05 s, avant le rendu.
   ⚠⚠ **Cause FAUSSE, mesurée trois fois négative par `26` avec son contrôle positif.**
   La vraie cause de `24` est une graine dans un bloc entièrement plein (occupation
   1,000, tenseur nul), cf `25`. Texte d'origine, gardé pour la trace du raisonnement :
   « cause identifiée : `direction_fields` absent, donc **aucune information
   d'orientation** — et une surface qui coupe les spires satisfait la prédiction seuillée
   autant qu'une qui en suit une.

23. ⭐ **L'inventaire des treize** (`23`) : **dix rouleaux n'ont AUCUN segment**, et les
   treize publient tous volume + prédiction de surface + `normal-grids` + `lasagna`.
   `PHerc1447` en a 16, `PHerc0800` 6, `PHerc1203` 1. Et `PHerc1447` est le **seul** à
   publier des volumes de surface (4, à 8,64 µm) : nos instruments y trouvent
   immédiatement un segment **hors du papyrus** (9 % de matière contre 51–59 %, 17,4 % au
   bord, écart +86 µm).

24. ⚠ **La migration est l'exception** (`11` §13) : 2 bandes sur 6, Fisher p = 0,079 — et
   le **témoin positif** (bande E, autour du site connu) ressort à p = 0,0285 avec une
   dérive de 1,20 mm/mm. La méthode retrouve la migration là où elle existe, donc les
   quatre bandes muettes sont de **vrais** négatifs.

25. ⚠⚠ **La prédiction des 50 µm est testée et scindée en trois** (`12` §13) : le **sens**
   tient (4,93 contre 5,91, p = 0,017), le **seuil** tombe (60 µm est pire que 50 *et* que
   70 — une courbe qui monte, redescend et remonte n'a pas de point de coupure), et la
   **forme forte est réfutée** (l'écart médian du corpus vaut 67,2 µm, donc le seuil
   condamnerait 64 segments sur 80 qui portent visiblement de l'encre).

### La jonction, et le domaine de définition

14. ⚠⚠ **La métrique de proximité a un DOMAINE DE DÉFINITION** (`07` §7). Elle exige une
   trace qui **repasse au-dessus d'elle-même** : sur les 53 traces de Scroll 5, **44
   rendent zéro cellule**, et la coupure est exactement à **un tour** (mesurées
   2,99–9,07, écartées 0,50–**1,00**). Ce n'est pas « moins bon sur un second rouleau »,
   c'est **inapplicable** à cette population. ⚠ Les 9 mesurables sont neuf morceaux du
   **même** segment : n = 1. ⭐ Le vrai second rouleau est PHerc0139 / PHerc1667 /
   PHerc0814, majoritairement au-dessus d'un tour — traces récupérées.
15. ✅ **Le seuil d'un tiers de `07` : ni arbitraire, ni supprimable** (`07` §8). Aucune
   grandeur sans seuil ne l'égale (**+0,340** et **−0,512** contre **+0,769**) — le
   signal est dans la queue extrême. Ce qui le défend est un **plateau** : rho 0,759 à
   0,779 de 0,15 à 0,40, un facteur **2,7**, puis effondrement. Un réglage sur-ajusté
   ferait un **pic**.

16. ⚠⚠ **La proximité géométrique ne prédit PAS la lisibilité.** rho **+0,019** à
   n = 89 tuiles (contrôle plat), et à ce n la mesure détecterait un rho de 0,3.
   La métrique de `07` corrèle avec les croisements publiés (+0,77) mais pas avec le
   résultat : **elle mesure un défaut de la TRACE, pas du RÉSULTAT**. Elle reste un
   contrôle qualité de trace bon marché ; elle n'est pas un argument sur le rendu.
   ⚠ Une seule trace — la seule qui ait maillage **et** encre.

## 6. ⚠ Le cap n'est PAS franchi

> **On ne publie rien sans une passe complète — rouleau déroulé, texte extrait, soumis
> à un expert qui dise si ça fait sens — et sur plusieurs rouleaux.**

Trois juges mécaniques ont échoué : Kraken (aucun modèle entraîné sur papyri), score
structurel sur région, score structurel sur segment entier. ⚠ La dernière cause est
définitive : **ce type de segment ne porte que 4 à 5 lignes de texte**, et les glyphes
**fusionnent** au seuil du modèle. Le juge calibré de `09` est le seul disponible.

## 7. ⏳ CE QUI RESTE — et le prochain lot n'est plus une mesure

⭐⭐ **Le cadrage a changé le 2026-08-19.** Objectif de l'auteur : *tout publiable pour le
31 août, les confirmations viennent après*. Et la lecture de la page des prix a corrigé la
cible — le pool ouvert fait **2 140 000 $** et le Grand Prize n'est pas le seul lot :

| prix | montant | ce qu'il faut | échéance |
|---|---:|---|---|
| **First Letters** | **50 000 $ × 10 rouleaux** | **10 lettres dans UNE zone de 4 cm²** | 25 juin 2027 |
| **Titre de PHerc. Paris 4** | **50 000 $** | l'image du titre, lisible par leurs papyrologues | 25 juin 2027 |
| Progress Prize | 20 000 $ / mois | la meilleure soumission du mois | **31 août** |
| Grand Prize | 800 000 $ | **100 %** du recto, intégré VC3D, ≤ 8 h d'annotation | 25 juin 2027 |

> ⭐ *« Sometimes ink is visible **directly in the flattened render, with no model at all**…
> **that by itself qualifies for the prize**. »* — donc l'étape suivante n'est pas
> d'entraîner, c'est de **regarder**.

| # | quoi | blocage |
|---|---|---|
| ~~T1~~ | ~~faire suivre une feuille au traceur~~ | ✅ **fermé le 2026-08-19** — mais en **deux moitiés**, et une seule est faite (`25`). *Où l'on part* est réglé ; *comment on avance* ne l'est pas |
| ~~T1b~~ | ~~brancher `direction_fields`~~ | ✅ **fait, et le résultat est un NÉGATIF** (`26`) : le contrat est dérivé, l'encodage mesuré sur 3 rouleaux, le champ se charge — et la croissance est **identique au centième**, même avec les axes délibérément permutés. Il n'agit que dans l'étape finale, où il fait empirer |
| ~~T1c~~ | ~~brancher `NormalGridVolume`~~ | ✅ **fait — second négatif** (`26` §7). La clé est **`normal_grid_path`** et elle est bien lue ; avec 1,53 Go de vraies grilles la vitesse tombe **×29** et la trajectoire ne bouge pas d'un centième **sur les 118 générations** ; l'étape finale, elle, rend **112 139** auto-intersections contre zéro. ⭐ Raison : les `.normal-grids` sont **dérivées de la prédiction que le traceur suit déjà** — les lui rendre est une tautologie |
| ~~T1d~~ | ~~régler `direction_weight`~~ | ✅ fait, jusqu'à ×100 : rien ne bouge (`26` §3) |
| ~~T1e~~ | ~~générer des grilles depuis le volume masqué~~ | ✅ **fait — troisième négatif** (`26` §8). 3,44 Go de volume en boîte à coordonnées absolues, 36 dalles sur 238, 4 608 tranches de grilles : **×17 de ralentissement, trajectoire identique**. Une information qui ne vient PAS de la prédiction ne change pas plus la trajectoire |
| **T1f** ⭐ | ce qui reste : la trajectoire ne répond qu'à **`step_size`** et à la **prédiction**. Explorer `step_size`, ou attaquer la prédiction elle-même | ⚠ ne PAS re-tenter les champs et les grilles : trois négatifs mesurés, chacun avec son contrôle |
| — | ⭐⭐ **le bilan qui cadre la suite** (`26` §8) : la trajectoire ne répond qu'à `step_size` et à la prédiction. Ni les champs, ni les grilles, ni les poids ne la déplacent — **la graine reste le seul levier mesuré** |
| ~~T2~~ | ~~rejouer la boucle sur d'autres rouleaux~~ | ✅ **fait** — `src/campagnes/campagne_graines.sh`, 12 rouleaux, appariée, reprenable |
| **T3** ⭐ | le **titre de Scroll 1** — *« looking somewhere new »* | c'est un problème de **recherche** sur le corpus où tous nos instruments marchent |
| T4 | finir et envoyer la soumission Progress Prize | ⏳ le texte existe (`21`), les chiffres sont gardés, il reste à publier le dépôt et à joindre les figures |
| R2 | exporter le champ de correction en coordonnées de fenêtre | — |
| — | le **pas inter-feuilles de PHerc1667** | ⚠ aucune prédiction de surface publiée pour ce rouleau : on ne juge pas ses sauts de feuille |
| — | le trend **position dans le rouleau** ↔ résiduel | ⚠ **NON établi** : trois corpus, trois motifs différents |

## 7bis. ⭐ T1 — ce qui a été fait, et ce qui reste (mis à jour le 2026-08-19)

> ✅ **La moitié « où l'on part » est faite** : `src/commun/trouver_graine.py` classe sur
> la planéité locale, `tracecheck.py --seed` la publie, et la campagne appariée sur
> 13 rouleaux la valide (`25`). ⚠ **La moitié « comment on avance » ne l'est pas** — voir
> T1b. ⚠ Ce qui suit est le contexte d'origine. **Il ne reste PAS exact en entier** :
> les trois pistes qu'il propose ont été mesurées négatives (`26`), et les chiffres de
> grilles qu'il cite ont été corrigés. Gardé pour la trace du raisonnement, pas comme
> consigne.

### Le contexte d'origine

**L'état exact** : la chaîne tourne de bout en bout (`docs/24`), les artefacts sont dans
[`data/artefacts/PHerc0358/`](data/artefacts/PHerc0358/) (2,2 Mo, dont le maillage et les paramètres
qui marchent), et **le seul défaut connu est que le traceur n'a aucune information
d'orientation**.

### Ce qui est établi et n'est pas à refaire

| fait | où |
|---|---|
| VC3D et ses 44 outils CLI sont installés sous `/usr/local/bin/` | §4 |
| `vc_grow_seg_from_seed -v` accepte `https://` — le volume n'est jamais téléchargé | `24` §1 |
| `seed.json` **doit** porter `"voxelsize"`, sinon tout est rejeté à 0 cm² | `24` §1 |
| la graine `1544 1544 7768` (ordre **x y z**) donne 8,48 cm² en 13,9 s | `data/artefacts/PHerc0358/` |
| la trace obtenue **coupe les spires** — 240 auto-intersections, 64 % de pics au bord | `24` §2 |
| `PHerc0358` est le rouleau **le moins difficile** des treize | `16` |
| **dix** rouleaux sur treize n'ont aucun segment | `23` |

### Les trois pistes, dans l'ordre du moins cher

1. ⭐ **Une graine choisie sur la PLANÉITÉ locale**, pas sur la valeur de voisinage.
   `src/commun/trouver_graine.py` classe aujourd'hui par la moyenne d'un cube 5³ — ce qui
   trouve « beaucoup de surface », y compris une **jonction** entre spires. Ce qu'il faut
   est un endroit où la prédiction forme un **plan** : mesurer l'anisotropie locale (le
   tenseur de structure de `src/nappe/fiber_orientation.py` sait déjà le faire) et
   retenir les points les plus plans. **Aucune donnée nouvelle à télécharger.**
2. **`step_size` réduit** (défaut 20) : moins de liberté par pas, donc moins de chances de
   sauter. Un essai coûte ~15 min.
3. **`direction_fields`**. ⚠ Deux obstacles vérifiés : le paramètre attend un chemin
   **local** (`std::filesystem::path`, pas d'URL) et la disposition `<zarr>/{x,y,z}/<niveau>`,
   alors que les `normal-grids` publiées (⚠ **10,40 Go**, pas 182 Mo — inventaire de `26` §6) sont en `xy/ xz/ yz/`. Il faut soit les
   convertir, soit les régénérer avec `vc_gen_normalgrids`, qui est installé.

### La boucle complète, une fois une trace obtenue

```bash
cd ~/LplVesuvius/data/trace/PHerc0358
S=".../surfaces/20250821151737-surface-...-th0.2.zarr"     # prediction
V=".../volumes/20250821151737-9.362um-1.2m-113keV-masked.zarr"
vc_grow_seg_from_seed -v "$S" -t . -p seed.json -s <x> <y> <z>
vc_tifxyz_selfcross --surface auto_grown_* -o selfcross.json   # ⚠ JUGER AVANT DE RENDRE
vc_flatten -i auto_grown_* -o flat
rm -rf render && vc_render_tifxyz -v cache_vol --remote-url "$V" --scale 1 -g 0 \
    -s flat --tif-output render -n 21 --slice-step 1 --auto-crop
cd ~/LplVesuvius/inference_xpu
uv run python src/volume/depth_profile.py data/trace/PHerc0358/render \
    --grid --step 400 --traced-layer 10 --voxel-um 9.362
uv run python src/volume/regarder_rendu.py data/trace/PHerc0358/render --png-dir data/trace/PHerc0358/png
```

⭐ **Le critère de succès est mesurable avant de regarder** : une bonne trace doit rendre
la part de pics **au bord** BASSE et le pic **centré**. La mauvaise trace de `24` donne
**64 % au bord, 16 % au centre, distribution bimodale**. C'est le nombre à faire descendre.

⚠ Et le but n'est que **4 cm²** avec 10 lettres — la trace ratée en faisait déjà 8,48.

## 8. ⚠ Les pièges payés, à ne pas repayer

**Mesure**
1. **Un seuil calé sur le niveau 0 ne se transporte pas** à une résolution réduite —
   réduire *moyenne* les voxels et remonte le fond. (« 53 feuilles au niveau 1 ».)
2. **Une valeur identique partout** = saturation contre sa propre borne. (Axe long à
   22,7 mm sur les 8 coupes.)
3. **Comparer une grandeur à elle-même.** (Mon « périmètre » valait 2π × rayon moyen.)
4. **Échantillonner à l'échelle de l'objet** et non de la structure cherchée : coupes
   à 22 mm pour un défaut millimétrique → verdict inversé.
5. **Décimer mange la queue** : −60 % du signal, parce qu'il *est* dans la queue.
6. **Un chiffre emprunté n'est pas une mesure** (« 300 µm entre spires »).
7. ⚠⚠ **Une référence locale doit être LARGE là où l'anomalie est PETITE.** Une boule
   3D autour d'un site de croisement est pleine de ce site : l'anomalie normalise sa
   propre référence. Mesuré : boule/bande = **1,001** partout, **0,766** aux cellules
   signalées, 43 traces sur 45, Wilcoxon **p = 1,4e-09** (`07` §6).
8. **Un seuil calibré sur un segment ne se transporte pas** : `TEXT_BANDS`/`BLANK_BANDS`
   sont des lignes mesurées sur `20230909121925`. Ailleurs, `--auto-bands`.
9. ⚠ **Un « témoin » où le détecteur trouve du signal n'est pas un témoin.** Refuser
   d'en rendre plutôt que d'en rendre de faux (`--blank-ceiling`).

**Outillage**
9bis. ⚠⚠ **`pgrep -x <nom>` échoue en silence au-delà de 15 caractères.** Linux tronque
    `comm` à 15 octets, donc `pgrep -x vc_render_tifxyz` ne matche **jamais** — et une
    boucle d'attente bâtie dessus sort **immédiatement**. Symptôme : on lit un TIFF dont
    l'IFD vaut `0x00000000`, c'est-à-dire un rendu à moitié écrit qui ressemble à un rendu
    fini. Attendre **par PID** (`while kill -0 $PID`), ou matcher le nom tronqué.
9ter. ⚠⚠ **Un argmax sur un échantillon nombreux sature contre la borne du score.** Le
    maximum de 13 824 blocs pour un score borné par 1 vaut ~1 quel que soit le terrain.
    C'est le piège nº 2 à un étage de plus, et je l'ai écrit **dans le fichier qui
    documentait déjà le piège**. Classer sur une **moyenne de voisinage**, pas sur un max.
9quater. ⚠⚠ **Une fenêtre plus étroite que la structure mesurée ne peut rien voir.** 21
    couches à 9,362 µm valent ±94 µm, soit une **demi**-distance inter-feuilles : le profil
    est plat à 1,5 %, et l'argmax d'un profil plat sort **aux deux bords**, ce qui imite
    une bimodalité. Vérifier l'**amplitude** avant de lire une position de pic.
9quinquies. ⚠⚠ **Un entier nu dans une recherche littérale ne peut pas être absent.**
    `verifier_chiffres` cherchait « 80 » et « 10 » dans des documents en prose : trouvés
    toujours, donc contrôles incapables d'échouer — **deux entrées antérieures** étaient
    concernées. Un chiffre se garde **avec son contexte** (« 80 segments »), jamais nu.
9septies. ⚠⚠ **Un processus par requête coûte une poignée de main TLS par requête.**
    41 538 chunks avec un `curl` par chunk : **7 chunks/s**. Avec un pool de connexions
    **persistantes** — une par fil, gardée ouverte sur des milliers de requêtes —
    **195 à 209 chunks/s**, soit **×28**. C'est la **latence** qui coûte, pas le débit.
    ⚠ LplKnowledge avait mesuré ×7,9 sur la même bascule (binaire `curl` → `libcurl`).
    ⚠⚠ **Ma première mesure du gain était fausse — ×6,8 — parce qu'elle a été prise
    pendant que les `curl` de l'ancienne version tournaient encore.** Un chiffre mesuré
    sous contention n'est pas le chiffre : arrêter l'ancien avant de mesurer le nouveau.
9octies. ⚠⚠ **`&&` après une commande qui échoue coupe la chaîne — et le commit ment.**
    `git rm … && python3 - <<EOF … EOF` : le `git rm` a refusé (modifications locales),
    donc le patch n'a **jamais** été appliqué, et le message de commit décrivait un
    changement absent. C'est le piège nº 18 sous un nouveau costume. Vérifier l'effet,
    pas le code de retour de la dernière commande.
9sexies. ⚠⚠ **`vc_grow_seg_from_seed` n'est pas reproductible**, même en `thread_limit: 1`
    (la valeur que VC3D utilise) : quatre exécutions de la même graine rendent quatre
    aires, à 0,08 % près. Les quatre rendent **0 auto-intersection** — donc juger par un
    **invariant**, jamais par l'artefact.
10. ⚠⚠ **Un outil validé sur 300 K cellules ne tient pas sur 21 M** : un `cKDTree`
   global y prend des gigaoctets et **a fait tomber la machine trois fois**. Découper
   en **blocs 3D** (validé à 0,0 % d'écart), jamais en tuiles de paramétrisation —
   la métrique cherche justement les points loin en paramétrisation et proches en 3D.
11. **`pkill -f` / `pgrep -f` matchent leur propre ligne de commande** (payé 4×).
12. **Le code de sortie d'un pipeline est celui de sa DERNIÈRE commande** (payé 3×).
13. **Chemin relatif après un `cd`** : `mkdir` à un endroit, écriture à un autre →
    10 bandes calculées puis perdues.
14. **Éditer un script pendant qu'il tourne** le casse (bash lit par offset).
15. **Une boucle d'attente sans borne** survit à la disparition de ce qu'elle attend
    (payé : 3 h 19).
16. **`aws s3 cp --include` énumère TOUT le préfixe.**
17. **Vérifier l'alignement avant toute comparaison d'images** (remplissage à 512).
18. ⚠ **`cd` dans un `&&` qui échoue coupe la chaîne** : le patch ne s'applique pas et
    la commande suivante tourne sur l'ancien code, dont la sortie a l'air plausible.
    Chemins **absolus** dans les scripts de patch (payé 3× le 2026-08-18).
19. **Mesurer là où la mesure a eu lieu** : le profil de profondeur a d'abord été pris
    à `left 2000` quand l'inférence tournait à `left 17000`, et il a répondu l'inverse.
20. ⚠⚠ **Afficher la courbe avant de croire son argmax.** Le contraste local a servi
    d'instrument jusqu'à ce qu'on trace sa courbe : sur un volume à 2,4 µm c'est un
    **U**, maximal aux deux bords et minimal dans la feuille — il suit les interfaces et
    le bruit. L'intensité localise la matière ; le contraste non. Les deux coïncidaient
    à 7,91 µm, donc rien ne les distinguait.
21. **Une statistique « relative à la fenêtre » n'est pas comparable entre fenêtres.**
    Le « tiers central » de la fenêtre 15–40 n'est pas centré sur la couche tracée 32,
    alors qu'il l'est sur un volume de surface. Rapporter un **écart à la trace en µm**.
22. **Une mesure « entre voisins » exige des voisins** : la première version tirait des
    fenêtres à vingt chunks d'écart et rendait `NaN` sur **0 paire comparée**.
23. ⚠ **Un zéro se rapporte avec sa puissance, et la puissance dit quoi faire.** À
    n = 12, seul un rho ≥ 0,73 est détectable : un +0,330 n'est alors ni confirmé ni
    infirmé, et la réponse est d'aller chercher n ≈ 70 — pas de conclure.
24. ⚠⚠ **Le piège nº 6 se repaie même en le connaissant** (2026-08-19). J'ai pris
    l'invariant de **PHerc0172** (142,8 µm) comme seuil pour des segments de
    **PHercParis4**, dont le pas mesuré vaut **172,8 µm** — quatre segments signalés au
    lieu d'un. Le remède n'est pas une note, c'est **retirer le défaut du paramètre** :
    sans `--pas-um`, l'outil ne rend plus le compte du tout.
25. ⚠⚠ **Un modèle de coût qui se flatte n'est pas un modèle de coût.** Le tableau
    d'échelle divisait par 16 fils ; la mesure dit **×8,35**. 0,5 h annoncé, 0,9 h réel.
26. ⚠ **Fermer un confond d'un seul côté ne le ferme pas.** Savoir que l'encre suit
    l'emprise ne suffit pas : il faut aussi savoir si le **critère** la suit. Les deux
    branches existaient (+0,463 et +0,384) — seule la corrélation **partielle** a tranché,
    et elle a **renforcé** la relation au lieu de la dissoudre.
27. ⚠ **Un échantillonnage régulier tombe dans le remplissage.** Un volume de surface est
    majoritairement du vide : des blocs posés à intervalles réguliers ont rendu **6
    fenêtres utiles sur 96**. Il faut **trouver la matière avant de la sonder**.
28quater. ⚠⚠ **Un outil qui saute ses sorties existantes saute aussi ses sorties
    CORROMPUES.** `vc_render_tifxyz` a affiché « all slices exist, skipping » sur 21 TIFF
    **tronqués** laissés par un run tué — et ça ressemble parfaitement à un rendu réussi.
    Effacer le répertoire de sortie avant de relancer.
28ter. ⚠⚠ **Un défaut par défaut peut annuler une vérification entière.** `voxelsize` vaut
    **0** dans les paramètres de `vc_grow_seg_from_seed`, donc l'aire en cm² est nulle *par
    construction* et **toute** surface est rejetée avec « area 0 below min_area_cm ». Le
    message accuse la surface ; le fautif est le paramètre absent.
28bis. ⚠⚠ **`kill $!` sur un `nohup uv run … &` ne tue que le WRAPPER.** Le vrai
    travailleur est un petit-fils (`uv run` → `python`), il survit, et il continue
    d'écrire dans le `--out` qu'on croyait abandonné. Payé **deux fois dans la même
    heure** : deux campagnes orphelines ont brûlé de la bande passante pendant 37 minutes
    en doublonnant celles qu'on venait de relancer, et le symptôme était une campagne
    « lente » et non une campagne fantôme. Remède : `ps -eo pid,ppid,etime,args` puis tuer
    **le petit-fils**, ou lancer avec `setsid` et tuer le groupe.
29. ⚠⚠ **Une réponse S3 contient le PRÉFIXE INTERROGÉ** en plus de ses sous-préfixes.
    Compter les lignes sans l'exclure décale une table de **un partout** — et une table
    décalée d'un cran ressemble parfaitement à une table juste.
30. ⚠⚠ **Un contrôle de robustesse doit d'abord prouver qu'il compare LA MÊME GRANDEUR.**
    J'ai passé une heure à affaiblir un résultat juste parce que je comparais un
    `avec_matiere` neutre à un mélange repérage+blocs. **La prudence n'est pas une
    méthode** : affaiblir semblait la position sûre, et c'est ce qui l'a rendu difficile
    à voir.
31. ⚠⚠ **Trop peu d'échantillons fabriquent des effets qui n'existent pas, avec leur
    explication toute prête.** À 3 tranches, la sensibilité du centre donnait **5,65 %** et
    une « marche » nette dès la plus petite perturbation, expliquée par « la mesure compte
    des pics, donc elle procède par marches ». À 6 tranches : **1,75 %**, aucune marche.
28. ⚠ Deux corrections de nom vérifiées sur le fichier plutôt que devinées : `events` est
    un **compte** dans l'index de `windcheck`, pas une liste ; et le volume `cos` du
    `lasagna` déclare ses niveaux dans son `.zattrs` — il n'en a pas de plus fin que 3.


**Ajoutés le 2026-08-19 (soirée)**
32. ⚠⚠ **Un run TUÉ enregistré comme une mesure — et sa valeur était le résultat
    espéré.** `timeout 3600` a tué `pas_5` à la génération 406 sur 480 ; sans maillage
    écrit, le script a enregistré `aire_cm2: 0` **et `transverse: 0`**. Or zéro
    auto-intersection est exactement ce qu'on cherche. **Un échec et un succès parfait
    avaient la même représentation.** Remède : lire le code de sortie (124 = tué), écrire
    un `statut` explicite, et ne laisser la garde de reprise accepter que `ok`.
33. ⚠ **Un budget de temps CONSTANT biaise la grandeur comparée.** Le même `timeout 3600`
    pour tous les pas favorise mécaniquement les grands, qui font moins de générations. Un
    budget doit suivre la cible.
34. ⚠⚠ **Un fichier vide dit deux choses.** `volumes_surface_PHerc0800.txt` était
    versionné vide, et signifiait à la fois « ce rouleau ne publie aucun volume » et « le
    listage a échoué » — le script tronquait la sortie **avant** d'interroger S3. Remède :
    tester la source avant d'écrire, et faire porter au fichier une ligne qui **dit** son
    résultat, y compris quand il est zéro.
35. ⚠ **`awk '$3>0'` compare NUMÉRIQUEMENT dès qu'un champ commence par un chiffre.** Un
    en-tête tabulé dont le 3ᵉ champ était une date `2026-08-19` passait le filtre et
    ressortait comme une ligne de données. Attrapé par le contrôle, pas par la relecture.
    Un en-tête de commentaire ne doit porter **aucun séparateur de champ**.
36. ⚠⚠ **Lire un papier depuis son résumé produit des chiffres faux.** La première version
    de `27` annonçait une « cible de 4 µm » absente du texte (la vraie est ~1 µm), une
    paraphrase entre guillemets, et reprenait une affirmation qu'un des papiers réfute
    avec un nombre. **Un résumé dit ce qu'un papier revendique, pas ce qu'il mesure** — et
    ce qui compte est presque toujours dans les tableaux, les limites, ou le code publié.
37. ⚠ **Le code publié d'un papier dit ce que le papier ne dit pas.** `fit_spiral.py` porte
    trois réserves en commentaire sur sa propre métrique (mesure en espace spirale, biais
    par densité, vérité terrain qui **saute elle-même** d'une spire) dont aucune n'est dans
    l'article. Cloner le dépôt d'une méthode qu'on cite coûte trente secondes.
38bis. ⚠⚠ **La chaîne magique d'un harnais de test ne doit apparaître QU'à la ligne de
    verdict.** `src/outils/temoins.sh` déclarait une batterie verte en cherchant `ALL PASS`
    *n'importe où* dans sa sortie, et **perdait le code de sortie dans le tube**. Deux
    batteries écrites le même jour sont passées au vert **en échouant** : l'une imprimait
    `ALL PASS (1 failures, …)` dans son bloc d'échec, l'autre recopiait la ligne de
    référence d'une **autre** suite. Fermé structurellement : `run()` exige désormais
    **code de sortie 0 ET** `ALL PASS`, et lit le **dernier** match, pas le premier.
39. ⚠⚠ **Un artefact de mesure doit porter CE SUR QUOI il a été pris.** Payé **trois
    fois** le même jour : `docs/mesures/sweep_PHerc1667.jsonl` n'enregistre ni le zarr ni la taille
    de voxel, donc `07` §11 attribue à PHerc1667 une résolution de **7,91 µm** que le
    bucket ne publie pas ; `docs/carte_difficulte/*.json` n'enregistre pas le nombre de
    chunks, donc `16` cite le nombre **nominal** du script ; et l'artefact des fibres
    n'enregistre pas la liste des segments, donc `14` annonce **12** au-dessus d'un tableau
    de **11**. Remède : la provenance (résolution, liste, comptes) va dans l'artefact, pas
    dans la phrase qui le cite.
40. ⚠⚠ **Un artefact versionné sans producteur dans l'arbre est une anecdote.** Six
    fichiers de mesure l'étaient — `src/depot/artefacts_orphelins.py` les a trouvés et
    est désormais une batterie de `temoins.sh`. ⚠ Sa première version signalait **389
    orphelins sur 568** parce qu'elle cherchait le nom de fichier seul, alors qu'un
    artefact par segment est nommé d'après le segment : *une alerte qui désigne les deux
    tiers du corpus ne désigne rien.*
41. ⚠ **Les backticks d'un message de commit sont exécutés par le shell.** Un
    `git commit -m "… \`timeout 3600\` …"` a lancé `timeout` et laissé des trous dans le
    message. Passer par `git commit -F fichier`.

**Ajoutés le 2026-08-20**
42. ⚠⚠ **Un verdict et une absence de mesure peuvent sortir par le même champ.**
    `vc_tifxyz_selfcross` rend `clean_of_transverse_self_intersection: true` avec
    `pairs_tested: 0` dès que son filtre `--maxedge` a jeté tous les quads — ce qui arrive
    **au réglage par défaut** sur un maillage à pas ≥ 60. Un portail bâti sur
    `--fail-on-crossing` laisserait alors passer n'importe quelle surface, avec le code de
    sortie 0 que le script attend. Six scripts d'ici lisaient ce rapport sans regarder
    `pairs_tested`. Remède : un **seul** lecteur, qui **refuse** au lieu de rendre un zéro
    assorti d'une réserve (`src/nappe/lire_selfcross.py`, `34`).
43. ⚠⚠ **Un compte n'est pas comparable entre deux résolutions de la chose qui compte.**
    Le même maillage, décimé sans que sa géométrie change, passe de **240** croisements à
    123, 72, 49. « Zéro au pas 40 » vaut donc moins que « zéro au pas 20 », et l'écart est
    mesuré (`34` §3). La règle générale : avant de comparer deux comptes, vérifier que
    l'**instrument** avait la même sensibilité des deux côtés.
44. ⚠⚠ **Une proportion sans son effectif ordonne ce qui n'est pas ordonné.** `16`
    classait treize rouleaux sur des parts de 4 à 24 %, mesurées sur **15 à 35 fenêtres**.
    Aucune des 78 paires n'est séparée, et le « 0 % » du témoin est compatible avec 14 %
    (`33`). Publier une part **sans son intervalle** est ce qui a rendu ce classement
    crédible pendant deux jours.
45. ⚠⚠ **Éditer un script pendant qu'il tourne le casse** — payé le 2026-08-20 sur
    `campagne_tirages.sh`, alors que le piège est écrit dans le `CLAUDE.md` de l'espace de
    travail. `bash` lit par offset : la campagne a fini son rouleau courant puis est morte
    sur « syntax error near unexpected token `done` ». Les 48 tirages déjà écrits étaient
    bons — vérifié, pas supposé, par un **contrôle d'intégrité** ajouté dans
    `table_tirages.py` : le résumé est une copie, le rapport `selfcross.json` est le
    record, et un désaccord est imprimé plutôt que résolu en silence.
46. ⚠⚠ **Une garde qui refuse pour une raison fausse est pire qu'une garde absente.**
    `campagne_tirages.sh` comparait deux tailles de voxel **comme du texte** et a sauté
    `PHerc0268` et `PHerc0800` en annonçant « 8.640 µm ≠ 8.64 µm ». Elle avait l'air de
    protéger la comparabilité des aires ; elle retirait des données.
47. ⚠ **Une étiquette sur un seul échantillon ne peut pas être fausse.** Mon propre
    dépouillement a affiché « reproductible » pour un rouleau qui n'avait qu'**un** tirage
    — l'aire y est trivialement identique à elle-même. Toute statistique de dispersion
    doit exiger n ≥ 2 et dire « non concluant » sinon.

**Ajoutés le 2026-08-20 (après-midi)**
48. ⚠⚠ **Une hypothèse vérifiée pour un producteur, utilisée pour un autre.** `12` §13
    vérifie sérieusement — 98 segments — que la couche tracée est au milieu de la pile, mais
    sur les **volumes de surface publiés**. Nos piles viennent de `vc_flatten` →
    `vc_render_tifxyz`, et le transport n'était dit nulle part. ⭐ Le contrôle a **réfuté**
    le soupçon (14,3 µm sur le même segment), et c'est le bon dénouement : la question
    méritait d'être posée, et sa réponse est maintenant écrite au lieu d'être supposée.
49. ⚠⚠ **Un exemplaire d'une classe n'est pas la classe.** `25` a retiré un critère parce
    qu'**un** segment officiel y échouait. Les quatre segments publiés du même rouleau vont
    de **18 % à 68 %**, et le quatrième s'appelle `z_dbg_gen_00320`. Avant d'appeler quelque
    chose « la référence », regarder combien il y en a et comment ils se distribuent.
50. ⚠ **Un chemin S3 se LISTE, il ne se devine pas.** J'ai supposé
    `<segment>/<segment>.tifxyz/` — la convention d'un maillage local — là où le bucket range
    sous `mesh/tifxyz/`. Le script a échoué sur « meta.json absent », message qui accuse le
    segment quand le fautif est le chemin. ⭐ Et le listage a rendu un fait qu'aucune
    supposition n'aurait donné : le dépôt publie aussi un `_flattened.obj`, donc leur chaîne
    aplatit comme la nôtre.
51. ⚠⚠ **Deux instruments qui mesurent la même chose n'écrivent pas les mêmes noms de
    champs.** `zarr_depth.py` écrit `ecart_a_la_trace` et un `layers` **entier** ;
    `depth_profile.py` écrit `ecart_trace_um_median` et un `layers` **liste**. Le rapport de
    l'expérience décisive supposait les seconds partout et levait un `TypeError` sur
    `len(int)` — donc **l'expérience ne rendait rien alors que ses deux moitiés avaient
    abouti**. Un lecteur qui joint deux producteurs doit réconcilier explicitement.
52. ⚠ **Une légende écrite à la main sur une figure juste.** Deux fois le même jour :
    « 11ᵉ » là où l'artefact dit 10ᵉ, et « il ne l'est sur aucun des quatre » là où la figure
    montrait le contraire sur une ligne. Les comptes et les rangs d'une légende se
    **dérivent des données**, comme le reste.
53. ⚠ **Le piège nº 41 se repaie en le connaissant** : les backticks d'un message de commit
    sont exécutés par le shell, et deux numéros de document ont disparu du message. Toujours
    `git commit -F fichier`, y compris quand le message paraît anodin.
54. ⭐ **Le remède structurel a fonctionné le jour même.** `src/outils/lancer.sh` gèle une copie
    avant de lancer ; corriger `campagne_second_axe.sh` **pendant qu'elle tournait** n'a rien
    cassé, là où la même chose avait tué deux campagnes le matin.

**Ajoutés le 2026-08-20 (soir) — et le premier est la leçon du jour**
55. ⭐⭐⭐ **Quand trois statistiques différentes dépendent toutes du réglage, la dépendance
    EST le signal.** En une après-midi, trois hypothèses sont tombées pour la même raison :
    l'écart à la trace suivait la fenêtre de rendu, l'écart *en spires* aussi, et la part de
    fenêtres plates aussi. La quatrième tentative n'a pas cherché une meilleure statistique —
    elle a **mesuré la dépendance** : une surface qui suit sa feuille garde sa distance quand
    la fenêtre triple (α = +0,00), la nôtre la suit (α = +1,01). ⭐ Le meilleur instrument du
    dépôt est sorti de l'échec des trois précédents, et il n'a ni seuil, ni vérité terrain,
    ni échelle. **Avant de chercher une statistique de plus, regarder ce que les échecs ont
    en commun.**
56. ⚠⚠ **Une valeur non censurée peut quand même suivre son plafond.** Le refus « écart ==
    plafond » ne suffisait pas : des valeurs à **90–94 %** de leur portée paraissaient
    mesurées et ne l'étaient pas. La règle générale : une mesure bornée par un réglage doit
    être écartée bien avant sa borne, et le seuil (80 %) doit être écrit dans l'instrument,
    pas dans la tête de qui le lit.
57. ⚠ **Deux refus peuvent se subsumer sans qu'on le voie.** Le refus de non-convergence
    couvre entièrement celui de censure — une valeur censurée vaut 100 % de sa portée — donc
    retirer la censure du filtre laissait le témoin **vert**. Trouvé par sonde, pas par
    relecture. Le remède n'est pas de choisir : c'est d'**asserter la subsomption**, et de
    garder les deux messages parce que « censuré » se lit mieux que « 100 % ».
58. ⚠ **Une métadonnée publiée peut porter la recette entière.** Le `meta.json` d'un segment
    officiel est dépouillé, mais `mesh/intermediate/tifxyz_original/meta.json` porte **la
    graine, le mode, les paramètres et le nombre de générations**. Regarder les
    intermédiaires avant de conclure qu'une provenance n'est pas publiée.


60. ⚠⚠ **Un chien de garde peut surveiller la mauvaise chose et tuer ce qui va bien.** Ma
    première version de `src/outils/rendre_surveille.sh` abandonnait un rendu dont la **sortie**
    ne grossissait plus. Or `vc_render_tifxyz` télécharge tout avant d'écrire : mesuré,
    `rchar` passait de 6,56 à 8,21 Mo en douze secondes pendant que `wchar` restait à 500
    octets et la sortie à 328. Le garde aurait tué un rendu sain et on en aurait conclu
    « injouable » sur un rendu qui marchait. ⭐ Surveiller l'**activité du processus**
    (`/proc/<pid>/io`, somme lecture + écriture) et pas son résultat.
    ⚠⚠ **Et le chiffre que j'en avais tiré était faux.** J'ai annoncé « plus de douze
    heures » à partir d'**un seul échantillon de quinze minutes** à 57 Ko/s ; le rendu
    suivant, même échelle et même volume, a fait **1108 Kio/s** — vingt fois plus. Une
    extrapolation depuis un point n'est pas une mesure, et j'ai arrêté une campagne
    là-dessus. ⭐ C'est le rapport de débit du chien de garde lui-même qui l'a corrigé :
    l'instrument construit pour diagnostiquer le problème a démenti le diagnostic.
61. ⚠⚠ **α ≈ 1 a deux causes, et le verdict n'en nommait qu'une.** Un profil plat n'a pas de
    pic, donc l'écart rapporté est le **bord de la fenêtre** — et le rapport de deux bords
    vaut le rapport des fenêtres, donc α = 1 **par identité arithmétique**. Le verdict
    imprimait quand même « le pic s'éloigne avec la fenêtre », une phrase sur un objet qui
    n'existe pas. Voir [`49`](docs/49_alpha_ne_separe_pas_deux_pannes.md). ⭐ Aucun verdict de
    convergence n'est touché — mesuré, 0 série convergente sur 107.
62. ⚠⚠ **Une fixture écrite d'après le code ne prouve que leur accord.** Mon lecteur de
    `table_tirages.json` cherchait la clé `tirages` (le fichier a `n`), a rendu **zéro
    rouleau traçable**, et le verdict « les deux ensembles sont disjoints » en découlait,
    parfaitement confiant — un ensemble vide le satisfait. Le témoin n'a rien vu parce que sa
    fixture utilisait la clé supposée. ⭐ Remède : le lecteur **refuse** au lieu de rendre
    vide, et une sonde tourne sur le **vrai fichier de résultat**.
62 bis. ⚠⚠ **`lancer.sh` gèle le script de campagne, PAS ses helpers.** Une campagne qui
    appelle `src/outils/rendre_surveille.sh` par chemin le relit **pendant** qu'on l'édite, et
    bash lit un script *par offset* : le run en cours s'est mis à exécuter des morceaux du
    bloc `--verifier` que je venais d'insérer (`v: command not found`). C'est le piège nº 45
    par une porte que le gel ne ferme pas. La règle pratique reste la même — **ne pas éditer
    un script pendant qu'un run l'utilise**, helper compris.
62 ter. ⚠⚠ **Une campagne relancée dans la même destination détruit la preuve d'un tableau
    publié.** `data/spires_pas025/spire03` porte des profils de 14 h 29 quand le verdict que
    `43` tabule date de 08 h 02 le même jour — et le traceur étant un tirage, ce n'est pas le
    même résultat. Les **verdicts** survivent dans `docs/`, les profils non. La règle « un run
    prend sa propre destination » ne vaut pas que pour des paramètres différents : elle vaut
    pour un run aux **mêmes** paramètres. ⭐ Corollaire pour qui lit un audit de l'arbre : un
    écart avec un document publié n'est pas forcément une erreur du document — regarder les
    horodatages d'abord.
62 quater. ⚠⚠ **Conclure à une absence depuis UNE SEULE orthographe.** Payé deux fois dans
    le même quart d'heure sur `21`. (a) J'ai grepé `^> #### ` et conclu « il n'y a pas de
    section 13 » — elle existe, écrite `### ` hors de la citation. (b) J'ai cherché
    « 0 candidat » dans un texte **anglais** et conclu que son contenu manquait — il est là,
    sous « 105 pairs » et « 79 µm ». ⚠⚠⚠ Et la première m'a fait *renuméroter* un schéma
    parfaitement cohérent : le « doublon 10 » est un **10 bis**, annoncé par un séparateur
    juste au-dessus que mon motif ne voyait pas. ⭐ Chercher le **contenu** avant de conclure
    à l'absence d'une **forme** — et, devant une incohérence apparente dans un document
    ancien, se demander d'abord si c'est le motif de recherche qui est trop étroit.
63. ⚠ **Ne pas anticiper un compte, même juste.** Écrire dans les documents le total qu'on
    prévoit pour le run courant le fait échouer — la garde compare aux totaux du run
    **précédent**. Prédiction 46/1348, mesure 46/1348, batterie rouge quand même. Lancer,
    **lire**, écrire, et le run suivant confirme.
64. ⚠ **Recopier un nombre, c'est perdre ce qui l'accompagne.** J'ai passé les écarts au juge
    de convergence par `--serie "41:48.0,161:192.0"` et perdu, au passage, l'amplitude et la
    part au bord que le profil portait — donc le juge n'a pas pu refuser. Le chemin
    `--profil` construit la série depuis les fichiers eux-mêmes.
65. ⚠ **Un résumé identique à la décimale est un résultat ET le symptôme d'une colonne
    recopiée deux fois**, et rien dans le tableau ne les distingue. `04` donnait la même
    moyenne, médiane, quartiles et σ aux deux populations. ⭐ L'instrument compare désormais
    les **multiensembles** de valeurs et refuse de dessiner si ce sont les mêmes données.
66. ⚠⚠ **Un budget choisi sur un coût faux devient un résultat.** Toutes les traces jamais
    faites sur `PHercParis4` s'arrêtent à la génération 59, et leurs aires coïncident à
    quatre chiffres — 0,3174 à 0,3182 cm², **0,25 % d'écart** — pour des graines séparées par
    des kilovoxels, dans deux prédictions différentes. Elles mesurent le **plafond**, pas la
    donnée. Or ce plafond de 60 a été fixé le jour où j'estimais le rendu à **57 Kio/s**, une
    extrapolation faite sur *un* échantillon ; la mesure l'a corrigé à **1108–5861 Kio/s**,
    vingt à cent fois plus vite. ⭐ **La leçon n'est pas « 60 était trop petit »** — on ne le
    sait pas encore, `src/outils/plafond_generations.sh` le mesure. Elle est plus gênante : un
    réglage pris pour une raison qui a cessé d'être vraie ne se signale jamais tout seul, et
    la **cohérence** des résultats qu'il produit est précisément ce qui le rend invisible.
    Sept traces d'accord à quatre chiffres ressemblent à une mesure robuste. ⚠ Corollaire :
    quand des runs indépendants s'accordent **au-delà de ce que leur bruit permet**, ce n'est
    pas une bonne nouvelle, c'est un réglage partagé qui parle à leur place. Ce qui l'a
    attrapé : avoir regardé une colonne qui n'était le sujet d'aucune question.
67. ⚠⚠ **Une sonde qui scanne son propre fichier ne doit jamais contenir son motif en
    clair.** Payé **trois fois** dans la même session : `pkill -f "validate.sh"` a tué mon
    propre shell ; `grep -q vc_grow_seg_from_seed` dans une sonde « aucune trace n'est
    réécrite ici » a signalé une duplication qui n'existait pas ; puis `grep -q
    rendre_surveille` dans une sonde « ce fichier ne rend pas lui-même ». À chaque fois le
    symptôme est le même et il est trompeur : **la sonde échoue sur un fichier correct**, et
    on part chercher le défaut dans le code au lieu de la sonde. ⭐ Remède : couper le motif
    en deux morceaux concaténés (`"tranches_au""_niveau"`), ce que le shell recolle et que
    le fichier ne contient donc pas d'un bloc. Corollaire plus général : quand une
    vérification échoue sur quelque chose qu'on vient d'écrire correctement, **suspecter la
    vérification avant le code**.


### ⭐⭐ 2026-08-22 (fin) — la voie du raccordement est fermée, et deux gardes de plus

**Le résultat, pour 4,5 Mo.** `vc_merge_tifxyz` sait raccorder des surfaces mais exige qu'elles
se **recouvrent**. Le dépôt public de `PHerc1447` publie **15 segments** — ce dépôt n'en avait
jamais utilisé qu'un. 51 de leurs 105 paires se recouvrent par boîte englobante, beaucoup à
90–100 %, mais un recouvrement de boîtes ne distingue pas « deux patchs d'une feuille » de
« deux nappes voisines » : à 113 µm d'écart elles occupent presque le même volume. Le
discriminant est la **distance médiane point-à-point** :

| écart médian | ce que ça veut dire | paires |
|---|---|---:|
| < 40 µm | patchs de la **même feuille**, raccordables | ⚠⚠ **0** |
| 40 à 250 µm | nappes **voisines** | 2 *(79 et 89 µm)* |
| ≥ 318 µm | plusieurs feuilles | 45 mesurées + 4 hors de portée |

> **La segmentation publiée de ce rouleau est un ensemble d'échantillons UN PATCH PAR
> FEUILLE, pas le pavage d'une feuille.** Les deux voies vers une bande continue sont donc
> mesurées et fermées : l'extension tangentielle converge vers un point fixe (~6 cm²), et le
> raccordement n'a aucun candidat. Outil : `src/commun/carte_segments.py` — il refait la
> carte en une commande le jour où le dépôt public grandit.

**⚠⚠ Un chiffre publié la veille était faux, et c'est la garde qui l'a dit.** Le tableau
annonçait 49 paires éloignées : il supposait que les 51 recouvrantes avaient toutes été
mesurées, alors que 4 ne l'ont pas été. `ecart_entre` rendait `None` pour **trois** raisons
— maillage illisible, patch trop maigre, *aucun point à moins de 432 µm* — et seule la
troisième est une mesure (« ces deux nappes sont loin »). Il rend désormais une **raison** à
côté de sa valeur, et `verifier_chiffres.py` recompte les quatre bandes depuis le JSON.
⭐ Le témoin a gagné la sonde qui manquait : les bandes doivent **totaliser** les paires
jugeables.

**⚠⚠ Et une garde neuve, parce que le dossier PART.** Les chiffres de
[`21`](docs/21_texte_de_soumission.md) sont recopiés **à l'anglaise** (`12.97`) depuis une
prose française (`12,97`) : la recherche « ce chiffre existe quelque part » était donc
satisfaite par le document **source**, et une faute de frappe à la recopie passait au vert.
`verifier_chiffres.py --soumission docs/21…md` exige que les chiffres cités par le corps
soient trouvés **dans ce document-là**. Sonde faite : transposer `12,97` en `12,79` dans une
copie fait échouer le contrôle. Câblé dans `src/outils/temoins.sh`.

**Le dossier est à jour** : la section 12 affirmait « aucun mode de l'outil ne fait de chaîne
tangentielle **aujourd'hui** » — réfuté par nos propres mesures depuis. Elle renvoie
maintenant à une **section 13** qui publie l'extension (×3 d'aire utile à α = +0,000), son
non-déterminisme corrigé, le point fixe du cycle, et la fermeture du raccordement.

⭐ Figure neuve : `docs/images/44_ecarts_segments.png`. Un compte de zéro se lit comme un
résultat faible ; la distribution montre un **trou d'un facteur deux** sous le seuil — la
paire la plus proche du rouleau est encore à 79 µm.

**Vérifié** : `src/outils/temoins.sh` — **TOUS LES TEMOINS PASSENT**, `93 chiffres retrouvés`
(contre 68 en début de session), 0 script sans appelant, 0 artefact sans producteur.
⚠ Les deux JSON `docs/cycle2_gen10*.json` étaient orphelins : leur producteur
`src/outils/juger_rognages.sh` existait mais l'**étiquette** (`cycle2_`), qui fait partie du nom du
résultat, ne vivait que dans un terminal. Les deux invocations réelles sont écrites dans le
script.

### ⭐⭐ MATIN DU 2026-08-22 — ce que l'extension tangentielle sait faire, et où elle s'arrête

Suite du bloc ci-dessous. Toutes les mesures sont sous graine et `thread_limit: 1`, donc
rejouables ; l'outil est `src/outils/etendre_nappe.sh`.

| surface | aire utile | croisements | α | **pic au bord** |
|---|---:|---:|---:|---:|
| segment officiel (départ) | 4,28 cm² | — | +0,000 | **0 %** |
| **extension, budget 100** | ⭐ **12,97 cm²** | **0** | ⭐ **+0,000** | 9 % |
| extension, budget 50 | 7,54 cm² | 0 | +0,000 | 12 % |
| budget 200 **d'un coup** | 28,62 cm² | 25 036 | ⚠ +1,313 | 30 % |
| budget 200 **en deux fois 100** | 50,30 cm² | 4 996 | ⚠ +1,040 | ⚠⚠ 56 % |
| budget 400 d'un coup | 78,30 cm² | 168 104 | *(non jugé)* | — |

**Ce qui est acquis :**
- ⭐ **Une extension triple la surface utile sans quitter la feuille** — 4,28 → 12,97 cm², arc
  21,9 → 37,2 mm, sommets valides 59 → 96 %, α = +0,000, reproduit **quatre fois**. C'est la
  première fois qu'une surface que nous produisons **gagne** de la surface (la chaîne radiale
  en perd 15,6 % par tour).
- ⚠ **Le gros budget ne tient pas.** Doubler le budget double l'aire et détruit la
  convergence : la surface **se replie sur elle-même** (25 036 auto-intersections).
- ⚠ **Enchaîner aide beaucoup et ne suffit pas.** Même budget final atteint en deux séances :
  +76 % d'aire et **cinq fois moins** de croisements qu'en une seule — mais toujours en
  travers.
- ⚠⚠ **Le budget est CUMULATIF** (`generations`, compté depuis le compteur de la surface
  reprise) : « enchaîner à budget constant » n'existe pas, le pas *I* doit viser *I × G*.

**⚠⚠ ET UNE LIMITE DE L'INSTRUMENT, trouvée en REGARDANT une figure :** α est une **médiane**,
donc il cache une minorité. L'extension à α = +0,000 a **9 % de fenêtres dont le pic tombe au
bord** — une périphérie sans feuille à portée, visible sur le rendu et invisible dans le
verdict. Pire : la chaîne à deux pas a un **meilleur α** (+1,040 contre +1,313) et une part au
bord **presque doublée** (56 % contre 30 %). **Une médiane peut s'améliorer pendant qu'une
minorité empire.**
⭐ Corrigé structurellement : `test_convergence.py --au-bord` attache une **réserve** à tout
verdict au-delà de 5 %, et les deux scripts de campagne la transmettent. Tout verdict α du
dépôt hérite de cette limite ; désormais il la porte.
⚠ Réserve sur la réserve : `au_bord_relief` est une **fraction**, donc sensible au rapport
périmètre/aire — mais la source, qui est la plus petite, est à 0 %, donc la taille n'explique
pas tout. À ne pas comparer entre surfaces de tailles très différentes sans y penser.

**✅ ~~En cours~~ RENDU, négativement** (`44`:1535 : « 100 | en deux fois 50 | 20,06 cm² | 0 | +1,806 (pire) ») : chaîne à pas de 50 (quatre pas cumulatifs). Le texte d'origine : si l'amélioration continue quand
le pas diminue, il existe une taille de pas qui tient et la bande peut grandir.

### ⭐⭐⭐ NUIT DU 2026-08-22 — la chaîne TANGENTIELLE, et un non-déterminisme trouvé

**Le contexte** : [`44`](docs/44_ou_la_chaine_se_trouve.md) §7 a établi qu'une chaîne radiale
(`gen_neighbor`) est une **colonne**, pas une bande — donc pour un morceau de rouleau déroulé
il faut étendre une nappe le long d'elle-même, et aucun mode de l'outil ne le fait
explicitement. `mode: resume` est le seul candidat.

**Le résultat, reproductible** : `src/outils/etendre_nappe.sh` étend le segment officiel qui
converge.

| | aire utile | sommets valides | arc | % d'un tour | α |
|---|---:|---:|---:|---:|---:|
| source officielle | 4,28 cm² | 59 % | 21,9 mm | 11,5 % | +0,000 |
| **extension** | ⭐ **12,97 cm²** | ⭐ **96 %** | ⭐ **37,2 mm** | **14,5 %** | ⭐ **+0,000** |

⭐⭐ **Première fois dans ce dépôt qu'une surface que nous produisons GAGNE de la surface** — la
chaîne radiale en perd 15,6 % par tour. Et elle rebouche ses trous (59 → 96 %), et son arc
grandit de 70 %, ce qui est la grandeur qui compte pour le graal.

**⚠⚠⚠ TROIS PIÈGES TROUVÉS EN Y ARRIVANT, tous dans la source :**

1. **`resume_generations` n'est lu par personne.** L'application écrit cette clé
   (`--resume-generations`, app :308) et `GrowPatch.cpp` lit `params.value("generations", 100)`
   (:3428). Dans GrowPatch, `resume_generations` n'est qu'une **variable locale** (le canal de
   générations par sommet, :3493). Donc la campagne `spires_repousse` (`resume_generations: 20`)
   et mon balayage (1, 3, 10) ont **tous** tourné à 100 générations — le journal le dit :
   « gen 96, 97, 98, 99 ». Un paramètre mort qui a l'air vivant : présent dans l'aide, dans le
   méta du maillage, dans nos scripts.
2. ⚠⚠⚠ **`mode: resume` N'ÉTAIT PAS DÉTERMINISTE.** Le générateur des perturbations est
   `thread_local` et, sans graine, semé par `std::random_device` (:99-107) ; les runs
   tournaient sur **22 threads OpenMP** alors que l'outil écrit lui-même *« tracing does not
   scale past a few threads (VC3D uses 1) »*. Mesuré : trois exécutions aux paramètres
   effectifs identiques ont donné **0, 596 et 0** auto-intersections et α = +0,000 / **+0,422**
   / +0,000.
   **Correctif vérifié** : `VC_GROWPATCH_RNG_SEED` (variable d'ENVIRONNEMENT, pas une clé de
   params) + `thread_limit: 1` → deux exécutions identiques donnent un maillage **identique
   octet pour octet**, 13,024947 cm² d'aire de méta des deux côtés (à ne pas confondre avec l'aire UTILE, 12,97 cm²).
3. **Ce que ça fait aux résultats passés** : ⭐ les 17 essais de `42` en sortent *renforcés*
   (17 tirages indépendants tous à α ≈ 1 échantillonnent la distribution) ; ⚠ mais l'unique
   point à +0,422 de la repousse est un tirage, donc **« resume sur une surface projetée
   dérive » n'est PAS établi** — à refaire sous graine.
   ⭐ La chaîne radiale n'est pas concernée : `gen_neighbor` n'a aucun aléa (vérifié), d'où ses
   maillages identiques au bit entre campagnes.

**Restant** : le vrai balayage de `generations` (100 mesuré, 200 et 400 à faire) — c'est le
budget d'extension, et le ×3 ci-dessus a été obtenu avec sa valeur **par défaut**.

### ⭐⭐⭐ RÉSULTAT DU 2026-08-21 (nuit) — ce n'est pas le PAS, c'est la PORTÉE

Le mécanisme de la courbe en U est lu dans `vc_grow_seg_from_seed.cpp` : `neighbor_exit_count`
(défaut 1) compte des **pas** et non une distance, donc la portée physique du test de sortie
du rayon vaut `exit_count × neighbor_step` — 8,6 µm à pas 1,0, **1,1 µm à pas 0,125**. À pas
fin, un seul échantillon sous-voxel interpolé suffit à déclarer « j'ai quitté la nappe », et le
rayon peut sortir puis rentrer dans **la même feuille**.

**Prédiction lancée, falsifiable des deux côtés, CONFIRMÉE** :

| campagne | pas | **portée** | α moyen | α pire tour | verdicts fragiles |
|---|---:|---:|---:|---:|---:|
| défauts | 1,0 | 1,0 | +0,357 | +1,475 | 1/7 |
| défauts | 0,5 | 0,5 | +0,129 | +0,583 | 1/7 |
| défauts | **0,25** | **0,25** | ⭐ **+0,102** | ⭐ **+0,246** | 1/9 |
| défauts | 0,125 | 0,125 | +0,327 | +0,758 | **4/11** |
| **`exit_count=2`** | **0,125** | **0,25** | ⭐ **+0,130** | +0,350 | ⭐ **0/10** |

⭐⭐ **À pas égal, changer la seule portée fait passer l'α de +0,327 à +0,130.** Deux campagnes
dont les pas diffèrent d'un facteur 2 mais qui partagent la portée 0,25 donnent le même α, et
**deux de leurs spires sont identiques au millième** (02 à +0,202, 06 à +0,246).

> **Ce n'est pas le pas qui a un optimum, c'est la PORTÉE.** Le pas peut donc être affiné
> librement — ce qui localise mieux la nappe — à condition de relever `exit_count` du même
> facteur.

⭐ Et la campagne compensée est **la seule dont aucun verdict n'est fragile** (0/10 contre 4/11
pour la même chaîne aux défauts) : tenir la portée ne fait pas que baisser les α, ça rend les
verdicts tranchés.

⚠ **Ce qui reste ouvert** : où est l'optimum de la portée. Quatre valeurs mesurées seulement
(0,125 / 0,25 / 0,5 / 1,0), et `neighbor_exit_threshold` (défaut `threshold × 0,5`) n'a jamais
été touché — la portée optimale peut dépendre de lui.

⚠ `src/outils/spire_suivante.sh` expose `SORTIE_PAS`, `FENETRE_PIC`, `DEGAGEMENT`, `DISTANCE_MAX`
et n'écrit un réglage dans le JSON **que s'il est demandé** — c'est ce qui permet à
`table_chaine.py --comparer` de lire dans le `meta.json` si une campagne est compensée ou non,
au lieu de le déduire du nom du dossier.

### ⭐⭐⭐ RÉSULTAT DU 2026-08-21 (fin) — le pas du rayon a un OPTIMUM

Quatre campagnes d'enchaînement, comparées **à profondeur égale** (7 premiers tours) et
**sans aucun seuil** — que des α et des aires, jamais un compte de verdicts :

| pas du rayon | α moyen | α du pire tour | érosion/tour |
|---|---:|---:|---:|
| 1,0 | +0,357 | **+1,475** | 4,0 % |
| 0,5 | +0,129 | +0,583 | 4,0 % |
| **0,25** | ⭐ **+0,102** | ⭐ **+0,246** | 4,0 % |
| 0,125 | +0,327 | +0,758 | 4,0 % |

⭐ **Courbe en U sur un facteur 8.** Trop grossier et trop fin sont tous deux trois fois
pires, et 0,125 est presque aussi mauvais que 1,0. Donc « halver encore » n'est PAS la voie —
la prédiction « chaque halvage achète un tour » est réfutée.

⭐⭐ **Et l'érosion refuse de bouger** : 4,0 % par tour dans les quatre cas (12,8 à 13,0 % sur
l'aire *utile*), et l'écart entre nappes reste à 102–116 µm partout.

> **Le pas du rayon décide OÙ la surface se pose, pas combien elle en perd.**

⚠⚠ **Deux artefacts de comparaison, et ils allaient dans le sens de mes hypothèses.**
- L'érosion lue sur *toute* la longueur de chaque chaîne allait de 13,2 à 18,0 % et semblait
  suivre le pas. À profondeur égale : 12,8 à 13,0 %. **Toute la tendance était l'artefact de
  chaînes de longueurs différentes** — le même confondant que celui qui a réfuté « la rupture
  est une érosion ». D'où `geometrie_chaine.py --tours N` et `table_chaine.py --comparer`.
- J'ai supposé qu'un pas trop fin faisait s'arrêter le rayon **avant** la nappe suivante.
  Mesuré : 115 µm à pas 0,125, indistinguable des 113 et 114. **Réfuté.** À profondeur égale
  la tendance existe (116 → 102 µm) mais est minuscule. **Le mécanisme reste inconnu**, et
  les leviers non sondés sont `neighbor_max_distance`, `neighbor_threshold`,
  `neighbor_min_clearance`.

⚠ **Une revendication publiée le matin a été RETIRÉE le soir.** « Halver le pas repousse la
rupture d'un tour » reposait sur `pas025_spire07`, α = +0,702 pour un seuil de 0,700 — **deux
millièmes**, quand l'instrument ne discrimine pas à ±0,2 près. C'est ce qui a produit le
recensement de fragilité (10 verdicts sur 55) et la règle : **comparer des α, jamais des
comptes de franchissements de seuil.**

**Ajoutés le 2026-08-21 (soir)**
59. ⚠⚠ **Une provenance inventée est pire que la coquille qu'elle explique.** `44` a été
    écrite avec `@f$…@f$` pour ses maths en ligne, et les délimiteurs se sont affichés
    **littéralement** en plein milieu d'une phrase. Signalé par l'auteur, pas par un contrôle.
    ⚠⚠ **Ce qui compte n'est pas la coquille, c'est ce que j'ai raconté ensuite.** J'ai
    justifié l'erreur par « `@f$` est la syntaxe Doxygen, correcte dans `LplKernel_Book.md`
    parce que Doxygen la traite ». **Faux, et l'auteur l'a relevé.** Mesuré dans le livre :
    `@f$` y apparaît **zéro fois**, tandis que l'inline `$…$` y est utilisé **73 fois** et
    `$$…$$` **22 fois**. La syntaxe ne venait de nulle part dans cet espace de travail — je
    l'ai importée d'une habitude générale et je lui ai fabriqué une provenance plausible au
    lieu de la vérifier. Un `grep -c` de trois secondes aurait suffi.
    ⚠ Et j'ai enchaîné une deuxième erreur du même genre : mon premier grep a « trouvé » six
    documents de LplVesuvius en `$…$`, et j'ai écrit qu'il y avait une convention établie.
    C'étaient des **variables shell** (`$PWD`, `$SCROLL`) dans des blocs de code. Compter des
    motifs sans les lire.
    ⚠ Conséquence du diagnostic faux : j'ai replié toutes les maths en bloc « par prudence,
    faute de pouvoir vérifier l'inline ». La prudence portait sur une prémisse fausse — la
    convention existait, mesurable, avec 73 précédents dans le document phare du projet.
    **Convention à suivre, désormais mesurée** : inline `$…$`, display `$$…$$`, jamais `@f$`.
    ⭐ La règle générale : quand une erreur de syntaxe se corrige, **vérifier la convention
    plutôt que l'expliquer**. Une explication qui sonne juste est ce qui empêche de regarder.

## ⭐⭐⭐ 2026-08-22, soirée — le registre est vide, et α a perdu une certitude

### ✅ CE QUI TOURNAIT, et ce qui en est sorti

```bash
tail -f .lances/tracer_prediction_paris4-20260822-213653.log   # 12 cellules, ~5 min chacune
python3 src/encre/comparer_predictions.py --docs docs --json docs/mesures/paris4_2x2.json
```

Le **2×2 répété** : les deux prédictions de `PHercParis4` × les deux graines × **trois
tirages**, à 60 générations et à l'échelle 1. Il écrit ses verdicts dans
`docs/prediction_paris4_<prédiction>_sur_graine_<graine>_r<n>.json`, et l'instrument
ci-dessus les croise.

### ✅ TERMINÉ le 2026-08-22 au soir — 16 cellules, quatre tirages chacune

| | graine `ps256` | graine `m7` |
|---|---|---|
| **`ps256`** | médiane **+1,05**, étendue 0,18 | ⚠⚠ **4 indécidables** |
| **`m7`** | médiane **+0,99**, étendue 0,07 | ⚠⚠ **4 indécidables** |

⭐⭐ **Effet prédiction : 0,06**, loin sous le bruit de 0,20 — et il a **rétréci** depuis
0,17 en répétant, ce qui est le comportement d'une différence due au bruit. **Effet endroit :
catégorique**, les huit indécidables du même côté.

> ⭐ **Conclusion pratique** : il n'y a pas de prédiction à choisir, prendre l'une ou l'autre.
> Ce qui décide est la **graine**, et c'est là que l'effort doit aller. ⚠ Les deux α
> mesurables valent ≈ 1 : indistinguables *et* mauvaises à cet endroit.

⭐ **La première passe (un tirage par cellule) avait déjà conclu** — l'effet est **l'endroit**,
pas la prédiction : α = +1,12 et +0,95 à la graine de `ps256` (écart 0,17, **sous** le bruit
de 0,20), et les **deux** prédictions rendent un profil **plat** à la graine de `m7`. Les
répétitions servent à savoir si ce 0,17 tient : mesuré sur la première cellule, l'étendue
intra-cellule vaut déjà **0,89 à 1,12**, donc il est probable que non.

⚠ **Ce qu'il ne faut pas en conclure** : « les deux prédictions se valent ». Les deux α
mesurables valent **≈ 1**, donc elles sont indistinguables *et* mauvaises à cet endroit. La
suite utile n'est pas de choisir une prédiction — c'est de chercher une meilleure **graine**.

### Le registre de [`29`](docs/29_ce_qui_reste.md) est vidé de ce qui était actionnable

| | |
|---|---|
| **M7** | ✅ [`45`](docs/45_consistent_with_quantifie.md) — « consistent with » quantifié |
| **M8** | ✅ [`46`](docs/46_le_temoin_negatif.md) — le témoin négatif |
| **N1** | ✅ graines **et** tirages de `PHerc1203` : 13 rouleaux, 78 tirages, 5/13 bascules |
| **N3** | ✅ la troncature explique stabilité **et** propreté |
| **N4** | ✅ [`47`](docs/47_le_critere_doit_etre_relatif.md) — la question se dissout |

### Les quatre constats de la journée, du plus dur au plus fin

1. ⚠⚠⚠ **[`49`](docs/49_alpha_ne_separe_pas_deux_pannes.md) — α ≈ 1 a deux causes.** Un pic
   qui recule et un profil **plat** donnent le même verdict, et le second sort par identité
   arithmétique. Audit des **217 profils** : 20 séries sur 107 ne séparent pas les deux.
   ⭐ Mesuré : le plus petit α non discriminant vaut **+0,8729**, le plus grand α convergent
   **+0,4222** — **0 verdict positif n'est touché**, les deux populations ne se recouvrent
   pas. C'est la *formulation* qui sur-affirmait.
2. ⭐⭐ **[`46`](docs/46_le_temoin_negatif.md) — le modèle rend la même carte sur une feuille
   et sur une coupe en travers** (ρ = +0,9979, écart 2,9 % contre 95,4 % si étrangères), avec
   deux entrées distinctes de 11,0 %. La thèse forte est **hors de portée** (le détecteur est
   inerte ici, σ = 1,7 % de sa valeur utile) et l'instrument **refuse** de la conclure.
3. ⭐⭐ **[`48`](docs/48_ou_monter_lexperience.md) — traçable et lisible sont disjoints.**
   13 rouleaux contre 3, intersection **vide**. L'expérience « réparer sert-il ? » doit être
   montée sur `PHercParis4`. ⚠ Et le rendu à 2,4 µm coûte **plus de douze heures** par fenêtre
   à l'échelle 1 — mesuré sur `/proc/<pid>/io`, pas estimé.
4. ⭐ **[`04`](docs/04_experience_excision.md) recalculé** : U, p et δ reproduits exactement,
   plus une réserve neuve — le niveau 0 est du **vide** et pèse 3,4 % ; sans lui p = 0,504 et
   la conclusion **survit**.

### Ce qui a changé dans l'outillage, et qu'il faut connaître

- `test_convergence.py` a un chemin **`--profil`** : il lit l'écart, l'amplitude et la part au
  bord dans le même fichier, donc il peut **refuser**. Le préférer à `--serie`.
- `verifier_chiffres.py` a enfin **son propre auto-test** (`--verifier`), dit **où** vit une
  valeur périmée, et liste les documents dont **aucun** chiffre n'est gardé (7 sur ~50).
- `src/outils/rendre_surveille.sh` abandonne un rendu inactif **en rapportant son débit**.
- `src/outils/dossier_soumission.sh` rassemble ce qui part, la liste des figures **dérivée du
  texte**, et refuse un dossier incomplet.
- L'article fait **17 pages** et se reconstruit par `./docs/article/build.sh`.

## 9. Règles de mesure tenues ici

1. **Aucun seuil absolu** sur une grandeur physique — normaliser, ou être **ordinal**.
2. **Vérifier le confond avant de conclure.**
3. **Un contrôle qui ne peut pas échouer ne prouve rien** : témoin apparié + cas négatif.
4. **Mesurer d'abord, expliquer ensuite.** La lecture du code a produit une hypothèse
   fausse à chaque fois qu'elle a précédé l'instrument.
5. ⚠⚠ **Un chiffre publié dont le calcul n'est pas dans l'arbre n'est pas un résultat,
   c'est une anecdote.** Payé : l'onde radiale a dû être récupérée du transcript.
6. **Une idée testée et écartée est un actif** — à condition que la *raison* soit
   écrite. Quatre formulations des fusions, trois échecs, et c'est le troisième qui a
   désigné la bonne méthode.
7. **Rapporter la puissance avec un zéro** : « pas de corrélation » ne veut rien dire
   sans le rho que la taille d'échantillon permettait de détecter.
