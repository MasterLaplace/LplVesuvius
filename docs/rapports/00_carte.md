# La carte — ce que ce dépôt sait, rangé pour être relu

> Ouvert le **2026-09-11**, après vingt-sept jours et **115 documents** (39 697 lignes). Ce dossier
> remplace la lecture de ces documents : ils sont **archivés, gelés, et cités** — jamais réécrits.
> La raison est mesurée dans `archive/75` : un registre des tâches y est devenu un cahier de labo de
> 7 473 lignes où une affirmation est retirée trois cents lignes après avoir été publiée. Le savoir y
> est ; il n'y est pas *trouvable*.

## 0. Comment lire ce dossier

| fichier | ce qu'il est | quand le lire |
|---|---|---|
| **`00_carte.md`** | ce document — le graal, les prix, les campagnes, les conventions | d'abord |
| **`PRIX.md`** | les quatre prix, leurs règles au jour près, et où le dépôt se tient sur chacun | pour arbitrer |
| **`R1`…`R6`** | un rapport par **campagne** : ce qui est établi, réfuté, rétracté, ouvert — avec les nombres et leur source | pour reprendre un sujet |
| **`REGISTRE_faits.tsv`** | un fait par ligne, avec son **statut courant** et son producteur | pour savoir ce qui tient aujourd'hui |
| **`REGISTRE_contradictions.md`** | A a dit, B a dit, C a tranché — et le statut courant | pour ne pas re-payer une dispute |
| **`REGISTRE_anteriorite.tsv`** | ce que le domaine a publié, lauréats compris, en face de chaque résultat | pour citer, et pour ne pas redécouvrir |
| **`FILS_ROUGES.md`** | les mécanismes qui traversent toutes les campagnes — les lois que le dépôt a payées | pour ne pas les repayer |
| **`PORTES_OUVERTES.md`** | ce qui reste, classé **par prix** | pour choisir la suite |

**Conventions, et elles ne changent pas :**

- Une source se cite **`archive/NN §k`** ou **`archive/NN:ligne`**. Le document archivé est la
  preuve ; le rapport est la lecture. Séparer les deux est ce qui rend le rapport auditable — c'est la
  règle du rapport modèle de `LplKnowledge` (*ce qui est dit* ≠ *ce qui est vérifié*).
- Un fait porte un **statut** parmi cinq : `établi` · `borné` (une borne, pas une valeur) ·
  `réfuté` · `rétracté` (publié puis retiré par le dépôt lui-même) · `ouvert`. Et un **producteur** :
  le script et le JSON qui le recalculent. Un fait sans producteur n'entre pas au registre.
- Les étoiles suivent la règle de `archive/HANDOFF` : elles marquent un résultat **mesuré**, jamais ce
  qu'une mesure va tester ; quatre étoiles nomment la tranche qu'elles déplacent.
- Rien dans `archive/` n'est modifié. Une erreur trouvée dans un document archivé se **note** au
  registre des contradictions, elle ne se corrige pas sur place.

## 1. Le graal, et les trois autres prix

Le prix demande de **dérouler 100 % du recto d'un rouleau automatiquement**, avec au plus 8 heures
d'humain, là où l'état de l'art en dépense **775** (31 spires × ~25 h de correction manuelle du
transfert de spire à spire, `archive/68` §1). Le livrable est une image Docker qu'ils lancent. Ce
n'est pas lire du grec, pas entraîner un modèle d'encre : l'encre est la **règle graduée**, pas
l'ouvrage. L'aplatissement est fait par d'autres (`vc_flatten` / SLIM). Ce qui manque est le
**transfert de spire à spire**, et la question tient en une ligne :

> **Qu'est-ce qui remplace l'humain qui corrige le transfert de spire à spire ?**

Mais il y a **quatre** prix, et l'argent n'est pas au même endroit que le graal :

| prix | montant | ce qu'il paie | échéance |
|---|---:|---|---|
| Grand Prize 2027 | 1 000 000 $ | le graal | 25 juin 2027 |
| First Letters | 500 000 $ | 10 lettres dans 4 cm² sur un des **23** rouleaux | 25 juin 2027 |
| Titre de Paris 4 | 50 000 $ | le titre de Scroll 1, toute résolution admise | 25 juin 2027 |
| Progress Prizes | ≥ 20 000 $ **par mois** | outils, audits, **résultats négatifs** | 30 septembre 2026, puis chaque mois |

Le détail et les règles verbatim sont dans **`PRIX.md`**. Ce qui compte pour lire la suite : les
campagnes qui ont *divergé* du graal n'ont pas divergé de l'argent — elles sont la matière des trois
autres prix.

## 2. Les six campagnes

Cent quinze documents, 27 jours, 835 commits. Six fils, entrelacés dans le temps mais séparables par
leur question :

| | campagne | la question | documents | rapport |
|---|---|---|---|---|
| **R1** | **L'encre — la règle graduée** | que reste-t-il de l'encre au régime du prix, et peut-on juger un rendu sans se mentir ? | `08`–`10`, `12`, `14`, `19`–`24`, `36`, `45`–`46`, `58`–`60`, `63`–`65`, `72`, `75` §C | `R1_encre.md` |
| **R2** | **L'excision et la réparation** | réparer une trace sert-il à quelque chose de mesurable ? | `03`–`07`, `33`–`34`, `75` D1 | `R2_excision.md` |
| **R3** | **La graine et le traceur** | le traceur est-il un tirage, et qu'est-ce qui gouverne où il va ? | `25`–`26`, `30`, `35`, `37`–`55` | `R3_graine_et_traceur.md` |
| **R4** | **Le déroulement** — *le graal* | qu'est-ce qui remplace l'humain du transfert ? | `76`–`79`, `81`–`86`, `90`–`114`, `75` §A et ses ~40 tranches | `R4_deroulement.md` |
| **R5** | **La méthode et l'hygiène** | comment ce dépôt se trompe, et ce qui l'attrape | `56`–`57`, `61`, `80`, `87`–`89` | `R5_methode.md` |
| **R6** | **La littérature et l'antériorité** | qu'est-ce qui était déjà publié, et par qui | `00`, `27`, `32`, `66`–`71`, les pages *winners* et *open problems* | `R6_litterature.md` |

Ce qui n'entre dans aucun rapport parce que c'est du **procédé** (plans, batchs, registres, brouillons
de soumission) : `01`, `02`, `13`, `15`, `18`, `21`, `28`, `29`, `31`, `39`, `40`, `57`, `75` §0/§E,
`HANDOFF`. Ils sont archivés et cités là où un rapport a besoin de dater une décision.

## 3. Ce que chaque campagne fait avancer — la matrice prix × campagne

| | Grand Prize | First Letters | Titre Paris 4 | Progress |
|---|:--:|:--:|:--:|:--:|
| **R1 encre** | la règle qui *valide* un déroulage | ⭐ **le cœur** : régime 9 µm, non-hallucination, 103 cases vides | le détecteur, à 2,4 µm | résultats négatifs, harnais |
| **R2 excision** | — | — | — | ⭐ audit de `windcheck`, borne de la réparation |
| **R3 graine** | où commencer, quel objet | quel rouleau | — | ⭐ le traceur est un tirage, artefacts de budget |
| **R4 déroulement** | ⭐ **le cœur** | — | la géométrie de Paris 4 est déjà mesurée | dérive du rollout, référent d'identité |
| **R5 méthode** | la reproductibilité exigée | — | — | ⭐ outils de QA, audits de données |
| **R6 littérature** | ne pas redécouvrir | qui a déjà tenté (Miller & Müller sur `0826`) | — | qui a été payé pour quoi |

Lecture : une case ⭐ est un endroit où la campagne a **déjà** de la matière soumissible ; une case
vide n'est pas une case perdue, c'est une case non travaillée.

## 4. Ce que ce dossier n'est pas

- **Pas une réécriture des documents.** Les 115 sont dans `archive/`, intacts, avec leurs images et
  leurs mesures là où elles étaient (`docs/images/`, `docs/mesures/` ne bougent pas).
- **Pas un troisième registre à côté des deux qui existaient.** `archive/29` (525 énoncés, 19 août),
  `archive/55` + `archive/registres/murs_et_causes.tsv` (57 lignes), `archive/75` §0 — trois
  embryons de base de faits, tous nés comme sous-produits, aucun tenu comme source de vérité.
  `REGISTRE_faits.tsv` reprend leur forme (`mur · cause · verdict · mesure · doc · ancre`) et **est**
  la source de vérité. Les trois sont cités, pas fusionnés.
- **Pas l'article.** `docs/article/` reste ce qu'il est ; les rapports le citent quand il condense.

## 5. Journal d'extension

| date | ce qui a été fait |
|---|---|
| 2026-09-11 | ouverture : carte, `PRIX.md` depuis les pages téléchargées le jour même |
