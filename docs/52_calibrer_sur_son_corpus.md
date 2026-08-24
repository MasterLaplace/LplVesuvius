# 52 — Calibrer sur son corpus, parce qu'un seuil n'appartient qu'à sa géométrie

2026-08-24. Suite directe de [`51`](51_une_pente_a_deux_appuis.md), et écrit après avoir
transporté **trois fois dans la même nuit** un nombre hors de la géométrie qui l'avait
produit. Aucune des trois fois n'a été trouvée en relisant.

![où se tient un corpus publié](images/52_calibration.png)

Instruments : [`analysis/src/calibration_corpus.py`](../analysis/src/calibration_corpus.py)
(11 témoins) et [`figure_calibration.py`](../analysis/src/figure_calibration.py)
(13 témoins). Données : [`docs/balayage_scroll1.csv`](balayage_scroll1.csv), 81 segments.

---

## 1. ⚠⚠ Les trois transports, et ce qu'ils avaient en commun

| # | le nombre | mesuré dans | offert à |
|---|---|---|---|
| 1 | le seuil **2,25×** du README public | fenêtres de **1024 px** | un outil qui lit **128 px** |
| 2 | les taux d'erreur **0/75** et **6/75** | piles **rendues** | un outil qui lit des **volumes publiés** |
| 3 | la profondeur du corpus, **« 65 couches »** | mon souvenir | une calibration publiable |

Le troisième vaut **109**, et je l'ai vérifié parce que le premier venait d'être pris en
faute. Le premier l'avait été par un écart de dix sans explication physique entre deux
distributions ; le second par le balayage lui-même, où `edge_pinned` n'atteint jamais le
seuil auquel je l'avais déclaré fautif.

> ⭐⭐ **Ce qui les relie** : le relief est lu sur une **moyenne de patch**, donc il dépend
> de la profondeur (exposant **+1,01**) *et* de l'étendue dans le plan (exposant
> **−0,830**). Une grandeur lue sur une moyenne appartient à la géométrie qui l'a moyennée.

## 2. ⭐ Le remède est dans le code, à trois endroits

Une mise en garde dans une prose ne survit pas au tableau d'à côté. Donc :

- **`tracecheck` écrit sa géométrie** dans son CSV (`layers`, `window_px`) — un fichier de
  calibration se décrit lui-même ;
- **`calibration_corpus` refuse** deux géométries dans un même fichier (jamais une moyenne),
  refuse une géométrie ni lue ni déclarée, et **marque** celle qu'on lui déclare à la main ;
- **`figure_calibration` l'imprime** sur le dessin.

## 3. ⚠⚠ Le refus a payé au premier usage réel

Lancé sur le balayage complet, `calibration_corpus` a **refusé** :

```
refus : layers n'est pas unique dans ce fichier : ['109', '6'] —
        deux instruments concaténés ne calibrent rien
```

**Un corpus publié n'est pas homogène.** Sur les 81 segments de `Scroll1`, quatre-vingts
sont lus sur **109 couches** et **un sur 6**. Une distribution unique aurait mélangé une
lecture sur six couches à quatre-vingts sur cent neuf.

⭐ Grouper vaut mieux que refuser **ou** que moyenner : `--par-geometrie` rend une
calibration par groupe, et un groupe d'un seul segment se voit immédiatement comme tel.

## 4. La calibration, enfin publiable

| 128 px × 109 couches, 80 segments | relief | `edge_pinned` |
|---|---:|---:|
| minimum | **0,040** | 0,000 |
| médiane | **0,744** | 0,073 |
| maximum | **0,975** | 0,254 |
| sous le plancher de 0,02 | **0** | — |
| au-dessus de 0,90 | — | **0** |

⭐ **Le corpus publié se tient loin du plancher** : ×2 au plus bas, ×37 à la médiane, ×49 au
plus haut. C'est la calibration que le README public promet désormais à ses lecteurs, et
c'est une commande.

⭐⭐ **Et le zéro de la seconde colonne est le plus instructif** : `edge_pinned` n'atteint
jamais, sur ce corpus, le seuil de 90 % auquel je l'avais déclaré fautif. **Sur cet
instrument, les deux signaux ne se départagent pas.** Le dire vaut mieux que réciter la
comparaison faite sur l'autre.

## 5. ⚠ Un segment publié à ×2 du plancher

| segment | relief | rapport | `material` |
|---|---:|---:|---:|
| `20260701183151-w128-129` | **0,040** | **×2** | 0,49 |
| suivant | 0,373 | ×19 | 0,61 |

Le second plus bas est déjà à ×19. Ce segment est donc **seul**, et le voir dans un tableau
demanderait de le chercher ; sur la figure il se voit d'un coup d'œil, isolé entre le
plancher et le nuage.

⚠ **Ce que ça n'établit pas.** Un relief bas dit que la colonne de profondeur ne porte
presque pas de structure là où l'outil a regardé. Ça ne dit pas que le segment est faux :
il peut être mince, mal exposé, ou tomber sur une région pauvre. Le critère est
**nécessaire, jamais suffisant** — la même prudence que [`45`](45_consistent_with_quantifie.md)
impose à la statistique typographique.

## 6. Ce que ce document n'établit pas

- ⚠ **Que le relief mesure la qualité d'une surface.** Il mesure si la colonne lue porte de
  la structure. [`51`](51_une_pente_a_deux_appuis.md) §6 montre qu'une fenêtre étroite plate
  condamne ; l'inverse n'absout pas.
- ⚠ **Que cette distribution vaille ailleurs.** Elle vaut pour 128 px × 109 couches et pour
  aucune autre géométrie — c'est tout le propos.
- ⚠ **Que les deux signaux soient équivalents.** Ils ne se départagent pas *ici*, faute
  d'occasion : `edge_pinned` ne monte jamais assez haut sur ce corpus pour se tromper.

## Reproduire

```bash
cd inference && uv run python ../tracecheck/tracecheck.py Scroll1 --all --csv \
    --voxel-um 2.4 --prefer 2.4um > ../docs/balayage_scroll1.csv

python3 analysis/src/calibration_corpus.py docs/balayage_scroll1.csv \
    --par-geometrie --json docs/calibration_scroll1.json

cd inference && uv run python ../analysis/src/figure_calibration.py \
    --csv ../docs/balayage_scroll1.csv --layers 109 \
    --sortie ../docs/images/52_calibration.png

# les témoins, hors ligne
python3 analysis/src/calibration_corpus.py --verifier
python3 analysis/src/figure_calibration.py --verifier
```
