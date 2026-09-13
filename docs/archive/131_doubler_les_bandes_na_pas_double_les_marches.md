# 131 — Doubler les bandes n'a pas doublé les marches qui répondent

> ⭐⭐⭐⭐ **`130` LAISSAIT UNE COMMANDE PRÉCISE — « le remède est plus de MARCHES, pas plus de
> pas » — ET SEIZE BANDES N'EN ONT ACHETÉ QU'UNE.** Huit bandes donnaient **3 marches sur 8** au
> plafond de 112 ; seize en donnent **4 sur 16**. Onze des seize s'arrêtent parce que le volume ne
> répond plus, une sort du champ. Le budget de bandes achète des marches, pas des marches qui vont
> au bout.
>
> ⭐⭐⭐⭐ **ET LA COMPENSATION DES VIRAGES RESTE NON ÉTABLIE, ALORS QUE LA PUISSANCE A DOUBLÉ.**
> `10 marches sur 14`, p **0,19373**, contre **17 sur 19** et p **0,00141** à vingt pas. Le p a
> baissé en doublant n — de 0,375 à 0,19373 — mais la **proportion** a baissé aussi, de **0,895 à
> 0,714**. Ce n'était donc pas seulement un manque de puissance : sur une traversée complète, le
> marcheur corrige **moins**.
>
> ⭐⭐⭐ **LA PORTÉE RESTE NON CENSURÉE** : **4 sur 16** touchent le plafond (**0,25**), contre
> **56 sur 56** à `107`. Le verdict `la_portee_est_encore_censuree` tient sur deux fois plus de
> marches.
>
> ⭐⭐⭐ **ET LE TAUX EST PLUS PLAT QUE JAMAIS** : **0,7526** sur **1043** pas voyants, il ne baisse
> pas avec la profondeur (0,763 contre 0,791, p **0,4885**) et il ne suit pas le rayon — rho
> **−0,025**, p **0,9267** sur seize marches. C'est la réfutation la plus plate de `R4-P21` à ce
> jour.
>
> ⚠⚠ **ET LE COÛT PUBLIÉ DE CETTE COURSE EST FAUX** : `secondes` vaut **60355,1**, dont environ
> neuf heures et demie de **sommeil de la machine**. C'est la dernière course qui le fera.

## 1. Pourquoi ce fichier

`130` a mesuré que le budget de pas n'achète plus de portée au-delà d'une soixantaine de
transferts, et il a nommé sa propre limite : **n = 3 au plafond**, donc la **fréquence** du recul
n'était pas mesurée. Sa commande était explicite — plus de marches, pas plus de pas.

La course est donc relancée à **seize bandes** au lieu de huit, mêmes paramètres, en reprenant les
huit déjà marchées. ⚠ Elle écrit dans un **fichier séparé** : `la_re_course.json` porte les
chiffres que `130` publie, et un producteur qui bouge sous un document publié casse l'appariement.

## 2. ⭐⭐⭐⭐ Ce que seize bandes ont acheté

| | `113`, 20 pas | 8 bandes, 112 pas | **16 bandes, 112 pas** |
|---|---:|---:|---:|
| marches | 24 | 8 | **16** |
| pas voyants | 382 | 624 | **1043** |
| marches au plafond | 17 / 24 | 3 / 8 | **4 / 16** |
| part au plafond | — | 0,375 | **0,25** |
| taux de confirmation | 0,7618 | 0,7468 | **0,7526** |
| marches utilisables pour la dérive | 19 | 7 | **14** |

⭐ **Doubler les bandes a doublé les marches et les pas — et ajouté UNE marche au plafond.** La
raison est dans les arrêts : **11 marches sur 16 s'arrêtent parce que le volume ne répond plus**,
et ce sont les rayons extérieurs. À 13,99 mm une marche fait 35 pas, à 16,93 elle en fait **3**, à
18,06 elle en fait 32.

⚠⚠ **C'est une donnée de planification, et elle se publie parce qu'elle coûte cher à redécouvrir** :
il faut de l'ordre de **quatre bandes pour une marche qui atteint le plafond**, et une bande coûte
environ soixante-dix minutes de lecture. Mesurer la fréquence du recul sur vingt marches
demanderait donc quatre-vingts bandes, soit plusieurs jours de lecture continue.

## 3. ⭐⭐⭐⭐ La compensation n'est pas seulement moins puissante, elle est plus faible

`119` a établi que les virages du marcheur se **compensent** : contre un tirage qui garde
exactement le virage de chaque pas mais en tire la direction au hasard, la marche réelle est plus
droite.

| | marches où le réel est plus droit | réel | simulé | p |
|---|---:|---:|---:|---:|
| 20 pas | **17 / 19** (0,895) | 0,928 | 0,811 | **0,00141** |
| 112 pas, 8 bandes | 5 / 7 (0,714) | 0,665 | 0,438 | 0,375 |
| **112 pas, 16 bandes** | **10 / 14** (0,714) | 0,856 | 0,588 | **0,19373** |

⭐⭐⭐ **Doubler n a fait tomber le p de 0,375 à 0,19373 sans changer la proportion** : elle reste à
**0,714**, exactement celle des sept marches. C'est ce qui distingue les deux lectures possibles —
si seule la puissance manquait, la proportion serait restée à 0,895 et le p aurait plongé. Il a
seulement glissé, parce que l'effet lui-même est plus faible sur une traversée complète.

⚠ **« Plus faible » et non « absent »** : le réel reste plus droit que le tirage dans dix marches
sur quatorze, et la différence de rectitude (0,856 contre 0,588) est large. Ce qui n'est pas
établi, c'est que ce ne soit pas le hasard — à ce n-là.

⚠⚠ Et la voie pour trancher n'est plus d'ajouter des marches : il en faudrait de l'ordre de
quarante à ce taux, donc **cent soixante bandes**. La question se tranchera par une fixture où la
réponse est connue, pas par plus de lecture.

## 4. ⭐⭐⭐ Le net culmine toujours, et ce sont les mêmes marches

Sur les **quatre** marches qui atteignent 112 pas, à population constante, le net médian culmine à
**7638,9 µm au pas 56** puis retombe à **4229,8** au pas 112 pendant que le chemin atteint
**20380,5**.

| rayon | maximum du net | au pas | au plafond |
|---:|---:|---:|---:|
| 4,07 mm | 8931,2 µm | 65 | **3726,5** |
| 9,40 mm | 8163,5 µm | 47 | **1597,2** |
| 11,57 mm | 14089,4 µm | 112 | 14089,4 |
| 15,46 mm | 4733,0 µm | 112 | 4733,0 |

⭐ **Les deux marches qui reculent sont exactement celles de `130`**, et les deux nouvelles sont
**monotones**. Le compte des marches qui reculent n'a donc pas bougé : **2**, sur 3 puis sur 4.
`le_budget_achete_de_la_portee` reste **faux**.

⚠ **n = 4.** La fréquence du recul n'est toujours pas mesurée, et c'est la même limite que `130`
nommait — seize bandes ne l'ont pas levée.

## 5. ⚠⚠ La rectitude, et le confondant que le contrôle retire encore

| | rho(pas, rectitude) | p | à longueur égale | p | marches |
|---|---:|---:|---:|---:|---:|
| 8 bandes | −0,8295 | 0,0109 | −0,1482 | 0,7511 | 7 |
| **16 bandes** | **−0,7763** | **0,0004** | **−0,3511** | **0,2183** | **14** |

La rectitude décroît avec la longueur de la marche, et à seize bandes le p brut tombe à
**0,0004**. ⚠⚠ **Et le contrôle à longueur égale la retire encore** : rho **−0,3511**, p
**0,2183**. Une marche d'un pas a une rectitude de 1,000 par construction, donc toute marche
courte est mécaniquement plus droite qu'une longue, et un jeu qui porte beaucoup de marches
courtes — ce que seize bandes ajoutent — renforce le confondant sans rien apprendre.

⚠ Le point estimé à longueur égale est plus négatif qu'à huit bandes (−0,3511 contre −0,1482), donc
un effet réel mais faible n'est pas exclu. Il n'est pas établi.

⭐ La même remarque vaut pour les médianes : la rectitude médiane passe de **0,7597** (8 bandes) à
**0,8563** (16), et l'angle entre les deux moitiés d'une marche de **56,3°** à **29,0°**. Ce n'est
pas une amélioration du marcheur, c'est l'arrivée de marches courtes dans le lot. **Deux médianes
sur des lots de longueurs différentes ne se comparent pas.**

## 6. ⭐⭐⭐ Le taux, et la réfutation la plus plate

| | |
|---|---:|
| taux de confirmation global | **0,7526** |
| précoce contre tardif | 0,763 / 0,791, p **0,4885** |
| rho avec le rayon | **−0,025**, p **0,9267** |

`113` publiait rho **−0,719** entre le taux et le rayon, et `115` a mesuré que cette corrélation
était portée par les marches qui ne lisent rien. Sur seize marches d'une traversée complète, avec
arrêt au premier pas aveugle, rho vaut **−0,025**. La prémisse de `R4-P21` est réfutée à la plus
grande échelle dont le dépôt dispose.

⚠ `le_taux_depend_il_de_la_marche` reste **indécidable** et le dit : les marches n'ont pas toutes le
même nombre de pas, donc le test d'une binomiale unique ne s'applique pas.

## 7. ⚠⚠ Le coût publié de cette course est faux, et le dire est le correctif

`secondes` vaut **60355,1** pour cette course. L'hôte a dormi environ neuf heures et demie au
milieu, et `time.time()` a compté ce sommeil comme du travail : le coût annoncé n'est pas le coût.

⭐ Le dépôt mesure désormais ses durées avec `maintenant()`, monotone, qui s'arrête avec la
machine — et `avancement` **refuse** un départ pris sur l'autre horloge plutôt que d'afficher une
durée de 1,7 milliard de secondes. Cette course est la dernière à porter le défaut, parce qu'elle
tournait déjà quand il a été corrigé.

## 8. Ce que ça change pour le graal

- ⭐⭐⭐⭐ **La commande de `130` est exécutée et elle ne suffit pas.** Plus de marches ne donne pas
  plus de marches qui vont au bout, parce que ce qui arrête onze marches sur seize n'est pas le
  budget mais le volume qui cesse de répondre. **La question de la fréquence du recul ne se
  tranchera pas par plus de lecture.**
- ⭐⭐⭐ **Et elle désigne ce qui reste** : une fixture où la réponse est connue. Le dépôt en a une
  depuis peu — `VolumeFabriqueEnSpirale`, dont la normale **tourne**, donc où un cap rigide coûte
  quelque chose. Sur une pile plane, garder la direction de départ est gratuit et donnerait raison
  à n'importe quelle proposition ; c'est là que la question du cap peut être tranchée sans
  attendre des jours de lecture.
- ⚠⚠ **Ce qui est confirmé et qui compte** : la portée n'est plus censurée, le taux est stable et
  indépendant du rayon, et le net culmine avant le plafond pour les mêmes deux marches. Rien de ce
  que `130` établit n'est corrigé ; ce qui change est ce qu'on sait de sa **puissance**.
- ⚠ **Onze arrêts sur seize sont « plus rien à lire »**, donc ce qui est mesuré reste la portée du
  couple marcheur-volume et non celle de la matière. `R4-P22` reste ouverte.

## 9. Les registres

Faits `R4-F62` (le budget de bandes n'achète pas des marches qui vont au bout : 3/8 puis 4/16, et
il faut de l'ordre de quatre bandes par marche utile) et `R4-F63` (la compensation des virages est
plus faible sur une traversée complète, pas seulement moins puissante : la proportion tombe de
0,895 à 0,714). `R4-P20` gagne ce que coûte la mesure de la fréquence, et l'issue qui reste. Aucune
porte nouvelle.

## Reproduire

```bash
uv run python src/nappe/jusquou_va_t_il_si_on_le_laisse.py \
    --pas 112 --bandes 16 --arret-sur-vide --reprendre \
    --json docs/mesures/la_re_course_large.json          # reprend les 8 bandes de `130`
uv run python src/nappe/le_marcheur_derive_t_il.py \
    --course docs/mesures/la_re_course_large.json \
    --json docs/mesures/le_marcheur_derive_sur_la_course_large.json
```

⚠ **Le même instrument que `119` et `130` tourne sur les trois courses** — c'est ce qui rend les
trois colonnes comparables. Un second instrument aurait comparé trois lectures au lieu de trois
courses.
