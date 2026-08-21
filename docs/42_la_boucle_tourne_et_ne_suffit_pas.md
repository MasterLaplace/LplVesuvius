# La boucle de correction tourne — et 318 points ne suffisent pas

2026-08-21. Reproductible : `./tools/lancer.sh --fond tools/boucle_de_correction.sh`.
Verdicts : `docs/boucle_temoin.json`, `docs/boucle_corrige_gen5.json`.

---

## 1. Ce qui est fait pour la première fois

Les maillons de [`39`](39_le_seam_de_correction.md) existaient séparément. Ils sont
désormais **bout à bout** :

```
tracer → marcher la prédiction → écrire les points → --resume --rewind-gen --correct → juger
```

Et le seam **fonctionne mécaniquement** : la reprise corrigée lit le fichier, en tient
compte, et produit une surface différente. Ce n'est pas rien — c'était l'inconnue de `39`.

## 2. Le résultat, apparié

Témoin et corrigé partagent graine (`5842 5839 7386`), volume, paramètres et générations.
**Seuls les points de passage diffèrent.**

| | aire | auto-intersections | écart 41 c | écart 161 c | **α** |
|---|---:|---:|---:|---:|---:|
| témoin | 19,82 cm² | **0** | 187,2 µm | 711,5 µm | **+0,98** |
| corrigé, 318 points | 20,65 cm² | **11 753** | 168,5 µm | 692,8 µm | **+1,03** |
| *segment officiel* | — | — | *17,3 µm* | *17,3 µm* | ***+0,00*** |

![les trois surfaces, la même mesure](images/42_boucle_convergence.png)

⚠⚠ **La correction a changé la trace et n'a pas changé sa nature.** L'aire bouge, les
auto-intersections passent de 0 à 11 753, les écarts baissent d'une dizaine de pour cent —
et **α reste à 1**. La surface suit toujours la fenêtre de rendu : elle est encore posée en
travers de l'empilement.

## 3. Pourquoi — et c'est un rapport de forces, pas un bug

**318 points de passage contre 56 630 points de grille.** Mesuré des deux côtés
(`correction.json` d'une part, la dernière ligne `-> done N` du journal de trace de l'autre) :
la correction porte sur **0,56 %** de la surface, avec un `correction_weight` qui vaut
**1,0 par défaut** — le même ordre que `DIST`, qui s'applique partout.

> Une correction de 318 points est un **coup de pouce local**, pas une réorientation.

⭐ Et ça désigne le levier suivant sans avoir à deviner : `correction_weight` est une clé
JSON que `applyJsonWeights` accepte (`GrowPatch.cpp:1311`), jamais réglée ici. Le balayage
est ajouté à `tools/boucle_de_correction.sh` (`POIDS`, défaut `1 100`).

## 4. ⚠ Ce que ce résultat retire à une hypothèse séduisante

[`38`](38_ce_qui_bouge_avec_la_fenetre.md) posait qu'une coupe radiale **ne peut pas** se
croiser elle-même, et donc que nos traces propres étaient peut-être les mauvaises. Ici, une
trace passe de **0 à 11 753 auto-intersections** et son α **ne s'améliore pas** (+0,98 →
+1,03).

⚠ Beaucoup de croisements n'est donc **ni** un symptôme de bon suivi **ni** son contraire :
c'est une propriété indépendante. L'hypothèse qui inverse perd son dernier appui indirect —
il restait `essai_ng2` (α = +0,65 avec 112 139 croisements), et un seul point ne fait pas
une tendance.

## 5. Ce que ça ne dit pas

- **Que les points de passage soient faux.** [`41`](41_marcher_le_long_dune_nappe.md) mesure
  que la marche suit une nappe sur ≈ 2,4 mm **sans traverser un seul vide**. Ce sont des
  points sur une feuille ; ils sont simplement trop peu nombreux et trop peu pondérés.
- **Que `--rewind-gen 5` soit le bon rembobinage.** Le balayage en essaie deux (5 et 40) ;
  `39` notait déjà que notre juge porte sur une trace entière et pas sur une génération.
- **Que la cause soit trouvée.** Trois leviers de données restent éteints chez nous
  (`41` §6ter), et un quatrième existe dont je ne sais pas dire s'il tire.

---

## Reproduire

```bash
./tools/lancer.sh --fond tools/boucle_de_correction.sh      # la boucle entière, appariée

# la figure, depuis les verdicts eux-mêmes — jamais des nombres recopiés
cd experiments && uv run python ../analysis/src/test_convergence.py \
  --serie "31:17.28,81:17.30" --nom "segment officiel (bonne surface)" \
  --depuis "../docs/boucle_temoin.json=témoin, sans correction" \
  --depuis "../docs/boucle_corrige_gen5.json=corrigé, 318 points de passage" \
  --json ../docs/boucle_convergence.json
cd ../inference && uv run python ../analysis/src/figure_convergence.py \
  --entree ../docs/boucle_convergence.json --sortie ../docs/images/42_boucle_convergence.png
```
