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

⚠ Trois paires, un contrôle à écart nul, et une rupture franche. La campagne continue vers
les spires 04 à 06, mais la conclusion ne dépend plus de ce qui reste : une chaîne qui casse
au troisième tour ne se rattrape pas au cinquième.

⚠ La spire 00 est **identique** dans les deux campagnes (+0,000 des deux côtés), ce qui est
le contrôle : c'est la même surface de départ, réellement partagée, donc l'écart des paires
suivantes vient bien de la repousse et pas du hasard de deux exécutions.

⭐ La suite naturelle n'est donc pas « repousser plus » mais **repousser sous contrainte** :
les points de passage de [`41`](41_marcher_le_long_dune_nappe.md) existent, `correction_weight`
existe, et une repousse corrigée est la seule combinaison des deux qui n'ait pas été essayée.

---

## Ce qui reste ouvert

| # | quoi |
|---|---|
| 1 | ⭐ **pourquoi la 7ᵉ casse.** Est-ce l'érosion (5,39 cm² de grille, moins de sommets pour voter), un interstice manqué, ou le rayon qui saute une spire ? La sonde naturelle est `neighbor_max_distance` et `neighbor_min_clearance`, tous deux paramétrables |
| 2 | **repousser entre deux tours** : une passe `mode: seed` ou `resume` sur la spire générée, pour rendre les sommets perdus avant de tirer la suivante |
| 3 | **le sens `in`** : la campagne tourne en `out`. Rien ne dit que l'erreur s'accumule pareil vers l'intérieur, où les spires se serrent |
| 4 | ⚠ **la validation par l'encre.** α dit qu'une feuille est à portée ; il ne dit pas qu'on lit du texte. Le seul juge qui trancherait est un rendu, et six spires en donnent la matière |

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
