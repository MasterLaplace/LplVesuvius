# 130 — Le budget de pas n'achète plus de portée

> ⭐⭐⭐⭐ **LA PORTÉE CESSE D'ÊTRE CENSURÉE, ET LA PREMIÈRE CHOSE QU'ELLE DIT EST QUE LE PLAFOND
> N'ÉTAIT PAS LE MUR.** Huit marches à 112 pas : **3 sur 8** touchent le plafond, quatre s'arrêtent
> parce que le volume ne répond plus, une sort du champ. `107` avait **56 sur 56** au plafond de six
> pas, portée entièrement censurée.
>
> ⭐⭐⭐⭐ **ET CE QUE LE BUDGET ACHÈTE N'EST PAS DE LA PORTÉE, C'EST DU CHEMIN.** Sur les trois
> marches qui vont au bout, le déplacement **net** culmine à **8931,2 µm au pas 65** puis
> **retombe à 3726,5 µm au pas 112**, pendant que le chemin parcouru continue de croître jusqu'à
> **20389,8 µm**. **Deux marches sur trois culminent AVANT le plafond**, contre **zéro sur
> dix-sept** au plafond de vingt pas.
>
> ⭐⭐⭐ **C'EST LA PANNE QUE `119` AVAIT NOMMÉE SANS POUVOIR LA VOIR** : *« une marche peut
> confirmer ses vingt pas en tournant lentement pour longer la feuille au lieu de la traverser »*.
> À vingt pas ses virages **se compensaient** (0,928 contre 0,811, 17 marches sur 19, p **0,00141**).
> À cent douze, ce n'est plus établi : **0,665 contre 0,438**, **5 marches sur 7**, p **0,375**.
>
> ⚠⚠⚠ **ET LE TAUX NE VOIT RIEN DE TOUT ÇA** : il vaut **0,7468** sur la traversée entière, il ne
> baisse pas avec la profondeur (0,762 contre 0,787, p **0,6162**) et il ne suit pas le rayon
> (rho **+0,0952**, p **0,8225**). Une marche qui revient sur ses pas confirme aussi bien qu'une
> marche qui avance.
>
> ⚠⚠ **ET UNE LECTURE DE MA PART A ÉTÉ CORRIGÉE PAR SON PROPRE CONTRÔLE.** La rectitude décroît
> avec la longueur de la marche — rho **−0,8295**, p **0,0109** — et j'allais en conclure que les
> marches longues sont de mauvaises marcheuses. **À longueur égale, l'effet disparaît** :
> rho **−0,1482**, p **0,7511**. C'est la longueur qui coûte, pas la marche.
>
> ⚠ **n = 3 au plafond.** Ce document établit qu'une marche peut reculer, pas à quelle fréquence.

## 1. Pourquoi ce fichier

`R4-P20` demande ce qui mesurerait la portée des marches qui lisent, et le dépôt n'a jamais pu
répondre : `107` a mis **56 marches sur 56** au plafond de six pas, `113` **28 sur 28** au plafond
de vingt. Une portée entièrement censurée n'est pas une portée, c'est un budget.

La re-course lève le plafond à **112** — le nombre que `plafond_pour_traverser` dérive de la
géométrie, et non un chiffre choisi — et laisse la marche s'arrêter d'elle-même (`--arret-sur-vide`).

⚠ Aucune lecture neuve ici : la course a gardé ses étapes, donc tout ce document se calcule dessus.
C'est la promesse que le fichier de `113` s'était faite — *« une lecture de plus par marche, et
toute relecture future devient gratuite »* — encaissée.

## 2. ⭐⭐⭐⭐ Ce qui arrête les marches, enfin

| rayon | pas | confirmés | chemin | arrêt |
|---:|---:|---:|---:|---|
| 4,07 mm | 112 | 85 | 20389,8 µm | plafond |
| 6,32 mm | 71 | 49 | 13460,5 µm | plus rien à lire |
| 8,02 mm | 2 | 1 | 95,2 µm | sortie du volume |
| 9,40 mm | 112 | 86 | 20371,3 µm | plafond |
| 10,51 mm | 101 | 72 | 18676,2 µm | plus rien à lire |
| 11,57 mm | 112 | 84 | 21193,8 µm | plafond |
| 12,48 mm | 67 | 48 | 12491,3 µm | plus rien à lire |
| 13,27 mm | 52 | 41 | 9065,9 µm | plus rien à lire |

**3 sur 8 au plafond**, soit **0,375**. Le verdict du module bascule : `la_portee_est_encore_censuree`
vaut **False**, contre **True** pour les 56 marches de `107`.

⚠ **Mais quatre des cinq arrêts sont « plus rien à lire »**, c'est-à-dire que le volume cesse de
répondre. Ce n'est donc pas la portée de la *matière* qui est mesurée, c'est celle du couple
marcheur-volume — `R4-P22` reste ouverte et ce document ne la touche pas.

## 3. ⭐⭐⭐⭐ Le net culmine, puis recule

Le chemin parcouru n'est pas une portée : une marche qui tourne parcourt sans emmener. Ce qui se
mesure est le **déplacement net**, qui ne demande ni rayon ni axe, donc qui échappe au confondant
que `119` déclare pour l'angle au radial.

⚠⚠ **La population est tenue constante**, et sans ça la courbe ment : prendre à chaque rang toutes
les marches qui y arrivent ferait changer l'échantillon sous la courbe, et un net qui baisse
pourrait n'être que la disparition des bonnes marches. Seules les **trois** marches qui atteignent
112 pas sont gardées.

| pas | chemin médian | net médian |
|---:|---:|---:|
| 9 | 1608,9 | 1571,9 |
| 19 | 3546,5 | 3041,3 |
| 28 | 5267,8 | 4738,0 |
| 37 | 7223,6 | 6355,0 |
| 47 | 8971,0 | 8163,5 |
| 56 | 10424,5 | 7737,0 |
| **65** | 12075,7 | **8931,2** |
| 75 | 14325,8 | 8174,2 |
| 84 | 15874,3 | 6718,9 |
| 93 | 17500,4 | 5278,9 |
| 103 | 18927,8 | 4115,4 |
| 112 | **20389,8** | **3726,5** |

Marche par marche : à 4,07 mm le maximum vaut **8931,2 µm au pas 65** et le plafond rend
**3726,5** ; à 9,40 mm, **8163,5 au pas 47** contre **1597,2** ; à 11,57 mm la marche est la
seule à progresser jusqu'au bout, **14089,4 µm**.

⭐ **Deux marches sur trois culminent avant le plafond**, donc `le_budget_achete_de_la_portee`
vaut **False**. Le même instrument sur la course de vingt pas rend **0 sur 17** et **True** : à
vingt pas, chaque marche gagnait encore au dernier pas.

⚠ **Le verdict est un compte, pas une moyenne.** Une médiane dirait « le net recule » d'un lot où
une seule marche recule beaucoup, et la marche qui continue tout droit serait invisible. Elle est
là, et elle compte.

⚠⚠ **Ce que ça ne distingue pas** : une marche qui revient sur ses pas et une marche qui fait le
tour du rouleau en longeant une feuille rendent toutes deux un net qui plafonne. La rotation
cumulée autour de l'axe est mesurée à côté — médiane **−22,1°**, étendue **[−79,2 ; 173,5]** — et
c'est elle qu'il faut lire pour les séparer. Une marche va jusqu'à un demi-tour du rouleau.

## 4. ⚠⚠ La lecture que son propre contrôle a corrigée

La rectitude — le net rapporté au chemin — décroît avec la longueur de la marche : rho
**−0,8295**, p **0,0109** sur huit marches. J'allais écrire que les marches longues sont de
mauvaises marcheuses, et le tableau y invitait : 0,183 et 0,078 pour deux des trois qui vont au
bout, contre 0,932 et 0,923 pour deux qui s'arrêtent tôt.

⚠⚠⚠ **C'est un confondant mécanique, et il était écrit d'avance** : une marche d'un pas a une
rectitude de 1,000 par construction, et toute marche courte est mécaniquement plus droite qu'une
longue. Le contrôle tronque donc **toutes** les marches à la même longueur — **28 pas**, sept
marches — et l'effet **disparaît** : rho **−0,1482**, p **0,7511**. Tronquées, les mêmes marches
rendent 0,799 · 0,945 · 0,964 · 0,692 · 0,867 · 0,934 · 0,873.

⭐ **Donc la marche ne se gâte pas : elle se courbe, et la courbure s'accumule.** Les deux marches
qui finissent à 0,18 et 0,08 sont droites sur leurs 28 premiers pas.

## 5. ⭐⭐⭐ La compensation de `119` ne tient pas la distance

`119` a établi que les virages du marcheur se **compensent** : contre un tirage qui garde
exactement le virage de chaque pas mais en tire la direction au hasard, la marche réelle est plus
droite — **0,928 contre 0,811**, sur **17 marches sur 19**, p **0,00141**. Il ne se contente pas de
ne pas dériver, il revient.

Le même témoin sur la traversée complète : **0,665 contre 0,438**, **5 marches sur 7**, p **0,375**.

| | 20 pas | 112 pas |
|---|---:|---:|
| rectitude médiane | **0,9323** | **0,7597** |
| étendue | [0,3533 ; 1,0000] | [0,0784 ; 1,0000] |
| net médian | 3121,6 µm | 9637,8 µm |
| chemin médian | 3525,1 µm | 16068,4 µm |
| angle entre les deux moitiés | **20,5°** | **56,3°** |
| au pire | 140,0° | **177,8°** |
| les virages se compensent | **oui** (p 0,00141) | **non établi** (p 0,375) |

⚠⚠ **« Non établi » et « faux » ne sont pas la même chose**, et n = 7 est la raison pour laquelle
on ne peut pas trancher : le sens est le même (le réel reste plus droit que le tiré), c'est la
puissance qui manque. Le remède est **plus de marches**, pas plus de pas — et c'est une commande
précise pour la prochaine course.

⭐ **Le chemin est multiplié par 4,6 et le net par 3,1.** Le budget n'est pas inutile ; il rend
moins que ce qu'il coûte, et au-delà d'une soixantaine de transferts il rend négatif.

## 6. ⚠⚠⚠ Et le taux ne voit rien de tout ça

| | |
|---|---:|
| taux de confirmation global | **0,7468** |
| précoce contre tardif | 0,762 / 0,787, p **0,6162** |
| rho avec le rayon | **+0,0952**, p **0,8225** |

Le taux tient sur 112 pas comme il tenait sur vingt — `115` publiait **0,7618** — il ne baisse pas
avec la profondeur et il ne suit pas le rayon, ce qui confirme à pleine échelle la réfutation de
`R4-P21`.

⚠⚠ **Et c'est précisément le problème.** Une marche dont le net retombe de 8931 à 3727 µm garde
un taux indiscernable de celle qui progresse. Le prédicat vérifie qu'un pas a franchi **un**
interstice ; il ne vérifie pas dans quel **sens**. C'est le troisième document d'affilée à mesurer
que `confirme` est aveugle à ce qui compte — `129` pour la garde des moitiés, `128` pour la faille,
celui-ci pour la direction.

⚠ `le_taux_depend_il_de_la_marche` est rendu **indécidable** et non faux : les marches n'ont pas
toutes le même nombre de pas, donc le test d'une binomiale unique ne s'applique pas.

## 7. Ce que ça change pour le graal

- ⭐⭐⭐⭐ **`R4-P20` a sa réponse, et ce n'est pas celle qu'on espérait.** La portée n'est pas
  limitée par un budget de lecture : elle est limitée par le fait que la marche cesse d'emmener
  vers 60 à 70 transferts. Lever le plafond de 20 à 112 multiplie le chemin par 4,6 et le net par
  3,1, et pour deux marches sur trois le dernier tiers du budget est **négatif**.
- ⭐⭐⭐ **Ce qui manque n'est donc pas un meilleur pas, c'est un CAP.** Le module n'a qu'un seul
  bit de supervision — le sens initial — et il est écrit dans son propre code : *« retourner pour
  CONTINUER, jamais pour viser »*. Ce bit tient vingt transferts. Il n'en tient pas cent.
- ⚠⚠ **Et l'humain qu'il faut remplacer fait exactement ça** : il tient le cap d'une spire à la
  suivante. `124` et `127` ont mesuré qu'il recoud les déchirures ; ce document mesure qu'il
  **oriente**, et que c'est la fonction dont le mécanisme est le plus dépourvu.
- ⚠ **Trois marches.** Ce document établit qu'une marche peut reculer sur la seconde moitié de son
  budget, pas à quelle fréquence — et la prochaine course doit élargir les marches avant
  d'allonger les pas.

## 8. Les registres

Faits `R4-F60` (le budget n'achète plus de portée au-delà d'une soixantaine de transferts, et la
portée cesse d'être censurée) et `R4-F61` (la rectitude tombe de 0,9323 à 0,7597 et la compensation
des virages n'est plus établie). `R4-P20` **passe de « ce qui mesurerait la portée » à la portée
mesurée**, avec ce qui la borne. Aucune porte nouvelle.

## Reproduire

```bash
uv run python src/nappe/jusquou_va_t_il_si_on_le_laisse.py \
    --pas 112 --bandes 8 --arret-sur-vide --json docs/mesures/la_re_course.json   # ~7 h
uv run python src/nappe/jusquou_va_t_il_si_on_le_laisse.py --verifier             # 47 contrôles
uv run python src/nappe/le_marcheur_derive_t_il.py --verifier                     # 44 contrôles
uv run python src/nappe/le_marcheur_derive_t_il.py \
    --course docs/mesures/la_re_course.json \
    --json docs/mesures/le_marcheur_derive_sur_la_re_course.json
```

⚠ **Zéro lecture distante après la course.** Le même instrument que `119` tourne sur les deux
courses — c'est ce qui rend les deux colonnes comparables, et un second instrument aurait comparé
deux lectures au lieu de deux courses.

⚠ La course a été **reprise** après un redémarrage de l'hôte : deux bandes venaient d'un brouillon
antérieur. La reprise est refusée dès qu'un paramètre diffère, et la marche est déterministe, donc
une bande reprise est exactement celle qu'on aurait remarchée.
