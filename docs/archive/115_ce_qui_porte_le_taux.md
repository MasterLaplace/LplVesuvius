# 115 — Le rayon ne portait pas le taux : il portait la probabilité que le volume réponde

> ⭐⭐⭐⭐ **LE RÉSULTAT DE `113` EST RETOURNÉ, ET DANS LE BON SENS.** Son rho de **−0,7188** entre
> le rayon et le taux de confirmation se lisait « la matière devient plus dure vers l'extérieur ».
> Elle ne l'est pas. **178 pas sur 560 (31,8 %) ne lisent RIEN**, ils sont concentrés au grand
> rayon, et **aucun des 178 ne confirme**. Sur les **17 marches qui ont lu quelque chose**, le rho
> tombe à **−0,1904 (p 0,4642)** : le rayon **ne survit pas**.
>
> ⭐⭐⭐⭐ **Là où le volume répond, le marcheur confirme 76,18 % de ses pas — à tout rayon.**
> Médiane 0,800 sous 17 mm contre **0,750 au-dessus** (p 0,2579). Une marche partie à 22,17 mm
> confirme aussi bien qu'une partie à 4,07.
>
> ⚠⚠⚠ **ET LE VIDE EST DÉCLARÉ ORIENTÉ : 178 FOIS SUR 178.** `oriente = desaccord <
> barre_moities`, or deux moitiés de rien ne peuvent pas être en désaccord — le désaccord vaut
> exactement 0,00°, donc il passe la barre. Le marcheur croit savoir où il va exactement là où il
> ne lit rien. Quatrième fois que ce dépôt paie cette forme.
>
> ⭐ **Zéro lecture distante** : tout se calcule sur les 560 étapes que `113` a gardées.

![Le rayon ne portait pas le taux](../images/115_le_rayon_ne_portait_pas_le_taux.png)

## 1. Pourquoi ce fichier

`113` a mesuré que le taux de confirmation suit le **rayon** et pas la **profondeur** — donc que le
marcheur n'échoue pas en avançant mais là où il part. La porte `R4-P21` demandait de séparer ce que
le rayon fait varier : l'épaisseur lue, la courbure, et la qualité du scan, dont la page *open
problems* de l'équipe dit elle-même qu'elle est **locale**. « Où » n'est pas « pourquoi ».

⭐ Et c'était mesurable sans rien relire : la course avait gardé, à chacun de ses 560 pas, ce que la
matière montrait à cet endroit — planarité, score du balayage, désaccord des deux moitiés du
gabarit, pas réel, drapeau d'orientation.

## 2. ⚠⚠ Trois covariables sont DANS le critère, et les corréler serait une tautologie

Le prédicat de `102` s'écrit :

```
confirme = (interstices == 1) et (accord > barre_interstice) et (non en_butee)
```

Donc `interstices_traverses`, `accord_de_linterstice` et `en_butee` sont **des termes de la
conjonction dont `confirme` est le résultat**. Demander si l'un prédit l'autre, c'est demander si
une conjonction prédit l'un de ses propres termes : la réponse est oui par construction, elle est
spectaculaire, et elle ne dit rien.

⭐ Elles sont **nommées et écartées** plutôt qu'absentes, et elles servent de **contrôle positif** :
`accord_de_linterstice` rend rho +0,7573 (p 3,0·10⁻⁶) avec le taux. Un test qui ne verrait pas
ça n'aurait aucune puissance, et tous les « pas de lien » de ce document voudraient dire « pas de
puissance ».

⚠ `feuilles_franchies` est écartée **pour parenté** et non pour appartenance : elle sort de la même
lecture de profil que `interstices_traverses`, dont elle est la version continue. C'est la
tautologie qui se voit moins, donc celle qui coûte le plus cher.

## 3. ⚠⚠ L'unité qui décide est la marche, pas le pas

Les 560 pas sont **28 marches de 20**, et les vingt pas d'une marche partagent son rayon, son
départ et ses conditions. Un test par pas prendrait 560 observations pour 28 et publierait des p
vingt fois trop petits. Tous les tests décisifs portent sur **n = 28** ; le niveau du pas n'est
rendu que comme description, et il le dit.

## 4. ⭐⭐⭐⭐ Un pas sur trois ne lit rien

| | |
|---|---:|
| pas gardés | 560 |
| **pas aveugles** | **178 (31,8 %)** |
| confirmés parmi eux | **0** |
| confirmés parmi les 382 voyants | 291 — taux **0,7618** |
| marches aveugles **dès le premier pas** | **4** sur 28 |

⚠⚠ **La signature d'un pas aveugle est CONJOINTE**, jamais un seuil : désaccord exactement 0,00°
**et** planarité exactement 0,000. Prendre l'un des deux seul serait un seuil réglé sur ce qu'on
voit ; les deux ensemble ne peuvent valoir zéro à la fois que sur un cube sans matière, parce que
la planarité d'une vraie feuille n'est jamais exactement nulle et qu'un vrai empilement ne rend
jamais un désaccord exactement nul. Les deux sondes de la batterie l'imposent — un désaccord nul
sur une vraie planarité n'est pas aveugle, et réciproquement.

Et les aveugles ne sont pas répartis. Douze marches, de **4,07 à 16,22 mm**, n'en ont **aucun**.
Au-delà, le volume devient **par plaques** : certaines bandes lisent parfaitement (0,75 à 17,51 mm ;
0,80 à 18,62 ; 0,80 à 20,69 ; 0,75 à 22,17), d'autres ne rendent rien du tout.

## 5. ⭐⭐⭐⭐ Le rayon ne survit pas aux marches qui ont lu

| | rho | p |
|---|---:|---:|
| les **28** marches | **−0,7188** | 1,6·10⁻⁵ |
| les **17** marches voyantes | **−0,1904** | **0,4642** |

| taux médian des voyantes | |
|---|---:|
| sous 17 mm | **0,800** |
| au-dessus | **0,750** |
| Mann–Whitney | **p 0,2579** |

⚠ La coupure de **17 mm** n'est pas ajustée : c'est le rayon de la première marche qui porte un pas
aveugle, donc elle est **lue dans les données**. Un seuil choisi pour que le résultat passe serait
le péché nº 1 de ce dépôt.

⚠ Une marche est **voyante** quand **aucun** de ses pas n'est aveugle, pas « peu ». Une fraction
tolérée serait encore un seuil ; zéro est la seule coupure que personne n'a réglée.

⚠⚠ Ce que ça ne prouve pas : **n = 17** pour le test des voyantes. Un rho qui tombe sous le seuil
**cesse de rejeter** l'absence d'effet, il ne la prouve pas. Ce qui est établi est que le rayon
n'est plus nécessaire pour expliquer ce qu'on voit, pas qu'il ne fait rien.

## 6. ⚠⚠⚠ Le vide est déclaré orienté — 178 fois sur 178

`oriente = bool(isfinite(desaccord) and desaccord < barre_moities)`. Deux moitiés de rien ne peuvent
pas être en désaccord : le désaccord vaut **0,00°**, donc il passe n'importe quelle barre. Le
marcheur porte donc son drapeau de confiance maximale **exactement** sur les pas où il ne lit rien.

⭐ C'est un défaut du **drapeau**, pas de la matière, et il se mesure par un compte plutôt que par
une lecture de code. Quatrième fois que ce dépôt paie cette forme :

| | |
|---|---|
| `54` | cinq rendus vides lus comme cinq surfaces plates (`alive = peak >= floor × max`, vrai partout sur des zéros) |
| `60` | la constante qui rendait le modèle muet, et dont σ lisait « pas d'encre » |
| `41` §6bis | un chunk absent (`numcodecs` manquant) lu comme « pas de matière », donc « graine non couverte » |
| `115` | un cube vide lu comme deux moitiés parfaitement d'accord |

⭐ La loi que ça donne, et elle est transportable : **la signature d'un vide se reconnaît à une
conjonction de grandeurs indépendantes exactement nulles, jamais à un seuil sur l'une d'elles.**

## 7. Ce que ça change pour le graal

- La question du graal est *qu'est-ce qui remplace l'humain qui corrige le transfert de spire à
  spire ?* `113` répondait implicitement « il faudrait corriger la dérive au grand rayon ». Il n'y a
  **pas** de dérive au grand rayon : **là où la matière est lisible, le marcheur tient 76 % de ses
  pas partout**.
- Ce qui manque n'est donc pas un correcteur de trajectoire, c'est de **savoir quand on ne lit
  rien** — et c'est bon marché, puisque la signature est disponible **avant** le pas : le désaccord
  et la planarité sont calculés pour choisir la direction, donc avant que le pas ne soit fait.
- ⚠ Et ce document **ne tranche pas** d'où vient le vide. Trois causes se lisent identiquement dans
  le registre de course : l'extérieur du rouleau n'a plus de matière, il est hors de la région
  chargée, ou des blocs absents sont rendus en zéros (la panne de `41` §6bis). Les séparer demande
  d'interroger le volume aux positions de départ, donc une lecture distante et un autre lot
  (`R4-P22`).

## 8. Les registres

Faits : `R4-F36` (un pas sur trois ne lit rien), `R4-F37` (le vide est déclaré orienté), `R4-F38`
(là où le volume répond, le marcheur tient à tout rayon). Loi `R4-L15`. Portes `R4-P22` (d'où vient
le vide) et `R4-P23` (réparer le drapeau).

⚠⚠ Et `R4-F34` passe à **rétracté** : « le taux suit le rayon » reste vrai comme corrélation et
faux comme cause. La corrélation n'a pas bougé d'un chiffre ; c'est sa lecture qui tombe.

## Reproduire

```bash
uv run python src/nappe/ce_qui_porte_le_taux.py --verifier           # 28 contrôles, hors ligne
uv run python src/nappe/ce_qui_porte_le_taux.py \
    --json docs/mesures/ce_qui_porte_le_taux.json                    # quelques secondes
uv run python src/figures/figure_ce_qui_porte_le_taux.py --verifier  # 14 contrôles
uv run python src/figures/figure_ce_qui_porte_le_taux.py
```

⚠ **Aucune lecture distante** : tout se calcule sur
`docs/mesures/jusquou_va_t_il_si_on_le_laisse.json`, dont `113` a gardé les 560 étapes. Une course
dont les étapes ne sont pas gardées se refait en entier pour chaque question nouvelle — celle-ci a
coûté cinq heures, et cette page en a coûté zéro.
