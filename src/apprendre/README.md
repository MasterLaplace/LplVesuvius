# `src/apprendre/` — comprendre ce projet, en vidéo

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
| **8** | La fenêtre qui mesure | le **relief**, et pourquoi un seuil ne voyage pas | 2 min 12 |

**8 épisodes, 14 min 00 au total.**

⚠⚠ L'épisode 8 raconte le piège le plus cher du dépôt, payé **cinq fois en une nuit** : un
nombre parfaitement juste, déplacé hors de la géométrie qui l'a produit, devient faux **sans
cesser d'avoir l'air sensé**. Il construit la grandeur (le relief), montre qu'elle dépend de
la fenêtre où on la lit, et finit sur le résultat que la règle a débloqué — cinq de nos
traces à zéro, trois dernières de leur propre rouleau.


## Fabriquer

```bash
src/apprendre/rendre.sh src/apprendre/01_suivre_une_feuille.py       # 480p, rapide
QUALITE=h src/apprendre/rendre.sh src/apprendre/02_comment_savoir.py  # 1080p
src/apprendre/rendre.sh --verifier                                       # les témoins
```

⚠ **Les huit, un par un.** Cette section n'en montrait que deux, et les six autres n'étaient
alors fabricables qu'en devinant le motif — ce qui est aussi pourquoi `appelants.py` les
comptait comme des scripts que rien n'exécute. Les voici en entier :

```bash
src/apprendre/rendre.sh src/apprendre/01_suivre_une_feuille.py
src/apprendre/rendre.sh src/apprendre/02_comment_savoir.py
src/apprendre/rendre.sh src/apprendre/03_le_mur_invisible.py
src/apprendre/rendre.sh src/apprendre/04_pas_une_fonction.py
src/apprendre/rendre.sh src/apprendre/05_le_temoin_negatif.py
src/apprendre/rendre.sh src/apprendre/06_deux_causes.py
src/apprendre/rendre.sh src/apprendre/07_ce_que_mesurer_coute.py
src/apprendre/rendre.sh src/apprendre/08_la_fenetre_qui_mesure.py
```

⚠⚠ `rendre.sh` extrait des **vignettes** après l'assemblage, et ce n'est pas un confort :
une vidéo qu'on ne regarde pas est une vidéo qu'on ne peut pas contrôler. Une légende posée
par-dessus une figure ne se voit jamais à la relecture du code — elle saute aux yeux sur une
vignette. C'est exactement comme ça que le premier rendu de la scène 2 a été corrigé.
