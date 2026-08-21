# La chaîne des spires : six tours tiennent, le septième casse

2026-08-21. Reproductible : `./tools/lancer.sh --fond tools/spire_suivante.sh`.
Dépouillement : `analysis/src/table_chaine.py` (7 témoins).
Verdicts : `docs/spire_spire0*.json`, table : `docs/chaine_spires.json`.

---

## 1. Le résultat

Un segment officiel qui **converge**, puis six spires générées par `mode: gen_neighbor`,
chacune servant de source à la suivante. Toutes jugées dans les **mêmes fenêtres** (31 et
81 couches) par la **même chaîne**.

![les sept spires, la meme mesure](images/43_chaine_spires.png)

| spire | grille | aire* | 31 c | 81 c | **α** | verdict |
|---|---|---:|---:|---:|---:|---|
| **00** (officiel) | 162×149 | 7,12 cm² | 17,28 µm | 17,28 µm | **+0,000** | **converge** |
| 01 | 157×145 | 6,71 cm² | 90,72 µm | 90,72 µm | **+0,000** | **converge** |
| 02 | 153×141 | 6,35 cm² | 43,20 µm | 51,84 µm | +0,190 | **converge** |
| 03 | 150×139 | 6,14 cm² | 12,96 µm | 21,60 µm | +0,532 | intermédiaire |
| 04 | 147×136 | 5,89 cm² | 77,76 µm | 77,76 µm | **+0,000** | **converge** |
| 05 | 144×133 | 5,64 cm² | 129,60 µm | 172,80 µm | +0,300 | intermédiaire |
| **06** | 141×130 | 5,39 cm² | 69,12 µm | **285,12 µm** | **+1,475** | ⚠⚠ **suit la fenêtre** |

\* aire de la **grille**, sommets invalides compris — un majorant, pas la surface utile.

**4 spires sur 7 convergent, 2 sont intermédiaires, et la 7ᵉ casse.**

⭐⭐⭐ Et c'est la première fois de tout ce dépôt qu'une surface **que nous avons produite**
converge. Toutes les traces poussées en `mode: seed` — dix-sept essais, quatre rembobinages
corrigés, deux semis, deux poids — sont à α ≈ 1 sans exception
([`42`](42_la_boucle_tourne_et_ne_suffit_pas.md)). Ici six surfaces d'affilée ne le sont pas.

## 1bis. ⭐⭐⭐ Et ça se VOIT — les sept spires, rendues

![les sept spires rendues, couche de surface](images/43_chaine_rendus.jpg)

Chaque bande est la **couche de surface** (40 sur 81) du rendu de cette spire, étirée entre
ses percentiles 1 et 99. ⚠ L'étirement est **par bande** : c'est le bon choix pour regarder
(chaque spire a son exposition) et le mauvais pour mesurer — **aucune mesure de ce dépôt ne
passe par ces images**.

La dégradation est **visible, et elle suit les chiffres** :

| bandes | ce qu'on voit | α |
|---|---|---|
| **000, 001** | treillis de fibres croisées partout, trous nets aux bords | +0,000 |
| **002, 003** | le treillis tient, mais des plages grises lisses apparaissent | +0,190 / +0,532 |
| **004, 005, 006** | les plages grises gagnent, avec des volutes — la surface quitte la feuille | +0,000 / +0,300 / **+1,475** |

⭐ Et l'érosion se voit aussi : l'empreinte rétrécit de bande en bande, exactement comme la
grille (7,12 → 5,39 cm²).

⚠ **Ce que ces images ne montrent pas : de l'encre.** Ce sont des rendus de matière, pas des
cartes d'encre. Voir du papyrus prouve qu'on est **sur** une feuille ; lire du texte
demanderait un détecteur, et [`36`](36_lorigine_de_la_pile.md) §5bis mesure que le modèle de
2023 sort une constante sur ce rouleau.

## 2. ⚠ Ce que « converge » dit et ne dit pas

**α mesure s'il y a une feuille à portée, pas si c'est la bonne.** La spire 01 converge
parfaitement (α = +0,000) à **90,72 µm** — pas à 17. Elle a donc trouvé de la matière stable,
mais rien ne dit que c'est la spire immédiatement voisine plutôt qu'une plus loin, ni que le
rayon tiré a franchi un seul interstice.

⚠ Et les écarts n'ont **aucune tendance** : 17,3 → 90,7 → 43,2 → 13,0 → 77,8 → 129,6 → 69,1.
Ça oscille. Un enchaînement qui dériverait régulièrement donnerait une suite monotone ; celui-ci
tombe bien ou mal selon le tour, et la spire 03 a même l'écart **le plus petit du tableau**
(12,96 µm, mieux que l'officiel).

⚠ **α sur deux fenêtres seulement.** Un écart de ±0,2 n'est pas interprétable, donc les deux
« intermédiaires » ne sont pas un diagnostic. Ce qui est solide, c'est la séparation entre
0,00–0,53 d'un côté et **1,475** de l'autre : la 7ᵉ est ailleurs, pas un peu plus loin.

## 3. ⭐⭐ L'érosion, mesurée : la chaîne a une longueur maximale

La grille rétrécit à **chaque** tour, et régulièrement : 162×149 → 141×130, soit
**7,12 → 5,39 cm² en six tours = 24 %, ou 4,0 % par tour**.

> À ce rythme, **la moitié de la surface est perdue en douze tours**.

Ce n'est donc pas la qualité qui borne la chaîne en premier, c'est la **taille** : chaque
spire est le rayon-cast de la précédente, et les sommets qui ne trouvent rien sont perdus
définitivement. `neighbor_fill` est déjà à `true` ; ce qui manque est une repousse — c'est-à-dire
exactement ce que `mode: seed` sait faire et que cette chaîne n'utilise pas.

## 4. ⚠⚠ Et le verdict d'auto-intersection de ces spires ne mesure rien

`vc_tifxyz_selfcross` rapporte `clean_of_transverse_self_intersection: true` et
`report_only: true` sur les sept — **sans `pairs_tested`, sans compte de croisements**. Notre
lecteur ([`34`](34_un_verdict_qui_ne_mesure_rien.md)) **refuse** de rendre un nombre dans ce
cas, d'où les `?` de la table. C'est le même défaut que `34` documente, sous une autre forme :
là c'était `--maxedge` qui jetait tous les quads, ici c'est le mode `report_only` qui omet les
comptes. Un portail bâti sur `clean` accepterait ces sept surfaces sans avoir rien testé.

## 5. Ce que la campagne refuse de faire

⚠ **Elle refuse de partir d'une surface qui ne converge pas.** La spire 0 est jugée, son
verdict est **lu dans le JSON**, et la campagne sort en le nommant si ce n'est pas
« converge » — parce qu'enchaîner depuis une surface posée en travers mesurerait la
**propagation d'un défaut**, et que le résultat aurait l'air d'un résultat.

⚠ Ce garde a servi le jour même : le premier lancement partait de
`data/trace/PHerc1447_officiel/`, choisi **parce que son nom disait « officiel· »** — et ce
segment-là est à α = +1,02 avec 72–78 % de pics au bord ([`36`](36_lorigine_de_la_pile.md)).
Le nom d'un répertoire n'est pas une mesure.

## 6. ⭐⭐ La repousse : la surface regagnée n'est pas sur la feuille

L'érosion de 4 % par tour vient de ce qu'un sommet dont le rayon ne trouve rien est perdu
**définitivement**. `mode: resume` sait faire repousser une surface — d'où le pari, posé
avant de le lancer : *ça peut aussi la tirer hors de sa feuille, parce que c'est le traceur
non contraint qui repousse.*

Comparaison **appariée** — même surface de départ, même sens, mêmes fenêtres, même nombre de
spires ; **seule la repousse change** :

![la repousse, comparaison appariee](images/43_repousse_appariee.png)

| | 31 c | 81 c | **α** | verdict |
|---|---:|---:|---:|---|
| **spire 01** sans repousse | 90,72 µm | 90,72 µm | **+0,000** | **converge** |
| **spire 01** repoussée (20 gén.) | 86,40 µm | 129,60 µm | **+0,422** | intermédiaire |
| **spire 02** sans repousse | 43,20 µm | 51,84 µm | **+0,190** | **converge** |
| **spire 02** repoussée | 64,80 µm | 112,32 µm | **+0,573** | intermédiaire |

Et la surface, sur la première paire : grille **157×145 → 212×200**, aire
**6,71 → 12,47 cm²**.

⭐ **La repousse marche, au sens où elle rend la surface** : la grille passe de 157×145 à
212×200, l'aire de 6,71 à 12,47 cm² — **près du double**, et bien au-delà de ce que l'érosion
avait pris.

⚠⚠ **Et elle dégrade la convergence** : α passe de +0,000 à +0,422. Le détail dit où : la
fenêtre 31 s'améliore un peu (90,72 → 86,40 µm) et la fenêtre 81 se dégrade nettement
(90,72 → 129,60). Ce n'est donc pas la surface entière qui s'abîme, c'est **la part regagnée
qui tire la mesure**.

> Ce qu'on apprend : **la surface qu'on récupère n'est pas sur la feuille.** L'érosion n'est
> pas un défaut à corriger, c'est le **prix** de rester dessus — au moins avec ce repousseur,
> qui est celui dont [`42`](42_la_boucle_tourne_et_ne_suffit_pas.md) montre qu'il produit des
> coupes radiales quand rien ne le contraint.

⭐⭐ **Et les trois mesures de la journée disent la même chose sous trois angles** :
`mode: seed` ne pose jamais la surface sur une feuille (17 essais, tous α ≈ 1) · les points
de correction ne réorienté pas ce qui a déjà poussé (`42`) · et faire repousser une bonne
surface la fait sortir de sa feuille (ici). **Ce qui garde une surface sur sa feuille, c'est
de ne pas la laisser croître librement.**

### ⭐⭐ Et à la troisième paire, la chaîne repoussée CASSE — deux fois plus tôt

| spire | base | repoussée | écart |
|---|---:|---:|---:|
| 00 (contrôle) | +0,000 | +0,000 | **0** |
| 01 | +0,000 | +0,422 | +0,42 |
| 02 | +0,190 | +0,573 | +0,38 |
| **03** | +0,532 | **+1,461** ⚠⚠ | **+0,93** |

La spire 03 repoussée fait **26,20 cm²** — quatre fois la spire 03 de base — avec **2 921
auto-intersections**, et son α la met franchement **en travers de l'empilement**.

> **La chaîne de base tient six tours ; la chaîne repoussée casse au troisième.** Faire
> repousser la matière perdue ne prolonge pas la chaîne : **ça la coupe en deux.**

⚠ Et la dégradation **accélère** : +0,42, +0,38, puis +0,93. Ce n'est pas un décalage
constant qu'on pourrait compenser, c'est une dérive qui se nourrit d'elle-même — chaque
repousse part d'une surface déjà un peu plus en travers que la précédente.

⚠ Trois paires, un contrôle à écart nul, et une rupture franche.

⚠⚠ **La campagne a été arrêtée au tour 4, délibérément**, et la raison est écrite dans
`data/spires_repousse/ABANDONNE` : les spires 04 à 06 ne mesureraient que **de combien
empire une chaîne déjà cassée**, et elles coûtent cher — la repousse fait grossir les
surfaces (26,20 cm² au tour 3 contre 6,14 sans repousse), donc chaque rendu est plus lent.
Une chaîne qui casse au troisième tour ne se rattrape pas au cinquième, et la machine était
mieux employée sur la question encore ouverte (le sens `in`).

⚠ La spire 00 est **identique** dans les deux campagnes (+0,000 des deux côtés), ce qui est
le contrôle : c'est la même surface de départ, réellement partagée, donc l'écart des paires
suivantes vient bien de la repousse et pas du hasard de deux exécutions.

⭐ La suite naturelle n'est donc pas « repousser plus » mais **repousser sous contrainte** :
les points de passage de [`41`](41_marcher_le_long_dune_nappe.md) existent, `correction_weight`
existe, et une repousse corrigée est la seule combinaison des deux qui n'ait pas été essayée.

---

## 6bis. ⭐⭐ Le sens `in` : ni meilleur, ni pire — et c'est la découverte

Vers l'intérieur les spires se serrent, donc le rayon a moins de chemin à faire. L'attente
était une chaîne plus solide. Mesuré, sur les **sept** tours, à conception appariée :

| spire | `out` | `in` |
|---|---:|---:|
| 00 (contrôle) | +0,000 | +0,000 |
| 01 | +0,000 | **+0,038** |
| 02 | +0,190 | +0,686 |
| 03 | +0,532 | +0,986 |
| 04 | +0,000 | +0,722 |
| 05 | +0,300 | **+0,000** |
| 06 | **+1,475** | +0,257 |

![la chaine vers l'interieur](images/43_chaine_dedans.png)

⚠ **Aucun des deux sens ne gagne.** `in` se dégrade plus vite au début (02 et 03 nettement
pires) puis **se rétablit** — la spire 05 est un +0,000 parfait après deux mauvais tours —
là où `out` tient longtemps puis casse net au 06.

⭐⭐ Et c'est ça, la découverte : **α oscille dans les deux sens.** Un tour parfait arrive
après deux mauvais. Ça contredit la lecture naturelle — « l'erreur s'accumule, la chaîne a
une longueur maximale » — et ça ouvre une lecture bien plus utile : **chaque tour joue sa
propre partie**, et un mauvais tour ne condamnerait pas la suite.

### ⚠⚠ Alors on l'a mesuré au lieu de le croire

`analysis/src/derive_ou_loterie.py` (11 témoins) teste la corrélation de rang au **décalage
1** entre α(tour N) et α(tour N+1), sur les **12 paires** des deux chaînes cumulées — sans
jamais recoller la fin d'une chaîne au début de l'autre.

| | |
|---|---:|
| ρ au décalage 1 | **+0,299** |
| p (permutation) | **0,344** |
| puissance à ρ = 0,7 | 68 % |
| **puissance à l'effet observé (ρ = 0,30)** | **15 %** |

> **Verdict : pas de dérive FORTE — une dérive de cette ampleur aurait été vue. Une dérive
> modérée, non.**

⚠ **Et la première version de ce verdict était trop généreuse** : elle concluait « loterie »
dès que la puissance à ρ = 0,7 dépassait 50 %. Ne pas voir une dérive *forte* ne dit rien
d'une dérive *modérée* — et le ρ observé valait justement 0,3, où le test n'a que **15 %** de
chances de voir quoi que ce soit. Le verdict ne peut exclure que ce que le test aurait su
voir, et il le dit maintenant.

⭐ Ce qui reste actionnable malgré l'indécision : **juger chaque spire et rejouer les
mauvaises** vaut la peine d'être essayé. Si les tours étaient fortement enchaînés, ça ne
servirait à rien — et c'est précisément ce que la mesure exclut.

## 6ter. ⚠⚠ Un juge à un seul rendu : mesuré AVANT de s'en servir, et il ne marche pas

Le test de convergence demande **deux** rendus, et un rendu est l'étape la plus chère de tout
le dépôt. Un juge à un seul rendu diviserait par deux le coût de toute campagne — et
permettrait d'essayer **plusieurs candidats par tour** là où on n'en essaie qu'un.

Le candidat naturel était `au_bord_relief`, déjà calculé : la part des fenêtres dont le pic
tombe **au bord** de la fenêtre rendue. C'est la forme locale de ce que α mesure globalement.
Vérifié sur les **18 spires** déjà jugées des deux façons :

| statistique d'UN rendu | ρ contre α | p |
|---|---:|---:|
| `au_bord_relief` | **+0,226** | 0,360 |
| écart médian à 31 couches | **+0,204** | 0,408 |

> **Aucune relation détectable. Le juge à un rendu n'existe pas.**

⭐ Et c'est précisément à ça que sert un contrôle posé **avant** : la campagne « essayer
plusieurs candidats par tour et garder le meilleur » allait être bâtie sur ce proxy. Chaque
sélection aurait été du bruit, et le résultat aurait ressemblé à une amélioration.

⚠ Réserve honnête : seules **3 des 18** spires sont condamnées par le vrai juge (α ≥ 0,75),
donc la puissance à décider si le proxy rate *spécifiquement* les cas durs est faible. Ce qui
est établi, c'est qu'il n'y a pas de relation d'ensemble — ce qui suffit à ne pas s'en servir.

⚠ Conséquence pratique : essayer K candidats par tour coûte **2K rendus**. C'est ce prix-là
ou rien.

## 6quater. ⏳ Le pas du rayon : trois tours identiques, donc ce n'est pas l'échantillonnage

`gen_neighbor` arrête son rayon au **premier** échantillon au-dessus du seuil, par pas de
`neighbor_step` voxels. Un pas plus fin localise donc la nappe plus précisément, et c'était
le dernier levier mécanique non testé pour « pourquoi un tour rate ».

| spire | pas 1,0 | pas 0,5 |
|---|---:|---:|
| 00 (contrôle) | +0,000 | +0,000 |
| 01 | +0,000 | +0,000 |
| 02 | +0,190 | **+0,160** |

⚠ **Trois tours, aucune différence utile.** Diviser le pas par deux ne change rien à ce que
le rayon trouve — donc les tours qui ratent ne ratent pas par manque de résolution le long
du rayon. C'est une cause de moins, et elle coûtait un doublement du travail par tour.

⏳ Campagne en cours : les tours 03 à 06 diront si ça reste vrai là où la chaîne à pas 1,0
se dégrade (+0,532) puis casse (+1,475). Tant qu'ils manquent, la conclusion ci-dessus ne
porte que sur les trois premiers tours.

## 7. ⭐⭐ Ce que les trois campagnes disent ensemble

| ce qu'on a essayé | ce que ça fait à la surface | α |
|---|---|---|
| `mode: seed` — la faire pousser depuis un point | elle prend l'orientation qu'elle veut | ≈ **1** (17 essais, sans exception) |
| `--correct` — lui dire où passer après coup | 318 puis 5 695 points ne réorienté pas ce qui a poussé | **+0,89** au mieux |
| **`gen_neighbor`** — la **projeter** d'une feuille à la suivante | aucune liberté, donc aucune dérive… | **+0,00** six tours de suite |
| `resume` — lui rendre ce que la projection a perdu | la liberté revient, et la dérive avec | **+1,46** au 3ᵉ tour |

> **Ce qui garde une surface sur sa feuille, c'est de ne pas la laisser croître librement.**
> Les quatre lignes ci-dessus sont quatre façons de le mesurer, et elles sont d'accord.

⭐ Ça explique aussi pourquoi `gen_neighbor` réussit là où tout le reste échoue : il ne fait
pas *croître* une surface, il en **projette** une existante. Et l'érosion de 4 % par tour
n'est pas un défaut de cette méthode — c'est **le prix de sa contrainte**.

## Ce qui reste ouvert

| # | quoi |
|---|---|
| 1 | ⭐ **pourquoi la 7ᵉ casse.** Est-ce l'érosion (5,39 cm² de grille, moins de sommets pour voter), un interstice manqué, ou le rayon qui saute une spire ? La sonde naturelle est `neighbor_max_distance`, `neighbor_min_clearance` et `neighbor_step`, tous paramétrables |
| 2 | ~~repousser entre deux tours~~ **✅ mesuré, et c'est non** : §6 — la chaîne casse deux fois plus tôt |
| 3 | ⏳ **le sens `in`** : les deux chaînes tournent en `out`. Vers l'intérieur les spires se serrent, donc le rayon a moins de chemin à faire et l'erreur n'a aucune raison de s'accumuler pareil. Campagne lancée (`data/spires_dedans`) |
| 4 | ⚠ **la validation par l'encre.** α dit qu'une feuille est à portée ; il ne dit pas qu'on lit du texte. Le seul juge qui trancherait est un rendu, et six spires en donnent la matière |
| 5 | **recoller les six spires en une seule surface.** Elles sont voisines par construction ; une surface unique de six spires serait la première chose de ce dépôt qui ressemble à un morceau de rouleau déroulé |

## Reproduire

```bash
./tools/lancer.sh --fond tools/spire_suivante.sh "$PWD/data/spires" 6
python3 analysis/src/table_chaine.py data/spires --voxel-um 8.64 --json docs/chaine_spires.json

cd experiments && uv run python ../analysis/src/test_convergence.py \
  --depuis "../docs/spire_spire00.json=spire 0 (segment officiel)" \
  --depuis "../docs/spire_spire01.json=spire 1" \
  --json ../docs/chaine_convergence.json     # … une ligne par spire
cd ../inference && uv run python ../analysis/src/figure_convergence.py \
  --entree ../docs/chaine_convergence.json --sortie ../docs/images/43_chaine_spires.png
```
