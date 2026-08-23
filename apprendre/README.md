# `apprendre/` — comprendre ce projet, en vidéo

Des animations construites avec [Manim](https://www.manim.community/), **pour l'auteur
d'abord** : publier un travail qu'on ne comprend pas est le seul résultat inacceptable de
tout ce dépôt.

## La règle de rédaction

⚠⚠ **Aucun prérequis.** Aucun symbole n'apparaît avant que la chose qu'il nomme ait été
montrée. `d` arrive après qu'on ait vu un écart, `n` après qu'on ait vu une fenêtre, α
seulement quand les deux rapports sont à l'écran. Les formules ne sont pas évitées — elles
sont **décortiquées**, morceau par morceau, chacun après son image.

⭐ **Les chiffres des vidéos sont les vrais.** Quand un exemple pédagogique tombe sur une
valeur ronde, on garde la valeur mesurée : un lecteur qui refait le calcul doit retrouver
ce que la vidéo annonce, sinon il a raison de ne plus rien croire. La vidéo 2 se termine
d'ailleurs sur ce constat — son α = 0,91 *est* la mesure réelle de `PHercParis4`.

## Les épisodes

| n° | titre | ce qu'on y comprend | durée |
|---|---|---|---|
| **1** | Suivre une feuille | rouleau, spire, coupe, pile, graine, trace, rendu | 1 min 12 |
| **2** | Comment savoir si c'est la bonne feuille ? | le profil de profondeur, le logarithme, **α** | 3 min 15 |
| **3** | Le mur invisible | la troncature : quand la stabilité n'est qu'un réglage | 1 min 46 |
| **4** | Le traceur n'est pas une fonction | le bruit de tirage, et pourquoi il faut **répéter** | 1 min 05 |
| **5** | Le témoin négatif | prouver qu'un détecteur **ne prouve rien** | 1 min 25 |
| **6** | α ≈ 1 a deux causes | le pic qui recule *contre* le profil plat | 1 min 11 |
| **7** | Ce que mesurer coûte | le mur mémoire, et pourquoi il était invisible | 1 min 52 |

**7 épisodes, 11 min 48 au total.**


## Fabriquer

```bash
apprendre/rendre.sh apprendre/scenes/01_suivre_une_feuille.py       # 480p, rapide
QUALITE=h apprendre/rendre.sh apprendre/scenes/02_comment_savoir.py  # 1080p
apprendre/rendre.sh --verifier                                       # les témoins
```

⚠⚠ `rendre.sh` extrait des **vignettes** après l'assemblage, et ce n'est pas un confort :
une vidéo qu'on ne regarde pas est une vidéo qu'on ne peut pas contrôler. Une légende posée
par-dessus une figure ne se voit jamais à la relecture du code — elle saute aux yeux sur une
vignette. C'est exactement comme ça que le premier rendu de la scène 2 a été corrigé.
