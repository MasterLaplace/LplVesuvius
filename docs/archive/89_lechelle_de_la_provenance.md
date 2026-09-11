# 89 — L'échelle de la provenance : ce que « 0 orphelin » cachait

> ⭐⭐⭐ **`artefacts_orphelins` disait « 0 artefact sans producteur ». Il dit désormais par quel
> BARREAU chaque artefact est passé : 3 observés par une chaîne, 1111 devinés par une tige — dont
> 675 sur douze caractères ou moins, et 275 sur cinq. Le nombre d'orphelins ne bouge pas ; ce qui
> change est qu'on sait enfin ce qu'il vaut.**

## 1. Pourquoi une échelle et pas un seuil plus strict

[`87`](87_la_forme_du_depot.md) a mesuré le prix du verdict : `juge_scroll4.json` était déclaré
produit parce que le mot `juge` apparaît quelque part dans `src/`. Le remède évident — un préfixe
plus étroit — était **déjà réfuté par la garde elle-même** : chercher le nom exact signalait
**389 orphelins sur 568**, et « une alerte qui désigne les deux tiers du corpus ne désigne rien ».

⭐ Le remède est donc ailleurs : `lplv enchainer` ([`88`](88_enchainer.md)) **observe** quel verbe
écrit quel fichier. La garde devient une **échelle d'escalade** au sens du skill
`concevoir-avant-coder` :

| barreau | ce qu'il affirme | prix | compte |
|---|---|---|---:|
| **1 · OBSERVÉ** | une chaîne a **vu** ce fichier apparaître pendant un étage | certain | **3** |
| **2 · DEVINÉ** | l'heuristique de tige a matché, **et sa longueur est retenue** | la dette | **1111** |
| **3 · ORPHELIN** | ni l'un ni l'autre | l'alerte | **0** |

⚠⚠ **L'invariant que les skills imposent est exactement ce qui manquait** : *un barreau a le droit
de baisser la PRÉTENTION du résultat, jamais la BARRE, et jamais en silence.* Le fichier disait
« produit » pour les barreaux 1 et 2 **indistinctement**.

## 2. La dette, chiffrée

```
4 car. ×12 · 5 car. ×275 · 6 car. ×30 · 7 car. ×22 · 8 car. ×162
9 car. ×70 · 10 car. ×67 · 11 car. ×10 · 12 car. ×27
```

**675 verdicts sur 1111 (61 %) tiennent à douze caractères ou moins, 275 à cinq, 12 à quatre.**

⚠⚠ **Et la dette ne fait PAS échouer la garde**, délibérément : la rendre rouge sur 61 % du corpus
la ferait désapprendre — c'est le compromis que sa propre docstring avait déjà établi. Ce qui
échoue reste un **orphelin**, plus quatre incohérences de l'échelle elle-même.

⭐ **La dette ne peut que rétrécir** : chaque chaîne écrite déplace des artefacts du barreau 2
vers le 1.

## 3. ⭐⭐ Ce que les contrôles neufs ont attrapé dès le premier parcours

Trois défauts, **tous les miens**, dont deux dans les contrôles que je venais d'écrire.

**⛔ « 3 enregistrements créditent un fichier disparu »** — les trois PNG de `84`/`85`/`86`, qui
existent et sont commités. Je testais « disparu » contre la **liste filtrée** (`SUFFIXES` ne
contient pas `.png`), pas contre le disque. **Un fichier qui existe sans être un artefact *gardé*
n'est pas un fichier disparu.**

**⛔ « les barreaux couvrent tout le corpus — 3+1111 pour 1115−2 »**, à une unité près. Cause :
je soustrayais `len(EXEMPTS)` en supposant que tous les exemptés sont rencontrés.

⭐⭐ **Et cette unité manquante en cachait une vraie : une exemption morte.**
`src/outils/repos.tsv` était exempté d'un parcours qui ne retenait que `docs/` et `data/` — la
décision **ne protégeait rien**, et personne ne pouvait le voir. Le skill tranche entre
*injoignable* (un défaut : on répare l'accessibilité) et *rare* (un filet en bon état). Celle-ci
était injoignable, et la réparation coûte **zéro** : `git ls-files src/**` ne rend qu'**un** fichier
à suffixe d'artefact, exactement celui que la table nomme. Le parcours balaye désormais `src/`, et
l'exemption protège la seule chose qu'elle désigne.

⚠ Un contrôle neuf garde le cas pour de bon : **une exemption qui porte sur un fichier hors du
parcours est nommée**.

## 4. ⭐ Neuf contrôles avant de payer 430 secondes

`lplv enchainer` a mesuré le coût de cette garde : **430,76 s**, soit **81 %** du budget des quatre
gardes de l'arbre. Une logique qu'on ne peut exercer qu'en payant ce parcours est une logique que
personne n'exerce en développant.

`verifier_la_mecanique()` exerce l'échelle et ses deux lecteurs sur **entrée fabriquée**, en
millisecondes, **avant** le parcours — et sort sans le payer si elle échoue. Elle couvre notamment
qu'un run **à sec** ne crédite rien (il n'observe rien par construction, donc le créditer
affirmerait une provenance qu'aucune écriture n'a produite) et qu'un enregistrement illisible ne
fait pas tomber la garde.

## 5. ⚠ Un piège d'outillage repayé sous une forme neuve

Mes relances successives ont laissé **trois parcours de 430 s tourner en concurrence**, se
disputant les entrées-sorties — aucun ne finissait, et aucune sortie n'apparaissait, les tampons
n'étant vidés qu'à la fin. Le dépôt connaissait « deux `validate.sh` concurrents cassent le
build » ; voici sa variante en lecture seule : **pas de corruption, mais pas de fin non plus**.
Tués **par PID**, jamais par motif — `pkill -f` matche sa propre ligne de commande et a déjà tué
mon shell deux fois.

## Reproduire

```
uv run python src/depot/artefacts_orphelins.py --verifier
lplv enchainer docs/chaines/les_gardes_de_larbre.chaine
```
