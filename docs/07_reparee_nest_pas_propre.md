# La réparation ne déplace pas le défaut : une mesure qui le montre

2026-08-17. Résultat sur PHercParis4 (Scroll 1), 46 traces mesurées.
Rejouable : `experiments/src/excision/{proximity,correlate}.py`.

> **En une phrase** : la réparation d'auto-intersection ramène les contacts à zéro
> et **ne change pas** la proximité anormale entre régions non adjacentes. La mesure
> corrèle fortement avec les croisements (rho 0,77, y compris à longueur contrôlée)
> mais **ne sépare pas** proprement les traces saines des réparées — c'est un
> indicateur continu, pas un classifieur.

---

## 1. Le dispositif, et pourquoi il est honnête

Trois traces du **même rouleau**, de **longueur quasi identique** (7,66 / 7,82 /
7,92 tours), donc le confond longueur/qualité identifié en `05` §1 est neutralisé
par construction. Deux d'entre elles couvrent **la même région** (`w038-045`) et
diffèrent d'un facteur **8** en nombre de croisements.

| trace | tours | croisements publiés | rôle |
|---|---|---|---|
| `20231022170901` | 7,66 | **0** | témoin : long **et** propre |
| `20260623143441-w038-045` | 7,82 | 52 | même région, peu atteinte |
| `20260701183126-w038-045` | 7,92 | **408** | même région, très atteinte |

⚠ Données vérifiées **par leur comportement** et non par un manifeste de hashes
(perdu à l'arrêt du récupérateur) : les comptes de triangles concordent exactement
avec la publication (1 047 154 · 3 615 528 · 5 850 912), et les contacts sur la
diagonale publiée aussi (1 584 · 11 673). C'est une vérification plus forte qu'une
somme de contrôle — elle prouve que la donnée est *juste*, pas seulement *intacte*.

## 2. La métrique ordonne correctement, à longueur contrôlée

`fraction_below_third` = part des cellules dont la distance à une partie **non
adjacente** vaut moins du tiers de l'espacement **local**.

| trace | croisements | espacement médian | cellules sous ⅓ |
|---|---|---|---|
| témoin | 0 | 160 µm | **0,09 %** |
| `w038-045` peu atteinte | 52 | 140 µm | 0,15 % |
| `w038-045` très atteinte | 408 | 138 µm | **0,37 %** |

Monotone avec le nombre de croisements, à longueur égale. La métrique mesure donc
la **qualité**, pas la longueur.

## 3. ⭐ Le test qui tranche : elle survit à la réparation

L'objection sérieuse était qu'une métrique de proximité **re-détecte simplement les
croisements** — un site de croisement *est* une approche rapprochée. Ce serait alors
une version dégradée du recensement, sans valeur propre.

Le test : mesurer la trace **réparée**, celle dont le recensement dit désormais zéro.

| état | recensement | espacement | cellules sous ⅓ |
|---|---|---|---|
| avant | **11 673 contacts**, *NOT clean* | 138 µm | 0,37 % |
| **après réparation** | **0 contact**, *clean* | 138 µm | **0,38 %** |
| témoin jamais atteint | 0 contact, *clean* | 160 µm | **0,09 %** |

La réparation retire **3 689 quads** (0,12 % de l'aire), fait tomber les contacts de
11 673 à **zéro**, et la métrique **ne bouge pas** (0,37 → 0,38 %).

> **Passer le recensement d'auto-intersection ne change rien à cette mesure.** La
> réparation ramène les contacts à zéro et laisse la proximité intacte.

C'est le résultat de `05` §4 généralisé : autre rouleau, trace entière, et cette
fois sur un vrai maillage réparé plutôt que sur des sites de croisement isolés.

### ⚠⚠ Correction : « quatre fois au-dessus d'une trace saine » était faux

Cette section a d'abord conclu que la trace réparée (0,38 %) valait **quatre fois**
une trace saine (0,09 %). C'était une comparaison à **un seul** témoin, qui se
trouvait être bas. Mesuré ensuite sur les **7 traces à zéro croisement** de Scroll 1
(mesure `06` 3.9) :

| population | médiane | étendue |
|---|---|---|
| zéro croisement (n = 7) | 0,090 % | **0,020 – 0,372 %** |
| avec croisements (n = 39) | 0,230 % | 0,040 – … |

Une trace parfaitement propre peut donc atteindre **0,372 %**, et la réparée
(0,38 %) est **à peine au-dessus**, pas hors norme. Les distributions se recouvrent :
seules **36 %** des traces atteintes dépassent la pire des saines.

**L'énoncé qui survit** : la réparation **ne déplace pas** la mesure (0,37 → 0,38 %),
donc la métrique voit quelque chose que le recensement ne voit pas. **L'énoncé qui
tombe** : que cette mesure sépare proprement « réparée » de « saine ». Elle ne le
fait pas — c'est un indicateur continu corrélé, pas un classifieur.

## 4. Pourquoi la mesure est construite ainsi

Trois décisions, chacune imposée par une erreur payée avant elle :

1. **Non adjacent se juge dans la PARAMÉTRISATION**, pas dans l'espace. Deux
   cellules voisines dans l'image sont censées être voisines en 3D ; les compter
   noierait le signal sous la continuité ordinaire de la surface.
2. **Normalisation par l'espacement LOCAL**, jamais par une constante. Mesuré :
   l'espacement va de 101 µm (p5) à 303 µm (p90) selon l'endroit, et croît de
   **28 %** du cœur vers l'extérieur (`05` §4bis, `06` 1.11). Une constante
   empruntée à un autre rouleau avait déjà produit une conclusion fausse.
3. **La médiane, pas la moyenne**, pour la référence locale : la grandeur cherchée
   est une queue basse, et une moyenne se laisse tirer par ce qu'on veut détecter.

Ni volume, ni modèle, ni étiquette : la trace seule suffit. Arbre k-d, 0,4 s de
construction sur 1,6 M de points.

## 4bis. La corrélation, sur 46 traces

La §2 portait sur 3 traces. Étendu à **toutes** les traces mesurables de Scroll 1
(46 sur 55 ; les 9 restantes couvrent moins d'un tour, donc ne peuvent pas revenir
près d'elles-mêmes) :

| corrélation de Spearman | rho | p |
|---|---|---|
| proximité ~ **croisements** | **+0,769** | 4,3e-10 |
| proximité ~ **longueur** | −0,232 | 0,12 *(non significatif)* |
| longueur ~ croisements | +0,050 | *le confond, ici absent* |

⚠ **Le confond de `05` n'existe pas dans Scroll 1** (rho = 0,05 entre longueur et
croisements). C'était une particularité de Scroll 5, où les seules traces longues
étaient aussi les seules automatiques.

À longueur contrôlée, par tercile de couverture :

| tercile | couverture | n | rho |
|---|---|---|---|
| 1 | 0,26 – 2,03 tours | 16 | **+0,820** |
| 2 | 2,03 – 3,97 tours | 15 | **+0,944** |
| 3 | 3,98 – 18,03 tours | 15 | **+0,739** |

Fort et significatif dans les trois. La métrique porte donc sur la **qualité**.

Rangs de Spearman et non Pearson : quelques traces portent des centaines de
croisements et la plupart aucun, donc une corrélation linéaire mesurerait surtout
la queue.

## 5. ⚠ Ce que ça ne prouve pas encore

- **La corrélation est établie (46 traces), la séparation ne l'est pas.** La
  métrique est un indicateur continu, pas un classifieur : voir la correction du §3.
- Un seul rouleau, une seule campagne de scan. Scroll 5 se comporte différemment
  (le confond y existe), donc rien ne dit que ces chiffres voyagent.
- ✅ **Le seuil d'un tiers : tranché le 2026-08-18** (voir §8). Il ne peut pas être
  supprimé — aucune grandeur sans seuil ne l'égale — et ce qui le défend est un
  **plateau** de 0,15 à 0,40. Ce n'est pas un paramètre réglé, c'est un **sélecteur de
  queue**, et le plateau montre que la sélection est robuste.
- **On ne sait pas si ces approches nuisent au texte.** C'est la même frontière que
  `04` : on mesure une anomalie géométrique, pas une perte de lisibilité. Le lien
  reste à établir.
- **Aucun plancher** : les 7 traces à zéro croisement s'étalent de 0,020 % à
  0,372 %, un facteur 18. Ce que la mesure attrape sur une trace sans croisement
  reste inexpliqué — vraies approches légitimes, ou bruit de la mesure.

## 6. Ce que ça vaut pour le concours

Les critères des Progress Prizes demandent une **amélioration quantitative sur
données réelles**, sur un problème de la *wishlist*. Les problèmes ouverts nº3
(« détecter et réparer trous, fusions et sauts de spire **sans inspection
humaine** ») et nº7 (« **métriques d'évaluation** ») sont exactement ceci.

Et le résultat a la forme utile : il ne dit pas « notre outil est meilleur », il dit
**« la vérification que tout le monde utilise laisse passer quelque chose, voici la
mesure et voici le contrôle »**.

⚠ En l'état ce n'est pas encore soumissionnable : il manque le seuil non arbitraire
(`06` 3.7) et un second rouleau. Ce qui est acquis, c'est la mesure et son contrôle
négatif — pas encore un outil que quelqu'un d'autre voudrait lancer.

---

## 6. ⚠⚠ La référence locale : le défaut est réel, le remède de principe est faux

2026-08-18. `06` §3.2 avait établi que la ligne de base « locale » de `proximity.py`
n'est pas locale : ±150 colonnes couvrent **96,9 % d'un tour**, et le rayon y varie de
**8,62 mm**, soit 59,5 % de l'étendue radiale. Le constat tient. Ce qui suit est ce
qu'on en fait.

### Le remède évident, et sa mesure

La grandeur mesurée est une **distance 3D**, donc son voisinage de référence devrait
l'être — une boule est locale en rayon par construction, et n'exige pas de connaître
l'axe du rouleau (que `06` §2.3 n'a toujours pas établi). Sur les mêmes 46 traces,
même grandeur, seule la définition de la référence change :

| référence | rho ~ croisements | p | couverture |
|---|---:|---:|---:|
| colonnes ±50 | **+0,805** | 1,6e-11 | 100 % |
| colonnes ±100 | +0,793 | 5,3e-11 | 100 % |
| **colonnes ±150** *(actuelle)* | **+0,769** | 4,3e-10 | 100 % |
| colonnes ±20 | +0,765 | 5,8e-10 | 100 % |
| colonnes ±10 | +0,755 | 1,4e-09 | 100 % |
| boule 400 vx | +0,560 | 5,3e-05 | 100 % |
| boule 200 vx | +0,474 | 8,8e-04 | 94 % |
| boule 100 vx | +0,206 | 0,17 | 24 % |

**Le remède de principe rend la métrique nettement pire**, et les fenêtres en colonnes
forment un **plateau** de ±10 à ±150 : la largeur n'est pas le facteur limitant. Un
gain de +0,036 en passant de 150 à 50 ne vaut pas qu'on retienne 50 — ce serait
retenir la valeur qui a le mieux marché sur ces 46 traces, exactement le piège que
`06` §3.7 évite pour le seuil.

### Deux mesures, et non deux explications

**(1) La non-localité est sans conséquence.** Rapport boule/bande sur les cellules
ordinaires : **1,001** en médiane sur **45 traces**, intervalle p10–p90
**[0,995 ; 1,015]**. Les deux références donnent le même
espacement typique — donc l'espacement ne varie pas assez avec le rayon pour que la
largeur de la fenêtre compte. Le rayon varie beaucoup dans la fenêtre ; l'espacement,
non. C'est cohérent avec l'invariant fort de `11` §3 (rayon / feuilles constant à
**cv 1,8 %**), même si celui-là est mesuré sur un autre rouleau et le long de *z*.

**(2) Et la boule détruit le contraste, spécifiquement là où il est.** Rapport
boule/bande **aux cellules signalées** : **0,766** en médiane, intervalle p10–p90
**[0,454 ; 0,945]**, et l'effondrement est spécifique sur **43 traces sur 45**
(Wilcoxon apparié, **p = 1,4e-09**). Un site de
croisement est une région 3D **compacte** où les cellules sont anormalement proches ;
une boule centrée dessus est donc remplie d'autres cellules du même site, la médiane
tombe à la valeur anormale, et **l'anomalie normalise sa propre référence**.

⚠ La bande de colonnes n'a pas ce défaut pour une raison précise : elle est **étroite
en colonne mais entière en ligne**. Elle traverse tout le segment, donc l'essentiel de
son contenu vient de régions saines même quand son centre est sur une anomalie.

> ⚠⚠ **La leçon, et elle dépasse ce fichier : une référence locale doit être LARGE
> dans la direction où l'anomalie est PETITE.** Être local dans toutes les dimensions
> de l'anomalie, c'est mesurer l'anomalie contre elle-même.

⚠ Deux traces sur 45 vont dans l'autre sens. Et l'ampleur — **23 %** de baisse de
référence aux cellules signalées, contre **0,1 %** partout ailleurs — explique la
**direction** du résultat ; qu'elle suffise à expliquer toute la chute de rho de 0,805
à 0,560 n'est pas établi par cette mesure seule.

⚠ Ce que le contraste des deux chiffres rend difficile à contester : la référence en
boule n'est pas globalement plus basse (elle est à **0,1 %** de la bande partout
ailleurs), elle ne s'effondre **qu'aux endroits qui portent le signal**. Une baisse
uniforme aurait été un décalage d'échelle, sans effet sur un rang de Spearman.

### Reproduire

```bash
cd experiments
uv run python src/excision/baseline_sweep.py \
    ../repos/windcheck/data/scroll1_tifxyz ../docs/baseline_sweep_scroll1.jsonl
uv run python src/excision/variant_correlate.py \
    ../docs/baseline_sweep_scroll1.jsonl ../repos/windcheck/results/index.json
```

---

## 7. 🎯 Le second rouleau : la métrique n'est pas *moins bonne*, elle est **inapplicable**

2026-08-18. `06` §C et le §5 ci-dessus réclamaient un second rouleau. Les 53 traces de
Scroll 5 (PHerc0172) étaient déjà sur disque. Le résultat n'est pas celui qu'on
attendait.

### Ce que la mesure a rendu

Sur les 53 traces, **9 seulement** ont produit une mesure. Les 44 autres : **zéro
cellule mesurée** — pas « peu », zéro.

Et les 9 survivantes sont `auto_grown_20251115002740308_{0..8}` : **neuf morceaux du
même segment**, créés à la même seconde. Ce n'est pas n = 9, c'est **n = 1**.

### ⚠⚠ La coupure est exactement à un tour

| | couverture, en tours |
|---|---|
| les 9 **mesurées** | **2,99 à 9,07** |
| les 44 **écartées** | **0,50 à 1,00** |

Une trace qui ne fait pas un tour **ne peut pas se recouvrir** : il n'existe alors
aucune paire de cellules éloignées dans la paramétrisation et proches en 3D, et c'est
exactement ce que la métrique mesure. Elle ne rend pas un mauvais chiffre — elle ne rend
**rien**.

> **La métrique de `07` exige une trace qui repasse au-dessus d'elle-même.** Ce n'est
> pas un réglage, c'est sa définition. Et personne ne l'avait écrit.

### Ce que ça change

- **`06` §C est répondu**, mais pas comme prévu : le problème n'est pas que les chiffres
  ne voyagent pas, c'est que la population de traces de Scroll 5 est majoritairement
  **hors du domaine de définition** (médiane **0,92 tour**).
- **Le confond longueur/qualité de `05` s'explique** : sur Scroll 5, seules les traces
  longues sont mesurables, donc toute corrélation y est confondue par construction.
- ⚠ La corrélation observée sur ces 9 morceaux (**rho +0,433, p = 0,244**) ne doit pas
  être citée : n = 1 observation indépendante, et aucune trace à zéro croisement.

### 🎯 Et le vrai second rouleau est ailleurs

L'index publié couvre **cinq** corpus, avec des populations très différentes :

| corpus | traces | tours (médiane) | **> 1 tour** |
|---|---:|---:|---:|
| PHerc0814 | 13 | 3,10 | **12** |
| PHerc1667 | 20 | 1,29 | **17** |
| PHerc0139 | 38 | 1,11 | **35** |
| Scroll 1 | 55 | 2,70 | 37 |
| **Scroll 5** | 53 | **0,92** | **10** |

Les trois corpus jamais utilisés sont **majoritairement mesurables**. C'est là qu'est le
test, et leurs traces se récupèrent depuis le bucket ouvert
(`tools/fetch_traces.py`) — `aws` est absent, mais l'API de listage HTTPS accepte un
préfixe par segment, donc on n'énumère pas tout (piège nº 16).

⚠ **Une règle d'applicabilité doit être posée dans l'outil**, pas seulement écrite ici :
une trace sous un tour de couverture doit être **refusée avec sa raison**, pas rendre
« 0 cellule mesurée » — un message qui ressemble à une panne.


---

## 8. ✅ Le seuil d'un tiers : ni arbitraire, ni supprimable

`06` §3.7 l'avait entamé, le §5 ci-dessus le réclamait encore. Tranché.

### Aucune grandeur sans seuil ne l'égale

Mêmes 46 traces, même référence, seule la grandeur corrélée change :

| grandeur | seuil ? | rho ~ croisements |
|---|---|---:|
| `fraction_below_third` | oui, 1/3 | **+0,769** |
| `fraction_below_half` | oui, 1/2 | +0,659 |
| `ratio_p5` (5ᵉ centile du rapport) | **non** — un centile, pas une valeur | **−0,512** |
| `shortfall` (déficit moyen) | **non** | **+0,340** |

Le déficit moyen perd **plus de la moitié** de la corrélation : il est dilué par la
masse des cellules normales. **Le signal est dans la queue extrême**, et toute
statistique qui moyenne sur la distribution entière l'y noie.

⚠ Le centile (`ratio_p5`) est la meilleure des grandeurs sans seuil de valeur, et il
reste loin derrière. Ce n'est donc pas « on n'a pas trouvé la bonne » : c'est que la
grandeur utile *est* une fraction de queue.

### Ce qui le défend : un plateau, pas un réglage

Balayage du seuil sur les mêmes traces :

| seuil | 0,15 | 0,20 | 0,25 | 0,30 | 1/3 | 0,40 | 0,50 | 0,60 | 0,70 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rho | 0,759 | 0,773 | 0,770 | **0,779** | 0,769 | 0,774 | 0,659 | 0,488 | 0,282 |

**De 0,15 à 0,40 — un facteur 2,7 sur le seuil — le rho ne bouge pas** (0,759 à 0,779).
Puis il s'effondre. Un paramètre sur-ajusté produirait un **pic** ; celui-ci produit un
plateau, et 1/3 est simplement dedans.

> **Un seuil qu'on peut multiplier par 2,7 sans que le résultat bouge n'est pas un
> réglage.** C'est le bord d'un régime, et le nommer 1/3 ou 1/4 est indifférent.

⚠ Ce qui **reste** vrai du §5 : le seuil sélectionne une queue dont on ne sait toujours
pas ce qu'elle contient sur une trace sans croisement (facteur 18 entre les 7 traces à
zéro croisement). Le plateau justifie le *choix* du seuil, pas l'interprétation de ce
qu'il attrape.

---

## 9. ⭐⭐ Le rayon de recherche était 4× trop grand — et le bon vient de la physique

2026-08-18. Trouvé en cherchant pourquoi la métrique réplique sur PHerc1667 (+0,700) et
pas sur PHerc0139 (+0,284). J'ai d'abord cru à un effet de **résolution du scan**. Le
contrôle l'a réfuté.

### Le contrôle qui sépare deux explications

Le rayon de recherche est en **voxels**, donc sa valeur *physique* dépend de la
campagne : 80 voxels font **749 µm** à 9,362 µm et **192 µm** à 2,403 µm. Deux lectures
possibles — (a) la résolution fine résout mieux la géométrie, (b) 749 µm est simplement
trop grand. Elles se séparent en balayant le rayon **sur la donnée grossière** :

| rayon | physique | rho ~ croisements | p | traces |
|---|---:|---:|---:|---:|
| 10 vx | 94 µm | +0,446 | 0,064 | 18 |
| **20 vx** | **187 µm** | **+0,609** | **1,3e-04** | 34 |
| 40 vx | 374 µm | +0,459 | 0,0056 | 35 |
| 80 vx *(valeur en vigueur)* | 749 µm | +0,284 | 0,093 | 36 |
| 160 vx | 1498 µm | **−0,143** | 0,407 | 36 |

**Ce n'est pas la résolution : c'est le rayon.** Et au-delà, la corrélation **s'inverse**.

⚠ L'explication est physique et se dit en une phrase : un rayon de 749 µm couvre
**plusieurs écarts inter-feuilles**. Il trouve donc la spire voisine — qui est de la
géométrie parfaitement normale — et noie l'anomalie dedans.

⚠ Un rayon trop petit coûte des traces : à 94 µm, 18 traces sur 36 ne rendent plus
aucune mesure.

### ⚠⚠ Et le bon rayon a été choisi par la PHYSIQUE, pas par la courbe

Balayer puis retenir le meilleur, c'est exactement le sur-ajustement que le §8 évite
pour le seuil. Le pas inter-feuilles a été **mesuré ailleurs et avant** — **142,8 µm,
cv 1,8 %** (`11` §3) — donc ce nombre ne vient pas de cette corrélation et **peut la
faire échouer**.

| corpus | rayon en vigueur (80 vx) | **rayon physique** (142,8 µm) |
|---|---:|---:|
| **Scroll 1** (7,91 µm → 18 vx) | +0,769 | **+0,840**  (p = 1,1e-12) |
| **PHerc0139** (9,362 µm → 15 vx) | +0,284 | **+0,666**  (p = 2,3e-05) |
| ⚠ PHerc1667 (**résolution à vérifier**) | +0,700 | +0,579  (p = 0,019) |

⚠⚠ **Corrigé le 2026-08-19 : PHerc1667 n'a AUCUN volume à 7,91 µm.** Vérifié sur le
bucket : il n'en publie que deux, **2,399 µm** et **1,129 µm**
(`docs/volumes_surface_PHerc1667.txt` le dit aussi). Les deux autres lignes du tableau se
tiennent — leur rayon physique est d'environ **140 µm** (18 × 7,91 et 15 × 9,362) — mais
celle-ci ne peut pas être lue :

- si le rayon **physique** de 140 µm a été appliqué, il vaut **~58 voxels** à 2,399 µm, pas 18 ;
- si **18 voxels** ont été appliqués tels quels, le rayon physique n'était que de **43 µm**,
  soit trois fois moins que sur les deux autres rouleaux — et la comparaison n'est plus appariée.

L'artefact `docs/sweep_PHerc1667.jsonl` **n'enregistre ni le zarr ni la taille de voxel**,
donc rien ici ne tranche. ⏳ **À rejouer en enregistrant la résolution**, et c'est aussi
une leçon d'outillage : *un artefact de mesure doit porter la résolution sur laquelle il a
été pris.*

> **Sur Scroll 1, le rayon issu de la physique (+0,840) bat le meilleur rayon du
> balayage (+0,829 à 16 voxels).** Un paramètre choisi sans regarder la réponse fait
> mieux que celui choisi en la regardant : ce n'est plus un réglage, c'est une
> constante physique du problème.

⚠ **PHerc1667 baisse** (+0,700 → +0,579), et c'est le plus petit corpus (n passe de 18
à 16). Deux corpus sur trois s'améliorent, le troisième se dégrade — à rapporter tel
quel, pas à moyenner.

### 🎯 Et le gain est le plus grand là où le prix se joue

Le gain massif est sur **PHerc0139, à 9,362 µm** : de **non significatif** (p = 0,093)
à **p = 2,3e-05**. Or les **13 rouleaux éligibles au Grand Prize 2027 sont tous scannés
à 8,640–9,362 µm**, et le règlement interdit d'utiliser des scans plus fins du même
rouleau. C'est exactement le régime où la correction compte.

### Reproduire

```bash
cd experiments
uv run python src/excision/baseline_sweep.py <traces> <sortie.jsonl> --search-radius 18
uv run python src/excision/variant_correlate.py <sortie.jsonl> \
    ../repos/windcheck/results/index.json --corpus "Scroll 1"
```
