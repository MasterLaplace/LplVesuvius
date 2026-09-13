# 132 — Le marcheur n'avait pas de gouvernail, et la matière ne lui demande presque aucun virage

> ⭐⭐⭐⭐ **EN CHERCHANT OÙ BRANCHER LE CAP QUE `130` RÉCLAME, LE CODE A RÉPONDU QU'IL N'Y AVAIT
> NULLE PART.** `sens` ne choisit que le **signe** : la direction d'un pas est entièrement celle du
> tenseur local, et `sens` résout seulement le ±. Il n'existait donc aucun mécanisme par lequel un
> cap aurait pu agir. `marcher` en reçoit un ici, et une mémoire nulle rend **exactement** le
> marcheur d'avant.
>
> ⭐⭐⭐⭐ **ET LA MATIÈRE ENROULÉE NE DEMANDE PRESQUE AUCUN VIRAGE.** Sur une traversée radiale
> complète — rayon **8000** à **27358,8 µm** — la normale vraie tourne de **0,1571°** en tout, soit
> **0,0103° par pas**. Le marcheur, lui, vire de **2,83° par pas**. Un facteur **273,9**.
>
> ⭐⭐⭐⭐ **ET SUR LA VRAIE MATIÈRE, LE VIRAGE ALTERNE.** Le cosinus entre deux virages consécutifs
> vaut **−0,2061** en médiane, **14 marches sur 14** négatives, p **0,000122**. Un virage qui
> persiste est une matière qui courbe ; un virage qui alterne est du **bruit** — et c'est
> exactement ce qu'une moyenne enlève.
>
> ⭐⭐⭐ **LA MÉMOIRE RÉDUIT L'ERREUR À LA VÉRITÉ ET NE COÛTE RIEN** : l'écart à la normale connue
> passe de **1,965°** à **0,699°** entre λ = 0 et λ = 0,75, pour un coût en taux de **0,0**.
>
> ⚠⚠⚠ **MAIS AUCUNE FIXTURE DU DÉPÔT NE REPRODUIT LA DÉRIVE DU VRAI ROULEAU.** Sur la pile plane
> bruitée qui porte `124`, `127` et `128`, le marcheur rend une rectitude de **0,9994** sur cent
> douze pas et confirme **tout**. Le bruit d'intensité ne fait pas dériver, donc la proposition de
> cap ne peut pas y être validée : il n'y a rien à réparer.

## 1. Pourquoi ce fichier

`130` a mesuré que le budget de pas n'achète plus de portée et que ce qui manque est un **cap** ;
`131` que la fréquence du recul ne se tranchera pas par plus de lecture. Restait à brancher un cap
et à mesurer ce qu'il coûte là où la matière tourne.

## 2. ⭐⭐⭐⭐ Il n'y avait pas de gouvernail

Le pas se choisit en deux temps : le tenseur de structure rend un **axe**, puis `sens` décide
laquelle des deux directions opposées prendre. Le commentaire du module le dit déjà — *« retourner
pour CONTINUER, jamais pour viser : le seul bit de supervision est le sens initial »* — mais la
conséquence n'avait pas été tirée : **la direction d'un pas ne dépend de l'histoire de la marche
que par un signe.** Un cap n'aurait rien eu à piloter.

`marcher` reçoit donc `memoire_du_cap` : la direction retenue est une moyenne exponentielle,
`(1 − λ) × lecture + λ × direction précédente`.

- ⭐ **Une mémoire nulle rend exactement le marcheur d'avant** — `(1−0)·d + 0·sens` vaut `d`, sans
  arrondi — donc aucune signature du dépôt ne bouge. La batterie l'asserte au lieu de s'y fier, et
  une sonde exige qu'une mémoire **non** nulle change bien les directions, sans quoi le paramètre
  serait inerte et tout ce qui suit mesurerait deux fois la même marche.
- ⚠ Le cap est `sens` et non une seconde variable. Ma première version en gardait une, toujours
  égale : deux noms pour une chose sont deux choses qui peuvent se contredire.
- ⚠ Le cap part du sens initial, parce que c'est le seul bit de supervision que la marche reçoit.
  Lui en donner un autre ajouterait une supervision que le graal n'aura pas.

## 3. ⭐⭐⭐⭐ La matière enroulée ne demande presque aucun virage

| | |
|---|---:|
| rayon parcouru | 8000 → **27358,8 µm** |
| angle parcouru autour de l'axe | **0,2806°** |
| virage de la normale VRAIE, en tout | **0,1571°** |
| ... par pas | **0,0103°** (max 0,0727) |
| virage du MARCHEUR, par pas | **2,83°** (max 8,24) |
| facteur | **273,9×** |

⚠⚠⚠ **Et c'est une correction de la prémisse qui a fait construire la spirale.** J'avais écrit
qu'une pile enroulée ferait payer un cap rigide puisque sa normale tourne. Elle tourne avec
l'**angle** — or un marcheur qui traverse des feuilles avance **radialement**, donc à angle presque
constant : 0,28° sur toute la traversée. La normale, presque radiale partout, ne bouge donc pas
sous lui.

⭐ **C'est un fait de géométrie et non un choix de paramètre.** Aucun pas, aucun rayon, aucune
graine ne le change : pour un marcheur qui croise des feuilles, un enroulement idéal ne demande
rien. Donc **un cap n'a rien à combattre**, et sa seule fonction est d'enlever du bruit.

## 4. ⭐⭐⭐⭐ Et sur la vraie matière, le virage alterne

Le virage est pris comme un **vecteur** — la composante du pas suivant perpendiculaire au pas
courant — et non comme un angle : deux virages de même amplitude dans des sens opposés ont le même
angle, et c'est précisément la différence qu'il faut voir.

| | |
|---|---:|
| cosinus entre virages consécutifs, médiane | **−0,2061** |
| étendue | **−0,321** à **−0,0373** |
| marches négatives | **14 / 14** |
| p contre zéro | **0,000122** |

⭐⭐⭐ **Le marcheur oscille.** Un virage qui persisterait signerait une matière qui courbe, et un
cap qui se souvient la combattrait ; un virage qui alterne est du bruit, et c'est le cas exact
qu'une moyenne exponentielle est faite d'enlever. C'est aussi le mécanisme derrière les *« virages
qui se compensent »* de `119` : ils se compensent parce qu'ils alternent.

⚠ L'unité décisive est la marche : les virages d'une même marche partagent sa matière, donc les
compter comme indépendants gonflerait n d'un facteur vingt.

## 5. ⭐⭐⭐ La mémoire réduit l'erreur, et ne coûte rien

Sur la spirale, l'erreur est mesurée contre la **normale vraie** — ce que seule une fixture permet.
Sur le vrai volume on ne peut comparer le marcheur qu'à lui-même, donc « il va plus droit » n'y
voudrait dire que « il change moins d'avis ».

| mémoire | erreur médiane | erreur max | taux | gain | coût |
|---:|---:|---:|---:|---:|---:|
| 0,00 | **1,965°** | 6,400° | 1,000 | — | — |
| 0,25 | 1,473° | 3,795° | 1,000 | 0,492 | **0,0** |
| 0,50 | 1,099° | 2,814° | 1,000 | 0,866 | **0,0** |
| 0,75 | **0,699°** | 1,802° | 1,000 | **1,266** | **0,0** |

Le test est apparié graine par graine : la même réalisation de bruit est marchée à chaque mémoire.

⚠ **Et le tableau ne montre aucun coût**, ce qui est cohérent avec le §3 — sur un enroulement
idéal la mémoire n'a rien à combattre. **Ce n'est donc pas une preuve que le cap est gratuit sur
un vrai rouleau** : c'est la mesure de ce qu'il coûte là où la matière ne tourne pas.

⚠ Quatre valeurs et non un balayage : chercher la meilleure mémoire sur le corpus qui sert à juger
serait régler un seuil sur ce qui passe.

## 6. ⚠⚠⚠ Et la pile plane ne dérive pas du tout

| | |
|---|---:|
| rectitude médiane, 112 pas | **0,9994** |
| virage du marcheur | 2,4° / pas |
| taux de confirmation | **1,000** |

Sur la fixture qui porte `124` (la déchirure), `127` (le lien latéral) et `128` (la faille) —
obliquité 35°, bruit 8, les paramètres que ces tranches emploient — **le marcheur va parfaitement
droit sur une traversée complète**. `130` mesure sur le vrai rouleau des rectitudes de **0,183** et
**0,078**.

⭐ **Le contrôle montre que le verdict peut rendre vrai** : à bruit 60 la même pile fait dériver.
« Elle ne dérive pas » n'est donc pas vrai par construction.

⚠⚠⚠ **La conséquence est lourde et elle vaut pour tout ce qui précède** : le bruit d'intensité ne
fait pas dériver le marcheur. Donc une proposition de cap ne peut **pas** être validée sur les
fixtures du dépôt — elle n'y aurait rien à réparer, et paraîtrait inutile ou inoffensive selon le
hasard. Ce qui manque à ces piles n'est pas plus de bruit : c'est que leurs feuilles sont
**parfaitement parallèles**.

## 7. Ce que ça change pour le graal

- ⭐⭐⭐⭐ **Le cap existe désormais, et il est presque gratuit là où on peut le mesurer** : la
  matière ne demande que 0,0103° de virage par pas, et le virage réel **alterne**, donc c'est
  exactement ce qu'une mémoire enlève. C'est la première proposition de mécanisme de cette
  campagne dont la mesure dit qu'elle devrait marcher.
- ⚠⚠ **Et elle ne peut pas être validée avant une course qui l'emploie.** Changer la direction
  change où le marcheur va, donc le tester demande de relire le volume — aucune relecture des
  courses gardées ne peut y répondre.
- ⚠⚠⚠ **Ce que ce document retire au dépôt** : `124`, `127` et `128` sont mesurés sur une pile où
  le marcheur va droit à 0,9994. Leurs résultats sur la déchirure, le lien et la faille **tiennent**
  — ils ne parlent pas de trajectoire — mais aucun d'eux ne peut servir d'argument sur la dérive.
- ⭐⭐ **Et il nomme la fixture qui manque** : des feuilles **non parallèles**. Ni l'enroulement
  (0,0103°/pas) ni le bruit d'intensité (rectitude 0,9994) ne font virer le marcheur ; sur le vrai
  rouleau il vire de 14,3° par pas. C'est `R4-P27`.

## 8. Les registres

Faits `R4-F64` (la matière enroulée ne demande presque aucun virage, facteur 273,9), `R4-F65` (le
virage réel alterne, donc c'est du bruit) et `R4-F66` (aucune fixture du dépôt ne reproduit la
dérive). Porte nouvelle `R4-P27` : qu'est-ce qui fait virer le marcheur de 14,3° par pas sur la
vraie matière ?

## Reproduire

```bash
uv run python src/nappe/un_cap_a_memoire.py --verifier   # 19 contrôles
uv run python src/nappe/un_cap_a_memoire.py --json docs/mesures/un_cap_a_memoire.json
uv run python src/nappe/combien_de_pas_la_matiere_porte.py --verifier
```

⚠ **Tout est analytique sauf le §4**, qui relit la course que `131` a gardée. Le cap vit dans
`marcher`, donc dans le module qui porte la marche : un second marcheur serait deux marches libres
de ne pas s'accorder.
