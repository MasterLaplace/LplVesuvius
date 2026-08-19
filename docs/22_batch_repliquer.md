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
| P1 | récupérer les cartes d'encre des 3 corpus | ✅ **110 cartes** (PHerc0172 53, PHerc0139 38, PHerc1667 19) |
| P2 | mesurer `avec_matiere` avec la **définition standard** (`zarr_depth`) sur les 3 | ✅ **110 segments** à 392 points. ⚠ Le `avec_matiere` de `champ_correction` n'est **pas** comparable — il mélange repérage et blocs, et c'est ce qui a produit le faux contrôle de `19` §9 |
| P3 | corréler, avec le **triangle du confond** fermé des deux côtés | ✅ fait sur les trois |
| P4 | rejouer la **décision** contre 2000 permutations, corpus par corpus | ✅ **la règle ne réplique pas** — `19` §11 et §12 |
| P5 | le **plateau** se retrouve-t-il ? | ❌ **non** hors de Scroll 1. ⚠ Mon explication par un effet de plancher était **fausse** : PHerc0139, à la même résolution et avec une étendue **plus grande**, rend le signe opposé |

⚠ **Ce qu'il ne faut pas faire** : agréger les quatre corpus en un seul n. Des résolutions
différentes et des traceurs différents ne se moyennent pas — c'est le confond que `07` §9
a mis une journée à démêler quand il croyait mesurer une résolution et mesurait un rayon.

## Voie Q — le produit : la table de qualité de toutes les traces publiées ⭐

Le concours demande *« reveal insightful, actionable information »*. Personne n'a publié
de **classement de qualité de trace** couvrant les segments du challenge, et on peut le
produire pour quelques centaines de mégaoctets.

| # | quoi | état |
|---|---|---|
| Q1 | mode lot + sortie CSV dans `tracecheck` | ✅ `--all --csv`, une ligne au fil de l'eau. ⚠⚠ Et un défaut trouvé en l'essayant : à faible échantillonnage, `coherence` 0,435 contre un témoin à **0,423** — le contrôle avait cessé de discriminer et rien ne le disait. `pairs` et `coherence_reliable` voyagent désormais avec |
| Q2 | passer sur tous les segments à volume de surface publié | 🔄 fait sur **PHerc1447**, le seul rouleau du **prix** qui en publie (`23`) |
| Q3 | publier la table | ⏳ à faire dans la soumission |

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
| R1 | écrire la limite, à l'endroit où la conclusion est tirée | ✅ `20` §4. ⚠⚠ **Et cette limite est tombée le jour même** : VC3D est construit, la chaîne maillage → rendu **est** ici, et `24` la pilote de bout en bout |
| R2 | exporter le champ en coordonnées de fenêtre | ⏳ |

## Voie S — les bandes niveau 0 (héritée de `18` M2)

| # | quoi | état |
|---|---|---|
| S1 | 4 bandes de plus, dont un **témoin positif** | ✅ **6 bandes** analysées |
| S2 | la migration est-elle la règle ou l'exception ? | ✅ **l'exception** — 2 sur 6, Fisher p = 0,079, et le témoin positif ressort (`11` §13) |


---

## ✅ Clôture du batch — 2026-08-19, et il a viré ailleurs qu'où il visait

⚠ **Trois voies sur quatre sont fermées** *(corrigé le 2026-08-19 : cette ligne disait
« les quatre »)*. Restent ouverts, dans les tableaux ci-dessus : **Q2** 🔄 — fait sur
**un seul** rouleau, PHerc1447 —, **Q3** ⏳ *publier la table*, et **R2** ⏳ *exporter le
champ en coordonnées de fenêtre*. Ce dernier est le lot nº 2 de
[`29`](29_ce_qui_reste.md). Le lot s'est terminé sur un terrain qu'il n'avait
pas prévu.

| voie | verdict |
|---|---|
| P — répliquer la règle | ❌ **elle ne réplique pas**, et deux de mes explications sont tombées en route |
| Q — la table de qualité | ✅ l'outil ; ⭐ appliqué au **premier rouleau du prix** (`23`) |
| R — ce que le champ peut produire | ✅ écrit — ⚠ **et périmé le jour même** : VC3D existe ici |
| S — bandes niveau 0 | ✅ la migration est l'**exception** |

### ⚠⚠ Ce que ce batch a appris et que je n'avais pas prévu

**Trois de mes propres conclusions ont été corrigées par la mesure, jamais par la
relecture** — et dans les trois cas la version fausse était **plausible et prudente** :

1. le contrôle de robustesse de `19` §9 comparait **deux grandeurs différentes** ;
2. l'explication par effet de plancher couvrait **un corpus sur trois** ;
3. « la chaîne de production n'est pas ici » était **faux** — 32 dépôts clonés, dont le
   monorepo officiel.

⭐ **La suite est dans [`24`](24_premiere_trace_rouleau_du_prix.md)** : `PHerc0358` tracé,
aplati, rendu — et **condamné par nos propres instruments avant qu'on regarde l'image**.
