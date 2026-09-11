# 120 — La garde contre le vide était écrite, testée, et personne ne l'appelait

> ⭐⭐⭐⭐ **`R4-P23` EST RÉPARÉE, ET LA CAUSE N'ÉTAIT PAS CELLE QU'ON CROYAIT.** `115` a mesuré que
> le marcheur déclare `oriente` sur **178 pas aveugles sur 178**. La lecture évidente est « il
> manque une garde ». **Faux : elle existait.** `planarite` rend exactement **0,0** sur un tenseur
> nul, sa docstring écrit que *« le cas dégénéré doit être DÉTECTÉ, pas répondu »*, et sa batterie
> asserte même que *« sa direction reste finie, donc **seule la planarité peut l'écarter** »*.
> C'était un contrat avec un consommateur qui n'a jamais existé.
>
> ⭐⭐⭐ **LE MARCHEUR CALCULAIT LA PLANARITÉ, LA PUBLIAIT, ET NE LA LISAIT PAS.**
> `direction_de_la_matiere` la rend à chaque pas ; `marcher` la range dans le registre et calcule
> `oriente` **depuis le seul désaccord des deux moitiés**. Or deux moitiés de rien ne peuvent pas
> être en désaccord : sur un cube constant l'angle vaut **exactement 0,00°**, donc il passe
> n'importe quelle barre.
>
> ⭐⭐ **LA RÉPARATION EST UNE LIGNE, ET ELLE NE TOUCHE À AUCUN SEUIL.** `oriente` exige désormais
> une planarité **strictement positive** — un test de dégénérescence, jamais une barre. Le pas
> porte en plus un champ `rien_lu` écrit à la source.
>
> ⚠ **Aucun chiffre publié ne bouge** : les cinq tranches qui relisent la course de `113`
> reproduisent leur JSON **octet pour octet**.

## 1. Ce que `115` a trouvé, et ce qu'on en a conclu trop vite

`115` a mesuré le défaut par un compte : `oriente = désaccord < barre_moities`, et **178 pas
aveugles sur 178** le portent. Le document l'a rangé avec `54`, `60` et `41` §6bis — *un vide lu
comme un accord parfait* — et a ouvert `R4-P23` pour réparer le drapeau.

Ce qui n'avait pas été regardé, c'est **pourquoi** la garde manquait. Elle ne manquait pas.

## 2. ⭐⭐⭐⭐ La garde, et son contrat sans consommateur

`la_direction_que_la_matiere_montre.planarite` :

> *« C'EST LE JUGE DE "LA MATIÈRE A-T-ELLE UNE ORIENTATION ICI", et il est nécessaire : sans lui,
> un cube homogène rendrait une direction arbitraire, parfaitement unitaire, que rien ne
> distinguerait d'une mesure. »*
>
> *« ⚠ Un tenseur exactement nul — cube constant — rend **0** plutôt qu'une division par zéro : le
> cas dégénéré doit être DÉTECTÉ, pas répondu. »*

Et sa batterie, sous un titre qui ne laisse aucun doute — `=== LE CAS DEGENERE, DETECTE PLUTOT QUE
REPONDU ===` :

```python
v("un cube CONSTANT rend une planarité nulle, pas une direction", planarite(val) == 0.0)
v("... et sa direction reste finie, donc seule la planarité peut l'écarter", ...)
```

⚠⚠ **Le second contrôle est une vérification qui passe pendant que ce qu'elle protège n'est pas
protégé.** Il asserte que *seule la planarité peut écarter le cas dégénéré* — c'est-à-dire qu'il
décrit un devoir d'appelant. Aucun appelant ne le remplissait.

## 3. Mesuré, pas supposé

| cube de 41³ | désaccord | planarité |
|---|---:|---:|
| zéros | **0,0** | **0,0** |
| constante 137 | **0,0** | **0,0** |
| bruit gaussien (graine 0) | 27,63° | 0,337 |

⚠ Les deux valeurs du bruit sont **épinglées dans la batterie** avec leur graine et leur forme :
un chiffre publié dont le calcul n'est pas dans l'arbre est une anecdote, et un tableau de
contraste en est un aussi.

La direction rendue sur un cube constant est `[0, 0, 1]` — parfaitement unitaire, arbitraire, et
indistinguable d'une mesure, exactement comme la docstring l'annonce.

## 4. ⭐⭐ La réparation, et pourquoi elle n'est pas un seuil

```python
rien_lu = not (np.isfinite(pl) and pl > 0.0)
oriente = bool(np.isfinite(desaccord) and desaccord < barre_moities and not rien_lu)
```

⚠⚠ **Fermer sur une BARRE de planarité aurait été le péché inverse**, et `accord_des_moities` le
mesure : à sigma 15 pour 40 d'amplitude, un cube de 175 µm rend la direction à **2,50°** pendant
que sa planarité vaut **0,344**, c'est-à-dire au niveau du bruit pur. Une barre de planarité
supprimerait donc ce que la garde doit laisser passer — le péché que `97` a payé avec son critère
de bord.

Seul l'**exactement nul** est refusé, et il ne peut venir que d'un tenseur nul.

⚠ `pl > 0.0` prend son sentinelle **dans** l'intervalle légitime [0, 1], et c'est dit plutôt que
caché : une vraie matière dont la plus grande valeur propre serait exactement nulle rendrait aussi
0,0. Ça demande un cube sans le moindre gradient, ce qui est la définition du cas dégénéré.

## 5. ⭐ Le champ écrit à la source

Le pas porte désormais `rien_lu`. Ce n'est pas un doublon de la signature que `115` déduit :

- la signature **déduite** (désaccord et planarité exactement nuls) lit les courses **déjà
  gardées**, qui ne portent pas le champ ;
- la signature **écrite** fait autorité quand elle est là — et il le faut, parce que la réparation
  change ce que le marcheur écrit et que rien ne garantit qu'une course future rende encore un
  désaccord *exactement* nul.

⚠⚠ Sans les deux, `est_aveugle` compterait **zéro pas aveugle** sur une course neuve, ce qui
ressemble exactement à un volume qui répond partout.

## 6. ⚠ Ce que ça change, et ce que ça ne change pas

- **Aucun chiffre publié ne bouge.** Les courses gardées sont des données : `115`, `116`, `117`,
  `118` et `119` reproduisent leur JSON **octet pour octet** après la réparation. C'est le
  contrôle, et il a été fait avant de commiter.
- **Une course future écrira autre chose**, et c'est le but : `oriente` cessera de valoir vrai là
  où le marcheur ne lit rien.
- ⚠ La réparation **ne change pas la règle d'arrêt**. `116` a mesuré que s'arrêter au premier pas
  aveugle ne coûte rien, mais en faire le défaut changerait ce que toute marche mesure — c'est la
  question de `R4-P20`, pas une retouche à glisser ici.

## 7. Les registres

Fait `R5-F21` (une garde écrite, documentée et assertée, sans appelant). Porte `R4-P23`
**fermée** ; la note de `R4-F37` dit depuis quand le drapeau est réparé. Et `R4-P21` est fermée
elle aussi, par `115` et `118` : sa prémisse — un taux qui chute au grand rayon — est tombée.

## Reproduire

```bash
uv run python src/nappe/combien_de_pas_la_matiere_porte.py --verifier   # 32 controles
uv run python src/nappe/ce_qui_porte_le_taux.py --verifier
```

⚠ La batterie du marcheur touche le volume réel sur sa fin ; les sondes de la réparation, elles,
sont **hors ligne** : un lecteur constant, un lecteur de bruit, et les deux contrôles symétriques —
le vide doit être refusé, **et le bruit ne doit pas l'être**.
