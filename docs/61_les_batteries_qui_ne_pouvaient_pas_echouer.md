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

## 3 bis. Le cas symétrique, trouvé le lendemain : un verdict que le lanceur ne LIT pas

⚠⚠ Une batterie verte peut aussi être comptée **ÉCHEC**, et la cause est au même endroit.
Le critère de `temoins.sh` est double :

```bash
if [ "$rc" -eq 0 ] && grep -q "ALL PASS" <<<"$sortie"; then
```

Deux nouvelles batteries écrites le 2026-08-28 imprimaient `TOUS LES TEMOINS PASSENT` et
rendaient 0. Elles passaient, le lanceur les aurait comptées rouges, et leurs contrôles
auraient disparu du total — **132 fichiers sur 135 emploient la formule attendue**, donc la
divergence était invisible à la relecture.

⭐ La règle est désormais dans le même garde-fou, parce que c'est la même panne vue de
l'autre côté : `verdicts_illisibles` lit les lignes du **lanceur** pour savoir ce qui est
réellement exécuté, puis vérifie que chaque module en question **imprime** une ligne
reconnaissable.

⚠⚠ Et il a fallu s'y reprendre à deux fois, pour la raison exacte que ce document décrit.
La première version cherchait la chaîne `ALL PASS` dans le **texte du fichier** — donc elle
était satisfaite par le commentaire qui explique la règle, et par la docstring qui la cite.
La sonde n'a pas tiré : casser volontairement un verdict n'a rien signalé. Une garde contre
les vérifications incapables d'échouer qui en était une.

La version juste passe par l'**arbre syntaxique** et ne regarde que les littéraux à
l'intérieur des appels à `print`, f-strings comprises. Quatre contrôles négatifs la tiennent,
dont celui qui manquait : *une simple mention hors d'un `print` ne suffit pas*.

ⓘ Note de cohérence assumée : `_est_le_verdict`, elle, accepte « témoins passent » comme
verdict. Ce n'est pas une contradiction — elle cherche **où** est le verdict dans l'arbre,
pas **si le lanceur sait le lire**. Deux questions, deux critères, chacun chez lui.

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
