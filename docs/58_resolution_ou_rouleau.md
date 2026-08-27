# 58 — Résolution ou rouleau : le mot en cachait deux, et elles ne s'additionnent pas

> ⚠⚠ **Ce document ferme une moitié de M1ter et nomme précisément l'autre.**
> [`36`](36_lorigine_de_la_pile.md) §5bis a répondu « non » à *l'encre est-elle lisible à
> 9 µm ?* — sur `PHerc1447` le modèle du Grand Prize 2023 sort une constante, σ **45 fois**
> plus petit que là où il marche. Mais la mesure laissait **trois causes** en lice, et
> [`29`](29_ce_qui_reste.md) les porte encore : la résolution, ce rouleau-ci, ou un papyrus
> vierge. [`46`](46_le_temoin_negatif.md) §3 a fermé la troisième. Celui-ci attaque la
> première, sur le rouleau où le modèle **marche**.

## 1. ⚠⚠ Le mot « résolution » cachait DEUX grandeurs

C'est la moitié du travail que de les séparer, et la comparaison publiée les faisait varier
**ensemble** — donc elle ne pouvait pas dire laquelle joue :

| | Scroll 1, 2,4 µm | `PHerc1447`, 8,64 µm | rapport |
|---|---:|---:|---:|
| ce qu'une tuile de 64 px couvre | 154 µm | 553 µm | **3,6** |
| ce que 26 couches couvrent en profondeur | 62 µm | 225 µm | **3,6** |

Le rapport est le même parce qu'il n'y a qu'un seul réglage derrière : **la taille du
voxel**. Un scan plus grossier bouge les deux boutons d'un coup, et c'est exactement
pourquoi personne ne les avait vus comme deux.

⚠ La dernière ligne du §5bis de `36` le disait déjà — *« quatre fois plus d'épaisseur pour
la même fenêtre. Ce n'est peut-être pas gratuit, et c'est à mesurer avant de bâtir
dessus »* — et personne ne l'avait mesuré.

## 2. La méthode : redonner à un rouleau qui marche les conditions d'un rouleau qui ne marche pas

On ne peut pas rendre `PHerc1447` plus fin. On peut rendre Scroll 1 plus grossier.

⭐ **Le grossissement est une MOYENNE de bloc, jamais une décimation.** Un détecteur plus
grossier intègre sur sa cellule ; prendre un pixel sur *f* en jetant les autres ajoute un
repliement qu'aucun scan réel ne porte, donc ferait paraître la dégradation pire qu'elle
n'est et prouverait autre chose que ce qu'on demande.

⭐ **L'étendue de papyrus est identique à chaque barreau.** La fenêtre native fait
1008 × 1008 et c'est l'**entrée du modèle** qui rétrécit — 1008, 504, 336, 252 — jamais la
région lue. Deux barreaux qui liraient deux régions compareraient deux endroits.

⚠⚠ **Et le contrôle sans lequel l'échelle ne veut rien dire.** Moyenner réduit la variance
par construction : une carte plus grossière a un σ plus petit même si le modèle n'a rien
perdu. Chaque barreau est donc lu contre son **σ attendu** — celui qu'on obtient en
moyennant la carte du barreau natif par le même facteur, les pixels non couverts écartés et
non comptés comme des zéros. Le rapport mesuré / attendu sépare *« le modèle a perdu
l'encre »* de *« les pixels sont plus gros »*.

⚠ La fenêtre est choisie sur la carte d'encre **publiée** du même segment, comme celle des
1008 × 1008 où elle varie le plus (σ = 1,5036, `top=10080 left=2520`). Le choix ne favorise
aucun barreau — tous lisent la même — il garantit seulement que l'échelle a quelque chose à
perdre. C'est aussi pourquoi le σ natif d'ici (**1,5202**) vaut le double du σ publié sur le
segment entier (0,7712) : une fenêtre choisie pour son encre varie plus que la moyenne d'un
segment.

## 3. ⭐ Axe « en plan » : contributif, et très loin de suffire

Scroll 1, segment `20230909121925`, profondeur maintenue à 62,4 µm à chaque barreau.

| | tuile de 64 px | entrée | **σ** | σ attendu | mesuré / attendu |
|---|---:|---:|---:|---:|---:|
| 2,40 µm (natif) | 154 µm | 1008 px | 1,5202 | 1,5202 | 1,000 |
| 4,80 µm | 307 µm | 504 px | 1,4352 | 1,5194 | **0,945** |
| 7,20 µm | 461 µm | 336 px | 0,9200 | 1,5195 | **0,605** |
| 9,60 µm | 614 µm | 252 px | 0,4118 | 1,5176 | **0,271** |

⭐ **Le moyennage n'explique rien.** Le σ attendu passe de 1,5202 à 1,5176 — **0,17 %** —
parce qu'une carte d'encre est lisse à l'échelle du pixel (la sortie 4 × 4 du modèle est
remontée en 64 × 64 par interpolation, puis cumulée). La chute mesurée est de **72,9 %**.
Ce n'est donc pas un artefact de pooling : le modèle perd réellement l'encre.

⭐⭐ **Et pourtant l'échantillonnage en plan ne suffit pas.** À **9,60 µm**, soit *plus
grossier* que les 8,64 µm de `PHerc1447`, Scroll 1 rend encore σ = **0,4118**, c'est-à-dire
**24,1 fois** le σ mesuré là-bas (0,0171). Rapporté à ce que chaque mesure a de natif —
0,271 ici contre 0,0221 pour `PHerc1447` face à son propre témoin — l'écart reste de
**12,2 fois**.

⚠ La falaise est entre **4,80 et 7,20 µm** : le premier doublement coûte 5,5 %, le suivant
39,5 %, le troisième 72,9 %. Les rouleaux du prix sont à **7,91 et 8,64 µm**, donc déjà
dessus.

## 4. ⭐⭐ Axe « profondeur » : huit fois plus coûteux, à facteur égal

⚠ Il faut un autre objet : atteindre 225 µm sur Scroll 1 demanderait **94 couches** à
2,4 µm, et ce segment n'en publie que 26. `scroll4_20231111135340` en publie **65** à
2,399 µm, ce qui permet un pas de couches de 1 ou de 2 — 62,4 µm contre 124,8 µm. Le modèle
y répond (σ = 0,8258, du même ordre que le témoin publié).

⭐ **Chaque barreau est CENTRÉ sur la même couche**, jamais aligné sur son bord : à départ
fixe, deux pas partagent leur bord proche et le barreau épais irait chercher sa matière
ailleurs dans l'empilement — on comparerait deux régions de la feuille plutôt que deux
épaisseurs de la même. C'est la contrepartie exacte, en profondeur, de l'étendue commune du
§3.

Les quatre combinaisons, même fenêtre, même centre, même segment :

| en plan | en profondeur | **σ** | rapport au natif |
|---:|---:|---:|---:|
| 2,40 µm | 62,4 µm | 0,8258 | 1,000 |
| 4,80 µm | 62,4 µm | 0,8232 | **0,997** |
| 2,40 µm | 124,8 µm | 0,4887 | **0,592** |
| 4,80 µm | 124,8 µm | 0,4078 | **0,494** |

⭐ **À facteur égal, doubler la profondeur coûte 40,8 % et doubler le plan coûte 0,3 %.**
La grandeur que personne n'avait isolée est de loin la plus destructrice des deux.

## 5. ⭐⭐ Et elles ne s'additionnent pas : elles s'aggravent

La prédiction d'indépendance était écrite avant de lancer le quatrième barreau :
0,997 × 0,592 = **0,590**. Le mesuré est **0,494**, soit **1,195 fois pire** que ce que
l'indépendance annonce.

⭐⭐ **Dit autrement : doubler l'échantillonnage en plan coûte 0,32 % quand la fenêtre de
profondeur est juste, et 16,6 % quand elle est déjà doublée — cinquante fois plus.** Un
grossissement en plan est presque gratuit tant que le modèle voit la bonne épaisseur, et
devient cher dès qu'il ne la voit plus.

⚠ C'est la raison structurelle pour laquelle les deux causes n'étaient pas séparables par
l'observation : elles ne viennent pas seulement du même réglage, elles **interagissent**.
Aucune lecture d'un σ isolé ne pouvait le montrer.

## 6. Ce que ça ferme, et ce que ça laisse ouvert

| | verdict |
|---|---|
| papyrus vierge | ✅ fermé avant ce document, par [`46`](46_le_temoin_negatif.md) §3 |
| échantillonnage **en plan** seul | ✅ **contributif, insuffisant** — 72,9 % de σ perdu à 9,60 µm, et il reste 12 à 24 fois trop de réponse pour ressembler à `PHerc1447` |
| épaisseur de la **fenêtre de profondeur** | ⭐ **mesurée à ×2** : 40,8 % de perte, huit fois le coût du plan, et elle **aggrave** l'autre |
| les deux à ×3,6, comme sur `PHerc1447` | ⏳ **non mesurable ici** : il faudrait un segment publiant ~94 couches à ~2,4 µm sur un objet où le modèle répond, et aucun des trois du dépôt ne le fait |
| **ce rouleau-ci** | ⏳ toujours en lice, et c'est ce qui reste après les deux lignes ci-dessus |

⚠ **Ce que ce document n'établit pas**, quel que soit le résultat : qu'il y ait ou non de
l'encre sur `PHerc1447`. Il dit ce que l'instrument perd quand on lui donne les conditions
de là-bas, pas ce qu'il y a à voir.

⚠ Et une borne sur l'émulation elle-même : elle **conserve le détail en profondeur** qu'un
vrai scan à 9,60 µm n'aurait pas, puisqu'un voxel plus large intègre aussi dans cette
direction. Les σ du §3 sont donc un **majorant** de ce qu'un vrai scan grossier rendrait —
ce qui est précisément pourquoi la conclusion du §3 est énoncée sur l'axe en plan **seul**,
et pourquoi le §5 existe.

## 7. ⚠⚠ Le détour qui a rendu tout ça possible : l'outil ne tournait plus

Cette mesure a commencé par ne pas pouvoir démarrer. `src/xpu/infer_ink.py` porte les poids
dans `data/models/`, valide ses arguments, puis mourait sur un `ModuleNotFoundError` nu :
`torch`, `transformers` et `timesformer_pytorch` n'étaient **dans aucun groupe de
dépendances**. Trois faits sont sortis de la réparation, et chacun n'est apparu qu'en
exécutant :

1. `timesformer_pytorch` n'apparaît dans **aucun de nos imports** — c'est le code du modèle,
   chargé par `trust_remote_code`, qui le demande. Ne lister que les imports visibles rendait
   un remède qui répare la moitié de la panne.
2. `transformers` doit être **borné sous 5**. La 5.16 exige de tout `PreTrainedModel` un
   attribut `all_tied_weights_keys` que ce modèle, écrit pour 4.46.3 comme son `config.json`
   le déclare, n'a pas : le chargement meurt sur un `AttributeError` **après** avoir installé
   3,8 Gio.
3. L'index de roues par défaut tire **2,7 Gio de runtime CUDA** à côté de 1,1 Gio de torch,
   sur une machine sans périphérique CUDA. L'index CPU ramène l'environnement de **4,9 Gio à
   1,2 Gio**.

⚠⚠ Et `uv sync` a **désinstallé 19 paquets** — `zarr`, `fsspec`, `s3fs` et leur suite — que
quatre outils de `src/excision/` importent *à l'intérieur de leurs fonctions*, et qu'aucun
fichier ne déclarait. Ils étaient là parce que quelqu'un les y avait posés à la main. Un
environnement reproductible qui ne survit pas à sa propre commande de synchronisation n'est
pas reproductible, et la panne ne se voit que le jour où on relit un volume.

## 8. ⭐ Deux contrôles de reproductibilité, gratuits et exacts

Les trois campagnes se recouvrent par construction, et les recouvrements doivent coïncider
**au bit près** — ce sont les mêmes couches, la même fenêtre, le même centre :

| | σ |
|---|---:|
| échelle profondeur, pas 1 | 0,825755 |
| échelle croisée `--pas-couches 1`, plan ×1 | 0,825755 |
| échelle profondeur, pas 2 | 0,488698 |
| échelle croisée `--pas-couches 2`, plan ×1 | 0,488698 |

⚠ Ce n'est pas une élégance : deux chemins de code atteignent ces piles — l'un passe par
l'axe profondeur, l'autre par l'option `--pas-couches` de l'axe plan — et un désaccord au
dernier chiffre aurait dit que l'un des deux ne lit pas les couches qu'il annonce.

## Reproduire

```bash
uv sync --extra encre --extra volume      # sans ça, l'outil REFUSE en nommant ce qui manque

# §3 — l'axe en plan, sur le rouleau où le modèle marche
uv run python src/encre/resolution_ou_rouleau.py data/layers/20230909121925 \
    --model data/models/timesformer_GP_scroll1 \
    --carte-publiee data/out/ink_segment_complet.npy \
    --sorties data/controle_resolution/plan \
    --json docs/mesures/m1ter_resolution_en_plan.json

# §4 et §5 — la profondeur, puis les deux croisées, sur les 65 couches de Scroll 4
uv run python src/encre/resolution_ou_rouleau.py data/layers/scroll4_20231111135340 \
    --model data/models/timesformer_GP_scroll1 --axe profondeur --facteurs 1,2 \
    --centre-couche 32 --cote 504 --top 2500 --left 8000 \
    --sorties data/controle_resolution/profondeur \
    --json docs/mesures/m1ter_profondeur.json
for PC in 1 2; do
  uv run python src/encre/resolution_ou_rouleau.py data/layers/scroll4_20231111135340 \
      --model data/models/timesformer_GP_scroll1 --axe plan --facteurs 1,2 --pas-couches $PC \
      --centre-couche 32 --cote 504 --top 2500 --left 8000 \
      --sorties data/controle_resolution/croise_pc$PC \
      --json docs/mesures/m1ter_croise_pc$PC.json
done

# Refaire le rapport a partir des seules cartes deja rendues, sans modele ni couche
uv run python src/encre/resolution_ou_rouleau.py --depuis data/controle_resolution/plan
```

⚠ La fenêtre de Scroll 4 (`top=2500 left=8000`) a été trouvée en sondant trois candidats à
`left` 8 000, 20 000 et 32 000 : seule la première rend une étendue franche
(−1,813 à +1,257 contre −1,805 à −1,153). Une échelle posée sur une fenêtre sans encre
mesurerait la platitude de la fenêtre.
