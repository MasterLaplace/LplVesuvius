# 64 — La dispersion n'était pas un effet, c'était le bruit d'une fenêtre

> ⭐⭐⭐ [`63`](63_la_premiere_verite_terrain.md) ferme sur une seule tâche vivante : « la
> dispersion est réelle, elle est plus grande que tout écart qu'on chercherait à mesurer
> entre deux réglages, et elle n'est pas expliquée. » Elle l'est. **Et la réponse n'est pas
> une cause : c'est que la question était mal posée.** Chaque fragment n'avait été mesuré que
> par une fenêtre, et une mesure unique n'a pas de barre d'erreur.

![La dispersion dans un fragment contre la dispersion entre fragments](../images/64_bruit_dune_fenetre.png)

## 1. Ce qu'il fallait mesurer avant de chercher une cause

Chercher **ce qui** distingue trois fragments suppose qu'il y ait quelque chose à distinguer.
La question préalable est bête et elle n'avait pas été posée : **de combien deux mesures du
même fragment diffèrent-elles ?** Si elles diffèrent autant que deux fragments, alors « le
fragment » n'explique rien, et l'écart de 0,171 d'AUC est un tirage, pas un fait.

Les trois cartes étaient déjà rendues. Il a suffi de les découper en tuiles de 256 px — la
maille d'annotation que [`evaluate_segment`](../../src/volume/evaluate_segment.py) emploie déjà —
et de mesurer une AUC par tuile.

| | |
|---|---:|
| écart-type **dans** un fragment, de tuile à tuile | **0,2243** |
| écart-type **entre** fragments | **0,0391** |
| rapport | **5,7×** |
| part attribuable au fragment (corrélation intraclasse) | **3,0 %** |
| paires de fragments dont les intervalles de confiance se recouvrent | **2** sur 3 |

⭐⭐⭐ **Savoir de quel fragment vient une tuile explique 3 % de la dispersion.** L'écart
publié entre `Frag1` et `Frag2` est plus petit que l'écart entre deux tuiles voisines du même
fragment. Il n'y a pas de cause à chercher : il y a un protocole à corriger.

## 2. ⚠⚠ Le piège qui aurait donné la réponse inverse

La barre d'erreur d'une AUC **ne se calcule pas** ici par la formule usuelle de
Hanley–McNeil. Cette formule suppose des tirages indépendants, et une carte d'encre est
massivement auto-corrélée : deux pixels voisins portent presque la même valeur et presque
toujours la même étiquette. Les deux estimations sont calculées côte à côte exprès :

| fragment | erreur-type par **tuiles** | par **Hanley–McNeil** | rapport |
|---|---:|---:|---:|
| `Frag1` | 0,0601 | 0,00055 | **×109** |
| `Frag2` | 0,0712 | 0,00072 | **×99** |
| `Frag3` | 0,0822 | 0,00239 | **×34** |

⚠⚠⚠ **Cent fois trop étroite.** Appliquée telle quelle, elle déclarerait significatif
n'importe quel écart entre n'importe quelles cartes, **y compris deux tirages du même
fragment**. Elle est gardée dans le fichier, non pour servir, mais pour que personne ne la
rapplique un jour en croyant bien faire : un intervalle cent fois trop étroit a exactement
l'air d'un intervalle rigoureux.

Le rééchantillonnage se fait donc **par tuiles**, l'échelle à laquelle la structure spatiale
existe.

## 3. ⚠⚠ Une hypothèse à moi, réfutée par sa propre mesure

Le tableau du § 1 a sorti un fait imprévu : sur `Frag3`, l'AUC **groupée** vaut 0,575 quand
la moyenne des AUC **par tuile** vaut 0,845. Même modèle, mêmes étiquettes.

L'explication qui vient d'elle-même est un **décalage de niveau par région** : dans chaque
tuile le modèle rangerait bien l'encre, mais d'une tuile à l'autre il travaillerait à des
hauteurs différentes, si bien qu'un pixel vierge d'une tuile « haute » passerait devant un
pixel encré d'une tuile « basse ». C'est testable en le retirant — remplacer, dans chaque
tuile, les scores par leur rang ramené à [0, 1], ce qui aligne les niveaux sans toucher à
l'ordre interne.

| fragment | AUC sur l'union des tuiles | après alignement des niveaux | écart |
|---|---:|---:|---:|
| `Frag1` | 0,677 | 0,626 | **−0,052** |
| `Frag2` | 0,581 | 0,531 | **−0,050** |
| `Frag3` | 0,801 | 0,703 | **−0,098** |

⭐⭐ **Aligner les niveaux rend l'AUC PIRE, sur les trois fragments.** L'hypothèse est donc
fausse, et son contraire est vrai : les différences de niveau entre tuiles **portent du
signal**. Le modèle note plus haut, en moyenne, dans les régions qui portent plus d'encre, et
cette information-là compte dans l'AUC groupée. La retirer coûte de 0,05 à 0,10.

ⓘ L'écart de `Frag3` reste donc à expliquer autrement, et [`63`](63_la_premiere_verite_terrain.md)
§2 ter l'avait déjà nommé : c'est le **domaine**. Sa fenêtre ne porte que 1,55 % d'encre, donc
« tout le segment » compte surtout du papyrus vierge (0,575), l'union de ses deux tuiles
annotées en compte beaucoup moins (0,801), et la moyenne de deux tuiles en compte encore
autrement (0,845). Trois nombres, trois domaines, un seul modèle.

## 4. ⚠⚠ Une tuile sur cinq est SOUS le hasard

**5 tuiles sur 23**, et la plus basse à **0,158**.

Ce n'est pas du bruit autour de 0,5. Une AUC de 0,158 veut dire que sur cette tuile le modèle
range l'encre **sous** le papyrus vierge — un signal réel, à l'envers. Une moyenne noie
complètement ce fait : `Frag2` sort à 0,600 en portant trois tuiles sous 0,35.

ⓘ Et la corrélation entre l'AUC d'une tuile et sa densité d'encre vaut **−0,248** : les tuiles
les plus encrées s'en sortent légèrement **moins** bien. Modeste, et contraire à l'intuition
qu'une tuile dense serait plus facile.

## 5. ⭐ Ce que ça change pour la suite : un nombre avant de lancer

L'écart observé entre le meilleur et le pire fragment vaut 0,171 d'AUC. Avec un écart-type
de tuile de 0,2243, l'établir au seuil usuel demande :

> **27 tuiles par fragment.** On en avait **10, 11 et 2.**

⚠ Et c'est un **minorant** : la formule suppose des tuiles indépendantes, or deux tuiles
voisines d'un même fragment se ressemblent. Le vrai compte est plus grand.

C'est la même leçon que le contrôle typographique du témoin négatif, qui avait manqué d'**une**
fenêtre : la taille de l'expérience se calcule **avant** de la lancer, pas après l'avoir
trouvée décevante. La différence est qu'ici le calcul existe maintenant dans l'instrument, et
qu'il sort avec la mesure.

## 6. Ce que ce document N'établit pas

1. ⚠⚠ **Que les fragments sont équivalents.** Deux intervalles qui se recouvrent ne prouvent
   pas l'égalité, ils prouvent que la différence **n'est pas établie**. Dire l'un pour l'autre
   serait exactement la faute que ce dépôt appelle « une vérification satisfaite pour la
   mauvaise raison ». Il reste possible que `Frag1` soit réellement meilleur que `Frag2` — mais
   il faudrait le montrer avec assez de tuiles, et personne ne l'a fait.
2. ⚠ **`Frag3` reste à part**, et son intervalle ne recouvre pas celui de `Frag2`. Mais il
   repose sur **2 tuiles**, ce qui est aussi le plus petit échantillon possible pour avoir un
   intervalle du tout. Ce n'est pas un résultat, c'est un avertissement.
3. ⚠ **La tuile de 256 px est un choix**, et il n'a pas été balayé. Une tuile plus petite
   rendrait des AUC plus bruitées, donc un écart-type intra plus grand, donc un ICC encore
   plus bas — la conclusion irait dans le même sens, mais l'ampleur dépend de la maille.
4. ⚠⚠ **Rien ici ne touche à ce que vaut la chaîne.** La question « le modèle lit-il de
   l'encre » reste répondue par oui : le contrôle par mélange rend 0,500 sur les trois
   fragments et les trois domaines. Ce qui tombe, c'est le classement entre eux.

---

**Instruments** : [`src/encre/bruit_dune_fenetre.py`](../../src/encre/bruit_dune_fenetre.py)
(44 contrôles, quatre sondes tenues — dont celle de l'ICC naïf, qui passait au vert avant
d'être écrite), [`src/figures/figure_bruit_dune_fenetre.py`](../../src/figures/figure_bruit_dune_fenetre.py)
(20 contrôles).
**Mesure** : [`bruit_dune_fenetre.json`](../mesures/bruit_dune_fenetre.json).
**Voir aussi** : [`63`](63_la_premiere_verite_terrain.md) pour les trois AUC dont ce document
mesure la dispersion, [`46`](46_le_temoin_negatif.md) §3 pour le contrôle typographique qui a
manqué d'une fenêtre faute du même calcul, et
[`src/encre/fenetres_par_region.py`](../../src/encre/fenetres_par_region.py) pour la version
« proportions » du même calcul de taille d'échantillon — deux questions, deux formules, et
c'est pourquoi la seconde n'a pas été réutilisée.
