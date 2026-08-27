# 57 — Les tâches laissées, instruites une par une

> ⚠⚠ **Ce document répond à une question, pas à une liste.** L'auteur a demandé si des
> choses avaient été laissées de côté sans que personne ne le remarque. Le dépôt portait
> **41 sabliers** sur 18 documents et **56 items numérotés** dans trois documents de
> backlog, et rien ne distinguait une vraie tâche d'un titre de section.
>
> L'inventaire est désormais **mécanique** : `src/depot/taches_ouvertes.py` dérive les
> marqueurs des documents, `docs/registres/taches.tsv` porte le verdict, et les deux se
> vérifient **dans les deux sens** — un marqueur sans entrée fait échouer le contrôle, une
> entrée dont l'ancre a disparu aussi. Ce document raconte ce que l'instruction a trouvé.

**Réponse courte : rien n'a été sauté.** Les 41 sabliers précèdent presque tous la session
de rangement, et ils portent le programme de recherche — la soumission, l'application de la
correction. Mais **plusieurs mentaient** : ils annonçaient « en cours » des campagnes
revenues depuis, et deux posaient une question qui avait sa réponse ailleurs.

---

## 1. ⭐⭐⭐ Trois questions fermées PAR LA MESURE

### 1.1 « 18 voxels bruts ou rayon physique ? » — les deux artefacts sont sur la grille 7,91 µm

`07` §7 signalait depuis le 2026-08-19 que `sweep_PHerc1667.jsonl` n'enregistre ni son
volume ni son voxel, donc que « 18 voxels » pouvait valoir 43 µm ou 142 µm. **Aucune des
deux branches n'était la bonne**, et la mesure le dit sans ambiguïté :

| artefact | grille | rayon | en µm |
|---|---|---:|---:|
| `sweep_PHerc1667.jsonl` | **7,91 µm** | **80 vox** | 632,8 |
| `sweep_1667_pas.jsonl` | **7,91 µm** | **18 vox** | 142,4 |

⭐ **Et c'est prouvé par reconstruction, pas par lecture** : relancer avec ces paramètres
rend les **18** et **16** enregistrements **identiques** — `cells` et `measured` au chiffre
près — le seul changement étant le champ `echelle` que `baseline_sweep.py` écrit désormais.

> ⚠⚠ **Ma première mesure était fausse et le disait pourtant.** J'avais cherché le corpus
> dans `data/repos/windcheck/data/`, conclu « PHerc1667 n'y est pas », et mesuré sur
> `scroll1_tifxyz` — un autre corpus. `data/traces/PHerc1667/` existe, avec ses 20 traces et
> ses quatre grilles. Chercher au mauvais endroit puis conclure sur ce qu'on y trouve est la
> panne la plus banale de ce dépôt, et elle ne se voit pas : les nombres sortent, ils sont
> justes, ils parlent d'autre chose.

⭐ **Le remède est dans le code, pas dans le document** : le record porte maintenant son
`echelle` — voxel, pas inter-feuilles, rayon en voxels **et** en µm, racine, variante. Sans
lui, « 18 voxels » n'est pas un chiffre, c'est une devinette. Corriger le document aurait
recopié un nombre ; corriger l'outil le fait porter par chaque campagne suivante.

⚠ Et un piège reste, nommé : sans `--variante`, le script prend la grille **alphabétiquement
première** — 3,24 µm sur ce corpus, pas 7,91. Un run sans variante mais avec
`--voxel-um 7.91` écrirait donc un record qui **déclare** 142 µm pour un rayon de 58.

### 1.2 « 36 contre 72 » — un budget nominal contre un compte réalisé

`19` §5 relevait deux comptes contradictoires qu'aucun document ne démêlait.

- **36** est la valeur par défaut de `--windows` (`src/commun/zarr_depth.py`) : un **budget
  nominal**, jamais un compte. Le code ne sonde pas 36 points, il en sonde
  `steps × min(2·steps, grid_x)` avec `steps = int(sqrt(windows))`, soit environ le double.
- **72** est un compte **réalisé** (`sondees`), et il appartient à la campagne fibres :
  `docs/mesures/fibres_corpus.json`, 80 entrées, `sondees = 72` constant, produit par
  `fiber_orientation.py --windows 36` (9 amas → 18 ancres × 4 chunks).

⭐ **Compatibles**, et par la même arithmétique : 36 → 72 est ce que font les **deux** outils,
qui doublent tous deux leur nominal. Il n'y avait pas de contradiction, il y avait deux
grandeurs qui portaient le même mot.

### 1.3 « Existe-t-il un régime où la nappe gagne de l'aire en RESTANT convergée ? » — oui, et il est borné

`44` posait la question la moins chère de sa famille et ne l'avait jamais tranchée. Balayage
du budget `generations`, conception appariée, graine posée :

| budget | aire utile | auto-intersections | α | verdict |
|---:|---:|---:|---:|---|
| source officielle | 4,28 cm² | — | +0,000 | converge |
| **100** | **12,968 cm²** | **0** | **+0,000** | ⭐ **×3 d'aire sans quitter la feuille** |
| 200 | 28,62 cm² | 25 036 | +1,313 | en travers |
| 400 | 78,30 cm² | 168 104 | — | replié, non jugé |

⚠ Et c'est une **propriété**, pas un tirage : deux exécutions identiques rendent le même
maillage, écart **0 µm** mesuré par un second instrument.

---

## 2. ⚠⚠ Deux lectures CORRIGÉES — le document disait plus que la mesure

### 2.1 « La correction dégrade α » — non : les deux valeurs sont sous la résolution

`42` a appliqué une correction et rapporté α **+0,98 → +1,03**, lu partout depuis comme une
dégradation. Ce n'en est pas une : les deux valeurs sont à **0,0375** et **0,0200** de l'α de
plafond (+1,0135), donc **sous la résolution 0,20** de l'instrument. Elles sortent par
identité arithmétique — les deux lectures sont le bord de leur fenêtre — et la paire de
l'ancre a en plus une fenêtre plate.

⭐ La boucle n'a donc mesuré **ni gain ni perte** sur l'axe « suit une feuille ». Elle a redit
que les deux traces sont condamnées, ce qui était déjà vrai du témoin.

⚠⚠ **Ce qui EST une vraie dégradation**, appariée et valide : **0 → 11 753**
auto-intersections à `step_size` identique. Le gain reste donc à montrer, mais pas contre le
résultat qu'on croyait avoir.

### 2.2 M1ter — une des trois causes est déjà close, et `29` ne le savait pas

L'encre n'est pas lisible à 9 µm ; `29` laissait trois causes en lice — la résolution, ce
rouleau-ci, ou un papyrus vierge. ⭐ `46` §3 a mesuré, sur le même rouleau, que **la sortie
du modèle ne dépend pas de son entrée** : deux surfaces géométriquement incompatibles,
entrées distinctes de 11,0 %, rendent la même carte. La cause « papyrus vierge » ne peut donc
pas être testée par ce modèle-là, quel que soit le papyrus.

⚠ Correction de libellé au passage : le rouleau mesuré n'est **pas** PHerc0172 mais
**PHerc1447** (`36` §5bis) ; PHerc0172 est un autre rouleau, à 7,91 µm, qui ne fait pas
partie des treize du prix.

---

## 3. ⚠ Ce qui reste, et ce qui le bloque

| tâche | état | ce qui bloque |
|---|---|---|
| ~~**R2** — exporter le champ en coordonnées de fenêtre~~ | ✅ **fait le 2026-08-26** | `20` §8. Les trois groupes sortent, et l'export a trouvé un vrai défaut au passage : deux réponses à « le pic est-il au bord », qui divergent sur les piles **impaires**, c'est-à-dire sur toutes les piles réelles du dépôt |
| **appliquer le champ, et montrer le gain** | **ouverte** | il faut une correction qui améliore *quelque chose de mesurable* — §2.1 vient d'établir que l'ancien résultat ne dit pas le contraire. L'export n'était que la moitié amont, et elle est désormais livrée |
| `16` — régénérer les cartes de difficulté | ⚠ **décision** | le script d'aujourd'hui n'échantillonne plus comme les artefacts publiés (64 → 108 sondes) : régénérer **déplacerait** le tableau §3. Le correctif de code est fait ; l'acte de régénérer appartient à l'auteur |
| **transport vers une région sans vérité** | ⚠ **impossible sur ce couple** | mesuré : la face n'est périodique qu'à une taille de fenêtre où les enroulements ne rendent **aucune** fenêtre. Il n'existe aucun réglage où les deux côtés en ont |
| **thèse forte du témoin négatif** | ⚠⚠ **CHIFFRE SANS RECORD** | la ligne disait « sur PHercParis4 : ρ = +0,9984, σ à 2,4 % du modèle qui marche ». Vérifié le 2026-08-27 : **aucun fichier de résultat du dépôt ne porte ce nombre** — `temoin_negatif.json` est celui de `46`, sur `PHerc1447`, et rend 0,99792. Ni les deux cartes, ni leur JSON. Elles ont probablement disparu au rangement de `data/`. Tant que la mesure n'est pas relancée, ce chiffre est une anecdote et non un résultat |
| **M1ter — isoler la cause** | ⭐⭐ **résolution ÉLIMINÉE le 2026-08-27** | → [`58`](58_resolution_ou_rouleau.md) : le pas du témoin où le modèle marche était noté 2,4 µm et vaut **7,91 µm** — il est donc déjà à **9 %** des conditions de `PHerc1447` sur les deux axes. Créditer la résolution de **dix fois** cet écart, sur les deux axes, pénalité d'interaction comprise, ne rend qu'un facteur **2,1** sur les **45** à expliquer. Reste **ce rouleau-ci**, seul |
| **campagnes détachées** | **dépouillée pour la piste C** | 3 verdicts sur 17 essais jugeables ; les leviers de perte n'ont laissé que `temoin/` |

### ⚠⚠ Et une limite du garde-fou des chiffres, que cette ligne vient de révéler

`src/depot/verifier_chiffres.py` vérifie que **chaque chiffre recalculé depuis un fichier de
résultat apparaît dans un document**. Il ne vérifie pas — et ne peut pas vérifier — la
réciproque : qu'un chiffre écrit dans un document ait un fichier de résultat derrière lui. Un
nombre publié sans record est donc **invisible pour lui**, quel que soit son nombre d'étoiles.

⚠ La réciproque n'est pas mécanisable telle quelle : un document en prose contient des
centaines de nombres qui ne sont pas des mesures. Ce qui l'est, en revanche, c'est de **ne
publier un chiffre qu'en écrivant d'abord son JSON** — la règle que ce dépôt s'applique
partout ailleurs, et qui a été enfreinte ici une fois.

### La moitié qui EST mécanisable, mesurée puis écrite le 2026-08-28

⭐ `src/depot/chiffres_sans_record.py`. Le cadrage a été **mesuré avant** d'écrire la règle,
parce qu'une garde qui désigne tout ne désigne rien : sur les documents du dépôt, **1154**
écritures à trois décimales ou plus, dont **1060 déjà adossées** à un fichier de
`docs/mesures/`. Le résidu est de **51 chiffres dans 17 documents** — un inventaire
relisible, pas une alerte de masse.

⚠ **Chaque orphelin porte SA LIGNE et son contexte**, et ce n'est pas un confort : sans la
localisation, le triage commence par retrouver cinquante et un nombres dans dix-sept
documents, c'est-à-dire par refaire la recherche que la garde vient de faire. Un inventaire
qui ne dit pas où regarder produit une tâche qu'on repousse.

⭐ Et la localisation a **immédiatement** montré un faux positif que la liste nue cachait :
`3686,1946` n'est pas un décimal, c'est la forme de tableau `[3686,1946,1946,]` — dans du
code, la virgule est un séparateur. Les spans et blocs de code sont donc effacés avant la
recherche, ce qui a retiré **cinq** faux positifs (56 → 51). Les spans, pas la ligne entière :
une ligne de tableau peut porter un `thread_limit: 0` entre accents graves **et** une vraie
mesure à côté.

⚠ Trois décimales et pas deux : la prose est pleine de pourcentages et de tailles à une ou
deux décimales qui ne sont pas des mesures. Les identifiants (DOI, arXiv, Zenodo) sont écartés
sur leur **contexte de ligne** et non sur leurs chiffres — `2304.02084` est un numéro d'article
et `2304,02084 cm²` serait une mesure parfaitement plausible.

⚠⚠ **Le piège de l'adossement circulaire**, trouvé en regardant le défaut connu *disparaître*.
Compter `docs/mesures/taches_ouvertes.json` comme record fait passer `+0,9984` pour adossé — or
ce fichier est **dérivé des documents**, donc il adosse le chiffre à sa propre copie. Un
registre qui enregistre une plainte n'est pas un enregistrement de mesure. Les registres
dérivés sont nommés et exclus.

⚠⚠⚠ **Et la limite, assertée plutôt que contournée.** Même registres dérivés exclus,
`+0,9984` **échappe** à cette garde : il coïncide avec `0.9984133775266987`, un ratio médian
de `proximity_scroll1.jsonl`, c'est-à-dire d'un tout autre rouleau. À quatre décimales, sur
un corpus de plusieurs centaines de milliers de nombres, la collision est **attendue**. Régler
le seuil jusqu'à ce que ce cas passe serait choisir un nombre pour que le cas du jour sorte,
ce que ce dépôt refuse partout ailleurs — deux contrôles assertent donc la collision, pour
qu'elle ne soit pas oubliée.

⭐ Ce qui reste vrai et utile : **un orphelin est un vrai orphelin, un adossé n'est qu'un
candidat.** La garde a un sens et un seul, et son pouvoir croît avec le nombre de décimales
publiées. La levée complète demanderait de rapprocher chaque chiffre du record que son
**propre document nomme** — un travail à part, pas un réglage de seuil.

⚠ La suite ne lance que `--verifier` : le balayage nu sort en **1** sur les 51 entrées
existantes, et brancher un échec connu dans la suite la rendrait rouge en permanence, donc
ignorée. Le triage des 51 est désormais une tâche **dimensionnée** et **localisée** au lieu
d'un manque vague.

⚠ Vérifié sur cinq d'entre eux (`19,834872`, `20,747079`, `1,5036`, `0,825755`, `22,431`) :
**aucun fichier de l'arbre entier** ne les porte, pas seulement aucun fichier de
`docs/mesures/`. Ce sont donc de vraies aires et de vrais σ publiés depuis une sortie de
terminal. Les rétablir demande de **rejouer** les mesures, pas d'écrire un JSON après coup —
fabriquer le record depuis le document serait précisément l'adossement circulaire ci-dessus.

---

## Reproduire

```bash
lplv taches_ouvertes                      # l'inventaire, dérivé des documents
lplv taches_ouvertes --verifier           # le registre se garde lui-même, dans les deux sens

# §1.1 — les deux sweeps, régénérés à l'identique avec leur échelle
uv run python src/excision/baseline_sweep.py data/traces/PHerc1667 \
    docs/mesures/sweep_PHerc1667.jsonl --variante 7.91um --voxel-um 7.91 --search-radius 80
uv run python src/excision/baseline_sweep.py data/traces/PHerc1667 \
    docs/mesures/sweep_1667_pas.jsonl --variante 7.91um --voxel-um 7.91 --search-radius 18
```
