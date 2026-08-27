# 60 — Une constante rendait le modèle muet, et elle a fondé un résultat négatif

> ⚠⚠⚠ **Ce document annule une conclusion publiée de ce dépôt.** `36` §5bis répondait « non »
> à *l'encre est-elle lisible à 9 µm ?*, sur la foi d'un σ **45 fois** plus petit que là où le
> modèle marche. Ce σ mesurait une erreur d'échelle de notre côté. **La même pile, la même
> fenêtre, le même modèle, à l'échelle corrigée : σ passe de 0,0171 à 0,6558**, soit
> **1,2 fois** le témoin où le modèle lit du grec.

![la meme fenetre, le meme modele, seule l echelle change](images/60_echelle_uint8.png)

> À gauche ce que le modèle recevait, à droite ce qu'il aurait dû recevoir. **Les deux
> panneaux partagent leur étirement** — étirer chacun sur sa propre plage rendrait la
> constante aussi contrastée qu'une vraie carte, ce qui est exactement l'inverse de ce
> qu'on montre.
>
> Figure : `src/figures/figure_echelle.py`, depuis `data/out/ink_PHerc0172_w062{,_u16}.npy`.

## 1. La ligne

`src/xpu/infer_ink.py`, dans `load_layer_stack` :

```python
# Le modele a ete entraine sur des entrees normalisees a [0, 1] depuis du
# uint16 ; garder l'echelle brute donnerait des activations hors domaine.
return stack / 65535.0
```

Le commentaire dit **uint16**, et la constante l'écrit en dur. Une pile **uint8** divisée par
65535 arrive au modèle **257 fois trop sombre** : moyenne 0,002 au lieu de 0,6. Du noir.

⚠⚠ **Et un modèle à qui l'on donne du noir rend une constante — qui se lit comme « il n'y a
pas d'encre ici ».** C'est ce qui rend cette panne coûteuse : elle ne ressemble pas à une
panne, elle ressemble à un résultat.

## 2. ⭐⭐ Le partage était TOTAL, et personne ne l'avait regardé

`src/depot/echelle_des_piles.py` liste le type de chaque pile de couches de l'arbre :

| type | piles | d'où elles viennent |
|---|---:|---|
| **uint16** | **3** | `data/layers/` — les stacks **publiés** (Scroll 1 ×2, Scroll 4) |
| **uint8** | **211** | tout ce que `vc_render_tifxyz` rend, tout ce que `zarr_vers_couches.py` écrit |

⭐⭐⭐ **Le partage « le modèle répond / le modèle est inerte » suivait exactement celui-là.**
Les σ autour de 0,77 sont tous sur les trois piles uint16 ; les σ autour de 0,015 sont tous
sur des piles uint8.

⚠ Le pont `zarr_vers_couches.py` le disait même dans son propre en-tête — *« les couches sont
écrites TELLES QUELLES, sans normalisation : le modèle a été entraîné sur des `uint8`
bruts »* — pendant que le lecteur divisait par 65535. **Deux fichiers du même dépôt, deux
échelles, et aucun des deux ne pouvait voir l'autre.**

## 3. La mesure, et son contrôle

Même fenêtre, même code, seule l'échelle d'entrée changeant :

| | min | méd | max | **étendue** |
|---|---:|---:|---:|---:|
| `PHerc0172`, uint8 divisé par 65535 | −1,215 | −1,121 | −1,008 | **0,207** |
| … la même remise à l'échelle à la main | −1,815 | −0,526 | +2,463 | **4,278** |
| … la même, uint8 brut, **après le correctif** | −1,815 | −0,526 | +2,463 | **4,278** |

⭐ Les deux dernières lignes sont **identiques au chiffre près** : le correctif fait
exactement ce que la remise à l'échelle manuelle faisait, ce qui est la façon la moins
discutable de montrer qu'il est juste.

⚠⚠ **Et le contrôle qui compte autant : le correctif ne doit RIEN changer sur uint16.**
`np.iinfo(uint16).max` vaut 65535, donc la valeur est identique — et c'est **mesuré**, pas
déduit : la même fenêtre de Scroll 1 rend `−1,778 / −1,559 / +1,691` avant et après, au
chiffre près. Aucun résultat publié sur les piles publiées ne bouge.

## 4. ⭐⭐⭐ Ce que ça renverse

| | avant | après | contre le témoin |
|---|---:|---:|---:|
| `PHerc1447` — **un rouleau du prix** | σ **0,0171** | σ **0,6558** | **1,2×** |
| `PHerc0172` — 53 keV, hors des treize | étendue 0,207 | σ **1,0217** | **0,8×** |
| Scroll 1 — le témoin | σ 0,7712 | σ 0,7712 | 1,0× |

⭐⭐⭐ **`PHerc1447` passe de 45 fois sous le témoin à 1,2 fois — le même régime.** Le verdict
de `comparer_encre.py`, qui ne sait rien de cette histoire, est *« la cible a une dynamique
comparable au témoin »*.

## 4 bis. ⚠⚠ Répondre n'est pas lire — et la surface entière le montre

σ dit que le modèle produit de la structure, pas qu'il produit du texte. La fenêtre de
1024 px du §4 ne pouvait pas trancher : à 8,64 µm elle fait 8,8 mm, **quatre lettres de
large**. La surface **publiée entière** de `PHerc1447` a donc été rendue — 2980 × 3240, soit
**25,7 × 28,0 mm**, de quoi porter une dizaine de lignes.

![carte d encre sur la surface publiee entiere de PHerc1447](images/60_PHerc1447_surface_entiere.png)

> σ = **0,4838** sur 9,58 M pixels, étendue **4,266**, soit **1,6×** sous le témoin — et
> `comparer_encre` rend son verdict habituel, *« la cible a une dynamique comparable au
> témoin »*.
>
> ⚠⚠ **Et à l'œil, c'est de la moucheture.** Pas de lettres, pas de lignes, pas de colonnes.
> Les zones claires suivent la forme du segment et ses trous, pas une écriture.

⭐⭐ **Donc M1ter est ROUVERT, pas répondu par l'affirmative.** La réponse négative reposait
sur un artefact ; la réponse positive n'est pas établie pour autant.

⚠⚠ **Et c'est une limite de l'instrument qu'il faut écrire** : le même σ qui a fondé le
résultat négatif ne peut pas fonder le résultat positif. Il mesure une **dispersion**, et une
moucheture pleine échelle en a autant qu'un texte. Ce qui trancherait est le juge calibré de
[`09`](09_protocole_jugement_modele.md), qui sépare vierge **0–1** de texte **3–6**.

⚠ Ce que ça n'accuse pas : ce segment est celui dont `36` dit que la surface tracée est à
**17 µm** de sa feuille avec **2 %** de fenêtres au tiers central, et son volume de surface
n'est couvert qu'à **52,5 %**. Une moucheture sur une surface qui n'est pas posée sur la
feuille est le résultat attendu, et le bug d'échelle n'a jamais touché ce fait-là.

## 4 ter. ⚠⚠ Et l'instrument typographique, LUI, y trouve de la périodicité

L'œil dit moucheture, mais l'œil regarde une image réduite. `src/encre/typographie.py`
mesure les quatre grandeurs de [`45`](45_consistent_with_quantifie.md) — couverture,
épaisseur de trait, **périodicité des lignes**, netteté du pic — et il sait travailler sur
nos cartes de prédiction depuis ce jour (`--npy`).

⚠⚠ **Il a d'abord fallu le calibrer**, et son réglage par défaut ne peut rien conclure
**sur nos cartes** : à la réduction 4, celle de Scroll 1 — où les lettres se lisent à l'œil —
rend **0 %** de fenêtres périodiques. Un instrument qui répond « pas de texte » sur du texte
ne conclut rien.

⭐ **Et ce n'est pas un défaut du réglage : c'est une différence d'échelle**, que la docstring
de l'outil annonce (*« le facteur est un PARAMÈTRE parce qu'il dépend de la résolution du
scan »*). Vérifié plutôt que supposé : sur les **190 cartes publiées**, mesurées à la
réduction 4, **156 ont au moins une fenêtre périodique** et la part médiane de `PHerc0172`
vaut 1,0. Les cartes publiées sont des JPEG déjà réduits ×8 par leur pipeline ; les nôtres
sont en pleine résolution. Il leur faut donc **ce ×8 en plus**, et le réglage calibré
ci-dessous n'est rien d'autre.

Le balayage donne le réglage utile :

| réduction | fenêtre | Scroll 1, texte connu |
|---:|---:|---|
| 4 | 512 | 0/12 — **incapable de conclure** |
| 8 | 512 | 2/3 |
| **8** | **256** | **8/12 (67 %), période 38 px = 2,4 mm** |

Au réglage calibré, avec le contrôle qui donne une échelle au compte :

| | fenêtres périodiques | période | netteté |
|---|---:|---:|---:|
| Scroll 1 — texte connu | **8/12 (67 %)** | 38 px → **2,4 mm** | 0,751 |
| … ses pixels **mélangés** | **0/12** | — | — |
| **`PHerc1447`, surface entière** | **2/2 (100 %)** | 48 px → **3,3 mm** | 0,672 |
| … ses pixels **mélangés** | **0/2** | — | — |

⭐⭐ **Le mélange garde la distribution et détruit la structure** : la périodicité de
`PHerc1447` ne vient donc pas de sa statistique de gris, elle vient de son agencement. Et
l'interligne trouvé, **3,3 mm**, est du même ordre que les 2,4 mm de Scroll 1.

⚠⚠⚠ **Et n vaut DEUX.** Deux fenêtres, c'est un tirage à pile ou face — [`33`](33_la_carte_nest_pas_resolue.md)
est un document entier sur le fait qu'on ne conclut pas à quinze fenêtres. **Ceci est une
piste, pas une lecture.** Le seul moyen d'augmenter n est de rendre plus de surface :
`PHerc1447` en publie **quatre**, une seule était rendue, et
`src/campagnes/campagne_encre_1447.sh` rend les trois autres.

### ⭐⭐ Le critère, écrit AVANT que la campagne ne rende

> Ce paragraphe est commité pendant que les trois rendus tournent, pour la raison que
> [`53`](53_le_temoin_positif_du_rendu.md) écrit en tête : *un témoin dont on n'a pas dit
> d'avance ce qu'il condamnerait ne condamne jamais rien — il s'explique après coup.*

Ce qui sera comparé n'est **pas** une part de fenêtres périodiques contre un seuil : un
seuil serait un nombre choisi pour que le tirage du jour passe. C'est la part observée
contre celle de la **même carte aux pixels mélangés**, à n identique, par un **Fisher exact
unilatéral** — la direction est déclarée ici, une carte réelle devrait être *plus* périodique
que son mélange, jamais moins.

| issue | ce qu'on en conclura |
|---|---|
| p < 0,05 | la périodicité de `PHerc1447` n'est pas un tirage. ⚠ Ça ne dira toujours pas que c'est du **texte** — seulement que la carte est structurée là où son mélange ne l'est pas |
| p ≥ 0,05 | on ne conclut rien, et les deux fenêtres du §4 ter restent une curiosité |
| moins de 8 fenêtres au total | **on ne teste pas** : sous cette taille le test n'a pas la puissance de distinguer, et le lancer quand même serait fabriquer un p |

⚠ Et l'issue la plus probable est la troisième : la première surface a rendu **2** fenêtres,
la deuxième en rendra de l'ordre de **4** au vu de son étendue. Il faudra peut-être les
quatre surfaces pour atteindre huit.

## 5. Ce qui est annulé, et ce qui tient

| document | ce qu'il disait | état |
|---|---|---|
| `36` §5bis | M1ter répondu **négativement** : l'encre n'est pas lisible à 9 µm | ⚠⚠ **ANNULÉ** — le σ mesurait notre échelle |
| `46` §3–4 | le témoin négatif, dont le contrôle **positif** était plat (σ 0,0129) | ⚠⚠ **à refaire** — sa pile `data/couches/…` est uint8 |
| `54` | cinq rendus **vides** | ⚠ **à relire** — les rendus sont uint8 |
| `58` | la résolution éliminée | ⭐ **TIENT** — son échelle de dégradation est mesurée sur les piles **uint16** publiées, donc hors du bug. Ce qui tombe est sa prémisse d'entrée (« un facteur 45 à expliquer ») : il n'y a plus de facteur 45 |
| `59` | la campagne de scan | ⚠ déjà réfutée le même jour, et la question qu'elle poursuivait n'existe plus sous cette forme |

## 6. ⚠⚠ Ce que la batterie ne voyait pas, et ce qu'elle voit maintenant

Premier jet de contrôles : le plafond d'un `uint8` vaut 255, celui d'un `uint16` 65535, leur
rapport est 257. **Tous verts, et tous restés verts quand j'ai remis la constante** — parce
qu'ils portaient sur la *règle* sans jamais traverser `load_layer_stack`.

⭐ Le contrôle qui manquait écrit **deux vraies piles**, une par type, et exige que le modèle
reçoive les mêmes valeurs. Remettre la constante le fait échouer.

Et deux refus, parce qu'un contrôle ne protège que ce qu'on relance :

1. **une pile dont le maximum normalisé est sous 1/64 de la pleine échelle est REFUSÉE**, en
   nommant le type lu et les deux causes possibles (pile vide, ou mauvais plafond). ⚠ Ce
   n'est pas un seuil réglé sur les données du jour : une pile mal mise à l'échelle d'un
   facteur 257 plafonne à 0,0039, soit **deux fois moins** que la borne la plus lâche qu'on
   puisse écrire ;
2. **une pile dont les couches changent de type est refusée** — elle serait normalisée de
   deux façons, et la panne se lirait comme une bande sombre dans la carte d'encre.

## 7. Ce que je retiens

⚠⚠ **La mesure qui a trouvé le bug n'a jamais porté sur le bug.** Elle portait sur une
question ordinaire — *quel type ont les piles de l'arbre ?* — posée pour une raison sans
rapport. Aucune relecture de `load_layer_stack` ne l'aurait donnée : la ligne est correcte
pour le type qu'elle nomme dans son commentaire, et le commentaire est juste.

⭐ Ce qui l'a rendue possible, c'est qu'une question de l'auteur (« c'est quoi ces images
dans `data/encre/` ? ») a forcé à regarder une donnée au lieu d'un raisonnement. C'est la
troisième fois dans la même journée qu'une de ses questions renverse un résultat.

## Reproduire

```bash
uv sync --extra encre --extra volume

# §2 — le type de chaque pile de l'arbre
uv run python src/depot/echelle_des_piles.py data --json docs/mesures/echelle_des_piles.json

# §3 — la même pile avant/après, et le contrôle uint16 qui ne doit pas bouger
uv run python src/xpu/infer_ink.py data/couches/PHerc0172_w062 \
    --model data/models/timesformer_GP_scroll1 --start-layer 4 \
    --top 400 --left 400 --height 256 --width 256 --out /tmp/apres.npy
uv run python src/xpu/infer_ink.py data/layers/20230909121925 \
    --model data/models/timesformer_GP_scroll1 --start-layer 15 \
    --top 2000 --left 2000 --height 256 --width 256 --out /tmp/regression.npy

# §4 — M1ter repris sur PHerc1447
uv run python src/encre/comparer_encre.py data/out/ink_PHerc1447_corrige.npy \
    --temoin data/out/ink_segment_complet.npy --json docs/mesures/m1ter_apres_correction_echelle.json

# la figure
uv run python src/figures/figure_echelle.py \
    --avant data/out/ink_PHerc0172_w062.npy --apres data/out/ink_PHerc0172_w062_u16.npy \
    --sortie docs/images/60_echelle_uint8.png
```
