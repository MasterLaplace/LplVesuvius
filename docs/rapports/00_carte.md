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
| **`R1`…`R6`** | un rapport par **campagne** : la fiche, les mouvements et leurs figures, la chronologie, ce que ça dit des prix | pour reprendre un sujet |
| **`REGISTRE_faits.tsv`** | **la source** : un fait par ligne, avec sa valeur, son statut, sa source et son producteur | pour savoir ce qui tient aujourd'hui |
| **`REGISTRE_contradictions.tsv`** | A a dit, B a dit, C a tranché — et le statut | pour ne pas re-payer une dispute |
| **`REGISTRE_lois.tsv`** | les mécanismes que le dépôt a payés | pour ne pas les repayer |
| **`REGISTRE_portes.tsv`** | ce qui reste, avec le prix que ça fait avancer | pour choisir la suite |
| **`REGISTRE_anteriorite.tsv`** | ce que le domaine a publié, lauréats compris, en face de chaque résultat | pour citer, et pour ne pas redécouvrir |
| `REGISTRE_faits.md`, `REGISTRE_contradictions.md`, `ANTERIORITE.md`, `FILS_ROUGES.md`, `PORTES_OUVERTES.md` | une **vue rendue** par registre, lisible d'affilée | pour lire, pas pour éditer |

⚠⚠ **Ce sont les `.tsv` qui POSSÈDENT la donnée, pas les rapports.** Un fait, une contradiction,
une loi, une porte et une antériorité sont des **lignes de table** : tant qu'elles vivaient dans la
prose d'un rapport, elles n'étaient ni cherchables, ni triables, ni modifiables autrement qu'en
éditant un document de six cents lignes — et chaque rapport payait la moitié de sa longueur pour
les porter. Les six rapports ont **fondu de 2 763 à 1 884 lignes** (−32 %) le jour où la donnée est
partie, et ils se lisent maintenant en entier.

- Un rapport **cite** une ligne par son identifiant : `R1-F07` (fait), `R2-C13` (contradiction),
  `R5-L09` (loi), `R4-P02` (porte), `A17` (antériorité).
- Chaque registre a sa **vue rendue** (`./lplv registres --ecrire`), et on ne l'édite pas : un
  `.tsv` dont les cellules font deux cents caractères ne se lit ni dans un terminal ni sur une
  page. ⚠ Il n'y en a d'abord eu que deux — pour les lois et les portes — et les deux plus gros
  registres, 130 faits et 231 contradictions, se sont retrouvés sans **aucune** forme lisible.
  Ce n'était pas la donnée qui manquait, c'était sa lecture ; corrigé le jour même.
- ⭐⭐ Et la garde qui empêche le retour en arrière : **un rapport qui réintroduit une table de
  faits, de contradictions ou d'antériorité fait échouer le contrôle** (`./lplv registres`).
  Sans elle, la prose reprendrait la donnée un lot à la fois, et il y aurait de nouveau deux
  sources libres de diverger — ce que ce dépôt a payé trois fois (`75` D3, `80`, `87` §3).

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
| **R1** | **L'encre — la règle graduée** | que reste-t-il de l'encre au régime du prix, et peut-on juger un rendu sans se mentir ? | `08`–`10`, `12`, `14`, `19`–`24`, `36`, `45`–`46`, `58`–`60`, `63`–`65`, `72`, `75` §C1–C3 | `R1_encre.md` |
| **R2** | **L'excision et la réparation** | réparer une trace sert-il à quelque chose de mesurable ? | `03`–`07`, `11`, `17`, `34`, `75` D1 | `R2_excision.md` |
| **R3** | **La graine et le traceur** | le traceur est-il un tirage, et qu'est-ce qui gouverne où il va ? | `16`, `25`–`26`, `30`, `33`, `35`, `37`–`44`, `47`–`55` | `R3_graine_et_traceur.md` |
| **R4** | **Le déroulement** — *le graal* | qu'est-ce qui remplace l'humain du transfert ? | `76`–`79`, `81`–`86`, `90`–`114`, `75` §A et ses ~40 tranches, `75` §C (la campagne `0500P2`, 5–7 sept.) | `R4_deroulement.md` |
| **R5** | **La méthode et l'hygiène** | comment ce dépôt se trompe, et ce qui l'attrape | `56`–`57`, `61`–`62`, `80`, `87`–`89`, `75` §D2–D4 et §E | `R5_methode.md` |
| **R6** | **La littérature et l'antériorité** | qu'est-ce qui était déjà publié, et par qui | `00`, `27`, `32`, `66`–`71`, `73`–`74`, les pages *winners* et *open problems* | `R6_litterature.md` |

Ce qui n'entre dans aucun rapport parce que c'est du **procédé** (plans, batchs, registres, brouillons
de soumission) : `01`, `02`, `13`, `15`, `18`, `21`, `28`, `29`, `31`, `75` §0,
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
  `REGISTRE_faits.tsv` reprend leur forme et **est** la source de vérité ; les trois sont cités,
  pas fusionnés. ⚠ Le sens a hésité une fois : les registres ont d'abord été écrits comme des vues
  *dérivées* des rapports, ce qui gardait la donnée dans la prose **et** en écrivait une copie.
  Corrigé le jour même, sur remarque de l'auteur — c'est la donnée qui possède, la prose qui
  raconte.
- **Pas l'article.** `docs/article/` reste ce qu'il est ; les rapports le citent quand il condense.

## 5. Journal d'extension

| date | ce qui a été fait |
|---|---|
| 2026-09-11 | ouverture : carte, `PRIX.md` depuis les pages téléchargées le jour même |
| 2026-09-11 | `R4_deroulement.md` (34 documents lus) ; `R6_litterature.md` (11 documents et les pages du prix) ; `73`–`74` rattachés à R6 |
| 2026-09-11 | `R1_encre.md` (24 documents et `75` §C1–C3) ; `75` §C scindé : la campagne de déroulement `0500P2` (lignes 1476–6738) va à R4, les cases C1–C3 à R1 |
| 2026-09-11 | `R2_excision.md` (9 documents et `75` D1) ; quatre documents que la carte ne rattachait à rien : `11` et `17` → R2 (leurs producteurs vivent dans `src/excision/`, leur référent est `windcheck`), `16` → R3 avec `33` (la carte des treize est une question d'objet), `62` → R5 |
| 2026-09-11 | `R3_graine_et_traceur.md` (25 documents) ; `39` et `40`, rangés dans le procédé, portent des faits (le seam de correction ; la référence de 44 spires et l'absence de carte d'encre sur les rouleaux du prix) et sortent de cette liste ; la plage `37`–`55` de R3 recouvrait `45`–`46`, qui sont à R1 : la ligne dit désormais `37`–`44`, `47`–`55` |
| 2026-09-11 | `R5_methode.md` (8 documents et `75` §D2–D4/§E) ; deux rattachements corrigés : `57` était listé **à la fois** en R5 et dans le procédé, et `75` §E (ce qui est hors registre, dont la décision de l'auteur sur la soumission) y est lu — la ligne du procédé ne garde que `75` §0 |
| 2026-09-11 | les cinq registres, **dérivés** par `src/depot/registres.py` (35 contrôles, 6 sondes) : 130 faits, 231 contradictions, 91 lois, 73 portes, 30 antériorités. La dérivation a trouvé deux défauts de son propre lecteur (une source à trois chiffres refusée, donc les cinq faits les plus récents de R4 déclarés sans preuve ; une seconde table de section lue comme une donnée) et un défaut de sa propre batterie, signalé par `batteries_incapables_dechouer.py` : la sortie ne dépendait pas du compteur d'échecs |
| 2026-09-11 | les cinq registres `REGISTRE_*.tsv` deviennent **la source** (130 faits, 231 contradictions, 91 lois, 73 portes, 30 antériorités) et les tables quittent les six rapports, qui passent de 2 763 à 1 884 lignes. La bascule est vérifiée entrée par entrée avant toute suppression (`./lplv registres --comparer` : 0 perdue), et une garde refuse désormais qu'une table revienne dans un rapport. `src/depot/registres.py` (41 contrôles, 9 sondes) ; les 74 renvois « fait N » sont devenus des identifiants ; et chaque registre a sa vue rendue — les deux premières versions n'en avaient que deux, donc les faits et les contradictions n'avaient plus de forme lisible |
