# 44 — Où la chaîne se trouve dans le rouleau

La liste des tâches ouvertes de [`43`](43_la_chaine_des_spires.md) finissait par celle-ci,
marquée ⭐ : *« recoller les spires en une seule surface — la première chose de ce dépôt qui
ressemble à un morceau de rouleau déroulé »*. Avant d'écrire ce recollement, il fallait
mesurer ce que la chaîne couvre réellement.

⚠⚠ **La mesure dit que la tâche était mal posée.** Une chaîne radiale n'est pas une bande de
papyrus, c'est une **colonne** — et deux nappes voisines sont séparées, le long du papyrus,
par la circonférence entière qu'on ne possède pas.

![où la chaîne se trouve dans le rouleau](images/44_geometrie_chaine.png)

Instrument : `analysis/src/geometrie_chaine.py` (39 témoins hors ligne).
Données : la chaîne à pas de rayon 0,25, neuf nappes, `data/spires_pas025`.

---

## 1. L'instrument, et pourquoi il est aveugle à l'axe

Pour savoir où une nappe se trouve dans un rouleau, il faudrait normalement connaître l'axe
du rouleau. On ne le connaît pas, et le chercher demanderait une hypothèse de plus.

⭐ **Le contournement tient en une phrase** : sur un cylindre, une ligne de grille qui court
le long de la circonférence **tourne**, une ligne qui court le long de l'axe est **droite**.
On n'a donc pas besoin de savoir où est l'axe pour savoir laquelle des deux directions de
grille est laquelle — il suffit de regarder laquelle courbe.

La courbure se mesure par la **flèche** de l'arc — la distance maximale entre l'arc et sa
corde. Pour un arc de demi-angle $\varphi$, la corde vaut $2R\sin\varphi$ et la flèche
$R(1-\cos\varphi)$, d'où

$$\varphi = 2\arctan\!\left(\frac{2\,\text{flèche}}{\text{corde}}\right)$$

exactement, sans approximation petit-angle.

⭐ **Et le rayon s'élimine.** C'est ce qui rend cette mesure utilisable là où le rayon,
lui, n'est pas déterminé (§6) : l'angle balayé se lit sur la forme de l'arc, sans jamais
avoir à décider de quel cercle il est un morceau.

⚠⚠ **La première version de ce discriminant était fausse et le témoin l'a refutée.** Elle
ajustait un cercle sur chaque ligne et divisait la longueur d'arc par le rayon. Sur une ligne
**droite** l'ajustement est singulier : il rend un rayon minuscule, donc un angle de 3,9 rad
— si bien que la direction axiale passait pour la plus courbe, et **une surface plane pour un
rouleau**. La flèche ne peut pas exploser ; elle tend vers zéro.

---

## 2. Deux défauts de l'outil que seules les vraies données ont trouvés

Le témoin passait à 26 contrôles sur des cylindres synthétiques. La première mesure réelle a
rendu **« surface plane, il n'y a pas d'axe de rouleau à trouver »** sur une chaîne
parfaitement courbe.

| ce que je supposais | ce que les données disent |
|---|---|
| la sentinelle d'invalidité est `(0,0,0)` | elle vaut **`-1`** — 100 % des sommets passaient pour valides |
| une spire porte un maillage | elle en porte **deux**, `trace/neighbor_out_*` (poussé) et `plat/` (aplati), aux grilles différentes |
| l'axe circonférentiel est le même pour toute la chaîne | **il ne l'est pas** : `spire00` l'a en colonnes, les huit autres en rangées |

⚠ **Mon témoin testait ma propre hypothèse.** C'est le mode de panne le plus discret de ce
dépôt : un contrôle écrit depuis la même croyance que le code ne peut pas la contredire. La
convention est pourtant écrite noir sur blanc par l'outil de vc lui-même, dans la note de son
rapport de self-intersection — *« z <= 0 invalid »*. Il suffisait de la lire.

⚠ Le troisième défaut est le plus coûteux : décider l'axe **une fois** faisait mesurer huit
spires le long du mauvais axe, et rendait des rayons de **312 mètres** sans que rien ne
signale l'erreur. `gen_neighbor` rend une grille transposée par rapport au segment source ;
l'axe se décide donc **par spire**, jamais par chaîne. C'est devenu un témoin : une chaîne
synthétique dont la première nappe est transposée et les suivantes non.

---

## 3. Ce que la mesure rend

| spire | grille | valide | aire utile | arc | tour | hauteur | écart |
|---|---|---:|---:|---:|---:|---:|---:|
| 00 | 149×161 | 58 % | 4,13 cm² | 21,9 mm | 11,5 % | 24,3 mm | — |
| 01 | 158×145 | 54 % | 3,72 cm² | 21,7 mm | 11,7 % | 23,9 mm | 134 µm |
| 02 | 154×141 | 49 % | 3,20 cm² | 21,3 mm | 11,8 % | 23,1 mm | 107 µm |
| 03 | 151×138 | 45 % | 2,78 cm² | 20,0 mm | 11,2 % | 22,3 mm | 100 µm |
| 04 | 148×135 | 40 % | 2,40 cm² | 15,8 mm | 10,7 % | 21,5 mm | 107 µm |
| 05 | 145×132 | 36 % | 2,07 cm² | 10,7 mm | 9,6 % | 20,3 mm | 104 µm |
| 06 | 142×129 | 32 % | 1,74 cm² | 10,3 mm | 9,0 % | 19,1 mm | 113 µm |
| 07 | 137×125 | 27 % | 1,40 cm² | 8,6 mm | 7,7 % | 18,3 mm | 114 µm |
| 08 | 131×119 | 23 % | 1,07 cm² | 8,7 mm | 8,1 % | 17,2 mm | 138 µm |

**Aire utile totale de la chaîne : 22,5 cm² sur neuf nappes.**

---

## 4. ⭐ Le chiffre qui valide la chaîne : 113 µm

L'écart entre deux nappes consécutives est une **distance au plus proche voisin** — aucun
modèle, aucune hypothèse de forme. Médiane **113 µm**, de 100 à 138.

C'est le seul chiffre de tout ce dépôt qui dise que **la chaîne avance d'une nappe à la
fois**. Un pas trop grand sauterait une feuille sans que rien d'autre le signale : la surface
convergerait toujours, elle convergerait juste sur la mauvaise feuille, et les rendus
auraient exactement la même allure. Cette panne-là était invisible jusqu'ici.

Et l'ordre de grandeur est celui qu'on attend d'un papyrus carbonisé d'Herculanum, où les
feuilles sont à une à deux centaines de micromètres l'une de l'autre.

---

## 5. ⚠ Correction d'un chiffre publié : l'érosion est de 15,6 % par tour, pas 4,0 %

[`43`](43_la_chaine_des_spires.md) publie une érosion de **4,0 % par tour**, calculée sur
l'aire de la **grille** — et le disait, dans une note : *« aire de la GRILLE (sommets
invalides compris) — un majorant, pas la surface utile »*. Ce qui manquait, c'est le
**facteur** de ce majorant. Il vaut presque deux au départ, et plus de quatre à la fin :

> **la part de sommets valides tombe de 58 % à 23 %.** La grille se creuse autant qu'elle
> rétrécit, donc une érosion calculée sur l'aire de grille ignore précisément la moitié qui
> disparaît.

Sur l'aire **utile**, l'érosion est de **4,13 → 1,07 cm² en huit tours, soit 74 % au total et
15,6 % par tour** — presque quatre fois le chiffre publié. À ce rythme la moitié de la
surface est perdue en **quatre** tours, pas en douze.

⭐ Et le panneau des rendus le montre sans qu'on ait à croire un nombre : le treillis de
fibres est net sur les trois premières bandes, se fragmente sur les trois suivantes, et la
région valide devient une bande diagonale étroite sur les trois dernières.

![les neuf nappes rendues, couche 15/31](images/43_chaine_pas025_rendus.jpg)

---

## 6. ⚠⚠ Ce que l'outil REFUSE de publier : le rayon

Deux estimateurs indépendants du rayon de la nappe :

1. **géométrique pur** — longueur d'arc divisée par angle balayé : 17 à 30 mm ;
2. **ajustement de cercle** dans le plan perpendiculaire à l'axe : 38 à 43 mm.

Ils se contredisent d'un **facteur deux**, et la cause est mesurable : le résidu
d'ajustement vaut **0,5 mm quand les nappes sont à 0,113 mm l'une de l'autre**. Une nappe de
papyrus gondole dix fois plus que la distance qui sépare deux nappes, donc **un cercle unique
n'est pas un modèle de cette surface**. « Le rayon de la spire » n'est pas une quantité que ce
maillage détermine.

⭐ L'outil le dit et refuse le chiffre, sur **9 nappes sur 9**. Publier l'un des deux aurait
été publier un nombre au hasard, et le panneau de gauche de la figure montre les deux plutôt
qu'une moyenne : *une figure doit montrer l'incertitude qu'elle a, sinon elle en fabrique une
certitude.*

⚠ Ce qui survit, c'est l'**ordre de grandeur** : 2 à 4 cm de rayon, ce qui est bien un
rouleau d'Herculanum. Rien de plus fin.

Le critère de refus est mesuré, pas choisi : sur un cylindre exact ou bruité à trois voxels,
les deux estimateurs s'accordent à moins de 1 % ; sur une nappe **gondolée** synthétiquement
comme les vraies, ils divergent de plus de 40 %. Sans ce dernier contrôle, le drapeau
« indéterminé » n'aurait jamais pu s'allumer, et son refus n'aurait rien voulu dire.

---

## 7. ⭐⭐ Le résultat structurel : une colonne, pas une bande

Chaque fenêtre couvre **environ 10 % d'un tour**. Il en faudrait donc **au moins 8**, côte à
côte, pour fermer **un seul** tour.

⚠ « Au moins » n'est pas une prudence de style, c'est le sens du biais : le gondolement de la
feuille s'ajoute à la flèche, donc l'angle mesuré est un **majorant** de l'angle réellement
balayé, donc le nombre de fenêtres par tour est un **minorant**. La conclusion n'en est que
renforcée.

Et voici pourquoi cela invalide la tâche telle qu'elle était écrite. `gen_neighbor` avance
**radialement** : la spire N+1 est la spire N projetée d'une nappe vers l'extérieur. Les deux
occupent donc la **même fenêtre angulaire**, à 113 µm l'une de l'autre. Or dans un rouleau
déroulé, deux nappes consécutives sont séparées **par une circonférence entière de papyrus**
— celle qu'on ne possède pas. Les recoller bout à bout produirait une bande continue qui
n'existe pas.

> **Il faut deux chaînes orthogonales, et je n'en ai construit qu'une.**
>
> | chaîne | ce qu'elle donne | état |
> |---|---|---|
> | **radiale** (`gen_neighbor`) — traverse les feuilles | une **colonne** : la profondeur, 9 nappes | ✅ faite, [`43`](43_la_chaine_des_spires.md) |
> | **tangentielle** — suit UNE feuille autour du tour | une **bande** : la longueur, un vrai morceau déroulé | ❌ **jamais tentée** |

C'est la chaîne tangentielle qui produirait « un morceau de rouleau déroulé ». Le graal — une
image du rouleau entier — a besoin des deux : la radiale pour la profondeur, la tangentielle
pour la longueur.

### ⚠⚠ Et l'outil n'a AUCUN mode qui la fasse — vérifié dans sa source

Avant de la nommer « prochaine étape », il fallait savoir si `vc_grow_seg_from_seed` sait déjà
le faire. Il ne sait pas :

| mode | ce qu'il fait réellement | utilisable ? |
|---|---|---|
| `gen_neighbor` | projette la surface le long de ses **normales de sommet**, `neighbor_dir` valant `in` ou `out` — **rien d'autre** (`vc_grow_seg_from_seed.cpp:622` et `:684`) | radial seulement |
| `expansion` | ⚠ tire un point **au hasard près du bord** d'un segment existant et **repart en croissance libre** depuis ce germe (`:392`) | non : c'est `mode: seed` déguisé, et les 17 essais en croissance libre sont tous à α ≈ 1 |
| `resume` | reprend une surface et la laisse repousser | non : §6 de [`43`](43_la_chaine_des_spires.md) — la liberté revient, et la dérive avec (+1,46 au 3ᵉ tour) |

⚠ `expansion` a en prime un défaut qui l'exclut d'une chaîne reproductible : son générateur
est semé par l'horloge, `std::default_random_engine rng(clock())`. Deux exécutions du même
appel ne donnent pas le même monde — et le prix demande explicitement une pipeline
*entièrement automatisée* et rejouable.

> **Il faut donc écrire quelque chose, et le principe à réutiliser est celui qui marche** :
> ne pas faire *croître* une surface, en **projeter** une — mais le long de la **tangente**
> de la nappe au lieu de sa normale.

⭐ Une pièce existe déjà pour ça : `analysis/src/suivre_nappe.py`
([`41`](41_marcher_le_long_dune_nappe.md)) marche le long d'une nappe et calcule justement la
tangente latérale par `cross(n, t)` — c'est ainsi qu'il émet ses « côtes ». Ce qu'il produit
est une liste de points 3D, c'est-à-dire exactement le format que `--correct` consomme.

### ⏳ Et la question la moins chère n'avait jamais été posée

Avant d'écrire un mécanisme, il fallait vérifier ce que `resume` fait déjà — c'est le seul des
trois modes qui étende une surface le long d'elle-même. La campagne `spires_repousse` de
[`43`](43_la_chaine_des_spires.md) §6 l'a fait, **avec `resume_generations = 20` et cette
valeur seule** :

| | aire | α |
|---|---:|---:|
| source (segment officiel) | 7,12 cm² | +0,000 |
| après 20 générations de repousse | **12,54 cm²** | **+0,422** |

⭐ Donc `resume` étend **réellement** — +76 % d'aire — et il dérive **dès le premier coup**.
Mais rien n'est su de ce qui se passe **entre 1 et 20 générations**, et c'est là que la
question se joue : s'il existe un régime où la surface gagne de l'aire en restant convergée,
la chaîne tangentielle est possible.

`tools/etendre_nappe.sh` balaie `resume_generations` sur **la même** surface convergente, à
conception appariée (même source, même aplatissement, mêmes fenêtres, une seule variable).
Il **refuse** de partir d'une source dont le verdict écrit n'est pas « converge » — étendre
une surface posée en travers de l'empilement ne mesure rien — et les trois chemins de refus
sont testés. Campagne lancée sur 1, 3 et 10 générations ; le point à 20 n'est pas refait,
il est déjà mesuré.

### ⭐⭐ Premier résultat : étendre le segment officiel triple sa surface utile

Une seule exécution de `mode: resume` sur le segment officiel qui converge :

| | grille | sommets valides | **aire utile** | **arc** | % d'un tour | rayon |
|---|---|---:|---:|---:|---:|---|
| source officielle | 162×149 | 59 % | **4,28 cm²** | 21,9 mm | 11,5 % | indéterminé |
| après extension | 219×206 | ⭐ **96 %** | ⭐ **12,97 cm²** | ⭐ **37,2 mm** | **15,4 %** | indéterminé |

Et le verdict : **α = +0,000, converge**, 0 auto-intersection.

⚠⚠ **Mesuré avant que le traçage soit rendu reproductible** : ce n'était qu'un des trois
tirages, dont un donnait +0,422. Le résultat a été **refait sous graine** et il tient —
12,97 cm² d'aire utile à α = +0,000, octet pour octet rejouable. Voir deux sections plus bas.

⭐⭐ **L'extension ne fait pas qu'ajouter de la grille, elle rebouche les trous** : la part de
sommets valides passe de 59 % à 96 %. C'est la première fois dans ce dépôt qu'une surface que
nous produisons **gagne** de la surface — la chaîne radiale, elle, en **perd** 15,6 % par tour.

⚠⚠ **Une revendication retirée** : j'avais écrit que le rayon devenait **déterminé** sur cette
surface. C'était vrai du tirage non déterministe (40,8 et 47,9 mm, accord à 17 %) et **faux du
run reproductible**, où les deux estimateurs donnent 38,4 et 47,9 mm — soit 25 % d'écart, donc
toujours indéterminé (§6). Étendre la plaque ne suffit pas à résoudre le rayon ; ce que ça
change est l'arc, pas la courbure.

⚠ Ça reste **une** surface, et l'extension va dans **toutes** les directions — la hauteur
monte aussi de 24,4 à 34,2 mm. « Tangentiel » décrit ce que la surface **est**
géométriquement (une nappe s'étend le long d'elle-même), pas une direction qu'on aurait
choisie.

### ⚠⚠⚠ CORRECTION — ce résultat est UN TIRAGE, pas une propriété

Le balayage a fini, et ses trois points se contredisent alors que leurs paramètres effectifs
sont les mêmes :

| réglage (ignoré) | aire | auto-intersections | α |
|---|---:|---:|---:|
| 1 | 12,96 cm² | **0** | **+0,000** converge |
| 3 | 13,01 cm² | **596** | **+0,422** intermédiaire |
| 10 | 12,98 cm² | **0** | **+0,000** converge |

Trois exécutions censées faire la même chose donnent 0, 596 et 0 croisements. Ce n'est pas le
paramètre balayé — il est ignoré, §précédent. **C'est de l'aléa**, et la source le confirme sur
deux points :

1. **Le générateur des perturbations est `thread_local` et, sans graine, semé par
   `std::random_device`** (`GrowPatch.cpp:99-107`). Avec 22 threads OpenMP, ce sont 22
   générateurs irreproductibles. La graine se pose par la variable d'environnement
   **`VC_GROWPATCH_RNG_SEED`** (ligne 83) — pas par une clé de paramètres, et la fonction
   `set_random_perturbation_seed` est marquée `[[maybe_unused]]`, donc jamais appelée.
2. **Le nombre de threads.** L'outil l'écrit lui-même au démarrage : *« tracing does not scale
   past a few threads. Set "thread_limit" in the params JSON (VC3D uses 1) »*. Même avec une
   graine identique partout, l'ordre d'attribution du travail peut varier.

⚠⚠ **Ce que ça fait au résultat ci-dessus** : le ×3 d'aire utile à α = +0,000 est **un tirage
sur trois**, dont deux bons et un mauvais. Ce n'est donc pas « étendre le segment officiel
converge » mais « converge **deux fois sur trois**, sur trois tirages » — ce qui est une
distribution, pas une propriété, et bien plus faible que ce que j'avais écrit.

⚠⚠ **Et ça se propage en arrière** : la campagne `spires_repousse`
([`43`](43_la_chaine_des_spires.md) §6) tournait aussi sans graine et sur 22 threads. Son
+0,422 peut donc être le même mauvais tirage, et non « resume sur une surface projetée
dérive ». **Le contraste source-officielle contre source-projetée que je venais de publier
n'est pas établi.**

⭐ La suite est déterminée par ça, et rien d'autre : `tools/etendre_nappe.sh` pose désormais
`VC_GROWPATCH_RNG_SEED` et `thread_limit: 1`, et sait **répéter un même réglage** — un réglage
qui apparaît deux fois dans la liste reçoit un dossier suffixé, sinon le second écraserait le
premier et le test serait impossible à faire. Le premier run est un **test de déterminisme** :
deux fois exactement la même chose. Tant qu'il n'est pas passé, aucun balayage ne veut dire
quoi que ce soit.

### ⭐⭐⭐ Le correctif est vérifié : deux exécutions identiques donnent le MÊME maillage

Avec `VC_GROWPATCH_RNG_SEED` posée et `thread_limit: 1`, la même commande lancée deux fois
produit un maillage **identique octet pour octet** — 13,024947 cm² d'aire de méta des deux côtés (à ne pas confondre avec l'aire UTILE, 12,97 cm²), à la
sixième décimale. Le traçage par croissance est donc **reproductible**, et il ne l'était pas.

Et le résultat qui survit à la correction :

| | aire utile | arc | auto-intersections | α |
|---|---:|---:|---:|---:|
| source officielle | 4,28 cm² | 21,9 mm | — | +0,000 |
| **extension reproductible** | ⭐ **12,97 cm²** | ⭐ **37,2 mm** | **0** | ⭐ **+0,000** |

⭐ Et un contrôle indépendant de l'identité des deux répétitions : `geometrie_chaine.py` mesure
un **écart de 0 µm** entre elles — la distance au plus proche voisin entre les deux surfaces
est nulle, ce que `cmp` disait déjà sur les octets mais qu'un second instrument confirme.

> **Étendre le segment officiel triple sa surface utile en la laissant sur sa feuille, et
> c'est maintenant rejouable.** Sans la graine, un tirage sur trois donnait +0,422.

⚠⚠ **Ce que ça implique pour tout le dépôt, et c'est plus large que cette page** : *toute*
campagne passée par le chemin de **croissance** était irreproductible — les dix-sept essais en
`mode: seed` de [`42`](42_la_boucle_tourne_et_ne_suffit_pas.md), et la repousse de
[`43`](43_la_chaine_des_spires.md) §6.

- ⭐ Pour les dix-sept essais, ça ne change **rien, et ça renforce même** : dix-sept tirages
  indépendants tous à α ≈ 1 échantillonnent la distribution au lieu de répéter un point. La
  conclusion « `mode: seed` ne pose jamais une surface sur une feuille » en sort plus solide,
  pas moins.
- ⚠ Pour la repousse, ça change tout : son **unique** point à +0,422 est un tirage, donc
  « resume sur une surface projetée dérive » n'est pas établi. À refaire avec la graine.

⭐ La chaîne radiale, elle, n'est pas concernée : `gen_neighbor` n'a aucun aléa (vérifié dans
la source), d'où les maillages identiques au bit entre campagnes constatés plus haut. Le
non-déterminisme est propre au chemin de croissance, et c'est pourquoi il n'avait jamais été
remarqué.

### ⏳ Le budget d'extension scale, et l'outil sait maintenant enchaîner

Le vrai bouton est `generations` (§suivant), et son effet est déjà lisible dans le journal du
traceur avant même le jugement : **`generations = 100` produit 13,0 cm², `generations = 200`
en produit 28,4**. Doubler le budget double à peu près l'étendue. Reste à savoir si α survit —
c'est ce que le balayage en cours mesure.

### ⚠⚠ Et le gros budget NE tient pas — la réponse est nette

| budget | aire | auto-intersections | croisements/cm² | α |
|---:|---:|---:|---:|---:|
| **100** | 12,97 cm² | ⭐ **0** | **0** | ⭐ **+0,000** converge |
| 200 | 28,62 cm² | ⚠⚠ **25 036** | 875 | ⚠⚠ **+1,313** en travers |
| 400 | 78,30 cm² | ⚠⚠ **168 104** | 2147 | *(inutile de juger)* |

Doubler le budget double l'aire **et détruit la convergence**. Les 25 036 auto-intersections
sont le mécanisme rendu visible : une surface qui s'étend trop **se replie sur elle-même**.

> **Donc le chemin vers une grande bande passe par l'enchaînement de petits pas, pas par un
> seul grand.** C'est l'inverse de ce que j'espérais une demi-heure plus tôt, et ça rend la
> capacité d'enchaînement nécessaire au lieu d'être un repli.

⭐ Le point à 400 a été obtenu **gratuitement** : sa croissance était finie quand j'ai arrêté
la campagne devenue sans objet, donc le maillage existait et son compte de croisements ne coûte
aucun rendu.

⭐⭐ **Et ça donne une porte gratuite**, ajoutée à l'outil : refuser de payer les deux rendus
quand les croisements dépassent **100 par cm²** — un ordre de grandeur au-dessus du cas qui
converge (0) et presque un ordre en dessous du premier qui casse (875).
⚠ Ce n'est **pas** un critère de qualité, et [`43`](43_la_chaine_des_spires.md) §4 explique
pourquoi : un compte de croisements est une propriété de l'**échantillonnage** autant que de la
surface — le même maillage décimé passe de 240 à 49. Le plafond ne sert qu'à ne pas brûler
vingt minutes de rendu sur une surface manifestement repliée. Une surface sous le plafond
n'est pas déclarée bonne : elle est jugée normalement.

### ⭐⭐ La voir, et découvrir que α cache une minorité

![une nappe étendue le long d'elle-même](images/44_extension.jpg)

À gauche le segment officiel de départ, à droite la même nappe après une extension, **à
l'échelle relative vraie**. Les trous noirs de gauche sont les 41 % de sommets invalides ; à
droite ils sont rebouchés, et le treillis de fibres continue sur une surface bien plus large.

⚠⚠ **Mais la périphérie de droite n'a pas la même texture que son cœur** : le haut-droite, le
bas et le bord gauche montrent des laminations tourbillonnantes, qui sont exactement ce à quoi
[`38`](38_ce_qui_bouge_avec_la_fenetre.md) dit que ressemble une surface posée *en travers* de
l'empilement. Regarder l'image a donc posé une question que le verdict ne posait pas — et
l'instrument pour y répondre existait déjà, calculé pour chaque surface :

| surface | pic **au bord** | fenêtres plates | écart médian |
|---|---:|---:|---:|
| source officielle | **0,000** | 0,000 | 17,3 µm |
| **extension budget 100** | **0,091** | 0,083 | ⭐ **17,3 µm** |
| extension budget 200 *(cassée)* | 0,305 | 0,464 | 73,4 µm |
| spire radiale qui casse | 0,250 | 0,000 | 77,8 µm |

⭐ **L'écart médian de l'extension est 17,3 µm — exactement celui du segment officiel.** Le
gros de la surface est donc aussi bien posé que la référence, ce qui est plus fort que ce que
α seul disait.

⚠⚠ **Et 9,1 % de ses fenêtres ont leur pic AU BORD**, contre 0,0 % pour la source : environ un
dixième de l'extension n'a aucune feuille à portée. C'est la périphérie qu'on voit tourbillonner
sur l'image, et **α ne le montre pas** — parce qu'il est calculé sur une **médiane**, et qu'une
médiane est insensible à une minorité.

> **α cache une minorité mauvaise.** C'est une limite de l'instrument, pas de cette surface :
> tout verdict α de ce dépôt en hérite. Le complément est `au_bord_relief`, qui est déjà
> calculé partout et qu'il suffit de lire à côté.

⭐ Conséquence pratique pour l'enchaînement, et c'est une prédiction que la chaîne en cours
teste : si chaque pas ajoute ~9 % de périphérie mauvaise, l'enchaînement la **compose**.

### ⚠⚠ « Enchaîner à budget constant » n'existe pas — le budget est CUMULATIF

Première chaîne lancée, quatre pas au budget 100. Le deuxième pas rend **exactement la même
aire que le premier** — 13,02 cm², 0 croisement, α = +0,000. Il n'a rien ajouté.

Le journal du traceur le dit en toutes lettres :

```
GrowPatch work grid 271x258 (resume=219x206, extra_cols=1, extra_rows=1, …)
Resuming from generation 99 with 43430 points.
```

Un `resume` **reprend le compteur de générations de la surface reprise** et s'arrête dès que
`generation >= stop_gen` (`GrowPatch.cpp:4680`). La surface étendue est déjà à la génération
99 ; avec `generations: 100`, il ne reste **qu'une** génération à faire, et une génération sur
une grille de 219×206 n'ajoute rien de mesurable.

⭐ **Donc « enchaîner à budget constant » n'est pas une opération.** Ce qui existe, c'est
atteindre un budget total **en plusieurs séances**, chacune relançant l'optimisation globale.
Le pas *I* doit viser *I × G*.

⭐⭐ **Et ça rend la question de la chaîne beaucoup plus nette qu'elle ne l'était** :

> Atteindre le budget 200 **en deux fois 100** vaut-il mieux que l'atteindre **d'un coup** —
> ce qui a été mesuré à α = +1,313, 25 036 auto-intersections ?

Même budget final, deux chemins. Si le passage par une étape intermédiaire — qui relance
l'optimisation depuis une surface convergente — suffit à garder la nappe sur sa feuille, alors
la bande peut grandir par paliers. Sinon, l'extension a une taille maximale et il faudra
autre chose.

⚠ La première chaîne a été arrêtée dès le diagnostic : continuer aurait fait deux pas de plus
à une génération chacun, c'est-à-dire quarante minutes de rendu pour rien.

### ⚠ Une mesure tentée et écartée : « l'extension reste-t-elle mince ? »

La question est bonne — une nappe étendue *le long d'elle-même* doit rester mince
radialement ; si elle avalait des feuilles voisines, ce serait autre chose qu'une extension.
J'ai essayé de la mesurer par l'étalement des points autour du cercle ajusté :

| | étalement radial (5–95 %) | en écarts entre nappes |
|---|---:|---:|
| source officielle | 1389 µm | **12,3** |
| extension budget 100 | 3572 µm | 31,6 |
| extension budget 200 | 5311 µm | 47,0 |

⚠⚠ **La première ligne réfute l'instrument.** La source est un segment officiel qui converge
parfaitement, et elle affiche déjà douze écarts entre nappes d'« épaisseur ». Ce que cette
mesure capte n'est pas l'épaisseur mais l'**écart à la circularité** — la nappe n'est pas un
arc de cercle, elle ondule (§6), et cette ondulation domine.

⭐ **Et la bonne mesure existe déjà** : une surface qui se replie sur elle-même, c'est
exactement ce que `vc_tifxyz_selfcross` détecte. Elle donne **0** auto-intersection au budget
100 et **25 036** au budget 200. La question était donc déjà répondue, et la réponse est que
l'extension reste bien une nappe simple tant que le budget tient.

⚠ La mesure est consignée ici plutôt que supprimée : quelqu'un d'autre — ou moi dans deux
jours — aurait essayé le même contournement, et savoir *pourquoi* il ne marche pas coûte moins
cher que de le refaire.

### Deux façons d'obtenir une grande bande, et une seule reste

| | ce que ça fait | verdict |
|---|---|---|
| un seul pas, gros budget | une surface étendue d'un coup | ⚠⚠ **écarté** — mesuré ci-dessus, α = +1,313 dès le double du budget |
| **enchaîner des petits pas** | chaque pas repart de l'étendue précédente | ⏳ **la seule piste restante** ; risque connu : ça **compose** les erreurs, comme la chaîne radiale qui casse au bout de six à huit tours | `tools/etendre_nappe.sh`
sait désormais faire les deux, et la distinction est écrite dans son en-tête parce que
mélanger les deux ferait varier deux choses par pas :

- **balayage** (défaut) : chaque réglage repart de **la même** source — conception appariée,
  donc on mesure ce que le réglage fait et rien d'autre ;
- **enchaînement** (`ENCHAINER=N`) : chaque pas repart de l'extension précédente, et le
  script **s'arrête** dès qu'un pas ne converge pas, parce qu'enchaîner depuis une surface
  posée en travers ne mesurerait plus rien. Un seul budget est utilisé en enchaînement, pour
  la même raison.

### ⚠⚠ Et le paramètre que je balayais n'est lu par personne

Le balayage devait porter sur `resume_generations`. En vérifiant pourquoi 1 et 3 générations
donnaient la même grille, le journal a répondu : **« gen 96, 97, 98, 99 »**. Les deux runs
avaient fait une centaine de générations.

La source explique pourquoi. Dans `GrowPatch.cpp`, `resume_generations` n'est **jamais** une
clé de paramètres : c'est une variable locale, le canal de générations par sommet de la
surface reprise (lignes 3493 et 3579). Ce que le traceur lit est
`params.value("generations", 100)` (ligne 3428). La clé que la ligne de commande de l'outil
écrit (`--resume-generations`, app ligne 308) **n'est relue par personne** — un paramètre mort
qui a l'air vivant : il apparaît dans l'aide, dans le méta du maillage, et dans nos scripts de
campagne.

⭐⭐ **Ce que ça change, et c'est en faveur du résultat** : la campagne `spires_repousse`
portait `resume_generations: 20` et a donc tourné, elle aussi, à 100 générations. La
différence entre ses +0,422 et les +0,000 ci-dessus **ne peut pas** venir du nombre de
générations. Elle vient de la **source** — une surface projetée dans un cas, le segment
officiel dans l'autre. Le confondant que je voulais retirer par le balayage se trouve retiré
par le fait que le paramètre est inerte.

⭐ Le vrai bouton est `generations` : il fixe `stop_gen`, donc à la fois quand la croissance
s'arrête **et** la taille de la grille de travail
(`gen_diff = stop_gen − start_gen → grow_max_extra_cols/rows`, lignes 3510-3515, par-dessus
une marge fixe de 25 cellules de chaque côté). C'est le **budget d'extension**, et le ×3
ci-dessus a été obtenu avec sa valeur par défaut.

⚠ Ce n'est pas pour autant une solution acquise : [`42`](42_la_boucle_tourne_et_ne_suffit_pas.md)
a mesuré que des points de correction **ne réorientent pas ce qui a déjà poussé** (+0,89 au
mieux). La question ouverte est donc précise, et c'est déjà mieux qu'une intention : *un
chemin tangentiel connu d'avance sert-il de contrainte à une surface qui n'a pas encore
poussé, alors qu'il ne corrige pas une surface déjà poussée ?*

---

## 8. ⚠⚠ Le contrôle qui a tué mon hypothèse

La chaîne casse au tour 7, et le tour 7 est aussi celui où l'arc valide s'effondre (21,9 →
8,6 mm) et où les sommets valides tombent à 27 %. L'hypothèse était donc tentante et
testable : **la rupture n'est pas un désalignement, c'est une érosion** — la surface ne part
pas en travers, elle n'a plus assez de matière pour être jugée.

`juge_a_un_rendu.py` a été généralisé pour la tester : trois candidats **gratuits** (érosion,
arc court, aire petite — ils ne coûtent aucun rendu, seulement une lecture du maillage) contre
les deux candidats qui coûtent un rendu.

| candidat | coût | ρ contre α | p | condamnées signalées |
|---|---|---:|---:|---:|
| `au_bord` | 1 rendu | +0,265 | 0,099 | 5/8 |
| `ecart_un_rendu_um` | 1 rendu | +0,327 | 0,039 | 5/8 |
| `erosion` | **0 rendu** | +0,429 | 0,007 | 6/8 |
| `arc_court` | **0 rendu** | +0,442 | 0,005 | 6/8 |
| `aire_petite` | **0 rendu** | +0,460 | 0,003 | 6/8 |
| **`indice` de spire** | **0 rendu** | **+0,530** | **0,001** | **7/8** |

*(n = 40 spires, quatre campagnes. ⚠ Une version antérieure de ce tableau donnait n = 34 et
un seuil de condamnation à 0,75 — voir §8bis : le seuil était **dupliqué** dans le dépôt.)*

⚠⚠ **Le simple numéro de la spire bat tous les candidats**, et signale sept des huit spires
condamnées là où les autres en attrapent six. Tout ce que j'ai mesuré n'est donc qu'un proxy
de la **profondeur dans la chaîne** : l'érosion et α croissent tous deux avec le tour, et
rien dans ces corrélations ne distingue une **cause** d'une **horloge**.

> L'hypothèse « la rupture est une érosion » **n'est pas établie**. Le meilleur prédicteur
> d'un échec de spire est le rang de cette spire, et c'est tout ce qu'on sait.

⭐ Le contrôle était facultatif — j'aurais pu publier ρ = +0,445 avec p = 0,009 et une jolie
conclusion mécanistique. C'est la troisième fois de la journée qu'un contrôle qu'on pouvait
sauter change la conclusion. Un contre-exemple achève de fermer la porte :
`spires_repousse/spire03` a **93 % de sommets valides et un arc de 35,8 mm** — beaucoup plus
de matière que n'importe quelle spire de la chaîne à pas 0,25 — et α = **+1,461**, en travers.
L'érosion n'est donc même pas nécessaire pour casser.

---

## 8bis. ⚠⚠ Un seuil écrit deux fois, et neuf verdicts qui sont des tirages au sort

En construisant le tableau du §8, deux défauts sont apparus dans la façon dont ce dépôt lit
ses propres chaînes. Aucun n'a été trouvé en relisant : c'est une spire de la campagne en
cours qui les a rendus visibles.

**1. Le seuil sur α était écrit DEUX fois, avec deux valeurs.** `test_convergence.py`
tranchait à **0,70** et `juge_a_un_rendu.py` à **0,75** — ce dernier avec un commentaire qui
affirmait reprendre le premier. Le cas qui l'a révélé est réel : `spires_pas0125/spire04`
sort à **α = +0,722**, donc « suit la fenêtre » pour l'un et **pas condamnée** pour l'autre.
Le même tour, deux verdicts opposés, dans le même dépôt. Le seuil est maintenant **importé**,
donc un futur désaccord est inlivrable, et un témoin l'assère.

⚠ Au passage, une constante `SUIT_LA_FENETRE = 1.6` vivait dans `test_convergence.py`,
**définie et utilisée nulle part**, portant le nom d'un verdict que α seul décide — un
lecteur pouvait raisonnablement croire que le verdict venait d'elle. Supprimée : une
constante morte au nom trompeur est une explication fausse posée dans le code.

**2. ⚠⚠ Onze verdicts sur quarante-huit sont des tirages au sort.** [`43`](43_la_chaine_des_spires.md)
écrit noir sur blanc que *« α sur deux fenêtres ne discrimine pas à ±0,2 près »*. Chaque
verdict porte donc désormais sa **marge au seuil** et un drapeau `fragile`, et le recensement est net — **11 verdicts fragiles sur 48** :

| verdict | α | marge au seuil | étiquette |
|---|---:|---:|---|
| `pas025_spire07` | +0,702 | 0,002 | suit la fenêtre |
| `dedans_spire02` | +0,686 | 0,014 | intermédiaire |
| `dedans_spire04` | +0,722 | 0,022 | suit la fenêtre |
| `pas0125_spire04` | +0,722 | 0,022 | suit la fenêtre |
| `pas0125_spire02` | +0,758 | 0,058 | suit la fenêtre |
| `pas0125_spire07` | +0,583 | 0,117 | intermédiaire |
| `pas05_spire06` | +0,583 | 0,117 | intermédiaire |
| `repousse_spire02` | +0,573 | 0,127 | intermédiaire |
| `spire03` | +0,532 | 0,168 | intermédiaire |
| `pas0125_spire05` | +0,532 | 0,168 | intermédiaire |

⭐⭐ **Et la fragilité se répartit très inégalement entre campagnes** — c'est un signal de
qualité que la moyenne des α ne porte pas :

| campagne | verdicts fragiles |
|---|---:|
| pas 0,125 (défauts) | **4 / 11**|
| `in` | 2 / 7 |
| repousse | 1 / 4 |
| portée 0,375 | 2 / 10 |
| pas 1,0 | 1 / 7 |
| pas 0,5 | 1 / 7 |
| pas 0,25 | 1 / 9 |
| portée 0,25 à pas 0,125 | ⭐ **0 / 10**|
| portée 0,25, pic 0,25 | ⭐ **0 / 10**|

La campagne compensée ([`43`](43_la_chaine_des_spires.md) §6quinquies) est la seule dont
**aucun** verdict ne tombe dans la zone d'indécision, là où la même chaîne aux réglages par
défaut en met quatre sur onze. Tenir la portée physique ne fait donc pas seulement baisser les
α : ça rend les verdicts **tranchés**, ce qui est une propriété différente et qu'on ne lit pas
sur une moyenne.

⚠⚠ **La première ligne est la revendication du §6quinquies de [`43`](43_la_chaine_des_spires.md)** :
« la rupture tombe au tour 07 » repose sur un α à **0,002 du seuil** — deux millièmes. Ce n'est
pas une mesure, c'est un lancer de pièce — et je l'avais publié comme un résultat le jour
même. Corrigé là-bas.

⭐ Ce que ça n'invalide pas : les chiffres du §3 au §7 de cette page ne passent par **aucun
seuil**. Un écart entre nappes, une longueur d'arc, une part de sommets valides et une
fraction de tour sont des grandeurs continues mesurées directement. C'est précisément
pourquoi ils survivent à ce genre de correction, et les comptes de verdicts non.

⚠⚠ **Le recensement DÉDOUBLONNE, et ça change le chiffre dans le sens qui compte.** Neuf
campagnes ont écrit **75** verdicts, mais seulement **48** séries distinctes : **27 verdicts** identiques y sont
la même mesure comptée à nouveau. La plus grosse duplication est structurelle — `spire00` est
**le même segment officiel de départ dans les neuf campagnes**, donc son verdict apparaît neuf
fois. S'y ajoutent les tours qui sortent identiques quand deux réglages ont la même portée
effective, jusqu'à deux campagnes entières identiques **octet pour octet**
(`spike_window` étant inerte, cf. [`43`](43_la_chaine_des_spires.md)).

⭐ Compter 75 aurait **sous-estimé** la fragilité : 12/75 = 16 %, alors que le taux réel est
**11/48 = 23 %**, presque un quart. Un dénominateur gonflé par des doublons dilue le problème
qu'il est censé mesurer. La clé de déduplication est la **série** elle-même — la donnée — et
non le nom du dossier, parce que deux séries égales sont le même verdict quel que soit le
dossier qui les porte.

⚠⚠ **Ce total vieillit à chaque campagne**, et le garde-fou de `verifier_chiffres.py` l'a
attrapé périmé **quatre fois le 2026-08-21** — chaque fois dans les minutes qui suivaient la
fin d'une campagne. Le défaut n'était pas le chiffre mais le fait qu'il était recopié dans
trois documents : il n'est donc plus écrit qu'**ici**, et les deux autres renvoient à cette
section au lieu de le répéter. Il se recalcule par
`test_convergence.py --depuis docs/spire_*.json`.

⚠ Et `--depuis` **recalcule** désormais chaque verdict depuis sa série au lieu de faire
confiance au champ stocké, en signalant tout verdict périmé. Un verdict écrit hier a été
rendu par les seuils d'hier ; la série, elle, est une donnée et ne peut pas être périmée.

---

## 9. Ce que cette page ne dit pas

- **Pas où est l'axe du rouleau à 1 % près.** L'axe rendu est la normale médiane de plans
  ajustés sur des lignes gondolées ; il sert à définir un plan de projection, pas à localiser
  le rouleau.
- **Pas le rayon d'une nappe.** Explicitement refusé, §6.
- **Pas que la chaîne suit la BONNE feuille.** L'écart de 113 µm dit qu'elle avance d'une
  nappe à la fois ; il ne dit pas que cette nappe est celle qui prolonge le texte. Cela
  demande de l'encre, et l'encre est la tâche ouverte de [`43`](43_la_chaine_des_spires.md).
- **Pas que la chaîne tangentielle marchera.** Elle n'a pas été tentée. Ce qui est établi,
  c'est qu'elle est nécessaire.

---

## Reproduire

```bash
# La géométrie de n'importe quelle campagne d'enchaînement
cd inference && uv run python ../analysis/src/geometrie_chaine.py ../data/spires_pas025 \
  --voxel-um 8.64 --json ../docs/geometrie_pas025.json \
  --figure ../docs/images/44_geometrie_chaine.png

# Les témoins de l'instrument, hors ligne (39 contrôles)
uv run python ../analysis/src/geometrie_chaine.py --verifier

# Le contrôle par l'indice de spire — celui qui tue l'hypothèse de §8
uv run python ../analysis/src/juge_a_un_rendu.py --racine ../data \
  --json ../docs/juge_a_un_rendu.json

# Le panneau des rendus : une couche par spire, puis la mosaïque
uv run python ../analysis/src/couche_de_rendu.py ../data/spires_pas025/spire0*/rendu_31 \
  --dossier-sortie ../data/mosaique/pas025 --index ../data/mosaique/pas025/index.tsv
uv run python ../analysis/src/assembler_mosaique.py ../data/mosaique/pas025/index.tsv \
  --sortie ../docs/images/43_chaine_pas025_rendus.jpg --colonnes 3 --um-par-px 8.64 \
  --rouleau "PHerc0172 — chaîne à pas de rayon 0,25" \
  --legende "nos surfaces, chaîne gen_neighbor pas 0,25 — couche 15/31"
```
