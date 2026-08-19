# Ce qui reste — registre consolidé

2026-08-19. Les **34 documents** du dépôt ont été lus **intégralement** — pas grepés :
onze lecteurs, chacun couvrant ses fichiers ligne à ligne. Ils ont relevé **525** énoncés
de travail ouvert, de limite connue ou de question non tranchée, répartis sur les
34 fichiers.

⚠ **525 lignes ne font pas 525 tâches.** La plupart sont des **répétitions** : la même
limite écrite dans le document qui l'a trouvée, dans celui qui s'y appuie, et dans la
passation. Ce document les replie. Chaque entrée porte ses sources en `fichier:ligne`,
pour qu'on puisse remonter à ce qui l'a dite plutôt qu'à ce résumé.

| nature | nombre |
|---|---:|
| limite connue | 296 |
| à faire | 102 |
| question ouverte | 64 |
| non mesuré | 31 |
| en attente | 16 |
| non publié | 16 |

---

## ⭐⭐⭐ 1. Le socle non prouvé : **réparer sert-il à quelque chose ?**

C'est le reste le plus profond du dépôt, et il n'est pas au bout de la chaîne — il est
**dessous**.

> *« Une surface propre donne un meilleur texte est une affirmation **sur le pipeline**,
> et elle n'est pas prouvée. »* — `03`:137
>
> *« [Réparer] peut parfaitement être **sans effet mesurable en aval**. C'est même
> l'hypothèse nulle honnête, et **personne ne l'a testée**. »* — `03`:133

Sources : `03`:130-137 · `02`:145 · `00`:117 (*« Whether removing it improves ink,
texturing, merging or tracing has not been measured »*, cité de `windcheck` lui-même).

⚠ **Tout l'appareil d'instruments de ce dépôt suppose cette proposition.** Un instrument
qui juge une trace n'a de valeur que si la qualité de trace décide de quelque chose en
aval. Et `04` a mesuré un fait qui *va contre* l'intuition : les cellules que `windcheck`
excise sont **indiscernables**, dans le CT, du papyrus qu'il garde (52 segments,
p = 0,859, delta de Cliff −0,000).

⭐ **Et ce n'est pas une faiblesse de ce dépôt : c'est un trou du domaine.** `28` montre
que l'équipe du concours ne publie **aucun taux d'erreur de traçage**, et `27` §2 que les
deux métriques qui portent l'argument du spiral fitting ne sont pas comparables à son
concurrent. **Personne n'a mesuré ce que coûte un défaut de trace.**

**Ce qu'il faudrait** : un cas où l'on tient les deux bouts — une trace fautive, sa
version réparée, et le **même** aval appliqué aux deux. C'est exactement le lot nº 2.

## ⭐⭐ 2. Appliquer la correction, et montrer le gain

Le seul ⏳ du « vrai produire », nommé dans cinq documents.

Sources : `00` §9.3 et §9.4:292-298 · `01`:179 (*« A′ — fermer la boucle sur UN défaut, de
bout en bout »*) · `18` J6 · `22` R2:74 · `27`:204.

- ✅ `20` a mesuré que **l'erreur d'une trace est structurée** et que **translater ne la
  répare pas** — donc le remède est un **gauchissement**, pas un décalage.
- ⏳ Reste : **exporter le champ en coordonnées de fenêtre** (`22` R2), l'appliquer, et
  rendre les deux versions.
- ⭐ **L'obstacle écrit est tombé** : `22` disait *« la chaîne maillage → rendu n'est pas
  ici »*. VC3D est construit depuis le 2026-08-19, et `24` a fait tourner la chaîne
  complète.

## ⭐⭐ 3. Le cap : un jugement de papyrologue

Écrit comme condition de publication depuis `06` §1bis, jamais franchi.

> *« On ne publie rien sans une passe complète — rouleau déroulé, texte extrait, **soumis
> à un expert qui dise si ça fait sens** — et sur plusieurs rouleaux. »*
> — `HANDOFF` §6:423, repris `06`:56

Sources : `06`:56, 78, 293 · `08`:141-146 · `09`:104-105 · `10`:8, 152 · `HANDOFF` §6.

⚠ **La distinction que ces documents tiennent, et qu'il ne faut pas laisser glisser** :
*le modèle retrouve les traits encrés* est **mesuré** (AUC 0,92, `08`) ; *le texte est
lisible* ne l'est **pas**. Des lettres reconnaissables ne font pas un texte suivi.

⚠ Et trois juges mécaniques ont **échoué** à remplacer l'expert (`HANDOFF` §6) : Kraken
(aucun modèle entraîné sur papyri), score structurel sur région, score structurel sur
segment entier — cette dernière cause étant **définitive** : un segment de ce type ne
porte que 4 à 5 lignes, et les glyphes fusionnent au seuil du modèle.

## ⭐ 4. Publier — et la seule échéance courte du dépôt

| quoi | où | état |
|---|---|---|
| publier le dépôt (`tracecheck/` au minimum) et mettre son adresse dans le texte | `21`:270 | ⏳ **l'adresse n'existe pas encore** |
| revérifier chaque chiffre contre son fichier de sortie **le jour de l'envoi** | `21`:16 | ⏳ règle posée, à exécuter |
| envoyer la soumission Progress Prize | `HANDOFF` T4, `15` | ⏳ le texte existe, les figures sont à joindre |

⚠ **Échéance : 31 août 2026, 23 h 59 Pacific** (`15`:3). C'est la seule date courte ;
tout le reste vise le 25 juin 2027.

⚠⚠ **Et `15` se déclare lui-même périmé sur deux points** (`15`:153, 175) : la règle de
`19` **ne réplique pas** hors de Scroll 1, et le tri de ce qui est soumissionnable est à
refaire. À faire **avant** d'envoyer, pas après.

## 5. Les limites de portée à ne jamais laisser tomber en route

Ce sont des **résultats**, pas des dettes — mais chacun a déjà été cité hors de son
domaine au moins une fois dans ce dépôt.

| limite | mesure | source |
|---|---|---|
| la règle de `19` est une propriété du **corpus publié de Scroll 1**, pas du problème | réplication échoue sur Scroll 5 : rho −0,217, p = 0,12 | `19` §11 · `21`:96 · `HANDOFF`:284-291 |
| le « 240 → 0 » de `24` **ne réplique pas** | zéro auto-intersection des deux côtés sur 12 rouleaux | `25` · `21`:204 |
| la métrique de proximité a un **domaine de définition** | > 1 tour de couverture | `07` §7 · `HANDOFF`:401 |
| sur Scroll 4, **rien n'est lisible, et la cause est en amont du modèle** | 61 % des pics au bord de la pile | `09` §12 · `12` · `HANDOFF`:237, 257 |
| l'inventaire des treize : **dix** sans segment, pas treize | `docs/etat_rouleaux_prix.txt` | `23` §1 |
| ⭐ **la trajectoire ne répond qu'à `step_size` et à la prédiction** | trois négatifs mesurés, contrôle positif | `26` |
| ⭐ et `step_size` **n'est pas un levier de qualité** | 4 pas sur 5 rendent zéro, aires comparables à 3,8 % | `26` §9 |
| ⚠ en **zone comprimée l'information n'est pas dans le CT** | 78 % de pics uniques couvrant deux feuilles | `28` §4 · `villa#191` |
| ⚠ **aucun test géométrique** ne sépare un saut d'une spire d'une courbure, dans le cas serré | écart inter-spires 18–58 vx contre 20 vx de cellule | `28` §4 |

## 6. Les mesures nommées, non faites

| # | quoi | coût | source |
|---|---|---|---|
| M1 | rejouer le balayage `step_size` sur la **mauvaise** graine de `24` | ⏳ **lancé le 2026-08-19** | `26` §9 |
| M2 | relire les 240 croisements de `24` sous un autre `--maxedge` — le filtre peut **masquer comme fabriquer** | quelques minutes | `28` §2 |
| M3 | lire le quatrième article, *EduceLab-Scrolls* (arXiv 2304.02084) | une session | `27` Références |
| M4 | chercher la vraie feuille en engendrant un volume plus profond que 65 couches | à chiffrer | `12`:259 |
| M5 | revoir les sites de fusion suspects à 2,4 µm | ⚠ **impossible** : PHerc0172 ne publie que du 7,91 µm | `06` §7:613, mesure 3.6 |
| M6 | savoir si le trend *position dans le rouleau ↔ résiduel* existe | ⚠ **non établi** : trois corpus, trois motifs | `HANDOFF` §7 |

## 7. ⚠ Ce que ce registre ne remplace pas

Il replie 525 lignes en une trentaine d'entrées, donc **il perd du détail par
construction**. Les 296 « limites connues » ne sont pas toutes ici : la plupart sont des
bornes de portée écrites au bon endroit, dans le document qui les a mesurées, et elles y
sont mieux qu'ici. Ce registre sert à **ne rien oublier de ce qui demande une action** ;
il ne sert pas de substitut à la lecture d'un document avant de s'appuyer dessus.

⚠ Et il a une date. Il a été construit le 2026-08-19 à partir d'une lecture intégrale ;
**une entrée close ailleurs et pas ici devient un piège**. La règle du dépôt s'applique à
lui comme au reste : corriger sur place, en disant ce qui était écrit avant.
