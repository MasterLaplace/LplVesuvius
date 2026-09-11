# 96 — Le premier signal dont le signe est le BON, et le plancher qui l'empêche de certifier

> ⭐⭐⭐ **Trois observables, et celle-ci est la première dont le signe soit correct.** `94` (le
> pli) et `95` (la pose sur la matière) disaient *« plus propre »* exactement là où le transfert
> casse. La part de cellules dont un tour de fermeture atterrit hors de la demi-feuille vaut
> **0,621 au cœur et 0,804 au bord**, et **monte** avec la rupture de continuité (**+0,822**).
>
> ⚠⚠⚠ **Et elle ne certifie pourtant aucune cellule** : 0,621 au cœur, là où la continuité est
> intacte (×1,7). Le balayage de fenêtre dit pourquoi — ce n'est pas du bruit, c'est de la
> structure, et elle ne se moyenne pas.

![la fermeture d'un tour](../images/96_la_fermeture_dun_tour.png)

## 1. Pourquoi cette observable après les deux autres

`94` et `95` ont échoué de la **même** façon, et le motif est établi : au bord, l'humain qui ne peut
pas suivre la vraie feuille en trace une autre, **proprement**. Le maillage épouse très bien *une*
feuille — simplement pas la bonne. Ce qui échoue n'est donc pas la **qualité locale** mais
l'**identité** de la feuille, et une observable locale ne peut pas la voir par construction : elle
mesure à quel point on est bien posé sur ce qu'on suit, jamais si c'est ce qu'il fallait suivre.

La **fermeture** est un énoncé d'identité. Partir d'une cellule, faire **un tour complet**, regarder
de combien le rayon a monté : la réponse doit être **un** pas de feuille. Zéro voudrait dire qu'on
est revenu sur la même, deux qu'on en a sauté une. Aucune supervision n'entre — le maillage seul
suffit.

## 2. ⭐⭐ Ce n'est pas la mesure de `91`, et l'argument vient de `91` lui-même

`91` ajuste une **droite** sur tout le rang : c'est le pas *moyen* sur une dizaine de tours, et un
saut et un manque s'y compensent. La fermeture est prise **tour par tour**, donc elle localise.

Et son avertissement fournit l'argument : une pente sur arc court est fausse parce que *« le rayon
oscille avec l'angle, la section n'étant pas un cercle »* — la même bande rend 202 µm sur dix tours
et **1817 sur un**. Or à **exactement 2π** cette oscillation revient sur elle-même. La fermeture est
donc **immune à l'ovalité** là où une pente sur fenêtre courte ne l'est pas. Mesuré sur fixture :
une section ovale à 5 % puis 15 % ne déplace pas la fermeture (0,998 puis 0,993 feuille) et
n'envoie **aucune** cellule hors de la demi-feuille.

## 3. ⚠⚠⚠ Un obstacle d'échelle qui interdit la version naïve

Un pas de cellule le long d'un rang vaut **~905 µm** quand un pas de feuille vaut **~173 µm** : une
cellule fait donc **cinq feuilles**. Indexer *« la cellule un tour plus loin »* par un nombre entier
de colonnes ne peut pas résoudre une feuille, et le faire rendrait un nombre plausible et faux.

La fermeture est donc lue en **interpolant** le rang par son angle déroulé et en l'évaluant à +2π.
L'erreur d'interpolation est la flèche du rang sur un pas de cellule, soit
`905²/(8·20000) ≈ 5 µm` — **trente-cinq fois sous le pas de feuille**. Asséré sur une grille
volontairement grossière (40 colonnes par tour).

## 4. ⭐⭐⭐ La médiane est aveugle, la part non — et c'est la fixture qui le dit

Sur une spirale fabriquée où **une feuille est sautée** au troisième tour :

| | valeur |
|---|---:|
| fermeture **médiane** | **1,000 feuille** — parfaitement aveugle |
| part hors demi-feuille | **0,200** |
| dont *feuille sautée* | 0,200 |
| dont *revenue sur la même* | 0,000 |

⭐ **Une revendication de ce genre ne se vérifie pas sur des données réelles**, où l'on ne sait pas
où est la faute. C'est pourquoi le générateur de spirales vit dans le module et non dans la
batterie.

⚠ Les deux modes sont comptés **séparément** : revenir sur la même feuille et en sauter une sont
deux fautes opposées, et une part unique les mélangerait en un nombre qui ne dit pas quoi corriger.

## 5. ⭐⭐⭐ Le résultat, et le renversement de signe

| tiers | fermeture | dispersion | hors ½ | sautée | continuité |
|---|---:|---:|---:|---:|---:|
| cœur (9 bandes) | 0,998 | 2,30 | **0,621** | 0,348 | ×1,7 |
| milieu (9) | 1,022 | 2,73 | 0,710 | 0,376 | ×5,9 |
| bord (10) | 0,952 | 4,65 | **0,804** | 0,397 | **×31,0** |

Corrélations : **+0,858** avec le rayon, **+0,822** avec la rupture, +0,614 avec le désalignement.

⭐ **Le pas est juste partout** (0,95 à 1,02 feuille) : ce n'est donc pas le pas qui manque, c'est
la fermeture **cellule par cellule**.

## 6. ⚠⚠⚠ Bruit ou structure ? Le balayage de fenêtre répond sans seuil

Du **bruit** se moyenne quand la fenêtre s'allonge ; une **structure** non. C'est la seule façon de
dire laquelle des deux on regarde, et elle ne demande aucun seuil.

| fenêtre | réel (5 bandes) | fixture bruit seul | fixture + saut |
|---:|---:|---:|---:|
| 1 tour | **0,556** | 0,312 | 0,398 |
| 2 tours | 0,530 | 0,061 | 0,211 |
| 3 tours | 0,517 | **0,004** | 0,096 |
| 5 tours | **0,495** | 0,000 | ⚠ 0,002 |

⭐⭐⭐ **Le réel est plat là où le bruit s'effondre.** Allonger la fenêtre ×5 fait tomber le réel de
**11 %** quand le même estimateur écrase un bruit blanc à **zéro**. L'irrégularité radiale des
maillages humains n'est donc **pas du bruit**.

⚠⚠ **La colonne à 5 tours de la fixture n'est pas un témoin** : sur une spirale de huit tours, une
fenêtre de cinq n'en laisse que trois de testables et efface l'échelon elle aussi (0,002). La plage
où le balayage **discrimine** est 2 à 3 tours, et le dire évite de lire une fenêtre trop longue
comme une preuve de propreté.

⚠ Et le corpus **borne** le remède : les bandes du bord ne portent que **deux tours**, donc une
fenêtre plus longue n'y est même pas disponible.

## 7. ⚠⚠⚠ Le balayage a dû être refait à sous-ensemble constant

Ma première version prenait **toutes** les bandes disponibles à chaque fenêtre — 28 à un tour, 5 à
cinq. Or les cinq qui portent cinq tours sont les plus **internes**, donc les plus propres : la
baisse mesurée était celle du **sous-ensemble**, pas celle de la fenêtre.

> **C'est la faute que `93` avait déjà payée** en comparant la bande 0 à la bande 7 en appelant la
> seconde « le bord ».

⭐ Le confondant retiré rend le fait **plus fort** : **11 %** de baisse sur un sous-ensemble
constant, contre les **30 %** que la version confondue annonçait. La forme confondue est gardée à
côté, nommée, parce que les comparer est ce qui montre l'ampleur du confondant plutôt que de le
laisser croire négligeable.

## 8. ⚠⚠ Un défaut de centre trouvé en regardant, pas en relisant

Ma première version indexait le centre d'enroulement **par cellule**. Or `axe_par_tranche` rend un
centre **constant par tranche** de z et l'axe dérive de 12,6 mm (`90`) : deux cellules d'un même
rang qui enjambent une frontière de tranche voient donc des centres écartés de **centaines de
micromètres**, et cet écart tombe directement dans la fermeture.

Mesure du défaut : **22 % des fermetures sortaient négatives** — un maillage qui rentrerait vers
l'intérieur après un tour entier une fois sur cinq. Le centre est désormais **interpolé** en z.

⚠ Un ajustement global comme celui de `91` en est en partie protégé par moyennage ; une fermeture
par tour ne l'est **pas du tout**. Et l'axe reste **partagé par toutes les bandes**, comme `91` et
`93` le font : un centre par bande ferait que *« un pas de feuille »* cesse d'être la même quantité
d'une bande à l'autre.

## 9. ⭐⭐ Ce que ça laisse pour le remplaçant de l'humain

La **direction est bonne** : un invariant topologique est la seule famille dont le signe soit
correct. Et la fixture prouve que l'estimateur **sait** détecter une feuille sautée — 0,096 contre
0,004 à trois tours.

⛔ **Ce qui manque n'est pas l'instrument mais un RÉFÉRENT.** Ces maillages ne ferment pas
eux-mêmes à la demi-feuille près — 62 % des cellules y échouent au cœur, là où tout est intact —
donc ils ne peuvent pas servir à calibrer le seuil d'un automate.

⭐ C'est le **même plancher que `95`** sur un autre axe : *l'erreur du référent, pas la mienne.*
`95` mesurait que la surface publiée n'est pas sur la feuille ; `96` mesure qu'elle ne **ferme** pas
non plus. Une confiance par cellule bâtie sur la fermeture est donc **écrivable et non
calibrable** avec ce corpus.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/la_fermeture_dun_tour.py --verifier
uv run python src/nappe/la_fermeture_dun_tour.py \
    --json docs/mesures/la_fermeture_dun_tour.json
uv run python src/figures/figure_la_fermeture_dun_tour.py --verifier
```
