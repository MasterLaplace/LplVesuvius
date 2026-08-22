# L'article — ce qu'il est, comment il se construit, et pourquoi il a cette forme

`article.typ` → `article.pdf`, 13 pages, **autonome** : il ne renvoie à aucun fichier de ce
dépôt et se lit sans le connaître.

```bash
./article/build.sh          # figures EN ANGLAIS + PDF
```

⚠ Le script **régénère** les figures au lieu de les copier. Une copie fige une traduction à
un instant donné, et le jour où un chiffre bouge, la figure de l'article dit encore
l'ancien. Chaque script refuse d'écrire une figure à moitié traduite, donc un libellé ajouté
sans sa traduction fait échouer la construction au lieu de produire un PDF franglais.

---

## Pourquoi UN article et pas plusieurs

La matière du dépôt se découperait volontiers en deux : les **instruments** (le test de
convergence, le tri à distance) et les **constats** qu'ils produisent (le traceur est un
tirage, la troncature, les segments ne pavent pas). Un article par moitié serait pourtant
un mauvais découpage :

- des instruments sans constat sont un outil dont personne ne sait s'il sert ;
- des constats sans instrument sont invérifiables — c'est justement leur méthode qui les
  rend opposables ;
- les deux moitiés auraient besoin du **même** préambule (ce qu'est un rouleau, un segment,
  une auto-intersection), donc les deux tiers de chaque papier seraient identiques. Le
  domaine appelle ça du *salami slicing* et le pénalise.

Un article a **une** thèse. Ici : *on peut mesurer la qualité d'une trace sans vérité
terrain, et quand on le fait, trois propriétés que la communauté tient pour acquises se
révèlent être des artefacts.* Les instruments sont la section Méthode, les constats la
section Résultats. C'est la forme standard.

## La charpente, section par section

| section | son rôle, et ce qu'un relecteur y cherche |
|---|---|
| **Abstract** | l'article entier en 250 mots : problème, méthode, **chiffres**, portée. Un lecteur décide ici s'il lit la suite. Il doit contenir des résultats, pas des promesses. |
| **1. Introduction** | pourquoi le problème existe, pourquoi il n'est pas résolu, et une **liste numérotée des contributions**. La liste est ce qu'on vous reprochera de ne pas avoir tenu. |
| **2. Background** | le minimum pour lire la suite, et **l'état de l'art avec ses limites chiffrées**. Citer un travail voisin sans dire ce qu'il ne couvre pas ne justifie pas le vôtre. |
| **3–4. Méthode** | assez précis pour être **réimplémenté** sans vous. D'où les formules : `(1)` définit α, `(2)` sépare les deux régimes, `(3)` donne l'angle par la flèche. |
| **5. Results** | ce qui a été mesuré, une sous-section par constat, chaque nombre avec son échantillon. Aucune interprétation nouvelle ici. |
| **6. Discussion** | ce que ça veut dire, et ce que ça vaut ailleurs. C'est le seul endroit où l'on a le droit de généraliser. |
| **7. Limitations** | ce que le travail **ne** montre pas. Une section Limitations franche est lue comme un signe de sérieux, pas de faiblesse — et son absence, comme un défaut. |
| **8. Conclusion** | trois phrases, sans chiffre neuf. |
| **References** | les travaux cités, numérotés. |

## Les conventions du domaine qu'on a suivies

- **Anglais.** Ce n'est pas obligatoire dans l'absolu, mais ça l'est ici : les quatre
  travaux cités sont en anglais, le concours est anglophone, et un préprint arXiv en
  `cs.CV` français ne serait pas lu. Les figures suivent — un texte anglais avec des
  légendes françaises est la première chose qu'un relecteur signale.
- **Une colonne, marges larges.** C'est la forme des préprints arXiv du domaine, et elle
  supporte de grandes figures. Le double colonnage est une contrainte de revue, pas une
  qualité en soi.
- **Chaque figure a une légende qui se lit seule.** Un relecteur regarde d'abord les
  figures. Si la légende ne dit pas ce qu'on voit et pourquoi c'est le résultat, la figure
  est décorative.
- **Les réserves sont dans le corps, pas en note.** Les encadrés rouges portent ce qui
  affaiblit le résultat : la résolution de l'instrument, le tirage qui n'a répliqué que
  deux fois sur trois, le nombre conservateur qu'on garde alors qu'un autre nous
  arrangerait. C'est ce qui rend le reste crédible.
- **On publie le corpus qui échoue.** Le §4.3 donne quatre corpus dont un seul marche.
  Publier le seul qui marche serait choisir son échantillon après l'avoir vu.

## Ce qu'il reste à faire avant d'en faire un vrai dépôt

| # | quoi |
|---|---|
| 1 | ⚠ **l'affiliation et l'identité de l'auteur** — « Independent researcher » est une affiliation valide sur arXiv, mais il faut un nom civil et un e-mail joignable |
| 2 | ⚠ **arXiv exige un endossement** (*endorsement*) pour un premier dépôt dans une catégorie comme `cs.CV`, obtenu auprès d'un auteur déjà publié dans cette catégorie |
| 3 | **une licence** sur le texte et les figures (CC BY 4.0 est l'usage) |
| 4 | **l'adresse du code** dans le texte : un article de méthode sans code exécutable ne sera pas repris |
| 5 | relire l'anglais avec quelqu'un dont c'est la langue — la structure est bonne, la langue se corrige |
