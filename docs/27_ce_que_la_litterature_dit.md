# Ce que la littérature primaire dit — trois papiers lus en entier

2026-08-19. `06` §0 notait **deux** papiers « à lire », depuis le 17 août. Ils ne
l'avaient jamais été. Les voici lus — et il y en avait **trois**.

⚠ Le troisième, et le plus important, n'était nommé nulle part chez nous : *Complete
virtual unwrapping and reading of a rolled Herculaneum papyrus* (arXiv 2606.29085,
27 juin 2026). Il a été trouvé dans la section References de `/2026_open_problems`.
C'est celui qui donne l'impression que le problème est résolu — et c'est aussi celui
qui chiffre pourquoi il ne l'est pas.

⚠⚠ **Première version de ce document : écrite depuis les RÉSUMÉS.** Elle contenait un
chiffre faux (« cible de 4 µm », §1), une citation qui était une paraphrase entre
guillemets, et elle reprenait à son compte une affirmation de `00` que le papier de
Henderson **réfute avec un nombre** (§2). Les trois articles ont depuis été lus
intégralement, corps, tableaux, annexes et données supplémentaires. Le contraste entre
les deux versions est la leçon : **un résumé dit ce qu'un papier revendique, pas ce
qu'il mesure.**

⚠ Les trois sont du **cœur de l'équipe** du concours. Paul Henderson signe les trois,
W. Brent Seales deux, et le troisième est cosigné par Nat Friedman et vingt-quatre
autres. Ce ne sont pas des travaux périphériques.

### Ce qu'ils établissent ensemble, en trois lignes

| | ce qui est démontré | ce qui reste ouvert |
|---|---|---|
| **§3** déroulage complet | **un** rouleau scellé lu de bout en bout | **~25 h d'humain par spire** (~775 h) ; aucun détecteur automatique d'erreur ; aucun taux d'erreur publié |
| **§2** spiral fitting | une nappe unique **garantie** par construction | **3,20 %** de traversées de spire ; la garantie est topologique, pas sémantique |
| **§1** topographie d'encre | l'encre lisible par le seul relief, à 0,34 µm | cible **~1 µm** ; les rouleaux du prix sont à 8,6–9,4 µm ; ne généralise pas encore entre papyrus (0,691 poolé) |

---

## 1. *Ink Detection from Surface Topography of the Herculaneum Papyri*

Angelotti, Nicolardi, Henderson, Seales — arXiv **2603.27698**, 29 mars 2026, publié
dans **Scientific Reports** (DOI `10.1038/s41598-026-58467-1`).
⚠ La version lue ici est le **preprint v1**, dont le champ *Comments* dit encore
« currently under review » : la version de revue peut différer.

**La thèse** : la **morphologie de surface** d'une région écrite porte assez de signal
pour distinguer l'encre du papyrus, **sans contraste d'absorption**. L'encre carbonée
laisse une **empreinte physique** et c'est ça qu'on détecte. ⚠ Pas un simple creux :
les auteurs mesurent que filtrer la seule rugosité **ne sépare pas** l'encre du support,
et concluent à *« a composite signal: surface roughness together with pressure-induced
deformations from ink deposition »*.

**Le matériel, et il faut le dire précisément** : profilomètre optique confocal
Sensofar S lynx 2, **0,34 µm** latéral, **8 nm** vertical, sur **3 papyrus ouverts
mécaniquement** — PHerc. 248 et 250, deux *scorze* découpées dans les années 1750 puis
grattées couche par couche au XIX siècle, et PHerc. 500P2, une pièce détachée.
**16 lettres en 14 échantillons**, régions d'environ **1,5 mm de côté**.

⚠ **Trois biais que le papier assume, et qui bornent ce qu'on peut en tirer** :
les lettres sont *« selected based on visible legibility and minimal physical damage »* ;
les masques de vérité viennent d'une **photographie en fond clair annotée à la main**,
donc l'encre devait être **déjà visible optiquement** — ce papier ne révèle aucune
écriture invisible ; et les surfaces mesurées sont exposées à l'air depuis ~200 ans, ce
que les auteurs signalent eux-mêmes (*« possible effacement on long-exposed opened
fragments »*).

### ⭐⭐ Le chiffre qui compte pour nous : **1 µm de résolution latérale**

⚠⚠ **Correction du 2026-08-19, deuxième passe.** La première version de ce document
annonçait **4 µm**, et ce nombre n'est **nulle part dans le papier**. Il a été écrit
depuis le résumé, sans ouvrir le corps de l'article. Le papier a été lu en entier
depuis, et sa cible est **quatre fois plus fine** — ce qui change la conclusion, pas
seulement le chiffre. Les trois phrases qui la portent, verbatim :

> *« On our dataset, reliable segmentation benefits from lateral sampling on the order
> of **1 µm or finer**. »* (Conclusion)

> *« Only models at or finer than **1.02 µm** exceed the Dice = 0.70 reference
> threshold. »* (légende du tableau 1)

> *« volumetric scans delivering effective isotropic resolution **at or below 1 µm**
> could be sufficient for morphology-based ink detection. »* (Discussion)

Les auteurs dégradent la résolution par moyennage de blocs et mesurent le DICE. Le
tableau 1 donne deux courbes, et **il faut les distinguer** — les confondre est
exactement ce qui produit un chiffre faux :

| taille de pixel | modèle **entraîné à cette résolution** | modèle **entraîné à 0,34 µm**, testé dégradé |
|---:|---:|---:|
| 0,34 µm | **0,890** | **0,899** |
| 0,68 µm | 0,817 | 0,881 |
| **1,02 µm** | **0,754** | 0,758 |
| 1,36 µm | 0,586 | 0,634 |
| 2,04 µm | 0,516 | 0,494 |
| 2,72 µm | 0,478 | 0,235 |
| 3,40 µm | 0,483 | **0,029** |
| 5,44 µm | 0,475 | **0,003** |
| 10,88 µm | 0,467 | **0,007** |

*(DICE médian ; seuil de référence 0,70 ; n = 14.)*

⚠ **Le plateau à ~0,47 de la colonne de gauche n'est pas un succès.** Un modèle
réentraîné à chaque résolution ne descend jamais sous 0,46 — mais il reste sous le
seuil de 0,70 dès 1,36 µm, et un DICE de 0,47 sur une tâche à deux classes est proche
de ce qu'une segmentation dégénérée rapporte. La colonne qui décrit **notre** situation
est celle de droite : un modèle appris sur du fin, appliqué à du grossier. Elle
**s'effondre à zéro** dès 3,40 µm.

⚠ Et la mesure la plus proche de la tomographie est une **troisième** colonne du papier,
non reproduite ici : les auteurs quantifient la hauteur en pas égaux au pixel latéral
pour émuler un voxel isotrope. Le DICE bouge alors d'au plus **0,026**. Autrement dit,
ce n'est pas la quantification verticale qui tue le signal, c'est bien
l'échantillonnage latéral.

⚠⚠ **Et ça se heurte à `16` de plein fouet**, bien plus durement que la première
version ne le disait :

| corpus | résolution | face à la cible de ~1 µm |
|---|---:|---|
| volumes de **surface** Scroll 1 / PHerc0139 / PHerc1667 | **1,129 / 2,399 / 2,400 µm** | ⚠ le plus fin est **au-dessus** de 1,02 µm, de peu ; les autres sont à 2,4 µm |
| **les 13 rouleaux du prix** (volume) | **8,640–9,362 µm** | ❌ **facteur 8,6 à 9,4** — et au-delà du point d'effondrement de 3,40 µm |

> ⭐ **Conséquence pour First Letters** : sur un rouleau du prix, espérer voir l'encre
> *dans le rendu, sans modèle* — ce que le règlement autorise explicitement — n'est pas
> une question de chance. À 9 µm on est **neuf fois** au-dessus de la résolution où
> cette voie fonctionne, et cinq fois au-delà de celle où elle rend zéro. Ça ne ferme
> pas First Letters (leur cible vaut pour la voie **topographique**, pas pour un
> détecteur appris sur du CT, qui exploite autre chose que le microrelief), mais ça dit
> **pourquoi** c'est dur, et ça donne un argument chiffré à qui demanderait un rescan.

⚠ **La transposition au CT est conditionnelle, et les auteurs insistent sur un mot.**
*« **If** volumetric imaging of closed scrolls can deliver comparable **effective**
resolution at the layer surfaces […] then morphology-only detection **becomes
plausible** inside sealed scrolls. We emphasize “effective” rather than nominal pixel
size because point-spread, partial-volume effects, scattering, reconstruction
regularization, and other artifacts can all diminish resolvable detail. »* Un scan
annoncé à 7,91 µm a donc une résolution **effective** moins bonne que 7,91 µm — l'écart
réel est pire que le rapport des nombres nominaux.

⚠ **Ce que le papier ne prétend pas** : *« This trend reflects our dataset and is not
claimed as a universal bound »*, et *« The exact requirement will depend on data
quantity and diversity, signal-to-noise, model architecture, and critically on the
amount and preservation state of ink »*. La cible de 1 µm est une **observation sur 16
lettres de trois papyrus**, pas une loi.

### ⚠⚠ Et le résultat que le résumé ne met pas en avant : ça ne généralise pas encore

Les auteurs font un **leave-one-papyrus-out** à 0,34 µm — entraîner sur deux papyrus,
tester sur le troisième. C'est la question qui décide si la méthode est un outil ou une
démonstration :

| papyrus retiré | n | DICE médian |
|---|---:|---:|
| PHerc. 248 | 5 | 0,757 |
| PHerc. 250 | 5 | 0,817 |
| **PHerc. 500P2** | 4 | **0,475** |
| **tous held-out, moyenne** | **14** | **0,691** |

**La moyenne poolée, 0,691, passe sous le seuil de 0,70 que le papier utilise
lui-même** — et sur un papyrus des trois, le DICE tombe à 0,475, soit ce que donne un
pas latéral de 2 à 10 µm sur un papyrus *déjà vu*. Phrase exacte : *« indicating
heterogeneous cross-manuscript transfer on this dataset »*. Les auteurs bornent
eux-mêmes : *« each papyrus contributes only 4–5 samples; thus, cross-papyrus estimates
are preliminary »*.

> ⭐ **Pour nous, ça change la lecture de la voie topographique.** Elle ne bute pas
> seulement sur la résolution des scans — elle n'a pas encore montré qu'elle transfère
> d'un manuscrit à l'autre, sur des données **quinze fois plus fines** que les nôtres et
> sur des surfaces **déjà lisibles à l'œil**. Ce n'est pas une porte fermée, c'est une
> piste beaucoup plus jeune que son résumé ne le laisse croire.

### ⚠ Ce que ça N'invalide PAS chez nous, et la différence est nette

Notre instrument de profondeur (`12`, `25` §5) et ce papier mesurent **deux choses
différentes**, et il faut le dire avant qu'un lecteur croie à un doublon :

| | leur mesure | la nôtre |
|---|---|---|
| donnée | profilométrie optique, papyrus **ouvert** | volume CT, rouleau **fermé** |
| grandeur | le **relief** de la face écrite | la **distribution de matière le long de la normale** |
| ce qu'elle sert à faire | **détecter l'encre** | juger si la **trace** suit la feuille |
| a besoin d'un modèle appris | oui | **non** |

⚠ Le point de contact réel est leur résultat de dégradation. Phrase exacte du résumé —
la première version de ce document en donnait une **paraphrase entre guillemets**, ce
qui est une faute de citation : *« Diminishing segmentation performance with decreasing
lateral resolution provides insight into the characteristic spatial scales that must be
resolved on our dataset to exploit the morphological signal. »* C'est la même forme que notre **`13` H2** (⚠ pas `12` §H2 : ce document n'a pas de
section H2 — un d′ **baisse** quand on résout plus de structure) et que le balayage de fenêtre de `25` §5. **Deux mesures indépendantes
disent que la résolution décide** — à citer comme convergence, pas comme priorité.

## 2. *Virtually Unrolling the Herculaneum Papyri by Diffeomorphic Spiral Fitting*

Paul Henderson (auteur unique) — arXiv **2512.04927**, 4 décembre 2025, **accepté à
WACV 2026**. Code publié : `github.com/pmh47/spiral-fitting`.

**La thèse** : la **première** méthode descendante qui ajuste automatiquement un modèle
de surface au CT d'un rouleau sévèrement abîmé. On n'essaie pas de tracer la feuille —
on **inverse le processus physique**. Le rouleau était une feuille rectangulaire unique,
enroulée puis déformée ; on cherche donc le couple (spirale idéale, déformation) qui
explique le scan.

### La construction, en trois pièces

1. **La spirale canonique** : spirale d'Archimède extrudée selon z, avec **un seul
   paramètre inconnu** — ω, le taux d'enroulement, qui est lui-même optimisé.
2. **Le difféomorphisme**, composé de trois étages : une affine par tranche en z, un
   **champ de vitesse stationnaire** intégré par 16 pas d'Euler, et un « gap expander »
   qui écarte les spires. ⚠ L'auteur reconnaît que le champ **suffirait seul** ; les
   deux autres existent pour faciliter l'optimisation et baisser la résolution mémoire.
3. **Sept pertes** pondérées, dont deux méritent d'être retenues :
   - la **stratégie en deux temps**, qui est la vraie idée anti-minimum-local. Les
     pertes principales contraignent *la densité et l'orientation* des spires mais
     **pas la phase** — donc le modèle peut librement glisser d'une spire vers
     l'intérieur ou l'extérieur sans être puni, ce qui évite le piège de la
     périodicité. La perte d'alignement exact n'est activée **qu'à mi-parcours**
     (itération 10 000 sur 20 000), une fois la structure globale trouvée ;
   - la **perte de rayon**, qui « déroule » l'accroissement dû à la spirale par un
     terme `−ω·arctan(y/x)` : être sur une spire devient *être à rayon constant*.

⭐ **Et l'aplatissement est gratuit** : θ et z de l'espace canonique **sont** déjà les
coordonnées U et V. Là où la chaîne officielle a besoin d'une étape SLIM séparée, le
modèle la porte dans sa paramétrisation.

### ⚠⚠ La garantie est TOPOLOGIQUE, et ce n'est pas ce que `00` en disait

La propriété est réelle et bien fondée : l'espace des champs de vitesse est **l'algèbre
de Lie qui engendre le groupe de Lie des difféomorphismes**, donc intégrer un champ
lisse produit une transformation bijective, lisse, d'inverse lisse. Un difféomorphisme
ne peut ni déchirer, ni recoller, ni replier. La spirale canonique étant une nappe
unique, son image l'est aussi — *« guaranteed to be manifold and free of
intersections »*.

**Mais elle garantit que la sortie EST une nappe, jamais que c'est LA nappe.** Et
l'auteur mesure l'écart, le nomme, et en donne la cause :

| ce qui est mesuré | valeur |
|---|---:|
| **WJF** — *winding jump fraction*, la fraction de segments de la vérité terrain qui traversent deux spires différentes de la spirale ajustée | **3,20 %** |
| MRWD — écart radial moyen entre la K-ième spire ajustée et la K-ième réelle | 7,64 |
| ChD — distance de chanfrein, vérité terrain → prédiction | 5,29 |
| AD — défaut angulaire moyen (courbure de Gauss intrinsèque, nul si développable) | 0,0568 |
| Str — étirement dans la feuille | 1,239 |

> *« when paths are contradictory due to imperfect U-Net predictions, **the surface
> sometimes wanders between two true windings, instead of committing to one** »*
> — section Limitations.

⭐ **La cause est diagnostiquée et le remède nommé** : les pertes sont en **norme L1**,
et une somme de L1 sur des contraintes contradictoires converge vers la **médiane**,
c'est-à-dire vers un compromis « entre les deux ». Une norme Lᵖ avec p < 1, ou un
lagrangien augmenté, forcerait un régime *winner-takes-all* — un **engagement** sur une
spire. L'auteur le propose comme travail futur et ne l'implémente pas.

⚠ **Aucune configuration testée n'atteint zéro** : toutes les variantes du tableau
d'ablations sont entre **2,77 % et 3,90 %**.

⚠⚠ **Et deux métriques sont en tension directe.** Retirer la contrainte de numéro
d'enroulement **améliore** le WJF (2,77 %, le meilleur du tableau) mais fait exploser le
MRWD de 7,64 à **25,67**. Autrement dit : sans contrainte globale la spirale glisse
localement pour épouser ce qu'elle voit — moins de croisements, mais un rayon
globalement faux. **On ne peut pas optimiser les deux à la fois dans cette
formulation.** C'est le même arbitrage global/local que `00` §2 décrit, mesuré.

### Ce que ça coûte, et ce que ça demande à un humain

| | |
|---|---|
| matériel | une **RTX 3090** |
| durée totale (PHerc. Paris 4) | **19 h**, dont **16 h de post-traitement** des sorties nnUNet et **3 h** d'ajustement |
| intervention humaine | ⭐ **un bit** — le sens d'enroulement, *« easy to observe visually »* |

⚠ **Les « numéros d'enroulement relatifs » ne sont PAS annotés**, contrairement à ce
qu'on pourrait croire : ils sont dérivés automatiquement par lancer de rayons le long
des normales, construction d'un graphe, suppression des nœuds appartenant à un cycle
(*« since these imply a contradiction »*) et vote majoritaire. C'est directement le
point que le §7 de l'article officiel des problèmes ouverts réclame — *« Automating
these procedures will boost scalability by a great extent »*.

⚠ Le travail humain **hérité** n'est pas compté : les trois U-Net viennent de la
communauté, entraînés *« on a tiny fraction of PHerc. Paris 4 »*, et le coût
d'annotation de cette fraction n'est ni chiffré ni discuté.

### La comparaison à ThaumatoAnakalyptor — et le trou qu'elle laisse

C'est *« the only existing work to unroll substantial regions of Herculaneum papyri
fully automatically »*, l'archétype ascendant : fragments de surface extraits d'un nuage
de points, puis recousus par heuristiques.

| métrique | spiral fitting | Thaumato | écart |
|---|---:|---:|---|
| ChD ↓ | **5,29** | 5,59 | −5,4 % |
| AD ↓ | **0,0568** | 0,1567 | −63,8 % |
| Str ↓ | 1,239 (1,031 avec SLIM) | **1,027** | défavorable sans SLIM, nul avec |
| **WJF** | 3,20 % | **non mesuré** | — |
| **MRWD** | 7,64 | **non mesuré** | — |

⚠⚠ **Les deux métriques qui portent tout l'argument théorique ne sont PAS comparables
au concurrent** — *« not those metrics which rely on access to the canonical spiral
representation »*. **Personne n'a donc jamais comparé le taux de saut de spire de deux
méthodes de traçage.** C'est un trou réel dans l'état de l'art.

⚠ Et la comparaison AD est probablement **0,0933 vs 0,1567** et non 0,0568 vs 0,1567 :
le texte dit *« if like [49] we use SLIM »*, donc Thaumato aplatit avec SLIM. À
conditions égales l'avantage tombe de ×2,76 à ×1,68 — réel, moins spectaculaire.

### ⭐⭐ Ce que ce papier dit de NOTRE travail

Trois choses, et elles vont toutes dans le même sens.

1. **Le WJF exige une vérité terrain.** Il est défini *contre* un maillage manuel — celui
   de PHerc. Paris 4, ~30 spires, *« a tour de force manual annotation effort requiring
   hundreds of hours of human input »*. Sur PHerc. 172, qui n'en a pas, **il n'est pas
   mesuré du tout**, et c'est pourtant là que le résultat visuel est le plus
   impressionnant. **Nos instruments — auto-intersection, profondeur — n'ont besoin
   d'aucune vérité terrain.** C'est exactement la différence qui les rend utilisables sur
   les treize rouleaux du prix, dont **aucun** n'a de maillage de référence.
2. **La garantie ne dispense pas du contrôle.** Une méthode dont la sortie est
   *garantie* propre produit quand même 3,2 % de traversées. Un contrôle qui ne
   regarderait que la topologie déclarerait cette sortie parfaite.
3. **Le mode d'échec change de forme, pas de nature.** Ascendant : saut discret,
   fragment, recollage faux. Descendant : dérive lisse. Une méthode qui ne détecterait
   que les auto-intersections verrait le premier et raterait le second — donc `12` et
   `25` §5 ne sont pas redondants avec `03`/`24`, ils couvrent l'autre moitié.

### ⭐⭐ Le code est publié — et il dit trois choses que le papier ne dit pas

`github.com/pmh47/spiral-fitting`, cloné le 2026-08-19 (ajouté à `tools/repos.tsv`, il
manquait). Le README apprend au passage que **le travail a reçu un prix de 30 000 $** du
concours (« Awarding the Amazing Autosegmentation »).

La métrique WJF est `evaluate_wrt_gp`, dans `fit_spiral.py:465`. Sa ligne centrale :

```python
nearest_windings = torch.where(shifted_radius % dr_per_winding > dr_per_winding / 2,
                               outer_winding, inner_winding)
frac_gp_jumping_windings = (nearest_windings[:, 0] != nearest_windings[:, 1])[~crosses_zero].float().mean()
```

Autrement dit : **la fraction des segments de la vérité terrain dont les deux
extrémités n'ont pas la même spire la plus proche**, en excluant ceux qui franchissent
θ = 0. C'est net, c'est honnête — et **ça exige un maillage de référence**, ici celui du
Banner du Grand Prize de Scroll 1.

**Trois réserves sont écrites en commentaire par l'auteur lui-même**, et aucune n'est
dans l'article :

1. ⚠ **La mesure est faite en espace SPIRALE, pas en espace rouleau.**
   > `# TODO: measure the distances in scroll space, to be more accurate where the
   > diffeomorphism has large 2nd derivative`

   Là où la déformation courbe fort — c'est-à-dire exactement dans les régions
   comprimées, celles qui posent problème — la distance mesurée n'est pas la distance
   réelle.

2. ⚠ **La métrique est biaisée par la densité de la solution.**
   > `# This complains if the GP is not parallel with ours, particularly strongly so if
   > ours is dense`

   Un ajustement plus dense est puni davantage, à erreur géométrique égale.

3. ⚠⚠ **Un défaut connu de la vérité terrain, non corrigé.**
   > `# FIXME: this assumes the GP starts at the same papyrus winding-index in all
   > slices -- whereas actually there's a jump at s1350 [...] should be whichever yields
   > better metrics overall`

   Le maillage de référence **saute lui-même d'une spire** à la tranche 1350, et
   l'appariement retenu est celui qui *« rend les meilleures métriques »*.

⚠ Et un mode de panne **silencieux** dans le MRWD : quand l'ajustement s'étire trop —
c'est-à-dire quand il échoue — le tableau des rayons est **complété par répétition de sa
dernière valeur** (`F.pad(..., value=winding_radii[-1])`) au lieu d'être pénalisé. Le
commentaire le dit : *« this means the windings have stretched out excessively »*. Le cas
d'échec est donc partiellement masqué par la mesure censée l'attraper.

> ⭐ **Rien de tout ça n'invalide le travail** — publier son code, avec ses FIXME, est
> précisément ce qui rend ces réserves connaissables. Mais ça change ce qu'on a le droit
> de faire du 3,20 % : c'est **un ordre de grandeur mesuré sous conditions**, pas une
> constante. Et ça renforce le point qui nous concerne : **une métrique qui a besoin
> d'une vérité terrain hérite des défauts de cette vérité terrain.** Les nôtres n'en ont
> pas.

### ⚠ Trois absences du papier, à connaître avant de le citer

- **Les unités de MRWD et ChD ne sont jamais données.** Ni voxels bruts, ni µm. Or
  l'espacement inter-spires de ce rouleau est de l'ordre de 10 à 16 voxels : selon la
  lecture, une erreur de 5,29 vaut **un tiers** ou **plus d'un** interstice. C'est la
  différence entre « lisible » et « illisible », et elle n'est pas décidable à la
  lecture.
- **L'exactitude dans les régions non détectées n'est jamais mesurée.** C'est pourtant
  le bénéfice unique revendiqué (*« passes through missing regions »*, *« interpolated
  correctly »*) — et par construction il n'y a là ni vérité terrain, ni prédiction.
  **Le bénéfice le plus revendiqué est le seul jamais isolé.**
- **Aucun texte n'est transcrit.** Le papier applique un TimeSformer tiers et montre
  *« many letters forming complete words »* — sans transcription, sans décompte de
  caractères, sans validation papyrologique, et sans comparer au texte que le maillage
  manuel de la même région donne déjà.

⚠ Et une idéalisation, posée en introduction puis jamais traitée : la spirale est
d'**épaisseur nulle**, alors que le papyrus est une **bi-couche** dont recto et verso se
sont par endroits séparés — *« sometimes the entire front and back surfaces have
separated over a larger area »*. Quand les deux faces sont écartées, le modèle doit en
choisir une, et **rien dans les pertes ne dit laquelle porte l'encre**.

### ⚠⚠ Ce que ça dit de notre journée

`26` a mesuré que la trajectoire de `vc_grow_seg_from_seed` ne répond ni aux champs de
direction, ni aux grilles de normales, ni à leurs poids — seulement à `step_size` et à
la prédiction. Henderson attaque le **même problème par l'autre bout** : au lieu de
contraindre un traceur ascendant, il impose la continuité **dans le modèle**.

> ⭐ Ce n'est pas une contradiction, c'est la carte du §2 de `00` qui se vérifie : *l'un
> porte une contrainte globale sans souplesse locale, l'autre l'inverse*. Nos trois
> négatifs disent que le second **ne se laisse pas contraindre par ce qu'on lui donne** ;
> le WJF de 3,20 % dit que le premier, même contraint par construction, **traverse
> encore**.

## 3. ⭐⭐ *Complete virtual unwrapping and reading of a rolled Herculaneum papyrus*

Angelotti, Parsons, Nicolardi, Nader, Johnson, Josey, Henderson, Schilling, Rudolph,
McDonald, Dal Prá, Tafforeau, Mirone, Parker, Posma, Kyles, Vergara, Lavorante, Villa,
Robustelli, D'Angelo, Del Mastro, McOsker, Fleischer, Chapman, **Friedman**, **Seales** —
arXiv **2606.29085**, 27 juin 2026. **27 auteurs**, l'équipe entière du concours plus
l'ESRF et quatre universités italiennes.

⚠ **Ce papier ne figurait pas dans `06` §0**, qui n'en nommait que deux. Il a été trouvé
le 2026-08-19 dans la section References de `/2026_open_problems`. C'est **le plus
important des trois** — et c'est celui qui donne l'impression que tout est résolu.

**Le résultat** : **PHerc. 1667**, un rouleau scellé, est **entièrement déroulé
virtuellement et lu**. 31 spires, **1231 cm²** de papyrus, **≈ 860 cm²** de surface
d'écriture préservée, **22 colonnes**, transcrites par **huit papyrologues**. C'est réel,
c'est une première, et ça mérite d'être dit sans réserve.

### ⚠⚠ Mais le mot qui porte le titre est « rolled », pas « complete »

**PHerc. 1667 est le plus petit et le plus abîmé des objets de la campagne**, pas un
rouleau intact :

| | PHerc. 1667 aujourd'hui | un rouleau entier |
|---|---:|---:|
| hauteur | **8 cm** | 19–24 cm |
| diamètre | **2 cm** | 4–6 cm |
| spires | **31** | plusieurs centaines |

Et cet état est le produit de deux siècles de tentatives destructrices — ouverture ratée
au XIX siècle, tentative Fackelmann abandonnée en 1969, méthode d'Oslo dans les années
1980 qui en a tiré dix fragments avant de le classer illisible :

> *« These interventions substantially altered the physical state of the artefact,
> **reducing the diameter of the surviving roll from 4.9 to 2 cm, and its weight from
> 14 g to approximately 6 g** »*

⭐ **« Complete » veut donc dire « tout ce qui survit encore »**, et les auteurs le
définissent honnêtement, dans un sens qu'ils qualifient eux-mêmes de **borné** :

> *« We use “complete virtual unwrapping” in a **bounded geometric sense**: the preserved
> surface included in the claim is **represented by an approved mesh**, can be inspected
> in the CT volume and is rendered in the flattened coordinate domain. »*

⚠ **Et le titre du traité n'est pas récupéré** : il était dans la partie haute, perdue.
*« neither the authorship nor the title of the work can be established with certainty »*.
Ce qu'on sait : un traité d'éthique, contexte stoïcien, mention d'**Aristocréon** (neveu
de Chrysippe), II siècle av. J.-C. Sur 22 colonnes, **4 sont en « traces »** sans une
lettre transcrite, et 2 des 18 restantes n'ont **aucune traduction**.

### ⭐⭐⭐ Le chiffre qui décide de tout : **~25 heures d'annotation MANUELLE par spire**

Il est dans la sous-section la plus discrète du papier, « Statistics and
reproducibility », en **une ligne** :

> *« The unwrapping was completed using the most efficient semi-automated segmentation
> tooling available at the time, a **wrap by wrap copy tool** combined with **~25 hours
> per wrap of manual annotation**. »*

**31 spires × 25 h ≈ 775 heures** — soit ~97 jours-personne, ~4,5 mois à temps plein,
et un débit de **1,6 cm² de papyrus déroulé par heure d'humain**. *(La multiplication est
de nous : le papier donne les deux facteurs et ne fait pas le produit.)*

Et ces 775 heures ne couvrent **que le déroulage**. Elles n'incluent ni la photogrammétrie
et la fabrication des coques, ni l'annotation des labels d'entraînement, ni les cinq tours
de pseudo-labellisation d'encre, ni les 256 voxels cliqués par un expert pour le prototype
DINO, ni la revue par huit papyrologues.

⚠ Le papier crédite d'ailleurs **un poste permanent de direction des annotations**, occupé
sans interruption depuis mai 2023 par deux personnes successives.

> ⭐ **À comparer au Grand Prize 2027, qui tolère 8 heures d'annotation humaine
> documentée.** L'écart est d'un facteur ~100. C'est exactement ce que l'annonce du prix
> dit en une phrase : *« the methods behind these technical breakthroughs still require
> humans in the loop. **Full automation is required.** »*

### ⚠⚠ Et voici ce que ce papier NE fait PAS — c'est notre sujet, mot pour mot

**Le traçage automatique d'une surface complète et correcte n'est pas résolu**, et les
auteurs le nomment comme le **premier des deux goulots dominants** :

> *« Two bottlenecks remain dominant. The first is **geometric**. **Even strong
> surface-prediction networks can fail in highly compressed regions, where mergers, holes
> and sheet switches destabilize surface estimation.** »*

⚠⚠ **« sheet switches » n'apparaît qu'UNE fois dans tout l'article** — dans cette phrase,
comme mode de panne non résolu.

**Il n'y a aucun détecteur automatique d'erreur de traçage.** Le seul rempart est un
humain qui juge à l'écran :

> *« **Regions judged geometrically consistent with a single sheet** were marked with an
> approval mask. »*

C'est ça, l'« approved mesh » du critère de complétude : **une catégorie humaine, pas une
métrique**. Le papier fournit un excellent outillage de *diagnostic* — n'importe quel point
de la surface aplatie renvoie à ses coordonnées 3D, ce qui laisse *« reviewers inspect the
underlying papyrus layer, assess local geometric reliability and **distinguish
surface-placement errors from ink-interpretation errors** »* — mais c'est un **reviewer**
qui regarde.

⚠⚠ **Conséquence directe : le papier ne publie AUCUN taux d'erreur de traçage.** Ni avant
correction, ni après. On ne sait pas combien d'erreurs la chaîne automatique produit, ni
combien la passe manuelle en rattrape.

Le prédicteur de surface lui-même est faible, et le papier le rétrograde explicitement :

| modèle de surface (nnU-Net 3D résiduel, patch 256³) | Dice | IoU |
|---|---:|---:|
| **classe surface** | **0,308** | **0,189** |
| classe fond | 0,883 | 0,801 |
| moyenne | 0,596 | 0,495 |

> *« The resulting voxelwise prediction was used **only as an intermediate cue** for
> geometric tracing. The final surface representation **was not the segmentation volume
> itself**, because dense predictions can contain **local sheet mergers, gaps and false
> positives** in tightly packed regions. »*

⚠ L'entraînement a d'ailleurs été **arrêté à 3 864 epochs sur 7 500 planifiés**, et le
pré-entraînement DINOv2 à **342 558 itérations sur 1 000 000**.

### La généralisation, dite par les auteurs eux-mêmes

> *« **This workflow does not imply that all sealed Herculaneum rolls are automatically
> readable.** Performance depends on scroll general preservation state, scan quality,
> layer separation, deformation, local ink contrast and surface preservation. »*

⚠ **Et les tables disent quelque chose que le corps du texte ne dit pas : ~20 objets ont
été scannés, 3 portent un résultat.** PHerc. Paris 3, 1451, 332, 814, 1299, 841, 1203,
MANB, MANBp, MAN5 sont tous scannés à 2,4 µm et n'apparaissent qu'en « comparison /
training volume ». **Aucun compte rendu d'échec** n'est donné pour ces quinze objets.
C'est un biais de sélection non discuté.

### ⭐ Ce qui EST résolu, et bien : le scan

C'est le morceau le plus solide et le plus reproductible du papier.

| paramètre de production | valeur |
|---|---|
| voxel | **2,4 µm isotrope** |
| distance de propagation | **0,22 m** |
| énergie moyenne | **78 keV** |
| phase retrieval | Paganin, **δ/β = 1000** |
| ligne | **BM18, ESRF** |
| volume reconstruit moyen | **20 To** (jusqu'à > 100 To bruts) |

Le raisonnement physique est la **décohérence** : les couches denses diffusent le
faisceau et brouillent les projections, *« could be linked to the presence of graphite (a
very efficient decoherer) »*. Le remède est contre-intuitif — **réduire** la distance de
propagation et **monter** l'énergie, donc affaiblir volontairement le contraste de phase
jusqu'au point où il aide sans brouiller. La campagne d'optimisation balaie 4×4 énergies ×
distances, et donne des valeurs opérationnelles par taille de pixel : **0,22 m à 2,4 µm,
~0,5 m à 4,6 µm, ~2 m à 8 µm**.

⭐⭐ **Et sur PHerc. Paris 4, ce protocole rend l'encre DIRECTEMENT VISIBLE dans le
volume** — dépôts de **10–20 µm** d'épaisseur apparente, segmentables en 3D sans aucun
modèle conditionné à la surface. Projetés sur la surface aplatie, ils **coïncident avec la
région du Banner du Grand Prize 2023**. C'est une validation physique indépendante de la
lecture de 2023.

⚠ Mais elle est **ponctuelle**, et les auteurs le bornent : *« under **at least one**
optimized scan regime and ink preservation state »*. Elle ne s'étend pas aux rouleaux où
l'encre reste invisible — c'est-à-dire précisément à PHerc. 1667 et 139, où repose le
résultat principal.

⚠ Enfin, une partie de la lecture de PHerc. 1667 **ne vient pas du volume de production** :
un scan complémentaire de région d'intérêt à **1,129 µm** (59 keV) a permis *« the reading
of previously illegible portions of the text »*.

### ⭐⭐ Ce que ce papier dit de NOTRE travail — et c'est la réponse à « tout est déjà fait »

Quatre faits, tirés du papier lui-même :

1. **L'équipe qui vient de lire un rouleau entier n'a aucun détecteur automatique d'erreur
   de traçage.** Son seul rempart est un masque d'approbation posé à la main, région par
   région.
2. **Elle ne publie aucun taux d'erreur de traçage**, ni avant ni après correction. La
   grandeur que nos instruments produisent n'existe nulle part dans la littérature.
3. **Elle nomme le saut de spire comme goulot non résolu**, une fois, dans sa Discussion.
4. **Le coût est de ~25 h/spire**, et le prix suivant en tolère 8 au total. **Un facteur
   ~100 sépare l'état de l'art de ce qui est demandé pour juin 2027.**

⚠ Et la comparaison de résolution est brutale pour les rouleaux du prix : ce papier
travaille à **2,4 µm** (et descend à **1,1 µm** pour les passages difficiles), quand les
treize rouleaux du Grand Prize 2027 sont publiés à **8,64–9,36 µm** — un facteur **3,6 à
3,9** par rapport au volume de production, et **8 à 8,3** par rapport au scan de secours.
C'est le même constat que le §1, par un autre chemin : **la résolution est le premier
mur.**

> ⭐ La conclusion des auteurs est la formulation la plus exacte de l'état du domaine, et
> elle vaut d'être citée entière :
>
> *« The remaining challenge is **not whether** sealed Herculaneum texts can be read
> non-invasively, but **how broadly, robustly and efficiently the workflow can be
> extended** across the still-unopened library. »*

## 4. Ce que la lecture complète des documents a trouvé d'autre

⚠ Un `grep` attrape les marqueurs, pas ce qui a été laissé en passant. Les 8 310 lignes
de `docs/` et de la passation ont donc été lues. Reste ouvert, dans l'ordre de valeur :

| # | quoi | où c'est dit |
|---|---|---|
| **1** ⭐⭐ | **appliquer la correction — un GAUCHISSEMENT — et montrer le gain** | `00` §9.3, `18` J6, `22` R2. C'est le dernier ⏳ du « vrai produire », et le seul obstacle écrit (« la chaîne maillage → rendu n'est pas ici ») **est tombé** : VC3D est construit |
| 2 | ~~extraire les chiffres du papier spiral fitting~~ | ✅ **FAIT** le 2026-08-19, §2 ci-dessus — lecture intégrale, WJF compris |
| 3 | publier la table de qualité de trace, et le dépôt | `22` Q3, `15` §5, `21` |
| 4 | `06` §2.3 « vérifier 1.11 avec le vrai ombilic » | ⚠ **périmé** : `18` M1 l'a clos **sans** l'ombilic, mesuré à 1,75 % contre un cv de 1,8 % |
| 5 | `06` §3bis C « un second rouleau » | ⚠ **périmé** : fait quatre fois (`19` §11) |
| 6 | `06` §3bis D « boucler la métrique sur le résultat » | ⚠ **périmé** : c'est la mesure 3.8, et la réponse est **NON** |

⭐ **Le reste nº 1 est le seul qui vaille un lot.**

⚠ Cette phrase disait « les trois « périmés » sont corrigés **ci-dessous** » — et c'était
la dernière ligne du fichier, donc rien ne suivait. Les corrections sont **dans
`06`** lui-même (§2.3, §3bis C, §3bis D), là où le piège attend son lecteur ; c'est le
renvoi qui était faux, pas le travail.

---

## Références

### Les trois articles primaires

Chacun a été **lu intégralement** le 2026-08-19 — corps, tableaux, légendes, méthodes,
annexes et données supplémentaires — et non depuis son résumé.

| réf | citation | lu |
|---|---|---|
| **[P1]** | G. Angelotti, F. Nicolardi, P. Henderson, W. B. Seales, *« Ink Detection from Surface Topography of the Herculaneum Papyri »*, arXiv:**2603.27698**v1 [cs.CV], 29 mars 2026 · publié dans **Scientific Reports**, DOI `10.1038/s41598-026-58467-1` | v1 (preprint), 9 p., 3 fig., 2 tables |
| **[P2]** | P. Henderson, *« Virtually Unrolling the Herculaneum Papyri by Diffeomorphic Spiral Fitting »*, arXiv:**2512.04927**v1 [cs.CV], 4 déc. 2025 · **accepté à WACV 2026** · code : `github.com/pmh47/spiral-fitting` | v1 intégral, annexes A/B/C comprises |
| **[P3]** | G. Angelotti, S. Parsons, F. Nicolardi, Y. Nader, S. Johnson, D. Josey, P. Henderson, H. Schilling, J. Rudolph, F. McDonald, E. R. Dal Prá, P. Tafforeau, A. Mirone, C. S. Parker, J. P. Posma, B. Kyles, C. Vergara, A. Lavorante, R. Villa, M. C. Robustelli, M. D'Angelo, G. Del Mastro, M. McOsker, K. Fleischer, C. Chapman, N. Friedman, W. B. Seales, *« Complete virtual unwrapping and reading of a rolled Herculaneum papyrus »*, arXiv:**2606.29085**v1 [eess.IV], 27 juin 2026 | v1 intégral, Extended Data et Supplementary Tables 1–5 comprises |

⚠ **Un quatrième**, cité par les trois et par le site, **non lu ici** : S. Parsons,
C. S. Parker, C. Chapman, M. Hayashida, W. B. Seales, *« EduceLab-Scrolls: Verifiable
Recovery of Text from Herculaneum Papyri using X-ray CT »*, arXiv:**2304.02084**, 2023.
C'est le jeu de données sur lequel [P2] travaille et la source des scans à 7,91 µm.
✅ **Lu le 2026-08-19** (v3) → [`32`](32_educelab_le_papier_fondateur.md).

### Pages officielles du concours

Miroir local complet dans `site/scrollprize.org/` (81 pages sur 81), récupéré par
`src/outils/mirror_site.sh`.

| page | ce qu'on en tire | dernière mise à jour affichée |
|---|---|---|
| `/2026_open_problems` | la carte technique de toute la chaîne, le tableau des goulots, les six appels à contribution, et la section References d'où vient [P3] | **10 juillet 2026** |
| `/prizes` | les montants et critères en vigueur (Grand Prize 2027, First Letters ×10, Titre de Paris 4) | — |
| `/unwrapping` | *« the problem is still unsolved. No method so far manages to perfectly fit the wanted surface to the data »* | — |
| `/winners`, `/grandprize`, `/firstscroll` | ce qui a été gagné, et par qui | — |
| `/data`, `/data_browser` | l'inventaire des volumes publiés par rouleau | — |

### Données

- **Bucket AWS Open Data** : `s3://vesuvius-challenge-open-data` — volumes CT en
  OME-Zarr, prédictions de surface, segments, cartes d'encre. C'est la source de
  **toutes** nos mesures à distance ; rien n'est téléchargé en entier.
- **`dl.ash2txt.org`** — le miroir HTTP de la communauté, dont les modèles
  communautaires (`bruniss`) qu'utilise [P2].

### Code

`tools/repos.tsv` porte le manifeste des **44 dépôts** clonés, en quatre niveaux
(0 = cœur officiel, 1 = déroulage/segmentation, 2 = encre, 3 = outillage), avec pour
chacun son URL et, le cas échéant, la raison de le garder alors qu'il est archivé ou
mort en amont. Les trois qui portent le plus de poids ici :

- `ScrollPrize/villa` — le monorepo officiel : VC3D / volume-cartographer (dont les
  outils `vc_*` que nous pilotons), lasagna, spiral fit, neural tracing ;
- `schillij95/ThaumatoAnakalyptor` — l'archétype ascendant, le concurrent de [P2] ;
- `hendrikschilling/volume-cartographer` — le fork d'où vient VC3D.

⚠ **`pmh47/spiral-fitting`, le code de [P2], n'est PAS dans le manifeste.** À ajouter.

### Ce que nos propres mesures utilisent

Toute affirmation chiffrée de ce dépôt renvoie à un script versionné de
`src/`, ou à un artefact de `docs/` ou `artefacts/`. La règle est
énoncée dans `HANDOFF.md` §9 : *un chiffre publié dont le calcul n'est pas dans l'arbre
n'est pas un résultat, c'est une anecdote.* Les batteries de contrôle sont dans
`src/outils/temoins.sh`, et la chaîne complète — tests, builds, boot, parité — dans
`validate.sh`.
