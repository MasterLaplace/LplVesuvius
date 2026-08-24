# 53 — Le témoin positif de notre chaîne de rendu

> ⚠⚠ **Le critère est écrit avant la mesure**, et l'ordre est visible dans l'historique du
> dépôt : ce document a été commité avec sa §3 vide. Un témoin dont on n'a pas dit d'avance
> ce qu'il condamnerait ne condamne jamais rien — il s'explique après coup.

## 1. L'hypothèse que rien n'avait mise à l'épreuve

[`52`](52_calibrer_sur_son_corpus.md) situe nos huit candidats dans le corpus publié de leur
propre rouleau, à la géométrie de ce corpus (128 px × 109 couches) :

| | relief | rang sur 80 |
|---|---:|---|
| corpus publié `Scroll1` | médiane **0,744** | — |
| nos `ps256` | 0,164 – 0,198 | **1** |
| nos `m7` | **0,0000** | **0** |

La lecture naturelle est « nos traces portent peu de structure ». Elle repose sur une
hypothèse, et cette hypothèse n'avait **aucun contrôle** : que *notre* chaîne de rendu
produise des piles comparables à celles que la communauté publie.

Si elle écrase le relief, alors « nos traces sont plates » ne dit rien sur nos traces. C'est
une propriété de notre instrument, et le classement des huit candidats est un artefact.

⚠ C'est exactement le reproche que [`32`](32_educelab_le_papier_fondateur.md) adresse au
papier fondateur : des mesures sans le contrôle négatif qui leur donnerait un sens. Ne pas
faire le nôtre serait le même défaut, chez nous.

## 2. Le contrôle est direct, parce que le format est le même

Le maillage publié d'un segment est un **`tifxyz`** — `meta.json` + `x.tif`/`y.tif`/`z.tif`,
`format: tifxyz`, `scale: 0.05` — c'est-à-dire **exactement** ce que notre aplatissement
produit dans `plat/`. Vérifié sur le segment `20230702185753` de `PHercParis4` :

```
publié :  bbox [[14037, 11637, 29438], [21223, 24400, 73919]]  scale 0.05  grille 2530 × 1820
le nôtre : bbox [[ 9627,  9461, 38722], [11875, 11758, 39341]]  scale 0.05  grille  120 ×  119
```

On peut donc prendre une surface **publiée**, la rendre **avec notre chaîne**, et lire son
relief à la géométrie du corpus. Rien n'est adapté, rien n'est converti : c'est le même
fichier d'entrée que celui que nos outils consomment déjà.

### Pourquoi un découpage

Un segment publié fait 2530 × 1820 points de grille quand nos candidats en font 120 × 119 —
soit **320 fois** l'aire. On ne peut pas rendre ça, et **on ne le voudrait pas** : le relief
dépend de l'étendue lue (exposant −0,830 dans le plan, [`52`](52_calibrer_sur_son_corpus.md)
§1), donc le témoin doit avoir la taille de ce qu'il contrôle.

`analysis/src/decouper_tifxyz.py` découpe des morceaux **à la taille lue dans un candidat**
(`--comme`), plutôt que retapée. Trois refus, chacun payé ailleurs dans ce dépôt :

1. **La bbox est recalculée**, jamais recopiée. Une bbox de segment entier posée sur un
   morceau ferait chercher au moteur une région de volume qui n'a rien à voir avec la
   surface qu'il tient : le rendu réussirait, et serait vide.
2. **Un morceau troué est refusé** — pas « peu troué », *aucun* trou. Un seuil de trous
   tolérés serait un nombre choisi pour que le tirage du jour passe, et on comparerait alors
   le bouchage de trous plutôt que la surface.
3. **`area_vx2` est omis et non recopié** : c'est l'aire du segment entier, et la garder sur
   un morceau serait un chiffre faux dans un fichier qui a l'air juste.

Le choix des morceaux n'a **aucun aléa** : on énumère les positions sans trou sur un pas
régulier, puis on en garde N réparties uniformément dans cette liste. Un tirage aurait
demandé une graine, donc une chose de plus à garder juste pour rejouer.

## 3. Ce qui se décide

⭐ **Écrit avant de mesurer.** Les morceaux publiés, rendus par notre chaîne et relus à
128 px × 109 couches :

- **s'ils reviennent dans la distribution du corpus** (médiane 0,744, et le segment d'origine
  lit **0,7912**) ⇒ notre chaîne est fidèle, et le déficit de nos traces est une propriété de
  **nos traces** ;
- **s'ils reviennent effondrés**, au niveau de nos candidats (0,16 – 0,20) ⇒ c'est **notre
  chaîne** qu'il faut réparer avant de juger quoi que ce soit d'autre, et le classement de
  [`52`](52_calibrer_sur_son_corpus.md) ne veut rien dire.

⚠ Ce que le témoin ne tranchera pas : le morceau publié couvre une fraction du segment, quand
la valeur publiée (0,7912) est lue sur ses 96 fenêtres. Les deux lectures partagent la
**géométrie de fenêtre** — 128 px, 109 couches — mais pas l'aire échantillonnée. Un écart de
quelques dixièmes ne se lira donc pas comme une panne ; un effondrement d'un facteur quatre,
si.

## 4. Un vrai défaut trouvé avant même le premier rendu

⚠⚠ Le garde de taille de `profiler_une_surface.sh` cherchait un rendu de référence avec
`find -path "*rendu*"` — une **sous-chaîne**, n'importe où dans le chemin. Les morceaux du
témoin vivent sous `data/temoin_rendu/`, donc le `find` y a trouvé le `x.tif` du **maillage**
(119 × 120 points de grille) et le garde a refusé **quatre surfaces parfaitement rendables**
en annonçant « ~119 px de côté » — pour des surfaces qui en font 2400.

Un maillage n'est pas un rendu, et la seule chose qui les distingue de façon fiable est le nom
du **dossier** qui les contient. Le motif est désormais un composant de chemin
(`*/rendu/*` ou `*/rendu_*/*`), et la batterie garde **les deux sens** : un maillage sous un
dossier nommé `…rendu` n'est plus pris pour un rendu, un vrai rendu l'est toujours, et
l'ancienne forme, elle, se trompait — la troisième sonde l'affirme, donc revenir en arrière
fait rougir la batterie.

⚠ Au passage, `profiler_une_surface.sh` **jetait** systématiquement la pile rendue. Le cache
doit partir (c'est du volume téléchargé, reconstructible et énorme), mais la pile est le seul
artefact qu'un second lecteur puisse relire à une **autre** géométrie : la jeter oblige à
repayer dix-sept minutes de rendu par morceau pour poser une question différente sur la même
surface. `GARDER_RENDU=1` la conserve ; le défaut reste de la jeter, parce qu'une campagne de
plusieurs fenêtres remplirait le disque en silence à 562 Mo la pile.

⭐ La décision est une **fonction** (`garder_rendu`) et non un test en ligne, pour que la sonde
porte sur le **comportement** et pas sur une orthographe — ce dépôt a payé le matin même une
sonde qui visait un appel écrit en une ligne et laissait passer le même appel écrit sur deux.

## 5. Reproduire

```bash
# le maillage publié du segment que le corpus lit à 0,7912
B=https://vesuvius-challenge-open-data.s3.amazonaws.com
M=$B/PHercParis4/segments/20230702185753/mesh/20230702185753-on-20260411134726-2.4um.tifxyz
mkdir -p data/temoin_rendu/publie_20230702185753
for f in meta.json x.tif y.tif z.tif; do
  curl -s -o data/temoin_rendu/publie_20230702185753/$f $M/$f
done

# des morceaux à la taille de nos candidats, sans aucun trou
uv run --project . python analysis/src/decouper_tifxyz.py \
    data/temoin_rendu/publie_20230702185753 \
    --comme data/paris4_candidats/ps256_c0/plat \
    --dest data/temoin_rendu/morceaux --nombre 4 \
    --json docs/temoin_rendu_morceaux.json

# le témoin : notre chaîne rend une surface publiée, puis on la situe dans son corpus
CORPUS=docs/balayage_scroll1.csv tools/temoin_du_rendu.sh data/temoin_rendu/morceaux/morceau_0*

# les témoins, hors ligne
uv run --project . python analysis/src/decouper_tifxyz.py --verifier
tools/temoin_du_rendu.sh --verifier
tools/profiler_une_surface.sh --verifier
```
