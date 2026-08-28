# 58 — Résolution ou rouleau : ce n'est pas la résolution

> ⚠⚠ **Ce document ferme une des deux causes qui restaient à M1ter, et il commence par
> corriger le chiffre sur lequel la question reposait.**
> [`36`](36_lorigine_de_la_pile.md) §5bis a répondu « non » à *l'encre est-elle lisible à
> 9 µm ?* — sur `PHerc1447` le modèle du Grand Prize 2023 sort une constante, σ **45 fois**
> plus petit que là où il marche. Trois causes restaient : la résolution, ce rouleau-ci, ou
> un papyrus vierge. [`46`](46_le_temoin_negatif.md) §3 a fermé la troisième. Celle-ci tombe
> parce que **le témoin où le modèle marche est déjà à la résolution de `PHerc1447`**.

> ⚠⚠ **Sa prémisse d'entrée est tombée depuis, et son résultat tient quand même.** Le
> « facteur 45 à expliquer » venait d'un σ de 0,0171 qui mesurait une erreur d'échelle
> ([`60`](60_la_constante_qui_rendait_le_modele_muet.md)) : à l'échelle corrigée `PHerc1447`
> rend σ = 0,6558, et il n'y a plus de facteur 45. ⭐ **Ce que ce document mesure, lui, est
> intact** : son échelle de dégradation tourne sur les piles **uint16 publiées**, donc hors
> du bug, et ce qu'elle dit — ce que coûtent un doublement en plan et un doublement en
> profondeur, et le fait qu'ils s'aggravent — reste vrai et reste utile.

## 1. ⚠⚠ Le chiffre qui portait la question était faux

`36` §5bis oppose « Scroll 1, `20230909121925`, **2,4 µm** » à « `PHerc1447`, **8,64 µm** ».
La seconde valeur est le nom même du volume publié
(`20250521151220-8.640um-1.2m-116keV-masked.zarr`). La première ne vient de nulle part : elle
a été reprise de la campagne ESRF, qui produit bien des **volumes de surface** à 2,4 µm, mais
qui n'est pas ce que cette pile de couches est.

Mesuré le 2026-08-27, contre le dépôt public, en suivant la chaîne que le format impose —
un segment déclare son volume, un volume déclare son pas :

| | segment | volume déclaré | `voxelsize` |
|---|---|---|---:|
| Scroll 1 | `20230909121925` | `20230205180739` | **7,91 µm** |
| Scroll 4 | `20231111135340` | `20231107190228` | **3,24 µm** |

⭐ **Et le dépôt le savait déjà, ailleurs.** [`12`](12_profondeur_de_surface.md) §, table des
sommets de matière, écrit « **6 voxels (47 µm)** » pour ce même segment — soit 7,83 µm par
couche — et « ≥ 32 voxels (253 µm) » pour la pile de Scroll 4. Deux documents du même dépôt
disaient deux pas différents pour la même pile, et personne ne les avait mis côte à côte.

⚠⚠ C'est le piège que [`57`](57_les_taches_laissees.md) §1.1 a déjà payé — « 18 voxels »
qui pouvaient valoir 43 µm ou 142 µm — et son remède s'applique ici mot pour mot : **le
remède est dans le code, pas dans le document.** `src/encre/resolution_ou_rouleau.py` n'a
plus de constante de pas ; il **exige** `--voxel-um` et l'inscrit dans chaque rapport. Une
échelle est une propriété de la donnée, pas une valeur qu'un fichier se rappelle.

## 2. ⭐⭐⭐ Ce que ça change : les deux objets sont à la même résolution

Le mot « résolution » couvre deux grandeurs que la taille du voxel bouge **ensemble** — ce
qu'une tuile de 64 px couvre, et ce que 26 couches couvrent en profondeur. Avec le bon pas,
les deux sont à **9 %** l'une de l'autre :

| | Scroll 1, 7,91 µm | `PHerc1447`, 8,64 µm | rapport |
|---|---:|---:|---:|
| ce qu'une tuile de 64 px couvre | 506,2 µm | 553,0 µm | **1,092** |
| ce que 26 couches couvrent | 205,7 µm | 224,6 µm | **1,092** |
| **σ de la sortie du modèle** | **0,7712** | **0,0171** | **45,2** |

⭐⭐⭐ **Le modèle atteint AUC 0,925 dans les conditions de `PHerc1447`.** Ce n'est donc pas
la résolution qui l'éteint là-bas — il faudrait qu'un écart de 9 % produise un facteur 45.

Le reste de ce document mesure **combien** la résolution peut coûter, pour que la phrase
ci-dessus soit une quantité et non une intuition.

## 3. La méthode : dégrader ce qui marche, une grandeur à la fois

On ne peut pas rendre `PHerc1447` plus fin. On peut rendre **Scroll 1 plus grossier**.

⭐ **Le grossissement est une MOYENNE de bloc, jamais une décimation.** Un détecteur plus
grossier intègre sur sa cellule ; prendre un pixel sur *f* en jetant les autres ajoute un
repliement qu'aucun scan réel ne porte, donc ferait paraître la dégradation pire qu'elle
n'est et prouverait autre chose que ce qu'on demande.

⭐ **L'étendue de papyrus est identique à chaque barreau.** La fenêtre native fait
1008 × 1008 et c'est l'**entrée du modèle** qui rétrécit — 1008, 504, 336, 252 — jamais la
région lue. Deux barreaux qui liraient deux régions compareraient deux endroits.

⚠⚠ **Et le contrôle sans lequel l'échelle ne veut rien dire.** Moyenner réduit la variance
par construction : une carte plus grossière a un σ plus petit même si le modèle n'a rien
perdu. Chaque barreau est donc lu contre son **σ attendu** — celui qu'on obtient en
moyennant la carte du barreau natif par le même facteur, les pixels non couverts écartés et
non comptés comme des zéros. Le rapport mesuré / attendu sépare *« le modèle a perdu
l'encre »* de *« les pixels sont plus gros »*.

⚠ La fenêtre est choisie sur la carte d'encre **publiée** du même segment, comme celle des
1008 × 1008 où elle varie le plus (σ = 1,5036, `top=10080 left=2520`). Le choix ne favorise
aucun barreau — tous lisent la même — il garantit seulement que l'échelle a quelque chose à
perdre. C'est aussi pourquoi le σ natif d'ici (**1,5202**) vaut le double du σ publié sur le
segment entier (0,7712) : une fenêtre choisie pour son encre varie plus que la moyenne d'un
segment. Les rapports entre barreaux, eux, ne dépendent pas de ce choix.

## 4. ⭐ Ce que coûte l'échantillonnage en plan

Scroll 1, segment `20230909121925`, profondeur maintenue à 205,7 µm à chaque barreau.

| | tuile de 64 px | entrée | **σ** | σ attendu | mesuré / attendu |
|---|---:|---:|---:|---:|---:|
| 7,91 µm (natif) | 506 µm | 1008 px | 1,5202 | 1,5202 | 1,000 |
| 15,82 µm | 1 012 µm | 504 px | 1,4352 | 1,5194 | **0,945** |
| 23,73 µm | 1 519 µm | 336 px | 0,9200 | 1,5195 | **0,605** |
| 31,64 µm | 2 025 µm | 252 px | 0,4118 | 1,5176 | **0,271** |

⭐ **Le moyennage n'explique rien.** Le σ attendu passe de 1,5202 à 1,5176 — **0,17 %** —
parce qu'une carte d'encre est lisse à l'échelle du pixel (la sortie 4 × 4 du modèle est
remontée en 64 × 64 par interpolation, puis cumulée). La chute mesurée à 31,64 µm est de
**72,9 %**. Quand le modèle perd l'encre, il la perd vraiment ; c'est le contrôle qui rend
la ligne suivante lisible.

⭐⭐ **Doubler l'échantillonnage coûte 5,6 %.** Or l'écart réel entre Scroll 1 et
`PHerc1447` est de 9 %, soit **un neuvième d'un doublement**.

## 5. ⭐⭐ Ce que coûte l'épaisseur de la fenêtre — huit fois plus

⚠ Il faut un autre objet : Scroll 1 ne publie que 26 couches, donc son épaisseur ne peut pas
varier. `scroll4_20231111135340` en publie **65** à 3,24 µm, ce qui permet un pas de couches
de 1 ou de 2 — 84,2 µm contre 168,5 µm. Le modèle y répond (σ = 0,8258).

⭐ **Chaque barreau est CENTRÉ sur la même couche**, jamais aligné sur son bord : à départ
fixe, deux pas partagent leur bord proche et le barreau épais irait chercher sa matière
ailleurs dans l'empilement — on comparerait deux régions de la feuille plutôt que deux
épaisseurs de la même. C'est la contrepartie exacte, en profondeur, de l'étendue commune du
§3.

Les quatre combinaisons, même fenêtre, même centre, même segment :

| en plan | en profondeur | **σ** | rapport au natif |
|---:|---:|---:|---:|
| 3,24 µm | 84,2 µm | 0,8258 | 1,000 |
| 6,48 µm | 84,2 µm | 0,8232 | **0,997** |
| 3,24 µm | 168,5 µm | 0,4887 | **0,592** |
| 6,48 µm | 168,5 µm | 0,4078 | **0,494** |

⭐ **À facteur égal, doubler la profondeur coûte 40,8 % et doubler le plan coûte 0,3 %.**
C'est la grandeur que personne n'avait isolée qui est de loin la plus destructrice.

## 6. ⭐⭐ Et elles ne s'additionnent pas : elles s'aggravent

La prédiction d'indépendance était écrite avant de lancer le quatrième barreau :
0,997 × 0,592 = **0,590**. Le mesuré est **0,494**, soit **1,195 fois pire** que ce que
l'indépendance annonce.

⭐⭐ **Dit autrement : doubler l'échantillonnage en plan coûte 0,32 % quand la fenêtre de
profondeur est juste et 16,6 % quand elle est déjà doublée — cinquante fois plus.** Un
grossissement en plan est presque gratuit tant que le modèle voit la bonne épaisseur, et
devient cher dès qu'il ne la voit plus. C'est aussi pourquoi les deux moitiés de
« résolution » ne se lisent pas séparément dans un σ isolé.

## 7. ⭐⭐⭐ Le compte, et il n'est pas serré

Créditons la résolution du coût **entier d'un doublement sur les deux axes** — c'est-à-dire
environ **dix fois** l'écart réel de 9 % — en prenant sur chaque axe la perte la **plus
forte** qu'on ait mesurée, fût-ce sur deux objets, et en leur appliquant en plus la pénalité
d'interaction du §6 :

| | facteur de σ |
|---|---:|
| un doublement en plan (Scroll 1, le plus coûteux des deux objets) | 0,944 |
| un doublement en profondeur (Scroll 4) | 0,592 |
| … et leur interaction, qui aggrave d'un facteur 1,195 | |
| **le compte le plus généreux qu'on puisse faire** | **0,468** |
| **ce qu'il faudrait expliquer** | **0,022** (= 1 / 45,2) |

⭐⭐⭐ Même en lui offrant dix fois l'écart qu'elle a, sur les deux axes, avec la pénalité
d'interaction par-dessus, la résolution rend un facteur **2,1** là où il en faut **45**.
**Elle est éliminée**, et pas de justesse.

⚠ La ligne « plan » et la ligne « profondeur » viennent de deux objets différents, et c'est
délibéré : on prend sur chaque axe le coût le plus élevé qu'on ait su mesurer, ce qui rend le
compte **favorable à l'hypothèse qu'on écarte**. Un compte défavorable qui conclut est un
compte qu'on n'a pas besoin de discuter.

## 8. Ce que ça ferme, et ce qui reste

| | verdict |
|---|---|
| papyrus vierge | ✅ fermé par [`46`](46_le_temoin_negatif.md) §3 |
| **résolution**, ses deux moitiés | ✅ **éliminée** : les deux objets sont à 9 % l'un de l'autre sur les deux axes, et dix fois cet écart ne rend qu'un facteur 2,1 sur 45 |
| **ce rouleau-ci** | ⚠ **seule cause en lice — et NON TESTABLE** avec le corpus publié : zéro rouleau porte une vérité terrain exploitable (voir juste dessous) |

> ⚠⚠⚠ **DEUX RÉSERVES AJOUTÉES LE 2026-08-28** → [`65`](65_ce_que_sigma_ne_dit_pas.md).
> **(1)** L'élimination ci-dessus est menée sur des **rapports de σ**, et rien n'avait vérifié
> qu'un σ élevé veut dire que le modèle lit. Testé une fois, contre de vraies étiquettes : σ
> arrive quatrième sur six grandeurs et ne tranche pas (p de Holm = 0,739).
> **(2)** Le chiffre de `63` — 0,686 d'AUC à 9,72 µm — ne peut **pas** être cité comme preuve
> que la résolution ne coûte rien : avec son intervalle, la lisibilité à 9,72 µm n'est **pas
> établie** ([0,455 ; 0,745], qui contient 0,5), et un balayage de maille montre que cette
> carte ne peut pas trancher.
> ⚠ Ni l'une ni l'autre ne **renverse** ce tableau : `58` compare deux objets réels à 9 % l'un
> de l'autre, `65` décime un seul objet d'un facteur 3. Ce sont deux questions. Mais l'argument
> ne peut plus être avancé sans ces deux lignes.

> ⚠⚠⚠ **ET CETTE CAUSE N'EST PAS TESTABLE AVEC LE CORPUS PUBLIÉ — établi par énumération le
> 2026-08-28** → [`59`](59_la_campagne_plutot_que_le_rouleau.md), relevé
> [`ou_la_verite_existe.json`](mesures/ou_la_verite_existe.json). Éprouver « c'est ce
> rouleau-ci » demande de **mesurer la lecture sur un rouleau**, et
> [`src/encre/ou_la_verite_existe.py`](../src/encre/ou_la_verite_existe.py) compte **zéro
> rouleau mesurable** sur cinq interrogés : quatre ne publient **aucune** étiquette d'encre,
> et `Scroll1` en a mais c'est le **jeu d'entraînement** du modèle, donc y mesurer une AUC ne
> dit rien. Seuls **4 fragments** sont mesurables.
>
> ⭐ **La condition qui rouvrirait la question est nommée, et se re-vérifie en une commande** :
> des étiquettes d'encre publiées sur un rouleau que `timesformer_GP_scroll1` n'a pas vu. Le
> jour où quelqu'un les publie, `ou_la_verite_existe.py` le dira.
>
> ⚠ Et ce n'est pas « le modèle ne lit pas sur un rouleau ». C'est qu'on ne peut pas le
> mesurer — deux énoncés différents, et les confondre serait la conclusion que ce dépôt refuse.
> ⚠⚠ À quoi s'ajoute [`65`](65_ce_que_sigma_ne_dit_pas.md) : le substitut employé jusqu'ici,
> σ, **ne prédit pas** la qualité mesurée (quatrième sur six grandeurs, p de Holm 0,739).

⚠ **Ce que ce document n'établit pas** : qu'il y ait ou non de l'encre sur `PHerc1447`. Il
dit que l'instrument ne perd pas sa réponse pour une raison d'échelle. Ce que « le rouleau »
recouvre — l'état de conservation, la chimie de l'encre, l'énergie du faisceau, la surface
tracée — reste à découper, et ce découpage-ci est le patron à suivre : rendre l'objet qui
marche semblable à celui qui ne marche pas, une propriété à la fois.

> ⚠⚠⚠ **ET UNE CONDITION PRÉALABLE, chiffrée le 2026-08-28** →
> [`64`](64_la_dispersion_netait_pas_un_effet.md). « Une propriété à la fois » suppose qu'on
> puisse voir l'effet d'une propriété, et la mesure dit de combien : l'AUC d'une tuile de
> 256 px varie d'un écart-type de **0,2243** d'une tuile à l'autre du **même** objet, au
> **même** réglage. Un écart de 0,10 demande donc **79 tuiles par condition**, un écart de
> 0,05 en demande **316** — et ce sont des minorants, la formule supposant des tuiles
> indépendantes. ⚠⚠ Le premier essai de ce patron (`63`, trois fragments) avait **10, 11 et
> 2** tuiles : il était de deux à treize fois trop petit, et l'écart qu'il rapportait n'était
> pas établi. Toute application future du patron se dimensionne **avant**, et se fait
> **appariée** — les deux conditions sur les **mêmes** tuiles — parce que c'est le seul moyen
> de retirer la variance qui domine tout le reste.

⚠ Et une borne sur l'émulation : elle **conserve le détail en profondeur** qu'un vrai scan
plus grossier n'aurait pas, puisqu'un voxel plus large intègre aussi dans cette direction.
Les σ du §4 sont donc un **majorant** de ce qu'un vrai scan grossier rendrait — ce qui va
dans le sens de la conclusion, puisque le §7 crédite déjà la résolution du coût plein d'un
doublement sur les **deux** axes, mesuré séparément.

## 8 bis. ⚠⚠⚠ L'axe que ce document n'avait pas nommé : l'énergie du faisceau

Ajouté le 2026-08-28. Ce document compare les deux objets sur la **résolution**, l'axe qu'il
élimine, et ne dit nulle part ce qu'ils valent sur les deux autres grandeurs que leur scan
porte. Le dépôt public les déclare, et l'écart n'est pas du même ordre :

> ⚠⚠⚠ **CORRECTION DU 2026-08-29 : « l'énergie » N'EST PAS UN AXE ISOLÉ, et ce tableau le
> laisse croire.** L'index du dépôt (`metadata.min.json`) porte la **distance de propagation**
> dans l'identifiant long de chaque scan, et je ne l'avais jamais lue. Les deux objets ne
> diffèrent pas d'une grandeur mais de **trois qui bougent ensemble** :
>
> | | témoin qui marche | objet qui échoue |
> |---|---|---|
> | identifiant | `20230205180739-7.910um-54keV` | `20250509011039-8.640um-1.2m-116keV` |
> | distance de propagation | **absente de l'identifiant** (ESRF 2023) | **1,2 m** |
>
> ⚠⚠ Et ce n'est pas une coïncidence de ces deux-là : dans tout le corpus, **les 31 scans à
> 1,2 m** sont ceux de la campagne 8,64/9,36 µm à 113–116 keV. Énergie, distance et taille de
> voxel **ne varient pas indépendamment** — c'est une **campagne de scan**, pas un réglage.
>
> ⭐ Le site du prix le dit dans ses termes, page *2026 open problems* : « **Three coupled
> scan parameters** » — taille de voxel, distance de propagation, énergie — et « *enough X-ray
> energy to penetrate the object and separate layers; not so much that useful absorption
> contrast disappears* ». La formulation de [`59`](59_la_campagne_plutot_que_le_rouleau.md),
> « la campagne plutôt que le rouleau », visait donc juste dans sa **forme** ; ce qui lui
> manquait était un moyen de l'établir, pas l'idée.
>
> Relevé : [`corpus_par_energie.json`](mesures/corpus_par_energie.json).
>
> ⚠⚠⚠ **ET LE 2026-08-29, PLUS GRAVE : cet axe est CONTREDIT par une ablation contrôlée
> publiée** → [`66`](66_audit_danteriorite.md) §3. Le papier de référence du prix
> (`data/site/scrollprize.org/pdf/main.pdf`, Angelotti et al., Extended Data Fig. 2) publie un
> balayage 4 × 4 énergie × distance et conclut : « *for a pixel size of about 8 µm the empiric
> **sweet spot** for the energy is between **100 and 120 keV*** ». Les **116 keV** de
> `PHerc1447` sont donc **dans** la fenêtre optimale publiée pour sa résolution.
>
> ⚠⚠ **Et le 114,8 % tenait au choix du témoin.** Le seul volume de `PHercParis4` portant une
> prédiction d'encre publiée est à **2,4 µm / 78 keV**, pas 7,91 µm / 54 keV — contre lui,
> l'écart en énergie tombe à ~48 % et celui en résolution monte à ~260 %, ce qui **inverse le
> classement des axes**. Ce tableau compare donc `PHerc1447` à un scan de 2023 que le pipeline
> actuel n'utilise plus.
>
> ⭐ La leçon générale : un **écart relatif** large sur un paramètre ne prouve pas qu'il est le
> facteur limitant. Il faut la **sensibilité**, pas la distance — et la sensibilité mesurée sur
> l'axe énergie est faible (« *the contrast drop is visible but gentle* »).

| grandeur | témoin qui **marche** | objet qui **échoue** | écart |
|---|---:|---:|---:|
| pas de voxel | 7,91 µm | 8,64 µm | **9,2 %** |
| **énergie du faisceau** | **54 keV** | **116 keV** | **114,8 %** |

Le témoin est `PHercParis4 54keV stitched_part_1` (`meta.json` du volume `20230205180739`,
qui déclare `voxelsize 7.91`) ; l'objet est
`8.64um-1.2m-116keV-volume-20250521151220`. Instrument :
[`src/encre/deux_objets.py`](../src/encre/deux_objets.py) (11 contrôles),
mesure : [`docs/mesures/deux_objets.json`](mesures/deux_objets.json).

⭐⭐ **Neuf pour cent d'un côté, cent quinze de l'autre.** « Ce rouleau-ci » n'est donc pas
le seul suspect qui reste : la **campagne de scan** en est un, et elle a une propriété que le
rouleau n'a pas — elle **s'achète**. Un rouleau ne change pas ; un scan, si.

⚠⚠⚠ **Ce que ça n'établit PAS, et il faut le répéter à chaque usage.**
[`59`](59_la_campagne_plutot_que_le_rouleau.md) a déjà mesuré que les trois grandeurs
**co-varient par campagne** — un scan fin est aussi à courte propagation et à basse énergie —
et que restreinte aux rouleaux réellement tentés, la séparation par campagne tombe à
**p = 0,50**. Ce tableau **ne sépare rien** : il chiffre l'écart sur chaque axe pour la paire
que M1ter oppose, ce que personne n'avait fait, et il déplace un suspect de « innommé » à
« nommé et mesuré ».

⚠ Isoler l'énergie demande de suivre le patron du §8 — rendre l'objet qui marche semblable à
celui qui ne marche pas, une propriété à la fois. Et l'émulation d'énergie **n'est pas une
décimation** : une énergie plus haute ne floute pas, elle change les coefficients
d'atténuation différemment selon le matériau, donc le contraste encre/papyrus. Ce qui est
émulable honnêtement est donc le **contraste mesuré**, pas « l'énergie » — et il faut le dire
ainsi, sinon on croirait avoir simulé un faisceau.

## 8 ter. ⭐⭐⭐ Ce que l'écart d'énergie fait au SIGNAL : 24 %, et ça referme la branche

Mesuré le 2026-08-28, dans la foulée du §8 bis. Chiffrer l'écart des campagnes ne dit rien
tant qu'on ne sait pas ce qu'il fait à ce que le modèle **reçoit**. Contraste dans le
papyrus, chaque pile normalisée par le plafond de **son** type — la règle de
[`60`](60_la_constante_qui_rendait_le_modele_muet.md), sans laquelle on comparerait deux
formats :

| | type | papyrus | σ | interquartile | p95 − p50 |
|---|---|---:|---:|---:|---:|
| témoin, **54 keV** | `uint16` | 100 % | 0,1676 | 0,2742 | 0,2264 |
| objet, **116 keV** | `uint8` | 88 % | 0,1349 | 0,2235 | 0,1765 |
| **rapport** | | | **1,243** | **1,227** | **1,283** |

⭐ Les trois mesures s'accordent : **115 % d'écart d'énergie ne produit que 24 % d'écart de
contraste**. C'est la même forme d'argument que le §7 employait pour la résolution, et elle
conclut dans le même sens.

### ⭐⭐⭐ Et la coïncidence qui referme la branche

| | rapport |
|---|---:|
| **contraste reçu** par le modèle (mesuré ici) | **1,243** |
| **σ rendu** par le modèle (0,7712 / 0,6558, cf. `60`) | **1,176** |
| écart entre les deux | **5,4 %** |

⚠⚠ **La réponse du modèle suit le contraste qu'il reçoit, presque un pour un.** Il n'y a donc
pas de résidu à expliquer sur cet axe : le 1,2× de sortie que `60` mesure est *exactement* ce
qu'on attend d'un objet dont le contraste d'entrée est 1,24 fois plus faible. La campagne de
scan est chiffrée, son effet sur le signal est chiffré, et les deux se referment l'un sur
l'autre.

### ⚠ Ce que ça ne dit pas, et ce qu'il faut avoir en tête

1. C'est le contraste de **tout le papyrus**, pas celui de l'**encre** — on ne sait pas où
   elle est sur `PHerc1447`, c'est la question même. Un contraste global effondré rendrait un
   contraste d'encre effondré probable ; l'inverse ne suit pas.
2. **Il n'y a plus de facteur 45 à expliquer.** `60` l'a annulé, et ce document l'écrit dans
   sa propre table de conséquences. Ce §8 ter ne comble donc pas un trou béant : il ferme
   proprement une branche qui aurait pu rester ouverte par inertie, et il le fait par une
   mesure au lieu d'un argument.
3. Les deux piles ne viennent pas du même endroit — un rendu `tifxyz` `uint16` d'un côté, le
   volume de surface **publié** en `uint8` de l'autre. ⚠ Vérifié à la source : le `.zarray`
   du dépôt déclare `|u1`, donc les huit bits sont ceux de la campagne et **non de notre
   pont**, qui écrit les couches telles quelles. C'est une différence entre les deux objets,
   pas un artefact de notre chaîne.

Instrument : [`src/encre/contraste_des_objets.py`](../src/encre/contraste_des_objets.py)
(15 contrôles), mesure :
[`docs/mesures/contraste_des_objets.json`](mesures/contraste_des_objets.json).

## 8 quater. ⭐⭐⭐ Le plan d'expérience existe déjà, et il n'y a rien à émuler

Trouvé le 2026-08-28, en corrigeant l'angle mort de
[`59`](59_la_campagne_plutot_que_le_rouleau.md). Le §8 pose le patron — *rendre l'objet qui
marche semblable à celui qui ne marche pas, une propriété à la fois* — et le §8 ter conclut
qu'isoler l'énergie demanderait d'**émuler** un contraste, faute de mieux.

**Faute de mieux était faux.** Les six fragments du dépôt public, dans le layout
`fragments/` que `campagnes_de_scan.py` n'interroge pas, sont un plan d'expérience contrôlé
déjà scanné :

| fragment | volumes | ce que la paire isole |
|---|---|---|
| `Frag1` à `Frag4` | 54 et 88 keV, **tous deux à 3,24 µm** | **l'énergie**, la résolution tenue |
| `Frag5` | 70 keV, **3,24 et 7,91 µm** | la résolution, l'énergie tenue |
| `Frag6` | 53, 70 et 88 keV à 3,24 µm **+** 53 keV à 7,91 µm | **trois** paires d'énergie et une de résolution |

**7 paires isolent l'énergie, 2 la résolution.** Instrument :
[`src/encre/paires_denergie.py`](../src/encre/paires_denergie.py) (18 contrôles), relevé :
[`docs/mesures/paires_denergie.json`](mesures/paires_denergie.json).

⭐⭐ **Le même objet, scanné aux deux énergies, au même pas.** Il n'y a donc rien à émuler :
là où le §7 a dû **décimer** pour la résolution, l'énergie se lit sur deux scans réels du
même fragment. Et ces fragments portent une **vérité terrain d'encre** — leur surface ouverte
est publiée (`working/54keV_exposed_surface/`), ce sont ceux du concours de détection.

### ⚠⚠⚠ CORRECTION du même jour : les paires existent, mais pas *utilisables ensemble*

Écrit ci-dessus, puis vérifié fragment par fragment. Le corpus se sépare en **deux moitiés
disjointes**, et aucune ne suffit seule :

| fragment | étiquettes d'encre | transformation de recalage | paires |
|---|:--:|:--:|---|
| `Frag1` | ✅ `inklabels.png` | ❌ `transforms/` vide | 54 / 88 keV |
| `Frag2` | ✅ | ❌ vide | 54 / 88 keV |
| `Frag3` | ✅ | ❌ vide | 88 / 54 keV |
| `Frag4` | ❌ | ❌ vide | 54 / 88 keV |
| `Frag5` | ❌ | ✅ **1 transformation** | 3,24 / 7,91 µm |
| `Frag6` | ❌ | ✅ **3 transformations** | 53 / 70 / 88 keV **+** 3,24 / 7,91 µm |

⚠⚠ **Les fragments qui ont la vérité terrain n'ont pas de recalage, et celui qui a le
recalage complet n'a pas de vérité terrain.** Or les deux volumes d'une paire n'ont pas la
même forme — `Frag1` fait 7219 × 1399 × 7198 à 54 keV et 7229 × 1608 × 7332 à 88 — donc les
coordonnées de surface de l'un **n'indexent pas** l'autre. ⚠ Et `volumes_standardized/` ne
recale rien : c'est la même forme en `uint8`, une normalisation d'intensité, pas une
transformation spatiale.

⭐ Ce qui reste vrai du §8 quater : les paires **existent** et une comparaison de statistiques
par énergie est faisable sur `Frag6` (trois énergies recalées, sans labels), tandis qu'une
mesure **contre étiquettes** est faisable à une seule énergie sur `Frag1` à `Frag3` — ce qui
est exactement ce que [`63`](63_la_premiere_verite_terrain.md) a fait.

⚠ Ce qui tombe : « il n'y a rien à émuler ». Pour comparer **la même surface** aux deux
énergies avec des étiquettes, il faut un recalage que personne ne publie pour les fragments
étiquetés. Le produire est un lot à soi — un recalage rigide 3D sur des volumes de sept mille
voxels de côté — et il introduirait sa propre source d'erreur dans une mesure censée en
isoler une seule.

⚠ Ce que ça ne fait pas encore : rendre et comparer. Ce lot demande de télécharger des
volumes que ce dépôt n'a pas, et c'est le pas suivant. Ce §8 quater établit que le pas est
**possible sur `Frag6`, sans étiquettes**, ce qui n'était pas acquis il y a une heure — et la
correction ci-dessus dit pourquoi il ne l'est pas avec elles.

## 9. ⭐ Deux contrôles de reproductibilité, gratuits et exacts

Les trois campagnes se recouvrent par construction, et les recouvrements doivent coïncider
**au bit près** — ce sont les mêmes couches, la même fenêtre, le même centre :

| | σ |
|---|---:|
| échelle profondeur, pas 1 | 0,825755 |
| échelle croisée `--pas-couches 1`, plan ×1 | 0,825755 |
| échelle profondeur, pas 2 | 0,488698 |
| échelle croisée `--pas-couches 2`, plan ×1 | 0,488698 |

⚠ Ce n'est pas une élégance : deux chemins de code atteignent ces piles — l'un passe par
l'axe profondeur, l'autre par l'option `--pas-couches` de l'axe plan — et un désaccord au
dernier chiffre aurait dit que l'un des deux ne lit pas les couches qu'il annonce.

## 10. ⚠⚠ Le détour : l'outil ne tournait plus du tout

Cette mesure a commencé par ne pas pouvoir démarrer. `src/xpu/infer_ink.py` porte les poids
dans `data/models/`, valide ses arguments, puis mourait sur un `ModuleNotFoundError` nu :
`torch`, `transformers` et `timesformer_pytorch` n'étaient **dans aucun groupe de
dépendances**. Trois faits sont sortis de la réparation, et chacun n'est apparu qu'en
exécutant :

1. `timesformer_pytorch` n'apparaît dans **aucun de nos imports** — c'est le code du modèle,
   chargé par `trust_remote_code`, qui le demande. Ne lister que les imports visibles rendait
   un remède qui répare la moitié de la panne.
2. `transformers` doit être **borné sous 5**. La 5.16 exige de tout `PreTrainedModel` un
   attribut `all_tied_weights_keys` que ce modèle, écrit pour 4.46.3 comme son `config.json`
   le déclare, n'a pas : le chargement meurt sur un `AttributeError` **après** avoir installé
   3,8 Gio.
3. L'index de roues par défaut tire **2,7 Gio de runtime CUDA** à côté de 1,1 Gio de torch,
   sur une machine sans périphérique CUDA. L'index CPU ramène l'environnement de **4,9 Gio à
   1,2 Gio**.

⚠⚠ Et `uv sync` a **désinstallé 19 paquets** — `zarr`, `fsspec`, `s3fs` et leur suite — que
quatre outils de `src/excision/` importent *à l'intérieur de leurs fonctions*, et qu'aucun
fichier ne déclarait. Ils étaient là parce que quelqu'un les y avait posés à la main. Un
environnement reproductible qui ne survit pas à sa propre commande de synchronisation n'est
pas reproductible, et la panne ne se voit que le jour où on relit un volume.

## Reproduire

```bash
uv sync --extra encre --extra volume      # sans ça, l'outil REFUSE en nommant ce qui manque

# §1 — le pas des couches, lu chez celui qui le déclare
curl -s https://dl.ash2txt.org/full-scrolls/Scroll1/PHercParis4.volpkg/paths/20230909121925/meta.json
curl -s https://dl.ash2txt.org/full-scrolls/Scroll1/PHercParis4.volpkg/volumes/20230205180739/meta.json

# §4 — l'axe en plan, sur le rouleau où le modèle marche
uv run python src/encre/resolution_ou_rouleau.py data/layers/20230909121925 \
    --model data/models/timesformer_GP_scroll1 --voxel-um 7.91 \
    --carte-publiee data/out/ink_segment_complet.npy \
    --sorties data/controle_resolution/plan \
    --json docs/mesures/m1ter_resolution_en_plan.json

# §5 et §6 — la profondeur, puis les deux croisées, sur les 65 couches de Scroll 4
uv run python src/encre/resolution_ou_rouleau.py data/layers/scroll4_20231111135340 \
    --model data/models/timesformer_GP_scroll1 --voxel-um 3.24 --axe profondeur --facteurs 1,2 \
    --centre-couche 32 --cote 504 --top 2500 --left 8000 \
    --sorties data/controle_resolution/profondeur \
    --json docs/mesures/m1ter_profondeur.json
for PC in 1 2; do
  uv run python src/encre/resolution_ou_rouleau.py data/layers/scroll4_20231111135340 \
      --model data/models/timesformer_GP_scroll1 --voxel-um 3.24 \
      --axe plan --facteurs 1,2 --pas-couches $PC \
      --centre-couche 32 --cote 504 --top 2500 --left 8000 \
      --sorties data/controle_resolution/croise_pc$PC \
      --json docs/mesures/m1ter_croise_pc$PC.json
done

# Refaire un rapport a partir des seules cartes deja rendues, sans modele ni couche
uv run python src/encre/resolution_ou_rouleau.py --depuis data/controle_resolution/plan \
    --voxel-um 7.91
```

⚠ La fenêtre de Scroll 4 (`top=2500 left=8000`) a été trouvée en sondant trois candidats à
`left` 8 000, 20 000 et 32 000 : seule la première rend une étendue franche
(−1,813 à +1,257 contre −1,805 à −1,153). Une échelle posée sur une fenêtre sans encre
mesurerait la platitude de la fenêtre.
