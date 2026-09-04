# 73 — Seconde passe : ce que le dépôt change à `docs/69`

> Rédigé le 2026-09-03 en réponse au second prompt (« lis ce qu'on a fait, et dis-nous ce que
> ça change »). Quatre livrables, dans l'ordre demandé, et rien d'autre. Même convention de
> marquage que `69` : **[établi]** (lu dans un fichier cité), **[calculé]**
> (`docs/mesures/69_arithmetique.py`, section `docs/73`), **[conjecture]**, **[je ne sais pas]**.
>
> ⚠ Le cadrage manquant de `HANDOFF` §0–1 — *le but est le déroulement, l'encre est la règle
> graduée* — est pris comme contrainte dure. Là où `69` mettait la physique au mois 1, ce
> document dit combien de temps la règle mérite, et pourquoi ce n'est pas zéro.

---

## 0. Ce qui a été lu, et trois vérifications faites en plus

Lus en entier : `docs/article/article.typ` (1535 lignes), `70`, `71`, `72`, `17`, `65`, `64`,
la tête de `07`, `46` §1–3 ter, `51` §1–5, `src/excision/laxe_nest_pas_une_ligne.py`,
`HANDOFF` REPRISE. Lus par leur fiche (`registres/fiches_de_lecture.md`) : `09`, `11`, `14`,
`16`, `20`, `26`, `33`, `41`–`45`, `49`, `55`.

Trois choses que les fiches ne disaient pas, vérifiées à la source parce que les livrables en
dépendent :

| vérification | résultat | où |
|---|---|---|
| que comptent les « croisements » contre lesquels `17` a testé la phase ? | des **auto-intersections** : `windcheck` se présente comme *« Self-intersection checks for Herculaneum surface traces »*, et son `index.json` porte `events`, `crossing_status` | `data/repos/windcheck/README.md`, `results/index.json` |
| les segments publiés portent-ils leur **numéro de spire** ? | **oui, dans leur nom** : `PHerc1667` publie `w011`…`w041` (20 segments), `PHerc0139` `w023`…`w059` (37 + `title`). `PHerc1447` et `PHerc0800` ne publient que des `auto_grown_*` | `data/metadata.min.json`, champ `suffix` |
| un masque d'approbation est-il publié à côté des `x/y/z.tif` ? | **non** : `tifxyz_original/` de `0139 w046` et `tifxyz_flattened/` de `1667 w032` ne contiennent que `meta.json`, `x.tif`, `y.tif`, `z.tif` | listage S3 du 2026-09-03 |

**[établi]** aussi : la carte dense de séparabilité existe pour les treize
(`docs/carte_separabilite_dense/*.json`, 57 à 115 fenêtres par rouleau) et son classement par
la queue (`part_sous_1`) est `PHerc0800` 2,6 % < `PHerc1447` 7,0 % < `PHerc1218` 8,8 % <
`PHerc1203` 9,1 % < … < **`PHerc0826` 22,8 %**.

---

## 1. Livrable 1 — H1 à H7 révisées contre ce que le dépôt a mesuré

| | verdict | ce qui tranche |
|---|---|---|
| H1 spectre d'AUC | **déjà répondue à moitié, sous-dimensionnée, et rétrogradée** | `65` §2, `64` §5 |
| H2 débinage | **inchangée, déclassée en courriel** | `68` §4 (case vide) |
| H3 décohérence locale | **morte comme instrument, vivante comme prédicteur sans référent** | `16`, `33`, `carte_separabilite_dense/` |
| H4 régions ambiguës | **inchangée ; référent disponible sous une autre forme** | listage S3, `44`, `51` |
| H5 résidus ↔ sauts | **inchangée sur le fond ; son test change de référent** | `17`, `windcheck/README.md`, noms `w0NN` |
| H6 prior universel | **déjà répondue, et elle corrige ma recommandation** | `winding-ruler`, `16`, `33`, carte dense |
| H7 verso témoin nul | **inchangée, non testée, rendue plus urgente par `46`** | `46` §3 |

### H1 — *l'évidence d'encre survit à la bande perdue*

**Déjà répondue à moitié**, sur `PHercParis2Fr47` contre les `inklabels` : AUC groupée
0,746 → 0,693 → 0,686 pour 3,24 → 6,48 → 9,72 µm, moyennes de tuiles 0,674 → 0,594 → 0,599
**[établi]** (`65` §2). Les points bougent peu — c'est le sens de H1. Mais les trois
intervalles par tuiles contiennent ou frôlent 0,5, et à 9,72 µm la largeur reste à ~0,20 quelle
que soit la maille (`65` §2, tableau 3×3 → 8×8) : **l'expérience ne peut pas trancher sur
cette carte**, et ce n'est pas le découpage qui manque, c'est la surface.

**Combien de tuiles.** Avec σ = 0,2243 (`64` §1) **[calculé]** : séparer l'AUC à 9,72 µm
(0,599) de 0,5 demande **40 tuiles** à une condition ; séparer 3,24 µm de 9,72 µm (écart
0,075) demande **140 tuiles par condition**. Le contrôle du calcul rend 27 pour l'écart de
0,171 de `64`. Ce sont des minorants : les tuiles voisines ne sont pas indépendantes. On en
avait 10, 11 et 2.

⚠ Et la mesure de `65` est une **décimation**, qui conserve le détail en profondeur qu'un vrai
scan n'aurait pas — un majorant (`65` §3). La seule mesure qui réponde est la case vide de
`68` §4 : les couches **natives** à 9,362 µm de `PHerc0500P2`, 38 segments, avec au moins
40 tuiles de 256 px — soit 2,3 cm² de fragment encré, ce que 38 segments permettent.

**Ce que le cadrage en fait** : H1 n'est plus une hypothèse sur le prix, c'est **l'étalonnage
de la règle**. Elle mérite ce que coûte une mesure faite une fois avec assez de tuiles — deux
semaines, dans le budget du §3 — et pas un mois.

### H2 — *le débinage ne rend presque rien*

**Inchangée** : aucun document ne compare 4,317 µm / 1,2 m à 9,362 µm / 1,2 m sur le même
objet, et la case du `68` §4 reste vide. **Déclassée** : côté règle. Ce qui reste est un
**courriel** à l'ESRF, ~~dont le coût est nul~~, avec un argument que `69` n'avait pas donné et
qui est géométrique : à 4,7 µm une feuille fait 8 à 10 voxels au lieu de 4 à 5, donc la
séparabilité `d′` de `16` monterait pour les treize — au prix de ×8 en volume (20 To → 160 To),
que le lecteur à distance de `volume/` absorbe par fenêtres. ~~Aucune expérience à monter avant
la réponse.~~

> ⚠⚠⚠ **2026-09-04 — CE PARAGRAPHE SUR-AFFIRME, et `69` porte déjà le contre-argument.** Son
> §1.2 est marqué `[établi]` : à 1,2 m le papier rend deux verdicts pour la **même acquisition**
> — 4,317 µm *haze-limited*, 9,362 µm *pixel-limited* — donc la résolution physique y est bornée
> par la **décohérence** entre 4,3 et 9,4 µm. **Plus de voxels échantillonnant un signal déjà
> flou ne relèvent pas `d′`** : l'argument géométrique ci-dessus ne suit pas de cette physique,
> et `69` chiffre l'attente inverse — au plus **1,3–1,5×** de résolution effective.
>
> Et `69` écrit sa condition en toutes lettres : *« Cette prédiction est testable sur des données
> publiques (H2), et **si elle est fausse**, la donnée manquante la plus précieuse du prix est
> une demande à l'ESRF. »* Le courriel est donc **conditionnel**, et « aucune expérience à monter
> avant la réponse » est faux — l'expérience est justement ce qui décide s'il faut écrire.
>
> ⭐ Elle est faisable : `src/volume/ou_vit_ce_rouleau.py PHerc0500P2` rend
> `volumes reconstruits → 0.550, 2.215, 4.317, 9.362`. **Le même objet est publié et
> téléchargeable aux deux échantillonnages**, et le lecteur par fenêtres l'absorbe sans
> rapatrier 20 To. Détail et ordre corrigé : [`75`](75_registre_des_taches.md) §C3.

### H3 — *la décohérence est un flou mesurable, local, et il prédit où le traçage échoue*

**Morte comme instrument.** Le dépôt a déjà la carte locale de qualité de scan sur les treize,
sous deux formes : `d′` par fenêtre (`carte_separabilite_dense/`, 57–115 fenêtres) et part de
fenêtres sous 150 µm (`16` §3). Et il a mesuré ce que ma carte aurait trouvé : la médiane ne
sépare rien (1,37–1,62 sur quatorze rouleaux), **la queue sépare**, et il faut 50 à 100
fenêtres pour que le classement tienne (`33` §3–4 bis). Un spectre polaire par fenêtre serait le
doublon de `16`.

**Vivante comme prédicteur, sans référent.** La moitié que le prompt nomme — la carte
co-localisée avec les régions où le **traçage** échoue — n'a pas de référent sur les treize :
toutes les traces du dépôt échouent **partout** (mur 1 de `55`, 26 séries `PHercParis4` sur 27
tombées, `51` §5), donc rien ne contraste. Le seul référent est ailleurs : les 37 spires
publiées et approuvées de `PHerc0139`, transformées dans le repère de son scan à 9,362 µm
(`68` §4). Test possible : `d′` par fenêtre le long de chaque spire publiée contre les endroits
où le `tifxyz` publié s'arrête ou se troue — les marques d'échec du pipeline lui-même.
**[conjecture]** que ces marques sont des échecs et non des choix d'opérateur ; c'est la
première chose à vérifier avant de mesurer.

### H4 — *le coût humain est proportionnel aux régions ambiguës, pas à l'aire*

**Inchangée**, et le référent que `69` demandait n'existe pas : aucun `approval.tif` n'est
publié (vérifié, §0). Mais il existe **sous une autre forme** : une spire publiée est approuvée
par construction — c'est ce que « publiée » veut dire dans `1667` (22 colonnes transcrites) —
donc « fraction approuvable » se mesure comme *fraction de l'aire d'une spire publiée où le
prédicat automatique passe*. Et le **témoin négatif d'un prédicat d'approbation** est déjà
outillé : la même nappe **translatée en bloc** (`44`, « plancher du hasard ») d'un demi-pas le
long de ses normales est une surface que le prédicat **doit refuser**.

Deux contraintes du dépôt que `69` ignorait et qui changent l'instrument :
- α sur deux fenêtres a une résolution de ±0,2 et **39 verdicts sur 138 ne tiennent plus** une
  fois la règle des deux appuis appliquée (`51` §4). Un prédicat d'approbation ne peut pas
  empiler des α : il doit lire **le relief dans la fenêtre étroite**, la question binaire de
  `51` §3.6 (0 des 75 convergentes plates, 34 des 63 condamnées) — et ce compte **ne se
  transporte pas** d'une géométrie de lecture à l'autre (article §3.6, dernier caveat).
- corriger 0,56 % de la surface ne change pas α (`42`) : le prédicat doit désigner des
  **régions**, pas des points.

### H5 — *les résidus du champ d'orientation prédisent les sauts de spire*

**Pas morte, et voici en quoi elle diffère mécaniquement de `17`.** Trois différences, chacune
vérifiable :

1. **Le référent de `17` n'était pas un saut de spire.** Ses ρ sont calculés contre les
   `events` de `windcheck`, qui sont des **auto-intersections** **[établi]** (§0). Un saut de
   spire — la surface passe de la feuille $k$ à $k+1$ — n'est pas une auto-intersection ; `43`
   mesure que le compte d'auto-intersections est une propriété de l'échantillonnage (240 → 49
   par décimation), et `06` §3.8 qu'il ne prédit pas la lisibilité. `17` a donc testé « marche
   de phase locale contre auto-intersections », et son négatif — propre et définitif sur cette
   question — ne porte pas sur « résidus contre sauts ».
2. **La grandeur de `17` était locale, celle de H5 est une intégrale de boucle.** `17` mesure
   une marche entre cellules voisines du canal `cos` de `lasagna`, dont la période vaut **3 à 7
   fois le pas** (614–1228 µm, `17` §1) : un champ diffusé, où un saut d'une feuille est une
   fraction de période. Un résidu est la circulation du gradient de phase **feuille-à-feuille**
   — construit sur la prédiction de surface `m7` (binaire, `th0.2`) et les `normal-grids`, dont
   la période **est** le pas — autour d'une plaquette : ±2π ou zéro, pas une amplitude.
   ⚠ `26` a payé que les `nx`/`ny` de `lasagna` sont un champ **2D** ; un résidu se calcule sur
   les grilles `xy`/`xz`/`yz` des `normal-grids`, jamais sur `lasagna` complété d'un `z` forcé.
3. **Le référent existe, et le dépôt l'a manipulé sans le lire.** Les 38 segments de
   `PHerc0139` sur lesquels `17` a tourné (n = 38) portent leur numéro de spire dans leur nom,
   `w023`…`w059` ; `PHerc1667` de même, `w011`…`w041` (20 segments, `w011` deux fois). Le test de H5 devient : *le champ
   déplié assigne-t-il un entier constant le long de chaque spire publiée, et des entiers
   consécutifs à deux spires consécutives ?* — un test d'**identité**, sans compte
   d'auto-intersections, sur des surfaces approuvées par des humains.

**Ce qui reste de mon doute du `69` §7** : les résidus peuvent n'être que le bruit de `m7`.
C'est exactement ce que le test 3 mesure — une carte de résidus qui contredit les indices
publiés est du bruit avec un beau nom, et on le saura sur 57 segments indexés.

### H6 — *le prior d'enroulement est universel*

**Déjà répondue**, aux trois quarts et par le dépôt : pas universel (`winding-ruler`, 187 µm,
35/36 dans 160–210), séparabilité médiane serrée (1,37–1,62, `16`), **et la queue qui
sépare**, à condition de 50–100 fenêtres (`33`). Ma grandeur « $Q$ effondré » est leur
`part_sous_1`. **Morte comme instrument neuf.**

⚠⚠ **Et elle corrige ma recommandation du `69` §6.** J'avais nommé `PHerc0826` (60 spires, le
moins de spires des treize). Par la carte dense, c'est **le pire des treize** : 22,8 % de
fenêtres indissociables, contre 2,6 % pour `PHerc0800` et 7,0 % pour `PHerc1447`. Le compte de
spires mesure le coût d'un pinceau ; la queue mesure la chance qu'un traceur suive. Choix
révisé, en §3.

### H7 — *le verso est le témoin nul du recto*

**Inchangée et non testée** — `46` teste un autre nul : une surface **en travers** de
l'empilement, qui contient des tranches de feuilles et, on y revient au §2, des tranches de
faces. Le verso est un nul **parallèle à la face**, sans arête de feuille dedans, et c'est ce
qui le rend différent. **Rendue plus urgente par `46`, pas moins** : le détecteur y rend *plus*
de dispersion sur la surface sans face (0,7111 contre 0,5894), donc « l'encre valide le
déroulage » n'est pas utilisable tant qu'on ne sait pas ce qu'il rend sur une face vierge.
Coût : un rendu décalé par segment — les couches de `0139` à 9,362 µm sont déjà rendues et le
décalage est connu. Dans le budget règle du §3, et pas au-delà.

---

## 2. Livrable 2 — avis de relecteur adverse sur l'article

L'article est un papier de **mesure**, et ses quatre résultats de §5 sont des mesures que le
domaine ne fait pas. Ce qui suit est ce qu'un relecteur hostile attaque, dans l'ordre où il
le ferait. Les trois premiers points sont des sur-affirmations que le dépôt lui-même contredit
ou peut tester ; les suivants sont des réserves.

### 2.1 ⚠⚠⚠ §6.7 — « *the predicate is the same one α estimates* » : non, il en manque deux tiers

Le prédicat du pinceau est cité dans l'article : *« regions judged geometrically consistent
with a **single sheet** »*. C'est un prédicat d'**identité** — la surface reste sur la feuille
$k$. α répond à un prédicat de **présence** — il y a une feuille à portée — et l'article le
sait : sa §2.3 écrit qu'une garantie topologique *« is not a guarantee about which sheet one is
on »*, et α est plus faible qu'une garantie topologique. Entre les deux il y a un prédicat de
**placement** — la surface est *sur* la feuille et non à côté, ce que `offset` mesure — que
l'article a aussi.

Le dépôt a **essayé** l'identité, et ça n'a pas marché : `17` (absent de l'article) est
exactement le détecteur de saut que §6.7 sous-entend, testé proprement, négatif. Un relecteur
qui lit le code de `villa` trouvera le mot *single sheet* et demandera où est le test
d'identité. La phrase à retirer est *« the same judgement made two ways »* ; la phrase à écrire
est : *α automates the presence half of the approval predicate; the identity half is open, and
the referent to test it against is published — the wrap index in the names of 57 human-approved
segments.* Et **publier `17` dans cette section**, comme le résultat négatif qu'il est : ça
tient en un paragraphe et ça rend §6.7 honnête au lieu de vulnérable.

### 2.2 ⚠⚠ §3 — « *no threshold on a physical quantity* » : vrai de α, faux du verdict

Une surface **parallèle aux feuilles, posée dans l'interstice** à un demi-pas de chacune, a
un pic stable à ~85 µm quelle que soit la fenêtre : $d_0 = d_1$, **α = 0**. Par la règle des
deux appuis (§3.6), l'appui étroit au bord en fait un majorant et *la convergence tient*.
L'instrument dirait « la feuille est là ». Ce qui distingue cette surface d'une surface sur sa
feuille est $d$ contre la demi-épaisseur d'une feuille — **un seuil en micromètres**. L'abstract
dit *needs neither a threshold*, §3.1 dit *it is close*, et « close » est ce seuil.

**Test, avec le dépôt** : translater un segment publié convergent d'un demi-pas le long de ses
normales (l'outil du « plancher du hasard » de `44`) et mesurer α. **Prédiction** : α ≈ 0 avec
$d$ ≈ 80–90 µm. Si α sort ≈ 1, je me trompe et la revendication tient ; si α ≈ 0, la phrase
devient *no threshold to decide whether the peak is a sheet or the window ; a physical offset
decides whether the surface is on it*, ce qui reste un bon résultat.

### 2.3 ⚠⚠ §2.1 — « *median centre-to-centre spacing of 113 µm* » contredit l'atlas que §2.4 cite

`gen_neighbor` arrête son rayon **au premier échantillon au-dessus du seuil** (`43`
§6quater) : chaque nappe de la chaîne est posée sur la **face proche** de la feuille suivante,
et l'écart au plus proche voisin entre deux nappes consécutives (`44` §4) est donc un écart
**face à face**, pas centre à centre. **[calculé]** 113 µm + 24 à 60 µm d'épaisseur de feuille
= 137 à 173 µm centre à centre — ce que `16` mesure sur le même rouleau (**156 µm** médian,
p10 138) et ce que l'atlas de `winding-ruler` publie (**172,8 µm** pour `PHerc1447` au
niveau 1). L'article cite cet atlas trois lignes plus loin. Un relecteur verra 113 contre 173
et ne saura pas lequel croire.

Correctif : relabelliser (*face-to-face gap*), corriger « about 13 voxels » en ~18–20, et
§5.5 survit tel quel — « the chain advances one sheet at a time » est même **plus** vrai avec
le bon label. Rien d'autre ne bouge : les seuils 40 / 250 µm de §5.7 portent sur des écarts
entre surfaces, donc face à face aussi.

### 2.4 ⚠ §6.5 — le témoin négatif n'est pas *sans encre* par construction

La surface à α ≈ 1 est décrite par l'article lui-même : *« concentric laminations — the
scroll seen edge-on »*. Elle **traverse** des feuilles, donc elle traverse leurs faces recto,
donc elle traverse la couche d'encre là où il y en a — en rubans de largeur $t/\sin\theta$,
2 à 4 pixels à 8,64 µm pour un dépôt de 10–20 µm. Ce que la géométrie exclut est une **face**
à portée, pas de la matière ni de l'encre. *« any ink reported there is a false positive by
construction »* et *« It reports ink where there is no sheet »* sur-affirment ; ce qui est
mesuré (σ, contraste) établit que **la réponse du détecteur n'est pas spécifique d'une face**,
ce qui est déjà la conclusion dure. Le nul propre est celui de H7 — parallèle à une face,
sans arête. Et la limite que §6.5 déclare (le contrôle typographique a manqué d'une fenêtre,
`46` §3 ter) est honnête ; garder.

### 2.5 ⚠ §5.5 — la méthode de la flèche suppose une direction axiale droite

*« a line running along the axis is straight »* — or `laxe_nest_pas_une_ligne.py` mesure sur
`Scroll 1` une errance de l'axe de **21,6 mm sur 108 mm** de hauteur. Sur un segment de
quelques millimètres de haut, la ligne « axiale » du quadrillage a sa propre flèche, qui peut
rivaliser avec la flèche circonférentielle d'une corde de 8 à 22 mm sur un rayon de 2 à 4 cm.
Test : sur l'ombilic publié de `Scroll 1`, flèche axiale locale sur l'étendue en $z$ d'un
segment contre la flèche circonférentielle mesurée. ⚠ Le script ne trouve d'ombilic que pour
`Scroll 1` sur les cinq répertoires qu'il a vérifiés, et **[je ne sais pas]** si `PHerc1447` en
publie un ailleurs ; tant qu'on ne l'a pas, sur le rouleau de §5.5 la réserve se déclare, elle
ne se mesure pas.

### 2.6 §5.7 — les quinze segments sont des `auto_grown_*`

Leurs noms le disent (`metadata.min.json`) : quatorze `auto_grown_<horodatage>` et un
`z_dbg_gen_00320`. Ce sont les sorties d'un traceur à **graine aléatoire**, dont « une pièce
par feuille » est le comportement attendu par construction. Le recensement des 105 paires est
juste et sans précédent (`71` §3) ; la formulation *« the published segmentation of a prize
scroll »* laisse croire à un effort de segmentation curaté. Nommer les segments pour ce qu'ils
sont rend le résultat plus petit et inattaquable.

### 2.7 Deux comptes, deux définitions

Abstract : *13 of 16 traces sit exactly on it* ; intro et §5.4 : *on 14 of 16 traces*.
`derive_profondeur.json` porte les deux : 13 censurées à la profondeur basse, **14 censurées
à l'une au moins** des deux (`n_censurees` du critère `ecart_um`). Les deux sont vrais ;
l'article les emploie comme un seul.

### 2.8 Une limite non déclarée : α n'a jamais vu de courbe ROC

La validation de §3.3 est **un** vert (un segment publié, donc approuvé par des humains) contre
les traces condamnées du dépôt. Sur les 75 séries convergentes de l'arbre, combien sont des
segments publiés ? Si c'est la majorité, α **re-dérive** une approbation humaine plus qu'il ne
la remplace — ce qui est déjà utile, mais se dit. Les 57 segments publiés et indexés donnent
57 positifs à deux résolutions ; leurs copies translatées d'un demi-pas donnent 57 négatifs
de la panne qui compte (§2.2). Une ROC de α **et** de $d$ sur ces 114 surfaces est à la portée
des instruments existants et fermerait §2.2 et §2.8 d'un coup.

### 2.9 Verdict

**La thèse tient, étroitement** : *un test de présence qui ne demande ni référence, ni
échelle, ni seuil pour dire si le pic est une feuille ou la fenêtre*. Les quatre résultats de
§5 sont solides et les corrections de `71` les ont rendus défendables. **Il vaut d'être publié**
à trois conditions : rétrécir §6.7 (présence ≠ identité, et y verser `17`), rétrécir
*no threshold* en §3 et dans l'abstract (le placement en a un), et corriger le label de §2.1.
Le titre promet *segmentation quality*, ce qu'un lecteur entendra comme *identité* ; c'est le
risque de lecture le plus probable, et il se lève dans l'abstract en une phrase.

---

## 3. Livrable 3 — le plan repondéré contre le cadrage

### 3.1 Ce que je défends de la règle, et combien de temps

Le cadrage dit : *l'encre est la règle graduée, pas l'ouvrage*. Je le prends au mot, et une
règle a une propriété qu'il faut établir avant de s'en servir : **elle lit quelque chose**.
`46` mesure que le détecteur rend plus de structure sur une surface sans face que sur une face
(`46` §3) ; `65` mesure qu'à 9,72 µm la lisibilité n'est pas établie contre 0,5. Une règle qui
marque autant sur le vide que sur le plein ne valide aucun déroulage — elle validerait aussi
bien une surface en travers. Étalonner la règle n'est donc pas « pousser l'AUC », c'est mesurer
son zéro et sa graduation, **une fois**, avec assez de tuiles, et s'arrêter.

**Trois semaines, pas quatre mois** :
- semaines 1–2 : la case vide de `68` §4, **native** à 9,362 µm sur `PHerc0500P2`, ≥ 40 tuiles
  de 256 px (`64`, `65`, §1 H1), intervalle par tuiles, témoin par mélange ;
- semaine 3 : le nul verso (H7) sur les mêmes couches, et sur trois segments `w` de `0139`.

Sortie : deux nombres avec leur intervalle. Si l'AUC native à 9,362 µm ne se sépare pas de
0,5 avec 40 tuiles, la règle ne lit pas à ce régime, et « colonnes visibles partout » devra
être jugé par la typographie (`45`) et par le juge à condition vierge (`09`) plutôt que par une
carte d'encre. C'est une conclusion sur la **méthode de validation**, pas sur le prix, et elle
se prend en trois semaines.

### 3.2 Ce qui remplace le pinceau : trois prédicats, dont un manque

| prédicat | question | état dans le dépôt |
|---|---|---|
| **présence** | y a-t-il une feuille à portée ? | α / relief dans la fenêtre étroite — construit (`38`, `49`, `51`) |
| **placement** | la surface est-elle *sur* la feuille ? | `offset` contre la demi-épaisseur — construit (`20`, triage §4) |
| **identité** | est-ce la *même* feuille qu'il y a un tour ? | **absent** — `17` a échoué contre le mauvais référent ; le référent existe (§1 H5) |

Le pinceau peint le troisième. Les deux premiers l'assistent — ils désignent où regarder —
et ne le remplacent pas. **Le prix se gagne sur le troisième.**

### 3.3 Le plan, mois par mois

- **Mois 1–2 — l'identité a un référent, on le lit.** Un lecteur des indices `w0NN` (57 segments,
  deux rouleaux, `0139` dans le repère du régime du prix). Puis la carte de résidus de `69` A2,
  sur `normal-grids` + `m7` au niveau 1, et le test de H5 révisé : un entier par spire publiée,
  consécutifs entre spires consécutives, résidus contre bords de spires. **Ce qui la ferait
  échouer** : des résidus répartis comme le bruit de `m7` et sans rapport avec les bords —
  auquel cas l'identité doit venir de la coupe à $K$ surfaces couplées (`69` §3.3), qui
  s'engage sur une feuille par construction, et je le dirais à ce moment-là.
- **Mois 2–4 — `approval.tif` à trois prédicats**, écrit à côté des `x/y/z.tif` (article §6.7),
  avec le contrôle à trois bras sur une spire de `1667` (masque automatique, vide, plein → écart
  de maillage) **et un quatrième bras** : la copie translatée d'un demi-pas, que le masque doit
  refuser. Sans le quatrième, un masque qui approuve tout passe le contrôle.
- **Mois 4–7 — extraire, pas faire pousser.** L'article a fermé les deux voies ascendantes par
  la mesure : l'extension converge vers un point fixe de 6 cm² (§5.6), les patchs ne pavent pas
  (§5.7). Ce qui reste est l'extraction de **toutes** les spires depuis un champ global (`69`
  A3–A4), sur **`PHerc0800`** — le meilleur des treize par la carte dense (2,6 %), 103 spires,
  6 patchs publiés — ou `PHerc1447` (7,0 %, 80 spires, 15 patchs, le rouleau le plus instrumenté
  du dépôt). **Jamais `0826`.** La mesure de succès est celle du point fixe : aire utile par
  spire extraite, à présence + placement + identité, contre 6,02 cm² ; une spire entière de
  `0800` fait 60 à 300 cm².
- **Mois 7–10 — aplatir, intégrer, livrer.** Érosion : une extraction n'érode pas comme une
  chaîne (15,6 % par tour, `44` §5) — à mesurer, pas à supposer. VC3D, Docker, reproductibilité
  (`depot/`).

### 3.4 Les hypothèses remplacées

| `69` | remplacée par |
|---|---|
| H1 (spectre d'AUC) | **H1′** — le champ déplié assigne un entier constant par spire publiée sur ≥ 95 % de son aire, et consécutif entre `w_k` et `w_{k+1}`, sur 57 segments |
| H2 (débinage) | **H2′** — le masque à trois prédicats approuve ≥ 80 % de l'aire d'une spire publiée et **refuse** ≥ 90 % de sa copie translatée d'un demi-pas |
| H7 (verso) | **H7′** — une spire extraite du champ global à présence + placement + identité dépasse 6,02 cm² d'aire propre, et son érosion par tour est inférieure à 15,6 % |

H1 et H7 d'origine passent au budget règle (§3.1) ; H2 au courriel ; H3 et H6 sont
répondues ; H4 et H5 sont le plan.

---

## 4. Livrable 4 — une chose que le dépôt n'a pas vue

**Les segments publiés portent leur numéro de spire dans leur nom, et aucun instrument du
dépôt ne le lit.** `PHerc0139` : `w023` à `w059` ; `PHerc1667` : `w011` à `w041` — 57 segments, 56 spires distinctes,
approuvés par des humains, transcrites pour 22 colonnes de `1667`, dont `0139` est transformé
dans le repère du **régime du prix**. C'est :

- le référent d'**identité** que le prédicat du pinceau exige (*single sheet*) ;
- le référent que `17` n'avait pas — il a tourné sur **ces 38 segments-là** contre des
  auto-intersections ;
- la vérité terrain que l'article dit ne pas exister (*« on a sealed scroll nothing says
  where the sheet actually is »*) — elle ne dit pas *où* est la feuille, elle dit
  *laquelle*, et c'est la moitié qui manque.

Le tester coûte un parseur de suffixe et les lecteurs déjà écrits (`17` pour `lasagna`, `26`
pour les `normal-grids`). ⚠ **[je ne sais pas]** si `w` compte les spires depuis le centre ou
depuis l'extérieur, ni si la numérotation de `0139` et celle de `1667` suivent la même
convention ; c'est la première ligne du lecteur, et elle se vérifie sur les `tifxyz`
transformés en mesurant le rayon médian de `w_k` contre `w_{k+1}`.

---

## 5. Ce dont je doute, cette fois

- **§2.2 repose sur une lecture de §3.6, pas sur une mesure.** Si le rendu d'une surface dans
  l'interstice donne un profil *plat* (deux pics symétriques à ±85 µm qui se neutralisent dans
  la médiane) plutôt qu'un pic stable, l'instrument refuse au lieu de converger, et l'attaque
  tombe. La translation d'un demi-pas tranche en un rendu.
- **§2.3 suppose que la source de la chaîne était centrée.** Le segment publié d'où part la
  chaîne est à $d$ = 17,3 µm de son pic, donc à peu près centré ; si la convention de
  `gen_neighbor` place plutôt la nappe au **centre** de la feuille suivante (je n'ai pas relu
  `GrowPatch.cpp` ligne à ligne), 113 µm serait bien centre à centre et c'est `16` et l'atlas
  qu'il faudrait réconcilier autrement. Le fichier tranche, pas moi.
- **La numérotation `w` peut être discontinue ou locale** (`1667` saute de `w013` à `w018`,
  puis à `w023`). Un test d'identité qui exige des entiers consécutifs doit d'abord vérifier
  que les indices publiés le sont.
- **Choisir `0800` sur la queue de `d′` suppose que `d′` prédit le traçage.** `55` dit que le
  mur 1 vient de la graine, pas du scan ; rien ne montre encore qu'un rouleau à 2,6 % se trace
  mieux qu'un rouleau à 22,8 %. C'est une hypothèse de plus, et elle se mesure sur les deux
  premiers rouleaux tracés.
