# 61 — Trente-neuf batteries sur cent cinq ne pouvaient pas échouer

> ⚠⚠⚠ **Le défaut que ce dépôt traque partout vivait dans l'instrument qui sert à le
> traquer.** Trouvé le 2026-08-27 **par accident**, en sondant un tout autre correctif : la
> sonde a rendu la phrase `ALL PASS (2 failures, 28 checks)`, qui se contredit elle-même.

## 1. Une ligne

`src/encre/typographie.py`, en fin de `verifier()` :

```python
print(f"ALL PASS ({echecs} failures, {controles} checks)")
return 0
```

Le compte est tenu, il est **imprimé**, et il est **jeté**. La batterie sort verte quoi que
disent ses contrôles.

⚠⚠ Et `temoins.sh` la comptait verte, parce que son critère est exactement celui que cette
ligne satisfait par construction :

```bash
if [ "$rc" -eq 0 ] && grep -q "ALL PASS" <<<"$sortie"; then
```

⚠ Pire que « verte à tort » : sur une batterie qui passe, le lanceur n'imprime **que** la
ligne de verdict. Les `❌` d'un contrôle en échec n'auraient donc même pas été visibles.

## 2. ⭐⭐ Le balayage, et il ne désigne pas une exception

`src/depot/batteries_incapables_dechouer.py` lit l'arbre syntaxique de chaque `verifier()`
de `src/*/*.py` :

| | |
|---|---:|
| batteries Python | **105** |
| **incapables d'échouer** | **39** |

⭐ **Aucune ne cachait un échec réel** : les trente-neuf, une fois corrigées, passent
toutes. Le défaut n'avait pas encore coûté un faux vert — mais une vérification qui ne peut
pas échouer occupe la place d'une vraie, et rend un compte de contrôles qui rassure.

## 3. ⚠⚠ La première règle était trop faible, et elle a raté son propre cas

Premier jet : *« un `verifier()` dont tous les `return` rendent le littéral 0 ne peut pas
échouer »*. La sonde qui remettait le défaut d'origine dans `typographie.py` a rendu **0
batterie signalée**.

La raison est instructive : ce `verifier()` porte un `return 1` **ailleurs**, sur un refus
d'argument. Une règle qui regarde toutes les sorties le déclare donc sain, alors que la
sortie **qui compte** — celle qui suit le verdict — jette le compte.

⭐ La règle qui décide vraiment : **la sortie qui suit le verdict imprimé doit dépendre du
compteur d'échecs.** Un `return 0` littéral juste après un `print("ALL PASS …")` est une
batterie verte par construction. C'est une propriété syntaxique, donc elle se lit sans
exécuter.

⚠ Et une garde contre le sur-signalement, apprise le même jour sur une autre alerte : les
`return` des **fonctions imbriquées** ne comptent pas. Un `verifier()` définit presque
toujours un helper `v(...)` qui rend `None` ; le compter ferait signaler tout le dépôt, et
une alerte qui désigne tout ne désigne rien.

## 4. Portée, dite plutôt que sous-entendue

⚠ **Les batteries en shell ne sont pas jugées.** Elles se testent autrement, et prétendre le
contraire ferait passer ce contrôle pour plus large qu'il n'est. Le lanceur en compte
quelques-unes ; elles restent à instruire.

⚠ Ce contrôle dit qu'une batterie **peut** échouer, jamais qu'elle **teste** quelque chose
d'utile. Une batterie d'un seul contrôle trivial passe le test de ce fichier. C'est la
différence entre « la sortie est branchée sur le compte » et « le compte veut dire quelque
chose », et seule la première est décidable ici.

## Reproduire

```bash
uv run python src/depot/batteries_incapables_dechouer.py            # le balayage
uv run python src/depot/batteries_incapables_dechouer.py --verifier # ses propres contrôles
```
