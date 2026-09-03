# 72 — Le second papier : ce qui est en main, et ce qui manque

> ⚠ [`70`](70_ce_que_larticle_condense.md) §3.1 écarte cinq documents de l'article en cours
> pour une raison de cohérence — *« ils n'attendent pas, ils attendent leur propre papier »*.
> Ce document dit lequel, avec ce qui est déjà mesuré et ce qui ne l'est pas.
>
> **Il ne fixe pas de calendrier et n'engage rien.** Il existe pour qu'un lot ne soit pas
> redécouvert dans trois semaines, et pour dire *ce qu'il faudrait mesurer d'abord*.

---

## 1. La thèse, en une phrase

**Les treize rouleaux du Grand Prize n'ont pas un mauvais scan : ils ont un scan de
REPÉRAGE**, et l'expérience qui dirait ce que ça coûte est **publiée mais non faite**.

C'est un sujet différent de celui du premier papier — celui-ci juge une **géométrie**, celui-là
jugerait un **régime d'imagerie** et ce qu'il laisse de l'encre. Les mélanger rendrait les deux
incohérents.

---

## 2. Ce qui est déjà mesuré, et se tient seul

| résultat | instrument | ce qui le rend défendable |
|---|---|---|
| ⭐⭐ **les trois paramètres n'en font qu'un** — $F = \sqrt{\lambda D}/p$ | `nombre_de_fresnel.py`, 13 contrôles | $F$ **ordonne les verdicts que les auteurs écrivent sous leurs propres panneaux**, aux deux bouts. Calculé sur les **59 scans publiés**, sans télécharger un octet |
| ⭐⭐ **103 cases vides du régime du prix** | `la_case_vide.py`, 8 contrôles | couches rendues publiées, **sans carte d'encre**, **avec un témoin positif sur le même segment** — dont **38 sur `PHerc0139`**, dont le titre est transcrit |
| ⭐ **la garantie anti-hallucination ne se transporte pas** | idem | 256 px valent 614 µm à 2,4 µm et **2 397 µm** à 9,362 — il faudrait **66 px** |
| **la résolution éliminée deux fois** | `58`, `63` | par émulation puis **contre de vraies étiquettes** : ramener un fragment au pas d'entraînement **dégrade** l'AUC |
| **la campagne de scan effondrée** | `59` | p de 0,0081 à **0,50** en séparant « jamais tracé » de « pas d'encre » |

⚠ Deux d'entre eux — la dispersion et Holm (`64`, `65`) — sont **partis dans le premier
papier** (§6.2) parce qu'ils y tenaient la promesse de sa §2.4. Ils ne sont plus disponibles
ici, et c'est le bon partage : ce sont des résultats de **méthode**, pas d'imagerie.

---

## 3. ⚠⚠ Ce qui manque, et c'est une seule mesure

Le papier **diagnostique sans chiffrer**. Il dit que les treize sont à $F = 0{,}39$ contre
0,73, et que la distance de propagation les met du mauvais côté d'un second critère. Il ne dit
pas **combien de caractères survivent**.

⭐ **La mesure qui le dirait est à portée**, et c'est la case vide : rendre une carte d'encre
depuis la pile de couches **déjà publiée** à 9,362 µm d'un fragment de supervision, et la
scorer contre les **mêmes étiquettes infrarouges** que le témoin positif à 2,215 µm. Même
objet, même surface, même aplatissement, réponse connue.

**Ni faisceau, ni annotation manuelle, ni rescan.** Les couches sont rendues.

⚠ Et le piège à ne pas hériter en la faisant : la tuile de 256 px, qui vaut **quatre fois** la
fenêtre des auteurs à ce pas. La rendre avec la tuile héritée produirait un résultat **sans la
propriété qui rendait l'original crédible**.

---

## 4. Ce qu'il faudrait vérifier avant d'écrire

1. ⚠ **L'antériorité, comme pour les trois autres.** Le motif du dépôt est constant : le
   domaine publie les mécanismes, ce qui résiste est la mesure. $F$ est de la physique
   standard en imagerie de phase par propagation — **il faut chercher si quelqu'un l'a déjà
   appliqué à ce corpus**, et l'audit doit porter sur le *concept*, pas sur le nom.
2. **Le contrôle P1 bis** de [`71`](71_les_trois_resultats_de_tete_audites.md), qui traîne :
   ×15,9 exigé contre ×3,8 observé.
3. ⚠ **Le fold du modèle du Grand Prize** (`66` §3) : indécidable depuis les métadonnées, mais
   **décidable par la mesure** — scorer sur les deux segments, celui où il fait le moins bien
   est celui qu'il n'a pas vu. Tant que ce n'est pas fait, tout résultat d'encre reposant sur
   ce modèle porte une réserve.

---

## 5. ⚠ Ce que ce document ne dit pas

Il ne dit pas que le papier **doit** être écrit, ni quand. Il dit qu'il y a de la matière
mesurée, qu'elle est cohérente, et qu'**une** mesure la rendrait nettement plus forte. La
décision appartient à l'auteur.

⭐ Et il nomme le risque à ne pas prendre : écrire le papier **sans** remplir la case vide
donnerait un diagnostic sans coût mesuré — exactement le genre d'affirmation que le premier
papier reproche à la littérature.
