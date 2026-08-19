# Le batch « répliquer » — un résultat sur un corpus n'est pas un résultat

2026-08-19, à la suite de `18` qui est clos. Le lot précédent a produit le premier
instrument qui **décide** (`19`). Ce lot-ci attaque sa faiblesse restante, et elle est
structurelle plutôt que technique :

> **La règle repose sur un seul corpus.** 80 segments de Scroll 1, une seule population,
> un seul protocole de scan, un seul groupe de traceurs.

Or ce dépôt a déjà vu, trois fois, un effet net sur une population fondre sur la suivante :
les fibres (+0,330 → **−0,192**), la phase (+0,52 → **+0,15**), le seuil des 50 µm
(direction gardée, **seuil perdu**). Une règle qui n'a pas été essayée ailleurs n'a pas
été essayée.

⭐ **Et le matériel existe** : trois corpus publient à la fois des volumes de surface et
des cartes d'encre, jamais utilisés pour ça.

| corpus | segments | résolution du volume | cartes d'encre |
|---|---:|---|---:|
| PHerc0172 (Scroll 5) | 53 | 7,91 µm | 53 |
| PHerc0139 | 38 | 9,362 / 2,399 / 1,129 µm | 38 |
| PHerc1667 (Scroll 4) | 19 | 2,399 / 1,129 µm | 19 |

**110 segments de plus**, sur trois rouleaux et quatre résolutions.

⚠⚠ **La prédiction est posée AVANT la mesure, et elle est falsifiable dans les deux
sens** : si `avec_matiere` prédit le contraste d'encre publié sur les trois corpus avec le
même signe, la règle est une propriété du problème. Si le signe bouge ou s'annule, c'est
une propriété de Scroll 1 — et il faudra le dire au lieu de moyenner.

---

## Voie P — répliquer la règle ⭐⭐

| # | quoi | état |
|---|---|---|
| P1 | récupérer les cartes d'encre des 3 corpus | 🔄 |
| P2 | mesurer `avec_matiere` avec la **définition standard** (`zarr_depth`) sur les 3 | ⏳ ⚠ Les champs de correction de PHerc0172 existent déjà mais leur `avec_matiere` **n'est pas comparable** — il mélange repérage et blocs (`19` §10) |
| P3 | corréler, avec le **triangle du confond** fermé des deux côtés | ⏳ |
| P4 | rejouer la **décision** contre 2000 permutations, corpus par corpus | ⏳ |
| P5 | le **plateau** se retrouve-t-il, et au même endroit ? | ⏳ |

⚠ **Ce qu'il ne faut pas faire** : agréger les quatre corpus en un seul n. Des résolutions
différentes et des traceurs différents ne se moyennent pas — c'est le confond que `07` §9
a mis une journée à démêler quand il croyait mesurer une résolution et mesurait un rayon.

## Voie Q — le produit : la table de qualité de toutes les traces publiées ⭐

Le concours demande *« reveal insightful, actionable information »*. Personne n'a publié
de **classement de qualité de trace** couvrant les segments du challenge, et on peut le
produire pour quelques centaines de mégaoctets.

| # | quoi | état |
|---|---|---|
| Q1 | mode lot + sortie CSV dans `tracecheck` | ⏳ |
| Q2 | passer sur **tous** les segments à volume de surface publié (≈ 190) | ⏳ |
| Q3 | publier la table, avec la colonne qui dit ce que chaque chiffre vaut | ⏳ |

## Voie R — ce que le champ peut RÉELLEMENT produire

⚠⚠ `20` conclut que le remède utile est un **gauchissement** et non une translation. Il
faut écrire pourquoi ce lot ne l'implémente pas, sinon la conclusion ressemble à une
promesse.

Un gauchissement déplace le **maillage**, ce qui régénère un **autre volume de surface**.
Or les volumes de surface sont des artefacts **publiés** : on les lit, on ne les produit
pas. Corriger une trace demande la chaîne maillage → paramétrisation → rendu, qui n'est
pas ici. Ce qui **est** livrable, c'est le champ lui-même — de combien, où, et si c'est
cohérent — pour qui a la chaîne.

| # | quoi | état |
|---|---|---|
| R1 | écrire la limite, à l'endroit où la conclusion est tirée | ⏳ |
| R2 | exporter le champ en coordonnées de fenêtre, lisible par un tiers | ⏳ |

## Voie S — les bandes niveau 0 (héritée de `18` M2)

| # | quoi | état |
|---|---|---|
| S1 | 4 bandes de plus, dont un **témoin positif** autour du site migrant | 🔄 |
| S2 | la migration est-elle la règle ou l'exception ? | ⏳ |
