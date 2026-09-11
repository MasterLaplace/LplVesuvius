# Reproduction de `windcheck` : ce qui tient, et ce qui reste ouvert

2026-08-16. Objectif de cette étape : **rattraper l'état de l'art sur un défaut
précis**, en le reproduisant plutôt qu'en le lisant. Rien ici n'est de la
contribution originale — c'est la ligne de base sans laquelle on ne peut rien
mesurer ensuite.

---

## 1. Le défaut : une surface qui se traverse elle-même

Une trace `tifxyz` peut passer à travers elle-même : deux parties non adjacentes de
la feuille tracée s'interpénètrent, donc la représentation n'est plus une surface
simple plongée. Tout étage en aval qui consomme une trace sale reçoit ce plongement
incohérent — et, dit `windcheck` : *« Unless the census is run, the surface metadata
itself does not disclose it. »* Le fichier ne porte aucune trace du défaut.

C'est encore la même famille que le *sheet switching* : **un artefact faux dont rien
dans sa forme ne signale qu'il l'est**.

## 2. Environnement

| élément | version / état |
|---|---|
| `uv sync` | 0 erreur |
| noyau C++ `engines/selfcross` | `clang++ -O3 -std=c++17 -pthread`, 53 Kio |
| suite de tests | **364 passés, 80 sautés**, 122 s |
| données `PHerc0172` (Scroll 5) | 212 fichiers, 0,41 Go, **VERIFIED, all files match** |

⚠ **Un accroc, et pourquoi je ne l'ai pas contourné à ma façon.** Le récupérateur de
`windcheck` délègue à `aws s3 cp --no-sign-request`, et le client `aws` était absent.
Le manifeste porte pourtant un SHA-256 par fichier, donc écrire notre propre
téléchargeur aurait été facile — et c'eût été une erreur : un écart de résultat
serait alors devenu indistinguable d'un écart de récupération. Le client a été
installé dans leur environnement virtuel, leur chemin de code reste intact.

⚠ **Portée de cette décision, précisée le 2026-08-18** : elle vaut pour *reproduire
`windcheck`*, où l'on veut leur chemin de code intact. Pour **notre** récupération, le
client `aws` est inutile — le bucket est public en HTTPS et son API de listage accepte
un préfixe **par segment**, ce qui évite en prime le piège nº 16 (`aws s3 cp --include`
énumère le préfixe entier avant de filtrer). Voir `src/outils/fetch_traces.py`, qui a
récupéré les 71 traces de PHerc0139 / PHerc1667 / PHerc0814 sans lui.

⚠ **80 tests sautés** : à ne pas lire comme « 80 tests verts ». Ce sont des tests
conditionnés à des données absentes. C'est exactement le *dénominateur silencieux*
du skill `tests-first` — on n'en tire aucune garantie, et on l'écrit plutôt que de
citer « 364 passés » tout court.

## 3. Niveau 1 — reproduction ponctuelle

Le README annonce un résultat chiffré sur un segment nommé. C'est falsifiable, donc
c'est ce qu'on vise.

| | annoncé par eux | obtenu ici |
|---|---|---|
| contacts transverses, diagonale 0 | **4** | **4** |
| contacts transverses, diagonale 1 | **7** | **7** |
| verdict | *not clean* | *NOT clean* (11 contacts, 1 événement) |
| durée | 0,2 s (Apple silicon) | 0,3 s |

Segment : `20251205115859-w094_…_flatboi`, grille 563 × 520, **416 398 triangles**.

**Réparation** (`windcheck transform`) : 6 quads retirés, **99,9989 % de surface
conservée**, statut *clean*.

## 4. Niveau 2 — recensement indépendant

C'est le seul niveau qui prouve quelque chose, parce qu'il ne fait confiance à rien
de ce qui précède : le recensement est relancé sur les **octets relus du disque**, et
sous **les deux triangulations canoniques** du quadrillage — une découpe qui ne
résoudrait les contacts que sous une diagonale échouerait ici.

```
triangles      416 398  ->  416 386      (12 = les 6 quads retires)
diagonale 0          4  ->        0
diagonale 1          7  ->        0
evenements           1  ->        0
VERDICT      NOT clean  ->    clean
```

La chaîne complète — recenser, réparer, re-recenser indépendamment — **reproduit**.

## 5. Niveau 3 — recensement du corpus Scroll 5, confronté à leur publication

Un segment reproduit peut être un segment bien choisi. J'ai donc recensé **les 53
segments** de PHerc0172 (`docs/mesures/census_scroll5.tsv`, régénérable) et confronté le
résultat à leur `results/index.json`, trace par trace et non en agrégat :

| confrontation | résultat |
|---|---|
| noms de traces appariés | **53 / 53** |
| verdicts concordants | **53 / 53** |
| comptes de triangles identiques | **53 / 53** |

Aucun désaccord. La reproduction tient donc à l'échelle d'un corpus, pas seulement
d'un exemple.

⚠ **Un écart apparent, levé par la confrontation.** Leur chiffre global est « 184
transformées / 90 déjà propres », soit un tiers de traces saines. Sur Scroll 5 je
n'en trouvais qu'**une sur 53**, ce qui ressemblait à une erreur de ma part — ou à
une mesure différente de la leur. Leur publication donne exactement la même chose
pour ce rouleau : 1 saine, 52 atteintes. **La propreté varie donc énormément d'un
échantillon à l'autre**, et un taux global masque cette dispersion.

Conséquence pratique : **Scroll 5 est un mauvais endroit pour chercher un témoin
sain**, et un bon endroit pour trouver des cas atteints.

### Ce que le recensement montre en plus

| famille de traces | atteintes | événements de croisement (médiane) | maximum |
|---|---|---|---|
| `auto_grown` (9 traces) | **9 / 9** | **192** | 664 |
| autres (44 traces) | 43 / 44 | **21** | 215 |

Les traces **poussées automatiquement sont environ neuf fois plus atteintes** que
les autres, en médiane. C'est cohérent avec le fait que l'automatisation est
précisément ce qui manque de supervision — et ça désigne la population sur laquelle
une réparation aurait le plus d'effet, si elle en a un.

⚠ Corrélation, pas causalité : les `auto_grown` sont aussi les plus grandes
(jusqu'à 3,58 M de triangles contre 402 k au minimum), et une trace plus grande a
mécaniquement plus d'occasions de se croiser. Normaliser par l'aire avant d'en
conclure quoi que ce soit.

## 6. Ce que cette reproduction établit, et ce qu'elle n'établit pas

**Établi** : l'outil fait ce qu'il annonce, sur nos données, avec nos binaires, et
ses chiffres publiés sont exacts. On peut s'appuyer dessus.

**Non établi, et c'est tout l'enjeu** : que réparer serve à quelque chose. Le README
le dit lui-même — *« Whether removing it improves ink, texturing, merging or tracing
**has not been measured** »*. Une réparation qui retire 6 quads sur 416 398 triangles
et conserve 99,9989 % de la surface peut parfaitement être **sans effet mesurable en
aval**. C'est même l'hypothèse nulle honnête, et personne ne l'a testée.

> ⚠ À ne pas confondre : *une surface propre est une meilleure surface* est une
> affirmation de géométrie, déjà prouvée. *Une surface propre donne un meilleur
> texte* est une affirmation sur le pipeline, et elle n'est pas prouvée. Les deux se
> ressemblent assez pour qu'on prenne la première pour la seconde.
