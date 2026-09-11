# 113 — Jusqu'où va-t-il si on le laisse ?

> ⭐⭐⭐ **Le plafond est ENCORE la mesure.** `107` avait publié une portée de **1 250 µm** sous un
> plafond de six pas que **56 marches sur 56** touchaient. Plafond levé à vingt : **28 marches sur
> 28** le touchent, **zéro** sortie du volume, **zéro** marche arrêtée par quoi que ce soit. Ce qui
> a bougé n'est pas la portée, c'est sa borne inférieure — **3966,3 µm** de médiane, 4870,2 au
> maximum.
>
> ⭐⭐⭐ **Et le résultat n'est pas celui qu'on cherchait.** Le taux de confirmation **ne baisse pas
> avec la profondeur** — précoce 0,56 sur six pas contre tardif 0,50, écart −0,060, **p = 0,3253**.
> Le marcheur ne s'use pas en avançant. Mais il **suit le rayon** : rho de Spearman **−0,7188**,
> **p = 1,6·10⁻⁵** sur 28 bandes de 4,07 à 23,8 mm.
>
> ⭐⭐⭐⭐ **Le marcheur n'échoue pas en avançant, il échoue là où il part** — et les deux n'ont pas
> le même remède. Cette tranche déplace `107` : la question « qu'est-ce qui arrête une marche »
> n'a toujours pas de réponse, et celle qui compte est devenue « où le marcheur cesse-t-il de
> confirmer ».
>
> ⚠⚠ **Les deux agrégats publiés avec la course CACHAIENT ce résultat**, parce qu'ils moyennent
> tous deux sur l'axe où l'écart se trouve. C'est la **figure** qui l'a montré, pas une relecture.

![Chaque marche, pas par pas, et le taux par profondeur](../images/113_le_plafond_est_encore_la_mesure.png)

## 1. Pourquoi cette tranche

`107` mesurait la portée d'un marcheur avec un plafond de **six** pas. Son propre registre le dit :
`marches: 56`, `marches_au_plafond: 56`, `sorties_du_volume: 0`. Un plafond que **tout le monde**
atteint n'est pas une borne observée, c'est un réglage — donc « la portée vaut 1 250 µm » ne disait
rien de la portée. C'est la loi que ce dépôt a payée ailleurs sous sa forme générale : *la grandeur
qu'on mesure est le plafond qu'on a réglé* (`35` §3bis, `47`, `48` §7).

Le plafond est passé à **vingt** pas, soit ~4,6 mm — l'ordre de grandeur auquel la chaîne de `44`
tient encore. Mêmes départs, même sélecteur (`deux_roles`, celui que `105` a corrigé), départs,
étapes et profils **gardés** pour que la course se relise sans être refaite.

## 2. Ce que la course rend

| | |
|---|---:|
| marches | **28** (une par bande) |
| plafond | **20** pas |
| marches au plafond | **28** — part 1,0 |
| sorties du volume | **0** |
| pas parcourus | médiane 20,0, de 20 à 20 |
| longueur | médiane **3966,3 µm**, maximum 4870,2 |
| rayons balayés | 4,07 à 23,8 mm |
| taux de confirmation global | 0,5196 |
| durée | 5 h 11 (18 659,8 s), 28 lectures de profil |

⚠ **`pas parcourus : de 20 à 20`** est la ligne qui compte. Aucune marche n'a été plus courte, donc
aucune n'a été arrêtée : ni par le volume, ni par le critère, ni par rien. Le verdict du module est
`quelque_chose_a_arrete_des_marches: false` et `la_portee_est_encore_censuree: true`.

⚠ Et la longueur médiane est une **borne inférieure**, jamais une portée. La publier seule ferait
exactement ce que `107` a fait avec 1 250 µm ; c'est pourquoi `verifier_chiffres.py` l'apparie au
compte au plafond et refuse qu'elle voyage sans lui.

## 3. Le taux ne baisse pas avec la profondeur

| | |
|---|---:|
| taux précoce (6 premiers pas) | **0,56** |
| taux tardif (6 derniers) | **0,50** |
| écart | **−0,060** |
| p sous un taux constant | **0,3253** |

Le nul n'est pas rejeté. Sur vingt pas — presque quatre millimètres — la marche **ne se dégrade
pas** : un pas au rang vingt est confirmé aussi souvent qu'un pas au rang un.

⚠ C'est un résultat négatif et il est fort : si le marcheur accumulait de l'erreur, c'est ici qu'on
le verrait. La panne n'est donc pas une dérive qui s'installe.

## 4. ⭐⭐⭐⭐ Le taux suit le RAYON

C'est la figure qui a posé cette question. Sa grille dessine **une ligne par marche et une case par
pas**, et les dernières lignes y sont visiblement plus vides que les premières — ce que le taux
global (0,5196) et le taux par profondeur (plat) cachent **tous les deux**, parce qu'ils moyennent
justement sur l'axe où l'écart se trouve.

**D'abord : les marches ne tirent pas au même taux.**

| | |
|---|---:|
| taux par marche | de **0,00** à **0,90** |
| variance observée | 49,3585 |
| variance sous un taux unique | 4,9923 |
| indice de dispersion | **9,887** |
| χ² (27 ddl) | **266,95**, p < 10⁻⁴ |

Le 0,5196 global est donc la moyenne de deux populations, pas le taux d'une population.

**Ensuite : ce qui les sépare est le rayon.** Les bandes sont ordonnées par rayon et chacune porte
une marche, donc le rang se teste.

| | |
|---|---:|
| rho de Spearman (rayon, taux) | **−0,7188** |
| p | **1,6·10⁻⁵** |
| taux de la première moitié | **0,7357** |
| taux de la seconde moitié | **0,3036** |

⚠ **Spearman et non Pearson**, délibérément : on demande si le taux **décroît** avec le rayon, pas
s'il décroît linéairement. Une chute brusque à un rayon donné est une réponse parfaitement bonne à
la première question et rendrait un mauvais coefficient à la seconde.

⚠⚠ **Une corrélation n'est pas une cause.** Le rayon fait varier au moins trois choses à la fois —
l'épaisseur lue, la courbure, et la qualité du scan, dont la page *open problems* de l'équipe dit
elle-même qu'elle est **locale**. Ce test dit **où** le marcheur cesse de confirmer, jamais
**pourquoi**. Les séparer demande de mesurer à rayon égal sur deux rouleaux, ou à qualité égale sur
deux rayons (porte `R4-P16`).

## 5. Ce que ça déplace

`107`, `109` et cette tranche lisaient toutes la même quantité — un taux de confirmation — comme une
propriété du **marcheur**. C'en est une propriété de l'**endroit**.

- La question du graal était : *qu'est-ce qui remplace l'humain qui corrige le transfert de spire à
  spire ?* Une dérive qui s'installe appellerait une correction **en cours de route**, ce qui est
  exactement ce que l'humain fait. Une chute liée au rayon appelle autre chose : un **choix de
  départ**, ou une mesure différente au grand rayon.
- ⚠ Ce que ça ne dit pas : rien ici ne mesure si une marche au grand rayon est *fausse*. Elle est
  **non confirmée**, ce qui veut dire que le critère de `98` ne se déclenche pas — et `109` a déjà
  établi qu'un pas non confirmé n'est pas une chute.

## 6. ⚠ Ce que la figure a corrigé, et ce que ça coûte de ne pas regarder

La première version de la figure dessinait **une barre par marche**, hauteur = pas parcourus.
Comme les vingt-huit marches font toutes exactement vingt pas, elle rendait un **rectangle plein** :
une image qui ne porte aucune information, alors que la mesure en porte trois. La grille qui l'a
remplacée les montre toutes les trois — le mur à droite, le damier, et le vidage de haut en bas.

⚠ Trois défauts de mise en page ont été attrapés par les gardes du dépôt et non par l'œil :
`textes_qui_se_recouvrent` (deux annotations posées **sur** les barres, puis une étiquette d'axe
contre une graduation), et un contrôle de bord bas (une ligne écrite **sous** la toile). La hauteur
de la toile est désormais **dérivée** du nombre de marches ; une constante déborderait le jour où
une campagne en rendrait trente.

## 7. Les registres, et ce qui est enregistré

Faits : `R4-F31` (le plafond est encore la mesure, **borné**), `R4-F32` (le taux ne baisse pas avec
la profondeur), `R4-F33` (les confirmations ne sont pas groupées **dans** une marche, mais les
marches ne tirent pas au même taux), `R4-F34` (le taux suit le rayon), `R4-F35` (les agrégats
cachaient le résultat). Loi `R4-L14`. Portes `R4-P15` et `R4-P16`.

⚠ `R4-F33` **rétracte le jour même** une lecture que ce même run autorisait : « une confirmation
ressemble à un tirage indépendant à p ≈ 0,52 ». C'est vrai **dans** une marche — run médian 1,0,
maximum 8 — et faux **entre** marches, où la dispersion vaut neuf fois ce qu'un taux unique admet.

⚠⚠ Les **vingt** taux par pas ne sont délibérément **pas** enregistrés dans
`verifier_chiffres.py` : ils vivent dans la figure, et les enregistrer créerait vingt obligations de
citation pour une courbe qu'aucune prose n'épellera valeur par valeur — donc vingt échecs
permanents. Une garde rouge en permanence cesse d'être lue (`57` §3).

## Reproduire

```bash
uv run python src/nappe/jusquou_va_t_il_si_on_le_laisse.py --verifier          # 27 contrôles
uv run python src/nappe/jusquou_va_t_il_si_on_le_laisse.py --pas 20 \
    --json docs/mesures/jusquou_va_t_il_si_on_le_laisse.json                   # 5 h 11
uv run python src/nappe/jusquou_va_t_il_si_on_le_laisse.py --reagreger \
    --json docs/mesures/jusquou_va_t_il_si_on_le_laisse.json                   # relire sans refaire
uv run python src/figures/figure_jusquou.py --verifier                         # 15 contrôles
uv run python src/figures/figure_jusquou.py
```

⚠ `--reagreger` relit le JSON et recalcule **tous** les agrégats sans toucher au volume : c'est ce
qui a permis d'ajouter les deux tests du §4 après coup, sans repayer cinq heures. Une course dont
les étapes ne sont pas gardées se refait en entier pour chaque question nouvelle.
