# L'article — ce qu'il est, comment il se construit, et pourquoi il a cette forme

`article.typ` → `article.pdf`, 18 pages, **autonome** : il ne renvoie à aucun fichier de ce
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
- ⭐⭐ **Un zéro se rapporte avec sa puissance, ou il ne se rapporte pas.** Le §4.3 a d'abord
  écrit « trois corpus non positifs » — et l'un des trois rendait **+0,425**. La colonne
  *detectable ρ* montre qu'aucun des trois n'avait la puissance de voir l'effet cherché :
  « ça ne réplique pas » et « on ne pouvait pas le voir » sont deux phrases très
  différentes, et compter les secondes comme les premières gonfle une réfutation.
- ⭐⭐ **Une section qui affaiblit votre propre instrument est ce qui le rend croyable.** Le
  §3.5 dit que α ≈ 1 a **deux** causes et que le test n'en distingue pas — sur un instrument
  qui est la contribution nº 1 de l'article. ⚠ Et la façon de l'écrire compte : on borne le
  dégât (aucun verdict positif touché, mesuré) au lieu de le minimiser, et on montre la
  borne en figure plutôt que de demander qu'on la croie.
- ⚠ **Une réserve se met là où le lecteur en a besoin**, pas reléguée en Limitations. Les
  encadrés rouges vivent dans la section qu'ils tempèrent ; Limitations récapitule, elle ne
  révèle pas.

## Ce qu'il reste à faire avant d'en faire un vrai dépôt

| # | quoi |
|---|---|
| 1 | ✅ **identité de l'auteur** — Guillaume Papineau, *Independent researcher*, adresse jointe, ORCID `0009-0006-1371-4119` en lien. ⏳ Reste le dossier ORCID lui-même, ci-dessous |
| 2 | ⚠ **arXiv exige un endossement** (*endorsement*) pour un premier dépôt dans une catégorie comme `cs.CV`, obtenu auprès d'un auteur déjà publié dans cette catégorie |
| 3 | **une licence** sur le texte et les figures (CC BY 4.0 est l'usage) |
| 4 | **l'adresse du code** dans le texte : un article de méthode sans code exécutable ne sera pas repris |
| 5 | relire l'anglais avec quelqu'un dont c'est la langue — la structure est bonne, la langue se corrige |

## Le dossier ORCID — la liste, par ordre d'importance

⚠⚠ **Ce n'est pas de la décoration.** L'article porte l'identifiant ; un lecteur qui le suit
tombe sur ce dossier, et ce qu'il y trouve devient une partie de ce que l'article vaut à ses
yeux. Un endosseur arXiv regardera exactement cette page.

| # | quoi | pourquoi |
|---|---|---|
| **1** | ⚠⚠ **Le nom public dit « Master Laplace », l'article signe « Guillaume Papineau »** — mettre le nom civil dans *Names*, et **garder « Master Laplace » dans *Also known as*** | un identifiant qui renvoie à un autre nom annule ce qu'il sert à garantir. Le champ *Also known as* existe précisément pour les pseudonymes, et il rend le dossier trouvable sous les deux |
| **2** | ⚠⚠ **Ajouter et VÉRIFIER une adresse personnelle permanente** — les deux adresses actuelles sont scolaires, et seul `ulaval.ca` est un domaine vérifié | le jour où les deux comptes d'école expirent, le dossier devient irrécupérable. C'est la seule action vraiment irréversible si elle est faite trop tard |
| **3** | ⚠ **Université Laval est classée *Employment*** — c'était une année d'échange, donc *Education and qualifications*, avec sa **date de fin** | classer des études en emploi est une inexactitude que quelqu'un qui lit vraiment le dossier remarquera. Et sans date de fin, le dossier laisse entendre que c'est en cours |
| **4** | **Ajouter Epitech** dans *Education and qualifications*, **en cours**, diplôme attendu | le dossier ne montre aujourd'hui aucune formation, ce qui est plus étrange qu'un cursus en cours. ⭐ Les deux entrées « EPITECH » et « EPITECH European Institute of Information Technology » proposées par ORCID sont **le même organisme** — vérifié : ROR n'a qu'un enregistrement, `ror.org/039jywa41`, et les deux libellés y sont des noms du même dossier. Prendre le nom long (un lecteur hors de France ne sait pas ce qu'est « EPITECH »), puis **vérifier que la ligne affiche bien ce ROR** |
| **4 bis** | **Le stage de 5ᵉ année va dans *Employment***, avec l'intitulé du poste et la date de début | c'est la seule ligne d'emploi réelle. ⚠⚠ Et elle ne doit PAS remonter dans l'article : mettre l'entreprise en affiliation laisserait entendre qu'elle a commandité ce travail — ce qui serait faux, et poserait en prime une question de propriété intellectuelle qui n'a pas lieu d'être. *Independent researcher* est exact **parce que** le stage est ailleurs |
| **5** | ⭐ **Remplir *Websites & social links*** : GitHub, les dépôts du projet | c'est là que le pseudonyme gagne sa place — il relie l'identité d'auteur à l'identité de développeur, et c'est ce qui donne du corps au dossier tant qu'il n'y a pas de publication |
| **6** | ⭐ **Remplir la *Biography*** : trois ou quatre phrases sur ce qu'on cherche | c'est la première chose qu'un lecteur lit après le nom |
| **7** | **Remplir les *Keywords*** : virtual unwrapping, Herculaneum papyri, X-ray tomography, surface segmentation, computational imaging | c'est ce qui rend le dossier trouvable par sujet |
| **8** | ⭐ **Ajouter les dépôts comme *Works* de type « software »** | ORCID accepte le logiciel comme production de recherche. Un dossier à zéro travaux se lit comme un compte vide ; deux dépôts et un préprint se lisent comme un travail en cours |
| **9** | Une fois le préprint en ligne, l'ajouter dans *Works* avec son identifiant arXiv, puis l'épingler en *Featured work* | c'est ce qui transforme l'identifiant en trace |
| 10 | Activer la mise à jour automatique (Crossref, DataCite) dans *Trusted parties* | les futurs DOI arrivent tout seuls, et le dossier cesse de demander de l'entretien |

⚠ Les points **1 et 2** sont les seuls urgents : le premier parce que l'article est déjà écrit
avec le lien, le second parce qu'il devient impossible après expiration des comptes.
