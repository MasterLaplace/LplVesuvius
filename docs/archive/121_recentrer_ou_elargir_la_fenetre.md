# 121 — Recentrer la fenêtre de pas est gratuit ; l'élargir ne l'est pas

> ⭐⭐⭐⭐ **LE REMÈDE ÉVIDENT DE `117` N'EST PAS LE BON, ET LA MESURE LE DIT AVANT QU'ON LE
> PAIE.** 63 pas voyants sur 382 sont refusés parce que l'optimum de longueur tombe au bord de la
> fenêtre [0,5 ; 2,0] × 173,0 µm, et `118` a montré que les deux bouts sont de **vrais pas**. On
> pense « élargir ». Or **le modèle nul se déplace quand la fenêtre s'élargit** : **1,2 σ** pour
> [0,3 ; 3,0], **2,0 σ** pour [0,25 ; 4,0]. Réutiliser la barre publiée sur une fenêtre élargie
> remettrait exactement le biais que `nul_par_candidat` existe pour tuer.
>
> ⭐⭐⭐⭐ **RECENTRER, EN REVANCHE, NE COÛTE RIEN.** Le nul est **invariant par changement
> d'échelle** : celui d'une fenêtre centrée sur 80 µm ou sur 400 µm est celui de la fenêtre publiée
> à **2,6·10⁻¹⁶** près, c'est-à-dire au bruit du flottant. La fenêtre peut donc suivre l'espacement
> local **sans rien recalibrer**.
>
> ⭐⭐⭐ **ET LE CONTRÔLE POSITIF TIENT TOUT** : le nul n'est pas plat. Il va de **0,1582** au plus
> court candidat à **0,0925** au plus long, soit **24,4 erreurs-types** sur 800 tirages. Sans ça,
> « pas d'écart au recentrage » serait une propriété d'une constante et ne dirait rien.
>
> ⭐ **Zéro lecture distante** : le nul est un tirage de bruit, il ne touche aucun volume.

## 1. Pourquoi ce fichier

`R4-P24` demande si une fenêtre centrée localement récupère les 63 pas que la fenêtre globale
refuse. Avant de refaire une course de plusieurs heures pour le savoir, il faut savoir **ce que
chaque façon de changer la fenêtre coûte**. Deux changements sont possibles et ils n'ont rien à voir
l'un avec l'autre : déplacer le **centre**, ou changer la **largeur**.

## 2. ⭐⭐⭐ Le contrôle positif, d'abord

Le nul par candidat existe parce qu'il n'est **pas** plat : un segment court rééchantillonné sur le
même nombre de points est sur-échantillonné, donc plus lisse, donc il corrèle mieux avec un gabarit
lisse. Son fichier le mesure et en tire la raison d'être de toute la calibration.

| | |
|---|---:|
| nul du plus court candidat | **0,1582** |
| nul du plus long | **0,0925** |
| amplitude | **0,0657** |
| en erreurs-types (800 tirages) | **24,4** |

⚠⚠ **L'échelle est l'erreur-type de la moyenne, pas la dispersion**, et ma première version s'y est
trompée : elle comparait l'amplitude à σ et déclarait **plat** un nul qui varie de vingt-quatre
erreurs-types. La question posée ici est « la forme du nul est-elle mesurée ou tirée au sort », et
une moyenne sur *n* tirages a une erreur-type de σ/√n. Comparer à σ répondrait à une autre question.

## 3. ⭐⭐⭐⭐ Recentrer : exact

| centre de fenêtre | écart max au nul publié | en σ |
|---|---:|---:|
| 80 µm | 2,6·10⁻¹⁶ | 0,000 |
| 120 µm | 1,5·10⁻¹⁶ | 0,000 |
| 173 µm *(publié)* | 0 | 0,000 |
| 250 µm | 1,5·10⁻¹⁶ | 0,000 |
| 400 µm | 1,5·10⁻¹⁶ | 0,000 |

La raison est dans `profils_emboites` et elle y est déjà écrite : **chaque candidat est rendu sur le
même nombre d'échantillons**, donc le nul ne dépend que des **rapports** `longueur / plus longue`.
Une fenêtre mise à l'échelle garde ses rapports.

⚠ 80 et 400 µm ne sont pas une plage décorative : ce sont les recentrages que la re-course
demanderait réellement, puisque `118` déduit **80,7 µm** au bout court et **380,2 µm** au bout long.

⚠ Le seuil de 10⁻¹² n'est pas réglé : c'est le bruit du flottant sur des scores de l'ordre de 0,1 en
double précision.

## 4. ⭐⭐⭐⭐ Élargir : non

Le σ du nul, qui donne l'échelle de la colonne de droite, vaut **0,07627**.

| fenêtre | écart max | en σ du nul |
|---|---:|---:|
| [0,50 ; 2,0] *(publiée)* | 0 | 0,0 |
| [0,40 ; 2,5] | 0,04605 | **0,6** |
| [0,30 ; 3,0] | 0,08973 | **1,2** |
| [0,25 ; 4,0] | 0,15284 | **2,0** |

⚠⚠ **Ici l'échelle est bien σ, et pour une raison précise** : le score calibré vaut
`(score − mu) / sd`, donc une erreur `Δmu` sur le nul déplace la décision de `Δmu / sd`. Un écart
de 1,2 σ veut dire que le score calibré est faux de plus d'un écart-type — ce qui décide.

⚠ Élargir change les **rapports** : le plus court candidat devient plus court *relativement* au plus
long, donc son sur-échantillonnage change, donc son nul aussi. C'est exactement le mécanisme que
`nul_par_candidat` documente, vu dans l'autre sens.

⚠⚠ Ce que ça ne dit **pas** : qu'il est interdit d'élargir. Ça dit qu'une fenêtre élargie exige
**son** nul — 800 tirages, quelques secondes — et que réutiliser celui qui est publié serait une
mesure fausse qui ressemble à une mesure.

## 5. Ce que ça change pour le graal

- `R4-P24` a maintenant un **dessin** plutôt qu'une intention : la fenêtre suit l'espacement mesuré
  à l'endroit du pas, **à largeur constante**, et rien n'est à recalibrer. Le remède le moins cher
  est aussi celui que `118` désigne, puisque la variation n'est pas radiale et qu'il faut donc une
  mesure locale de toute façon.
- ⚠ Et le piège est nommé : la lecture spontanée de `117` — « les pas tombent au bord, élargissons »
  — aurait coûté une re-course **et** une barre fausse. La mesure a coûté quelques secondes.

## 6. Les registres

Fait `R4-F49` (recentrer est exact, élargir déplace le nul). Porte `R4-P24` **resserrée** : elle
porte désormais le dessin, pas seulement la question. Aucune porte ouverte.

## Reproduire

```bash
uv run python src/nappe/recentrer_ou_elargir_la_fenetre.py --verifier   # 12 contrôles
uv run python src/nappe/recentrer_ou_elargir_la_fenetre.py \
    --json docs/mesures/recentrer_ou_elargir_la_fenetre.json
```

⚠ **Aucune lecture distante, aucune figure** : le résultat tient en deux tableaux, et un dessin y
serait une décoration. Le nul est **importé** de `le_pas_que_la_matiere_montre.py` et jamais
réécrit — un second nul serait deux modèles d'un même bruit, et c'est précisément l'accord entre
deux nuls que ce document mesure.
