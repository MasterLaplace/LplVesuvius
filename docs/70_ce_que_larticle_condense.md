# 70 — Ce que l'article condense, et ce qu'il laisse dehors

> ⚠⚠⚠ **Question de l'auteur, le 2026-09-03 :** *« en 68 docs, j'aimerais que l'article soit
> l'extrait de tout ce qu'on a appris. Est-ce que c'est le cas ? »* — après avoir constaté,
> à juste titre, que la vérification précédente n'avait lu que les premières lignes de chaque
> document.
>
> **Réponse mesurée : non.** Environ **21 documents sur 48 porteurs de résultat** ont leur
> conclusion dans l'article. Le reste se répartit en trois familles, et **une seule** est un
> vrai manque.

**Méthode, et ce qui la rend vérifiable.** Les 70 documents ont été lus **intégralement** —
23 389 lignes — par dix agents, un lot chacun, chacun devant rendre par document : nature,
résumé, conclusions falsifiables avec leurs chiffres, rétractations internes, et **deux
citations verbatim numérotées**, une après 60 % du fichier et une dans les quinze dernières
lignes. Les fiches sont conservées : [`registres/fiches_de_lecture.md`](registres/fiches_de_lecture.md).

⚠⚠ **La garde est la citation, pas la promesse.** Un agent qui n'aurait lu que l'en-tête ne
peut pas citer la ligne 147 d'un fichier de 148. Les **88 citations** ont été recherchées dans
les fichiers cités par `verifier_citations.py` : **88 retrouvées, 0 introuvable**. L'article a
été lu séparément et en entier — ses 1479 lignes — parce que le croisement ne se délègue pas.

⚠ **Et le croisement ne se fait PAS par les chiffres.** Il a été essayé : il rend « partiel »
pour les 70 documents et ne discrimine rien, parce qu'un document porte des dizaines de nombres
incidents. Pire, il fabrique des faux positifs — dans cette session `0,030` a matché la couleur
CSS `#b03030`, `105` a matché « 105 paires de segments », `14,3` a matché une borne d'intervalle
de confiance. Chaque correspondance ci-dessous a donc été **ouverte et lue en contexte**.

---

## 1. Le compte

| | documents |
|---|---:|
| **procédé** — plan, inventaire, feuille de route, registre, revue de littérature, texte de soumission | **22** |
| **résultat dans l'article** | **21** |
| **résultat hors de l'article** | **27** |

⚠ La frontière entre « procédé » et « résultat » est un jugement, et plusieurs documents sont
mixtes : `06` est un carnet de tâches dont une entrée porte un compte rendu complet, `29` est un
registre qui replie 525 énoncés. Le compte est donc un ordre de grandeur, pas une constante.

**La comparaison « 68 documents → 27 pages » n'est pas la bonne.** Un tiers du corpus est le
*procédé* — comment on a décidé quoi mesurer — et aucun article n'en contient. Ce qui se compare
est l'ensemble des résultats, et là **il en manque plus qu'il n'y en a**.

---

## 2. Ce qui est dedans, vérifié en contexte

| § de l'article | documents qu'il condense |
|---|---|
| §3 le test de convergence α | `38` (l'instrument), `49` (deux pannes), `51` (deux appuis), `52` (calibrer sur sa géométrie) |
| §4 le triage à distance | `19` (+0,381), `22` (la non-réplication), `20` en partie (`rigid_share` 22,1 %) |
| §5.1 le traceur est un tirage | `35` (78 tirages, 13 rouleaux) |
| §5.2 les artefacts de budget | `25` (campagne de graines appariée) |
| §5.4 le second plafond | `47` |
| §5.5–5.7 géométrie, chaîne, pavage | `44` |
| §6.2 ce que coûte un point estimé | `63`, `64`, `65` |
| §6.4 un cran en aval | `45` |
| §6.5 le témoin négatif | `46` + `60` (la constante qui l'avait fondé à l'envers) |
| §6.6 le juge | `09` |
| §6.7 où ça se branche | `68` §1 |
| §7 limites | `50` (la mémoire) |
| §8 reproductibilité | `61` (39 batteries sur 105) |

---

## 3. Ce qui est dehors — trois familles, une seule est un manque

### 3.1 ⭐ Hors périmètre : c'est un second papier (5 documents)

`08` `10` `58` `59`, et `68` §3–4. Tous côté **encre et régime de scan** : la première passe
complète, le segment entier à AUC 0,925, la résolution éliminée, la campagne de scan effondrée,
le nombre de Fresnel et les 103 cases vides.

L'article s'appelle *« Measuring segmentation quality »*. Y verser l'encre le rendrait
incohérent — c'est la contrainte que l'auteur a posée le jour même. **Ces cinq-là ne manquent
pas, ils attendent leur propre papier**, et ils en ont la matière.

### 3.2 ⚠ Résultats négatifs, absents (5 documents)

| doc | ce qui a été réfuté |
|---|---|
| **`17`** | détecter un saut de spire par la **phase d'enroulement publiée** : ρ **+0,517 (n=8) → +0,306 (n=30) → +0,149 (n=38)**, p = 0,37 — l'effet fond quand l'échantillon grandit, ce qui est la signature d'une absence d'effet. ⭐ Et le tableau des goulots du concours **réclame nommément** cette détection |
| **`26`** | `direction_fields` et `normal_grid_path` — les deux mécanismes censés gouverner la trajectoire du traceur — **ne la déplacent pas d'un centième**, y compris à ×100 d'intensité et avec 1,53 Go de vraies grilles coûtant 29 fois le temps de calcul. Contrôle positif présent |
| **`36`** | notre chaîne de rendu ne décale **pas** l'origine de la pile : accord à **14,3 µm** avec les volumes publiés, et elle place même mieux sa pile (100 % de pics dans le tiers central contre 62,5 %) |
| **`37`** | « sélectionner sur un axe, valider sur l'autre » : **1 accord sur 8** là où le hasard seul en donnerait ~4 |
| **`62`** | l'hypothèse de falaise de cache L3, réfutée par sa propre mesure — et d'un ordre de grandeur **×2142** |

⭐ Un journal sérieux prend des résultats négatifs, et le `17` en est un bon : une méthode que le
concours demande, essayée proprement, et qui ne marche pas. Ils ne tiennent pas dans **cet**
article, qui a déjà sa thèse ; ils feraient une note courte.

### 3.3 ⚠⚠ Dans le périmètre, et simplement absents (17 documents)

C'est la seule famille qui soit un manque. Les plus notables :

- ⭐⭐ **L'arc excision/réparation, quatre documents entiers** — `03` (reproduction de `windcheck`,
  tous les chiffres retrouvés exactement), `04` (les cellules excisées échantillonnaient-elles
  autre chose que du papyrus ? **non, H₀ non rejetée**), `05` (le prédicat vérifié est plus
  étroit que le défaut), `07` (**la réparation ramène les contacts à zéro et ne déplace pas la
  proximité anormale, 0,37 → 0,38 %**). Le mot « excision » apparaît **zéro fois** dans
  l'article. C'est une histoire complète, mesurée, sur la qualité d'une réparation — donc en
  plein dans le sujet.
- ⭐ **`33`** : le classement des treize rouleaux de `16` est **annulé** par sa propre incertitude
  — aucune des 78 paires séparée, aucun rouleau distinct du témoin après Holm. C'est exactement
  la thèse de l'article (une barre d'erreur change une conclusion), sur son propre corpus, et
  il ne la porte pas.
- ⭐ **`34`** : un **mode de panne silencieux** de `vc_tifxyz_selfcross`, l'outil officiel — « propre »
  et « rien mesuré » sortent par le même champ JSON.
- **`54`** : cinq rendus déclarés « plats » étaient **entièrement noirs**, et un défaut
  d'instrument (`alive = peak_value >= floor * peak_value.max()`, vrai partout sur un tableau de
  zéros) les comptait comme « 49 fenêtres avec matière ».
- **`53`** : le témoin **positif** de notre propre chaîne de rendu, avec son critère écrit avant
  la mesure (le document a été commité avec sa §3 vide).
- **`42`** : la boucle de correction tourne de bout en bout, et **318 points contre 56 630, soit
  0,56 % de la surface, ne suffisent pas** — α reste à 1.
- **`41`** : « au plus proche » échoue parce que dans un rouleau **le voisin d'en face est plus
  proche que le voisin d'à côté**.
- **`16`** : ce n'est pas la médiane qui sépare les treize rouleaux, c'est la **queue**.
- **`43`** : la chaîne radiale converge sur 4 spires sur 7, et ce qui décide n'est pas le pas mais
  la **portée physique du test de sortie**. *(Son existence est dans l'article §5.5 ; sa mesure, non.)*
- Et : `11` (onde radiale, ~13,87 m de papyrus), `12` (l'instrument de profondeur et ses deux
  révisions), `14` (fibres — n ≈ 70 requis, mesuré par analyse de puissance), `20` (l'erreur
  d'une trace est **structurée**, 98 segments sur 98 battent leur témoin de mélange), `24`
  (première trace sur un rouleau du prix, condamnée avant rendu), `55` (**30 causes candidates
  sur 4 murs : 19 éliminées, 10 confirmées, 1 bloquée**).

---

## 4. Deux défauts vivants que la relecture a fait remonter

⚠ Ni l'un ni l'autre n'est un défaut de l'article ; les deux sont des défauts du **dépôt**.

1. **`nappe/espacement_spires.py` tourne encore au niveau 2 de pyramide.** `winding-ruler` a
   mesuré chez lui que ce niveau **fusionne les feuilles voisines** — le pas mesuré baisse de
   **10,3 % en repassant au niveau 1, 36/36 négatif, sd 2,6** — et a tout recalculé. Notre outil
   propage le biais dans `ecart_de_maillages.en_micrometres()` via `spire_um`.
   ⚠ *Vérifié à la source* (`data/repos/winding-ruler/atlas/build_atlas_v2.py`, lignes 7–15) et
   non arbitré entre deux résumés : la fiche du `67` se lisait comme si l'article attribuait à
   tort ce chiffre à `winding-ruler`. **Les deux moitiés sont bien d'eux, la phrase de l'article
   est exacte.**
2. **`sensibilite_centre.py` repose sur une prémisse fausse** : l'ombilic **est** publié pour le
   rouleau qu'il nomme, sur `dl.ash2txt.org` — notre vérification portait sur le bucket S3.

---

## 5. Ce que je recommande, et ce que je ne recommande pas

**À faire avant tout envoi**, et c'est court : **trois des quatre résultats de tête de l'article
n'ont jamais été audités pour antériorité.** Les 14 clés du `66` couvrent l'énergie, la
résolution, la vérité terrain, le fold, σ, la dispersion, Hanley–McNeil, le témoin négatif, la
périodicité, α-fenêtre, l'extension, la graine, le pas, le juge — **aucune** ne couvre « le
traceur est un tirage », « la stabilité est un artefact de budget », ni « les segments publiés ne
pavent pas une feuille ».

**À ne pas faire** : verser les 27 documents restants dans l'article. L'auteur l'a dit et il a
raison — *« il faut que ça reste organisé et cohérent »*. Un article qui contient tout ne
démontre rien.

Ce qui est raisonnable, dans l'ordre :

1. auditer les trois résultats de tête pour antériorité ;
2. ~~écrire l'**arc excision/réparation**~~ ⚠⚠ **RETIRÉ le 2026-09-03.** En voulant rendre
   son chiffre-clé recalculable — la règle de l'article l'exigeait — la réparation a été
   rejouée et **le résultat ne tient pas** : sur les deux traces mesurables de Scroll 5 la
   proximité **baisse de 22 à 50 %**, là où `07` publie qu'elle ne bouge pas. Écrire la
   section aurait publié un résultat déstabilisé le jour même. L'arc reste le plus gros
   manque de l'article, et il demande d'abord d'être **refondé** →
   [`07`](07_reparee_nest_pas_propre.md), en-tête ;
3. ajouter `33` à §6.1, qui est **l'exemple le plus court** de la thèse de l'article : une barre
   d'erreur annule un classement publié, ici le nôtre ;
4. le second papier côté encre, quand la case vide du `68` §4 sera remplie.

---

**Instruments** : `verifier_citations.py` (88/88), `croiser.py` (essayé, insuffisant, et c'est
pourquoi le croisement final a été fait à la main). Fiches :
[`registres/fiches_de_lecture.md`](registres/fiches_de_lecture.md).
