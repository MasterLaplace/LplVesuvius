# Le grand ménage — plan, mesuré avant d'être écrit

> ⚠⚠ **Ce document est un PLAN, pas un résultat.** Il est écrit pour être repris par une session
> neuve qui n'a pas le contexte. Tout ce qu'il avance est mesuré, et la commande qui produit
> chaque chiffre est donnée. Ce qu'il **décide de ne pas faire** est écrit aussi — c'est la
> partie qu'on oublie et c'est celle qui empêche la question de revenir tous les quinze jours.

Cadré avec le skill [`concevoir-avant-coder`](../../LplCraftSkills/skills/concevoir-avant-coder/SKILL.md) :
besoin avant solution, YAGNI sur ses deux axes, ossature en stubs, modules et paliers, pipeline
adaptatif par modes et compteurs, échelle d'escalade.

---

## 1. Ce qui est MESURÉ, et ce que ça corrige de l'impression de départ

L'impression était : *« sept dossiers blindés de scripts, une montagne de doublons, des données
en double, des choses recalculées »*. Trois de ces quatre points sont vrais, un est faux, et
c'est le plus gros.

### 1.1 ⚠⚠ Les « sept dossiers de scripts » sont DEUX dossiers et cinq environnements

| dossier | fichiers **source** | lignes | poids réel | poids total |
|---|---:|---:|---:|---:|
| `analysis/` | **123** | 35 561 | 3,2 M | 3,2 M |
| `tools/` | **73** | 8 359 | 624 K | 624 K |
| `experiments/` | 16 | 3 464 | 624 K | **351 M** |
| `tracecheck/` | 4 | 1 310 | 144 K | 144 K |
| `htr/` | **1** | 185 | 264 K | **5,1 G** |
| `inference_xpu/` | **1** | 169 | 128 K | **6,3 G** |
| `inference/` | **0** | 0 | 256 K | **5,2 G** |

`htr/`, `inference/` et `inference_xpu/` ne portent **aucun code** ou presque : ce sont des
`.venv`, **16,6 Go de paquets installés**. Ce qui donne l'impression d'une montagne est un
environnement, pas un programme.

⚠ Et `inference/` **sert** : c'est l'environnement le plus utilisé du dépôt, **25 sites
d'appel** (`uv run --project inference`). Il porte torch/transformers pour l'inférence d'encre.
Le supprimer casserait un quart des commandes.

```bash
for d in analysis experiments htr inference inference_xpu tools tracecheck; do
  n=$(find "$d" \( -name '*.py' -o -name '*.sh' \) -not -path '*/.venv/*' | wc -l)
  printf '%-16s %4s fichiers  %8s total\n' "$d" "$n" "$(du -sh "$d" | cut -f1)"
done
grep -rl -- "--project.*inference\b" tools/*.sh analysis/src/*.py | wc -l
```

### 1.2 ⭐ La duplication de code est PETITE en volume et DÉJÀ DIVERGENTE

630 fonctions définies, **328 noms distincts**, **40 noms répétés**. Mais les gros répétés sont
**structurels** et voulus : `main` ×122 (un par verbe), `verifier`/`_verifier` ×75 (une batterie
par module — c'est la règle du dépôt).

Les vrais doublons sont petits, et c'est leur **divergence** qui coûte :

| fonction | copies | **variantes distinctes** |
|---|---:|---:|
| `_police` | 15 | ⚠⚠ **4** |
| `_pixels` | 14 | ⚠ **3** |
| palette `FOND`/`ENCRE`/`GRIS`/`TRAIT` | 14 | à vérifier |

**~300 lignes sur 35 561, soit 0,8 %.** Quatre variantes de la même fonction, c'est exactement la
classe de défaut que ce dépôt traque partout ailleurs : *la même chose qui n'est plus la même*.

```bash
grep -hoP '^def \K\w+' analysis/src/*.py | sort | uniq -c | sort -rn | head -20
for f in $(grep -l "^def _police" analysis/src/*.py); do
  awk '/^def _police/,/^$/' "$f" | md5sum | cut -c1-8
done | sort | uniq -c
```

### 1.3 ⚠⚠⚠ Le vrai gaspillage : **97 Go de rendus**, et un cas mesuré de recalcul

`data/` pèse **177 Go**, 80 dossiers de premier niveau, **68 540 fichiers**. Dont :

| | poids | part |
|---|---:|---:|
| **324 dossiers `rendu*`** | **97 Go** | ⚠⚠ **55 %** |
| `data/layers/` | 51 Go | 29 % |
| `data/traces/` | 17 Go | 10 % |

Et le recalcul n'est pas une hypothèse — **il a été mesuré le 2026-08-25** : la même surface
(`morceau_00`) a été rendue et profilée **deux fois**, dans deux campagnes différentes, pour un
résultat **bit-pour-bit identique** :

```
c1ff66d445eea26dadfa5f4d0b1e6173  data/chaine_tangentielle/profil_morceau_00/g0_n41/profil.json
c1ff66d445eea26dadfa5f4d0b1e6173  data/chaine_courte/profil_morceau_00/g0_n41/profil.json
```

**~15 minutes de rendu payées deux fois**, parce que le cache de `profiler_une_surface.sh` est
**par répertoire de destination**, pas par contenu.

⚠ **En revanche, l'hypothèse « téléchargé en double » ne tient PAS** dans `layers/` et
`traces/` : le proxy « même nom + même taille » n'y trouve que **1,0 Go**, presque uniquement
des `meta.json` de quelques centaines d'octets, qui sont légitimement un par maillage. Sur tout
`data/`, le même proxy annonce 17,4 Go — mais il **surcompte** : ce sont des chunks zarr nommés
`40`, `41`… de 2 Mio, qui portent le même nom dans des volumes différents **sans être le même
contenu**. À confirmer par hachage réel avant d'effacer quoi que ce soit.

```bash
find data -maxdepth 3 -type d -name "rendu*" | wc -l
find data -maxdepth 3 -type d -name "rendu*" -exec du -s {} + | awk '{t+=$1} END {printf "%.1f Go\n", t/1048576}'
```

### 1.4 ⚠ `docs/` mélange quatre natures de choses, et `.lances/` s'accumule

`docs/` : **528 entrées** — 57 markdown (de la prose), **341 JSON** (des résultats), 73 images
(des figures), et **~57 `.log` / `.csv` / `.jsonl`** (des sorties brutes de campagne). Quatre
choses qui n'ont ni le même cycle de vie ni le même lecteur, dans un seul dossier.

`.lances/` : **196 fichiers**, soit ~65 lancements × (`.log`, `.pid`, `.sh`). Rien ne les purge.

---

## 2. Le besoin, avant la solution

Ce que le ménage doit rendre **observable**, et qui le constate :

1. **Un rendu déjà calculé n'est jamais recalculé.** Constatable : relancer une campagne qui
   partage une surface avec une autre ne relance aucun rendu, et le journal le dit.
2. **Un rouleau se voit d'un seul endroit.** Constatable : `ls data/PHercParis4/` montre tout ce
   qu'on possède de ce rouleau, et une seule commande dit ce qui est calculé, ce qui manque et
   ce qui a coûté quoi.
3. **Un verbe se découvre sans lire la doc.** Constatable : `lplv --help` liste les verbes,
   `lplv <verbe> --help` décrit celui-là, et **aucun des deux ne peut périmer** puisqu'ils sont
   dérivés du code.
4. **Une fonction de dessin existe en un seul exemplaire.** Constatable : `_police` est définie
   une fois, et le garde-fou des batteries échoue si une seconde apparaît.

⚠ **Ce qui est vrai aujourd'hui et ne le sera plus** : les chemins `data/<campagne>/…` sont
écrits en dur dans des dizaines de scripts et dans les blocs « Reproduire » de 57 documents. Une
réorganisation de `data/` **casse ces chemins**. C'est la contrainte dure du chantier B, et elle
décide de son ordre.

---

## 3. Les quatre chantiers, indépendants, ordonnés par rapport bénéfice/risque

> ⚠ **Ils sont indépendants EXPRÈS.** Chacun se livre seul, se juge seul, et se retire seul.
> Un « grand refactor » monolithique est exactement ce que le §2 du skill interdit : un diff que
> personne ne peut relire, donc approuvé au lieu d'être relu.

### ⭐ Chantier A — le cache de rendu par CONTENU (le seul qui rapporte des gigaoctets)

**Le besoin** : ne jamais recalculer un rendu déjà calculé, même dans une autre campagne.

**La forme** : une clé = `hash(contenu du tifxyz) + paramètres de fenêtre + niveau`. Un dossier
`data/cache/rendus/<clé>/`, et les campagnes y font un lien plutôt qu'un rendu.

- ⭐ Il y a **déjà** un cache, mais indexé par *destination* : le rendre indexé par *contenu*
  est un changement local dans `tools/profiler_une_surface.sh` et rien d'autre.
- ⚠ **Ce qui doit être compté** (skill §8, règle 1) : `cache_hit` / `cache_miss`, écrits dans le
  journal. Un cache dont on ne mesure pas le taux de succès est une devinette avec un dossier.
- ⚠⚠ **Et le repli est bruyant** : un manque de cache se dit, il ne se déduit pas d'un temps
  d'exécution.
- **La porte de sortie** : relancer la campagne `chaine_courte` après `chaine_tangentielle` ne
  déclenche **aucun** rendu de `morceau_00`, et le compteur dit `cache_hit=1`.

**Ce que ça rapporte, mesuré** : sur 324 dossiers de rendu et 97 Go, la part réellement
dupliquée reste **à mesurer par hachage** — c'est la première tâche du chantier, et elle est
bon marché. Le cas connu vaut 15 minutes ; il y en a probablement des dizaines.

### ⭐⭐ Chantier B — un dossier par ROULEAU, et un manifeste JSON par rouleau

**Le besoin** : que ce qu'on possède d'un rouleau se lise d'un seul endroit, et que la mise à
jour soit une écriture dans **un** objet plutôt que dans quinze fichiers éparpillés.

**La forme proposée** :

```
data/
  PHercParis4/
    manifeste.json          ← l'objet unique : ce qu'on a, où, calculé quand, par quoi
    volumes/                ← boîtes zarr locales (prédictions, scan)
    couches/                ← rendus de couches téléchargés
    maillages/              ← tifxyz : traces, morceaux, chaînes
    campagnes/              ← résultats de campagne, un dossier par campagne
  PHerc1447/  …
  cache/rendus/             ← partagé entre rouleaux (chantier A)
```

Le **manifeste** est l'objet flexible demandé : une entrée par artefact, avec sa provenance
(commande, date, version du code), son coût, et son hash. C'est lui qui rend le reste
interrogeable, et c'est lui qui remplace « chercher dans quinze dossiers ».

⚠⚠ **La contrainte dure, et elle commande l'ordre du chantier** : des dizaines de scripts et
les blocs « Reproduire » de 57 documents écrivent `data/<campagne>/…` en dur. Donc :

1. **d'abord** un verbe `lplv chemin <rouleau> <genre> <nom>` qui rend le chemin — un seul
   endroit qui sait où sont les choses ;
2. **ensuite** la migration, avec des **liens symboliques** depuis les anciens chemins, pour que
   rien ne casse pendant la transition ;
3. **enfin** le retrait des liens, quand un garde-fou confirme que plus aucun script ni document
   ne cite un ancien chemin.

⚠ **Écrire la migration comme un script rejouable**, pas comme une session de `mv`. Une
réorganisation de 177 Go faite à la main n'est pas reproductible, donc pas vérifiable.

### ⭐⭐⭐ Chantier C — nommer le pipeline à plugins qui EXISTE DÉJÀ

**C'est le chantier le plus rentable, et c'est aussi celui qui demande le moins de code neuf**,
parce que l'architecture est déjà là — elle n'a simplement pas de nom.

Mesuré : sur **123 modules** de `analysis/src/`, **122 ont un `main()`**, **75 exposent
`--verifier`**, **63 exposent `--json`**. C'est-à-dire que **123 greffons de forme uniforme
existent**, sans registre et sans point d'entrée.

> ⚠⚠ Le skill (§7) dit de ne pas construire une architecture à plugins avant le **deuxième
> implémenteur réel**. Ici il y en a **cent vingt-trois**. La question n'est donc pas *faut-il
> des plugins*, elle est *pourquoi n'ont-ils pas de registre*.

**La forme** : un point d'entrée `lplv` qui découvre les modules, expose `lplv <verbe> --help`
dérivé de l'`argparse` du module, et `lplv --help` qui liste les verbes avec la première ligne
de leur docstring.

Ce que ça achète, et c'est la raison invoquée par l'auteur : **une aide qui ne peut pas
périmer**, parce qu'elle est dérivée du code et non recopiée à côté (skill `doc-derivee`).

⚠ **Ce qu'il ne faut PAS faire** : un registre à l'exécution avec cycle de vie, versions de
contrat et mode dégradé. Les modules sont dans le même dépôt, compilés ensemble : la découverte
par le système de fichiers suffit, et tout le reste serait le prix d'un liage tardif dont
personne n'a besoin ici (skill §7, tableau palier/plugin).

**Les paliers** tombent alors tout seuls, et le dépôt en a déjà trois de fait :

| palier | ce qu'il contient | ce qui le prouve |
|---|---|---|
| **prod** | ce que la branche de release porte | `tools/faire_la_release.sh` la construit déjà |
| **dev** | plus l'outillage de campagne | c'est ce qu'on lance tous les jours |
| **debug** | plus les sondes et les verbes de diagnostic | `--plancher`, les cartes, les sondes |

⚠ Le piège nommé par le skill (§7) s'applique déjà : **le palier que personne ne construit
pourrit**. La release est construite par un script ; le vérifier reste une tâche de ce chantier.

### ⭐ Chantier D — l'extraction du dessin, et le rangement de `docs/`

Deux petites choses, groupées parce qu'elles ne coûtent presque rien.

1. **`analysis/src/figure_commune.py`** : `_police`, `_pixels`, la palette. C'est le seul endroit
   où des copies ont **réellement divergé** (4 variantes de `_police`). ⚠ Et un garde-fou dans
   `tools/temoins.sh`, sur le modèle de « batteries non lancées » : *aucune seconde définition
   de `_police` dans l'arbre*. Sans lui, les copies reviendront.
2. **`docs/` séparé par nature** : la prose reste, les 341 JSON de résultats et les ~57 logs
   partent dans `docs/resultats/` et `docs/journaux/`. ⚠ **Les blocs « Reproduire » citent ces
   chemins** — même précaution que le chantier B, et le garde-fou `tools/images_des_docs.sh`
   existe déjà pour les images.
3. **`.lances/` se purge** : 196 fichiers, ~65 lancements. Une rétention (les N derniers, ou
   les 30 derniers jours), écrite dans le script qui les crée.

---

## 4. ⚠⚠ Ce qu'on décide de NE PAS faire, et pourquoi

C'est la partie que le skill dit qu'on oublie toujours d'écrire.

| Écarté | La raison, mesurée |
|---|---|
| **Un grand refactor monolithique** | 0,8 % de duplication réelle. Les chiffres ne le justifient pas, et un diff que personne ne peut relire est approuvé, pas relu |
| **Supprimer `inference/`** | il porte **25 sites d'appel**. Il ne contient aucun code parce que c'est un environnement, pas un programme |
| **Fusionner `analysis/` et `tools/`** | frontière réelle et à sens unique : `tools/*.sh` orchestre, `analysis/src/*.py` mesure. Aucune mesure n'appelle un outil. C'est déjà la bonne direction (skill §7) |
| **Un registre de plugins à l'exécution** | même dépôt, même build : la découverte par le système de fichiers suffit. Le liage tardif n'a aucun demandeur |
| **Effacer les 17,4 Go de « doublons »** | le proxy *même nom + même taille* **surcompte** sur les chunks zarr. À hacher avant d'effacer — et un effacement n'est pas réversible |
| **Toucher aux `.venv`** | 16,6 Go, mais reconstructibles et déjà hors de git. Le poids n'est pas dans le dépôt versionné |
| **Réécrire les 57 documents** | ils portent des mesures datées. Les chemins qu'ils citent se réparent par des liens, pas par une réécriture |

---

## 5. L'ordre recommandé, et pourquoi celui-là

1. **C (le registre `lplv`)** en premier : aucun risque, aucun déplacement de données, et il
   donne le vocabulaire dont B a besoin (`lplv chemin …`).
2. **A (le cache par contenu)** ensuite : c'est le seul qui rapporte des gigaoctets et du temps,
   et il est local à un fichier.
3. **D (le dessin, `docs/`, `.lances/`)** : bon marché, et le garde-fou empêche la rechute.
4. **B (la réorganisation de `data/`)** en dernier : c'est le seul qui casse des chemins, donc
   le seul qui a besoin que tout le reste soit stable.

⚠ **Et chacun se termine par la même porte** : `./tools/temoins.sh` vert, avec le compte relu et
réécrit dans `docs/31_roadmap.md` et `HANDOFF.md`.

---

## 6. La porte de sortie, avant d'implémenter quoi que ce soit

Les cinq réponses que le skill exige, pour le chantier qu'on attaquera :

1. **le comportement observable qui change** — § 2 ci-dessus, quatre énoncés constatables ;
2. **l'ossature en stubs** — à écrire, une par chantier, avec des noms définitifs et des corps
   qui **lèvent** ;
3. **ce qui est injecté** — le chemin d'un rouleau, le cache, le journal. Rien d'autre : ce sont
   les trois choses qui touchent le monde ;
4. **les points d'extension justifiés par un deuxième cas RÉEL** — le registre l'est par 123 ;
   rien d'autre ne l'est ;
5. **ce qu'on a décidé de ne pas faire** — § 4 ci-dessus.
