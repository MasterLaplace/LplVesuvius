# La profondeur de surface : un instrument de tracé sans vérité terrain

2026-08-18. Né d'une enquête sur l'échec du détecteur d'encre sur Scroll 4 (`09` §12),
et devenu autre chose que ce qu'il cherchait.

---

## 1. D'où ça vient

Le détecteur GP-2023 lit **26 couches** d'une pile — ici les couches 15 à 40.

⚠ **La convention est vérifiée à la source, pas supposée.** Le tutoriel officiel
(miroir local, `site/scrollprize.org/tutorial_VC.html`) donne la commande qui les
engendre :

```
vc_layers_from_ppm -v "/full_scrolls/$SCROLL" -p "$SEGMENT.ppm"     --output-dir layers/ -r 32 -f tif
```

> *« The result of this process are the 65 tifs in the /layers/ directory, also
> referred to as a "surface volume". »*

**Rayon 32, 65 couches : la couche 32 EST la surface tracée**, et les autres s'en
écartent d'un voxel par indice. Si la trace suit bien la feuille, la surface tombe donc
au même indice partout — au voisinage de 32 — et le modèle la trouve là où il la
cherche. ⚠ Sans cette vérification, tout ce qui suit serait un raisonnement sur une
convention devinée.

La première cause candidate à l'échec sur Scroll 4 était donc : *et si la surface
n'était pas dans la fenêtre lue ?* Elle se teste **sans rien télécharger** — la réponse
est déjà dans les couches qu'on a.

## 2. La mesure

`analysis/src/depth_profile.py`. Pour chaque couche, sur une fenêtre : l'**intensité
moyenne** (où est la matière) et le **contraste local**, écart-type d'un passe-haut 3×3
(où est la *structure*). C'est le second qui localise : il pique là où les fibres et
l'encre sont nettes, c'est-à-dire à la surface.

⚠ **Chaque profil est normalisé dans sa propre pile.** Deux campagnes de scan n'ont ni
la même dynamique ni le même gain ; comparer des niveaux bruts comparerait les
scanners. Ce qui se compare est la **forme** — où est le pic.

⚠ **Les couches sont lues une fois chacune, toutes fenêtres confondues.** Une couche
fait ~500 Mo et se décode entière ; boucler sur les fenêtres à l'extérieur relirait la
pile autant de fois qu'il y a de fenêtres.

⚠ Une fenêtre sans matière n'a pas de surface : celles dont l'intensité maximale reste
sous la moitié du maximum global sont **écartées et comptées**.

## 3. 🎯 Ce qu'on voit

Le segment de Scroll 1 qui donne l'**AUC 0,925**, profil sur une fenêtre : une courbe
**unimodale propre**, pic de contraste à la couche **26**, au milieu de ce qui est lu.
Le même profil sur Scroll 4, à l'endroit exact où l'inférence a tourné : le contraste
est **maximal à la couche 15** — la première lue — et décroît jusqu'à 40. **La surface
est au-dessus de la fenêtre.**

⚠⚠ Et une autre fenêtre du **même** segment Scroll 4 donne son pic à la couche **40**,
l'autre bord. Les deux extrêmes, sur le même segment. C'est ce désaccord qui a
transformé un diagnostic en instrument.

### Le balayage complet — trois segments, même plage de couches

| segment | rouleau | pic dans le **tiers central** | écart interquartile | pic **au bord** |
|---|---|---:|---:|---:|
| `20231022170901` | Scroll 1 | **63 %** | **4,0** couches | 15 % |
| `20230909121925` | Scroll 1 | 50 % | 11,5 | 37 % |
| `scroll4_20231111135340` | Scroll 4 | **7 %** | **22,0** | **61 %** |

⚠ Le filtre `--from-layer 15 --to-layer 40` n'est pas un confort : `20231022170901` a
été téléchargé avec **38** couches et les deux autres avec 26. Sans restreindre à une
plage commune, les « tiers centraux » n'ont pas la même largeur et les pourcentages ne
veulent pas dire la même chose. Le chiffre de ce segment passe de 76 % à 63 % une fois
la comparaison rendue légitime.

### ⚠⚠ La forme importe autant que la position

Scroll 4 n'est pas simplement **décalé** : sa distribution est **bimodale**, 92 fenêtres
piquant à la couche 15 et 49 à la couche 40, avec un milieu presque vide. Un décalage
uniforme — « ce rouleau engendre ses couches autour d'un autre indice » — déplacerait la
médiane **sans gonfler l'écart interquartile**. Or celui-ci passe de 4,0 à **22,0**.

> **La surface de ce segment ne se tient pas à une profondeur constante : elle
> voyage d'un bout à l'autre de ce qui est lu.** C'est la signature d'une trace qui
> dérive, et c'est exactement le défaut que le déroulement doit éviter.

## 4. Pourquoi c'est utile

Cette mesure ne demande **ni vérité terrain, ni modèle d'encre, ni juge**. Elle ne lit
que les couches, qui existent pour tout segment publié. C'est la première grandeur du
dépôt qui parle de la **qualité d'une trace** sans passer par ce qu'on arrive à lire
dessus — et l'objectif est le déroulement, pas la lecture.

Et elle explique l'échec de `09` §12 sans invoquer un décalage de domaine : le modèle
ne s'est pas trompé sur l'encre de Scroll 4, **il a regardé à côté**.

## 5. ⚠ Ce que ça ne dit PAS

1. **Trois segments, deux rouleaux.** Ce n'est pas un corpus. La grandeur est plausible
   et mesurée ; elle n'est pas validée sur une population.
2. **Elle ne classe pas la qualité de détection d'encre.** `20230909121925` est celui
   qui donne l'AUC 0,925, et il est **moins bon** ici que `20231022170901` (50 % contre
   63 %). Prétendre qu'elle prédit la lisibilité répéterait exactement l'erreur que la
   tâche D a coûté cher à écarter (`06` §3.8).
3. **La bimodalité pourrait venir de l'engendrement des couches** plutôt que de la
   trace. Pour les départager il faudrait un segment dont on sait indépendamment qu'il
   est propre, avec sa pile complète.
4. Le passe-haut 3×3 est une mesure de netteté locale parmi d'autres. Un autre noyau
   déplacerait les chiffres ; il ne déplacerait pas un facteur 7.

## 6. ⚠⚠ Avec la pile complète 0–40 : le trait est plus dur

Les couches 0 à 14 ont été téléchargées (7,5 Go) pour voir **sous** la fenêtre lue.
Résultat sur le segment Scroll 4, 230 fenêtres :

| pic de contraste | fenêtres |
|---|---:|
| **couche 0** (le bord absolu de la pile) | **100** |
| couches 1 à 39 | 104, dispersées |
| **couche 40** | **26** |

⚠ Un pic au bord peut être un **artefact de bord** — un passe-haut réagit fort à une
troncature. La forme le réfute : à l'endroit exact où l'inférence a tourné
(`top 2560, left 20000`), le contraste **décroît de façon lisse et monotone** de 1,000 à
la couche 0 jusqu'à 0,000 à la couche 40, et l'intensité moyenne fait de même (plateau
0,99–1,00 des couches 0 à 5, puis chute à 0 vers la couche 36). C'est une courbe, pas
une pointe.

> **La matière occupe les couches 0 à ~28 et le reste est du vide.** La surface tracée
> est la couche **32** : elle tombe donc **dans le vide**, à une vingtaine de voxels au
> moins de la feuille — soit plus qu'une épaisseur de feuille (142,8 µm, `11` §3).
> **La trace est posée à côté du papyrus.**

Pour comparaison, le segment Scroll 1 qui donne l'AUC 0,925 a son pic **à l'intérieur**
de ce qui est lu (couche 26), avec une courbe unimodale propre qui retombe à zéro vers
34 puis **remonte** légèrement en 39–40 — la feuille suivante.

⚠ Et la bimodalité demeure : 100 fenêtres au bord bas, 26 au bord haut. **Aucune plage
unique ne peut servir tout le segment.** Ce n'est pas un décalage constant qu'on
corrigerait avec un `--start-layer` ; c'est une trace qui n'est pas sur la feuille au
même endroit d'un bout à l'autre.

## 7. La suite que ça ouvre

⭐ **Relancer l'inférence Scroll 4 sur `--start-layer 0`** — lancé. La région inférée
appartient à la population « pic à la couche 0 », donc la fenêtre 0–25 est celle qui
contient le plus de matière. C'est le test qui départage :

| si | alors |
|---|---|
| le détecteur retrouve de la structure de trait | l'instrument **transporte**, `09` §12 devient « mal visé » |
| rien ne change | le décalage de couches n'était pas la cause, et il reste le décalage de domaine |

⚠ Dans les deux cas la trace de ce segment reste suspecte : une trace posée sur la
feuille n'aurait pas 55 % de ses fenêtres avec le pic à un bord.

## Reproduire

```bash
cd inference_xpu
# une fenêtre, profil détaillé
uv run python ../analysis/src/depth_profile.py ../data/layers/<segment> \
    --top 2560 --left 20000 --size 1024
# le segment entier
uv run python ../analysis/src/depth_profile.py ../data/layers/<a> ../data/layers/<b> \
    --grid --size 512 --step 1024 --from-layer 15 --to-layer 40 \
    --out ../docs/profil_grille.json
```
