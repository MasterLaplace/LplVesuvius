---
id: V-001
titre: Un logiciel qui exécute, prix par prix, ce que le dépôt a validé
statut: LIVRÉ
priorite: 1
ouvert: 2026-09-24
---

## Ce qui a été demandé

L'auteur, le 2026-09-24 : « le logiciel officiel qui comprendrait le pipeline complet », capable de
gérer **First Letters**, le **Grand Prize** et le **titre de PHerc. Paris 4**, qui contienne ce que la
recherche a accumulé d'utile, rangé en modules partagés entre pipelines et entre prix, qui sorte
**ce que chaque prix attend**, et où l'on voie **les formules et les pipelines à l'œuvre**. Stack
laissé au choix ; préférence C, puis C++, puis Python. Architecture approuvée le même jour : noyau
C11 et services Python, adossés aux nombres publiés.

## Ce qui est vrai aujourd'hui

- La recherche vit en 246 tranches (`docs/archive/`) et environ 280 000 lignes de Python (`src/`),
  chacune une mesure. Rien ne les enchaîne par prix : `lplv` expose des verbes, pas des pipelines
  (`docs/archive/244_le_pipeline_v3.md` §4, « le livrable »).
- Le maillon du transfert de spire à spire est franchi **sur un segment** : des boucles de consensus
  sous le demi-feuillet entourent 0,9172 de l'empreinte de `20230702185753` (`R4-F408`), et la
  procédure sans main (`246`) refait chaque décision de la main.
- Aucune image Docker n'existe.

## Ce qui manque

- Une couche qui compose les étages en pipelines, un par prix, avec leurs sorties.
- Un formulaire exécutable : chaque équation une fonction, avec l'identifiant du fait qui la porte.
- La preuve que la réécriture rend les nombres publiés.

## Comment on saura que c'est fini

1. `vesuve <prix> …` existe pour `grand-prize`, `first-letters`, `paris4-title` et `progress`, et
   chaque commande écrit, sur des données réelles, les artefacts que son prix attend, plus un
   `rapport.json` qui liste chaque équation appliquée, sa valeur, et **l'étage où le pipeline s'est
   arrêté, avec sa raison**.
2. Le noyau C compile sans un avertissement sous `-Wall -Wextra -Wpedantic -Werror`, et ses tests C
   passent, sanitizers compris.
3. Chaque noyau porté rend le nombre que son producteur publie dans `docs/mesures/` (tests de
   parité), et un noyau cassé fait échouer son test.
4. L'image Docker se construit et exécute une démonstration hors ligne.
5. Cas négatifs : sans réseau, un pipeline distant dit « indécidable » et nomme la cause, jamais
   zéro ; sans modèle d'encre, `first-letters` le dit et rend le rendu sans modèle.

Ce qui n'est pas couvert : dérouler un rouleau entier (le Grand Prize n'est pas gagné par ce
logiciel, il dit jusqu'où la chaîne va), lire du grec, entraîner un modèle.

## Livré le 2026-09-24

Les cinq critères, vérifiés le jour même :

1. Les quatre verbes tournent sur des données réelles (`exemples/`, un run daté). Grand Prize : 6333
   chunks sur 97771 certifiés, et 111 bandes (24263 chunks) nommées comme restant à lire. Progress :
   la colonne 260, rangées 26 à 223, désignée. First Letters sur PHerc1447 : aucune rangée
   périodique, dit comme tel. Paris 4 : la dernière colonne de `w010-027`, courte, et la zone qui la
   suit, sur la révision qui recale à 0,98.
2. `make test` : 98 vérifications C, 0 échec, sous ASan et UBSan, zéro avertissement.
3. `pytest` : 75 tests verts deux fois de suite (`VESUVE_RESEAU=1`), chacun sondé en cassant la règle
   qu'il garde.
4. `docker build` construit et teste le noyau ; `docker run --network none` va au bout du Grand Prize
   et de Progress.
5. Hors ligne, les étages distants disent « le réseau a échoué » et nomment le fichier ; sans
   `--donnees`, First Letters et Paris 4 sont sautés en le disant.

Ce qui reste, et qui n'est pas ce logiciel : lire les 111 bandes (`vesuve grand-prize --lire`), et
faire regarder les vues de Paris 4 par un papyrologue.
